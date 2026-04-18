#!/usr/bin/env python3
"""
inject_sql.py -- Deterministically inject SQL blocks from test-design-api.md into batch-3.json.

Logic:
- Parse ### headings inside ## Kiem tra chuc nang and ## Kiem tra ngoai le sections
- For each heading that has a SQL: line -> collect subsequent lines as SQL text
  (until next ### or ## heading)
- For each test case in batch-3.json:
  - Match by testCaseName == heading text (strip + normalize whitespace)
  - If SQL found AND expectedResult does not already contain 'Kiem tra DB':
    Append newline + '2. Kiem tra DB:' block to expectedResult
- Write updated batch-3.json in-place only when injected_count > 0
- Print summary: Injected SQL into N/{total} test cases
"""

import argparse
import json
import re
import sys


def parse_args():
    p = argparse.ArgumentParser(description="Inject SQL blocks from test-design-api.md into batch-3.json")
    p.add_argument("--test-design", required=True, help="Path to test-design-api.md")
    p.add_argument("--batch", required=True, help="Path to batch-3.json")
    return p.parse_args()


def extract_target_sections(md_text: str) -> str:
    """
    Return concatenated text of ## Kiem tra chuc nang and ## Kiem tra ngoai le sections.
    Stops each section at the next ## heading or end of file.
    """
    target_patterns = [
        re.compile(r'^##\s+Ki\u1ec3m tra ch\u1ee9c n\u0103ng\s*$', re.MULTILINE | re.IGNORECASE),
        re.compile(r'^##\s+Ki\u1ec3m tra ngo\u1ea1i l\u1ec7\s*$', re.MULTILINE | re.IGNORECASE),
    ]

    collected = []
    for pattern in target_patterns:
        m = pattern.search(md_text)
        if not m:
            continue
        start = m.end()
        next_section = re.search(r'^##\s+', md_text[start:], re.MULTILINE)
        if next_section:
            collected.append(md_text[start: start + next_section.start()])
        else:
            collected.append(md_text[start:])

    return "\n".join(collected)


def normalize_ws(text: str) -> str:
    """Normalize internal whitespace for matching."""
    return re.sub(r'\s+', ' ', text).strip()


def parse_headings_with_sql(section_text: str) -> dict:
    """
    Parse ### headings from the section text.
    Returns dict: normalized_heading_text -> sql_string (or None if no SQL: found).

    SQL block: lines after a line whose stripped value == 'SQL:' until next ### or ## heading.
    """
    result = {}
    # Split on ### headings
    parts = re.split(r'^###\s+', section_text, flags=re.MULTILINE)
    for part in parts:
        if not part.strip():
            continue
        lines = part.split('\n')
        heading = lines[0].strip()
        if not heading:
            continue
        body_lines = lines[1:]

        sql_text = None
        in_sql = False
        sql_lines = []

        for line in body_lines:
            stripped = line.strip()
            if in_sql:
                # Stop collecting if we hit a new ## heading
                if stripped.startswith('## '):
                    break
                sql_lines.append(line.rstrip())
            else:
                # Check for SQL: marker line
                if stripped == 'SQL:' or stripped == 'SQL:  ':
                    in_sql = True

        if in_sql and sql_lines:
            # Strip leading/trailing blank lines from collected SQL
            while sql_lines and not sql_lines[0].strip():
                sql_lines.pop(0)
            while sql_lines and not sql_lines[-1].strip():
                sql_lines.pop()
            if sql_lines:
                sql_text = '\n'.join(sql_lines)

        normalized = normalize_ws(heading)
        result[normalized] = sql_text

    return result


def inject(test_design_path: str, batch_path: str):
    with open(test_design_path, encoding="utf-8") as f:
        md_text = f.read()

    section_text = extract_target_sections(md_text)
    if not section_text.strip():
        print("WARNING: ## Kiem tra chuc nang / ## Kiem tra ngoai le sections not found in test design -- skipping inject_sql")
        return

    headings = parse_headings_with_sql(section_text)
    if not headings:
        print("WARNING: No ### headings found in target sections -- skipping inject_sql")
        return

    with open(batch_path, encoding="utf-8") as f:
        batch = json.load(f)

    total = len(batch)
    injected_count = 0
    skipped_headings = []

    # Build reverse lookup: normalized heading -> sql
    # (headings without SQL will be in skipped list)
    sql_map = {}
    for heading, sql in headings.items():
        if sql is None:
            skipped_headings.append(heading)
        else:
            sql_map[heading] = sql

    for tc in batch:
        tc_name = normalize_ws(tc.get("testCaseName", ""))
        if tc_name not in sql_map:
            continue
        sql = sql_map[tc_name]
        expected = tc.get("expectedResult", "")
        if "Ki\u1ec3m tra DB" in expected:
            # Already has DB check -- do not duplicate
            continue
        db_block = "\n2. Ki\u1ec3m tra DB:\n  2.1. Ch\u1ea1y SQL:\n  " + sql
        tc["expectedResult"] = expected.rstrip() + db_block
        injected_count += 1

    for h in skipped_headings:
        print(f"WARNING: No SQL block found under ### {h} -- skipping this heading")

    if injected_count == 0:
        print(f"inject_sql: nothing to write -- 0/{total} test cases updated")
        return

    with open(batch_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)

    print(f"inject_sql: Injected SQL into {injected_count}/{total} test cases")
    if skipped_headings:
        print(f"inject_sql: {len(skipped_headings)} heading(s) skipped (no SQL block in test design)")


def main():
    args = parse_args()
    try:
        inject(args.test_design, args.batch)
    except Exception as e:
        print(f"WARNING: inject_sql.py failed -- {e}", file=sys.stderr)
        sys.exit(0)  # non-fatal -- workflow continues


if __name__ == "__main__":
    main()
