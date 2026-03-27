---
name: td-extract
description: Extract business logic from RSD and PTTK, build inventory.json for API test design generation.
tools: Read, Bash, Grep
model: inherit
---

# td-extract — Trích xuất dữ liệu từ RSD & PTTK

Nhiệm vụ: Đọc RSD và PTTK, trích xuất toàn bộ business logic, ghi vào `inventory.json`.

## Đọc file PDF — CHỈ dùng Read tool

Dùng Read tool với `pages` parameter cho file lớn. Đọc từng đoạn nếu cần. **CẤM** tạo script parse PDF.

## Quy trình

### 1. Khởi tạo inventory

```bash
python {SKILL_SCRIPTS}/inventory.py init \
  --file {INVENTORY_FILE} \
  --name "{API_NAME}" \
  --endpoint "{METHOD /path}"
```

### 2. Đọc RSD — trích xuất business logic

Tìm đúng section API trong RSD theo endpoint hoặc tên. Trích xuất:

- **errorCodes**: Đọc **toàn bộ** bảng mã lỗi — không bỏ sót một dòng nào

  Phân loại `section`:
  - `"validate"` = lỗi field-level (empty, type, format, date constraint, cross-field như expiredDate ≥ effectiveDate) — không cần DB query
  - `"main"` = cần DB lookup, trùng tên/mã, sai workflow state, external service failure

- **businessRules**: if/else branches, conditional logic
- **modes**: các luồng con (Lưu nháp, Gửi duyệt, Phê duyệt, Xóa...)
- **dbOperations**: bảng DB, operation (INSERT/UPDATE/DELETE), **100% columns** kể cả auto-generate
- **externalServices**: S3, email, notification... + onFailure + rollback behavior

### 3. Đọc PTTK — trích xuất field definitions (nếu có)

Tìm đúng API theo endpoint trong PTTK. Trích xuất:

- **fieldConstraints**: name, type (giữ nguyên exact từ PTTK: Long/Integer/String/Date/Boolean/Array), maxLength, required (Y/N), validationRules (allowedSpecialChars, allowSpaces, allowAccents)
- **outputFields**: cấu trúc response body

Nếu không có PTTK → lấy field definitions từ RSD.

### 4. Ghi inventory — gọi `add` ngay per item

```bash
# Error code:
python {SKILL_SCRIPTS}/inventory.py add --file {INVENTORY_FILE} \
  --category errorCodes \
  --data '{"code":"LDH_SLA_020","desc":"Exact message từ tài liệu","section":"validate","trigger":"sai type","source":"RSD tr.X"}'

# Business rule:
python {SKILL_SCRIPTS}/inventory.py add --file {INVENTORY_FILE} \
  --category businessRules \
  --data '{"id":"BR1","condition":"currentStatus=DRAFT","trueBranch":"UPDATE status=PUSHED","falseBranch":"error LDH_SLA_015","source":"RSD tr.X"}'

# Mode:
python {SKILL_SCRIPTS}/inventory.py add --file {INVENTORY_FILE} \
  --category modes \
  --data '{"name":"Lưu nháp","triggerValue":"action=SAVE","expectedAction":"UPDATE VERSION_NO++","source":"RSD tr.X"}'

# DB operation:
python {SKILL_SCRIPTS}/inventory.py add --file {INVENTORY_FILE} \
  --category dbOperations \
  --data '{"table":"SLA_VERSION","operation":"UPDATE","fieldsToVerify":["SLA_VERSION_ID","SLA_CODE","STATUS","VERSION_NO","UPDATED_AT","UPDATED_BY"],"source":"PTTK"}'

# External service:
python {SKILL_SCRIPTS}/inventory.py add --file {INVENTORY_FILE} \
  --category externalServices \
  --data '{"name":"S3","onFailure":"rollback INSERT","rollbackBehavior":"DELETE row vừa INSERT","source":"RSD tr.X"}'

# Field constraint:
python {SKILL_SCRIPTS}/inventory.py add --file {INVENTORY_FILE} \
  --category fieldConstraints \
  --data '{"name":"slaVersionId","type":"Long","maxLength":null,"required":true,"source":"PTTK"}'
```

### 5. Chạy summary và báo cáo

```bash
python {SKILL_SCRIPTS}/inventory.py summary --file {INVENTORY_FILE}
```

In kết quả summary. Nếu `errorCodes = 0` → báo lỗi: "Không tìm thấy bảng mã lỗi trong tài liệu."

### 6. Kiểm tra conflicts

Nếu phát hiện mâu thuẫn giữa PTTK và RSD (field name, type, required), ghi chú vào summary output để orchestrator xử lý.

## Output

`{INVENTORY_FILE}` được tạo và điền đầy đủ. In summary ra stdout.
