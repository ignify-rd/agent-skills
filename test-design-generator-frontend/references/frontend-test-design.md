# Frontend Test Design — Hướng dẫn sinh chi tiết

> **Quy tắc ưu tiên nguồn dữ liệu**: Xem `--ref priority-rules`

## Pipeline tổng thể

```
Phase 1:  Phân tích hình ảnh (nếu có) → consolidate → bổ sung vào UI structure
Phase 2:  Extract UI structure từ RSD → JSON (screenName, screenType, permissions, UI layout, business logic)
Phase 3:  Extract fields từ PTTK (if available) → REPLACE field definitions từ RSD (PTTK wins hoàn toàn)
Phase 4:  Generate validate section (per-field templates + LLM extra business cases)
Phase 5:  Generate lưới dữ liệu section (LLM) + chức năng section (LLM)
Phase 6:  Verify & supplement chức năng against RSD (LLM re-read)
Phase 7:  Combine with base template (common UI, permissions, pagination, timeout)
Phase 8:  Validate and fix markdown
```

## Base Template (8 placeholders)

```markdown
# {SCREEN_NAME}

{COMMON_UI_SECTION}

{PERMISSION_SECTION}

## Kiểm tra validate

{VALIDATE_SECTION}

{GRID_SECTION}

{PAGINATION_SECTION}

{FUNCTION_SECTION}

{TIMEOUT_SECTION}
```

**DETAIL screen:** Rename `## Kiểm tra validate` → `## Kiểm tra dữ liệu hiển thị`

## Phase 1: Phân tích hình ảnh (nếu có screenshots/wireframes)

Tương ứng với logic trong ứng dụng tại `rsd-to-mindmap-frontend.vue` — service `preImageAnalysisService`.

### Khi nào áp dụng

Áp dụng khi user cung cấp hình ảnh (screenshots, wireframes, figma exports) cùng với RSD.

### Bước 1: Phân tích từng hình ảnh độc lập

Với **mỗi hình ảnh**, phân tích và trích xuất:

```json
{
  "imageIndex": 0,
  "platform": "web",
  "screenType": "LIST | FORM | POPUP | DETAIL | UNKNOWN",
  "screenName": "Tên màn hình đoán từ hình",
  "buttons": ["Tìm kiếm", "Thêm mới", "Xuất Excel"],
  "inputFields": [
    {"label": "Tên trường", "type": "textbox | dropdown | combobox | toggle | checkbox", "placeholder": "...", "location": "form | filter | popup | grid"}
  ],
  "gridColumns": ["STT", "Tên cột 1", "Tên cột 2"],
  "hasPagination": true,
  "navigationElements": ["breadcrumb path", "tab names"],
  "uiComponents": ["table", "modal", "tabs", "accordion"],
  "confidence": 0.85,
  "notes": "Ghi chú về những phần không rõ"
}
```

### Bước 2: Consolidate tất cả phân tích hình ảnh

Sau khi phân tích từng ảnh, tổng hợp lại thành một cấu trúc duy nhất:

1. **Gộp** các field/button trùng nhau từ nhiều ảnh
2. **Lọc bỏ** các UI component không liên quan đến yêu cầu trong RSD
3. **Ưu tiên RSD** nếu có conflict với hình ảnh (hình ảnh chỉ là bổ sung)
4. Kết quả consolidate là **input bổ sung** cho Phase 0

```json
{
  "consolidatedScreens": [
    {
      "screenName": "Tên màn hình chính",
      "screenType": "LIST | FORM | POPUP | DETAIL",
      "inputFields": [...],
      "buttons": [...],
      "gridColumns": [...],
      "hasPagination": true,
      "navigationElements": [...]
    }
  ],
  "additionalUIDetails": [
    "Placeholder thực tế: 'Nhập tên...'",
    "Button Xóa chỉ hiện khi có quyền DELETE",
    "Dropdown có icon X để clear"
  ],
  "confidence": 0.9
}
```

### Bước 3: Merge với RSD extraction (Phase 2)

**Nguyên tắc merge**: Theo `--ref priority-rules`. Hình ảnh chỉ bổ sung, không override PTTK/RSD.

**Merge rules:**
- Hình ảnh **KHÔNG ĐƯỢC** override bất kỳ thông tin nào từ RSD/PTTK bao gồm: field names, **maxLength, minLength, data types, required/optional, format constraints, enum values, validation rules**
- Hình ảnh **CHỈ ĐƯỢC** bổ sung những thông tin RSD/PTTK không đề cập: placeholder thực tế, hasIconX, button labels, vị trí field
- Hình ảnh **CÓ THỂ** phát hiện thêm: fields hoặc buttons không được đề cập trong RSD → **hỏi user trước khi thêm**
- Nếu hình ảnh hiện field không có trong RSD → note lại trong `additionalFeatures`, KHÔNG tự ý thêm vào test design
- **⚠️ Nếu conflict** (ví dụ: ảnh gợi ý maxLength=100 nhưng RSD ghi maxLength=200) → **LUÔN dùng RSD/PTTK**

### Ví dụ: Hình ảnh bổ sung gì cho RSD

```
RSD nói: "Dropdown Trạng thái"
→ Hình ảnh xác nhận thêm: hasIconX=true, placeholder="Chọn trạng thái", position=filter

RSD nói: "Textbox Tên dịch vụ, maxLength=100"
→ Hình ảnh xác nhận thêm: placeholder="Nhập tên dịch vụ", hasIconX=true

RSD không đề cập button "Xuất Excel"
→ Hình ảnh thấy button "Xuất Excel" → NOTE lại, KHÔNG tự thêm vào test design
```

---

## Phase 2: Trích xuất cấu trúc UI từ RSD

Theo `priority-rules.md`: khi có PTTK chỉ lấy từ RSD business logic/screen structure. Khi không có PTTK, lấy tất cả.

Đọc RSD và trích xuất JSON đầy đủ:

```json
{
  "screenName": "Tên đầy đủ (VD: WEB_BO_Danh mục > Dịch vụ thu phí)",
  "screenTitle": "Tiêu đề hiển thị",
  "screenType": "LIST | FORM | POPUP | DETAIL",
  "breadcrumb": "Đường dẫn breadcrumb hoặc null",
  "elements": [
    "Liệt kê TẤT CẢ phần tử UI:",
    "Textbox - Mã dịch vụ",
    "Dropdown list - Trạng thái",
    "Button - Tìm kiếm",
    "Lưới dữ liệu",
    "Phân trang"
  ],
  "fields": [
    {
      "name": "Tên field hiển thị",
      "type": "textbox | combobox | dropdown | searchable_dropdown | toggle | checkbox | button | icon_x | date | daterange | textarea | number | radio | file_upload | password | tag_input | richtext",
      "placeholder": "Placeholder text hoặc null",
      "maxLength": null,
      "allowSpecialChars": false,
      "allowSpaces": true,
      "isRequired": false,
      "isSingleSelect": true,
      "hasIconX": true,
      "isReadOnly": false,
      "apiEndpoint": "API endpoint nếu có",
      "values": ["Giá trị cố định nếu có"],
      "dataFormat": "Format hiển thị (VD: Mã - Tên)",
      "dbQuery": "SQL query nếu RSD đề cập",
      "warningMessage": "Cảnh báo khi vượt maxLength",
      "searchDescription": "Mô tả khi nhập 1 phần ký tự",
      "searchRealtimeDesc": "Mô tả tìm kiếm realtime",
      "allowSearchSpecialChars": false,
      "maxSearchLength": 100,
      "defaultValueDesc": "Mô tả giá trị mặc định (cho toggle)",
      "transitions": [{"from": "A", "to": "B", "description": "Hành vi chuyển đổi"}],
      "text": "Text hiển thị trên button",
      "alwaysEnabled": true,
      "closeResult": "Kết quả khi nhấn đóng (cho icon X)",
      "requiresDeletePermission": false
    }
  ],
  "grid": {
    "name": "Tên lưới dữ liệu",
    "columns": [
      {
        "name": "Tên cột hiển thị",
        "fieldName": "Tên field API/response",
        "dbColumn": "Tên cột DB (UPPERCASE)",
        "dbTable": "Tên bảng DB",
        "format": "Định dạng hiển thị (DD/MM/YYYY)",
        "description": "Mô tả thêm",
        "dbQuery": "SQL query cụ thể cho cột này"
      }
    ],
    "pinnedColumns": ["Cột cố định khi cuộn ngang"],
    "sortOrder": "CREATED_TIME DESC",
    "dbTable": "Bảng DB chính",
    "defaultEmpty": "Mô tả khi lưới trống"
  },
  "pagination": {"values": [5, 10, 20], "defaultValue": 5},
  "permissions": {
    "noPermissionResult": "Không view được màn hình",
    "hasPermissionDesc": "Kiểm tra login user có quyền",
    "hasPermissionResult": "User có quyền thao tác chức năng truy vấn"
  },
  "buttonVisibilityRules": [
    {
      "buttonName": "Chỉnh sửa",
      "visibleCondition": "status != 5",
      "hiddenCondition": "status = 5",
      "statusCases": [
        {"status": "5", "visible": false, "description": "Không hiển thị khi status = 5"},
        {"status": "1", "visible": true, "description": "Hiển thị khi status = 1"}
      ]
    }
  ],
  "sections": [
    {
      "name": "Tên section (chỉ DETAIL screen)",
      "type": "fields | grid",
      "fields": [{"name": "...", "dbColumn": "...", "dbTable": "...", "dbQuery": "...", "rsdDescription": "..."}],
      "columns": [{"name": "...", "dbColumn": "...", "dbTable": "...", "dbQuery": "...", "rsdDescription": "..."}]
    }
  ],
  "hasCheckbox": false,
  "searchEndpoint": "API endpoint tìm kiếm",
  "additionalFeatures": ["clear_filter", "back_navigation", "delete", "create"]
}
```

## {COMMON_UI_SECTION} — Kiểm tra giao diện chung

Hardcoded template:

```markdown
## Kiểm tra giao diện chung

### Kiểm tra điều hướng đến màn hình {screenTitle}

- Điều hướng thành công đến màn hình {screenTitle}

### Kiểm tra bố cục giao diện tổng thể

- + Hiển thị theo đúng figma
  + Màn hình {screenTitle} hiển thị đầy đủ các thông tin:
  + {element 1}
  + {element 2}
  + ...

### Kiểm tra hiển thị breadcrumb

- {breadcrumb}

### Kiểm tra hiển thị bố cục layout cân đối

- Hiển thị đúng cỡ chữ, màu chữ, bố cục cân đối, kích thước chính xác, đúng chính tả

### Kiểm tra phóng to/thu nhỏ

- Màn hình không bị vỡ form
```

Cho DETAIL screen: thêm section display tests:
```markdown
### Kiểm tra hiển thị Section "{section.name}"

- Hiển thị đầy đủ Section "{section.name}" với các trường dữ liệu theo thiết kế
```

## {PERMISSION_SECTION} — Kiểm tra phân quyền

```markdown
## Kiểm tra phân quyền

### Kiểm tra login user không có quyền

- {noPermissionResult}

### {hasPermissionDesc}

- {hasPermissionResult}
```

## {VALIDATE_SECTION} — Phase 4

### Cho LIST/FORM/POPUP screens

Sử dụng per-field templates từ `field-templates.md`. Dispatch theo field type:

| field.type | Template function |
|-----------|-------------------|
| textbox, text, input | generateTextboxTests |
| combobox, searchable_combobox | generateComboboxTests |
| dropdown, select (có values[]) | generateSimpleDropdownTests |
| dropdown, select (có apiEndpoint) | generateSearchableDropdownTests |
| toggle, toggle_button, switch | generateToggleTests |
| checkbox | generateCheckboxTests |
| button | generateButtonTests |
| icon_x, icon_close | generateIconXTests |
| date, datepicker | generateDatePickerTests |
| daterange, date_range | generateDateRangePickerTests |
| textarea, multiline | generateTextareaTests |
| number, number_input | generateNumberInputTests |
| radio, radio_group | generateRadioButtonTests |
| file, file_upload, upload | generateFileUploadTests |
| password, password_input | generatePasswordInputTests |
| tag, tag_input, chip | generateTagInputTests |
| richtext, rich_text_editor | generateRichTextEditorTests |
| Unknown type | Fallback → generateTextboxTests |

Sau khi generate tất cả field templates → gọi LLM để tìm **extra business validation** không có trong template:
- Cross-field validation (field A phụ thuộc field B)
- Giá trị đặc biệt (mã 990000 không cho sửa)
- Cascading fields
- Auto-fill rules

### Cho DETAIL screens

KHÔNG dùng field templates. Thay bằng `generateDetailDataSection()`:

```markdown
### {Section Name}

- Kiểm tra bố cục {section name} hiển thị dạng [layout theo figma]
    - Hiển thị đúng bố cục theo thiết kế

- Kiểm tra khi trường có giá trị null / rỗng
    - Ẩn trường hoặc hiển thị "--"

- Kiểm tra dữ liệu hiển thị "{field name}"
    - {rsdDescription} do server trả về ở API {screenTitle}
        - {SQL query SELECT ... FROM ... WHERE ...}
```

## {GRID_SECTION} — Phase 5 (LIST screens only)

```markdown
## Kiểm tra lưới dữ liệu

### Kiểm tra mặc định
- [Trạng thái mặc định — server trả list trống hoặc hiện data]

### Kiểm tra hiển thị sắp xếp các bản ghi trên lưới dữ liệu
- [Sort order + SQL]

### Kiểm tra cột "{column.name}"
- Hiển thị thông tin {fieldName} do server trả về theo DB:
    - {SQL query SELECT column FROM table WHERE... ORDER BY...}
- [Format đặc biệt nếu có]

### Kiểm tra lưới dữ liệu khi kéo thanh cuộn ngang
- Khi cuộn ngang cố định các cột: {pinnedColumns}

### Kiểm tra lưới dữ liệu khi kéo thanh cuộn dọc
- [Mô tả hành vi cuộn dọc]

### Kiểm tra dữ liệu trả về từ server
- [Verify data]
```

**SQL rules:**
- SELECT cụ thể, FROM, WHERE (GIÁ TRỊ MẪU: WHERE ID = 10000001), ORDER BY
- TUYỆT ĐỐI KHÔNG dùng placeholder: [param], {param}, :param
- Tên bảng schema-qualified, tên cột UPPERCASE

**Bỏ qua** grid section cho DETAIL screens (data đã trong validate).

## {PAGINATION_SECTION} — Hardcoded template

```markdown
## Kiểm tra "Phân trang"

### Kiểm tra giá trị phân trang khi không có dữ liệu
- Ẩn lưới dữ liệu

### Kiểm tra các giá trị số lượng bản ghi /trang
- Danh mục giá trị gồm:
    - {value1}/Trang
    - {value2}/Trang
    - {value3}/Trang

### Kiểm tra giá trị phân trang mặc định
- Mặc định là {defaultValue}

### Kiểm tra khi chọn giá trị là {value1}
- Hiển thị {value1} bản ghi / trang

### Kiểm tra khi chọn giá trị là {value2}
- Hiển thị {value2} bản ghi / trang

### Kiểm tra khi chọn giá trị là {value3}
- Hiển thị {value3} bản ghi / trang

### Kiểm tra khi thay đổi lựa chọn đổi số lượng phân trang
- Client reload tìm kiếm và hiển thị grid giao dịch theo giá trị phân trang mới.

### Kiểm tra hiển thị số lượng bản ghi khi thay đổi số lượng phân trang
- Hiển thị tương ứng với tổng số lượng bản ghi server trả/ {số lượng bản ghi/trang}

### Kiểm tra khi click vào số trang
- Hiển thị danh sách các bản ghi ở trang đã chọn

### Kiểm tra khi click > khi đang ở trang 1
- Cho phép chuyển đến trang tiếp theo

### Kiểm tra khi click < khi đang ở trang 1
- Button < bị disable

### Kiểm tra khi click > khi đang ở trang khác trang 1
- Cho phép chuyển đến trang tiếp theo

### Kiểm tra khi click < khi đang ở trang khác trang 1
- Cho phép chuyển đến trang trước đó

### Kiểm tra khi click > khi đang ở trang cuối cùng
- Button > bị disable
```

Chỉ sinh khi `pagination` exists trong UI structure.

## {FUNCTION_SECTION} — Phase 5 (LLM-generated)

Nội dung thay đổi tùy **screenType**:

### Cho LIST screens

```markdown
## Kiểm tra chức năng

### Kiểm tra khi click button "Tìm kiếm"

#### {Field 1}
- Kiểm tra khi nhập {field 1} tồn tại
    - Hiển thị thông tin match + SQL
- Kiểm tra khi nhập {field 1} không tồn tại
    - Danh sách rỗng
- Kiểm tra khi nhập 1 phần {field 1}
    - Hiển thị kết quả chứa + SQL LIKE

#### {Field 2}
...

### Kiểm tra kết hợp tương tác giữa các fields
- Kiểm tra khi chọn {dropdown A} = "X" + nhập {textbox B} = "Y"
    - Hiển thị kết quả thỏa mãn cả 2 điều kiện
    - SQL: WHERE FIELD_A = 'X' AND FIELD_B = 'Y'

### Kiểm tra tìm kiếm kết hợp tất cả các tiêu chí
- Kiểm tra khi điền/chọn tất cả các tiêu chí
    - Hiển thị dữ liệu match + SQL kết hợp tất cả WHERE conditions

### Kiểm tra click icon "Xóa bộ lọc" (nếu có)
- Xóa toàn bộ giá trị, reset về trạng thái ban đầu

### Kiểm tra click button "Thêm mới" (nếu có)
- Điều hướng đến màn hình Thêm mới
```

### Cho FORM/POPUP screens

```markdown
## Kiểm tra chức năng

### Kiểm tra khi click button "Lưu"
- Test validate tổng hợp (bỏ trống required fields)
- Test lưu thành công → toast thông báo
- Test lưu thất bại → hiển thị lỗi

### Kiểm tra kết hợp tương tác giữa các fields
- Enable/disable fields dựa vào giá trị field khác
- Auto-fill / auto-calculate
- Dependent validation
- Business rules với nhiều điều kiện

### Kiểm tra khi click button "Hủy"
- Đóng popup / quay về màn hình trước
```

### Cho DETAIL screens

```markdown
## Kiểm tra chức năng

### Kiểm tra hiển thị cụm chức năng
- Kiểm tra khi user có quyền UPDATE: hiển thị button "Chỉnh sửa"
- Kiểm tra khi user không có quyền UPDATE: ẩn button
- Kiểm tra khi bản ghi có status = {value}: {visible/hidden}

### Kiểm tra khi click button "Chỉnh sửa"
- Điều hướng đến màn hình Chỉnh sửa

### Kiểm tra khi click icon Quay lại (<)
- Quay lại màn hình danh sách trước đó
```

**DETAIL screen rules:**
- KHÔNG test validate input (read-only)
- KHÔNG tạo section timeout (đã có riêng)
- KHÔNG tạo section phân trang (đã có riêng)
- CHỈ test: hiển thị/ẩn button theo quyền/status + click button + điều hướng

## {TIMEOUT_SECTION} — Hardcoded template

```markdown
## Kiểm tra timeout

### Kiểm tra khi server không nhận được phản hồi

- Hiển thị popup thông báo lỗi:

    - + Icon x
      + Tiêu đề: "Lỗi"
      + Nội dung: <Mã lỗi> : <Mô tả lỗi Server trả>
      + Button: Đóng

### Kiểm tra khi Server trả lỗi tường minh

- Hiển thị popup thông báo lỗi:

    - + Button X: Nhấn đóng thông báo hiển thị màn hình đang thao tác
      + icon x
      + Tiêu đề: "Lỗi"
      + Nội dung: <Mã lỗi> : <Mô tả lỗi Server trả>
```

## Phase 6: Verify + Supplement

Sau khi generate function section, re-read RSD và verify:

### Cho LIST screens
- Tìm kiếm từng field riêng lẻ: đủ chưa?
- Tìm kiếm kết hợp nhiều field: có test combinations chưa?
- Kết quả rỗng: test empty result chưa?
- "Xóa bộ lọc": reset đúng chưa?
- Xóa bản ghi: confirm/cancel popup chưa?
- Nút thêm mới: navigate chưa?

### Cho FORM/POPUP screens
- Lưu thành công/thất bại: đủ scenarios chưa?
- Validate bỏ trống required: đủ combinations chưa?
- Field dependency rules: test chưa?
- Auto-fill / auto-calculate: test chưa?
- Dependent validation: test chưa?
- Cancel / Đóng: test chưa?

### Cho DETAIL screens
- Button visibility theo STATUS: đủ TẤT CẢ status values chưa?
- Button visibility theo QUYỀN: có/không quyền — test chưa?
- Click button (Chỉnh sửa, Phê duyệt, Từ chối): success/failure chưa?

**Merge rules:**
- Test case cần sửa → viết `### [SỬA] Kiểm tra ...` → replace original
- Test case mới → append ở cuối function section
- Nếu TẤT CẢ đã đúng → return "VERIFIED_OK"
