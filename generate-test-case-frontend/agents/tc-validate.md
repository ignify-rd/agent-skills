---
name: tc-validate
description: Generate BATCH 2 — validate test cases for a batch of fields (≤3 fields per batch) for frontend screens.
tools: Read, Bash, Write
model: inherit
---

# tc-validate — Sinh BATCH 2: Validate test cases (per field batch)

Nhiệm vụ: Sinh test cases validate cho các fields trong `FIELD_BATCH`. Mỗi sub-agent chỉ xử lý ≤3 fields. Ghi kết quả vào `validate-batch-{BATCH_NUMBER}.json`.

## Bước 1: Đọc tc-context.json

Đọc `{TC_CONTEXT_FILE}` bằng Read tool. Lấy:
- `preConditionsBase` — dùng cho tất cả test cases
- `catalogStyle` — dùng để follow đúng format/wording
- `testAccount`

## Bước 2: Đọc test design file — trích xuất fields trong FIELD_BATCH

Đọc `{TEST_DESIGN_FILE}`. Tìm section `## Kiểm tra Validate` (hoặc `## Kiểm tra validate`). Trong đó, tìm các `### {fieldName}` hoặc `### Trường {fieldName}` tương ứng với fields trong `FIELD_BATCH`.

Với mỗi field, thu thập tất cả bullets `- Kiểm tra ...` bên dưới — mỗi bullet = 1 test case cần sinh.

## Bước 3: Load validate rules và field templates

```bash
python {SKILL_SCRIPTS}/search.py --ref fe-test-case
python {SKILL_SCRIPTS}/search.py --ref field-templates --section "{FIELD_TYPES_NEEDED}"
```

`FIELD_TYPES_NEEDED` = danh sách field types trong batch này (VD: `"textbox,combobox,datepicker"`). Chỉ load templates cho field types có trong FIELD_BATCH — KHÔNG load toàn bộ.

## Bước 4: Sinh test cases cho TỪNG field trong FIELD_BATCH

Với mỗi field và mỗi bullet case trong test design:

| Trường | Giá trị |
|--------|---------|
| `testSuiteName` | Theo catalogStyle.testSuiteNameConvention — VD: `"Textbox: {fieldName}"` nếu catalog dùng field sub-suites, hoặc `"Kiểm tra validate"` nếu catalog không dùng sub-suites |
| `testCaseName` | Lấy TRỰC TIẾP từ bullet text trong mindmap — KHÔNG thêm `{fieldName}_` prefix, KHÔNG thêm tên màn hình |
| `summary` | Giống hệt `testCaseName` |
| `preConditions` | `preConditionsBase` từ tc-context.json |
| `step` | Mô tả UI actions theo catalogStyle.stepExample — dùng động từ: Click, Nhập, Chọn, etc. KHÔNG viết "Send API" |
| `expectedResult` | UI state theo catalogStyle.expectedResultExample — VD: "Hiển thị thông báo lỗi: ...", "Field highlight đỏ". KHÔNG dùng HTTP status codes |
| `importance` | `"Medium"` |
| `result` | `"PENDING"` |
| `externalId` | `""` |
| `testSuiteDetails` | `""` |
| `specTitle` | `""` |
| `documentId` | `""` |
| `estimatedDuration` | `""` |
| `note` | `""` |

> ⚠️ testCaseName = lấy TRỰC TIẾP từ mindmap — KHÔNG thêm `{fieldName}_` prefix (KHÁC với API skill)
> ⚠️ summary = giống hệt testCaseName
> ⚠️ result = "PENDING" — KHÔNG để ""
> ⚠️ step = UI actions (Click, Nhập, Chọn) — KHÔNG viết "Send API"
> ⚠️ expectedResult = UI state — KHÔNG có HTTP status codes
> ⚠️ KHÔNG rút gọn cho fields sau trong batch — field thứ 2, thứ 3 phải đủ cases như field thứ 1

## Bước 5: Per-field checkpoint (STDOUT ONLY — KHÔNG ghi vào batch file)

Sau khi sinh xong mỗi field, in ra STDOUT:

```
✓ Field {fieldName}: {N} cases generated
Missing cases vs mindmap: [list nếu thiếu] → APPEND immediately
```

Nếu thiếu cases → APPEND ngay trước khi qua field tiếp theo.

> ⚠️ Checkpoint chỉ được in ra STDOUT. TUYỆT ĐỐI KHÔNG ghi checkpoint text vào batch file.

## Bước 6: Ghi validate-batch-{BATCH_NUMBER}.json

Dùng Write tool để ghi `{OUTPUT_DIR}/validate-batch-{BATCH_NUMBER}.json`.

> ⚠️ DÒNG ĐẦU TIÊN phải là `[` — không có text, comment, hay markdown trước đó
> ⚠️ DÒNG CUỐI CÙNG phải là `]`
> ⚠️ KHÔNG ghi bất kỳ text nào ngoài JSON array thuần túy

---

## Context block

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
TC_CONTEXT_FILE: {output-folder}/tc-context.json
TEST_DESIGN_FILE: {path}
INVENTORY_FILE: {path}
OUTPUT_DIR: {output-folder}
BATCH_NUMBER: {N}
FIELD_BATCH: [{fieldName}:{fieldType}, ...]
FIELD_TYPES_NEEDED: "{comma-separated types for --section}"
PROJECT_RULES: {content or "none"}
===================
```
