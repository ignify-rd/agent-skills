```
 █████╗  ██████╗ ███████╗███╗   ██╗████████╗    ███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝    ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║       ███████╗█████╔╝ ██║██║     ██║     ███████╗
██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║       ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║       ███████║██║  ██╗██║███████╗███████╗███████║
╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝       ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝
```
# Test Genie – Hướng dẫn sử dụng

Tool giúp tự động tạo **test design** và **test case** từ tài liệu RSD/PTTK, chạy ngay trong IDE.

---

## Cài đặt (chỉ làm 1 lần)

**1. Cài Node.js**
- Windows: https://nodejs.org → tải bản **LTS** → chạy cài đặt
- macOS: https://nodejs.org → tải bản **LTS** → chạy cài đặt

**2. Cài Test Genie**

```bash
npm install -g git+https://github.com/ignify-rd/agent-skills.git
```

---

## Kết nối Google Drive & Google Sheets (chỉ làm 1 lần)

Để AI tự đẩy test case lên Google Sheets, bạn cần kết nối Cursor với Google. Gồm 2 phần: **Google Drive** (tạo file) và **Google Sheets** (ghi dữ liệu).

### Bước 1: Tạo Google Cloud Project

1. Mở trình duyệt, vào https://console.cloud.google.com
2. Đăng nhập bằng tài khoản Google công ty
3. Ở thanh trên cùng, nhấn **chọn project** → **New Project**
4. Đặt tên (ví dụ: `test-genie`) → nhấn **Create**
5. Đợi vài giây, chọn project vừa tạo

### Bước 2: Bật API

1. Ở menu bên trái, chọn **APIs & Services** → **Library**
2. Tìm **Google Drive API** → nhấn **Enable**
3. Quay lại Library, tìm **Google Sheets API** → nhấn **Enable**

### Bước 3: Tạo OAuth credentials (cho Google Drive MCP)

1. Vào **APIs & Services** → **Credentials**
2. Nhấn **Create Credentials** → **OAuth client ID**
3. Nếu chưa có Consent Screen → nhấn **Configure Consent Screen** → chọn **External** → điền tên app → Save
4. Quay lại tạo OAuth: Application type = **Desktop app** → nhấn **Create**
5. Nhấn **Download JSON** → lưu file thành `gcp-oauth.keys.json`
6. Đặt file vào: `C:\Users\<tên_bạn>\.gdrive-mcp\gcp-oauth.keys.json`

### Bước 4: Tạo Service Account (cho Google Sheets MCP)

1. Vào **APIs & Services** → **Credentials**
2. Nhấn **Create Credentials** → **Service Account**
3. Đặt tên (ví dụ: `test-genie-sheets`) → nhấn **Create and Continue** → **Done**
4. Trong danh sách Service Accounts, nhấn vào tên vừa tạo
5. Tab **Keys** → **Add Key** → **Create new key** → chọn **JSON** → **Create**
6. File JSON tự download → đổi tên thành `service-account-key.json`
7. Đặt file vào: `C:\Users\<tên_bạn>\.gdrive-mcp\service-account-key.json`

> **Ghi nhớ email Service Account** (có dạng `test-genie-sheets@xxx.iam.gserviceaccount.com`). Bạn sẽ cần share spreadsheet cho email này ở bước sau.

### Bước 5: Cấu hình MCP trong Cursor

1. Mở Cursor → nhấn **Ctrl+Shift+P** → gõ `Open User Settings (JSON)` → Enter
2. Hoặc mở file trực tiếp: `C:\Users\<tên_bạn>\.cursor\mcp.json`
3. Thay toàn bộ nội dung bằng (nhớ đổi `<tên_bạn>` thành tên user Windows của bạn):

```json
{
  "mcpServers": {
    "gdrive": {
      "command": "npx",
      "args": ["-y", "@anthropic/gdrive-mcp"],
      "env": {
        "GDRIVE_OAUTH_PATH": "C:\\Users\\<tên_bạn>\\.gdrive-mcp\\gcp-oauth.keys.json",
        "GDRIVE_CREDENTIALS_PATH": "C:\\Users\\<tên_bạn>\\.gdrive-mcp\\credentials.json"
      }
    },
    "gsheets": {
      "command": "npx",
      "args": ["-y", "mcp-gsheets@latest"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\<tên_bạn>\\.gdrive-mcp\\service-account-key.json"
      }
    }
  }
}
```

4. **Restart Cursor** (tắt hoàn toàn rồi mở lại)

### Bước 6: Xác thực Google Drive (lần đầu tiên)

1. Mở Cursor, gõ chat: `list files in my google drive`
2. Cursor sẽ mở trình duyệt → đăng nhập Google → cho phép quyền truy cập
3. Sau khi cho phép, file `credentials.json` tự động được tạo trong `.gdrive-mcp/`
4. Từ lần sau không cần làm lại bước này

### Bước 7: Share spreadsheet cho Service Account

Mỗi khi tạo spreadsheet mới hoặc dùng template có sẵn:

1. Mở Google Sheets trên trình duyệt
2. Nhấn **Share** (Chia sẻ)
3. Dán email Service Account (từ Bước 4) → chọn quyền **Editor** → **Send**

> Nếu AI tự tạo spreadsheet từ template thì nó sẽ tự share. Bạn chỉ cần share khi dùng spreadsheet có sẵn.

### Kiểm tra kết nối

Trong Cursor, gõ chat:

```
Liệt kê các file trong Google Drive của tôi
```

Nếu thấy danh sách file → **Google Drive MCP hoạt động**.

```
Đọc dữ liệu từ Google Sheets ID: <paste spreadsheet ID vào đây>
```

Nếu thấy dữ liệu → **Google Sheets MCP hoạt động**.

---

## Setup dự án mới (chỉ làm 1 lần/dự án)

Mở terminal tại thư mục dự án, chạy:

```bash
test-genie init --ai cursor
```

Hỗ trợ các IDE khác: `claude`, `windsurf`, `copilot`, `gemini` — hoặc `--ai all` để cài hết.

> ⚠️ Lệnh này **không ghi đè** `AGENTS.md` nếu file đã tồn tại. Muốn reset thì xóa file đó trước rồi chạy lại.

Sau khi init, dự án sẽ có cấu trúc:

```
my-project/
├── AGENTS.md          ← Quy tắc riêng của dự án (bạn chỉnh)
├── catalog/           ← File mẫu để AI học theo (bạn bỏ vào)
│   ├── api/
│   ├── frontend/
│   └── mobile/
└── excel_template/    ← Template Excel
```

<!-- 📸 [Screenshot: cây thư mục dự án trong IDE] -->

---

## Bỏ file mẫu vào catalog

AI sẽ **bắt chước theo các file mẫu** này để sinh đúng format của dự án. Càng nhiều mẫu tốt, kết quả càng chuẩn.

| Loại | Định dạng | Bỏ vào đâu |
|---|---|---|
| Test case mẫu | `.csv`, `.xlsx` | `catalog/api/` hoặc `catalog/frontend/` |
| Test design mẫu | `.md`, `.txt` | `catalog/api/` hoặc `catalog/frontend/` |
| Mindmap | `.gitmind`, `.xmind` | Export sang `.md`/`.txt` trước rồi mới bỏ vào |

**Lấy file mẫu ở đâu?**
- Test case: mở Google Sheets cũ → **File > Download > CSV** → copy vào `catalog/`
- Test design: lấy file `.md` từ lần sinh trước → copy vào `catalog/`

<!-- 📸 [Screenshot: export CSV từ Google Sheets] -->
<!-- 📸 [Screenshot: thư mục catalog với các file mẫu] -->

---

## Tùy chỉnh AGENTS.md (nếu cần)

Mở file `AGENTS.md` ở gốc dự án và thêm quy tắc riêng, ví dụ:

```markdown
## Project-Specific Rules

- Response dùng "code"/"message" thay vì "errorCode"/"errorDesc"
- Tất cả API phải có header X-Request-ID
- Khi tài liệu không rõ, tự quyết định, không cần hỏi.
```

<!-- 📸 [Screenshot: file AGENTS.md trong IDE] -->

---

## Tạo test design

**Chuẩn bị:** Đặt file RSD và PTTK vào thư mục dự án.

**Gọi lệnh trong IDE:**

```
/generate-test-design
```

AI đọc tài liệu, có thể hỏi thêm vài câu để làm rõ, rồi sinh ra file `.md`.

<!-- 📸 [Screenshot: gõ lệnh trong IDE] -->
<!-- 📸 [Screenshot: file .md kết quả] -->

> 💡 Sau khi xong, copy file `.md` vào `catalog/` để AI học cho lần sau.

---

## Tạo test case

**Gọi lệnh trong IDE:**

```
/generate-test-case
```

AI hỏi đường dẫn file test design, sinh test case theo 3 đợt (common → validate → luồng chính), rồi đẩy kết quả lên **Google Sheets**.

<!-- 📸 [Screenshot: gõ lệnh trong IDE] -->
<!-- 📸 [Screenshot: link Google Sheets kết quả] -->

> 💡 Chưa có file test design cũng không sao — AI sẽ tự tạo trước rồi mới sinh test case.

---

## Cập nhật khi có phiên bản mới

```bash
test-genie update --ai cursor
```

File của bạn (`catalog/`, `AGENTS.md`) **sẽ không bị ảnh hưởng**.