---
name: execute-test-case-frontend
description: Execute frontend validate test cases directly using Playwright MCP — no scripts generated. Claude reads cases from Google Sheets, navigates the browser, interacts with the main content area (ignoring sidebar/header), takes screenshots, and writes P/F/E back to the sheet. Triggers when user says "execute frontend test", "run FE test", "chạy test case frontend", or provides a Google Sheets URL with test data.
---

# Execute Test Case — Frontend (Playwright MCP)

Claude drives the browser step-by-step using Playwright MCP tools. No Python script generation. Each test case is executed one-by-one with screenshot evidence.

**Scope:** Only rows where Name (col B) contains `"Validate"` and col I (Lần 1) is empty.

---

## Input Parameters

| Parameter | Description |
|-----------|-------------|
| `url` | URL of the page under test |
| `spreadsheetId` | Google Sheets ID (from URL: `/d/{ID}/edit`) |
| `sheetName` | Sheet tab name (default: first sheet) |

---

## Column Layout

| Col | Index | Field | Notes |
|-----|-------|-------|-------|
| A | 0 | External ID / Section | Section header or empty |
| B | 1 | Name | Filter: starts with `FE_` AND contains `"Validate"` |
| C | 2 | PreConditions | Login + navigation steps |
| D | 3 | Importance | High / Medium / Low |
| E | 4 | Steps | Test steps in Vietnamese |
| F | 5 | Data test | Input value (may be empty) |
| G | 6 | Expected Result | Expected behavior |
| H | 7 | Actual Result | **Write:** observed result |
| I | 8 | Lần 1 (Chrome) | **Write: P / F / E** |

---

## Main Screen Scope Rule

**CRITICAL:** All interactions must target the **main content area only**, NOT sidebar or header.

Before any interaction, identify the main content container:
```
mcp__playwright__browser_evaluate(function="() => {
  // Find the main content area — try common patterns
  const candidates = [
    document.querySelector('main'),
    document.querySelector('[role=\"main\"]'),
    document.querySelector('.main-content'),
    document.querySelector('.content-area'),
    document.querySelector('.page-content'),
    // Fallback: largest visible div that is NOT header/nav/aside
    ...[...document.querySelectorAll('div')].filter(el => {
      const tag = el.tagName.toLowerCase();
      const r = el.getBoundingClientRect();
      const isNav = el.closest('header,nav,aside,[role=navigation],[role=banner]');
      return !isNav && r.width > 600 && r.height > 400;
    }).sort((a,b) => b.getBoundingClientRect().height - a.getBoundingClientRect().height)
  ].filter(Boolean);
  const main = candidates[0];
  return main ? {
    tag: main.tagName,
    id: main.id,
    className: main.className?.split(' ').slice(0,4).join(' '),
    rect: main.getBoundingClientRect()
  } : null;
}")
```

Use the identified main container selector for all subsequent `browser_evaluate` and `browser_click` calls. Never click elements inside `header`, `nav`, `aside`, or `[role=navigation]`.

---

## Workflow

### Step 1 — Read test cases

```
mcp__gsheets__read_all_from_sheet(spreadsheetId="{id}", sheetName="{sheet}")
```

Parse rows. Build list of pending validate cases:
- `row[1]` starts with `"FE_"` AND contains `"validate"` (case-insensitive)
- `row[8]` (col I) is empty/null

Extract field groups from name pattern: `FE_{N}_Kiểm tra Validate_{FIELD}_{subtest}`

Print:
```
{total} validate pending cases across {n} field groups:
  - {FIELD}: {n} cases
  ...
```

---

### Step 2 — Navigate and login

```
mcp__playwright__browser_navigate(url="{url}")
```

Read precondition from first test case (col C). Execute login steps if needed:
- Extract credentials from precondition text (e.g. `account 28980/ Test@147258`)
- Fill login form, click submit
- Navigate to the target screen (follow menu path from precondition, e.g. "Thẻ > Quản lý yêu cầu thẻ")

**Do NOT re-login between test cases or groups.**

---

### Step 3 — Scan main content DOM (once per field group)

After navigating to the target screen, scan ONLY the main content area:

```
mcp__playwright__browser_evaluate(function="() => {
  // Scope to main content only
  const main = document.querySelector('main, [role=\"main\"], .main-content, .content-area')
           || document.body;
  const fields = [];
  main.querySelectorAll('input,select,textarea,[role=combobox],[role=textbox],[role=spinbutton],button').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    // Skip elements inside header/nav/sidebar
    if (el.closest('header,nav,aside,[role=navigation],[role=banner],[role=toolbar]')) return;
    fields.push({
      tag: el.tagName.toLowerCase(),
      type: el.type || null,
      id: el.id || null,
      placeholder: el.placeholder || null,
      ariaLabel: el.getAttribute('aria-label') || null,
      dataTestid: el.getAttribute('data-testid') || null,
      role: el.getAttribute('role') || null,
      text: (el.textContent||'').trim().slice(0,40) || null,
      rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }
    });
  });
  return JSON.stringify(fields.filter(f => Object.values(f).some(v => v !== null)));
}")
```

Use this snapshot to resolve locators for each test case in the group.

---

### Step 4 — Execute each test case

For each pending test case, in order:

#### 4a. Interpret the test case

From `name`, `steps`, `data`, `expected` — determine:
- **Field to target**: from the field group name (e.g. `textbox "Tìm kiếm nhanh"`)
- **Action**: type / paste / click / observe / select
- **Input data**: from `data` column or implied by name (e.g. "emoji", "39 ký tự", "SQL injection")
- **Verification**: from `expected` — what to check after the action

#### 4b. Perform the action

Use the appropriate Playwright MCP tool. Always scope to main content area.

**For textbox — type input:**
```
mcp__playwright__browser_click(element="...", ref="...")   # focus the field
mcp__playwright__browser_type(text="{data}")
```

**For textbox — paste input:**
```
mcp__playwright__browser_evaluate(function="() => {
  const el = document.querySelector('{selector_in_main}');
  el.focus();
  // Set clipboard
  return navigator.clipboard.writeText('{data}').then(() => 'ok').catch(e => e.message);
}")
mcp__playwright__browser_press_key(key="Control+v")
```

**For textbox — clear then retype:**
```
mcp__playwright__browser_triple_click → then type new value
```
Or use:
```
mcp__playwright__browser_evaluate(function="() => { const el = ...; el.value = ''; el.dispatchEvent(new Event('input')); }")
mcp__playwright__browser_type(text="{data}")
```

**For combobox — select option:**
```
mcp__playwright__browser_click(element="combobox {field_name}")
mcp__playwright__browser_click(element="option {value}")
```

**For date picker — type date:**
```
mcp__playwright__browser_click(element="date input {field_name}")
mcp__playwright__browser_type(text="{dd/mm/yyyy}")
mcp__playwright__browser_press_key(key="Tab")
```

**For observe only (no action):**
Proceed directly to verification + screenshot.

#### 4c. Wait briefly

```
mcp__playwright__browser_wait_for(time=500)
```

#### 4d. Verify result

Use `browser_evaluate` scoped to main content to check the expected outcome:

| Expected pattern | Verification |
|-----------------|--------------|
| `chặn không cho phép nhập` | field value === '' or === original value |
| `cho phép nhập` | field value === typed text |
| `hiển thị icon X / xóa nhanh` | clear-button element visible in main area |
| `Clear data` | field value === '' after click |
| `hiển thị thông báo lỗi` | error message element visible in main area |
| `mặc định rỗng` | field value === '' |
| `luôn hiển thị và enable` | element visible AND not disabled |
| `placeholder` text match | element.placeholder === expected text |
| `mặc định` value | combobox text/value === expected default |
| `lưới hiển thị` / filter result | table row count > 0 OR specific items visible |

```
mcp__playwright__browser_evaluate(function="() => {
  const main = document.querySelector('main,[role=\"main\"],.main-content') || document.body;
  // Run specific check based on test case
  ...
  return { pass: true/false, actual: '...' };
}")
```

#### 4e. Take screenshot

```
mcp__playwright__browser_take_screenshot(filename="{safe_name}_{timestamp}.png")
```

Screenshot captures full page visible area. Note the returned file path.

#### 4f. Determine verdict and write to sheet

```
mcp__gsheets__edit_cell(spreadsheetId="{id}", sheetName="{sheet}", row={row_1indexed}, col=9, value="P")  # or F or E
mcp__gsheets__edit_cell(spreadsheetId="{id}", sheetName="{sheet}", row={row_1indexed}, col=8, value="{actual_observed}")
```

Print per case:
```
  [{idx}/{total}] {name_short}
    Action: {action}  →  Actual: {actual}  →  {P/F/E}
```

---

### Step 5 — Reset field between test cases

After each test case that modifies a field, reset it to empty state before the next case:
- **Textbox**: clear value + trigger input event
- **Combobox**: click X (clear) button if visible, otherwise select default "Tất cả"
- **Date picker**: click X button or clear manually

---

### Step 6 — Close browser and print summary

```
mcp__playwright__browser_close()
```

```
=== Frontend Validate Test Summary ===
Total executed : {n}
PASS  (P)      : {n}
FAIL  (F)      : {n}
ERROR (E)      : {n}

Results written to Google Sheets: {spreadsheetId}
```

---

## Locator Priority (within main content only)

1. `data-testid` attribute
2. `aria-label` attribute  
3. `placeholder` attribute (for text inputs)
4. `id` attribute
5. Visible text content (for buttons/options)
6. Position/rect (fallback — use bounding box from DOM snapshot)

**Never** use locators that match elements in `header`, `nav`, `aside`, or `[role=navigation]`.

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Login fails | Stop, report to user |
| Element not found in main area | Mark E, `"Element not found: {field}"`, continue |
| Action has no effect (field still empty when should allow) | Mark F |
| Unexpected dialog/popup | Dismiss, then retry once |
| Entire group fails | Mark all in group E, continue to next group |

---

## Guardrails

- **NEVER** modify col A–G (read only).
- **ONLY** write to col H (Actual) and col I (Lần 1).
- **NEVER** re-execute rows where col I already has a value.
- **NEVER** interact with sidebar, header, or navigation elements.
- **DO NOT** re-login between groups — reuse the session.
- **ALWAYS** reset fields between test cases to avoid state bleed.
- Stop and ask user if: login fails, main content area cannot be identified, same error repeats 3+ times.
