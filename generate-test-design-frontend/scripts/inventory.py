#!/usr/bin/env python3
"""
Inventory manager for test generation workflow.
Incrementally builds and queries inventory.json.

Commands:
  init     Create or reset inventory file
  add      Append one item to a category
  patch    Merge a JSON file {category: [items]} into inventory (avoids shell encoding issues)
  get      Query items from a category (optionally filtered)
  summary  Print item counts per category

Usage:
  python inventory.py init    --file PATH --name NAME [--screen-type TYPE]
  python inventory.py add     --file PATH --category CATEGORY --data JSON
  python inventory.py add     --file PATH --category CATEGORY --data-file ITEM.json
  python inventory.py patch   --file PATH --patch-file PATCH.json
  python inventory.py get     --file PATH --category CATEGORY [--filter KEY=VALUE]
  python inventory.py summary --file PATH

Windows encoding note:
  On Windows, passing Vietnamese JSON via --data may fail due to shell encoding.
  Use --data-file or --patch-file instead:
    python inventory.py add --file inv.json --category fieldConstraints --data-file item.json
    python inventory.py patch --file inv.json --patch-file all_items.json

patch-file format (add multiple categories at once):
  {
    "fieldConstraints": [{"name":"tenField","type":"textbox","required":true}],
    "businessRules": [{"id":"BR1","condition":"...","trueBranch":"...","falseBranch":"..."}],
    "errorMessages": [{"code":"E001","text":"Lỗi...","field":"tenField"}]
  }

Categories (Frontend): fieldConstraints, businessRules, errorMessages, enableDisableRules,
                       autoFillRules, statusTransitions, permissions
Categories (API):      errorCodes, businessRules, modes, dbOperations, externalServices,
                       statusTransitions, decisionCombinations, fieldConstraints

Examples:
  python inventory.py init --file feat/inventory.json --name "Màn hình Dịch vụ" --screen-type "LIST"
  python inventory.py patch --file feat/inventory.json --patch-file patch.json
  python inventory.py get  --file feat/inventory.json --category fieldConstraints
  python inventory.py summary --file feat/inventory.json
"""

import json
import sys
import io
import os
import argparse

# Force UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def load(path):
    if not os.path.exists(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cmd_init(args):
    data = {
        "_meta": {
            "name": args.name or "",
            "endpoint": args.endpoint or "",
            "screenType": args.screen_type or "",
        },
        "errorCodes": [],
        "businessRules": [],
        "modes": [],
        "dbOperations": [],
        "externalServices": [],
        "statusTransitions": [],
        "decisionCombinations": [],
        "fieldConstraints": [],
        "errorMessages": [],
        "enableDisableRules": [],
        "autoFillRules": [],
        "permissions": [],
    }
    save(args.file, data)
    print(f"✓ Initialized: {args.file}")


def cmd_add(args):
    data = load(args.file)
    # Support --data-file to avoid Windows shell encoding issues
    if args.data_file:
        try:
            with open(args.data_file, encoding="utf-8") as f:
                item = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error: cannot read --data-file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.data:
        try:
            item = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON in --data: {e}", file=sys.stderr)
            print("Tip: on Windows use --data-file instead to avoid encoding issues", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: must provide --data or --data-file", file=sys.stderr)
        sys.exit(1)
    cat = args.category
    if cat not in data:
        data[cat] = []
    data[cat].append(item)
    save(args.file, data)
    print(f"✓ Added to {cat} ({len(data[cat])} total)")


def cmd_patch(args):
    """Merge patch-file {category: [items]} into inventory. Best for Windows."""
    data = load(args.file)
    try:
        with open(args.patch_file, encoding="utf-8") as f:
            patch = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error: cannot read --patch-file: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(patch, dict):
        print("Error: patch-file must be a JSON object {category: [items]}", file=sys.stderr)
        sys.exit(1)
    counts = {}
    for cat, items in patch.items():
        if not isinstance(items, list):
            print(f"Warning: skipping {cat} — value must be a list", file=sys.stderr)
            continue
        if cat not in data:
            data[cat] = []
        data[cat].extend(items)
        counts[cat] = len(items)
    save(args.file, data)
    for cat, n in counts.items():
        print(f"✓ Patched {cat}: +{n} items ({len(data[cat])} total)")


def cmd_get(args):
    data = load(args.file)
    cat = args.category
    items = data.get(cat, [])
    if args.filter:
        key, val = args.filter.split("=", 1)
        items = [i for i in items if str(i.get(key, "")) == val]
    print(json.dumps(items, ensure_ascii=False, indent=2))


def cmd_summary(args):
    data = load(args.file)
    meta = data.get("_meta", {})
    print(f"📋 Inventory: {args.file}")
    if meta.get("name"):
        print(f"   Name:     {meta['name']}")
    if meta.get("endpoint"):
        print(f"   Endpoint: {meta['endpoint']}")
    if meta.get("screenType"):
        print(f"   Screen:   {meta['screenType']}")
    print()
    categories = [
        "errorCodes", "businessRules", "modes", "dbOperations",
        "externalServices", "statusTransitions", "decisionCombinations",
        "fieldConstraints", "errorMessages", "enableDisableRules",
        "autoFillRules", "permissions",
    ]
    for cat in categories:
        items = data.get(cat, [])
        if items:
            labels = []
            for i in items:
                label = i.get("code") or i.get("id") or i.get("name") or i.get("table") or i.get("field") or i.get("target") or ""
                if label:
                    labels.append(label)
            suffix = f" ({', '.join(labels)})" if labels else ""
            print(f"  {cat}: {len(items)}{suffix}")


def main():
    parser = argparse.ArgumentParser(description="Inventory manager for test generation")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init")
    p_init.add_argument("--file", required=True)
    p_init.add_argument("--name", default="")
    p_init.add_argument("--endpoint", default="")
    p_init.add_argument("--screen-type", default="", dest="screen_type")

    p_add = sub.add_parser("add")
    p_add.add_argument("--file", required=True)
    p_add.add_argument("--category", required=True)
    p_add.add_argument("--data", default="", help="JSON string of item to append")
    p_add.add_argument("--data-file", default="", dest="data_file",
                       help="Path to JSON file containing item (avoids Windows shell encoding issues)")

    p_patch = sub.add_parser("patch")
    p_patch.add_argument("--file", required=True)
    p_patch.add_argument("--patch-file", required=True, dest="patch_file",
                         help="JSON file {category: [items]} to merge into inventory")

    p_get = sub.add_parser("get")
    p_get.add_argument("--file", required=True)
    p_get.add_argument("--category", required=True)
    p_get.add_argument("--filter", default="", help="KEY=VALUE to filter results")

    p_sum = sub.add_parser("summary")
    p_sum.add_argument("--file", required=True)

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "patch":
        cmd_patch(args)
    elif args.command == "get":
        cmd_get(args)
    elif args.command == "summary":
        cmd_summary(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
