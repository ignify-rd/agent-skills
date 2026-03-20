# Test Case Generator — Agent Rules

Rules that override default behavior. Loaded automatically by AI agents.

> **Per-project override:** Projects can have their own `AGENTS.md` at the project root. Rules defined there are **merged** with these defaults — only sections explicitly defined in project `AGENTS.md` override the corresponding defaults here. Sections not mentioned fall back to these skill-level defaults.

## Input Priority (PTTK vs RSD)

| Source | Priority | Used for |
|--------|----------|----------|
| **PTTK** | **Highest** for field definitions | Field names, data types, required/optional, maxLength, format constraints, request/response structure |
| **RSD** | **Highest** for business logic | Main flow, error codes, DB mapping, if/else branches |

**When PTTK is available, IGNORE field definitions, request body, and response body in RSD.**
PTTK is typically the larger document — always find the EXACT API/screen by endpoint or name before extracting.

## Extract Rules

### Phase 2 — Request Body (API mode)

Source: PTTK if available, fallback RSD.

1. Find the API endpoint section
2. Extract from source: field names (exact), data types, required/optional, maxLength, format constraints, example values
3. Build body JSON with ALL required fields having concrete values

### Phase 3 — Response Templates

Source: PTTK if available, fallback RSD.

- Extract response SUCCESS (status 200, errorCode "0") and ERROR (validation fail) **once**
- Inject into all BATCH 1, 2, 3

## Batch Strategy

- **BATCH 1**: Pre-validate sections (common, permissions) — testSuiteName = section name
- **BATCH 2**: Validate section — 1 sub-batch PER FIELD (### heading) — testSuiteName = field type + name OR "Kiểm tra validate"
- **BATCH 3**: Post-validate sections (grid, functionality, timeout) — testSuiteName = section name, maxTokens: 65536

Each batch: "Chỉ sinh test cases cho section: {name}. KHÔNG sinh cases cho sections khác."

## Output Rules

- `externalId`, `testSuiteDetails`, `specTitle`, `documentId`, `estimatedDuration`, `note` = always `""`
- `result` = always `"PENDING"`
- `summary` = exactly same as `testCaseName`
- API testCaseName: with prefix `"{Field}_Mô tả"` — Frontend: no prefix, direct from mindmap
- Dedup: track testCaseNames case-insensitive, keep first occurrence

## Quality Rules

- 100% Vietnamese, keep field/button names exactly as in RSD/PTTK
- No placeholders: `{value}`, `[param]`, `<field>` — use concrete sample values
- 1 test = 1 check (atomic), max 80 chars testCaseName
- Forbidden phrases: "và/hoặc", "hoặc", "có thể", "nên", "ví dụ:", "[placeholder]"

## Format Differences

| Aspect | API | Frontend |
|--------|-----|----------|
| preConditions | Endpoint + headers + body JSON | Screen path + login |
| step | API method/params | UI actions (click, nhập, chọn) |
| expectedResult | HTTP status + JSON response | UI state (hiển thị, enable, disable) |
| testCaseName | With prefix | No prefix |
