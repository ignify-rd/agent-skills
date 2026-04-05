---
name: rsd-to-pttk
description: Generate PTTK (Phân tích thiết kế kỹ thuật) from RSD on Confluence/Jira and auto-publish to Confluence, returning the page URL. Use this skill whenever the user wants to: create PTTK from RSD, viết PTTK từ RSD, sinh PTTK, generate technical design document, convert requirement to technical design, lấy RSD từ Jira/Confluence và tạo PTTK, đẩy PTTK lên Confluence, or mentions phrases like "tạo PTTK", "viết PTTK", "sinh PTTK", "PTTK từ RSD". Always use this skill when PTTK generation is mentioned — do not attempt this workflow without it.
---

# RSD → PTTK Generator

Skill tự động hóa: **đọc RSD từ Confluence → phân tích → sinh PTTK kỹ thuật → đẩy lên Confluence → trả về link**.

Dùng MCP tools của Atlassian plugin (không cần Python scripts).

---

## Inputs cần thu thập

Hỏi user nếu chưa cung cấp:

| Input | Mô tả | Ví dụ |
|-------|-------|-------|
| `rsd_url` | URL Confluence page của RSD (tổng quan hoặc chi tiết UC) | `https://bidv-vn.atlassian.net/wiki/spaces/PS0112025/pages/...` |
| `parent_page_url` | URL trang Confluence cha để tạo PTTK vào (tuỳ chọn) | Trang PTTK tổng thể |
| `scope` | `"uc"` = 1 UC, `"full"` = toàn release (mặc định: `"uc"`) | `"uc"` |

---

## Quy trình thực hiện

### Bước 1 — Lấy cloudId

Trước khi gọi bất kỳ tool nào, cần lấy `cloudId` của site Atlassian:

```
getConfluenceSpaces(cloudId="")
```

Nếu trả về lỗi, thử:
```
getConfluenceSpaces()
```

Từ kết quả, tìm space có key `PS0112025` để xác nhận đúng site. Lưu `cloudId` để dùng cho các bước tiếp theo.

> Nếu user đã cung cấp URL dạng `https://bidv-vn.atlassian.net/...` thì cloudId thường được resolve tự động bởi plugin.

### Bước 2 — Fetch nội dung RSD

Trích xuất `pageId` từ URL (pattern: `/pages/<pageId>/`), sau đó:

```
getConfluencePage(
    cloudId="<cloudId>",
    pageId="<pageId-from-url>",
    contentFormat="markdown"
)
```

Nếu `scope = "full"` (RSD tổng quan với nhiều UC):
- Dùng CQL để tìm child pages:
```
searchConfluenceUsingCql(
    cloudId="<cloudId>",
    cql="parent = <pageId> AND type = page"
)
```
- Fetch từng child page quan trọng (RSD chi tiết từng UC)

Nếu user cung cấp Jira issue URL thay vì Confluence:
```
getJiraIssue(cloudId="<cloudId>", issueIdOrKey="PS0112025-XXX")
```
Tìm link Confluence trong description/attachments của issue.

### Bước 3 — Phân tích RSD và sinh PTTK

Đọc nội dung RSD đã fetch. Áp dụng 7 bước tư duy thiết kế để sinh PTTK:

**Bước 0 — Chuẩn hoá đầu vào**
- Xác định phạm vi UC: in-scope vs out-of-scope
- Liệt kê điểm RSD còn mở → ghi vào mục "Điểm cần xác nhận"
- Trích xuất: danh sách UC, phân quyền, NFR

**Bước 1 — Phân rã chức năng theo khối kỹ thuật**
Tạo ma trận traceability: `UC → API endpoint → DB table → Job → Role`
Nhóm theo: Frontend, Backend API, DB, Job/Batch, Integration

**Bước 2 — Thiết kế luồng kỹ thuật (Sequence)**
Với mỗi UC, vẽ sequence diagram dạng text/Mermaid:
```
UI → API Gateway → Service → DB → External System
```
Xác định: sync/async, retry/timeout, idempotency

**Bước 3 — Đặc tả API**
Với mỗi endpoint (mới hoặc sửa):
- Method + path, auth/authz, headers chuẩn (X-Request-Id, X-Channel-Id)
- Request schema (field, type, length, required)
- Response schema (success + error)
- Error codes: mã lỗi, message, HTTP status
- Logging: log gì, mask field nào

**Bước 4 — Thiết kế DB**
- ERD/logical model (entity, quan hệ)
- Physical: bảng, cột, datatype, PK/FK, index
- HIS table nếu cần lịch sử
- Migration/seed data nếu có

**Bước 5 — Thiết kế xử lý nghiệp vụ**
- Validation rules (cụ thể hoá từ RSD)
- Business rules & công thức tính
- Transaction boundary (commit/rollback)
- Pseudocode cho logic phức tạp

**Bước 6 — Áp NFR vào thiết kế**
- Performance SLA (tham chiếu trang hiệu năng dự án)
- Security: phân quyền role, audit trail, masking
- Logging/monitoring, data retention

Xem `references/pttk_template.md` để biết cấu trúc 10 mục đầy đủ của PTTK.

### Bước 4 — Tìm vị trí tạo PTTK trên Confluence

Nếu user cung cấp `parent_page_url`: trích xuất `parentId` từ URL.

Nếu không có: tìm trang PTTK phù hợp trong space PS0112025:
```
searchConfluenceUsingCql(
    cloudId="<cloudId>",
    cql="title ~ 'PTTK' AND space = 'PS0112025' AND type = page"
)
```
Đề xuất cho user chọn trang cha trước khi tạo.

Lấy `spaceId` (không phải space key):
```
getConfluenceSpaces(cloudId="<cloudId>")
```
Tìm record có `key = "PS0112025"`, lấy trường `id`.

### Bước 5 — Đẩy PTTK lên Confluence

```
createConfluencePage(
    cloudId="<cloudId>",
    spaceId="<spaceId>",
    title="PTTK <Tên UC/Feature>",
    body="<nội dung PTTK đã sinh — viết bằng markdown>",
    contentFormat="markdown",
    parentId="<parentId nếu có>"
)
```

Nếu trang đã tồn tại (tên trùng):
```
updateConfluencePage(
    cloudId="<cloudId>",
    pageId="<existing-page-id>",
    body="<nội dung mới>",
    contentFormat="markdown",
    versionMessage="Cập nhật PTTK từ RSD v<version>"
)
```

### Bước 6 — Báo kết quả cho user

```
✅ PTTK đã được tạo thành công!
📄 Tên: PTTK <Tên UC>
🔗 Link: https://bidv-vn.atlassian.net/wiki/spaces/PS0112025/pages/<page-id>/...
📝 Ghi chú: Có <N> điểm cần xác nhận với BA (xem mục "Điểm cần xác nhận")
```

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Xử lý |
|-----|-------------|-------|
| cloudId không resolve | Plugin chưa authenticated | Yêu cầu user chạy `/atlassian login` |
| 403 Forbidden | Không có quyền đọc/ghi page | Liên hệ admin Confluence |
| RSD quá ngắn/thiếu | RSD chưa đủ điều kiện thiết kế | Sinh PTTK best-effort, ghi rõ điểm còn mở |
| Page title trùng | PTTK đã được tạo trước | Hỏi user: update hay tạo bản mới? |

---

## Nguyên tắc quan trọng

- **Không block vì RSD không hoàn hảo** — sinh best-effort và ghi "Điểm cần xác nhận" rõ ràng
- **Mọi quyết định kỹ thuật phải trỏ về UC/requirement trong RSD** — giữ traceability
- **Ngôn ngữ:** tiếng Việt, thuật ngữ kỹ thuật (API, endpoint, DB) giữ tiếng Anh
- **Format:** ngày dd/MM/yyyy, tiền tệ VND, phân trang 20 bản ghi/trang (theo quy chuẩn dự án)
