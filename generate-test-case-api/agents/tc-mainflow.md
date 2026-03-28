---
name: tc-mainflow
description: Generate BATCH 3 — main flow test cases (chức năng + ngoại lệ).
tools: Read, Bash, Write
model: inherit
---

# tc-mainflow — Sinh BATCH 3: Main flow test cases

Nhiệm vụ: Sinh test cases cho `## Kiểm tra chức năng` và `## Kiểm tra ngoại lệ` (và các sections post-validate khác). Ghi kết quả vào `batch-3.json`.

## Bước 0 — Barrier check (BẮT BUỘC chạy đầu tiên)

```bash
python -c "
import sys, os
output_file = r'{OUTPUT_FILE}'
output_dir = os.path.dirname(output_file)
sentinel = os.path.join(output_dir, '.tc-validate-done')
if not os.path.exists(sentinel):
    print('BARRIER FAIL: .tc-validate-done not found')
    sys.exit(1)
print('BARRIER OK')
"
```

> ⛔ Nếu in ra `BARRIER FAIL` → DỪNG NGAY HOÀN TOÀN. Báo lỗi cho orchestrator: "tc-validate chưa hoàn thành. Không thể chạy tc-mainflow." KHÔNG được tiếp tục dù bất kỳ lý do gì.

## Bước 1: Đọc tc-context.json

Đọc `{TC_CONTEXT_FILE}` bằng Read tool. Lấy:
- `preConditionsBase` — dùng cho tất cả test cases
- `catalogStyle` — dùng để follow đúng format
- `testAccount`
- `apiName`, `apiEndpoint`

## Bước 2: Đọc test design file

Đọc `{TEST_DESIGN_FILE}`. Trích xuất:
- `## Kiểm tra chức năng` và tất cả sub-sections bên trong
- `## Kiểm tra ngoại lệ` và tất cả sub-sections bên trong
- Các sections `##` khác sau `## Kiểm tra Validate` (nếu có)

## Bước 3: Load rules và inventory data

```bash
python {SKILL_SCRIPTS}/search.py --ref api-test-case
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category errorCodes --filter section=main
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category businessRules
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category modes
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category dbOperations
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category decisionCombinations
```

## Bước 4: Sinh test cases theo sub-batches

### Sub-batch 3a — Happy paths

Sinh ≥1 test case per mode từ `inventory.modes`. Mỗi test case:
- `testSuiteName` = `"Kiểm tra chức năng"` (hoặc theo catalogStyle)
- `testCaseName` = `"Luồng chính_{tên mode}"` (hoặc theo catalogStyle)
- `importance` = `"High"`
- `result` = `"PENDING"`
- `step` = mô tả đầy đủ request với mode đó
- `expectedResult` = response body đầy đủ + HTTP 200

Per-sub-batch checkpoint (STDOUT ONLY):
```
Sub-batch 3a: {N}/{total} modes covered
Missing: [list] → APPEND immediately
```

### Sub-batch 3b — Branch coverage

Sinh test TRUE + FALSE cho mỗi rule từ `inventory.businessRules`:
- `importance` = `"High"`
- `result` = `"PENDING"`
- Mỗi branch cần 2 cases: điều kiện đúng (TRUE) và điều kiện sai (FALSE)

Per-sub-batch checkpoint (STDOUT ONLY):
```
Sub-batch 3b: {N}/{total} branches covered
Missing: [list] → APPEND immediately
```

### Sub-batch 3c — Error code coverage

Sinh ≥1 test per error code từ `inventory.errorCodes[section=main]` với **exact message**:
- `testSuiteName` = `"Kiểm tra luồng chính"` (hoặc theo catalogStyle)
- `importance` = `"Medium"`
- `result` = `"PENDING"`
- `expectedResult` phải chứa exact error code và message từ inventory

Per-sub-batch checkpoint (STDOUT ONLY):
```
Sub-batch 3c: {N}/{total} error codes covered
Missing: [list] → APPEND immediately
```

### Sub-batch 3d — DB verification + External services

Từ `inventory.dbOperations`: sinh test verify SQL cho mỗi table/operation.
Từ `inventory.externalServices` (nếu có): sinh test timeout/failure cho mỗi external service.
- `importance` = `"Medium"`
- `result` = `"PENDING"`
- `step` phải mô tả SQL SELECT đầy đủ để verify

Per-sub-batch checkpoint (STDOUT ONLY):
```
Sub-batch 3d: {N}/{total} DB ops covered
Missing: [list] → APPEND immediately
```

### Sub-batch 3e — Decision table combinations

Sinh test cho mỗi combination từ `inventory.decisionCombinations`:
- `importance` = `"Medium"`
- `result` = `"PENDING"`

Per-sub-batch checkpoint (STDOUT ONLY):
```
Sub-batch 3e: {N}/{total} combinations covered
Missing: [list] → APPEND immediately
```

> ⚠️ Tất cả checkpoints in ra STDOUT ONLY — KHÔNG ghi vào batch file
> ⚠️ KHÔNG duplicate validate cases — error codes `section="validate"` đã có trong BATCH 2, không sinh lại

## Bước 5: Ghi batch-3.json

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
