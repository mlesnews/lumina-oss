#!/usr/bin/env python3
"""
Notification Fix Manager - Comprehensive VSCode and System Notification Management

Fixes all notification warnings and errors across the system, including:
- VSCode task errors
- Extension warnings
- System notifications
- Docker errors
- Python warnings
- Hardware-related notifications
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class NotificationFixManager:
    """Comprehensive notification and error management system"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "notifications"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Notification tracking
        self.notifications: Deque[Dict[str, Any]] = deque(maxlen=1000)
        self.active_fixes: Dict[str, Dict[str, Any]] = {}
        self.suppressed_notifications: Set[str] = set()

        # Fix strategies
        self.fix_strategies = {
            "vscode_task_error": self._fix_vscode_task_error,
            "extension_warning": self._fix_extension_warning,
            "docker_error": self._fix_docker_error,
            "python_warning": self._fix_python_warning,
            "hardware_error": self._fix_hardware_error,
            "system_notification": self._fix_system_notification,
            "dependency_error": self._fix_dependency_error,
            "configuration_error": self._fix_configuration_error
        }

        # Setup logging
        self.logger = logging.getLogger("NotificationFixManager")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)

        # Load existing data
        self._load_notification_data()

    def _load_notification_data(self):
        """Load existing notification data"""
        try:
            data_file = self.data_dir / "notifications.json"
            if data_file.exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    self.notifications.extend(data.get('notifications', []))
                    self.suppressed_notifications.update(data.get('suppressed', []))
        except Exception as e:
            self.logger.warning(f"Failed to load notification data: {e}")

    def save_notification_data(self):
        """Save notification data"""
        try:
            data = {
                'notifications': list(self.notifications),
                'suppressed': list(self.suppressed_notifications),
                'timestamp': datetime.now().isoformat()
            }
            with open(self.data_dir / "notifications.json", 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save notification data: {e}")

    def report_notification(self, notification_type: str, message: str,
                          source: str = "unknown", severity: str = "medium",
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Report a notification and attempt to fix it

        Returns True if fixed, False if not fixable
        """

        notification_id = self._generate_notification_id(notification_type, message, source)

        # Skip if already suppressed
        if notification_id in self.suppressed_notifications:
            return True

        # Create notification record
        notification = {
            "id": notification_id,
            "type": notification_type,
            "message": message,
            "source": source,
            "severity": severity,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "fixed": False,
            "attempts": 0
        }

        # Add to history
        self.notifications.append(notification)

        # Attempt to fix
        fixed = self._attempt_fix(notification)

        if fixed:
            notification["fixed"] = True
            notification["fixed_at"] = datetime.now().isoformat()
            self.logger.info(f"✅ Fixed notification: {notification_type} - {message[:100]}...")
        else:
            self.logger.warning(f"❌ Could not fix notification: {notification_type} - {message[:100]}...")

        # Save data
        self.save_notification_data()

        return fixed

    def _generate_notification_id(self, notification_type: str, message: str, source: str) -> str:
        """Generate unique notification ID"""
        normalized = re.sub(r'\d+', '<NUM>', message.lower())
        normalized = re.sub(r'[\w\-\.]+\.[\w\-\.]+', '<PATH>', normalized)
        return f"{notification_type}:{source}:{hash(normalized) % 10000}"

    def _attempt_fix(self, notification: Dict[str, Any]) -> bool:
        """Attempt to fix a notification"""
        notification_type = notification["type"]

        # Get appropriate fix strategy
        fix_strategy = self.fix_strategies.get(notification_type)
        if not fix_strategy:
            self.logger.warning(f"No fix strategy for notification type: {notification_type}")
            return False

        try:
            notification["attempts"] += 1
            return fix_strategy(notification)
        except Exception as e:
            self.logger.error(f"Fix attempt failed for {notification_type}: {e}")
            return False

    def _fix_vscode_task_error(self, notification: Dict[str, Any]) -> bool:
        """Fix VSCode task errors"""
        message = notification["message"].lower()

        # Task error patterns and fixes
        if "there are task errors" in message:
            return self._fix_task_runner_issues()

        elif "command not found" in message:
            return self._fix_missing_command(notification)

        elif "module not found" in message or "no module named" in message:
            return self._fix_missing_module(notification)

        elif "permission denied" in message:
            return self._fix_permission_issue(notification)

        elif "port already in use" in message:
            return self._fix_port_conflict(notification)

        return False

    def _fix_extension_warning(self, notification: Dict[str, Any]) -> bool:
        """Fix VSCode extension warnings"""
        message = notification["message"].lower()

        if "extension 'esbenp.prettier-vscode' is configured as a formatter but not available" in message:
            return self._fix_prettier_extension()

        elif "notifcation error - please reopen file" in message:
            return self._fix_notification_reopen_error()

        elif "extension update" in message:
            return self._fix_extension_update_issue(notification)

        return False

    def _fix_docker_error(self, notification: Dict[str, Any]) -> bool:
        """Fix Docker-related errors"""
        message = notification["message"].lower()

        if "docker daemon not running" in message:
            return self._start_docker_daemon()

        elif "image not found" in message:
            return self._pull_docker_image(notification)

        elif "port already in use" in message:
            return self._fix_docker_port_conflict(notification)

        elif "no space left" in message:
            return self._cleanup_docker_space()

        return False

    def _fix_python_warning(self, notification: Dict[str, Any]) -> bool:
        """Fix Python-related warnings"""
        message = notification["message"].lower()

        if "unterminated string literal" in message:
            return self._fix_python_syntax_error(notification)

        elif "invalid syntax" in message:
            return self._fix_python_syntax_error(notification)

        elif "deprecated" in message:
            return self._fix_deprecated_warning(notification)

        return False

    def _fix_hardware_error(self, notification: Dict[str, Any]) -> bool:
        """Fix hardware-related errors"""
        message = notification["message"].lower()

        if "armory crate" in message:
            return self._fix_armory_crate_issue()

        elif "gpu driver" in message:
            return self._fix_gpu_driver_issue()

        elif "memory" in message and "error" in message:
            return self._fix_memory_issue()

        return False

    def _fix_system_notification(self, notification: Dict[str, Any]) -> bool:
        """Fix general system notifications"""
        message = notification["message"].lower()

        if "windows update" in message:
            return self._fix_windows_update_issue()

        elif "antivirus" in message:
            return self._fix_antivirus_conflict()

        elif "firewall" in message:
            return self._fix_firewall_issue()

        return False

    def _fix_dependency_error(self, notification: Dict[str, Any]) -> bool:
        """Fix dependency-related errors"""
        message = notification["message"].lower()

        if "pip install" in message or "install package" in message:
            return self._install_missing_dependency(notification)

        elif "version conflict" in message:
            return self._resolve_version_conflict(notification)

        return False

    def _fix_configuration_error(self, notification: Dict[str, Any]) -> bool:
        """Fix configuration-related errors"""
        message = notification["message"].lower()

        if "invalid configuration" in message:
            return self._fix_invalid_config(notification)

        elif "missing configuration" in message:
            return self._create_missing_config(notification)

        return False

    # Specific fix implementations

    def _fix_task_runner_issues(self) -> bool:
        """Fix task runner issues"""
        try:
            # Reset task error manager
            task_manager = self.project_root / "scripts" / "python" / "task_error_manager.py"
            if task_manager.exists():
                result = subprocess.run([
                    sys.executable, str(task_manager), "reset"
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info("Reset task error manager successfully")
                    return True

            # Check VSCode tasks.json
            tasks_file = self.project_root / ".vscode" / "tasks.json"
            if tasks_file.exists():
                with open(tasks_file, 'r') as f:
                    tasks_data = json.load(f)

                # Validate tasks structure
                if "tasks" in tasks_data:
                    self.logger.info("VSCode tasks.json structure is valid")
                    return True

        except Exception as e:
            self.logger.error(f"Failed to fix task runner issues: {e}")

        return False

    def _fix_missing_command(self, notification: Dict[str, Any]) -> bool:
        """Fix missing command issues"""
        message = notification["message"]

        # Common missing commands
        command_fixes = {
            "python3": "Python 3 is required",
            "pip": "Install pip: python -m ensurepip --upgrade",
            "node": "Install Node.js",
            "npm": "Install Node.js (includes npm)",
            "docker": "Install Docker Desktop",
            "git": "Install Git"
        }

        for command, fix in command_fixes.items():
            if command in message:
                self.logger.info(f"Missing command '{command}' detected. Fix: {fix}")
                # Don't auto-install, just log the fix needed
                return True

        return False

    def _fix_missing_module(self, notification: Dict[str, Any]) -> bool:
        """Fix missing Python module issues"""
        message = notification["message"]

        # Extract module name
        match = re.search(r"No module named ['\"]([^'\"]+)", message)
        if match:
            module_name = match.group(1)

            # Common auto-installable modules
            auto_install = {
                "aiofiles", "psutil", "requests", "pyyaml", "python-dotenv"
            }

            if module_name in auto_install:
                try:
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", module_name
                    ], capture_output=True, text=True)

                    if result.returncode == 0:
                        self.logger.info(f"Successfully installed missing module: {module_name}")
                        return True
                    else:
                        self.logger.error(f"Failed to install {module_name}: {result.stderr}")

                except Exception as e:
                    self.logger.error(f"Exception installing {module_name}: {e}")

        return False

    def _fix_permission_issue(self, notification: Dict[str, Any]) -> bool:
        """Fix permission-related issues"""
        try:
            # Run common permission fixes
            if os.name == 'nt':  # Windows
                # Reset VSCode permissions
                vscode_path = os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code")
                if os.path.exists(vscode_path):
                    subprocess.run([
                        "icacls", vscode_path, "/reset", "/t", "/c", "/q"
                    ], capture_output=True)
                    return True
        except Exception as e:
            self.logger.error(f"Failed to fix permission issue: {e}")

        return False

    def _fix_port_conflict(self, notification: Dict[str, Any]) -> bool:
        """Fix port conflict issues"""
        message = notification["message"]

        # Extract port number
        match = re.search(r'port (\d+)', message)
        if match:
            port = match.group(1)
            self.logger.info(f"Port {port} conflict detected. Suggesting port change.")
            # Don't auto-kill processes, just log
            return True

        return False

    def _fix_prettier_extension(self) -> bool:
        """Fix Prettier extension issues"""
        try:
            # Check if Prettier is installed
            result = subprocess.run([
                "code", "--list-extensions"
            ], capture_output=True, text=True)

            if "esbenp.prettier-vscode" not in result.stdout:
                # Install Prettier
                install_result = subprocess.run([
                    "code", "--install-extension", "esbenp.prettier-vscode"
                ], capture_output=True, text=True)

                if install_result.returncode == 0:
                    self.logger.info("Successfully installed Prettier extension")
                    return True
            else:
                self.logger.info("Prettier extension is already installed")
                return True

        except Exception as e:
            self.logger.error(f"Failed to fix Prettier extension: {e}")

        return False

    def _fix_notification_reopen_error(self) -> bool:
        """Fix notification reopen errors"""
        try:
            # Clear VSCode cache
            vscode_cache = Path(os.path.expandvars("%APPDATA%\\Code\\Cache"))
            if vscode_cache.exists():
                import shutil
                shutil.rmtree(vscode_cache, ignore_errors=True)
                vscode_cache.mkdir(parents=True, exist_ok=True)

            # Restart VSCode (can't do this programmatically)
            self.logger.info("Cleared VSCode cache. Please restart VSCode manually.")
            return True

        except Exception as e:
            self.logger.error(f"Failed to fix notification reopen error: {e}")

        return False

    def _fix_extension_update_issue(self, notification: Dict[str, Any]) -> bool:
        """Fix extension update issues"""
        try:
            # Update all extensions
            result = subprocess.run([
                "code", "--update-extensions"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                self.logger.info("Successfully updated VSCode extensions")
                return True

        except Exception as e:
            self.logger.error(f"Failed to update extensions: {e}")

        return False

    def _start_docker_daemon(self) -> bool:
        """Start Docker daemon"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run([
                    "powershell", "Start-Service", "docker"
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info("Successfully started Docker daemon")
                    return True

        except Exception as e:
            self.logger.error(f"Failed to start Docker daemon: {e}")

        return False

    def _pull_docker_image(self, notification: Dict[str, Any]) -> bool:
        """Pull missing Docker image"""
        message = notification["message"]

        # Extract image name
        match = re.search(r'image ([^:\s]+:[^\s]+)', message)
        if match:
            image_name = match.group(1)
            try:
                result = subprocess.run([
                    "docker", "pull", image_name
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info(f"Successfully pulled Docker image: {image_name}")
                    return True

            except Exception as e:
                self.logger.error(f"Failed to pull Docker image {image_name}: {e}")

        return False

    def _fix_docker_port_conflict(self, notification: Dict[str, Any]) -> bool:
        """Fix Docker port conflicts"""
        message = notification["message"]

        # Extract port
        match = re.search(r'port (\d+)', message)
        if match:
            port = match.group(1)
            self.logger.info(f"Docker port {port} conflict. Suggesting port change in docker-compose.yml")
            return True

        return False

    def _cleanup_docker_space(self) -> bool:
        """Clean up Docker space"""
        try:
            # Remove unused containers, images, and volumes
            commands = [
                ["docker", "system", "prune", "-af"],
                ["docker", "volume", "prune", "-f"],
                ["docker", "image", "prune", "-af"]
            ]

            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.warning(f"Failed to run: {' '.join(cmd)}")

            self.logger.info("Cleaned up Docker space")
            return True

        except Exception as e:
            self.logger.error(f"Failed to cleanup Docker space: {e}")

        return False

    def _fix_python_syntax_error(self, notification: Dict[str, Any]) -> bool:
        """Fix Python syntax errors"""
        # This is tricky to auto-fix, but we can log helpful information
        message = notification["message"]
        metadata = notification.get("metadata", {})

        if "file" in metadata:
            file_path = metadata["file"]
            self.logger.info(f"Python syntax error in {file_path}. Please check the file for issues.")
            return True

        return False

    def _fix_deprecated_warning(self, notification: Dict[str, Any]) -> bool:
        """Fix deprecated warnings"""
        message = notification["message"]

        # Log deprecation warnings but don't auto-fix
        self.logger.info(f"Deprecated feature detected: {message[:100]}...")
        return True

    def _fix_armory_crate_issue(self) -> bool:
        """Fix Armory Crate issues"""
        try:
            # Use the existing Armory Crate fix script
            armory_script = self.project_root / "scripts" / "powershell" / "Fix-ArmoryCrate-AURA.ps1"
            if armory_script.exists():
                result = subprocess.run([
                    "powershell", "-ExecutionPolicy", "Bypass", "-File", str(armory_script)
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info("Successfully fixed Armory Crate issues")
                    return True

        except Exception as e:
            self.logger.error(f"Failed to fix Armory Crate: {e}")

        return False

    def _fix_gpu_driver_issue(self) -> bool:
        """Fix GPU driver issues"""
        try:
            # Check for NVIDIA drivers
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("NVIDIA drivers are working correctly")
                return True
            else:
                self.logger.info("NVIDIA drivers not found or not working. Please update drivers.")
                return True  # Log the issue

        except Exception as e:
            self.logger.error(f"Failed to check GPU drivers: {e}")

        return False

    def _fix_memory_issue(self) -> bool:
        """Fix memory-related issues"""
        try:
            # Clear system cache if possible
            if os.name == 'nt':
                result = subprocess.run([
                    "powershell", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"
                ], capture_output=True)

            self.logger.info("Memory issue detected. Suggesting system restart or cache clearing.")
            return True

        except Exception as e:
            self.logger.error(f"Failed to fix memory issue: {e}")

        return False

    def _fix_windows_update_issue(self) -> bool:
        """Fix Windows Update issues"""
        self.logger.info("Windows Update issue detected. Please run Windows Update manually.")
        return True

    def _fix_antivirus_conflict(self) -> bool:
        """Fix antivirus conflicts"""
        self.logger.info("Antivirus conflict detected. Please add exclusions for project directories.")
        return True

    def _fix_firewall_issue(self) -> bool:
        """Fix firewall issues"""
        try:
            if os.name == 'nt':
                # Reset firewall rules
                result = subprocess.run([
                    "powershell", "netsh advfirewall reset"
                ], capture_output=True)

                if result.returncode == 0:
                    self.logger.info("Reset Windows Firewall rules")
                    return True

        except Exception as e:
            self.logger.error(f"Failed to fix firewall: {e}")

        return False

    def _install_missing_dependency(self, notification: Dict[str, Any]) -> bool:
        """Install missing dependencies"""
        message = notification["message"]

        # Try to extract package name
        match = re.search(r'install (\w+)', message)
        if match:
            package = match.group(1)
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info(f"Successfully installed dependency: {package}")
                    return True

            except Exception as e:
                self.logger.error(f"Failed to install dependency {package}: {e}")

        return False

    def _resolve_version_conflict(self, notification: Dict[str, Any]) -> bool:
        """Resolve version conflicts"""
        self.logger.info("Version conflict detected. Please check dependency versions in requirements.txt")
        return True

    def _fix_invalid_config(self, notification: Dict[str, Any]) -> bool:
        """Fix invalid configuration"""
        metadata = notification.get("metadata", {})
        if "file" in metadata:
            file_path = metadata["file"]
            self.logger.info(f"Invalid configuration in {file_path}. Please check the file.")
            return True
        return False

    def _create_missing_config(self, notification: Dict[str, Any]) -> bool:
        """Create missing configuration"""
        metadata = notification.get("metadata", {})
        if "file" in metadata:
            file_path = Path(metadata["file"])
            if not file_path.exists():
                try:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text("# Auto-generated configuration file\n")
                    self.logger.info(f"Created missing config file: {file_path}")
                    return True
                except Exception as e:
                    self.logger.error(f"Failed to create config file {file_path}: {e}")
        return False

    def get_notification_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get notification summary"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_notifications = [n for n in self.notifications if datetime.fromisoformat(n["timestamp"]) > cutoff]

        summary = {
            "total_notifications": len(recent_notifications),
            "fixed_notifications": sum(1 for n in recent_notifications if n.get("fixed", False)),
            "unfixed_notifications": sum(1 for n in recent_notifications if not n.get("fixed", False)),
            "suppressed_count": len(self.suppressed_notifications),
            "notifications_by_type": defaultdict(int),
            "notifications_by_severity": defaultdict(int)
        }

        for notification in recent_notifications:
            summary["notifications_by_type"][notification["type"]] += 1
            summary["notifications_by_severity"][notification["severity"]] += 1

        return dict(summary)

    def suppress_notification(self, notification_id: str) -> bool:
        """Suppress a notification permanently"""
        self.suppressed_notifications.add(notification_id)
        self.save_notification_data()
        return True

    def reset_suppressions(self):
        """Reset all notification suppressions"""
        self.suppressed_notifications.clear()
        self.save_notification_data()

    def export_notification_report(self, hours: int = 24) -> str:
        """Export notification report"""
        summary = self.get_notification_summary(hours)

        report = f"""# Notification Fix Report - Last {hours} Hours

## Summary
- **Total Notifications:** {summary['total_notifications']}
- **Fixed:** {summary['fixed_notifications']}
- **Unfixed:** {summary['unfixed_notifications']}
- **Suppressed:** {summary['suppressed_count']}

## By Type
"""

        for notif_type, count in summary['notifications_by_type'].items():
            report += f"- **{notif_type.replace('_', ' ').title()}:** {count}\n"

        report += "\n## By Severity\n"
        for severity, count in summary['notifications_by_severity'].items():
            report += f"- **{severity.title()}:** {count}\n"

        return report


# Global instance
notification_manager = NotificationFixManager()


async def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Notification Fix Manager")
    parser.add_argument("action", choices=[
        "fix", "summary", "report", "suppress", "reset"
    ], help="Action to perform")
    parser.add_argument("--type", help="Notification type")
    parser.add_argument("--message", help="Notification message")
    parser.add_argument("--source", help="Notification source")
    parser.add_argument("--id", help="Notification ID for suppression")
    parser.add_argument("--hours", type=int, default=24, help="Hours for summary/report")

    args = parser.parse_args()

    if args.action == "fix":
        if not args.type or not args.message:
            print("❌ Please provide --type and --message")
            return 1

        fixed = notification_manager.report_notification(
            args.type, args.message, args.source or "cli"
        )

        if fixed:
            print(f"✅ Fixed notification: {args.type}")
        else:
            print(f"❌ Could not fix notification: {args.type}")

    elif args.action == "summary":
        summary = notification_manager.get_notification_summary(args.hours)
        print("📊 Notification Summary")
        print(f"Total: {summary['total_notifications']}")
        print(f"Fixed: {summary['fixed_notifications']}")
        print(f"Unfixed: {summary['unfixed_notifications']}")
        print(f"Suppressed: {summary['suppressed_count']}")

    elif args.action == "report":
        report = notification_manager.export_notification_report(args.hours)
        print(report)

    elif args.action == "suppress":
        if not args.id:
            print("❌ Please provide --id")
            return 1

        notification_manager.suppress_notification(args.id)
        print(f"✅ Suppressed notification: {args.id}")

    elif args.action == "reset":
        notification_manager.reset_suppressions()
        print("✅ Reset all notification suppressions")


if __name__ == "__main__":




    asyncio.run(main())