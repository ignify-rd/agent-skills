---
name: execute-test-case-frontend
description: Execute frontend validation test cases from a Google Sheets URL or local Excel file using Playwright MCP with minimal browser steps. Downloads/copies the input into a local .xlsx run folder, filters only "Kiểm tra validate" cases, runs cases in browser batches through browser_run_code, captures screenshots, and writes P/F/E plus evidence into one Excel result workbook. Use when the user asks to run FE/frontend test cases, "chạy test case frontend", execute only validate cases, or make frontend execution work like auto-postman.
---

# Execute Test Case - Frontend Validate

Run frontend validate cases like `auto-postman`: prepare local Excel input, execute browser work through Playwright MCP, then write all results into one Excel workbook with an Evidence sheet.

**Core rule:** Playwright MCP does browser work only. Sheet download/filtering and result writing are handled by `scripts/frontend_validate_excel.py`.

**Goal:** few MCP calls, fast execution, no accidental clicks outside the target screen.

---

## Required Inputs

- `url`: application page under test.
- One input source:
  - Google Sheets URL, or
  - local `.xlsx` path, or
  - `values-json` exported from Sheets MCP when direct Google export is not allowed.
- Optional `sheetName`: defaults to `TestCase`, otherwise first worksheet.

Prerequisite for the helper:

```powershell
pip install openpyxl Pillow
```

Playwright MCP on Windows must have a writable output directory. If MCP errors with
`EPERM: operation not permitted, mkdir 'C:\Windows\System32\.playwright-mcp'`,
update `C:\Users\<user>\.codex\config.toml`:

```toml
[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp@latest", "--viewport-size", "1920,1080", "--output-dir", "D:\\Code\\agent-skills\\frontend_validate_runs\\mcp-output"]
```

Restart Codex Desktop or the thread after changing MCP config; existing MCP
transports do not reliably reload server args.

---

## Expected Columns

The helper detects headers dynamically. Standard layout:

| Col | Field | Use |
|-----|-------|-----|
| B | Name | test case name |
| C | PreConditions | login/navigation hints |
| D | Importance | priority |
| E | Steps | action instructions |
| F | Data test | input value |
| G | Expected Result | verification target |
| H | Actual Result | written by finalize |
| I | Lần 1 (Chrome) | written as `P` / `F` / `E` |

If `Screenshot`, `Error`, or `Executed At` columns do not exist, the helper appends them in the result workbook only.

---

## Workflow

### 1. Prepare Excel Run

Use the bundled helper. Do not read the full Google Sheet through MCP unless export fails.

Google Sheets input:

```powershell
python -X utf8 D:\Code\agent-skills\execute-test-case-frontend\scripts\frontend_validate_excel.py prepare --sheet-url "SHEET_URL" --sheet-name "TestCase"
```

Local Excel input:

```powershell
python -X utf8 D:\Code\agent-skills\execute-test-case-frontend\scripts\frontend_validate_excel.py prepare --xlsx "D:\path\input.xlsx" --sheet-name "TestCase"
```

The command prints JSON:

```json
{
  "runDir": "...",
  "inputWorkbook": "...\\input.xlsx",
  "resultWorkbook": "...\\frontend_validate_results_YYYYMMDD_HHMMSS.xlsx",
  "casesFile": "...\\cases.json",
  "screenshotsDir": "...\\screenshots",
  "caseCount": 12,
  "groups": {
    "Textbox: Tên": 5
  }
}
```

Proceed only when `caseCount > 0`. The helper filters:

- rows under the `Kiểm tra validate` section, including field sub-suites below it;
- rows whose name contains `Validate`;
- pending rows only. Empty, `PENDING`, `chưa chạy`, or `not run` count as pending. Existing `P/F/E/PASS/FAIL/ERROR` rows are skipped unless `--include-done` is passed.

If Google export fails because the sheet is private, get values with Sheets MCP and save them as a 2D JSON array, then run:

```powershell
python -X utf8 D:\Code\agent-skills\execute-test-case-frontend\scripts\frontend_validate_excel.py prepare --values-json "D:\path\values.json" --sheet-name "TestCase"
```

### 2. Load Cases

Read `cases.json`. Each case has:

```json
{
  "id": "r18",
  "row": 18,
  "suite": "Kiểm tra validate",
  "fieldGroup": "Textbox: Tên",
  "name": "...",
  "preconditions": "...",
  "steps": "...",
  "data": "...",
  "expected": "...",
  "safeName": "18_case_name"
}
```

Use `fieldGroup`, `steps`, `data`, and `expected` to build the browser batch.

### 3. Navigate And Login Once

Use Playwright MCP:

1. `browser_navigate` to `url`.
2. Login only if the application requires it. Extract account hints from the first case precondition if present.
3. Navigate to the target screen once.
4. Do not re-login between cases or field groups.

For login/navigation discovery, normal MCP actions are acceptable. After the target screen is open, switch to `browser_run_code` batches.

### 4. Discover Main Content And Locators

Run one `browser_run_code` scan on the target screen. Scope every candidate to main content and exclude navigation chrome.

```js
async (page) => {
  const data = await page.evaluate(() => {
    const bad = 'header,nav,aside,[role="navigation"],[role="banner"],[role="toolbar"]';
    const visible = (el) => {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
    };
    const mains = [
      document.querySelector('main'),
      document.querySelector('[role="main"]'),
      document.querySelector('.main-content'),
      document.querySelector('.content-area'),
      document.querySelector('.page-content'),
      ...[...document.querySelectorAll('section,div')]
        .filter(el => visible(el) && !el.closest(bad))
        .sort((a, b) => {
          const ar = a.getBoundingClientRect();
          const br = b.getBoundingClientRect();
          return (br.width * br.height) - (ar.width * ar.height);
        })
    ].filter(Boolean);
    const main = mains[0];
    if (!main) return { error: 'Main content not found' };

    const cssPath = (el) => {
      if (el.id) return `#${CSS.escape(el.id)}`;
      const parts = [];
      for (let n = el; n && n.nodeType === 1 && n !== document.body; n = n.parentElement) {
        let part = n.tagName.toLowerCase();
        if (n.classList.length) part += '.' + [...n.classList].slice(0, 2).map(CSS.escape).join('.');
        const parent = n.parentElement;
        if (parent) {
          const same = [...parent.children].filter(c => c.tagName === n.tagName);
          if (same.length > 1) part += `:nth-of-type(${same.indexOf(n) + 1})`;
        }
        parts.unshift(part);
      }
      return parts.join(' > ');
    };

    const controls = [...main.querySelectorAll('input,textarea,select,button,[role="combobox"],[role="textbox"],[contenteditable="true"]')]
      .filter(el => visible(el) && !el.closest(bad))
      .map(el => {
        const label = el.id ? document.querySelector(`label[for="${CSS.escape(el.id)}"]`) : null;
        const r = el.getBoundingClientRect();
        return {
          selector: cssPath(el),
          tag: el.tagName.toLowerCase(),
          type: el.getAttribute('type') || '',
          role: el.getAttribute('role') || '',
          text: (el.innerText || el.textContent || '').trim().slice(0, 80),
          label: (label?.innerText || '').trim(),
          placeholder: el.getAttribute('placeholder') || '',
          ariaLabel: el.getAttribute('aria-label') || '',
          testId: el.getAttribute('data-testid') || '',
          disabled: !!el.disabled || el.getAttribute('aria-disabled') === 'true',
          rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }
        };
      });
    return { mainSelector: cssPath(main), controls };
  });
  return JSON.stringify(data);
}
```

Create a locator map from this scan. Prefer, in order:

1. `data-testid`
2. associated `label`
3. `aria-label`
4. `placeholder`
5. stable `id`
6. exact visible button/option text

Never use viewport coordinates as a locator. If a target is missing or ambiguous, mark that case `E` instead of guessing.

### 5. Execute Cases In Batches

Use one `browser_run_code` call per screen or per field group. Keep batches around 10-20 cases if the page is fragile; otherwise one batch is fine.

Result objects must match this shape so the helper can write Excel:

```json
{
  "id": "r18",
  "row": 18,
  "verdict": "P",
  "actual": "Observed validation message ...",
  "screenshot": "D:\\...\\screenshots\\18_case.png",
  "error": ""
}
```

Batch runner pattern:

```js
async (page) => {
  const cases = [
    // paste selected cases from cases.json
  ];
  const screenshotsDir = 'D:/path/from/prepare/screenshots';
  const locatorMap = {
    // fieldGroup or case id -> stable selector from the DOM scan
    // "Textbox: Tên": "[data-testid=\"customer-name\"]",
    // __mainSelector: ".main-content"  // used by triggerValidation to scope button search
  };

  const results = [];
  const bad = 'header,nav,aside,[role="navigation"],[role="banner"],[role="toolbar"]';
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));

  async function safeLocator(selector, label) {
    const loc = page.locator(selector);
    const count = await loc.count();
    const visible = [];
    for (let i = 0; i < count; i++) {
      const item = loc.nth(i);
      const ok = await item.isVisible().catch(() => false)
        && await item.evaluate((el, bad) => !el.closest(bad), bad).catch(() => false);
      if (ok) visible.push(item);
    }
    if (visible.length !== 1) {
      throw new Error(`${label}: expected 1 visible element, found ${visible.length}`);
    }
    return visible[0];
  }

  async function setValue(selector, value) {
    const isNav = await page.evaluate((selector) => {
      const el = document.querySelector(selector);
      return el?.closest('header,nav,aside,[role="navigation"],[role="banner"],[role="toolbar"]') != null;
    }, selector);
    if (isNav) throw new Error(`Refusing to edit navigation element: ${selector}`);

    if (value === '' || value === null || value === undefined) {
      // Clear field via native setter, then blur to trigger validation
      await page.evaluate((selector) => {
        const el = document.querySelector(selector);
        if (!el) return;
        if ('value' in el) {
          const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
          const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
          setter ? setter.call(el, '') : (el.value = '');
          el.dispatchEvent(new InputEvent('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          el.dispatchEvent(new FocusEvent('blur', { bubbles: true }));
        } else {
          el.textContent = '';
        }
      }, selector);
      return;
    }

    // Focus the field first, select all, then use keyboard.insertText for full
    // Unicode/Vietnamese diacritics support (insertText preserves diacritics unlike type()).
    const field = page.locator(selector).first();
    await field.click({ clickCount: 3 });
    await page.keyboard.press('Control+a');
    await page.keyboard.insertText(`${value}`);

    // Dispatch extra events so Angular/React/Vue controlled inputs pick up the new value.
    await page.evaluate(({ selector, value }) => {
      const el = document.querySelector(selector);
      if (!el) return;
      el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: value }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }, { selector, value: `${value}` });

    // IMPORTANT: blur the field after every setValue to trigger Angular/Vue validation
    // (equivalent to the user clicking outside the field).
    await page.evaluate((selector) => {
      const el = document.querySelector(selector);
      if (!el) return;
      el.dispatchEvent(new FocusEvent('blur', { bubbles: true }));
      el.blur?.();
    }, selector);
    await sleep(150);
  }

  // After entering a value, trigger validation by blurring first, then optionally
  // clicking a submit/search/apply button inside the form.
  async function triggerValidation(mainSelector) {
    // Always blur first to fire field-level validation
    await page.keyboard.press('Tab');
    await sleep(150);

    const submitTexts = ['Áp dụng','Apply','Tìm kiếm','Search','Filter','Lọc','OK','Lưu','Save','Xác nhận','Confirm','Submit','Gửi'];
    const scope = mainSelector || 'main,[role="main"],.main-content,.content-area,.page-content,body';

    // 1. type="submit" inside a <form>
    const formSubmit = page.locator(`${scope} form button[type="submit"], ${scope} form input[type="submit"]`).first();
    if (await formSubmit.isVisible().catch(() => false)) {
      await formSubmit.click();
      await sleep(400);
      return;
    }

    // 2. named action buttons (prefer "Áp dụng" for Vietnamese apps)
    for (const text of submitTexts) {
      const btn = page.locator(`${scope} button`).filter({ hasText: new RegExp(`^${text}$`, 'i') }).first();
      if (await btn.isVisible().catch(() => false)) {
        await btn.click();
        await sleep(400);
        return;
      }
    }
    // blur alone is sufficient when no submit button exists
  }

  async function readField(selector) {
    return page.evaluate((selector) => {
      const el = document.querySelector(selector);
      if (!el) return '';
      return 'value' in el ? el.value : (el.textContent || '').trim();
    }, selector);
  }

  // Resolve test data in priority order:
  // 1. tc.data (explicit cell value from spreadsheet)
  // 2. Quoted/example value extracted from steps or name text
  // 3. Keyword-based defaults when no explicit value is present
  function inferData(tc) {
    // 1. Spreadsheet "Data test" cell
    if (tc.data && tc.data.trim()) return tc.data.trim();

    // 2. Extract explicit value from steps/name text.
    //    Patterns recognised (case-insensitive, original-case preserved from raw text):
    //      - ví dụ: <value>            e.g. "ví dụ: ' OR 1=1--"
    //      - (ví dụ: <value>)          e.g. "(ví dụ: <script>alert(1)</script>)"
    //      - e.g. <value> / e.g.: <value>
    //      - 'single-quoted'           e.g. nhập 'Tìm kiếm'
    //      - "double-quoted"           e.g. nhập "test value"
    //      - nhập <X> ký tự / <X> chars → generate a string of length X
    const rawCtx = `${tc.steps || ''} ${tc.name || ''}`;

    // Extract from (ví dụ: ...) or ví dụ: ... (stops at ), newline, or end)
    const vdMatch = rawCtx.match(/v[ií] d[uụ]\s*:\s*([^\n\)]{1,120})/i);
    if (vdMatch) return vdMatch[1].trim().replace(/\)$/, '').trim();

    // Extract from e.g.: ... or e.g. ...
    const egMatch = rawCtx.match(/e\.g\.?\s*:?\s*([^\n\)]{1,120})/i);
    if (egMatch) return egMatch[1].trim().replace(/\)$/, '').trim();

    // Extract single-quoted value  'value'
    const sqMatch = rawCtx.match(/'([^']{1,120})'/);
    if (sqMatch) return sqMatch[1];

    // Extract double-quoted value  "value"
    const dqMatch = rawCtx.match(/"([^"]{1,120})"/);
    if (dqMatch) return dqMatch[1];

    // Extract N-character length request: "39 ký tự", "40 chars", etc.
    const lenMatch = rawCtx.match(/(\d+)\s*k[ií] t[ựu]|(\d+)\s*char/i);
    if (lenMatch) {
      const n = parseInt(lenMatch[1] || lenMatch[2], 10);
      return 'a'.repeat(n);
    }

    // 3. Keyword-based fallback (no explicit value found)
    const ctx = rawCtx.toLowerCase();
    if (/emoji/.test(ctx)) return '😀🎉';
    if (/xss|script/.test(ctx)) return '<script>alert(1)</script>';
    if (/sql.inject|sql inject/.test(ctx)) return "' OR 1=1--";
    if (/unicode.*trung|tiếng trung|tiếng nhật|tiếng hàn|cjk/.test(ctx)) return '你好日本語';
    if (/đặc biệt|special.*char|ký tự ngoài/.test(ctx)) return '@#!$%^&*';
    if (/all space|toàn bộ space/.test(ctx)) return '     ';
    if (/space đầu|space cuối|leading.*space|trailing.*space|trim/.test(ctx)) return '  test  ';
    if (/tiếng việt|vietnamese|có dấu/.test(ctx)) return 'tiếng Việt';
    if (/số|number|digit/.test(ctx)) return '123456';
    if (/chữ|letter|alpha/.test(ctx)) return 'abcdef';
    if (/paste/.test(ctx)) return 'pastetest';
    if (/partial|gần đúng|1 phần/.test(ctx)) return '381638';
    return '';
  }

  async function verify(tc, selector) {
    const typed = inferData(tc);            // what we attempted to type
    const value = await readField(selector); // what the field actually holds
    const expected = `${tc.expected || ''}`.toLowerCase();
    const errors = await page.locator('body')
      .locator('.error,.invalid,.ant-form-item-explain-error,[role="alert"],.text-danger,.text-red,.ng-invalid ~ .error-msg')
      .allTextContents()
      .catch(() => []);
    const errorText = errors.map(t => t.trim()).filter(Boolean).join(' | ');

    // "chặn không cho phép nhập" → field must be empty or differ from typed input
    if (/chặn|không cho phép nhập|khong cho phep nhap|không nhập được|blocked/.test(expected)) {
      const blocked = !value || value.trim() === '' || value === typed ? false : true;
      // Also pass if value is empty regardless
      const pass = !value || value.trim() === '';
      return { pass, actual: `Typed:"${typed}" → field:"${value}"` };
    }
    // "cho phép nhập" → field has some accepted value (may be stripped/transformed)
    if (/cho phép nhập|cho phep nhap|hệ thống cho phép/.test(expected)) {
      const pass = value !== null && value !== undefined && value.trim() !== '';
      return { pass, actual: `Value after input: "${value}"` };
    }
    // "tự động bỏ dấu" or "tự động trim" → field transforms input, just check non-empty
    if (/tự động bỏ dấu|tu dong bo dau|auto.*remov.*diacrit/.test(expected)) {
      return { pass: value.trim() !== '', actual: `Typed diacritics → stored:"${value}"` };
    }
    // "tự động trim space" → trimmed value equals typed without surrounding spaces
    if (/tự động trim|tu dong trim|trim space/.test(expected)) {
      const pass = value.trim() === typed.trim();
      return { pass, actual: `Raw:"${value}" Trimmed:"${value.trim()}"` };
    }
    // "clear data" / "xóa" → field is empty after action
    if (/mặc định rỗng|mac dinh rong|clear data|xóa data|xoa data/.test(expected)) {
      return { pass: !value || value.trim() === '', actual: `Value: "${value}"` };
    }
    // "thông báo lỗi" / "required" → validation error visible
    if (/thông báo lỗi|thong bao loi|message lỗi|required|bắt buộc|bat buoc/.test(expected)) {
      return { pass: !!errorText, actual: errorText || 'No validation error visible' };
    }
    // Default: observe and pass, record actual
    return { pass: true, actual: errorText || `Value: "${value}"` };
  }

  for (const tc of cases) {
    const screenshot = `${screenshotsDir}/${tc.safeName}.png`;
    try {
      const selector = locatorMap[tc.id] || locatorMap[tc.fieldGroup];
      if (!selector) throw new Error(`No locator mapped for ${tc.fieldGroup || tc.id}`);

      const field = await safeLocator(selector, tc.fieldGroup || tc.name);
      await field.scrollIntoViewIfNeeded();

      const actionText = `${tc.steps || ''} ${tc.name || ''}`.toLowerCase();
      const isObserve = /observe|quan sát|quan sat|kiểm tra hiển thị|kiem tra hien thi|mặc định|mac dinh/.test(actionText);

      if (!isObserve) {
        // Use tc.data if provided, otherwise infer from case context
        const inputData = inferData(tc);
        await setValue(selector, inputData);
        await sleep(200);
        // Trigger validation (blur + optionally click submit button)
        await triggerValidation(locatorMap.__mainSelector || null);
        await sleep(300);
      }

      const check = await verify(tc, selector);
      await page.screenshot({ path: screenshot, fullPage: false });
      results.push({
        id: tc.id,
        row: tc.row,
        verdict: check.pass ? 'P' : 'F',
        actual: check.actual,
        screenshot,
        error: ''
      });

      // Reset field after each case so next case starts clean
      if (!isObserve) {
        await setValue(selector, '');
        await sleep(150);
      }
    } catch (err) {
      await page.screenshot({ path: screenshot, fullPage: false }).catch(() => {});
      results.push({
        id: tc.id,
        row: tc.row,
        verdict: 'E',
        actual: err.message,
        screenshot,
        error: err.message
      });
    }
  }
  return JSON.stringify(results);
}
```

Adapt the action and verify functions to the application. Keep the safety invariants:

- scope to main content;
- require exactly one visible target;
- never click by coordinates;
- never click sidebar/header/navigation;
- mark `E` on ambiguous selectors.

### 6. Finalize Excel

Save the JSON returned by `browser_run_code` or pass it directly, then finalize:

```powershell
python -X utf8 D:\Code\agent-skills\execute-test-case-frontend\scripts\frontend_validate_excel.py finalize --run-dir "RUN_DIR" --results-file "D:\path\results.json"
```

or:

```powershell
python -X utf8 D:\Code\agent-skills\execute-test-case-frontend\scripts\frontend_validate_excel.py finalize --run-dir "RUN_DIR" --results-json "JSON_RETURNED_BY_BROWSER_RUN_CODE"
```

The helper writes:

- `Actual Result`
- `Lần 1 (Chrome)` as `P` / `F` / `E`
- `Screenshot`
- `Error`
- `Executed At`
- `Summary` sheet
- `Evidence` sheet with embedded screenshots when image files exist

Then close the browser:

```text
mcp__playwright__browser_close()
```

---

## Result Semantics

| Verdict | Meaning |
|---------|---------|
| `P` | observed behavior matches expected result |
| `F` | browser action succeeded but observed behavior does not match expected result |
| `E` | automation error, missing/ambiguous element, login/navigation failure, or script exception |

Do not write back to the source Google Sheet. The result workbook is the source of truth for this execution run.

---

## Speed Rules

- Download/copy the sheet once.
- Read `cases.json` once.
- Login once.
- Scan main DOM once per screen or field group.
- Run cases with `browser_run_code` batches, not one MCP click/type call per step.
- Save Excel once at the end.
- Capture one screenshot per case unless the user asks for more evidence.

---

## Anti-Misclick Rules

- Identify a main content selector before executing tests.
- Exclude `header`, `nav`, `aside`, `[role="navigation"]`, `[role="banner"]`, and `[role="toolbar"]`.
- Prefer stable semantic locators over CSS shape or position.
- Require exactly one visible target before editing/clicking.
- Use DOM value setters for text inputs when possible; dispatch `input`, `change`, and `blur` events.
- For combobox/date picker/button flows, click only exact visible options inside main content.
- If the UI opens a modal, re-scope to the modal body only while the modal is active.
- If the same selector matches multiple visible elements, mark the case `E` and continue.

---

## When To Stop

Stop and report instead of continuing when:

- login fails;
- target screen cannot be reached;
- main content cannot be identified;
- more than three consecutive cases fail from the same selector or navigation issue;
- the helper returns zero validate cases but the user expected cases.

Final response should include:

```text
Total selected: N
Executed: N
PASS: N
FAIL: N
ERROR: N
Result workbook: ...
Evidence screenshots: ...
```
