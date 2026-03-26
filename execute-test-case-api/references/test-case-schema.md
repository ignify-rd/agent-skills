# API Test Case — Spreadsheet Schema

## Tab name
Default: `API Tests`
Override in project AGENTS.md: `sheet_name: "My Tests"`

---

## Column layout

| Col | Field | Type | Written by | Required |
|-----|-------|------|------------|---------|
| A | Test ID | Text | User | Yes |
| B | Title | Text | User | Yes |
| C | Precondition Group | Text | User | No |
| D | Precondition Steps | JSON array | User | No |
| E | HTTP Method | Text | User | Yes |
| F | URL | Text | User | Yes |
| G | Headers | JSON object | User | No |
| H | Request Body | JSON / text | User | No |
| I | Expected Status | Number | User | Yes |
| J | Expected Response | Assertions | User | No |
| K | Result | PASS/FAIL/ERROR | **Agent** | — |
| L | Error Message | Text | **Agent** | — |
| M | Response Body | Text | **Agent** | — |
| N | Executed At | ISO 8601 | **Agent** | — |

---

## Column details

### C — Precondition Group
Optional identifier. Consecutive rows with the same value share an auth state — precondition steps execute only once for the group.

- Leave empty if no shared auth is needed.
- Use descriptive names: `login-admin`, `login-guest`, `api-key-service`.

### D — Precondition Steps
JSON array of setup actions to run once before the group's first test case.

**Supported actions:**

#### `http` — Call an API and capture variables
```json
[
  {
    "action": "http",
    "method": "POST",
    "url": "https://api.example.com/auth/login",
    "headers": {"Content-Type": "application/json"},
    "body": {"username": "admin", "password": "secret"},
    "capture": {
      "token": "$.data.accessToken",
      "userId": "$.data.userId"
    }
  }
]
```

- `capture`: map of `variableName → JSONPath` — extracts values from the response body
- Captured variables are referenced in subsequent columns as `{{variableName}}`

#### `set` — Define a static variable
```json
[
  {"action": "set", "variable": "baseUrl", "value": "https://api.staging.example.com"}
]
```

### E — HTTP Method
One of: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`

### F — URL
Full URL. May use `{{variables}}` from precondition captures.

Example: `https://api.example.com/users/{{userId}}`

### G — Headers
JSON object. May use `{{variables}}`.

```json
{"Authorization": "Bearer {{token}}", "Content-Type": "application/json"}
```

### H — Request Body
JSON payload or plain text. May use `{{variables}}`. Leave empty for GET requests.

### I — Expected Status
Integer HTTP status code: `200`, `201`, `400`, `401`, `403`, `404`, `500`, etc.

### J — Expected Response
One assertion per line. Supported formats:

```
$.field EXISTS
$.field NOT_EXISTS
$.field EQUALS "value"
$.field EQUALS 42
$.field EQUALS true
$.field CONTAINS "substring"
$.field STARTS_WITH "prefix"
$.field MATCHES "regex_pattern"
$.array[0].id EXISTS
$.meta.total GREATER_THAN 0
$.meta.total LESS_THAN 100
```

Leave empty to skip response body validation (only status is checked).

---

## Example rows

### Row 2 — Login (precondition group setup)
| Col | Value |
|-----|-------|
| A | API-001 |
| B | Login thành công với admin |
| C | login-admin |
| D | `[{"action":"http","method":"POST","url":"https://api.example.com/auth/login","headers":{"Content-Type":"application/json"},"body":{"username":"admin","password":"Admin@123"},"capture":{"token":"$.data.accessToken"}}]` |
| E | POST |
| F | `https://api.example.com/auth/login` |
| G | `{"Content-Type": "application/json"}` |
| H | `{"username": "admin", "password": "Admin@123"}` |
| I | 200 |
| J | `$.data.accessToken EXISTS` |

### Row 3 — Uses auth from group (no precondition re-execution)
| Col | Value |
|-----|-------|
| A | API-002 |
| B | Lấy danh sách users |
| C | login-admin |
| D | *(empty — reuses group's auth)* |
| E | GET |
| F | `https://api.example.com/users` |
| G | `{"Authorization": "Bearer {{token}}"}` |
| H | *(empty)* |
| I | 200 |
| J | `$.data EXISTS`<br>`$.meta.total GREATER_THAN 0` |

### Row 4 — Different group (new auth)
| Col | Value |
|-----|-------|
| A | API-003 |
| B | Truy cập với guest bị từ chối |
| C | login-guest |
| D | `[{"action":"http","method":"POST","url":"https://api.example.com/auth/login","headers":{"Content-Type":"application/json"},"body":{"username":"guest","password":"Guest@123"},"capture":{"token":"$.data.accessToken"}}]` |
| E | GET |
| F | `https://api.example.com/admin/users` |
| G | `{"Authorization": "Bearer {{token}}"}` |
| H | *(empty)* |
| I | 403 |
| J | *(empty)* |
