#!/usr/bin/env python3
"""
merge_batches.py — Merge test case batch JSON files into a single array.

Usage:
  python merge_batches.py --output-dir DIR --output-file FILE [--dry-run]

Batch file order:
  1. batch-1.json          (common + permission cases)
  2. validate-batch-1.json, validate-batch-2.json, ... (validate cases, in order)
  3. batch-3.json          (main flow cases)

What it does:
  1. Finds batch files in the order above
  2. Validates each is a JSON array — exits 1 with clear error if not
  3. Merges all into one array
  4. Deduplicates by testCaseName (case-insensitive, keep first occurrence)
  5. Reports per-batch counts and dedup count
  6. --dry-run: validate + report without writing

Exit codes:
  0 — success
  1 — error (file not a JSON array, no batches found, write error)
"""

import os
import sys
import json
import glob
import argparse
import io

# Force UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def load_batch(path: str) -> list:
    """Load a JSON file and validate it is a JSON array. Returns list or exits 1."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: {path} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: cannot read {path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print(
            f"ERROR: {path} must be a JSON array (got {type(data).__name__})",
            file=sys.stderr,
        )
        sys.exit(1)

    return data


def collect_batch_files(output_dir: str) -> list:
    """Return batch file paths in correct merge order."""
    files = []

    # 1. batch-1.json (common + permission)
    p = os.path.join(output_dir, "batch-1.json")
    if os.path.exists(p):
        files.append(p)

    # 2. validate-batch-N.json in numeric order
    validate_pattern = os.path.join(output_dir, "validate-batch-*.json")
    validate_files = sorted(
        glob.glob(validate_pattern),
        key=lambda x: int(
            os.path.basename(x).replace("validate-batch-", "").replace(".json", "")
        ),
    )
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
