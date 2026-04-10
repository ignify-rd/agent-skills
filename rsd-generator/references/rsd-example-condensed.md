# RSD Example (condensed) — "WEB 2.1. Danh sách thẻ tín dụng nội địa"

Đây là trích rút gọn từ 1 RSD thật đang prod. Mục đích: cho thấy mức độ chi tiết và phong cách viết mong muốn. Không copy nguyên văn — đây chỉ là mẫu tham chiếu phong cách.

## Section 1.2 — Đặc tả usecase (ví dụ)

|  |  |
| --- | --- |
| **Tên** | Danh sách thẻ tín dụng nội địa |
| **Mô tả** | Cho phép người dùng tra cứu danh sách thẻ tín dụng nội địa |
| **Tác nhân** | Tác nhân chủ động: Khách hàng BIDV. Tác nhân thụ động: BDR, Hệ thống core thẻ mới (way4) |
| **Mức độ ưu tiên** | Medium |
| **Điều kiện trước** | 1. User đăng nhập FO iBank thành công. 2. User được phân quyền 1 trong 2: (a) Dịch vụ chủ thẻ — MENU_CODE=M_CARD_LIST_DVCT_TT, Function=INQUIRY, Dịch vụ=T-DVCT, Dịch vụ cấp 2=T-DVCT-TT; hoặc (b) Dịch vụ quản trị thẻ doanh nghiệp — MENU_CODE=M_CARD_LIST_DVQT_TT... 3. Truy cập menu tương ứng. |
| **Luồng chính** | User nhấn menu Thẻ > Danh sách thẻ > tab Thẻ tín dụng nội địa. 1. Client hiển thị màn hình danh sách thẻ, focus tab, gọi API danh sách thẻ. 2. Server trả kết quả. 3. Client hiển thị. 4. User thao tác tiếp. |
| **Luồng ngoại lệ** | 1. User chuyển menu / logout / mất mạng → usecase kết thúc. 2. API lấy dữ liệu fail → quay lại bước 1. |
| **Quy tắc nghiệp vụ** | Phân quyền dữ liệu: user được phân quyền tại CIM; BDR tuân theo chính sách core thẻ (gọi API với đầu vào CIF DN/cá nhân). Nguyên tắc Chủ thẻ: combo chọn "Tất cả" → API theo CIF DN; chọn "Thẻ của tôi" → API theo CIF DN + CIF cá nhân. Trạng thái "Chưa kích hoạt": productionStatus=Locked AND plasticStatus=PO. |

**Điểm học được:** trường "Điều kiện trước" và "Quy tắc nghiệp vụ" có thể rất dài và chứa các code cụ thể (MENU_CODE, biến API). Nếu URD có → bắt buộc đưa vào chi tiết. Nếu URD không có → `[Cần xác nhận]`.

## Section 2.2 — Kết nối (ví dụ 1 row)

| Bước | Tên kết nối | Trạng thái | Backend | Phương thức | Luồng | Mô tả |
| --- | --- | --- | --- | --- | --- | --- |
| User nhấn tab Thẻ tín dụng nội địa hoặc Áp dụng tìm kiếm | API danh sách thẻ | Có sẵn | Backend Ibank | API | FO BDR > Server Card | Trả về danh sách thẻ theo điều kiện. Endpoint: /card/inq/list/1.0 |
|  | API cardListBusiness | Có sẵn | ESB | API | Server Card > ESB | Endpoint: /libra/cardservice/v1.0/cardlistbusiness |

## Section 4b — Mô tả màn hình (ví dụ mức chi tiết 1 row)

| 7 | Số thẻ | Textbox | Input | N | 6 | Khi chưa có dữ liệu, hiển thị placeholder: "Số thẻ (6 số đầu hoặc 4 số cuối thẻ)". Mặc định: Rỗng. **Validate**: chỉ cho phép số, tối đa 6 ký tự. **Logic**: tìm gần đúng theo 6 số đầu hoặc 4 số cuối; nút X xóa nhanh khi focus / khi có giá trị; outfocus/enter giữ nguyên kết quả không update; chặn nhập vượt 6 ký tự. **Giá trị hiển thị**: user tự nhập. **Ẩn/hiện**: luôn hiện. **Mặc định**: Enable. |

**Điểm học được:** một row mô tả màn hình phải trả lời: placeholder, default, validate rules, logic tương tác (onBlur, onEnter, clear button), giá trị hiển thị từ đâu, ẩn/hiện, enable/disable. Viết dày đặc, dùng bullet trong 1 cell.

## Section 5 — Logic xử lý (ví dụ mức chi tiết)

| Thao tác | Tác nhân | Mô tả |
| --- | --- | --- |
| User chọn tab Thẻ tín dụng nội địa HOẶC nhấn Áp dụng tại Tìm kiếm nâng cao | Client | **1/ Gửi request lấy danh sách**. Endpoint: /card/inq/list/1.0. Payload: Header chung; Loại thẻ = 4 (TDNĐ); Chủ thẻ: default All / theo user chọn; Giá trị phân trang: default 10; Số trang: default 1. |
|  | Server Card | **1/ Kiểm tra input**: không hợp lệ → INPUT_01; hết phiên → SESSION_TIMEOUT_01; hợp lệ → bước 2. **2/ Kiểm tra phân quyền**: chấp nhận dịch vụ chủ thẻ (M_CARD_LIST_DVCT_TT) hoặc quản trị thẻ doanh nghiệp (M_CARD_LIST_DVQT_TT); không hợp lệ → CARD.003; hợp lệ → bước 3. **3/ Kiểm tra Chủ thẻ**: bảng quyết định theo (chọn Chủ thẻ × có quyền chủ thẻ × có quyền quản trị) → xác định "thẻ cá nhân" / "thẻ DN" / "rỗng". **4/** Map CIF cá nhân qua getPersonalCif(). **5/** Gọi cardListBusiness (loop toàn bộ), trả về ảnh phôi, số thẻ mask 6F4L, cardId, tên chủ thẻ, tên sản phẩm, trạng thái (map theo bảng trạng thái). **6/** Trường hợp DN — tương tự nhưng chỉ với CIF DN. **7/** Trả về client. |
|  | Client | **Nhận phản hồi**: lỗi phân quyền CARD.003 → popup "Người dùng chưa được phân quyền..." (WEB điều hướng về Trang chủ, APP ở lại màn Thẻ); lỗi khác → popup với message server; thành công + có dữ liệu → hiển thị grid theo mô tả Section 4; thành công + rỗng → 2 variants: vào từ menu → "Khách hàng chưa có thẻ. Vui lòng phát hành thẻ để sử dụng", vào từ Áp dụng search → "Không tồn tại dữ liệu theo điều kiện tìm kiếm". |

**Điểm học được:** Section 5 là trái tim của RSD. Phải mô tả:
- Client gọi endpoint nào, payload gì
- Server kiểm tra theo thứ tự (validate → authz → business logic)
- Mỗi nhánh lỗi có error code + message cụ thể
- Mỗi nhánh thành công hiển thị gì ở client (reference Section 4)
- Decision tables khi logic phức tạp (như bảng Chủ thẻ × quyền)

## Điểm style quan trọng

1. **Heading đánh số cố định** (1., 2., 3., 4., 5., 2.1., 2.2., 2.3., 2.3.1., 4.a, 4.b).
2. **Bảng markdown** với header in đậm, row "section header" (in đậm toàn bộ row, các cột khác để trống).
3. **Link chéo tới page khác** dùng `<https://...>` inline trong cell bảng.
4. **Tiếng Việt có dấu** ở mọi label và nội dung; không dịch sang tiếng Anh.
5. **Ghi rõ error code** (INPUT_01, CARD.003, SESSION_TIMEOUT_01...) khi đã xác định được từ URD.
