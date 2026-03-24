# Test Case Generator — Agent Rules

Rules that override default behavior. Loaded automatically by AI agents.

> **Per-project override:** Projects can have their own `AGENTS.md` at the project root. If project `AGENTS.md` defines a rule → use that rule. If not → use the defaults here and in skill references.

## Override Scope

| Category | Project AGENTS.md can override? |
|----------|-------------------------------|
| Chat input / user request | **Always — HIGHEST PRIORITY** |
| testAccount | Yes |
| testSuiteName convention | Yes |
| Writing style (ngắn/dài, cách viết step) | Yes |
| Section assignment (buttons vào section nào) | Yes |
| Output JSON field names | No |
| Batch strategy (BATCH 1/2/3 split) | No |
| Field type dispatch table | No |
| Importance mapping | No |

## ⚠️ How to Apply Project AGENTS.md

**This is CRITICAL — project AGENTS.md must be READ and APPLIED, not just checked for existence.**

1. At the start of generation (Step 0), **READ the entire project AGENTS.md file**
2. Extract ALL sections and rules — especially `## Project-Specific Rules`
3. Store as `projectRules` and apply throughout the entire workflow
4. Any rule in project AGENTS.md that is explicitly defined → apply that rule
5. Sections in project AGENTS.md not present here are **ADDED** (custom rules), not ignored

**Common project-level overrides:**
- Custom section assignment (e.g., "buttons go in function section, not validate")
- Writing style constraints (e.g., "viết ngắn gọn", "tách riêng từng case")
- Image analysis behavior (e.g., "analyze images before reading RSD")
- Custom test account override
- Scope rules (e.g., "only generate for specified sections")

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
- **BATCH 2**: Validate section — 1 sub-batch PER FIELD (### heading) — testSuiteName = theo catalog convention (field sub-suites `"{FieldType}: {FieldName}"` nếu catalog dùng, hoặc `"Kiểm tra validate"` nếu không)
- **BATCH 3**: Post-validate sections (grid, functionality, timeout) — testSuiteName = section name, maxTokens: 65536

Each batch: "Chỉ sinh test cases cho section: {name}. KHÔNG sinh cases cho sections khác."

## Output Rules

- `externalId`, `testSuiteDetails`, `specTitle`, `documentId`, `estimatedDuration`, `note` = always `""`
- `result` = always `"PENDING"`
- `summary` = exactly same as `testCaseName`
- API testCaseName: with prefix `"{Field}_Mô tả"` — Frontend: no prefix, direct from mindmap
- Dedup: track testCaseNames case-insensitive, keep first occurrence

## Test Account

Test account used in preConditions. Resolved by priority:
1. **Project AGENTS.md** — define `testAccount` to override for all test cases
2. **Catalog examples** — if catalog CSV files contain a specific account in preConditions, use that
3. **Default** — `164987/ Test@147258369`

**⚠️ Catalog là nguồn chuẩn cho FORMAT/STYLE — References chỉ là nguồn RULES/LOGIC.**

Phân biệt rõ 2 nguồn:
- **Catalog** quyết định: **VIẾT như thế nào** — format preConditions, steps, expectedResults, testSuiteName convention, testCaseName style, cấu trúc phân nhóm (field sub-suites hay không)
- **References** quyết định: **CHECK cái gì** — loại cases nào cần sinh (maxLength, empty, XSS, emoji...), rules logic, importance mapping

**Khi catalog ≠ references:**
- Catalog dùng field sub-suites `"Textbox: Tên"` → dùng field sub-suites (bỏ qua rule "KHÔNG có field sub-suites" trong refs)
- Catalog viết preConditions 1 dòng → viết 1 dòng (bỏ qua format multi-line trong refs)
- Catalog viết steps/expectedResults khác → follow catalog format
- **References chỉ có ví dụ mẫu = FALLBACK khi catalog rỗng**

Phải load 2-3 catalog examples trước khi generate (xem Step 6a trong SKILL.md) và inject vào mỗi batch prompt

<!-- Projects can override by adding this section in their own AGENTS.md: -->
<!-- testAccount: "your_username/ your_password" -->

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
