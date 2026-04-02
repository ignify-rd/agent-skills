# Hướng dẫn cài đặt MCP cho Agent Skills

Hướng dẫn này giúp cài đặt 3 MCP servers cần thiết cho các skill execute-test-case (API & Frontend):

1. **Playwright** — điều khiển browser tự động
2. **Google Sheets** — đọc/ghi test case từ Google Sheets
3. **Google Drive** — upload screenshot evidence lên Drive

---

## Yêu cầu chung

- **Node.js** >= 18 (kiểm tra: `node -v`)
- **Python** >= 3.10 (kiểm tra: `python3 --version`)
- **Claude Code** đã cài đặt (CLI hoặc VS Code extension)

---

## 1. Playwright MCP

Playwright MCP đơn giản nhất — không cần credentials.

### Cài đặt

```bash
claude mcp add playwright -s user -- npx -y @playwright/mcp@latest
```

### Kiểm tra

```bash
claude mcp list | grep playwright
# playwright: npx -y @playwright/mcp@latest - ✓ Connected
```

Không cần config thêm gì.

---

## 2. Google Sheets MCP

### Bước 1 — Tạo OAuth credentials trên Google Cloud Console

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Bật APIs:
   - Vào **APIs & Services → Library**
   - Tìm và bật **Google Sheets API**
   - Tìm và bật **Google Drive API**
4. Tạo OAuth credentials:
   - Vào **APIs & Services → Credentials**
   - Bấm **+ CREATE CREDENTIALS → OAuth client ID**
   - Application type: **Desktop app**
   - Đặt tên bất kỳ (VD: `mcp-sheets`)
   - Bấm **CREATE**
5. Tải file JSON:
   - Bấm **DOWNLOAD JSON** (nút download bên phải)
   - File tải về có dạng `client_secret_XXXXX.json`

### Bước 2 — Lấy refresh token

Cài package:

```bash
npm install -g mcp-google-sheets
```

Chạy auth flow lần đầu để lấy token:

```bash
npx mcp-google-sheets-auth
```

Lệnh này sẽ:
- Hỏi Client ID và Client Secret (lấy từ file JSON ở Bước 1)
- Mở browser để bạn đăng nhập Google và cho phép quyền
- Trả về **Access Token**, **Refresh Token**, **Expiry**

Copy các giá trị này.

### Bước 3 — Thêm MCP vào Claude Code

```bash
claude mcp add gsheets -s user \
  -e GOOGLE_SHEETS_CLIENT_ID="<client_id_từ_file_json>" \
  -e GOOGLE_SHEETS_CLIENT_SECRET="<client_secret_từ_file_json>" \
  -e GOOGLE_SHEETS_REFRESH_TOKEN="<refresh_token_từ_bước_2>" \
  -e GOOGLE_SHEETS_ACCESS_TOKEN="<access_token_từ_bước_2>" \
  -e GOOGLE_SHEETS_TOKEN_EXPIRY="<expiry_từ_bước_2>" \
  -- node <đường_dẫn_tới>/node_modules/mcp-google-sheets/dist/index.js
```

> **Lưu ý:** `<đường_dẫn_tới>` phụ thuộc vào cách cài Node.js. Nếu dùng nvm thì có thể là `C:\nvm4w\nodejs`. Tìm bằng: `npm root -g`

### Kiểm tra

```bash
claude mcp list | grep gsheets
# gsheets: node .../mcp-google-sheets/dist/index.js - ✓ Connected
```

---

## 3. Google Drive MCP (search + upload)

### Bước 1 — Tạo OAuth credentials (dùng chung hoặc tạo riêng)

Có thể **dùng chung** project Google Cloud ở phần Google Sheets, nhưng cần tạo thêm 1 OAuth client ID riêng cho Drive (hoặc dùng chung cũng được).

1. Vào **APIs & Services → Library** → bật **Google Drive API** (nếu chưa bật)
2. Vào **APIs & Services → Credentials** → **+ CREATE CREDENTIALS → OAuth client ID**
   - Application type: **Desktop app**
   - Tên: `mcp-gdrive`
   - Bấm **CREATE** → **DOWNLOAD JSON**

### Bước 2 — Đặt file credentials

Tạo thư mục và đặt file:

```bash
mkdir -p ~/.gdrive-mcp
```

Copy file JSON tải về thành:

```bash
cp client_secret_XXXXX.json ~/.gdrive-mcp/gcp-oauth.keys.json
```

### Bước 3 — Thêm MCP vào Claude Code

```bash
claude mcp add gdrive -s user \
  -e GDRIVE_OAUTH_PATH="C:\Users\<username>\.gdrive-mcp\gcp-oauth.keys.json" \
  -e GDRIVE_CREDENTIALS_PATH="C:\Users\<username>\.gdrive-mcp\credentials.json" \
  -- npx -y @modelcontextprotocol/server-gdrive
```

Thay `<username>` bằng tên user Windows.

### Bước 4 — Auth lần đầu

Lần đầu chạy Claude Code với MCP gdrive, nó sẽ báo **"Needs authentication"**.

```bash
claude mcp list | grep gdrive
# gdrive: ... - ! Needs authentication
```

Chạy lệnh sau trong Claude Code (hoặc chạy trực tiếp):

```bash
npx -y @modelcontextprotocol/server-gdrive
```

Server sẽ in ra 1 URL → mở trong browser → đăng nhập Google → cho phép quyền → redirect về localhost với authorization code → server tự lưu token vào `~/.gdrive-mcp/credentials.json`.

Sau khi auth xong, restart Claude Code. Kiểm tra:

```bash
claude mcp list | grep gdrive
# gdrive: npx -y @modelcontextprotocol/server-gdrive - ✓ Connected
```

### Bước 5 — Cài thư viện Python cho upload script

Script `gdrive_upload.py` cần thư viện Google API:

```bash
pip install google-api-python-client google-auth google-auth-oauthlib
```

Script tự động dùng lại credentials từ `~/.gdrive-mcp/` — không cần config thêm.

### Kiểm tra upload

```bash
python3 scripts/gdrive_upload.py "đường_dẫn_ảnh.png"
```

Output:

```json
{
  "id": "...",
  "name": "ảnh.png",
  "link": "https://drive.google.com/file/d/.../view",
  "direct": "https://lh3.googleusercontent.com/d/..."
}
```

URL `direct` có thể dùng trong Google Sheets: `=IMAGE("https://lh3.googleusercontent.com/d/...")`

---

## OAuth Consent Screen (quan trọng!)

Nếu gặp lỗi **"Access blocked: This app's request is invalid"** hoặc **"Error 403: access_denied"**:

1. Vào **Google Cloud Console → APIs & Services → OAuth consent screen**
2. Chọn **External** (nếu chưa có)
3. Điền thông tin bắt buộc:
   - App name: bất kỳ (VD: `MCP Agent`)
   - User support email: email của bạn
   - Developer contact: email của bạn
4. **Scopes**: thêm:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive.file`
5. **Test users**: thêm email Google của bạn
6. Bấm **Save**

> **Lưu ý:** App ở trạng thái "Testing" chỉ cho phép test users đăng nhập. Đủ dùng cho cá nhân. Không cần publish.

---

## Tổng kết cấu trúc file

```
~/.gdrive-mcp/
├── gcp-oauth.keys.json          ← OAuth client JSON (tải từ Google Cloud Console)
├── credentials.json             ← Token tự động tạo sau auth lần đầu (gdrive)
└── .gdrive-server-credentials.json  ← Token MCP gdrive server lưu
```

MCP configs lưu trong Claude Code (không cần sửa file thủ công):

```bash
claude mcp list
# playwright: npx -y @playwright/mcp@latest               - ✓ Connected
# gsheets:    node .../mcp-google-sheets/dist/index.js      - ✓ Connected
# gdrive:     npx -y @modelcontextprotocol/server-gdrive    - ✓ Connected
```

---

## Troubleshooting

| Vấn đề | Giải pháp |
|---------|-----------|
| `! Needs authentication` | Chạy lại auth flow (Bước 4 của gdrive hoặc Bước 2 của gsheets) |
| `Token expired` | Token tự refresh. Nếu refresh token hết hạn → chạy lại auth flow |
| `=IMAGE()` không hiển thị trong Sheets | Vào **File → Settings → Calculation** → bật "Allow access to fetch data from external URLs" |
| `google-api-python-client not found` | `pip install google-api-python-client google-auth google-auth-oauthlib` |
| Google chặn đăng nhập OAuth | Kiểm tra OAuth Consent Screen đã thêm email vào Test Users chưa |
