#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upload_template.py - Upload excel_template/template.xlsx to Google Drive as a new Google Sheets

Always uploads a fresh copy — does NOT reuse existing files on Drive.
The template structure is whatever the project placed in excel_template/template.xlsx.

Usage:
  python upload_template.py --name "TC_API_Lay_danh_sach_180326"
  python upload_template.py --name "TC_API_Lay_danh_sach_180326" --template excel_template/template.xlsx
  python upload_template.py --name "TC_API_Lay_danh_sach_180326" --credentials path/to/credentials.json

Output (JSON):
  {
    "spreadsheetId": "1abc...",
    "webViewLink": "https://docs.google.com/spreadsheets/d/1abc.../edit",
    "name": "TC_API_Lay_danh_sach_180326"
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
    from googleapiclient.http import MediaFileUpload
except ImportError:
    print(json.dumps({"error": "Missing dependencies. Run: pip install google-api-python-client google-auth"}))
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
]

GOOGLE_SHEETS_MIME = 'application/vnd.google-apps.spreadsheet'
DEFAULT_TEMPLATE = 'excel_template/template.xlsx'


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


def build_drive_service(credentials_path):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)


def upload_as_sheets(drive_service, template_path, name):
    """Upload .xlsx file to Drive, converting to Google Sheets format. Always creates new file."""
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    media = MediaFileUpload(
        template_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        resumable=False
    )
    file_metadata = {
        'name': name,
        'mimeType': GOOGLE_SHEETS_MIME,  # converts .xlsx → Google Sheets on upload
    }
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,name,mimeType,webViewLink'
    ).execute()
    return uploaded


def wait_for_processing(drive_service, file_id, retries=5, delay=2):
    """Wait until Drive finishes converting the file to Google Sheets format."""
    for attempt in range(retries):
        file_info = drive_service.files().get(
            fileId=file_id,
            fields='id,name,mimeType,webViewLink'
        ).execute()
        if file_info.get('mimeType') == GOOGLE_SHEETS_MIME:
            return file_info
        time.sleep(delay)
    raise RuntimeError(
        f"Upload processing timeout: mimeType is still '{file_info.get('mimeType')}' "
        f"after {retries} retries. Expected '{GOOGLE_SHEETS_MIME}'."
    )


def main():
    parser = argparse.ArgumentParser(
        description='Upload excel_template/template.xlsx to Google Drive as a new Google Sheets'
    )
    parser.add_argument('--name', required=True,
                        help='Name for the new spreadsheet (e.g. TC_API_Lay_danh_sach_180326)')
    parser.add_argument('--template', default=DEFAULT_TEMPLATE,
                        help=f'Path to .xlsx template file (default: {DEFAULT_TEMPLATE})')
    parser.add_argument('--credentials', help='Path to service account credentials.json')
    args = parser.parse_args()

    credentials_path = find_credentials(args.credentials)
    if not credentials_path:
        print(json.dumps({
            "error": "credentials.json not found. Provide --credentials or place credentials.json in project root."
        }))
        sys.exit(1)

    try:
        drive_service = build_drive_service(credentials_path)

        # Always upload fresh — never reuse existing Drive files
        uploaded = upload_as_sheets(drive_service, args.template, args.name)

        # Wait for Drive to finish converting .xlsx → Google Sheets
        time.sleep(2)
        validated = wait_for_processing(drive_service, uploaded['id'])

        print(json.dumps({
            "spreadsheetId": validated['id'],
            "webViewLink": validated.get('webViewLink', ''),
            "name": validated['name'],
        }, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
