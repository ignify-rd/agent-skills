---
name: rsd-generator
description: Sinh tài liệu RSD (Requirement Specification Document) hoàn chỉnh và đăng lên Confluence từ URD, ảnh/link Figma, và các tài liệu tham chiếu. Hãy dùng skill này bất cứ khi nào user nhắc tới "tạo RSD", "viết RSD", "generate RSD", "RSD cho usecase", "làm tài liệu đặc tả", "draft spec từ URD + Figma", hoặc đưa link URD/Figma kèm yêu cầu tạo tài liệu đặc tả chức năng — kể cả khi user không gọi đúng tên "RSD". Skill biết template chuẩn của dự án (đặc tả usecase, sơ đồ luồng, ma trận phân quyền, mô tả màn hình, logic xử lý) và đăng kết quả lên Confluence trả về link page mới.
---

# RSD Generator

Sinh một tài liệu RSD (Requirement Specification Document) cấp chức năng theo template chuẩn của dự án, lấy đầu vào từ URD + ảnh/link Figma + các page Confluence liên quan, và upload thẳng lên Confluence.

## Khi nào dùng skill này

- User muốn tạo mới một RSD cho một màn hình / usecase / chức năng cụ thể (ví dụ "Danh sách thẻ tín dụng nội địa WEB", "Xem chi tiết giao dịch APP").
- User cung cấp các input dạng: link Confluence URD, link Figma, ảnh mockup, hoặc link tới các page Confluence khác (RSD cấp 1, bảng mã lỗi, trạng thái, RSD WEB tương ứng nếu đang làm APP...).
- User yêu cầu output là một page Confluence mới, kèm link tới page đó.

## Nguyên tắc cốt lõi (đọc kỹ trước khi làm)

RSD **không phải là sáng tác**. Nó là tài liệu có cấu trúc cố định, nội dung phải **truy nguồn** được từ input user cung cấp. Năm nguyên tắc:

0. **Publish luôn — không draft.** Output phải là tài liệu hoàn chỉnh, publish trực tiếp lên Confluence. Không tạo file draft local. Không ghi "Dự thảo" trong bảng Phiên bản tài liệu — dùng "Khởi tạo". Khai thác tối đa mọi resource user cung cấp trước khi hỏi thêm hay đánh dấu `[Cần xác nhận]`.

1. **Không bịa dữ liệu — nhưng phải khai thác hết resource trước.** Đọc kỹ toàn bộ URD, tất cả page Confluence tham chiếu, và Figma trước khi kết luận "thiếu thông tin". Chỉ dùng `[Cần xác nhận: ...]` cho những gì thực sự không có trong bất kỳ resource nào user đã cung cấp. Cuối tài liệu tổng hợp lại danh sách để user review.
2. **Ưu tiên tham chiếu hơn copy-paste.** Khi có page Confluence đã mô tả sẵn (RSD cấp 1, bảng trạng thái, API spec...), link sang đó thay vì paste lại. Các RSD APP thường chỉ viết Section 4 (mô tả màn hình) còn lại tham chiếu sang RSD WEB.
3. **Tuân thủ template Việt hoá — bao gồm cả format heading.** Toàn bộ heading, label bảng, từ khoá (Tác nhân, Luồng chính, Điều kiện trước, ...) phải khớp chính xác template. Đặc biệt:
   - **Heading chính (section 1–5)** phải dùng **setext-style** (tên section + dòng `---` bên dưới), KHÔNG dùng ATX-style (`##`). Ví dụ đúng:
     ```
     1. Đặc tả/Tóm tắt usecase
     ---------------------------
     ```
   - **Section 4** có format đặc biệt: `4**. Mô tả màn hình**` (số `4` không in đậm, tên mục in đậm).
   - **Bảng Section 4b** (mô tả màn hình): cột STT dùng **header rỗng** `|  |`, không viết `| **STT** |`.
   - **Heading phụ** (1.1, 1.2, 2.1, ...) dùng `###` là đúng — giữ nguyên.
4. **Tuyệt đối không dùng emoji/icon trong nội dung tài liệu.** Không được dùng bất kỳ emoji hay icon nào (✅ ❌ 🔘 🟡 🟢 🔴 ✏️ ▶ ✖ 📋 ⚠️ v.v.) trong nội dung bảng, mô tả màn hình, hay bất kỳ chỗ nào trong tài liệu RSD (trừ mục "Các điểm cần user xác nhận" ở cuối). Thay thế cụ thể:
   - Ma trận phân quyền: dùng **"x"** cho có quyền, để **trống ô** cho không có quyền
   - Trạng thái badge: viết text thuần (ví dụ: "Tạo nháp", "Chờ duyệt", "Hoạt động")
   - Tên nút chức năng: viết text không có icon (ví dụ: "Chỉnh sửa", "Phê duyệt", "Từ chối")

## Workflow end-to-end

Thực hiện tuần tự:

### Bước 1 — Gather & đọc hết inputs ngay lập tức

Xác định các input user đã cung cấp. Chỉ hỏi thêm những gì **bắt buộc và chưa có**:

| Input | Bắt buộc | Nếu thiếu |
|-------|----------|-----------|
| Tên chức năng + platform (WEB/APP/BO) | Có | Hỏi user |
| Space Confluence + Parent page ID | Có | Hỏi user |
| URD (link Confluence hoặc Jira issue) | Có | Hỏi user |
| Figma link hoặc ảnh mockup | Không | Bỏ qua phần ảnh, ghi chú chờ bổ sung |
| Page tham chiếu (RSD cấp 1, bảng trạng thái, RSD WEB...) | Không | Bỏ qua, tham chiếu khi có URL |
| Tên tác giả | Không | Dùng tên user hiện tại hoặc để trống |

**Đọc tất cả resource song song ngay sau khi có đủ input bắt buộc:**
- Từng page Confluence: `mcp__mcp-atlassian__confluence_get_page`. Page quá lớn → đọc theo chunks, grep heading trước.
- Jira issue: `mcp__mcp-atlassian__jira_get_issue` — đọc description + attachments + comments.
- Figma: `mcp__plugin_figma_figma__get_design_context` (element-level) + `get_screenshot` cho từng state (default, empty, error...). Parse URL: `figma.com/design/{fileKey}/...?node-id={nodeId}` — convert `-` thành `:` trong nodeId.
- Ảnh đính kèm trong Jira/Confluence: download về local nếu cần attach lên page mới.

### Bước 2 — Quyết định chiến lược nội dung

Trước khi viết, xác định:

- **Đây là RSD WEB hay RSD APP?** Nếu APP và đã có RSD WEB tương ứng, hầu hết các section 1.2, 2.2, 3, 5 sẽ **tham chiếu** (link) sang RSD WEB thay vì viết lại. Chỉ Section 4 (Mô tả màn hình) là viết mới theo Figma APP.
- **Đây là chức năng mới hay update?** Chức năng mới cần liệt kê đầy đủ các kết nối trong 2.2; update chỉ mô tả phần thay đổi.
- **Các quy tắc nghiệp vụ tới từ đâu?** Thường từ URD; nếu URD thiếu, đánh dấu `[Cần xác nhận]`.

### Bước 3 — Sinh nội dung theo template

Đọc `references/rsd-template.md` để lấy skeleton đầy đủ (wiki format). Đọc `references/rsd-example-condensed.md` để thấy ví dụ cách điền. Đọc `references/figma-to-mockup.md` khi viết Section 4.

**Viết tài liệu theo Confluence Wiki Markup** (không phải Markdown). Lý do: MCP `confluence_create_page` với `content_format="wiki"` cho phép dùng macro `{toc}` tạo TOC tự động có link, heading syntax rõ ràng, và image attachment native — tốt hơn hẳn markdown.

**Cú pháp wiki cơ bản cần nhớ:**
```
*bold*          → in đậm
_italic_        → in nghiêng
h2. Tên         → heading level 2 (dùng cho section 1–5)
h3. Tên         → heading level 3 (dùng cho 1.1, 1.2, 2.1...)
||Col1||Col2||  → header row của bảng
|Cell1|Cell2|   → data row của bảng
[Text|URL]      → hyperlink
[#anchor-id]    → link nội bộ đến anchor trong cùng page
{anchor:id}     → đặt anchor tại vị trí hiện tại
{toc:maxLevel=2} → macro TOC tự động, clickable
!filename.png!  → nhúng ảnh attachment
{noformat}...{noformat} → khối text không format (dùng cho sơ đồ ASCII)
```

Các section trong wiki format:

1. **Phiên bản tài liệu** — bảng với header row `||Version||Lý do||...||`, data row `|1.0|Thêm mới|<ngày hôm nay>|<tác giả>|Khởi tạo|` — **không ghi "Dự thảo"**
2. **Mục lục** — dùng macro `{toc:maxLevel=2}`, Confluence tự sinh TOC clickable từ h2/h3 headings
3. **Section 1–5** — mỗi section dùng `h2.` + `{anchor:section-N}` để TOC link đến đúng vị trí. Sub-section dùng `h3.`
4. **Section 1.2** — bảng 2 cột với đầu tiên là tên trường in đậm `|*Tên*|giá trị|`
5. **Section 2.2** — bảng API connections với header row 7 cột
6. **Section 3** — ma trận phân quyền: dùng "x" cho có quyền, trống cho không có. Columns tùy theo loại dự án (xem template)
7. **Section 4 — Mô tả màn hình** (quan trọng nhất, viết chi tiết):
   - Link Figma: `Figma: [Link|https://figma.com/...]`
   - **a. Mockup màn hình**: Caption (text thuần, không emoji) rồi ảnh:
     - Có Figma: tải ảnh bằng Figma MCP → lưu local → sau khi tạo page, attach bằng `mcp__mcp-atlassian__confluence_upload_attachments` → chèn `!ten-file.png!`
     - Không có Figma: chèn `_(Ảnh: chưa có - cần bổ sung từ Figma)_`
   - **KHÔNG** dùng emoji hay mô tả blockquote thay cho ảnh
   - **b. Bảng mô tả màn hình**: header row `|| ||*Hạng mục*||*Kiểu hiển thị*||*Kiểu thao tác*||*Bắt buộc*||*Độ dài*||*Mô tả*||` (cột đầu để trống). Row group header: `|*Cụm thông tin đầu trang*| | | | | |`
8. **Section 5** — bảng 3 cột `||*Thao tác*||*Tác nhân*||*Mô tả*||`

Trong suốt quá trình: nếu thông tin **có thể suy luận hợp lý từ context** → điền trực tiếp. Chỉ ghi `[Cần xác nhận: <câu hỏi cụ thể>]` khi thực sự không thể xác định từ bất kỳ resource nào đã đọc.

### Bước 4 — Tổng hợp checklist (nếu còn điểm chưa rõ)

Nếu có `[Cần xác nhận]` trong body, thêm section cuối:
```
h2. Các điểm cần bổ sung
```
Liệt kê dạng bullet `*` kèm section reference. Nếu không có điểm nào → bỏ qua section này hoàn toàn.

### Bước 5 — Upload lên Confluence

Dùng MCP `mcp__mcp-atlassian__confluence_create_page` trực tiếp với `content_format="wiki"`:

```
mcp__mcp-atlassian__confluence_create_page(
    space_key="<SPACE>",
    title="<TITLE>",
    content="<nội dung wiki markup>",
    content_format="wiki",
    parent_id="<PARENT_PAGE_ID>"
)
```

Sau khi tạo page, nếu có ảnh cần attach:
```
mcp__mcp-atlassian__confluence_upload_attachments(
    page_id="<page_id>",
    files=["./screenshots/01-default.png", ...]
)
```

Xem `references/confluence-upload.md` để biết chi tiết và fallback khi cần update page đã có.

**Title format**: `"<PLATFORM> <số thứ tự>. <Tên chức năng>_<Tên dự án>"` — ví dụ `"WEB 2.1. Danh sách thẻ tín dụng nội địa_Skymap"`. Hỏi user nếu chưa rõ.

### Bước 6 — Trả kết quả

Trả về cho user:

```
✅ Đã tạo RSD: <title>
🔗 Link: https://<domain>/wiki/spaces/<SPACE>/pages/<id>/<slug>
⚠️ <N> điểm cần xác nhận (xem mục cuối page / list dưới đây):
   - ...
```

## Xử lý lỗi thường gặp

- **Figma MCP trả quá nhiều dữ liệu cho 1 node lớn**: thu hẹp bằng cách truyền đúng nodeId của từng màn con, không lấy node cha.
- **Confluence page quá lớn khi đọc URD**: tool lưu ra file; đọc theo offset/limit, grep heading trước để tìm section cần thiết thay vì đọc toàn bộ.
- **Upload fail do size**: markdown >10KB phải dùng `upload_confluence_v2.py`, không dùng MCP `confluence_create_page`.
- **Ảnh không hiện sau upload**: kiểm tra đường dẫn ảnh trong markdown là relative tới file .md, không phải absolute.

## Reference files

- `references/rsd-template.md` — Skeleton markdown đầy đủ 7 sections, copy & fill.
- `references/rsd-example-condensed.md` — Ví dụ rút gọn từ sample thực, dùng để học cách diễn đạt & mức độ chi tiết.
- `references/figma-to-mockup.md` — Cách biến Figma output thành caption mockup + rows bảng Mô tả màn hình.
- `references/confluence-upload.md` — Hai path upload (MCP cho page nhỏ, script cho page lớn), cách tạo page mới và attach ảnh.
