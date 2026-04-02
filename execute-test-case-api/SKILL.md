---
name: execute-test-case-api
description: Execute API test cases from a Google Sheets spreadsheet using Postman web browser. Reads test rows, opens Postman web, sends each request, screenshots the response as evidence, validates against expected results, and writes PASS/FAIL back to the sheet with screenshots stored in a separate Evidence tab. Use when user says "execute api test", "run api test cases", "chạy test case api", or provides a Sheets URL with API test data.
---

# Execute Test Case — API

Reads API test cases from Google Sheets, executes each via **Postman web browser** (Playwright), captures a screenshot of the response as evidence, validates the result, and writes back to two sheets: the main test sheet (PASS/FAIL) and a separate **Evidence** tab (Test ID + screenshot).

Groups consecutive test cases by `Precondition Group` to reuse auth tokens — the login call runs **once per group**.

Uses **subagent-per-batch** execution to prevent token accumulation across test cases.

---

## Prerequisites

- **gsheets MCP** configured (`mcp__gsheets__*` tools available)
- **Playwright MCP** configured (`mcp__playwright__*` tools available)
- `curl` available in terminal (for precondition auth calls only)
- **Google Drive OAuth** — `~/.gdrive-mcp/` credentials (from MCP gdrive setup) for screenshot upload
- Google Sheet structured per the [API schema](references/test-case-schema.md)
- Postman account (for Postman web login — see [postman-web.md](references/postman-web.md))

---

## ⛔ Temp File Rules

**NEVER** write helper/temp script files to disk (`_*.py`, `_*.ps1`, `_check_*.py`, etc.). Use `python3 -X utf8 -c "..."` inline in Bash, or use Read/Edit/Write tools directly.

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

**Build `evidenceMap`**: a mapping of `testId → evidence sheet row number` (e.g., `{"API-001": 2, "API-002": 3, ...}`). This is passed to subagents.

---

### Step 3 — Group by Precondition Group + batch splitting

Group consecutive rows by column C value. Empty C → solo group. Non-consecutive same names → separate instances.

```
API-001  group=login-admin  → Group A (execute preconditions)
API-002  group=login-admin  → Group A (reuse token)
API-003  group=login-guest  → Group B (new preconditions)
API-004  group=             → Solo
```

**Batch splitting** — after grouping, split large groups into batches:

- `MAX_BATCH = 5` — if a group has more than 5 pending test cases, split into sub-batches of 5
- Each sub-batch is treated as an independent batch (re-runs preconditions)
- This is a minor overhead but prevents token accumulation within large groups

Example: Group A has 12 cases → Batch A1 (cases 1–5), Batch A2 (cases 6–10), Batch A3 (cases 11–12). Each batch re-runs the group's precondition steps.

---

### Step 4 — Execute batches via subagents

To prevent token accumulation, each batch is executed by a **separate subagent** with a fresh context. The subagent writes results directly to the sheet.

**Small run shortcut**: If total pending test cases ≤ 3, skip subagents and execute directly following [execute-batch.md](references/execute-batch.md) instructions inline. The overhead of spawning subagents is not worth it for very small runs.

#### For each batch, spawn a subagent:

```
Agent(
  description="API test {startId}–{endId}",
  prompt="""
Read these files for execution instructions:
- {skillDir}/references/execute-batch.md
- {skillDir}/references/postman-web.md
- {skillDir}/references/execution-rules.md

## Data

spreadsheetId: {spreadsheetId}
sheetName: {sheetName}

### Precondition Steps (execute once via curl before test cases):
{preconditionStepsJSON or "None — no preconditions for this batch"}

### Test cases to execute:
| Row | Test ID | Method | URL | Headers | Body | Expected Status | Expected Response |
|-----|---------|--------|-----|---------|------|----------------|-------------------|
| {row} | {id} | {method} | {url} | {headers} | {body} | {status} | {response} |
...

### Evidence row mapping:
| Test ID | Evidence Row |
|---------|-------------|
| {id} | {evidenceRow} |
...

Follow execute-batch.md workflow. Write results to the sheet as you go.
Report summary when done: total/pass/fail/error counts + failed test details.
"""
)
```

**Replace `{skillDir}`** with the actual absolute path to this skill's directory.

**Important execution rules:**
- Execute batches **sequentially** — wait for each subagent to finish before starting the next. Playwright MCP supports only one browser session at a time.
- After each subagent returns, collect its pass/fail/error counts for the final summary.
- If a subagent reports a blocker (e.g., Postman login required, environment not set) → pause, resolve with user, then re-spawn the same batch.

---

### Step 5 — Print summary

Aggregate results from all subagent summaries:

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
ERROR cases:
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
