#!/usr/bin/env python3
"""
Outlook Account Verifier and Auto-Configurator
Checks and verifies Outlook account setup for NAS Mail Hub
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    import win32com.client
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False
    print("[WARN] win32com not available. Install: pip install pywin32")

def check_outlook_accounts() -> Dict[str, Any]:
    """Check Outlook accounts via COM"""
    if not WIN32COM_AVAILABLE:
        return {"error": "win32com not available"}

    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        accounts = namespace.Accounts

        account_list = []
        nas_account_found = False

        for i in range(accounts.Count):
            account = accounts.Item(i + 1)
            account_info = {
                "display_name": account.DisplayName,
                "smtp_address": account.SmtpAddress,
                "account_type": account.AccountType,
            }
            account_list.append(account_info)

            if account.SmtpAddress == "mlesn@<LOCAL_HOSTNAME>":
                nas_account_found = True

        return {
            "success": True,
            "accounts": account_list,
            "nas_account_found": nas_account_found,
            "total_accounts": accounts.Count
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    """Main function"""
    print("=" * 80)
    print("OUTLOOK ACCOUNT VERIFIER")
    print("=" * 80)
    print("")

    if not WIN32COM_AVAILABLE:
        print("[ERROR] win32com not available")
        print("[INFO] Install: pip install pywin32")
        return

    result = check_outlook_accounts()

    if "error" in result:
        print(f"[ERROR] {result['error']}")
        return

    print(f"[INFO] Total accounts: {result['total_accounts']}")
    print("")

    if result['accounts']:
        print("[ACCOUNTS] Found accounts:")
        for acc in result['accounts']:
            print(f"  - {acc['display_name']} ({acc['smtp_address']})")
    else:
        print("[INFO] No accounts found")

    print("")

    if result['nas_account_found']:
        print("[SUCCESS] NAS Mail Hub account is configured!")
    else:
        print("[INFO] NAS Mail Hub account not found")
        print("[ACTION] Complete setup in Outlook:")
        print("  1. Enter password when Outlook prompts")
        print("  2. Or manually add account if needed")

    print("")

if __name__ == "__main__":


    main()