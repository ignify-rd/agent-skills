#!/usr/bin/env python3
"""
normalize_suites.py — Normalize testSuiteName in test-cases JSON using test-design headings.

Problem: tc-validate sub-agents sometimes generate verbose/garbage testSuiteName values
instead of clean section headings from the test-design. This script deterministically
fixes them by mapping each test case to the correct ## section from test-design-api.md.

Usage:
  python normalize_suites.py --test-design PATH --test-cases PATH [--inventory PATH] [--dry-run]

What it does:
  1. Parse test-design-api.md to extract ## sections and ### field headings
  2. Build a mapping: field name / subheading -> correct testSuiteName (the ## heading)
  3. For each test case in JSON, match to the correct ## heading and normalize
  4. Report changes and overwrite the JSON file

Exit codes:
  0 — success
  1 — error
"""

import os
import sys
import re
import json
import io
import argparse

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def parse_test_design(path):
    """Parse test-design-api.md -> list of sections with fields and bullet case names."""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    sections = []
    current_section = None
    current_field = None

    for line in content.split("\n"):
        m2 = re.match(r"^##\s+(.+)$", line)
        if m2:
            current_section = {
                "heading": m2.group(1).strip(),
                "fields": [],
                "subheadings": [],
                "case_names": [],
            }
            sections.append(current_section)
            current_field = None
            continue

        m3 = re.match(r"^###\s+(.+)$", line)
        if m3 and current_section is not None:
            sub = m3.group(1).strip()
            current_section["subheadings"].append(sub)
            fm = re.match(r"^Trường\s+(.+)$", sub)
            if fm:
                current_field = fm.group(1).strip()
                current_section["fields"].append(current_field)
            else:
                current_field = None
            continue

        # Top-level bullet = test case name (inside a ### field section)
        mb = re.match(r"^- (.+)$", line)
        if mb and current_section is not None:
            current_section["case_names"].append(mb.group(1).strip())

    return sections


def load_inventory_field_map(inventory_path, field_map):
    """Load inventory and add fieldName -> heading mappings via displayName.

    inventory.json may have:
      - fieldConstraints[].name  (e.g. "slaVersionId")
      - fileContentFields[].name (e.g. "debitAccount") + .displayName (e.g. "Tài khoản chuyển")

    If displayName is in field_map, we also map the technical name to the same heading.
    """
    if not inventory_path or not os.path.exists(inventory_path):
        return

    try:
        with open(inventory_path, encoding="utf-8") as f:
            inv = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    for category in ("fieldConstraints", "fileContentFields"):
        for item in inv.get(category, []):
            tech_name = item.get("name", "")
            display_name = item.get("displayName", "")

            if not tech_name:
                continue

            # If displayName matches a known field -> map tech_name to same heading
            if display_name and display_name.lower() in field_map:
                heading = field_map[display_name.lower()]
                field_map[tech_name.lower()] = heading


def build_suite_map(sections, inventory_path=None):
    """Build lookup structures for matching test cases to suite names."""
    field_map = {}        # field_name_lower -> heading
    subheading_map = {}   # subheading_lower -> heading
    case_name_map = {}    # case_name_lower -> heading

    for section in sections:
        heading = section["heading"]
        for field in section["fields"]:
            field_map[field.lower()] = heading
        for sub in section["subheadings"]:
            subheading_map[sub.lower()] = heading
        for cn in section["case_names"]:
            case_name_map[cn.lower()] = heading

    # Enrich field_map with inventory technical names
    load_inventory_field_map(inventory_path, field_map)

    return field_map, subheading_map, case_name_map


def normalize(test_cases, sections, inventory_path=None):
    """Normalize testSuiteName for each test case. Returns (cases, changes_count, details)."""
    field_map, subheading_map, case_name_map = build_suite_map(sections, inventory_path)
    valid_suites = {s["heading"] for s in sections}

    changes = 0
    details = []

    for tc in test_cases:
        old_suite = tc.get("testSuiteName", "")
        case_name = tc.get("testCaseName", "")

        if old_suite in valid_suites:
            continue

        new_suite = _resolve_suite(case_name, old_suite, field_map, subheading_map, case_name_map, valid_suites)

        if new_suite and new_suite != old_suite:
            tc["testSuiteName"] = new_suite
            changes += 1
            if len(details) < 20:
                old_display = old_suite[:60] + "..." if len(old_suite) > 60 else old_suite
                details.append(f"  '{old_display}' -> '{new_suite}'")

    return test_cases, changes, details


def _resolve_suite(case_name, old_suite, field_map, subheading_map, case_name_map, valid_suites):
    """Try multiple strategies to resolve the correct suite name."""
    case_lower = case_name.lower()

    # 1. Exact match on case_name from test-design bullets
    if case_lower in case_name_map:
        return case_name_map[case_lower]

    # 2. Extract field name from testCaseName patterns
    for pattern in [
        r"(?:truyền\s+)?trường\s+(\S+)",          # "trường slaVersionId"
        r"nội dung file\s+.*?trường\s+(.+?)(?:\s|$)",  # fileContent field
        r"^(\w+?)_",                                # "fieldName_description"
    ]:
        m = re.search(pattern, case_name, re.IGNORECASE)
        if m:
            field = m.group(1).strip()
            if field.lower() in field_map:
                return field_map[field.lower()]

    # 3. Check if testCaseName contains any known display field name (longer names first)
    sorted_fields = sorted(field_map.keys(), key=len, reverse=True)
    for field_lower in sorted_fields:
        if field_lower in case_lower:
            return field_map[field_lower]

    # 4. Match against ### subheadings
    for sub_lower, heading in subheading_map.items():
        if case_lower.startswith(sub_lower) or sub_lower in case_lower:
            return heading

    # 5. Extract field name from old_suite "Kiểm tra trường X" pattern
    m_suite = re.match(r"kiểm tra trường\s+(\S+)", old_suite, re.IGNORECASE)
    if m_suite:
        suite_field = m_suite.group(1).strip().lower()
        if suite_field in field_map:
            return field_map[suite_field]

    # 6. Check if old_suite contains a valid heading as substring
    old_lower = old_suite.lower()
    for heading in valid_suites:
        if heading.lower() in old_lower:
            return heading

    return ""


def main():
    parser = argparse.ArgumentParser(description="Normalize testSuiteName using test-design headings")
    parser.add_argument("--test-design", required=True, dest="test_design")
    parser.add_argument("--test-cases", required=True, dest="test_cases")
    parser.add_argument("--inventory", default="", help="Path to inventory.json for fieldName->displayName mapping")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run")
    args = parser.parse_args()

    if not os.path.exists(args.test_design):
        print(f"ERROR: test-design not found: {args.test_design}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.test_cases):
        print(f"ERROR: test-cases not found: {args.test_cases}", file=sys.stderr)
        sys.exit(1)

    sections = parse_test_design(args.test_design)
    print(f"Sections found: {len(sections)}")
    for s in sections:
        fc = f", {len(s['fields'])} fields" if s["fields"] else ""
        print(f"  ## {s['heading']} ({len(s['subheadings'])} subheadings{fc})")

    try:
        with open(args.test_cases, encoding="utf-8") as f:
            test_cases = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: cannot read test-cases: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(test_cases, list):
        print("ERROR: test-cases must be a JSON array", file=sys.stderr)
        sys.exit(1)

    test_cases, changes, details = normalize(test_cases, sections, args.inventory)

    print(f"\nTotal test cases: {len(test_cases)}")
    print(f"Suite names normalized: {changes}")

    if details:
        print("\nSample changes:")
        for d in details:
            print(d)

    if changes == 0:
        print("\nNo changes needed.")
        return

    if args.dry_run:
        print(f"\nDRY RUN — would normalize {changes} suite names")
        return

    try:
        with open(args.test_cases, "w", encoding="utf-8") as f:
            json.dump(test_cases, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"ERROR: cannot write test-cases: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n=> Normalized {changes} suite names -> {args.test_cases}")


if __name__ == "__main__":
    main()
