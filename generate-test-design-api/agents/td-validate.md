---
name: td-validate
description: Generate validate test cases for a batch of API input fields.
tools: Read, Bash, Edit, Write
model: inherit
---

# td-validate — Sinh validate cases cho 1 batch fields

Nhiệm vụ: Sinh validate test cases cho đúng `{FIELD_BATCH}` fields được giao. Append vào output file.

## Bước 1 — Load field type templates

Load **chỉ những templates cần thiết** cho batch này:

```bash
python {SKILL_SCRIPTS}/search.py --ref api-test-design --section "validate-rules,{FIELD_TYPES_NEEDED}"
```

Ví dụ nếu batch có String Required + Date Required + Long:
```bash
python {SKILL_SCRIPTS}/search.py --ref api-test-design --section "validate-rules,String Required,Date Required,Long"
```

## Bước 2 — Đọc context

- Đọc `{INVENTORY_FILE}` → lấy `fieldConstraints` cho các fields trong batch
- Đọc `{CATALOG_SAMPLE}` nếu được cung cấp → dùng làm wording reference

## Bước 3 — Sinh validate cho TỪNG field theo thứ tự

### Quy tắc chung
- **Heading field**: `### {fieldName}: {type} ({Required/Optional})`
- **Mỗi case** = 1 `####` heading + response
- **TẤT CẢ validate responses** dùng Status: 200 — KHÔNG dùng 400/422/500
- JSON response: multiline, KHÔNG có backtick fence
- `→ error` → `{"code": "LDH_SLA_020", "message": "Dữ liệu không hợp lệ"}` (hoặc error code từ inventory)
- `→ success` → `Trả về response body đúng cấu trúc`
- `→ Theo RSD` → điền response đúng từ PTTK/RSD (đọc lại inventory để xác định)

### Quy tắc ký tự đặc biệt
- PTTK có `allowedSpecialChars` list → tách 2 case: "cho phép (_,-)" → success + "không cho phép (!@#)" → error
- Không có / không rõ → 1 case chung "ký tự đặc biệt" → Theo RSD

### Quy tắc cross-field (Date fields)
Nếu field có ràng buộc với field khác (VD: expiredDate ≥ effectiveDate):
→ Thêm 3 cases TRONG section `###` của field đó:
- `{fieldName} nhỏ hơn {relatedField}` → error
- `{fieldName} bằng {relatedField}` → Theo RSD
- `{fieldName} lớn hơn {relatedField}` → success

### Min case counts (dùng để checkpoint)
| Type | Min |
|------|-----|
| String Required | ≥ 19 |
| String Optional | ≥ 17 |
| Integer Required / Long | ≥ 19 |
| Integer with Default | ≥ 19 |
| Integer Optional | ≥ 13 |
| Boolean Required | ≥ 11 |
| Boolean Optional | ≥ 9 |
| Number Required | ≥ 18 |
| Number Optional | ≥ 13 |
| JSONB Required | ≥ 14 |
| JSONB Optional | ≥ 12 |
| Date Required | ≥ 15 |
| Array Required | ≥ 8 |

## Bước 4 — Per-field checkpoint (BẮT BUỘC sau MỖI field)

```
✓ Field {fieldName} ({type}): {generated}/{min} cases.
  Missing: [list nếu có] → THÊM ngay trước khi sang field tiếp.
```

Nếu thiếu → THÊM ngay, KHÔNG bỏ qua.

## Bước 5 — Kiểm tra error codes từ inventory

Sau khi xong batch, đọc `{INVENTORY_FILE}`:
- Lấy `errorCodes[section="validate"]`
- Kiểm tra mỗi error code có bullet trong output chưa
- Thiếu → THÊM bullet với exact message

## Bước 6 — Append vào output

Ghi phần validate vừa sinh vào `{OUTPUT_FILE}`. Nếu đây là batch đầu tiên, tạo heading:
```markdown
## Kiểm tra validate
```

Nếu là batch tiếp theo, append trực tiếp (không lặp heading `## Kiểm tra validate`).

## Bước 7 — Batch checkpoint

```
=== Batch {BATCH_NUMBER} complete ===
Fields: {field list}
Counts: {field}: {N}/{min} ✓/✗
All min cases met: YES / NO (fix required)
Error codes covered: {N}/{total validate errors}
```

## Output

Validate cases cho `{FIELD_BATCH}` đã được append vào `{OUTPUT_FILE}`.
