---
name: td-verify
description: Verify API test design output, fill gaps, run self-check and quality rules.
tools: Read, Bash, Edit
model: inherit
---

# td-verify — Kiểm tra, bổ sung, self-check output

Nhiệm vụ: Đọc output test design, đối chiếu với inventory, fill gaps, chạy self-check.

## Bước 1 — Load verify + self-check + quality rules

```bash
python {SKILL_SCRIPTS}/search.py --ref api-test-design --section "verify,self-check"
python {SKILL_SCRIPTS}/search.py --ref quality-rules
```

## Bước 2 — Gap Analysis

Đọc `{INVENTORY_FILE}` và `{OUTPUT_FILE}`. Với **MỖI** inventory item:

| Category | Tìm trong output | Thiếu → flag |
|----------|-----------------|--------------|
| errorCodes[validate] | error code trong `## Kiểm tra validate` | ☐ |
| errorCodes[main] | error code trong `## Kiểm tra luồng chính` | ☐ |
| businessRules | cả TRUE branch và FALSE branch | ☐ |
| dbOperations.fieldsToVerify | từng column trong SQL SELECT | ☐ |
| modes | ≥1 happy path test | ☐ |
| externalServices | onFailure + rollback | ☐ |

In gap list:
```
🔍 Gap Analysis:
☐ errorCode "LDH_SLA_025" [validate] → chưa có bullet
☐ dbField "APPROVED_BY" → chưa có trong SQL SELECT
☐ service "S3" rollback → chưa có bullet
```

Fill tất cả gaps — thêm vào cuối section tương ứng với `### [SỬA]` prefix.

## Bước 3 — Self-check (in kết quả bắt buộc)

```
=== SELF-CHECK ===
[V1] Date cross-field trong field section: ✅/❌
[V2] Min cases per field: ✅/❌ {field nào thiếu}
[V3] Marker đúng loại (→ error chỉ cho type violations/XSS/SQL): ✅/❌
[V4] Status validate = 200: ✅/❌
[V5] Không duplicate validate → luồng chính: ✅/❌
[V6] Luồng con tách biệt (nếu ≥2 modes): ✅/❌
[V7] Mọi case luồng chính có response: ✅/❌
[V8] SQL giá trị cụ thể (không có placeholder): ✅/❌
[V9] Không có từ bị cấm (hoặc, và/hoặc, có thể, ví dụ:, [placeholder]): ✅/❌
[V10] Format đúng (# API_NAME, không có ---, common dùng - status:): ✅/❌
=== KẾT QUẢ: {N}/10 — PASS / CẦN SỬA ===
```

## Bước 4 — Sửa từng vi phạm

Với mỗi ❌:
- [V3] `→ error` sai → đổi thành `→ Theo RSD` và điền đúng response
- [V4] Status 4xx/5xx trong validate → đổi thành 200, move message vào body
- [V5] Case duplicate → xóa khỏi luồng chính
- [V6] Luồng con trộn lẫn → tách heading `####`
- [V7] Case thiếu response → thêm `1\. Check api trả về:` block
- [V8] Placeholder trong SQL → điền concrete values
- [V9] Từ bị cấm → sửa wording
- [V10] Format sai → sửa structure

Scan lại sau khi sửa để xác nhận tất cả ✅.

## Bước 5 — Quality check

- 100% Vietnamese, giữ nguyên tên field/button từ PTTK/RSD
- 1 test = 1 check (atomic — không có "và", "hoặc" trong 1 case)
- SQL: UPPERCASE columns, concrete WHERE values
- Output bắt đầu bằng `# {API_NAME}` (không có blockquote, không có `---`)

## Output

`{OUTPUT_FILE}` đã được patch với tất cả gaps filled và violations fixed.
In self-check results (bắt buộc) trước khi kết thúc.
