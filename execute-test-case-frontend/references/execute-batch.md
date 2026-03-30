# Execute Frontend Test Batch

Instructions for a subagent executing a batch of frontend test cases via Playwright browser automation. The subagent receives test case data and format details in its prompt.

Read this companion file for detailed instructions:
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
2. Determine Playwright action from step text:

| Step text pattern | Playwright action |
|-------------------|------------------|
| Contains URL (`https?://`) | `browser_navigate(url=...)` |
| "click", "nhấn", "bấm" + element | `browser_click(element=<from snapshot>)` |
| "nhập", "điền", "enter" + value | `browser_type(ref=<from snapshot>, text=...)` |
| "chờ", "wait", "tải trang" | `browser_wait_for(time=2)` |
| "scroll", "cuộn" | `browser_evaluate(script="window.scrollBy(0, 300)")` |
| "hover", "di chuột" | `browser_hover(element=<from snapshot>)` |

On step failure → capture screenshot, record error, stop further steps for this case.

**2c — Validate result**

*Standard format* (JSON assertion array):

Take fresh snapshot. Evaluate each assertion:
- `visible` → element in snapshot, not hidden
- `not_visible` → element absent or hidden
- `text_contains` → element text contains value
- `text_equals` → element text exactly equals value
- `url_contains` → page URL contains value
- `url_equals` → page URL exactly equals value
- `count` → matching element count equals expected

*Zephyr format* (human-readable expected result):

Take fresh snapshot. Check if key phrases from Expected Result appear in the snapshot's visible text. If expected mentions URL → also check `browser_evaluate("window.location.href")`.

**2d — Capture screenshot** (always, regardless of result):
```
mcp__playwright__browser_take_screenshot(filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png", type="png")
```

**2e — Write results immediately**

*Standard format* — test sheet:
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "G{sheetRow}:J{sheetRow}", [[
  "PASS"|"FAIL"|"ERROR", errorMessage or "", screenshotPath, isoTimestamp
]])
```

*Zephyr format* — test sheet:
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "{actualResultCol}{sheetRow}", [[actualResultText]])
mcp__gsheets__update_cells(spreadsheetId, sheetName, "{resultCol}{sheetRow}", [[result]])
```

Evidence sheet — find row where column A = testId, write screenshot path to column B:
```
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "B{evidenceRow}", [[screenshotPath]])
```

---

### 3 — Close browser

```
mcp__playwright__browser_close()
```

Always close, even if errors occurred.

---

### 4 — Return summary

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
