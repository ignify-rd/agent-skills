# API Đăng ký gói SPDV tại FEE ENGINE

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

### requestId : String (Required)

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


#### Truyền requestId = 299 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền requestId = 300 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền requestId = 301 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền requestId là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền requestId là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền requestId là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền requestId là ký tự đặc biệt
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền requestId là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền requestId có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền requestId có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền requestId là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền requestId là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền requestId trùng với giao dịch đang được xử lý (Idempotency Check)
- 1\. Check api trả về:
  1.1. Status: 409
  1.2. Response:
  
      {
        "message": "Request đang được xử lý"
      }

#### Truyền requestId đã tồn tại trong lịch sử giao dịch (Duplicate Check)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Mã requestId đã tồn tại",
        "data": null
      }

#### Truyền regChannel không tồn tại trong bảng tham số kênh (PAR_COMMON)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Mã kênh đăng ký không hợp lệ",
        "data": null
      }

#### Truyền createdUser không tồn tại trong hệ thống quản lý cán bộ
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Mã cán bộ khởi tạo không tồn tại",
        "data": null
      }

#### Truyền approvedUser chứa mã cán bộ không tồn tại hoặc sai định dạng danh sách
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Danh sách cán bộ phê duyệt không hợp lệ",
        "data": null
      }

### cifNo : String (Required)

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


#### Truyền cifNo là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền cifNo là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền cifNo là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifNo là ký tự đặc biệt
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifNo là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifNo có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifNo có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifNo là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifNo là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền cifNo đã đăng ký gói dịch vụ này và đang hiệu lực (Active)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "failedList": [
      {
        "errorCode": "PRPC_005",
        "errorDesc": "Khách hàng đã đăng ký gói này"
      }
    ]
  }

#### Truyền cifNo đã đăng ký gói khác thuộc cùng nhóm chiến dịch (pkgGroupCode) và đang hiệu lực
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "failedList": [
      {
        "errorCode": "PRPC_006",
        "errorDesc": "Khách hàng đang sử dụng gói khác trong cùng nhóm gói"
      }
    ]
  }

#### Truyền cifNo không phải là chủ sở hữu chính (Primary Owner) của tài khoản thu phí (feeAcctNo)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "failedList": [
      {
        "errorCode": "PRPC_009",
        "errorDesc": "CIF đang đăng ký không phải CIF chính của tài khoản thanh toán."
      }
    ]
  }

#### Truyền regChannel nằm ngoài khoảng giá trị cho phép (lớn hơn 10)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Tham số đầu vào không hợp lệ",
    "failedList": [
       {
         "errorCode": "PRPC_001",
         "errorDesc": "Dữ liệu không hợp lệ"
       }
    ]
  }

#### Truyền approvedUser chứa danh sách nhiều cán bộ nhưng không phân cách bằng dấu phẩy
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Tham số đầu vào không hợp lệ",
    "failedList": [
       {
         "errorCode": "PRPC_001",
         "errorDesc": "Dữ liệu không hợp lệ"
       }
    ]
  }

### cifName : String (Required)

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


#### Truyền cifName = 149 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền cifName = 150 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền cifName = 151 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifName là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền cifName là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền cifName là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifName là ký tự đặc biệt
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifName là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifName có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifName có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifName là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền cifName là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


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

#### Truyền regBranch là ký tự đặc biệt
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


#### Truyền regBranch không tồn tại trong danh mục hoặc không phải cấp chi nhánh (Type != 0)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "totalFailed": 1,
      "failedList": [
        {
          "errorCode": "PRPC_004",
          "errorDesc": "Địa bàn/Chi nhánh không hợp lệ."
        }
      ]
    }
  }

#### Truyền regBranch không thuộc phạm vi áp dụng Địa bàn (Scope = 2) của gói dịch vụ
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "totalFailed": 1,
      "failedList": [
        {
          "errorCode": "PRPC_004",
          "errorDesc": "Địa bàn/Chi nhánh không hợp lệ."
        }
      ]
    }
  }

#### Truyền regBranch không thuộc phạm vi áp dụng Chi nhánh (Scope = 3) của gói dịch vụ
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "totalFailed": 1,
      "failedList": [
        {
          "errorCode": "PRPC_004",
          "errorDesc": "Địa bàn/Chi nhánh không hợp lệ."
        }
      ]
    }
  }

#### Truyền regChannel không tồn tại trong danh mục kênh (PAR_COMMON với type = 'CHANNEL')
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "PRPC_001",
        "poErrorDesc": "Tham số đầu vào không hợp lệ"
      }

### regChannel : number (Required)

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

#### Truyền regChannel là số âm
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel là số thập phân (VD: 1.5)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel là số có leading zero (VD: 00123)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel là số rất lớn vượt giới hạn number
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel là chuỗi ký tự (VD: "abc")
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel là chuỗi chữ lẫn số (VD: "10abc000")
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel là ký tự đặc biệt (VD: @#$%, *, -, +)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel có space đầu/cuối (VD: " 123 ", "123 ")
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel là boolean (true/false)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền regChannel là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền regChannel vượt quá độ dài cho phép (lớn hơn 10 ký tự số)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "PRPC_001",
        "poErrorDesc": "Tham số đầu vào không hợp lệ"
      }

#### Truyền regChannel không tồn tại trong hệ thống (zChannelId không tìm thấy trong bảng tham số kênh PAR_COMMON)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "PRPC_001",
        "poErrorDesc": "Tham số đầu vào không hợp lệ"
      }

### createdUser : String (Required)

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


#### Truyền createdUser = 29 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền createdUser = 30 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền createdUser = 31 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền createdUser là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền createdUser là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền createdUser là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền createdUser là ký tự đặc biệt
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền createdUser là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền createdUser có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền createdUser có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền createdUser là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền createdUser là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền createdUser trùng với approvedUser hoặc nằm trong danh sách approvedUser
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Người tạo và người duyệt không được trùng nhau"
      }

#### Truyền createdUser không tồn tại trong hệ thống hoặc đã nghỉ việc
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Mã cán bộ khởi tạo không tồn tại hoặc không hoạt động"
      }

#### Truyền createdUser không phải là cán bộ thuộc nhóm GDV (Sai vai trò nghiệp vụ)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Mã cán bộ không có quyền khởi tạo đăng ký (Không phải GDV)"
      }

#### Truyền createdUser không thuộc chi nhánh đăng ký (regBranch)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Cán bộ khởi tạo không thuộc chi nhánh đăng ký"
      }

### pkgList : Array (Required) (gồm các trường: pkgCode, pkgGroupCode, feeAcctNo)

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

#### Truyền pkgList là mảng rỗng []
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList chứa phần tử rỗng (VD: [{}])
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList là string thay vì array
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList là number thay vì array
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList là object thay vì array
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList là boolean thay vì array
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền regChannel không tồn tại trong danh mục kênh (PAR_COMMON)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Tham số đầu vào không hợp lệ",
        "data": null
      }

#### Truyền pkgList chứa gói dịch vụ không tồn tại trong hệ thống hoặc Status != 1 (Active)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký thất bại",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_TEST_01",
          "errorCode": "PRPC_002",
          "errorDesc": "Gói dịch vụ không tồn tại."
        }
      ]
    }
  }

#### Truyền pkgList chứa gói dịch vụ không nằm trong thời gian bán (Sale Date)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký thất bại",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_TEST_01",
          "errorCode": "PRPC_003",
          "errorDesc": "Hiện tại đang không trong thời gian bán gói sản phẩm."
        }
      ]
    }
  }

#### Truyền pkgList chứa gói dịch vụ có phạm vi áp dụng (Scope) không bao gồm chi nhánh đăng ký (regBranch)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký thất bại",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_TEST_01",
          "errorCode": "PRPC_004",
          "errorDesc": "Địa bàn/Chi nhánh không hợp lệ."
        }
      ]
    }
  }

#### Truyền pkgList chứa gói dịch vụ mà khách hàng đã đăng ký và đang hoạt động (Trùng gói)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký thất bại",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_TEST_01",
          "errorCode": "PRPC_005",
          "errorDesc": "Khách hàng đã đăng ký gói dịch vụ."
        }
      ]
    }
  }

#### Truyền pkgList chứa gói dịch vụ thuộc nhóm chiến dịch mà khách hàng đã đăng ký gói khác (Trùng nhóm)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký thất bại",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_TEST_01",
          "errorCode": "PRPC_006",
          "errorDesc": "Khách hàng đã đăng ký chiến dịch này với gói khác, vui lòng dùng chức năng chỉnh sửa"
        }
      ]
    }
  }

#### Truyền pkgList chứa tài khoản thu phí (feeAcctNo) có trạng thái không cho phép trích nợ (không nằm trong SYS_CONFIG)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký thất bại",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_TEST_01",
          "errorCode": "PRPC_007",
          "errorDesc": "Số tài khoản thu phí có trạng thái không hợp lệ."
        }
      ]
    }
  }

#### Truyền pkgList chứa tài khoản thu phí (feeAcctNo) thuộc danh sách sản phẩm cấm thu phí (CAT_PROD_NOTALLOW)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký thất bại",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_TEST_01",
          "errorCode": "PRPC_008",
          "errorDesc": "Số tài khoản thu phí có mã sản phẩm thuộc danh mục không được thu phí."
        }
      ]
    }
  }

#### Truyền pkgList chứa tài khoản thu phí (feeAcctNo) mà CIF đăng ký không phải là chủ sở hữu chính (Quan hệ != 1)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký thất bại",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_TEST_01",
          "errorCode": "PRPC_009",
          "errorDesc": "CIF đang đăng ký không phải CIF chính của tài khoản thanh toán."
        }
      ]
    }
  }

#### Truyền pkgList chứa tài khoản thu phí (feeAcctNo) có loại tiền tệ khác VND
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký thất bại",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_TEST_01",
          "errorDesc": "Loại tiền tài khoản không hợp lệ ."
        }
      ]
    }
  }

### pkgList[].pkgCode : String (Required)

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


#### Truyền pkgList[].pkgCode = 49 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgList[].pkgCode = 50 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgList[].pkgCode = 51 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgCode là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgList[].pkgCode là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgList[].pkgCode là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgCode là ký tự đặc biệt
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgCode là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgCode có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgCode có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgCode là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgCode là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền pkgList[].pkgCode không tồn tại trong hệ thống hoặc trạng thái ngưng hoạt động
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_NON_EXIST",
          "errorCode": "PRPC_002",
          "errorDesc": "Gói dịch vụ không tồn tại"
        }
      ]
    }
  }

#### Truyền pkgList[].pkgCode nằm ngoài thời gian mở bán (SALE_START_DATE - SALE_END_DATE)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_EXPIRED",
          "errorCode": "PRPC_003",
          "errorDesc": "Hiện tại đang không trong thời gian bán gói sản phẩm"
        }
      ]
    }
  }

#### Truyền pkgList[].pkgCode không phù hợp với phạm vi áp dụng (Địa bàn/Chi nhánh) của gói (Scope Check)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_SCOPE_INVALID",
          "errorCode": "PRPC_004",
          "errorDesc": "Địa bàn/Chi nhánh không hợp lệ"
        }
      ]
    }
  }

#### Truyền pkgList[].pkgCode mà khách hàng (CIF) đã đăng ký và đang hoạt động (Trùng gói)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_DUPLICATE",
          "errorCode": "PRPC_005",
          "errorDesc": "Khách hàng đã đăng ký gói dịch vụ"
        }
      ]
    }
  }

#### Truyền pkgList[].pkgCode thuộc nhóm chiến dịch (pkgGroupCode) mà khách hàng đang sử dụng một gói khác (Trùng nhóm chiến dịch)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "failedList": [
        {
          "pkgCode": "PKG_GROUP_CONFLICT",
          "errorCode": "PRPC_006",
          "errorDesc": "Khách hàng đã đăng ký chiến dịch này với gói khác, vui lòng dùng chức năng chỉnh sửa"
        }
      ]
    }
  }

#### Truyền regChannel vượt quá độ dài cho phép (10 chữ số)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "PRPC_001",
        "poErrorDesc": "Tham số đầu vào không hợp lệ",
        "data": null
      }

#### Truyền createdUser vượt quá độ dài cho phép (30 ký tự)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "PRPC_001",
        "poErrorDesc": "Tham số đầu vào không hợp lệ",
        "data": null
      }

#### Truyền approvedUser sai định dạng danh sách (Không ngăn cách bởi dấu phẩy hoặc chứa ký tự không hợp lệ)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "PRPC_001",
        "poErrorDesc": "Tham số đầu vào không hợp lệ",
        "data": null
      }

### pkgList[].pkgGroupCode : String (Required)

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


#### Truyền pkgList[].pkgGroupCode = 49 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgList[].pkgGroupCode = 50 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgList[].pkgGroupCode = 51 ký tự hợp lệ
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgGroupCode là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgList[].pkgGroupCode là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgList[].pkgGroupCode là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgGroupCode là ký tự đặc biệt
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgGroupCode là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgGroupCode có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgGroupCode có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgGroupCode là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].pkgGroupCode là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền pkgList[].pkgGroupCode không tồn tại trong hệ thống hoặc trạng thái (STATUS) không hoạt động (Active = 1)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "failedList": [
        {
          "errorCode": "PRPC_002",
          "errorDesc": "Gói hoặc Nhóm gói không tồn tại"
        }
      ]
    }
  }

#### Truyền pkgList[].pkgGroupCode không khớp với pkgList[].pkgCode (Gói con không thuộc Gói cha quy định trong CAT_PKG)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "failedList": [
        {
          "errorCode": "PRPC_002",
          "errorDesc": "Gói hoặc Nhóm gói không tồn tại"
        }
      ]
    }
  }

#### Truyền pkgList[].pkgGroupCode nằm ngoài khoảng thời gian bán cho phép (Ngày hiện tại không thuộc SALE_START_DATE - SALE_END_DATE)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "failedList": [
        {
          "errorCode": "PRPC_003",
          "errorDesc": "Ngoài thời gian bán sản phẩm"
        }
      ]
    }
  }

#### Truyền pkgList[].pkgGroupCode có cấu hình phạm vi áp dụng (Scope) không bao gồm Chi nhánh/Địa bàn đăng ký (regBranch)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "failedList": [
        {
          "errorCode": "PRPC_004",
          "errorDesc": "Ngoài phạm vi triển khai"
        }
      ]
    }
  }

#### Truyền pkgList[].pkgGroupCode mà khách hàng (CIF) đang có gói khác thuộc nhóm này đang hoạt động (Active)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "failedList": [
        {
          "errorCode": "PRPC_006",
          "errorDesc": "Khách hàng đang sử dụng gói khác"
        }
      ]
    }
  }

### pkgList[].feeAcctNo : String (Required)

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


#### Truyền pkgList[].feeAcctNo là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgList[].feeAcctNo là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền pkgList[].feeAcctNo là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].feeAcctNo là ký tự đặc biệt
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].feeAcctNo là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].feeAcctNo có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].feeAcctNo có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].feeAcctNo là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền pkgList[].feeAcctNo là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền pkgList[].feeAcctNo có loại tiền tệ không phải VND
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "total": 1,
      "totalSuccess": 0,
      "totalFailed": 1,
      "failedList": [
        {
          "pkgCode": "MÃ_GÓI_TEST",
          "errorCode": "PRPC_xxx",
          "errorDesc": "Loại tiền tài khoản không hợp lệ ."
        }
      ]
    }
  }

#### Truyền pkgList[].feeAcctNo có trạng thái không được phép trích nợ (không nằm trong cấu hình dda.status.allow.debit)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "total": 1,
      "totalSuccess": 0,
      "totalFailed": 1,
      "failedList": [
        {
          "pkgCode": "MÃ_GÓI_TEST",
          "errorCode": "PRPC_007",
          "errorDesc": "Số tài khoản thu phí có trạng thái không hợp lệ."
        }
      ]
    }
  }

#### Truyền pkgList[].feeAcctNo có mã sản phẩm thuộc danh sách không được phép thu phí (tồn tại trong CAT_PROD_NOTALLOW)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "total": 1,
      "totalSuccess": 0,
      "totalFailed": 1,
      "failedList": [
        {
          "pkgCode": "MÃ_GÓI_TEST",
          "errorCode": "PRPC_008",
          "errorDesc": "Số tài khoản thu phí có mã sản phẩm thuộc danh mục không được thu phí."
        }
      ]
    }
  }

#### Truyền pkgList[].feeAcctNo mà CIF đăng ký không phải là chủ sở hữu chính (AccRelation != 1)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  {
    "poErrorCode": "1",
    "poErrorDesc": "Có gói đăng ký không hợp lệ",
    "data": {
      "total": 1,
      "totalSuccess": 0,
      "totalFailed": 1,
      "failedList": [
        {
          "pkgCode": "MÃ_GÓI_TEST",
          "errorCode": "PRPC_009",
          "errorDesc": "CIF đang đăng ký không phải CIF chính của tài khoản thanh toán."
        }
      ]
    }
  }

#### Truyền regChannel không hợp lệ hoặc không tồn tại trong danh mục kênh (PAR_COMMON)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Tham số đầu vào không hợp lệ",
        "data": null
      }

### approvedUser : String (Required)

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


#### Truyền approvedUser là ký tự số
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền approvedUser là chữ (thường/hoa) không dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền approvedUser là chữ (thường/hoa) có dấu
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền approvedUser là ký tự đặc biệt
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền approvedUser là all space
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền approvedUser có space ở giữa
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền approvedUser có space đầu/cuối
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền approvedUser là object
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền approvedUser là mảng
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền regChannel không tồn tại trong bảng tham số kênh (PAR_COMMON)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "PRPC_001",
        "poErrorDesc": "Tham số đầu vào không hợp lệ"
      }

#### Truyền approvedUser sai định dạng (sử dụng ký tự phân cách khác dấu phẩy trong trường hợp duyệt nhiều cấp)
- 1\. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "PRPC_001",
        "poErrorDesc": "Tham số đầu vào không hợp lệ"
      }

## Kiểm tra luồng chính

### Kiểm tra đăng ký thành công (Happy Path)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 1,
          "totalFailed": 0,
          "failedList": []
        }
      }
      SQL:
      SELECT * FROM SRV_PKG_CUSTOMER
      WHERE CIF_NO = '12345678'
      AND PKG_CODE = 'PKG001'
      AND REG_CHANNEL = 'CHANNEL01'
      AND STATUS = '1';

### Kiểm tra tính toán ngày hiệu lực phí (Start Charge Period)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 1,
          "totalFailed": 0,
          "failedList": []
        }
      }
      SQL:
      SELECT START_CHARGE_PERIOD, END_CHARGE_PERIOD 
      FROM SRV_PKG_CUSTOMER
      WHERE CIF_NO = '12345678' AND STATUS = '1';
      -- Logic verify: START_CHARGE_PERIOD phải bằng tháng kế tiếp nếu đăng ký tháng hiện tại

### Kiểm tra gói dịch vụ không tồn tại
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 0,
          "totalFailed": 1,
          "failedList": [
            {
              "pkgCode": "PKG_INVALID",
              "errorCode": "PRPC_002",
              "errorDesc": "Gói dịch vụ không tồn tại"
            }
          ]
        }
      }
      SQL:
      SELECT COUNT(*) FROM CAT_PKG 
      WHERE PKG_CODE = 'PKG_INVALID' 
      AND STATUS = 1;

### Kiểm tra gói không trong thời gian bán
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 0,
          "totalFailed": 1,
          "failedList": [
            {
              "pkgCode": "PKG001",
              "errorCode": "PRPC_003",
              "errorDesc": "Hiện tại đang không trong thời gian bán gói sản phẩm"
            }
          ]
        }
      }
      SQL:
      SELECT * FROM CAT_PKG_GRP 
      WHERE PKG_GROUP_CODE = 'GRP001'
      AND (SALE_START_DATE > SYSDATE OR SALE_END_DATE < SYSDATE);

### Kiểm tra địa bàn không hợp lệ (Scope Tỉnh/Thành phố)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 0,
          "totalFailed": 1,
          "failedList": [
            {
              "pkgCode": "PKG001",
              "errorCode": "PRPC_004",
              "errorDesc": "Địa bàn/Chi nhánh không hợp lệ"
            }
          ]
        }
      }
      SQL:
      SELECT b.PROVINCE_CODE 
      FROM CATEGORY_BRANCH b
      JOIN CAT_PKG_GRP g ON g.APPLY_SCOPE_TYPE = 2
      WHERE b.BRCD = '123'
      AND b.PROVINCE_CODE NOT IN (SELECT REGEXP_SUBSTR(g.APPLY_UNIT_CODES, '[^,]+', 1, LEVEL) FROM DUAL CONNECT BY REGEXP_SUBSTR(g.APPLY_UNIT_CODES, '[^,]+', 1, LEVEL) IS NOT NULL);

### Kiểm tra chi nhánh không hợp lệ (Scope Chi nhánh cụ thể)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 0,
          "totalFailed": 1,
          "failedList": [
            {
              "pkgCode": "PKG001",
              "errorCode": "PRPC_004",
              "errorDesc": "Địa bàn/Chi nhánh không hợp lệ"
            }
          ]
        }
      }
      SQL:
      SELECT * FROM CAT_PKG_GRP 
      WHERE APPLY_SCOPE_TYPE = 3 
      AND INSTR(',' || APPLY_UNIT_CODES || ',', ',' || '123' || ',') = 0;

### Kiểm tra khách hàng đã đăng ký chính gói này
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 0,
          "totalFailed": 1,
          "failedList": [
            {
              "pkgCode": "PKG001",
              "errorCode": "PRPC_005",
              "errorDesc": "Khách hàng đã đăng ký gói dịch vụ"
            }
          ]
        }
      }
      SQL:
      SELECT * FROM SRV_PKG_CUSTOMER
      WHERE CIF_NO = '12345678'
      AND PKG_CODE = 'PKG001'
      AND STATUS = '1';

### Kiểm tra khách hàng đăng ký gói khác trong cùng chiến dịch
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 0,
          "totalFailed": 1,
          "failedList": [
            {
              "pkgCode": "PKG002",
              "errorCode": "PRPC_006",
              "errorDesc": "Khách hàng đã đăng ký chiến dịch này với gói khác"
            }
          ]
        }
      }
      SQL:
      SELECT * FROM SRV_PKG_CUSTOMER
      WHERE CIF_NO = '12345678'
      AND PKG_GROUP_CODE = 'GRP001'
      AND PKG_CODE != 'PKG002'
      AND STATUS = '1';

### Kiểm tra trạng thái tài khoản không hợp lệ (Cấu hình)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 0,
          "totalFailed": 1,
          "failedList": [
            {
              "pkgCode": "PKG001",
              "errorCode": "PRPC_007",
              "errorDesc": "Số tài khoản thu phí có trạng thái không hợp lệ"
            }
          ]
        }
      }
      SQL:
      SELECT CONFIG_VALUE FROM SYS_CONFIG 
      WHERE CONFIG_CODE = 'dda.status.allow.debit';

### Kiểm tra tài khoản thuộc danh mục sản phẩm không thu phí
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 0,
          "totalFailed": 1,
          "failedList": [
            {
              "pkgCode": "PKG001",
              "errorCode": "PRPC_008",
              "errorDesc": "Số tài khoản thu phí có mã sản phẩm thuộc danh mục không được thu phí"
            }
          ]
        }
      }
      SQL:
      SELECT * FROM CAT_PROD_NOTALLOW 
      WHERE PROD_SRC = 'CODE_FROM_SOA' 
      AND STATUS = 1 
      AND IS_DELETED = 0;

### Kiểm tra CIF không phải chủ sở hữu chính của tài khoản
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thực hiện thành công",
        "data": {
          "total": 1,
          "totalSuccess": 0,
          "totalFailed": 1,
          "failedList": [
            {
              "pkgCode": "PKG001",
              "errorCode": "PRPC_009",
              "errorDesc": "CIF đang đăng ký không phải CIF chính của tài khoản thanh toán"
            }
          ]
        }
      }

### Kiểm tra lỗi hệ thống nội bộ (DB Error)
- 1\. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "poErrorCode": "Internal Error",
        "poErrorDesc": "Lỗi hệ thống nội bộ FEE ENGINE",
        "data": null
      }


## Kiểm tra khi bị timeout

### Kiểm tra khi lấy dữ liệu DB không thành công do lỗi DB
- 1\. Check api trả về:
  1.1. Status: 500
  1.2. Response:
  {
    "message": "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."
  }
