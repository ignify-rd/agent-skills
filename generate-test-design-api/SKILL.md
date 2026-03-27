---
name: generate-test-design-api
description: Generate API test design mindmap from RSD/PTTK. For API endpoints only. Use when user says "sinh test design api", "tao mindmap api", "tạo test design api", or provides RSD/PTTK for an API endpoint.
---

# Test Design Generator — API Mode

Generate comprehensive test design documents (.md) for API endpoints from RSD and optional PTTK. Uses a searchable catalog of real test design examples to ensure output matches the correct format per project.

> **Scope**: This skill covers **test design** (mindmap output) for API endpoints only. It does NOT cover Frontend test design or test case generation (JSON/Excel output).

## When to Apply

- User provides RSD/PTTK for an API endpoint and asks to generate test design or mindmap
- User says "sinh test design api", "tạo test design api", "tao mindmap api"
- User uploads .pdf/.txt/.md files for API test design / mindmap generation

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
| Section assignment | Yes |
| Output JSON field names | No |
| Batch strategy (BATCH 1/2/3 split) | No |
| Field type dispatch table | No |
| Importance mapping | No |

**How it works:** Chat input from the user → Project `AGENTS.md` → Skill defaults. User says "viết ngắn gọn" → do it, even if it contradicts AGENTS.md or skill defaults.

## Workflow

### Step 0: Validate Project Setup & Load Project Rules

Before starting generation, check project structure and **load project-level rules**:

1. **Check catalog** — look for `catalog/` directory at project root (contains `api/` subdirectory)
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

**If catalog exists but has no examples (empty api/):**
- Warn user: "Catalog chưa có examples. Output có thể không chính xác format. Bạn có muốn thêm examples trước không?"
- Proceed with skill references as fallback

**⚠️ CRITICAL: Project AGENTS.md rules take precedence when explicitly defined.** Every subsequent step must check `projectRules` and apply them.

### Step 0b: Validate Required Inputs

**⚠️ STOP — Do NOT read any files or proceed until the user explicitly provides input file paths.**

Required inputs:
- **RSD file path** — required
- **PTTK file path** — optional
- **Output folder** — required (e.g. `feature-1/`), output will be saved as `<output-folder>/test-design-api.md`

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

### Step 1: Mode Detection (API Mode Only)

This skill is **API-only**. The input RSD must describe an API endpoint.

**Heuristic-first detection (rule-based, no LLM needed):**

| Heuristic | Confidence |
|-----------|------------|
| Title/heading matches `(GET\|POST\|PUT\|DELETE\|PATCH)\s+/` | High |
| Document contains `endpoint`, `request body`, `response body`, `API` (case-insensitive) in first 2 pages | Medium |
| Document contains `màn hình`, `screen`, `giao diện` | Low (may be mixed) |

**Decision logic:**
1. If heuristic returns **High confidence** → proceed as API
2. If document appears to be Frontend/RSD → inform user: "Tài liệu này là Frontend, không phải API. Sử dụng skill `generate-test-design-frontend` thay thế."
3. If **no heuristic matches** → ask user for clarification

### Step 2: Load Rules & References

**Step 2a: Apply project AGENTS.md rules (loaded in Step 0)**

Before loading any references, review `projectRules` from Step 0. Project rules affect:
- **Which sections to generate** — project may add/remove/rename sections
- **How to generate each section** — project may override format rules
- **Quality/style constraints** — project may define custom forbidden phrases, naming conventions, writing style
- **Test case granularity** — project may require splitting cases differently

All rules from project AGENTS.md apply as overrides throughout the remaining steps.

**Step 2b: Load skill references (API mode)**

#### Resolve SKILL_SCRIPTS path

```bash
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/generate-test-design-api/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
# Fallback: check .claude/skills, .cursor/skills, .windsurf/skills, .roo/skills, .kiro/skills, or global npm
```

If all fail → Read reference files directly from `<skills-dir>/generate-test-design-api/references/`. **⚠️ NEVER proceed without loading references.**

**Note:** `search.py` auto-detects the project root by looking for `catalog/` or `AGENTS.md`. You can also pass `--project-root /path/to/project` explicitly.

#### Load API references

**Always load first (API mode):**
```bash
python $SKILL_SCRIPTS/search.py --ref priority-rules
python $SKILL_SCRIPTS/search.py --ref quality-rules
python $SKILL_SCRIPTS/search.py --ref api-test-design
```

#### Search examples & utilities

```bash
# Search API examples by keyword (searches catalog/api/ in project root)
python $SKILL_SCRIPTS/search.py "search list api" --domain api

# Search format rules (skill-bundled, not in project catalog)
python $SKILL_SCRIPTS/search.py "common section status" --domain rules

# List all available references
python $SKILL_SCRIPTS/search.py --list-refs

# List all available examples
python $SKILL_SCRIPTS/search.py --list

# Read full content of top match
python $SKILL_SCRIPTS/search.py "export excel" --domain api --full
```

### Step 3: Read the Top-1 Matching Example

**Criteria chọn catalog example (theo thứ tự ưu tiên):**
1. **Keyword match chính xác nhất** — tên feature/API/screen trùng với request
2. **Cùng project** — ưu tiên examples từ project hiện tại (catalog trong project)
3. **Cùng domain** — ví dụ: upload API → ưu tiên upload, search API → ưu tiên search
4. **Gần đây nhất** — nếu nhiều candidates cùng quality

**Search strategy:**
```bash
# Tìm keyword chính xác trước
python $SKILL_SCRIPTS/search.py "{feature_keyword}" --domain api --full --top 1

# Nếu top 1 không phù hợp (domain khác, quality thấp) → thử top 2
python $SKILL_SCRIPTS/search.py "{feature_keyword}" --domain api --full --top 2
```

**Fallback:** Nếu top 1 và top 2 đều không phù hợp → thông báo user và dùng format mặc định từ references.

**⚠️ Catalog là nguồn WORDING & FORMAT cao nhất — cao hơn cả references:**
- Output PHẢI giống catalog về: cách đặt tên bullet, cách viết expected result, SQL format, response body format
- References cung cấp **danh sách cases cần gen** — KHÔNG copy wording từ references nếu catalog có cách viết khác
- **Nếu không tìm thấy catalog phù hợp** → thông báo user rồi dùng format mặc định từ references

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

### Step 4b: Validate Documents & Ask Clarification

After extraction, check for issues and **proactively ask user** before proceeding:

**Missing information (MUST ask):**
- RSD has no error codes or error code table is empty → ask: "RSD không có bảng mã lỗi. Bạn có tài liệu bổ sung không, hay bỏ qua phần error codes?"
- Cannot find the exact API/screen in PTTK → ask: "PTTK có nhiều API, không tìm thấy endpoint `{endpoint}`. Bạn muốn dùng API nào?" (list candidates)
- Field type unclear (RSD says "text" but no maxLength, no format) → ask: "Field `{name}` không có maxLength/format trong tài liệu. Giá trị mặc định nào phù hợp?"

**Conflicts between documents (MUST ask):**
- PTTK field name differs from RSD field name → ask: "PTTK gọi là `{pttk_name}` nhưng RSD gọi là `{rsd_name}`. Dùng tên nào?"
- PTTK says required but RSD says optional (or vice versa) → ask: "Field `{name}`: PTTK = required, RSD = optional. Theo tài liệu nào?"
- Different data types between documents → ask: "Field `{name}`: PTTK type = `{type1}`, RSD type = `{type2}`. Dùng type nào?"
- Response structure differs between PTTK and RSD → follow PTTK (per priority rules), but note the difference

**Suspicious/unclear content (SHOULD ask):**
- Business logic description is vague or uses ambiguous words ("có thể", "tùy trường hợp") → ask: "Logic `{description}` không rõ ràng. Cụ thể điều kiện là gì?"

**DO NOT ask if:**
- Information can be reasonably inferred (e.g., WRONG_METHODS from API method)
- Priority rules already define the answer (e.g., PTTK wins for field definitions)
- It's a formatting/style question covered by references

### Step 4c: Business Logic Inventory (API Mode)

**Before generating any section**, extract toàn bộ business logic và ghi vào `inventory.json` từng bước bằng script.

**Khởi tạo file:**
```bash
python $SKILL_SCRIPTS/inventory.py init \
  --file <output-folder>/inventory.json \
  --name "<API name>" \
  --endpoint "<METHOD /path>"
```

**Extraction rules:**
- `errorCodes[].section`: `"validate"` = thuộc "Kiểm tra validate"; `"main"` = thuộc "Kiểm tra luồng chính"
- `errorCodes[].desc`: copy **exact** từ bảng mã lỗi — **đọc toàn bộ bảng, không bỏ sót dòng nào**
- `dbOperations[].fieldsToVerify`: lấy từ bảng DB mapping — **list 100% columns** kể cả auto-generate
- `fieldConstraints[]`: lấy từ PTTK Phase 2 — name, type, maxLength, required, format

**Với mỗi item extract được, gọi ngay lệnh add (KHÔNG tích lũy rồi write một lần):**

```bash
# Mỗi error code:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category errorCodes \
  --data '{"code":"PCER_001","desc":"exact message","section":"validate","trigger":"condition","source":"RSD tr.X"}'

# Mỗi business rule:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category businessRules \
  --data '{"id":"BR1","condition":"uploadType=1","trueBranch":"INSERT action=ADD","falseBranch":null,"source":"RSD tr.X"}'

# Mỗi mode:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category modes \
  --data '{"name":"Thêm mới","triggerValue":"uploadType=1","expectedAction":"INSERT","source":"RSD tr.X"}'

# Mỗi DB operation (1 entry per table):
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category dbOperations \
  --data '{"table":"TABLE_NAME","operation":"INSERT","fieldsToVerify":["COL1","COL2"],"source":"PTTK section Y"}'

# Mỗi external service:
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category externalServices \
  --data '{"name":"S3","onFailure":"error code 2","rollbackBehavior":"không INSERT DB","source":"RSD tr.X"}'

# Mỗi field constraint (từ PTTK Phase 2):
python $SKILL_SCRIPTS/inventory.py add --file <output-folder>/inventory.json \
  --category fieldConstraints \
  --data '{"name":"fieldName","type":"String","maxLength":100,"required":true,"source":"PTTK section Y"}'
```

**⚠️ Inventory = Mandatory Checklist — mỗi item PHẢI có trong output:**

| Inventory Item | Required Output | Section |
|---|---|---|
| Mỗi errorCode[validate] | ≥1 bullet với exact message | ## Kiểm tra validate |
| Mỗi errorCode[main] | ≥1 bullet với exact message | ## Kiểm tra luồng chính |
| Mỗi businessRule | bullet TRUE + FALSE | ## Kiểm tra luồng chính |
| Mỗi dbOperation | SQL SELECT all fieldsToVerify | ## Kiểm tra luồng chính |
| Mỗi mode | ≥1 happy path bullet | ## Kiểm tra luồng chính |
| Mỗi externalService | bullet onFailure + rollback | ## Kiểm tra luồng chính |

**Kết thúc generation: tất cả items phải ☑. Chưa ☑ = THÊM bullet.**

### Step 4d: Inventory Verification Gate

**Sau khi hoàn thành Step 4c, chạy summary và báo cáo cho user:**

```bash
python $SKILL_SCRIPTS/inventory.py summary --file <output-folder>/inventory.json
```

**Nếu bất kỳ category = 0 VÀ tài liệu có khả năng chứa → HỎI USER:**
> "Không tìm thấy {category} trong tài liệu. Tài liệu có đề cập không?"

**Nếu errorCodes = 0:** Dừng lại, hỏi user:
> "Không tìm thấy bảng mã lỗi. Bạn có thể chỉ rõ section nào chứa error codes không?"

### Step 5: Generate Test Design Sections (API Mode)

Generate the test design following the rules loaded via `--ref` and the format of the catalog examples.

**⚠️ BEFORE generating any section, review `projectRules` from Step 0.** Project AGENTS.md rules MUST be applied throughout generation:
- If project defines custom section structure → follow that
- If project defines writing style (e.g., "viết ngắn gọn") → follow that
- If project defines any `## Project-Specific Rules` → apply ALL of them to every section

#### API Mode — Generation

**Common section (hardcoded):** Copy the base template exactly — only replace `{API_NAME}` and `{WRONG_METHODS}`. Format: `- status: 107` (simple). NEVER use `1\. Check api trả về:` in common.

**Post-section checkpoint — Common:** Có đủ Method + URL + Authorization test cases? Thiếu → thêm bullet.
→ Count: {generated}/{expected}. Missing → THÊM bullet ngay, KHÔNG proceed đến section tiếp.

**Validate section (per-field):** For each inputField from Phase 2, generate test cases using the field templates in `--ref api-test-design`. **Process 1 field at a time** — complete ALL cases for the current field before moving to the next.

- **String Required** → test ALL 19+ cases: empty, missing, null, maxLen-1/maxLen/maxLen+1, numeric chars, lowercase/uppercase, accented chars, special chars (see special-char rule below), all space, space in middle, space at start/end, emoji, unicode, boolean, array, object, XSS, SQL injection
- **Integer Required (no default)** → test ALL 19 cases: empty (→ error), missing (→ error), null (→ error), valid positive, negative, decimal, leading zero (00123), very large number, string only (abc), mixed string+number (10abc), special chars (@#$), all space, space at start/end, boolean, array, object, XSS, SQL injection
- **Integer with default** → test ALL 19 cases: empty/missing/null (→ uses default, success), valid value, negative, decimal, leading zero, very large, string, mixed string+number, special chars, all space, space at start/end, boolean, array, object, XSS, SQL injection
- **Optional Integer** → test: empty/missing/null (→ returns all), valid/invalid value, negative, decimal, string, boolean, array, object, XSS, SQL injection
- **JSONB Required** → test ALL 14 cases: empty (→ error), missing (→ error), null (→ error), valid JSON, JSON sai syntax, JSON sai format nghiệp vụ, object rỗng `{}`, mảng `[]`, chuỗi rỗng, string thuần, number, boolean, XSS trong JSON value, SQL injection trong JSON value
- **JSONB Optional** → test: missing/null (→ success), valid JSON (→ success), JSON sai syntax, JSON sai format nghiệp vụ, object rỗng, mảng, chuỗi rỗng, string thuần, number, boolean, XSS trong JSON value, SQL injection trong JSON value
- **Special chars rule**: Only include "ký tự đặc biệt cho phép" + "không cho phép" cases when PTTK explicitly defines `allowedSpecialChars`. If not specified → use 1 generic "ký tự đặc biệt" case with expectedResult = "Theo RSD"
- ALL validate responses use Status: 200 (errors in body, NOT 400/422/500)
- JSON response must be multiline WITHOUT backtick fence

**⚠️ Per-field checkpoint (MANDATORY after EACH field):**
Count generated cases vs required minimum. If any field < min → APPEND missing cases immediately before moving to next field.
```
Field {fieldName} ({type}): {generated}/{min_required} cases. Missing: [list] → THÊM ngay.
```
Min case counts: String Required ≥ 19 | Integer Required ≥ 19 | Integer with Default ≥ 19 | JSONB Required ≥ 14 | JSONB Optional ≥ 12

**Post-section checkpoint — Validate (API):** TỪNG field trong `inventory.errorCodes[section="validate"]` → có bullet với exact error code? Thiếu → THÊM bullet `### [SỬA]`.
→ Count per field: {generated}/{expected} error codes covered. Missing → THÊM `### [SỬA]` ngay, KHÔNG proceed đến main flow.

**Main flow section (LLM-generated):** Every test case MUST include response with `1\. Check api trả về:` / `1\.1. Status:` / `1\.2. Response:` format.

**⚠️ KHÔNG duplicate validate cases vào luồng chính:** Các lỗi validate (truyền sai kiểu, bỏ trống, vượt maxLength...) đã có trong "Kiểm tra validate" → KHÔNG viết lại vào "Kiểm tra luồng chính". Luồng chính chỉ test business logic (error codes từ RSD, DB operations, mode variations, external services).

**⚠️ PHẢI sinh dựa trên inventory từ Step 4c — inject các items cụ thể vào generation:**

```
Sinh test cases cho ## Kiểm tra luồng chính. BẮT BUỘC cover đủ các items sau từ inventory:

Modes:            {list inventory.modes[] — mỗi mode cần ≥1 happy path}
Business rules:   {list inventory.businessRules[] — mỗi branch cần test TRUE + FALSE}
Error codes:      {list inventory.errorCodes[section="main"] — mỗi code cần 1 test với exact message}
DB fields:        {list inventory.dbFields[] — TẤT CẢ fields phải có trong SQL verify}
External services:{list inventory.externalServices[] — cần test onFailure + rollback}

KHÔNG bỏ sót bất kỳ item nào.
```

**Split main flow thành sub-sections (mỗi sub = 1 generation step):**

**Sub-section A — Response fields + DB mapping:**
- Response body verification — list ALL output fields (camelCase) với sample values
- Full SQL: SELECT/FROM/WHERE/ORDER BY với concrete values, verify **tất cả `dbFields[]`**
- Sort order verification

**Sub-section B — Search/Query scenarios:**
- Exact search, approximate (LIKE), combined conditions, not found
- Mỗi search field → ≥2 bullets (exists + not exists)

**Sub-section C — Error codes + Business logic:**
- Mỗi `errorCodes[section="main"]` → 1 test case với **exact message từ inventory**
- Mỗi `businessRules[]` branch → test TRUE + FALSE, mỗi có Response

**Sub-section D — Mode variations + Status transitions:**
- Mỗi `modes[]` item → ≥1 happy path test riêng
- Valid/invalid transitions → test each

**Sub-section E — External services + Rollback:**
- Mỗi `externalServices[]` → test onFailure + rollback không INSERT DB
- DB validations — exists/not exists → test both cases

**Per-sub-section checkpoint (MANDATORY after each sub-section):**
```
Sub-A: {N}/{N} dbFields in SQL, {N}/{N} output fields
Sub-B: {N}/{N} search fields covered
Sub-C: {N}/{N} error codes, {N}/{N} branches
Sub-D: {N}/{N} modes, {N}/{N} transitions
Sub-E: {N}/{N} services, {N}/{N} rollback scenarios
→ Missing: [list] → THÊM bullet `### [SỬA]` ngay
```

**Verify — coverage summary (API mode):**

Kiểm tra nhanh đã cover đủ:
- [ ] `inventory.errorCodes[section="validate"]` → mỗi code có bullet trong ## Kiểm tra validate
- [ ] `inventory.errorCodes[section="main"]` → mỗi code có bullet trong ## Kiểm tra luồng chính
- [ ] `inventory.businessRules[]` → mỗi branch có bullet TRUE + FALSE
- [ ] `inventory.dbFields[]` → tất cả fields có trong SQL SELECT
- [ ] `inventory.externalServices[]` → mỗi service có bullet onFailure + rollback
- [ ] `inventory.modes[]` → mỗi mode có ≥1 happy path

Item nào thiếu → THÊM bullet `### [SỬA] Kiểm tra ...`

**⚠️ PHẢI hiển thị coverage summary cho user sau khi verify (API mode):**
```
📊 Coverage Report (API):
✓ Error codes [validate]: {N}/{N} covered
✓ Error codes [main]:     {N}/{N} covered
✓ Business rules:         {N}/{N} covered
✓ DB fields:              {N}/{N} covered
✓ Modes:                  {N}/{N} covered
✓ External services:      {N}/{N} covered
[SỬA]: {N} bullets thêm/sửa
```

### Step 5a2: Pass 2 — Gap Analysis & Auto-Fill

**Sau khi generate xong tất cả sections, thực hiện pass 2:**

1. **Re-read inventory** từ Step 4c
2. **Scan output markdown** — với MỖI inventory item:
   - Tìm keyword/error code/field name trong output
   - Nếu KHÔNG TÌM THẤY → flag as gap
3. **Gap list:**
```
🔍 Gap Analysis:
- ☐ errorCode "2" [main] → chưa có bullet
- ☐ dbField "S3_FILE_KEY" → chưa có trong SQL SELECT
- ☐ service "S3" rollback → chưa có bullet
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
python <skills-root>/generate-test-design-api/scripts/search.py --ref quality-rules
```

Checklist:
- 100% Vietnamese, keep field/button names exactly as in RSD/PTTK
- No placeholders — use concrete sample values in SQL and responses
- 1 test = 1 check (atomic)
- Forbidden words: "và/hoặc", "hoặc", "có thể", "nên", "ví dụ:", "[placeholder]"
- SQL: concrete values (`WHERE ID = 10001`), UPPERCASE columns, NO placeholders
- Output starts with `# {API_NAME}` — NO blockquote header, NO `---` horizontal rules
- **Project AGENTS.md quality rules**: If project defines additional quality constraints → apply them

## Catalog Management

### Add Examples to Catalog

To add new reference examples:
1. Save the test design output as a `.md` file
2. Place it in `catalog/api/` at your project root
3. The search engine will automatically index new files

### List Available Examples

```bash
python <skills-root>/generate-test-design-api/scripts/search.py --list
```

## Project Structure

After running `test-genie init`, your project has this structure:

```
<project-root>/
├── node_modules/test-genie/           ← Skills live here (managed by npm)
│   ├── generate-test-design-api/
│   │   ├── SKILL.md                      ← Workflow instructions (this file)
│   │   ├── AGENTS.md                     ← Skill-level default rules
│   │   ├── references/                   ← Detailed rules (dev-managed)
│   │   │   ├── api-test-design.md
│   │   │   ├── priority-rules.md
│   │   │   ├── quality-rules.md
│   │   │   └── output-examples.md
│   │   ├── data/rules/
│   │   │   └── api-rules.csv             ← Format rules (searchable via --domain rules)
│   │   └── scripts/
│   │       └── search.py                 ← Catalog search (auto-detects project root)
│   └── generate-test-case-api/
│       └── ...
├── .claude/commands/                  ← Claude slash commands (auto-generated)
│   └── generate-test-design-api.md
├── catalog/                           ← Managed by user/tester
│   ├── api/                              ← API test design .md examples
│   └── mobile/                           ← Mobile test design examples
├── excel_template/
│   ├── template.xlsx                  ← Spreadsheet template
│   └── structure.json                 ← Template structure
├── <tên-test-case>/                   ← Per-feature test folder
│   ├── RSD.pdf                           ← Input: requirement spec
│   ├── PTTK.pdf                          ← Input: technical spec (optional)
│   └── test-design-api.md               ← Output: test design mindmap
├── credentials.json                   ← OAuth credentials (DO NOT COMMIT)
└── AGENTS.md                          ← Project-specific rules (user-managed)
```

**Output location:** Save the generated test design `.md` file into the `<tên-test-case>/` folder alongside the input documents. The folder name should match the feature/API being tested.

## Key Format Rules (Quick Reference)

### Critical Rules
- Output starts with `# {API_NAME}` — NO blockquote header, NO `---` horizontal rules
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
