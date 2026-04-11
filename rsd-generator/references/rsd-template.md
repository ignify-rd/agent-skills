# RSD Template (skeleton) — Confluence Wiki Markup

Đây là skeleton đầy đủ của 1 page RSD viết bằng **Confluence Wiki Markup**. Copy toàn bộ, điền dữ liệu từ URD/Figma. Giữ nguyên heading và label bảng (tiếng Việt, có dấu).

Upload lên Confluence bằng MCP với `content_format="wiki"`.

---

## Template wiki (copy phần dưới đây vào content)

```wiki
*Phiên bản tài liệu*

||Version||Lý do||Date||Người sửa||Mô tả||
|1.0|Thêm mới|{{YYYY-MM-DD}}|{{Tác giả}}|Khởi tạo|

----

*Mục lục*

{toc:maxLevel=2}

----

{anchor:section-1}
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

----

{anchor:section-2}
h2. 2. Sơ đồ luồng xử lý

h3. 2.1. Sơ đồ luồng xử lý

{{Chèn ảnh nếu có: !ten-anh-so-do.png! \\ Hoặc sơ đồ ASCII trong khối noformat:}}

{noformat}
{{Sơ đồ luồng ASCII hoặc để trống + ghi chú "Sẽ bổ sung"}}
{noformat}

h3. 2.2. Yêu cầu với các kết nối phát sinh mới/ cần chỉnh sửa trong luồng

# Hệ thống mới, chức năng mới: Liệt kê toàn bộ các kết nối được sử dụng tại chức năng này.
# Với các kết nối mới/ cần chỉnh sửa: mô tả yêu cầu của nghiệp vụ với các kết nối này.

||Bước||Tên kết nối||Trạng thái sẵn sàng||Backend cung cấp kết nối||Phương thức tích hợp||Luồng gọi API||Mô tả kết nối||
|{{Mô tả bước}}|{{Tên API}}|Có sẵn / Phát sinh mới / Cần chỉnh sửa|{{Module backend}}|API / DBlink / Job|{{Client → Server → Core}}|{{Endpoint + chức năng}}|

h3. 2.3. Danh mục hoặc sơ đồ trạng thái

h4. 2.3.1. {{Tên đối tượng, ví dụ: Trạng thái của thẻ}}

Theo mô tả tại: [{{tên tài liệu trạng thái}}|{{URL}}]

----

{anchor:section-3}
h2. 3. Ma trận phân quyền và phân bổ chức năng

Mô tả tính năng phân bổ ở các FO/BO/iconnect và phân quyền người dùng (khởi tạo, sửa, xác nhận, duyệt).
_Dùng "x" cho ô có quyền, để trống ô không có quyền. Không dùng emoji._

_Chọn cấu trúc cột phù hợp với dự án:_

*Cho iBank / FO (nhiều kênh):*

||STT||Usecase (chức năng cấp 3)||MB||IB||BO||ERP (web/app)||ERP (H2H)||Maker-KH||Checker-KH||Inquiry-KH||Admin-KH||GDV CN||KSV CN||GDV TSC||KSV TSC||Inquiry-BO||Nhóm quyền khác||Mô tả||
|1|*{{Tên nhóm chức năng}}*| | | | | | | | | | | | | | | | |
|1.1|{{Chức năng cấp 3}}|x|x| | | |x|x|x|x| | | | | | |{{Ghi chú phân giao}}|

*Cho BO nội bộ / BackOffice (KSV/GDV):*

||STT||Chức năng||Nơi phân bổ||KSV||GDV||Mô tả||
|1|*{{Tên nhóm chức năng}}*| | | | |
|1.1|{{Chức năng cấp 3}}|BO|x|x|{{Ghi chú}}|

_(Nếu là RSD APP có RSD WEB tương ứng, thay toàn bộ bảng bằng: "Tham chiếu tại [RSD WEB|{{URL}}]")_

----

{anchor:section-4}
h2. 4. Mô tả màn hình

Figma: [{{tên Figma file}}|{{https://figma.com/design/...}}]

*a. Mockup màn hình*

Đường dẫn: {{Cách truy cập chức năng, ví dụ: Menu Thẻ > Danh sách thẻ > tab ...}}

{{Caption state 1 — text thuần, không emoji, ví dụ: Màn hình danh sách khi có dữ liệu}}

!screen-01-default.png!

{{Caption state 2 — ví dụ: Màn hình khi không có dữ liệu}}

_(Ảnh: chưa có - cần bổ sung)_

{{Caption state 3 — ví dụ: Màn hình khi mở Tìm kiếm nâng cao}}

!screen-03-search.png!

_Quy tắc: mỗi state = 1 dòng caption + 1 dòng ảnh (!file.png!) hoặc placeholder. Không được thay bằng ghi chú chung như "screenshots đính kèm". Enumerate từng state cụ thể dù không có ảnh._

*b. Mô tả màn hình*

|| ||*Hạng mục*||*Kiểu hiển thị*||*Kiểu thao tác*||*Bắt buộc*||*Độ dài*||*Mô tả*||
|1|*Cụm thông tin đầu trang*| | | | | |
|2|{{Element, ví dụ: Breadcrumb}}|Label / Button / Textbox / Droplist / Image / Tab ...|Read-only / Click / Input / Select|Y / N / -|{{max length hoặc "-"}}|{{Placeholder + mặc định + validate + logic + ẩn/hiện + enable/disable}}|
|3|*Cụm tìm kiếm nâng cao*| | | | | |
|4|...| | | | | |
|5|*Danh sách ...*| | | | | |
|6|...| | | | | |
|7|*Phân trang*| | | | | |
|8|...| | | | | |

----

{anchor:section-5}
h2. 5. Logic xử lý {{tên action chính, ví dụ: khi truy cập menu Thẻ > Danh sách thẻ > tab Thẻ tín dụng nội địa}}

||*Thao tác*||*Tác nhân*||*Mô tả*||
|{{Trigger user, ví dụ: User chọn tab Thẻ tín dụng nội địa}}|Client web/app|*1/ Gửi yêu cầu lấy danh sách ... qua API ...* \\ Endpoint: {{...}} \\ Payload: {{...}}|
| |Server {{Module}}|*1/ Kiểm tra tính hợp lệ input* \\ * Không hợp lệ: trả lỗi INPUT_01 \\ * Hết phiên: SESSION_TIMEOUT_01 \\ * Hợp lệ: chuyển bước 2 \\ \\ *2/ Kiểm tra phân quyền* \\ ... \\ \\ *3/ ...*|
| |Client web/app|*Nhận phản hồi* \\ * Lỗi phân quyền CARD.003: hiển thị popup "Người dùng chưa được phân quyền..." \\ * Thành công: hiển thị danh sách theo mô tả màn hình|

----

h2. Các điểm cần user xác nhận trước khi chính thức hoá

* {{Ghi rõ từng [Cần xác nhận] đã đánh dấu ở trên, kèm section reference}}
```

---

## Quy tắc quan trọng khi điền template

1. **Không dùng emoji** trong bất kỳ cell bảng hay đoạn text nào
2. **TOC tự động** từ `{toc:maxLevel=2}` — không cần tạo thủ công
3. **Xuống dòng trong cell bảng** dùng `\\` (2 backslash), KHÔNG dùng Enter/newline thật — vi phạm = vỡ bảng
4. **Numbered list trong cell** dùng số thủ công: `1. ... \\ 2. ... \\ 3. ...` — KHÔNG dùng `#` wiki list syntax
5. **KHÔNG dùng ký tự `|` trong nội dung cell** — parser hiểu là ranh giới cột → tạo thêm cột thừa
6. **Link ngoài** dùng `[Text|URL]`; **link nội bộ** dùng `[#section-id]`
7. **Ảnh** attach lên page sau khi tạo, chèn bằng `!ten-file.png!` hoặc `!ten-file.png|width=800!`
8. **Số thứ tự bảng section 4b**: để trống header cột đầu (`|| ||`)
9. **Row group header** trong bảng 4b: cell đầu là `*Tên cụm*`, các cột còn lại để trống
10. **Section 4a**: mỗi state = 1 dòng caption + 1 dòng `!file.png!` hoặc `_(Ảnh: chưa có - cần bổ sung)_`. KHÔNG thay bằng ghi chú chung.
