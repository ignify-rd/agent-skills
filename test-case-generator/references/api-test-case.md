# API Test Case — Hướng dẫn sinh chi tiết

> **⚠️ Style/wording**: Các ví dụ trong file này là **format mặc định** (fallback). Nếu project có catalog examples → output PHẢI follow style/wording của catalog, KHÔNG copy format mẫu từ file này. File này chỉ cung cấp **rules và logic**.

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

**5 tên suite cố định dùng cho API** (KHÔNG được tạo suite mới ngoài danh sách này):

| Batch | testSuiteName |
|-------|--------------|
| BATCH 1 | `"Kiểm tra các case common"` |
| BATCH 1 | `"Kiểm tra phân quyền"` |
| BATCH 2 — wrapper | `"Kiểm tra validate"` _(không dùng trực tiếp, xem sub-suite bên dưới)_ |
| BATCH 2 — per field | `"Kiểm tra trường {fieldName}"` _(VD: "Kiểm tra trường file", "Kiểm tra trường uploadType")_ |
| BATCH 3 | `"Kiểm tra luồng chính"` |
| BATCH 3 | `"Kiểm tra timeout"` _(chỉ khi có timeout section)_ |

**Quy tắc bắt buộc:**
- **BATCH 2**: mỗi `### {fieldName}` trong mindmap → testSuiteName = `"Kiểm tra trường {fieldName}"`
  - `{fieldName}` = TÊN field (VD: `file`, `uploadType`, `domainType`) — KHÔNG phải type definition từ PTTK
  - SAI: `"file: MultipartFile (Required)"`, `"String : id"`, `"Integer : isPriority"`
  - ĐÚNG: `"Kiểm tra trường file"`, `"Kiểm tra trường id"`, `"Kiểm tra trường isPriority"`
- **KHÔNG được tạo** suite tên mới như: "Kiểm tra bảo mật", "Kiểm tra lỗi nghiệp vụ", "Kiểm tra security", v.v.
- **Kỹ thuật 4 (Error codes)**: testSuiteName = `"Kiểm tra luồng chính"` — KHÔNG tạo suite riêng
- **Security tests** (XSS, SQL injection, emoji trong validate): testSuiteName = `"Kiểm tra trường {fieldName}"` — KHÔNG tạo "Kiểm tra bảo mật"
- Nhiều APIs cùng suite name → gộp vào 1 suite, KHÔNG reset số thứ tự

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
- `"Phân quyền_Kiểm tra user không có quyền"` ← expect 403/401
- `"Phân quyền_Kiểm tra user có quyền"` ← expect 200 **(bắt buộc — PHẢI có)**
- `"regChannel_Bỏ trống field bắt buộc"`
- `"regChannel_Truyền 101 ký tự"`

Ví dụ sai:
- `"Kiểm tra validate regChannel bỏ trống"` (thiếu prefix)
- `"Kiểm tra các case common_Method_sai method"` (prefix sai)

## R3: summary

- = testCaseName, GIỐNG HỆT, không thay đổi

## R4: preConditions

**Format mặc định (fallback — dùng khi catalog KHÔNG có examples):**

> **⚠️ Nếu catalog có examples:** PHẢI follow đúng cách viết preConditions của catalog. Format dưới đây chỉ là fallback.
```
1. Send API login thành công{loginDetail}
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
- `{loginDetail}` = chi tiết login, xác định theo thứ tự ưu tiên:
  1. **Project AGENTS.md** (ưu tiên cao nhất) — nếu định nghĩa `testAccount` trong section `## Test Account`
  2. **Catalog examples** — nếu project có catalog CSV với account/login cụ thể trong preConditions, extract và dùng format đó
  3. **Default** — để trống (chỉ ghi "Send API login thành công")
- Cách diễn đạt, hành văn trong preConditions phải **tuân theo catalog** — nếu catalog dùng cách viết/format cụ thể, output phải theo đúng style đó (catalog style > format ví dụ ở trên)
- Luôn dùng endpoint user cung cấp (nếu có). KHÔNG tự đặt endpoint khác.
- Body = request hợp lệ hoàn chỉnh (baseline). Step sẽ mô tả sự thay đổi.
- Body KHÔNG được để trống nếu API có input fields.
- Header luôn có Authorization + Content-Type.
- KHÔNG thay đổi body theo từng test case trong preConditions (thay đổi thể hiện ở step).
- Account phải **nhất quán** trong toàn bộ output — KHÔNG dùng account khác nhau giữa các test cases.

## R5: step

> **⚠️ Catalog style ưu tiên:** Nếu catalog dùng cách viết steps khác ví dụ dưới đây → follow catalog.

Format: numbered steps
```
1. {Hành động 1}
2. {Hành động 2}
```

Ví dụ theo section:
- **Method**: `"1. Nhập invalid Method: GET\n2. Send API"`
- **URL**: `"1. Nhập sai endpoint: /v1/fee/invalid-path\n2. Send API"`
- **Phân quyền (no permission)**: `"1. Login với user không có quyền\n2. Send API"`
- **Phân quyền (has permission)**: `"1. Login với user có quyền\n2. Send API"` ← **bắt buộc, luôn có**
- **Validate (bỏ trống)**: `"1. Bỏ trống {field} (bắt buộc)\n2. Send API"`
- **Validate (type error)**: `"1. Truyền {field} = true (boolean)\n2. Send API"`
- **Validate (over max)**: `"1. Truyền {field} = 101 ký tự\n2. Send API"`
- **Luồng chính**: `"1. Truyền {field} hợp lệ = {concrete_value}\n2. Send API"`

## R6: expectedResult

> **⚠️ Catalog style ưu tiên:** Nếu catalog dùng cách viết expectedResult khác ví dụ dưới đây → follow catalog.

**Format mặc định (fallback):**
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

**Force-override:** `testSuiteName` = `"Kiểm tra trường {fieldName}"` — lấy tên field (KHÔNG dùng type definition từ PTTK)

**testCaseName format:** `"{fieldName}_{mô tả}"` (VD: `"id_Kiểm tra bỏ trống"`, `"file_Truyền sai định dạng"`)

**Ví dụ sub-batch cho field "id" (string):**
```json
[
  {
    "testSuiteName": "Kiểm tra trường id",
    "testCaseName": "id_Kiểm tra bỏ trống",
    ...
  },
  {
    "testSuiteName": "Kiểm tra trường id",
    "testCaseName": "id_Kiểm tra truyền null",
    ...
  },
  {
    "testSuiteName": "Kiểm tra trường id",
    "testCaseName": "id_Truyền 101 ký tự",
    ...
  }
]
```

---

## Phase 6 — BATCH 3: Luồng chính (Business Logic)

**Sections xử lý:** tất cả ## sections SAU "Kiểm tra validate"

**Force-override:** `testSuiteName` = tên section đang xử lý

**maxTokens:** 65536

---

### Kỹ thuật coverage cho luồng chính

Áp dụng đủ **6 kỹ thuật** sau đây — theo thứ tự. Mỗi kỹ thuật sinh ra một nhóm test cases riêng.

---

#### Kỹ thuật 1: Happy Path — mỗi mode/luồng thành công

Với mỗi mode/luồng được mô tả trong RSD (tạo mới, xoá, tìm kiếm, phê duyệt...), sinh **ít nhất 1 happy path** với input hợp lệ hoàn chỉnh.

**Template:**
```
step:
  1. Chuẩn bị {input hợp lệ với giá trị cụ thể}
  2. Send API

expectedResult:
  1. Check api trả về:
     1.1. Status: 200
     1.2. Response:
     {response body đúng cấu trúc với giá trị cụ thể}
     1.3. DB: SELECT ... FROM {table} WHERE {condition} → verify {field} = {expected_value}
```

**Ví dụ (Upload uploadType=1):**
```
testCaseName: "Luồng chính_Upload file thêm mới thành công (uploadType=1)"
step: "1. Chuẩn bị file .xlsx hợp lệ 5 bản ghi\n2. data: uploadType=1, domainType=\"1\", feeService=\"QLTKCN\"\n3. Send API"
expectedResult: "1. Check api trả về:\n   1.1. Status: 200\n   1.2. Response:\n   {\n     \"poErrorCode\": \"0\",\n     \"data\": 10001\n   }\n   1.3. DB: SELECT STATUS FROM PROMOTION_CUSTOMER_PENDING WHERE BATCH_ID = 10001 → STATUS = 1 (WAITING_PREVIEW)\n   1.4. S3: File được lưu tại bucket đúng path"
```

---

#### Kỹ thuật 2: Branch Coverage — mỗi nhánh if/else

Với mỗi điều kiện phân nhánh trong RSD, sinh **1 test cho nhánh TRUE + 1 test cho nhánh FALSE**.

**Cách trích xuất branches:** đọc RSD, tìm các pattern:
- "Nếu ... thì ..., ngược lại ..."
- "Trường hợp ... / Trường hợp ..."
- Bảng điều kiện (condition → action)

**Template cho mỗi branch:**
```
testCaseName: "{Context}_{Mô tả điều kiện TRUE/FALSE}"
step: "1. Tạo điều kiện: {điều kiện cụ thể}\n2. Send API"
expectedResult: "1. Check api trả về:\n   1.1. Status: 200\n   1.2. Response: {expected cho nhánh này}\n   1.3. DB: {verify side effect của nhánh này}"
```

**Ví dụ (uploadType phân nhánh):**
```
Branch TRUE  → testCaseName: "Luồng chính_uploadType=1 tạo bản ghi PENDING với action THÊM MỚI"
Branch FALSE → testCaseName: "Luồng chính_uploadType=2 tạo bản ghi PENDING với action XOÁ"
```

**Quy tắc:**
- Mỗi nhánh = 1 test case RIÊNG
- KHÔNG gộp 2 nhánh vào 1 test
- Verify **side effect khác nhau** giữa 2 nhánh (DB state, response field, status)

---

#### Kỹ thuật 3: Decision Table — tổ hợp điều kiện

Khi có **≥2 điều kiện** cùng ảnh hưởng output, tạo bảng quyết định rồi sinh test case cho mỗi dòng có **expected result khác nhau**.

**Cách tạo bảng:**
1. List tất cả điều kiện: C1, C2, C3...
2. Enumerate tổ hợp (2^n với boolean, hoặc n×m với enum)
3. Prune: loại tổ hợp impossible (không bao giờ xảy ra trong thực tế)
4. Nhóm các tổ hợp có cùng expected result → 1 test đại diện

**Ví dụ (3 điều kiện: uploadType × domainType × feeService):**

| uploadType | domainType | feeService | Expected | Test case? |
|-----------|-----------|------------|----------|-----------|
| 1 | "1" | valid | Success | ✓ happy path |
| 1 | "1" | invalid | PCER_009 | ✓ riêng |
| 1 | "2" | valid | Success | ✓ riêng (khác domain) |
| 2 | "1" | valid | Success (delete) | ✓ riêng (khác action) |
| 2 | "2" | invalid | PCER_009 | ✓ riêng |

**Quy tắc:**
- Chỉ tạo test khi **expected result khác nhau** giữa các tổ hợp
- Mỗi error code phải có **đúng 1 tổ hợp trigger** nó

---

#### Kỹ thuật 4: Error Code Coverage — mỗi mã lỗi 1 test

Với **mỗi error code** trong bảng mã lỗi của RSD, sinh 1 test case trigger đúng lỗi đó.

**Template:**
```
testCaseName: "Lỗi nghiệp vụ_{ERROR_CODE}_{mô tả ngắn}"
step: "1. Tạo điều kiện trigger {ERROR_CODE}: {mô tả cụ thể}\n2. Send API"
expectedResult: "1. Check api trả về:\n   1.1. Status: 200\n   1.2. Response:\n   {\n     \"poErrorCode\": \"{ERROR_CODE}\",\n     \"poErrorDesc\": \"{exact message từ RSD}\"\n   }"
```

**Quy tắc bắt buộc:**
- `poErrorDesc` phải **copy exact** từ RSD, không paraphrase
- Mỗi error code = 1 test case riêng
- Nếu 1 error code có thể trigger từ nhiều điều kiện → chỉ cần 1 test (điều kiện dễ nhất)
- Error code "0" (success) → đã cover ở Kỹ thuật 1, không cần lặp lại

---

#### Kỹ thuật 5: DB Verification — verify data flow

Với mỗi **write operation** (INSERT/UPDATE/DELETE) mô tả trong RSD, sinh test case verify data được lưu đúng.

**Template:**
```
testCaseName: "DB_{Tên table}_{mô tả operation}"
step: "1. Chuẩn bị {input với giá trị cụ thể X}\n2. Send API thành công"
expectedResult: "1. Check DB:\n   SELECT {fields} FROM {TABLE}\n   WHERE {condition với giá trị X}\n   → {field1} = {expected_value1}, {field2} = {expected_value2}"
```

**Các trường hợp cần cover:**
- Verify **tất cả fields được lưu đúng** (không chỉ key field)
- Verify **giá trị mặc định** (STATUS = 1, CREATED_TIME ≈ now...)
- Verify **dữ liệu input xuất hiện đúng** trong DB (file name, upload type, fee service...)
- Nếu có **nhiều table**: mỗi table = 1 test case riêng

**Ví dụ:**
```
testCaseName: "DB_PROMOTION_CUSTOMER_PENDING_Kiểm tra bản ghi được INSERT đúng"
step: "1. Upload file với uploadType=1, domainType=\"1\", feeService=\"QLTKCN\"\n2. Send API thành công, nhận batchId=10001"
expectedResult: "1. Check DB:\n   SELECT UPLOAD_TYPE, DOMAIN_TYPE, FEE_SERVICE, STATUS, FILE_NAME\n   FROM PROMOTION_CUSTOMER_PENDING\n   WHERE BATCH_ID = 10001\n   → UPLOAD_TYPE = 1\n   → DOMAIN_TYPE = '1'\n   → FEE_SERVICE = 'QLTKCN'\n   → STATUS = 1 (WAITING_PREVIEW)\n   → FILE_NAME = tên file gốc"
```

---

#### Kỹ thuật 6: External Service Failures

Với mỗi **external service** (S3, third-party API, message queue...) được gọi trong luồng xử lý, sinh test cases cho:

| Scenario | Test case |
|----------|-----------|
| Service thành công | → đã cover ở happy path |
| Service timeout | → API trả error code nào? |
| Service unavailable / lỗi kết nối | → API trả error code nào? |
| Service trả lỗi nghiệp vụ | → API handle thế nào? |

**Template:**
```
testCaseName: "{ServiceName}_{failure_type}_Kiểm tra khi {mô tả}"
step: "1. Mock/simulate {service} {failure condition}\n2. Send API với input hợp lệ"
expectedResult: "1. Check api trả về:\n   1.1. Status: 200\n   1.2. Response:\n   {\n     \"poErrorCode\": \"{error code theo RSD}\",\n     \"poErrorDesc\": \"{message}\"\n   }\n   2. Verify không có data được INSERT vào DB (rollback)"
```

**Quy tắc:**
- Nếu RSD không mô tả error code cho external failure → dùng error code generic ("2", "500", hoặc theo convention project)
- Luôn verify **rollback behavior**: khi external call fail, data không bị ghi dở vào DB

---

### Trình tự xử lý BATCH 3

Sinh test cases theo đúng thứ tự, dựa trên inventory đã extract ở Step 5c:

```
1. Happy paths (Kỹ thuật 1)       — mỗi mode/luồng trong inventory.modes[]
2. Branch coverage (Kỹ thuật 2)   — mỗi branch trong inventory.businessRules[]
3. Decision table (Kỹ thuật 3)    — mỗi combo trong inventory.decisionCombinations[]
4. Error codes (Kỹ thuật 4)       — mỗi code trong inventory.errorCodes[] section="main"
5. DB verification (Kỹ thuật 5)   — mỗi operation trong inventory.dbOperations[]
6. External failures (Kỹ thuật 6) — mỗi service trong inventory.externalServices[]
```

**KHÔNG bỏ qua kỹ thuật nào**, kể cả khi mindmap không đề cập rõ — đọc RSD để tìm.

**⚠️ CHECKLIST trước khi kết thúc BATCH 3:**
```
□ Mỗi mode trong inventory.modes[]           → có ≥1 happy path test case?
□ Mỗi branch trong inventory.businessRules[] → có test TRUE + test FALSE?
□ Mỗi error code section="main"              → có test với exact message từ RSD?
□ Mỗi dbOperation[]                          → có test SELECT verify tất cả fields?
□ Mỗi externalService[]                      → có test onFailure + onTimeout?
□ Mỗi decisionCombination[]                  → có test với exact combination đó?
Nếu bất kỳ ô nào chưa tích → tự append trước khi kết thúc batch.
```

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

---

## Standard Validate Cases cho Number/Integer Field

Mỗi Number/Integer field cần cover các cases:

| Case | step | expectedResult |
|------|------|----------------|
| Để trống (required) | Bỏ trống field | Status 200, error message |
| Không truyền (required) | Không truyền field trong body | Status 200, error message |
| Truyền null | `"field": null` | Theo RSD |
| Số âm | Truyền `-1` | Status 200, error |
| Số thập phân | Truyền `1.5` | Status 200, error |
| Leading zero | Truyền `00123` | Status 200, error |
| Số quá lớn vượt giới hạn Integer | Truyền số rất lớn | Status 200, error |
| Chuỗi ký tự | `"abc"` | Status 200, error |
| Chuỗi chữ lẫn số | `"10abc000"` | Status 200, error |
| Ký tự đặc biệt | `@#$%, *, -, +` | Status 200, error |
| All space | `"   "` | Status 200, error |
| Space đầu/cuối | `" 123 "` | Status 200, error |
| Boolean | `true` / `false` | Status 200, error |
| XSS | `<script>alert(1)</script>` | Status 200, error |
| SQL Injection | `' OR 1=1--` | Status 200, error |
| Object | `{}` | Status 200, error |
| Array | `[]` | Status 200, error |

---

## Standard Validate Cases cho Date Field

Mỗi Date field cần cover các cases (format mặc định: `dd/MM/yyyy`):

| Case | step | expectedResult |
|------|------|----------------|
| Để trống (required) | Bỏ trống field | Status 200, error message |
| Không truyền (required) | Không truyền field trong body | Status 200, error message |
| Truyền null | `"field": null` | Theo RSD |
| Đúng định dạng | Truyền `25/12/2024` | Status 200, success |
| Sai định dạng | Truyền `yyyy/dd/MM` thay vì `dd/MM/yyyy` | Status 200, error |
| Chuỗi không phải ngày | `"abc123"` | Status 200, error |
| Ngày không tồn tại | `30/02/2025`, `32/01/2025` | Status 200, error |
| Ngày quá khứ | `01/01/2020` | Theo RSD (allowed/not allowed) |
| Ngày hiện tại | Today | Theo RSD |
| Ngày tương lai | `31/12/2099` | Theo RSD (allowed/not allowed) |
| Số nguyên | `20241225` | Status 200, error |
| XSS | `<script>alert(1)</script>` | Status 200, error |
| SQL Injection | `' OR 1=1--` | Status 200, error |
| Object | `{}` | Status 200, error |
| Array | `[]` | Status 200, error |

**Lưu ý:** Nếu RSD quy định constraint ngày quá khứ/hiện tại/tương lai (VD: không được chọn ngày quá khứ), adjust expectedResult theo đúng constraint đó.

---

## Standard Validate Cases cho DateTime Field

Mỗi DateTime field cần cover các cases (format mặc định: `dd/MM/yyyy HH:mm:ss`):

| Case | step | expectedResult |
|------|------|----------------|
| Để trống (required) | Bỏ trống field | Status 200, error message |
| Không truyền (required) | Không truyền field trong body | Status 200, error message |
| Truyền null | `"field": null` | Theo RSD |
| Đúng định dạng | Truyền `25/12/2024 14:30:45` | Status 200, success |
| Sai định dạng ngày | Truyền `yyyy/dd/MM HH:mm:ss` | Status 200, error |
| Sai định dạng giờ | Truyền `25/12/2024 25:70:90` | Status 200, error |
| Chỉ có ngày không có giờ | `25/12/2024` | Status 200, error |
| Chuỗi không phải ngày giờ | `"abc123"` | Status 200, error |
| Ngày không tồn tại | `30/02/2025 14:30:45` | Status 200, error |
| Ngày giờ quá khứ | `01/01/2020 10:00:00` | Theo RSD (allowed/not allowed) |
| Ngày giờ hiện tại | Now | Theo RSD |
| Ngày giờ tương lai | `31/12/2099 23:59:59` | Theo RSD (allowed/not allowed) |
| Số nguyên | `20241225` | Status 200, error |
| XSS | `<script>alert(1)</script>` | Status 200, error |
| SQL Injection | `' OR 1=1--` | Status 200, error |
| Object | `{}` | Status 200, error |
| Array | `[]` | Status 200, error |

---

## Standard Validate Cases cho Array Field

Mỗi Array field cần cover các cases:

| Case | step | expectedResult |
|------|------|----------------|
| Không truyền (required) | Không truyền field trong body | Status 200, error message |
| Truyền null | `"field": null` | Theo RSD |
| Mảng rỗng | `[]` | Status 200, error |
| Phần tử rỗng trong mảng | `[{}]` | Status 200, error |
| String thay vì array | `"field": "abc"` | Status 200, error |
| Number thay vì array | `"field": 123` | Status 200, error |
| Object thay vì array | `"field": {}` | Status 200, error |
| Boolean thay vì array | `"field": true` | Status 200, error |
| XSS | `<script>alert(1)</script>` | Status 200, error |
| SQL Injection | `' OR 1=1--` | Status 200, error |

**Lưu ý:** Với Array field có child fields, sinh thêm validate cases cho từng child field riêng (mỗi child field = 1 sub-suite `"Kiểm tra trường {childFieldName}"`).

