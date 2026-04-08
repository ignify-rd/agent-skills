---
name: execute-test-case-api
description: Execute API test cases from a local Excel (.xlsx) file using Postman web. User navigates to collection manually, then Playwright takes over — runs first case step-by-step to discover selectors, builds a batch script, executes remaining cases via single browser_run_code call. Captures screenshots as evidence embedded into an Evidence sheet in the same .xlsx file. Writes PASS/FAIL back to the sheet. Triggers when user says "execute api test", "run api test cases", "chạy test case api", or provides a path to an .xlsx file with API test data.
---

# Execute Test Case — API

Reads API test cases from a local `.xlsx` file, executes each via **Postman web** (Playwright), captures screenshots embedded into an Evidence sheet, and writes results back — all without any MCP data calls.

**Strategy:** Run case 1 step-by-step to discover Postman selectors → build Playwright script → execute remaining cases in 1 `browser_run_code` call.

**Token savings:** ~90%+ vs per-action MCP calls.

---

## ⛔ Mandatory Execution Method

**ALWAYS use Playwright MCP to execute tests via Postman web browser.**

- **NEVER** use `curl`, `requests`, `httpx`, or any direct HTTP library to send test requests
- **NEVER** call APIs directly from terminal/bash for the purpose of test execution
- The only exception is `page.evaluate(fetch(...))` inside a `browser_run_code` call — this runs inside the browser context through Postman web, which counts as browser-based execution
- Screenshots from Postman web UI are mandatory evidence — no browser = no evidence = invalid test

---

## Prerequisites

- **Playwright MCP** configured
- `openpyxl` installed (`pip show openpyxl`)
- Local `.xlsx` file accessible
- User has Postman web account and collection ready

---

## Temp File Rules

**NEVER** write helper/temp scripts to disk. Use `python3 -X utf8 -c "..."` inline only.

---

## Column Layout

Read the header row to detect column positions. Standard layout:

| Col | Field | Notes |
|-----|-------|-------|
| A | Test Suite Name | May span merged rows |
| G | Test Case Name | Used to match request in Postman collection |
| I | PreConditions | Natural language description |
| O | Step | Test steps description |
| P | Expected Result | Expected status + response description |
| Q | Actual Result | **Agent writes actual response here** |
| Z | Kết quả hiện tại | **Agent writes PASS / FAIL / ERROR** |

Skip rows where column G (Test Case Name) is empty or is a header value.
Pending = column Z empty.

---

## Workflow

### Step 1 — Read test cases from .xlsx

```bash
python3 -X utf8 -c "
import openpyxl, json
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')
ws = wb['TestCase']
results = []
for i, row in enumerate(ws.iter_rows(min_row=1, values_only=True), start=1):
    name = row[6]  # col G (0-indexed)
    if not name or not isinstance(name, str) or name in ('Name', 'Test Case'):
        continue
    status = row[25] if len(row) > 25 else None  # col Z
    results.append({'row': i, 'name': name, 'status': status})
print(json.dumps(results, ensure_ascii=False))
"
```

Parse output. Pending cases = those where `status` is None or empty.

Print:
```
Loaded {total} test cases: {pending} pending, {done} already executed (skipping)
```

### Step 2 — Filter (optional)

User may specify a subset by name pattern or row range. If not specified → run all pending.

### Step 3 — User navigates to collection

Tell user:
```
Please open Postman web (https://web.postman.co), navigate to your collection,
and confirm when ready.
```

Wait for user confirmation.

### Step 4 — Case 1: Step-by-step (send all via sidebar, then read)

**Phase A — Send all requests via sidebar clicks** (individual MCP calls):

For each test case:
```
mcp__playwright__browser_click(element="sidebar item matching {testCaseName}", ref="...")
mcp__playwright__browser_click(element="Send button", ref="...")
mcp__playwright__browser_wait_for(state="networkidle", timeout=15000)
```

This opens each request in its own tab and loads the response.

**Phase B — Screenshot + read via batch script** (1 MCP call):

After all requests are sent, run `browser_run_code` to loop through each tab, screenshot, and call `fetch()` for reliable data:

```js
async (page) => {
  const cases = [
    // { name, method, url, headers, body, screenshotPath, expectedStatus }
  ];
  const results = [];

  for (const tc of cases) {
    try {
      // 1. Click the TAB (top tab bar) to make it active for screenshot
      //    Use getByRole('tab') — NOT [role="treeitem"] (that's sidebar)
      const tab = page.getByRole('tab').filter({ hasText: tc.name.substring(0, 20) });
      await tab.click();
      await page.waitForTimeout(500);

      // 2. Screenshot Postman UI as evidence
      await page.screenshot({ path: tc.screenshotPath });

      // 3. Fetch directly for reliable status + body
      //    DO NOT read from .response-meta-item__status or .view-line —
      //    those selectors accumulate content from all open tabs in the DOM.
      const data = await page.evaluate(async ({ method, url, headers, body }) => {
        try {
          const opts = { method, headers };
          if (body) opts.body = body;
          const r = await fetch(url, opts);
          const text = await r.text();
          return { statusCode: r.status, body: text.substring(0, 500) };
        } catch (e) {
          return { statusCode: 0, body: e.message };
        }
      }, { method: tc.method, url: tc.url, headers: tc.headers || {}, body: tc.body || null });

      results.push({
        name: tc.name,
        statusCode: data.statusCode,
        body: data.body,
        screenshot: tc.screenshotPath,
        error: ''
      });
    } catch (err) {
      results.push({ name: tc.name, statusCode: 0, body: '', screenshot: tc.screenshotPath, error: err.message });
    }
  }
  return JSON.stringify(results);
}
```

> **Why fetch() instead of DOM scraping:**
> Postman web keeps all open tabs rendered in the DOM simultaneously.
> `.response-meta-item__status` returns the first element found (may be a hidden tab).
> `.view-line` (Monaco editor) accumulates text from ALL tabs, not just the active one.
> `fetch()` via `page.evaluate()` always returns the exact HTTP response — no DOM ambiguity.

**Screenshot path rules:**
- Format: `{screenshotDir}/{testCaseName_sanitized}_{yyyyMMdd_HHmmss}.png`
- `testCaseName_sanitized` = test case name with ALL spaces and special chars replaced by `_`
- Timestamp must be generated at the START of the execution run and reused for all cases in that batch (same `ts` variable)
- **NEVER** use pre-existing files from a previous run. Always use the `screenshot` path returned in the current batch result — this is the file that was just saved by `page.screenshot()` in this execution.
- `screenshotDir` = the screenshots folder specified or default to `screenshots/` relative to the xlsx file location

### Step 5 — Execute batch (1 MCP call)

```
mcp__playwright__browser_run_code(code="<script from Step 4 Phase B>")
```

Parse returned JSON.

**If script fails:** Check error message. Common fixes:
- Tab selector not matching → use shorter prefix (first 10 chars of name) or index-based click
- fetch() CORS blocked → fall back to reading from active tab DOM using `:visible` filter
- Fix and retry once.

### Step 6 — Validate results

Combine all results from Step 5.

For each result:
- Parse expected status from Expected Result cell (column P) — look for pattern like `1.1. Status: 404` or `Status: 200`
- Compare actual status vs expected
- Match → **PASS**
- Mismatch → **FAIL**: `Expected {expected}, got {actual}`
- Exception → **ERROR**: `{error message}`

Format actual result text:
```
Status: {actualStatusCode}
Response:
{actualResponseBody}
```

### Step 8 — Write results to .xlsx

```bash
python3 -X utf8 -c "
import openpyxl, json
from datetime import datetime

data = json.loads('''RESULTS_JSON''')
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')
ws = wb['TestCase']

for item in data:
    row = item['row']
    ws.cell(row=row, column=17).value = item['actualResult']   # col Q
    ws.cell(row=row, column=26).value = item['result']         # col Z
    ws.cell(row=row, column=27).value = item['error']          # col AA (error message)

wb.save('PATH_TO_FILE.xlsx')
print('done')
"
```

### Step 9 — Embed screenshots into Evidence sheet

```bash
python3 -X utf8 -c "
import openpyxl, json
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter

data = json.loads('''RESULTS_JSON''')
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')

# Create Evidence sheet if not exists
if 'Evidence' not in wb.sheetnames:
    ws_ev = wb.create_sheet('Evidence')
    ws_ev['A1'] = 'Test Case Name'
    ws_ev['B1'] = 'Screenshot'
    ws_ev['C1'] = 'Result'
    ws_ev['D1'] = 'Executed At'
    # Set column widths
    ws_ev.column_dimensions['A'].width = 50
    ws_ev.column_dimensions['B'].width = 80
    ws_ev.column_dimensions['C'].width = 10
    ws_ev.column_dimensions['D'].width = 20
else:
    ws_ev = wb['Evidence']

# Find next empty row
next_row = ws_ev.max_row + 1
if next_row == 2 and ws_ev['A1'].value == 'Test Case Name':
    next_row = 2

from datetime import datetime
ts = datetime.now().isoformat(timespec='seconds')

for item in data:
    if not item.get('screenshot'):
        continue
    r = next_row
    ws_ev.cell(row=r, column=1).value = item['name']
    ws_ev.cell(row=r, column=3).value = item['result']
    ws_ev.cell(row=r, column=4).value = ts
    try:
        img = XLImage(item['screenshot'])
        img.width = 600
        img.height = 350
        ws_ev.row_dimensions[r].height = 265
        ws_ev.add_image(img, f'B{r}')
    except Exception as e:
        ws_ev.cell(row=r, column=2).value = f'Screenshot not found: {item[\"screenshot\"]}'
    next_row += 1

wb.save('PATH_TO_FILE.xlsx')
print('done')
"
```

### Step 10 — Cleanup & summary

Close browser:
```
mcp__playwright__browser_close()
```

Print:
```
=== API Test Summary ===
Total:  {n}
PASS:   {n}
FAIL:   {n}
ERROR:  {n}
Results written to: {filePath}
Evidence sheet: {'created' | 'updated'} with {n} screenshots
```

---

## Batching (> 15 cases)

- Phase A (send via sidebar): send all requests first, up to 15 per batch
- Phase B (read via batch script): 1 `browser_run_code` call per batch, click tabs + fetch()
- Write all results in 1 Python call after all batches complete

---

## Error Classification

| Condition | Result | Message |
|-----------|--------|---------|
| Postman not logged in | ERROR | `Postman not logged in` |
| Request not found in sidebar | ERROR | `Request not found: {name}` |
| Response timeout | ERROR | `Request timeout after 15s` |
| Could not read response | ERROR | `Could not read response from Postman UI` |
| Status mismatch | FAIL | `Expected {expected}, got {actual}` |
| All checks pass | PASS | (empty) |

---

## Guardrails

- **NEVER** overwrite columns other than Q, Z, AA.
- **NEVER** re-execute rows with Result already set unless instructed.
- **ALWAYS** close browser after completion.
- **NEVER** use pre-existing screenshot files from previous runs when embedding Evidence. Use ONLY files whose paths were returned by `page.screenshot()` in the current execution batch.
- **ALWAYS** verify screenshot file exists (`os.path.exists(path)`) before embedding. If missing → write `"Screenshot not captured"` in cell, do not embed.
- When the screenshots folder contains files from multiple runs, identify current-run files by matching the exact paths stored in the results object — not by scanning the folder.
- Screenshot filenames: `{testCaseName}_{yyyyMMdd_HHmmss}.png` (no spaces, replace spaces with `_`).
- **NEVER** write temp scripts to disk — use `python3 -c` inline only.
- Save `.xlsx` only after ALL results collected (1 save operation).

---

## Anti-loop

Stop and ask user if:
- TestCase sheet not found in file
- Column G (Test Case Name) not found
- Postman requires login and user cannot confirm
- `browser_run_code` script fails 2 times in a row on same error
- Screenshot embed fails for all cases
