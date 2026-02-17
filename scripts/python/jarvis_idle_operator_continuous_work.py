#!/usr/bin/env python3
"""
JARVIS Idle Operator Continuous Work System

Monitors operator activity and when operator is idle, AI works continuously.
Works side by side, assisting and mentoring the operator.

Tags: #IDLE_MONITOR #CONTINUOUS_WORK #OPERATOR_MONITORING #MENTORING @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISIdleOperator")


class IdleOperatorMonitor:
    """Monitor operator activity and enable continuous work when idle"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "idle_operator_monitor"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.data_dir / "monitor_state.json"
        self.activity_log_file = self.data_dir / "activity_log.jsonl"

        self.is_monitoring = False
        self.monitor_thread = None
        self.operator_idle = False
        self.idle_since = None
        self.idle_threshold_seconds = 300  # 5 minutes
        self.last_activity = datetime.now()

        # Continuous work system
        self.continuous_work_active = False
        self.work_thread = None

        self.load_state()

    def load_state(self):
        """Load monitor state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.is_monitoring = state.get("is_monitoring", False)
                    self.operator_idle = state.get("operator_idle", False)
                    self.idle_since = state.get("idle_since")
                    if self.idle_since:
                        self.idle_since = datetime.fromisoformat(self.idle_since)
            except Exception as e:
                logger.error(f"Error loading monitor state: {e}")

    def save_state(self):
        """Save monitor state"""
        try:
            state = {
                "is_monitoring": self.is_monitoring,
                "operator_idle": self.operator_idle,
                "idle_since": self.idle_since.isoformat() if self.idle_since else None,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving monitor state: {e}")

    def log_activity(self, activity_type: str, details: Dict[str, Any] = None):
        """Log operator activity"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "activity_type": activity_type,
                "details": details or {}
            }
            with open(self.activity_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')

            self.last_activity = datetime.now()
        except Exception as e:
            logger.error(f"Error logging activity: {e}")

    def detect_activity(self) -> bool:
        """Detect operator activity"""
        # Multiple detection methods

        # Method 1: Check for recent file modifications
        recent_files = self._check_recent_file_modifications()
        if recent_files:
            return True

        # Method 2: Check for keyboard/mouse activity (platform-specific)
        # This would require platform-specific libraries
        # For now, we'll use file-based detection

        # Method 3: Check for active processes (IDE, browser, etc.)
        active_processes = self._check_active_processes()
        if active_processes:
            return True

        return False

    def _check_recent_file_modifications(self) -> bool:
        """Check for recent file modifications in project"""
        try:
            now = datetime.now()
            scripts_dir = self.project_root / "scripts"

            if scripts_dir.exists():
                for py_file in scripts_dir.rglob("*.py"):
                    try:
                        stat = py_file.stat()
                        mod_time = datetime.fromtimestamp(stat.st_mtime)
                        if (now - mod_time).total_seconds() < self.idle_threshold_seconds:
                            return True
                    except Exception:
                        continue
        except Exception as e:
            logger.debug(f"Error checking file modifications: {e}")

        return False

    def _check_active_processes(self) -> bool:
        """Check for active processes (IDE, browser, etc.)"""
        # Placeholder - would use psutil or similar
        # For now, assume active if monitoring is enabled
        return True

    def start_monitoring(self) -> Dict[str, Any]:
        """Start monitoring operator activity"""
        if self.is_monitoring:
            logger.warning("Already monitoring")
            return {"success": False, "error": "Already monitoring"}

        logger.info("=" * 80)
        logger.info("👁️  STARTING IDLE OPERATOR MONITOR")
        logger.info("=" * 80)

        self.is_monitoring = True
        self.save_state()
        self.log_activity("monitoring_started")

        # Start monitor thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("✅ Idle operator monitor started")
        return {"success": True, "started_at": datetime.now().isoformat()}

    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring operator activity"""
        if not self.is_monitoring:
            logger.warning("Not monitoring")
            return {"success": False, "error": "Not monitoring"}

        logger.info("🛑 Stopping idle operator monitor...")

        self.is_monitoring = False
        self.operator_idle = False
        self._stop_continuous_work()

        self.save_state()
        self.log_activity("monitoring_stopped")

        logger.info("✅ Idle operator monitor stopped")
        return {"success": True}

    def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🔄 Monitoring loop started")

        while self.is_monitoring:
            try:
                # Detect activity
                is_active = self.detect_activity()

                if is_active:
                    # Operator is active
                    if self.operator_idle:
                        logger.info("👤 Operator active - stopping continuous work")
                        self.operator_idle = False
                        self.idle_since = None
                        self._stop_continuous_work()
                        self.log_activity("operator_active")

                    self.last_activity = datetime.now()
                else:
                    # Operator appears idle
                    if not self.operator_idle:
                        # Check if idle threshold reached
                        idle_duration = (datetime.now() - self.last_activity).total_seconds()
                        if idle_duration >= self.idle_threshold_seconds:
                            logger.info(f"😴 Operator idle ({idle_duration:.0f}s) - starting continuous work")
                            self.operator_idle = True
                            self.idle_since = datetime.now()
                            self._start_continuous_work()
                            self.log_activity("operator_idle", {"idle_duration": idle_duration})

                self.save_state()

                # Check every 30 seconds
                time.sleep(30)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)

        logger.info("🔄 Monitoring loop ended")

    def _start_continuous_work(self):
        """Start continuous work when operator is idle"""
        if self.continuous_work_active:
            return

        logger.info("🚀 Starting continuous work (operator idle)")

        self.continuous_work_active = True

        # Start continuous work thread
        self.work_thread = threading.Thread(target=self._continuous_work_loop, daemon=True)
        self.work_thread.start()

        self.log_activity("continuous_work_started")

    def _stop_continuous_work(self):
        """Stop continuous work"""
        if not self.continuous_work_active:
            return

        logger.info("🛑 Stopping continuous work")

        self.continuous_work_active = False
        self.log_activity("continuous_work_stopped")

    def _continuous_work_loop(self):
        """Continuous work loop - AI works when operator is idle"""
        logger.info("⚙️  Continuous work loop started")

        while self.continuous_work_active and self.operator_idle:
            try:
                # Get work tasks
                tasks = self._get_continuous_work_tasks()

                if tasks:
                    logger.info(f"📋 Processing {len(tasks)} continuous work tasks")

                    for task in tasks:
                        if not self.continuous_work_active or not self.operator_idle:
                            break

                        result = self._execute_continuous_task(task)
                        self.log_activity("continuous_task_executed", {
                            "task": task.get("name"),
                            "result": result
                        })

                        time.sleep(2)
                else:
                    # No specific tasks - do background work
                    self._do_background_work()

                # Sleep before next iteration
                time.sleep(10)

            except Exception as e:
                logger.error(f"Error in continuous work loop: {e}")
                time.sleep(30)

        logger.info("⚙️  Continuous work loop ended")

    def _get_continuous_work_tasks(self) -> List[Dict[str, Any]]:
        """Get continuous work tasks"""
        tasks = []

        # Code quality improvements
        tasks.append({
            "name": "code_quality_review",
            "description": "Review and improve code quality",
            "priority": "medium"
        })

        # Documentation updates
        tasks.append({
            "name": "documentation_update",
            "description": "Update and improve documentation",
            "priority": "low"
        })

        # System optimization
        tasks.append({
            "name": "system_optimization",
            "description": "Optimize system performance",
            "priority": "medium"
        })

        return tasks

    def _execute_continuous_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a continuous work task"""
        task_name = task.get("name")
        logger.info(f"   ⚙️  Executing: {task_name}")

        # Placeholder - would integrate with actual task execution
        return {"success": True, "task": task_name}

    def _do_background_work(self):
        """Do background work when no specific tasks"""
        logger.debug("🔄 Background work mode")
        time.sleep(30)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Idle Operator Continuous Work")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--status", action="store_true", help="Show status")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    monitor = IdleOperatorMonitor(project_root)

    if args.start:
        result = monitor.start_monitoring()
        print(json.dumps(result, indent=2, default=str))

        # Keep running
        try:
            while monitor.is_monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()

    elif args.stop:
        result = monitor.stop_monitoring()
        print(json.dumps(result, indent=2, default=str))

    elif args.status:
        status = {
            "is_monitoring": monitor.is_monitoring,
            "operator_idle": monitor.operator_idle,
            "idle_since": monitor.idle_since.isoformat() if monitor.idle_since else None,
            "continuous_work_active": monitor.continuous_work_active,
            "last_activity": monitor.last_activity.isoformat()
        }
        print(json.dumps(status, indent=2, default=str))

    else:
        # Default: show status
        status = {
            "is_monitoring": monitor.is_monitoring,
            "operator_idle": monitor.operator_idle,
            "idle_since": monitor.idle_since.isoformat() if monitor.idle_since else None,
            "continuous_work_active": monitor.continuous_work_active
        }
        print(json.dumps(status, indent=2, default=str))


if __name__ == "__main__":


    main()