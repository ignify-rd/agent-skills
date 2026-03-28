---
name: tc-common
description: Generate BATCH 1 — common and permission test cases (Kiểm tra token, Kiểm tra Endpoint & Method).
tools: Read, Bash, Write
model: inherit
---

# tc-common — Sinh BATCH 1: Common + Permission test cases

Nhiệm vụ: Sinh test cases cho các sections TRƯỚC `## Kiểm tra Validate` (thường là "Kiểm tra token" và "Kiểm tra Endpoint & Method"). Ghi kết quả vào `batch-1.json`.

## Bước 1: Đọc tc-context.json

Đọc `{TC_CONTEXT_FILE}` bằng Read tool. Lấy:
- `preConditionsBase` — dùng cho tất cả test cases
- `catalogStyle` — dùng để follow đúng format
- `testAccount`
- `apiName`, `apiEndpoint`

## Bước 2: Đọc test design file

Đọc `{TEST_DESIGN_FILE}`. Trích xuất tất cả sections `##` **TRƯỚC** `## Kiểm tra Validate`.

Thường gồm:
- `## Kiểm tra token`
- `## Kiểm tra Endpoint & Method`

Mỗi `###` sub-heading bên trong = 1 test case cần sinh.

## Bước 3: Load rules

```bash
python {SKILL_SCRIPTS}/search.py --ref api-test-case
```

## Bước 4: Sinh test cases

Với mỗi section `##` (TRƯỚC validate), sinh test cases cho tất cả `###` sub-headings:

| Trường | Giá trị |
|--------|---------|
| `testSuiteName` | Tên section `##` (theo catalogStyle convention) |
| `testCaseName` | `"{Category}_{Mô tả}"` (theo catalogStyle.testCaseNameFormat) |
| `summary` | Giống hệt `testCaseName` |
| `preConditions` | `preConditionsBase` từ tc-context.json |
| `step` | Mô tả hành động cụ thể cho case này (theo catalogStyle.stepExample) |
| `expectedResult` | Kết quả mong đợi từ bullet trong test design (theo catalogStyle.expectedResultExample) |
| `importance` | `"Low"` (cho "Kiểm tra token" và "Kiểm tra Endpoint & Method") |
| `result` | `"PENDING"` |
| `externalId` | `""` |
| `testSuiteDetails` | `""` |
| `specTitle` | `""` |
| `documentId` | `""` |
| `estimatedDuration` | `""` |
| `note` | `""` |

> ⚠️ `result` = `"PENDING"` — KHÔNG để `""`
> ⚠️ `summary` = giống hệt `testCaseName` — KHÔNG viết khác

## Bước 5: Per-section checkpoint (STDOUT ONLY)

Sau khi sinh xong mỗi section, in ra STDOUT (KHÔNG ghi vào batch file):

```
✓ Section {tên section}: {N} cases generated
Missing expected cases: [list nếu thiếu] → APPEND immediately
```

Nếu thiếu cases → APPEND ngay trước khi qua section tiếp theo.

## Bước 6: Ghi batch-1.json

Dùng Write tool để ghi `{OUTPUT_DIR}/batch-1.json`.

> ⚠️ DÒNG ĐẦU TIÊN của file PHẢI là `[` — không có text, comment, hay markdown trước đó
> ⚠️ DÒNG CUỐI CÙNG PHẢI là `]`
> ⚠️ Chỉ ghi JSON array thuần túy — KHÔNG ghi checkpoint text, comment, hay bất kỳ nội dung nào khác

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
