#!/usr/bin/env python3
"""Upload Docker image tar to NAS via File Station API."""

import os
import sys

import requests
import urllib3

# Disable SSL warnings for self-signed cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add scripts path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nas_azure_vault_integration import NASAzureVaultIntegration

NAS_HOST = "<NAS_PRIMARY_IP>"
NAS_PORT = 5000  # HTTP (more stable for large uploads)
TAR_FILE = os.path.join(os.environ.get("TEMP", "/tmp"), "manus-mcp-server.tar")
DEST_PATH = "/docker/lumina-mcp-central"


def main():
    # Get credentials
    print("Getting credentials from Azure Key Vault...")
    integration = NASAzureVaultIntegration()
    creds = integration.get_nas_credentials()
    if not creds:
        print("ERROR: Could not get NAS credentials")
        return 1
    username = creds["username"]
    password = creds["password"]
    print(f"Username: {username}")

    base_url = f"http://{NAS_HOST}:{NAS_PORT}/webapi"
    session = requests.Session()
    session.verify = False

    # Login
    print("Logging in to DSM...")
    login_resp = session.get(
        f"{base_url}/auth.cgi",
        params={
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": username,
            "passwd": password,
            "session": "FileStation",
            "format": "sid",
        },
    )
    login_data = login_resp.json()
    if not login_data.get("success"):
        print(f"Login failed: {login_data}")
        return 1

    sid = login_data["data"]["sid"]
    print(f"Logged in, SID: {sid[:8]}...")

    # Upload file via File Station
    print(f"Uploading {TAR_FILE} to {DEST_PATH}...")
    if not os.path.exists(TAR_FILE):
        print(f"ERROR: File not found: {TAR_FILE}")
        return 1

    file_size = os.path.getsize(TAR_FILE) / (1024 * 1024)
    print(f"File size: {file_size:.2f} MB")

    with open(TAR_FILE, "rb") as f:
        upload_resp = session.post(
            f"{base_url}/entry.cgi",
            params={"_sid": sid},
            data={
                "api": "SYNO.FileStation.Upload",
                "version": "2",
                "method": "upload",
                "path": DEST_PATH,
                "create_parents": "true",
                "overwrite": "true",
            },
            files={"file": ("manus-mcp-server.tar", f, "application/x-tar")},
            timeout=600,  # 10 minute timeout for large file
        )

    upload_data = upload_resp.json()
    if upload_data.get("success"):
        print("Upload successful!")
    else:
        print(f"Upload failed: {upload_data}")
        return 1

    # Logout
    session.get(
        f"{base_url}/auth.cgi",
        params={
            "api": "SYNO.API.Auth",
            "version": "1",
            "method": "logout",
            "session": "FileStation",
        },
    )
    print("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
