# BO_Phí định kỳ > Bộ lọc chính sách phí > Popup Xác nhận phê duyệt/ từ chối duyệt

## Kiểm tra giao diện chung

### Kiểm tra điều hướng đến màn hình Xác nhận phê duyệt / Từ chối duyệt

- Điều hướng thành công đến màn hình Xác nhận phê duyệt / Từ chối duyệt
  
### Kiểm tra bố cục giao diện tổng thể

- + Hiển thị theo đúng figma  
  + Màn hình Xác nhận phê duyệt / Từ chối duyệt hiển thị đầy đủ các thông tin:  
  + Popup Xác nhận phê duyệt:  
  + Icon - Close (X)  
  + Label - Tiêu đề: Xác nhận phê duyệt  
  + Label - Nội dung: Bạn có chắc chắn phê duyệt bản ghi này?  
  + Button - Đóng  
  + Button - Xác nhận  
  + Popup Xác nhận từ chối:  
  + Icon - Close (X)  
  + Label - Tiêu đề: Từ chối duyệt  
  + Textbox - Nhập lý do (kèm counter 0/160)  
  + Icon - Xóa nhanh (trong textbox)  
  + Button - Đóng  
  + Button - Xác nhận
  
### Kiểm tra hiển thị breadcrumb

- Phí định kỳ > Bộ lọc chính sách phí
  
### Kiểm tra hiển thị bố cục layout cân đối

- Hiển thị đúng cỡ chữ, màu chữ, bố cục cân đối, kích thước chính xác, đúng chính tả
  
### Kiểm tra phóng to/thu nhỏ

- Màn hình không bị vỡ form

## Kiểm tra phân quyền

### Kiểm tra login user không có quyền

- Không view được màn hình

### Header theo quy định authen user BO

- User có quyền thao tác chức năng truy vấn

## Kiểm tra validate

### Kiểm tra textbox "Nhập lý do"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "Nhập lý do"

- Kiểm tra hiển thị icon X khi nhập 1 ký tự

    - Hiển thị icon X xóa nhanh ký tự nhập

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh ký tự nhập

    - Clear data đã nhập ở textbox

- Kiểm tra khi nhập kí tự là số

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự chữ

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự đặc biệt

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập 1 phần kí tự

    - Cho phép nhập freetext

- Kiểm tra khi nhập kí tự chứa space đầu/cuối

    - Hệ thống cho phép nhập

- Kiểm tra khi Paste kí tự chứa space đầu/cuối

    - Hệ thống cho phép Paste

- Kiểm tra khi nhập all space

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập 159 kí tự

    - Hệ thống cho phép nhập

- Kiểm tra khi nhập 160 kí tự

    - Hệ thống cho phép nhập

- Kiểm tra khi Paste 160 kí tự

    - Hệ thống cho phép Paste

- Kiểm tra khi nhập 161 kí tự

    - Hiển thị cảnh báo "User nhập quá maxlength, Client chặn không cho nhập tiếp"

### Kiểm tra Button Xác nhận (Popup Phê duyệt)

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra hiển thị text, thiết kế của button

    - Hiển thị text "Xác nhận", thiết kết theo figma

### Kiểm tra Button Xác nhận (Popup Từ chối)

- Kiểm tra hiển thị

    - Mặc định enable

- Kiểm tra hiển thị text, thiết kế của button

    - Hiển thị text "Xác nhận", thiết kết theo figma

### Kiểm tra Button Đóng

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra hiển thị text, thiết kế của button

    - Hiển thị text "Đóng", thiết kết theo figma

- Kiểm tra trạng thái enable/disable của button "Xác nhận" dựa trên giá trị của trường "Nhập lý do" (Màn hình Từ chối)
    - Button "Xác nhận" ở trạng thái Disable khi trường "Nhập lý do" trống; chuyển sang trạng thái Enable khi người dùng đã nhập dữ liệu

- Kiểm tra hiển thị nội dung lỗi trên Popup thông báo khi API trả về lỗi nghiệp vụ
    - Tiêu đề là "Lỗi" và nội dung (Content) hiển thị đúng text `poErrorDesc` do server trả về

- Kiểm tra hiển thị nội dung lỗi trên Popup thông báo khi không nhận được phản hồi từ Server (Timeout/Network error)
    - Hiển thị popup với nội dung cố định: “Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại.”

- Kiểm tra luồng xử lý làm mới dữ liệu sau khi Phê duyệt hoặc Từ chối thành công
    - Sau khi đóng popup và hiện toast thông báo, hệ thống phải tự động gọi API `Service_API Lấy danh sách bộ lọc chính sách` để cập nhật lại lưới dữ liệu mới nhất

- Kiểm tra tính chính xác của dữ liệu gửi đi khi thực hiện hành động Từ chối
    - Body request gửi lên API phải có tham số `task: reject` và `rejectedMessage` lấy đúng giá trị từ trường "Nhập lý do" người dùng đã nhập

- Kiểm tra tính chính xác của dữ liệu gửi đi khi thực hiện hành động Phê duyệt
    - Body request gửi lên API phải có tham số `task: approve` và `rejectedMessage` có giá trị là `null`

## Kiểm tra lưới dữ liệu

### Kiểm tra mặc định

- Màn hình hiển thị dưới dạng Popup xác nhận (Phê duyệt hoặc Từ chối), không hiển thị danh sách bản ghi dưới dạng lưới dữ liệu (Grid).
- Các thành phần hiển thị bao gồm tiêu đề, nội dung thông báo (Label) hoặc ô nhập lý do (Textbox), và các nút thao tác.

### Kiểm tra hiển thị sắp xếp các bản ghi trên lưới dữ liệu

- Không áp dụng (Không có lưới dữ liệu).

### Kiểm tra lưới dữ liệu khi kéo thanh cuộn ngang

- Không áp dụng.

### Kiểm tra lưới dữ liệu khi kéo thanh cuộn dọc

- Không áp dụng.

### Kiểm tra dữ liệu trả về từ server

- Kiểm tra logic gọi API khi người dùng nhấn nút "Xác nhận":
    - API endpoint: `Service_API Phê duyệt/Từ chối`
    - Body input gửi lên server:
        - `segConfId`: ID của bản ghi master hiện tại (`SEG_CONF_ID`).
        - `task`: Giá trị `approve` (nếu Phê duyệt) hoặc `reject` (nếu Từ chối).
        - `rejectedMessage`: Giá trị `null` (nếu Phê duyệt) hoặc `[Lý do nhập từ giao diện]` (nếu Từ chối).
- Kiểm tra xử lý phản hồi từ server:
    - Nếu Server trả về thành công: Đóng popup hiện tại, hiển thị Toast notification thành công, reload lưới dữ liệu tại màn hình cha (Bộ lọc chính sách phí).
    - Nếu Server trả về lỗi (có `poErrorDesc`): Hiển thị Popup thông báo lỗi với nội dung từ server.
    - Nếu không nhận được phản hồi: Hiển thị Popup thông báo lỗi mặc định "Có lỗi xảy ra...".

## Kiểm tra "Phân trang"

### Kiểm tra giá trị phân trang khi không có dữ liệu

- Ẩn lưới dữ liệu
  
### Kiểm tra các giá trị số lượng bản ghi /trang

- Danh mục giá trị gồm:
  

      
### Kiểm tra giá trị phân trang mặc định

- Mặc định là 5
  


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

### Kiểm tra khi click button "Xác nhận" (Popup Phê duyệt)

#### Logic xử lý phê duyệt

- Kiểm tra khi click button "Xác nhận"

    - Gọi API `Service_API Phê duyệt/Từ chối`
    - Body: `task: approve`, `segConfId: [ID bản ghi]`, `rejectedMessage: null`
    - Đóng popup
    - Hiển thị toast notification thành công: "Phê duyệt thành công"
    - Gọi API `Service_API Lấy danh sách bộ lọc chính sách` để refresh lưới dữ liệu

- Kiểm tra trường hợp server trả về lỗi

    - Hiển thị popup thông báo lỗi modal
    - Tiêu đề: "Lỗi"
    - Content: Nội dung `poErrorDesc` từ server trả về
    - Button: "Đóng"

- Kiểm tra trường hợp không nhận được phản hồi từ server

    - Hiển thị popup thông báo lỗi modal
    - Tiêu đề: "Lỗi"
    - Content: "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."

### Kiểm tra các field trên Popup Từ chối

#### Nhập lý do (Textbox)

- Kiểm tra khi nhập văn bản (freetext)

    - Hiển thị đúng các ký tự đã nhập
    - Hiển thị nút "X" ở cuối textbox để xóa nhanh

- Kiểm tra khi nhập quá 160 ký tự

    - Hệ thống chặn không cho nhập tiếp ký tự thứ 161
    - Bộ đếm ký tự hiển thị: 160/160

- Kiểm tra khi click nút "X" trong textbox

    - Xóa toàn bộ nội dung trong textbox
    - Button "Xác nhận" chuyển sang trạng thái Disabled

### Kiểm tra kết hợp tương tác giữa các fields (Popup Từ chối)

- Kiểm tra khi textbox "Nhập lý do" bị bỏ trống

    - Button "Xác nhận" bị Disable (không thể click)

- Kiểm tra khi textbox "Nhập lý do" có dữ liệu (>= 1 ký tự)

    - Button "Xác nhận" Enable (có thể click)

### Kiểm tra khi click button "Xác nhận" (Popup Từ chối)

#### Logic xử lý từ chối

- Kiểm tra khi click button "Xác nhận" (đã nhập lý do)

    - Gọi API `Service_API Phê duyệt/Từ chối`
    - Body: `task: reject`, `id: [ID bản ghi]`, `rejectedMessage: [Giá trị textbox]`
    - Đóng popup
    - Hiển thị toast notification thành công: "Từ chối thành công" (Content: "Đã từ chối duyệt bản ghi thành công")
    - Gọi API `Service_API Lấy danh sách bộ lọc chính sách` để refresh lưới dữ liệu

### Kiểm tra các thao tác đóng Popup

#### Button "Đóng" và Icon "X"

- Kiểm tra khi click Button "Đóng" hoặc Icon "X" (trên cả 2 popup)

    - Đóng popup
    - Quay về màn hình danh sách/bộ lọc chính sách phí
    - Không thực hiện gọi API phê duyệt/từ chối

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