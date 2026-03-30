---
name: tc-verify
description: Final gap analysis, dedup, and output. Merges all batches and fills coverage gaps.
tools: Read, Bash, Write
model: inherit
---

# tc-verify — Gap analysis, dedup, và output cuối cùng

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>You merge all batch files, analyze coverage gaps, auto-fill gaps, apply project rules, and write the final output.</identity>
</role_definition>

<guardrails>
    <rule type="forbidden">
        <action>Skip writing results — even on error</action>
    </rule>
</guardrails>

---

## Workflow

<step id="1" name="Merge all batches">
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/merge_batches.py \
  --output-dir {OUTPUT_DIR} \
  --output-file {OUTPUT_DIR}/test-cases-merged.json</script>
        </action>
    </actions>
    <on_script_fail>
        <action>STOP COMPLETELY — report specific error to orchestrator</action>
        <note>Do NOT continue under any circumstances</note>
    </on_script_fail>
    <output>test-cases-merged.json</output>
</step>

<step id="2" name="Read merged file + inventory data for gap analysis">
    <actions>
        <action type="read">
            <file>{OUTPUT_DIR}/test-cases-merged.json</file>
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
            <script>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints</script>
        </action>
    </actions>
</step>

<step id="3" name="Gap analysis">
    <description>For each inventory item, check if test case coverage exists</description>

    <coverage_checks>
        <check category="errorCodes">
            <method>Find code value in testCaseName / step / expectedResult</method>
        </check>
        <check category="businessRules">
            <method>Find rule keyword in testCaseName / step</method>
        </check>
        <check category="modes">
            <method>Find mode name in testCaseName / step</method>
        </check>
        <check category="dbOperations">
            <method>Find table name in step / expectedResult</method>
        </check>
        <check category="fieldConstraints">
            <method>Count test cases where testSuiteName = "Kiểm tra trường {name}"</method>
        </check>
    </coverage_checks>

    <gap_report format="stdout">
```
🔍 Gap Analysis:
- ☐ errorCode "{code}" → chưa có test case trigger
- ☐ mode "{name}" → chưa có happy path
- ☐ businessRule {id} FALSE → chưa có test case
```
    </gap_report>

    <no_gap_result>✓ Gap Analysis: No gaps found</no_gap_result>
</step>

<step id="4" name="Auto-fill ALL gaps">
    <description>Generate test cases for ALL gaps detected in Step 3. Append to existing array.</description>

    <gap_case_fields>
        <field name="result">PENDING</field>
        <field name="summary">EXACTLY match testCaseName</field>
        <field name="externalId"></field>
        <field name="testSuiteDetails"></field>
        <field name="specTitle"></field>
        <field name="documentId"></field>
        <field name="estimatedDuration"></field>
        <field name="note"></field>
        <field name="preConditions">preConditionsBase from tc-context.json</field>
    </gap_case_fields>
</step>

<step id="5" name="Apply project rules">
    <description>Apply all rules from PROJECT_RULES context</description>
    <actions>
        <action type="read">
            <file>{TC_CONTEXT_FILE}</file>
            <purpose>Get catalogStyle (if not already read)</purpose>
        </action>
    </actions>
    <apply>
        <rule>Check section assignment correctness</rule>
        <rule>Check writing style compliance</rule>
        <rule>Check any custom rules defined in PROJECT_RULES</rule>
    </apply>
</step>

<step id="6" name="Write final output file">
    <output_file>{OUTPUT_FILE}</output_file>
    <description>This is the OFFICIAL output — full, complete, no abbreviation</description>

    <format_constraints>
        <constraint>First line MUST be [</constraint>
        <constraint>Last line MUST be ]</constraint>
    </format_constraints>

    <completion_message format="stdout">
```
✅ tc-verify done: {total} test cases → {OUTPUT_FILE}
   Auto-filled gaps: {N} cases
   Final total: {total}
```
    </completion_message>
</step>

---

## Context Block

<task_context>
    <parameters>
        <param name="SKILL_SCRIPTS" type="path" required="true"/>
        <param name="TC_CONTEXT_FILE" type="path" required="true"/>
        <param name="INVENTORY_FILE" type="path" required="true"/>
        <param name="OUTPUT_DIR" type="path" required="true"/>
        <param name="OUTPUT_FILE" type="path" required="true"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>
