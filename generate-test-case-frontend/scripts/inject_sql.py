#!/usr/bin/env python3
"""
inject_sql.py — Deterministically inject SQL from test-design-frontend.md into batch-3.json.

Logic:
- Parse ### headings inside ## Kiem tra chuc nang section of test-design-frontend.md
- For each heading that has a SQL code block -> find matching test cases in batch-3.json
  by testSuiteName == heading text
- Copy SQL verbatim into "query" field of matching test cases
- Guard: only operates on ## Kiem tra chuc nang (never ## Kiem tra Validate)
- If a heading has no SQL block -> skip it and print a warning
"""

import argparse
import json
import re
import sys


def parse_args():
    p = argparse.ArgumentParser(description="Inject SQL from test design into batch-3.json")
    p.add_argument("--test-design", required=True, help="Path to test-design-frontend.md")
    p.add_argument("--batch", required=True, help="Path to batch-3.json")
    return p.parse_args()


def extract_function_section(md_text: str) -> str:
    """
    Return the text of ## Kiem tra chuc nang section only.
    Stops at the next ## heading or end of file.
    Skips ## Kiem tra Validate entirely.
    """
    # Match section header (handles diacritics)
    pattern = re.compile(
        r'^##\s+Ki\u1ec3m tra ch\u1ee9c n\u0103ng\s*$',
        re.MULTILINE | re.IGNORECASE
    )
    m = pattern.search(md_text)
    if not m:
        return ""

    start = m.end()
    # Find next ## heading
    next_section = re.search(r'^##\s+', md_text[start:], re.MULTILINE)
    if next_section:
        return md_text[start: start + next_section.start()]
    return md_text[start:]


def parse_headings_with_sql(section_text: str) -> dict:
    """
    Parse ### headings from the section text.
    Returns dict: heading_text -> sql_string (or None if no SQL block found).
    """
    result = {}
    # Split on ### headings
    parts = re.split(r'^###\s+', section_text, flags=re.MULTILINE)
    for part in parts:
        if not part.strip():
            continue
        # First line is the heading
        lines = part.split('\n', 1)
        heading = lines[0].strip()
        if not heading:
            continue
        body = lines[1] if len(lines) > 1 else ""
        # Find first SQL code block
        sql_match = re.search(r'```sql\s*\n(.*?)```', body, re.DOTALL | re.IGNORECASE)
        if sql_match:
            result[heading] = sql_match.group(1).strip()
        else:
            result[heading] = None
    return result


def inject(test_design_path: str, batch_path: str):
    with open(test_design_path, encoding="utf-8") as f:
        md_text = f.read()

    func_section = extract_function_section(md_text)
    if not func_section:
        print("WARNING: ## Kiem tra chuc nang section not found in test design — skipping inject_sql")
        return

    headings = parse_headings_with_sql(func_section)
    if not headings:
        print("WARNING: No ### headings found in ## Kiem tra chuc nang — skipping inject_sql")
        return

    with open(batch_path, encoding="utf-8") as f:
        batch = json.load(f)

    injected_count = 0
    skipped_headings = []

    for heading, sql in headings.items():
        if sql is None:
            skipped_headings.append(heading)
            continue

        matched = False
        for tc in batch:
            if tc.get("testSuiteName", "").strip() == heading:
                tc["query"] = sql
                injected_count += 1
                matched = True

        if not matched:
            print(f"WARNING: No test cases matched testSuiteName='{heading}' in batch — SQL not injected for this heading")

    for h in skipped_headings:
        print(f"WARNING: No SQL block found under ### {h} — skipping this heading")

    if injected_count == 0:
        print("inject_sql: nothing to write — 0 test cases updated")
        return

    with open(batch_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)

    print(f"inject_sql: {injected_count} test case(s) updated with 'query' field")
    if skipped_headings:
        print(f"inject_sql: {len(skipped_headings)} heading(s) skipped (no SQL block in test design)")


def main():
    args = parse_args()
    try:
        inject(args.test_design, args.batch)
    except Exception as e:
        print(f"WARNING: inject_sql.py failed — {e}", file=sys.stderr)
        sys.exit(0)  # non-fatal — workflow continues


if __name__ == "__main__":
    main()
