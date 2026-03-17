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
# Install for Claude Code
test-genie init --ai claude
```

This copies the skills into `.claude/skills/` in your current directory. Claude will automatically load them.

#### Commands

```bash
# Install skills for your AI assistant
test-genie init --ai claude

# Check available versions
test-genie versions

# Update skills to the latest version
test-genie update --ai claude
```

#### How it works

Running `test-genie init --ai claude` installs the following into your project:

```
.claude/
└── skills/
    ├── test-case-generator/   ← Generate test case JSON from mindmaps
    └── test-design-generator/ ← Generate test design mindmaps from RSD/PTTK
```

Once installed, activate a skill in Claude by describing your task — Claude will automatically apply the appropriate skill.
