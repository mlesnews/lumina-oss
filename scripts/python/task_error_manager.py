#!/usr/bin/env python3
"""
Task Error Manager - Suppress Excessive VSCode Task Notifications

Manages task errors to prevent excessive notifications while providing
comprehensive error reporting and diagnostics.

Features:
- Aggregates multiple task errors into single notifications
- Suppresses repetitive error messages
- Provides detailed error analysis and solutions
- Background error monitoring and reporting
- Error pattern recognition and automatic fixes
- User-controlled notification preferences
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
from typing import Dict, List, Any, Optional, Tuple, Deque
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class TaskErrorManager:
    """Manages VSCode task errors to prevent excessive notifications"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "task_errors"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Error tracking
        self.error_history: Deque[Dict[str, Any]] = deque(maxlen=1000)
        self.active_errors: Dict[str, Dict[str, Any]] = {}
        self.suppressed_notifications: Dict[str, datetime] = {}
        self.error_patterns: Dict[str, Dict[str, Any]] = {}

        # Configuration
        self.notification_cooldown = 300  # 5 minutes between similar notifications
        self.max_simultaneous_notifications = 3
        self.error_aggregation_window = 60  # 1 minute window for aggregation

        # Setup logging
        self.logger = logging.getLogger("TaskErrorManager")
        self.logger.setLevel(logging.INFO)

        # Add console handler if not already present
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Load existing data
        self._load_error_data()

    def _load_error_data(self):
        """Load existing error data"""
        try:
            # Load error history
            history_file = self.data_dir / "error_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                    self.error_history.extend(history_data[-1000:])  # Keep last 1000

            # Load error patterns
            patterns_file = self.data_dir / "error_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    self.error_patterns = json.load(f)

        except Exception as e:
            self.logger.warning(f"Failed to load error data: {e}")

    def save_error_data(self):
        """Save error data"""
        try:
            # Save error history
            with open(self.data_dir / "error_history.json", 'w') as f:
                json.dump(list(self.error_history), f, indent=2)

            # Save error patterns
            with open(self.data_dir / "error_patterns.json", 'w') as f:
                json.dump(self.error_patterns, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save error data: {e}")

    def report_task_error(self, task_name: str, error_message: str,
                         exit_code: Optional[int] = None,
                         command: Optional[str] = None) -> bool:
        """
        Report a task error and decide whether to show notification

        Returns True if notification should be shown, False if suppressed
        """

        error_key = self._generate_error_key(task_name, error_message)
        timestamp = datetime.now()

        # Create error record
        error_record = {
            "task_name": task_name,
            "error_message": error_message,
            "exit_code": exit_code,
            "command": command,
            "timestamp": timestamp.isoformat(),
            "error_key": error_key,
            "pattern": self._identify_error_pattern(error_message),
            "severity": self._assess_error_severity(error_message, exit_code)
        }

        # Add to history
        self.error_history.append(error_record)

        # Update active errors
        self.active_errors[error_key] = error_record

        # Check if notification should be suppressed
        should_notify = self._should_show_notification(error_key, error_record)

        if should_notify:
            # Update suppression tracking
            self.suppressed_notifications[error_key] = timestamp

            # Analyze error for potential fixes
            self._analyze_error_for_fixes(error_record)

        # Clean up old suppressed notifications
        self._cleanup_old_suppressions()

        # Save data
        self.save_error_data()

        return should_notify

    def _generate_error_key(self, task_name: str, error_message: str) -> str:
        """Generate a unique key for similar errors"""
        # Normalize error message for grouping
        normalized = re.sub(r'\d+', '<NUM>', error_message.lower())
        normalized = re.sub(r'[\w\-\.]+\.[\w\-\.]+', '<PATH>', normalized)

        return f"{task_name}:{hash(normalized) % 10000}"

    def _identify_error_pattern(self, error_message: str) -> str:
        """Identify the error pattern for categorization"""
        patterns = {
            "module_not_found": r"ModuleNotFoundError|No module named",
            "file_not_found": r"FileNotFoundError|No such file",
            "permission_denied": r"PermissionError|Access denied",
            "connection_failed": r"ConnectionError|Failed to connect",
            "timeout": r"TimeoutError|timeout",
            "syntax_error": r"SyntaxError|invalid syntax",
            "import_error": r"ImportError|cannot import",
            "command_not_found": r"command not found|is not recognized",
            "port_in_use": r"port.*already in use|address.*in use",
            "disk_space": r"No space left|disk.*full",
            "memory_error": r"MemoryError|out of memory",
            "network_error": r"NetworkError|connection.*failed"
        }

        for pattern_name, regex in patterns.items():
            if re.search(regex, error_message, re.IGNORECASE):
                return pattern_name

        return "unknown"

    def _assess_error_severity(self, error_message: str, exit_code: Optional[int]) -> str:
        """Assess the severity of an error"""
        if exit_code and exit_code > 100:
            return "critical"
        elif "critical" in error_message.lower() or "fatal" in error_message.lower():
            return "critical"
        elif exit_code and exit_code > 1:
            return "high"
        elif "error" in error_message.lower() or "exception" in error_message.lower():
            return "high"
        elif "warning" in error_message.lower():
            return "medium"
        else:
            return "low"

    def _should_show_notification(self, error_key: str, error_record: Dict[str, Any]) -> bool:
        """Determine if a notification should be shown"""

        # Always show critical errors
        if error_record["severity"] == "critical":
            return True

        # Check cooldown period
        last_notification = self.suppressed_notifications.get(error_key)
        if last_notification and (datetime.now() - last_notification).seconds < self.notification_cooldown:
            return False

        # Check simultaneous notification limit
        recent_notifications = sum(
            1 for ts in self.suppressed_notifications.values()
            if (datetime.now() - ts).seconds < self.error_aggregation_window
        )

        if recent_notifications >= self.max_simultaneous_notifications:
            return False

        # Check if this is a repetitive error
        similar_recent_errors = sum(
            1 for error in list(self.error_history)[-10:]  # Last 10 errors
            if error.get("error_key") == error_key
        )

        if similar_recent_errors >= 3:
            # Only show every 5th occurrence of repetitive errors
            return similar_recent_errors % 5 == 0

        return True

    def _analyze_error_for_fixes(self, error_record: Dict[str, Any]):
        """Analyze error for potential automatic fixes"""

        error_pattern = error_record["pattern"]
        task_name = error_record["task_name"]
        error_message = error_record["error_message"]

        # Pattern-specific fixes
        if error_pattern == "module_not_found":
            self._fix_missing_module(error_record)

        elif error_pattern == "command_not_found":
            self._fix_missing_command(error_record)

        elif error_pattern == "port_in_use":
            self._fix_port_conflict(error_record)

        elif error_pattern == "file_not_found":
            self._fix_missing_file(error_record)

        # Update error patterns for learning
        self._update_error_patterns(error_record)

    def _fix_missing_module(self, error_record: Dict[str, Any]):
        """Attempt to fix missing module errors"""
        error_message = error_record["error_message"]

        # Extract module name
        match = re.search(r"No module named ['\"]([^'\"]+)", error_message)
        if match:
            module_name = match.group(1)

            # Check if it's a known module that can be installed
            installable_modules = {
                "aiofiles": "pip install aiofiles",
                "psutil": "pip install psutil",
                "requests": "pip install requests",
                "pyyaml": "pip install pyyaml",
                "python-dotenv": "pip install python-dotenv"
            }

            if module_name in installable_modules:
                fix_command = installable_modules[module_name]
                error_record["suggested_fix"] = fix_command
                error_record["fix_type"] = "install_module"

    def _fix_missing_command(self, error_record: Dict[str, Any]):
        """Attempt to fix missing command errors"""
        error_message = error_record["error_message"]

        # Common missing commands and their fixes
        command_fixes = {
            "python3": "Install Python 3 or use 'python' instead",
            "pip": "Install pip: python -m ensurepip --upgrade",
            "node": "Install Node.js from nodejs.org",
            "npm": "Install Node.js (includes npm)",
            "docker": "Install Docker Desktop",
            "git": "Install Git from git-scm.com"
        }

        for command, fix in command_fixes.items():
            if command in error_message:
                error_record["suggested_fix"] = fix
                error_record["fix_type"] = "install_tool"
                break

    def _fix_port_conflict(self, error_record: Dict[str, Any]):
        """Attempt to fix port conflict errors"""
        error_message = error_record["error_message"]

        # Extract port number
        match = re.search(r'port (\d+)', error_message)
        if match:
            port = match.group(1)
            error_record["suggested_fix"] = f"Change port to {int(port) + 1} or kill process using port {port}"
            error_record["fix_type"] = "change_port"

    def _fix_missing_file(self, error_record: Dict[str, Any]):
        """Attempt to fix missing file errors"""
        error_message = error_record["error_message"]

        # Extract file path
        match = re.search(r"No such file[^']*['\"]([^'\"]+)", error_message)
        if match:
            file_path = match.group(1)
            error_record["suggested_fix"] = f"Create file: {file_path} or check file path"
            error_record["fix_type"] = "create_file"

    def _update_error_patterns(self, error_record: Dict[str, Any]):
        """Update error patterns for learning"""
        pattern = error_record["pattern"]
        error_key = error_record["error_key"]

        if pattern not in self.error_patterns:
            self.error_patterns[pattern] = {
                "count": 0,
                "first_seen": error_record["timestamp"],
                "last_seen": error_record["timestamp"],
                "common_tasks": [],
                "suggested_fixes": []
            }

        pattern_data = self.error_patterns[pattern]
        pattern_data["count"] += 1
        pattern_data["last_seen"] = error_record["timestamp"]

        # Track common tasks for this pattern
        task_name = error_record["task_name"]
        if task_name not in pattern_data["common_tasks"]:
            pattern_data["common_tasks"].append(task_name)

        # Track suggested fixes
        if "suggested_fix" in error_record:
            fix = error_record["suggested_fix"]
            if fix not in pattern_data["suggested_fixes"]:
                pattern_data["suggested_fixes"].append(fix)

    def _cleanup_old_suppressions(self):
        """Clean up old suppressed notification tracking"""
        cutoff = datetime.now() - timedelta(hours=1)
        self.suppressed_notifications = {
            k: v for k, v in self.suppressed_notifications.items()
            if v > cutoff
        }

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get a summary of errors in the specified time period"""

        cutoff = datetime.now() - timedelta(hours=hours)
        recent_errors = [e for e in self.error_history if datetime.fromisoformat(e["timestamp"]) > cutoff]

        summary = {
            "total_errors": len(recent_errors),
            "time_period_hours": hours,
            "errors_by_severity": defaultdict(int),
            "errors_by_pattern": defaultdict(int),
            "errors_by_task": defaultdict(int),
            "most_common_errors": [],
            "suppressed_notifications": len(self.suppressed_notifications),
            "active_error_patterns": len(self.error_patterns)
        }

        for error in recent_errors:
            summary["errors_by_severity"][error["severity"]] += 1
            summary["errors_by_pattern"][error["pattern"]] += 1
            summary["errors_by_task"][error["task_name"]] += 1

        # Get most common errors
        pattern_counts = sorted(summary["errors_by_pattern"].items(), key=lambda x: x[1], reverse=True)
        summary["most_common_errors"] = pattern_counts[:5]

        return dict(summary)

    def apply_error_fix(self, error_key: str) -> bool:
        """Apply an automatic fix for a known error"""

        if error_key not in self.active_errors:
            return False

        error_record = self.active_errors[error_key]
        fix_type = error_record.get("fix_type")

        try:
            if fix_type == "install_module":
                module_name = error_record["error_message"].split("'")[-2]
                subprocess.run([sys.executable, "-m", "pip", "install", module_name],
                             capture_output=True, check=True)
                return True

            elif fix_type == "install_tool":
                # For now, just log that manual installation is needed
                self.logger.info(f"Manual installation needed: {error_record.get('suggested_fix')}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to apply fix for {error_key}: {e}")

        return False

    def reset_error_suppression(self):
        """Reset all error suppression (for debugging)"""
        self.suppressed_notifications.clear()
        self.logger.info("Error suppression reset")

    def export_error_report(self, hours: int = 24) -> str:
        """Export a comprehensive error report"""

        summary = self.get_error_summary(hours)

        report = f"""
# VSCode Task Error Report - Last {hours} Hours

## Summary
- **Total Errors:** {summary['total_errors']}
- **Suppressed Notifications:** {summary['suppressed_notifications']}
- **Active Error Patterns:** {summary['active_error_patterns']}

## Errors by Severity
"""

        for severity, count in summary['errors_by_severity'].items():
            report += f"- **{severity.title()}:** {count}\n"

        report += "\n## Most Common Error Patterns\n"
        for pattern, count in summary['most_common_errors']:
            report += f"- **{pattern.replace('_', ' ').title()}:** {count}\n"

        report += "\n## Errors by Task\n"
        task_errors = sorted(summary['errors_by_task'].items(), key=lambda x: x[1], reverse=True)
        for task, count in task_errors[:10]:  # Top 10
            report += f"- **{task}:** {count}\n"

        # Add suggested fixes
        report += "\n## Suggested Fixes\n"

        for pattern_name, pattern_data in list(self.error_patterns.items())[:5]:  # Top 5 patterns
            if pattern_data.get("suggested_fixes"):
                report += f"\n### {pattern_name.replace('_', ' ').title()}\n"
                for fix in pattern_data["suggested_fixes"][:3]:  # Top 3 fixes
                    report += f"- {fix}\n"

        return report


class VSCodeTaskMonitor:
    """Monitors VSCode tasks and manages error notifications"""

    def __init__(self):
        self.error_manager = TaskErrorManager()
        self.task_status: Dict[str, Dict[str, Any]] = {}
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        self.logger = self.error_manager.logger  # Use the same logger as TaskErrorManager

    async def monitor_tasks(self):
        """Monitor VSCode tasks continuously"""
        self.logger.info("Starting VSCode task monitoring...")

        while True:
            try:
                # Check for new task errors (this would integrate with VSCode API)
                await self._check_task_status()

                # Process notification queue
                await self._process_notifications()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Task monitoring error: {e}")
                await asyncio.sleep(60)

    async def _check_task_status(self):
        """Check status of running tasks"""
        # This would integrate with VSCode's task API
        # For now, we'll rely on error reporting from tasks
        pass

    async def _process_notifications(self):
        """Process queued notifications"""
        while not self.notification_queue.empty():
            notification = await self.notification_queue.get()

            # Apply error management logic
            should_show = self.error_manager.report_task_error(
                notification.get("task_name", "unknown"),
                notification.get("error_message", ""),
                notification.get("exit_code"),
                notification.get("command")
            )

            if should_show:
                await self._show_notification(notification)

    async def _show_notification(self, notification: Dict[str, Any]):
        """Show a notification to the user"""
        # This would integrate with VSCode's notification API
        task_name = notification.get("task_name", "Unknown Task")
        error_msg = notification.get("error_message", "Unknown error")

        # Create a concise notification
        title = f"Task Error: {task_name}"
        message = self._truncate_message(error_msg, 100)

        # Add suggested fix if available
        suggested_fix = self._get_suggested_fix(notification)
        if suggested_fix:
            message += f"\n💡 Fix: {suggested_fix}"

        print(f"🔔 {title}: {message}")

    def _truncate_message(self, message: str, max_length: int) -> str:
        """Truncate message to max length"""
        if len(message) <= max_length:
            return message
        return message[:max_length - 3] + "..."

    def _get_suggested_fix(self, notification: Dict[str, Any]) -> Optional[str]:
        """Get suggested fix for notification"""
        task_name = notification.get("task_name", "")
        error_message = notification.get("error_message", "")

        error_key = self.error_manager._generate_error_key(task_name, error_message)

        if error_key in self.error_manager.active_errors:
            error_record = self.error_manager.active_errors[error_key]
            return error_record.get("suggested_fix")

        return None

    def report_task_error(self, task_name: str, error_message: str,
                         exit_code: Optional[int] = None,
                         command: Optional[str] = None):
        """Report a task error for processing"""

        # Queue the notification for processing
        asyncio.create_task(self.notification_queue.put({
            "task_name": task_name,
            "error_message": error_message,
            "exit_code": exit_code,
            "command": command,
            "timestamp": datetime.now().isoformat()
        }))


# Global instance for easy access
task_monitor = VSCodeTaskMonitor()


async def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Task Error Manager")
    parser.add_argument("action", choices=[
        "summary", "report", "reset", "fix", "monitor"
    ], help="Action to perform")
    parser.add_argument("--hours", type=int, default=24, help="Hours for summary/report")
    parser.add_argument("--error-key", help="Error key for fix action")

    args = parser.parse_args()

    manager = TaskErrorManager()

    if args.action == "summary":
        summary = manager.get_error_summary(args.hours)
        print("📊 Task Error Summary")
        print(f"Total Errors (last {args.hours}h): {summary['total_errors']}")
        print(f"Suppressed Notifications: {summary['suppressed_notifications']}")
        print("\nErrors by Severity:")
        for severity, count in summary['errors_by_severity'].items():
            print(f"  {severity.title()}: {count}")
        print("\nMost Common Patterns:")
        for pattern, count in summary['most_common_errors']:
            print(f"  {pattern}: {count}")

    elif args.action == "report":
        report = manager.export_error_report(args.hours)
        print(report)

    elif args.action == "reset":
        manager.reset_error_suppression()
        print("✅ Error suppression reset")

    elif args.action == "fix":
        if not args.error_key:
            print("❌ Please provide --error-key")
            return 1

        success = manager.apply_error_fix(args.error_key)
        if success:
            print(f"✅ Applied fix for error {args.error_key}")
        else:
            print(f"❌ Failed to apply fix for error {args.error_key}")

    elif args.action == "monitor":
        print("🚀 Starting task error monitoring...")
        await task_monitor.monitor_tasks()


if __name__ == "__main__":


    asyncio.run(main())