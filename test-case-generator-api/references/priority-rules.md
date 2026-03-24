# Quy tắc ưu tiên nguồn dữ liệu (RSD vs PTTK)

## Bảng ưu tiên

| Có PTTK? | Nguồn cho field definitions / request / response | Nguồn cho business logic |
|-----------|--------------------------------------------------|--------------------------|
| **Có** | **CHỈ dùng PTTK** — BỎ QUA field definitions, request body, response body trong RSD | RSD |
| **Không** | RSD (fallback) | RSD |

## Chi tiết

### PTTK ưu tiên cho (khi có PTTK):
- Tên field (giữ nguyên tên gốc từ PTTK)
- Kiểu dữ liệu (Date, Integer, Long, String — chính xác từ PTTK)
- Required/Optional
- maxLength, format constraints (dd/MM/yyyy, etc.)
- Request body structure
- Response body structure (tên trường, kiểu dữ liệu, nesting)
- API endpoints
- DB mappings, enum values

### RSD ưu tiên cho (luôn luôn):
- Business logic, luồng chính
- Error codes, error messages
- DB mapping logic (conditions, orderBy)
- If/else branches, conditional fields
- Mode variations (create/update/delete)
- Status transitions
- Screen flow, permissions

### BỎ QUA trong RSD (khi có PTTK):
- Mọi phần định nghĩa fields (tên, kiểu, required...)
- Request body structure
- Response body structure

## Lưu ý quan trọng

- PTTK thường là file lớn hơn và chứa nhiều API/screen khác nhau
- Luôn tìm ĐÚNG API/screen theo endpoint hoặc tên trước khi trích xuất
- Khi có conflict giữa PTTK và RSD về field definitions → PTTK thắng
- Khi có conflict về business logic → RSD thắng
