# Output Format — Test Case JSON Schema

## JSON Schema (mỗi test case)

```typescript
{
  "testSuiteName": string,       // Tên test suite = ## heading trong mindmap
  "testCaseName": string,        // Tên test case (xem rules trong api/fe-test-case.md)
  "summary": string,             // = testCaseName (giống hệt)
  "preConditions": string,       // Multi-line
  "step": string,                // Numbered steps: "1. ...\n2. ..."
  "expectedResult": string,      // Expected outcome
  "importance": "Low" | "Medium" | "High",
  "result": "PENDING"            // LUÔN để "PENDING"
}
```

## Importance Mapping

### API Test Cases

| testSuiteName contains | importance |
|------------------------|------------|
| "case common" | "Low" |
| "phân quyền" | "Medium" |
| "validate" | "Medium" |
| "luồng chính" | "High" |
| "chức năng" | "High" |
| Khác | "Medium" |

---

> **Lưu ý về style/wording:** Các ví dụ dưới đây là **format mặc định** (fallback). Nếu project có catalog examples → output PHẢI follow style/wording của catalog, KHÔNG copy cách viết từ ví dụ bên dưới. Account xác định theo thứ tự: (1) project AGENTS.md → (2) catalog examples → (3) default `164987/ Test@147258369`. Xem chi tiết tại `api-test-case.md` R4.

## Ví dụ 1: API Test Case — Common Section

```json
{
  "testSuiteName": "Kiểm tra các case common",
  "testCaseName": "Method_Kiểm tra khi nhập sai method",
  "summary": "Method_Kiểm tra khi nhập sai method",
  "preConditions": "1. Send API login thành công\n2. Chuẩn bị request hợp lệ\n   2.1 Endpoint: POST {{BASE_URL}}/v1/fee/search\n   2.2 Header:\n   {\n     \"Authorization\": \"Bearer {JWT_TOKEN}\",\n     \"Content-Type\": \"application/json\"\n   }\n   2.3 Body:\n   {\n     \"regChannel\": \"WEB\",\n     \"pageSize\": 5,\n     \"pageIndex\": 1\n   }",
  "step": "1. Nhập invalid Method: GET\n2. Send API",
  "expectedResult": "1. Check api trả về:\n   1.1. Status: 107\n   1.2. Response:\n   {\n     \"message\": \"Error retrieving AuthorInfo for token from TokenLib: Token is invalid signature\"\n   }",
  "importance": "Low",
  "result": "PENDING"
}
```

## Ví dụ 2: API Test Case — Validate Section

```json
{
  "testSuiteName": "Kiểm tra validate",
  "testCaseName": "regChannel_Bỏ trống field bắt buộc",
  "summary": "regChannel_Bỏ trống field bắt buộc",
  "preConditions": "1. Send API login thành công\n2. Chuẩn bị request hợp lệ\n   2.1 Endpoint: POST {{BASE_URL}}/v1/fee/search\n   2.2 Header:\n   {\n     \"Authorization\": \"Bearer {JWT_TOKEN}\",\n     \"Content-Type\": \"application/json\"\n   }\n   2.3 Body:\n   {\n     \"regChannel\": \"WEB\",\n     \"pageSize\": 5,\n     \"pageIndex\": 1\n   }",
  "step": "1. Bỏ trống regChannel (bắt buộc)\n2. Send API",
  "expectedResult": "1. Check api trả về:\n   1.1. Status: 200\n   1.2. Response:\n   {\n     \"message\": \"Dữ liệu không hợp lệ\"\n   }",
  "importance": "Medium",
  "result": "PENDING"
}
```