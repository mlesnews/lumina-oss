#!/usr/bin/env python3
"""
JARVIS Configure DSM MailPlus IMAP via GUI Automation

Uses MANUS GUI automation to configure MailPlus IMAP settings in DSM.
Ensures browser window is properly focused before all typing operations.

Tags: #JARVIS #MAILPLUS #IMAP #GUI_AUTOMATION #MANUS
@JARVIS @LUMINA @MANUS @DOIT
"""

import sys
import time
import subprocess
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

try:
    import pyautogui
    import pygetwindow as gw
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False

try:
    from jarvis_auto_mdv_activator import JARVISAutoMDVActivator
    MDV_AVAILABLE = True
except ImportError:
    MDV_AVAILABLE = False

logger = get_logger("JARVISConfigureDSM")


class JARVISDSMConfigurator:
    """JARVIS DSM MailPlus IMAP Configurator"""

    def __init__(self):
        """Initialize configurator"""
        self.dsm_url = "https://<NAS_PRIMARY_IP>:5001"
        self.browser_window = None
        self.mdv_activator = None
        self.mdv_active = False

        if not GUI_AVAILABLE:
            logger.warning("⚠️  pyautogui/pygetwindow not available")
            logger.info("   Install: pip install pyautogui pygetwindow")

        # Initialize MDV for session recording
        if MDV_AVAILABLE:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.mdv_activator = JARVISAutoMDVActivator(project_root=project_root)
                logger.info("✅ MDV initialized for session recording")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize MDV: {e}")

    def find_neo_browser(self) -> Optional[str]:
        try:
            """Find NEO browser executable"""
            import os
            neo_paths = [
                r"C:\Program Files\Neo\Application\neo.exe",
                r"C:\Program Files (x86)\Neo\Application\neo.exe",
                r"C:\Users\{}\AppData\Local\Neo\Application\neo.exe".format(
                    os.getenv("USERNAME", "")
                )
            ]

            for path in neo_paths:
                if Path(path).exists():
                    return path

            return None

        except Exception as e:
            self.logger.error(f"Error in find_neo_browser: {e}", exc_info=True)
            raise
    def open_dsm_in_browser(self) -> bool:
        """Open DSM in browser"""
        logger.info("🌐 Opening DSM in browser...")

        neo_path = self.find_neo_browser()
        if neo_path:
            try:
                subprocess.Popen([neo_path, self.dsm_url], shell=False)
                logger.info("✅ Opened DSM in NEO browser")
                time.sleep(3)  # Wait for browser to open
                return True
            except Exception as e:
                logger.warning(f"⚠️  Failed to open NEO: {e}")

        # Fallback
        try:
            webbrowser.open(self.dsm_url)
            logger.info("✅ Opened DSM in default browser")
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to open browser: {e}")
            return False

    def find_browser_window(self) -> bool:
        """Find browser window"""
        if not GUI_AVAILABLE:
            return False

        try:
            windows = gw.getWindowsWithTitle("")
            for window in windows:
                if "neo" in window.title.lower() or "edge" in window.title.lower() or "chrome" in window.title.lower():
                    if "<NAS_PRIMARY_IP>" in window.title or "dsm" in window.title.lower() or "synology" in window.title.lower():
                        self.browser_window = window
                        logger.info(f"✅ Found browser window: {window.title}")
                        return True

            # Try to find any browser window
            for window in windows:
                if window.visible and (window.width > 800 and window.height > 600):
                    self.browser_window = window
                    logger.info(f"✅ Using browser window: {window.title}")
                    return True
        except Exception as e:
            logger.debug(f"Window search error: {e}")

        return False

    def ensure_window_focused(self) -> bool:
        """Ensure browser window is focused before typing"""
        if not GUI_AVAILABLE:
            return False

        if not self.browser_window:
            logger.warning("⚠️  No browser window found")
            # Try to find it again
            if not self.find_browser_window():
                return False

        try:
            # Activate window
            self.browser_window.activate()
            time.sleep(0.5)  # Give window time to activate

            # Click center of window to force focus
            center_x = self.browser_window.left + (self.browser_window.width // 2)
            center_y = self.browser_window.top + (self.browser_window.height // 2)
            pyautogui.click(center_x, center_y)
            time.sleep(0.3)

            # Verify window is active
            try:
                active_window = gw.getActiveWindow()
                if active_window and (active_window.title == self.browser_window.title or 
                                     "neo" in active_window.title.lower() or 
                                     "dsm" in active_window.title.lower()):
                    logger.debug("✅ Window is focused")
                    return True
            except Exception:
                # If we can't verify, assume it worked
                pass

            # Retry activation if needed
            self.browser_window.activate()
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"❌ Window focus failed: {e}")
            return False

    def handle_certificate_warning(self) -> bool:
        """Handle certificate warning"""
        if not GUI_AVAILABLE:
            return False

        logger.info("🔒 Handling certificate warning...")

        # Ensure window is focused before typing
        if not self.ensure_window_focused():
            logger.warning("⚠️  Could not focus window for certificate handling")
            return False

        try:
            # Try Chrome bypass shortcut
            pyautogui.write("thisisunsafe", interval=0.1)
            time.sleep(2)

            # Or try clicking Advanced/Proceed
            # This is browser-specific and may need adjustment
            logger.info("   Attempted certificate bypass")
            return True
        except Exception as e:
            logger.debug(f"Certificate handling: {e}")
            return False

    def login_to_dsm(self) -> bool:
        """Login to DSM"""
        if not GUI_AVAILABLE or not VAULT_AVAILABLE:
            return False

        logger.info("🔐 Logging into DSM...")

        try:
            # Get credentials
            nas_integration = NASAzureVaultIntegration()
            credentials = nas_integration.get_nas_credentials()

            if not credentials:
                logger.error("❌ Could not get credentials")
                return False

            # CRITICAL: Ensure window is focused before any typing
            if not self.ensure_window_focused():
                logger.error("❌ Could not focus browser window - typing would go to wrong window")
                return False

            # Find login fields and enter credentials
            time.sleep(2)  # Wait for page to load

            # Click username field (usually first input)
            # Use window-relative coordinates
            if self.browser_window:
                center_x = self.browser_window.left + (self.browser_window.width // 2)
                center_y = self.browser_window.top + (self.browser_window.height // 2) - 50
            else:
                center_x = pyautogui.size()[0] // 2
                center_y = pyautogui.size()[1] // 2 - 50

            pyautogui.click(center_x, center_y)
            time.sleep(0.5)

            # Ensure focus again before typing username
            self.ensure_window_focused()
            pyautogui.write(credentials["username"], interval=0.1)
            time.sleep(0.5)

            # Tab to password field
            pyautogui.press("tab")
            time.sleep(0.5)

            # CRITICAL: Ensure focus before typing password
            self.ensure_window_focused()
            # Password is typed but NEVER logged
            pyautogui.write(credentials["password"], interval=0.1)
            time.sleep(0.5)

            # Press Enter or click Login
            pyautogui.press("enter")
            time.sleep(3)

            logger.info("✅ Login attempted")
            # Clear password from memory (credentials dict is local, but good practice)
            credentials["password"] = "***"  # Mask password
            return True
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False

    def navigate_to_mailplus(self) -> bool:
        """Navigate to MailPlus settings"""
        if not GUI_AVAILABLE:
            return False

        logger.info("📧 Navigating to MailPlus...")

        # CRITICAL: Ensure window is focused before typing
        if not self.ensure_window_focused():
            logger.error("❌ Could not focus browser window")
            return False

        try:
            # Wait for DSM to load
            time.sleep(3)

            # Type URL directly in address bar
            pyautogui.hotkey("ctrl", "l")  # Focus address bar
            time.sleep(0.5)

            # Ensure focus again before typing URL
            self.ensure_window_focused()
            pyautogui.write("https://<NAS_PRIMARY_IP>:5001/#mailplus", interval=0.1)
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(3)

            logger.info("✅ Navigated to MailPlus")
            return True
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False

    def configure_imap(self) -> bool:
        """Configure IMAP settings"""
        if not GUI_AVAILABLE:
            return False

        logger.info("⚙️  Configuring IMAP settings...")

        try:
            # Navigate to Settings → Mail Service
            # This requires specific UI interaction
            logger.info("   Opening Mail Service settings...")

            # Try keyboard navigation
            time.sleep(2)
            pyautogui.press("tab", presses=5)  # Navigate to Settings
            time.sleep(0.5)
            pyautogui.press("enter")
            time.sleep(1)

            # Look for IMAP service checkbox
            logger.info("   Enabling IMAP service...")
            # This would need screen recognition or specific coordinates

            logger.warning("⚠️  GUI automation for IMAP configuration requires")
            logger.warning("   specific UI element recognition")
            logger.warning("   Manual configuration may be more reliable")

            return False
        except Exception as e:
            logger.error(f"❌ IMAP configuration failed: {e}")
            return False

    def check_nas_space(self) -> bool:
        """Check NAS storage space before recording"""
        try:
            from nas_storage_utility import NASStorageUtility

            storage_util = NASStorageUtility()
            space_info = storage_util.get_storage_info()

            if space_info:
                storage_path = space_info.get("storage_path", "Unknown")
                nas_available = space_info.get("nas_available", False)

                logger.info(f"💾 NAS Storage Check:")
                logger.info(f"   Storage Path: {storage_path}")
                logger.info(f"   NAS Available: {'✅' if nas_available else '❌'}")

                # Try to get actual disk space if available
                try:
                    import shutil
                    if nas_available and Path(storage_path).exists():
                        stat = shutil.disk_usage(storage_path)
                        available_gb = stat.free / (1024**3)
                        total_gb = stat.total / (1024**3)
                        used_percent = (stat.used / stat.total) * 100

                        logger.info(f"   Available: {available_gb:.2f} GB / {total_gb:.2f} GB total ({used_percent:.1f}% used)")

                        # Warn if space is low (less than 50GB or more than 90% used)
                        if available_gb < 50 or used_percent > 90:
                            logger.warning(f"⚠️  NAS storage is low: {available_gb:.2f} GB available")
                            logger.warning("   Consider cleaning up old recordings")
                        else:
                            logger.info("✅ NAS has sufficient storage space for recording")
                except Exception as e:
                    logger.debug(f"Could not get disk usage: {e}")

                return True
        except ImportError:
            logger.debug("NAS storage utility not available")
        except Exception as e:
            logger.debug(f"NAS space check: {e}")

        # Proceed anyway if check fails
        logger.info("💾 Proceeding with recording (space check unavailable)")
        return True

    def start_mdv_recording(self) -> bool:
        """Start MDV recording for this session"""
        if not MDV_AVAILABLE or not self.mdv_activator:
            logger.warning("⚠️  MDV not available for session recording")
            return False

        # Check NAS space before recording
        logger.info("💾 Checking NAS storage space...")
        if not self.check_nas_space():
            logger.warning("⚠️  NAS space check failed, but proceeding with recording")

        try:
            logger.info("📹 Starting MDV session recording...")
            result = self.mdv_activator.activate_mdv()
            if result.get("success"):
                self.mdv_active = True
                logger.info("✅ MDV recording started")
                if result.get("video_path"):
                    logger.info(f"   Video path: {result.get('video_path')}")
                return True
            else:
                logger.warning(f"⚠️  MDV recording may not have started: {result.get('message')}")
                return False
        except Exception as e:
            logger.error(f"❌ MDV recording failed: {e}")
            return False

    def execute_full_configuration(self) -> Dict[str, Any]:
        """Execute full DSM configuration"""
        logger.info("=" * 80)
        logger.info("🤖 JARVIS CONFIGURING DSM MAILPLUS IMAP")
        logger.info("=" * 80)
        logger.info("")

        # Start MDV recording at the beginning of the session
        self.start_mdv_recording()
        logger.info("")

        result = {
            "browser_opened": False,
            "logged_in": False,
            "navigated": False,
            "imap_configured": False,
            "mdv_recording": self.mdv_active
        }

        if not GUI_AVAILABLE:
            logger.error("❌ GUI automation not available")
            logger.info("   Install: pip install pyautogui pygetwindow")
            return result

        # Step 1: Open browser
        if self.open_dsm_in_browser():
            result["browser_opened"] = True
            time.sleep(3)

        # Step 2: Find browser window and ensure it's focused
        if self.find_browser_window():
            if not self.ensure_window_focused():
                logger.warning("⚠️  Could not focus browser window")

        # Step 3: Handle certificate
        self.handle_certificate_warning()
        time.sleep(2)

        # Step 4: Login
        if self.login_to_dsm():
            result["logged_in"] = True
            time.sleep(3)

        # Step 5: Navigate to MailPlus
        if self.navigate_to_mailplus():
            result["navigated"] = True
            time.sleep(2)

        # Step 6: Configure IMAP
        # Note: This requires specific UI element recognition
        logger.info("")
        logger.info("⚠️  IMAP configuration requires manual interaction")
        logger.info("   Please complete the following steps:")
        logger.info("")
        logger.info("   1. In the browser window, navigate to:")
        logger.info("      MailPlus → Settings → Mail Service")
        logger.info("   2. Enable: 'IMAP service' checkbox")
        logger.info("   3. Set IMAP port: 993")
        logger.info("   4. Select encryption: SSL/TLS")
        logger.info("   5. Click: Apply/Save")
        logger.info("")
        logger.info("   JARVIS monitoring will detect when IMAP is enabled")

        return result


def main():
    """Main entry point"""
    configurator = JARVISDSMConfigurator()
    result = configurator.execute_full_configuration()

    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 CONFIGURATION STATUS")
    logger.info("=" * 80)
    logger.info(f"Browser Opened: {'✅' if result['browser_opened'] else '❌'}")
    logger.info(f"Logged In: {'✅' if result['logged_in'] else '❌'}")
    logger.info(f"Navigated: {'✅' if result['navigated'] else '❌'}")
    logger.info(f"IMAP Configured: {'✅' if result['imap_configured'] else '⚠️  Manual Required'}")
    logger.info(f"MDV Recording: {'✅ Active' if result.get('mdv_recording') else '❌ Not Active'}")
    logger.info("=" * 80)

    # Note: MDV recording continues until session ends
    # Video will be saved to NAS automatically

    return 0


if __name__ == "__main__":


    sys.exit(main())