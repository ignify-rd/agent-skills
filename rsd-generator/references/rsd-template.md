# RSD Template (skeleton) — copy & fill

Đây là skeleton đầy đủ 7 phần của 1 page RSD. Copy toàn bộ, rồi điền dữ liệu từ URD/Figma. Giữ nguyên heading và các label trong bảng (tiếng Việt, có dấu) vì người review quen với wording này.

---

**Phiên bản tài liệu**

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Version** | **Lý do** | **Date** | **Người sửa** | **Mô tả** |
| 1.0 | Thêm mới | {{YYYY-MM-DD}} | {{Tác giả}} | Dự thảo |

**Mục lục**

none

1. Đặc tả/Tóm tắt usecase
---------------------------

### 1.1. Sơ đồ Usecase (nếu có)

Tham chiếu tại {{link RSD cấp 1 — section sơ đồ use case}}

### 1.2. Đặc tả/tóm tắt Usecase

|  |  |
| --- | --- |
| **Tên** | {{Tên usecase, ví dụ: Danh sách thẻ tín dụng nội địa}} |
| **Mã** | {{để trống nếu chưa có}} |
| **Mô tả** | {{1-2 câu mô tả ngắn gọn mục đích}} |
| **Tác nhân** | Tác nhân chủ động: {{vai trò user}}  Tác nhân thụ động: {{các hệ thống backend liên quan}} |
| **Mức độ ưu tiên** | High / **Medium** / Low |
| **Điều kiện kích hoạt** | {{Khi nào user kích hoạt chức năng này}} |
| **Điều kiện trước** | 1. User đăng nhập thành công 2. User được phân quyền ... |
| **Kết quả mong muốn** | {{Hệ thống hiển thị / xử lý gì}} |
| **Luồng chính** | {{Bước 1...2...3...}} |
| **Luồng thay thế** | N/A hoặc mô tả |
| **Luồng ngoại lệ** | 1. ... 2. ... |
| **Quy tắc nghiệp vụ (nếu có)** | {{Rules business phải tuân — phân quyền dữ liệu, logic trạng thái...}} |
| **Yêu cầu phi chức năng (nếu có)** | Theo yêu cầu phi chức năng chung tại RSD cấp 1 |

2. Sơ đồ luồng xử lý
--------------------

### 2.1. Sơ đồ luồng xử lý

{{Chèn sơ đồ nếu có; nếu không, để trống và note "Sẽ bổ sung"}}

### 2.2. Yêu cầu với các kết nối phát sinh mới/ cần chỉnh sửa trong luồng

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| **Bước** | **Tên kết nối** | **Trạng thái sẵn sàng** | **Backend cung cấp kết nối** | **Phương thức tích hợp** | **Luồng gọi API** | **Mô tả kết nối** |
| {{Mô tả bước}} | {{Tên API}} | Có sẵn / Phát sinh mới / Cần chỉnh sửa | {{Module backend}} | API / DBlink / Job | {{Client → Server → Core}} | {{Endpoint + chức năng}} |

### 2.3. Danh mục hoặc sơ đồ trạng thái

#### 2.3.1. {{Tên đối tượng, ví dụ: Trạng thái của thẻ}}

Theo mô tả tại: {{link bảng trạng thái chung}}

3. Ma trận phân quyền và phân bổ chức năng
------------------------------------------

Mô tả tính năng phân bổ ở các FO/BO/iconnect và phân quyền người dùng (khởi tạo, sửa, xác nhận, duyệt).

| **STT** | **Usecase (chức năng cấp 3)** | **MB** | **IB** | **BO** | **ERP (web/app)** | **ERP (H2H)** | **Maker-KH** | **Checker-KH** | **Inquiry-KH** | **Admin-KH** | **GDV CN** | **KSV CN** | **GDV TSC** | **KSV TSC** | **Inquiry-BO** | **Nhóm quyền khác** | **Mô tả** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **{{Tên nhóm chức năng}}** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 1.1 | {{Chức năng cấp 3}} | x | x |  |  |  | x | x | x | x |  |  |  |  |  |  | {{Ghi chú phân giao}} |

*(Nếu là RSD APP có RSD WEB tương ứng, thay toàn bộ bảng bằng: "Tham chiếu tại {{link RSD WEB}}#3.-Ma-tr%E1%BA%ADn-ph%C3%A2n-quy%E1%BB%81n")*

4**. Mô tả màn hình**
---------------------

Figma: {{link figma}}

**a. Mockup màn hình**

Đường dẫn: {{Cách truy cập chức năng, ví dụ: Menu Thẻ > Danh sách thẻ > tab ...}}

{{Caption state 1, ví dụ: Màn hình danh sách khi có dữ liệu}}

![screenshot-1.png](screenshot-1.png)

{{Caption state 2}}

![screenshot-2.png](screenshot-2.png)

{{... lặp lại cho từng state cần mô tả: default / advanced search mở / empty / error / loading / hover / các variant dropdown ...}}

**b. Mô tả màn hình**

|  | **Hạng mục** | **Kiểu hiển thị** | **Kiểu thao tác** | **Bắt buộc** | **Độ dài** | **Mô tả** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Cụm thông tin đầu trang** |  |  |  |  |  |
| 2 | {{Element}} | Label / Button / Textbox / Droplist / Image / Tab ... | Read-only / Click / Input / Select | Y / N / - | {{max length hoặc "-"}} | {{Placeholder + mặc định + validate + logic + ẩn/hiện + enable/disable}} |
| 3 | **Cụm tìm kiếm / Cụm danh sách / ...** |  |  |  |  |  |
| ... |  |  |  |  |  |  |

5. Logic xử lý {{tên action chính, ví dụ: khi truy cập menu Thẻ > Danh sách thẻ > tab Thẻ tín dụng nội địa}}
------------------------------------------------------------------------------------------------------------

| **Thao tác** | **Tác nhân** | **Mô tả** |
| --- | --- | --- |
| {{Trigger user, ví dụ: User chọn tab Thẻ tín dụng nội địa}} | Client web/app | **1/ Gửi yêu cầu lấy danh sách ... qua API ...** Endpoint: {{...}} Payload: {{...}} |
|  | Server {{Module}} | **1/ Kiểm tra tính hợp lệ input** - Không hợp lệ: trả lỗi INPUT_01 - Hết phiên: SESSION_TIMEOUT_01 - Hợp lệ: chuyển bước 2  **2/ Kiểm tra phân quyền** ...  **3/ ...** |
|  | Client web/app | **Nhận phản hồi** - Lỗi phân quyền CARD.003: hiển thị popup "Người dùng chưa được phân quyền..." - Thành công: hiển thị danh sách theo mô tả màn hình |

---

## ⚠️ Các điểm cần user xác nhận trước khi chính thức hoá

- [ ] {{Ghi rõ từng [Cần xác nhận] đã đánh dấu ở trên, kèm section reference}}
