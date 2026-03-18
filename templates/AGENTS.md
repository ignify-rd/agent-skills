# {PROJECT_NAME} — Test Genie Rules

Project-level rules for test-genie AI skills. Edit this file to customize behavior for your project.
Only define rules that DIFFER from the defaults. Undefined rules fall back to skill-level defaults.

## How to Use

| Goal | Say this | Output |
|------|----------|--------|
| Generate test design | "sinh test design", "tạo mindmap", "generate test design" | `.md` mindmap file |
| Generate test cases | "sinh test case", "tạo test case", "generate test case" | Google Sheets URL |

Both skills support **API mode** and **Frontend mode** (auto-detected from input).

## Catalog

Add example files to help AI learn your project's format:

```
catalog/
├── api/           ← API examples (.csv for test cases, .md for test designs)
├── frontend/      ← Frontend examples (.csv or .md)
└── mobile/        ← Mobile examples (.csv or .md)
```

**How to add examples:**
1. Export test cases from Google Sheets as CSV (UTF-8) → place in `catalog/api/` or `catalog/frontend/`
2. Save test design output as `.md` → place in same folders
3. AI auto-indexes new files via the built-in search engine

**Excel template:** Place your spreadsheet template (`.xlsx`) in `excel_template/` for Google Sheets output formatting.

## Input Priority (PTTK vs RSD)

| Source | Priority | Used for |
|--------|----------|----------|
| **PTTK** | **Highest** for field definitions | Field names, data types, required/optional, maxLength, format constraints, request/response structure |
| **RSD** | **Highest** for business logic | Main flow, error codes, DB mapping, if/else branches, permissions |

**When PTTK is available, IGNORE field definitions, request body, and response body in RSD.**
PTTK is typically the larger document — always find the EXACT API/screen by endpoint or name before extracting.

## Output Rules

- `externalId`, `testSuiteDetails`, `specTitle`, `documentId`, `estimatedDuration`, `note` = always `""`
- `result` = always `"PENDING"`
- `summary` = exactly same as `testCaseName`
- API `testCaseName`: with prefix `"{Field}_Mô tả"` — Frontend: no prefix, direct from mindmap
- Dedup: track testCaseNames case-insensitive, keep first occurrence

## Quality Rules

- 100% Vietnamese, keep field/button names exactly as in RSD/PTTK
- No placeholders: `{value}`, `[param]`, `<field>` — use concrete sample values
- 1 test = 1 check (atomic), max 80 chars per test case name
- Forbidden phrases: "và/hoặc", "hoặc", "có thể", "nên", "ví dụ:", "[placeholder]"
- SQL: concrete values (`WHERE ID = 10001`), UPPERCASE column names, NO placeholders
- Response body format comes from PTTK (no fixed format)

## API Mode — Format Rules

- Common section: `- status: 107` (simple) — NEVER use `1\. Check api trả về:` in common
- Validate + Luồng chính: `- 1\. Check api trả về:` / `1\.1. Status:` / `1\.2. Response:`
- ALL validate responses use Status: 200 (errors in body, NOT 400/422/500)
- Output starts with `# {API_NAME}` — NO blockquote header, NO `---` horizontal rules

## Frontend Mode — Screen Type Rules

| Screen Type | Has validate? | Has grid? | Has pagination? | Function section |
|-------------|--------------|-----------|-----------------|------------------|
| LIST | Yes | Yes | Yes | Search per field, combined, clear filter |
| FORM/POPUP | Yes | No | No | Save success/fail, field interactions, cancel |
| DETAIL | No (→ "dữ liệu hiển thị") | No | No | Button visibility by status/permission |

## Batch Strategy (Test Case Generation)

- **BATCH 1**: Pre-validate sections (common, permissions) — testSuiteName = section name
- **BATCH 2**: Validate section — 1 sub-batch PER FIELD (`###` heading) — testSuiteName = field type + name
- **BATCH 3**: Post-validate sections (grid, functionality, timeout) — testSuiteName = section name, maxTokens: 65536

Each batch: "Chỉ sinh test cases cho section: {name}. KHÔNG sinh cases cho sections khác."

## Project-Specific Rules

<!-- Uncomment and customize rules specific to your project -->
<!-- - Response body uses "code"/"message" instead of "errorCode"/"errorDesc" -->
<!-- - All API test cases must include X-Request-ID header -->
<!-- - Custom template type: API_TEST / HOME / FEE_ENGINE / LENDING -->
<!-- - Error status code mapping: 0 = success, other = error -->
