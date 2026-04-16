---
name: merge-postman-results
description: >
  Merge API test execution results from the auto-postman tool into a Google Spreadsheet.
  Use this skill whenever the user wants to merge, import, or update Postman/API test results
  into a Google Sheet — even if they phrase it as "cập nhật kết quả", "điền actual result",
  "đánh giá pass/fail", "upload evidence", or "import postman output".
  The skill runs a Python script to: download the Google Sheet as xlsx, match test cases by name,
  fill the Actual Result column with response JSON body, evaluate Pass/Fail by status code
  comparison and write the verdict to the "Kết quả hiện tại" (status) column,
  embed screenshots into an "Evidence" sheet, and upload the merged xlsx back to Google Sheets.
---

# Merge Postman Results into Google Spreadsheet

## What this skill does

Reads the auto-postman tool output (an `.xlsx` file) and merges results into the target
**Google Spreadsheet**. The workflow:

1. **Downloads** the Google Sheet as `.xlsx` (preserving all formatting)
2. **Matches** test cases by name between source and target
3. Fills the **Actual Result** column with the response JSON body from source
4. Evaluates **Pass / Fail / N/A** by comparing status codes (expected vs actual)
5. Writes the verdict (`PASS`/`FAIL`/`N/A`) to the **Kết quả hiện tại** (status) column
6. Creates/updates the **"Evidence"** sheet with embedded screenshot images
7. **Uploads** the merged `.xlsx` back to the Google Sheet (converted to native Google Sheets format)

## Inputs the user must provide

| Input | Description |
|-------|-------------|
| **Source xlsx** | Auto-postman output, e.g. `api_results_20260415_091720.xlsx` |
| **Target Google Sheet** | Google Sheets URL, e.g. `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit` |
| **structure.json** | Column mapping for the target file |

### structure.json format

```json
{
  "headerRow": 10,
  "dataStartRow": 13,
  "columnMapping": {
    "externalId":      0,
    "testCaseName":    1,
    "expectedResults": 6,
    "actualResult":    7,
    "status":          11
  }
}
```

> **Note:** Column indices are **0-based** (0 = column A, 1 = column B, ...)

**Fields used by this skill:**

| Field | Required | Purpose |
|-------|----------|---------|
| `testCaseName` | yes | **Match key** — matched against `API Name` from source |
| `expectedResults` | yes | Status code compared for evaluation |
| `actualResult` | yes | Filled with response JSON body from source |
| `headerRow` | yes | Which row contains column headers |
| `dataStartRow` | yes | First row with test case data |
| `status` | **recommended** | Filled with `PASS` / `FAIL` / `N/A` verdict. Auto-detected by scanning the header row for "Status", "Trạng thái", "Kết quả hiện tại", "Result", "Pass/Fail". |

## Auto-detect structure from a new Google Sheet

If you don't have a `structure.json` for the target sheet, generate one automatically:

```python
# Via Python import (avoids argparse --source/--target requirement)
python -c "
import sys, json
sys.path.insert(0, 'scripts')
from merge_postman_results import detect_structure

result = detect_structure('https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit')
print(json.dumps(result, ensure_ascii=False, indent=2))
" > structure.json
```

Or redirect stderr to keep stdout clean:

```bash
python merge_postman_results.py --detect "URL_SHEET" > structure.json 2>nul
```

The `detect_structure()` function:
1. Downloads the Google Sheet as xlsx
2. Scans rows 1-40 to find the header row (looks for "External ID" + "Name" + "Expected Result" + "Step")
3. Matches columns using `FIELD_SYNONYMS` (checks header row and row above for merged-cell labels like "Kết quả hiện tại")
4. Auto-detects the `externalId` column by scanning data rows for `API_1`, `API1`, `Login`, etc.
5. Detects `dataStartRow` by finding the first row with a non-empty externalId

## How to run

```bash
python scripts/merge_postman_results.py \
  --source "/path/to/api_results_20260415_091720.xlsx" \
  --target "https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit" \
  --structure "path/to/structure.json"
```

Optional flags:

| Flag | Effect |
|------|--------|
| `--dry-run` | Print what would happen without writing anything |

## Google Authentication

The script reuses OAuth credentials from the **gsheets MCP server**:

- Token file: `~/google-sheets-mcp/dist/.gsheets-server-credentials.json`
- OAuth keys: `~/google-sheets-mcp/dist/gcp-oauth.keys.json`

On first run, if the token lacks **Drive scope** (needed to download/upload the spreadsheet),
the script will open a browser for one-time re-authorization. The updated token is saved back
to the same credential file, so the MCP server continues to work.

**Required scopes:**
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/drive`

## Workflow when user asks to merge

1. **Ask for** source xlsx path and target Google Sheet URL
2. **No structure.json?** → Run `detect_structure()` first to generate it (see section above), save to `structure.json`
3. **Validate structure.json** if provided — check `headerRow`, `dataStartRow`, and `columnMapping` keys exist
4. **Run the script**: `python scripts/merge_postman_results.py --source ... --target ... --structure ...`
5. **Report results**: matched count, PASS/FAIL/N/A breakdown, unmatched test cases, Google Sheet URL
6. If many test cases are unmatched, compare API Name values to diagnose mismatches

## Evidence sheet

The script creates (or replaces) the "Evidence" sheet with:

- **Column A** — `ID`: test case name or external ID
- **Column B** — `Evidence`: screenshot image embedded directly in the cell

Screenshots are extracted from embedded images in the source xlsx. Missing images show
a `[No screenshot]` placeholder. Images are preserved when uploaded back to Google Sheets.

## Troubleshooting

**Test cases not matching**
The `API Name` in source must exactly match the `testCaseName` column in the target.
Use `--dry-run` to compare values.

**Google auth error**
Delete `~/google-sheets-mcp/dist/.gsheets-server-credentials.json` and re-run.
The script will re-authorize from scratch.

**openpyxl image error**
Install Pillow: `pip install pillow`
