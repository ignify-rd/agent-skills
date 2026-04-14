#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assign_lv_ids.py — Group cases by testSuiteName, assign sequential testcaseId,
and recompute summary based on LV fields.

Steps:
  1. Group test cases by testSuiteName (preserving first-seen suite order + case order within each suite)
  2. Assign testcaseId = "FE_1", "FE_2", ... (sequential after grouping)
  3. Recompute summary = testcaseLV3 if non-empty; else testcaseLV2
  4. Compute testCaseName:
       - If template has testcaseLV1/LV2/LV3 columns → "{testcaseId}_{LV1}_{LV2}_{LV3}"
       - If template only has testCaseName (no LV columns) → just summary (clean test case name)

Usage:
  python assign_lv_ids.py --file test-cases.json
  python assign_lv_ids.py --file test-cases.json --prefix TC
  python assign_lv_ids.py --file test-cases.json --test-design path/to/test-design.md
  python assign_lv_ids.py --file test-cases.json --structure path/to/structure.json
"""

import argparse
import json
import os
import re
import sys
import io
from collections import OrderedDict

# Force UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def find_structure_json(start_path):
    """Walk up from start_path looking for excel_template/*/structure.json.
    Returns path to first match, or None if not found."""
    current = os.path.abspath(start_path)
    if os.path.isfile(current):
        current = os.path.dirname(current)

    for _ in range(8):  # max 8 levels up
        for sub in ('frontend', 'api', '.'):
            candidate = os.path.join(current, 'excel_template', sub, 'structure.json')
            if os.path.isfile(candidate):
                return candidate
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def template_has_lv_columns(structure_path):
    """Return True if structure.json columnMapping contains testcaseLV1/LV2/LV3."""
    if not structure_path or not os.path.isfile(structure_path):
        return True  # unknown → assume LV formula (safe default)
    try:
        with open(structure_path, encoding='utf-8') as f:
            structure = json.load(f)
        col_map = structure.get('columnMapping', {})
        return any(k in col_map for k in ('testcaseLV1', 'testcaseLV2', 'testcaseLV3'))
    except Exception:
        return True  # parse error → safe default


def parse_suite_order_from_test_design(path):
    """Parse test design to get ordered list of ## headings and ### subheadings.
    Returns list of (name, level) tuples preserving document order."""
    if not path or not os.path.isfile(path):
        return []

    order = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            m2 = re.match(r'^##\s+(.+)$', line)
            if m2:
                order.append(m2.group(1).strip())
                continue
            m3 = re.match(r'^###\s+(.+)$', line)
            if m3:
                order.append(m3.group(1).strip())
    return order


def group_by_suite(test_cases, suite_order=None):
    """Group test cases by testSuiteName, preserving first-seen order.
    If suite_order is provided (from test design), use it to determine group order.
    Returns flat list with cases grouped by suite."""

    # Collect groups preserving first-seen order
    groups = OrderedDict()  # suite_name -> [tc, ...]
    for tc in test_cases:
        suite = tc.get('testSuiteName', '')
        if suite not in groups:
            groups[suite] = []
        groups[suite].append(tc)

    if not suite_order:
        # No test design order — just return grouped by first-seen order
        result = []
        for suite_cases in groups.values():
            result.extend(suite_cases)
        return result

    # Sort groups by test design order
    suite_rank = {}
    for idx, name in enumerate(suite_order):
        if name not in suite_rank:
            suite_rank[name] = idx
        # Also index lowercase for case-insensitive matching
        if name.lower() not in suite_rank:
            suite_rank[name.lower()] = idx

    def group_sort_key(suite_name):
        if suite_name in suite_rank:
            return suite_rank[suite_name]
        if suite_name.lower() in suite_rank:
            return suite_rank[suite_name.lower()]
        return 9999

    sorted_suites = sorted(groups.keys(), key=group_sort_key)

    result = []
    for suite in sorted_suites:
        result.extend(groups[suite])
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Group by suite, assign sequential testcaseId, recompute summary'
    )
    parser.add_argument('--file', required=True, help='Path to test-cases.json')
    parser.add_argument('--prefix', default='FE', help='ID prefix (default: FE)')
    parser.add_argument('--test-design', default='', dest='test_design',
                        help='Path to test-design .md for suite ordering (optional)')
    parser.add_argument('--structure', default='', dest='structure',
                        help='Path to structure.json to detect LV columns (optional; auto-discovered if omitted)')
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f'ERROR: file not found: {args.file}', file=sys.stderr)
        sys.exit(1)

    with open(args.file, encoding='utf-8') as f:
        test_cases = json.load(f)

    if not isinstance(test_cases, list):
        print(f'ERROR: {args.file} must be a JSON array', file=sys.stderr)
        sys.exit(1)

    # Resolve structure.json path + detect whether template uses LV columns
    structure_path = args.structure or find_structure_json(args.file)
    use_lv_formula = template_has_lv_columns(structure_path)
    if structure_path:
        mode = 'LV formula' if use_lv_formula else 'simple name (no LV columns in template)'
        print(f'Structure: {structure_path} → testCaseName mode: {mode}')
    else:
        print('Structure: not found → using LV formula (default)')

    # Step 1: Parse test design for suite ordering (if provided)
    suite_order = parse_suite_order_from_test_design(args.test_design)
    if suite_order:
        print(f'Suite order from test design: {len(suite_order)} entries')

    # Step 2: Group cases by testSuiteName (deterministic ordering)
    original_suites = []
    for tc in test_cases:
        s = tc.get('testSuiteName', '')
        if not original_suites or original_suites[-1] != s:
            original_suites.append(s)

    test_cases = group_by_suite(test_cases, suite_order or None)

    regrouped_suites = []
    for tc in test_cases:
        s = tc.get('testSuiteName', '')
        if not regrouped_suites or regrouped_suites[-1] != s:
            regrouped_suites.append(s)

    reordered = original_suites != regrouped_suites

    # Step 3: Assign sequential IDs + recompute summary + compute name formula
    prefix = args.prefix
    for i, tc in enumerate(test_cases, start=1):
        tc['testcaseId'] = f'{prefix}_{i}'

        lv1 = (tc.get('testcaseLV1') or '').strip()
        lv2 = (tc.get('testcaseLV2') or '').strip()
        lv3 = (tc.get('testcaseLV3') or '').strip()
        tc['summary'] = lv3 if lv3 else lv2

        # Compute testCaseName based on template structure:
        #   LV columns present  → "{testcaseId}_{LV1}_{LV2}_{LV3}"
        #   No LV columns       → just summary (clean test case name)
        if use_lv_formula:
            parts = [tc['testcaseId'], lv1, lv2]
            if lv3:
                parts.append(lv3)
            tc['testCaseName'] = '_'.join(parts)
        else:
            tc['testCaseName'] = tc['summary']

    # Step 4: Write back
    with open(args.file, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)

    print(f'✓ Assigned IDs {prefix}_1..{prefix}_{len(test_cases)} and recomputed summary for {len(test_cases)} test cases')
    if reordered:
        print(f'  Regrouped by testSuiteName ({len(regrouped_suites)} groups)')
    print(f'  → {args.file}')


if __name__ == '__main__':
    main()
