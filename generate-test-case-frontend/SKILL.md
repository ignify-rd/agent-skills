---
name: generate-test-case-frontend
description: Generate Frontend test cases from RSD/PTTK (or mindmap) and output to test-cases.json. For UI screens only. Use when user says "sinh test case frontend", "sinh test case fe", "sinh test case giao diện", "generate frontend test case", "tạo test case màn hình", or provides Confluence links to RSD/PTTK or a mindmap file for a UI screen.
---

# Test Case Generator — Frontend Mode (Orchestrator)

<role_definition>
    <task_type>orchestrator</task_type>
    <identity>You coordinate specialized sub-agents to generate Frontend UI test cases. You orchestrate the workflow but do NOT read test-design or inventory files directly.</identity>

    <boundary>
        <permitted>
            <action>Query inventory via inventory.py scripts</action>
            <action>List catalog files via search.py scripts</action>
            <action>Read catalog files (limited) for wording reference</action>
            <action>Spawn sub-agents with context blocks</action>
            <action>Check file existence (sentinel files, batch files)</action>
        </permitted>

        <forbidden>
            <action>Read test-design-frontend.md directly</action>
            <action>Read inventory.json directly (query only via inventory.py)</action>
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
        <condition>If orchestrator reads test-design-frontend.md or inventory.json directly</condition>
        <consequence>VIOLATION: architecture breach, causes context pollution, distorts output</consequence>
        <recovery>Use inventory.py script queries instead. Only sub-agents (tc-*) may read those files.</recovery>
    </hard_stop>

    <auto_invoke id="missing_design">
        <condition>test-design-frontend.md hoặc inventory.json chưa có trong OUTPUT_DIR</condition>
        <consequence>AUTO-INVOKE generate-test-design-frontend — không hỏi lại user, tự động thực thi ngay</consequence>
        <recovery>Tìm generate-test-design-frontend/SKILL.md (sibling directory), đọc và thực thi toàn bộ workflow với cùng inputs của user, sau đó tiếp tục sinh test case.</recovery>
    </auto_invoke>

    <hard_stop id="missing_output_dir">
        <condition>OUTPUT_DIR không được cung cấp và không thể suy luận từ context</condition>
        <consequence>STOP — hỏi user đường dẫn thư mục output</consequence>
        <recovery>"Vui lòng cung cấp đường dẫn thư mục output (ví dụ: feature-1/)"</recovery>
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
        <condition>Any agent is about to write a helper/temp script file (e.g. _*.py, _*.ps1, _check_*.py, etc.)</condition>
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

<step id="0b" name="Check & Auto-generate Test Design if Missing">
    <trigger>Always — before any generation step</trigger>

    <required_inputs>
        <input name="Output Folder" var="OUTPUT_DIR" source="user or context" required="true">
            <description>Thư mục output chứa test design và test cases</description>
            <example>feature-1/</example>
            <infer>Suy luận từ tên feature/folder user đề cập trong chat nếu không nói rõ</infer>
        </input>
    </required_inputs>

    <derived_defaults>
        <var name="TEST_DESIGN_FILE">{OUTPUT_DIR}/test-design-frontend.md</var>
        <var name="INVENTORY_FILE">{OUTPUT_DIR}/inventory.json</var>
        <var name="OUTPUT_FILE">{OUTPUT_DIR}/test-cases.json</var>
    </derived_defaults>

    <actions>
        <action type="bash" id="detect-design-files">
            <script>python3 -X utf8 -c "
import os
td  = r'{OUTPUT_DIR}/test-design-frontend.md'
inv = r'{OUTPUT_DIR}/inventory.json'
ok  = os.path.exists(td) and os.path.getsize(td) > 10 \
    and os.path.exists(inv) and os.path.getsize(inv) > 10
print('FOUND' if ok else 'MISSING')
"</script>
            <stores>designStatus</stores>
        </action>
    </actions>

    <branch condition="designStatus == FOUND">
        <message>Test design đã có → tiến hành sinh test case.</message>
        <proceed_to>Step 1</proceed_to>
    </branch>

    <branch condition="designStatus == MISSING">
        <message>Test design chưa có. Đang tự động sinh test design trước (không cần xác nhận)...</message>

        <action type="find_design_skill">
            <script>python3 -X utf8 -c "
import os

def find_skill(name, start='.', max_depth=5):
    current = os.path.abspath(start)
    for _ in range(max_depth):
        candidate = os.path.join(current, name, 'SKILL.md')
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return 'NOT_FOUND'

print(find_skill('generate-test-design-frontend'))
"</script>
            <stores>DESIGN_SKILL_MD</stores>
            <on_not_found>STOP — thông báo không tìm thấy generate-test-design-frontend/SKILL.md</on_not_found>
        </action>

        <action type="invoke_design_skill">
            <description>
                Đọc DESIGN_SKILL_MD và thực thi TOÀN BỘ workflow của generate-test-design-frontend.
                KHÔNG hỏi lại user. Truyền nguyên inputs của user (RSD URL, Confluence link...) + OUTPUT_DIR = {OUTPUT_DIR}.
                Thực thi như thể user vừa yêu cầu sinh test design cho cùng feature.
            </description>
            <steps>
                <step>Read {DESIGN_SKILL_MD}</step>
                <step>Execute all steps in generate-test-design-frontend/SKILL.md with current user inputs and OUTPUT_DIR = {OUTPUT_DIR}</step>
                <step>Verify completion:
python3 -X utf8 -c "
import os, sys
td  = r'{OUTPUT_DIR}/test-design-frontend.md'
inv = r'{OUTPUT_DIR}/inventory.json'
if not os.path.exists(td):  print('ERROR: test-design-frontend.md missing');  sys.exit(1)
if not os.path.exists(inv): print('ERROR: inventory.json missing'); sys.exit(1)
print('OK: design files ready')
"</step>
            </steps>
        </action>

        <proceed_to>Step 1</proceed_to>
    </branch>
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
" "$(pwd)/generate-test-case-frontend/scripts/search.py" 2>/dev/null || echo "generate-test-case-frontend/scripts"</script>
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
" "$(pwd)/generate-test-case-frontend/agents/tc-context.md" 2>/dev/null || echo "generate-test-case-frontend/agents"</script>
            <stores>SKILL_AGENTS</stores>
        </action>
    </actions>

    <fallback_paths>
        <path>.claude/skills/generate-test-case-frontend</path>
        <path>.cursor/skills/generate-test-case-frontend</path>
        <path>node_modules/generate-test-case-frontend</path>
    </fallback_paths>

    <output>
        <var name="SKILL_SCRIPTS">Path to skill scripts directory</var>
        <var name="SKILL_AGENTS">Path to agents directory</var>
    </output>
</step>

<step id="2" name="Catalog Listing (CATALOG_SAMPLE)">
    <actions>
        <action type="bash">
            <script>python3 $SKILL_SCRIPTS/search.py --list --domain frontend</script>
            <stores>catalogList</stores>
        </action>
    </actions>

    <catalog_reading_rules>
        <rule condition="catalog_count <= 3">
            <action>Select up to 3 most relevant files — dùng Read tool với limit=80 cho mỗi file</action>
        </rule>
        <rule condition="catalog_count > 3">
            <action>Select 3 most relevant files (by name, screen type, same business group, similar UI structure)</action>
            <action>Dùng Read tool với limit=80 cho mỗi file — KHÔNG đọc toàn bộ file</action>
        </rule>
        <rule condition="no_relevant_files">
            <action>Read first 2–3 files in the list (50 lines each)</action>
        </rule>
    </catalog_reading_rules>

    <output>
        <var name="CATALOG_SAMPLE">{OUTPUT_DIR}/catalog-sample.md — FILE PATH (không phải nội dung inline). Sau khi đọc catalog với limit=80, ghi toàn bộ nội dung đọc được vào file này bằng Write tool.</var>
    </output>

    <note>
        Catalog = highest priority source for wording.
        ⚠️ CATALOG_SAMPLE = FILE PATH đến {OUTPUT_DIR}/catalog-sample.md, KHÔNG phải nội dung text.
        Sau khi đọc catalog (limit=80/file): ghi vào catalog-sample.md bằng Write tool.
        Truyền file path cho sub-agents — sub-agents tự đọc Read(CATALOG_SAMPLE, limit=80) khi cần.
    </note>
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
    <description>Generate BATCH 1 — UI + permission test cases</description>
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
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <file_exists>{OUTPUT_DIR}/batch-1.json</file_exists>
    </completion_criteria>
</step>

<step id="5a" name="Query inventory — batch fields + detect screenType">
    <description>Get fieldConstraints list and detect screen type for routing</description>
    <trigger>After Step 4</trigger>

    <actions>
        <action type="bash">
            <script>python3 $SKILL_SCRIPTS/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints</script>
            <stores>fieldConstraints</stores>
        </action>
        <action type="bash">
            <script>python3 $SKILL_SCRIPTS/inventory.py summary --file {INVENTORY_FILE}</script>
            <stores>inventorySummary</stores>
        </action>
    </actions>

    <batch_strategy>
        <rule>Extract screenType from summary (LIST | FORM | POPUP | DETAIL)</rule>
        <rule>Group fields into batches of max 3 fields each: Batch 1: [F1, F2, F3], Batch 2: [F4, F5, F6], ... (⚠️ tối đa 3 fields/batch)</rule>
        <rule>Detect FIELD_TYPES_NEEDED per batch: extract "type" values from fieldConstraints for each field in batch — used as FIELD_TYPES_NEEDED for tc-validate (comma-separated, e.g. "textbox,combobox")</rule>
        <rule>If fieldConstraints returns 0 items: skip Step 5b, proceed to Step 5c</rule>
    </batch_strategy>
</step>

<step id="5b" name="Spawn ALL tc-validate agents + tc-search IN PARALLEL" type="parallel">
    <description>
        Spawn ALL tc-validate batches in parallel — one sub-agent per batch.
        If screenType = LIST, also spawn tc-search in the same parallel wave.
        Each sub-agent writes to its own output file — never share output files.
    </description>
    <trigger>After Step 5a</trigger>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/tc-validate.md</file>
        </action>
        <action type="spawn_subagent" repeat="per_batch">
            <agent_type>tc-validate</agent_type>
            <prompt>{tc-validate.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="TC_CONTEXT_FILE">{OUTPUT_DIR}/tc-context.json</param>
                <param name="TEST_DESIGN_FILE">{TEST_DESIGN_FILE}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="OUTPUT_DIR">{OUTPUT_DIR}</param>
                <param name="BATCH_NUMBER">{N}</param>
                <param name="FIELD_BATCH">[{fieldName}:{fieldType}, ...]</param>
                <param name="FIELD_TYPES_NEEDED">"{comma-separated field types for --section}"</param>
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>

        <action type="spawn_subagent" condition="screenType == LIST">
            <agent_type>tc-search</agent_type>
            <prompt>{tc-search.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="TC_CONTEXT_FILE">{OUTPUT_DIR}/tc-context.json</param>
                <param name="TEST_DESIGN_FILE">{TEST_DESIGN_FILE}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="OUTPUT_DIR">{OUTPUT_DIR}</param>
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_check>
        <action type="bash">
            <script>python3 -X utf8 -c "
import sys, os, glob
output_dir = '{OUTPUT_DIR}'
batches = sorted(glob.glob(os.path.join(output_dir, 'validate-batch-*.json')))
if not batches:
    print('ERROR: no validate batches found')
    sys.exit(1)
print(f'Found {len(batches)} validate batch(es)')
for b in batches:
    print(f'  {os.path.basename(b)}: {os.path.getsize(b)} bytes')
"</script>
        </action>
        <on_success>
            <create_sentinel>
                <file>{OUTPUT_DIR}/.tc-validate-done</file>
                <content>done</content>
            </create_sentinel>
        </on_success>
        <on_fail>
            <action>Re-spawn missing batch. Check which validate-batch-*.json files are absent and re-run only those agents.</action>
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
    <description>Generate BATCH 3 — function + button test cases</description>
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
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <file_exists>{OUTPUT_DIR}/batch-3.json</file_exists>
    </completion_criteria>
</step>

<step id="5d" name="Spawn tc-workflow" type="sequential-conditional">
    <description>Generate BATCH workflow — Maker-Checker + role flows (optional)</description>
    <trigger>After Step 5c</trigger>

    <condition_check>
        <script>python3 -X utf8 -c "
import json, sys
inv = json.load(open('{INVENTORY_FILE}', encoding='utf-8'))
if inv.get('permissions') or inv.get('statusTransitions'):
    print('SPAWN')
else:
    print('SKIP')
"</script>
        <on_skip>Skip Step 5d entirely, proceed to Step 6.</on_skip>
    </condition_check>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/tc-workflow.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>tc-workflow</agent_type>
            <prompt>{tc-workflow.md content}</prompt>
            <context>
                <param name="SKILL_SCRIPTS">{SKILL_SCRIPTS}</param>
                <param name="TC_CONTEXT_FILE">{OUTPUT_DIR}/tc-context.json</param>
                <param name="TEST_DESIGN_FILE">{TEST_DESIGN_FILE}</param>
                <param name="INVENTORY_FILE">{INVENTORY_FILE}</param>
                <param name="OUTPUT_DIR">{OUTPUT_DIR}</param>
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE}</param>
                <param name="PROJECT_RULES">{projectRules or "none"}</param>
            </context>
        </action>
    </actions>

    <completion_criteria>
        <file_exists>{OUTPUT_DIR}/batch-workflow.json</file_exists>
    </completion_criteria>
</step>

<step id="5c.5" name="Inject SQL into batch-3 (deterministic)">
    <trigger>After Step 5c — batch-3.json exists</trigger>

    <actions>
        <action type="bash">
            <script>python3 -X utf8 {SKILL_SCRIPTS}/inject_sql.py \
                --test-design {TEST_DESIGN_FILE} \
                --batch {OUTPUT_DIR}/batch-3.json
            </script>
        </action>
    </actions>

    <on_failure>Print warning and CONTINUE — do not stop workflow</on_failure>

    <note>Script chi copy SQL tu test-design-frontend.md — KHONG tu sinh SQL.
    Neu test design chua co SQL cho mot heading → skip heading do, khong inject placeholder.
    Chi inject vao ## Kiem tra chuc nang — khong bao gio inject vao ## Kiem tra Validate.</note>
</step>

<step id="6" name="Spawn tc-verify" type="sequential">
    <description>Gap analysis, dedup, and final output</description>
    <trigger>After Step 5c.5 (and Step 5d if spawned)</trigger>

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
                <param name="CATALOG_SAMPLE">{CATALOG_SAMPLE}</param>
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
                {OUTPUT_DIR_NAME} = tên thư mục chứa test-cases.json (ví dụ: "feature-1").
                {PROJECT_ROOT} = thư mục gốc của project (chứa AGENTS.md, catalog/).
                Nếu upload thất bại (lỗi auth, network...) → in cảnh báo và TIẾP TỤC (không dừng).
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
    python $SKILL_SCRIPTS/upload_gsheet.py {OUTPUT_DIR_NAME} --project-root {PROJECT_ROOT}
```
        </output_message>
    </on_failure>
</step>

---

## Project AGENTS.md Override

| Category | Can Override? |
|----------|--------------|
| Chat input / user request | **Always — HIGHEST PRIORITY** |
| testAccount | Yes |
| testSuiteName convention | Yes |
| Writing style (ngắn/dài, cách viết step) | Yes |
| Section assignment (buttons vào section nào) | Yes |
| Output JSON field names | No |
| Batch strategy (BATCH 1/2/3 split) | No |
| Field type dispatch table | No |
| Importance mapping | No |

---

## Quick Reference — Batch File Naming

| Batch | File | Content |
|-------|------|---------|
| BATCH 1 | `batch-1.json` | UI + permission test cases |
| BATCH search | `batch-search.json` | Search/filter/pagination (LIST screens only, optional) |
| BATCH 2 | `validate-batch-1.json`, `validate-batch-2.json`, ... | Validate cases per field batch |
| BATCH 3 | `batch-3.json` | Function + button cases |
| BATCH workflow | `batch-workflow.json` | Maker-Checker + role flows (optional) |
| Merged | `test-cases-merged.json` | After merge_batches.py |
| Final | `test-cases.json` | After gap fill + project rules |

---

## Quick Reference — Frontend testCaseName Format

- **testCaseName = LẤY TRỰC TIẾP từ mindmap bullet** — KHÔNG thêm prefix, KHÔNG thêm screen name
- **testSuiteName:** theo catalog convention — field sub-suites (`"Textbox: Tên cấu hình SLA"`) hoặc fallback `"Kiểm tra validate"`

| Catalog convention | testSuiteName |
|-------------------|---------------|
| Field sub-suites | `"Textbox: Tên cấu hình SLA"` |
| No sub-suites | `"Kiểm tra validate"` |

Examples:
- Mindmap: `- Kiểm tra khi nhập 101 ký tự`
  → testCaseName: `Kiểm tra khi nhập 101 ký tự` (NO prefix)
- Mindmap: `### Kiểm tra điều hướng đến màn hình`
  → testCaseName: `Kiểm tra điều hướng đến màn hình`
