#!/usr/bin/env python3
"""
normalize_suites.py — Normalize testSuiteName in test-cases JSON using test-design headings.

Problem: tc-validate sub-agents sometimes generate verbose/garbage testSuiteName values
instead of clean section headings from the test-design. This script deterministically
fixes them by mapping each test case to the correct ## section from test-design-api.md.
Also reorders test cases to match ## section + ### subheading order from test-design.

Usage:
  python normalize_suites.py --test-design PATH --test-cases PATH [--inventory PATH] [--dry-run]

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
            continue

        m3 = re.match(r"^###\s+(.+)$", line)
        if m3 and current_section is not None:
            sub = m3.group(1).strip()
            current_section["subheadings"].append(sub)
            fm = re.match(r"^Trường\s+(.+)$", sub)
            if fm:
                current_section["fields"].append(fm.group(1).strip())
            continue

        mb = re.match(r"^- (.+)$", line)
        if mb and current_section is not None:
            current_section["case_names"].append(mb.group(1).strip())

    return sections


def load_inventory_field_map(inventory_path, field_map):
    """Load inventory and add fieldName -> heading mappings via displayName."""

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
            if display_name and display_name.lower() in field_map:
                heading = field_map[display_name.lower()]
                field_map[tech_name.lower()] = heading


def build_suite_map(sections, inventory_path=None):
    """Build lookup structures for matching test cases to suite names."""
    field_map = {}
    subheading_map = {}
    case_name_map = {}

    for section in sections:
        heading = section["heading"]
        for field in section["fields"]:
            field_map[field.lower()] = heading
        for sub in section["subheadings"]:
            subheading_map[sub.lower()] = heading
        for cn in section["case_names"]:
            case_name_map[cn.lower()] = heading

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

        # Preserve per-field validate sub-suites ("Kiểm tra trường X") — do NOT
        # flatten them to the parent section heading. upload_gsheet.py uses them
        # to render gray field-level sub-headers inside the validate section.
        if re.match(r"kiểm tra trường\s+\S", old_suite, re.IGNORECASE):
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

    if case_lower in case_name_map:
        return case_name_map[case_lower]

    # Extract field name from patterns like "trường X" or "nội dung file ... trường X"
    m = re.search(r"(?:truyền\s+)?trường\s+(.+?)(?:\s|$)", case_name, re.IGNORECASE)
    if m:
        field = m.group(1).strip()
        if field.lower() in field_map:
            return field_map[field.lower()]

    # Check if testCaseName contains any known display field name (longer names first)
    sorted_fields = sorted(field_map.keys(), key=len, reverse=True)
    for field_lower in sorted_fields:
        if field_lower in case_lower:
            return field_map[field_lower]

    # Match against ### subheadings
    for sub_lower, heading in subheading_map.items():
        if case_lower.startswith(sub_lower) or sub_lower in case_lower:
            return heading

    # Extract field name from old_suite "Kiểm tra trường X" pattern
    m_suite = re.match(r"kiểm tra trường\s+(.+?)(?:\s|$)", old_suite, re.IGNORECASE)
    if m_suite:
        suite_field = m_suite.group(1).strip().lower()
        if suite_field in field_map:
            return field_map[suite_field]

    # Check if old_suite contains a valid heading as substring
    old_lower = old_suite.lower()
    for heading in valid_suites:
        if heading.lower() in old_lower:
            return heading

    return ""


def _extract_field_from_case(case_name, sections):
    """Extract field/subheading name + index from testCaseName for ordering purposes."""
    case_lower = case_name.lower()

    # 1. Try exact subheading/field match (longer names first)
    all_subs = []
    for section in sections:
        for sub in section["subheadings"]:
            all_subs.append((sub, section["heading"], section["subheadings"].index(sub)))
        for field in section["fields"]:
            all_subs.append((field, section["heading"], section["fields"].index(field)))
    all_subs.sort(key=lambda x: len(x[0]), reverse=True)

    for sub, heading, idx in all_subs:
        if sub.lower() in case_lower or case_lower.startswith(sub.lower()):
            return heading, sub, idx

    # 2. Pattern: "Để trống Tài khoản chuyển" or "Nhập Tài khoản chuyển toàn ký tự"
    #    Match after the leading "Để trống" / "Nhập" keywords
    m = re.search(
        r"(?:để trống|nhập|nhập\s+file|bỏ trống)\s+(.+?)(?:\s|,|toàn|nội dung|$)",
        case_lower,
    )
    if m:
        field_part = m.group(1).strip()
        # Strip leading numbers like "2.1." or "2.1 " -> "Tài khoản chuyển"
        field_part = re.sub(r"^\d+[\.\)]\s*", "", field_part)
        # Now match against known field names
        for sub, heading, idx in all_subs:
            if field_part in sub.lower():
                return heading, sub, idx
        for sub, heading, idx in all_subs:
            if sub.lower() in field_part:
                return heading, sub, idx

    # 3. Pattern: "Kiểm tra truyền file có dung lượng..." -> belongs to "Trường File upload"
    #    Also "Kiểm tra truyền file không có dữ liệu", "Kiểm tra truyền file có số lượng bản ghi..."
    if re.search(r"truyền\s+file|upload\s+file|file\s+upload|truyền\s+file\s", case_lower):
        # Look for "Trường File upload" subheading
        for sub, heading, idx in all_subs:
            if "file upload" in sub.lower():
                return heading, sub, idx

    return None, None, None


def reorder_by_test_design(test_cases, sections):
    """
    Reorder test cases to match ## section order AND ### subheading order from test-design.
    Within each ## section, test cases are sorted by their ### subheading order.
    Returns (reordered_cases, changed_order).
    """
    if not sections:
        return test_cases, False

    suite_order = [s["heading"] for s in sections]

    def sort_key(tc):
        suite = tc.get("testSuiteName", "")
        case_name = tc.get("testCaseName", "")

        suite_idx = suite_order.index(suite) if suite in suite_order else 999
        _, _, sub_idx = _extract_field_from_case(case_name, sections)
        if sub_idx is None:
            sub_idx = 999

        return (suite_idx, sub_idx)

    original_order = [
        (tc.get("testSuiteName", ""), tc.get("testCaseName", ""))
        for tc in test_cases
    ]
    reordered = sorted(test_cases, key=sort_key)
    new_order = [
        (tc.get("testSuiteName", ""), tc.get("testCaseName", ""))
        for tc in reordered
    ]

    return reordered, original_order != new_order


def main():
    parser = argparse.ArgumentParser(description="Normalize testSuiteName using test-design headings")
    parser.add_argument("--test-design", required=True, dest="test_design")
    parser.add_argument("--test-cases", required=True, dest="test_cases")
    parser.add_argument("--inventory", default="", help="Path to inventory.json")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run")
    args = parser.parse_args()

    if not os.path.exists(args.test_design):
        print("ERROR: test-design not found: " + args.test_design, file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.test_cases):
        print("ERROR: test-cases not found: " + args.test_cases, file=sys.stderr)
        sys.exit(1)

    sections = parse_test_design(args.test_design)
    print("Sections found: " + str(len(sections)))
    for s in sections:
        fc = ", " + str(len(s["fields"])) + " fields" if s["fields"] else ""
        print("  ## " + s["heading"] + " (" + str(len(s["subheadings"])) + " subheadings" + fc + ")")

    try:
        with open(args.test_cases, encoding="utf-8") as f:
            test_cases = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print("ERROR: cannot read test-cases: " + str(e), file=sys.stderr)
        sys.exit(1)

    if not isinstance(test_cases, list):
        print("ERROR: test-cases must be a JSON array", file=sys.stderr)
        sys.exit(1)

    test_cases, changes, details = normalize(test_cases, sections, args.inventory or None)

    print("\nTotal test cases: " + str(len(test_cases)))
    print("Suite names normalized: " + str(changes))

    if details:
        print("\nSample changes:")
        for d in details:
            print(d)

    test_cases, order_changed = reorder_by_test_design(test_cases, sections)
    if order_changed:
        print("\nSuite + subheading order re-aligned to test-design")

    if changes == 0 and not order_changed:
        print("\nNo changes needed.")
        return

    if args.dry_run:
        print("\nDRY RUN — would normalize " + str(changes) + " suite names")
        return

    try:
        with open(args.test_cases, "w", encoding="utf-8") as f:
            json.dump(test_cases, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print("ERROR: cannot write test-cases: " + str(e), file=sys.stderr)
        sys.exit(1)

    print("\n=> Normalized " + str(changes) + " suite names -> " + args.test_cases)


if __name__ == "__main__":
    main()
