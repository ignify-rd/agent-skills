# RSD Template (skeleton) — Confluence Storage Format

Đây là skeleton đầy đủ của 1 page RSD viết bằng **Confluence Storage Format** (XHTML + ac: macros). Upload lên Confluence bằng MCP với `content_format="storage"`.

---

## Cấu trúc page (storage format)

```xml
<!-- PHIÊN BẢN TÀI LIỆU -->
<p><strong>Phiên bản tài liệu</strong></p>
<table><tbody>
<tr><th><p>Version</p></th><th><p>Lý do</p></th><th><p>Date</p></th><th><p>Người sửa</p></th><th><p>Mô tả</p></th></tr>
<tr><td><p>1.0</p></td><td><p>Thêm mới</p></td><td><p>YYYY-MM-DD</p></td><td><p>Tác giả</p></td><td><p>Dự thảo</p></td></tr>
</tbody></table>

<!-- MỤC LỤC -->
<p><strong>Mục lục</strong></p>
<ac:structured-macro ac:name="toc"><ac:parameter ac:name="style">none</ac:parameter></ac:structured-macro>

<!-- SECTION 1 -->
<h2>1. Đặc tả/Tóm tắt usecase</h2>

<h3>1.1. Sơ đồ Usecase (nếu có)</h3>
<p>Tham chiếu tại <a href="URL">link RSD cấp 1 — section sơ đồ use case</a></p>

<h3>1.2. Đặc tả/tóm tắt Usecase</h3>
<table><tbody>
<tr><th><p>Hạng mục</p></th><th><p>Nội dung</p></th></tr>
<tr><td><p><strong>Tên</strong></p></td><td><p>Tên usecase, ví dụ: Danh sách thẻ tín dụng nội địa</p></td></tr>
<tr><td><p><strong>Mã</strong></p></td><td><p>để trống nếu chưa có</p></td></tr>
<tr><td><p><strong>Mô tả</strong></p></td><td><p>1-2 câu mô tả ngắn gọn mục đích</p></td></tr>
<tr><td><p><strong>Tác nhân</strong></p></td><td><p>Tác nhân chủ động: vai trò user<br/>Tác nhân thụ động: các hệ thống backend liên quan</p></td></tr>
<tr><td><p><strong>Mức độ ưu tiên</strong></p></td><td><p>High / Medium / Low</p></td></tr>
<tr><td><p><strong>Điều kiện kích hoạt</strong></p></td><td><p>Khi nào user kích hoạt chức năng này</p></td></tr>
<tr><td><p><strong>Điều kiện trước</strong></p></td><td><p>1. User đăng nhập thành công<br/>2. User được phân quyền ...</p></td></tr>
<tr><td><p><strong>Kết quả mong muốn</strong></p></td><td><p>Hệ thống hiển thị / xử lý gì</p></td></tr>
<tr><td><p><strong>Luồng chính</strong></p></td><td><p>1. Bước 1<br/>2. Bước 2<br/>3. Bước 3</p></td></tr>
<tr><td><p><strong>Luồng thay thế</strong></p></td><td><p>N/A hoặc mô tả</p></td></tr>
<tr><td><p><strong>Luồng ngoại lệ</strong></p></td><td><p>1. ...<br/>2. ...</p></td></tr>
<tr><td><p><strong>Quy tắc nghiệp vụ (nếu có)</strong></p></td><td><p>Rules business phải tuân — phân quyền dữ liệu, logic trạng thái...</p></td></tr>
<tr><td><p><strong>Yêu cầu phi chức năng (nếu có)</strong></p></td><td><p>Theo yêu cầu phi chức năng chung tại RSD cấp 1</p></td></tr>
</tbody></table>

<!-- SECTION 2 -->
<h2>2. Sơ đồ luồng xử lý</h2>

<h3>2.1. Sơ đồ luồng xử lý</h3>
<ac:structured-macro ac:name="noformat"><ac:plain-text-body><![CDATA[
Sơ đồ luồng ASCII hoặc để trống + ghi chú "Sẽ bổ sung"
]]></ac:plain-text-body></ac:structured-macro>

<h3>2.2. Yêu cầu với các kết nối phát sinh mới/ cần chỉnh sửa trong luồng</h3>
<ac:structured-macro ac:name="info"><ac:rich-text-body>
<p>Hệ thống mới, chức năng mới: Liệt kê toàn bộ các kết nối được sử dụng tại chức năng này.<br/>
Với các kết nối mới/ cần chỉnh sửa: mô tả yêu cầu của nghiệp vụ với các kết nối này.</p>
</ac:rich-text-body></ac:structured-macro>
<table><tbody>
<tr><th><p>Bước</p></th><th><p>Tên kết nối</p></th><th><p>Trạng thái sẵn sàng</p></th><th><p>Backend cung cấp kết nối</p></th><th><p>Phương thức tích hợp</p></th><th><p>Luồng gọi API/ Luồng đi của kết nối</p></th><th><p>Mô tả kết nối</p></th></tr>
<tr><td><p>Mô tả bước</p></td><td><p>Tên API</p></td><td><p>Có sẵn / Phát sinh mới / Cần chỉnh sửa</p></td><td><p>Module backend</p></td><td><p>API / DBlink / Job</p></td><td><p>Client → Server → Core</p></td><td><p>Endpoint + chức năng</p></td></tr>
</tbody></table>

<h3>2.3. Danh mục hoặc sơ đồ trạng thái</h3>
<h4>2.3.1. Tên đối tượng, ví dụ: Trạng thái của thẻ</h4>
<p>Theo mô tả tại: <a href="URL">tên tài liệu trạng thái</a></p>

<!-- SECTION 3 -->
<h2>3. Ma trận phân quyền và phân bổ chức năng</h2>
<ac:structured-macro ac:name="info"><ac:rich-text-body>
<p>Mô tả tính năng phân bổ ở các FO/BO/iconnect và phân quyền người dùng (khởi tạo, sửa, xác nhận, duyệt).<br/>
Dùng "x" cho ô có quyền, để trống ô không có quyền. Không dùng emoji.</p>
</ac:rich-text-body></ac:structured-macro>

<p><strong>Cho iBank / FO (nhiều kênh):</strong></p>
<table><tbody>
<tr><th><p>STT</p></th><th><p>Usecase (chức năng cấp 3)</p></th><th><p>MB</p></th><th><p>IB</p></th><th><p>BO</p></th><th><p>ERP (web/app)</p></th><th><p>ERP (H2H)</p></th><th><p>Maker-KH</p></th><th><p>Checker-KH</p></th><th><p>Inquiry-KH</p></th><th><p>Admin-KH</p></th><th><p>GDV CN</p></th><th><p>KSV CN</p></th><th><p>GDV TSC</p></th><th><p>KSV TSC</p></th><th><p>Inquiry-BO</p></th><th><p>Nhóm quyền khác còn lại</p></th><th><p>Mô tả</p></th></tr>
<tr><td><p>1</p></td><td><p><strong>Tên nhóm chức năng</strong></p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
<tr><td><p>1.1</p></td><td><p>Chức năng cấp 3</p></td><td><p> </p></td><td><p>x</p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p>x</p></td><td><p>x</p></td><td><p>x</p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p>Ghi chú phân giao</p></td></tr>
</tbody></table>

<p><strong>Cho BO nội bộ / BackOffice (KSV/GDV):</strong></p>
<table><tbody>
<tr><th><p>STT</p></th><th><p>Chức năng</p></th><th><p>Nơi phân bổ</p></th><th><p>KSV</p></th><th><p>GDV</p></th><th><p>Mô tả</p></th></tr>
<tr><td><p>1</p></td><td><p><strong>Tên nhóm chức năng</strong></p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
<tr><td><p>1.1</p></td><td><p>Chức năng cấp 3</p></td><td><p>BO</p></td><td><p>x</p></td><td><p>x</p></td><td><p>Ghi chú</p></td></tr>
</tbody></table>
<p><em>(Nếu là RSD APP có RSD WEB tương ứng, thay toàn bộ bảng bằng: "Tham chiếu tại <a href="URL">RSD WEB</a>")</em></p>

<!-- SECTION 4 -->
<h2>4<strong>. Mô tả màn hình</strong></h2>

<p>Figma: <a href="https://figma.com/design/...">Tên Figma file</a></p>

<p><strong>a. Mockup màn hình</strong></p>
<p>Đường dẫn: Cách truy cập chức năng, ví dụ: Menu Thẻ &gt; Danh sách thẻ &gt; tab ...</p>

<!-- WEB: three_equal | APP: four_equal | Dialog: two_equal -->
<!-- WEB image width=360 | APP image width=200 | Dialog image width=500 -->
<ac:layout>
<ac:layout-section ac:breakout-mode="wide" ac:breakout-width="1174" ac:type="three_equal">
<ac:layout-cell>
<p>Caption state 1 — text thuần, không emoji, ví dụ: Màn hình danh sách khi có dữ liệu</p>
<ac:image ac:width="360"><ri:attachment ri:filename="screen-01-default.png"/></ac:image>
<p>Caption state 2 — ví dụ: Màn hình khi không có dữ liệu</p>
<p><em>(Ảnh: chưa có - cần bổ sung)</em></p>
</ac:layout-cell>
<ac:layout-cell>
<p>Caption state 3 — ví dụ: Màn hình khi mở Tìm kiếm nâng cao</p>
<ac:image ac:width="360"><ri:attachment ri:filename="screen-03-search.png"/></ac:image>
<p>Caption state 4 — ví dụ: Màn hình kết quả tìm kiếm</p>
<p><em>(Ảnh: chưa có - cần bổ sung)</em></p>
</ac:layout-cell>
<ac:layout-cell>
<p>Caption state 5 — ví dụ: Màn hình khi chọn dropdown</p>
<p><em>(Ảnh: chưa có - cần bổ sung)</em></p>
</ac:layout-cell>
</ac:layout-section>
</ac:layout>

<p><strong>b. Mô tả màn hình</strong></p>
<table><tbody>
<tr><th><p> </p></th><th><p><strong>Hạng mục</strong></p></th><th><p><strong>Kiểu hiển thị</strong></p></th><th><p><strong>Kiểu thao tác</strong></p></th><th><p><strong>Bắt buộc</strong></p></th><th><p><strong>Độ dài</strong></p></th><th><p><strong>Mô tả</strong></p></th></tr>
<tr><td><p>1</p></td><td><p><strong>Cụm thông tin đầu trang</strong></p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
<tr><td><p>2</p></td><td><p>Element, ví dụ: Breadcrumb</p></td><td><p>Label / Button / Textbox / Droplist / Image / Tab ...</p></td><td><p>Read-only / Click / Input / Select</p></td><td><p>Y / N / -</p></td><td><p>max length hoặc -</p></td><td><p>Placeholder + mặc định + validate + logic + ẩn/hiện + enable/disable</p></td></tr>
<tr><td><p>3</p></td><td><p><strong>Cụm tìm kiếm nhanh</strong></p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
<tr><td><p>4</p></td><td><p>...</p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
<tr><td><p>5</p></td><td><p><strong>Cụm tìm kiếm nâng cao</strong></p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
<tr><td><p>6</p></td><td><p>...</p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
<tr><td><p>7</p></td><td><p><strong>Danh sách ...</strong></p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
<tr><td><p>8</p></td><td><p>...</p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
<tr><td><p>9</p></td><td><p><strong>Phân trang</strong></p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
<tr><td><p>10</p></td><td><p>...</p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td><td><p> </p></td></tr>
</tbody></table>

<!-- SECTION 5 -->
<h2>5. Logic xử lý tên action chính, ví dụ: khi truy cập menu Thẻ &gt; Danh sách thẻ</h2>
<table><tbody>
<tr><th><p><strong>Thao tác</strong></p></th><th><p><strong>Tác nhân</strong></p></th><th><p><strong>Mô tả</strong></p></th></tr>
<tr><td><p>Trigger user, ví dụ: User chọn tab Thẻ tín dụng nội địa</p></td><td><p>Client web/app</p></td><td><p><strong>1/ Gửi yêu cầu lấy danh sách qua API</strong><br/>Endpoint: ...<br/>Payload: ...</p></td></tr>
<tr><td><p> </p></td><td><p>Server Module</p></td><td><p><strong>1/ Kiểm tra tính hợp lệ input</strong><br/>- Không hợp lệ: trả lỗi INPUT_01<br/>- Hết phiên: SESSION_TIMEOUT_01<br/>- Hợp lệ: chuyển bước 2<br/><br/><strong>2/ Kiểm tra phân quyền</strong><br/>...<br/><br/><strong>3/ ...</strong></p></td></tr>
<tr><td><p> </p></td><td><p>Client web/app</p></td><td><p><strong>Nhận phản hồi</strong><br/>- Lỗi phân quyền CARD.003: hiển thị popup "Người dùng chưa được phân quyền..."<br/>- Thành công: hiển thị danh sách theo mô tả màn hình</p></td></tr>
</tbody></table>
```

---

## Quy tắc quan trọng khi điền template

1. **Không dùng emoji** trong bất kỳ cell hay đoạn text nào
2. **TOC**: `<ac:structured-macro ac:name="toc"><ac:parameter ac:name="style">none</ac:parameter></ac:structured-macro>` — không cần tạo thủ công
3. **Xuống dòng trong cell bảng** dùng `<br/>`, KHÔNG dùng `\\`
4. **Text trong cell phải bọc trong `<p>`**: `<td><p>nội dung</p></td>`
5. **Cell rỗng**: `<td><p> </p></td>` — có `<p> </p>` bên trong
6. **Link**: `<a href="URL">Text</a>` (không dùng wiki `[Text|URL]`)
7. **Ảnh attachment**: `<ac:image ac:width="360"><ri:attachment ri:filename="file.png"/></ac:image>`
8. **Image grid Section 4a**: BẮT BUỘC dùng `<ac:layout><ac:layout-section ac:breakout-mode="wide" ac:breakout-width="1174" ac:type="three_equal">` — KHÔNG dùng `{section}/{column}` wiki macro
9. **Section 4 heading**: `<h2>4<strong>. Mô tả màn hình</strong></h2>` — số `4` không bold
10. **Row group header bảng 4b**: `<tr><td><p>STT</p></td><td><p><strong>Tên cụm</strong></p></td><td><p> </p></td>...(5 cells)</tr>`
11. **KHÔNG ghi annotation trong document** — dùng `Chờ xác nhận từ BA` trong cell. Báo cáo trong chat reply sau upload.
12. **Escape HTML chars trong nội dung**: `&amp;` cho `&`, `&lt;` cho `<`, `&gt;` cho `>`
