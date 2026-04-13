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

Wait 3–5 seconds for redirect. If login page appears:

```js
// browser_run_code — fill and submit login form
async (page) => {
  await page.getByRole('textbox', { name: 'Email or username' }).fill('{postman_email}');
  await page.getByRole('textbox', { name: 'Password' }).fill('{postman_password}');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('**postman.co/**', { timeout: 20000 });
  return page.url();
}
```

Wait 4 more seconds for Postman workspace to finish loading.

If `cookie_file` is provided in auth.json and file exists, inject cookies instead:
```js
// browser_run_code
async (page) => {
  const fs = require('fs');
  const cookies = JSON.parse(fs.readFileSync('{cookiePath}', 'utf8'));
  await page.context().addCookies(cookies);
  await page.reload();
  await page.waitForTimeout(3000);
}
```

### Step 5 — Find collection and activate environment

**5a — Navigate to collection by name:**

Use `browser_run_code` to find and click the collection in the sidebar:
```js
async (page) => {
  const items = page.locator('[role="treeitem"]');
  const count = await items.count();
  for (let i = 0; i < count; i++) {
    const text = await items.nth(i).textContent();
    if (text?.includes('{collection_name}')) {
      await items.nth(i).click();
      await page.waitForTimeout(1500);
      return 'found';
    }
  }
  return 'not_found';
}
```

If `not_found` → stop and ask user:
```
Collection "{collection_name}" not found in sidebar. Please verify the name in auth.json or open it manually.
```

**5b — Activate environment:**

```js
// browser_run_code — activate environment by name
async (page) => {
  // Open env dropdown
  await page.locator('[data-testid="environment-selector"]').click();
  await page.waitForTimeout(1000);
  // Click matching option
  const option = page.locator('[data-testid="env-filter-select-dropdown__option"]')
    .filter({ hasText: '{environment_name}' });
  if (await option.count() === 0) return 'not_found';
  await option.first().click();
  await page.waitForTimeout(800);
  return 'selected';
}
```

If `not_found` → warn user but continue (no environment = environment-less run).

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

**6b — Execute Login request and verify:**

```js
// browser_run_code — click Login in sidebar, Send, wait for response
async (page) => {
  // Find and click Login request in sidebar
  const items = page.locator('[role="treeitem"]');
  const count = await items.count();
  for (let i = 0; i < count; i++) {
    const text = await items.nth(i).textContent();
    if (text?.trim().replace(/^(GET|POST|PUT|PATCH|DELETE)/, '').trim() === '{login_api_name}') {
      await items.nth(i).click();
      await page.waitForTimeout(1500);
      break;
    }
  }

  // Click Send
  await page.getByRole('button', { name: 'Send', exact: true }).click();

  // Wait for response status in ACTIVE tab (scope prevents hidden-tab match)
  await page.locator('[data-testid="active-tab-content"] [data-testid="response-code"]')
    .waitFor({ state: 'visible', timeout: 20000 });
  await page.waitForTimeout(500);

  // Read status code (scoped to active tab)
  const statusCode = await page.locator('[data-testid="active-tab-content"] [data-testid="response-code"]')
    .first().textContent();

  // Read response body from active tab's response pane
  const body = await page.evaluate(() => {
    const activeContent = document.querySelector('[data-testid="active-tab-content"]');
    if (!activeContent) return '';
    const lines = [...activeContent.querySelectorAll('.response-viewer-pane .view-line')];
    return lines.map(l => l.textContent).join('\n').trim().substring(0, 1000);
  });

  return JSON.stringify({ statusCode: parseInt(statusCode), body });
}
```

If status is not 2xx → **STOP**:
```
Login API returned {status}. Auth token not obtained. Check credentials in auth.json.
```

**6c — Token is set automatically:**

If the collection's Tests script contains `pm.environment.set('{auth_variable}', ...)`, the token is set automatically. No further action needed.

If NOT automated → manually set via environment quick-look:
- Click the eye icon next to the environment selector
- Find `{auth_variable}` row → update Current Value with token from response body
- Fallback paths if token key differs: `token`, `access_token`, `accessToken`, `data.token`

### Step 7 — Execute test cases via batch script (1 MCP call)

Build the `cases` array from Step 1 data, then run **one** `browser_run_code` call.

Each test case captures **3 screenshots** in this order:
1. `_params.png` — Params tab (request query/path params), taken **before** Send
2. `_body.png` — Body tab (request body), taken **before** Send
3. `_response.png` — Response pane clipped, taken **after** Send completes

```js
async (page) => {
  const cases = [
    // Fill from Step 1 data — one object per pending test case:
    // {
    //   name: 'Login',
    //   row: 18,
    //   sanitizedName: 'Login',          // name with spaces/special chars → _
    //   timestamp: '20260413_120000',    // yyyyMMdd_HHmmss, same for all cases in batch
    //   screenshotDir: 'C:/path/to/screenshots',
    //   expectedStatus: 200,             // parsed from Expected Result column
    //   nameCol: 6, actualCol: 16, resultCol: 25
    // }
  ];

  const results = [];

  for (const tc of cases) {
    const paramsPath  = `${tc.screenshotDir}/${tc.sanitizedName}_${tc.timestamp}_params.png`;
    const bodyPath    = `${tc.screenshotDir}/${tc.sanitizedName}_${tc.timestamp}_body.png`;
    const responsePath = `${tc.screenshotDir}/${tc.sanitizedName}_${tc.timestamp}_response.png`;

    try {
      // ── Step 1: Navigate to request via sidebar ──────────────────────────
      // Sidebar items use role="treeitem"; text = "{METHOD}{name}" e.g. "POSTLogin"
      const sidebarItem = page.locator('[role="treeitem"]')
        .filter({ hasText: tc.name })
        .first();
      await sidebarItem.click();
      await page.waitForTimeout(1500); // allow request panel to fully render

      // Scope all request-tab clicks to active-tab-content to avoid duplicate
      // selector error (Postman renders the tab strip twice in the DOM)
      const reqPanel = page.locator('[data-testid="active-tab-content"]');

      // ── Step 2: Screenshot 1 — PARAMS tab ────────────────────────────────
      await reqPanel.locator('[data-testid="request-editor-tab--params"]').click();
      // Wait until the tab's aria-selected flips to true
      await page.waitForFunction(
        () => !!document.querySelector('[data-testid="request-editor-tab--params"][aria-selected="true"]'),
        { timeout: 5000 }
      ).catch(() => {});
      await page.waitForTimeout(800); // allow panel content to paint
      await page.screenshot({ path: paramsPath });

      // ── Step 3: Screenshot 2 — BODY tab ──────────────────────────────────
      await reqPanel.locator('[data-testid="request-editor-tab--body"]').click();
      // Wait for Monaco editor to appear (body editor uses Monaco)
      await page.waitForFunction(
        () => {
          const m = document.querySelector('.monaco-editor.no-user-select');
          return m && m.clientHeight > 0;
        },
        { timeout: 5000 }
      ).catch(() => page.waitForTimeout(1000));
      await page.waitForTimeout(800);
      await page.screenshot({ path: bodyPath });

      // ── Step 4: Send request ──────────────────────────────────────────────
      // Send button: button[aria-label="Send"] (unique on page)
      await page.getByRole('button', { name: 'Send', exact: true }).click();

      // Wait for response status code in the ACTIVE tab only.
      // IMPORTANT: scope to [data-testid="active-tab-content"] — each open Postman
      // tab has its own hidden [data-testid="response-code"], causing waitForSelector
      // to time out because it finds the hidden one first.
      await page.locator('[data-testid="active-tab-content"] [data-testid="response-code"]')
        .waitFor({ state: 'visible', timeout: 25000 });
      await page.waitForTimeout(1000); // let response body fully render

      // ── Step 5: Screenshot 3 — RESPONSE pane ─────────────────────────────
      // Clip to the active response pane only
      const responsePaneBox = await page.locator('[data-testid="active-tab-content"] .response-viewer-pane')
        .first().boundingBox();
      await page.screenshot({
        path: responsePath,
        clip: responsePaneBox || undefined
      });

      // ── Step 6: Read actual response data ────────────────────────────────
      const rawStatus = await page.locator('[data-testid="active-tab-content"] [data-testid="response-code"]')
        .first().textContent();
      const statusCode = parseInt(rawStatus?.trim()) || 0;

      // Read response body from Monaco in the ACTIVE tab's response pane
      const responseBody = await page.evaluate(() => {
        const activeContent = document.querySelector('[data-testid="active-tab-content"]');
        if (!activeContent) return '';
        const pane = activeContent.querySelector('.response-viewer-pane');
        if (!pane) return '';
        const lines = [...pane.querySelectorAll('.view-line')];
        return lines.map(l => l.textContent).join('\n').trim().substring(0, 500);
      });

      results.push({
        name:             tc.name,
        row:              tc.row,
        nameCol:          tc.nameCol,
        actualCol:        tc.actualCol,
        resultCol:        tc.resultCol,
        statusCode:       statusCode,
        responseBody:     responseBody || '(see screenshot)',
        paramsScreenshot: paramsPath,
        bodyScreenshot:   bodyPath,
        responseScreenshot: responsePath,
        error:            ''
      });

    } catch (err) {
      results.push({
        name:             tc.name,
        row:              tc.row,
        nameCol:          tc.nameCol,
        actualCol:        tc.actualCol,
        resultCol:        tc.resultCol,
        statusCode:       0,
        responseBody:     '',
        paramsScreenshot: paramsPath,
        bodyScreenshot:   bodyPath,
        responseScreenshot: responsePath,
        error:            err.message
      });
    }
  }

  return JSON.stringify(results);
}
```

> **Why sidebar navigation instead of tab-bar switching:**
> Postman's top tab bar uses hashed CSS classes with no stable `data-testid`.
> Clicking a sidebar item that is already open in a tab simply switches to that tab
> (response is preserved). This is more reliable than tab-bar DOM matching.

> **Why not `fetch()` for response data:**
> `fetch()` from browser context is subject to CORS restrictions and bypasses
> Postman's environment variable resolution. DOM scraping from `.response-viewer-pane`
> reads exactly what Postman sent, including auth tokens resolved at runtime.

**Screenshot path rules:**
- Each test case produces **3 screenshots** — always, regardless of HTTP method:
  - `{screenshotDir}/{sanitizedName}_{yyyyMMdd_HHmmss}_params.png`
  - `{screenshotDir}/{sanitizedName}_{yyyyMMdd_HHmmss}_body.png`
  - `{screenshotDir}/{sanitizedName}_{yyyyMMdd_HHmmss}_response.png`
- `sanitizedName` = test case name with spaces and special chars replaced by `_`
- Timestamp = same value for all cases in one execution run (generated at start)
- `screenshotDir` = `screenshots/` relative to the xlsx file
- **NEVER** reuse screenshot paths from a previous run

### Step 8 — Execute batch

```
mcp__playwright__browser_run_code(code="<script from Step 7>")
```

Parse returned JSON array.

**If script fails on a specific test case:** The error is captured per-case in `results[i].error` — execution continues for remaining cases. Only retry if the script itself crashes (not a per-case error).

**If the whole script throws:** Check the error. Common fixes:
- `strict mode violation` on tab locator → `reqPanel.locator(...)` scope is missing — ensure `[data-testid="active-tab-content"]` scoping
- Sidebar item not found → verify the `tc.name` matches the treeitem text exactly (partial match required)
- Response timeout (>25s) → check if Postman environment variables are set correctly
- Fix and retry once. If it fails again → stop and report to user.

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

**4 columns:** A = Test Case Name, B = Params screenshot, C = Body screenshot, D = Response screenshot.
Each test case occupies 1 row with 3 embedded images side by side.

```bash
python3 -X utf8 -c "
import openpyxl, os, json
from openpyxl.drawing.image import Image as XLImage

data = json.loads('''RESULTS_JSON''')
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')

if 'Evidence' in wb.sheetnames:
    del wb['Evidence']
ws_ev = wb.create_sheet('Evidence')

ws_ev['A1'] = 'Test Case Name'
ws_ev['B1'] = 'Params'
ws_ev['C1'] = 'Body'
ws_ev['D1'] = 'Response'

COL_A_WIDTH = 40
IMG_WIDTH_PX = 550
IMG_HEIGHT_PX = 320
ws_ev.column_dimensions['A'].width = COL_A_WIDTH
ws_ev.column_dimensions['B'].width = IMG_WIDTH_PX / 7
ws_ev.column_dimensions['C'].width = IMG_WIDTH_PX / 7
ws_ev.column_dimensions['D'].width = IMG_WIDTH_PX / 7

for i, item in enumerate(data, start=2):
    ws_ev.cell(row=i, column=1).value = item['name']
    ws_ev.row_dimensions[i].height = IMG_HEIGHT_PX * 0.75

    # Column B — Params screenshot
    params_path = item.get('paramsScreenshot', '')
    if params_path and os.path.exists(params_path):
        img = XLImage(params_path)
        img.width = IMG_WIDTH_PX
        img.height = IMG_HEIGHT_PX
        ws_ev.add_image(img, f'B{i}')
    else:
        ws_ev.cell(row=i, column=2).value = 'Not captured'

    # Column C — Body screenshot
    body_path = item.get('bodyScreenshot', '')
    if body_path and os.path.exists(body_path):
        img = XLImage(body_path)
        img.width = IMG_WIDTH_PX
        img.height = IMG_HEIGHT_PX
        ws_ev.add_image(img, f'C{i}')
    else:
        ws_ev.cell(row=i, column=3).value = 'Not captured'

    # Column D — Response screenshot
    res_path = item.get('responseScreenshot', '')
    if res_path and os.path.exists(res_path):
        img = XLImage(res_path)
        img.width = IMG_WIDTH_PX
        img.height = IMG_HEIGHT_PX
        ws_ev.add_image(img, f'D{i}')
    else:
        ws_ev.cell(row=i, column=4).value = 'Not captured'

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

- Split into batches of up to 15 cases each
- Each batch = 1 `browser_run_code` call with the Step 7 script
- Collect all batch results, then write to xlsx in 1 Python call after all batches complete

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
- Each test case produces **3 screenshots** — always, all methods: `..._params.png`, `..._body.png`, `..._response.png`.
- Screenshot filenames: `{sanitizedName}_{yyyyMMdd_HHmmss}_{params|body|response}.png` (spaces and special chars → `_`).
- Screenshot tab clicks must be scoped to `[data-testid="active-tab-content"]` to avoid duplicate-element errors.
- After clicking any request tab, wait for `aria-selected="true"` + 800ms before screenshotting — never use fixed 300ms.
- After clicking Send, wait for `[data-testid="response-code"]` to appear (up to 25s) — never use `networkidle`.
- Response screenshot must be clipped to `.response-viewer-pane` bounding box.
- Navigate between test cases via sidebar `[role="treeitem"]` click — never via the requester tab bar.
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
