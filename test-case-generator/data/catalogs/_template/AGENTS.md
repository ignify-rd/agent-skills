# {PROJECT_NAME} — Test Case Generator Rules

Project-specific rules that override the skill-level AGENTS.md.
Only define rules that DIFFER from the defaults. Undefined rules fall back to skill-level.

## Input Priority (PTTK vs RSD)

<!-- Uncomment and modify if this project has different priority rules -->
<!-- | Source | Priority | Used for | -->
<!-- |--------|----------|----------| -->
<!-- | **PTTK** | **Highest** for field definitions | Field names, data types, required/optional, maxLength | -->
<!-- | **RSD** | **Highest** for business logic | Main flow, error codes, DB mapping | -->

## Output Rules

<!-- Uncomment and modify if this project has different output conventions -->
<!-- - `externalId` prefix: "API_" for API, "FE_" for Frontend -->
<!-- - `importance` mapping: Critical→High, Major→Medium, Minor→Low -->
<!-- - `testCaseName` max length: 80 chars -->

## Quality Rules

<!-- Uncomment and modify if this project has different quality standards -->
<!-- - Language: 100% Vietnamese -->
<!-- - Forbidden phrases: "và/hoặc", "hoặc", "có thể" -->

## Project-Specific Rules

<!-- Add any rules unique to this project -->
<!-- Example: -->
<!-- - All API test cases must include X-Request-ID header -->
<!-- - Response body always uses "code" instead of "errorCode" -->
<!-- - Status codes: 0 = success, 1 = error (not errorCode) -->
