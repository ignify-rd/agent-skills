---
name: generate-test-case-api
description: Generate API test cases from RSD/PTTK (or mindmap) and output to test-cases.json. For API endpoints only. Use when user says "sinh test case api", "sinh test cases api", "generate api test case", "tạo test case api", or provides RSD/PTTK/.pdf documents or a mindmap file for an API endpoint.
---

# Test Case Generator — API Mode

Generate test cases for API endpoints from RSD/PTTK documents (or mindmap) and output to a JSON file. Đọc trực tiếp RSD/PTTK — KHÔNG yêu cầu user tạo test design/mindmap trước. Uses a searchable catalog of real API test cases (CSV format exported from spreadsheet) to ensure output matches the expected format per project.

Output: **`test-cases.json`** — a JSON array of test case objects. To upload to Google Sheets, use: `python upload_gsheet.py <tên-test-case>`

## When to Apply

- User says "sinh test case api", "sinh test cases api", "tạo test case api", "generate api test case"
- User provides RSD/PTTK for an API endpoint and asks to generate test cases → **đọc RSD trực tiếp, KHÔNG yêu cầu tạo test design trước**
- User provides a mindmap file (.txt or .md exported from .gmind) for an API
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
| Output JSON field names | No |
| Batch strategy (BATCH 1/2/3 split) | No |
| Field type dispatch table | No |
| Importance mapping | No |

**How it works:** Chat input from the user → Project `AGENTS.md` → Skill defaults. User says "viết ngắn gọn" → do it, even if it contradicts AGENTS.md or skill defaults.

## Workflow

### Step 0: Validate Project Setup & Load Project Rules

Before starting generation, check project structure and **load project-level rules**:

1. **Check catalog** — look for `catalog/` directory at project root (contains `api/`, `frontend/` subdirectories)
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

**If catalog exists but has no examples (empty api/ and frontend/):**
- Warn user: "Catalog chưa có examples. Output có thể không chính xác format. Bạn có muốn thêm CSV examples trước không?"
- Proceed with skill references as fallback

**⚠️ CRITICAL: Project AGENTS.md rules take precedence when explicitly defined.** Every subsequent step must check `projectRules` and apply them.

**If `excel_template/structure.json` does not exist:**
- Check if `excel_template/template.xlsx` exists
- If yes → run `python <skills-root>/test-case-generator-api/scripts/extract_structure.py --project-root .` to generate it
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
   - DB field mappings
   - Mode variations
   - External service behaviors

2. **Khi đọc RSD/PTTK ở Step 4** — bổ sung inventory từ mindmap:
   - Nếu RSD/PTTK có thông tin BỔ SUNG cho 1 item đã có trong mindmap → dùng RSD/PTTK (chi tiết hơn)
   - Nếu RSD/PTTK có item MỚI không có trong mindmap → thêm vào inventory
   - **Tuyệt đối KHÔNG bỏ qua** thông tin đã extract từ mindmap

3. **Priority khi conflict:**
   - Exact error message: dùng message từ RSD/PTTK (nếu chi tiết hơn)
   - Error codes + trigger: **GIỮ NGUYÊN** từ mindmap
   - Business logic: RSD thắng

**Tại sao đọc mindmap trước?**
Mindmap từ test-design đã trải qua quá trình extract kỹ lưỡng (Step 4c inventory trong test-design), bao gồm exact error messages từ bảng mã lỗi. Nếu bỏ qua mindmap và đọc lại RSD/PTTK, agent có thể miss exact messages vì phải tự extract lại.

### Step 2: Load Rules & References

#### Resolve SKILL_SCRIPTS path

```bash
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/test-case-generator-api/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
# Fallback: check .cursor/skills, .claude/skills, .windsurf/skills, or global npm
```

If all fail → Read reference files directly from `<skills-dir>/test-case-generator-api/references/`.

#### Load references
```bash
python $SKILL_SCRIPTS/search.py --ref priority-rules
python $SKILL_SCRIPTS/search.py --ref output-format
python $SKILL_SCRIPTS/search.py --ref quality-rules
python $SKILL_SCRIPTS/search.py --ref api-test-case
```

#### Extract test account from catalog

Priority: 1. Project AGENTS.md `testAccount` → 2. Catalog examples → 3. Default: `164987/ Test@147258369`

**How to extract from catalog:**
- Read first few rows of `catalog/api/*.csv`
- Look for the login/account pattern in `preConditions` column
- Pattern: account string like `164987/ Test@147258369`

**Store the resolved account** for use in all test case generation batches. The account MUST be consistent across all test cases in the output.

**Cách diễn đạt, hành văn:** Toàn bộ cách viết preConditions, step, expectedResult cũng phải **tuân theo catalog**. Catalog là nguồn chuẩn cho style/wording — nếu catalog viết theo cách nào thì output phải theo đúng cách đó.

### Step 3: Read the Mindmap

Parse: Line 1 = API name → `preConditions`; ## headings = test suites → `testSuiteName`; ### headings = field groupings; - bullets = `testCaseName`.

### Step 4: Extract Field & Body Context

1. Find the API endpoint section in PTTK (preferred) or RSD (fallback)
2. Extract: field names, data types, required/optional, maxLength, format constraints
3. Build complete request body JSON with ALL required fields having concrete values
4. Extract response templates (SUCCESS + ERROR) — inject into all batches

### Step 4b: Validate Documents & Ask Clarification

**Missing information (MUST ask):**
- Cannot find exact API in PTTK → ask user to confirm which API
- Mindmap has fields not found in RSD/PTTK → ask: skip or generate with available info
- No response body structure → ask for supplementary docs

**Conflicts (MUST ask):**
- Mindmap field name differs from PTTK/RSD → confirm which name to use
- PTTK says required but RSD says optional → confirm which document to follow

### Step 4c: Business Logic Inventory

**⚠️ NGUYÊN TẮC TRÍCH XUẤT — KHÔNG HALLUCINATE:**
- Mỗi item trong inventory PHẢI có field `"source"` ghi rõ trang/section trong tài liệu.
- Nếu không tìm thấy nguồn trong RSD/PTTK → **KHÔNG thêm item vào inventory**. Ghi nhận là missing và hỏi user.
- **KHÔNG suy luận** error codes, table names, field names, hay business rules dựa trên kiến thức chung.

Extract complete inventory before generating. Output as internal JSON:

```json
{
  "apiName": "string",
  "endpoint": "METHOD /path",
  "errorCodes": [
    { "code": "PCER_001", "desc": "exact message từ tài liệu", "triggerCondition": "condition", "section": "validate|main", "source": "RSD trang X / PTTK section Y" }
  ],
  "businessRules": [
    { "id": "BR1", "type": "branch", "condition": "x = 1", "trueBranch": "do A", "falseBranch": "do B", "source": "RSD trang X" }
  ],
  "modes": [
    { "name": "Thêm mới", "triggerValue": "type=1", "expectedAction": "INSERT", "source": "Ảnh X" }
  ],
  "dbOperations": [
    { "table": "TABLE_NAME", "operation": "INSERT", "fieldsToVerify": ["COL1", "COL2"], "source": "RSD trang X / PTTK section Y" }
  ],
  "externalServices": [
    { "name": "S3", "onFailure": "error code từ RSD", "rollbackBehavior": "mô tả từ RSD", "source": "RSD trang X" }
  ],
  "statusTransitions": [
    { "from": "N/A", "to": "WAITING (1)", "trigger": "success", "source": "PTTK trang X" }
  ],
  "decisionCombinations": [
    { "conditions": {"type": 1, "flag": true}, "expected": "success", "source": "RSD trang X" }
  ]
}
```

**⚠️ Inventory = Mandatory Checklist:**
Mỗi item trong inventory PHẢI map đến ≥1 test case trong output. Tracking table:

| Inventory Item | Required Test Cases | Generated? |
|---|---|---|
| Mỗi errorCode | ≥1 test trigger | ☐ |
| Mỗi businessRule | test TRUE + FALSE | ☐ |
| Mỗi mode | ≥1 happy path | ☐ |
| Mỗi dbOperation | SQL verify all columns | ☐ |
| Mỗi externalService | onFailure + rollback | ☐ |
| Mỗi decisionCombo | exact combo test | ☐ |

**Sau mỗi batch, update table. Cuối cùng tất cả phải = ☑.**

### Step 4d: Inventory Verification Gate

**Sau khi extract xong, PHẢI báo cáo cho user:**
```
📋 Business Logic Inventory đã extract:
- Error codes:        {N} (list: ...)
- Business rules:     {N} branches (list: BR1, BR2, ...)
- Modes/flows:        {N} (list: Thêm mới, Xoá, ...)
- DB operations:      {N} tables
- External services:  {N}
- Decision combos:    {N}
```

**Nếu bất kỳ category = 0 VÀ tài liệu có khả năng chứa → hỏi user.**
**Nếu tất cả = 0:** Dừng, hỏi user chỉ rõ section chứa business logic.

### Step 5: Generate Test Cases in Batches

#### Step 5a: Load Catalog Style Examples (MANDATORY)

**⚠️ CRITICAL — Catalog examples là nguồn chuẩn cho style/wording. PHẢI load trước khi sinh bất kỳ test case nào.**

Search catalog to get 1 real example. This is the **primary style reference** — output PHẢI follow catalog format, KHÔNG follow reference examples.

```bash
python $SKILL_SCRIPTS/search.py "{feature_keyword}" --domain api --full --top 1
```

**Nếu catalog có examples:**
1. Đọc 3-5 examples đầu tiên (full content: preConditions, steps, expectedResults)
2. **Extract style patterns:**
   - **testSuiteName convention** — catalog chia suite thế nào? field sub-suites `"FieldType: FieldName"` hay chung?
   - **preConditions format** — format Đ/k, numbering, wording
   - **steps format** — động từ, cấu trúc câu
   - **expectedResults format** — format, wording
   - **testCaseName convention** — prefix? format?
3. Lưu patterns làm `catalogStyle` — dùng cho TOÀN BỘ batches

**Catalog style override TOÀN BỘ format mặc định:**
- Field sub-suites → dùng field sub-suites (bỏ qua "KHÔNG có field sub-suites" trong refs)
- PreConditions 1 dòng → dùng 1 dòng (bỏ qua multi-line trong refs)

**References chỉ cung cấp: LOẠI cases nào cần check (rules/logic). Catalog quyết định: VIẾT như thế nào (format/style).**

**Nếu catalog KHÔNG có examples:**
- Warn user: "Catalog chưa có examples, sẽ dùng format mặc định từ references."
- Fall back to reference examples as style guide

---

**Quy tắc testSuiteName — Catalog convention ưu tiên:**

> **⚠️ Nếu catalog có convention riêng → PHẢI follow catalog.** Fallback dưới đây chỉ dùng khi catalog rỗng.
>
> **Fallback:** `"Kiểm tra các case common"`, `"Kiểm tra phân quyền"`, `"Kiểm tra trường {fieldName}"` (BATCH 2), `"Kiểm tra luồng chính"`, `"Kiểm tra timeout"`

**BATCH 1 — Pre-validate sections:**
- All ## sections BEFORE "Kiểm tra validate" (common cases, permissions)
- Force testSuiteName = section name
- Instruction: "Chỉ sinh test cases cho section: {name}. KHÔNG sinh cases cho validate hay luồng chính."

**Post-batch checkpoint — BATCH 1:**
- Mỗi section đã có test cases? (Method, URL, Authorization)
- Thiếu → tự APPEND ngay.
→ Count: {generated}/{expected}. If any missing → APPEND immediately, do NOT proceed to BATCH 2.

**BATCH 2 — Validate section:**
- "Kiểm tra validate" and all ### subsections
- Group 3-5 fields per sub-batch (similar types together)
- Max 5 fields per sub-batch

**Minimum case count per field type:**

| Field type | Min cases | Must include |
|-----------|-----------|--------------|
| String | ≥15 | empty, null, maxLen-1/maxLen/maxLen+1, XSS, SQL, emoji |
| Number/Integer | ≥12 | empty, null, negative, decimal, leading-zero, string, XSS, SQL |
| Date | ≥10 | empty, null, correct/wrong format, invalid date, past/present/future |
| Array | ≥8 | missing, null, empty, wrong type |

**Post-batch checkpoint — BATCH 2:**
- Mỗi field đã có test cases? Field nào < min_cases → APPEND cases còn thiếu.
→ Count per field: {field}: {generated}/{min_cases}. If any field < min → APPEND immediately, do NOT proceed to BATCH 3.

**BATCH 3 — Post-validate sections (split by technique):**
- All ## sections AFTER "Kiểm tra validate" (grid, functionality, timeout)
- **Split into sub-batches by technique** to ensure thorough coverage:

**Sub-batch 3a — Happy paths (1 per mode):**
- Inject: `inventory.modes[]`
- Sinh ≥1 happy path test cho TỪNG mode
- Include full response body + SQL verify

**Sub-batch 3b — Branch coverage:**
- Inject: `inventory.businessRules[]`
- Sinh test TRUE + FALSE cho TỪNG branch
- Include response body cho mỗi case

**Sub-batch 3c — Error code coverage:**
- Inject: `inventory.errorCodes[section="main"]`
- Sinh ≥1 test trigger TỪNG error code với **exact message**
- testSuiteName = "Kiểm tra luồng chính"

**Sub-batch 3d — DB verification + External services:**
- Inject: `inventory.dbOperations[]` + `inventory.externalServices[]`
- Sinh test verify TỪNG table/operation với full SQL SELECT (all columns)
- Sinh test onFailure + onTimeout cho TỪNG external service
- Include rollback behavior

**Sub-batch 3e — Decision table:**
- Inject: `inventory.decisionCombinations[]`
- Sinh test cho TỪNG combination

**Per-sub-batch checkpoint (MANDATORY after each sub-batch):**
After each sub-batch, count generated items vs inventory items:
```
Sub-batch 3a: {generated}/{total} modes covered
Sub-batch 3b: {generated}/{total} branches covered
Sub-batch 3c: {generated}/{total} error codes covered
Sub-batch 3d: {generated}/{total} DB ops + {generated}/{total} services covered
Sub-batch 3e: {generated}/{total} combinations covered
→ Missing items: [list] → AUTO-APPEND immediately
```

**After all batches:** Deduplicate testCaseNames (case-insensitive, keep first).

### Step 5b: Final Coverage Summary

**PHẢI hiển thị cho user:**
```
📊 Coverage Report:
✓ BATCH 1: {N}/{N} sections covered
✓ BATCH 2: {N}/{N} fields, {M} < min_cases → appended
✓ BATCH 3: {N}/{N} modes, {N}/{N} branches, {N}/{N} error codes, {N}/{N} DB ops, {N}/{N} services
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
- ☐ errorCode "PCER_001" → chưa có test case trigger
- ☐ branch BR2 FALSE → chưa có test case
- ☐ mode "Xoá" → chưa có happy path
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
test-case-generator-api/
├── SKILL.md                      ← Workflow instructions (API mode only)
├── AGENTS.md                     ← Skill-level default rules
├── references/
│   ├── api-test-case.md          ← API test case rules
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
        ├── default/api/          ← API test case CSV examples
        └── _template/api/        ← Template AGENTS.md
```

## Quick Reference — API testCaseName format

| testSuiteName | testCaseName format |
|---------------|---------------------|
| Kiểm tra các case common | `Method_Kiểm tra khi nhập sai method` |
| Kiểm tra phân quyền | `Phân quyền_Kiểm tra user không có quyền` |
| Kiểm tra trường {field} | `{field}_Bỏ trống`, `{field}_Truyền 101 ký tự` |
| Kiểm tra luồng chính | `Luồng chính_Upload thêm mới thành công` |
| Kiểm tra timeout | `Timeout_Kiểm tra khi server không phản hồi` |

**Format:** `"Category_Mô tả"` — category = field name or section. Use `_` underscore between category and description.
