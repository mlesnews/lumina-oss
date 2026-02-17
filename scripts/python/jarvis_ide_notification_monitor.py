#!/usr/bin/env python3
"""
JARVIS IDE Notification Monitor

Monitors and responds to Cursor IDE/VSCode notifications automatically.
Handles Git warnings, errors, and other IDE notifications.

Tags: #CURSOR-IDE #AUTOMATION #NOTIFICATIONS @CURSOR-ENGINEER
"""

import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISIDENotifications")


class JARVISIDENotificationMonitor:
    """
    JARVIS IDE Notification Monitor

    Monitors and responds to Cursor IDE/VSCode notifications.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.is_git_repo = (project_root / ".git").exists()

        # Notification patterns to monitor
        self.notification_patterns = {
            "git_too_many_changes": {
                "pattern": r"too many active changes",
                "action": "auto_commit",
                "priority": "high",
                "description": "Git repository has too many active changes",
            },
            "git_unstaged_changes": {
                "pattern": r"unstaged changes",
                "action": "auto_stage",
                "priority": "medium",
                "description": "Unstaged changes detected",
            },
            "git_conflict": {
                "pattern": r"merge conflict|conflict",
                "action": "notify",
                "priority": "critical",
                "description": "Git merge conflict detected",
            },
            "python_error": {
                "pattern": r"python.*error|syntax error",
                "action": "notify",
                "priority": "high",
                "description": "Python error detected",
            },
            "import_error": {
                "pattern": r"import.*error|cannot import",
                "action": "notify",
                "priority": "medium",
                "description": "Import error detected",
            },
            "mcp_restart": {
                "pattern": r"MCP.*restart|MCP server.*restart|mcp.*restarting",
                "action": "mcp_fix",
                "priority": "high",
                "description": "MCP server restart loop",
            },
            "mcp_error": {
                "pattern": r"MCP.*error|MCP.*failed|mcp.*(error|failed)|Model Context Protocol",
                "action": "mcp_fix",
                "priority": "high",
                "description": "MCP connection or protocol error",
            },
            "mcp_secrets": {
                "pattern": r"secrets required|SECRETS REQUIRED",
                "action": "mcp_fix",
                "priority": "medium",
                "description": "MCP server needs secrets (e.g. ElevenLabs)",
            },
            "mcp_config_error": {
                "pattern": r"must have either a command \(for stdio\) or url \(for SSE\)|cursor-browser-extension|MCP configuration errors",
                "action": "mcp_fix",
                "priority": "high",
                "description": "MCP config error (e.g. cursor-browser-extension missing command/url)",
            },
        }

        self.logger.info("✅ JARVIS IDE Notification Monitor initialized")

    def check_git_status(self) -> Dict[str, Any]:
        """Check Git status for issues"""
        if not self.is_git_repo:
            return {"status": "not_git_repo", "changes": 0}

        try:
            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return {"status": "error", "error": result.stderr}

            lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
            change_count = len(lines)

            # Check for too many changes (Git typically warns at 1000+)
            too_many_changes = change_count > 1000

            return {
                "status": "ok",
                "changes": change_count,
                "too_many_changes": too_many_changes,
                "files": lines[:20] if lines else [],  # First 20 files
            }

        except subprocess.TimeoutExpired:
            return {"status": "timeout", "changes": 0}
        except Exception as e:
            self.logger.error(f"❌ Error checking Git status: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def handle_git_too_many_changes(self) -> Dict[str, Any]:
        """Handle 'too many active changes' Git warning"""
        self.logger.warning("⚠️  Git repository has too many active changes - Auto-committing...")

        try:
            # Import auto git manager
            from jarvis_auto_git_manager import JARVISAutoGitManager

            git_manager = JARVISAutoGitManager(self.project_root)

            # Auto-commit all changes
            result = git_manager.auto_stage_and_commit(
                message="[AUTO] Auto-commit to resolve 'too many active changes' warning",
                operation="git_cleanup",
            )

            if result.get("success"):
                self.logger.info(f"✅ Auto-committed {result.get('changes_count', 0)} changes")
                return {
                    "success": True,
                    "action": "auto_committed",
                    "changes_committed": result.get("changes_count", 0),
                    "commit_hash": result.get("commit_hash"),
                }
            else:
                self.logger.error(f"❌ Failed to auto-commit: {result.get('error')}")
                return {
                    "success": False,
                    "action": "auto_commit_failed",
                    "error": result.get("error"),
                }

        except ImportError:
            self.logger.error("❌ JARVISAutoGitManager not available")
            return {"success": False, "error": "Auto git manager not available"}
        except Exception as e:
            self.logger.error(f"❌ Error handling Git warning: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def monitor_git_notifications(self) -> Dict[str, Any]:
        """Monitor Git-related notifications"""
        self.logger.info("🔍 Monitoring Git notifications...")

        git_status = self.check_git_status()

        if git_status.get("too_many_changes"):
            self.logger.warning("⚠️  Too many Git changes detected - Handling automatically...")
            return self.handle_git_too_many_changes()

        if git_status.get("changes", 0) > 100:
            self.logger.info(f"ℹ️  {git_status['changes']} Git changes detected (not critical)")
            return {
                "success": True,
                "status": "monitoring",
                "changes": git_status["changes"],
                "action": "none_needed",
            }

        return {"success": True, "status": "ok", "changes": git_status.get("changes", 0)}

    def check_ide_logs(self) -> Dict[str, Any]:
        """Check IDE logs for notifications (if accessible)"""
        # This would require IDE-specific log access
        # For now, we'll focus on Git status monitoring
        return {
            "status": "not_implemented",
            "note": "IDE log monitoring requires IDE-specific APIs",
        }

    def check_mcp_config(self) -> Dict[str, Any]:
        """Check MCP config and Docker gateway; suggest fix if MCP errors are likely."""
        out: Dict[str, Any] = {
            "status": "ok",
            "mcp_config_valid": True,
            "recommendations": [],
            "fix_script": str(self.project_root / "scripts" / "fix_mcp_notifications_laptop.ps1"),
        }
        # Project MCP config
        project_mcp = self.project_root / ".cursor" / "mcp.json"
        if not project_mcp.exists():
            out["recommendations"].append("Missing .cursor/mcp.json")
            out["mcp_config_valid"] = False
            return out
        try:
            with open(project_mcp, encoding="utf-8") as f:
                data = json.load(f)
            servers = data.get("mcpServers", {})
            for name, cfg in servers.items():
                if isinstance(cfg, dict) and (cfg.get("url") or "http" in str(cfg).lower()):
                    out["recommendations"].append(
                        f"Remove HTTP/URL from MCP server '{name}'; MCP uses stdio only."
                    )
                    out["mcp_config_valid"] = False
        except (json.JSONDecodeError, OSError) as e:
            out["status"] = "error"
            out["recommendations"].append(f"Fix .cursor/mcp.json: {e}")
            out["mcp_config_valid"] = False
        # Docker gateway availability (optional)
        try:
            r = subprocess.run(
                ["docker", "mcp", "client", "ls"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root,
            )
            if r.returncode != 0:
                out["recommendations"].append(
                    "Docker MCP not available. Start Docker Desktop and run: docker mcp client connect cursor"
                )
            elif (
                "cursor" not in (r.stdout or "").lower()
                and "connected" not in (r.stdout or "").lower()
            ):
                out["recommendations"].append(
                    "Run: docker mcp client connect cursor (then restart Cursor)"
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            out["recommendations"].append(
                "Docker not running or not in PATH. Start Docker Desktop for MCP gateway."
            )
        return out

    def monitor_mcp_notifications(self) -> Dict[str, Any]:
        """Monitor MCP-related state; report and recommend fixes (for use when IDE shows MCP errors)."""
        self.logger.info("🔍 Checking MCP config and gateway...")
        result = self.check_mcp_config()
        if result.get("recommendations"):
            self.logger.warning("⚠️  MCP recommendations: %s", result["recommendations"])
            result["action"] = "run_fix_script"
            result["fix_script"] = str(
                self.project_root / "scripts" / "fix_mcp_notifications_laptop.ps1"
            )
        else:
            self.logger.info("✅ MCP config and gateway OK")
        return result

    def create_notification_handler(self) -> Dict[str, Any]:
        """Create a notification handler script"""
        self.logger.info("📝 Creating IDE notification handler...")

        handler_script = """#!/usr/bin/env python3
\"\"\"
IDE Notification Handler

Automatically handles IDE notifications by calling JARVIS.
\"\"\"

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from jarvis_ide_notification_monitor import JARVISIDENotificationMonitor

monitor = JARVISIDENotificationMonitor(project_root)
result = monitor.monitor_git_notifications()

print(json.dumps(result, indent=2))
"""

        handler_path = self.project_root / "scripts" / "python" / "handle_ide_notification.py"
        try:
            with open(handler_path, "w", encoding="utf-8") as f:
                f.write(handler_script)
            handler_path.chmod(0o755)  # Make executable
            self.logger.info(f"✅ Created notification handler at {handler_path}")
            return {"success": True, "path": str(handler_path)}
        except Exception as e:
            self.logger.error(f"❌ Failed to create handler: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def setup_auto_monitoring(self) -> Dict[str, Any]:
        """Set up automatic monitoring"""
        self.logger.info("⚙️  Setting up automatic IDE notification monitoring...")

        # Create a task in tasks.json to run monitoring
        tasks_path = self.project_root / ".cursor" / "tasks.json"

        try:
            if tasks_path.exists():
                with open(tasks_path) as f:
                    tasks = json.load(f)
            else:
                tasks = {"version": "2.0.0", "tasks": []}

            # Add monitoring task
            monitoring_task = {
                "label": "JARVIS: Monitor IDE Notifications",
                "type": "shell",
                "command": "python",
                "args": [
                    "${workspaceFolder}/scripts/python/jarvis_ide_notification_monitor.py",
                    "--monitor",
                ],
                "problemMatcher": [],
                "presentation": {"reveal": "silent", "panel": "shared"},
                "runOptions": {"runOn": "folderOpen"},
            }

            # Check if task already exists
            existing = [t for t in tasks["tasks"] if t.get("label") == monitoring_task["label"]]
            if not existing:
                tasks["tasks"].append(monitoring_task)

                with open(tasks_path, "w", encoding="utf-8") as f:
                    json.dump(tasks, f, indent=2, ensure_ascii=False)

                self.logger.info(f"✅ Added monitoring task to {tasks_path}")
                return {"success": True, "task_added": True}
            else:
                self.logger.info("ℹ️  Monitoring task already exists")
                return {"success": True, "task_added": False, "exists": True}

        except Exception as e:
            self.logger.error(f"❌ Failed to setup monitoring: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def continuous_monitor(self, interval: int = 60) -> None:
        """Continuously monitor IDE notifications"""
        self.logger.info(f"🔄 Starting continuous monitoring (interval: {interval}s)...")

        try:
            while True:
                result = self.monitor_git_notifications()

                if result.get("action") == "auto_committed":
                    self.logger.info(
                        f"✅ Handled notification: {result.get('changes_committed', 0)} changes committed"
                    )

                time.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Monitoring error: {e}", exc_info=True)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS IDE Notification Monitor")
        parser.add_argument(
            "--monitor", action="store_true", help="Monitor Git and MCP notifications"
        )
        parser.add_argument("--check", action="store_true", help="Check Git status")
        parser.add_argument(
            "--mcp-check", action="store_true", help="Check MCP config and Docker gateway"
        )
        parser.add_argument("--handle", action="store_true", help="Handle Git warnings")
        parser.add_argument("--setup", action="store_true", help="Setup auto-monitoring")
        parser.add_argument("--continuous", action="store_true", help="Continuous monitoring")
        parser.add_argument(
            "--interval", type=int, default=60, help="Monitoring interval (seconds)"
        )

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        monitor = JARVISIDENotificationMonitor(project_root)

        if args.check:
            result = monitor.check_git_status()
            print(json.dumps(result, indent=2, default=str))

        elif args.handle:
            result = monitor.handle_git_too_many_changes()
            print(json.dumps(result, indent=2, default=str))

        elif args.setup:
            result = monitor.setup_auto_monitoring()
            print(json.dumps(result, indent=2, default=str))

        elif args.continuous:
            monitor.continuous_monitor(interval=args.interval)

        elif args.mcp_check:
            result = monitor.monitor_mcp_notifications()
            print(json.dumps(result, indent=2, default=str))

        elif args.monitor:
            git_result = monitor.monitor_git_notifications()
            mcp_result = monitor.monitor_mcp_notifications()
            combined = {
                "git": git_result,
                "mcp": mcp_result,
            }
            print(json.dumps(combined, indent=2, default=str))

        else:
            # Default: monitor once
            result = monitor.monitor_git_notifications()
            print(json.dumps(result, indent=2, default=str))

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
