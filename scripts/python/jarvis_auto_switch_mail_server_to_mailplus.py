#!/usr/bin/env python3
"""
JARVIS: Automatic Switch from Mail Server to MailPlus

Fully automated script that stops Mail Server and starts MailPlus using multiple methods.

Tags: #JARVIS #MAILPLUS #MAILSERVER #AUTOMATION #FULLAUTO @JARVIS @LUMINA @DOIT
"""

import sys
import time
import pyautogui
import pygetwindow as gw
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

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

logger = get_logger("JARVISAutoMailSwitch")

# Disable pyautogui failsafe for automation
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.5


class JARVISAutoMailServerSwitcher:
    """JARVIS fully automated Mail Server to MailPlus switcher"""

    def __init__(self):
        """Initialize switcher"""
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.dsm_url = f"https://{self.nas_ip}:5001"
        self.browser_window = None

        logger.info("=" * 80)
        logger.info("🤖 JARVIS: AUTOMATIC MAIL SERVER → MAILPLUS SWITCH")
        logger.info("=" * 80)
        logger.info("")

    def ensure_window_focused(self) -> bool:
        """Ensure browser window is focused before typing"""
        try:
            windows = gw.getWindowsWithTitle("")
            browser_windows = []

            for window in windows:
                title_lower = window.title.lower()
                if any(browser in title_lower for browser in ["neo", "edge", "chrome", "firefox", "dsm", "synology"]):
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

                logger.debug(f"✅ Focused browser window: {self.browser_window.title}")
                return True
            except Exception as e:
                logger.warning(f"⚠️  Could not focus window: {e}")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Window focus check failed: {e}")
            return False

    def try_ssh_full_path(self) -> Tuple[bool, bool]:
        """Try SSH with full path to synopkg"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            import paramiko

            nas_integration = NASAzureVaultIntegration()
            credentials = nas_integration.get_nas_credentials()

            if not credentials:
                return False, False

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.nas_ip,
                username=credentials["username"],
                password=credentials["password"],
                timeout=10
            )

            # Try full path to synopkg
            logger.info("🔌 Attempting SSH with full path to synopkg...")

            # Find synopkg location
            stdin, stdout, stderr = ssh.exec_command("which synopkg || find /usr -name synopkg 2>/dev/null | head -1")
            synopkg_path = stdout.read().decode().strip()

            if not synopkg_path:
                # Try common locations
                for path in ["/usr/syno/bin/synopkg", "/usr/local/bin/synopkg", "/bin/synopkg"]:
                    stdin, stdout, stderr = ssh.exec_command(f"test -f {path} && echo {path} || echo ''")
                    if stdout.read().decode().strip():
                        synopkg_path = path
                        break

            if not synopkg_path:
                logger.warning("⚠️  Could not find synopkg")
                ssh.close()
                return False, False

            logger.info(f"✅ Found synopkg at: {synopkg_path}")

            # Check Mail Server status
            stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailServer")
            mail_server_status = stdout.read().decode().strip()

            # Check MailPlus status
            stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailPlus")
            mailplus_status = stdout.read().decode().strip()

            mail_server_running = "is running" in mail_server_status.lower()
            mailplus_running = "is running" in mailplus_status.lower()

            logger.info(f"Mail Server: {'Running' if mail_server_running else 'Stopped'}")
            logger.info(f"MailPlus: {'Running' if mailplus_running else 'Stopped'}")

            # Stop Mail Server if running
            if mail_server_running:
                logger.info("🛑 Stopping Mail Server...")
                stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} stop MailServer")
                stdout.read()  # Wait for completion
                time.sleep(3)

                # Verify stopped
                stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailServer")
                new_status = stdout.read().decode().strip()
                if "is stopped" in new_status.lower() or "is not running" in new_status.lower():
                    logger.info("✅ Mail Server stopped")
                    mail_server_running = False
                else:
                    logger.warning(f"⚠️  Mail Server status unclear: {new_status}")

            # Start MailPlus if not running
            if not mailplus_running and not mail_server_running:
                logger.info("🚀 Starting MailPlus...")
                stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} start MailPlus")
                stdout.read()  # Wait for completion
                time.sleep(5)

                # Verify started
                stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailPlus")
                new_status = stdout.read().decode().strip()
                if "is running" in new_status.lower():
                    logger.info("✅ MailPlus started")
                    mailplus_running = True
                else:
                    logger.warning(f"⚠️  MailPlus status unclear: {new_status}")

            ssh.close()

            return not mail_server_running, mailplus_running

        except ImportError:
            logger.warning("⚠️  paramiko not available")
            return False, False
        except Exception as e:
            logger.warning(f"⚠️  SSH method failed: {e}")
            return False, False

    def try_dsm_api_alternative(self) -> Tuple[bool, bool]:
        """Try alternative DSM API methods"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            from synology_api_base import SynologyAPIBase

            nas_integration = NASAzureVaultIntegration()
            credentials = nas_integration.get_nas_credentials()

            if not credentials:
                return False, False

            logger.info("🔌 Attempting DSM API alternative methods...")
            api = SynologyAPIBase(nas_ip=self.nas_ip, nas_port=5001, verify_ssl=False)

            if not api.login(credentials["username"], credentials["password"]):
                logger.error("❌ Failed to login to DSM")
                return False, False

            logger.info("✅ Connected to DSM API")

            # Try Package Manager API
            package_url = f"{api.base_url}/webapi/entry.cgi"

            # List packages to find correct names
            params = {
                "api": "SYNO.Core.Package",
                "version": "1",
                "method": "list",
                "_sid": api.sid
            }

            response = api.session.get(package_url, params=params, timeout=10)
            data = response.json()

            if data.get("success"):
                packages = data.get("data", {}).get("packages", [])

                # Find Mail Server and MailPlus
                mail_server_pkg = None
                mailplus_pkg = None

                for pkg in packages:
                    name = pkg.get("name", "").lower()
                    if "mail server" in name and "mailplus" not in name:
                        mail_server_pkg = pkg
                    elif "mailplus" in name:
                        mailplus_pkg = pkg

                # Stop Mail Server if running
                if mail_server_pkg and mail_server_pkg.get("status") == "running":
                    logger.info("🛑 Stopping Mail Server via API...")
                    stop_params = {
                        "api": "SYNO.Core.Package",
                        "version": "1",
                        "method": "stop",
                        "id": mail_server_pkg.get("id"),
                        "_sid": api.sid
                    }
                    response = api.session.get(package_url, params=stop_params, timeout=10)
                    if response.json().get("success"):
                        logger.info("✅ Mail Server stopped")
                        time.sleep(3)

                # Start MailPlus if not running
                if mailplus_pkg and mailplus_pkg.get("status") != "running":
                    logger.info("🚀 Starting MailPlus via API...")
                    start_params = {
                        "api": "SYNO.Core.Package",
                        "version": "1",
                        "method": "start",
                        "id": mailplus_pkg.get("id"),
                        "_sid": api.sid
                    }
                    response = api.session.get(package_url, params=start_params, timeout=10)
                    if response.json().get("success"):
                        logger.info("✅ MailPlus started")
                        time.sleep(5)
                        api.logout()
                        return True, True

            api.logout()
            return False, False

        except Exception as e:
            logger.warning(f"⚠️  DSM API alternative failed: {e}")
            return False, False

    def try_gui_automation(self) -> Tuple[bool, bool]:
        try:
            """Try GUI automation via browser"""
            logger.info("🖥️  Attempting GUI automation...")

            # Open DSM Package Center
            logger.info("   Opening DSM Package Center...")
            webbrowser.open(f"{self.dsm_url}/#packages")
            time.sleep(5)

            if not self.ensure_window_focused():
                logger.warning("⚠️  Could not focus browser")
                return False, False

            logger.warning("⚠️  GUI automation requires manual interaction")
            logger.info("   Please follow on-screen prompts")
            logger.info("   1. Find 'Mail Server' and click 'Stop'")
            logger.info("   2. Find 'MailPlus Server' and click 'Start'")

            return False, False

        except Exception as e:
            self.logger.error(f"Error in try_gui_automation: {e}", exc_info=True)
            raise
    def execute_automatic_switch(self) -> Dict[str, Any]:
        """Execute automatic switch using best available method"""
        logger.info("🚀 JARVIS AUTOMATIC SWITCH STARTING")
        logger.info("")

        results = {
            "mail_server_stopped": False,
            "mailplus_started": False,
            "method_used": None
        }

        # Method 1: Try SSH with full path
        logger.info("METHOD 1: SSH with full path to synopkg")
        logger.info("-" * 80)
        mail_stopped, mailplus_started = self.try_ssh_full_path()

        if mail_stopped and mailplus_started:
            results["mail_server_stopped"] = True
            results["mailplus_started"] = True
            results["method_used"] = "ssh_full_path"
            logger.info("✅ SUCCESS via SSH!")
            return results

        logger.info("")

        # Method 2: Try DSM API alternative
        logger.info("METHOD 2: DSM API Package Manager")
        logger.info("-" * 80)
        mail_stopped, mailplus_started = self.try_dsm_api_alternative()

        if mail_stopped and mailplus_started:
            results["mail_server_stopped"] = True
            results["mailplus_started"] = True
            results["method_used"] = "dsm_api_package"
            logger.info("✅ SUCCESS via DSM API!")
            return results

        logger.info("")

        # Method 3: GUI automation (opens browser for manual steps)
        logger.info("METHOD 3: GUI Automation")
        logger.info("-" * 80)
        mail_stopped, mailplus_started = self.try_gui_automation()

        if mail_stopped and mailplus_started:
            results["mail_server_stopped"] = True
            results["mailplus_started"] = True
            results["method_used"] = "gui_automation"
        else:
            results["method_used"] = "gui_manual_required"

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 AUTOMATIC SWITCH SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Mail Server Stopped: {'✅ Yes' if results['mail_server_stopped'] else '❌ No'}")
        logger.info(f"MailPlus Started: {'✅ Yes' if results['mailplus_started'] else '❌ No'}")
        logger.info(f"Method Used: {results['method_used'] or 'None'}")
        logger.info("")

        if results["mail_server_stopped"] and results["mailplus_started"]:
            logger.info("✅ AUTOMATIC SWITCH COMPLETE!")
            logger.info("   MailPlus Server is now running and ready for IMAP configuration")
        else:
            logger.info("⚠️  Automatic switch partially complete")
            logger.info("   DSM Package Center has been opened in your browser")
            logger.info("   Please manually:")
            logger.info("   1. Stop 'Mail Server' in Package Center")
            logger.info("   2. Start 'MailPlus Server' in Package Center")

        logger.info("=" * 80)

        return results


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Automatic Mail Server to MailPlus Switch")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        switcher = JARVISAutoMailServerSwitcher()
        results = switcher.execute_automatic_switch()

        if args.json:
            import json
            print(json.dumps(results, indent=2, default=str))

        if results["mail_server_stopped"] and results["mailplus_started"]:
            return 0
        elif results["mail_server_stopped"]:
            return 1
        else:
            return 2


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())