# Confluence Upload — 2 paths

## Path A: Markdown nhỏ, không ảnh (< ~10KB)

Dùng MCP trực tiếp:

```
mcp__mcp-atlassian__confluence_create_page
  space_key: <SPACE>
  parent_id: <PARENT_PAGE_ID>
  title: "<TITLE>"
  content: <storage format HTML hoặc markdown>
```

Đa số RSD sẽ **lớn hơn 10KB** (bảng mô tả màn hình + logic xử lý rất dày) → không dùng path này. Chỉ dùng cho test nhanh hoặc RSD APP rút gọn toàn tham chiếu.

## Path B: Markdown lớn và/hoặc có ảnh (recommended)

Dùng `confluence-skill` đã cài sẵn:

```bash
python3 ~/.claude/skills/confluence-skill/scripts/upload_confluence_v2.py \
    ./rsd-draft/rsd.md \
    --space <SPACE_KEY> \
    --parent <PARENT_PAGE_ID> \
    --title "<TITLE>"
```

Script tự động:
- Convert markdown → Confluence storage format
- Upload ảnh relative path từ `.md` làm attachment
- Tạo page mới nếu chưa tồn tại, update nếu đã có

Nếu script không hỗ trợ tạo page mới, fallback:

1. Tạo page rỗng qua MCP: `confluence_create_page` với content = `<p>Placeholder</p>` → lấy về `page_id`.
2. Chạy `upload_confluence_v2.py` với `--id <page_id>` để ghi đè nội dung thật.
3. Kiểm tra link page trả về.

## Cấu trúc draft folder

Khi làm 1 RSD, dựng workspace tạm dạng:

```
./rsd-draft-<slug>/
├── rsd.md                  # file markdown chính
└── screenshots/            # ảnh Figma đã download
    ├── 01-default.png
    ├── 02-empty.png
    └── ...
```

Trong `rsd.md`, tham chiếu ảnh relative:

```markdown
![Màn hình danh sách khi có dữ liệu](screenshots/01-default.png)
```

## Sau khi upload

1. Lấy URL page từ output script.
2. Kiểm tra nhanh bằng `confluence_get_page` để xác nhận page tồn tại và ảnh hiển thị.
3. Trả link về cho user.

## Title convention (từ sample thật)

- `TN_<Tên màn hình>_<Project>` (ví dụ `TN_Danh sách giao dịch chờ xử lý_WEB`)
- `WEB <số>. <Tên>_<Project>` (ví dụ `WEB 2.1. Danh sách thẻ tín dụng nội địa_Skymap`)
- `APP <số>. <Tên>_<Project>` (ví dụ `APP 2.1. Danh sách thẻ tín dụng nội địa_Skymap`)

Hỏi user nếu không chắc convention.
