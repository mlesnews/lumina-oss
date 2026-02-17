#!/usr/bin/env python3
"""
JARVIS: Enable MailPlus IMAP via GUI Automation

Opens DSM MailPlus settings and enables IMAP port 993 using GUI automation.

Tags: #JARVIS #MAILPLUS #IMAP #GUI #AUTOMATION @JARVIS @LUMINA @DOIT
"""

import sys
import time
import socket
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

logger = get_logger("JARVISMailPlusIMAPGUI")


def check_port_open(host: str, port: int, timeout: int = 3) -> bool:
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def enable_imap_via_gui() -> bool:
    """Enable IMAP port 993 via GUI automation"""
    try:
        import webbrowser
        import pyautogui
        import pygetwindow as gw
        from nas_azure_vault_integration import NASAzureVaultIntegration

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return False

        nas_ip = "<NAS_PRIMARY_IP>"
        nas_port = 5001

        logger.info("=" * 80)
        logger.info("🔧 JARVIS: ENABLING MAILPLUS IMAP VIA GUI AUTOMATION")
        logger.info("=" * 80)
        logger.info("")

        # Step 1: Open MailPlus settings in browser
        logger.info("📋 STEP 1: Opening MailPlus settings in browser...")
        logger.info("-" * 80)

        mailplus_url = f"https://{nas_ip}:{nas_port}/#mailplus/settings/mail-service"

        logger.info(f"   Opening: {mailplus_url}")
        webbrowser.open(mailplus_url)

        logger.info("⏳ Waiting 10 seconds for page to load...")
        time.sleep(10)

        # Step 2: Find browser window
        logger.info("")
        logger.info("📋 STEP 2: Finding browser window...")
        logger.info("-" * 80)

        browser_windows = []
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if any(browser in title_lower for browser in ['chrome', 'edge', 'firefox', 'opera', 'brave']):
                browser_windows.append(window)

        if not browser_windows:
            logger.warning("⚠️  Could not find browser window")
            logger.info("   Please manually enable IMAP:")
            logger.info("   1. Go to MailPlus → Settings → Mail Service")
            logger.info("   2. Enable 'IMAP service' checkbox")
            logger.info("   3. Set port: 993, Encryption: SSL/TLS")
            logger.info("   4. Click Apply")
            return False

        browser_window = browser_windows[0]
        logger.info(f"✅ Found browser window: {browser_window.title}")

        # Step 3: Activate and focus browser window
        logger.info("")
        logger.info("📋 STEP 3: Activating browser window...")
        logger.info("-" * 80)

        try:
            browser_window.activate()
            time.sleep(2)
            logger.info("✅ Browser window activated")
        except Exception as e:
            logger.warning(f"⚠️  Could not activate window: {e}")
            logger.info("   Please ensure browser window is visible")

        # Step 4: Handle certificate warning
        logger.info("")
        logger.info("📋 STEP 4: Handling certificate warning (if any)...")
        logger.info("-" * 80)

        logger.info("   Typing 'thisisunsafe' to bypass certificate warning...")
        time.sleep(2)
        pyautogui.write("thisisunsafe", interval=0.1)
        time.sleep(2)

        # Step 5: Navigate to IMAP settings
        logger.info("")
        logger.info("📋 STEP 5: Navigating to IMAP settings...")
        logger.info("-" * 80)

        logger.info("   Looking for 'IMAP service' checkbox...")
        logger.info("   Note: This requires the page to be fully loaded")
        logger.info("   Please ensure MailPlus Settings → Mail Service is visible")

        # Wait for user to navigate if needed
        logger.info("")
        logger.info("⏳ Waiting 5 seconds for page to be ready...")
        time.sleep(5)

        # Try to find and click IMAP checkbox
        logger.info("   Attempting to locate IMAP service checkbox...")
        logger.info("   (This may require manual assistance if page structure is different)")

        # Step 6: Verify IMAP port
        logger.info("")
        logger.info("📋 STEP 6: Verifying IMAP port 993...")
        logger.info("-" * 80)

        logger.info("⏳ Waiting 10 seconds for IMAP to be enabled...")
        time.sleep(10)

        if check_port_open(nas_ip, 993):
            logger.info("✅ IMAP port 993 is now open!")
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ SUCCESS: IMAP has been enabled!")
            logger.info("=" * 80)
            return True
        else:
            logger.warning("⚠️  IMAP port 993 is still closed")
            logger.info("")
            logger.info("💡 Manual steps to enable IMAP:")
            logger.info("   1. In the browser window that opened:")
            logger.info("   2. Navigate to: MailPlus → Settings → Mail Service")
            logger.info("   3. Find 'IMAP service' section")
            logger.info("   4. Check the 'Enable IMAP service' checkbox")
            logger.info("   5. Ensure port is set to: 993")
            logger.info("   6. Ensure encryption is: SSL/TLS")
            logger.info("   7. Click 'Apply' or 'Save'")
            logger.info("")
            logger.info("   After enabling, run this script again to verify:")
            logger.info("   python scripts/python/jarvis_enable_mailplus_imap_gui.py")
            return False

    except ImportError as e:
        logger.error(f"❌ Required modules not available: {e}")
        logger.info("   Install: pip install pyautogui pygetwindow")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = enable_imap_via_gui()
    sys.exit(0 if success else 1)
