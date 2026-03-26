# API Execution Rules

## curl command template

```bash
STATUS=$(curl -s \
  -o /tmp/tc_response.txt \
  -w "%{http_code}" \
  -X {METHOD} \
  "{URL}" \
  {HEADER_FLAGS} \
  {BODY_FLAG} \
  --max-time 30)

BODY=$(cat /tmp/tc_response.txt)
```

Build flags:
- `{HEADER_FLAGS}` — one `-H "Key: Value"` per header entry
- `{BODY_FLAG}` — `-d '{json_string}'` if request body is non-empty; omit if empty

Exit code from `curl` (not STATUS): `0` = success, non-zero = connection/timeout error.

---

## Variable substitution

Before executing, replace `{{varName}}` in URL, headers JSON, and body JSON with captured group variables.

Rules:
- Substitution is case-sensitive.
- If a variable is referenced but not captured → write ERROR: `"Variable {{varName}} not defined in precondition captures"`.
- Substitute in this order: URL first, then headers, then body.

---

## Status validation

```
if actual_status != expected_status:
    result = FAIL
    error = f"Expected {expected_status}, got {actual_status}"
    → skip JSONPath assertions
```

---

## JSONPath assertion evaluation

Parse `Expected Response` column: one assertion per line. Evaluate each in order.

### Supported operators

| Operator | Description | Example |
|---|---|---|
| `EXISTS` | Path exists and is not null | `$.data.id EXISTS` |
| `NOT_EXISTS` | Path does not exist or is null | `$.error NOT_EXISTS` |
| `EQUALS` | Exact equality (string/number/bool) | `$.status EQUALS "ACTIVE"` |
| `CONTAINS` | String contains substring | `$.message CONTAINS "success"` |
| `STARTS_WITH` | String starts with prefix | `$.code STARTS_WITH "ERR_"` |
| `MATCHES` | String matches regex | `$.uuid MATCHES "^[0-9a-f-]{36}$"` |
| `GREATER_THAN` | Numeric comparison | `$.total GREATER_THAN 0` |
| `LESS_THAN` | Numeric comparison | `$.count LESS_THAN 1000` |

### Evaluation rules

1. If response body is empty and assertions are present → ERROR: `"Empty response body"`
2. If response body is not valid JSON and assertions are present → ERROR: `"Response is not JSON"`
3. Evaluate assertions sequentially. On first failure → FAIL, record the failing assertion, stop.
4. If all assertions pass → PASS.

### JSONPath extraction rules

- `$.field` — top-level field
- `$.nested.field` — nested field
- `$.array[0].field` — array index access
- `$.array[*].field` — any array element (EXISTS checks if any element has the field)
- Evaluate using simple path traversal (no filter expressions required)

---

## PASS / FAIL / ERROR determination

| Condition | Result |
|---|---|
| Precondition step failed | ERROR |
| curl non-zero exit | ERROR |
| curl timeout (exit 28) | ERROR (retry once) |
| Status mismatch | FAIL |
| Any JSONPath assertion fails | FAIL |
| Response not JSON (assertions present) | ERROR |
| All checks pass | PASS |

---

## Retry policy

- Retry **once** on these curl errors: exit 6 (DNS), exit 7 (connection refused), exit 28 (timeout)
- Wait 2 seconds before retry
- If retry also fails → ERROR
- Never retry on FAIL (assertion mismatch) — write result immediately

---

## Response body handling

1. Read from `/tmp/tc_response.txt`
2. Strip leading/trailing whitespace
3. Truncate to 500 characters; append `...` if truncated
4. Write to column M

Clean up temp file after each test: `rm -f /tmp/tc_response.txt`
