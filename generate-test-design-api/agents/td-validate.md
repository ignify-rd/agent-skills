---
name: td-validate
description: Generate validate test cases for a batch of API input fields using inventory rsdConstraints.
tools: Read, Bash, Edit, Write
model: inherit
---

# td-validate — Sinh validate cases cho 1 batch fields (tối đa 3 fields/batch)

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>You generate validate test cases for exactly the fields in FIELD_BATCH (≤3 fields). You read field templates from api-test-design.md (bảng cases BẮT BUỘC từ fieldTestTemplates.js) and resolve response using rsdConstraints from inventory. PHẢI sinh ĐẦY ĐỦ mọi case — KHÔNG được thiếu.</identity>
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
        <description>MỌI field cùng type PHẢI có ĐẦY ĐỦ cases theo bảng template. Các field cùng type chỉ khác nhau về RESPONSE (dựa trên rsdConstraints / Required vs Optional), KHÔNG khác về SỐ LƯỢNG cases.</description>
    </rule>

    <rule type="checkpoint_destination">
        <description>Checkpoint goes to STDOUT ONLY — NEVER to batch file</description>
    </rule>

    <rule type="dedup_overlap" id="R7">
        <description>
            ⛔ BASE TEMPLATE OVERLAPS VỚI BOUNDARY RULES — PHẢI MERGE trước khi sinh cases.
            Agent KHÔNG được sinh base cases VÀ boundary cases ĐỘC LẬP. PHẢI merge thành 1 danh sách cuối cùng.
        </description>

        <step name="pre_generation_merge" type="MANDATORY_BEFORE_STEP_3">
            <description>Trước khi sinh bất kỳ case nào, PHẢI thực hiện 3 bước merge:</description>

            <substep id="1" name="Thu thập base cases">
                Lấy tất cả cases từ template bảng (rows 1-N của section type tương ứng).
                ĐÁNH DẤU mỗi base case bằng nhãn loại: type-group (String, Number, Integer, Date...).
            </substep>

            <substep id="2" name="Thu thập constraint cases">
                Dựa vào rsdConstraints (min, max, maxDecimalPlaces, maxLength...) → tính constraint values.
                VÍ DỤ: min=0, max=100, maxDecimalPlaces=2 → boundary values = [-1, 0, 100, 101, 1.5, 1.55, 1.555].
            </substep>

            <substep id="3" name="MERGE — loại bỏ overlap">
                Với mỗi constraint value, tìm base case cùng loại/nhóm:
                - Base case "Số âm" (-1) trùng boundary value (-1) → MERGE → giữ boundary case, BỎ base case.
                - Base case "Số thập phân" (1.5) trùng decimal boundary (1.5) → MERGE → giữ boundary case, BỎ base case.
                - Base case "Boolean" (true/false) → KHÔNG trùng với number boundary → GIỮ base case.
                KẾT QUẢ = final_case_list = (base_cases − overlapping) + constraint_cases
            </substep>
        </step>

        <overlap_map>
            <description>Bảng map overlap GIỮA base template VÀ constraint rules:</description>
            <table>
                | Base case (template) | Trùng với constraint nào? | Hành động |
                |----------------------|---------------------------|-----------|
                | "Số âm" (VD: -1) | min-1 (nếu min > min-1) | MERGE → dùng boundary case |
                | "Số thập phân" (VD: 1.5) | maxDecimalPlaces boundary | MERGE → dùng boundary case |
                | "maxLength-1/max/max+1" | String maxLength constraint | MERGE → dùng boundary case |
                | "Số 0" | min=0 hoặc max=0 | MERGE → dùng boundary case |
                | "Boolean" (true/false) | Không trùng number | GIỮ base case |
                | "XSS", "SQL", "Object", "Mảng" | Không trùng | GIỮ base case |
                | "Leading zero", "Số rất lớn" | Không trùng | GIỮ base case |
            </table>
        </overlap_map>

        <wrong_approach>
            <description>SAI — làm thế này = VI PHẠM R7:</description>
            <example>Sinh base case "Số âm" → error RỒI sinh tiếp boundary case "-1" → error → TRÙNG LẶP!</example>
        </wrong_approach>

        <correct_approach>
            <description>ĐÚNG — sau khi MERGE:</description>
            <example>CHỈ 1 case cho -1: "Kiểm tra truyền trường warningYellowPct nhỏ hơn min = -1" → error</example>
        </correct_approach>
    </rule>
</guardrails>

---

## Workflow

<step id="1" name="Load field type templates">
    <description>Load templates cần cho batch — mỗi type có bảng cases BẮT BUỘC từ fieldTestTemplates.js. Agent PHẢI sinh ĐẦY ĐỦ mọi case trong bảng, KHÔNG được bỏ sót.</description>
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
        <item>errorCodes[section="validate"] → error code + message for error cases</item>
        <item>responseSchema.success → success response for success cases</item>
        <item>responseSchema.error → error response structure</item>
    </extract_from_inventory>
</step>

<step id="2b" name="Pre-generation — MERGE base + boundary (MANDATORY)">
    <description>
        ⛔ BẮT BUỘC thực hiện TRƯỚC KHI sinh bất kỳ case nào.
        Thực hiện theo R7 dedup_overlap trong guardrails.
    </description>
    <actions>
        <action type="merge">
            <input>base_template_cases + constraint_values_from_rsdConstraints</input>
            <output>final_case_list (deduplicated)</output>
        </action>
    </actions>

    <output>
        <item>final_case_list: danh sách cases sau khi MERGE loại bỏ overlap</item>
        <item>case_count: số cases cuối cùng</item>
    </output>

    <checkpoint>
        Sau khi merge, in ra console:
        ```
        [R7] MERGE complete: {base_count} base + {constraint_count} constraint → {final_count} final cases
        Overlaps removed: {list giá trị bị loại}
        ```
    </checkpoint>
</step>

<step id="3" name="Generate validate per field (in order)">
    <description>Generate ALL validate cases for each field in FIELD_BATCH sequentially — dùng final_case_list từ Step 2b</description>

    <response_resolution>
        <description>
            Mỗi case trong bảng template có cột "Response mặc định". Agent fill response theo logic sau:
        </description>

        <rule name="error">
            <condition>Cột ghi "→ error"</condition>
            <response>Error code từ errorCodes[section="validate"] trong inventory. Status: 200.</response>
        </rule>

        <rule name="success">
            <condition>Cột ghi "→ success"</condition>
            <response>Success response từ responseSchema.success trong inventory. Status: 200.</response>
        </rule>

        <rule name="theo_rsd">
            <condition>Cột ghi "→ Theo RSD: rsdConstraints.X (mặc định: Y)"</condition>
            <resolution_logic>
                1. Đọc rsdConstraints.X trong inventory cho field hiện tại
                2. Nếu giá trị = true/"success" → dùng success response
                3. Nếu giá trị = false/"error" → dùng error response
                4. Nếu giá trị = null (tài liệu không đề cập) → dùng response MẶC ĐỊNH ghi trong template (thường là error)
            </resolution_logic>
        </rule>

        <completeness_rule>
            ⛔ CRITICAL: Agent PHẢI sinh ĐẦY ĐỦ mọi case trong **final_case_list** (sau khi MERGE từ Step 2b).
            KHÔNG được bỏ sót bất kỳ case nào trong final_case_list.
        </completeness_rule>
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
        | String Required | ≥ 17 |
        | String Optional | ≥ 17 |
        | Integer Required / Long | ≥ 18 |
        | Integer with Default | ≥ 18 |
        | Integer Optional | ≥ 18 |
        | Boolean Required | ≥ 11 |
        | Boolean Optional | ≥ 9 |
        | Number Required | ≥ 18 |
        | Number Optional | ≥ 18 |
        | JSONB Required | ≥ 14 |
        | JSONB Optional | ≥ 12 |
        | Date Required | ≥ 15 |
        | Date Optional | ≥ 15 |
        | DateTime Required | ≥ 17 |
        | DateTime Optional | ≥ 17 |
        | Array Required | ≥ 15 |
        | Array Optional | ≥ 15 |
    </min_case_counts>

    <boundary_rules>
        <description>⛔ CHỈ sinh đúng số boundary cases theo constraint, KHÔNG thêm giá trị trung gian.</description>
        <table>
            | Constraint | Cases cần sinh | Ví dụ |
            |---|---|---|
            | Có cả min VÀ max (VD: 0–100) | **4 cases**: min-1, min, max, max+1 | -1, 0, 100, 101 |
            | Chỉ có max (VD: max=100) | **3 cases**: max-1, max, max+1 | 99, 100, 101 |
            | Chỉ có min (VD: min=0) | **3 cases**: min-1, min, min+1 | -1, 0, 1 |
            | Số chữ số (maxDigits: N) | **3 cases**: (N-1) chữ số, N chữ số (=max), N+1 chữ số | maxDigits=2 → 9, 99, 100 |
        </table>
        <examples>
            <wrong_cases>
                - min=0, max=100 → KHÔNG sinh: 1, 50, 99 (giá trị trung gian)
            </wrong_cases>
            <correct_cases>
                - min=0, max=100 → CHỈ sinh: -1, 0, 100, 101
                - max=100 → CHỈ sinh: 99, 100, 101
                - min=0 → CHỈ sinh: -1, 0, 1
            </correct_cases>
        </examples>
    </boundary_rules>
</step>

<step id="4" name="Per-field checkpoint (IMMEDIATELY after each field)">
    <output_destination>MEMORY / STDOUT ONLY — NOT to batch file</output_destination>
    <description>Check AFTER each field, not after entire batch</description>

    <checkpoint_categories per_type="String Required / String Optional">
        Bỏ trống ✓ | Không truyền ✓ | Null ✓ | maxLength-1 ✓ | maxLength ✓ | maxLength+1 ✓ | Ký tự số ✓ | Chữ không dấu ✓ | Chữ có dấu ✓ | Ký tự đặc biệt ✓ | All space ✓ | Space giữa ✓ | Space đầu/cuối ✓ | XSS ✓ | SQL injection ✓ | Object ✓ | Mảng ✓
    </checkpoint_categories>

    <checkpoint_categories per_type="Integer Required / Long / Integer Default / Integer Optional">
        Để trống ✓ | Không truyền ✓ | Null ✓ | Boundary ✓ | Số thập phân ✓ | Leading zero ✓ | Số rất lớn ✓ | Chuỗi ✓ | Chữ lẫn số ✓ | Ký tự đặc biệt ✓ | All space ✓ | Space đầu/cuối ✓ | Space giữa ✓ | Boolean ✓ | XSS ✓ | SQL injection ✓ | Object ✓ | Mảng ✓
    </checkpoint_categories>

    <checkpoint_categories per_type="Number Required / Number Optional">
        Để trống ✓ | Không truyền ✓ | Null ✓ | Boundary ✓ | Số thập phân hợp lệ ✓ | Leading zero ✓ | Số rất lớn ✓ | Chuỗi ✓ | Chữ lẫn số ✓ | Ký tự đặc biệt ✓ | All space ✓ | Space đầu/cuối ✓ | Boolean ✓ | XSS ✓ | SQL injection ✓ | Object ✓ | Mảng ✓
        *(Ghi chú: "Boundary" = min-1/min/max/max+1 đã MERGE từ base "Số âm" + boundary rule. "Số thập phân hợp lệ" = maxDecimalPlaces cases đã MERGE từ base "Số thập phân")*
    </checkpoint_categories>

    <checkpoint_categories per_type="Array Required / Array Optional">
        Không truyền ✓ | Null ✓ | Mảng rỗng ✓ | Phần tử rỗng ✓ | String thay vì array ✓ | Number thay vì array ✓ | Object thay vì array ✓ | Boolean thay vì array ✓ | XSS ✓ | SQL injection ✓ | Mảng 1 phần tử ✓ | Mảng nhiều phần tử ✓ | Phần tử trùng nhau ✓ | Phần tử là String (sai kiểu) ✓ | Phần tử là Integer (sai kiểu) ✓
    </checkpoint_categories>

    <checkpoint_categories per_type="Boolean Required / Boolean Optional">
        Để trống ✓ | Không truyền ✓ | Null ✓ | true ✓ | false ✓ | Chuỗi "true"/"false" ✓ | Số nguyên (0/1) ✓ | Số khác 0 và 1 ✓ | Chuỗi bất kỳ ✓ | Mảng ✓ | Object ✓
    </checkpoint_categories>

    <checkpoint_categories per_type="JSONB Required / JSONB Optional">
        Để trống ✓ | Không truyền ✓ | Null ✓ | JSON sai syntax ✓ | Mảng thay vì object ✓ | Chuỗi rỗng ✓ | String thuần ✓ | Number ✓ | Boolean ✓ | XSS trong JSON value ✓ | SQL injection trong JSON value ✓ | JSON hợp lệ ✓ | JSON sai format nghiệp vụ ✓ | Object rỗng ✓
    </checkpoint_categories>

    <checkpoint_categories per_type="Date Required / Date Optional">
        Để trống ✓ | Không truyền ✓ | Null ✓ | Đúng định dạng ✓ | Sai định dạng ✓ | Chuỗi không phải ngày tháng ✓ | Ngày không tồn tại ✓ | Ngày quá khứ ✓ | Ngày hiện tại ✓ | Ngày tương lai ✓ | Số nguyên ✓ | XSS ✓ | SQL injection ✓ | Object ✓ | Mảng ✓
    </checkpoint_categories>

    <checkpoint_categories per_type="DateTime Required / DateTime Optional">
        Để trống ✓ | Không truyền ✓ | Null ✓ | Đúng định dạng ✓ | Sai định dạng ngày ✓ | Sai định dạng giờ ✓ | Chỉ có ngày không có giờ ✓ | Chuỗi không phải ngày giờ ✓ | Ngày không tồn tại ✓ | Ngày giờ quá khứ ✓ | Ngày giờ hiện tại ✓ | Ngày giờ tương lai ✓ | Số nguyên ✓ | XSS ✓ | SQL injection ✓ | Object ✓ | Mảng ✓
    </checkpoint_categories>

    <output format="stdout">
```
✓ Field {fieldName} ({type}): {generated}/{min} cases.
  [V3] Error cases → error response, Success cases → success response: ✅/❌
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
