---
name: execute-test-case-frontend
description: Execute frontend/UI test cases from Google Sheets using Playwright. Reads test rows, performs browser interactions, validates page state against descriptions, captures screenshots, and writes PASS/FAIL back to the sheet. Triggers when user says "execute frontend test", "run FE test cases", "chạy test case frontend", or provides a Sheets URL with frontend test data.
---

# Execute Test Case — Frontend

Reads frontend test cases from Google Sheets, executes each via Playwright browser, and writes results back.

**Format:** Standard (JSON steps/assertions) — fixed, no auto-detection.
**Batch size:** 10-15 cases per subagent.
**Execution:** Sequential (1 Playwright profile).

---

## Prerequisites

- **gsheets MCP** configured
- **Playwright MCP** configured
- **Google Drive OAuth** — `~/.gdrive-mcp/` credentials for screenshot upload
- Sheet tab: `Frontend Tests`

---

## ⛔ Temp File Rules

**NEVER** write helper/temp scripts (`_*.py`, `_*.ps1`, `_check_*.py`, etc.) to disk. Use `python3 -X utf8 -c "..."` inline, or Read/Edit/Write tools.

---

## Workflow

### Step 1 — Read test cases

```
mcp__gsheets__list_sheets(spreadsheetId)
mcp__gsheets__get_sheet_data(spreadsheetId, sheetName="Frontend Tests")
```

**Column layout (fixed, no auto-detection):**

| Col | Field | Notes |
|-----|-------|-------|
| A | Test ID | e.g. `FE-001` |
| B | Title | Short description |
| C | Precondition Group | Consecutive same-value rows share browser session |
| D | Precondition Steps | JSON array — execute once per group |
| E | Steps | JSON array — actions for this test case |
| F | Assertions | JSON array — validation rules |
| G | Result | Agent writes: PASS / FAIL / ERROR |
| H | Error Message | Agent writes |
| I | Screenshot | Agent writes: file path |
| J | Executed At | Agent writes: ISO 8601 |

Skip rows where column A is empty. Pending = column G empty.

Print at start:
```
Loaded {total} test cases: {pending} pending, {done} already executed (skipping)
```

---

### Step 2 — Filter (optional)

User may specify: range (`DVC1 to DVC10`), list (`DVC3, DVC7`), or re-run failures. If not specified → run all pending.

---

### Step 3 — Group + batch

Group consecutive rows by column C (Precondition Group). Empty C → solo group.

Split into batches of **10-15 cases** each.

---

### Step 4 — Pre-load instructions once

Before spawning any subagent, read the Playwright tool mapping once and store as `pwInstructions`:

```
## Playwright Tool Mapping
- goto → mcp__playwright__browser_navigate(url=...)
- back → mcp__playwright__browser_navigate_back()
- click → snapshot first, then mcp__playwright__browser_click(ref=..., element=...)
- fill → snapshot first, then mcp__playwright__browser_type(ref=..., text=...)
- fill_form → mcp__playwright__browser_fill_form(fields=[{name, type, ref, value}])
- select → mcp__playwright__browser_select_option(ref=..., values=...)
- wait_for → mcp__playwright__browser_wait_for(selector=..., timeout=...)
- hover → mcp__playwright__browser_hover(ref=...)
- press_key → mcp__playwright__browser_press_key(key=...)
- scroll → mcp__playwright__browser_evaluate(script="window.scrollBy(0, 300)")
- snapshot → mcp__playwright__browser_snapshot()
- handle_dialog → mcp__playwright__browser_handle_dialog(accept=true/false)
```

---

### Step 5 — Execute batches via subagent

Each batch = separate subagent (fresh context, no token accumulation).

**Subagent prompt:**
```
Agent(
  description="FE test batch {batchNum}",
  prompt="""
## Execution Instructions

{pwInstructions}

---

## Data

skillDir: {skillDir}
spreadsheetId: {spreadsheetId}
sheetName: {sheetName}

### Precondition Steps (execute once before test cases):
{preconditionStepsJSON or "None"}

### Test cases to execute:
| Sheet Row | Test ID | Steps | Assertions |
|-----------|---------|-------|------------|
| {row} | {id} | {steps} | {assertions} |
...

---

## Workflow (execute in order)

### 1 — Execute Precondition Steps

If precondition steps provided → execute each action using tool mapping above.
After success → record `entryUrl` from snapshot (current URL).

If failed → mark ALL cases in this batch as ERROR: "Precondition failed: {detail}", write results, close browser, return.

### 2 — Execute each test case

Initialize:
- results = []
- screenshots = []

For each test case:

**2a — Reset to entry state** (skip for first case in batch):
- Navigate to entryUrl + wait 2s
- If failed → ERROR for this case + remaining: "Entry reset failed"

**2b — Execute steps** (JSON array):
- For each action: snapshot first, then call matching Playwright tool
- On step failure → capture screenshot, record error, stop

**2c — Validate result** (JSON assertion array):
- Take snapshot
- Evaluate each assertion:
  - `visible` → element in snapshot, not hidden
  - `not_visible` → element absent or hidden
  - `text_contains` → element text contains value
  - `text_equals` → element text exactly equals value
  - `url_contains` → page URL contains value
  - `url_equals` → page URL exactly equals value
  - `count` → matching element count equals expected
- All passed → PASS
- Any failed → FAIL

**2d — Screenshot** (always, regardless of result):
```
mcp__playwright__browser_take_screenshot(type="png", filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png")
```

**2e — Collect result** (do NOT write yet):
```
results.push({sheetRow, result, error, screenshot: filename, timestamp: isoTimestamp})
```

### 3 — Upload screenshots

```
python3 {skillDir}/scripts/gdrive_batch_upload.py screenshots/{file1} screenshots/{file2} ...
```

Output: JSON array with {name, id, direct} per file. Map `direct` URL to each test case.

### 4 — Write results to sheet

**Test sheet (columns G–J):**
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "G{firstRow}:J{lastRow}", [
  [result1, error1, screenshot1, ts1],
  [result2, error2, screenshot2, ts2],
  ...
])
```

**Evidence sheet:**
If "Evidence" tab exists → read column A to find row for each testId.
If not exists → create it with header "Test ID | Screenshot", pre-populate column A with all testIds.
Write `=IMAGE("{directUrl}")` to column B at the matched row for each test case.

### 5 — Close browser
```
mcp__playwright__browser_close()
```

### 6 — Return summary
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
=== Frontend Test Summary ===
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
| Precondition failed | ERROR | `Precondition failed: {detail}` |
| Entry reset failed | ERROR | `Entry reset failed: {detail}` |
| Step failed / timeout | ERROR | `Step {n} failed: {action} — {detail}` |
| Assertion failed | FAIL | `Assertion failed: {type} on "{selector}" — {detail}` |
| All passed | PASS | (empty) |

---

## Guardrails

- **NEVER** modify columns A–F.
- **NEVER** skip writing results.
- **NEVER** re-execute rows with Result already set unless instructed.
- **ALWAYS** close browser after each group.
- Screenshot filenames: `{testId}_{yyyyMMdd_HHmmss}.png` (no spaces).
- **NEVER** write temp scripts to disk.

## ⛔ Anti-loop

Stop and ask user if:
- Format cannot be detected (shouldn't happen — fixed format)
- Same blocker occurs 3+ times in a row