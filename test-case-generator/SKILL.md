---
name: generate-test-case
description: Generate test cases from RSD/PTTK (or mindmap) and output to test-cases.json. Đọc trực tiếp RSD/PTTK — không yêu cầu tạo test design trước. Use when user says "sinh test case", "sinh test cases", "generate test case", "generate test cases", "tạo test case", "tạo test cases", "xuất test case", "xuất json", or provides RSD/PTTK/.pdf documents or a mindmap file.
---

# Test Case Generator

Generate test cases from RSD/PTTK documents (or mindmap) and output to a JSON file. Đọc trực tiếp RSD/PTTK — KHÔNG yêu cầu user tạo test design/mindmap trước. Uses a searchable catalog of real test cases (CSV format exported from spreadsheet) to ensure output matches the expected format per project.

Output: **`<tên-test-case>/test-cases.json`** — a JSON array of test case objects. To upload to Google Sheets, use: `python upload_gsheet.py <tên-test-case>`

> **Scope**: This skill covers **test case generation** (spreadsheet output) for two modes:
> - **API mode** — API test cases
> - **Frontend mode** — Frontend test cases
>
> It does **NOT** cover test design/mindmap generation — that is handled by `test-design-generator` skill.

## When to Apply

- User says "sinh test case", "sinh test cases", "tạo test case", "tạo test cases", "generate test case", "generate test cases", "xuất json", "xuất test case"
- User provides RSD/PTTK and asks to generate test cases → **đọc RSD trực tiếp, KHÔNG yêu cầu tạo test design trước**
- User provides a mindmap file (.txt or .md exported from .gmind) and asks to generate test cases
- User uploads mindmap + optional RSD/PTTK for test case generation
- User provides a feature folder containing .pdf files → scan và đọc trực tiếp

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## ⚠️ Đọc file PDF — CHỈ dùng Read tool

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

1. **Check catalog** — look for `catalog/` directory at project root (contains `api/`, `frontend/`, `mobile/`)
2. **Check & READ AGENTS.md** — look for `AGENTS.md` at project root (project-level rules)
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
- Use skill-level `AGENTS.md` (default rules)
- Inform user: "Project chưa có AGENTS.md. Đang dùng rules mặc định."

**⚠️ CRITICAL: Project AGENTS.md rules take precedence when explicitly defined.** Every subsequent step (mode detection, extraction, generation, verification) MUST check `projectRules` and apply them. If a project rule is explicitly defined, use that rule.

**If catalog exists but has no examples (empty api/ and frontend/):**
- Warn user: "Catalog chưa có examples. Output có thể không chính xác format. Bạn có muốn thêm CSV examples trước không?"
- Proceed with skill references as fallback

**If `excel_template/structure.json` does not exist:**
- Check if `excel_template/template.xlsx` exists
- If yes → run `python <skills-root>/test-case-generator/scripts/extract_structure.py` to generate it
- If no → inform user: "Chưa có template. Bạn cần đặt file template.xlsx vào excel_template/"

### Step 1: Check Input Type

**If user provides a feature folder name** (e.g., `/generate-test-case feature-1` or `sinh test case cho feature-1`):
1. Look inside `<feature-name>/` folder for input documents automatically:
   - Scan for document files: `.pdf`, `.docx`, `.doc`, `.md`, `.txt` — identify RSD and PTTK by filename
   - Also check for existing `test-design.md` (mindmap already generated)
2. **DO NOT ask** the user for file paths — use whatever documents are found in the folder
3. **If folder is empty** → scan toàn bộ project root cho document files liên quan đến feature name. Tài liệu có thể nằm ở thư mục khác.
4. If truly no documents found anywhere → inform user: "Không tìm thấy tài liệu RSD/PTTK. Hãy cung cấp đường dẫn hoặc upload file."

| Input found | Flow |
|-------------|------|
| Document files (`.pdf`, `.docx`, `.md`...) found | **Direct flow** — đọc trực tiếp, go to Step 2. Nếu có `test-design.md` thì dùng làm **tham khảo bổ sung**, KHÔNG bắt buộc |
| Only `test-design.md` (no other docs) | **Mindmap-only flow** — dùng mindmap, go to Step 2 |
| Mindmap (.md/.txt) provided directly by user | **Mindmap flow** — go to Step 2 |
| RSD + PTTK provided directly by user | **Direct flow** — đọc trực tiếp, go to Step 2 |

**⚠️ QUAN TRỌNG — LUÔN đọc RSD/PTTK nếu có:**
- Khi folder có tài liệu (pdf/docx/md) VÀ `test-design.md` → **ĐỌC TÀI LIỆU GỐC LÀ CHÍNH**, dùng test-design.md làm tham khảo
- Khi folder chỉ có tài liệu → đọc trực tiếp, tự sinh cấu trúc test cases
- Khi user cung cấp RSD/PTTK trực tiếp → đọc ngay, KHÔNG yêu cầu user tạo/upload test design trước
- **KHÔNG BAO GIỜ** yêu cầu user "hãy tạo test design trước" hay "upload mindmap" khi đã có RSD/PTTK
- **Khi folder rỗng** → tìm tài liệu ở thư mục khác trong project (tài liệu có thể nằm ở root hoặc folder khác)

**Direct flow (có RSD/PTTK):**
1. Đọc RSD/PTTK trực tiếp — extract tất cả fields, business logic, error codes, constraints
2. Nếu có `test-design.md` → đọc thêm để lấy cấu trúc sections (nhưng data field vẫn từ RSD/PTTK)
3. Nếu không có `test-design.md` → tự tạo cấu trúc sections dựa trên RSD content
4. Go to Step 2

**Mindmap-only flow (chỉ có mindmap, không có RSD):**
1. Dùng mindmap làm nguồn chính
2. Sinh test cases theo cấu trúc mindmap — nhưng sẽ thiếu field constraints cụ thể
3. Warn user: "Không có RSD/PTTK — test cases sẽ thiếu thông tin maxLength, data types, business logic cụ thể."

### Step 2: Determine Mode

| Mindmap content | Mode | Output |
|-----------------|------|--------|
| API name + endpoint references | API | JSON test cases for API |
| Screen name + UI section names | Frontend | JSON test cases for Frontend |

#### Heuristic-first detection (rule-based, no LLM needed)

Apply these checks on the **first 10 lines** of the mindmap:

| Heuristic | Mode | Confidence |
|-----------|------|------------|
| Line 1 matches `(GET\|POST\|PUT\|DELETE\|PATCH)\s+/` or contains API endpoint pattern | API | High |
| Sections include `case common` + `validate` + field names are UPPER_SNAKE_CASE (PAR_TYPE, REG_CHANNEL) | API | High |
| Line 1 starts with `WEB_` or contains `Danh mục >`, `Màn hình` | Frontend | High |
| Sections include `giao diện chung`, `lưới dữ liệu`, `chức năng` | Frontend | High |

**Decision logic:**
1. If heuristic returns **High confidence** → use that mode, skip LLM detection
2. If **no heuristic matches** or **conflicting signals** → fallback to LLM to read mindmap and determine mode

**Clues for API mode (LLM fallback):** First line is API name, sections include "case common", "phân quyền", "validate", field names are request params (PAR_TYPE, REG_CHANNEL...).

**Clues for Frontend mode (LLM fallback):** First line is screen name (e.g., "WEB_BO_Danh mục > ..."), sections include "giao diện chung", "phân quyền", "validate", "lưới dữ liệu", "chức năng".

### Step 3: Load Rules & References

**Step 3a: Apply project AGENTS.md rules (loaded in Step 0)**

Before loading any references, review `projectRules` from Step 0. Project rules affect:
- **How to generate each field** — project may override format, writing style, section assignment
- **Quality/style constraints** — project may define custom forbidden phrases, naming conventions, writing style
- **Test case granularity** — project may require splitting cases differently (e.g., "tách riêng từng field", "buttons vào phần chức năng")
- **Image analysis behavior** — project may require analyzing images before reading RSD
- **Account/credentials** — project may define custom test account

All rules from project AGENTS.md apply as overrides throughout the remaining steps. If project AGENTS.md explicitly defines a rule, use that rule.

**Step 3b: Load skill references (mode-specific)**

**Load ONLY the references needed for the detected mode.** Do NOT load all references upfront.

#### Resolve SKILL_SCRIPTS path

Scripts are installed alongside this SKILL.md file in a `scripts/` subdirectory. Try these methods in order:

**Method 1 — Recursive find from project root:**
```bash
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/test-case-generator/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
echo "SKILL_SCRIPTS=$SKILL_SCRIPTS"
```

**Method 2 — Direct path check (if Method 1 returns empty):**
```bash
for d in \
  ".claude/skills/test-case-generator/scripts" \
  ".cursor/skills/test-case-generator/scripts" \
  ".windsurf/skills/test-case-generator/scripts" \
  ".roo/skills/test-case-generator/scripts" \
  ".kiro/skills/test-case-generator/scripts"; do
  [ -f "$d/search.py" ] && SKILL_SCRIPTS="$d" && break
done
echo "SKILL_SCRIPTS=$SKILL_SCRIPTS"
```

**Method 3 — Global npm (if Method 2 returns empty):**
```bash
npm_root=$(npm root -g 2>/dev/null)
[ -n "$npm_root" ] && [ -f "$npm_root/test-genie/test-case-generator/scripts/search.py" ] && \
  SKILL_SCRIPTS="$npm_root/test-genie/test-case-generator/scripts"
```

**Method 4 — CRITICAL FALLBACK (if all above fail): Read reference files directly**

If `SKILL_SCRIPTS` is still empty after all methods, **DO NOT skip loading references**. Instead, read the reference files directly using the Read tool (or equivalent file reading capability):

```
READ: <skills-dir>/test-case-generator/references/priority-rules.md
READ: <skills-dir>/test-case-generator/references/quality-rules.md
READ: <skills-dir>/test-case-generator/references/output-format.md
READ: <skills-dir>/test-case-generator/references/api-test-case.md      (API mode only)
READ: <skills-dir>/test-case-generator/references/fe-test-case.md        (Frontend mode only)
```

Where `<skills-dir>` is wherever the `.claude/`, `.cursor/`, etc. directory is found. Try common paths:
- `.claude/skills/`
- `.cursor/skills/`
- `.windsurf/skills/`

**⚠️ NEVER proceed without loading references.** The output-format and mode-specific rules are mandatory. If you truly cannot find any reference file, inform the user: "Không tìm thấy skill scripts. Bạn có thể chạy `test-genie init` để khởi tạo lại không?"

**Note:** `search.py` auto-detects the project root by looking for `catalog/` or `AGENTS.md`. You can also pass `--project-root /path/to/project` explicitly.

#### Load by mode (lazy-load)

**Always load first (both modes):**
```bash
python $SKILL_SCRIPTS/search.py --ref priority-rules
python $SKILL_SCRIPTS/search.py --ref output-format
python $SKILL_SCRIPTS/search.py --ref quality-rules
```

**API mode — load this only:**
```bash
python $SKILL_SCRIPTS/search.py --ref api-test-case
```

**Frontend mode — load these:**
```bash
python $SKILL_SCRIPTS/search.py --ref fe-test-case
```

Ngoài ra, **bắt buộc load `field-templates.md`** từ test-design-generator (skill chị em):
```bash
# Resolve path to field-templates.md
for d in \
  ".claude/skills/test-design-generator/references" \
  ".cursor/skills/test-design-generator/references" \
  ".windsurf/skills/test-design-generator/references" \
  ".roo/skills/test-design-generator/references" \
  ".kiro/skills/test-design-generator/references"; do
  [ -f "$d/field-templates.md" ] && FIELD_TEMPLATES="$d/field-templates.md" && break
done

# Nếu không tìm được qua scripts, dùng npm global:
[ -z "$FIELD_TEMPLATES" ] && {
  npm_root=$(npm root -g 2>/dev/null)
  f="$npm_root/test-genie/test-design-generator/references/field-templates.md"
  [ -f "$f" ] && FIELD_TEMPLATES="$f"
}

# Fallback: đọc trực tiếp bằng Read tool
# Nếu vẫn không tìm được → đọc file field-templates.md bằng Read tool tại path phổ biến nhất
cat "$FIELD_TEMPLATES"
```

> **Tại sao cần field-templates.md?** File này là nguồn chuẩn định nghĩa ĐẦY ĐỦ cases cho từng loại field frontend. `fe-test-case.md` chỉ chứa format/rules — field-templates.md chứa DANH SÁCH cases. Thiếu file này → validate cases bị thiếu emoji, XSS, SQL injection, minLength, format validation.

> **Why lazy-load?** Loading all references regardless of mode wastes tokens on rules that won't be used. Only load what the detected mode requires.

#### Extract test account from catalog

After loading references, extract the test account/password to use in preConditions:

**Priority order:**
1. **Project AGENTS.md** (highest) — check for `## Test Account` section with `testAccount:` value
2. **Catalog examples** — read 1-2 CSV files from `catalog/{mode}/`, extract the account used in preConditions (look for `account:` pattern in preConditions column)
3. **Default** — `164987/ Test@147258369`

**How to extract from catalog:**
```bash
# Quick extract: find account pattern in first catalog CSV
head -20 catalog/frontend/*.csv 2>/dev/null | grep -oP 'account:\s*\K[^"\\]+' | head -1
```

Or read the first catalog CSV and look for the login/account pattern in preConditions.

**Store the resolved account** for use in all test case generation batches. The account MUST be consistent across all test cases in the output.

**Cách diễn đạt, hành văn:** Ngoài account, toàn bộ cách viết preConditions, step, expectedResult cũng phải **tuân theo catalog**. Catalog là nguồn chuẩn cho style/wording — nếu catalog viết theo cách nào thì output phải theo đúng cách đó.

#### Search examples & utilities

```bash
# Search API examples (searches catalog/api/ in project root)
python $SKILL_SCRIPTS/search.py "search list validate" --domain api

# Search Frontend examples (searches catalog/frontend/ in project root)
python $SKILL_SCRIPTS/search.py "giao dien chung phan quyen" --domain frontend

# List all available references
python $SKILL_SCRIPTS/search.py --list-refs

# List all available examples
python $SKILL_SCRIPTS/search.py --list

# Read full content of top match
python $SKILL_SCRIPTS/search.py "validate string field" --domain api --full
```

### Step 4: Read the Mindmap

Parse the mindmap structure:
- **Line 1**: API name / Screen name → used in `preConditions`
- **## headings**: Test suites → `testSuiteName`
- **### headings**: Sub-sections / Field names → grouping
- **- bullet items**: Test case descriptions → `testCaseName`

### Step 5: Extract Field & Body Context

If RSD/PTTK files are provided:

**API Mode:**
1. Find the API endpoint section in PTTK (preferred) or RSD (fallback)
2. Extract: field names, data types, required/optional, maxLength, format constraints, example values
3. Build complete request body JSON with ALL required fields having concrete values
4. Extract response templates (SUCCESS + ERROR) once — inject into all batches

**Frontend Mode:**
1. Find the screen/API section in PTTK (preferred) or RSD (fallback)
2. Extract: field names, types, placeholder, maxLength, API endpoints, DB mappings, enum values
3. Use extracted details to enrich validate test case generation

Priority rules: see `AGENTS.md` or `--ref priority-rules`.

### Step 5b: Validate Documents & Ask Clarification

After extraction, check for issues and **proactively ask user** before proceeding:

**Missing information (MUST ask):**
- Cannot find the exact API/screen in PTTK → ask: "PTTK có nhiều API, không tìm thấy endpoint `{endpoint}`. Bạn muốn dùng API nào?" (list candidates)
- Mindmap has field names not found in RSD/PTTK → ask: "Mindmap có field `{name}` nhưng không tìm thấy trong RSD/PTTK. Bỏ qua hay sinh test case với thông tin có sẵn?"
- No response body structure in any document → ask: "Không tìm thấy cấu trúc response body. Bạn có tài liệu bổ sung không?"
- Mindmap section names don't match expected format → ask: "Section `{name}` không khớp format chuẩn. Đây là validate, luồng chính, hay section khác?"

**Conflicts between documents (MUST ask):**
- Mindmap field name differs from PTTK/RSD → ask: "Mindmap gọi là `{mm_name}` nhưng PTTK gọi là `{pttk_name}`. Dùng tên nào cho testCaseName?"
- PTTK says required but RSD says optional → ask: "Field `{name}`: PTTK = required, RSD = optional. Theo tài liệu nào?"
- Mindmap has test cases that contradict RSD logic → ask: "Mindmap mô tả `{case}` nhưng RSD logic ngược lại. Theo tài liệu nào?"

**Suspicious/unclear content (SHOULD ask):**
- Mindmap has very few test cases for a complex section → ask: "Section `{name}` chỉ có {n} cases nhưng có {m} fields. Bạn muốn sinh thêm cases không?"
- Business logic in RSD is ambiguous → ask: "Logic `{description}` không rõ ràng. Expected result cụ thể là gì?"
- Duplicate test case names in mindmap → ask: "Có {n} test cases trùng tên `{name}`. Giữ tất cả hay deduplicate?"

**DO NOT ask if:**
- Information can be reasonably inferred from context
- Priority rules already define the answer (e.g., PTTK wins for field definitions)
- Mindmap is clear and matches RSD/PTTK

### Step 5c: Business Logic Extraction — Inventory

**Before generating any test cases**, read RSD/PTTK và extract toàn bộ business logic thành structured inventory. Đây là checklist bắt buộc — mọi item phải có ≥1 test case trong luồng chính.

Output dưới dạng internal JSON (không show cho user):

```json
{
  "apiName": "string — tên API",
  "endpoint": "METHOD /path",
  "errorCodes": [
    {
      "code": "PCER_UPLOAD_001",
      "desc": "exact message từ RSD — copy nguyên văn",
      "triggerCondition": "điều kiện cụ thể để trigger lỗi này"
    }
  ],
  "businessRules": [
    {
      "id": "BR1",
      "type": "branch",
      "condition": "uploadType = 1",
      "trueBranch": "INSERT vào PROMOTION_CUSTOMER_PENDING với action=ADD",
      "falseBranch": null
    },
    {
      "id": "BR2",
      "type": "branch",
      "condition": "uploadType = 2",
      "trueBranch": "INSERT vào PROMOTION_CUSTOMER_PENDING với action=DELETE",
      "falseBranch": null
    },
    {
      "id": "BR3",
      "type": "condition",
      "condition": "rows > PROMO_CUS_MAX_ROW",
      "effect": "error PCER_UPLOAD_003"
    }
  ],
  "modes": [
    { "name": "Thêm mới", "triggerValue": "uploadType=1", "expectedAction": "INSERT pending records" },
    { "name": "Xoá", "triggerValue": "uploadType=2", "expectedAction": "mark for deletion" }
  ],
  "dbOperations": [
    {
      "table": "PROMOTION_CUSTOMER_PENDING",
      "operation": "INSERT",
      "when": "upload thành công",
      "fieldsToVerify": ["UPLOAD_TYPE", "DOMAIN_TYPE", "FEE_SERVICE", "STATUS", "FILE_NAME", "BATCH_ID"]
    }
  ],
  "externalServices": [
    {
      "name": "S3",
      "callPoint": "sau khi validate file thành công",
      "onSuccess": "lưu file, tiếp tục insert DB",
      "onFailure": "error code theo RSD (vd: code=2)",
      "onTimeout": "error code theo RSD"
    }
  ],
  "statusTransitions": [
    { "from": "N/A", "to": "WAITING_PREVIEW (1)", "trigger": "upload thành công" }
  ],
  "decisionCombinations": [
    { "conditions": {"uploadType": 1, "domainType": "1", "feeServiceExists": true}, "expected": "success" },
    { "conditions": {"uploadType": 1, "domainType": "1", "feeServiceExists": false}, "expected": "PCER_009" },
    { "conditions": {"uploadType": 2, "domainType": "2", "feeServiceExists": true}, "expected": "success delete" }
  ]
}
```

**Hướng dẫn extract từng mục:**

| Mục | Lấy từ đâu trong RSD/PTTK | Lưu ý |
|-----|--------------------------|-------|
| `errorCodes[]` | Bảng mã lỗi — đọc **toàn bộ bảng**, không bỏ sót dòng nào | Copy **exact** message, không paraphrase. Thêm `"section": "validate"\|"main"` để biết thuộc batch nào |
| `businessRules[]` | Mô tả luồng xử lý, điều kiện if/else | Mỗi nhánh = 1 rule riêng |
| `modes[]` | Các mode/loại hoạt động của API | Ví dụ: create/update/delete/search |
| `dbOperations[].fieldsToVerify` | Bảng DB mapping trong PTTK — đọc **tất cả cột** trong bảng | **BẮT BUỘC** list đủ 100% fields, kể cả auto-generate (ID, CREATED_TIME, CREATED_USER) và derived fields (BRANCH = bdsCode + "000") |
| `externalServices[]` | Tích hợp S3, queue, third-party | Phải có `onFailure`, `onTimeout`, và `rollbackBehavior` |
| `statusTransitions[]` | Status field, flow diagram | Valid + invalid transitions |
| `decisionCombinations[]` | Khi ≥2 conditions cùng ảnh hưởng output | Prune impossible combos |

**Quy tắc bổ sung cho errorCodes extraction:**

Mỗi error code phải có field `"section"` để biết nó thuộc BATCH nào:
```json
{ "code": "PCER_UPLOAD_004", "desc": "File upload không đúng file mẫu", "triggerCondition": "file thiếu cột bắt buộc", "section": "validate" },
{ "code": "PCER_UPLOAD_005", "desc": "Tồn tại dòng trống dữ liệu", "triggerCondition": "file có blank row", "section": "validate" },
{ "code": "PCER_UPLOAD_006", "desc": "File upload chứa phần mềm không hợp lệ", "triggerCondition": "file có macro/virus", "section": "validate" },
{ "code": "2", "desc": "Có lỗi xảy ra trong quá trình xử lý", "triggerCondition": "S3 error hoặc DB error", "section": "main" }
```

**Quy tắc bổ sung cho dbOperations.fieldsToVerify:**

Phải bao gồm **tất cả** — kể cả:
- Fields do system tự generate: `ID`, `CREATED_TIME`, `CREATED_USER`
- Fields có logic derived: `BRANCH = bdsCode + "000"`, `STATUS = 1`
- Fields lưu từ input: `FILE_NAME`, `UPLOAD_TYPE`, `DOMAIN_TYPE`, `FEE_SERVICE`
- Fields từ S3 response: `S3_FILE_KEY`, `S3_FILE_PATH`
- Counter fields: `TOTAL_UPLOAD`

**Quy tắc bổ sung cho externalServices rollback:**
```json
{
  "name": "S3",
  "onFailure": "trả error code 2",
  "onTimeout": "trả error code 2",
  "rollbackBehavior": "KHÔNG INSERT vào DB — verify bằng SELECT COUNT(*) = 0 sau khi S3 fail"
}
```

**⚠️ CRITICAL:** Không được sinh test cases cho đến khi extraction JSON hoàn chỉnh. Đây là checklist sẽ dùng để verify coverage ở Step 6b.

### Step 5d: Inventory Verification Gate

**Sau khi hoàn thành Step 5c, PHẢI báo cáo cho user (bắt buộc, không được skip):**

```
📋 Business Logic Inventory đã extract:
- Error codes:        {N} (list: PCER_001, PCER_002, ...)
- Business rules:     {N} if/else branches (list: BR1, BR2, ...)
- Modes/flows:        {N} (list: Thêm mới, Xoá, ...)
- DB operations:      {N} tables (list: TABLE_A INSERT, TABLE_B UPDATE, ...)
- External services:  {N} (list: S3, Queue, ...)
- Status transitions: {N}
- Decision combos:    {N}
```

**Nếu bất kỳ category nào = 0 VÀ tài liệu có khả năng chứa thông tin đó → HỎI USER xác nhận trước:**
> "Không tìm thấy {category} trong tài liệu. Tài liệu có đề cập không? (có thể tôi đọc bỏ sót phần nào đó)"

**Nếu tất cả categories đều = 0:** Dừng lại ngay, hỏi user:
> "Không extract được business logic nào từ tài liệu. Bạn có thể chỉ rõ section nào trong tài liệu chứa luồng xử lý / error codes / DB mapping không?"

### Step 6: Generate Test Cases in Batches

#### Step 6a: Load Catalog Style Examples (MANDATORY)

**⚠️ CRITICAL — Catalog examples là nguồn chuẩn cho style/wording. PHẢI load trước khi sinh bất kỳ test case nào.**

Trước khi sinh test cases, search catalog để lấy 2-3 examples thực tế. Đây là **style reference chính** — output PHẢI follow đúng cách viết của catalog, KHÔNG follow cách viết của ví dụ trong references.

```bash
# Search catalog examples matching the current feature/section
python $SKILL_SCRIPTS/search.py "{feature_keyword}" --domain {mode} --full --top 3
```

**Nếu catalog có examples:**
1. Đọc 2-3 examples đầu tiên (full content: preConditions, steps, expectedResults)
2. **Extract style patterns** từ catalog:
   - **testSuiteName convention** — catalog chia suite thế nào? Ví dụ: field sub-suites `"Textbox: Tên cấu hình SLA"` hay chung `"Kiểm tra validate"`?
   - **preConditions format** — catalog viết preconditions thế nào? (format Đ/k, numbering, wording, số dòng, chi tiết level)
   - **steps format** — catalog viết steps thế nào? (động từ, cấu trúc câu, chi tiết level)
   - **expectedResults format** — catalog viết expected results thế nào? (format, wording, numbering)
   - **testCaseName convention** — catalog đặt tên test case thế nào? (prefix, wording)
   - **Cấu trúc phân nhóm** — catalog nhóm test cases theo trường/field riêng hay chung?
3. Lưu các patterns này làm `catalogStyle` — dùng cho TOÀN BỘ batches
4. **Khi generate:** "Viết theo đúng style/wording/structure của catalog examples dưới đây. References chỉ cung cấp rules/logic — KHÔNG copy format/wording/structure từ ví dụ trong references."

> **⚠️ QUAN TRỌNG:** `catalogStyle` override TOÀN BỘ format mặc định trong references. Nếu catalog dùng:
> - Field sub-suites → dùng field sub-suites (bỏ qua rule "KHÔNG có field sub-suites" trong refs)
> - PreConditions 1 dòng → dùng 1 dòng (bỏ qua format multi-line trong refs)
> - Steps/ExpectedResults format khác → follow catalog format
> **References chỉ cung cấp: LOẠI cases nào cần check (rules/logic). Catalog quyết định: VIẾT như thế nào (format/style).**

**Nếu catalog KHÔNG có examples (rỗng):**
- Warn user: "Catalog chưa có examples, sẽ dùng format mặc định từ references."
- Fall back to reference examples as style guide

**Quy tắc ưu tiên style:**
1. **Project AGENTS.md** — nếu có quy định style cụ thể → override tất cả
2. **Catalog examples** — style/wording chính, PHẢI follow
3. **References (fe-test-case.md, api-test-case.md)** — chỉ dùng cho RULES và LOGIC, KHÔNG dùng format/wording mẫu

**Ví dụ áp dụng catalog style:**

Nếu catalog viết preConditions:
```
Đ/k1: Vào màn hình:
1. Đăng nhập vào hệ thống BO bằng tài khoản: 164987/ Test@147258369
2. Truy cập màn hình: Danh mục > Tần suất thu phí
```

Thì output PHẢI viết:
```
Đ/k1: Vào màn hình:
1. Đăng nhập vào hệ thống BO bằng tài khoản: 164987/ Test@147258369
2. Truy cập màn hình: Danh mục > Tần suất thu phí
```

KHÔNG được viết theo format ví dụ trong references (nếu khác):
```
Đ/k1: Vào màn hình:
1. Người dùng đăng nhập thành công BO trên Web với account: 164987/ Test@147258369
2. Tại sitemap, người dùng truy cập màn hình Danh mục > Tần suất thu phí
```

→ Khác cách viết = SAI. Phải match **exact wording style** của catalog.

---

Split mindmap into 3 batches, process sequentially:

**Quy tắc testSuiteName — Catalog convention ưu tiên:**

> **⚠️ Nếu catalog có convention riêng cho testSuiteName → PHẢI follow catalog.** Danh sách dưới đây là fallback.
>
> **Catalog convention phổ biến:**
> - BATCH 2 Frontend dùng **field sub-suites**: `"{FieldType}: {FieldName}"` (VD: `"Textbox: Tên cấu hình SLA"`, `"DatePicker: Ngày hiệu lực"`)
> - BATCH 2 API dùng: `"Kiểm tra trường {fieldName}"`
>
> **Fallback (khi catalog không có examples):**
> - API: `"Kiểm tra các case common"`, `"Kiểm tra phân quyền"`, `"Kiểm tra trường {fieldName}"` (BATCH 2), `"Kiểm tra luồng chính"`, `"Kiểm tra timeout"`
> - Frontend: `"Kiểm tra giao diện chung"`, `"Kiểm tra phân quyền"`, `"Kiểm tra validate"` hoặc field sub-suites (BATCH 2), `"Kiểm tra chức năng"`, `"Kiểm tra lưới dữ liệu"`, `"Kiểm tra phân trang"`, `"Kiểm tra timeout"`
> - SAI: `"Kiểm tra bảo mật"`, `"Kiểm tra lỗi nghiệp vụ"`, `"Kiểm tra security"`, `"String : id"`, `"file: MultipartFile (Required)"`, v.v.

**BATCH 1 — Pre-validate sections:**
- All ## sections BEFORE "Kiểm tra validate" (e.g., common cases, permissions)
- Force testSuiteName = section name
- Instruction: "Chỉ sinh test cases cho section: {name}. KHÔNG sinh cases cho validate hay luồng chính."

**Post-batch checkpoint — BATCH 1:**
- Mỗi section đã được generate đủ test cases?
  - "Kiểm tra các case common" → có Method + URL test cases?
  - "Kiểm tra phân quyền" → có "không có quyền" + "có quyền"?
- Item nào thiếu → tự APPEND vào output ngay, không hỏi user.

**BATCH 2 — Validate section (grouped fields):**
- "Kiểm tra validate" and all ### subsections inside
- **Group 3-5 fields per sub-batch** instead of 1 field per sub-batch to reduce LLM round-trips
- **testSuiteName per field:** Nếu `catalogStyle` có field sub-suites (VD: `"Textbox: Tên cấu hình SLA"`) → mỗi field PHẢI có testSuiteName riêng theo format catalog: `"{FieldType}: {FieldName}"`. Nếu catalog không có → dùng `"Kiểm tra validate"` cho tất cả.
- Instruction per sub-batch: "Sinh test cases validate cho các fields sau: {field_1}, {field_2}, {field_3}. Mỗi field xử lý riêng biệt, KHÔNG trộn test cases giữa các fields. testSuiteName = theo catalog convention."

**Grouping rules:**
- Group fields with **similar types** together (e.g., 3 textbox fields in 1 call, 2 combobox + 1 dropdown in 1 call)
- If a field has **complex validation** (nhiều rule đặc biệt, cross-field dependencies) → tách riêng 1 sub-batch
- Maximum 5 fields per sub-batch — nếu nhiều hơn 5 thì chia thêm sub-batch
- Each sub-batch MUST include: field names, types, constraints, and request body context

> **Why group?** Per-field sub-batch gọi LLM N lần (mỗi lần re-inject context). Gộp 3-5 fields giảm xuống N/4 calls, tiết kiệm overhead context đáng kể mà vẫn đủ rõ ràng cho LLM xử lý.

**Minimum case count per field type — BATCH 2 enforcement:**

| Field type | Min cases | Cases PHẢI có |
|-----------|-----------|----------------|
| String/Textbox (API) | ≥15 | empty, null, maxLen-1, maxLen, maxLen+1, XSS, SQL injection, emoji, wrong type (bool/array/obj) |
| Number/Integer (API) | ≥12 | empty, null, negative, decimal, leading-zero, string, XSS, SQL injection |
| Date (API) | ≥10 | empty, null, correct format, wrong format, invalid date, past/present/future |
| Array (API) | ≥8 | missing, null, empty `[]`, `[{}]`, wrong type (string/number/bool/object) |
| Textbox (Frontend) | ≥18 | default display, placeholder, icon X (hiển thị + clear), số, chữ, special chars, emoji, XSS, SQL, space đầu/cuối, all-space, maxLen-1, maxLen, maxLen+1 |
| Combobox (Frontend) | ≥15 | default, placeholder, required, API timeout, API error, API rỗng, loading state, select 1, search keywords, hiển thị sau khi chọn |
| Simple Dropdown (Frontend) | ≥8 | default, placeholder, danh sách values, chọn từng value, icon X, required |
| Toggle (Frontend) | ≥4 | default, toggle A→B, toggle B→A, disabled state |

**Sau khi sinh xong mỗi field, kiểm tra:**
> Nếu số cases sinh ra < min_cases cho field type đó → tự append các cases còn thiếu trước khi chuyển sang field tiếp theo. KHÔNG được để thiếu.

**Post-batch checkpoint — BATCH 2:**
- Mỗi field trong inventory đã có test cases? Danh sách field nào chưa có → APPEND.
- Mỗi field có ≥ min_cases theo type? Field nào < min_cases → tự APPEND cases còn thiếu.
- Frontend: mỗi combobox đã có API timeout/error/rỗng cases? Chưa có → APPEND.

**BATCH 3 — Post-validate sections:**
- All ## sections AFTER "Kiểm tra validate" (e.g., grid, functionality, timeout)
- Force testSuiteName = section name, maxTokens: 65536
- **Instruction PHẢI include toàn bộ inventory từ Step 5c** (không được dùng instruction ngắn chung chung):

```
Sinh test cases cho luồng chính. BẮT BUỘC apply đủ 6 kỹ thuật dựa trên inventory sau:

1. Happy paths — sinh ≥1 test cho TỪNG mode/flow: {list modes từ inventory}
2. Branch coverage — sinh test TRUE + test FALSE cho TỪNG if/else: {list branches từ inventory}
3. Decision table — sinh test cho TỪNG combination có expected result khác nhau: {list decisionCombinations từ inventory}
4. Error code coverage — sinh ≥1 test trigger TỪNG error code (copy exact message từ RSD): {list errorCodes từ inventory}
5. DB verification — sinh test verify data TỪNG table/operation: {list dbOperations từ inventory}
6. External service failures — sinh test onFailure + onTimeout cho TỪNG external service: {list externalServices từ inventory}

KHÔNG được bỏ sót bất kỳ item nào. Inventory có N items → output phải cover ≥N items.
```

**Post-batch checkpoint — BATCH 3:**
- API: Đã cover đủ 6 kỹ thuật? Kiểm tra nhanh:
  - [ ] TỪNG mode trong `inventory.modes[]` → có ≥1 happy path?
  - [ ] TỪNG branch trong `inventory.businessRules[]` → có test TRUE + FALSE?
  - [ ] TỪNG error code trong `inventory.errorCodes[]` (section="main") → có test với exact message?
  - [ ] TỪNG operation trong `inventory.dbOperations[]` → có test SELECT verify tất cả fields?
  - [ ] TỪNG service trong `inventory.externalServices[]` → có test onFailure + onTimeout?
  - [ ] TỪNG combo trong `inventory.decisionCombinations[]` → có test với exact combination?
  - Item nào thiếu → tự APPEND vào suite tương ứng ngay.
- Frontend: Đã cover đủ? Kiểm tra nhanh:
  - [ ] TỪNG button/action → có test success + fail + permission?
  - [ ] TỪNG enable/disable rule → có test cả 2 state?
  - [ ] TỪNG combobox/dropdown → có test API timeout/error/rỗng?
  - Item nào thiếu → tự APPEND.

**After all batches:** Deduplicate testCaseNames (case-insensitive, keep first occurrence).

Generate following rules loaded via `--ref api-test-case` (API) or `--ref fe-test-case` (Frontend).

**⚠️ REMINDER mỗi batch:** Inject `catalogStyle` (từ Step 6a) vào prompt. Format instruction cho mỗi batch:
> "Viết test cases theo đúng style/wording từ catalog examples sau. References chỉ cung cấp rules — KHÔNG copy wording/format từ ví dụ trong references nếu khác catalog."
> [Paste 1-2 catalog examples here as style reference]

### Step 6b: Final Coverage Summary

**Coverage đã được check per-batch (Step 6 Post-batch checkpoints). Bước này chỉ tổng hợp kết quả.**

**PHẢI hiển thị coverage summary cho user (bắt buộc, không skip):**

```
📊 Coverage Report:
✓ BATCH 1: {N}/{N} sections covered
✓ BATCH 2: {N}/{N} fields covered, {M} fields < min_cases → appended
✓ BATCH 3 (API): {N}/{N} modes, {N}/{N} branches, {N}/{N} error codes, {N}/{N} DB ops, {N}/{N} external services
✓ BATCH 3 (Frontend): {N}/{N} actions, {N}/{N} enable/disable rules
✅ Tổng: {total} test cases | Auto-appended: {M} cases
```

> **Target:** Mọi item trong inventory đều có ít nhất 1 test case. 5% còn lại là undocumented implicit behaviors — chấp nhận được.

### Step 7: Output to JSON File

Output is a **JSON file** saved to the test case folder. Flow:

1. **Generate** JSON array of test case objects
2. **Save** to `<tên-test-case>/test-cases.json`
3. **Report** result and guide user to upload if needed

#### 7a: Generate JSON Array

Generate a JSON array where each element is one test case object. Use these standard field names:

| Field | Description | Notes |
|-------|-------------|-------|
| `testSuiteName` | Test suite / group name | Triggers a suite header row on upload |
| `testCaseName` | Test case name | Required |
| `summary` | Summary (usually = testCaseName) | |
| `preConditions` | Pre-conditions + test data | Multiline with `\n` |
| `steps` | Test steps | Multiline with `\n` |
| `expectedResults` | Expected results | Multiline with `\n` |
| `result` | Test result | Default: `"PENDING"` |
| `priority` | Priority | `Low` / `Medium` / `High` |
| `externalId` | Test case ID | Usually `""` (auto-generated by formula) |
| `note` | Notes | Usually `""` |

Other fields (`details`, `status`, `executionType`, `keywords`, `specTitle`, `documentId`, `duration`, `testcaseLV1/2/3`, `testCaseId`, `testCaseTitle`, `testSteps`, `testResults`, `bugId`, `actualResult`) are also supported and will be mapped if the template has matching columns.

#### 7b: Save to JSON File

Save the JSON array to `<tên-test-case>/test-cases.json`:
- Pretty-print with `indent=2`, `ensure_ascii=False`
- The test case folder should already contain the input documents (RSD, PTTK) and optionally `test-design.md`

```bash
# Example: save to file
cat > "<tên-test-case>/test-cases.json" << 'EOF'
[
  {
    "testSuiteName": "Kiểm tra các case common",
    "testCaseName": "Method_Kiểm tra khi nhập sai method GET",
    ...
  }
]
EOF
```

#### 7c: Upload to Google Sheets (automatic)

After saving `test-cases.json`, **automatically** upload to Google Sheets. Do NOT stop and ask the user — run upload immediately.

**Pre-check (one-time):** If `excel_template/structure.json` does not exist, extract it first:
```bash
python $SKILL_SCRIPTS/extract_structure.py --project-root .
```

**Upload:**
```bash
python $SKILL_SCRIPTS/upload_gsheet.py <tên-test-case> --project-root .
```

**Prerequisites** (install if missing):
```bash
pip install google-auth-oauthlib google-auth google-api-python-client openpyxl
```

First run will open a browser for OAuth authentication — token is cached at `~/.config/test-genie/token.json` for reuse. Credentials fallback to bundled test-genie OAuth credentials if user's `credentials.json` is missing or invalid.

#### 7d: Return Result

Report both JSON file and Google Sheets link:

```
Đã lưu {testCaseCount} test cases tại `<tên-test-case>/test-cases.json`.
Suites: {suiteCount} | Test cases: {testCaseCount}
Google Sheets: {spreadsheetUrl}
```

If upload fails, still report the JSON file and show the error:
```
Đã lưu {testCaseCount} test cases tại `<tên-test-case>/test-cases.json`.
Upload Google Sheets thất bại: {error}
Để upload thủ công: python $SKILL_SCRIPTS/upload_gsheet.py <tên-test-case>
```

#### Upload Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `credentials.json not found` | File chưa có ở project root | Script tự dùng bundled credentials. Hoặc đặt file vào project root |
| `Missing dependencies` | Chưa cài thư viện | Chạy `pip install google-auth-oauthlib google-auth google-api-python-client` |
| `structure.json not found` | Chưa extract template | Chạy `python extract_structure.py` |
| Browser không mở | First-time auth trên server | Dùng `--no-browser` hoặc copy URL thủ công |
| Sharing fails | Org policy | File vẫn được tạo, share thủ công |

## Catalog Management

### Catalog Format

Catalogs are **CSV files** exported from the project spreadsheet. Each row = one test case.

Expected CSV columns (must match):
```
externalId,testSuiteName,testCaseName,preConditions,step,expectedResult,importance
```

### Add Examples to Catalog

1. Export test cases from Google Sheets / Excel as CSV (UTF-8)
2. Place in `catalog/api/` or `catalog/frontend/` at your project root
3. The search engine will automatically index new files

### List Available Examples

```bash
python <skills-root>/test-case-generator/scripts/search.py --list
```

## Project Structure

After running `test-genie init`, your project has this structure:

```
<project-root>/
├── node_modules/test-genie/           ← Skills live here (managed by npm)
│   ├── test-case-generator/
│   │   ├── SKILL.md                      ← Workflow instructions (this file)
│   │   ├── AGENTS.md                     ← Skill-level default rules
│   │   ├── references/                   ← Detailed rules (dev-managed)
│   │   │   ├── priority-rules.md
│   │   │   ├── api-test-case.md
│   │   │   ├── fe-test-case.md
│   │   │   ├── output-format.md
│   │   │   └── quality-rules.md
│   │   └── scripts/
│   │       ├── search.py                 ← Catalog search (auto-detects project root)
│   │       ├── extract_structure.py      ← Extract template → structure.json (one-time)
│   │       ├── upload_gsheet.py          ← Upload test-cases.json → Google Sheets
│   │       ├── google_auth.py            ← OAuth Desktop App authentication
│   │       ├── upload_template.py        ← Legacy: upload .xlsx → Google Drive
│   │       ├── detect_template.py        ← Legacy: detect columns from uploaded sheet
│   │       └── upload_to_sheet.py        ← Legacy: write data to existing sheet
│   └── test-design-generator/
│       └── ...
├── .claude/commands/                  ← Claude slash commands (auto-generated)
│   ├── generate-test-case.md
│   └── generate-test-design.md
├── catalog/                           ← Managed by user/tester
│   ├── api/                              ← API test case .csv examples
│   ├── frontend/                         ← Frontend test case .csv examples
│   └── mobile/                           ← Mobile test case examples
├── excel_template/
│   ├── template.xlsx                  ← Spreadsheet template
│   └── structure.json                 ← Template structure (generated by extract_structure.py)
├── <tên-test-case>/                   ← Per-feature test folder
│   ├── RSD.pdf                          ← Input: requirement spec
│   ├── PTTK.pdf                         ← Input: technical spec (optional)
│   ├── test-design.md                    ← Output: test design mindmap
│   └── test-cases.json                   ← Output: test cases JSON array
├── credentials.json                   ← OAuth Desktop App credentials (DO NOT COMMIT)
└── AGENTS.md                          ← Project-specific rules (user-managed)
```

## Key Format Differences: API vs Frontend

| Aspect | API Test Cases | Frontend Test Cases |
|--------|---------------|---------------------|
| `preConditions` | API endpoint + headers + body | Screen navigation path + login |
| `step` | API method/params changes | UI interactions (click, type, select) |
| `expectedResult` | HTTP status + JSON response | UI state (displayed, enabled, visible) |
| `testCaseName` | With prefix (e.g., "Phân quyền_...") | No prefix, direct from mindmap |
| External ID hint | API_1, API_2... | FE_1, FE_2... |
