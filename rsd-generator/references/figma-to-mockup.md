# Figma → Mockup + Bảng mô tả màn hình

Section 4 của RSD ("Mô tả màn hình") là phần duy nhất không thể tham chiếu — luôn phải viết tay theo Figma. Đây là hướng dẫn.

**Format**: tất cả output Section 4 viết bằng **Confluence Wiki Markup** — dùng `||` cho header bảng, `|cell|` cho data, `*bold*` cho in đậm, `\\` để xuống dòng trong cell.

## Pipeline

```
Figma input  ─┐
              ├─► a. Mockup (caption + !ảnh!)
              │
              └─► b. Bảng mô tả màn hình (từng element)
```

## Trích ảnh Figma

Có 2 nguồn:

### (1) Link Figma (figma.com/design/...)

- Parse URL: `figma.com/design/{fileKey}/{name}?node-id={nodeId}` — convert `-` thành `:` trong nodeId.
- Dùng `mcp__plugin_figma_figma__get_screenshot` với `fileKey` + `nodeId` cho **từng state cần mô tả** (ví dụ: default, empty, dropdown opened, error, loading...). **Không** lấy node cha chứa tất cả state — quá to, khó dùng.
- Lưu các ảnh về thư mục workspace (ví dụ `./screenshots/screen-01.png`). Ảnh này sẽ được attach lên page Confluence khi upload.
- Dùng `mcp__plugin_figma_figma__get_design_context` để lấy mô tả element-level (tên layer, props) — giúp viết cột "Hạng mục" và "Mô tả" trong bảng 4b.

### (2) Ảnh đã đính kèm trên Confluence page khác

- Nếu URD hoặc RSD tham chiếu đã có ảnh, có thể download về local rồi attach lại vào page mới để ảnh không bị mất khi page nguồn bị xoá. Dùng `mcp__mcp-atlassian__confluence_download_content_attachments`.

## Cách xác định "các state cần mô tả"

Quan sát Figma frame list / các artboard. RSD sample điển hình có các state sau:

1. **Default (có dữ liệu)** — state cơ bản khi load thành công
2. **Empty state** — khi API trả rỗng (khi vào từ menu)
3. **Empty search state** — khi tìm kiếm không có kết quả
4. **Advanced search opened** — form tìm kiếm nâng cao mở rộng
5. **Search with results** — sau khi nhấn Áp dụng
6. **Input states** — các textbox đang có giá trị
7. **Dropdown opened** — các droplist khi user click
8. **Loading / error / no connection** — nếu Figma có
9. **Missing assets** — ví dụ "không có phôi thẻ"
10. **Hover / tooltip** — nếu có thao tác hover

## Caption mockup — phong cách

Caption ngắn, mô tả chính xác **trạng thái** của ảnh, viết **trên** ảnh. Không dùng emoji. Ví dụ:

- "Màn hình danh sách khi có dữ liệu"
- "Màn hình danh sách khi nhấn button Tìm kiếm nâng cao"
- "Màn hình danh sách Kết quả tìm kiếm nâng cao khi có dữ liệu"
- "Màn hình danh sách Kết quả tìm kiếm nâng cao khi không có dữ liệu"
- "Khi nhập tìm Số thẻ"
- "Khi nhấn chọn droplist Trạng thái"

## Format wiki cho Section 4a — Mockup

Ảnh mockup **bắt buộc** hiển thị dạng lưới cột dùng `{section}/{column}`. Số cột theo platform (dựa trên Confluence mẫu thực tế):

| Platform | Số cột | Width mỗi cột | Image width |
|----------|--------|---------------|-------------|
| APP | 4 cột | `width=25%` | `width=200` |
| WEB | 3 cột | `width=33%` | `width=360` |
| Dialog / Detail | 2 cột | `width=50%` | `width=500` |

Ví dụ WEB (3 cột):

```wiki
{section}
{column:width=33%}
Caption mô tả state 1 (text thuần, không emoji)

!screen-01-default.png|width=360!

Caption mô tả state 2

!screen-02-empty.png|width=360!
{column}
{column:width=33%}
Caption mô tả state 3

!screen-03-search.png|width=360!

Caption mô tả state 4

_(Ảnh: chưa có - cần bổ sung)_
{column}
{column:width=33%}
Caption mô tả state 5

_(Ảnh: chưa có - cần bổ sung)_
{column}
{section}
```

Ví dụ APP (4 cột): thay `width=33%` → `width=25%`, `width=360` → `width=200`.

Nếu số state ít hơn số cột: cột trống để `{column:width=33%}{column}`.

Nếu nhiều hơn 6 state (WEB) hoặc 8 state (APP): thêm `{section}` thứ 2 bên dưới.

## Bảng mô tả màn hình (4b) — format wiki

**Cấu trúc header** (cột đầu phải rỗng `|| ||`):

```wiki
|| ||*Hạng mục*||*Kiểu hiển thị*||*Kiểu thao tác*||*Bắt buộc*||*Độ dài*||*Mô tả*||
```

**Row group header** (in đậm, các cột khác trống):

```wiki
|1|*Cụm thông tin đầu trang*| | | | | |
```

**Row element thường**:

```wiki
|2|Breadcrumb|Label|Read-only|-|-|Hiển thị đường dẫn Menu > Danh sách thẻ > tab. Luôn hiện.|
```

**Phân nhóm thường gặp:**

```wiki
|| ||*Hạng mục*||*Kiểu hiển thị*||*Kiểu thao tác*||*Bắt buộc*||*Độ dài*||*Mô tả*||
|1|*Cụm thông tin đầu trang*| | | | | |
|2|Breadcrumb|Label|Read-only|-|-|...|
|3|*Cụm tìm kiếm nhanh*| | | | | |
|4|...|...|...|...|...|...|
|5|*Danh sách*| | | | | |
|6|...|...|...|...|...|...|
|7|*Phân trang*| | | | | |
|8|...|...|...|...|...|...|
```

**Với mỗi element (row thường)**, các cột cần điền:

||Cột||Cách xác định||
|Kiểu hiển thị|Label, Button, Textbox, Droplist, Image, Tab, Icon, Link&Label, Radio, Checkbox, Toggle, Card...|
|Kiểu thao tác|Read-only, Click, Input, Select, Input/Paste, Hover, Drag, Scroll|
|Bắt buộc|Y / N / "-" (dùng "-" cho element không cần validation như label)|
|Độ dài|Max length cho input (số), hoặc "-" cho element không có khái niệm length|
|Mô tả|Cột dày nhất — xem checklist bên dưới|

**Checklist nội dung cột "Mô tả"** (điền trong 1 cell, xuống dòng bằng `\\`):

- Placeholder khi chưa có giá trị
- Mặc định (default value, hoặc "Rỗng")
- Validate rules (ký tự cho phép, min/max length, format)
- Logic tương tác: onFocus, onBlur, onEnter, onChange, onClick, clear button behavior
- Nguồn dữ liệu (hardcode / API trả về tên field nào / user nhập)
- Ẩn/hiện (luôn hiện, hiện khi nào)
- Enable/Disable (mặc định + điều kiện)
- Logic nghiệp vụ (ví dụ "khi chọn tab X, gọi API Y")

## Ví dụ cell "Mô tả" chất lượng cao (wiki)

```wiki
|7|Số thẻ|Textbox|Input|N|6|Khi chưa có dữ liệu, hiển thị placeholder: "Số thẻ (6 số đầu hoặc 4 số cuối thẻ)". Mặc định: Rỗng. \\ *Validate*: Chỉ cho phép nhập số, tối đa 6 ký tự. \\ *Logic*: Tìm gần đúng theo 6 số đầu hoặc 4 số cuối. Nút X xuất hiện khi focus / có giá trị; outfocus/enter giữ nguyên kết quả; chặn nhập vượt 6 ký tự. \\ *Giá trị hiển thị*: User tự nhập. \\ *Ẩn/hiện*: Luôn hiện. *Mặc định*: Enable.|
```

## Khi Figma không cho biết điều gì đó

Nếu Figma chỉ có visual, không có annotation về validate/logic/API → **đừng bịa**. Điền `Chờ xác nhận từ BA` vào đúng cell đó trong bảng, ghi lại nội bộ để báo cáo cho user trong chat reply sau khi upload. KHÔNG ghi `[Cần xác nhận]` hay comment dạng annotation trong document.
