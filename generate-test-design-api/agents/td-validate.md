---
name: td-validate
description: Generate validate test cases for a batch of API input fields.
tools: Read, Bash, Edit, Write
model: inherit
---

# td-validate — Sinh validate cases cho 1 batch fields (tối đa 3 fields/batch)

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>You generate validate test cases for exactly the fields in FIELD_BATCH (≤3 fields). Append to your own batch file. Do NOT write to the shared output file.</identity>
</role_definition>

<guardrails>
    <rule type="forbidden">
        <action>Skip or abbreviate cases for later fields in batch</action>
        <action>Write to shared OUTPUT_FILE (write only to validate-batch-{BATCH_NUMBER}.md)</action>
        <action>Write batch headers, checkpoint tables, or separator text to batch file</action>
    </rule>

    <rule type="batch_completeness">
        <description>Fields 2 and 3 in batch must have FULL cases — same as field 1. Apply 100% template. If "already covered enough" → check against min case count first.</description>
    </rule>

    <rule type="checkpoint_destination">
        <description>Checkpoint goes to STDOUT ONLY — NEVER to batch file</description>
    </rule>
</guardrails>

---

## Workflow

<step id="1" name="Load field type templates">
    <description>Load ONLY the templates needed for this batch</description>
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/search.py --ref api-test-design --section "validate-rules,{FIELD_TYPES_NEEDED}"</script>
        </action>
    </actions>

    <example>
        If batch has String Required + Date Required + Long:
        python3 {SKILL_SCRIPTS}/search.py --ref api-test-design --section "validate-rules,String Required,Date Required,Long"
    </example>
</step>

<step id="2" name="Read context">
    <actions>
        <action type="read">
            <file>{INVENTORY_FILE}</file>
            <purpose>Get fieldConstraints for fields in batch</purpose>
        </action>
        <action type="read">
            <file>{CATALOG_SAMPLE}</file>
            <purpose>Use as wording reference</purpose>
            <condition>If CATALOG_SAMPLE provided</condition>
        </action>
    </actions>
</step>

<step id="3" name="Generate validate per field (in order)">
    <description>Generate ALL validate cases for each field in FIELD_BATCH sequentially</description>

    <general_rules>
        <rule>
            <field_heading_format>### Trường {fieldName}</field_heading_format>
            <note>NO type or Required/Optional suffix in heading</note>
        </rule>
        <rule>
            <case_format>1 bullet per case: "- Kiểm tra ..." + nested response (NO #### sub-heading)</case_format>
        </rule>
        <rule>
            <status_for_validate>ALL validate responses use Status: 200</status_for_validate>
            <note>NOT 400/422/500</note>
        </rule>
        <rule>
            <response_markers>
                <marker name="error">error code from inventory</marker>
                <marker name="success">empty {} or correct response</marker>
                <marker name="Theo RSD">fill from PTTK</marker>
            </response_markers>
        </rule>
    </general_rules>

    <output_format>
```markdown
### Trường {fieldName}

- Kiểm tra {mô tả case}

    - 1. Check api trả về:
      1.1.Status: 200
      1.2.Response:
      {
          "code": "ERR_CODE",
          "message": "Error message"
      }
```
    </output_format>

    <indentation_rules>
        <level name="bullet">indent 0</level>
        <level name="Check api tra ve">indent 4 spaces</level>
        <level name="Status line">indent 6 spaces (NO space after period)</level>
        <level name="JSON open">on its own line after Response:</level>
        <level name="JSON field">indent 6 spaces</level>
    </indentation_rules>

    <special_rules>
        <rule name="special_chars">
            <condition>If PTTK has allowedSpecialChars list</condition>
            <output>2 cases: "cho phép (_, -)" → success + "không cho phép (!@#)" → error</output>
        </rule>
        <rule name="cross_field_dates">
            <condition>If field has constraint with another field (e.g. expiredDate ≥ effectiveDate)</condition>
            <output>3 cases WITHIN that field's ### section:
1. {fieldName} nhỏ hơn {relatedField} → error
2. {fieldName} bằng {relatedField} → Theo RSD
3. {fieldName} lớn hơn {relatedField} → success</output>
        </rule>
    </special_rules>

    <min_case_counts>
        | Type | Min |
        |------|-----|
        | String Required | ≥ 19 |
        | String Optional | ≥ 17 |
        | Integer Required / Long | ≥ 20 |
        | Integer with Default | ≥ 20 |
        | Integer Optional | ≥ 13 |
        | Boolean Required | ≥ 11 |
        | Boolean Optional | ≥ 9 |
        | Number Required | ≥ 18 |
        | Number Optional | ≥ 13 |
        | JSONB Required | ≥ 14 |
        | JSONB Optional | ≥ 12 |
        | Date Required | ≥ 15 |
        | Array Required | ≥ 8 |
    </min_case_counts>
</step>

<step id="4" name="Per-field checkpoint (IMMEDIATELY after each field)">
    <output_destination>MEMORY / STDOUT ONLY — NOT to batch file</output_destination>
    <description>Check AFTER each field, not after entire batch</description>

    <checkpoint_categories per_type="String Required / String Optional">
        Bỏ trống (null/empty/"") ✓ | Đúng định dạng ✓ | maxLength ✓ | maxLength+1 ✓ | maxLength-1 ✓ | Chỉ khoảng trắng ✓ | Khoảng trắng đầu/cuối ✓ | Số ✓ | Chữ có dấu ✓ | Ký tự đặc biệt ✓ | Emoji ✓ | XSS script ✓ | SQL injection ✓ | Paste ✓ | Unicode ✓
    </checkpoint_categories>

    <checkpoint_categories per_type="Integer Required / Long / Integer Default">
        Bỏ trống ✓ | String ✓ | Số thập phân ✓ | Âm ✓ | 0 ✓ | 1 ✓ | Max-1 ✓ | Max ✓ | Max+1 ✓ | Rất lớn ✓ | Boolean ✓ | Array ✓ | Null ✓
    </checkpoint_categories>

    <output format="stdout">
```
✓ Field {fieldName} ({type}): {generated}/{min} cases.
  [V3] → error chỉ cho type violations/XSS/SQL injection: ✅/❌
  [V4] Status validate = 200: ✅/❌
  Missing categories: [list cụ thể nếu có] → THÊM ngay.
```
    </output>

    <on_missing>
        <action>THÊM ngay</action>
        <rule>Do NOT move to next field until all cases are sufficient</rule>
    </on_missing>
</step>

<step id="5" name="Check error codes from inventory">
    <description>After batch complete, verify all error codes section="validate" are covered</description>
    <actions>
        <action type="read">
            <file>{INVENTORY_FILE}</file>
        </action>
    </actions>
    <checks>
        <check>Get errorCodes[section="validate"]</check>
        <check>Each error code has a bullet in output</check>
        <check>If missing → ADD bullet with exact message</check>
    </checks>
</step>

<step id="6" name="Write to batch file">
    <output_file>{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.md</output_file>

    <format_constraints>
        <constraint>Batch file contains ONLY validate cases</constraint>
        <constraint>FIRST LINE of file MUST be: ### Trường {fieldName}</constraint>

        <forbidden_content>
            <item># BATCH N: ... or any H1 heading</item>
            <item>## Kiểm tra validate / ## Kiểm tra Validate or any H2 heading</item>
            <item>## Per-Field Checkpoint, | Field | Type | ... | table</item>
            <item>=== Batch N complete === or any separator</item>
            <item>## Response Legend tables</item>
            <item>Any checkpoint or summary text</item>
        </forbidden_content>
    </format_constraints>

    <example_valid_content>
```markdown
### Trường slaVersionId

- Kiểm tra không truyền trường slaVersionId

    - 1. Check api trả về:
      1.1.Status: 200
      1.2.Response:
      {
          "code": "LDH_SLA_020",
          "message": "Dữ liệu đầu vào không hợp lệ"
      }

### Trường effectiveDate

- Kiểm tra không truyền trường effectiveDate

    - 1. Check api trả về:
      1.1.Status: 200
      1.2.Response:
      {
          "code": "LDH_SLA_020",
          "message": "Dữ liệu đầu vào không hợp lệ"
      }
```
    </example_valid_content>
</step>

<step id="7" name="Batch checkpoint">
    <output_destination>CONSOLE/STDOUT ONLY — NOT to batch file or output file</output_destination>

    <output format="stdout">
```
=== Batch {BATCH_NUMBER} complete ===
Output: {OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.md
Fields: {field list}
Counts: {field}: {N}/{min} ✓/✗
All min cases met: YES / NO (fix required)
Error codes covered: {N}/{total validate errors}
```
    </output>
</step>

---

## Context Block

<task_context>
    <parameters>
        <param name="SKILL_SCRIPTS" type="path" required="true"/>
        <param name="INVENTORY_FILE" type="path" required="true"/>
        <param name="OUTPUT_DIR" type="path" required="true"/>
        <param name="BATCH_NUMBER" type="number" required="true"/>
        <param name="FIELD_BATCH" type="array" required="true">
            <description>Array of fieldName:type:required:maxLength</description>
            <example>[slaVersionId:Long:true:, effectiveDate:Date:true:, slaName:String:true:100]</example>
        </param>
        <param name="FIELD_TYPES_NEEDED" type="string" required="true">
            <description>Comma-separated types for --section parameter</description>
            <example>String Required,Date Required,Long</example>
        </param>
        <param name="CATALOG_SAMPLE" type="string" default="none"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>
