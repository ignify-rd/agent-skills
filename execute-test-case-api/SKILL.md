---
name: execute-test-case-api
description: Execute API test cases from a local Excel (.xlsx) file using Postman web. Reads auth config from auth.json, logs in to Postman, finds collection + environment, calls Login API first if auth is required, then runs all test cases. Playwright takes over — runs first case step-by-step to discover selectors, builds a batch script, executes remaining cases via single browser_run_code call. Captures screenshots as evidence embedded into an Evidence sheet in the same .xlsx file. Writes PASS/FAIL back to the sheet. Triggers when user says "execute api test", "run api test cases", "chạy test case api", or provides a path to an .xlsx file with API test data.
---

# Execute Test Case — API

Reads API test cases from a local `.xlsx` file, executes each via **Postman web** (Playwright), captures screenshots embedded into an Evidence sheet, and writes results back — all without any MCP data calls.

**Strategy:** Auth-aware execution → find collection + env → call Login API → run cases via batch script.

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
- `auth.json` config file in same directory as `.xlsx` (see Auth Config section)
- User has Postman web account

---

## Temp File Rules

**NEVER** write helper/temp scripts to disk. Use `python3 -X utf8 -c "..."` inline only.

---

## Auth Config (`auth.json`)

Located in the same directory as the `.xlsx` file. If not found, prompt user to create it.

```json
{
  "postman_email": "user@example.com",
  "postman_password": "yourpassword",
  "collection_name": "My API Collection",
  "environment_name": "Dev",
  "login_api_name": "Login",
  "auth_variable": "accessToken",
  "cookie_file": ""
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `postman_email` | Yes | Postman web login email |
| `postman_password` | Yes | Postman web login password |
| `collection_name` | Yes | Exact name of the collection in Postman |
| `environment_name` | Yes | Environment to activate (e.g., `Dev`, `Staging`) |
| `login_api_name` | No | Name of Login request in collection. If empty → skip auth step |
| `auth_variable` | No | Environment variable name that stores the token (default: `accessToken`) |
| `cookie_file` | No | Path to `cookies.json` — if provided, use cookies instead of login |

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

# data_only=True reads formula-computed values (not formula strings)
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx', data_only=True)

# Find the TestCase sheet
sheetName = 'TestCase'
if sheetName not in wb.sheetnames:
    # Try first sheet
    sheetName = wb.sheetnames[0]
ws = wb[sheetName]

# Step 1: Find header row — the row where col G (index 6) = 'Name' (test case name header)
headerRow = None
nameCol = 6    # default col G
resultCol = 25 # default col Z
actualCol = 16 # default col Q
for i, row in enumerate(ws.iter_rows(min_row=1, max_row=20, values_only=True), start=1):
    for j, cell in enumerate(row):
        val = str(cell).strip() if cell else ''
        if val == 'Name' and j == 6:
            headerRow = i
        if 'Kết quả' in val or 'ket qua' in val.lower():
            resultCol = j
        if 'Actual' in val or 'Kết quả thực tế' in val:
            actualCol = j

# Step 2: Read data rows
results = []
dataStart = (headerRow + 1) if headerRow else 17  # default start row 17
for i, row in enumerate(ws.iter_rows(min_row=dataStart, values_only=True), start=dataStart):
    name = row[nameCol] if len(row) > nameCol else None
    # Skip formula strings, empty, or header values
    if not name or not isinstance(name, str) or name.startswith('=') or name in ('Name', 'Test Case', 'Tên'):
        # Try summary column (col H = 7) as fallback
        name = row[7] if len(row) > 7 else None
        if not name or not isinstance(name, str):
            continue
    status = row[resultCol] if len(row) > resultCol else None
    results.append({
        'row': i,
        'name': name,
        'status': status,
        'nameCol': nameCol,
        'resultCol': resultCol,
        'actualCol': actualCol
    })

print(json.dumps({'headerRow': headerRow, 'cases': results}, ensure_ascii=False))
"
```

Parse output. Pending cases = those where `status` is None or empty.

**Note:** `resultCol` and `actualCol` are detected dynamically — use these values when writing results back (Step 10).

Print:
```
Loaded {total} test cases: {pending} pending, {done} already executed (skipping)
```

### Step 2 — Read auth config

```bash
python3 -X utf8 -c "
import json, os
xlsxDir = os.path.dirname('PATH_TO_FILE.xlsx')
authPath = os.path.join(xlsxDir, 'auth.json')
if not os.path.exists(authPath):
    print(json.dumps({'error': 'auth.json not found'}))
else:
    with open(authPath, encoding='utf-8') as f:
        print(f.read())
"
```

If `auth.json` not found → tell user:
```
auth.json not found in {xlsxDir}. Please create it with the following fields:
{show template from Auth Config section}
```
Then stop.

### Step 3 — Filter (optional)

User may specify a subset by name pattern or row range. If not specified → run all pending.

### Step 4 — Login to Postman web

Navigate to Postman web and log in using credentials from `auth.json`.

```
mcp__playwright__browser_navigate(url="https://web.postman.co")
```

If already logged in (user avatar visible) → skip login steps.

If login form visible:
```
mcp__playwright__browser_type(ref="email input", text="{postman_email}")
mcp__playwright__browser_type(ref="password input", text="{postman_password}")
mcp__playwright__browser_click(ref="Sign In button")
mcp__playwright__browser_wait_for(selector="[data-testid='user-avatar']", timeout=15000)
```

If `cookie_file` is provided in auth.json and file exists, inject cookies instead:
```js
// browser_run_code
async (page) => {
  const cookies = JSON.parse(fs.readFileSync(cookiePath, 'utf8'));
  await page.context().addCookies(cookies);
  await page.reload();
}
```

### Step 5 — Find collection and activate environment

**5a — Navigate to collection by name:**

Take a snapshot of the sidebar. Search for `{collection_name}` in the sidebar.
Click on it to open.

If not found → stop and ask user:
```
Collection "{collection_name}" not found in sidebar. Please verify the name in auth.json or open it manually.
```

**5b — Activate environment:**

Click the environment selector (top-right dropdown). Select `{environment_name}`.

If environment not found → warn user but continue (no environment = environment-less run).

### Step 6 — Auth: Call Login API first (if configured)

If `login_api_name` is set in auth.json:

**6a — Find Login request in collection sidebar:**

Look for a request named exactly `{login_api_name}` in the collection tree.

If not found → **STOP** and tell user:
```
Login API "{login_api_name}" not found in collection "{collection_name}".
Cannot proceed without auth. Either:
1. Add a Login request to your collection with that exact name, or
2. Clear "login_api_name" in auth.json if your API does not require auth.
```

**6b — Execute Login request:**

```
mcp__playwright__browser_click(element="sidebar item matching {login_api_name}", ref="...")
mcp__playwright__browser_click(element="Send button", ref="...")
mcp__playwright__browser_wait_for(state="networkidle", timeout=15000)
```

**6c — Verify login success:**

Run `browser_run_code` to fetch the login request and extract the token:

```js
async (page) => {
  // Read active response status
  const statusEl = document.querySelector('.response-meta-item__status:visible');
  return statusEl ? statusEl.textContent.trim() : 'unknown';
}
```

If status is not 2xx → **STOP**:
```
Login API returned {status}. Auth token not obtained. Check credentials in auth.json.
```

**6d — Extract token and save to environment:**

```js
async (page) => {
  // Get response body text from active tab
  const lines = [...document.querySelectorAll('.view-line')];
  return lines.map(l => l.textContent).join('');
}
```

Parse JSON response, extract `{auth_variable}` value.

If extraction fails → try common paths: `token`, `access_token`, `accessToken`, `data.token`.

Manually set in Postman environment via UI:
```
mcp__playwright__browser_click(element="environment quick-look icon")
// Find {auth_variable} row, update its Current Value
```

Or via `browser_run_code` using Postman SDK if available.

### Step 7 — Case 1: Step-by-step (send all via sidebar, then read)

**Phase A — Send all requests via sidebar clicks** (individual MCP calls):

For each test case:
```
mcp__playwright__browser_click(element="sidebar item matching {testCaseName}", ref="...")
mcp__playwright__browser_click(element="Send button", ref="...")
mcp__playwright__browser_wait_for(state="networkidle", timeout=15000)
```

**Note:** All requests must have Authorization set to **"Inherit auth from parent"** — do not override per-request. The collection-level auth uses the token set in Step 6.

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
      const tab = page.getByRole('tab').filter({ hasText: tc.name.substring(0, 20) });
      await tab.click();
      await page.waitForTimeout(500);

      await page.screenshot({ path: tc.screenshotPath });

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
- Timestamp generated at START of execution run, reused for all cases in that batch
- **NEVER** use pre-existing files from a previous run
- `screenshotDir` = `screenshots/` relative to the xlsx file location

### Step 8 — Execute batch (1 MCP call)

```
mcp__playwright__browser_run_code(code="<script from Step 7 Phase B>")
```

Parse returned JSON.

**If script fails:** Check error message. Common fixes:
- Tab selector not matching → use shorter prefix (first 10 chars of name) or index-based click
- fetch() CORS blocked → fall back to reading from active tab DOM using `:visible` filter
- Fix and retry once.

### Step 9 — Validate results

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

### Step 10 — Write results to .xlsx

```bash
python3 -X utf8 -c "
import openpyxl, json
from datetime import datetime

data = json.loads('''RESULTS_JSON''')
# data must include: row, actualResult, result, error, actualCol, resultCol
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')
sheetName = 'TestCase' if 'TestCase' in wb.sheetnames else wb.sheetnames[0]
ws = wb[sheetName]

for item in data:
    row = item['row']
    actualCol = item.get('actualCol', 16)   # default col Q (1-indexed = 17)
    resultCol = item.get('resultCol', 25)   # default col Z (1-indexed = 26)
    ws.cell(row=row, column=actualCol + 1).value = item['actualResult']
    ws.cell(row=row, column=resultCol + 1).value = item['result']
    ws.cell(row=row, column=resultCol + 2).value = item['error']  # next col after result

wb.save('PATH_TO_FILE.xlsx')
print('done')
"
```

### Step 11 — Embed screenshots into Evidence sheet

2 columns only: **A = Test Case ID**, **B = Screenshot** (image fits cell size exactly).

```bash
python3 -X utf8 -c "
import openpyxl, os, json
from openpyxl.drawing.image import Image as XLImage

data = json.loads('''RESULTS_JSON''')
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')

if 'Evidence' in wb.sheetnames:
    del wb['Evidence']
ws_ev = wb.create_sheet('Evidence')

ws_ev['A1'] = 'Test Case ID'
ws_ev['B1'] = 'Screenshot'

COL_A_WIDTH = 40
IMG_WIDTH_PX = 600
IMG_HEIGHT_PX = 350
ws_ev.column_dimensions['A'].width = COL_A_WIDTH
ws_ev.column_dimensions['B'].width = IMG_WIDTH_PX / 7

for i, item in enumerate(data, start=2):
    ws_ev.cell(row=i, column=1).value = item['name']
    if not item.get('screenshot') or not os.path.exists(item['screenshot']):
        ws_ev.cell(row=i, column=2).value = 'Screenshot not captured'
        continue
    img = XLImage(item['screenshot'])
    img.width = IMG_WIDTH_PX
    img.height = IMG_HEIGHT_PX
    ws_ev.row_dimensions[i].height = IMG_HEIGHT_PX * 0.75
    ws_ev.add_image(img, f'B{i}')

wb.save('PATH_TO_FILE.xlsx')
print('done')
"
```

### Step 12 — Cleanup & summary

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
| auth.json not found | STOP | `auth.json not found — create it first` |
| Postman login failed | STOP | `Postman login failed: {detail}` |
| Collection not found | STOP | `Collection "{name}" not found in sidebar` |
| Login API not found | STOP | `Login API "{name}" not found — cannot proceed` |
| Login API returned non-2xx | STOP | `Login API returned {status} — check credentials` |
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
- **NEVER** use pre-existing screenshot files from previous runs when embedding Evidence.
- **ALWAYS** verify screenshot file exists (`os.path.exists(path)`) before embedding.
- Screenshot filenames: `{testCaseName}_{yyyyMMdd_HHmmss}.png` (no spaces, replace with `_`).
- **NEVER** write temp scripts to disk — use `python3 -c` inline only.
- Save `.xlsx` only after ALL results collected (1 save operation).
- All requests in Postman must use **"Inherit auth from parent"** — never set per-request Bearer tokens.

---

## Anti-loop

Stop and ask user if:
- TestCase sheet not found in file
- Column G (Test Case Name) not found
- auth.json missing or malformed
- Login API not found in collection
- `browser_run_code` script fails 2 times in a row on same error
- Screenshot embed fails for all cases
