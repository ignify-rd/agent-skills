# execute-test-case-frontend — Agent Rules

These rules apply when the `execute-test-case-frontend` skill is active. A project-level `AGENTS.md` may override values in the **Override scope** table but may not override the guardrails section.

---

## Override scope

| Setting | Default | Project can override? |
|---|---|---|
| Sheet tab name | `Frontend Tests` | Yes |
| Step timeout | 5000ms | Yes |
| Wait timeout | 3000ms | Yes |
| Screenshot folder | `screenshots/` | Yes |
| Skip already-executed rows | true | Yes |
| Entry state reset selector | Last `wait_for` in precondition steps | Yes — set `entry_selector` in project AGENTS.md |
| Continue on assertion failure | false (stop at first) | Yes |
| Max batch size (subagent) | 5 | Yes — controls how many test cases per subagent (lower = less tokens, more overhead) |

---

## Browser session management

### Core principle: minimal context execution

The goal is to run as many test cases as possible without re-doing login or navigation. Execute preconditions **once per consecutive group**, then reuse the session.

### Session lifecycle

```
Group starts       → execute precondition steps → record entryUrl + entrySelector
  Case N (first)   → execute test steps (no reset needed)
  Case N+1         → navigate to entryUrl, wait for entrySelector, then test steps
  Case N+2         → navigate to entryUrl, wait for entrySelector, then test steps
  ...
Group ends         → mcp__playwright__browser_close()
Next group starts  → fresh browser, new preconditions
```

### Entry state reset

Before each test case (except the first in a group):
1. Call `mcp__playwright__browser_navigate(url=entryUrl)`
2. Call `mcp__playwright__browser_wait_for(selector=entrySelector, timeout=waitTimeout)`
3. If this fails → ERROR for current test case: `"Entry reset failed — session may have expired"`. Close browser. Remaining cases in group → ERROR with same message. Move to next group.

### When to force a full reset

Force full precondition re-execution (even within a group) if:
- Entry reset fails (session expired, page unresponsive)
- Browser process crashes or becomes unresponsive
- `mcp__playwright__browser_snapshot` returns an error

In these cases: close browser, re-execute preconditions, mark the failed case as ERROR.

---

## Step execution

### Action → Playwright MCP tool mapping

| Action | Tool | Key params |
|---|---|---|
| `goto` | `mcp__playwright__browser_navigate` | `url` |
| `click` | `mcp__playwright__browser_click` — use snapshot first to get `ref` | `ref`, `element` |
| `fill` | `mcp__playwright__browser_type` | `ref`, `text` |
| `select` | `mcp__playwright__browser_select_option` | `ref`, `values` |
| `wait_for` | `mcp__playwright__browser_wait_for` | `selector`, `timeout` |
| `hover` | `mcp__playwright__browser_hover` | `ref` |
| `press_key` | `mcp__playwright__browser_press_key` | `key` |
| `snapshot` | `mcp__playwright__browser_snapshot` | — |
| `scroll` | `mcp__playwright__browser_evaluate` with `window.scrollTo` | — |

For `click` and `fill`: always call `mcp__playwright__browser_snapshot` first to get element refs, then use the ref in the action call. Do not use CSS selectors directly in action tools.

### Timeout handling

- Apply per-step timeout (default 5000ms) to all actions that wait for something (`wait_for`, `click` on dynamic elements).
- If a step times out → step ERROR, stop executing steps, capture screenshot.

---

## Assertion evaluation

Use `mcp__playwright__browser_snapshot` to get current page accessibility tree, then evaluate:

| Type | How to evaluate |
|---|---|
| `visible` | selector must appear in snapshot with no `hidden` attribute |
| `not_visible` | selector must not appear in snapshot, or appear with `hidden` |
| `text_contains` | element text (from snapshot) contains the value string |
| `text_equals` | element text exactly equals the value string |
| `url_contains` | current page URL contains the value string |
| `url_equals` | current page URL exactly equals the value string |
| `count` | number of matching elements equals the expected count |

If snapshot cannot be taken → ERROR: `"Cannot take snapshot for assertions"`.

---

## Evidence sheet

- Tab name: `"Evidence"` (non-configurable — shared with API test runs in the same spreadsheet).
- Create on first run if not present; write header row `Test ID | Screenshot`.
- Pre-populate column A with all test case IDs. Build `evidenceMap: testId → row number`.
- Subagents write `=IMAGE()` formula to column B at the pre-mapped row for each test case.
- Never overwrite evidence rows that already have a screenshot (column B non-empty).

## Screenshot settings

- Always capture after test steps complete (regardless of PASS/FAIL/ERROR).
- Use `mcp__playwright__browser_take_screenshot(type="png", filename="{testId}_{yyyyMMdd_HHmmss}.png")`.
- Store in the configured `screenshot_folder` (default: `screenshots/`).
- Write the file path (relative to working directory) to column I.
- If screenshot fails → write `"screenshot_failed"` to column I, do not block result writing.

---

## Error classification

| Condition | Result | Error message format |
|---|---|---|
| Precondition step failed | ERROR | `Precondition failed: step {n} — {detail}` |
| Entry state reset failed | ERROR | `Entry reset failed: {detail}` |
| Browser step failed/timed out | ERROR | `Step {n} failed: {action} on "{selector}" — {detail}` |
| Assertion failed | FAIL | `Assertion failed: {type} on "{selector}" — {detail}` |
| All assertions passed | PASS | (empty) |

---

## Guardrails (non-overridable)

- NEVER modify columns A–F.
- NEVER skip writing a result row, even on ERROR.
- NEVER re-execute a row with a non-empty Result (column G) unless explicitly instructed.
- ALWAYS close the browser after each group completes or errors.
- NEVER store passwords in screenshot filenames or error messages.
- **NEVER write temp/helper scripts to disk** (`_*.py`, `_*.ps1`, `_check_*.py`, etc.) — use `python3 -X utf8 -c "..."` inline in Bash, or use Read/Edit/Write tools directly.
