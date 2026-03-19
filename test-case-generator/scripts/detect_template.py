#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detect_template.py - Copy template from Drive and detect column structure

Usage:
  # Copy template and detect structure
  python detect_template.py --template-id 1abc... --name "TC_API_Test_180326" --project-type API_TEST

  # Detect structure from existing spreadsheet (no copy)
  python detect_template.py --spreadsheet-id 1xyz... --project-type API_TEST

  # Full flow: copy + detect
  python detect_template.py --template-id 1abc... --name "TC_API_Test" --project-type API_TEST --credentials creds.json

Output (JSON):
  {
    "spreadsheetId": "1xyz...",
    "webViewLink": "https://docs.google.com/spreadsheets/d/1xyz.../edit",
    "sheetName": "TestCases",
    "sheetId": 0,
    "columnMapping": {
      "testSuiteName": 0,
      "details": 1,
      "externalId": 2,
      "testCaseName": 3,
      ...
    },
    "totalColumns": 13,
    "lastCol": "M",
    "headerRow": 1,
    "dataStartRow": 2
  }

Requirements:
  pip install google-api-python-client google-auth
"""

import argparse
import json
import os
import sys
import time

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print(json.dumps({"error": "Missing dependencies. Run: pip install google-api-python-client google-auth"}))
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
]

# Fallback dataStartRow per project type (if header detection fails)
FALLBACK_DATA_START = {
    'API_TEST':   2,
    'FEE_ENGINE': 3,
    'HOME':       18,
    'LENDING':    14,
}

# Fallback header row per project type
FALLBACK_HEADER_ROW = {
    'API_TEST':   1,
    'FEE_ENGINE': 2,
    'HOME':       16,
    'LENDING':    13,
}

# Map header label (normalized) → JSON key
# When the same label appears multiple times (e.g. "name"), position determines key
LABEL_TO_KEY = {
    'test suite name':              'testSuiteName',
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
    'result':                       'result',
    'test results':                 'testResults',
    'note':                         'note',
    'notes':                        'note',
    # HOME-specific
    'testcase lv1':                 'testcaseLV1',
    'testcase lv2':                 'testcaseLV2',
    'testcase lv3':                 'testcaseLV3',
    'status':                       'status',
    'executiontype':                'executionType',
    'importance':                   'priority',
    'keywords':                     'keywords',
    'number of attachments':        'attachments',
    'actual result':                'actualResult',
    'stepexectype':                 'stepExecType',
    # LENDING-specific
    'test case id':                 'testCaseId',
    'test case title':              'testCaseTitle',
    'priority':                     'priority',
    'bugid':                        'bugId',
}

# Column index → letter (0-based)
def col_index_to_letter(index):
    result = ''
    index += 1  # 1-based
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def find_credentials(provided_path=None):
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
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    drive = build('drive', 'v3', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds)
    return drive, sheets


def copy_template(drive_service, template_id, name):
    """Copy template file in Drive, returns new spreadsheet metadata."""
    copied = drive_service.files().copy(
        fileId=template_id,
        body={'name': name},
        fields='id,name,webViewLink'
    ).execute()
    return copied


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


def read_header_area(sheets_service, spreadsheet_id, sheet_name, project_type):
    """Read header rows from spreadsheet to detect column structure."""
    header_row = FALLBACK_HEADER_ROW.get(project_type, 1)
    data_start = FALLBACK_DATA_START.get(project_type, 2)
    last_col = 'U'  # Read up to col U (21 cols) to cover all templates

    range_str = f"'{sheet_name}'!A1:{last_col}{data_start}"
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_str,
        valueRenderOption='FORMATTED_VALUE'
    ).execute()
    return result.get('values', []), header_row, data_start


def build_column_mapping(header_rows, header_row_index):
    """
    Build column mapping from header row values.
    header_row_index: 1-based row number of the actual header row.
    Returns dict: { jsonKey: colIndex (0-based) }
    """
    if not header_rows or header_row_index > len(header_rows):
        return {}

    row = header_rows[header_row_index - 1]  # convert to 0-based
    mapping = {}
    name_count = 0  # track how many "name" columns we've seen

    for col_idx, cell in enumerate(row):
        label = str(cell).strip().lower()
        if not label:
            continue

        # Special case: "name" appears twice in most templates
        # First "name" (col A) = testSuiteName, second "name" = testCaseName
        if label == 'name':
            name_count += 1
            if name_count == 1:
                mapping['testSuiteName'] = col_idx
            else:
                mapping['testCaseName'] = col_idx
            continue

        key = LABEL_TO_KEY.get(label)
        if key and key not in mapping:
            mapping[key] = col_idx

    return mapping


def clear_sample_data(sheets_service, spreadsheet_id, sheet_name, data_start_row, last_col):
    """Clear sample data rows from template (keep headers)."""
    range_str = f"'{sheet_name}'!A{data_start_row}:{last_col}"
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_str
    ).execute()


def main():
    parser = argparse.ArgumentParser(description='Copy template and detect column structure')
    parser.add_argument('--template-id', help='Google Drive file ID of the template to copy')
    parser.add_argument('--spreadsheet-id', help='Existing spreadsheet ID (skip copy step)')
    parser.add_argument('--name', help='Name for the new spreadsheet (required if --template-id)')
    parser.add_argument('--project-type', required=True,
                        choices=['API_TEST', 'HOME', 'FEE_ENGINE', 'LENDING'],
                        help='Project type')
    parser.add_argument('--credentials', help='Path to service account credentials.json')
    parser.add_argument('--no-clear', action='store_true',
                        help='Skip clearing sample data from template')
    args = parser.parse_args()

    if not args.template_id and not args.spreadsheet_id:
        print(json.dumps({"error": "Provide either --template-id or --spreadsheet-id"}))
        sys.exit(1)

    if args.template_id and not args.name:
        print(json.dumps({"error": "--name is required when using --template-id"}))
        sys.exit(1)

    credentials_path = find_credentials(args.credentials)
    if not credentials_path:
        print(json.dumps({
            "error": "credentials.json not found. Provide --credentials or place credentials.json in project root."
        }))
        sys.exit(1)

    try:
        drive_service, sheets_service = build_services(credentials_path)

        # Step 1: Copy template or use existing spreadsheet
        if args.template_id:
            copied = copy_template(drive_service, args.template_id, args.name)
            spreadsheet_id = copied['id']
            web_view_link = copied.get('webViewLink', '')
            # Wait for Drive to finish processing
            time.sleep(2)
        else:
            spreadsheet_id = args.spreadsheet_id
            file_info = drive_service.files().get(
                fileId=spreadsheet_id,
                fields='id,webViewLink'
            ).execute()
            web_view_link = file_info.get('webViewLink', '')

        # Step 2: Get sheet name and sheetId
        sheet_name, sheet_id = get_sheet_info(sheets_service, spreadsheet_id)

        # Step 3: Read header area and detect column structure
        header_rows, header_row, data_start_row = read_header_area(
            sheets_service, spreadsheet_id, sheet_name, args.project_type
        )

        column_mapping = build_column_mapping(header_rows, header_row)

        # Determine total columns from header row
        if header_rows and header_row <= len(header_rows):
            total_columns = len(header_rows[header_row - 1])
        else:
            total_columns = max(column_mapping.values()) + 1 if column_mapping else 13

        last_col = col_index_to_letter(total_columns - 1)

        # Step 4: Clear sample data (keep headers)
        if not args.no_clear:
            clear_sample_data(sheets_service, spreadsheet_id, sheet_name, data_start_row, last_col)

        print(json.dumps({
            "spreadsheetId": spreadsheet_id,
            "webViewLink": web_view_link,
            "sheetName": sheet_name,
            "sheetId": sheet_id,
            "columnMapping": column_mapping,
            "totalColumns": total_columns,
            "lastCol": last_col,
            "headerRow": header_row,
            "dataStartRow": data_start_row
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
