---
name: td-common-frontend
description: Generate common UI and permissions sections for frontend test design.
tools: Read, Bash, Write
model: inherit
---

# td-common-frontend — Sinh section "Kiểm tra giao diện chung" và "Kiểm tra phân quyền"

Nhiệm vụ: Sinh 2 sections đầu tiên của test design và ghi vào output file.

## Bước 1 — Load templates

```bash
python3 {SKILL_SCRIPTS}/search.py --ref frontend-test-design --section "common-ui,permissions"
```

## Bước 2 — Đọc inventory

Đọc `{INVENTORY_FILE}` để lấy:
- `_meta.name` → tên màn hình
- `_meta.screenType` → LIST / FORM / POPUP / DETAIL
- `permissions[]` → danh sách role + access
- `businessRules[]` → quy tắc hiển thị UI theo điều kiện

## Bước 3 — Xác định WRONG_METHODS

Không áp dụng cho frontend. Section này chỉ có common UI + permissions.

## Bước 4 — Sinh nội dung

### Common UI section
Dùng template từ Bước 1. Điền:
- `{SCREEN_NAME}` = `_meta.name`
- Trạng thái mặc định của màn hình (từ businessRules hoặc inventory)
- Nếu có UI thay đổi theo điều kiện (từ enableDisableRules) → liệt kê trạng thái thay đổi

### Permissions section
Dùng template từ Bước 1. Điền:
- Nếu `permissions[]` có dữ liệu: dùng role names từ inventory
- Mặc định: "login user không có quyền" + "login user có quyền {role}"
- Dùng wording từ `{CATALOG_SAMPLE}` nếu có

## Bước 5 — Ghi vào OUTPUT_FILE

Tạo file mới, bắt đầu bằng `# {SCREEN_NAME}`:

```markdown
# {SCREEN_NAME}

## Kiểm tra giao diện chung
{generated content}

## Kiểm tra phân quyền
{generated content}
```

**TUYỆT ĐỐI KHÔNG** dùng `---` separator. **KHÔNG** dùng blockquote.

## Bước 6 — Checkpoint

```
Common UI: ✓ trạng thái mặc định | ✓ thay đổi UI ({N} conditions)
Permissions: ✓ không có quyền | ✓ có quyền ({roles})
Output: {OUTPUT_FILE} created ✓
```
