# {PROJECT_NAME} — Test Design Generator Rules

Project-specific rules that override the skill-level AGENTS.md.
Only define rules that DIFFER from the defaults. Undefined rules fall back to skill-level.

## Input Priority (PTTK vs RSD)

<!-- Uncomment and modify if this project has different priority rules -->
<!-- | Source | Priority | Used for | -->
<!-- |--------|----------|----------| -->
<!-- | **PTTK** | **Highest** for field definitions | Field names, data types, required/optional, maxLength | -->
<!-- | **RSD** | **Highest** for business logic | Main flow, error codes, DB mapping | -->

## API Mode — Format Rules

<!-- Uncomment and modify if this project has different format conventions -->
<!-- - Common section format: `- status: 107` -->
<!-- - Validate response status: always 200 -->
<!-- - SQL column naming: UPPERCASE -->

## Frontend Mode — Screen Type Rules

<!-- Uncomment and modify if this project has different screen type conventions -->
<!-- | Screen Type | Has validate? | Has grid? | Has pagination? | -->
<!-- |-------------|--------------|-----------|------------------| -->
<!-- | LIST | Yes | Yes | Yes | -->
<!-- | FORM/POPUP | Yes | No | No | -->
<!-- | DETAIL | No | No | No | -->

## Quality Rules

<!-- Uncomment and modify if this project has different quality standards -->
<!-- - Language: 100% Vietnamese -->
<!-- - Forbidden phrases: "và/hoặc", "hoặc", "có thể" -->

## Project-Specific Rules

<!-- Add any rules unique to this project -->
<!-- Example: -->
<!-- - Response body uses "code"/"message" instead of "errorCode"/"errorDesc" -->
<!-- - All SQL queries must include schema prefix: SCHEMA_NAME.TABLE_NAME -->
<!-- - Error status code 500 is used for server errors (not 200) -->
