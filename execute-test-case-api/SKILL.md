---
name: execute-test-case-api
description: Execute API test cases from a Google Sheets spreadsheet using Postman web browser. Reads test rows, opens Postman web, sends each request, screenshots the response as evidence, validates against expected results, and writes PASS/FAIL back to the sheet with screenshots stored in a separate Evidence tab. Use when user says "execute api test", "run api test cases", "chạy test case api", or provides a Sheets URL with API test data.
---

# Execute Test Case — API

Reads API test cases from Google Sheets, executes each via **Postman web browser** (Playwright), captures a screenshot of the response as evidence, validates the result, and writes back to two sheets: the main test sheet (PASS/FAIL) and a separate **Evidence** tab (Test ID + screenshot).

Groups consecutive test cases by `Precondition Group` to reuse auth tokens — the login call runs **once per group**.

---

## Prerequisites

- **gsheets MCP** configured (`mcp__gsheets__*` tools available)
- **Playwright MCP** configured (`mcp__playwright__*` tools available)
- `curl` available in terminal (for precondition auth calls only)
- Google Sheet structured per the [API schema](references/test-case-schema.md)
- Postman account (for Postman web login — see [postman-web.md](references/postman-web.md))

---

## Workflow

### Step 0 — Parse spreadsheet URL

Extract `spreadsheetId` from the URL:
- `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit...` → segment between `/d/` and `/edit`

If not provided, ask for it.

---

### Step 0b — Optional: Range / filter

The user may optionally specify which test cases to run:
- **Range**: "run API-010 to API-025" → only rows where Test ID is in that range
- **List**: "run API-003, API-007, API-012" → only those specific IDs
- **Re-run failures**: "re-run failed cases" → only rows where column K = "FAIL"
- **Force re-run**: "re-run all" or `--force` → ignore already-executed check

If not specified → run all pending (non-executed) rows in order.

Store filter as `idFilter` (list of IDs, or null for all). Applied after Step 1 partitioning.

---

### Step 1 — Read test cases

```
mcp__gsheets__list_sheets(spreadsheetId)
```

- Default tab: `"API Tests"`. If not in the list → ask user which tab to use. **Do NOT guess.**

```
mcp__gsheets__get_sheet_data(spreadsheetId, sheetName=<confirmed tab>)
```

- Row 1 is header. Skip rows with empty column A.

**⛔ Schema validation — STOP if mismatch:**

After reading, inspect row 1 (column headers). Expected layout:

| Col | Expected header keyword |
|-----|------------------------|
| A | Test ID / ID |
| B | Title / Name |
| E | Method |
| F | URL |
| I | Expected Status |

If row 1 does NOT contain these keywords in roughly the right columns:
1. Print: `Found columns: [A="{val}", B="{val}", C="{val}", D="{val}", E="{val}", ...]`
2. **STOP. Ask user:**
   > "Sheet format không khớp schema mong đợi. Tìm thấy: [actual headers]. Đây có phải đúng tab không? Nếu không, hãy cho biết tên tab hoặc mapping cột."
3. **Do NOT attempt to auto-map, adapt, or infer** column meanings from content. Wait for explicit user confirmation before continuing.

Column mapping (after schema confirmed):

| Col | Field | Notes |
|-----|-------|-------|
| A | Test ID | e.g. `API-001` |
| B | Title | Short description |
| C | Precondition Group | Optional. Consecutive same-value rows share auth state |
| D | Precondition Steps | JSON array — auth setup (login call). Executed once per group via curl |
| E | HTTP Method | GET / POST / PUT / PATCH / DELETE |
| F | URL | Full endpoint URL |
| G | Headers | JSON object or empty |
| H | Request Body | JSON payload or empty |
| I | Expected Status | Numeric HTTP status code |
| J | Expected Response | JSONPath assertions |
| K | Result | **Agent writes**: PASS / FAIL / ERROR |
| L | Error Message | **Agent writes**: failure detail or empty |
| M | Response Body | **Agent writes**: actual response (truncated 500 chars) |
| N | Executed At | **Agent writes**: ISO 8601 timestamp |

**Skip already-executed rows:**
After reading, partition rows into two lists:
- `pendingRows` — rows where column K is empty (not yet executed)
- `doneRows` — rows where column K is non-empty (already have results)

If user explicitly passes `--force` or says "re-run all" → use all rows as `pendingRows`.
Otherwise → only execute `pendingRows`. Print at start:
```
Loaded {total} test cases: {pending} pending, {done} already executed (skipping)
```
All subsequent steps operate on `pendingRows` only.

---

### Step 2 — Prepare Evidence sheet

Read test cases first (Step 1 must complete before this step).

Check if an `"Evidence"` tab exists:
```
mcp__gsheets__list_sheets(spreadsheetId)
```

If not found, create it, write header, then **pre-populate column A with all test case IDs** (from `pendingRows` + `doneRows`, in original order):
```
mcp__gsheets__create_sheet(spreadsheetId, "Evidence")
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "A1:B1", [["Test ID", "Screenshot"]])
# Pre-populate column A with all test IDs
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "A2:A{n+1}", [[id] for id in allTestIds])
```

If Evidence **already exists**, read current content to find which rows already have screenshots (column B non-empty) — skip re-writing those.

**Always look up Evidence row by scanning column A for the testId** — never assume sequential order.

---

### Step 3 — Group by Precondition Group

Group consecutive rows by column C value. Empty C → solo group. Non-consecutive same names → separate instances.

```
API-001  group=login-admin  → Group A (execute preconditions)
API-002  group=login-admin  → Group A (reuse token)
API-003  group=login-guest  → Group B (new preconditions)
API-004  group=             → Solo
```

---

### Step 4 — Open Postman web (once per skill invocation)

```
mcp__playwright__browser_navigate("https://web.postman.co")
```

Check login state via snapshot. If login screen appears → follow [postman-web.md](references/postman-web.md) login instructions. Once on workspace, open a new HTTP request tab — this single tab is reused for all test cases (just update fields each time).

**⛔ Environment check — STOP if missing:**

After reaching the workspace, take a snapshot and check the environment selector (top-right area, shows current environment name or "No environment"):

- If it shows **"No environment"** AND any test case URL or header contains `{{variable}}` syntax → **STOP. Ask user:**
  > "Postman chưa chọn environment. Một số request dùng `{{variables}}` (e.g. `{{serviceUrl}}`, `{{token}}`). Vui lòng chọn environment phù hợp trong Postman, hoặc cung cấp giá trị thực tế (base URL + token) để tôi điền trực tiếp."
- Wait for user to either select an environment or provide literal values. **Do NOT proceed with unresolved `{{variables}}`.**

---

### Step 5 — Execute each group

#### 5a — Run Precondition Steps via curl (once per group)

Take column D from the group's first row. Execute each auth step via curl to capture variables (e.g., `{{token}}`):

```json
[
  {
    "action": "http",
    "method": "POST",
    "url": "https://api.example.com/auth/login",
    "headers": {"Content-Type": "application/json"},
    "body": {"username": "admin", "password": "secret"},
    "capture": {"token": "$.data.accessToken"}
  }
]
```

Build curl command, execute, capture variables from response body using JSONPath. Store as group-scoped variables.

If precondition fails → mark all cases in group as ERROR: `"Precondition failed: {detail}"`.
Close browser immediately: `mcp__playwright__browser_close()`
Then skip to next group (re-open browser for next group).

#### 5b — Execute each test case in Postman web

For each test row:

**5b-1: Variable substitution**

Replace `{{variableName}}` in columns F, G, H with captured group variables.

**5b-2: Configure request in Postman**

Using Playwright, update the open Postman request tab:

1. Set method — take snapshot, find the method dropdown (currently showing GET/POST/etc.), click and select the correct method from column E
2. Clear and fill URL field with column F value
3. Headers (column G non-empty):
   - Click "Headers" tab in Postman
   - Add each key/value pair (snapshot → find key/value input rows → fill)
4. Body (column H non-empty):
   - Click "Body" tab → select "raw" mode → select "JSON" from format dropdown
   - Clear existing content, paste body JSON
5. Click **Send**

See [postman-web.md](references/postman-web.md) for detailed Postman UI navigation.

**5b-3: Wait for response, take screenshot**

After clicking Send:
- Wait for the response panel to show a status code — use `mcp__playwright__browser_wait_for` watching for the status indicator element (snapshot to identify it)
- Take screenshot immediately:

```
mcp__playwright__browser_take_screenshot(
  type="png",
  filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png"
)
```

**5b-4: Read response from Postman UI**

Take snapshot. From the response panel extract:
- **Status code**: find text matching a 3-digit HTTP status pattern (e.g., "200 OK", "401 Unauthorized") → parse numeric part
- **Response body**: find the response body content area → read text content

If status code cannot be read from UI → mark ERROR: `"Could not read response status from Postman UI"`.

**5b-5: Validate response**

1. Compare extracted status code vs column I (Expected Status) → mismatch → FAIL
2. If column J is non-empty: run each JSONPath assertion against extracted response body → any mismatch → FAIL
3. All pass → PASS

See [execution-rules.md](references/execution-rules.md) for JSONPath operator reference.

**5b-6: Write results**

Write to test sheet immediately:
```
mcp__gsheets__update_cells(spreadsheetId, "API Tests", rowIndex, {
  K: "PASS" | "FAIL" | "ERROR",
  L: errorMessage or "",
  M: responseBody (truncated 500 chars),
  N: ISO timestamp
})
```

Write to Evidence sheet — find the row whose column A matches `testId`, then write screenshot path to column B:
```
# Find Evidence row by testId (from the pre-populated column A)
evidenceRow = lookup row in Evidence where A == testId

mcp__gsheets__update_cells(spreadsheetId, "Evidence", f"B{evidenceRow}",
  [[screenshotPath]]
)
```

**After last case in group completes** (pass or fail), close the browser context:
```
mcp__playwright__browser_close()
```
Then re-open for the next group:
```
mcp__playwright__browser_navigate("https://web.postman.co")
```
(Login state may be preserved by browser profile — take snapshot to verify, re-login if needed.)

#### 5c — After all groups complete

Browser is already closed after the last group — no additional close needed.

---

### Step 6 — Print summary

```
=== API Test Execution Summary ===
Total:  {n}
PASS:   {n}  ✓
FAIL:   {n}  ✗
ERROR:  {n}  ⚠

Screenshots saved to: screenshots/
Evidence sheet: "Evidence" tab in the spreadsheet

FAILED cases:
  - API-003: Expected 200, got 401
FAILED cases:
  - API-006: Precondition failed: login returned 500
```

---

## Guardrails

- **Never modify** columns A–J. Only write to K, L, M, N.
- **Never skip writing results** — even on ERROR.
- **Never re-execute** rows where column K is non-empty unless explicitly instructed.
- **Always close Postman browser** after all groups complete.
- Screenshot filenames must not contain spaces: use `{testId}_{yyyyMMdd_HHmmss}.png`.

## ⛔ Anti-loop rules

These situations require an **immediate STOP + ask user** — never attempt to auto-adapt or analyze further:

| Situation | Action |
|-----------|--------|
| Sheet tab `"API Tests"` not found | List sheets → ask user which tab |
| Row 1 headers don't match expected schema | Print found headers → ask user to confirm mapping |
| Postman shows "No environment" with `{{variables}}` in requests | Ask user to select environment or provide literal values |
| Cannot determine Test ID or Method from a row | Skip that row, log `"Could not parse row {n}"`, continue |
| Same blocker occurs 2+ times in a row | STOP all execution, report to user |

**Analysis limit**: If you catch yourself re-reading the same sheet data or re-examining the same snapshot more than twice to answer the same question → STOP and ask the user instead.
