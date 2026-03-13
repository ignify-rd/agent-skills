---
name: test-design-generator
description: Generate comprehensive test design documents (.md) and test cases from RSD and optional PTTK. Supports Frontend UI testing and API testing. Use when user says "generate test design", "create test cases", "RSD to mindmap", "sinh test", "tao test design", "tao mindmap", or uploads files for test generation.
---

# Test Design Generator

Generate comprehensive test design documents from RSD and optional PTTK documents.
Supports **Frontend UI testing** and **API testing** workflows.

## Overview

This skill reads requirement documents (RSD/PTTK) and generates structured test design mindmaps
in Markdown format. The output must match **100%** with the application's generation logic.

### Two Modes

| Mode | Input | Output Sections |
|------|-------|-----------------|
| **Frontend** | RSD + optional PTTK + optional images | 8 sections: screen name, giao diện chung, phân quyền, validate, lưới dữ liệu, phân trang, chức năng, timeout |
| **API** | RSD + optional PTTK | 3 sections: case common, validate, luồng chính |

## Instructions

### Step 1: Determine Mode and Collect Inputs

Auto-detect from context:

- **Frontend mode**: User mentions "frontend", "UI", "screen", "giao diện", "màn hình", or RSD describes a screen
- **API mode**: User mentions "API", "endpoint", "request/response", "backend", or RSD describes an API

**Required inputs:**
- RSD file (`.docx`, `.pdf`, `.txt`, `.md`)

**Optional inputs:**
- PTTK file — Technical design doc with detailed field specs
- Custom instructions — User's specific requirements (ALWAYS take priority)
- Images — UI screenshots/wireframes (Frontend mode only)
- DB Structure — Database schema (API mode only)
- API Endpoint — Exact endpoint path (API mode only)

### Step 2: Extract Structure from RSD

Read the RSD document thoroughly and extract a structured representation.

**For Frontend mode**, extract ALL fields matching the schema in `references/frontend-test-design.md` Phase 0.

**Screen type rules:**
- `LIST`: Has search filters + data grid + pagination
- `FORM`: Has editable input fields
- `POPUP`: Small dialog/popup
- `DETAIL`: Read-only view — all fields READ ONLY; extract `sections[]` and `buttonVisibilityRules[]`

**For API mode**, extract ALL fields matching the schema in `references/api-test-design.md`.

### Step 3: Enhance with PTTK (if provided)

If PTTK is provided, find the matching screen/API by name/breadcrumb/endpoint/fields overlap.

**CRITICAL source hierarchy:**

| Nội dung cần test | Nguồn chính | Nguồn bổ sung |
|---|---|---|
| **Validate field** (maxLength, required, format, type) | **PTTK** | RSD nếu PTTK không có |
| **Logic xử lý** (business rules, branching, DB operations) | **RSD** | — |
| **Error codes & messages** | **RSD** (bảng mã lỗi) | — |
| **DB mapping** (table, column, SQL) | **PTTK** | RSD nếu PTTK không có |
| **UI structure** (fields, buttons, layout) | **RSD** | Images, PTTK bổ sung |

**Quy tắc khi có PTTK:**
- PTTK data OVERRIDES RSD for field properties (maxLength, type, required, apiEndpoint, dbQuery)
- For API mode: when PTTK available → use ONLY PTTK fields for validate. RSD only for business logic.
- For Frontend mode: merge PTTK fields into RSD structure (PTTK wins on conflict)

### Step 4: Generate Test Design — Frontend Mode

Consult `references/frontend-test-design.md` for detailed phase instructions.
Consult `references/field-templates.md` for exact per-field test case templates.

**Output uses this exact base template:**

```markdown
# {SCREEN_NAME}

{COMMON_UI_SECTION}

{PERMISSION_SECTION}

## Kiểm tra validate

{VALIDATE_SECTION}

{GRID_SECTION}

{PAGINATION_SECTION}

{FUNCTION_SECTION}

{TIMEOUT_SECTION}
```

Each placeholder is filled by a specific generator — see `references/frontend-test-design.md`.

**For DETAIL screens:**
- Rename `## Kiểm tra validate` → `## Kiểm tra dữ liệu hiển thị`
- Skip `{GRID_SECTION}` (data already in validate section)
- Function section focuses on button visibility by status/role only

### Step 5: Generate Test Design — API Mode

Consult `references/api-test-design.md` for detailed instructions.

**Output uses this exact base template:**

```markdown
# {API_NAME}

## Kiểm tra các case common

### Method

#### Kiểm tra truyền sai method ({WRONG_METHODS})
- status: 107
- {
  "message": "Error retrieving AuthorInfo for token from TokenLib: Token is invalid signature"
  }

### URL

#### Kiểm tra truyền sai url
- status: 500
- {
  "message": "Access denied"
  }

### Kiểm tra phân quyền

#### Không có quyền
- status: 500
- {
  "message": "Access denied"
  }

#### Được phân quyền
- status: 200

## Kiểm tra validate

{VALIDATE_SECTION}

## Kiểm tra luồng chính

{MAIN_FLOW_SECTION}
```

**CRITICAL — Format Rules:**
- **KHÔNG** thêm blockquote header (` > **Endpoint:** ...`) — output bắt đầu ngay từ `# {API_NAME}`
- **KHÔNG** dùng `---` (horizontal rule) phân cách giữa các section hoặc field
- **Section common** dùng format đơn giản: `- status: 107` — **KHÔNG** dùng `1\. Check api trả về:` trong common
- Format `1\. Check api trả về:` / `1\.1. Status:` / `1\.2. Response:` **CHỈ** dùng trong section validate và luồng chính
- ALL validate responses use **Status: 200** regardless of valid/invalid data
- Invalid data returns error in response body: `{"message": "Dữ liệu không hợp lệ"}`
- Valid data returns success response body
- Wrong method → status: 107
- Wrong URL / no permission → status: 500

### Step 6: Apply Custom Instructions

If the user provided custom instructions, prepend as critical block:

```
📌 YÊU CẦU TÙY CHỈNH CỦA NGƯỜI DÙNG (ƯU TIÊN THỰC HIỆN):
[user's custom instructions]

→ Đọc kỹ yêu cầu trên và áp dụng. Yêu cầu này được ưu tiên hơn các hướng dẫn mặc định.
```

### Step 7: Verify + Supplement Cycle

After generating the test design, perform a verify+supplement cycle:

**Bước 7a — Re-read RSD and enumerate ALL logic branches:**
- Every if/else in "Logic nghiệp vụ" / "Logic xử lý"
- Every conditional field (required khi X, ẩn khi Y)
- Every DB validation (check tồn tại / không tồn tại)
- Every mode/task variation (create vs update vs delete)
- Every error code in bảng mã lỗi
- Every status transition
- Every field dependency / cascading rule
- Every button visibility rule by status/role (for DETAIL)

**Bước 7b — Cross-check with generated test cases:**
- ✅ Already has test case → skip
- ❌ Missing test case → generate and append
- ⚠️ Has test case but wrong expected result → mark as `[SỬA]` and replace

**Bước 7c — Quality check** (see `references/quality-rules.md`):
1. All names match RSD/PTTK exactly
2. No forbidden phrases
3. Each test case = 1 condition (atomic)
4. All values are specific (no placeholders)
5. Error messages verbatim from RSD
6. Output is 100% Vietnamese
7. Every RSD logic branch has ≥1 test case

Write the final markdown to a file.

## Important Rules

See `references/quality-rules.md` for the complete list. Key rules:

1. **100% Vietnamese output** — never translate field/button names
2. **Use exact names from RSD/PTTK** — never rename
3. **1 test case = 1 condition** — never combine
4. **Specific values only** — never use `[placeholder]`, `abc...`, `giá trị test`
5. **Status 200 for ALL validate** — error in response body, not HTTP status
6. **Only test what RSD mentions** — no guessing
7. **RSD scope is final** — PTTK/images only supplement, never add new features

## API Field Type Classification

When generating API validate test cases, classify each field:

| Field Type | How to detect from RSD | XSS/SQL Injection Response |
|-----------|----------------------|---------------------------|
| SEARCH_FIELD | RSD says "tìm kiếm gần đúng", "LIKE", "trim", "không phân biệt hoa/thường" | Status: 200 (treated as search text) |
| FILTER_FIELD | Optional string for filtering | Status: 200 with `{"message": "Dữ liệu không hợp lệ"}` |
| ENUM_FIELD | RSD specifies fixed values (e.g., "1: active, 0: inactive") | Status: 200 |
| INTEGER_REQUIRED | Type Integer, required=Y | Status: 200 with error message in body |

**Special character rules — MUST split into 2 test cases:**
- "Truyền {FieldName} là ký tự đặc biệt cho phép _" → Status: 200 (if RSD allows `_`)
- "Truyền {FieldName} là ký tự đặc biệt không cho phép" → Status: 200

## Examples

### Example 1: Frontend LIST Screen

User says: "Generate test design for this RSD" (uploads LIST screen RSD)

Result: 8-section markdown with per-field validate templates, grid with SQL per column, function with search tests per field + combined search.

### Example 2: API Test Design

User says: "Create API test from this RSD" (uploads API RSD)

Result: 3-section markdown. Common section has exact status codes (107/500/200). Validate section uses `1\.1. Status: 200` / `1\.2. Response:` format per field. Main flow has business logic with SQL queries.

### Example 3: Frontend DETAIL Screen

User says: "Generate test for this detail view RSD"

Result: Section renamed to "Kiểm tra dữ liệu hiển thị" (not "validate"). Per-field data display with SQL queries. Function section has only button visibility by status/role.

## Troubleshooting

### File cannot be read
Ask user to convert to `.txt` or `.md`, or paste content directly.

### Screen type unclear
Default to `LIST` if has input fields + data grid. Default to `FORM` if only editable fields. Default to `DETAIL` if all fields are read-only.

### Missing field properties
Use `null` — do NOT guess. If PTTK has the property, use PTTK value.
