---
name: execute-test-case-frontend
description: Execute frontend validation test cases from a Google Sheets URL or local Excel file using Playwright MCP tools directly (browser_fill, browser_click, browser_press_key, etc.). Downloads/copies the input into a local .xlsx run folder, filters only "Kiểm tra validate" cases, preprocesses cases into per-group step plans, runs each case with individual MCP calls, captures screenshots, and writes P/F/E plus evidence into one Excel result workbook. Use when the user asks to run FE/frontend test cases, "chạy test case frontend", execute only validate cases, or make frontend execution work like auto-postman.
---

# Execute Test Case - Frontend Validate

Run frontend validate cases using Playwright MCP tools directly — no big JS scripts built at runtime. The core loop is: **prepare → preprocess → navigate/login → execute per group → incremental save → finalize**.

**Core rule:** Use individual MCP tools (`browser_fill`, `browser_click`, `browser_press_key`, `browser_snapshot`, `browser_take_screenshot`) for all browser actions. Reserve `browser_run_code` only for DOM inspection queries that cannot be expressed with other MCP tools.

**Goal:** Clear, predictable execution — each case maps to a fixed sequence of MCP calls with only the input value changing per case.

---

## Required Inputs

- `url`: application page under test.
- One input source:
  - Google Sheets URL, or
  - local `.xlsx` path, or
  - `values-json` exported from Sheets MCP when direct Google export is not allowed.
- Optional `sheetName`: defaults to `TestCase`, otherwise first worksheet.

---

## Environment Constraints — `browser_run_code`

The JS execution context of `browser_run_code` is a **Playwright evaluate context**, NOT a browser page context or Node.js. These APIs are **NOT available**:

| ❌ Unavailable | ✅ Use instead |
|---|---|
| `setTimeout` / `setInterval` | `await page.waitForTimeout(ms)` |
| `fetch` / `XMLHttpRequest` | `await page.evaluate(() => fetch(...))` — but localhost is unreliable, avoid |
| `require` / `import` | Not available — inline all code |
| `fs` / `process` / Node APIs | Not available — use Python scripts for file I/O |
| `console.log` (for debugging) | Return values from `browser_run_code` directly |

**Timeout:** Each `browser_run_code` call has a **120-second hard timeout**. Never attempt to execute more than a handful of sequential operations in a single call. The DOM crawl (§4b) is fine as it's a single fast query. For test execution, use individual MCP tool calls per case.

**Localhost fetch:** `page.evaluate(() => fetch('http://127.0.0.1:...'))` will hang because the browser page typically can't reach localhost services. Do NOT use this pattern. Store results in AI working memory instead.

---

## PowerShell Path Handling

Windows paths containing `[` or `]` (e.g. `D:\[WEB]_Danh sách.xlsx`) cause failures:

| Command | Problem | Fix |
|---|---|---|
| `Test-Path "path"` | `[` `]` treated as wildcard → returns `False` | `Test-Path -LiteralPath "path"` |
| `Copy-Item "src" "dst"` | Same wildcard issue | `Copy-Item -LiteralPath "src" -Destination "dst"` |
| `Get-Item "path"` | Same | `Get-Item -LiteralPath "path"` |

**Rule:** Always use `-LiteralPath` when the path may contain special characters. When passing paths to Python scripts, use double-quotes and the path works normally since Python's `pathlib` doesn't interpret wildcards.

---

## Expected Columns

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

---

## Workflow

### 1. Prepare Excel Run

```powershell
# Local Excel (note: -LiteralPath not needed here — Python handles paths correctly):
python -X utf8 "D:\Code\card4-skills\.claude\skills\execute-test-case-frontend\scripts\frontend_validate_excel.py" prepare --xlsx "D:\path\input.xlsx"

# Google Sheets:
python -X utf8 "D:\Code\card4-skills\.claude\skills\execute-test-case-frontend\scripts\frontend_validate_excel.py" prepare --sheet-url "SHEET_URL" --sheet-name "TestCase"
```

Prints JSON with `runDir`, `casesFile`, `screenshotsDir`, `caseCount`, `groups`. Stop if `caseCount == 0`.

### 2. Read Cases

Read `cases.json`. Each case:

```json
{
  "id": "r18",
  "row": 18,
  "suite": "Kiểm tra validate",
  "fieldGroup": "Textbox: Tên",
  "name": "Kiểm tra khi nhập số",
  "steps": "Nhập số vào field Tên",
  "data": "123",
  "expected": "Hệ thống chặn không cho phép nhập",
  "safeName": "18_case_name"
}
```

### 3. Navigate and Login Once

```
browser_navigate(url)
```

If the page redirects to a login form:
- Fill username, password from preconditions
- Fill captcha if present (user provides captcha value in arguments)
- Click Login
- Wait for the target screen to appear
- **Do not re-login between cases.**

### 4. Preprocess: DOM Crawl + Define Group Plans (Combined)

**Before any test execution**, run a **single DOM crawl** that simultaneously:
1. Extracts all interactive elements and their locators from the live page
2. Matches elements to `fieldGroup` names from `cases.json`
3. Produces a complete `groupPlan` for every group — no re-scanning needed during execution

This is one `browser_run_code` call (or two if advanced search must be expanded first). All locators are resolved upfront and stored in memory.

#### 4a. Expand hidden panels first

If any `fieldGroup` names suggest fields that may be hidden (e.g. combobox filters, date pickers), trigger their reveal before crawling:

```
browser_run_code → click "Tìm kiếm nâng cao" or equivalent toggle
[wait 600ms via page.waitForTimeout(600)]
```

**⚠️ Use `await page.waitForTimeout(600)` — NOT `setTimeout`.**

#### 4b. Single DOM crawl — extract everything

Run one `browser_run_code` that walks the entire main content tree and returns a structured map of every interactive element:

```js
async (page) => {
  return await page.evaluate(() => {
    const bad = 'header,nav,aside,[role="navigation"],[role="banner"],[role="toolbar"]';
    const visible = el => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && getComputedStyle(el).display !== 'none';
    };

    // Find label text associated with an element
    const labelOf = el => {
      if (el.id) {
        const lbl = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
        if (lbl) return lbl.innerText.trim();
      }
      // TUI: label inside the component wrapper
      const wrapper = el.closest('tui-input,tui-select,tui-multi-select,tui-input-date-range,tui-textarea,tui-combo-box');
      if (wrapper) {
        const lbl = wrapper.querySelector('label');
        if (lbl) return lbl.innerText.trim();
      }
      return '';
    };

    // Stable CSS selector (prefer id, then component tag, then class path)
    const sel = el => {
      if (el.id && !el.id.startsWith('tui_')) return `#${CSS.escape(el.id)}`;
      const comp = el.closest('tui-input,tui-select,tui-multi-select,tui-input-date-range,tui-textarea,tui-combo-box,ibank2-input-text-search');
      if (comp) {
        const stable = comp.tagName.toLowerCase();
        const nth = [...(comp.parentElement?.children || [])].filter(c => c.tagName === comp.tagName).indexOf(comp);
        const nthSuffix = nth > 0 ? `:nth-of-type(${nth + 1})` : '';
        return `${stable}${nthSuffix} input`;
      }
      const parts = [];
      for (let n = el; n && n !== document.body; n = n.parentElement) {
        let p = n.tagName.toLowerCase();
        const stableClass = [...n.classList].find(c => !c.match(/^(ng-|t-|_nghost|_ngcontent|tui_)/));
        if (stableClass) p += '.' + CSS.escape(stableClass);
        parts.unshift(p);
      }
      return parts.join(' > ');
    };

    const fields = [];
    const seen = new Set();

    for (const el of document.querySelectorAll(
      'input,textarea,select,[role="combobox"],[role="textbox"],[contenteditable="true"],' +
      'tui-input,tui-select,tui-multi-select,tui-input-date-range'
    )) {
      if (!visible(el) || el.closest(bad)) continue;
      const r = el.getBoundingClientRect();
      const key = `${Math.round(r.x)},${Math.round(r.y)}`;
      if (seen.has(key)) continue;
      seen.add(key);

      const actualInput = el.tagName.startsWith('TUI') ? el.querySelector('input') : el;
      if (!actualInput) continue;

      fields.push({
        label: labelOf(el),
        tag: el.tagName.toLowerCase(),
        inputSel: sel(actualInput),
        triggerSel: el.tagName.startsWith('TUI') ? sel(el) : null,
        type: el.getAttribute('type') || '',
        maxlength: actualInput.getAttribute('maxlength') || '',
        placeholder: actualInput.getAttribute('placeholder') || actualInput.getAttribute('aria-label') || '',
        rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }
      });
    }

    const buttons = [...document.querySelectorAll('button,[role="button"]')]
      .filter(el => visible(el) && !el.closest(bad))
      .map(el => {
        const r = el.getBoundingClientRect();
        return {
          text: el.innerText.trim().slice(0, 60),
          ariaLabel: el.getAttribute('aria-label') || '',
          rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }
        };
      });

    const grid = document.querySelector('[role="treegrid"],[role="grid"],table');
    const gridCols = grid
      ? [...grid.querySelectorAll('[role="columnheader"],th')].map(th => th.innerText.trim())
      : [];

    return JSON.stringify({ fields, buttons, gridCols });
  });
}
```

#### 4c. Build group plans from crawl output

After receiving the crawl JSON, match each `fieldGroup` from `cases.json` to the extracted `fields` by **label text similarity** (case-insensitive, substring match). Then classify and build a plan:

```json
{
  "fieldGroup": "Kiểm tra textbox \"Tìm kiếm nhanh\"",
  "type": "textbox",
  "inputSel": "ibank2-input-text-search input",
  "triggerSel": null,
  "clearIconSel": null,
  "submitSel": "button[text='Áp dụng']",
  "verifyStrategy": "field_value",
  "maxlength": 40,
  "notes": "maxlength=40 enforced by TUI; Tab triggers blur validator"
}
```

**Type classification rules** (apply in order):

| `fieldGroup` contains | Assigned type |
|---|---|
| textbox / input / tìm kiếm nhanh | `textbox` |
| combobox / loại yêu cầu / trạng thái | `combobox` |
| date range / ngày / date picker | `datepicker` |
| checkbox | `checkbox` |
| lưới / grid / cột / sort / phân trang / cuộn / scroll | `observe` |

**Store all plans in memory** before executing any case. The DOM crawl result is the single source of truth for the entire execution run — no re-scanning between cases or groups.

### 5. Execute Cases — Per Group

Process all cases of the same `fieldGroup` together. For each group:

1. Ensure the group's field is visible (open advanced search if required).
2. For each case in the group, run the **step sequence** defined by `type`.
3. **After each case**, append result to `allResults[]` in AI working memory.
4. **After each group finishes**, call `incremental` to persist results to Excel.

---

#### Type: `textbox`

Per-case step sequence:

```
Step 1 — Focus field:
  browser_click(locator)

Step 2 — Clear existing value:
  browser_press_key("Control+a")
  browser_press_key("Delete")   [or browser_fill(locator, "")]

Step 3 — Type value (only if not an observe case):
  browser_type(locator, inferData(tc))
  [use insertText via browser_run_code if Vietnamese diacritics are needed]

Step 4 — Trigger validator:
  browser_press_key("Tab")

Step 5 — Verify:
  browser_run_code → read input.value (NOT wrapper innerText), check for error elements
  Apply verifyStrategy (see §Verify Strategies)

Step 6 — Screenshot:
  browser_take_screenshot(path=screenshotsDir/safeName.png)

Step 7 — Reset field:
  browser_click(locator)
  browser_press_key("Control+a")
  browser_press_key("Delete")
  browser_press_key("Tab")
```

For **observe** cases (name/steps contains: quan sát, mặc định, hiển thị mặc định, kiểm tra hiển thị):
- Skip Steps 2–3–4–7
- Just take snapshot/screenshot and verify

---

#### Type: `combobox`

Per-case step sequence:

```
Step 1 — Click trigger to open dropdown:
  browser_click(triggerLocator or locator)
  [wait 500ms]

Step 2 — Read available options (first time per group):
  browser_run_code → find options in tui-dropdown or cdk-overlay

Step 3 — Click the target option (only if not observe):
  browser_run_code → find option by text, click it
  [for "Tất cả" as default observe case: just read displayed text without opening]

Step 4 — Close dropdown:
  browser_press_key("Escape")
  [wait 300ms]

Step 5 — Verify:
  browser_run_code → read displayed value of combobox
  Apply verifyStrategy

Step 6 — Screenshot:
  browser_take_screenshot(path=screenshotsDir/safeName.png)

Step 7 — Reset to default:
  [only if a non-default option was selected]
  browser_click(triggerLocator)
  [click "Tất cả" option or click X clear icon]
  browser_press_key("Escape")
```

**Dropdown option discovery**: TUI dropdowns render in `tui-dropdown` (not `.cdk-overlay-container`). Use:
```js
// browser_run_code to find options:
async (page) => {
  return await page.evaluate(() => {
    const dd = document.querySelector('tui-dropdown');
    const opts = [...(dd?.querySelectorAll('[role="option"]') || [])];
    return opts.map(o => o.innerText.trim());
  });
}
```

**Never click `li` as a standalone option selector** — always scope to `tui-dropdown` first.

---

#### Type: `datepicker`

Per-case step sequence:

```
Step 1 — Click date range trigger:
  browser_click(triggerLocator)
  [wait 600ms for calendar to render]

Step 2 — Interact with calendar:
  For "date input" cases: browser_type(inputLocator, dateValue)
  For "select from calendar" cases: navigate months then click day cells
  For "clear" cases: click X icon

Step 3 — Close calendar:
  browser_press_key("Escape") or click outside

Step 4 — Verify:
  browser_run_code → read actual date values from inner inputs (see §6a)
  Apply verifyStrategy

Step 5 — Screenshot:
  browser_take_screenshot(path=screenshotsDir/safeName.png)

Step 6 — Reset:
  Click X clear icon on date range field
```

**⚠️ TUI Date Range Picker — reading values correctly:**

TUI `tui-input-date-range` contains two `<input>` elements (from-date and to-date). Reading from the wrapper's `innerText` returns the label text (e.g. "Date range Ngày yêu cầu hiển thị"), NOT the date values.

```js
// CORRECT — read from inner input elements:
async (page) => {
  return await page.evaluate(() => {
    const dr = document.querySelector('tui-input-date-range');
    const inputs = dr ? dr.querySelectorAll('input') : [];
    const fromVal = inputs[0]?.value || '';
    const toVal = inputs[1]?.value || '';
    // Check for error/validation state
    const hasError = dr?.classList.contains('ng-invalid') && dr?.classList.contains('ng-touched');
    const errorEl = dr?.closest('.field-wrapper,.form-group')?.querySelector('[class*="error"],[class*="invalid"]');
    return JSON.stringify({
      from: fromVal,
      to: toVal,
      display: fromVal && toVal ? `${fromVal} – ${toVal}` : '',
      hasError: hasError || false,
      errorText: errorEl?.innerText?.trim() || ''
    });
  });
}
```

**⚠️ Many date picker cases may be false positives.** TUI date range components often:
- Accept any typed text into the input field (including invalid dates, emoji, XSS)
- Only validate the actual Date value on form submission or blur
- Don't visually block invalid input at the field level

When reviewing FAIL results for datepicker cases, check whether the "expected behavior" (e.g. "chặn nhập") matches TUI's actual behavior (which may allow input but show error on blur/submit).

---

#### Type: `observe`

For grid, table, column, sort, pagination, scroll cases:

```
Step 1 — Perform the described action (click sort header, change page size, etc.)
  browser_click(target element)
  [wait 500ms]

Step 2 — Snapshot or screenshot:
  browser_snapshot() to read current DOM state
  browser_take_screenshot(path=screenshotsDir/safeName.png)

Step 3 — Verify:
  Check the snapshot/DOM for expected state
  Apply verifyStrategy (usually "visible" or "table_rows")
```

---

### 6. Verify Strategies

**Never use screenshots to read page state.** After each action, run a targeted `browser_run_code` that returns only the data needed to evaluate pass/fail. Screenshots are taken **only as evidence** via `browser_take_screenshot` after the verdict is already determined.

#### 6a. Verify helper (one `browser_run_code` per case)

**⚠️ Critical: always read `input.value` from the actual `<input>` element, never from wrapper `innerText`.**

```js
async (page) => {
  return await page.evaluate(() => {
    const inputSel = '__INPUT_SEL__';

    // Always drill into the actual <input> or <textarea>
    const rawEl = document.querySelector(inputSel);
    const input = (rawEl?.tagName === 'INPUT' || rawEl?.tagName === 'TEXTAREA')
      ? rawEl
      : rawEl?.querySelector('input,textarea');

    const fieldValue = input ? input.value : null;

    // For TUI date range — read both inputs
    const dateRange = rawEl?.closest('tui-input-date-range') || rawEl?.tagName?.toLowerCase() === 'tui-input-date-range' ? rawEl : null;
    let dateValues = null;
    if (dateRange || rawEl?.closest('tui-input-date-range')) {
      const dr = dateRange || rawEl.closest('tui-input-date-range');
      const dateInputs = dr.querySelectorAll('input');
      dateValues = {
        from: dateInputs[0]?.value || '',
        to: dateInputs[1]?.value || ''
      };
    }

    // Error detection — broad selectors for various UI frameworks
    const errorTexts = [...document.querySelectorAll(
      '.error,.invalid,[role="alert"],.text-danger,.ng-invalid ~ .error-msg,[class*="error-msg"],[class*="text-error"],[class*="field-error"]'
    )].filter(el => el.getBoundingClientRect().height > 0)
      .map(el => el.innerText.trim()).filter(Boolean);

    const clearIconVisible = (() => {
      const wrapper = rawEl?.closest('tui-input,tui-select,tui-multi-select,tui-input-date-range,ibank2-input-text-search');
      if (!wrapper) return false;
      const clearBtn = wrapper.querySelector('[automation-id*="clear"],[tuicleaner],[class*="t-clear"],button[class*="clear"]');
      return clearBtn ? clearBtn.getBoundingClientRect().height > 0 : false;
    })();

    const tableRows = document.querySelectorAll(
      '[role="treegrid"] [role="row"],[role="grid"] tr,tbody tr'
    ).length;

    const comboDisplayText = (() => {
      const tuiSel = [...document.querySelectorAll('tui-select,tui-multi-select,tui-combo-box')]
        .find(s => s.contains(rawEl));
      if (!tuiSel) return null;
      // Read from the content projection, not input value
      const content = tuiSel.querySelector('[class*="content"],[class*="textfield-value"]');
      return content?.innerText?.trim() || tuiSel.querySelector('input')?.value || null;
    })();

    return JSON.stringify({ fieldValue, dateValues, errorTexts, clearIconVisible, tableRows, comboDisplayText });
  });
}
```

#### 6b. Pass/fail decision table

Apply in order — first matching keyword wins:

| Expected keyword | Pass condition | `actual` recorded |
|---|---|---|
| `cho phép nhập` | `fieldValue` is non-empty | `"Value: <fieldValue>"` |
| `chặn / không cho phép nhập` | `fieldValue` is empty OR unchanged from before | `"Typed:<inputData> → field:<fieldValue>"` |
| `tự động bỏ dấu` | `fieldValue` non-empty (diacritics removed) | `"Stored: <fieldValue>"` |
| `tự động trim` | `fieldValue.trim() === inputData.trim()` | `"Raw:<fieldValue>"` |
| `thông báo lỗi / required / bắt buộc` | `errorTexts.length > 0` | joined error text |
| `clear data / rỗng / mặc định rỗng` | `fieldValue` is empty | `"Value: <fieldValue>"` |
| `icon X / icon x` | `clearIconVisible === true` | `"Icon X visible: <true/false>"` |
| `placeholder` | `fieldValue` empty + label visible | `"Placeholder shown"` |
| `kết quả chứa / hiển thị kết quả` | `tableRows > 0` | `"Rows: <tableRows>"` |
| `cho phép chọn / hiển thị giá trị` | `comboDisplayText` non-empty | `"Displayed: <comboDisplayText>"` |
| `ngày / date range` (datepicker) | `dateValues.from` or `dateValues.to` matches expected | `"From:<from> To:<to>"` |
| Default | always P | `"Value: <fieldValue>"` |

### 7. Infer Input Data

Resolve input value per case in this priority order:

1. `tc.data` cell from spreadsheet (use as-is if non-empty)
2. Extract from steps/name text:
   - `ví dụ: <value>` or `(ví dụ: <value>)`
   - `'single-quoted'` or `"double-quoted"`
   - `N ký tự` or `N chars` → `'a'.repeat(N)`
3. Keyword fallback from steps/name:
   - emoji → `😀🎉`
   - xss/script → `<script>alert(1)</script>`
   - sql inject → `' OR 1=1--`
   - tiếng trung/nhật/hàn → `你好日本語`
   - đặc biệt/special char → `@#!$%^&*`
   - all space → `'     '`
   - space đầu/cuối/trim → `'  test  '`
   - tiếng việt/có dấu → `tiếng Việt`
   - số/number → `123456`
   - chữ/letter → `abcdef`
   - partial/gần đúng → `381638`
4. Empty string if no match

### 8. Collect Results — Incremental Persistence

**After each case**, append to a results list **in AI working memory** (a variable, NOT in browser context):

```json
{
  "id": "r18",
  "row": 18,
  "verdict": "P",
  "actual": "field value after input: \"123\"",
  "screenshot": "D:\\...\\screenshots\\18_case_name.png",
  "error": ""
}
```

Verdict codes:
- `P` — observed behavior matches expected
- `F` — action succeeded but result does not match expected
- `E` — automation error (element not found, ambiguous locator, login failure, etc.)

**⚠️ Do NOT store results in `window.__frontendResults` or any browser-side variable.** Browser context is unreliable:
- Page navigations clear `window` state
- Browser crashes lose all data
- No way to persist to disk from browser context

Instead, keep `allResults` as a conceptual list in the AI agent's working memory and persist after each group.

### 9. Incremental Save — After Each Group

After completing all cases in a group, write results to disk immediately:

```powershell
# Write results for the completed group to a JSON file first:
# (Avoids PowerShell escaping issues with large JSON on command line)
Set-Content -LiteralPath "RUN_DIR\results_partial.json" -Value 'JSON_ARRAY' -Encoding UTF8

# Then call incremental save:
python -X utf8 "D:\Code\card4-skills\.claude\skills\execute-test-case-frontend\scripts\frontend_validate_excel.py" incremental --run-dir "RUN_DIR" --results-file "RUN_DIR\results_partial.json"
```

The `incremental` subcommand:
- Writes verdict + actual + screenshot + error + executedAt to each row in the result workbook
- Does NOT create Summary/Evidence sheets (saves time)
- Returns count of rows written
- Can be called multiple times safely (overwrites same cells)

This ensures that **if the agent is interrupted**, all groups completed so far are already saved in the Excel workbook.

### 10. Finalize Excel

After **all groups** are done (or after recovering from an interruption), finalize once:

```powershell
# Write all results to file:
Set-Content -LiteralPath "RUN_DIR\results_final.json" -Value 'FULL_JSON_ARRAY' -Encoding UTF8

python -X utf8 "D:\Code\card4-skills\.claude\skills\execute-test-case-frontend\scripts\frontend_validate_excel.py" finalize --run-dir "RUN_DIR" --results-file "RUN_DIR\results_final.json"
```

The helper writes Actual Result, verdict, Screenshot, Error, Executed At columns, plus Summary and Evidence sheets.

Then close the browser:
```
browser_close()
```

---

## Anti-Misclick Rules

- Always scope element search to main content — exclude `header`, `nav`, `aside`, `[role="navigation"]`, `[role="banner"]`, `[role="toolbar"]`.
- For dropdowns: always scope option lookup to `tui-dropdown` or the specific overlay container, never to `document` globally.
- After `browser_fill` or `browser_type`, always press Tab (`browser_press_key("Tab")`) to trigger field-level validators.
- If a selector matches 0 or 2+ visible elements, mark case `E` and continue to next case.
- Never use pixel coordinates for clicking — always use semantic locators.
- For TUI components with dynamic IDs (`tui_XXXX`): do not rely on the ID across cases — locate by label text, component tag, or stable attributes instead.

---

## When To Stop

Stop and report immediately when:
- Login fails
- Target screen cannot be reached
- Main content cannot be identified after `browser_snapshot`
- 3+ consecutive cases in the same group all return `E` from the same root cause

**Before stopping, always call `incremental` save** for any results collected so far.

Final response format:

```
Total selected: N
Executed: N
PASS: N  
FAIL: N
ERROR: N
Skipped (not executed): N
Result workbook: D:\...\frontend_validate_results_YYYYMMDD_HHMMSS.xlsx
```
