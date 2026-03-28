---
name: td-validate-frontend
description: Generate validate test cases for a batch of frontend fields using field-type templates.
tools: Read, Bash, Edit, Write
model: inherit
---

# td-validate-frontend — Sinh validate cases cho 1 batch fields

Nhiệm vụ: Sinh validate test cases cho đúng `{FIELD_BATCH}` fields được giao. Dùng field-type templates.

## Bước 1 — Load field type templates

Load **chỉ những templates cần thiết** cho batch này:

```bash
python {SKILL_SCRIPTS}/search.py --ref field-templates --section "{FIELD_TYPES_NEEDED}"
```

Ví dụ nếu batch có textbox + combobox + datepicker:
```bash
python {SKILL_SCRIPTS}/search.py --ref field-templates --section "textbox,combobox,datepicker"
```

Mapping field.type → section name:
- textbox / text / input → `textbox`
- combobox → `combobox`
- dropdown (có values[]) → `simple-dropdown`
- dropdown (có apiEndpoint) → `searchable-dropdown`
- toggle / switch → `toggle`
- checkbox → `checkbox`
- button → `button`
- icon_x → `icon-x`
- date / datepicker → `datepicker`
- daterange → `daterange`
- textarea → `textarea`
- number → `number`
- radio → `radio`
- file_upload → `file-upload`
- password → `password`
- tag_input → `tag-input`
- richtext → `richtext`

## Bước 2 — Đọc context

- Đọc `{INVENTORY_FILE}` → lấy `fieldConstraints` cho các fields trong batch
- Đọc `{CATALOG_SAMPLE}` nếu được cung cấp → dùng làm wording reference

## Bước 3 — Sinh validate cho TỪNG field theo thứ tự

### Quy tắc chung
- **Heading field**: `### Kiểm tra {fieldType} "{fieldName}"`
- Template sinh ~80% cases — điền đúng `{fieldName}`, `{maxLength}`, `{placeholder}`, `{allowSpecialChars}`
- **TẤT CẢ validate responses** = bullet đơn giản, KHÔNG có `1\. Check api trả về:`
- Dùng format: `- {kết quả mong đợi}`
- `allowSpecialChars` từ `validationRules` trong inventory

### Quy tắc displayBehavior
- `always` → chỉ sinh validate cases (không có enable/disable)
- `conditional` → sinh validate cases + thêm case "khi {condition}: field disable → không validate"

### Quy tắc cross-field
Nếu field có ràng buộc với field khác (VD: ngayKetThuc ≥ ngayHieuLuc):
→ Thêm 3 cases TRONG section `###` của field đó:
- `{fieldName} nhỏ hơn {relatedField}` → lỗi
- `{fieldName} bằng {relatedField}` → Theo RSD
- `{fieldName} lớn hơn {relatedField}` → thành công

### Quy tắc errorMessages
Nếu inventory có `errorMessages[field="{fieldName}"]` → dùng exact text từ inventory.

## Bước 4 — Per-field checkpoint (BẮT BUỘC sau MỖI field)

> ⚠️ **Checkpoint chỉ trong MEMORY / STDOUT — KHÔNG ghi vào batch file.**

```
✓ Field {fieldName} ({type}): {generated} cases từ template.
  [V3] Không dùng "→ error" (format API) — chỉ dùng bullet: ✅/❌
  [V4] Không có Status 4xx/5xx — format frontend là bullet đơn: ✅/❌
  Missing cases từ template: [list nếu có] → THÊM ngay.
```

Nếu thiếu → THÊM ngay, KHÔNG bỏ qua.

## Bước 5 — Kiểm tra errorMessages từ inventory

Sau khi xong batch, đọc `{INVENTORY_FILE}`:
- Lấy `errorMessages` cho các fields trong batch
- Kiểm tra mỗi message có bullet trong output chưa
- Thiếu → THÊM bullet với exact text

## Bước 6 — Ghi vào file batch riêng

**KHÔNG ghi vào `{OUTPUT_FILE}` chung.** Ghi vào file riêng:

```
{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.md
```

> ⚠️ **NỘI DUNG FILE BATCH CHỈ ĐƯỢC CHỨA validate cases. TUYỆT ĐỐI KHÔNG ghi:**
> - `# BATCH N: ...` hay bất kỳ heading H1 nào
> - `## Kiểm tra validate`, `## Kiểm tra Validate`, hay bất kỳ heading H2 nào
> - `## Per-Field Checkpoint`, bảng checkpoint hay count table
> - `=== Batch N complete ===` hay bất kỳ separator text nào
> - Bất kỳ text nào từ các bước checkpoint hay tổng kết
>
> **DÒNG ĐẦU TIÊN của file PHẢI LÀ: `### Kiểm tra {fieldType} "..."` — tuyệt đối không có gì trước đó.**

File này chứa **chỉ** validate cases của batch, không có heading `## Kiểm tra validate` — orchestrator sẽ merge sau.

Ví dụ nội dung `validate-batch-1.md`:
```markdown
### Kiểm tra textbox "Tên dịch vụ"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

...

### Kiểm tra combobox "Loại dịch vụ"
...
```

## Bước 7 — Batch checkpoint

> ⚠️ **In ra CONSOLE/STDOUT ONLY — KHÔNG ghi vào batch file hay output file nào.**

```
=== Batch {BATCH_NUMBER} complete ===
Output: {OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.md
Fields: {field list}
Counts: {field}: {N} cases ✓
Template coverage: {N}/{N} template cases applied
Error messages covered: {N}/{total for batch}
```

## Output

`{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.md` — chứa validate cases của batch này.
Orchestrator sẽ merge tất cả batch files vào `{OUTPUT_FILE}` theo đúng thứ tự.
