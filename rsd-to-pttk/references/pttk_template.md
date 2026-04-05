# PTTK Template — Cấu trúc chuẩn dự án Fee Engine (PS0112025)

## Mục lục
1. [Thông tin tài liệu](#1-thong-tin)
2. [Tổng quan thiết kế](#2-tong-quan)
3. [Ma trận traceability](#3-ma-tran)
4. [Thiết kế luồng kỹ thuật](#4-luong)
5. [Đặc tả API](#5-api)
6. [Thiết kế DB](#6-db)
7. [Thiết kế xử lý nghiệp vụ](#7-xu-ly)
8. [Yêu cầu phi chức năng (NFR)](#8-nfr)
9. [Điểm cần xác nhận](#9-can-xac-nhan)
10. [Phụ lục](#10-phu-luc)

---

## 1. Thông tin tài liệu

| Mục | Nội dung |
|-----|----------|
| Mã tài liệu | PTTK-[MÃ-UC]-v[VERSION] |
| Tên tài liệu | PTTK [Tên UC/Feature] |
| Phiên bản | 1.0 |
| Ngày tạo | dd/MM/yyyy |
| Người soạn | [SA/Dev Lead] |
| Trạng thái | Bản nháp / Review / Đã phê duyệt |
| Tài liệu nguồn (RSD) | [Link Confluence RSD] |

### Lịch sử thay đổi

| Phiên bản | Ngày | Người sửa | Mô tả thay đổi |
|-----------|------|-----------|----------------|
| 1.0 | dd/MM/yyyy | - | Tạo mới |

---

## 2. Tổng quan thiết kế

### 2.1 Mục tiêu
[Mô tả ngắn gọn UC/feature này giải quyết vấn đề gì, cho ai]

### 2.2 Phạm vi
- **In scope:** [Danh sách UC/chức năng sẽ thiết kế]
- **Out of scope:** [Danh sách UC/chức năng KHÔNG thuộc phiên bản này]

### 2.3 Kiến trúc tổng thể
[Mô tả tổng quan kiến trúc: các layer, service liên quan, hệ thống tích hợp]

```
[Sơ đồ kiến trúc nếu cần — có thể dùng ASCII art hoặc Mermaid]
```

### 2.4 Tác nhân (Actor)
| Tác nhân | Mô tả | Quyền liên quan |
|----------|-------|-----------------|
| [Role 1] | - | - |

---

## 3. Ma trận Traceability

| UC ID | Tên UC | API Endpoint | Bảng DB | Job/Batch | Role/Permission |
|-------|--------|--------------|---------|-----------|-----------------|
| UC-001 | [Tên] | POST /api/v1/... | tbl_xxx | - | ROLE_X |

---

## 4. Thiết kế luồng kỹ thuật

### 4.1 Sequence Diagram — [Tên UC/Luồng chính]

```
Tiêu đề: [Tên luồng]

Actor -> FE: Thao tác [xxx]
FE -> API Gateway: POST /api/v1/[endpoint]
  Note: Header: Authorization, X-Request-Id, X-Channel-Id
API Gateway -> ServiceA: validate + xử lý
ServiceA -> DB: SELECT/INSERT/UPDATE [bảng]
DB --> ServiceA: Kết quả
ServiceA -> ExternalSystem: Gọi [hệ thống ngoài nếu có]
ExternalSystem --> ServiceA: Response
ServiceA --> API Gateway: Response
API Gateway --> FE: HTTP 200 + payload
FE --> Actor: Hiển thị kết quả
```

### 4.2 Luồng ngoại lệ (Exception flows)

| Trường hợp | Bước xảy ra | Xử lý | HTTP Status | Mã lỗi |
|------------|-------------|-------|-------------|--------|
| [Input không hợp lệ] | Bước validate | Return 400 | 400 | ERR_001 |
| [Không tìm thấy data] | Bước query DB | Return 404 | 404 | ERR_002 |
| [Lỗi hệ thống ngoài] | Bước gọi ext | Retry 3 lần, log, return 503 | 503 | ERR_003 |

### 4.3 Trạng thái dữ liệu (State Transition)
[Nếu đối tượng có nhiều trạng thái: vẽ bảng hoặc diagram]

| Trạng thái hiện tại | Sự kiện | Trạng thái tiếp theo | Điều kiện |
|---------------------|---------|----------------------|-----------|
| DRAFT | Submit | PENDING_REVIEW | User có quyền submit |
| PENDING_REVIEW | Approve | APPROVED | Role APPROVER |

---

## 5. Đặc tả API

### 5.1 [Tên API 1] — [POST/GET/PUT/DELETE] /api/v1/[path]

**Mô tả:** [Mô tả ngắn gọn API làm gì]

**Authentication:** Bearer JWT (role: [ROLE_NAME])

**Headers chuẩn:**
```
Authorization: Bearer <token>
X-Request-Id: <uuid>
X-Channel-Id: <channel-code>
Content-Type: application/json
```

**Request Body:**
```json
{
  "fieldName": "string",       // Mô tả, required, max 100 chars
  "amount": 0,                 // Số tiền VND, required, > 0
  "effectiveDate": "dd/MM/yyyy" // Ngày hiệu lực, required
}
```

| Field | Type | Required | Validation | Mô tả |
|-------|------|----------|------------|-------|
| fieldName | String | Yes | max 100, not null | [Mô tả] |
| amount | Long | Yes | > 0 | Số tiền (VND) |
| effectiveDate | String | Yes | format dd/MM/yyyy | Ngày hiệu lực |

**Response — 200 OK:**
```json
{
  "code": "SUCCESS",
  "message": "Thành công",
  "data": {
    "id": "uuid",
    "status": "CREATED"
  }
}
```

**Error Codes:**
| HTTP | Mã lỗi | Message | Nguyên nhân |
|------|--------|---------|-------------|
| 400 | ERR_INVALID_INPUT | Dữ liệu đầu vào không hợp lệ | Field thiếu hoặc sai format |
| 404 | ERR_NOT_FOUND | Không tìm thấy | ID không tồn tại |
| 409 | ERR_DUPLICATE | Dữ liệu đã tồn tại | Trùng key nghiệp vụ |
| 500 | ERR_INTERNAL | Lỗi hệ thống | Xử lý ngoại lệ không dự kiến |

**Logging:**
- Log INFO: request (mask sensitive fields), response code, duration
- Log ERROR: exception, request body (mask password/card number)
- Mask fields: `password`, `cardNumber`, `cvv`, `pin`

---

## 6. Thiết kế DB

### 6.1 ERD (Sơ đồ thực thể)

```
[Entity A] 1---* [Entity B]
           |
           *---1 [Entity C]
```

### 6.2 Thiết kế bảng

#### Bảng: `tbl_[tên_bảng]`

**Mô tả:** [Mô tả bảng lưu gì]

| Cột | Kiểu dữ liệu | Nullable | Default | Mô tả |
|-----|-------------|----------|---------|-------|
| ID | NUMBER(18) | NO | SEQ_xxx.NEXTVAL | Khóa chính |
| CODE | VARCHAR2(50) | NO | - | Mã duy nhất |
| NAME | VARCHAR2(200) | NO | - | Tên |
| STATUS | VARCHAR2(20) | NO | 'ACTIVE' | Trạng thái: ACTIVE/INACTIVE |
| CREATED_BY | VARCHAR2(100) | NO | - | Người tạo |
| CREATED_DATE | DATE | NO | SYSDATE | Ngày tạo |
| UPDATED_BY | VARCHAR2(100) | YES | - | Người cập nhật |
| UPDATED_DATE | DATE | YES | - | Ngày cập nhật |

**Constraints:**
```sql
PRIMARY KEY (ID)
UNIQUE (CODE)
FOREIGN KEY (PARENT_ID) REFERENCES tbl_parent(ID)
CHECK (STATUS IN ('ACTIVE', 'INACTIVE'))
```

**Indexes:**
```sql
CREATE INDEX IDX_tbl_xxx_CODE ON tbl_xxx(CODE);
CREATE INDEX IDX_tbl_xxx_STATUS ON tbl_xxx(STATUS, CREATED_DATE);
```

**HIS Table (nếu cần lịch sử):** `tbl_[tên]_his` — cấu trúc giống bảng chính + thêm cột `CHANGE_TYPE` (INSERT/UPDATE/DELETE), `CHANGE_DATE`

### 6.3 Data Migration / Seed Data
[Nếu có data cần migrate hoặc seed khi deploy]

---

## 7. Thiết kế xử lý nghiệp vụ

### 7.1 Validation Rules

| Rule ID | Field/Đối tượng | Điều kiện | Thông báo lỗi | Mã lỗi |
|---------|----------------|-----------|---------------|--------|
| VAL-001 | amount | > 0 | Số tiền phải lớn hơn 0 | ERR_INVALID_INPUT |
| VAL-002 | effectiveDate | Không được là ngày quá khứ | Ngày hiệu lực phải từ hôm nay | ERR_INVALID_DATE |

### 7.2 Business Rules

| Rule ID | Mô tả | Công thức / Logic | Tham chiếu RSD |
|---------|-------|-------------------|----------------|
| BIZ-001 | Tính phí | fee = amount * rate / 100 | RSD Mục 4.2 |
| BIZ-002 | Giới hạn giao dịch | Không quá [X] giao dịch/ngày/tài khoản | RSD Mục 4.3 |

### 7.3 Transaction Boundary

```
BEGIN TRANSACTION
  1. Validate input
  2. Lock record (SELECT ... FOR UPDATE NOWAIT)
  3. Insert/Update main table
  4. Insert HIS record
  5. Call external service (nếu có)
  6. If all success → COMMIT
  7. If any fail → ROLLBACK + log error
END TRANSACTION
```

### 7.4 Xử lý Concurrency

[Mô tả cơ chế xử lý đồng thời nếu có — optimistic locking, pessimistic locking, queue]

### 7.5 Pseudocode các logic phức tạp

```
function processXxx(input):
  // Step 1: validate
  if input.amount <= 0: throw ERR_INVALID_INPUT
  
  // Step 2: get current record
  record = db.findById(input.id)
  if not record: throw ERR_NOT_FOUND
  
  // Step 3: calculate
  fee = calculateFee(record, input)
  
  // Step 4: save
  db.update(record.id, {fee: fee, status: 'PROCESSED'})
  db.insertHis(record, 'UPDATE')
  
  return {success: true, fee: fee}
```

---

## 8. Yêu cầu phi chức năng (NFR)

### 8.1 Performance
| Metric | Yêu cầu | Ghi chú |
|--------|---------|---------|
| Response time (normal load) | < 2s (95th percentile) | Theo trang hiệu năng dự án |
| Throughput | > 50 TPS | - |
| Batch window | Hoàn thành trong 2h (00:00 - 02:00) | Nếu có job |

### 8.2 Security & Phân quyền
| Role | Quyền | Mô tả |
|------|-------|-------|
| ROLE_MAKER | CREATE, READ | Tạo và xem |
| ROLE_CHECKER | READ, APPROVE | Xem và phê duyệt |
| ROLE_ADMIN | ALL | Toàn quyền |

**Audit Trail:** Mọi thay đổi dữ liệu phải log: user, thời gian, action, giá trị trước/sau.

### 8.3 Logging
- Level INFO: request/response tóm tắt (không log nhạy cảm)
- Level ERROR: toàn bộ exception stack + request context
- Retention: 90 ngày (log thường), 1 năm (audit log)

### 8.4 Data Retention
- Dữ liệu nóng (online): 2 năm
- Dữ liệu ấm (archive): 5 năm
- Xóa vật lý: sau 7 năm theo quy định NHNN

---

## 9. Điểm cần xác nhận

> Đây là danh sách các câu hỏi còn mở từ RSD — SA/Dev cần confirm với BA trước khi code.

| STT | Vấn đề | Nội dung câu hỏi | Người cần confirm | Deadline |
|-----|--------|-----------------|-------------------|---------|
| 1 | [Tên vấn đề] | [Câu hỏi cụ thể] | BA [Tên] | dd/MM/yyyy |

---

## 10. Phụ lục

### 10.1 Danh sách viết tắt
| Viết tắt | Nghĩa đầy đủ |
|----------|-------------|
| PTTK | Phân tích thiết kế kỹ thuật |
| RSD | Requirement Specification Document |
| UC | Use Case |
| BA | Business Analyst |
| SA | Solution Architect |

### 10.2 Tài liệu tham chiếu
- RSD nguồn: [Link Confluence]
- Template PTTK chuẩn: [Link Confluence]
- Yêu cầu hiệu năng: https://bidv-vn.atlassian.net/wiki/spaces/PS0112025/pages/1680048949/
- Hướng dẫn phê duyệt: https://bidv-vn.atlassian.net/wiki/spaces/PS0112025/pages/1281425409/
