---
name: execute-test-case-api
description: Execute API test cases from a local Excel (.xlsx) file using Postman web. User navigates to collection manually, then Playwright takes over — runs first case step-by-step to discover selectors, builds a batch script, executes remaining cases via single browser_run_code call. Captures screenshots as evidence embedded into an Evidence sheet in the same .xlsx file. Writes PASS/FAIL back to the sheet. Triggers when user says "execute api test", "run api test cases", "chạy test case api", or provides a path to an .xlsx file with API test data.
---

# Execute Test Case — API

Reads API test cases from a local `.xlsx` file, executes each via **Postman web** (Playwright), captures screenshots embedded into an Evidence sheet, and writes results back — all without any MCP data calls.

**Strategy:** Run case 1 step-by-step to discover Postman selectors → build Playwright script → execute remaining cases in 1 `browser_run_code` call.

**Token savings:** ~90%+ vs per-action MCP calls.

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

### Step 4 — Case 1: Step-by-step selector discovery

Execute the **first pending test case** using individual MCP calls:

**4a — Snapshot to see current state:**
```
mcp__playwright__browser_snapshot()
```

**4b — Find and click the request in sidebar** matching the test case name:
```
mcp__playwright__browser_click(element="...", ref="...")
```

**4c — Click Send:**
```
mcp__playwright__browser_click(element="Send button", ref="...")
```

**4d — Wait for response:**
```
mcp__playwright__browser_wait_for(state="networkidle", timeout=15000)
```

**4e — Screenshot:**
```
mcp__playwright__browser_take_screenshot(filename="screenshots/{testCaseName}_{yyyyMMdd_HHmmss}.png")
```

**4f — Snapshot to read response:**
```
mcp__playwright__browser_snapshot()
```
Extract status code (3-digit number e.g. "200 OK") and response body text.

If body unreadable, try:
```
mcp__playwright__browser_evaluate(script="
  const el = document.querySelector('[data-testid=\"response-body\"]')
    || document.querySelector('.response-body-container');
  return el ? el.innerText : null;
")
```

**4g — Record selectors** discovered: sidebar item pattern, Send button, status element, body element.

### Step 5 — Build batch script

Using verified selectors from Step 4, build the Playwright script:

```js
async (page) => {
  const cases = CASES_JSON; // injected array of {name, screenshotPath}
  const results = [];

  for (const tc of cases) {
    try {
      // Find request in sidebar
      const item = page.locator('SIDEBAR_SELECTOR', { hasText: tc.name });
      await item.click();
      await page.waitForTimeout(500);

      // Send
      await page.locator('SEND_BUTTON_SELECTOR').click();
      await page.waitForLoadState('networkidle', { timeout: 15000 });
      await page.waitForTimeout(1000);

      // Screenshot
      await page.screenshot({ path: tc.screenshotPath });

      // Read status
      const statusText = await page.locator('STATUS_SELECTOR').textContent();
      const statusCode = parseInt(statusText.match(/\d{3}/)?.[0] || '0');

      // Read body
      let body = await page.locator('BODY_SELECTOR').textContent();
      if (body && body.length > 500) body = body.substring(0, 500) + '...';

      results.push({ name: tc.name, statusCode, body: body || '', screenshot: tc.screenshotPath, error: '' });
    } catch (err) {
      results.push({ name: tc.name, statusCode: 0, body: '', screenshot: '', error: err.message });
    }
  }
  return JSON.stringify(results);
}
```

Replace `CASES_JSON`, `SIDEBAR_SELECTOR`, `SEND_BUTTON_SELECTOR`, `STATUS_SELECTOR`, `BODY_SELECTOR` with actual values.

Generate screenshot paths: `screenshots/{testCaseName}_{yyyyMMdd_HHmmss}.png`

### Step 6 — Execute remaining cases (1 MCP call)

```
mcp__playwright__browser_run_code(code="<script from Step 5>")
```

Parse returned JSON.

**If script fails:** Re-run case 2 step-by-step to re-verify selectors, fix script, retry once.

### Step 7 — Validate results

Combine case 1 (Step 4) + batch results (Step 6).

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

- Case 1 always runs step-by-step (selector discovery)
- Remaining cases split into batches of 15
- Each batch = 1 `browser_run_code` call with same script, different `cases` array
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
