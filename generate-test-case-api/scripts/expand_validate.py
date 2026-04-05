#!/usr/bin/env python3
"""
expand_validate.py — Expand lightweight agent-case lists into template-format batch JSON.

Reads:
  validate-cases-{N}.json   — agent's lightweight output  (array of {field, case, value?})
  tc-context.json          — templates + catalogStyle
  inventory.json           — fieldConstraints + errorCodes

Writes:
  validate-batch-{N}.json  — template format (for merge_batches.py)

Usage:
  python expand_validate.py \\
      --cases validate-cases-1.json \\
      --context tc-context.json \\
      --inventory inventory.json \\
      --output validate-batch-1.json

Input format (validate-cases-{N}.json):
  [
    {"field": "slaName", "case": "Không truyền"},
    {"field": "slaName", "case": "Truyền null", "value": null},
    {"field": "slaName", "case": "Truyền chuỗi rỗng", "value": ""},
    {"field": "slaName", "case": "Truyền vượt maxLength", "value": "aaa...101"},
    ...
  ]

Output format (validate-batch-{N}.json):
  {
    "_template": { preConditions, stepPrefix, baseParams, importance, result },
    "testCases": [
      { testSuiteName, testCaseName, paramOverride, expectedResult },
      ...
    ]
  }

The output format is template-format, compatible with merge_batches.py.
"""

import json
import sys
import os
import re
import copy
import argparse
import io

# ── UTF-8 guard for Windows ─────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# ── Sentinel value for field removal ─────────────────────────────────────────
_REMOVE = "__REMOVE__"


# ══════════════════════════════════════════════════════════════════════════════
#  Helpers: case-type → error-code mapping
# ══════════════════════════════════════════════════════════════════════════════

def _slugify(text: str) -> str:
    """Convert Vietnamese string to snake_case slug."""
    # lowercase, replace spaces/special chars with underscore, collapse runs
    s = text.lower().strip()
    s = re.sub(r"[^a-zàáạảãâầấậẩẫăằắặẳẫèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộỗỡơờớợởỡùúụủũưừứựữừỳýỵỷỹđ0-9]+", "_", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("_")
    return s


def _normalize_case(case_text: str) -> str:
    """Strip common Vietnamese prefixes to get clean case type."""
    t = case_text.strip()
    # strip trailing "field" / "trường" mention if at start
    t = re.sub(r"^(field|trường|field\s+)", "", t, flags=re.IGNORECASE)
    return t.strip()


def _build_error_map(inv: dict) -> dict:
    """
    Build lookup: case_type_normalized → error_code_entry.
    case_type_normalized is a slug like 'khong_truyen', 'truyen_null', etc.

    Also builds: field_name → list of error_code entries (for cross-field rules).
    """
    error_codes = inv.get("errorCodes", [])
    field_constraints = {f["name"]: f for f in inv.get("fieldConstraints", [])}

    # Map: slug → first matching error code entry
    slug_map = {}
    for ec in error_codes:
        slug_map[_slugify(ec.get("trigger", ""))] = ec
        slug_map[_slugify(ec.get("desc", ""))] = ec
        slug_map[_slugify(ec.get("code", ""))] = ec

    # Field-specific: slug → list of error codes
    field_slug_map = {}
    for ec in error_codes:
        for fc_name, fc in field_constraints.items():
            trigger = ec.get("trigger", "").lower()
            if fc_name.lower() in trigger or trigger in fc_name.lower():
                key = _slugify(fc_name)
                if key not in field_slug_map:
                    field_slug_map[key] = []
                field_slug_map[key].append(ec)

    return slug_map, field_slug_map


def _resolve_error(case_type_norm: str, field_name: str, inv: dict) -> tuple:
    """
    Resolve (error_code, error_message) for a case.
    Returns (code, message) or (None, None) if not found.

    Resolution order:
      1. Match slug against cross-field error codes in inventory
      2. Match slug against generic validate error codes
      3. Match against field-specific error codes
      4. Fall back to generic "Dữ liệu đầu vào không hợp lệ" / "LDH_SLA_020"
    """
    slug_map, field_slug_map = _build_error_map(inv)
    error_codes = inv.get("errorCodes", [])

    # Generic validation error fallback
    generic_validate = next(
        (e for e in error_codes if e.get("section") == "validate" and
         "đầu vào" in e.get("desc", "") or "không hợp lệ" in e.get("desc", "")),
        None
    )

    # 1. Try direct slug match
    if case_type_norm in slug_map:
        ec = slug_map[case_type_norm]
        return ec.get("code", ""), ec.get("desc", "")

    # 2. Try field-specific
    field_slug = _slugify(field_name)
    if field_slug in field_slug_map:
        for ec in field_slug_map[field_slug]:
            # Try exact match on trigger
            trigger_slug = _slugify(ec.get("trigger", ""))
            if trigger_slug == case_type_norm:
                return ec.get("code", ""), ec.get("desc", "")
        # Fall back to first field-specific code
        ec = field_slug_map[field_slug][0]
        return ec.get("code", ""), ec.get("desc", "")

    # 3. Cross-field lookups
    cross_field_patterns = {
        "het_han_lon_hon_hieu_luc": "LDH_SLA_004",
        "hieu_luc_lon_hon_hoac_bang_ngay_hien_tai": "LDH_SLA_003",
        "khong_truyen": None,  # handled by field-level rules
        "truyen_null": None,
        "chieu_dai_vuot_maxlength": None,
        "dinh_dang_sai": None,
        "truyen_chuoi_rong": None,
    }

    # Try generic validate error for common validation cases
    common_validate_cases = [
        "khong_truyen", "truyen_null", "truyen_chuoi_rong", "chieu_dai_vuot_maxlength",
        "dinh_dang_sai", "sai_dinh_dang", "ky_tu_so", "ky_tu_chu", "ky_tu_dac_biet",
        "boolean", "array", "object", "xss", "sql_injection", "emoji",
        "so_am", "so_thap_phan", "chuoi_ky_tu", "all_space", "space_dau_cuoi",
        "mo_rong", "thu_hep", "default_value",
    ]
    if case_type_norm in common_validate_cases:
        if generic_validate:
            return generic_validate.get("code", ""), generic_validate.get("desc", "")

    return None, None


# ══════════════════════════════════════════════════════════════════════════════
#  Helpers: testCaseName & step construction
# ══════════════════════════════════════════════════════════════════════════════

def _build_test_case_name(field: str, case: str, ctx: dict) -> str:
    """Build testCaseName from original Vietnamese text (no slugify)."""
    case_fmt = ctx.get("catalogStyle", {}).get("testCaseNameFormat", "no_underscore")

    if case_fmt == "underscore":
        # Only use slug when explicitly required; otherwise use original case text
        case_slug = _slugify(case)
        if case_slug.startswith(field.lower()):
            return case_slug
        return f"{field}_{case_slug}"
    else:
        # Default: use original case text as-is (Vietnamese, with spaces)
        return case


def _build_param_override(field: str, case: str, value, fc: dict, file_content_base: dict) -> dict:
    """
    Convert (field, case, value) into a paramOverride dict.

    For fileContent fields (columns inside uploaded .xlsx), the override goes under
    the "fileContent" key so merge_batches.py can handle it as a special structure.

    Rules:
      - "Không truyền" / "khong truyen" / "not provided"  → __REMOVE__
      - "Truyền null" / "null"                             → null
      - "Truyền chuỗi rỗng" / "empty string"               → ""
      - Any explicit value provided                        → use it
      - Type-mismatch cases (string→number, etc.)          → use explicit value
    """
    is_file_content = bool(file_content_base) and field in file_content_base
    norm = _normalize_case(case).lower()

    # Determine the actual value
    if norm in ("không truyền", "khong truyen", "not provided", "bo trong",
                "khong gui", "bo qua"):
        actual_value = _REMOVE
    elif norm in ("truyền null", "truyen null", "null", "bằng null"):
        actual_value = None
    elif norm in ("truyền chuỗi rỗng", "truyen chuoi rong", "empty string",
                 "chuỗi rỗng", "empty"):
        actual_value = ""
    elif value is not None:
        actual_value = value
    else:
        actual_value = _REMOVE

    # Wrap under "fileContent" key for fileContent fields
    if is_file_content:
        return {"fileContent": {field: actual_value}}
    return {field: actual_value}


def _build_step(field: str, case: str, value, inv: dict) -> str:
    """Build the step description."""
    norm = _normalize_case(case)

    if value is not None and value != "" and value != _REMOVE:
        if isinstance(value, bool):
            val_str = "true" if value else "false"
        elif isinstance(value, (int, float)):
            val_str = str(value)
        elif isinstance(value, str):
            val_str = f'"{value}"' if len(value) > 20 else value
        elif isinstance(value, list):
            val_str = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, dict):
            val_str = json.dumps(value, ensure_ascii=False)
        else:
            val_str = str(value)

        # Heuristic: type-mismatch cases
        if norm.lower() in ("string thay vì number", "number thay vì string",
                              "sai kiểu dữ liệu", "wrong type", "type error"):
            return f'1. Truyền {field} = {val_str}\n2. Send API'
        if norm.lower() in ("boolean", "boolean thay vì", "true/false"):
            return f'1. Truyền {field} = {val_str}\n2. Send API'
        if norm.lower() in ("array", "array thay vì", "mảng rỗng"):
            return f'1. Truyền {field} = {val_str}\n2. Send API'
        if norm.lower() in ("object", "object thay vì"):
            return f'1. Truyền {field} = {val_str}\n2. Send API'
        if norm.lower() in ("không truyền", "khong truyen", "not provided"):
            return f'1. Không truyền {field}\n2. Send API'
        if norm.lower() in ("truyền null", "truyen null", "null"):
            return f'1. Truyền {field} = null\n2. Send API'
        if norm.lower() in ("truyền chuỗi rỗng", "truyen chuoi rong", "empty string"):
            return f'1. Truyền {field} = ""\n2. Send API'

        # Default: show value
        if norm:
            return f'1. {norm.capitalize()} {field} = {val_str}\n2. Send API'
        else:
            return f'1. Truyền {field} = {val_str}\n2. Send API'

    norm_lower = norm.lower()
    if norm_lower in ("không truyền", "khong truyen", "not provided"):
        return f"1. Không truyền {field}\n2. Send API"
    if norm_lower in ("truyền null", "truyen null", "null"):
        return f"1. Truyền {field} = null\n2. Send API"
    if norm_lower in ("truyền chuỗi rỗng", "truyen chuoi rong", "empty string"):
        return f'1. Truyền {field} = ""\n2. Send API'

    if norm:
        return f'1. {norm.capitalize()} {field}\n2. Send API'
    return f"1. Truyền {field} không hợp lệ\n2. Send API"


# ══════════════════════════════════════════════════════════════════════════════
#  Helpers: expectedResult construction
# ══════════════════════════════════════════════════════════════════════════════

def _fmt_json_multiline(code: str, message: str) -> str:
    return (
        '1. Check api trả về:\n'
        '   1.1. Status: 200\n'
        '   1.2. Response:\n'
        '{\n'
        f'  "code": "{code}",\n'
        f'  "message": "{message}"\n'
        '}'
    )


def _fmt_json_oneline(code: str, message: str) -> str:
    msg_escaped = message.replace('"', '\\"')
    return (
        '1. Check api trả về:\n'
        '   1.1. Status: 200\n'
        '   1.2. Response: '
        f'{{"code":"{code}","message":"{msg_escaped}"}}'
    )


def _build_expected_result(case_type_norm: str, field_name: str,
                            inv: dict, ctx: dict) -> str:
    """
    Build expectedResult text.
    Uses inventory errorCodes to find code+message.
    Falls back to generic validate error.
    """
    code, message = _resolve_error(case_type_norm, field_name, inv)

    if not code:
        # Fallback: use generic validation error from inventory
        error_codes = inv.get("errorCodes", [])
        generic = next(
            (e for e in error_codes
             if e.get("section") == "validate" and
             ("đầu vào" in e.get("desc", "") or "không hợp lệ" in e.get("desc", ""))),
            {"code": "LDH_SLA_020", "desc": "Dữ liệu đầu vào không hợp lệ"}
        )
        code, message = generic.get("code", "LDH_SLA_020"), generic.get("desc", "Dữ liệu đầu vào không hợp lệ")

    json_fmt = ctx.get("catalogStyle", {}).get("responseJsonFormat", "multiline")
    if json_fmt == "oneline":
        return _fmt_json_oneline(code, message)
    return _fmt_json_multiline(code, message)


# ══════════════════════════════════════════════════════════════════════════════
#  Helpers: testSuiteName
# ══════════════════════════════════════════════════════════════════════════════

def _build_test_suite_name(field: str, ctx: dict, display_name: str = "") -> str:
    """Build testSuiteName following catalogStyle.testSuiteNameConvention.

    Uses display_name (from inventory displayName) instead of technical field name
    when available, so suite names match test-design headings (e.g. "File upload"
    not "file").
    """
    import re as _re
    label = display_name if display_name else field
    convention = ctx.get("catalogStyle", {}).get("testSuiteNameConvention", "")
    if convention:
        # Strip connector + unresolved placeholder groups from the raw convention
        # e.g. " hoặc {FieldType}: {FieldName}" → removed before substitution
        cleaned = _re.sub(r'\s*(hoặc|or)\s*(\{[^}]+\}[^{]*)+', '', convention).strip()
        # Replace field name placeholders
        result = cleaned
        for placeholder in ("{fieldName}", "{field}", "{FieldName}", "{FieldType}"):
            result = result.replace(placeholder, label)
        # Final cleanup: remove any leftover {…} tokens
        result = _re.sub(r'\{[^}]+\}', '', result).strip()
        return result
    return f"Kiểm tra trường {label}"


# ══════════════════════════════════════════════════════════════════════════════
#  Main expansion logic
# ══════════════════════════════════════════════════════════════════════════════

def _load_json(path: str, label: str) -> dict | list:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: {label} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: cannot read {label}: {e}", file=sys.stderr)
        sys.exit(1)


def expand(cases: list, ctx: dict, inv: dict) -> dict:
    """
    Expand agent's lightweight case list into template-format batch.

    Returns:
        dict with "_template" + "testCases" (for merge_batches.py)
    """
    base_params = ctx.get("requestBody", {})
    # Separate file content fields base — used when paramOverride targets a fileContent field
    file_content_base = ctx.get("fileContentFieldsBase", {})
    pre_conditions = ctx.get("preConditionsBase", "")
    importance = "Medium"
    result = "PENDING"

    # Build step prefix from preConditions / context
    method = ctx.get("apiEndpoint", "POST /").split(" ")[0]
    step_prefix = (
        f"1. Nhập các tham số\n"
        f"1.1. Authorization: Bearer {{JWT_TOKEN}}\n"
        f"1.2. Method: {method}\n"
        f"1.3. Param:\n"
    )

    # Build fieldConstraints lookup
    field_constraints = {}
    for fc in inv.get("fieldConstraints", []):
        field_constraints[fc["name"]] = fc

    # Build displayName lookup (fieldConstraints + fileContentFields)
    display_names = {}
    for fc in inv.get("fieldConstraints", []):
        if fc.get("displayName"):
            display_names[fc["name"]] = fc["displayName"]
    for fc in inv.get("fileContentFields", []):
        if fc.get("displayName"):
            display_names[fc["name"]] = fc["displayName"]

    test_cases = []

    for item in cases:
        field = item.get("field", "")
        case = item.get("case", "")
        value = item.get("value", _REMOVE)  # default: remove field

        # Phase A Extended: allow agent to override computed fields
        expected_result_override = item.get("expectedResult")
        test_case_name_override = item.get("testCaseName")

        # Skip entries without field or case
        if not field or not case:
            print(f"  WARNING: skipping item without field/case: {item}", file=sys.stderr)
            continue

        case_norm = _slugify(_normalize_case(case))
        fc = field_constraints.get(field, {})
        display_name = display_names.get(field, "")

        # Build components
        param_override = _build_param_override(
            field, case, value, fc, file_content_base
        )
        # Use agent-provided expectedResult if present (Phase A Extended)
        if expected_result_override is not None:
            expected_result = expected_result_override
        else:
            expected_result = _build_expected_result(case_norm, field, inv, ctx)
        test_suite = _build_test_suite_name(field, ctx, display_name)
        # Use agent-provided testCaseName if present (Phase A Extended)
        test_case_name = test_case_name_override or _build_test_case_name(field, case, ctx)

        test_cases.append({
            "testSuiteName": test_suite,
            "testCaseName": test_case_name,
            "paramOverride": param_override,
            "expectedResult": expected_result,
        })

    return {
        "_template": {
            "preConditions": pre_conditions,
            "stepPrefix": step_prefix,
            "baseParams": base_params,
            "importance": importance,
            "result": result,
        },
        "testCases": test_cases,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  CLI entry point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Expand lightweight agent-case list → template-format batch JSON"
    )
    parser.add_argument("--cases", required=True, dest="cases_file",
                        help="Agent output: validate-cases-{N}.json")
    parser.add_argument("--context", required=True, dest="context_file",
                        help="tc-context.json")
    parser.add_argument("--inventory", required=True, dest="inventory_file",
                        help="inventory.json")
    parser.add_argument("--output", required=True, dest="output_file",
                        help="validate-batch-{N}.json")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                        help="Show output without writing")
    args = parser.parse_args()

    # Load inputs
    cases = _load_json(args.cases_file, "cases file")
    if not isinstance(cases, list):
        print("ERROR: cases file must be a JSON array", file=sys.stderr)
        sys.exit(1)

    ctx = _load_json(args.context_file, "tc-context.json")
    inv = _load_json(args.inventory_file, "inventory.json")

    print(f"Loaded {len(cases)} cases from {args.cases_file}")
    print(f"Context: {ctx.get('apiName', '?')} — {ctx.get('apiEndpoint', '?')}")
    print(f"Inventory: {inv.get('_meta', {}).get('name', '?')} "
          f"(errorCodes={len(inv.get('errorCodes', []))}, "
          f"fieldConstraints={len(inv.get('fieldConstraints', []))})")

    # Expand
    result = expand(cases, ctx, inv)
    tc_count = len(result["testCases"])

    # Per-field breakdown
    field_counts = {}
    for tc in result["testCases"]:
        suite = tc.get("testSuiteName", "")
        suite_norm = suite.replace("Kiểm tra trường ", "")
        field_counts[suite_norm] = field_counts.get(suite_norm, 0) + 1

    print(f"\nExpanded → {tc_count} test cases across {len(field_counts)} field(s)")
    for fld, cnt in sorted(field_counts.items()):
        print(f"  {fld}: {cnt} cases")

    if args.dry_run:
        print(f"\nDRY RUN — would write {tc_count} cases to: {args.output_file}")
        print("\nSample test case:")
        if result["testCases"]:
            sample = result["testCases"][0]
            print(json.dumps(sample, ensure_ascii=False, indent=2))
        return

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(args.output_file)), exist_ok=True)
    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Written: {args.output_file}")


if __name__ == "__main__":
    main()
