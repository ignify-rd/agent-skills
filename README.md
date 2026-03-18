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
- **Per-project customization** via `AGENTS.md` at project root
- **Catalog system** — add CSV/MD examples to help AI match your format
- **Agent asks** when documents are missing info, have conflicts, or are ambiguous

#### Installation

```bash
npm install -g git+https://github.com/ignify-rd/agent-skills.git
```

#### Setup

```bash
cd /path/to/your/project

# Install for a specific AI assistant
test-genie init --ai claude      # Claude Code   → .claude/skills/
test-genie init --ai cursor      # Cursor         → .cursor/skills/
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

#### What `init` Creates

```
<project>/
├── .cursor/skills/                ← AI skills (managed by dev team)
│   ├── test-case-generator/
│   │   ├── SKILL.md
│   │   ├── AGENTS.md
│   │   ├── references/
│   │   └── scripts/
│   └── test-design-generator/
│       ├── SKILL.md
│       ├── AGENTS.md
│       ├── references/
│       ├── data/rules/
│       └── scripts/
├── catalog/                       ← Project examples (managed by user)
│   ├── api/
│   ├── frontend/
│   └── mobile/
├── excel_template/
│   └── template.xlsx
└── AGENTS.md                      ← Project rules (managed by user)
```

**Skills** (inside `.cursor/skills/`) are managed by the dev team. Run `test-genie update` to get the latest version.

**Project data** (`catalog/`, `excel_template/`, `AGENTS.md`) is managed by the user. These files are never overwritten by `update`.

#### Commands

```bash
# Install skills + project structure
test-genie init --ai <type>

# Check available versions
test-genie versions

# Update skills to the latest version (does not touch project data)
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

#### Adding Project Examples

Add examples to help AI match your project's format:

```bash
# Test case examples (CSV exported from Google Sheets)
catalog/api/my-api-tests.csv
catalog/frontend/my-frontend-tests.csv

# Test design examples (MD output from previous generations)
catalog/api/my-api-design.md
catalog/frontend/my-screen-design.md
```

#### Customizing Rules

Edit `AGENTS.md` at your project root to customize behavior:

```markdown
## Project-Specific Rules

- Response body uses "code"/"message" instead of "errorCode"/"errorDesc"
- All API test cases must include X-Request-ID header
- Custom template type: HOME
```

#### Rule Override Hierarchy

Rules resolve top-down (highest priority first):

1. Project `AGENTS.md` — at project root (user-managed)
2. Skill `AGENTS.md` — inside skill folder (dev-managed)
3. Skill references — `references/*.md` (dev-managed)
4. SKILL.md — workflow instructions (never overridden)
