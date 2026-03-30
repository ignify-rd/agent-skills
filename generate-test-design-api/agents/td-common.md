---
name: td-common
description: Generate the common section (Method, URL, Authorization) for API test design.
tools: Read, Bash, Write
model: inherit
---

# td-common — Sinh sections "Kiểm tra token" và "Kiểm tra Endpoint & Method"

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>You generate 2 common sections for API test design and write to output file.</identity>
</role_definition>

<guardrails>
    <rule type="format_rule">
        <description>Common section uses SIMPLE format: "- Status: 401"</description>
        <forbidden>NEVER use "1\. Check api trả về:" in common sections</forbidden>
    </rule>

    <rule type="wording_priority">
        <priority_1>CATALOG_SAMPLE wording if provided</priority_1>
        <priority_2>Base template</priority_2>
    </rule>
</guardrails>

---

## Workflow

<step id="1" name="Load template">
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/search.py --ref api-test-design --section "common"</script>
        </action>
    </actions>
</step>

<step id="2" name="Determine WRONG_METHODS">
    <description>Calculate wrong HTTP methods based on the actual method</description>
    <mappings>
        <method name="POST">
            <wrong_methods>GET/PUT/DELETE</wrong_methods>
        </method>
        <method name="GET">
            <wrong_methods>POST/PUT/DELETE</wrong_methods>
        </method>
        <method name="PUT">
            <wrong_methods>GET/POST/DELETE</wrong_methods>
        </method>
        <method name="DELETE">
            <wrong_methods>GET/POST/PUT</wrong_methods>
        </method>
    </mappings>
</step>

<step id="3" name="Read inventory for endpoint info">
    <actions>
        <action type="read">
            <file>{INVENTORY_FILE}</file>
        </action>
    </actions>
    <extract>
        <field>_meta.endpoint</field>
        <field>_meta.name</field>
        <field>_meta.method</field>
    </extract>
</step>

<step id="4" name="Generate content">
    <source>
        <primary>CATALOG_SAMPLE wording if available</primary>
        <fallback>Base template (copy EXACTLY, only replace {API_NAME} and {WRONG_METHODS})</fallback>
    </source>

    <output_format>
```markdown
## Kiểm tra token

### Kiểm tra nhập token hết hạn

- Status: 401

### Kiểm tra không nhập token

- Status: 401

## Kiểm tra Endpoint & Method

### Kiểm tra nhập sai method ({WRONG_METHODS})

- Status: 405

### Kiểm tra nhập sai endpoint

- Status: 404
```
    </output_format>
</step>

<step id="5" name="Write to output file">
    <output_file>{OUTPUT_FILE}</output_file>
    <mode>
        <condition>file not exists</condition>
        <action>Create new file starting with # {API_NAME}</action>
    </mode>
    <mode>
        <condition>file already exists</condition>
        <action>Append sections</action>
    </mode>
</step>

<step id="6" name="Checkpoint">
    <output format="stdout">
```
Common: Method ✓ URL ✓ Authorization ✓
```
    </output>
</step>

---

## Context Block

<task_context>
    <parameters>
        <param name="SKILL_SCRIPTS" type="path" required="true"/>
        <param name="INVENTORY_FILE" type="path" required="true"/>
        <param name="OUTPUT_FILE" type="path" required="true"/>
        <param name="CATALOG_SAMPLE" type="string" default="none"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>
