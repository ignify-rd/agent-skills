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

### Step 2: Load References & Search Catalog

**Always load the project-specific references first**, then search for examples:

```bash
# Read reference files (auto-resolves: catalog-specific → shared fallback)
python .claude/skills/test-design-generator/scripts/search.py --ref api-test-design
python .claude/skills/test-design-generator/scripts/search.py --ref frontend-test-design
python .claude/skills/test-design-generator/scripts/search.py --ref field-templates

# For a specific project catalog
python .claude/skills/test-design-generator/scripts/search.py --ref api-test-design --catalog project-x

# List all available references (shows which are overridden)
python .claude/skills/test-design-generator/scripts/search.py --list-refs
python .claude/skills/test-design-generator/scripts/search.py --list-refs --catalog project-x

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

Generate the test design following the references loaded via `--ref` and the format of the catalog examples.
References are resolved per-catalog: if the catalog has its own `references/` folder, those files take priority over the shared defaults.

#### API Mode
1. Read RSD → extract fields (name, type, required, maxLength, enum values)
2. Read PTTK (if provided) → extract response structure, business logic, DB mappings
3. Generate output following the reference example's exact format

#### Frontend Mode
1. Read RSD → extract screen type, fields, grid, pagination, permissions
2. Read PTTK (if provided) → merge field details
3. Generate output following the reference example's exact format

### Step 5: Apply Format Rules

Load quality rules and verify:
```bash
# Load quality rules (per-catalog with fallback)
python .claude/skills/test-design-generator/scripts/search.py --ref quality-rules

# Search format rules in CSV
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
mkdir -p .claude/skills/test-design-generator/data/catalogs/new-project/references

# Copy relevant examples
cp reference-test-design.md .claude/skills/test-design-generator/data/catalogs/new-project/api/

# Optionally override references for this project
cp references/api-test-design.md data/catalogs/new-project/references/
cp references/field-templates.md data/catalogs/new-project/references/
# Edit the copied files to match the new project's format
```

## References per-Catalog

References (rules, templates, format specs) support **per-catalog overrides** with shared fallback:

### Resolution Order

1. `data/catalogs/{catalog}/references/{file}.md` — catalog-specific (highest priority)
2. `references/{file}.md` — shared fallback (default)

### How to Override References for a Project

```bash
# 1. Copy the shared reference you want to customize
cp references/api-test-design.md data/catalogs/my-project/references/api-test-design.md

# 2. Edit to match project-specific format (e.g., different base template, field templates, quality rules)
# 3. When using --catalog my-project, the overridden file will be loaded automatically
```

### Check Which References Are Active

```bash
python .claude/skills/test-design-generator/scripts/search.py --list-refs --catalog my-project
# Output shows: OVERRIDE (catalog-specific), shared (fallback), or catalog-only
```

## Data Structure

```
test-design-generator/
├── references/            ← Shared references (fallback for all catalogs)
│   ├── api-test-design.md
│   ├── frontend-test-design.md
│   ├── field-templates.md
│   ├── output-examples.md
│   └── quality-rules.md
├── data/
│   ├── catalogs/
│   │   ├── default/
│   │   │   ├── api/           ← API test design .md examples
│   │   │   ├── frontend/      ← Frontend test design .md examples
│   │   │   └── references/    ← Override references for default catalog (optional)
│   │   └── {other-project}/
│   │       ├── api/
│   │       ├── frontend/
│   │       └── references/    ← Override references for this project
│   │           ├── api-test-design.md     ← Custom base template
│   │           ├── field-templates.md     ← Custom field templates
│   │           └── quality-rules.md       ← Custom quality rules
│   └── rules/
│       └── api-rules.csv     ← Format rules (shared across projects)
└── scripts/
    └── search.py
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
