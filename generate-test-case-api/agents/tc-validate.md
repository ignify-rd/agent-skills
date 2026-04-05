---
name: tc-validate
description: Generate BATCH 2 — validate test cases for a batch of fields (≤5 fields per batch).
tools: Read, Bash, Write
model: inherit
---

# tc-validate — Sinh BATCH 2: Validate test cases (per field batch)

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>You generate validate test cases for fields in FIELD_BATCH. Use Phase A Extended for fileContent fields (write lightweight JSON with expectedResult inline), Phase A for standard request fields, Phase B only as last resort. Always write a completion sentinel at the end.</identity>
</role_definition>

<guardrails>
    <rule type="forbidden">
        <action>Skip or abbreviate cases for later fields in batch</action>
        <action>Read test-design-api.md directly</action>
        <action>Write non-JSON content to batch file</action>
        <action>Output JSON objects MUST NOT contain these fields: externalId, testSuiteDetails, specTitle, documentId, estimatedDuration, note — omit them entirely</action>
        <action>Print or display the generated JSON content in text response — ONLY write to file via Write tool. Text output must be brief status messages only (e.g. "Writing batch..." / "Done.").</action>
        <action>Create temporary Python/JS scripts to process data — use existing scripts in {SKILL_SCRIPTS}/ only</action>
    </rule>

    <rule type="hard_constraint">
        <field>result</field>
        <required_value>PENDING</required_value>
        <note>NOT empty string ""</note>
    </rule>

    <rule type="hard_constraint">
        <field>summary</field>
        <rule>EXACTLY match testCaseName</rule>
    </rule>

    <rule type="batch_completeness">
        <description>ALL fields in batch (up to 5) must have FULL cases — same as field 1. Do NOT abbreviate.</description>
        <condition>If agent thinks "already covered enough"</condition>
        <action>Check against min case count before concluding</action>
    </rule>

    <rule type="checkpoint_destination">
        <description>Checkpoint goes to STDOUT ONLY — NEVER to batch file</description>
    </rule>

    <rule type="token_efficiency" id="no_relist">
        <description>
            ⛔ CRITICAL TOKEN OPTIMIZATION — DO NOT re-list, re-enumerate, or repeat the test case descriptions
            in your thinking/reasoning before generating output. You already have all field info and templates.
            Go DIRECTLY to generating the template JSON output. Do not plan cases one by one in thinking —
            apply the template mechanically for each field type.
        </description>
    </rule>
</guardrails>

---

## Workflow

## Phase selection guide

| Situation | Use |
|-----------|-----|
| Request fields, standard patterns (null/empty/type/maxLength) | Phase A |
| FileContent fields with custom error text from test-design | **Phase A Extended** |
| Cases needing cross-field logic or unusual step format | Phase B (fallback only) |

---

### Phase A — Script expansion (RECOMMENDED for standard cases)

Use this approach when test cases follow standard validation patterns (null, empty, type error, maxLength, format) — no custom business-logic expectedResult needed.

<step id="A1" name="Write lightweight agent output — validate-cases-{N}.json">
    <description>
        Write a JSON array with one object per case. Each object has:
        - "field": field name
        - "case": case description in Vietnamese (e.g. "Không truyền", "Truyền null", "Boolean thay vì string")
        - "value" (optional): the test value to send. If omitted → field is removed from request body.

        ⛔ DO NOT write full test case objects here. Keep it lightweight (~3-4 tokens per case).
        expand_validate.py will fill in testSuiteName, testCaseName, step, expectedResult, preConditions.
    </description>

    <output_file>{OUTPUT_DIR}/validate-cases-{BATCH_NUMBER}.json</output_file>

    <examples>
        ```json
        [
          {"field": "slaName", "case": "Không truyền"},
          {"field": "slaName", "case": "Truyền null", "value": null},
          {"field": "slaName", "case": "Truyền chuỗi rỗng", "value": ""},
          {"field": "slaName", "case": "Truyền 101 ký tự (vượt max)", "value": "AAA...101"},
          {"field": "slaName", "case": "Boolean thay vì string", "value": true},
          {"field": "slaVersionId", "case": "String thay vì number", "value": "abc"},
          {"field": "effectiveDate", "case": "Sai định dạng", "value": "2025/01/01"},
          {"field": "effectiveDate", "case": "Ngày không tồn tại", "value": "30/02/2025"}
        ]
        ```
    </examples>

    <case_description_rules>
        - "Không truyền" → field absent from body
        - "Truyền null" → field = null
        - "Truyền chuỗi rỗng" → field = ""
        - "Boolean thay vì string" → field = true/false
        - "String thay vì number" → field = "abc"
        - "Array thay vì object" → field = []
        - "Object thay vì array" → field = {}
        - "Sai định dạng" → field = "wrong-format"
        - "Ngày không tồn tại" → field = "30/02/2025"
        - "Ký tự đặc biệt" → field = "@#$%"
        - "SQL Injection" → field = "' OR 1=1--"
        - "XSS" → field = "&lt;script&gt;alert(1)&lt;/script&gt;"
        - "Unicode đặc biệt" → field = "中文"
        - Custom cases → describe in Vietnamese with explicit value
    </case_description_rules>
</step>

<step id="A2" name="Run expand_validate.py">
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/expand_validate.py \
    --cases "{OUTPUT_DIR}/validate-cases-{BATCH_NUMBER}.json" \
    --context "{TC_CONTEXT_FILE}" \
    --inventory "{INVENTORY_FILE}" \
    --output "{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.json"</script>
        </action>
    </actions>

    <notes>
        - Script reads catalogStyle.responseJsonFormat from tc-context.json to decide multiline vs oneline.
        - Script looks up error codes from inventory.errorCodes (section="validate").
        - Script generates testSuiteName, testCaseName, paramOverride, expectedResult automatically.
        - If item has "expectedResult" field → script uses it directly (Phase A Extended).
        - If item has "testCaseName" field → script uses it as-is.
        - merge_batches.py handles the rest (template → full test case expansion).
    </notes>
</step>

<step id="A3" name="Write completion sentinel">
    <actions>
        <action type="bash">
            <script>python3 -X utf8 -c "
import os
s = r'{OUTPUT_DIR}/.validate-{BATCH_NUMBER}.done'
open(s, 'w').write('done')
print(f'Sentinel written: {s}')
"</script>
        </action>
    </actions>
    <note>This sentinel tells the orchestrator this batch is complete. MUST write even if 0 cases generated.</note>
</step>

---

### Phase A Extended — Phase A with custom expectedResult (RECOMMENDED for fileContent fields)

Use this when the test design has **specific expected result text** per case (e.g., fileContent fields with per-field error messages like "Trường X không được để trống").

Same workflow as Phase A, but the lightweight cases JSON includes `"expectedResult"` (and optionally `"testCaseName"`) inline:

```json
[
  {
    "field": "debitAccount",
    "case": "Kiểm tra truyền file hợp lệ, nội dung file Để trống Tài khoản chuyển",
    "value": "__REMOVE__",
    "expectedResult": "1. Check api trả về:\n  1.1. Status: 200\n  1.2. Response: Bản ghi không hợp lệ, mô tả lỗi: \"Trường Tài khoản chuyển không được để trống\""
  },
  {
    "field": "debitAccount",
    "case": "Kiểm tra truyền file hợp lệ, nội dung file Nhập Tài khoản chuyển 14 ký tự (maxLength)",
    "value": "12345678901234",
    "expectedResult": "1. Check api trả về:\n  1.1. Status: 200\n  1.2. Response: Bản ghi hợp lệ"
  }
]
```

**Workflow:**
1. Read tc-context.json (for preConditionsBase)
2. Read test-design-api.md — extract bullets for fields in FIELD_BATCH
3. For each bullet under `### Trường {fieldName}`:
   - `"field"`: field name (camelCase, from FIELD_BATCH)
   - `"case"`: bullet text exactly as in test-design (this becomes testCaseName)
   - `"value"`: derive from case description (e.g., "Để trống" → `"__REMOVE__"`, "14 ký tự" → `"12345678901234"`, etc.)
   - `"expectedResult"`: copy EXACTLY from the response block under the bullet
4. Write `validate-cases-{BATCH_NUMBER}.json`
5. Run expand_validate.py (same as Phase A Step A2)
6. Write sentinel (same as Phase A Step A3)

<note>Token savings vs Phase B: agent writes ~100 chars/case instead of ~800 chars/case (no preConditions, stepPrefix, testSuiteName repetition). For 30 cases/batch → saves ~20K tokens.</note>

---

### Phase B — Manual template format (fallback / special cases)

Use this approach when:
- The expectedResult requires business logic from test design (not just "Dữ liệu đầu vào không hợp lệ")
- The step description is non-standard
- The case involves cross-field validation with specific error codes

<step id="B1" name="Read tc-context.json">
    <actions>
        <action type="read">
            <file>{TC_CONTEXT_FILE}</file>
        </action>
    </actions>
    <extract_fields>
        <field>preConditionsBase</field>
        <field>catalogStyle</field>
        <field>testAccount</field>
    </extract_fields>
</step>

<step id="B2" name="Read test design file — extract fields in FIELD_BATCH">
    <actions>
        <action type="read">
            <file>{TEST_DESIGN_FILE}</file>
        </action>
    </actions>
    <extraction>
        <section>## Kiểm tra Validate</section>
        <within>Find ### Trường {fieldName} matching fields in FIELD_BATCH</within>
        <case_per_bullet>Each bullet "- Kiểm tra ..." = 1 test case</case_per_bullet>
    </extraction>
</step>

<step id="B3" name="Load validate rules">
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/search.py --ref api-test-case</script>
        </action>
    </actions>
</step>

<step id="B4" name="Generate test cases per field">

    <field_mappings>
        <mapping>
            <output_field>testSuiteName</output_field>
            <template>"Kiểm tra trường {fieldName}"</template>
            <note>Or follow catalogStyle.testSuiteNameConvention</note>
        </mapping>
        <mapping>
            <output_field>testCaseName</output_field>
            <note>Lấy TRỰC TIẾP từ mindmap — KHÔNG dùng "{fieldName}_{mô tả}" hay snake_case</note>
            <example>Mindmap: "- Kiểm tra không truyền ngày quyết định" → testCaseName: "Kiểm tra không truyền ngày quyết định"</example>
        </mapping>
        <mapping>
            <output_field>summary</output_field>
            <rule>EXACTLY match testCaseName</rule>
        </mapping>
        <mapping>
            <output_field>preConditions</output_field>
            <source>tc-context.json preConditionsBase</source>
        </mapping>
        <mapping>
            <output_field>step</output_field>
            <description>Specific change for this case (e.g. "1. Bỏ trống {field}\n2. Send API")</description>
            <source>catalogStyle.stepExample</source>
        </mapping>
        <mapping>
            <output_field>expectedResult</output_field>
            <description>Expected result from response block in test design bullet</description>
            <source>catalogStyle.expectedResultExample</source>
            <response_json_rule>
                If catalogStyle.responseJsonFormat = "multiline":
                  Response JSON phải có \n + indent (2 spaces), VD:
                  "1.2. Response:\n{\n  \"code\": \"ERR_001\",\n  \"message\": \"...\"\n}"
                If catalogStyle.responseJsonFormat = "oneline":
                  Response JSON trên 1 dòng, VD:
                  "1.2. Response: {\"code\":\"ERR_001\",\"message\":\"...\"}"
            </response_json_rule>
        </mapping>
        <mapping>
            <output_field>importance</output_field>
            <value>Medium</value>
        </mapping>
        <mapping>
            <output_field>result</output_field>
            <value>PENDING</value>
        </mapping>
    </field_mappings>
</step>

<step id="B5" name="Per-field checkpoint (STDOUT ONLY)">
    <output_destination>stdout ONLY — NOT to batch file</output_destination>
    <format>
```
✓ Field {fieldName}: {N} cases generated
Missing cases vs mindmap: [list nếu thiếu] → APPEND immediately
```
    </format>
    <action_on_missing>
        APPEND missing cases immediately before moving to next field
    </action_on_missing>
</step>

<step id="B6" name="Write validate-batch-{BATCH_NUMBER}.json — TEMPLATE FORMAT (then write sentinel in B7)">
    <output_file>{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.json</output_file>

    <description>
        ⛔ CRITICAL: Use TEMPLATE FORMAT to avoid repeating preConditions/testSteps in every test case.
        merge_batches.py will expand templates into full test case objects automatically.
    </description>

    <format_constraints>
        <constraint>Write a JSON OBJECT (not array) with two keys: "_template" and "testCases"</constraint>
        <constraint>_template contains shared fields that are IDENTICAL across all test cases in this batch</constraint>
        <constraint>Each testCase contains ONLY the fields that DIFFER per case</constraint>
    </format_constraints>

    <template_format>
```json
{
  "_template": {
    "preConditions": "{preConditionsBase from tc-context.json — write ONCE here}",
    "stepPrefix": "1. Nhập các tham số\n1.1. Authorization: {Token}\n1.2. Method: {METHOD}\n1.3. Param:\n",
    "baseParams": {
      "field1": "validValue1",
      "field2": "validValue2"
    },
    "importance": "Medium",
    "result": "PENDING"
  },
  "testCases": [
    {
      "testCaseName": "Kiểm tra không truyền field1",
      "testSuiteName": "Kiểm tra trường field1",
      "paramOverride": {"field1": "__REMOVE__"},
      "expectedResult": "1. Check api trả về:\n  1.1. Status: 200\n  1.2. Response:\n{\n    \"code\": \"ERR_001\",\n    \"message\": \"...\"\n}"
    },
    {
      "testCaseName": "Kiểm tra truyền null cho field1",
      "testSuiteName": "Kiểm tra trường field1",
      "paramOverride": {"field1": null},
      "expectedResult": "..."
    },
    {
      "testCaseName": "Kiểm tra truyền chuỗi rỗng cho field1",
      "testSuiteName": "Kiểm tra trường field1",
      "paramOverride": {"field1": ""},
      "expectedResult": "..."
    }
  ]
}
```

<note>
testCaseName: Lấy TRỰC TIẾP từ mindmap — KHÔNG dùng snake_case như "field1_Khong_truyen"
Ví dụ đúng: "Kiểm tra không truyền field1", "Kiểm tra truyền null cho field1"
</note>
    </template_format>

    <paramOverride_rules>
        <rule name="remove_field">Use "__REMOVE__" as value to omit the field from request body (for "Không truyền" cases)</rule>
        <rule name="null_value">Use null for null cases</rule>
        <rule name="type_change">Use the actual value: {"field": true} for boolean, {"field": [1]} for array, {"field": {}} for object</rule>
        <rule name="multiple_fields">Can override multiple fields: {"field1": "val", "field2": "val2"} for cross-field tests</rule>
        <rule name="raw_body">For non-object body, use "rawBody" key instead of "paramOverride": {"rawBody": "\"string body\""}</rule>
    </paramOverride_rules>

    <token_savings>
        This format saves ~750 tokens per test case by not repeating preConditions and the unchanged parts of testSteps.
        For a batch of 5 fields × ~20 cases each = 100 cases, this saves ~75,000 tokens per batch.
    </token_savings>
</step>

<step id="B7" name="Write completion sentinel">
    <actions>
        <action type="bash">
            <script>python3 -X utf8 -c "
import os
s = r'{OUTPUT_DIR}/.validate-{BATCH_NUMBER}.done'
open(s, 'w').write('done')
print(f'Sentinel written: {s}')
"</script>
        </action>
    </actions>
    <note>MUST write even if errors occurred in B6. Orchestrator will verify file size separately.</note>
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
        <param name="BATCH_NUMBER" type="number" required="true"/>
        <param name="FIELD_BATCH" type="array" required="true"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>
