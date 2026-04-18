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


def _apply_nested(result: dict, dotted_key: str, value) -> None:
    """Set or remove a value at a dot-notation path inside result.

    Example: _apply_nested(result, "page.pageSize", 10)
      navigates to result["page"] (creating it if absent) and sets ["pageSize"] = 10.
    If value is _REMOVE_SENTINEL, removes the leaf key instead.

    Note: only simple dot-notation paths are supported (e.g. "page.pageSize").
    Array notation keys such as "orders[].field" or "orders[0].field" are NOT
    supported -- keys containing "[" will be set as literal dict keys.
    """
    parts = dotted_key.split(".")
    obj = result
    for part in parts[:-1]:
        if part not in obj or not isinstance(obj[part], dict):
            obj[part] = {}
        obj = obj[part]
    leaf = parts[-1]
    if value == _REMOVE_SENTINEL:
        obj.pop(leaf, None)
    else:
        obj[leaf] = value


def _apply_override(base_params: dict, param_override: dict) -> dict:
    """Apply paramOverride to a copy of baseParams. Returns modified body dict.

    Rules:
      - "__REMOVE__" → delete key from body
      - null/other   → set key to that value
      - "fileContent" key is skipped (handled separately for file-upload APIs)
      - dot-notation keys (e.g. "page.pageSize") are resolved into nested dicts
    """
    result = copy.deepcopy(base_params)
    for key, value in param_override.items():
        if key == "fileContent":
            continue
        if "." in key:
            _apply_nested(result, key, value)
        elif value == _REMOVE_SENTINEL:
            result.pop(key, None)
        else:
            result[key] = value
    return result


def _format_body_json(body: dict, indent: int = 4) -> str:
    """Format body dict as indented JSON string for step display."""
    return json.dumps(body, ensure_ascii=False, indent=indent)


def _extract_primary_field_value(param_override: dict) -> tuple:
    """Extract the primary (first non-fileContent) field name and its display value from paramOverride."""
    for key, value in param_override.items():
        if key == "fileContent":
            continue
        if value == _REMOVE_SENTINEL:
            return key, "(bỏ qua / không truyền)"
        if value is None:
            return key, "null"
        if value == "":
            return key, '""'
        if isinstance(value, bool):
            return key, "true" if value else "false"
        if isinstance(value, (int, float)):
            return key, str(value)
        if isinstance(value, str):
            return key, f'"{value}"' if len(value) <= 40 else f'"{value[:40]}..."'
        return key, json.dumps(value, ensure_ascii=False)
    return "", ""


def _has_step_placeholders(template: str) -> bool:
    """Return True if template has any recognized placeholder."""
    return any(p in template for p in (
        "{FIELD_ACTION}", "{BODY_JSON}", "{METHOD}",
        "{fieldName}", "{value}", "{field_name}", "{field}", "{val}"
    ))


def _format_field_change(field: str, value) -> str:
    """Format a single field change description (Vietnamese)."""
    if value == _REMOVE_SENTINEL:
        return f"Bỏ trường {field} khỏi request body"
    if value is None:
        return f"Truyền {field} = null"
    if value == "":
        return f'Truyền {field} = ""'
    if isinstance(value, bool):
        return f"Truyền {field} = {'true' if value else 'false'}"
    if isinstance(value, (int, float)):
        return f"Truyền {field} = {value}"
    if isinstance(value, str):
        display = value if len(value) <= 40 else value[:40] + "..."
        return f'Truyền {field} = "{display}"'
    return f"Truyền {field} = {json.dumps(value, ensure_ascii=False)}"


def _build_field_change_step(param_override: dict, step_num: int = 2) -> str:
    """Build step N describing the specific field change for a validate test case."""
    if not param_override or not isinstance(param_override, dict):
        return f"{step_num}. Send API"
    parts = []
    for field, value in param_override.items():
        if field == "fileContent" and isinstance(value, dict):
            for fc_field, fc_value in value.items():
                parts.append(_format_field_change(fc_field, fc_value))
        else:
            parts.append(_format_field_change(field, value))
    if parts:
        return f"{step_num}. " + "\n   ".join(parts)
    return f"{step_num}. Send API"


def _expand_template_batch(data: dict, path: str, file_content_base: dict) -> list:
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
    step_template = tpl.get("stepTemplate", "")
    api_endpoint = tpl.get("apiEndpoint", "")
    base_params = tpl.get("baseParams", {})
    importance = tpl.get("importance", "Medium")
    result = tpl.get("result", "PENDING")

    # Extract method from apiEndpoint (e.g. "POST /sla-service/v1/slas/update" → "POST")
    api_method = api_endpoint.split()[0] if api_endpoint else ""

    expanded = []
    for tc in cases:
        tc_name = tc.get("testCaseName", "")

        # Build field action description for the step
        field_action = ""
        if "paramOverride" in tc:
            po = tc["paramOverride"]
            field_action = _build_field_change_step(po, step_num=2)
            # Strip the step number prefix — template will add its own numbering
            field_action_text = field_action.lstrip("0123456789. ")

            # Fallback: if field_action says "Bỏ trường X" but testCaseName implies a different
            # action, derive from testCaseName instead
            _remove_patterns = ("không truyền", "bo truong", "bỏ trường", "not provided")
            if "Bỏ trường" in field_action and not any(p in tc_name.lower() for p in _remove_patterns):
                desc = tc_name
                for pfx in ("Kiểm tra ", "kiểm tra "):
                    if desc.startswith(pfx):
                        desc = desc[len(pfx):]
                        break
                field_action_text = desc[0].upper() + desc[1:] if desc else desc

        # Build modified body JSON
        body_json = ""
        if base_params and "paramOverride" in tc:
            modified_body = _apply_override(base_params, tc["paramOverride"])
            body_json = _format_body_json(modified_body)

        # ── Use stepTemplate if available (catalog format) ──
        if step_template and _has_step_placeholders(step_template):
            steps = step_template

            # {FIELD_ACTION} — full action sentence (e.g. "Bỏ trường X khỏi request body")
            if "{FIELD_ACTION}" in steps:
                if "rawBody" in tc:
                    steps = steps.replace("{FIELD_ACTION}", f"Gửi body: {tc['rawBody']}")
                elif "paramOverride" in tc:
                    steps = steps.replace("{FIELD_ACTION}", field_action_text)
                else:
                    steps = steps.replace("{FIELD_ACTION}", "Send API")

            # {fieldName} / {field_name} / {field} — just the field name
            primary_field, primary_value_str = "", ""
            if "paramOverride" in tc:
                primary_field, primary_value_str = _extract_primary_field_value(tc["paramOverride"])
            for ph in ("{fieldName}", "{field_name}", "{field}"):
                if ph in steps:
                    steps = steps.replace(ph, primary_field)

            # {value} / {val} — the test value
            for ph in ("{value}", "{val}"):
                if ph in steps:
                    steps = steps.replace(ph, primary_value_str)

            # {BODY_JSON} — full modified body JSON
            if "{BODY_JSON}" in steps:
                if body_json:
                    steps = steps.replace("{BODY_JSON}", body_json)
                elif base_params:
                    steps = steps.replace("{BODY_JSON}", _format_body_json(base_params))
                else:
                    steps = steps.replace("{BODY_JSON}", "{}")
            elif body_json and base_params:
                # Template has no {BODY_JSON} but we have a full body — append for copy-paste
                # This handles catalog-style templates that use {fieldName}/{value} without {BODY_JSON}
                steps += f"\n   Param:\n{body_json}"

            # {METHOD} — HTTP method
            if "{METHOD}" in steps:
                steps = steps.replace("{METHOD}", api_method)

        # ── Fallback: stepPrefix-based format ──
        elif "rawBody" in tc:
            raw = tc["rawBody"]
            steps = f"{step_prefix}\n2. Gửi body: {raw}\n3. Send API"
        elif "paramOverride" in tc:
            steps = f"{step_prefix}\n{field_action}\n3. Send API"
            # Append modified body so testers can copy-paste into Postman
            if body_json:
                steps += f"\n   Param:\n{body_json}"
        else:
            steps = f"{step_prefix}\n2. Send API"

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


def load_batch(path: str, file_content_base: dict = None) -> list:
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
        return _expand_template_batch(data, path, file_content_base or {})

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

    # 2. validate-batch.json (single file from scripts) OR validate-batch-*.json (legacy numbered)
    single = os.path.join(output_dir, "validate-batch.json")
    if os.path.exists(single):
        files.append(single)
    else:
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
    parser.add_argument("--context", default=None, dest="context_file",
                        help="tc-context.json — loads fileContentFieldsBase for fileContent field handling")
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

    # Load fileContentFieldsBase from tc-context.json (for fileContent field handling)
    file_content_base = {}
    if args.context_file and os.path.exists(args.context_file):
        try:
            with open(args.context_file, encoding="utf-8") as f:
                ctx = json.load(f)
                file_content_base = ctx.get("fileContentFieldsBase", {})
        except (json.JSONDecodeError, OSError) as e:
            print(f"  WARNING: could not read context file {args.context_file}: {e}", file=sys.stderr)

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
        items = load_batch(path, file_content_base)
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
