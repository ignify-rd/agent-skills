---
name: generate-test-case-frontend
description: Generate Frontend test cases from RSD/PTTK (or mindmap) and output to test-cases.json. For UI screens only. Use when user says "sinh test case frontend", "sinh test case fe", "sinh test case giao diện", "generate frontend test case", "tạo test case màn hình", or provides RSD/PTTK/.pdf documents or a mindmap file for a UI screen.
---

# Test Case Generator — Frontend Mode (Orchestrator)

Generate test cases for UI screens from a test design file and inventory, by coordinating specialized sub-agents.

> **Scope**: Frontend UI test cases only. Requires `test-design-frontend.md` and `inventory.json` produced by `generate-test-design-frontend`.

## When to Apply

- User says "sinh test case frontend", "sinh test case fe", "sinh test case giao diện", "tạo test case màn hình", "generate frontend test case"
- User provides a test design file (`test-design-frontend.md`) for a UI screen

## Prerequisites

Python 3 installed. Check:
```bash
python3 --version || python --version
```

## ⛔ ORCHESTRATOR KHÔNG ĐỌC test-design-frontend.md, inventory.json TRỰC TIẾP

**Orchestrator TUYỆT ĐỐI KHÔNG đọc nội dung file `test-design-frontend.md` hay `inventory.json` trực tiếp.** Orchestrator chỉ dùng các lệnh query để lấy fieldConstraints cho việc batch, và truyền file paths cho sub-agents.

> Nếu orchestrator tự đọc test-design-frontend.md hay inventory.json → vi phạm kiến trúc, gây context pollution, gây sai lệch output.

**Orchestrator được phép:**
- Chạy `python $SKILL_SCRIPTS/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints` để đếm và batch fields
- Chạy `python $SKILL_SCRIPTS/inventory.py summary --file {INVENTORY_FILE}` để lấy screenType và summary
- Chạy `python $SKILL_SCRIPTS/search.py --list --domain frontend` để list catalog files
- Đọc 2–3 catalog files (50 dòng đầu mỗi file) để lấy CATALOG_SAMPLE
- Kiểm tra file existence (sentinel, batch files)

**Orchestrator KHÔNG được phép:**
- Read `test-design-frontend.md` trực tiếp
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
- **Test design file path** (`test-design-frontend.md`) — bắt buộc
- **Inventory file path** (`inventory.json`) — bắt buộc
- **Output folder** — bắt buộc (VD: `feature-1/`)

NEVER scan folders hoặc đoán file paths. Nếu thiếu → hỏi:
> "Skill này yêu cầu file test design và inventory.json. Vui lòng chạy skill `generate-test-design-frontend` trước — nó sẽ tạo cả hai file. Sau đó cung cấp đường dẫn."

Sau khi nhận được inputs, set:
```
INVENTORY_FILE = <inventory-file-path>
TEST_DESIGN_FILE = <test-design-frontend.md path>
OUTPUT_DIR = <output-folder>
OUTPUT_FILE = <output-folder>/test-cases.json
```

### Step 1: Resolve SKILL_SCRIPTS và SKILL_AGENTS paths

```bash
SKILL_SCRIPTS=$(find . -name "search.py" -path "*/generate-test-case-frontend/scripts/*" 2>/dev/null | head -1 | xargs -r dirname)
SKILL_AGENTS=$(find . -name "tc-context.md" -path "*/generate-test-case-frontend/agents/*" 2>/dev/null | head -1 | xargs -r dirname)
```

Fallback: kiểm tra `.claude/skills`, `.cursor/skills`, `.windsurf/skills`, hoặc global npm.

### Step 2: Catalog listing (CATALOG_SAMPLE)

List tất cả catalog files:
```bash
python $SKILL_SCRIPTS/search.py --list --domain frontend
```

Đọc **2–3 file đầu tiên** trong danh sách (KHÔNG chọn theo tên — chỉ lấy 2–3 file đầu):
```bash
# Dùng Read tool — đọc 50 dòng đầu mỗi file
# VD: Read("catalog/frontend/sample1.csv", limit=50)
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

### Step 5a: Query inventory — batch fields + detect screenType

```bash
python $SKILL_SCRIPTS/inventory.py get --file {INVENTORY_FILE} --category fieldConstraints
python $SKILL_SCRIPTS/inventory.py summary --file {INVENTORY_FILE}
```

Từ kết quả:
1. **Lấy screenType** từ summary (LIST | FORM | POPUP | DETAIL)
2. **Nhóm fields thành batches** tối đa **3 fields** mỗi batch:
   - Batch 1: [F1, F2, F3]
   - Batch 2: [F4, F5, F6]
   - ...
3. **Detect FIELD_TYPES_NEEDED per batch**: lấy `type` values từ fieldConstraints của từng field trong batch — dùng làm `FIELD_TYPES_NEEDED` cho tc-validate (comma-separated, VD: `"textbox,combobox"`)

### Step 5b: Spawn ALL tc-validate agents + tc-search IN PARALLEL

**Spawn TẤT CẢ batches tc-validate song song** — mỗi batch 1 sub-agent riêng biệt.

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
FIELD_BATCH: [{fieldName}:{fieldType}, ...]
FIELD_TYPES_NEEDED: "{comma-separated field types for --section}"
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

**Đồng thời — nếu screenType = LIST:** Cũng spawn tc-search song song:

```bash
cat $SKILL_AGENTS/tc-search.md
```

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
TC_CONTEXT_FILE: {OUTPUT_DIR}/tc-context.json
TEST_DESIGN_FILE: {TEST_DESIGN_FILE}
INVENTORY_FILE: {INVENTORY_FILE}
OUTPUT_DIR: {OUTPUT_DIR}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

Mỗi sub-agent ghi vào file riêng — KHÔNG ghi chung. Spawn TẤT CẢ song song.

**Sau khi TẤT CẢ parallel agents hoàn thành — kiểm tra:**

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

### Step 5c: Spawn tc-mainflow (sequential, after barrier)

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

### Step 5d: Spawn tc-workflow (sequential, conditional)

Kiểm tra xem inventory có permissions hoặc statusTransitions không:

```bash
python -c "
import json, sys
inv = json.load(open('{INVENTORY_FILE}', encoding='utf-8'))
if inv.get('permissions') or inv.get('statusTransitions'):
    print('SPAWN')
else:
    print('SKIP')
"
```

**Nếu kết quả là `SKIP`** → bỏ qua Step 5d, chuyển sang Step 6.

**Nếu kết quả là `SPAWN`** → đọc agent instructions và spawn:

```bash
cat $SKILL_AGENTS/tc-workflow.md
```

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {path}
TC_CONTEXT_FILE: {OUTPUT_DIR}/tc-context.json
TEST_DESIGN_FILE: {TEST_DESIGN_FILE}
INVENTORY_FILE: {INVENTORY_FILE}
OUTPUT_DIR: {OUTPUT_DIR}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

**Kết thúc Step 5d khi:** `{OUTPUT_DIR}/batch-workflow.json` tồn tại (hoặc skipped).

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
| Section assignment (buttons vào section nào) | Yes |
| Output JSON field names | No |
| Batch strategy (BATCH 1/2/3 split) | No |
| Field type dispatch table | No |
| Importance mapping | No |

## Project Structure

```
generate-test-case-frontend/
├── SKILL.md                         ← Orchestrator workflow (this file)
├── AGENTS.md                        ← Skill-level default rules
├── agents/
│   ├── tc-context.md                ← Load catalog style, build preConditionsBase
│   ├── tc-common.md                     ← BATCH 1: giao diện chung + phân quyền
│   ├── tc-search.md                 ← Search/filter/pagination (LIST screens only)
│   ├── tc-validate.md               ← BATCH 2: validate cases (per field batch)
│   ├── tc-mainflow.md               ← BATCH 3: button/action/function cases
│   ├── tc-workflow.md               ← Maker-Checker + role flows (conditional)
│   └── tc-verify.md                 ← Gap analysis, dedup, final output
├── references/
│   ├── fe-test-case.md
│   ├── field-templates.md
│   ├── priority-rules.md
│   ├── output-format.md
│   └── quality-rules.md
├── scripts/
│   ├── search.py
│   ├── inventory.py
│   ├── merge_batches.py             ← Merge + dedup batch JSON files
│   ├── extract_structure.py
│   ├── upload_gsheet.py
│   └── ...
└── data/
    ├── templates/template.xlsx
    └── catalogs/
        ├── default/frontend/        ← Frontend test case CSV examples
        └── _template/
            ├── frontend/            ← Template AGENTS.md
            └── references/          ← Reserved
```

## Quick Reference — Batch File Naming

| Batch | File | Content |
|-------|------|---------|
| BATCH 1 | `batch-1.json` | UI + permission test cases |
| BATCH search | `batch-search.json` | Search/filter/pagination (LIST screens only, optional) |
| BATCH 2 | `validate-batch-1.json`, `validate-batch-2.json`, ... | Validate cases per field batch |
| BATCH 3 | `batch-3.json` | Function + button cases |
| BATCH workflow | `batch-workflow.json` | Maker-Checker + role flows (optional) |
| Merged | `test-cases-merged.json` | After merge_batches.py |
| Final | `test-cases.json` | After gap fill + project rules |

## Quick Reference — Frontend testCaseName format

- **testCaseName = LẤY TRỰC TIẾP từ mindmap bullet** — KHÔNG thêm prefix, KHÔNG thêm screen name
- **testSuiteName:** theo catalog convention — field sub-suites (`"Textbox: Tên cấu hình SLA"`) hoặc fallback `"Kiểm tra validate"`

| Catalog convention | testSuiteName |
|-------------------|---------------|
| Field sub-suites | `"Textbox: Tên cấu hình SLA"` |
| No sub-suites | `"Kiểm tra validate"` |

Examples:
- Mindmap: `- Kiểm tra khi nhập 101 ký tự`
  → testCaseName: `Kiểm tra khi nhập 101 ký tự` (NO prefix)
- Mindmap: `### Kiểm tra điều hướng đến màn hình`
  → testCaseName: `Kiểm tra điều hướng đến màn hình`
