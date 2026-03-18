# Agent Rules

## Skills Overview

This repo contains two complementary skills for test generation:

```
RSD/PTTK + Images
        ↓
  test-design-generator     ← Generates test design mindmap (.md)
        ↓
  test-case-generator       ← Generates test case JSON from mindmap
        ↓
  JSON test cases
```

- **test-design-generator**: RSD/PTTK → markdown mindmap (test design)
- **test-case-generator**: mindmap → JSON test cases. If no mindmap provided, auto-invokes test-design-generator first.

## Input Priority Rules (applies to BOTH skills)

| Source | Priority | Used for |
|--------|----------|----------|
| **PTTK** | **Highest** for field definitions | Field names, data types, required/optional, maxLength, format constraints, request/response structure, API endpoints, DB mappings |
| **RSD** | **Highest** for business logic | Main flow, error codes, if/else branches, screen flow, permissions, DB mapping logic |

**When PTTK is available, IGNORE field definitions, request body, and response body in RSD.**

PTTK is typically the larger document and contains more APIs — always find the EXACT API/screen by endpoint or name before extracting.

## Skill Rules Loading

Both skills use `search.py --ref` to load rules from `references/`. Always load in this order:

```bash
# 1. Priority rules (MUST load first)
python <skills-root>/<skill>/scripts/search.py --ref priority-rules

# 2. Generation rules (mode-specific)
python <skills-root>/<skill>/scripts/search.py --ref api-test-design    # or api-test-case
python <skills-root>/<skill>/scripts/search.py --ref quality-rules

# 3. Catalog examples
python <skills-root>/<skill>/scripts/search.py "keyword" --domain api
```

## Per-Catalog Overrides

Each project can override any reference file:

```
references/priority-rules.md                          ← shared default
data/catalogs/{project}/references/priority-rules.md  ← project override (wins)
```

Resolution: catalog-specific → shared fallback.

## Language & Format

- All test output in Vietnamese
- Keep field/button names exactly as in RSD/PTTK (do not translate)
- Technical terms (API, HTTP, JSON, SQL) stay in English
- No placeholders: use concrete sample values
- 1 test = 1 check (atomic)
