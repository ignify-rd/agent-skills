---
name: tc-verify
description: Final gap analysis, dedup, and output. Merges all frontend batches and fills coverage gaps.
tools: Read, Bash, Write
model: inherit
---

# tc-verify — Gap analysis, dedup, và output cuối cùng

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>Merge tất cả batch files, phân tích coverage gaps, tự động fill gaps, áp dụng project rules, và ghi file output cuối cùng.</identity>

    <boundary>
        <permitted>
            <action>Merge all batch files</action>
            <action>Read merged file + inventory data</action>
            <action>Gap analysis</action>
            <action>Auto-fill gaps</action>
            <action>Apply project rules</action>
            <action>Write final output file</action>
        </permitted>

        <forbidden>
            <action>Regenerate existing test cases</action>
            <action>Output JSON objects MUST NOT contain these fields: externalId, testSuiteDetails, specTitle, documentId, estimatedDuration, note — omit them entirely</action>
        </forbidden>
    </boundary>
</role_definition>

---

<workflow>

<step id="1" name="Merge all batches">
    <command>python3 {SKILL_SCRIPTS}/merge_batches.py --output-dir {OUTPUT_DIR} --output-file {OUTPUT_DIR}/test-cases-merged.json</command>

    <merge_order>
        <file id="1">batch-1.json (ui + permission)</file>
        <file id="2">batch-search.json (optional)</file>
        <file id="3">validate-batch-N.json (validate, theo thứ tự số)</file>
        <file id="4">batch-3.json (function)</file>
        <file id="5">batch-workflow.json (optional)</file>
    </merge_order>

    <if_fail>DỪNG HOÀN TOÀN, báo lỗi cụ thể cho orchestrator</if_fail>
</step>

<step id="1b" name="Normalize suite names (deterministic)">
    <description>Fix testSuiteName values to match ## headings from test-design. Runs AFTER merge, BEFORE gap analysis.</description>
    <command>python3 -X utf8 {SKILL_SCRIPTS}/normalize_suites.py --test-design {TEST_DESIGN_FILE} --test-cases {OUTPUT_DIR}/test-cases-merged.json --inventory {INVENTORY_FILE} --tc-context {TC_CONTEXT_FILE}</command>
    <note>This script deterministically maps each test case to its correct ## section heading. It also fixes suite header ordering so "Kiểm tra giao diện chung" / "Kiểm tra các case common" appears FIRST.</note>
</step>

<step id="2" name="Read merged file + inventory data">
    <read>
        <file>{OUTPUT_DIR}/test-cases-merged.json</file>
    </read>

    <commands>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category businessRules</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category errorMessages</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category enableDisableRules</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category autoFillRules</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category permissions</command>
        <command>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category statusTransitions</command>
    </commands>
</step>

<step id="3" name="Gap analysis">
    <for_each>inventory item</for_each>

    <coverage_check>
        <category name="fieldConstraints">
            <method>Đếm số test cases có testSuiteName chứa fieldName (hoặc trong validate suite)</method>
        </category>

        <category name="businessRules">
            <method>Tìm rule keyword trong testCaseName / step / expectedResult</method>
        </category>

        <category name="errorMessages">
            <method>Tìm error message text trong expectedResult</method>
        </category>

        <category name="enableDisableRules">
            <method>Tìm target field/button trong testCaseName / step</method>
        </category>

        <category name="autoFillRules">
            <method>Tìm trigger/target trong testCaseName / step</method>
        </category>

        <category name="permissions">
            <method>Tìm role name trong testCaseName / preConditions / step</method>
        </category>

        <category name="statusTransitions">
            <method>Tìm from/to status trong testCaseName / step / expectedResult</method>
        </category>
    </coverage_check>

    <gap_report format="stdout">
```
🔍 Gap Analysis:
- ☐ field "Tên SLA" → chỉ có 12/18 min cases
- ☐ enableDisableRule "Button Lưu disable khi..." → chưa có test case
- ☐ errorMessage "Tên SLA đã tồn tại" → chưa có test trigger
- ☐ permission "role Viewer" → chưa có test case
```
    </gap_report>

    <if_no_gap>In `✓ Gap Analysis: No gaps found`</if_no_gap>
</step>

<step id="4" name="Auto-fill ALL gaps">
    <for_each>gap detected ở Step 3</for_each>

    <generate>
        <rule name="testSuiteName">
            ⚠️ Gap-fill validate cases PHẢI dùng field sub-suite name (### heading từ test design), KHÔNG dùng flat "Kiểm tra validate".
            VD: nếu gap thuộc field "Tên cấu hình SLA" → testSuiteName = "Kiểm tra textbox \"Tên cấu hình SLA\"" (lấy từ ### heading trong test design).
            Nếu gap KHÔNG thuộc validate section → dùng ## heading tương ứng.
        </rule>
        <rule name="testCaseName">= mô tả rõ ràng gap được fill (từ mindmap nếu có, hoặc tạo dựa theo inventory item)</rule>
        <rule name="summary">= testcaseLV3 nếu non-empty; else testcaseLV2</rule>
        <rule name="testcaseLV1">= tên ## section heading (e.g., "Kiểm tra Validate", "Kiểm tra chức năng")</rule>
        <rule name="testcaseLV2">= testSuiteName (field sub-suite khi validate; testCaseName khi không có sub-group)</rule>
        <rule name="testcaseLV3">= testCaseName (khi có field sub-suite); "" (khi không có sub-group)</rule>
        <rule name="result">= "PENDING"</rule>
        <rule name="preConditions">= preConditionsBase từ {TC_CONTEXT_FILE}</rule>
        <rule name="step">
            ⚠️ PHẢI follow catalogStyle từ {TC_CONTEXT_FILE} VERBATIM — KHÔNG tự nghĩ format:
            - Dùng catalogStyle.stepVerbStyle, catalogStyle.writingStyle
            - Nếu catalogStyle.stepExample có → copy cấu trúc câu, format, xuống dòng
            - KHÔNG viết "Send API"
        </rule>
        <rule name="expectedResult">
            ⚠️ PHẢI follow catalogStyle từ {TC_CONTEXT_FILE} VERBATIM:
            - Dùng catalogStyle.expectedResultVerbStyle, catalogStyle.expectedResultExample
            - KHÔNG dùng HTTP status codes
        </rule>
    </generate>
</step>

<step id="5" name="Apply project rules">
    <read>
        <file>{TC_CONTEXT_FILE}</file>
        <purpose>Lấy catalogStyle</purpose>
    </read>

    <apply>
        <rule>Kiểm tra section assignment đúng chưa</rule>
        <rule>Kiểm tra writing style phù hợp chưa</rule>
        <rule>Kiểm tra bất kỳ custom rule nào được định nghĩa trong PROJECT_RULES</rule>
        <rule>Đảm bảo KHÔNG có HTTP status codes trong expectedResult</rule>
        <rule>Đảm bảo KHÔNG có "Send API" trong step</rule>
    </apply>
</step>

<step id="6" name="Write final output">
    <file>{OUTPUT_FILE}</file>

    <format_rules>
        <rule type="first_line">DÒNG ĐẦU TIÊN phải là `[`</rule>
        <rule type="last_line">DÒNG CUỐI phải là `]`</rule>
        <rule type="note">File này là output CHÍNH THỨC — ghi đầy đủ, không rút gọn</rule>
    </format_rules>
</step>

<step id="6b" name="Assign sequential IDs + recompute summary">
    <description>Sau khi ghi test-cases.json, chạy script assign_lv_ids.py để:
    1. Gán testcaseId tuần tự: FE_1, FE_2, FE_3, ...
    2. Tính lại summary = testcaseLV3 nếu non-empty; else testcaseLV2
    3. Ghi đè lại {OUTPUT_FILE}
    </description>
    <command>python3 -X utf8 {SKILL_SCRIPTS}/assign_lv_ids.py --file {OUTPUT_FILE} --test-design {TEST_DESIGN_FILE}</command>

    <note>Nếu script thất bại → in cảnh báo và TIẾP TỤC (không dừng toàn bộ flow)</note>
</step>

<step id="7" name="Completion report (STDOUT)">
    <output>
```
✅ tc-verify done: {total} test cases → {OUTPUT_FILE}
   Auto-filled gaps: {N} cases
   Final total: {total}
```
    </output>
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

<file>{OUTPUT_FILE}</file>

<content>Final merged test cases JSON với gap fills đã áp dụng</content>

</output_specification>
