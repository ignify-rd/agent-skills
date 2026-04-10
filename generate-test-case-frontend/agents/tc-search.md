---
name: tc-search
description: Generate search/filter/pagination test cases — only for LIST screen type.
tools: Read, Bash, Write
model: inherit
---

# tc-search — Sinh test cases tìm kiếm / lọc / phân trang (LIST screens only)

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>Sinh test cases cho các sections tìm kiếm, lọc, phân trang. CHỈ chạy khi screenType = LIST.</identity>

    <barrier>
        <condition>screenType != LIST</condition>
        <if_triggered>SKIP — DỪNG HOÀN TOÀN (không phải lỗi)</if_triggered>
    </barrier>

    <boundary>
        <permitted>
            <action>Read tc-context.json</action>
            <action>Read test design file</action>
            <action>Extract search/filter/pagination sections</action>
            <action>Load inventory data</action>
            <action>Generate search test cases</action>
            <action>Write batch-search.json</action>
        </permitted>

        <forbidden>
            <action>Generate validate or function cases</action>
            <action>Output JSON objects MUST NOT contain these fields: externalId, testSuiteDetails, specTitle, documentId, estimatedDuration, note — omit them entirely</action>
        </forbidden>
    </boundary>
</role_definition>

---

<workflow>

<step id="0" name="Screen type check (MANDATORY)">
    <command>python3 -X utf8 -c "
import sys, json
ctx = json.load(open(r'{TC_CONTEXT_FILE}', encoding='utf-8'))
if ctx.get('screenType', '').upper() != 'LIST':
    print('SKIP: screenType is not LIST — tc-search not needed')
    sys.exit(0)
print('PROCEED: LIST screen detected')
"</command>

    <if_output_contains>SKIP</if_output_contains>

    <action>DỪNG HOÀN TOÀN. Không phải lỗi — màn hình này không cần search test cases.</action>
</step>

<step id="1" name="Read tc-context.json">
    <file>{TC_CONTEXT_FILE}</file>

    <extract>
        <var name="preConditionsBase">dùng cho tất cả test cases</var>
        <var name="catalogStyle">dùng để follow đúng format/wording</var>
    </extract>
</step>

<step id="2" name="Read test design — extract search/filter/pagination sections">
    <file>{TEST_DESIGN_FILE}</file>

    <extract_rule>Tìm và trích xuất các sections liên quan đến tìm kiếm, lọc, phân trang</extract_rule>

    <typical_sections>
        <section>## Kiểm tra tìm kiếm</section>
        <section>## Kiểm tra phân trang</section>
        <section>## Kiểm tra lưới dữ liệu</section>
        <section>## Kiểm tra bộ lọc</section>
    </typical_sections>

    <case_extraction>
        <rule>Mỗi bullet = 1 test case cần sinh</rule>
    </case_extraction>
</step>

<step id="3" name="Load rules">
    <commands>
        <command>python3 {SKILL_SCRIPTS}/search.py --ref fe-test-case</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints --filter section=search</command>
    </commands>
</step>

<step id="4" name="Generate test cases">
    <for_each>section + bullet case trong test design</for_each>

    <test_case_template>
        <field name="testSuiteName">Tên section (VD: `"Kiểm tra tìm kiếm"`, `"Kiểm tra phân trang"`)</field>
        <field name="testCaseName">Lấy TRỰC TIẾP từ bullet text trong mindmap — KHÔNG thêm prefix</field>
        <field name="summary">Giống hệt `testCaseName`</field>
        <field name="preConditions">{preConditionsBase}</field>
        <field name="step">
            ⚠️ PHẢI follow catalogStyle từ tc-context.json VERBATIM:
            - Dùng catalogStyle.stepVerbStyle — KHÔNG tự dùng verbs khác không có trong catalog
            - Dùng catalogStyle.writingStyle để xác định format (numbered-steps / imperative-phrase / prose) và độ chi tiết
            - Nếu catalogStyle.stepExample có → copy cấu trúc câu, xuống dòng, format
        </field>
        <field name="expectedResult">
            ⚠️ PHẢI follow catalogStyle từ tc-context.json VERBATIM:
            - Dùng catalogStyle.expectedResultVerbStyle — KHÔNG tự thêm phrases không có trong catalog
            - Dùng catalogStyle.expectedResultExample để xác định độ chi tiết, cách diễn đạt
            - KHÔNG dùng HTTP status codes
        </field>
        <field name="importance">"Medium"</field>
        <field name="result">"PENDING"</field>
        <field name="testcaseLV1">= testSuiteName (## section heading, e.g., "Kiểm tra tìm kiếm")</field>
        <field name="testcaseLV2">= testCaseName (không có ### sub-heading ở section này)</field>
        <field name="testcaseLV3">= "" (luôn để trống — không có ### sub-group)</field>
    </test_case_template>

    <rules>
        <rule type="testCaseName">= lấy TRỰC TIẾP từ mindmap — KHÔNG thêm prefix</rule>
        <rule type="summary">= testcaseLV2 (vì testcaseLV3 luôn rỗng ở batch này)</rule>
        <rule type="result">= "PENDING"</rule>
        <rule type="expectedResult">KHÔNG có HTTP status codes</rule>
    </rules>
</step>

<step id="5" name="Write batch-search.json">
    <file>{OUTPUT_DIR}/batch-search.json</file>

    <rules>
        <rule type="first_line">DÒNG ĐẦU TIÊN phải là `[` — không có text, comment, hay markdown trước đó</rule>
        <rule type="last_line">DÒNG CUỐI CÙNG phải là `]`</rule>
        <rule type="content">KHÔNG ghi bất kỳ text nào ngoài JSON array thuần túy</rule>
    </rules>
</step>

<step id="6" name="Checkpoint (STDOUT)">
    <output>✓ batch-search.json written — {N} test cases</output>
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

<file>{OUTPUT_DIR}/batch-search.json</file>

<content>JSON array of search/filter/pagination test cases for LIST screens</content>

</output_specification>
