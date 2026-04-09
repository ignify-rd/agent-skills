---
name: generate-test-case-api
description: Generate API test cases from RSD/PTTK (or mindmap) and output to test-cases.json. For API endpoints only. Use when user says "sinh test case api", "sinh test cases api", "generate api test case", "tạo test case api", or provides RSD/PTTK/.pdf documents or a mindmap file for an API endpoint.
---

# Test Case Generator — API Mode (Orchestrator)

<role_definition>
    <task_type>orchestrator</task_type>
    <identity>You coordinate specialized sub-agents to generate API test cases. You orchestrate the workflow but do NOT read test-design or inventory files directly.</identity>

    <boundary>
        <permitted>
            <action>Query inventory via inventory.py scripts</action>
            <action>List catalog files via search.py scripts</action>
            <action>Read catalog files (limited) for wording reference</action>
            <action>Spawn sub-agents with context blocks</action>
            <action>Check file existence (sentinel files, batch files)</action>
        </permitted>

        <forbidden>
            <action>Read test-design-api.md directly</action>
            <action>Read inventory.json directly</action>
        </forbidden>
    </boundary>

    <priority_rules>
        <rule id="override_priority" type="hierarchy">
            <level id="1" name="chat_input" priority="highest">User chat input / user request</level>
            <level id="2" name="project_rules" priority="medium">Project AGENTS.md — overrides skill defaults when explicitly defined</level>
            <level id="3" name="skill_defaults" priority="lowest">Skill-level defaults — used when project rules undefined</level>
        </rule>
    </priority_rules>
</role_definition>

<guardrails>
    <hard_stop id="orchestrator_reads_design">
        <condition>If orchestrator reads test-design-api.md or inventory.json directly</condition>
        <consequence>VIOLATION: architecture breach, causes context pollution, distorts output</consequence>
        <recovery>Use inventory.py script queries instead. Only sub-agents (tc-*) may read those files.</recovery>
    </hard_stop>

    <hard_stop id="missing_inputs">
        <condition>Required inputs missing (test design path, inventory path, output folder)</condition>
        <consequence>STOP — ask user to run generate-test-design-api first</consequence>
        <recovery>"Skill này yêu cầu file test design và inventory.json. Vui lòng chạy skill generate-test-design-api trước."</recovery>
    </hard_stop>

    <hard_stop id="catalog_missing">
        <condition>catalog/ directory not found at project root</condition>
        <consequence>STOP — prompt user to run test-genie init</consequence>
    </hard_stop>

    <soft_warning id="no_agents_md">
        <condition>Project AGENTS.md not found</condition>
        <consequence>Use skill defaults + notify user</consequence>
        <message>Project chưa có AGENTS.md. Đang dùng rules mặc định.</message>
    </soft_warning>

    <hard_stop id="no_temp_files">
        <condition>Any agent is about to write a helper/temp script file (e.g. _*.py, _*.ps1, _check_*.py, _append_*.ps1, etc.)</condition>
        <consequence>VIOLATION — do NOT create temp script files on disk under any circumstances</consequence>
        <recovery>Use python3 -X utf8 -c "..." inline in Bash, or use the Read/Edit/Write tools directly. Never write a helper script to disk.</recovery>
    </hard_stop>
</guardrails>

---

## Workflow

<step id="0" name="Load Project Rules">
    <trigger>Always — first step</trigger>
    <actions>
        <action type="check">
            <target>catalog/ directory</target>
            <at>project root</at>
            <if_missing>Ask user to run test-genie init</if_missing>
        </action>
        <action type="read">
            <target>AGENTS.md</target>
            <at>project root</at>
            <store_as>projectRules</store_as>
            <fallback>Use skill-level defaults</fallback>
        </action>
    </actions>

    <output>
        <var name="projectRules">Full AGENTS.md content or "none"</var>
    </output>
</step>

<step id="0b" name="Validate Required Inputs">
    <trigger>Always — before any other step</trigger>

    <required_inputs>
        <input name="Test Design File" var="TEST_DESIGN_FILE" source="user" required="true">
            <description>Path to test-design-api.md</description>
            <example>feature-1/test-design-api.md</example>
        </input>
        <input name="Inventory File" var="INVENTORY_FILE" source="user" required="true">
            <description>Path to inventory.json</description>
            <example>feature-1/inventory.json</example>
        </input>
        <input name="Output Folder" var="OUTPUT_DIR" source="user" required="true">
            <description>Output directory for generated files</description>
            <example>feature-1/</example>
        </input>
    </required_inputs>

    <derived_vars>
        <var name="OUTPUT_FILE">{OUTPUT_DIR}/test-cases.json</var>
    </derived_vars>

    <guardrails>
        <rule type="hard_stop">
            <condition>Any required input missing</condition>
            <action>NEVER scan folders or guess paths</action>
        </rule>
    </guardrails>
</step>

<step id="1" name="Resolve SKILL_SCRIPTS and SKILL_AGENTS paths">
    <actions>
        <action type="bash">
            <script>python3 -X utf8 -c "
import os, sys
skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '$(pwd)')))
for root, dirs, files in os.walk(skill_dir, topdown=True):
    depth = root.count(os.sep) - skill_dir.count(os.sep)
    if depth > 3:
        dirs[:] = []
        continue
    if 'search.py' in files and 'scripts' in root:
        print(os.path.dirname(root))
        break
" "$(pwd)/generate-test-case-api/scripts/search.py" 2>/dev/null || echo "generate-test-case-api/scripts"</script>
            <stores>SKILL_SCRIPTS</stores>
        </action>
        <action type="bash">
            <script>python3 -X utf8 -c "
import os, sys
skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '$(pwd)')))
for root, dirs, files in os.walk(skill_dir, topdown=True):
    depth = root.count(os.sep) - skill_dir.count(os.sep)
    if depth > 3:
        dirs[:] = []
        continue
    if 'tc-context.md' in files and 'agents' in root:
        print(root)
        break
" "$(pwd)/generate-test-case-api/agents/tc-context.md" 2>/dev/null || echo "generate-test-case-api/agents"</script>
            <stores>SKILL_AGENTS</stores>
        </action>
    </actions>

    <fallback_paths>
        <path>.claude/skills/generate-test-case-api</path>
        <path>.cursor/skills/generate-test-case-api</path>
        <path>node_modules/generate-test-case-api</path>
    </fallback_paths>

    <output>
        <var name="SKILL_SCRIPTS">Path to skill scripts directory</var>
        <var name="SKILL_AGENTS">Path to agents directory</var>
    </output>
</step>

<step id="2" name="Catalog Listing (CATALOG_SAMPLE)">
    <actions>
        <action type="bash">
            <script>python3 $SKILL_SCRIPTS/search.py --list --domain api</script>
            <stores>catalogList</stores>
        </action>
    </actions>

    <catalog_reading_rules>
        <rule condition="catalog_count <= 3">
            <action>Read ALL catalog files completely (no line limit)</action>
        </rule>
        <rule condition="catalog_count > 3">
            <action>Select 3 most relevant files (by name, title, same business group, same HTTP method, similar structure)</action>
            <action>Read complete content of all 3 files</action>
        </rule>
        <rule condition="no_relevant_files">
            <action>Read first file in the list</action>
        </rule>
    </catalog_reading_rules>

    <output>
        <var name="CATALOG_SAMPLE">Concatenated catalog file contents for sub-agent reference</var>
    </output>

    <note>Catalog = highest priority source for wording. Always use CATALOG_SAMPLE for sub-agents. Do NOT use default templates as wording source.</note>
</step>

<step id="3" name="Spawn tc-context" type="sequential">
    <description>Load catalog style and build preConditions base</description>
    <trigger>After Step 2</trigger>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/tc-context.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>tc-context</agent_type>
            <prompt>{tc-context.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="OUTPUT_DIR">{OUTPUT_DIR}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <file_exists>{OUTPUT_DIR}/tc-context.json</file_exists>
    </completion_criteria>
</step>

<step id="4" name="Spawn tc-common" type="sequential">
    <description>Generate BATCH 1 — common and permission test cases</description>
    <trigger>After Step 3</trigger>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/tc-common.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>tc-common</agent_type>
            <prompt>{tc-common.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="TC_CONTEXT_FILE">{OUTPUT_DIR}/tc-context.json</param>
                <param name="TEST_DESIGN_FILE">{TEST_DESIGN_FILE}</param>
                <param name="OUTPUT_DIR">{OUTPUT_DIR}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <file_exists>{OUTPUT_DIR}/batch-1.json</file_exists>
    </completion_criteria>
</step>

<step id="5a" name="Query inventory — batch fields for tc-validate">
    <description>Get ALL fields (request + fileContent) and group into batches</description>
    <trigger>After Step 4</trigger>

    <actions>
        <action type="bash">
            <script>python3 -X utf8 $SKILL_SCRIPTS/inventory.py allFields --file {INVENTORY_FILE}</script>
            <stores>allFields</stores>
        </action>
    </actions>

    <field_source_handling>
        <rule>allFields returns unified list with "source" field: "request" or "fileContent"</rule>
        <rule>Request fields (source=request): use validate-batch-{N}.json naming</rule>
        <rule>FileContent fields (source=fileContent): use validate-batch-fc-{N}.json naming</rule>
        <rule>If allFields returns 0 items: skip Step 5b entirely, proceed to Step 5c</rule>
    </field_source_handling>

    <batch_strategy>
        <note>Step 5b now uses scripts (not agents) — batching is handled automatically by parse_test_design.py.
        allFields query below is kept for reference only; Step 5b does not require manual batching.</note>
    </batch_strategy>
</step>

<step id="5b" name="Generate BATCH 2 — validate cases via scripts (no agent)" type="script">
    <description>
        Run 2 scripts to produce validate-batch.json.
        NO sub-agents needed. Scripts replace tc-validate entirely.

        Script 1 — parse_test_design.py:
          Primary source = test-design-api.md (QA-editable, authoritative).
          Supplement     = inventory.json crossFieldRules + conditionalRequired
                           (adds cases NOT already in test-design).
          patch.json     = optional overrides for field metadata.

        Script 2 — expand_validate.py:
          Expands lightweight cases → template-format batch (for merge_batches.py).
    </description>
    <trigger>After Step 5a</trigger>

    <actions>
        <action type="bash" id="5b-1" name="Parse test-design → validate-cases.json">
            <script>python3 -X utf8 {SKILL_SCRIPTS}/parse_test_design.py \
  --test-design "{TEST_DESIGN_FILE}" \
  --inventory   "{INVENTORY_FILE}" \
  --patch       "{OUTPUT_DIR}/../patch.json" \
  --output      "{OUTPUT_DIR}/validate-cases.json"</script>
            <note>
                --patch is optional. Script prints a gap report to stdout.
                If patch.json is not at ../patch.json, omit --patch flag.
                Check for patch.json existence first:
                  python3 -X utf8 -c "import os,sys; sys.exit(0 if os.path.exists(r'{OUTPUT_DIR}/../patch.json') else 1)"
            </note>
        </action>

        <action type="bash" id="5b-2" name="Expand cases → validate-batch.json">
            <script>python3 -X utf8 {SKILL_SCRIPTS}/expand_validate.py \
  --cases    "{OUTPUT_DIR}/validate-cases.json" \
  --context  "{OUTPUT_DIR}/tc-context.json" \
  --inventory "{INVENTORY_FILE}" \
  --output   "{OUTPUT_DIR}/validate-batch.json"</script>
        </action>
    </actions>

    <file_naming>
        <file pattern="{OUTPUT_DIR}/validate-cases.json"  description="Intermediate — parse_test_design.py output" />
        <file pattern="{OUTPUT_DIR}/validate-batch.json"  description="Final — merge_batches.py input" />
    </file_naming>

    <completion_check>
        <action type="bash">
            <script>python3 -X utf8 -c "
import sys, os
f = r'{OUTPUT_DIR}/validate-batch.json'
if not os.path.exists(f):
    print('ERROR: validate-batch.json not found')
    sys.exit(1)
size = os.path.getsize(f)
if size < 10:
    print(f'ERROR: validate-batch.json too small ({size} bytes)')
    sys.exit(1)
print(f'OK: validate-batch.json ({size} bytes)')
"</script>
        </action>
        <on_success>
            <create_sentinel>
                <file>{OUTPUT_DIR}/.tc-validate-done</file>
                <content>done</content>
            </create_sentinel>
        </on_success>
        <on_fail>
            <action>Check script output above for parse/expand errors. Fix and re-run.</action>
        </on_fail>
    </completion_check>

    <barrier id="validate_barrier">
        <description>MUST check before proceeding to Step 5c</description>
        <script>python3 -X utf8 -c "
import sys, os
sentinel = '{OUTPUT_DIR}/.tc-validate-done'
if not os.path.exists(sentinel):
    print('NOT READY: .tc-validate-done missing')
    sys.exit(1)
print('READY')
"</script>

        <on_not_ready>
            <action>STOP COMPLETELY. Do NOT spawn Step 5c. Debug Step 5b first.</action>
        </on_not_ready>

        <note>Do NOT skip this barrier check under any circumstances.</note>
    </barrier>
</step>

<step id="5c" name="Spawn tc-mainflow" type="sequential">
    <description>Generate BATCH 3 — main flow test cases (functionality + exceptions)</description>
    <trigger>After validate barrier passes</trigger>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/tc-mainflow.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>tc-mainflow</agent_type>
            <prompt>{tc-mainflow.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="TC_CONTEXT_FILE">{OUTPUT_DIR}/tc-context.json</param>
                <param name="TEST_DESIGN_FILE">{TEST_DESIGN_FILE}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="OUTPUT_DIR">{OUTPUT_DIR}</param>
                <param name="OUTPUT_FILE">{OUTPUT_FILE}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <file_exists>{OUTPUT_DIR}/batch-3.json</file_exists>
    </completion_criteria>
</step>

<step id="6" name="Spawn tc-verify" type="sequential">
    <description>Gap analysis, dedup, and final output</description>
    <trigger>After Step 5c</trigger>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/tc-verify.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>tc-verify</agent_type>
            <prompt>{tc-verify.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="TC_CONTEXT_FILE">{OUTPUT_DIR}/tc-context.json</param>
                <param name="TEST_DESIGN_FILE">{TEST_DESIGN_FILE}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="OUTPUT_DIR">{OUTPUT_DIR}</param>
                <param name="OUTPUT_FILE">{OUTPUT_FILE}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <file_exists>{OUTPUT_FILE}</file_exists>
    </completion_criteria>
</step>

<step id="7" name="Upload to Google Sheets">
    <description>Auto-upload test-cases.json lên Google Sheets</description>
    <trigger>After Step 6</trigger>

    <actions>
        <action type="bash">
            <script>python3 -X utf8 {SKILL_SCRIPTS}/upload_gsheet.py {OUTPUT_DIR_NAME} --project-root {PROJECT_ROOT}</script>
            <note>
                {OUTPUT_DIR_NAME} = tên thư mục chứa test-cases.json (ví dụ: "feature-3").
                {PROJECT_ROOT} = thư mục gốc của project (chứa AGENTS.md, catalog/).
                Nếu upload thất bại (lỗi auth, network...) → in cảnh báo và TIẾP TỤC sang Step 8 (không dừng).
            </note>
        </action>
    </actions>

    <on_success>
        <output_message>
```
✅ Test cases hoàn thành: {OUTPUT_FILE}
📋 Inventory: {INVENTORY_FILE}
📝 Test design: {TEST_DESIGN_FILE}
🔗 Google Sheets: {SHEET_URL}
```
        </output_message>
    </on_success>

    <on_failure>
        <output_message>
```
✅ Test cases hoàn thành: {OUTPUT_FILE}
⚠️  Upload Google Sheets thất bại — hãy chạy thủ công:
    python3 {SKILL_SCRIPTS}/upload_gsheet.py {OUTPUT_DIR_NAME} --project-root {PROJECT_ROOT}
```
        </output_message>
    </on_failure>
</step>

<step id="8" name="Cleanup — Delete intermediate files">
    <description>Remove temporary batch files, keep only final outputs</description>
    <trigger>After Step 7</trigger>

    <keep_files>
        <file>inventory.json</file>
        <file>patch.json</file>
        <file>test-cases.json</file>
        <file>test-design-api.md</file>
    </keep_files>

    <delete_patterns>
        <pattern>tc-context.json</pattern>
        <pattern>batch-*.json</pattern>
        <pattern>validate-batch-*.json</pattern>
        <pattern>validate-batch-fc-*.json</pattern>
        <pattern>validate-cases-*.json</pattern>
        <pattern>validate-cases-fc-*.json</pattern>
        <pattern>test-cases-merged.json</pattern>
        <pattern>.tc-validate-done</pattern>
        <pattern>_*.py</pattern>
        <pattern>_*.ps1</pattern>
    </delete_patterns>
</step>

---

## Project AGENTS.md Override

| Category | Can Override? |
|----------|--------------|
| Chat input / user request | **Always — HIGHEST PRIORITY** |
| testAccount | Yes |
| testSuiteName convention | Yes |
| Writing style (ngắn/dài, cách viết step) | Yes |
| Output JSON field names | No |
| Batch strategy (BATCH 1/2/3 split) | No |
| Field type dispatch table | No |
| Importance mapping | No |

---

## Quick Reference — Batch File Naming

| Batch | File | Content |
|-------|------|---------|
| BATCH 1 | `batch-1.json` | Common + permission test cases |
| BATCH 2 | `validate-batch-N.json` | Validate cases per request field batch |
| BATCH 2 | `validate-batch-fc-N.json` | Validate cases per fileContent field batch |
| BATCH 3 | `batch-3.json` | Main flow cases |
| Merged | `test-cases-merged.json` | After merge_batches.py + normalize_suites.py |
| Final | `test-cases.json` | After gap fill + project rules |
