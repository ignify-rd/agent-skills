# Profile Schema

This profile makes the generator reusable across different project templates.

## JSON Shape

```json
{
  "name": "project-name",
  "aliases": {
    "id": ["ID", "Test Case ID"],
    "name": ["Name", "Test Case Name"],
    "method": ["Method", "HTTP Method"],
    "endpoint": ["Endpoint", "Path", "URL"],
    "headers": ["Headers", "Request Headers"],
    "body": ["Body", "Request Body"],
    "auth_type": ["Auth Type", "Auth"],
    "auth_token": ["Auth Token", "Token"],
    "expected_status": ["Expected Status", "Status Code"],
    "description": ["Description", "Details"],
    "preconditions": ["PreConditions", "Pre-conditions"],
    "query_params": ["Params", "Query"],
    "curl": ["cURL", "Raw Request", "Request CURL"],
    "prerequest_script": ["Pre-request Script", "Pre Script"],
    "test_script": ["Test Script", "Post Script"],
    "response_assertions": ["Response Assertions", "Assertions"]
  },
  "defaults": {
    "auth_type": "bearer",
    "auth_token": "{{globalToken}}",
    "expected_status": 200,
    "base_url_variable": "{{serviceUrl}}"
  },
  "regex_extractors": [
    {
      "target": "method",
      "sources": ["Step", "Action"],
      "pattern": "\\\\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\\\\b",
      "group": 1
    },
    {
      "target": "endpoint",
      "sources": ["Step", "Action"],
      "pattern": "(\\\\/[-A-Za-z0-9_{}\\\\/.]*)",
      "group": 1
    }
  ],
  "default_headers": {
    "Content-Type": "application/json"
  },
  "row_filters": {
    "allow_root_endpoint": false,
    "allow_non_ascii_endpoint": false,
    "skip_if_no_method_and_endpoint": true,
    "skip_if_sparse_row": true,
    "sparse_non_empty_threshold": 2,
    "suite_header_keywords": ["test suite", "section", "link pttk", "link rsd"]
  },
  "bootstrap": {
    "enabled": true,
    "sample_size": 8
  },
  "query_parsing": {
    "from_step_when_get": true,
    "require_params_marker": true
  }
}
```

## Notes

- `aliases`: First matching column is used.
- `defaults.base_url_variable`: Used to build request URL when endpoint is relative.
- `regex_extractors`: Optional fallback extraction for mixed-content templates.
- `default_headers`: Merged with row headers; row headers take precedence.
- `row_filters`: Guards to remove suite/header rows and metadata rows.
- `bootstrap`: Sample first N test cases to infer base request signature (method/endpoint/headers/body) before full parsing.
- `query_parsing`: Control whether to infer query params from `Step` for GET requests.
