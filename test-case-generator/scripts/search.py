#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Case Generator - BM25 Search Engine for Test Case Catalogs
Searches CSV catalog files (exported from spreadsheet) using BM25 ranking.

Catalogs are located at the project root (catalog/api/, catalog/frontend/).
References are located inside the skill folder (references/).

CSV format from spreadsheet export:
  Row 1: Group header (ignored)
  Row 2-3: Column names (ignored - may span 2 lines due to quoted newlines)
  Row N: Suite separator (col[0] has value, col[2] empty) OR test case row

Column mapping (by index):
  0: testSuiteName (only on separator rows)
  2: externalId
  3: testCaseName
  4: summary
  5: preConditions
  8: importance
  13: step
  14: expectedResult

Usage:
  python search.py "validate string" --domain api
  python search.py "giao dien chung" --domain frontend
  python search.py --list
  python search.py "validate" --domain api --full
  python search.py --ref output-format
  python search.py --list-refs
"""

import argparse
import sys
import io
import csv
import re
import json
from pathlib import Path
from math import log
from collections import defaultdict

# Force UTF-8 for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SKILL_DIR = Path(__file__).parent.parent
REFS_DIR = SKILL_DIR / "references"
CATALOG_DIR = Path.cwd() / "catalog"
MAX_RESULTS = 5

# Column index mapping
COL = {
    "testSuiteName": 0,
    "externalId": 2,
    "testCaseName": 3,
    "summary": 4,
    "preConditions": 5,
    "importance": 8,
    "step": 13,
    "expectedResult": 14,
}

SEARCH_FIELDS = ["testSuiteName", "testCaseName", "step", "expectedResult", "preConditions"]
PREVIEW_FIELDS = ["testSuiteName", "testCaseName", "step", "expectedResult", "importance"]


# ============ BM25 ============
class BM25:
    def __init__(self, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.corpus, self.doc_lengths = [], []
        self.avgdl, self.N = 0, 0
        self.idf, self.doc_freqs = {}, defaultdict(int)

    def tokenize(self, text):
        text = re.sub(r'[^\w\s]', ' ', str(text).lower())
        return [w for w in text.split() if len(w) > 1]

    def fit(self, documents):
        self.corpus = [self.tokenize(doc) for doc in documents]
        self.N = len(self.corpus)
        if self.N == 0:
            return
        self.doc_lengths = [len(doc) for doc in self.corpus]
        self.avgdl = sum(self.doc_lengths) / self.N
        for doc in self.corpus:
            for word in set(doc):
                self.doc_freqs[word] += 1
        for word, freq in self.doc_freqs.items():
            self.idf[word] = log((self.N - freq + 0.5) / (freq + 0.5) + 1)

    def score(self, query):
        tokens = self.tokenize(query)
        scores = []
        for idx, doc in enumerate(self.corpus):
            s = 0
            tf = defaultdict(int)
            for w in doc:
                tf[w] += 1
            for t in tokens:
                if t in self.idf:
                    n = tf[t] * (self.k1 + 1)
                    d = tf[t] + self.k1 * (1 - self.b + self.b * self.doc_lengths[idx] / self.avgdl)
                    s += self.idf[t] * n / d
            scores.append((idx, s))
        return sorted(scores, key=lambda x: x[1], reverse=True)


# ============ CSV PARSING ============
def safe_col(row, idx):
    """Get column value safely, return empty string if out of range."""
    return row[idx].strip() if idx < len(row) else ''


def is_suite_separator(row):
    """Suite separator row: col[0] has value, col[2] (externalId) is empty."""
    return bool(safe_col(row, 0)) and not safe_col(row, 2)


def is_header_row(row):
    """Header rows contain 'Test Suite', 'Name', 'External ID', etc."""
    text = ' '.join(row[:5]).lower()
    return 'test suite' in text or 'external id' in text or 'name' in text and 'details' in text


def parse_csv_file(filepath):
    """Parse a spreadsheet-exported CSV into test case dicts."""
    test_cases = []
    current_suite = ""

    with open(filepath, 'r', encoding='utf-8-sig') as fh:
        reader = csv.reader(fh)
        for row in reader:
            if not row or all(c.strip() == '' for c in row):
                continue

            # Skip header rows
            if is_header_row(row):
                continue

            # Suite separator row
            if is_suite_separator(row):
                current_suite = safe_col(row, 0)
                continue

            # Test case row: must have externalId or testCaseName
            ext_id = safe_col(row, COL["externalId"])
            case_name = safe_col(row, COL["testCaseName"])
            if not ext_id and not case_name:
                continue

            test_cases.append({
                "testSuiteName": current_suite,
                "externalId": ext_id,
                "testCaseName": case_name,
                "summary": safe_col(row, COL["summary"]),
                "preConditions": safe_col(row, COL["preConditions"]),
                "importance": safe_col(row, COL["importance"]),
                "step": safe_col(row, COL["step"]),
                "expectedResult": safe_col(row, COL["expectedResult"]),
                "_source": filepath.name,
            })

    return test_cases


def load_all_cases(directory):
    """Load all test cases from CSV files in a directory."""
    if not directory.exists():
        return []

    all_cases = []
    for f in sorted(directory.glob("*.csv")):
        try:
            all_cases.extend(parse_csv_file(f))
        except Exception as e:
            print(f"Warning: Could not read {f.name}: {e}", file=sys.stderr)
    return all_cases


# ============ SEARCH ============
def search_cases(query, directory, max_results=MAX_RESULTS):
    """Search test cases using BM25."""
    if not directory.exists():
        return {"error": f"Directory not found: {directory}", "results": []}

    cases = load_all_cases(directory)
    if not cases:
        return {"error": f"No test cases found in {directory}", "results": []}

    # Build search documents from key fields
    documents = []
    for c in cases:
        parts = [c.get(f, '') or '' for f in SEARCH_FIELDS]
        documents.append(' '.join(parts))

    bm25 = BM25()
    bm25.fit(documents)
    ranked = bm25.score(query)

    results = []
    for idx, score in ranked[:max_results]:
        if score > 0:
            case = dict(cases[idx])
            case['_score'] = round(score, 2)
            results.append(case)

    return {
        "query": query,
        "total_cases": len(cases),
        "count": len(results),
        "results": results
    }


# ============ LIST ============
def list_catalog(catalog_dir):
    """List all CSV files and test case counts."""
    if not catalog_dir.exists():
        return f"Catalog not found: {catalog_dir}"

    lines = [f"Catalog: {catalog_dir}", ""]

    for subdir in ["api", "frontend", "mobile"]:
        sub_path = catalog_dir / subdir
        if not sub_path.exists():
            continue
        csv_files = sorted(sub_path.glob("*.csv"))
        if not csv_files:
            lines.append(f"  {subdir}/ (empty)")
            continue

        lines.append(f"  {subdir}/ ({len(csv_files)} files)")
        total = 0
        for f in csv_files:
            try:
                cases = parse_csv_file(f)
                suites = sorted(set(c['testSuiteName'] for c in cases if c['testSuiteName']))
                total += len(cases)
                lines.append(f"    {f.name} — {len(cases)} cases, suites: {', '.join(suites)}")
            except Exception:
                lines.append(f"    {f.name} — (parse error)")
        lines.append(f"    Total: {total} test cases")
        lines.append("")

    return "\n".join(lines)


# ============ OUTPUT ============
def format_preview(result):
    """Format search results as preview."""
    if "error" in result:
        return f"Error: {result['error']}"

    lines = [
        f"## Search Results",
        f"Query: {result['query']} | Found: {result['count']} / {result['total_cases']} total",
        ""
    ]

    for i, r in enumerate(result['results'], 1):
        lines.append(f"### Result {i} (score: {r.get('_score', '?')}, file: {r.get('_source', '?')})")
        for f in PREVIEW_FIELDS:
            val = r.get(f, '')
            if val:
                display = val.replace('\n', ' | ')
                if len(display) > 150:
                    display = display[:150] + "..."
                lines.append(f"  {f}: {display}")
        lines.append("")

    return "\n".join(lines)


def format_full_json(result):
    """Output top matches as clean JSON (no internal fields)."""
    if not result.get('results'):
        return "No results found."

    clean = []
    for r in result['results'][:3]:
        clean.append({k: v for k, v in r.items() if not k.startswith('_')})

    return json.dumps(clean, ensure_ascii=False, indent=2)


# ============ REFERENCES ============
def read_reference(ref_name):
    """Read a reference file from the skill's references directory."""
    if not ref_name.endswith('.md'):
        ref_name += '.md'

    ref_path = REFS_DIR / ref_name
    if not ref_path.exists():
        return f"Reference not found: {ref_name}\nSearched: {ref_path}"
    content = ref_path.read_text(encoding='utf-8')
    return f"## Reference: {ref_path.name}\n**Path:** {ref_path}\n\n{content}"


def list_references():
    """List all available references."""
    lines = ["## Available References", ""]

    if REFS_DIR.exists():
        for f in sorted(REFS_DIR.glob("*.md")):
            lines.append(f"  {f.name}")
    else:
        lines.append("  (no references directory found)")

    return "\n".join(lines)


# ============ CLI ============
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Case Catalog Search (CSV)")
    parser.add_argument("query", nargs="?", default="", help="Search query")
    parser.add_argument("--domain", "-d", choices=["api", "frontend", "mobile"])
    parser.add_argument("--data-dir", help="Override catalog directory (default: ./catalog)")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS)
    parser.add_argument("--list", "-l", action="store_true")
    parser.add_argument("--full", "-f", action="store_true", help="Output top 3 as JSON")
    parser.add_argument("--ref", "-r", metavar="NAME", help="Read a reference file")
    parser.add_argument("--list-refs", action="store_true", help="List available references")

    args = parser.parse_args()

    catalog_dir = Path(args.data_dir) if args.data_dir else CATALOG_DIR

    if args.list_refs:
        print(list_references())
        sys.exit(0)

    if args.ref:
        print(read_reference(args.ref))
        sys.exit(0)

    if args.list:
        print(list_catalog(catalog_dir))
        sys.exit(0)

    if not args.query:
        parser.print_help()
        sys.exit(1)

    if args.domain:
        result = search_cases(args.query, catalog_dir / args.domain, args.max_results)
    else:
        # Auto: search both, merge by score
        r_api = search_cases(args.query, catalog_dir / "api", args.max_results)
        r_fe = search_cases(args.query, catalog_dir / "frontend", args.max_results)
        all_r = r_api.get("results", []) + r_fe.get("results", [])
        all_r.sort(key=lambda x: x.get("_score", 0), reverse=True)
        total = r_api.get("total_cases", 0) + r_fe.get("total_cases", 0)
        result = {"query": args.query, "total_cases": total,
                  "count": len(all_r[:args.max_results]), "results": all_r[:args.max_results]}

    if args.full:
        print(format_full_json(result))
    else:
        print(format_preview(result))
