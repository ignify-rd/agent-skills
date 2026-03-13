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
- ĐÚNG: `"regChannel": "WEB"`, `"pageSize": 5`, `"PAR_TYPE": "CUSTOMER_TYPE"`
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
result = "PENDING"
note = ""
```

## summary = testCaseName

`summary` phải **giống hệt** `testCaseName`. Không rút ngắn, không thay đổi.

## Các lỗi phổ biến cần tránh

| Lỗi | Cách sửa |
|-----|----------|
| preConditions body để trống dù API có input fields | Luôn điền body đầy đủ với required fields |
| testCaseName quá dài | Tối đa 80 ký tự, cắt bỏ phần thừa |
| step không numbered | Luôn dùng `"1. ...\n2. ..."` |
| expectedResult không có status code (API) | Luôn có `1.1. Status: ...` và `1.2. Response: ...` |
| Frontend test có HTTP status code | KHÔNG dùng status code cho FE test |
| Dùng placeholder trong preConditions body | Thay bằng giá trị cụ thể |
| summary khác testCaseName | summary = testCaseName |
| importance chưa đúng | Tra bảng mapping trong output-format.md |
