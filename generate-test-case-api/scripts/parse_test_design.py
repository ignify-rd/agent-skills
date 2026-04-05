#!/usr/bin/env python3
"""
parse_test_design.py — Parse validate sections from test-design-api.md into
                        lightweight cases JSON for expand_validate.py.

Primary source  : test-design-api.md  (QA-editable, authoritative)
Supplement from : inventory.json       (crossFieldRules + conditionalRequired
                                        → adds cases MISSING from test-design)
Merge with      : patch.json (optional) — same schema as inventory, fields
                                          override inventory when present.

Output format (validate-cases.json):
  [
    {
      "field": "debitAccount",
      "case":  "Kiểm tra truyền file hợp lệ, nội dung file Để trống Tài khoản chuyển",
      "value": "__REMOVE__",
      "expectedResult": "1. Check api trả về:\\n  1.1. Status: 200\\n  1.2. Response: Bản ghi không hợp lệ, mô tả lỗi: \\"...\\""
    },
    ...
  ]

Usage:
  python parse_test_design.py \\
      --test-design  feature-4/test-design-api.md \\
      --inventory    feature-4/inventory.json \\
      --patch        feature-4/patch.json \\
      --output       feature-4/validate-cases.json \\
      [--section     "## Kiểm tra Validate"]   # default
      [--dry-run]
"""

import argparse
import io
import json
import os
import re
import sys
from datetime import date, timedelta

# ── UTF-8 guard ──────────────────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

_REMOVE = "__REMOVE__"


# ══════════════════════════════════════════════════════════════════════════════
#  I/O helpers
# ══════════════════════════════════════════════════════════════════════════════

def _load_json(path: str, label: str):
    if not os.path.exists(path):
        print(f"WARNING: {label} not found: {path}", file=sys.stderr)
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: {label} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def _load_text(path: str) -> str:
    if not os.path.exists(path):
        print(f"ERROR: test-design not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════════════
#  Inventory merge  (patch overrides inventory field-by-field)
# ══════════════════════════════════════════════════════════════════════════════

def _merge_inventory(inv: dict, patch: dict) -> dict:
    """Merge patch into inventory. patch.fileContentFields entries override
    matching inventory entries (by name). Other patch keys are ignored."""
    merged = dict(inv)
    patch_fc = {f["name"]: f for f in patch.get("fileContentFields", [])}
    if not patch_fc:
        return merged
    merged_fc = []
    for field in inv.get("fileContentFields", []):
        override = patch_fc.get(field["name"])
        if override:
            merged_fc.append({**field, **override})
        else:
            merged_fc.append(field)
    merged["fileContentFields"] = merged_fc
    return merged


# ══════════════════════════════════════════════════════════════════════════════
#  Build lookup: displayName (case-insensitive) → fieldName
# ══════════════════════════════════════════════════════════════════════════════

def _build_display_map(inv: dict) -> dict:
    """Returns {displayName_lower: fieldName}."""
    m = {}
    for f in inv.get("fileContentFields", []):
        name = f.get("name", "")
        dn = f.get("displayName", "")
        if dn:
            m[dn.lower().strip()] = name
        # Also map name itself (for request fields)
        if name:
            m[name.lower()] = name
    for f in inv.get("fieldConstraints", []):
        name = f.get("name", "")
        if name:
            m[name.lower()] = name
    return m


def _resolve_field(heading: str, display_map: dict) -> str | None:
    """Try to match a ### heading to a fieldName via displayName lookup."""
    heading = heading.strip()
    # Strip common prefixes
    for prefix in ("Trường ", "trường ", "Field ", "field "):
        if heading.startswith(prefix):
            heading = heading[len(prefix):]
            break
    key = heading.lower().strip()
    # Exact match
    if key in display_map:
        return display_map[key]
    # Partial match: find displayName whose lower is a substring of key or vice-versa
    for dn, fn in display_map.items():
        if dn and (dn in key or key in dn):
            return fn
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  Value derivation from case text
# ══════════════════════════════════════════════════════════════════════════════

def _derive_value(case_text: str, field_info: dict) -> object:
    """
    Derive a test value from the case description text.
    Returns _REMOVE, None, or a concrete value.

    Priority:
      1. Explicit length patterns  ("N ký tự")
      2. Semantic patterns         ("Để trống", "toàn space", etc.)
      3. Char-class patterns       ("ký tự số", "ký tự đặc biệt ...")
      4. Date patterns             ("ngày tương lai", "sai định dạng ngày")
      5. Conditional / cross-field → None  (value not derivable)
    """
    t = case_text.lower()

    # ── Removal / empty ──────────────────────────────────────────────────────
    if re.search(r"(để|bỏ)\s*trống|không truyền|không nhập|không điền", t):
        return _REMOVE
    if re.search(r"(toàn|all)\s*(ký tự\s*)?space|toàn\s*dấu\s*cách", t):
        return "   "
    if re.search(r"\boptional\b", t):
        return _REMOVE

    # ── Exact-length patterns ─────────────────────────────────────────────────
    m = re.search(r"(\d+)\s*ký\s*tự\s*\(maxlength\+1\)", t)
    if m:
        return "A" * (int(m.group(1)) + 1)

    m = re.search(r"(\d+)\s*ký\s*tự\s*\(maxlength-1\)", t)
    if m:
        return "A" * (int(m.group(1)) - 1)

    m = re.search(r"(\d+)\s*ký\s*tự\s*\(maxlength\)", t)
    if m:
        return "A" * int(m.group(1))

    # Plain "N ký tự" — check if it's digit-type ("ký tự số")
    m = re.search(r"(\d+)\s*ký\s*tự\s*(số\b)?", t)
    if m:
        n = int(m.group(1))
        is_numeric = bool(m.group(2)) or re.search(r"ký tự số", t)
        if is_numeric:
            # Generate a realistic N-digit number string
            return ("1234567890" * (n // 10 + 1))[:n]
        return "A" * n

    # ── Char-class patterns ───────────────────────────────────────────────────
    if re.search(r"ký tự số\s*\(0-9\)|ký tự số$|^các ký tự số", t):
        return "12345"
    if re.search(r"ký tự chữ (và số|kết hợp)", t):
        return "ABC123"
    if re.search(r"ký tự chữ (không dấu|a-z)|ký tự chữ$", t):
        return "ABCDE"
    if re.search(r"ký tự chữ có dấu|dấu tiếng việt|tiếng việt", t):
        # Check if field allows accents
        if field_info.get("allowAccents") is True:
            return "Tên Có Dấu"
        return "TênCóDấu"

    # Special chars — extract from parentheses in case text (the actual chars)
    m = re.search(r"(ngoài|không\s*cho\s*phép|không\s*hợp\s*lệ).+?\(([^)]+)\)", case_text)
    if m:
        chars = m.group(2).strip()
        # Take first 3 chars that are actually special
        special = [c for c in chars if not c.isalnum() and c not in " \t"]
        return "".join(special[:3]) if special else chars[:4]

    m = re.search(r"(cho\s*phép|hợp\s*lệ).+?\(([^)]+)\)", case_text)
    if m:
        chars = m.group(2).strip()
        return chars[:4]

    if re.search(r"ký tự đặc biệt", t):
        return "!@#$"

    # ── Space patterns ────────────────────────────────────────────────────────
    if re.search(r"khoảng trắng (ở )?giữa|space ở giữa", t):
        return "ABC DEF"
    if re.search(r"khoảng trắng (đầu|cuối)|space đầu|space cuối", t):
        return " ABC "
    if re.search(r"khoảng trắng kép|tab|enter", t):
        return "ABC  DEF"

    # ── Leading-zero patterns ─────────────────────────────────────────────────
    if re.search(r"số 0 ở đầu|leading zero|ký tự ' để giữ số 0", t):
        return "0123"

    # ── Date patterns ─────────────────────────────────────────────────────────
    date_fmt = field_info.get("dateFormat", "")
    if re.search(r"ngày tương lai|future date", t):
        tomorrow = date.today() + timedelta(days=1)
        if date_fmt and "dd" in date_fmt.lower():
            return tomorrow.strftime("%d/%m/%Y")
        return tomorrow.isoformat()

    if re.search(r"sai định dạng (ngày|date)|định dạng ngày không", t):
        return "2025-99-99"

    if re.search(r"ngày không tồn tại|ngày không hợp lệ", t):
        return "30/02/2025"

    # ── Enum / droplist ───────────────────────────────────────────────────────
    enum_vals = field_info.get("enumValues") or []
    if enum_vals and re.search(r"ngoài|không hợp lệ|không tồn tại", t):
        return "INVALID_ENUM_VALUE"
    if enum_vals and re.search(r"hợp lệ|đúng|cho phép", t):
        return enum_vals[0]

    # ── Cross-field / conditional / business-logic → not derivable ───────────
    if re.search(r"khi điều kiện|nộp thay|khác với|không thuộc|không khớp|vượt hạn mức", t):
        return None

    # ── Default: not derivable ────────────────────────────────────────────────
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  Expected-result builder  (used for supplement cases from inventory)
# ══════════════════════════════════════════════════════════════════════════════

def _build_expected_valid() -> str:
    return (
        "1. Check api trả về:\n"
        "  1.1. Status: 200\n"
        "  1.2. Response: Bản ghi hợp lệ"
    )


def _build_expected_invalid(error_msg: str) -> str:
    return (
        "1. Check api trả về:\n"
        "  1.1. Status: 200\n"
        f'  1.2. Response: Bản ghi không hợp lệ, mô tả lỗi: "{error_msg}"'
    )


# ══════════════════════════════════════════════════════════════════════════════
#  Step 1: Parse test-design → cases per field
# ══════════════════════════════════════════════════════════════════════════════

def _parse_test_design(md: str, section_header: str, display_map: dict,
                       fc_lookup: dict) -> list[dict]:
    """
    Parse all bullets under `section_header` (e.g. "## Kiểm tra Validate").

    Returns list of {field, case, value, expectedResult}.
    """
    lines = md.splitlines()
    results = []

    # Find the start line of the target section
    section_start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## ") and section_header.lower() in stripped.lower():
            section_start = i
            break

    if section_start is None:
        print(f"WARNING: section '{section_header}' not found in test-design",
              file=sys.stderr)
        return results

    # Find end of section (next ## at same or higher level)
    section_end = len(lines)
    for i in range(section_start + 1, len(lines)):
        if lines[i].strip().startswith("## "):
            section_end = i
            break

    section_lines = lines[section_start:section_end]

    # Walk section: track current field (###) and bullets (-)
    current_field_name = None
    current_field_info = {}
    i = 0
    while i < len(section_lines):
        line = section_lines[i]
        stripped = line.strip()

        # ### heading → new field
        if stripped.startswith("### "):
            heading = stripped[4:].strip()
            current_field_name = _resolve_field(heading, display_map)
            current_field_info = fc_lookup.get(current_field_name, {})
            if not current_field_name:
                print(f"  WARNING: cannot map heading '{heading}' to a field",
                      file=sys.stderr)
            i += 1
            continue

        # Bullet = one test case
        if stripped.startswith("- ") and current_field_name:
            case_text = stripped[2:].strip()

            # Collect expected result: look ahead for indented response block
            expected_lines = []
            j = i + 1
            while j < len(section_lines):
                ahead = section_lines[j].strip()
                if ahead.startswith("- ") and not ahead.startswith("- 1."):
                    break  # next bullet at same level
                if ahead.startswith("### ") or ahead.startswith("## "):
                    break
                if ahead:
                    expected_lines.append(ahead)
                j += 1

            expected_result = _extract_expected_result(expected_lines, case_text)

            value = _derive_value(case_text, current_field_info)

            results.append({
                "field": current_field_name,
                "case": case_text,
                "value": value,
                "expectedResult": expected_result,
                "_source": "test-design",
            })
            i = j
            continue

        i += 1

    return results


def _extract_expected_result(block_lines: list[str], case_text: str = "") -> str:
    """
    Extract expected result text from the indented block under a bullet.
    Handles both:
      - 1. Check api trả về:
        1.1.Status: 200
        1.2.Response: ...
    """
    if not block_lines:
        return ""

    # Reconstruct into a clean string
    text = "\n".join(block_lines)

    # Extract Status
    status_m = re.search(r"1\.1[.\s]*[Ss]tatus\s*:\s*(\d+)", text)
    status = status_m.group(1) if status_m else "200"

    # Extract Response line
    resp_m = re.search(r"1\.2[.\s]*[Rr]esponse\s*:\s*(.+)", text, re.DOTALL)
    if resp_m:
        resp_text = resp_m.group(1).strip()
        # Clean up trailing lines that are just more step numbering
        resp_text = re.split(r"\n\s*\d+\.", resp_text)[0].strip()
    else:
        resp_text = ""

    if not resp_text and not status:
        return ""

    result = f"1. Check api trả về:\n  1.1. Status: {status}"
    if resp_text:
        result += f"\n  1.2. Response: {resp_text}"
    return result


# ══════════════════════════════════════════════════════════════════════════════
#  Step 2: Supplement from inventory (crossFieldRules + conditionalRequired)
# ══════════════════════════════════════════════════════════════════════════════

def _fingerprint(case: dict) -> str:
    """Simple fingerprint to detect duplicate cases."""
    field = case.get("field", "")
    text = case.get("case", "").lower()
    # Strip boilerplate prefix common in fileContent test-design
    text = re.sub(r"kiểm tra truyền file hợp lệ, nội dung file\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return f"{field}::{text}"


def _supplement_from_inventory(existing: list[dict], inv: dict) -> list[dict]:
    """
    For each crossFieldRule and conditionalRequired in inventory that has
    no corresponding case in `existing`, generate a supplement case.
    Uses inv["_meta"]["caseTitlePrefix"] to match wording style of test-design cases.
    """
    existing_fps = {_fingerprint(c) for c in existing}
    fc_lookup = {f["name"]: f for f in inv.get("fileContentFields", [])}
    # Prefix from inventory _meta — normalises supplement wording to match test-design style
    title_prefix = inv.get("_meta", {}).get("caseTitlePrefix", "").strip()
    supplements = []

    for field_info in inv.get("fileContentFields", []):
        field = field_info.get("name", "")
        display = field_info.get("displayName", field)
        cond_req = field_info.get("conditionalRequired")
        cross_rules = field_info.get("crossFieldRules", [])
        biz_rules = field_info.get("businessValidation", [])

        # ── Conditional required → 2 cases ───────────────────────────────────
        if cond_req and field_info.get("required") == "conditional":
            # Keyword-based dedup: if test-design already has a case for this field
            # containing "khi điều kiện" or similar → skip supplement to avoid duplicate
            existing_for_field = [c for c in existing if c.get("field") == field]
            _conditional_keywords = ["khi điều kiện", "điều kiện", "conditional", "optional"]
            _already_has_conditional = any(
                any(kw in c.get("case", "").lower() for kw in _conditional_keywords)
                for c in existing_for_field
            )

            err_msg = None
            for bv in biz_rules:
                if bv.get("errorMessage"):
                    err_msg = bv["errorMessage"]
                    break
            if not err_msg:
                err_msg = f"Trường {display} không được để trống"

            _case_true_body = (f"Để trống {display} khi điều kiện "
                               f"{cond_req} = true")
            case_true = f"{title_prefix} {_case_true_body}".strip() if title_prefix else _case_true_body
            fp_true = f"{field}::{case_true.lower()}"
            if fp_true not in existing_fps and not _already_has_conditional:
                supplements.append({
                    "field": field,
                    "case": case_true,
                    "value": _REMOVE,
                    "expectedResult": _build_expected_invalid(err_msg),
                    "_source": "inventory:conditionalRequired:true",
                })

            # Case 2: empty when condition = false (should pass)
            _case_false_body = (f"Để trống {display} khi điều kiện "
                                f"{cond_req} = false")
            case_false = f"{title_prefix} {_case_false_body}".strip() if title_prefix else _case_false_body
            fp_false = f"{field}::{case_false.lower()}"
            if fp_false not in existing_fps and not _already_has_conditional:
                supplements.append({
                    "field": field,
                    "case": case_false,
                    "value": _REMOVE,
                    "expectedResult": _build_expected_valid(),
                    "_source": "inventory:conditionalRequired:false",
                })

        # ── Cross-field rules ─────────────────────────────────────────────────
        for rule in cross_rules:
            related = rule.get("relatedField", "")
            rule_text = rule.get("rule", "")
            err_msg = rule.get("errorMessage", "")
            related_display = fc_lookup.get(related, {}).get("displayName", related)

            # Build a case name that reflects the violation
            _body = (f"Nhập {display} vi phạm ràng buộc với {related_display}: "
                     f"{rule_text}")
            case_name = f"{title_prefix} {_body}".strip() if title_prefix else _body

            # Special case: date in future
            if re.search(r"tương lai|future", rule_text, re.IGNORECASE):
                tomorrow = date.today() + timedelta(days=1)
                val = tomorrow.strftime("%d/%m/%Y")
                _b = f"Nhập {display} là ngày tương lai"
                case_name = f"{title_prefix} {_b}".strip() if title_prefix else _b
            elif re.search(r"!=|không\s*(được\s*)?giống|không\s*bằng", rule_text, re.IGNORECASE):
                val = None
                _b = f"Nhập {display} giống {related_display} (vi phạm: {rule_text})"
                case_name = f"{title_prefix} {_b}".strip() if title_prefix else _b
            elif re.search(r"=\s*(mst|mã số|login)|phải\s*(bằng|=)", rule_text, re.IGNORECASE):
                val = None
                _b = f"Nhập {display} khác {related_display} (vi phạm: {rule_text})"
                case_name = f"{title_prefix} {_b}".strip() if title_prefix else _b
            elif re.search(r"thuộc|thuộc về|belong", rule_text, re.IGNORECASE):
                val = None
                _b = f"Nhập {display} không thuộc {related_display} đã chọn"
                case_name = f"{title_prefix} {_b}".strip() if title_prefix else _b
            else:
                val = None

            fp = f"{field}::{case_name.lower()}"
            # Also check if any existing case already covers this errorMessage
            already_covered = any(
                err_msg and err_msg.lower() in (c.get("expectedResult", "")).lower()
                for c in existing
                if c.get("field") == field
            )
            if fp not in existing_fps and not already_covered:
                expected = (_build_expected_invalid(err_msg) if err_msg
                            else _build_expected_valid())
                supplements.append({
                    "field": field,
                    "case": case_name,
                    "value": val,
                    "expectedResult": expected,
                    "_source": f"inventory:crossFieldRule:{related}",
                })

    return supplements


# ══════════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Parse test-design validate sections → lightweight cases JSON"
    )
    parser.add_argument("--test-design", required=True, dest="test_design",
                        help="Path to test-design-api.md")
    parser.add_argument("--inventory", required=True, dest="inventory",
                        help="Path to inventory.json")
    parser.add_argument("--patch", default=None, dest="patch",
                        help="Path to patch.json (optional — overrides inventory fields)")
    parser.add_argument("--output", required=True, dest="output",
                        help="Output path: validate-cases.json")
    parser.add_argument("--section", default="Kiểm tra Validate",
                        help="## section header to parse (default: 'Kiểm tra Validate')")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                        help="Print summary without writing output file")
    args = parser.parse_args()

    # Load inputs
    md = _load_text(args.test_design)
    inv = _load_json(args.inventory, "inventory.json")
    patch = _load_json(args.patch, "patch.json") if args.patch else {}
    merged_inv = _merge_inventory(inv, patch)

    display_map = _build_display_map(merged_inv)
    fc_lookup = {f["name"]: f for f in merged_inv.get("fileContentFields", [])}

    print(f"Parsing: {args.test_design}")
    print(f"Section: ## {args.section}")

    # Step 1: parse test-design
    cases = _parse_test_design(md, args.section, display_map, fc_lookup)
    print(f"\nParsed {len(cases)} cases from test-design")

    # Per-field breakdown
    field_counts: dict[str, int] = {}
    for c in cases:
        field_counts[c["field"]] = field_counts.get(c["field"], 0) + 1
    for fld, cnt in sorted(field_counts.items()):
        print(f"  {fld}: {cnt} cases")

    # Step 2: supplement from inventory
    supplements = _supplement_from_inventory(cases, merged_inv)
    if supplements:
        print(f"\nSupplemented {len(supplements)} cases from inventory "
              f"(not found in test-design):")
        for s in supplements:
            print(f"  [{s['field']}] {s['case'][:80]}  "
                  f"  ← {s.get('_source', '')}")
    else:
        print("\nNo gaps found — test-design covers all inventory rules.")

    # Merge: test-design cases first, then supplements
    all_cases = cases + supplements

    # Rename internal _source → source in output
    output_cases = [
        {("source" if k == "_source" else k): v for k, v in c.items()}
        for c in all_cases
    ]

    # Value derivation summary
    none_val = [c for c in output_cases if c.get("value") is None]
    if none_val:
        print(f"\nNote: {len(none_val)} cases have value=null "
              f"(cross-field / context-dependent — tester fills in):")
        for c in none_val:
            print(f"  [{c['field']}] {c['case'][:70]}")

    print(f"\nTotal: {len(output_cases)} cases "
          f"({len(cases)} from test-design + {len(supplements)} from inventory)")

    if args.dry_run:
        print("\nDRY RUN — not writing output.")
        print("\nSample (first 3 cases):")
        for c in output_cases[:3]:
            print(json.dumps(c, ensure_ascii=False, indent=2))
        return

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_cases, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Written: {args.output}")


if __name__ == "__main__":
    main()
