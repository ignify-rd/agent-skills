---
name: td-common
description: Generate the common section (Method, URL, Authorization) for API test design.
tools: Read, Bash, Write
model: inherit
---

# td-common — Sinh section "Kiểm tra các case common"

Nhiệm vụ: Sinh section common cho API test design và ghi vào output file.

## Load template

```bash
python {SKILL_SCRIPTS}/search.py --ref api-test-design --section "common"
```

## Quy tắc

- Dùng format ĐƠN GIẢN: `- status: 107` — **TUYỆT ĐỐI KHÔNG** dùng `1\. Check api trả về:` trong common
- `{WRONG_METHODS}`: POST → "GET/PUT/DELETE", GET → "POST/PUT/DELETE", PUT → "GET/POST/DELETE"
- Copy base template **chính xác**, chỉ thay `{API_NAME}` và `{WRONG_METHODS}`

## Format output bắt buộc

```markdown
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
```

## Quy trình

1. Đọc `{INVENTORY_FILE}` để lấy: `_meta.endpoint`, `_meta.name`, `_meta.method`
2. Xác định `{WRONG_METHODS}` từ method
3. Dùng catalog wording nếu có (từ `{CATALOG_SAMPLE}`) — catalog > template
4. Ghi section vào `{OUTPUT_FILE}`:
   - Nếu file chưa tồn tại: tạo mới, bắt đầu bằng `# {API_NAME}`
   - Nếu đã tồn tại: append section
5. In checkpoint: "Common: Method ✓ URL ✓ Authorization ✓"
