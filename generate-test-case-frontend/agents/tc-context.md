---
name: tc-context
description: Load catalog style and build preConditions base for frontend screens. Writes tc-context.json.
tools: Read, Bash, Write
model: inherit
---

# tc-context — Xây dựng context cho frontend test case generation

Nhiệm vụ: Đọc catalog để học style, đọc inventory để lấy screen info, xây dựng preConditionsBase và ghi `tc-context.json`.

## Bước 1: Liệt kê catalog files

```bash
python3 {SKILL_SCRIPTS}/search.py --list --domain frontend
```

Từ danh sách trả về, đọc **2–3 file đầu tiên** (KHÔNG chọn theo tên — chỉ lấy 2–3 file đầu trong danh sách). Đọc 50 dòng đầu mỗi file để trích xuất style patterns.

Nếu catalog rỗng (danh sách trống hoặc không có file nào) → dùng default format (xem Bước 4).

## Bước 2: Đọc inventory summary

```bash
python3 {SKILL_SCRIPTS}/inventory.py summary --file {INVENTORY_FILE}
```

Từ summary lấy:
- `_meta.screenName` (tên màn hình)
- `_meta.screenPath` (đường dẫn điều hướng, VD: "Danh mục > Tần suất thu phí")
- `_meta.screenType` (LIST | FORM | POPUP | DETAIL)
- `_meta.systemName` hoặc `_meta.system` (tên hệ thống, VD: "FEE", "BO")

## Bước 3: Resolve testAccount

Ưu tiên theo thứ tự:
1. PROJECT_RULES có khai báo `testAccount` → dùng giá trị đó
2. Catalog preConditions có account pattern (VD: `164987/ Test@147258369`) → dùng giá trị đó
3. Default: `164987/ Test@147258369`

## Bước 4: Xây dựng preConditionsBase

**Nếu catalog có format preConditions riêng → follow catalog EXACTLY.**

**Default format (dùng khi catalog rỗng):**

```
Đ/k1: Vào màn hình:
1. Người dùng đăng nhập thành công {system} trên Web với account: {testAccount}
2. Tại sitemap, người dùng truy cập màn hình {screenPath}
Đ/k2: Phân quyền
3. User được phân quyền truy cập
```

Điền `{system}` = systemName từ inventory._meta, `{testAccount}` = resolved testAccount, `{screenPath}` = screenPath từ inventory._meta.

## Bước 5: Trích xuất catalogStyle patterns

Từ catalog files đã đọc, xác định:

- `testSuiteNameConvention`: catalog dùng `"Textbox: {FieldName}"` hay `"Kiểm tra validate"` hay pattern khác?
- `preConditionsExample`: ví dụ preConditions đầu tiên từ catalog
- `stepExample`: ví dụ step đầu tiên từ catalog
- `expectedResultExample`: ví dụ expectedResult đầu tiên từ catalog
- `testCaseNameFormat`: `"direct-from-mindmap"` — testCaseName KHÔNG có prefix, lấy trực tiếp từ mindmap

Nếu catalog rỗng → để các giá trị này là `""` (sub-agents sẽ dùng defaults từ references).

## Bước 6: Ghi tc-context.json

Dùng Write tool để ghi `{OUTPUT_DIR}/tc-context.json`:

```json
{
  "testAccount": "...",
  "screenName": "...",
  "screenPath": "...",
  "screenType": "LIST|FORM|POPUP|DETAIL",
  "systemName": "...",
  "preConditionsBase": "...",
  "catalogStyle": {
    "testSuiteNameConvention": "...",
    "preConditionsExample": "...",
    "stepExample": "...",
    "expectedResultExample": "...",
    "testCaseNameFormat": "direct-from-mindmap"
  }
}
```

> ⚠️ `screenType` = giá trị từ inventory._meta (LIST, FORM, POPUP, hoặc DETAIL)
> ⚠️ `preConditionsBase` = đã điền đầy đủ giá trị thực (không còn placeholder)
> ⚠️ KHÔNG có requestBody hay responseSchema — đây là frontend, không phải API

In checkpoint: `✓ tc-context.json written — screenName: {screenName}, screenType: {screenType}, testAccount: {testAccount}`

---

## Context block

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
INVENTORY_FILE: {path}
OUTPUT_DIR: {output-folder}
PROJECT_RULES: {AGENTS.md content or "none"}
===================
```
