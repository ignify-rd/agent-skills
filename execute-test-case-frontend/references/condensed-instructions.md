# Frontend Test Batch — Condensed Execution Guide

Single-file reference for subagents. Do NOT read other reference files.

---

## Core pattern: snapshot → ref → act

Playwright MCP actions (`click`, `fill`, `select`) require an element `ref` from the accessibility snapshot. Always:
1. `mcp__playwright__browser_snapshot` → get current page state
2. Find element by matching against snapshot output
3. Use `ref` in the action call

**Do NOT** use CSS selectors directly in action parameters.

### Tool mapping

| Action | Tool | Key params |
|--------|------|------------|
| `goto` / URL | `mcp__playwright__browser_navigate` | `url` |
| `back` | `mcp__playwright__browser_navigate_back` | — |
| `click` / nhấn / bấm | `mcp__playwright__browser_click` | `ref`, `element` |
| `fill` (single field) / nhập / điền | `mcp__playwright__browser_type` | `ref`, `text` |
| `fill_form` (multiple fields) | `mcp__playwright__browser_fill_form` | `fields: [{name, type, ref, value}]` |
| `select` | `mcp__playwright__browser_select_option` | `ref`, `values` |
| `wait_for` / chờ | `mcp__playwright__browser_wait_for` | `selector` or `time`, `timeout` |
| `hover` / di chuột | `mcp__playwright__browser_hover` | `ref` |
| `press_key` | `mcp__playwright__browser_press_key` | `key` |
| `scroll` / cuộn | `mcp__playwright__browser_evaluate` | `window.scrollBy(0, 300)` |
| `snapshot` | `mcp__playwright__browser_snapshot` | — |
| `handle_dialog` | `mcp__playwright__browser_handle_dialog` | `accept: true/false` |

---

## 1 — Execute Precondition Steps

**Standard format** (JSON array):
Execute each action using the tool mapping above. Example: `goto` → `browser_navigate`, `fill` → snapshot + `browser_type`, etc.

**Zephyr format** (human-readable text):
1. Extract URL if present → `browser_navigate(url=...)`
2. Extract login credentials (email regex + password after `mật khẩu`/`password:`) → fill form + click login
3. Wait: `browser_wait_for(time=2)`
4. Take snapshot to confirm page loaded

After preconditions succeed → record `entryUrl` (current URL from snapshot).

**On failure** → mark ALL cases as ERROR: `"Precondition failed: {detail}"`, write results, close browser, return.

---

## 2 — Execute test cases (loop)

Initialize result collectors:

```
results = []       # [{sheetRow, result, error, actualResult}]
screenshots = []   # [{testId, filename}]
evidenceData = []  # [{evidenceRow, directUrl}]
```

For each test case:

### 2a — Reset to entry state (skip for first case)

```
mcp__playwright__browser_navigate(url=entryUrl)
mcp__playwright__browser_wait_for(time=2)
```

If reset fails → ERROR for this case + all remaining: `"Entry reset failed"`. Close browser, return.

### 2b — Execute test steps

*Standard format* (JSON array):
Execute each action using tool mapping. Always snapshot before `click`/`fill` to get refs.

*Zephyr format* (numbered steps):
Parse numbered steps. For each step:
1. Take snapshot
2. Determine action from text:
   - URL → `browser_navigate`
   - "click"/"nhấn"/"bấm" → `browser_click`
   - "nhập"/"điền"/"enter" → `browser_type`
   - "chờ"/"wait" → `browser_wait_for(time=2)`
   - "scroll"/"cuộn" → `browser_evaluate(script="window.scrollBy(0, 300)")`
   - "hover"/"di chuột" → `browser_hover`

On step failure → capture screenshot, record error, stop further steps for this case.

### 2c — Validate result

*Standard format* (JSON assertions):
Take fresh snapshot. Evaluate each assertion:
- `visible` → element in snapshot, not hidden
- `not_visible` → element absent or hidden
- `text_contains` → element text contains value
- `text_equals` → element text exactly equals value
- `url_contains` → page URL contains value
- `url_equals` → page URL exactly equals value
- `count` → matching element count equals expected

*Zephyr format* (human-readable expected result):
Take snapshot. Check if key phrases from Expected Result appear in snapshot's visible text. If expected mentions URL → also check `browser_evaluate("window.location.href")`.

### 2d — Capture screenshot (always, regardless of result)

```
mcp__playwright__browser_take_screenshot(filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png", type="png")
```

Add to screenshots list: `{testId, filename}`

### 2e — Collect result (do NOT write yet)

*Standard format:*
```
results.push({sheetRow, result: "PASS"|"FAIL"|"ERROR", error: errorMsg, screenshot: filename, timestamp: isoTimestamp})
```

*Zephyr format:*
```
results.push({sheetRow, result: "PASS"|"FAIL"|"ERROR", actualResult: actualResultText, screenshot: filename})
```

---

## 3 — Batch upload screenshots

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

## 4 — Batch write results to sheets

### Standard format — test sheet (columns G–J):

For contiguous rows, use a single range:
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "G{firstRow}:J{lastRow}", [
  [result1, error1, screenshot1, ts1],
  [result2, error2, screenshot2, ts2],
  ...
])
```

### Zephyr format — test sheet:

Write Actual Result + Result status. For each test case:
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "{actualResultCol}{sheetRow}", [[actualResultText]])
mcp__gsheets__update_cells(spreadsheetId, sheetName, "{resultCol}{sheetRow}", [[result]])
```

Batch contiguous rows where possible.

### Evidence sheet (both formats):

Write `=IMAGE()` formulas. Batch contiguous evidence rows:
```
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "B{firstRow}:B{lastRow}", [
  ['=IMAGE("{directUrl1}")'],
  ['=IMAGE("{directUrl2}")'],
  ...
])
```

---

## 5 — Close browser

```
mcp__playwright__browser_close()
```

Always close, even if errors occurred.

---

## 6 — Return summary

```
Batch {startId}–{endId}: {pass} PASS, {fail} FAIL, {error} ERROR
[For each FAIL/ERROR]:
  - {testId}: {errorMessage}
```

---

## Error classification

| Condition | Result | Error message |
|-----------|--------|---------------|
| Precondition step failed | ERROR | `Precondition failed: step {n} — {detail}` |
| Entry state reset failed | ERROR | `Entry reset failed: {detail}` |
| Browser step failed/timed out | ERROR | `Step {n} failed: {action} on "{selector}" — {detail}` |
| Assertion failed | FAIL | `Assertion failed: {type} on "{selector}" — {detail}` |
| All assertions passed | PASS | (empty) |

## Error recovery patterns

### Element not found
If element ref cannot be located in snapshot:
- Retry `mcp__playwright__browser_snapshot` once (page may still be loading)
- If still not found → step ERROR: `"Element not found: {selector}"`

### Navigation timeout
If `mcp__playwright__browser_wait_for` times out:
- Step ERROR: `"Timeout waiting for: {selector} ({timeout}ms)"`
- Capture screenshot before recording the error

### Unexpected dialog
If a dialog appears unexpectedly:
- Call `mcp__playwright__browser_handle_dialog(accept=False)` to dismiss
- Continue execution

### Browser crash / session lost
If Playwright tools return errors suggesting the browser is closed:
- Step ERROR: `"Browser session lost"`
- Mark remaining cases in the batch as ERROR with same message
- Close browser, return summary

## Guardrails

- NEVER modify user-input columns (A–F Standard, test data columns Zephyr).
- NEVER skip writing results — even on ERROR.
- Always close browser when done.
- Screenshot filenames: `{testId}_{yyyyMMdd_HHmmss}.png` (no spaces).
- NEVER write temp/helper scripts to disk.
