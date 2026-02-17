#!/usr/bin/env python3
"""
MANUS User Control Interface

Complete user control over MANUS operations:
- Start/Stop/Status control
- Task execution and monitoring
- Configuration management
- Resource provisioning
- System operations
- Real-time status and logs

This gives YOU full control over MANUS.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MANUS-User-Control")


class MANUSStatus(Enum):
    """MANUS system status"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"


class MANUSTaskType(Enum):
    """MANUS task types"""
    PROVISION = "provision"
    CONFIGURE = "configure"
    EXECUTE = "execute"
    MONITOR = "monitor"
    CLEANUP = "cleanup"
    STATUS = "status"


class MANUSUserControl:
    """
    User Control Interface for MANUS

    Provides complete control over MANUS operations from user perspective.
    """

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize MANUS User Control Interface

        Args:
            config_file: Optional path to configuration file. 
                        Defaults to config/manus_user_control.json
        """
        self.config_file = config_file or Path("config/manus_user_control.json")
        self.config = self._load_config()
        self.status = MANUSStatus.UNKNOWN
        self.active_tasks: Dict[str, Any] = {}
        self.logs: List[Dict[str, Any]] = []

        logger.info("✅ MANUS User Control Interface initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load MANUS configuration"""
        default_config = {
            "azure_key_vault": "jarvis-lumina",
            "azure_resource_group": "jarvis-lumina-rg",
            "azure_location": "eastus",
            "workspace_path": str(Path.cwd()),
            "log_level": "INFO",
            "auto_start": False,
            "task_timeout": 300,
            "max_concurrent_tasks": 5
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")

        return default_config

    def save_config(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
            raise

    # =================================================================
    # STATUS CONTROL
    # =================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get MANUS system status"""
        return {
            "status": self.status.value,
            "active_tasks": len(self.active_tasks),
            "config": {
                "key_vault": self.config["azure_key_vault"],
                "resource_group": self.config["azure_resource_group"],
                "location": self.config["azure_location"]
            },
            "timestamp": datetime.now().isoformat()
        }

    def check_status(self) -> MANUSStatus:
        """Check MANUS operational status"""
        try:
            # Check if key MANUS scripts are accessible
            manus_scripts = [
                "scripts/python/manus_provision_azure_speech.py",
                "scripts/python/manus_neo_browser_control.py",
            ]

            all_exist = all(Path(script).exists() for script in manus_scripts)

            if all_exist:
                self.status = MANUSStatus.RUNNING
            else:
                self.status = MANUSStatus.ERROR

            return self.status
        except Exception as e:
            logger.error(f"❌ Error checking status: {e}")
            self.status = MANUSStatus.ERROR
            return self.status

    # =================================================================
    # TASK EXECUTION
    # =================================================================

    def execute_task(self, task_type: MANUSTaskType, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a MANUS task

        Args:
            task_type: Type of task to execute
            task_data: Task-specific data

        Returns:
            Task execution result
        """
        task_id = f"{task_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"🚀 Executing task: {task_id} ({task_type.value})")

        self.active_tasks[task_id] = {
            "id": task_id,
            "type": task_type.value,
            "data": task_data,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "result": None
        }

        try:
            if task_type == MANUSTaskType.PROVISION:
                result = self._provision_task(task_data)
            elif task_type == MANUSTaskType.CONFIGURE:
                result = self._configure_task(task_data)
            elif task_type == MANUSTaskType.EXECUTE:
                result = self._execute_task(task_data)
            elif task_type == MANUSTaskType.MONITOR:
                result = self._monitor_task(task_data)
            elif task_type == MANUSTaskType.STATUS:
                result = self._status_task(task_data)
            else:
                result = {"success": False, "error": f"Unknown task type: {task_type}"}

            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["result"] = result
            self.active_tasks[task_id]["end_time"] = datetime.now().isoformat()

            self._log("INFO", f"Task {task_id} completed", result)

            return {
                "success": True,
                "task_id": task_id,
                "result": result
            }

        except Exception as e:
            self.active_tasks[task_id]["status"] = "failed"
            self.active_tasks[task_id]["error"] = str(e)
            self.active_tasks[task_id]["end_time"] = datetime.now().isoformat()

            self._log("ERROR", f"Task {task_id} failed", {"error": str(e)})

            return {
                "success": False,
                "task_id": task_id,
                "error": str(e)
            }

    def _provision_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute provisioning task"""
        resource_type = data.get("resource_type")

        if resource_type == "azure_speech":
            return self._provision_azure_speech()
        elif resource_type == "azure_key_vault_secret":
            return self._provision_key_vault_secret(
                data.get("secret_name"),
                data.get("secret_value")
            )
        else:
            return {"success": False, "error": f"Unknown resource type: {resource_type}"}

    def _provision_azure_speech(self) -> Dict[str, Any]:
        """Provision Azure Speech service"""
        try:
            result = subprocess.run(
                ["python", "scripts/python/manus_provision_azure_speech.py"],
                capture_output=True,
                text=True,
                timeout=self.config["task_timeout"]
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _provision_key_vault_secret(self, name: str, value: str) -> Dict[str, Any]:
        """Store secret in Azure Key Vault"""
        try:
            result = subprocess.run([
                "az", "keyvault", "secret", "set",
                "--vault-name", self.config["azure_key_vault"],
                "--name", name,
                "--value", value
            ], capture_output=True, text=True, timeout=30)

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _configure_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute configuration task"""
        config_updates = data.get("config", {})

        # Update configuration
        self.config.update(config_updates)
        self.save_config()

        return {
            "success": True,
            "message": "Configuration updated",
            "updated_keys": list(config_updates.keys())
        }

    def _execute_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a script or command"""
        script = data.get("script")
        command = data.get("command")
        args = data.get("args", [])

        if script:
            # Execute Python script
            cmd = ["python", script] + args
        elif command:
            # Execute shell command
            cmd = command.split() + args
        else:
            return {"success": False, "error": "No script or command specified"}

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config["task_timeout"],
                cwd=self.config["workspace_path"]
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _monitor_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring task"""
        monitor_type = data.get("monitor_type", "status")

        if monitor_type == "status":
            return self.get_status()
        elif monitor_type == "tasks":
            return {
                "active_tasks": len(self.active_tasks),
                "tasks": list(self.active_tasks.values())
            }
        elif monitor_type == "logs":
            limit = data.get("limit", 100)
            return {
                "logs": self.logs[-limit:],
                "total": len(self.logs)
            }
        else:
            return {"success": False, "error": f"Unknown monitor type: {monitor_type}"}

    def _status_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get status information"""
        return self.get_status()

    # =================================================================
    # NEO BROWSER CONTROL
    # =================================================================

    def control_neo_browser(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Control NEO browser through MANUS

        Args:
            action: Action to perform (launch, close, navigate, cookies, etc.)
            params: Action parameters

        Returns:
            Dict with success status and result data
        """
        params = params or {}

        try:
            try:
                from manus_neo_integration import MANUSNEOIntegration
            except ImportError as e:
                logger.warning(f"MANUS-NEO integration not available: {e}")
                return {
                    "success": False,
                    "error": "MANUS-NEO integration not available",
                    "message": "Install required dependencies or ensure manus_neo_integration.py exists"
                }

            # Initialize integration with error handling
            try:
                integration = MANUSNEOIntegration()
            except Exception as e:
                logger.error(f"Failed to initialize MANUSNEOIntegration: {e}")
                return {
                    "success": False,
                    "error": f"Failed to initialize browser integration: {e}"
                }

            if action == "launch":
                try:
                    url = params.get("url", "https://elevenlabs.io")
                    success = integration.open_website(url)
                    return {"success": success, "action": "launch", "url": url}
                except Exception as e:
                    logger.error(f"Failed to launch browser: {e}")
                    return {"success": False, "error": f"Failed to launch browser: {e}"}

            elif action == "cookies":
                try:
                    domain = params.get("domain", "elevenlabs.io")
                    cookies = integration.get_cookies_for_domain(domain)
                    return {"success": True, "cookies": cookies, "count": len(cookies)}
                except Exception as e:
                    logger.error(f"Failed to get cookies: {e}")
                    return {"success": False, "error": f"Failed to get cookies: {e}"}

            elif action == "elevenlabs_setup":
                try:
                    result = integration.automate_elevenlabs_setup()
                    return result
                except Exception as e:
                    logger.error(f"Failed to setup ElevenLabs: {e}")
                    return {"success": False, "error": f"Failed to setup ElevenLabs: {e}"}

            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except ImportError:
            return {"success": False, "error": "MANUS-NEO integration not available"}
        except Exception as e:
            logger.error(f"Unexpected error in control_neo_browser: {e}")
            return {"success": False, "error": str(e)}

    # =================================================================
    # LOGGING & MONITORING
    # =================================================================

    def _log(self, level: str, message: str, data: Any = None):
        """Add log entry"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data
        }
        self.logs.append(log_entry)

        # Keep only last 1000 logs
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]

        # Also log to logger
        if level == "ERROR":
            logger.error(f"{message}: {data}")
        elif level == "WARNING":
            logger.warning(f"{message}: {data}")
        else:
            logger.info(f"{message}")

    def get_logs(self, level: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs"""
        logs = self.logs[-limit:] if limit else self.logs

        if level:
            logs = [log for log in logs if log["level"] == level.upper()]

        return logs

    # =================================================================
    # TASK MANAGEMENT
    # =================================================================

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks"""
        try:
            return list(self.active_tasks.values())
        except Exception as e:
            logger.error(f"❌ Error listing tasks: {e}")
            return []

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get specific task"""
        try:
            return self.active_tasks.get(task_id)
        except Exception as e:
            logger.error(f"❌ Error getting task: {e}")
            return None

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                if task["status"] == "running":
                    task["status"] = "cancelled"
                    task["end_time"] = datetime.now().isoformat()
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Error cancelling task: {e}")
            return False

    # =================================================================
    # CONFIGURATION MANAGEMENT
    # =================================================================

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration"""
        try:
            self.config.update(updates)
            self.save_config()

            return {
                "success": True,
                "message": "Configuration updated",
                "updated_keys": list(updates.keys()),
                "config": self.config
            }
        except Exception as e:
            logger.error(f"❌ Error updating config: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update configuration"
            }

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()

    def reset_config(self) -> Dict[str, Any]:
        """Reset configuration to defaults"""
        try:
            self.config_file.unlink(missing_ok=True)
            self.config = self._load_config()
            return {"success": True, "message": "Configuration reset to defaults"}
        except Exception as e:
            logger.error(f"❌ Error resetting config: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to reset configuration"
            }


def main():
    """CLI Interface for MANUS User Control"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS User Control Interface")

    # Status commands
    parser.add_argument("--status", action="store_true", help="Get MANUS status")
    parser.add_argument("--check", action="store_true", help="Check MANUS status")

    # Task commands
    parser.add_argument("--provision", type=str, help="Provision resource (azure_speech, etc.)")
    parser.add_argument("--execute", type=str, help="Execute script or command")
    parser.add_argument("--configure", type=str, help="Update configuration (JSON)")

    # NEO browser commands
    parser.add_argument("--neo-launch", type=str, help="Launch NEO browser with URL")
    parser.add_argument("--neo-cookies", type=str, help="Get cookies for domain")
    parser.add_argument("--neo-elevenlabs", action="store_true", help="Automate ElevenLabs setup")

    # Monitoring commands
    parser.add_argument("--logs", type=int, help="Get logs (limit)")
    parser.add_argument("--tasks", action="store_true", help="List tasks")

    # Config commands
    parser.add_argument("--config-get", action="store_true", help="Get configuration")
    parser.add_argument("--config-set", type=str, help="Set configuration (JSON)")
    parser.add_argument("--config-reset", action="store_true", help="Reset configuration")

    args = parser.parse_args()

    control = MANUSUserControl()

    try:
        if args.status or args.check:
            status = control.get_status()
            print("\n" + "="*70)
            print("MANUS Status")
            print("="*70)
            print(json.dumps(status, indent=2))

        elif args.provision:
            if args.provision == "azure_speech":
                result = control.execute_task(MANUSTaskType.PROVISION, {"resource_type": "azure_speech"})
                print("\n" + "="*70)
                print("Provisioning Result")
                print("="*70)
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Unknown resource type: {args.provision}")

        elif args.execute:
            result = control.execute_task(MANUSTaskType.EXECUTE, {"command": args.execute})
            print(json.dumps(result, indent=2))

        elif args.configure:
            try:
                updates = json.loads(args.configure)
                result = control.update_config(updates)
                print(json.dumps(result, indent=2))
            except json.JSONDecodeError:
                print("❌ Invalid JSON configuration")

        elif args.neo_launch:
            result = control.control_neo_browser("launch", {"url": args.neo_launch})
            print(json.dumps(result, indent=2))

        elif args.neo_cookies:
            result = control.control_neo_browser("cookies", {"domain": args.neo_cookies})
            print(json.dumps(result, indent=2))

        elif args.neo_elevenlabs:
            result = control.control_neo_browser("elevenlabs_setup")
            print("\n" + "="*70)
            print("ElevenLabs Setup Result")
            print("="*70)
            print(json.dumps(result, indent=2))

        elif args.logs:
            logs = control.get_logs(limit=args.logs)
            print("\n" + "="*70)
            print(f"Recent Logs (last {args.logs})")
            print("="*70)
            for log in logs:
                print(f"[{log['timestamp']}] {log['level']}: {log['message']}")

        elif args.tasks:
            tasks = control.list_tasks()
            print("\n" + "="*70)
            print("Active Tasks")
            print("="*70)
            print(json.dumps(tasks, indent=2))

        elif args.config_get:
            config = control.get_config()
            print(json.dumps(config, indent=2))

        elif args.config_set:
            try:
                updates = json.loads(args.config_set)
                result = control.update_config(updates)
                print(json.dumps(result, indent=2))
            except json.JSONDecodeError:
                print("❌ Invalid JSON configuration")

        elif args.config_reset:
            result = control.reset_config()
            print(json.dumps(result, indent=2))

        else:
            parser.print_help()
            print("\n" + "="*70)
            print("Quick Examples:")
            print("="*70)
            print("  # Get status")
            print("  python manus_user_control_interface.py --status")
            print()
            print("  # Provision Azure Speech")
            print("  python manus_user_control_interface.py --provision azure_speech")
            print()
            print("  # Launch NEO browser")
            print("  python manus_user_control_interface.py --neo-launch https://elevenlabs.io")
            print()
            print("  # Get cookies")
            print("  python manus_user_control_interface.py --neo-cookies elevenlabs.io")
            print()
            print("  # Configure MANUS")
            print('  python manus_user_control_interface.py --configure \'{"log_level": "DEBUG"}\'')

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":



    main()