#!/usr/bin/env python3
"""
ProtonPass Automated Login

Uses credentials from Azure Key Vault to authenticate ProtonPass CLI.
The extra password (gating key) is stored ONLY in Azure Key Vault.

Security Architecture:
- Azure Key Vault = Gatekeeper (holds unlock key)
- ProtonPass = Secondary vault (never stores its own key)
"""

import sys
import subprocess
import time
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ProtonPassAutoLogin")

logger = get_logger("ProtonPassAutoLogin") if 'get_logger' in dir() else logging.getLogger("ProtonPassAutoLogin")

# Check both possible locations
PROTONPASS_CLI_ALT = Path(r"C:\Users\mlesn\AppData\Local\Programs\pass-cli.exe")
PROTONPASS_CLI = Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe")
if not PROTONPASS_CLI.exists() and PROTONPASS_CLI_ALT.exists():
    PROTONPASS_CLI = PROTONPASS_CLI_ALT
PROJECT_ROOT = Path(r"C:\Users\mlesn\Dropbox\my_projects\.lumina")


def get_protonpass_credentials():
    """Retrieve ProtonPass credentials from Azure Key Vault."""
    manager = UnifiedSecretsManager(PROJECT_ROOT)

    # The extra password is the gating key stored in Azure
    extra_password = manager.get_secret("protonpass-extra-password", source=SecretSource.AZURE_KEY_VAULT)

    if not extra_password:
        logger.error("❌ protonpass-extra-password not found in Azure Key Vault")
        return None, None, None

    # Username and main password are optional for web login
    username = manager.get_secret("protonpass-username", source=SecretSource.AZURE_KEY_VAULT)
    password = manager.get_secret("protonpass-password", source=SecretSource.AZURE_KEY_VAULT)

    return username, password, extra_password


def clear_session():
    """Clear any existing ProtonPass CLI session."""
    import os
    session_dir = Path(os.environ.get("APPDATA", "")) / "proton-pass-cli"
    if session_dir.exists():
        import shutil
        try:
            shutil.rmtree(session_dir)
            logger.info("🗑️  Cleared existing session")
        except Exception as e:
            logger.warning(f"⚠️  Could not clear session: {e}")


def check_login_status():
    """Check if ProtonPass CLI is logged in."""
    try:
        result = subprocess.run(
            [str(PROTONPASS_CLI), "test"],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            return True, "logged_in"
        elif "needs extra password" in result.stderr:
            return False, "needs_extra_password"
        elif "not logged in" in result.stderr:
            return False, "not_logged_in"
        elif "no session" in result.stderr:
            return False, "no_session"
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)


def attempt_web_login():
    try:
        """Start web login and wait for completion."""
        print("\n🌐 Starting web login...")
        print("   A browser window will open. Complete authentication there.")

        proc = subprocess.Popen(
            [str(PROTONPASS_CLI), "login"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for URL to be printed
        time.sleep(3)

        # Poll for authentication (up to 3 minutes)
        for i in range(36):
            time.sleep(5)
            logged_in, status = check_login_status()

            if logged_in:
                print("✅ Web login successful!")
                proc.terminate()
                return True
            elif status == "needs_extra_password":
                print("🔑 Web auth complete, needs extra password...")
                proc.terminate()
                return "needs_extra_password"

            print(f"   [{i+1}/36] Waiting for browser auth...")

        proc.terminate()
        return False


    except Exception as e:
        logger.error(f"Error in attempt_web_login: {e}", exc_info=True)
        raise
def provide_extra_password(extra_password: str):
    """
    Provide the extra password to unlock the vault.
    Note: ProtonPass CLI may need interactive input for this.
    """
    # The CLI doesn't have a direct flag for extra password
    # We may need to use a different approach
    print("🔐 Providing extra password...")

    # Check if we can use stdin
    try:
        proc = subprocess.Popen(
            [str(PROTONPASS_CLI), "login", "--interactive"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Try to send the extra password
        stdout, stderr = proc.communicate(input=f"{extra_password}\n", timeout=30)

        if proc.returncode == 0:
            print("✅ Extra password accepted!")
            return True
        else:
            print(f"⚠️  Result: {stderr}")
            return False

    except Exception as e:
        logger.error(f"❌ Error providing extra password: {e}")
        return False


def main():
    try:
        print("=" * 60)
        print("🔐 ProtonPass Automated Login")
        print("   Using Azure Key Vault gating mechanism")
        print("=" * 60)

        if not PROTONPASS_CLI.exists():
            print(f"❌ ProtonPass CLI not found at {PROTONPASS_CLI}")
            return False

        # Get credentials from Azure
        print("\n📦 Retrieving credentials from Azure Key Vault...")
        username, password, extra_password = get_protonpass_credentials()

        if not extra_password:
            print("❌ Cannot proceed without extra password from Azure Key Vault")
            return False

        print("✅ Gating credentials retrieved")

        # Check current status
        print("\n🔍 Checking current login status...")
        logged_in, status = check_login_status()

        if logged_in:
            print("✅ Already logged in!")
            return True

        print(f"   Status: {status}")

        if status == "needs_extra_password":
            # Just need to provide extra password
            return provide_extra_password(extra_password)

        elif status in ["not_logged_in", "no_session"]:
            # Need full login flow
            result = attempt_web_login()

            if result == "needs_extra_password":
                return provide_extra_password(extra_password)
            elif result:
                return True
            else:
                print("❌ Web login timed out or failed")
                return False

        else:
            print(f"⚠️  Unexpected status: {status}")
            return False


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    print("\n" + "=" * 60)
    if success:
        print("✅ ProtonPass CLI is now authenticated!")
        print("   You can now run the Triad Baseline Sync.")
    else:
        print("❌ Authentication incomplete.")
        print("   Please run interactive login manually:")
        print(f'   & "{PROTONPASS_CLI}" login --interactive')
    print("=" * 60)
    sys.exit(0 if success else 1)

    success = main()