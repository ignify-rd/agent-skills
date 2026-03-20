# Frontend Field Templates — Exact Format

Mỗi field type có template hardcoded. Templates sinh ~80% test cases. LLM chỉ bổ sung business-specific cases.

## Dispatch Logic

```
field.type → template function:
  textbox / text / input     → generateTextboxTests()
  combobox                   → generateComboboxTests()
  dropdown (có values[])     → generateSimpleDropdownTests()
  dropdown (có apiEndpoint)  → generateSearchableDropdownTests()
  toggle / switch            → generateToggleTests()
  checkbox                   → generateCheckboxTests()
  button                     → generateButtonTests()
  icon_x / icon_close        → generateIconXTests()
  unknown                    → Fallback: generateTextboxTests()
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

    - Hiển thị data UI map với response API. Endpoint: {apiEndpoint}
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
        ...

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

    - Danh sách hiển thị các giá trị theo API: {apiEndpoint}
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
