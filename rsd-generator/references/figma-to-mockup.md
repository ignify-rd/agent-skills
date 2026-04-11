# Figma → Mockup + Bảng mô tả màn hình

Section 4 của RSD ("Mô tả màn hình") là phần duy nhất không thể tham chiếu — luôn phải viết tay theo Figma. Đây là hướng dẫn.

**Format**: tất cả output Section 4 viết bằng **Confluence Storage Format** (XHTML) — dùng `<table><tbody><tr><th>` cho header, `<td><p>content</p></td>` cho data, `<strong>` cho in đậm, `<br/>` để xuống dòng trong cell. Section 4a dùng `<ac:layout><ac:layout-section ac:breakout-mode="wide">` cho lưới ảnh wide layout.

## Pipeline

```
Figma input  ─┐
              ├─► a. Mockup (caption <p> + <ac:image>)
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

## Format storage cho Section 4a — Mockup

Ảnh mockup **bắt buộc** hiển thị dạng lưới cột dùng `<ac:layout><ac:layout-section ac:breakout-mode="wide">`. **Cấm** dùng wiki `{section}/{column}`. Số cột theo platform:

| Platform | `ac:type` | Image width |
|----------|-----------|-------------|
| APP | `four_equal` | `ac:width="200"` |
| WEB | `three_equal` | `ac:width="360"` |
| Dialog / Detail | `two_equal` | `ac:width="500"` |

Ví dụ WEB (3 cột — `three_equal`, `ac:breakout-width="1174"`):

```xml
<ac:layout>
<ac:layout-section ac:breakout-mode="wide" ac:breakout-width="1174" ac:type="three_equal">
<ac:layout-cell>
<p>Caption mô tả state 1 (text thuần, không emoji)</p>
<ac:image ac:width="360"><ri:attachment ri:filename="screen-01-default.png"/></ac:image>
<p>Caption mô tả state 2</p>
<ac:image ac:width="360"><ri:attachment ri:filename="screen-02-empty.png"/></ac:image>
</ac:layout-cell>
<ac:layout-cell>
<p>Caption mô tả state 3</p>
<ac:image ac:width="360"><ri:attachment ri:filename="screen-03-search.png"/></ac:image>
<p>Caption mô tả state 4</p>
<p><em>(Ảnh: chưa có - cần bổ sung)</em></p>
</ac:layout-cell>
<ac:layout-cell>
<p>Caption mô tả state 5</p>
<p><em>(Ảnh: chưa có - cần bổ sung)</em></p>
</ac:layout-cell>
</ac:layout-section>
</ac:layout>
```

Ví dụ APP (4 cột): thay `ac:type="three_equal"` → `four_equal`, `ac:width="360"` → `ac:width="200"`.

Nếu số state ít hơn số cột: cell trống để `<ac:layout-cell><p> </p></ac:layout-cell>`.

Nếu nhiều hơn 6 state (WEB) hoặc 8 state (APP): thêm `<ac:layout-section>` thứ 2 bên dưới, cùng trong thẻ `<ac:layout>`.

## Bảng mô tả màn hình (4b) — format storage

**Cấu trúc header** (cột đầu phải rỗng):

```xml
<table><tbody>
<tr>
  <th><p></p></th>
  <th><p><strong>Hạng mục</strong></p></th>
  <th><p><strong>Kiểu hiển thị</strong></p></th>
  <th><p><strong>Kiểu thao tác</strong></p></th>
  <th><p><strong>Bắt buộc</strong></p></th>
  <th><p><strong>Độ dài</strong></p></th>
  <th><p><strong>Mô tả</strong></p></th>
</tr>
```

**Row group header** (in đậm, các cột khác trống):

```xml
<tr>
  <td><p>1</p></td>
  <td><p><strong>Cụm thông tin đầu trang</strong></p></td>
  <td><p></p></td><td><p></p></td><td><p></p></td><td><p></p></td><td><p></p></td>
</tr>
```

**Row element thường**:

```xml
<tr>
  <td><p>2</p></td>
  <td><p>Breadcrumb</p></td>
  <td><p>Label</p></td>
  <td><p>Read-only</p></td>
  <td><p>-</p></td>
  <td><p>-</p></td>
  <td><p>Hiển thị đường dẫn Menu &gt; Danh sách thẻ &gt; tab. Luôn hiện.</p></td>
</tr>
```

**Phân nhóm thường gặp** (shorthand — thực tế dùng XML storage format trên):

```
[header row]
1 | *Cụm thông tin đầu trang* | | | | |
2 | Breadcrumb | Label | Read-only | - | - | ...
3 | *Cụm tìm kiếm nhanh* | | | | |
4 | ... | ... | ... | ... | ... | ...
5 | *Danh sách* | | | | |
6 | ... | ... | ... | ... | ... | ...
7 | *Phân trang* | | | | |
8 | ... | ... | ... | ... | ... | ...
[close table]
```

**Với mỗi element (row thường)**, các cột cần điền:

||Cột||Cách xác định||
|Kiểu hiển thị|Label, Button, Textbox, Droplist, Image, Tab, Icon, Link&Label, Radio, Checkbox, Toggle, Card...|
|Kiểu thao tác|Read-only, Click, Input, Select, Input/Paste, Hover, Drag, Scroll|
|Bắt buộc|Y / N / "-" (dùng "-" cho element không cần validation như label)|
|Độ dài|Max length cho input (số), hoặc "-" cho element không có khái niệm length|
|Mô tả|Cột dày nhất — xem checklist bên dưới|

**Checklist nội dung cột "Mô tả"** (điền trong 1 `<td>`, xuống dòng bằng `<br/>`):

- Placeholder khi chưa có giá trị
- Mặc định (default value, hoặc "Rỗng")
- Validate rules (ký tự cho phép, min/max length, format)
- Logic tương tác: onFocus, onBlur, onEnter, onChange, onClick, clear button behavior
- Nguồn dữ liệu (hardcode / API trả về tên field nào / user nhập)
- Ẩn/hiện (luôn hiện, hiện khi nào)
- Enable/Disable (mặc định + điều kiện)
- Logic nghiệp vụ (ví dụ "khi chọn tab X, gọi API Y")

## Ví dụ cell "Mô tả" chất lượng cao (storage format)

```xml
<tr>
  <td><p>7</p></td>
  <td><p>Số thẻ</p></td>
  <td><p>Textbox</p></td>
  <td><p>Input</p></td>
  <td><p>N</p></td>
  <td><p>6</p></td>
  <td><p>Khi chưa có dữ liệu, hiển thị placeholder: "Số thẻ (6 số đầu hoặc 4 số cuối thẻ)". Mặc định: Rỗng.<br/>
<strong>Validate</strong>: Chỉ cho phép nhập số, tối đa 6 ký tự.<br/>
<strong>Logic</strong>: Tìm gần đúng theo 6 số đầu hoặc 4 số cuối. Nút X xuất hiện khi focus / có giá trị; outfocus/enter giữ nguyên kết quả; chặn nhập vượt 6 ký tự.<br/>
<strong>Giá trị hiển thị</strong>: User tự nhập.<br/>
<strong>Ẩn/hiện</strong>: Luôn hiện. <strong>Mặc định</strong>: Enable.</p></td>
</tr>
```

## Khi Figma không cho biết điều gì đó

Nếu Figma chỉ có visual, không có annotation về validate/logic/API → **đừng bịa**. Điền `Chờ xác nhận từ BA` vào đúng cell đó trong bảng, ghi lại nội bộ để báo cáo cho user trong chat reply sau khi upload. KHÔNG ghi `[Cần xác nhận]` hay comment dạng annotation trong document.
