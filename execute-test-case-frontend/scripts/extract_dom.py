#!/usr/bin/env python3
"""
extract_dom.py - Step 1 of execute-test-case-frontend skill.

Opens a URL using Playwright (headless), waits for networkidle,
extracts only form-relevant DOM elements (form, input, select, textarea, button)
with their key attributes, and writes cleaned JSON to output path.

Usage:
    python extract_dom.py <url> [--output <path>]

Default output: agent-workspace/raw-dom.json
"""

import argparse
import json
import os
import sys


EXTRACT_SCRIPT = """
() => {
    const RELEVANT_TAGS = ['form', 'input', 'select', 'textarea', 'button'];
    const RELEVANT_ATTRS = [
        'id', 'name', 'type', 'required', 'placeholder',
        'minlength', 'maxlength', 'pattern', 'aria-label',
        'data-testid', 'value', 'class', 'aria-required',
        'aria-invalid', 'autocomplete', 'for'
    ];

    function cleanAttrs(el) {
        const attrs = {};
        for (const attr of RELEVANT_ATTRS) {
            const val = el.getAttribute(attr);
            if (val !== null && val !== '') {
                attrs[attr] = val;
            }
        }
        return attrs;
    }

    function extractElement(el) {
        const tag = el.tagName.toLowerCase();
        const result = {
            tag: tag,
            attrs: cleanAttrs(el),
        };

        // For select, extract options
        if (tag === 'select') {
            result['options'] = Array.from(el.options).map(opt => ({
                value: opt.value,
                label: opt.text,
                selected: opt.defaultSelected
            }));
        }

        // For button, extract text
        if (tag === 'button') {
            result['text'] = el.innerText.trim().substring(0, 100);
        }

        // For input[type=radio] or input[type=checkbox], include checked state
        if (tag === 'input' && (el.type === 'radio' || el.type === 'checkbox')) {
            result['checked'] = el.defaultChecked;
        }

        return result;
    }

    function extractForm(formEl) {
        const formAttrs = cleanAttrs(formEl);
        const fields = [];

        // Get all relevant child elements
        const elements = formEl.querySelectorAll('input, select, textarea, button');
        for (const el of elements) {
            // Skip hidden inputs that are not useful
            if (el.tagName.toLowerCase() === 'input' && el.type === 'hidden') {
                continue;
            }
            fields.push(extractElement(el));
        }

        return {
            tag: 'form',
            attrs: formAttrs,
            fields: fields
        };
    }

    const result = {
        url: window.location.href,
        title: document.title,
        forms: []
    };

    const forms = document.querySelectorAll('form');
    if (forms.length > 0) {
        for (const form of forms) {
            result.forms.push(extractForm(form));
        }
    } else {
        // No <form> tag — look for standalone inputs (SPA forms without <form> element)
        const standaloneFields = [];
        const elements = document.querySelectorAll('input, select, textarea, button');
        for (const el of elements) {
            if (el.tagName.toLowerCase() === 'input' && el.type === 'hidden') {
                continue;
            }
            standaloneFields.push(extractElement(el));
        }

        if (standaloneFields.length > 0) {
            result.forms.push({
                tag: 'form',
                attrs: { 'data-note': 'no-form-tag-detected' },
                fields: standaloneFields
            });
        }
    }

    return result;
}
"""


def extract_dom(url: str, output_path: str) -> dict:
    """Extract DOM from URL using Playwright and save to JSON."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(1)

    print(f"[extract_dom] Opening URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (compatible; TestAgent/1.0)"
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"[extract_dom] Warning: networkidle timeout, proceeding anyway: {e}", file=sys.stderr)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
            except Exception as e2:
                print(f"ERROR: Cannot load URL: {e2}", file=sys.stderr)
                browser.close()
                sys.exit(1)

        print(f"[extract_dom] Page loaded: {page.title()}")

        try:
            dom_data = page.evaluate(EXTRACT_SCRIPT)
        except Exception as e:
            print(f"ERROR: DOM extraction failed: {e}", file=sys.stderr)
            browser.close()
            sys.exit(1)

        browser.close()

    # Count extracted fields
    total_fields = sum(len(f.get("fields", [])) for f in dom_data.get("forms", []))
    total_forms = len(dom_data.get("forms", []))
    print(f"[extract_dom] Extracted {total_forms} form(s), {total_fields} field(s)")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dom_data, f, ensure_ascii=False, indent=2)

    print(f"[extract_dom] Saved to: {output_path}")
    return dom_data


def main():
    parser = argparse.ArgumentParser(
        description="Extract form DOM from a URL for test automation"
    )
    parser.add_argument("url", help="URL to extract DOM from")
    parser.add_argument(
        "--output",
        default="agent-workspace/raw-dom.json",
        help="Output JSON file path (default: agent-workspace/raw-dom.json)"
    )

    args = parser.parse_args()

    result = extract_dom(args.url, args.output)

    if not result.get("forms"):
        print("WARNING: No forms or interactive elements found on the page.", file=sys.stderr)
        sys.exit(0)

    print(f"[extract_dom] Done. Forms: {len(result['forms'])}")


if __name__ == "__main__":
    main()
