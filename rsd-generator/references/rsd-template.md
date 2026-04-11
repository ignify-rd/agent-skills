# RSD Template (skeleton) — Confluence Wiki Markup

Đây là skeleton đầy đủ của 1 page RSD viết bằng **Confluence Wiki Markup**. Copy toàn bộ, điền dữ liệu từ URD/Figma. Giữ nguyên heading và label bảng (tiếng Việt, có dấu).

Upload lên Confluence bằng MCP với `content_format="wiki"`.

---

## Template wiki (copy phần dưới đây vào content)

```wiki
*Phiên bản tài liệu*

||Version||Lý do||Date||Người sửa||Mô tả||
|1.0|Thêm mới|{{YYYY-MM-DD}}|{{Tác giả}}|Dự thảo|

*Mục lục*

{toc:style=none}

h2. 1. Đặc tả/Tóm tắt usecase

h3. 1.1. Sơ đồ Usecase (nếu có)

Tham chiếu tại [{{link RSD cấp 1 — section sơ đồ use case}}|{{URL}}]

h3. 1.2. Đặc tả/tóm tắt Usecase

||Hạng mục||Nội dung||
|*Tên*|{{Tên usecase, ví dụ: Danh sách thẻ tín dụng nội địa}}|
|*Mã*|{{để trống nếu chưa có}}|
|*Mô tả*|{{1-2 câu mô tả ngắn gọn mục đích}}|
|*Tác nhân*|Tác nhân chủ động: {{vai trò user}} \\ Tác nhân thụ động: {{các hệ thống backend liên quan}}|
|*Mức độ ưu tiên*|High / *Medium* / Low|
|*Điều kiện kích hoạt*|{{Khi nào user kích hoạt chức năng này}}|
|*Điều kiện trước*|1. User đăng nhập thành công \\ 2. User được phân quyền ...|
|*Kết quả mong muốn*|{{Hệ thống hiển thị / xử lý gì}}|
|*Luồng chính*|1. {{Bước 1}} \\ 2. {{Bước 2}} \\ 3. {{Bước 3}}|
|*Luồng thay thế*|N/A hoặc mô tả|
|*Luồng ngoại lệ*|1. ... \\ 2. ...|
|*Quy tắc nghiệp vụ (nếu có)*|{{Rules business phải tuân — phân quyền dữ liệu, logic trạng thái...}}|
|*Yêu cầu phi chức năng (nếu có)*|Theo yêu cầu phi chức năng chung tại RSD cấp 1|

h2. 2. Sơ đồ luồng xử lý

h3. 2.1. Sơ đồ luồng xử lý

Nếu có ảnh sơ đồ: !ten-anh-so-do.png!

Nếu không có ảnh, dùng khối noformat bên dưới:

{noformat}
{{Sơ đồ luồng ASCII hoặc để trống + ghi chú "Sẽ bổ sung"}}
{noformat}

h3. 2.2. Yêu cầu với các kết nối phát sinh mới/ cần chỉnh sửa trong luồng

{info}
Hệ thống mới, chức năng mới: Liệt kê toàn bộ các kết nối được sử dụng tại chức năng này.
Với các kết nối mới/ cần chỉnh sửa: mô tả yêu cầu của nghiệp vụ với các kết nối này.
{info}

||Bước||Tên kết nối||Trạng thái sẵn sàng||Backend cung cấp kết nối||Phương thức tích hợp||Luồng gọi API/ Luồng đi của kết nối||Mô tả kết nối||
|{{Mô tả bước}}|{{Tên API}}|Có sẵn / Phát sinh mới / Cần chỉnh sửa|{{Module backend}}|API / DBlink / Job|{{Client → Server → Core}}|{{Endpoint + chức năng}}|

h3. 2.3. Danh mục hoặc sơ đồ trạng thái

h4. 2.3.1. {{Tên đối tượng, ví dụ: Trạng thái của thẻ}}

Theo mô tả tại: [{{tên tài liệu trạng thái}}|{{URL}}]

h2. 3. Ma trận phân quyền và phân bổ chức năng

{info}
Mô tả tính năng phân bổ ở các FO/BO/iconnect và phân quyền người dùng (khởi tạo, sửa, xác nhận, duyệt).
Dùng "x" cho ô có quyền, để trống ô không có quyền. Không dùng emoji.
{info}

*Cho iBank / FO (nhiều kênh):*

||STT||Usecase (chức năng cấp 3)||MB||IB||BO||ERP (web/app)||ERP (H2H)||Maker-KH||Checker-KH||Inquiry-KH||Admin-KH||GDV CN||KSV CN||GDV TSC||KSV TSC||Inquiry-BO||Nhóm quyền khác còn lại||Mô tả||
|1|*{{Tên nhóm chức năng}}*| | | | | | | | | | | | | | | | |
|1.1|{{Chức năng cấp 3}}|x|x| | | |x|x|x|x| | | | | | |{{Ghi chú phân giao}}|

*Cho BO nội bộ / BackOffice (KSV/GDV):*

||STT||Chức năng||Nơi phân bổ||KSV||GDV||Mô tả||
|1|*{{Tên nhóm chức năng}}*| | | | |
|1.1|{{Chức năng cấp 3}}|BO|x|x|{{Ghi chú}}|

_(Nếu là RSD APP có RSD WEB tương ứng, thay toàn bộ bảng bằng: "Tham chiếu tại [RSD WEB|{{URL}}]")_

h2. 4*. Mô tả màn hình*

Figma: [{{tên Figma file}}|{{https://figma.com/design/...}}]

*a. Mockup màn hình*

Đường dẫn: {{Cách truy cập chức năng, ví dụ: Menu Thẻ > Danh sách thẻ > tab ...}}

{section}
{column:width=33%}
{{Caption state 1 — text thuần, không emoji, ví dụ: Màn hình danh sách khi có dữ liệu}}

!screen-01-default.png|width=360!

{{Caption state 2 — ví dụ: Màn hình khi không có dữ liệu}}

_(Ảnh: chưa có - cần bổ sung)_
{column}
{column:width=33%}
{{Caption state 3 — ví dụ: Màn hình khi mở Tìm kiếm nâng cao}}

!screen-03-search.png|width=360!

{{Caption state 4 — ví dụ: Màn hình kết quả tìm kiếm}}

_(Ảnh: chưa có - cần bổ sung)_
{column}
{column:width=33%}
{{Caption state 5 — ví dụ: Màn hình khi chọn dropdown}}

_(Ảnh: chưa có - cần bổ sung)_
{column}
{section}

*b. Mô tả màn hình*

|| ||*Hạng mục*||*Kiểu hiển thị*||*Kiểu thao tác*||*Bắt buộc*||*Độ dài*||*Mô tả*||
|1|*Cụm thông tin đầu trang*| | | | | |
|2|{{Element, ví dụ: Breadcrumb}}|Label / Button / Textbox / Droplist / Image / Tab ...|Read-only / Click / Input / Select|Y / N / -|{{max length hoặc "-"}}|{{Placeholder + mặc định + validate + logic + ẩn/hiện + enable/disable}}|
|3|*Cụm tìm kiếm nhanh*| | | | | |
|4|...| | | | | |
|5|*Cụm tìm kiếm nâng cao*| | | | | |
|6|...| | | | | |
|7|*Danh sách ...*| | | | | |
|8|...| | | | | |
|9|*Phân trang*| | | | | |
|10|...| | | | | |

h2. 5. Logic xử lý {{tên action chính, ví dụ: khi truy cập menu Thẻ > Danh sách thẻ > tab Thẻ tín dụng nội địa}}

||*Thao tác*||*Tác nhân*||*Mô tả*||
|{{Trigger user, ví dụ: User chọn tab Thẻ tín dụng nội địa}}|Client web/app|*1/ Gửi yêu cầu lấy danh sách ... qua API ...* \\ Endpoint: {{...}} \\ Payload: {{...}}|
| |Server {{Module}}|*1/ Kiểm tra tính hợp lệ input* \\ - Không hợp lệ: trả lỗi INPUT_01 \\ - Hết phiên: SESSION_TIMEOUT_01 \\ - Hợp lệ: chuyển bước 2 \\ \\ *2/ Kiểm tra phân quyền* \\ ... \\ \\ *3/ ...*|
| |Client web/app|*Nhận phản hồi* \\ - Lỗi phân quyền CARD.003: hiển thị popup "Người dùng chưa được phân quyền..." \\ - Thành công: hiển thị danh sách theo mô tả màn hình|
```

---

## Quy tắc quan trọng khi điền template

1. **Không dùng emoji** trong bất kỳ cell bảng hay đoạn text nào
2. **TOC tự động** từ `{toc:style=none}` — không cần tạo thủ công, không giới hạn maxLevel
3. **Xuống dòng trong cell bảng** dùng `\\` (2 backslash), KHÔNG dùng Enter/newline thật — vi phạm = vỡ bảng
4. **Numbered list trong cell** dùng số thủ công: `1. ... \\ 2. ... \\ 3. ...` — KHÔNG dùng `#` wiki list syntax
5. **KHÔNG dùng ký tự `|` trong nội dung cell** — parser hiểu là ranh giới cột → tạo thêm cột thừa
6. **Link ngoài** dùng `[Text|URL]`; **link nội bộ** dùng `[Text|#heading-anchor]`
7. **Ảnh** attach lên page sau khi tạo, chèn bằng `!ten-file.png|width=200!`. Width tuỳ platform: APP=200, WEB=360
8. **Số thứ tự bảng section 4b**: để trống header cột đầu (`|| ||`)
9. **Row group header** trong bảng 4b: `|STT|*Tên cụm*| | | | | |` — cột 1 là số thứ tự, cột 2 là tên cụm in đậm, 5 cột còn lại để trống (tổng 7 cells, khớp với 7 cột header)
10. **Section 4a**: luôn dùng lưới cột `{section}/{column}`. APP=4 cột (width=25%), WEB=3 cột (width=33%), màn hình detail/dialog=2 cột (width=50%). Mỗi state = 1 dòng caption + 1 dòng ảnh hoặc `_(Ảnh: chưa có - cần bổ sung)_`. KHÔNG bỏ qua khối `{section}` dù không có ảnh.
11. **KHÔNG ghi annotation trong document** (kể cả `[Cần xác nhận]`) — dùng placeholder text rõ ràng trong cell (ví dụ: `Chờ xác nhận từ BA`). Báo cáo các điểm chưa rõ trong chat reply sau khi upload.
12. **Không dùng `{anchor:section-N}`** — Confluence tự tạo anchor từ heading text.
13. **Không dùng `----`** để ngăn cách section — các section chỉ phân tách bằng heading h2.
14. **`{info}...{info}`** dùng cho instruction/callout text (dùng trong Section 2.2 và 3 theo mẫu).
