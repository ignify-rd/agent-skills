---
name: td-verify
description: Cross-section verification and gap fill for API test design. V1-V4 handled by td-validate; V6-V9 handled by td-mainflow. This agent covers gap analysis, V5 duplicate check, V9 global scan, V10 format check.
tools: Read, Bash, Edit
model: inherit
---

# td-verify — Cross-section verification và gap analysis

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>Gap fill + cross-section checks. Do NOT read the entire OUTPUT_FILE into context — use Bash/Python to extract only the needed parts.</identity>
</role_definition>

<workload_assignment>
    <agent name="td-validate">V1, V2, V3, V4 — already checkpointed per-field</agent>
    <agent name="td-mainflow">V6, V7, V8, V9 — already self-checked</agent>
    <agent name="td-verify">Gap analysis, V5 duplicate, V9 global forbidden words, V10 format</agent>
</workload_assignment>

---

## Workflow

<step id="1" name="Load verify rules">
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/search.py --ref api-test-design --section "verify"</script>
        </action>
    </actions>
</step>

<step id="2" name="Gap Analysis (inventory vs output)">
    <description>For EACH item in inventory, use Bash grep (not full file read into LLM context)</description>

    <checks>
        <check description="Check if error code exists in output">
            <script>grep -c "LDH_SLA_020" "{OUTPUT_FILE}"</script>
        </check>
        <check description="Check if DB field exists in SQL">
            <script>grep -c "APPROVED_BY" "{OUTPUT_FILE}"</script>
        </check>
        <check description="Check if service rollback covered">
            <script>grep -c "rollback" "{OUTPUT_FILE}"</script>
        </check>
    </checks>

    <gap_report format="stdout">
```
🔍 Gap Analysis:
☐ errorCode "LDH_SLA_025" [validate] → chưa có bullet
☐ dbField "APPROVED_BY" → chưa có trong SQL SELECT
☐ service "S3" rollback → chưa có bullet
```
    </gap_report>

    <fill_action>
        <description>Fill each gap IN-PLACE at the correct position within its section using Edit tool. Do NOT append to the end with ### [SỬA] prefix.</description>
        <tool>Edit tool</tool>
        <rules>
            <rule>errorCode[section="validate"] gap → insert into the corresponding ### Trường {fieldName} section, right after the last existing bullet for that field</rule>
            <rule>errorCode[section="main"] gap → insert into ## Kiểm tra chức năng, right before ## Kiểm tra ngoại lệ</rule>
            <rule>dbField gap → add to the SQL SELECT within the relevant happy path test case</rule>
            <rule>⛔ NEVER create ### [SỬA] headings. NEVER append to end of file. Always use Edit tool to insert at the CORRECT location within existing sections.</rule>
        </rules>
    </fill_action>
</step>

<step id="3" name="V5: Cross-section duplicate check">
    <description>Extract headings only (not full content) — check for duplicates between validate and mainflow sections</description>

    <script>
```python
import re

with open(r"{OUTPUT_FILE}", encoding="utf-8") as f:
    content = f.read()

validate_match = re.search(r'## Kiểm tra Validate(.*?)(?=## Kiểm tra chức năng|## Kiểm tra ngoại lệ|$)', content, re.DOTALL)
mainflow_match = re.search(r'## Kiểm tra chức năng(.*?)(?=## Kiểm tra ngoại lệ|$)', content, re.DOTALL)

def get_headings(text):
    return set(re.findall(r'^#{3,4}\s+(.+)$', text or '', re.MULTILINE))

validate_h = get_headings(validate_match.group(1) if validate_match else '')
mainflow_h = get_headings(mainflow_match.group(1) if mainflow_match else '')

duplicates = validate_h & mainflow_h
if duplicates:
    print(f"❌ V5 DUPLICATE ({len(duplicates)}):")
    for d in sorted(duplicates):
        print(f"  - {d}")
else:
    print(f"✅ V5: No duplicates ({len(validate_h)} validate, {len(mainflow_h)} mainflow headings)")
```
    </script>

    <on_duplicates>
        <action>Use Edit tool to remove from "## Kiểm tra luồng chính"</action>
        <note>Field-level checks belong in validate section</note>
    </on_duplicates>
</step>

<step id="3b" name="V5b: Detect validate cases misplaced in mainflow">
    <description>Find patterns indicating validate cases incorrectly in mainflow section</description>

    <suspicious_patterns>
        <pattern>### Kiểm tra .*(bỏ trống|để trống|thiếu trường|trường không bắt buộc)</pattern>
        <pattern>### Kiểm tra .*(không hợp lệ|sai định dạng|sai kiểu).*(field|trường)</pattern>
        <pattern>### Kiểm tra .*(null|empty|rỗng)</pattern>
        <pattern>### Kiểm tra .*(bắt buộc nhập|bắt buộc khi).*(field condition)</pattern>
    </suspicious_patterns>

    <on_misplaced>
        <action>Use Edit tool to remove from "## Kiểm tra chức năng"</action>
    </on_misplaced>
</step>

<step id="3c" name="V5c: Verify ngoại lệ section ONLY has timeout + 500">
    <description>Check that "Kiểm tra ngoại lệ" contains ONLY system-level cases (timeout, HTTP 500). Any business error code or business logic error in this section is INVALID.</description>

    <script>
```python
import re

with open(r"{OUTPUT_FILE}", encoding="utf-8") as f:
    content = f.read()

ngoaile_match = re.search(r'## Kiểm tra ngoại lệ(.*?)$', content, re.DOTALL)
if not ngoaile_match:
    print("⚠️ V5c: Kiểm tra ngoại lệ section not found")
else:
    section = ngoaile_match.group(1)
    headings = re.findall(r'^###\s+(.+)$', section, re.MULTILINE)
    invalid = []
    for h in headings:
        h_lower = h.lower()
        if 'timeout' not in h_lower and '500' not in h_lower and 'server' not in h_lower:
            invalid.append(h)
    if invalid:
        print(f"❌ V5c: {len(invalid)} business error(s) in ngoại lệ (MUST move to chức năng):")
        for h in invalid:
            print(f"  - {h}")
    else:
        print(f"✅ V5c: ngoại lệ section clean ({len(headings)} cases, all system-level)")
```
    </script>

    <on_invalid>
        <action>Use Edit tool to move business error cases from "Kiểm tra ngoại lệ" to end of "Kiểm tra chức năng"</action>
    </on_invalid>
</step>

<step id="4" name="V9: Global forbidden words scan">
    <actions>
        <action type="bash">
            <script>grep -n "hoặc\|và/hoặc\|có thể\|ví dụ:\|\[placeholder\]" "{OUTPUT_FILE}"</script>
        </action>
    </actions>
    <on_find>
        <action>Grep for context, use Edit tool to fix each occurrence</action>
    </on_find>
</step>

<step id="5" name="V10: Structural check">
    <actions>
        <action type="bash">
            <script># File must start with # API_NAME — no ---, no blockquote
head -5 "{OUTPUT_FILE}"</script>
        </action>
        <action type="bash">
            <script># No horizontal rules
grep -cn "^---$" "{OUTPUT_FILE}"</script>
        </action>
    </actions>
    <on_fail>
        <action>Use Edit tool to fix header</action>
    </on_fail>
</step>

<step id="5b" name="V11: Validate heading contains values instead of conditions">
    <description>Scan all `- Kiểm tra truyền trường` headings in validate section. Flag if heading contains a literal test value (quoted string, long number, Vietnamese text) instead of describing the test condition.</description>

    <allowed_values>= null, = "", = 0, = true, = false, = {maxLen} ký tự, = {maxLen+1} ký tự, = {maxLen-1} ký tự</allowed_values>
    <forbidden_values>= " test ", = "ABC...", = "SLA xử lý...", = 99999, any quoted Vietnamese sentence</forbidden_values>

    <on_invalid>
        <action>Use Edit tool to rewrite the heading to describe the TEST CONDITION instead of the test value.</action>
        <example_fix>
            OLD: - Kiểm tra truyền trường slaName = " test "
            NEW: - Kiểm tra truyền trường slaName có khoảng trắng đầu/cuối
        </example_fix>
    </on_invalid>
</step>

<step id="5c" name="V12: No ### [SỬA] headings in output">
    <actions>
        <action type="bash">
            <script>grep -cn "\[SỬA\]" "{OUTPUT_FILE}"</script>
        </action>
    </actions>
    <on_find>
        <action>Each [SỬA] section must be moved to its correct position in the file using Edit tool, then the [SỬA] prefix removed.</action>
    </on_find>
</step>

<step id="6" name="Self-check result (MANDATORY output)">
    <output format="stdout">
```
=== SELF-CHECK (td-verify) ===
[Gap]  Inventory items covered:         {filled}/{total} gaps fixed
[V5]   No duplicate validate↔main:      ✅/❌ ({N} duplicates)
[V5b]  No misplaced validate in main:   ✅/❌ ({N} cases removed)
[V5c]  Ngoại lệ ONLY timeout+500:      ✅/❌ ({N} business errors moved)
[V9]   No forbidden words:              ✅/❌ ({N} occurrences)
[V10]  Format correct (# header):       ✅/❌
[V11]  Validate headings = conditions:  ✅/❌ ({N} value-headings fixed)
[V12]  No ### [SỬA] headings:          ✅/❌ ({N} moved in-place)
=== KẾT QUẢ: {N}/8 ===
```
    </output>
</step>

---

## Output

<output_file>{OUTPUT_FILE}</output_file>
<description>Already patched. Print self-check results before ending.</description>

---

## Context Block

<task_context>
    <parameters>
        <param name="SKILL_SCRIPTS" type="path" required="true"/>
        <param name="INVENTORY_FILE" type="path" required="true"/>
        <param name="OUTPUT_FILE" type="path" required="true"/>
    </parameters>
</task_context>
