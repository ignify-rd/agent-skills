<!-- @section: overview -->
# API Test Design — Hướng dẫn sinh chi tiết

## Tổng quan

API test design sinh ra markdown mindmap gồm 3 section chính:
1. **Các case common** (method, URL, phân quyền) — hardcoded template
2. **Validate** (kiểm tra validate từng field đầu vào) — per-field templates
3. **Luồng chính** (business logic, DB operations, error scenarios) — LLM-generated

> **Quy tắc ưu tiên nguồn dữ liệu**: Xem `--ref priority-rules`

<!-- @section: common -->
## Base Template (hardcoded — KHÔNG thay đổi)

```markdown
# {API_NAME}

## Kiểm tra token

### Kiểm tra nhập token hết hạn

- Status: 401

### Kiểm tra không nhập token

- Status: 401

### Kiểm tra nhập token không hợp lệ (sai token)

- Status: 401

### Kiểm tra nhập token hợp lệ

- Status: 200

## Kiểm tra Endpoint & Method

### Kiểm tra nhập sai method ({WRONG_METHODS})

- Status: 405

### Kiểm tra nhập sai endpoint

- Status: 404

## Kiểm tra Validate

{VALIDATE_SECTION}

## Kiểm tra chức năng

{FUNCTION_SECTION}

## Kiểm tra ngoại lệ

{EXCEPTION_SECTION}
```

**⚠️ CRITICAL — Format Rules:**
1. **KHÔNG** thêm blockquote/mô tả endpoint — output bắt đầu NGAY từ `# {API_NAME}`
2. **KHÔNG** dùng `---` (horizontal rule) bất kỳ đâu
3. **Section common** (`## Kiểm tra token`, `## Kiểm tra Endpoint & Method`) dùng format ĐƠN GIẢN: `- Status: 401` — **TUYỆT ĐỐI KHÔNG** dùng `1\. Check api trả về:` trong common
4. Format `1\. Check api trả về:` **CHỈ** dùng trong **Validate** và **luồng chính**
5. `{WRONG_METHODS}`: nếu method=POST → "GET/PUT/DELETE"

---

<!-- @section: extraction -->
## Phase 1: Trích xuất cấu trúc từ RSD — business logic

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

```json
{
  "inputFields": [
    {
      "name": "tên field",
      "type": "string | integer | date | boolean | array | object | jsonb",
      "maxLength": 30,
      "required": "Y | N",
      "nullBehavior": "Mô tả khi truyền null (nếu optional)",
      "validationRules": {
        "allowedSpecialChars": ["_", "-"],
        "allowSpaces": false,
        "allowAccents": false
      }
    }
  ],
  "outputFields": [{"name": "field name"}]
}
```

**Khi KHÔNG có PTTK:** lấy field definitions từ RSD.
**Khi có PTTK:** IGNORE field definitions trong RSD, chỉ dùng PTTK cho fields.

---

<!-- @section: validate-rules -->
## Phase 3: Kiểm tra validate

### Nguồn tham chiếu chính: fieldTestTemplates.js

Mỗi field type có danh sách cases BẮT BUỘC từ `fieldTestTemplates.js`. Agent PHẢI sinh ĐẦY ĐỦ tất cả cases — KHÔNG được thiếu. Chỉ được THÊM cases (nếu tài liệu RSD/PTTK đề cập thêm).

### Cách xác định response

| Loại response | Cách xác định | Áp dụng khi |
|---------------|---------------|-------------|
| **Error** (mặc định) | Dùng error code từ `errorCodes[section="validate"]` trong inventory | Cases ghi "→ error" trong template |
| **Success** | Dùng success response từ `responseSchema.success` trong inventory | Cases ghi "→ success" trong template |
| **Theo RSD** | Đọc `rsdConstraints` trong inventory → nếu có dữ liệu → fill theo; nếu `null` → dùng **error** (default an toàn) | Cases ghi "→ Theo RSD: rsdConstraints.X" |

**CRITICAL:** ALL validate responses dùng Status: 200 — KHÔNG dùng 400/422/500 cho validate.

### Quy tắc chống duplicate / merge cases (áp dụng cho MỌI type)

| Tình huống | Rule |
|-----------|------|
| 2 case khác giá trị nhưng cùng mục đích kiểm tra + cùng response | Giữ 1, bỏ case còn lại |
| Constraint dạng "tối đa N chữ số" cho **INTEGER field** (giá trị số thực) | max = 10^N - 1. Chỉ generate: (N-1) chữ số, N chữ số (max), N+1 chữ số (max+1). Label: "(N-1 chữ số)", "(N chữ số, maxValue = 10^N-1)", "(N+1 chữ số, vượt maxValue)" |
| Constraint dạng "tối đa N chữ số" cho **fileContent STRING field** (cột Excel/CSV đọc như text) | maxLength = N. Chỉ generate: (N-1) ký tự số (maxLength-1), N ký tự số (maxLength), N+1 ký tự số (maxLength+1). Label: "(N-1 ký tự số, maxLength-1)", "(N ký tự số, maxLength)", "(N+1 ký tự số, maxLength+1)". ⛔ KHÔNG dùng label "maxValue = 10^N-1" — đây là STRING, không phải integer |
| Constraint dạng "min ≤ x ≤ max" (giá trị số) | Generate: min-1, min, max, max+1 |
| "Space ở giữa" và "All space" và "Space đầu/cuối" | Đây là 3 case **khác nhau**, giữ cả 3 |

### ⛔ CRITICAL: BASE TEMPLATE OVERLAPS VỚI BOUNDARY RULES — PHẢI MERGE

**Vấn đề gốc:** Base template (18 cases cho Integer) và Boundary Rules hoạt động ĐỘC LẬP, dẫn đến cùng 1 giá trị được test 2 lần.

**Quy trình bắt buộc (3 bước):**

**Bước 1 — Thu thập base cases:** Lấy tất cả cases từ template bảng. Đánh dấu mỗi case bằng nhãn loại: type-group.

**Bước 2 — Thu thập constraint cases:** Dựa vào rsdConstraints (min, max, maxDecimalPlaces...) → tính constraint values.

**Bước 3 — MERGE loại bỏ overlap:**

| Base case (template) | Trùng với constraint nào? | Hành động |
|----------------------|---------------------------|-----------|
| "Số âm" (VD: -1) | min-1 | **MERGE** → dùng boundary case, BỎ base case |
| "Số thập phân" (VD: 1.5) | maxDecimalPlaces boundary | **MERGE** → dùng boundary case, BỎ base case |
| "maxLength-1/max/max+1" | String maxLength | **MERGE** → dùng boundary case |
| "Số 0" | min=0 hoặc max=0 | **MERGE** → dùng boundary case |
| "Boolean" (true/false) | Không trùng number | GIỮ base case |
| "XSS", "SQL", "Object", "Mảng" | Không trùng | GIỮ base case |
| "Leading zero", "Số rất lớn" | Không trùng | GIỮ base case |

**Ví dụ min=0, max=100, maxDecimalPlaces=2 (warningYellowPct):**

```
❌ SAI (trùng lặp):
   Base: "Số âm" → error  (test -1)
   Base: "Số thập phân" → error  (test 1.5)
   Boundary: "Kiểm tra = -1 (min-1)" → error  (test -1 lần 2!)
   Boundary: "Kiểm tra = 1.5 (decimal hợp lệ)" → success  (test 1.5 lần 2!)

✅ ĐÚNG (sau merge):
   Base (non-overlap): Boolean, XSS, SQL, Object, Mảng, Leading zero, Số rất lớn...
   + Boundary (MERGED): -1, 0, 100, 101
   + Decimal (MERGED): 1.5, 1.55, 1.555
   = TỔNG: ~9-12 cases (thay vì 21+)
```

**Min counts sau MERGE (ước tính):**

| Type | Trước merge | Sau merge (ước tính) |
|------|------|------------|-----------------|
| Number min=0,max=100,decimal=2 | ~25 | ~9-12 |
| Number chỉ có min/max | ~22 | ~6-8 |
| Integer Required (có boundary) | ~22 | ~6-8 |
| String Required (maxLength=100) | ~17 | ~17 |

> **Lưu ý:** min_case_counts vẫn giữ nguyên ≥18 cho Number Required — nhưng sau MERGE, số case thực tế sẽ giảm đáng kể. Rule đảm bảo KHÔNG THIẾU cases, không phải LUÔN ĐẠT ≥18.

**CRITICAL — Space cases:** `Space ở giữa`, `All space`, `Space đầu/cuối` là 3 case **hoàn toàn khác nhau** — TUYỆT ĐỐI KHÔNG merge.

### Quy tắc ký tự đặc biệt cho String

Đọc `rsdConstraints.allowSpecialChars` + `rsdConstraints.allowedChars` trong inventory:

| inventory có `allowedChars`? | Sinh cases |
|------------------------------------|-----------|
| Có (VD: `["_", "-"]`) | Tách 2 case: "cho phép (_, -)" → success + "không cho phép (!@#$%^&*)" → error |
| Không có / null | 1 case chung "ký tự đặc biệt" → error |

**CRITICAL:** Case "không cho phép" LUÔN LUÔN error.

### Per-field output format

Heading field: `### Trường {fieldName}`

Mỗi case = 1 **bullet** `- Kiểm tra ...` + response lồng trong, theo format:

```markdown
### Trường {fieldName}

- Kiểm tra không truyền trường {fieldName}

    - 1. Check api trả về:
      1.1.Status: 200
      1.2.Response:
      {
          "code": "LDH_..._020",
          "message": "Dữ liệu đầu vào không hợp lệ"
      }

- Kiểm tra truyền trường {fieldName} = null

    - 1. Check api trả về:
      1.1.Status: 200
      1.2.Response:
      {
      }
```

**Quy tắc bắt buộc:**
- Case heading: `- Kiểm tra ...` (KHÔNG dùng `####`)
- Response: thụt vào 4 spaces dưới bullet cha: `    - 1. Check api trả về:`
- JSON mở đầu ngay sau `1.2.Response:` trên dòng tiếp theo
- JSON body thụt 6 spaces: `      "code": "..."`

**⛔ Quy tắc heading — TUYỆT ĐỐI KHÔNG vi phạm:**
- Heading mô tả **ĐIỀU KIỆN kiểm tra**, KHÔNG chứa giá trị cụ thể truyền vào
- SAI: `- Kiểm tra truyền trường slaName = " test "` (chứa giá trị)
- SAI: `- Kiểm tra truyền trường slaName = "SLA xử lý Báo cáo"` (chứa giá trị)
- ĐÚNG: `- Kiểm tra truyền trường slaName có khoảng trắng đầu/cuối`
- ĐÚNG: `- Kiểm tra truyền trường slaName = {maxLen+1} ký tự`
- ĐÚNG: `- Kiểm tra truyền trường slaName chứa ký tự đặc biệt`
- Ngoại lệ duy nhất: `= null`, `= ""`, `= 0`, `= true/false` — đây là từ khóa kỹ thuật, KHÔNG phải giá trị test

---

<!-- @section: String Required -->
### STRING Required — ≥ 17 cases (từ fieldTestTemplates.js)

**Cases BẮT BUỘC** (mapping từ `generateStringFieldTests(fieldName, isRequired=true, maxLength)`):

| # | Case | Response mặc định | Ghi chú |
|---|------|--------------------|---------|
| 1 | Để trống ("") | → error | |
| 2 | Không truyền field | → error | |
| 3 | Truyền null | → error | |
| 4 | {maxLen-1} ký tự hợp lệ | → success | Chỉ khi có maxLength |
| 5 | {maxLen} ký tự hợp lệ | → success | Chỉ khi có maxLength |
| 6 | {maxLen+1} ký tự hợp lệ | → error | Chỉ khi có maxLength |
| 7 | Ký tự số | → success | |
| 8 | Chữ thường/hoa không dấu | → success | |
| 9 | Chữ có dấu tiếng Việt | → error | Theo RSD: `rsdConstraints.allowAccents` (mặc định: error) |
| 10 | Ký tự đặc biệt | → error | Theo RSD: `rsdConstraints.allowSpecialChars` + `allowedChars` (mặc định: error) |
| 11 | All space | → error | |
| 12 | Space ở giữa | → error | |
| 13 | Space đầu/cuối | → error | |
| 14 | XSS (`<script>alert(1)</script>`) | → error | |
| 15 | SQL Injection (`' OR 1=1 --`) | → error | |
| 16 | Object ({}) | → error | |
| 17 | Mảng ([]) | → error | |

> Không có maxLength → bỏ case 4, 5, 6 → ≥ 14 cases.

---

<!-- @section: String Optional -->
### STRING Optional — ≥ 17 cases (từ fieldTestTemplates.js)

**Cases BẮT BUỘC** (mapping từ `generateStringFieldTests(fieldName, isRequired=false, maxLength)`):

| # | Case | Response mặc định | Ghi chú |
|---|------|--------------------|---------|
| 1 | Để trống ("") | → success | Khác Required |
| 2 | Không truyền field | → success | Khác Required |
| 3 | Truyền null | → success | Khác Required |
| 4 | {maxLen-1} ký tự hợp lệ | → success | Chỉ khi có maxLength |
| 5 | {maxLen} ký tự hợp lệ | → success | Chỉ khi có maxLength |
| 6 | {maxLen+1} ký tự hợp lệ | → error | Chỉ khi có maxLength |
| 7 | Ký tự số | → success | |
| 8 | Chữ thường/hoa không dấu | → success | |
| 9 | Chữ có dấu tiếng Việt | → error | Theo RSD: `rsdConstraints.allowAccents` (mặc định: error) |
| 10 | Ký tự đặc biệt | → error | Theo RSD: `rsdConstraints.allowSpecialChars` + `allowedChars` (mặc định: error) |
| 11 | All space | → error | |
| 12 | Space ở giữa | → error | |
| 13 | Space đầu/cuối | → error | |
| 14 | XSS (`<script>alert(1)</script>`) | → error | |
| 15 | SQL Injection (`' OR 1=1 --`) | → error | |
| 16 | Object ({}) | → error | |
| 17 | Mảng ([]) | → error | |

> Không có maxLength → bỏ case 4, 5, 6 → ≥ 14 cases.

---

<!-- @section: Integer Required -->
<!-- @section: Integer Required -->
### INTEGER Required (no default) — base 15 cases + boundary cases (nếu inventory CÓ constraint)

**⛔ CẤU TRÚC BẮT BUỘC — Đọc kỹ trước khi sinh:**

**A. Base cases (LUÔN LUÔN sinh):**

| # | Case | Response mặc định |
|---|------|--------------------|
| 1 | Để trống | → error |
| 2 | Không truyền | → error |
| 3 | Truyền null | → error |
| 4 | Số rất lớn vượt giới hạn Integer | → error |
| 5 | Chuỗi ký tự | → error |
| 6 | Chuỗi chữ lẫn số | → error |
| 7 | Ký tự đặc biệt | → error |
| 8 | All space | → error |
| 9 | Space đầu/cuối | → error |
| 10 | Space ở giữa | → error |
| 11 | Boolean | → error |
| 12 | XSS | → error |
| 13 | SQL Injection | → error |
| 14 | Object | → error |
| 15 | Mảng | → error |

**B. Boundary cases (CHỈ sinh khi inventory CÓ rsdConstraints rõ ràng):**

| # | Case | Ghi chú |
|---|------|---------|
| 16 | Boundary min-1 → error | **THAY THẾ** "Số âm" trong base (không cộng thêm) |
| 17 | Boundary min → success | |
| 18 | Boundary max → success | |
| 19 | Boundary max+1 → error | |
| 20 | maxDigits-1 chữ số → success | Chỉ khi có maxDigits |
| 21 | maxDigits chữ số → success | |
| 22 | maxDigits+1 chữ số → error | |

**⛔ R7 MERGE (QUAN TRỌNG):**
- B16–B19 **THAY THẾ**, không cộng thêm. Nếu inventory có min/max → sinh B16–B19 **thay cho** "Số âm" trong base.
- Nếu inventory **KHÔNG CÓ** min/max/maxDigits → **CHỈ sinh phần A (15 cases)**, không tự suy ra boundary.
- **KHÔNG sinh giá trị trung gian** (1, 50, 99...). Chỉ sinh đúng boundary values.

---


<!-- @section: Integer Default -->
### INTEGER with Default Value — ≥ 18 cases

Heading: `### {fieldName}: Integer (Required, default = {defaultValue})`

> Cùng cases như INTEGER Required, NGOẠI TRỪ: Để trống / Không truyền / Truyền null → **success** + ghi chú "Hệ thống sử dụng default {fieldName} = {defaultValue}".

| # | Case | Response mặc định | Ghi chú |
|---|------|--------------------|---------|
| 1 | Để trống | → success + ghi chú default | Khác Required |
| 2 | Không truyền | → success + ghi chú default | Khác Required |
| 3 | Truyền null | → success + ghi chú default | Khác Required |
| 4 | Số âm (VD: -1) | → error | |
| 5 | Số thập phân (VD: 1.5) | → error | |
| 6 | Số có leading zero (VD: 00123) | → error | |
| 7 | Số rất lớn vượt giới hạn Integer | → error | |
| 8 | Chuỗi ký tự (VD: "abc") | → error | |
| 9 | Chuỗi chữ lẫn số (VD: "10abc000") | → error | |
| 10 | Ký tự đặc biệt (VD: @#$%, *, -, +) | → error | |
| 11 | All space | → error | |
| 12 | Space đầu/cuối (VD: " 123 ") | → error | |
| 13 | Space ở giữa (VD: "1 23") | → error | |
| 14 | Boolean (true/false) | → error | |
| 15 | XSS (`<script>alert(1)</script>`) | → error | |
| 16 | SQL Injection (`' OR 1=1 --`) | → error | |
| 17 | Object | → error | |
| 18 | Mảng | → error | |

---

<!-- @section: Integer Optional -->
### INTEGER Optional — ≥ 18 cases

Heading: `### {fieldName}: Integer (Optional)`

> Cùng cases như INTEGER Required, NGOẠI TRỪ: Để trống / Không truyền / Truyền null → **success**.

| # | Case | Response mặc định | Ghi chú |
|---|------|--------------------|---------|
| 1 | Để trống | → success | Khác Required |
| 2 | Không truyền | → success | Khác Required |
| 3 | Truyền null | → success | Khác Required |
| 4–18 | (giống INTEGER Required cases 4–18) | → error |
---

<!-- @section: JSONB Required -->
### JSONB Required — 14 cases

| # | Case | Response mặc định |
|---|------|-------------------|
| 1 | Để trống | → error |
| 2 | Không truyền | → error |
| 3 | Truyền null | → error |
| 4 | JSON sai syntax (không parse được) | → error |
| 5 | Mảng `[]` thay vì object | → error |
| 6 | Chuỗi rỗng | → error |
| 7 | String thuần (không phải JSON) | → error |
| 8 | Number | → error |
| 9 | Boolean | → error |
| 10 | XSS trong JSON value | → error |
| 11 | SQL injection trong JSON value | → error |
| 12 | JSON hợp lệ | → success |
| 13 | JSON sai format nghiệp vụ (thiếu trường bắt buộc) | → Theo RSD (mặc định: error) |
| 14 | Object rỗng `{}` | → Theo RSD (mặc định: error) |

---

<!-- @section: JSONB Optional -->
### JSONB Optional — 12 cases

> Giống JSONB Required, NGOẠI TRỪ: Để trống / Không truyền / Truyền null → **success**.

---

<!-- @section: Date Required -->
### DATE Required — ≥ 15 cases (từ fieldTestTemplates.js)

**Cases BẮT BUỘC** (mapping từ `generateDateFieldTests(fieldName, isRequired=true, constraints, dateFormat)`):

| # | Case | Response mặc định | Ghi chú |
|---|------|--------------------|---------|
| 1 | Để trống | → error | |
| 2 | Không truyền | → error | |
| 3 | Truyền null | → error | |
| 4 | Đúng định dạng (VD: 25/12/2024) | → success | Format theo PTTK/RSD |
| 5 | Sai định dạng (VD: yyyy/dd/MM thay vì dd/MM/yyyy) | → error | |
| 6 | Chuỗi không phải ngày tháng (VD: "abc123") | → error | |
| 7 | Ngày không tồn tại (VD: 30/02/2025, 32/01/2025) | → error | |
| 8 | Ngày quá khứ (VD: 01/01/2020) | → Theo RSD: `rsdConstraints.allowPastDate` (mặc định: success) | |
| 9 | Ngày hiện tại | → Theo RSD: `rsdConstraints.allowCurrentDate` (mặc định: success) | |
| 10 | Ngày tương lai (VD: 31/12/2099) | → Theo RSD: `rsdConstraints.allowFutureDate` (mặc định: success) | |
| 11 | Số nguyên | → error | |
| 12 | XSS (`<script>alert(1)</script>`) | → error | |
| 13 | SQL Injection (`' OR 1=1 --`) | → error | |
| 14 | Object | → error | |
| 15 | Mảng | → error | |

**So sánh với Date field khác (khi có ràng buộc):**

Đọc `rsdConstraints.crossFieldRules` trong inventory. Khi một Date field có ràng buộc so sánh với Date field khác (VD: `expiredDate` phải >= `effectiveDate`), thêm các case NGAY TRONG section `###` của field đó:

- {fieldName} nhỏ hơn {relatedField} → error
- {fieldName} bằng {relatedField} → spec-dependent
- {fieldName} lớn hơn {relatedField} → success

---

<!-- @section: Date Optional -->
### DATE Optional — ≥ 15 cases

> Giống DATE Required, NGOẠI TRỪ: Để trống / Không truyền / Truyền null → **success**.

---

<!-- @section: DateTime Required -->
### DATETIME Required — ≥ 18 cases (từ fieldTestTemplates.js)

**Cases BẮT BUỘC** (mapping từ `generateDateTimeFieldTests(fieldName, isRequired=true, constraints, dateFormat)`):

| # | Case | Response mặc định | Ghi chú |
|---|------|--------------------|---------|
| 1 | Để trống | → error | |
| 2 | Không truyền | → error | |
| 3 | Truyền null | → error | |
| 4 | Đúng định dạng (VD: 25/12/2024 14:30:45) | → success | Format theo PTTK/RSD |
| 5 | Sai định dạng ngày (VD: yyyy/dd/MM HH:mm:ss) | → error | |
| 6 | Sai định dạng giờ (VD: 25/12/2024 25:70:90) | → error | |
| 7 | Chỉ có ngày không có giờ (VD: 25/12/2024) | → error | |
| 8 | Chuỗi không phải ngày giờ (VD: "abc123") | → error | |
| 9 | Ngày không tồn tại (VD: 30/02/2025 14:30:45) | → error | |
| 10 | Ngày giờ quá khứ (VD: 01/01/2020 10:00:00) | → Theo RSD: `rsdConstraints.allowPastDateTime` (mặc định: success) | |
| 11 | Ngày giờ hiện tại | → Theo RSD: `rsdConstraints.allowCurrentDateTime` (mặc định: success) | |
| 12 | Ngày giờ tương lai (VD: 31/12/2099 23:59:59) | → Theo RSD: `rsdConstraints.allowFutureDateTime` (mặc định: success) | |
| 13 | Số nguyên | → error | |
| 14 | XSS (`<script>alert(1)</script>`) | → error | |
| 15 | SQL Injection (`' OR 1=1 --`) | → error | |
| 16 | Object | → error | |
| 17 | Mảng | → error | |

---

<!-- @section: DateTime Optional -->
### DATETIME Optional — ≥ 18 cases

> Giống DATETIME Required, NGOẠI TRỪ: Để trống / Không truyền / Truyền null → **success**.

---

<!-- @section: Array Required -->
### ARRAY Required — ≥ 15 cases (từ fieldTestTemplates.js)

**Cases BẮT BUỘC** (mapping từ `generateArrayFieldTests(fieldName, isRequired=true, childFieldNames)`):

| # | Case | Response mặc định |
|---|------|-------------------|
| 1 | Không truyền | → error |
| 2 | Truyền null | → error |
| 3 | Mảng rỗng `[]` | → error |
| 4 | Mảng chứa phần tử rỗng `[{}]` | → error |
| 5 | String thay vì array | → error |
| 6 | Number thay vì array | → error |
| 7 | Object thay vì array | → error |
| 8 | Boolean thay vì array | → error |
| 9 | XSS (`<script>alert(1)</script>`) | → error |
| 10 | SQL Injection (`' OR 1=1 --`) | → error |
| 11 | Mảng 1 phần tử hợp lệ | → Theo RSD |
| 12 | Mảng nhiều phần tử hợp lệ | → Theo RSD |
| 13 | Mảng có phần tử trùng nhau (duplicate values) | → Theo RSD |
| 14 | Mảng có phần tử là String (sai kiểu) | → error |
| 15 | Mảng có phần tử là Integer/Number (sai kiểu) | → error |

> **Lưu ý:** Case 14–15 áp dụng khi array chứa phần tử có kiểu xác định (VD: array of objects). Nếu array of primitives thì điều chỉnh theo kiểu phần tử mong đợi.

> Với Array có child fields: sinh thêm validate cases cho từng child field riêng (`### {childFieldName}`).

---

<!-- @section: Array Optional -->
### ARRAY Optional — ≥ 15 cases

> Giống ARRAY Required, NGOẠI TRỪ: Không truyền / Truyền null → **success**.

---

<!-- @section: Long -->
### INTEGER / LONG — cùng template, khác heading

Cả `int`/`Integer`/`integer` và `long`/`Long` đều dùng **INTEGER Required** template (≥ 18 cases).

- Type trong PTTK/RSD là `int` / `Integer` / `integer` → Heading: `### {fieldName}: Integer (Required)`
- Type trong PTTK/RSD là `long` / `Long` → Heading: `### {fieldName}: Long (Required)`

**CRITICAL:** KHÔNG dùng "Long" heading cho field có type `int`/`Integer`.

---

<!-- @section: Boolean Required -->
### BOOLEAN Required — 11 cases

| # | Case | Response mặc định |
|---|------|-------------------|
| 1 | Để trống | → error |
| 2 | Không truyền | → error |
| 3 | Truyền null | → error |
| 4 | Số khác 0 và 1 | → error |
| 5 | Chuỗi bất kỳ (abc) | → error |
| 6 | Mảng | → error |
| 7 | Object | → error |
| 8 | true | → success |
| 9 | false | → success |
| 10 | Chuỗi "true" / "false" | → Theo RSD (mặc định: error) |
| 11 | Số nguyên (0/1) | → Theo RSD (mặc định: error) |

---

<!-- @section: Boolean Optional -->
### BOOLEAN Optional — 9 cases

> Giống BOOLEAN Required, NGOẠI TRỪ: Để trống / Không truyền / Truyền null → **success**.

---

<!-- @section: MultipartFile Required -->
### MULTIPARTFILE Required — ≥ 16 cases (từ fieldTestTemplates.js)

**Cases BẮT BUỘC** (mapping từ `generateMultipartFileFieldTests(fieldName, isRequired=true, constraints)`):

Đọc `fieldConstraints[].rsdConstraints` trong inventory để lấy:
- `allowedExtensions`: danh sách extension hợp lệ (VD: `[".xls", ".xlsx"]`)
- `maxFileSizeMB`: giới hạn dung lượng (VD: `10` cho 10MB)
- `maxRecords`: giới hạn số bản ghi (VD: `1000`)
- `allowedChars`: ký tự cho phép trong tên file
- `allowDuplicate`: có cho phép trùng tên file hay không

|| # | Case | Response mặc định | Ghi chú |
||---|------|--------------------|---------|
|| 1 | Để trống field file (`"${fieldName}": ""`) | → error | |
|| 2 | Không truyền field file (body rỗng `{}`) | → error | |
|| 3 | Truyền `${fieldName} = null` | → error | |
|| 4 | Truyền file rỗng (0 byte) | → error | |
|| 5 | File có định dạng hợp lệ `.xls` | → success | Chỉ khi `allowedExtensions` có `.xls` |
|| 6 | File có định dạng hợp lệ `.xlsx` | → success | Chỉ khi `allowedExtensions` có `.xlsx` |
|| 7 | File có định dạng không hợp lệ `.pdf` | → error (GOV0014) | |
|| 8 | File vượt dung lượng tối đa | → error (GOV0015) | Chỉ khi `maxFileSizeMB` có giá trị |
|| 9 | File vượt số bản ghi tối đa | → error (GOV0016) | Chỉ khi `maxRecords` có giá trị |
|| 10 | File có tên chứa ký tự đặc biệt không thuộc danh sách cho phép | → error (GOV0017) | Theo `allowedChars` |
|| 11 | File có tên chứa khoảng trắng | → success hoặc error | Theo `allowedChars` |
|| 12 | File có tên chứa dấu tiếng Việt | → success hoặc error | Theo `allowedChars` |
|| 13 | File trùng tên với file ở trạng thái Đang kiểm tra (cùng CIF) | → error (GOV0018) | Theo `allowDuplicate` |
|| 14 | File trùng tên với file ở trạng thái Đã kiểm tra (cùng CIF) | → error (GOV0018) | Theo `allowDuplicate` |
|| 15 | File trùng tên với file ở trạng thái Đã đẩy duyệt (cùng CIF) | → error (GOV0018) | Theo `allowDuplicate` |
|| 16 | File trùng tên với file có lỗi kiểm tra (cùng CIF) | → success | File có lỗi không thuộc trùng lặp |
|| 17 | File không đúng template/mẫu (thiếu cột bắt buộc) | → error (GOV0014 hoặc GOV0019) | |
|| 18 | File có nội dung trống (không có dữ liệu) | → error (GOV0019) | |

> Nếu `allowDuplicate = true` → bỏ case 13–15 (không trùng lặp).
> Nếu không có `maxFileSizeMB` → bỏ case 8.
> Nếu không có `maxRecords` → bỏ case 9.
> `allowedChars` nếu không có trong inventory → dùng default: `["_", "-", ".", "(", ")"]`.

---

<!-- @section: FileContentField TextInput -->
### FILE CONTENT FIELD — TextInput (trường text bên trong file upload)

**Áp dụng khi:** API có MultipartFile input VÀ inventory có `fileContentFields[]` với `inputType = "TextInput"`.

**Heading format:** `### Trường {displayName} trong file`

**Cases BẮT BUỘC:** Sinh từ thông tin trong `fileContentFields[].allowedChars`, `maxLength`, `allowAccents`, `allowSpaces`, `crossFieldRules`, `businessValidation`.

| # | Case | Response mặc định | Điều kiện |
|---|------|--------------------|-----------|
| 1 | Để trống {displayName} | → error | Khi required = Y |
| 2 | Nhập {displayName} all space | → error | |
| 3 | Nhập {displayName} = {maxLength} ký tự | → success | Khi có maxLength |
| 4 | Nhập {displayName} = {maxLength+1} ký tự | → error | Khi có maxLength |
| 5 | Nhập {displayName} = {maxLength-1} ký tự | → success | Khi có maxLength |
| 6 | Nhập {displayName} là các ký tự đặc biệt thuộc danh sách cho phép | → success | Khi allowedChars có ký tự đặc biệt |
| 7 | Nhập {displayName} là các ký tự đặc biệt ngoài danh sách cho phép | → error | |
| 8 | Nhập {displayName} có dấu tiếng Việt | → success hoặc error | Theo allowAccents |
| 9 | Nhập {displayName} có khoảng trắng kép, tab, enter, space đầu/cuối | → success (chuẩn hóa) | Khi có autoFormat |
| 10 | Nhập {displayName} có số 0 ở đầu | → success (hệ thống xử lý) | Khi có leadingZeroRule |
| 11 | Nhập {displayName} có space ở giữa | → Theo allowSpaces | |

**Cases từ crossFieldRules:** Mỗi crossFieldRule → 1 case riêng.
VD: "Nhập MST người nộp thuế khác MST tài khoản sử dụng" → error "Mã số người thuế không khớp"

**Cases từ businessValidation:** Mỗi businessValidation rule → 1 case riêng.
VD: "Nhập TK trích nợ user không được phân quyền" → error "Tài khoản không được phân quyền"

**Cases conditional required:**
Khi required = conditional → thêm 2 cases:
- "Để trống {displayName} khi điều kiện {condition} = true" → error
- "Để trống {displayName} khi điều kiện {condition} = false" → success

> **Format heading:** "Kiểm tra truyền file hợp lệ, nội dung file {mô tả case}"

---

<!-- @section: FileContentField NumberInput -->
### FILE CONTENT FIELD — NumberInput (trường số bên trong file upload)

| # | Case | Response mặc định | Điều kiện |
|---|------|--------------------|-----------|
| 1 | Để trống {displayName} | → error | Khi required = Y |
| 2 | Nhập {displayName} all space | → error | |
| 3 | Nhập {displayName} = 0 | → Theo spec | |
| 4 | Nhập {displayName} = {maxLength} ký tự số | → success | Khi có maxLength |
| 5 | Nhập {displayName} = {maxLength+1} ký tự số | → error | Khi có maxLength |
| 6 | Nhập {displayName} = {maxLength-1} ký tự số | → success | Khi có maxLength |
| 7 | Nhập {displayName} là chữ | → error | |
| 8 | Nhập {displayName} là ký tự đặc biệt | → error | |
| 9 | Nhập {displayName} là số âm | → error | |
| 10 | Nhập {displayName} là số thập phân | → error hoặc success | Theo spec |
| 11 | Nhập {displayName} có số 0 ở đầu | → success (chuẩn hóa) | Khi có leadingZeroRule |

**Cases từ businessValidation:** Mỗi rule → 1 case.
VD:
- "Nhập số tiền > số tiền tối đa" → error
- "Nhập số tiền < số tiền tối thiểu" → error
- "Nhập số tiền vượt hạn mức KH từng giao dịch" → error
- "Nhập số tiền vượt hạn mức TK từng giao dịch" → error

---

<!-- @section: FileContentField DateInput -->
### FILE CONTENT FIELD — DateInput (trường ngày bên trong file upload)

| # | Case | Response mặc định |
|---|------|-------------------|
| 1 | Để trống {displayName} | → error (khi required = Y) |
| 2 | Nhập {displayName} không đúng định dạng {dateFormat} | → error |
| 3 | Nhập {displayName} là ngày hiện tại | → success |
| 4 | Nhập {displayName} là ngày tương lai | → error hoặc success (theo spec) |
| 5 | Nhập {displayName} là ngày quá khứ | → success hoặc error (theo spec) |

---

<!-- @section: FileContentField Droplist -->
### FILE CONTENT FIELD — Droplist (trường chọn từ danh sách bên trong file upload)

| # | Case | Response mặc định | Điều kiện |
|---|------|--------------------|-----------|
| 1 | Để trống {displayName} | → error | Khi required = Y |
| 2 | Nhập {displayName} all space | → error | |
| 3 | Nhập {displayName} không có trong {referenceTable} | → error | |
| 4 | Nhập {displayName} có trong {referenceTable} nhưng không thuộc {parentField} đã chọn | → error | Khi có parentField |
| 5 | Nhập {displayName} hợp lệ | → success | |

**Cases từ businessValidation:** VD:
- "Nhập Mã kho bạc không tồn tại" → error "Mã kho bạc nhà nước không hợp lệ"
- "Nhập Mã kho bạc tồn tại nhưng trạng thái không hoạt động" → error

---

<!-- @section: FileContentField CrossField -->
### FILE CONTENT FIELD — Cross-field & Business Logic (logic liên trường / nghiệp vụ)

Sinh thêm các case từ logic validate PTTK section 4.x mà KHÔNG thuộc riêng 1 field cụ thể:

| # | Case | Response mặc định |
|---|------|-------------------|
| 1 | Trùng thông tin bản ghi trong cùng file (theo tiêu chí check trùng) | → error |
| 2 | Giao dịch thuộc tham số xử lý thủ công | → Theo spec |
| 3 | Giao dịch thuộc tham số ngừng giao dịch | → error |
| 4 | Gọi TCC validate không nhận phản hồi | → error |

> Các cases này đặt trong section riêng: `### Logic nghiệp vụ liên trường trong file`

---

<!-- @section: FileContentField output-format -->
### FILE CONTENT FIELD — Output format

**Heading cấp section:** `## Kiểm tra Validate nội dung file`

Đặt SAU section `## Kiểm tra Validate` (validate API params) và TRƯỚC `## Kiểm tra chức năng`.

**Format cho từng trường:**
```markdown
## Kiểm tra Validate nội dung file

### Trường Tài khoản chuyển

- Kiểm tra truyền file hợp lệ, nội dung file Để trống Tài khoản chuyển

    - 1. Check api trả về:
      1.1.Status: 200
      1.2.Response: Theo RSD — bản ghi không hợp lệ, mô tả lỗi tại cột mô tả

- Kiểm tra truyền file hợp lệ, nội dung file Nhập Tài khoản chuyển 14 ký tự

    - 1. Check api trả về:
      1.1.Status: 200
      1.2.Response: Bản ghi hợp lệ

### Trường Mã Số thuế người nộp thuế

...

### Logic nghiệp vụ liên trường trong file

- Kiểm tra truyền file hợp lệ, nội dung file Nhập trùng thông tin bản ghi

    - 1. Check api trả về:
      1.1.Status: 200
      1.2.Response: error_code: "Có bản ghi trùng lặp..."
```

**⚠️ CRITICAL — Response cho file content field:**
- File content fields validate qua **job bất đồng bộ** → response KHÔNG trả lỗi trực tiếp qua API upload
- API upload trả SUCCESS (batchNo, batchId), sau đó job validate từng bản ghi
- Kết quả validate hiển thị tại tab "Bản ghi hợp lệ" / "Bản ghi không hợp lệ" với mô tả lỗi cụ thể
- Response format: mô tả trạng thái bản ghi + mô tả lỗi (nếu có), KHÔNG dùng error code API

---

<!-- @section: Number Required -->
### NUMBER Required (decimal/float) — base 15 cases + boundary cases (nếu inventory CÓ constraint)

**⛔ CẤU TRÚC BẮT BUỘC — Đọc kỹ trước khi sinh:**

**A. Base cases (LUÔN LUÔN sinh):**

| # | Case | Response mặc định |
|---|------|--------------------|
| 1 | Để trống | → error |
| 2 | Không truyền | → error |
| 3 | Truyền null | → error |
| 4 | Số có leading zero | → error |
| 5 | Số rất lớn vượt giới hạn | → error |
| 6 | Chuỗi ký tự | → error |
| 7 | Chuỗi chữ lẫn số | → error |
| 8 | Ký tự đặc biệt | → error |
| 9 | All space | → error |
| 10 | Boolean | → error |
| 11 | XSS | → error |
| 12 | SQL Injection | → error |
| 13 | Object | → error |
| 14 | Mảng | → error |

**B. Boundary cases (CHỈ sinh khi inventory CÓ rsdConstraints rõ ràng):**

| # | Case | Ghi chú |
|---|------|---------|
| 15 | Boundary min-1 → error | **THAY THẾ** base "Số âm" (không cộng thêm) |
| 16 | Boundary min → success | |
| 17 | Boundary max → success | |
| 18 | Boundary max+1 → error | |
| 19 | Decimal hợp lệ 1 (VD: 1.5) → success | **THAY THẾ** base "Số thập phân" (không cộng thêm) |
| 20 | Decimal hợp lệ 2 (VD: 1.55) → success | |
| 21 | Decimal vượt quá (VD: 1.555) → error | |

**⛔ R7 MERGE (QUAN TRỌNG):**
- B15–B18 **THAY THẾ** "Số âm" trong base. B19–B21 **THAY THẾ** "Số thập phân" trong base. KHÔNG cộng thêm.
- Nếu inventory **KHÔNG CÓ** min/max/maxDecimalPlaces → **CHỈ sinh phần A (14 cases)**, không tự suy ra boundary.
- Số cases sau MERGE: có min+max+decimal → ~12–15 cases; không có constraint → 14 cases.

---

<!-- @section: Number Optional -->
### NUMBER Optional — ≥ 18 cases (sau MERGE: ~9-12)

> **⛔ ÁP DỤNG R7 MERGE:** Giống NUMBER Required, VỚI thay đổi:
> - Để trống / Không truyền / Truyền null → **success**
> - Boundary cases → **error** (vì giá trị nằm ngoài range)

**Cases sau khi MERGE:**

| # | Case | Response mặc định | Ghi chú |
|---|------|--------------------|---------|
| 1 | Để trống | → success | Khác Required |
| 2 | Không truyền | → success | Khác Required |
| 3 | Truyền null | → success | Khác Required |
| 4 | Boundary min-1 | → error | |
| 5 | Boundary min | → success | |
| 6 | Boundary max | → success | |
| 7 | Boundary max+1 | → error | |
| 8 | Decimal hợp lệ (VD: 1.5) | → success | |
| 9 | Decimal hợp lệ (VD: 1.55) | → success | |
| 10 | Decimal vượt quá (VD: 1.555) | → error | |
| 11 | Số có leading zero | → error | |
| 12 | Số rất lớn | → error | |
| 13 | Chuỗi ký tự | → error | |
| 14 | Chuỗi chữ lẫn số | → error | |
| 15 | Ký tự đặc biệt | → error | |
| 16 | All space | → error | |
| 17 | Boolean | → error | |
| 18 | XSS / SQL Injection / Object / Mảng | → error | |

> **Lưu ý:** Number Optional KHÔNG bỏ trống → vẫn error (khác với String Optional).

---

<!-- @section: checkpoint -->
### Per-field checkpoint (bắt buộc sau MỖI field)

```
Field {fieldName} ({type}): {generated}/{min} cases. Missing: [list] → THÊM ngay.
```

Min counts: String Required ≥ 17 | String Optional ≥ 17 | Integer Required ≥ 18 | Integer with Default ≥ 18 | Integer Optional ≥ 18 | Long ≥ 18 | JSONB Required ≥ 14 | JSONB Optional ≥ 12 | Date Required ≥ 15 | Date Optional ≥ 15 | DateTime Required ≥ 17 | DateTime Optional ≥ 17 | Array Required ≥ 15 | Array Optional ≥ 15 | Boolean Required ≥ 11 | Boolean Optional ≥ 9 | Number Required ≥ 18 | Number Optional ≥ 18 | **MultipartFile Required ≥ 16 | MultipartFile Optional ≥ 14**

---

<!-- @section: main-flow -->
## Phase 4: Kiểm tra luồng chính

### Bước 4.0: Xác định luồng con (BẮT BUỘC trước khi viết bất kỳ test case nào)

Đọc RSD và liệt kê TẤT CẢ các sub-flow (luồng con) của API này. Ví dụ:

| API loại | Các luồng con thường gặp |
|----------|--------------------------|
| Tạo mới | Lưu nháp, Gửi duyệt |
| Chỉnh sửa | Chỉnh sửa + Lưu, Chỉnh sửa + Gửi duyệt |
| Phê duyệt | Duyệt, Từ chối, Yêu cầu bổ sung |
| Xóa | Xóa 1 bản ghi, Xóa nhiều bản ghi |

**⛔ RANH GIỚI LUỒNG — chỉ liệt kê luồng con THUỘC API NÀY, KHÔNG liệt kê luồng của API khác:**

| Ví dụ API được yêu cầu | Được liệt kê (luồng của API này) | KHÔNG liệt kê (luồng của API khác) |
|------------------------|-----------------------------------|--------------------------------------|
| API Tạo SLA | Lưu nháp, Gửi duyệt | Duyệt SLA, Từ chối SLA, Chỉnh sửa SLA |
| API Phê duyệt SLA | Duyệt, Từ chối, Yêu cầu bổ sung | Tạo SLA, Chỉnh sửa SLA |
| API Tìm kiếm | Tìm thấy kết quả, Không tìm thấy | Tạo mới, Xóa |

**⚠️ TUYỆT ĐỐI KHÔNG trộn lẫn test cases của các luồng con khác nhau.** Mỗi luồng con PHẢI có heading `####` riêng trong `## Kiểm tra luồng chính`. Ví dụ:

```markdown
## Kiểm tra luồng chính

#### Luồng lưu nháp
### Kiểm tra response khi lưu nháp thành công
...

#### Luồng gửi duyệt
### Kiểm tra response khi gửi duyệt thành công
...
```

Nếu API chỉ có 1 luồng duy nhất → không cần heading phân nhóm. Nhưng nếu có ≥ 2 luồng → BẮT BUỘC tách heading.

### ⚠️ QUY TẮC QUAN TRỌNG NHẤT

**MỌI test case trong luồng chính PHẢI có response:**
```
- 1\. Check api trả về:
      1\.1. Status: {status_code}
      1\.2. Response:
      {
        ...response body theo PTTK/RSD...
      }
      SQL:
      SELECT ... FROM ... WHERE ...;
```

**TUYỆT ĐỐI KHÔNG** viết test case không có response.

**⚠️ KHÔNG duplicate validate cases vào luồng chính.** Bất kỳ case nào đã có trong "Kiểm tra validate" → KHÔNG viết lại vào luồng chính, kể cả:
- Lỗi kiểu dữ liệu: sai kiểu, bỏ trống, vượt maxLength, null...
- Lỗi format date: sai định dạng, ngày không tồn tại, ngày quá khứ, ngày tương lai, ngày hiện tại
- So sánh date: expiredDate < effectiveDate, expiredDate = effectiveDate, expiredDate > effectiveDate...

**Luồng chính chỉ test business logic chưa được cover ở validate** (trạng thái SLA không hợp lệ, quyền, overlap với SLA khác, DB không tồn tại...).

**⚠️ Field-conditional validation KHÔNG thuộc luồng chính.** Ví dụ: "nếu approvalFlowType = X thì creditMethod bắt buộc" → đây là validate, KHÔNG phải chức năng. Chỉ flow-conditional logic (trạng thái, version, permission) mới thuộc luồng chính.

**⚠️ TUYỆT ĐỐI KHÔNG generate test cases cho LUỒNG XỬ LÝ của API khác.** Chỉ sinh test cases cho API đang thiết kế.

**⛔ PHÂN BIỆT: field VALUE ≠ processing FLOW**

| Loại | Ví dụ | Thuộc API này? |
|------|-------|---------------|
| **Field VALUE** — giá trị truyền vào field của API này | `action = "Đẩy duyệt"`, `status = "Dự thảo"` | ✅ CÓ — test giá trị field |
| **Processing FLOW** — luồng xử lý của API khác | "SLA sau khi được phê duyệt", "hiển thị trên danh sách" | ❌ KHÔNG — đây là API khác |

> **Ví dụ — khi generate API Chỉnh sửa SLA:**
> - ✅ ĐÚNG: `### Kiểm tra response khi action = Đẩy duyệt` → test giá trị field `action` của API Chỉnh sửa
> - ✅ ĐÚNG: `### Kiểm tra response chỉnh sửa SLA ở trạng thái Dự thảo` → happy path của API Chỉnh sửa
> - ❌ SAI: `### Kiểm tra SLA sau khi được phê duyệt` → đây là luồng của API Phê duyệt SLA
> - ❌ SAI: `### Kiểm tra hiển thị SLA trên danh sách sau khi chỉnh sửa` → đây là API Danh sách

> Response body cấu trúc tùy theo PTTK/RSD của từng API — KHÔNG có format cố định. Các ví dụ dùng `errorCode`, `poErrorCode`, `data` chỉ là MẪU từ project demo.

### Nội dung bắt buộc (theo thứ tự ưu tiên)

1. **Status transitions (ƯU TIÊN CAO NHẤT)** — mỗi valid status → happy path RIÊNG (KHÔNG gộp chung). Mỗi invalid status/pre-condition failure → error case riêng. Đây là NỘI DUNG CHÍNH của luồng chức năng cho API edit/approve/reject.
2. **Response fields verification** — list ALL output fields (camelCase) với sample values
3. **DB mapping verification** — SQL đầy đủ SELECT/FROM/WHERE/ORDER BY, concrete values
4. **Business logic branches** — mỗi if/else → test TRUE + FALSE, mỗi branch có Response riêng. CHỈ flow-conditional (thay đổi luồng xử lý), KHÔNG field-conditional.
5. **Mode variations** — mỗi mode (tạo/sửa/xóa) → test riêng, có Response
6. **External services** — mỗi service → test success + failure
7. **Search scenarios** — chính xác, gần đúng (LIKE), kết hợp nhiều điều kiện, không tồn tại (cho search APIs)
8. **Sort order verification** — kiểm tra ORDER BY đúng (cho list APIs)

### "Kiểm tra ngoại lệ" — STRICTLY system-level ONLY

⛔ Section "Kiểm tra ngoại lệ" chỉ chứa ĐÚNG 2 loại:
- Request timeout (504)
- Internal server error (500)

MỌI business error (not found, wrong status, duplicate, permission, version mismatch, etc.) → PHẢI nằm trong "Kiểm tra chức năng". Đặt business error vào ngoại lệ = SAI.

### SQL query rules

- Concrete values: `WHERE SRV_CODE = 'FEEACC001'` — KHÔNG dùng placeholder
- Tên bảng schema-qualified nếu biết: `FEE_ENGINE_SIT.SEGMENT_CONFIG`
- Tên cột UPPERCASE từ RSD; response fields dùng camelCase từ PTTK

### Training Examples

**Example 1 — Basic flow + DB:**
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
```

**Example 2 — Error code:**
```markdown
### Kiểm tra response khi dữ liệu không hợp lệ
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "errorCode": "1",
        "errorDesc": "Dữ liệu không hợp lệ"
      }
```

**Example 3 — Search LIKE:**
```markdown
### Kiểm tra tìm kiếm gần đúng theo srvCode
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "poErrorCode": "0",
        "total": 3,
        "data": [{"srvCode": "FEEACC001"}, ...]
      }
      SQL:
      SELECT * FROM CAT_FEESERVICE
      WHERE UPPER(TRIM(SRV_CODE)) LIKE UPPER(TRIM('%FEEACC%'))
      ORDER BY UPDATED_TIME DESC;
```

---

<!-- @section: verify -->
## Phase 5: Verify + Supplement

Sau khi generate luồng chính, re-read RSD:

1. Liệt kê TẤT CẢ nhánh logic: if/else, conditional fields, DB validations, mode variations, error codes
2. Đối chiếu với test cases đã sinh:
   - ✅ Đã có → bỏ qua
   - ❌ Thiếu → sinh bổ sung (PHẢI có Response)
   - ⚠️ Sai expected result → viết `### [SỬA] Kiểm tra ...` và replace
3. Merge: `[SỬA]` cases replace originals; new cases append

---

<!-- @section: self-check -->
## Phase 6: Self-check (BẮT BUỘC — thực hiện TRƯỚC KHI output markdown cuối cùng)

**Quy trình bắt buộc:**
1. Scan từng mục theo hướng dẫn bên dưới
2. **In kết quả checklist ra** (✅ hoặc ❌ + mô tả vi phạm) — KHÔNG được bỏ qua bước này
3. Nếu có ❌ → SỬA phần vi phạm → scan lại mục đó
4. Chỉ output markdown cuối cùng sau khi TẤT CẢ ✅

**Format output checklist (bắt buộc in ra trước markdown):**
```
=== SELF-CHECK ===
[V1] So sánh DATE trong field section: ✅ / ❌ {mô tả vi phạm nếu có}
[V2] Số case tối thiểu mỗi field: ✅ / ❌ {field nào thiếu, thiếu bao nhiêu}
[V3] Marker đúng loại: ✅ / ❌ {case nào dùng sai marker}
[V4] Status validate = 200: ✅ / ❌ {case nào dùng sai status}
[V5] Không duplicate validate → luồng chính: ✅ / ❌ {case nào bị duplicate}
[V6] Luồng con tách biệt: ✅ / ❌ {luồng nào bị trộn}
[V7] Mọi case luồng chính có response: ✅ / ❌ {case nào thiếu}
[V8] SQL giá trị cụ thể: ✅ / ❌ {query nào dùng placeholder}
[V9] Không có từ bị cấm: ✅ / ❌ {case nào, từ nào}
[V10] Format đầu ra đúng: ✅ / ❌ {vi phạm gì}
[V13] Không trùng lặp cases do BASE + BOUNDARY overlap: ✅ / ❌ {giá trị nào bị trùng, case nào thừa}
[V14] Không có cases của API khác: ✅ / ❌ {case nào thuộc API/luồng ngoài scope}
=== KẾT QUẢ: {số ✅}/12 — {PASS / CẦN SỬA} ===
```

### Hướng dẫn scan từng mục

**[V1] So sánh DATE trong field section**
→ Tìm tất cả Date field có ràng buộc so sánh (expiredDate vs effectiveDate...). Kiểm tra các case `nhỏ hơn/bằng/lớn hơn` có nằm trong `###` section của field đó không. ❌ nếu chúng nằm ngoài field section.

**[V2] Số case tối thiểu**
→ Đếm `- Kiểm tra` bullet trong mỗi `###` field section. Min: String Req ≥18 | String Opt ≥17 | Int Req ≥18 | Date ≥14 | Boolean Req ≥11 | JSONB Req ≥14 | Array ≥15 | Number Req ≥18. ❌ nếu thiếu.

**[V3] Response nhóm đúng loại**
→ Scan validate: cases Nhóm 1 (XSS, SQL injection, sai kiểu, Boolean/Mảng/Object) phải có error response. Cases Nhóm 3 (null, ký tự đặc biệt, space, dấu tiếng Việt) phải có response dựa trên `rsdConstraints` từ inventory. ❌ nếu Nhóm 1 có success response hoặc Nhóm 3 dùng error response khi inventory chỉ rõ cho phép.

**[V4] Status validate = 200**
→ Tìm `Status: 4` hoặc `Status: 5` trong section `## Kiểm tra validate`. ❌ nếu tìm thấy.

**[V5] Không duplicate**
→ Với mỗi case trong `## Kiểm tra luồng chính`, kiểm tra xem case đó đã có trong `## Kiểm tra validate` chưa (sai kiểu, bỏ trống, so sánh date...). ❌ nếu có case giống nhau.

**[V6] Luồng con tách biệt**
→ Đếm số luồng con xác định ở Bước 4.0. Nếu ≥2 → kiểm tra mỗi luồng có `####` heading riêng không. ❌ nếu test cases của các luồng khác nhau nằm lẫn nhau.

**[V7] Mọi case luồng chính có response**
→ Tìm mỗi `###` heading trong `## Kiểm tra luồng chính`, kiểm tra có `1\. Check api trả về:` ngay sau không. ❌ nếu thiếu.

**[V8] SQL giá trị cụ thể**
→ Tìm `WHERE` trong các SQL block. ❌ nếu thấy `{placeholder}`, `?`, `<value>`, hoặc tên field không có giá trị cụ thể.

**[V9] Không có từ bị cấm**
→ Tìm: "hoặc", "và/hoặc", "ví dụ:", "tương tự", "có thể", "[placeholder]", "...". ❌ nếu tìm thấy trong bất kỳ case nào.

**[V10] Format đầu ra đúng**
→ Kiểm tra: (a) dòng đầu tiên là `# {API_NAME}`, (b) không có `---` trước `#`, (c) section common dùng `- status:` không dùng `1\. Check api trả về:`.

**[V11] Heading validate mô tả điều kiện, KHÔNG chứa giá trị**
→ Scan tất cả `- Kiểm tra truyền trường` trong validate. Nếu heading chứa giá trị cụ thể (chuỗi trong ngoặc kép, số nhiều chữ số, text tiếng Việt dài) thay vì mô tả điều kiện → ❌. Ngoại lệ: `= null`, `= ""`, `= 0`, `= true/false` là hợp lệ.

**[V12] Không có ### [SỬA] heading**
→ Tìm `### [SỬA]` trong output. ❌ nếu tìm thấy — nội dung thiếu phải được insert in-place tại đúng vị trí, không append xuống cuối.

**[V13] Không trùng lặp cases do BASE + BOUNDARY overlap**
→ Sau khi MERGE (R7), kiểm tra: (a) giá trị -1 chỉ xuất hiện 1 lần, không 2 lần (base "Số âm" + boundary). (b) giá trị decimal như 1.5/1.55 chỉ xuất hiện 1 lần, không 2 lần. (c) không có 2 cases cùng giá trị, cùng response, cùng mục đích. ❌ nếu phát hiện trùng lặp.

**[V14] Không có cases thuộc LUỒNG XỬ LÝ của API khác**
→ Đọc lại từng `###` heading trong `## Kiểm tra chức năng`. Phân biệt: test field VALUE thuộc API này (action="Đẩy duyệt") = ✅ hợp lệ; test PROCESSING FLOW của API khác ("SLA sau khi được phê duyệt", "hiển thị trên danh sách") = ❌ vi phạm. Chỉ ❌ khi heading mô tả một luồng xử lý mà API KHÁC đảm nhiệm.
