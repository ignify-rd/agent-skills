---
name: td-mainflow
description: Generate the main flow section (luồng chính) for API test design from inventory.
tools: Read, Bash, Edit, Write
model: inherit
---

# td-mainflow — Sinh section "Kiểm tra luồng chính"

Nhiệm vụ: Sinh main flow section dựa trên inventory, append vào output file.

## Bước 1 — Load main flow rules

```bash
python {SKILL_SCRIPTS}/search.py --ref api-test-design --section "main-flow"
```

## Bước 2 — Đọc inventory

Đọc `{INVENTORY_FILE}` — lấy TẤT CẢ categories:
- `modes[]` — danh sách luồng con
- `businessRules[]` — if/else branches
- `errorCodes[section="main"]` — DB lookup errors
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

Trước khi viết bất kỳ case nào, nhớ quy tắc:
- Lỗi đã có trong `## Kiểm tra validate` → **KHÔNG viết lại**
- Bao gồm: empty, type mismatch, format sai, date constraint, cross-field so sánh, maxLength
- Luồng chính **CHỈ** test: DB lookup errors, workflow state, external service failures, business branches

## Bước 5 — Sinh theo từng sub-section

**Sub-A — Response + DB:**
- List ALL output fields với sample values
- SQL đầy đủ: SELECT {100% fieldsToVerify từ dbOperations} FROM {table} WHERE {concrete value} ORDER BY ...
- Concrete values: `WHERE SLA_VERSION_ID = 101` — KHÔNG dùng placeholder

**Sub-B — Search scenarios (nếu là search API):**
- Tìm kiếm chính xác / gần đúng (LIKE) / không tồn tại
- Mỗi search field → ≥2 bullets (có kết quả + không có kết quả)

**Sub-C — Error codes + Business logic:**
- Mỗi `errorCodes[section="main"]` → 1 test case với **exact message từ inventory**
- Mỗi `businessRules[]` → test TRUE branch + FALSE branch, mỗi branch có response riêng

**Sub-D — Mode variations + Status transitions:**
- Mỗi `modes[]` → ≥1 happy path test
- Valid/invalid status transitions → test each

**Sub-E — External services + Rollback:**
- Mỗi `externalServices[]` → test onFailure + rollback không INSERT DB

## Bước 6 — Per-sub-section checkpoint

```
Sub-A: {N}/{N} dbFields in SQL, {N}/{N} output fields ✓/✗
Sub-B: {N}/{N} search fields ✓/✗
Sub-C: {N}/{N} error codes, {N}/{N} branches ✓/✗
Sub-D: {N}/{N} modes, {N}/{N} transitions ✓/✗
Sub-E: {N}/{N} services, {N}/{N} rollback ✓/✗
Missing → THÊM `### [SỬA]` ngay
```

## Quy tắc format mỗi test case

```markdown
### Kiểm tra {mô tả}
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        ...response body theo PTTK...
      }
      SQL:
      SELECT COL1, COL2, COL3
      FROM TABLE_NAME
      WHERE COL1 = 'concrete_value'
      ORDER BY COL2 ASC;
```

**TUYỆT ĐỐI KHÔNG** viết test case không có response.

## Bước 6b — Self-check trước khi append (BẮT BUỘC)

> ⚠️ **Xác nhận trong MEMORY ONLY — KHÔNG ghi bất kỳ dòng nào sau đây vào OUTPUT_FILE.**

Scan nội dung vừa sinh (trong memory, TRƯỚC khi ghi file):

```
[V6] ≥2 modes → mỗi mode có #### heading riêng: ✅/❌
[V7] Mọi ### Kiểm tra đều có "1\. Check api trả về:" block: ✅/❌
[V8] SQL không có placeholder ({...}, ..., <value>, ???): ✅/❌
[V9] Không từ bị cấm (hoặc, và/hoặc, có thể, ví dụ:, [placeholder]): ✅/❌
```

Nếu có ❌ → SỬA ngay trong memory trước khi sang Bước 7.

## Bước 7 — Append vào output + Coverage report

Append **CHỈ** nội dung sau vào `{OUTPUT_FILE}` (không có gì khác):
```markdown
## Kiểm tra luồng chính
{generated content}
```

> ⚠️ **KHÔNG append vào OUTPUT_FILE:** Coverage report, Self-check, bảng thống kê, separator `---`, hay bất kỳ text nào từ các bước checkpoint.

In coverage report ra STDOUT (không ghi vào file):
```
📊 Coverage Report (Main Flow):
✓ Error codes [main]: {N}/{N}
✓ Business rules:     {N}/{N} (TRUE+FALSE)
✓ DB fields in SQL:  {N}/{N}
✓ Modes:             {N}/{N}
✓ External services: {N}/{N}
```
