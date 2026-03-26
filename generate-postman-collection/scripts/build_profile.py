#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_profile.py - Build a project profile JSON for Postman generation.

Usage:
  python build_profile.py --input sample.csv --output data/profiles/my-project.json
  python build_profile.py --input sample.json --output data/profiles/my-project.json
  python build_profile.py --sheet-url "https://docs.google.com/spreadsheets/d/.../edit#gid=0" --output data/profiles/my-project.json
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from google_sheet_input import is_google_sheet_url, read_google_sheet_rows

DEFAULT_ALIASES: Dict[str, List[str]] = {
    "id": ["ID", "Test Case ID", "Case ID", "External ID"],
    "name": ["Name", "Test Case Name", "Title", "Test Name"],
    "method": ["Method", "HTTP Method", "Verb"],
    "endpoint": ["Endpoint", "Path", "URL", "API"],
    "headers": ["Headers", "Header", "Request Headers"],
    "body": ["Body", "Request Body", "Payload"],
    "auth_type": ["Auth Type", "Auth", "Authentication Type"],
    "auth_token": ["Auth Token", "Token", "Access Token"],
    "expected_status": ["Expected Status", "Status Code", "Expected Code"],
    "description": ["Description", "Details", "Summary"],
    "preconditions": ["PreConditions", "Pre-conditions", "Preconditions"],
    "query_params": ["Params", "Query", "Query Params", "QueryParameters"],
    "curl": ["cURL", "Curl", "Raw Request", "Request CURL", "Request"],
    "prerequest_script": ["Pre-request Script", "Pre Script", "Prerequest"],
    "test_script": ["Test Script", "Post Script", "Tests"],
    "response_assertions": ["Response Assertions", "Assertions"]
}

DEFAULT_PROFILE = {
    "defaults": {
        "auth_type": "bearer",
        "auth_token": "{{globalToken}}",
        "expected_status": 200,
        "base_url_variable": "{{serviceUrl}}"
    },
    "regex_extractors": [
        {
            "target": "method",
            "sources": ["Step", "Action", "Description", "Details"],
            "pattern": r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b",
            "group": 1
        },
        {
            "target": "endpoint",
            "sources": ["Step", "Action", "Description", "Details"],
            "pattern": r"(\/[-A-Za-z0-9_{}\/.]*)",
            "group": 1
        }
    ],
    "default_headers": {
        "Content-Type": "application/json"
    },
    "row_filters": {
        "allow_root_endpoint": False,
        "allow_non_ascii_endpoint": False,
        "skip_if_no_method_and_endpoint": True,
        "skip_if_sparse_row": True,
        "sparse_non_empty_threshold": 2,
        "suite_header_keywords": [
            "test suite",
            "suite",
            "section",
            "kiểm tra",
            "man hinh test",
            "màn hình test",
            "link pttk",
            "link rsd",
            "link jira",
            "link jra"
        ]
    },
    "bootstrap": {
        "enabled": True,
        "sample_size": 8
    },
    "query_parsing": {
        "from_step_when_get": True,
        "require_params_marker": True
    }
}


def normalize(text: str) -> str:
    return "".join(ch.lower() for ch in str(text) if ch.isalnum())


def read_headers_from_csv(path: Path) -> List[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or [])


def read_headers_from_json(path: Path) -> List[str]:
    data = json.loads(path.read_text(encoding="utf-8"))

    rows: List[Dict[str, Any]] = []
    if isinstance(data, list):
        rows = [x for x in data if isinstance(x, dict)]
    elif isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                rows = [x for x in value if isinstance(x, dict)]
                break
        if not rows:
            rows = [data]

    if not rows:
        return []

    headers: List[str] = []
    seen = set()
    for row in rows[:50]:
        for key in row.keys():
            key_str = str(key)
            if key_str not in seen:
                seen.add(key_str)
                headers.append(key_str)
    return headers


def read_headers(path: Path) -> List[str]:
    ext = path.suffix.lower()
    if ext == ".csv":
        return read_headers_from_csv(path)
    if ext == ".json":
        return read_headers_from_json(path)
    raise ValueError(f"Unsupported input format: {ext}. Use .csv or .json")


def read_headers_from_google_sheet(
    sheet_url: str,
    sheet_name: str = "",
    sheet_gid: Optional[int] = None,
    credentials_path: str = "",
    header_row: Optional[int] = None,
    data_start_row: Optional[int] = None
) -> List[str]:
    info = read_google_sheet_rows(
        sheet_url_or_id=sheet_url,
        sheet_name=sheet_name,
        sheet_gid=sheet_gid,
        credentials_path=credentials_path,
        header_row=header_row,
        data_start_row=data_start_row,
        known_labels=[alias for aliases in DEFAULT_ALIASES.values() for alias in aliases]
    )
    return info.get("headers", [])


def unique_keep_order(items: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def match_headers(headers: List[str], aliases: List[str]) -> List[str]:
    norm_aliases = [normalize(x) for x in aliases]
    matched: List[str] = []

    for header in headers:
        hn = normalize(header)
        for alias_norm in norm_aliases:
            if not alias_norm:
                continue
            if hn == alias_norm or hn in alias_norm or alias_norm in hn:
                matched.append(header)
                break
    return matched


def build_alias_map(headers: List[str]) -> Dict[str, List[str]]:
    alias_map: Dict[str, List[str]] = {}
    for field, aliases in DEFAULT_ALIASES.items():
        detected = match_headers(headers, aliases)
        alias_map[field] = unique_keep_order([*detected, *aliases])
    return alias_map


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Postman profile JSON from sample template.")
    parser.add_argument("--input", default="", help="Sample input file (.csv or .json), or Google Sheet URL")
    parser.add_argument("--sheet-url", default="", help="Google Sheet URL (alternative to --input)")
    parser.add_argument("--sheet-name", default="", help="Google Sheet tab name (optional)")
    parser.add_argument("--sheet-gid", type=int, default=None, help="Google Sheet gid/tab id (optional)")
    parser.add_argument("--credentials", default="", help="Path to OAuth credentials.json (optional)")
    parser.add_argument("--header-row", type=int, default=None, help="Header row number (1-based)")
    parser.add_argument("--data-start-row", type=int, default=None, help="Data start row number (1-based)")
    parser.add_argument("--output", required=True, help="Output profile JSON path")
    parser.add_argument("--name", default="", help="Profile name (default: output filename stem)")
    args = parser.parse_args()

    sheet_url = args.sheet_url.strip()
    input_value = args.input.strip()
    output_path = Path(args.output).expanduser().resolve()

    use_google_sheet = bool(sheet_url) or is_google_sheet_url(input_value)
    if use_google_sheet:
        source = sheet_url or input_value
        headers = read_headers_from_google_sheet(
            sheet_url=source,
            sheet_name=args.sheet_name,
            sheet_gid=args.sheet_gid,
            credentials_path=args.credentials,
            header_row=args.header_row,
            data_start_row=args.data_start_row
        )
    else:
        if not input_value:
            raise RuntimeError("Provide --input <file> or --sheet-url <google-sheet-url>.")
        input_path = Path(input_value).expanduser().resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        headers = read_headers(input_path)

    if not headers:
        raise RuntimeError("Cannot detect columns from sample input.")

    profile_name = args.name.strip() or output_path.stem
    profile: Dict[str, Any] = {
        "name": profile_name,
        "aliases": build_alias_map(headers),
        "detected_columns": headers
    }
    profile.update(DEFAULT_PROFILE)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Profile created: {output_path}")
    print(f"Detected columns: {len(headers)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
