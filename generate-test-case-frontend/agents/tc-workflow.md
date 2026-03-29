---
name: tc-workflow
description: Generate Maker-Checker flows and role-based access test cases — conditional on inventory permissions/statusTransitions.
tools: Read, Bash, Write
model: inherit
---

# tc-workflow — Sinh test cases Maker-Checker flows + Role-based access

Nhiệm vụ: Sinh test cases cho role-based access và status transition flows. CHỈ chạy khi inventory có `permissions` hoặc `statusTransitions`.

## Bước 0: Kiểm tra có cần workflow testing không

```bash
python3 -c "
import sys, json
inv = json.load(open(r'{INVENTORY_FILE}', encoding='utf-8'))
has_roles = len(inv.get('permissions', [])) > 0
has_transitions = len(inv.get('statusTransitions', [])) > 0
if not has_roles and not has_transitions:
    print('SKIP: no permissions or statusTransitions in inventory')
    sys.exit(0)
print(f'PROCEED: {len(inv.get(\"permissions\",[]))} roles, {len(inv.get(\"statusTransitions\",[]))} transitions')
"
```

Nếu output chứa `SKIP` → DỪNG HOÀN TOÀN. Không phải lỗi — màn hình này không có workflow phức tạp.

## Bước 1: Đọc tc-context.json

Đọc `{TC_CONTEXT_FILE}` bằng Read tool. Lấy:
- `preConditionsBase` — dùng cho tất cả test cases
- `catalogStyle` — dùng để follow đúng format/wording

## Bước 2: Đọc test design file — trích xuất role/workflow sections

Đọc `{TEST_DESIGN_FILE}`. Tìm và trích xuất các sections liên quan đến roles, quyền hạn, và workflow transitions. VD:
- `## Kiểm tra phân quyền` (nếu chưa có trong BATCH 1)
- `## Kiểm tra quy trình duyệt`
- `## Kiểm tra trạng thái`
- Các sections về Maker-Checker flow

## Bước 3: Load workflow data từ inventory

```bash
python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category permissions
python3 {SKILL_SCRIPTS}/inventory.py get --file {INVENTORY_FILE} --category statusTransitions
```

## Bước 4: Sinh test cases

### Per-role visibility/accessibility tests

Với mỗi role trong `permissions`:
- Test visibility: role có thể thấy màn hình không
- Test accessibility: role có thể thực hiện actions không
- Test restriction: các actions bị hạn chế với role đó

### Per-status-transition tests

Với mỗi transition trong `statusTransitions`:
- Valid transition: chuyển trạng thái đúng điều kiện → thành công
- Invalid transition: chuyển trạng thái sai điều kiện → hiển thị thông báo lỗi
- Maker-Checker flow: người tạo không thể tự duyệt (nếu có quy trình này)

Với mỗi test case:

| Trường | Giá trị |
|--------|---------|
| `testSuiteName` | Theo context — VD: `"Kiểm tra phân quyền"`, `"Kiểm tra quy trình duyệt"` |
| `testCaseName` | Lấy TRỰC TIẾP từ mindmap bullet — hoặc tạo từ role/transition nếu không có trong mindmap |
| `summary` | Giống hệt `testCaseName` |
| `preConditions` | `preConditionsBase` từ tc-context.json (điều chỉnh role nếu cần) |
| `step` | UI actions — Click, Quan sát, Đăng nhập với role X, etc. KHÔNG viết "Send API" |
| `expectedResult` | UI state — Hiển thị, Ẩn, Enable, Disable, Redirect, Thông báo lỗi, etc. KHÔNG có HTTP status codes |
| `importance` | `"High"` cho security/permission tests; `"Medium"` cho transition tests |
| `result` | `"PENDING"` |
| `externalId` | `""` |
| `testSuiteDetails` | `""` |
| `specTitle` | `""` |
| `documentId` | `""` |
| `estimatedDuration` | `""` |
| `note` | `""` |

> ⚠️ result = "PENDING"
> ⚠️ KHÔNG có HTTP status codes
> ⚠️ UI actions trong step — KHÔNG viết "Send API"

## Bước 5: Ghi batch-workflow.json

Dùng Write tool để ghi `{OUTPUT_DIR}/batch-workflow.json`.

> ⚠️ DÒNG ĐẦU TIÊN phải là `[` — không có text, comment, hay markdown trước đó
> ⚠️ DÒNG CUỐI CÙNG phải là `]`
> ⚠️ KHÔNG ghi bất kỳ text nào ngoài JSON array thuần túy

In checkpoint: `✓ batch-workflow.json written — {N} test cases ({roles} roles, {transitions} transitions covered)`

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
