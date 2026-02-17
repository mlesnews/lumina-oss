#!/usr/bin/env python3
"""
Task Recurrence Pattern Analyzer

Examines tasks to identify recurrence patterns and automatically schedules them
on NAS Kron (cron) scheduler. Runs as daemons from NAS for entire environment.

IDE-style execution: No terminal needed, just type tasks being run.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Pattern
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import re
import json
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TaskRecurrenceAnalyzer")


class RecurrencePattern(Enum):
    """Recurrence pattern types"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM_INTERVAL = "custom_interval"
    ON_DEMAND = "on_demand"
    UNKNOWN = "unknown"


@dataclass
class TaskRecurrence:
    """Task recurrence information"""
    task_name: str
    pattern: RecurrencePattern
    schedule: Dict[str, Any]
    cron_expression: str
    confidence: float  # 0.0 to 1.0
    detected_from: str  # How pattern was detected
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskRecurrenceAnalyzer:
    """
    Analyzes tasks for recurrence patterns and generates NAS Kron schedules

    Features:
    - Pattern detection from task definitions
    - Automatic cron expression generation
    - NAS Kron deployment
    - Daemon execution
    - IDE-style task execution
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("TaskRecurrenceAnalyzer")

        self.data_dir = self.project_root / "data" / "tasks" / "recurrence"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tasks: List[Dict[str, Any]] = []
        self.recurrences: List[TaskRecurrence] = []

        # Pattern detection rules
        self.pattern_rules = {
            RecurrencePattern.HOURLY: [
                r"hourly",
                r"every\s+hour",
                r"each\s+hour",
                r"interval.*?3600",
                r"schedule.*?type.*?hourly"
            ],
            RecurrencePattern.DAILY: [
                r"daily",
                r"every\s+day",
                r"each\s+day",
                r"schedule.*?type.*?daily",
                r"time.*?\d{2}:\d{2}"  # Time pattern like "00:00"
            ],
            RecurrencePattern.WEEKLY: [
                r"weekly",
                r"every\s+week",
                r"each\s+week",
                r"schedule.*?type.*?weekly",
                r"day.*?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
            ],
            RecurrencePattern.MONTHLY: [
                r"monthly",
                r"every\s+month",
                r"each\s+month",
                r"schedule.*?type.*?monthly",
                r"day.*?\d{1,2}"  # Day of month
            ]
        }

        self.logger.info("🔍 Task Recurrence Analyzer initialized")

    def load_tasks(self, tasks_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Load tasks from configuration file"""
        if tasks_file is None:
            tasks_file = self.project_root / "config" / "lumina_scheduled_tasks.json"

        if not tasks_file.exists():
            self.logger.warning(f"Tasks file not found: {tasks_file}")
            return []

        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Combine regular tasks and monthly tasks
            all_tasks = data.get("tasks", []) + data.get("monthly_tasks", [])
            self.tasks = all_tasks

            self.logger.info(f"✅ Loaded {len(self.tasks)} tasks from {tasks_file}")
            return all_tasks
        except Exception as e:
            self.logger.error(f"❌ Error loading tasks: {e}")
            return []

    def analyze_task(self, task: Dict[str, Any]) -> TaskRecurrence:
        """Analyze a single task for recurrence pattern"""
        task_name = task.get("name", "unknown")
        schedule = task.get("schedule", {})
        description = task.get("description", "").lower()

        # Combine all text for pattern matching
        search_text = f"{description} {json.dumps(schedule).lower()}"

        # Detect pattern
        pattern = RecurrencePattern.UNKNOWN
        confidence = 0.0
        detected_from = "unknown"
        cron_expression = ""

        # Check each pattern type
        for pattern_type, rules in self.pattern_rules.items():
            for rule in rules:
                if re.search(rule, search_text, re.IGNORECASE):
                    pattern = pattern_type
                    confidence = 0.9
                    detected_from = f"pattern_match: {rule}"
                    break
            if pattern != RecurrencePattern.UNKNOWN:
                break

        # Check schedule type directly
        schedule_type = schedule.get("type", "").lower()
        if schedule_type:
            try:
                pattern = RecurrencePattern(schedule_type)
                confidence = 1.0
                detected_from = "schedule.type"
            except ValueError:
                pass

        # Generate cron expression
        cron_expression = self._generate_cron_expression(task, pattern, schedule)

        # Check interval-based patterns
        if "interval" in task:
            interval = task.get("interval")
            if isinstance(interval, int):
                pattern = RecurrencePattern.CUSTOM_INTERVAL
                confidence = 0.95
                detected_from = "interval_seconds"
                cron_expression = self._interval_to_cron(interval)

        recurrence = TaskRecurrence(
            task_name=task_name,
            pattern=pattern,
            schedule=schedule,
            cron_expression=cron_expression,
            confidence=confidence,
            detected_from=detected_from,
            metadata={
                "script": task.get("script", ""),
                "arguments": task.get("arguments", []),
                "enabled": task.get("enabled", True),
                "priority": task.get("priority", 0)
            }
        )

        return recurrence

    def _generate_cron_expression(self, task: Dict[str, Any], pattern: RecurrencePattern, schedule: Dict[str, Any]) -> str:
        """Generate cron expression from task and pattern"""
        # Default: daily at midnight
        default_cron = "0 0 * * *"

        if pattern == RecurrencePattern.HOURLY:
            # Every hour at minute 0
            return "0 * * * *"

        elif pattern == RecurrencePattern.DAILY:
            time_str = schedule.get("time", "00:00")
            hour, minute = self._parse_time(time_str)
            return f"{minute} {hour} * * *"

        elif pattern == RecurrencePattern.WEEKLY:
            day = schedule.get("day", "Monday")
            time_str = schedule.get("time", "00:00")
            hour, minute = self._parse_time(time_str)
            day_num = self._day_name_to_cron(day)
            return f"{minute} {hour} * * {day_num}"

        elif pattern == RecurrencePattern.MONTHLY:
            day = schedule.get("day", 1)
            time_str = schedule.get("time", "00:00")
            hour, minute = self._parse_time(time_str)
            # Handle negative day (last day of month)
            if isinstance(day, int) and day < 0:
                # Use a workaround: run on 28th (safe for all months)
                day = 28
            return f"{minute} {hour} {day} * *"

        elif pattern == RecurrencePattern.CUSTOM_INTERVAL:
            interval = task.get("interval", 3600)
            return self._interval_to_cron(interval)

        return default_cron

    def _parse_time(self, time_str: str) -> tuple:
        """Parse time string (HH:MM) to (hour, minute)"""
        try:
            parts = time_str.split(":")
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            return hour, minute
        except:
            return 0, 0

    def _day_name_to_cron(self, day_name: str) -> int:
        """Convert day name to cron day number (0=Sunday, 1=Monday, etc.)"""
        days = {
            "sunday": 0, "sun": 0,
            "monday": 1, "mon": 1,
            "tuesday": 2, "tue": 2, "tues": 2,
            "wednesday": 3, "wed": 3,
            "thursday": 4, "thu": 4, "thur": 4, "thurs": 4,
            "friday": 5, "fri": 5,
            "saturday": 6, "sat": 6
        }
        return days.get(day_name.lower(), 1)  # Default to Monday

    def _interval_to_cron(self, interval_seconds: int) -> str:
        """Convert interval in seconds to cron expression"""
        if interval_seconds < 60:
            # Less than a minute - run every minute
            return "* * * * *"
        elif interval_seconds < 3600:
            # Less than an hour - run every N minutes
            minutes = interval_seconds // 60
            return f"*/{minutes} * * * *"
        elif interval_seconds < 86400:
            # Less than a day - run every N hours
            hours = interval_seconds // 3600
            return f"0 */{hours} * * *"
        else:
            # Daily or more
            days = interval_seconds // 86400
            return f"0 0 */{days} * *"

    def analyze_all_tasks(self) -> List[TaskRecurrence]:
        """Analyze all loaded tasks for recurrence patterns"""
        self.logger.info(f"🔍 Analyzing {len(self.tasks)} tasks for recurrence patterns...")

        self.recurrences = []
        for task in self.tasks:
            if task.get("enabled", True):
                recurrence = self.analyze_task(task)
                self.recurrences.append(recurrence)
                self.logger.info(f"  ✅ {recurrence.task_name}: {recurrence.pattern.value} ({recurrence.confidence:.0%})")

        self.logger.info(f"✅ Analyzed {len(self.recurrences)} recurring tasks")

        return self.recurrences

    def generate_nas_cron_file(self, output_file: Optional[Path] = None) -> Path:
        try:
            """Generate NAS cron file from analyzed recurrences"""
            if output_file is None:
                output_file = self.data_dir / "nas_crontab"

            self.logger.info(f"📝 Generating NAS cron file: {output_file}")

            cron_lines = [
                "# LUMINA Recurring Tasks - Auto-generated by Task Recurrence Analyzer",
                f"# Generated: {datetime.now().isoformat()}",
                "#",
                "# Environment: Entire LUMINA environment",
                "# Execution: Daemon mode (no terminal)",
                "#",
                ""
            ]

            for recurrence in self.recurrences:
                if recurrence.pattern != RecurrencePattern.UNKNOWN and recurrence.pattern != RecurrencePattern.ON_DEMAND:
                    # Build command
                    script_path = recurrence.metadata.get("script", "")
                    args = recurrence.metadata.get("arguments", [])

                    # Convert Windows path to NAS path if needed
                    nas_script_path = self._convert_to_nas_path(script_path)

                    # Build full command
                    command_parts = ["python3", nas_script_path]
                    command_parts.extend([str(arg) for arg in args])
                    command = " ".join(command_parts)

                    # Add logging
                    log_file = f"/volume1/docker/jarvis/.lumina/logs/cron_{recurrence.task_name}.log"
                    command_with_log = f"{command} >> {log_file} 2>&1"

                    # Create cron entry
                    cron_lines.append(f"# {recurrence.task_name}")
                    cron_lines.append(f"# Pattern: {recurrence.pattern.value} (confidence: {recurrence.confidence:.0%})")
                    cron_lines.append(f"# Detected from: {recurrence.detected_from}")
                    cron_lines.append(f"{recurrence.cron_expression} {command_with_log}")
                    cron_lines.append("")

            # Write file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(cron_lines))

            self.logger.info(f"✅ Generated NAS cron file: {output_file} ({len(cron_lines)} lines)")

            return output_file

        except Exception as e:
            self.logger.error(f"Error in generate_nas_cron_file: {e}", exc_info=True)
            raise
    def _convert_to_nas_path(self, windows_path: str) -> str:
        """Convert Windows path to NAS path"""
        # Example: scripts/python/script.py -> /volume1/docker/jarvis/.lumina/scripts/python/script.py
        if windows_path.startswith("scripts/"):
            return f"/volume1/docker/jarvis/.lumina/{windows_path}"
        elif "\\" in windows_path:
            # Windows path - convert to Unix
            unix_path = windows_path.replace("\\", "/")
            if unix_path.startswith("scripts/"):
                return f"/volume1/docker/jarvis/.lumina/{unix_path}"
        return windows_path

    def get_recurrence_summary(self) -> Dict[str, Any]:
        """Get summary of recurrence patterns"""
        summary = {
            "total_tasks": len(self.tasks),
            "recurring_tasks": len(self.recurrences),
            "by_pattern": {},
            "by_confidence": {
                "high": 0,  # >= 0.8
                "medium": 0,  # 0.5-0.79
                "low": 0  # < 0.5
            }
        }

        for recurrence in self.recurrences:
            pattern = recurrence.pattern.value
            summary["by_pattern"][pattern] = summary["by_pattern"].get(pattern, 0) + 1

            if recurrence.confidence >= 0.8:
                summary["by_confidence"]["high"] += 1
            elif recurrence.confidence >= 0.5:
                summary["by_confidence"]["medium"] += 1
            else:
                summary["by_confidence"]["low"] += 1

        return summary


def main():
    try:
        """CLI for task recurrence analyzer"""
        import argparse

        parser = argparse.ArgumentParser(description="Task Recurrence Pattern Analyzer")
        parser.add_argument("--analyze", action="store_true", help="Analyze tasks for recurrence patterns")
        parser.add_argument("--generate-cron", action="store_true", help="Generate NAS cron file")
        parser.add_argument("--summary", action="store_true", help="Show recurrence summary")
        parser.add_argument("--tasks-file", help="Path to tasks JSON file")

        args = parser.parse_args()

        analyzer = TaskRecurrenceAnalyzer()

        # Load tasks
        tasks_file = Path(args.tasks_file) if args.tasks_file else None
        analyzer.load_tasks(tasks_file)

        if args.analyze or args.generate_cron or args.summary:
            # Analyze tasks
            recurrences = analyzer.analyze_all_tasks()

            if args.summary:
                summary = analyzer.get_recurrence_summary()
                print(f"\n📊 Recurrence Pattern Summary:")
                print(f"  Total Tasks: {summary['total_tasks']}")
                print(f"  Recurring Tasks: {summary['recurring_tasks']}")
                print(f"\n  By Pattern:")
                for pattern, count in summary["by_pattern"].items():
                    print(f"    {pattern}: {count}")
                print(f"\n  By Confidence:")
                print(f"    High (>=80%): {summary['by_confidence']['high']}")
                print(f"    Medium (50-79%): {summary['by_confidence']['medium']}")
                print(f"    Low (<50%): {summary['by_confidence']['low']}")

            if args.generate_cron:
                cron_file = analyzer.generate_nas_cron_file()
                print(f"\n✅ NAS cron file generated: {cron_file}")
                print(f"   Tasks scheduled: {len(recurrences)}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()