#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
google_auth.py - Shared OAuth Desktop App authentication for Google APIs

Uses OAuth 2.0 Desktop (installed) app flow instead of Service Account.
Token is cached at ~/.config/test-genie/token.json for reuse.

Usage (as module):
    from google_auth import get_credentials, build_services, find_credentials

    creds = get_credentials('credentials.json')
    drive, sheets = build_services('credentials.json')

Requirements:
    pip install google-auth-oauthlib google-auth google-api-python-client
"""

import json
import os
import sys
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    print(json.dumps({"error": "Missing dependencies. Run: pip install google-auth google-api-python-client"}))
    sys.exit(1)

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    InstalledAppFlow = None  # Will fail gracefully if first-time auth is needed

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
]

TOKEN_DIR = Path.home() / '.config' / 'test-genie'
TOKEN_PATH = TOKEN_DIR / 'token.json'


def _is_valid_oauth_credentials(path):
    """Check if a credentials.json is a valid OAuth (installed/web) type, not service_account.
    Also rejects unfilled templates (containing placeholder values like '<YOUR_')."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Valid OAuth credentials have 'installed' or 'web' top-level key
        if 'installed' not in data and 'web' not in data:
            return False
        # Check for unfilled template placeholders
        oauth_data = data.get('installed') or data.get('web') or {}
        client_id = oauth_data.get('client_id', '')
        if not client_id or '<YOUR_' in client_id:
            return False
        return True
    except (json.JSONDecodeError, OSError):
        return False


# Bundled fallback credentials (shipped with test-genie)
_BUNDLED_CREDENTIALS = {
    "installed": {
        "client_id": "557486265467-392qr7me0acjg8g9ofi8d3883a3ro189.apps.googleusercontent.com",
        "project_id": "trim-heaven-475813-a2",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost"]
    }
}

_BUNDLED_CREDENTIALS_PATH = os.path.join(
    os.path.expanduser('~/.config/test-genie'), 'credentials.json'
)


def _ensure_bundled_credentials():
    """Write bundled credentials to ~/.config/test-genie/credentials.json if not present."""
    if os.path.isfile(_BUNDLED_CREDENTIALS_PATH) and _is_valid_oauth_credentials(_BUNDLED_CREDENTIALS_PATH):
        return _BUNDLED_CREDENTIALS_PATH
    os.makedirs(os.path.dirname(_BUNDLED_CREDENTIALS_PATH), exist_ok=True)
    with open(_BUNDLED_CREDENTIALS_PATH, 'w', encoding='utf-8') as f:
        json.dump(_BUNDLED_CREDENTIALS, f, indent=2)
    return _BUNDLED_CREDENTIALS_PATH


def find_credentials(provided_path=None):
    """Search for credentials.json in standard locations.

    Priority:
    1. Explicit path (--credentials)
    2. Project root credentials.json
    3. ~/.config/test-genie/credentials.json
    4. Bundled fallback (auto-written to ~/.config/test-genie/)

    Skips service_account type credentials (not compatible with OAuth desktop flow).
    """
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
        if path and os.path.isfile(path) and _is_valid_oauth_credentials(path):
            return path

    # No valid OAuth credentials found — use bundled fallback
    return _ensure_bundled_credentials()


def _load_token(credentials_path):
    """Load cached token and attach client_id/client_secret from credentials.json."""
    if not TOKEN_PATH.exists():
        return None

    try:
        token_data = json.loads(TOKEN_PATH.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return None

    refresh_token = token_data.get('refresh_token')
    if not refresh_token:
        return None

    # Read client_id and client_secret from credentials.json
    try:
        with open(credentials_path, 'r', encoding='utf-8') as f:
            cred_data = json.load(f)
        installed = cred_data.get('installed', cred_data.get('web', {}))
        client_id = installed.get('client_id')
        client_secret = installed.get('client_secret')
        token_uri = installed.get('token_uri', 'https://oauth2.googleapis.com/token')
    except (json.JSONDecodeError, OSError, KeyError):
        return None

    if not client_id or not client_secret:
        return None

    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    return creds


def _save_token(creds):
    """Save token to cache file."""
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes) if creds.scopes else SCOPES,
    }
    TOKEN_PATH.write_text(json.dumps(token_data, indent=2), encoding='utf-8')


def get_credentials(credentials_path):
    """Get valid OAuth credentials, refreshing or running auth flow as needed.

    1. Try loading cached token from ~/.config/test-genie/token.json
    2. If expired, refresh using refresh_token
    3. If no token or refresh fails, run InstalledAppFlow (opens browser)

    Args:
        credentials_path: Path to credentials.json (OAuth Desktop App type)

    Returns:
        google.oauth2.credentials.Credentials
    """
    # Try cached token
    creds = _load_token(credentials_path)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds)
            return creds
        except Exception:
            pass  # Fall through to full auth flow

    # Full auth flow — requires google_auth_oauthlib
    if InstalledAppFlow is None:
        print(json.dumps({
            "error": "First-time authentication requires google_auth_oauthlib. "
                     "Run: pip install google-auth-oauthlib"
        }))
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True)
    _save_token(creds)

    return creds


def build_services(credentials_path):
    """Build and return (drive_service, sheets_service) using OAuth credentials."""
    creds = get_credentials(credentials_path)
    drive = build('drive', 'v3', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds)
    return drive, sheets


def build_sheets_service(credentials_path):
    """Build and return sheets_service only."""
    creds = get_credentials(credentials_path)
    return build('sheets', 'v4', credentials=creds)


def build_drive_service(credentials_path):
    """Build and return drive_service only."""
    creds = get_credentials(credentials_path)
    return build('drive', 'v3', credentials=creds)
