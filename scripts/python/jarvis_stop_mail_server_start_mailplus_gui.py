#!/usr/bin/env python3
"""
JARVIS: Stop Mail Server and Start MailPlus via DSM GUI

Uses GUI automation to stop Mail Server and start MailPlus in DSM web interface.

Tags: #JARVIS #MAILPLUS #MAILSERVER #GUI_AUTOMATION #MANUS @JARVIS @LUMINA
"""

import sys
import time
import pyautogui
import pygetwindow as gw
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

logger = get_logger("JARVISMailServerGUI")

# Disable pyautogui failsafe for automation
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.5


class JARVISMailServerGUISwitcher:
    """JARVIS GUI automation for switching Mail Server to MailPlus"""

    def __init__(self):
        """Initialize switcher"""
        self.dsm_url = "https://<NAS_PRIMARY_IP>:5001"
        self.browser_window = None

        logger.info("=" * 80)
        logger.info("🤖 JARVIS: SWITCHING TO MAILPLUS VIA DSM GUI")
        logger.info("=" * 80)
        logger.info("")

    def ensure_window_focused(self) -> bool:
        """Ensure browser window is focused before typing"""
        try:
            # Find browser window (NEO or Edge)
            windows = gw.getWindowsWithTitle("")
            browser_windows = []

            for window in windows:
                title_lower = window.title.lower()
                if any(browser in title_lower for browser in ["neo", "edge", "chrome", "firefox", "dsm", "synology"]):
                    browser_windows.append(window)

            if not browser_windows:
                logger.warning("⚠️  No browser window found")
                return False

            # Use the first browser window found
            self.browser_window = browser_windows[0]

            # Activate and focus the window
            try:
                self.browser_window.activate()
                time.sleep(0.5)

                # Click center of window to ensure focus
                center_x = self.browser_window.left + self.browser_window.width // 2
                center_y = self.browser_window.top + self.browser_window.height // 2
                pyautogui.click(center_x, center_y)
                time.sleep(0.3)

                logger.debug(f"✅ Focused browser window: {self.browser_window.title}")
                return True
            except Exception as e:
                logger.warning(f"⚠️  Could not focus window: {e}")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Window focus check failed: {e}")
            return False

    def open_dsm_package_center(self) -> bool:
        try:
            """Open DSM Package Center"""
            logger.info("📦 Opening DSM Package Center...")

            if not self.ensure_window_focused():
                logger.warning("⚠️  Could not focus browser - opening DSM in new tab")

            # Open DSM in browser
            import webbrowser
            webbrowser.open(f"{self.dsm_url}/#packages")
            time.sleep(3)

            # Ensure window is focused
            if not self.ensure_window_focused():
                logger.warning("⚠️  Could not focus browser window")
                return False

            logger.info("✅ DSM Package Center opened")
            return True

        except Exception as e:
            self.logger.error(f"Error in open_dsm_package_center: {e}", exc_info=True)
            raise
    def stop_mail_server(self) -> bool:
        try:
            """Stop Mail Server via Package Center"""
            logger.info("🛑 Stopping Mail Server...")
            logger.info("")

            if not self.open_dsm_package_center():
                return False

            time.sleep(2)

            if not self.ensure_window_focused():
                logger.warning("⚠️  Could not focus browser")
                return False

            # Search for Mail Server
            logger.info("   Searching for Mail Server...")
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            pyautogui.write("Mail Server", interval=0.1)
            time.sleep(1)
            pyautogui.press('esc')  # Close search

            # Look for Mail Server package and click Stop
            # This is approximate - may need adjustment based on actual UI
            logger.info("   Looking for Mail Server package...")
            time.sleep(2)

            # Try to find and click Stop button
            # Note: This is a simplified approach - actual UI may vary
            logger.warning("⚠️  Manual intervention may be required:")
            logger.info("   1. Find 'Mail Server' in Package Center")
            logger.info("   2. Click on it")
            logger.info("   3. Click 'Stop' button")
            logger.info("   4. Wait for it to stop")
            logger.info("")

            return False  # Return False to indicate manual step needed

        except Exception as e:
            self.logger.error(f"Error in stop_mail_server: {e}", exc_info=True)
            raise
    def start_mailplus(self) -> bool:
        try:
            """Start MailPlus via Package Center"""
            logger.info("🚀 Starting MailPlus...")
            logger.info("")

            if not self.open_dsm_package_center():
                return False

            time.sleep(2)

            if not self.ensure_window_focused():
                logger.warning("⚠️  Could not focus browser")
                return False

            # Search for MailPlus
            logger.info("   Searching for MailPlus...")
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            pyautogui.write("MailPlus", interval=0.1)
            time.sleep(1)
            pyautogui.press('esc')  # Close search

            # Look for MailPlus package and click Start
            logger.info("   Looking for MailPlus package...")
            time.sleep(2)

            # Try to find and click Start button
            logger.warning("⚠️  Manual intervention may be required:")
            logger.info("   1. Find 'MailPlus Server' in Package Center")
            logger.info("   2. Click on it")
            logger.info("   3. Click 'Start' button")
            logger.info("   4. Wait for it to start")
            logger.info("")

            return False  # Return False to indicate manual step needed

        except Exception as e:
            self.logger.error(f"Error in start_mailplus: {e}", exc_info=True)
            raise
    def execute_switch(self) -> Dict[str, Any]:
        try:
            """Execute complete switch via GUI"""
            logger.info("🚀 JARVIS GUI SWITCH STARTING")
            logger.info("")

            results = {
                "mail_server_stopped": False,
                "mailplus_started": False,
                "method": "gui_automation"
            }

            logger.info("=" * 80)
            logger.info("📋 MANUAL STEPS REQUIRED")
            logger.info("=" * 80)
            logger.info("")
            logger.info("Due to DSM web interface complexity, manual steps are recommended:")
            logger.info("")
            logger.info("STEP 1: Stop Mail Server")
            logger.info("   1. Open DSM: https://<NAS_PRIMARY_IP>:5001")
            logger.info("   2. Go to: Package Center")
            logger.info("   3. Find: Mail Server")
            logger.info("   4. Click: Stop (if running)")
            logger.info("   5. Wait: Until it shows 'Stopped'")
            logger.info("")
            logger.info("STEP 2: Start MailPlus")
            logger.info("   1. In Package Center, find: MailPlus Server")
            logger.info("   2. Click: Start")
            logger.info("   3. Wait: Until it shows 'Running'")
            logger.info("")
            logger.info("ALTERNATIVE: Use DSM Main Menu")
            logger.info("   1. Open DSM: https://<NAS_PRIMARY_IP>:5001")
            logger.info("   2. Main Menu → MailPlus")
            logger.info("   3. If you see the error about Mail Server, go to:")
            logger.info("      Package Center → Mail Server → Stop")
            logger.info("   4. Then return to MailPlus and it should start")
            logger.info("")
            logger.info("=" * 80)
            logger.info("")

            # Try to open DSM for user
            logger.info("🌐 Opening DSM in browser...")
            import webbrowser
            webbrowser.open(f"{self.dsm_url}/#packages")
            logger.info("✅ DSM Package Center opened in browser")
            logger.info("   Please follow the manual steps above")
            logger.info("")

            return results


        except Exception as e:
            self.logger.error(f"Error in execute_switch: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Switch Mail Server to MailPlus via GUI")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    switcher = JARVISMailServerGUISwitcher()
    results = switcher.execute_switch()

    if args.json:
        import json
        print(json.dumps(results, indent=2, default=str))

    return 0


if __name__ == "__main__":


    sys.exit(main())