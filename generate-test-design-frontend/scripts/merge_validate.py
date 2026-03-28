#!/usr/bin/env python3
"""
merge_validate.py — Merge and sanitize validate batch files into the output file.

Usage:
  python merge_validate.py --output-dir DIR --output-file FILE [--dry-run]

What it does:
  1. Finds validate-batch-1.md, validate-batch-2.md, ... in order
  2. Sanitizes each: strips H1/H2 headers, === === lines, and horizontal rules
     that agents accidentally write into batch files
  3. Validates each: after sanitization the first line must start with ###
     (H3 field heading). Exits 1 if any batch is empty after sanitization.
  4. Merges all batches under ## Kiểm tra Validate, appends to OUTPUT_FILE
  5. Writes .validate-done sentinel to OUTPUT_DIR

Exit codes:
  0 — success
  1 — error (no batches found, empty batch after sanitize, output file missing)
"""

import os
import re
import sys
import io
import argparse

# Force UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Patterns that agents write into batch files but should NOT be there
_GARBAGE = [
    re.compile(r"^# .+"),           # # BATCH N: Validate — fieldName
    re.compile(r"^## .+"),          # ## Kiểm tra Validate / ## Per-Field Checkpoint / ## Response Legend
    re.compile(r"^==="),             # === Batch N complete === or standalone ===
    re.compile(r"^---\s*$"),        # horizontal rule
    re.compile(r"^\|"),             # markdown table rows (checkpoint tables, legend tables)
]


def sanitize(content: str) -> str:
    """Strip garbage lines from batch file content."""
    lines = content.split("\n")
    cleaned = []
    removed = []
    for i, line in enumerate(lines, 1):
        if any(p.match(line) for p in _GARBAGE):
            removed.append((i, line))
        else:
            cleaned.append(line)
    # Strip leading/trailing blank lines
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()
    return "\n".join(cleaned), removed


def validate_first_line(content: str, batch_num: int, path: str) -> bool:
    """After sanitization, first line must be an H3 heading (### )."""
    first = content.split("\n")[0] if content else ""
    if not first.startswith("### "):
        print(
            f"  WARNING batch-{batch_num}: first line after sanitize is not H3 heading",
            file=sys.stderr,
        )
        print(f"    Got:      {repr(first[:100])}", file=sys.stderr)
        print(f"    Expected: starts with '### '", file=sys.stderr)
        print(f"    File: {path}", file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Merge validate batch files into output"
    )
    parser.add_argument("--output-dir", required=True, dest="output_dir")
    parser.add_argument("--output-file", required=True, dest="output_file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Validate and print what would be merged, without writing anything",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"ERROR: output-dir does not exist: {args.output_dir}", file=sys.stderr)
        sys.exit(1)

    if not args.dry_run and not os.path.exists(args.output_file):
        print(
            f"ERROR: output-file does not exist: {args.output_file}", file=sys.stderr
        )
        print(
            "  td-common must run first to create the output file.", file=sys.stderr
        )
        sys.exit(1)

    # ── Step 1: Collect and sanitize batch files ──────────────────────────────
    batch_parts = []
    n = 1
    while True:
        path = os.path.join(args.output_dir, f"validate-batch-{n}.md")
        if not os.path.exists(path):
            break

        print(f"Processing batch-{n}: {path}")
        with open(path, encoding="utf-8") as f:
            raw = f.read()

        sanitized, removed = sanitize(raw)

        if removed:
            print(f"  Stripped {len(removed)} garbage line(s):")
            for lineno, text in removed:
                print(f"    line {lineno}: {repr(text[:80])}")

        if not sanitized.strip():
            print(
                f"ERROR: validate-batch-{n}.md is empty after sanitization.",
                file=sys.stderr,
            )
            print(f"  Raw content ({len(raw)} chars):", file=sys.stderr)
            print(f"  {repr(raw[:300])}", file=sys.stderr)
            sys.exit(1)

        validate_first_line(sanitized, n, path)

        batch_parts.append(sanitized)
        n += 1

    # ── Step 2: Check we found at least one batch ──────────────────────────────
    if not batch_parts:
        print(
            f"ERROR: no validate-batch-*.md files found in: {args.output_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\nFound {len(batch_parts)} batch(es) — total fields to merge")

    # ── Step 3: Dry-run report ─────────────────────────────────────────────────
    if args.dry_run:
        print("\nDRY RUN — would write to output file:")
        print(f"  ## Kiểm tra Validate")
        for i, part in enumerate(batch_parts, 1):
            lines = part.split("\n")
            print(f"  batch-{i}: {len(lines)} lines, first: {repr(lines[0][:70])}")
        return

    # ── Step 4: Append to output file ─────────────────────────────────────────
    with open(args.output_file, "a", encoding="utf-8") as f:
        f.write("\n\n## Kiểm tra Validate\n\n")
        f.write("\n\n".join(batch_parts))

    # ── Step 5: Write sentinel ─────────────────────────────────────────────────
    sentinel = os.path.join(args.output_dir, ".validate-done")
    with open(sentinel, "w", encoding="utf-8") as f:
        f.write(f"merged {len(batch_parts)} batches")

    print(f"\n✓ Merged {len(batch_parts)} batch(es) → {args.output_file}")
    print(f"✓ Sentinel written: {sentinel}")


if __name__ == "__main__":
    main()
