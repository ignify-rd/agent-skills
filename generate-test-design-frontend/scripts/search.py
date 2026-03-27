#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Design Generator - BM25 Search Engine for Test Design Catalogs
Searches .md example files and .csv rule files using BM25 ranking.

Catalogs are located at the project root (catalog/api/, catalog/frontend/).
References and format rules are located inside the skill folder.

Usage:
  python search.py "<query>" --domain api          # Search API examples
  python search.py "<query>" --domain frontend     # Search Frontend examples
  python search.py "<query>" --domain rules        # Search format rules (skill-bundled)
  python search.py --list                           # List all available examples
  python search.py --ref frontend-test-design      # Read reference file
  python search.py --ref field-templates --section "textbox,combobox"  # Read specific sections
  python search.py --list-refs                      # List available references
"""

import argparse
import sys
import io
import csv
import re
import json
import hashlib
import tempfile
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
RULES_DIR = SKILL_DIR / "data" / "rules"
MAX_RESULTS = 3

# Marker files/dirs that identify the project root
_PROJECT_MARKERS = ("catalog", "AGENTS.md", "excel_template")


def find_project_root(explicit_path=None):
    """Find project root by walking up from CWD looking for marker files.

    Markers: catalog/, AGENTS.md, excel_template/
    Falls back to CWD if nothing found within 10 levels.
    """
    if explicit_path:
        p = Path(explicit_path)
        if p.exists():
            return p

    current = Path.cwd()
    for _ in range(10):
        if any((current / m).exists() for m in _PROJECT_MARKERS):
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return Path.cwd()  # fallback


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
        if self.N == 0: return
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
            for w in doc: tf[w] += 1
            for t in tokens:
                if t in self.idf:
                    n = tf[t] * (self.k1 + 1)
                    d = tf[t] + self.k1 * (1 - self.b + self.b * self.doc_lengths[idx] / self.avgdl)
                    s += self.idf[t] * n / d
            scores.append((idx, s))
        return sorted(scores, key=lambda x: x[1], reverse=True)


# ============ CACHE ============
def _cache_key(directory):
    """Generate a hash key based on directory path + file names + modification times."""
    md_files = sorted(directory.glob("*.md"))
    parts = [str(directory)]
    for f in md_files:
        parts.append(f"{f.name}:{f.stat().st_mtime}")
    return hashlib.md5("|".join(parts).encode()).hexdigest()


def _cache_path(directory, prefix="tdg"):
    """Get the temp cache file path for a directory."""
    key = _cache_key(directory)
    return Path(tempfile.gettempdir()) / f"{prefix}_catalog_{key}.json"


def _load_cached(directory, prefix="tdg"):
    """Load cached documents + file_names if cache is valid."""
    cp = _cache_path(directory, prefix)
    if cp.exists():
        try:
            data = json.loads(cp.read_text(encoding='utf-8'))
            return data["documents"], data["file_names"], data["file_paths"]
        except (json.JSONDecodeError, KeyError):
            pass
    return None, None, None


def _save_cache(directory, documents, file_names, file_paths, prefix="tdg"):
    """Save parsed documents to cache."""
    cp = _cache_path(directory, prefix)
    try:
        cp.write_text(json.dumps({
            "documents": documents,
            "file_names": file_names,
            "file_paths": file_paths,
        }, ensure_ascii=False), encoding='utf-8')
    except OSError:
        pass  # Non-critical, skip silently


# ============ SEARCH ============
def search_md_files(query, directory, max_results=MAX_RESULTS):
    """Search .md files in directory using BM25"""
    if not directory.exists():
        return {"error": f"Directory not found: {directory}", "results": []}

    md_files = sorted(directory.glob("*.md"))
    if not md_files:
        return {"error": f"No .md files in {directory}", "results": []}

    # Try cache first
    documents, file_names, file_paths = _load_cached(directory)
    if documents is None:
        documents, file_names, file_paths = [], [], []
        for f in md_files:
            content = f.read_text(encoding='utf-8')
            documents.append(content)
            file_names.append(f.name)
            file_paths.append(str(f))
        _save_cache(directory, documents, file_names, file_paths)

    bm25 = BM25()
    bm25.fit(documents)
    ranked = bm25.score(query)

    results = []
    for idx, score in ranked[:max_results]:
        if score > 0:
            content = documents[idx]
            title_match = re.match(r'^#\s+(.+)', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else file_names[idx]
            preview = content[:800].strip()
            results.append({
                "file": file_names[idx],
                "title": title,
                "score": round(score, 2),
                "preview": preview,
                "full_path": file_paths[idx] if file_paths else str(md_files[idx])
            })

    return {
        "query": query,
        "directory": str(directory),
        "count": len(results),
        "results": results
    }


def search_csv_rules(query, rules_dir, max_results=MAX_RESULTS):
    """Search .csv rule files using BM25 (skill-bundled format rules)"""
    if not rules_dir.exists():
        return {"error": f"Rules directory not found: {rules_dir}", "results": []}

    csv_files = sorted(rules_dir.glob("*.csv"))
    if not csv_files:
        return {"error": f"No .csv files in {rules_dir}", "results": []}

    all_rows, documents = [], []
    for f in csv_files:
        with open(f, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                row['_source_file'] = f.name
                all_rows.append(row)
                documents.append(' '.join(str(v) for v in row.values()))

    bm25 = BM25()
    bm25.fit(documents)
    ranked = bm25.score(query)

    results = []
    for idx, score in ranked[:max_results]:
        if score > 0:
            results.append({**all_rows[idx], "_score": round(score, 2)})

    return {
        "query": query,
        "count": len(results),
        "results": results
    }


def list_catalog(catalog_dir):
    """List all .md files in the catalog (api/, frontend/, mobile/ subdirs)"""
    if not catalog_dir.exists():
        return f"Catalog not found: {catalog_dir}"

    lines = [f"Catalog: {catalog_dir}", ""]

    for subdir in ["api", "frontend", "mobile"]:
        sub_path = catalog_dir / subdir
        if not sub_path.exists():
            continue
        md_files = sorted(sub_path.glob("*.md"))
        lines.append(f"  {subdir}/ ({len(md_files)} files)")
        for f in md_files:
            content = f.read_text(encoding='utf-8')
            title_match = re.match(r'^#\s+(.+)', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else f.name
            lines.append(f"    {f.name} — {title}")
        lines.append("")

    return "\n".join(lines)


def format_output(result):
    """Format search results for LLM consumption"""
    if "error" in result:
        return f"Error: {result['error']}"

    lines = [f"## Search Results", f"**Query:** {result['query']} | **Found:** {result['count']}", ""]

    for i, r in enumerate(result['results'], 1):
        if 'file' in r:
            lines.append(f"### Result {i}: {r['title']}")
            lines.append(f"**File:** {r['file']} | **Score:** {r['score']}")
            lines.append(f"**Path:** {r['full_path']}")
            lines.append(f"\n```markdown\n{r['preview']}\n```\n")
        else:
            lines.append(f"### Rule {i} (score: {r.get('_score', '?')})")
            for k, v in r.items():
                if not k.startswith('_') and v:
                    lines.append(f"- **{k}:** {v}")
            lines.append("")

    if result['count'] > 0:
        lines.append("---")
        lines.append("To read full file: use `view_file` on the path above")

    return "\n".join(lines)


# ============ REFERENCES ============

# Section markers in reference files: <!-- @section: name -->
_SECTION_RE = re.compile(r'<!--\s*@section:\s*(.+?)\s*-->')


def _parse_sections(content):
    """Parse reference file into named sections using <!-- @section: name --> markers.

    Returns dict: {section_name: section_content}.
    Content before the first marker is keyed as '_preamble'.
    """
    sections = {}
    current_name = '_preamble'
    current_lines = []

    for line in content.splitlines():
        m = _SECTION_RE.match(line.strip())
        if m:
            # Save previous section
            text = '\n'.join(current_lines).strip()
            if text:
                sections[current_name] = text
            current_name = m.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Save last section
    text = '\n'.join(current_lines).strip()
    if text:
        sections[current_name] = text

    return sections


def read_reference(ref_name, section_filter=None):
    """Read a reference file, optionally filtered to specific sections.

    Args:
        ref_name: Reference file name (with or without .md)
        section_filter: Comma-separated section names to include.
                       If None, returns the entire file.
    """
    if not ref_name.endswith('.md'):
        ref_name += '.md'

    ref_path = REFS_DIR / ref_name
    if not ref_path.exists():
        return f"Reference not found: {ref_name}\nSearched: {ref_path}"

    content = ref_path.read_text(encoding='utf-8')

    if not section_filter:
        return f"## Reference: {ref_path.name}\n**Path:** {ref_path}\n\n{content}"

    # Parse sections and filter
    sections = _parse_sections(content)
    requested = [s.strip() for s in section_filter.split(',')]

    matched = []
    missing = []
    for req in requested:
        # Case-insensitive match
        found = None
        for name, text in sections.items():
            if name.lower() == req.lower():
                found = text
                break
        if found:
            matched.append(f"<!-- section: {req} -->\n{found}")
        else:
            missing.append(req)

    if not matched:
        available = [k for k in sections.keys() if k != '_preamble']
        return (f"No matching sections in {ref_name}.\n"
                f"Requested: {requested}\n"
                f"Available: {available}")

    header = f"## Reference: {ref_path.name} (sections: {', '.join(requested)})\n"
    if missing:
        header += f"**Missing sections:** {missing}\n"
    result = header + "\n" + "\n\n".join(matched)
    return result


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
    parser = argparse.ArgumentParser(description="Test Design Catalog Search")
    parser.add_argument("query", nargs="?", default="", help="Search query")
    parser.add_argument("--domain", "-d", choices=["api", "frontend", "mobile", "rules"], help="Search domain")
    parser.add_argument("--data-dir", help="Override catalog directory (default: auto-detect)")
    parser.add_argument("--project-root", help="Explicit project root path (auto-detected if omitted)")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS, help="Max results")
    parser.add_argument("--list", "-l", action="store_true", help="List available examples")
    parser.add_argument("--full", "-f", action="store_true", help="Show full file content instead of preview")
    parser.add_argument("--ref", "-r", metavar="NAME", help="Read a reference file")
    parser.add_argument("--section", "-s", metavar="SECTIONS", help="Comma-separated section names to filter (use with --ref)")
    parser.add_argument("--list-refs", action="store_true", help="List available references")

    args = parser.parse_args()

    project_root = find_project_root(args.project_root)
    catalog_dir = Path(args.data_dir) if args.data_dir else project_root / "catalog"

    if args.list_refs:
        print(list_references())
        sys.exit(0)

    if args.ref:
        print(read_reference(args.ref, section_filter=args.section))
        sys.exit(0)

    if args.list:
        print(list_catalog(catalog_dir))
        sys.exit(0)

    if not args.query:
        parser.print_help()
        sys.exit(1)

    if args.domain == "rules":
        result = search_csv_rules(args.query, RULES_DIR, args.max_results)
    elif args.domain in ("api", "frontend", "mobile"):
        result = search_md_files(args.query, catalog_dir / args.domain, args.max_results)
    else:
        # Auto: search both api + frontend, merge by score
        r_api = search_md_files(args.query, catalog_dir / "api", args.max_results)
        r_fe = search_md_files(args.query, catalog_dir / "frontend", args.max_results)
        all_results = r_api.get("results", []) + r_fe.get("results", [])
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        result = {"query": args.query, "count": len(all_results[:args.max_results]), "results": all_results[:args.max_results]}

    if args.full and result.get("results"):
        top = result["results"][0]
        if "full_path" in top:
            content = Path(top["full_path"]).read_text(encoding='utf-8')
            print(f"# Full content: {top['file']}\n")
            print(content)
        else:
            print(format_output(result))
    else:
        print(format_output(result))
