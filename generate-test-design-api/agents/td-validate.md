---
name: td-validate
description: Generate validate test cases for a batch of API input fields using inventory rsdConstraints.
tools: Read, Bash, Edit, Write
model: inherit
---

# td-validate — Sinh validate cases cho 1 batch fields (tối đa 3 fields/batch)

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>You generate validate test cases for exactly the fields in FIELD_BATCH (≤3 fields). You read field templates from api-test-design.md (3 nhóm: luôn lỗi / luôn thành công / phụ thuộc spec) and resolve spec-dependent cases using rsdConstraints from inventory.</identity>
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

    <rule type="consistency">
        <description>MỌI field cùng type PHẢI có ĐÚNG cùng số cases Nhóm 1 + Nhóm 2. Nhóm 3 chỉ khác nhau về RESPONSE (dựa trên rsdConstraints), KHÔNG khác về SỐ LƯỢNG cases.</description>
    </rule>

    <rule type="checkpoint_destination">
        <description>Checkpoint goes to STDOUT ONLY — NEVER to batch file</description>
    </rule>
</guardrails>

---

## Workflow

<step id="1" name="Load field type templates">
    <description>Load ONLY the templates needed for this batch — templates now have 3 nhóm thay vì bảng marker</description>
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/search.py --ref api-test-design --section "validate-rules,{FIELD_TYPES_NEEDED}"</script>
        </action>
    </actions>
</step>

<step id="2" name="Read inventory — get rsdConstraints">
    <actions>
        <action type="read">
            <file>{INVENTORY_FILE}</file>
            <purpose>Get fieldConstraints[].rsdConstraints for fields in batch + errorCodes[section="validate"] + responseSchema</purpose>
        </action>
        <action type="read">
            <file>{CATALOG_SAMPLE}</file>
            <purpose>Use as wording reference</purpose>
            <condition>If CATALOG_SAMPLE provided</condition>
        </action>
    </actions>

    <extract_from_inventory>
        <item>fieldConstraints[] → filter by field names in FIELD_BATCH → get rsdConstraints per field</item>
        <item>errorCodes[section="validate"] → error code + message for Nhóm 1 cases</item>
        <item>responseSchema.success → success response for Nhóm 2 cases</item>
        <item>responseSchema.error → error response structure</item>
    </extract_from_inventory>
</step>

<step id="3" name="Generate validate per field (in order)">
    <description>Generate ALL validate cases for each field in FIELD_BATCH sequentially</description>

    <response_resolution>
        <nhom1 name="Luôn lỗi">
            <description>Cases listed under "Nhóm 1" in template</description>
            <response>Error code từ errorCodes[section="validate"] trong inventory. Status: 200.</response>
        </nhom1>

        <nhom2 name="Luôn thành công">
            <description>Cases listed under "Nhóm 2" in template</description>
            <response>Success response từ responseSchema.success trong inventory. Status: 200.</response>
        </nhom2>

        <nhom3 name="Phụ thuộc spec">
            <description>Cases listed under "Nhóm 3" in template — each references a rsdConstraints field</description>
            <resolution_logic>
                1. Đọc rsdConstraints field tương ứng (VD: case "Truyền null" → đọc rsdConstraints.allowNull)
                2. Nếu giá trị = true/"success" → dùng success response
                3. Nếu giá trị = false/"error" → dùng error response
                4. Nếu giá trị = string khác (custom) → dùng response tùy chỉnh theo mô tả
                5. Nếu giá trị = null (tài liệu không đề cập) → dùng error response (default an toàn)
            </resolution_logic>
        </nhom3>
    </response_resolution>

    <general_rules>
        <rule>
            <field_heading_format>### Trường {fieldName}</field_heading_format>
            <note>NO type or Required/Optional suffix in heading</note>
        </rule>
        <rule>
            <case_format>1 bullet per case: "- Kiểm tra ..." + nested response (NO #### sub-heading)</case_format>
        </rule>
        <rule id="heading_describes_condition" type="hard_constraint">
            <description>⛔ Case heading mô tả ĐIỀU KIỆN KIỂM TRA, KHÔNG mô tả giá trị cụ thể truyền vào.</description>
            <wrong>- Kiểm tra truyền trường slaName = " test "</wrong>
            <wrong>- Kiểm tra truyền trường slaName = "SLA xử lý Báo cáo đề xuất tín dụng"</wrong>
            <correct>- Kiểm tra truyền trường slaName có khoảng trắng đầu/cuối</correct>
            <correct>- Kiểm tra truyền trường slaName = {maxLen+1} ký tự</correct>
            <correct>- Kiểm tra truyền trường slaName chứa ký tự đặc biệt</correct>
            <correct>- Kiểm tra truyền trường slaName = null</correct>
            <principle>Heading trả lời "kiểm tra CÁI GÌ" (điều kiện), KHÔNG trả lời "truyền GIÁ TRỊ GÌ".</principle>
        </rule>
        <rule>
            <status_for_validate>ALL validate responses use Status: 200</status_for_validate>
            <note>NOT 400/422/500</note>
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
            <condition>If inventory has rsdConstraints.allowedChars list</condition>
            <output>2 cases: "cho phép (_, -)" → success + "không cho phép (!@#)" → error</output>
        </rule>
        <rule name="cross_field_dates">
            <condition>If rsdConstraints.crossFieldRules has entries</condition>
            <output>For each crossFieldRule, add cases WITHIN that field's ### section:
1. {fieldName} nhỏ hơn {relatedField} → error (use errorCode from crossFieldRule)
2. {fieldName} bằng {relatedField} → spec-dependent
3. {fieldName} lớn hơn {relatedField} → success</output>
        </rule>
    </special_rules>

    <min_case_counts>
        | Type | Min |
        |------|-----|
        | String Required | ≥ 18 |
        | String Optional | ≥ 17 |
        | Integer Required / Long | ≥ 16 |
        | Integer with Default | ≥ 16 |
        | Integer Optional | ≥ 13 |
        | Boolean Required | ≥ 11 |
        | Boolean Optional | ≥ 9 |
        | Number Required | ≥ 15 |
        | Number Optional | ≥ 11 |
        | JSONB Required | ≥ 14 |
        | JSONB Optional | ≥ 12 |
        | Date Required | ≥ 14 |
        | Array Required | ≥ 10 |
    </min_case_counts>
</step>

<step id="4" name="Per-field checkpoint (IMMEDIATELY after each field)">
    <output_destination>MEMORY / STDOUT ONLY — NOT to batch file</output_destination>
    <description>Check AFTER each field, not after entire batch</description>

    <checkpoint_categories per_type="String Required / String Optional">
        Bỏ trống (null/empty/"") ✓ | Đúng định dạng ✓ | maxLength ✓ | maxLength+1 ✓ | maxLength-1 ✓ | Chỉ khoảng trắng ✓ | Khoảng trắng đầu/cuối ✓ | Khoảng trắng giữa ✓ | Chữ có dấu ✓ | Ký tự đặc biệt ✓ | Emoji ✓ | XSS ✓ | SQL injection ✓ | Unicode ✓
    </checkpoint_categories>

    <checkpoint_categories per_type="Integer Required / Long / Integer Default">
        Bỏ trống ✓ | Chuỗi ✓ | Số thập phân ✓ | Âm ✓ | Hợp lệ ✓ | Boolean ✓ | Mảng ✓ | Object ✓ | Null ✓ | XSS ✓ | SQL injection ✓
    </checkpoint_categories>

    <output format="stdout">
```
✓ Field {fieldName} ({type}): {generated}/{min} cases.
  [V3] Nhóm 1 all error, Nhóm 2 all success: ✅/❌
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
