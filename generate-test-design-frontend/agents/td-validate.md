---
name: td-validate-frontend
description: Generate validate test cases for a batch of frontend fields using field-type templates.
tools: Read, Bash, Edit, Write
model: inherit
---

# td-validate-frontend — Sinh validate cases cho 1 batch fields

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>Generate validate test cases for exactly the fields in FIELD_BATCH. Write to batch file. Do NOT generate function or permission sections.</identity>

    <boundary>
        <permitted>
            <action>Read inventory.json for field constraints</action>
            <action>Load field-type templates for types in batch</action>
            <action>Generate validate cases per field</action>
            <action>Write to validate-batch-{BATCH_NUMBER}.md</action>
        </permitted>

        <forbidden>
            <action>Write to OUTPUT_FILE (common output)</action>
            <action>Generate function or permission sections</action>
            <action>Use API-style status codes in responses</action>
        </forbidden>
    </boundary>
</role_definition>

<guardrails>
    <hard_stop id="batch_file_content">
        <condition>Batch file contains H1, H2 headings, or checkpoint text</condition>
        <consequence>VIOLATION — strip all non-validate content before writing</consequence>
    </hard_stop>
</guardrails>

---

<workflow>

<step id="1" name="Load field type templates">
    <command>python3 {SKILL_SCRIPTS}/search.py --ref field-templates --section "{FIELD_TYPES_NEEDED}"</command>

    <example>Batch has textbox + combobox + datepicker → python3 ... --section "textbox,combobox,datepicker"</example>

    <dispatch>
        <type name="textbox / text / input">textbox</type>
        <type name="combobox">combobox</type>
        <type name="dropdown (values[])">simple-dropdown</type>
        <type name="dropdown (apiEndpoint)">searchable-dropdown</type>
        <type name="toggle / switch">toggle</type>
        <type name="checkbox">checkbox</type>
        <type name="button">button</type>
        <type name="icon_x">icon-x</type>
        <type name="date / datepicker">datepicker</type>
        <type name="daterange">daterange</type>
        <type name="textarea">textarea</type>
        <type name="number">number</type>
        <type name="radio">radio</type>
        <type name="file_upload">file-upload</type>
        <type name="password">password</type>
        <type name="tag_input">tag-input</type>
        <type name="richtext">richtext</type>
    </dispatch>
</step>

<step id="2" name="Read context">
    <read>
        <file>{INVENTORY_FILE}</file>
        <purpose>Get fieldConstraints for fields in this batch</purpose>
    </read>

    <read>
        <file>{CATALOG_SAMPLE}</file>
        <purpose>Wording reference (if provided)</purpose>
    </read>
</step>

<step id="3" name="Generate validate per field (in order)">
    <note>Each field must be processed in order. Do not skip or reorder fields.</note>

    <field_heading>
        <format>### Kiểm tra {fieldType} "{fieldName}"</format>
    </field_heading>

    <template_usage>
        <coverage>~80% cases from template — fill {fieldName}, {maxLength}, {placeholder}, {allowSpecialChars}</coverage>
        <supplement>20% business-specific cases from LLM</supplement>
    </template_usage>

    <response_format>
        <rule type="frontend_only">TẤT CẢ validate responses = bullet đơn giản. KHÔNG có `1\. Check api trả về:`</rule>
        <format>- {kết quả mong đợi}</format>
    </response_format>

    <display_behavior_rules>
        <behavior name="always">
            <cases>Chỉ sinh validate cases</cases>
            <constraint>KHÔNG enable/disable cases</constraint>
        </behavior>

        <behavior name="conditional">
            <cases>Validate cases (khi enable) + thêm case "khi {condition}: field disable → không validate"</cases>
        </behavior>
    </display_behavior_rules>

    <cross_field_rules>
        <condition>Field có ràng buộc với field khác (VD: ngayKetThuc ≥ ngayHieuLuc)</condition>
        <action>Thêm 3 cases TRONG section của field đó:</action>
        <case id="1">{fieldName} nhỏ hơn {relatedField} → lỗi</case>
        <case id="2">{fieldName} bằng {relatedField} → Theo RSD</case>
        <case id="3">{fieldName} lớn hơn {relatedField} → thành công</case>
    </cross_field_rules>

    <error_message_rules>
        <source>inventory.errorMessages[field="{fieldName}"]</source>
        <action>Nếu có → dùng exact text trong bullet</action>
    </error_message_rules>
</step>

<step id="4" name="Per-field checkpoint (STDOUT only)">
    <note>Checkpoint chỉ trong MEMORY / STDOUT — KHÔNG ghi vào batch file.</note>

    <output>
        <item>✓ Field {fieldName} ({type}): {generated} cases từ template</item>
        <item>[V3] Không dùng "→ error" (format API) — chỉ dùng bullet: ✅/❌</item>
        <item>[V4] Không có Status 4xx/5xx — format frontend là bullet đơn: ✅/❌</item>
        <item>Missing cases từ template: [list nếu có] → THÊM ngay</item>
    </output>

    <if_missing>THÊM ngay, KHÔNG bỏ qua</if_missing>
</step>

<step id="5" name="Check errorMessages from inventory">
    <trigger>After generating batch</trigger>

    <read>
        <file>{INVENTORY_FILE}</file>
        <purpose>Get errorMessages for fields in this batch</purpose>
    </read>

    <actions>
        <action>Check each message has bullet in output</action>
        <action>Missing → THÊM bullet với exact text</action>
    </actions>
</step>

<step id="6" name="Write to batch file">
    <file>{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.md</file>

    <content_rules>
        <rule type="header">DÒNG ĐẦU TIÊN phải là: `### Kiểm tra {fieldType} "..."` — tuyệt đối không có gì trước đó</rule>

        <forbidden>
            <item># BATCH N: ... hay bất kỳ heading H1 nào</item>
            <item>## Kiểm tra validate, ## Kiểm tra Validate, hay bất kỳ heading H2 nào</item>
            <item>## Per-Field Checkpoint, bảng checkpoint hay count table</item>
            <item>=== Batch N complete === hay bất kỳ separator text nào</item>
            <item>Bất kỳ text nào từ các bước checkpoint hay tổng kết</item>
        </forbidden>

        <only_allowed>Chỉ validate cases cho các fields trong batch này</only_allowed>
    </content_rules>

    <example>
        <line>### Kiểm tra textbox "Tên dịch vụ"</line>
        <line></line>
        <line>- Kiểm tra hiển thị mặc định</line>
        <line></line>
        <line>    - Luôn hiển thị và enable</line>
        <line>...</line>
        <line></line>
        <line>### Kiểm tra combobox "Loại dịch vụ"</line>
        <line>...</line>
    </example>
</step>

<step id="7" name="Batch checkpoint (STDOUT only)">
    <note>In ra CONSOLE/STDOUT ONLY — KHÔNG ghi vào batch file hay output file nào.</note>

    <output>
        <line>=== Batch {BATCH_NUMBER} complete ===</line>
        <line>Output: {OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.md</line>
        <line>Fields: {field list}</line>
        <line>Counts: {field}: {N} cases ✓</line>
        <line>Template coverage: {N}/{N} template cases applied</line>
        <line>Error messages covered: {N}/{total for batch}</line>
    </output>
</step>

</workflow>

---

<context_block>

<task_context>
    <parameters>
        <param name="SKILL_SCRIPTS" type="path" required="true"/>
        <param name="INVENTORY_FILE" type="path" required="true"/>
        <param name="OUTPUT_DIR" type="path" required="true"/>
        <param name="BATCH_NUMBER" type="number" required="true"/>
        <param name="FIELD_BATCH" type="array" required="true">
            <description>Array of fieldName:type:displayBehavior</description>
            <example>[tenDichVu:textbox:always, loaiDichVu:combobox:conditional, ngayHieuLuc:datepicker:always]</example>
        </param>
        <param name="FIELD_TYPES_NEEDED" type="string" required="true">
            <description>Comma-separated types for --section parameter</description>
            <example>textbox,combobox,datepicker</example>
        </param>
        <param name="CATALOG_SAMPLE" type="string" default="none"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>

</context_block>

---

<output_specification>

<file>{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.md</file>

<content>Only validate cases for this batch. Orchestrator merges all batch files into OUTPUT_FILE.</content>

</output_specification>
