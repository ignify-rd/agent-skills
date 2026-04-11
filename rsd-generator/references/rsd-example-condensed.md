# RSD Example (condensed) — "WEB 2.1. Danh sách thẻ tín dụng nội địa"

Đây là trích rút gọn từ 1 RSD thật đang prod. Mục đích: cho thấy mức độ chi tiết và phong cách viết mong muốn. Không copy nguyên văn — chỉ là mẫu tham chiếu.

**Format**: tất cả ví dụ bên dưới viết bằng **Confluence Wiki Markup** — dùng `||` cho header bảng, `h2.`/`h3.` cho heading, `*bold*` cho in đậm.

---

## Section 1.2 — Đặc tả usecase (ví dụ)

```wiki
||Hạng mục||Nội dung||
|*Tên*|Danh sách thẻ tín dụng nội địa|
|*Mô tả*|Cho phép người dùng tra cứu danh sách thẻ tín dụng nội địa|
|*Tác nhân*|Tác nhân chủ động: Khách hàng BIDV \\ Tác nhân thụ động: BDR, Hệ thống core thẻ mới (way4)|
|*Mức độ ưu tiên*|Medium|
|*Điều kiện trước*|1. User đăng nhập FO iBank thành công \\ 2. User được phân quyền 1 trong 2: (a) Dịch vụ chủ thẻ — MENU_CODE=M_CARD_LIST_DVCT_TT, Function=INQUIRY; hoặc (b) Dịch vụ quản trị thẻ doanh nghiệp — MENU_CODE=M_CARD_LIST_DVQT_TT \\ 3. Truy cập menu tương ứng|
|*Luồng chính*|1. User nhấn menu Thẻ > Danh sách thẻ > tab Thẻ tín dụng nội địa \\ 2. Client hiển thị màn hình danh sách thẻ, focus tab, gọi API danh sách thẻ \\ 3. Server trả kết quả \\ 4. Client hiển thị \\ 5. User thao tác tiếp|
|*Luồng ngoại lệ*|1. User chuyển menu / logout / mất mạng → usecase kết thúc \\ 2. API lấy dữ liệu fail → quay lại bước 1|
|*Quy tắc nghiệp vụ*|Phân quyền dữ liệu: user được phân quyền tại CIM; BDR tuân theo chính sách core thẻ. \\ Nguyên tắc Chủ thẻ: combo chọn "Tất cả" → API theo CIF DN; chọn "Thẻ của tôi" → API theo CIF DN + CIF cá nhân. \\ Trạng thái "Chưa kích hoạt": productionStatus=Locked AND plasticStatus=PO.|
```

**Điểm học được:** "Điều kiện trước" và "Quy tắc nghiệp vụ" có thể rất dài và chứa code cụ thể (MENU_CODE, biến API). Nếu URD có → bắt buộc đưa vào chi tiết. Nếu URD không có → điền placeholder text mô tả rõ ràng (ví dụ: `Chờ xác nhận từ BA`) — KHÔNG ghi `[Cần xác nhận]` trong document. Xuống dòng trong cell bảng dùng `\\` (2 backslash).

---

## Section 2.2 — Kết nối (ví dụ 1 row)

```wiki
||Bước||Tên kết nối||Trạng thái sẵn sàng||Backend cung cấp kết nối||Phương thức tích hợp||Luồng gọi API/ Luồng đi của kết nối||Mô tả kết nối||
|User nhấn tab Thẻ tín dụng nội địa hoặc Áp dụng tìm kiếm|API danh sách thẻ|Có sẵn|Backend Ibank|API|FO BDR > Server Card|Trả về danh sách thẻ theo điều kiện. Endpoint: /card/inq/list/1.0|
| |API cardListBusiness|Có sẵn|ESB|API|Server Card > ESB|Endpoint: /libra/cardservice/v1.0/cardlistbusiness|
```

---

## Section 3 — Ma trận phân quyền (ví dụ rút gọn cho iBank FO)

```wiki
{info}
Mô tả tính năng phân bổ ở các FO/BO/iconnect và phân quyền người dùng.
Dùng "x" cho ô có quyền, để trống ô không có quyền. Không dùng emoji.
{info}

*Cho iBank / FO (nhiều kênh):*

||STT||Usecase (chức năng cấp 3)||MB||IB||BO||ERP (web/app)||ERP (H2H)||Maker-KH||Checker-KH||Inquiry-KH||Admin-KH||GDV CN||KSV CN||GDV TSC||KSV TSC||Inquiry-BO||Nhóm quyền khác còn lại||Mô tả||
|1|*Danh sách thẻ tín dụng nội địa*| | | | | | | | | | | | | | | | |
|1.1|Xem danh sách thẻ| |x| | | |x|x|x| | | | | | | |Hiển thị danh sách thẻ theo CIF|
|1.2|Tìm kiếm thẻ| |x| | | |x|x|x| | | | | | | |Tìm theo số thẻ, trạng thái, chủ thẻ|
```

**Điểm học được:** Luôn dùng `{info}` block để wrap instruction text đầu section. Cột "Nhóm quyền khác còn lại" (không phải "Nhóm quyền khác"). Row group header không có giá trị ở cột quyền. Dùng text "x" — không dùng emoji hay ký tự đặc biệt.

---

## Section 4a — Mockup màn hình (ví dụ — WEB dùng 3 cột width=33%)

```wiki
Figma: [Tên file|https://figma.com/design/...]

*a. Mockup màn hình*

Đường dẫn: Menu Thẻ > Danh sách thẻ > tab Thẻ tín dụng nội địa

{section}
{column:width=33%}
Màn hình danh sách khi có dữ liệu

!screen-01-default.png|width=360!

Màn hình danh sách khi không có dữ liệu (vào từ menu)

!screen-02-empty.png|width=360!
{column}
{column:width=33%}
Màn hình khi nhấn Tìm kiếm nâng cao

!screen-03-search-expanded.png|width=360!

Màn hình kết quả tìm kiếm nâng cao khi có dữ liệu

!screen-04-search-result.png|width=360!
{column}
{column:width=33%}
Màn hình kết quả tìm kiếm nâng cao khi không có dữ liệu

_(Ảnh: chưa có - cần bổ sung)_
{column}
{section}
```

**Điểm học được:** Section 4a luôn dùng lưới cột `{section}/{column}` — WEB=3 cột (width=33%), APP=4 cột (width=25%), dialog/detail=2 cột (width=50%). Mỗi cột chứa 1-2 state (caption + ảnh hoặc placeholder). Không được bỏ layout này dù không có ảnh — vẫn phải sinh caption + placeholder cho từng state.

---

## Section 4b — Mô tả màn hình (ví dụ mức chi tiết 1 row)

```wiki
|| ||*Hạng mục*||*Kiểu hiển thị*||*Kiểu thao tác*||*Bắt buộc*||*Độ dài*||*Mô tả*||
|1|*Cụm tìm kiếm nhanh*| | | | | |
|2|Số thẻ|Textbox|Input|N|6|Khi chưa có dữ liệu, hiển thị placeholder: "Số thẻ (6 số đầu hoặc 4 số cuối thẻ)". Mặc định: Rỗng. *Validate*: chỉ cho phép số, tối đa 6 ký tự. *Logic*: tìm gần đúng theo 6 số đầu hoặc 4 số cuối; nút X xóa nhanh khi focus / khi có giá trị; outfocus/enter giữ nguyên kết quả không update; chặn nhập vượt 6 ký tự. *Giá trị hiển thị*: user tự nhập. *Ẩn/hiện*: luôn hiện. *Mặc định*: Enable.|
```

**Điểm học được:** một row mô tả màn hình phải trả lời: placeholder, default, validate rules, logic tương tác (onBlur, onEnter, clear button), giá trị hiển thị từ đâu, ẩn/hiện, enable/disable. Viết dày đặc, dùng `\\` để xuống dòng giữa các mục trong cùng một cell.

---

## Section 5 — Logic xử lý (ví dụ mức chi tiết)

```wiki
||*Thao tác*||*Tác nhân*||*Mô tả*||
|User chọn tab Thẻ tín dụng nội địa HOẶC nhấn Áp dụng tại Tìm kiếm nâng cao|Client|*1/ Gửi request lấy danh sách*. Endpoint: /card/inq/list/1.0. \\ Payload: Header chung; Loại thẻ = 4 (TDNĐ); Chủ thẻ: default All / theo user chọn; Giá trị phân trang: default 10; Số trang: default 1.|
| |Server Card|*1/ Kiểm tra input*: không hợp lệ → INPUT_01; hết phiên → SESSION_TIMEOUT_01; hợp lệ → bước 2. \\ *2/ Kiểm tra phân quyền*: chấp nhận M_CARD_LIST_DVCT_TT hoặc M_CARD_LIST_DVQT_TT; không hợp lệ → CARD.003; hợp lệ → bước 3. \\ *3/ Kiểm tra Chủ thẻ*: xác định thẻ cá nhân / thẻ DN / rỗng. \\ *4/* Map CIF cá nhân qua getPersonalCif(). \\ *5/* Gọi cardListBusiness, trả về số thẻ mask 6F4L, cardId, tên chủ thẻ, trạng thái. \\ *6/* Trả về client.|
| |Client|*Nhận phản hồi*: lỗi CARD.003 → popup "Người dùng chưa được phân quyền..."; lỗi khác → popup message server; thành công + có dữ liệu → hiển thị grid theo Section 4; thành công + rỗng → "Khách hàng chưa có thẻ...".|
```

**Điểm học được:** Section 5 phải mô tả:
- Client gọi endpoint nào, payload gì
- Server kiểm tra theo thứ tự (validate → authz → business logic)
- Mỗi nhánh lỗi có error code + message cụ thể
- Mỗi nhánh thành công hiển thị gì ở client (reference Section 4)

---

## Điểm style quan trọng

1. **Heading** dùng `h2.` / `h3.` — không dùng Markdown `##` / `###`
2. **Bảng** dùng `||col||` cho header, `|cell|` cho data — không dùng Markdown `| --- |`
3. **In đậm** dùng `*text*` — không dùng Markdown `**text**`
4. **Xuống dòng trong cell** dùng `\\` (2 backslash)
5. **Link chéo tới page khác** dùng `[Text|URL]` trong cell bảng
6. **Tiếng Việt có dấu** ở mọi label và nội dung
7. **Ghi rõ error code** (INPUT_01, CARD.003, SESSION_TIMEOUT_01...) khi đã xác định được từ URD
