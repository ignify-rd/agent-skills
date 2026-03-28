---
name: tc-verify
description: Final gap analysis, dedup, and output. Merges all frontend batches and fills coverage gaps.
tools: Read, Bash, Write
model: inherit
---

# tc-verify — Gap analysis, dedup, và output cuối cùng

Nhiệm vụ: Merge tất cả batch files, phân tích coverage gaps, tự động fill gaps, áp dụng project rules, và ghi file output cuối cùng.

## Bước 1: Merge tất cả batches

```bash
python {SKILL_SCRIPTS}/merge_batches.py \
  --output-dir {OUTPUT_DIR} \
  --output-file {OUTPUT_DIR}/test-cases-merged.json
```

Script sẽ tự động tìm và merge theo thứ tự:
1. `batch-1.json` (ui + permission)
2. `batch-search.json` (optional — nếu tồn tại)
3. `batch-validate-N.json` (validate, theo thứ tự số)
4. `batch-3.json` (function)
5. `batch-workflow.json` (optional — nếu tồn tại)

Nếu lệnh trên exit 1 → DỪNG HOÀN TOÀN, báo lỗi cụ thể cho orchestrator. KHÔNG tiếp tục.

## Bước 2: Đọc merged file + inventory data cho gap analysis

Đọc `{OUTPUT_DIR}/test-cases-merged.json` bằng Read tool.

Query inventory:
```bash
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category businessRules
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category errorMessages
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category enableDisableRules
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category autoFillRules
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category permissions
python {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category statusTransitions
```

## Bước 3: Gap analysis

Với mỗi inventory item, kiểm tra xem đã có test case cover chưa:

| Inventory category | Cách kiểm tra coverage |
|--------------------|------------------------|
| `fieldConstraints` | Đếm số test cases có testSuiteName chứa fieldName (hoặc trong validate suite) |
| `businessRules` | Tìm rule keyword trong `testCaseName` / `step` / `expectedResult` |
| `errorMessages` | Tìm error message text trong `expectedResult` |
| `enableDisableRules` | Tìm target field/button trong `testCaseName` / `step` |
| `autoFillRules` | Tìm trigger/target trong `testCaseName` / `step` |
| `permissions` | Tìm role name trong `testCaseName` / `preConditions` / `step` |
| `statusTransitions` | Tìm from/to status trong `testCaseName` / `step` / `expectedResult` |

In gap report ra STDOUT:
```
🔍 Gap Analysis:
- ☐ field "Tên SLA" → chỉ có 12/18 min cases
- ☐ enableDisableRule "Button Lưu disable khi..." → chưa có test case
- ☐ errorMessage "Tên SLA đã tồn tại" → chưa có test trigger
- ☐ permission "role Viewer" → chưa có test case
```

Nếu không có gap → in `✓ Gap Analysis: No gaps found`.

## Bước 4: Auto-fill ALL gaps

Sinh test cases cho TẤT CẢ gaps được phát hiện ở Bước 3. Append vào array đã đọc.

Với mỗi gap case:
- `testCaseName` = mô tả rõ ràng gap được fill (từ mindmap nếu có, hoặc tạo dựa theo inventory item)
- `summary` = giống hệt `testCaseName`
- `result` = `"PENDING"`
- `externalId`, `testSuiteDetails`, `specTitle`, `documentId`, `estimatedDuration`, `note` = `""`
- `preConditions` = `preConditionsBase` từ `{TC_CONTEXT_FILE}`
- `step` = UI actions (KHÔNG dùng "Send API")
- `expectedResult` = UI state (KHÔNG dùng HTTP status codes)

## Bước 5: Áp dụng project rules

Đọc `{TC_CONTEXT_FILE}` để lấy catalogStyle (nếu chưa đọc).

Áp dụng TẤT CẢ rules từ `PROJECT_RULES` context:
- Kiểm tra section assignment đúng chưa
- Kiểm tra writing style phù hợp chưa
- Kiểm tra bất kỳ custom rule nào được định nghĩa trong PROJECT_RULES
- Đảm bảo KHÔNG có HTTP status codes trong bất kỳ expectedResult nào
- Đảm bảo KHÔNG có "Send API" trong bất kỳ step nào

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
