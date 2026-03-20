---
name: generate-test-case
description: Generate test cases from mindmap + RSD/PTTK and output to test-cases.json. Use when user says "sinh test case", "sinh test cases", "generate test case", "generate test cases", "tạo test case", "tạo test cases", "xuất test case", "xuất json", or provides a mindmap file (.txt/.md) for test case generation.
---

# Test Case Generator

Generate test cases from a parsed mindmap file (exported from `.gmind`) and output to a JSON file. Uses a searchable catalog of real test cases (CSV format exported from spreadsheet) to ensure output matches the expected format per project.

Output: **`<tên-test-case>/test-cases.json`** — a JSON array of test case objects. To upload to Google Sheets, use: `python upload_gsheet.py <tên-test-case>`

> **Scope**: This skill covers **test case generation** (spreadsheet output) for two modes:
> - **API mode** — API test cases
> - **Frontend mode** — Frontend test cases
>
> It does **NOT** cover test design/mindmap generation — that is handled by `test-design-generator` skill.

## When to Apply

- User provides a mindmap file (.txt or .md exported from .gmind) and asks to generate test cases
- User says "sinh test case", "sinh test cases", "tạo test case", "tạo test cases", "generate test case", "generate test cases", "xuất json", "xuất test case"
- User uploads mindmap + optional RSD/PTTK for test case generation
- **User provides only RSD + PTTK (no mindmap)** — skill auto-generates mindmap structure internally, then generates test cases from it

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## Rule Override Hierarchy

Rules are resolved in this order (highest priority first):

1. **Project `AGENTS.md`** — `AGENTS.md` at project root (user-managed, project-specific overrides)
2. **Skill-level `AGENTS.md`** — `test-case-generator/AGENTS.md` (default rules)
3. **Skill references** — `references/*.md` (detailed rules, managed by dev team)
4. **This SKILL.md** — workflow instructions (lowest priority, never overridden)

**How overrides work:** Rules in project `AGENTS.md` are merged with skill defaults — only the sections/rules explicitly defined in project `AGENTS.md` override the corresponding defaults. Sections not mentioned fall back to skill-level `AGENTS.md`.

## Workflow

### Step 0: Validate Project Setup

Before starting generation, check that the project structure exists:

1. **Check catalog** — look for `catalog/` directory at project root (contains `api/`, `frontend/`, `mobile/`)
2. **Check AGENTS.md** — look for `AGENTS.md` at project root (project-level rules)
3. **Check template structure** — look for `excel_template/structure.json`

**If catalog directory does not exist:**
- Ask user: "Chưa có thư mục `catalog/`. Bạn đã chạy `test-genie init` chưa?"
- If not → guide user to run `test-genie init` to set up project structure

**If AGENTS.md does not exist at project root:**
- Use skill-level `AGENTS.md` (default rules)
- Inform user: "Project chưa có AGENTS.md. Đang dùng rules mặc định."

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
   - Scan for `.pdf` files — identify RSD and PTTK by filename (e.g., `RSD*.pdf`, `PTTK*.pdf`, or any `.pdf` files present)
   - Also check for existing `test-design.md` (mindmap already generated)
2. **DO NOT ask** the user for file paths — use whatever documents are found in the folder
3. If no `.pdf` files found → inform user: "Folder `<feature-name>/` không có tài liệu RSD/PTTK. Hãy đặt file vào folder trước."

| Input found in folder | Flow |
|----------------------|------|
| `test-design.md` exists (mindmap) | **Standard flow** — go to Step 2 |
| `.pdf` files found but no `test-design.md` | **Auto flow** — invoke `test-design-generator` first, then go to Step 2 |
| Mindmap (.md/.txt) provided directly by user | **Standard flow** — go to Step 2 |
| RSD + PTTK provided directly by user (no mindmap) | **Auto flow** — invoke `test-design-generator` first, then go to Step 2 |

**Auto flow (no mindmap):**
1. Invoke `test-design-generator` skill with the RSD + PTTK from the feature folder
2. The skill generates a complete test design mindmap → saved as `<feature-name>/test-design.md`
3. Use that generated mindmap as input for the standard flow below

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

**Load ONLY the references needed for the detected mode.** Do NOT load all references upfront.

Use the installed skill path for your assistant:
- Claude: find with `find ~/.claude -name "search.py" -path "*/test-case-generator/*" 2>/dev/null | head -1`
- Cursor: find with `find ~/.cursor -name "search.py" -path "*/test-case-generator/*" 2>/dev/null | head -1`
- Or use: `node -e "require('child_process').execSync('npm root -g', {encoding:'utf8'}).trim() + '/test-genie/test-case-generator/scripts/search.py'" 2>/dev/null`

**Shortcut** — resolve script path automatically:
```bash
SKILL_SCRIPTS=$(node -e "const p=require('child_process').execSync('npm root -g',{encoding:'utf8'}).trim(); console.log(p+'/test-genie/test-case-generator/scripts')" 2>/dev/null \
  || find ~/.claude ~/.cursor -name "search.py" -path "*/test-case-generator/*" 2>/dev/null | head -1 | xargs dirname)
echo $SKILL_SCRIPTS
```

**Note:** `search.py` auto-detects the project root by looking for `catalog/` or `AGENTS.md`. You can also pass `--project-root /path/to/project` explicitly.

#### Load by mode (lazy-load)

**Always load first (both modes):**
```bash
python <skills-root>/test-case-generator/scripts/search.py --ref priority-rules
python <skills-root>/test-case-generator/scripts/search.py --ref output-format
python <skills-root>/test-case-generator/scripts/search.py --ref quality-rules
```

**API mode — load this only:**
```bash
python <skills-root>/test-case-generator/scripts/search.py --ref api-test-case
```

**Frontend mode — load this only:**
```bash
python <skills-root>/test-case-generator/scripts/search.py --ref fe-test-case
```

> **Why lazy-load?** Loading all references regardless of mode wastes tokens on rules that won't be used. Only load what the detected mode requires.

#### Search examples & utilities

```bash
# Search API examples (searches catalog/api/ in project root)
python <skills-root>/test-case-generator/scripts/search.py "search list validate" --domain api

# Search Frontend examples (searches catalog/frontend/ in project root)
python <skills-root>/test-case-generator/scripts/search.py "giao dien chung phan quyen" --domain frontend

# List all available references
python <skills-root>/test-case-generator/scripts/search.py --list-refs

# List all available examples
python <skills-root>/test-case-generator/scripts/search.py --list

# Read full content of top match
python <skills-root>/test-case-generator/scripts/search.py "validate string field" --domain api --full
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

### Step 6: Generate Test Cases in Batches

Split mindmap into 3 batches, process sequentially:

**BATCH 1 — Pre-validate sections:**
- All ## sections BEFORE "Kiểm tra validate" (e.g., common cases, permissions)
- Force testSuiteName = section name
- Instruction: "Chỉ sinh test cases cho section: {name}. KHÔNG sinh cases cho validate hay luồng chính."

**BATCH 2 — Validate section (grouped fields):**
- "Kiểm tra validate" and all ### subsections inside
- **Group 3-5 fields per sub-batch** instead of 1 field per sub-batch to reduce LLM round-trips
- Force testSuiteName per catalog convention (search catalog first)
- Instruction per sub-batch: "Sinh test cases validate cho các fields sau: {field_1}, {field_2}, {field_3}. Mỗi field xử lý riêng biệt, KHÔNG trộn test cases giữa các fields."

**Grouping rules:**
- Group fields with **similar types** together (e.g., 3 textbox fields in 1 call, 2 combobox + 1 dropdown in 1 call)
- If a field has **complex validation** (nhiều rule đặc biệt, cross-field dependencies) → tách riêng 1 sub-batch
- Maximum 5 fields per sub-batch — nếu nhiều hơn 5 thì chia thêm sub-batch
- Each sub-batch MUST include: field names, types, constraints, and request body context

> **Why group?** Per-field sub-batch gọi LLM N lần (mỗi lần re-inject context). Gộp 3-5 fields giảm xuống N/4 calls, tiết kiệm overhead context đáng kể mà vẫn đủ rõ ràng cho LLM xử lý.

**BATCH 3 — Post-validate sections:**
- All ## sections AFTER "Kiểm tra validate" (e.g., grid, functionality, timeout)
- Force testSuiteName = section name, maxTokens: 65536
- Instruction: "Chỉ sinh test cases cho section: {name}. KHÔNG sinh lại cases đã có."

**After all batches:** Deduplicate testCaseNames (case-insensitive, keep first occurrence).

Generate following rules loaded via `--ref api-test-case` (API) or `--ref fe-test-case` (Frontend).

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

#### 7c: Return Result

```
Đã lưu {testCaseCount} test cases tại `<tên-test-case>/test-cases.json`.
Suites: {suiteCount} | Test cases: {testCaseCount}
Để upload lên Google Sheets, chạy: python <skills-root>/test-case-generator/scripts/upload_gsheet.py <tên-test-case>
```

### Upload to Google Sheets (separate command)

After generating `test-cases.json`, upload to Google Sheets using:

```bash
python <skills-root>/test-case-generator/scripts/upload_gsheet.py <tên-test-case>
```

**Prerequisites:**
```bash
pip install google-auth-oauthlib google-auth google-api-python-client openpyxl
```

Place `credentials.json` (OAuth Desktop App / installed type) at project root. First run will open a browser for authentication — token is cached at `~/.config/test-genie/token.json`.

**Extract template structure (one-time setup):**
```bash
python <skills-root>/test-case-generator/scripts/extract_structure.py
```
This reads `excel_template/template.xlsx` and outputs `excel_template/structure.json`.

**Upload test cases:**
```bash
python <skills-root>/test-case-generator/scripts/upload_gsheet.py <tên-test-case> \
  [--title "Custom Title"] \
  [--credentials credentials.json]
```

Output:
```json
{
  "success": true,
  "spreadsheetId": "1abc...",
  "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/1abc.../edit",
  "title": "TC_Ten_chuc_nang_200326",
  "rowsWritten": 75,
  "suiteCount": 5,
  "testCaseCount": 70
}
```

This script:
- Creates a new Google Sheets with template header rows + formatting (from `structure.json`)
- Writes test case data with suite headers (light green, bold, merged) and test case rows (white, wrap text)
- Shares the file with "anyone" as editor
- Returns the spreadsheet URL

#### Upload Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `credentials.json not found` | File chưa có ở project root | Đặt file vào project root hoặc dùng `--credentials path/to/file.json` |
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
