---
name: generate-test-design-frontend
description: Generate Frontend test design mindmap from RSD/PTTK on Confluence. For UI screens only. Use when user says "sinh test design frontend", "sinh test design giao diện", "tao mindmap màn hình", or provides Confluence links to RSD/PTTK for a UI screen.
---

# Test Design Generator — Frontend Mode (Orchestrator)

Generate test design documents (.md) for Frontend UI screens bằng cách điều phối các sub-agents chuyên biệt.

> **Scope**: Frontend test design (mindmap) only. NOT API, NOT test case generation.

## When to Apply

- User provides RSD/PTTK for a UI screen and asks to generate test design or mindmap
- User says "sinh test design frontend", "sinh test design giao diện", "tạo test design màn hình"

## Prerequisites

Python 3 installed. Check: `python3 --version || python --version`

## Đọc tài liệu từ Confluence — dùng Atlassian MCP

Đọc nội dung RSD/PTTK từ Confluence bằng Atlassian MCP tools:
1. Resolve `cloudId` bằng `getConfluenceSpaces()`
2. Trích xuất `pageId` từ Confluence URL (pattern: `/pages/<pageId>/`)
3. Gọi `getConfluencePage(cloudId, pageId)` để lấy nội dung trang (markdown)
4. **CẤM TUYỆT ĐỐI** dùng WebFetch cho Confluence URL (yêu cầu authentication)

## ⛔ Temp File Rules

**CẤM TUYỆT ĐỐI** tạo file script tạm trên đĩa (`_*.py`, `_*.ps1`, `_check_*.py`, v.v.). Dùng `python3 -X utf8 -c "..."` inline trong Bash, hoặc dùng Read/Edit/Write tools trực tiếp.

---

## Workflow — Orchestrator

### Step 0: Validate Project Setup & Load Project Rules

1. Check `catalog/` at project root — nếu không có → hỏi user chạy `test-genie init`
2. Check & READ `AGENTS.md` at project root → store as `projectRules`
3. Nếu không có AGENTS.md → dùng skill-level defaults, thông báo user

**⚠️ projectRules override tất cả skill defaults.**

### Step 0b: Validate Required Inputs

**⚠️ STOP — Chờ user cung cấp đủ:**
- **RSD Confluence URL** — bắt buộc (VD: `https://your-site.atlassian.net/wiki/spaces/SPACE/pages/123456/RSD`)
- **PTTK Confluence URL** — tuỳ chọn
- **Output folder** — bắt buộc (VD: `feature-1/`)
- **Screen scope** — tuỳ chọn (VD: "chỉ generate US05.2")

NEVER guess URLs. Nếu thiếu → hỏi user cung cấp link Confluence.

### Step 1: Mode Detection (Frontend Mode Only)

- Chứa `màn hình`, `screen`, `giao diện`, `button`, `textbox`, `combobox` → High confidence → proceed
- Title matches `(GET|POST|PUT|DELETE|PATCH)\s+/` → suggest `generate-test-design-api`
- Không rõ → hỏi user

### Step 2: Resolve Paths & Load Priority Rules

```bash
# Resolve SKILL_SCRIPTS — dùng Python thay vì find (cross-platform)
SKILL_SCRIPTS=$(python3 -X utf8 -c "
import os, sys
skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '$(pwd)')))
for root, dirs, files in os.walk(skill_dir, topdown=True):
    depth = root.count(os.sep) - skill_dir.count(os.sep)
    if depth > 3:
        dirs[:] = []
        continue
    if 'search.py' in files and 'scripts' in root:
        print(os.path.dirname(root))
        break
" "$(pwd)/generate-test-design-frontend/scripts/search.py" 2>/dev/null || echo "generate-test-design-frontend/scripts")

# Resolve SKILL_AGENTS
SKILL_AGENTS=$(python3 -X utf8 -c "
import os, sys
skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '$(pwd)')))
for root, dirs, files in os.walk(skill_dir, topdown=True):
    depth = root.count(os.sep) - skill_dir.count(os.sep)
    if depth > 3:
        dirs[:] = []
        continue
    if 'td-extract.md' in files and 'agents' in root:
        print(root)
        break
" "$(pwd)/generate-test-design-frontend/agents/td-extract.md" 2>/dev/null || echo "generate-test-design-frontend/agents")
```

Fallback paths: `.claude/skills/generate-test-design-frontend`, `.cursor/skills/generate-test-design-frontend`, `node_modules/generate-test-design-frontend`.

```bash
python3 $SKILL_SCRIPTS/search.py --ref priority-rules
```

Xác định các paths dùng xuyên suốt:
- `INVENTORY_FILE` = `{output-folder}/inventory.json`
- `OUTPUT_FILE` = `{output-folder}/test-design-frontend.md`
- `OUTPUT_DIR` = `{output-folder}`

### Step 3: Catalog Example

Liệt kê tất cả catalog files:
```bash
python3 $SKILL_SCRIPTS/search.py --list --domain frontend
```

Đọc **tối đa 3 file** có chức năng gần nhất với màn hình đang generate (dựa theo tên file + title):
```bash
# Đọc từng file bằng Read tool — KHÔNG dùng search.py để tìm
# VD: Read("catalog/frontend/Screen_Ten_man_hinh.md", limit=80)
```

Chọn catalog phù hợp nhất (cùng screen type LIST/FORM/DETAIL, cùng domain, hoặc cấu trúc tương tự). Nếu không có file nào phù hợp → đọc file đầu tiên trong danh sách.

**Trích xuất CATALOG_SAMPLE:** Dùng Read tool để đọc **50 dòng đầu + 50 dòng cuối** của file được chọn. Nếu file < 100 dòng → đọc toàn bộ. In nội dung ra cho sub-agents dùng.

Catalog = nguồn WORDING cao nhất. Luôn dùng CATALOG_SAMPLE (từ Step 3) cho sub-agents, KHÔNG dùng template mặc định.

---

### Step 4: Sub-agent — td-extract (Trích xuất dữ liệu)

**Spawn sub-agent để extract RSD/PTTK/images và tạo inventory.**

Đọc agent instructions:
```bash
cat $SKILL_AGENTS/td-extract.md
```

Spawn sub-agent với prompt = nội dung td-extract.md + context block sau:

```
=== TASK CONTEXT ===
SKILL_SCRIPTS: {resolved SKILL_SCRIPTS path}
INVENTORY_FILE: {INVENTORY_FILE}
OUTPUT_DIR: {OUTPUT_DIR}
CLOUD_ID: {cloudId từ Atlassian MCP}
RSD_PAGE_ID: {pageId trích từ RSD Confluence URL}
PTTK_PAGE_ID: {pageId trích từ PTTK Confluence URL hoặc "none"}
SCREEN_NAME: {tên màn hình từ RSD title}
SCREEN_TYPE: {LIST|FORM|POPUP|DETAIL — xác định sơ bộ từ RSD}
PROJECT_RULES: {projectRules nếu có, hoặc "none"}
===================
```

**Trước Step 4:** Resolve cloudId bằng `getConfluenceSpaces()` và trích xuất pageId từ Confluence URLs (pattern: `/pages/<pageId>/`).

**Kết thúc Step 4 khi:** `{INVENTORY_FILE}` được tạo và `fieldConstraints` không rỗng.

**Nếu fieldConstraints = 0:** Hỏi user trước khi tiếp tục.
**Nếu có conflicts PTTK/RSD:** Hỏi user để xác nhận.

---

### Step 5a: Sub-agent — td-common (Sinh common UI + permissions)

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

**Kết thúc Step 5a khi:** `{OUTPUT_FILE}` tồn tại và chứa `## Kiểm tra giao diện chung`.

---

### Step 5b: Sub-agent — td-validate (Sinh validate, song song theo batch)

Đọc `{INVENTORY_FILE}` để lấy tất cả `fieldConstraints[]`.
Nhóm fields thành batches tối đa **3 fields** mỗi batch.

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
FIELD_TYPES_NEEDED: "{comma-separated section names for --section}"
CATALOG_SAMPLE: {wording snippet hoặc "none"}
PROJECT_RULES: {projectRules hoặc "none"}
===================
```

⚠️ **Mỗi sub-agent ghi vào file riêng** `{output-folder}/validate-batch-{N}.md`.

**Sau khi TẤT CẢ batches hoàn thành — merge bằng script:**

```bash
python3 $SKILL_SCRIPTS/merge_validate.py \
  --output-dir {output-folder} \
  --output-file {OUTPUT_FILE}
```

Script tự động strip garbage headers và tạo sentinel `.td-validate-done`.
Nếu exit 1 → đọc error, re-spawn batch bị lỗi.

**Kết thúc Step 5b khi:** File `{output-folder}/.td-validate-done` tồn tại VÀ `{OUTPUT_FILE}` chứa `## Kiểm tra Validate`.

---

> ⛔ **SEQUENTIAL BARRIER — BẮT BUỘC CHẠY LỆNH NÀY TRƯỚC KHI SPAWN Step 5c:**
>
> ```bash
> python3 -X utf8 -c "
> import sys, os
> sentinel = '{output-folder}/.td-validate-done'
> output = '{OUTPUT_FILE}'
> if not os.path.exists(sentinel):
>     print('NOT READY: .td-validate-done missing')
>     sys.exit(1)
> content = open(output, encoding='utf-8').read()
> if '## Kiểm tra Validate' not in content:
>     print('NOT READY: ## Kiểm tra Validate missing from output')
>     sys.exit(1)
> print('READY')
> "
> ```
>
> **Nếu in ra `NOT READY` → DỪNG HOÀN TOÀN. KHÔNG spawn Step 5c. Debug Step 5b trước.**

---

### Step 5c: Sub-agent — td-mainflow (Sinh grid + function + timeout)

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

**Kết thúc Step 5c khi:** `{OUTPUT_FILE}` chứa `## Kiểm tra chức năng` và coverage report.

---

> ⛔ **SEQUENTIAL BARRIER — BẮT BUỘC CHẠY LỆNH NÀY TRƯỚC KHI SPAWN Step 6:**
>
> ```bash
> python3 -X utf8 -c "
> import sys
> c = open('{OUTPUT_FILE}', encoding='utf-8').read()
> required = ['## Kiểm tra giao diện chung', '## Kiểm tra phân quyền',
>             '## Kiểm tra Validate', '## Kiểm tra chức năng']
> missing = [s for s in required if s not in c]
> print('READY' if not missing else 'NOT READY: MISSING: ' + str(missing))
> sys.exit(0 if not missing else 1)
> "
> ```
>
> **Nếu in ra `NOT READY` → DỪNG HOÀN TOÀN. KHÔNG spawn Step 6. Debug bước thiếu trước.**

---

### Step 6: Sub-agent — td-verify (Gap-fill + Cross-section check)

> V3/V4 đã được td-validate checkpoint per-field. V6-V9 đã được td-mainflow self-check.
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

