---
name: test-case-generator
description: Generate test case JSON from mindmap + RSD/PTTK. Use when user says "sinh test cases", "generate test cases", "tạo test cases", "xuất json test", or provides a mindmap file (.txt/.md) for test case generation.
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
- User says "sinh test cases", "tạo test cases", "generate test cases", "xuất json"
- User uploads mindmap + optional RSD/PTTK for test case generation

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## Workflow

### Step 1: Determine Mode

| Mindmap content | Mode | Output |
|-----------------|------|--------|
| API name + endpoint references | API | JSON test cases for API |
| Screen name + UI section names | Frontend | JSON test cases for Frontend |

**Clues for API mode:** First line is API name, sections include "case common", "phân quyền", "validate", field names are request params (PAR_TYPE, REG_CHANNEL...).

**Clues for Frontend mode:** First line is screen name (e.g., "WEB_BO_Danh mục > ..."), sections include "giao diện chung", "phân quyền", "validate", "lưới dữ liệu", "chức năng".

### Step 2: Search Catalog for Reference Examples

**Always search for relevant examples first** to understand the expected output format for this project:

```bash
# Search API examples
python .claude/skills/test-case-generator/scripts/search.py "search list validate" --domain api

# Search Frontend examples
python .claude/skills/test-case-generator/scripts/search.py "giao dien chung phan quyen" --domain frontend

# List all available examples
python .claude/skills/test-case-generator/scripts/search.py --list

# Read full content of top match
python .claude/skills/test-case-generator/scripts/search.py "validate string field" --domain api --full
```

### Step 3: Read the Mindmap

Parse the mindmap structure:
- **Line 1**: API name / Screen name → used in `preConditions`
- **## headings**: Test suites → `testSuiteName`
- **### headings**: Sub-sections / Field names → grouping
- **- bullet items**: Test case descriptions → `testCaseName`

### Step 4: Extract RSD Context (API Mode Only)

If RSD/PTTK files are provided:
1. Extract the request body structure (field names, types, required status, example values)
2. Use this to build the `preConditions` body in all test cases
3. Priority: PTTK > RSD

### Step 5: Generate Test Cases in 3 Batches

Follow the 3-batch strategy defined in the reference files:

- **BATCH 1**: Pre-validate sections (common cases, permissions)
- **BATCH 2**: Validate section — one sub-batch PER FIELD (### heading)
- **BATCH 3**: Post-validate sections (grid, pagination, functionality, timeout)

Generate following rules in `references/api-test-case.md` (API) or `references/fe-test-case.md` (Frontend).

### Step 6: Output JSON

Output a JSON array. Each element is one test case object following the schema in `references/output-format.md`.

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
python .claude/skills/test-case-generator/scripts/search.py "keyword" --catalog other-project
```

### Create a New Catalog for Another Project

```bash
mkdir -p .claude/skills/test-case-generator/data/catalogs/new-project/api
mkdir -p .claude/skills/test-case-generator/data/catalogs/new-project/frontend
# Copy relevant CSV files
cp exported-test-cases.csv .claude/skills/test-case-generator/data/catalogs/new-project/api/
```

## Data Structure

```
data/
└── catalogs/
    ├── default/           ← Current project's examples (CSV from spreadsheet)
    │   ├── api/           ← API test case .csv files
    │   └── frontend/      ← Frontend test case .csv files
    └── {other-project}/   ← Another project's examples
        ├── api/
        └── frontend/
```

## Key Format Differences: API vs Frontend

| Aspect | API Test Cases | Frontend Test Cases |
|--------|---------------|---------------------|
| `preConditions` | API endpoint + headers + body | Screen navigation path + login |
| `step` | API method/params changes | UI interactions (click, type, select) |
| `expectedResult` | HTTP status + JSON response | UI state (displayed, enabled, visible) |
| `testCaseName` | With prefix (e.g., "Phân quyền_...") | No prefix, direct from mindmap |
| External ID hint | API_1, API_2... | FE_1, FE_2... |
