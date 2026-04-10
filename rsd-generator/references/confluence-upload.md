# Confluence Upload — Wiki Format (recommended)

## Cách chính: MCP với content_format="wiki"

Toàn bộ nội dung RSD viết bằng Confluence Wiki Markup, upload trực tiếp qua MCP — không cần script Python, không cần convert.

### Tạo page mới

```
mcp__mcp-atlassian__confluence_create_page(
    space_key="<SPACE_KEY>",         # ví dụ: "CGAAA", "AIT"
    title="<TITLE>",                  # ví dụ: "WEB 2.1. Danh sách thẻ tín dụng nội địa_Skymap"
    content="<nội dung wiki markup>", # toàn bộ nội dung từ rsd-template.md
    content_format="wiki",
    parent_id="<PARENT_PAGE_ID>"      # ID của page cha (số nguyên dạng string)
)
```

Trả về: `page_id` và `url` của page vừa tạo.

### Update page đã có

```
mcp__mcp-atlassian__confluence_update_page(
    page_id="<PAGE_ID>",
    title="<TITLE>",
    content="<nội dung wiki markup mới>",
    content_format="wiki",
    version_comment="Cập nhật nội dung RSD"
)
```

### Attach ảnh sau khi tạo page

Gom tất cả ảnh từ mọi nguồn (Figma, user paste, Jira download) vào 1 thư mục rồi upload 1 lần:

```
mcp__mcp-atlassian__confluence_upload_attachments(
    content_id="<PAGE_ID>",
    file_paths="./screenshots/screen-01-default.png,./screenshots/screen-02-empty.png,..."
)
```

Sau khi attach thành công, ảnh được chèn trong wiki content bằng `!screen-01-default.png!`.

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

Nếu chỉ thấy ảnh inline (không có path/base64/url): chèn `_(Ảnh: <mô tả nội dung> — cần attach file)_` trong wiki content.

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

Nếu chỉ có URL của page cha, trích `parent_id` từ URL:
- URL: `https://ignify-co.atlassian.net/wiki/spaces/AIT/pages/90505238/...`
- `space_key` = `AIT`
- `parent_id` = `90505238`

Nếu cần tìm space:
```
mcp__mcp-atlassian__confluence_search(
    query="space = \"<SPACE_KEY>\" AND type = page",
    limit=1
)
```

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
