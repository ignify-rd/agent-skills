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
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/test-case-generator-api/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
```

If empty, try direct paths:
```bash
for d in \
  ".cursor/skills/test-case-generator-api/scripts" \
  ".claude/skills/test-case-generator-api/scripts" \
  ".windsurf/skills/test-case-generator-api/scripts"; do
  [ -f "$d/search.py" ] && SKILL_SCRIPTS="$d" && break
done
```

Or global npm:
```bash
npm_root=$(npm root -g 2>/dev/null)
[ -n "$npm_root" ] && [ -f "$npm_root/test-genie/test-case-generator-api/scripts/search.py" ] && \
  SKILL_SCRIPTS="$npm_root/test-genie/test-case-generator-api/scripts"
```

**Fallback:** Read reference files directly:
```
READ: <skills-dir>/test-case-generator-api/references/priority-rules.md
READ: <skills-dir>/test-case-generator-api/references/quality-rules.md
READ: <skills-dir>/test-case-generator-api/references/output-format.md
READ: <skills-dir>/test-case-generator-api/references/api-test-case.md
```

#### Load references
```bash
python $SKILL_SCRIPTS/search.py --ref priority-rules
python $SKILL_SCRIPTS/search.py --ref output-format
python $SKILL_SCRIPTS/search.py --ref quality-rules
python $SKILL_SCRIPTS/search.py --ref api-test-case
```

#### Extract test account
Priority: 1. Project AGENTS.md `testAccount` → 2. Catalog examples → 3. Default: `164987/ Test@147258369`

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

Extract complete inventory before generating. Output as internal JSON:

```json
{
  "apiName": "string",
  "endpoint": "METHOD /path",
  "errorCodes": [
    { "code": "PCER_001", "desc": "exact message", "triggerCondition": "condition", "section": "validate|main" }
  ],
  "businessRules": [
    { "id": "BR1", "type": "branch", "condition": "x = 1", "trueBranch": "do A", "falseBranch": "do B" }
  ],
  "modes": [
    { "name": "Thêm mới", "triggerValue": "type=1", "expectedAction": "INSERT" }
  ],
  "dbOperations": [
    { "table": "TABLE_NAME", "operation": "INSERT", "fieldsToVerify": ["COL1", "COL2"] }
  ],
  "externalServices": [
    { "name": "S3", "onFailure": "error code 2", "rollbackBehavior": "không INSERT DB" }
  ],
  "statusTransitions": [
    { "from": "N/A", "to": "WAITING (1)", "trigger": "success" }
  ],
  "decisionCombinations": [
    { "conditions": {"type": 1, "flag": true}, "expected": "success" }
  ]
}
```

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

Search catalog for style reference:
```bash
python $SKILL_SCRIPTS/search.py "{keyword}" --domain api --full --top 3
```

**Catalog style = primary.** References only provide rules/logic.

---

Split into 3 batches:

**BATCH 1 — Pre-validate sections:**
- All ## sections BEFORE "Kiểm tra validate" (common cases, permissions)
- Force testSuiteName = section name
- Instruction: "Chỉ sinh test cases cho section: {name}. KHÔNG sinh cases cho validate hay luồng chính."

**Post-batch checkpoint — BATCH 1:**
- Mỗi section đã có test cases? (Method, URL, Authorization)
- Thiếu → tự APPEND ngay.

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

**BATCH 3 — Post-validate sections:**
- All ## sections AFTER "Kiểm tra validate" (grid, functionality, timeout)
- Inject full inventory into generation instruction:

```
Sinh test cases cho luồng chính. BẮT BUỘC apply đủ 6 kỹ thuật:

1. Happy paths — ≥1 test cho TỪNG mode: {list modes}
2. Branch coverage — test TRUE + FALSE cho TỪNG branch: {list}
3. Decision table — test cho TỪNG combination: {list}
4. Error code coverage — ≥1 test trigger TỪNG code (exact message): {list}
5. DB verification — test verify TỪNG table/operation: {list}
6. External service failures — test onFailure + onTimeout cho TỪNG service: {list}

Inventory có N items → output phải cover ≥N items.
```

**Post-batch checkpoint — BATCH 3:**
- [ ] TỪNG mode → có ≥1 happy path?
- [ ] TỪNG branch → có test TRUE + FALSE?
- [ ] TỪNG error code → có test với exact message?
- [ ] TỪNG dbOperation → có test SELECT verify tất cả fields?
- [ ] TỪNG service → có test onFailure + onTimeout?
- [ ] TỪNG combination → có test với exact combo?
- Item thiếu → tự APPEND.

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
