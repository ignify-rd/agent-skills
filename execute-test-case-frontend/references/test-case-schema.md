# Frontend Test Case — Spreadsheet Schema

## Tab name
Default: `Frontend Tests`
Override in project AGENTS.md: `sheet_name: "My Tests"`

---

## Column layout

| Col | Field | Type | Written by | Required |
|-----|-------|------|------------|---------|
| A | Test ID | Text | User | Yes |
| B | Title | Text | User | Yes |
| C | Precondition Group | Text | User | No |
| D | Precondition Steps | JSON array | User | No |
| E | Steps | JSON array | User | Yes |
| F | Assertions | JSON array | User | Yes |
| G | Result | PASS/FAIL/ERROR | **Agent** | — |
| H | Error Message | Text | **Agent** | — |
| I | Screenshot URL | Text | **Agent** | — |
| J | Executed At | ISO 8601 | **Agent** | — |

---

## Column details

### C — Precondition Group
Optional identifier. Consecutive rows with the same value share a browser session — precondition steps execute only once for the group.

- Leave empty to reset browser before this case.
- Use descriptive names: `login-admin`, `login-guest`, `navigate-to-form`.

### D — Precondition Steps
JSON array of browser actions to run once before the group's first test case (login, navigate to page, etc.).

**Supported actions:**

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

### E — Steps
JSON array of browser actions for this specific test case. Execute after resetting to entry state.

```json
[
  {"action": "click", "selector": "#btn-create"},
  {"action": "fill", "selector": "#form-name", "value": "Test Item"},
  {"action": "click", "selector": "#btn-submit"},
  {"action": "wait_for", "selector": ".success-toast", "timeout": 3000}
]
```

### F — Assertions
JSON array of conditions to verify after steps execute.

```json
[
  {"type": "visible", "selector": ".success-toast"},
  {"type": "text_equals", "selector": "h1", "value": "Tạo mới thành công"},
  {"type": "not_visible", "selector": ".error-message"},
  {"type": "url_contains", "value": "/dashboard"}
]
```

**Supported assertion types:**

| Type | Checks | Required fields |
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

---

## Grouping logic

- Empty `Precondition Group` → solo case (reset browser before running)
- Same non-empty value in consecutive rows → share browser session within that run
- Non-consecutive appearances of the same group name → separate groups (each re-executes preconditions)

---

## Example rows

### Row 2 — First case in group (login + navigate)
| Col | Value |
|-----|-------|
| A | FE-001 |
| B | Tạo item mới thành công |
| C | login-admin |
| D | `[{"action":"goto","url":"https://app.example.com/login"},{"action":"fill","selector":"#email","value":"admin@test.com"},{"action":"fill","selector":"#password","value":"Admin@123"},{"action":"click","selector":"button[type=submit]"},{"action":"wait_for","selector":".dashboard","timeout":5000}]` |
| E | `[{"action":"click","selector":"#btn-create"},{"action":"fill","selector":"#form-name","value":"Test Item"},{"action":"click","selector":"#btn-submit"}]` |
| F | `[{"type":"visible","selector":".success-toast"},{"type":"not_visible","selector":".error-message"}]` |

### Row 3 — Same group (reuse browser session)
| Col | Value |
|-----|-------|
| A | FE-002 |
| B | Tạo item thất bại khi bỏ trống tên |
| C | login-admin |
| D | *(empty — reuses group's login)* |
| E | `[{"action":"click","selector":"#btn-create"},{"action":"click","selector":"#btn-submit"}]` |
| F | `[{"type":"visible","selector":".error-message"},{"type":"text_contains","selector":".error-message","value":"Tên không được để trống"}]` |

### Row 4 — Solo case (reset browser)
| Col | Value |
|-----|-------|
| A | FE-003 |
| B | Không thể truy cập khi chưa login |
| C | *(empty)* |
| D | *(empty — no shared preconditions)* |
| E | `[{"action":"goto","url":"https://app.example.com/admin"}]` |
| F | `[{"type":"url_contains","value":"/login"}]` |
