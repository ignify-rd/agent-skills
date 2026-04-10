# Figma → Mockup + Bảng mô tả màn hình

Section 4 của RSD ("Mô tả màn hình") là phần duy nhất không thể tham chiếu — luôn phải viết tay theo Figma. Đây là hướng dẫn.

## Pipeline

```
Figma input  ─┐
              ├─► a. Mockup (list caption + ảnh)
              │
              └─► b. Bảng mô tả màn hình (từng element)
```

## Trích ảnh Figma

Có 2 nguồn:

### (1) Link Figma (figma.com/design/...)

- Parse URL: `figma.com/design/{fileKey}/{name}?node-id={nodeId}` — convert `-` thành `:` trong nodeId.
- Dùng `mcp__plugin_figma_figma__get_screenshot` với `fileKey` + `nodeId` cho **từng state cần mô tả** (ví dụ: default, empty, dropdown opened, error, loading...). **Không** lấy node cha chứa tất cả state — quá to, khó dùng.
- Lưu các ảnh về thư mục workspace (ví dụ `./rsd-draft/screenshots/screen-01.png`). Ảnh này sẽ được attach lên page Confluence khi upload.
- Dùng `mcp__plugin_figma_figma__get_design_context` để lấy mô tả element-level (tên layer, props) — giúp viết cột "Hạng mục" và "Mô tả" trong bảng 4b.

### (2) Ảnh đã đính kèm trên Confluence page khác

- Nếu URD hoặc RSD tham chiếu đã có ảnh, có thể dùng lại URL attachment dạng `https://<domain>/wiki/download/attachments/{pageId}/{filename}`.
- Nhưng cách tốt hơn là download ảnh về local rồi attach lại vào page mới, để ảnh không bị mất khi page nguồn bị xoá. Dùng `mcp__mcp-atlassian__confluence_download_content_attachments` hoặc script.

## Cách xác định "các state cần mô tả"

Quan sát Figma frame list / các artboard. RSD sample điển hình có các state sau (không nhất thiết đủ hết, nhưng đây là checklist):

1. **Default (có dữ liệu)** — state cơ bản khi load thành công
2. **Empty state** — khi API trả rỗng (khi vào từ menu)
3. **Empty search state** — khi tìm kiếm không có kết quả
4. **Advanced search opened** — form tìm kiếm nâng cao mở rộng
5. **Search with results** — sau khi nhấn Áp dụng
6. **Input states** — các textbox đang có giá trị (nhập số thẻ, nhập tên)
7. **Dropdown opened** — các droplist khi user click
8. **Loading / error / no connection** — nếu Figma có
9. **Missing assets** — ví dụ "không có phôi thẻ"
10. **Hover / tooltip** — nếu có thao tác hover

## Caption mockup — phong cách

Caption ngắn, mô tả chính xác **trạng thái** của ảnh, viết **trên** ảnh. Ví dụ (lấy từ sample thật):

- "Màn hình danh sách khi có dữ liệu"
- "Màn hình danh sách khi nhấn button Tìm kiếm nâng cao"
- "Màn hình danh sách Kết quả tìm kiếm nâng cao khi có dữ liệu"
- "Màn hình danh sách Kết quả tìm kiếm nâng cao khi không có dữ liệu"
- "Khi nhập tìm Số thẻ"
- "Khi nhấn chọn droplist Trạng thái"
- "Màn hình sách thẻ khi không có phôi thẻ (chưa khai báo/vấn tin API không được)"

## Bảng mô tả màn hình (4b) — cách điền

**Phân nhóm bằng row header in đậm** (cột Hạng mục in đậm, các cột khác để trống):

| | Hạng mục | Kiểu hiển thị | ... |
| --- | --- | --- | --- |
| 1 | **Cụm thông tin đầu trang** | | |
| 2 | Breadcrumb | Label&Hyperlink | ... |

Các cụm thường gặp:
- Cụm thông tin đầu trang (breadcrumb, tên màn hình, tab)
- Cụm tìm kiếm nhanh / nâng cao
- Cụm danh sách (grid/list items)
- Phân trang
- Cụm action bar
- Bottom sheet / Modal / Popup (nếu có)

**Với mỗi element (row thường)**, các cột cần điền:

| Cột | Cách xác định |
| --- | --- |
| **Kiểu hiển thị** | Label, Button, Textbox, Droplist, Image, Tab, Icon, Link&Label, Dropdown secondary, Radio, Checkbox, Toggle, Card... (bằng tiếng Việt có dấu đúng như sample) |
| **Kiểu thao tác** | Read-only, Click, Input, Select, Input/Paste, Hover, Drag, Scroll |
| **Bắt buộc** | Y / N / "-" (dùng "-" cho element không cần validation như label) |
| **Độ dài** | Max length cho input (số), hoặc "-" cho những element không có khái niệm length |
| **Mô tả** | Là cột dày nhất. Phải trả lời các câu sau (nếu applicable): |

**Checklist nội dung cột "Mô tả":**

- [ ] **Placeholder** khi chưa có giá trị
- [ ] **Mặc định** (default value, hoặc "Rỗng")
- [ ] **Validate rules** (ký tự cho phép, min/max length, format)
- [ ] **Logic tương tác**: onFocus, onBlur, onEnter, onChange, onClick, clear button behavior
- [ ] **Nguồn dữ liệu** (hardcode / API trả về tên field nào / user nhập)
- [ ] **Ẩn/hiện** (luôn hiện, hiện khi nào)
- [ ] **Enable/Disable** (mặc định + điều kiện)
- [ ] **Logic nghiệp vụ** (ví dụ "khi chọn tab X, gọi API Y với payload Z")
- [ ] **Link sang section khác** khi hành vi phức tạp (ví dụ "Xem chi tiết logic tại Section 5")

## Ví dụ cell "Mô tả" chất lượng cao

> Khi chưa có dữ liệu, hiển thị placeholder: "Số thẻ (6 số đầu hoặc 4 số cuối thẻ)". Mặc định: Rỗng.
> **Validate**: Chỉ cho phép nhập số, tối đa 6 ký tự. Không cho phép nhập ký tự không phải số.
> **Logic**:
> - Tìm gần đúng theo 6 số đầu hoặc 4 số cuối.
> - Hỗ trợ xóa nhanh bằng nút X: X xuất hiện ở cuối textbox khi (a) user focus vào textbox đã có giá trị, (b) user nhập bất kỳ ký tự nào.
> - Outfocus (blur): giữ nguyên màn hình kết quả, không cập nhật output.
> - User nhấn enter: giữ nguyên màn hình kết quả, không cập nhật output.
> - Tìm kiếm quá số ký tự cho phép: chặn nhập thêm.
> - **Giá trị hiển thị**: Do user tự nhập.
> - **Ẩn/hiện**: Luôn luôn hiện.
> - **Mặc định enable hay disable?** Enable.

## Khi Figma không cho biết điều gì đó

Nếu Figma chỉ có visual, không có annotation về validate/logic/API → **đừng bịa**. Viết `[Cần xác nhận: quy tắc validate cho field X]` và thêm vào checklist cuối page.
