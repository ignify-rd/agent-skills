# Ví dụ đầu ra

## Ví dụ 1: Frontend Test Design — Màn hình LIST

Đầu vào: RSD mô tả màn hình quản lý "Tần suất thu phí" với bộ lọc tìm kiếm, lưới dữ liệu, và các thao tác CRUD.

### Kết quả mong đợi:

```markdown
# WEB_BO_Danh mục > Tần suất thu phí - Test Design

## Kiểm tra giao diện chung

### Kiểm tra điều hướng đến màn hình Tần suất thu phí

- Điều hướng thành công đến màn hình Tần suất thu phí

### Kiểm tra bố cục giao diện tổng thể

- + Hiển thị theo đúng figma
  + Màn hình Tần suất thu phí hiển thị đầy đủ các thông tin:
  + Button Thêm mới
  + Dropdown Đối tượng khai báo
  + Textbox Tên tần suất
  + Button Tìm kiếm
  + Lưới dữ liệu
  + Phân trang

### Kiểm tra hiển thị breadcrumb

- Danh mục/ Tần suất thu phí

### Kiểm tra hiển thị bố cục layout cân đối

- Hiển thị đúng cỡ chữ, màu chữ, bố cục cân đối, kích thước chính xác, đúng chính tả

### Kiểm tra phóng to/thu nhỏ

- Màn hình không bị vỡ form

## Kiểm tra phân quyền

### Kiểm tra login user không có quyền

- Không view được màn hình

### Kiểm tra login user có quyền

- User có quyền thao tác chức năng truy vấn

## Kiểm tra validate

### Kiểm tra dropdown list "Đối tượng khai báo"

- Kiểm tra hiển thị mặc định
    - Luôn hiện và enable

- Kiểm tra giá trị mặc định
    - Mặc định rỗng

- Kiểm tra placeholder
    - Hiển thị placeholder "Chọn giá trị"

- Kiểm tra giá trị hiển thị khi nhấn chọn Dropdown list
    - Hiển thị danh sách các giá trị:
        - Tất cả
        - Cá nhân
        - Doanh nghiệp

- Kiểm tra khi chọn giá trị = "Cá nhân"
    - Hệ thống hiển thị text "Cá nhân" tại dropdown list

- Kiểm tra khi chọn giá trị = "Doanh nghiệp"
    - Hệ thống hiển thị text "Doanh nghiệp" tại dropdown list

- Kiểm tra hiển thị icon X khi chọn giá trị
    - Hiển thị icon X xóa nhanh ký tự nhập

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh giá trị đã chọn
    - Clear data đã chọn

### Kiểm tra textbox "Tên tần suất"

- Kiểm tra hiển thị mặc định
    - Luôn hiển thị và enable

- Kiểm tra giá trị mặc định
    - Mặc định rỗng

- Kiểm tra hiển thị icon X khi nhập 1 ký tự
    - Hiển thị icon X xóa nhanh ký tự nhập

- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh ký tự nhập
    - Clear data đã nhập ở textbox

- Kiểm tra khi nhập kí tự là số
    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự chữ
    - Hệ thống cho phép nhập

- Kiểm tra khi nhập kí tự đặc biệt
    - Hệ thống chặn không cho phép nhập

- Kiểm tra khi nhập kí tự chứa space đầu/cuối
    - Hệ thống cho phép nhập

- Kiểm tra khi nhập all space
    - Hệ thống cho phép nhập

- Kiểm tra khi nhập 99 kí tự
    - Hệ thống cho phép nhập

- Kiểm tra khi nhập 100 kí tự
    - Hệ thống cho phép nhập

- Kiểm tra khi Paste 100 kí tự
    - Hệ thống cho phép Paste

- Kiểm tra khi nhập 101 kí tự
    - Hiển thị cảnh báo "Tên tần suất không được vượt quá 100 ký tự"

## Kiểm tra lưới dữ liệu

### Kiểm tra mặc định

- Server trả về danh sách tần suất thu phí

### Kiểm tra hiển thị sắp xếp các bản ghi trên lưới dữ liệu

- Sắp xếp theo CREATED_TIME DESC
    - SELECT * FROM FEE_ENGINE.FEE_FREQUENCY ORDER BY CREATED_TIME DESC

### Kiểm tra cột "STT"

- Hiển thị số thứ tự tăng dần từ 1

### Kiểm tra cột "Tên tần suất"

- Hiển thị tên tần suất do server trả về
    - SELECT NAME FROM FEE_ENGINE.FEE_FREQUENCY WHERE ID = 10000001

### Kiểm tra cột "Đối tượng khai báo"

- Hiển thị tên đối tượng khai báo do server trả về
    - SELECT OBJ_TYPE_NAME FROM FEE_ENGINE.FEE_FREQUENCY WHERE ID = 10000001

### Kiểm tra cột "Trạng thái"

- Hiển thị trạng thái do server trả về
    - SELECT STATUS FROM FEE_ENGINE.FEE_FREQUENCY WHERE ID = 10000001

### Kiểm tra lưới dữ liệu khi kéo thanh cuộn ngang

- Khi cuộn ngang cố định các cột: STT

### Kiểm tra lưới dữ liệu khi kéo thanh cuộn dọc

- Cuộn dọc hiển thị các bản ghi tiếp theo

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

### Kiểm tra khi click > khi đang ở trang 1

- Cho phép chuyển đến trang tiếp theo

### Kiểm tra khi click < khi đang ở trang 1

- Button < bị disable

### Kiểm tra khi click > khi đang ở trang cuối cùng

- Button > bị disable

## Kiểm tra chức năng

### Kiểm tra chức năng Tìm kiếm

- Nhập điều kiện tìm kiếm hợp lệ và click Tìm kiếm
    - Hiển thị kết quả khớp với điều kiện

- Click Tìm kiếm khi không nhập điều kiện
    - Hiển thị toàn bộ danh sách

- Tìm kiếm không có kết quả
    - Hiển thị thông báo "Không có dữ liệu"

### Kiểm tra chức năng Thêm mới

- Click button Thêm mới
    - Mở popup/form thêm mới thành công

### Kiểm tra chức năng Xóa bộ lọc

- Click Xóa bộ lọc sau khi đã chọn điều kiện
    - Reset toàn bộ bộ lọc về trạng thái mặc định

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
```

## Ví dụ 2: API Test Design — Markdown output

Đầu vào: RSD mô tả API "Lấy danh sách danh mục active" (POST, 1 field PAR_TYPE string, maxLength=100).

### Kết quả mong đợi:

```markdown
# API Lấy danh sách danh mục active theo category_type

## Kiểm tra các case common

### Method

#### Kiểm tra truyền sai method (GET/PUT/DELETE)
- status: 107
- {
  "message": "Error retrieving AuthorInfo for token from TokenLib: Token is invalid signature"
  }

### URL

#### Kiểm tra truyền sai url
- status: 500
- {
  "message": "Access denied"
  }

### Kiểm tra phân quyền

#### Không có quyền
- status: 500
- {
  "message": "Access denied"
  }

#### Được phân quyền
- status: 200

## Kiểm tra validate

### PAR_TYPE: string

#### Để trống
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Không truyền
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền null
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Lấy danh sách active của tất cả các danh mục

#### Truyền PAR_TYPE = 99 ký tự
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền PAR_TYPE = 100 ký tự
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền PAR_TYPE = 101 ký tự
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE là ký tự số
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền PAR_TYPE là chữ(thường/hoa) không dấu
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền PAR_TYPE là chữ(thường/hoa) có dấu
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE là ký tự đặc biệt cho phép _
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response: Trả về response body đúng cấu trúc

#### Truyền PAR_TYPE là ký tự đặc biệt không cho phép
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE là all space
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE có space ở giữa
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE có space đầu / cuối
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE là emoji/icons (😀🏠⚡)
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE là ký tự Unicode đặc biệt (tiếng Trung, Nhật, Ả Rập...)
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE là boolean (true/false)
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE là mảng
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE là object
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE là XSS
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

#### Truyền PAR_TYPE là SQL INJECTION
- 1\. Check api trả về:
  1\.1. Status: 200
  1\.2. Response:
  {
    "message": "Dữ liệu không hợp lệ"
  }

## Kiểm tra luồng chính

### Kiểm tra response khi truyền PAR_TYPE tồn tại kết quả
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "errorCode": "0",
        "errorDesc": "",
        "total": 5,
        "items": [...]
      }
      SQL:
      SELECT * FROM PAR_COMMON
      WHERE PAR_TYPE = 'CUSTOMER_TYPE'
      ORDER BY PAR_TYPE ASC, PAR_CODE ASC;

### Kiểm tra response khi truyền PAR_TYPE không tồn tại kết quả
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "errorCode": "0",
        "errorDesc": "",
        "total": 0,
        "items": []
      }
      SQL:
      SELECT * FROM PAR_COMMON
      WHERE PAR_TYPE = 'KHONG_TON_TAI';

### Kiểm tra response trả ra đầy đủ các trường
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": [
          {
            "parType": "CUSTOMER_TYPE",
            "parCode": "01",
            "parName": "Khách hàng cá nhân",
            "status": 1
          }
        ]
      }
      SQL:
      SELECT PAR_TYPE, PAR_CODE, PAR_NAME, STATUS FROM PAR_COMMON
      WHERE PAR_TYPE = 'CUSTOMER_TYPE' AND STATUS = 1
      ORDER BY PAR_TYPE ASC, PAR_CODE ASC;

### Kiểm tra sắp xếp kết quả
- 1\. Check api trả về:
      1\.1. Status: 200
      1\.2. Response: Danh sách được sắp xếp theo PAR_TYPE ASC, PAR_CODE ASC
      SQL:
      SELECT * FROM PAR_COMMON
      ORDER BY PAR_TYPE ASC, PAR_CODE ASC;
```

