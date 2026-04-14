# API vấn tin danh sách yêu cầu thay đổi số TK liên kết thẻ GNQT

## Kiểm tra phân quyền

### Kiểm tra người dùng được phân quyền VIEW

- Status: 200
  
### Kiểm tra người dùng không được phân quyền VIEW

- Status: 403
  
## Kiểm tra token

### Kiểm tra nhập token hết hạn

- Status: 401
  
### Kiểm tra không nhập token

- Status: 401
  
### Kiểm tra nhập token không hợp lệ (sai token)

- Status: 401
  
### Kiểm tra nhập token hợp lệ

- Status: 200
  
## Kiểm tra Endpoint & Method

### Kiểm tra nhập sai method (POST/PUT/DELETE)

- Status: 405
  
### Kiểm tra nhập sai endpoint

- Status: 404
  
## Kiểm tra Validate

### Trường requestType

- Kiểm tra không truyền trường requestType
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType là mảng rỗng []
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType với 1 giá trị hợp lệ = ["ACTIVATE_CARD"]
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType với nhiều giá trị hợp lệ (multi-select)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType chứa giá trị không nằm trong danh sách enum
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType chứa chuỗi rỗng trong mảng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType là String
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
       }
       
- Kiểm tra truyền trường requestType là Object
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
       }
       
- Kiểm tra truyền trường requestType chứa ký tự đặc biệt trong mảng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType chứa SQL Injection trong mảng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType chứa XSS trong mảng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType chứa phần tử trùng nhau trong mảng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường requestType là mảng chứa phần tử là Integer sai kiểu
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
### Trường status

- Kiểm tra không truyền trường status
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường status = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường status là mảng rỗng []
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường status với 1 giá trị hợp lệ = ["PENDING_APPROVAL"]
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường status với nhiều giá trị hợp lệ (multi-select)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường status chứa giá trị không nằm trong danh sách enum
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường status chứa chuỗi rỗng trong mảng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường status là String
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường status là kiểu dữ liệu không phải mảng (Object)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường status chứa ký tự đặc biệt trong mảng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       }
       
- Kiểm tra truyền trường status chứa SQL Injection trong mảng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường status chứa XSS trong mảng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường status chứa phần tử trùng nhau trong mảng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường status là mảng chứa phần tử là Integer sai kiểu
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
### Trường fromDate

- Kiểm tra không truyền trường fromDate
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường fromDate = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường fromDate rỗng = ""
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường fromDate đúng định dạng yyyy-MM-dd, ngày hợp lệ trong khoảng 1 năm trở về quá khứ
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường fromDate không đúng định dạng (thiếu dấu gạch ngang, dạng yyyyMMdd)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường fromDate không đúng định dạng (dạng dd/MM/yyyy)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường fromDate không đúng định dạng (chuỗi ký tự chữ không phải ngày)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường fromDate là ngày không tồn tại (2026-02-31)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường fromDate là ngày tương lai
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường fromDate là ngày hiện tại
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường fromDate quá khứ hơn 1 năm so với ngày hiện tại
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường fromDate chứa ký tự đặc biệt không hợp lệ(@@@@-@@-@)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường fromDate là kiểu số nguyên (Integer)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường fromDate là Object
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường fromDate là Array
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
       "}
       
### Trường toDate

- Kiểm tra không truyền trường toDate
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường toDate = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường toDate rỗng = ""
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường toDate đúng định dạng yyyy-MM-dd, ngày  quá khứ trong vòng 1 năm kể từ ngày hiện tại
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường toDate đúng định dạng yyyy-MM-dd, ngày quá khứ quá 1 năm kể từ ngày hiện tại
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường toDate đúng định dạng yyyy-MM-dd, ngày hợp lệ là hôm nay
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường toDate đúng định dạng yyyy-MM-dd, ngày hợp lệ là tương lai
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }  
       }
       
- Kiểm tra truyền trường toDate không đúng định dạng (thiếu dấu gạch ngang, dạng yyyyMMdd)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường toDate không đúng định dạng (dạng dd/MM/yyyy)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường toDate không đúng định dạng (chuỗi ký tự chữ không phải ngày)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường toDate là ngày không tồn tại (2026-02-30)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường toDate là ngày tương lai
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường toDate trước fromDate 
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường toDate bằng fromDate (toDate = fromDate)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường toDate sau fromDate (toDate > fromDate, khoảng hợp lệ)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường toDate chứa ký tự đặc biệt không hợp lệ(@@@@-@@-@)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường toDate là kiểu số nguyên (Integer)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường toDate là Object
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường toDate là Array
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
### Trường search

- Kiểm tra không truyền trường search
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường search = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường search rỗng = ""
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường search = {39 ký tự hợp lệ} (maxLength-1)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường search = {40 ký tự hợp lệ} (maxLength)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường search = {41 ký tự hợp lệ} (maxLength+1)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường search chứa ký tự số (0-9)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường search chứa chữ thường/hoa không dấu (a-z, A-Z)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường search chứa chữ có dấu tiếng Việt
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường search chứa ký tự đặc biệt không được phép
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường search toàn khoảng trắng (all space)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường search có khoảng trắng ở giữa (space ở giữa)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS",  
       "data": {  
       "items": [...],  
       "total": ...  
       }  
       }
       
- Kiểm tra truyền trường search có khoảng trắng đầu/cuối
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường search chứa XSS
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường search chứa SQL Injection
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường search là Object
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường search là Array
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
### Trường page

- Kiểm tra không truyền trường page
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường page = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường page sai kiểu dữ liệu (String thay vì Object)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường page sai kiểu dữ liệu (Integer thay vì Object)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường page sai kiểu dữ liệu (Array thay vì Object)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường page là Object rỗng ({})
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường page là Object hợp lệ có pageSize và pageNum
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
### Trường pageSize

- Kiểm tra không truyền trường pageSize
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường pageSize = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường pageSize để trống ("")
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường pageSize sai kiểu dữ liệu (String thay vì Integer)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       }
       
- Kiểm tra truyền trường pageSize sai kiểu dữ liệu (Boolean thay vì Integer)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageSize sai kiểu dữ liệu (Object thay vì Integer)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageSize sai kiểu dữ liệu (Array thay vì Integer)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageSize là số nguyên dương
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageSize là số âm
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageSize là số thập phân
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageSize = 0
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageSize chứa ký tự XSS
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
       }
       
- Kiểm tra truyền trường pageSize chứa SQL Injection
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
### Trường pageNum

- Kiểm tra không truyền trường pageNum
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường pageNum = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường pageNum để trống ("")
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường pageNum sai kiểu dữ liệu (String thay vì Integer)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageNum sai kiểu dữ liệu (Boolean thay vì Integer)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageNum sai kiểu dữ liệu (Object thay vì Integer)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageNum sai kiểu dữ liệu (Array thay vì Integer)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageNum = 1 (giá trị hợp lệ tối thiểu)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường pageNum là số dương hợp lệ
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường pageNum = 0 (nhỏ hơn giá trị tối thiểu)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageNum là số âm
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageNum là số thập phân
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageNum chứa ký tự XSS
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường pageNum chứa SQL Injection
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
### Trường orders

- Kiểm tra không truyền trường orders
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders sai kiểu dữ liệu (String thay vì Object)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders sai kiểu dữ liệu (Integer thay vì Object)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders sai kiểu dữ liệu (Array thay vì Object)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders sai kiểu dữ liệu (Boolean thay vì Array)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders là  Object hợp lệ (có field và direction)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders là Object nhiều phần tử hợp lệ
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders là là Object rỗng ({})
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
### Trường orders.Field

- Kiểm tra không truyền trường orders.Field
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders.Field = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders.Field để trống ("")
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders.Field = "createdBy" (giá trị hợp lệ trong enum)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders.Field là giá trị không nằm trong enum hợp lệ
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders.Field sai kiểu dữ liệu (Integer thay vì String)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders.Field sai kiểu dữ liệu (Boolean thay vì String)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders.Field sai kiểu dữ liệu (Object thay vì String)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders.Field sai kiểu dữ liệu (Array thay vì String)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders.Field chứa khoảng trắng đầu/cuối
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders.Field chứa toàn khoảng trắng
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders.Field chứa khoảng trắng ở giữa
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders.Field chứa ký tự đặc biệt
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders.Field chứa ký tự XSS
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường orders.Field chứa SQL Injection
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
### Trường orders.Direction

- Kiểm tra không truyền trường orders.Direction
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders.Direction = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders.Direction = ""
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders.Direction = giá trị hợp lệ "ASC"
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường orders.Direction = giá trị hợp lệ "DESC"
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường ordersDirection giá trị không nằm trong enum
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường ordersDirection sai kiểu dữ liệu (number)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường ordersDirection sai kiểu dữ liệu (array)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường ordersDirection chứa ký tự đặc biệt
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường ordersDirection chứa XSS
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường ordersDirection chứa SQL Injection
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
### Trường isChecker

- Kiểm tra không truyền trường isChecker
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường isChecker = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường isChecker = true/false chữ thường
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường isChecker = true/false chữ hoa
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường isChecker sai kiểu dữ liệu (khác chuỗi "true"/"false")
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
       }
       
- Kiểm tra truyền trường isChecker sai kiểu dữ liệu (số nguyên 0/1)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
       }
       
- Kiểm tra truyền trường isChecker sai kiểu dữ liệu (array)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường isChecker sai kiểu dữ liệu (OBJECT)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường isChecker sai kiểu dữ liệu (String)
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
### Trường createdBy

- Kiểm tra không truyền trường createdBy
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường createdBy = null
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường createdBy = ""
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường createdBy là chuỗi ký tự hợp lệ
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường createdBy chứa ký tự số
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường createdBy chứa chữ thường/hoa không dấu
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       "status": 0,  
       "code": "0",  
       "message": "SUCCESS"  
       }
       
- Kiểm tra truyền trường createdBy chứa chữ có dấu tiếng Việt
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
       }
       
- Kiểm tra truyền trường createdBy chứa ký tự đặc biệt
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường createdBy all space
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường createdBy có space ở giữa
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường createdBy có space đầu/cuối
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường createdBy chứa XSS
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường createdBy chứa SQL Injection
  
    1. Check api trả về:  
       1.1.Status: 200  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường createdBy sai kiểu dữ liệu (number)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường createdBy sai kiểu dữ liệu (array)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
- Kiểm tra truyền trường createdBy sai kiểu dữ liệu (object)
  
    1. Check api trả về:  
       1.1.Status: 400  
       1.2.Response:  
       {  
         
       }
       
## Kiểm tra chức năng

### Kiểm tra response khi không truyền filter

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006712",  
   "createdBy": "1578490uyendo",  
   "createdDate": "2025-11-07T17:44:33",  
   "updatedDate": "2025-11-07T17:45:17",  
   "acceptedDate": "2025-11-07T17:44:32",  
   "status": "FAILED",  
   "statusDesc": "Không thành công",  
   "requestType": "UNLOCK_TRANS",  
   "requestTypeDesc": "Khoá/mở khóa giao dịch",  
   "cardDisplay": "406220******6585",  
   "cardHolderName": "CONTACT CENTER CORPORATE YEN TEST TRUONG NGON THANH MAI",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CREATED_DATE DESC  
   
   
### Kiểm tra response khi truyền requestType = CHANGE_PRIMARY_LINKED_ACCOUNT

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006800",  
   "createdBy": "1578490maker01",  
   "createdDate": "2026-01-10T09:00:00",  
   "updatedDate": "2026-01-10T09:01:00",  
   "acceptedDate": "2026-01-10T09:00:59",  
   "status": "SUCCESS",  
   "statusDesc": "Thành công",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "requestTypeDesc": "Thay đổi TK liên kết chính",  
   "cardDisplay": "406220******7001",  
   "cardHolderName": "NGUYEN VAN A",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "12345678901"  
   }  
   ],  
   "total": 5  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CARD_ACTION_TYPE = 'CHANGE_PRIMARY_LINKED_ACCOUNT'  
   ORDER BY CREATED_DATE DESC  
   
   
### Kiểm tra response khi truyền requestType = ACTIVATE_CARD

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006001",  
   "createdBy": "1578490maker02",  
   "createdDate": "2026-02-01T08:30:00",  
   "updatedDate": "2026-02-01T08:31:00",  
   "acceptedDate": "2026-02-01T08:30:59",  
   "status": "SUCCESS",  
   "statusDesc": "Thành công",  
   "requestType": "ACTIVATE_CARD",  
   "requestTypeDesc": "Kích hoạt thẻ",  
   "cardDisplay": "406220******1001",  
   "cardHolderName": "TRAN THI B",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 3  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CARD_ACTION_TYPE = 'ACTIVATE_CARD'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền requestType = UNLOCK_TRANS

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006002",  
   "createdBy": "1578490maker03",  
   "createdDate": "2026-02-02T10:00:00",  
   "updatedDate": "2026-02-02T10:01:00",  
   "acceptedDate": "2026-02-02T10:00:59",  
   "status": "FAILED",  
   "statusDesc": "Không thành công",  
   "requestType": "UNLOCK_TRANS",  
   "requestTypeDesc": "Khoá/mở khóa giao dịch",  
   "cardDisplay": "406220******6585",  
   "cardHolderName": "LE VAN C",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 2  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CARD_ACTION_TYPE = 'UNLOCK_TRANS'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền requestType = CARD_CREDIT_PAYMENT

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006003",  
   "createdBy": "1578490maker04",  
   "createdDate": "2026-02-03T11:00:00",  
   "updatedDate": "2026-02-03T11:01:00",  
   "acceptedDate": "2026-02-03T11:00:59",  
   "status": "SUCCESS",  
   "statusDesc": "Thành công",  
   "requestType": "CARD_CREDIT_PAYMENT",  
   "requestTypeDesc": "Thanh toán thẻ tín dụng",  
   "cardDisplay": "406220******3003",  
   "cardHolderName": "PHAM THI D",  
   "transAmount": 5000000,  
   "ccy": "VND",  
   "accountNo": "98765432100"  
   }  
   ],  
   "total": 4  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CARD_ACTION_TYPE = 'CARD_CREDIT_PAYMENT'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền requestType = BLOCK_OR_UNLOCK_CARD

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006004",  
   "createdBy": "1578490maker05",  
   "createdDate": "2026-02-04T09:00:00",  
   "updatedDate": "2026-02-04T09:01:00",  
   "acceptedDate": "2026-02-04T09:00:59",  
   "status": "PENDING_APPROVAL",  
   "statusDesc": "Chờ duyệt",  
   "requestType": "BLOCK_OR_UNLOCK_CARD",  
   "requestTypeDesc": "Khoá/mở thẻ",  
   "cardDisplay": "406220******4004",  
   "cardHolderName": "HOANG VAN E",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 6  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CARD_ACTION_TYPE = 'BLOCK_OR_UNLOCK_CARD'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền requestType = BATCH_CARD_CREDIT_PAYMENT

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006005",  
   "createdBy": "1578490maker06",  
   "createdDate": "2026-02-05T14:00:00",  
   "updatedDate": "2026-02-05T14:01:00",  
   "acceptedDate": "2026-02-05T14:00:59",  
   "status": "BANK_PROCESSING",  
   "statusDesc": "Ngân hàng đang xử lý",  
   "requestType": "BATCH_CARD_CREDIT_PAYMENT",  
   "requestTypeDesc": "Thanh toán thẻ tín dụng theo lô",  
   "cardDisplay": null,  
   "cardHolderName": null,  
   "transAmount": 20000000,  
   "ccy": "VND",  
   "accountNo": "11223344550"  
   }  
   ],  
   "total": 2  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CARD_ACTION_TYPE = 'BATCH_CARD_CREDIT_PAYMENT'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền status = PENDING_APPROVAL

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006100",  
   "status": "PENDING_APPROVAL",  
   "statusDesc": "Chờ duyệt",  
   "requestType": "ACTIVATE_CARD",  
   "requestTypeDesc": "Kích hoạt thẻ",  
   "cardDisplay": "406220******1100",  
   "cardHolderName": "VU THI F",  
   "createdBy": "1578490maker07",  
   "createdDate": "2026-03-01T08:00:00",  
   "updatedDate": "2026-03-01T08:00:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 8  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND STATUS = 'PENDING_APPROVAL'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền status = SUCCESS

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006101",  
   "status": "SUCCESS",  
   "statusDesc": "Thành công",  
   "requestType": "UNLOCK_TRANS",  
   "requestTypeDesc": "Khoá/mở khóa giao dịch",  
   "cardDisplay": "406220******1101",  
   "cardHolderName": "DINH VAN G",  
   "createdBy": "1578490maker08",  
   "createdDate": "2026-03-02T09:00:00",  
   "updatedDate": "2026-03-02T09:01:00",  
   "acceptedDate": "2026-03-02T09:00:59",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 15  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND STATUS = 'SUCCESS'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền status = REJECTED

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006102",  
   "status": "REJECTED",  
   "statusDesc": "Từ chối duyệt",  
   "requestType": "BLOCK_OR_UNLOCK_CARD",  
   "requestTypeDesc": "Khoá/mở thẻ",  
   "cardDisplay": "406220******1102",  
   "cardHolderName": "NGUYEN THI H",  
   "createdBy": "1578490maker09",  
   "createdDate": "2026-03-03T10:00:00",  
   "updatedDate": "2026-03-03T10:05:00",  
   "acceptedDate": "2026-03-03T10:04:59",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 3  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND STATUS = 'REJECTED'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền status = UNDEFINED

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006103",  
   "status": "UNDEFINED",  
   "statusDesc": "Chưa xác định",  
   "requestType": "CARD_CREDIT_PAYMENT",  
   "requestTypeDesc": "Thanh toán thẻ tín dụng",  
   "cardDisplay": "406220******1103",  
   "cardHolderName": "TRAN VAN I",  
   "createdBy": "1578490maker10",  
   "createdDate": "2026-03-04T11:00:00",  
   "updatedDate": "2026-03-04T11:00:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 1  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND STATUS = 'UNDEFINED'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền status = FAILED

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006104",  
   "status": "FAILED",  
   "statusDesc": "Không thành công",  
   "requestType": "ACTIVATE_CARD",  
   "requestTypeDesc": "Kích hoạt thẻ",  
   "cardDisplay": "406220******1104",  
   "cardHolderName": "LE THI J",  
   "createdBy": "1578490maker11",  
   "createdDate": "2026-03-05T12:00:00",  
   "updatedDate": "2026-03-05T12:01:00",  
   "acceptedDate": "2026-03-05T12:00:59",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 7  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND STATUS = 'FAILED'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền status = CANCELLED

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006105",  
   "status": "CANCELLED",  
   "statusDesc": "Hết hiệu lực",  
   "requestType": "UNLOCK_TRANS",  
   "requestTypeDesc": "Khoá/mở khóa giao dịch",  
   "cardDisplay": "406220******1105",  
   "cardHolderName": "PHAM VAN K",  
   "createdBy": "1578490maker12",  
   "createdDate": "2026-03-06T13:00:00",  
   "updatedDate": "2026-03-06T13:05:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 2  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND STATUS = 'CANCELLED'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền status = BANK_PROCESSING

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006106",  
   "status": "BANK_PROCESSING",  
   "statusDesc": "Ngân hàng đang xử lý",  
   "requestType": "BATCH_CARD_CREDIT_PAYMENT",  
   "requestTypeDesc": "Thanh toán thẻ tín dụng theo lô",  
   "cardDisplay": null,  
   "cardHolderName": null,  
   "createdBy": "1578490maker13",  
   "createdDate": "2026-03-07T14:00:00",  
   "updatedDate": "2026-03-07T14:00:00",  
   "acceptedDate": null,  
   "transAmount": 10000000,  
   "ccy": "VND",  
   "accountNo": "55667788990"  
   }  
   ],  
   "total": 1  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND STATUS = 'BANK_PROCESSING'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền status = PARTIALLY_SUCCESS

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006107",  
   "status": "PARTIALLY_SUCCESS",  
   "statusDesc": "Thành công một phần",  
   "requestType": "BATCH_CARD_CREDIT_PAYMENT",  
   "requestTypeDesc": "Thanh toán thẻ tín dụng theo lô",  
   "cardDisplay": null,  
   "cardHolderName": null,  
   "createdBy": "1578490maker14",  
   "createdDate": "2026-03-08T15:00:00",  
   "updatedDate": "2026-03-08T15:02:00",  
   "acceptedDate": "2026-03-08T15:01:59",  
   "transAmount": 15000000,  
   "ccy": "VND",  
   "accountNo": "99887766550"  
   }  
   ],  
   "total": 1  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND STATUS = 'PARTIALLY_SUCCESS'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền fromDate và toDate trong khoảng tồn tại kết quả

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006200",  
   "status": "SUCCESS",  
   "statusDesc": "Thành công",  
   "requestType": "ACTIVATE_CARD",  
   "requestTypeDesc": "Kích hoạt thẻ",  
   "cardDisplay": "406220******2001",  
   "cardHolderName": "NGUYEN VAN L",  
   "createdBy": "1578490maker15",  
   "createdDate": "2026-03-10T09:00:00",  
   "updatedDate": "2026-03-10T09:01:00",  
   "acceptedDate": "2026-03-10T09:00:59",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 5  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CREATED_DATE >= '2026-03-01 00:00:00'  
   AND CREATED_DATE <= '2026-03-31 23:59:59'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền fromDate và toDate trong khoảng không tồn tại kết quả

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   ],  
   "total": 0  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CREATED_DATE >= '2026-03-01 00:00:00'  
   AND CREATED_DATE <= '2026-03-31 23:59:59'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền fromDate và toDate trong khoảng không tồn tại kết quả

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   ],  
   "total": 0  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CREATED_DATE >= '2026-03-01 00:00:00'  
   AND CREATED_DATE <= '2026-03-31 23:59:59'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền fromDate 

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   ],  
   "total": 0  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CREATED_DATE >= '2026-03-01 00:00:00''  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền  toDate 

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   ],  
   "total": 0  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CREATED_DATE <= '2026-03-31 23:59:59'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi tìm kiếm theo search khớp với CARD_DISPLAY

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006300",  
   "status": "SUCCESS",  
   "statusDesc": "Thành công",  
   "requestType": "UNLOCK_TRANS",  
   "requestTypeDesc": "Khoá/mở khóa giao dịch",  
   "cardDisplay": "406220******6585",  
   "cardHolderName": "TRAN VAN M",  
   "createdBy": "1578490maker16",  
   "createdDate": "2026-03-11T09:00:00",  
   "updatedDate": "2026-03-11T09:01:00",  
   "acceptedDate": "2026-03-11T09:00:59",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 2  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND (UPPER(TRIM(CARD_DISPLAY)) LIKE UPPER(TRIM('%6585%'))  
   OR UPPER(TRIM(CARD_HOLDER_NAME)) LIKE UPPER(TRIM('%6585%')))  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi tìm kiếm theo search khớp với CARD_HOLDER_NAME

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006301",  
   "status": "PENDING_APPROVAL",  
   "statusDesc": "Chờ duyệt",  
   "requestType": "BLOCK_OR_UNLOCK_CARD",  
   "requestTypeDesc": "Khoá/mở thẻ",  
   "cardDisplay": "406220******3001",  
   "cardHolderName": "NGUYEN VAN AN",  
   "createdBy": "1578490maker17",  
   "createdDate": "2026-03-12T10:00:00",  
   "updatedDate": "2026-03-12T10:00:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 3  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND (UPPER(TRIM(CARD_DISPLAY)) LIKE UPPER(TRIM('%NGUYEN VAN AN%'))  
   OR UPPER(TRIM(CARD_HOLDER_NAME)) LIKE UPPER(TRIM('%NGUYEN VAN AN%')))  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi tìm kiếm theo search không có kết quả

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [],  
   "total": 0  
   }  
   }  
   SQL:  
   SELECT ID, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, STATUS, CARD_ACTION_TYPE, CARD_DISPLAY,CARD_HOLDER_NAME, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND (UPPER(TRIM(CARD_DISPLAY)) LIKE UPPER(TRIM('%XYZNOTFOUND%'))  
   OR UPPER(TRIM(CARD_HOLDER_NAME)) LIKE UPPER(TRIM('%XYZNOTFOUND%')))  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền isChecker = true và createdBy để lọc theo người yêu cầu

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006601",  
   "status": "SUCCESS",  
   "statusDesc": "Thành công",  
   "requestType": "ACTIVATE_CARD",  
   "requestTypeDesc": "Kích hoạt thẻ",  
   "cardDisplay": "406220******6601",  
   "cardHolderName": "VU VAN S",  
   "createdBy": "1578490maker24",  
   "createdDate": "2026-03-26T10:00:00",  
   "updatedDate": "2026-03-26T10:01:00",  
   "acceptedDate": "2026-03-26T10:00:59",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 4  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CREATED_BY = '1578490maker24'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi kết hợp 2 điều kiện requestType + status

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006800",  
   "status": "SUCCESS",  
   "statusDesc": "Thành công",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "requestTypeDesc": "Thay đổi TK liên kết chính",  
   "cardDisplay": "406220******8000",  
   "cardHolderName": "DINH VAN U",  
   "createdBy": "1578490maker25",  
   "createdDate": "2026-04-01T09:00:00",  
   "updatedDate": "2026-04-01T09:01:00",  
   "acceptedDate": "2026-04-01T09:00:59",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "44455566677"  
   }  
   ],  
   "total": 3  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CARD_ACTION_TYPE = 'CHANGE_PRIMARY_LINKED_ACCOUNT'  
   AND STATUS = 'SUCCESS'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi kết hợp 3 điều kiện requestType + status + fromDate/toDate

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006801",  
   "status": "PENDING_APPROVAL",  
   "statusDesc": "Chờ duyệt",  
   "requestType": "BLOCK_OR_UNLOCK_CARD",  
   "requestTypeDesc": "Khoá/mở thẻ",  
   "cardDisplay": "406220******8001",  
   "cardHolderName": "TRAN THI V",  
   "createdBy": "1578490maker26",  
   "createdDate": "2026-04-05T10:00:00",  
   "updatedDate": "2026-04-05T10:00:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 2  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CARD_ACTION_TYPE = 'BLOCK_OR_UNLOCK_CARD'  
   AND STATUS = 'PENDING_APPROVAL'  
   AND CREATED_DATE >= '2026-04-01 00:00:00'  
   AND CREATED_DATE <= '2026-04-10 23:59:59'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi kết hợp tất cả điều kiện lọc và có kết quả

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006802",  
   "status": "SUCCESS",  
   "statusDesc": "Thành công",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "requestTypeDesc": "Thay đổi TK liên kết chính",  
   "cardDisplay": "406220******8002",  
   "cardHolderName": "LE VAN W",  
   "createdBy": "1578490maker27",  
   "createdDate": "2026-04-10T08:00:00",  
   "updatedDate": "2026-04-10T08:01:00",  
   "acceptedDate": "2026-04-10T08:00:59",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "55566677788"  
   }  
   ],  
   "total": 1  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CARD_ACTION_TYPE = 'CHANGE_PRIMARY_LINKED_ACCOUNT'  
   AND STATUS = 'SUCCESS'  
   AND (UPPER(TRIM(CARD_DISPLAY)) LIKE UPPER(TRIM('%8002%'))  
   OR UPPER(TRIM(CARD_HOLDER_NAME)) LIKE UPPER(TRIM('%LE VAN W%')))  
   AND CREATED_DATE >= '2026-04-01 00:00:00'  
   AND CREATED_DATE <= '2026-04-12 23:59:59'  
   AND CREATED_BY = '1578490maker27'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi kết hợp tất cả điều kiện lọc và không có kết quả

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [],  
   "total": 0  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   AND CARD_ACTION_TYPE = 'ACTIVATE_CARD'  
   AND STATUS = 'BANK_PROCESSING'  
   AND (UPPER(TRIM(CARD_DISPLAY)) LIKE UPPER(TRIM('%XYZNOTFOUND%'))  
   OR UPPER(TRIM(CARD_HOLDER_NAME)) LIKE UPPER(TRIM('%XYZNOTFOUND%')))  
   AND CREATED_DATE >= '2026-04-11 00:00:00'  
   AND CREATED_DATE <= '2026-04-12 23:59:59'  
   AND CREATED_BY = '1578490makernotexist'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi truyền page.pageNum vượt quá tổng số trang

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [],  
   "total": 25  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 100;
   
### Kiểm tra response khi sắp xếp theo createdDate ASC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006500",  
   "createdDate": "2025-04-13T07:00:00",  
   "status": "SUCCESS",  
   "requestType": "ACTIVATE_CARD",  
   "cardDisplay": "406220******5000",  
   "cardHolderName": "TRAN VAN O",  
   "createdBy": "1578490maker19",  
   "updatedDate": "2025-04-13T07:01:00",  
   "acceptedDate": "2025-04-13T07:00:59",  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": null  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CREATED_DATE ASC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo createdDate DESC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CREATED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo createdBy DESC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CREATED_BY DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo createdBy ASC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CREATED_BY ASC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo APPROVED_DATE DESC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY APPROVED_DATE DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo APPROVED_DATE ASC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY APPROVED_DATE ASC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo STATUS  DESC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY STATUS  DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo STATUS ASC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY STATUS ASC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo CARD_ACTION_TYPE  DESC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CARD_ACTION_TYPE  DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo CARD_ACTION_TYPE ASC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CARD_ACTION_TYPE ASC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo CARD_DISPLAY  DESC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CARD_DISPLAY  DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo CARD_DISPLAY ASC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CARD_DISPLAY ASC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo CARD_HOLDER_NAME  DESC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CARD_HOLDER_NAME  DESC  
   LIMIT 10 OFFSET 0;
   
### Kiểm tra response khi sắp xếp theo CARD_HOLDER_NAME  ASC

1. Check api trả về:  
   1.1. Status: 200  
   1.2. Response:  
   {  
   "status": 0,  
   "code": "0",  
   "message": "SUCCESS",  
   "traceId": "68c27c6f9f444316cc20f8c2d1481942",  
   "data": {  
   "items": [  
   {  
   "id": "CD2125110700006501",  
   "createdDate": "2026-04-12T17:59:00",  
   "status": "PENDING_APPROVAL",  
   "requestType": "CHANGE_PRIMARY_LINKED_ACCOUNT",  
   "cardDisplay": "406220******5001",  
   "cardHolderName": "LE VAN P",  
   "createdBy": "1578490maker20",  
   "updatedDate": "2026-04-12T17:59:00",  
   "acceptedDate": null,  
   "transAmount": null,  
   "ccy": null,  
   "accountNo": "22334455660"  
   }  
   ],  
   "total": 20  
   }  
   }  
   SQL:  
   SELECT ID, CARD_DISPLAY, CARD_HOLDER_NAME, STATUS, CARD_ACTION_TYPE, CREATED_BY, CREATED_DATE, UPDATED_DATE, ACCEPTED_DATE, TRANS_AMOUNT, CCY, ACCOUNT_NO  
   FROM TXN_CARD_REQUEST  
   WHERE CIF_NO = 'CIF001'  
   ORDER BY CARD_HOLDER_NAME ASC  
   LIMIT 10 OFFSET 0;
   
## Kiểm tra ngoại lệ

### Kiểm tra trường hợp request timeout

- Status: 504
  
### Kiểm tra trường hợp server trả về lỗi 500

- Status: 500
  
