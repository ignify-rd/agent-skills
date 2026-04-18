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
            <action>Check Jira attachments for DB document (tai lieu DB rieng ngoai PTTK va RSD)</action>
            <action>Read DB document content to extract SQL queries verbatim</action>
        </permitted>

        <forbidden>
            <action>Overwrite existing content in OUTPUT_FILE</action>
            <action>Read RSD/PTTK directly</action>
            <action>Auto-generate SQL placeholders — SQL PHAI lay tu tai lieu DB that su</action>
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

<step id="0.5" name="Load DB document for SQL injection (LIST screens only)">
    <condition>Thuc hien khi SCREEN_TYPE == LIST (xac dinh sau barrier check tu inventory hoac SCREEN_TYPE context)</condition>

    <description>
        Tai lieu DB (ngoai PTTK va RSD) chua cac SQL SELECT dung de kiem tra chuc nang tim kiem.
        Bu^o'c nay tim va tai tai lieu DB de su dung trong Step 4 (Function > LIST).
    </description>

    <check_order>
        <check id="1">Neu DB_DOC_CONTENT duoc truyen vao context → su dung luon, bo qua check Jira.</check>
        <check id="2">Neu DB_DOC_PATH duoc truyen vao context → doc file do.</check>
        <check id="3">Neu khong co gi trong context → kiem tra Jira attachments:
            - Lay danh sach attachments tu Jira issue tuong ung (dung mcp__mcp-atlassian__ tools)
            - Tim file co ten chua "DB" hoac "database" hoac co duoi .pdf/.docx (ngoai file RSD/PTTK)
            - Doc noi dung file do neu tim thay
        </check>
        <check id="4">Neu khong tim thay tai lieu DB → in CANH BAO va TIEP TUC (KHONG dung workflow):
            "WARNING: Khong tim thay tai lieu DB — SQL blocks se bi bo qua trong ## Kiem tra chuc nang.
            inject_sql.py se khong co gi de copy vao test cases. Vui long cung cap tai lieu DB."
        </check>
    </check_order>

    <stores>DB_DOC_CONTENT — noi dung tai lieu DB (hoac "NOT_FOUND")</stores>

    <guardrail>
        TUYET DOI KHONG tu sinh SQL. Neu khong co tai lieu DB → de trong SQL block, KHONG dien placeholder.
        Chi copy SQL verbatim tu tai lieu DB that su.
    </guardrail>
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
            <case>Search/filter: mỗi search field — sinh bullet test case theo loại field (xem naming_rules và format_example bên dưới)</case>
            <case>Search kết hợp nhiều fields</case>
            <case>Clear filter</case>
            <case>Export (nếu có)</case>
            <case>Thêm mới — navigate to FORM</case>

            <naming_rules>
                ⚠️ BẮT BUỘC — Tên bullet (test case name) chỉ mô tả INPUT: truyền gì, giá trị nào.
                KHÔNG được đưa kết quả mong đợi vào tên bullet.

                ĐÚNG:
                - Kiểm tra truyền {tên_field} có giá trị = {giá_trị}
                - Kiểm tra khi nhập {tên_field} tồn tại
                - Kiểm tra khi nhập {tên_field} không tồn tại

                SAI — TUYỆT ĐỐI KHÔNG viết:
                - Kiểm tra {field} = [{value}] → có kết quả        ← SAI (dùng → và [])
                - Kiểm tra {field} = [{value}] → không có kết quả  ← SAI (dùng → và [])
                - Tìm kiếm thành công khi chọn {value}             ← SAI (đưa "thành công" vào tên)

                Quy tắc cho từng loại field:
                - Textbox (freetext): "Kiểm tra khi nhập {tên_field} tồn tại" / "... không tồn tại"
                - Dropdown/Combobox có giá trị enum cố định: mỗi giá trị enum = 1 bullet riêng, format: "Kiểm tra truyền {tên_field} có giá trị = {enum_value}"
                - DateRange: "Kiểm tra tìm kiếm theo {tên_field} với khoảng thời gian hợp lệ" / "... không có kết quả"
            </naming_rules>

            <sql_requirement>
                **BẮT BUỘC — SQL block dưới mỗi ### heading trong ## Kiểm tra chức năng:**

                Sau khi viết xong các bullet test cases dưới mỗi `### heading`, BẮT BUỘC thêm SQL block
                nếu DB_DOC_CONTENT != "NOT_FOUND":

                ```sql
                {SQL SELECT từ DB_DOC_CONTENT tương ứng với chức năng tìm kiếm của heading này}
                ```

                **Quy tắc lấy SQL:**
                - SQL PHẢI copy verbatim từ DB_DOC_CONTENT — KHÔNG tự sinh, KHÔNG paraphrase
                - Tìm SQL phù hợp với chức năng của `### heading` (VD: heading "Tìm kiếm theo Loại yêu cầu"
                  — tìm SQL SELECT có WHERE clause liên quan đến request_type / loại yêu cầu)
                - Nếu DB_DOC_CONTENT có nhiều SQL — chọn SQL phù hợp nhất với heading đó
                - Nếu KHÔNG tìm được SQL phù hợp trong DB_DOC_CONTENT — KHÔNG thêm SQL block,
                  in cảnh báo: "WARNING: Khong tim thay SQL cho heading '{heading}' trong tai lieu DB"
                - Nếu DB_DOC_CONTENT == "NOT_FOUND" — KHÔNG thêm SQL block, KHÔNG thêm placeholder
            </sql_requirement>

            <format_example>
                VÍ DỤ ĐÚNG — Dropdown có enum cố định (VD: requestType = ACTIVATE_CARD, UNLOCK_TRANS, ...):

                ### Tìm kiếm theo Loại yêu cầu
                - Kiểm tra truyền requestType có giá trị = ACTIVATE_CARD
                - Kiểm tra truyền requestType có giá trị = UNLOCK_TRANS
                - Kiểm tra truyền requestType có giá trị = CARD_CREDIT_PAYMENT
                - Kiểm tra truyền requestType có giá trị = BLOCK_CARD

                ```sql
                SELECT * FROM TXN_CARD_REQUEST WHERE REQUEST_TYPE = :requestType
                ```

                VÍ DỤ ĐÚNG — Textbox freetext:

                ### Tìm kiếm theo Mã giao dịch
                - Kiểm tra khi nhập mã giao dịch tồn tại
                - Kiểm tra khi nhập mã giao dịch không tồn tại

                VÍ DỤ SAI — KHÔNG được viết như này:

                ### Tìm kiếm theo Loại yêu cầu
                - Kiểm tra requestType = [ACTIVATE_CARD] → có kết quả       ← SAI
                - Kiểm tra requestType = [ACTIVATE_CARD] → không có kết quả ← SAI
                - Tìm kiếm thành công khi chọn loại yêu cầu hợp lệ          ← SAI (không rõ giá trị nào)

                VÍ DỤ ĐÚNG — Heading KHÔNG có SQL:

                ### Tìm kiếm kết hợp nhiều điều kiện
                - Kiểm tra tìm kiếm khi kết hợp 2 điều kiện có kết quả
                - Kiểm tra tìm kiếm khi kết hợp 2 điều kiện không có kết quả
            </format_example>
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
        <param name="SCREEN_TYPE" type="string" default="LIST">
            Loai man hinh: LIST | FORM | DETAIL — lay tu inventory._meta.screenType hoac truyen tu orchestrator.
            Step 0.5 chi chay khi SCREEN_TYPE == LIST.
        </param>
        <param name="DB_DOC_CONTENT" type="string" default="NOT_FOUND">
            Noi dung tai lieu DB (trich tu file dinh kem Jira). Neu chua co → agent tu kiem tra Jira.
            KHONG tu sinh SQL neu khong co tai lieu nay.
        </param>
        <param name="JIRA_ISSUE_KEY" type="string" default="none">
            Key Jira issue hien tai (VD: CARD4-914) — dung de lay attachments neu DB_DOC_CONTENT chua duoc truyen.
        </param>
    </parameters>
</task_context>

</context_block>

---

<output_specification>

<file>{OUTPUT_FILE}</file>

<content>Appended sections: grid + pagination + function + timeout (depending on screenType)</content>

</output_specification>
