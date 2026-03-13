# BO_Phí định kỳ > Phí chính sách tự động

## Kiểm tra giao diện chung

### Kiểm tra điều hướng đến màn hình Phí chính sách tự động

- Điều hướng thành công đến màn hình Phí chính sách tự động
  
### Kiểm tra bố cục giao diện tổng thể

- + Hiển thị theo đúng figma  
  + Màn hình Phí chính sách tự động hiển thị đầy đủ các thông tin:  
  + Dropdown list - Đối tượng khai báo  
  + Dropdown list (Searchable) - Dịch vụ thu phí/Gói SPDV  
  + Dropdown list (Multi-select) - Trạng thái  
  + Button - Tìm kiếm  
  + Button - Xóa bộ lọc  
  + Button - Xuất excel  
  + Lưới dữ liệu - Danh sách phí chính sách tự động  
  + Phân trang  
  + Icon - Chỉnh sửa (trong lưới)
  
### Kiểm tra hiển thị breadcrumb

- Phí định kỳ > Phí chính sách tự động
  
### Kiểm tra hiển thị bố cục layout cân đối

- Hiển thị đúng cỡ chữ, màu chữ, bố cục cân đối, kích thước chính xác, đúng chính tả
  
### Kiểm tra phóng to/thu nhỏ

- Màn hình không bị vỡ form

## Kiểm tra phân quyền

### Kiểm tra login user không có quyền

- Không truy cập được màn hình hoặc button bị ẩn/disable

### GDV: Xem, Xuất excel, Chỉnh sửa (create/update). KSV: Xem, Xuất excel, Phê duyệt (approve/reject).

- GDV thấy icon chỉnh sửa, KSV thấy checkbox phê duyệt (tại màn chi tiết)

## Kiểm tra validate

### Kiểm tra dropdown list "Đối tượng khai báo"

- Kiểm tra hiển thị mặc định
  
    - Luôn hiện và enable
      
- Kiểm tra giá trị mặc định
  
    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "Chọn đối tượng"
      
- Kiểm tra giá trị hiển thị khi nhấn chọn Dropdown list
  
    - Hiển thị danh sách các giá trị:
      
        - Tất cả  
        - Dịch vụ thu phí  
        - Gói SPDV

- Kiểm tra khi chọn giá trị trong Dropdown list

    - Kiểm tra khi chọn 1 giá trị

        - Hệ thống cho phép chọn

    - Kiểm tra khi chọn nhiều giá trị

        - Hệ thống chỉ cho phép chọn 1

- Kiểm tra khi chọn giá trị = "Tất cả"
  
    - Hệ thống hiển thị text "Tất cả" tại dropdown list  
  
- Kiểm tra khi chọn giá trị = "Dịch vụ thu phí"
  
    - Hệ thống hiển thị text "Dịch vụ thu phí" tại dropdown list  
  
- Kiểm tra khi chọn giá trị = "Gói SPDV"
  
    - Hệ thống hiển thị text "Gói SPDV" tại dropdown list

#### Icon X

- Kiểm tra hiển thị khi chọn giá trị

    - Hiển thị icon X xóa nhanh ký tự nhập

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh giá trị đã chọn

    - Clear data đã chọn

### Kiểm tra textbox "Dịch vụ thu phí/Gói SPDV"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "Chọn dịch vụ/gói"

- Kiểm tra khi nhập kí tự là số

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự chữ

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự đặc biệt

    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập kí tự chứa space đầu/cuối

    - Hệ thống cho phép nhập

- Kiểm tra khi Paste kí tự chứa space đầu/cuối

    - Hệ thống cho phép Paste

- Kiểm tra khi nhập all space

    - Hệ thống cho phép nhập

### Kiểm tra dropdown list "Trạng thái"

- Kiểm tra hiển thị mặc định
  
    - Luôn hiện và enable
      
- Kiểm tra giá trị mặc định
  
    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "Chọn trạng thái"
      
- Kiểm tra giá trị hiển thị khi nhấn chọn Dropdown list
  
    - Hiển thị danh sách các giá trị:
      
        - Tất cả  
        - Không hoạt động (0)  
        - Hoạt động (1)  
        - Tạo nháp (2)  
        - Chờ duyệt sửa (4)

- Kiểm tra khi chọn giá trị trong Dropdown list

    - Kiểm tra khi chọn 1 giá trị

        - Hệ thống cho phép chọn

    - Kiểm tra khi chọn nhiều giá trị

        - Cho phép chọn nhiều

- Kiểm tra khi chọn giá trị = "Tất cả"
  
    - Hệ thống hiển thị text "Tất cả" tại dropdown list  
  
- Kiểm tra khi chọn giá trị = "Không hoạt động (0)"
  
    - Hệ thống hiển thị text "Không hoạt động (0)" tại dropdown list  
  
- Kiểm tra khi chọn giá trị = "Hoạt động (1)"
  
    - Hệ thống hiển thị text "Hoạt động (1)" tại dropdown list  
  
- Kiểm tra khi chọn giá trị = "Tạo nháp (2)"
  
    - Hệ thống hiển thị text "Tạo nháp (2)" tại dropdown list  
  
- Kiểm tra khi chọn giá trị = "Chờ duyệt sửa (4)"
  
    - Hệ thống hiển thị text "Chờ duyệt sửa (4)" tại dropdown list

#### Icon X

- Kiểm tra hiển thị khi chọn giá trị

    - Hiển thị icon X xóa nhanh ký tự nhập

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh giá trị đã chọn

    - Clear data đã chọn

### Kiểm tra Button Tìm kiếm

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra hiển thị text, thiết kế của button

    - Hiển thị text "Tìm kiếm", thiết kết theo figma

### Kiểm tra Button Xóa bộ lọc

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra hiển thị text, thiết kế của button

    - Hiển thị text "Xóa bộ lọc", thiết kết theo figma

### Kiểm tra Button Xuất excel

- Kiểm tra hiển thị

    - Mặc định enable

- Kiểm tra hiển thị text, thiết kế của button

    - Hiển thị text "Xuất excel", thiết kết theo figma

- Kiểm tra trạng thái field "Dịch vụ thu phí/Gói SPDV" khi field "Đối tượng khai báo" chưa chọn hoặc chọn giá trị "Tất cả"
    - Field "Dịch vụ thu phí/Gói SPDV" bị khóa (Disable), không cho phép thao tác

- Kiểm tra nguồn dữ liệu (API) của field "Dịch vụ thu phí/Gói SPDV" khi field "Đối tượng khai báo" chọn là "Dịch vụ thu phí"
    - Dropdown load danh sách từ API `/v1/dropdown/fee-service/active` với tham số `srvType = 1`

- Kiểm tra nguồn dữ liệu (API) của field "Dịch vụ thu phí/Gói SPDV" khi field "Đối tượng khai báo" chọn là "Gói SPDV"
    - Dropdown load danh sách từ API `/v1/dropdown/pkg-grp/active`

- Kiểm tra giá trị của field "Dịch vụ thu phí/Gói SPDV" khi thay đổi giá trị field "Đối tượng khai báo" (ví dụ: từ Dịch vụ sang Gói)
    - Field "Dịch vụ thu phí/Gói SPDV" phải reset giá trị đã chọn về rỗng/mặc định

- Kiểm tra giá trị mặc định của field "Trạng thái" khi người dùng đăng nhập có quyền KSV (functionCode: approve hoặc reject)
    - Field hiển thị mặc định chọn 1 giá trị là "Chờ duyệt sửa" (code = 4)

- Kiểm tra giá trị mặc định của field "Trạng thái" khi người dùng đăng nhập KHÔNG có quyền KSV
    - Field hiển thị placeholder "Chọn trạng thái" (không chọn giá trị nào)

- Kiểm tra hành động nhấn nút "Xóa bộ lọc" đối với người dùng có quyền KSV
    - Các field search reset về rỗng, riêng field "Trạng thái" reset về giá trị "Chờ duyệt sửa" (theo trạng thái ban đầu khi vào chức năng)

- Kiểm tra hiển thị nút "Xuất excel" khi danh sách kết quả tìm kiếm Trống (Empty)
    - Nút "Xuất excel" bị ẩn hoặc disable (Dựa trên rule: Chỉ hiển thị khi Danh sách khác trống)

- Kiểm tra hiển thị icon "Chỉnh sửa" trên lưới dữ liệu đối với bản ghi có Trạng thái là "Không hoạt động" (Mã 0 - INACTIVE)
    - Không hiển thị icon "Chỉnh sửa" (hoặc icon bị ẩn)

- Kiểm tra hiển thị icon "Chỉnh sửa" trên lưới dữ liệu đối với bản ghi có Trạng thái KHÁC "Không hoạt động" (Mã != 0) và user có quyền Update
    - Hiển thị icon "Chỉnh sửa"

- Kiểm tra hiển thị icon "Chỉnh sửa" trên lưới dữ liệu khi User KHÔNG có quyền Update (functionCode: update)
    - Không hiển thị icon "Chỉnh sửa" ở tất cả các dòng, bất kể trạng thái bản ghi

## Kiểm tra lưới dữ liệu

### Kiểm tra mặc định

- Kiểm tra hiển thị khi không có dữ liệu:
    - Server trả về danh sách rỗng (empty list).
    - Lưới hiển thị trạng thái "Không có dữ liệu" (Empty state) theo design.
- Kiểm tra hiển thị khi có dữ liệu:
    - Server trả về danh sách các bản ghi thỏa mãn điều kiện tìm kiếm.
    - Lưới hiển thị đầy đủ các cột và dữ liệu tương ứng.

### Kiểm tra hiển thị sắp xếp các bản ghi trên lưới dữ liệu

- Hiển thị theo thứ tự mặc định do server trả về (thường là ngày cập nhật hoặc ngày tạo mới nhất):
    - SELECT * FROM SEGMENT_FEE_MASTER ORDER BY UPDATED_TIME DESC

### Kiểm tra cột "STT"

- Hiển thị số thứ tự tăng dần theo trang:
    - Giá trị được tính toán tại Client hoặc Server trả về theo index của trang hiện tại.

### Kiểm tra cột "Đối tượng khai báo"

- Hiển thị thông tin DOMAIN_TYPE_NAME do server trả về theo DB:
    - SELECT DOMAIN_TYPE FROM SEGMENT_FEE_MASTER WHERE ...
- Hiển thị theo logic mapping (ví dụ: 1 = Dịch vụ thu phí, 2 = Gói SPDV).

### Kiểm tra cột "Dịch vụ thu phí/ Gói SPDV"

- Hiển thị thông tin FEE_SERVICE và FEE_SERVICE_NAME do server trả về theo DB:
    - SELECT FEE_SERVICE FROM SEGMENT_FEE_MASTER WHERE ...
- Hiển thị theo định dạng: [Mã] - [Tên] ({FEE_SERVICE} - {FEE_SERVICE_NAME})

### Kiểm tra cột "Phí segment hoạt động"

- Hiển thị thông tin số lượng segment Active / Tổng số segment do server trả về (tính toán từ bảng SEGMENT_FEE_CONFIG):
    - SELECT COUNT(*) FROM SEGMENT_FEE_CONFIG WHERE STATUS = 1 AND MASTER_ID = [ID] (Active Segment)
    - SELECT COUNT(*) FROM SEGMENT_FEE_CONFIG WHERE MASTER_ID = [ID] (Total Segment)
- Hiển thị theo định dạng: {ACTIVE_SEGMENT}/{TOTAL_SEGMENT}

### Kiểm tra cột "Trạng thái"

- Hiển thị thông tin STATUS_NAME do server trả về theo DB:
    - SELECT STATUS FROM SEGMENT_FEE_MASTER WHERE ...
- Hiển thị màu sắc và tên trạng thái theo quy định (ví dụ: 0: Không hoạt động, 1: Hoạt động, 2: Tạo nháp, 4: Chờ duyệt sửa).

### Kiểm tra cột "Người cập nhật"

- Hiển thị thông tin UPDATED_USER do server trả về theo DB:
    - SELECT UPDATED_USER FROM SEGMENT_FEE_MASTER WHERE ...
- Nếu dữ liệu null, hiển thị trống.

### Kiểm tra cột "Ngày cập nhật"

- Hiển thị thông tin UPDATED_TIME do server trả về theo DB:
    - SELECT UPDATED_TIME FROM SEGMENT_FEE_MASTER WHERE ...
- Hiển thị theo định dạng: dd/mm/yyyy HH:mm:ss
- Nếu dữ liệu null, hiển thị trống.

### Kiểm tra cột "Người duyệt"

- Hiển thị thông tin APPROVED_USER do server trả về theo DB:
    - SELECT APPROVED_USER FROM SEGMENT_FEE_MASTER WHERE ...
- Hiển thị mã cán bộ duyệt.

### Kiểm tra cột "Ngày duyệt"

- Hiển thị thông tin APPROVED_TIME do server trả về theo DB:
    - SELECT APPROVED_TIME FROM SEGMENT_FEE_MASTER WHERE ...
- Hiển thị theo định dạng: dd/mm/yyyy HH:mm:ss

### Kiểm tra cột "Thao tác"

- Hiển thị các action button (Chỉnh sửa) dựa trên trạng thái bản ghi và quyền của người dùng:
    - Kiểm tra hiển thị icon "Chỉnh sửa" khi hover vào dòng bản ghi (với trạng thái != Không hoạt động).
    - Kiểm tra ẩn icon khi không thỏa mãn điều kiện.

### Kiểm tra lưới dữ liệu khi kéo thanh cuộn ngang

- Khi cuộn ngang cố định các cột: Thao tác

### Kiểm tra lưới dữ liệu khi kéo thanh cuộn dọc

- Tiêu đề lưới (Header) và khung tìm kiếm được giữ cố định ở vị trí đầu danh sách.
- Dữ liệu trong lưới cuộn theo thao tác người dùng.

### Kiểm tra dữ liệu trả về từ server

- Verify tổng số bản ghi hiển thị trên lưới khớp với tổng số bản ghi trả về từ API (Total elements).
- Verify dữ liệu phân trang (Pagination) hoạt động đúng theo size và page number gửi lên server.

## Kiểm tra "Phân trang"

### Kiểm tra giá trị phân trang khi không có dữ liệu

- Ẩn lưới dữ liệu
  
### Kiểm tra các giá trị số lượng bản ghi /trang

- Danh mục giá trị gồm:
  
    - 5/Trang  
      
    - 10/Trang  
      
    - 20/Trang
      
### Kiểm tra giá trị phân trang mặc định

- Mặc định là 5
  
### Kiểm tra khi chọn giá trị là 5

- Hiển thị 5 bản ghi / trang  
  
### Kiểm tra khi chọn giá trị là 10

- Hiển thị 10 bản ghi / trang  
  
### Kiểm tra khi chọn giá trị là 20

- Hiển thị 20 bản ghi / trang

### Kiểm tra khi thay đổi lựa chọn đổi số lượng phân trang

- Client reload tìm kiếm và hiển thị grid giao dịch theo giá trị phân trang mới.

### Kiểm tra hiển thị số lượng bản ghi khi thay đổi số lượng phân trang

- Hiển thị tương ứng với tổng số lượng bản ghi server trả/ {số lượng bản ghi/trang}

### Kiểm tra khi click vào số trang

- Hiển thị danh sách các bản ghi ở trang đã chọn

### Kiểm tra khi click > khi đang ở trang 1

- Cho phép chuyển đến trang tiếp theo

### Kiểm tra khi click < khi đang ở trang 1

- Button < bị disable

### Kiểm tra khi click > khi đang ở trang khác trang 1

- Cho phép chuyển đến trang tiếp theo

### Kiểm tra khi click < khi đang ở trang khác trang 1

- Cho phép chuyển đến trang trước đó

### Kiểm tra khi click > khi đang ở trang cuối cùng

- Button > bị disable

## Kiểm tra chức năng

### Kiểm tra khi click button "Tìm kiếm"

#### Đối tượng khai báo

- Kiểm tra khi chọn "Đối tượng khai báo" = "Dịch vụ thu phí"

    - Hiển thị danh sách các bản ghi có loại đối tượng là Dịch vụ thu phí
    - `SELECT * FROM SEGMENT_FEE_CONFIG WHERE DOMAIN_TYPE = 1`

- Kiểm tra khi chọn "Đối tượng khai báo" = "Gói SPDV"

    - Hiển thị danh sách các bản ghi có loại đối tượng là Gói SPDV
    - `SELECT * FROM SEGMENT_FEE_CONFIG WHERE DOMAIN_TYPE = 2`

- Kiểm tra khi chọn "Đối tượng khai báo" = "Tất cả" (hoặc bỏ trống)

    - Hiển thị tất cả các loại đối tượng
    - `SELECT * FROM SEGMENT_FEE_CONFIG`

#### Dịch vụ thu phí/Gói SPDV

- Kiểm tra khi nhập/chọn giá trị [Dịch vụ/Gói] tồn tại

    - Hiển thị chính xác bản ghi thuộc dịch vụ/gói đã chọn
    - `SELECT * FROM SEGMENT_FEE_CONFIG WHERE FEE_SERVICE_CODE = '[Mã_Đã_Chọn]'`

- Kiểm tra khi nhập từ khóa tìm kiếm (text input) khớp một phần tên/mã

    - Dropdown hiển thị danh sách gợi ý chứa từ khóa (search client-side hoặc API filter)
    - Sau khi chọn giá trị từ gợi ý, lưới dữ liệu hiển thị bản ghi tương ứng

- Kiểm tra khi chọn giá trị không tồn tại (nếu cho phép nhập text)

    - Hiển thị thông báo không tìm thấy hoặc lưới dữ liệu rỗng

#### Trạng thái

- Kiểm tra khi chọn 1 trạng thái cụ thể (VD: Hoạt động)

    - Hiển thị các bản ghi có trạng thái tương ứng
    - `SELECT * FROM SEGMENT_FEE_CONFIG WHERE STATUS = 1`

- Kiểm tra khi chọn nhiều trạng thái (VD: Hoạt động + Tạo nháp)

    - Hiển thị các bản ghi thuộc tập hợp các trạng thái đã chọn
    - `SELECT * FROM SEGMENT_FEE_CONFIG WHERE STATUS IN (1, 2)`

- Kiểm tra khi chọn "Tất cả" trạng thái

    - Hiển thị bản ghi ở mọi trạng thái (Hoạt động, Không hoạt động, Tạo nháp, Chờ duyệt sửa)
    - `SELECT * FROM SEGMENT_FEE_CONFIG`

### Kiểm tra kết hợp tương tác giữa các fields

- Kiểm tra trạng thái mặc định của field "Dịch vụ thu phí/Gói SPDV" khi chưa chọn "Đối tượng khai báo"

    - Field "Dịch vụ thu phí/Gói SPDV" bị khóa (Disable)
    - Không thể nhập liệu hoặc chọn giá trị

- Kiểm tra khi chọn [Đối tượng khai báo] = "Dịch vụ thu phí"

    - Field "Dịch vụ thu phí/Gói SPDV" được mở (Enable)
    - Danh sách trong dropdown load dữ liệu từ API `/v1/dropdown/fee-service/active` (srvType = 1)

- Kiểm tra khi chọn [Đối tượng khai báo] = "Gói SPDV"

    - Field "Dịch vụ thu phí/Gói SPDV" được mở (Enable)
    - Danh sách trong dropdown load dữ liệu từ API `/v1/dropdown/pkg-grp/active`

- Kiểm tra khi thay đổi [Đối tượng khai báo] từ "Dịch vụ" sang "Gói SPDV"

    - Giá trị đã chọn tại field "Dịch vụ thu phí/Gói SPDV" (nếu có) bị clear
    - Dropdown reload dữ liệu mới tương ứng với Gói SPDV

- Kiểm tra quyền KSV khi vào màn hình (Mặc định)

    - Field "Trạng thái" tự động chọn giá trị "Chờ duyệt sửa" (Status = 4)
    - `SELECT * FROM SEGMENT_FEE_CONFIG WHERE STATUS = 4`

- Kiểm tra quyền GDV/User thường khi vào màn hình (Mặc định)

    - Field "Trạng thái" hiển thị placeholder "Chọn trạng thái" hoặc chọn mặc định theo cấu hình (nếu có)

### Kiểm tra tìm kiếm kết hợp tất cả các tiêu chí

- Kiểm tra khi chọn [Đối tượng] + chọn [Dịch vụ cụ thể] + chọn [Trạng thái]

    - Hiển thị kết quả thỏa mãn tất cả điều kiện
    - `SELECT * FROM SEGMENT_FEE_CONFIG WHERE DOMAIN_TYPE = [Type_Val] AND FEE_SERVICE_CODE = '[Code_Val]' AND STATUS = [Status_Val]`

### Kiểm tra khi click button "Xóa bộ lọc"

- Kiểm tra hành động click nút "Xóa bộ lọc"

    - Các field "Đối tượng khai báo", "Dịch vụ thu phí/Gói SPDV" reset về rỗng
    - Field "Dịch vụ thu phí/Gói SPDV" chuyển về trạng thái Disable (do Đối tượng khai báo rỗng)
    - Field "Trạng thái" reset về giá trị mặc định ban đầu (VD: KSV về 'Chờ duyệt sửa', User khác về rỗng)
    - Lưới dữ liệu reload lại theo điều kiện mặc định

### Kiểm tra khi click button "Xuất excel"

- Kiểm tra khi click "Xuất excel" với dữ liệu hiện tại

    - Hệ thống gọi API `/bo-service/v1/category/segment-fee-config/export`
    - Tải xuống file Excel chứa dữ liệu tương ứng với điều kiện tìm kiếm hiện tại

- Kiểm tra khi danh sách rỗng (Không có dữ liệu)

    - Button "Xuất excel" bị ẩn hoặc disable (theo logic "Chỉ hiển thị khi danh sách khác trống")

### Kiểm tra tương tác trên lưới dữ liệu (Grid)

- Kiểm tra hiển thị icon "Chỉnh sửa" (cột Thao tác)

    - Icon hiển thị với bản ghi có `STATUS != 0` (Khác "Không hoạt động") VÀ user có quyền Update
    - Icon ẩn với bản ghi có `STATUS = 0` ("Không hoạt động")

- Kiểm tra khi click icon "Chỉnh sửa"

    - Hiển thị popup/màn hình "Chỉnh sửa giá segment"
    - API lấy chi tiết được gọi thành công

- Kiểm tra khi Double Click vào dòng bản ghi

    - Chuyển hướng sang màn hình "Chi tiết Phí chính sách tự động" (View Detail)

- Kiểm tra phân trang (Pagination)

    - Thay đổi số lượng bản ghi/trang (5, 10, 20) -> Lưới hiển thị đúng số lượng row
    - Chuyển trang (Next/Prev) -> Dữ liệu load trang tiếp theo chính xác
    - `SELECT * FROM SEGMENT_FEE_CONFIG ORDER BY UPDATED_TIME DESC OFFSET [Start_Row] ROWS FETCH NEXT [Page_Size] ROWS ONLY`

## Kiểm tra timeout

### Kiểm tra khi server không nhận được phản hồi

- Hiển thị popup thông báo lỗi:
  
    - + Icon x  
      + Tiêu đề: "Lỗi"  
      + Nội dung: <Mã lỗi> : <Mô tả lỗi Server trả>  
      + Button: Đóng
      
### Kiểm tra khi Server trả lỗi tường minh

- Hiển thị popup thông báo lỗi:
  
    - + Button X: Nhấn đóng thông báo hiển thị màn hình đang thao tác  
      + icon x  
      + Tiêu đề: "Lỗi"  
      + Nội dung: <Mã lỗi> : <Mô tả lỗi Server trả>