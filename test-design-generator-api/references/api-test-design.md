# API Test Design — Hướng dẫn sinh chi tiết

## Tổng quan

API test design sinh ra markdown mindmap gồm 3 section chính:
1. **Các case common** (method, URL, phân quyền) — hardcoded template
2. **Validate** (kiểm tra validate từng field đầu vào) — per-field templates
3. **Luồng chính** (business logic, DB operations, error scenarios) — LLM-generated

## Pipeline tổng thể

```
Phase 1:  Extract RSD structure → business logic, errorCodes, dbMapping
Phase 2:  Extract PTTK fields (if available) → inputFields[], outputFields[] (PTTK wins)
Phase 3:  Generate validate section (per-field templates)
Phase 4:  Generate main flow section (LLM from RSD)
Phase 5:  Verify & supplement main flow (re-read RSD, cross-check, merge [SỬA])
Phase 6:  Combine with base template
Phase 7:  Validate and fix markdown
```

> **Quy tắc ưu tiên nguồn dữ liệu**: Xem `--ref priority-rules`

## Base Template (hardcoded — KHÔNG thay đổi)

```markdown
# {API_NAME}

## Kiểm tra các case common

### Method

#### Kiểm tra truyền sai method ({WRONG_METHODS})
- status: 107
- {
  "message": "Error retrieving AuthorInfo for token from TokenLib: Token is invalid signature"
  }

### URL

#### Kiểm tra truyền sai url
- status: 500
- {
  "message": "Access denied"
  }

### Kiểm tra phân quyền

#### Không có quyền
- status: 500
- {
  "message": "Access denied"
  }

#### Được phân quyền
- status: 200

## Kiểm tra validate

{VALIDATE_SECTION}

## Kiểm tra luồng chính

{MAIN_FLOW_SECTION}
```

**⚠️ CRITICAL — Format Rules cho toàn bộ API output:**
1. **KHÔNG** thêm blockquote/mô tả endpoint (` > **Endpoint:** ...`) — output bắt đầu NGAY từ `# {API_NAME}`
2. **KHÔNG** dùng `---` (horizontal rule) phân cách giữa các section, field, hoặc bất kỳ đâu
3. **Section common** dùng format ĐƠN GIẢN: `- status: 107` — **TUYỆT ĐỐI KHÔNG** dùng `1\. Check api trả về:` trong common
4. Format `1\. Check api trả về:` / `1\.1. Status:` / `1\.2. Response:` **CHỈ** dùng trong section **validate** và **luồng chính**
5. Section common là **hardcoded template** — copy ĐÚNG NGUYÊN VĂN, chỉ thay `{API_NAME}` và `{WRONG_METHODS}`

**`{WRONG_METHODS}`**: Tính từ API method. VD: nếu method=POST → WRONG_METHODS = "GET/PUT/DELETE"

## Phase 1: Trích xuất cấu trúc từ RSD — business logic

Đọc RSD và trích xuất phần **business logic** (luôn lấy từ RSD):

```json
{
  "title": "Tên API",
  "endpoint": "POST /v1/category/search",
  "method": "GET | POST | PUT | DELETE",
  "errorCodes": {"mô tả lỗi": "status code"},
  "dbMapping": {
    "table": "Tên bảng DB",
    "conditions": ["Điều kiện WHERE"],
    "orderBy": "Sắp xếp"
  }
}
```

## Phase 2: Đọc PTTK (nếu có) — lấy field definitions

Nếu có PTTK → tìm ĐÚNG API theo endpoint → đọc bảng INPUT/OUTPUT:

```json
{
  "inputFields": [
    {
      "name": "tên field (từ PTTK)",
      "type": "string | number | date | boolean | array | object",
      "maxLength": 30,
      "required": "Y | N",
      "nullBehavior": "Mô tả khi truyền null (nếu optional)",
      "validationRules": {
        "allowedSpecialChars": ["_", "-"],
        "allowSpaces": false,
        "allowAccents": false
      },
      "children": []
    }
  ],
  "outputFields": [
    {"name": "field name", "children": []}
  ]
}
```

- Lấy TẤT CẢ fields từ PTTK (Trường, Kiểu dữ liệu, Bắt buộc, Định dạng, Mô tả)
- **CHỈ dùng PTTK fields cho validate**. RSD chỉ dùng hiểu business logic
- Data types chính xác từ PTTK (Date, Integer, Long, String)
- Format constraints từ PTTK (dd/MM/yyyy, etc.)
- Response body structure từ PTTK (tên trường, kiểu dữ liệu, nesting)

## Phase 1+2 fallback: Khi KHÔNG có PTTK

Nếu không có PTTK, đọc RSD và trích xuất CẢ field definitions lẫn business logic:

```json
{
  "title": "Tên API",
  "endpoint": "POST /v1/category/search",
  "method": "GET | POST | PUT | DELETE",
  "inputFields": [
    {
      "name": "tên field",
      "type": "string | number | date | boolean | array | object",
      "maxLength": 30,
      "required": "Y | N",
      "nullBehavior": "Mô tả khi truyền null (nếu optional)",
      "validationRules": {
        "allowedSpecialChars": ["_", "-"],
        "allowSpaces": false,
        "allowAccents": false
      },
      "children": []
    }
  ],
  "outputFields": [
    {"name": "field name", "children": []}
  ],
  "errorCodes": {"mô tả lỗi": "status code"},
  "dbMapping": {
    "table": "Tên bảng DB",
    "conditions": ["Điều kiện WHERE"],
    "orderBy": "Sắp xếp"
  }
}
```

## Phase 3: Kiểm tra validate

### Format chuẩn cho MỖI field

Mỗi field được sinh test cases theo format escaped numbering:

```markdown
### {fieldName} : {type} ({Required/Optional})

#### Để trống
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Không truyền
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền null
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }
```

**CRITICAL — Status Code Rules:**
- **ALL validate responses use Status: 200** — bất kể valid hay invalid
- Invalid data → response body: `{"message": "Dữ liệu không hợp lệ"}`
- Valid data → response body: `Trả về response body đúng cấu trúc`
- JSON response MUST be multiline WITHOUT backtick fence, directly after `1\.2. Response:`

### Field type classification (ảnh hưởng response)

| Field Type | Detect | XSS/SQL Response |
|-----------|--------|------------------|
| SEARCH_FIELD | "tìm kiếm gần đúng", "LIKE", "trim" | Status: 200 (search text) |
| FILTER_FIELD | Optional string lọc | Status: 200 + error body |
| ENUM_FIELD | Giá trị cố định ("1: active, 0: inactive") | Status: 200 |
| INTEGER_REQUIRED | Type Integer, required=Y | Status: 200 + error body |

### Template: String Required (không có default)

```markdown
### {fieldName}: string (Required, không có default)

#### Để trống
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Không truyền
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền null
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} = {maxLen-1} ký tự
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền {fieldName} = {maxLen} ký tự
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền {fieldName} = {maxLen+1} ký tự
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là ký tự số
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền {fieldName} là chữ(thường/hoa) không dấu
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền {fieldName} là chữ(thường/hoa) có dấu
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là ký tự đặc biệt cho phép _
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền {fieldName} là ký tự đặc biệt không cho phép
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là all space
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} có space ở giữa
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} có space đầu / cuối
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là emoji/icons (😀🏠⚡)
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là ký tự Unicode đặc biệt (tiếng Trung, Nhật, Ả Rập...)
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là boolean (true/false)
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là mảng
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là object
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là XSS
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là SQL INJECTION
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }
```

### Template: Integer with Default Value

```markdown
### {fieldName}: Integer (Required, default = {defaultValue})

#### Để trống
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc
  Hệ thống sử dụng giá trị default {fieldName} = {defaultValue}

#### Không truyền
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc
  Hệ thống sử dụng giá trị default {fieldName} = {defaultValue}

#### Truyền null
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc
  Hệ thống sử dụng giá trị default {fieldName} = {defaultValue}

#### Truyền {fieldName} = {validValue}
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền {fieldName} là số âm
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là số thập phân
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là chuỗi ký tự
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }
```

### Template: Optional Integer (null = tìm tất cả)

```markdown
### {fieldName}: Integer (Optional, null = tìm tất cả)

#### Để trống
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc
  Trả về TẤT CẢ bản ghi (cả active và inactive)
- Verify: Kết quả chứa cả bản ghi có STATUS = 0 và STATUS = 1

#### Không truyền
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc
  Trả về TẤT CẢ bản ghi (cả active và inactive)

#### Truyền null
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc
  Trả về TẤT CẢ bản ghi (cả active và inactive)

#### Truyền {fieldName} = {validValue} (giá trị hợp lệ)
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc
  CHỈ trả về bản ghi khớp

#### Truyền {fieldName} = {invalidValue} (giá trị không hợp lệ)
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền {fieldName} là chuỗi
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }
```

### Test cases theo kiểu dữ liệu

**STRING field — Full test list:**
Để trống, Không truyền, Truyền null, Độ dài (maxLen-1, maxLen, maxLen+1), Ký tự số, Chữ không dấu, Chữ có dấu, Ký tự đặc biệt cho phép, Ký tự đặc biệt không cho phép, All space, Space ở giữa, Space đầu/cuối, Emoji/Icons, Unicode đặc biệt, Boolean, Mảng, Object, XSS, SQL INJECTION.

**NUMBER/INTEGER field — Full test list:**
Để trống, Không truyền, Truyền null, Số nguyên hợp lệ, Số âm, Số thập phân, Số leading zero, Số rất lớn, Chuỗi chữ lẫn số, Ký tự chữ, Ký tự đặc biệt, Emoji, Unicode, Boolean, All space, Space đầu/cuối, Mảng, Object, XSS, SQL INJECTION.

**ARRAY field — Test list:**
Không truyền, Truyền null, Mảng rỗng [], Mảng chứa phần tử rỗng, String/Number/Object (thay vì array).

## Phase 4: Kiểm tra luồng chính

### ⚠️ QUY TẮC QUAN TRỌNG NHẤT

**MỌI test case trong luồng chính PHẢI có response rõ ràng theo format:**
```
- 1\. Check api trả về:
      1\.1. Status: {status_code}
      1\.2. Response:
      {
        ...response body theo PTTK/RSD định nghĩa...
      }
      SQL:
      SELECT ... FROM ... WHERE ...;
```

> **LƯU Ý:** Response body và request body KHÔNG có format cố định. Cấu trúc response
> (tên trường, kiểu dữ liệu, nesting) tùy thuộc vào PTTK/RSD của từng API.
> Các ví dụ bên dưới dùng `errorCode`, `poErrorCode`, `data` chỉ là MẪU từ 1 project cụ thể.
> Khi sinh test cases, PHẢI đọc PTTK/RSD để lấy đúng cấu trúc response thực tế.

**TUYỆT ĐỐI KHÔNG** viết test case chỉ mô tả hành động mà không có response. VD SAI:
```
### Kiểm tra mapping cột "Chi nhánh"
- Check file excel: Cột hiển thị 120000 - Chi nhánh Hà Nội
```

VD ĐÚNG:
```
### Kiểm tra mapping cột "Chi nhánh"
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        ...response body chứa thông tin "Chi nhánh" theo cấu trúc PTTK định nghĩa...
      }
      SQL:
      SELECT BRANCH_CODE, BRANCH_NAME FROM CAT_BRANCH
      WHERE BRANCH_CODE = '120000';
```

### App's 4 Training Examples (copy ĐÚNG format)

**Example 1 — Basic flow with DB query:**
```markdown
### Kiểm tra response khi truyền PAR_TYPE tồn tại kết quả
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "errorCode": "0",
        "errorDesc": "",
        "total": 5,
        "items": [...]
      }
      SQL:
      SELECT * FROM PAR_COMMON
      WHERE PAR_TYPE = 'CUSTOMER_TYPE'
      ORDER BY PAR_TYPE ASC, PAR_CODE ASC;

### Kiểm tra response khi truyền PAR_TYPE không tồn tại kết quả
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "errorCode": "0",
        "errorDesc": "",
        "total": 0,
        "items": []
      }
      SQL:
      SELECT * FROM PAR_COMMON
      WHERE PAR_TYPE = 'KHONG_TON_TAI';
```

**Example 2 — Output field mapping (response trả đầy đủ các trường):**
```markdown
### Kiểm tra response trả ra đầy đủ các trường
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "pageNo": 0,
        "pageSize": 5,
        "total": 1,
        "totalPage": 1,
        "data": [
          {
            "srvCode": "FEEACC001",
            "srvName": "Phí thu hộ",
            "cusPers": "S",
            "cusPersName": "KHTC siêu nhỏ",
            "status": 1,
            "createdUser": "admin",
            "createdTime": "2024-01-15 10:30:00",
            "updatedUser": "admin",
            "updatedTime": "2024-01-15 10:30:00"
          }
        ]
      }
      SQL:
      SELECT * FROM CAT_FEESERVICE
      WHERE SRV_CODE = 'FEEACC001'
      ORDER BY UPDATED_TIME DESC;
```

**Example 3 — Error code scenarios:**
```markdown
### Kiểm tra response khi dữ liệu không hợp lệ
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "errorCode": "1",
        "errorDesc": "Dữ liệu không hợp lệ"
      }

### Kiểm tra response khi không có quyền
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "errorCode": "1",
        "errorDesc": "Phân quyền người dùng không hợp lệ"
      }

### Kiểm tra response khi lỗi hệ thống
- 1\. Check api trả về:
      1\.1. Status: 500
      1\.2. Response:
      {
        "errorCode": "1",
        "errorDesc": "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."
      }
```

**Example 4 — Search with SQL (exact + approximate):**
```markdown
### Kiểm tra tìm kiếm chính xác theo srvCode
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "total": 1,
        "data": [
          {
            "srvCode": "FEEACC001",
            "srvName": "Phí thu hộ",
            "status": 1
          }
        ]
      }
      SQL:
      SELECT * FROM CAT_FEESERVICE
      WHERE SRV_CODE = 'FEEACC001'
      ORDER BY UPDATED_TIME DESC;

### Kiểm tra tìm kiếm gần đúng theo srvCode
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "total": 3,
        "data": [
          {"srvCode": "FEEACC001", "status": 1},
          {"srvCode": "FEEACC002", "status": 1},
          {"srvCode": "FEEACC003", "status": 1}
        ]
      }
      SQL:
      SELECT * FROM CAT_FEESERVICE
      WHERE UPPER(TRIM(SRV_CODE)) LIKE UPPER(TRIM('%FEEACC%'))
      ORDER BY UPDATED_TIME DESC;

### Kiểm tra kết hợp nhiều điều kiện tìm kiếm
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": [...]
      }
      SQL:
      SELECT * FROM CAT_FEESERVICE
      LEFT JOIN CAT_CUSTYPE ON CAT_CUSTYPE.TYPE_CODE = CAT_FEESERVICE.CUS_PERS
      WHERE UPPER(TRIM(SRV_CODE)) LIKE '%FEE%'
        AND UPPER(TRIM(SRV_NAME)) LIKE '%PHÍ%'
        AND CUS_PERS = 'S'
        AND STATUS = 1
      ORDER BY UPDATED_TIME DESC;
```

### Nội dung bắt buộc

1. **Response fields verification** — Kiểm tra response trả ra đầy đủ các trường (list ALL output fields dạng camelCase với sample values)
2. **DB mapping verification** — Kiểm tra data mapping đúng DB (với SQL query ĐẦY ĐỦ SELECT/FROM/WHERE/ORDER BY)
3. **Search scenarios** — Tìm kiếm chính xác, gần đúng (LIKE), kết hợp nhiều điều kiện, không tồn tại
4. **Sort order verification** — Kiểm tra sắp xếp theo đúng ORDER BY
5. **Error code scenarios** — Mỗi error code trong bảng mã lỗi → 1 test case với exact message trong Response
6. **Business logic branches** — Mỗi if/else → test cả true và false branch, MỖI branch có Response riêng
7. **DB validations** — Check tồn tại/không tồn tại → test cả 2 trường hợp, mỗi cái có Response
8. **Mode variations** — Nếu có task=create/update → test từng mode, mỗi mode có Response
9. **Status transitions** — Nếu có chuyển trạng thái → test valid/invalid transitions, mỗi cái có Response

### SQL query rules

- SELECT cụ thể (liệt kê cột hoặc *), FROM, WHERE, ORDER BY
- GIÁ TRỊ MẪU CỤ THỂ: `WHERE SRV_CODE = 'FEEACC001'` — KHÔNG dùng placeholder
- Tên bảng schema-qualified nếu biết: `FEE_ENGINE_SIT.SEGMENT_CONFIG`
- Tên cột UPPERCASE từ RSD
- Response fields dùng camelCase (extract từ PTTK nếu có)

## Phase 5: Verify + Supplement

Sau khi generate luồng chính, re-read RSD:

1. Liệt kê TẤT CẢ nhánh logic: if/else, conditional fields, DB validations, mode variations, error codes
2. Đối chiếu với test cases đã sinh:
   - ✅ Đã có → bỏ qua
   - ❌ Thiếu → sinh bổ sung (PHẢI có Response)
   - ⚠️ Sai expected result → viết `### [SỬA] Kiểm tra ...` và replace
3. Merge: `[SỬA]` cases replace originals; new cases append
