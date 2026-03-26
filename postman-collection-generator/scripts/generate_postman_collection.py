#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_postman_collection.py - Generate Postman Collection JSON from CSV/JSON.

Usage:
  python generate_postman_collection.py \
    --input test-cases.csv \
    --output out.postman_collection.json \
    --profile data/profiles/default.json \
    --collection-name "Project API"

  python generate_postman_collection.py \
    --sheet-url "https://docs.google.com/spreadsheets/d/.../edit#gid=0" \
    --output out.postman_collection.json \
    --profile data/profiles/default.json
"""

import argparse
import csv
import json
import logging
import re
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qsl, urlencode, urlparse

from google_sheet_input import is_google_sheet_url, read_google_sheet_rows

logger = logging.getLogger("postman-generator")

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}

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

DEFAULT_PROFILE: Dict[str, Any] = {
    "aliases": DEFAULT_ALIASES,
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


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def read_rows(input_path: Path) -> List[Dict[str, Any]]:
    ext = input_path.suffix.lower()
    if ext == ".csv":
        with input_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]

    if ext == ".json":
        data = json.loads(input_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    return [x for x in value if isinstance(x, dict)]
            return [data]
        return []

    raise ValueError(f"Unsupported input format: {ext}. Use .csv or .json")


def read_rows_from_google_sheet(
    sheet_url: str,
    profile: Dict[str, Any],
    sheet_name: str = "",
    sheet_gid: Optional[int] = None,
    credentials_path: str = "",
    header_row: Optional[int] = None,
    data_start_row: Optional[int] = None
) -> List[Dict[str, Any]]:
    aliases = profile.get("aliases", DEFAULT_ALIASES)
    known_labels: List[str] = []
    if isinstance(aliases, dict):
        for values in aliases.values():
            if isinstance(values, list):
                known_labels.extend(str(x) for x in values)

    info = read_google_sheet_rows(
        sheet_url_or_id=sheet_url,
        sheet_name=sheet_name,
        sheet_gid=sheet_gid,
        credentials_path=credentials_path,
        header_row=header_row,
        data_start_row=data_start_row,
        known_labels=known_labels
    )
    return info.get("rows", [])


def load_profile(profile_path: Optional[Path]) -> Dict[str, Any]:
    profile = DEFAULT_PROFILE
    if profile_path and profile_path.exists():
        loaded = json.loads(profile_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            profile = deep_merge(DEFAULT_PROFILE, loaded)
    return profile


def row_casefold_lookup(row: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for key in row.keys():
        out[normalize(str(key))] = str(key)
    return out


def get_row_value(row: Dict[str, Any], aliases: List[str]) -> Any:
    if not aliases:
        return None
    lookup = row_casefold_lookup(row)
    for alias in aliases:
        key = lookup.get(normalize(alias))
        if key is not None:
            return row.get(key)
    return None


def get_source_value(row: Dict[str, Any], source: str) -> Any:
    lookup = row_casefold_lookup(row)
    key = lookup.get(normalize(source))
    if key is not None:
        return row.get(key)
    return None


def parse_json_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    return None


def parse_headers(value: Any) -> Dict[str, str]:
    parsed = parse_json_value(value)
    if isinstance(parsed, dict):
        return {str(k): str(v) for k, v in parsed.items()}
    if isinstance(parsed, list):
        out: Dict[str, str] = {}
        for item in parsed:
            if isinstance(item, dict) and "key" in item and "value" in item:
                out[str(item["key"])] = str(item["value"])
        return out

    if not isinstance(value, str):
        return {}

    out: Dict[str, str] = {}
    for part in re.split(r"[\n;]+", value):
        line = part.strip()
        if not line:
            continue
        if ":" in line:
            key, val = line.split(":", 1)
        elif "=" in line:
            key, val = line.split("=", 1)
        else:
            continue
        out[key.strip()] = val.strip()
    return out


def parse_body(value: Any) -> Any:
    parsed = parse_json_value(value)
    if parsed is not None:
        return parsed

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return {}
        return {"mode": "raw", "content": text}
    return {}


def parse_script_lines(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if str(x).strip()]
    if isinstance(value, str):
        return [line for line in value.splitlines() if line.strip()]
    return [str(value)]


def parse_expected_status(value: Any, fallback: int) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        m = re.search(r"\d{3}", value)
        if m:
            return int(m.group(0))
    return fallback


def parse_response_assertions(value: Any) -> List[Dict[str, Any]]:
    parsed = parse_json_value(value)
    if isinstance(parsed, list):
        return [x for x in parsed if isinstance(x, dict)]
    return []


def extract_json_block(text: str, keyword: str) -> Optional[str]:
    if not text:
        return None
    lower_text = text.lower()
    key_idx = lower_text.find(keyword.lower())
    if key_idx < 0:
        return None

    brace_start = text.find("{", key_idx)
    if brace_start < 0:
        return None

    depth = 0
    in_string = False
    escape = False
    for idx in range(brace_start, len(text)):
        ch = text[idx]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[brace_start: idx + 1]
    return None


def safe_json_loads(text: str) -> Optional[Any]:
    cleaned = str(text or "").strip()
    if not cleaned:
        return None
    cleaned = cleaned.replace("\r", "")
    try:
        return json.loads(cleaned)
    except Exception:
        # Repair common malformed snippets from spreadsheets, e.g. `"id": ,`
        repaired = re.sub(r":\s*,", ": null,", cleaned)
        repaired = re.sub(r":\s*}", ": null}", repaired)
        try:
            return json.loads(repaired)
        except Exception:
            return None


def parse_preconditions_context(preconditions_text: str) -> Dict[str, Any]:
    context: Dict[str, Any] = {"method": "", "endpoint": "", "headers": {}, "body": {}}
    if not preconditions_text:
        return context

    endpoint_match = re.search(
        r"Endpoint\s*:\s*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+([^\s]+)",
        preconditions_text,
        flags=re.IGNORECASE
    )
    if endpoint_match:
        context["method"] = endpoint_match.group(1).upper()
        endpoint_raw = endpoint_match.group(2).strip()
        endpoint_raw = re.sub(r"\{\{BASE_URL\}\}|\{BASE_URL\}", "", endpoint_raw, flags=re.IGNORECASE)
        context["endpoint"] = endpoint_raw if endpoint_raw.startswith("/") else f"/{endpoint_raw}"

    headers_block = extract_json_block(preconditions_text, "header")
    headers_obj = safe_json_loads(headers_block) if headers_block else None
    if isinstance(headers_obj, dict):
        context["headers"] = {str(k): str(v) for k, v in headers_obj.items()}

    body_block = extract_json_block(preconditions_text, "body")
    body_obj = safe_json_loads(body_block) if body_block else None
    if isinstance(body_obj, (dict, list)):
        context["body"] = body_obj

    return context


def parse_loose_scalar(text: str) -> Any:
    raw = str(text or "").strip().rstrip(",")
    if not raw:
        return ""

    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return raw[1:-1]

    lowered = raw.lower()
    if lowered == "null":
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False

    if re.fullmatch(r"-?\d+", raw):
        # Keep numbers with leading zero as string to preserve intent (e.g. 00123)
        if raw.lstrip("-").startswith("0") and len(raw.lstrip("-")) > 1:
            return raw
        try:
            return int(raw)
        except Exception:
            return raw

    if re.fullmatch(r"-?\d+\.\d+", raw):
        try:
            return float(raw)
        except Exception:
            return raw

    parsed = safe_json_loads(raw)
    if parsed is not None:
        return parsed

    return raw


def apply_step_body_mutations(base_body: Any, step_text: str) -> Any:
    if not step_text:
        return base_body

    text = str(step_text)
    assign_matches = list(re.finditer(r'"([A-Za-z0-9_]+)"\s*:\s*([^\n\r]+)', text))
    delete_matches = list(re.finditer(r'(?i)x[oó]a\s+"?([A-Za-z0-9_]+)"?', text))

    if not assign_matches and not delete_matches:
        return base_body

    if isinstance(base_body, dict):
        result = dict(base_body)
    else:
        result = {}

    for match in delete_matches:
        key = match.group(1)
        if key in result:
            result.pop(key, None)

    for match in assign_matches:
        key = match.group(1)
        value_raw = match.group(2).strip()
        result[key] = parse_loose_scalar(value_raw)

    return result


def parse_query_params(value: Any, require_marker: bool = False) -> Dict[str, str]:
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items() if str(k).strip()}
    if isinstance(value, list):
        out: Dict[str, str] = {}
        for item in value:
            if isinstance(item, dict) and "key" in item:
                out[str(item.get("key", "")).strip()] = str(item.get("value", ""))
        return {k: v for k, v in out.items() if k}
    if not isinstance(value, str):
        return {}

    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if not lines:
        return {}

    params: Dict[str, str] = {}
    marker_present = any("params" in line.lower() for line in lines[:3])
    if require_marker and not marker_present:
        return {}

    in_params_block = not require_marker

    for line in lines:
        lower = line.lower()
        if "params" in lower and len(line) <= 30:
            in_params_block = True
            continue

        if require_marker and not in_params_block:
            continue

        if re.match(r"^\d+\.\s*", line):
            # Usually "1. ...", "2. Send API"; stop parsing params on next numbered step.
            if in_params_block and "send api" in lower:
                break
            continue

        match = re.match(r"^([A-Za-z0-9_.\-\[\]]+)\s*:\s*(.+)$", line)
        if not match:
            continue

        key = match.group(1).strip()
        val = match.group(2).strip()
        if not key:
            continue
        params[key] = str(parse_loose_scalar(val))

    return params


def parse_curl_context(text: str) -> Dict[str, Any]:
    context: Dict[str, Any] = {"method": "", "endpoint": "", "headers": {}, "body": {}}
    if not text or "curl" not in text.lower():
        return context

    normalized = re.sub(r"\\\s*[\r\n]+", " ", str(text))
    normalized = normalized.replace("\r", " ").replace("\n", " ")

    method_match = re.search(r"(?:-X|--request)\s+([A-Za-z]+)", normalized, flags=re.IGNORECASE)
    if method_match:
        context["method"] = method_match.group(1).upper()

    url_match = re.search(r"(https?://[^\s\"']+|\{\{[^}]+\}\}[^\s\"']+|/[-A-Za-z0-9_{}\/.?=&%]+)", normalized)
    if url_match:
        endpoint_raw = url_match.group(1).strip()
        if endpoint_raw.startswith("http://") or endpoint_raw.startswith("https://"):
            context["endpoint"] = endpoint_raw
        else:
            endpoint_clean = re.sub(r"\{\{BASE_URL\}\}|\{BASE_URL\}", "", endpoint_raw, flags=re.IGNORECASE)
            context["endpoint"] = endpoint_clean if endpoint_clean.startswith("/") else f"/{endpoint_clean}"

    headers: Dict[str, str] = {}
    for header_match in re.finditer(r"(?:-H|--header)\s+(['\"])(.*?)\1", normalized):
        header_text = header_match.group(2).strip()
        if ":" in header_text:
            k, v = header_text.split(":", 1)
            headers[k.strip()] = v.strip()
    if headers:
        context["headers"] = headers

    body_match = re.search(r"(?:--data-raw|--data-binary|--data|-d)\s+(['\"])(.*?)\1", normalized, flags=re.IGNORECASE)
    if body_match:
        payload = body_match.group(2)
        parsed = safe_json_loads(payload)
        if isinstance(parsed, (dict, list)):
            context["body"] = parsed
        elif payload.strip():
            context["body"] = {"mode": "raw", "content": payload.strip()}

    return context


def merge_request_context(*contexts: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {"method": "", "endpoint": "", "headers": {}, "body": {}}
    for ctx in contexts:
        if not isinstance(ctx, dict):
            continue
        if not merged["method"] and ctx.get("method"):
            merged["method"] = str(ctx.get("method", "")).upper()
        if not merged["endpoint"] and ctx.get("endpoint"):
            merged["endpoint"] = str(ctx.get("endpoint", "")).strip()
        if not merged["headers"] and isinstance(ctx.get("headers"), dict) and ctx.get("headers"):
            merged["headers"] = dict(ctx.get("headers", {}))
        if not merged["body"] and ctx.get("body"):
            merged["body"] = ctx.get("body")
    return merged


def build_bootstrap_context(rows: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
    bootstrap_cfg = profile.get("bootstrap", {})
    if not bool(bootstrap_cfg.get("enabled", True)):
        return {"method": "", "endpoint": "", "headers": {}, "body": {}}

    sample_size = int(bootstrap_cfg.get("sample_size", 8))
    sample_rows = rows[: max(1, sample_size)]

    method_counter: Counter = Counter()
    endpoint_counter: Counter = Counter()
    headers_candidate: Dict[str, str] = {}
    body_candidate: Any = {}

    for row in sample_rows:
        pre_text = _pick_from_aliases(row, profile, "preconditions") or get_source_value(row, "PreConditions") or ""
        curl_text = (
            _pick_from_aliases(row, profile, "curl")
            or get_source_value(row, "Details")
            or get_source_value(row, "Description")
            or get_source_value(row, "Step")
            or ""
        )

        ctx = merge_request_context(parse_preconditions_context(str(pre_text)), parse_curl_context(str(curl_text)))

        method = str(ctx.get("method", "")).upper().strip()
        endpoint = str(ctx.get("endpoint", "")).strip()

        if method:
            method_counter[method] += 1
        if endpoint:
            endpoint_counter[endpoint] += 1
        if not headers_candidate and isinstance(ctx.get("headers"), dict) and ctx.get("headers"):
            headers_candidate = dict(ctx.get("headers", {}))
        if (not body_candidate) and ctx.get("body"):
            body_candidate = ctx.get("body")

    return {
        "method": method_counter.most_common(1)[0][0] if method_counter else "",
        "endpoint": endpoint_counter.most_common(1)[0][0] if endpoint_counter else "",
        "headers": headers_candidate or {},
        "body": body_candidate or {},
    }


def extract_regex_value(row: Dict[str, Any], extractor: Dict[str, Any]) -> Optional[str]:
    pattern = extractor.get("pattern")
    if not pattern:
        return None
    group = int(extractor.get("group", 1))
    sources = extractor.get("sources", [])
    if not isinstance(sources, list):
        return None

    for source in sources:
        source_value = get_source_value(row, str(source))
        if source_value is None:
            continue
        text = str(source_value)
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return match.group(group)
            except IndexError:
                return match.group(0)
    return None


def fallback_method(row: Dict[str, Any]) -> str:
    combined = " ".join(str(v) for v in row.values() if v is not None)
    match = re.search(r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b", combined, flags=re.IGNORECASE)
    return match.group(1).upper() if match else "GET"


def fallback_endpoint(row: Dict[str, Any]) -> str:
    combined = " ".join(str(v) for v in row.values() if v is not None)
    match = re.search(r"(https?://[^\s\"']+|/[-A-Za-z0-9_{}\/.]*\??[^\s\"']*)", combined)
    if match:
        return match.group(1)
    return ""


def _pick_from_aliases(row: Dict[str, Any], profile: Dict[str, Any], field: str) -> Any:
    aliases: Dict[str, List[str]] = profile.get("aliases", {})
    field_aliases = aliases.get(field, DEFAULT_ALIASES.get(field, []))
    return get_row_value(row, field_aliases)


def is_valid_endpoint(endpoint: str, allow_non_ascii_endpoint: bool = False) -> bool:
    if not endpoint:
        return False

    endpoint = endpoint.strip()
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        parsed = urlparse(endpoint)
        return bool(parsed.netloc)

    if not endpoint.startswith("/"):
        return False

    if allow_non_ascii_endpoint:
        return True

    pattern = r"^/[A-Za-z0-9\-._~/{}/]*([?][A-Za-z0-9\-._~%=&{}]*)?$"
    return bool(re.match(pattern, endpoint))


def looks_like_test_case_id(value: Any) -> bool:
    text = str(value or "").strip()
    return bool(re.match(r"^[A-Za-z]{2,20}[_-]?\d+$", text))


def extract_method_hint_from_row(row: Dict[str, Any]) -> Optional[str]:
    combined = " ".join(str(v) for v in row.values() if v is not None)
    match = re.search(r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b", combined, flags=re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def should_skip_row(row: Dict[str, Any], profile: Dict[str, Any]) -> Optional[str]:
    row_filters = profile.get("row_filters", {})
    endpoint_val = str(_pick_from_aliases(row, profile, "endpoint") or "").strip()
    method_val = str(_pick_from_aliases(row, profile, "method") or "").strip()
    name_val = str(_pick_from_aliases(row, profile, "name") or "").strip().lower()

    skip_no_method_endpoint = bool(row_filters.get("skip_if_no_method_and_endpoint", True))
    if skip_no_method_endpoint and not endpoint_val and not method_val:
        combined = " ".join(str(v) for v in row.values() if v is not None)
        has_method_hint = bool(
            re.search(r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b", combined, flags=re.IGNORECASE)
        )
        has_endpoint_hint = bool(
            re.search(r"(https?://[^\s\"']+|/[-A-Za-z0-9_{}\/.]+)", combined)
        )
        if not has_method_hint and not has_endpoint_hint:
            return "skip row without method and endpoint"

    skip_sparse = bool(row_filters.get("skip_if_sparse_row", True))
    sparse_threshold = int(row_filters.get("sparse_non_empty_threshold", 2))
    if skip_sparse:
        non_empty = sum(1 for value in row.values() if str(value).strip())
        if non_empty <= sparse_threshold and not endpoint_val:
            return f"skip sparse row (<= {sparse_threshold} non-empty cells)"

    keywords = [str(x).lower() for x in row_filters.get("suite_header_keywords", [])]
    if name_val and any(keyword in name_val for keyword in keywords) and not endpoint_val:
        return "skip suite/header row by keyword"

    return None


def build_test_case(
    row: Dict[str, Any],
    profile: Dict[str, Any],
    index: int,
    bootstrap_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    aliases: Dict[str, List[str]] = profile.get("aliases", {})
    defaults: Dict[str, Any] = profile.get("defaults", {})
    regex_extractors: List[Dict[str, Any]] = profile.get("regex_extractors", [])
    default_headers: Dict[str, Any] = profile.get("default_headers", {})

    def pick(field: str) -> Any:
        field_aliases = aliases.get(field, DEFAULT_ALIASES.get(field, []))
        return get_row_value(row, field_aliases)

    raw_id = pick("id")
    raw_name = pick("name")
    raw_method = pick("method")
    raw_endpoint = pick("endpoint")
    raw_headers = pick("headers")
    raw_body = pick("body")
    raw_auth_type = pick("auth_type")
    raw_auth_token = pick("auth_token")
    raw_expected_status = pick("expected_status")
    raw_description = pick("description")
    raw_preconditions = pick("preconditions") or get_source_value(row, "PreConditions")
    raw_query_params = pick("query_params")
    raw_pre_script = pick("prerequest_script")
    raw_test_script = pick("test_script")
    raw_assertions = pick("response_assertions")
    raw_step_text = get_source_value(row, "Step") or get_source_value(row, "Test steps") or ""

    extracted: Dict[str, Any] = {}
    for ex in regex_extractors:
        target = str(ex.get("target", "")).strip()
        if not target:
            continue
        extracted_value = extract_regex_value(row, ex)
        if extracted_value:
            extracted[target] = extracted_value

    preconditions_context = parse_preconditions_context(str(raw_preconditions or ""))
    curl_context = parse_curl_context(str(_pick_from_aliases(row, profile, "curl") or raw_step_text or ""))
    baseline_context = merge_request_context(preconditions_context, curl_context, bootstrap_context or {})

    method = str(raw_method or extracted.get("method") or baseline_context.get("method") or fallback_method(row)).upper()
    if method not in HTTP_METHODS:
        method = "GET"

    endpoint = str(
        raw_endpoint
        or extracted.get("endpoint")
        or baseline_context.get("endpoint")
        or fallback_endpoint(row)
    ).strip()
    if not endpoint:
        endpoint = "/"

    headers = parse_headers(raw_headers)
    if not headers and isinstance(baseline_context.get("headers"), dict):
        headers = baseline_context["headers"]
    merged_headers = {str(k): str(v) for k, v in default_headers.items()}
    merged_headers.update(headers)

    body = parse_body(raw_body)
    if not body and baseline_context.get("body"):
        body = baseline_context["body"]
    body = apply_step_body_mutations(body, str(raw_step_text or ""))
    expected_status = parse_expected_status(raw_expected_status, int(defaults.get("expected_status", 200)))
    query_params = parse_query_params(raw_query_params) if raw_query_params else {}
    query_cfg = profile.get("query_parsing", {})
    from_step_when_get = bool(query_cfg.get("from_step_when_get", True))
    require_marker = bool(query_cfg.get("require_params_marker", True))
    if not query_params and method == "GET" and from_step_when_get:
        query_params = parse_query_params(str(raw_step_text or ""), require_marker=require_marker)

    test_id = str(raw_id).strip() if raw_id is not None and str(raw_id).strip() else f"API_{index:03d}"
    test_name = str(raw_name).strip() if raw_name is not None and str(raw_name).strip() else test_id

    return {
        "id": test_id,
        "name": test_name,
        "method": method,
        "endpoint": endpoint,
        "headers": merged_headers,
        "body": body,
        "auth_type": str(raw_auth_type or defaults.get("auth_type", "bearer")).lower(),
        "auth_token": str(raw_auth_token or defaults.get("auth_token", "{{globalToken}}")),
        "expected_status": expected_status,
        "description": str(raw_description or ""),
        "query_params": query_params,
        "prerequest_script": parse_script_lines(raw_pre_script),
        "test_script": parse_script_lines(raw_test_script),
        "response_assertions": parse_response_assertions(raw_assertions)
    }


class PostmanCollectionGenerator:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.collection_id = str(uuid.uuid4())

    def generate_collection(
        self,
        test_cases: List[Dict[str, Any]],
        base_url_variable: str = "{{serviceUrl}}",
        include_collection_scripts: bool = True
    ) -> Dict[str, Any]:
        collection = {
            "info": {
                "_postman_id": self.collection_id,
                "name": self.collection_name,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                "_exporter_id": "agent-skills",
                "description": f"Generated by test-genie on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            },
            "item": [],
            "event": []
        }

        for test_case in test_cases:
            collection["item"].append(self._generate_item(test_case, base_url_variable))

        if include_collection_scripts:
            collection["event"] = self._generate_collection_events()

        return collection

    def _generate_item(self, test_case: Dict[str, Any], base_url_variable: str) -> Dict[str, Any]:
        return {
            "name": test_case.get("name", test_case.get("id", "Unnamed API")),
            "event": self._generate_events(
                prerequest_script=test_case.get("prerequest_script", []),
                test_script=test_case.get("test_script", []),
                expected_status=int(test_case.get("expected_status", 200)),
                response_assertions=test_case.get("response_assertions", [])
            ),
            "request": self._generate_request(test_case, base_url_variable),
            "response": []
        }

    def _generate_request(self, test_case: Dict[str, Any], base_url_variable: str) -> Dict[str, Any]:
        method = str(test_case.get("method", "GET")).upper()
        request = {
            "auth": self._generate_auth(
                str(test_case.get("auth_type", "bearer")),
                str(test_case.get("auth_token", "{{globalToken}}"))
            ),
            "method": method,
            "header": self._generate_headers(test_case.get("headers", {})),
            "url": self._generate_url(
                base_url_variable,
                str(test_case.get("endpoint", "/")),
                test_case.get("query_params", {})
            )
        }

        body = test_case.get("body", {})
        if method not in {"GET", "DELETE"} and body:
            request["body"] = self._generate_body(body)

        description = str(test_case.get("description", "")).strip()
        if description:
            request["description"] = description

        return request

    def _generate_auth(self, auth_type: str, auth_token: str) -> Dict[str, Any]:
        auth = auth_type.lower()
        if auth == "bearer":
            return {"type": "bearer", "bearer": [{"key": "token", "value": auth_token, "type": "string"}]}
        if auth == "basic":
            username, _, password = auth_token.partition(":")
            return {
                "type": "basic",
                "basic": [
                    {"key": "username", "value": username, "type": "string"},
                    {"key": "password", "value": password, "type": "string"}
                ]
            }
        if auth == "apikey":
            return {
                "type": "apikey",
                "apikey": [
                    {"key": "key", "value": "X-API-Key", "type": "string"},
                    {"key": "value", "value": auth_token, "type": "string"},
                    {"key": "in", "value": "header", "type": "string"}
                ]
            }
        return {"type": "noauth"}

    def _generate_headers(self, headers: Any) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        if isinstance(headers, dict):
            for key, value in headers.items():
                out.append({"key": str(key), "value": str(value), "type": "text"})
        elif isinstance(headers, list):
            for item in headers:
                if isinstance(item, dict):
                    out.append(
                        {
                            "key": str(item.get("key", "")),
                            "value": str(item.get("value", "")),
                            "type": str(item.get("type", "text"))
                        }
                    )
        return out

    def _generate_body(self, body: Any) -> Dict[str, Any]:
        if isinstance(body, dict) and "mode" in body and "raw" in body:
            return body

        if isinstance(body, dict) and body.get("mode") == "raw" and "content" in body:
            content = body.get("content", "")
            return {
                "mode": "raw",
                "raw": str(content),
                "options": {"raw": {"language": "json"}}
            }

        if isinstance(body, dict) and body.get("mode") == "formdata":
            return {"mode": "formdata", "formdata": body.get("formdata", [])}

        if isinstance(body, dict) and body.get("mode") == "urlencoded":
            return {"mode": "urlencoded", "urlencoded": body.get("urlencoded", [])}

        if isinstance(body, (dict, list)):
            raw = json.dumps(body, indent=2, ensure_ascii=False)
        else:
            raw = str(body)

        return {
            "mode": "raw",
            "raw": raw,
            "options": {"raw": {"language": "json"}}
        }

    def _generate_url(self, base_url: str, endpoint: str, query_params: Any = None) -> Dict[str, Any]:
        query_param_dict: Dict[str, str] = {}
        if isinstance(query_params, dict):
            query_param_dict = {str(k): str(v) for k, v in query_params.items() if str(k).strip()}

        endpoint = endpoint.strip()
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            parsed = urlparse(endpoint)
            path_segments = [seg for seg in parsed.path.split("/") if seg]
            query_map: Dict[str, str] = {k: v for k, v in parse_qsl(parsed.query, keep_blank_values=True)}
            query_map.update(query_param_dict)
            query = [{"key": k, "value": v} for k, v in query_map.items()]
            raw = endpoint.split("?", 1)[0]
            if query_map:
                raw = f"{raw}?{urlencode(query_map)}"
            url = {"raw": raw, "host": [parsed.netloc], "path": path_segments}
            if query:
                url["query"] = query
            return url

        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        parsed_endpoint = urlparse(endpoint)
        path_segments = [seg for seg in parsed_endpoint.path.split("/") if seg]
        query_map: Dict[str, str] = {k: v for k, v in parse_qsl(parsed_endpoint.query, keep_blank_values=True)}
        query_map.update(query_param_dict)
        query = [{"key": k, "value": v} for k, v in query_map.items()]

        if base_url.endswith("/") and parsed_endpoint.path.startswith("/"):
            raw = f"{base_url[:-1]}{parsed_endpoint.path}"
        elif not base_url.endswith("/") and not parsed_endpoint.path.startswith("/"):
            raw = f"{base_url}/{parsed_endpoint.path}"
        else:
            raw = f"{base_url}{parsed_endpoint.path}"
        if query_map:
            raw += f"?{urlencode(query_map)}"

        url = {"raw": raw, "host": [base_url], "path": path_segments}
        if query:
            url["query"] = query
        return url

    def _generate_events(
        self,
        prerequest_script: List[str],
        test_script: List[str],
        expected_status: int,
        response_assertions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []

        if prerequest_script:
            events.append(
                {
                    "listen": "prerequest",
                    "script": {
                        "exec": prerequest_script,
                        "type": "text/javascript",
                        "packages": {},
                        "requests": {}
                    }
                }
            )

        test_exec = list(test_script or [])
        test_exec.extend(
            [
                "",
                f"pm.test('Status code is {expected_status}', function () {{",
                f"    pm.response.to.have.status({expected_status});",
                "});"
            ]
        )

        for assertion in response_assertions:
            if not isinstance(assertion, dict):
                continue
            assertion_type = str(assertion.get("type", "property"))
            property_path = str(assertion.get("property", ""))
            expected_value = assertion.get("value")

            if assertion_type == "equals" and property_path:
                test_exec.extend(
                    [
                        "",
                        f"pm.test('Property {property_path} equals expected value', function () {{",
                        "    const response = pm.response.json();",
                        f"    pm.expect(response.{property_path}).to.eql({json.dumps(expected_value)});",
                        "});"
                    ]
                )
            elif assertion_type == "contains" and property_path:
                test_exec.extend(
                    [
                        "",
                        f"pm.test('Property {property_path} contains expected value', function () {{",
                        "    const response = pm.response.json();",
                        f"    pm.expect(String(response.{property_path})).to.include({json.dumps(str(expected_value))});",
                        "});"
                    ]
                )
            elif property_path:
                test_exec.extend(
                    [
                        "",
                        f"pm.test('Response has property {property_path}', function () {{",
                        "    const response = pm.response.json();",
                        f"    pm.expect(response).to.have.property('{property_path}');",
                        "});"
                    ]
                )

        events.append(
            {
                "listen": "test",
                "script": {
                    "exec": test_exec,
                    "type": "text/javascript",
                    "packages": {},
                    "requests": {}
                }
            }
        )
        return events

    def _generate_collection_events(self) -> List[Dict[str, Any]]:
        return [
            {
                "listen": "prerequest",
                "script": {
                    "type": "text/javascript",
                    "packages": {},
                    "requests": {},
                    "exec": [
                        "// Collection-level pre-request script",
                        "// Runs before each request in the collection"
                    ]
                }
            },
            {
                "listen": "test",
                "script": {
                    "type": "text/javascript",
                    "packages": {},
                    "requests": {},
                    "exec": [
                        "// Collection-level test script",
                        "// Runs after each request in the collection"
                    ]
                }
            }
        ]

    @staticmethod
    def save_collection(collection: Dict[str, Any], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(collection, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Postman collection from CSV/JSON input.")
    parser.add_argument("--input", default="", help="Input test cases file (.csv or .json), or Google Sheet URL")
    parser.add_argument("--sheet-url", default="", help="Google Sheet URL (alternative to --input)")
    parser.add_argument("--sheet-name", default="", help="Google Sheet tab name (optional)")
    parser.add_argument("--sheet-gid", type=int, default=None, help="Google Sheet gid/tab id (optional)")
    parser.add_argument("--credentials", default="", help="Path to OAuth credentials.json (optional)")
    parser.add_argument("--header-row", type=int, default=None, help="Header row number (1-based)")
    parser.add_argument("--data-start-row", type=int, default=None, help="Data start row number (1-based)")
    parser.add_argument("--output", required=True, help="Output .postman_collection.json")
    parser.add_argument("--profile", default="", help="Profile JSON path")
    parser.add_argument("--collection-name", default="API Test Collection", help="Postman collection name")
    parser.add_argument("--base-url-variable", default="", help="Override base URL variable, e.g. {{serviceUrl}}")
    parser.add_argument("--no-collection-scripts", action="store_true", help="Disable collection-level scripts")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    output_path = Path(args.output).expanduser().resolve()

    profile_path: Optional[Path] = None
    if args.profile:
        profile_path = Path(args.profile).expanduser().resolve()

    profile = load_profile(profile_path)
    defaults = profile.get("defaults", {})
    base_url_variable = args.base_url_variable.strip() or str(defaults.get("base_url_variable", "{{serviceUrl}}"))

    sheet_url = args.sheet_url.strip()
    input_value = args.input.strip()
    use_google_sheet = bool(sheet_url) or is_google_sheet_url(input_value)

    if use_google_sheet:
        source = sheet_url or input_value
        rows = read_rows_from_google_sheet(
            sheet_url=source,
            profile=profile,
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
        rows = read_rows(input_path)

    if not rows:
        raise RuntimeError("No rows found in input data.")

    bootstrap_context = build_bootstrap_context(rows, profile)

    kept_candidates: List[Dict[str, Any]] = []
    salvage_candidates: List[Dict[str, Any]] = []
    skipped: List[str] = []
    for idx, row in enumerate(rows, 1):
        try:
            pre_skip_reason = should_skip_row(row, profile)
            if pre_skip_reason:
                skipped.append(f"Row {idx}: {pre_skip_reason}")
                continue

            test_case = build_test_case(row, profile, idx, bootstrap_context=bootstrap_context)
            test_id_value = _pick_from_aliases(row, profile, "id")
            endpoint_value = str(test_case.get("endpoint", "")).strip()
            if not endpoint_value:
                if looks_like_test_case_id(test_id_value):
                    salvage_candidates.append(
                        {"idx": idx, "row": row, "test_case": test_case, "reason": "missing endpoint"}
                    )
                else:
                    skipped.append(f"Row {idx}: missing endpoint")
                continue

            allow_root_endpoint = bool(profile.get("row_filters", {}).get("allow_root_endpoint", False))
            if endpoint_value == "/" and not allow_root_endpoint:
                if looks_like_test_case_id(test_id_value):
                    salvage_candidates.append(
                        {"idx": idx, "row": row, "test_case": test_case, "reason": "root endpoint filtered"}
                    )
                else:
                    skipped.append(f"Row {idx}: root endpoint filtered")
                continue

            allow_non_ascii_endpoint = bool(profile.get("row_filters", {}).get("allow_non_ascii_endpoint", False))
            if not is_valid_endpoint(endpoint_value, allow_non_ascii_endpoint=allow_non_ascii_endpoint):
                if looks_like_test_case_id(test_id_value):
                    salvage_candidates.append(
                        {
                            "idx": idx,
                            "row": row,
                            "test_case": test_case,
                            "reason": f"invalid endpoint format ({endpoint_value})"
                        }
                    )
                else:
                    skipped.append(f"Row {idx}: invalid endpoint format ({endpoint_value})")
                continue
            kept_candidates.append({"idx": idx, "row": row, "test_case": test_case, "reason": ""})
        except Exception as exc:
            skipped.append(f"Row {idx}: {exc}")

    # Context recovery:
    # Some templates provide API endpoint once (or in section metadata) instead of every row.
    # For rows that look like real test cases (API_x) but endpoint parsing failed, reuse dominant endpoint.
    endpoint_counter = Counter(
        str(item["test_case"].get("endpoint", "")).strip()
        for item in kept_candidates
        if str(item["test_case"].get("endpoint", "")).strip()
    )
    dominant_endpoint = endpoint_counter.most_common(1)[0][0] if endpoint_counter else ""

    method_counter = Counter(
        str(item["test_case"].get("method", "")).strip().upper()
        for item in kept_candidates
        if str(item["test_case"].get("method", "")).strip()
    )
    dominant_method = method_counter.most_common(1)[0][0] if method_counter else "POST"

    for candidate in salvage_candidates:
        tc = candidate["test_case"]
        row = candidate["row"]
        idx = candidate["idx"]

        if dominant_endpoint:
            tc["endpoint"] = dominant_endpoint
        else:
            skipped.append(f"Row {idx}: {candidate['reason']}")
            continue

        # If this row has no explicit/implicit method hint, use dominant method.
        method_hint = extract_method_hint_from_row(row)
        if not method_hint and str(tc.get("method", "")).upper() == "GET":
            tc["method"] = dominant_method

        kept_candidates.append({"idx": idx, "row": row, "test_case": tc, "reason": "salvaged by context"})

    kept_candidates.sort(key=lambda item: int(item["idx"]))
    test_cases = [item["test_case"] for item in kept_candidates]
    salvaged_count = sum(1 for item in kept_candidates if item.get("reason") == "salvaged by context")

    if not test_cases:
        raise RuntimeError("No valid test cases after parsing input rows.")

    generator = PostmanCollectionGenerator(args.collection_name)
    collection = generator.generate_collection(
        test_cases=test_cases,
        base_url_variable=base_url_variable,
        include_collection_scripts=not args.no_collection_scripts
    )
    generator.save_collection(collection, output_path)

    logger.info("Generated collection: %s", output_path)
    logger.info("Items: %s | Skipped: %s | Salvaged: %s", len(test_cases), len(skipped), salvaged_count)
    if skipped:
        logger.warning("Skipped rows:\n- %s", "\n- ".join(skipped[:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
