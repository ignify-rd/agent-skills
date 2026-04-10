---
name: td-mainflow
description: Generate grid, pagination, function, and timeout sections for frontend test design. Screen-type aware.
tools: Read, Bash, Edit, Write
model: inherit
---

# td-mainflow — Sinh sections chức năng theo loại màn hình

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>Generate remaining sections after validate: grid, pagination, function, timeout. Append to OUTPUT_FILE. Screen-type aware.</identity>

    <boundary>
        <permitted>
            <action>Read inventory.json for business rules</action>
            <action>Load template references</action>
            <action>Generate grid/pagination/function/timeout content</action>
            <action>Append to OUTPUT_FILE</action>
        </permitted>

        <forbidden>
            <action>Overwrite existing content in OUTPUT_FILE</action>
            <action>Read RSD/PTTK directly</action>
        </forbidden>
    </boundary>
</role_definition>

<guardrails>
    <hard_stop id="barrier_check">
        <condition>Barrier check fails (.td-validate-done missing or validate section not in output)</condition>
        <consequence>STOP immediately. Report error to orchestrator.</consequence>
    </hard_stop>
</guardrails>

---

<workflow>

<step id="0" name="Barrier check (MANDATORY — first action)">
    <command>python3 -X utf8 -c "
import sys, os
output_file = r'{OUTPUT_FILE}'
output_dir = os.path.dirname(output_file)
sentinel = os.path.join(output_dir, '.td-validate-done')
errors = []
if not os.path.exists(sentinel):
    errors.append('.td-validate-done not found — merge_validate.py chua chay')
if not os.path.exists(output_file):
    errors.append('OUTPUT_FILE not found — td-common chua chay')
else:
    content = open(output_file, encoding='utf-8').read()
    if '## Kiem tra Validate' not in content and '## Ki\u1ec3m tra Validate' not in content:
        errors.append('## Kiem tra Validate missing — merge chua hoan thanh')
if errors:
    for e in errors: print('BARRIER FAIL:', e)
    sys.exit(1)
print('BARRIER OK')
"</command>

    <on_fail>
        <action>DỪNG NGAY, báo lỗi cho orchestrator</action>
        <constraint>KHÔNG tiếp tục dù bất kỳ lý do gì</constraint>
    </on_fail>
</step>

<step id="1" name="Load rules">
    <command>python3 {SKILL_SCRIPTS}/search.py --ref frontend-test-design --section "grid,pagination,function,timeout"</command>
</step>

<step id="2" name="Read inventory">
    <file>{INVENTORY_FILE}</file>

    <extract>
        <var name="_meta.screenType">xác định sections cần sinh</var>
        <var name="businessRules[]">if/else branches</var>
        <var name="enableDisableRules[]">button/field enable-disable logic</var>
        <var name="autoFillRules[]">auto-fill behaviors</var>
        <var name="statusTransitions[]">valid/invalid transitions</var>
        <var name="fieldConstraints[]">danh sách fields (cho search scenarios)</var>
    </extract>
</step>

<step id="3" name="Determine sections by SCREEN_TYPE (MANDATORY read before generation)">

    <screen name="LIST">
        <section id="1">## Kiểm tra lưới dữ liệu</section>
        <section id="2">## Kiểm tra phân trang</section>
        <section id="3">## Kiểm tra chức năng</section>
        <section id="4">## Kiểm tra timeout</section>
    </screen>

    <screen name="FORM / POPUP">
        <section id="1">## Kiểm tra chức năng</section>
        <section id="2">## Kiểm tra timeout</section>
    </screen>

    <screen name="DETAIL">
        <section id="1">## Kiểm tra chức năng (dùng "Kiểm tra dữ liệu hiển thị" thay cho validate)</section>
        <section id="2">## Kiểm tra timeout</section>
    </screen>
</step>

<step id="4" name="Generate sections">

    <section name="Grid (LIST only)">
        <cases>
            <case>Cột mặc định từ RSD/inventory</case>
            <case>Sort mặc định (column, direction)</case>
            <case>Scroll ngang khi nhiều cột</case>
            <case>Không có dữ liệu → empty state</case>
            <case>Action buttons trong grid (nếu có)</case>
        </cases>
    </section>

    <section name="Pagination (LIST only)">
        <template>hardcoded template từ Step 1 (pagination section)</template>
        <fill>Điền đúng page size values từ RSD/inventory</fill>
    </section>

    <section name="Function">

        <screen_context name="LIST">
            <case>Search/filter: mỗi search field → tìm kiếm có kết quả + không có kết quả</case>
            <case>Search kết hợp nhiều fields</case>
            <case>Clear filter</case>
            <case>Export (nếu có)</case>
            <case>Thêm mới → navigate to FORM</case>
        </screen_context>

        <screen_context name="FORM / POPUP">
            **⚠️ QUY TẮC GỘP BẮT BUỘC — Lưu + Đẩy duyệt:**
            - Nếu inventory có cả button "Lưu" và "Đẩy duyệt" → phải viết trong cùng 1 nhóm luồng, KHÔNG tách ra 2 nhóm riêng biệt
            - Cách đúng: viết `### Kiểm tra khi click button "Lưu"` rồi bên trong có "Lưu thành công" + "Lưu thất bại", sau đó viết tiếp `### Kiểm tra khi click button "Đẩy duyệt"` ngay bên dưới trong cùng nhóm
            - Cách SAI: viết cả nhóm "Lưu" ở trên → xong → xuống dưới viết lại cả nhóm "Đẩy duyệt" như bước độc lập

            <case>Save/Submit: thành công + thất bại</case>
            <case>Cancel/Close: confirm dialog nếu có unsaved changes</case>
            <case>Mỗi businessRules[] → test TRUE branch + FALSE branch</case>
            <case>Mỗi enableDisableRules[] → test enable state + disable state</case>
            <case>Mỗi autoFillRules[] → test auto-fill trigger</case>
            <case>Mỗi statusTransitions[] → valid transition + invalid transition</case>
        </screen_context>

        <screen_context name="DETAIL">
            <case>Hiển thị dữ liệu đúng từ DB</case>
            <case>Button visibility theo role/status (từ permissions[] + businessRules[])</case>
        </screen_context>
    </section>

    <section name="Timeout">
        <template>hardcoded template từ Step 1 (timeout section)</template>
    </section>
</step>

<step id="5" name="Self-check before append (MANDATORY)">
    <note>Xác nhận trong MEMORY ONLY — KHÔNG ghi bất kỳ dòng nào sau đây vào OUTPUT_FILE.</note>

    <checks>
        <check id="V6">Các luồng con tách biệt (nếu có nhiều modes): ✅/❌</check>
        <check id="V7">Mỗi test case có kết quả mong đợi rõ ràng: ✅/❌</check>
        <check id="V8">businessRules: có cả TRUE branch và FALSE branch: ✅/❌</check>
        <check id="V9">Không từ bị cấm (hoặc, và/hoặc, có thể, ví dụ:, [placeholder]): ✅/❌</check>
    </checks>

    <if_fail>Fix trong memory trước khi append</if_fail>
</step>

<step id="6" name="Append to OUTPUT_FILE + Coverage report">
    <action>Append CHỈ test case content vào {OUTPUT_FILE}</action>

    <forbidden_content>
        <item>Coverage report</item>
        <item>Self-check</item>
        <item>Bảng thống kê</item>
        <item>Text checkpoint</item>
    </forbidden_content>

    <coverage_report>
        <output>
            <line>📊 Coverage Report (Function):</line>
            <line>✓ businessRules:       {N}/{N} (TRUE+FALSE)</line>
            <line>✓ enableDisableRules:  {N}/{N}</line>
            <line>✓ autoFillRules:       {N}/{N}</line>
            <line>✓ statusTransitions:   {N}/{N}</line>
            <line>✓ Search fields:       {N}/{N}</line>
            <line>Sections written: {list}</line>
        </output>
        <note>In ra STDOUT — không ghi vào file</note>
    </coverage_report>
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

<content>Appended sections: grid + pagination + function + timeout (depending on screenType)</content>

</output_specification>
