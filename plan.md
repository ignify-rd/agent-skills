# Improvement Plan — test-case-generator & test-design-generator

> Based on code review session — 2026-03-24

---

## Context

Hai skills hiện tại (`test-case-generator`, `test-design-generator`) đã được cải tiến coverage logic (inventory gate, traceability matrix, batch checklist). Tuy nhiên phân tích kiến trúc phát hiện 5 rủi ro ảnh hưởng đến độ tin cậy khi agent sử dụng.

**Số liệu hiện tại:**

| Skill | Instruction lines | Token ước tính |
|-------|-----------------|----------------|
| test-case-generator | ~2,387 lines | ~30,000 tokens |
| test-design-generator | ~4,306 lines | ~54,000 tokens |

---

## Rủi ro đã xác định

| ID | Rủi ro | Mức độ |
|----|--------|--------|
| R1 | Attention dilution — rules ở cuối context bị LLM "quên" | Cao |
| R2 | Priority hierarchy 4 tầng gây conflict khi project AGENTS.md override một phần | Cao |
| R3 | `field-templates.md` 1,707 lines — quá lớn, dispatch dễ sai | Cao |
| R4 | BATCH 3 prompt inflation sau khi inject inventory | Trung bình |
| R5 | "Read ≠ Apply" — LLM đọc AGENTS.md nhưng không apply ở step sau | Trung bình |

---

## Các cải tiến đã làm (session 2026-03-24)

### test-case-generator
- [x] **Step 5d** — Inventory Verification Gate: báo cáo count cho user, hỏi nếu = 0
- [x] **BATCH 2** — Minimum case count per field type (Textbox ≥15, Combobox ≥15, ...)
- [x] **BATCH 3** — Inject inventory items cụ thể vào prompt thay vì instruction chung chung
- [x] **Step 6b** — Frontend Traceability Matrix (tương đương API matrix)
- [x] **Coverage Report** — Bắt buộc hiển thị `📊 Coverage Report` cho user
- [x] **api-test-case.md** — Thêm checklist 6 kỹ thuật cuối BATCH 3
- [x] **fe-test-case.md** — Thêm min case count table + BATCH 3 checklist

### test-design-generator
- [x] **Step 4d** — Inventory Verification Gate (API + Frontend mode)
- [x] **API Main Flow** — Inject inventory items vào generation instruction
- [x] **Frontend Function section** — Inject inventory items vào generation instruction
- [x] **Coverage Report (API)** — Bắt buộc hiển thị `📊 Coverage Report (API)`
- [x] **Coverage Report (Frontend)** — Bắt buộc hiển thị `📊 Coverage Report (Frontend)`

---

## Việc cần làm tiếp theo

### P0 — Tách API và Frontend thành 2 skill riêng

**Mục tiêu:** Giảm instruction load 40% mỗi invocation, loại bỏ mode detection complexity.

**Áp dụng cho cả 2 skills:**

```
test-case-generator/
  → test-case-generator-api/        SKILL.md chỉ load api-test-case.md
  → test-case-generator-frontend/   SKILL.md chỉ load fe-test-case.md + field-templates.md

test-design-generator/
  → test-design-generator-api/      SKILL.md chỉ load api-test-design.md
  → test-design-generator-frontend/ SKILL.md chỉ load frontend-test-design.md + field-templates.md
```

**Trigger conditions mới (trong description):**
- API skill: "api", "endpoint", "POST /", "GET /", "PUT /", "DELETE /"
- Frontend skill: "màn hình", "screen", "giao diện", "frontend", "FE"

**Effort:** Cao (cần refactor SKILL.md + package.json + bin scripts)

---

### P0 — Giản lược Priority Hierarchy xuống 2 tầng

**Hiện tại (4 tầng — dễ gây confused):**
```
1. Project AGENTS.md
2. Skill AGENTS.md
3. References (*.md)
4. SKILL.md (lowest)
```

**Đề xuất (2 tầng — rõ ràng hơn):**
```
1. Project AGENTS.md → override bất kỳ default nào bên dưới
2. Skill defaults (AGENTS.md + references + SKILL.md gộp lại)
```

**Thay đổi cần làm:**
- Xóa mô tả 4-tầng trong SKILL.md của cả 2 skills
- Trong AGENTS.md: bỏ mục "Rule Override Hierarchy", thay bằng: "Nếu project AGENTS.md định nghĩa rule X → dùng X. Nếu không → dùng default bên dưới."
- Định nghĩa rõ **scope** project AGENTS.md có thể override:
  - CÓ THỂ override: `testAccount`, `testSuiteName convention`, `writing style`, `section assignment`
  - KHÔNG override: `batch strategy`, `output JSON format`, `field type dispatch table`

**Effort:** Thấp

---

### P1 — field-templates.md: Pre-generate skeleton thay vì LLM tự dispatch

**Vấn đề:** 1,707 lines template, LLM đọc rồi tự áp dụng → hay bị thiếu cases.

**Giải pháp:** Thêm script `generate_field_skeleton.py`:
1. Nhận input: list fields với type + constraints từ RSD
2. Output: skeleton mindmap với tất cả bullet items từ template đã fill sẵn
3. LLM chỉ cần điền: `{fieldName}`, `{maxLength}`, `{placeholder}`, `{apiEndpoint}`, enum values

```bash
python $SKILL_SCRIPTS/generate_field_skeleton.py \
  --field "Tên cấu hình SLA" --type textbox --maxLength 100 --required true
```

Output skeleton:
```markdown
### Kiểm tra textbox "Tên cấu hình SLA"
- Kiểm tra hiển thị mặc định → Luôn hiển thị và enable
- Kiểm tra giá trị mặc định → Mặc định rỗng
- Kiểm tra placeholder → Hiển thị placeholder "Nhập tên cấu hình SLA"
- Nhập 99 ký tự → Hệ thống cho phép nhập
- Nhập 100 ký tự → Hệ thống cho phép nhập
- Nhập 101 ký tự → Hiển thị cảnh báo "..."
...
```

LLM chỉ fill values, không cần "nhớ" toàn bộ template.

**Effort:** Trung bình (cần viết script mới)

---

### P2 — Coverage check per-batch thay vì cuối workflow

**Vấn đề:** Coverage check hiện tại ở Step 6b (cuối cùng) — context đã đầy, LLM ít chú ý hơn.

**Đề xuất:** Mini-check sau mỗi batch:

```
Sau BATCH 1: "Đã cover đủ N sections pre-validate chưa?"
Sau BATCH 2: "Mỗi field có ≥ min_cases chưa? List field nào thiếu."
Sau BATCH 3: "Đã cover đủ error codes/branches/DB tables chưa? List item nào thiếu."
```

Mỗi mini-check nhỏ hơn, context tươi hơn sau mỗi batch → accuracy cao hơn.

**Thay đổi cần làm:**
- Thêm "Post-batch checkpoint" vào mỗi BATCH definition trong SKILL.md
- Xóa / giản lược Step 6b (vì đã check per-batch)

**Effort:** Thấp

---

### P3 — Đơn giản hóa AGENTS.md override scope

**Vấn đề:** "Bất kỳ rule nào trong project AGENTS.md đều override skill defaults" — quá rộng, LLM không biết scope chính xác.

**Đề xuất:** Trong AGENTS.md, thêm bảng override scope:

```markdown
## Override Scope

| Category | Project AGENTS.md có thể override? |
|----------|-----------------------------------|
| testAccount | ✅ Có |
| testSuiteName convention | ✅ Có |
| writing style (ngắn/dài, cách viết step) | ✅ Có |
| section assignment (buttons vào section nào) | ✅ Có |
| output JSON field names | ❌ Không |
| batch strategy (BATCH 1/2/3 split) | ❌ Không |
| field type dispatch table | ❌ Không |
| importance mapping | ❌ Không |
```

**Effort:** Thấp

---

## Timeline đề xuất

```
Week 1:
  [P0] Giản lược Priority Hierarchy → 2 tầng
  [P2] Coverage check per-batch
  [P3] Override scope table trong AGENTS.md

Week 2-3:
  [P0] Tách API/Frontend thành skill riêng (test-case-generator trước)

Week 4:
  [P0] Tách API/Frontend cho test-design-generator
  [P1] Script generate_field_skeleton.py (prototype)

Week 5:
  [P1] Integrate skeleton script vào workflow
  Testing + catalog update
```

---

## Metrics để đo cải thiện

| Metric | Hiện tại (ước tính) | Target |
|--------|---------------------|--------|
| Error code coverage rate | ~60% | ≥90% |
| DB field coverage rate | ~50% | ≥85% |
| Branch coverage rate | ~55% | ≥85% |
| Frontend field min cases hit rate | ~40% | ≥80% |
| Instruction load per session | 30k–54k tokens | ≤20k tokens (sau tách skill) |
