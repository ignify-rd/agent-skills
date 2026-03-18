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