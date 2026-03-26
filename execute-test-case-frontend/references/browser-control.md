# Browser Control — Playwright MCP Reference

## Core pattern: snapshot → ref → act

Playwright MCP actions that interact with elements (`click`, `fill`, `select`, etc.) require an element `ref` from the accessibility snapshot. Always:

1. Call `mcp__playwright__browser_snapshot` to get the current page state
2. Find the element by matching `selector` against the snapshot output
3. Use the `ref` value in the action call

**Do not** use CSS selectors directly in action tool parameters — they only accept refs.

---

## Tool reference

### Navigation

#### `mcp__playwright__browser_navigate`
Navigate to a URL.
```
mcp__playwright__browser_navigate(url="https://example.com")
```

#### `mcp__playwright__browser_navigate_back`
Go to the previous page.
```
mcp__playwright__browser_navigate_back()
```

---

### Page inspection

#### `mcp__playwright__browser_snapshot`
Returns the page accessibility tree as YAML. Use this to:
- Find element refs for interaction
- Evaluate `visible` / `text_contains` / `text_equals` assertions
- Verify page state after an action

```
mcp__playwright__browser_snapshot()
```

Returns snapshot YAML. Parse it to find element refs and text content.

#### `mcp__playwright__browser_take_screenshot`
Capture the current viewport as PNG.
```
mcp__playwright__browser_take_screenshot(
  type="png",
  filename="screenshots/FE-001_20260326_143000.png"
)
```

---

### Interactions

#### `mcp__playwright__browser_click`
Click an element by ref.
```
# 1. Get snapshot
snapshot = mcp__playwright__browser_snapshot()
# 2. Find ref matching selector (e.g. button with text "Submit")
# 3. Click
mcp__playwright__browser_click(ref="e42", element="Submit button")
```

#### `mcp__playwright__browser_type`
Type text into an input by ref.
```
mcp__playwright__browser_type(ref="e18", text="admin@test.com")
```

To submit after typing (press Enter):
```
mcp__playwright__browser_type(ref="e18", text="search query", submit=True)
```

#### `mcp__playwright__browser_fill_form`
Fill multiple form fields at once.
```
mcp__playwright__browser_fill_form(fields=[
  {"name": "Email", "type": "textbox", "ref": "e18", "value": "admin@test.com"},
  {"name": "Password", "type": "textbox", "ref": "e21", "value": "Admin@123"}
])
```

#### `mcp__playwright__browser_select_option`
Select a dropdown option by ref.
```
mcp__playwright__browser_select_option(ref="e33", values=["ACTIVE"])
```

#### `mcp__playwright__browser_hover`
Hover over an element.
```
mcp__playwright__browser_hover(ref="e55", element="menu item")
```

#### `mcp__playwright__browser_press_key`
Press a keyboard key.
```
mcp__playwright__browser_press_key(key="Enter")
mcp__playwright__browser_press_key(key="Escape")
mcp__playwright__browser_press_key(key="Tab")
```

---

### Waiting

#### `mcp__playwright__browser_wait_for`
Wait for a condition to be true. Use after navigation or actions that trigger page changes.
```
mcp__playwright__browser_wait_for(selector=".dashboard-header", timeout=5000)
```

- `timeout`: milliseconds (default 5000)
- Throws error if element not found within timeout → treat as step failure

---

### Advanced

#### `mcp__playwright__browser_evaluate`
Run JavaScript in the page context.
```
mcp__playwright__browser_evaluate(script="window.scrollTo(0, 0)")
mcp__playwright__browser_evaluate(script="document.querySelector('.modal').scrollTop = 0")
```

Use sparingly — prefer DOM-based tools when possible.

#### `mcp__playwright__browser_handle_dialog`
Accept or dismiss browser dialogs (alert, confirm, prompt).
```
mcp__playwright__browser_handle_dialog(accept=True)
mcp__playwright__browser_handle_dialog(accept=False)
```

Call this before the step that triggers the dialog.

---

### Session management

#### `mcp__playwright__browser_close`
Close the browser. Call at the end of each Precondition Group.
```
mcp__playwright__browser_close()
```

---

## Assertion evaluation using snapshot

After `mcp__playwright__browser_snapshot`, evaluate assertions against the YAML output:

| Assertion type | How to check |
|---|---|
| `visible` | Look for an element with matching role/text/selector in snapshot; it should not have a `hidden` flag |
| `not_visible` | Element should be absent from snapshot, or present with `hidden` attribute |
| `text_contains` | Find element in snapshot, check its text content contains the value |
| `text_equals` | Find element in snapshot, check its text content exactly equals the value |
| `url_contains` | Check `Page URL:` line in snapshot result |
| `url_equals` | Check `Page URL:` line in snapshot result |
| `count` | Count elements matching the selector pattern in snapshot |

**Selector matching in snapshot:** match by CSS selector (role + text), aria label, or visible text. If multiple elements match, use the first one.

---

## Error recovery patterns

### Element not found
If an element ref cannot be located in snapshot:
- Retry `mcp__playwright__browser_snapshot` once (page may still be loading)
- If still not found after retry → step ERROR: `"Element not found: {selector}"`

### Navigation timeout
If `mcp__playwright__browser_wait_for` times out:
- Step ERROR: `"Timeout waiting for: {selector} ({timeout}ms)"`
- Capture screenshot before recording the error

### Unexpected dialog
If a dialog appears unexpectedly:
- Call `mcp__playwright__browser_handle_dialog(accept=False)` to dismiss
- Continue execution

### Browser close during session
If Playwright tools return errors suggesting the browser is closed:
- Step ERROR: `"Browser session lost"`
- Mark remaining cases in the group as ERROR
- Move to next group (do not attempt to reopen for remaining cases in current group)
