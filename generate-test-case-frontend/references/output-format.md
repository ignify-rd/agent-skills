# Output Format — Test Case JSON Schema

## JSON Schema (mỗi test case)

```typescript
{
  "testSuiteName": string,       // Tên test suite = ## heading trong mindmap
  "testCaseName": string,        // Tên test case (xem rules trong fe-test-case.md)
  "testcaseLV1": string,         // ## section heading (main suite group, e.g., "Kiểm tra giao diện chung")
  "testcaseLV2": string,         // ### sub-heading OR testCaseName if no sub-heading
  "testcaseLV3": string,         // testCaseName if ### sub-heading exists; "" otherwise
  "summary": string,             // = testcaseLV3 if non-empty; else testcaseLV2
  "preConditions": string,       // Multi-line
  "step": string,                // Numbered steps: "1. ...\n2. ..."
  "expectedResult": string,      // Expected outcome
  "importance": "Low" | "Medium" | "High",
  "result": "PENDING"            // LUÔN để "PENDING"
}
```

## LV1 / LV2 / LV3 Rules

| Trường hợp | testcaseLV1 | testcaseLV2 | testcaseLV3 | summary |
|-----------|-------------|-------------|-------------|---------|
| ## section, không có ### sub-group (giao diện, phân quyền, tìm kiếm...) | testSuiteName | testCaseName | `""` | testcaseLV2 |
| ## Kiểm tra validate + field sub-suite (catalog dùng "Textbox: Tên X") | `"Kiểm tra validate"` | field sub-suite name | testCaseName | testcaseLV3 |
| ## Kiểm tra validate, không có field sub-suite | `"Kiểm tra validate"` | testCaseName | `""` | testcaseLV2 |
| ## section có ### button sub-group (tc-mainflow, e.g., "Button Lưu") | parent ## heading | testSuiteName (button name) | testCaseName | testcaseLV3 |

## Importance Mapping

| testSuiteName contains | importance |
|------------------------|------------|
| "giao diện chung" | "Low" |
| "phân quyền" | "Medium" |
| "validate" | "Medium" |
| "lưới dữ liệu" | "Low" |
| "phân trang" | "Low" |
| "chức năng" | "High" |
| "timeout" | "Low" |
| Khác | "Medium" |

---

> **Lưu ý về style/wording:** Các ví dụ dưới đây là **format mặc định** (fallback). Nếu project có catalog examples → output PHẢI follow style/wording của catalog, KHÔNG copy cách viết từ ví dụ bên dưới. Account xác định theo thứ tự: (1) project AGENTS.md → (2) catalog examples → (3) default `164987/ Test@147258369`. Xem chi tiết tại `fe-test-case.md` R4.

## Ví dụ 1: Frontend Test Case — Giao diện chung

```json
{
  "testSuiteName": "Kiểm tra giao diện chung",
  "testCaseName": "Kiểm tra điều hướng đến màn hình Tần suất thu phí",
  "summary": "Kiểm tra điều hướng đến màn hình Tần suất thu phí",
  "preConditions": "Đ/k1: Vào màn hình:\n1. Người dùng đăng nhập thành công FEE trên Web với account: 164987/ Test@147258369\n2. Tại sitemap, người dùng truy cập màn hình Danh mục > Tần suất thu phí\nĐ/k2: Phân quyền\n3. User được phân quyền truy cập",
  "step": "1. Quan sát màn hình sau khi điều hướng",
  "expectedResult": "Điều hướng thành công đến màn hình Tần suất thu phí",
  "importance": "Low",
  "result": "PENDING",
}
```

## Ví dụ 2: Frontend Test Case — Validate Field

```json
{
  "testSuiteName": "Kiểm tra validate",
  "testCaseName": "Kiểm tra khi nhập 101 ký tự",
  "summary": "Kiểm tra khi nhập 101 ký tự",
  "preConditions": "Đ/k1: Vào màn hình:\n1. Người dùng đăng nhập thành công FEE trên Web với account: 164987/ Test@147258369\n2. Tại sitemap, người dùng truy cập màn hình Danh mục > Tần suất thu phí\nĐ/k2: Phân quyền\n3. User được phân quyền truy cập",
  "step": "1. Tại textbox \"Tên tần suất\", nhập 101 ký tự\n2. Quan sát",
  "expectedResult": "Hiển thị cảnh báo \"Tên tần suất không được vượt quá 100 ký tự\"",
  "importance": "Medium",
  "result": "PENDING",
}
```

## Ví dụ 3: Frontend Test Case — Chức năng

```json
{
  "testSuiteName": "Kiểm tra chức năng",
  "testCaseName": "Kiểm tra chức năng Tìm kiếm khi nhập điều kiện hợp lệ",
  "summary": "Kiểm tra chức năng Tìm kiếm khi nhập điều kiện hợp lệ",
  "preConditions": "Đ/k1: Vào màn hình:\n1. Người dùng đăng nhập thành công FEE trên Web với account: 164987/ Test@147258369\n2. Tại sitemap, người dùng truy cập màn hình Danh mục > Tần suất thu phí\nĐ/k2: Phân quyền\n3. User được phân quyền truy cập\n4. Có dữ liệu trong hệ thống",
  "step": "1. Nhập điều kiện tìm kiếm hợp lệ vào các fields bộ lọc\n2. Click button \"Tìm kiếm\"",
  "expectedResult": "Hiển thị kết quả khớp với điều kiện tìm kiếm đã nhập",
  "importance": "High",
  "result": "PENDING",
}
```
