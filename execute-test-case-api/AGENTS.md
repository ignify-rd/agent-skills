# execute-test-case-api — Agent Rules

These rules apply when the `execute-test-case-api` skill is active. A project-level `AGENTS.md` may override the values in the **Override scope** table below, but may not override the guardrails section.

---

## Override scope

| Setting | Default | Project can override? |
|---|---|---|
| Sheet tab name | `API Tests` | Yes — specify in project AGENTS.md |
| Request timeout | 30 seconds | Yes |
| Retry count | 1 | Yes (max 3) |
| Retry delay | 2 seconds | Yes |
| Response truncation length | 500 characters | Yes |
| Result column start | Column K | No |
| Skip already-executed rows | true | Yes — set to false to force re-run |

---

## Auth / Precondition reuse

- Execute `Precondition Steps` **once per consecutive group** (same `Precondition Group` value).
- Store captured variables in a group-scoped map. Discard when the group ends.
- If the same group name appears non-consecutively (rows interleaved with other groups), treat each occurrence as a **separate group instance** — re-execute preconditions.
- Never cache auth tokens across separate skill invocations.

## HTTP execution

- **Test cases**: executed via Postman web browser (Playwright). One browser session per skill invocation; one request tab reused across all cases.
- **Precondition steps** (auth/login): executed via `curl` to reliably capture variables (token, etc.). Curl is not used for actual test cases.
- Curl timeout: `--max-time 30` (default). For HTTPS self-signed certs: `-k` only if `allow_insecure: true` in project AGENTS.md.
- Postman request timeout: 15000ms (default). Override via `postman_timeout` in project AGENTS.md.

## Response validation

- HTTP status check is always performed first. Mismatch → FAIL immediately (skip JSONPath checks).
- JSONPath assertions are evaluated in order. First failure stops evaluation — record the failing assertion in the error message.
- Empty `Expected Response` column → skip JSONPath assertions, only check status.
- If response body is not valid JSON and JSONPath assertions are present → ERROR with message `"Response is not JSON"`.

## Evidence sheet

- Tab name: `"Evidence"` (non-configurable — shared between API and Frontend test runs in the same spreadsheet).
- Create on first run if not present; write header row `Test ID | Screenshot`.
- Append one row per executed test case regardless of PASS/FAIL/ERROR.
- Column B contains the local screenshot file path (relative to working directory).
- Never overwrite existing Evidence rows — always append to the next empty row.

## Result writing

- Write results **row by row** immediately after each test execution — do not accumulate and batch.
- Use `mcp__gsheets__update_cells` for single-row writes.
- Timestamp format: `YYYY-MM-DDTHH:mm:ssZ` (ISO 8601 UTC).
- Response body in column M: strip leading/trailing whitespace, truncate at configured limit, append `...` if truncated.

## Error classification

| Condition | Result | Error Message format |
|---|---|---|
| Precondition step failed | ERROR | `Precondition failed: {http_status} {response_snippet}` |
| curl timeout / connection error | ERROR | `Request failed: {curl_error}` |
| HTTP status mismatch | FAIL | `Expected {expected}, got {actual}` |
| JSONPath assertion failed | FAIL | `Assertion failed: {jsonpath} — expected {expected}, got {actual}` |
| Response not JSON (assertions present) | ERROR | `Response is not JSON` |
| All assertions passed | PASS | (empty) |

## Guardrails (non-overridable)

- NEVER modify columns A through J.
- NEVER skip writing a result row, even on ERROR.
- NEVER re-execute a row with a non-empty Result (column K) unless explicitly instructed.
- NEVER store credentials or auth tokens to disk or sheet columns.
- NEVER print auth tokens or passwords in the execution summary.
