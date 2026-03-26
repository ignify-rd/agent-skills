# Frontend Field Templates — Exact Format

Mỗi field type có template hardcoded (19 loại). Templates sinh ~80% test cases. LLM chỉ bổ sung business-specific cases.

## Dispatch Logic

```
field.type → template function:
  textbox / text / input       → generateTextboxTests()
  combobox                     → generateComboboxTests()
  dropdown (có values[])       → generateSimpleDropdownTests()
  dropdown (có apiEndpoint)    → generateSearchableDropdownTests()
  toggle / switch              → generateToggleTests()
  checkbox                     → generateCheckboxTests()
  button                       → generateButtonTests()
  icon_x / icon_close          → generateIconXTests()
  date / datepicker            → generateDatePickerTests()
  daterange / date_range       → generateDateRangePickerTests()
  textarea / multiline         → generateTextareaTests()
  number / number_input        → generateNumberInputTests()
  radio / radio_group          → generateRadioButtonTests()
  file / file_upload / upload  → generateFileUploadTests()
  password / password_input    → generatePasswordInputTests()
  tag / tag_input / chip       → generateTagInputTests()
  richtext / rich_text_editor  → generateRichTextEditorTests()
  unknown                      → Fallback: generateTextboxTests()
```

---

## 1. Textbox (editable)

```markdown
### Kiểm tra textbox "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "{placeholder}"

- Kiểm tra hiển thị khi nhập 1 ký tự

    - Hiển thị icon X xóa nhanh ký tự nhập

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh ký tự nhập

    - Clear data đã nhập ở textbox

- Kiểm tra khi nhập kí tự là số

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự chữ

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự đặc biệt

    - {allowSpecialChars ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra khi nhập kí tự chữ có dấu (tiếng Việt)

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập emoji

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập XSS script

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập SQL injection

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập unicode đặc biệt (tiếng Trung, Nhật, Hàn)

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập 1 phần kí tự

    - {searchDescription}
    (Chỉ sinh nếu có searchDescription)

- Kiểm tra khi nhập kí tự chứa space đầu/cuối

    - {allowSpaces ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra khi Paste kí tự chứa space đầu/cuối

    - {allowSpaces ? "Hệ thống cho phép Paste" : "Hệ thống chặn không cho phép Paste"}

- Kiểm tra khi nhập all space

    - {allowSpaces ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra khi nhập {maxLength-1} kí tự

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập {maxLength} kí tự

    - Hệ thống cho phép nhập

- Kiểm tra khi Paste {maxLength} kí tự

    - Hệ thống cho phép Paste

- Kiểm tra khi nhập {maxLength+1} kí tự

    - Hiển thị cảnh báo "{warningMessage}"
    (Chỉ sinh nếu có warningMessage)

{Nếu có minLength:}
- Kiểm tra khi nhập {minLength-1} kí tự

    - Hiển thị thông báo lỗi validate "Vui lòng nhập tối thiểu {minLength} ký tự"

- Kiểm tra khi nhập {minLength} kí tự

    - Hệ thống cho phép nhập

{Nếu isRequired:}
- Kiểm tra khi để trống trường {fieldName}

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng nhập {fieldName}"}"

{Nếu có validationPattern (email/phone/số/...):}
- Kiểm tra khi nhập giá trị đúng định dạng {formatName}

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập giá trị sai định dạng {formatName}

    - Hiển thị thông báo lỗi validate "{formatErrorMessage}"

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Textbox ở trạng thái Disabled, không thể nhập
```

**Conditional sections:**
- `placeholder` → sinh test placeholder (bỏ nếu null)
- `hasIconX` → sinh Icon X section (bỏ nếu false)
- `searchDescription` → sinh "nhập 1 phần kí tự" test
- `maxLength` → sinh 3 boundary tests (maxLen-1, maxLen, maxLen+1)
- `warningMessage` → sinh cảnh báo test (chỉ khi có maxLength)
- `minLength` → sinh 2 boundary tests (minLen-1 → lỗi, minLen → ok)
- `isRequired` → sinh test bỏ trống
- `validationPattern` → sinh 2 format tests (đúng/sai định dạng)
- `isConditionallyDisabled` → sinh test trạng thái disabled

## 2. Textbox (Read Only)

```markdown
### Kiểm tra textbox "{fieldName}"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường {fieldName}

    - Textbox ở trạng thái Read Only / Disabled

- Kiểm tra giá trị hiển thị tại trường {fieldName}

    - Hiển thị đúng {valueDescription}

{Nếu allowCopy:}
- Kiểm tra khi copy nội dung tại trường {fieldName}

    - Cho phép bôi đen và copy nội dung

{Nếu !allowCopy:}
- Kiểm tra khi copy nội dung tại trường {fieldName}

    - Không cho phép bôi đen và copy nội dung
```

---

## 3. Combobox (searchable dropdown with API data)

```markdown
### Kiểm tra Combobox "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

{Nếu isRequired:}
- Có icon * thể hiện bắt buộc

- Kiểm tra khi bỏ trống

    - Hiển thị support text tại trường {fieldName} "Vui lòng chọn giá trị"

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "{placeholder}"

- Kiểm tra hiển thị icon x

    - Khi có giá trị được chọn, hiển thị icon x cho phép xoá nhanh

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh giá trị đã chọn

    - Clear data đã chọn

- Kiểm tra giá trị

    - Hiển thị danh sách giá trị (liệt kê ĐẦY ĐỦ giá trị cụ thể từ RSD/PTTK, KHÔNG ghi chung chung. Nếu >20 giá trị thì liệt kê 10 giá trị đầu + ghi "... và N giá trị khác theo RSD/PTTK"). Endpoint: {apiEndpoint}
    - {dbQuery}

- Kiểm tra hiển thị khi không nhận được phản hồi của API {apiEndpoint}

    - Hiển thị popup thông báo lỗi theo design modal lỗi với nội dung "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."

- Kiểm tra hiển thị khi nhận phản hồi lỗi

    - Hiển thị popup thông báo lỗi theo design modal lỗi với nội dung errorDesc server trả về

- Kiểm tra khi API trả về danh sách rỗng

    - Hiển thị "Không tìm thấy" tại Combobox

- Kiểm tra trạng thái loading khi gọi API

    - Hiển thị loading indicator trong khi chờ kết quả API

- Kiểm tra khi chọn giá trị trong Combobox

    - Kiểm tra khi chọn 1 giá trị

        - Hệ thống cho phép chọn

    - Kiểm tra khi chọn nhiều giá trị

        - {isSingleSelect ? "Chỉ cho phép chọn 1" : "Cho phép chọn nhiều"}

- Kiểm tra nhập ký tự

    - Không cho nhập, chỉ được chọn theo danh sách có sẵn

#### Textbox Tìm kiếm

- Kiểm tra mặc định

    - Hiển thị Placeholder: "Tìm kiếm"

{Nếu có searchRealtimeDesc:}
- Kiểm tra hiển thị realtime theo ký tự nhập

    - {searchRealtimeDesc}

- Kiểm tra focus

    - Mặc định focus Textbox tìm kiếm khi nhấn mở combobox

- Kiểm tra nhập số

    - Cho phép nhập

- Kiểm tra nhập chữ a-z A-Z

    - Cho phép nhập

- Kiểm tra nhập ký tự đặc biệt

    - {allowSearchSpecialChars ? "Cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra nhập emoji

    - Hệ thống chặn không cho phép nhập

- Kiểm tra nhập XSS script

    - Hệ thống chặn không cho phép nhập

- Kiểm tra nhập SQL injection

    - Hệ thống chặn không cho phép nhập

- Kiểm tra nhập khoảng trắng

    - Cho phép nhập

{Nếu có dataFormat:}
- Kiểm tra định dạng của data trả về

    - Mỗi loại hiển thị dạng: {dataFormat}

- Kiểm tra khi nhập {maxSearchLength-1} kí tự

    - Hệ thống cho phép nhập {maxSearchLength-1} kí tự

- Kiểm tra khi nhập {maxSearchLength} kí tự

    - Hệ thống cho phép nhập {maxSearchLength} kí tự

- Kiểm tra khi nhập {maxSearchLength+1} kí tự

    - Hệ thống chặn không cho nhập quá {maxSearchLength} kí tự

- Nhập từ khoá tồn tại

    - Hiển thị kết quả tương ứng với từ khoá đã nhập

- Nhập từ khoá không tồn tại

    - Hiển thị Không tìm thấy tại Dropdown

- Nhập một phần từ khoá

    - Hiển thị kết quả chứa một phần từ khoá đã nhập

- Kiểm tra hiển thị khi nhấn tab

    - Cho phép nhấn tab để chuyển từ textbox tìm kiếm sang danh sách giá trị

- Kiểm tra hiển thị khi nhấn các phím mũi tên

    - Cho phép nhấn Gõ các phím mũi tên di chuyển để chuyển focus giữa các giá trị

- Kiểm tra chọn giá trị bằng chuột trái

    - Cho phép Chọn select bằng cách click chuột trái vào dòng giá trị

- Kiểm tra chọn giá trị bằng bàn phím

    - Cho phép Chọn select bằng cách focus và nhấn enter/SPACE

- Kiểm tra hiển thị giá trị sau khi chọn

    - Fill đúng text (tên) giá trị đã chọn và đóng combobox

{Nếu !isSingleSelect:}
- Kiểm tra hiển thị sau khi chọn nhiều giá trị

    - Fill đúng text (tên) các giá trị đã chọn, các giá trị được chọn ngăn cách bằng dấu phẩy trên ô tìm kiếm

- Kiểm tra khi thực hiện bỏ chọn checkbox

    - Cho phép bỏ chọn

{Nếu có dataFormat:}
- Kiểm tra danh sách giá trị trong Combobox

    - Danh sách hiển thị theo thứ tự server trả về:

        {!isSingleSelect ? "+ Checkbox" : ""}
        + Mỗi loại hiển thị dạng: {dataFormat}
        + {dbQuery}
```

---

## 4. Simple Dropdown (hardcoded values, no search)

```markdown
### Kiểm tra dropdown list "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Luôn hiện và enable

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "{placeholder}"

{Nếu isRequired:}
- Kiểm tra khi bỏ trống trường {fieldName}

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng chọn {fieldName}"}"

- Kiểm tra giá trị hiển thị khi nhấn chọn Dropdown list

    - Hiển thị danh sách các giá trị:

        - {value1}
        - {value2}
        - {value3}
        - ... (liệt kê ĐẦY ĐỦ TẤT CẢ giá trị cụ thể từ RSD/PTTK, KHÔNG được bỏ sót hay ghi "...". Nếu >20 giá trị thì liệt kê 10 giá trị đầu + ghi "... và N giá trị khác theo RSD/PTTK")

- Kiểm tra khi chọn giá trị trong Dropdown list

    - Kiểm tra khi chọn 1 giá trị

        - Hệ thống cho phép chọn

    - Kiểm tra khi chọn nhiều giá trị

        - {isSingleSelect ? "Hệ thống chỉ cho phép chọn 1" : "Cho phép chọn nhiều"}

{Cho MỖI giá trị trong values[]:}
- Kiểm tra khi chọn giá trị = "{value}"

    - Hệ thống hiển thị text "{value}" tại dropdown list

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Dropdown ở trạng thái Disabled, không thể chọn

#### Icon X

- Kiểm tra hiển thị khi chọn giá trị

    - Hiển thị icon X xóa nhanh ký tự nhập

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh giá trị đã chọn

    - Clear data đã chọn
```

---

## 5. Searchable Dropdown (API data + search textbox)

```markdown
### Kiểm tra Searchable Dropdown List "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "{placeholder}"

#### Icon X

- Kiểm tra icon X hiển thị khi nhập/chọn dữ liệu

    - Hiển thị icon X xóa nhanh ký tự nhập

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh giá trị đã nhập/chọn

    - Clear data đã nhập ở textbox

- Kiểm tra danh sách giá trị trong dropdown

    - Hiển thị danh sách giá trị (liệt kê ĐẦY ĐỦ giá trị cụ thể từ RSD/PTTK, KHÔNG ghi chung chung. Nếu >20 giá trị thì liệt kê 10 giá trị đầu + ghi "... và N giá trị khác theo RSD/PTTK"). Endpoint: {apiEndpoint}
    - {dbQuery}

#### searchBox

- Kiểm tra khi nhập 1 phần giá trị

    - Danh sách hiển thị các bản ghi chứa chuỗi nhập

- Kiểm tra hiển thị realtime theo ký tự nhập

    - {searchRealtimeDesc || "Cho phép tự động tìm kiếm..."}

- Kiểm tra khi nhập ký tự chữ

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập ký tự là số

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập giá trị chứa ký tự đặc biệt

    - {allowSearchSpecialChars ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra khi nhập emoji

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập XSS script

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập SQL injection

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập giá trị là all space

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập giá trị chứa space đầu cuối

    - Hệ thống cho phép nhập

- Kiểm tra khi Paste giá trị chứa space đầu cuối

    - Hệ thống cho phép Paste

- Kiểm tra khi nhập giá trị không hợp lệ

    - Hệ thống chặn không cho phép nhập

{Nếu có maxSearchLength:}
- Kiểm tra khi nhập {maxSearchLength-1} kí tự

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập {maxSearchLength} kí tự

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập {maxSearchLength+1} kí tự

    - Hệ thống chặn không cho nhập quá {maxSearchLength} kí tự

- Nhập từ khoá tồn tại

    - Hiển thị kết quả tương ứng với từ khoá đã nhập

- Nhập từ khoá không tồn tại

    - Hiển thị "Không tìm thấy" tại dropdown

- Nhập một phần từ khoá

    - Hiển thị kết quả chứa một phần từ khoá đã nhập

- Kiểm tra trạng thái loading khi gọi API {apiEndpoint}

    - Hiển thị loading indicator trong khi chờ kết quả API

- Kiểm tra khi không nhận được phản hồi của API {apiEndpoint}

    - Hiển thị popup thông báo lỗi với nội dung "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."

- Kiểm tra khi chọn giá trị trong Searchable Dropdown

    - Hiển thị text giá trị đã chọn tại ô dropdown, đóng danh sách

{Nếu isRequired:}
- Kiểm tra khi bỏ trống trường {fieldName}

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng chọn {fieldName}"}"
```

---

## 6. Toggle Button

```markdown
### Kiểm tra Toggle Button "{fieldName}"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - {defaultValueDesc}

- Kiểm tra các giá trị của Toggle Button "{fieldName}"

    - Có {values.length} giá trị:

+ {value1}

+ {value2}

{Cho MỖI transition:}
- Kiểm tra khi chuyển từ {from} → {to}

    - {description}

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Toggle ở trạng thái Disabled, không thể thao tác

{Nếu hasPermissionControl:}
- Kiểm tra khi user không có quyền thay đổi {fieldName}

    - Toggle ở trạng thái Disabled
```

---

## 7. Checkbox (in data grid)

```markdown
### Kiểm tra Check box "Checkbox"

- Kiểm tra hiển thị

    - User có quyền DELETE
        - Enable

    - User có không quyền DELETE

        - Disable

- Kiểm tra khi tick checkbox tại bản ghi

    - Checkbox header hiển thị trạng thái chọn 1 phần (–)
    - Hiển thị dạng {Số lượng bản ghi đã chọn}/{Tổng số dòng bản ghi server trả về ở trường total API lấy danh sách}

- Kiểm tra khi chọn all bản ghi

    - Tất cả các bản ghi được tích chọn và Checkbox header ở trạng thái checked

- Kiểm tra khi click checkbox header khi đang checked

    - Bỏ chọn toàn bộ bản ghi trong trang
    - Checkbox header chuyển sang unchecked

- Kiểm tra khi bỏ chọn từng bản ghi khi đang chọn all

    - Checkbox header chuyển từ checked → (–)

- Kiểm tra hiển thị số lượng bản ghi đã chọn

    - Hiển thị dạng {số bản ghi đã chọn}/{tổng số bản ghi} theo đúng giá trị field `total` từ API lấy danh sách

- Kiểm tra khi chọn all trên page hiện tại (nếu có phân trang)

    - Chỉ chọn bản ghi trong trang hiện tại, không ảnh hưởng trang khác

- Kiểm tra khi chuyển sang trang khác sau khi đã chọn bản ghi

    - Bản ghi đã chọn ở trang trước vẫn được giữ nguyên
```

Nếu `requiresDeletePermission = false`: thay block quyền bằng `- Mặc định enable`.

---

## 8. Button

```markdown
### Kiểm tra Button {fieldName}

- Kiểm tra hiển thị

    - {alwaysEnabled ? "Luôn hiển thị và enable" : "Mặc định enable"}

{Nếu có text:}
- Kiểm tra hiển thị text, thiết kế của button

    - Hiển thị text "{text}", thiết kế theo figma

- Kiểm tra khi nhấn button {fieldName}

    - {clickResult}

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Button ở trạng thái Disabled, không thể nhấn

- Kiểm tra trạng thái khi {enableCondition}

    - Button ở trạng thái Enable

{Nếu hasLoadingState:}
- Kiểm tra trạng thái khi đang xử lý sau khi nhấn

    - Button hiển thị loading, không thể nhấn lại trong khi đang xử lý

{Nếu hasConfirmDialog:}
- Kiểm tra khi nhấn button {fieldName} và xác nhận

    - {confirmResult}

- Kiểm tra khi nhấn button {fieldName} và huỷ bỏ

    - Đóng dialog, không thực hiện hành động
```

---

## 9. Icon X (close icon)

```markdown
### Kiểm tra {fieldName}

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhấn đóng popup đang thao tác

    - {closeResult || "Popup được đóng\n\nHệ thống hiển thị màn hình danh sách trước đó"}

{Nếu hasUnsavedWarning:}
- Kiểm tra khi nhấn đóng khi đang có dữ liệu chưa lưu

    - Hiển thị dialog xác nhận "{unsavedWarningMessage || "Dữ liệu chưa được lưu. Bạn có chắc muốn thoát?"}"

    - Kiểm tra khi xác nhận thoát

        - Đóng popup, bỏ qua dữ liệu chưa lưu

    - Kiểm tra khi huỷ bỏ

        - Đóng dialog xác nhận, quay lại popup đang thao tác

{Nếu hasEscKey:}
- Kiểm tra khi nhấn phím ESC

    - {escResult || "Có tác dụng tương đương nhấn icon X — đóng popup"}
```

---

## 10. Button Visibility (DETAIL screens only — sinh từ `buttonVisibilityRules[]`)

```markdown
### Kiểm tra hiển thị nút "{buttonName}"

- Kiểm tra khi bản ghi có status = {status1}

    - {description1}

- Kiểm tra khi bản ghi có status = {status2}

    - {description2}

{Nếu hasRoleControl:}
- Kiểm tra khi user có quyền {requiredRole}

    - Nút hiển thị và enable

- Kiểm tra khi user không có quyền {requiredRole}

    - Nút ẩn hoặc Disabled
```

Sinh từ `buttonVisibilityRules[]` cho mỗi button.

---

## 11. Date Picker

```markdown
### Kiểm tra Date Picker "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - {defaultValueDesc || "Mặc định rỗng"}

- Kiểm tra placeholder

    - Hiển thị placeholder "{placeholder || "dd/MM/yyyy"}"

- Kiểm tra icon lịch

    - Hiển thị icon lịch bên phải textbox

- Kiểm tra khi click icon lịch

    - Mở popup calendar

- Kiểm tra khi chọn ngày hợp lệ

    - Hiển thị ngày đã chọn theo định dạng {dateFormat || "dd/MM/yyyy"}

- Kiểm tra khi nhập ngày hợp lệ bằng bàn phím

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập sai định dạng ngày

    - Hiển thị thông báo lỗi validate "{formatErrorMessage || "Vui lòng nhập đúng định dạng dd/MM/yyyy"}"

- Kiểm tra khi nhập ngày không tồn tại (30/02, 32/01)

    - Hiển thị thông báo lỗi validate "Ngày không hợp lệ"

{Nếu có minDate:}
- Kiểm tra khi chọn ngày trước {minDate}

    - {minDateErrorMessage || "Không cho phép chọn ngày trước " + minDate}

- Kiểm tra khi chọn ngày = {minDate}

    - Hệ thống cho phép chọn

{Nếu có maxDate:}
- Kiểm tra khi chọn ngày sau {maxDate}

    - {maxDateErrorMessage || "Không cho phép chọn ngày sau " + maxDate}

- Kiểm tra khi chọn ngày = {maxDate}

    - Hệ thống cho phép chọn

{Nếu không cho chọn ngày quá khứ:}
- Kiểm tra khi chọn ngày quá khứ

    - Ngày quá khứ bị disable, không thể chọn

{Nếu không cho chọn ngày tương lai:}
- Kiểm tra khi chọn ngày tương lai

    - Ngày tương lai bị disable, không thể chọn

- Kiểm tra khi nhập ký tự chữ

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập ký tự đặc biệt (ngoài dấu /)

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập emoji

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập XSS script

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập SQL injection

    - Hệ thống chặn không cho phép nhập

#### Icon X

- Kiểm tra hiển thị icon X khi có giá trị

    - Hiển thị icon X xóa nhanh giá trị đã chọn

- Kiểm tra hoạt động khi click icon X

    - Clear ngày đã chọn, trở về trạng thái rỗng

{Nếu isRequired:}
- Kiểm tra khi để trống trường {fieldName}

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng chọn ngày"}"

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Date Picker ở trạng thái Disabled, không thể chọn
```

**Conditional sections:**
- `minDate` / `maxDate` → sinh boundary tests
- `allowPastDates` = false → sinh test ngày quá khứ bị disable
- `allowFutureDates` = false → sinh test ngày tương lai bị disable
- `isRequired` → sinh test bỏ trống
- `isConditionallyDisabled` → sinh test disabled state

---

## 12. Date Range Picker

```markdown
### Kiểm tra Date Range Picker "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Hiển thị 2 ô input: Từ ngày — Đến ngày, luôn enable

- Kiểm tra giá trị mặc định

    - {defaultValueDesc || "Mặc định rỗng cả 2 ô"}

- Kiểm tra placeholder

    - Từ ngày: placeholder "{fromPlaceholder || "dd/MM/yyyy"}"
    - Đến ngày: placeholder "{toPlaceholder || "dd/MM/yyyy"}"

- Kiểm tra khi chọn ngày bắt đầu hợp lệ

    - Hiển thị ngày bắt đầu theo đúng định dạng

- Kiểm tra khi chọn ngày kết thúc hợp lệ

    - Hiển thị ngày kết thúc theo đúng định dạng

- Kiểm tra khi ngày bắt đầu > ngày kết thúc

    - Hiển thị thông báo lỗi "{rangeErrorMessage || "Từ ngày không được lớn hơn Đến ngày"}"

- Kiểm tra khi ngày bắt đầu = ngày kết thúc

    - Hệ thống cho phép chọn

- Kiểm tra khi chỉ nhập ngày bắt đầu, bỏ trống ngày kết thúc

    - {partialRangeRule || "Hiển thị thông báo lỗi validate"}

- Kiểm tra khi chỉ nhập ngày kết thúc, bỏ trống ngày bắt đầu

    - {partialRangeRule || "Hiển thị thông báo lỗi validate"}

- Kiểm tra khi nhập sai định dạng ngày

    - Hiển thị thông báo lỗi validate "Vui lòng nhập đúng định dạng dd/MM/yyyy"

- Kiểm tra khi nhập ngày không tồn tại

    - Hiển thị thông báo lỗi validate "Ngày không hợp lệ"

{Nếu có maxRange:}
- Kiểm tra khi khoảng cách > {maxRange} ngày

    - Hiển thị thông báo lỗi "{maxRangeMessage || "Khoảng cách tìm kiếm không được vượt quá " + maxRange + " ngày"}"

- Kiểm tra khi nhập ký tự chữ

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập emoji

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập XSS script

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập SQL injection

    - Hệ thống chặn không cho phép nhập

#### Icon X

- Kiểm tra hiển thị icon X khi có giá trị

    - Hiển thị icon X xóa nhanh

- Kiểm tra hoạt động khi click icon X

    - Clear cả Từ ngày và Đến ngày

{Nếu isRequired:}
- Kiểm tra khi để trống cả 2 ô ngày

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng chọn khoảng thời gian"}"

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Date Range Picker ở trạng thái Disabled
```

---

## 13. Textarea (multiline text)

```markdown
### Kiểm tra Textarea "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "{placeholder}"

- Kiểm tra khi nhập kí tự là số

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự chữ

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự chữ có dấu (tiếng Việt)

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự đặc biệt

    - {allowSpecialChars ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra khi nhập emoji

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập XSS script

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập SQL injection

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập unicode đặc biệt (tiếng Trung, Nhật, Hàn)

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập xuống dòng (Enter)

    - Hệ thống cho phép xuống dòng

- Kiểm tra khi nhập nhiều dòng

    - Textarea tự động mở rộng chiều cao (hoặc hiển thị scrollbar)

- Kiểm tra khi nhập kí tự chứa space đầu/cuối

    - {allowSpaces ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra khi nhập all space

    - {allowSpaces ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

{Nếu có maxLength:}
- Kiểm tra khi nhập {maxLength-1} kí tự

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập {maxLength} kí tự

    - Hệ thống cho phép nhập

- Kiểm tra khi Paste {maxLength} kí tự

    - Hệ thống cho phép Paste

- Kiểm tra khi nhập {maxLength+1} kí tự

    - Hiển thị cảnh báo "{warningMessage}"

{Nếu có charCounter:}
- Kiểm tra hiển thị bộ đếm ký tự

    - Hiển thị số ký tự đã nhập / {maxLength}

{Nếu isRequired:}
- Kiểm tra khi để trống trường {fieldName}

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng nhập {fieldName}"}"

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Textarea ở trạng thái Disabled, không thể nhập
```

**Conditional sections:**
- Kế thừa tất cả conditional sections từ Textbox (editable)
- Thêm: `charCounter` → sinh test bộ đếm ký tự
- Thêm: test xuống dòng và multiline behavior

---

## 14. Number Input

```markdown
### Kiểm tra Number Input "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - {defaultValueDesc || "Mặc định rỗng"}

- Kiểm tra placeholder

    - Hiển thị placeholder "{placeholder}"

- Kiểm tra khi nhập số nguyên dương

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập số 0

    - {allowZero ? "Hệ thống cho phép nhập" : "Hiển thị thông báo lỗi validate"}

- Kiểm tra khi nhập số âm

    - {allowNegative ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra khi nhập số thập phân

    - {allowDecimal ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

{Nếu allowDecimal:}
- Kiểm tra khi nhập quá {maxDecimalPlaces} chữ số thập phân

    - Hệ thống chặn không cho nhập quá {maxDecimalPlaces} chữ số thập phân

- Kiểm tra khi nhập leading zero (00123)

    - Hệ thống tự động xóa leading zero hoặc chặn

- Kiểm tra khi nhập ký tự chữ

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập ký tự đặc biệt (@#$%)

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập khoảng trắng

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập emoji

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập XSS script

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập SQL injection

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi Paste giá trị chứa chữ

    - Hệ thống chặn không cho phép Paste

{Nếu có minValue:}
- Kiểm tra khi nhập giá trị = {minValue - 1}

    - Hiển thị thông báo lỗi validate "Giá trị tối thiểu là {minValue}"

- Kiểm tra khi nhập giá trị = {minValue}

    - Hệ thống cho phép nhập

{Nếu có maxValue:}
- Kiểm tra khi nhập giá trị = {maxValue}

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập giá trị = {maxValue + 1}

    - Hiển thị thông báo lỗi validate "Giá trị tối đa là {maxValue}"

- Kiểm tra khi nhập số quá lớn vượt giới hạn

    - Hệ thống hiển thị lỗi hoặc chặn không cho nhập

{Nếu có stepper (nút +/-):}
- Kiểm tra khi click nút tăng (+)

    - Giá trị tăng thêm {step || 1}

- Kiểm tra khi click nút giảm (-)

    - Giá trị giảm đi {step || 1}

- Kiểm tra khi giá trị = {minValue} và click nút giảm

    - Nút giảm bị disable hoặc giá trị không thay đổi

- Kiểm tra khi giá trị = {maxValue} và click nút tăng

    - Nút tăng bị disable hoặc giá trị không thay đổi

#### Icon X

- Kiểm tra hiển thị icon X khi có giá trị

    - Hiển thị icon X xóa nhanh

- Kiểm tra hoạt động khi click icon X

    - Clear giá trị đã nhập

{Nếu isRequired:}
- Kiểm tra khi để trống trường {fieldName}

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng nhập {fieldName}"}"

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Number Input ở trạng thái Disabled, không thể nhập
```

**Conditional sections:**
- `allowNegative` → sinh test số âm
- `allowDecimal` → sinh test thập phân + maxDecimalPlaces
- `allowZero` → sinh test giá trị 0
- `minValue` / `maxValue` → sinh boundary tests
- `hasStepper` → sinh test nút +/-

---

## 15. Radio Button / Radio Group

```markdown
### Kiểm tra Radio Button "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - {defaultValueDesc || "Không có giá trị nào được chọn mặc định"}

- Kiểm tra danh sách các giá trị

    - Hiển thị đầy đủ các giá trị:

        - {value1}
        - {value2}
        - {value3}
        ...

{Cho MỖI giá trị trong values[]:}
- Kiểm tra khi chọn giá trị = "{value}"

    - Hệ thống hiển thị "{value}" ở trạng thái selected

- Kiểm tra khi thay đổi lựa chọn từ "{value1}" sang "{value2}"

    - "{value1}" bị bỏ chọn, "{value2}" được chọn (chỉ cho phép chọn 1)

- Kiểm tra layout hiển thị

    - {layoutDesc || "Các radio button hiển thị theo hàng ngang/dọc đúng thiết kế"}

{Nếu isRequired:}
- Kiểm tra khi không chọn giá trị nào

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng chọn {fieldName}"}"

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Tất cả radio buttons ở trạng thái Disabled, không thể chọn

{Nếu có conditionalValues — giá trị A ẩn/hiện dựa vào field khác:}
- Kiểm tra khi {showCondition}

    - Hiển thị đầy đủ các giá trị

- Kiểm tra khi {hideCondition}

    - Ẩn radio button hoặc disable
```

---

## 16. File Upload

```markdown
### Kiểm tra File Upload "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Hiển thị vùng upload file (button hoặc drag & drop area), enable

- Kiểm tra hiển thị text hướng dẫn

    - {uploadGuideText || "Kéo thả file hoặc click để chọn file"}

- Kiểm tra khi upload file đúng định dạng ({allowedFormats})

    - Hệ thống cho phép upload, hiển thị tên file đã chọn

- Kiểm tra khi upload file sai định dạng

    - Hiển thị thông báo lỗi "{formatErrorMessage || "Định dạng file không hợp lệ. Vui lòng chọn file " + allowedFormats}"

{Nếu có maxFileSize:}
- Kiểm tra khi upload file có dung lượng = {maxFileSize}

    - Hệ thống cho phép upload

- Kiểm tra khi upload file có dung lượng > {maxFileSize}

    - Hiển thị thông báo lỗi "{sizeErrorMessage || "Dung lượng file vượt quá giới hạn " + maxFileSize}"

- Kiểm tra khi upload file rỗng (0 KB)

    - Hiển thị thông báo lỗi "File rỗng, vui lòng chọn file khác"

{Nếu có maxFiles > 1:}
- Kiểm tra khi upload {maxFiles} file

    - Hệ thống cho phép upload

- Kiểm tra khi upload {maxFiles + 1} file

    - Hiển thị thông báo lỗi "Chỉ cho phép upload tối đa {maxFiles} file"

- Kiểm tra khi upload file trùng tên

    - {duplicateRule || "Hiển thị thông báo lỗi file trùng tên"}

- Kiểm tra khi upload file có tên chứa ký tự đặc biệt

    - {specialCharRule || "Hệ thống cho phép upload"}

- Kiểm tra khi upload file có tên chứa unicode (tiếng Việt)

    - Hệ thống cho phép upload

- Kiểm tra hiển thị progress bar khi đang upload

    - Hiển thị progress upload

- Kiểm tra khi hủy upload giữa chừng

    - Upload bị hủy, file không được lưu

- Kiểm tra khi upload thành công

    - Hiển thị tên file, dung lượng, icon xóa

- Kiểm tra khi click icon xóa file đã upload

    - Xóa file đã upload, quay về trạng thái ban đầu

{Nếu hasDragDrop:}
- Kiểm tra khi kéo thả file đúng định dạng vào vùng upload

    - Hệ thống cho phép upload

- Kiểm tra khi kéo thả file sai định dạng vào vùng upload

    - Hiển thị thông báo lỗi định dạng

{Nếu hasPreview:}
- Kiểm tra hiển thị preview file sau khi upload

    - Hiển thị preview file đúng nội dung

{Nếu isRequired:}
- Kiểm tra khi không upload file

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng chọn file"}"

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Vùng upload ở trạng thái Disabled
```

**Conditional sections:**
- `allowedFormats` → sinh test đúng/sai định dạng (e.g., `.xlsx`, `.pdf`, `.jpg`)
- `maxFileSize` → sinh boundary test dung lượng
- `maxFiles` → sinh test số lượng file
- `hasDragDrop` → sinh test kéo thả
- `hasPreview` → sinh test preview

---

## 17. Password Input

```markdown
### Kiểm tra Password Input "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "{placeholder}"

- Kiểm tra ẩn ký tự khi nhập

    - Ký tự nhập hiển thị dạng dấu chấm (•••) hoặc dấu sao (***)

- Kiểm tra icon hiện/ẩn mật khẩu

    - Hiển thị icon mắt (eye) bên phải textbox

- Kiểm tra khi click icon hiện mật khẩu

    - Hiển thị ký tự đã nhập dạng plain text

- Kiểm tra khi click icon ẩn mật khẩu

    - Ẩn ký tự đã nhập dạng dấu chấm

- Kiểm tra khi nhập kí tự là số

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự chữ

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự đặc biệt

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập khoảng trắng

    - {allowSpaces ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra khi nhập emoji

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập XSS script

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập SQL injection

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi Paste giá trị vào password

    - {allowPaste ? "Hệ thống cho phép Paste" : "Hệ thống chặn không cho phép Paste"}

- Kiểm tra khi copy mật khẩu

    - Hệ thống chặn không cho phép copy

{Nếu có maxLength:}
- Kiểm tra khi nhập {maxLength-1} kí tự

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập {maxLength} kí tự

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập {maxLength+1} kí tự

    - Hiển thị cảnh báo "{warningMessage}"

{Nếu có minLength:}
- Kiểm tra khi nhập {minLength-1} kí tự

    - Hiển thị thông báo lỗi validate "Mật khẩu tối thiểu {minLength} ký tự"

- Kiểm tra khi nhập {minLength} kí tự

    - Hệ thống cho phép nhập

{Nếu có passwordStrength:}
- Kiểm tra khi nhập mật khẩu yếu (chỉ chữ thường)

    - Hiển thị indicator "Yếu"

- Kiểm tra khi nhập mật khẩu trung bình (chữ + số)

    - Hiển thị indicator "Trung bình"

- Kiểm tra khi nhập mật khẩu mạnh (chữ + số + đặc biệt)

    - Hiển thị indicator "Mạnh"

{Nếu hasConfirmPassword:}
- Kiểm tra khi nhập xác nhận mật khẩu khớp

    - Hệ thống cho phép

- Kiểm tra khi nhập xác nhận mật khẩu không khớp

    - Hiển thị thông báo lỗi "Mật khẩu xác nhận không khớp"

{Nếu isRequired:}
- Kiểm tra khi để trống trường {fieldName}

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng nhập mật khẩu"}"

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Password Input ở trạng thái Disabled
```

---

## 18. Tag Input / Chip Input

```markdown
### Kiểm tra Tag Input "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - {defaultValueDesc || "Mặc định rỗng"}

- Kiểm tra placeholder

    - Hiển thị placeholder "{placeholder}"

- Kiểm tra khi nhập giá trị và nhấn Enter

    - Tạo tag mới với giá trị đã nhập

- Kiểm tra khi nhập giá trị và nhấn dấu phẩy (,)

    - {commaAsSeparator ? "Tạo tag mới" : "Hệ thống cho phép nhập dấu phẩy"}

- Kiểm tra khi nhập giá trị trùng với tag đã có

    - {allowDuplicate ? "Cho phép tạo tag trùng" : "Hiển thị thông báo \"Giá trị đã tồn tại\""}

- Kiểm tra khi click icon X trên tag

    - Xóa tag đã chọn

- Kiểm tra khi nhấn Backspace khi textbox rỗng

    - Xóa tag cuối cùng

- Kiểm tra khi nhập kí tự đặc biệt

    - {allowSpecialChars ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra khi nhập emoji

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập XSS script

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập SQL injection

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập all space

    - Hệ thống chặn không cho tạo tag rỗng

{Nếu có maxTags:}
- Kiểm tra khi thêm tag thứ {maxTags}

    - Hệ thống cho phép thêm

- Kiểm tra khi thêm tag thứ {maxTags + 1}

    - Hiển thị thông báo "Đã đạt giới hạn {maxTags} tags"

{Nếu có maxTagLength:}
- Kiểm tra khi nhập tag dài {maxTagLength + 1} ký tự

    - Hệ thống chặn không cho nhập quá {maxTagLength} ký tự

{Nếu có suggestions (autocomplete):}
- Kiểm tra khi nhập và có gợi ý

    - Hiển thị danh sách gợi ý tương ứng

- Kiểm tra khi chọn giá trị từ gợi ý

    - Tạo tag mới với giá trị được chọn

{Nếu isRequired:}
- Kiểm tra khi không có tag nào

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng thêm ít nhất 1 giá trị"}"

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Tag Input ở trạng thái Disabled
```

---

## 19. Rich Text Editor

```markdown
### Kiểm tra Rich Text Editor "{fieldName}"

- Kiểm tra hiển thị mặc định

    - Hiển thị editor với toolbar đầy đủ, enable

- Kiểm tra giá trị mặc định

    - {defaultValueDesc || "Mặc định rỗng"}

- Kiểm tra toolbar hiển thị

    - Hiển thị đầy đủ các nút: {toolbarButtons || "Bold, Italic, Underline, Bullet List, Number List, Link, Image"}

- Kiểm tra khi nhập text bình thường

    - Hệ thống cho phép nhập

- Kiểm tra khi áp dụng Bold

    - Text được in đậm đúng

- Kiểm tra khi áp dụng Italic

    - Text được in nghiêng đúng

- Kiểm tra khi áp dụng Underline

    - Text được gạch chân đúng

- Kiểm tra khi tạo Bullet List

    - Hiển thị danh sách dạng bullet

- Kiểm tra khi tạo Number List

    - Hiển thị danh sách đánh số

- Kiểm tra khi chèn link

    - Hiển thị link clickable đúng URL

- Kiểm tra khi nhập kí tự chữ có dấu (tiếng Việt)

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập emoji

    - {allowEmoji ? "Hệ thống cho phép nhập" : "Hệ thống chặn không cho phép nhập"}

- Kiểm tra khi nhập XSS script

    - Hệ thống sanitize và chặn script injection

- Kiểm tra khi nhập SQL injection

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi Paste nội dung từ Word/Excel

    - Hệ thống xử lý formatting, loại bỏ styles không hỗ trợ

- Kiểm tra khi Paste nội dung có chứa HTML tags

    - Hệ thống sanitize HTML, chỉ giữ các tags cho phép

- Kiểm tra khi Undo (Ctrl + Z)

    - Hoàn tác thao tác cuối cùng

- Kiểm tra khi Redo (Ctrl + Y)

    - Thực hiện lại thao tác đã hoàn tác

{Nếu có maxLength (tính theo text content, không tính HTML tags):}
- Kiểm tra khi nhập nội dung đạt {maxLength} ký tự

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập nội dung vượt {maxLength} ký tự

    - Hiển thị cảnh báo vượt quá giới hạn

{Nếu có charCounter:}
- Kiểm tra hiển thị bộ đếm ký tự

    - Hiển thị số ký tự đã nhập / {maxLength}

{Nếu hasImageUpload:}
- Kiểm tra khi chèn hình ảnh đúng định dạng

    - Hiển thị hình ảnh trong editor

- Kiểm tra khi chèn hình ảnh sai định dạng

    - Hiển thị thông báo lỗi định dạng

- Kiểm tra khi chèn hình ảnh vượt dung lượng

    - Hiển thị thông báo lỗi dung lượng

{Nếu isRequired:}
- Kiểm tra khi để trống editor

    - Hiển thị thông báo lỗi validate "{requiredMessage || "Vui lòng nhập nội dung"}"

{Nếu isConditionallyDisabled:}
- Kiểm tra trạng thái khi {disableCondition}

    - Editor ở trạng thái Disabled, toolbar bị disable
```
