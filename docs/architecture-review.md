# Phan tich kien truc test-genie agent

> RD-941 - Architecture review cho test-design-generator va test-case-generator

---

## Kien truc hien tai

### test-design-generator

**Flow:**

1. **Step 0** - Validate project setup: kiem tra `catalog/` va `AGENTS.md` tai project root
2. **Step 1** - Detect mode: xac dinh API mode (RSD mo ta endpoint) hay Frontend mode (RSD mo ta UI screen)
3. **Step 2** - Load rules & references qua `search.py --ref`: priority-rules, api-test-design / frontend-test-design, field-templates, quality-rules
4. **Step 3** - Read top-matching example tu catalog: tim vi du thuc te theo keyword, doc full text
5. **Step 4** - Extract data tu RSD + PTTK (2-3 phases tuy mode):
   - API mode: Phase 1 (business logic tu RSD) + Phase 2 (field definitions tu PTTK)
   - Frontend mode: Phase 1 (image analysis) + Phase 2 (screen structure tu RSD) + Phase 3 (field definitions tu PTTK)
6. **Step 4b** - Validate & ask clarification neu thieu/mau thuan thong tin
7. **Step 5** - Generate test design sections:
   - Common section (hardcoded template)
   - Validate section (per-field, dung field templates)
   - Main flow section (LLM-generated)
   - Verify + supplement: LLM re-read RSD va cross-check coverage
8. **Step 6** - Apply quality rules + self-verify

**Dac diem chinh:**
- Catalog-based RAG: `search.py` tim vi du theo keyword, load full text vao context
- Rule hierarchy: project `AGENTS.md` > skill `AGENTS.md` > `references/*.md` > `SKILL.md`
- Self-verify: sau khi sinh, LLM re-read RSD va cross-check coverage

---

### test-case-generator

**Flow:**

1. **Step 0** - Validate project setup: kiem tra `catalog/`, `AGENTS.md`, `excel_template/template.xlsx`
2. **Step 1** - Check input type: neu khong co mindmap thi invoke `test-design-generator` truoc
3. **Step 2** - Detect mode: API vs Frontend dua vao mindmap content
4. **Step 3** - Load rules & examples qua `search.py --ref`
5. **Step 4** - Parse mindmap structure (headings -> test suites, bullets -> test cases)
6. **Step 5** - Extract field/body context tu PTTK/RSD
7. **Step 5b** - Validate & ask clarification
8. **Step 6** - Generate test cases theo 3 batches tuan tu:
   - Batch 1: Pre-validate sections (common, permissions)
   - Batch 2: Validate section, per-field sub-batch (moi field = 1 LLM call rieng)
   - Batch 3: Post-validate sections (grid, functionality)
9. **Step 7** - Output len Google Sheets qua 4 scripts Python:
   - `upload_template.py`: upload .xlsx -> Google Drive as new Sheets
   - `detect_template.py`: detect column structure dong (scan header row)
   - `upload_to_sheet.py`: write test case rows + formatting
   - Return URL

**Dac diem chinh:**
- Batch processing: chia mindmap thanh 3 lo xu ly tuan tu, tranh context overflow
- Validate batch dung per-field sub-batch (moi field = 1 LLM call rieng)
- Google Sheets integration qua Service Account credentials
- Column mapping hoan toan dynamic: `detect_template.py` scan header row, khong hardcode project type
- Moi lan chay tao spreadsheet MOI tren Google Drive, khong reuse file cu

---

## Phan tich hieu qua token

### Diem lang phi

| Van de | Mo ta | Uoc tinh |
|--------|-------|----------|
| Load toan bo references moi lan | Step 2 ca 2 skills load nhieu file `--ref` vao context (priority-rules, api/fe-test-case/design, output-format, quality-rules) - du co dung hay khong | 5-10k tokens/lan |
| Load full example tu catalog | Step 3 (test-design) doc full text file vi du dau tien - chu yeu de hoc format | 2-5k tokens |
| Self-verify step | Step 5 yeu cau LLM re-read toan bo RSD va cross-check - thuong khong phat hien loi sau | 1-2k tokens extra |
| Per-field sub-batch | Validate section goi LLM nhieu lan (1 lan/field), moi lan phai re-inject context (rules + request body) -> nhan so token voi so fields | Tang tuyen tinh theo field count |
| Clarification step lap | Step 4b/5b co the trigger nhieu cau hoi user - round-trip ton kem neu user phai tra loi tung cai | N/A |

### Diem phu thuoc nang vao LLM quality

| Buoc | Rui ro |
|------|--------|
| Detect mode (API vs Frontend) | Dua vao LLM doc mindmap/RSD va phan doan - khong co rule cung nao backup, de sai voi tai lieu mo ho |
| Extract tu RSD/PTTK | LLM phai parse tai lieu Word/PDF khong cau truc, nhan dien dung field name, type, required - de bo sot hoac nham voi doc lon |
| Main flow generation | LLM-generated hoan toan - khong co template cung - quality phu thuoc truc tiep vao model va context window |
| Self-verify | LLM tu verify output cua chinh minh - khong du independence de phat hien logic error sau |
| testSuiteName assignment | Dua vao catalog search + LLM judgment de chon dung ten suite - neu catalog thieu vi du thi fallback vao LLM guess |

---

## Huong cai thien de xuat

### 1. Lazy-load references theo mode

Thay vi load tat ca `--ref` ngay tu dau, chi load nhung file can thiet cho mode da detect.

- API mode: chi load `priority-rules`, `api-test-design`, `quality-rules`
- Frontend mode: chi load `priority-rules`, `frontend-test-design`, `field-templates`, `quality-rules`
- Tiet kiem 30-50% tokens o buoc load rules
- Ap dung cho ca `test-design-generator` va `test-case-generator`

### 2. Structured extraction thay vi free-form LLM parsing

Viet script Python nho de pre-parse RSD/PTTK (docx -> structured JSON: field list, endpoint, error codes). LLM nhan JSON thay vi raw document text.

- Giam rui ro extract sai voi tai lieu lon
- Giam context size (JSON compact hon full docx text)
- Lam ro rang ket qua extraction de de kiem tra

### 3. Rule-based mode detection

Them heuristic cung (regex) de detect API vs Frontend truoc khi de LLM phan doan.

Vi du: neu mindmap line 1 match `/^(GET|POST|PUT|DELETE)\s+\//` -> API mode. LLM chi can confirm khi heuristic khong chac.

- Giam rui ro detect sai voi tai lieu mo ho
- Nhanh hon, re hon mot LLM call

### 4. Gop per-field sub-batch thanh batch lon hon

Thay vi 1 LLM call / field, group 3-5 fields vao 1 call voi instruction ro rang.

- Giam so round-trip, giam tong overhead context
- Can dam bao instruction du ro de LLM khong lan fields

### 5. Tach self-verify thanh checklist cung

Thay vi "LLM re-read RSD", dua ra mot checklist co dinh (coverage matrix) ma LLM chi can tick. Vi du: [ ] error codes covered, [ ] all if/else branches tested, [ ] DB mapping verified.

- Nhanh hon (khong re-read toan bo RSD)
- De audit hon (checklist explicit)
- Phat hien van de duoc chu dong hon

### 6. Cache catalog search results

Neu cung keyword duoc search nhieu lan trong 1 session, cache ket qua de tranh re-scan catalog. Dac biet huu ich khi chay nhieu fields cung loai.

- Ap dung don gian nhat: in-memory dict trong `search.py`
- Hu ich nhat voi validate section (nhieu fields co cung domain keyword)

---

## Tong ket

Ca hai skills deu co kien truc tot: rule hierarchy ro rang, catalog-based RAG linh hoat, batch processing tranh context overflow. Cac diem can cai thien chu yeu la o hieu qua token (lazy-load references, gop per-field batch) va giam phu thuoc vao LLM judgment (rule-based mode detection, structured extraction, checklist verify). Nhung cai thien nay khong doi hoi thay doi kien truc tong the, chi can refine cac buoc hien co.
