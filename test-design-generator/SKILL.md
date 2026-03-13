---
name: test-design-generator
description: Generate test design documents (mindmap .md) from RSD/PTTK. Searches catalog of real examples by keyword to find matching reference. Use when user says "generate test design", "sinh test design", "tao mindmap", "tạo test design", or provides RSD/PTTK documents for mindmap generation.
---

# Test Design Generator

Generate comprehensive test design documents (.md) from RSD and optional PTTK. Uses a searchable catalog of real test design examples to ensure output matches the correct format per project.

> **Scope**: This skill covers **test design** (mindmap output) for two pages:
> - `src/pages/rsd-to-mindmap.vue` — API test design
> - `src/pages/rsd-to-mindmap-frontend.vue` — Frontend test design (with optional image analysis)
>
> It does **NOT** cover test case generation (JSON/Excel output) — that is handled by `api-test-generation.vue` and `fe-test-generation.vue`.

## When to Apply

- User provides RSD/PTTK and asks to generate test design or mindmap
- User says "sinh test design", "tạo test design", "tạo mindmap", "tao mindmap"
- User uploads .docx/.pdf/.txt/.md files for test design / mindmap generation

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## Workflow

### Step 1: Determine Mode

| Input | Mode | Output |
|-------|------|--------|
| RSD describes an API endpoint | API | Markdown test design for API |
| RSD describes a UI screen | Frontend | Markdown test design for Frontend |

### Step 2: Search Catalog for Reference Examples

**Always search for relevant examples first** to understand the expected output format:

```bash
# Search API examples by keyword
python .claude/skills/test-design-generator/scripts/search.py "search list api" --domain api

# Search Frontend examples
python .claude/skills/test-design-generator/scripts/search.py "danh sach list screen" --domain frontend

# Search format rules
python .claude/skills/test-design-generator/scripts/search.py "common section status" --domain rules

# List all available examples
python .claude/skills/test-design-generator/scripts/search.py --list

# Read full content of top match
python .claude/skills/test-design-generator/scripts/search.py "export excel" --domain api --full
```

### Step 3: Read the Top-Matching Example

After search returns results, **read the full example file** to understand the exact format:

```bash
# search.py returns the full_path — use view_file on it
```

### Step 4: Generate Test Design Following the Example

Generate the test design following the exact format of the reference example:

#### API Mode
1. Read RSD → extract fields (name, type, required, maxLength, enum values)
2. Read PTTK (if provided) → extract response structure, business logic, DB mappings
3. Generate output following the reference example's exact format

#### Frontend Mode
1. Read RSD → extract screen type, fields, grid, pagination, permissions
2. Read PTTK (if provided) → merge field details
3. Generate output following the reference example's exact format

### Step 5: Apply Format Rules

Search and verify against rules:
```bash
python .claude/skills/test-design-generator/scripts/search.py "format status response" --domain rules
```

## Catalog Management

### Switch Catalog (per-project)

Each project can have its own catalog of reference examples:

```bash
# Use a different project's catalog
python .claude/skills/test-design-generator/scripts/search.py "keyword" --catalog other-project

# List examples in a specific catalog
python .claude/skills/test-design-generator/scripts/search.py --list --catalog other-project
```

### Add Examples to Catalog

To add new reference examples:
1. Save the test design output as a `.md` file
2. Place it in `data/catalogs/{catalog_name}/api/` or `data/catalogs/{catalog_name}/frontend/`
3. The search engine will automatically index it

### Create a New Catalog for Another Project

```bash
# Create new catalog folder
mkdir -p .claude/skills/test-design-generator/data/catalogs/new-project/api
mkdir -p .claude/skills/test-design-generator/data/catalogs/new-project/frontend

# Copy relevant examples
cp reference-test-design.md .claude/skills/test-design-generator/data/catalogs/new-project/api/
```

## Data Structure

```
data/
├── catalogs/
│   ├── default/           ← Current project's examples
│   │   ├── api/           ← API test design .md files
│   │   └── frontend/      ← Frontend test design .md files
│   └── {other-project}/   ← Another project's examples
│       ├── api/
│       └── frontend/
└── rules/
    └── api-rules.csv      ← Format rules (shared across projects)
```

## Key Format Rules (Quick Reference)

### API Test Design

| Section | Format |
|---------|--------|
| Common | `- status: 107` (simple, NO `1\. Check api trả về:`) |
| Validate | `- 1\. Check api trả về: 1\.1. Status: 200 1\.2. Response: {...}` |
| Luồng chính | Same as validate — MUST include Response JSON |

### Critical Rules
- Output starts with `# {API_NAME}` — NO blockquote header
- NO `---` horizontal rules between sections
- ALL validate responses use Status: 200 (errors in body)
- SQL uses concrete values, UPPERCASE columns, NO placeholders
- Response body format comes from PTTK (no fixed format)
