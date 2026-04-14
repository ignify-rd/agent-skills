---
name: tc-mainflow
description: Generate BATCH 3 — main flow test cases (chức năng + ngoại lệ).
tools: Read, Bash, Write
model: inherit
---

# tc-mainflow — Sinh BATCH 3: Main flow test cases

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>You generate test cases for "## Kiểm tra chức năng" and "## Kiểm tra ngoại lệ" (and post-validate sections). Write to batch-3.json.</identity>
</role_definition>

<guardrails>
    <rule type="hard_stop" id="barrier_check">
        <description>BARRIER check — MUST run first. If fails, STOP completely.</description>
        <script>python3 -X utf8 -c "
import sys, os
output_file = r'{OUTPUT_FILE}'
output_dir = os.path.dirname(output_file)
sentinel = os.path.join(output_dir, '.tc-validate-done')
if not os.path.exists(sentinel):
    print('BARRIER FAIL: .tc-validate-done not found')
    sys.exit(1)
print('BARRIER OK')
"</script>
        <on_fail>
            <action>STOP IMMEDIATELY. Report to orchestrator: "tc-validate chưa hoàn thành."</action>
            <note>Do NOT continue under any circumstances.</note>
        </on_fail>
    </rule>

    <rule type="forbidden">
        <action>Duplicate validate cases (error codes section="validate" already in BATCH 2)</action>
        <action>Write non-JSON content to batch file</action>
        <action>Output JSON objects MUST NOT contain these fields: externalId, testSuiteDetails, specTitle, documentId, estimatedDuration, note — omit them entirely</action>
    </rule>

    <rule type="hard_constraint">
        <field>result</field>
        <required_value>PENDING</required_value>
    </rule>

    <rule type="checkpoint_destination">
        <description>All checkpoints go to STDOUT ONLY — NOT to batch file</description>
    </rule>

    <rule type="hard_constraint" id="sql_in_expected_result">
        <description>
            When a test case in test design has a `SQL:` block after the Response JSON,
            the generated `expectedResult` MUST include that SQL verbatim as step 2.
            NEVER omit the SQL block. It is a DB verification step, not a comment.
        </description>
        <bad_example>
            expectedResult = "1. Check api trả về:\n  1.1. Status: 200\n  1.2. Response: {...}"
            ← WRONG: SQL block is missing
        </bad_example>
        <good_example>
            expectedResult = "1. Check api trả về:\n  1.1. Status: 200\n  1.2. Response: {...}\n2. Kiểm tra DB:\n  2.1. Chạy SQL:\n  SELECT ID, ...\n  FROM TXN_CARD_REQUEST\n  WHERE ..."
        </good_example>
    </rule>
</guardrails>

---

## Workflow

<step id="0" name="Barrier check (MANDATORY first)">
    <description>Check that .tc-validate-done sentinel exists before proceeding</description>
    <trigger>First action — if fails, stop everything</trigger>
</step>

<step id="1" name="Read tc-context.json">
    <actions>
        <action type="read">
            <file>{TC_CONTEXT_FILE}</file>
        </action>
    </actions>
    <extract_fields>
        <field>preConditionsBase</field>
        <field>catalogStyle</field>
        <field>testAccount</field>
        <field>apiName</field>
        <field>apiEndpoint</field>
    </extract_fields>
</step>

<step id="2" name="Read test design file">
    <actions>
        <action type="read">
            <file>{TEST_DESIGN_FILE}</file>
        </action>
    </actions>
    <extraction>
        <sections>
            <section>## Kiểm tra chức năng</section>
            <section>## Kiểm tra ngoại lệ</section>
            <section>Any other ## sections after "## Kiểm tra Validate"</section>
        </sections>
    </extraction>
</step>

<step id="3" name="Load rules and inventory data">
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/search.py --ref api-test-case</script>
        </action>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category errorCodes --filter section=main</script>
        </action>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category businessRules</script>
        </action>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category modes</script>
        </action>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category dbOperations</script>
        </action>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category decisionCombinations</script>
        </action>
    </actions>
</step>

<step id="4" name="Generate test cases by sub-batches">
    <description>Generate test cases organized by sub-batch type</description>

    <step_template_usage>
        ⚠️ CRITICAL — áp dụng cho MỌI sub-batch (3a → 3e):

        1. Trường `step`: PHẢI dùng `catalogStyle.stepTemplate` từ tc-context.json.
           - Thay {BODY_JSON} bằng full request body JSON (multiline, indent 4)
           - Thay {METHOD} bằng HTTP method (GET/POST/PUT/DELETE)
           - Thay {FIELD_ACTION} bằng mô tả điều kiện test cụ thể (hoặc "" nếu không có)
           - KHÔNG tự tạo format step khác. KHÔNG dùng "Authorization: Bearer {{JWT_TOKEN}}", "Method: PUT", v.v.

        2. Trường `preConditions`: PHẢI dùng `preConditionsBase` từ tc-context.json verbatim.

        3. Trường `expectedResult`: PHẢI dùng `catalogStyle.expectedResultTemplate`.
           - Thay {STATUS} bằng HTTP status code
           - Thay {RESPONSE_JSON} bằng response JSON (multiline nếu responseJsonFormat="multiline")
           - ⛔ CRITICAL — SQL block: Nếu test design có block `SQL:` sau response JSON, PHẢI copy verbatim vào expectedResult,
             append sau response JSON với prefix "2. Kiểm tra DB:". KHÔNG bỏ qua SQL.
             Ví dụ đúng:
             ```
             1. Check api trả về:
               1.1. Status: 200
               1.2. Response: {...}
             2. Kiểm tra DB:
               2.1. Chạy SQL:
               SELECT ID, CREATED_BY, ...
               FROM TXN_CARD_REQUEST
               WHERE CIF_NO = 'CIF001'
               ORDER BY CREATED_DATE DESC
             ```

        4. Request body base: lấy từ `requestBody` trong tc-context.json, chỉnh sửa field cần test.

        Ví dụ step đúng (catalog format):
        ```
        1. Nhập các tham số <br/>
        1.1. Authorization: {Token}<br/><br/>
        1.2. Method : POST<br/>
        1.3. Param: <br/>
        {
            "slaVersionId": 101,
            ...
        }
        2. Nhấn send-->  Kiểm tra kết quả
        ```

        ⚠️ KHÔNG ghi "Điều kiện: ..." hay bất kỳ precondition nào vào trường `step`.
        Mọi điều kiện tiên quyết đặc thù của test case (SLA ở trạng thái X, record Y tồn tại, v.v.)
        phải ghi vào trường `preConditions`, append sau `preConditionsBase`:
        ```
        {preConditionsBase}
        3. SLA versionId=101 đang ở trạng thái APPROVED
        ```
    </step_template_usage>

    <sub_batch id="3a" name="Happy paths">
        <description>≥1 test case per mode from inventory.modes</description>
        <fields>
            <field name="testSuiteName">"Kiểm tra chức năng" (or catalogStyle)</field>
            <field name="testCaseName">Lấy TRỰC TIẾP từ mindmap — KHÔNG dùng snake_case</field>
            <field name="importance">High</field>
            <field name="result">PENDING</field>
            <field name="step">Dùng catalogStyle.stepTemplate — xem step_template_usage ở trên</field>
            <field name="expectedResult">Full response body + HTTP 200 (format theo catalogStyle.responseJsonFormat)</field>
        </fields>
        <checkpoint format="stdout_only">
```
Sub-batch 3a: {N}/{total} modes covered
Missing: [list] → APPEND immediately
```
        </checkpoint>
    </sub_batch>

    <sub_batch id="3b" name="Branch coverage">
        <description>Test TRUE + FALSE for each rule from inventory.businessRules</description>
        <fields>
            <field name="importance">High</field>
            <field name="result">PENDING</field>
        </fields>
        <coverage_rule>Each branch needs 2 cases: TRUE condition and FALSE condition</coverage_rule>
        <checkpoint format="stdout_only">
```
Sub-batch 3b: {N}/{total} branches covered
Missing: [list] → APPEND immediately
```
        </checkpoint>
    </sub_batch>

    <sub_batch id="3c" name="Error code coverage">
        <description>≥1 test per error code from inventory.errorCodes[section=main] with exact message</description>
        <fields>
            <field name="testSuiteName">"Kiểm tra luồng chính" (or catalogStyle)</field>
            <field name="importance">Medium</field>
            <field name="result">PENDING</field>
            <field name="expectedResult">Must contain exact error code and message from inventory (format theo catalogStyle.responseJsonFormat)</field>
        </fields>
        <checkpoint format="stdout_only">
```
Sub-batch 3c: {N}/{total} error codes covered
Missing: [list] → APPEND immediately
```
        </checkpoint>
    </sub_batch>

    <sub_batch id="3d" name="DB verification + External services">
        <description>From inventory.dbOperations: test SQL verify for each table/operation. From inventory.externalServices (if any): test timeout/failure.</description>
        <fields>
            <field name="importance">Medium</field>
            <field name="result">PENDING</field>
        </fields>
        <step_requirement>step must describe complete SQL SELECT for verification</step_requirement>
        <checkpoint format="stdout_only">
```
Sub-batch 3d: {N}/{total} DB ops covered
Missing: [list] → APPEND immediately
```
        </checkpoint>
    </sub_batch>

    <sub_batch id="3e" name="Decision table combinations">
        <description>Test for each combination from inventory.decisionCombinations</description>
        <fields>
            <field name="importance">Medium</field>
            <field name="result">PENDING</field>
        </fields>
        <checkpoint format="stdout_only">
```
Sub-batch 3e: {N}/{total} combinations covered
Missing: [list] → APPEND immediately
```
        </checkpoint>
    </sub_batch>
</step>

<step id="5" name="Write batch-3.json">
    <output_file>{OUTPUT_DIR}/batch-3.json</output_file>

    <format_constraints>
        <constraint>First line MUST be [</constraint>
        <constraint>Last line MUST be ]</constraint>
        <constraint>Write ONLY JSON array — no checkpoint text, no comments</constraint>
    </format_constraints>
</step>

---

## Context Block

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
