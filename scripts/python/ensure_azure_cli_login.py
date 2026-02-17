#!/usr/bin/env python3
"""
Ensure Azure CLI is logged in before startup

This script checks if Azure CLI is logged in and attempts to use existing credentials
to avoid certificate prompts during startup.

Tags: #AZURE #STARTUP #AUTHENTICATION
"""

import sys
import subprocess
import json
from pathlib import Path

def check_azure_cli_login() -> bool:
    """Check if Azure CLI is logged in"""
    try:
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            account_info = json.loads(result.stdout)
            print(f"✅ Azure CLI is logged in: {account_info.get('name', 'Unknown account')}")
            return True
        else:
            print("⚠️  Azure CLI is not logged in")
            return False
    except FileNotFoundError:
        print("⚠️  Azure CLI not found")
        return False
    except json.JSONDecodeError:
        print("⚠️  Could not parse Azure CLI account info")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Azure CLI check timed out")
        return False
    except Exception as e:
        print(f"⚠️  Error checking Azure CLI login: {e}")
        return False


def main():
    """Main function"""
    is_logged_in = check_azure_cli_login()

    if not is_logged_in:
        print("\n💡 To avoid certificate prompts during startup:")
        print("   1. Run: az login")
        print("   2. Or: az login --use-device-code")
        print("   3. This will prevent certificate selection prompts")
        return 1

    return 0


if __name__ == "__main__":

    sys.exit(main())