#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_postman_results.py — Merge auto-postman API test results into a test case Excel file.

Reads api_results_*.xlsx (auto-postman output), matches rows by test case name,
fills Actual Result with the raw response (Status + Response Body), evaluates
Pass/Fail via Claude AI and writes the verdict to the "Kết quả hiện tại" (status)
column, replaces sample JSON in Expected Result with real response JSON, and
embeds screenshots in an Evidence sheet.

Usage:
  python merge_postman_results.py \\
    --source api_results_20260415_091720.xlsx \\
    --target test_cases.xlsx \\
    --structure structure.json \\
    [--output result.xlsx] \\
    [--api-key sk-ant-...] \\
    [--no-ai] \\
    [--dry-run]

Requirements:
  pip install openpyxl pillow anthropic
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Extract embedded images from xlsx drawing layer
# ---------------------------------------------------------------------------

def _extract_embedded_images(xlsx_path: str, col_index: int = None) -> dict:
    """
    Parse the drawing XML inside an xlsx (zip) file and return a dict mapping
    0-based row index → raw image bytes.

    Drawing coordinates use 0-based row/col indices where Excel row N = drawing row N-1.

    Args:
        xlsx_path:  Path to the xlsx file.
        col_index:  0-based column index to filter images by (None = all columns).

    Returns:
        dict: { drawing_row_0based: bytes }
    """
    import zipfile
    import xml.etree.ElementTree as ET

    NS_SD = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
    NS_A  = "http://schemas.openxmlformats.org/drawingml/2006/main"
    NS_R  = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    NS_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"

    result = {}

    with zipfile.ZipFile(xlsx_path) as zf:
        names = set(zf.namelist())

        # Find all drawing files (support multiple sheets)
        drawing_files = sorted(
            n for n in names
            if n.startswith("xl/drawings/drawing") and n.endswith(".xml") and "_rels" not in n
        )
        if not drawing_files:
            return result

        for drawing_path in drawing_files:
            rels_path = f"xl/drawings/_rels/{drawing_path.split('/')[-1]}.rels"
            if rels_path not in names:
                continue

            # rId → media path  (e.g.  rId1 → xl/media/image1.png)
            rels_root = ET.fromstring(zf.read(rels_path).decode("utf-8"))
            rid_to_media = {}
            for rel in rels_root.findall(f"{{{NS_PKG}}}Relationship"):
                rid    = rel.get("Id")
                target = rel.get("Target", "")
                if "media" in target:
                    # target is like "../media/image1.png" — normalise to xl/media/...
                    media_path = "xl/media/" + target.rsplit("/", 1)[-1]
                    rid_to_media[rid] = media_path

            # Parse anchors → (row, col, rId)
            drawing_root = ET.fromstring(zf.read(drawing_path).decode("utf-8"))
            anchor_types = [f"{{{NS_SD}}}oneCellAnchor", f"{{{NS_SD}}}twoCellAnchor"]

            for anchor_tag in anchor_types:
                for anchor in drawing_root.findall(anchor_tag):
                    from_el = anchor.find(f"{{{NS_SD}}}from")
                    if from_el is None:
                        continue

                    col_el = from_el.find(f"{{{NS_SD}}}col")
                    row_el = from_el.find(f"{{{NS_SD}}}row")
                    if col_el is None or row_el is None:
                        continue

                    img_col = int(col_el.text)   # 0-based
                    img_row = int(row_el.text)   # 0-based

                    if col_index is not None and img_col != col_index:
                        continue

                    # Drill down to the blip embed rId
                    pic = anchor.find(f"{{{NS_SD}}}pic")
                    if pic is None:
                        continue
                    blip_fill = pic.find(f"{{{NS_SD}}}blipFill")
                    if blip_fill is None:
                        continue
                    blip = blip_fill.find(f"{{{NS_A}}}blip")
                    if blip is None:
                        continue

                    rid = blip.get(f"{{{NS_R}}}embed")
                    if not rid:
                        continue

                    media_path = rid_to_media.get(rid)
                    if media_path and media_path in names:
                        result[img_row] = zf.read(media_path)

    return result


# ---------------------------------------------------------------------------
# Load source (auto-postman output)
# ---------------------------------------------------------------------------

def load_source(source_path: str) -> dict:
    """
    Load auto-postman results xlsx.

    Supports two screenshot formats:
      - NEW: screenshots embedded directly as images in the xlsx drawing layer.
             The Screenshot cell is empty; images are matched by row position.
      - OLD: Screenshot cell contains a relative file path to a .png file.

    Returns:
        dict: { api_name: { status_code, response_body, screenshot } }
              'screenshot' is raw bytes (embedded) or a file-path string,
              or None when no screenshot is available.
    """
    import openpyxl

    wb = openpyxl.load_workbook(source_path, data_only=True)
    ws = wb.active
    source_dir = Path(source_path).parent

    # Locate header row — first row that contains 'API Name'
    header_row_idx = None
    col_indices = {}

    for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
        vals = [str(v).strip() if v is not None else "" for v in row]
        if "API Name" in vals:
            header_row_idx = row_idx
            for col_idx, val in enumerate(vals):
                col_indices[val] = col_idx
            break

    if header_row_idx is None:
        raise ValueError(
            f"Cannot find 'API Name' header in source xlsx: {source_path}"
        )

    api_col    = col_indices.get("API Name")
    status_col = col_indices.get("Status Code")
    body_col   = col_indices.get("Response Body")
    shot_col   = col_indices.get("Screenshot")

    # Pre-extract embedded images keyed by 0-based drawing row index.
    # Drawing row 0 = Excel row 1, so: drawing_row = excel_row - 1.
    embedded = {}
    if shot_col is not None:
        embedded = _extract_embedded_images(source_path, col_index=shot_col)

    results = {}

    for excel_row, row in enumerate(
        ws.iter_rows(min_row=header_row_idx + 1, values_only=True),
        start=header_row_idx + 1,
    ):
        if api_col is None or row[api_col] is None:
            continue

        name = str(row[api_col]).strip()
        if not name:
            continue

        # --- Screenshot resolution (new embedded format takes priority) ---
        drawing_row = excel_row - 1   # 0-based drawing coordinate
        screenshot = embedded.get(drawing_row)  # bytes if embedded, else None

        if screenshot is None and shot_col is not None and row[shot_col]:
            # Fallback: old format with file path in the cell
            raw = str(row[shot_col]).replace("\\", "/").strip()
            for candidate in [
                source_dir / raw,          # e.g. results/screenshots/…
                source_dir.parent / raw,   # e.g. auto-postman/screenshots/…
                Path(raw),                 # absolute path
            ]:
                if candidate.exists():
                    screenshot = str(candidate)
                    break

        results[name] = {
            "status_code": (
                str(row[status_col]).strip()
                if status_col is not None and row[status_col] is not None
                else ""
            ),
            "response_body": (
                str(row[body_col]).replace("\xa0", " ").strip()
                if body_col is not None and row[body_col] is not None
                else ""
            ),
            "screenshot": screenshot,   # bytes | path string | None
        }

    return results


# ---------------------------------------------------------------------------
# Column detection from structure.json + header row scan
# ---------------------------------------------------------------------------

FIELD_SYNONYMS = {
    "testCaseName": [
        "Name", "Test Case Name", "TestCase Name", "Tên test case",
        "API Name", "testCaseName",
    ],
    "status": [
        "Status", "Trạng thái", "Kết quả", "Result",
        "Pass/Fail", "ExecutionStatus", "Kết quả hiện tại",
    ],
    "expectedResults": [
        "Expected Result", "Expected Results", "Expected",
        "Kết quả mong đợi", "ExpectedResult",
    ],
    "actualResult": [
        "Actual Result", "Actual", "Kết quả thực tế", "ActualResult",
    ],
}


def detect_columns(ws, structure: dict) -> dict:
    """
    Merge structure.json columnMapping with header-row auto-detection.

    Returns:
        dict: { field_name: 0-based column index }
    """
    mapping = {k: int(v) for k, v in structure.get("columnMapping", {}).items()}
    header_row = structure.get("headerRow", 1)

    headers = [cell.value for cell in ws[header_row]]

    for field, synonyms in FIELD_SYNONYMS.items():
        if field not in mapping:
            for col_idx, header_val in enumerate(headers):
                if header_val in synonyms:
                    mapping[field] = col_idx
                    break

    return mapping


def auto_detect_structure(ws, structure: dict) -> tuple:
    """
    Scan the entire worksheet to find the real header row and column mapping
    when the structure.json values appear to be wrong (e.g., matched = 0).

    Strategy: look for a row that contains at least 2 known column name synonyms.

    Returns:
        (header_row, data_start_row, col_map)  — all 1-based row numbers, 0-based col indices.
        Returns the original values unchanged if no better row is found.
    """
    all_synonyms = {v: field for field, syns in FIELD_SYNONYMS.items() for v in syns}

    best_row     = None
    best_score   = 0
    best_mapping = {}

    for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
        found = {}
        for col_idx, val in enumerate(row):
            if val and str(val).strip() in all_synonyms:
                field = all_synonyms[str(val).strip()]
                if field not in found:
                    found[field] = col_idx

        if len(found) >= 2 and len(found) > best_score:
            best_score   = len(found)
            best_row     = row_idx
            best_mapping = found

    if best_row is None:
        # Nothing better found — return originals
        orig_header = structure.get("headerRow", 1)
        return orig_header, structure.get("dataStartRow", orig_header + 1), detect_columns(ws, structure)

    # Merge with existing structure.json mapping (structure.json wins for fields not found by scan)
    existing = {k: int(v) for k, v in structure.get("columnMapping", {}).items()}
    merged = {**existing, **best_mapping}   # scan result overrides for detected fields

    # data_start_row: skip the row right after header if it looks like a suite/group header
    data_row = best_row + 1
    first_data = [ws.cell(data_row, c + 1).value for c in range(min(ws.max_column, 5))]
    tc_col = merged.get("testCaseName")
    if tc_col is not None:
        tc_val = ws.cell(data_row, tc_col + 1).value
        if not tc_val:                          # blank in name col → likely a group row
            data_row = best_row + 2

    return best_row, data_row, merged


# ---------------------------------------------------------------------------
# JSON replacement in expected result text
# ---------------------------------------------------------------------------

def _find_outermost_json(text: str):
    """
    Find the first top-level JSON object { ... } in text.

    Returns:
        (start, end) indices or None
    """
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                return start, i + 1
    return None


def replace_json_in_expected(expected_text: str, actual_body: str) -> str:
    """
    Replace the sample JSON object inside expected_text with the real response body.
    Text outside the JSON block (descriptions, status lines) is preserved.

    Example:
        expected_text = "1. Check:\n 1.1. Status: 200\n 1.2. Response:\n{\"code\":0}"
        actual_body   = '{"code":200,"message":"OK"}'
        → "1. Check:\n 1.1. Status: 200\n 1.2. Response:\n{\n  \"code\": 200,\n  \"message\": \"OK\"\n}"
    """
    if not actual_body:
        return expected_text

    span = _find_outermost_json(expected_text)
    if span is None:
        # No JSON block found — append actual body after a separator
        return expected_text + "\n" + actual_body

    start, end = span

    # Pretty-print actual body if it is valid JSON
    clean = actual_body.replace("\xa0", " ").strip()
    try:
        obj = json.loads(clean)
        formatted = json.dumps(obj, ensure_ascii=False, indent=2)
    except (json.JSONDecodeError, ValueError):
        formatted = clean

    return expected_text[:start] + formatted + expected_text[end:]


# ---------------------------------------------------------------------------
# Cell formatting helpers
# ---------------------------------------------------------------------------

def _wrap_align():
    """Return an Alignment with wrap_text=True, top-aligned."""
    from openpyxl.styles import Alignment
    return Alignment(wrap_text=True, vertical="top")


def _autofit_row_height(ws, row_idx: int, *col_indices):
    """
    Set row height based on the maximum line count across the given columns.
    Each text line ≈ 15 pt. Minimum 15 pt, capped at 409 pt (Excel max).
    """
    LINE_HEIGHT_PT = 15
    max_lines = 1
    for col_idx in col_indices:
        if col_idx is None:
            continue
        val = ws.cell(row=row_idx, column=col_idx + 1).value
        if val:
            lines = str(val).count("\n") + 1
            max_lines = max(max_lines, lines)
    height = min(max_lines * LINE_HEIGHT_PT, 409)
    ws.row_dimensions[row_idx].height = height


# ---------------------------------------------------------------------------
# Pass / Fail evaluation
# ---------------------------------------------------------------------------

def _extract_status_code(text: str):
    """Pull the first 3-digit status code from a text block."""
    m = re.search(r"\b(\d{3})\b", text or "")
    return m.group(1) if m else None


def evaluate_simple(expected_text: str, actual_text: str):
    """
    Rule-based evaluation: compare status codes extracted from both texts.

    Returns:
        (verdict, reason)  — verdict is 'PASS', 'FAIL', or 'N/A'
    """
    if not actual_text or not actual_text.strip():
        return "N/A", "No actual result"

    exp_status = _extract_status_code(expected_text)
    act_status = _extract_status_code(actual_text)

    if exp_status and act_status:
        if exp_status == act_status:
            return "PASS", f"Status code match: {act_status}"
        return "FAIL", f"Status mismatch: expected {exp_status}, got {act_status}"

    return "FAIL", "Cannot determine (no 3-digit status code found)"


def evaluate_ai(expected_text: str, actual_text: str, api_key: str = None):
    """
    Ask Claude to evaluate Pass / Fail by comparing expected vs actual results.

    Returns:
        (verdict, reason)
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("  [warn] ANTHROPIC_API_KEY not set — falling back to simple evaluation",
              file=sys.stderr)
        return evaluate_simple(expected_text, actual_text)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=key)
        prompt = (
            "Bạn là QA engineer đang đánh giá kết quả test API.\n\n"
            f"**Kết quả mong đợi (Expected Result):**\n{expected_text}\n\n"
            f"**Kết quả thực tế (Actual Result):**\n{actual_text}\n\n"
            "So sánh kết quả thực tế với kết quả mong đợi:\n"
            "- PASS: status code và cấu trúc/giá trị quan trọng của response khớp\n"
            "- FAIL: không khớp\n"
            "- N/A: không đủ dữ liệu để đánh giá\n\n"
            "Trả lời theo đúng format: PASS|FAIL|N/A - <lý do ngắn gọn, 1 dòng>"
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()

        upper = text.upper()
        if upper.startswith("PASS"):
            return "PASS", text
        elif upper.startswith("FAIL"):
            return "FAIL", text
        elif upper.startswith("N/A"):
            return "N/A", text
        else:
            # Claude responded with something else — treat as FAIL and include the note
            return "FAIL", text

    except Exception as exc:
        print(f"  [warn] AI evaluation error: {exc} — falling back to simple", file=sys.stderr)
        return evaluate_simple(expected_text, actual_text)


# ---------------------------------------------------------------------------
# Evidence sheet
# ---------------------------------------------------------------------------

def update_evidence_sheet(wb, source_results: dict):
    """
    Create (or replace) the 'Evidence' sheet.

    Layout:
        Column A — ID (test case name)
        Column B — Evidence (embedded screenshot, or placeholder text)

    'screenshot' in source_results can be:
        bytes      — image extracted from the source xlsx drawing layer (new format)
        str        — absolute file path (old format)
        None       — no screenshot available
    """
    SHEET_NAME = "Evidence"

    if SHEET_NAME in wb.sheetnames:
        del wb[SHEET_NAME]

    # Always create Evidence as the second sheet (index 1)
    ws = wb.create_sheet(SHEET_NAME, index=1)
    ws["A1"] = "ID"
    ws["B1"] = "Evidence"
    ws.column_dimensions["A"].width = 55
    ws.column_dimensions["B"].width = 90

    row_num = 2
    for api_name, data in source_results.items():
        # Use externalId if captured from target file, fallback to api_name
        display_id = data.get("externalId") or api_name
        ws[f"A{row_num}"] = display_id
        shot = data.get("screenshot")

        if isinstance(shot, (bytes, bytearray)) and shot:
            # New format: embedded image bytes extracted from source xlsx
            ok = _embed_image_bytes(ws, row_num, "B", shot)
            if not ok:
                ws[f"B{row_num}"] = "[Image embed failed]"
        elif isinstance(shot, str) and os.path.exists(shot):
            # Old format: file path
            _embed_image_file(ws, row_num, "B", shot)
        else:
            ws[f"B{row_num}"] = "[No screenshot]"

        row_num += 1


def _scale_dimensions(width: int, height: int, max_w: int = 700, max_h: int = 450):
    """Return (w, h) scaled down to fit within max_w × max_h, preserving aspect ratio."""
    scale = min(max_w / max(width, 1), max_h / max(height, 1), 1.0)
    return int(width * scale), int(height * scale)


def _apply_image_to_cell(ws, img, row_num: int, col_letter: str):
    """Anchor img to the cell, set row height and column width to match."""
    from openpyxl.utils import column_index_from_string, get_column_letter

    img.anchor = f"{col_letter}{row_num}"
    ws.add_image(img)

    ws.row_dimensions[row_num].height = img.height / 1.33   # px → pt
    col_idx = column_index_from_string(col_letter)
    ws.column_dimensions[get_column_letter(col_idx)].width = max(
        ws.column_dimensions[get_column_letter(col_idx)].width or 0,
        img.width / 7,
    )


def _embed_image_bytes(ws, row_num: int, col_letter: str, img_bytes: bytes) -> bool:
    """
    Embed raw image bytes into a cell.  Uses a BytesIO buffer — no temp file needed.
    Returns True on success.
    """
    try:
        import io
        from openpyxl.drawing.image import Image as XLImage
        from PIL import Image as PILImage

        pil_img = PILImage.open(io.BytesIO(img_bytes))
        w, h = _scale_dimensions(pil_img.width, pil_img.height)

        # openpyxl needs to know the format; save through a buffer
        buf = io.BytesIO()
        fmt = pil_img.format or "PNG"
        pil_img.save(buf, format=fmt)
        buf.seek(0)

        xl_img = XLImage(buf)
        xl_img.width, xl_img.height = w, h
        _apply_image_to_cell(ws, xl_img, row_num, col_letter)
        return True

    except Exception as exc:
        ws[f"{col_letter}{row_num}"] = f"[Image error: {exc}]"
        return False


def _embed_image_file(ws, row_num: int, col_letter: str, img_path: str):
    """Embed an image from a file path into a cell."""
    try:
        from openpyxl.drawing.image import Image as XLImage

        xl_img = XLImage(img_path)
        w, h = _scale_dimensions(xl_img.width, xl_img.height)
        xl_img.width, xl_img.height = w, h
        _apply_image_to_cell(ws, xl_img, row_num, col_letter)

    except Exception as exc:
        ws[f"{col_letter}{row_num}"] = f"[Image error: {exc}]"


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def _verify_output(out_path: str, structure: dict, col_map: dict, data_start_row: int, expected_matched: int) -> dict:
    """
    Re-open the saved file and verify key columns were written correctly.

    Checks:
      - actualResult: how many rows have response content written
      - expectedResults: how many rows where JSON was replaced (contains '{')
      - Evidence sheet: row count vs image count
    """
    import openpyxl

    wb = openpyxl.load_workbook(out_path, data_only=True)
    ws = wb.worksheets[0]

    act_col = col_map.get("actualResult")
    exp_col = col_map.get("expectedResults")

    actual_written = 0
    status_written = 0
    verdict_counts = {"PASS": 0, "FAIL": 0, "N/A": 0}
    json_replaced   = 0
    blank_actual    = []

    verdicts_set = {"PASS", "FAIL", "N/A"}
    sts_col_v = col_map.get("status")

    for row_idx in range(data_start_row, ws.max_row + 1):
        # Only check rows that should have been updated (non-empty testCaseName)
        tc_col = col_map.get("testCaseName")
        if tc_col is not None:
            tc_val = ws.cell(row=row_idx, column=tc_col + 1).value
            if not tc_val:
                continue

        if act_col is not None:
            cell_val = ws.cell(row=row_idx, column=act_col + 1).value
            text = str(cell_val or "").strip()
            if text:
                actual_written += 1
            else:
                blank_actual.append(row_idx)

        # Check status column for verdict
        if sts_col_v is not None:
            sts_val = ws.cell(row=row_idx, column=sts_col_v + 1).value
            sts_text = str(sts_val or "").strip()
            if sts_text in verdicts_set:
                status_written += 1
                verdict_counts[sts_text] = verdict_counts.get(sts_text, 0) + 1

        if exp_col is not None:
            exp_val = ws.cell(row=row_idx, column=exp_col + 1).value
            if exp_val and "{" in str(exp_val):
                json_replaced += 1

    # Evidence sheet
    ev_rows   = 0
    ev_images = 0
    if "Evidence" in wb.sheetnames:
        ev_ws = wb["Evidence"]
        ev_rows   = max(ev_ws.max_row - 1, 0)   # minus header
        ev_images = len(ev_ws._images)

    ok = actual_written == expected_matched

    return {
        "ok":              ok,
        "expected_matched": expected_matched,
        "actual_written":  actual_written,
        "status_written":  status_written,
        "verdict_counts":  verdict_counts,
        "json_replaced":   json_replaced,
        "evidence_rows":   ev_rows,
        "evidence_images": ev_images,
        "blank_actual_rows": blank_actual,
    }


def _print_verify(v: dict):
    ok_mark = "✓" if v["ok"] else "✗"
    print(f"  {ok_mark} actualResult written : {v['actual_written']} / {v['expected_matched']}"
          + ("" if v["ok"] else "  ← MISMATCH"))
    print(f"  ✓ status (Kết quả hiện tại) written : {v.get('status_written', 0)}")
    print(f"    PASS={v['verdict_counts'].get('PASS',0)}  "
          f"FAIL={v['verdict_counts'].get('FAIL',0)}  "
          f"N/A={v['verdict_counts'].get('N/A',0)}")
    print(f"  ✓ expectedResults with JSON : {v['json_replaced']} rows")
    ev_ok = v["evidence_images"] == v["evidence_rows"]
    ev_mark = "✓" if ev_ok else "✗"
    print(f"  {ev_mark} Evidence sheet : {v['evidence_images']} images / {v['evidence_rows']} rows"
          + ("" if ev_ok else "  ← some images missing"))
    if v["blank_actual_rows"]:
        print(f"  [warn] Rows with value but no verdict prefix: {v['blank_actual_rows']}")
    if not v["ok"] or not ev_ok:
        print("  → Check structure.json column mapping and re-run.")


# ---------------------------------------------------------------------------
# Main merge logic
# ---------------------------------------------------------------------------

def merge_results(
    source_path: str,
    target_path: str,
    structure_path: str,
    output_path: str = None,
    api_key: str = None,
    no_ai: bool = False,
    dry_run: bool = False,
    auto_fix: bool = True,
) -> dict:
    import openpyxl

    print(f"[1/4] Loading source: {source_path}")
    source_results = load_source(source_path)
    print(f"      {len(source_results)} test results found")

    print(f"[2/4] Loading structure: {structure_path}")
    with open(structure_path, "r", encoding="utf-8") as f:
        structure = json.load(f)

    print(f"[3/4] Loading target: {target_path}")
    wb = openpyxl.load_workbook(target_path)

    # Always use the first sheet for test case data
    ws = wb.worksheets[0]
    print(f"      Sheet: '{ws.title}'")

    col_map = detect_columns(ws, structure)
    header_row    = structure.get("headerRow", 1)
    data_start_row = structure.get("dataStartRow", header_row + 1)

    # Validate required columns
    tc_col  = col_map.get("testCaseName")
    exp_col = col_map.get("expectedResults")
    act_col = col_map.get("actualResult")
    sts_col = col_map.get("status")

    missing = [f for f, c in [("testCaseName", tc_col)] if c is None]
    if missing:
        raise ValueError(
            f"Cannot find columns: {missing}. "
            "Check structure.json columnMapping or target file header row."
        )

    print(f"      Column map: testCaseName={tc_col} status={sts_col} "
          f"expectedResults={exp_col} actualResult={act_col}")
    if sts_col is None:
        print("      [warn] 'status' column not found — Pass/Fail will not be written. "
              "Add 'status': <col_index> to columnMapping in structure.json.")

    # Print a sample of what the testCaseName column contains (helps debug mismatches)
    sample_names = []
    for r in ws.iter_rows(min_row=data_start_row, max_row=data_start_row + 3, values_only=True):
        if tc_col is not None and r[tc_col]:
            sample_names.append(str(r[tc_col])[:60])
    if sample_names:
        print(f"      Sample testCaseName values (rows {data_start_row}+): {sample_names}")

    # --- Process each data row ---
    print(f"[4/4] Merging results (rows {data_start_row}+) ...")
    matched = 0
    not_found = []
    verdicts = {"PASS": 0, "FAIL": 0, "N/A": 0}

    for row_idx in range(data_start_row, ws.max_row + 1):
        # Get test case name from the match-key column
        tc_cell = ws.cell(row=row_idx, column=tc_col + 1)
        if tc_cell.value is None:
            continue
        tc_name = str(tc_cell.value).strip()
        if not tc_name:
            continue

        if tc_name not in source_results:
            not_found.append(tc_name)
            continue

        matched += 1
        data = source_results[tc_name]

        # Read existing expected result (needed for AI evaluation + JSON replacement)
        expected_text = ""
        if exp_col is not None:
            exp_cell = ws.cell(row=row_idx, column=exp_col + 1)
            expected_text = str(exp_cell.value or "")

        # Build raw actual text (used for AI comparison)
        raw_actual = f"Status: {data['status_code']}\nResponse:\n{data['response_body']}"

        # Evaluate Pass/Fail
        if no_ai:
            verdict, reason = evaluate_simple(expected_text, raw_actual)
        else:
            verdict, reason = evaluate_ai(expected_text, raw_actual, api_key)

        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        print(f"  [{verdict:7s}] {tc_name[:65]}")

        # Read externalId from target row (used for Evidence sheet)
        ext_id_col = col_map.get("externalId")
        if ext_id_col is not None:
            ext_id_val = ws.cell(row=row_idx, column=ext_id_col + 1).value
            if ext_id_val:
                data["externalId"] = str(ext_id_val).strip()

        if dry_run:
            continue

        # Write actual result: raw response (status code + response body)
        if act_col is not None:
            cell = ws.cell(row=row_idx, column=act_col + 1)
            cell.value = raw_actual
            cell.alignment = _wrap_align()

        # Write verdict (PASS/FAIL/N/A) to "Kết quả hiện tại" (status) column
        if sts_col is not None:
            cell = ws.cell(row=row_idx, column=sts_col + 1)
            cell.value = verdict
            cell.alignment = _wrap_align()

        # Replace sample JSON in expected result with real response JSON
        if exp_col is not None and data["response_body"]:
            updated_expected = replace_json_in_expected(expected_text, data["response_body"])
            cell = ws.cell(row=row_idx, column=exp_col + 1)
            cell.value = updated_expected
            cell.alignment = _wrap_align()

        # Auto-fit row height based on line count in actual result
        _autofit_row_height(ws, row_idx, act_col, exp_col)

    print()
    print(f"  Matched : {matched} / {len(source_results)}")
    print(f"  PASS    : {verdicts.get('PASS', 0)}")
    print(f"  FAIL    : {verdicts.get('FAIL', 0)}")
    print(f"  N/A : {verdicts.get('N/A', 0)}")
    if not_found:
        print(f"  Unmatched ({len(not_found)}): {not_found[:8]}"
              + (" ..." if len(not_found) > 8 else ""))

    # --- Auto-fix: if nothing matched, scan for the real header row ---
    if matched == 0 and auto_fix and len(source_results) > 0:
        print("\n[auto-fix] matched = 0 — scanning worksheet for correct header row ...")
        new_header, new_data_start, new_col_map = auto_detect_structure(ws, structure)

        changed = (
            new_header != header_row
            or new_data_start != data_start_row
            or new_col_map.get("testCaseName") != col_map.get("testCaseName")
        )

        if not changed:
            print("[auto-fix] No better mapping found — check that API Name values match testCaseName column.")
        else:
            # Report what changed
            if new_header != header_row:
                print(f"[auto-fix] headerRow: {header_row} → {new_header}")
            if new_data_start != data_start_row:
                print(f"[auto-fix] dataStartRow: {data_start_row} → {new_data_start}")
            for field in ("testCaseName", "expectedResults", "actualResult", "status", "externalId"):
                old_c = col_map.get(field)
                new_c = new_col_map.get(field)
                if old_c != new_c:
                    print(f"[auto-fix] {field}: col {old_c} → {new_c}")

            # Re-run the merge loop with corrected values
            header_row     = new_header
            data_start_row = new_data_start
            col_map        = new_col_map
            tc_col  = col_map.get("testCaseName")
            exp_col = col_map.get("expectedResults")
            act_col = col_map.get("actualResult")
            sts_col = col_map.get("status")

            matched   = 0
            not_found = []
            verdicts  = {"PASS": 0, "FAIL": 0, "N/A": 0}

            print(f"\n[auto-fix] Re-merging (rows {data_start_row}+) ...")
            for row_idx in range(data_start_row, ws.max_row + 1):
                tc_cell = ws.cell(row=row_idx, column=tc_col + 1)
                if tc_cell.value is None:
                    continue
                tc_name = str(tc_cell.value).strip()
                if not tc_name:
                    continue

                if tc_name not in source_results:
                    not_found.append(tc_name)
                    continue

                matched += 1
                data = source_results[tc_name]

                expected_text = ""
                if exp_col is not None:
                    exp_cell = ws.cell(row=row_idx, column=exp_col + 1)
                    expected_text = str(exp_cell.value or "")

                raw_actual = f"Status: {data['status_code']}\nResponse:\n{data['response_body']}"

                if no_ai:
                    verdict, reason = evaluate_simple(expected_text, raw_actual)
                else:
                    verdict, reason = evaluate_ai(expected_text, raw_actual, api_key)

                verdicts[verdict] = verdicts.get(verdict, 0) + 1
                print(f"  [{verdict:7s}] {tc_name[:65]}")

                ext_id_col = col_map.get("externalId")
                if ext_id_col is not None:
                    ext_id_val = ws.cell(row=row_idx, column=ext_id_col + 1).value
                    if ext_id_val:
                        data["externalId"] = str(ext_id_val).strip()

                if dry_run:
                    continue

                if act_col is not None:
                    cell = ws.cell(row=row_idx, column=act_col + 1)
                    cell.value = raw_actual
                    cell.alignment = _wrap_align()

                # Write verdict to "Kết quả hiện tại" (status) column
                if sts_col is not None:
                    cell = ws.cell(row=row_idx, column=sts_col + 1)
                    cell.value = verdict
                    cell.alignment = _wrap_align()

                if exp_col is not None and data["response_body"]:
                    updated_expected = replace_json_in_expected(expected_text, data["response_body"])
                    cell = ws.cell(row=row_idx, column=exp_col + 1)
                    cell.value = updated_expected
                    cell.alignment = _wrap_align()

                _autofit_row_height(ws, row_idx, act_col, exp_col)

            print()
            print(f"  [auto-fix] Matched : {matched} / {len(source_results)}")
            print(f"  PASS    : {verdicts.get('PASS', 0)}")
            print(f"  FAIL    : {verdicts.get('FAIL', 0)}")
            print(f"  N/A : {verdicts.get('N/A', 0)}")
            if not_found:
                print(f"  Unmatched ({len(not_found)}): {not_found[:8]}"
                      + (" ..." if len(not_found) > 8 else ""))

    if not dry_run:
        # Update Evidence sheet
        print("\nUpdating Evidence sheet ...")
        update_evidence_sheet(wb, source_results)

        out_path = output_path or target_path
        wb.save(out_path)
        print(f"Saved → {out_path}")

        # Verify output
        print("\n[Verify] Re-reading saved file ...")
        verify = _verify_output(out_path, structure, col_map, data_start_row, matched)
        _print_verify(verify)
    else:
        print("\n[dry-run] No changes written.")
        out_path = None

    return {
        "matched": matched,
        "total_source": len(source_results),
        "verdicts": verdicts,
        "not_found": not_found,
        "output": out_path,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Merge auto-postman results into test case Excel file"
    )
    parser.add_argument("--source",    required=True, help="Path to api_results_*.xlsx")
    parser.add_argument("--target",    required=True, help="Path to test case xlsx")
    parser.add_argument("--structure", required=True, help="Path to structure.json")
    parser.add_argument("--output",    help="Output path (default: overwrite target)")
    parser.add_argument("--api-key",   help="Anthropic API key (or ANTHROPIC_API_KEY env var)")
    parser.add_argument("--no-ai",     action="store_true", help="Skip AI evaluation")
    parser.add_argument("--dry-run",   action="store_true",
                        help="Print what would happen without writing anything")
    args = parser.parse_args()

    try:
        result = merge_results(
            source_path=args.source,
            target_path=args.target,
            structure_path=args.structure,
            output_path=args.output,
            api_key=args.api_key,
            no_ai=args.no_ai,
            dry_run=args.dry_run,
        )
        print()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"\n[error] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
