# {PROJECT_NAME} — Test Case Generator Rules

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
| Importance mapping | No |

## Test Case — API

<!-- Uncomment and modify only what differs from defaults: -->

<!-- **testSuiteName Convention** -->
<!-- - testCaseName prefix format: "{Section}_{Description}" -->
<!-- - Example: "Method_Kiểm tra khi nhập sai method" -->

<!-- **Output Format** -->
<!-- - Always include X-Request-ID header in preConditions -->
<!-- - Importance mapping: Critical→High, Major→Medium, Minor→Low -->
<!-- - Response body uses "code"/"message" instead of "errorCode"/"errorDesc" -->

## Test Case — Frontend

<!-- Uncomment and modify only what differs from defaults: -->

<!-- **Section Assignment** -->
<!-- - Buttons go in "Kiểm tra chức năng" (not in validate) -->
<!-- - Error messages go in "Kiểm tra validate" -->

## Quality Rules

<!-- Uncomment and modify if this project has different quality standards -->
<!-- - Language: 100% Vietnamese -->
<!-- - Forbidden phrases: "và/hoặc", "hoặc", "có thể" -->
<!-- - testCaseName max length: 100 chars (default: 80) -->

## Test Account

<!-- Override the default test account used in preConditions: -->
<!-- testAccount: "username/ password" -->
