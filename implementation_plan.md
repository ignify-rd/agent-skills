# Build `execute-test-case-api` & `execute-test-case-frontend` Skills

Two new agent skills that **execute** test cases (not generate them). They read test cases from Google Sheets, run them (API calls or browser interactions), capture evidence, and write results back.

## Design Decisions

### MCP Servers Used

| Capability | MCP Server | Why |
|---|---|---|
| Google Sheets R/W | **gdrive MCP** (already configured in your environment) | You already have `gdrive` and `gsheets` MCP servers connected — we use the existing tools (`read_spreadsheet`, `write_spreadsheet`, etc.) |
| Google Drive (screenshot storage) | **gdrive MCP** (`upload_file`, `create_file`) | Same MCP already available for file uploads |
| Browser automation (frontend) | **Playwright MCP** (`@playwright/mcp`) | First-class Playwright tools: `goto`, `click`, `fill`, `screenshot`, `wait_for_selector`. Deterministic, supports headless + screenshots |
| HTTP requests (API) | **Agent's built-in terminal** (`curl`/`fetch`) or Playwright's API context | No additional MCP needed — agent can use `run_command` with curl, or the skill prompt instructs to use fetch-style tool calls |

### Approach: Skill-as-Prompt (no runtime code)

Following the existing pattern in this repo, each skill is a **self-contained markdown prompt** (SKILL.md) that instructs the AI agent on the full workflow. No compiled code — the agent uses MCP tools and terminal commands directly.

> [!IMPORTANT]
> These skills assume the user's IDE (Cursor/Claude Code) already has the **gdrive**, **gsheets**, and **Playwright MCP** servers configured. The SKILL.md will document prerequisites and verification steps.

## Spreadsheet Schema

Both skills share a common schema convention. The user creates a Google Sheet with **two possible tab layouts**:

### API Tests Tab

| Column | Description | Written by |
|---|---|---|
| A: Test ID | Unique identifier (e.g., `API-001`) | User |
| B: Title | Short description | User |
| C: HTTP Method | GET/POST/PUT/DELETE/PATCH | User |
| D: URL | Full endpoint URL | User |
| E: Headers | JSON object (e.g., `{"Authorization": "Bearer xxx"}`) | User |
| F: Request Body | JSON payload or empty | User |
| G: Expected Status | HTTP status code (e.g., `200`, `401`) | User |
| H: Expected Response | JSONPath assertions (e.g., `$.data.id EXISTS`, `$.status EQUALS "ACTIVE"`) | User |
| I: Result | PASS / FAIL / ERROR | **Agent** |
| J: Error Message | Failure details | **Agent** |
| K: Response Body | Actual response summary | **Agent** |
| L: Executed At | Timestamp | **Agent** |

### Frontend Tests Tab

| Column | Description | Written by |
|---|---|---|
| A: Test ID | Unique identifier (e.g., `FE-001`) | User |
| B: Title | Short description | User |
| C: Start URL | Page to navigate to | User |
| D: Steps | JSON array of step objects (see below) | User |
| E: Assertions | JSON array of assertion objects (see below) | User |
| F: Result | PASS / FAIL / ERROR | **Agent** |
| G: Error Message | Failure details | **Agent** |
| H: Screenshot URL | Google Drive link to screenshot | **Agent** |
| I: Executed At | Timestamp | **Agent** |

**Steps JSON format (Frontend):**
```json
[
  {"action": "goto", "url": "https://example.com/login"},
  {"action": "fill", "selector": "#email", "value": "user@test.com"},
  {"action": "click", "selector": "button[type=submit]"},
  {"action": "wait", "selector": ".dashboard", "timeout": 5000}
]
```

**Assertions JSON format (Frontend):**
```json
[
  {"type": "visible", "selector": ".dashboard"},
  {"type": "text_contains", "selector": "h1", "value": "Welcome"},
  {"type": "url_contains", "value": "/dashboard"}
]
```

---

## Proposed Changes

### execute-test-case-api

#### [NEW] [SKILL.md](file:///d:/Code/agent-skills/execute-test-case-api/SKILL.md)

Main workflow prompt with frontmatter. Key sections:
- **When to Apply**: user says "execute/run api test", "chạy test case api", provides a Sheets URL
- **Prerequisites**: gdrive MCP, gsheets MCP configured; curl or HTTP tool available
- **Workflow**:
  1. Parse spreadsheet URL → extract `spreadsheetId`
  2. Read test cases from "API Tests" tab using gsheets MCP
  3. For each row: build HTTP request → execute via `curl` command → capture response
  4. Compare response status & body vs expected → determine PASS/FAIL
  5. Write back results (Result, Error Message, Response Body, Executed At) to the sheet
  6. Print summary: total/pass/fail/error counts
- **Error handling**: timeout policy, retry-once for transient errors, skip to next on assertion failures
- **Guardrails**: never modify user-defined columns, only write to result columns

#### [NEW] [AGENTS.md](file:///d:/Code/agent-skills/execute-test-case-api/AGENTS.md)

Default rules: timeout settings, retry policy, result column mapping, validation logic.

#### [NEW] [references/test-case-schema.md](file:///d:/Code/agent-skills/execute-test-case-api/references/test-case-schema.md)

Spreadsheet schema reference (API columns), JSONPath assertion syntax, example rows.

#### [NEW] [references/execution-rules.md](file:///d:/Code/agent-skills/execute-test-case-api/references/execution-rules.md)

HTTP execution rules, response validation patterns, PASS/FAIL determination logic.

---

### execute-test-case-frontend

#### [NEW] [SKILL.md](file:///d:/Code/agent-skills/execute-test-case-frontend/SKILL.md)

Main workflow prompt. Key sections:
- **When to Apply**: user says "execute/run frontend test", "chạy test case frontend/FE", provides a Sheets URL
- **Prerequisites**: gdrive MCP, gsheets MCP, **Playwright MCP** configured
- **Workflow**:
  1. Parse spreadsheet URL → extract `spreadsheetId`
  2. Read test cases from "Frontend Tests" tab using gsheets MCP
  3. For each row:
     a. Open new browser context via Playwright MCP
     b. Execute step sequence: goto → fill → click → wait
     c. Run assertions: check visibility, text content, URL
     d. Capture full-page screenshot
     e. Upload screenshot to Google Drive, get shareable link
     f. Determine PASS/FAIL based on assertion results
  4. Write back results (Result, Error Message, Screenshot URL, Executed At) to the sheet
  5. Print summary
- **Error handling**: per-step timeout, browser crash recovery (close + reopen context), fail-fast on assertion mismatch
- **Browser management**: one context per test case, always close after test, headless by default

#### [NEW] [AGENTS.md](file:///d:/Code/agent-skills/execute-test-case-frontend/AGENTS.md)

Default rules: browser config, screenshot settings, timeout defaults, retry policy.

#### [NEW] [references/test-case-schema.md](file:///d:/Code/agent-skills/execute-test-case-frontend/references/test-case-schema.md)

Spreadsheet schema reference (Frontend columns), Steps JSON syntax, Assertions JSON syntax.

#### [NEW] [references/browser-control.md](file:///d:/Code/agent-skills/execute-test-case-frontend/references/browser-control.md)

Playwright MCP tool reference, supported actions, screenshot capture patterns, error recovery.

---

### Package updates

#### [MODIFY] [package.json](file:///d:/Code/agent-skills/package.json)

Add new skill directories to the `files` array:
```diff
 "files": [
   "bin/",
   "src/",
   "templates/",
   "test-design-generator-api/",
   "test-design-generator-frontend/",
   "test-case-generator-api/",
   "test-case-generator-frontend/",
-  "postman-collection-generator/"
+  "postman-collection-generator/",
+  "execute-test-case-api/",
+  "execute-test-case-frontend/"
 ],
```

---

## Verification Plan

### Automated Checks
1. **Frontmatter validation**: Verify SKILL.md files have valid YAML frontmatter with `name` and `description` fields
   ```bash
   # Check frontmatter exists in both new SKILL.md files
   head -5 execute-test-case-api/SKILL.md
   head -5 execute-test-case-frontend/SKILL.md
   ```

2. **File structure consistency**: Verify both skills follow the same directory layout as existing skills
   ```bash
   # List both new skill directories
   ls -R execute-test-case-api/
   ls -R execute-test-case-frontend/
   ```

3. **Package.json validity**: Ensure package.json is valid JSON after modification
   ```bash
   node -e "require('./package.json')"
   ```

### Manual Verification
- **User review**: The SKILL.md content should be reviewed by the user to confirm:
  - The spreadsheet schema matches their team's conventions
  - MCP tool names match their actual MCP configuration
  - The workflow steps are clear and complete
  - Error handling policies are acceptable
