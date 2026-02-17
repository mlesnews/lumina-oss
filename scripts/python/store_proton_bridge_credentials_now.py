#!/usr/bin/env python3
"""
Store Proton Bridge Credentials Now
Quick script to store credentials from clipboard.

Tags: #PROTONBRIDGE #CREDENTIALS #STORE
@JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from get_proton_bridge_credentials import ProtonBridgeCredentialManager
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "get_proton_bridge_credentials",
            script_dir / "get_proton_bridge_credentials.py"
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            ProtonBridgeCredentialManager = module.ProtonBridgeCredentialManager
    except Exception as e:
        print(f"Error importing: {e}")
        sys.exit(1)

logger = get_logger("StoreProtonBridgeCredentials")


def get_clipboard() -> str:
    """Get clipboard contents"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Clipboard"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        logger.error(f"Error reading clipboard: {e}")
    return ""


def main():
    """Main execution"""
    # Email from user
    username = "mlesnews@protonmail.com"

    # Get password from clipboard
    logger.info("📋 Reading password from clipboard...")
    password = get_clipboard()

    if not password or len(password) < 8:
        logger.error("❌ Password not found in clipboard or too short")
        logger.info("💡 Please copy the Proton Bridge password to clipboard and try again")
        return 1

    # Remove any extra whitespace/newlines
    password = password.strip()

    logger.info(f"✅ Password retrieved from clipboard [REDACTED]")
    logger.info(f"👤 Username: {username}")
    logger.info("")

    # Initialize credential manager
    try:
        manager = ProtonBridgeCredentialManager()
    except Exception as e:
        logger.error(f"❌ Error initializing credential manager: {e}")
        return 1

    # Store credentials
    # Use account name based on email
    account_name = "mlesnews"  # From mlesnews@protonmail.com

    logger.info(f"💾 Storing credentials for account: {account_name}")
    logger.info("")

    results = manager.store_bridge_credentials(
        username=username,
        password=password,
        account_name=account_name,
        store_in_protonpass=True,
        store_in_azure_vault=True
    )

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 STORAGE SUMMARY")
    logger.info("=" * 80)

    if results.get("protonpass"):
        logger.info("✅ Stored in ProtonPassCli")
    else:
        logger.warning("⚠️  Not stored in ProtonPassCli (not available)")

    if results.get("azure_vault"):
        logger.info("✅ Stored in Azure Vault")
    else:
        logger.warning("⚠️  Not stored in Azure Vault (check errors above)")

    logger.info("=" * 80)

    # Verify storage
    logger.info("")
    logger.info("🔍 Verifying stored credentials...")
    logger.info("")

    stored_username = manager.get_bridge_username(account_name)
    stored_password = manager.get_bridge_password(account_name)

    if stored_username and stored_password:
        logger.info("✅ Credentials verified and accessible!")
        logger.info(f"   Username: {stored_username}")
        logger.info(f"   Password: [REDACTED]")
    else:
        logger.warning("⚠️  Credentials stored but verification failed")
        if not stored_username:
            logger.warning("   Username not retrievable")
        if not stored_password:
            logger.warning("   Password not retrievable")

    return 0 if (results.get("protonpass") or results.get("azure_vault")) else 1


if __name__ == "__main__":


    exit(main())