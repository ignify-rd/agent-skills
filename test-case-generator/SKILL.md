---
name: generate-test-case
description: Generate test case JSON from mindmap + RSD/PTTK. Use when user says "sinh test case", "sinh test cases", "generate test case", "generate test cases", "tạo test case", "tạo test cases", "xuất json test", or provides a mindmap file (.txt/.md) for test case generation.
---

# Test Case Generator

Generate test case JSON arrays from a parsed mindmap file (exported from `.gmind`). Uses a searchable catalog of real test cases (CSV format exported from spreadsheet) to ensure output matches the expected format per project.

> **Scope**: This skill covers **test case generation** (JSON output) for two pages:
> - `src/pages/api-test-generation.vue` — API test cases
> - `src/pages/fe-test-generation.vue` — Frontend test cases
>
> It does **NOT** cover test design/mindmap generation — that is handled by `rsd-to-mindmap.vue` and `rsd-to-mindmap-frontend.vue` (see `test-design-generator` skill).

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

1. **Project-level `AGENTS.md`** — `data/catalogs/{catalog}/AGENTS.md` overrides ALL skill-level rules for that project
2. **Project-level references** — `data/catalogs/{catalog}/references/*.md` override shared references
3. **Skill-level `AGENTS.md`** — `test-case-generator/AGENTS.md` (default rules)
4. **Shared references** — `references/*.md` (fallback)
5. **This SKILL.md** — workflow instructions (lowest priority, never overridden)

When a project has its own `AGENTS.md`, any rule defined there **completely replaces** the corresponding rule in the skill-level `AGENTS.md`. Rules NOT defined in the project `AGENTS.md` fall back to skill-level.

## Workflow

### Step 0: Validate Project Setup

Before starting generation, check that the catalog and project config exist:

1. **Detect catalog** — if user specifies `--catalog {name}`, check if `data/catalogs/{name}/` exists
2. **Check AGENTS.md** — look for `data/catalogs/{name}/AGENTS.md` (project-level override rules)
3. **Check references** — look for `data/catalogs/{name}/references/` (project-level reference overrides)
4. **Check template** — look for `data/catalogs/{name}/templates/template.xlsx` (project-level spreadsheet template)

**If catalog folder does not exist:**
- Ask user: "Catalog `{name}` chưa tồn tại. Bạn muốn tạo mới với cấu trúc mặc định không?"
- If yes → scaffold using `test-genie scaffold --catalog {name}` or create manually (see "Create a New Catalog" section)
- If no → fall back to `default` catalog

**If AGENTS.md does not exist in catalog:**
- Use skill-level `AGENTS.md` (default rules)
- Inform user: "Project `{name}` chưa có AGENTS.md riêng. Đang dùng rules mặc định. Bạn có muốn tạo AGENTS.md cho project này không?"

**If catalog exists but has no examples (empty api/ and frontend/):**
- Warn user: "Catalog `{name}` chưa có examples. Output có thể không chính xác format. Bạn có muốn thêm CSV examples trước không?"
- Proceed with shared references as fallback

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
- Codex: `${CODEX_HOME:-~/.codex}/skills/test-case-generator/scripts/search.py`

```bash
# Load priority rules (MUST load first)
python <skills-root>/test-case-generator/scripts/search.py --ref priority-rules

# Load generation rules
python <skills-root>/test-case-generator/scripts/search.py --ref api-test-case    # API mode
python <skills-root>/test-case-generator/scripts/search.py --ref fe-test-case     # Frontend mode
python <skills-root>/test-case-generator/scripts/search.py --ref output-format
python <skills-root>/test-case-generator/scripts/search.py --ref quality-rules

# For a specific project catalog
python <skills-root>/test-case-generator/scripts/search.py --ref api-test-case --catalog project-x

# List all available references (shows which are overridden)
python <skills-root>/test-case-generator/scripts/search.py --list-refs
python <skills-root>/test-case-generator/scripts/search.py --list-refs --catalog project-x

# Search API examples
python <skills-root>/test-case-generator/scripts/search.py "search list validate" --domain api

# Search Frontend examples
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
These references are resolved per-catalog: if the catalog has its own `references/` folder, those files take priority over the shared defaults.

### Step 7: Output to Spreadsheet

Output is a **spreadsheet file** (not raw JSON). The skill generates JSON internally, then inserts it into a template and uploads to Google Sheets.

#### 7a: Generate JSON Array (internal)

Generate a JSON array. Each element is one test case object following the schema loaded via `--ref output-format`.

```json
[
  {
    "externalId": "",
    "testSuiteName": "...",
    "testSuiteDetails": "",
    "testCaseName": "...",
    "summary": "...",
    "preConditions": "...",
    "step": "...",
    "expectedResult": "...",
    "importance": "Low|Medium|High",
    "specTitle": "",
    "documentId": "",
    "estimatedDuration": "",
    "result": "PENDING",
    "note": ""
  }
]
```

#### 7b: Detect Template Structure

Template location (per-catalog override supported):
```bash
# Resolution order:
# 1. data/catalogs/{catalog}/templates/template.xlsx  (catalog-specific)
# 2. data/templates/template.xlsx                      (shared default)
```

**CRITICAL: Do NOT hardcode any row numbers, column letters, or sheet names.** The template structure is fully dynamic and varies per project. Detect everything by reading the actual file.

**Detection algorithm:**

1. **Open template** — read the `.xlsx` file, list all sheet names
2. **Identify the data sheet** — find the sheet that contains test case data (may not be the first sheet, may have any name)
3. **Find header row(s)** — scan all rows top-to-bottom, look for rows where multiple cells match known column label patterns:

   | JSON field | Possible header labels (case-insensitive, partial match OK) |
   |-----------|-------------------------------------------------------------|
   | testSuiteName | "Test Suite", "Suite Name", "Name" (in suite context) |
   | externalId | "External ID", "ID", "Mã" |
   | testCaseName | "Test Case", "Name" (in test case context), "Tên" |
   | summary | "Summary", "Tóm tắt" |
   | preConditions | "PreConditions", "Pre Conditions", "Điều kiện" |
   | importance | "Importance", "Priority", "Mức độ" |
   | step | "Step", "Steps", "Bước" |
   | expectedResult | "Expected Result", "Expected", "Kết quả mong đợi" |
   | result | "Result", "Kết quả" |
   | note | "Note", "Ghi chú" |

   Headers may span **multiple rows** (merged cells for group headers on row N, detail headers on row N+1). Detect both levels.

4. **Build column mapping** — for each detected header label, record its column letter. Only map columns that actually exist in this template. If a JSON field has no matching column → skip it (do not error).

5. **Find protected zone** — all rows ABOVE the header row(s) are the protected zone (summary area, formulas, metadata). Record this range. It may be 0 rows (header at row 1) or 20+ rows.

6. **Find data start row** — first row after headers. Check if it's empty or has existing data:
   - Empty → this is where insertion begins
   - Has data → find the first empty row after existing data (append mode)

7. **Detect preserved elements** — record merged cells, formula cells, conditional formatting, data validation rules anywhere in the sheet. These must not be overwritten.

**Output of detection** — a structure like:
```json
{
  "sheetName": "(detected)",
  "headerRows": [15, 16],
  "protectedZone": "1:17",
  "dataStartRow": 18,
  "columnMapping": {
    "testSuiteName": "A",
    "externalId": "F",
    "testCaseName": "G",
    "...": "..."
  },
  "mergedCells": ["A15:B15", "..."],
  "formulaCells": ["C6", "D6", "..."]
}
```

#### 7c: Insert Test Cases into Template

For each test case in the JSON array:
1. Map JSON fields to template columns using the column mapping from 7b. Skip any JSON field that has no mapped column.
2. Write each test case to the next available row starting from data start row
3. **Preserve the protected zone** — never write to any row in the protected zone (summary, formulas, metadata above headers)
4. **Preserve merged cells** — do not break existing merged cell ranges
5. **Preserve formulas** — do not overwrite cells that contain formulas (they typically reference the data range and auto-update)
6. If template has existing data rows, append after the last existing row

#### 7d: Upload to Google Sheets via MCP

Use the Google Drive MCP server to upload the populated spreadsheet:

1. **Check MCP availability** — verify Google Drive MCP server is connected
2. **Upload** the populated `.xlsx` file to Google Drive
3. **Convert** to Google Sheets format (if supported by MCP)
4. **Return** the Google Sheets URL to the user

If MCP is not available or upload fails:
- Save the populated `.xlsx` file locally
- Inform user of the local file path
- Ask if they want to retry upload or use the local file

## Catalog Management

### Catalog Format

Catalogs are **CSV files** exported from the project spreadsheet. Each row = one test case.

Expected CSV columns (must match):
```
externalId,testSuiteName,testCaseName,preConditions,step,expectedResult,importance
```

### Add Examples to Catalog

1. Export test cases from Google Sheets / Excel as CSV (UTF-8)
2. Place in `data/catalogs/{catalog_name}/api/` or `data/catalogs/{catalog_name}/frontend/`
3. The search engine will automatically index it

### Switch Catalog (per-project)

```bash
python <skills-root>/test-case-generator/scripts/search.py "keyword" --catalog other-project
```

### Create a New Catalog for Another Project

Use the `_template` scaffold:
```bash
# Copy the entire template scaffold
cp -r <skills-root>/test-case-generator/data/catalogs/_template <skills-root>/test-case-generator/data/catalogs/new-project

# Edit AGENTS.md — replace {PROJECT_NAME}, uncomment and customize rules
# Add CSV examples to api/ and frontend/
# Optionally override references in references/
# Optionally add a custom template.xlsx in templates/
```

Or create manually:
```bash
mkdir -p <skills-root>/test-case-generator/data/catalogs/new-project/{api,frontend,references,templates}
```

The `_template` scaffold includes:
```
_template/
├── AGENTS.md          ← Project-specific rule overrides (commented template)
├── api/.gitkeep       ← API test case CSV examples
├── frontend/.gitkeep  ← Frontend test case CSV examples
├── references/.gitkeep ← Override shared references
└── templates/.gitkeep  ← Override spreadsheet template
```

## References per-Catalog

References (rules, format specs, quality checks) support **per-catalog overrides** with shared fallback:

### Resolution Order

1. `data/catalogs/{catalog}/references/{file}.md` — catalog-specific (highest priority)
2. `references/{file}.md` — shared fallback (default)

### How to Override References for a Project

```bash
# 1. Copy the shared reference you want to customize
cp references/output-format.md data/catalogs/my-project/references/output-format.md

# 2. Edit to match project-specific format (e.g., different JSON schema, importance mapping)
# 3. When using --catalog my-project, the overridden file will be loaded automatically
```

### Check Which References Are Active

```bash
python <skills-root>/test-case-generator/scripts/search.py --list-refs --catalog my-project
# Output shows: OVERRIDE (catalog-specific), shared (fallback), or catalog-only
```

## Data Structure

```
test-case-generator/
├── SKILL.md               ← Workflow instructions (this file)
├── AGENTS.md              ← Skill-level override rules
├── references/            ← Shared references & rules (fallback for all catalogs)
│   ├── priority-rules.md     ← PTTK vs RSD priority rules
│   ├── api-test-case.md      ← API test case generation rules
│   ├── fe-test-case.md       ← Frontend test case generation rules
│   ├── output-format.md      ← JSON output schema & examples
│   └── quality-rules.md      ← Quality & language rules
├── data/
│   ├── templates/
│   │   └── template.xlsx     ← Default spreadsheet template
│   └── catalogs/
│       ├── _template/        ← Scaffold for new projects (cp -r to create new catalog)
│       │   ├── AGENTS.md        ← Project-level rule overrides (commented template)
│       │   ├── api/
│       │   ├── frontend/
│       │   ├── references/
│       │   └── templates/
│       ├── default/
│       │   ├── AGENTS.md     ← Project-level rule overrides (optional)
│       │   ├── api/           ← API test case .csv examples
│       │   ├── frontend/      ← Frontend test case .csv examples
│       │   ├── references/    ← Override references for default catalog (optional)
│       │   └── templates/     ← Override template for this catalog (optional)
│       └── {other-project}/
│           ├── AGENTS.md     ← Project-level rule overrides
│           ├── api/
│           ├── frontend/
│           ├── references/
│           └── templates/
├── scripts/
│   └── search.py
```

## Key Format Differences: API vs Frontend

| Aspect | API Test Cases | Frontend Test Cases |
|--------|---------------|---------------------|
| `preConditions` | API endpoint + headers + body | Screen navigation path + login |
| `step` | API method/params changes | UI interactions (click, type, select) |
| `expectedResult` | HTTP status + JSON response | UI state (displayed, enabled, visible) |
| `testCaseName` | With prefix (e.g., "Phân quyền_...") | No prefix, direct from mindmap |
| External ID hint | API_1, API_2... | FE_1, FE_2... |
