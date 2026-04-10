---
name: td-extract-fields
description: Extract field definitions, constraints, and validate-related info from RSD/PTTK on Confluence into inventory.json fieldConstraints with rsdConstraints.
tools: Read, Bash, Grep
model: inherit
---

# td-extract-fields — Trích xuất field definitions + rsdConstraints (Confluence)

<role_definition>
    <task_type>sub-agent</task_type>
    <identity>You read RSD and PTTK from Confluence via Atlassian MCP, extract ALL field-related information including validate constraints. You write fieldConstraints (with rsdConstraints), requestSchema, responseSchema, and testData to inventory. You run IN PARALLEL with td-extract-logic — each writes to different inventory categories.</identity>
</role_definition>

<confluence_reading>
    <description>
        Đọc tài liệu RSD/PTTK từ Confluence bằng Atlassian MCP tools (KHÔNG dùng Read tool cho tài liệu).
        
        Cách đọc Confluence page:
        1. Dùng getConfluencePage(cloudId=CLOUD_ID, pageId=PTTK_PAGE_ID) để lấy nội dung PTTK
        2. Dùng getConfluencePage(cloudId=CLOUD_ID, pageId=RSD_PAGE_ID) để lấy nội dung RSD
        3. Nội dung trả về dạng markdown — xử lý như đọc file .md bình thường
        4. Nếu trang có child pages chứa thông tin bổ sung → dùng searchConfluenceUsingCql hoặc getConfluencePage cho từng child page
    </description>
</confluence_reading>

<guardrails>
    <rule type="forbidden">
        <action>Use --data directly with Vietnamese text on Windows (encoding issue)</action>
        <action>Write to categories owned by td-extract-logic: errorCodes, businessRules, modes, dbOperations, externalServices, statusTransitions</action>
    </rule>

    <rule type="file_content_fields">
        <description>
            Khi API có input là MultipartFile (file upload) VÀ PTTK mô tả cấu trúc file template (bảng "Mẫu file upload" hoặc section tương tự):
            → PHẢI trích xuất TẤT CẢ các trường bên trong file template thành `fileContentFields`.
            Đây là các trường mà backend validate khi xử lý nội dung file (job bất đồng bộ hoặc realtime).
            KHÔNG bỏ sót bất kỳ trường nào trong bảng mô tả file template.
        </description>
    </rule>

    <rule type="encoding_workaround">
        <description>On Windows, use patch.json + inventory.py patch instead of --data with Vietnamese text</description>
    </rule>
</guardrails>

---

## Workflow

<step id="1" name="Identify field source documents">
    <description>
        ⚠️ CRITICAL — Before reading any document, understand the document roles from user prompt:

        The user may provide MULTIPLE documents with DIFFERENT purposes:
        - PTTK: API technical spec → contains REQUEST BODY field definitions (camelCase JSON fields)
        - RSD/US doc for validate rules: UI screen spec → contains validation constraints per field
        - RSD/US doc for business logic: feature doc → contains error codes, flow, business rules

        FIELD SOURCE RULE:
        ┌─────────────────────────────────────────────────────────────────┐
        │ fieldConstraints = API REQUEST BODY fields ONLY                 │
        │   Source: PTTK "Request Body" / "Tham số đầu vào" table        │
        │   Field names MUST be camelCase JSON keys (slaVersionId, not   │
        │   "ID phiên bản SLA")                                           │
        │                                                                 │
        │ ❌ NEVER use UI screen field table as fieldConstraints source   │
        │   UI tables have display names ("Tên SLA", "Loại luồng")       │
        │   API body has camelCase keys (slaName, approvalFlowType)       │
        └─────────────────────────────────────────────────────────────────┘

        VALIDATION RULES SOURCE:
        - rsdConstraints = read from whichever doc user says contains validate rules
        - If user says "lấy validate từ US05.2" → read US05.2 for rsdConstraints ONLY
        - Do NOT take field names from that document — only take constraint rules

        IDENTIFY before reading:
        1. Which document has the API Request Body definition? → use for fieldConstraints
        2. Which document has validation rules? → use for rsdConstraints
        3. Which document has business logic/error codes? → pass to td-extract-logic

        If unclear, prioritize: PTTK > API-specific RSD > general RSD
    </description>
</step>

<step id="2" name="Read PTTK from Confluence (if provided) — extract field definitions">
    <condition>If PTTK_PAGE_ID is provided (not "none")</condition>
    <actions>
        <action type="confluence_read">
            <tool>getConfluencePage(cloudId={CLOUD_ID}, pageId={PTTK_PAGE_ID})</tool>
            <purpose>Find the section for API_NAME, extract REQUEST BODY fields with constraints</purpose>
        </action>
    </actions>

    <field_source_identification>
        When reading PTTK, locate the correct table by these markers (in priority order):
        1. Section header matching API_NAME or endpoint
        2. Table labeled "Request Body", "Tham số đầu vào", "Input", "Body"
        3. Table with camelCase field names + type + required columns

        ❌ SKIP these tables — they are NOT API field definitions:
        - UI screen field tables (have "Loại input", "Display", "Readonly" columns)
        - Response body tables
        - Database column tables
        - Tables from a DIFFERENT API section

        ✅ CORRECT source: a table row like:
          | slaVersionId | Long | M | ID phiên bản SLA |
          | currentStatus | Integer | M | Trạng thái hiện tại |

        ❌ WRONG source (UI screen table):
          | Tên SLA | String | Display | Editable | Tối đa 100 ký tự |
          | Loại luồng phê duyệt | String | Display | Editable | ... |
    </field_source_identification>

    <extract>
        <section name="fieldConstraints">
            <field name="name">Field name (camelCase — from API request body, NOT UI display name)</field>
            <field name="type">
                Map EXACTLY from PTTK label — do NOT upgrade types:
                | PTTK says | inventory type |
                |-----------|---------------|
                | Int / Integer / int | Integer |
                | Long / long | Long |
                | String / string / varchar | String |
                | Date / DateTime / date | Date |
                | Boolean / boolean / bool | Boolean |
                | Array / List / array | Array |
                | JSONB / JSON / jsonb | JSONB |
                | Number / Decimal / Float / double | Number |
                | MultipartFile / file upload / File / file | MultipartFile |

                CRITICAL: "Int" → "Integer". NEVER map "Int" to "Long".
                Only use "Long" if PTTK explicitly says "Long".
                CRITICAL: JSONB/JSON fields stay JSONB regardless of required/optional.
                CRITICAL: MultipartFile type is for file upload fields (file input, multipart/form-data). ALWAYS map file upload fields to MultipartFile.
            </field>
            <field name="maxLength">For String fields — character length limit</field>
            <field name="maxDigits">For Integer/Number — digit count limit (e.g. "tối đa 2 chữ số" → maxDigits: 2).
                ⚠️ maxDigits=N means max value = 10^N - 1: N=2 → max=99, N=3 → max=999, N=4 → max=9999.
                Always also set max = 10^N - 1 when maxDigits is derived from "tối đa N chữ số".
            </field>
            <field name="min">Minimum numeric value (e.g. "lớn hơn hoặc bằng 0" → min: 0)</field>
            <field name="max">Maximum numeric value — derive from PTTK constraint text, NOT from example values.
                "tối đa 2 chữ số" (Integer) → max=99. "tối đa 3 chữ số" → max=999.
                "tối đa 999.99" (Decimal, 2dp) → max=999.99.
                ⚠️ Do NOT use boundary test values from RSD examples as the max constraint.
            </field>
            <field name="required">Y/N</field>
            <field name="defaultValue">Default value if any</field>
            <field name="source">PTTK or RSD</field>
            <field name="rsdConstraints">⚠️ CRITICAL — see dedicated section below</field>
        </section>

        <section name="requestSchema">
            <field name="pathParams">path parameters with type/required/constraints</field>
            <field name="queryParams">query parameters</field>
            <field name="bodyParams">All fields from fieldConstraints with full constraints</field>
        </section>

        <section name="responseSchema">
            <description>Response structure success + error from PTTK, with sample values</description>
        </section>

        <section name="testData">
            <description>1 valid sample value per field</description>
        </section>
    </extract>

    <fallback>
        <condition>If no PTTK provided (PTTK_PAGE_ID = "none")</condition>
        <action>Extract API request body field definitions from RSD on Confluence — find the Request Body table, NOT the UI screen table</action>
    </fallback>
</step>

<step id="3" name="Read RSD from Confluence — extract rsdConstraints per field">
    <actions>
        <action type="confluence_read">
            <tool>getConfluencePage(cloudId={CLOUD_ID}, pageId={RSD_PAGE_ID})</tool>
            <purpose>Find validate rules, constraints, allowed values for each field</purpose>
        </action>
    </actions>

    <description>
        For EACH field in fieldConstraints, scan the RSD/PTTK for validate-related constraints.
        Fill the `rsdConstraints` object for each field.
    </description>

    <rsdConstraints_schema>
        <field name="allowNull" type="string|null">
            What happens when null is passed? Values: "error", "success", "default:{value}", or null (unknown)
        </field>
        <field name="allowEmpty" type="boolean|null">
            Does the field accept empty string ""? null = unknown
        </field>
        <field name="allowSpecialChars" type="boolean|null">
            Does the field accept special characters? null = unknown
        </field>
        <field name="allowedChars" type="array|null">
            Specific allowed special characters, e.g. ["_", "-"]. null = not specified
        </field>
        <field name="allowSpaces" type="boolean|null">
            Does the field accept spaces (leading/trailing/middle/all)? null = unknown
        </field>
        <field name="allowAccents" type="boolean|null">
            Does the field accept Vietnamese diacritics? null = unknown
        </field>
        <field name="allowNumbers" type="boolean|null">
            (For String) Does the field accept numeric characters? null = unknown
        </field>
        <field name="allowNegative" type="boolean|null">
            (For Integer/Number) Does the field accept negative values? null = unknown → default error
        </field>
        <field name="allowDecimal" type="boolean|null">
            (For Integer) Does the field accept decimal values? null = unknown → default error
        </field>
        <field name="enumValues" type="array|null">
            Fixed set of allowed values, e.g. ["SAVE", "PUSH"]. null = not enum
        </field>
        <field name="crossFieldRules" type="array">
            Cross-field constraints. Each: {"relatedField": "effectiveDate", "rule": ">=", "errorCode": "LDH_SLA_025"}
        </field>
        <field name="customRules" type="array">
            Other spec-specific rules as plain text, e.g. ["Không cho phép trùng tên SLA", "Tự động trim khoảng trắng"]
        </field>
        <!-- MultipartFile-specific fields -->
        <field name="allowedExtensions" type="array|null">
            (For MultipartFile) Allowed file extensions, e.g. [".xls", ".xlsx"]. null = not specified
        </field>
        <field name="maxFileSizeMB" type="number|null">
            (For MultipartFile) Maximum file size in MB, e.g. 10 for 10MB. null = not specified
        </field>
        <field name="maxRecords" type="number|null">
            (For MultipartFile) Maximum number of rows/records allowed in file. null = not specified
        </field>
        <field name="allowDuplicate" type="boolean|null">
            (For MultipartFile) Whether duplicate filename is allowed. false = error GOV0018. null = unknown → default false
        </field>
    </rsdConstraints_schema>

    <extraction_rules>
        <rule>Scan the spec for EACH field — look for phrases like:
            - "cho phép", "không cho phép", "bắt buộc", "tối đa", "tối thiểu"
            - "ký tự đặc biệt", "khoảng trắng", "tiếng Việt", "dấu"
            - "giá trị hợp lệ", "danh sách giá trị", enum definitions
            - "so sánh với", "lớn hơn", "nhỏ hơn", cross-field references
            - "định dạng", "file", "upload", "dung lượng", "bản ghi", "trùng" (cho MultipartFile)
        </rule>
        <rule>If spec does NOT mention a constraint for a field → set that rsdConstraints field to null</rule>
        <rule>EVERY field MUST have rsdConstraints object — even if all values are null</rule>
        <rule>crossFieldRules and customRules default to empty arrays []</rule>
        <!-- MultipartFile defaults -->
        <rule>MultipartFile: allowDuplicate defaults to false if not specified (default safe = error on duplicate)</rule>
        <rule>MultipartFile: maxFileSizeMB defaults to null if not specified</rule>
        <rule>MultipartFile: maxRecords defaults to null if not specified</rule>
    </extraction_rules>
</step>

<step id="2b" name="Extract file content fields (khi API có MultipartFile input)">
    <condition>Khi fieldConstraints có ít nhất 1 field type = "MultipartFile" VÀ PTTK có section mô tả cấu trúc file template (VD: "Mẫu file upload", bảng mô tả các cột/trường trong file)</condition>

    <description>
        Trích xuất TẤT CẢ trường bên trong file template từ PTTK vào `fileContentFields`.
        Đây là các trường mà user điền trong file Excel/CSV trước khi upload, và backend validate từng trường này.

        ĐỌC KỸ:
        1. Section "Mẫu file upload" (hoặc tương tự) trong PTTK → bảng liệt kê các cột trong file
        2. Section "Logic xử lý" (4.2, 4.3...) trong PTTK → logic validate chi tiết cho từng trường
           - Check tồn tại trong bảng tham số (Mã kho bạc trong TCC_DM_KHOBAC...)
           - Cross-field validation (MST vs CIF login, loại tiền TK vs loại tiền GD...)
           - Conditional required (bắt buộc nếu Nộp thay)
           - Hạn mức, phân quyền TK...
    </description>

    <extract>
        <section name="fileContentFields">
            <description>Mỗi trường trong file template = 1 entry trong fileContentFields</description>
            <field name="name">Tên trường (camelCase, VD: debitAccount, taxCode, taxPayerName)</field>
            <field name="displayName">Tên hiển thị tiếng Việt (VD: "Tài khoản chuyển", "Mã Số thuế người nộp thuế")</field>
            <field name="inputType">
                Loại input trong file template:
                | PTTK nói | inputType |
                |----------|-----------|
                | Text Input | TextInput |
                | Number Input | NumberInput |
                | Date Input | DateInput |
                | Droplist / Click | Droplist |
            </field>
            <field name="required">Y / N / conditional (kèm condition)</field>
            <field name="conditionalRequired">
                Nếu required = conditional → mô tả điều kiện.
                VD: "Bắt buộc nếu bản ghi Nộp thay"
            </field>
            <field name="maxLength">Độ dài tối đa (nếu có)</field>
            <field name="allowedChars">
                Ký tự cho phép nhập (lấy từ mô tả PTTK).
                VD: ["0-9", "A-z", "a-z"] cho Tài khoản chuyển
                VD: ["0-9", "A-z", "a-z", "@", "&", "-", ".", "(", ")", "_", ",", "/"] cho MST
            </field>
            <field name="allowAccents">Cho phép tiếng Việt có dấu (true/false)</field>
            <field name="allowSpaces">Cho phép khoảng trắng (true/false)</field>
            <field name="autoFormat">
                VD: "UPPER CASE", "loại bỏ ký tự điều khiển", "chuẩn hóa khoảng trắng kép"
            </field>
            <field name="leadingZeroRule">
                Quy tắc xử lý số 0 đầu tiên (nếu có).
                VD: "Nhập ký tự ' để giữ số 0. Hệ thống tự động loại bỏ ký tự '"
            </field>
            <field name="referenceTable">
                Bảng tham số / danh sách tham chiếu (cho Droplist).
                VD: "TCC_DM_KHOBAC", "tab MA KBNN trong file excel"
            </field>
            <field name="parentField">
                Trường cha ràng buộc (cho Droplist phụ thuộc).
                VD: Mã cơ quan thu phụ thuộc vào Mã kho bạc đã chọn
            </field>
            <field name="crossFieldRules">
                Các ràng buộc liên trường (từ logic validate section 4.x).
                Mỗi rule: {"relatedField": "...", "rule": "...", "errorMessage": "..."}
                VD:
                - {"relatedField": "loginCifMst", "rule": "MST phải = MST CIF login (Nộp cho DN)", "errorMessage": "Mã số người thuế không khớp"}
                - {"relatedField": "taxCode", "rule": "MST nộp thay != MST nộp thuế", "errorMessage": "Mã số thuế không được giống mã số người nộp thay"}
                - {"relatedField": "debitAccountCurrency", "rule": "loại tiền TK = loại tiền GD", "errorMessage": "..."}
            </field>
            <field name="businessValidation">
                Logic validate nghiệp vụ phức tạp (từ section 4.x PTTK).
                Mỗi rule: {"check": "...", "errorMessage": "...", "source": "PTTK tr.X"}
                VD:
                - {"check": "Mã kho bạc tồn tại và trạng thái hoạt động trong TCC_DM_KHOBAC", "errorMessage": "Mã kho bạc nhà nước không hợp lệ. Vui lòng kiểm tra lại"}
                - {"check": "Số tiền <= hạn mức KH từng giao dịch", "errorMessage": "Vượt hạn mức khách hàng"}
                - {"check": "Kiểm tra tham số xử lý thủ công", "errorMessage": "..."}
                - {"check": "Check trùng bản ghi (MST + Số tờ khai + Mã KB + TK NSNN + CQ thu + Mã chương + NDKT + Sắc thuế + Loại tiền HQ + Loại hình XNK)", "errorMessage": "Có bản ghi trùng lặp"}
            </field>
            <field name="dateFormat">Format ngày (cho DateInput). VD: "dd/mm/yyyy"</field>
            <field name="enumValues">Giá trị cố định (nếu có). VD: ["1 - Doanh nghiệp", "2 - Cá nhân"]</field>
        </section>
    </extract>

    <extraction_rules>
        <rule priority="CRITICAL">
            **STEP A: Tìm section "Mẫu file upload" hoặc "3.1" trong PTTK/RSD**
            - Tìm bảng liệt kê các cột/trường trong file Excel template upload
            - Đây thường là bảng có các cột: STT, Tên trường, Kiểu dữ liệu, Bắt buộc, Giải thích
            - KHÔNG bỏ qua phần này ngay cả khi API input chỉ có 1 field type=MultipartFile
        </rule>

        <rule priority="CRITICAL">
            **STEP B: Đọc KỸ TOÀN BỘ bảng mẫu file — TỪNG HÀNG = 1 fileContentField**
            - Scan từ hàng đầu tiên (sau header) đến hàng cuối cùng
            - Với MỖI hàng trong bảng mẫu file upload:
              * Extract: name (camelCase), displayName, inputType, required, maxLength, allowedChars, ...
              * Không bỏ qua hàng nào (kể cả STT, trường ẩn, trường auto-generated)
            - **ĐẾM tổng số hàng trong bảng** → PHẢI bằng với số fileContentFields extracted
        </rule>

        <rule priority="CRITICAL">
            **STEP C: Đọc section "Logic xử lý" (4.2, 4.3...) để lấy validation rules**
            - Scan section này để tìm các constraint cho từng field:
              * allowedChars: "Ký tự cho phép...", "Chỉ chứa...", "Không có..."
              * crossFieldRules: "MST phải = ", "Nộp thay != ", "loại tiền TK = ", "phụ thuộc vào..."
              * businessValidation: "Tồn tại trong bảng...", "Kiểm tra tham số...", "Hạn mức...", "Phân quyền..."
              * conditional required: "Bắt buộc nếu...", "Không bắt buộc khi..."
            - Map các rule này vào field tương ứng trong fileContentFields[i]
        </rule>

        <rule>Trường auto-generated (STT) → vẫn extract nhưng đánh dấu required = "auto"</rule>
        
        <rule>Trường conditional required → ghi rõ condition trong conditionalRequired field</rule>

        <rule priority="ENFORCEMENT">
            **SANITY CHECK — KHÔNG ĐƯỢC BỎ SÓT:**
            1. Đếm số hàng trong bảng "Mẫu file upload" (VD: 25 hàng)
            2. Đếm số fileContentFields extracted (PHẢI = 25)
            3. Nếu không bằng → **LỖI**: dừng lại và đọc lại bảng cẩn thận
            4. Liệt kê tên fields extracted → so với bảng gốc để kiểm tra từng cái
        </rule>

        <rule>KHÔNG bỏ sót trường nào — hàng nào trong bảng PTTK mà không có trong fileContentFields → **LỖI GIAI ĐOẠN**</rule>
    </extraction_rules>
</step>

<step id="3" name="Write patch.json">
    <output_file>{OUTPUT_DIR}/patch.json</output_file>

    <structure>
```json
{
  "fieldConstraints": [
    {
      "name": "slaName",
      "type": "String",
      "maxLength": 100,
      "required": true,
      "source": "PTTK",
      "rsdConstraints": {
        "allowNull": "error",
        "allowEmpty": false,
        "allowSpecialChars": false,
        "allowedChars": null,
        "allowSpaces": true,
        "allowAccents": true,
        "allowNumbers": true,
        "allowNegative": null,
        "allowDecimal": null,
        "enumValues": null,
        "crossFieldRules": [],
        "customRules": ["Không cho phép trùng tên SLA"]
      }
    }
  ],
  "fileContentFields": [
    {
      "name": "debitAccount",
      "displayName": "Tài khoản chuyển",
      "inputType": "TextInput",
      "required": "Y",
      "conditionalRequired": null,
      "maxLength": 14,
      "allowedChars": ["0-9", "A-z", "a-z"],
      "allowAccents": false,
      "allowSpaces": false,
      "autoFormat": "loại bỏ khoảng trắng kép, ký tự điều khiển",
      "leadingZeroRule": null,
      "referenceTable": null,
      "parentField": null,
      "crossFieldRules": [],
      "businessValidation": [
        {"check": "TK trích nợ phải được phân quyền cho user", "errorMessage": "Tài khoản không được phân quyền"}
      ],
      "dateFormat": null,
      "enumValues": null
    }
  ],
  "requestSchema": {
    "pathParams": [],
    "queryParams": [],
    "bodyParams": []
  },
  "responseSchema": {
    "success": {"status": 200, "body": {}, "sample": {}},
    "error": {"status": 200, "body": {"code": "String", "message": "String"}}
  },
  "testData": [
    {"field": "slaName", "type": "String", "validValue": "SLA Test 001", "note": "tên hợp lệ"}
  ]
}
```
    </structure>

    <critical_rules>
        <rule>EVERY field in fieldConstraints MUST have rsdConstraints object</rule>
        <rule>When MultipartFile detected + PTTK has file template section → fileContentFields MUST be populated with ALL fields from template</rule>
        <rule>Do NOT write errorCodes, businessRules, modes, dbOperations, externalServices, statusTransitions — those belong to td-extract-logic</rule>
    </critical_rules>
</step>

<step id="4" name="Apply patch">
    <actions>
        <action type="bash">
            <script>python3 {SKILL_SCRIPTS}/inventory.py patch \
  --file {INVENTORY_FILE} \
  --patch-file {OUTPUT_DIR}/patch.json</script>
        </action>
    </actions>
</step>

<step id="5" name="Validation checkpoint (STDOUT)">
    <output format="stdout">
```
=== td-extract-fields checkpoint ===
Fields extracted: {N}
Fields with rsdConstraints: {N}/{N}
Fields missing rsdConstraints: [list if any]
fileContentFields: {N} (fields inside uploaded file template)
requestSchema.bodyParams: {N}
responseSchema: success={yes/no}, error={yes/no}
testData: {N} fields
```
    </output>

    <validation_checks>
        <check condition="any field missing rsdConstraints">
            <action>STOP — go back and extract rsdConstraints for missing fields</action>
        </check>
        <check condition="requestSchema.bodyParams = 0">
            <message>Cảnh báo: Không tìm thấy request body params</message>
        </check>
        <check name="ui_vs_api_field_check" condition="ALWAYS">
            <description>Verify extracted fields are API body fields, NOT UI screen fields</description>
            <red_flags>
                - Field names are Vietnamese display names ("Tên SLA", "Loại luồng") → WRONG SOURCE
                - Field names match UI table columns (Display, Editable, Readonly) → WRONG SOURCE
                - Field count matches UI screen row count but mismatches PTTK request body → WRONG SOURCE
            </red_flags>
            <action>If any red flag found → STOP, re-read PTTK to find the correct Request Body table</action>
        </check>
        <check name="field_name_format_check" condition="ALWAYS">
            <description>All fieldConstraint names must be camelCase JSON keys</description>
            <examples_correct>slaVersionId, currentStatus, approvalFlowType, warningYellowPct</examples_correct>
            <examples_wrong>Tên SLA, Loại luồng phê duyệt, warningPercent (if API says warningYellowPct)</examples_wrong>
            <action>If any field name contains spaces or Vietnamese characters → STOP, correct field names from API spec</action>
        </check>
    </validation_checks>
</step>

---

## Context Block

<task_context>
    <parameters>
        <param name="SKILL_SCRIPTS" type="path" required="true"/>
        <param name="INVENTORY_FILE" type="path" required="true"/>
        <param name="OUTPUT_DIR" type="path" required="true"/>
        <param name="CLOUD_ID" type="string" required="true">Atlassian Cloud ID</param>
        <param name="RSD_PAGE_ID" type="string" required="true">Confluence page ID of RSD</param>
        <param name="PTTK_PAGE_ID" type="string" default="none">Confluence page ID of PTTK</param>
        <param name="API_NAME" type="string" required="true"/>
        <param name="METHOD" type="string" required="true"/>
        <param name="PROJECT_RULES" type="string" default="none"/>
    </parameters>
</task_context>
