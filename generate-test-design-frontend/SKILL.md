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

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## Đọc file PDF — CHỈ dùng Read tool

Đọc PDF bằng Read tool (`pages` parameter cho file lớn). Nếu Read tool trả về binary/garbled → đọc lại với `pages`. Nếu vẫn fail → hỏi user copy-paste.

**CẤM TUYỆT ĐỐI** tạo script (.py/.ps1/.sh/.js), chạy python/pip, import thư viện PDF, parse binary.

## Project AGENTS.md Override

**Scope — what project `AGENTS.md` CAN override:**

| Category | Can override? |
|----------|--------------|
| Chat input / user request | **Always — HIGHEST PRIORITY** |
| `testAccount` | Yes |
| testSuiteName convention | Yes |
| Writing style (ngắn/dài, cách viết step) | Yes |
| Section assignment (buttons vào section nào) | Yes |
| Output JSON field names | No |
| Batch strategy (BATCH 1/2/3 split) | No |
| Field type dispatch table | No |
| Importance mapping | No |

**How it works:** Chat input from the user → Project `AGENTS.md` → Skill defaults. User says "viết ngắn gọn" or "chỉ generate test case cho chức năng ..." → do it, even if it contradicts AGENTS.md or skill defaults.

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

### Step 0b: Validate Required Inputs

**⚠️ STOP — Do NOT read any files or proceed until the user explicitly provides input file paths.**

Required inputs:
- **RSD file path** — required
- **PTTK file path** — optional
- **Output folder** — required (e.g. `feature-1/`), output will be saved as `<output-folder>/test-design-frontend.md`

**NEVER:**
- Scan folders looking for files
- Guess file paths from feature names or conversation context
- Read any file not explicitly provided by the user

**If any required input is missing → STOP immediately and ask:**
> "Vui lòng cung cấp:
> 1. Đường dẫn file RSD (bắt buộc)
> 2. Đường dẫn file PTTK (nếu có)
> 3. Thư mục output (bắt buộc, ví dụ: `feature-1/`)"

Do not proceed until the user provides these.

**⛔ Extract & enforce user scope:**

Trước khi làm bất cứ điều gì, kiểm tra user request có chỉ định phạm vi không:
- "chỉ gen US05.2", "chỉ gen phần validate", "chỉ gen chức năng Thêm mới" → lưu vào `userScope`
- Nếu có `userScope` → **chỉ generate đúng phần đó, dừng lại và không gen thêm bất cứ section/feature nào khác**
- Nếu không có `userScope` → generate toàn bộ màn hình

Confirm scope với user trước khi bắt đầu nếu request mơ hồ:
> "Bạn muốn gen test design cho toàn bộ màn hình hay chỉ phần `{phần cụ thể}`?"

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

```bash
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/generate-test-design-frontend/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
# Fallback: check .claude/skills, .cursor/skills, .windsurf/skills, .roo/skills, .kiro/skills, or global npm
```

If all fail → Read reference files directly from `<skills-dir>/generate-test-design-frontend/references/`. **⚠️ NEVER proceed without loading references.**

#### Load Frontend references

**Always load first (Frontend mode):**
```bash
python $SKILL_SCRIPTS/search.py --ref priority-rules
python $SKILL_SCRIPTS/search.py --ref quality-rules
python $SKILL_SCRIPTS/search.py --ref frontend-test-design
# ⚠️ field-templates.md: KHÔNG load toàn bộ ở đây — lazy-load per field type trong Step 5
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

### Step 3: Read the Top-1 Matching Example

**Criteria chọn catalog example (theo thứ tự ưu tiên):**
1. **Keyword match chính xác nhất** — tên feature/API/screen trùng với request
2. **Cùng project** — ưu tiên examples từ project hiện tại (catalog trong project)
3. **Cùng domain** — ví dụ: LIST screen → ưu tiên LIST, FORM → ưu tiên FORM
4. **Gần đây nhất** — nếu nhiều candidates cùng quality

**Search strategy:**
```bash
# Tìm keyword chính xác trước
python $SKILL_SCRIPTS/search.py "{feature_keyword}" --domain frontend --full --top 1

# Nếu top 1 không phù hợp (domain khác, quality thấp) → thử top 2
python $SKILL_SCRIPTS/search.py "{feature_keyword}" --domain frontend --full --top 2
```

**Fallback:** Nếu top 1 và top 2 đều không phù hợp → thông báo user và dùng format mặc định từ references.

**⚠️ Catalog là nguồn WORDING & FORMAT cao nhất — cao hơn cả references:**
- Output PHẢI giống catalog về: cách đặt tên bullet, cách viết expected result, density của cases, structure của heading
- References cung cấp **danh sách cases cần gen** — KHÔNG copy wording từ references nếu catalog có cách viết khác
- **Nếu không tìm thấy catalog phù hợp** → thông báo user rồi dùng format mặc định từ references

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
7. **⛔ Bắt buộc scan toàn bộ điều kiện của Button Lưu/Submit — KHÔNG được bỏ sót:**
   Đọc kỹ phần mô tả luồng Save trong RSD, tìm TẤT CẢ các trường hợp đặc biệt:
   - **Version conflict / phiên bản cũ:** "Nếu phiên bản không phải mới nhất", "version không khớp" → extract message + behavior
   - **Concurrent lock / đang chỉnh sửa bởi người khác:** "SLA đang được chỉnh sửa", "record bị lock" → extract message + behavior
   - **Trạng thái thay đổi khi đang edit:** "trạng thái giao dịch đã thay đổi", "status changed" → extract message + behavior
   - **Trạng thái không hợp lệ:** "trạng thái không hợp lệ để thực hiện" → extract message + behavior
   - **Lưu thất bại (hệ thống):** "không thể lưu dữ liệu", "system error when saving" → extract message + behavior

   Mỗi điều kiện đặc biệt tìm được → thêm vào `inventory.businessRules[section="function"]` với exact message.
   **Nếu RSD có bảng mô tả luồng Save với nhiều dòng điều kiện → đọc TỪNG DÒNG, không đọc lướt.**

**⚠️ Với mỗi field, phân loại `displayBehavior` dựa trên TEXT CHÍNH XÁC trong RSD — KHÔNG suy diễn:**

| displayBehavior | Điều kiện xác định | Cases cần gen |
|---|---|---|
| `always` | RSD không đề cập điều kiện hiển thị, hoặc ghi rõ "luôn hiển thị" | **Chỉ validate cases** (maxLength, required, format...) |
| `conditional` | RSD ghi rõ điều kiện: "hiển thị khi...", "ẩn khi...", "enable khi...", "disable khi..." | Validate cases (khi đang enable) **+ enable/disable cases** |

**Quy tắc phân loại — tránh nhầm lẫn:**
- Không có câu nào trong RSD mô tả điều kiện hiển thị/ẩn/enable/disable của field → `always`
- RSD chỉ mô tả validate rule (VD: "bắt buộc", "tối đa 100 ký tự") → KHÔNG phải điều kiện hiển thị → `always`
- `always` + `conditional` đều phải có validate cases — field `always` KHÔNG được bỏ validate cases

**⛔ Condition của block KHÔNG truyền — không xuống field bên trong, không sang field ở block khác:**

Câu "Nếu X thì hiển thị Khối A gồm: [field1, field2, field3]" chỉ làm **Khối A** = `conditional`.
→ field1, field2, field3 bên trong Khối A = `always` (không có điều kiện riêng)
→ **Mọi field ở block khác trên cùng màn hình = `always`** — dù RSD có câu điều kiện về Khối A

SAI — nhầm lan điều kiện của Khối Luồng trình sang field ở Khối khác:
```
RSD: "Nếu Loại nghiệp vụ = Cấp tín dụng thì hiển thị Khối Luồng trình gồm: Luồng phê duyệt, Kỳ hạn, Phương thức"

Datepicker Ngày hết hiệu lực (thuộc Khối Thông tin chung)
→ displayBehavior: conditional, condition: "Loại nghiệp vụ = Cấp tín dụng"  ← SAI
```

ĐÚNG:
```
Khối Luồng trình              → displayBehavior: conditional, condition: "Loại nghiệp vụ = Cấp tín dụng"
Field Luồng phê duyệt (trong Khối Luồng trình) → displayBehavior: always
Field Kỳ hạn (trong Khối Luồng trình)          → displayBehavior: always
Datepicker Ngày hết hiệu lực (Khối Thông tin chung, không trong danh sách) → displayBehavior: always
```

Ví dụ khi cả block và field đều có điều kiện riêng:
- RSD ghi "Khối Luồng trình ẩn khi ..." VÀ "Field Kỳ hạn ẩn khi Loại kỳ = Ngắn hạn"
- Khối Luồng trình → `conditional`, source trỏ đoạn về Khối
- Field Kỳ hạn → `conditional`, source trỏ đoạn về Field Kỳ hạn (KHÁC đoạn về Khối)

Condition của field phải được quote từ đúng đoạn RSD nói về FIELD ĐÓ, không phải đoạn nói về block chứa nó.

**Sau Phase 1, với mỗi field in ra:**
```
- Tên SLA:          type=textbox,  displayBehavior=always     → source: "không có điều kiện"
- Loại nghiệp vụ:   type=dropdown, displayBehavior=always     → source: "không có điều kiện"
- Ngày hết hiệu lực: type=datepicker, displayBehavior=always  → source: "không có điều kiện riêng — Khối X có điều kiện nhưng field này không có"
- Kỳ hạn:           type=dropdown, displayBehavior=conditional → source: RSD tr.5 "Hiển thị khi Loại NV = X"
```

**Phase 2: PTTK → field definitions (if available)**
1. Find the exact screen/API in PTTK by name or endpoint
2. **Extract ALL fields — không được bỏ sót bất kỳ field nào:**
   - Duyệt TỪNG dòng trong PTTK, liệt kê mọi field theo thứ tự xuất hiện
   - Xác định loại type chính xác: `textbox`, `dropdown (values[])`, `dropdown (apiEndpoint)`, `number`, `datepicker`, `toggle`, `checkbox`, `button`, `file`, `textarea`...
   - **"Dropdown list" hoặc "Danh sách"** trong RSD/PTTK = `dropdown (values[])` nếu có danh sách cố định, = `dropdown (apiEndpoint)` nếu load từ API
   - Extract: field names, types, API endpoints, DB mappings, enum values, maxLength, format constraints
3. **REPLACE** all field definitions from RSD with PTTK values (PTTK wins completely)
4. **If no PTTK** → keep field definitions from RSD
5. **Sau Phase 2: in ra danh sách tất cả fields đã extract** (tên + type) để verify trước khi tiếp tục

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

**⚠️ Frontend CŨNG PHẢI extract business logic từ RSD — KHÔNG được bỏ qua.**

**Khởi tạo file:**
```bash
python $SKILL_SCRIPTS/inventory.py init \
  --file <output-folder>/inventory.json \
  --name "<Screen name>" \
  --screen-type "FORM|LIST"
```

**Với mỗi item extract được, gọi ngay lệnh add (KHÔNG tích lũy rồi write một lần):**

```bash
# Mỗi field constraint:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category fieldConstraints \
  --data '{"field":"Tên cấu hình SLA","type":"textbox","maxLength":100,"required":true,"unique":true,"source":"RSD tr.X"}'

# Mỗi business rule:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category businessRules \
  --data '{"id":"BR1","type":"validation","condition":"...","expected":"...","section":"validate","source":"RSD tr.X"}'

# Mỗi error message:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category errorMessages \
  --data '{"trigger":"Bỏ trống field bắt buộc","message":"exact message từ RSD","section":"validate","source":"RSD tr.X"}'

# Mỗi enable/disable rule:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category enableDisableRules \
  --data '{"target":"Button Lưu","targetType":"button","condition":"Form chưa đủ required","state":"disable","section":"function","source":"RSD tr.X"}'

# Mỗi auto-fill rule:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category autoFillRules \
  --data '{"trigger":"Chọn Dropdown X","target":"Field Y","action":"auto-fill giá trị tương ứng","source":"RSD tr.X"}'

# Mỗi status transition:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category statusTransitions \
  --data '{"from":"Draft","to":"Active","trigger":"Click Phê duyệt","source":"RSD tr.X"}'

# Mỗi permission:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category permissions \
  --data '{"action":"Tạo mới","role":"Maker","source":"RSD tr.X"}'
```

**Extraction rules (Frontend):**
- `fieldConstraints[]`: lấy từ RSD/PTTK — **maxLength, minLength, required, unique, format** phải chính xác từ tài liệu, KHÔNG đoán từ ảnh
- `businessRules[]`: đọc **toàn bộ mô tả nghiệp vụ** trong RSD — mỗi condition/if-else/validation rule = 1 entry
- `errorMessages[]`: messages thường nằm trong **bảng mô tả luồng xử lý** của RSD/PTTK — PHẢI đọc toàn bộ các bảng này, không bỏ sót

  **Cách nhận diện bảng chứa message:**
  - Bảng có cột dạng: `Thao tác / Điều kiện / Kết quả`, `Hành động / Xử lý / Thông báo`, `Trường hợp / Message`, `Nếu... thì...`
  - Thường xuất hiện trong mục "Mô tả luồng xử lý", "Xử lý nghiệp vụ", "Validate", "Điều kiện xử lý"
  - Mỗi row trong bảng = 1 entry trong `errorMessages[]`

  **Extraction rule:**
  - **Nếu có trong bảng** → copy **exact** nội dung cột message/thông báo, lưu vào `message` field
  - **Nếu không có trong tài liệu** → lưu `message: null`, khi gen expected result dùng mô tả hành vi (không đặt trong `""`, không bịa nội dung)

  **Ví dụ đúng khi gen expected result:**
  - RSD bảng có dòng: "Bỏ trống Tên SLA / Tên cấu hình SLA không được để trống" → `message="Tên cấu hình SLA không được để trống"` → expected: `Hiển thị lỗi: "Tên cấu hình SLA không được để trống"`
  - RSD không đề cập message khi lưu thất bại → `message=null` → expected: `Hệ thống không lưu dữ liệu` (mô tả hành vi, không có `""` quanh message)
- `enableDisableRules[]`: lấy từ RSD — **bắt buộc gán `targetType` và `section` cho từng rule:**

  | targetType | Đối tượng | section | Generate vào đâu |
  |---|---|---|---|
  | `block` | Khối, Nhóm, Section ẩn/hiện | `ui_common` | ## Kiểm tra giao diện chung |
  | `field` | Field đơn lẻ enable/disable | `validate` | #### field tương ứng trong validate |
  | `button` | Button enable/disable | `function` | ## Kiểm tra chức năng |

  **Ví dụ routing đúng:**
  - RSD: "Khối Luồng trình ẩn khi Loại nghiệp vụ ≠ Cấp tín dụng" → `targetType=block`, `section=ui_common` → gen `### Kiểm tra giao diện khi Loại nghiệp vụ = "Cấp tín dụng"` trong "Kiểm tra giao diện chung"
  - RSD: "Field Mã SLA disable khi trạng thái = Đã phê duyệt" → `targetType=field`, `section=validate` → gen case disable trong `#### Kiểm tra textbox "Mã SLA"`
  - RSD: "Button Phê duyệt ẩn khi user không có quyền Checker" → `targetType=button`, `section=function` → gen case trong "Kiểm tra chức năng"
- `autoFillRules[]`: lấy từ RSD mô tả auto-fill, cascading dependencies
- `statusTransitions[]`: lấy từ RSD flow diagram hoặc mô tả luồng
- `permissions[]`: lấy từ RSD phân quyền

**Dùng inventory này khi sinh từng section (Frontend):**
- `fieldConstraints[]` → mỗi field PHẢI dùng maxLength/minLength/required/unique từ inventory, KHÔNG từ ảnh
- `businessRules[section="validate"]` → phải có bullet trong ## Kiểm tra validate
- `businessRules[section="function"]` → phải có bullet trong ## Kiểm tra chức năng
- `errorMessages[]` → mỗi error message phải có ≥1 bullet test case
- `enableDisableRules[section="ui_common"]` → generate vào ## Kiểm tra giao diện chung (1 `###` case per condition)
- `enableDisableRules[section="validate"]` → generate vào `####` field tương ứng trong validate
- `enableDisableRules[section="function"]` → generate vào ## Kiểm tra chức năng
- `autoFillRules[]` → phải có test case cho từng auto-fill behavior
- `permissions[]` → mỗi role phải có test case trong ## Kiểm tra phân quyền

**⚠️ Inventory = Mandatory Checklist — mỗi item PHẢI có trong output:**

| Inventory Item | Required Output | Section |
|---|---|---|
| Mỗi fieldConstraint | validate cases theo template | ## Kiểm tra validate |
| Mỗi businessRule[validate] | ≥1 bullet | ## Kiểm tra validate |
| Mỗi businessRule[function] | ≥1 bullet | ## Kiểm tra chức năng |
| Mỗi errorMessage | bullet với exact message | Section tương ứng |
| Mỗi enableDisableRule | bullet enable + disable | Section theo targetType |
| Mỗi autoFillRule | bullet verify behavior | ## Kiểm tra chức năng |
| Mỗi permission | bullet per role | ## Kiểm tra phân quyền |

**Kết thúc generation: tất cả items phải ☑. Chưa ☑ = THÊM bullet.**

### Step 4d: Inventory Verification Gate

**Sau khi hoàn thành Step 4c, chạy summary và báo cáo cho user:**

```bash
python $SKILL_SCRIPTS/inventory.py summary --file <output-folder>/inventory.json
```

**⚠️ displayBehavior checklist bắt buộc:**
- Field nào = `always` → verify: KHÔNG gen enable/disable cases, CHỈ validate cases
- Field nào = `conditional` → verify: CÓ validate cases (khi enable) + CÓ enable/disable cases
- Điều kiện của block KHÔNG lan sang field ở block khác

**Nếu bất kỳ category nào = 0 VÀ tài liệu có khả năng chứa thông tin đó → HỎI USER xác nhận:**
> "Không tìm thấy {category} trong tài liệu. Tài liệu có đề cập không?"

### Step 5: Generate Test Design Sections (Frontend Mode)

**⛔ TRƯỚC KHI generate bất cứ section nào:**
1. Kiểm tra `userScope` (từ Step 0b) — nếu có scope → chỉ gen sections trong scope, skip toàn bộ phần khác
2. Xem lại catalog example từ Step 3 — wording và format của output PHẢI theo catalog
3. Review `projectRules` (từ Step 0) — apply tất cả project-specific rules

Generate the test design following the format of the catalog examples (highest priority) and rules loaded via `--ref` (for case completeness).

**⚠️ BEFORE generating any section, review `projectRules` from Step 0.** Project AGENTS.md rules MUST be applied throughout generation:
- If project defines custom section structure (e.g., "buttons vào phần chức năng thay vì validate") → follow that
- If project defines writing style (e.g., "viết ngắn gọn", "tách riêng từng case") → follow that
- If project defines image analysis behavior (e.g., "phân tích hình ảnh trước") → follow that
- If project defines custom field handling not in default templates → follow that
- If project defines any `## Project-Specific Rules` → apply ALL of them to every section

#### Frontend Mode — Generation

**Common UI section — đọc toàn bộ spec, sinh đủ các trạng thái UI:**

1. **Trạng thái mặc định** — "Kiểm tra giao diện khi mới vào màn hình": liệt kê toàn bộ nhóm/field/button mặc định hiển thị hoặc ẩn
2. **Mỗi điều kiện làm UI thay đổi** — 1 case riêng: đọc từ bảng luồng xử lý, mục enable/disable, hiển thị có điều kiện trong spec
3. **Mỗi popup/modal** — 1 case riêng: liệt kê field/button bên trong

**⚠️ Indentation — dùng `  +` (2 spaces + plus) để giữ nội dung trong cùng 1 bullet:**
```
ĐÚNG:
- Màn hình hiển thị:
  + Nhóm Thông tin chung: Tên SLA, Loại nghiệp vụ
  + Nhóm Luồng trình: ẩn
  + Button: Lưu, Đẩy duyệt

ĐÚNG:
- Màn hình hiển thị:
  + Khối Thông tin chính: Tên SLA, Loại nghiệp vụ, Ngày hiệu lực
  + Khối Luồng trình: ẩn
  + Khối Ghi chú: ẩn
  + Button: Lưu, Đẩy duyệt, Thoát
```

**Permission section (hardcoded):** No permission / has permission — 2 test cases.

**Validate section (per-field templates):** **QUAN TRỌNG: Phải output ĐẦY ĐỦ TẤT CẢ cases có trong template — không được bỏ bớt, không được chọn lọc.**

**⚠️ Lazy-load field templates — CHỈ load template cho field types có trong RSD:**

**Bắt buộc theo 3 bước:**
1. Từ `inventory.fieldConstraints[]`, extract danh sách unique field types (VD: textbox, combobox, datepicker)
2. CHỈ đọc sections tương ứng từ field-templates.md — mỗi section cho 1 field type
3. **KHÔNG đọc toàn bộ 19 templates** — chỉ đọc template của field types thực tế có trong tài liệu

**Cách đọc template:**
```bash
# Dùng search.py nếu hỗ trợ --section:
python $SKILL_SCRIPTS/search.py --ref field-templates --section "textbox,combobox,datepicker"

# Nếu search.py không hỗ trợ --section → đọc file và CHỈ áp dụng template sections cho field types có trong RSD
```

Dispatch by field.type:

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
- Boundary: nhập maxLen-1, maxLen, nhập maxLen+1 → cảnh báo; Paste maxLen+1 → chặn
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

In ra checklist đối chiếu sau khi generate xong validate section:
```
Fields đã gen (đối chiếu với inventory.fieldConstraints[]):
[x] Textbox Tên SLA          → always    → có #### validate cases
[x] Dropdown Loại nghiệp vụ  → always    → có #### validate cases
[ ] Searchable Dropdown Luồng phê duyệt → always ← THIẾU validate → THÊM NGAY
[x] Dropdown Kỳ hạn          → conditional → có validate cases (khi enable) + enable/disable cases
```
- TỪNG field trong `inventory.fieldConstraints[]` → phải có `####` heading với validate cases
- Field `displayBehavior=always` → KHÔNG được có enable/disable cases, CHỈ validate cases
- Field `displayBehavior=conditional` → CÓ validate cases (khi field đang enable) + enable/disable cases
- **⛔ Điều kiện ẩn/hiện của block/nhóm thuộc giao diện chung, KHÔNG vào validate:**
  - ĐÚNG: "Khối Luồng trình ẩn khi Loại nghiệp vụ ≠ Cấp tín dụng" → `### Kiểm tra giao diện khi Loại nghiệp vụ = "Cấp tín dụng"` trong giao diện chung
  - ĐÚNG: "Nhóm Thông tin thêm hiển thị khi chọn Loại = Ưu đãi" → `### Kiểm tra giao diện khi Loại = "Ưu đãi"` trong giao diện chung
- TỪNG combobox/dropdown → có API timeout/error/rỗng cases?
- **Expected result cho error messages:** `message != null` → dùng exact text trong `""` / `message = null` → mô tả hành vi, KHÔNG đặt trong `""`
- Item nào sai hoặc thiếu → THÊM/SỬA bullet `### [SỬA]` ngay.
→ Count: {generated}/{expected} fields covered. Missing → THÊM ngay, KHÔNG proceed đến section tiếp.

**For DETAIL screens:** Do NOT use field templates. Use `generateDetailDataSection()` — test data display, null/empty handling, SQL queries per field.

**Grid section (LIST only):** Default state, sort order, each column with SQL, scroll behavior (pinned columns), data verification.

**Pagination section (hardcoded):** Values, default, per-value test, page navigation. Only generate when pagination exists.

**Function section (LLM-generated per screenType) — PHẢI inject inventory từ Step 4c vào generation:**

**⚠️ Section này phải cover TOÀN BỘ business logic. KHÔNG được sinh function section mà không có inventory items.**

**⚠️ KHÔNG duplicate validate cases vào chức năng:**
- Lỗi validate field (empty, type, length, format, date constraint, cross-field) đã có trong "Kiểm tra validate" → KHÔNG viết lại vào "Kiểm tra chức năng"
- **Cross-field validate** (VD: expiredDate < effectiveDate, endDate ≤ startDate) → sinh trong validate section dưới field thứ 2, KHÔNG sinh trong chức năng
- Chức năng **CHỈ** test: button actions, save/submit flow, status transitions, permissions, auto-fill behavior

**⚠️ PHẢI tách riêng từng action thành ### heading riêng biệt:**

Nếu màn hình có nhiều action/button (VD: Lưu, Chỉnh sửa, Đẩy duyệt, Xóa), **mỗi action = 1 heading `###` riêng**:

```
## Kiểm tra chức năng

### Kiểm tra chức năng Lưu
- Lưu thành công khi ...
- Lưu thất bại khi ...

### Kiểm tra chức năng Chỉnh sửa
- Chỉnh sửa thành công khi ...

### Kiểm tra chức năng Đẩy duyệt
- Đẩy duyệt thành công khi ...
- Đẩy duyệt thất bại khi ...
```

**KHÔNG gộp tất cả actions vào chung 1 heading.** Mỗi action có business rules riêng → tách riêng để dễ đọc và kiểm tra.

**Split function generation thành sub-sections:**

**Sub-section A — Button/Action flows (TÁCH RIÊNG TỪNG ACTION):**
- TỪNG `businessRules[section="function"]` → test condition met + not met
- TỪNG `errorMessages[section="function"]` → test trigger với exact message
- FORM: **Mỗi button/action = 1 heading `###` riêng**: Lưu (success + fail), Chỉnh sửa, Đẩy duyệt, Xóa, Cancel, Navigation...

**Sub-section B — Enable/Disable + Auto-fill:**
- TỪNG `enableDisableRules[section="function"]` → test state enable VÀ disable
- TỪNG `autoFillRules[]` → test verify auto-fill behavior

**Sub-section C — Status transitions + Permissions:**
- TỪNG `statusTransitions[]` → valid transition + invalid transition
- TỪNG `permissions[]` → test visibility/accessibility per role

**Per-sub-section checkpoint (MANDATORY):**
```
Sub-A: {N}/{N} business rules, {N}/{N} error messages covered — tách {N} actions riêng biệt
Sub-B: {N}/{N} enable/disable, {N}/{N} auto-fill covered
Sub-C: {N}/{N} transitions, {N}/{N} permissions covered
→ Missing: [list] → THÊM bullet `### [SỬA]` ngay
```

**Screen type guidance:**
- **LIST:** Search per field (exists/not exists/partial), combined search, clear filter, add new button
- **FORM/POPUP:** Save success/fail, field interactions, cancel, back navigation — **mỗi button = 1 `###` riêng**
- **DETAIL:** Button visibility by status/permission, click actions, navigation, status transitions
- **All:** Buttons belong in function section (not validate)

**⚠️ Project AGENTS.md override:** If project AGENTS.md defines additional function section rules → apply them here.

**Post-section checkpoint — Function (Frontend):**
- TỪNG `inventory.businessRules[section="function"]` → có bullet?
- TỪNG `inventory.errorMessages[section="function"]` → có bullet với exact message?
- TỪNG `inventory.enableDisableRules[]` → có bullet state enable VÀ disable?
- TỪNG `inventory.autoFillRules[]` → có bullet verify auto-fill?
- TỪNG `inventory.permissions[]` → có bullet cho từng role?
- Item nào thiếu → THÊM bullet `### [SỬA]` ngay.
→ Count: {generated}/{expected}. Missing → THÊM ngay, KHÔNG proceed.

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

### Step 5a2: Pass 2 — Gap Analysis & Auto-Fill

**Sau khi generate xong tất cả sections, thực hiện pass 2:**

1. **Re-read inventory** từ Step 4c
2. **Scan output markdown** — với MỖI inventory item:
   - Tìm keyword/field name/error message trong output
   - Nếu KHÔNG TÌM THẤY → flag as gap
3. **Gap list:**
```
🔍 Gap Analysis:
- ☐ field "Luồng phê duyệt" → chưa có validate cases
- ☐ enableDisableRule "Button Lưu disable" → chưa có test case
- ☐ errorMessage "Tên SLA đã tồn tại" → chưa có bullet
```
4. **Auto-fill:** Sinh bullet cho TẤT CẢ gaps → THÊM vào output với `### [SỬA]`
5. **Re-verify:** Tất cả items covered → proceed

**Chỉ proceed khi Gap list = empty.**

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
python <skills-root>/generate-test-design-frontend/scripts/search.py --ref quality-rules
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
python <skills-root>/generate-test-design-frontend/scripts/search.py --list
```

## Project Structure

After running `test-genie init`, your project has this structure:

```
<project-root>/
├── node_modules/test-genie/           ← Skills live here (managed by npm)
│   ├── generate-test-design-frontend/
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
│   └── generate-test-case-frontend/
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

- Kiểm tra hiển thị icon X khi chọn giá trị
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
