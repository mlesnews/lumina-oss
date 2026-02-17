#!/usr/bin/env python3
"""
JARVIS Autonomous Work Shift System

AI automatically begins work shifts, much as any human would.
Works continuously, assisting and mentoring the operator.
When operator is idle, AI works continuously.

Tags: #AUTONOMOUS_WORK #WORK_SHIFT #CONTINUOUS #MENTORING @JARVIS @LUMINA
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading

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

logger = get_logger("JARVISAutonomousWorkShift")

# Azure Service Bus integration
try:
    from jarvis_azure_ecosystem_integration import AzureEcosystemIntegration
    AZURE_ECOSYSTEM_AVAILABLE = True
except ImportError:
    AZURE_ECOSYSTEM_AVAILABLE = False
    logger.debug("Azure ecosystem integration not available")


class AutonomousWorkShift:
    """Autonomous work shift system - AI works like a human would"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "autonomous_work_shift"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.data_dir / "shift_state.json"
        self.work_log_file = self.data_dir / "work_log.jsonl"

        self.is_running = False
        self.shift_thread = None
        self.current_shift = None

        # Azure ecosystem integration
        self.azure_ecosystem = None
        if AZURE_ECOSYSTEM_AVAILABLE:
            try:
                self.azure_ecosystem = AzureEcosystemIntegration(project_root)
            except Exception as e:
                logger.debug(f"Azure ecosystem not available: {e}")

        self.load_state()

    def load_state(self):
        """Load shift state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.is_running = state.get("is_running", False)
                    self.current_shift = state.get("current_shift")
            except Exception as e:
                logger.error(f"Error loading shift state: {e}")
                self.is_running = False
                self.current_shift = None

    def save_state(self):
        """Save shift state"""
        try:
            state = {
                "is_running": self.is_running,
                "current_shift": self.current_shift,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving shift state: {e}")

    def log_work(self, action: str, details: Dict[str, Any] = None):
        """Log work activity"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "details": details or {}
            }
            with open(self.work_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error logging work: {e}")

    def start_shift(self) -> Dict[str, Any]:
        """Start a new work shift"""
        if self.is_running:
            logger.warning("Work shift already running")
            return {"success": False, "error": "Shift already running"}

        logger.info("=" * 80)
        logger.info("🚀 STARTING AUTONOMOUS WORK SHIFT")
        logger.info("=" * 80)

        shift_id = f"shift_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_shift = {
            "shift_id": shift_id,
            "started_at": datetime.now().isoformat(),
            "status": "active",
            "tasks_completed": 0,
            "tasks_failed": 0
        }

        self.is_running = True
        self.save_state()
        self.log_work("shift_started", {"shift_id": shift_id})

        # Send event to Azure Service Bus
        if self.azure_ecosystem:
            try:
                self.azure_ecosystem.send_work_shift_event("shift_started", {
                    "shift_id": shift_id,
                    "started_at": self.current_shift["started_at"]
                })
            except Exception as e:
                logger.debug(f"Could not send to Azure Service Bus: {e}")

        # Start shift thread
        self.shift_thread = threading.Thread(target=self._run_shift, daemon=True)
        self.shift_thread.start()

        logger.info(f"✅ Work shift {shift_id} started")
        return {
            "success": True,
            "shift_id": shift_id,
            "started_at": self.current_shift["started_at"]
        }

    def stop_shift(self) -> Dict[str, Any]:
        """Stop the current work shift"""
        if not self.is_running:
            logger.warning("No work shift running")
            return {"success": False, "error": "No shift running"}

        logger.info("🛑 Stopping work shift...")

        self.is_running = False

        if self.current_shift:
            self.current_shift["status"] = "stopped"
            self.current_shift["stopped_at"] = datetime.now().isoformat()
            self.log_work("shift_stopped", {"shift_id": self.current_shift["shift_id"]})

        self.save_state()
        logger.info("✅ Work shift stopped")

        return {"success": True, "shift_id": self.current_shift.get("shift_id") if self.current_shift else None}

    def _run_shift(self):
        """Run the work shift loop"""
        logger.info("🔄 Work shift loop started")

        while self.is_running:
            try:
                # Get work tasks
                tasks = self._get_work_tasks()

                if tasks:
                    logger.info(f"📋 Found {len(tasks)} work tasks")

                    for task in tasks:
                        if not self.is_running:
                            break

                        result = self._execute_task(task)

                        if result.get("success"):
                            self.current_shift["tasks_completed"] += 1
                            self.log_work("task_completed", {
                                "task_id": task.get("id"),
                                "result": result
                            })
                            # Send event to Azure Service Bus
                            if self.azure_ecosystem:
                                try:
                                    self.azure_ecosystem.send_work_shift_event("task_completed", {
                                        "task_id": task.get("id"),
                                        "task_type": task.get("type"),
                                        "shift_id": self.current_shift.get("shift_id")
                                    })
                                except Exception:
                                    pass
                        else:
                            self.current_shift["tasks_failed"] += 1
                            self.log_work("task_failed", {
                                "task_id": task.get("id"),
                                "error": result.get("error")
                            })
                            # Send event to Azure Service Bus
                            if self.azure_ecosystem:
                                try:
                                    self.azure_ecosystem.send_work_shift_event("task_failed", {
                                        "task_id": task.get("id"),
                                        "error": result.get("error"),
                                        "shift_id": self.current_shift.get("shift_id")
                                    })
                                except Exception:
                                    pass

                        self.save_state()

                        # Brief pause between tasks
                        time.sleep(1)
                else:
                    # No tasks available, check for continuous work
                    self._do_continuous_work()

                # Sleep before next iteration
                time.sleep(5)

            except Exception as e:
                logger.error(f"Error in work shift loop: {e}")
                time.sleep(10)

        logger.info("🔄 Work shift loop ended")

    def _get_work_tasks(self) -> List[Dict[str, Any]]:
        """Get work tasks from various sources"""
        tasks = []

        # Check for pending asks/requests
        asks_file = self.project_root / "data" / "session_tracking" / "asks.json"
        if asks_file.exists():
            try:
                with open(asks_file, 'r', encoding='utf-8') as f:
                    asks = json.load(f)
                    for ask in asks:
                        if ask.get("status") == "pending":
                            tasks.append({
                                "id": ask.get("ask_id"),
                                "type": "ask",
                                "priority": "high",
                                "description": ask.get("question"),
                                "data": ask
                            })
            except Exception as e:
                logger.debug(f"Error loading asks: {e}")

        # Check for pending changes
        changes_file = self.project_root / "data" / "session_tracking" / "pending_changes.json"
        if changes_file.exists():
            try:
                with open(changes_file, 'r', encoding='utf-8') as f:
                    changes = json.load(f)
                    for change in changes:
                        if change.get("status") == "pending":
                            tasks.append({
                                "id": f"change_{change.get('file_path', 'unknown')}",
                                "type": "change",
                                "priority": "medium",
                                "description": change.get("description"),
                                "data": change
                            })
            except Exception as e:
                logger.debug(f"Error loading changes: {e}")

        # Check master todos
        todos_file = self.project_root / "data" / "todo" / "master_todos.json"
        if todos_file.exists():
            try:
                with open(todos_file, 'r', encoding='utf-8') as f:
                    todos_data = json.load(f)
                    todos = todos_data.get("todos", [])
                    for todo in todos:
                        if todo.get("status") in ["pending", "in_progress"]:
                            tasks.append({
                                "id": todo.get("id"),
                                "type": "todo",
                                "priority": todo.get("priority", "medium"),
                                "description": todo.get("content"),
                                "data": todo
                            })
            except Exception as e:
                logger.debug(f"Error loading todos: {e}")

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        tasks.sort(key=lambda t: priority_order.get(t.get("priority", "medium"), 2))

        return tasks

    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a work task"""
        task_id = task.get("id")
        task_type = task.get("type")

        logger.info(f"⚙️  Executing task: {task_id} ({task_type})")

        try:
            if task_type == "ask":
                # Process ask
                return self._process_ask(task)
            elif task_type == "change":
                # Process change
                return self._process_change(task)
            elif task_type == "todo":
                # Process todo
                return self._process_todo(task)
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            return {"success": False, "error": str(e)}

    def _process_ask(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process an ask task"""
        # Placeholder - would integrate with ask processing system
        logger.info(f"   📝 Processing ask: {task.get('description', 'N/A')}")
        return {"success": True, "message": "Ask processed"}

    def _process_change(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a change task"""
        # Placeholder - would integrate with change acceptance system
        logger.info(f"   ✅ Processing change: {task.get('description', 'N/A')}")
        return {"success": True, "message": "Change processed"}

    def _process_todo(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a todo task"""
        # Placeholder - would integrate with todo system
        logger.info(f"   📋 Processing todo: {task.get('description', 'N/A')}")
        return {"success": True, "message": "Todo processed"}

    def _do_continuous_work(self):
        """Do continuous work when no specific tasks available"""
        # Continuous improvement tasks
        continuous_tasks = [
            {
                "name": "code_review",
                "description": "Review and improve code quality"
            },
            {
                "name": "documentation",
                "description": "Update and improve documentation"
            },
            {
                "name": "optimization",
                "description": "Optimize system performance"
            },
            {
                "name": "testing",
                "description": "Run tests and improve coverage"
            }
        ]

        # Select a continuous task (round-robin or random)
        # For now, just log that we're in continuous work mode
        logger.debug("🔄 Continuous work mode - no specific tasks")
        time.sleep(10)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Autonomous Work Shift")
    parser.add_argument("--start", action="store_true", help="Start work shift")
    parser.add_argument("--stop", action="store_true", help="Stop work shift")
    parser.add_argument("--status", action="store_true", help="Show shift status")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    shift = AutonomousWorkShift(project_root)

    if args.start:
        result = shift.start_shift()
        print(json.dumps(result, indent=2, default=str))

        if args.continuous:
            # Keep running
            try:
                while shift.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                shift.stop_shift()

    elif args.stop:
        result = shift.stop_shift()
        print(json.dumps(result, indent=2, default=str))

    elif args.status:
        status = {
            "is_running": shift.is_running,
            "current_shift": shift.current_shift
        }
        print(json.dumps(status, indent=2, default=str))

    else:
        # Default: show status
        status = {
            "is_running": shift.is_running,
            "current_shift": shift.current_shift
        }
        print(json.dumps(status, indent=2, default=str))


if __name__ == "__main__":


    main()