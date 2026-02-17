#!/usr/bin/env python3
"""
Setup NAS Push Migration - Retrieve credentials from Azure Key Vault and run migration script

ALWAYS use Azure Key Vault credentials +++++
Never hardcode passwords +++++

Tags: #NAS #MIGRATION #PUSH #WINDOWS @JARVIS
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("NASPushMigrationSetup")

def main():
    """Setup and run NAS push migration with credentials"""

    # Get NAS credentials
    try:
        vault_integration = NASAzureVaultIntegration()
        credentials = vault_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Failed to retrieve NAS credentials")
            return 1

        username = credentials.get("username", "backupadm")
        password = credentials.get("password", "")

        # Verify username is "backupadm" (+++++ CRITICAL - user requirement)
        if username != "backupadm":
            logger.warning(f"⚠️  WARNING: Username from Azure Vault is '{username}', expected 'backupadm'")
            logger.warning("⚠️  Please verify Azure Key Vault secrets 'nas-username' and 'nas-password' contain 'backupadm' credentials")

        # Verify credentials are not empty
        if not username or not password:
            logger.error("❌ ERROR: Credentials from Azure Vault are empty!")
            logger.error(f"   Username: {'(empty)' if not username else '***'}")
            logger.error(f"   Password: {'(empty)' if not password else '***'}")
            return 1

        logger.info(f"✅ Retrieved credentials for user: {username} [REDACTED]")
    except Exception as e:
        logger.error(f"❌ Error retrieving credentials: {e}")
        return 1

    # Path to PowerShell script
    ps_script = project_root / "scripts" / "nas_push_migration_from_windows.ps1"

    if not ps_script.exists():
        logger.error(f"❌ PowerShell script not found: {ps_script}")
        return 1

    # Build command with credentials from Azure Vault (+++++ ALWAYS USE VAULT)
    # Pass credentials securely to PowerShell script
    cmd = [
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-File", str(ps_script),
        "-NasUsername", username,
        "-NasPassword", password  # Credentials from Azure Key Vault (+++++)
    ]

    logger.info("🚀 Starting NAS push migration...")
    logger.info(f"   Script: {ps_script}")
    logger.info(f"   User: {username}")

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        logger.error(f"❌ Error running migration script: {e}")
        return 1

if __name__ == "__main__":


    sys.exit(main())