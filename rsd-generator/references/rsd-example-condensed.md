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
|*Điều kiện trước*|# User đăng nhập FO iBank thành công \\ # User được phân quyền 1 trong 2: (a) Dịch vụ chủ thẻ — MENU_CODE=M_CARD_LIST_DVCT_TT, Function=INQUIRY; hoặc (b) Dịch vụ quản trị thẻ doanh nghiệp — MENU_CODE=M_CARD_LIST_DVQT_TT \\ # Truy cập menu tương ứng|
|*Luồng chính*|# User nhấn menu Thẻ > Danh sách thẻ > tab Thẻ tín dụng nội địa \\ # Client hiển thị màn hình danh sách thẻ, focus tab, gọi API danh sách thẻ \\ # Server trả kết quả \\ # Client hiển thị \\ # User thao tác tiếp|
|*Luồng ngoại lệ*|# User chuyển menu / logout / mất mạng → usecase kết thúc \\ # API lấy dữ liệu fail → quay lại bước 1|
|*Quy tắc nghiệp vụ*|Phân quyền dữ liệu: user được phân quyền tại CIM; BDR tuân theo chính sách core thẻ. \\ Nguyên tắc Chủ thẻ: combo chọn "Tất cả" → API theo CIF DN; chọn "Thẻ của tôi" → API theo CIF DN + CIF cá nhân. \\ Trạng thái "Chưa kích hoạt": productionStatus=Locked AND plasticStatus=PO.|
```

**Điểm học được:** "Điều kiện trước" và "Quy tắc nghiệp vụ" có thể rất dài và chứa code cụ thể (MENU_CODE, biến API). Nếu URD có → bắt buộc đưa vào chi tiết. Nếu URD không có → `[Cần xác nhận]`. Xuống dòng trong cell bảng dùng `\\` (2 backslash).

---

## Section 2.2 — Kết nối (ví dụ 1 row)

```wiki
||Bước||Tên kết nối||Trạng thái sẵn sàng||Backend cung cấp kết nối||Phương thức tích hợp||Luồng gọi API||Mô tả kết nối||
|User nhấn tab Thẻ tín dụng nội địa hoặc Áp dụng tìm kiếm|API danh sách thẻ|Có sẵn|Backend Ibank|API|FO BDR > Server Card|Trả về danh sách thẻ theo điều kiện. Endpoint: /card/inq/list/1.0|
| |API cardListBusiness|Có sẵn|ESB|API|Server Card > ESB|Endpoint: /libra/cardservice/v1.0/cardlistbusiness|
```

---

## Section 4a — Mockup màn hình (ví dụ)

```wiki
Figma: [Tên file|https://figma.com/design/...]

*a. Mockup màn hình*

Đường dẫn: Menu Thẻ > Danh sách thẻ > tab Thẻ tín dụng nội địa

Màn hình danh sách khi có dữ liệu

!screen-01-default.png!

Màn hình danh sách khi không có dữ liệu (vào từ menu)

!screen-02-empty.png!

Màn hình khi nhấn Tìm kiếm nâng cao

!screen-03-search-expanded.png!
```

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
