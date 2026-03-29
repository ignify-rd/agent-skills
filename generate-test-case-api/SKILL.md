---
name: generate-test-case-api
description: Generate API test cases from RSD/PTTK (or mindmap) and output to test-cases.json. For API endpoints only. Use when user says "sinh test case api", "sinh test cases api", "generate api test case", "tạo test case api", or provides RSD/PTTK/.pdf documents or a mindmap file for an API endpoint.
---

# Test Case Generator — API Mode (Orchestrator)

Generate test cases for API endpoints from a test design file and inventory, by coordinating specialized sub-agents.

> **Scope**: API test cases only. Requires `test-design-api.md` and `inventory.json` produced by `generate-test-design-api`.

## When to Apply

- User says "sinh test case api", "sinh test cases api", "tạo test case api", "generate api test case"
- User provides a test design file (`test-design-api.md`) for an API endpoint

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## ⛔ ORCHESTRATOR KHÔNG ĐỌC test-design-api.md, inventory.json TRỰC TIẾP

**Orchestrator TUYỆT ĐỐI KHÔNG đọc nội dung file `test-design-api.md` hay `inventory.json` trực tiếp.** Orchestrator chỉ dùng các lệnh query để lấy fieldConstraints cho việc batch, và truyền file paths cho sub-agents.

> Nếu orchestrator tự đọc test-design-api.md hay inventory.json → vi phạm kiến trúc, gây context pollution, gây sai lệch output.

**Orchestrator được phép:**
- Chạy `python $SKILL_SCRIPTS/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints` để đếm và batch fields
- Chạy `python $SKILL_SCRIPTS/search.py --list --domain api` để list catalog files
- Đọc 2–3 catalog files (50 dòng đầu mỗi file) để lấy CATALOG_SAMPLE
- Kiểm tra file existence (sentinel, batch files)

**Orchestrator KHÔNG được phép:**
- Read `test-design-api.md` trực tiếp
- Read `inventory.json` trực tiếp (chỉ query qua inventory.py)

---

## Workflow — Orchestrator

### Step 0: Load AGENTS.md (Project Rules)

1. Check `catalog/` directory tại project root — nếu không có → hỏi user chạy `test-genie init`
2. Check & READ `AGENTS.md` tại project root → store toàn bộ nội dung làm `projectRules`
3. Nếu không có AGENTS.md → dùng skill-level defaults, thông báo user: "Project chưa có AGENTS.md. Đang dùng rules mặc định."

**⚠️ projectRules override tất cả skill defaults khi được định nghĩa rõ ràng.**

### Step 0b: Validate Required Inputs

**⚠️ STOP — Chờ user cung cấp đủ:**
- **Test design file path** (`test-design-api.md`) — bắt buộc
- **Inventory file path** (`inventory.json`) — bắt buộc
- **Output folder** — bắt buộc (VD: `feature-1/`)

NEVER scan folders hoặc đoán file paths. Nếu thiếu → hỏi:
> "Skill này yêu cầu file test design và inventory.json. Vui lòng chạy skill `generate-test-design-api` trước — nó sẽ tạo cả hai file. Sau đó cung cấp đường dẫn."

Sau khi nhận được inputs, set:
```
INVENTORY_FILE = <inventory-file-path>
TEST_DESIGN_FILE = <test-design-api.md path>
OUTPUT_DIR = <output-folder>
OUTPUT_FILE = <output-folder>/test-cases.json
```

### Step 1: Resolve SKILL_SCRIPTS và SKILL_AGENTS paths

```bash
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/generate-test-case-api/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
SKILL_AGENTS=$(find . -name "tc-context.md" -path "*/generate-test-case-api/agents/*" 2>/dev/null | head -1 | xargs -r dirname)
```

Fallback: kiểm tra `.claude/skills`, `.cursor/skills`, `.windsurf/skills`, hoặc global npm.

### Step 2: Catalog listing (CATALOG_SAMPLE)

List tất cả catalog files:
```bash
python $SKILL_SCRIPTS/search.py --list --domain api
```

Đọc **2–3 file đầu tiên** trong danh sách (KHÔNG chọn theo tên — chỉ lấy 2–3 file đầu):
```bash
# Dùng Read tool — đọc 50 dòng đầu mỗi file
# VD: Read("catalog/api/sample1.csv", limit=50)
```

Lưu `CATALOG_SAMPLE` = nội dung đã đọc — truyền cho sub-agents làm wording reference.

### Step 3: Spawn tc-context (sequential)

Đọc agent instructions:
```bash
cat $SKILL_AGENTS/tc-context.md
```

Spawn sub-agent với prompt = nội dung tc-context.md + context block:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {resolved SKILL_SCRIPTS path}
INVENTORY_FILE: {INVENTORY_FILE}
OUTPUT_DIR: {OUTPUT_DIR}
PROJECT_RULES: {projectRules nếu có, hoặc "none"}
===================
```

**Kết thúc Step 3 khi:** `{OUTPUT_DIR}/tc-context.json` tồn tại.

### Step 4: Spawn tc-common (sequential)

Đọc agent instructions:
```bash
cat $SKILL_AGENTS/tc-common.md
```

Spawn sub-agent với prompt = nội dung tc-common.md + context:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
TC_CONTEXT_FILE: {OUTPUT_DIR}/tc-context.json
TEST_DESIGN_FILE: {TEST_DESIGN_FILE}
OUTPUT_DIR: {OUTPUT_DIR}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

**Kết thúc Step 4 khi:** `{OUTPUT_DIR}/batch-1.json` tồn tại.

### Step 5a: Query inventory — batch fields cho tc-validate

```bash
python $SKILL_SCRIPTS/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints
```

Từ kết quả, nhóm fields thành batches tối đa **3 fields** mỗi batch:
- Batch 1: [F1, F2, F3]
- Batch 2: [F4, F5, F6]
- ...

### Step 5b: Spawn ALL tc-validate agents in PARALLEL (one per batch)

Với mỗi batch, đọc agent instructions:
```bash
cat $SKILL_AGENTS/tc-validate.md
```

Spawn sub-agent với prompt = nội dung tc-validate.md + context:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
TC_CONTEXT_FILE: {OUTPUT_DIR}/tc-context.json
TEST_DESIGN_FILE: {TEST_DESIGN_FILE}
INVENTORY_FILE: {INVENTORY_FILE}
OUTPUT_DIR: {OUTPUT_DIR}
BATCH_NUMBER: {N}
FIELD_BATCH: [{fieldName}, ...]
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

Mỗi sub-agent ghi vào `{OUTPUT_DIR}/validate-batch-{N}.json` riêng — KHÔNG ghi chung. Spawn TẤT CẢ batches song song.

**Sau khi TẤT CẢ batches hoàn thành — kiểm tra:**

```bash
python -c "
import sys, os, glob
output_dir = '{OUTPUT_DIR}'
batches = sorted(glob.glob(os.path.join(output_dir, 'validate-batch-*.json')))
if not batches:
    print('ERROR: no validate batches found')
    sys.exit(1)
print(f'Found {len(batches)} validate batch(es)')
for b in batches:
    print(f'  {os.path.basename(b)}: {os.path.getsize(b)} bytes')
"
```

Nếu exit 1 → re-spawn batch bị thiếu.

Sau khi tất cả batch files tồn tại → tạo sentinel:
```bash
python -c "open('{OUTPUT_DIR}/.tc-validate-done','w').write('done')"
```

---

> ⛔ **SEQUENTIAL BARRIER — BẮT BUỘC CHẠY LỆNH NÀY TRƯỚC KHI SPAWN Step 5c:**
>
> ```bash
> python -c "
> import sys, os
> sentinel = '{OUTPUT_DIR}/.tc-validate-done'
> if not os.path.exists(sentinel):
>     print('NOT READY: .tc-validate-done missing')
>     sys.exit(1)
> print('READY')
> "
> ```
>
> **Nếu in ra `NOT READY` → DỪNG HOÀN TOÀN. KHÔNG spawn Step 5c. Debug Step 5b trước.**
> **KHÔNG được skip bước kiểm tra này dù bất kỳ lý do gì.**

---

### Step 5c: Spawn tc-mainflow (sequential)

Đọc agent instructions:
```bash
cat $SKILL_AGENTS/tc-mainflow.md
```

Spawn sub-agent với prompt = nội dung tc-mainflow.md + context:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
TC_CONTEXT_FILE: {OUTPUT_DIR}/tc-context.json
TEST_DESIGN_FILE: {TEST_DESIGN_FILE}
INVENTORY_FILE: {INVENTORY_FILE}
OUTPUT_DIR: {OUTPUT_DIR}
OUTPUT_FILE: {OUTPUT_FILE}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

**Kết thúc Step 5c khi:** `{OUTPUT_DIR}/batch-3.json` tồn tại.

### Step 6: Spawn tc-verify (sequential)

Đọc agent instructions:
```bash
cat $SKILL_AGENTS/tc-verify.md
```

Spawn sub-agent với prompt = nội dung tc-verify.md + context:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
TC_CONTEXT_FILE: {OUTPUT_DIR}/tc-context.json
INVENTORY_FILE: {INVENTORY_FILE}
OUTPUT_DIR: {OUTPUT_DIR}
OUTPUT_FILE: {OUTPUT_FILE}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

**Kết thúc Step 6 khi:** `{OUTPUT_DIR}/test-cases.json` tồn tại.

### Step 7: Final Output

Thông báo user:
```
✅ Test cases hoàn thành: {OUTPUT_FILE}
📋 Inventory: {INVENTORY_FILE}
📝 Test design: {TEST_DESIGN_FILE}
```

Nếu cần upload lên Google Sheets:
```bash
python $SKILL_SCRIPTS/upload_gsheet.py <tên-test-case> --project-root .
```

---

## Project AGENTS.md Override

**Scope — what project `AGENTS.md` CAN override:**

| Category | Can override? |
|----------|--------------|
| Chat input / user request | **Always — HIGHEST PRIORITY** |
| `testAccount` | Yes |
| testSuiteName convention | Yes |
| Writing style (ngắn/dài, cách viết step) | Yes |
| Output JSON field names | No |
| Batch strategy (BATCH 1/2/3 split) | No |
| Field type dispatch table | No |
| Importance mapping | No |

## Project Structure

```
generate-test-case-api/
├── SKILL.md                      ← Orchestrator workflow (this file)
├── AGENTS.md                     ← Skill-level default rules
├── agents/
│   ├── tc-context.md             ← Load catalog style, build preConditionsBase
│   ├── tc-common.md              ← BATCH 1: common + permission cases
│   ├── tc-validate.md            ← BATCH 2: validate cases (per field batch)
│   ├── tc-mainflow.md            ← BATCH 3: main flow cases
│   └── tc-verify.md              ← Gap analysis, dedup, final output
├── references/
│   ├── api-test-case.md
│   ├── priority-rules.md
│   ├── output-format.md
│   └── quality-rules.md
├── scripts/
│   ├── search.py
│   ├── inventory.py
│   ├── merge_batches.py          ← Merge + dedup batch JSON files
│   ├── extract_structure.py
│   ├── upload_gsheet.py
│   └── ...
└── data/
    ├── templates/template.xlsx
    └── catalogs/
        ├── default/api/
        └── _template/api/
```

## Quick Reference — Batch File Naming

| Batch | File | Content |
|-------|------|---------|
| BATCH 1 | `batch-1.json` | Common + permission test cases |
| BATCH 2 | `validate-batch-1.json`, `validate-batch-2.json`, ... | Validate cases per field batch |
| BATCH 3 | `batch-3.json` | Main flow cases |
| Merged | `test-cases-merged.json` | After merge_batches.py |
| Final | `test-cases.json` | After gap fill + project rules |
