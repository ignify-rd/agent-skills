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

    <sub_batch id="3a" name="Happy paths">
        <description>≥1 test case per mode from inventory.modes</description>
        <fields>
            <field name="testSuiteName">"Kiểm tra chức năng" (or catalogStyle)</field>
            <field name="testCaseName">"Luồng chính_{tên mode}"</field>
            <field name="importance">High</field>
            <field name="result">PENDING</field>
            <field name="step">Full request description with that mode</field>
            <field name="expectedResult">Full response body + HTTP 200</field>
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
            <field name="expectedResult">Must contain exact error code and message from inventory</field>
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
