---
name: tc-verify
description: Final gap analysis, dedup, and output. Merges all batches and fills coverage gaps.
tools: Read, Bash, Write
model: inherit
---

# tc-verify — Gap analysis, dedup, và output cuối cùng

Nhiệm vụ: Merge tất cả batch files, phân tích coverage gaps, tự động fill gaps, áp dụng project rules, và ghi file output cuối cùng.

## Bước 1: Merge tất cả batches

```bash
python3 {SKILL_SCRIPTS}/merge_batches.py \
  --output-dir {OUTPUT_DIR} \
  --output-file {OUTPUT_DIR}/test-cases-merged.json
```

Nếu lệnh trên exit 1 → DỪNG HOÀN TOÀN, báo lỗi cụ thể cho orchestrator. KHÔNG tiếp tục.

## Bước 2: Đọc merged file + inventory data cho gap analysis

Đọc `{OUTPUT_DIR}/test-cases-merged.json` bằng Read tool.

Query inventory:
```bash
python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category errorCodes --filter section=main
python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category businessRules
python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category modes
python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category dbOperations
python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints
```

## Bước 3: Gap analysis

Với mỗi inventory item, kiểm tra xem đã có test case cover chưa:

| Inventory category | Cách kiểm tra coverage |
|--------------------|------------------------|
| `errorCodes` | Tìm code value trong `testCaseName` / `step` / `expectedResult` |
| `businessRules` | Tìm rule keyword trong `testCaseName` / `step` |
| `modes` | Tìm mode name trong `testCaseName` / `step` |
| `dbOperations` | Tìm table name trong `step` / `expectedResult` |
| `fieldConstraints` | Đếm số test cases có `testSuiteName` = `"Kiểm tra trường {name}"` |

In gap report ra STDOUT:
```
🔍 Gap Analysis:
- ☐ errorCode "LDH_SLA_001" → chưa có test case trigger
- ☐ mode "Lưu nháp" → chưa có happy path
- ☐ businessRule BR3 FALSE → chưa có test case
```

Nếu không có gap → in `✓ Gap Analysis: No gaps found`.

## Bước 4: Auto-fill ALL gaps

Sinh test cases cho TẤT CẢ gaps được phát hiện ở Bước 3. Append vào array đã đọc.

Với mỗi gap case:
- `result` = `"PENDING"`
- `summary` = giống hệt `testCaseName`
- `externalId`, `testSuiteDetails`, `specTitle`, `documentId`, `estimatedDuration`, `note` = `""`
- Dùng `preConditionsBase` từ `{TC_CONTEXT_FILE}`

## Bước 5: Áp dụng project rules

Đọc `{TC_CONTEXT_FILE}` để lấy catalogStyle (nếu chưa đọc).

Áp dụng TẤT CẢ rules từ `PROJECT_RULES` context:
- Kiểm tra section assignment đúng chưa
- Kiểm tra writing style phù hợp chưa
- Kiểm tra bất kỳ custom rule nào được định nghĩa trong PROJECT_RULES

## Bước 6: Ghi file output cuối cùng

Dùng Write tool để ghi `{OUTPUT_FILE}` (tức `{OUTPUT_DIR}/test-cases.json`).

> ⚠️ DÒNG ĐẦU TIÊN phải là `[`, DÒNG CUỐI phải là `]`
> ⚠️ File này là output CHÍNH THỨC — ghi đầy đủ, không rút gọn

In thông báo hoàn thành:
```
✅ tc-verify done: {total} test cases → {OUTPUT_FILE}
   Auto-filled gaps: {N} cases
   Final total: {total}
```

---

## Context block

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
TC_CONTEXT_FILE: {output-folder}/tc-context.json
INVENTORY_FILE: {path}
OUTPUT_DIR: {output-folder}
OUTPUT_FILE: {output-folder}/test-cases.json
PROJECT_RULES: {content or "none"}
===================
```
