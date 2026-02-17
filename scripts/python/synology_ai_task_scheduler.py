#!/usr/bin/env python3
"""
Synology AI Task Scheduler
Interacts with Synology DSM AI/API to schedule tasks automatically
Uses Synology DSM API instead of direct crontab access
#JARVIS #MANUS #NAS #SYNOLOGY #AI #API #AUTOMATION
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    AZURE_VAULT_AVAILABLE = True
except ImportError:
    AZURE_VAULT_AVAILABLE = False

logger = get_logger("SynologyAITaskScheduler")


class SynologyAITaskScheduler:
    """
    Interact with Synology DSM API/AI to schedule tasks
    Uses Synology DSM Task Scheduler API instead of crontab
    """

    def __init__(self, project_root: Path, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 5001):
        self.project_root = project_root
        self.nas_ip = nas_ip
        self.nas_port = nas_port

        # Use base class for SSL handling
        try:
            from synology_api_base import SynologyAPIBase
            self.api = SynologyAPIBase(nas_ip=nas_ip, nas_port=nas_port, verify_ssl=True)
            self.session = self.api.session
            self.base_url = self.api.base_url
            self.sid = None  # Will be set by login
            logger.info("✅ Using SynologyAPIBase for SSL certificate handling")
        except ImportError as e:
            # Fallback if base class not available
            logger.warning(f"SynologyAPIBase not available ({e}), using direct session")
            self.api = None
            self.base_url = f"https://{nas_ip}:{nas_port}"
            self.session = requests.Session()
            self._setup_ssl_verification()
            self.sid = None

        # Load credentials
        self.credentials = self._get_credentials()

        logger.info(f"🤖 Synology AI Task Scheduler initialized for {nas_ip}")

    def _setup_ssl_verification(self) -> None:
        """Setup SSL verification (fallback method)"""
        try:
            from nas_certificate_manager import NASCertificateManager
            cert_manager = NASCertificateManager()
            self.session.verify = cert_manager.get_requests_verify_setting(
                self.nas_ip, self.nas_port, auto_download=True, auto_generate=True
            )
        except:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings()

    def _get_credentials(self) -> Dict[str, str]:
        """Get NAS credentials from Azure Key Vault"""
        if not AZURE_VAULT_AVAILABLE:
            logger.warning("Azure Key Vault not available")
            return {}

        try:
            vault = NASAzureVaultIntegration()
            credentials = vault.get_nas_credentials()
            return credentials
        except Exception as e:
            logger.error(f"Error getting credentials: {e}")
            return {}

    def login(self) -> bool:
        """
        Login to Synology DSM API
        Returns session ID (SID) for API calls
        """
        if not self.credentials:
            logger.error("No credentials available")
            return False

        username = self.credentials.get("username")
        password = self.credentials.get("password")

        if not username or not password:
            logger.error("Missing username or password")
            return False

        # Synology DSM API login endpoint
        login_url = f"{self.base_url}/webapi/auth.cgi"

        params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": username,
            "passwd": password,
            "session": "TaskScheduler",
            "format": "sid"
        }

        try:
            # Use the session's verify setting (set during init)
            response = self.session.get(login_url, params=params, timeout=10, verify=self.session.verify)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                self.sid = data.get("data", {}).get("sid")
                logger.info("✅ Logged in to Synology DSM API")
                return True
            else:
                error = data.get("error", {})
                logger.error(f"❌ Login failed: {error.get('code')} - {error.get('errors')}")
                return False

        except Exception as e:
            logger.error(f"❌ Error logging in: {e}")
            return False

    def create_scheduled_task(self, task_name: str, schedule: str, command: str, 
                             enabled: bool = True) -> bool:
        """
        Create a scheduled task via Synology DSM API

        Args:
            task_name: Name of the task
            schedule: Cron schedule (minute hour day month weekday)
            command: Command to execute
            enabled: Whether task is enabled

        Returns:
            True if task created successfully
        """
        if not self.sid:
            if not self.login():
                return False

        # Parse cron schedule
        schedule_parts = schedule.split()
        if len(schedule_parts) != 5:
            logger.error(f"Invalid cron schedule: {schedule}")
            return False

        minute, hour, day, month, weekday = schedule_parts

        # Synology Task Scheduler API endpoint
        task_url = f"{self.base_url}/webapi/entry.cgi"

        # Convert cron to Synology schedule format
        # Synology uses different format - need to convert
        params = {
            "api": "SYNO.Core.TaskScheduler",
            "version": "1",
            "method": "create",
            "sid": self.sid,
            "name": task_name,
            "task": json.dumps({
                "enabled": enabled,
                "task": {
                    "type": "user_defined_script",
                    "user_defined_script": {
                        "script": command
                    }
                },
                "schedule": {
                    "type": "cron",
                    "minute": minute,
                    "hour": hour,
                    "day": day,
                    "month": month,
                    "weekday": weekday
                }
            })
        }

        try:
            response = self.session.get(task_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                logger.info(f"✅ Created task: {task_name}")
                return True
            else:
                error = data.get("error", {})
                logger.error(f"❌ Failed to create task: {error.get('code')} - {error.get('errors')}")
                return False

        except Exception as e:
            logger.error(f"❌ Error creating task: {e}")
            return False

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all scheduled tasks"""
        if not self.sid:
            if not self.login():
                return []

        # Use base class API call if available
        if self.api:
            data = self.api.api_call(
                api="SYNO.Core.TaskScheduler",
                method="list",
                version="1",
                require_auth=True
            )
            if data:
                tasks = data.get("tasks", [])
                logger.info(f"✅ Found {len(tasks)} scheduled tasks")
                return tasks
            return []

        # Fallback to direct API call
        task_url = f"{self.base_url}/webapi/entry.cgi"

        params = {
            "api": "SYNO.Core.TaskScheduler",
            "version": "1",
            "method": "list",
            "_sid": self.sid
        }

        try:
            response = self.session.get(task_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                tasks = data.get("data", {}).get("tasks", [])
                logger.info(f"✅ Found {len(tasks)} scheduled tasks")
                return tasks
            else:
                logger.warning("Could not list tasks")
                return []

        except Exception as e:
            logger.error(f"❌ Error listing tasks: {e}")
            return []

    def deploy_cursor_tasks(self, cron_file: Path) -> Dict[str, Any]:
        try:
            """
            Deploy tasks from cursor tasks cron file via Synology API

            Args:
                cron_file: Path to crontab file with tasks

            Returns:
                Dict with deployment results
            """
            if not cron_file.exists():
                logger.error(f"Cron file not found: {cron_file}")
                return {"success": False, "error": "File not found"}

            # Login first
            if not self.login():
                return {"success": False, "error": "Login failed"}

            # Parse cron file
            tasks = []
            with open(cron_file) as f:
                current_task = None
                for line in f:
                    line = line.strip()
                    if line.startswith("#"):
                        # Task name/comment
                        current_task = line.replace("#", "").strip()
                    elif line and not line.startswith("#"):
                        # Cron entry
                        parts = line.split(None, 5)
                        if len(parts) >= 6:
                            schedule = " ".join(parts[:5])
                            command = parts[5]
                            tasks.append({
                                "name": current_task or f"Task_{len(tasks)+1}",
                                "schedule": schedule,
                                "command": command
                            })

            # Deploy each task
            results = {
                "success": True,
                "deployed": [],
                "failed": []
            }

            for task in tasks:
                success = self.create_scheduled_task(
                    task_name=task["name"],
                    schedule=task["schedule"],
                    command=task["command"]
                )

                if success:
                    results["deployed"].append(task["name"])
                else:
                    results["failed"].append(task["name"])
                    results["success"] = False

            return results


        except Exception as e:
            self.logger.error(f"Error in deploy_cursor_tasks: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Synology AI Task Scheduler")
        parser.add_argument("--deploy", type=str, help="Deploy cron file to Synology")
        parser.add_argument("--list", action="store_true", help="List scheduled tasks")
        parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
        parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
        args = parser.parse_args()

        scheduler = SynologyAITaskScheduler(project_root, nas_ip=args.nas_ip, nas_port=args.nas_port)

        if args.list:
            print("=" * 70)
            print("   SYNOLOGY SCHEDULED TASKS")
            print("=" * 70)
            print("")

            tasks = scheduler.list_tasks()
            if tasks:
                for task in tasks:
                    print(f"  • {task.get('name', 'Unknown')}")
                    print(f"    Enabled: {task.get('enabled', False)}")
                    print("")
            else:
                print("  No tasks found")
            print("")
            return 0

        if args.deploy:
            cron_file = Path(args.deploy)
            if not cron_file.is_absolute():
                cron_file = project_root / cron_file

            print("=" * 70)
            print("   DEPLOY TASKS TO SYNOLOGY DSM")
            print("=" * 70)
            print("")
            print(f"Deploying: {cron_file}")
            print("")

            results = scheduler.deploy_cursor_tasks(cron_file)

            if results["success"]:
                print("✅ Deployment successful!")
                print(f"   Deployed: {len(results['deployed'])} tasks")
                if results["failed"]:
                    print(f"   Failed: {len(results['failed'])} tasks")
            else:
                print("❌ Deployment failed")
                if results.get("error"):
                    print(f"   Error: {results['error']}")

            print("")
            return 0 if results["success"] else 1

        print("Usage:")
        print("  --deploy <file>  - Deploy cron file to Synology")
        print("  --list            - List scheduled tasks")
        print("")
        print("Example:")
        print("  python synology_ai_task_scheduler.py --deploy scripts/nas/cron/cursor_tasks_crontab.txt")
        print("")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())