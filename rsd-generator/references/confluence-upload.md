# Confluence Upload — Storage Format (XHTML)

## Cách chính: MCP với content_format="storage"

Toàn bộ nội dung RSD viết bằng **Confluence Storage Format** (XHTML + ac: macros), upload qua MCP. Full-width được đảm bảo bằng **2 cơ chế trong content** — không phụ thuộc vào page_width setting:

1. **`data-layout="full-width"` trên mọi `<table>`** — thiếu attribute này table sẽ hẹp
2. **Outer `<ac:layout>` bao toàn bộ page** — tables ngoài layout wrapper render hẹp hơn

### Tạo page mới

```
mcp__mcp-atlassian__confluence_create_page(
    space_key="<SPACE_KEY>",           # ví dụ: "CGAAA", "AIT"
    title="<TITLE>",                    # ví dụ: "[WEB] 2.1. Danh sách thẻ tín dụng nội địa_Skymap"
    content="<nội dung storage format>", # XHTML + Confluence macros
    content_format="storage",
    parent_id="<PARENT_PAGE_ID>",       # ID của page cha (số nguyên dạng string)
)
```

Trả về: `page_id` và `url` của page vừa tạo.

### Update page đã có

```
mcp__mcp-atlassian__confluence_update_page(
    page_id="<PAGE_ID>",
    title="<TITLE>",
    content="<nội dung storage format mới>",
    content_format="storage",
    version_comment="Cập nhật nội dung RSD"
)
```

**Lưu ý**: `confluence_update_page` không hỗ trợ tham số `page_width` — đừng truyền vào. Full-width đã được đảm bảo bằng `data-layout="full-width"` trong content.

### Attach ảnh sau khi tạo page

Gom tất cả ảnh từ mọi nguồn (Figma, user paste, Jira download) vào `/tmp/rsd-screenshots/` rồi upload 1 lần:

```bash
mkdir -p /tmp/rsd-screenshots
cp <source>/*.png /tmp/rsd-screenshots/
```

```
mcp__mcp-atlassian__confluence_upload_attachments(
    content_id="<PAGE_ID>",
    file_paths="/tmp/rsd-screenshots/screen-01-default.png,/tmp/rsd-screenshots/screen-02-empty.png,..."
)
```

**Lưu ý**: Tránh path có khoảng trắng — MCP sẽ không tìm thấy file. Trên Windows với Git Bash, nếu `/tmp/` không hoạt động với MCP, thử path tuyệt đối Windows (ví dụ `d:/tmp/rsd-screenshots/`).

Sau khi attach thành công, ảnh được chèn trong storage content bằng `<ac:image ac:width="360"><ri:attachment ri:filename="screen-01-default.png"/></ac:image>`.

### Lấy ảnh từ conversation

Không giả định format — kiểm tra thực tế và xử lý theo những gì nhận được:

```bash
# Local file path:
cp "<path>" "./screenshots/screen-01-default.png"

# Base64 string:
echo "<base64-string>" | base64 -d > "./screenshots/screen-01-default.png"

# URL (attachment URL, CDN link):
curl -L -o "./screenshots/screen-01-default.png" "<url>"
```

Sau khi có file local → upload như bình thường.

Nếu chỉ thấy ảnh inline (không có path/base64/url): chèn `<p><em>(Ảnh: <mô tả nội dung> — cần attach file)</em></p>` trong storage content.

### Lấy ảnh từ Jira issue

```
mcp__mcp-atlassian__jira_download_attachments(
    issue_key="<ISSUE-KEY>",
    download_dir="./screenshots/"
)
```

Upload kết quả download lên Confluence page mới.

---

## Lấy space_key và parent_id

**Không hỏi user nếu có thể tự tìm.** Ưu tiên theo thứ tự:

1. **URL của page cha** → trích trực tiếp:
   - URL: `https://ignify-co.atlassian.net/wiki/spaces/AIT/pages/90505238/...`
   - `space_key` = `AIT`, `parent_id` = `90505238`

2. **User nói tên space** (ví dụ: "space AIT", "board AIT", "root folder của AIT") → tự tìm:
   ```
   mcp__mcp-atlassian__confluence_get_space_page_tree(
       space_key="AIT"
   )
   ```
   → Tìm page có `parent_id = null` → đó là root page → dùng `id` của nó làm `parent_id`.

3. **Chỉ biết tên dự án** → search:
   ```
   mcp__mcp-atlassian__confluence_search(
       query="space = \"<SPACE_KEY>\" AND type = page",
       limit=5
   )
   ```

Chỉ hỏi user khi không có bất kỳ thông tin nào để suy ra.

---

## Title convention (từ sample thật)

| Pattern | Ví dụ |
|---------|-------|
| `[WEB] <số>. <Tên>_<Project>` | `[WEB] 2.1. Danh sách thẻ tín dụng nội địa_Skymap` |
| `[APP] <số>. <Tên>_<Project>` | `[APP] 2.1. Danh sách thẻ tín dụng nội địa_Skymap` |
| `TN_<Tên màn hình>_<Platform>` | `TNĐ_Xem chi tiết_Skymap` |
| `AIT-RSD - <Tên màn hình>` | `AIT-RSD - Chi tiết bộ lọc` |

Hỏi user nếu không chắc convention của dự án.

---

## Kiểm tra sau khi upload

```
mcp__mcp-atlassian__confluence_get_page(
    page_id="<PAGE_ID>",
    convert_to_markdown=false   # xem raw để kiểm tra content
)
```

---

## Fallback: page quá lớn hoặc MCP lỗi

Nếu MCP `create_page` timeout hoặc lỗi vì content quá lớn (>100KB):
1. Tạo page rỗng trước: `create_page` với content = `_Placeholder_`
2. Lấy `page_id` từ response
3. Update content thật: `update_page` với `page_id` vừa lấy
