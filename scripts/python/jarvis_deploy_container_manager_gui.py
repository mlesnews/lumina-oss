#!/usr/bin/env python3
"""
JARVIS Deploy Container Manager Project via GUI Automation

Automates Container Manager project creation via DSM GUI.
Uses UI automation to navigate and deploy docker-compose project.

Tags: #JARVIS #CONTAINER_MANAGER #GUI_AUTOMATION #MANUS #DOIT
@JARVIS @LUMINA @MANUS @SCOTTY @DOIT
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

logger = get_logger("JARVISContainerManagerDeploy")


class JARVISContainerManagerDeployer:
    """JARVIS Container Manager GUI Deployer"""

    def __init__(self, project_name: str = "homelab-ide-notification-handler", 
                 compose_file_path: str = "/volume1/docker/homelab-ide-notification-handler/docker-compose.yml"):
        """Initialize deployer"""
        self.dsm_url = "https://<NAS_PRIMARY_IP>:5001"
        self.project_name = project_name
        self.compose_file_path = compose_file_path
        self.browser_window = None

        if not GUI_AVAILABLE:
            logger.error("❌ pyautogui/pygetwindow not available")
            logger.info("   Install: pip install pyautogui pygetwindow")
            raise ImportError("GUI automation libraries not available")

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
                time.sleep(5)  # Wait for browser to open and load
                return True
            except Exception as e:
                logger.warning(f"⚠️  Failed to open NEO: {e}")

        # Fallback
        try:
            webbrowser.open(self.dsm_url)
            logger.info("✅ Opened DSM in default browser")
            time.sleep(5)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to open browser: {e}")
            return False

    def find_browser_window(self) -> bool:
        """Find browser window"""
        try:
            time.sleep(2)
            windows = gw.getWindowsWithTitle("")
            for window in windows:
                if window.visible:
                    title_lower = window.title.lower()
                    if any(browser in title_lower for browser in ["neo", "edge", "chrome", "firefox"]):
                        if "<NAS_PRIMARY_IP>" in window.title or "dsm" in title_lower or "synology" in title_lower:
                            self.browser_window = window
                            logger.info(f"✅ Found browser window: {window.title}")
                            return True

            # Try to find any large browser window
            for window in windows:
                if window.visible and (window.width > 800 and window.height > 600):
                    self.browser_window = window
                    logger.info(f"✅ Using browser window: {window.title}")
                    return True
        except Exception as e:
            logger.debug(f"Window search error: {e}")

        return False

    def ensure_window_focused(self) -> bool:
        """Ensure browser window is focused"""
        if not self.browser_window:
            return False

        try:
            if not self.browser_window.isActive:
                self.browser_window.activate()
                time.sleep(1)
            self.browser_window.maximize()
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.warning(f"⚠️  Could not focus window: {e}")
            return False

    def navigate_to_container_manager(self) -> bool:
        """Navigate to Container Manager in DSM"""
        logger.info("🧭 Navigating to Container Manager...")

        if not self.ensure_window_focused():
            return False

        try:
            # Click on Main Menu (top left)
            logger.info("   📍 Clicking Main Menu...")
            pyautogui.click(50, 50)  # Approximate Main Menu location
            time.sleep(1)

            # Type "Container" to search/filter
            logger.info("   ⌨️  Typing 'Container'...")
            pyautogui.write("Container", interval=0.1)
            time.sleep(1)

            # Press Enter or click Container Manager
            logger.info("   ⏎ Pressing Enter...")
            pyautogui.press('enter')
            time.sleep(3)  # Wait for Container Manager to load

            logger.info("✅ Navigated to Container Manager")
            return True
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False

    def create_project_from_compose(self) -> bool:
        """Create project from compose file"""
        logger.info("📦 Creating project from compose file...")

        if not self.ensure_window_focused():
            return False

        try:
            # Click on "Project" tab
            logger.info("   📍 Clicking Project tab...")
            # Try to find and click Project button (usually top menu)
            pyautogui.click(200, 100)  # Approximate Project tab location
            time.sleep(1)

            # Click "Create" button
            logger.info("   📍 Clicking Create button...")
            pyautogui.click(300, 150)  # Approximate Create button location
            time.sleep(1)

            # Select "From Compose File"
            logger.info("   📍 Selecting 'From Compose File'...")
            pyautogui.click(400, 200)  # Approximate menu item location
            time.sleep(2)

            # Enter project name
            logger.info(f"   ⌨️  Entering project name: {self.project_name}...")
            pyautogui.write(self.project_name, interval=0.1)
            time.sleep(1)

            # Enter compose file path
            logger.info(f"   ⌨️  Entering compose file path...")
            pyautogui.press('tab')  # Move to path field
            time.sleep(0.5)
            pyautogui.write(self.compose_file_path, interval=0.1)
            time.sleep(1)

            # Click Create/OK button
            logger.info("   📍 Clicking Create button...")
            pyautogui.press('enter')  # Or click OK/Create button
            time.sleep(5)  # Wait for deployment to start

            logger.info("✅ Project creation initiated")
            return True
        except Exception as e:
            logger.error(f"❌ Project creation failed: {e}")
            return False

    def deploy(self) -> Dict[str, Any]:
        """Execute full deployment"""
        logger.info("=" * 80)
        logger.info("🚀 JARVIS Container Manager GUI Deployment")
        logger.info("=" * 80)
        logger.info("")

        try:
            # Step 1: Open DSM
            if not self.open_dsm_in_browser():
                return {"success": False, "error": "Failed to open DSM"}

            # Step 2: Find browser window
            if not self.find_browser_window():
                return {"success": False, "error": "Failed to find browser window"}

            # Step 3: Navigate to Container Manager
            if not self.navigate_to_container_manager():
                return {"success": False, "error": "Failed to navigate to Container Manager"}

            # Step 4: Create project
            if not self.create_project_from_compose():
                return {"success": False, "error": "Failed to create project"}

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ DEPLOYMENT INITIATED")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📋 Next Steps:")
            logger.info("   1. Monitor deployment in Container Manager")
            logger.info("   2. Check container logs when ready")
            logger.info("")

            return {"success": True, "message": "Deployment initiated via GUI"}
        except Exception as e:
            logger.error(f"❌ Deployment error: {e}")
            return {"success": False, "error": str(e)}


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy Container Manager project via GUI")
    parser.add_argument('--project-name', type=str, 
                       default="homelab-ide-notification-handler",
                       help='Project name')
    parser.add_argument('--compose-file', type=str,
                       default="/volume1/docker/homelab-ide-notification-handler/docker-compose.yml",
                       help='Path to docker-compose.yml on NAS')

    args = parser.parse_args()

    deployer = JARVISContainerManagerDeployer(
        project_name=args.project_name,
        compose_file_path=args.compose_file
    )

    result = deployer.deploy()
    return 0 if result.get("success") else 1


if __name__ == "__main__":


    sys.exit(main())