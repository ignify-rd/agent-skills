---
name: generate-test-design-api
description: Generate API test design mindmap from RSD/PTTK. For API endpoints only. Use when user says "sinh test design api", "tao mindmap api", "tạo test design api", or provides RSD/PTTK for an API endpoint.
---

# Test Design Generator — API Mode (Orchestrator)

Generate test design documents (.md) for API endpoints bằng cách điều phối các sub-agents chuyên biệt.

> **Scope**: API test design (mindmap) only. NOT Frontend, NOT test case generation.

## When to Apply

- User provides RSD/PTTK for an API endpoint and asks to generate test design or mindmap
- User says "sinh test design api", "tạo test design api", "tao mindmap api"

## Prerequisites

Python 3 installed. Check: `python3 --version || python --version`

## Đọc file PDF — CHỈ dùng Read tool

Dùng Read tool với `pages` parameter cho file lớn. **CẤM TUYỆT ĐỐI** tạo script parse PDF.

---

## Workflow — Orchestrator

### Step 0: Validate Project Setup & Load Project Rules

1. Check `catalog/` at project root — nếu không có → hỏi user chạy `test-genie init`
2. Check & READ `AGENTS.md` at project root → store as `projectRules`
3. Nếu không có AGENTS.md → dùng skill-level defaults, thông báo user

**⚠️ projectRules override tất cả skill defaults.**

### Step 0b: Validate Required Inputs

**⚠️ STOP — Chờ user cung cấp đủ 3 thứ:**
- **RSD file path** — bắt buộc
- **PTTK file path** — tuỳ chọn
- **Output folder** — bắt buộc (VD: `feature-1/`)

NEVER scan folders hoặc đoán file paths. Nếu thiếu → hỏi.

### Step 1: Mode Detection (API Mode Only)

- Title matches `(GET|POST|PUT|DELETE|PATCH)\s+/` → High confidence → proceed
- Chứa `màn hình`, `screen`, `giao diện` → suggest `generate-test-design-frontend`
- Không rõ → hỏi user

### Step 2: Resolve Paths & Load Priority Rules

```bash
# Resolve SKILL_SCRIPTS
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/generate-test-design-api/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)

# Resolve SKILL_AGENTS
SKILL_AGENTS=$(find . -name "td-extract.md" -path "*/generate-test-design-api/agents/*" 2>/dev/null | head -1 | xargs -r dirname)
```

Nếu fail → tìm trong `.claude/skills`, `.cursor/skills`, `node_modules/test-genie/`.

```bash
python $SKILL_SCRIPTS/search.py --ref priority-rules
```

Xác định các paths dùng xuyên suốt:
- `INVENTORY_FILE` = `{output-folder}/inventory.json`
- `OUTPUT_FILE` = `{output-folder}/test-design-api.md`

### Step 3: Catalog Example

```bash
python $SKILL_SCRIPTS/search.py "{feature_keyword}" --domain api --full --top 1
```

Lưu `CATALOG_SAMPLE` (snippet wording + format) để truyền vào sub-agents. Catalog = nguồn WORDING cao nhất.

---

### Step 4: Sub-agent — td-extract (Trích xuất dữ liệu)

**Spawn sub-agent để extract RSD/PTTK và tạo inventory.**

Đọc agent instructions:
```bash
cat $SKILL_AGENTS/td-extract.md
```

Spawn sub-agent với prompt = nội dung td-extract.md + context block sau:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {resolved SKILL_SCRIPTS path}
INVENTORY_FILE: {INVENTORY_FILE}
RSD_FILE: {rsd file path}
PTTK_FILE: {pttk file path hoặc "none"}
API_NAME: {tên API từ RSD title}
METHOD: {HTTP method}
PROJECT_RULES: {projectRules nếu có, hoặc "none"}
===================
```

**Kết thúc Step 4 khi:** `{INVENTORY_FILE}` được tạo và summary không rỗng.

**Nếu errorCodes = 0:** Hỏi user trước khi tiếp tục.
**Nếu có conflicts PTTK/RSD:** Hỏi user để xác nhận.

---

### Step 5a: Sub-agent — td-common (Sinh common section)

Đọc agent instructions:
```bash
cat $SKILL_AGENTS/td-common.md
```

Spawn sub-agent với prompt = nội dung td-common.md + context:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
INVENTORY_FILE: {path}
OUTPUT_FILE: {path}
CATALOG_SAMPLE: {wording snippet từ Step 3, hoặc "none"}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

**Kết thúc Step 5a khi:** `{OUTPUT_FILE}` tồn tại và chứa `## Kiểm tra token`.

---

### Step 5b: Sub-agent — td-validate (Sinh validate, song song theo batch)

Đọc `{INVENTORY_FILE}` để lấy tất cả `fieldConstraints[]`.
Nhóm fields thành batches tối đa **3 fields** mỗi batch: Batch 1 [F1–F3], Batch 2 [F4–F6], ...
(Giới hạn 3 fields/batch để đảm bảo mỗi sub-agent có đủ context cho 100% template cases mỗi field.)

**Spawn TẤT CẢ batch sub-agents song song** — mỗi batch 1 sub-agent độc lập.

Với mỗi batch, đọc agent instructions:
```bash
cat $SKILL_AGENTS/td-validate.md
```

Spawn sub-agent với prompt = nội dung td-validate.md + context:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
INVENTORY_FILE: {path}
OUTPUT_DIR: {output-folder}
BATCH_NUMBER: {N}
FIELD_BATCH: [{fieldName}:{type}:{required}:{maxLength}, ...]
FIELD_TYPES_NEEDED: "{comma-separated types for --section}"
CATALOG_SAMPLE: {wording snippet hoặc "none"}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

⚠️ **Mỗi sub-agent ghi vào file riêng** `{output-folder}/validate-batch-{N}.md` — KHÔNG ghi vào output chung. Tránh race condition khi chạy song song.

**Sau khi TẤT CẢ batches hoàn thành — merge theo thứ tự:**

```python
import os

output_dir = "{output-folder}"
output_file = "{OUTPUT_FILE}"

# Collect batch files theo đúng thứ tự
batch_parts = []
n = 1
while os.path.exists(f"{output_dir}/validate-batch-{n}.md"):
    with open(f"{output_dir}/validate-batch-{n}.md", encoding="utf-8") as f:
        batch_parts.append(f.read().strip())
    n += 1

# Append validate section vào output
with open(output_file, "a", encoding="utf-8") as f:
    f.write("\n\n## Kiểm tra Validate\n\n")
    f.write("\n\n".join(batch_parts))

# Ghi sentinel để báo merge hoàn thành
with open(f"{output_dir}/.validate-done", "w") as f:
    f.write(f"merged {n-1} batches")

print(f"Merged {n-1} validate batches → {output_file}")
```

Nếu có ❌ trong batch checkpoint → re-spawn batch đó với note "Batch {N} thiếu cases cho fields: [list]".

**Kết thúc Step 5b khi:** File `{output-folder}/.validate-done` tồn tại VÀ `{OUTPUT_FILE}` chứa `## Kiểm tra validate`.

---

> ⛔ **SEQUENTIAL BARRIER — KHÔNG proceed Step 5c cho đến khi:**
> 1. File `{output-folder}/.validate-done` tồn tại
> 2. `{OUTPUT_FILE}` chứa `## Kiểm tra validate`
>
> Kiểm tra bằng lệnh:
> ```bash
> python -c "
> import sys
> done = open('{output-folder}/.validate-done').read()
> content = open('{OUTPUT_FILE}', encoding='utf-8').read()
> ok = '## Kiểm tra Validate' in content
> print('READY' if ok else 'NOT READY')
> sys.exit(0 if ok else 1)
> "
> ```
> Nếu in ra `NOT READY` → DỪNG, debug Step 5b trước.

---

### Step 5c: Sub-agent — td-mainflow (Sinh main flow)

Đọc agent instructions:
```bash
cat $SKILL_AGENTS/td-mainflow.md
```

Spawn sub-agent với prompt = nội dung td-mainflow.md + context:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
INVENTORY_FILE: {path}
OUTPUT_FILE: {path}
CATALOG_SAMPLE: {wording snippet hoặc "none"}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

**Kết thúc Step 5c khi:** `{OUTPUT_FILE}` chứa `## Kiểm tra luồng chính` và coverage report.

---

> ⛔ **SEQUENTIAL BARRIER — KHÔNG proceed Step 6 cho đến khi `{OUTPUT_FILE}` chứa đủ 3 sections:**
> ```bash
> python -c "
> import sys
> c = open('{OUTPUT_FILE}', encoding='utf-8').read()
> checks = ['## Kiểm tra token', '## Kiểm tra Validate', '## Kiểm tra luồng chính']
> missing = [s for s in checks if s not in c]
> print('READY' if not missing else f'MISSING: {missing}')
> sys.exit(0 if not missing else 1)
> "
> ```

---

### Step 6: Sub-agent — td-verify (Gap-fill + Cross-section check)

> V1-V4 đã được td-validate checkpoint per-field. V6-V9 đã được td-mainflow self-check.
> td-verify CHỈ làm: gap analysis, V5 duplicate, V9 global scan, V10 format.
> **KHÔNG đọc toàn bộ OUTPUT_FILE** — dùng grep/Python extract sections.

Đọc agent instructions:
```bash
cat $SKILL_AGENTS/td-verify.md
```

Spawn sub-agent với prompt = nội dung td-verify.md + context:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
INVENTORY_FILE: {path}
OUTPUT_FILE: {path}
===================
```

**Kết thúc khi:** Self-check in ra 4/4 ✅ hoặc tất cả gaps/vi phạm đã được sửa.

---

### Step 7: Final Output

Thông báo user:
```
✅ Test design hoàn thành: {OUTPUT_FILE}
📋 Inventory: {INVENTORY_FILE}
```

Nếu có `### [SỬA]` trong output → thông báo số lượng items được tự động thêm/sửa.
