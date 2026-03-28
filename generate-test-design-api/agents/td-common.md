---
name: td-common
description: Generate the common section (Method, URL, Authorization) for API test design.
tools: Read, Bash, Write
model: inherit
---

# td-common — Sinh sections "Kiểm tra token" và "Kiểm tra Endpoint & Method"

Nhiệm vụ: Sinh 2 sections common cho API test design và ghi vào output file.

## Load template

```bash
python {SKILL_SCRIPTS}/search.py --ref api-test-design --section "common"
```

## Quy tắc

- Dùng format ĐƠN GIẢN: `- Status: 401` — **TUYỆT ĐỐI KHÔNG** dùng `1\. Check api trả về:` trong common
- `{WRONG_METHODS}`: POST → "GET/PUT/DELETE", GET → "POST/PUT/DELETE", PUT → "GET/POST/DELETE"
- Copy base template **chính xác**, chỉ thay `{API_NAME}` và `{WRONG_METHODS}`
- Dùng wording từ `{CATALOG_SAMPLE}` nếu có — catalog > template

## Format output bắt buộc

```markdown
## Kiểm tra token

### Kiểm tra nhập token hết hạn

- Status: 401

### Kiểm tra không nhập token

- Status: 401

## Kiểm tra Endpoint & Method

### Kiểm tra nhập sai method ({WRONG_METHODS})

- Status: 405

### Kiểm tra nhập sai endpoint

- Status: 404
```

## Quy trình

1. Đọc `{INVENTORY_FILE}` để lấy: `_meta.endpoint`, `_meta.name`, `_meta.method`
2. Xác định `{WRONG_METHODS}` từ method
3. Dùng catalog wording nếu có (từ `{CATALOG_SAMPLE}`) — catalog > template
4. Ghi section vào `{OUTPUT_FILE}`:
   - Nếu file chưa tồn tại: tạo mới, bắt đầu bằng `# {API_NAME}`
   - Nếu đã tồn tại: append section
5. In checkpoint: "Common: Method ✓ URL ✓ Authorization ✓"
