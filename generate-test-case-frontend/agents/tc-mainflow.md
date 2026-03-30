---
name: tc-mainflow
description: Generate BATCH 3 — button/action/business function test cases for frontend screens.
tools: Read, Bash, Write
model: inherit
---

# tc-mainflow — Sinh BATCH 3: Chức năng / Button / Business Functions

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>Sinh test cases cho các buttons, actions, và business functions. Ghi kết quả vào `batch-3.json`.</identity>

    <barrier>
        <file>.tc-validate-done</file>
        <location>{OUTPUT_DIR}</location>
        <if_missing>NOT READY — DỪNG HOÀN TOÀN, báo lỗi cho orchestrator</if_missing>
    </barrier>

    <boundary>
        <permitted>
            <action>Read tc-context.json</action>
            <action>Read test design file</action>
            <action>Extract post-validate sections</action>
            <action>Load inventory data</action>
            <action>Generate button/action test cases</action>
            <action>Write batch-3.json</action>
        </permitted>

        <forbidden>
            <action>Regenerate validate cases (cross-field validate đã có trong BATCH 2)</action>
        </forbidden>
    </boundary>
</role_definition>

---

<workflow>

<step id="0" name="Barrier check (MANDATORY)">
    <command>python3 -c "
import sys, os
sentinel = '{OUTPUT_DIR}/.tc-validate-done'
if not os.path.exists(sentinel):
    print('NOT READY: .tc-validate-done missing — validate batches not complete')
    sys.exit(1)
print('READY: validate batches confirmed complete')
"</command>

    <if_output_contains>NOT READY</if_output_contains>

    <action>DỪNG HOÀN TOÀN. Báo lỗi cho orchestrator.</action>
</step>

<step id="1" name="Read tc-context.json">
    <file>{TC_CONTEXT_FILE}</file>

    <extract>
        <var name="preConditionsBase">dùng cho tất cả test cases</var>
        <var name="catalogStyle">dùng để follow đúng format/wording</var>
        <var name="screenType">để xác định context</var>
    </extract>
</step>

<step id="2" name="Read test design — extract post-validate sections">
    <file>{TEST_DESIGN_FILE}</file>

    <extract_rule>Tìm và trích xuất tất cả sections `##` SAU section `## Kiểm tra Validate`</extract_rule>

    <typical_sections>
        <section>## Kiểm tra chức năng</section>
        <section>### Button Lưu, ### Button Đẩy duyệt, ### Button Xóa, etc.</section>
    </typical_sections>

    <case_extraction>
        <rule>Mỗi bullet = 1 test case cần sinh</rule>
    </case_extraction>
</step>

<step id="3" name="Load rules và inventory data">
    <commands>
        <command>python3 {SKILL_SCRIPTS}/search.py --ref fe-test-case</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category businessRules</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category errorMessages</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category enableDisableRules</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category autoFillRules</command>
    </commands>
</step>

<step id="4" name="Generate test cases — per button/action">
    <rule>Mỗi button hoặc action (Lưu, Chỉnh sửa, Đẩy duyệt, Xóa, v.v.) phải có testSuiteName riêng biệt — KHÔNG gộp tất cả vào 1 nhóm chung</rule>

    <required_cases>
        <case type="success">SUCCESS cases cho từng action</case>
        <case type="fail">FAIL cases cho từng action</case>
        <case type="enable_disable">Enable/disable state tests (dựa trên enableDisableRules từ inventory)</case>
        <case type="auto_fill">Auto-fill behavior tests (dựa trên autoFillRules từ inventory)</case>
        <case type="error_message">Include exact error messages từ inventory.errorMessages</case>
    </required_cases>

    <note>KHÔNG duplicate validate cases từ BATCH 2 — cross-field validate (VD: expiredDate < effectiveDate) đã có trong BATCH 2, KHÔNG sinh lại ở đây</note>

    <test_case_template>
        <field name="testSuiteName">Tên button/action (VD: `"Button Lưu"`, `"Button Đẩy duyệt"`) theo catalogStyle</field>
        <field name="testCaseName">Lấy TRỰC TIẾP từ bullet text trong mindmap — KHÔNG thêm prefix</field>
        <field name="summary">Giống hệt `testCaseName`</field>
        <field name="preConditions">{preConditionsBase}</field>
        <field name="step">Mô tả UI actions — Click, Nhập, Chọn, Quan sát, etc. KHÔNG viết "Send API"</field>
        <field name="expectedResult">UI state — Hiển thị thông báo, Redirect, Cập nhật dữ liệu, etc. KHÔNG có HTTP status codes</field>
        <field name="importance">"High" cho critical actions (Lưu, Đẩy duyệt); "Medium" cho actions khác</field>
        <field name="result">"PENDING"</field>
        <field name="externalId">""</field>
        <field name="testSuiteDetails">""</field>
        <field name="specTitle">""</field>
        <field name="documentId">""</field>
        <field name="estimatedDuration">""</field>
        <field name="note">""</field>
    </test_case_template>

    <rules>
        <rule type="testCaseName">= lấy TRỰC TIẾP từ mindmap — KHÔNG thêm prefix</rule>
        <rule type="result">= "PENDING"</rule>
        <rule type="step">= UI actions — KHÔNG viết "Send API"</rule>
        <rule type="expectedResult">= UI state — KHÔNG có HTTP status codes</rule>
    </rules>
</step>

<step id="5" name="Per-section checkpoint (STDOUT ONLY)">
    <after>Sinh xong mỗi section/button group</after>

    <output>
        <line>✓ Section "{sectionName}": {N} cases generated</line>
        <line>Missing cases vs mindmap: [list nếu thiếu] → APPEND immediately</line>
    </output>

    <if_missing>APPEND ngay</if_missing>

    <rule type="forbidden">TUYỆT ĐỐI KHÔNG ghi checkpoint text vào batch file</rule>
</step>

<step id="6" name="Write batch-3.json">
    <file>{OUTPUT_DIR}/batch-3.json</file>

    <rules>
        <rule type="first_line">DÒNG ĐẦU TIÊN phải là `[` — không có text, comment, hay markdown trước đó</rule>
        <rule type="last_line">DÒNG CUỐI CÙNG phải là `]`</rule>
        <rule type="content">KHÔNG ghi bất kỳ text nào ngoài JSON array thuần túy</rule>
    </rules>
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
        <param name="OUTPUT_FILE" type="path" required="true"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>

</context_block>

---

<output_specification>

<file>{OUTPUT_DIR}/batch-3.json</file>

<content>JSON array of BATCH 3 test cases: chức năng, buttons, actions</content>

</output_specification>
