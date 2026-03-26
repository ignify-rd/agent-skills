#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
google_sheet_input.py - Shared Google Sheet URL reader for Postman skill scripts.
"""

import importlib
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse


def is_google_sheet_url(value: str) -> bool:
    return bool(re.search(r"https?://docs\.google\.com/spreadsheets/d/", value or "", flags=re.IGNORECASE))


def extract_spreadsheet_id(value: str) -> Optional[str]:
    if not value:
        return None

    text = value.strip()
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9\-_]+)", text)
    if match:
        return match.group(1)

    # Also support passing bare spreadsheet id
    if re.fullmatch(r"[a-zA-Z0-9\-_]{20,}", text):
        return text

    return None


def extract_gid(value: str) -> Optional[int]:
    if not value:
        return None
    try:
        parsed = urlparse(value)
        qs = parse_qs(parsed.query)
        gid_values = qs.get("gid") or []
        if not gid_values:
            return None
        return int(gid_values[0])
    except Exception:
        return None


def _resolve_google_auth_module():
    """
    Resolve shared google_auth.py from available sibling skills.
    """
    script_dir = Path(__file__).resolve().parent
    skill_root = script_dir.parent
    skills_base = skill_root.parent

    candidates = [
        script_dir,  # local first if one is provided later
        skills_base / "generate-test-case-api" / "scripts",
        skills_base / "generate-test-case-frontend" / "scripts",
    ]

    for candidate in candidates:
        module_path = candidate / "google_auth.py"
        if module_path.exists():
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            return importlib.import_module("google_auth")

    raise RuntimeError(
        "Cannot find google_auth.py. Install generate-test-case-api skill or place google_auth.py in this scripts directory."
    )


def _score_row_as_header(row: List[str], known_labels: List[str]) -> int:
    if not row:
        return 0

    score = 0
    non_empty = 0
    known = {x.strip().lower() for x in known_labels if str(x).strip()}

    for cell in row:
        text = str(cell).strip().lower()
        if not text:
            continue
        non_empty += 1
        score += 1
        if text in known:
            score += 3

    if non_empty:
        matched = sum(1 for cell in row if str(cell).strip().lower() in known)
        score += int((matched / non_empty) * 10)
    return score


def detect_header_row(
    rows: List[List[str]],
    known_labels: Optional[List[str]] = None,
    max_scan_rows: int = 30
) -> Tuple[int, int]:
    if not rows:
        return 1, 2

    labels = known_labels or []
    best_score = -1
    best_idx = 0
    for idx, row in enumerate(rows[:max_scan_rows]):
        score = _score_row_as_header(row, labels)
        if score > best_score:
            best_score = score
            best_idx = idx

    header_row = best_idx + 1
    data_start_row = header_row + 1
    return header_row, data_start_row


def _pick_sheet(properties: List[Dict[str, Any]], sheet_name: str, sheet_gid: Optional[int]) -> Tuple[str, int]:
    if not properties:
        raise RuntimeError("No sheets found in spreadsheet.")

    if sheet_name:
        for item in properties:
            if str(item.get("title", "")).strip() == sheet_name.strip():
                return str(item["title"]), int(item["sheetId"])
        raise RuntimeError(f"Sheet name not found: {sheet_name}")

    if sheet_gid is not None:
        for item in properties:
            if int(item.get("sheetId", -1)) == int(sheet_gid):
                return str(item["title"]), int(item["sheetId"])
        raise RuntimeError(f"Sheet gid not found: {sheet_gid}")

    first = properties[0]
    return str(first["title"]), int(first["sheetId"])


def read_google_sheet_rows(
    sheet_url_or_id: str,
    sheet_name: str = "",
    sheet_gid: Optional[int] = None,
    credentials_path: str = "",
    header_row: Optional[int] = None,
    data_start_row: Optional[int] = None,
    known_labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    spreadsheet_id = extract_spreadsheet_id(sheet_url_or_id)
    if not spreadsheet_id:
        raise RuntimeError("Invalid Google Sheet URL or spreadsheet id.")

    if sheet_gid is None:
        sheet_gid = extract_gid(sheet_url_or_id)

    google_auth = _resolve_google_auth_module()
    creds_path = google_auth.find_credentials(credentials_path or None)
    _, sheets_service = google_auth.build_services(creds_path)

    metadata = sheets_service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="sheets.properties(sheetId,title)"
    ).execute()
    sheet_props = [x.get("properties", {}) for x in metadata.get("sheets", [])]
    chosen_name, chosen_gid = _pick_sheet(sheet_props, sheet_name=sheet_name, sheet_gid=sheet_gid)

    # Read full used range from the sheet.
    range_str = f"'{chosen_name}'"
    values_response = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_str,
        valueRenderOption="FORMATTED_VALUE"
    ).execute()
    values = values_response.get("values", [])

    if not values:
        return {
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": chosen_name,
            "sheet_gid": chosen_gid,
            "header_row": 1,
            "data_start_row": 2,
            "headers": [],
            "rows": [],
        }

    if header_row is None:
        header_row, auto_data_start = detect_header_row(values, known_labels=known_labels)
        if data_start_row is None:
            data_start_row = auto_data_start
    if data_start_row is None:
        data_start_row = header_row + 1

    header_idx = max(1, int(header_row)) - 1
    data_idx = max(1, int(data_start_row)) - 1

    if header_idx >= len(values):
        raise RuntimeError(f"header_row out of range: {header_row}")

    raw_headers = [str(x).strip() for x in values[header_idx]]
    headers: List[str] = []
    seen: Dict[str, int] = {}
    for idx, header in enumerate(raw_headers):
        base = header or f"column_{idx + 1}"
        count = seen.get(base, 0) + 1
        seen[base] = count
        headers.append(base if count == 1 else f"{base}_{count}")

    rows: List[Dict[str, Any]] = []
    for row in values[data_idx:]:
        padded = row + [""] * (len(headers) - len(row))
        row_dict = {headers[i]: padded[i] if i < len(padded) else "" for i in range(len(headers))}
        if any(str(v).strip() for v in row_dict.values()):
            rows.append(row_dict)

    return {
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": chosen_name,
        "sheet_gid": chosen_gid,
        "header_row": int(header_row),
        "data_start_row": int(data_start_row),
        "headers": headers,
        "rows": rows,
    }
