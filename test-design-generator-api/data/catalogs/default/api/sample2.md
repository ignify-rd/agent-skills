# API Danh sách gói hợp lệ để đăng ký - Cung cấp cho SCH qua trục ESB

## Kiểm tra các case common

### Method

#### Kiểm tra truyền sai method (POST/PUT/DELETE)
- status: 405

### URL

#### Kiểm tra truyền sai url
- status: 500

### Kiểm tra token

#### Không hợp lệ
- status: 107

#### Hết hạn
- status: 401

### Kiểm tra phân quyền

#### Không có quyền
- status: 500

#### Được phân quyền
- status: 200

## Kiểm tra validate

### regBranch : String (Required)

#### Để trống
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Không truyền
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền null
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền regBranch là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền regBranch là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền regBranch là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch là ký tự đặc biệt cho phép _
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền regBranch là ký tự đặc biệt không cho phép
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch là emoji/icons (😀🏠⚡)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch là ký tự Unicode đặc biệt (tiếng Trung, Nhật, Ả Rập...)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch là boolean (true/false)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch là XSS
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regBranch là SQL INJECTION
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền regBranch không tồn tại trong bảng danh mục chi nhánh (CAT_BRANCH) hoặc trạng thái không hoạt động (STATUS != 1)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "PRPC_011",
        "poErrorDesc": "Mã chi nhánh không hợp lệ"
      }

### pkgGroupCode : String (Optional)

#### Để trống
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Không truyền
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền null
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc


#### Truyền pkgGroupCode là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgGroupCode là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgGroupCode là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode là ký tự đặc biệt cho phép _
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgGroupCode là ký tự đặc biệt không cho phép
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode là emoji/icons (😀🏠⚡)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode là ký tự Unicode đặc biệt (tiếng Trung, Nhật, Ả Rập...)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode là boolean (true/false)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode là XSS
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgGroupCode là SQL INJECTION
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


### cusSubType : String (Optional)

#### Để trống
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Không truyền
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền null
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc


#### Truyền cusSubType là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền cusSubType là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền cusSubType là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType là ký tự đặc biệt cho phép _
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền cusSubType là ký tự đặc biệt không cho phép
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType là emoji/icons (😀🏠⚡)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType là ký tự Unicode đặc biệt (tiếng Trung, Nhật, Ả Rập...)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType là boolean (true/false)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType là XSS
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cusSubType là SQL INJECTION
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


### page : Integer (Optional)

#### Để trống
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Không truyền
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền null
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền page là số âm
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là số thập phân (VD: 1.5)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là số có leading zero (VD: 00123)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là số rất lớn vượt giới hạn Integer
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là chuỗi ký tự (VD: "abc")
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là chuỗi chữ lẫn số (VD: "10abc000")
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là ký tự đặc biệt (VD: @#$%, *, -, +)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page có space đầu/cuối (VD: " 123 ", "123 ")
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là emoji/icons (😀🏠⚡)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là ký tự Unicode đặc biệt (tiếng Trung, Nhật, Ả Rập...)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là boolean (true/false)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là XSS
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền page là SQL INJECTION
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


### size : Integer (Optional)

#### Để trống
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Không truyền
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền null
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền size là số âm
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là số thập phân (VD: 1.5)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là số có leading zero (VD: 00123)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là số rất lớn vượt giới hạn Integer
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là chuỗi ký tự (VD: "abc")
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là chuỗi chữ lẫn số (VD: "10abc000")
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là ký tự đặc biệt (VD: @#$%, *, -, +)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size có space đầu/cuối (VD: " 123 ", "123 ")
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là emoji/icons (😀🏠⚡)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là ký tự Unicode đặc biệt (tiếng Trung, Nhật, Ả Rập...)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là boolean (true/false)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là XSS
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền size là SQL INJECTION
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


### orders : String (Optional)

#### Để trống
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Không truyền
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền null
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc


#### Truyền orders là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền orders là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền orders là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders là ký tự đặc biệt cho phép _
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền orders là ký tự đặc biệt không cho phép
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders là emoji/icons (😀🏠⚡)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders là ký tự Unicode đặc biệt (tiếng Trung, Nhật, Ả Rập...)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders là boolean (true/false)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders là XSS
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền orders là SQL INJECTION
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


## Kiểm tra luồng chính

### Kiểm tra lấy danh sách gói áp dụng Toàn hệ thống (Scope=1)
- 1\. Check api trả về:
      1.1. Status: 0
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "total": 1,
        "data": [
          {
            "pkgGroupCode": "CAMP_2024_ALL",
            "pkgGroupName": "Gói ưu đãi toàn quốc 2024",
            "scopeType": "1",
            "unitCodes": null,
            "typeCode": "KHDN,KHCN",
            "updatedDate": "2024-01-15 08:00:00",
            "pkgList": [
              {
                "pkgCode": "FEE_PKG_01",
                "pkgName": "Gói miễn phí chuyển tiền",
                "pkgDesc": "Miễn phí 100% phí chuyển tiền"
              }
            ]
          }
        ]
      }
      SQL:
      SELECT g.GRP_CODE, g.GRP_NAME, g.SCOPE_TYPE, g.UPDATED_DATE, 
             p.PKG_CODE, p.PKG_NAME, p.PKG_DESC
      FROM CAT_PKG_GRP g
      JOIN CAT_PKG p ON g.GRP_CODE = p.GRP_CODE
      WHERE g.STATUS = 1 
      AND g.SCOPE_TYPE = 1
      AND TRUNC(SYSDATE) BETWEEN g.SALE_START_DATE AND g.SALE_END_DATE
      AND p.STATUS = 1
      ORDER BY g.GRP_CODE ASC, g.UPDATED_DATE DESC;

### Kiểm tra lấy danh sách gói theo Địa bàn tỉnh (Scope=2)
- 1\. Check api trả về:
      1.1. Status: 0
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "total": 1,
        "data": [
          {
            "pkgGroupCode": "CAMP_HANOI",
            "pkgGroupName": "Ưu đãi khu vực Hà Nội",
            "scopeType": "2",
            "unitCodes": "HNO,HBI",
            "updatedDate": "2024-02-01 10:00:00",
            "pkgList": [
              {
                "pkgCode": "HN_PKG_01",
                "pkgName": "Gói tài khoản số đẹp Hà Nội",
                "pkgDesc": null
              }
            ]
          }
        ]
      }
      SQL:
      SELECT g.* 
      FROM CAT_PKG_GRP g
      JOIN CAT_BRANCH b ON b.BRANCH_CODE = '001' -- Input regBranch
      WHERE g.STATUS = 1
      AND g.SCOPE_TYPE = 2 
      AND INSTR(g.UNIT_CODES, b.PROVINCE_CODE) > 0
      ORDER BY g.GRP_CODE ASC;

### Kiểm tra lấy danh sách gói theo Chi nhánh cụ thể (Scope=3)
- 1\. Check api trả về:
      1.1. Status: 0
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "total": 1,
        "data": [
          {
            "pkgGroupCode": "CAMP_BR_001",
            "pkgGroupName": "Tri ân khách hàng CN Sở Giao Dịch",
            "scopeType": "3",
            "unitCodes": "001,002",
            "updatedDate": "2024-03-10 09:30:00",
            "pkgList": [
              {
                "pkgCode": "VIP_BR_01",
                "pkgName": "Gói VIP Branch",
                "pkgDesc": "Dành riêng cho CN 001"
              }
            ]
          }
        ]
      }
      SQL:
      SELECT g.* 
      FROM CAT_PKG_GRP g
      WHERE g.STATUS = 1
      AND g.SCOPE_TYPE = 3
      AND INSTR(g.UNIT_CODES, '001') > 0 -- Input regBranch
      ORDER BY g.GRP_CODE ASC;

### Kiểm tra tìm kiếm chính xác theo Mã chiến dịch (pkgGroupCode)
- 1\. Check api trả về:
      1.1. Status: 0
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "total": 1,
        "data": [
          {
            "pkgGroupCode": "TARGET_CAMP_01",
            "pkgGroupName": "Chiến dịch mục tiêu tháng 10",
            "scopeType": "1",
            "updatedDate": "2024-10-01 08:00:00",
            "pkgList": [
              {
                "pkgCode": "PKG_TARGET_A",
                "pkgName": "Gói Target A",
                "pkgDesc": null
              }
            ]
          }
        ]
      }
      SQL:
      SELECT * FROM CAT_PKG_GRP
      WHERE GRP_CODE = 'TARGET_CAMP_01'
      AND STATUS = 1;

### Kiểm tra tìm kiếm theo đối tượng khách hàng (cusSubType)
- 1\. Check api trả về:
      1.1. Status: 0
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "total": 2,
        "data": [
          {
            "pkgGroupCode": "SME_PROMO",
            "pkgGroupName": "Ưu đãi doanh nghiệp vừa và nhỏ",
            "typeCode": "SME,MSME",
            "typeName": "Doanh nghiệp SME",
            "pkgList": []
          }
        ]
      }
      SQL:
      SELECT g.*, c.TYPE_NAME
      FROM CAT_PKG_GRP g
      LEFT JOIN CAT_CUSTYPE c ON c.TYPE_CODE = 'SME'
      WHERE g.STATUS = 1
      AND (
          INSTR(g.TYPE_CODE, 'SME') > 0 
          OR INSTR(g.TYPE_CODE, 'CORP') > 0
      );

### Kiểm tra logic sắp xếp dữ liệu trả về (Order By)
- 1\. Check api trả về:
      1.1. Status: 0
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "data": [
          {
            "pkgGroupCode": "A_CAMP",
            "updatedDate": "2024-12-30 10:00:00"
          },
          {
            "pkgGroupCode": "B_CAMP",
            "updatedDate": "2024-12-30 09:00:00"
          }
        ]
      }
      SQL:
      SELECT * FROM CAT_PKG_GRP
      WHERE STATUS = 1
      ORDER BY GRP_CODE ASC, UPDATED_DATE DESC;

### Kiểm tra không hiển thị gói con đã ngừng hoạt động (STATUS=0)
- 1\. Check api trả về:
      1.1. Status: 0
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "data": [
          {
            "pkgGroupCode": "CAMP_FILTER_CHILD",
            "pkgList": [
              {
                "pkgCode": "ACTIVE_PKG",
                "pkgName": "Gói đang hoạt động",
                "status": "1"
              }
            ]
          }
        ]
      }
      SQL:
      SELECT * FROM CAT_PKG
      WHERE GRP_CODE = 'CAMP_FILTER_CHILD'
      AND STATUS = 1;

### Kiểm tra lỗi khi mã chi nhánh không hợp lệ
- 1\. Check api trả về:
      1.1. Status: PRPC_011
      1.2. Response:
      
      {
        "poErrorCode": "PRPC_011",
        "poErrorDesc": "Mã chi nhánh không hợp lệ",
        "total": 0,
        "data": []
      }
      SQL:
      SELECT COUNT(*) FROM CAT_BRANCH 
      WHERE BRANCH_CODE = '9999' 
      AND STATUS = 1;

### Kiểm tra khi không tìm thấy dữ liệu phù hợp
- 1\. Check api trả về:
      1.1. Status: 0
      1.2. Response:
      
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "total": 0,
        "data": []
      }
      SQL:
      SELECT * FROM CAT_PKG_GRP
      WHERE STATUS = 1
      AND GRP_CODE = 'NON_EXISTENT_CODE';

### Kiểm tra xử lý lỗi hệ thống (DB Timeout/Connection Error)
- 1\. Check api trả về:
      1.1. Status: System Error
      1.2. Response:
      
      {
        "poErrorCode": "System Error",
        "poErrorDesc": "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại.",
        "data": null
      }
      SQL:
      -- Simulate DB connection failure or query timeout
      SELECT * FROM CAT_PKG_GRP;


## Kiểm tra khi bị timeout

### Kiểm tra khi lấy dữ liệu DB không thành công do lỗi DB
- 1\. Check api trả về:
  1.1. Status: 500
  1.2. Response:
  {
    "message": "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."
  }
