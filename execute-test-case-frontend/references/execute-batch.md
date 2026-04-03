# Execute Frontend Test Batch

Instructions for a subagent executing a batch of frontend test cases via Playwright browser automation. The subagent receives test case data and format details in its prompt.

**Performance note:** This file is kept as a fallback reference. For optimal speed, the main agent embeds [condensed-instructions.md](condensed-instructions.md) directly into the subagent prompt — subagents should NOT need to read this file. If you were told to read this file, follow the workflow below. Otherwise, follow the instructions already in your prompt.

Read this companion file only if NOT using condensed instructions:
- [browser-control.md](browser-control.md) — Playwright MCP tool reference, snapshot-ref-act pattern, assertion evaluation

---

## Workflow

### 1 — Execute Precondition Steps

**Standard format** (JSON array provided):

Execute each action in the JSON array using Playwright tools:
- `goto` → `mcp__playwright__browser_navigate(url=...)`
- `fill` → snapshot first to get ref, then `mcp__playwright__browser_type(ref=..., text=...)`
- `click` → snapshot first to get ref, then `mcp__playwright__browser_click(ref=..., element=...)`
- `wait_for` → `mcp__playwright__browser_wait_for(selector=..., timeout=...)`

**Zephyr format** (human-readable text provided):

1. Extract URL if present (`https?://[^\s]+`) → `browser_navigate(url=...)`
2. Extract login credentials if present:
   - Email pattern: `[\w.+-]+@[\w-]+\.[a-z]+`
   - Password: text after `mật khẩu` or `password:`
   - → Fill login form: `browser_fill` email field, `browser_fill` password field, `browser_click` login button
3. Wait: `browser_wait_for(time=2)`
4. Take snapshot to confirm page loaded

After preconditions succeed → record `entryUrl` (current URL from snapshot).

**On failure** → mark all cases in batch as ERROR (`"Precondition failed: {detail}"`), write results to sheet, close browser, return.

---

### 2 — Execute each test case

Initialize result collectors:
```
results = []       # [{sheetRow, result, error, actualResult, screenshot, timestamp}]
screenshots = []   # [{testId, filename}]
```

For each test case (in order):

**2a — Reset to entry state** (skip for the first case in the batch):
```
mcp__playwright__browser_navigate(url=entryUrl)
mcp__playwright__browser_wait_for(time=2)
```
If reset fails → ERROR for this case + all remaining cases: `"Entry reset failed"`. Close browser, return.

**2b — Execute test steps**

*Standard format* (JSON array):
Execute each action using Playwright tools (see browser-control.md). Always call `mcp__playwright__browser_snapshot` before `click`/`fill` to get element refs.

*Zephyr format* (numbered human-readable steps):
Parse numbered steps (split on `\n`, strip step numbers). For each step:
1. Take snapshot to see current page state
2. Determine Playwright action from step text (click/nhấn/bấm, nhập/điền/enter, chờ/wait, scroll/cuộn, hover/di chuột)

On step failure → capture screenshot, record error, stop further steps for this case.

**2c — Validate result**

*Standard format* (JSON assertion array):
Take fresh snapshot. Evaluate each assertion (visible, not_visible, text_contains, text_equals, url_contains, url_equals, count).

*Zephyr format* (human-readable expected result):
Take fresh snapshot. Check if key phrases from Expected Result appear in the snapshot's visible text. If expected mentions URL → also check `browser_evaluate("window.location.href")`.

**2d — Capture screenshot** (always, regardless of result):
```
mcp__playwright__browser_take_screenshot(filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png", type="png")
```
Add to screenshots list: `{testId, filename}`

**2e — Collect result (do NOT write to sheet yet)**

```
results.push({sheetRow, result, error, actualResult, screenshot: filename, timestamp: isoTimestamp})
```

---

### 3 — Batch upload screenshots

After ALL test cases are done, upload all screenshots in one call:

```bash
python3 {skillDir}/scripts/gdrive_batch_upload.py screenshots/{file1} screenshots/{file2} ...
```

Output: JSON array with `{name, id, direct}` per file. Map each `direct` URL to the corresponding test case by filename.

---

### 4 — Batch write results to sheets

**Standard format** — test sheet (columns G–J):

For contiguous rows, use a single range:
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "G{firstRow}:J{lastRow}", [
  [result1, error1, screenshot1, ts1],
  [result2, error2, screenshot2, ts2],
  ...
])
```

**Zephyr format** — test sheet:

Write Actual Result + Result status. Batch contiguous rows where possible:
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "{actualResultCol}{sheetRow}", [[actualResultText]])
mcp__gsheets__update_cells(spreadsheetId, sheetName, "{resultCol}{sheetRow}", [[result]])
```

**Evidence sheet** (both formats):

Write `=IMAGE()` formulas. Batch contiguous evidence rows:
```
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "B{firstRow}:B{lastRow}", [
  ['=IMAGE("{directUrl1}")'],
  ['=IMAGE("{directUrl2}")'],
  ...
])
```

---

### 5 — Close browser

```
mcp__playwright__browser_close()
```

Always close, even if errors occurred.

---

### 6 — Return summary

```
Batch {startId}–{endId}: {pass} PASS, {fail} FAIL, {error} ERROR
[For each FAIL/ERROR]:
  - {testId}: {errorMessage}
```

---

## Guardrails

- **Never modify** user-input columns (A–F for Standard, test data columns for Zephyr).
- **Never skip** writing results — even on ERROR.
- **Always close** browser when done.
- Screenshot filenames: `{testId}_{yyyyMMdd_HHmmss}.png` (no spaces).
- **NEVER write temp/helper scripts to disk.**
