#!/usr/bin/env python3
"""
assemble_batch.py — Convert intermediate validate-batch.json to final catalog format.

Reads the `_template` + `testCases` structure produced by expand_validate.py and
renders each case into the assembled format that matches batch-1.json (tc-common output):

  { testSuiteName, testCaseName, summary, preConditions, step, expectedResult,
    importance, result }

Usage:
  python assemble_batch.py \\
    --input   validate-batch.json \\
    --context tc-context.json \\
    --output  validate-assembled.json

Options:
  --input    PATH   validate-batch.json from expand_validate.py (required)
  --context  PATH   tc-context.json — used for fileContentField displayNames (optional)
  --output   PATH   output JSON array (required)
"""

import json
import sys
import os
import argparse
import io

# ── UTF-8 guard for Windows ──────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

_REMOVE = "__REMOVE__"


# ── I/O helpers ───────────────────────────────────────────────────────────────

def _load_json(path: str, label: str) -> dict | list:
    if not os.path.exists(path):
        print(f"Error: {label} not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: str, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Display name lookup ───────────────────────────────────────────────────────

def _build_display_map(ctx: dict) -> dict[str, str]:
    """
    Build {fieldName → displayName} from tc-context.json.
    Falls back to identity if key is missing.
    """
    display_map: dict[str, str] = {}
    fc_base = ctx.get("fileContentFieldsBase", {})
    for field_name, info in fc_base.items():
        if isinstance(info, dict):
            display_map[field_name] = info.get("displayName", field_name)
        else:
            display_map[field_name] = field_name
    return display_map


# ── Step renderer ─────────────────────────────────────────────────────────────

def _render_value(value) -> str:
    """Human-readable representation of a test value."""
    if value is None:
        return "(xem mô tả testcase)"
    if value == _REMOVE:
        return "(để trống)"
    if isinstance(value, str) and value.strip() == "" and len(value) > 0:
        return f'"{value}" (toàn space)'
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


def _render_step(template: dict, param_override: dict, display_map: dict[str, str]) -> str:
    """
    Build the Test Steps string from template + paramOverride.

    paramOverride shape (from expand_validate.py):
      { "fileContent": { "<field>": <value> } }   — file content field override
      { "requestBody": { "<field>": <value> } }   — request body field override

    For file-content overrides, the step is kept concise:
      - Only the overridden field is mentioned (not the entire file content schema)
      - Format: file: <file .xlsx hợp lệ, riêng trường "{displayName}": {value}>
    """
    step_prefix = template.get("stepPrefix", "")

    file_content_overrides = param_override.get("fileContent", {})
    request_body_overrides = param_override.get("requestBody", {})

    param_lines = []

    if file_content_overrides:
        # Concise: just say which field is being tested and what value
        for field, value in file_content_overrides.items():
            display = display_map.get(field, field)
            rendered = _render_value(value)
            param_lines.append(
                f"  - file: <file .xlsx hợp lệ, riêng trường \"{display}\": {rendered}>"
            )
    elif request_body_overrides:
        for field, value in request_body_overrides.items():
            display = display_map.get(field, field)
            rendered = _render_value(value)
            param_lines.append(f"  - {field}: {rendered}")
    else:
        param_lines.append("  - file: <file .xlsx hợp lệ>")

    # Add any non-file base params (e.g. description field in request body)
    base_params = template.get("baseParams", {})
    overridden_keys = set(file_content_overrides) | set(request_body_overrides)
    for k, v in base_params.items():
        if k not in overridden_keys and k != "file":
            param_lines.append(f"  - {k}: {_render_value(v)}")

    params_block = "\n".join(param_lines)
    return f"{step_prefix}{params_block}"


# ── Assembly ──────────────────────────────────────────────────────────────────

def assemble(batch: dict, display_map: dict[str, str]) -> list[dict]:
    """
    Convert validate-batch.json intermediate format → assembled catalog rows.
    """
    template = batch.get("_template", {})
    pre_conditions = template.get("preConditions", "")
    importance = template.get("importance", "Medium")
    result = template.get("result", "PENDING")

    assembled = []
    for case in batch.get("testCases", []):
        test_suite_name = case.get("testSuiteName", "")
        test_case_name = case.get("testCaseName", "")
        param_override = case.get("paramOverride", {})
        expected_result = case.get("expectedResult", "")

        step = _render_step(template, param_override, display_map)

        assembled.append({
            "testSuiteName": test_suite_name,
            "testCaseName": test_case_name,
            "summary": test_case_name,
            "preConditions": pre_conditions,
            "step": step,
            "expectedResult": expected_result,
            "importance": importance,
            "result": result,
        })

    return assembled


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Assemble validate-batch.json into final catalog format"
    )
    parser.add_argument("--input",   required=True,  help="validate-batch.json")
    parser.add_argument("--context", default=None,   help="tc-context.json (optional)")
    parser.add_argument("--output",  required=True,  help="Output assembled JSON array")
    args = parser.parse_args()

    batch = _load_json(args.input, "validate-batch.json")

    # Load display name map from tc-context.json if provided
    display_map: dict[str, str] = {}
    if args.context:
        ctx = _load_json(args.context, "tc-context.json")
        display_map = _build_display_map(ctx)
        print(f"Context: loaded {len(display_map)} field displayNames")

    if not isinstance(batch, dict) or "testCases" not in batch:
        print("Error: input must be validate-batch.json with _template + testCases",
              file=sys.stderr)
        sys.exit(1)

    total = len(batch["testCases"])
    print(f"Input: {total} cases from {args.input}")

    assembled = assemble(batch, display_map)

    # Summary
    suites: dict[str, int] = {}
    for row in assembled:
        s = row["testSuiteName"]
        suites[s] = suites.get(s, 0) + 1
    print(f"\nAssembled → {len(assembled)} cases across {len(suites)} suite(s)")
    for suite, cnt in sorted(suites.items()):
        print(f"  {suite}: {cnt} cases")

    _save_json(args.output, assembled)
    print(f"\n✓ Written: {args.output}")


if __name__ == "__main__":
    main()
