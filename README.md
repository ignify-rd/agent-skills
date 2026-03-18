██╗ ██████╗ ███╗   ██╗    ███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██║██╔════╝ ████╗  ██║    ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
██║██║  ███╗██╔██╗ ██║    ███████╗█████╔╝ ██║██║     ██║     ███████╗
██║██║   ██║██║╚██╗██║    ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
██║╚██████╔╝██║ ╚████║    ███████║██║  ██╗██║███████╗███████╗███████║
╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

[![CI](https://github.com/ignify-rd/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/ignify-rd/agent-skills/actions/workflows/ci.yml)

A collection of AI skill apps. Each app ships one or more skills that extend your AI assistant's capabilities.

## Apps

### test-genie

Skills for software testing workflows.

| Skill | Description |
|-------|-------------|
| `generate-test-case` | Generate test case JSON arrays from mindmap files |
| `generate-test-design` | Generate test design documents (mindmap .md) from RSD/PTTK |

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

- `/generate-test-case` — generate test case JSON from a mindmap file
- `/generate-test-design` — generate a test design mindmap from RSD/PTTK

For Codex, these are skills, not slash commands. Ask naturally instead:

- `Generate test cases from this mindmap`
- `Use the generate-test-case skill on this file`
- `Generate a test design from this RSD`
