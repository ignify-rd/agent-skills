#!/usr/bin/env python3
"""
merge_batches.py — Merge test case batch JSON files into a single array.

Usage:
  python merge_batches.py --output-dir DIR --output-file FILE [--dry-run]

Batch file order:
  1. batch-1.json          (common + permission cases)
  2. validate-batch-1.json, validate-batch-2.json, ... (validate cases, in order)
  3. batch-3.json          (main flow cases)

Supported batch formats:
  A. Flat format — JSON array of test case objects (batch-1, batch-3, legacy validate)
  B. Template format — object with _template + testCases array (optimized validate batches)
     The _template contains shared fields (preConditions, stepPrefix, baseParams, importance, result).
     Each testCase only stores the diff (testCaseName, testSuiteName, paramOverride, expectedResult).
     This script expands templates into full test case objects before merging.

What it does:
  1. Finds batch files in the order above
  2. Detects format (flat array vs template object) and loads accordingly
  3. Expands template-format batches into flat test case arrays
  4. Merges all into one array
  5. Deduplicates by testCaseName (case-insensitive, keep first occurrence)
  6. Reports per-batch counts and dedup count
  7. --dry-run: validate + report without writing

Exit codes:
  0 — success
  1 — error (file not valid, no batches found, write error)
"""

import os
import sys
import json
import glob
import copy
import argparse
import io

# Force UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


_REMOVE_SENTINEL = "__REMOVE__"


def _expand_template_batch(data: dict, path: str) -> list:
    """
    Expand a template-format batch into a flat list of test case objects.

    Template format:
    {
      "_template": {
        "preConditions": "...",
        "stepPrefix": "1. Nhập các tham số\n1.1. Authorization: ...\n1.2. Method: POST\n1.3. Param:\n",
        "baseParams": { "field1": "val1", ... },
        "importance": "Medium",
        "result": "PENDING"
      },
      "testCases": [
        {
          "testCaseName": "field_case_desc",
          "testSuiteName": "Type: field",
          "paramOverride": { "field1": newValue },   // or "__REMOVE__" to omit key
          "expectedResult": "..."
        }, ...
      ]
    }

    For cases that send a non-object body (e.g. raw string), use "rawBody" instead of "paramOverride".
    """
    tpl = data.get("_template", {})
    cases = data.get("testCases", [])

    if not cases:
        print(f"  WARNING: {path} template has 0 testCases", file=sys.stderr)
        return []

    pre_conditions = tpl.get("preConditions", "")
    step_prefix = tpl.get("stepPrefix", "")
    base_params = tpl.get("baseParams", {})
    importance = tpl.get("importance", "Medium")
    result = tpl.get("result", "PENDING")

    expanded = []
    for tc in cases:
        tc_name = tc.get("testCaseName", "")

        # Build testSteps
        if "rawBody" in tc:
            # Non-object body (string, number, etc.)
            steps = step_prefix + str(tc["rawBody"])
        elif "paramOverride" in tc:
            params = copy.deepcopy(base_params)
            for k, v in tc["paramOverride"].items():
                if v == _REMOVE_SENTINEL:
                    params.pop(k, None)
                else:
                    params[k] = v
            steps = step_prefix + json.dumps(params, ensure_ascii=False, indent=2)
        else:
            # No override — use baseParams as-is
            steps = step_prefix + json.dumps(base_params, ensure_ascii=False, indent=2)

        expanded.append({
            "testCaseName": tc_name,
            "testSuiteName": tc.get("testSuiteName", ""),
            "preConditions": pre_conditions,
            "step": steps,
            "expectedResult": tc.get("expectedResult", ""),
            "importance": tc.get("importance", importance),
            "result": result,
            "summary": tc_name,
        })

    return expanded


def load_batch(path: str) -> list:
    """
    Load a JSON batch file. Supports two formats:
      A. Flat: JSON array of test case objects
      B. Template: JSON object with _template + testCases (auto-expanded)
    Returns flat list of test case objects, or exits 1 on error.
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: {path} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: cannot read {path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Template format: { "_template": {...}, "testCases": [...] }
    if isinstance(data, dict) and "_template" in data:
        print(f"  [template format] expanding {len(data.get('testCases', []))} cases...")
        return _expand_template_batch(data, path)

    # Flat format: [...]
    if isinstance(data, list):
        return data

    print(
        f"ERROR: {path} must be a JSON array or template object (got {type(data).__name__})",
        file=sys.stderr,
    )
    sys.exit(1)


def _validate_batch_sort_key(path: str):
    """Sort key for validate-batch files.

    Supports patterns:
      validate-batch-1.json       -> (0, "", 1)
      validate-batch-10.json      -> (0, "", 10)
      validate-batch-fc-1.json    -> (1, "fc", 1)
      validate-batch-fc-10.json   -> (1, "fc", 10)

    Order: numeric batches first, then named batches grouped by prefix alphabetically,
    then by number within each prefix group.
    """
    name = os.path.basename(path).replace("validate-batch-", "").replace(".json", "")
    try:
        return (0, "", int(name))
    except ValueError:
        pass
    parts = name.rsplit("-", 1)
    if len(parts) == 2:
        prefix, num_str = parts
        try:
            return (1, prefix, int(num_str))
        except ValueError:
            pass
    return (2, name, 0)


def collect_batch_files(output_dir: str) -> list:
    """Return batch file paths in correct merge order."""
    files = []

    # 1. batch-1.json (common + permission)
    p = os.path.join(output_dir, "batch-1.json")
    if os.path.exists(p):
        files.append(p)

    # 2. validate-batch-*.json — supports numeric and named patterns (e.g. fc-1)
    validate_pattern = os.path.join(output_dir, "validate-batch-*.json")
    validate_files = sorted(glob.glob(validate_pattern), key=_validate_batch_sort_key)
    files.extend(validate_files)

    # 3. batch-3.json (main flow)
    p = os.path.join(output_dir, "batch-3.json")
    if os.path.exists(p):
        files.append(p)

    return files


def deduplicate(items: list) -> tuple:
    """
    Deduplicate by testCaseName (case-insensitive), keeping first occurrence.
    Returns (deduplicated_list, removed_count).
    """
    seen = {}
    result = []
    removed = 0
    for item in items:
        name = item.get("testCaseName", "")
        key = name.lower()
        if key not in seen:
            seen[key] = True
            result.append(item)
        else:
            removed += 1
    return result, removed


def main():
    parser = argparse.ArgumentParser(
        description="Merge test case batch JSON files into a single array"
    )
    parser.add_argument("--output-dir", required=True, dest="output_dir")
    parser.add_argument("--output-file", required=True, dest="output_file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Validate and report without writing output",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"ERROR: output-dir does not exist: {args.output_dir}", file=sys.stderr)
        sys.exit(1)

    # ── Step 1: Collect batch files ───────────────────────────────────────────
    batch_files = collect_batch_files(args.output_dir)

    if not batch_files:
        print(
            f"ERROR: no batch files found in: {args.output_dir}", file=sys.stderr
        )
        print(
            "  Expected: batch-1.json, validate-batch-1.json, ..., batch-3.json",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Step 2: Load and validate each batch ─────────────────────────────────
    all_items = []
    batch_counts = []

    for path in batch_files:
        label = os.path.basename(path)
        items = load_batch(path)
        count = len(items)
        batch_counts.append((label, count))
        print(f"  {label}: {count} test case(s)")
        all_items.extend(items)

    total_before = len(all_items)
    print(f"\nTotal before dedup: {total_before}")

    # ── Step 3: Deduplicate ───────────────────────────────────────────────────
    merged, removed = deduplicate(all_items)
    total_after = len(merged)

    if removed > 0:
        print(f"Deduplicated: removed {removed} duplicate(s) (case-insensitive testCaseName)")
    else:
        print("Dedup: no duplicates found")

    print(f"Total after dedup: {total_after}")

    # ── Step 4: Per-batch report ──────────────────────────────────────────────
    print("\nPer-batch summary:")
    for label, count in batch_counts:
        print(f"  {label}: {count}")

    # ── Step 5: Dry-run ───────────────────────────────────────────────────────
    if args.dry_run:
        print(
            f"\nDRY RUN — would write {total_after} test cases to: {args.output_file}"
        )
        return

    # ── Step 6: Write output ──────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(args.output_file)), exist_ok=True)
    try:
        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"ERROR: cannot write output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n✓ Merged {total_after} test cases → {args.output_file}")


if __name__ == "__main__":
    main()
