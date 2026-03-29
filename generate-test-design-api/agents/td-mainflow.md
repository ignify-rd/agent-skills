---
name: td-mainflow
description: Generate the main flow sections (Kiểm tra chức năng + Kiểm tra ngoại lệ) for API test design from inventory.
tools: Read, Bash, Edit, Write
model: inherit
---

# td-mainflow — Sinh sections "Kiểm tra chức năng" và "Kiểm tra ngoại lệ"

Nhiệm vụ: Sinh 2 sections cuối dựa trên inventory, append vào output file.

## Bước 0 — Kiểm tra barrier (BẮT BUỘC chạy trước mọi thứ)

**Chạy lệnh này NGAY ĐẦU TIÊN. Nếu exit 1 → DỪNG, không làm gì thêm.**

```bash
python3 -c "
import sys, os
output_file = r'{OUTPUT_FILE}'
output_dir = os.path.dirname(output_file)
sentinel = os.path.join(output_dir, '.td-validate-done')
errors = []
if not os.path.exists(sentinel):
    errors.append('.td-validate-done not found — merge_validate.py chua chay')
if not os.path.exists(output_file):
    errors.append('OUTPUT_FILE not found — td-common chua chay')
else:
    content = open(output_file, encoding='utf-8').read()
    if '## Kiem tra Validate' not in content and '## Ki\u1ec3m tra Validate' not in content:
        errors.append('## Kiem tra Validate missing — merge chua hoan thanh')
if errors:
    for e in errors: print('BARRIER FAIL:', e)
    sys.exit(1)
print('BARRIER OK')
"
```

Nếu in ra `BARRIER FAIL` → **DỪNG NGAY, báo lỗi cho orchestrator**. KHÔNG tiếp tục dù bất kỳ lý do gì.

## Bước 1 — Load main flow rules

```bash
python3 {SKILL_SCRIPTS}/search.py --ref api-test-design --section "main-flow"
```

## Bước 2 — Đọc inventory

Đọc `{INVENTORY_FILE}` — lấy TẤT CẢ categories:
- `modes[]` — danh sách luồng con
- `businessRules[]` — if/else branches
- `errorCodes[section="main"]` — DB lookup errors → đưa vào `## Kiểm tra ngoại lệ`
- `dbOperations[]` — tables + fieldsToVerify
- `externalServices[]` — external calls + rollback
- `statusTransitions[]` — valid/invalid transitions

## Bước 3 — Xác định luồng con (BẮT BUỘC)

Từ `modes[]`, liệt kê tất cả luồng con. Nếu ≥ 2 luồng → mỗi luồng có `####` heading riêng:

```markdown
#### Luồng lưu nháp
### Kiểm tra ...

#### Luồng gửi duyệt
### Kiểm tra ...
```

**TUYỆT ĐỐI KHÔNG trộn test cases của các luồng khác nhau.**

## Bước 4 — KHÔNG duplicate validate cases

- Lỗi đã có trong `## Kiểm tra Validate` → **KHÔNG viết lại**
- Bao gồm: empty, type mismatch, format sai, date constraint, cross-field, maxLength
- `## Kiểm tra chức năng` **CHỈ** test: happy path, DB state, business branches, external services
- `## Kiểm tra ngoại lệ` **CHỈ** test: error codes section="main" (DB lookup, workflow state, concurrency)

**Các pattern NGHIÊM CẤM trong chức năng:**
- `### Kiểm tra ... bỏ trống` — đây là validate
- `### Kiểm tra ... với giá trị hợp lệ / không hợp lệ` — đây là validate
- `### Kiểm tra ... khi thiếu trường X` — đây là validate
- Không có "Pre-conditions:" block
- Không có "Expected:" trailing text

## Bước 5 — Quy tắc format mỗi test case

```markdown
### Kiểm tra {mô tả ngắn gọn}

- 1. Check api trả về:
  1.1.Status: 200
  1.2.Response:
  {
      "code": "00",
      "data": {
          "slaVersionId": 10001,
          "status": "DRAFT"
      }
  }
  SQL:
  SELECT COL1, COL2, COL3
  FROM TABLE_NAME
  WHERE COL1 = concrete_value;
```

**Quy tắc bắt buộc:**
- Case bắt đầu NGAY bằng `- 1. Check api trả về:` — **KHÔNG có bullet `- Body:` hay `- Request:` hay bất kỳ bullet nào khác trước đó**
- `1.1.Status:` — KHÔNG có space sau dấu chấm
- JSON body: plain `{` không có backtick fence
- SQL: plain text sau `  SQL:`, không có backtick fence, indent 2 spaces
- KHÔNG có "Pre-conditions:" block
- KHÔNG có "Expected:" trailing text
- KHÔNG có `---` separator giữa các cases
- KHÔNG có `#### Luồng ...` heading ngay trước `### Kiểm tra` trong cùng một case — `####` chỉ dùng để nhóm nhiều cases lại, xuất hiện TRƯỚC block cases của luồng đó
- Concrete values trong SQL: `WHERE ID = 10001` — KHÔNG dùng placeholder

## Bước 6 — Sinh nội dung

### Section "Kiểm tra chức năng"

Sinh theo từng sub-section:

**Sub-A — Happy path theo modes:**
- Mỗi `modes[]` → ≥1 test case với data hợp lệ
- Response đầy đủ từ `responseSchema.success.sample`
- SQL: SELECT 100% `fieldsToVerify` từ `dbOperations`

**Sub-B — Business rules:**
- Mỗi `businessRules[]` → test TRUE branch + FALSE branch, mỗi branch response riêng

**Sub-C — External services:**
- Mỗi `externalServices[]` → test onSuccess + onFailure

### Section "Kiểm tra ngoại lệ"

- Mỗi `errorCodes[section="main"]` → 1 test case với exact message từ inventory
- Format đơn giản: `- Status: 500` hoặc response body tùy error type

## Bước 7 — Per-sub-section checkpoint (STDOUT only)

> ⚠️ **STDOUT ONLY — KHÔNG ghi vào OUTPUT_FILE.**

```
Sub-A: {N}/{N} modes ✓/✗
Sub-B: {N}/{N} business rules (TRUE+FALSE) ✓/✗
Sub-C: {N}/{N} external services ✓/✗
Ngoại lệ: {N}/{N} error codes [main] ✓/✗
Missing → THÊM ngay
```

## Bước 8 — Self-check trước khi append (MEMORY ONLY)

> ⚠️ **MEMORY ONLY — KHÔNG ghi vào OUTPUT_FILE.**

```
[V6] ≥2 modes → mỗi mode có #### heading riêng: ✅/❌
[V7] Mọi ### đều có "1. Check api trả về:" block: ✅/❌
[V8] SQL không có placeholder: ✅/❌
[V9] Không từ bị cấm (hoặc, và/hoặc, có thể, ví dụ:): ✅/❌
[VX] Không có Pre-conditions, Expected, backtick fences, ---: ✅/❌
```

Nếu có ❌ → SỬA trong memory trước khi sang Bước 9.

## Bước 9 — Append vào output

Append **CHỈ** test case content vào `{OUTPUT_FILE}`:

```markdown
## Kiểm tra chức năng

{Sub-A + Sub-B + Sub-C content}

## Kiểm tra ngoại lệ

{error codes content}
```

> ⚠️ **KHÔNG append:** Coverage report, checkpoint tables, separator `---`, hay bất kỳ text nào từ các bước trên.

In coverage report ra STDOUT:
```
📊 Coverage:
✓ Modes:          {N}/{N}
✓ Business rules: {N}/{N} (TRUE+FALSE)
✓ External svc:   {N}/{N}
✓ Error codes:    {N}/{N}
```
