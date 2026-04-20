---
name: generate-test-design-frontend
description: Generate Frontend test design mindmap from RSD/PTTK on Confluence. For UI screens only. Use when user says "sinh test design frontend", "sinh test design giao diện", "tao mindmap màn hình", or provides Confluence links to RSD/PTTK for a UI screen.
---

# Test Design Generator — Frontend Mode (Orchestrator)

Generate test design documents (.md) for Frontend UI screens bằng cách điều phối các sub-agents chuyên biệt.

> **Scope**: Frontend test design (mindmap) only. NOT API, NOT test case generation.

## When to Apply

- User provides RSD/PTTK for a UI screen and asks to generate test design or mindmap
- User says "sinh test design frontend", "sinh test design giao diện", "tạo test design màn hình"

## Prerequisites

Python 3 installed. Check: `python3 --version || python --version`

<role_definition>
    <task_type>orchestrator</task_type>
    <identity>You coordinate specialized sub-agents to generate Frontend test design documents (.md) from RSD/PTTK. You orchestrate the workflow but do NOT read RSD/PTTK directly.</identity>

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
            <action>Use WebFetch for Confluence URLs (requires authentication)</action>
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
    <hard_stop id="no_confluence_webfetch">
        <condition>If orchestrator uses WebFetch for Confluence URL</condition>
        <consequence>VIOLATION — Confluence requires authentication, WebFetch will fail</consequence>
        <recovery>
            Đọc nội dung RSD/PTTK từ Confluence bằng Atlassian MCP tools:
            1. Resolve cloudId bằng getConfluenceSpaces()
            2. Trích xuất pageId từ Confluence URL (pattern: /pages/&lt;pageId&gt;/)
            3. Gọi getConfluencePage(cloudId, pageId) để lấy nội dung trang (markdown)
        </recovery>
    </hard_stop>

    <hard_stop id="no_temp_files">
        <condition>Any agent is about to write a helper/temp script file (e.g. _*.py, _*.ps1, _check_*.py, v.v.)</condition>
        <consequence>VIOLATION — do NOT create temp script files on disk under any circumstances</consequence>
        <recovery>Dùng python3 -X utf8 -c "..." inline trong Bash, hoặc dùng Read/Edit/Write tools trực tiếp. Never write a helper script to disk.</recovery>
    </hard_stop>

    <hard_stop id="missing_inputs">
        <condition>Required inputs missing (RSD URL, output folder)</condition>
        <consequence>STOP — ask user for required inputs. NEVER guess URLs.</consequence>
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
</guardrails>

---

## Workflow

<step id="0" name="Validate Project Setup & Load Project Rules">
    <trigger>Always — first step</trigger>
    <actions>
        1. Check `catalog/` at project root — nếu không có → hỏi user chạy `test-genie init`
        2. Check & READ `AGENTS.md` at project root → store as `projectRules`
        3. Nếu không có AGENTS.md → dùng skill-level defaults, thông báo user

        **⚠️ projectRules override tất cả skill defaults.**
    </actions>
</step>

<step id="0b" name="Validate Required Inputs">
    <trigger>Always — before any other step</trigger>

    <required_inputs>
        <input name="RSD Confluence URL" var="RSD_URL" source="user" required="true">
            <description>Confluence page URL of RSD document</description>
            <example>https://your-site.atlassian.net/wiki/spaces/SPACE/pages/123456/RSD</example>
        </input>
        <input name="PTTK Confluence URL" var="PTTK_URL" source="user" required="false">
            <description>Confluence page URL of PTTK document (optional)</description>
        </input>
        <input name="Output folder" var="OUTPUT_DIR" source="user" required="true">
            <description>Output directory</description>
            <example>feature-1/</example>
        </input>
        <input name="Screen scope" var="SCREEN_SCOPE" source="user" required="false">
            <description>Optional scope (e.g. "chỉ generate US05.2")</description>
        </input>
    </required_inputs>

    <guardrails>
        <rule>NEVER guess URLs. Nếu thiếu → hỏi user cung cấp link Confluence.</rule>
    </guardrails>

    <derived_vars>
        <var name="INVENTORY_FILE">{OUTPUT_DIR}/inventory.json</var>
        <var name="OUTPUT_FILE">{OUTPUT_DIR}/test-design-frontend.md</var>
    </derived_vars>
</step>

<step id="1" name="Mode Detection (Frontend Mode Only)">
    <rules>
        <rule condition="contains màn hình, screen, giao diện, button, textbox, combobox">
            <result>High confidence Frontend → proceed</result>
        </rule>
        <rule condition="title matches (GET|POST|PUT|DELETE|PATCH)\s+/">
            <result>suggest generate-test-design-api</result>
        </rule>
        <rule condition="unclear">
            <result>ask user</result>
        </rule>
    </rules>
</step>

<step id="2" name="Resolve Paths & Load Priority Rules">
    <actions>
        <action type="bash">

```bash
# Resolve SKILL_SCRIPTS — dùng Python thay vì find (cross-platform)
SKILL_SCRIPTS=$(python3 -X utf8 -c "
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
" "$(pwd)/generate-test-design-frontend/scripts/search.py" 2>/dev/null || echo "generate-test-design-frontend/scripts")

# Resolve SKILL_AGENTS
SKILL_AGENTS=$(python3 -X utf8 -c "
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
" "$(pwd)/generate-test-design-frontend/agents/td-extract.md" 2>/dev/null || echo "generate-test-design-frontend/agents")
```

        </action>
    </actions>

    <fallback_paths>
        <path>.claude/skills/generate-test-design-frontend</path>
        <path>.cursor/skills/generate-test-design-frontend</path>
        <path>node_modules/generate-test-design-frontend</path>
    </fallback_paths>

    <actions>
        <action type="bash">

```bash
python3 $SKILL_SCRIPTS/search.py --ref priority-rules
```

        </action>
    </actions>

    <output>
        Xác định các paths dùng xuyên suốt:
        - `INVENTORY_FILE` = `{output-folder}/inventory.json`
        - `OUTPUT_FILE` = `{output-folder}/test-design-frontend.md`
        - `OUTPUT_DIR` = `{output-folder}`
    </output>
</step>

<step id="3" name="Catalog Example">
    <actions>
        <action type="bash">

```bash
python3 $SKILL_SCRIPTS/search.py --list --domain frontend
```

        </action>
    </actions>

    <catalog_reading_rules>
        Đọc **tối đa 3 file** có chức năng gần nhất với màn hình đang generate (dựa theo tên file + title):
        - Chọn catalog phù hợp nhất (cùng screen type LIST/FORM/DETAIL, cùng domain, hoặc cấu trúc tương tự)
        - Nếu không có file nào phù hợp → đọc file đầu tiên trong danh sách
        - Dùng Read tool để đọc từng file — KHÔNG dùng search.py để đọc file (VD: `Read("catalog/frontend/Screen_Ten_man_hinh.md", limit=80)`)
    </catalog_reading_rules>

    <output>
        <var name="CATALOG_SAMPLE">
            Dùng Read tool để đọc **50 dòng đầu + 50 dòng cuối** của file được chọn (hoặc toàn bộ nếu &lt; 100 dòng).
            Ghi nội dung đã đọc vào {OUTPUT_DIR}/catalog-sample.md (xem catalog_file_write bên dưới).
            CATALOG_SAMPLE = {OUTPUT_DIR}/catalog-sample.md — FILE PATH, KHÔNG phải nội dung inline.
        </var>
    </output>

    <catalog_file_write>
        Sau khi đọc catalog: ghi toàn bộ nội dung đã đọc vào {OUTPUT_DIR}/catalog-sample.md
        dùng Write tool. BẮT BUỘC thực hiện trước khi spawn bất kỳ sub-agent nào.
    </catalog_file_write>

    <note>
        Catalog = nguồn WORDING cao nhất. Luôn truyền CATALOG_SAMPLE (file path) cho sub-agents.
        ⚠️ CATALOG_SAMPLE = FILE PATH đến catalog-sample.md, KHÔNG phải nội dung text inline.
        Sub-agents tự đọc Read(CATALOG_SAMPLE, limit=80) khi cần wording reference.
    </note>
</step>

<step id="3b" name="Sao chép nội dung RSD/PTTK (BC1 — BẮT BUỘC)">
    <trigger>TRƯỚC Step 4 — BẮT BUỘC. Không được bỏ qua hoặc gộp chung với bước khác.</trigger>

    <actions>
        **Trước khi gọi bất kỳ sub-agent nào**, phải:
        1. **Sao chép nội dung RSD** vào `{OUTPUT_DIR}/rsd-source.md` — dùng nội dung đã lấy từ `getConfluencePage`
        2. **Nếu có PTTK** → sao chép nội dung PTTK vào `{OUTPUT_DIR}/pttk-source.md`
        3. **Tạo file marker** `{OUTPUT_DIR}/.bc1-copy-done` để đánh dấu BC1 hoàn thành

```
BC1: Sao chép nội dung nguồn
  ✅ RSD → rsd-source.md
  ✅ PTTK → pttk-source.md (nếu có)
  ✅ Marker: .bc1-copy-done
```

        **⚠️ SAI — KHÔNG ĐƯỢC LÀM:**
        - Không sao chép ngay vào inventory (phải extract trước)
        - Không bỏ qua bước này vì "sẽ đọc lại từ Confluence"
        - Không gộp BC1 chung với BC2
    </actions>

    <barrier id="bc1_barrier">
        <description>SEQUENTIAL BARRIER — BẮT BUỘC CHẠY TRƯỚC KHI SPAWN Step 4</description>
        <script>python3 -X utf8 -c "
import sys, os
sentinel = '{output-folder}/.bc1-copy-done'
rsd = '{OUTPUT_DIR}/rsd-source.md'
if not os.path.exists(sentinel):
    print('NOT READY: .bc1-copy-done missing — chua lam BC1')
    sys.exit(1)
if not os.path.exists(rsd):
    print('NOT READY: rsd-source.md missing')
    sys.exit(1)
print('READY')
"</script>
        <on_not_ready>DỪNG HOÀN TOÀN. KHÔNG spawn Step 4. Chạy lại Step 3b.</on_not_ready>
    </barrier>
</step>

<step id="4" name="Sub-agent — td-extract (Trích xuất dữ liệu từ BC1 đã sao chép)">
    <description>Spawn sub-agent để extract RSD/PTTK/images và tạo inventory.</description>
    <trigger>After bc1_barrier passes</trigger>

    <pre_actions>
        Resolve cloudId bằng `getConfluenceSpaces()` và trích xuất pageId từ Confluence URLs (pattern: `/pages/&lt;pageId&gt;/`).
    </pre_actions>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/td-extract.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>td-extract</agent_type>
            <prompt>{td-extract.md content}</prompt>
            <context>
```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {resolved SKILL_SCRIPTS path}
INVENTORY_FILE: {INVENTORY_FILE}
OUTPUT_DIR: {OUTPUT_DIR}
CLOUD_ID: {cloudId từ Atlassian MCP}
RSD_PAGE_ID: {pageId trích từ RSD Confluence URL}
PTTK_PAGE_ID: {pageId trích từ PTTK Confluence URL hoặc "none"}
SCREEN_NAME: {tên màn hình từ RSD title}
SCREEN_TYPE: {LIST|FORM|POPUP|DETAIL — xác định sơ bộ từ RSD}
PROJECT_RULES: {projectRules nếu có, hoặc "none"}
===================
```
            </context>
        </action>
    </actions>

    <completion_criteria>
        <condition>`{INVENTORY_FILE}` được tạo và `fieldConstraints` không rỗng</condition>
        <condition>Nếu fieldConstraints = 0 → Hỏi user trước khi tiếp tục</condition>
        <condition>Nếu có conflicts PTTK/RSD → Hỏi user để xác nhận</condition>
    </completion_criteria>
</step>

<step id="5a" name="Sub-agent — td-common (Sinh common UI + permissions)">
    <trigger>After Step 4</trigger>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/td-common.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>td-common</agent_type>
            <prompt>{td-common.md content}</prompt>
            <context>
```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
INVENTORY_FILE: {path}
OUTPUT_FILE: {path}
CATALOG_SAMPLE: {wording snippet từ Step 3, hoặc "none"}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```
            </context>
        </action>
    </actions>

    <completion_criteria>
        <condition>`{OUTPUT_FILE}` tồn tại và chứa `## Kiểm tra giao diện chung`</condition>
    </completion_criteria>
</step>

<step id="5b" name="Sub-agent — td-validate (Sinh validate, song song theo batch)">
    <trigger>After Step 5a</trigger>

    <preparation>
        Đọc `{INVENTORY_FILE}` để lấy tất cả `fieldConstraints[]`.
        Nhóm fields thành batches tối đa **3 fields** mỗi batch.

        **Spawn TẤT CẢ batch sub-agents song song** — mỗi batch 1 sub-agent độc lập.
    </preparation>

    <per_batch_actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/td-validate.md</file>
        </action>
        <action type="spawn_subagent" repeat="per_batch">
            <agent_type>td-validate</agent_type>
            <prompt>{td-validate.md content}</prompt>
            <context>
```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
INVENTORY_FILE: {path}
OUTPUT_DIR: {output-folder}
BATCH_NUMBER: {N}
FIELD_BATCH: [{fieldName}:{type}:{required}:{maxLength}, ...]
FIELD_TYPES_NEEDED: "{comma-separated section names for --section}"
CATALOG_SAMPLE: {wording snippet hoặc "none"}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```
            </context>
        </action>
    </per_batch_actions>

    <file_naming>
        <file pattern="{output-folder}/validate-batch-{N}.md" description="Output per batch" />
        <note>⚠️ Mỗi sub-agent ghi vào file riêng — KHÔNG share output files.</note>
    </file_naming>

    <merge>
        <description>Sau khi TẤT CẢ batches hoàn thành — merge bằng script:</description>
        <script>python3 $SKILL_SCRIPTS/merge_validate.py \
  --output-dir {output-folder} \
  --output-file {OUTPUT_FILE}</script>
        <note>Script tự động strip garbage headers và tạo sentinel `.td-validate-done`. Nếu exit 1 → đọc error, re-spawn batch bị lỗi.</note>
    </merge>

    <completion_criteria>
        <condition>File `{output-folder}/.td-validate-done` tồn tại</condition>
        <condition>`{OUTPUT_FILE}` chứa `## Kiểm tra Validate`</condition>
    </completion_criteria>

    <barrier id="validate_barrier">
        <description>SEQUENTIAL BARRIER — BẮT BUỘC CHẠY TRƯỚC KHI SPAWN Step 5c</description>
        <script>python3 -X utf8 -c "
import sys, os
sentinel = '{output-folder}/.td-validate-done'
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
        <on_not_ready>DỪNG HOÀN TOÀN. KHÔNG spawn Step 5c. Debug Step 5b trước.</on_not_ready>
    </barrier>
</step>

<step id="5c" name="Sub-agent — td-mainflow (Sinh grid + function + timeout)">
    <trigger>After validate_barrier passes</trigger>

    <note>
        **⚠️ QUY TẮC GỘP BẮT BUỘC — Lưu + Đẩy duyệt phải trong CÙNG 1 luồng:**
        - Nếu màn hình có cả button "Lưu" và "Đẩy duyệt" → phải viết trong cùng 1 section `### Kiểm tra khi click button "Lưu"` VÀ `### Kiểm tra khi click button "Đẩy duyệt"` bên dưới, KHÔNG được tách ra làm 2 luồng riêng
        - KHÔNG được viết "Lưu" ở trên rồi "Đẩy duyệt" ở dưới như 2 bước độc lập
        - Nếu RSD có 2 button này → gộp thành 1 nhóm chức năng chính
    </note>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/td-mainflow.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>td-mainflow</agent_type>
            <prompt>{td-mainflow.md content}</prompt>
            <context>
```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
INVENTORY_FILE: {path}
OUTPUT_FILE: {path}
CATALOG_SAMPLE: {wording snippet hoặc "none"}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```
            </context>
        </action>
    </actions>

    <completion_criteria>
        <condition>`{OUTPUT_FILE}` chứa `## Kiểm tra chức năng` và coverage report</condition>
    </completion_criteria>

    <barrier id="mainflow_barrier">
        <description>SEQUENTIAL BARRIER — BẮT BUỘC CHẠY TRƯỚC KHI SPAWN Step 6</description>
        <script>python3 -X utf8 -c "
import sys
c = open('{OUTPUT_FILE}', encoding='utf-8').read()
required = ['## Kiểm tra giao diện chung', '## Kiểm tra phân quyền',
            '## Kiểm tra Validate', '## Kiểm tra chức năng']
missing = [s for s in required if s not in c]
print('READY' if not missing else 'NOT READY: MISSING: ' + str(missing))
sys.exit(0 if not missing else 1)
"</script>
        <on_not_ready>DỪNG HOÀN TOÀN. KHÔNG spawn Step 6. Debug bước thiếu trước.</on_not_ready>
    </barrier>
</step>

<step id="6" name="Sub-agent — td-verify (Gap-fill + Cross-section check)">
    <trigger>After mainflow_barrier passes</trigger>

    <note>
        V3/V4 đã được td-validate checkpoint per-field. V6-V9 đã được td-mainflow self-check.
        td-verify CHỈ làm: gap analysis, V5 duplicate, V9 global scan, V10 format.
        **KHÔNG đọc toàn bộ OUTPUT_FILE** — dùng grep/Python extract sections.
    </note>

    <actions>
        <action type="read_agent_instructions">
            <file>SKILL_AGENTS/td-verify.md</file>
        </action>
        <action type="spawn_subagent">
            <agent_type>td-verify</agent_type>
            <prompt>{td-verify.md content}</prompt>
            <context>
```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
INVENTORY_FILE: {path}
OUTPUT_FILE: {path}
===================
```
            </context>
        </action>
    </actions>

    <completion_criteria>
        <condition>Self-check in ra 4/4 ✅ hoặc tất cả gaps/vi phạm đã được sửa</condition>
    </completion_criteria>
</step>

<step id="7" name="Final Output">
    <actions>
        Thông báo user:
```
✅ Test design hoàn thành: {OUTPUT_FILE}
📋 Inventory: {INVENTORY_FILE}
```
        Nếu có `### [SỬA]` trong output → thông báo số lượng items được tự động thêm/sửa.
    </actions>
</step>
