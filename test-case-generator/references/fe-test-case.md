# Frontend Test Case — Hướng dẫn sinh chi tiết

> **Quy tắc ưu tiên nguồn dữ liệu**: Xem `--ref priority-rules`

## Pipeline tổng thể

```
Phase 1:  Parse mindmap → tree (screenName, screenPath, suites[], fields[])
Phase 2:  Extract field details từ PTTK (nếu có) → enrich validate test cases
Phase 3:  BATCH 1 — Pre-validate sections (giao diện chung, phân quyền)
Phase 4:  BATCH 2 — Validate section — 1 sub-batch PER FIELD (### heading)
Phase 5:  BATCH 3 — Post-validate sections (lưới dữ liệu, phân trang, chức năng, timeout)
Phase 6:  Dedup — Loại bỏ duplicate testCaseName
Phase 7:  Output JSON array
```

## Xác định Screen Path cho preConditions

Từ mindmap header (dòng 1) và breadcrumb trong mindmap, xác định:
- `screenPath`: đường dẫn điều hướng (VD: "Danh mục > Tần suất thu phí")
- `screenName`: tên màn hình hiển thị (VD: "Tần suất thu phí")
- `systemName`: tên hệ thống (VD: "FEE", "BO")

Nếu không xác định được từ mindmap, dùng header dòng 1 làm screenPath.

---

## R0: testSuiteName

- = Level 1 node (## heading) trong mindmap
- Force-override trong mỗi batch:
  - BATCH 1: = tên section (VD: "Kiểm tra giao diện chung")
  - BATCH 2: = "Kiểm tra validate" (cố định, KHÔNG phải tên field)
  - BATCH 3: = tên section (VD: "Kiểm tra chức năng")

## R1: externalId

- LUÔN để trống `""`
- Excel formula tự điền: FE_1, FE_2...

## R2: testCaseName

**Lấy TRỰC TIẾP từ mindmap** — KHÔNG thêm prefix, KHÔNG thêm screen name

- = text của ### heading hoặc bullet item trong mindmap
- KHÔNG thêm category prefix (KHÔNG làm như API: "Phân quyền_...", "Field_...")
- KHÔNG thêm tên màn hình vào cuối
- Phải unique trong toàn bộ output

Ví dụ ĐÚNG:
```
Mindmap: "- Kiểm tra khi nhập 101 ký tự"
→ testCaseName: "Kiểm tra khi nhập 101 ký tự"

Mindmap: "### Kiểm tra điều hướng đến màn hình Tần suất thu phí"
→ testCaseName: "Kiểm tra điều hướng đến màn hình Tần suất thu phí"
```

Ví dụ SAI:
```
"Validate_Kiểm tra khi nhập 101 ký tự"    ← KHÔNG thêm prefix
"Kiểm tra khi nhập 101 ký tự - Tần suất thu phí"  ← KHÔNG thêm screen name
```

**Trường hợp validate field:** testSuiteName = "Kiểm tra validate", testCaseName = text của bullet bên dưới ### field_name

## R3: summary

- = testCaseName, GIỐNG HỆT, không thay đổi

## R4: preConditions

**Format bắt buộc:**
```
Đ/k1: Vào màn hình:
1. Người dùng đăng nhập thành công {system} trên Web với account: 164987/ Test@147258369
2. Tại sitemap, người dùng truy cập màn hình {screenPath}
Đ/k2: Phân quyền
3. User được phân quyền truy cập
```

**Thêm dòng 4 khi test cần dữ liệu:**
```
4. Có dữ liệu trong hệ thống
```

**Trường hợp đặc biệt — test không có quyền:**
```
Đ/k1: Vào màn hình:
1. Người dùng đăng nhập thành công {system} trên Web với account: 164987/ Test@147258369
2. Tại sitemap, người dùng truy cập màn hình {screenPath}
Đ/k2: Phân quyền
3. User không được phân quyền truy cập
```

**Rules:**
- `{system}` = tên hệ thống (VD: "FEE", "BO"), lấy từ mindmap header
- `{screenPath}` = đường dẫn breadcrumb đến màn hình
- KHÔNG thay đổi format preConditions (cố định cho toàn bộ project)
- KHÔNG dùng HTTP endpoint hay body JSON trong preConditions (đây là Frontend, không phải API)

## R5: step

Format: numbered steps, mô tả hành động UI

```
1. {UI action 1}
2. {UI action 2}
```

**Bộ động từ UI chuẩn:**
- `Click` — nhấn button, icon, link
- `Nhập` — gõ text vào textbox/combobox
- `Chọn` — chọn giá trị từ dropdown/combobox
- `Quan sát` — nhìn vào màn hình để verify
- `Kéo` — drag & drop
- `Scroll` — cuộn trang
- `Double-click` — nhấn đúp
- `Hover` — di chuột qua element

Ví dụ theo loại test:
- **Điều hướng**: `"1. Quan sát màn hình sau khi điều hướng"`
- **Bố cục**: `"1. Quan sát bố cục màn hình"`
- **Dropdown**: `"1. Click vào dropdown list \"{tên}\"\n2. Quan sát danh sách hiển thị"`
- **Chọn giá trị**: `"1. Click vào dropdown list \"{tên}\"\n2. Chọn giá trị \"{giá trị cụ thể}\""`
- **Nhập ký tự**: `"1. Tại textbox \"{tên}\", nhập {N} ký tự\n2. Quan sát"`
- **Icon X**: `"1. Nhập giá trị vào textbox \"{tên}\"\n2. Click icon X"`
- **Tìm kiếm**: `"1. Nhập điều kiện tìm kiếm\n2. Click button \"Tìm kiếm\""`
- **Phân trang**: `"1. Click button >\n2. Quan sát"` hoặc `"1. Chọn giá trị 10 từ dropdown phân trang"`

## R6: expectedResult

Mô tả trạng thái UI mong đợi. KHÔNG dùng HTTP status code.

**Bộ trạng thái UI chuẩn:**
- `Hiển thị` — element xuất hiện trên màn hình
- `Ẩn` — element không hiển thị
- `Enable` — element có thể tương tác
- `Disable` — element không thể tương tác
- `Focus` — element đang được focus
- `Redirect` — điều hướng sang màn hình khác

Ví dụ theo section:
- **Điều hướng**: `"Điều hướng thành công đến màn hình {screenName}"`
- **Bố cục**: `"+ Hiển thị theo đúng figma\n+ Màn hình {screenName} hiển thị đầy đủ:\n+ {element1}\n+ {element2}"`
- **Default display**: `"Luôn hiển thị và enable"`
- **Giá trị mặc định**: `"Mặc định rỗng"` hoặc `"Mặc định là {giá trị}"`
- **Placeholder**: `"Hiển thị placeholder \"{text placeholder}\""`
- **Dropdown values**: `"Hiển thị danh sách:\n    - {value1}\n    - {value2}"`
- **Chọn giá trị**: `"Hệ thống hiển thị text \"{giá trị được chọn}\" tại dropdown"`
- **Max length**: `"Hiển thị cảnh báo \"{warning message}\""`
- **Icon X**: `"Hiển thị icon X xóa nhanh ký tự nhập"`
- **Clear**: `"Clear data đã nhập"`
- **Tìm kiếm**: `"Hiển thị kết quả khớp với điều kiện"`
- **Rỗng**: `"Hiển thị thông báo \"Không có dữ liệu\""`
- **Disable**: `"Button < bị disable"`
- **Lưới mặc định**: `"Server trả về danh sách {tên}"`
- **Timeout**: `"Hiển thị popup thông báo lỗi:\n    - + Icon x\n      + Tiêu đề: \"Lỗi\"\n      + Nội dung: <Mã lỗi> : <Mô tả lỗi Server trả>\n      + Button: Đóng"`

**Copy trực tiếp từ mindmap:** nếu leaf node trong mindmap đã có expected result cụ thể → copy nguyên văn

## R6.1: importance

Xem bảng mapping trong `output-format.md`.

---

## Phase 3 — BATCH 1: Pre-Validate Sections

**Sections xử lý:** tất cả ## sections TRƯỚC "Kiểm tra validate"
- Thường: "Kiểm tra giao diện chung", "Kiểm tra phân quyền"

**Có thể combine tất cả pre-sections vào 1 LLM call** (khác API phải tách)

**Force-override:** `testSuiteName` = tên section tương ứng của từng test case

**Lưu ý cho "Kiểm tra giao diện chung":**
- Các test case thường rất ngắn, copy trực tiếp từ mindmap bullet
- expectedResult copy nguyên văn từ leaf node

**Ví dụ output BATCH 1:**
```json
[
  {
    "testSuiteName": "Kiểm tra giao diện chung",
    "testCaseName": "Kiểm tra điều hướng đến màn hình Tần suất thu phí",
    "step": "1. Quan sát màn hình sau khi điều hướng",
    "expectedResult": "Điều hướng thành công đến màn hình Tần suất thu phí"
  },
  {
    "testSuiteName": "Kiểm tra phân quyền",
    "testCaseName": "Kiểm tra login user không có quyền",
    "step": "1. Login với user không có quyền\n2. Truy cập màn hình",
    "expectedResult": "Không view được màn hình"
  }
]
```

---

## Phase 4 — BATCH 2: Validate Section — Per-Field

**Section xử lý:** "Kiểm tra validate" và tất cả ### field headings bên trong

**Split strategy:** mỗi `### field_name` = 1 sub-batch riêng

**Force-override:**
- `testSuiteName` = "Kiểm tra validate"
- `testCaseName` = text của bullet item dưới ### heading (KHÔNG thêm field prefix)

**Instruction thêm vào mỗi sub-batch:**
> "Chỉ sinh test cases cho field: {field_name}. testSuiteName = 'Kiểm tra validate'. testCaseName lấy trực tiếp từ bullet items."

**Ví dụ sub-batch cho "Dropdown list Đối tượng khai báo":**
```json
[
  {
    "testSuiteName": "Kiểm tra validate",
    "testCaseName": "Kiểm tra hiển thị mặc định",
    "step": "1. Quan sát dropdown list \"Đối tượng khai báo\"",
    "expectedResult": "Luôn hiện và enable"
  },
  {
    "testSuiteName": "Kiểm tra validate",
    "testCaseName": "Kiểm tra giá trị mặc định",
    "step": "1. Quan sát giá trị mặc định của dropdown list \"Đối tượng khai báo\"",
    "expectedResult": "Mặc định rỗng"
  }
]
```

---

## Phase 5 — BATCH 3: Post-Validate Sections

**Sections xử lý:** tất cả ## sections SAU "Kiểm tra validate"
- Thường: "Kiểm tra lưới dữ liệu", "Kiểm tra Phân trang", "Kiểm tra chức năng", "Kiểm tra timeout"

**Có thể combine tất cả post-sections vào 1 LLM call**

**Force-override:** `testSuiteName` = tên section tương ứng

**Instruction thêm vào prompt:**
> "Chỉ sinh test cases cho các sections sau validate: {section_names}. KHÔNG sinh lại cases đã có ở validate hay giao diện chung."

**Ví dụ Kiểm tra lưới dữ liệu:**
```json
[
  {
    "testSuiteName": "Kiểm tra lưới dữ liệu",
    "testCaseName": "Kiểm tra mặc định",
    "step": "1. Quan sát lưới dữ liệu sau khi load màn hình",
    "expectedResult": "Server trả về danh sách tần suất thu phí"
  },
  {
    "testSuiteName": "Kiểm tra lưới dữ liệu",
    "testCaseName": "Kiểm tra cột \"STT\"",
    "step": "1. Quan sát cột STT trong lưới dữ liệu",
    "expectedResult": "Hiển thị số thứ tự tăng dần từ 1"
  }
]
```

---

## Standard Validate Cases cho Frontend Fields

### Textbox (editable)

| Case | step | expectedResult |
|------|------|----------------|
| Hiển thị mặc định | Quan sát | Luôn hiển thị và enable |
| Giá trị mặc định | Quan sát | Mặc định rỗng |
| Placeholder | Quan sát | Hiển thị placeholder "{text}" |
| Nhập số | Nhập ký tự số | Hệ thống cho phép nhập |
| Nhập chữ | Nhập ký tự chữ | Hệ thống cho phép nhập |
| Nhập ký tự đặc biệt | Nhập @#$ | Hệ thống chặn không cho phép nhập |
| Nhập space đầu/cuối | Nhập " abc " | Hệ thống cho phép nhập |
| Nhập all space | Nhập "   " | Hệ thống cho phép nhập |
| Nhập N-1 ký tự | Nhập N-1 ký tự | Hệ thống cho phép nhập |
| Nhập N ký tự (max) | Nhập N ký tự | Hệ thống cho phép nhập |
| Paste N ký tự | Paste N ký tự | Hệ thống cho phép Paste |
| Nhập N+1 ký tự | Nhập N+1 ký tự | Hiển thị cảnh báo "{warning}" |
| Icon X — hiển thị | Nhập 1 ký tự | Hiển thị icon X xóa nhanh |
| Icon X — clear | Click icon X | Clear data đã nhập |

### Dropdown/Combobox

| Case | step | expectedResult |
|------|------|----------------|
| Hiển thị mặc định | Quan sát | Luôn hiện và enable |
| Giá trị mặc định | Quan sát | Mặc định rỗng |
| Placeholder | Quan sát | Hiển thị placeholder "{text}" |
| Nhấn mở dropdown | Click dropdown | Hiển thị danh sách các giá trị: {list} |
| Chọn giá trị X | Chọn giá trị X | Hệ thống hiển thị text "X" |
| Icon X — hiển thị | Chọn giá trị | Hiển thị icon X xóa nhanh |
| Icon X — clear | Click icon X | Clear data đã chọn |

### Toggle

| Case | step | expectedResult |
|------|------|----------------|
| Hiển thị mặc định | Quan sát | {defaultState} |
| Giá trị mặc định | Quan sát | Mặc định là {default} |
| Click bật | Click toggle (đang tắt) | Toggle chuyển sang bật |
| Click tắt | Click toggle (đang bật) | Toggle chuyển sang tắt |
