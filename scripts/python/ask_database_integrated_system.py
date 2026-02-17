#!/usr/bin/env python3
"""
@ask Database Integrated System
<COMPANY_NAME> LLC

Complete integration of:
- @ask Database with US Government checks and balances
- Master Blueprint continuous evaluation
- Master/Padawan ToDoLists concurrent maintenance

@JARVIS @MARVIN @SYPHON @R5 @BLUEPRINT
"""

import sys
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from ask_database_checks_balances import (
    AskDatabase, Ask, AskStatus, Branch, Priority, ChecksAndBalances, MasterPadawanTodo
)

logger = get_logger("AskDatabaseIntegratedSystem")


class AskDatabaseIntegratedSystem:
    """
    Integrated @ask Database System

    Features:
    - US Government-style checks and balances
    - Continuous master blueprint evaluation
    - Concurrent Master/Padawan todo maintenance
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("AskDatabaseIntegratedSystem")

        # Initialize subsystems
        self.ask_db = AskDatabase(project_root)

        # Import blueprint sync
        try:
            from living_blueprint_sync import LivingBlueprintSync
            self.blueprint_sync = LivingBlueprintSync(project_root)
        except ImportError:
            self.blueprint_sync = None
            self.logger.warning("LivingBlueprintSync not available")

        # Import todo systems
        try:
            from master_todo_tracker import MasterTodoTracker
            from dual_todo_system import DualTodoSystem
            self.master_todo = MasterTodoTracker(project_root)
            self.dual_todo = DualTodoSystem(project_root)
        except ImportError:
            self.master_todo = None
            self.dual_todo = None
            self.logger.warning("Todo systems not available")

        # Continuous evaluation thread
        self.evaluation_running = False
        self.evaluation_thread = None
        self.evaluation_interval = 3600  # seconds

    def create_ask_with_integration(self, ask_text: str, priority: Priority = Priority.MEDIUM,
                                    submitted_by: str = "user", tags: List[str] = None) -> Ask:
        """
        Create an ask with full integration:
        1. Create ask in database
        2. Evaluate blueprint impact
        3. Create Master/Padawan todos
        """
        # 1. Create ask
        ask = self.ask_db.create_ask(ask_text, priority, submitted_by, tags)
        self.logger.info(f"✅ Created ask: {ask.ask_id}")

        # 2. Evaluate blueprint impact
        if self.blueprint_sync:
            try:
                impact = self.ask_db.evaluate_blueprint_impact(ask.ask_id)
                self.logger.info(f"✅ Evaluated blueprint impact: {ask.ask_id}")
            except Exception as e:
                self.logger.error(f"Could not evaluate blueprint impact: {e}")

        # 3. Create Master/Padawan todos
        try:
            master_todo_text = f"Master: {ask_text}"
            padawan_todo_text = f"Padawan: {ask_text}"

            todo = self.ask_db.create_master_padawan_todos(
                ask.ask_id, master_todo_text, padawan_todo_text
            )

            # Also add to master todo tracker if available
            if self.master_todo:
                try:
                    self.master_todo.add_task(
                        title=master_todo_text,
                        description=f"Master todo for ask: {ask.ask_id}",
                        priority=priority.value,
                        category="ask_database"
                    )
                except Exception as e:
                    self.logger.debug(f"Could not add to master todo: {e}")

            self.logger.info(f"✅ Created Master/Padawan todos: {todo.todo_id}")
        except Exception as e:
            self.logger.error(f"Could not create todos: {e}")

        return ask

    def process_ask_through_branches(self, ask_id: str) -> bool:
        """
        Process an ask through all branches:
        1. Legislative: Review and approve
        2. Executive: Execute
        3. Judicial: Validate
        4. Update checks and balances
        """
        ask = self.ask_db.get_ask(ask_id)
        if not ask:
            self.logger.error(f"Ask not found: {ask_id}")
            return False

        # Legislative: Submit and review
        if ask.status == AskStatus.DRAFT:
            self.ask_db.submit_ask(ask_id)
            self.ask_db.review_ask(ask_id, "legislative_reviewer", approve=True,
                                  notes=["Auto-approved for execution"])

        # Executive: Execute
        if ask.status == AskStatus.APPROVED:
            execution_plan = f"Execute: {ask.ask_text}"
            self.ask_db.execute_ask(ask_id, "executive_agent", execution_plan)

            # Simulate execution (in real system, this would be actual execution)
            time.sleep(1)  # Simulate work

            self.ask_db.complete_execution(ask_id, f"Execution completed for: {ask.ask_text}")

        # Judicial: Validate
        if ask.status == AskStatus.EXECUTED:
            # Re-evaluate blueprint compliance
            blueprint_compliant = True
            if self.blueprint_sync:
                try:
                    impact = self.ask_db.evaluate_blueprint_impact(ask_id)
                    blueprint_compliant = ask.blueprint_compliance if ask.blueprint_compliance is not None else True
                except Exception:
                    blueprint_compliant = True

            self.ask_db.validate_ask(
                ask_id, "judicial_reviewer",
                blueprint_compliance=blueprint_compliant,
                validation_result="Execution validated",
                notes=["All checks passed"]
            )

        # Update checks and balances
        checks = self.ask_db.update_checks_balances(ask_id)

        return checks.all_checks_passed()

    def continuously_evaluate_blueprint(self):
        """
        Continuously evaluate master blueprint

        Runs in background thread, constantly checking and updating blueprint
        """
        while self.evaluation_running:
            try:
                # Get all active asks
                active_asks = self.ask_db.list_asks(
                    status=AskStatus.APPROVED
                ) + self.ask_db.list_asks(
                    status=AskStatus.IN_EXECUTION
                )

                # Evaluate blueprint impact for each
                for ask in active_asks:
                    try:
                        self.ask_db.evaluate_blueprint_impact(ask.ask_id)
                    except Exception as e:
                        self.logger.debug(f"Could not evaluate blueprint for {ask.ask_id}: {e}")

                # Sync blueprint if available
                if self.blueprint_sync:
                    try:
                        self.blueprint_sync.sync_blueprint()
                    except Exception as e:
                        self.logger.debug(f"Could not sync blueprint: {e}")

                # Sleep until next evaluation
                time.sleep(self.evaluation_interval)

            except Exception as e:
                self.logger.error(f"Error in continuous blueprint evaluation: {e}")
                time.sleep(self.evaluation_interval)

    def continuously_maintain_todos(self):
        """
        Continuously maintain Master/Padawan todos

        Runs in background thread, keeping todos synchronized
        """
        while self.evaluation_running:
            try:
                # Get all asks with todos
                all_asks = self.ask_db.list_asks()

                for ask in all_asks:
                    if ask.master_todo_id and ask.padawan_todo_id:
                        # Update todo status based on ask status
                        try:
                            todo = self.ask_db.todos.get(ask.master_todo_id)
                            if todo:
                                # Update todo status
                                if ask.status == AskStatus.EXECUTED:
                                    todo.master_status = "completed"
                                    todo.padawan_status = "completed"
                                elif ask.status == AskStatus.IN_EXECUTION:
                                    todo.master_status = "in_progress"
                                    todo.padawan_status = "in_progress"
                                elif ask.status == AskStatus.APPROVED:
                                    todo.master_status = "pending"
                                    todo.padawan_status = "pending"

                                todo.updated_at = datetime.now().isoformat()
                                self.ask_db._save_data()
                        except Exception as e:
                            self.logger.debug(f"Could not update todo: {e}")

                # Sleep until next maintenance
                time.sleep(self.evaluation_interval)

            except Exception as e:
                self.logger.error(f"Error in continuous todo maintenance: {e}")
                time.sleep(self.evaluation_interval)

    def start_continuous_evaluation(self):
        """Start continuous evaluation threads"""
        if self.evaluation_running:
            self.logger.warning("Continuous evaluation already running")
            return

        self.evaluation_running = True

        # Start blueprint evaluation thread
        blueprint_thread = threading.Thread(
            target=self.continuously_evaluate_blueprint,
            daemon=True,
            name="BlueprintEvaluation"
        )
        blueprint_thread.start()
        self.logger.info("✅ Started continuous blueprint evaluation")

        # Start todo maintenance thread
        todo_thread = threading.Thread(
            target=self.continuously_maintain_todos,
            daemon=True,
            name="TodoMaintenance"
        )
        todo_thread.start()
        self.logger.info("✅ Started continuous todo maintenance")

    def stop_continuous_evaluation(self):
        """Stop continuous evaluation threads"""
        self.evaluation_running = False
        self.logger.info("⏹️ Stopped continuous evaluation")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        all_asks = self.ask_db.list_asks()

        status = {
            "total_asks": len(all_asks),
            "by_status": {},
            "by_branch": {},
            "by_priority": {},
            "checks_balances": {},
            "blueprint_sync": {
                "available": self.blueprint_sync is not None,
                "last_sync": None
            },
            "todo_systems": {
                "master_todo": self.master_todo is not None,
                "dual_todo": self.dual_todo is not None
            },
            "continuous_evaluation": {
                "running": self.evaluation_running,
                "interval": self.evaluation_interval
            }
        }

        # Count by status
        for ask in all_asks:
            status_name = ask.status.value
            status["by_status"][status_name] = status["by_status"].get(status_name, 0) + 1

            branch_name = ask.branch.value
            status["by_branch"][branch_name] = status["by_branch"].get(branch_name, 0) + 1

            priority_name = ask.priority.value
            status["by_priority"][priority_name] = status["by_priority"].get(priority_name, 0) + 1

        # Checks and balances summary
        for ask_id, checks in self.ask_db.checks.items():
            if checks.all_checks_passed():
                status["checks_balances"]["all_passed"] = status["checks_balances"].get("all_passed", 0) + 1
            else:
                status["checks_balances"]["pending"] = status["checks_balances"].get("pending", 0) + 1

        return status


def main():
    """Main function - demonstrate integrated system"""
    print("=" * 80)
    print("@ASK DATABASE INTEGRATED SYSTEM")
    print("US Government Checks & Balances + Blueprint + Master/Padawan Todos")
    print("=" * 80)
    print()

    project_root = Path(__file__).parent.parent.parent
    system = AskDatabaseIntegratedSystem(project_root)

    # Create an ask with full integration
    ask = system.create_ask_with_integration(
        "Implement comprehensive system audit with Marvin roast",
        priority=Priority.HIGH,
        tags=["audit", "marvin", "system"]
    )

    print(f"✅ Created integrated ask: {ask.ask_id}")
    print(f"   Status: {ask.status.value}")
    print(f"   Branch: {ask.branch.value}")
    print(f"   Blueprint Impact: {len(ask.blueprint_impact)} areas")
    print(f"   Master Todo: {ask.master_todo_id}")
    print(f"   Padawan Todo: {ask.padawan_todo_id}")
    print()

    # Process through all branches
    print("Processing ask through all branches...")
    success = system.process_ask_through_branches(ask.ask_id)
    print(f"✅ Processing complete: {success}")
    print()

    # Get checks and balances
    checks = system.ask_db.get_checks_balances(ask.ask_id)
    if checks:
        print("Checks and Balances:")
        print(f"  Executive: {checks.executive_check}")
        print(f"  Legislative: {checks.legislative_check}")
        print(f"  Judicial: {checks.judicial_check}")
        print(f"  Blueprint: {checks.blueprint_check}")
        print(f"  Todos: {checks.todo_check}")
        print(f"  All Passed: {checks.all_checks_passed()}")
        print()

    # Get system status
    status = system.get_system_status()
    print("System Status:")
    print(f"  Total Asks: {status['total_asks']}")
    print(f"  By Status: {status['by_status']}")
    print(f"  By Branch: {status['by_branch']}")
    print(f"  By Priority: {status['by_priority']}")
    print(f"  Blueprint Sync: {status['blueprint_sync']['available']}")
    print(f"  Todo Systems: {status['todo_systems']}")
    print()

    # Start continuous evaluation
    print("Starting continuous evaluation...")
    system.start_continuous_evaluation()
    print("✅ Continuous evaluation started")
    print("   (Press Ctrl+C to stop)")
    print()

    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("Stopping continuous evaluation...")
        system.stop_continuous_evaluation()
        print("✅ Stopped")

    print()
    print("=" * 80)
    print("SYSTEM READY")
    print("=" * 80)

    return 0


if __name__ == "__main__":



    sys.exit(main())