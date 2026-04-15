#!/usr/bin/env python3
"""
generate_report.py - Step 6 of execute-test-case-frontend skill.

Reads test results JSON (output of run_tests.py) and generates a Markdown
report summarizing pass/fail counts, bug list, and screenshot paths.

Usage:
    python generate_report.py [--results <path>] [--output <path>] [--url <tested-url>]

Default:
    --results  agent-workspace/test-results/results.json
    --output   agent-workspace/test-results/report.md
"""

import argparse
import json
import os
import sys
from datetime import datetime


def generate_report(results_path: str, output_path: str, tested_url: str = "") -> str:
    """Read results JSON and generate a Markdown report."""

    if not os.path.isfile(results_path):
        print(f"ERROR: Results file not found: {results_path}", file=sys.stderr)
        sys.exit(1)

    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    passed = results.get("passed", 0)
    failed = results.get("failed", 0)
    skipped = results.get("skipped", 0)
    total = results.get("total", 0)
    duration_ms = results.get("duration_ms", 0)
    errors = results.get("errors", [])
    screenshots = results.get("screenshots", [])

    duration_s = duration_ms / 1000 if duration_ms else 0
    pass_rate = (passed / total * 100) if total > 0 else 0.0
    status_icon = "PASS" if failed == 0 else "FAIL"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []

    # Header
    lines.append(f"# Frontend Test Report")
    lines.append(f"")
    lines.append(f"**Status:** {status_icon}")
    lines.append(f"**Generated at:** {generated_at}")
    if tested_url:
        lines.append(f"**Tested URL:** {tested_url}")
    lines.append(f"")

    # Summary table
    lines.append(f"## Summary")
    lines.append(f"")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Tests | {total} |")
    lines.append(f"| Passed | {passed} |")
    lines.append(f"| Failed | {failed} |")
    lines.append(f"| Skipped | {skipped} |")
    lines.append(f"| Pass Rate | {pass_rate:.1f}% |")
    lines.append(f"| Duration | {duration_s:.2f}s |")
    lines.append(f"")

    # Failures / Bugs
    if errors:
        lines.append(f"## Bugs / Failures ({len(errors)})")
        lines.append(f"")
        lines.append(f"These test cases failed, indicating validation issues or broken functionality:")
        lines.append(f"")

        for i, err in enumerate(errors, start=1):
            test_name = err.get("test", "Unknown test")
            error_msg = err.get("error", "No error message")
            location = err.get("location", "")
            file_name = err.get("file", "")

            lines.append(f"### Bug {i}: {test_name}")
            lines.append(f"")
            lines.append(f"- **File:** `{file_name}`")
            if location:
                lines.append(f"- **Location:** `{location}`")
            lines.append(f"- **Error:**")
            lines.append(f"")
            lines.append(f"  ```")
            # Indent error message
            for eline in error_msg.split("\n")[:10]:
                lines.append(f"  {eline}")
            lines.append(f"  ```")
            lines.append(f"")
    else:
        lines.append(f"## Bugs / Failures")
        lines.append(f"")
        lines.append(f"No failures detected. All validation tests passed.")
        lines.append(f"")

    # Screenshots
    if screenshots:
        lines.append(f"## Screenshots ({len(screenshots)})")
        lines.append(f"")
        for shot in screenshots:
            # Use relative path if possible
            rel_path = os.path.relpath(shot) if os.path.isabs(shot) else shot
            fname = os.path.basename(shot)
            lines.append(f"- `{rel_path}` ({fname})")
        lines.append(f"")
    else:
        lines.append(f"## Screenshots")
        lines.append(f"")
        lines.append(f"No screenshots captured (all tests passed without failures).")
        lines.append(f"")

    # Recommendations
    lines.append(f"## Recommendations")
    lines.append(f"")
    if failed == 0:
        lines.append(f"- Form validation is working correctly for all tested scenarios.")
        lines.append(f"- Consider adding more edge case tests (e.g., Unicode input, very long strings).")
    else:
        lines.append(f"- **{failed} validation issue(s) detected.** Review the Bugs section above.")
        lines.append(f"- Prioritize fixing required field validation errors first.")
        lines.append(f"- Re-run tests after fixes: `python execute-test-case-frontend/scripts/run_tests.py agent-workspace/tests/form-validate.spec.ts`")

    report_content = "\n".join(lines)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[generate_report] Report written to: {output_path}")
    print(f"[generate_report] Summary: {passed}/{total} passed ({pass_rate:.1f}%), {failed} failed")

    return report_content


def main():
    parser = argparse.ArgumentParser(
        description="Generate Markdown test report from run_tests.py results"
    )
    parser.add_argument(
        "--results",
        default="agent-workspace/test-results/results.json",
        help="Path to results.json (default: agent-workspace/test-results/results.json)"
    )
    parser.add_argument(
        "--output",
        default="agent-workspace/test-results/report.md",
        help="Output path for report.md (default: agent-workspace/test-results/report.md)"
    )
    parser.add_argument(
        "--url",
        default="",
        help="URL that was tested (for report header)"
    )

    args = parser.parse_args()

    report = generate_report(args.results, args.output, args.url)

    # Print report to stdout as well
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)


if __name__ == "__main__":
    main()
