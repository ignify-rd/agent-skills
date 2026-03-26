# Frontend Test Case — Spreadsheet Schema

## Tab name
Default: `Frontend Tests`
Override in project AGENTS.md: `sheet_name: "UI Tests"`

---

## Column layout

| Col | Field | Type | Written by | Required |
|-----|-------|------|------------|---------|
| A | Test ID | Text | User | Yes |
| B | Title | Text | User | Yes |
| C | Precondition Group | Text | User | No |
| D | Precondition Steps | JSON array | User | No |
| E | Steps | JSON array | User | Yes |
| F | Assertions | JSON array | User | No |
| G | Result | PASS/FAIL/ERROR | **Agent** | — |
| H | Error Message | Text | **Agent** | — |
| I | Screenshot URL | Text | **Agent** | — |
| J | Executed At | ISO 8601 | **Agent** | — |

---

## Column C — Precondition Group

An optional label that identifies which test cases share the same browser session (login state + navigation).

- Consecutive rows with the **same non-empty value** share one browser session.
- The first case in a group executes `Precondition Steps`; subsequent cases skip preconditions and reset to the entry URL.
- Empty value → solo execution (browser resets before this case).

**Naming convention:** `{role}-{context}` — e.g., `admin-user-management`, `guest-homepage`, `staff-order-list`

---

## Column D — Precondition Steps

JSON array of browser steps to run **once** before the group's first test case. Typically: login, navigate to the feature under test.

Only the first row of a group needs to populate this column. Subsequent rows' column D is **ignored**.

### Step format

Each step is a JSON object with `"action"` and action-specific fields:

#### `goto` — Navigate to URL
```json
{"action": "goto", "url": "https://app.example.com/login"}
```

#### `fill` — Type text into an input
```json
{"action": "fill", "selector": "#email", "value": "admin@test.com"}
```
`selector` is a CSS selector used to find the element in the accessibility snapshot.

#### `click` — Click an element
```json
{"action": "click", "selector": "button[type=submit]"}
```

#### `wait_for` — Wait for element to appear
```json
{"action": "wait_for", "selector": ".dashboard-header", "timeout": 5000}
```
The last `wait_for` step's selector becomes the **entry selector** used to reset state between test cases.

#### `select` — Choose a dropdown option
```json
{"action": "select", "selector": "#status-filter", "value": "ACTIVE"}
```

#### `press_key` — Press a keyboard key
```json
{"action": "press_key", "key": "Enter"}
```

#### `hover` — Hover over an element
```json
{"action": "hover", "selector": ".menu-item"}
```

---

## Column E — Steps

JSON array of test-specific browser steps. Same format as Precondition Steps.

These steps execute **after** the entry state is established. They represent the actual test scenario.

---

## Column F — Assertions

JSON array of conditions to verify after Steps complete.

### Assertion types

#### `visible` — Element is present and visible
```json
{"type": "visible", "selector": ".success-toast"}
```

#### `not_visible` — Element is absent or hidden
```json
{"type": "not_visible", "selector": ".error-banner"}
```

#### `text_contains` — Element text includes a substring
```json
{"type": "text_contains", "selector": "h1", "value": "Danh sách người dùng"}
```

#### `text_equals` — Element text exactly matches
```json
{"type": "text_equals", "selector": ".total-count", "value": "10"}
```

#### `url_contains` — Current URL includes a substring
```json
{"type": "url_contains", "value": "/users"}
```

#### `url_equals` — Current URL exactly matches
```json
{"type": "url_equals", "value": "https://app.example.com/users"}
```

#### `count` — Number of matching elements equals expected
```json
{"type": "count", "selector": ".table-row", "value": 5}
```

---

## Full example

### Sheet setup (3 cases, grouped by login)

**Row 2 — FE-001** (first in group — includes preconditions)
| Col | Value |
|-----|-------|
| A | FE-001 |
| B | Hiển thị danh sách user |
| C | admin-user-list |
| D | `[{"action":"goto","url":"https://app.example.com/login"},{"action":"fill","selector":"#email","value":"admin@test.com"},{"action":"fill","selector":"#password","value":"Admin@123"},{"action":"click","selector":"button[type=submit]"},{"action":"wait_for","selector":".dashboard","timeout":5000},{"action":"goto","url":"https://app.example.com/users"},{"action":"wait_for","selector":".user-table","timeout":3000}]` |
| E | `[{"action":"wait_for","selector":".user-table","timeout":2000}]` |
| F | `[{"type":"visible","selector":".user-table"},{"type":"count","selector":".user-table tr","value":10}]` |

**Row 3 — FE-002** (same group — reuses session, navigates back to user list)
| Col | Value |
|-----|-------|
| A | FE-002 |
| B | Tìm kiếm user theo tên |
| C | admin-user-list |
| D | *(empty — reuses group session)* |
| E | `[{"action":"fill","selector":"#search-input","value":"Nguyen"},{"action":"click","selector":"#btn-search"},{"action":"wait_for","selector":".search-results","timeout":3000}]` |
| F | `[{"type":"visible","selector":".search-results"},{"type":"text_contains","selector":".result-count","value":"Nguyen"}]` |

**Row 4 — FE-003** (same group — reuses session)
| Col | Value |
|-----|-------|
| A | FE-003 |
| B | Lọc user theo trạng thái ACTIVE |
| C | admin-user-list |
| D | *(empty)* |
| E | `[{"action":"select","selector":"#status-filter","value":"ACTIVE"},{"action":"click","selector":"#btn-apply-filter"},{"action":"wait_for","selector":".filtered-results","timeout":3000}]` |
| F | `[{"type":"visible","selector":".filtered-results"},{"type":"not_visible","selector":".empty-state"}]` |

**Row 5 — FE-004** (different group — new login as guest)
| Col | Value |
|-----|-------|
| A | FE-004 |
| B | Guest không thấy menu admin |
| C | guest-home |
| D | `[{"action":"goto","url":"https://app.example.com/login"},{"action":"fill","selector":"#email","value":"guest@test.com"},{"action":"fill","selector":"#password","value":"Guest@123"},{"action":"click","selector":"button[type=submit]"},{"action":"wait_for","selector":".home-content","timeout":5000}]` |
| E | `[{"action":"wait_for","selector":".home-content","timeout":2000}]` |
| F | `[{"type":"not_visible","selector":".admin-menu"},{"type":"visible","selector":".home-content"}]` |
