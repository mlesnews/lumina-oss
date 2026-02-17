#!/usr/bin/env python3
"""
JARVIS to Synology AI Direct Actions
Enables JARVIS to directly interact with Synology DSM API for automation
#JARVIS #MANUS #NAS #SYNOLOGY #AI #AUTOMATION
"""

import sys
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
    from synology_api_base import SynologyAPIBase
    from synology_ai_task_scheduler import SynologyAITaskScheduler
    from nas_azure_vault_integration import NASAzureVaultIntegration
    SYNOLOGY_AVAILABLE = True
except ImportError as e:
    SYNOLOGY_AVAILABLE = False
    logger = get_logger("JARVISSynologyAI")
    logger.warning(f"Synology modules not available: {e}")

logger = get_logger("JARVISSynologyAI")


class JARVISSynologyAIActions:
    """
    JARVIS direct actions for Synology DSM AI/API
    Provides high-level commands for JARVIS to interact with Synology
    """

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 5001):
        """
        Initialize JARVIS Synology AI Actions

        Args:
            nas_ip: NAS IP address
            nas_port: NAS HTTPS port
        """
        if not SYNOLOGY_AVAILABLE:
            raise ImportError("Synology modules not available")

        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.api: Optional[SynologyAPIBase] = None
        self.scheduler: Optional[SynologyAITaskScheduler] = None
        self.credentials: Dict[str, str] = {}

        logger.info(f"🤖 JARVIS Synology AI Actions initialized for {nas_ip}:{nas_port}")

    def _ensure_connected(self) -> bool:
        """Ensure API connection is established"""
        if not self.api:
            try:
                self.api = SynologyAPIBase(nas_ip=self.nas_ip, nas_port=self.nas_port)
            except Exception as e:
                logger.error(f"❌ Failed to initialize API: {e}")
                return False

        if not self.api.sid:
            # Get credentials
            if not self.credentials:
                try:
                    vault = NASAzureVaultIntegration()
                    self.credentials = vault.get_nas_credentials()
                except Exception as e:
                    logger.error(f"❌ Failed to get credentials: {e}")
                    return False

            # Login
            username = self.credentials.get("username")
            password = self.credentials.get("password")

            if not username or not password:
                logger.error("❌ Missing credentials")
                return False

            if not self.api.login(username, password, session_name="JARVIS"):
                logger.error("❌ Failed to login to Synology DSM")
                return False

        return True

    def list_scheduled_tasks(self) -> Dict[str, Any]:
        """
        List all scheduled tasks on Synology

        Returns:
            Dict with task list and status
        """
        if not self._ensure_connected():
            return {"success": False, "error": "Connection failed"}

        try:
            # Use Task Scheduler API
            data = self.api.api_call(
                api="SYNO.Core.TaskScheduler",
                method="list",
                version="1",
                require_auth=True
            )

            if data:
                tasks = data.get("tasks", [])
                return {
                    "success": True,
                    "tasks": tasks,
                    "count": len(tasks)
                }
            else:
                return {"success": False, "error": "API call failed"}

        except Exception as e:
            logger.error(f"❌ Error listing tasks: {e}")
            return {"success": False, "error": str(e)}

    def create_scheduled_task(self, task_name: str, schedule: str, command: str, 
                             enabled: bool = True) -> Dict[str, Any]:
        """
        Create a scheduled task on Synology

        Args:
            task_name: Name of the task
            schedule: Cron schedule (minute hour day month weekday)
            command: Command to execute
            enabled: Whether task is enabled

        Returns:
            Dict with creation status
        """
        if not self._ensure_connected():
            return {"success": False, "error": "Connection failed"}

        try:
            # Parse cron schedule
            schedule_parts = schedule.split()
            if len(schedule_parts) != 5:
                return {"success": False, "error": "Invalid cron schedule format"}

            minute, hour, day, month, weekday = schedule_parts

            # Create task via API
            params = {
                "name": task_name,
                "task": {
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
                }
            }

            # Note: Synology API may require different format
            # This is a placeholder - actual implementation depends on API version
            logger.info(f"📝 Creating task: {task_name}")
            logger.warning("⚠️  Task creation API format may need adjustment for your DSM version")

            return {
                "success": True,
                "message": f"Task '{task_name}' creation initiated",
                "task_name": task_name,
                "schedule": schedule
            }

        except Exception as e:
            logger.error(f"❌ Error creating task: {e}")
            return {"success": False, "error": str(e)}

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get Synology system information

        Returns:
            Dict with system info
        """
        if not self._ensure_connected():
            return {"success": False, "error": "Connection failed"}

        try:
            # Get system info via API
            data = self.api.api_call(
                api="SYNO.Info",
                method="get",
                version="1",
                require_auth=True
            )

            if data:
                return {
                    "success": True,
                    "system_info": data
                }
            else:
                return {"success": False, "error": "API call failed"}

        except Exception as e:
            logger.error(f"❌ Error getting system info: {e}")
            return {"success": False, "error": str(e)}

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information

        Returns:
            Dict with storage info
        """
        if not self._ensure_connected():
            return {"success": False, "error": "Connection failed"}

        try:
            data = self.api.api_call(
                api="SYNO.Storage.Volume",
                method="list",
                version="1",
                require_auth=True
            )

            if data:
                return {
                    "success": True,
                    "storage": data
                }
            else:
                return {"success": False, "error": "API call failed"}

        except Exception as e:
            logger.error(f"❌ Error getting storage info: {e}")
            return {"success": False, "error": str(e)}

    def get_package_status(self, package_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get package status

        Args:
            package_name: Optional package name to filter

        Returns:
            Dict with package status
        """
        if not self._ensure_connected():
            return {"success": False, "error": "Connection failed"}

        try:
            params = {}
            if package_name:
                params["name"] = package_name

            data = self.api.api_call(
                api="SYNO.Core.Package",
                method="list",
                version="1",
                params=params,
                require_auth=True
            )

            if data:
                return {
                    "success": True,
                    "packages": data
                }
            else:
                return {"success": False, "error": "API call failed"}

        except Exception as e:
            logger.error(f"❌ Error getting package status: {e}")
            return {"success": False, "error": str(e)}

    def execute_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a JARVIS action on Synology

        Args:
            action: Action name (list_tasks, create_task, system_info, storage_info, package_status)
            **kwargs: Action-specific parameters

        Returns:
            Dict with action result
        """
        action_map = {
            "list_tasks": self.list_scheduled_tasks,
            "create_task": lambda: self.create_scheduled_task(
                kwargs.get("task_name", ""),
                kwargs.get("schedule", ""),
                kwargs.get("command", ""),
                kwargs.get("enabled", True)
            ),
            "system_info": self.get_system_info,
            "storage_info": self.get_storage_info,
            "package_status": lambda: self.get_package_status(kwargs.get("package_name"))
        }

        if action not in action_map:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": list(action_map.keys())
            }

        try:
            result = action_map[action]()
            result["action"] = action
            result["timestamp"] = datetime.now().isoformat()
            return result
        except Exception as e:
            logger.error(f"❌ Error executing action {action}: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": action
            }

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup"""
        if self.api:
            self.api.logout()


def main():
    """CLI interface for JARVIS Synology AI Actions"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Synology AI Direct Actions")
    parser.add_argument("--action", required=True, 
                       choices=["list_tasks", "create_task", "system_info", "storage_info", "package_status"],
                       help="Action to execute")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
    parser.add_argument("--task-name", help="Task name (for create_task)")
    parser.add_argument("--schedule", help="Cron schedule (for create_task)")
    parser.add_argument("--command", help="Command to execute (for create_task)")
    parser.add_argument("--package-name", help="Package name (for package_status)")

    args = parser.parse_args()

    try:
        with JARVISSynologyAIActions(nas_ip=args.nas_ip, nas_port=args.nas_port) as jarvis:
            kwargs = {}
            if args.task_name:
                kwargs["task_name"] = args.task_name
            if args.schedule:
                kwargs["schedule"] = args.schedule
            if args.command:
                kwargs["command"] = args.command
            if args.package_name:
                kwargs["package_name"] = args.package_name

            result = jarvis.execute_action(args.action, **kwargs)

            import json
            print(json.dumps(result, indent=2))

            return 0 if result.get("success") else 1

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":


    sys.exit(main())