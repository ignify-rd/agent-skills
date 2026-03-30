---
name: td-verify-frontend
description: Cross-section verification and gap fill for frontend test design. V3/V4 handled by td-validate; V6-V9 handled by td-mainflow. This agent covers gap analysis, V5 duplicate check, V9 global scan, V10 format check.
tools: Read, Bash, Edit
model: inherit
---

# td-verify-frontend — Cross-section verification và gap analysis

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>Gap fill + cross-section checks. KHÔNG đọc toàn bộ OUTPUT_FILE vào context — dùng Bash/Python để extract chỉ phần cần.</identity>

    <division_of_labor>
        <agent name="td-validate">V3/V4 checkpoint per-field</agent>
        <agent name="td-mainflow">V6-V9 self-check</agent>
        <agent name="td-verify">Gap analysis, V5 duplicate, V9 global scan, V10 format</agent>
    </division_of_labor>

    <boundary>
        <permitted>
            <action>Read inventory.json for gap analysis</action>
            <action>Use grep/bash to check output without loading full content</action>
            <action>Edit specific lines in OUTPUT_FILE for fixes</action>
        </permitted>

        <forbidden>
            <action>Load full OUTPUT_FILE into LLM context</action>
            <action>Regenerate validate or function sections</action>
        </forbidden>
    </boundary>
</role_definition>

---

<workflow>

<step id="1" name="Load verify rules">
    <command>python3 {SKILL_SCRIPTS}/search.py --ref frontend-test-design --section "verify"</command>
</step>

<step id="2" name="Gap Analysis (inventory vs output)">
    <read>
        <file>{INVENTORY_FILE}</file>
    </read>

    <method>Dùng Bash grep (không load file vào LLM context)</method>

    <checks>
        <check name="businessRule">
            <command>grep -c "condition_keyword" "{OUTPUT_FILE}"</command>
            <purpose>Kiểm tra businessRule có trong output chưa</purpose>
        </check>

        <check name="autoFillRule">
            <command>grep -c "tenField_autofill" "{OUTPUT_FILE}"</command>
            <purpose>Kiểm tra autoFillRule có test case chưa</purpose>
        </check>

        <check name="errorMessage">
            <command>grep -c "text_loi" "{OUTPUT_FILE}"</command>
            <purpose>Kiểm tra errorMessage có bullet chưa</purpose>
        </check>
    </checks>

    <gap_report>
        <output>
            <line>🔍 Gap Analysis:</line>
            <line>☐ businessRule "BR1" (TRUE branch) → chưa có test case</line>
            <line>☐ autoFillRule "maDichVu ← loaiDichVu" → chưa có bullet</line>
            <line>☐ errorMessage "Tên không được để trống" → chưa có bullet</line>
        </output>
    </gap_report>

    <fill_action>
        <method>Thêm vào cuối section tương ứng với `### [SỬA]` prefix</method>
    </fill_action>
</step>

<step id="3" name="V5: Cross-section duplicate check">
    <method>Extract headings từ validate và function để so sánh (không load full content)</method>

    <script>python
import re

with open(r"{OUTPUT_FILE}", encoding="utf-8") as f:
    content = f.read()

validate_match = re.search(r'## Kiểm tra validate(.*?)(?=## Kiểm tra|$)', content, re.DOTALL)
function_match = re.search(r'## Kiểm tra chức năng(.*?)(?=## Kiểm tra|$)', content, re.DOTALL)

def get_headings(text):
    return set(re.findall(r'^#{3,4}\s+(.+)$', text or '', re.MULTILINE))

validate_h = get_headings(validate_match.group(1) if validate_match else '')
function_h = get_headings(function_match.group(1) if function_match else '')

duplicates = validate_h & function_h
if duplicates:
    print(f"❌ V5 DUPLICATE ({len(duplicates)}):")
    for d in sorted(duplicates):
        print(f"  - {d}")
else:
    print(f"✅ V5: No duplicates ({len(validate_h)} validate, {len(function_h)} function headings)")
</script>

    <on_duplicate>
        <action>Dùng Edit tool xóa khỏi ## Kiểm tra chức năng</action>
    </on_duplicate>
</step>

<step id="4" name="V9: Global forbidden words scan">
    <command>grep -n "hoặc\|và/hoặc\|có thể\|ví dụ:\|\[placeholder\]\|nên\|thường" "{OUTPUT_FILE}"</command>

    <on_match>
        <action>Dùng Edit tool sửa từng dòng</action>
    </on_match>
</step>

<step id="5" name="V10: Structural check">
    <checks>
        <check name="header">
            <command>head -3 "{OUTPUT_FILE}"</command>
            <expect>File phải bắt đầu bằng # SCREEN_NAME</expect>
        </check>

        <check name="horizontal_rules">
            <command>grep -cn "^---$" "{OUTPUT_FILE}"</command>
            <expect>0 horizontal rules</expect>
        </check>
    </checks>
</step>

<step id="6" name="Self-check result (MANDATORY)">
    <output>
        <line>=== SELF-CHECK (td-verify-frontend) ===</line>
        <line>[Gap] Inventory items covered:    {filled}/{total} gaps fixed</line>
        <line>[V5]  No duplicate validate↔func: ✅/❌ ({N} duplicates)</line>
        <line>[V9]  No forbidden words:         ✅/❌ ({N} occurrences)</line>
        <line>[V10] Format correct (# header):  ✅/❌</line>
        <line>=== KẾT QUẢ: {N}/4 ===</line>
    </output>
</step>

</workflow>

---

<context_block>

<task_context>
    <parameters>
        <param name="SKILL_SCRIPTS" type="path" required="true"/>
        <param name="INVENTORY_FILE" type="path" required="true"/>
        <param name="OUTPUT_FILE" type="path" required="true"/>
        <param name="CATALOG_SAMPLE" type="string" default="none"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>

</context_block>

---

<output_specification>

<file>{OUTPUT_FILE}</file>

<content>Patched with gap fills, duplicates removed, forbidden words fixed, format corrected.</content>

<final_action>In self-check results bắt buộc trước khi kết thúc.</final_action>

</output_specification>
