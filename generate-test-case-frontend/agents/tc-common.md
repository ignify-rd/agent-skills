---
name: tc-common
description: Generate BATCH 1 — UI/giao diện chung + phân quyền test cases for frontend screens.
tools: Read, Bash, Write
model: inherit
---

# tc-common — Sinh BATCH 1: Giao diện chung + Phân quyền

Nhiệm vụ: Sinh test cases cho các sections TRƯỚC `## Kiểm tra Validate` (giao diện chung, phân quyền, và các sections pre-validate tương tự). Ghi kết quả vào `batch-1.json`.

## Bước 1: Đọc tc-context.json

Đọc `{TC_CONTEXT_FILE}` bằng Read tool. Lấy:
- `preConditionsBase` — dùng cho tất cả test cases
- `catalogStyle` — dùng để follow đúng format/wording
- `screenType` — để xác định context màn hình

## Bước 2: Đọc test design file — trích xuất sections pre-validate

Đọc `{TEST_DESIGN_FILE}`. Tìm và trích xuất tất cả sections `##` TRƯỚC section `## Kiểm tra Validate` (hoặc `## Kiểm tra validate`).

Thông thường bao gồm:
- `## Kiểm tra giao diện chung`
- `## Kiểm tra phân quyền`
- Các sections tương tự khác xuất hiện trước validate

Với mỗi section, thu thập tất cả bullets `- Kiểm tra ...` — mỗi bullet = 1 test case cần sinh.

## Bước 3: Load rules

```bash
python3 {SKILL_SCRIPTS}/search.py --ref fe-test-case
```

## Bước 4: Sinh test cases cho từng section

Với mỗi section và mỗi bullet case trong test design:

| Trường | Giá trị |
|--------|---------|
| `testSuiteName` | Tên section (VD: `"Kiểm tra giao diện chung"`, `"Kiểm tra phân quyền"`) |
| `testCaseName` | Lấy TRỰC TIẾP từ bullet text trong mindmap — KHÔNG thêm prefix, KHÔNG thêm tên màn hình |
| `summary` | Giống hệt `testCaseName` |
| `preConditions` | `preConditionsBase` từ tc-context.json |
| `step` | Mô tả UI actions theo catalogStyle.stepExample — dùng động từ: Click, Nhập, Chọn, Quan sát, etc. |
| `expectedResult` | UI state theo catalogStyle.expectedResultExample — dùng: Hiển thị, Enable, Disable, Redirect, etc. KHÔNG dùng HTTP status codes |
| `importance` | `"Kiểm tra giao diện chung"` → `"Low"` ; `"Kiểm tra phân quyền"` → `"Medium"` |
| `result` | `"PENDING"` |
| `externalId` | `""` |
| `testSuiteDetails` | `""` |
| `specTitle` | `""` |
| `documentId` | `""` |
| `estimatedDuration` | `""` |
| `note` | `""` |

> ⚠️ testCaseName = lấy TRỰC TIẾP từ mindmap bullet text — KHÔNG thêm prefix
> ⚠️ summary = giống hệt testCaseName
> ⚠️ result = "PENDING" — KHÔNG để ""
> ⚠️ expectedResult = UI state (Hiển thị, Enable, Disable, Redirect...) — KHÔNG có HTTP status codes
> ⚠️ KHÔNG rút gọn cases — mỗi bullet trong mindmap phải có 1 test case tương ứng

## Bước 5: Per-section checkpoint (STDOUT ONLY)

Sau khi sinh xong mỗi section, in ra STDOUT:

```
✓ Section "{sectionName}": {N} cases generated
Missing cases vs mindmap: [list nếu thiếu] → APPEND immediately
```

Nếu thiếu cases → APPEND ngay trước khi qua section tiếp theo.

> ⚠️ Checkpoint chỉ được in ra STDOUT. TUYỆT ĐỐI KHÔNG ghi checkpoint text vào batch file.

## Bước 6: Ghi batch-1.json

Dùng Write tool để ghi `{OUTPUT_DIR}/batch-1.json`.

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
OUTPUT_DIR: {output-folder}
PROJECT_RULES: {content or "none"}
===================
```
