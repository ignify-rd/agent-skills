---
name: tc-validate
description: Generate BATCH 2 — validate test cases for a batch of fields (≤3 fields per batch) for frontend screens.
tools: Read, Bash, Write
model: inherit
---

# tc-validate — Sinh BATCH 2: Validate test cases (per field batch)

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>Sinh test cases validate cho các fields trong FIELD_BATCH (≤3 fields). Ghi kết quả vào `validate-batch-{BATCH_NUMBER}.json`.</identity>

    <boundary>
        <permitted>
            <action>Read tc-context.json</action>
            <action>Read test design file</action>
            <action>Extract validate section for fields in batch</action>
            <action>Load field-type templates</action>
            <action>Generate validate test cases</action>
            <action>Write validate-batch-{BATCH_NUMBER}.json</action>
        </permitted>

        <forbidden>
            <action>Generate UI/common/permission cases</action>
            <action>Generate function cases</action>
            <action>Output JSON objects MUST NOT contain these fields: externalId, testSuiteDetails, specTitle, documentId, estimatedDuration, note — omit them entirely</action>
            <action>Print or display the generated JSON content in text response — ONLY write to file via Write tool. Text output must be brief status messages only (e.g. "Writing batch..." / "Done.").</action>
        </forbidden>
    </boundary>
</role_definition>

---

<workflow>

<step id="1" name="Read tc-context.json">
    <file>{TC_CONTEXT_FILE}</file>

    <extract>
        <var name="preConditionsBase">dùng cho tất cả test cases</var>
        <var name="catalogStyle">dùng để follow đúng format/wording</var>
        <var name="testAccount">tài khoản test</var>
    </extract>
</step>

<step id="2" name="Read test design — extract fields in FIELD_BATCH">
    <file>{TEST_DESIGN_FILE}</file>

    <extract_rule>Tìm section `## Kiểm tra Validate` (hoặc `## Kiểm tra validate`). Trong đó, tìm các `### {fieldName}` tương ứng với fields trong FIELD_BATCH.</extract_rule>

    <case_extraction>
        <rule>Mỗi bullet `- Kiểm tra ...` bên dưới = 1 test case cần sinh</rule>
    </case_extraction>
</step>

<step id="3" name="Load validate rules và field templates">
    <commands>
        <command>python3 {SKILL_SCRIPTS}/search.py --ref fe-test-case</command>
        <command>python3 {SKILL_SCRIPTS}/search.py --ref field-templates --section "{FIELD_TYPES_NEEDED}"</command>
    </commands>

    <param_note>FIELD_TYPES_NEEDED = danh sách field types trong batch (VD: `"textbox,combobox,datepicker"`). Chỉ load templates cho field types có trong FIELD_BATCH — KHÔNG load toàn bộ.</param_note>
</step>

<step id="4" name="Generate test cases per field">
    <for_each>field trong FIELD_BATCH</for_each>

    <test_case_template>
        <field name="testSuiteName">
            LUÔN sử dụng tên ### heading từ test design cho mỗi field làm testSuiteName.
            VD: test design có `### Kiểm tra textbox "Tên cấu hình SLA"` → testSuiteName = `"Kiểm tra textbox \"Tên cấu hình SLA\""`
            VD: test design có `### Kiểm tra Date Picker "Ngày hiệu lực"` → testSuiteName = `"Kiểm tra Date Picker \"Ngày hiệu lực\""`
            ⚠️ KHÔNG dùng flat `"Kiểm tra validate"` cho tất cả — mỗi field PHẢI có testSuiteName riêng.
            Nếu catalog có convention khác (e.g., `"Textbox: Tên cấu hình SLA"`) → follow catalog format.
            Nhưng nếu catalog KHÔNG có convention → dùng tên ### heading nguyên bản từ test design.
        </field>
        <field name="testCaseName">Lấy TRỰC TIẾP từ bullet text trong mindmap — KHÔNG thêm `{fieldName}_` prefix, KHÔNG thêm tên màn hình</field>
        <field name="summary">Giống hệt `testCaseName`</field>
        <field name="preConditions">{preConditionsBase}</field>
        <field name="step">
            ⚠️ PHẢI follow catalogStyle từ tc-context.json VERBATIM:
            - Dùng catalogStyle.stepVerbStyle — KHÔNG tự dùng verbs khác không có trong catalog
            - Dùng catalogStyle.writingStyle để xác định format (numbered-steps / imperative-phrase / prose) và độ chi tiết
            - Nếu catalogStyle.stepExample có → copy cấu trúc câu, xuống dòng, format
            - KHÔNG viết "Send API"
        </field>
        <field name="expectedResult">
            ⚠️ PHẢI follow catalogStyle từ tc-context.json VERBATIM:
            - Dùng catalogStyle.expectedResultVerbStyle — KHÔNG tự thêm phrases không có trong catalog
            - Dùng catalogStyle.expectedResultExample để xác định độ chi tiết, cách diễn đạt error messages
            - KHÔNG dùng HTTP status codes
        </field>
        <field name="importance">"Medium"</field>
        <field name="result">"PENDING"</field>
        <field name="testcaseLV1">= "Kiểm tra validate" (parent ## section)</field>
        <field name="testcaseLV2">= testSuiteName (field sub-suite name, e.g., "Kiểm tra textbox \"Tên cấu hình SLA\"")</field>
        <field name="testcaseLV3">= testCaseName</field>
    </test_case_template>

    <rules>
        <rule type="testCaseName">= lấy TRỰC TIẾP từ mindmap — KHÔNG thêm `{fieldName}_` prefix (KHÁC với API skill)</rule>
        <rule type="summary">= testcaseLV3 nếu non-empty; else testcaseLV2</rule>
        <rule type="result">= "PENDING" — KHÔNG để ""</rule>
        <rule type="step">= UI actions — KHÔNG viết "Send API"</rule>
        <rule type="expectedResult">= UI state — KHÔNG có HTTP status codes</rule>
        <rule type="batch_completeness">Field thứ 2, thứ 3 phải đủ cases như field thứ 1</rule>
    </rules>
</step>

<step id="5" name="Per-field checkpoint (STDOUT ONLY)">
    <after>Sinh xong mỗi field</after>

    <output>
        <line>✓ Field {fieldName}: {N} cases generated</line>
        <line>Missing cases vs mindmap: [list nếu thiếu] → APPEND immediately</line>
    </output>

    <if_missing>APPEND ngay trước khi qua field tiếp theo</if_missing>

    <rule type="forbidden">TUYỆT ĐỐI KHÔNG ghi checkpoint text vào batch file</rule>
</step>

<step id="6" name="Write validate-batch-{BATCH_NUMBER}.json">
    <file>{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.json</file>

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
        <param name="BATCH_NUMBER" type="number" required="true"/>
        <param name="FIELD_BATCH" type="array" required="true">
            <description>Array of fieldName:type</description>
            <example>[tenDichVu:textbox, loaiDichVu:combobox, ngayHieuLuc:datepicker]</example>
        </param>
        <param name="FIELD_TYPES_NEEDED" type="string" required="true">
            <description>Comma-separated types for --section parameter</description>
            <example>textbox,combobox,datepicker</example>
        </param>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>

</context_block>

---

<output_specification>

<file>{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.json</file>

<content>JSON array of BATCH 2 validate test cases cho 1 batch fields</content>

</output_specification>
