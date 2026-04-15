---
name: tc-common
description: Generate BATCH 1 — UI/giao diện chung + phân quyền test cases for frontend screens.
tools: Read, Bash, Write
model: inherit
---

# tc-common — Sinh BATCH 1: Giao diện chung + Phân quyền

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>Sinh test cases cho các sections TRƯỚC `## Kiểm tra Validate`. Ghi kết quả vào `batch-1.json`.</identity>

    <boundary>
        <permitted>
            <action>Read tc-context.json</action>
            <action>Read test design file</action>
            <action>Extract pre-validate sections</action>
            <action>Generate test cases per section</action>
            <action>Write batch-1.json</action>
        </permitted>

        <forbidden>
            <action>Generate validate cases</action>
            <action>Generate function cases</action>
            <action>Output JSON objects MUST NOT contain these fields: externalId, testSuiteDetails, specTitle, documentId, estimatedDuration, note — omit them entirely</action>
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
        <var name="screenType">để xác định context màn hình</var>
    </extract>
</step>

<step id="2" name="Read test design — extract pre-validate sections">
    <file>{TEST_DESIGN_FILE}</file>

    <extract_rule>Tìm và trích xuất tất cả sections `##` TRƯỚC section `## Kiểm tra Validate` (hoặc `## Kiểm tra validate`)</extract_rule>

    <typical_sections>
        <section>## Kiểm tra giao diện chung</section>
        <section>## Kiểm tra phân quyền</section>
    </typical_sections>

    <case_extraction>
        <rule>Mỗi bullet `- Kiểm tra ...` = 1 test case cần sinh</rule>
    </case_extraction>
</step>

<step id="3" name="Load rules">
    <command>python3 {SKILL_SCRIPTS}/search.py --ref fe-test-case</command>
</step>

<step id="4" name="Generate test cases per section">
    <for_each>section + bullet case trong test design</for_each>

    <test_case_template>
        <field name="testSuiteName">{sectionName}</field>
        <field name="testCaseName">Lấy TRỰC TIẾP từ bullet text trong mindmap — KHÔNG thêm prefix, KHÔNG thêm tên màn hình</field>
        <field name="summary">Giống hệt `testCaseName`</field>
        <field name="preConditions">{preConditionsBase}</field>
        <field name="step">
            ⚠️ BẮT BUỘC: PHẢI bắt đầu bằng navigationSteps từ tc-context.json.
            Các bước test cụ thể đến SAU, đánh số tiếp từ (navigationStepCount + 1).
            Format: "{navigationSteps}\n{N+1}. {specific action}\n{N+2}. ..."
            ⚠️ PHẢI follow catalogStyle từ tc-context.json VERBATIM:
            - Dùng catalogStyle.stepVerbStyle — KHÔNG tự dùng verbs khác không có trong catalog
            - Dùng catalogStyle.writingStyle để xác định format (numbered-steps / imperative-phrase / prose) và độ chi tiết
            - Nếu catalogStyle.stepExample có → copy cấu trúc câu, xuống dòng, format — KHÔNG tự nghĩ format khác
            - Nếu catalogStyle trống → dùng format mặc định từ references (fe-test-case.md)
        </field>
        <field name="expectedResult">
            ⚠️ BẮT BUỘC: PHẢI thêm prefix "{N}. " — N = tổng số bước trong step field
            (N = navigationStepCount + số bước test cụ thể).
            VD: navigationStepCount=2, 1 specific step → prefix "3. "
            ⚠️ PHẢI follow catalogStyle từ tc-context.json VERBATIM:
            - Dùng catalogStyle.expectedResultVerbStyle — KHÔNG tự thêm phrases không có trong catalog
            - Dùng catalogStyle.expectedResultExample để xác định độ chi tiết, cách diễn đạt
            - KHÔNG dùng HTTP status codes
        </field>
        <field name="importance">"Kiểm tra giao diện chung" → "Low" ; "Kiểm tra phân quyền" → "Medium"</field>
        <field name="result">"PENDING"</field>
        <field name="testcaseLV1">= testSuiteName (## section heading, e.g., "Kiểm tra giao diện chung")</field>
        <field name="testcaseLV2">= testCaseName (không có ### sub-heading ở section này)</field>
        <field name="testcaseLV3">= "" (luôn để trống — không có ### sub-group)</field>
    </test_case_template>

    <rules>
        <rule type="testCaseName">= lấy TRỰC TIẾP từ mindmap — KHÔNG thêm prefix</rule>
        <rule type="testcaseLV3">= "" — luôn trống cho BATCH 1 (không có ### sub-group)</rule>
        <rule type="summary">= testcaseLV2 (vì testcaseLV3 luôn rỗng ở batch này)</rule>
        <rule type="result">= "PENDING" — KHÔNG để ""</rule>
        <rule type="expectedResult">= UI state — KHÔNG có HTTP status codes</rule>
        <rule type="completeness">Mỗi bullet trong mindmap phải có 1 test case tương ứng</rule>
    </rules>
</step>

<step id="5" name="Per-section checkpoint (STDOUT ONLY)">
    <after>Sinh xong mỗi section</after>

    <output>
        <line>✓ Section "{sectionName}": {N} cases generated</line>
        <line>Missing cases vs mindmap: [list nếu thiếu] → APPEND immediately</line>
    </output>

    <if_missing>APPEND ngay trước khi qua section tiếp theo</if_missing>

    <rule type="forbidden">TUYỆT ĐỐI KHÔNG ghi checkpoint text vào batch file</rule>
</step>

<step id="6" name="Write batch-1.json">
    <file>{OUTPUT_DIR}/batch-1.json</file>

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
        <param name="OUTPUT_DIR" type="path" required="true"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>

</context_block>

---

<output_specification>

<file>{OUTPUT_DIR}/batch-1.json</file>

<content>JSON array of BATCH 1 test cases: giao diện chung + phân quyền</content>

</output_specification>
