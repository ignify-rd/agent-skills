# Quy tắc chất lượng cho sinh Test Design

Các quy tắc này PHẢI được áp dụng cho MỌI test case được sinh ra. Được trích xuất từ
các tiêu chuẩn QA đã được kiểm chứng trong các đội QA ngân hàng/tài chính Việt Nam.

## Quy tắc ngôn ngữ

- Output 100% tiếng Việt
- KHÔNG BAO GIỜ dịch tên field/button sang tiếng Anh
- Giữ nguyên tên chính xác như trong RSD/PTTK

## Văn phong — Ngắn gọn, văn nói

- **Name**: TỐI ĐA 40 ký tự. Ví dụ: "Nhập < 12 ký tự", "Bỏ trống", "Nhập 50 ký tự"
- **Steps**: 1 câu ngắn, không chủ ngữ. Ví dụ: "Nhập 11 ký tự số", "Click Hoàn tất"
- **Expected**: 1 câu. Ví dụ: "Cho phép nhập", "Hiển thị lỗi: ..."
- **Định dạng PreConditions**:
  ```
  Đ/k1: Vào màn hình:
  1. Đăng nhập [App]
  2. Tại [màn hình]
  Đ/k2: Phân quyền:
  1. Người dùng được phân quyền = [Role]
  ```
- **Test Data**: "N/A" hoặc giá trị cụ thể như "11111111111 (11 ký tự)"
- **KHÔNG dùng**: "thực hiện", "tiến hành", "người dùng", "ví dụ:"

## Giá trị cụ thể — CRITICAL

- testSteps và testData PHẢI có giá trị CỤ THỂ từ RSD hoặc Custom Instructions
- KHÔNG dùng: "giá trị test", "[value]", "abc...", "[placeholder]"
- Extract từ RSD: tên màn hình, tên field, test data, error messages
- Nếu Custom Instructions có test data → ưu tiên dùng
- Nếu không có data → dùng data hợp lý (user@bidv.vn, 0912345678, HoaLT2)
- Test permission/UI có thể không cần test data cụ thể → "N/A" chấp nhận được

## Boundary Testing — BẮT BUỘC với mọi constraint có giá trị cụ thể

**Khi RSD/PTTK định nghĩa giới hạn số N → PHẢI test đủ 3 case: N-1, N, N+1.**
KHÔNG được viết chung chung "nhập quá N" mà không có case cụ thể.

| Loại constraint | Cách test |
|---|---|
| maxLength = N | Nhập N-1 ký tự → ok / Nhập N ký tự → ok / Nhập N+1 ký tự → lỗi |
| minLength = N | Nhập N-1 ký tự → lỗi / Nhập N ký tự → ok |
| maxValue = N | Nhập N-1 → ok / Nhập N → ok / Nhập N+1 → lỗi |
| minValue = N | Nhập N+1 → ok / Nhập N → ok / Nhập N-1 → lỗi |
| maxDecimalPlaces = N | Nhập N-1 chữ số thập phân → ok / Nhập N → ok / Nhập N+1 → lỗi |
| maxRange (date range) = N ngày | Chọn N-1 ngày → ok / Chọn N ngày → ok / Chọn N+1 ngày → lỗi |

**Ví dụ — maxDecimalPlaces = 2:**

SAI: `"Kiểm tra khi nhập quá 2 chữ số thập phân → Hệ thống chặn"` (chung chung, không có giá trị thực)
SAI: `"Kiểm tra khi nhập 1 chữ số thập phân → ok"` (vẫn chung chung, không có số cụ thể)
ĐÚNG:
- `"Kiểm tra khi nhập 1.5 → Hệ thống cho phép nhập"`
- `"Kiểm tra khi nhập 1.55 → Hệ thống cho phép nhập"`
- `"Kiểm tra khi nhập 1.555 → Hệ thống chặn không cho nhập quá 2 chữ số thập phân"`

**Ví dụ — maxLength = 100:**

SAI: `"Kiểm tra khi nhập quá 100 ký tự → Hệ thống chặn"`
ĐÚNG:
- `"Kiểm tra khi nhập 99 ký tự → Hệ thống cho phép nhập"`
- `"Kiểm tra khi nhập 100 ký tự → Hệ thống cho phép nhập"`
- `"Kiểm tra khi nhập 101 ký tự → Hiển thị cảnh báo ..."`

## Atomic Test Cases — 1 Test = 1 Kiểm tra

- MỖI test case CHỈ kiểm tra 1 thứ
- TÁCH: Mỗi field/tag/button/validation rule = 1 test case riêng
- KHÔNG gộp nhiều điều kiện vào 1 test case

## Cụm từ bị cấm — CẤM TUYỆT ĐỐI

Các cụm từ này BỊ CẤM trong TẤT CẢ các trường của test case (name, testSteps, testData, expectedResult, preConditions, screen, field, role, sourceDetail, TẤT CẢ giá trị khác):

### Danh sách từ/cụm từ bị cấm:
- "và/hoặc"
- "hoặc"
- "hay"
- "có thể"
- "nên"
- "thường"
- "nếu có"
- "(nếu có)"
- "kèm theo"
- "tương tự"
- "hoặc tương tự"
- "ví dụ:"
- "(ví dụ: ...)"
- "[placeholder]"
- "[value]"
- "..."
- "tương ứng"
- "phù hợp"
- "X hoặc Y"
- "A và/hoặc B"

### Ví dụ sai:
- "Hiển thị thông báo X và/hoặc hình ảnh Y" → SAI
- "Click button Lưu hoặc Hoàn tất" → SAI
- "Nhập giá trị hợp lệ (ví dụ: abc123)" → SAI
- "Hiển thị lỗi tương ứng" → SAI
- "Màn hình A hoặc màn hình B" → SAI

### Ví dụ đúng:
- "Hiển thị thông báo: Lưu thành công" → ĐÚNG (1 giá trị cụ thể)
- "Click button Hoàn tất" → ĐÚNG (1 button cụ thể)
- "Nhập giá trị = \"abc123\"" → ĐÚNG (giá trị cụ thể)
- "Hiển thị lỗi: Vui lòng nhập đủ 12 ký tự" → ĐÚNG (message cụ thể)

## Nguyên tắc vàng

1. KHÔNG CHẮC CHẮN 100% → KHÔNG TẠO TEST CASE ĐÓ
2. Mỗi giá trị PHẢI là 1 giá trị DUY NHẤT, CỤ THỂ
3. KHÔNG đoán, KHÔNG suy luận — chỉ dùng thông tin từ RSD/Image
4. Nếu RSD không đề cập → KHÔNG tạo test case
5. KHÔNG BAO GIỜ viết 2 lựa chọn trong 1 trường

## Bám sát RSD — Nguồn chính, không tự bịa

### Thứ tự ưu tiên:
1. **RSD DOCUMENT (CHÍNH — BẮT BUỘC)**
   - CHỈ tạo test case cho những gì CÓ trong RSD
   - Dùng CHÍNH XÁC tên button/màn hình/message từ RSD
   - Expected Result: Copy message từ RSD, KHÔNG tự bịa

2. **IMAGES (PHỤ — CHỈ BỔ SUNG)**
   - CHỈ dùng khi RSD đề cập feature nhưng thiếu chi tiết
   - KHÔNG được thêm test cases chỉ vì images có mà RSD không đề cập

### TỰ BỊA = XÓA:
- Messages như "Bạn chưa có lịch hẹn nào", "Không có dữ liệu" → Nếu RSD không có → XÓA
- Empty states, error messages → Nếu RSD không đề cập → XÓA
- Features như search/filter/pagination → Nếu RSD không có → KHÔNG tạo

### BLACKLIST — KHÔNG TẠO (trừ khi RSD ghi rõ):
ESC đóng popup, click ngoài, double-click, session timeout, swipe, drag-drop, responsive, refresh, pull-to-refresh

## Ánh xạ màn hình - phần tử — CRITICAL

- MỖI FIELD chỉ thuộc về MỘT màn hình cụ thể
- MỖI BUTTON chỉ thuộc về MỘT màn hình cụ thể
- Test case cho field X PHẢI gán đúng màn hình chứa field X
- KHÔNG ĐƯỢC tạo test case với field của màn hình A nhưng gán cho màn hình B

## Đặt tên field

- SỬ DỤNG ĐÚNG TÊN TRƯỜNG TỪ RSD, không tự đặt tên khác
- Nếu RSD ghi "Số tiền vay dự kiến" → dùng đúng "Số tiền vay dự kiến"
- PHÂN BIỆT: Textbox (có thể nhập) vs Read-only (chỉ đọc)

## Định nghĩa Priority

- **High**: Validate bắt buộc, business rules chính, Security (SQL/XSS)
- **Medium**: Validate format, boundary values, UI state
- **Low**: Field tùy chọn, edge cases hiếm gặp
