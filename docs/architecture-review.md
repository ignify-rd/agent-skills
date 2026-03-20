# Phân tích kiến trúc test-genie agent

> RD-941 - Architecture review cho test-design-generator và test-case-generator

---

## Kiến trúc hiện tại

### test-design-generator

**Flow:**

1. **Step 0** - Validate project setup: kiểm tra `catalog/` và `AGENTS.md` tại project root
2. **Step 1** - Detect mode: xác định API mode (RSD mô tả endpoint) hay Frontend mode (RSD mô tả UI screen)
3. **Step 2** - Load rules & references qua `search.py --ref`: priority-rules, api-test-design / frontend-test-design, field-templates, quality-rules
4. **Step 3** - Read top-matching example từ catalog: tìm ví dụ thực tế theo keyword, đọc full text
5. **Step 4** - Extract data từ RSD + PTTK (2-3 phases tùy mode):
   - API mode: Phase 1 (business logic từ RSD) + Phase 2 (field definitions từ PTTK)
   - Frontend mode: Phase 1 (image analysis) + Phase 2 (screen structure từ RSD) + Phase 3 (field definitions từ PTTK)
6. **Step 4b** - Validate & ask clarification nếu thiếu/mâu thuẫn thông tin
7. **Step 5** - Generate test design sections:
   - Common section (hardcoded template)
   - Validate section (per-field, dùng field templates)
   - Main flow section (LLM-generated)
   - Verify + supplement: LLM re-read RSD và cross-check coverage
8. **Step 6** - Apply quality rules + self-verify

**Đặc điểm chính:**
- Catalog-based RAG: `search.py` tìm ví dụ theo keyword, load full text vào context
- Rule hierarchy: project `AGENTS.md` > skill `AGENTS.md` > `references/*.md` > `SKILL.md`
- Self-verify: sau khi sinh, LLM re-read RSD và cross-check coverage

---

### test-case-generator

**Flow:**

1. **Step 0** - Validate project setup: kiểm tra `catalog/`, `AGENTS.md`, `excel_template/template.xlsx`
2. **Step 1** - Check input type: nếu không có mindmap thì invoke `test-design-generator` trước
3. **Step 2** - Detect mode: API vs Frontend dựa vào mindmap content
4. **Step 3** - Load rules & examples qua `search.py --ref`
5. **Step 4** - Parse mindmap structure (headings -> test suites, bullets -> test cases)
6. **Step 5** - Extract field/body context từ PTTK/RSD
7. **Step 5b** - Validate & ask clarification
8. **Step 6** - Generate test cases theo 3 batches tuần tự:
   - Batch 1: Pre-validate sections (common, permissions)
   - Batch 2: Validate section, per-field sub-batch (mỗi field = 1 LLM call riêng)
   - Batch 3: Post-validate sections (grid, functionality)
9. **Step 7** - Output lên Google Sheets qua 4 scripts Python:
   - `upload_template.py`: upload .xlsx -> Google Drive as new Sheets
   - `detect_template.py`: detect column structure động (scan header row)
   - `upload_to_sheet.py`: write test case rows + formatting
   - Return URL

**Đặc điểm chính:**
- Batch processing: chia mindmap thành 3 lô xử lý tuần tự, tránh context overflow
- Validate batch dùng per-field sub-batch (mỗi field = 1 LLM call riêng)
- Google Sheets integration qua Service Account credentials
- Column mapping hoàn toàn dynamic: `detect_template.py` scan header row, không hardcode project type
- Mỗi lần chạy tạo spreadsheet mới trên Google Drive, không reuse file cũ

---

## Phân tích hiệu quả token

### Điểm lãng phí

| Vấn đề | Mô tả | Ước tính |
|--------|-------|----------|
| Load toàn bộ references mỗi lần | Step 2 cả 2 skills load nhiều file `--ref` vào context (priority-rules, api/fe-test-case/design, output-format, quality-rules) - dù có dùng hay không | 5-10k tokens/lần |
| Load full example từ catalog | Step 3 (test-design) đọc full text file ví dụ đầu tiên - chủ yếu để học format | 2-5k tokens |
| Self-verify step | Step 5 yêu cầu LLM re-read toàn bộ RSD và cross-check - thường không phát hiện được lỗi sâu | 1-2k tokens extra |
| Per-field sub-batch | Validate section gọi LLM nhiều lần (1 lần/field), mỗi lần phải re-inject context (rules + request body) -> nhân số token với số fields | Tăng tuyến tính theo field count |
| Clarification step lặp | Step 4b/5b có thể trigger nhiều câu hỏi user - round-trip tốn kém nếu user phải trả lời từng cái | N/A |

### Điểm phụ thuộc nặng vào LLM quality

| Bước | Rủi ro |
|------|--------|
| Detect mode (API vs Frontend) | Dựa vào LLM đọc mindmap/RSD và phán đoán - không có rule cứng nào backup, dễ sai với tài liệu mơ hồ |
| Extract từ RSD/PTTK | LLM phải parse tài liệu Word/PDF không cấu trúc, nhận diện đúng field name, type, required - rất dễ bỏ sót hoặc nhầm với doc lớn |
| Main flow generation | LLM-generated hoàn toàn - không có template cứng - quality phụ thuộc trực tiếp vào model và context window |
| Self-verify | LLM tự verify output của chính mình - không đủ independence để phát hiện logic error sâu |
| testSuiteName assignment | Dựa vào catalog search + LLM judgment để chọn đúng tên suite - nếu catalog thiếu ví dụ thì fallback vào LLM guess |

---

## Hướng cải thiện đề xuất

### 1. Lazy-load references theo mode

Thay vì load tất cả `--ref` ngay từ đầu, chỉ load những file cần thiết cho mode đã detect.

- API mode: chỉ load `priority-rules`, `api-test-design`, `quality-rules`
- Frontend mode: chỉ load `priority-rules`, `frontend-test-design`, `field-templates`, `quality-rules`
- Tiết kiệm 30-50% tokens ở bước load rules
- Áp dụng cho cả `test-design-generator` và `test-case-generator`

### 2. Structured extraction thay vì free-form LLM parsing

Viết script Python nhỏ để pre-parse RSD/PTTK (docx -> structured JSON: field list, endpoint, error codes). LLM nhận JSON thay vì raw document text.

- Giảm rủi ro extract sai với tài liệu lớn
- Giảm context size (JSON compact hơn full docx text)
- Làm rõ ràng kết quả extraction để dễ kiểm tra

### 3. Rule-based mode detection

Thêm heuristic cứng (regex) để detect API vs Frontend trước khi để LLM phán đoán.

Ví dụ: nếu mindmap line 1 match `/^(GET|POST|PUT|DELETE)\s+\//` -> API mode. LLM chỉ cần confirm khi heuristic không chắc.

- Giảm rủi ro detect sai với tài liệu mơ hồ
- Nhanh hơn, rẻ hơn một LLM call

### 4. Gộp per-field sub-batch thành batch lớn hơn

Thay vì 1 LLM call / field, group 3-5 fields vào 1 call với instruction rõ ràng.

- Giảm số round-trip, giảm tổng overhead context
- Cần đảm bảo instruction đủ rõ để LLM không lẫn fields

### 5. Tách self-verify thành checklist cứng

Thay vì "LLM re-read RSD", đưa ra một checklist cố định (coverage matrix) mà LLM chỉ cần tick. Ví dụ: [ ] error codes covered, [ ] all if/else branches tested, [ ] DB mapping verified.

- Nhanh hơn (không re-read toàn bộ RSD)
- Dễ audit hơn (checklist explicit)
- Phát hiện vấn đề được chủ động hơn

### 6. Cache catalog search results

Nếu cùng keyword được search nhiều lần trong 1 session, cache kết quả để tránh re-scan catalog. Đặc biệt hữu ích khi chạy nhiều fields cùng loại.

- Áp dụng đơn giản nhất: in-memory dict trong `search.py`
- Hữu ích nhất với validate section (nhiều fields có cùng domain keyword)

---

## Tổng kết

Cả hai skills đều có kiến trúc tốt: rule hierarchy rõ ràng, catalog-based RAG linh hoạt, batch processing tránh context overflow. Các điểm cần cải thiện chủ yếu là ở hiệu quả token (lazy-load references, gộp per-field batch) và giảm phụ thuộc vào LLM judgment (rule-based mode detection, structured extraction, checklist verify). Những cải thiện này không đòi hỏi thay đổi kiến trúc tổng thể, chỉ cần refine các bước hiện có.
