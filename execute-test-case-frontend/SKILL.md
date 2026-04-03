---
name: execute-test-case-frontend
description: Execute frontend/UI test cases from a Google Sheets spreadsheet using Playwright browser automation. Reads test rows, performs browser interactions, validates assertions, captures screenshots, and writes PASS/FAIL results back to the sheet. Supports two sheet formats: Standard (JSON steps/assertions) and Zephyr/TestRail (human-readable steps, detected automatically). Use when user says "execute frontend test", "run FE test cases", "chạy test case frontend", or provides a Sheets URL with frontend test data.
---

# Execute Test Case — Frontend

Reads frontend test cases from Google Sheets, executes each via Playwright browser automation, and writes results back. Supports two spreadsheet formats, detected automatically.

Uses **subagent-per-batch** execution to prevent token accumulation across test cases.

---

## Prerequisites

- **gsheets MCP** configured (`mcp__gsheets__*` tools available)
- **Playwright MCP** configured (`mcp__playwright__*` tools available)
- **Google Drive OAuth** — `~/.gdrive-mcp/` credentials (from MCP gdrive setup) for screenshot upload
- Google Sheet in Standard or Zephyr format (see Step 1)

---

## ⛔ Temp File Rules

**NEVER** write helper/temp script files to disk (`_*.py`, `_*.ps1`, `_check_*.py`, etc.). Use `python3 -X utf8 -c "..."` inline in Bash, or use Read/Edit/Write tools directly.

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

**Build `evidenceMap`**: a mapping of `testId → evidence sheet row number`. This is passed to subagents.

---

### Step 2b — Group + batch splitting

**Standard format**: Group consecutive rows by column C (Precondition Group). Empty C → solo group.

**Zephyr format**: Group by PreConditions text prefix (see Zephyr grouping logic above).

**Batch splitting** — after grouping, split large groups into batches:

- `MAX_BATCH = 5` — if a group has more than 5 pending test cases, split into sub-batches of 5
- Each sub-batch re-runs preconditions independently (minor overhead, major token savings)

Example: Group A has 12 cases → Batch A1 (cases 1–5), Batch A2 (cases 6–10), Batch A3 (cases 11–12).

---

### Step 2c — Pre-load execution instructions (once)

Read the condensed instructions file **once** before spawning any subagent:

```
Read({skillDir}/references/condensed-instructions.md)
```

Store the full content as `executionInstructions`. This will be embedded verbatim into each subagent prompt so subagents can start executing **immediately** without reading any files.

---

### Step 3 — Execute batches via subagents

To prevent token accumulation, each batch is executed by a **separate subagent** with a fresh context. The subagent writes results directly to the sheet.

**Small run shortcut**: If total pending test cases ≤ 5, skip subagents and execute directly following [condensed-instructions.md](references/condensed-instructions.md) instructions inline. With batch writes the per-case overhead is low enough. When executing inline, substitute `{skillDir}` with this skill's absolute directory path (the directory containing this SKILL.md).

#### Subagent prompt template — Standard format

```
Agent(
  description="FE test {startId}–{endId}",
  prompt="""
## Execution Instructions

{executionInstructions}

---

## Data

skillDir: {skillDir}
spreadsheetId: {spreadsheetId}
sheetName: {sheetName}
format: Standard

### Precondition Steps (execute once before test cases):
{preconditionStepsJSON or "None"}

### Test cases to execute:
| Sheet Row | Test ID | Steps (JSON) | Assertions (JSON) |
|-----------|---------|-------------|-------------------|
| {row} | {id} | {steps} | {assertions} |
...

### Evidence row mapping:
| Test ID | Evidence Row |
|---------|-------------|
| {id} | {evidenceRow} |
...

Execute all test cases following the instructions above (Standard format sections).
Batch write results to columns G–J + batch upload screenshots at the end.
Report summary when done.
"""
)
```

#### Subagent prompt template — Zephyr format

```
Agent(
  description="FE test {startId}–{endId}",
  prompt="""
## Execution Instructions

{executionInstructions}

---

## Data

skillDir: {skillDir}
spreadsheetId: {spreadsheetId}
sheetName: {sheetName}
format: Zephyr

### Column mapping:
- Actual Result column: {actualResultCol}
- Result column: {resultCol}

### Precondition text (execute once):
{preconditionText or "None"}

### Test cases to execute:
| Sheet Row | Test ID | Steps | Expected Result |
|-----------|---------|-------|----------------|
| {row} | {id} | {steps} | {expected} |
...

### Evidence row mapping:
| Test ID | Evidence Row |
|---------|-------------|
| {id} | {evidenceRow} |
...

Execute all test cases following the instructions above (Zephyr format sections).
Batch write Actual Result + PASS/FAIL + batch upload screenshots at the end.
Report summary when done.
"""
)
```

**Replace `{skillDir}`** with the actual absolute path to this skill's directory.
**Replace `{executionInstructions}`** with the content loaded in Step 2c.

**Important execution rules:**
- Execute batches **sequentially** — Playwright MCP supports only one browser session at a time.
- After each subagent returns, collect its pass/fail/error counts.
- If a subagent reports a blocker → resolve with user, then re-spawn.

---

### Step 4 — Print summary

Aggregate results from all subagent summaries:

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
