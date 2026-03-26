# {PROJECT_NAME} — Test Design Generator Rules

Project-specific rules that override the skill-level AGENTS.md.
Only define rules that DIFFER from the defaults. Undefined rules fall back to skill-level.

## Override Scope

| Category | Can override? |
|----------|--------------|
| Chat input / user request | **Always — HIGHEST PRIORITY** |
| `testAccount` | Yes |
| testSuiteName convention | Yes |
| Writing style (ngắn/dài, cách viết step) | Yes |
| Section assignment (buttons vào section nào) | Yes |
| Output JSON field names | No |
| Batch strategy (BATCH 1/2/3 split) | No |
| Field type dispatch table | No |

## Test Design — API Only

<!-- Uncomment and modify only what differs from defaults: -->

<!-- **Response Format** -->
<!-- - Common section format: `- status: 107` -->
<!-- - Validate response status: always 200 -->
<!-- - Response body uses "code"/"message" instead of "errorCode"/"errorDesc" -->

<!-- **SQL Conventions** -->
<!-- - All SQL queries must include schema prefix: SCHEMA_NAME.TABLE_NAME -->
<!-- - Column naming: UPPERCASE -->

<!-- **Section Structure** -->
<!-- - Base URL: {{BASE_URL}} = https://api.example.com -->
<!-- - Error status code: 500 for server errors (not 200) -->

## Quality Rules

<!-- Uncomment and modify if this project has different quality standards -->
<!-- - Language: 100% Vietnamese -->
<!-- - Forbidden phrases: "và/hoặc", "hoặc", "có thể" -->
<!-- - testCaseName max length: 100 chars (default: 80) -->

## Test Account

<!-- Override the default test account used in preConditions: -->
<!-- testAccount: "username/ password" -->
