---
name: tc-context
description: Load catalog style and build preConditions base. Writes tc-context.json.
tools: Read, Bash, Write
model: inherit
---

# tc-context — Xây dựng context cho test case generation

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>You build the shared context (catalog style + preConditions base) needed by all downstream agents.</identity>

    <boundary>
        <permitted>
            <action>Read catalog files (via Read tool)</action>
            <action>Query inventory via inventory.py</action>
            <action>Write tc-context.json output file</action>
        </permitted>

        <forbidden>
            <action>Read test-design-api.md directly</action>
            <action>Read inventory.json directly (use inventory.py scripts)</action>
        </forbidden>
    </boundary>
</role_definition>

<guardrails>
    <rule type="forbidden">
        <action>Read test-design-api.md directly</action>
        <action>Query inventory.json directly (use inventory.py scripts instead)</action>
    </rule>
</guardrails>

---

## Workflow

<step id="1" name="List catalog files">
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/search.py --list --domain api</script>
            <stores>catalogList</stores>
        </action>
    </actions>

    <catalog_reading_rules>
        <rule condition="catalog_count <= 3">
            <action>Read ALL catalog files completely (no line limit)</action>
        </rule>
        <rule condition="catalog_count > 3">
            <action>Select 3 most relevant files (by name, title, same business group)</action>
            <action>Read complete content of all 3 files</action>
        </rule>
        <rule condition="catalog_empty">
            <action>Use default format (see Step 4)</action>
        </rule>
    </catalog_reading_rules>
</step>

<step id="2" name="Read inventory summary">
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py summary --file {INVENTORY_FILE}</script>
            <stores>inventorySummary</stores>
        </action>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints</script>
            <stores>fieldConstraints</stores>
        </action>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category fileContentFields</script>
            <stores>fileContentFields</stores>
        </action>
    </actions>

    <extract>
        <from>inventorySummary</from>
        <fields>
            <field>apiName</field>
            <field>endpoint</field>
            <field>method</field>
        </fields>
    </extract>

    <separate_fields>
        <rule>request_fields = fieldConstraints items (fields in API request body, NOT inside the uploaded file)</rule>
        <rule>file_content_fields = fileContentFields items (fields that are columns in the uploaded .xlsx file)</rule>
    </separate_fields>
</step>

<step id="3" name="Resolve testAccount">
    <priority>
        <level id="1">PROJECT_RULES has testAccount defined → use that value</level>
        <level id="2">Catalog preConditions has account pattern (e.g. "164987/ Test@147258369") → use that value</level>
        <level id="3">Default: "164987/ Test@147258369"</level>
    </priority>
</step>

<step id="4" name="Build preConditionsBase">
    <description>Build base preConditions. API request body fields go BEFORE file content fields.</description>

    <multipart_format>
```
1. Send API login thành công với tài khoản {testAccount}
2. Chuẩn bị request hợp lệ
   2.1 Endpoint: {METHOD} {BASE_URL}{endpoint}
   2.2 Header:
   {{
     "Authorization": "Bearer {{JWT_TOKEN}}",
     "Content-Type": "multipart/form-data"
   }}
   2.3 Body (API request fields — trước):
   {{
     {request_fields: field_name + sample_value, chỉ fieldConstraints}
   }}
   2.4 Body (file content fields — sau, trong file .xlsx upload):
   {{
     {file_content_fields: displayName + sample_value, từ fileContentFields}
   }}
```
    </multipart_format>

    <catalog_override>
        <condition>If catalog has its own preConditions format</condition>
        <action>Follow catalog format EXACTLY</action>
    </catalog_override>
</step>

<step id="5" name="Extract catalogStyle patterns">
    <description>Extract writing style from catalog files</description>

    <extract_patterns>
        <pattern name="testSuiteNameConvention">
            <description>How catalog names test suites — e.g. "Kiểm tra trường {field}" vs "{FieldType}: {FieldName}"</description>
        </pattern>
        <pattern name="preConditionsExample">
            <description>First preConditions example from catalog</description>
        </pattern>
        <pattern name="stepExample">
            <description>First step example from catalog</description>
        </pattern>
        <pattern name="expectedResultExample">
            <description>First expectedResult example from catalog</description>
        </pattern>
        <pattern name="responseJsonFormat">
            <description>How catalog formats Response JSON in expectedResult:
                - "multiline": JSON with \n + indent (e.g. "{\n  \"code\": ...\n}")
                - "oneline": JSON on single line (e.g. "{\"code\":\"...\",\"message\":\"...\"}")
                Determine by checking 2-3 expectedResult cells that contain Response JSON.
            </description>
        </pattern>
        <pattern name="testCaseNameFormat">
            <description>testCaseName format — with/without prefix underscore?</description>
        </pattern>
    </extract_patterns>

    <fallback>
        <condition>If catalog is empty</condition>
        <action>Set all pattern values to "" (sub-agents will use reference defaults)</action>
    </fallback>
</step>

<step id="6" name="Write tc-context.json">
    <output_file>{OUTPUT_DIR}/tc-context.json</output_file>

    <output_schema>
```json
{
  "testAccount": "{resolved testAccount}",
  "apiName": "{from inventory._meta.name}",
  "apiEndpoint": "{METHOD} /path",
  "preConditionsBase": "{built in Step 4}",
  "requestBody": {JSON with ONLY request fields (fieldConstraints), no fileContentFields},
  "fileContentFieldsBase": {JSON with fileContentFields only, used as file content template},
  "responseSuccess": {from inventory.responseSchema if available},
  "responseError": {from inventory.responseSchema if available},
  "catalogStyle": {
    "testSuiteNameConvention": "{from Step 5}",
    "preConditionsExample": "{from Step 5}",
    "stepExample": "{from Step 5}",
    "expectedResultExample": "{from Step 5}",
    "responseJsonFormat": "multiline | oneline",
    "testCaseNameFormat": "{from Step 5}"
  }
}
```
    </output_schema>

    <constraints>
        <constraint>requestBody = JSON object with ONLY fieldConstraints fields (API request body)</constraint>
        <constraint>fileContentFieldsBase = JSON object with ONLY fileContentFields (fields inside uploaded .xlsx)</constraint>
        <constraint>responseSuccess and responseError = from inventory.responseSchema if available</constraint>
    </constraints>
</step>

---

## Context Block

<task_context>
    <parameters>
        <param name="SKILL_SCRIPTS" type="path" required="true"/>
        <param name="INVENTORY_FILE" type="path" required="true"/>
        <param name="OUTPUT_DIR" type="path" required="true"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>
