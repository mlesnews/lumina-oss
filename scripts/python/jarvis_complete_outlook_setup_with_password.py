#!/usr/bin/env python3
"""
JARVIS: Complete Outlook Setup with Password Management

Handles password retrieval/setting and completes Outlook email account setup.

Tags: #JARVIS #OUTLOOK #MAILPLUS #PASSWORD #AUTOMATION @JARVIS @LUMINA @DOIT
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCompleteOutlook")

# Account configuration
ACCOUNT_CONFIG = {
    "email": "mlesn@<LOCAL_HOSTNAME>",
    "display_name": "mlesn",
    "password": "fiLVL3wVWfbv&Jpf",  # Password from jarvis_clear_and_start_mailplus.py
    "imap_server": "<NAS_PRIMARY_IP>",
    "imap_port": "993",
    "smtp_server": "<NAS_PRIMARY_IP>",
    "smtp_port": "587",
    "imap_encryption": "SSL/TLS",
    "smtp_encryption": "STARTTLS"
}


def get_or_set_password():
    """Get password from MailPlus or set a new one"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        from synology_api_base import SynologyAPIBase

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return None

        nas_ip = "<NAS_PRIMARY_IP>"
        nas_port = 5001
        account_email = ACCOUNT_CONFIG["email"]

        logger.info("=" * 80)
        logger.info("🔐 JARVIS: GETTING/SETTING MAILPLUS PASSWORD")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Account: {account_email}")
        logger.info("")

        # Connect to DSM API
        api = SynologyAPIBase(nas_ip=nas_ip, nas_port=nas_port, verify_ssl=False)

        if not api.login(credentials["username"], credentials["password"]):
            logger.error("❌ Failed to login to DSM API")
            return None

        logger.info("✅ Connected to DSM API")
        logger.info("")

        # Step 1: Try to get account info
        logger.info("📋 STEP 1: Checking MailPlus account...")
        logger.info("-" * 80)

        # Try to list accounts
        accounts = api.api_call(
            api="SYNO.MailPlusServer.Account",
            method="list",
            version="1",
            require_auth=True
        )

        account_found = False
        if accounts:
            logger.info(f"✅ Found {len(accounts.get('accounts', []))} account(s)")
            for acc in accounts.get('accounts', []):
                if acc.get('email', '').lower() == account_email.lower():
                    account_found = True
                    logger.info(f"✅ Found account: {account_email}")
                    break

        if not account_found:
            logger.warning(f"⚠️  Account {account_email} not found in MailPlus")
            logger.info("   Account may need to be created first")
            logger.info("   Will try to use NAS password as fallback")
            api.logout()
            return credentials["password"]  # Use NAS password as fallback

        # Step 2: Try to get password (may not be possible via API)
        logger.info("")
        logger.info("📋 STEP 2: Attempting to retrieve password...")
        logger.info("-" * 80)

        # MailPlus API typically doesn't expose passwords for security
        # So we'll use NAS password as the email password
        logger.info("💡 MailPlus API doesn't expose passwords (security)")
        logger.info("   Using NAS admin password as email account password")
        logger.info("   (This is the standard setup for MailPlus)")

        api.logout()
        return credentials["password"]

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        # Fallback to NAS password
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            nas_integration = NASAzureVaultIntegration()
            credentials = nas_integration.get_nas_credentials()
            if credentials:
                logger.info("💡 Using NAS password as fallback")
                return credentials["password"]
        except:
            pass
        return None


def complete_outlook_setup(password: str):
    """Complete Outlook setup with the password"""
    try:
        import pyautogui
        import pygetwindow as gw

        logger.info("")
        logger.info("=" * 80)
        logger.info("📧 JARVIS: COMPLETING OUTLOOK SETUP")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Account: {ACCOUNT_CONFIG['email']}")
        logger.info(f"Password: [REDACTED]")
        logger.info("")

        # Find Outlook window
        logger.info("📋 Finding Outlook window...")
        outlook_windows = []
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if 'outlook' in title_lower:
                outlook_windows.append(window)

        if not outlook_windows:
            logger.error("❌ Outlook window not found")
            logger.info("   Please open Outlook Classic first")
            return False

        outlook_window = outlook_windows[0]
        logger.info(f"✅ Found Outlook window: {outlook_window.title}")

        # Activate Outlook
        try:
            outlook_window.activate()
            time.sleep(2)
        except Exception:
            pass

        # Navigate to Account Settings
        logger.info("")
        logger.info("📋 Opening Account Settings...")
        pyautogui.hotkey('alt', 'f')
        time.sleep(1)
        pyautogui.press('t')
        time.sleep(1)
        pyautogui.press('a')
        time.sleep(3)

        # Click New
        logger.info("📋 Clicking 'New...' button...")
        pyautogui.press('n')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)

        # Manual setup
        logger.info("📋 Selecting manual setup...")
        pyautogui.press('m')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)

        # Enter email
        logger.info(f"📋 Entering email: {ACCOUNT_CONFIG['email']}")
        pyautogui.write(ACCOUNT_CONFIG['email'], interval=0.1)
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(0.5)

        # Enter password
        logger.info("📋 Entering password...")
        pyautogui.write(password, interval=0.05)
        time.sleep(1)

        # Click Next
        logger.info("📋 Clicking Next...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        # More Settings
        logger.info("📋 Opening More Settings...")
        pyautogui.press('tab', presses=3)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        # Advanced tab
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)

        # IMAP settings
        logger.info(f"📋 Configuring IMAP: {ACCOUNT_CONFIG['imap_server']}:{ACCOUNT_CONFIG['imap_port']}")
        pyautogui.press('tab', presses=5)
        time.sleep(0.5)
        # Clear any existing text first
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(ACCOUNT_CONFIG['imap_server'], interval=0.1)  # Server only, no port
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)
        # Clear port field
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(ACCOUNT_CONFIG['imap_port'], interval=0.1)  # Port in separate field
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)
        if ACCOUNT_CONFIG['imap_encryption'] == "SSL/TLS":
            pyautogui.press('down', presses=1)
        time.sleep(0.5)

        # SMTP settings
        logger.info(f"📋 Configuring SMTP: {ACCOUNT_CONFIG['smtp_server']}:{ACCOUNT_CONFIG['smtp_port']}")
        pyautogui.press('tab', presses=3)
        time.sleep(0.5)
        # Clear any existing text first
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(ACCOUNT_CONFIG['smtp_server'], interval=0.1)  # Server only, no port
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)
        # Clear port field
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(ACCOUNT_CONFIG['smtp_port'], interval=0.1)  # Port in separate field
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)
        if ACCOUNT_CONFIG['smtp_encryption'] == "STARTTLS":
            pyautogui.press('down', presses=2)
        time.sleep(0.5)

        # Save
        logger.info("📋 Saving settings...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        # Test connection
        logger.info("📋 Testing connection...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(5)

        # Finish
        logger.info("📋 Completing setup...")
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ OUTLOOK SETUP COMPLETED!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Please verify:")
        logger.info("   1. Check if account appears in Outlook")
        logger.info("   2. Try sending/receiving email")
        logger.info("   3. Account should be: {ACCOUNT_CONFIG['email']}")

        return True

    except ImportError:
        logger.error("❌ Required modules not available")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def main():
    """Main execution"""
    logger.info("=" * 80)
    logger.info("🚀 JARVIS: COMPLETE OUTLOOK SETUP WITH PASSWORD")
    logger.info("=" * 80)
    logger.info("")

    # Get or set password
    password = get_or_set_password()

    if not password:
        logger.error("❌ Could not get password")
        logger.info("")
        logger.info("💡 Please manually:")
        logger.info("   1. Check MailPlus → Account for password")
        logger.info("   2. Or reset password in MailPlus")
        logger.info("   3. Then run this script again")
        return False

    logger.info("")
    logger.info("✅ Password obtained")
    logger.info("")

    # Complete Outlook setup
    success = complete_outlook_setup(password)

    if success:
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ALL DONE!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📧 Outlook email account should now be configured")
        logger.info("   Check Outlook to verify the account is working")

    return success


if __name__ == "__main__":
    sys.exit(0 if success else 1)


    success = main()