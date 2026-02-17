#!/usr/bin/env python3
"""
JARVIS Cursor Terminal Manager
Manages terminal startup configuration in Cursor IDE.

Tags: #CURSOR #TERMINAL #STARTUP #AUTOMATION @AUTO
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCursorTerminalManager")


class CursorTerminalManager:
    """
    Manages terminal startup configuration in Cursor IDE.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Cursor configuration paths
        self.cursor_dir = project_root / ".cursor"
        self.tasks_file = self.cursor_dir / "tasks.json"
        self.settings_file = self.cursor_dir / "settings.json"

        self.logger.info("✅ Cursor Terminal Manager initialized")
        self.logger.info(f"   Tasks File: {self.tasks_file}")
        self.logger.info(f"   Settings File: {self.settings_file}")

    def get_auto_start_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks that auto-start on folder open"""
        auto_start_tasks = []

        if not self.tasks_file.exists():
            return auto_start_tasks

        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                tasks_config = json.load(f)

            tasks = tasks_config.get("tasks", [])
            for task in tasks:
                run_options = task.get("runOptions", {})
                if run_options.get("runOn") == "folderOpen":
                    auto_start_tasks.append({
                        "label": task.get("label", "Unknown"),
                        "command": task.get("command", ""),
                        "args": task.get("args", []),
                        "presentation": task.get("presentation", {}),
                        "runOn": run_options.get("runOn")
                    })

        except Exception as e:
            self.logger.error(f"❌ Failed to read tasks.json: {e}", exc_info=True)

        return auto_start_tasks

    def disable_auto_start(self, task_label: Optional[str] = None) -> bool:
        """Disable auto-start for a specific task or all tasks"""
        if not self.tasks_file.exists():
            self.logger.warning("⚠️  tasks.json not found")
            return False

        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                tasks_config = json.load(f)

            tasks = tasks_config.get("tasks", [])
            modified = False

            for task in tasks:
                if task_label is None or task.get("label") == task_label:
                    if "runOptions" in task:
                        if task["runOptions"].get("runOn") == "folderOpen":
                            del task["runOptions"]["runOn"]
                            if not task["runOptions"]:
                                del task["runOptions"]
                            modified = True
                            self.logger.info(f"   ✅ Disabled auto-start for: {task.get('label')}")

            if modified:
                # Backup original
                backup_file = self.tasks_file.with_suffix('.json.backup')
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(tasks_config, f, indent=2)
                self.logger.info(f"   💾 Backup saved to: {backup_file.name}")

                # Write updated config
                with open(self.tasks_file, 'w', encoding='utf-8') as f:
                    json.dump(tasks_config, f, indent=2)

                self.logger.info("✅ Updated tasks.json")
                return True
            else:
                self.logger.info("ℹ️  No changes needed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Failed to update tasks.json: {e}", exc_info=True)
            return False

    def enable_auto_start(self, task_label: str) -> bool:
        """Enable auto-start for a specific task"""
        if not self.tasks_file.exists():
            self.logger.warning("⚠️  tasks.json not found")
            return False

        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                tasks_config = json.load(f)

            tasks = tasks_config.get("tasks", [])
            modified = False

            for task in tasks:
                if task.get("label") == task_label:
                    if "runOptions" not in task:
                        task["runOptions"] = {}
                    task["runOptions"]["runOn"] = "folderOpen"
                    modified = True
                    self.logger.info(f"   ✅ Enabled auto-start for: {task_label}")
                    break

            if modified:
                # Backup original
                backup_file = self.tasks_file.with_suffix('.json.backup')
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(tasks_config, f, indent=2)
                self.logger.info(f"   💾 Backup saved to: {backup_file.name}")

                # Write updated config
                with open(self.tasks_file, 'w', encoding='utf-8') as f:
                    json.dump(tasks_config, f, indent=2)

                self.logger.info("✅ Updated tasks.json")
                return True
            else:
                self.logger.warning(f"⚠️  Task '{task_label}' not found")
                return False

        except Exception as e:
            self.logger.error(f"❌ Failed to update tasks.json: {e}", exc_info=True)
            return False

    def list_auto_start_tasks(self) -> None:
        """List all auto-start tasks"""
        self.logger.info("="*80)
        self.logger.info("AUTO-START TERMINALS")
        self.logger.info("="*80)

        auto_start_tasks = self.get_auto_start_tasks()

        if not auto_start_tasks:
            self.logger.info("ℹ️  No auto-start tasks found")
            return

        self.logger.info(f"📋 Found {len(auto_start_tasks)} auto-start task(s):")
        self.logger.info("")

        for i, task in enumerate(auto_start_tasks, 1):
            self.logger.info(f"{i}. {task['label']}")
            self.logger.info(f"   Command: {task['command']} {' '.join(task.get('args', []))}")
            self.logger.info(f"   Presentation: {task['presentation'].get('reveal', 'default')}")
            self.logger.info(f"   Panel: {task['presentation'].get('panel', 'default')}")
            self.logger.info("")

    def configure_terminal_startup(self, disable_all: bool = False, keep_tasks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Configure terminal startup behavior"""
        self.logger.info("="*80)
        self.logger.info("CONFIGURING TERMINAL STARTUP")
        self.logger.info("="*80)

        auto_start_tasks = self.get_auto_start_tasks()

        if not auto_start_tasks:
            self.logger.info("ℹ️  No auto-start tasks to configure")
            return {"success": True, "message": "No auto-start tasks found"}

        if disable_all:
            self.logger.info("🔧 Disabling all auto-start tasks...")
            success = self.disable_auto_start()
            return {
                "success": success,
                "action": "disabled_all",
                "tasks_affected": len(auto_start_tasks)
            }

        if keep_tasks:
            self.logger.info(f"🔧 Keeping auto-start for: {', '.join(keep_tasks)}")
            self.logger.info("   Disabling others...")

            disabled_count = 0
            for task in auto_start_tasks:
                if task["label"] not in keep_tasks:
                    if self.disable_auto_start(task["label"]):
                        disabled_count += 1

            return {
                "success": True,
                "action": "selective_disable",
                "tasks_kept": keep_tasks,
                "tasks_disabled": disabled_count
            }

        # Default: disable all
        self.logger.info("🔧 Disabling all auto-start tasks (default)...")
        success = self.disable_auto_start()
        return {
            "success": success,
            "action": "disabled_all",
            "tasks_affected": len(auto_start_tasks)
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Manage Cursor IDE terminal startup")
        parser.add_argument("--list", action="store_true", help="List auto-start tasks")
        parser.add_argument("--disable", type=str, help="Disable auto-start for specific task")
        parser.add_argument("--disable-all", action="store_true", help="Disable all auto-start tasks")
        parser.add_argument("--enable", type=str, help="Enable auto-start for specific task")
        parser.add_argument("--keep", nargs="+", help="Keep auto-start for specific tasks (disable others)")
        parser.add_argument("--configure", action="store_true", help="Configure terminal startup (interactive)")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        manager = CursorTerminalManager(project_root)

        if args.list:
            manager.list_auto_start_tasks()
        elif args.disable:
            manager.disable_auto_start(args.disable)
        elif args.disable_all:
            manager.disable_auto_start()
        elif args.enable:
            manager.enable_auto_start(args.enable)
        elif args.keep:
            manager.configure_terminal_startup(keep_tasks=args.keep)
        elif args.configure:
            manager.list_auto_start_tasks()
            print("\nOptions:")
            print("1. Disable all auto-start tasks")
            print("2. Keep specific tasks (disable others)")
            choice = input("\nEnter choice (1 or 2): ").strip()

            if choice == "1":
                manager.configure_terminal_startup(disable_all=True)
            elif choice == "2":
                tasks = manager.get_auto_start_tasks()
                print("\nAvailable tasks:")
                for i, task in enumerate(tasks, 1):
                    print(f"{i}. {task['label']}")
                keep_input = input("\nEnter task numbers to keep (comma-separated): ").strip()
                keep_indices = [int(x.strip()) - 1 for x in keep_input.split(",") if x.strip().isdigit()]
                keep_tasks = [tasks[i]["label"] for i in keep_indices if 0 <= i < len(tasks)]
                if keep_tasks:
                    manager.configure_terminal_startup(keep_tasks=keep_tasks)
                else:
                    print("No valid tasks selected")
            else:
                print("Invalid choice")
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()