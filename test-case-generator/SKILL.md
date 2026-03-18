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

## Workflow

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

### Step 7: Output JSON

Output a JSON array. Each element is one test case object following the schema loaded via `--ref output-format`.

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

```bash
mkdir -p <skills-root>/test-case-generator/data/catalogs/new-project/api
mkdir -p <skills-root>/test-case-generator/data/catalogs/new-project/frontend
mkdir -p <skills-root>/test-case-generator/data/catalogs/new-project/references
# Copy relevant CSV files
cp exported-test-cases.csv <skills-root>/test-case-generator/data/catalogs/new-project/api/
# Optionally override references for this project
cp <skills-root>/test-case-generator/references/output-format.md <skills-root>/test-case-generator/data/catalogs/new-project/references/
# Edit the copied file to match the new project's format
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
├── references/            ← Shared references & rules (fallback for all catalogs)
│   ├── priority-rules.md     ← PTTK vs RSD priority rules
│   ├── api-test-case.md      ← API test case generation rules
│   ├── fe-test-case.md       ← Frontend test case generation rules
│   ├── output-format.md      ← JSON output schema & examples
│   └── quality-rules.md      ← Quality & language rules
├── data/
│   └── catalogs/
│       ├── default/
│       │   ├── api/           ← API test case .csv examples
│       │   ├── frontend/      ← Frontend test case .csv examples
│       │   └── references/    ← Override references for default catalog (optional)
│       └── {other-project}/
│           ├── api/
│           ├── frontend/
│           └── references/    ← Override references for this project
├── scripts/
│   └── search.py
└── SKILL.md
```

## Key Format Differences: API vs Frontend

| Aspect | API Test Cases | Frontend Test Cases |
|--------|---------------|---------------------|
| `preConditions` | API endpoint + headers + body | Screen navigation path + login |
| `step` | API method/params changes | UI interactions (click, type, select) |
| `expectedResult` | HTTP status + JSON response | UI state (displayed, enabled, visible) |
| `testCaseName` | With prefix (e.g., "Phân quyền_...") | No prefix, direct from mindmap |
| External ID hint | API_1, API_2... | FE_1, FE_2... |
