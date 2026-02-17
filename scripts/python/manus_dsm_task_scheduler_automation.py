#!/usr/bin/env python3
"""
MANUS DSM Task Scheduler Automation
Automates DSM Task Scheduler UI to install cron tasks via RDP/MANUS
#JARVIS #MANUS #NAS #DSM #AUTOMATION #RDP
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import json
import time

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False

logger = get_logger("MANUSDSMTaskScheduler")


class DSMTaskSchedulerAutomation:
    """Automate DSM Task Scheduler via browser"""

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 5001, project_root: Path = None):
        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.dsm_url = f"https://{nas_ip}:{nas_port}"
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.credentials: Optional[Dict[str, str]] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

    def _get_credentials(self) -> bool:
        """Get DSM credentials from Azure Key Vault"""
        if not VAULT_AVAILABLE:
            logger.error("Azure Vault integration not available")
            return False

        try:
            vault = NASAzureVaultIntegration()
            self.credentials = vault.get_nas_credentials()
            if not self.credentials:
                logger.error("Could not retrieve credentials")
                return False
            return True
        except Exception as e:
            logger.error(f"Error getting credentials: {e}")
            return False

    def _setup_browser(self, headless: bool = False) -> bool:
        """Setup Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available. Install with: pip install playwright && playwright install")
            return False

        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--ignore-certificate-errors',
                    '--ignore-ssl-errors',
                    '--ignore-certificate-errors-spki-list',
                    '--disable-web-security'
                ],
                slow_mo=500  # Slow down for better reliability
            )

            # Create context with SSL verification disabled
            self.context = self.browser.new_context(
                ignore_https_errors=True,
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = self.context.new_page()

            # Set longer timeout
            self.page.set_default_timeout(30000)

            logger.info("✅ Browser initialized")
            logger.info("   Note: Browser will stay open for manual verification if needed")
            return True
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            return False

    def _login_to_dsm(self) -> bool:
        """Login to DSM"""
        if not self.page or not self.credentials:
            return False

        try:
            logger.info(f"🌐 Navigating to DSM: {self.dsm_url}")
            self.page.goto(self.dsm_url, wait_until="networkidle", timeout=30000)
            time.sleep(2)

            # Wait for login form
            logger.info("🔐 Waiting for login form...")
            self.page.wait_for_selector("input[name='username'], input[type='text']", timeout=10000)

            # Fill username
            username_input = self.page.query_selector("input[name='username'], input[type='text']")
            if username_input:
                username_input.fill(self.credentials["username"])
                logger.info(f"   ✓ Username entered: {self.credentials['username']}")

            # Fill password
            password_input = self.page.query_selector("input[name='password'], input[type='password']")
            if password_input:
                password_input.fill(self.credentials["password"])
                logger.info("   ✓ Password entered")

            # Click login button
            login_button = self.page.query_selector("button[type='submit'], button:has-text('Sign In'), button:has-text('Login')")
            if not login_button:
                # Try pressing Enter
                password_input.press("Enter")
            else:
                login_button.click()

            logger.info("   ✓ Login button clicked")

            # Wait for dashboard or main page
            logger.info("⏳ Waiting for login to complete...")
            time.sleep(5)

            # Check if we're logged in (look for DSM main interface)
            if "login" not in self.page.url.lower():
                logger.info("✅ Successfully logged in to DSM")
                return True
            else:
                logger.warning("⚠️  May still be on login page")
                return False

        except Exception as e:
            logger.error(f"❌ Error during login: {e}")
            # Take screenshot for debugging
            screenshot_path = self.project_root / "data" / "screenshots" / f"dsm_login_error_{int(time.time())}.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(screenshot_path))
            logger.info(f"   Screenshot saved: {screenshot_path}")
            return False

    def navigate_to_task_scheduler(self) -> bool:
        """Navigate to Task Scheduler in DSM"""
        if not self.page:
            return False

        try:
            logger.info("📋 Navigating to Task Scheduler...")

            # Method 1: Try direct URL
            task_scheduler_url = f"{self.dsm_url}/#taskScheduler"
            self.page.goto(task_scheduler_url, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # Method 2: Try clicking Control Panel > Task Scheduler
            # Look for Control Panel menu
            control_panel = self.page.query_selector("a:has-text('Control Panel'), [aria-label*='Control Panel']")
            if control_panel:
                control_panel.click()
                time.sleep(2)

                # Look for Task Scheduler
                task_scheduler = self.page.query_selector("a:has-text('Task Scheduler'), [aria-label*='Task Scheduler']")
                if task_scheduler:
                    task_scheduler.click()
                    time.sleep(3)

            # Check if we're on Task Scheduler page
            if "task" in self.page.url.lower() or "scheduler" in self.page.url.lower():
                logger.info("✅ Navigated to Task Scheduler")
                return True
            else:
                logger.warning("⚠️  May not be on Task Scheduler page")
                # Take screenshot
                screenshot_path = self.project_root / "data" / "screenshots" / f"task_scheduler_{int(time.time())}.png"
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                self.page.screenshot(path=str(screenshot_path))
                logger.info(f"   Screenshot saved: {screenshot_path}")
                return True  # Continue anyway

        except Exception as e:
            logger.error(f"❌ Error navigating to Task Scheduler: {e}")
            return False

    def create_scheduled_task(self, task_name: str, command: str, schedule: str = "daily") -> bool:
        """Create a scheduled task in DSM Task Scheduler"""
        if not self.page:
            return False

        try:
            logger.info(f"➕ Creating task: {task_name}")

            # Look for "Create" or "Add" button
            create_button = self.page.query_selector(
                "button:has-text('Create'), button:has-text('Add'), button:has-text('New'), "
                "[aria-label*='Create'], [aria-label*='Add']"
            )

            if create_button:
                create_button.click()
                time.sleep(2)
                logger.info("   ✓ Clicked Create button")
            else:
                logger.warning("   ⚠️  Create button not found, trying alternative methods")

            # Fill in task name
            name_input = self.page.query_selector("input[name='name'], input[placeholder*='name'], input[type='text']")
            if name_input:
                name_input.fill(task_name)
                logger.info(f"   ✓ Task name entered: {task_name}")

            # Select task type (Scheduled Task)
            task_type = self.page.query_selector("select[name='type'], select:has(option[value*='scheduled'])")
            if task_type:
                task_type.select_option("scheduled")
                logger.info("   ✓ Task type selected")

            # Fill in command
            command_input = self.page.query_selector(
                "textarea[name='command'], textarea[placeholder*='command'], "
                "input[name='command'], textarea"
            )
            if command_input:
                command_input.fill(command)
                logger.info(f"   ✓ Command entered: {command[:50]}...")

            # Set schedule
            schedule_select = self.page.query_selector("select[name='schedule'], select:has(option[value*='daily'])")
            if schedule_select:
                schedule_select.select_option(schedule)
                logger.info(f"   ✓ Schedule set: {schedule}")

            # Save task
            save_button = self.page.query_selector(
                "button:has-text('Save'), button:has-text('OK'), button:has-text('Apply'), "
                "button[type='submit']"
            )
            if save_button:
                save_button.click()
                time.sleep(2)
                logger.info("   ✓ Task saved")
                return True
            else:
                logger.warning("   ⚠️  Save button not found")
                return False

        except Exception as e:
            logger.error(f"❌ Error creating task: {e}")
            screenshot_path = self.project_root / "data" / "screenshots" / f"create_task_error_{int(time.time())}.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(screenshot_path))
            return False

    def install_cron_tasks_from_file(self, cron_file_path: str) -> Dict[str, Any]:
        """Install cron tasks from the deployed cron file"""
        results = {
            "success": False,
            "tasks_created": [],
            "tasks_failed": [],
            "errors": []
        }

        try:
            # Read cron file
            cron_file = Path(cron_file_path)
            if not cron_file.exists():
                # Try to find it on NAS
                cron_file = self.project_root / "scripts" / "nas" / "cron" / "cursor_tasks_crontab.txt"

            if not cron_file.exists():
                logger.error(f"❌ Cron file not found: {cron_file}")
                results["errors"].append(f"Cron file not found: {cron_file}")
                return results

            logger.info(f"📄 Reading cron file: {cron_file}")
            cron_lines = cron_file.read_text().splitlines()

            # Parse cron entries
            tasks = []
            for line in cron_lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Parse cron line: minute hour day month weekday command
                    parts = line.split()
                    if len(parts) >= 6:
                        schedule = " ".join(parts[:5])
                        command = " ".join(parts[5:])
                        task_name = f"CursorTask_{len(tasks) + 1}"
                        tasks.append({
                            "name": task_name,
                            "schedule": schedule,
                            "command": command
                        })

            logger.info(f"📋 Found {len(tasks)} tasks to create")

            # Setup browser and login
            if not self._setup_browser(headless=False):
                results["errors"].append("Failed to setup browser")
                return results

            if not self._get_credentials():
                results["errors"].append("Failed to get credentials")
                return results

            if not self._login_to_dsm():
                results["errors"].append("Failed to login to DSM")
                return results

            if not self.navigate_to_task_scheduler():
                results["errors"].append("Failed to navigate to Task Scheduler")
                return results

            # Create each task
            for task in tasks:
                logger.info(f"\n📝 Creating task: {task['name']}")
                success = self.create_scheduled_task(
                    task_name=task["name"],
                    command=task["command"],
                    schedule="custom"  # DSM may need custom schedule format
                )

                if success:
                    results["tasks_created"].append(task["name"])
                    logger.info(f"   ✅ Task created: {task['name']}")
                else:
                    results["tasks_failed"].append(task["name"])
                    logger.warning(f"   ❌ Failed to create: {task['name']}")

                time.sleep(2)  # Wait between tasks

            results["success"] = len(results["tasks_created"]) > 0
            logger.info(f"\n✅ Completed: {len(results['tasks_created'])}/{len(tasks)} tasks created")

        except Exception as e:
            logger.error(f"❌ Error installing cron tasks: {e}")
            results["errors"].append(str(e))
        finally:
            if self.browser:
                time.sleep(5)  # Keep browser open for a moment to see results
                # self.browser.close()  # Commented out so user can see results

        return results

    def close(self):
        """Close browser"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("🔒 Browser closed")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Automate DSM Task Scheduler via RDP/MANUS")
        parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
        parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
        parser.add_argument("--cron-file", help="Path to cron file (auto-detected if not provided)")
        parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

        args = parser.parse_args()

        automation = DSMTaskSchedulerAutomation(nas_ip=args.nas_ip, nas_port=args.nas_port)

        # Auto-detect cron file
        cron_file = args.cron_file
        if not cron_file:
            # Try to find the deployed cron file path
            cron_file = f"/var/services/homes/backupadm/.crontab_cursor_tasks_20260101_225836"
            # Or use local converted file
            local_cron = project_root / "scripts" / "nas" / "cron" / "cursor_tasks_crontab.txt"
            if local_cron.exists():
                cron_file = str(local_cron)

        result = automation.install_cron_tasks_from_file(cron_file)

        if result["success"]:
            print(f"\n✅ Successfully created {len(result['tasks_created'])} tasks")
            if result["tasks_failed"]:
                print(f"⚠️  Failed to create {len(result['tasks_failed'])} tasks")
        else:
            print(f"\n❌ Failed to install tasks")
            for error in result["errors"]:
                print(f"   Error: {error}")
            return 1

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())