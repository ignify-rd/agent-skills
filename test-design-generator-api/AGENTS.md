# Test Design Generator — Agent Rules

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
- Custom field types beyond the 8 default templates
- Scope rules (e.g., "only generate for specified sections")

## Input Priority (PTTK vs RSD)

| Source | Priority | Field definitions / request body | Response body |
|--------|----------|----------------------------------|---------------|
| **PTTK** | **Highest** for field definitions | Field names, data types, required/optional, maxLength, format constraints, request body structure, API endpoints, DB mappings | **PTTK** — response body structure (field names, data types, nesting) |
| **RSD** | **Highest** for business logic | Main flow, error codes, if/else branches, screen flow, permissions | **RSD fallback** — nếu PTTK không có |

> **⚠️ Response body:** Khi PTTK có mô tả response body → dùng PTTK. Khi PTTK không có → dùng RSD. Tuyệt đối không dùng format mặc định cố định.

> **⚠️ Khi có PTTK → REPLACE hoàn toàn. KHÔNG dùng field/request/response từ RSD:**
> - PTTK **REPLACES** toàn bộ field definitions, request body, response body từ RSD
> - Field chỉ có trong RSD (không có trong PTTK) → **bỏ qua**, không dùng
> - Khi upload PTTK → bỏ qua TẤT CẢ field definitions từ RSD, dùng PTTK

## Image Priority (Frontend only)

| Source | Priority |
|--------|----------|
| PTTK | Highest for field definitions |
| RSD | Highest for business logic. IGNORE fields/request/response if PTTK available |
| Images | Supplementary only — placeholder text, icon X, button labels |

Images CANNOT override field names or add features not in RSD. If image shows field not in RSD → note it, do NOT add to test design.

## API Mode — Extract Rules

### Phase 1: RSD → business logic only
Extract: title, endpoint, method, errorCodes, dbMapping (table, conditions, orderBy)

### Phase 2: PTTK → field definitions (if available)
Extract: inputFields (name, type, maxLength, required, validationRules), outputFields
- CHỈ dùng PTTK fields cho validate. RSD chỉ dùng hiểu business logic
- Data types chính xác từ PTTK (Date, Integer, Long, String)

### Fallback: no PTTK → extract everything from RSD

## API Mode — Format Rules

- Common section: `- status: 107` — NEVER use `1\. Check api trả về:` in common
- Validate + Luồng chính: `- 1\. Check api trả về:` / `1\.1. Status:` / `1\.2. Response:`
- ALL validate responses use Status: 200 (errors in body, NOT 400/422/500)
- Output starts with `# {API_NAME}` — NO blockquote, NO `---` horizontal rules
- SQL: concrete values (`WHERE ID = 10001`), UPPERCASE columns, NO placeholders

## Frontend Mode — Field Templates

Dispatch by field.type → template function (from `field-templates.md`):

| Type | Template |
|------|----------|
| textbox/text/input | generateTextboxTests |
| combobox | generateComboboxTests |
| dropdown (values[]) | generateSimpleDropdownTests |
| dropdown (apiEndpoint) | generateSearchableDropdownTests |
| toggle/switch | generateToggleTests |
| checkbox | generateCheckboxTests |
| button | generateButtonTests |
| icon_x/icon_close | generateIconXTests |
| date/datepicker | generateDatePickerTests |
| daterange/date_range | generateDateRangePickerTests |
| textarea/multiline | generateTextareaTests |
| number/number_input | generateNumberInputTests |
| radio/radio_group | generateRadioButtonTests |
| file/file_upload/upload | generateFileUploadTests |
| password/password_input | generatePasswordInputTests |
| tag/tag_input/chip | generateTagInputTests |
| richtext/rich_text_editor | generateRichTextEditorTests |

Templates generate ~80% of test cases (19 field types). LLM supplements business-specific cases.

## Frontend Mode — Screen Type Rules

| Screen Type | Has validate? | Has grid? | Has pagination? | Function section |
|-------------|--------------|-----------|-----------------|------------------|
| LIST | Yes | Yes | Yes | Search per field, combined, clear filter |
| FORM/POPUP | Yes | No | No | Save success/fail, field interactions, cancel |
| DETAIL | No (→ "dữ liệu hiển thị") | No | No | Button visibility by status/permission |

## Quality Rules

- 100% Vietnamese, keep field/button names exactly as in RSD/PTTK
- No placeholders — use concrete sample values
- 1 test = 1 check (atomic)
- Forbidden: "và/hoặc", "hoặc", "có thể", "nên", "ví dụ:", "[placeholder]"
- Response body format comes from PTTK (no fixed format)
