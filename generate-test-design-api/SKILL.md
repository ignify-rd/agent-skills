---
name: generate-test-design-api
description: Generate API test design mindmap from RSD/PTTK on Confluence. For API endpoints only. Use when user says "sinh test design api", "tao mindmap api", "tạo test design api", or provides Confluence links to RSD/PTTK for an API endpoint.
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
        <consequence>VIOLATION: architecture breach — td-extract sub-agent has sole responsibility for reading RSD/PTTK from Confluence</consequence>
        <recovery>Pass Confluence URLs to td-extract sub-agent only.</recovery>
    </hard_stop>

    <hard_stop id="missing_inputs">
        <condition>Required inputs missing (RSD file path, output folder)</condition>
        <consequence>STOP — ask user for required inputs</consequence>
    </hard_stop>

    <hard_stop id="catalog_missing">
        <condition>catalog/ directory not found at project root</condition>
        <consequence>STOP — prompt user to run test-genie init</consequence>
    </hard_stop>

    <hard_stop id="no_temp_files">
        <condition>Any agent is about to write a helper/temp script file (e.g. _*.py, _*.ps1, _check_*.py, _append_*.ps1, etc.)</condition>
        <consequence>VIOLATION — do NOT create temp script files on disk under any circumstances</consequence>
        <recovery>Use python3 -X utf8 -c "..." inline in Bash, or use the Read/Edit/Write tools directly. Never write a helper script to disk.</recovery>
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
        <input name="RSD Confluence URL" var="RSD_URL" source="user" required="true">
            <description>Confluence page URL of RSD document</description>
            <example>https://your-site.atlassian.net/wiki/spaces/SPACE/pages/123456/RSD-Ten-API</example>
        </input>
        <input name="PTTK Confluence URL" var="PTTK_URL" source="user" required="false">
            <description>Confluence page URL of PTTK document (optional)</description>
            <example>https://your-site.atlassian.net/wiki/spaces/SPACE/pages/789012/PTTK-Ten-API</example>
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
            <condition>RSD Confluence URL missing</condition>
            <action>NEVER guess URLs — ask user for the Confluence page link</action>
        </rule>
    </guardrails>
</step>

<step id="0c" name="Authenticate Atlassian MCP">
    <trigger>Always — before reading any Confluence page</trigger>
    <description>
        Ensure Atlassian MCP is authenticated. If not yet authenticated, call authenticate tool.
        Then resolve cloudId by calling getConfluenceSpaces().
        Extract pageId from Confluence URLs using pattern: /pages/&lt;pageId&gt;/
    </description>
    <actions>
        <action type="mcp">
            <tool>getConfluenceSpaces</tool>
            <purpose>Resolve cloudId for subsequent Confluence API calls</purpose>
        </action>
    </actions>
    <output>
        <var name="CLOUD_ID">Atlassian Cloud ID</var>
        <var name="RSD_PAGE_ID">Page ID extracted from RSD_URL</var>
        <var name="PTTK_PAGE_ID">Page ID extracted from PTTK_URL (or "none")</var>
    </output>
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
" "$(pwd)/generate-test-design-api/scripts/search.py" 2>/dev/null || echo "generate-test-design-api/scripts"</script>
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
    if 'td-extract-logic.md' in files and 'agents' in root:
        print(root)
        break
" "$(pwd)/generate-test-design-api/agents/td-extract-logic.md" 2>/dev/null || echo "generate-test-design-api/agents"</script>
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

<step id="4" name="Spawn td-extract-logic + td-extract-fields (PARALLEL)" type="parallel">
    <description>Extract business logic AND field definitions from RSD/PTTK in parallel. Both write to same inventory.json but to DIFFERENT categories.</description>
    <trigger>After Step 3 (Catalog)</trigger>

    <sub_step id="4a" name="Spawn td-extract-logic">
        <description>Extracts: errorCodes, businessRules, modes, dbOperations, externalServices, statusTransitions, and endpoint from RSD. Also runs inventory init.</description>
        <actions>
            <action type="read_agent_instructions">
                <file>SKILL_AGENTS/td-extract-logic.md</file>
            </action>
            <action type="spawn_subagent">
                <agent_type>td-extract-logic</agent_type>
                <prompt>{td-extract-logic.md content}</prompt>
                <context>
                    <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                    <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                    <param name="OUTPUT_DIR">{OUTPUT_DIR}</param>
                    <param name="CLOUD_ID">{CLOUD_ID}</param>
                    <param name="RSD_PAGE_ID">{RSD_PAGE_ID}</param>
                    <param name="PTTK_PAGE_ID">{PTTK_PAGE_ID or "none"}</param>
                    <param name="API_NAME">{from RSD title}</param>
                    <param name="METHOD">{HTTP method}</param>
                    <param name="PROJECT_RULES">{projectRules or "none"}</param>
                </context>
            </action>
        </actions>
    </sub_step>

    <sub_step id="4b" name="Spawn td-extract-fields">
        <description>Extracts: fieldConstraints (with rsdConstraints), requestSchema, responseSchema, testData.</description>
        <actions>
            <action type="read_agent_instructions">
                <file>SKILL_AGENTS/td-extract-fields.md</file>
            </action>
            <action type="spawn_subagent">
                <agent_type>td-extract-fields</agent_type>
                <prompt>{td-extract-fields.md content}</prompt>
                <context>
                    <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                    <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                    <param name="OUTPUT_DIR">{OUTPUT_DIR}</param>
                    <param name="CLOUD_ID">{CLOUD_ID}</param>
                    <param name="RSD_PAGE_ID">{RSD_PAGE_ID}</param>
                    <param name="PTTK_PAGE_ID">{PTTK_PAGE_ID or "none"}</param>
                    <param name="API_NAME">{from RSD title}</param>
                    <param name="METHOD">{HTTP method}</param>
                    <param name="PROJECT_RULES">{projectRules or "none"}</param>
                </context>
            </action>
        </actions>
    </sub_step>

    <execution_order>
        <rule>td-extract-logic MUST start first (runs inventory init)</rule>
        <rule>td-extract-fields starts immediately after (patches into existing inventory)</rule>
        <rule>Both can run in parallel — they write to different inventory categories</rule>
    </execution_order>

    <completion_criteria>
        <condition>Both agents complete successfully</condition>
        <condition>inventory.json has fieldConstraints with rsdConstraints + errorCodes + statusTransitions</condition>
    </completion_criteria>

    <post_completion>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py summary --file {INVENTORY_FILE}</script>
        </action>
    </post_completion>

    <error_handling>
        <condition>errorCodes = 0</condition>
        <action>Ask user before continuing</action>
        <condition>Any fieldConstraints missing rsdConstraints</condition>
        <action>Re-spawn td-extract-fields with note to fill missing rsdConstraints</action>
        <condition>Conflicts between PTTK and RSD detected</condition>
        <action>Ask user to confirm</action>
    </error_handling>
</step>

<step id="4c" name="Clarify modes with user (if conflict detected)" type="user_interaction">
    <trigger>After Step 4 completes (both extract agents done) — ONLY if conflict between user intent and inventory.modes[]</trigger>

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
    <trigger>After Step 4c</trigger>

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
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py get \
  --file {INVENTORY_FILE} \
  --category fieldConstraints \
  --keys name,type,required,maxLength</script>
            <purpose>Get field list for batching — only name/type/required/maxLength, NOT full rsdConstraints</purpose>
        </action>
        <batch_strategy>
            <batch_size>5 fields per batch</batch_size>
            <example>Batch 1: [F1–F5]; Batch 2: [F6–F10]</example>
            <note>Increased from 3 to 5 — reduces number of sub-agents and coordination overhead.</note>
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
                <param name="FIELD_TYPES_NEEDED">
                    Comma-separated section names from api-test-design.md for the field types in this batch.
                    Always include "validate-rules" first.
                    Use EXACTLY these section names (td-validate also self-computes, this is a backup hint):

                    | Type (case-insensitive)          | required=Y (no default) | required=N     |
                    |-----------------------------------|-------------------------|----------------|
                    | String / string / varchar         | String Required         | String Optional |
                    | Integer / Int / int / integer     | Integer Required        | Integer Optional |
                    | Long / long                       | Long                    | Long            |
                    | Number / Decimal / Float / float  | Number Required         | Number Optional |
                    | Date / date                       | Date Required           | Date Optional   |
                    | DateTime / datetime               | DateTime Required       | DateTime Optional |
                    | Boolean / boolean / bool          | Boolean Required        | Boolean Optional |
                    | JSONB / JSON / jsonb              | JSONB Required          | JSONB Optional  |
                    | Array / List / array              | Array Required          | Array Optional  |
                    | MultipartFile / file              | MultipartFile Required  | MultipartFile Optional |
                    | Integer/Long with defaultValue    | Integer Default         | Integer Optional |

                    Example: batch [slaName:String:Y:100, effectiveDate:Date:Y:null, expiredDate:Date:N:null]
                    → FIELD_TYPES_NEEDED = "validate-rules,String Required,Date Required,Date Optional"
                </param>
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE or "none"}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>

        <compact_prompt_rule>
            ⛔ CRITICAL: When constructing the sub-agent spawn prompt, pass ONLY:
            1. The td-validate.md agent instructions (full content)
            2. The context params listed above (paths + FIELD_BATCH as compact "fieldName:type:required:maxLength" format)
            
            DO NOT include in the prompt:
            - Full rsdConstraints details per field (the sub-agent queries inventory.py itself)
            - Pre-generated case descriptions or bullet lists
            - Full errorCode tables or response schemas
            - Any "here are the N cases to generate" listings
            
            The sub-agent has tools (Read, Bash, Edit, Write) to fetch its own data from inventory.
            Passing verbose data in the prompt wastes ~2-3K tokens per batch.
        </compact_prompt_rule>
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
        <script>python3 -X utf8 -c "
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

    <post_merge_dedup_check>
        <description>Scan output for BASE + BOUNDARY overlap violations (R7). RE-SPAWN if overlap found.</description>
        <script>python3 -X utf8 -c "
import re, sys
content = open('{OUTPUT_FILE}', encoding='utf-8').read()

# Detect overlap patterns after R7 MERGE enforcement
overlap_issues = []

# Pattern 1: Same value tested multiple times with same error code
# e.g., '= -1' and 'nhỏ hơn min = -1' both appear
neg_values = re.findall(r'= (-?\d+(?:\.\d+)?)', content)
from collections import Counter
neg_counts = Counter(neg_values)

# Check for Number/Integer boundary overlap: -1 + min-1 = duplicate
# Check for decimal overlap: 1.5 + 1.5 decimal = duplicate
# Pattern: specific values that should have been MERGED
values_to_check = ['-1', '-0.01', '1', '50', '99', '999', '-100', '1.5']
for v in values_to_check:
    pattern = r'= ' + re.escape(v) + r'(?!\d)'
    matches = re.findall(pattern, content)
    if len(matches) > 1:
        overlap_issues.append(f'OVERLAP: giá trị {v} xuất hiện {len(matches)} lần — có thể chưa MERGE')

# Pattern 2: Count bullets per field — if Number field has >15 cases, flag for review
field_sections = re.findall(r'### Trường (\w+)
(.*?)(?=### Trường|$)', content, re.DOTALL)
for field_name, section in field_sections:
    bullet_count = len(re.findall(r'^- ', section, re.MULTILINE))
    # Check if field is Number/Decimal type in inventory
    try:
        inv = json.load(open('{INVENTORY_FILE}', encoding='utf-8'))
        field_type = next((f.get('type','') for f in inv.get('requestSchema',{}).get('bodyParams',[]) if f.get('name') == field_name), '')
        constraints = next((f.get('rsdConstraints',{}) for f in inv.get('requestSchema',{}).get('bodyParams',[]) if f.get('name') == field_name), {})
        has_minmax = bool(constraints.get('min') is not None or constraints.get('max') is not None)
        has_decimal = constraints.get('maxDecimalPlaces') is not None
        if field_type in ('Number', 'decimal') and has_minmax and bullet_count > 15:
            overlap_issues.append(f'WARN: {field_name} có {bullet_count} cases (>15) — có thể chưa MERGE (Number + min/max + decimal)')
    except:
        pass

if overlap_issues:
    print('R7_DEDUP_FAIL: ' + '; '.join(overlap_issues))
    print('RECOMMENDATION: Re-spawn td-validate với R7 MERGE enforcement')
    sys.exit(1)
print('R7_DEDUP_OK: No overlap detected')
"</script>
        <on_overlap_found>
            <action>RE-SPAWN td-validate với explicit R7 MERGE note trong context</action>
            <action>Pass danh sách fields có overlap vào FIELD_BATCH lại</action>
            <action>Re-run merge + dedup scan sau khi re-spawn</action>
        </on_overlap_found>
    </post_merge_dedup_check>

    <completion_criteria>
        <file_exists>{OUTPUT_DIR}/.td-validate-done</file_exists>
        <content_check>{OUTPUT_FILE} contains "## Kiểm tra Validate"</content_check>
    </completion_criteria>

    <barrier id="validate_barrier">
        <description>SEQUENTIAL BARRIER — MUST check before proceeding to Step 5c</description>
        <script>python3 -X utf8 -c "
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

<step id="5b2" name="Spawn td-validate agents for fileContentFields (if any)" type="parallel">
    <description>Generate validate cases for fields INSIDE uploaded file template (parallel)</description>
    <trigger>After Step 5b completes — ONLY if inventory has fileContentFields[]</trigger>

    <condition>
        <script>python3 -X utf8 -c "
import json, sys
inv = json.load(open('{INVENTORY_FILE}', encoding='utf-8'))
fcf = inv.get('fileContentFields', [])
if not fcf:
    print('NO_FILE_CONTENT_FIELDS')
    sys.exit(0)
print('FILE_CONTENT_FIELDS: ' + str(len(fcf)))
for f in fcf:
    print(f'  - {f[\"name\"]} ({f[\"inputType\"]}, required={f[\"required\"]})')
"</script>
        <on_no_fields>Skip this step entirely — proceed to Step 5c</on_no_fields>
    </condition>

    <preparation>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py get \
  --file {INVENTORY_FILE} \
  --category fileContentFields \
  --keys name,displayName,inputType,required,maxLength</script>
            <purpose>Get file content field list for batching — only key info, NOT full constraints</purpose>
        </action>
        <batch_strategy>
            <batch_size>5 fields per batch</batch_size>
            <example>Batch 1: [debitAccount, taxCode, taxPayerName, taxPayerAddress, substitutesTaxCode]; Batch 2: [substitutesName, substitutesAddress, declarationNumber, declarationDate, treasuryCode]</example>
            <note>Increased from 3 to 5 — reduces number of sub-agents for file content fields.</note>
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
                <param name="BATCH_NUMBER">fc-{N} (use "fc-" prefix to distinguish from API field batches, e.g. fc-1, fc-2)</param>
                <param name="FIELD_BATCH">[{name}:{inputType}:{required}:{maxLength}, ...]</param>
                <param name="FIELD_TYPES_NEEDED">"FileContentField TextInput,FileContentField NumberInput,FileContentField DateInput,FileContentField Droplist"</param>
                <param name="FIELD_SOURCE">fileContentFields</param>
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE or "none"}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>

        <compact_prompt_rule>
            ⛔ Same rule as Step 5b: pass ONLY agent instructions + context params.
            DO NOT include full fileContentField details (displayName, allowedChars, businessValidation, etc.) in prompt.
            The sub-agent queries inventory.py to get field details itself.
        </compact_prompt_rule>
    </per_batch_actions>

    <file_naming>
        <file pattern="{OUTPUT_DIR}/validate-batch-fc-{N}.md" />
        <note>Use "fc-" prefix to distinguish from API field batch files (validate-batch-1.md, validate-batch-2.md...)</note>
    </file_naming>

    <merge>
        <description>Merge file content field batches into output file under new section "## Kiểm tra Validate nội dung file"</description>
        <script>python3 -X utf8 -c "
import os, glob, sys, re

output_dir = r'{OUTPUT_DIR}'
output_file = r'{OUTPUT_FILE}'

content = open(output_file, encoding='utf-8').read()

if '## Kiểm tra Validate nội dung file' in content:
    print('FILE_CONTENT_VALIDATE already exists')
    sys.exit(0)

# Find fc-* batch files in order
fc_files = sorted(glob.glob(os.path.join(output_dir, 'validate-batch-fc-*.md')),
                  key=lambda x: int(re.search(r'fc-(\d+)', x).group(1)))

if not fc_files:
    print('No file content batches found')
    sys.exit(0)

fc_parts = []
for bf in fc_files:
    bc = open(bf, encoding='utf-8').read().strip()
    if bc:
        fc_parts.append(bc)

fc_section = '\n\n## Kiểm tra Validate nội dung file\n\n' + '\n\n'.join(fc_parts)

if '## Kiểm tra chức năng' in content:
    content = content.replace('## Kiểm tra chức năng', fc_section + '\n\n## Kiểm tra chức năng')
else:
    content += fc_section

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(content)
print('FILE_CONTENT_VALIDATE merged: ' + str(len(fc_parts)) + ' batches')
"</script>
    </merge>

    <post_merge_field_coverage_check>
        <description>Verify ALL fileContentFields are present in output</description>
        <script>python3 -X utf8 -c "
import json, sys
inv = json.load(open('{INVENTORY_FILE}', encoding='utf-8'))
fields = [f['displayName'] for f in inv.get('fileContentFields', [])]
content = open('{OUTPUT_FILE}', encoding='utf-8').read()
missing = [f for f in fields if ('### Trường ' + f) not in content]
if missing:
    print('MISSING_FILE_CONTENT_FIELDS: ' + ', '.join(missing))
    sys.exit(1)
print('FILE_CONTENT_FIELD_COVERAGE OK: ' + str(len(fields)) + '/' + str(len(fields)))
"</script>
    </post_merge_field_coverage_check>
</step>

<step id="5c" name="Spawn td-mainflow" type="sub-agent">
    <description>Generate "Kiểm tra chức năng" and "Kiểm tra ngoại lệ" sections</description>
    <trigger>After validate barrier passes</trigger>

    <barrier>
        <description>Barrier check before spawning — only check prerequisites that ALREADY exist (token + validate). Do NOT check for "Kiểm tra chức năng" here — td-mainflow creates it.</description>
        <script>python3 -X utf8 -c "
import sys
c = open('{OUTPUT_FILE}', encoding='utf-8').read()
checks = ['## Kiểm tra token', '## Kiểm tra Validate']
missing = [s for s in checks if s not in c]
print('READY' if not missing else 'NOT READY: MISSING: ' + str(missing))
sys.exit(0 if not missing else 1)
"</script>

        <on_not_ready>
            <action>STOP COMPLETELY. Do NOT spawn td-mainflow.</action>
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
    <note>V1-V4 handled by td-validate. V6-V9 handled by td-mainflow. td-verify covers: gap analysis, V5 duplicate, V9 global, V10 format, V13 scope.</note>
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
    <description>Verify output file, then report completion to user</description>
    <trigger>After Step 6</trigger>

    <verify_output>
        <script>python3 -X utf8 -c "
import json, sys
checks = [
    ('## Kiểm tra chức năng', 'td-mainflow output'),
    ('## Kiểm tra Validate', 'td-validate output'),
    ('## Kiểm tra token', 'td-common output'),
]
# Add file content validate check only if fileContentFields exist
try:
    inv = json.load(open('{INVENTORY_FILE}', encoding='utf-8'))
    if inv.get('fileContentFields', []):
        checks.append(('## Kiểm tra Validate nội dung file', 'file content field validate'))
except: pass
missing = []
for section, label in checks:
    with open('test-design-api.md', encoding='utf-8') as f:
        if section not in f.read():
            missing.append(f'{section} (mising: {label})')
if missing:
    print('MISSING SECTIONS: ' + ', '.join(missing))
    sys.exit(1)
print('ALL_SECTIONS_PRESENT')
"</script>
        <failure_action>Retry spawn td-verify or report to user</failure_action>
    </verify_output>

    <output_message>
```
✅ Test design hoàn thành: {OUTPUT_FILE}
🧠 XMind: {OUTPUT_DIR}/test-design-api.xmind
📋 Inventory: {INVENTORY_FILE}
```
    </output_message>

    <notification>
        <condition>If ### [SỬA] exists in output</condition>
        <message>Auto-added/fixed items count</message>
    </notification>
</step>

<step id="8" name="Generate XMind + Cleanup">
    <description>Convert final .md to .xmind mind map, then remove intermediate files</description>
    <trigger>After Step 7</trigger>

    <action name="generate_xmind">
        <script>python3 $SKILL_SCRIPTS/md_to_xmind.py --input {OUTPUT_FILE} --output {OUTPUT_DIR}/test-design-api.xmind</script>
        <on_error>skip — xmind generation is optional, do not fail the workflow</on_error>
    </action>

    <keep_files>
        <file>inventory.json</file>
        <file>patch.json</file>
        <file>patch-logic.json</file>
        <file>test-design-api.md</file>
        <file>test-design-api.xmind</file>
    </keep_files>

    <delete_patterns>
        <pattern>validate-batch-*.md</pattern>
        <pattern>validate-batch-fc-*.md</pattern>
        <pattern>.td-validate-done</pattern>
        <pattern>_*.py</pattern>
        <pattern>_*.ps1</pattern>
    </delete_patterns>
</step>

---

## Project Structure

```
generate-test-design-api/
├── SKILL.md                      ← Orchestrator workflow (this file)
├── AGENTS.md                     ← Skill-level default rules
├── agents/
│   ├── td-extract-fields.md      ← Extract fields + rsdConstraints → inventory.json
│   ├── td-extract-logic.md       ← Extract business logic → inventory.json
│   ├── td-common.md              ← Generate common sections (token, endpoint)
│   ├── td-validate.md            ← Generate validate per field batch (reads rsdConstraints)
│   ├── td-mainflow.md            ← Generate main flow + exceptions
│   └── td-verify.md              ← Gap analysis, dedup, format check
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
