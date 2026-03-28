---
name: execute-test-case-frontend
description: Execute frontend/UI test cases from a Google Sheets spreadsheet using Playwright browser automation. Reads test rows, performs browser interactions, validates assertions, captures screenshots, and writes PASS/FAIL results back to the sheet. Groups consecutive cases by Precondition Group to reuse browser session state — login and navigation run only once per group. Use when user says "execute frontend test", "run FE test cases", "chạy test case frontend", or provides a Sheets URL with frontend test data.
---

# Execute Test Case — Frontend

Reads frontend test cases from Google Sheets, executes each via Playwright browser automation, and writes results back. Groups consecutive cases by `Precondition Group` so that login and page navigation run **once per group** — subsequent cases in the group reuse the existing browser session and only execute their test-specific steps.

---

## Prerequisites

- **gsheets MCP** configured (`mcp__gsheets__*` tools available)
- **Playwright MCP** configured (`mcp__playwright__*` tools available)
- Google Sheet structured per the [Frontend schema](references/test-case-schema.md)

---

## Workflow

### Step 0 — Parse spreadsheet URL

Extract `spreadsheetId` from the URL the user provides:
- `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit...` → segment between `/d/` and `/edit`

If not provided, ask for it.

---

### Step 0b — Optional: Range / filter

The user may optionally specify which test cases to run:
- **Range**: "run FE-010 to FE-025" → only rows where Test ID is in that range
- **List**: "run FE-003, FE-007" → only those specific IDs
- **Re-run failures**: "re-run failed cases" → only rows where column G = "FAIL"
- **Force re-run**: "re-run all" → ignore already-executed check

If not specified → run all pending rows in order.

Store filter as `idFilter` (list of IDs, or null for all). Applied after Step 1 partitioning.

---

### Step 1 — Read test cases

```
mcp__gsheets__get_sheet_data(spreadsheetId, sheetName="Frontend Tests")
```

- Default tab name: `"Frontend Tests"`. If not found, call `mcp__gsheets__list_sheets` and ask the user.
- Row 1 is the header. Skip it.
- Skip rows where column A (Test ID) is empty.

Column mapping (1-indexed):

| Col | Field | Notes |
|-----|-------|-------|
| A | Test ID | e.g. `FE-001` |
| B | Title | Short description |
| C | Precondition Group | Optional. Consecutive cases with same value share browser state |
| D | Precondition Steps | JSON array — browser steps to reach the test entry point. Executed once per group |
| E | Steps | JSON array — test-specific browser steps |
| F | Assertions | JSON array — conditions to verify after steps |
| G | Result | **Agent writes**: PASS / FAIL / ERROR |
| H | Error Message | **Agent writes**: failure detail or empty |
| I | Screenshot URL | **Agent writes**: file path of screenshot |
| J | Executed At | **Agent writes**: ISO 8601 timestamp |

**Skip already-executed rows:**
- `pendingRows` — rows where column G is empty
- `doneRows` — rows where column G is non-empty

Print at start:
```
Loaded {total} test cases: {pending} pending, {done} already executed (skipping)
```
Only execute `pendingRows` (unless user says "re-run all").

---

### Step 2 — Prepare Evidence sheet

Read test cases first (Step 1 must complete before this step).

Check if an `"Evidence"` tab exists:
```
mcp__gsheets__list_sheets(spreadsheetId)
```

If not found, create it, write the header row, then pre-populate column A with **all test case IDs** (from `pendingRows` + `doneRows`, in original order):
```
mcp__gsheets__create_sheet(spreadsheetId, "Evidence")
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "A1:B1", [["Test ID", "Screenshot"]])

# Pre-populate column A with all test IDs
# e.g. if test IDs are FE-001…FE-020, write them to A2:A21
mcp__gsheets__update_cells(spreadsheetId, "Evidence", "A2:A{n+1}", [[id] for id in allTestIds])
```

If the Evidence sheet **already exists**, read its current content to determine which rows already have screenshots (column B non-empty) so you can skip re-writing those rows.

Track the next available Evidence row: find the first row in column A that has a Test ID but an empty column B (or append after the last populated row).

**Important:** column A is the source of truth for row positions — always look up the Evidence row for a given Test ID by scanning column A, do not assume sequential order.

---

### Step 3 — Group by Precondition Group

**Group consecutive rows** sharing the same `Precondition Group` value (column C).

- Empty column C → solo group (browser resets before this case).
- Non-consecutive appearances of the same group name → separate group instances (re-execute preconditions).

```
Example:
  FE-001  group=login-admin   → Group A (first case — execute preconditions)
  FE-002  group=login-admin   → Group A (reuse session)
  FE-003  group=login-admin   → Group A (reuse session)
  FE-004  group=login-guest   → Group B (new group — execute preconditions)
  FE-005  group=login-guest   → Group B (reuse session)
  FE-006  group=              → Solo (reset browser)
  FE-007  group=login-admin   → Group C (non-consecutive — re-execute preconditions)
```

---

### Step 4 — Execute each group

#### 4a — Execute Precondition Steps (once per group, first case only)

Take `Precondition Steps` (column D) from the **first row** of the group (subsequent rows' column D is ignored even if non-empty).

Precondition steps execute the login flow, navigate to the feature page, and establish the **entry state** for all test cases in the group.

Execute each step using Playwright MCP tools (see [browser-control.md](references/browser-control.md)):

```json
[
  {"action": "goto", "url": "https://app.example.com/login"},
  {"action": "fill", "selector": "#email", "value": "admin@test.com"},
  {"action": "fill", "selector": "#password", "value": "Admin@123"},
  {"action": "click", "selector": "button[type=submit]"},
  {"action": "wait_for", "selector": ".dashboard", "timeout": 5000},
  {"action": "goto", "url": "https://app.example.com/feature"},
  {"action": "wait_for", "selector": ".feature-list", "timeout": 3000}
]
```

After all precondition steps complete successfully, record the **entry URL** (current page URL from snapshot). This URL is used to reset state between test cases within the group.

If any precondition step fails → mark **all cases in the group** as ERROR: `"Precondition failed: {step_index} — {detail}"`. Close browser. Skip to next group.

#### 4b — Execute each test case in the group

For each test row, in order:

**4b-1: Reset to entry state (skip for the first case in the group)**

For the 2nd and subsequent cases: navigate back to the entry URL before running steps.

```
mcp__playwright__browser_navigate(url=entryUrl)
mcp__playwright__browser_wait_for(selector=lastPreconditionWaitSelector, timeout=3000)
```

This ensures each test starts from the same page without re-doing the full login flow.

**4b-2: Execute test Steps (column E)**

```json
[
  {"action": "click", "selector": "#btn-create"},
  {"action": "fill", "selector": "#form-name", "value": "Test Item"},
  {"action": "click", "selector": "#btn-submit"},
  {"action": "wait_for", "selector": ".success-toast", "timeout": 3000}
]
```

Execute using Playwright MCP tools. See [browser-control.md](references/browser-control.md) for action → tool mapping.

On step failure:
- Capture screenshot immediately.
- Record step index and error detail.
- Stop executing further steps.
- Proceed to assertions (they will likely fail too, providing more context).

**4b-3: Run Assertions (column F)**

```json
[
  {"type": "visible",          "selector": ".success-toast"},
  {"type": "not_visible",      "selector": ".error-message"},
  {"type": "text_equals",      "selector": "h1",            "value": "Tạo mới thành công"},
  {"type": "text_contains",    "selector": ".status-badge", "value": "Đang xử lý"},
  {"type": "value_equals",     "selector": "#input-name",   "value": "Tên sản phẩm A"},
  {"type": "attribute_equals", "selector": "#btn-save",     "attribute": "disabled", "value": "true"},
  {"type": "count_equals",     "selector": ".table-row",    "value": 5},
  {"type": "url_contains",     "value": "/dashboard"},
  {"type": "url_equals",       "value": "https://app.example.com/dashboard"}
]
```

**Assertion type reference:**

| type | Checks | Required fields |
|------|--------|----------------|
| `visible` | Element exists and is visible | `selector` |
| `not_visible` | Element absent or hidden | `selector` |
| `text_equals` | Element text = value (exact, trimmed) | `selector`, `value` |
| `text_contains` | Element text contains value | `selector`, `value` |
| `value_equals` | Input/textarea `.value` = value | `selector`, `value` |
| `attribute_equals` | Element attribute = value | `selector`, `attribute`, `value` |
| `count_equals` | Number of matching elements = value | `selector`, `value` (integer) |
| `url_contains` | Current URL contains value | `value` |
| `url_equals` | Current URL = value (exact) | `value` |

Use `mcp__playwright__browser_snapshot` to get the current page state, then evaluate assertions against the snapshot.

On first failure → record `"Assertion failed [{type}]: selector={selector}, expected={value}, got={actual}"`. Continue remaining assertions to collect all failures.

**4b-4: Capture screenshot**

Always capture screenshot regardless of pass/fail:

```
mcp__playwright__browser_take_screenshot(
  filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png",
  type="png"
)
```

Save to a `screenshots/` folder relative to the working directory.

**4b-5: Write result**

Write to test sheet immediately:
```
mcp__gsheets__update_cells(spreadsheetId, "Frontend Tests", rowIndex, {
  G: "PASS" | "FAIL" | "ERROR",
  H: errorMessage or "",
  I: screenshotPath,
  J: ISO timestamp
})
```

Write to Evidence sheet — find the row whose column A matches `testId`, then write an `=IMAGE()` formula to column B so the screenshot renders as a viewable image in the sheet:
```
# Find Evidence row by testId (from the pre-populated column A)
evidenceRow = lookup row in Evidence where A == testId

# Write IMAGE formula to column B
# screenshotUrl must be a web-accessible URL (https://...)
# If screenshots are saved locally, upload to a public host first (e.g. Google Drive
# shared link, imgbb, etc.) and use that URL here.
mcp__gsheets__update_cells(spreadsheetId, "Evidence", f"B{evidenceRow}",
  [[f'=IMAGE("{screenshotUrl}")']]
)
```

**Obtaining a web-accessible screenshot URL:**
- If the Playwright MCP returns a public URL for the screenshot, use it directly.
- If only a local file path is available, attempt to upload the file to Google Drive using any available `mcp__gdrive__*` upload tool, then use the shareable `https://drive.google.com/uc?id=FILE_ID` link.
- If no upload mechanism is available, fall back to writing the local file path as plain text (the image will not render inline but the path is preserved for reference).

#### 4c — Close browser after each group

After all cases in a group complete (or on group-level ERROR), close the browser context:
```
mcp__playwright__browser_close()
```

---

### Step 5 — Print summary

```
=== Frontend Test Execution Summary ===
Total:  {n}
PASS:   {n}  ✓
FAIL:   {n}  ✗
ERROR:  {n}  ⚠

Screenshots saved to: screenshots/
Evidence sheet: "Evidence" tab in the spreadsheet

FAILED cases:
  - FE-003 "Tạo item mới": Assertion failed — ".success-toast" not visible

ERROR cases:
  - FE-006 "Xem chi tiết": Precondition failed: step 2 — selector "#email" not found
```

---

## Guardrails

- **Never modify** columns A–F (user input). Only write to G, H, I, J.
- **Never skip writing results** — even on ERROR, write the result row.
- **Never re-execute** rows where column G is already non-empty unless explicitly instructed.
- **Always close the browser** after each group, even on error.
- Screenshot filenames must not contain spaces or special characters — use `{testId}_{yyyyMMdd_HHmmss}.png`.
