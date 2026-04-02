"""Upload file to Google Drive and get shareable link.

Reuses OAuth credentials from ~/.gdrive-mcp/ (same as MCP gdrive server).

Usage:
    python3 gdrive_upload.py <file_path> [--folder <folder_id>] [--name <display_name>]

Output (JSON):
    {"id": "...", "name": "...", "link": "https://drive.google.com/file/d/.../view", "direct": "https://drive.google.com/uc?id=..."}
"""

import argparse
import json
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CRED_DIR = Path.home() / ".gdrive-mcp"
OAUTH_KEYS = CRED_DIR / "gcp-oauth.keys.json"
TOKEN_FILE = CRED_DIR / ".gdrive-server-credentials.json"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def load_credentials():
    if not TOKEN_FILE.exists():
        print(f"ERROR: Token file not found: {TOKEN_FILE}", file=sys.stderr)
        print("Please ensure MCP gdrive server has been set up and authenticated.", file=sys.stderr)
        sys.exit(1)

    token_data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    oauth_keys = json.loads(OAUTH_KEYS.read_text(encoding="utf-8"))
    client_info = oauth_keys.get("installed", oauth_keys.get("web", {}))

    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_info["client_id"],
        client_secret=client_info["client_secret"],
        scopes=SCOPES,
    )

    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        # Save refreshed token
        token_data["access_token"] = creds.token
        TOKEN_FILE.write_text(json.dumps(token_data), encoding="utf-8")

    return creds


def upload_file(file_path, folder_id=None, display_name=None):
    creds = load_credentials()
    service = build("drive", "v3", credentials=creds)

    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    name = display_name or file_path.name

    # Detect MIME type
    import mimetypes
    mime_type, _ = mimetypes.guess_type(str(file_path))
    mime_type = mime_type or "application/octet-stream"

    metadata = {"name": name}
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)
    file = service.files().create(body=metadata, media_body=media, fields="id,name").execute()
    file_id = file["id"]

    # Set permission: anyone with link can view
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    result = {
        "id": file_id,
        "name": file["name"],
        "link": f"https://drive.google.com/file/d/{file_id}/view",
        "direct": f"https://lh3.googleusercontent.com/d/{file_id}",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description="Upload file to Google Drive")
    parser.add_argument("file", help="Path to file to upload")
    parser.add_argument("--folder", help="Google Drive folder ID (optional)")
    parser.add_argument("--name", help="Display name on Drive (default: filename)")
    args = parser.parse_args()
    upload_file(args.file, args.folder, args.name)


if __name__ == "__main__":
    main()
