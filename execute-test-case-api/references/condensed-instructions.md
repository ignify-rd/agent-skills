# API Test Batch — Condensed Execution Guide

Single-file reference for subagents. Do NOT read other reference files.

---

## 1 — Preconditions (curl)

If precondition steps are provided, execute each via curl:

```bash
STATUS=$(curl -s -o /tmp/tc_response.txt -w "%{http_code}" -X {METHOD} "{URL}" {HEADER_FLAGS} {BODY_FLAG} --max-time 30)
BODY=$(cat /tmp/tc_response.txt)
```

- `{HEADER_FLAGS}` = one `-H "Key: Value"` per header
- `{BODY_FLAG}` = `-d '{json}'` if body non-empty; omit if empty
- Extract `capture` variables via JSONPath from response body. Store in variable map.
- On failure → mark ALL cases in batch as ERROR: `"Precondition failed: {detail}"`, write results, return.
- Retry once on curl exit 6/7/28, wait 2s before retry.

### Variable substitution

Before executing each test case, replace `{{varName}}` in URL, headers, body with captured variables. Order: URL → headers → body. Missing variable → ERROR.

---

## 2 — Open Postman

```
mcp__playwright__browser_navigate("https://web.postman.co")
```

- Take snapshot. Login screen → tell user: `"Postman web requires login."` Wait for confirmation.
- After user confirms → take snapshot again to verify login succeeded. If still on login screen → mark all test cases as ERROR: `"Postman not logged in"` and return.
- Once on workspace → click "+" to open new HTTP request tab. Reuse this tab for ALL cases.
- If any URL/header/body has `{{variable}}` AND Postman shows "No environment" → ERROR: `"Postman chưa chọn environment"`, return.

---

## 3 — Execute test cases (loop)

Initialize result collectors:

```
results = []       # [{row, result, error, body, timestamp}]
screenshots = []   # [{testId, filename}]
evidenceData = []  # [{evidenceRow, directUrl}]
```

For each test case:

### 3a — Configure request in Postman

1. **Method**: click method dropdown → select correct method
2. **URL**: triple-click URL bar to select all → type new URL
3. **Headers**: click "Headers" tab → remove previous non-default rows → add each key/value
4. **Body**: click "Body" tab → select "raw" + "JSON" → Ctrl+A → paste body. Empty body → select "none"
5. Click **Send**

### 3b — Wait for response + screenshot

- `mcp__playwright__browser_wait_for` — wait for status code to appear, timeout 15000ms
- Screenshot:
```
mcp__playwright__browser_take_screenshot(type="png", filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png")
```
- Add to screenshots list: `{testId, filename}`

### 3c — Read response

Take snapshot. Extract:
- **Status code**: text matching `\d{3}` (e.g. "200 OK") → parse numeric part
- **Response body**: from response body content area

If unreadable, try:
```
mcp__playwright__browser_evaluate(script="
  const el = document.querySelector('[data-testid=\"response-body\"]') || document.querySelector('.response-body-container');
  return el ? el.innerText : null;
")
```
Still unreadable → ERROR: `"Could not read response from Postman UI"`.

### 3d — Validate

1. Status code vs Expected Status → mismatch → FAIL: `"Expected {expected}, got {actual}"` (skip JSONPath)
2. If Expected Response non-empty → evaluate JSONPath assertions in order:
   - Empty body + assertions → ERROR: `"Empty response body"`
   - Non-JSON body + assertions → ERROR: `"Response is not JSON"`
   - Operators: `EXISTS`, `NOT_EXISTS`, `EQUALS`, `CONTAINS`, `STARTS_WITH`, `MATCHES`, `GREATER_THAN`, `LESS_THAN`
   - First assertion failure → FAIL, stop evaluating
3. All pass → PASS

### 3e — Collect result (do NOT write yet)

```
results.push({
  row: sheetRow,
  result: "PASS" | "FAIL" | "ERROR",
  error: errorMessage or "",
  body: responseBody (truncated 500 chars, "..." if truncated),
  timestamp: "YYYY-MM-DDTHH:mm:ssZ"
})
```

---

## 4 — Batch upload screenshots

After ALL test cases are done, upload all screenshots in one call:

```bash
python3 {skillDir}/scripts/gdrive_batch_upload.py screenshots/{file1} screenshots/{file2} ...
```

Output: JSON array with `{name, id, direct}` per file. Map each `direct` URL to the corresponding test case by filename.

Build evidence data:
```
for each upload result:
  evidenceData.push({evidenceRow, directUrl: result.direct})
```

---

## 5 — Batch write results to sheets

### 5a — Test sheet results

Write all results at once. For contiguous rows, use a single range:
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "K{firstRow}:N{lastRow}", [
  [result1, error1, body1, ts1],
  [result2, error2, body2, ts2],
  ...
])
```

If rows are non-contiguous, group contiguous ranges and write each group:
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "K{row}:N{row}", [[result, error, body, ts]])
```

### 5b — Evidence sheet

For each test case, write `=IMAGE()` formula:
```
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "B{evidenceRow}", [['=IMAGE("{directUrl}")']])
```

If multiple evidence rows are contiguous, batch them:
```
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "B{firstRow}:B{lastRow}", [
  ['=IMAGE("{url1}")'],
  ['=IMAGE("{url2}")'],
  ...
])
```

Clean up: `rm -f /tmp/tc_response.txt`

---

## 6 — Close browser

```
mcp__playwright__browser_close()
```

Always close, even if errors occurred.

---

## 7 — Return summary

```
Batch {startId}–{endId}: {pass} PASS, {fail} FAIL, {error} ERROR
[For each FAIL/ERROR]:
  - {testId}: {errorMessage}
```

---

## Guardrails

- NEVER modify columns A–J. Only write K, L, M, N.
- NEVER skip writing results — even on ERROR.
- Always close browser when done.
- Screenshot filenames: `{testId}_{yyyyMMdd_HHmmss}.png` (no spaces).
- NEVER write temp/helper scripts to disk.
- Retry once on curl exit 6/7/28. Never retry on FAIL (assertion mismatch).
