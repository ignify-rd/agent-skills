#!/usr/bin/env python3
"""
run_tests.py - Step 4 of execute-test-case-frontend skill.

Runs a Playwright test spec file using `npx playwright test` with JSON reporter,
parses the result, and returns a structured dict with pass/fail/error counts
and screenshot paths.

Usage:
    python run_tests.py <spec-file> [--output-dir <path>] [--config <playwright.config.ts>]

Exit codes:
    0 - all tests passed
    1 - some tests failed (results still written)
    2 - runner error (npx/playwright not available, parse failure)

Output JSON schema:
{
  "passed": 3,
  "failed": 1,
  "skipped": 0,
  "total": 4,
  "duration_ms": 12340,
  "errors": [
    {
      "test": "TC-002: invalid email",
      "file": "form-validate.spec.ts",
      "error": "Expected aria-invalid to be true",
      "location": "form-validate.spec.ts:45"
    }
  ],
  "screenshots": [
    "agent-workspace/test-results/screenshots/TC-001-failed.png"
  ],
  "raw_output": "..."
}
"""

import argparse
import json
import os
import subprocess
import sys


def find_screenshots(output_dir: str) -> list:
    """Find all screenshot files in the output directory."""
    screenshots = []
    screenshots_dir = os.path.join(output_dir, "screenshots")
    if os.path.isdir(screenshots_dir):
        for root, _dirs, files in os.walk(screenshots_dir):
            for fname in files:
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    screenshots.append(os.path.join(root, fname))
    return sorted(screenshots)


def parse_playwright_json(raw_json: str, output_dir: str) -> dict:
    """Parse Playwright JSON reporter output into structured result."""
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        return {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "duration_ms": 0,
            "errors": [{"test": "parse_error", "file": "", "error": f"JSON parse failed: {e}", "location": ""}],
            "screenshots": find_screenshots(output_dir),
            "raw_output": raw_json[:2000]
        }

    passed = 0
    failed = 0
    skipped = 0
    errors = []
    duration_ms = data.get("stats", {}).get("duration", 0)

    def process_suite(suite):
        nonlocal passed, failed, skipped
        for spec in suite.get("specs", []):
            for test in spec.get("tests", []):
                status = test.get("status", "unknown")
                results_list = test.get("results", [])

                if status == "expected" or (results_list and results_list[-1].get("status") == "passed"):
                    passed += 1
                elif status == "skipped":
                    skipped += 1
                else:
                    failed += 1
                    # Extract error message
                    error_msg = ""
                    location = ""
                    for result in results_list:
                        if result.get("status") in ("failed", "timedOut"):
                            errs = result.get("errors", [])
                            if errs:
                                error_msg = errs[0].get("message", "")
                                # Strip ANSI codes
                                import re
                                error_msg = re.sub(r'\x1b\[[0-9;]*m', '', error_msg).strip()
                                # Trim to 500 chars
                                if len(error_msg) > 500:
                                    error_msg = error_msg[:500] + "..."

                            # Get location from attachments or errors
                            for err in errs:
                                loc = err.get("location", {})
                                if loc:
                                    location = f"{loc.get('file', '')}:{loc.get('line', '')}"

                    errors.append({
                        "test": spec.get("title", ""),
                        "file": spec.get("file", ""),
                        "error": error_msg,
                        "location": location
                    })

        for child_suite in suite.get("suites", []):
            process_suite(child_suite)

    for suite in data.get("suites", []):
        process_suite(suite)

    total = passed + failed + skipped

    return {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "total": total,
        "duration_ms": int(duration_ms),
        "errors": errors,
        "screenshots": find_screenshots(output_dir),
        "raw_output": raw_json[:1000] if len(raw_json) > 1000 else raw_json
    }


def run_tests(spec_file: str, output_dir: str, config_path: str = None) -> dict:
    """Run Playwright tests and return structured results."""

    if not os.path.isfile(spec_file):
        return {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "duration_ms": 0,
            "errors": [{"test": "file_not_found", "file": spec_file, "error": f"Spec file not found: {spec_file}", "location": ""}],
            "screenshots": [],
            "raw_output": ""
        }

    os.makedirs(output_dir, exist_ok=True)
    results_json_path = os.path.join(output_dir, "results.json")

    cmd = ["npx", "playwright", "test", spec_file, "--reporter=json"]

    if config_path and os.path.isfile(config_path):
        cmd += ["--config", config_path]

    print(f"[run_tests] Running: {' '.join(cmd)}")

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
    except FileNotFoundError:
        return {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "duration_ms": 0,
            "errors": [{"test": "runner_error", "file": "", "error": "npx not found. Install Node.js >= 18.", "location": ""}],
            "screenshots": [],
            "raw_output": ""
        }
    except subprocess.TimeoutExpired:
        return {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "duration_ms": 120000,
            "errors": [{"test": "timeout", "file": spec_file, "error": "Test run exceeded 120 second timeout.", "location": ""}],
            "screenshots": find_screenshots(output_dir),
            "raw_output": ""
        }

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    print(f"[run_tests] Exit code: {proc.returncode}")
    if stderr:
        print(f"[run_tests] stderr:\n{stderr[:500]}", file=sys.stderr)

    # Playwright JSON reporter writes to stdout
    result = parse_playwright_json(stdout, output_dir)

    # Also save results.json
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[run_tests] Results: {result['passed']} passed, {result['failed']} failed, {result['skipped']} skipped")
    print(f"[run_tests] Saved to: {results_json_path}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run Playwright test spec and return structured JSON results"
    )
    parser.add_argument("spec_file", help="Path to the Playwright spec file (.spec.ts)")
    parser.add_argument(
        "--output-dir",
        default="agent-workspace/test-results",
        help="Directory for results.json and screenshots (default: agent-workspace/test-results)"
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to playwright.config.ts (optional)"
    )

    args = parser.parse_args()

    result = run_tests(args.spec_file, args.output_dir, args.config)

    # Print summary
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Exit with 0 if all passed, 1 if any failed, 2 if runner error
    if result["errors"] and result["errors"][0].get("test") in ("runner_error", "file_not_found", "timeout"):
        sys.exit(2)
    elif result["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
