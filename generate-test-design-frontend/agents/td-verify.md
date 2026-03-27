---
name: td-verify-frontend
description: Cross-section verification and gap fill for frontend test design. V3/V4 handled by td-validate; V6-V9 handled by td-function. This agent covers gap analysis, V5 duplicate check, V9 global scan, V10 format check.
tools: Read, Bash, Edit
model: inherit
---

# td-verify-frontend — Cross-section verification và gap analysis

Nhiệm vụ: Gap fill + cross-section checks. **KHÔNG đọc toàn bộ OUTPUT_FILE vào context** — dùng Bash/Python để extract chỉ phần cần.

> **Phân công:** V3/V4 đã được td-validate checkpoint per-field. V6-V9 đã được td-function self-check. td-verify chỉ chịu trách nhiệm: gap analysis, V5 duplicate, V9 global scan, V10 format.

## Bước 1 — Load verify rules

```bash
python {SKILL_SCRIPTS}/search.py --ref frontend-test-design --section "verify"
```

## Bước 2 — Gap Analysis (inventory vs output)

Đọc `{INVENTORY_FILE}`. Với MỖI item, dùng Bash grep (không load file vào LLM context):

```bash
# Kiểm tra businessRule có trong output chưa
grep -c "condition_keyword" "{OUTPUT_FILE}"

# Kiểm tra autoFillRule có test case chưa
grep -c "tenField_autofill" "{OUTPUT_FILE}"

# Kiểm tra errorMessage có bullet chưa
grep -c "text_loi" "{OUTPUT_FILE}"
```

Liệt kê gaps:
```
🔍 Gap Analysis:
☐ businessRule "BR1" (TRUE branch) → chưa có test case
☐ autoFillRule "maDichVu ← loaiDichVu" → chưa có bullet
☐ errorMessage "Tên không được để trống" → chưa có bullet
```

Fill từng gap — thêm vào cuối section tương ứng với `### [SỬA]` prefix.

## Bước 3 — V5: Cross-section duplicate check

Extract headings từ validate và function để so sánh (không load full content):

```python
import re

with open(r"{OUTPUT_FILE}", encoding="utf-8") as f:
    content = f.read()

validate_match = re.search(r'## Kiểm tra validate(.*?)(?=## Kiểm tra|$)', content, re.DOTALL)
function_match = re.search(r'## Kiểm tra chức năng(.*?)(?=## Kiểm tra|$)', content, re.DOTALL)

def get_headings(text):
    return set(re.findall(r'^#{3,4}\s+(.+)$', text or '', re.MULTILINE))

validate_h = get_headings(validate_match.group(1) if validate_match else '')
function_h = get_headings(function_match.group(1) if function_match else '')

duplicates = validate_h & function_h
if duplicates:
    print(f"❌ V5 DUPLICATE ({len(duplicates)}):")
    for d in sorted(duplicates):
        print(f"  - {d}")
else:
    print(f"✅ V5: No duplicates ({len(validate_h)} validate, {len(function_h)} function headings)")
```

Nếu có duplicate → dùng Edit tool xóa khỏi `## Kiểm tra chức năng`.

## Bước 4 — V9: Global forbidden words scan

```bash
grep -n "hoặc\|và/hoặc\|có thể\|ví dụ:\|\[placeholder\]\|nên\|thường" "{OUTPUT_FILE}"
```

Nếu có kết quả → dùng Edit tool sửa từng dòng.

## Bước 5 — V10: Structural check

```bash
# File phải bắt đầu bằng # SCREEN_NAME
head -3 "{OUTPUT_FILE}"

# Không có horizontal rules
grep -cn "^---$" "{OUTPUT_FILE}"
```

## Bước 6 — Self-check kết quả (in bắt buộc)

```
=== SELF-CHECK (td-verify-frontend) ===
[Gap] Inventory items covered:    {filled}/{total} gaps fixed
[V5]  No duplicate validate↔func: ✅/❌ ({N} duplicates)
[V9]  No forbidden words:         ✅/❌ ({N} occurrences)
[V10] Format correct (# header):  ✅/❌
=== KẾT QUẢ: {N}/4 ===
```

## Output

`{OUTPUT_FILE}` đã được patch. In self-check results bắt buộc trước khi kết thúc.
