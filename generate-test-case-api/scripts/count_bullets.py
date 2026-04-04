#!/usr/bin/env python3
"""
count_bullets.py — Count expected test cases per section from test-design-api.md
and compare with actual test-cases.json output.

Usage:
  python count_bullets.py --test-design PATH [--test-cases PATH] [--json]

What it does:
  1. Parse test-design-api.md to count:
     - ## sections: each ### heading = 1 test case (for non-validate sections)
     - ### Trường X sections: each top-level bullet (- ...) = 1 test case
  2. If --test-cases provided, compare expected vs actual counts per section
  3. Report missing counts per section

Output modes:
  Default: human-readable report
  --json:  machine-readable JSON for tc-verify to consume

Exit codes:
  0 — success (or no gaps if --test-cases provided)
  2 — gaps detected (expected > actual for at least one section)
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


def parse_expected(path):
    """Parse test-design-api.md and return expected counts.

    Returns list of:
    {
        "section": "Kiểm tra Validate",
        "subsections": [
            {"name": "slaVersionId", "heading": "Trường slaVersionId", "expected": 15},
            ...
        ],
        "total_expected": 245
    }

    For non-validate sections (token, endpoint, chức năng, ngoại lệ):
    each ### heading = 1 test case, no bullet counting needed.
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()

    sections = []
    current_section = None
    current_sub = None
    is_validate_section = False

    for line in content.split("\n"):
        m2 = re.match(r"^##\s+(.+)$", line)
        if m2:
            heading = m2.group(1).strip()
            is_validate_section = "validate" in heading.lower()
            current_section = {
                "section": heading,
                "subsections": [],
                "total_expected": 0,
            }
            sections.append(current_section)
            current_sub = None
            continue

        m3 = re.match(r"^###\s+(.+)$", line)
        if m3 and current_section is not None:
            sub_heading = m3.group(1).strip()

            if is_validate_section:
                fm = re.match(r"^Trường\s+(.+)$", sub_heading)
                field_name = fm.group(1).strip() if fm else sub_heading
                current_sub = {
                    "name": field_name,
                    "heading": sub_heading,
                    "expected": 0,
                }
                current_section["subsections"].append(current_sub)
            else:
                # Non-validate: each ### = 1 test case
                current_sub = {
                    "name": sub_heading,
                    "heading": sub_heading,
                    "expected": 1,
                }
                current_section["subsections"].append(current_sub)
                current_section["total_expected"] += 1
            continue

        # Count top-level bullets (- ...) inside validate field sections
        if is_validate_section and current_sub is not None:
            mb = re.match(r"^- (.+)$", line)
            if mb:
                current_sub["expected"] += 1
                current_section["total_expected"] += 1

    return sections


def _load_display_to_tech_map(inventory_path):
    """Load inventory and build displayName -> [techName, ...] reverse map."""
    if not inventory_path or not os.path.exists(inventory_path):
        return {}
    try:
        with open(inventory_path, encoding="utf-8") as f:
            inv = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

    result = {}
    for category in ("fieldConstraints", "fileContentFields"):
        for item in inv.get(category, []):
            tech = item.get("name", "")
            display = item.get("displayName", "")
            if tech and display:
                result.setdefault(display.lower(), []).append(tech.lower())
    return result


def count_actual(test_cases, sections, inventory_path=None):
    """Count actual test cases per section by matching testSuiteName and testCaseName.

    Returns sections with added 'actual' counts.
    """
    display_to_tech = _load_display_to_tech_map(inventory_path)

    # Build lookup: section_heading -> section index
    section_lookup = {}
    for i, sec in enumerate(sections):
        section_lookup[sec["section"].lower()] = i

    # Count per section
    section_counts = [0] * len(sections)
    # Count per subsection (for validate fields)
    sub_counts = {}
    for i, sec in enumerate(sections):
        for j, sub in enumerate(sec["subsections"]):
            sub_counts[(i, j)] = 0

    matched = 0
    for tc in test_cases:
        suite = tc.get("testSuiteName", "").lower()
        case_name = tc.get("testCaseName", "")
        case_lower = case_name.lower()

        # Find matching section
        sec_idx = section_lookup.get(suite)
        if sec_idx is not None:
            section_counts[sec_idx] += 1
            matched += 1

            # Try to match to a subsection (for validate: match by field name)
            sec = sections[sec_idx]
            for j, sub in enumerate(sec["subsections"]):
                sub_name_lower = sub["name"].lower()
                # Direct match: displayName in testCaseName
                if sub_name_lower in case_lower:
                    sub_counts[(sec_idx, j)] += 1
                    break
                # Inventory match: techName in testCaseName
                tech_names = display_to_tech.get(sub_name_lower, [])
                if any(tn in case_lower for tn in tech_names):
                    sub_counts[(sec_idx, j)] += 1
                    break

    # Write actual counts back
    for i, sec in enumerate(sections):
        sec["actual"] = section_counts[i]
        sec["missing"] = max(0, sec["total_expected"] - section_counts[i])
        for j, sub in enumerate(sec["subsections"]):
            sub["actual"] = sub_counts.get((i, j), 0)

    return sections, matched


def main():
    parser = argparse.ArgumentParser(description="Count expected test cases from test-design")
    parser.add_argument("--test-design", required=True, dest="test_design")
    parser.add_argument("--test-cases", default="", dest="test_cases")
    parser.add_argument("--inventory", default="", help="Path to inventory.json for fieldName->displayName mapping")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not os.path.exists(args.test_design):
        print(f"ERROR: test-design not found: {args.test_design}", file=sys.stderr)
        sys.exit(1)

    sections = parse_expected(args.test_design)
    grand_total = sum(s["total_expected"] for s in sections)

    # Compare with actual if provided
    has_gaps = False
    if args.test_cases:
        if not os.path.exists(args.test_cases):
            print(f"ERROR: test-cases not found: {args.test_cases}", file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.test_cases, encoding="utf-8") as f:
                test_cases = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"ERROR: cannot read test-cases: {e}", file=sys.stderr)
            sys.exit(1)

        sections, matched = count_actual(test_cases, sections, args.inventory)
        total_actual = len(test_cases)
        has_gaps = any(s.get("missing", 0) > 0 for s in sections)

    if args.json:
        output = {
            "expected_total": grand_total,
            "sections": sections,
        }
        if args.test_cases:
            output["actual_total"] = total_actual
            output["matched"] = matched
            output["has_gaps"] = has_gaps
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"Expected total: {grand_total} test cases\n")
        for sec in sections:
            line = f"  ## {sec['section']}: {sec['total_expected']} expected"
            if args.test_cases:
                actual = sec.get("actual", "?")
                missing = sec.get("missing", 0)
                status = "OK" if missing == 0 else f"MISSING {missing}"
                line += f", actual {actual} [{status}]"
            print(line)

            # Show per-field detail for validate sections with gaps
            if args.test_cases and sec.get("missing", 0) > 0:
                for sub in sec["subsections"]:
                    sub_missing = max(0, sub["expected"] - sub.get("actual", 0))
                    if sub_missing > 0:
                        print(f"    - {sub['name']}: expected {sub['expected']}, actual {sub.get('actual', 0)}, missing {sub_missing}")

        if args.test_cases:
            print(f"\nActual total: {total_actual}")
            print(f"Matched to sections: {matched}")
            if has_gaps:
                total_missing = sum(s.get("missing", 0) for s in sections)
                print(f"Total missing: {total_missing}")

    sys.exit(2 if has_gaps else 0)


if __name__ == "__main__":
    main()
