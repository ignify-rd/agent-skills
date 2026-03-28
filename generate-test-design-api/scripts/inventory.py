#!/usr/bin/env python3
"""
Inventory manager for test generation workflow.
Incrementally builds and queries inventory.json.

Commands:
  init     Create or reset inventory file
  add      Append one item to a category
  patch    Merge a JSON file into inventory (avoids shell encoding issues)
  get      Query items from a category (optionally filtered)
  summary  Print item counts per category

Usage:
  python inventory.py init    --file PATH --name NAME [--endpoint ENDPOINT] [--method METHOD] [--screen-type TYPE]
  python inventory.py add     --file PATH --category CATEGORY --data JSON
  python inventory.py add     --file PATH --category CATEGORY --data-file ITEM.json
  python inventory.py patch   --file PATH --patch-file PATCH.json
  python inventory.py get     --file PATH --category CATEGORY [--filter KEY=VALUE]
  python inventory.py summary --file PATH

Windows encoding note:
  On Windows, passing Vietnamese JSON via --data may fail due to shell encoding.
  Use --data-file or --patch-file instead:
    python inventory.py add --file inv.json --category errorCodes --data-file item.json
    python inventory.py patch --file inv.json --patch-file all_items.json

patch-file format — supports both arrays (extend) and objects (deep-merge):
  {
    "errorCodes": [{"code":"LDH_SLA_001","desc":"...","section":"validate"}],
    "fieldConstraints": [{"name":"slaVersionId","type":"Long","required":true}],
    "requestSchema": {
      "pathParams": [{"name":"slaVersionId","type":"Long","required":true}],
      "queryParams": [{"name":"action","type":"String","required":true,"values":["SAVE","PUSH"]}],
      "bodyParams": [{"name":"slaName","type":"String","required":true,"maxLength":100}]
    },
    "responseSchema": {
      "success": {
        "status": 200,
        "body": {"slaVersionId":"Long","slaName":"String","status":"String"},
        "sample": {"slaVersionId":10001,"slaName":"SLA Test","status":"DRAFT"}
      },
      "error": {
        "status": 200,
        "body": {"code":"String","message":"String"}
      }
    },
    "testData": [
      {"field":"slaName","type":"String","validValue":"SLA Test 001","note":"tên SLA hợp lệ"}
    ]
  }

Categories (API):      errorCodes, businessRules, modes, dbOperations, externalServices,
                       statusTransitions, decisionCombinations, fieldConstraints,
                       testData  (arrays — extend on patch)
Schema objects (API):  requestSchema, responseSchema  (dicts — deep-merge on patch)

Categories (Frontend): fieldConstraints, businessRules, errorMessages, enableDisableRules,
                       autoFillRules, statusTransitions, permissions, testData

Examples:
  python inventory.py init --file feat/inventory.json --name "Chỉnh sửa SLA" --endpoint "POST /sla-service/v1/slas/update" --method POST
  python inventory.py patch --file feat/inventory.json --patch-file patch.json
  python inventory.py get   --file feat/inventory.json --category requestSchema
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


def _deep_merge(base, patch):
    """Recursively merge patch dict into base dict."""
    for k, v in patch.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def cmd_init(args):
    data = {
        "_meta": {
            "name": args.name or "",
            "endpoint": args.endpoint or "",
            "method": args.method or "",
            "screenType": args.screen_type or "",
        },
        # ── Request / Response schema (dùng cho test case generation) ──
        "requestSchema": {
            "pathParams": [],   # [{"name":"id","type":"Long","required":true}]
            "queryParams": [],  # [{"name":"action","type":"String","required":true,"values":["SAVE","PUSH"]}]
            "bodyParams": []    # [{"name":"slaName","type":"String","required":true,"maxLength":100}]
        },
        "responseSchema": {
            "success": {},  # {"status":200,"body":{...},"sample":{...}}
            "error": {}     # {"status":200,"body":{"code":"String","message":"String"}}
        },
        # ── Sample data for test cases ──
        "testData": [],  # [{"field":"slaName","type":"String","validValue":"SLA Test","note":"..."}]
        # ── Business logic ──
        "errorCodes": [],
        "businessRules": [],
        "modes": [],
        "dbOperations": [],
        "externalServices": [],
        "statusTransitions": [],
        "decisionCombinations": [],
        "fieldConstraints": [],
        # ── Frontend categories (shared schema) ──
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
    existing = data.get(cat)
    if isinstance(existing, list):
        existing.append(item)
        data[cat] = existing
        print(f"✓ Added to {cat} ({len(data[cat])} total)")
    elif isinstance(existing, dict):
        _deep_merge(existing, item)
        data[cat] = existing
        print(f"✓ Merged into {cat}")
    else:
        data[cat] = [item]
        print(f"✓ Added to {cat} (1 total)")
    save(args.file, data)


def cmd_patch(args):
    """Merge patch-file into inventory.
    - List values → extend existing list
    - Dict values → deep-merge into existing dict
    """
    data = load(args.file)
    try:
        with open(args.patch_file, encoding="utf-8") as f:
            patch = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error: cannot read --patch-file: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(patch, dict):
        print("Error: patch-file must be a JSON object", file=sys.stderr)
        sys.exit(1)
    for cat, value in patch.items():
        if isinstance(value, list):
            if cat not in data or not isinstance(data.get(cat), list):
                data[cat] = []
            data[cat].extend(value)
            print(f"✓ Patched {cat}: +{len(value)} items ({len(data[cat])} total)")
        elif isinstance(value, dict):
            if cat not in data or not isinstance(data.get(cat), dict):
                data[cat] = {}
            _deep_merge(data[cat], value)
            print(f"✓ Patched {cat}: merged {len(value)} keys")
        else:
            print(f"Warning: skipping {cat} — value must be list or dict", file=sys.stderr)
    save(args.file, data)


def cmd_get(args):
    data = load(args.file)
    cat = args.category
    value = data.get(cat)
    if value is None:
        print("[]")
        return
    if args.filter and isinstance(value, list):
        key, val = args.filter.split("=", 1)
        value = [i for i in value if str(i.get(key, "")) == val]
    print(json.dumps(value, ensure_ascii=False, indent=2))


def cmd_summary(args):
    data = load(args.file)
    meta = data.get("_meta", {})
    print(f"📋 Inventory: {args.file}")
    if meta.get("name"):
        print(f"   Name:     {meta['name']}")
    if meta.get("method") and meta.get("endpoint"):
        print(f"   Endpoint: {meta['method']} {meta['endpoint']}")
    elif meta.get("endpoint"):
        print(f"   Endpoint: {meta['endpoint']}")
    if meta.get("screenType"):
        print(f"   Screen:   {meta['screenType']}")
    print()

    # Request schema
    req = data.get("requestSchema", {})
    path_p = req.get("pathParams", [])
    query_p = req.get("queryParams", [])
    body_p = req.get("bodyParams", [])
    if path_p or query_p or body_p:
        path_names = [p.get("name", "") for p in path_p]
        query_names = [p.get("name", "") for p in query_p]
        body_names = [p.get("name", "") for p in body_p]
        print(f"  requestSchema:")
        if path_p:
            print(f"    pathParams  ({len(path_p)}): {', '.join(path_names)}")
        if query_p:
            print(f"    queryParams ({len(query_p)}): {', '.join(query_names)}")
        if body_p:
            print(f"    bodyParams  ({len(body_p)}): {', '.join(body_names)}")

    # Response schema
    resp = data.get("responseSchema", {})
    success = resp.get("success", {})
    if success:
        body_keys = list(success.get("body", {}).keys())
        print(f"  responseSchema.success: {{{', '.join(body_keys)}}}")

    # testData
    test_data = data.get("testData", [])
    if test_data:
        td_names = [t.get("field", "") for t in test_data]
        print(f"  testData ({len(test_data)}): {', '.join(td_names)}")

    print()

    # Array categories
    array_categories = [
        "errorCodes", "businessRules", "modes", "dbOperations",
        "externalServices", "statusTransitions", "decisionCombinations",
        "fieldConstraints", "errorMessages", "enableDisableRules",
        "autoFillRules", "permissions",
    ]
    for cat in array_categories:
        items = data.get(cat, [])
        if items:
            labels = []
            for i in items:
                label = (i.get("code") or i.get("id") or i.get("name") or
                         i.get("table") or i.get("field") or i.get("target") or "")
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
    p_init.add_argument("--method", default="", help="HTTP method: GET, POST, PUT, DELETE, PATCH")
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
                         help="JSON file to merge into inventory (lists extend, dicts deep-merge)")

    p_get = sub.add_parser("get")
    p_get.add_argument("--file", required=True)
    p_get.add_argument("--category", required=True)
    p_get.add_argument("--filter", default="", help="KEY=VALUE to filter results (lists only)")

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
