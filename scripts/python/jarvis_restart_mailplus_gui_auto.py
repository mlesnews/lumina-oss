#!/usr/bin/env python3
"""
JARVIS: Automatically Restart MailPlus-Server via DSM GUI

Fully automated GUI automation to restart MailPlus-Server in DSM Package Center.

Tags: #JARVIS #MAILPLUS #GUI_AUTOMATION #MANUS #FULLAUTO @JARVIS @LUMINA @DOIT
"""

import sys
import time
import pyautogui
import pygetwindow as gw
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

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

logger = get_logger("JARVISRestartMailPlusGUI")

# Disable pyautogui failsafe for automation
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.5


class JARVISRestartMailPlusGUI:
    """JARVIS GUI automation for restarting MailPlus-Server"""

    def __init__(self):
        """Initialize automation"""
        self.dsm_url = "https://<NAS_PRIMARY_IP>:5001"
        self.browser_window = None

        logger.info("=" * 80)
        logger.info("🤖 JARVIS: AUTOMATIC MAILPLUS-SERVER RESTART")
        logger.info("=" * 80)
        logger.info("")

    def ensure_window_focused(self) -> bool:
        """Ensure browser window is focused"""
        try:
            windows = gw.getWindowsWithTitle("")
            browser_windows = []

            for window in windows:
                title_lower = window.title.lower()
                if any(browser in title_lower for browser in ["neo", "edge", "chrome", "firefox", "dsm", "synology", "package"]):
                    browser_windows.append(window)

            if not browser_windows:
                logger.warning("⚠️  No browser window found")
                return False

            self.browser_window = browser_windows[0]

            try:
                self.browser_window.activate()
                time.sleep(0.5)

                center_x = self.browser_window.left + self.browser_window.width // 2
                center_y = self.browser_window.top + self.browser_window.height // 2
                pyautogui.click(center_x, center_y)
                time.sleep(0.3)

                logger.debug(f"✅ Focused: {self.browser_window.title}")
                return True
            except Exception as e:
                logger.warning(f"⚠️  Could not focus: {e}")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Window focus failed: {e}")
            return False

    def open_dsm_package_center(self) -> bool:
        try:
            """Open DSM Package Center"""
            logger.info("🌐 Opening DSM Package Center...")

            webbrowser.open(f"{self.dsm_url}/#packages")
            time.sleep(5)

            if not self.ensure_window_focused():
                logger.warning("⚠️  Could not focus browser")
                return False

            logger.info("✅ DSM Package Center opened")
            return True

        except Exception as e:
            self.logger.error(f"Error in open_dsm_package_center: {e}", exc_info=True)
            raise
    def search_for_mailplus(self) -> bool:
        try:
            """Search for MailPlus-Server in Package Center"""
            logger.info("🔍 Searching for MailPlus-Server...")

            if not self.ensure_window_focused():
                return False

            # Use Ctrl+F to search
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)

            # Type search term
            pyautogui.write("MailPlus", interval=0.1)
            time.sleep(1)

            # Press Enter to find
            pyautogui.press('enter')
            time.sleep(1)

            # Close search (Esc)
            pyautogui.press('esc')
            time.sleep(1)

            logger.info("✅ Search completed")
            return True

        except Exception as e:
            self.logger.error(f"Error in search_for_mailplus: {e}", exc_info=True)
            raise
    def click_mailplus_restart(self) -> bool:
        try:
            """Click restart button for MailPlus-Server"""
            logger.info("🖱️  Attempting to click MailPlus-Server restart...")

            if not self.ensure_window_focused():
                return False

            # Strategy: Use keyboard navigation
            # Tab to navigate to MailPlus-Server, then use arrow keys and Enter

            # First, try clicking in the center-right area where action buttons usually are
            if self.browser_window:
                # Calculate approximate position for action menu (three dots)
                # Usually in the right side of the package card
                action_x = self.browser_window.left + int(self.browser_window.width * 0.85)
                action_y = self.browser_window.top + int(self.browser_window.height * 0.4)

                logger.info(f"   Clicking action area: ({action_x}, {action_y})")
                pyautogui.click(action_x, action_y)
                time.sleep(1)

                # Try to find and click "Restart" option
                # This is approximate - may need image recognition
                logger.info("   Looking for Restart option...")

                # Try typing "Restart" to find it
                pyautogui.write("Restart", interval=0.1)
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(2)

                logger.info("✅ Restart action attempted")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error in click_mailplus_restart: {e}", exc_info=True)
            raise
    def wait_for_mailplus_start(self, max_wait: int = 30) -> bool:
        """Wait for MailPlus-Server to start"""
        logger.info(f"⏳ Waiting for MailPlus-Server to start (max {max_wait}s)...")

        # Check status via SSH
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            import paramiko

            nas_integration = NASAzureVaultIntegration()
            credentials = nas_integration.get_nas_credentials()

            if not credentials:
                logger.warning("⚠️  Could not get credentials for status check")
                return False

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect("<NAS_PRIMARY_IP>", username=credentials["username"], password=credentials["password"], timeout=10)

            synopkg_path = "/usr/syno/bin/synopkg"

            for i in range(max_wait // 3):
                stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailPlus-Server")
                status = stdout.read().decode().strip()

                if "is running" in status.lower() or '"status":"start"' in status:
                    logger.info("✅ MailPlus-Server is running!")
                    ssh.close()
                    return True

                time.sleep(3)

            ssh.close()
            logger.warning("⚠️  MailPlus-Server did not start within timeout")
            return False

        except Exception as e:
            logger.warning(f"⚠️  Status check failed: {e}")
            return False

    def execute_automatic_restart(self) -> Dict[str, Any]:
        """Execute automatic restart"""
        logger.info("🚀 JARVIS AUTOMATIC RESTART STARTING")
        logger.info("")

        results = {
            "dsm_opened": False,
            "mailplus_found": False,
            "restart_clicked": False,
            "mailplus_started": False
        }

        # Step 1: Open DSM Package Center
        logger.info("STEP 1: Opening DSM Package Center")
        logger.info("-" * 80)
        if self.open_dsm_package_center():
            results["dsm_opened"] = True
        else:
            logger.error("❌ Failed to open DSM")
            return results

        time.sleep(3)

        # Step 2: Search for MailPlus
        logger.info("")
        logger.info("STEP 2: Searching for MailPlus-Server")
        logger.info("-" * 80)
        if self.search_for_mailplus():
            results["mailplus_found"] = True
        else:
            logger.warning("⚠️  Search may have failed")

        time.sleep(2)

        # Step 3: Click restart
        logger.info("")
        logger.info("STEP 3: Clicking Restart")
        logger.info("-" * 80)
        if self.click_mailplus_restart():
            results["restart_clicked"] = True
        else:
            logger.warning("⚠️  Restart click may have failed")

        # Step 4: Wait for start
        logger.info("")
        logger.info("STEP 4: Waiting for MailPlus-Server to start")
        logger.info("-" * 80)
        if self.wait_for_mailplus_start():
            results["mailplus_started"] = True
        else:
            logger.warning("⚠️  MailPlus-Server may not have started")

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 SUMMARY")
        logger.info("=" * 80)
        logger.info(f"DSM Opened: {'✅' if results['dsm_opened'] else '❌'}")
        logger.info(f"MailPlus Found: {'✅' if results['mailplus_found'] else '❌'}")
        logger.info(f"Restart Clicked: {'✅' if results['restart_clicked'] else '❌'}")
        logger.info(f"MailPlus Started: {'✅' if results['mailplus_started'] else '❌'}")
        logger.info("")

        if results["mailplus_started"]:
            logger.info("✅ SUCCESS! MailPlus-Server is running!")
            logger.info("   Ready for IMAP configuration")
        else:
            logger.warning("⚠️  Automatic restart may not have completed")
            logger.info("   Please check DSM Package Center manually")
            logger.info("   Look for MailPlus-Server and click 'Restart' or 'Start'")

        logger.info("=" * 80)

        return results


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Automatic MailPlus-Server Restart")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        automator = JARVISRestartMailPlusGUI()
        results = automator.execute_automatic_restart()

        if args.json:
            import json
            print(json.dumps(results, indent=2, default=str))

        if results["mailplus_started"]:
            return 0
        else:
            return 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())