---
name: rsd-generator
description: Sinh tài liệu RSD (Requirement Specification Document) mới trên Confluence bằng cách tổng hợp thông tin từ các page nguồn (RSD cũ, URD, Figma, tài liệu tham chiếu). Dùng skill này khi user nhắc tới "tạo RSD", "viết RSD", "generate RSD", "làm tài liệu đặc tả", "update tài liệu", "tạo tài liệu mới từ RSD cũ", "copy và cập nhật RSD", "tổng hợp RSD từ các tài liệu", hoặc đưa link page RSD/URD kèm yêu cầu tạo tài liệu mới — kể cả khi user không gọi đúng tên "RSD". Skill đọc các page nguồn, copy phần đã có, để trống phần chưa có, hỏi trước khi thêm thông tin mới, và tạo page Confluence mới trả về link.
---

# RSD Generator

Sinh một tài liệu RSD (Requirement Specification Document) mới trên Confluence bằng cách tổng hợp từ các page nguồn user cung cấp (RSD cũ, URD, Figma, bảng tham chiếu...). Output luôn là **page Confluence mới** — không sửa trực tiếp page cũ.

## Khi nào dùng skill này

- User muốn tạo RSD mới cho một màn hình / usecase / chức năng, có thể cung cấp thêm link RSD cũ (từ dự án khác hoặc phiên bản trước) làm nguồn tham chiếu.
- User muốn "update tài liệu" — tức là tạo page RSD mới từ RSD cũ: copy các section đã có, thay tên/thông tin mới, bổ sung phần còn thiếu.
- User cung cấp link Confluence (URD, RSD tham chiếu), link Figma, ảnh mockup, hoặc ghi chú yêu cầu nghiệp vụ riêng.
- Output: page Confluence mới hoàn chỉnh, kèm link.

## Quy tắc bất biến (đọc trước khi làm bất cứ điều gì)

**CLONE task KHÔNG có nghĩa là task đã xong.** Nếu Jira task được gắn nhãn "CLONE" hoặc tìm thấy trang Confluence cũ có nội dung tương tự → đó là tài liệu NGUỒN để copy từ, không phải output. Vẫn phải tạo page Confluence mới và chuyển Jira về "Done" chỉ sau khi page mới đã được tạo thành công.

**Không bao giờ chuyển Jira sang "Done" trước khi page Confluence mới được tạo và link được trả về cho user.**

## Nguyên tắc cốt lõi (đọc kỹ trước khi làm)

RSD **không phải là sáng tác**. Nó là tài liệu có cấu trúc cố định, nội dung phải **truy nguồn** được từ input user cung cấp. Năm nguyên tắc:

0. **Publish luôn — không draft.** Output phải là tài liệu hoàn chỉnh, publish trực tiếp lên Confluence. Không tạo file draft local. Khai thác tối đa mọi resource user cung cấp trước khi hỏi thêm. Bảng Phiên bản tài liệu dùng "Dự thảo" cho lần tạo đầu (theo convention thực tế của các dự án).

1. **Copy nguyên văn — không viết lại, không rút gọn, không sáng tác.** Mọi thông tin đã có trong tài liệu đính kèm, page nguồn, hoặc page Confluence trong Description/links → **copy nguyên văn vào đúng section tương ứng**. Các vi phạm bị cấm tuyệt đối:
   - **KHÔNG paraphrase, tóm tắt, hay viết lại** nội dung từ tài liệu nguồn
   - **KHÔNG rút gọn danh sách** — nếu nguồn có 13 API thì phải copy đủ 13, không được bỏ bớt thành 9
   - **KHÔNG thêm item mới không có trong nguồn** — cấm sáng tác thêm API, bước xử lý, vai trò, hay bất kỳ thông tin nào
   - **KHÔNG format lại bảng phức tạp thành bảng đơn giản hơn** — copy nguyên cấu trúc bảng từ nguồn
   - **KHÔNG chèn link "Tham chiếu tại..."** vào Section 2, 3, 5 khi nội dung đó ĐÃ có trong tài liệu nguồn — phải copy thẳng vào
   
   Chỉ viết mới những phần thực sự chưa có thông tin. Nếu thông tin nào thực sự chưa xác định được: **để trống cell đó** — KHÔNG điền placeholder như `Chờ xác nhận từ BA`, KHÔNG ghi `[Cần xác nhận]`. Ghi lại danh sách nội bộ để hỏi user trong chat sau khi upload.

2. **Ưu tiên tham chiếu hơn copy-paste — chỉ áp dụng khi tài liệu nguồn CÓ LINK sang page khác.** Khi page nguồn (RSD cũ, Luồng xử lý...) bản thân nó đã link sang một page Confluence khác (RSD cấp 1, bảng trạng thái, API spec...) → link sang page đó thay vì paste lại nội dung. Nguyên tắc này **KHÔNG áp dụng** khi nội dung đó là nội dung inline trong tài liệu nguồn — trường hợp đó phải copy. Các RSD APP thường chỉ viết Section 4 (mô tả màn hình) còn lại tham chiếu sang RSD WEB.
3. **Tuân thủ template Việt hoá — dùng Confluence Storage Format (XHTML), không dùng Markdown.** Toàn bộ heading, label bảng, từ khoá phải khớp chính xác template. Quy tắc heading và bảng:
   - **Heading section 1–5**: dùng `<h2>`, không cần anchor. Ví dụ: `<h2>1. Đặc tả/Tóm tắt usecase</h2>`. Confluence tự tạo anchor từ heading text.
   - **Heading sub-section** (1.1, 1.2, 2.1, ...): dùng `<h3>`. Ví dụ: `<h3>1.1. Sơ đồ Usecase</h3>`
   - **Không dùng `<hr/>`** để ngăn cách section — chỉ dùng heading h2 để phân tách.
   - **Bảng** dùng `<table data-layout="full-width"><tbody><tr><th><p>col</p></th>...` cho header row, `<tr><td><p>cell</p></td>...` cho data row. **BẮT BUỘC có `data-layout="full-width"` trên mọi `<table>` — thiếu thì table sẽ hiển thị hẹp.**
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
| **Page nguồn (RSD cũ / tài liệu tương tự)** — link Confluence page dùng làm nguồn tổng hợp | Không | Bỏ qua; nếu không có thì tạo mới hoàn toàn theo template |
| **Ghi chú / Description** — yêu cầu nghiệp vụ riêng, điều chỉnh cụ thể cho tài liệu này (ví dụ: "chỉ update section 2", "thay tên dự án sang BIDV", "bỏ section phân quyền") | Không | Bỏ qua; xử lý theo flow chuẩn |
| Ảnh mockup hoặc Figma link | Không | Copy từ page nguồn nếu có; nếu không có thì để trống, không sinh placeholder |
| URD (link Confluence, Jira issue...) | Không | Copy từ page nguồn nếu có; nếu không có thì để trống section đó |
| Page tham chiếu (RSD cấp 1, bảng trạng thái, RSD WEB...) | Không | Bỏ qua, điền khi user cung cấp |
| Tên tác giả | Không | Dùng tên user hiện tại hoặc để trống |

**Quy trình đọc resource:**

**0a. Đọc page nguồn trước tiên** (nếu user cung cấp link RSD cũ / tài liệu tương tự):
- Gọi `mcp__mcp-atlassian__confluence_get_page` để lấy toàn bộ nội dung page nguồn.
- Map từng section của page nguồn vào đúng section tương ứng trong template mới.
- **Quy tắc copy:** section nào trong page nguồn (hoặc tài liệu đính kèm, page Confluence trong Description/links) đã có nội dung → **copy nguyên văn, không viết lại, không paraphrase, không tóm tắt**. Chỉ thay tên dự án/chức năng nếu Ghi chú chỉ định rõ. Section nào trống trong page nguồn → để trống trong tài liệu mới, KHÔNG tự điền.
- Áp dụng **Ghi chú / Description** của user (nếu có) để điều chỉnh: thay tên, bỏ section, cập nhật thông tin cụ thể...
- **Hỏi user trước khi thêm bất kỳ thông tin mới nào** không có trong page nguồn và không được nêu trong Ghi chú.

**0b. Luôn scan `./screenshots/` trước tiên** — ngay khi bắt đầu, trước khi xử lý bất kỳ input nào khác:
```bash
ls ./screenshots/ 2>/dev/null || ls /tmp/rsd-screenshots/ 2>/dev/null
```
Nếu có file ảnh → đây là nguồn ảnh chính cho Section 4a. Nếu ảnh nằm trong thư mục có khoảng trắng hoặc ký tự đặc biệt, copy sang `/tmp/rsd-screenshots/` trước khi dùng. Không cần user đính kèm lại hay cung cấp thêm nguồn nào khác.

- **Figma link**: `mcp__plugin_figma_figma__get_design_context` (lấy element-level) + `get_screenshot` cho từng state cần mô tả (default, empty, error, dropdown mở...). Parse URL: `figma.com/design/{fileKey}/...?node-id={nodeId}` — convert `-` thành `:` trong nodeId. Tải ảnh về `./screenshots/`.
- **Ảnh đính kèm trên trang Confluence nguồn** — **KHÔNG dùng curl với Basic Auth** (sẽ nhận file 0 bytes). Thay vào đó dùng MCP theo thứ tự ưu tiên:
  1. `mcp__mcp-atlassian__confluence_download_attachment(page_id="...", attachment_id="...", download_dir="./screenshots/")` — lấy `attachment_id` bằng cách gọi `confluence_get_attachments(page_id="...")` trước
  2. Hoặc `mcp__mcp-atlassian__confluence_download_content_attachments(page_id="...", download_dir="./screenshots/")` để tải hết tất cả ảnh trong page một lượt
  3. Nếu ảnh có trong Jira ticket kèm theo: dùng `mcp__mcp-atlassian__jira_download_attachments(issue_key="...", download_dir="./screenshots/")`
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

- **Có page nguồn không?**
  - **Có page nguồn** → ưu tiên copy từ page nguồn. Phần nào nguồn có → copy. Phần nào nguồn trống → để trống trong tài liệu mới. Chỉ bổ sung thêm nếu có URD/Figma/Ghi chú mới chỉ định rõ, và **phải hỏi user trước** nếu thông tin đó không có trong nguồn và không được nêu trong Ghi chú.
  - **Không có page nguồn** → tạo mới theo template. Section nào có input → điền. Section nào không có input → để trống (không điền placeholder tự động).
- **Đây là RSD WEB hay RSD APP?** Nếu APP và đã có RSD WEB tương ứng, sections 1.2, 2.2, 3, 5 sẽ **tham chiếu** (link) sang RSD WEB. Chỉ Section 4 là viết mới theo Figma/ảnh APP.
- **Có URD/tài liệu không?** Nếu có → đọc hết và extract thông tin cho sections 1, 2, 3, 5. Nếu không → để trống các section thiếu thông tin (KHÔNG điền `Chờ xác nhận từ BA` hay placeholder tương tự).
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

<!-- Bảng — BẮT BUỘC data-layout="full-width" cho mọi table -->
<table data-layout="full-width"><tbody>
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

<!-- TOÀN BỘ PAGE BẮT BUỘC bọc trong 1 <ac:layout> duy nhất — cấu trúc 3 section -->
<!-- Tables nằm ngoài layout wrapper sẽ render hẹp (không full-width như sample) -->
<ac:layout>

<!-- Section 1: fixed-width — chứa version table, TOC, sections 1–3, đầu section 4 -->
<ac:layout-section ac:breakout-mode="default" ac:type="fixed-width">
<ac:layout-cell>
<p>...version table, TOC, sections 1–3, heading 4, Figma link, "a. Mockup màn hình"...</p>
</ac:layout-cell>
</ac:layout-section>

<!-- Section 2: wide — chứa image grid Section 4a -->
<!-- WEB: three_equal width=360 | APP: four_equal width=200 | Dialog: two_equal width=500 -->
<ac:layout-section ac:breakout-mode="wide" ac:breakout-width="1174" ac:type="three_equal">
<ac:layout-cell><p>Caption state 1</p>
<ac:image ac:width="360"><ri:attachment ri:filename="screen-01.png"/></ac:image></ac:layout-cell>
<ac:layout-cell><p>Caption state 2</p>
<ac:image ac:width="360"><ri:attachment ri:filename="screen-02.png"/></ac:image></ac:layout-cell>
<ac:layout-cell><p>Caption state 3</p>
<p><em>(Ảnh: chưa có - cần bổ sung)</em></p></ac:layout-cell>
</ac:layout-section>

<!-- Section 3: fixed-width — chứa bảng 4b + section 5 -->
<ac:layout-section ac:breakout-mode="default" ac:type="fixed-width">
<ac:layout-cell>
<p>...bảng mô tả màn hình 4b, section 5 logic xử lý...</p>
</ac:layout-cell>
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
<table data-layout="full-width"><tbody>
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
   - **a. Mockup màn hình** — heading + Figma link + nav text đặt trong `fixed-width` section (trước image grid). Image grid là `wide` section riêng trong outer layout. **KHÔNG** bọc image grid trong `<ac:layout>` riêng — nó là sibling section của outer layout:
     - Số cột theo platform:
       - **WEB**: `ac:type="three_equal"`, image `ac:width="360"`
       - **APP**: `ac:type="four_equal"`, image `ac:width="200"`
       - **Dialog/Detail**: `ac:type="two_equal"`, image `ac:width="500"`
     - Ví dụ image grid WEB (chỉ phần `<ac:layout-section>` — nằm trong outer layout):
       ```xml
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
       ```
     - **Luôn sinh ra section image grid dù không có ảnh nào** — dùng `<em>(Ảnh: chưa có - cần bổ sung)</em>` cho mỗi state
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

Trong suốt quá trình: nếu thông tin **có thể suy luận hợp lý từ context hoặc lấy được từ page nguồn** → điền trực tiếp. Nếu không thể xác định → **để trống cell** (`<td><p> </p></td>`), ghi nội bộ để hỏi user trong chat. KHÔNG điền placeholder như `Chờ xác nhận từ BA` hay `[Cần xác nhận]` — để trống thì rõ ràng hơn.

### Bước 3b — Kiểm tra tính toàn vẹn dữ liệu trước khi upload

Trước khi upload, tự kiểm tra lại nội dung đã sinh:

- **Section 2.1 (danh sách API/luồng)**: Đếm số lượng API/bước trong tài liệu nguồn, đếm số lượng trong nội dung vừa sinh → phải khớp chính xác. Nếu lệch → đọc lại nguồn và bổ sung đủ trước khi tiếp tục.
- **Section 5 (logic xử lý)**: Kiểm tra cấu trúc bảng có khớp với nguồn không (số cột, số nhóm dòng). Nếu nguồn có nhiều sub-table/block → phải copy đủ, không gộp.
- **Mọi section copy từ nguồn**: Nếu phát hiện mình đã tóm tắt, format lại, hay bỏ bớt bất kỳ nội dung nào → phải làm lại section đó với nội dung gốc nguyên văn.

Nếu phát hiện sai lệch mà không thể đọc lại nguồn (token limit, page mất...): **comment trên Jira báo rõ phần nào không thể xác minh**, không upload tài liệu chứa nội dung chưa được xác nhận là khớp 100%.

### Bước 4 — Tổng hợp checklist và hỏi user trước khi upload

Nếu có thông tin chưa xác định được (cell để trống, section không có nguồn): ghi lại danh sách nội bộ. Trước khi upload, **hỏi user** về những phần này — đặc biệt nếu có thông tin mới không có trong page nguồn mà bot muốn thêm vào:

```
Trước khi tạo page, mình cần xác nhận thêm:
- [Section X.Y] <câu hỏi cụ thể>
- [Section X.Y] Muốn thêm <thông tin X> — bạn có muốn bổ sung không?
```

Nếu user xác nhận → bổ sung vào nội dung rồi upload. Nếu không → để trống và upload luôn.

Nếu không có điểm nào cần hỏi → bỏ qua bước này, upload thẳng.

### Bước 5 — Upload lên Confluence

Dùng MCP `mcp__mcp-atlassian__confluence_create_page` với `content_format="storage"`:

```
mcp__mcp-atlassian__confluence_create_page(
    space_key="<SPACE>",
    title="<TITLE>",
    content="<nội dung storage format XHTML>",
    content_format="storage",
    parent_id="<PARENT_PAGE_ID>"
)
```

Full-width được đảm bảo bằng content (outer `<ac:layout>` + `data-layout="full-width"` trên mọi table) — không cần `page_width` parameter.

Nếu đã có page cùng tên (duplicate), dùng `confluence_update_page` thay vì tạo mới:
```
mcp__mcp-atlassian__confluence_update_page(
    page_id="<PAGE_ID>",
    title="<TITLE>",
    content="<nội dung storage format XHTML>",
    content_format="storage",
    version_comment="Cập nhật nội dung RSD"
)
```
**Không truyền `page_width`** — `update_page` không hỗ trợ parameter này (validation error).

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

Các section để trống (chưa có thông tin):
- [Section X.Y] <tên section>
```

Nếu không có section nào để trống thì bỏ phần đó đi — chỉ trả link.

## Xử lý lỗi thường gặp

- **Figma MCP trả quá nhiều dữ liệu cho 1 node lớn**: thu hẹp bằng cách truyền đúng nodeId của từng màn con, không lấy node cha.
- **Confluence page quá lớn (token limit exceeded, >50KB)**: KHÔNG cố đọc toàn bộ page vào bộ nhớ. Chiến lược xử lý theo thứ tự:
  1. Gọi `confluence_get_page` → nếu bị lỗi token limit, tool sẽ lưu nội dung ra file tạm (ví dụ `/tmp/confluence_page_<id>.txt`)
  2. Dùng bash để grep heading trước: `grep -n "<h[23]>" /tmp/confluence_page_<id>.txt | head -50` → xác định offset của từng section
  3. Đọc từng section cần thiết bằng `sed -n '<start>,<end>p' /tmp/confluence_page_<id>.txt > /tmp/section_<name>.txt`
  4. Đọc file tạm đó bằng Read tool với `offset` và `limit` thích hợp
  5. **KHÔNG viết script Python để xử lý** — dùng bash sed/grep là đủ và nhanh hơn
  6. Khi copy nội dung section: vẫn phải copy đủ tất cả dòng, không bỏ bớt do page lớn
- **Upload fail do size**: nếu content >100KB thì tạo page rỗng trước rồi update — xem `references/confluence-upload.md`.
- **Ảnh không hiện sau upload**: kiểm tra `ri:filename` trong `<ac:image>` khớp chính xác tên file attach (case-sensitive).
- **Dòng image placeholder bị bỏ**: KHÔNG được bỏ `<p><em>(Ảnh: chưa có - cần bổ sung)</em></p>` — mỗi caption phải có `<ac:image>` hoặc placeholder ngay bên dưới.
- **Section 4 bị thiếu khi không có URD**: Section 4 không phụ thuộc URD — sinh từ ảnh/Figma. Không được skip Section 4 chỉ vì thiếu tài liệu nghiệp vụ.
- **Upload ảnh fail "File not found"**: Tránh path có khoảng trắng. Copy ảnh vào `/tmp/rsd-screenshots/` trước khi upload. Trên Windows với Git Bash, nếu MCP vẫn không tìm thấy `/tmp/`, thử dùng path tuyệt đối Windows tương đương (ví dụ `d:/tmp/rsd-screenshots/`).
- **Duplicate title khi create page**: Confluence từ chối tạo page trùng tên. Dùng `confluence_update_page` thay vì tạo mới — thông báo cho user rằng đã update page có sẵn.
- **Tables/text bị hẹp**: Hai nguyên nhân phổ biến — (1) thiếu `data-layout="full-width"` trên `<table>`: phải có trên **mọi** table trong document; (2) content không bọc trong outer `<ac:layout>`: tables ngoài layout wrapper render hẹp. BẮT BUỘC dùng cấu trúc 3 section: `fixed-width → wide (image grid) → fixed-width` trong 1 `<ac:layout>` duy nhất. Xem `references/rsd-template.md`.
- **`page_width` parameter trong `update_page`**: MCP tool không hỗ trợ — ĐỪNG truyền vào (validation error). Full-width đã đảm bảo bằng `data-layout="full-width"` trong content.

## Reference files

- `references/rsd-template.md` — Skeleton wiki markup đầy đủ 5 sections, copy & fill.
- `references/rsd-example-condensed.md` — Ví dụ rút gọn từ sample thực, dùng để học cách diễn đạt & mức độ chi tiết.
- `references/figma-to-mockup.md` — Cách biến Figma output thành caption mockup + rows bảng Mô tả màn hình.
- `references/confluence-upload.md` — Upload wiki format qua MCP, cách attach ảnh, fallback khi page quá lớn.
