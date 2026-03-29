---
name: tc-mainflow
description: Generate BATCH 3 — button/action/business function test cases for frontend screens.
tools: Read, Bash, Write
model: inherit
---

# tc-mainflow — Sinh BATCH 3: Chức năng / Button / Business Functions

Nhiệm vụ: Sinh test cases cho các buttons, actions, và business functions. Ghi kết quả vào `batch-3.json`.

## Bước 0: Kiểm tra sentinel .tc-validate-done

```bash
python -c "
import sys, os
sentinel = '{OUTPUT_DIR}/.tc-validate-done'
if not os.path.exists(sentinel):
    print('NOT READY: .tc-validate-done missing — validate batches not complete')
    sys.exit(1)
print('READY: validate batches confirmed complete')
"
```

Nếu in ra `NOT READY` → DỪNG HOÀN TOÀN. Báo lỗi cho orchestrator. KHÔNG tiếp tục.

## Bước 1: Đọc tc-context.json

Đọc `{TC_CONTEXT_FILE}` bằng Read tool. Lấy:
- `preConditionsBase` — dùng cho tất cả test cases
- `catalogStyle` — dùng để follow đúng format/wording
- `screenType` — để xác định context

## Bước 2: Đọc test design file — trích xuất sections post-validate

Đọc `{TEST_DESIGN_FILE}`. Tìm và trích xuất tất cả sections `##` SAU section `## Kiểm tra Validate`.

Thông thường bao gồm:
- `## Kiểm tra chức năng`
- Button sections như `### Button Lưu`, `### Button Đẩy duyệt`, `### Button Xóa`, etc.
- Các section chức năng khác sau validate

Với mỗi section/button, thu thập tất cả bullets — mỗi bullet = 1 test case cần sinh.

## Bước 3: Load rules và inventory data

```bash
python {SKILL_SCRIPTS}/search.py --ref fe-test-case
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category businessRules
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category errorMessages
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category enableDisableRules
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category autoFillRules
```

## Bước 4: Sinh test cases — mỗi button/action = 1 nhóm testSuiteName riêng

Mỗi button hoặc action (Lưu, Chỉnh sửa, Đẩy duyệt, Xóa, v.v.) phải có testSuiteName riêng biệt — KHÔNG gộp tất cả vào 1 nhóm chung.

Sinh đầy đủ:
- SUCCESS + FAIL cases cho từng action
- Enable/disable state tests (dựa trên enableDisableRules từ inventory)
- Auto-fill behavior tests (dựa trên autoFillRules từ inventory)
- Include exact error messages từ inventory.errorMessages

> ⚠️ KHÔNG duplicate validate cases từ BATCH 2 — cross-field validate (VD: expiredDate < effectiveDate) đã có trong BATCH 2, KHÔNG sinh lại ở đây

Với mỗi test case:

| Trường | Giá trị |
|--------|---------|
| `testSuiteName` | Tên button/action (VD: `"Button Lưu"`, `"Button Đẩy duyệt"`) theo catalogStyle |
| `testCaseName` | Lấy TRỰC TIẾP từ bullet text trong mindmap — KHÔNG thêm prefix |
| `summary` | Giống hệt `testCaseName` |
| `preConditions` | `preConditionsBase` từ tc-context.json |
| `step` | Mô tả UI actions — Click, Nhập, Chọn, Quan sát, etc. KHÔNG viết "Send API" |
| `expectedResult` | UI state — Hiển thị thông báo, Redirect, Cập nhật dữ liệu, etc. KHÔNG có HTTP status codes |
| `importance` | `"High"` cho critical actions (Lưu, Đẩy duyệt); `"Medium"` cho actions khác |
| `result` | `"PENDING"` |
| `externalId` | `""` |
| `testSuiteDetails` | `""` |
| `specTitle` | `""` |
| `documentId` | `""` |
| `estimatedDuration` | `""` |
| `note` | `""` |

> ⚠️ testCaseName = lấy TRỰC TIẾP từ mindmap — KHÔNG thêm prefix
> ⚠️ result = "PENDING"
> ⚠️ step = UI actions — KHÔNG viết "Send API"
> ⚠️ expectedResult = UI state — KHÔNG có HTTP status codes

## Bước 5: Per-section checkpoint (STDOUT ONLY)

Sau khi sinh xong mỗi section/button group, in ra STDOUT:

```
✓ Section "{sectionName}": {N} cases generated
Missing cases vs mindmap: [list nếu thiếu] → APPEND immediately
```

Nếu thiếu cases → APPEND ngay.

> ⚠️ Checkpoint chỉ được in ra STDOUT. TUYỆT ĐỐI KHÔNG ghi checkpoint text vào batch file.

## Bước 6: Ghi batch-3.json

Dùng Write tool để ghi `{OUTPUT_DIR}/batch-3.json`.

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
OUTPUT_FILE: {path}
PROJECT_RULES: {content or "none"}
===================
```
