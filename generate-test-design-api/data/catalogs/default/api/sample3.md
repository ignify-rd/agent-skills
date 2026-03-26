# API lấy Chi tiết giá tự động

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
- status: N/A

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


Based on the provided RSD (Page 9) and PTTK (Page 30), here are the specific business validation rules for `segConfId` in the `get-detail` API:

#### Truyền segConfId không tồn tại trong hệ thống
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "SFCD1",
        "poErrorDesc": "Bản ghi không tồn tại"
      }

#### Truyền segConfId thuộc bản ghi Segment (bản ghi con có MASTER_ID khác null)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
  
      {
        "poErrorCode": "SFCD1",
        "poErrorDesc": "Bản ghi không tồn tại"
      }

## Kiểm tra luồng chính

### Kiểm tra lấy chi tiết thành công (Domain Type 1 - Dịch vụ)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "total": 1,
        "data": {
          "segConfId": 1001,
          "domainType": 1,
          "domainTypeName": "Dịch vụ thu phí",
          "feeService": "SRV_SMS",
          "feeServiceName": "Phí dịch vụ SMS",
          "maxFeeVnd": 50000,
          "status": 1,
          "statusName": "Hoạt động",
          "rejectedMessage": null,
          "updatedUser": "user1",
          "updatedTime": "2024-01-01",
          "approvedUser": "admin",
          "approvedTime": "2024-01-02",
          "listSegment": [
            {
              "segConfId": 2001,
              "feeCodeId": "10",
              "feeCode": "FEE_SMS_01",
              "segmentName": "Khách hàng VIP",
              "masterId": 1001,
              "priceType": 0,
              "priceTypeName": "Cố định",
              "priceVnd": 10000,
              "priceUsd": null,
              "status": 1,
              "statusName": "Hoạt động",
              "updatedUser": "user1",
              "updatedTime": "2024-01-01",
              "approvedUser": "admin",
              "approvedTime": "2024-01-02"
            }
          ]
        }
      }
      SQL:
      SELECT m.SEG_CONF_ID, m.DOMAIN_TYPE, d.PAR_NAME as DOMAIN_TYPE_NAME,
             m.FEE_SERVICE, s.SRV_NAME as FEE_SERVICE_NAME,
             st.STATE_NAME as STATUS_NAME,
             seg.SEGMENT_NAME, c.FEE_CODE
      FROM SEGMENT_FEE_CONFIG m
      LEFT JOIN PAR_COMMON d ON m.DOMAIN_TYPE = d.PAR_CODE AND d.PAR_TYPE = 'DOMAIN_TYPE'
      LEFT JOIN CAT_FEESERVICE s ON m.FEE_SERVICE = s.SRV_CODE
      LEFT JOIN SYS_STATE_CODE st ON m.STATUS = st.STATE_CODE AND st.STATE_TYPE = 'SEGMENT_FEE_MASTER'
      LEFT JOIN SEGMENT_FEE_CONFIG seg ON m.SEG_CONF_ID = seg.MASTER_ID
      LEFT JOIN CAT_FEECODE c ON seg.FEE_CODE_ID = c.ID
      WHERE m.SEG_CONF_ID = 1001 AND m.MASTER_ID IS NULL AND m.DOMAIN_TYPE = 1;

### Kiểm tra lấy chi tiết thành công (Domain Type 2 - Gói SPDV)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "total": 1,
        "data": {
          "segConfId": 1002,
          "domainType": 2,
          "domainTypeName": "Gói SPDV",
          "feeService": "GRP_COMBO",
          "feeServiceName": "Gói Combo Tài khoản",
          "maxFeeVnd": null,
          "status": 1,
          "statusName": "Hoạt động",
          "listSegment": [
            {
              "segConfId": 2002,
              "feeCodeId": "CODE_DIRECT",
              "feeCode": "CODE_DIRECT",
              "segmentName": "Gói Chuẩn",
              "masterId": 1002,
              "priceType": 2,
              "priceTypeName": "Đơn giá sản lượng",
              "priceVnd": 5000,
              "priceUsd": null
            }
          ]
        }
      }
      SQL:
      SELECT m.SEG_CONF_ID, m.DOMAIN_TYPE,
             m.FEE_SERVICE, g.GRP_NAME as FEE_SERVICE_NAME,
             seg.FEE_CODE_ID as FEE_CODE
      FROM SEGMENT_FEE_CONFIG m
      LEFT JOIN CAT_PKG_GRP g ON m.FEE_SERVICE = g.GRP_CODE
      LEFT JOIN SEGMENT_FEE_CONFIG seg ON m.SEG_CONF_ID = seg.MASTER_ID
      WHERE m.SEG_CONF_ID = 1002 AND m.MASTER_ID IS NULL AND m.DOMAIN_TYPE = 2;

### Kiểm tra logic sắp xếp listSegment
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "poErrorDesc": "Thành công",
        "data": {
          "segConfId": 1001,
          "listSegment": [
            {
              "segConfId": 2001,
              "segmentName": "Segment A"
            },
            {
              "segConfId": 2002,
              "segmentName": "Segment B"
            }
          ]
        }
      }
      SQL:
      SELECT * FROM SEGMENT_FEE_CONFIG
      WHERE MASTER_ID = 1001
      ORDER BY SEG_CONF_ID ASC;

### Kiểm tra lookup statusName từ SYS_STATE_CODE
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "data": {
          "segConfId": 1001,
          "status": 4,
          "statusName": "Chờ duyệt sửa"
        }
      }
      SQL:
      SELECT m.STATUS, s.STATE_NAME
      FROM SEGMENT_FEE_CONFIG m
      JOIN SYS_STATE_CODE s ON m.STATUS = s.STATE_CODE
      WHERE m.SEG_CONF_ID = 1001
      AND s.STATE_TYPE = 'SEGMENT_FEE_MASTER';

### Kiểm tra lookup priceTypeName từ PAR_COMMON
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      {
        "poErrorCode": "0",
        "data": {
          "listSegment": [
            {
              "priceType": 2,
              "priceTypeName": "Đơn giá sản lượng"
            }
          ]
        }
      }
      SQL:
      SELECT s.PRICE_TYPE, p.PAR_NAME
      FROM SEGMENT_FEE_CONFIG s
      JOIN PAR_COMMON p ON s.PRICE_TYPE = p.PAR_CODE
      WHERE s.MASTER_ID = 1001
      AND p.PAR_TYPE = 'PRICE_TYPE';

### Kiểm tra không tồn tại bản ghi (Mã không có trong DB)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "poErrorCode": "N/A",
        "poErrorDesc": "Bản ghi không tồn tại",
        "total": 0,
        "data": null
      }
      SQL:
      SELECT * FROM SEGMENT_FEE_CONFIG
      WHERE SEG_CONF_ID = 999999;

### Kiểm tra không tồn tại bản ghi (Mã có nhưng không phải Master)
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "poErrorCode": "N/A",
        "poErrorDesc": "Bản ghi không tồn tại",
        "total": 0,
        "data": null
      }
      SQL:
      SELECT * FROM SEGMENT_FEE_CONFIG
      WHERE SEG_CONF_ID = 2001 AND MASTER_ID IS NOT NULL;

### Kiểm tra phân quyền user không hợp lệ
- 1. Check api trả về:
      1.1. Status: 200
      1.2. Response:
      
      {
        "poErrorCode": "N/A",
        "poErrorDesc": "Phân quyền người dùng không hợp lệ"
      }

### Kiểm tra lỗi DB (Timeout/Connection)
- 1. Check api trả về:
      1.1. Status: 500
      1.2. Response:
      
      {
        "poErrorCode": "N/A",
        "poErrorDesc": "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại"
      }


## Kiểm tra khi bị timeout

### Kiểm tra khi lấy dữ liệu DB không thành công do lỗi DB
- 1. Check api trả về:
  1.1. Status: 500
  1.2. Response:
  {
    "message": "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."
  }