```
 █████╗  ██████╗ ███████╗███╗   ██╗████████╗    ███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝    ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║       ███████╗█████╔╝ ██║██║     ██║     ███████╗
██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║       ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║       ███████║██║  ██╗██║███████╗███████╗███████║
╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝       ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝                                          
```

[![CI](https://github.com/ignify-rd/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/ignify-rd/agent-skills/actions/workflows/ci.yml)

A collection of AI skill apps. Each app ships one or more skills that extend your AI assistant's capabilities.

## Apps

### test-genie

Skills for software testing workflows — generate test designs and test cases from RSD/PTTK documents.

| Skill | Description |
|-------|-------------|
| `generate-test-design` | RSD/PTTK → test design mindmap (.md) |
| `generate-test-case` | Mindmap → test cases → spreadsheet (Google Sheets) |

#### Workflow Overview

```
RSD + PTTK (+ images)
       │
       ▼
┌──────────────────┐
│ generate-test-   │  Step 1: Extract business logic (RSD) + field definitions (PTTK)
│ design           │  Step 2: Generate test design mindmap (.md)
└────────┬─────────┘
         │ .md mindmap
         ▼
┌──────────────────┐
│ generate-test-   │  Step 1: Parse mindmap sections
│ case             │  Step 2: Generate test cases (3 batches)
│                  │  Step 3: Insert into template → upload to Google Sheets
└────────┬─────────┘
         │
         ▼
   Google Sheets URL
```

Both skills can run independently or chained. `generate-test-case` auto-invokes `generate-test-design` when no mindmap is provided.

#### Key Concepts

- **PTTK wins** for field definitions, request/response structure
- **RSD wins** for business logic, error codes, main flow
- **Per-project customization** via catalog system (rules, references, templates, examples)
- **Agent asks** when documents are missing info, have conflicts, or are ambiguous

#### Installation

```bash
npm install -g git+https://github.com/ignify-rd/agent-skills.git
```

#### Setup

```bash
# Install for a specific AI assistant
test-genie init --ai claude      # Claude Code   → .claude/skills/
test-genie init --ai cursor      # Cursor         → .cursor/rules/
test-genie init --ai windsurf    # Windsurf       → .windsurf/rules/
test-genie init --ai antigravity # Antigravity    → .agent/skills/
test-genie init --ai copilot     # GitHub Copilot → .github/copilot-skills/
test-genie init --ai kiro        # Kiro           → .kiro/rules/
test-genie init --ai codex       # Codex CLI      → $CODEX_HOME/skills or ~/.codex/skills/
test-genie init --ai qoder       # Qoder          → .qoder/rules/
test-genie init --ai roocode     # Roo Code       → .roo/rules/
test-genie init --ai gemini      # Gemini CLI     → .gemini/skills/
test-genie init --ai trae        # Trae           → .trae/rules/
test-genie init --ai opencode    # OpenCode       → .opencode/skills/
test-genie init --ai continue    # Continue       → .continue/skills/
test-genie init --ai codebuddy   # CodeBuddy      → .codebuddy/skills/
test-genie init --ai droid       # Droid (Factory)→ .factory/skills/
test-genie init --ai all         # All assistants above
```

#### Commands

```bash
# Install skills for your AI assistant
test-genie init --ai <type>

# Check available versions
test-genie versions

# Update skills to the latest version
test-genie update --ai <type>
```

#### Usage

After running `test-genie init`, use these commands in your AI assistant:

- `/generate-test-case` — generate test cases from mindmap → spreadsheet
- `/generate-test-design` — generate test design mindmap from RSD/PTTK

For Codex, these are skills, not slash commands. Ask naturally instead:

- `Generate test cases from this mindmap`
- `Use the generate-test-case skill on this file`
- `Generate a test design from this RSD`

#### Starting a New Project

Each project gets its own catalog with custom rules, examples, references, and templates.

```bash
# 1. Copy the template scaffold
cp -r <skills-root>/test-case-generator/data/catalogs/_template \
      <skills-root>/test-case-generator/data/catalogs/my-project
cp -r <skills-root>/test-design-generator/data/catalogs/_template \
      <skills-root>/test-design-generator/data/catalogs/my-project

# 2. Edit AGENTS.md in each — set project-specific rules
# 3. Add example CSVs (test-case) and .md files (test-design)
# 4. Optionally override references/ and templates/
```

Catalog structure per skill:
```
data/catalogs/my-project/
├── AGENTS.md          ← Project rules (overrides skill-level AGENTS.md)
├── api/               ← Example files for API mode
├── frontend/          ← Example files for Frontend mode
├── references/        ← Override shared references (optional)
└── templates/         ← Override spreadsheet template (test-case only, optional)
```

#### Rule Override Hierarchy

Rules resolve top-down (highest priority first):

1. Project `AGENTS.md` — `data/catalogs/{project}/AGENTS.md`
2. Project references — `data/catalogs/{project}/references/*.md`
3. Skill `AGENTS.md` — `{skill}/AGENTS.md`
4. Shared references — `{skill}/references/*.md`
5. SKILL.md — workflow instructions (never overridden)
