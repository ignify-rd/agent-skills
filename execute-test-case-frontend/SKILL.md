---
name: execute-test-case-frontend
description: Execute frontend/UI test cases from a local Excel (.xlsx) file using a DOM Snapshot + Generate-then-Execute approach. Reads only "Kiem tra validate" test cases, scans the live DOM to extract form structure, generates a Playwright script via LLM, executes it in one batch per Test Suite group, and writes PASS/FAIL/ERROR results with screenshots back to the .xlsx file. Triggers when user says "execute frontend test", "run FE test cases", "chay test case frontend", or provides a path to an .xlsx file with frontend test data.
---

# Execute Test Case - Frontend

Reads frontend validation test cases from a local `.xlsx` file, scans the live DOM of the target page, generates a Playwright script for each Test Suite group, executes the batch, and writes results back.

**Flow:** DOM Snapshot -> Generate Script -> Execute -> Write Excel Results

**Scope:** Only test cases belonging to group **"Kiem tra validate"**. Cases in **"Kiem tra chuc nang"** are ignored entirely (no result written, no execution).

---

## Prerequisites

- **Playwright MCP** configured
- `openpyxl` installed (`pip show openpyxl`)
- Local `.xlsx` file accessible
- Sheet tab: `TestCase` (or first sheet if not found)

---

## Input Parameters

| Parameter | Description |
|-----------|-------------|
| `url` | URL of the web page to test (top-level required input) |
| `file` | Path to the Excel file containing test cases (.xlsx) |

> `url` is a required top-level parameter, not read from column D. Column D (Precondition) may still contain complex pre-actions (e.g., login before navigating to the form).

---

## Column Layout

| Col | Field | Notes |
|-----|-------|-------|
| A | Test Suite | Suite grouping (also used to identify test type) |
| B | Test Case ID | e.g. `FE-001` |
| C | Title | Short description |
| D | Precondition | Complex pre-actions in natural language (optional) |
| E | Steps | Natural language description of actions for this test case |
| F | Assertions | Natural language description of expected results |
| G | Result | **Agent writes: PASS / FAIL / ERROR** |
| H | Error Message | **Agent writes** |
| I | Screenshot | **Agent writes: file path** |
| J | Executed At | **Agent writes: ISO 8601** |

Skip rows where column B (Test Case ID) is empty.
Pending = column G empty.

---

## Temp File Rules

**NEVER** write helper/temp scripts to disk. Use `python3 -X utf8 -c "..."` inline only.

---

## Workflow

### Step 1 - Read test cases from Excel

```bash
python3 -X utf8 -c "
import openpyxl, json
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')
sheetName = 'TestCase' if 'TestCase' in wb.sheetnames else wb.sheetnames[0]
ws = wb[sheetName]
results = []
for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
    testId = row[1]   # col B
    if not testId or not isinstance(testId, str):
        continue
    results.append({
        'row': i,
        'suite': str(row[0] or ''),
        'id': testId,
        'title': str(row[2] or ''),
        'precondition': str(row[3] or ''),
        'steps': str(row[4] or ''),
        'assertions': str(row[5] or ''),
        'status': row[6]
    })
print(json.dumps(results, ensure_ascii=False))
"
```

**Filter criteria (apply both conditions simultaneously):**
- Column G is empty (not yet executed).
- Test Suite (column A) indicates **"Kiem tra validate"** type. Common signals: Suite name contains "validate", "validation", "Kiem tra validate", or "Validate". Do **NOT** execute rows whose Suite belongs to "Kiem tra chuc nang" / "chuc nang" / "functional".

Print:
```
Loaded {total} test cases: {pending_validate} validate pending, {skipped_functional} functional skipped, {done} already executed
```

### Step 2 - Group validate cases by Test Suite

Group the filtered validate test cases by their Test Suite (column A). Each unique suite value = one execution group. Maintain the sheet row order within each group.

Print grouping summary:
```
Validate groups:
  Group 1: "{suiteName}" - {n} cases (rows {start}-{end})
  Group 2: "{suiteName}" - {n} cases (rows {start}-{end})
  ...
```

---

### Step 3 - Scan DOM to extract form structure (per group)

For each group:

**3a. Navigate to the target URL:**
```
mcp__playwright__browser_navigate(url="{url}")
```

If the group's Precondition column (col D) contains complex pre-actions (natural language), execute them using the appropriate Playwright MCP tools before scanning DOM. If precondition fails, mark ALL cases in this group as ERROR: `"Precondition failed: {detail}"` and skip the group.

**3b. Extract Accessibility Tree + form structure:**

```
mcp__playwright__browser_evaluate(function="async () => {
  const fields = [];
  const selectors = ['form', 'input', 'select', 'textarea', 'button',
    '[role=combobox]', '[role=listbox]', '[role=option]', '[role=textbox]'];
  document.querySelectorAll(selectors.join(',')).forEach(el => {
    const entry = {
      tag: el.tagName.toLowerCase(),
      type: el.type || null,
      id: el.id || null,
      name: el.name || null,
      placeholder: el.placeholder || null,
      ariaLabel: el.getAttribute('aria-label') || null,
      dataTestid: el.getAttribute('data-testid') || null,
      role: el.getAttribute('role') || null,
      textContent: el.tagName === 'BUTTON' ? (el.textContent || '').trim().slice(0, 60) : null
    };
    // Remove null keys
    Object.keys(entry).forEach(k => entry[k] === null && delete entry[k]);
    fields.push(entry);
  });
  return JSON.stringify(fields);
}")
```

The result is a compact JSON describing all interactive elements on the page. This is the **DOM snapshot** used in the next step.

---

### Step 4 - Generate Playwright script via LLM

Send the following prompt to the LLM (yourself) to generate a single Playwright async script for all cases in this group:

---

**Prompt template:**

```
You are a Playwright test automation engineer. Given the DOM structure and a list of validation test cases, generate a single JavaScript async function that runs all test cases and returns a results array.

## DOM Structure (compact JSON)
{DOM_SNAPSHOT_JSON}

## Test Cases to automate
{TEST_CASES_JSON}
(Each test case: { id, title, steps (natural language), assertions (natural language), screenshotPath })

## Requirements
1. Generate a single `async (page) => { ... return JSON.stringify(results); }` function.
2. For each test case, navigate back to `{url}` before running it.
3. Use the most specific locator available from the DOM: prefer `id` -> `aria-label` -> `placeholder` -> `data-testid` -> `name`.
4. For dropdown/combobox/select components: click to open first, then fill or select option.
5. For multiselect components: click to open, then click each desired option.
6. After all steps for a test case, call `await page.waitForLoadState('networkidle').catch(() => {})` OR `await page.waitForTimeout(300)` before taking a screenshot.
7. Take a screenshot with `await page.screenshot({ path: tc.screenshotPath })` after each test case.
8. Each test case result must be pushed to `results` as `{ id, result: 'PASS'|'FAIL'|'ERROR', error: '', screenshotPath }`.
9. If a locator cannot be resolved from the DOM, push `{ id, result: 'ERROR', error: 'Locator not found: {field_name}', screenshotPath }` and continue - do NOT throw.
10. Wrap each test case in a try/catch. Catch -> result ERROR with error message.
11. Output ONLY the code block. No explanation, no markdown wrapper.

## Output format
A single self-contained `async (page) => { ... }` function ready to pass to `browser_run_code`.
```

---

The LLM (you) must produce the complete Playwright script for the entire group.

---

### Step 5 - Execute the generated script

```
mcp__playwright__browser_run_code(code="{GENERATED_SCRIPT}")
```

Parse the returned JSON string into a results array:
```json
[
  { "id": "FE-001", "result": "PASS", "error": "", "screenshotPath": "screenshots/FE-001_20240101_120000.png" },
  { "id": "FE-002", "result": "FAIL", "error": "Expected visible: .error-msg", "screenshotPath": "screenshots/FE-002_20240101_120000.png" }
]
```

**If script execution fails entirely** (syntax error or unhandled exception): mark all cases in this group as `ERROR: "Batch script error: {detail}"`.

---

### Step 6 - Repeat Steps 3-5 for each remaining validate group

Iterate over all groups. After all groups are done, proceed to write results.

---

### Step 7 - Write results to Excel

After all groups complete, write all results in a single Python call:

```bash
python3 -X utf8 -c "
import openpyxl, json
from datetime import datetime

data = json.loads('''RESULTS_JSON''')
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')
sheetName = 'TestCase' if 'TestCase' in wb.sheetnames else wb.sheetnames[0]
ws = wb[sheetName]

now = datetime.now().isoformat()
for item in data:
    row = item['row']
    ws.cell(row=row, column=7).value = item['result']           # col G
    ws.cell(row=row, column=8).value = item.get('error', '')    # col H
    ws.cell(row=row, column=9).value = item.get('screenshotPath', '')  # col I
    ws.cell(row=row, column=10).value = now                     # col J

wb.save('PATH_TO_FILE.xlsx')
print('done')
"
```

### Step 8 - Embed screenshots into Evidence sheet

```bash
python3 -X utf8 -c "
import openpyxl, os, json
from openpyxl.drawing.image import Image as XLImage

data = json.loads('''RESULTS_JSON''')
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')

if 'Evidence' in wb.sheetnames:
    del wb['Evidence']
ws_ev = wb.create_sheet('Evidence')

ws_ev['A1'] = 'Test Case ID'
ws_ev['B1'] = 'Screenshot'

IMG_WIDTH_PX = 800
IMG_HEIGHT_PX = 450
ws_ev.column_dimensions['A'].width = 30
ws_ev.column_dimensions['B'].width = IMG_WIDTH_PX / 7

for i, item in enumerate(data, start=2):
    ws_ev.cell(row=i, column=1).value = item['id']
    screenshotPath = item.get('screenshotPath', '')
    if not screenshotPath or not os.path.exists(screenshotPath):
        ws_ev.cell(row=i, column=2).value = 'Screenshot not captured'
        continue
    img = XLImage(screenshotPath)
    img.width = IMG_WIDTH_PX
    img.height = IMG_HEIGHT_PX
    ws_ev.row_dimensions[i].height = IMG_HEIGHT_PX * 0.75
    ws_ev.add_image(img, f'B{i}')

wb.save('PATH_TO_FILE.xlsx')
print('done')
"
```

### Step 9 - Close browser and print summary

Close browser:
```
mcp__playwright__browser_close()
```

Print:
```
=== Frontend Test Summary ===
Total validate cases run: {n}
PASS:   {n}
FAIL:   {n}
ERROR:  {n}

Groups executed: {n} validate groups
Functional cases skipped: {n}

Results written to: {filePath}
Evidence sheet: updated with {n} screenshots
```

---

## Screenshot path rules

- Format: `{screenshotDir}/{testId}_{yyyyMMdd_HHmmss}.png`
- `screenshotDir` = `screenshots/` relative to the xlsx file location
- Timestamp generated at START of execution run, reused for all cases in the run
- Replace spaces and special chars in test ID with `_`

---

## Error Classification

| Condition | Result | Message |
|-----------|--------|---------|
| TestCase sheet not found | STOP | `Sheet "TestCase" not found` |
| Precondition failed | ERROR | `Precondition failed: {detail}` |
| Locator not found in DOM | ERROR | `Locator not found: {field_name}` |
| Batch script error | ERROR | `Batch script error: {detail}` |
| Assertion failed | FAIL | `{assertionType} failed on "{selector}" - {detail}` |
| All passed | PASS | (empty) |

---

## Guardrails

- **NEVER** modify columns A-F.
- **NEVER** write results for "Kiem tra chuc nang" cases.
- **NEVER** skip writing results for executed validate cases.
- **NEVER** re-execute rows with Result already set unless instructed.
- **ALWAYS** close browser after all groups finish.
- **NEVER** write temp scripts to disk.
- Save `.xlsx` only after ALL results collected (1 save operation).
- Do not stop the entire batch if one test case's locator is not found - mark it ERROR and continue.

---

## Anti-loop

Stop and ask user if:
- TestCase sheet not found in file
- Column B (Test Case ID) not found in file
- Same batch script error occurs 2+ times in a row for the same group
- Screenshot embed fails for all cases
