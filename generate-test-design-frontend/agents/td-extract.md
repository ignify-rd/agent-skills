---
name: td-extract-frontend
description: Extract business logic from RSD, PTTK, and images for frontend test design. Build inventory.json.
tools: Read, Bash, Grep
model: inherit
---

# td-extract-frontend — Trích xuất dữ liệu từ RSD, PTTK & Images

Nhiệm vụ: Đọc RSD và PTTK (và images nếu có), trích xuất toàn bộ business logic và field definitions, ghi vào `inventory.json`.

## Đọc file PDF — CHỈ dùng Read tool

Dùng Read tool với `pages` parameter cho file lớn. Đọc từng đoạn nếu cần. **CẤM** tạo script parse PDF.

## Quy trình

### 1. Khởi tạo inventory

```bash
python3 {SKILL_SCRIPTS}/inventory.py init \
  --file {INVENTORY_FILE} \
  --name "{SCREEN_NAME}" \
  --screen-type "{SCREEN_TYPE}"
```

`SCREEN_TYPE` = `LIST | FORM | POPUP | DETAIL` (xác định từ RSD).

### 2. Đọc RSD — trích xuất business logic & structure

Tìm đúng section màn hình trong RSD. Trích xuất:

- **screenType**: LIST / FORM / POPUP / DETAIL
- **businessRules**: if/else branches, hiển thị có điều kiện, luồng xử lý
- **errorMessages**: tất cả thông báo lỗi, validation messages
- **enableDisableRules**: quy tắc enable/disable cho fields và buttons
- **autoFillRules**: auto-fill từ field này sang field khác
- **statusTransitions**: trạng thái hợp lệ / không hợp lệ
- **permissions**: phân quyền theo role

### 3. Đọc PTTK — trích xuất field definitions (nếu có)

PTTK THAY THẾ HOÀN TOÀN field definitions từ RSD. Trích xuất:

- **fieldConstraints**: name (giữ nguyên từ PTTK), type, required (Y/N), maxLength, displayBehavior (always/conditional), condition, placeholder, validationRules (allowSpecialChars, allowSpaces, allowAccents)

Nếu không có PTTK → lấy field definitions từ RSD.

### 4. Phân tích images (nếu có)

**CHỈ bổ sung** sau khi đã extract từ RSD/PTTK. Images không được override RSD/PTTK.
Extract từ images: placeholder text, icon X, button labels, gridColumns.

### 5. Ghi inventory — dùng `patch` command (tránh Windows encoding issue)

**Bước 5a** — Tạo file `{OUTPUT_DIR}/patch.json` bằng Python:

```python
import json

patch = {
  "fieldConstraints": [
    {
      "name": "tenField",
      "type": "textbox",
      "required": True,
      "maxLength": 200,
      "displayBehavior": "always",
      "condition": None,
      "placeholder": "Nhập tên...",
      "validationRules": {"allowSpecialChars": False},
      "source": "PTTK tr.X"
    },
    # ... tất cả fields
  ],
  "businessRules": [
    {"id": "BR1", "condition": "status=DRAFT", "trueBranch": "Hiển thị button Lưu", "falseBranch": "Ẩn button Lưu", "source": "RSD tr.X"},
  ],
  "errorMessages": [
    {"code": "E001", "text": "Tên không được để trống", "field": "tenField", "trigger": "empty", "source": "RSD tr.X"},
  ],
  "enableDisableRules": [
    {"target": "buttonLuu", "condition": "form valid", "defaultState": "disable", "source": "RSD tr.X"},
  ],
  "autoFillRules": [
    {"targetField": "maDichVu", "sourceField": "loaiDichVu", "condition": "chọn loại", "source": "RSD tr.X"},
  ],
  "statusTransitions": [
    {"from": "DRAFT", "to": "ACTIVE", "trigger": "Phê duyệt", "source": "RSD tr.X"},
  ],
  "permissions": [
    {"role": "ADMIN", "access": "full", "screen": "{SCREEN_NAME}", "source": "RSD tr.X"},
  ]
}

with open(r"{OUTPUT_DIR}/patch.json", "w", encoding="utf-8") as f:
    json.dump(patch, f, ensure_ascii=False, indent=2)
```

**Bước 5b** — Apply patch:

```bash
python3 {SKILL_SCRIPTS}/inventory.py patch \
  --file {INVENTORY_FILE} \
  --patch-file {OUTPUT_DIR}/patch.json
```

### 6. Báo cáo

```bash
python3 {SKILL_SCRIPTS}/inventory.py summary --file {INVENTORY_FILE}
```

In kết quả summary. Nếu `fieldConstraints = 0` → báo lỗi: "Không tìm thấy field definitions trong tài liệu."

### 7. Kiểm tra conflicts

Nếu phát hiện mâu thuẫn giữa PTTK và RSD (field name, type, required), ghi chú vào summary output để orchestrator xử lý.

## Output

`{INVENTORY_FILE}` được tạo và điền đầy đủ. In summary ra stdout.
