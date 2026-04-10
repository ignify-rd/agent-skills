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

RSD **không phải là sáng tác**. Nó là tài liệu có cấu trúc cố định, nội dung phải **truy nguồn** được từ input user cung cấp. Bốn nguyên tắc:

1. **Không bịa dữ liệu.** Nếu template yêu cầu 1 trường (vd: "Điều kiện trước", "Quy tắc nghiệp vụ") mà input không nói rõ, hãy viết `[Cần xác nhận: ...]` thay vì phịa. Cuối cùng tổng hợp lại các chỗ này thành một danh sách để user review.
2. **Ưu tiên tham chiếu hơn copy-paste.** Khi có page Confluence đã mô tả sẵn (RSD cấp 1, bảng trạng thái, API spec...), link sang đó thay vì paste lại. Các RSD APP thường chỉ viết Section 4 (mô tả màn hình) còn lại tham chiếu sang RSD WEB.
3. **Tuân thủ template Việt hoá.** Toàn bộ heading, label bảng, từ khoá (Tác nhân, Luồng chính, Điều kiện trước, ...) phải khớp chính xác template — vì người review và tooling đều dựa vào đó.
4. **Tuyệt đối không dùng emoji/icon trong nội dung tài liệu.** Không được dùng bất kỳ emoji hay icon nào (✅ ❌ 🔘 🟡 🟢 🔴 ✏️ ▶ ✖ 📋 ⚠️ v.v.) trong nội dung bảng, mô tả màn hình, hay bất kỳ chỗ nào trong tài liệu RSD (trừ mục "Các điểm cần user xác nhận" ở cuối). Thay thế cụ thể:
   - Ma trận phân quyền: dùng **"x"** cho có quyền, để **trống ô** cho không có quyền
   - Trạng thái badge: viết text thuần (ví dụ: "Tạo nháp", "Chờ duyệt", "Hoạt động")
   - Tên nút chức năng: viết text không có icon (ví dụ: "Chỉnh sửa", "Phê duyệt", "Từ chối")

## Workflow end-to-end

Thực hiện tuần tự:

### Bước 1 — Gather inputs

Hỏi user (nếu chưa có đủ) về các đầu vào sau; nếu user đã paste một số link/ảnh thì xác nhận và bổ sung các phần còn thiếu:

- **Tên chức năng + platform (WEB/APP/BO)** — dùng để đặt title page.
- **Space Confluence + Parent page ID** — nơi tạo page mới.
- **URD** — link Confluence hoặc file mô tả yêu cầu nghiệp vụ gốc.
- **Figma** — link figma.com/design/... (dùng Figma MCP) hoặc ảnh đính kèm sẵn.
- **Page tham chiếu** (0..n):
  - RSD cấp 1 của module (thường có sơ đồ usecase, yêu cầu phi chức năng)
  - Bảng trạng thái, bảng mã lỗi
  - RSD WEB tương ứng (nếu đang làm RSD APP) — cực kỳ quan trọng vì phần lớn nội dung sẽ tham chiếu
- **Tên tác giả** cho bảng Phiên bản tài liệu (default: hỏi user).

Sau khi có đủ, đọc các page Confluence bằng `mcp__mcp-atlassian__confluence_get_page`. Nếu page quá lớn, tool sẽ lưu ra file và bạn đọc theo chunks. Với Figma link, dùng `mcp__plugin_figma_figma__get_design_context` và/hoặc `get_screenshot` theo `fileKey + nodeId` trích từ URL (convert `-` thành `:` trong nodeId).

### Bước 2 — Quyết định chiến lược nội dung

Trước khi viết, xác định:

- **Đây là RSD WEB hay RSD APP?** Nếu APP và đã có RSD WEB tương ứng, hầu hết các section 1.2, 2.2, 3, 5 sẽ **tham chiếu** (link) sang RSD WEB thay vì viết lại. Chỉ Section 4 (Mô tả màn hình) là viết mới theo Figma APP.
- **Đây là chức năng mới hay update?** Chức năng mới cần liệt kê đầy đủ các kết nối trong 2.2; update chỉ mô tả phần thay đổi.
- **Các quy tắc nghiệp vụ tới từ đâu?** Thường từ URD; nếu URD thiếu, đánh dấu `[Cần xác nhận]`.

### Bước 3 — Sinh nội dung theo template

Đọc `references/rsd-template.md` để lấy skeleton đầy đủ. Đọc `references/rsd-example-condensed.md` để thấy ví dụ cách điền. Đọc `references/figma-to-mockup.md` khi viết Section 4.

Viết tài liệu dưới dạng **Markdown** trước (dễ review, dễ convert). Các section:

1. **Phiên bản tài liệu** — bảng 1 hàng với Version=1.0, Lý do="Thêm mới", Date=hôm nay, Người sửa=tác giả, Mô tả="Dự thảo"
2. **Mục lục (TOC)** — Tạo TOC có anchor links để người đọc click nhảy đến từng section. Cú pháp Markdown:
   ```
   1. [Đặc tả/Tóm tắt usecase](#section-1)
   2. [Sơ đồ luồng xử lý](#section-2)
   3. [Ma trận phân quyền và phân bổ chức năng](#section-3)
   4. [Mô tả màn hình](#section-4)
   5. [Logic xử lý](#section-5)
   ```
   Trước mỗi heading section chính, đặt HTML anchor tương ứng:
   ```
   <a name="section-1"></a>
   ## 1. Đặc tả/Tóm tắt usecase
   ```
3. **Section 1** — 1.1 tham chiếu sơ đồ usecase cấp 1 (nếu có); 1.2 điền bảng đặc tả usecase từ URD. Các trường bắt buộc: Tên, Mã, Mô tả, Tác nhân, Mức độ ưu tiên, Điều kiện kích hoạt, Điều kiện trước, Kết quả mong muốn, Luồng chính, Luồng thay thế, Luồng ngoại lệ, Quy tắc nghiệp vụ, Yêu cầu phi chức năng.
4. **Section 2** — 2.1 sơ đồ luồng (nếu user cung cấp ảnh/Mermaid thì nhúng; không có thì bỏ trống + note). 2.2 bảng kết nối API nếu xác định được từ URD; nếu không có thông tin kết nối cụ thể và đây là RSD APP, hãy tham chiếu sang RSD WEB. 2.3 danh mục trạng thái — thường tham chiếu sang bảng trạng thái chung.
5. **Section 3** — ma trận phân quyền. Dùng "x" cho ô có quyền, để trống ô không có quyền. Không dùng emoji. Nếu URD không nêu chi tiết, tham chiếu sang RSD cấp 1 hoặc RSD WEB.
6. **Section 4 — Mô tả màn hình** (quan trọng nhất, viết chi tiết):
   - Chèn link Figma ở đầu (nếu có)
   - **a. Mockup màn hình**: Với mỗi state cần mô tả, viết 1 caption ngắn bằng text thuần (không emoji), rồi chèn ảnh theo một trong 2 cách:
     - **Nếu có Figma**: dùng `mcp__plugin_figma_figma__get_screenshot` tải ảnh về thư mục `./rsd-draft-<slug>/screenshots/`, chèn bằng `![caption](screenshots/ten-file.png)`. Sau khi tạo page Confluence, attach tất cả ảnh lên page.
     - **Nếu không có Figma/ảnh**: thay bằng dòng chú thích `*(Ảnh: chưa có - cần bổ sung từ Figma)*`
   - **KHÔNG** dùng blockquote (`>`) hay emoji để mô tả giao diện thay cho ảnh. Mô tả UI chỉ nằm trong bảng 4b, không phải trong phần mockup.
   - **b. Bảng mô tả màn hình**: mỗi row là một hạng mục UI với các cột **STT | Hạng mục | Kiểu hiển thị | Kiểu thao tác | Bắt buộc | Độ dài | Mô tả**. Phân nhóm bằng các row header in đậm (ví dụ "Cụm thông tin đầu trang", "Cụm tìm kiếm nâng cao", "Danh sách ...", "Phân trang"). Với mỗi element cần trả lời: placeholder, mặc định, validate, logic, ẩn/hiện, enable/disable. Xem `references/figma-to-mockup.md`.
7. **Section 5 — Logic xử lý** — bảng 3 cột **Thao tác | Tác nhân | Mô tả**. Mô tả phải bao gồm các bước Client gọi gì → Server kiểm tra gì → xử lý các nhánh. Nếu là RSD APP và có WEB tương ứng, tham chiếu sang WEB.

Trong suốt quá trình, khi gặp thông tin không chắc chắn → ghi `[Cần xác nhận: <câu hỏi cụ thể>]` inline.

### Bước 4 — Tổng hợp checklist các chỗ cần xác nhận

Cuối file draft, tạo một mục **"⚠️ Các điểm cần user xác nhận trước khi chính thức hoá"** liệt kê các `[Cần xác nhận]` đã đánh dấu trong body. Đây là thứ user sẽ review.

### Bước 5 — Upload lên Confluence

Dùng **confluence-skill** có sẵn trong hệ thống để upload (không reinvent):

```bash
python3 ~/.claude/skills/confluence-skill/scripts/upload_confluence_v2.py \
    <draft.md> --space <SPACE> --parent <PARENT_PAGE_ID> --title "<TITLE>"
```

Nếu `upload_confluence_v2.py` không hỗ trợ tạo mới (chỉ update), dùng MCP để tạo page rỗng trước lấy ID, rồi upload nội dung vào ID đó. Xem `references/confluence-upload.md` để biết 2 path.

Với ảnh Figma tải về local, `upload_confluence_v2.py` sẽ tự động attach nếu đường dẫn ảnh trong markdown là relative path.

**Title format** quan sát từ samples: `"<PLATFORM> <số thứ tự>. <Tên chức năng>_<Tên dự án>"` — ví dụ `"WEB 2.1. Danh sách thẻ tín dụng nội địa_Skymap"`, `"APP 2.1. Danh sách thẻ tín dụng nội địa_Skymap"`. Hỏi user nếu chưa rõ dự án/số thứ tự.

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
