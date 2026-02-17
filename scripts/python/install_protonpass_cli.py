#!/usr/bin/env python3
"""
Install ProtonPass CLI for Windows
Part of the Triad Password Manager System (Azure Key Vault, ProtonPass CLI, Dashlane)
"""
import sys
import subprocess
import urllib.request
import shutil
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("InstallProtonPassCLI")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("InstallProtonPassCLI")

PROTONPASS_INSTALL_DIR = Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass")
PROTONPASS_CLI_PATH_ALT = Path(r"C:\Users\mlesn\AppData\Local\Programs\pass-cli.exe")  # Actual install location
PROTONPASS_CLI_PATH = PROTONPASS_INSTALL_DIR / "pass-cli.exe"
INSTALL_SCRIPT_URL = "https://proton.me/download/pass-cli/install.ps1"
INSTALL_SCRIPT = Path.home() / "Downloads" / "install-protonpass-cli.ps1"
PROTONPASS_INSTALL_DIR_ENV = "PROTON_PASS_CLI_INSTALL_DIR"

def check_existing_installation() -> bool:
    """Check if ProtonPass CLI is already installed"""
    if PROTONPASS_CLI_PATH.exists():
        try:
            result = subprocess.run(
                [str(PROTONPASS_CLI_PATH), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"✅ ProtonPass CLI already installed: {result.stdout.strip()}")
                return True
        except Exception as e:
            logger.warning(f"⚠️  CLI exists but may not be working: {e}")
    return False

def download_installer_script() -> bool:
    """Download ProtonPass CLI installer script"""
    logger.info("📥 Downloading ProtonPass CLI installer script...")
    logger.info(f"   URL: {INSTALL_SCRIPT_URL}")

    try:
        # Create downloads directory if it doesn't exist
        INSTALL_SCRIPT.parent.mkdir(parents=True, exist_ok=True)

        # Download the installer script
        logger.info(f"   Saving to: {INSTALL_SCRIPT}")
        urllib.request.urlretrieve(INSTALL_SCRIPT_URL, INSTALL_SCRIPT)

        if INSTALL_SCRIPT.exists():
            logger.info(f"✅ Download complete: {INSTALL_SCRIPT.stat().st_size / 1024:.2f} KB")
            return True
        else:
            logger.error("❌ Download failed - file not found")
            return False
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return False

def install_protonpass() -> bool:
    """Install ProtonPass CLI using the official PowerShell installer script"""
    if not INSTALL_SCRIPT.exists():
        logger.error("❌ Installer script not found. Please download first.")
        return False

    logger.info("🔧 Installing ProtonPass CLI...")
    logger.info(f"   Using official installer: {INSTALL_SCRIPT}")
    logger.info(f"   Target directory: {PROTONPASS_INSTALL_DIR}")

    try:
        # Set install directory environment variable
        import os
        os.environ[PROTONPASS_INSTALL_DIR_ENV] = str(PROTONPASS_INSTALL_DIR.parent)

        # Run the PowerShell installer script
        logger.info("   Executing PowerShell installer...")
        process = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(INSTALL_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes timeout
        )

        if process.returncode == 0:
            logger.info("✅ Installer completed successfully")
            logger.info(f"   Output: {process.stdout}")
            return True
        else:
            logger.warning(f"⚠️  Installer returned code {process.returncode}")
            logger.info(f"   Output: {process.stdout}")
            logger.info(f"   Errors: {process.stderr}")
            # Still check if it installed
            if PROTONPASS_CLI_PATH.exists():
                logger.info("✅ CLI found despite non-zero exit code")
                return True
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Installer timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to run installer: {e}")
        return False

def verify_installation() -> bool:
    """Verify ProtonPass CLI installation"""
    logger.info("🔍 Verifying installation...")

    # Check both possible locations
    cli_path = None
    if PROTONPASS_CLI_PATH_ALT.exists():
        cli_path = PROTONPASS_CLI_PATH_ALT
    elif PROTONPASS_CLI_PATH.exists():
        cli_path = PROTONPASS_CLI_PATH
    else:
        logger.error(f"❌ CLI not found at expected locations:")
        logger.error(f"   {PROTONPASS_CLI_PATH}")
        logger.error(f"   {PROTONPASS_CLI_PATH_ALT}")
        logger.info("💡 Please check if installation completed successfully")
        return False

    try:
        result = subprocess.run(
            [str(cli_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info(f"✅ ProtonPass CLI installed successfully!")
            logger.info(f"   Version: {result.stdout.strip()}")
            logger.info(f"   Path: {cli_path}")
            return True
        else:
            logger.error(f"❌ CLI exists but version check failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False

def cleanup_installer():
    """Clean up downloaded installer script"""
    if INSTALL_SCRIPT.exists():
        try:
            INSTALL_SCRIPT.unlink()
            logger.info("🧹 Cleaned up installer script")
        except Exception as e:
            logger.debug(f"Could not remove installer script: {e}")

def main():
    """Main installation process"""
    import argparse

    parser = argparse.ArgumentParser(description="Install ProtonPass CLI")
    parser.add_argument("--download-only", action="store_true", help="Only download, don't install")
    parser.add_argument("--install-only", action="store_true", help="Only install (assumes download exists)")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing installation")
    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("🔧 PROTONPASS CLI INSTALLATION")
    logger.info("=" * 70)
    logger.info("")

    # Check if already installed
    if check_existing_installation() and not args.verify_only:
        logger.info("✅ ProtonPass CLI is already installed!")
        logger.info("💡 Use --verify-only to check status, or uninstall first to reinstall")
        return 0

    if args.verify_only:
        if verify_installation():
            return 0
        else:
            return 1

    # Download
    if not args.install_only:
        if not download_installer_script():
            logger.error("❌ Download failed")
            return 1

    # Install
    if not args.download_only:
        if not install_protonpass():
            logger.error("❌ Installation failed")
            return 1

        # Wait a bit for installation
        logger.info("⏳ Waiting for installation to complete...")
        logger.info("   Please complete the installer, then press Enter to continue verification...")
        try:
            input()
        except:
            pass

        # Verify
        if verify_installation():
            logger.info("")
            logger.info("=" * 70)
            logger.info("✅ PROTONPASS CLI INSTALLATION COMPLETE")
            logger.info("=" * 70)
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Authenticate: python scripts/python/protonpass_auto_login.py")
            logger.info("2. Test: python scripts/python/copy_mariadb_credentials_from_protonpass.py")
            cleanup_installer()
            return 0
        else:
            logger.error("❌ Installation verification failed")
            return 1

    return 0

if __name__ == "__main__":

    sys.exit(main())