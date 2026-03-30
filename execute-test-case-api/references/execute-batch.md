# Execute API Test Batch

Instructions for a subagent executing a batch of API test cases. The subagent receives test case data in its prompt and executes them via Postman web browser.

Read these companion files for detailed instructions:
- [postman-web.md](postman-web.md) — Postman UI navigation (login, request setup, response reading)
- [execution-rules.md](execution-rules.md) — curl templates, variable substitution, JSONPath validation

---

## Workflow

### 1 — Run Precondition Steps via curl

If precondition steps are provided in the prompt data, execute each step via curl to capture variables (token, userId, etc.).

**curl template** (see execution-rules.md for full details):
```bash
STATUS=$(curl -s -o /tmp/tc_response.txt -w "%{http_code}" -X {METHOD} "{URL}" {HEADER_FLAGS} {BODY_FLAG} --max-time 30)
BODY=$(cat /tmp/tc_response.txt)
```

Capture variables from the response using JSONPath paths specified in `capture` fields. Store in a group-scoped variable map.

**On failure** → mark **all** test cases in this batch as ERROR (`"Precondition failed: {detail}"`), write results to sheet immediately, skip Postman, and return summary.

If no precondition steps → skip to step 2.

---

### 2 — Open Postman web

```
mcp__playwright__browser_navigate("https://web.postman.co")
```

- Take snapshot. If login screen appears → notify user: `"Postman web requires login."` Wait for confirmation.
- Once on workspace, open a new HTTP request tab (click "+" in tab bar). This tab is **reused for all test cases** in this batch.
- **Environment check**: If any test URL/header/body contains `{{variable}}` syntax AND Postman shows "No environment" → report error: `"Postman chưa chọn environment"` and return.

---

### 3 — Execute each test case

For each test case row (in order):

**3a — Variable substitution**

Replace `{{varName}}` in URL, headers, body with captured precondition variables. If a variable is not found → ERROR: `"Variable {{varName}} not defined"`.

**3b — Configure request in Postman** (see postman-web.md):

1. Set method — click method dropdown, select correct method
2. Clear URL field (triple-click to select all), type new URL
3. Headers — click "Headers" tab, clear previous non-default rows, add each new key/value pair
4. Body — click "Body" tab, select "raw" + "JSON", clear + paste body JSON. If empty body → select "none"
5. Click **Send**

**3c — Wait for response + screenshot**

- Wait for response panel to show a status code (use `mcp__playwright__browser_wait_for`, timeout 15000ms)
- Take screenshot immediately:
```
mcp__playwright__browser_take_screenshot(type="png", filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png")
```

**3d — Read response from Postman UI**

Take snapshot. Extract:
- **Status code**: text matching `\d{3}` pattern (e.g., "200 OK") → parse numeric part
- **Response body**: read from the response body content area

If unreadable → ERROR: `"Could not read response from Postman UI"`.

**3e — Validate** (see execution-rules.md):

1. Compare status code vs Expected Status → mismatch → FAIL immediately
2. If Expected Response is non-empty → evaluate JSONPath assertions in order → first failure → FAIL
3. All pass → PASS

**3f — Write results immediately**

Test sheet (columns K–N):
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "K{row}:N{row}", [[
  "PASS"|"FAIL"|"ERROR",
  errorMessage or "",
  responseBody (truncated 500 chars, append "..." if truncated),
  "YYYY-MM-DDTHH:mm:ssZ"
]])
```

Evidence sheet — find the row where column A = testId, write screenshot path to column B:
```
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "B{evidenceRow}", [[screenshotPath]])
```

Clean up: `rm -f /tmp/tc_response.txt`

---

### 4 — Close browser

```
mcp__playwright__browser_close()
```

Always close, even if errors occurred.

---

### 5 — Return summary

Report back to the main conversation:
```
Batch {startId}–{endId}: {pass} PASS, {fail} FAIL, {error} ERROR
[For each FAIL/ERROR]:
  - {testId}: {errorMessage}
```

---

## Guardrails

- **Never modify** columns A–J. Only write to K, L, M, N.
- **Never skip** writing results — even on ERROR.
- **Always close** browser when done.
- Screenshot filenames: `{testId}_{yyyyMMdd_HHmmss}.png` (no spaces).
- Retry once on curl errors (exit 6, 7, 28). Wait 2s before retry.
- Never retry on FAIL (assertion mismatch).
