---
name: generate-test-case-frontend
description: Generate Frontend test cases from RSD/PTTK (or mindmap) and output to test-cases.json. For UI screens only. Use when user says "sinh test case frontend", "sinh test case fe", "sinh test case giao diện", "generate frontend test case", "tạo test case màn hình", or provides RSD/PTTK/.pdf documents or a mindmap file for a UI screen.
---

# Test Case Generator — Frontend Mode

Generate test cases for UI screens from RSD/PTTK documents (or mindmap) and output to a JSON file. Đọc trực tiếp RSD/PTTK — KHÔNG yêu cầu user tạo test design/mindmap trước. Uses a searchable catalog of real Frontend test cases (CSV format exported from spreadsheet) to ensure output matches the expected format per project.

Output: **`test-cases.json`** — a JSON array of test case objects. To upload to Google Sheets, use: `python upload_gsheet.py <tên-test-case>`

## When to Apply

- User says "sinh test case frontend", "sinh test case fe", "sinh test case giao diện", "tạo test case màn hình", "generate frontend test case"
- User provides RSD/PTTK for a UI screen and asks to generate test cases → **đọc RSD trực tiếp, KHÔNG yêu cầu tạo test design trước**
- User provides a mindmap file (.txt or .md exported from .gmind) for a UI screen
- User provides a feature folder containing .pdf files → scan và đọc trực tiếp

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## Đọc file PDF — CHỈ dùng Read tool

Đọc PDF bằng Read tool (`pages` parameter cho file lớn). **CẤM TUYỆT ĐỐI** tạo script (.py/.ps1/.sh/.js), chạy python/pip, import thư viện PDF.

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

**How it works:** Chat input from the user → Project `AGENTS.md` → Skill defaults. User says "viết ngắn gọn" → do it, even if it contradicts AGENTS.md or skill defaults.

## Workflow

### Step 0: Validate Project Setup & Load Project Rules

Before starting generation, check project structure and **load project-level rules**:

1. **Check catalog** — look for `catalog/` directory at project root (contains `frontend/` subdirectory)
2. **Check & READ AGENTS.md** — look for `AGENTS.md` at project root
3. **Check template structure** — look for `excel_template/structure.json`

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
- Use skill-level defaults
- Inform user: "Project chưa có AGENTS.md. Đang dùng rules mặc định."

**If catalog exists but has no examples (empty frontend/):**
- Warn user: "Catalog chưa có examples. Output có thể không chính xác format. Bạn có muốn thêm CSV examples trước không?"
- Proceed with skill references as fallback

**⚠️ CRITICAL: Project AGENTS.md rules take precedence when explicitly defined.** Every subsequent step must check `projectRules` and apply them.

**If `excel_template/structure.json` does not exist:**
- Check if `excel_template/template.xlsx` exists
- If yes → run `python <skills-root>/test-case-generator-frontend/scripts/extract_structure.py --project-root .` to generate it
- If no → inform user: "Chưa có template. Bạn cần đặt file template.xlsx vào excel_template/"

### Step 1: Check Input Type

**If user provides a feature folder name:**
1. Look inside `<feature-name>/` for input documents: `.pdf`, `.docx`, `.md`, `.txt`
2. **DO NOT ask** the user for file paths
3. **If folder is empty** → scan project root for relevant documents
4. If no documents found → inform user

| Input found | Flow |
|-------------|------|
| Document files found | **Direct flow** — đọc trực tiếp |
| Only `test-design.md` | **Mindmap-only flow** — dùng mindmap |
| Mindmap provided directly | **Mindmap flow** — go to Step 3 |

**LUÔN đọc RSD/PTTK nếu có** — không yêu cầu user tạo test design trước.

### Step 1b: Read Mindmap First (if available alongside RSD/PTTK)

**⚠️ CRITICAL — Đọc mindmap TRƯỚC khi đọc RSD/PTTK khi có cả hai.**

Khi user cung cấp CẢ mindmap (test-design đã sinh) VÀ RSD/PTTK:

1. **Đọc mindmap TRƯỚC TIÊN** — extract vào inventory tạm:
   - Exact error messages (đã extract từ bảng mã lỗi trong mindmap)
   - Error codes với trigger conditions
   - Business rules với exact descriptions
   - Luồng chính đã được phân tích
   - DB field mappings (nếu có)
   - Mode variations
   - External service behaviors
   - displayBehavior per field (always/conditional)
   - Enable/disable rules đã extract
   - Auto-fill rules đã extract

2. **Khi đọc RSD/PTTK ở Step 4** — bổ sung inventory từ mindmap:
   - Nếu RSD/PTTK có thông tin BỔ SUNG cho 1 item đã có trong mindmap → dùng RSD/PTTK (chi tiết hơn)
   - Nếu RSD/PTTK có item MỚI không có trong mindmap → thêm vào inventory
   - **Tuyệt đối KHÔNG bỏ qua** thông tin đã extract từ mindmap

3. **Priority khi conflict:**
   - Exact error message: dùng message từ RSD/PTTK (nếu chi tiết hơn)
   - Error codes + trigger: **GIỮ NGUYÊN** từ mindmap
   - Business logic: RSD thắng
   - displayBehavior: **GIỮ NGUYÊN** từ mindmap (đã được phân loại kỹ)

**Tại sao đọc mindmap trước?**
Mindmap từ test-design đã trải qua quá trình extract kỹ lưỡng (Step 4c inventory trong test-design), bao gồm exact error messages từ bảng mã lỗi và displayBehavior classification. Nếu bỏ qua mindmap và đọc lại RSD/PTTK, agent có thể miss exact messages vì phải tự extract lại.

### Step 2: Load Rules & References

#### Resolve SKILL_SCRIPTS path

```bash
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/test-case-generator-frontend/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
# Fallback: check .cursor/skills, .claude/skills, .windsurf/skills, or global npm
```

If all fail → Read reference files directly from `<skills-dir>/test-case-generator-frontend/references/`.

#### Load references
```bash
python $SKILL_SCRIPTS/search.py --ref priority-rules
python $SKILL_SCRIPTS/search.py --ref output-format
python $SKILL_SCRIPTS/search.py --ref quality-rules
python $SKILL_SCRIPTS/search.py --ref fe-test-case
```

**⚠️ field-templates.md: KHÔNG load toàn bộ ở đây.** Load theo field type trong BATCH 2 (lazy-load).

#### Extract test account
Priority: 1. Project AGENTS.md `testAccount` → 2. Catalog examples → 3. Default: `164987/ Test@147258369`

### Step 3: Read the Mindmap

Parse: Line 1 = Screen name → `preConditions`; ## headings = test suites → `testSuiteName`; ### headings = field groupings; - bullets = `testCaseName`.

### Step 4: Extract Field & Body Context

1. Find the screen/API section in PTTK (preferred) or RSD (fallback)
2. Extract: field names, types, placeholder, maxLength, API endpoints, DB mappings, enum values
3. Use extracted details to enrich validate test case generation

### Step 4b: Validate Documents & Ask Clarification

**Missing information (MUST ask):**
- Mindmap has fields not found in RSD/PTTK → ask: skip or generate with available info
- No screen structure in documents → ask for supplementary docs
- Ambiguous business logic → ask for clarification

**Conflicts (MUST ask):**
- Mindmap field name differs from RSD/PTTK → confirm which name to use

### Step 4c: Business Logic Inventory

Extract complete inventory before generating. Output as internal JSON:

```json
{
  "screenName": "Tên màn hình",
  "screenType": "FORM|LIST|POPUP|DETAIL",
  "fieldConstraints": [
    { "field": "Tên cấu hình SLA", "type": "textbox", "maxLength": 100, "required": true, "source": "RSD" }
  ],
  "businessRules": [
    { "id": "BR1", "type": "validation", "condition": "Tên đã tồn tại", "expected": "Hiển thị cảnh báo", "section": "validate" }
  ],
  "errorMessages": [
    { "trigger": "Bỏ trống field bắt buộc", "message": "exact message", "section": "validate" }
  ],
  "enableDisableRules": [
    { "field": "Button Lưu", "condition": "Form chưa nhập đủ", "state": "disable" }
  ],
  "autoFillRules": [
    { "trigger": "Chọn giá trị X", "target": "Field Y", "action": "auto-fill" }
  ],
  "statusTransitions": [
    { "from": "Draft", "to": "Active", "trigger": "Click Phê duyệt" }
  ],
  "permissions": [
    { "action": "Tạo mới", "role": "Maker" }
  ]
}
```

**⚠️ Inventory = Mandatory Checklist:**
Mỗi item trong inventory PHẢI map đến ≥1 test case trong output:

| Inventory Item | Required Test Cases | Generated? |
|---|---|---|
| Mỗi fieldConstraint | validate cases ≥ min_cases per type | ☐ |
| Mỗi businessRule | test condition met + not met | ☐ |
| Mỗi errorMessage | test trigger với exact message | ☐ |
| Mỗi enableDisableRule | test state enable + disable | ☐ |
| Mỗi autoFillRule | test auto-fill behavior | ☐ |
| Mỗi permission | test per role | ☐ |

**Sau mỗi batch, update table. Cuối cùng tất cả phải = ☑.**

### Step 4d: Inventory Verification Gate

**Sau khi extract xong, PHẢI báo cáo cho user:**
```
📋 Business Logic Inventory đã extract:
- Fields:             {N} fields cần generate validate cases
- Business rules:     {N} (list: BR1 [validate], BR2 [function], ...)
- Error messages:     {N} messages cần cover
- Enable/disable:    {N} rules
- Auto-fill:         {N} cascading rules
- Permissions:        {N} roles
```

**Nếu bất kỳ category = 0 VÀ tài liệu có khả năng chứa → hỏi user.**

### Step 5: Generate Test Cases in Batches

#### Step 5a: Load Catalog Style Examples (MANDATORY)

**⚠️ CRITICAL — Catalog examples là nguồn chuẩn cho style/wording. PHẢI load trước khi sinh bất kỳ test case nào.**

Search catalog to get 1 real example. This is the **primary style reference** — output PHẢI follow catalog format, KHÔNG follow reference examples.

```bash
python $SKILL_SCRIPTS/search.py "{feature_keyword}" --domain frontend --full --top 1
```

**Nếu catalog có examples:**
1. Đọc 3-5 examples đầu tiên (full content: preConditions, steps, expectedResults)
2. **Extract style patterns:**
   - **testSuiteName convention** — field sub-suites `"Textbox: Tên"` hay fallback `"Kiểm tra validate"`?
   - **preConditions format** — format Đ/k, numbering, wording
   - **steps format** — động từ, cấu trúc câu
   - **expectedResults format** — format, wording
   - **testCaseName convention** — KHÔNG có prefix, lấy trực tiếp từ mindmap
3. Lưu patterns làm `catalogStyle` — dùng cho TOÀN BỘ batches

**Catalog style override TOÀN BỘ format mặc định trong references.**

**References chỉ cung cấp: LOẠI cases nào cần check (rules/logic). Catalog quyết định: VIẾT như thế nào (format/style).**

**Nếu catalog KHÔNG có examples:**
- Warn user: "Catalog chưa có examples, sẽ dùng format mặc định từ references."
- Fall back to reference examples as style guide

---

Split into 3 batches:

**BATCH 1 — Pre-validate sections:**
- All ## sections BEFORE "Kiểm tra validate" (giao diện chung, phân quyền)
- Force testSuiteName = section name
- Combine all pre-sections in 1 LLM call

**Post-batch checkpoint — BATCH 1:**
- Mỗi section đã có test cases? (navigation, layout, permission)
- Thiếu → tự APPEND ngay.
→ Count: {generated}/{expected}. If any missing → APPEND immediately, do NOT proceed to BATCH 2.

**BATCH 2 — Validate section:**
- "Kiểm tra validate" and all ### subsections
- Group 3-5 fields per sub-batch (similar types together)
- Max 5 fields per sub-batch

**Lazy-load field templates:** Sau khi extract field types từ RSD/PTTK (Step 4), xác định danh sách unique field types (VD: textbox, combobox, datepicker). CHỈ load sections tương ứng từ field-templates.md:
```bash
# Chỉ load template cho field types có trong RSD, VD:
python $SKILL_SCRIPTS/search.py --ref field-templates --section "textbox,combobox,datepicker"
# HOẶC Read trực tiếp chỉ phần cần thiết từ field-templates.md
```
Nếu search.py chưa hỗ trợ `--section`, đọc file và CHỈ áp dụng template cho field types có trong RSD. **KHÔNG đọc toàn bộ 19 templates.**

**Minimum case count per field type:**

| Field type | Min cases | Must include |
|-----------|-----------|--------------|
| Textbox | ≥18 | default, placeholder, icon X, số, chữ, emoji, XSS, SQL, space, maxLen boundary |
| Combobox | ≥15 | default, placeholder, required, API timeout, API error, API rỗng, select, search |
| Simple Dropdown | ≥8 | default, placeholder, values, icon X, required |
| Toggle | ≥4 | default, toggle A→B, toggle B→A, disabled |
| DatePicker | ≥10 | display, placeholder, format, boundary, icon X, required |
| Upload/File | ≥8 | format, size boundary, empty, trùng tên |

**Post-batch checkpoint — BATCH 2:**
- Mỗi field đã có test cases? Field nào < min_cases → APPEND cases còn thiếu.
- Mỗi combobox đã có API timeout/error/rỗng cases?
→ Count per field: {field}: {generated}/{min_cases}. If any field < min → APPEND immediately, do NOT proceed to BATCH 3.

**BATCH 3 — Post-validate sections (split by technique):**
- All ## sections AFTER "Kiểm tra validate" (grid, pagination, chức năng, timeout)
- **Split into sub-batches by technique:**

**Sub-batch 3a — Button/Action success + fail:**
- Inject: `inventory.businessRules[section="function"]`
- Sinh test success + fail cho TỪNG button/action
- Include exact error messages từ `inventory.errorMessages[section="function"]`

**Sub-batch 3b — Enable/Disable rules:**
- Inject: `inventory.enableDisableRules[]`
- Sinh test state enable VÀ state disable cho TỪNG rule

**Sub-batch 3c — Auto-fill + Cascading:**
- Inject: `inventory.autoFillRules[]`
- Sinh test verify auto-fill behavior cho TỪNG rule

**Sub-batch 3d — Permissions + Status transitions:**
- Inject: `inventory.permissions[]` + `inventory.statusTransitions[]`
- Sinh test visibility/accessibility cho TỪNG role
- Sinh test valid + invalid transition cho TỪNG status transition

**Per-sub-batch checkpoint (MANDATORY after each sub-batch):**
```
Sub-batch 3a: {generated}/{total} actions covered
Sub-batch 3b: {generated}/{total} enable/disable rules covered
Sub-batch 3c: {generated}/{total} auto-fill rules covered
Sub-batch 3d: {generated}/{total} permissions + transitions covered
→ Missing items: [list] → AUTO-APPEND immediately
```

**After all batches:** Deduplicate testCaseNames (case-insensitive, keep first).

### Step 5b: Final Coverage Summary

**PHẢI hiển thị cho user:**
```
📊 Coverage Report:
✓ BATCH 1: {N}/{N} sections covered
✓ BATCH 2: {N}/{N} fields, {M} < min_cases → appended
✓ BATCH 3: {N}/{N} actions, {N}/{N} enable/disable rules
✅ Tổng: {total} test cases | Auto-appended: {M} cases
```

### Step 5b2: Pass 2 — Gap Analysis & Auto-Fill

**Re-read inventory từ Step 4c. Cross-check từng item:**

1. **Scan output** — với MỖI item trong inventory:
   - Search testCaseName/step/expectedResult chứa item keyword
   - Nếu KHÔNG TÌM THẤY → flag as gap
2. **Gap list:**
```
🔍 Gap Analysis:
- ☐ field "Tên SLA" → chỉ có 12/18 min cases
- ☐ enableDisableRule "Button Lưu disable" → chưa có test case
- ☐ errorMessage "Tên SLA đã tồn tại" → chưa có test trigger
```
3. **Auto-fill:** Sinh test cases cho TẤT CẢ gaps → APPEND vào output
4. **Verify:** Re-count → tất cả items phải covered

**Chỉ proceed khi Gap list = empty.**

### Step 5c: Final Project Rules Enforcement

**⚠️ MANDATORY — Đọc lại TOÀN BỘ `projectRules` (từ Step 0) và kiểm tra output lần cuối:**

1. Đọc lại `## Project-Specific Rules` trong project AGENTS.md
2. Duyệt từng rule → kiểm tra output đã tuân thủ chưa
3. Nếu vi phạm → sửa ngay trước khi chuyển Step 6

**Các lỗi thường gặp khi quên projectRules:**
- Button test cases nằm trong "Kiểm tra validate" thay vì "Kiểm tra chức năng"
- Test case viết dài dòng thay vì ngắn gọn
- Case chung chung thay vì tách riêng từng giá trị cụ thể
- Section assignment sai (buttons vào section khác với quy định của project)
- Ảnh có field nhưng thiếu test case

### Step 6: Output to JSON File

Generate JSON array, save to `<tên-test-case>/test-cases.json`:
```bash
python $SKILL_SCRIPTS/upload_gsheet.py <tên-test-case> --project-root .
```

Prerequisites: `pip install google-auth-oauthlib google-api-python-client openpyxl`

Report both JSON file and Google Sheets link to user.

## Project Structure

```
test-case-generator-frontend/
├── SKILL.md                         ← Workflow instructions (Frontend mode only)
├── AGENTS.md                        ← Skill-level default rules
├── references/
│   ├── fe-test-case.md             ← Frontend test case rules
│   ├── field-templates.md          ← Field type dispatch templates
│   ├── priority-rules.md
│   ├── output-format.md
│   └── quality-rules.md
├── scripts/
│   ├── search.py
│   ├── extract_structure.py
│   ├── upload_gsheet.py
│   └── ...
└── data/
    ├── templates/template.xlsx
    └── catalogs/
        ├── default/frontend/        ← Frontend test case CSV examples
        └── _template/
            ├── frontend/            ← Template AGENTS.md
            └── references/          ← Reserved
```

## Quick Reference — Frontend testCaseName format

- **testCaseName = LẤY TRỰC TIẾP từ mindmap bullet** — KHÔNG thêm prefix, KHÔNG thêm screen name
- **testSuiteName:** theo catalog convention — field sub-suites (`"Textbox: Tên cấu hình SLA"`) hoặc fallback `"Kiểm tra validate"`

| Catalog convention | testSuiteName |
|-------------------|---------------|
| Field sub-suites | `"Textbox: Tên cấu hình SLA"` |
| No sub-suites | `"Kiểm tra validate"` |

Examples:
- Mindmap: `- Kiểm tra khi nhập 101 ký tự`
  → testCaseName: `Kiểm tra khi nhập 101 ký tự` (NO prefix)
- Mindmap: `### Kiểm tra điều hướng đến màn hình`
  → testCaseName: `Kiểm tra điều hướng đến màn hình`
