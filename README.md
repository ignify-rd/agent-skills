# agent-skills

[![CI](https://github.com/ignify-rd/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/ignify-rd/agent-skills/actions/workflows/ci.yml)

A collection of AI skill apps. Each app ships one or more skills that extend your AI assistant's capabilities.

## Apps

### test-genie

Skills for software testing workflows.

| Skill | Description |
|-------|-------------|
| `test-case-generator` | Generate test case JSON arrays from mindmap files |
| `test-design-generator` | Generate test design documents (mindmap .md) from RSD/PTTK |

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
test-genie init --ai codex       # Codex CLI      → .codex/skills/
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

#### How it works

Running `test-genie init --ai <type>` installs the following into your project's AI config directory:

```
# Example: --ai claude
.claude/
└── skills/
    ├── test-case-generator/   ← Generate test case JSON from mindmaps
    └── test-design-generator/ ← Generate test design mindmaps from RSD/PTTK

# Example: --ai cursor
.cursor/
└── rules/
    ├── test-case-generator/
    └── test-design-generator/
```

Once installed, activate a skill in your AI assistant by describing your task — the assistant will automatically apply the appropriate skill.
