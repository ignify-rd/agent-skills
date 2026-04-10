#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upload_gsheet.py - Upload test cases to Google Sheets with full formatting

Reads structure.json (template structure) and test-cases.json (test case data),
creates a new Google Sheets spreadsheet with template headers, formatting,
merged cells, and test case data.

Uses OAuth Desktop App flow (not Service Account).
After creation, shares the file with anyone as editor.

Usage:
  python upload_gsheet.py <test-case-name>
  python upload_gsheet.py <test-case-name> --structure excel_template/structure.json
  python upload_gsheet.py <test-case-name> --credentials credentials.json
  python upload_gsheet.py <test-case-name> --project-root /path/to/project
  python upload_gsheet.py <test-case-name> --title "Custom Title"

Output (JSON):
  {
    "success": true,
    "spreadsheetId": "1abc...",
    "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/1abc.../edit",
    "title": "TC_API_Ten_chuc_nang_200326",
    "rowsWritten": 75,
    "suiteCount": 5,
    "testCaseCount": 70
  }

Requirements:
  pip install google-auth-oauthlib google-auth google-api-python-client
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Import shared auth module (same directory)
sys.path.insert(0, os.path.dirname(__file__))
try:
    from google_auth import find_credentials, build_services, get_credentials
except ImportError:
    print(json.dumps({"error": "Cannot import google_auth.py. Ensure it is in the same directory."}))
    sys.exit(1)

try:
    from googleapiclient.discovery import build
except ImportError:
    print(json.dumps({"error": "Missing dependencies. Run: pip install google-api-python-client google-auth google-auth-oauthlib"}))
    sys.exit(1)


# ============ PROJECT ROOT ============
_PROJECT_MARKERS = ("catalog", "AGENTS.md", "excel_template")


def find_project_root(explicit_path=None):
    """Find project root by walking up from CWD."""
    if explicit_path:
        p = Path(explicit_path)
        if p.exists():
            return p
    current = Path.cwd()
    for _ in range(10):
        if any((current / m).exists() for m in _PROJECT_MARKERS):
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return Path.cwd()


# ============ COLOR CONVERSION ============
def argb_to_rgb(argb):
    """Convert ARGB hex string (e.g. 'FF4472C4') to Google Sheets RGB dict."""
    if not argb or len(argb) < 6:
        return None
    # Strip alpha if present
    hex_str = argb[-6:]  # last 6 chars = RGB
    try:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return {'red': r, 'green': g, 'blue': b}
    except (ValueError, IndexError):
        return None


def border_style_to_sheets(style):
    """Convert openpyxl border style to Google Sheets border style."""
    mapping = {
        'thin': 'SOLID',
        'medium': 'SOLID_MEDIUM',
        'thick': 'SOLID_THICK',
        'dashed': 'DASHED',
        'dotted': 'DOTTED',
        'double': 'DOUBLE',
        'hair': 'SOLID',
    }
    return mapping.get(style, 'SOLID')


# ============ TEMPLATE HEADER WRITING ============
def build_header_requests(structure, sheet_id):
    """Build batchUpdate requests to write template header rows with formatting."""
    requests = []
    template_rows = structure.get('templateRows', [])
    total_columns = structure.get('totalColumns', 13)

    for row_data in template_rows:
        row_idx = row_data['rowNumber'] - 1  # 0-based for API

        # Set row height if specified
        if 'height' in row_data:
            requests.append({
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': row_idx,
                        'endIndex': row_idx + 1,
                    },
                    'properties': {'pixelSize': int(row_data['height'] * 1.33)},  # pt to px approx
                    'fields': 'pixelSize',
                }
            })

        # Build cell data for the row
        row_cells = []
        for cell_data in row_data.get('cells', []):
            cell = {}

            # Value
            value = cell_data.get('value', '')
            formula = cell_data.get('formula')
            if formula:
                cell['userEnteredValue'] = {'formulaValue': f'={formula}'}
            elif value:
                cell['userEnteredValue'] = {'stringValue': str(value)}
            else:
                cell['userEnteredValue'] = {'stringValue': ''}

            # Format
            fmt = {}

            # Background color
            bg = cell_data.get('backgroundColor')
            if bg:
                rgb = argb_to_rgb(bg)
                if rgb:
                    fmt['backgroundColor'] = rgb

            # Font
            font_data = cell_data.get('font', {})
            if font_data:
                text_fmt = {}
                if font_data.get('bold'):
                    text_fmt['bold'] = True
                if font_data.get('italic'):
                    text_fmt['italic'] = True
                if font_data.get('size'):
                    text_fmt['fontSize'] = font_data['size']
                font_color = font_data.get('color')
                if font_color:
                    rgb = argb_to_rgb(font_color)
                    if rgb:
                        text_fmt['foregroundColor'] = rgb
                if font_data.get('name'):
                    text_fmt['fontFamily'] = font_data['name']
                if text_fmt:
                    fmt['textFormat'] = text_fmt

            # Alignment
            align_data = cell_data.get('alignment', {})
            if align_data:
                h = align_data.get('horizontal', '').upper()
                if h in ('LEFT', 'CENTER', 'RIGHT'):
                    fmt['horizontalAlignment'] = h
                v = align_data.get('vertical', '').upper()
                if v == 'MIDDLE':
                    v = 'MIDDLE'
                if v in ('TOP', 'MIDDLE', 'BOTTOM'):
                    fmt['verticalAlignment'] = v
                if align_data.get('wrapText'):
                    fmt['wrapStrategy'] = 'WRAP'

            # Border
            border_data = cell_data.get('border', {})
            if border_data:
                borders = {}
                for side_name in ('top', 'bottom', 'left', 'right'):
                    side = border_data.get(side_name)
                    if side:
                        border_entry = {'style': border_style_to_sheets(side.get('style', 'thin'))}
                        color = side.get('color')
                        if color:
                            rgb = argb_to_rgb(color)
                            if rgb:
                                border_entry['color'] = rgb
                        borders[side_name] = border_entry
                if borders:
                    fmt['borders'] = borders

            if fmt:
                cell['userEnteredFormat'] = fmt

            row_cells.append(cell)

        # updateCells for this row
        if row_cells:
            requests.append({
                'updateCells': {
                    'rows': [{'values': row_cells}],
                    'start': {
                        'sheetId': sheet_id,
                        'rowIndex': row_idx,
                        'columnIndex': 0,
                    },
                    'fields': 'userEnteredValue,userEnteredFormat',
                }
            })

    # Apply merged cells (clamp to grid limits)
    for mc in structure.get('mergedCells', []):
        end_col = min(mc['endCol'], total_columns)
        start_col = mc['startCol'] - 1
        if start_col >= total_columns:
            continue  # skip merges outside grid
        requests.append({
            'mergeCells': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': mc['startRow'] - 1,
                    'endRowIndex': mc['endRow'],
                    'startColumnIndex': start_col,
                    'endColumnIndex': end_col,
                },
                'mergeType': 'MERGE_ALL',
            }
        })

    # Set column widths
    column_widths = structure.get('columnWidths', [])
    for col_idx, width in enumerate(column_widths):
        pixel_size = max(int(width * 7), 30)  # Excel width units to pixels approx
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': col_idx,
                    'endIndex': col_idx + 1,
                },
                'properties': {'pixelSize': pixel_size},
                'fields': 'pixelSize',
            }
        })

    return requests


# ============ TEST CASE DATA (reused from upload_to_sheet.py) ============

# 5 main suite names (any testSuiteName matching these → green header)
MAIN_SUITE_NAMES = {
    'kiểm tra các case common',
    'kiểm tra giao diện chung',
    'kiểm tra phân quyền',
    'kiểm tra validate',
    'kiểm tra luồng chính',
    'kiểm tra timeout',
    'kiểm tra chức năng',
    'kiểm tra lưới dữ liệu',
    'kiểm tra phân trang',
}

def _is_main_suite(suite_name: str) -> bool:
    """Return True if suite_name is one of the 5 main suites (green header)."""
    return suite_name.strip().lower() in MAIN_SUITE_NAMES

# Suite header formatting: light green #DAEAD0 (for main suites)
SUITE_HEADER_FORMAT = {
    'backgroundColor': {'red': 0.855, 'green': 0.918, 'blue': 0.816},
    'textFormat': {
        'foregroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0},
        'bold': True,
        'fontSize': 11,
    },
    'horizontalAlignment': 'LEFT',
    'verticalAlignment': 'TOP',
    'wrapStrategy': 'WRAP',
    'borders': {
        'top':    {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'bottom': {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'left':   {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'right':  {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
    },
}

# Field sub-suite header formatting: light gray #E8E8E8 (for "Kiểm tra trường X")
FIELD_SUITE_HEADER_FORMAT = {
    'backgroundColor': {'red': 0.910, 'green': 0.910, 'blue': 0.910},
    'textFormat': {
        'foregroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
        'bold': True,
        'fontSize': 10,
    },
    'horizontalAlignment': 'LEFT',
    'verticalAlignment': 'TOP',
    'wrapStrategy': 'WRAP',
    'borders': {
        'top':    {'style': 'SOLID', 'color': {'red': 0.7, 'green': 0.7, 'blue': 0.7}},
        'bottom': {'style': 'SOLID', 'color': {'red': 0.7, 'green': 0.7, 'blue': 0.7}},
        'left':   {'style': 'SOLID', 'color': {'red': 0.7, 'green': 0.7, 'blue': 0.7}},
        'right':  {'style': 'SOLID', 'color': {'red': 0.7, 'green': 0.7, 'blue': 0.7}},
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
    'verticalAlignment': 'TOP',
    'wrapStrategy': 'WRAP',
    'borders': {
        'top':    {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'bottom': {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'left':   {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
        'right':  {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
    },
}

FORMAT_FIELDS = 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy,borders)'


def col_index_to_letter(index):
    """Convert 0-based column index to letter."""
    result = ''
    index += 1
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


VALIDATE_PARENT = 'Kiểm tra validate'


def _is_field_subsuite(suite_name: str) -> bool:
    """Return True if this is a per-field sub-suite inside 'Kiểm tra validate'."""
    return not _is_main_suite(suite_name) and bool(suite_name.strip())


def _append_suite_row(rows, suite_row_indices, suite_names_by_index, suite_name, total_columns):
    """Helper: append one suite header row to rows and update index maps."""
    row_idx = len(rows)
    suite_row_indices.append(row_idx)
    suite_names_by_index[row_idx] = suite_name
    suite_row = [''] * total_columns
    suite_row[0] = suite_name
    rows.append(suite_row)


def build_rows(test_cases, column_mapping, total_columns):
    """Build 2D array from test cases using column mapping.

    Guarantees:
    - Each unique testSuiteName appears as a header row only ONCE (dedup by name).
    - Field sub-suites (not in MAIN_SUITE_NAMES) automatically get a green
      'Kiểm tra validate' parent header inserted before the first field sub-suite
      in each validate block.
    - Test cases with the same testSuiteName that are non-contiguous are
      grouped together: the suite header is NOT repeated; cases are placed
      under the EXISTING header.

    Returns (rows, suite_row_indices, test_case_count, suite_names_by_index).
    suite_names_by_index: dict mapping row_index → suite_name string.
    """
    # Step 1: pre-group test cases by suite order, preserving first-seen order
    # This prevents duplicate headers caused by non-contiguous same-suite cases.
    from collections import OrderedDict
    suite_groups: OrderedDict = OrderedDict()  # suite_name → [tc, ...]
    for tc in test_cases:
        suite_name = tc.get('testSuiteName', '').strip()
        if suite_name not in suite_groups:
            suite_groups[suite_name] = []
        suite_groups[suite_name].append(tc)

    # Build LV1 lookup: testSuiteName → testcaseLV1 (first tc wins)
    suite_lv1_map: dict = {}
    for tc in test_cases:
        sn = tc.get('testSuiteName', '').strip()
        lv1 = tc.get('testcaseLV1', '').strip()
        if sn and lv1 and sn not in suite_lv1_map:
            suite_lv1_map[sn] = lv1

    # Step 2: For each non-main sub-suite, insert its LV1 parent header immediately
    # before the first occurrence of that sub-suite (if not already present).
    # This handles BOTH "Kiểm tra validate" and "Kiểm tra chức năng" parent headers.
    ordered_suites = list(suite_groups.keys())
    already_inserted: set = set(ordered_suites)  # tracks what's already in the list
    i = 0
    while i < len(ordered_suites):
        suite = ordered_suites[i]
        if not _is_field_subsuite(suite):
            i += 1
            continue
        # Determine parent LV1 for this sub-suite
        lv1 = suite_lv1_map.get(suite, '')
        # Fallback: if no LV1 info, assume it belongs to validate (legacy behavior)
        if not lv1:
            lv1 = VALIDATE_PARENT
        if lv1 not in already_inserted:
            ordered_suites.insert(i, lv1)
            suite_groups[lv1] = []  # header-only row (no test cases)
            already_inserted.add(lv1)
            i += 2  # skip past the inserted parent AND the current sub-suite
        else:
            i += 1

    # Step 3: build rows from ordered groups
    rows = []
    suite_row_indices = []
    suite_names_by_index = {}  # row_index → suite_name
    test_case_count = 0

    def make_row(field_values):
        row = [''] * total_columns
        for key, value in field_values.items():
            col_idx = column_mapping.get(key)
            if col_idx is not None and col_idx < total_columns:
                row[col_idx] = str(value) if value is not None else ''
        return row

    for suite_name in ordered_suites:
        tcs = suite_groups.get(suite_name, [])

        # Emit suite header row
        _append_suite_row(rows, suite_row_indices, suite_names_by_index, suite_name, total_columns)

        for tc in tcs:
            # Normalize field aliases
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
                'priority':        tc.get('priority') or tc.get('importance', ''),
                'externalId':      tc.get('externalId', ''),
                'testCaseId':      tc.get('testCaseId', ''),
                'note':            tc.get('note', ''),
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
            })
            rows.append(tc_row)
            test_case_count += 1

    return rows, suite_row_indices, test_case_count, suite_names_by_index


def build_format_requests(rows, suite_row_indices, start_row, sheet_id, total_columns, suite_names_by_index=None):
    """Build formatting requests for suite headers and test case rows.
    suite_names_by_index: dict mapping row_index → suite_name (used for color selection).
    Main suites (5 fixed names) → green. Field sub-suites → gray.
    """
    requests = []
    suite_set = set(suite_row_indices)
    suite_names_by_index = suite_names_by_index or {}

    i = 0
    while i < len(rows):
        sheet_row = start_row + i
        row_index = sheet_row - 1  # 0-based

        if i in suite_set:
            # Determine color: green for main suites, gray for field sub-suites
            suite_name = suite_names_by_index.get(i, '')
            header_fmt = SUITE_HEADER_FORMAT if _is_main_suite(suite_name) else FIELD_SUITE_HEADER_FORMAT
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
                    'cell': {'userEnteredFormat': header_fmt},
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
            j = i
            while j < len(rows) and j not in suite_set:
                j += 1
            start_idx = start_row + i - 1
            end_idx = start_row + j - 1
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

    # Auto-resize rows
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


def parse_start_row(updated_range):
    """Extract start row from range string like 'Sheet1!A3:M77'."""
    import re
    match = re.search(r'!A(\d+)', updated_range or '')
    return int(match.group(1)) if match else None


# ============ MAIN ============
def main():
    parser = argparse.ArgumentParser(
        description='Upload test cases to Google Sheets with full formatting'
    )
    parser.add_argument('test_case_name', help='Test case folder name (contains test-cases.json)')
    parser.add_argument('--structure', help='Path to structure.json (default: excel_template/structure.json)')
    parser.add_argument('--data', help='Path to test-cases.json (default: <test-case-name>/test-cases.json)')
    parser.add_argument('--credentials', help='Path to credentials.json')
    parser.add_argument('--project-root', help='Explicit project root path')
    parser.add_argument('--sheet', help='Sheet index (1, 2, 3...) or sheet name to use (from structure.json if omitted)')
    parser.add_argument('--title', help='Custom spreadsheet title (auto-generated if omitted)')
    parser.add_argument('--no-share', action='store_true', help='Skip sharing the file')
    args = parser.parse_args()

    project_root = find_project_root(args.project_root)

    # Resolve paths
    structure_path = args.structure or str(project_root / 'excel_template' / 'structure.json')
    data_path = args.data or str(project_root / args.test_case_name / 'test-cases.json')
    credentials_path = find_credentials(args.credentials or str(project_root / 'credentials.json'))

    if not credentials_path:
        print(json.dumps({
            "error": "credentials.json not found. Place it at project root or use --credentials."
        }))
        sys.exit(1)

    # Load structure.json
    if not os.path.isfile(structure_path):
        print(json.dumps({
            "error": f"structure.json not found: {structure_path}. "
                     "Run: python extract_structure.py"
        }))
        sys.exit(1)

    with open(structure_path, 'r', encoding='utf-8') as f:
        structure = json.load(f)

    # Load test-cases.json
    if not os.path.isfile(data_path):
        print(json.dumps({
            "error": f"test-cases.json not found: {data_path}"
        }))
        sys.exit(1)

    with open(data_path, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)

    if not isinstance(test_cases, list):
        print(json.dumps({"error": "test-cases.json must contain a JSON array"}))
        sys.exit(1)

    try:
        # Authenticate
        drive_service, sheets_service = build_services(credentials_path)

        column_mapping = structure.get('columnMapping', {})
        # Ensure column_mapping values are ints
        column_mapping = {k: int(v) for k, v in column_mapping.items()}
        total_columns = structure.get('totalColumns', 13)
        data_start_row = structure.get('dataStartRow', 3)
        last_col = structure.get('lastCol', col_index_to_letter(total_columns - 1))
        # Resolve sheet name: --sheet overrides structure.json
        sheet_name = args.sheet if args.sheet else structure.get('sheetName', 'Sheet1')

        # Generate title
        date_str = datetime.now().strftime('%d%m%y')
        title = args.title or f"TC_{args.test_case_name}_{date_str}"

        # Step 1: Create blank spreadsheet
        spreadsheet_body = {
            'properties': {'title': title},
            'sheets': [{
                'properties': {
                    'sheetId': 0,
                    'title': sheet_name,
                    'gridProperties': {
                        'rowCount': max(len(test_cases) + data_start_row + 50, 200),
                        'columnCount': total_columns,
                    },
                }
            }],
        }
        created = sheets_service.spreadsheets().create(body=spreadsheet_body).execute()
        spreadsheet_id = created['spreadsheetId']
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

        # Step 2: Write template header rows with formatting
        header_requests = build_header_requests(structure, sheet_id=0)
        if header_requests:
            # Split into chunks of 100
            for i in range(0, len(header_requests), 100):
                chunk = header_requests[i:i + 100]
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': chunk}
                ).execute()

        # Step 3: Build test case rows
        rows, suite_row_indices, test_case_count, suite_names_by_index = build_rows(
            test_cases, column_mapping, total_columns
        )

        if not rows:
            print(json.dumps({
                "success": True,
                "spreadsheetId": spreadsheet_id,
                "spreadsheetUrl": spreadsheet_url,
                "title": title,
                "rowsWritten": 0,
                "suiteCount": 0,
                "testCaseCount": 0,
            }))
            return

        # Step 4: Append data rows
        range_str = f"'{sheet_name}'!A:{last_col}"
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

        # Step 5: Apply formatting
        if last_updated_range:
            start_row = parse_start_row(last_updated_range)
            if start_row is not None:
                format_requests = build_format_requests(
                    rows, suite_row_indices, start_row, 0, total_columns,
                    suite_names_by_index=suite_names_by_index,
                )
                for i in range(0, len(format_requests), 100):
                    chunk = format_requests[i:i + 100]
                    sheets_service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body={'requests': chunk}
                    ).execute()

        # Step 6: Share file (anyone with link = editor)
        if not args.no_share:
            try:
                drive_service.permissions().create(
                    fileId=spreadsheet_id,
                    body={
                        'type': 'anyone',
                        'role': 'writer',
                    },
                    sendNotificationEmail=False,
                ).execute()
            except Exception as share_err:
                # Non-fatal — still return the URL
                print(json.dumps({
                    "warning": f"File created but sharing failed: {share_err}"
                }), file=sys.stderr)

        print(json.dumps({
            "success": True,
            "spreadsheetId": spreadsheet_id,
            "spreadsheetUrl": spreadsheet_url,
            "title": title,
            "rowsWritten": len(rows),
            "suiteCount": len(suite_row_indices),
            "testCaseCount": test_case_count,
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
