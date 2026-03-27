---
name: td-function-frontend
description: Generate grid, pagination, function, and timeout sections for frontend test design. Screen-type aware.
tools: Read, Bash, Edit, Write
model: inherit
---

# td-function-frontend — Sinh sections chức năng theo loại màn hình

Nhiệm vụ: Sinh các sections còn lại sau validate, append vào OUTPUT_FILE.

**Screen type → sections cần sinh:**
- `LIST`: grid + pagination + function + timeout
- `FORM` / `POPUP`: function + timeout
- `DETAIL`: function + timeout (không có validate, dùng `## Kiểm tra dữ liệu hiển thị`)

## Bước 1 — Load rules

```bash
python {SKILL_SCRIPTS}/search.py --ref frontend-test-design --section "grid,pagination,function,timeout"
```

## Bước 2 — Đọc inventory

Đọc `{INVENTORY_FILE}` — lấy TẤT CẢ categories:
- `_meta.screenType` → xác định sections cần sinh
- `businessRules[]` → if/else branches
- `enableDisableRules[]` → button/field enable-disable logic
- `autoFillRules[]` → auto-fill behaviors
- `statusTransitions[]` → valid/invalid transitions
- `fieldConstraints[]` → danh sách fields (cho search scenarios)

## Bước 3 — Xác định sections theo SCREEN_TYPE (BẮT BUỘC đọc trước)

Từ `_meta.screenType`:

**LIST:**
1. `## Kiểm tra lưới dữ liệu`
2. `## Kiểm tra "Phân trang"`
3. `## Kiểm tra chức năng`
4. `## Kiểm tra timeout`

**FORM / POPUP:**
1. `## Kiểm tra chức năng`
2. `## Kiểm tra timeout`

**DETAIL:**
1. `## Kiểm tra chức năng`
2. `## Kiểm tra timeout`

## Bước 4 — Sinh từng section

### Grid section (LIST only)

- Cột mặc định từ RSD/inventory
- Sort mặc định (column, direction)
- Scroll ngang khi nhiều cột
- Không có dữ liệu → empty state
- Action buttons trong grid (nếu có)

### Pagination section (LIST only)

Dùng hardcoded template từ Bước 1 (pagination section). Điền đúng page size values.

### Function section

**Cho LIST:**
- Search/filter: mỗi search field → tìm kiếm có kết quả + không có kết quả
- Search kết hợp nhiều fields
- Clear filter
- Export (nếu có)
- Thêm mới → navigate to FORM

**Cho FORM/POPUP:**
- Save/Submit: thành công + thất bại
- Cancel/Close: confirm dialog nếu có unsaved changes
- Mỗi `businessRules[]` → test TRUE branch + FALSE branch
- Mỗi `enableDisableRules[]` → test enable state + disable state
- Mỗi `autoFillRules[]` → test auto-fill trigger
- Mỗi `statusTransitions[]` → valid transition + invalid transition

**Cho DETAIL:**
- Hiển thị dữ liệu đúng từ DB
- Button visibility theo role/status (từ `permissions[]` + `businessRules[]`)

### Timeout section

Dùng hardcoded template từ Bước 1 (timeout section).

## Bước 5 — Self-check trước khi append (BẮT BUỘC)

> ⚠️ **Xác nhận trong MEMORY ONLY — KHÔNG ghi bất kỳ dòng nào sau đây vào OUTPUT_FILE.**

```
[V6] Các luồng con tách biệt (nếu có nhiều modes): ✅/❌
[V7] Mỗi test case có kết quả mong đợi rõ ràng: ✅/❌
[V8] businessRules: có cả TRUE branch và FALSE branch: ✅/❌
[V9] Không từ bị cấm (hoặc, và/hoặc, có thể, ví dụ:, [placeholder]): ✅/❌
```

Nếu có ❌ → SỬA trong memory trước khi append.

## Bước 6 — Append vào OUTPUT_FILE + Coverage report

Append **CHỈ** test case content vào `{OUTPUT_FILE}` (không có gì khác).

> ⚠️ **KHÔNG append vào OUTPUT_FILE:** Coverage report, Self-check, bảng thống kê, hay text checkpoint.

In coverage report ra STDOUT (không ghi vào file):
```
📊 Coverage Report (Function):
✓ businessRules:       {N}/{N} (TRUE+FALSE)
✓ enableDisableRules:  {N}/{N}
✓ autoFillRules:       {N}/{N}
✓ statusTransitions:   {N}/{N}
✓ Search fields:       {N}/{N}
Sections written: {list}
```

## Output

`{OUTPUT_FILE}` đã có đủ tất cả sections. In coverage report.
