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

0. **Publish luôn — không draft.** Output phải là tài liệu hoàn chỉnh, publish trực tiếp lên Confluence. Không tạo file draft local. Khai thác tối đa mọi resource user cung cấp trước khi hỏi thêm. Bảng Phiên bản tài liệu dùng "Dự thảo" cho lần tạo đầu (theo convention thực tế của các dự án).

1. **Không bịa dữ liệu — nhưng phải khai thác hết resource trước.** Đọc kỹ toàn bộ URD, tất cả page Confluence tham chiếu, và Figma trước khi kết luận "thiếu thông tin". Nếu thông tin nào thực sự chưa xác định được: điền placeholder text mô tả rõ ràng (ví dụ: `Chờ xác nhận từ BA`) vào đúng vị trí trong tài liệu — KHÔNG được ghi `[Cần xác nhận]` hay comment kiểu annotation trong document. Ghi lại danh sách nội bộ để báo cáo trong chat sau khi upload.
2. **Ưu tiên tham chiếu hơn copy-paste.** Khi có page Confluence đã mô tả sẵn (RSD cấp 1, bảng trạng thái, API spec...), link sang đó thay vì paste lại. Các RSD APP thường chỉ viết Section 4 (mô tả màn hình) còn lại tham chiếu sang RSD WEB.
3. **Tuân thủ template Việt hoá — dùng Confluence Storage Format (XHTML), không dùng Markdown.** Toàn bộ heading, label bảng, từ khoá phải khớp chính xác template. Quy tắc heading và bảng:
   - **Heading section 1–5**: dùng `<h2>`, không cần anchor. Ví dụ: `<h2>1. Đặc tả/Tóm tắt usecase</h2>`. Confluence tự tạo anchor từ heading text.
   - **Heading sub-section** (1.1, 1.2, 2.1, ...): dùng `<h3>`. Ví dụ: `<h3>1.1. Sơ đồ Usecase</h3>`
   - **Không dùng `<hr/>`** để ngăn cách section — chỉ dùng heading h2 để phân tách.
   - **Bảng** dùng `<table><tbody><tr><th><p>col</p></th>...` cho header row, `<tr><td><p>cell</p></td>...` cho data row.
   - **Bảng Section 4b** (mô tả màn hình): header cột đầu phải là `<th><p></p></th>` (rỗng). Row group header: cột 2 là `<td><p><strong>Tên cụm</strong></p></td>`, 5 cột còn lại `<td><p> </p></td>`.
   - **Info callout** dùng `<ac:structured-macro ac:name="info"><ac:rich-text-body><p>...</p></ac:rich-text-body></ac:structured-macro>` đầu section 2.2 và section 3 (theo mẫu thực tế)
4. **Tuyệt đối không dùng emoji/icon trong nội dung tài liệu.** Không được dùng bất kỳ emoji hay icon nào (✅ ❌ 🔘 🟡 🟢 🔴 ✏️ ▶ ✖ 📋 ⚠️ v.v.) trong nội dung bảng, mô tả màn hình, hay bất kỳ chỗ nào trong tài liệu RSD. Thay thế cụ thể:
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
| Space Confluence + Parent page ID | Có | Tự tìm: nếu user cung cấp URL → trích từ URL; nếu user nói tên space → gọi `confluence_get_space_page_tree` lấy root page; chỉ hỏi nếu không suy ra được |
| Ảnh mockup hoặc Figma link | Không | Sinh placeholder caption cho từng state phổ biến + `_(Ảnh: chưa có - cần bổ sung)_` — Section 4 vẫn phải đầy đủ |
| URD (link Confluence, Jira issue...) | Không | Điền `Chờ xác nhận từ BA` cho các field thiếu thông tin |
| Page tham chiếu (RSD cấp 1, bảng trạng thái, RSD WEB...) | Không | Bỏ qua, điền khi user cung cấp |
| Tên tác giả | Không | Dùng tên user hiện tại hoặc để trống |

**Quy trình đọc resource:**

**0. Luôn scan `./screenshots/` trước tiên** — ngay khi bắt đầu, trước khi xử lý bất kỳ input nào khác:
```bash
ls ./screenshots/ 2>/dev/null || ls /tmp/rsd-screenshots/ 2>/dev/null
```
Nếu có file ảnh → đây là nguồn ảnh chính cho Section 4a. Nếu ảnh nằm trong thư mục có khoảng trắng hoặc ký tự đặc biệt, copy sang `/tmp/rsd-screenshots/` trước khi dùng. Không cần user đính kèm lại hay cung cấp thêm nguồn nào khác.

- **Figma link**: `mcp__plugin_figma_figma__get_design_context` (lấy element-level) + `get_screenshot` cho từng state cần mô tả (default, empty, error, dropdown mở...). Parse URL: `figma.com/design/{fileKey}/...?node-id={nodeId}` — convert `-` thành `:` trong nodeId. Tải ảnh về `./screenshots/`.
- **Ảnh đính kèm trong conversation** — không giả định format. Kiểm tra thực tế và xử lý:
  - **Local file path**: `cp "<path>" "./screenshots/screen-01-default.png"`
  - **Base64 string**: `echo "<base64>" | base64 -d > "./screenshots/screen-01-default.png"`
  - **URL** (attachment URL, CDN link...): `curl -L -o "./screenshots/screen-01-default.png" "<url>"`
  - **Chỉ thấy ảnh inline, không có path/base64/url**: ghi placeholder `_(Ảnh: <mô tả nội dung> — cần attach file)_`
  
  Sau khi có file local → copy vào `/tmp/rsd-screenshots/` → chèn `<ac:image ac:width="..."><ri:attachment ri:filename="tên-file.png"/></ac:image>` trong storage content đúng state → attach sau khi tạo page bằng `confluence_upload_attachments`
- **Ảnh từ Jira issue** (nếu user cung cấp link Jira có ảnh đính kèm): dùng `mcp__mcp-atlassian__jira_download_attachments` → tải về `./screenshots/` → dùng như bình thường
- **URD / Jira issue** (nếu có): `mcp__mcp-atlassian__confluence_get_page` hoặc `mcp__mcp-atlassian__jira_get_issue` — đọc description + comments + attachments.
- **Page tham chiếu** (nếu có): đọc tương tự, extract thông tin liên quan cho từng section.

### Bước 2 — Quyết định chiến lược nội dung

Trước khi viết, xác định:

- **Đây là RSD WEB hay RSD APP?** Nếu APP và đã có RSD WEB tương ứng, sections 1.2, 2.2, 3, 5 sẽ **tham chiếu** (link) sang RSD WEB. Chỉ Section 4 là viết mới theo Figma/ảnh APP.
- **Có URD/tài liệu không?** Nếu có → đọc hết và extract thông tin cho sections 1, 2, 3, 5. Nếu không → các section đó dùng minimal template với `Chờ xác nhận từ BA` ở các field thiếu thông tin, nhưng **Section 4 vẫn phải đầy đủ**.
- **Số lượng ảnh/state**: Xác định từ kết quả `ls ./screenshots/` (Bước 1), Figma, hoặc ảnh user cung cấp. Nếu `./screenshots/` có file → đó là danh sách state, mỗi file = 1 state trong Section 4a. Mỗi state = 1 caption `<p>` + 1 ảnh `<ac:image ac:width="..."><ri:attachment ri:filename="..."/></ac:image>` + rows tương ứng trong bảng 4b.

### Bước 3 — Sinh nội dung theo template

Đọc `references/rsd-template.md` để lấy skeleton đầy đủ (storage format). Đọc `references/rsd-example-condensed.md` để thấy ví dụ cách điền. Đọc `references/figma-to-mockup.md` khi viết Section 4.

**Viết tài liệu theo Confluence Storage Format** (XHTML + Confluence macros), dùng `content_format="storage"`. Lý do: storage format hỗ trợ `<ac:layout-section ac:breakout-mode="wide">` giúp Section 4a image grid hiển thị đúng chiều rộng như các page mẫu — wiki format `{section}` không có tính năng này.

**Cú pháp storage format cần nhớ:**
```xml
<strong>bold</strong>                       → in đậm
<em>italic</em>                              → in nghiêng
<h2>Heading</h2>                             → heading level 2
<h3>Sub-heading</h3>                         → heading level 3
<h4>Sub-sub-heading</h4>                     → heading level 4

<!-- Bảng -->
<table><tbody>
<tr><th><p>Col1</p></th><th><p>Col2</p></th></tr>
<tr><td><p>Cell1</p></td><td><p>Cell2</p></td></tr>
</tbody></table>

<!-- Xuống dòng trong cell bảng -->
<br/>

<!-- Link -->
<a href="URL">Text</a>

<!-- TOC macro -->
<ac:structured-macro ac:name="toc"><ac:parameter ac:name="style">none</ac:parameter></ac:structured-macro>

<!-- Info callout (đầu Section 2.2 và 3) -->
<ac:structured-macro ac:name="info"><ac:rich-text-body><p>Nội dung</p></ac:rich-text-body></ac:structured-macro>

<!-- Noformat block (sơ đồ ASCII) -->
<ac:structured-macro ac:name="noformat"><ac:plain-text-body><![CDATA[nội dung]]></ac:plain-text-body></ac:structured-macro>

<!-- Ảnh attachment -->
<ac:image ac:width="360"><ri:attachment ri:filename="screen-01.png"/></ac:image>

<!-- Wide image grid — BẮT BUỘC dùng ac:layout, KHÔNG dùng {section}/{column} -->
<!-- WEB: three_equal, APP: four_equal, dialog: two_equal -->
<ac:layout>
<ac:layout-section ac:breakout-mode="wide" ac:breakout-width="1174" ac:type="three_equal">
<ac:layout-cell><p>Caption state 1</p>
<ac:image ac:width="360"><ri:attachment ri:filename="screen-01.png"/></ac:image></ac:layout-cell>
<ac:layout-cell><p>Caption state 2</p>
<ac:image ac:width="360"><ri:attachment ri:filename="screen-02.png"/></ac:image></ac:layout-cell>
<ac:layout-cell><p>Caption state 3</p>
<p><em>(Ảnh: chưa có - cần bổ sung)</em></p></ac:layout-cell>
</ac:layout-section>
</ac:layout>
```

**Lưu ý quan trọng khi viết storage format:**
- Tất cả nội dung phải là well-formed XHTML — đóng thẻ đúng, escape ký tự đặc biệt (`&amp;`, `&lt;`, `&gt;`)
- Text trong `<td>` và `<th>` phải bọc trong `<p>...</p>`
- Bold trong cell: `<td><p><strong>Tên</strong></p></td>`
- Không cần lo về `|` trong nội dung — không còn restriction này ở storage format
- Line break trong cell: dùng `<br/>` thay vì `\\`

**Quy tắc viết bảng trong storage format:**

1. **Mỗi cell là một `<td>` hoặc `<th>`, nội dung bọc trong `<p>...</p>`.**
2. **Xuống dòng trong cell dùng `<br/>`** — không dùng ký tự `\\`.
3. **Ký tự `|` trong nội dung hoàn toàn OK** — không còn restriction này ở storage format.
4. **Numbered list trong cell** dùng `1. text<br/>2. text` hoặc `<ol><li>...</li></ol>`.
5. **Bold trong cell**: `<td><p><strong>Tên</strong></p></td>`.
6. **Cell rỗng**: `<td><p> </p></td>` — phải có `<p> </p>` bên trong.

Ví dụ bảng Section 1.2 đúng:
```xml
<table><tbody>
<tr><th><p>Hạng mục</p></th><th><p>Nội dung</p></th></tr>
<tr><td><p><strong>Tên</strong></p></td><td><p>Danh sách thẻ tín dụng nội địa</p></td></tr>
<tr><td><p><strong>Điều kiện trước</strong></p></td><td><p>1. User đăng nhập thành công<br/>2. User được phân quyền...</p></td></tr>
</tbody></table>
```

Các section trong storage format:

1. **Phiên bản tài liệu** — `<table>` với headers Version/Lý do/Date/Người sửa/Mô tả, data row: `1.0 | Thêm mới | <ngày hôm nay> | <tác giả> | Dự thảo`
2. **Mục lục** — `<ac:structured-macro ac:name="toc"><ac:parameter ac:name="style">none</ac:parameter></ac:structured-macro>`. Confluence tự sinh TOC clickable từ h2/h3/h4 tags. Không cần anchor thủ công.
3. **Section 1–5** — dùng `<h2>` cho section chính, `<h3>` cho sub-section (1.1, 1.2...), `<h4>` cho sub-sub (2.3.1...). Không dùng `<hr>` separator.
4. **Section 1.2** — `<table>` 2 cột, cột đầu có `<strong>Tên trường</strong>`
5. **Section 2.2** — bắt đầu bằng `ac:structured-macro ac:name="info"` block, sau đó bảng 7 cột. Tên cột 6: `Luồng gọi API/ Luồng đi của kết nối`
6. **Section 3** — bắt đầu bằng `info` macro block. Ma trận phân quyền: "x" cho có quyền, cell rỗng `<td><p> </p></td>` cho không có. Cột cuối: `Nhóm quyền khác còn lại`. Columns tùy theo loại dự án (xem template)
7. **Section 4 — Mô tả màn hình** (heading: `<h2>4<strong>. Mô tả màn hình</strong></h2>` — số `4` không bold, phần còn lại bold theo mẫu). LUÔN sinh đầy đủ dù thiếu bất kỳ input nào khác:
   - Link Figma: `<p>Figma: <a href="https://figma.com/...">Tên file</a></p>` hoặc `<p>Figma: N/A</p>`
   - **a. Mockup màn hình** — BẮT BUỘC dùng `<ac:layout>` với `breakout-mode="wide"`:
     - Số cột theo platform:
       - **WEB**: `ac:type="three_equal"`, image `ac:width="360"`
       - **APP**: `ac:type="four_equal"`, image `ac:width="200"`
       - **Dialog/Detail**: `ac:type="two_equal"`, image `ac:width="500"`
     - Ví dụ WEB (3 cột):
       ```xml
       <ac:layout>
       <ac:layout-section ac:breakout-mode="wide" ac:breakout-width="1174" ac:type="three_equal">
       <ac:layout-cell>
       <p>Caption state 1</p>
       <ac:image ac:width="360"><ri:attachment ri:filename="screen-01-default.png"/></ac:image>
       <p>Caption state 2</p>
       <ac:image ac:width="360"><ri:attachment ri:filename="screen-02-empty.png"/></ac:image>
       </ac:layout-cell>
       <ac:layout-cell>
       <p>Caption state 3</p>
       <ac:image ac:width="360"><ri:attachment ri:filename="screen-03-search.png"/></ac:image>
       <p>Caption state 4</p>
       <p><em>(Ảnh: chưa có - cần bổ sung)</em></p>
       </ac:layout-cell>
       <ac:layout-cell>
       <p>Caption state 5</p>
       <p><em>(Ảnh: chưa có - cần bổ sung)</em></p>
       </ac:layout-cell>
       </ac:layout-section>
       </ac:layout>
       ```
     - **Luôn sinh ra khối `<ac:layout>` dù không có ảnh nào** — dùng `<em>(Ảnh: chưa có - cần bổ sung)</em>` cho mỗi state
     - Nếu **có ảnh**: dùng `<ac:image ac:width="..."><ri:attachment ri:filename="filename"/></ac:image>`
     - **CẤM dùng `{section}/{column}` wiki macro** — không có `breakout-mode`, sẽ hẹp hơn mẫu
     - Mỗi state = 1 `<p>Caption</p>` + 1 `<ac:image>` hoặc `<p><em>(Ảnh: chưa có...)</em></p>`
   - **b. Bảng mô tả màn hình** — **BẮT BUỘC sinh đầy đủ**:
     - Header row: cột đầu `<th><p> </p></th>`, các cột: Hạng mục / Kiểu hiển thị / Kiểu thao tác / Bắt buộc / Độ dài / Mô tả
     - Row group header: `<tr><td><p>STT</p></td><td><p><strong>Tên cụm</strong></p></td><td><p> </p></td>...(5 cells trống)</td></tr>`
     - Các cụm cần liệt kê: Thông tin đầu trang, Tìm kiếm nhanh, Tìm kiếm nâng cao, Danh sách, Phân trang, Action buttons
     - Mỗi element một row, điền đầy đủ: placeholder, mặc định, validate, logic tương tác, nguồn dữ liệu, ẩn/hiện, enable/disable
     - Xem `references/figma-to-mockup.md` để biết cách map Figma → từng row
8. **Section 5** — bảng 3 cột: Thao tác / Tác nhân / Mô tả

Trong suốt quá trình: nếu thông tin **có thể suy luận hợp lý từ context** → điền trực tiếp. Nếu thực sự không thể xác định → điền placeholder text mô tả (ví dụ: `Chờ xác nhận từ BA`, `Cần bổ sung API endpoint`) vào đúng cell, ghi nội bộ để báo cáo trong chat. KHÔNG ghi `[Cần xác nhận]` hoặc bất kỳ annotation dạng comment nào trong document Confluence.

### Bước 4 — Tổng hợp checklist nội bộ

Nếu có thông tin chưa xác định được: ghi lại danh sách nội bộ (không upload vào document). Danh sách này sẽ được báo cáo trong chat reply ở Bước 6 sau khi upload xong. Format nội bộ:

```
- [Section X.Y] <câu hỏi cụ thể cần xác nhận>
- [Section X.Y] <câu hỏi khác>
```

Nếu không có điểm nào → bỏ qua hoàn toàn.

### Bước 5 — Upload lên Confluence

Dùng MCP `mcp__mcp-atlassian__confluence_create_page` với `content_format="storage"`:

```
mcp__mcp-atlassian__confluence_create_page(
    space_key="<SPACE>",
    title="<TITLE>",
    content="<nội dung storage format XHTML>",
    content_format="storage",
    parent_id="<PARENT_PAGE_ID>",
    page_width="full-width"    # BẮT BUỘC — nếu thiếu page sẽ hẹp hơn sample
)
```

Nếu đã có page cùng tên (duplicate), dùng `confluence_update_page` thay vì tạo mới:
```
mcp__mcp-atlassian__confluence_update_page(
    page_id="<PAGE_ID>",
    title="<TITLE>",
    content="<nội dung storage format XHTML>",
    content_format="storage",
    page_width="full-width",
    version_comment="Cập nhật nội dung RSD"
)
```

Sau khi tạo/update page, nếu có ảnh cần attach:
```bash
# Staging: copy tất cả ảnh vào /tmp/rsd-screenshots/ (không có khoảng trắng)
mkdir -p /tmp/rsd-screenshots
cp <source_dir>/*.png /tmp/rsd-screenshots/
```
```
mcp__mcp-atlassian__confluence_upload_attachments(
    content_id="<page_id>",
    file_paths="/tmp/rsd-screenshots/screen-01-default.png,/tmp/rsd-screenshots/screen-02-empty.png,..."
)
```
`file_paths` là chuỗi path ngăn cách bởi dấu phẩy — không phải array. Tránh path có khoảng trắng.

Xem `references/confluence-upload.md` để biết chi tiết và fallback khi cần update page đã có.

**Title format**: `"[<PLATFORM>] <số thứ tự>. <Tên chức năng>_<Tên dự án>"` — ví dụ `"[WEB] 2.1. Danh sách thẻ tín dụng nội địa_Skymap"` hoặc `"[APP] 2.1. Danh sách thẻ tín dụng nội địa_Skymap"`. Hỏi user nếu convention của dự án khác.

### Bước 6 — Trả kết quả

Trả về cho user trong chat (không emoji — text thuần):

```
Đã tạo RSD: <title>
Link: https://<domain>/wiki/spaces/<SPACE>/pages/<id>/<slug>

Các điểm cần xác nhận thêm:
- [Section X.Y] <câu hỏi 1>
- [Section X.Y] <câu hỏi 2>
```

Nếu không có điểm nào cần xác nhận thì bỏ phần đó đi — chỉ trả link.

## Xử lý lỗi thường gặp

- **Figma MCP trả quá nhiều dữ liệu cho 1 node lớn**: thu hẹp bằng cách truyền đúng nodeId của từng màn con, không lấy node cha.
- **Confluence page quá lớn khi đọc URD**: tool lưu ra file; đọc theo offset/limit, grep heading trước để tìm section cần thiết thay vì đọc toàn bộ.
- **Upload fail do size**: nếu content >100KB thì tạo page rỗng trước rồi update — xem `references/confluence-upload.md`.
- **Ảnh không hiện sau upload**: kiểm tra `ri:filename` trong `<ac:image>` khớp chính xác tên file attach (case-sensitive).
- **Dòng image placeholder bị bỏ**: KHÔNG được bỏ `<p><em>(Ảnh: chưa có - cần bổ sung)</em></p>` — mỗi caption phải có `<ac:image>` hoặc placeholder ngay bên dưới.
- **Section 4 bị thiếu khi không có URD**: Section 4 không phụ thuộc URD — sinh từ ảnh/Figma. Không được skip Section 4 chỉ vì thiếu tài liệu nghiệp vụ.
- **Upload ảnh fail "File not found"**: Tránh path có khoảng trắng. Copy ảnh vào `/tmp/rsd-screenshots/` trước khi upload. Trên Windows với Git Bash, nếu MCP vẫn không tìm thấy `/tmp/`, thử dùng path tuyệt đối Windows tương đương (ví dụ `d:/tmp/rsd-screenshots/`).
- **Duplicate title khi create page**: Confluence từ chối tạo page trùng tên. Dùng `confluence_update_page` thay vì tạo mới — thông báo cho user rằng đã update page có sẵn.
- **Page width nhỏ hơn sample**: Luôn thêm `page_width="full-width"` trong `create_page` và `update_page`. Nếu quên, page sẽ dùng fixed-width mặc định.

## Reference files

- `references/rsd-template.md` — Skeleton wiki markup đầy đủ 5 sections, copy & fill.
- `references/rsd-example-condensed.md` — Ví dụ rút gọn từ sample thực, dùng để học cách diễn đạt & mức độ chi tiết.
- `references/figma-to-mockup.md` — Cách biến Figma output thành caption mockup + rows bảng Mô tả màn hình.
- `references/confluence-upload.md` — Upload wiki format qua MCP, cách attach ảnh, fallback khi page quá lớn.
