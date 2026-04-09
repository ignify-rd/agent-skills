---
name: execute-test-case-frontend
description: Execute frontend/UI test cases from a local Excel (.xlsx) file using Playwright. Reads test rows, groups consecutive validation cases by page to reduce token usage, performs browser interactions, validates page state against descriptions, captures screenshots, and writes PASS/FAIL back to the .xlsx file. Triggers when user says "execute frontend test", "run FE test cases", "chạy test case frontend", or provides a path to an .xlsx file with frontend test data.
---

# Execute Test Case — Frontend

Reads frontend test cases from a local `.xlsx` file, executes each via Playwright browser, and writes results back.

**Key optimization:** Consecutive validation test cases on the same page are grouped and executed in a single `browser_run_code` call — reducing individual MCP tool calls by ~70%.

**Execution:** Sequential groups, each group = 1 `browser_run_code` batch.

---

## Prerequisites

- **Playwright MCP** configured
- `openpyxl` installed (`pip show openpyxl`)
- Local `.xlsx` file accessible
- Sheet tab: `TestCase` (or first sheet if not found)

---

## ⛔ Temp File Rules

**NEVER** write helper/temp scripts to disk. Use `python3 -X utf8 -c "..."` inline only.

---

## Column Layout

| Col | Field | Notes |
|-----|-------|-------|
| A | Test Suite | Suite grouping |
| B | Test Case ID | e.g. `FE-001` |
| C | Title | Short description |
| D | Precondition | Natural language or URL to navigate first |
| E | Steps | JSON array — actions for this test case |
| F | Assertions | JSON array — validation rules |
| G | Result | **Agent writes: PASS / FAIL / ERROR** |
| H | Error Message | **Agent writes** |
| I | Screenshot | **Agent writes: file path** |
| J | Executed At | **Agent writes: ISO 8601** |

Skip rows where column B (Test Case ID) is empty.
Pending = column G empty.

---

## Step Format (column E)

JSON array of action objects:

```json
[
  { "action": "goto", "url": "https://example.com/login" },
  { "action": "fill", "selector": "input[name=username]", "value": "admin" },
  { "action": "click", "selector": "button[type=submit]" },
  { "action": "wait_for", "selector": ".dashboard", "timeout": 5000 },
  { "action": "press_key", "key": "Enter" },
  { "action": "select", "selector": "select#role", "value": "admin" },
  { "action": "scroll", "direction": "down", "amount": 300 }
]
```

## Assertion Format (column F)

```json
[
  { "type": "visible", "selector": ".error-msg" },
  { "type": "not_visible", "selector": ".success-toast" },
  { "type": "text_contains", "selector": ".error-msg", "value": "required" },
  { "type": "text_equals", "selector": "h1", "value": "Dashboard" },
  { "type": "url_contains", "value": "/dashboard" },
  { "type": "url_equals", "value": "https://example.com/dashboard" },
  { "type": "count", "selector": ".item", "expected": 3 }
]
```

---

## Workflow

### Step 1 — Read test cases from .xlsx

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
        'suite': row[0],
        'id': testId,
        'title': row[2],
        'precondition': row[3] or '',
        'steps': row[4] or '[]',
        'assertions': row[5] or '[]',
        'status': row[6]
    })
print(json.dumps(results, ensure_ascii=False))
"
```

Print:
```
Loaded {total} test cases: {pending} pending, {done} already executed (skipping)
```

### Step 2 — Filter (optional)

User may specify range (`FE-001 to FE-010`), list (`FE-003, FE-007`), or re-run failures. If not specified → run all pending.

### Step 3 — Group and optimize

**Validation Group Detection:**

A set of consecutive test cases can be grouped if they share the same entry URL (same `precondition`) AND each case consists only of **field validation actions** (fill/type a field value and check for validation message).

Heuristic: a case is a "validation case" if:
- Steps contain only `fill`/`type` actions (no `goto`, no `click` on submit/save buttons)
- OR steps contain `fill` + `click submit` with assertions checking for error messages

**Grouping rule:**
1. Sort pending cases by sheet row order.
2. Scan for consecutive runs of validation cases with the same `precondition` URL.
3. Each such run = 1 **Validation Group** (executed in 1 `browser_run_code` call).
4. Non-validation cases (complex flows) = Solo Group (1 case per execution block).

Print grouping summary:
```
Groups formed:
  Validation Group 1: FE-001 to FE-008 (8 cases, same form) → 1 browser_run_code call
  Solo: FE-009 (complex flow)
  Validation Group 2: FE-010 to FE-014 (5 cases) → 1 browser_run_code call
```

---

### Step 4 — Execute precondition (per group)

For the first case in each group, execute precondition steps:
- If `precondition` is a URL string → navigate to it
- If `precondition` is a JSON array of actions → execute each action using Playwright tools

```
mcp__playwright__browser_navigate(url="{preconditionUrl}")
mcp__playwright__browser_wait_for(selector="body", timeout=5000)
```

Take snapshot. Record `entryUrl` (current URL after precondition).

If precondition fails → mark ALL cases in this group as ERROR: `"Precondition failed: {detail}"` → skip group.

---

### Step 5 — Execute groups

#### 5A — Solo group (complex flow)

Execute step-by-step using individual MCP tool calls:

```
snapshot → mcp__playwright__browser_snapshot()
```

For each step in `steps` JSON:
- `goto` → `mcp__playwright__browser_navigate(url=...)`
- `back` → `mcp__playwright__browser_navigate_back()`
- `click` → snapshot first, then `mcp__playwright__browser_click(ref=..., element=...)`
- `fill` → snapshot first, then `mcp__playwright__browser_type(ref=..., text=...)`
- `fill_form` → `mcp__playwright__browser_fill_form(fields=[...])`
- `select` → `mcp__playwright__browser_select_option(ref=..., values=...)`
- `wait_for` → `mcp__playwright__browser_wait_for(selector=..., timeout=...)`
- `hover` → `mcp__playwright__browser_hover(ref=...)`
- `press_key` → `mcp__playwright__browser_press_key(key=...)`
- `scroll` → `mcp__playwright__browser_evaluate(script="window.scrollBy(0, 300)")`
- `handle_dialog` → `mcp__playwright__browser_handle_dialog(accept=true/false)`

After all steps → take snapshot → evaluate assertions:
- `visible` → check element present + not hidden
- `not_visible` → check element absent or hidden
- `text_contains` → check element text includes value
- `text_equals` → check element text exactly equals value
- `url_contains` → check `page.url()` includes value
- `url_equals` → check `page.url()` exactly equals value
- `count` → check matching element count equals expected

Take screenshot:
```
mcp__playwright__browser_take_screenshot(type="png", filename="{screenshotPath}")
```

Collect result.

#### 5B — Validation group (batch)

Build a single `browser_run_code` script that loops through all cases in the group:

```js
async (page) => {
  const entryUrl = "{entryUrl}";
  const cases = [
    {
      id: "FE-001",
      title: "Validate required field",
      screenshotPath: "screenshots/FE-001_20240101_120000.png",
      steps: [
        { action: "fill", selector: "input[name=email]", value: "" },
        { action: "click", selector: "button[type=submit]" }
      ],
      assertions: [
        { type: "visible", selector: ".field-error" },
        { type: "text_contains", selector: ".field-error", value: "required" }
      ]
    }
    // ... more cases
  ];

  const results = [];

  for (const tc of cases) {
    // Reset to entry state (navigate back)
    await page.goto(entryUrl);
    await page.waitForTimeout(1000);

    let stepError = null;
    try {
      for (const step of tc.steps) {
        if (step.action === 'fill') {
          const el = page.locator(step.selector).first();
          await el.fill(step.value ?? '');
        } else if (step.action === 'click') {
          await page.locator(step.selector).first().click();
        } else if (step.action === 'select') {
          await page.locator(step.selector).first().selectOption(step.value);
        } else if (step.action === 'press_key') {
          await page.keyboard.press(step.key);
        } else if (step.action === 'wait_for') {
          await page.waitForSelector(step.selector, { timeout: step.timeout || 5000 });
        }
        await page.waitForTimeout(300);
      }
    } catch (e) {
      stepError = e.message;
    }

    await page.screenshot({ path: tc.screenshotPath });

    if (stepError) {
      results.push({ id: tc.id, result: 'ERROR', error: stepError, screenshot: tc.screenshotPath });
      continue;
    }

    // Evaluate assertions
    const assertionErrors = [];
    for (const a of tc.assertions) {
      try {
        if (a.type === 'visible') {
          const count = await page.locator(a.selector).count();
          if (count === 0) assertionErrors.push(`Expected visible: ${a.selector}`);
        } else if (a.type === 'not_visible') {
          const count = await page.locator(a.selector).count();
          if (count > 0) assertionErrors.push(`Expected not visible: ${a.selector}`);
        } else if (a.type === 'text_contains') {
          const text = await page.locator(a.selector).first().textContent() || '';
          if (!text.includes(a.value)) assertionErrors.push(`"${a.selector}" text "${text}" does not contain "${a.value}"`);
        } else if (a.type === 'text_equals') {
          const text = await page.locator(a.selector).first().textContent() || '';
          if (text.trim() !== a.value) assertionErrors.push(`"${a.selector}" text "${text}" !== "${a.value}"`);
        } else if (a.type === 'url_contains') {
          const url = page.url();
          if (!url.includes(a.value)) assertionErrors.push(`URL "${url}" does not contain "${a.value}"`);
        } else if (a.type === 'url_equals') {
          const url = page.url();
          if (url !== a.value) assertionErrors.push(`URL "${url}" !== "${a.value}"`);
        } else if (a.type === 'count') {
          const count = await page.locator(a.selector).count();
          if (count !== a.expected) assertionErrors.push(`"${a.selector}" count ${count} !== ${a.expected}`);
        }
      } catch (e) {
        assertionErrors.push(`Assertion error on "${a.selector}": ${e.message}`);
      }
    }

    if (assertionErrors.length === 0) {
      results.push({ id: tc.id, result: 'PASS', error: '', screenshot: tc.screenshotPath });
    } else {
      results.push({ id: tc.id, result: 'FAIL', error: assertionErrors.join('; '), screenshot: tc.screenshotPath });
    }
  }

  return JSON.stringify(results);
}
```

Run:
```
mcp__playwright__browser_run_code(code="<script above with cases populated>")
```

Parse returned JSON array.

**If script fails:** Check error. Common fixes:
- Selector not found → try broader selector or `page.getByLabel()` / `page.getByPlaceholder()`
- Timing issue → add `waitForTimeout(500)` before assertion
- Fix and retry once.

---

### Step 6 — Write results to .xlsx

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
    ws.cell(row=row, column=7).value = item['result']       # col G
    ws.cell(row=row, column=8).value = item['error']        # col H
    ws.cell(row=row, column=9).value = item['screenshot']   # col I
    ws.cell(row=row, column=10).value = now                 # col J

wb.save('PATH_TO_FILE.xlsx')
print('done')
"
```

### Step 7 — Embed screenshots into Evidence sheet

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
    if not item.get('screenshot') or not os.path.exists(item['screenshot']):
        ws_ev.cell(row=i, column=2).value = 'Screenshot not captured'
        continue
    img = XLImage(item['screenshot'])
    img.width = IMG_WIDTH_PX
    img.height = IMG_HEIGHT_PX
    ws_ev.row_dimensions[i].height = IMG_HEIGHT_PX * 0.75
    ws_ev.add_image(img, f'B{i}')

wb.save('PATH_TO_FILE.xlsx')
print('done')
"
```

### Step 8 — Cleanup & summary

Close browser:
```
mcp__playwright__browser_close()
```

Print:
```
=== Frontend Test Summary ===
Total:  {n}
PASS:   {n}
FAIL:   {n}
ERROR:  {n}

Groups executed:
  {n} validation groups ({n} cases) — batch execution
  {n} solo cases — step-by-step execution

Results written to: {filePath}
Evidence sheet: updated with {n} screenshots
```

---

## Batching large suites (> 20 cases)

Split pending cases into batches of 15-20. For each batch:
1. Detect validation groups within the batch
2. Execute batch groups sequentially
3. Continue to next batch

Write all results in 1 Python call after all batches.

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
| Step failed / timeout | ERROR | `Step failed: {action} on "{selector}" — {detail}` |
| Assertion failed | FAIL | `{assertionType} failed on "{selector}" — {detail}` |
| browser_run_code error | ERROR | `Batch script error: {detail}` |
| All passed | PASS | (empty) |

---

## Guardrails

- **NEVER** modify columns A–F.
- **NEVER** skip writing results.
- **NEVER** re-execute rows with Result already set unless instructed.
- **ALWAYS** close browser after all groups finish.
- **NEVER** write temp scripts to disk.
- Save `.xlsx` only after ALL results collected (1 save operation).

---

## Anti-loop

Stop and ask user if:
- TestCase sheet not found in file
- Column B (Test Case ID) not found
- Same blocker occurs 2+ times in a row in `browser_run_code`
- Screenshot embed fails for all cases
