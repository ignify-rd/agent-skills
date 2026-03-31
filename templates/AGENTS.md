# {PROJECT_NAME} — Project Rules

Project-level overrides for test-genie skills.
**Only define rules that DIFFER from the defaults.** Sections not listed here fall back to skill defaults automatically.

## Authority & Priority

**Priority — highest first:**

| Authority | Scope |
|----------|-------|
| **User chat input** | Always — **HIGHEST PRIORITY**. Whatever the user says in their request overrides any rule below. |
| Project `AGENTS.md` | Project-specific overrides — only applies when a rule is explicitly defined here |
| Skill defaults | `generate-*/AGENTS.md` + references — used when neither of the above provides a rule |

**How it works:** If the user says "viết ngắn gọn" or "chỉ generate 10 cases" → do exactly that, even if it contradicts everything below. If the user is silent on a topic → fall back to project AGENTS.md if defined → else skill defaults.

## Quick Start

| Goal | Command |
|------|---------|
| Generate test design (API) | `/generate-test-design-api` or say "sinh test design api" |
| Generate test design (Frontend) | `/generate-test-design-frontend` or say "sinh test design giao diện" |
| Generate test cases (API) | `/generate-test-case-api` or say "sinh test case api" |
| Generate test cases (Frontend) | `/generate-test-case-frontend` or say "sinh test case giao diện" |

---

# Test Design Rules

Override the `generate-test-design-*` skills. These rules only affect mindmap output.

## Test Design — API

<!-- Uncomment and edit only what differs from defaults: -->

<!-- **Response Format** -->
<!-- - Response body uses "code"/"message" instead of "errorCode"/"errorDesc" -->
<!-- - Error status code: 0 = success, non-zero = error -->

<!-- **SQL Conventions** -->
<!-- - All SQL queries must include schema prefix: SCHEMA_NAME.TABLE_NAME -->
<!-- - Column naming: UPPERCASE (default) -->

<!-- **API Section Structure** -->
<!-- - Base URL: {{BASE_URL}} = https://api.example.com -->
<!-- - Add custom section: "Kiểm tra bảo mật" -->

## Test Design — Frontend

<!-- Uncomment and edit only what differs from defaults: -->

<!-- **Screen Type Convention** -->
<!-- - Override default screenType dispatch: ... -->

<!-- **Section Assignment** -->
<!-- - Buttons go in ## Kiểm tra chức năng (not in validate) -->
<!-- - Error messages go in ## Kiểm tra validate -->

<!-- **Image Analysis** -->
<!-- - Always analyze images before reading RSD text -->
<!-- - Ignore fields visible only in images (not in RSD) -->

---

# Test Case Rules

Override the `generate-test-case-*` skills. These rules only affect JSON output.

## Test Case — API

<!-- Uncomment and edit only what differs from defaults: -->

<!-- **testSuiteName Convention** -->
<!-- - testCaseName prefix format: "{Section}_{Description}" -->
<!-- - Example: "Method_Kiểm tra khi nhập sai method" -->

<!-- **Output Format** -->
<!-- - Always include X-Request-ID header in preConditions -->
<!-- - Importance mapping: Critical→High, Major→Medium, Minor→Low -->

## Test Case — Frontend

<!-- Uncomment and edit only what differs from defaults: -->

<!-- **Section Assignment** -->
<!-- - Buttons go in "Kiểm tra chức năng" (not in validate) -->
<!-- - Error messages go in "Kiểm tra validate" -->

---

# Shared Rules

These rules apply to both test design and test case generation.

## Test Account

<!-- Override the default test account used in preConditions: -->
<!-- testAccount: "username/ password" -->

## Catalog

Add example files so AI learns your project's format:

```
catalog/
├── api/           ← Export API test cases from Google Sheets as CSV (UTF-8)
├── frontend/      ← Frontend test cases (.csv or .md)
└── mobile/        ← Mobile examples
```

**Catalog is the source of truth for:**
- Writing style (wording, tone, verbosity)
- preConditions format
- testSuiteName convention (field sub-suites or flat?)
- Section grouping

## Temp File Rules

<!-- Non-overridable — applies to all skills: -->
<!-- NEVER write temp/helper scripts to disk (_*.py, _*.ps1, _check_*.py, etc.) -->
<!-- Use python3 -X utf8 -c "..." inline in Bash, or Read/Edit/Write tools directly. -->

## Quality Rules

<!-- Uncomment and edit only what differs from defaults: -->

<!-- **Language** -->
<!-- - 100% Vietnamese (default) -->
<!-- - English field names are acceptable when quoting from RSD -->

<!-- **Naming Constraints** -->
<!-- - testCaseName max length: 100 chars (default: 80) -->

<!-- **Forbidden Phrases** -->
<!-- - Default: "và/hoặc", "hoặc", "có thể", "nên", "ví dụ:", "[placeholder]" -->
<!-- - Custom: ... -->

<!-- **testCaseName Convention** -->
<!-- - API: prefix with field name, e.g. "FieldName_Mô tả" (default) -->
<!-- - Frontend: no prefix, direct from mindmap (default) -->
