#!/usr/bin/env python3
"""Add admin credentials to Azure Vault from clipboard"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from unified_secrets_manager import SecretSource, UnifiedSecretsManager
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False
    print("❌ unified_secrets_manager not available")
    sys.exit(1)

def get_clipboard():
    """Get password from clipboard"""
    try:
        import pyperclip
        return pyperclip.paste()
    except:
        pass

    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        return root.clipboard_get()
    except:
        pass

    return None

def main():
    print("=" * 60)
    print("🔐 ADD ADMIN CREDENTIALS TO AZURE VAULT")
    print("=" * 60)

    if not SECRETS_MANAGER_AVAILABLE:
        print("❌ Secrets manager not available")
        return 1

    project_root = Path(__file__).parent.parent.parent
    manager = UnifiedSecretsManager(project_root)

    # Try to get password from clipboard
    print("\n📋 Getting password from clipboard...")
    password = get_clipboard()

    if not password:
        password = input("   Password (or paste from clipboard): ").strip()

    if not password:
        print("❌ Password required")
        return 1

    username = "admin"

    print("\n💾 Saving to Azure Vault...")
    print(f"   Username: {username}")
    print(f"   Password: [REDACTED]")

    try:
        # Save username
        if manager.set_secret("admin-username", username, source=SecretSource.AZURE_KEY_VAULT):
            print(f"   ✅ Saved: admin-username = {username}")
        else:
            print("   ❌ Failed to save username")
            return 1

        # Save password
        if manager.set_secret("admin-password", password, source=SecretSource.AZURE_KEY_VAULT):
            print("   ✅ Saved: admin-password")
        else:
            print("   ❌ Failed to save password")
            return 1

        print("\n" + "=" * 60)
        print("✅ CREDENTIALS SAVED!")
        print("=" * 60)
        print("\n🧪 Test connection:")
        print("   python scripts/python/test_mariadb_connection.py \\")
        print("     --host <NAS_PRIMARY_IP> --database lumina_holocrons")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":


    sys.exit(main())