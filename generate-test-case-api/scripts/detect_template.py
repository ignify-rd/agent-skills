#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detect_template.py - Detect column structure from an uploaded Google Sheets spreadsheet

Reads the actual header rows from the spreadsheet and builds a dynamic column mapping.
No hardcoded project types — works with any template structure.

Usage:
  python detect_template.py --spreadsheet-id 1abc...
  python detect_template.py --spreadsheet-id 1abc... --credentials path/to/credentials.json

Output (JSON):
  {
    "spreadsheetId": "1abc...",
    "webViewLink": "https://docs.google.com/spreadsheets/d/1abc.../edit",
    "sheetName": "TestCases",
    "sheetId": 0,
    "columnMapping": {
      "testSuiteName": 0,
      "details": 1,
      "externalId": 2,
      "testCaseName": 3,
      "summary": 4,
      "preConditions": 5,
      "steps": 6,
      "expectedResults": 7,
      "result": 11,
      "note": 12
    },
    "totalColumns": 13,
    "lastCol": "M",
    "headerRow": 2,
    "dataStartRow": 3
  }

Header detection strategy:
  - Scans rows 1-20 to find the row with the most non-empty cells matching known column labels
  - dataStartRow = headerRow + 1, unless the next row also looks like a header (merged group headers)
  - Fully dynamic: works with any template the project provides

Requirements:
  pip install google-api-python-client google-auth
"""

import argparse
import json
import os
import sys
import time

# Import shared auth module (same directory)
sys.path.insert(0, os.path.dirname(__file__))
try:
    from google_auth import find_credentials as _find_creds, build_services as _build_svc
    _USE_OAUTH = True
except ImportError:
    _USE_OAUTH = False

try:
    from googleapiclient.discovery import build
except ImportError:
    print(json.dumps({"error": "Missing dependencies. Run: pip install google-api-python-client google-auth"}))
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
]

# Known column header labels → normalized JSON key
# Covers all known template variants. Detection is purely label-based.
LABEL_TO_KEY = {
    # Common across all templates
    'name':                         '__name__',     # special: position-dependent (see build_column_mapping)
    'details':                      'details',
    'external id':                  'externalId',
    'summary':                      'summary',
    'preconditions':                'preConditions',
    'pre-conditions':               'preConditions',
    'step':                         'steps',
    'test steps':                   'testSteps',
    'expected result':              'expectedResults',
    'spec title':                   'specTitle',
    'document id':                  'documentId',
    'duration':                     'duration',
    'estimated exec. duration':     'duration',
    'estimated exec.\nduration':    'duration',
    'result':                       'result',
    'test results':                 'testResults',
    'note':                         'note',
    'notes':                        'note',
    'status':                       'status',
    'executiontype':                'executionType',
    'importance':                   'priority',
    'keywords':                     'keywords',
    'number of attachments':        'attachments',
    'actual result':                'actualResult',
    'stepexec\n type':              'stepExecType',
    'stepexectype':                 'stepExecType',
    # HOME-specific
    'testcase lv1':                 'testcaseLV1',
    'testcase lv2':                 'testcaseLV2',
    'testcase lv3':                 'testcaseLV3',
    # LENDING-specific
    'test case id':                 'testCaseId',
    'test case title':              'testCaseTitle',
    'test case title\n(tên testcase)': 'testCaseTitle',
    'pre-conditions\n(điều kiện bắt buộc)': 'preConditions',
    'test steps\n(các bước thực hiện)': 'testSteps',
    'expected result\n(kết quả mong muốn)': 'expectedResults',
    'priority':                     'priority',
    'bugid':                        'bugId',
    # BIDV iBank2.0 format
    'id':                           'externalId',
    'name testcase':                'testCaseName',
    'name testcase ':               'testCaseName',
    'mã lỗi':                       'bugId',
}

# Labels that are group/section headers (row 1 of multi-row headers) — not column headers
GROUP_HEADER_LABELS = {
    'test suite', 'test case', 'attachments', 'custom fields',
    'steps', 'coverage', 'time management', 'result',
    'kịch bản kiểm thử *', 'tên màn hình/tên chức năng',
}


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


def build_services(credentials_path):
    if _USE_OAUTH:
        return _build_svc(credentials_path)
    # Legacy fallback: service account
    from google.oauth2 import service_account
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    drive = build('drive', 'v3', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds)
    return drive, sheets


def get_sheet_info(sheets_service, spreadsheet_id):
    """Get first sheet name and sheetId."""
    meta = sheets_service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields='sheets.properties(sheetId,title)'
    ).execute()
    sheets = meta.get('sheets', [])
    if not sheets:
        raise RuntimeError('No sheets found in spreadsheet')
    first = sheets[0]['properties']
    return first['title'], first['sheetId']


def read_top_rows(sheets_service, spreadsheet_id, sheet_name, max_rows=20):
    """Read first max_rows rows to scan for header row."""
    range_str = f"'{sheet_name}'!A1:ZZ{max_rows}"
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_str,
        valueRenderOption='FORMATTED_VALUE'
    ).execute()
    return result.get('values', [])


def score_row_as_header(row):
    """
    Score how likely a row is the column header row.
    Higher = more likely to be the real header row.
    """
    if not row:
        return 0

    score = 0
    non_empty = 0
    matched_labels = 0

    for cell in row:
        label = str(cell).strip().lower()
        if not label:
            continue
        non_empty += 1

        # Penalize group header labels
        if label in GROUP_HEADER_LABELS:
            score -= 2
            continue

        # Reward known column labels
        if label in LABEL_TO_KEY or label == 'name':
            matched_labels += 1
            score += 3

        # Reward generic column-like labels
        score += 1

    # Bonus for density of matched labels
    if non_empty > 0:
        score += int((matched_labels / non_empty) * 10)

    return score


def find_header_row(rows):
    """
    Find the best header row index (1-based) by scoring each row.
    Returns (header_row_1based, data_start_row_1based).
    """
    if not rows:
        return 1, 2

    best_score = -1
    best_idx = 0  # 0-based

    for i, row in enumerate(rows):
        score = score_row_as_header(row)
        if score > best_score:
            best_score = score
            best_idx = i

    header_row = best_idx + 1  # convert to 1-based

    # dataStartRow: skip at most 1 non-empty metadata row immediately after header
    # Only skip if the row has ≤2 non-empty cells with low score (e.g. "Màn hình test:", "Function")
    # Empty rows are NOT skipped — they become the first data row
    data_start = header_row + 1
    next_idx = best_idx + 1  # 0-based
    if next_idx < len(rows):
        next_row = rows[next_idx]
        non_empty = [c for c in next_row if str(c).strip()]
        score = score_row_as_header(next_row)
        if 1 <= len(non_empty) <= 2 and score <= 2:
            # Single-cell metadata row (e.g. HOME row17, LENDING row14) — skip it
            data_start = header_row + 2

    return header_row, data_start


def build_column_mapping(rows, header_row_1based):
    """
    Build column mapping from the header row.
    Returns dict: { jsonKey: colIndex (0-based) }
    """
    if not rows or header_row_1based > len(rows):
        return {}

    row = rows[header_row_1based - 1]
    mapping = {}
    name_count = 0

    for col_idx, cell in enumerate(row):
        label = str(cell).strip().lower()
        if not label:
            continue

        # 'name' appears multiple times: first = testSuiteName, second = testCaseName.
        # Exception: if externalId is already mapped at a lower column index, this
        # 'Name' is the test case name (BIDV frontend format: External ID | Name | ...)
        if label == 'name':
            name_count += 1
            ext_id_col = mapping.get('externalId')
            if name_count == 1 and (ext_id_col is None or col_idx < ext_id_col):
                key = 'testSuiteName'
            else:
                key = 'testCaseName'
            if key not in mapping:
                mapping[key] = col_idx
            continue

        key = LABEL_TO_KEY.get(label)
        if key and key != '__name__' and key not in mapping:
            mapping[key] = col_idx

    return mapping


def col_index_to_letter(index):
    """Convert 0-based column index to letter (0→A, 25→Z, 26→AA)."""
    result = ''
    index += 1
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def clear_data_rows(sheets_service, spreadsheet_id, sheet_name, data_start_row, last_col):
    """Clear sample/formula rows from template, keeping headers intact."""
    range_str = f"'{sheet_name}'!A{data_start_row}:{last_col}"
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_str
    ).execute()


def main():
    parser = argparse.ArgumentParser(
        description='Detect column structure from an uploaded Google Sheets spreadsheet'
    )
    parser.add_argument('--spreadsheet-id', required=True,
                        help='Google Sheets spreadsheet ID (from upload_template.py output)')
    parser.add_argument('--credentials', help='Path to service account credentials.json')
    parser.add_argument('--no-clear', action='store_true',
                        help='Skip clearing sample data rows (keep template data intact)')
    args = parser.parse_args()

    credentials_path = find_credentials(args.credentials)
    if not credentials_path:
        print(json.dumps({
            "error": "credentials.json not found. Provide --credentials or place credentials.json in project root."
        }))
        sys.exit(1)

    try:
        drive_service, sheets_service = build_services(credentials_path)

        # Get sheet name and sheetId
        sheet_name, sheet_id = get_sheet_info(sheets_service, args.spreadsheet_id)

        # Get webViewLink
        file_info = drive_service.files().get(
            fileId=args.spreadsheet_id,
            fields='id,webViewLink'
        ).execute()
        web_view_link = file_info.get('webViewLink', '')

        # Read top rows to detect header structure
        rows = read_top_rows(sheets_service, args.spreadsheet_id, sheet_name)

        # Find header row dynamically
        header_row, data_start_row = find_header_row(rows)

        # Build column mapping from detected header row
        column_mapping = build_column_mapping(rows, header_row)

        # Determine total columns from header row
        if rows and header_row <= len(rows):
            header_cells = rows[header_row - 1]
            # Count up to last non-empty cell
            total_columns = len(header_cells)
            while total_columns > 0 and not str(header_cells[total_columns - 1]).strip():
                total_columns -= 1
            if total_columns == 0:
                total_columns = len(header_cells)
        else:
            total_columns = max(column_mapping.values()) + 1 if column_mapping else 13

        last_col = col_index_to_letter(total_columns - 1)

        # Clear sample data rows (keep headers)
        if not args.no_clear and data_start_row <= 1000:
            clear_data_rows(sheets_service, args.spreadsheet_id, sheet_name, data_start_row, last_col)

        print(json.dumps({
            "spreadsheetId": args.spreadsheet_id,
            "webViewLink": web_view_link,
            "sheetName": sheet_name,
            "sheetId": sheet_id,
            "columnMapping": column_mapping,
            "totalColumns": total_columns,
            "lastCol": last_col,
            "headerRow": header_row,
            "dataStartRow": data_start_row,
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
