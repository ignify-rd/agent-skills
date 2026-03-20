---
name: generate-test-case
description: Generate test cases from mindmap + RSD/PTTK and push to Google Sheets. Use when user says "sinh test case", "sinh test cases", "generate test case", "generate test cases", "tạo test case", "tạo test cases", "xuất test case", "đẩy lên sheet", or provides a mindmap file (.txt/.md) for test case generation.
---

# Test Case Generator

Generate test cases from a parsed mindmap file (exported from `.gmind`) and push directly to Google Sheets. Uses a searchable catalog of real test cases (CSV format exported from spreadsheet) to ensure output matches the expected format per project.

Output: **Google Sheets URL** (not raw JSON). The skill generates JSON internally, maps it to the spreadsheet template structure, and writes data via Google Sheets MCP.

> **Scope**: This skill covers **test case generation** (spreadsheet output) for two modes:
> - **API mode** — API test cases
> - **Frontend mode** — Frontend test cases
>
> It does **NOT** cover test design/mindmap generation — that is handled by `test-design-generator` skill.

## When to Apply

- User provides a mindmap file (.txt or .md exported from .gmind) and asks to generate test cases
- User says "sinh test case", "sinh test cases", "tạo test case", "tạo test cases", "generate test case", "generate test cases", "xuất json"
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
3. **Check template** — look for `excel_template/template.xlsx` (spreadsheet template for Google Sheets output)

**If catalog directory does not exist:**
- Ask user: "Chưa có thư mục `catalog/`. Bạn đã chạy `test-genie init` chưa?"
- If not → guide user to run `test-genie init` to set up project structure

**If AGENTS.md does not exist at project root:**
- Use skill-level `AGENTS.md` (default rules)
- Inform user: "Project chưa có AGENTS.md. Đang dùng rules mặc định."

**If catalog exists but has no examples (empty api/ and frontend/):**
- Warn user: "Catalog chưa có examples. Output có thể không chính xác format. Bạn có muốn thêm CSV examples trước không?"
- Proceed with skill references as fallback

### Step 1: Check Input Type

| Input provided | Flow |
|---------------|------|
| Mindmap (.md/.txt) + optional RSD/PTTK | **Standard flow** — go to Step 2 |
| RSD + PTTK only (no mindmap) | **Auto flow** — invoke `test-design-generator` skill first to generate mindmap, then go to Step 2 |
| RSD only (no PTTK, no mindmap) | **Auto flow** — invoke `test-design-generator` skill first, then go to Step 2 |

**Auto flow (no mindmap):**
1. Invoke `test-design-generator` skill with the provided RSD + PTTK
2. The skill generates a complete test design mindmap (.md)
3. Use that generated mindmap as input for the standard flow below

### Step 2: Determine Mode

| Mindmap content | Mode | Output |
|-----------------|------|--------|
| API name + endpoint references | API | JSON test cases for API |
| Screen name + UI section names | Frontend | JSON test cases for Frontend |

**Clues for API mode:** First line is API name, sections include "case common", "phân quyền", "validate", field names are request params (PAR_TYPE, REG_CHANNEL...).

**Clues for Frontend mode:** First line is screen name (e.g., "WEB_BO_Danh mục > ..."), sections include "giao diện chung", "phân quyền", "validate", "lưới dữ liệu", "chức năng".

### Step 3: Load Rules & References

**Always load priority rules and project-specific references first**, then search for examples:

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

**IMPORTANT:** Always run search.py from the **project root** directory (where `catalog/` and `AGENTS.md` are located).

```bash
# Load priority rules (MUST load first)
python <skills-root>/test-case-generator/scripts/search.py --ref priority-rules

# Load generation rules
python <skills-root>/test-case-generator/scripts/search.py --ref api-test-case    # API mode
python <skills-root>/test-case-generator/scripts/search.py --ref fe-test-case     # Frontend mode
python <skills-root>/test-case-generator/scripts/search.py --ref output-format
python <skills-root>/test-case-generator/scripts/search.py --ref quality-rules

# List all available references
python <skills-root>/test-case-generator/scripts/search.py --list-refs

# Search API examples (searches catalog/api/ in project root)
python <skills-root>/test-case-generator/scripts/search.py "search list validate" --domain api

# Search Frontend examples (searches catalog/frontend/ in project root)
python <skills-root>/test-case-generator/scripts/search.py "giao dien chung phan quyen" --domain frontend

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

**BATCH 2 — Validate section (per-field):**
- "Kiểm tra validate" and all ### subsections inside
- Split: each `### field_name` = 1 separate sub-batch
- Force testSuiteName per catalog convention (search catalog first)
- Instruction per sub-batch: "Chỉ sinh test cases validate cho field: {field_name}."

**BATCH 3 — Post-validate sections:**
- All ## sections AFTER "Kiểm tra validate" (e.g., grid, functionality, timeout)
- Force testSuiteName = section name, maxTokens: 65536
- Instruction: "Chỉ sinh test cases cho section: {name}. KHÔNG sinh lại cases đã có."

**After all batches:** Deduplicate testCaseNames (case-insensitive, keep first occurrence).

Generate following rules loaded via `--ref api-test-case` (API) or `--ref fe-test-case` (Frontend).

### Step 7: Output to Google Sheets

Output is a **Google Sheets URL** (not raw JSON). Flow:

1. **Upload** `excel_template/template.xlsx` → Google Drive as new Google Sheets
2. **Detect** column structure dynamically from the uploaded sheet
3. **Write** test case rows + apply formatting

**IMPORTANT:**
- Final deliverable is ALWAYS a Google Sheets link — never return raw JSON
- Each run creates a **new** spreadsheet — never reuse existing Drive files
- Template structure is whatever is in `excel_template/template.xlsx` — no fixed project types

**Script paths** — resolve automatically:
```bash
SKILL_SCRIPTS=$(node -e "const p=require('child_process').execSync('npm root -g',{encoding:'utf8'}).trim(); console.log(p+'/test-genie/test-case-generator/scripts')" 2>/dev/null \
  || find ~/.claude ~/.cursor -name "upload_template.py" -path "*/test-case-generator/*" 2>/dev/null | head -1 | xargs dirname)
echo $SKILL_SCRIPTS
```

**Prerequisites:**
```bash
pip install google-api-python-client google-auth
```
Place `credentials.json` (Service Account) at project root, or pass `--credentials path/to/credentials.json`.

**ALWAYS run scripts from the project root directory.**

#### 7a: Generate JSON Array (internal)

Generate a JSON array where each element is one test case object. Use these standard field names — `detect_template.py` will map them to the correct columns automatically:

| Field | Description | Notes |
|-------|-------------|-------|
| `testSuiteName` | Test suite / group name | Triggers a suite header row |
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

#### 7b: Upload Template to Google Drive

```bash
python $SKILL_SCRIPTS/upload_template.py \
  --name "TC_API_Ten_chuc_nang_DDMMYY"
```

- `--name`: name for the new spreadsheet (e.g. `TC_API_Lay_danh_sach_200326`)
- `--template`: path to xlsx file (default: `excel_template/template.xlsx`)

Output:
```json
{
  "spreadsheetId": "1abc...",
  "webViewLink": "https://docs.google.com/spreadsheets/d/1abc.../edit",
  "name": "TC_API_Ten_chuc_nang_DDMMYY"
}
```

Save `spreadsheetId` and `webViewLink` for next steps.

#### 7c: Detect Column Structure

```bash
python $SKILL_SCRIPTS/detect_template.py \
  --spreadsheet-id {spreadsheetId}
```

Output:
```json
{
  "spreadsheetId": "1abc...",
  "webViewLink": "https://docs.google.com/spreadsheets/d/1abc.../edit",
  "sheetName": "TestCases",
  "sheetId": 0,
  "columnMapping": {
    "testSuiteName": 0,
    "details": 1,
    "externalId": 2,
    "testCaseName": 3,
    "summary": 4,
    "preConditions": 5,
    "steps": 6,
    "expectedResults": 7,
    "result": 11,
    "note": 12
  },
  "totalColumns": 13,
  "lastCol": "M",
  "headerRow": 2,
  "dataStartRow": 3
}
```

This script:
- Scans rows 1–20 to find the actual header row (fully dynamic, no hardcoded project types)
- Skips group-header rows (e.g. "Test Suite", "Test Case") and single-cell metadata rows
- Clears sample/formula rows from the template (keeps headers intact)

Save all output fields — they are inputs for the next step.

> **Re-detect only:** Use `--no-clear` to skip clearing sample data (useful for inspection).

#### 7d: Write Test Cases to Sheet

Save the generated JSON array to a temp file, then run:

```bash
python $SKILL_SCRIPTS/upload_to_sheet.py \
  --spreadsheet-id {spreadsheetId} \
  --sheet-name "{sheetName}" \
  --sheet-id {sheetId} \
  --data /tmp/test_cases.json \
  --column-mapping '{columnMapping as JSON string}' \
  --total-columns {totalColumns} \
  --data-start-row {dataStartRow}
```

Output:
```json
{
  "success": true,
  "rowsWritten": 75,
  "suiteCount": 5,
  "testCaseCount": 70,
  "updatedRange": "TestCases!A3:M77",
  "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/1abc.../edit"
}
```

This script:
- Inserts suite header rows automatically when `testSuiteName` changes
- Appends with `valueInputOption: RAW` — `\n` renders as newlines in cells
- Applies formatting: suite headers (light green, bold, merged) + test case rows (white, wrap text)

#### 7e: Return Result

```
✅ Đã đẩy {testCaseCount} test cases lên Google Sheets.
📊 URL: {spreadsheetUrl}
📋 Sheet: {sheetName} — {suiteCount} test suites, {testCaseCount} test cases
```

**If scripts fail (no credentials / Drive access):**
- Save JSON to `test_cases.json` at project root
- Inform user: "Không thể kết nối Google Drive. Đã lưu {n} test cases tại `test_cases.json`."

#### 7f: Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `credentials.json not found` | File chưa có ở project root | Đặt file vào project root hoặc dùng `--credentials path/to/file.json` |
| `Missing dependencies` | Chưa cài thư viện | Chạy `pip install google-api-python-client google-auth` |
| Upload fails 403 | Service account không có quyền Drive | Cấp quyền Drive API trong Google Cloud Console |
| Upload processing timeout | Google chưa xử lý xong | Chạy lại `upload_template.py` |
| `columnMapping` rỗng | Header row không detect được | Chạy `detect_template.py --no-clear` để xem headers thực tế |
| Columns bị lệch | Template có cấu trúc lạ | Xem output `columnMapping` từ `detect_template.py`, đối chiếu với header row thực tế |
| `\n` không xuống dòng | Thiếu wrap text | Script tự apply `wrapStrategy: WRAP`, kiểm tra `--no-format` có bị bật không |
| Cells hiện `#REF!` | Ghi đè lên formula zone | Kiểm tra `dataStartRow` từ output `detect_template.py` |

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
│   │       ├── search.py
│   │       ├── upload_template.py     ← Upload .xlsx → Google Drive (one-time)
│   │       ├── detect_template.py     ← Copy template + detect column structure
│   │       └── upload_to_sheet.py     ← Write test cases + apply formatting
│   └── test-design-generator/
│       └── ...
├── .claude/commands/                  ← Claude slash commands (auto-generated)
│   ├── generate-test-case.md
│   └── generate-test-design.md
├── .cursor/commands/                  ← Cursor slash commands (auto-generated)
│   ├── generate-test-case.mdc
│   └── generate-test-design.mdc
├── .cursor/rules/
│   └── test-genie.mdc                 ← Cursor auto-loads when relevant
├── catalog/                           ← Managed by user/tester
│   ├── api/                              ← API test case .csv examples
│   ├── frontend/                         ← Frontend test case .csv examples
│   └── mobile/                           ← Mobile test case examples
├── excel_template/
│   └── template.xlsx                  ← Spreadsheet template for Google Sheets
├── credentials.json                   ← Service Account (DO NOT COMMIT)
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
