---
name: generate-test-design-api
description: Generate API test design mindmap from RSD/PTTK. For API endpoints only. Use when user says "sinh test design api", "tao mindmap api", "tạo test design api", or provides RSD/PTTK for an API endpoint.
---

# Test Design Generator — API Mode (Orchestrator)

<role_definition>
    <task_type>orchestrator</task_type>
    <identity>You coordinate specialized sub-agents to generate API test design documents (.md) from RSD/PTTK. You orchestrate the workflow but do NOT read RSD/PTTK directly.</identity>

    <boundary>
        <permitted>
            <action>List catalog files via search.py scripts</action>
            <action>Read catalog files (limited) for wording reference</action>
            <action>Spawn sub-agents with context blocks</action>
            <action>Check file existence (sentinel files, batch files)</action>
            <action>Merge validate batch files</action>
        </permitted>

        <forbidden>
            <action>Read RSD or PTTK files directly</action>
            <action>Read inventory.json directly (sub-agents handle this)</action>
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
    <hard_stop id="orchestrator_reads_rsd">
        <condition>If orchestrator reads RSD or PTTK directly</condition>
        <consequence>VIOLATION: architecture breach — td-extract sub-agent has sole responsibility for reading RSD/PTTK</consequence>
        <recovery>Pass file paths to td-extract sub-agent only.</recovery>
    </hard_stop>

    <hard_stop id="missing_inputs">
        <condition>Required inputs missing (RSD file path, output folder)</condition>
        <consequence>STOP — ask user for required inputs</consequence>
    </hard_stop>

    <hard_stop id="catalog_missing">
        <condition>catalog/ directory not found at project root</condition>
        <consequence>STOP — prompt user to run test-genie init</consequence>
    </hard_stop>
</guardrails>

---

## Workflow

<step id="0" name="Validate Project Setup & Load Project Rules">
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
            <fallback>Use skill-level defaults + notify user</fallback>
        </action>
    </actions>
</step>

<step id="0b" name="Validate Required Inputs">
    <trigger>Always — before any other step</trigger>

    <required_inputs>
        <input name="RSD File" var="RSD_FILE" source="user" required="true">
            <description>Path to RSD file (PDF or document)</description>
        </input>
        <input name="PTTK File" var="PTTK_FILE" source="user" required="false">
            <description>Path to PTTK file (optional)</description>
        </input>
        <input name="Output Folder" var="OUTPUT_DIR" source="user" required="true">
            <description>Output directory</description>
            <example>feature-1/</example>
        </input>
    </required_inputs>

    <derived_vars>
        <var name="INVENTORY_FILE">{OUTPUT_DIR}/inventory.json</var>
        <var name="OUTPUT_FILE">{OUTPUT_DIR}/test-design-api.md</var>
    </derived_vars>

    <guardrails>
        <rule type="hard_stop">
            <condition>RSD file path missing</condition>
            <action>NEVER scan folders or guess paths</action>
        </rule>
    </guardrails>
</step>

<step id="1" name="Mode Detection">
    <description>Detect if this is API or Frontend</description>
    <rules>
        <rule condition="title matches (GET|POST|PUT|DELETE|PATCH)\s+/">
            <result>High confidence API → proceed</result>
        </rule>
        <rule condition="contains màn hình, screen, giao diện">
            <result>suggest generate-test-design-frontend</result>
        </rule>
        <rule condition="unclear">
            <result>ask user</result>
        </rule>
    </rules>
</step>

<step id="2" name="Resolve SKILL_SCRIPTS and SKILL_AGENTS paths">
    <actions>
        <action type="bash">
            <script>python3 -c "
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
" "$(pwd)/generate-test-design-api/scripts/search.py" 2>/dev/null || echo "generate-test-design-api/scripts"</script>
            <stores>SKILL_SCRIPTS</stores>
        </action>
        <action type="bash">
            <script>python3 -c "
import os, sys
skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '$(pwd)')))
for root, dirs, files in os.walk(skill_dir, topdown=True):
    depth = root.count(os.sep) - skill_dir.count(os.sep)
    if depth > 3:
        dirs[:] = []
        continue
    if 'td-extract.md' in files and 'agents' in root:
        print(root)
        break
" "$(pwd)/generate-test-design-api/agents/td-extract.md" 2>/dev/null || echo "generate-test-design-api/agents"</script>
            <stores>SKILL_AGENTS</stores>
        </action>
    </actions>

    <fallback_paths>
        <path>.claude/skills/generate-test-design-api</path>
        <path>.cursor/skills/generate-test-design-api</path>
        <path>node_modules/generate-test-design-api</path>
    </fallback_paths>

    <actions>
        <action type="bash">
            <script>python3 $SKILL_SCRIPTS/search.py --ref priority-rules</script>
        </action>
    </actions>
</step>

<step id="3" name="Catalog Example">
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
            <action>Select 3 most relevant files (by name, title, same business group, same HTTP method)</action>
            <action>Read complete content of all 3 files</action>
        </rule>
        <rule condition="no_relevant_files">
            <action>Read first file in the list</action>
        </rule>
    </catalog_reading_rules>

    <output>
        <var name="CATALOG_SAMPLE">Concatenated catalog file contents for sub-agent reference</var>
    </output>

    <note>Catalog = highest priority source for wording. Always use CATALOG_SAMPLE for sub-agents.</note>
</step>

<step id="4" name="Spawn td-extract" type="sub-agent">
    <description>Extract business logic from RSD/PTTK and build inventory.json</description>
    <trigger>After Step 3</trigger>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/td-extract.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>td-extract</agent_type>
            <prompt>{td-extract.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="RSD_FILE">{RSD_FILE}</param>
                <param name="PTTK_FILE">{PTTK_FILE or "none"}</param>
                <param name="API_NAME">{from RSD title}</param>
                <param name="METHOD">{HTTP method}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <condition>inventory.json created and summary non-empty</condition>
    </completion_criteria>

    <error_handling>
        <condition>errorCodes = 0</condition>
        <action>Ask user before continuing</action>
        <condition>Conflicts between PTTK and RSD detected</condition>
        <action>Ask user to confirm</action>
    </error_handling>
</step>

<step id="4b" name="Clarify modes with user (if conflict detected)" type="user_interaction">
    <trigger>After Step 4 — ONLY if conflict between user intent and inventory.modes[]</trigger>

    <conflict_detection>
        <description>Compare user's original request with inventory.modes[]</description>
        <signals_single_api>
            <signal>User used "chỉ" (e.g. "chỉ generate", "chỉ test")</signal>
            <signal>User named exactly 1 API or 1 action (e.g. "api chỉnh sửa", "api tạo mới")</signal>
            <signal>User did NOT mention multiple flows/modes explicitly</signal>
        </signals_single_api>
        <conflict>inventory.modes[].length >= 2 AND any signal_single_api present → CONFLICT</conflict>
        <no_conflict>User explicitly listed multiple modes, or said "tất cả modes" → skip this step</no_conflict>
    </conflict_detection>

    <action type="ask_user">
        <message>
Bạn nói "{user's original phrasing}" nhưng inventory có {N} mode:
{list modes[].name + description}

Bạn muốn sinh test design cho:
A. Tất cả modes
B. Chỉ một mode cụ thể: [user chọn]
C. Không chia theo mode — chỉ test API đơn thuần

(Nếu không chắc, chọn C)
        </message>
    </action>

    <on_response>
        <case value="A">
            <action>Pass all modes to td-mainflow as-is</action>
        </case>
        <case value="B">
            <action>Filter inventory.modes[] to only selected mode before spawning td-mainflow</action>
        </case>
        <case value="C">
            <action>Set modes = [] in context passed to td-mainflow — treat as single-flow API</action>
        </case>
    </on_response>
</step>

<step id="5a" name="Spawn td-common" type="sub-agent">
    <description>Generate "Kiểm tra token" and "Kiểm tra Endpoint & Method" sections</description>
    <trigger>After Step 4</trigger>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/td-common.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>td-common</agent_type>
            <prompt>{td-common.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="OUTPUT_FILE">{OUTPUT_FILE}</param>
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE or "none"}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <file_exists>{OUTPUT_FILE}</file_exists>
        <content_check>Contains "## Kiểm tra token"</content_check>
    </completion_criteria>
</step>

<step id="5b" name="Spawn ALL td-validate agents" type="parallel">
    <description>Generate validate cases per field batch (parallel)</description>
    <trigger>After Step 5a</trigger>

    <spawn_mode>ALL batches simultaneously</spawn_mode>

    <preparation>
        <action type="read">
            <file>{INVENTORY_FILE}</file>
            <purpose>Extract fieldConstraints for batching</purpose>
        </action>
        <batch_strategy>
            <batch_size>3 fields per batch</batch_size>
            <example>Batch 1: [F1–F3]; Batch 2: [F4–F6]</example>
        </batch_strategy>
    </preparation>

    <per_batch_actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/td-validate.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>td-validate</agent_type>
            <prompt>{td-validate.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="OUTPUT_DIR">{OUTPUT_DIR}</param>
                <param name="BATCH_NUMBER">{N}</param>
                <param name="FIELD_BATCH">[{fieldName}:{type}:{required}:{maxLength}, ...]</param>
                <param name="FIELD_TYPES_NEEDED">"{comma-separated types for --section}"</param>
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE or "none"}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </per_batch_actions>

    <file_naming>
        <file pattern="{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.md" />
    </file_naming>

    <merge>
        <script>python3 $SKILL_SCRIPTS/merge_validate.py --output-dir {OUTPUT_DIR} --output-file {OUTPUT_FILE}</script>
        <on_exit_1>
            <action>Read error message</action>
            <action>Re-spawn failed batch with note</action>
        </on_exit_1>
    </merge>

    <post_merge_field_coverage_check>
        <description>Verify ALL fields from bodyParams are present in output — catch silent sub-agent failures</description>
        <script>python3 -c "
import json, sys
inv = json.load(open('{INVENTORY_FILE}', encoding='utf-8'))
fields = [f['name'] for f in inv.get('requestSchema', {}).get('bodyParams', [])]
content = open('{OUTPUT_FILE}', encoding='utf-8').read()
missing = [f for f in fields if ('### Trường ' + f) not in content]
if missing:
    print('MISSING_FIELDS: ' + ', '.join(missing))
    sys.exit(1)
print('FIELD_COVERAGE OK: ' + str(len(fields)) + '/' + str(len(fields)))
"</script>
        <on_missing_fields>
            <action>Identify which batch numbers cover the missing fields</action>
            <action>Re-spawn ONLY the failed batches with same context</action>
            <action>Re-run merge after re-spawn completes</action>
        </on_missing_fields>
    </post_merge_field_coverage_check>

    <completion_criteria>
        <file_exists>{OUTPUT_DIR}/.td-validate-done</file_exists>
        <content_check>{OUTPUT_FILE} contains "## Kiểm tra Validate"</content_check>
    </completion_criteria>

    <barrier id="validate_barrier">
        <description>SEQUENTIAL BARRIER — MUST check before proceeding to Step 5c</description>
        <script>python3 -c "
import sys, os
sentinel = '{OUTPUT_DIR}/.td-validate-done'
output = '{OUTPUT_FILE}'
if not os.path.exists(sentinel):
    print('NOT READY: .td-validate-done missing')
    sys.exit(1)
content = open(output, encoding='utf-8').read()
if '## Kiểm tra Validate' not in content:
    print('NOT READY: ## Kiểm tra Validate missing from output')
    sys.exit(1)
print('READY')
"</script>

        <on_not_ready>
            <action>STOP COMPLETELY. Do NOT spawn Step 5c.</action>
            <action>Debug Step 5b first.</action>
        </on_not_ready>
    </barrier>
</step>

<step id="5c" name="Spawn td-mainflow" type="sub-agent">
    <description>Generate "Kiểm tra chức năng" and "Kiểm tra ngoại lệ" sections</description>
    <trigger>After validate barrier passes</trigger>

    <barrier>
        <description>Barrier check before spawning</description>
        <script>python3 -c "
import sys
c = open('{OUTPUT_FILE}', encoding='utf-8').read()
checks = ['## Kiểm tra token', '## Kiểm tra Validate', '## Kiểm tra chức năng']
missing = [s for s in checks if s not in c]
print('READY' if not missing else 'NOT READY: MISSING: ' + str(missing))
sys.exit(0 if not missing else 1)
"</script>

        <on_not_ready>
            <action>STOP COMPLETELY. Do NOT spawn Step 6.</action>
        </on_not_ready>
    </barrier>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/td-mainflow.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>td-mainflow</agent_type>
            <prompt>{td-mainflow.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="OUTPUT_FILE">{OUTPUT_FILE}</param>
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE or "none"}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <content_check>{OUTPUT_FILE} contains "## Kiểm tra chức năng"</content_check>
    </completion_criteria>
</step>

<step id="6" name="Spawn td-verify" type="sub-agent">
    <description>Gap analysis, V5 duplicate check, V9 global scan, V10 format check</description>
    <note>V1-V4 handled by td-validate. V6-V9 handled by td-mainflow. td-verify only covers: gap analysis, V5 duplicate, V9 global, V10 format.</note>
    <trigger>After Step 5c</trigger>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/td-verify.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>td-verify</agent_type>
            <prompt>{td-verify.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="OUTPUT_FILE">{OUTPUT_FILE}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <result>Self-check prints 4/4 ✅ or all gaps/violations fixed</result>
    </completion_criteria>
</step>

<step id="7" name="Final Output">
    <description>Report completion to user</description>
    <trigger>After Step 6</trigger>

    <output_message>
```
✅ Test design hoàn thành: {OUTPUT_FILE}
📋 Inventory: {INVENTORY_FILE}
```
    </output_message>

    <notification>
        <condition>If ### [SỬA] exists in output</condition>
        <message>Auto-added/fixed items count</message>
    </notification>
</step>

<step id="8" name="Cleanup — Delete intermediate files">
    <description>Remove temporary batch files, keep only final outputs</description>
    <trigger>After Step 7</trigger>

    <keep_files>
        <file>inventory.json</file>
        <file>patch.json</file>
        <file>test-design-api.md</file>
    </keep_files>

    <delete_patterns>
        <pattern>validate-batch-*.md</pattern>
        <pattern>.td-validate-done</pattern>
    </delete_patterns>
</step>

---

## Project Structure

```
generate-test-design-api/
├── SKILL.md                      ← Orchestrator workflow (this file)
├── AGENTS.md                     ← Skill-level default rules
├── agents/
│   ├── td-extract.md             ← Extract RSD/PTTK → inventory.json
│   ├── td-common.md              ← Generate common sections (token, endpoint)
│   ├── td-validate.md            ← Generate validate per field batch
│   ├── td-mainflow.md            ← Generate main flow + exceptions
│   └── td-verify.md             ← Gap analysis, dedup, format check
├── references/
│   ├── api-test-design.md
│   ├── priority-rules.md
│   └── quality-rules.md
└── scripts/
    ├── search.py
    ├── inventory.py
    ├── merge_validate.py
    └── ...
```
