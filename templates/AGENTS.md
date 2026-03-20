# {PROJECT_NAME} — Project Rules

Project-level overrides for test-genie skills.
**Only define rules that DIFFER from the defaults.** Sections not listed here fall back to skill defaults automatically.

## Quick Start

| Goal | Command |
|------|---------|
| Generate test design | `/generate-test-design` or say "sinh test design" |
| Generate test cases | `/generate-test-case` or say "sinh test case" |

## Project Type

<!-- Uncomment one: -->
<!-- project_type: API_TEST -->
<!-- project_type: HOME -->
<!-- project_type: FEE_ENGINE -->
<!-- project_type: LENDING -->

## Catalog

Add example files so AI learns your project's format:

```
catalog/
├── api/           ← Export test cases from Google Sheets as CSV (UTF-8)
├── frontend/      ← Frontend examples (.csv or .md)
└── mobile/        ← Mobile examples
```

## Project-Specific Overrides

<!-- Uncomment and edit only what differs from defaults: -->

<!-- ### Response Format
- Response body uses "code"/"message" instead of "errorCode"/"errorDesc"
- Error status code: 0 = success, non-zero = error -->

<!-- ### API Rules
- All API test cases must include X-Request-ID header
- Base URL: {{BASE_URL}} = https://api.example.com -->

<!-- ### Output Rules
- testCaseName prefix format: "{Section}_{Description}" -->

<!-- ### Quality Rules
- Max test case name length: 100 chars (override default 80) -->
