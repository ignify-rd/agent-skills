#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified verification script for td-verify agent.
Runs ALL V checks + gap analysis in a single pass — reads the output file ONCE.

Usage:
    python3 verify.py --output OUTPUT_FILE --inventory INVENTORY_FILE [--fix]

Output:
    Structured report with PASS/FAIL per check + details for failures.
    Exit code 0 = all pass, 1 = issues found (printed to stdout for agent to fix).
"""

import argparse
import json
import re
import sys
from pathlib import Path


def load_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_inventory(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Section extractors
# ---------------------------------------------------------------------------

def extract_section(content: str, header: str, next_headers: list[str] | None = None) -> str | None:
    """Extract content between a ## header and the next ## header."""
    pattern = re.escape(header)
    if next_headers:
        stop = "|".join(re.escape(h) for h in next_headers)
        m = re.search(rf"^{pattern}(.*?)(?=^(?:{stop})|\Z)", content, re.DOTALL | re.MULTILINE)
    else:
        m = re.search(rf"^{pattern}(.*?)(?=^## |\Z)", content, re.DOTALL | re.MULTILINE)
    return m.group(1) if m else None


def get_headings(text: str, level: str = "###") -> list[str]:
    """Get all headings of a given level from text."""
    prefix = "#" * len(level)
    return re.findall(rf"^{prefix}\s+(.+)$", text or "", re.MULTILINE)


# ---------------------------------------------------------------------------
# Gap Analysis
# ---------------------------------------------------------------------------

def check_gap_error_codes(content: str, inv: dict) -> tuple[bool, list[str]]:
    """Check all errorCodes from inventory appear in output (word boundary match)."""
    codes = [e.get("code", "") for e in inv.get("errorCodes", [])]
    missing = []
    for code in codes:
        if not code:
            continue
        if not re.search(r"\b" + re.escape(code) + r"\b", content):
            section = next(
                (e.get("section", "?") for e in inv.get("errorCodes", []) if e.get("code") == code),
                "?"
            )
            missing.append(f"{code} [section={section}]")
    return len(missing) == 0, missing


def check_gap_db_operations(content: str, inv: dict) -> tuple[bool, list[str]]:
    """Check all dbOperations tables appear in output."""
    tables = []
    for op in inv.get("dbOperations", []):
        table = op if isinstance(op, str) else op.get("table", op.get("name", ""))
        if table:
            tables.append(table)
    missing = [t for t in tables if t not in content]
    return len(missing) == 0, missing


# ---------------------------------------------------------------------------
# V5: Duplicate check between validate and mainflow
# ---------------------------------------------------------------------------

def check_v5_duplicates(content: str) -> tuple[bool, list[str]]:
    validate_text = extract_section(content, "## Kiểm tra Validate",
                                     ["## Kiểm tra chức năng", "## Kiểm tra ngoại lệ"])
    # Also check file content validate section
    fc_text = extract_section(content, "## Kiểm tra Validate nội dung file",
                               ["## Kiểm tra chức năng", "## Kiểm tra ngoại lệ"])
    mainflow_text = extract_section(content, "## Kiểm tra chức năng",
                                     ["## Kiểm tra ngoại lệ"])

    validate_h = set(get_headings(validate_text or ""))
    if fc_text:
        validate_h |= set(get_headings(fc_text))
    mainflow_h = set(get_headings(mainflow_text or ""))

    duplicates = sorted(validate_h & mainflow_h)
    return len(duplicates) == 0, duplicates


# ---------------------------------------------------------------------------
# V5b: Misplaced validate cases in mainflow
# ---------------------------------------------------------------------------

def check_v5b_misplaced(content: str) -> tuple[bool, list[str]]:
    mainflow_text = extract_section(content, "## Kiểm tra chức năng",
                                     ["## Kiểm tra ngoại lệ"])
    mainflow_h = get_headings(mainflow_text or "")

    suspicious_patterns = [
        r"Kiểm tra .*(bỏ trống|để trống|thiếu trường|trường không bắt buộc)",
        r"Kiểm tra .*(không hợp lệ|sai định dạng|sai kiểu).*(field|trường)",
        r"Kiểm tra .*(null|empty|rỗng)",
        r"Kiểm tra .*(bắt buộc nhập|bắt buộc khi)",
    ]

    misplaced = []
    for h in mainflow_h:
        for pat in suspicious_patterns:
            if re.search(pat, h, re.IGNORECASE):
                misplaced.append(h)
                break
    return len(misplaced) == 0, misplaced


# ---------------------------------------------------------------------------
# V5c: Ngoại lệ section ONLY system-level (timeout, 5xx)
# ---------------------------------------------------------------------------

SYSTEM_KEYWORDS = ["timeout", "500", "502", "503", "504", "server", "lỗi hệ thống", "internal", "gateway"]


def check_v5c_ngoaile(content: str) -> tuple[bool, list[str]]:
    ngoaile_text = extract_section(content, "## Kiểm tra ngoại lệ")
    if ngoaile_text is None:
        return False, ["Section 'Kiểm tra ngoại lệ' not found"]

    headings = get_headings(ngoaile_text)
    invalid = []
    for h in headings:
        h_lower = h.lower()
        if not any(k in h_lower for k in SYSTEM_KEYWORDS):
            invalid.append(h)
    return len(invalid) == 0, invalid


# ---------------------------------------------------------------------------
# V9: Global forbidden words scan
# ---------------------------------------------------------------------------

FORBIDDEN_PATTERNS = [
    r"và/hoặc",
    r"(?<!\w)hoặc(?!\w)",  # "hoặc" as standalone word, not part of another word
    r"có thể",
    r"ví dụ:",
    r"\[placeholder\]",
    r"\[value\]",
]


def check_v9_forbidden(content: str) -> tuple[bool, list[dict]]:
    lines = content.split("\n")
    issues = []
    for i, line in enumerate(lines, 1):
        # Skip headings (## / ### / ####) and code blocks
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("```"):
            continue
        for pat in FORBIDDEN_PATTERNS:
            m = re.search(pat, line, re.IGNORECASE)
            if m:
                issues.append({"line": i, "word": m.group(), "context": line.strip()[:80]})
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# V10: Structural check — file starts with # API_NAME
# ---------------------------------------------------------------------------

def check_v10_structure(content: str) -> tuple[bool, list[str]]:
    issues = []
    first_line = content.lstrip().split("\n")[0].strip()
    if not first_line.startswith("# "):
        issues.append(f"File does not start with '# API_NAME'. Found: '{first_line[:60]}'")

    hr_count = len(re.findall(r"^---$", content, re.MULTILINE))
    if hr_count > 0:
        issues.append(f"Found {hr_count} horizontal rules (---) — should be 0")

    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# V11: Validate headings describe conditions, not literal values
# ---------------------------------------------------------------------------

VALUE_PATTERNS = [
    r'= "(?!null|true|false)[^"]{10,}"',  # Quoted string > 10 chars (likely a value, not condition)
    r"= \d{5,}",  # Number with 5+ digits (likely test data)
    r'= "[A-ZĐ][a-zàáạảãâầấậẩẫăằắặẳẵ]',  # Vietnamese sentence in value
]


def check_v11_headings(content: str) -> tuple[bool, list[str]]:
    validate_text = extract_section(content, "## Kiểm tra Validate",
                                     ["## Kiểm tra chức năng", "## Kiểm tra ngoại lệ"])
    fc_text = extract_section(content, "## Kiểm tra Validate nội dung file",
                               ["## Kiểm tra chức năng", "## Kiểm tra ngoại lệ"])

    all_text = (validate_text or "") + "\n" + (fc_text or "")
    # Get bullet-level headings (- Kiểm tra ...)
    bullets = re.findall(r"^- Kiểm tra .+$", all_text, re.MULTILINE)

    invalid = []
    for b in bullets:
        for pat in VALUE_PATTERNS:
            if re.search(pat, b):
                invalid.append(b.strip()[:100])
                break
    return len(invalid) == 0, invalid


# ---------------------------------------------------------------------------
# V12: No ### [SỬA] headings
# ---------------------------------------------------------------------------

def check_v12_sua(content: str) -> tuple[bool, int]:
    count = len(re.findall(r"\[SỬA\]", content))
    return count == 0, count


# ---------------------------------------------------------------------------
# V13: No cases belonging to other API's processing flow
# ---------------------------------------------------------------------------

FLOW_PATTERNS = [
    r"sau khi.*(duyệt|tạo|xóa|chỉnh sửa)",
    r"hiển thị.*trên.*(danh sách|màn hình)",
    r"kết quả.*(tìm kiếm|danh sách).*sau",
]


def check_v13_scope(content: str) -> tuple[bool, list[str]]:
    mainflow_text = extract_section(content, "## Kiểm tra chức năng",
                                     ["## Kiểm tra ngoại lệ"])
    headings = get_headings(mainflow_text or "")

    invalid = []
    for h in headings:
        h_lower = h.lower()
        for pat in FLOW_PATTERNS:
            if re.search(pat, h_lower):
                invalid.append(h)
                break
    return len(invalid) == 0, invalid


# ---------------------------------------------------------------------------
# V14: Array fields have required cases
# ---------------------------------------------------------------------------

ARRAY_REQUIRED_PATTERNS = [
    (r"1 phần tử", "Mảng 1 phần tử"),
    (r"nhiều phần tử", "Mảng nhiều phần tử"),
    (r"trùng nhau|duplicate", "Phần tử trùng nhau"),
    (r"phần tử là String|phần tử.*String.*sai kiểu", "Phần tử là String (sai kiểu)"),
    (r"phần tử là Integer|phần tử.*Integer.*sai kiểu|phần tử.*Number.*sai kiểu",
     "Phần tử là Integer (sai kiểu)"),
]


def check_v14_array(content: str) -> tuple[bool, list[tuple[str, list[str]]]]:
    validate_text = extract_section(content, "## Kiểm tra Validate",
                                     ["## Kiểm tra chức năng", "## Kiểm tra ngoại lệ"])
    if not validate_text:
        return True, []

    field_sections = re.split(r"(?=^### )", validate_text, flags=re.MULTILINE)
    issues = []
    for sec in field_sections:
        # Detect array field by heuristic
        if re.search(r"(mảng rỗng|String thay vì array|thay vì array)", sec, re.IGNORECASE):
            heading = re.match(r"^### (.+)", sec)
            field_name = heading.group(1) if heading else "unknown"
            missing = []
            for pattern, label in ARRAY_REQUIRED_PATTERNS:
                if not re.search(pattern, sec, re.IGNORECASE):
                    missing.append(label)
            if missing:
                issues.append((field_name, missing))
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# Duplicate section headings
# ---------------------------------------------------------------------------

def check_duplicate_headings(content: str) -> tuple[bool, list[str]]:
    """Check for duplicate ## level headings."""
    h2_headings = re.findall(r"^## (.+)$", content, re.MULTILINE)
    from collections import Counter
    counts = Counter(h2_headings)
    duplicates = [f'"{h}" (x{c})' for h, c in counts.items() if c > 1]
    return len(duplicates) == 0, duplicates


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Fix Windows console encoding
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Unified td-verify checks")
    parser.add_argument("--output", required=True, help="Path to test-design-api.md")
    parser.add_argument("--inventory", required=True, help="Path to inventory.json")
    args = parser.parse_args()

    content = load_file(args.output)
    inv = load_inventory(args.inventory)

    results = []
    has_failure = False

    # --- Gap Analysis: errorCodes ---
    ok, missing = check_gap_error_codes(content, inv)
    total_codes = len(inv.get("errorCodes", []))
    covered = total_codes - len(missing)
    results.append(f"[Gap]  errorCodes covered:              {'✅' if ok else '❌'} ({covered}/{total_codes})")
    if not ok:
        has_failure = True
        for m in missing:
            results.append(f"       ☐ {m} — chưa có trong output")

    # --- Gap Analysis: dbOperations ---
    ok, missing = check_gap_db_operations(content, inv)
    total_db = len(inv.get("dbOperations", []))
    covered_db = total_db - len(missing)
    results.append(f"[Gap]  dbOperations covered:            {'✅' if ok else '❌'} ({covered_db}/{total_db})")
    if not ok:
        has_failure = True
        for m in missing:
            results.append(f"       ☐ {m} — chưa có trong SQL SELECT")

    # --- Duplicate ## headings ---
    ok, dups = check_duplicate_headings(content)
    results.append(f"[Dup]  No duplicate ## headings:        {'✅' if ok else '❌'} ({len(dups)} duplicates)")
    if not ok:
        has_failure = True
        for d in dups:
            results.append(f"       - {d}")

    # --- V5: Cross-section duplicate ---
    ok, dups = check_v5_duplicates(content)
    results.append(f"[V5]   No duplicate validate↔main:      {'✅' if ok else '❌'} ({len(dups)} duplicates)")
    if not ok:
        has_failure = True
        for d in dups:
            results.append(f"       - {d}")

    # --- V5b: Misplaced validate in mainflow ---
    ok, misplaced = check_v5b_misplaced(content)
    results.append(f"[V5b]  No misplaced validate in main:   {'✅' if ok else '❌'} ({len(misplaced)} cases)")
    if not ok:
        has_failure = True
        for m in misplaced:
            results.append(f"       - {m}")

    # --- V5c: Ngoại lệ only system-level ---
    ok, invalid = check_v5c_ngoaile(content)
    results.append(f"[V5c]  Ngoại lệ ONLY system-level:     {'✅' if ok else '❌'} ({len(invalid)} business errors)")
    if not ok:
        has_failure = True
        for i in invalid:
            results.append(f"       - {i}")

    # --- V9: Forbidden words ---
    ok, issues = check_v9_forbidden(content)
    results.append(f"[V9]   No forbidden words:              {'✅' if ok else '❌'} ({len(issues)} occurrences)")
    if not ok:
        has_failure = True
        for issue in issues[:10]:  # limit output
            results.append(f"       L{issue['line']}: \"{issue['word']}\" — {issue['context']}")

    # --- V10: Structure ---
    ok, issues = check_v10_structure(content)
    results.append(f"[V10]  Format correct (# header):       {'✅' if ok else '❌'}")
    if not ok:
        has_failure = True
        for i in issues:
            results.append(f"       - {i}")

    # --- V11: Validate headings = conditions ---
    ok, invalid = check_v11_headings(content)
    results.append(f"[V11]  Validate headings = conditions:  {'✅' if ok else '❌'} ({len(invalid)} value-headings)")
    if not ok:
        has_failure = True
        for i in invalid[:10]:
            results.append(f"       - {i}")

    # --- V12: No [SỬA] ---
    ok, count = check_v12_sua(content)
    results.append(f"[V12]  No ### [SỬA] headings:           {'✅' if ok else '❌'} ({count})")
    if not ok:
        has_failure = True

    # --- V13: No other API flow ---
    ok, invalid = check_v13_scope(content)
    results.append(f"[V13]  No other API's flow cases:       {'✅' if ok else '❌'} ({len(invalid)} cases)")
    if not ok:
        has_failure = True
        for i in invalid:
            results.append(f"       - {i}")

    # --- V14: Array fields ---
    ok, issues = check_v14_array(content)
    label = "N/A" if not issues and ok else f"{len(issues)} fields"
    results.append(f"[V14]  Array fields — new cases:        {'✅' if ok else '❌'} ({label})")
    if not ok:
        has_failure = True
        for fname, missing in issues:
            results.append(f"       - {fname}: thiếu {missing}")

    # --- Summary ---
    check_names = ["Gap-EC", "Gap-DB", "Dup", "V5", "V5b", "V5c", "V9", "V10", "V11", "V12", "V13", "V14"]
    pass_count = sum(1 for line in results if line.startswith("[") and "✅" in line)
    total_count = sum(1 for line in results if line.startswith("["))

    print("=== SELF-CHECK (td-verify) ===")
    for r in results:
        print(r)
    print(f"=== KẾT QUẢ: {pass_count}/{total_count} ===")

    sys.exit(1 if has_failure else 0)


if __name__ == "__main__":
    main()
