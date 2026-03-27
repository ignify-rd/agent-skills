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

**Kết thúc Step 5a khi:** `{OUTPUT_FILE}` tồn tại và chứa `## Kiểm tra các case common`.

---

### Step 5b: Sub-agent — td-validate (Sinh validate, 1 sub-agent per batch)

Đọc `{INVENTORY_FILE}` để lấy tất cả `fieldConstraints[]`.
Nhóm fields thành batches tối đa 5 fields mỗi batch.

**Với MỖI batch [F1..F5], [F6..F10], ...:**

1. Xác định `FIELD_TYPES_NEEDED` = danh sách unique types trong batch
   - VD: `[slaVersionId:Long, effectiveDate:Date Required, description:String 500 Optional]` → `"validate-rules,Long,Date Required,String Optional"`

2. Đọc agent instructions:
```bash
cat $SKILL_AGENTS/td-validate.md
```

3. Spawn sub-agent với prompt = nội dung td-validate.md + context:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
INVENTORY_FILE: {path}
OUTPUT_FILE: {path}
BATCH_NUMBER: {N}
FIELD_BATCH: [{fieldName}:{type}:{required}:{maxLength}, ...]
FIELD_TYPES_NEEDED: "{comma-separated types for --section}"
CATALOG_SAMPLE: {wording snippet hoặc "none"}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

4. **Sau khi sub-agent kết thúc:** Kiểm tra output file có batch content không. Nếu có ❌ trong checkpoint → re-spawn với note "Batch {N} thiếu cases cho fields: [list]".

**Kết thúc Step 5b khi:** Tất cả batches hoàn thành và có `## Kiểm tra validate` trong output.

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

### Step 6: Sub-agent — td-verify (Verify + Gap-fill + Self-check)

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

**Kết thúc khi:** Self-check in ra 10/10 ✅ hoặc tất cả vi phạm đã được sửa.

---

### Step 7: Final Output

Thông báo user:
```
✅ Test design hoàn thành: {OUTPUT_FILE}
📋 Inventory: {INVENTORY_FILE}
```

Nếu có `### [SỬA]` trong output → thông báo số lượng items được tự động thêm/sửa.
