#!/usr/bin/env python3
"""
Create the 'models' shared folder on NAS via DSM API
"""

import os
import sys
from pathlib import Path

import requests
import urllib3

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

urllib3.disable_warnings()

NAS_IP = "<NAS_PRIMARY_IP>"
BASE_URL = f"https://{NAS_IP}:5001/webapi"


def main():
    # Get credentials from Azure Key Vault
    try:
        from azure_service_bus_integration import AzureKeyVaultClient

        vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
        vault = AzureKeyVaultClient(vault_url=vault_url)

        # Use mlesn account for admin operations
        nas_user = "mlesn"
        nas_pass = vault.get_secret("synology-admin-password")
        if not nas_pass:
            nas_pass = vault.get_secret("nas-password")
        if not nas_pass:
            print("ERROR: Could not retrieve NAS password from Key Vault")
            print("Trying environment variable NAS_PASSWORD...")
            nas_pass = os.getenv("NAS_PASSWORD")
            if not nas_pass:
                print("ERROR: No NAS password available")
                return False
    except Exception as e:
        print(f"ERROR: Could not get credentials: {e}")
        return False

    print(f"Authenticating as {nas_user}...")

    # Login
    login_url = f"{BASE_URL}/auth.cgi"
    login_params = {
        "api": "SYNO.API.Auth",
        "version": "6",
        "method": "login",
        "account": nas_user,
        "passwd": nas_pass,
        "session": "DSMShare",
        "format": "sid",
    }
    response = requests.get(login_url, params=login_params, verify=False)
    login_data = response.json()

    if not login_data.get("success"):
        error = login_data.get("error", {})
        error_code = error.get("code")
        print(f"Login failed: code={error_code}")
        return False

    sid = login_data["data"]["sid"]
    print("Authenticated successfully")

    try:
        # Create share
        print("Creating 'models' share on /volume1...")
        create_url = f"{BASE_URL}/entry.cgi"
        create_params = {
            "api": "SYNO.Core.Share",
            "version": "1",
            "method": "create",
            "name": "models",
            "vol_path": "/volume1",
            "desc": "AI Models Storage for BitNet and other LLMs",
            "_sid": sid,
        }
        create_response = requests.get(create_url, params=create_params, verify=False)
        create_data = create_response.json()

        if create_data.get("success"):
            print("SUCCESS: 'models' share created!")
            return True
        else:
            error = create_data.get("error", {})
            error_code = error.get("code")
            # Error 404 = share already exists
            if error_code == 404:
                print("Share 'models' already exists (error 404)")
                return True
            # Error 400 = share name conflict or exists
            elif error_code == 400:
                print("Share 'models' may already exist (error 400)")
                return True
            else:
                print(f"Share creation failed: {create_data}")
                return False
    finally:
        # Logout
        logout_params = {
            "api": "SYNO.API.Auth",
            "version": "6",
            "method": "logout",
            "session": "DSMShare",
        }
        requests.get(login_url, params=logout_params, verify=False)
        print("Logged out")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
