#!/usr/bin/env python3
"""
Inventory manager for test generation workflow.
Incrementally builds and queries inventory.json.

Commands:
  init     Create or reset inventory file
  add      Append one item to a category
  get      Query items from a category (optionally filtered)
  summary  Print item counts per category

Usage:
  python inventory.py init    --file PATH --name NAME [--endpoint ENDPOINT] [--screen-type TYPE]
  python inventory.py add     --file PATH --category CATEGORY --data JSON
  python inventory.py get     --file PATH --category CATEGORY [--filter KEY=VALUE]
  python inventory.py summary --file PATH

Categories (API):      errorCodes, businessRules, modes, dbOperations, externalServices,
                       statusTransitions, decisionCombinations, fieldConstraints
Categories (Frontend): fieldConstraints, businessRules, errorMessages, enableDisableRules,
                       autoFillRules, statusTransitions, permissions

Examples:
  python inventory.py init --file feat/inventory.json --name "Upload File" --endpoint "POST /v1/upload"
  python inventory.py add  --file feat/inventory.json --category errorCodes \\
      --data '{"code":"E001","desc":"File quá lớn","section":"validate","trigger":"size>10MB","source":"RSD tr.5"}'
  python inventory.py get  --file feat/inventory.json --category errorCodes
  python inventory.py get  --file feat/inventory.json --category errorCodes --filter section=validate
  python inventory.py summary --file feat/inventory.json
"""

import json
import sys
import os
import argparse
import io

# ── UTF-8 guard for Windows ─────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


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
            "caseTitlePrefix": args.case_title_prefix or "",
        },
        "errorCodes": [],
        "businessRules": [],
        "modes": [],
        "dbOperations": [],
        "externalServices": [],
        "statusTransitions": [],
        "decisionCombinations": [],
        "fieldConstraints": [],
        "fileContentFields": [],
        "errorMessages": [],
        "enableDisableRules": [],
        "autoFillRules": [],
        "permissions": [],
    }
    save(args.file, data)
    print(f"✓ Initialized: {args.file}")


def cmd_add(args):
    data = load(args.file)
    try:
        item = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in --data: {e}", file=sys.stderr)
        sys.exit(1)
    cat = args.category
    if cat not in data:
        data[cat] = []
    data[cat].append(item)
    save(args.file, data)
    print(f"✓ Added to {cat} ({len(data[cat])} total)")


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
        "fieldConstraints", "fileContentFields", "errorMessages", "enableDisableRules",
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


def cmd_allfields(args):
    """Return unified list of fieldConstraints + fileContentFields for batch planning.

    Each item gets a 'source' field: 'request' or 'fileContent'.
    Output: JSON array of {name, type, required, source, ...} objects.
    """
    data = load(args.file)
    result = []

    for item in data.get("fieldConstraints", []):
        entry = {
            "name": item.get("name", ""),
            "type": item.get("type", ""),
            "required": item.get("required", False),
            "source": "request",
        }
        if "maxLength" in item:
            entry["maxLength"] = item["maxLength"]
        if "rsdConstraints" in item:
            entry["rsdConstraints"] = item["rsdConstraints"]
        result.append(entry)

    for item in data.get("fileContentFields", []):
        entry = {
            "name": item.get("name", "") or item.get("displayName", ""),
            "type": item.get("inputType", item.get("type", "")),
            "required": item.get("required", False),
            "source": "fileContent",
        }
        if "maxLength" in item:
            entry["maxLength"] = item["maxLength"]
        if "displayName" in item:
            entry["displayName"] = item["displayName"]
        result.append(entry)

    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Inventory manager for test generation")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init")
    p_init.add_argument("--file", required=True)
    p_init.add_argument("--name", default="")
    p_init.add_argument("--endpoint", default="")
    p_init.add_argument("--screen-type", default="", dest="screen_type")
    p_init.add_argument("--case-title-prefix", default="", dest="case_title_prefix",
                        help="Prefix for supplement case titles (e.g. 'Kiểm tra truyền file hợp lệ, nội dung file')")

    p_add = sub.add_parser("add")
    p_add.add_argument("--file", required=True)
    p_add.add_argument("--category", required=True)
    p_add.add_argument("--data", required=True, help="JSON string of item to append")

    p_get = sub.add_parser("get")
    p_get.add_argument("--file", required=True)
    p_get.add_argument("--category", required=True)
    p_get.add_argument("--filter", default="", help="KEY=VALUE to filter results")

    p_sum = sub.add_parser("summary")
    p_sum.add_argument("--file", required=True)

    p_all = sub.add_parser("allFields", help="Unified fieldConstraints + fileContentFields list")
    p_all.add_argument("--file", required=True)

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "get":
        cmd_get(args)
    elif args.command == "summary":
        cmd_summary(args)
    elif args.command == "allFields":
        cmd_allfields(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
