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

**Đọc PDF bằng Read tool. Không có ngoại lệ.**

```
Read file: path/to/document.pdf
Read file: path/to/document.pdf pages=1-10    (file lớn, đọc theo pages)
```

**CẤM TUYỆT ĐỐI:**
- ❌ KHÔNG tạo file mới: `.py`, `.ps1`, `.sh`, `.js`
- ❌ KHÔNG chạy `python`, `python3`, `pip install` để đọc PDF
- ❌ KHÔNG import PyPDF2, pdfplumber, fitz
- ❌ KHÔNG tạo script để đọc PDF

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

**How it works:** If project `AGENTS.md` defines a rule → use that rule. If not → use the skill defaults below.

## Workflow

### Step 0: Validate Project Setup & Load Project Rules

1. **Check catalog** — look for `catalog/` directory at project root (contains `api/`, `frontend/`)
2. **Check & READ AGENTS.md** — look for `AGENTS.md` at project root
3. **Check template structure** — look for `excel_template/structure.json`

**If catalog directory does not exist:**
- Ask user: "Chưa có thư mục `catalog/`. Bạn đã chạy `test-genie init` chưa?"

**If AGENTS.md exists at project root:**
- **READ the entire file content** — extract ALL sections and rules defined by the project
- Store as `projectRules` — apply throughout generation when explicitly defined
- Sections not mentioned fall back to skill-level defaults

**If AGENTS.md does not exist at project root:**
- Use skill-level defaults
- Inform user: "Project chưa có AGENTS.md. Đang dùng rules mặc định."

**If `excel_template/structure.json` does not exist:**
- Check if `excel_template/template.xlsx` exists
- If yes → run `python <skills-root>/scripts/extract_structure.py` to generate it

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

### Step 2: Load Rules & References

#### Resolve SKILL_SCRIPTS path

```bash
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/test-case-generator-frontend/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
```

If empty, try direct paths:
```bash
for d in \
  ".cursor/skills/test-case-generator-frontend/scripts" \
  ".claude/skills/test-case-generator-frontend/scripts" \
  ".windsurf/skills/test-case-generator-frontend/scripts"; do
  [ -f "$d/search.py" ] && SKILL_SCRIPTS="$d" && break
done
```

Or global npm:
```bash
npm_root=$(npm root -g 2>/dev/null)
[ -n "$npm_root" ] && [ -f "$npm_root/test-genie/test-case-generator-frontend/scripts/search.py" ] && \
  SKILL_SCRIPTS="$npm_root/test-genie/test-case-generator-frontend/scripts"
```

**Fallback:** Read reference files directly:
```
READ: <skills-dir>/test-case-generator-frontend/references/priority-rules.md
READ: <skills-dir>/test-case-generator-frontend/references/quality-rules.md
READ: <skills-dir>/test-case-generator-frontend/references/output-format.md
READ: <skills-dir>/test-case-generator-frontend/references/fe-test-case.md
READ: <skills-dir>/test-case-generator-frontend/references/field-templates.md
```

#### Load references
```bash
python $SKILL_SCRIPTS/search.py --ref priority-rules
python $SKILL_SCRIPTS/search.py --ref output-format
python $SKILL_SCRIPTS/search.py --ref quality-rules
python $SKILL_SCRIPTS/search.py --ref fe-test-case
# field-templates.md: used internally for field type dispatch, load via search or direct read
```

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

Search catalog for style reference:
```bash
python $SKILL_SCRIPTS/search.py "{keyword}" --domain frontend --full --top 3
```

**Catalog style = primary.** References only provide rules/logic.

---

Split into 3 batches:

**BATCH 1 — Pre-validate sections:**
- All ## sections BEFORE "Kiểm tra validate" (giao diện chung, phân quyền)
- Force testSuiteName = section name
- Combine all pre-sections in 1 LLM call

**Post-batch checkpoint — BATCH 1:**
- Mỗi section đã có test cases? (navigation, layout, permission)
- Thiếu → tự APPEND ngay.

**BATCH 2 — Validate section:**
- "Kiểm tra validate" and all ### subsections
- Group 3-5 fields per sub-batch (similar types together)
- Max 5 fields per sub-batch
- Load `field-templates.md` for field-specific test cases

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

**BATCH 3 — Post-validate sections:**
- All ## sections AFTER "Kiểm tra validate" (grid, pagination, chức năng, timeout)
- Combine all post-sections in 1 LLM call
- Inject inventory items:

```
Sinh ## Kiểm tra chức năng. BẮT BUỘC cover đủ:
- TỪNG button/action → test success + fail + permission
- TỪNG enable/disable rule → test cả 2 states
- TỪNG auto-fill rule → verify auto-fill behavior
- TỪNG error message → test với exact message
- TỪNG permission → test visibility/accessibility per role
```

**Post-batch checkpoint — BATCH 3:**
- [ ] TỪNG button/action → có success + fail + permission cases?
- [ ] TỪNG enable/disable rule → có state enable VÀ disable?
- Item thiếu → tự APPEND.

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
