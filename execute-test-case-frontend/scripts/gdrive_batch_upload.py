"""Batch upload multiple files to Google Drive in a single API client session.

Reuses OAuth credentials from ~/.gdrive-mcp/ (same as MCP gdrive server).
Initializes the Drive API client ONCE and uploads all files sequentially,
avoiding the per-file cold-start overhead of gdrive_upload.py.

Usage:
    python3 gdrive_batch_upload.py file1.png file2.png file3.png [--folder <folder_id>]

Output (JSON array):
    [
      {"name": "file1.png", "id": "...", "link": "https://drive.google.com/file/d/.../view", "direct": "https://lh3.googleusercontent.com/d/..."},
      ...
    ]
"""

import argparse
import json
import mimetypes
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
        token_data["access_token"] = creds.token
        TOKEN_FILE.write_text(json.dumps(token_data), encoding="utf-8")

    return creds


def batch_upload(file_paths, folder_id=None):
    creds = load_credentials()
    service = build("drive", "v3", credentials=creds)

    results = []
    for file_path in file_paths:
        fp = Path(file_path)
        if not fp.exists():
            results.append({"name": fp.name, "error": f"File not found: {file_path}"})
            continue

        try:
            mime_type, _ = mimetypes.guess_type(str(fp))
            mime_type = mime_type or "application/octet-stream"

            metadata = {"name": fp.name}
            if folder_id:
                metadata["parents"] = [folder_id]

            media = MediaFileUpload(str(fp), mimetype=mime_type, resumable=True)
            file = service.files().create(
                body=metadata, media_body=media, fields="id,name"
            ).execute()
            file_id = file["id"]

            service.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader"},
            ).execute()

            results.append({
                "name": file["name"],
                "id": file_id,
                "link": f"https://drive.google.com/file/d/{file_id}/view",
                "direct": f"https://lh3.googleusercontent.com/d/{file_id}",
            })
        except Exception as e:
            results.append({"name": fp.name, "error": str(e)})

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return results


def main():
    parser = argparse.ArgumentParser(description="Batch upload files to Google Drive")
    parser.add_argument("files", nargs="+", help="Paths to files to upload")
    parser.add_argument("--folder", help="Google Drive folder ID (optional)")
    args = parser.parse_args()
    batch_upload(args.files, args.folder)


if __name__ == "__main__":
    main()
