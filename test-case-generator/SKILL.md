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

When the project has its own `AGENTS.md` at the root, any rule defined there **completely replaces** the corresponding rule in the skill-level `AGENTS.md`.

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
- Claude: `.claude/skills/test-case-generator/scripts/search.py`
- Cursor: `.cursor/skills/test-case-generator/scripts/search.py`
- Codex: `${CODEX_HOME:-~/.codex}/skills/test-case-generator/scripts/search.py`

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

Output is a **Google Sheets URL** (not raw JSON). The flow follows the same 3-step pattern as the test-genie web app:

1. **Upload template** → Drive (one-time per project type, converts .xlsx → Google Sheets)
2. **Copy template** → create new spreadsheet (preserves all headers, formatting, formulas, merged cells)
3. **Append data** → write test case rows via Sheets API

**IMPORTANT:** The final deliverable is ALWAYS a Google Sheets link. JSON is only internal — NEVER return raw JSON as final output.

#### 7a: Generate JSON Array (internal)

Generate a JSON array. Each element is one test case object. The field names depend on the **project type** (template).

**Determine project type** — check the catalog's AGENTS.md or ask user. Available types:

| Project Type | Template File | Columns | Header Row | Data Start Row | ID Pattern |
|-------------|---------------|---------|------------|----------------|------------|
| `API_TEST` | API_Fee_Template.xlsx | A-M (13) | 1 | 2 | API_1, API_2... |
| `FEE_ENGINE` | TestLink.xlsm | A-U (21) | 2 | 3 | WEB_1, WEB_2... |
| `HOME` | Template_new.xlsx | A-T (20) | 16 | 18 | TC_001, TC_002... |
| `LENDING` | Template_old.xlsx | A-I (9) | 13 | 14 | TC_0001, TC_0002... |

**API_TEST column mapping** (most common for API test cases):

| Col | Header | JSON Key | Description |
|-----|--------|----------|-------------|
| A | Name | `testSuiteName` | Test Suite Name |
| B | Details | `details` | Test Suite Details (usually `""`) |
| C | External ID | `externalId` | Test Case ID: API_1, API_2... (usually `""`, auto-generated) |
| D | Name | `testCaseName` | Test Case Name |
| E | Summary | `summary` | = same as testCaseName |
| F | PreConditions | `preConditions` | Endpoint + headers + body JSON |
| G | Step | `steps` | Test steps |
| H | Expected Result | `expectedResults` | Expected response |
| I | Spec Title | `specTitle` | `""` |
| J | Document ID | `documentId` | `""` |
| K | Duration | `duration` | `""` |
| L | Result | `result` | `"PENDING"` |
| M | Note | `note` | `""` |

**HOME column mapping** (for frontend/general test cases):

| Col | Header | JSON Key | Description |
|-----|--------|----------|-------------|
| A | Name | `taskName` | Test Suite Name |
| B | Details | `details` | Test Suite Details |
| C-E | Testcase LV1/2/3 | `testcaseLV1/2/3` | Category levels |
| F | External ID | `testCaseId` | TC_001, TC_002... |
| G | Name | `testCaseTitle` | Test Case Name |
| H | Summary | `testObjective` | Test Objective |
| I | PreConditions | `preConditions` | Pre-conditions + Test Data |
| J | Status | `status` | Status |
| K | ExecutionType | `executionType` | Manual/Automated |
| L | Importance | `priority` | Low/Medium/High |
| M | Keywords | `keywords` | Keywords |
| N | Attachments | `attachments` | Attachment count |
| O | Step | `testSteps` | Test Steps |
| P | Expected Result | `expectedResult` | Expected Result |
| Q | Actual Result | `actualResult` | Actual Result |
| R | StepExecType | `stepExecType` | Step Exec Type |
| S | Spec Title | `specTitle` | Spec Title |
| T | Document ID | `documentId` | Document ID |

> For FEE_ENGINE and LENDING column mappings, see `test-genie/src/services/templates/templateDefinitions.js`.

#### 7b: Upload Template to Google Drive (one-time)

The template .xlsx file must exist in Google Drive as a Google Sheets file BEFORE creating spreadsheets. This is a one-time setup per project type.

**Template resolution:**
```
excel_template/template.xlsx    (project root, created by test-genie init)
```

**Step 1 — Search for existing template:**
```
# MCP: google_drive.search_files or google_drive.list_files
query: "name = 'Test-Genie Template - API_TEST (DO NOT DELETE)' and mimeType = 'application/vnd.google-apps.spreadsheet'"
```
If found → save `templateFileId`, skip to 7c.

**Step 2 — Upload template if not found:**
```
# MCP: google_drive.upload_file
filePath: "excel_template/template.xlsx"
name: "Test-Genie Template - API_TEST (DO NOT DELETE)"
mimeType: "application/vnd.google-apps.spreadsheet"   # CRITICAL: converts .xlsx → Google Sheets
description: "Test case template for Test-Genie (API_TEST). DO NOT DELETE."
```
Returns: `{ id: "1abc...", webViewLink: "https://docs.google.com/..." }`
Save `templateFileId = result.id`

**Step 3 — Validate upload:**
```
# MCP: google_drive.get_file
fileId: "{templateFileId}"
fields: "id,name,mimeType"
```
Verify `mimeType` = `"application/vnd.google-apps.spreadsheet"` (not xlsx).

**CRITICAL:** The template preserves ALL formatting — headers, merged cells, colors, column widths, formulas. This is WHY we copy the template instead of building from scratch.

#### 7c: Copy Template → Create New Spreadsheet

**Step 1 — Copy template:**
```
# MCP: google_drive.copy_file
fileId: "{templateFileId}"
name: "TC_API_Lay_danh_sach_bo_loc_chinh_sach_phi_180326"
```
Returns: `{ id: "1xyz...", webViewLink: "https://docs.google.com/spreadsheets/d/1xyz.../edit" }`
Save `spreadsheetId = result.id`

**Step 2 — Get sheet name from the copied file:**
```
# MCP: google_sheets.get_spreadsheet
spreadsheetId: "{spreadsheetId}"
fields: "sheets.properties(sheetId,title)"
```
Returns: `{ sheets: [{ properties: { sheetId: 0, title: "TestCases" } }] }`
Save `sheetName = result.sheets[0].properties.title`

**Step 3 — Read & analyze template structure (CRITICAL):**

Do NOT assume column mapping from the static tables in 7a. Always read the actual header row(s) from the copied spreadsheet to build a **dynamic column mapping**.

```
# MCP: google_sheets.get_values
spreadsheetId: "{spreadsheetId}"
range: "{sheetName}!A1:{lastCol}{dataStartRow}"    # e.g., "TestCases!A1:M2" for API_TEST
```

Returns the header area. Example for API_TEST (headerRow=1, dataStartRow=2):
```json
{
  "values": [
    ["Name", "Details", "External ID", "Name", "Summary", "PreConditions", "Step", "Expected Result", "Spec Title", "Document ID", "Duration", "Result", "Note"]
  ]
}
```

For HOME (headerRow=16, dataStartRow=18), read rows 1-18:
```
range: "{sheetName}!A1:T18"
```
Headers may span multiple rows (e.g., rows 15-16 with merged group headers on row 15 and detail headers on row 16).

**Build dynamic column mapping from header row:**

```javascript
// Pseudocode — agent parses actual headers
const headerRow = response.values[headerRowIndex]  // last row in header area
const columnMapping = {}

headerRow.forEach((header, colIndex) => {
  const normalized = header.trim().toLowerCase()

  // Map header labels to JSON keys
  const labelToKey = {
    // API_TEST / FEE_ENGINE / HOME share these labels
    "name":             colIndex === 0 ? "testSuiteName" : "testCaseName",  // col A = suite, later "Name" = test case
    "details":          "details",
    "external id":      "externalId",
    "summary":          "summary",
    "preconditions":    "preConditions",
    "step":             "steps",
    "expected result":  "expectedResults",
    "spec title":       "specTitle",
    "document id":      "documentId",
    "duration":         "duration",
    "estimated exec. duration": "duration",
    "result":           "result",
    "note":             "note",
    "notes":            "note",
    // HOME-specific
    "testcase lv1":     "testcaseLV1",
    "testcase lv2":     "testcaseLV2",
    "testcase lv3":     "testcaseLV3",
    "status":           "status",
    "executiontype":    "executionType",
    "importance":       "priority",
    "keywords":         "keywords",
    "number of attachments": "attachments",
    "actual result":    "actualResult",
    "stepexectype":     "stepExecType",
    // LENDING-specific
    "test case id":     "testCaseId",
    "test case title":  "testCaseTitle",
    "pre-conditions":   "preConditions",
    "test steps":       "testSteps",
    "expected result":  "expectedResult",
    "priority":         "priority",
    "test results":     "testResults",
    "bugid":            "bugId",
  }

  const key = labelToKey[normalized]
  if (key) {
    columnMapping[key] = colIndex
  }
})
```

**Output:** `columnMapping` object, e.g.:
```json
{
  "testSuiteName": 0,
  "details": 1,
  "externalId": 2,
  "testCaseName": 3,
  "summary": 4,
  "preConditions": 5,
  "steps": 6,
  "expectedResults": 7,
  "specTitle": 8,
  "documentId": 9,
  "duration": 10,
  "result": 11,
  "note": 12
}
```

Also detect:
- `totalColumns` = headerRow.length (number of columns to use in each row)
- `dataStartRow` = headerRowIndex + 2 (1-indexed, first row after headers)
- `lastCol` = column letter for last column (e.g., "M" for 13 columns, "T" for 20)

**Step 4 — Clear sample data (keep headers):**
```
# MCP: google_sheets.clear_values
spreadsheetId: "{spreadsheetId}"
range: "{sheetName}!A{dataStartRow}:{lastCol}"    # e.g., "TestCases!A2:M" for API_TEST
```
This removes any sample rows from the template, leaving headers intact.

> **Fallback dataStartRow** (if detection fails): API_TEST=2, FEE_ENGINE=3, HOME=18, LENDING=14

#### 7d: Build Values Array & Insert Data

**Step 1 — Build 2D array using the dynamic column mapping from 7c Step 3:**

Group by `testSuiteName`. For each group, insert a **suite header row** (col A only) followed by test case rows.

```javascript
// Pseudocode — agent builds this array using dynamic columnMapping from 7c Step 3
const rows = []
let currentSuite = null
const totalCols = totalColumns  // from 7c detection, e.g., 13 for API_TEST

// Helper: create a row with value at the correct column index
function makeRow(fieldValues) {
  const row = new Array(totalCols).fill("")
  for (const [key, value] of Object.entries(fieldValues)) {
    const colIndex = columnMapping[key]   // from 7c Step 3
    if (colIndex !== undefined) {
      row[colIndex] = value || ""
    }
  }
  return row
}

for (const tc of testCases) {
  // Insert suite header when suite changes
  if (tc.testSuiteName !== currentSuite) {
    currentSuite = tc.testSuiteName
    // Suite header: only testSuiteName column has value, rest empty
    rows.push(makeRow({ testSuiteName: currentSuite }))
  }

  // Test case row: use dynamic mapping — NOT hardcoded column positions
  rows.push(makeRow({
    testCaseName:    tc.testCaseName,
    summary:         tc.testCaseName,         // summary = same as testCaseName
    preConditions:   tc.preConditions,         // multiline string with \n
    steps:           tc.step,
    expectedResults: tc.expectedResult,
    result:          "PENDING",
    // All other fields default to "" (externalId, specTitle, documentId, etc.)
  }))
}
```

**Example output** (API_TEST, 13 columns A-M):
```json
[
  ["Kiểm tra các case common", "", "", "", "", "", "", "", "", "", "", "", ""],
  ["", "", "", "Method_Kiểm tra khi nhập sai method GET", "Method_Kiểm tra khi nhập sai method GET", "1. Send API login thành công\n2. Chuẩn bị request hợp lệ\n 2.1 Endpoint: POST {{BASE_URL}}/v1/segment-manager/segment-config/search\n 2.2 Header:\n {\n  \"Authorization\": \"Bearer {JWT_TOKEN}\",\n  \"Content-Type\": \"application/json\"\n }\n 2.3 Body:\n {\n  \"page\": 0,\n  \"size\": 10\n }", "1. Nhập invalid Method: GET\n2. Send API", "1. Check api trả về:\n 1.1. Status: 107\n 1.2. Response:\n {\n  \"message\": \"Error retrieving AuthorInfo\"\n }", "", "", "", "PENDING", ""],
  ["", "", "", "URL_Kiểm tra khi truyền sai url", "URL_Kiểm tra khi truyền sai url", "...", "...", "...", "", "", "", "PENDING", ""],
  ["Kiểm tra phân quyền", "", "", "", "", "", "", "", "", "", "", "", ""],
  ["", "", "", "Phân quyền_User không có quyền menu", "Phân quyền_User không có quyền menu", "...", "...", "...", "", "", "", "PENDING", ""]
]
```

**Step 2 — Write data to sheet using MCP:**
```
# MCP: google_sheets.append_values
spreadsheetId: "{spreadsheetId}"
range: "{sheetName}!A:{lastCol}"           # lastCol from 7c detection, e.g., "TestCases!A:M"
values: [                                   # the 2D array built above
  ["Kiểm tra các case common", "", "", ...],
  ["", "", "", "Method_Kiểm tra khi nhập sai method GET", ...],
  ...
]
valueInputOption: "RAW"                     # IMPORTANT: RAW, not USER_ENTERED
insertDataOption: "INSERT_ROWS"             # append after existing content
```

**IMPORTANT rules for append:**
- `valueInputOption: "RAW"` — prevents Google Sheets from interpreting `=` as formula
- `insertDataOption: "INSERT_ROWS"` — appends after existing data (preserves headers)
- Multiline text (with `\n`) is preserved — Google Sheets renders newlines in cells
- If total rows > 500 → split into chunks and call append multiple times

#### 7e: Apply Formatting

After writing data, format suite headers and test case rows using batchUpdate.

**Step 1 — Calculate row positions:**
```javascript
// Parse the append response to get the starting row
// Response: { updates: { updatedRange: "TestCases!A2:M75" } }
const startRow = 2  // from updatedRange
let currentRow = startRow

// Use dynamic values from 7c Step 3
const testCaseNameCol = columnMapping["testCaseName"]   // e.g., 3 for API_TEST
const totalCols = totalColumns                           // e.g., 13 for API_TEST

// Track which rows are suite headers vs test cases
const formatRequests = []
rows.forEach(row => {
  // Suite header: col A has value, testCaseName column is empty
  const isSuiteHeader = row[0] !== "" && row[testCaseNameCol] === ""
  if (isSuiteHeader) {
    // Format + merge for suite header
    formatRequests.push(/* repeatCell + mergeCells — endColumnIndex: totalCols */)
  } else {
    // Format for test case row
    formatRequests.push(/* repeatCell — endColumnIndex: totalCols */)
  }
  currentRow++
})
```

**Step 2 — Send batchUpdate:**
```
# MCP: google_sheets.batch_update
spreadsheetId: "{spreadsheetId}"
requests: [
  # --- Suite header row (example: row 2 = startRowIndex 1) ---
  {
    "repeatCell": {
      "range": {
        "sheetId": 0,                    # from 7c Step 2 get_spreadsheet response
        "startRowIndex": 1,              # 0-indexed: row 2 = index 1
        "endRowIndex": 2,
        "startColumnIndex": 0,
        "endColumnIndex": 13             # = totalColumns from 7c Step 3 (dynamic!)
      },
      "cell": {
        "userEnteredFormat": {
          "backgroundColor": { "red": 0.855, "green": 0.918, "blue": 0.816 },
          "textFormat": {
            "foregroundColor": { "red": 0, "green": 0, "blue": 0 },
            "bold": true,
            "fontSize": 11
          },
          "horizontalAlignment": "LEFT",
          "wrapStrategy": "WRAP",
          "borders": {
            "top": { "style": "SOLID", "color": { "red": 0.8, "green": 0.8, "blue": 0.8 } },
            "bottom": { "style": "SOLID", "color": { "red": 0.8, "green": 0.8, "blue": 0.8 } },
            "left": { "style": "SOLID", "color": { "red": 0.8, "green": 0.8, "blue": 0.8 } },
            "right": { "style": "SOLID", "color": { "red": 0.8, "green": 0.8, "blue": 0.8 } }
          }
        }
      },
      "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,wrapStrategy,borders)"
    }
  },
  {
    "mergeCells": {
      "range": {
        "sheetId": 0,
        "startRowIndex": 1,
        "endRowIndex": 2,
        "startColumnIndex": 0,
        "endColumnIndex": 13             # = totalColumns (dynamic!)
      },
      "mergeType": "MERGE_ALL"
    }
  },
  # --- Test case rows (example: rows 3-5 = startRowIndex 2, endRowIndex 5) ---
  {
    "repeatCell": {
      "range": {
        "sheetId": 0,
        "startRowIndex": 2,
        "endRowIndex": 5,
        "startColumnIndex": 0,
        "endColumnIndex": 13             # = totalColumns (dynamic!)
      },
      "cell": {
        "userEnteredFormat": {
          "backgroundColor": { "red": 1, "green": 1, "blue": 1 },
          "textFormat": {
            "foregroundColor": { "red": 0, "green": 0, "blue": 0 },
            "bold": false,
            "fontSize": 11
          },
          "horizontalAlignment": "LEFT",
          "wrapStrategy": "WRAP",
          "borders": {
            "top": { "style": "SOLID", "color": { "red": 0.8, "green": 0.8, "blue": 0.8 } },
            "bottom": { "style": "SOLID", "color": { "red": 0.8, "green": 0.8, "blue": 0.8 } },
            "left": { "style": "SOLID", "color": { "red": 0.8, "green": 0.8, "blue": 0.8 } },
            "right": { "style": "SOLID", "color": { "red": 0.8, "green": 0.8, "blue": 0.8 } }
          }
        }
      },
      "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,wrapStrategy,borders)"
    }
  }
]
```

> **Note on row indices:** Google Sheets batchUpdate uses 0-indexed row/col. Row 2 in the sheet = `startRowIndex: 1`. The `sheetId` comes from the get_spreadsheet response (usually `0` for first sheet).

**Formatting summary:**
| Element | Background | Text | Bold | Merge |
|---------|-----------|------|------|-------|
| Suite header row | `#DAEAD0` (light green) | Black, 11pt | Yes | Merge A to last col |
| Test case row | White | Black, 11pt | No | No |
| Both | Borders: solid, `rgb(0.8, 0.8, 0.8)` | Wrap text | — | — |

#### 7f: Return Result

```
✅ Đã đẩy {n} test cases lên Google Sheets.
📊 URL: https://docs.google.com/spreadsheets/d/{spreadsheetId}/edit
📋 Sheet: {sheetName}, {suiteCount} test suites, {testCaseCount} test cases
```

**If Google Sheets MCP is not available:**
- Save JSON output to a local `.json` file
- Inform user: "Google Sheets MCP không khả dụng. Đã lưu {n} test cases tại `{path}`."
- Provide manual import instructions: "Copy file vào Google Sheets hoặc kết nối MCP Google Drive/Sheets và thử lại."

#### 7g: Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Template upload fails | MCP không có quyền Drive | Kiểm tra MCP config có scope `drive.file` hoặc `drive` |
| Copy returns 404 | Template bị xóa trên Drive | Xóa cached templateFileId, upload lại (7b) |
| Copy returns 500 | Google chưa xử lý xong file upload | Đợi 2-3 giây sau upload rồi copy lại |
| Append writes wrong columns | Sai project type | Kiểm tra column mapping, so sánh với templateDefinitions.js |
| Data bị mất format | Dùng `USER_ENTERED` thay vì `RAW` | Đổi sang `valueInputOption: "RAW"` |
| Cells hiện `#REF!` | Ghi đè lên protected zone (headers/formulas) | Chỉ clear/write từ `dataStartRow` trở xuống |
| `\n` không xuống dòng | Cell chưa bật wrap text | Apply formatting với `wrapStrategy: "WRAP"` (7e) |

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
├── .cursor/skills/                    ← Managed by dev team (test-genie update)
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
│   │       └── search.py
│   └── test-design-generator/
│       └── ...
├── catalog/                           ← Managed by user/tester
│   ├── api/                              ← API test case .csv examples
│   ├── frontend/                         ← Frontend test case .csv examples
│   └── mobile/                           ← Mobile test case examples
├── excel_template/
│   └── template.xlsx                  ← Spreadsheet template for Google Sheets
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
