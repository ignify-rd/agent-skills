# API Phê duyệt, từ chối

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

### segConfId : String (Required)

#### Để trống
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Không truyền
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền segConfId là ký tự số
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền segConfId là chữ (thường/hoa) không dấu
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền segConfId là chữ (thường/hoa) có dấu
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền segConfId là ký tự đặc biệt
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền segConfId là all space
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền segConfId có space ở giữa
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền segConfId có space đầu/cuối
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền segConfId là object
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền segConfId là mảng
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền segConfId không tồn tại trong hệ thống hoặc không phải là bản ghi Master (MASTER_ID khác null)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Bản ghi không tồn tại"
      }

#### Truyền segConfId của bản ghi có trạng thái khác "Chờ duyệt sửa" (STATUS != 4)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Trạng thái bản ghi không hợp lệ"
      }

### task : String (Required)

#### Để trống
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Không truyền
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền task là ký tự số
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền task là chữ (thường/hoa) không dấu
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền task là chữ (thường/hoa) có dấu
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền task là ký tự đặc biệt
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền task là all space
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền task có space ở giữa
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền task có space đầu/cuối
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền task là object
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền task là mảng
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền task không nằm trong danh sách cho phép (approve, reject)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Dữ liệu không hợp lệ"
      }

#### Truyền task là approve nhưng có truyền rejectedMessage
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Dữ liệu không hợp lệ"
      }

#### Truyền task là reject nhưng không truyền rejectedMessage
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Dữ liệu không hợp lệ"
      }

### rejectedMessage : String (Optional)

#### Để trống
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Không truyền
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc


#### Truyền rejectedMessage = 224 ký tự hợp lệ
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền rejectedMessage = 225 ký tự hợp lệ
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền rejectedMessage = 226 ký tự hợp lệ
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền rejectedMessage là ký tự số
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền rejectedMessage là chữ (thường/hoa) không dấu
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response: Trả về response body đúng cấu trúc

#### Truyền rejectedMessage là chữ (thường/hoa) có dấu
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền rejectedMessage là ký tự đặc biệt
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền rejectedMessage là all space
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền rejectedMessage có space ở giữa
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền rejectedMessage có space đầu/cuối
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền rejectedMessage là object
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }

#### Truyền rejectedMessage là mảng
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "message": "Dữ liệu không hợp lệ"
      }


#### Truyền task = reject nhưng không truyền rejectedMessage hoặc truyền null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Dữ liệu không hợp lệ"
      }

#### Truyền task = approve nhưng vẫn truyền rejectedMessage (khác null)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Dữ liệu không hợp lệ"
      }

#### Truyền rejectedMessage vượt quá độ dài cho phép theo nghiệp vụ (225 ký tự)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "1",
        "poErrorDesc": "Dữ liệu không hợp lệ"
      }

## Kiểm tra luồng chính

### Kiểm tra quyền phê duyệt hợp lệ
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "data": {
          "segConfId": "1001"
        }
      }
      SQL:
      SELECT COUNT(*) FROM SYS_USER_RIGHT
      WHERE USER_NAME = 'admin' 
      AND MENU_CODE = 'FEE_AUTO_POLICY' 
      AND FUNC_CODE = 'approve';

### Kiểm tra quyền phê duyệt không hợp lệ
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "poErrorCode": null,
        "poErrorDesc": "Phân quyền người dùng không hợp lệ",
        "data": null
      }
      SQL:
      SELECT COUNT(*) FROM SYS_USER_RIGHT
      WHERE USER_NAME = 'user_no_access' 
      AND MENU_CODE = 'FEE_AUTO_POLICY' 
      AND FUNC_CODE = 'approve';

### Kiểm tra bản ghi không tồn tại hoặc sai điều kiện master
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "poErrorCode": null,
        "poErrorDesc": "Bản ghi không tồn tại",
        "data": null
      }
      SQL:
      SELECT * FROM SEGMENT_FEE_CONFIG
      WHERE SEG_CONF_ID = 99999 
      OR (SEG_CONF_ID = 1001 AND MASTER_ID IS NOT NULL);

### Kiểm tra trạng thái bản ghi không hợp lệ (Status != 4)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "poErrorCode": null,
        "poErrorDesc": "Trạng thái bản ghi không hợp lệ",
        "data": null
      }
      SQL:
      SELECT STATUS FROM SEGMENT_FEE_CONFIG
      WHERE SEG_CONF_ID = 1002;
      -- Expect STATUS != 4 (e.g., 1 or 2)

### Kiểm tra phê duyệt thành công (Update DB)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "data": {
          "segConfId": "1001"
        }
      }
      SQL:
      SELECT STATUS, APPROVED_USER, APPROVED_TIME 
      FROM SEGMENT_FEE_CONFIG 
      WHERE SEG_CONF_ID = 1001;
      -- Expect STATUS = '1'

### Kiểm tra phê duyệt thành công (Ghi log ACTION_LOG)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "data": {
          "segConfId": "1001"
        }
      }
      SQL:
      SELECT * FROM ACTION_LOG
      WHERE TABLE_NAME = 'SEGMENT_FEE_CONFIG'
      AND MASTER_ID = '1001'
      AND STATUS = '1'
      ORDER BY CREATED_TIME DESC;

### Kiểm tra phê duyệt thành công (Xóa HIS)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "data": {
          "segConfId": "1001"
        }
      }
      SQL:
      SELECT COUNT(*) FROM SEGMENT_FEE_CONFIG_HIS
      WHERE SEG_CONF_ID = 1001 
      OR MASTER_ID = 1001;
      -- Expect count = 0

### Kiểm tra từ chối thành công (Rollback từ HIS)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "data": {
          "segConfId": "1003"
        }
      }
      SQL:
      SELECT REJECTED_MESSAGE, STATUS 
      FROM SEGMENT_FEE_CONFIG
      WHERE SEG_CONF_ID = 1003;
      -- Expect REJECTED_MESSAGE = input message, STATUS restored from HIS

### Kiểm tra từ chối thành công (Ghi log ACTION_LOG)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "data": {
          "segConfId": "1003"
        }
      }
      SQL:
      SELECT * FROM ACTION_LOG
      WHERE TABLE_NAME = 'SEGMENT_FEE_CONFIG'
      AND MASTER_ID = '1003'
      AND STATUS IN ('1', '2') -- Depends on HIS status
      ORDER BY CREATED_TIME DESC;

### Kiểm tra lỗi hệ thống (DB Error)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "poErrorCode": null,
        "poErrorDesc": "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại.",
        "data": null
      }
      SQL:
      -- Simulate DB connection loss or query timeout


## Kiểm tra khi bị timeout

### Kiểm tra khi lấy dữ liệu DB không thành công do lỗi DB
- 1. Check api trả về:
  1.1. Status: 500
  1.2. Response:
  {
    "message": "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."
  }