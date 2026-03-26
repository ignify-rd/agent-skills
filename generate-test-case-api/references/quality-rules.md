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
- **API Mode**: có prefix theo field/section: `"regChannel_Bỏ trống field bắt buộc"`
- **Frontend Mode**: không prefix, lấy trực tiếp từ mindmap: `"Kiểm tra giá trị mặc định"`

## Atomic test cases — 1 test = 1 check

- KHÔNG gộp nhiều kiểm tra vào 1 test case
- KHÔNG dùng "và/hoặc" trong testCaseName để mô tả 2 check
- Ví dụ SAI: `"Kiểm tra khi nhập 100 ký tự và 101 ký tự"`
- Ví dụ ĐÚNG: `"Kiểm tra khi nhập 100 ký tự"` + `"Kiểm tra khi nhập 101 ký tự"` (2 cases riêng)

## Giá trị cụ thể — KHÔNG placeholder

- LUÔN dùng giá trị mẫu cụ thể trong preConditions body
- KHÔNG dùng: `{fieldName}`, `[value]`, `<param>`, `"your_value"`, `"example"`
- **KHÔNG dùng dấu `<>` cho bất kỳ giá trị nào trong request body**: `<channel>`, `<date>`, `<id>` đều bị cấm
- `{JWT_TOKEN}` trong Authorization header là chấp nhận được (Postman variable), nhưng data field values phải là giá trị thật
- ĐÚNG: `"regChannel": "WEB"`, `"pageSize": 5`, `"PAR_TYPE": "CUSTOMER_TYPE"`
- SAI: `"regChannel": "<channel>"`, `"fromDate": "<date>"`, `"id": "<id>"`
- Body trong preConditions = request hợp lệ hoàn chỉnh với tất cả required fields

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
- testCaseName = `"{field}_Mô tả"` (API) hoặc lấy trực tiếp từ bullet (Frontend)
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
1. `"Phân quyền_Kiểm tra user không có quyền"` — expect 403/401
2. `"Phân quyền_Kiểm tra user có quyền"` — expect 200 (happy path)

KHÔNG được chỉ sinh 1 trong 2.

## Các lỗi phổ biến cần tránh

| Lỗi | Cách sửa |
|-----|----------|
| preConditions body để trống dù API có input fields | Luôn điền body đầy đủ với required fields |
| testCaseName quá dài | Tối đa 80 ký tự, cắt bỏ phần thừa |
| step không numbered | Luôn dùng `"1. ...\n2. ..."` |
| expectedResult không có status code (API) | Luôn có `1.1. Status: ...` và `1.2. Response: ...` |
| Frontend test có HTTP status code | KHÔNG dùng status code cho FE test |
| Dùng placeholder `<>` trong preConditions body | Thay bằng giá trị thật: `"WEB"` không phải `"<channel>"` |
| SQL có `-->` ở đầu dòng xuống dòng | Xóa `-->`, xuống dòng trực tiếp |
| Phân quyền chỉ có case "không có quyền" | Luôn thêm case "có quyền" |
| summary khác testCaseName | summary = testCaseName |
| importance chưa đúng | Tra bảng mapping trong output-format.md |
