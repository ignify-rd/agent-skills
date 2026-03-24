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
- User uploads .pdf/.txt/.md files for test design / mindmap generation
- Called internally by `test-case-generator` skill when user provides only RSD+PTTK without a mindmap

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## ⚠️ Đọc file PDF — KHÔNG tự viết parser

**TUYỆT ĐỐI KHÔNG được tự viết code parse PDF** (không tạo extract_pdf.py, extract_pdf.ps1, không parse xref table, không decode binary). Thay vào đó:

**Cách 1 (ưu tiên): Dùng Read tool trực tiếp**
- Hầu hết AI tools (Claude Code, Cursor, Windsurf) có thể đọc PDF trực tiếp bằng Read tool
- Chỉ cần: `Read file: path/to/document.pdf`
- Nếu file lớn, đọc theo pages: `Read file: path/to/document.pdf pages=1-10`

**Cách 2 (fallback): Dùng Python + PyPDF2/pdfplumber**
```bash
# Cài đặt nếu chưa có
python3 -m pip install PyPDF2

# Extract text từ PDF
python3 -c "
import PyPDF2
reader = PyPDF2.PdfReader('path/to/document.pdf')
for page in reader.pages:
    print(page.extract_text())
"
```

**Cách 3 (fallback 2): pdftotext (nếu có sẵn)**
```bash
pdftotext "path/to/document.pdf" -
```

**KHÔNG BAO GIỜ:**
- Tạo file script mới để parse PDF (extract_pdf.py, extract_pdf.ps1...)
- Parse PDF binary format thủ công (xref table, byte offsets, content streams)
- Mất hơn 30 giây để đọc 1 file PDF — nếu quá lâu, chuyển sang cách khác

## Rule Override Hierarchy

Rules are resolved in this order (highest priority first):

1. **Project `AGENTS.md`** — `AGENTS.md` at project root (user-managed, project-specific overrides)
2. **Skill-level `AGENTS.md`** — `test-design-generator/AGENTS.md` (default rules)
3. **Skill references** — `references/*.md` (detailed rules, managed by dev team)
4. **This SKILL.md** — workflow instructions (lowest priority, never overridden)

**How overrides work:** Rules in project `AGENTS.md` are merged with skill defaults — only the sections/rules explicitly defined in project `AGENTS.md` override the corresponding defaults. Sections not mentioned fall back to skill-level `AGENTS.md`.

## Workflow

### Step 0: Validate Project Setup & Load Project Rules

Before starting generation, check project structure and **load project-level rules**:

1. **Check catalog** — look for `catalog/` directory at project root (contains `api/`, `frontend/`, `mobile/`)
2. **Check & READ AGENTS.md** — look for `AGENTS.md` at project root (project-level rules)

**If catalog directory does not exist:**
- Ask user: "Chưa có thư mục `catalog/`. Bạn đã chạy `test-genie init` chưa?"
- If not → guide user to run `test-genie init` to set up project structure

**If AGENTS.md exists at project root:**
- **READ the entire file content** — extract ALL sections and rules defined by the project
- Store these rules as `projectRules` — they will be applied with **HIGHEST PRIORITY** throughout the entire generation workflow
- Any rule in project AGENTS.md **overrides** the corresponding rule in skill-level AGENTS.md and references
- Sections in project AGENTS.md that don't exist in defaults are **ADDED** (not ignored)
- Pay special attention to `## Project-Specific Rules` — these are custom rules that MUST be followed in every step

**If AGENTS.md does not exist at project root:**
- Use skill-level `AGENTS.md` (default rules)
- Inform user: "Project chưa có AGENTS.md. Đang dùng rules mặc định."

**If catalog exists but has no examples (empty api/ and frontend/):**
- Warn user: "Catalog chưa có examples. Output có thể không chính xác format. Bạn có muốn thêm examples trước không?"
- Proceed with skill references as fallback

**⚠️ CRITICAL: Project AGENTS.md is the highest-priority rule source.** Every subsequent step (mode detection, extraction, generation, verification) MUST check `projectRules` and apply them. If a project rule conflicts with a skill reference or default, the project rule WINS.

### Step 0b: Resolve Input Documents

**If user provides a feature folder name** (e.g., `/generate-test-design feature-1` or `sinh test design cho feature-1`):
1. Look inside `<feature-name>/` folder for input documents automatically:
   - Scan for document files: `.pdf`, `.docx`, `.doc`, `.md`, `.txt` — identify RSD and PTTK by filename
2. **DO NOT ask** the user for file paths — use whatever documents are found in the folder
3. **If folder is empty** → scan toàn bộ project root cho document files liên quan đến feature name
4. If truly no documents found → inform user: "Không tìm thấy tài liệu RSD/PTTK. Hãy cung cấp đường dẫn hoặc upload file."
5. Save output as `<feature-name>/test-design.md`

### Step 1: Determine Mode

| Input | Mode | Output |
|-------|------|--------|
| RSD describes an API endpoint | API | Markdown test design for API |
| RSD describes a UI screen | Frontend | Markdown test design for Frontend |

#### Heuristic-first detection (rule-based, no LLM needed)

Apply these regex/keyword checks on the RSD **before** asking LLM:

| Heuristic | Mode | Confidence |
|-----------|------|------------|
| Title/heading matches `(GET\|POST\|PUT\|DELETE\|PATCH)\s+/` | API | High |
| Document contains `endpoint`, `request body`, `response body`, `API` (case-insensitive) in first 2 pages | API | Medium |
| Document contains `màn hình`, `screen`, `giao diện`, `button`, `textbox`, `combobox`, `lưới` | Frontend | Medium |
| Title contains `Danh sách`, `Chi tiết`, `Thêm mới`, `Cập nhật` + UI element names | Frontend | Medium |

**Decision logic:**
1. If heuristic returns **High confidence** → use that mode, skip LLM detection
2. If heuristic returns **Medium confidence** → use that mode but note in output: "Mode detected by heuristic: {mode}"
3. If **no heuristic matches** or **conflicting signals** → fallback to LLM to read RSD and determine mode

### Step 2: Load Rules & References

**Step 2a: Apply project AGENTS.md rules (loaded in Step 0)**

Before loading any references, review `projectRules` from Step 0. Project rules affect:
- **Which sections to generate** — project may add/remove/rename sections
- **How to generate each section** — project may override field template dispatch, screen type rules, format rules
- **Quality/style constraints** — project may define custom forbidden phrases, naming conventions, writing style
- **Test case granularity** — project may require splitting cases differently (e.g., "tách riêng từng field", "buttons vào phần chức năng")
- **Image analysis behavior** — project may require analyzing images before reading RSD
- **Custom field types** — project may define field types not in default templates

All rules from project AGENTS.md apply as overrides throughout the remaining steps. If project AGENTS.md defines a rule that contradicts a skill reference, **follow the project rule**.

**Step 2b: Load skill references (mode-specific)**

**Load ONLY the references needed for the detected mode.** Do NOT load all references upfront.

#### Resolve SKILL_SCRIPTS path

Scripts are installed alongside this SKILL.md file in a `scripts/` subdirectory. Try these methods in order:

**Method 1 — Recursive find from project root:**
```bash
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/test-design-generator/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
echo "SKILL_SCRIPTS=$SKILL_SCRIPTS"
```

**Method 2 — Direct path check (if Method 1 returns empty):**
```bash
for d in \
  ".claude/skills/test-design-generator/scripts" \
  ".cursor/skills/test-design-generator/scripts" \
  ".windsurf/skills/test-design-generator/scripts" \
  ".roo/skills/test-design-generator/scripts" \
  ".kiro/skills/test-design-generator/scripts"; do
  [ -f "$d/search.py" ] && SKILL_SCRIPTS="$d" && break
done
echo "SKILL_SCRIPTS=$SKILL_SCRIPTS"
```

**Method 3 — Global npm (if Method 2 returns empty):**
```bash
npm_root=$(npm root -g 2>/dev/null)
[ -n "$npm_root" ] && [ -f "$npm_root/test-genie/test-design-generator/scripts/search.py" ] && \
  SKILL_SCRIPTS="$npm_root/test-genie/test-design-generator/scripts"
```

**Method 4 — CRITICAL FALLBACK (if all above fail): Read reference files directly**

If `SKILL_SCRIPTS` is still empty after all methods, **DO NOT skip loading references**. Instead, read the reference files directly using the Read tool (or equivalent file reading capability):

```
READ: <skills-dir>/test-design-generator/references/priority-rules.md
READ: <skills-dir>/test-design-generator/references/quality-rules.md
READ: <skills-dir>/test-design-generator/references/api-test-design.md      (API mode only)
READ: <skills-dir>/test-design-generator/references/frontend-test-design.md  (Frontend mode only)
READ: <skills-dir>/test-design-generator/references/field-templates.md       (Frontend mode only)
```

Where `<skills-dir>` is wherever the `.claude/`, `.cursor/`, etc. directory is found. Try common paths:
- `.claude/skills/`
- `.cursor/skills/`
- `.windsurf/skills/`

**⚠️ NEVER proceed without loading references.** The format template in `api-test-design.md` is mandatory — without it the output will be in wrong format. If you truly cannot find any reference file, inform the user: "Không tìm thấy skill scripts. Bạn có thể chạy `test-genie init` để khởi tạo lại không?"

**Note:** `search.py` auto-detects the project root by looking for `catalog/` or `AGENTS.md`. You can also pass `--project-root /path/to/project` explicitly.

#### Load by mode (lazy-load)

**Always load first (both modes):**
```bash
python $SKILL_SCRIPTS/search.py --ref priority-rules
python $SKILL_SCRIPTS/search.py --ref quality-rules
```

**API mode — load this only:**
```bash
python $SKILL_SCRIPTS/search.py --ref api-test-design
```

**Frontend mode — load these only:**
```bash
python $SKILL_SCRIPTS/search.py --ref frontend-test-design
python $SKILL_SCRIPTS/search.py --ref field-templates
```

> **Why lazy-load?** Loading all references regardless of mode wastes 30-50% tokens on rules that won't be used. Only load what the detected mode requires.

#### Search examples & utilities

```bash
# Search API examples by keyword (searches catalog/api/ in project root)
python $SKILL_SCRIPTS/search.py "search list api" --domain api

# Search Frontend examples (searches catalog/frontend/ in project root)
python $SKILL_SCRIPTS/search.py "danh sach list screen" --domain frontend

# Search format rules (skill-bundled, not in project catalog)
python $SKILL_SCRIPTS/search.py "common section status" --domain rules

# List all available references
python $SKILL_SCRIPTS/search.py --list-refs

# List all available examples
python $SKILL_SCRIPTS/search.py --list

# Read full content of top match
python $SKILL_SCRIPTS/search.py "export excel" --domain api --full
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

**⚠️ THỨ TỰ BẮT BUỘC: Đọc RSD/PTTK TRƯỚC — ảnh CHỈ bổ sung SAU.** Không được đọc ảnh trước rồi dùng RSD để "sửa lại". RSD/PTTK là nguồn chính, ảnh chỉ thêm thông tin RSD/PTTK thiếu.

**Phase 1: RSD → screen structure + business logic (LUÔN đọc TRƯỚC TIÊN)**
1. Extract: screenName, screenType (LIST/FORM/POPUP/DETAIL), breadcrumb, permissions, UI elements
2. Extract: fields with types (textbox/combobox/dropdown/toggle/checkbox/button/icon_x)
3. Extract: **maxLength, minLength, data types, required/optional, format constraints, enum values** cho từng field — ghi lại chính xác từ RSD
4. Extract: grid columns (name, dbColumn, dbTable, format), pagination values, sort order
5. Extract: button visibility rules by status/permission, additional features
6. **Extract business logic:** điều kiện enable/disable, auto-fill rules, cascading dependencies, validation rules nghiệp vụ (VD: "Ngày hiệu lực phải >= ngày hiện tại", "Mã SLA unique"), error messages, luồng save/submit, status transitions

**Phase 2: PTTK → field definitions (if available)**
1. Find the exact screen/API in PTTK by name or endpoint
2. Extract: field names, types, API endpoints, DB mappings, enum values, maxLength, format constraints
3. **REPLACE** all field definitions from RSD with PTTK values (PTTK wins completely)
4. **If no PTTK** → keep field definitions from RSD

**Phase 3: Analyze images (if provided — CUỐI CÙNG)**
1. For each image: extract screenType, buttons, inputFields (label, type, placeholder, location), gridColumns, hasPagination
2. Consolidate all image analyses into one structure
3. **⚠️ CRITICAL merge rule:** So sánh với data đã extract từ Phase 1+2:
   - Hình ảnh **CHỈ bổ sung** thông tin mà RSD/PTTK **KHÔNG có**: placeholder text, hasIconX, button labels, vị trí field
   - Hình ảnh **KHÔNG ĐƯỢC override** bất kỳ thông tin nào từ RSD/PTTK: field names, maxLength, minLength, data types, required/optional, format constraints, enum values, API endpoints, validation rules
   - Nếu conflict → **LUÔN giữ giá trị từ RSD/PTTK (Phase 1+2)**
   - Nếu ảnh có field/button không trong RSD → **hỏi user trước khi thêm**

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

### Step 4c: Business Logic Inventory (CẢ API và Frontend)

**Before generating any section**, extract toàn bộ business logic thành inventory. Đây là checklist để đảm bảo mọi item đều xuất hiện trong mindmap đúng section.

#### API Mode Inventory:
```json
{
  "errorCodes": [
    { "code": "PCER_UPLOAD_001", "desc": "exact từ RSD", "section": "validate", "triggerCondition": "file format sai" },
    { "code": "PCER_UPLOAD_004", "desc": "exact từ RSD", "section": "validate", "triggerCondition": "file sai template" },
    { "code": "2", "desc": "Có lỗi xảy ra trong quá trình xử lý", "section": "main", "triggerCondition": "S3 error hoặc DB error" }
  ],
  "businessRules": [
    { "id": "BR1", "condition": "uploadType = 1", "trueBranch": "INSERT với action=ADD", "falseBranch": null, "section": "main" },
    { "id": "BR2", "condition": "uploadType = 2", "trueBranch": "INSERT với action=DELETE", "falseBranch": null, "section": "main" }
  ],
  "dbFields": [
    "ID (auto)", "DOMAIN_TYPE", "FEE_SERVICE", "CUSTOMER_ID", "BRANCH (= bdsCode + '000')",
    "STATUS (= 1)", "UPLOAD_TYPE", "CREATED_USER", "CREATED_TIME", "TOTAL_UPLOAD", "FILE_NAME", "S3_FILE_KEY"
  ],
  "externalServices": [
    { "name": "S3", "onFailure": "error code 2", "rollbackBehavior": "không INSERT DB" }
  ],
  "modes": ["uploadType=1 (Thêm mới)", "uploadType=2 (Xoá)"]
}
```

#### Frontend Mode Inventory:

**⚠️ Frontend CŨ̃NG PHẢI extract business logic từ RSD — KHÔNG được bỏ qua.**

```json
{
  "screenName": "Tạo mới SLA",
  "screenType": "FORM",
  "fieldConstraints": [
    { "field": "Tên cấu hình SLA", "type": "textbox", "maxLength": 100, "required": true, "unique": true, "source": "RSD" },
    { "field": "Ngày hiệu lực", "type": "datepicker", "constraint": ">= ngày hiện tại", "required": true, "source": "RSD" }
  ],
  "businessRules": [
    { "id": "BR1", "type": "validation", "condition": "Tên cấu hình SLA đã tồn tại", "expected": "Hiển thị cảnh báo 'Tên cấu hình SLA đã tồn tại'", "section": "validate" },
    { "id": "BR2", "type": "condition", "condition": "Ngày hiệu lực < ngày hiện tại", "expected": "Không cho phép chọn", "section": "validate" },
    { "id": "BR3", "type": "flow", "condition": "Click Lưu khi form hợp lệ", "expected": "Lưu thành công, hiển thị thông báo", "section": "function" },
    { "id": "BR4", "type": "flow", "condition": "Click Lưu khi form có lỗi validate", "expected": "Hiển thị cảnh báo lỗi", "section": "function" }
  ],
  "errorMessages": [
    { "trigger": "Bỏ trống field bắt buộc", "message": "exact message từ RSD", "section": "validate" },
    { "trigger": "Nhập quá maxLength", "message": "exact message từ RSD", "section": "validate" },
    { "trigger": "Lưu thất bại", "message": "exact message từ RSD", "section": "function" }
  ],
  "enableDisableRules": [
    { "field": "Button Lưu", "condition": "Form chưa nhập đủ required fields", "state": "disable" },
    { "field": "Dropdown X", "condition": "Chọn loại A", "state": "enable", "cascading": "load danh sách theo loại A" }
  ],
  "autoFillRules": [
    { "trigger": "Chọn giá trị tại Dropdown X", "target": "Field Y", "action": "auto-fill giá trị tương ứng" }
  ],
  "statusTransitions": [
    { "from": "Draft", "to": "Active", "trigger": "Click Phê duyệt" }
  ],
  "permissions": [
    { "action": "Xem", "role": "Viewer" },
    { "action": "Tạo mới", "role": "Maker" },
    { "action": "Phê duyệt", "role": "Checker" }
  ]
}
```

**Extraction rules (API):**
- `errorCodes[].section`: `"validate"` = thuộc section "Kiểm tra validate" trong mindmap; `"main"` = thuộc "Kiểm tra luồng chính"
- `errorCodes[].desc`: copy **exact** từ bảng mã lỗi trong RSD/PTTK — **đọc toàn bộ bảng, không bỏ sót dòng nào**
- `dbFields[]`: lấy từ bảng DB mapping trong PTTK — **list 100% columns** kể cả auto-generate và derived fields
- `externalServices[].rollbackBehavior`: nếu RSD mô tả "không lưu DB khi lỗi" → ghi rõ, cần 1 bullet trong mindmap

**Dùng inventory này khi sinh từng section (API):**
- Error codes có `section="validate"` → phải xuất hiện trong ## Kiểm tra validate
- Error codes có `section="main"` → phải xuất hiện trong ## Kiểm tra luồng chính
- `dbFields[]` → tất cả fields phải có trong SQL verify của luồng chính
- `rollbackBehavior` → phải có bullet "S3 lỗi → không INSERT vào DB" trong luồng chính

**Extraction rules (Frontend):**
- `fieldConstraints[]`: lấy từ RSD/PTTK — **maxLength, minLength, required, unique, format** phải chính xác từ tài liệu, KHÔNG đoán từ ảnh
- `businessRules[]`: đọc **toàn bộ mô tả nghiệp vụ** trong RSD — mỗi condition/if-else/validation rule = 1 entry
- `errorMessages[]`: copy **exact** message từ RSD — đọc toàn bộ bảng thông báo lỗi, không bỏ sót
- `enableDisableRules[]`: lấy từ RSD mô tả điều kiện enable/disable cho từng field/button
- `autoFillRules[]`: lấy từ RSD mô tả auto-fill, cascading dependencies
- `statusTransitions[]`: lấy từ RSD flow diagram hoặc mô tả luồng
- `permissions[]`: lấy từ RSD phân quyền

**Dùng inventory này khi sinh từng section (Frontend):**
- `fieldConstraints[]` → mỗi field PHẢI dùng maxLength/minLength/required/unique từ inventory, KHÔNG từ ảnh
- `businessRules[section="validate"]` → phải có bullet trong ## Kiểm tra validate
- `businessRules[section="function"]` → phải có bullet trong ## Kiểm tra chức năng
- `errorMessages[]` → mỗi error message phải có ≥1 bullet test case
- `enableDisableRules[]` → phải có test case cho từng rule enable/disable
- `autoFillRules[]` → phải có test case cho từng auto-fill behavior
- `permissions[]` → mỗi role phải có test case trong ## Kiểm tra phân quyền

### Step 5: Generate Test Design Sections

Generate the test design following the rules loaded via `--ref` and the format of the catalog examples.

**⚠️ BEFORE generating any section, review `projectRules` from Step 0.** Project AGENTS.md rules MUST be applied throughout generation:
- If project defines custom section structure (e.g., "buttons vào phần chức năng thay vì validate") → follow that
- If project defines writing style (e.g., "viết ngắn gọn", "tách riêng từng case") → follow that
- If project defines image analysis behavior (e.g., "phân tích hình ảnh trước") → follow that
- If project defines custom field handling not in default templates → follow that
- If project defines any `## Project-Specific Rules` → apply ALL of them to every section
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

**Verify — coverage checklist (API):**

Dùng inventory JSON từ Step 4c để cross-check — **không re-read toàn bộ RSD**:

**A. Error Code Coverage**
```
Với mỗi errorCodes[]:
  → section="validate": phải có bullet trong ## Kiểm tra validate (đúng subsection field)
  → section="main":     phải có bullet trong ## Kiểm tra luồng chính
  → Bullet phải chứa exact error code và mô tả ngắn trigger condition
  → Nếu thiếu: THÊM bullet vào đúng section, đánh dấu ### [SỬA]
```

**B. Business Rule Coverage**
```
Với mỗi businessRules[]:
  → type="branch": cần 2 bullets (trueBranch + falseBranch)
  → Nếu thiếu: THÊM vào ## Kiểm tra luồng chính
```

**C. DB Field Coverage**
```
Với dbFields[]:
  → Tất cả fields phải xuất hiện trong SQL SELECT của luồng chính
  → Đặc biệt check: CREATED_TIME, S3_FILE_KEY, BRANCH (derived), TOTAL_UPLOAD
  → Nếu thiếu: UPDATE bullet luồng chính để thêm fields vào SQL
```

**D. Rollback Coverage**
```
Với externalServices[].rollbackBehavior:
  → Phải có bullet: "{ServiceName} lỗi → không INSERT vào DB"
  → Nếu thiếu: THÊM vào ## Kiểm tra luồng chính
```

**E. Mode Coverage**
```
Với modes[]:
  → Mỗi mode cần ≥1 bullet happy path trong luồng chính
  → Nếu thiếu: THÊM
```

Nếu bất kỳ item nào NO → thêm bullet với `### [SỬA] Kiểm tra ...`

#### Frontend Mode — Generation

**Common UI section (hardcoded):** Navigation, layout, breadcrumb, zoom — copy template from `--ref frontend-test-design`.

**Permission section (hardcoded):** No permission / has permission — 2 test cases.

**Validate section (per-field templates):** Dispatch by field.type using `--ref field-templates`. **QUAN TRỌNG: Phải output ĐẦY ĐỦ TẤT CẢ cases có trong template — không được bỏ bớt, không được chọn lọc.**

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
| date/datepicker | generateDatePickerTests |
| daterange/date_range | generateDateRangePickerTests |
| textarea/multiline | generateTextareaTests |
| number/number_input | generateNumberInputTests |
| radio/radio_group | generateRadioButtonTests |
| file/file_upload/upload | generateFileUploadTests |
| password/password_input | generatePasswordInputTests |
| tag/tag_input/chip | generateTagInputTests |
| richtext/rich_text_editor | generateRichTextEditorTests |

**Mandatory completeness rule — KHÔNG được bỏ bất kỳ case nào trong template:**

Với mỗi textbox editable, bắt buộc sinh ĐỦ các cases sau (lấy từ field-templates.md):
- Hiển thị mặc định, giá trị mặc định, placeholder
- Icon X: hiển thị khi nhập, xóa nhanh
- Nhập số, nhập chữ, nhập ký tự đặc biệt (@#$%^&*)
- Nhập ký tự chứa space đầu/cuối, Paste ký tự chứa space đầu/cuối, nhập all space
- Boundary: nhập maxLen-1, maxLen, Paste maxLen, nhập maxLen+1 → cảnh báo
- **Bắt buộc (đã có trong template):** emoji, XSS (`<script>alert(1)</script>`), SQL injection (`' OR 1=1 --`), unicode đặc biệt, chữ có dấu tiếng Việt
- MinLength boundary: minLen-1 → lỗi, minLen → ok (nếu có minLength)
- Required validation: bỏ trống → lỗi (nếu isRequired)
- Format validation: đúng/sai định dạng (nếu có regex/pattern)
- Conditional disabled state (nếu field có thể bị disabled theo điều kiện)

Với mỗi combobox/dropdown, bắt buộc sinh ĐỦ:
- Hiển thị, placeholder, icon X, chọn 1/nhiều
- API error, API trả rỗng → "Không tìm thấy", loading state
- Search textbox: số, chữ, ký tự đặc biệt, emoji, XSS, SQL injection, maxSearchLen boundary
- Tìm từ khóa tồn tại/không tồn tại/1 phần, chọn bằng chuột/bàn phím
- Required validation (nếu có)

Với mỗi date picker/date range, bắt buộc sinh ĐỦ:
- Hiển thị, placeholder, icon lịch, chọn ngày hợp lệ, nhập sai định dạng, ngày không tồn tại
- Min/max date boundary, ngày quá khứ/tương lai (nếu có constraint)
- Icon X, required validation, emoji/XSS/SQL injection

Với mỗi number input, bắt buộc sinh ĐỦ:
- Nhập số dương, số 0, số âm, số thập phân, leading zero
- Nhập chữ/ký tự đặc biệt/khoảng trắng → chặn
- Min/max value boundary, stepper +/- (nếu có)
- emoji/XSS/SQL injection

Với mỗi file upload, bắt buộc sinh ĐỦ:
- Upload đúng/sai định dạng, dung lượng boundary, file rỗng
- Upload trùng tên, tên chứa ký tự đặc biệt/unicode
- Progress, hủy upload, xóa file, drag & drop (nếu có)

Với mỗi textarea, bắt buộc sinh ĐỦ:
- Tất cả cases của textbox + xuống dòng (Enter), multiline, bộ đếm ký tự (nếu có)

Sau khi áp dụng template, supplement thêm với LLM: cross-field validation, cascading fields, auto-fill rules.

**For DETAIL screens:** Do NOT use field templates. Use `generateDetailDataSection()` — test data display, null/empty handling, SQL queries per field.

**Grid section (LIST only):** Default state, sort order, each column with SQL, scroll behavior (pinned columns), data verification.

**Pagination section (hardcoded):** Values, default, per-value test, page navigation. Only generate when pagination exists.

**Function section (LLM-generated per screenType) — PHẢI dùng inventory từ Step 4c:**

**⚠️ Section này phải cover TOÀN BỘ business logic từ inventory. Không được bỏ qua nghiệp vụ.**

Dùng `businessRules[]`, `enableDisableRules[]`, `autoFillRules[]`, `statusTransitions[]`, `errorMessages[section="function"]` từ inventory:

- **LIST:** Search per field (exists/not exists/partial), combined search, clear filter, add new button
- **FORM/POPUP:**
  - Save success (form hợp lệ) → expected: thông báo thành công
  - Save fail (form có lỗi) → expected: exact error message từ `errorMessages[]`
  - Từng `enableDisableRules[]` → test case enable/disable
  - Từng `autoFillRules[]` → test case auto-fill behavior
  - Từng `businessRules[section="function"]` → test case cho mỗi condition
  - Cancel, back navigation
- **DETAIL:** Button visibility by status/permission, click actions, navigation, status transitions
- **All screen types:**
  - Từng `statusTransitions[]` → test valid/invalid transition
  - Từng `permissions[]` → test action visibility/accessibility per role
  - Any button-related test cases belong in function section (not validate) — buttons test logic flow, not input validation

**⚠️ Project AGENTS.md override:** If project AGENTS.md defines additional function section rules (e.g., "buttons vào phần chức năng", custom section assignments), apply them here. Project rules take precedence over the defaults above.

**Verify — coverage checklist (Frontend) — dùng inventory từ Step 4c:**

Verify against inventory JSON VÀ checklist cố định:

**A. Field Constraint Coverage (từ `fieldConstraints[]`):**
- [ ] Mỗi field có test cases dùng **đúng maxLength/minLength/required từ inventory** (KHÔNG từ ảnh)
- [ ] Field có `unique: true` → có test case "nhập giá trị đã tồn tại"
- [ ] Field có `constraint` (VD: ">= ngày hiện tại") → có test case boundary cho constraint đó

**B. Business Rule Coverage (từ `businessRules[]`):**
- [ ] Mỗi `businessRules[]` có ≥1 test case trong đúng section (validate/function)
- [ ] Mỗi condition có test case cho BOTH true/false paths

**C. Error Message Coverage (từ `errorMessages[]`):**
- [ ] Mỗi `errorMessages[]` có test case với **exact message** từ inventory
- [ ] Error messages nằm đúng section (validate/function)

**D. Enable/Disable Coverage (từ `enableDisableRules[]`):**
- [ ] Mỗi rule có test case cho state enable VÀ disable

**E. Auto-fill/Cascading Coverage (từ `autoFillRules[]`):**
- [ ] Mỗi auto-fill rule có test case verify auto-fill behavior

**F. Standard Coverage:**
- [ ] **All fields covered**: Every field from RSD/PTTK has validate test cases
- [ ] **All fields from images**: Every visible field in images has test cases (nếu có trong RSD)
- [ ] **Field types match templates**: Each field dispatched to correct template
- [ ] **Search scenarios**: Every searchable field has exists/not exists/partial (LIST only)
- [ ] **Grid columns**: Every column has data verification + sort (LIST only)
- [ ] **Empty state**: Grid empty, form default state tested
- [ ] **Permissions**: Has/no permission test cases exist
- [ ] **Test case granularity**: 1 test = 1 check, no vague cases
- [ ] **Section assignment**: Buttons in "chức năng", not "validate"
- [ ] **Project AGENTS.md rules**: ALL project-specific rules satisfied

If any item is NO → append missing test cases. Wrong expected result → `### [SỬA]` and replace.

### Step 5b: Final Project Rules Enforcement

**⚠️ MANDATORY — Đọc lại TOÀN BỘ `projectRules` (từ Step 0) và kiểm tra output lần cuối:**

1. Đọc lại `## Project-Specific Rules` trong project AGENTS.md
2. Duyệt từng rule → kiểm tra output đã tuân thủ chưa
3. Nếu vi phạm → sửa ngay trước khi chuyển Step 6

**Các lỗi thường gặp khi quên projectRules:**
- maxLength/minLength lấy sai nguồn (từ ảnh thay vì RSD/PTTK)
- Button test cases nằm trong "Kiểm tra validate" thay vì "Kiểm tra chức năng"
- Test case viết dài dòng thay vì ngắn gọn
- Case chung chung thay vì tách riêng từng giá trị cụ thể
- Ảnh có field nhưng thiếu test case (chưa cover toàn bộ màn hình)

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
- **Project AGENTS.md quality rules**: If project defines additional quality constraints (e.g., "viết ngắn gọn", custom forbidden phrases, writing style) → apply them on top of defaults

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
│   │       └── search.py                 ← Catalog search (auto-detects project root)
│   └── test-case-generator/
│       └── ...
├── .claude/commands/                  ← Claude slash commands (auto-generated)
│   ├── generate-test-case.md
│   └── generate-test-design.md
├── catalog/                           ← Managed by user/tester
│   ├── api/                              ← API test design .md examples
│   ├── frontend/                         ← Frontend test design .md examples
│   └── mobile/                           ← Mobile test design examples
├── excel_template/
│   ├── template.xlsx                  ← Spreadsheet template
│   └── structure.json                 ← Template structure (generated by extract_structure.py)
├── <tên-test-case>/                   ← Per-feature test folder
│   ├── RSD.pdf                           ← Input: requirement spec
│   ├── PTTK.pdf                          ← Input: technical spec (optional)
│   ├── test-design.md                    ← Output: test design mindmap
│   └── test-cases.json                   ← Output: test cases (from test-case-generator)
├── credentials.json                   ← OAuth Desktop App credentials (DO NOT COMMIT)
└── AGENTS.md                          ← Project-specific rules (user-managed)
```

**Output location:** Save the generated test design `.md` file into the `<tên-test-case>/` folder alongside the input documents. The folder name should match the feature/API being tested.

## Key Format Rules (Quick Reference)

### Critical Rules
- Output starts with `# {API_NAME}` or `# {SCREEN_NAME}` — NO blockquote header, NO `---` horizontal rules
- **ONLY test sections** — NO "thông tin chung", "headers", "request body", "response", "bảng mã lỗi" sections. These are API spec, NOT test design.
- ALL validate responses use Status: 200 (errors in body, NOT 400/422/500)
- SQL uses concrete values, UPPERCASE columns, NO placeholders
- Response body format comes from PTTK (no fixed format)
- Sections NOT numbered — use `## Kiểm tra ...` NOT `## 1. Kiểm tra ...`

### API Test Design — Inline Format Example

This is the REQUIRED output format. AI MUST follow this structure even when catalog/references are unavailable.

```markdown
# API Tên API ở đây

## Kiểm tra các case common

### Method

#### Kiểm tra truyền sai method (GET/PUT/DELETE)
- status: 107
- {
  "message": "Error retrieving AuthorInfo..."
  }

### URL

#### Kiểm tra truyền sai url
- status: 500
- {
  "message": "Access denied"
  }

### Kiểm tra phân quyền

#### Không có quyền
- status: 500
- {
  "message": "Access denied"
  }

#### Được phân quyền
- status: 200

## Kiểm tra validate

### FIELD_NAME: type (Required)

#### Để trống
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Không truyền
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền null
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền FIELD_NAME = 99 ký tự
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền FIELD_NAME = 100 ký tự (maxLength)
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền FIELD_NAME = 101 ký tự (vượt maxLength)
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền FIELD_NAME là ký tự số
#### Truyền FIELD_NAME là chữ(thường/hoa) không dấu
#### Truyền FIELD_NAME là chữ(thường/hoa) có dấu
#### Truyền FIELD_NAME là ký tự đặc biệt cho phép _
#### Truyền FIELD_NAME là ký tự đặc biệt không cho phép
#### Truyền FIELD_NAME là all space
#### Truyền FIELD_NAME có space đầu / cuối
#### Truyền FIELD_NAME là emoji/icons
#### Truyền FIELD_NAME là ký tự Unicode đặc biệt
#### Truyền FIELD_NAME là boolean (true/false)
#### Truyền FIELD_NAME là mảng
#### Truyền FIELD_NAME là object
#### Truyền FIELD_NAME là XSS
#### Truyền FIELD_NAME là SQL INJECTION

## Kiểm tra luồng chính

### Kiểm tra response khi truyền FIELD_NAME tồn tại kết quả
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "errorCode": "0",
        "errorDesc": "",
        "data": [...]
      }
      SQL:
      SELECT * FROM TABLE_NAME
      WHERE FIELD = 'VALUE'
      ORDER BY FIELD ASC;

### Kiểm tra response khi truyền FIELD_NAME không tồn tại kết quả
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "errorCode": "0",
        "errorDesc": "",
        "total": 0,
        "items": []
      }
```

**Format rules summary:**

| Section | Heading level | Response format |
|---------|--------------|-----------------|
| Common (method/url/phân quyền) | `## > ### > ####` | `- status: {code}` + JSON (simple, NO `1\.`) |
| Validate (per field) | `## > ### FIELD: type > ####` | `- 1\. Check api trả về:` + `1\.1. Status:` + `1\.2. Response:` |
| Luồng chính | `## > ###` | Same as validate + SQL |

### Frontend Test Design — Inline Format Example

```markdown
# WEB_BO_Danh mục > Tên màn hình - Test Design

## Kiểm tra giao diện chung

### Kiểm tra điều hướng đến màn hình Tên màn hình
- Điều hướng thành công đến màn hình Tên màn hình

### Kiểm tra bố cục giao diện tổng thể
- + Hiển thị theo đúng figma
  + Màn hình hiển thị đầy đủ các thông tin:
  + Button Thêm mới
  + Dropdown Đối tượng
  + Textbox Tên
  + Button Tìm kiếm
  + Lưới dữ liệu
  + Phân trang

### Kiểm tra hiển thị breadcrumb
- Danh mục/ Tên màn hình

### Kiểm tra hiển thị bố cục layout cân đối
- Hiển thị đúng cỡ chữ, màu chữ, bố cục cân đối

### Kiểm tra phóng to/thu nhỏ
- Màn hình không bị vỡ form

## Kiểm tra phân quyền

### Kiểm tra login user không có quyền
- Không view được màn hình

### Kiểm tra login user có quyền
- User có quyền thao tác chức năng

## Kiểm tra validate

### Kiểm tra dropdown list "Tên field"
- Kiểm tra hiển thị mặc định
    - Luôn hiện và enable
- Kiểm tra giá trị mặc định
    - Mặc định rỗng
- Kiểm tra placeholder
    - Hiển thị placeholder "Chọn giá trị"
- Kiểm tra giá trị hiển thị khi nhấn chọn Dropdown list
    - Hiển thị danh sách các giá trị:
        - Giá trị 1
        - Giá trị 2

#### Icon X
- Kiểm tra hiển thị khi chọn giá trị
    - Hiển thị icon X xóa nhanh
- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh
    - Clear data đã chọn

### Kiểm tra textbox "Tên field"
- Kiểm tra hiển thị mặc định
    - Luôn hiển thị và enable
- Kiểm tra khi nhập kí tự là số
    - Hệ thống cho phép nhập
- Kiểm tra khi nhập 100 kí tự (maxLength)
    - Hệ thống cho phép nhập
- Kiểm tra khi nhập 101 kí tự
    - Hiển thị cảnh báo "Tên field không được vượt quá 100 ký tự"

## Kiểm tra lưới dữ liệu

### Kiểm tra mặc định
- Server trả về danh sách

### Kiểm tra hiển thị sắp xếp các bản ghi trên lưới dữ liệu
- Sắp xếp theo CREATED_TIME DESC
    - SELECT * FROM TABLE_NAME ORDER BY CREATED_TIME DESC

### Kiểm tra cột "Tên cột"
- Hiển thị giá trị do server trả về
    - SELECT COLUMN FROM TABLE_NAME WHERE ID = 10000001

## Kiểm tra "Phân trang"

### Kiểm tra giá trị phân trang mặc định
- Mặc định là 5

### Kiểm tra khi chọn giá trị là 10
- Hiển thị 10 bản ghi / trang

## Kiểm tra chức năng

### Kiểm tra chức năng Tìm kiếm
- Nhập điều kiện tìm kiếm hợp lệ và click Tìm kiếm
    - Hiển thị kết quả khớp với điều kiện

## Kiểm tra timeout

### Kiểm tra khi server không nhận được phản hồi
- Hiển thị popup thông báo lỗi:
    - + Icon x
      + Tiêu đề: "Lỗi"
      + Nội dung: <Mã lỗi> : <Mô tả lỗi Server trả>
      + Button: Đóng
```
