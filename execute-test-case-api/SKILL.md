---
name: execute-test-case-api
description: Execute API test cases from Google Sheets using Postman web. Reads test rows, opens Postman web for user to load their collection, sends each request, captures the actual response, updates the Expected Result cell with the real response, validates status code, takes a screenshot, and writes PASS/FAIL back to the sheet. Triggers when user says "execute api test", "run api test cases", "chạy test case api", or provides a Sheets URL with API test data.
---

# Execute Test Case — API

Reads API test cases from Google Sheets, executes each via **Postman web browser** (Playwright), captures the real response, updates the Expected Result cell, validates status, captures screenshot, and writes results back.

**Batch size:** 10-15 cases per subagent.
**Execution:** Sequential (1 Playwright profile).

---

## Prerequisites

- **gsheets MCP** configured
- **Playwright MCP** configured
- `curl` available in terminal (for precondition auth calls only)
- **Google Drive OAuth** — `~/.gdrive-mcp/` credentials for screenshot upload
- Sheet tab: `API Tests`

---

## ⛔ Temp File Rules

**NEVER** write helper/temp scripts (`_*.py`, `_*.ps1`, `_check_*.py`, etc.) to disk. Use `python3 -X utf8 -c "..."` inline, or Read/Edit/Write tools.

---

## Workflow

### Step 1 — Read test cases

```
mcp__gsheets__list_sheets(spreadsheetId)
mcp__gsheets__get_sheet_data(spreadsheetId, sheetName="API Tests")
```

**Column layout (fixed):**

| Col | Field | Notes |
|-----|-------|-------|
| A | Test ID | e.g. `API-001` |
| B | Title | Short description |
| C | Precondition Group | Consecutive same-value rows share auth state |
| D | Precondition Steps | JSON array — auth setup via curl. Execute once per group |
| E | HTTP Method | GET / POST / PUT / PATCH / DELETE |
| F | URL | Full endpoint URL |
| G | Headers | JSON object or empty |
| H | Request Body | JSON payload or empty |
| I | Expected Status | Numeric HTTP status code (e.g. 200, 400) |
| J | Expected Result | Template with status + sample JSON. **Agent will replace with actual response** |
| K | Result | Agent writes: PASS / FAIL / ERROR |
| L | Error Message | Agent writes |
| M | Response Body | Agent writes: actual response (truncated 500 chars) |
| N | Executed At | Agent writes: ISO 8601 timestamp |

Skip rows where column A is empty. Pending = column K empty.

Print at start:
```
Loaded {total} test cases: {pending} pending, {done} already executed (skipping)
```

---

### Step 2 — Filter (optional)

User may specify: range (`API-010 to API-025`), list (`API-003, API-007`), re-run failures. If not specified → run all pending.

---

### Step 3 — Group + batch

Group consecutive rows by column C (Precondition Group). Empty C → solo group.

Split into batches of **10-15 cases** each.

---

### Step 4 — Pre-load instructions once

Store these as `apiInstructions`:

```
## Preconditions (curl)
If precondition steps provided, execute each via curl:
  STATUS=$(curl -s -o /tmp/tc_resp.txt -w "%{http_code}" -X {METHOD} "{URL}" {HEADER_FLAGS} {BODY_FLAG} --max-time 30)
  BODY=$(cat /tmp/tc_resp.txt)
Extract captured variables from response JSON. Store in group variable map.
On failure → ERROR all cases in batch, write results, return.
Retry once on curl exit 6/7/28, wait 2s before retry.

## Variable substitution
Before each test case, replace {{varName}} in URL, headers, body with captured variables.
Missing variable → ERROR.

## Postman web navigation
- Navigate to https://web.postman.co
- If login screen → tell user: "Postman web requires login. Please log in, then confirm to continue."
- After user confirms → snapshot to verify login succeeded. If still login → ERROR: "Postman not logged in", return.
- Once on workspace → click "+" to open new HTTP request tab. Reuse this tab for ALL cases.
- If {{variable}} in request AND Postman shows "No environment" → ERROR: "Postman chưa chọn environment", return.

## Sending a request
1. Method: click method dropdown → select correct method
2. URL: triple-click URL bar → type new URL
3. Headers: click "Headers" tab → clear previous rows → add each key/value
4. Body: click "Body" tab → select "raw" + "JSON" → Ctrl+A → paste body. Empty body → select "none"
5. Click Send
6. Wait for response panel to show status code (wait_for, timeout 15000ms)
7. Screenshot:
   mcp__playwright__browser_take_screenshot(type="png", filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png")

## Reading response
- Take snapshot. Extract status code: text matching \\d{3} pattern (e.g. "200 OK") → parse numeric part
- Extract response body: from response body content area in snapshot
- If unreadable:
   mcp__playwright__browser_evaluate(script="
     const el = document.querySelector('[data-testid=\"response-body\"]') || document.querySelector('.response-body-container');
     return el ? el.innerText : null;
   ")
  Still unreadable → ERROR: "Could not read response from Postman UI"
```

---

### Step 5 — Execute batches via subagent

Each batch = separate subagent (fresh context, no token accumulation).

**Subagent prompt:**
```
Agent(
  description="API test batch {batchNum}",
  prompt="""
## Execution Instructions

{apiInstructions}

---

## Data

skillDir: {skillDir}
spreadsheetId: {spreadsheetId}
sheetName: {sheetName}

### Precondition Steps (execute once via curl before test cases):
{preconditionStepsJSON or "None — no preconditions for this batch"}

### Test cases to execute:
| Row | Test ID | Method | URL | Headers | Body | Expected Status |
|-----|---------|--------|-----|---------|------|-----------------|
| {row} | {id} | {method} | {url} | {headers} | {body} | {status} |
...

---

## Workflow

### 1 — Run Preconditions

If precondition steps provided → execute via curl. Extract and store captured variables.
On failure → mark ALL cases as ERROR: "Precondition failed: {detail}", write results, return.

### 2 — Open Postman Web

Navigate to https://web.postman.co. Handle login if needed (see instructions).
Open a new HTTP request tab (+). Verify ready.

### 3 — Execute each test case

Initialize:
- results = []
- screenshots = []

For each test case:

**3a — Substitute variables** in URL, headers, body using captured variables.
Missing variable → ERROR for this case.

**3b — Configure request in Postman**:
- Set method, URL, headers, body
- Click Send
- Wait for response (timeout 15000ms)

**3c — Screenshot immediately** after response loads:
```
mcp__playwright__browser_take_screenshot(type="png", filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png")
```

**3d — Read response**:
- Extract status code (numeric)
- Extract response body text (truncate to 500 chars, append "..." if truncated)

**3e — Update Expected Result cell**:
Write the ACTUAL response to column J (Expected Result column). Format:
```
Status: {actualStatus}
Response:
{actualResponseBody}
```

**3f — Validate**:
- Compare actual status vs expected status (column I)
- Mismatch → FAIL: "Expected {expected}, got {actual}"
- Match → PASS

**3g — Collect result** (do NOT write yet):
```
results.push({
  row: sheetRow,
  result: "PASS" | "FAIL" | "ERROR",
  error: errorMessage or "",
  body: responseBody,
  timestamp: "YYYY-MM-DDTHH:mm:ssZ"
})
screenshots.push({testId, filename})
```

### 4 — Upload screenshots

```
python3 {skillDir}/scripts/gdrive_batch_upload.py screenshots/{file1} screenshots/{file2} ...
```

Output: JSON array with {name, id, direct} per file. Map `direct` URL to each test case by filename.

### 5 — Write results to sheet

**Test sheet (columns K–N):**
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "K{firstRow}:N{lastRow}", [
  [result1, error1, body1, ts1],
  [result2, error2, body2, ts2],
  ...
])
```

**Evidence sheet:**
If "Evidence" tab exists → read column A to find row for each testId.
If not exists → create it with header "Test ID | Screenshot", pre-populate column A with all testIds.
Write `=IMAGE("{directUrl}")` to column B at the matched row for each test case.

Cleanup: `rm -f /tmp/tc_resp.txt`

### 6 — Close browser
```
mcp__playwright__browser_close()
```

### 7 — Return summary
```
Batch {batchNum}: {pass} PASS, {fail} FAIL, {error} ERROR
FAILED: {testId}: {errorMessage}
ERROR: {testId}: {errorMessage}
```
"""
)
```

**Execute batches sequentially.** After each subagent returns, collect counts for final summary.

---

### Step 6 — Print summary

```
=== API Test Summary ===
Total:  {n}
PASS:   {n}  ✓
FAIL:   {n}  ✗
ERROR:  {n}  ⚠
Screenshots: screenshots/
Evidence: Evidence tab in spreadsheet
```

---

## Error classification

| Condition | Result | Message |
|-----------|--------|---------|
| Precondition curl failed | ERROR | `Precondition failed: {detail}` |
| Postman not logged in | ERROR | `Postman not logged in` |
| Variable not found | ERROR | `Variable {{varName}} not defined` |
| Status mismatch | FAIL | `Expected {expected}, got {actual}` |
| Could not read response | ERROR | `Could not read response from Postman UI` |
| Response CORS blocked | ERROR | `CORS blocked — API does not allow browser requests` |
| All checks pass | PASS | (empty) |

---

## Guardrails

- **NEVER** modify columns A–J (except J will be overwritten with actual response — this is intentional).
- **NEVER** skip writing results.
- **NEVER** re-execute rows with Result already set unless instructed.
- **ALWAYS** close browser after all groups complete.
- Screenshot filenames: `{testId}_{yyyyMMdd_HHmmss}.png` (no spaces).
- **NEVER** write temp scripts to disk.
- Retry curl once on exit 6/7/28. Never retry on FAIL.

## ⛔ Anti-loop

Stop and ask user if:
- "API Tests" tab not found
- Row 1 headers don't match expected schema
- Postman requires login and user cannot confirm
- Same blocker occurs 3+ times in a row