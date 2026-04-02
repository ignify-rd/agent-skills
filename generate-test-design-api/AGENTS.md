# Test Design Generator — Agent Rules

Rules that override default behavior. Loaded automatically by AI agents.

> **Per-project override:** Projects can have their own `AGENTS.md` at the project root. If project `AGENTS.md` defines a rule → use that rule. If not → use the defaults here and in skill references.

## Override Scope

| Category | Project AGENTS.md can override? |
|----------|-------------------------------|
| Chat input / user request | **Always — HIGHEST PRIORITY** |
| testAccount | Yes |
| testSuiteName convention | Yes |
| Writing style (ngắn/dài, cách viết step) | Yes |
| Section assignment | Yes |
| Field type dispatch table (API validate) | No |

## ⚠️ How to Apply Project AGENTS.md

**This is CRITICAL — project AGENTS.md must be READ and APPLIED, not just checked for existence.**

1. At the start of generation (Step 0), **READ the entire project AGENTS.md file**
2. Extract ALL sections and rules — especially `## Project-Specific Rules`
3. Store as `projectRules` and apply throughout the entire workflow
4. Any rule in project AGENTS.md that is explicitly defined → apply that rule
5. Sections in project AGENTS.md not present here are **ADDED** (custom rules), not ignored

**Common project-level overrides:**
- Custom section assignment (e.g., "buttons go in function section, not validate")
- Writing style constraints (e.g., "viết ngắn gọn", "tách riêng từng case")
- Image analysis behavior (e.g., "analyze images before reading RSD")
- Custom field types beyond the 8 default templates
- Scope rules (e.g., "only generate for specified sections")

## Input Priority (PTTK vs RSD)

| Source | Priority | Field definitions / request body | Response body |
|--------|----------|----------------------------------|---------------|
| **PTTK** | **Highest** for field definitions | Field names, data types, required/optional, maxLength, format constraints, request body structure, API endpoints, DB mappings | **PTTK** — response body structure (field names, data types, nesting) |
| **RSD** | **Highest** for business logic | Main flow, error codes, if/else branches, screen flow, permissions | **RSD fallback** — nếu PTTK không có |

> **⚠️ Response body:** Khi PTTK có mô tả response body → dùng PTTK. Khi PTTK không có → dùng RSD. Tuyệt đối không dùng format mặc định cố định.

> **⚠️ Khi có PTTK → REPLACE hoàn toàn. KHÔNG dùng field/request/response từ RSD:**
> - PTTK **REPLACES** toàn bộ field definitions, request body, response body từ RSD
> - Field chỉ có trong RSD (không có trong PTTK) → **bỏ qua**, không dùng
> - Khi upload PTTK → bỏ qua TẤT CẢ field definitions từ RSD, dùng PTTK

## Extract Rules

### Phase 1: RSD → business logic only
Extract: title, endpoint, method, errorCodes, dbMapping (table, conditions, orderBy)

### Phase 2: PTTK → field definitions (if available)
Extract: inputFields (name, type, maxLength, required, validationRules), outputFields
- CHỈ dùng PTTK fields cho validate. RSD chỉ dùng hiểu business logic
- Data types chính xác từ PTTK (Date, Integer, Long, String)

### Fallback: no PTTK → extract everything from RSD

## Format Rules

- Common section: `- status: 107` — NEVER use `1\. Check api trả về:` in common
- Validate + Luồng chính: `- 1\. Check api trả về:` / `1\.1. Status:` / `1\.2. Response:`
- ALL validate responses use Status: 200 (errors in body, NOT 400/422/500)
- Output starts with `# {API_NAME}` — NO blockquote, NO `---` horizontal rules
- SQL: concrete values (`WHERE ID = 10001`), UPPERCASE columns, NO placeholders

## Temp File Rules

- **NEVER write temp/helper scripts to disk** (`_*.py`, `_*.ps1`, `_check_*.py`, etc.)
- For Python logic: use `python3 -X utf8 -c "..."` inline in Bash
- For file ops: use Read / Edit / Write tools directly
- Violation = architecture breach — all agents must follow this rule

## Quality Rules

- 100% Vietnamese, keep field/button names exactly as in RSD/PTTK
- No placeholders — use concrete sample values
- 1 test = 1 check (atomic)
- Forbidden: "và/hoặc", "hoặc", "có thể", "nên", "ví dụ:", "[placeholder]"
- Response body format comes from PTTK (no fixed format)

## R7: BASE + BOUNDARY MERGE (CRITICAL)

**⛔ ĐÂY LÀ RULE BẮT BUỘC — TUYỆT ĐỐI KHÔNG ĐƯỢC VI PHẠM.**

Base template cases và Boundary/Decimal rules TRÙNG LẶP nhau. **PHẢI MERGE** trước khi sinh cases.

**Quy trình bắt buộc (3 bước):**

1. **Thu thập base cases** từ template bảng
2. **Thu thập constraint cases** từ rsdConstraints (min, max, maxDecimalPlaces)
3. **MERGE loại bỏ overlap:**

| Base case | Trùng với constraint | Hành động |
|-----------|---------------------|-----------|
| "Số âm" (VD: -1) | min-1 | **MERGE** → dùng boundary case |
| "Số thập phân" (VD: 1.5) | maxDecimalPlaces | **MERGE** → dùng boundary case |
| "maxLength-1/max/max+1" | String maxLength | **MERGE** → dùng boundary case |
| "Số 0" | min=0 hoặc max=0 | **MERGE** → dùng boundary case |
| "Boolean", "XSS", "SQL", "Object", "Mảng" | Không trùng | GIỮ base case |
| MultipartFile: "Định dạng hợp lệ .xls" | allowedExtensions chỉ có .xlsx | **BỎ** case không áp dụng |
| MultipartFile: "Định dạng hợp lệ .xlsx" | allowedExtensions chỉ có .xls | **BỎ** case không áp dụng |
| MultipartFile: "Vượt dung lượng" | maxFileSizeMB = null | **BỎ** case không có constraint |
| MultipartFile: "Vượt số bản ghi" | maxRecords = null | **BỎ** case không có constraint |
| MultipartFile: trùng tên | allowDuplicate = true | **BỎ** case không báo lỗi trùng |

**Ví dụ min=0, max=100, maxDecimalPlaces=2 (warningYellowPct):**

```
❌ SAI — chưa MERGE:
   - "Số âm" → error  (test -1)          ← base
   - "Kiểm tra = -1" → error  (test -1)   ← boundary ← TRÙNG!
   - "Số thập phân" → error  (test 1.5)    ← base
   - "Kiểm tra = 1.5" → success (test 1.5) ← decimal ← TRÙNG!

✅ ĐÚNG — sau MERGE:
   - Boundary (MERGED): -1, 0, 100, 101
   - Decimal (MERGED): 1.5, 1.55, 1.555
   - Base (non-overlap): Boolean, XSS, SQL, Object, Mảng...
   = ~9-12 cases (thay vì 21+)
```

**⚠️ Number fields sau MERGE sẽ CÓ ÍT HƠN min_case_counts (≥18).** Đây là bình thường — min_case_counts là cap TỐI THIỂU (không thiếu), không phải target cố định.
