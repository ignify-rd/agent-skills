---
name: generate-test-design-frontend
description: Generate Frontend test design mindmap from RSD/PTTK. For UI screens only. Use when user says "sinh test design frontend", "sinh test design giao diện", "tao mindmap màn hình", or provides RSD/PTTK for a UI screen.
---

# Test Design Generator — Frontend Mode

Generate comprehensive test design documents (.md) for Frontend UI screens from RSD and optional PTTK. Uses a searchable catalog of real test design examples to ensure output matches the correct format per project.

> **Scope**: This skill covers **test design** (mindmap output) for Frontend UI screens only. It does NOT cover API test design or test case generation (JSON/Excel output).

## When to Apply

- User provides RSD/PTTK for a UI screen and asks to generate test design or mindmap
- User says "sinh test design frontend", "sinh test design giao diện", "tạo test design màn hình", "tao mindmap"
- User uploads .pdf/.txt/.md files for Frontend test design / mindmap generation
- Called internally by `test-case-generator-frontend` skill when user provides only RSD+PTTK without a mindmap

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## Đọc file PDF — CHỈ dùng Read tool

**Đọc PDF bằng Read tool. Không có ngoại lệ.**

```
Read file: path/to/document.pdf
Read file: path/to/document.pdf pages=1-10    (file lớn, đọc theo pages)
```

Read tool của AI tools (Claude Code, Cursor, Windsurf, Copilot, Roo Code...) đều hỗ trợ đọc PDF trực tiếp. File lớn thì chia pages (VD: pages 1-10, rồi 11-20...).

**CẤM TUYỆT ĐỐI — vi phạm bất kỳ điều nào = DỪNG LẠI ngay:**
- ❌ KHÔNG tạo file mới: `.py`, `.ps1`, `.sh`, `.js` — dù chỉ 1 file
- ❌ KHÔNG chạy `python`, `python3`, `pip install` để đọc PDF
- ❌ KHÔNG import PyPDF2, pdfplumber, fitz, hoặc bất kỳ thư viện nào
- ❌ KHÔNG parse binary, xref table, byte offsets, content streams
- ❌ KHÔNG tạo find_us05.py, extract_pdf.py, read_pdf.ps1 hay bất kỳ script nào tương tự
- ❌ KHÔNG dùng Bash/PowerShell để đọc PDF

**Nếu Read tool trả về binary/garbled text:** Đọc lại với `pages` parameter (VD: `pages="1-5"`). Nếu vẫn không đọc được → HỎI USER cung cấp nội dung text hoặc copy-paste section cần thiết. **KHÔNG BAO GIỜ tự tạo script.**

## Project AGENTS.md Override

**Scope — what project `AGENTS.md` CAN override:**

| Category | Can override? |
|----------|--------------|
| `testAccount` | Yes |
| testSuiteName convention | Yes |
| Writing style (ngắn/dài, cách viết step) | Yes |
| Section assignment (buttons vào section nào) | Yes |
| Output JSON field names | No |
| Batch strategy (BATCH 1/2/3 split) | No |
| Field type dispatch table | No |
| Importance mapping | No |

**How it works:** If project `AGENTS.md` defines a rule → use that rule. If not → use the skill defaults below. Project AGENTS.md only overrides sections/rules it explicitly defines; everything else falls back to skill defaults.

## Workflow

### Step 0: Validate Project Setup & Load Project Rules

Before starting generation, check project structure and **load project-level rules**:

1. **Check catalog** — look for `catalog/` directory at project root (contains `frontend/` subdirectory)
2. **Check & READ AGENTS.md** — look for `AGENTS.md` at project root (project-level rules)

**If catalog directory does not exist:**
- Ask user: "Chưa có thư mục `catalog/`. Bạn đã chạy `test-genie init` chưa?"
- If not → guide user to run `test-genie init` to set up project structure

**If AGENTS.md exists at project root:**
- **READ the entire file content** — extract ALL sections and rules defined by the project
- Store these rules as `projectRules` — they will be applied throughout the entire generation workflow when explicitly defined
- Any rule in project AGENTS.md **overrides** the corresponding rule in skill-level AGENTS.md and references
- Sections in project AGENTS.md that don't exist in defaults are **ADDED** (not ignored)
- Pay special attention to `## Project-Specific Rules` — these are custom rules that MUST be followed in every step

**If AGENTS.md does not exist at project root:**
- Use skill-level `AGENTS.md` (default rules)
- Inform user: "Project chưa có AGENTS.md. Đang dùng rules mặc định."

**If catalog exists but has no examples (empty frontend/):**
- Warn user: "Catalog chưa có examples. Output có thể không chính xác format. Bạn có muốn thêm examples trước không?"
- Proceed with skill references as fallback

**⚠️ CRITICAL: Project AGENTS.md rules take precedence when explicitly defined.** Every subsequent step must check `projectRules` and apply them.

### Step 0b: Resolve Input Documents

**If user provides a feature folder name** (e.g., `/generate-test-design-frontend feature-1` or `sinh test design frontend cho feature-1`):
1. Look inside `<feature-name>/` folder for input documents automatically:
   - Scan for document files: `.pdf`, `.docx`, `.doc`, `.md`, `.txt` — identify RSD and PTTK by filename
2. **DO NOT ask** the user for file paths — use whatever documents are found in the folder
3. **If folder is empty** → scan toàn bộ project root cho document files liên quan đến feature name
4. If truly no documents found → inform user: "Không tìm thấy tài liệu RSD/PTTK. Hãy cung cấp đường dẫn hoặc upload file."
5. Save output as `<feature-name>/test-design-frontend.md`

### Step 1: Mode Detection (Frontend Mode Only)

This skill is **Frontend-only**. The input RSD must describe a UI screen.

**Heuristic-first detection (rule-based, no LLM needed):**

| Heuristic | Confidence |
|-----------|------------|
| Document contains `màn hình`, `screen`, `giao diện`, `button`, `textbox`, `combobox`, `lưới` | High |
| Title contains `Danh sách`, `Chi tiết`, `Thêm mới`, `Cập nhật` + UI element names | High |
| Document describes UI layout, form fields, grid display | High |

**Decision logic:**
1. If heuristic returns **High confidence** → proceed as Frontend
2. If document appears to be API/RSD → inform user: "Tài liệu này là API, không phải Frontend. Sử dụng skill `generate-test-design-api` thay thế."
3. If **no heuristic matches** → ask user for clarification

### Step 2: Load Rules & References

**Step 2a: Apply project AGENTS.md rules (loaded in Step 0)**

Before loading any references, review `projectRules` from Step 0. Project rules affect:
- **Which sections to generate** — project may add/remove/rename sections
- **How to generate each section** — project may override field template dispatch, screen type rules, format rules
- **Quality/style constraints** — project may define custom forbidden phrases, naming conventions, writing style
- **Test case granularity** — project may require splitting cases differently (e.g., "tách riêng từng field", "buttons vào phần chức năng")
- **Image analysis behavior** — project may require analyzing images before reading RSD
- **Custom field types** — project may define field types not in default templates

All rules from project AGENTS.md apply as overrides throughout the remaining steps.

**Step 2b: Load skill references (Frontend mode)**

#### Resolve SKILL_SCRIPTS path

Scripts are installed alongside this SKILL.md file in a `scripts/` subdirectory. Try these methods in order:

**Method 1 — Recursive find from project root:**
```bash
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/test-design-generator-frontend/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
echo "SKILL_SCRIPTS=$SKILL_SCRIPTS"
```

**Method 2 — Direct path check (if Method 1 returns empty):**
```bash
for d in \
  ".claude/skills/test-design-generator-frontend/scripts" \
  ".cursor/skills/test-design-generator-frontend/scripts" \
  ".windsurf/skills/test-design-generator-frontend/scripts" \
  ".roo/skills/test-design-generator-frontend/scripts" \
  ".kiro/skills/test-design-generator-frontend/scripts"; do
  [ -f "$d/search.py" ] && SKILL_SCRIPTS="$d" && break
done
echo "SKILL_SCRIPTS=$SKILL_SCRIPTS"
```

**Method 3 — Global npm (if Method 2 returns empty):**
```bash
npm_root=$(npm root -g 2>/dev/null)
[ -n "$npm_root" ] && [ -f "$npm_root/test-genie/test-design-generator-frontend/scripts/search.py" ] && \
  SKILL_SCRIPTS="$npm_root/test-genie/test-design-generator-frontend/scripts"
```

**Method 4 — CRITICAL FALLBACK (if all above fail): Read reference files directly**

If `SKILL_SCRIPTS` is still empty after all methods, **DO NOT skip loading references**. Instead, read the reference files directly:

```
READ: <skills-dir>/test-design-generator-frontend/references/frontend-test-design.md
READ: <skills-dir>/test-design-generator-frontend/references/field-templates.md
READ: <skills-dir>/test-design-generator-frontend/references/priority-rules.md
READ: <skills-dir>/test-design-generator-frontend/references/quality-rules.md
READ: <skills-dir>/test-design-generator-frontend/references/output-examples.md
```

Where `<skills-dir>` is wherever the `.claude/`, `.cursor/`, etc. directory is found. Try common paths:
- `.claude/skills/`
- `.cursor/skills/`
- `.windsurf/skills/`

**⚠️ NEVER proceed without loading references.** The format templates in `frontend-test-design.md` and `field-templates.md` are mandatory.

**Note:** `search.py` auto-detects the project root by looking for `catalog/` or `AGENTS.md`. You can also pass `--project-root /path/to/project` explicitly.

#### Load Frontend references

**Always load first (Frontend mode):**
```bash
python $SKILL_SCRIPTS/search.py --ref priority-rules
python $SKILL_SCRIPTS/search.py --ref quality-rules
python $SKILL_SCRIPTS/search.py --ref frontend-test-design
python $SKILL_SCRIPTS/search.py --ref field-templates
```

#### Search examples & utilities

```bash
# Search Frontend examples (searches catalog/frontend/ in project root)
python $SKILL_SCRIPTS/search.py "danh sach list screen" --domain frontend

# Search format rules (skill-bundled, not in project catalog)
python $SKILL_SCRIPTS/search.py "common section status" --domain rules

# List all available references
python $SKILL_SCRIPTS/search.py --list-refs

# List all available examples
python $SKILL_SCRIPTS/search.py --list

# Read full content of top match
python $SKILL_SCRIPTS/search.py "export excel" --domain frontend --full
```

### Step 3: Read the Top-Matching Example

After search returns results, **read the full example file** to understand the exact format:

```bash
# search.py returns the full_path — use view_file on it
```

### Step 4: Extract Data from RSD & PTTK

Priority rules: see `AGENTS.md` or `--ref priority-rules`. When PTTK is available, IGNORE field definitions, request body, and response body in RSD.

### Step 4: Extract Data from RSD, PTTK & Images

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
- screenType ambiguous (has both grid and form elements) → ask: "Màn hình này vừa có lưới vừa có form. screenType là LIST hay FORM?"
- No permissions section in RSD → ask: "RSD không mô tả phân quyền. Bỏ qua section phân quyền hay tạo mặc định?"

**Conflicts between documents (MUST ask):**
- PTTK field name differs from RSD field name → ask: "PTTK gọi là `{pttk_name}` nhưng RSD gọi là `{rsd_name}`. Dùng tên nào?"
- PTTK says required but RSD says optional (or vice versa) → ask: "Field `{name}`: PTTK = required, RSD = optional. Theo tài liệu nào?"

**Suspicious/unclear content (SHOULD ask):**
- Business logic description is vague or uses ambiguous words ("có thể", "tùy trường hợp") → ask: "Logic `{description}` không rõ ràng. Cụ thể điều kiện là gì?"
- Image shows field/button not in RSD → ask: "Hình ảnh có `{element}` nhưng RSD không đề cập. Thêm vào test design không?"

**DO NOT ask if:**
- Information can be reasonably inferred
- Priority rules already define the answer
- It's a formatting/style question covered by references

### Step 4c: Business Logic Inventory (Frontend Mode)

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

### Step 4d: Inventory Verification Gate

**Sau khi hoàn thành Step 4c, PHẢI báo cáo cho user (bắt buộc, không được skip):**

```
📋 Business Logic Inventory đã extract:
- Fields:             {N} fields cần generate validate cases (list tên + type)
- Business rules:     {N} (list: BR1 [validate], BR2 [function], ...)
- Error messages:     {N} messages cần cover (list trigger)
- Enable/disable:     {N} rules (list field + condition)
- Auto-fill:          {N} cascading rules
- Permissions:        {N} roles
```

**Nếu bất kỳ category nào = 0 VÀ tài liệu có khả năng chứa thông tin đó → HỎI USER xác nhận trước khi tiếp tục:**
> "Không tìm thấy {category} trong tài liệu. Tài liệu có đề cập không? (có thể tôi đọc bỏ sót phần nào đó)"

### Step 5: Generate Test Design Sections (Frontend Mode)

Generate the test design following the rules loaded via `--ref` and the format of the catalog examples.

**⚠️ BEFORE generating any section, review `projectRules` from Step 0.** Project AGENTS.md rules MUST be applied throughout generation:
- If project defines custom section structure (e.g., "buttons vào phần chức năng thay vì validate") → follow that
- If project defines writing style (e.g., "viết ngắn gọn", "tách riêng từng case") → follow that
- If project defines image analysis behavior (e.g., "phân tích hình ảnh trước") → follow that
- If project defines custom field handling not in default templates → follow that
- If project defines any `## Project-Specific Rules` → apply ALL of them to every section

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

**Post-section checkpoint — Validate (Frontend):**
- TỪNG field trong `inventory.fieldConstraints[]` → có bullet trong ## Kiểm tra validate?
- TỪNG combobox → có API timeout/error/rỗng cases?
- Item nào thiếu → THÊM bullet `### [SỬA]` ngay.

**For DETAIL screens:** Do NOT use field templates. Use `generateDetailDataSection()` — test data display, null/empty handling, SQL queries per field.

**Grid section (LIST only):** Default state, sort order, each column with SQL, scroll behavior (pinned columns), data verification.

**Pagination section (hardcoded):** Values, default, per-value test, page navigation. Only generate when pagination exists.

**Function section (LLM-generated per screenType) — PHẢI inject inventory từ Step 4c vào generation:**

**⚠️ Section này phải cover TOÀN BỘ business logic. KHÔNG được sinh function section mà không có inventory items.**

```
Sinh ## Kiểm tra chức năng. BẮT BUỘC cover đủ các items sau từ inventory:

Business rules [function]: {list inventory.businessRules[section="function"]}
Error messages [function]:  {list inventory.errorMessages[section="function"] với exact message}
Enable/disable rules:       {list inventory.enableDisableRules[] — mỗi rule cần test BOTH states}
Auto-fill rules:            {list inventory.autoFillRules[]}
Status transitions:         {list inventory.statusTransitions[] — valid + invalid transition}
Permissions:                {list inventory.permissions[] — mỗi role cần test}

KHÔNG bỏ sót bất kỳ item nào.
```

- **LIST:** Search per field (exists/not exists/partial), combined search, clear filter, add new button
- **FORM/POPUP:**
  - Save success (form hợp lệ) → expected: thông báo thành công
  - Save fail (form có lỗi) → expected: **exact error message từ `errorMessages[]` trong inventory**
  - Từng `enableDisableRules[]` → test case state enable VÀ state disable
  - Từng `autoFillRules[]` → test case verify auto-fill behavior
  - Từng `businessRules[section="function"]` → test case cho mỗi condition
  - Cancel, back navigation
- **DETAIL:** Button visibility by status/permission, click actions, navigation, status transitions
- **All screen types:**
  - Từng `statusTransitions[]` → test valid transition + invalid transition (từ sai state)
  - Từng `permissions[]` → test action visibility/accessibility per role
  - Any button-related test cases belong in function section (not validate) — buttons test logic flow, not input validation

**⚠️ Project AGENTS.md override:** If project AGENTS.md defines additional function section rules (e.g., "buttons vào phần chức năng", custom section assignments), apply them here.

**Post-section checkpoint — Function (Frontend):**
- TỪNG `inventory.businessRules[section="function"]` → có bullet?
- TỪNG `inventory.errorMessages[section="function"]` → có bullet với exact message?
- TỪNG `inventory.enableDisableRules[]` → có bullet state enable VÀ disable?
- TỪNG `inventory.autoFillRules[]` → có bullet verify auto-fill?
- TỪNG `inventory.permissions[]` → có bullet cho từng role?
- Item nào thiếu → THÊM bullet `### [SỬA]` ngay.

**Verify — coverage summary (Frontend mode):**
Kiểm tra nhanh đã cover đủ:
- [ ] TỪNG field → có validate test cases
- [ ] TỪNG `inventory.businessRules[]` → có bullet đúng section
- [ ] TỪNG `inventory.errorMessages[]` → có bullet với exact message
- [ ] TỪNG `inventory.enableDisableRules[]` → có bullet enable VÀ disable
- [ ] TỪNG `inventory.autoFillRules[]` → có bullet verify auto-fill
- [ ] TỪNG `inventory.permissions[]` → có bullet cho từng role
- [ ] Buttons trong ## Kiểm tra chức năng, KHÔNG trong validate

Item nào thiếu → THÊM bullet `### [SỬA]`. Wrong expected → `### [SỬA]` and replace.

**⚠️ PHẢI hiển thị coverage summary cho user sau khi verify (Frontend mode):**
```
📊 Coverage Report (Frontend):
✓ Fields covered:        {N}/{N} fields có validate test cases
✓ Business rules:        {N}/{N} covered ({validate: N, function: N})
✓ Error messages:         {N}/{N} covered với exact messages
✓ Enable/disable rules:  {N}/{N} covered
✓ Auto-fill rules:       {N}/{N} covered
✓ Permissions:           {N}/{N} roles covered
[SỬA]: {N} bullets thêm/sửa
```

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
python <skills-root>/test-design-generator-frontend/scripts/search.py --ref quality-rules
```

Checklist:
- 100% Vietnamese, keep field/button names exactly as in RSD/PTTK
- No placeholders — use concrete sample values
- 1 test = 1 check (atomic)
- Forbidden words: "và/hoặc", "hoặc", "có thể", "nên", "ví dụ:", "[placeholder]"
- Output starts with `# {SCREEN_NAME}` — NO blockquote header, NO `---` horizontal rules
- **Project AGENTS.md quality rules**: If project defines additional quality constraints (e.g., "viết ngắn gọn", custom forbidden phrases, writing style) → apply them

## Catalog Management

### Add Examples to Catalog

To add new reference examples:
1. Save the test design output as a `.md` file
2. Place it in `catalog/frontend/` at your project root
3. The search engine will automatically index new files

### List Available Examples

```bash
python <skills-root>/test-design-generator-frontend/scripts/search.py --list
```

## Project Structure

After running `test-genie init`, your project has this structure:

```
<project-root>/
├── node_modules/test-genie/           ← Skills live here (managed by npm)
│   ├── test-design-generator-frontend/
│   │   ├── SKILL.md                      ← Workflow instructions (this file)
│   │   ├── AGENTS.md                     ← Skill-level default rules
│   │   ├── references/                   ← Detailed rules (dev-managed)
│   │   │   ├── frontend-test-design.md
│   │   │   ├── field-templates.md
│   │   │   ├── priority-rules.md
│   │   │   ├── quality-rules.md
│   │   │   └── output-examples.md
│   │   └── scripts/
│   │       └── search.py                 ← Catalog search (auto-detects project root)
│   └── test-case-generator-frontend/
│       └── ...
├── .claude/commands/                  ← Claude slash commands (auto-generated)
│   └── generate-test-design-frontend.md
├── catalog/                           ← Managed by user/tester
│   ├── frontend/                         ← Frontend test design .md examples
│   └── mobile/                           ← Mobile test design examples
├── excel_template/
│   ├── template.xlsx                  ← Spreadsheet template
│   └── structure.json                 ← Template structure
├── <tên-test-case>/                   ← Per-feature test folder
│   ├── RSD.pdf                           ← Input: requirement spec
│   ├── PTTK.pdf                          ← Input: technical spec (optional)
│   └── test-design-frontend.md          ← Output: test design mindmap
├── credentials.json                   ← OAuth credentials (DO NOT COMMIT)
└── AGENTS.md                          ← Project-specific rules (user-managed)
```

**Output location:** Save the generated test design `.md` file into the `<tên-test-case>/` folder alongside the input documents. The folder name should match the feature/screen being tested.

## Key Format Rules (Quick Reference)

### Critical Rules
- Output starts with `# {SCREEN_NAME}` — NO blockquote header, NO `---` horizontal rules
- **ONLY test sections** — NO "thông tin chung", "headers", "request body", "response" sections
- Sections NOT numbered — use `## Kiểm tra ...` NOT `## 1. Kiểm tra ...`

### Frontend Screen Type Rules

| Screen Type | Has validate? | Has grid? | Has pagination? | Function section |
|-------------|--------------|-----------|-----------------|------------------|
| LIST | Yes | Yes | Yes | Search per field, combined, clear filter |
| FORM/POPUP | Yes | No | No | Save success/fail, field interactions, cancel |
| DETAIL | No (→ "dữ liệu hiển thị") | No | No | Button visibility by status/permission |

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
