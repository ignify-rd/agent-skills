---
name: execute-test-case-frontend
description: Execute frontend/UI test cases from a Google Sheets spreadsheet using Playwright browser automation. Reads test rows, performs browser interactions, validates assertions, captures screenshots, and writes PASS/FAIL results back to the sheet. Supports two sheet formats: Standard (JSON steps/assertions) and Zephyr/TestRail (human-readable steps, detected automatically). Use when user says "execute frontend test", "run FE test cases", "chạy test case frontend", or provides a Sheets URL with frontend test data.
---

# Execute Test Case — Frontend

Reads frontend test cases from Google Sheets, executes each via Playwright browser automation, and writes results back. Supports two spreadsheet formats, detected automatically.

---

## Prerequisites

- **gsheets MCP** configured (`mcp__gsheets__*` tools available)
- **Playwright MCP** configured (`mcp__playwright__*` tools available)
- Google Sheet in Standard or Zephyr format (see Step 1)

---

## Workflow

### Step 0 — Parse spreadsheet URL

Extract `spreadsheetId` from the URL the user provides:
- `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit...` → segment between `/d/` and `/edit`

If not provided, ask for it.

---

### Step 0b — Optional: Range / filter

The user may optionally specify which test cases to run:
- **Range**: "run DVC1 to DVC10" → only rows where Test ID is in that range
- **List**: "run DVC3, DVC7" → only those specific IDs
- **Re-run failures**: "re-run failed cases" → only rows where Result column = "FAIL"
- **Force re-run**: "re-run all" → ignore already-executed check

If not specified → run all pending rows in order.

Store filter as `idFilter`. Applied after Step 1 partitioning.

---

### Step 1 — Read test cases + detect format

```
mcp__gsheets__list_sheets(spreadsheetId)
```

If no tab matches `"Frontend Tests"` — do NOT ask. Read all available tabs and auto-detect the format (below).

```
mcp__gsheets__get_sheet_data(spreadsheetId, sheetName=<best candidate tab>)
```

Best candidate: tab named "TestCase", "Test Cases", "TestCases", "Frontend Tests", or the first non-"Evidence" tab.

---

#### Format auto-detection (no user input required)

Scan all rows to find the header row (the row that contains the most column name keywords):

**Zephyr/TestRail format detected if ANY of these appear in the header row:**
- `"External ID"` or `"ExternalID"`
- `"Testcase LV1"` or `"TestCase LV"`
- `"PreConditions"` (as a column header)
- `"Expected Result"` paired with `"Step"` column

**Standard format detected if header row contains:**
- `"Test ID"` near column A AND `"Steps"` near column E AND `"Assertions"` near column F

If neither format can be detected with confidence → **STOP. Ask user** to confirm the tab name and column layout. This is the only case that requires user input.

---

#### Standard format — column mapping

| Col | Field | Notes |
|-----|-------|-------|
| A | Test ID | e.g. `FE-001` |
| B | Title | Short description |
| C | Precondition Group | Consecutive same-value rows share browser state |
| D | Precondition Steps | JSON array of browser actions. Executed once per group |
| E | Steps | JSON array of browser actions for this test case |
| F | Assertions | JSON array of assertion objects |
| G | **Result** | Agent writes: PASS / FAIL / ERROR |
| H | **Error Message** | Agent writes |
| I | **Screenshot** | Agent writes: file path |
| J | **Executed At** | Agent writes: ISO 8601 |

Skip rows where column A is empty. Pending = column G empty.

---

#### Zephyr/TestRail format — column mapping

**Step 1: Build column map from ALL header rows (multi-header support)**

Zephyr sheets often have 2 stacked header rows (section-level + column-level). Do NOT assume a single header row. Instead:

1. Scan rows from the top until the first valid data row (see "Data row detection" below).
2. Treat ALL rows in that pre-data zone as potential header rows.
3. Merge column labels across all those rows: for each column index, collect every non-empty label found across all header rows.
4. Use the merged label set to locate each field.

Example merged scan for column Z: section header says "Kết quả hiện tại", column header is empty → result column = Z. ✓

**Step 2: Locate each field by keyword (position may vary)**

| Keyword in any header row | Field | Agent reads/writes |
|---------------------------|-------|--------------------|
| `External ID` | Test ID | reads |
| `Name` (in test case section, not "Name" in section header) | Title | reads |
| `PreConditions` | Precondition text | reads |
| `Step` | Test steps text | reads |
| `Expected Result` | Expected outcome text | reads |
| `Actual Result` | Actual outcome | **agent writes** |
| `Kết quả` or `Kết quả hiện tại` | Result status | **agent writes**: PASS / FAIL / ERROR |

**Result column rule:** Only accept a column as the result column if its merged label contains a recognized keyword (`Kết quả`, `Result`, `Lần 1`/`Lần 2`/`Lần 3`). **Never** use a column as the result column because its header cell happens to contain a result value (`"FAIL"`, `"PASS"`, `"PENDING"`) — that indicates data contamination in the header area, not a column name.

**Data row detection — skip invalid rows:**

A row is a valid test case data row if ALL of the following are true:
1. The External ID cell is **non-empty** AND does **not** start with `#` (formula errors: `#REF!`, `#DIV/0!`, `#N/A`, `#VALUE!`, etc.)
2. The External ID value looks like a test case ID (alphanumeric, e.g. `DVC1`, `FE-001`, `TC_001`)

Skip ALL other rows regardless of other column content.

**Pending rows:** Rows where the Result column is empty or contains `"PENDING"`.

**Already-executed rows:** Result column is `"PASS"` or `"FAIL"` — skip unless `--force`.

**Row number tracking:** After reading, record the actual spreadsheet row number for each test case as `sheetRow = dataArrayIndex + 1` (1-based sheet row). Store this per test case **at read time**. This is critical for writing results back accurately — never recompute it later.

Print at start:
```
[Zephyr format detected] Loaded {total} test cases: {pending} pending, {done} already executed (skipping)
```

---

#### Zephyr grouping logic (replaces Precondition Group column)

Since Zephyr format has no dedicated group column, derive groups by comparing the `PreConditions` text of consecutive rows:

1. Take the first 200 characters of the PreConditions text (normalized: trim whitespace, lowercase)
2. Consecutive rows where this prefix is **identical** → same group (reuse browser session)
3. Consecutive rows where prefix differs → new group (reset browser, re-run preconditions)
4. Empty PreConditions → solo group (reset browser before this case)

```
Example:
  DVC1  precond="mở trình duyệt, vào url..."  → Group A (execute preconditions)
  DVC2  precond="mở trình duyệt, vào url..."  → Group A (same prefix, reuse session)
  DVC6  precond="đăng nhập với tài khoản..."  → Group B (different prefix, new group)
  DVC7  precond="đăng nhập với tài khoản..."  → Group B (reuse session)
```

Commit to the first grouping derived — do NOT re-analyze or reconsider.

---

### Step 2 — Prepare Evidence sheet

Check if `"Evidence"` tab exists:
```
mcp__gsheets__list_sheets(spreadsheetId)
```

If not found → create it:
```
mcp__gsheets__create_sheet(spreadsheetId, "Evidence")
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "A1:B1", [["Test ID", "Screenshot"]])
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "A2:A{n+1}", [[id] for id in allTestIds])
```

If already exists → read column A to build a `testId → evidenceRow` lookup map. Never assume sequential order.

---

### Step 3 — Execute each group

#### 3a — Execute Precondition Steps (once per group)

**Standard format:** Execute the JSON array from column D using Playwright tools.

**Zephyr format:** Parse the PreConditions text from the group's first row:

1. Extract URL if present (pattern: `https?://[^\s]+`) → `browser_navigate(url=...)`
2. Extract login credentials if present:
   - Email pattern: `[\w.+-]+@[\w-]+\.[a-z]+`
   - Password: text after `mật khẩu` or `password:`
   - → Fill login form: `browser_fill` email field, `browser_fill` password field, `browser_click` login button
3. Wait for page to settle: `browser_wait_for(time=2)`
4. Take snapshot to confirm page loaded

After all precondition steps succeed → record `entryUrl` (current URL from snapshot).

If preconditions fail → mark all cases in group as ERROR: `"Precondition failed: {detail}"`. Close browser. Skip to next group.

#### 3b — Execute each test case

For each test row, in order:

**3b-1: Reset to entry state (skip for the first case in each group)**

```
mcp__playwright__browser_navigate(url=entryUrl)
mcp__playwright__browser_wait_for(time=2)
```

**3b-2: Execute test Steps**

**Standard format:** Execute the JSON array from column E using Playwright tools (see [browser-control.md](references/browser-control.md)).

**Zephyr format:** The Steps column contains numbered human-readable steps. Execute each step sequentially:

1. Parse numbered steps: split on `\n`, strip step numbers (`1.`, `2.`, etc.)
2. For each step text:
   - **Take snapshot** to see current page state
   - Determine the appropriate Playwright action based on step description:

| Step text pattern | Playwright action |
|-------------------|------------------|
| Contains URL (`https?://`) | `browser_navigate(url=...)` |
| "click", "nhấn", "bấm" + element description | `browser_click(element=<find from snapshot>)` |
| "nhập", "điền", "enter" + value + field description | `browser_fill(element=<find from snapshot>, value=...)` |
| "chờ", "wait", "tải trang" | `browser_wait_for(time=2)` |
| "scroll", "cuộn" | `browser_evaluate(script="window.scrollBy(0, 300)")` |
| "hover", "di chuột" | `browser_hover(element=<find from snapshot>)` |

   - Use snapshot's accessibility tree to find the correct `ref` for elements mentioned in the step
   - On step failure: capture screenshot, record error, stop further steps for this case

**3b-3: Validate result**

**Standard format:** Evaluate each assertion in the JSON array from column F against a fresh snapshot.

**Zephyr format:** The Expected Result column contains a human-readable description. Validate by:

1. Take a fresh snapshot
2. Check if **key phrases** from the Expected Result text appear in the snapshot's visible text
3. If expected result mentions a URL pattern → also check `browser_evaluate("window.location.href")`
4. Record as PASS if key phrases are present; FAIL with detail if absent

Key phrase extraction: take noun phrases and quoted strings from the expected result. Example:
- "Hệ thống đăng nhập thành công, điều hướng tới trang Discuss" → check for "Discuss" in snapshot + URL contains `/discuss`
- "Hiển thị thông báo lỗi 'Sai mật khẩu'" → check for "Sai mật khẩu" in snapshot

**3b-4: Capture screenshot**

Always capture, regardless of pass/fail:
```
mcp__playwright__browser_take_screenshot(
  filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png",
  type="png"
)
```

**3b-5: Write result**

**Standard format** — write to the test sheet:
```
mcp__gsheets__update_cells(spreadsheetId, sheetName, "G{sheetRow}:J{sheetRow}", [[
  "PASS"|"FAIL"|"ERROR",
  errorMessage or "",
  screenshotPath,
  isoTimestamp
]])
```

**Zephyr format** — write to the test sheet using the exact `sheetRow` recorded in Step 1:
```
# Write Actual Result
mcp__gsheets__update_cells(spreadsheetId, sheetName, "{actualResultCol}{sheetRow}", [[actualResultText]])

# Write PASS/FAIL to result column
mcp__gsheets__update_cells(spreadsheetId, sheetName, "{resultCol}{sheetRow}", [["PASS"|"FAIL"|"ERROR"]])
```

Write to Evidence sheet — find the row where column A = testId, write screenshot path to column B:
```
evidenceRow = lookup in evidenceMap[testId]
mcp__gsheets__update_cells(spreadsheetId, "Evidence", f"B{evidenceRow}", [[screenshotPath]])
```

#### 3c — Close browser after each group

```
mcp__playwright__browser_close()
```

---

### Step 4 — Print summary

```
=== Frontend Test Execution Summary ===
Format: Standard | Zephyr
Total:  {n}
PASS:   {n}  ✓
FAIL:   {n}  ✗
ERROR:  {n}  ⚠

Screenshots saved to: screenshots/

FAILED cases:
  - DVC-003 "Tạo item mới": Expected "thành công" not found in page
ERROR cases:
  - DVC-006 "Xem chi tiết": Precondition failed — login form not found
```

---

## Guardrails

- **Never modify** user-input columns. Only write to Result, Actual Result, Screenshot, Executed At columns.
- **Never skip writing results** — even on ERROR.
- **Never re-execute** already-executed rows unless explicitly instructed.
- **Always close the browser** after each group, even on error.
- Screenshot filenames must not contain spaces — use `{testId}_{yyyyMMdd_HHmmss}.png`.
- **Commit to the detected format immediately.** Do not switch format mid-execution.

## ⛔ Anti-loop rules

These are the ONLY situations that require stopping to ask the user:

| Situation | Action |
|-----------|--------|
| Format cannot be auto-detected (neither Standard nor Zephyr markers found) | Print found headers → ask user |
| Cannot determine which column is the Result column | Ask user once, then proceed |
| Same execution blocker occurs 3+ times in a row | STOP all execution, report to user |

**Analysis limit**: If you catch yourself re-reading the same sheet data, reconsidering the same grouping, or re-examining the same snapshot more than twice to answer the same question → commit to the best available interpretation and proceed.
