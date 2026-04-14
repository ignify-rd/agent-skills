#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upload_to_sheet.py - Write test case JSON data to Google Sheets + apply formatting

Usage:
  python upload_to_sheet.py --spreadsheet-id 1xyz... --sheet-name TestCases \
    --data test_cases.json --column-mapping mapping.json

  # Or pipe JSON directly
  echo '[{"testSuiteName":"Suite A","testCaseName":"TC1",...}]' | \
    python upload_to_sheet.py --spreadsheet-id 1xyz... --sheet-name TestCases \
    --column-mapping mapping.json --stdin

  # Full options
  python upload_to_sheet.py \
    --spreadsheet-id 1xyz... \
    --sheet-name TestCases \
    --sheet-id 0 \
    --data test_cases.json \
    --column-mapping '{"testSuiteName":0,"testCaseName":3,...}' \
    --total-columns 13 \
    --data-start-row 2 \
    --credentials credentials.json

Input JSON format (array of test case objects):
  [
    {
      "testSuiteName": "Kiểm tra các case common",
      "testCaseName": "Method_Kiểm tra khi nhập sai method GET",
      "summary": "Method_Kiểm tra khi nhập sai method GET",
      "preConditions": "1. Send API login...",
      "steps": "1. Nhập invalid Method: GET\\n2. Send API",
      "expectedResults": "1. Check api trả về:\\n 1.1. Status: 107",
      "result": "PENDING"
    },
    ...
  ]

Output (JSON):
  {
    "success": true,
    "rowsWritten": 75,
    "suiteCount": 5,
    "testCaseCount": 70,
    "updatedRange": "TestCases!A2:M76"
  }

Requirements:
  pip install google-api-python-client google-auth
"""

import argparse
import json
import os
import sys

# Import shared auth module (same directory)
sys.path.insert(0, os.path.dirname(__file__))
try:
    from google_auth import find_credentials as _find_creds, build_sheets_service as _build_sheets
    _USE_OAUTH = True
except ImportError:
    _USE_OAUTH = False

try:
    from googleapiclient.discovery import build
except ImportError:
    print(json.dumps({"error": "Missing dependencies. Run: pip install google-api-python-client google-auth"}))
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]

# Suite header formatting: light green #DAEAD0
SUITE_HEADER_FORMAT = {
    'backgroundColor': {'red': 0.855, 'green': 0.918, 'blue': 0.816},
    'textFormat': {
        'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
        'bold': True,
        'fontSize': 11,
    },
    'horizontalAlignment': 'LEFT',
    'wrapStrategy': 'WRAP',
    'borders': {
        'top':    {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'bottom': {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'left':   {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'right':  {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
    },
}

# Test case row formatting: white background
TEST_CASE_FORMAT = {
    'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
    'textFormat': {
        'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
        'bold': False,
        'fontSize': 11,
    },
    'horizontalAlignment': 'LEFT',
    'wrapStrategy': 'WRAP',
    'borders': {
        'top':    {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'bottom': {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'left':   {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'right':  {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
    },
}

FORMAT_FIELDS = 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy,borders)'


def find_credentials(provided_path=None):
    if _USE_OAUTH:
        return _find_creds(provided_path)
    candidates = []
    if provided_path:
        candidates.append(provided_path)
    candidates += [
        'credentials.json',
        os.path.expanduser('~/.config/test-genie/credentials.json'),
        os.path.join(os.path.dirname(__file__), '..', 'credentials.json'),
        os.path.join(os.path.dirname(__file__), 'credentials.json'),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def build_sheets_service(credentials_path):
    if _USE_OAUTH:
        return _build_sheets(credentials_path)
    # Legacy fallback: service account
    from google.oauth2 import service_account
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)


def col_index_to_letter(index):
    """Convert 0-based column index to letter (0→A, 25→Z, 26→AA)."""
    result = ''
    index += 1
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def build_rows(test_cases, column_mapping, total_columns):
    """
    Build 2D array from test cases using column mapping.
    Inserts suite header rows when testSuiteName changes.
    Returns (rows, suite_row_indices, test_case_count)
    """
    rows = []
    suite_row_indices = []  # 0-based indices of suite header rows in `rows`
    test_case_count = 0
    current_suite = None

    def make_row(field_values):
        row = [''] * total_columns
        for key, value in field_values.items():
            col_idx = column_mapping.get(key)
            if col_idx is not None and col_idx < total_columns:
                row[col_idx] = str(value) if value is not None else ''
        return row

    for tc in test_cases:
        suite_name = tc.get('testSuiteName', '')

        # Insert suite header when suite changes
        if suite_name and suite_name != current_suite:
            current_suite = suite_name
            suite_row_indices.append(len(rows))
            rows.append(make_row({'testSuiteName': suite_name}))

        # Build test case row
        # Normalize field aliases first so column mapping works regardless of key name used
        steps_val = tc.get('steps') or tc.get('step') or tc.get('testSteps') or ''
        expected_val = tc.get('expectedResults') or tc.get('expectedResult') or ''
        summary_val = tc.get('summary') or tc.get('testObjective') or tc.get('testCaseName', '')
        tc_name_val = tc.get('testCaseName') or tc.get('testCaseTitle') or ''

        tc_row = make_row({
            'testCaseName':    tc_name_val,
            'testCaseTitle':   tc_name_val,
            'summary':         summary_val,
            'testObjective':   summary_val,
            'preConditions':   tc.get('preConditions', ''),
            'steps':           steps_val,
            'testSteps':       steps_val,
            'expectedResults': expected_val,
            'expectedResult':  expected_val,
            'result':          tc.get('result', 'PENDING'),
            'testResults':     tc.get('testResults', ''),
            'importance':      tc.get('importance', ''),
            'priority':        tc.get('priority') or tc.get('importance', ''),
            'externalId':      tc.get('externalId', ''),
            'testCaseId':      tc.get('testCaseId', ''),
            'note':            tc.get('note', ''),
            'notes':           tc.get('note', ''),
            'details':         tc.get('details', ''),
            'specTitle':       tc.get('specTitle', ''),
            'documentId':      tc.get('documentId', ''),
            'duration':        tc.get('duration', ''),
            'keywords':        tc.get('keywords', ''),
            'status':          tc.get('status', ''),
            'executionType':   tc.get('executionType', ''),
            'testcaseLV1':     tc.get('testcaseLV1', ''),
            'testcaseLV2':     tc.get('testcaseLV2', ''),
            'testcaseLV3':     tc.get('testcaseLV3', ''),
            'actualResult':    tc.get('actualResult', ''),
            'stepExecType':    tc.get('stepExecType', ''),
            'attachments':     tc.get('attachments', ''),
            'bugId':           tc.get('bugId', ''),
            'testLevel':       tc.get('testLevel', ''),
        })
        rows.append(tc_row)
        test_case_count += 1

    return rows, suite_row_indices, test_case_count


def append_rows(sheets_service, spreadsheet_id, sheet_name, last_col, rows, data_start_row):
    """Append rows to sheet using INSERT_ROWS mode."""
    range_str = f"'{sheet_name}'!A:{last_col}"

    # Split into chunks of 500 rows to avoid API limits
    chunk_size = 500
    last_updated_range = None

    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i + chunk_size]
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_str,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': chunk}
        ).execute()
        updated = result.get('updates', {}).get('updatedRange', '')
        if updated:
            last_updated_range = updated

    return last_updated_range


def parse_start_row(updated_range):
    """Extract start row number from range string like 'Sheet1!A2:M76'."""
    import re
    match = re.search(r'!A(\d+)', updated_range or '')
    return int(match.group(1)) if match else None


def build_format_requests(rows, suite_row_indices, start_row, sheet_id, total_columns):
    """Build batchUpdate requests for suite headers and test case rows."""
    requests = []
    suite_set = set(suite_row_indices)

    # Group consecutive test case rows for efficiency
    i = 0
    while i < len(rows):
        sheet_row = start_row + i  # 1-based
        row_index = sheet_row - 1  # 0-based for API

        if i in suite_set:
            # Suite header: format + merge
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': row_index,
                        'endRowIndex': row_index + 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': total_columns,
                    },
                    'cell': {'userEnteredFormat': SUITE_HEADER_FORMAT},
                    'fields': FORMAT_FIELDS,
                }
            })
            requests.append({
                'mergeCells': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': row_index,
                        'endRowIndex': row_index + 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': total_columns,
                    },
                    'mergeType': 'MERGE_ALL',
                }
            })
            i += 1
        else:
            # Find consecutive test case rows (not suite headers)
            j = i
            while j < len(rows) and j not in suite_set:
                j += 1
            # Format range [i, j) as test case rows
            start_idx = start_row + i - 1  # 0-based
            end_idx = start_row + j - 1    # 0-based exclusive
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': start_idx,
                        'endRowIndex': end_idx,
                        'startColumnIndex': 0,
                        'endColumnIndex': total_columns,
                    },
                    'cell': {'userEnteredFormat': TEST_CASE_FORMAT},
                    'fields': FORMAT_FIELDS,
                }
            })
            i = j

    # Auto-resize rows to fit content
    requests.append({
        'autoResizeDimensions': {
            'dimensions': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'startIndex': start_row - 1,
                'endIndex': start_row - 1 + len(rows),
            }
        }
    })

    return requests


def apply_formatting(sheets_service, spreadsheet_id, requests):
    """Send batchUpdate with formatting requests."""
    if not requests:
        return
    # Split into chunks of 100 requests to avoid API limits
    chunk_size = 100
    for i in range(0, len(requests), chunk_size):
        chunk = requests[i:i + chunk_size]
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': chunk}
        ).execute()


def main():
    parser = argparse.ArgumentParser(description='Upload test cases to Google Sheets')
    parser.add_argument('--spreadsheet-id', required=True, help='Google Sheets spreadsheet ID')
    parser.add_argument('--sheet-name', required=True, help='Sheet/tab name')
    parser.add_argument('--sheet-id', type=int, default=0, help='Sheet ID (default: 0)')
    parser.add_argument('--data', help='Path to JSON file with test cases array')
    parser.add_argument('--stdin', action='store_true', help='Read test cases JSON from stdin')
    parser.add_argument('--column-mapping', required=True,
                        help='JSON string or file path: {"testSuiteName":0,"testCaseName":3,...}')
    parser.add_argument('--total-columns', type=int, default=13,
                        help='Total number of columns (default: 13)')
    parser.add_argument('--data-start-row', type=int, default=2,
                        help='Row number where data starts (default: 2)')
    parser.add_argument('--credentials', help='Path to service account credentials.json')
    parser.add_argument('--no-format', action='store_true',
                        help='Skip formatting step (faster)')
    args = parser.parse_args()

    # Load test cases
    if args.stdin:
        test_cases = json.load(sys.stdin)
    elif args.data:
        with open(args.data, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
    else:
        print(json.dumps({"error": "Provide --data <file> or --stdin"}))
        sys.exit(1)

    if not isinstance(test_cases, list):
        print(json.dumps({"error": "Input must be a JSON array of test case objects"}))
        sys.exit(1)

    # Load column mapping
    col_map_arg = args.column_mapping
    if os.path.isfile(col_map_arg):
        with open(col_map_arg, 'r', encoding='utf-8') as f:
            column_mapping = json.load(f)
    else:
        column_mapping = json.loads(col_map_arg)

    # Convert string keys to int values if needed
    column_mapping = {k: int(v) for k, v in column_mapping.items()}

    credentials_path = find_credentials(args.credentials)
    if not credentials_path:
        print(json.dumps({
            "error": "credentials.json not found. Provide --credentials or place credentials.json in project root."
        }))
        sys.exit(1)

    try:
        sheets_service = build_sheets_service(credentials_path)

        total_columns = args.total_columns
        last_col = col_index_to_letter(total_columns - 1)

        # Build rows array
        rows, suite_row_indices, test_case_count = build_rows(
            test_cases, column_mapping, total_columns
        )

        if not rows:
            print(json.dumps({
                "success": True,
                "rowsWritten": 0,
                "suiteCount": 0,
                "testCaseCount": 0,
                "updatedRange": None
            }))
            return

        # Append data to sheet
        updated_range = append_rows(
            sheets_service, args.spreadsheet_id,
            args.sheet_name, last_col, rows, args.data_start_row
        )

        # Apply formatting
        if not args.no_format and updated_range:
            start_row = parse_start_row(updated_range)
            if start_row is not None:
                format_requests = build_format_requests(
                    rows, suite_row_indices, start_row,
                    args.sheet_id, total_columns
                )
                apply_formatting(sheets_service, args.spreadsheet_id, format_requests)

        print(json.dumps({
            "success": True,
            "rowsWritten": len(rows),
            "suiteCount": len(suite_row_indices),
            "testCaseCount": test_case_count,
            "updatedRange": updated_range,
            "spreadsheetUrl": f"https://docs.google.com/spreadsheets/d/{args.spreadsheet_id}/edit"
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
