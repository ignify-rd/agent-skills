# API Test Design — Hướng dẫn sinh chi tiết

## Tổng quan

API test design sinh ra markdown mindmap gồm 3 section chính:
1. **Các case common** (method, URL, phân quyền) — hardcoded template
2. **Validate** (kiểm tra validate từng field đầu vào) — per-field templates
3. **Luồng chính** (business logic, DB operations, error scenarios) — LLM-generated

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

**⚠️ CRITICAL — Format Rules:**
1. **KHÔNG** thêm blockquote/mô tả endpoint — output bắt đầu NGAY từ `# {API_NAME}`
2. **KHÔNG** dùng `---` (horizontal rule) bất kỳ đâu
3. **Section common** dùng format ĐƠN GIẢN: `- status: 107` — **TUYỆT ĐỐI KHÔNG** dùng `1\. Check api trả về:` trong common
4. Format `1\. Check api trả về:` **CHỈ** dùng trong **validate** và **luồng chính**
5. `{WRONG_METHODS}`: nếu method=POST → "GET/PUT/DELETE"

---

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

## Phase 3: Kiểm tra validate

### Response Legend (áp dụng cho MỌI validate case)

| Marker | Ý nghĩa | Output thực tế trong file .md |
|--------|---------|-------------------------------|
| `→ error` | Luôn luôn lỗi, bất kể spec (sai kiểu dữ liệu, XSS, SQL injection...) | Status 200 + `{"message": "Dữ liệu không hợp lệ"}` |
| `→ success` | Luôn luôn thành công khi đúng kiểu/format | Status 200 + `Trả về response body đúng cấu trúc` |
| `→ Theo RSD` | Kết quả phụ thuộc vào spec — **bắt buộc đọc tài liệu** để xác định trước khi điền response | Điền response đúng theo PTTK/RSD |

**CRITICAL:** ALL validate responses dùng Status: 200 — KHÔNG dùng 400/422/500 cho validate.

### Quy tắc ký tự đặc biệt cho String

| Tài liệu có `allowedSpecialChars`? | Sinh cases |
|------------------------------------|-----------|
| Có (VD: `["_", "-"]`) | Tách 2 case: "cho phép (_, -)" `→ success` + "không cho phép (!@#$%^&*)" `→ error` |

**CRITICAL:** Case "không cho phép" LUÔN LUÔN `→ error` — KHÔNG được fill `"code": "00"` hay response thành công vào case này.
| Không có / không rõ | 1 case chung "ký tự đặc biệt" `→ Theo RSD` |

### Per-field output format

Heading field: `### {fieldName}: {type} ({Required/Optional})`
Mỗi case = 1 `####` heading + response theo legend trên.

---

### STRING Required — 19+ cases

| Case | Marker |
|------|--------|
| Để trống | `→ error` |
| Không truyền | `→ error` |
| Truyền null | `→ Theo RSD` |
| {maxLen-1} ký tự | `→ success` |
| {maxLen} ký tự | `→ success` |
| {maxLen+1} ký tự | `→ error` |
| Ký tự số | `→ Theo RSD` |
| Chữ thường/hoa không dấu | `→ success` |
| Chữ có dấu tiếng Việt | `→ Theo RSD` |
| Ký tự đặc biệt (xem quy tắc trên) | `→ Theo RSD` |
| All space | `→ Theo RSD` |
| Space đầu / cuối | `→ Theo RSD` |
| Space ở giữa | `→ Theo RSD` |
| Emoji/icons (😀🏠⚡) | `→ Theo RSD` |
| Unicode đặc biệt (tiếng Trung, Nhật...) | `→ Theo RSD` |
| Boolean | `→ error` |
| Mảng | `→ error` |
| Object | `→ error` |
| XSS | `→ error` |
| SQL INJECTION | `→ error` |

---

### INTEGER Required (no default) — 19 cases

| Case | Marker |
|------|--------|
| Để trống | `→ error` |
| Không truyền | `→ error` |
| Truyền null | `→ Theo RSD` |
| Số nguyên hợp lệ | `→ success` |
| Số âm | `→ Theo RSD` |
| Số thập phân | `→ Theo RSD` |
| Số leading zero (00123) | `→ Theo RSD` |
| Số rất lớn vượt giới hạn Integer | `→ Theo RSD` |
| Chuỗi ký tự (abc) | `→ error` |
| Chuỗi chữ lẫn số (10abc) | `→ error` |
| Ký tự đặc biệt (@#$) | `→ error` |
| All space | `→ error` |
| Space đầu / cuối | `→ error` |
| Boolean | `→ error` |
| Mảng | `→ error` |
| Object | `→ error` |
| XSS | `→ error` |
| SQL INJECTION | `→ error` |

---

### INTEGER with Default Value — 19 cases

Heading: `### {fieldName}: Integer (Required, default = {defaultValue})`

| Case | Marker |
|------|--------|
| Để trống | `→ success` + ghi chú: "Hệ thống sử dụng default {fieldName} = {defaultValue}" |
| Không truyền | `→ success` + ghi chú default |
| Truyền null | `→ success` + ghi chú default |
| Số nguyên hợp lệ | `→ success` |
| Số âm | `→ Theo RSD` |
| Số thập phân | `→ Theo RSD` |
| Số leading zero (00123) | `→ Theo RSD` |
| Số rất lớn vượt giới hạn Integer | `→ Theo RSD` |
| Chuỗi ký tự (abc) | `→ error` |
| Chuỗi chữ lẫn số (10abc) | `→ error` |
| Ký tự đặc biệt (@#$) | `→ error` |
| All space | `→ error` |
| Space đầu / cuối | `→ error` |
| Boolean | `→ error` |
| Mảng | `→ error` |
| Object | `→ error` |
| XSS | `→ error` |
| SQL INJECTION | `→ error` |

---

### INTEGER Optional (null = tìm tất cả)

Heading: `### {fieldName}: Integer (Optional, null = tìm tất cả)`

| Case | Marker |
|------|--------|
| Để trống | `→ success` + "Trả về TẤT CẢ bản ghi" |
| Không truyền | `→ success` + "Trả về TẤT CẢ bản ghi" |
| Truyền null | `→ success` + "Trả về TẤT CẢ bản ghi" |
| Giá trị hợp lệ | `→ success` + "CHỈ trả về bản ghi khớp" |
| Giá trị không hợp lệ | `→ Theo RSD` |
| Số âm | `→ Theo RSD` |
| Số thập phân | `→ Theo RSD` |
| Chuỗi | `→ error` |
| Boolean | `→ error` |
| Mảng | `→ error` |
| Object | `→ error` |
| XSS | `→ error` |
| SQL INJECTION | `→ error` |

---

### JSONB Required — 14 cases

| Case | Marker |
|------|--------|
| Để trống | `→ error` |
| Không truyền | `→ error` |
| Truyền null | `→ Theo RSD` |
| JSON hợp lệ | `→ success` |
| JSON sai syntax (không parse được) | `→ error` |
| JSON sai format nghiệp vụ (thiếu trường bắt buộc trong JSON) | `→ Theo RSD` |
| Object rỗng `{}` | `→ Theo RSD` |
| Mảng `[]` thay vì object | `→ error` |
| Chuỗi rỗng | `→ error` |
| String thuần (không phải JSON) | `→ error` |
| Number | `→ error` |
| Boolean | `→ error` |
| XSS trong JSON value | `→ error` |
| SQL injection trong JSON value | `→ error` |

---

### JSONB Optional — 12 cases

| Case | Marker |
|------|--------|
| Không truyền | `→ success` |
| Truyền null | `→ success` |
| JSON hợp lệ | `→ success` |
| JSON sai syntax (không parse được) | `→ error` |
| JSON sai format nghiệp vụ | `→ Theo RSD` |
| Object rỗng `{}` | `→ Theo RSD` |
| Mảng `[]` thay vì object | `→ error` |
| Chuỗi rỗng | `→ error` |
| String thuần (không phải JSON) | `→ error` |
| Number | `→ error` |
| Boolean | `→ error` |
| XSS trong JSON value | `→ error` |
| SQL injection trong JSON value | `→ error` |

---

### DATE Required — format theo PTTK/RSD

| Case | Marker |
|------|--------|
| Để trống | `→ error` |
| Không truyền | `→ error` |
| Truyền null | `→ Theo RSD` |
| Đúng định dạng | `→ success` |
| Sai định dạng | `→ error` |
| Ngày không tồn tại (2025-00-00, 2025-02-30) | `→ error` |
| Ngày quá khứ | `→ Theo RSD` |
| Ngày hiện tại | `→ Theo RSD` |
| Ngày tương lai | `→ Theo RSD` |
| Số nguyên | `→ error` |
| Boolean | `→ error` |
| Mảng | `→ error` |
| Object | `→ error` |
| XSS | `→ error` |
| SQL INJECTION | `→ error` |

**So sánh với Date field khác (khi có ràng buộc):**

Khi một Date field có ràng buộc so sánh với Date field khác (VD: `expiredDate` phải >= `effectiveDate`), thêm các case sau NGAY TRONG section `###` của field đó:

| Case | Marker |
|------|--------|
| {fieldName} nhỏ hơn {relatedField} | `→ error` |
| {fieldName} bằng {relatedField} | `→ Theo RSD` |
| {fieldName} lớn hơn {relatedField} | `→ success` |

---

### ARRAY Required — cases

| Case | Marker |
|------|--------|
| Không truyền | `→ error` |
| Truyền null | `→ Theo RSD` |
| Mảng rỗng `[]` | `→ error` |
| Mảng chứa phần tử rỗng `[{}]` | `→ error` |
| String thay vì array | `→ error` |
| Number thay vì array | `→ error` |
| Object thay vì array | `→ error` |
| Boolean thay vì array | `→ error` |
| XSS trong phần tử | `→ error` |
| SQL injection trong phần tử | `→ error` |

> Với Array có child fields: sinh thêm validate cases cho từng child field riêng (`### {childFieldName}`).

---

### INTEGER / LONG — cùng template, khác heading

Cả `int`/`Integer`/`integer` và `long`/`Long` đều dùng **INTEGER Required (no default)** template (≥ 19 cases).

- Type trong PTTK/RSD là `int` / `Integer` / `integer` → Heading: `### {fieldName}: Integer (Required)`
- Type trong PTTK/RSD là `long` / `Long` → Heading: `### {fieldName}: Long (Required)`

**CRITICAL:** KHÔNG dùng "Long" heading cho field có type `int`/`Integer`.

---

### BOOLEAN Required — 11 cases

| Case | Marker |
|------|--------|
| Để trống | `→ error` |
| Không truyền | `→ error` |
| Truyền null | `→ Theo RSD` |
| true | `→ success` |
| false | `→ success` |
| Chuỗi "true" / "false" | `→ Theo RSD` |
| Số nguyên (0/1) | `→ Theo RSD` |
| Số khác 0 và 1 | `→ error` |
| Chuỗi bất kỳ (abc) | `→ error` |
| Mảng | `→ error` |
| Object | `→ error` |

---

### BOOLEAN Optional — 9 cases

| Case | Marker |
|------|--------|
| Không truyền | `→ success` |
| Truyền null | `→ success` |
| true | `→ success` |
| false | `→ success` |
| Chuỗi "true" / "false" | `→ Theo RSD` |
| Số nguyên (0/1) | `→ Theo RSD` |
| Chuỗi bất kỳ (abc) | `→ error` |
| Mảng | `→ error` |
| Object | `→ error` |

---

### NUMBER Required (decimal/float, có thể có range) — ≥ 18 cases

| Case | Marker |
|------|--------|
| Để trống | `→ error` |
| Không truyền | `→ error` |
| Truyền null | `→ Theo RSD` |
| Số nguyên hợp lệ | `→ success` |
| Số thập phân hợp lệ | `→ success` |
| Số âm | `→ Theo RSD` |
| Quá nhiều chữ số thập phân (vượt precision) | `→ Theo RSD` |
| Số rất lớn | `→ Theo RSD` |
| Chuỗi ký tự (abc) | `→ error` |
| Chuỗi chữ lẫn số (10abc) | `→ error` |
| Ký tự đặc biệt (@#$) | `→ error` |
| All space | `→ error` |
| Space đầu / cuối | `→ error` |
| Boolean | `→ error` |
| Mảng | `→ error` |
| Object | `→ error` |
| XSS | `→ error` |
| SQL INJECTION | `→ error` |

> Nếu spec có range [min, max]: thêm "Giá trị < min" `→ Theo RSD` và "Giá trị > max" `→ Theo RSD`

---

### NUMBER Optional — ≥ 13 cases

| Case | Marker |
|------|--------|
| Không truyền | `→ success` |
| Truyền null | `→ success` |
| Số nguyên hợp lệ | `→ success` |
| Số thập phân hợp lệ | `→ success` |
| Số âm | `→ Theo RSD` |
| Quá nhiều chữ số thập phân | `→ Theo RSD` |
| Số rất lớn | `→ Theo RSD` |
| Chuỗi | `→ error` |
| Boolean | `→ error` |
| Mảng | `→ error` |
| Object | `→ error` |
| XSS | `→ error` |
| SQL INJECTION | `→ error` |

> Nếu spec có range [min, max]: thêm "Giá trị < min" `→ Theo RSD` và "Giá trị > max" `→ Theo RSD`

---

### STRING Optional — ≥ 17 cases

| Case | Marker |
|------|--------|
| Không truyền | `→ success` |
| Truyền null | `→ success` |
| Để trống ("") | `→ Theo RSD` |
| {maxLen-1} ký tự | `→ success` |
| {maxLen} ký tự | `→ success` |
| {maxLen+1} ký tự | `→ error` |
| Ký tự số | `→ Theo RSD` |
| Chữ thường/hoa không dấu | `→ success` |
| Chữ có dấu tiếng Việt | `→ Theo RSD` |
| Ký tự đặc biệt (xem quy tắc) | `→ Theo RSD` |
| All space | `→ Theo RSD` |
| Space đầu / cuối | `→ Theo RSD` |
| Space ở giữa | `→ Theo RSD` |
| Emoji/icons | `→ Theo RSD` |
| Unicode đặc biệt | `→ Theo RSD` |
| Boolean | `→ error` |
| Mảng | `→ error` |
| Object | `→ error` |
| XSS | `→ error` |
| SQL INJECTION | `→ error` |

> Nếu không có maxLength: bỏ qua 3 cases maxLen → min ≥ 17 → ≥ 14 cases.

---

### Per-field checkpoint (bắt buộc sau MỖI field)

```
Field {fieldName} ({type}): {generated}/{min} cases. Missing: [list] → THÊM ngay.
```

Min counts: String Required ≥ 19 | String Optional ≥ 17 | Integer Required ≥ 19 | Integer with Default ≥ 19 | Long ≥ 19 | JSONB Required ≥ 14 | JSONB Optional ≥ 12 | Date ≥ 15 | Array ≥ 8 | Boolean Required ≥ 11 | Boolean Optional ≥ 9 | Number Required ≥ 18 | Number Optional ≥ 13

---

## Phase 4: Kiểm tra luồng chính

### Bước 4.0: Xác định luồng con (BẮT BUỘC trước khi viết bất kỳ test case nào)

Đọc RSD và liệt kê TẤT CẢ các sub-flow (luồng con) của API này. Ví dụ:

| API loại | Các luồng con thường gặp |
|----------|--------------------------|
| Tạo mới | Lưu nháp, Gửi duyệt |
| Chỉnh sửa | Chỉnh sửa + Lưu, Chỉnh sửa + Gửi duyệt |
| Phê duyệt | Duyệt, Từ chối, Yêu cầu bổ sung |
| Xóa | Xóa 1 bản ghi, Xóa nhiều bản ghi |

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

> Response body cấu trúc tùy theo PTTK/RSD của từng API — KHÔNG có format cố định. Các ví dụ dùng `errorCode`, `poErrorCode`, `data` chỉ là MẪU từ project demo.

### Nội dung bắt buộc

1. **Response fields verification** — list ALL output fields (camelCase) với sample values
2. **DB mapping verification** — SQL đầy đủ SELECT/FROM/WHERE/ORDER BY, concrete values
3. **Search scenarios** — chính xác, gần đúng (LIKE), kết hợp nhiều điều kiện, không tồn tại
4. **Sort order verification** — kiểm tra ORDER BY đúng
5. **Business logic branches** — mỗi if/else → test TRUE + FALSE, mỗi branch có Response riêng
6. **DB validations** — tồn tại/không tồn tại → test cả 2, mỗi cái có Response
7. **Mode variations** — mỗi mode (tạo/sửa/xóa) → test riêng, có Response
8. **Status transitions** — valid/invalid transitions, mỗi cái có Response

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

## Phase 5: Verify + Supplement

Sau khi generate luồng chính, re-read RSD:

1. Liệt kê TẤT CẢ nhánh logic: if/else, conditional fields, DB validations, mode variations, error codes
2. Đối chiếu với test cases đã sinh:
   - ✅ Đã có → bỏ qua
   - ❌ Thiếu → sinh bổ sung (PHẢI có Response)
   - ⚠️ Sai expected result → viết `### [SỬA] Kiểm tra ...` và replace
3. Merge: `[SỬA]` cases replace originals; new cases append

---

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
=== KẾT QUẢ: {số ✅}/10 — {PASS / CẦN SỬA} ===
```

### Hướng dẫn scan từng mục

**[V1] So sánh DATE trong field section**
→ Tìm tất cả Date field có ràng buộc so sánh (expiredDate vs effectiveDate...). Kiểm tra các case `nhỏ hơn/bằng/lớn hơn` có nằm trong `###` section của field đó không. ❌ nếu chúng nằm ngoài field section.

**[V2] Số case tối thiểu**
→ Đếm `####` heading trong mỗi `###` field section. Min: String Req ≥19 | String Opt ≥17 | Int Req ≥19 | Date ≥15 | Boolean Req ≥11 | JSONB Req ≥14 | Array ≥8. ❌ nếu thiếu.

**[V3] Marker đúng loại**
→ Scan tất cả `→ error` trong validate: chỉ hợp lệ cho sai kiểu dữ liệu (boolean/array/object vào string field) và XSS/SQL injection. Kết quả phụ thuộc spec (ngày quá khứ, ký tự đặc biệt, null...) phải là `→ Theo RSD`. ❌ nếu dùng `→ error` cho case business rule.

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
