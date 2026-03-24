# BO_Phí định kỳ > Bộ lọc chính sách phí > Chi tiết bộ lọc > Chi tiết segment

## Kiểm tra giao diện chung

### Kiểm tra điều hướng đến màn hình Chi tiết segment

- Điều hướng thành công đến màn hình Chi tiết segment
  
### Kiểm tra bố cục giao diện tổng thể

- + Hiển thị theo đúng figma  
  + Màn hình Chi tiết segment hiển thị đầy đủ các thông tin:  
  + Badge - Trạng thái (hiển thị theo design, label lấy từ statusName)  
  + Button - X (Đóng popup)  
  + Textbox - Mã phí/ mã gói  
  + Textbox - Mức ưu tiên  
  + Textbox - Mã segment  
  + Textbox - Tên segment  
  + Textbox - Mô tả  
  + Textbox - Lỗi kiểm tra  
  + Textbox - Người tạo  
  + Textbox - Ngày tạo  
  + Textbox - Người cập nhật  
  + Textbox - Ngày cập nhật  
  + Textbox - Người duyệt  
  + Textbox - Ngày duyệt  
  + Section Header - Điều kiện chính sách tự động  
  + Label - Khai báo điều kiện  
  + Combobox - Loại kết hợp điều kiện (Và/Hoặc)  
  + Combobox - Bảng (Table)  
  + Combobox - Cột (Column)  
  + Combobox - Biểu thức (Operator)  
  + Textbox/Combobox - Giá trị (Value)  
  + Button - Chỉnh sửa
  
### Kiểm tra hiển thị bố cục layout cân đối

- Hiển thị đúng cỡ chữ, màu chữ, bố cục cân đối, kích thước chính xác, đúng chính tả
  
### Kiểm tra phóng to/thu nhỏ

- Màn hình không bị vỡ form

## Kiểm tra phân quyền

### Kiểm tra login user không có quyền

- Không hiển thị nút Chỉnh sửa

### Quyền update (GDV) và quyền approve (KSV)

- GDV: Hiển thị nút Chỉnh sửa (theo điều kiện status). KSV: Chỉ xem chi tiết.

## Kiểm tra validate

### Kiểm tra textbox "Trạng thái"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Trạng thái

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Mã phí/ mã gói"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Mã phí/ mã gói

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Mức ưu tiên"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Mức ưu tiên

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Mã segment"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Mã segment

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Tên segment"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Tên segment

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Mô tả"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Mô tả

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Lỗi kiểm tra"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Lỗi kiểm tra

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Người tạo"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Người tạo

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Ngày tạo"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Ngày tạo

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Người cập nhật"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Người cập nhật

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Ngày cập nhật"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Ngày cập nhật

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Người duyệt"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Người duyệt

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra textbox "Ngày duyệt"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Ngày duyệt

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra Combobox "Loại kết hợp điều kiện"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Có icon * thể hiện bắt buộc

- Kiểm tra khi bỏ trống

    - Hiển thị support text tại trường Loại kết hợp điều kiện "Vui lòng chọn giá trị"

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "null"

- Kiểm tra hiển thị icon x

    - Khi có giá trị được chọn, hiển thị icon x cho phép xoá nhanh

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh giá trị đã chọn

    - Clear data đã chọn

- Kiểm tra giá trị

    - Hiển thị danh sách giá trị theo server trả về


- Kiểm tra hiển thị khi không nhận được phản hồi của API

    - Hiển thị popup thông báo lỗi theo design modal lỗi với nội dung "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."

- Kiểm tra hiển thị khi nhận phản hồi lỗi

    - Hiển thị popup thông báo lỗi theo design modal lỗi với nội dung errorDesc server trả về

- Kiểm tra khi chọn giá trị trong Combobox

    - Kiểm tra khi chọn 1 giá trị

        - Hệ thống cho phép chọn

    - Kiểm tra khi chọn nhiều giá trị

        - Chỉ cho phép chọn 1

- Kiểm tra nhập ký tự

    - Không cho nhập, chỉ được chọn theo danh sách có sẵn

#### Textbox Tìm kiếm

- Kiểm tra mặc định

    - Hiển thị Placeholder: "Tìm kiếm"

- Kiểm tra focus

    - Mặc định focus Textbox tìm kiếm khi nhấn mở combobox

- Kiểm tra nhập số

    - Cho phép nhập

- Kiểm tra nhập chữ a-z A-Z

    - Cho phép nhập

- Kiểm tra nhập ký tự đặc biệt

    - Hệ thống chặn không cho phép nhập

- Kiểm tra nhập khoảng trắng

    - Cho phép nhập

- Kiểm tra định dạng của data trả về

    - Mỗi loại hiển thị dạng: logicOperator

- Kiểm tra khi nhập 99 kí tự

    - Hệ thống cho phép nhập 99 kí tự

- Kiểm tra khi nhập 100 kí tự

    - Hệ thống cho phép nhập 100 kí tự

- Nhập từ khoá tồn tại

    - Hiển thị kết quả tương ứng với từ khoá đã nhập

- Nhập từ khoá không tồn tại

    - Hiển thị Không tìm thấy tại Dropdown

- Nhập một phần từ khoá

    - Hiển thị kết quả chứa một phần từ khoá đã nhập

- Kiểm tra hiển thị khi nhấn tab

    - Cho phép nhấn tab để chuyển từ textbox tìm kiếm sang danh sách giá trị

- Kiểm tra hiển thị khi nhấn các phím mũi tên

    - Cho phép nhấn Gõ các phím mũi tên di chuyển để chuyển focus giữa các giá trị

- Kiểm tra chọn giá trị bằng chuột trái

    - Cho phép Chọn select bằng cách click chuột trái vào dòng giá trị

- Kiểm tra chọn giá trị bằng bàn phím

    - Cho phép Chọn select bằng cách focus và nhấn enter/SPACE

- Kiểm tra hiển thị giá trị sau khi chọn

    - Fill đúng text (tên) giá trị đã chọn và đóng combobox

- Kiểm tra danh sách giá trị trong Combobox

    - Danh sách hiển thị theo thứ tự server trả về:

        + Mỗi loại hiển thị dạng: logicOperator


### Kiểm tra Combobox "Bảng"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Có icon * thể hiện bắt buộc

- Kiểm tra khi bỏ trống

    - Hiển thị support text tại trường Bảng "Vui lòng chọn giá trị"

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "null"

- Kiểm tra hiển thị icon x

    - Khi có giá trị được chọn, hiển thị icon x cho phép xoá nhanh

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh giá trị đã chọn

    - Clear data đã chọn

- Kiểm tra giá trị

    - Hiển thị data UI map với response API. Endpoint: API Lấy danh sách miền dữ liệu tại CDP


- Kiểm tra hiển thị khi không nhận được phản hồi của API API Lấy danh sách miền dữ liệu tại CDP

    - Hiển thị popup thông báo lỗi theo design modal lỗi với nội dung "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."

- Kiểm tra hiển thị khi nhận phản hồi lỗi

    - Hiển thị popup thông báo lỗi theo design modal lỗi với nội dung errorDesc server trả về

- Kiểm tra khi chọn giá trị trong Combobox

    - Kiểm tra khi chọn 1 giá trị

        - Hệ thống cho phép chọn

    - Kiểm tra khi chọn nhiều giá trị

        - Chỉ cho phép chọn 1

- Kiểm tra nhập ký tự

    - Không cho nhập, chỉ được chọn theo danh sách có sẵn

#### Textbox Tìm kiếm

- Kiểm tra mặc định

    - Hiển thị Placeholder: "Tìm kiếm"

- Kiểm tra focus

    - Mặc định focus Textbox tìm kiếm khi nhấn mở combobox

- Kiểm tra nhập số

    - Cho phép nhập

- Kiểm tra nhập chữ a-z A-Z

    - Cho phép nhập

- Kiểm tra nhập ký tự đặc biệt

    - Hệ thống chặn không cho phép nhập

- Kiểm tra nhập khoảng trắng

    - Cho phép nhập

- Kiểm tra định dạng của data trả về

    - Mỗi loại hiển thị dạng: description

- Kiểm tra khi nhập 99 kí tự

    - Hệ thống cho phép nhập 99 kí tự

- Kiểm tra khi nhập 100 kí tự

    - Hệ thống cho phép nhập 100 kí tự

- Nhập từ khoá tồn tại

    - Hiển thị kết quả tương ứng với từ khoá đã nhập

- Nhập từ khoá không tồn tại

    - Hiển thị Không tìm thấy tại Dropdown

- Nhập một phần từ khoá

    - Hiển thị kết quả chứa một phần từ khoá đã nhập

- Kiểm tra hiển thị khi nhấn tab

    - Cho phép nhấn tab để chuyển từ textbox tìm kiếm sang danh sách giá trị

- Kiểm tra hiển thị khi nhấn các phím mũi tên

    - Cho phép nhấn Gõ các phím mũi tên di chuyển để chuyển focus giữa các giá trị

- Kiểm tra chọn giá trị bằng chuột trái

    - Cho phép Chọn select bằng cách click chuột trái vào dòng giá trị

- Kiểm tra chọn giá trị bằng bàn phím

    - Cho phép Chọn select bằng cách focus và nhấn enter/SPACE

- Kiểm tra hiển thị giá trị sau khi chọn

    - Fill đúng text (tên) giá trị đã chọn và đóng combobox

- Kiểm tra danh sách giá trị trong Combobox

    - Danh sách hiển thị theo thứ tự server trả về:

        + Mỗi loại hiển thị dạng: description


### Kiểm tra Combobox "Cột"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Có icon * thể hiện bắt buộc

- Kiểm tra khi bỏ trống

    - Hiển thị support text tại trường Cột "Vui lòng chọn giá trị"

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "null"

- Kiểm tra hiển thị icon x

    - Khi có giá trị được chọn, hiển thị icon x cho phép xoá nhanh

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh giá trị đã chọn

    - Clear data đã chọn

- Kiểm tra giá trị

    - Hiển thị data UI map với response API. Endpoint: API Lấy danh sách thuộc tính tại CDP


- Kiểm tra hiển thị khi không nhận được phản hồi của API API Lấy danh sách thuộc tính tại CDP

    - Hiển thị popup thông báo lỗi theo design modal lỗi với nội dung "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."

- Kiểm tra hiển thị khi nhận phản hồi lỗi

    - Hiển thị popup thông báo lỗi theo design modal lỗi với nội dung errorDesc server trả về

- Kiểm tra khi chọn giá trị trong Combobox

    - Kiểm tra khi chọn 1 giá trị

        - Hệ thống cho phép chọn

    - Kiểm tra khi chọn nhiều giá trị

        - Chỉ cho phép chọn 1

- Kiểm tra nhập ký tự

    - Không cho nhập, chỉ được chọn theo danh sách có sẵn

#### Textbox Tìm kiếm

- Kiểm tra mặc định

    - Hiển thị Placeholder: "Tìm kiếm"

- Kiểm tra focus

    - Mặc định focus Textbox tìm kiếm khi nhấn mở combobox

- Kiểm tra nhập số

    - Cho phép nhập

- Kiểm tra nhập chữ a-z A-Z

    - Cho phép nhập

- Kiểm tra nhập ký tự đặc biệt

    - Hệ thống chặn không cho phép nhập

- Kiểm tra nhập khoảng trắng

    - Cho phép nhập

- Kiểm tra định dạng của data trả về

    - Mỗi loại hiển thị dạng: description

- Kiểm tra khi nhập 99 kí tự

    - Hệ thống cho phép nhập 99 kí tự

- Kiểm tra khi nhập 100 kí tự

    - Hệ thống cho phép nhập 100 kí tự

- Nhập từ khoá tồn tại

    - Hiển thị kết quả tương ứng với từ khoá đã nhập

- Nhập từ khoá không tồn tại

    - Hiển thị Không tìm thấy tại Dropdown

- Nhập một phần từ khoá

    - Hiển thị kết quả chứa một phần từ khoá đã nhập

- Kiểm tra hiển thị khi nhấn tab

    - Cho phép nhấn tab để chuyển từ textbox tìm kiếm sang danh sách giá trị

- Kiểm tra hiển thị khi nhấn các phím mũi tên

    - Cho phép nhấn Gõ các phím mũi tên di chuyển để chuyển focus giữa các giá trị

- Kiểm tra chọn giá trị bằng chuột trái

    - Cho phép Chọn select bằng cách click chuột trái vào dòng giá trị

- Kiểm tra chọn giá trị bằng bàn phím

    - Cho phép Chọn select bằng cách focus và nhấn enter/SPACE

- Kiểm tra hiển thị giá trị sau khi chọn

    - Fill đúng text (tên) giá trị đã chọn và đóng combobox

- Kiểm tra danh sách giá trị trong Combobox

    - Danh sách hiển thị theo thứ tự server trả về:

        + Mỗi loại hiển thị dạng: description


### Kiểm tra Combobox "Biểu thức"

- Kiểm tra hiển thị mặc định

    - Luôn hiển thị và enable

- Có icon * thể hiện bắt buộc

- Kiểm tra khi bỏ trống

    - Hiển thị support text tại trường Biểu thức "Vui lòng chọn giá trị"

- Kiểm tra giá trị mặc định

    - Mặc định rỗng

- Kiểm tra placeholder

    - Hiển thị placeholder "null"

- Kiểm tra hiển thị icon x

    - Khi có giá trị được chọn, hiển thị icon x cho phép xoá nhanh

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh giá trị đã chọn

    - Clear data đã chọn

- Kiểm tra giá trị

    - Hiển thị data UI map với response API. Endpoint: Service_API Chi tiết segment


- Kiểm tra hiển thị khi không nhận được phản hồi của API Service_API Chi tiết segment

    - Hiển thị popup thông báo lỗi theo design modal lỗi với nội dung "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."

- Kiểm tra hiển thị khi nhận phản hồi lỗi

    - Hiển thị popup thông báo lỗi theo design modal lỗi với nội dung errorDesc server trả về

- Kiểm tra khi chọn giá trị trong Combobox

    - Kiểm tra khi chọn 1 giá trị

        - Hệ thống cho phép chọn

    - Kiểm tra khi chọn nhiều giá trị

        - Chỉ cho phép chọn 1

- Kiểm tra nhập ký tự

    - Không cho nhập, chỉ được chọn theo danh sách có sẵn

#### Textbox Tìm kiếm

- Kiểm tra mặc định

    - Hiển thị Placeholder: "Tìm kiếm"

- Kiểm tra focus

    - Mặc định focus Textbox tìm kiếm khi nhấn mở combobox

- Kiểm tra nhập số

    - Cho phép nhập

- Kiểm tra nhập chữ a-z A-Z

    - Cho phép nhập

- Kiểm tra nhập ký tự đặc biệt

    - Hệ thống chặn không cho phép nhập

- Kiểm tra nhập khoảng trắng

    - Cho phép nhập

- Kiểm tra khi nhập 99 kí tự

    - Hệ thống cho phép nhập 99 kí tự

- Kiểm tra khi nhập 100 kí tự

    - Hệ thống cho phép nhập 100 kí tự

- Nhập từ khoá tồn tại

    - Hiển thị kết quả tương ứng với từ khoá đã nhập

- Nhập từ khoá không tồn tại

    - Hiển thị Không tìm thấy tại Dropdown

- Nhập một phần từ khoá

    - Hiển thị kết quả chứa một phần từ khoá đã nhập

- Kiểm tra hiển thị khi nhấn tab

    - Cho phép nhấn tab để chuyển từ textbox tìm kiếm sang danh sách giá trị

- Kiểm tra hiển thị khi nhấn các phím mũi tên

    - Cho phép nhấn Gõ các phím mũi tên di chuyển để chuyển focus giữa các giá trị

- Kiểm tra chọn giá trị bằng chuột trái

    - Cho phép Chọn select bằng cách click chuột trái vào dòng giá trị

- Kiểm tra chọn giá trị bằng bàn phím

    - Cho phép Chọn select bằng cách focus và nhấn enter/SPACE

- Kiểm tra hiển thị giá trị sau khi chọn

    - Fill đúng text (tên) giá trị đã chọn và đóng combobox

### Kiểm tra textbox "Giá trị"

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhập vào trường Giá trị

    - Textbox ở trạng thái Read Only / Disabled

### Kiểm tra Button Chỉnh sửa

- Kiểm tra hiển thị

    - Mặc định enable

- Kiểm tra hiển thị text, thiết kế của button

    - Hiển thị text "Chỉnh sửa", thiết kết theo figma

### Kiểm tra Close (X)

- Kiểm tra hiển thị

    - Luôn hiển thị và enable

- Kiểm tra khi nhấn đóng popup đang thao tác

    - Đóng popup

- Kiểm tra hiển thị nút "Chỉnh sửa" khi bản ghi Master có trạng thái là "Chờ duyệt khoá" (Status = 5)
    - Nút "Chỉnh sửa" bị ẩn (không hiển thị)

- Kiểm tra hiển thị nút "Chỉnh sửa" khi bản ghi Master có trạng thái khác "Chờ duyệt khoá" (Status != 5) và user có quyền update
    - Nút "Chỉnh sửa" hiển thị và cho phép click

- Kiểm tra hiển thị trường "Mức ưu tiên" khi API trả về isPriority = 0
    - Ẩn hoàn toàn cả Label và Giá trị của trường "Mức ưu tiên"

- Kiểm tra hiển thị trường "Mức ưu tiên" khi API trả về isPriority = 1
    - Hiển thị Label và Giá trị priorityLevel từ API

- Kiểm tra hiển thị các trường thông tin bổ sung (Mô tả, Lỗi kiểm tra, Người tạo, Ngày tạo, Người duyệt...) khi API trả về giá trị null hoặc rỗng
    - Ẩn hoàn toàn cả Label và Giá trị của trường tương ứng (không hiển thị vùng trống)

- Kiểm tra hiển thị tên "Bảng" và "Cột" trong lưới điều kiện
    - Hiển thị Mô tả tiếng Việt (Description) được lấy từ API danh sách miền dữ liệu/thuộc tính của CDP (không hiển thị Mã code lưu trong bảng segmentConditionCol)

- Kiểm tra hiển thị "Giá trị" trong lưới điều kiện khi cột có Type = COMBOBOX hoặc MULTI_COMBOBOX
    - Hiển thị Text mô tả được lấy từ API danh sách giá trị thuộc tính của CDP (không hiển thị Value code lưu trong database)

- Kiểm tra hiển thị "Giá trị" trong lưới điều kiện khi cột có Type = NUMBER/TEXT/CALENDAR
    - Hiển thị nguyên giá trị (raw value) từ trường segmentConditionCol mà server trả về

- Kiểm tra hiển thị Loại kết hợp điều kiện khi API trả về logicOperator = AND
    - Hiển thị text là "Và"

- Kiểm tra hiển thị Loại kết hợp điều kiện khi API trả về logicOperator = OR
    - Hiển thị text là "Hoặc"

- Kiểm tra xử lý khi gọi API Chi tiết segment thành công nhưng 1 trong các API phụ trợ (lấy Meta data từ CDP/ESB) bị lỗi
    - Hiển thị popup thông báo lỗi theo design modal và không hiển thị màn hình chi tiết

- Kiểm tra hiển thị danh sách giá trị trong cột "Giá trị" khi Type = MULTI_COMBOBOX và có nhiều giá trị được chọn
    - Các text mô tả hiển thị cách nhau bởi dấu phẩy (,)

## Kiểm tra lưới dữ liệu

### Kiểm tra mặc định

- Kiểm tra hiển thị danh sách "Điều kiện chính sách tự động" khi vào màn hình chi tiết:
    - Danh sách hiển thị đúng số lượng bản ghi điều kiện trả về từ API.
    - Nếu API trả về danh sách rỗng, lưới dữ liệu không hiển thị dòng nào.

### Kiểm tra hiển thị sắp xếp các bản ghi trên lưới dữ liệu

- Kiểm tra thứ tự hiển thị các dòng điều kiện:
    - Hiển thị theo đúng thứ tự cấp biểu thức trong nhóm điều kiện (`segmentConditionCol`) do server trả về (theo index của mảng JSON hoặc ID tăng dần).
    - SELECT * FROM SEGMENT_CONDITION WHERE SEGMENT_ID = '{id}' ORDER BY ID ASC

### Kiểm tra cột "Loại kết hợp điều kiện"

- Hiển thị thông tin `logicOperator` do server trả về theo DB:
    - SELECT LOGIC_OPERATOR FROM SEGMENT_CONDITION WHERE SEGMENT_ID = '{id}' ORDER BY ID ASC
- Kiểm tra hiển thị theo định dạng đặc biệt:
    - Nếu giá trị là "AND" hiển thị: "Và"
    - Nếu giá trị là "OR" hiển thị: "Hoặc"

### Kiểm tra cột "Bảng"

- Hiển thị thông tin `table` (mã bảng) do server trả về theo DB:
    - SELECT TABLE_NAME FROM SEGMENT_CONDITION WHERE SEGMENT_ID = '{id}' ORDER BY ID ASC
- Kiểm tra hiển thị theo định dạng đặc biệt:
    - Hiển thị Mô tả (Description) của bảng lấy từ hệ thống CDP (mapping mã bảng với danh sách miền dữ liệu CDP).

### Kiểm tra cột "Cột"

- Hiển thị thông tin `column` (mã cột) do server trả về theo DB:
    - SELECT COLUMN_NAME FROM SEGMENT_CONDITION WHERE SEGMENT_ID = '{id}' ORDER BY ID ASC
- Kiểm tra hiển thị theo định dạng đặc biệt:
    - Hiển thị Mô tả (Description) của cột lấy từ hệ thống CDP (mapping mã cột với danh sách thuộc tính CDP).

### Kiểm tra cột "Biểu thức"

- Hiển thị thông tin `conditions` (toán tử) do server trả về theo DB:
    - SELECT OPERATOR FROM SEGMENT_CONDITION WHERE SEGMENT_ID = '{id}' ORDER BY ID ASC

### Kiểm tra cột "Giá trị"

- Hiển thị thông tin `value` do server trả về theo DB:
    - SELECT VALUE FROM SEGMENT_CONDITION WHERE SEGMENT_ID = '{id}' ORDER BY ID ASC
- Kiểm tra hiển thị theo định dạng đặc biệt:
    - Nếu cột có type = NUMBER/TEXT/CALENDAR: Hiển thị giá trị gốc (Text/Number/Date).
    - Nếu cột có type = COMBOBOX/MULTI_COMBOBOX: Hiển thị Text lấy từ hệ thống CDP (mapping value với danh sách giá trị thuộc tính CDP).
    - Các giá trị cách nhau bởi dấu phẩy ",".

### Kiểm tra lưới dữ liệu khi kéo thanh cuộn ngang

- Khi cuộn ngang không có cột nào bị cố định (hoặc theo thiết kế chung của table component).

### Kiểm tra lưới dữ liệu khi kéo thanh cuộn dọc

- Khi số lượng điều kiện vượt quá chiều cao vùng hiển thị, thanh cuộn dọc xuất hiện.
- Kéo thanh cuộn dọc, header của lưới (nếu có) giữ nguyên, nội dung các dòng điều kiện trượt tương ứng.

### Kiểm tra dữ liệu trả về từ server

- Verify dữ liệu hiển thị trên lưới khớp với response từ API `Chi tiết segment` (trường `segmentConditionCol`):
    - So sánh số lượng dòng.
    - So sánh nội dung từng ô dữ liệu sau khi đã map (Logic Operator, Table Description, Column Description, Operator, Value Text).

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

### Kiểm tra hiển thị dữ liệu khi mở màn hình (Khởi tạo)

#### Các field thông tin chung (Read-only)

- Kiểm tra hiển thị dữ liệu khi mở popup chi tiết segment

    - Hiển thị đúng dữ liệu trả về từ server, khớp với database
    - Header hiển thị: "Chi tiết segment" + Badge trạng thái (label lấy theo statusName)
    - [SQL query: SELECT ID, SEGMENT_NAME, SEGMENT_DESC, PREVIEW_MESSAGE, CREATED_USER, CREATED_TIME, UPDATED_USER, UPDATED_TIME, APPROVED_USER, APPROVED_TIME FROM SEGMENT_TABLE WHERE ID = 'input_id']

- Kiểm tra hiển thị field [Mã phí/ mã gói]

    - Hiển thị format: `{feeCode} - {feeCodeName}`
    - [SQL query: SELECT FEE_CODE, FEE_CODE_NAME FROM SERVICE_TABLE WHERE ID = 'service_id']

- Kiểm tra field [Mô tả], [Lỗi kiểm tra], [Người duyệt], [Ngày duyệt] khi giá trị là null/empty

    - Không hiển thị field (ẩn cả label và giá trị)

- Kiểm tra định dạng ngày tháng (Ngày tạo, cập nhật, duyệt)

    - Hiển thị đúng định dạng: `dd/mm/yyyy HH:mm:ss`

#### Mức ưu tiên

- Kiểm tra khi bản ghi master có `isPriority = 0`

    - Ẩn field "Mức ưu tiên" (ẩn cả label và giá trị)
    - [SQL query: SELECT IS_PRIORITY FROM MASTER_TABLE WHERE ID = 'id']

- Kiểm tra khi bản ghi master có `isPriority = 1`

    - Hiển thị field "Mức ưu tiên"
    - Giá trị hiển thị lấy từ `priorityLevel`

### Kiểm tra logic hiển thị Section "Điều kiện chính sách tự động"

#### Hiển thị cấu trúc điều kiện (Dynamic Fields)

- Kiểm tra hiển thị [Loại kết hợp điều kiện]

    - Nếu `logicOperator = AND` → Hiển thị "Và"
    - Nếu `logicOperator = OR` → Hiển thị "Hoặc"
    - Hiển thị lồng nhau đúng cấp bậc như response trả về

- Kiểm tra hiển thị [Bảng] và [Cột]

    - Hiển thị Description tiếng Việt lấy từ API ESB/CDP (không hiển thị mã code raw)
    - Gọi API lấy danh sách miền dữ liệu CDP để map tên Bảng
    - Gọi API lấy danh sách thuộc tính CDP để map tên Cột

- Kiểm tra hiển thị [Biểu thức]

    - Hiển thị giá trị toán tử (VD: =, >, <, LIKE...) từ `segmentConditionCol`

#### Hiển thị Giá trị (Value) của điều kiện

- Kiểm tra khi [Cột] có type = NUMBER / TEXT / CALENDAR

    - Hiển thị dạng Textbox (Readonly)
    - Giá trị hiển thị là value gốc từ server

- Kiểm tra khi [Cột] có type = COMBOBOX / MULTI_COMBOBOX

    - Hiển thị dạng Combobox (Readonly)
    - Giá trị hiển thị là Text tiếng Việt (được map từ API lấy danh sách giá trị thuộc tính CDP)
    - Nếu là Multi-combobox, các giá trị cách nhau bởi dấu phẩy (,)

### Kiểm tra khi click button "Chỉnh sửa"

#### Logic ẩn/hiện button (Business Rule)

- Kiểm tra khi User có quyền `update` + Trạng thái bản ghi master != 5 (Khác "Chờ duyệt khoá")

    - Button "Chỉnh sửa" hiển thị
    - Button ở trạng thái Enable

- Kiểm tra khi User KHÔNG có quyền `update` HOẶC Trạng thái bản ghi master = 5 ("Chờ duyệt khoá")

    - Button "Chỉnh sửa" KHÔNG hiển thị

#### Hành động click button

- Kiểm tra khi click button "Chỉnh sửa"

    - Mở popup "Chỉnh sửa segment" (theo luồng 2.6.5)
    - Popup hiện tại đóng lại hoặc bị đè lên (theo design system)

### Kiểm tra khi click icon "X" (Close)

- Kiểm tra khi click icon X ở góc trên bên phải

    - Đóng popup "Chi tiết segment"
    - Quay lại màn hình danh sách/màn hình trước đó
    - Không lưu bất kỳ thay đổi nào (vì là màn hình view)

### Kiểm tra xử lý API và Lỗi (Integration Test)

- Kiểm tra khi gọi API `Service_API Chi tiết segment` thành công

    - Hiển thị popup và dữ liệu đầy đủ

- Kiểm tra khi gọi API `Service_API Chi tiết segment` thất bại (Server error/Timeout)

    - Hiển thị popup thông báo lỗi modal
    - Title: "Lỗi"
    - Content: Nội dung `errorDesc` từ server trả về hoặc message mặc định
    - Button: "Đóng" (click để tắt popup lỗi, popup chi tiết không mở)

- Kiểm tra khi gọi API tích hợp ESB/CDP thất bại (1 trong các API map data)

    - Hiển thị popup thông báo lỗi modal
    - Title: "Lỗi"
    - Content: "Có lỗi xảy ra trong quá trình xử lý..." hoặc nội dung từ ESB
    - Popup chi tiết segment KHÔNG hiển thị dữ liệu sai/thiếu

- Kiểm tra khi Client BO gọi Server nhưng không nhận được phản hồi

    - Hiển thị popup lỗi: "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."

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