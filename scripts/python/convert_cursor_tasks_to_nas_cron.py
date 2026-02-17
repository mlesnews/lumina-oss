#!/usr/bin/env python3
"""
Convert Cursor IDE Tasks to NAS Cron Scheduler Tasks
Converts tasks.json to Synology NAS cron format for automated execution
#JARVIS #MANUS #NAS #CRON #SCHEDULER #AUTOMATION
"""

import sys
import json
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

logger = get_logger("CursorTasksToNAS")


class CursorTasksToNASCron:
    """
    Convert Cursor IDE tasks to NAS cron scheduler tasks
    """

    # Task scheduling defaults
    DEFAULT_SCHEDULES = {
        "JARVIS: Auto Git Commit": "0 */6 * * *",  # Every 6 hours
        "JARVIS: Health Check": "0 */2 * * *",  # Every 2 hours
        "JARVIS: Cursor IDE Optimization": "0 0 * * 0",  # Weekly on Sunday
        "JARVIS: Monitor IDE Notifications": "*/15 * * * *",  # Every 15 minutes
        "MANUS: Quick Screenshot": None,  # Manual only
        "MANUS: Capture Screenshot with Context": None,  # Manual only
        "MANUS: Capture Screenshot": None,  # Manual only
        "LDAP: Troubleshoot Authentication": None,  # Manual only
        "SSO: Verify Readiness": "0 8 * * *",  # Daily at 8 AM
        "SSO: Setup SAML": None,  # Manual only
    }

    # Tasks that should NOT be scheduled (manual only)
    MANUAL_ONLY_TASKS = [
        "MANUS: Quick Screenshot",
        "MANUS: Capture Screenshot with Context",
        "MANUS: Capture Screenshot",
        "LDAP: Troubleshoot Authentication",
        "SSO: Setup SAML",
    ]

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tasks_file = project_root / ".cursor" / "tasks.json"
        self.output_dir = project_root / "scripts" / "nas" / "cron"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_cursor_tasks(self) -> Dict[str, Any]:
        """Load tasks from Cursor tasks.json"""
        if not self.tasks_file.exists():
            logger.error(f"Tasks file not found: {self.tasks_file}")
            return {"tasks": []}

        try:
            with open(self.tasks_file) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            return {"tasks": []}

    def convert_task_to_cron(self, task: Dict[str, Any], schedule: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Convert a Cursor task to NAS cron format

        Args:
            task: Cursor task definition
            schedule: Cron schedule (minute hour day month weekday)

        Returns:
            NAS cron task definition or None if manual-only
        """
        task_label = task.get("label", "")

        # Skip manual-only tasks
        if task_label in self.MANUAL_ONLY_TASKS:
            logger.debug(f"Skipping manual-only task: {task_label}")
            return None

        # Get schedule
        if not schedule:
            schedule = self.DEFAULT_SCHEDULES.get(task_label)

        if not schedule:
            logger.debug(f"No schedule defined for task: {task_label}")
            return None

        # Extract command and args
        command = task.get("command", "python")
        args = task.get("args", [])

        # Convert workspaceFolder paths
        script_path = None
        for arg in args:
            if isinstance(arg, str):
                # Handle ${workspaceFolder} paths
                if "${workspaceFolder}" in arg:
                    # Convert to NAS path
                    nas_path = arg.replace("${workspaceFolder}", "/volume1/lumina")
                    if nas_path.endswith(".py"):
                        script_path = nas_path
                        break
                # Handle relative paths (from scripts/python/)
                elif arg.endswith(".py") and not arg.startswith("/"):
                    # Convert relative path to NAS absolute path
                    nas_path = f"/volume1/lumina/{arg}"
                    script_path = nas_path
                    break
                # Handle absolute paths (already full path)
                elif arg.endswith(".py") and arg.startswith("/"):
                    # Already absolute, just use it
                    script_path = arg
                    break

        if not script_path:
            logger.warning(f"Could not find script path for task: {task_label}")
            return None

        # Build command
        full_command = f"{command} {script_path}"

        # Add additional args (excluding script path)
        additional_args = []
        script_found = False
        for arg in args:
            if isinstance(arg, str):
                # Skip script path (already in full_command)
                if (arg.endswith(".py") and 
                    (script_path.endswith(arg) or arg in script_path or script_path.endswith(arg.replace("${workspaceFolder}", "")))):
                    script_found = True
                    continue
                elif "${workspaceFolder}" in arg and arg.endswith(".py"):
                    script_found = True
                    continue  # Skip script path
                elif "${input:" in arg:
                    # Skip input prompts for cron (use defaults or remove)
                    continue
                else:
                    additional_args.append(arg)
            else:
                additional_args.append(str(arg))

        if additional_args:
            full_command += " " + " ".join(additional_args)

        # Create NAS cron task
        cron_task = {
            "name": task_label,
            "schedule": schedule,
            "command": full_command,
            "enabled": True,
            "description": f"Auto-generated from Cursor task: {task_label}",
            "created": datetime.now().isoformat(),
            "source": "cursor_tasks.json"
        }

        return cron_task

    def generate_cron_file(self, cron_tasks: List[Dict[str, Any]]) -> Path:
        try:
            """
            Generate NAS cron configuration file

            Args:
                cron_tasks: List of cron task definitions

            Returns:
                Path to generated cron file
            """
            output_file = self.output_dir / "cursor_tasks_cron.json"

            cron_config = {
                "version": "1.0.0",
                "source": "Cursor IDE tasks.json",
                "generated": datetime.now().isoformat(),
                "tasks": cron_tasks
            }

            with open(output_file, "w") as f:
                json.dump(cron_config, f, indent=2)

            logger.info(f"✅ Generated cron config: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error in generate_cron_file: {e}", exc_info=True)
            raise
    def generate_crontab_format(self, cron_tasks: List[Dict[str, Any]]) -> Path:
        try:
            """
            Generate standard crontab format file

            Args:
                cron_tasks: List of cron task definitions

            Returns:
                Path to generated crontab file
            """
            output_file = self.output_dir / "cursor_tasks_crontab.txt"

            lines = [
                "# Cursor IDE Tasks - Converted to NAS Cron",
                f"# Generated: {datetime.now().isoformat()}",
                "# Source: .cursor/tasks.json",
                "",
            ]

            for task in cron_tasks:
                schedule = task["schedule"]
                command = task["command"]
                name = task["name"]

                lines.append(f"# {name}")
                lines.append(f"{schedule} {command}")
                lines.append("")

            with open(output_file, "w") as f:
                f.write("\n".join(lines))

            logger.info(f"✅ Generated crontab file: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error in generate_crontab_format: {e}", exc_info=True)
            raise
    def generate_dsm_scheduler_script(self, cron_tasks: List[Dict[str, Any]]) -> Path:
        try:
            """
            Generate DSM Task Scheduler script (for manual import)

            Args:
                cron_tasks: List of cron task definitions

            Returns:
                Path to generated DSM script
            """
            output_file = self.output_dir / "dsm_scheduler_import.sh"

            lines = [
                "#!/bin/bash",
                "# DSM Task Scheduler Import Script",
                f"# Generated: {datetime.now().isoformat()}",
                "# Source: Cursor IDE tasks.json",
                "",
                "# This script can be used to import tasks into DSM Task Scheduler",
                "# Run on NAS via SSH or DSM Control Panel",
                "",
            ]

            for task in cron_tasks:
                name = task["name"]
                schedule = task["schedule"]
                command = task["command"]

                # Escape special characters for shell
                name_escaped = name.replace('"', '\\"')
                command_escaped = command.replace('"', '\\"')

                lines.append(f"# Task: {name}")
                lines.append(f"# Schedule: {schedule}")
                lines.append(f"# Command: {command}")
                lines.append(f'echo "Adding task: {name_escaped}"')
                lines.append("")

            lines.append("echo 'Done importing tasks'")

            with open(output_file, "w") as f:
                f.write("\n".join(lines))

            # Make executable
            output_file.chmod(0o755)

            logger.info(f"✅ Generated DSM script: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error in generate_dsm_scheduler_script: {e}", exc_info=True)
            raise
    def convert_all(self, custom_schedules: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Convert all Cursor tasks to NAS cron format

        Args:
            custom_schedules: Optional custom schedules for specific tasks

        Returns:
            Dict with conversion results
        """
        logger.info("🔄 Converting Cursor tasks to NAS cron format...")

        # Load tasks
        tasks_data = self.load_cursor_tasks()
        tasks = tasks_data.get("tasks", [])

        logger.info(f"Found {len(tasks)} tasks to convert")

        # Override schedules if provided
        if custom_schedules:
            self.DEFAULT_SCHEDULES.update(custom_schedules)

        # Convert tasks
        cron_tasks = []
        skipped = []

        for task in tasks:
            task_label = task.get("label", "")
            schedule = custom_schedules.get(task_label) if custom_schedules else None

            cron_task = self.convert_task_to_cron(task, schedule)

            if cron_task:
                cron_tasks.append(cron_task)
                logger.info(f"✅ Converted: {task_label}")
            else:
                skipped.append(task_label)
                logger.debug(f"⏭️  Skipped: {task_label}")

        # Generate output files
        json_file = self.generate_cron_file(cron_tasks)
        crontab_file = self.generate_crontab_format(cron_tasks)
        dsm_script = self.generate_dsm_scheduler_script(cron_tasks)

        result = {
            "converted": len(cron_tasks),
            "skipped": len(skipped),
            "total": len(tasks),
            "output_files": {
                "json": str(json_file),
                "crontab": str(crontab_file),
                "dsm_script": str(dsm_script)
            },
            "cron_tasks": cron_tasks,
            "skipped_tasks": skipped
        }

        logger.info(f"✅ Conversion complete: {len(cron_tasks)} tasks converted, {len(skipped)} skipped")

        return result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Convert Cursor tasks to NAS cron")
    parser.add_argument("--custom-schedule", nargs=2, metavar=("TASK", "SCHEDULE"),
                       action="append", help="Custom schedule for task (e.g., 'JARVIS: Health Check' '0 */2 * * *')")
    parser.add_argument("--list", action="store_true", help="List available tasks")
    args = parser.parse_args()

    converter = CursorTasksToNASCron(project_root)

    if args.list:
        tasks_data = converter.load_cursor_tasks()
        tasks = tasks_data.get("tasks", [])

        print("=" * 70)
        print("   AVAILABLE CURSOR TASKS")
        print("=" * 70)
        print("")

        for task in tasks:
            label = task.get("label", "Unknown")
            schedule = converter.DEFAULT_SCHEDULES.get(label, "Not scheduled")
            manual = " (Manual Only)" if label in converter.MANUAL_ONLY_TASKS else ""

            print(f"  {label}")
            print(f"    Schedule: {schedule}{manual}")
            print("")

        return 0

    # Parse custom schedules
    custom_schedules = {}
    if args.custom_schedule:
        for task, schedule in args.custom_schedule:
            custom_schedules[task] = schedule

    # Convert
    result = converter.convert_all(custom_schedules)

    print("=" * 70)
    print("   CURSOR TASKS → NAS CRON CONVERSION")
    print("=" * 70)
    print("")
    print(f"✅ Converted: {result['converted']} tasks")
    print(f"⏭️  Skipped: {result['skipped']} tasks (manual only)")
    print(f"📊 Total: {result['total']} tasks")
    print("")
    print("Generated Files:")
    print(f"  JSON Config: {result['output_files']['json']}")
    print(f"  Crontab: {result['output_files']['crontab']}")
    print(f"  DSM Script: {result['output_files']['dsm_script']}")
    print("")
    print("=" * 70)
    print("")
    print("Next Steps:")
    print("  1. Review generated cron files")
    print("  2. Copy crontab.txt to NAS and add to crontab")
    print("  3. Or use DSM Task Scheduler to import tasks")
    print("")

    return 0


if __name__ == "__main__":


    sys.exit(main())