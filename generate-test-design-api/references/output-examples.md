# Ví dụ đầu ra

## Ví dụ 1: API Test Design — Markdown output

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

