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
3. **Tuân thủ template Việt hoá — dùng Confluence Wiki Markup, không dùng Markdown.** Toàn bộ heading, label bảng, từ khoá phải khớp chính xác template. Quy tắc heading và bảng:
   - **Heading section 1–5**: đặt anchor trước rồi dùng `h2.`. Ví dụ đúng:
     ```
     {anchor:section-1}
     h2. 1. Đặc tả/Tóm tắt usecase
     ```
   - **Heading sub-section** (1.1, 1.2, 2.1, ...): dùng `h3.`. Ví dụ: `h3. 1.1. Sơ đồ Usecase`
   - **Bảng** dùng `||col||` cho header row, `|cell|` cho data row. KHÔNG dùng Markdown `| --- |`
   - **Bảng Section 4b** (mô tả màn hình): header cột đầu phải rỗng `|| ||`. Ví dụ đúng:
     ```
     || ||*Hạng mục*||*Kiểu hiển thị*||*Kiểu thao tác*||*Bắt buộc*||*Độ dài*||*Mô tả*||
     ```
   - **Row group header** trong bảng 4b: `|STT|*Tên cụm*| | | | | |` — cột đầu là số thứ tự, cột 2 là tên cụm in đậm, 5 cột còn lại để trống (tổng 7 cells, khớp với 7 cột header)
4. **Tuyệt đối không dùng emoji/icon trong nội dung tài liệu.** Không được dùng bất kỳ emoji hay icon nào (✅ ❌ 🔘 🟡 🟢 🔴 ✏️ ▶ ✖ 📋 ⚠️ v.v.) trong nội dung bảng, mô tả màn hình, hay bất kỳ chỗ nào trong tài liệu RSD (trừ mục "Các điểm cần user xác nhận" ở cuối). Thay thế cụ thể:
   - Ma trận phân quyền: dùng **"x"** cho có quyền, để **trống ô** cho không có quyền
   - Trạng thái badge: viết text thuần (ví dụ: "Tạo nháp", "Chờ duyệt", "Hoạt động")
   - Tên nút chức năng: viết text không có icon (ví dụ: "Chỉnh sửa", "Phê duyệt", "Từ chối")

## Workflow end-to-end

Thực hiện tuần tự:

### Bước 1 — Gather & đọc hết inputs ngay lập tức

**Ưu tiên thực sự của skill này: Section 4 (Mô tả màn hình) là output quan trọng nhất, luôn phải sinh ra đầy đủ.** Ảnh/Figma là input chính. URD và các tài liệu khác là optional — có thì enrich thêm các section còn lại, không có thì vẫn phải ra được Section 4.

| Input | Bắt buộc | Nếu thiếu |
|-------|----------|-----------|
| Tên chức năng + platform (WEB/APP/BO) | Có | Hỏi user |
| Space Confluence + Parent page ID | Có | Hỏi user |
| Ảnh mockup hoặc Figma link | Có | Hỏi user — đây là nguồn sinh Section 4 |
| URD (link Confluence, Jira issue...) | Không | Để trống / `[Cần bổ sung]` ở các section liên quan |
| Page tham chiếu (RSD cấp 1, bảng trạng thái, RSD WEB...) | Không | Bỏ qua, điền khi user cung cấp |
| Tên tác giả | Không | Dùng tên user hiện tại hoặc để trống |

**Quy trình đọc resource:**

**0. Luôn scan `./screenshots/` trước tiên** — ngay khi bắt đầu, trước khi xử lý bất kỳ input nào khác:
```bash
ls ./screenshots/
```
Nếu thư mục tồn tại và có file ảnh → đây là nguồn ảnh chính cho Section 4a. Liệt kê tên các file, dùng trực tiếp trong wiki content (`!tên-file.png!`) và attach sau khi tạo page. Không cần user đính kèm lại hay cung cấp thêm nguồn nào khác.

- **Figma link**: `mcp__plugin_figma_figma__get_design_context` (lấy element-level) + `get_screenshot` cho từng state cần mô tả (default, empty, error, dropdown mở...). Parse URL: `figma.com/design/{fileKey}/...?node-id={nodeId}` — convert `-` thành `:` trong nodeId. Tải ảnh về `./screenshots/`.
- **Ảnh đính kèm trong conversation** — không giả định format. Kiểm tra thực tế và xử lý:
  - **Local file path**: `cp "<path>" "./screenshots/screen-01-default.png"`
  - **Base64 string**: `echo "<base64>" | base64 -d > "./screenshots/screen-01-default.png"`
  - **URL** (attachment URL, CDN link...): `curl -L -o "./screenshots/screen-01-default.png" "<url>"`
  - **Chỉ thấy ảnh inline, không có path/base64/url**: ghi placeholder `_(Ảnh: <mô tả nội dung> — cần attach file)_`
  
  Sau khi có file local → chèn `!tên-file.png!` vào wiki content đúng state → attach sau khi tạo page bằng `confluence_upload_attachments`
- **Ảnh từ Jira issue** (nếu user cung cấp link Jira có ảnh đính kèm): dùng `mcp__mcp-atlassian__jira_download_attachments` → tải về `./screenshots/` → dùng như bình thường
- **URD / Jira issue** (nếu có): `mcp__mcp-atlassian__confluence_get_page` hoặc `mcp__mcp-atlassian__jira_get_issue` — đọc description + comments + attachments.
- **Page tham chiếu** (nếu có): đọc tương tự, extract thông tin liên quan cho từng section.

### Bước 2 — Quyết định chiến lược nội dung

Trước khi viết, xác định:

- **Đây là RSD WEB hay RSD APP?** Nếu APP và đã có RSD WEB tương ứng, sections 1.2, 2.2, 3, 5 sẽ **tham chiếu** (link) sang RSD WEB. Chỉ Section 4 là viết mới theo Figma/ảnh APP.
- **Có URD/tài liệu không?** Nếu có → đọc hết và extract thông tin cho sections 1, 2, 3, 5. Nếu không → các section đó dùng minimal template hoặc `[Cần bổ sung]`, nhưng **Section 4 vẫn phải đầy đủ**.
- **Số lượng ảnh/state**: Xác định từ kết quả `ls ./screenshots/` (Bước 1), Figma, hoặc ảnh user cung cấp. Nếu `./screenshots/` có file → đó là danh sách state, mỗi file = 1 state trong Section 4a. Mỗi state = 1 caption + 1 ảnh (`!filename.png!`) + rows tương ứng trong bảng 4b.

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

**CRITICAL — Quy tắc tuyệt đối khi viết nội dung trong cell bảng (vi phạm = vỡ bảng):**

1. **Toàn bộ nội dung 1 cell phải nằm trên 1 dòng duy nhất.** Không được xuống dòng thật (Enter) giữa chừng trong nội dung cell. Confluence parser thấy `\n` giữa cell = kết thúc row → vỡ bảng.
2. **Dùng `\\` (2 backslash) để xuống dòng trong cell**, không dùng Enter.
3. **Không dùng ký tự `|` (pipe) trong nội dung cell.** Parser hiểu `|` = ranh giới cột → tạo thêm cột thừa.
4. **Không dùng `#` để tạo numbered list trong cell.** Dùng số thủ công với `\\`:

   SAI — sẽ vỡ bảng:
   ```
   |*Điều kiện trước*|# User đăng nhập
   # User được phân quyền|
   ```
   ĐÚNG:
   ```
   |*Điều kiện trước*|1. User đăng nhập \\ 2. User được phân quyền|
   ```

   SAI — extra columns vì dùng `|` trong Mô tả:
   ```
   |5|Textbox|Input|N|-|Placeholder: "..."|Logic: ...|Ẩn/hiện: ...|
   ```
   ĐÚNG:
   ```
   |5|Textbox|Input|N|-|Placeholder: "...". Logic: ... Ẩn/hiện: ...|
   ```

Các section trong wiki format:

1. **Phiên bản tài liệu** — bảng với header row `||Version||Lý do||...||`, data row `|1.0|Thêm mới|<ngày hôm nay>|<tác giả>|Khởi tạo|` — **không ghi "Dự thảo"**
2. **Mục lục** — dùng macro `{toc:maxLevel=2}`, Confluence tự sinh TOC clickable từ h2/h3 headings
3. **Section 1–5** — mỗi section dùng `h2.` + `{anchor:section-N}` để TOC link đến đúng vị trí. Sub-section dùng `h3.`
4. **Section 1.2** — bảng 2 cột với đầu tiên là tên trường in đậm `|*Tên*|giá trị|`
5. **Section 2.2** — bảng API connections với header row 7 cột
6. **Section 3** — ma trận phân quyền: dùng "x" cho có quyền, trống cho không có. Columns tùy theo loại dự án (xem template)
7. **Section 4 — Mô tả màn hình** (quan trọng nhất — LUÔN sinh đầy đủ dù thiếu bất kỳ input nào khác):
   - Link Figma: `Figma: [Link|https://figma.com/...]` hoặc `Figma: N/A`
   - **a. Mockup màn hình** — quy tắc BẮT BUỘC:
     - Với **mỗi state** (default, empty, error, dropdown, v.v.), viết theo pattern:
       ```
       Caption mô tả state (text thuần, không emoji)

       !ten-file.png!
       ```
     - Nếu **có Figma**: tải ảnh → lưu vào `./screenshots/` → chèn `!ten-file.png!` → attach sau khi tạo page
     - Nếu **có ảnh user đính kèm**: lưu local → chèn `!ten-file.png!` → attach sau khi tạo page
     - Nếu **không có ảnh nào**: chèn placeholder `_(Ảnh: chưa có - cần bổ sung)_`
     - **CẤM tuyệt đối các cách sau** — đây là output SAI:
       - `*(15 screenshots được đính kèm tại page Confluence)*` — ghi chú chung thay cho ảnh
       - `[Ảnh sơ đồ luồng — cần bổ sung nếu có tài liệu đính kèm]` — note mơ hồ
       - Để trống section 4a, không có caption cũng không có ảnh/placeholder
     - Mỗi state = 1 caption + 1 dòng ảnh hoặc placeholder — không có ngoại lệ
   - **b. Bảng mô tả màn hình** — sinh từ ảnh/Figma là chính:
     - Header: `|| ||*Hạng mục*||*Kiểu hiển thị*||*Kiểu thao tác*||*Bắt buộc*||*Độ dài*||*Mô tả*||` (cột đầu để trống — không ghi STT)
     - Row group header: `|STT|*Tên cụm*| | | | | |` (STT = số thứ tự, 7 cells tổng)
     - Mỗi element một row, điền đầy đủ: placeholder, mặc định, validate, logic tương tác, nguồn dữ liệu, ẩn/hiện, enable/disable
     - Xem `references/figma-to-mockup.md` để biết cách map Figma → từng row
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
    content_id="<page_id>",
    file_paths="./screenshots/01-default.png,./screenshots/02-empty.png,..."
)
```
`file_paths` là chuỗi các path ngăn cách bởi dấu phẩy — không phải array.

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
- **Upload fail do size**: nếu wiki content >100KB thì tạo page rỗng trước rồi update — xem `references/confluence-upload.md`.
- **Ảnh không hiện sau upload**: kiểm tra tên file trong `!filename.png!` khớp chính xác tên file attach (case-sensitive).
- **Dòng image placeholder bị bỏ**: KHÔNG được bỏ dòng `_(Ảnh: chưa có - cần bổ sung)_` — mỗi caption phải có dòng ảnh hoặc placeholder ngay bên dưới.
- **Section 4 bị thiếu khi không có URD**: Section 4 không phụ thuộc URD — sinh từ ảnh/Figma. Không được skip Section 4 chỉ vì thiếu tài liệu nghiệp vụ.

## Reference files

- `references/rsd-template.md` — Skeleton wiki markup đầy đủ 5 sections, copy & fill.
- `references/rsd-example-condensed.md` — Ví dụ rút gọn từ sample thực, dùng để học cách diễn đạt & mức độ chi tiết.
- `references/figma-to-mockup.md` — Cách biến Figma output thành caption mockup + rows bảng Mô tả màn hình.
- `references/confluence-upload.md` — Upload wiki format qua MCP, cách attach ảnh, fallback khi page quá lớn.
