# Quality Rules — Test Case Generation

## Ngôn ngữ

- **100% tiếng Việt** trong testCaseName, step, expectedResult, preConditions
- Giữ nguyên tên field/button **đúng như trong mindmap** (ví dụ: "regChannel", "Tần suất thu phí")
- Thuật ngữ kỹ thuật (API, HTTP, JSON, endpoint, token, URL...) giữ nguyên tiếng Anh
- KHÔNG dịch tên field sang tiếng Việt: `regChannel` → KHÔNG đổi thành "kênh đăng ký"

## Tên test case (testCaseName)

- **Ngắn gọn**: tối đa 80 ký tự
- **Cụ thể**: mô tả chính xác hành động đang test
- **Không trùng lặp**: mỗi test case phải unique trong toàn bộ output
- Không prefix, lấy trực tiếp từ mindmap: `"Kiểm tra giá trị mặc định"`

## Atomic test cases — 1 test = 1 check

- KHÔNG gộp nhiều kiểm tra vào 1 test case
- KHÔNG dùng "và/hoặc" trong testCaseName để mô tả 2 check
- Ví dụ SAI: `"Kiểm tra khi nhập 100 ký tự và 101 ký tự"`
- Ví dụ ĐÚNG: `"Kiểm tra khi nhập 100 ký tự"` + `"Kiểm tra khi nhập 101 ký tự"` (2 cases riêng)

## Bóc tách logic điều kiện phức tạp — BẮT BUỘC

Khi một kết quả/lỗi có **nhiều điều kiện kích hoạt khác nhau** → mỗi điều kiện = 1 case riêng.
KHÔNG được gộp tất cả vào 1 case chung chỉ vì outcome giống nhau.

**Các dạng cần bóc tách:**

| Dạng logic | Cách bóc tách |
|---|---|
| `if A → check set X` / `if B → check set Y` | 1 case cho nhánh A, 1 case cho nhánh B |
| Date field có thể = `null` (open-ended) | 1 case khi record cũ null, 1 case khi record mới null, 1 case cả hai null |
| Overlap boundary | 1 case riêng cho boundary |
| Negative case (không thỏa điều kiện) | 1 case riêng — không lỗi, thao tác thành công |

**Checklist khi gặp logic phức tạp trong mindmap:**
1. Đếm số nhánh `if/else` → mỗi nhánh = 1 case
2. Tìm field nào có thể = `null` → tạo case cho từng kịch bản null
3. Tìm boundary condition → tạo case riêng cho boundary
4. Tạo ít nhất 1 negative case (điều kiện không thỏa mãn → không lỗi)

## Giá trị cụ thể — KHÔNG placeholder

- KHÔNG dùng: `{fieldName}`, `[value]`, `<param>`, `"your_value"`, `"example"`
- **KHÔNG dùng dấu `<>` cho bất kỳ giá trị nào**: `<screen>`, `<field>`, `<value>` đều bị cấm

## Deduplication

- Track tên test case đã sinh ra (case-insensitive)
- Nếu 2 batch sinh ra cùng testCaseName → giữ lại 1, bỏ duplicate
- Ưu tiên giữ case được sinh ra trước (batch nhỏ hơn)

## Phân chia batch — KHÔNG cross-contaminate

- BATCH 1 (pre-validate): CHỈ sinh cases cho sections trước validate
- BATCH 2 (validate): CHỈ sinh cases cho validate section, filter out common/permission cases
- BATCH 3 (post-validate): CHỈ sinh cases cho sections sau validate
- Mỗi batch phải có instruction rõ: "Chỉ sinh test cases cho section: [tên section]"

## Validate Section — Per-Field Processing

- Mỗi `### field name` trong validate section = 1 sub-batch riêng
- testSuiteName = "Kiểm tra validate" (force override)
- testCaseName = lấy trực tiếp từ bullet
- KHÔNG mix cases của field A vào batch đang xử lý field B

## Các field LUÔN trống

```
externalId = ""
testSuiteDetails = ""
specTitle = ""
documentId = ""
estimatedDuration = ""
result = ""
note = ""
```

## summary = testCaseName

`summary` phải **giống hệt** `testCaseName`. Không rút ngắn, không thay đổi.

## SQL trong expectedResult

- SQL phải viết trên 1 dòng hoặc xuống dòng trực tiếp — **KHÔNG thêm `-->` ở đầu dòng tiếp theo**
- SAI: `"SELECT * FROM users\n--> WHERE id = 1"`
- ĐÚNG: `"SELECT * FROM users\nWHERE id = 1"`

## Phân quyền — PHẢI có đủ 2 cases

Section "Kiểm tra phân quyền" PHẢI sinh **đủ 2 test case**:
1. `"Kiểm tra user không có quyền"` — expect UI hiển thị thông báo lỗi hoặc điều hướng
2. `"Kiểm tra user có quyền"` — expect truy cập thành công (happy path)

KHÔNG được chỉ sinh 1 trong 2.

## Các lỗi phổ biến cần tránh

| Lỗi | Cách sửa |
|-----|----------|
| testCaseName quá dài | Tối đa 80 ký tự, cắt bỏ phần thừa |
| step không numbered | Luôn dùng `"1. ...\n2. ..."` |
| expectedResult dùng HTTP status code | KHÔNG dùng status code cho FE test |
| Dùng placeholder `<>` trong preConditions | Thay bằng giá trị thật: `"WEB"` không phải `"<channel>"` |
| SQL có `-->` ở đầu dòng xuống dòng | Xóa `-->`, xuống dòng trực tiếp |
| Phân quyền chỉ có case "không có quyền" | Luôn thêm case "có quyền" |
| summary khác testCaseName | summary = testCaseName |
| importance chưa đúng | Tra bảng mapping trong output-format.md |
