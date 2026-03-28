---
name: td-extract
description: Extract business logic from RSD and PTTK, build inventory.json for API test design generation.
tools: Read, Bash, Grep
model: inherit
---

# td-extract — Trích xuất dữ liệu từ RSD & PTTK

Nhiệm vụ: Đọc RSD và PTTK, trích xuất toàn bộ business logic + request/response schema, ghi vào `inventory.json`.

## Đọc file PDF — CHỈ dùng Read tool

Dùng Read tool với `pages` parameter cho file lớn. Đọc từng đoạn nếu cần. **CẤM** tạo script parse PDF.

## Quy trình

### 1. Khởi tạo inventory

```bash
python {SKILL_SCRIPTS}/inventory.py init \
  --file {INVENTORY_FILE} \
  --name "{API_NAME}" \
  --endpoint "{/path}" \
  --method "{GET|POST|PUT|DELETE|PATCH}"
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

### 3. Đọc PTTK — trích xuất field definitions + schema

Tìm đúng API theo endpoint trong PTTK. Trích xuất:

- **fieldConstraints**: name, type (giữ nguyên exact từ PTTK: Long/Integer/String/Date/Boolean/Array), maxLength, required (Y/N), validationRules
- **requestSchema**: pathParams, queryParams, bodyParams với đầy đủ type/required/constraints
- **responseSchema**: cấu trúc response success + error từ PTTK, kèm sample values
- **testData**: 1 valid sample value cho mỗi field (dùng để gen test cases sau)

Nếu không có PTTK → lấy từ RSD.

### 4. Ghi inventory — dùng `patch` command (tránh Windows encoding issue)

**KHÔNG dùng `--data` trực tiếp với tiếng Việt trên Windows.** Thay vào đó:

**Bước 4a** — Tạo file `{OUTPUT_DIR}/patch.json` bằng Python:

```python
import json

patch = {
  # ── Business logic ──
  "errorCodes": [
    {"code": "LDH_SLA_020", "desc": "Dữ liệu đầu vào không hợp lệ", "section": "validate", "trigger": "sai type/format", "source": "Mã lỗi tr.X"},
    {"code": "LDH_SLA_002", "desc": "Không tìm thấy thông tin SLA", "section": "main", "trigger": "slaVersionId không tồn tại", "source": "Mã lỗi tr.X"},
    # ... tất cả error codes
  ],
  "businessRules": [
    {"id": "BR1", "condition": "currentStatus=DRAFT", "trueBranch": "UPDATE status=PUSHED", "falseBranch": "error LDH_SLA_015", "source": "RSD tr.X"},
  ],
  "modes": [
    {"name": "Lưu nháp", "triggerValue": "action=SAVE", "expectedAction": "UPDATE VERSION_NO++", "source": "RSD tr.X"},
    {"name": "Gửi duyệt", "triggerValue": "action=PUSH", "expectedAction": "UPDATE status=PUSHED", "source": "RSD tr.X"},
  ],
  "dbOperations": [
    {"table": "SLA_VERSION", "operation": "UPDATE", "fieldsToVerify": ["SLA_VERSION_ID","SLA_CODE","STATUS","VERSION_NO","UPDATED_AT","UPDATED_BY"], "source": "PTTK"},
  ],
  "externalServices": [],
  "fieldConstraints": [
    {"name": "slaVersionId", "type": "Long", "maxLength": None, "required": True, "source": "PTTK"},
    {"name": "effectiveDate", "type": "Date", "maxLength": None, "required": True, "source": "PTTK"},
    # ... tất cả fields
  ],

  # ── Request schema (pathParams / queryParams / bodyParams) ──
  "requestSchema": {
    "pathParams": [
      # {"name": "slaVersionId", "type": "Long", "required": True, "desc": "ID phiên bản SLA"}
    ],
    "queryParams": [
      # {"name": "action", "type": "String", "required": True, "values": ["SAVE", "PUSH"], "desc": "Loại hành động"}
    ],
    "bodyParams": [
      # Liệt kê toàn bộ fields từ fieldConstraints kèm constraint đầy đủ
      # {"name": "slaName", "type": "String", "required": True, "maxLength": 100},
      # {"name": "steps", "type": "Array<Step>", "required": True, "items": {
      #   "processStepCode": {"type": "String", "required": True, "maxLength": 50},
      #   "processStepName": {"type": "String", "required": True, "maxLength": 200},
      #   "slaHours": {"type": "Integer", "required": True, "min": 1, "max": 99}
      # }}
    ]
  },

  # ── Response schema ──
  "responseSchema": {
    "success": {
      "status": 200,
      "body": {
        # Tên field: type — từ PTTK response definition
        # "slaVersionId": "Long",
        # "slaName": "String",
        # "status": "String (DRAFT|PUSHED|APPROVED)"
      },
      "sample": {
        # Giá trị mẫu thực tế — KHÔNG dùng placeholder
        # "slaVersionId": 10001,
        # "slaName": "SLA Chỉnh sửa Test",
        # "status": "DRAFT"
      }
    },
    "error": {
      "status": 200,
      "body": {"code": "String", "message": "String"}
    }
  },

  # ── Sample valid data cho test case generation ──
  "testData": [
    # 1 valid value cho mỗi field — dùng làm base request trong test cases
    # {"field": "slaName", "type": "String", "validValue": "SLA Test 001", "note": "tên SLA đúng định dạng"},
    # {"field": "effectiveDate", "type": "Date", "validValue": "2025-01-01", "note": "ngày hiệu lực hợp lệ"},
    # {"field": "action", "type": "String", "validValue": "SAVE", "note": "lưu nháp"},
  ]
}

with open(r"{OUTPUT_DIR}/patch.json", "w", encoding="utf-8") as f:
    json.dump(patch, f, ensure_ascii=False, indent=2)
```

**Bước 4b** — Apply patch:

```bash
python {SKILL_SCRIPTS}/inventory.py patch \
  --file {INVENTORY_FILE} \
  --patch-file {OUTPUT_DIR}/patch.json
```

### 5. Chạy summary và báo cáo

```bash
python {SKILL_SCRIPTS}/inventory.py summary --file {INVENTORY_FILE}
```

In kết quả summary. Kiểm tra:
- `errorCodes = 0` → báo lỗi: "Không tìm thấy bảng mã lỗi trong tài liệu."
- `requestSchema.bodyParams = 0` → báo lỗi: "Không tìm thấy request body params trong PTTK."
- `responseSchema.success = {}` → cảnh báo: "Không tìm thấy response schema — test cases có thể thiếu response body."

### 6. Kiểm tra conflicts

Nếu phát hiện mâu thuẫn giữa PTTK và RSD (field name, type, required), ghi chú vào summary output để orchestrator xử lý.

## Output

`{INVENTORY_FILE}` được tạo và điền đầy đủ bao gồm:
- Business logic (errorCodes, businessRules, modes, dbOperations, externalServices)
- fieldConstraints (cho td-validate)
- requestSchema + responseSchema + testData (cho generate-test-case-api)

In summary ra stdout.
