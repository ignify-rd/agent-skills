---
name: generate-test-design
description: Generate test design documents (mindmap .md) from RSD/PTTK. Searches catalog of real examples by keyword to find matching reference. Use when user says "generate test design", "generate mindmap", "sinh test design", "tao mindmap", "tạo test design", "tạo mindmap", or provides RSD/PTTK documents for mindmap generation.
---

# Test Design Generator

Generate comprehensive test design documents (.md) from RSD and optional PTTK. Uses a searchable catalog of real test design examples to ensure output matches the correct format per project.

> **Scope**: This skill covers **test design** (mindmap output) for two pages:
> - `src/pages/rsd-to-mindmap.vue` — API test design
> - `src/pages/rsd-to-mindmap-frontend.vue` — Frontend test design (with optional image analysis)
>
> It does **NOT** cover test case generation (JSON/Excel output) — that is handled by `api-test-generation.vue` and `fe-test-generation.vue`.

## When to Apply

- User provides RSD/PTTK and asks to generate test design or mindmap
- User says "sinh test design", "tạo test design", "tạo mindmap", "tao mindmap"
- User uploads .docx/.pdf/.txt/.md files for test design / mindmap generation
- Called internally by `test-case-generator` skill when user provides only RSD+PTTK without a mindmap

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## Rule Override Hierarchy

Rules are resolved in this order (highest priority first):

1. **Project `AGENTS.md`** — `AGENTS.md` at project root (user-managed, project-specific overrides)
2. **Skill-level `AGENTS.md`** — `test-design-generator/AGENTS.md` (default rules)
3. **Skill references** — `references/*.md` (detailed rules, managed by dev team)
4. **This SKILL.md** — workflow instructions (lowest priority, never overridden)

**How overrides work:** Rules in project `AGENTS.md` are merged with skill defaults — only the sections/rules explicitly defined in project `AGENTS.md` override the corresponding defaults. Sections not mentioned fall back to skill-level `AGENTS.md`.

## Workflow

### Step 0: Validate Project Setup

Before starting generation, check that the project structure exists:

1. **Check catalog** — look for `catalog/` directory at project root (contains `api/`, `frontend/`, `mobile/`)
2. **Check AGENTS.md** — look for `AGENTS.md` at project root (project-level rules)

**If catalog directory does not exist:**
- Ask user: "Chưa có thư mục `catalog/`. Bạn đã chạy `test-genie init` chưa?"
- If not → guide user to run `test-genie init` to set up project structure

**If AGENTS.md does not exist at project root:**
- Use skill-level `AGENTS.md` (default rules)
- Inform user: "Project chưa có AGENTS.md. Đang dùng rules mặc định."

**If catalog exists but has no examples (empty api/ and frontend/):**
- Warn user: "Catalog chưa có examples. Output có thể không chính xác format. Bạn có muốn thêm examples trước không?"
- Proceed with skill references as fallback

### Step 1: Determine Mode

| Input | Mode | Output |
|-------|------|--------|
| RSD describes an API endpoint | API | Markdown test design for API |
| RSD describes a UI screen | Frontend | Markdown test design for Frontend |

### Step 2: Load Rules & References

**Always load priority rules first**, then load generation rules and search for examples:

Use the installed skill path for your assistant:
- Claude: find with `find ~/.claude -name "search.py" -path "*/test-design-generator/*" 2>/dev/null | head -1`
- Cursor: find with `find ~/.cursor -name "search.py" -path "*/test-design-generator/*" 2>/dev/null | head -1`

**Shortcut** — resolve script path automatically:
```bash
SKILL_SCRIPTS=$(node -e "const p=require('child_process').execSync('npm root -g',{encoding:'utf8'}).trim(); console.log(p+'/test-genie/test-design-generator/scripts')" 2>/dev/null \
  || find ~/.claude ~/.cursor -name "search.py" -path "*/test-design-generator/*" 2>/dev/null | head -1 | xargs dirname)
echo $SKILL_SCRIPTS
```

**IMPORTANT:** Always run search.py from the **project root** directory (where `catalog/` and `AGENTS.md` are located).

```bash
# Load priority rules (MUST load first)
python <skills-root>/test-design-generator/scripts/search.py --ref priority-rules

# Load generation rules
python <skills-root>/test-design-generator/scripts/search.py --ref api-test-design       # API mode
python <skills-root>/test-design-generator/scripts/search.py --ref frontend-test-design   # Frontend mode
python <skills-root>/test-design-generator/scripts/search.py --ref field-templates         # Frontend field templates
python <skills-root>/test-design-generator/scripts/search.py --ref quality-rules

# List all available references
python <skills-root>/test-design-generator/scripts/search.py --list-refs

# Search API examples by keyword (searches catalog/api/ in project root)
python <skills-root>/test-design-generator/scripts/search.py "search list api" --domain api

# Search Frontend examples (searches catalog/frontend/ in project root)
python <skills-root>/test-design-generator/scripts/search.py "danh sach list screen" --domain frontend

# Search format rules (skill-bundled, not in project catalog)
python <skills-root>/test-design-generator/scripts/search.py "common section status" --domain rules

# List all available examples
python <skills-root>/test-design-generator/scripts/search.py --list

# Read full content of top match
python <skills-root>/test-design-generator/scripts/search.py "export excel" --domain api --full
```

### Step 3: Read the Top-Matching Example

After search returns results, **read the full example file** to understand the exact format:

```bash
# search.py returns the full_path — use view_file on it
```

### Step 4: Extract Data from RSD & PTTK

Priority rules: see `AGENTS.md` or `--ref priority-rules`. When PTTK is available, IGNORE field definitions, request body, and response body in RSD.

#### API Mode — Extraction

**Phase 1: RSD → business logic only (always from RSD)**
1. Find the exact API section in RSD by endpoint or name
2. Extract: title, endpoint, method, errorCodes (description → status code mapping), dbMapping (table, conditions, orderBy)
3. Extract: if/else branches, mode variations (create/update/delete), status transitions

**Phase 2: PTTK → field definitions (if available)**
1. Find the EXACT API by endpoint in PTTK (PTTK is usually a large document with many APIs)
2. Extract inputFields: name, type (Date/Integer/Long/String — exact from PTTK), maxLength, required (Y/N), nullBehavior, validationRules (allowedSpecialChars, allowSpaces, allowAccents)
3. Extract outputFields: name, type, nesting structure
4. Extract response body structure (field names, data types, nesting) — this defines the response format for ALL test cases
5. **If no PTTK** → fallback: extract field definitions AND business logic from RSD

#### Frontend Mode — Extraction

**Phase 1: Analyze images (if provided)**
1. For each image: extract screenType, buttons, inputFields (label, type, placeholder, location), gridColumns, hasPagination
2. Consolidate all image analyses into one structure
3. Merge with RSD: images only supplement (placeholder text, hasIconX, button labels) — images CANNOT override field names from RSD/PTTK

**Phase 2: RSD → screen structure (always from RSD)**
1. Extract: screenName, screenType (LIST/FORM/POPUP/DETAIL), breadcrumb, permissions, UI elements
2. Extract: fields with types (textbox/combobox/dropdown/toggle/checkbox/button/icon_x)
3. Extract: grid columns (name, dbColumn, dbTable, format), pagination values, sort order
4. Extract: button visibility rules by status/permission, additional features

**Phase 3: PTTK → field definitions (if available)**
1. Find the exact screen/API in PTTK by name or endpoint
2. Extract: field names, types, API endpoints, DB mappings, enum values, maxLength, format constraints
3. **REPLACE** all field definitions from RSD with PTTK values (PTTK wins completely)
4. **If no PTTK** → keep field definitions from RSD

### Step 4b: Validate Documents & Ask Clarification

After extraction, check for issues and **proactively ask user** before proceeding:

**Missing information (MUST ask):**
- RSD has no error codes or error code table is empty → ask: "RSD không có bảng mã lỗi. Bạn có tài liệu bổ sung không, hay bỏ qua phần error codes?"
- Cannot find the exact API/screen in PTTK → ask: "PTTK có nhiều API, không tìm thấy endpoint `{endpoint}`. Bạn muốn dùng API nào?" (list candidates)
- Field type unclear (RSD says "text" but no maxLength, no format) → ask: "Field `{name}` không có maxLength/format trong tài liệu. Giá trị mặc định nào phù hợp?"
- screenType ambiguous (has both grid and form elements) → ask: "Màn hình này vừa có lưới vừa có form. screenType là LIST hay FORM?"
- No permissions section in RSD → ask: "RSD không mô tả phân quyền. Bỏ qua section phân quyền hay tạo mặc định?"

**Conflicts between documents (MUST ask):**
- PTTK field name differs from RSD field name → ask: "PTTK gọi là `{pttk_name}` nhưng RSD gọi là `{rsd_name}`. Dùng tên nào?"
- PTTK says required but RSD says optional (or vice versa) → ask: "Field `{name}`: PTTK = required, RSD = optional. Theo tài liệu nào?"
- Different data types between documents → ask: "Field `{name}`: PTTK type = `{type1}`, RSD type = `{type2}`. Dùng type nào?"
- Response structure differs between PTTK and RSD → follow PTTK (per priority rules), but note the difference

**Suspicious/unclear content (SHOULD ask):**
- Business logic description is vague or uses ambiguous words ("có thể", "tùy trường hợp") → ask: "Logic `{description}` không rõ ràng. Cụ thể điều kiện là gì?"
- Image shows field/button not in RSD → ask: "Hình ảnh có `{element}` nhưng RSD không đề cập. Thêm vào test design không?"
- Duplicate fields with different specs → ask: "Field `{name}` xuất hiện 2 lần với spec khác nhau. Dùng spec nào?"

**DO NOT ask if:**
- Information can be reasonably inferred (e.g., WRONG_METHODS from API method)
- Priority rules already define the answer (e.g., PTTK wins for field definitions)
- It's a formatting/style question covered by references

### Step 5: Generate Test Design Sections

Generate the test design following the rules loaded via `--ref` and the format of the catalog examples.
#### API Mode — Generation

**Common section (hardcoded):** Copy the base template exactly — only replace `{API_NAME}` and `{WRONG_METHODS}`. Format: `- status: 107` (simple). NEVER use `1\. Check api trả về:` in common.

**Validate section (per-field):** For each inputField from Phase 2, generate test cases using the field templates in `--ref api-test-design`:
- String Required → test: empty, missing, null, maxLen-1/maxLen/maxLen+1, numeric, accented chars, special chars, spaces, emoji, unicode, boolean, array, object, XSS, SQL injection
- Integer with default → test: empty/missing/null (uses default), valid value, negative, decimal, string
- Optional Integer → test: empty/missing/null (returns all), valid/invalid value, string
- ALL validate responses use Status: 200 (errors in body, NOT 400/422/500)
- JSON response must be multiline WITHOUT backtick fence

**Main flow section (LLM-generated):** Every test case MUST include response with `1\. Check api trả về:` / `1\.1. Status:` / `1\.2. Response:` format:
1. Response fields verification — list ALL output fields (camelCase) with sample values
2. DB mapping verification — full SQL: SELECT/FROM/WHERE/ORDER BY with concrete values
3. Search scenarios — exact, approximate (LIKE), combined conditions, not found
4. Sort order verification — ORDER BY clause
5. Error code scenarios — each error code → 1 test case with exact message
6. Business logic branches — each if/else → test both true and false, each with Response
7. DB validations — exists/not exists → test both cases
8. Mode variations — create/update/delete → test each mode
9. Status transitions — valid/invalid transitions → test each

**Verify + supplement:** Re-read RSD, list ALL logic branches, cross-check with generated test cases. Missing → add. Wrong expected result → write `### [SỬA] Kiểm tra ...` and replace.

#### Frontend Mode — Generation

**Common UI section (hardcoded):** Navigation, layout, breadcrumb, zoom — copy template from `--ref frontend-test-design`.

**Permission section (hardcoded):** No permission / has permission — 2 test cases.

**Validate section (per-field templates):** Dispatch by field.type using `--ref field-templates`:

| field.type | Template |
|-----------|----------|
| textbox/text/input | generateTextboxTests |
| combobox | generateComboboxTests |
| dropdown (values[]) | generateSimpleDropdownTests |
| dropdown (apiEndpoint) | generateSearchableDropdownTests |
| toggle/switch | generateToggleTests |
| checkbox | generateCheckboxTests |
| button | generateButtonTests |
| icon_x/icon_close | generateIconXTests |

After field templates, supplement with LLM for: cross-field validation, special values, cascading fields, auto-fill rules.

**For DETAIL screens:** Do NOT use field templates. Use `generateDetailDataSection()` — test data display, null/empty handling, SQL queries per field.

**Grid section (LIST only):** Default state, sort order, each column with SQL, scroll behavior (pinned columns), data verification.

**Pagination section (hardcoded):** Values, default, per-value test, page navigation. Only generate when pagination exists.

**Function section (LLM-generated per screenType):**
- **LIST:** Search per field (exists/not exists/partial), combined search, clear filter, add new button
- **FORM/POPUP:** Save success/fail, field interactions (enable/disable, auto-fill, dependent validation), cancel
- **DETAIL:** Button visibility by status/permission, click actions, navigation

**Verify + supplement:** Re-read RSD and verify all search scenarios, field combinations, empty results, business rules are covered. Missing → append. Wrong → `### [SỬA]` and replace.

### Step 6: Apply Quality Rules

Load quality rules and verify:
```bash
python <skills-root>/test-design-generator/scripts/search.py --ref quality-rules
```

Checklist:
- 100% Vietnamese, keep field/button names exactly as in RSD/PTTK
- No placeholders — use concrete sample values in SQL and responses
- 1 test = 1 check (atomic)
- Forbidden words: "và/hoặc", "hoặc", "có thể", "nên", "ví dụ:", "[placeholder]"
- SQL: concrete values (`WHERE ID = 10001`), UPPERCASE columns, NO placeholders
- Output starts with `# {API_NAME}` or `# {SCREEN_NAME}` — NO blockquote header, NO `---` horizontal rules

## Catalog Management

### Add Examples to Catalog

To add new reference examples:
1. Save the test design output as a `.md` file
2. Place it in `catalog/api/` or `catalog/frontend/` at your project root
3. The search engine will automatically index new files

### List Available Examples

```bash
python <skills-root>/test-design-generator/scripts/search.py --list
```

## Project Structure

After running `test-genie init`, your project has this structure:

```
<project-root>/
├── node_modules/test-genie/           ← Skills live here (managed by npm)
│   ├── test-design-generator/
│   │   ├── SKILL.md                      ← Workflow instructions (this file)
│   │   ├── AGENTS.md                     ← Skill-level default rules
│   │   ├── references/                   ← Detailed rules (dev-managed)
│   │   │   ├── priority-rules.md
│   │   │   ├── api-test-design.md
│   │   │   ├── frontend-test-design.md
│   │   │   ├── field-templates.md
│   │   │   ├── output-examples.md
│   │   │   └── quality-rules.md
│   │   ├── data/rules/
│   │   │   └── api-rules.csv             ← Format rules (searchable via --domain rules)
│   │   └── scripts/
│   │       └── search.py
│   └── test-case-generator/
│       └── ...
├── .claude/commands/                  ← Claude slash commands (auto-generated)
│   ├── generate-test-case.md
│   └── generate-test-design.md
├── .cursor/commands/                  ← Cursor slash commands (auto-generated)
│   ├── generate-test-case.mdc
│   └── generate-test-design.mdc
├── .cursor/rules/
│   └── test-genie.mdc                 ← Cursor auto-loads when relevant
├── catalog/                           ← Managed by user/tester
│   ├── api/                              ← API test design .md examples
│   ├── frontend/                         ← Frontend test design .md examples
│   └── mobile/                           ← Mobile test design examples
├── excel_template/
│   └── template.xlsx                  ← Spreadsheet template (used by test-case-generator)
└── AGENTS.md                          ← Project-specific rules (user-managed)
```

## Key Format Rules (Quick Reference)

### API Test Design

| Section | Format |
|---------|--------|
| Common | `- status: 107` (simple, NO `1\. Check api trả về:`) |
| Validate | `- 1\. Check api trả về: 1\.1. Status: 200 1\.2. Response: {...}` |
| Luồng chính | Same as validate — MUST include Response JSON |

### Critical Rules
- Output starts with `# {API_NAME}` — NO blockquote header
- NO `---` horizontal rules between sections
- ALL validate responses use Status: 200 (errors in body)
- SQL uses concrete values, UPPERCASE columns, NO placeholders
- Response body format comes from PTTK (no fixed format)
