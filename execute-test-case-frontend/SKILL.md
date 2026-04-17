---
name: execute-test-case-frontend
description: Execute frontend/UI validate test cases from a Google Sheets URL or local Excel (.xlsx) file. Scans the live DOM, generates a Playwright script via LLM, executes batch per field group, writes PASS/FAIL + screenshots back to source. Only executes rows where Name contains "Validate". Triggers when user says "execute frontend test", "run FE test", "chạy test case frontend", or provides a Google Sheets URL / .xlsx path with frontend test data.
---

# Execute Test Case — Frontend

Reads validate test cases from **Google Sheets** (preferred) or local `.xlsx`, scans the live DOM, generates and runs a Playwright script per field group, writes results back.

**Flow:** Read Cases → DOM Snapshot → Generate Script → Execute → Write Results

**Scope:** Only rows where Name (col B) contains `"Validate"` / `"validate"`. All other rows are ignored.

---

## Prerequisites

- Playwright MCP configured
- Google Sheets MCP configured (for Google Sheets input)
- `openpyxl` installed (`pip show openpyxl`) — for xlsx input only

---

## Input Parameters

| Parameter | Description |
|-----------|-------------|
| `url` | URL of the web page under test (required) |
| `source` | Google Sheets URL **or** path to local `.xlsx` file |

---

## Column Layout (Google Sheets / Excel)

| Col | Index | Field | Notes |
|-----|-------|-------|-------|
| A | 0 | External ID / Section | Empty or section header; skip non-FE rows |
| B | 1 | Name | Test case name — filter: contains "Validate" AND starts with "FE_" |
| C | 2 | PreConditions | Login steps / navigation preconditions |
| D | 3 | Importance | High / Medium / Low |
| E | 4 | Steps | Natural language test steps |
| F | 5 | Data test | Input data for the test (may be empty) |
| G | 6 | Expected Result | Natural language expected outcome |
| H | 7 | Actual Result | **Write:** observed behavior |
| I | 8 | Lần 1 (Chrome) | **Write: P (pass) / F (fail) / E (error)** |

Pending = col I (Lần 1) is empty.
Skip rows already having a value in col I.

---

## Workflow

### Step 1 — Read test cases from source

**If Google Sheets URL:**

```
spreadsheetId = extract from URL (the long ID between /d/ and /edit)
mcp__gsheets__read_all_from_sheet(spreadsheetId="{id}", sheetName="{sheetName}")
```

Parse the returned rows. Filter:
- Col B (index 1) starts with `"FE_"` AND contains `"Validate"` (case-insensitive)
- Col I (index 8) is empty (not yet executed)

**If .xlsx file:**

```bash
python3 -X utf8 -c "
import openpyxl, json
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')
ws = wb['TestCase'] if 'TestCase' in wb.sheetnames else wb[wb.sheetnames[0]]
rows = []
for i, row in enumerate(ws.iter_rows(min_row=1, values_only=True), start=1):
    name = str(row[1] or '').strip()
    if name.startswith('FE_') and 'validate' in name.lower():
        done = row[8]  # col I
        if not done:
            rows.append({'row': i, 'name': name, 'precondition': str(row[2] or ''),
                         'steps': str(row[4] or ''), 'data': str(row[5] or ''),
                         'expected': str(row[6] or '')})
print(json.dumps(rows, ensure_ascii=False))
"
```

Print:
```
Loaded {total} validate pending cases, {skipped} already executed / non-validate skipped
```

---

### Step 2 — Group by field

Extract the field name from each test case name using the pattern:
`FE_{N}_Kiểm tra Validate_{FIELD}_{subtest}`

Group cases by `{FIELD}`. Each unique field = one execution group. Maintain row order.

Print:
```
Validate groups:
  Group 1: "{field}" — {n} cases
  Group 2: "{field}" — {n} cases
  ...
```

---

### Step 3 — Navigate + handle precondition

For the **first group only** (or whenever the URL changes), execute the precondition from col C of the first test case. Common precondition pattern:
- Login: extract credentials and login URL from the precondition text
- Navigate to: extract the menu path (e.g. "Thẻ > Quản lý yêu cầu thẻ")

Navigate to the target `url` and execute any required precondition steps using Playwright MCP tools. If precondition fails, mark all cases in that group ERROR and skip.

Reuse the same browser session across all groups — do NOT re-login between groups.

---

### Step 4 — Scan DOM to extract form structure

```
mcp__playwright__browser_evaluate(function="() => {
  const fields = [];
  document.querySelectorAll('input,select,textarea,button,[role=combobox],[role=listbox],[role=option],[role=textbox],[role=spinbutton]').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;
    const e = {
      tag: el.tagName.toLowerCase(),
      type: el.type || null,
      id: el.id || null,
      name: el.name || null,
      placeholder: el.placeholder || null,
      ariaLabel: el.getAttribute('aria-label') || null,
      dataTestid: el.getAttribute('data-testid') || null,
      role: el.getAttribute('role') || null,
      text: el.tagName === 'BUTTON' ? (el.textContent||'').trim().slice(0,60) : null,
      className: el.className?.split(' ').slice(0,3).join(' ') || null
    };
    Object.keys(e).forEach(k => e[k] === null && delete e[k]);
    fields.push(e);
  });
  return JSON.stringify(fields);
}")
```

---

### Step 5 — Generate Playwright batch script (per group)

Send this prompt to yourself (LLM) to generate a single `async (page) => {}` function for all cases in the group:

```
You are a Playwright test automation engineer writing a batch script.

## DOM Structure (compact JSON)
{DOM_SNAPSHOT_JSON}

## Target URL
{url}

## Test Cases
{TEST_CASES_JSON}
Each case: { rowIndex, name, steps, data, expected, screenshotPath }

## Script Requirements
1. Generate a single `async (page) => { return JSON.stringify(results); }` function.
2. Before each test case: navigate back to `{url}` if needed (only navigate if page URL has changed).
3. Use most specific locator: id → aria-label → placeholder → data-testid → name → visible text.
4. For textbox validation cases:
   - Clear the field first, then type/paste the test data
   - For "paste" cases: use page.evaluate to set clipboard then Ctrl+V
   - For "emoji/XSS/SQL/unicode" blocked cases: verify field value stays empty after input
5. For combobox cases: click to open, then click the desired option
6. For date picker cases: click the field, type the date value
7. After each test case action: await page.waitForTimeout(300)
8. Screenshot after each case: await page.screenshot({ path: tc.screenshotPath, fullPage: false })
9. Determine PASS/FAIL programmatically:
   - "chặn không cho phép nhập" → PASS if field value unchanged / empty after typing
   - "cho phép nhập" → PASS if field value equals typed text
   - "hiển thị icon X" → PASS if clear button element is visible
   - "clear data" → PASS if field value is empty after click
   - "hiển thị thông báo lỗi" → PASS if error message element is visible
   - "mặc định rỗng" → PASS if field value is empty
   - "luôn hiển thị và enable" → PASS if element is visible and not disabled
   - "placeholder" text → PASS if placeholder attribute matches expected text
   - "mặc định" value → PASS if field/combobox shows the expected default value
   - For combobox filter cases → PASS if grid/list updates (row count changes or items visible)
10. Each result: { rowIndex, name, result: 'P'|'F'|'E', actual: string, error: string, screenshotPath }
11. Try/catch per test case. Never throw; catch → result 'E' with error message.
12. Output ONLY the code. No markdown. No explanation.
```

---

### Step 6 — Execute the generated script

```
mcp__playwright__browser_run_code(code="{GENERATED_SCRIPT}")
```

Parse returned JSON. If entire script fails: mark all cases in group as `E: "Batch script error: {detail}"`.

---

### Step 7 — Repeat Steps 4-6 for remaining groups

---

### Step 8 — Write results back to source

**If Google Sheets:**

For each result, update 2 cells:
```
mcp__gsheets__edit_cell(spreadsheetId="{id}", sheetName="{sheet}", row={row+1}, col=9, value="{P|F|E}")    # col I = Lần 1
mcp__gsheets__edit_cell(spreadsheetId="{id}", sheetName="{sheet}", row={row+1}, col=8, value="{actual}")   # col H = Actual Result
```

Note: rows in gsheets MCP are 1-indexed. Add 1 to the 0-indexed row from step 1.

**If xlsx:**

```bash
python3 -X utf8 -c "
import openpyxl, json
data = json.loads('''RESULTS_JSON''')
wb = openpyxl.load_workbook('PATH_TO_FILE.xlsx')
ws = wb['TestCase'] if 'TestCase' in wb.sheetnames else wb[wb.sheetnames[0]]
for item in data:
    row = item['row']
    ws.cell(row=row, column=9).value = item['result']      # col I
    ws.cell(row=row, column=8).value = item.get('actual', '')  # col H
wb.save('PATH_TO_FILE.xlsx')
print('done')
"
```

---

### Step 9 — Close browser and print summary

```
mcp__playwright__browser_close()
```

```
=== Frontend Validate Test Summary ===
Total executed : {n}
PASS  (P)      : {n}
FAIL  (F)      : {n}
ERROR (E)      : {n}

Groups executed: {n}
Results written to: {source}
Screenshots: {screenshotDir}/
```

---

## Screenshot path rules

- Format: `{screenshotDir}/{safe_name}_{yyyyMMdd_HHmmss}.png`
- `screenshotDir` = `screenshots/` relative to xlsx, or `C:/Users/{user}/Downloads/screenshots/` for Google Sheets
- `safe_name` = test case name with spaces/special chars replaced by `_`, truncated to 60 chars
- Timestamp generated at START of run, reused for all cases

---

## Error Classification

| Condition | Result | Note |
|-----------|--------|------|
| Precondition failed | E | Skip group, mark all cases ERROR |
| Locator not found | E | Continue to next case |
| Batch script error | E | Mark all in group, continue to next group |
| Field blocked input as expected | P | |
| Field allowed input as expected | P | |
| Behavior did not match expected | F | |

---

## Guardrails

- **NEVER** modify cols A-G (read-only).
- **ONLY** write to col H (Actual Result) and col I (Lần 1 / Chrome result).
- **NEVER** re-execute rows where col I already has a value.
- **NEVER** write results for non-Validate cases.
- **ALWAYS** close browser after all groups finish.
- **DO NOT** re-login between groups — reuse the browser session.
- Save all results in 1 batch write (not cell-by-cell for xlsx).
- For Google Sheets: use `mcp__gsheets__edit_cell` per cell (no batch option).
- Stop and ask user if: source not found, login fails, same batch script error repeats 2+ times for same group.
