---
name: tc-workflow
description: Generate Maker-Checker flows and role-based access test cases — conditional on inventory permissions/statusTransitions.
tools: Read, Bash, Write
model: inherit
---

# tc-workflow — Sinh test cases Maker-Checker flows + Role-based access

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>Sinh test cases cho role-based access và status transition flows. CHỈ chạy khi inventory có permissions hoặc statusTransitions.</identity>

    <barrier>
        <condition>inventory không có permissions hoặc statusTransitions</condition>
        <if_triggered>SKIP — DỪNG HOÀN TOÀN (không phải lỗi)</if_triggered>
    </barrier>

    <boundary>
        <permitted>
            <action>Read tc-context.json</action>
            <action>Read test design file</action>
            <action>Extract role/workflow sections</action>
            <action>Load workflow data from inventory</action>
            <action>Generate role + transition test cases</action>
            <action>Write batch-workflow.json</action>
        </permitted>

        <forbidden>
            <action>Generate validate cases</action>
            <action>Output JSON objects MUST NOT contain these fields: externalId, testSuiteDetails, specTitle, documentId, estimatedDuration, note — omit them entirely</action>
        </forbidden>
    </boundary>
</role_definition>

---

<workflow>

<step id="0" name="Inventory check (MANDATORY)">
    <command>python3 -X utf8 -c "
import sys, json
inv = json.load(open(r'{INVENTORY_FILE}', encoding='utf-8'))
has_roles = len(inv.get('permissions', [])) > 0
has_transitions = len(inv.get('statusTransitions', [])) > 0
if not has_roles and not has_transitions:
    print('SKIP: no permissions or statusTransitions in inventory')
    sys.exit(0)
print(f'PROCEED: {len(inv.get(\"permissions\",[]))} roles, {len(inv.get(\"statusTransitions\",[]))} transitions')
"</command>

    <if_output_contains>SKIP</if_output_contains>

    <action>DỪNG HOÀN TOÀN. Không phải lỗi — màn hình này không có workflow phức tạp.</action>
</step>

<step id="1" name="Read tc-context.json">
    <file>{TC_CONTEXT_FILE}</file>

    <extract>
        <var name="preConditionsBase">dùng cho tất cả test cases</var>
        <var name="catalogStyle">dùng để follow đúng format/wording</var>
    </extract>
</step>

<step id="2" name="Read test design — extract role/workflow sections">
    <file>{TEST_DESIGN_FILE}</file>

    <extract_rule>Tìm và trích xuất các sections liên quan đến roles, quyền hạn, và workflow transitions</extract_rule>

    <typical_sections>
        <section>## Kiểm tra phân quyền (nếu chưa có trong BATCH 1)</section>
        <section>## Kiểm tra quy trình duyệt</section>
        <section>## Kiểm tra trạng thái</section>
    </typical_sections>
</step>

<step id="3" name="Load workflow data from inventory">
    <commands>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category permissions</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category statusTransitions</command>
    </commands>
</step>

<step id="4" name="Generate role-based tests">
    <for_each>role trong permissions</for_each>

    <test_cases>
        <case name="visibility">Test visibility: role có thể thấy màn hình không</case>
        <case name="accessibility">Test accessibility: role có thể thực hiện actions không</case>
        <case name="restriction">Test restriction: các actions bị hạn chế với role đó</case>
    </test_cases>
</step>

<step id="5" name="Generate status transition tests">
    <for_each>transition trong statusTransitions</for_each>

    <test_cases>
        <case name="valid">Valid transition: chuyển trạng thái đúng điều kiện → thành công</case>
        <case name="invalid">Invalid transition: chuyển trạng thái sai điều kiện → hiển thị thông báo lỗi</case>
        <case name="maker_checker">Maker-Checker flow: người tạo không thể tự duyệt (nếu có quy trình này)</case>
    </test_cases>
</step>

<step id="6" name="Write test cases">
    <test_case_template>
        <field name="testSuiteName">Theo context — VD: `"Kiểm tra phân quyền"`, `"Kiểm tra quy trình duyệt"`</field>
        <field name="testCaseName">Lấy TRỰC TIẾP từ mindmap bullet — hoặc tạo từ role/transition nếu không có trong mindmap</field>
        <field name="summary">Giống hệt `testCaseName`</field>
        <field name="preConditions">{preConditionsBase} (điều chỉnh role nếu cần)</field>
        <field name="step">UI actions — Click, Quan sát, Đăng nhập với role X, etc. KHÔNG viết "Send API"</field>
        <field name="expectedResult">UI state — Hiển thị, Ẩn, Enable, Disable, Redirect, Thông báo lỗi, etc. KHÔNG có HTTP status codes</field>
        <field name="importance">"High" cho security/permission tests; "Medium" cho transition tests</field>
        <field name="result">"PENDING"</field>
    </test_case_template>

    <rules>
        <rule type="result">= "PENDING"</rule>
        <rule type="expectedResult">KHÔNG có HTTP status codes</rule>
        <rule type="step">= UI actions — KHÔNG viết "Send API"</rule>
    </rules>
</step>

<step id="7" name="Write batch-workflow.json">
    <file>{OUTPUT_DIR}/batch-workflow.json</file>

    <rules>
        <rule type="first_line">DÒNG ĐẦU TIÊN phải là `[` — không có text, comment, hay markdown trước đó</rule>
        <rule type="last_line">DÒNG CUỐI CÙNG phải là `]`</rule>
        <rule type="content">KHÔNG ghi bất kỳ text nào ngoài JSON array thuần túy</rule>
    </rules>
</step>

<step id="8" name="Checkpoint (STDOUT)">
    <output>✓ batch-workflow.json written — {N} test cases ({roles} roles, {transitions} transitions covered)</output>
</step>

</workflow>

---

<context_block>

<task_context>
    <parameters>
        <param name="SKILL_SCRIPTS" type="path" required="true"/>
        <param name="TC_CONTEXT_FILE" type="path" required="true"/>
        <param name="TEST_DESIGN_FILE" type="path" required="true"/>
        <param name="INVENTORY_FILE" type="path" required="true"/>
        <param name="OUTPUT_DIR" type="path" required="true"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>

</context_block>

---

<output_specification>

<file>{OUTPUT_DIR}/batch-workflow.json</file>

<content>JSON array of workflow/role-based test cases</content>

</output_specification>
