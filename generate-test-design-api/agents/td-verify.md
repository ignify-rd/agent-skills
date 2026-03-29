---
name: td-verify
description: Cross-section verification and gap fill for API test design. V1-V4 handled by td-validate; V6-V9 handled by td-mainflow. This agent covers gap analysis, V5 duplicate check, V9 global scan, V10 format check.
tools: Read, Bash, Edit
model: inherit
---

# td-verify — Cross-section verification và gap analysis

Nhiệm vụ: Gap fill + cross-section checks. **KHÔNG đọc toàn bộ OUTPUT_FILE vào context** — dùng Bash/Python để extract chỉ phần cần.

> **Phân công:** V1-V4 đã được td-validate checkpoint per-field. V6-V9 đã được td-mainflow self-check. td-verify chỉ chịu trách nhiệm: gap analysis, V5 duplicate, V9 global, V10 format.

## Bước 1 — Load verify rules

```bash
python3 {SKILL_SCRIPTS}/search.py --ref api-test-design --section "verify"
```

## Bước 2 — Gap Analysis (inventory vs output)

Đọc `{INVENTORY_FILE}`. Với MỖI item trong inventory, dùng Bash grep (không load file vào LLM context):

```bash
# Kiểm tra error code có trong output chưa
grep -c "LDH_SLA_020" "{OUTPUT_FILE}"

# Kiểm tra DB field có trong SQL chưa
grep -c "APPROVED_BY" "{OUTPUT_FILE}"

# Kiểm tra service rollback
grep -c "rollback" "{OUTPUT_FILE}"
```

Liệt kê gaps:
```
🔍 Gap Analysis:
☐ errorCode "LDH_SLA_025" [validate] → chưa có bullet
☐ dbField "APPROVED_BY" → chưa có trong SQL SELECT
☐ service "S3" rollback → chưa có bullet
```

Fill từng gap — thêm vào cuối section tương ứng với `### [SỬA]` prefix. Dùng Edit tool để append.

## Bước 3 — V5: Cross-section duplicate check

Chạy Python script — extract chỉ headings (không load content):

```python
import re

with open(r"{OUTPUT_FILE}", encoding="utf-8") as f:
    content = f.read()

validate_match = re.search(r'## Kiểm tra Validate(.*?)(?=## Kiểm tra chức năng|## Kiểm tra ngoại lệ|$)', content, re.DOTALL)
mainflow_match = re.search(r'## Kiểm tra chức năng(.*?)(?=## Kiểm tra ngoại lệ|$)', content, re.DOTALL)

def get_headings(text):
    return set(re.findall(r'^#{3,4}\s+(.+)$', text or '', re.MULTILINE))

validate_h = get_headings(validate_match.group(1) if validate_match else '')
mainflow_h = get_headings(mainflow_match.group(1) if mainflow_match else '')

duplicates = validate_h & mainflow_h
if duplicates:
    print(f"❌ V5 DUPLICATE ({len(duplicates)}):")
    for d in sorted(duplicates):
        print(f"  - {d}")
else:
    print(f"✅ V5: No duplicates ({len(validate_h)} validate, {len(mainflow_h)} mainflow headings)")
```

Nếu có duplicate → dùng Edit tool xóa khỏi `## Kiểm tra luồng chính` (field-level checks thuộc về validate).

## Bước 3b — V5b: Detect validate cases misplaced in mainflow

```python
import re

with open(r"{OUTPUT_FILE}", encoding="utf-8") as f:
    content = f.read()

mainflow_match = re.search(r'## Kiểm tra luồng chính(.*?)$', content, re.DOTALL)
if mainflow_match:
    mainflow = mainflow_match.group(1)
    # Patterns that indicate validate cases in mainflow
    suspicious_patterns = [
        r'### Kiểm tra .*(bỏ trống|để trống|thiếu trường|trường không bắt buộc)',
        r'### Kiểm tra .*(không hợp lệ|sai định dạng|sai kiểu)',
        r'### Kiểm tra .*(null|empty|rỗng)',
    ]
    found = []
    for pat in suspicious_patterns:
        matches = re.findall(pat, mainflow, re.IGNORECASE)
        found.extend(matches)
    if found:
        print(f"❌ V5b MISPLACED ({len(found)}) validate cases in mainflow:")
        for m in found:
            print(f"  - {m}")
    else:
        print("✅ V5b: No misplaced validate cases in mainflow")
```

Nếu có misplaced → dùng Edit tool xóa khỏi `## Kiểm tra luồng chính`.

## Bước 4 — V9: Global forbidden words scan

```bash
grep -n "hoặc\|và/hoặc\|có thể\|ví dụ:\|\[placeholder\]" "{OUTPUT_FILE}"
```

Nếu có kết quả → grep thêm context, dùng Edit tool sửa từng dòng.

## Bước 5 — V10: Structural check

```bash
# File phải bắt đầu bằng # API_NAME — không có ---, không có blockquote
head -5 "{OUTPUT_FILE}"

# Không có horizontal rules
grep -cn "^---$" "{OUTPUT_FILE}"
```

Nếu file bắt đầu sai → dùng Edit tool sửa header.

## Bước 6 — Self-check kết quả (in bắt buộc)

```
=== SELF-CHECK (td-verify) ===
[Gap]  Inventory items covered:         {filled}/{total} gaps fixed
[V5]   No duplicate validate↔main:      ✅/❌ ({N} duplicates)
[V5b]  No misplaced validate in main:   ✅/❌ ({N} cases removed)
[V9]   No forbidden words:              ✅/❌ ({N} occurrences)
[V10]  Format correct (# header):       ✅/❌
=== KẾT QUẢ: {N}/5 ===
```

## Output

`{OUTPUT_FILE}` đã được patch. In self-check results bắt buộc trước khi kết thúc.
