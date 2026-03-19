#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upload_template.py - Upload Excel template to Google Drive as Google Sheets

Usage:
  python upload_template.py --template excel_template/template.xlsx --project-type API_TEST
  python upload_template.py --template excel_template/template.xlsx --project-type HOME
  python upload_template.py --credentials path/to/credentials.json --template ...

Output (JSON):
  { "templateFileId": "1abc...", "webViewLink": "https://docs.google.com/..." }

Steps:
  1. Search Drive for existing template (by name)
  2. If found → return existing templateFileId
  3. If not found → upload .xlsx, convert to Google Sheets format
  4. Validate upload (check mimeType)

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

TEMPLATE_NAMES = {
    'API_TEST':   'Test-Genie Template - API_TEST (DO NOT DELETE)',
    'HOME':       'Test-Genie Template - HOME (DO NOT DELETE)',
    'FEE_ENGINE': 'Test-Genie Template - FEE_ENGINE (DO NOT DELETE)',
    'LENDING':    'Test-Genie Template - LENDING (DO NOT DELETE)',
}

GOOGLE_SHEETS_MIME = 'application/vnd.google-apps.spreadsheet'


def find_credentials(provided_path=None):
    """Find credentials.json in common locations."""
    candidates = []
    if provided_path:
        candidates.append(provided_path)
    # Common locations
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


def search_existing_template(service, template_name):
    """Search for existing template in Drive by name."""
    query = (
        f"name = '{template_name}' "
        f"and mimeType = '{GOOGLE_SHEETS_MIME}' "
        f"and trashed = false"
    )
    result = service.files().list(
        q=query,
        fields='files(id,name,webViewLink)',
        pageSize=1
    ).execute()
    files = result.get('files', [])
    return files[0] if files else None


def upload_template(service, template_path, template_name):
    """Upload .xlsx file to Drive, converting to Google Sheets format."""
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    media = MediaFileUpload(
        template_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        resumable=False
    )
    file_metadata = {
        'name': template_name,
        'mimeType': GOOGLE_SHEETS_MIME,  # CRITICAL: converts .xlsx → Google Sheets
        'description': f'Test case template for Test-Genie ({template_name}). DO NOT DELETE.',
    }
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,name,mimeType,webViewLink'
    ).execute()
    return uploaded


def validate_upload(service, file_id, retries=3):
    """Verify uploaded file has correct mimeType (Google Sheets, not xlsx)."""
    for attempt in range(retries):
        file_info = service.files().get(
            fileId=file_id,
            fields='id,name,mimeType,webViewLink'
        ).execute()
        if file_info.get('mimeType') == GOOGLE_SHEETS_MIME:
            return file_info
        time.sleep(2)
    raise RuntimeError(
        f"Upload validation failed: mimeType is '{file_info.get('mimeType')}', "
        f"expected '{GOOGLE_SHEETS_MIME}'"
    )


def main():
    parser = argparse.ArgumentParser(description='Upload Excel template to Google Drive')
    parser.add_argument('--template', required=True, help='Path to .xlsx template file')
    parser.add_argument('--project-type', required=True,
                        choices=list(TEMPLATE_NAMES.keys()),
                        help='Project type (API_TEST, HOME, FEE_ENGINE, LENDING)')
    parser.add_argument('--credentials', help='Path to service account credentials.json')
    parser.add_argument('--force', action='store_true',
                        help='Force re-upload even if template already exists')
    args = parser.parse_args()

    credentials_path = find_credentials(args.credentials)
    if not credentials_path:
        print(json.dumps({
            "error": "credentials.json not found. Provide --credentials path or place credentials.json in project root."
        }))
        sys.exit(1)

    template_name = TEMPLATE_NAMES[args.project_type]

    try:
        service = build_drive_service(credentials_path)

        # Step 1: Search for existing template
        if not args.force:
            existing = search_existing_template(service, template_name)
            if existing:
                print(json.dumps({
                    "templateFileId": existing['id'],
                    "webViewLink": existing.get('webViewLink', ''),
                    "name": existing['name'],
                    "status": "existing"
                }))
                return

        # Step 2: Upload template
        uploaded = upload_template(service, args.template, template_name)

        # Step 3: Validate upload (wait for Drive to process)
        time.sleep(2)
        validated = validate_upload(service, uploaded['id'])

        print(json.dumps({
            "templateFileId": validated['id'],
            "webViewLink": validated.get('webViewLink', ''),
            "name": validated['name'],
            "status": "uploaded"
        }))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
