---
name: tc-search
description: Generate search/filter/pagination test cases — only for LIST screen type.
tools: Read, Bash, Write
model: inherit
---

# tc-search — Sinh test cases tìm kiếm / lọc / phân trang (LIST screens only)

Nhiệm vụ: Sinh test cases cho các sections tìm kiếm, lọc, phân trang. CHỈ chạy khi screenType = LIST.

## Bước 0: Kiểm tra screenType

```bash
python -c "
import sys, json
ctx = json.load(open(r'{TC_CONTEXT_FILE}', encoding='utf-8'))
if ctx.get('screenType', '').upper() != 'LIST':
    print('SKIP: screenType is not LIST — tc-search not needed')
    sys.exit(0)
print('PROCEED: LIST screen detected')
"
```

Nếu output chứa `SKIP` → DỪNG HOÀN TOÀN. Không phải lỗi — màn hình này không cần search test cases.

## Bước 1: Đọc tc-context.json

Đọc `{TC_CONTEXT_FILE}` bằng Read tool. Lấy:
- `preConditionsBase` — dùng cho tất cả test cases
- `catalogStyle` — dùng để follow đúng format/wording

## Bước 2: Đọc test design file — trích xuất search/filter/pagination sections

Đọc `{TEST_DESIGN_FILE}`. Tìm và trích xuất các sections liên quan đến tìm kiếm, lọc, phân trang, ví dụ:
- `## Kiểm tra tìm kiếm`
- `## Kiểm tra phân trang`
- `## Kiểm tra lưới dữ liệu`
- `## Kiểm tra bộ lọc`
- Và các sections tương tự

Với mỗi section, thu thập tất cả bullets — mỗi bullet = 1 test case cần sinh.

## Bước 3: Load rules

```bash
python {SKILL_SCRIPTS}/search.py --ref fe-test-case
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints --filter section=search
```

## Bước 4: Sinh test cases

Với mỗi section và mỗi bullet case trong test design:

| Trường | Giá trị |
|--------|---------|
| `testSuiteName` | Tên section (VD: `"Kiểm tra tìm kiếm"`, `"Kiểm tra phân trang"`) |
| `testCaseName` | Lấy TRỰC TIẾP từ bullet text trong mindmap — KHÔNG thêm prefix |
| `summary` | Giống hệt `testCaseName` |
| `preConditions` | `preConditionsBase` từ tc-context.json |
| `step` | Mô tả UI actions theo catalogStyle — dùng động từ: Click, Nhập, Chọn, Quan sát, etc. |
| `expectedResult` | UI state — Hiển thị, Lọc, Cập nhật danh sách, etc. KHÔNG dùng HTTP status codes |
| `importance` | `"Medium"` |
| `result` | `"PENDING"` |
| `externalId` | `""` |
| `testSuiteDetails` | `""` |
| `specTitle` | `""` |
| `documentId` | `""` |
| `estimatedDuration` | `""` |
| `note` | `""` |

> ⚠️ testCaseName = lấy TRỰC TIẾP từ mindmap bullet — KHÔNG thêm prefix
> ⚠️ result = "PENDING"
> ⚠️ KHÔNG có HTTP status codes trong expectedResult

## Bước 5: Ghi batch-search.json

Dùng Write tool để ghi `{OUTPUT_DIR}/batch-search.json`.

> ⚠️ DÒNG ĐẦU TIÊN phải là `[` — không có text, comment, hay markdown trước đó
> ⚠️ DÒNG CUỐI CÙNG phải là `]`
> ⚠️ KHÔNG ghi bất kỳ text nào ngoài JSON array thuần túy

In checkpoint: `✓ batch-search.json written — {N} test cases`

---

## Context block

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
TC_CONTEXT_FILE: {output-folder}/tc-context.json
TEST_DESIGN_FILE: {path}
INVENTORY_FILE: {path}
OUTPUT_DIR: {output-folder}
PROJECT_RULES: {content or "none"}
===================
```
