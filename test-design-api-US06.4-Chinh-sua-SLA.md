# API Chỉnh sửa SLA

## Kiểm tra các case common

### Method

#### Kiểm tra truyền sai method (GET)
- status: 405
- {
  "code": "405",
  "message": "Method Not Allowed"
  }

#### Kiểm tra truyền sai method (PUT)
- status: 405
- {
  "code": "405",
  "message": "Method Not Allowed"
  }

#### Kiểm tra truyền sai method (DELETE)
- status: 405
- {
  "code": "405",
  "message": "Method Not Allowed"
  }

### URL

#### Kiểm tra truyền sai url
- status: 404
- {
  "code": "404",
  "message": "Not Found"
  }

#### Kiểm tra truyền url đúng nhưng body rỗng
- status: 200
- {
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ"
  }

### Kiểm tra phân quyền

#### Không có quyền (không truyền Authorization)
- status: 401
- {
  "code": "401",
  "message": "Unauthorized"
  }

#### Token không hợp lệ
- status: 401
- {
  "code": "401",
  "message": "Unauthorized"
  }

#### Được phân quyền (token hợp lệ, đầy đủ trường bắt buộc)
- status: 200

### X-Request-Id

#### Không truyền X-Request-Id
- status: 400
- {
  "code": "400",
  "message": "Bad Request"
  }

## Kiểm tra validate

### slaVersionId: Long (Required)

#### Để trống slaVersionId
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Thiếu trường id phiên bản SLA",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền slaVersionId
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Thiếu trường id phiên bản SLA",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = 0
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "2",
  "message": "Không tìm thấy thông tin SLA",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = -1
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "2",
  "message": "Không tìm thấy thông tin SLA",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = số rất lớn (999999999999)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "2",
  "message": "Không tìm thấy thông tin SLA",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = chuỗi ký tự ("abc")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = chuỗi ký tự số ("100")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaVersionId = số thập phân (10.5)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Thiếu trường id phiên bản SLA",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = boolean (true)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = mảng rỗng ([])
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = object ({})
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = XSS script
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = SQL INJECTION
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaVersionId = số nguyên dương hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

### currentStatus: Integer (Required, enum: 0=Dự thảo, 1=Chờ duyệt, 2=APPROVED, 3=Từ chối)

#### Để trống currentStatus
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Thiếu trường trạng thái hiện tại",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền currentStatus
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Thiếu trường trạng thái hiện tại",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền currentStatus = 0 (Dự thảo)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền currentStatus = 1 (Chờ duyệt)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền currentStatus = 2 (APPROVED)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "3",
  "message": "Trạng thái SLA không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền currentStatus = 3 (Từ chối)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "3",
  "message": "Trạng thái SLA không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền currentStatus = 4 (vượt enum)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "3",
  "message": "Trạng thái SLA không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền currentStatus = -1
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "3",
  "message": "Trạng thái SLA không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền currentStatus = chuỗi ký tự ("Dự thảo")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền currentStatus = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Thiếu trường trạng thái hiện tại",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền currentStatus = số thập phân (1.5)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền currentStatus = boolean (true)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền currentStatus = mảng ([1])
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền currentStatus = object ({})
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### slaName: String (Required, maxLength: 100)

#### Để trống slaName
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "Tên cấu hình SLA bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền slaName
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaName = 99 ký tự
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = 100 ký tự (maxLength)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = 101 ký tự (vượt maxLength)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "28",
  "message": "Tên cấu hình SLA không được vượt quá 100 ký tự",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaName = ký tự số ("12345")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = chữ thường không dấu ("sla chuan")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = chữ hoa không dấu ("SLA CHẤP THUẬN")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = chữ có dấu tiếng Việt
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = ký tự đặc biệt cho phép (_- )
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = ký tự đặc biệt không cho phép (!@#$%)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = all space ("          ")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "Tên cấu hình SLA bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaName = space đầu/cuối
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = emoji
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = Unicode đặc biệt
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = boolean (true)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaName = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaName = object
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền slaName = XSS
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = SQL INJECTION
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền slaName = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "Tên cấu hình SLA bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### approvalFlowType: JSONB (Required)

#### Để trống approvalFlowType
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "approvalFlowType bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền approvalFlowType
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền approvalFlowType = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "approvalFlowType bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền approvalFlowType = JSON hợp lệ (object có code và name)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền approvalFlowType = JSON sai syntax (thiếu đóng ngoặc)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền approvalFlowType = object rỗng ({})
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "4",
  "message": "Loại đẩy duyệt không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền approvalFlowType = mảng rỗng ([])
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền approvalFlowType = chuỗi rỗng ("")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "4",
  "message": "Loại đẩy duyệt không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền approvalFlowType = string thuần ("Luồng CN đề xuất")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "4",
  "message": "Loại đẩy duyệt không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền approvalFlowType = number thuần (123)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền approvalFlowType = boolean (true)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền approvalFlowType = JSON object có trường code và name hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền approvalFlowType = XSS trong JSON value
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "4",
  "message": "Loại đẩy duyệt không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền approvalFlowType = SQL INJECTION trong JSON value
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "4",
  "message": "Loại đẩy duyệt không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### effectiveDate: Date yyyy-MM-dd (Required)

#### Để trống effectiveDate
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "effectiveDate bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền effectiveDate
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền effectiveDate = ngày hợp lệ lớn hơn hoặc bằng Today
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền effectiveDate = Today
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền effectiveDate = ngày trong quá khứ (Today - 1)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "26",
  "message": "Ngày hiệu lực không được phép là ngày trong quá khứ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền effectiveDate = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "effectiveDate bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền effectiveDate = chuỗi rỗng ("")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "effectiveDate bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền effectiveDate = định dạng sai (dd/MM/yyyy)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền effectiveDate = ngày không hợp lệ (2026-13-45)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền effectiveDate = số (20260327)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền effectiveDate = boolean
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền effectiveDate = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền effectiveDate = object
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### expiredDate: Date yyyy-MM-dd (Optional)

#### Không truyền expiredDate
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền expiredDate = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền expiredDate = chuỗi rỗng ("")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền expiredDate = ngày lớn hơn effectiveDate
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền expiredDate = bằng effectiveDate
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền expiredDate nhỏ hơn effectiveDate
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "21",
  "message": "Ngày hết hạn phải lớn hơn hoặc bằng ngày hiệu lực",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền expiredDate = ngày trong quá khứ (Today - 1)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "27",
  "message": "Ngày hết hiệu lực không được phép là ngày trong quá khứ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền expiredDate = định dạng sai
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền expiredDate = ngày không hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền expiredDate = boolean
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền expiredDate = number
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền expiredDate = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền expiredDate = object
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### terms: Array<String> (Required)

#### Để trống terms
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "terms bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền terms
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền terms = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "terms bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền terms = mảng rỗng ([])
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "terms bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền terms = mảng hợp lệ (["SHORT", "MEDIUM"])
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền terms = mảng 1 phần tử (["SHORT"])
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền terms = chuỗi rỗng ("")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền terms = chuỗi thuần ("SHORT")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền terms = number
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền terms = boolean
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền terms = object
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền terms = mảng chứa giá trị null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền terms = mảng chứa chuỗi rỗng ("")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### creditMethod: String (Optional)

#### Không truyền creditMethod
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền creditMethod = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền creditMethod = chuỗi rỗng ("")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền creditMethod = giá trị hợp lệ ("LIMIT")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền creditMethod = "MON"
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền creditMethod = giá trị không hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền creditMethod = boolean
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền creditMethod = number
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền creditMethod = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền creditMethod = object
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### totalSlaHours: Integer (Required, max 2 chữ số)

#### Để trống totalSlaHours
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "totalSlaHours bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền totalSlaHours
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền totalSlaHours = 0
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền totalSlaHours = số dương hợp lệ (24)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền totalSlaHours = 99 (max)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền totalSlaHours = 100 (vượt max 2 chữ số)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "30",
  "message": "totalSlaHours có giá trị lớn nhất là 99",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền totalSlaHours = số âm (-1)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền totalSlaHours = số thập phân (24.5)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền totalSlaHours = chuỗi số ("24")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền totalSlaHours = chuỗi ký tự ("abc")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền totalSlaHours = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "totalSlaHours bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền totalSlaHours = boolean
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền totalSlaHours = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền totalSlaHours = object
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền totalSlaHours = số rất lớn (9999999999)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "30",
  "message": "totalSlaHours có giá trị lớn nhất là 99",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền totalSlaHours = leading zero (024)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

### hasEnvRisk: Boolean (Required)

#### Để trống hasEnvRisk
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "hasEnvRisk bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền hasEnvRisk
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền hasEnvRisk = true
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền hasEnvRisk = false
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền hasEnvRisk = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "hasEnvRisk bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền hasEnvRisk = chuỗi ("true")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền hasEnvRisk = số (1)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền hasEnvRisk = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền hasEnvRisk = object
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### warningYellowPct: Number (Required, range [0, 100], max 2 chữ số thập phân)

#### Để trống warningYellowPct
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "warningYellowPct bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền warningYellowPct
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền warningYellowPct = 0
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền warningYellowPct = 50.00 (số thập phân hợp lệ)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền warningYellowPct = 100.00 (max range)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền warningYellowPct = 100.01 (vượt max range)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "30",
  "message": "warningYellowPct có giá trị lớn nhất là 100",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền warningYellowPct = -1 (nhỏ hơn min range)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "29",
  "message": "warningYellowPct có giá trị nhỏ nhất là 0",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền warningYellowPct = 50.123 (vượt 2 chữ số thập phân)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "31",
  "message": "warningYellowPct có tối đa 2 chữ số phần nguyên và 2 chữ số phần thập phân",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền warningYellowPct = 50.1 (đúng 1 chữ số thập phân)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền warningYellowPct = chuỗi số ("50")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền warningYellowPct = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "warningYellowPct bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền warningYellowPct = chuỗi ký tự ("abc")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền warningYellowPct = boolean
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền warningYellowPct = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền warningYellowPct = object
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### description: String (Optional, maxLength: 500)

#### Không truyền description
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền description = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền description = chuỗi rỗng ("")
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền description = 500 ký tự (maxLength)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền description = 501 ký tự (vượt maxLength)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "28",
  "message": "description không được vượt quá 500 ký tự",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền description = ký tự tiếng Việt có dấu
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền description = ký tự đặc biệt
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền description = all space
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền description = boolean
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền description = number
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền description = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền description = object
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### steps: Array<Step> (Required)

#### Để trống steps
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "steps bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền steps
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền steps = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "steps bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền steps = mảng rỗng ([])
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "steps bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền steps = mảng object hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền steps = chuỗi thuần
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền steps = number
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền steps = object
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Step.processStepId: Long (Required trong mỗi step)

#### Truyền step thiếu processStepId
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền step với processStepId = 0
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền step với processStepId = chuỗi
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Step.slaHours: Number (Required trong mỗi step)

#### Truyền step thiếu slaHours
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền step với slaHours = 0
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền step với slaHours = số dương hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền step với slaHours = số âm
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền step với slaHours = chuỗi
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Step.warningPct: Number (Required trong mỗi step)

#### Truyền step thiếu warningPct
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền step với warningPct = 50.00
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền step với warningPct = -1
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "29",
  "message": "warningPct có giá trị nhỏ nhất là 0",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền step với warningPct = 101
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "30",
  "message": "warningPct có giá trị lớn nhất là 100",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### businessObject: JSONB (Required)

#### Để trống businessObject
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "businessObject bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Không truyền businessObject
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền businessObject = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "businessObject bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền businessObject = JSON object hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền businessObject = object rỗng ({})
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền businessObject = JSON sai syntax
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền businessObject = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền businessObject = chuỗi rỗng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền businessObject = number
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền businessObject = boolean
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### customerType: JSONB (Required)

#### Để trống customerType
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "customerType bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền customerType = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "customerType bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền customerType = JSON object hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền customerType = object rỗng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền customerType = JSON sai syntax
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền customerType = chuỗi
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền customerType = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### bcdxType: JSONB (Required)

#### Để trống bcdxType
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "bcdxType bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền bcdxType = null
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "25",
  "message": "bcdxType bắt buộc nhập",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền bcdxType = JSON object hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền bcdxType = object rỗng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {}
}

#### Truyền bcdxType = JSON sai syntax
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền bcdxType = chuỗi
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

#### Truyền bcdxType = mảng
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

## Kiểm tra luồng chính

### Kiểm tra chỉnh sửa SLA thành công khi trạng thái hiện tại = 0 (Dự thảo) và tất cả trường hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {
    "slaId": 1,
    "slaCode": "SLA1",
    "versionId": 10001,
    "versionNo": 2,
    "status": "DRAFT",
    "createdAt": "2026-03-27T10:00:00Z",
    "createdBy": "admin"
  }
}
SQL:
SELECT ID, SLA_MASTER_ID, VERSION_NO, STATUS, SLA_NAME,
       EFFECTIVE_DATE, EXPIRED_DATE, TERMS,
       TOTAL_SLA_HOURS, HAS_ENV_RISK, WARNING_YELLOW_PCT,
       DESCRIPTION, BUSINESS_OBJECT, CUSTOMER_TYPE, BCDX_TYPE,
       CREDIT_METHOD, APPROVAL_FLOW_TYPE,
       UPDATED_AT, UPDATED_BY,
       BASE_VERSION_ID, SNAPSHOT_DATA, DIFF_DATA
FROM SLA_VERSION
WHERE ID = 10001;

SELECT ID, SLA_VERSION_ID, PROCESS_STEP_ID,
       STEP_ORDER, SLA_HOURS, WARNING_PCT, CREATED_AT
FROM SLA_VERSION_STEP
WHERE SLA_VERSION_ID = 10001;

SELECT ID, SLA_VERSION_ID, STATUS, ACTION_TYPE,
       NOTE, BEFORE_DATA, AFTER_DATA,
       CREATED_AT, CREATED_BY
FROM SLA_VERSION_HISTORY
WHERE SLA_VERSION_ID = 10001
ORDER BY CREATED_AT DESC;

### Kiểm tra chỉnh sửa SLA thành công khi trạng thái hiện tại = 3 (Từ chối) và tất cả trường hợp lệ
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {
    "slaId": 1,
    "slaCode": "SLA1",
    "versionId": 10001,
    "versionNo": 2,
    "status": "DRAFT",
    "createdAt": "2026-03-27T10:00:00Z",
    "createdBy": "admin"
  }
}
SQL:
SELECT * FROM SLA_VERSION WHERE ID = 10001;

### Kiểm tra chỉnh sửa SLA khi trạng thái giao dịch đã thay đổi (BR1)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "5",
  "message": "Trạng thái SLA đã bị thay đổi. Vui lòng nhấn F5 để cập nhật lại",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi trạng thái giao dịch không hợp lệ (BR2)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "3",
  "message": "Trạng thái SLA không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi tồn tại phiên bản Đang xử lý khác (LDH_SLA_009)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "9",
  "message": "SLA đang được chỉnh sửa. Vui lòng thử lại sau",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi tên SLA trùng với SLA đã duyệt (LDH_SLA_001)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "1",
  "message": "Tên SLA đã tồn tại. Vui lòng kiểm tra lại",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi slaVersionId không tồn tại (LDH_SLA_002)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "2",
  "message": "Không tìm thấy thông tin SLA",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi approvalFlowType không hợp lệ (LDH_SLA_004)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "4",
  "message": "Loại đẩy duyệt không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi không tìm thấy lịch sử trạng thái (LDH_SLA_007)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "7",
  "message": "Không tìm thấy lịch sử trạng thái cho SLA",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi không phải phiên bản mới nhất (LDH_SLA_008)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "8",
  "message": "Chỉ được chỉnh sửa phiên bản mới nhất",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi expiredDate nhỏ hơn effectiveDate (LDH_SLA_021)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "21",
  "message": "Ngày hết hạn phải lớn hơn hoặc bằng ngày hiệu lực",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi effectiveDate trong quá khứ (LDH_SLA_026)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "26",
  "message": "Ngày hiệu lực không được phép là ngày trong quá khứ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi expiredDate trong quá khứ (LDH_SLA_027)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "27",
  "message": "Ngày hết hiệu lực không được phép là ngày trong quá khứ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA với tên SLA trùng nhưng ngày hiệu lực không overlap (không báo lỗi LDH_SLA_001)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {
    "slaId": 2,
    "slaCode": "SLA2",
    "versionId": 10002,
    "versionNo": 1,
    "status": "DRAFT",
    "createdAt": "2026-03-27T10:00:00Z",
    "createdBy": "admin"
  }
}

### Kiểm tra chỉnh sửa SLA khi dữ liệu JSON sai format nghiệp vụ trong businessObject
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA khi tất cả trường required bị bỏ trống cùng lúc
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "20",
  "message": "Dữ liệu đầu vào không hợp lệ",
  "traceId": "string",
  "responseTime": "string",
  "data": null
}

### Kiểm tra chỉnh sửa SLA với expiredDate = null (không bắt buộc)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {
    "slaId": 1,
    "slaCode": "SLA1",
    "versionId": 10003,
    "versionNo": 3,
    "status": "DRAFT",
    "createdAt": "2026-03-27T10:00:00Z",
    "createdBy": "admin"
  }
}
SQL:
SELECT ID, SLA_NAME, EFFECTIVE_DATE, EXPIRED_DATE
FROM SLA_VERSION
WHERE ID = 10003;
-- Kỳ vọng EXPIRED_DATE = NULL hoặc giá trị mặc định 2099-12-31

### Kiểm tra chỉnh sửa SLA khi creditMethod = null (không bắt buộc)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {
    "slaId": 1,
    "slaCode": "SLA1",
    "versionId": 10004,
    "versionNo": 4,
    "status": "DRAFT",
    "createdAt": "2026-03-27T10:00:00Z",
    "createdBy": "admin"
  }
}
SQL:
SELECT ID, CREDIT_METHOD
FROM SLA_VERSION
WHERE ID = 10004;
-- Kỳ vọng CREDIT_METHOD = NULL

### Kiểm tra chỉnh sửa SLA khi description = null (không bắt buộc)
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {
    "slaId": 1,
    "slaCode": "SLA1",
    "versionId": 10005,
    "versionNo": 5,
    "status": "DRAFT",
    "createdAt": "2026-03-27T10:00:00Z",
    "createdBy": "admin"
  }
}
SQL:
SELECT ID, DESCRIPTION
FROM SLA_VERSION
WHERE ID = 10005;
-- Kỳ vọng DESCRIPTION = NULL

### Kiểm tra chỉnh sửa SLA với nhiều bước trong steps array
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {
    "slaId": 1,
    "slaCode": "SLA1",
    "versionId": 10006,
    "versionNo": 6,
    "status": "DRAFT",
    "createdAt": "2026-03-27T10:00:00Z",
    "createdBy": "admin"
  }
}
SQL:
SELECT PROCESS_STEP_ID, STEP_ORDER, SLA_HOURS, WARNING_PCT
FROM SLA_VERSION_STEP
WHERE SLA_VERSION_ID = 10006
ORDER BY STEP_ORDER ASC;
-- Kỳ vọng: 4 dòng với đúng STEP_ORDER 1, 2, 3, 4

### Kiểm tra chỉnh sửa SLA với terms chứa nhiều giá trị
- 1. Check api trả về:
  1.1. Status: 200
  1.2. Response:
{
  "code": "00",
  "message": "Thành công",
  "traceId": "string",
  "responseTime": "string",
  "data": {
    "slaId": 1,
    "slaCode": "SLA1",
    "versionId": 10007,
    "versionNo": 7,
    "status": "DRAFT",
    "createdAt": "2026-03-27T10:00:00Z",
    "createdBy": "admin"
  }
}
SQL:
SELECT ID, TERMS
FROM SLA_VERSION
WHERE ID = 10007;
-- Kỳ vọng TERMS chứa ["SHORT", "MEDIUM", "LONG"]
