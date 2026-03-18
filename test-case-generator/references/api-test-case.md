# API Test Case — Hướng dẫn sinh chi tiết

## Pipeline tổng thể

```
Phase 1:  Parse mindmap → tree (apiName, suites[], fields[])
Phase 2:  Extract request body từ RSD/PTTK (nếu có) → inject vào tất cả batches
Phase 3:  Extract response templates từ PTTK (1 LLM call) → inject vào R6
Phase 4:  BATCH 1 — Pre-validate sections (common cases, phân quyền)
Phase 5:  BATCH 2 — Validate section — 1 sub-batch PER FIELD (### heading)
Phase 6:  BATCH 3 — Post-validate sections (lưới dữ liệu, chức năng, timeout...)
Phase 7:  Dedup — Loại bỏ duplicate testCaseName
Phase 8:  Output JSON array
```

> **Quy tắc ưu tiên nguồn dữ liệu**: Xem `--ref priority-rules`

## Phase 2: Trích xuất Request Body từ RSD/PTTK

Theo quy tắc trong `priority-rules.md`: dùng PTTK nếu có, fallback RSD.

Nếu user cung cấp RSD hoặc PTTK:

1. Tìm phần mô tả API endpoint này (dùng "API Table of Contents" hint nếu có)
2. Trích xuất (từ PTTK nếu có, fallback RSD):
   - Tên field (giữ nguyên tên gốc)
   - Kiểu dữ liệu (string, integer, array, object)
   - Bắt buộc/tùy chọn
   - maxLength, format constraints
   - Giá trị mẫu hợp lệ (concrete values)
3. Build body JSON với TẤT CẢ required fields có giá trị mẫu

Ví dụ output:
```json
{
  "regChannel": "WEB",
  "pageSize": 5,
  "pageIndex": 1,
  "fromDate": "01/01/2024",
  "toDate": "31/12/2024"
}
```

## Phase 3: Response Template Optimization

Trước khi chạy batches, extract response templates **1 lần**:
- **Nguồn**: theo `priority-rules.md` — PTTK (ưu tiên) → RSD (fallback)
- Lấy response body SUCCESS (status 200, errorCode "0")
- Lấy response body ERROR (validation fail)
- Inject cùng templates vào tất cả BATCH 1, 2, 3

Tiết kiệm: ~1750 tokens/generation (15 SUCCESS cases × ~200 tokens - 500 extraction cost)

---

## R0: testSuiteName

- = Level 1 node (## heading) trong mindmap
- Force-override trong mỗi batch:
  - BATCH 1: = tên section đang xử lý (VD: "Kiểm tra các case common", "Kiểm tra phân quyền")
  - BATCH 2: = tên field type + field name (VD: "String : id", "Integer : isPriority", "List listPriorityLevel") HOẶC = "Kiểm tra validate" tùy project
  - BATCH 3: = tên section đang xử lý (VD: "Kiểm tra luồng chính", "Kiểm tra chức năng chính", "Kiểm tra khi bị timeout")
- Nhiều APIs cùng suite name → gộp vào 1 suite, KHÔNG reset số thứ tự
- **Luôn search catalog trước** để xem project đang dùng naming convention nào cho validate suites

## R1: externalId

- LUÔN để trống `""`
- Excel formula tự điền: API_1, API_2...

## R2: testCaseName

**Format**: `"{Category}_Mô tả hành động"`

- Category = tên field hoặc section (VD: "Phân quyền", "regChannel", "Method", "URL")
- Dùng underscore `_` giữa category và mô tả
- KHÔNG bao gồm testSuiteName
- KHÔNG bao gồm tên API
- Phải unique trong toàn bộ output

Ví dụ đúng:
- `"Method_Kiểm tra khi nhập sai method"`
- `"URL_Kiểm tra khi truyền sai url"`
- `"Phân quyền_Kiểm tra user không có quyền"`
- `"regChannel_Bỏ trống field bắt buộc"`
- `"regChannel_Truyền 101 ký tự"`

Ví dụ sai:
- `"Kiểm tra validate regChannel bỏ trống"` (thiếu prefix)
- `"Kiểm tra các case common_Method_sai method"` (prefix sai)

## R3: summary

- = testCaseName, GIỐNG HỆT, không thay đổi

## R4: preConditions

**Format bắt buộc:**
```
1. Send API login thành công
2. Chuẩn bị request hợp lệ
   2.1 Endpoint: {METHOD} {{BASE_URL}}{path}
   2.2 Header:
   {
     "Authorization": "Bearer {JWT_TOKEN}",
     "Content-Type": "application/json"
   }
   2.3 Body:
   {
     {extracted_body_with_concrete_values}
   }
```

**Rules:**
- Luôn dùng endpoint user cung cấp (nếu có). KHÔNG tự đặt endpoint khác.
- Body = request hợp lệ hoàn chỉnh (baseline). Step sẽ mô tả sự thay đổi.
- Body KHÔNG được để trống nếu API có input fields.
- Header luôn có Authorization + Content-Type.
- KHÔNG thay đổi body theo từng test case trong preConditions (thay đổi thể hiện ở step).

## R5: step

Format: numbered steps
```
1. {Hành động 1}
2. {Hành động 2}
```

Ví dụ theo section:
- **Method**: `"1. Nhập invalid Method: GET\n2. Send API"`
- **URL**: `"1. Nhập sai endpoint: /v1/fee/invalid-path\n2. Send API"`
- **Phân quyền (no permission)**: `"1. Login với user không có quyền\n2. Send API"`
- **Validate (bỏ trống)**: `"1. Bỏ trống {field} (bắt buộc)\n2. Send API"`
- **Validate (type error)**: `"1. Truyền {field} = true (boolean)\n2. Send API"`
- **Validate (over max)**: `"1. Truyền {field} = 101 ký tự\n2. Send API"`
- **Luồng chính**: `"1. Truyền {field} hợp lệ = {concrete_value}\n2. Send API"`

## R6: expectedResult

**Format bắt buộc:**
```
1. Check api trả về:
   1.1. Status: {code}
   1.2. Response:
   {
     {response_body}
   }
```

**Status codes:**
- Common errors: 107 (wrong method), 500 (access denied/wrong URL)
- Validate errors: 200 (error trong body, KHÔNG phải 400/422)
- Success: 200

**Response rules:**
- ALL validation errors: Status 200, error trong body (KHÔNG dùng status 400/422/500 cho validate)
- Luồng chính SUCCESS: dùng response template từ PTTK (Phase 0c)
- Nếu không có PTTK: `"Trả về response body đúng cấu trúc"`
- LUÔN có SQL kèm theo cho luồng chính có query DB

Ví dụ validate error:
```
1. Check api trả về:
   1.1. Status: 200
   1.2. Response:
   {
     "message": "Dữ liệu không hợp lệ"
   }
```

Ví dụ success:
```
1. Check api trả về:
   1.1. Status: 200
   1.2. Response:
   {
     "errorCode": "0",
     "errorDesc": "Thực hiện thành công",
     "total": 5,
     "items": [...]
   }
   SQL:
   SELECT * FROM FEE_ENGINE.FEE_TABLE
   WHERE STATUS = 1
   ORDER BY CREATED_TIME DESC;
```

## R6.1: importance

Xem bảng mapping trong `output-format.md`.

---

## Phase 4 — BATCH 1: Pre-Validate Sections

**Sections xử lý:** tất cả ## sections TRƯỚC "Kiểm tra validate" trong mindmap
- Thường: "Kiểm tra các case common", "Phân quyền", "Xác thực token"

**Instruction thêm vào prompt:**
> "Chỉ sinh test cases cho section: {section_name}. KHÔNG sinh cases cho validate hay luồng chính."

**Force-override:** `testSuiteName` = tên section đang xử lý

**Ví dụ output BATCH 1:**
```json
[
  {
    "testSuiteName": "Kiểm tra các case common",
    "testCaseName": "Method_Kiểm tra khi nhập sai method",
    ...
  },
  {
    "testSuiteName": "Kiểm tra các case common",
    "testCaseName": "URL_Kiểm tra khi truyền sai url",
    ...
  }
]
```

---

## Phase 5 — BATCH 2: Validate Section — Per-Field

**Section xử lý:** "Kiểm tra validate" và tất cả ### subsections bên trong

**Split strategy:** mỗi `### field_name` = 1 sub-batch riêng
- Lọc ra các headings không phải field (common, permission, auth) → bỏ qua
- Xử lý tuần tự từng field

**Instruction thêm vào mỗi sub-batch:**
> "Chỉ sinh test cases validate cho field: {field_name}. KHÔNG sinh cases cho các field khác hay common cases."

**Force-override:** `testSuiteName` = tên field type + field name (VD: `"String : id"`) HOẶC `"Kiểm tra validate"` — tùy convention trong catalog

**testCaseName format:** `"Validate_{mô tả}"` (VD: `"Validate_Kiểm tra truyền id là mảng"`)

**Ví dụ sub-batch cho field "id" (string):**
```json
[
  {
    "testSuiteName": "String : id",
    "testCaseName": "Validate_Kiểm tra bỏ trống id",
    ...
  },
  {
    "testSuiteName": "String : id",
    "testCaseName": "Validate_Kiểm tra truyền id = null",
    ...
  },
  {
    "testSuiteName": "String : id",
    "testCaseName": "Validate_Kiểm tra truyền id 101 ký tự",
    ...
  }
]
```

---

## Phase 6 — BATCH 3: Post-Validate Sections

**Sections xử lý:** tất cả ## sections SAU "Kiểm tra validate"
- Thường: "Kiểm tra luồng chính", "Kiểm tra chức năng", "Timeout"

**Instruction thêm vào prompt:**
> "Chỉ sinh test cases cho section: {section_name}. KHÔNG sinh lại các cases đã có ở validate hay common."

**Force-override:** `testSuiteName` = tên section đang xử lý

**maxTokens:** 65536 (vì luồng chính thường có nhiều cases với response JSON dài)

---

## Standard Validate Cases cho String Field

Mỗi string field cần cover các cases:

| Case | step | expectedResult |
|------|------|----------------|
| Bỏ trống (required) | Bỏ trống field | Status 200, error message |
| Không truyền (required) | Không truyền field trong body | Status 200, error message |
| Truyền null | `"field": null` | Theo RSD |
| Truyền N-1 ký tự (maxLength-1) | Truyền N-1 ký tự | Status 200, success |
| Truyền N ký tự (maxLength) | Truyền N ký tự | Status 200, success |
| Truyền N+1 ký tự | Truyền N+1 ký tự | Status 200, error |
| Ký tự số | Truyền số | Theo RSD |
| Ký tự chữ không dấu | Truyền chữ | Theo RSD |
| Ký tự chữ có dấu | Truyền có dấu | Theo RSD |
| Ký tự đặc biệt cho phép | Truyền ký tự _ | Status 200, success |
| Ký tự đặc biệt không cho phép | Truyền @, #, $ | Status 200, error |
| All space | `"field": "   "` | Theo RSD |
| Space đầu/cuối | `" value "` | Theo RSD |
| Space ở giữa | `"va lue"` | Theo RSD |
| Emoji/icons | Truyền 😀🏠 | Status 200, error |
| Unicode đặc biệt | Tiếng Trung, Nhật... | Status 200, error |
| Boolean | `true` / `false` | Status 200, error |
| Array | `[]` | Status 200, error |
| Object | `{}` | Status 200, error |
| XSS | `<script>alert(1)</script>` | Status 200, error |
| SQL Injection | `' OR 1=1--` | Status 200, error |
