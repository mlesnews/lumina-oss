#!/usr/bin/env python3
"""
NAS Migration Teams Triage & BAU with Helpdesk Integration
DEPRECATED: This logic has been moved to @C3PO

Please use: jarvis_c3po_teams_triage_bau.py instead

This file is kept for backward compatibility but delegates to C-3PO.

Tags: #NAS-MIGRATION #TRIAGE #BAU #HELPDESK #TEAMS #BACKUP #STORAGE #NETWORK #DEPRECATED @C3PO @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("NASMigrationTeamsTriageBAU")
ts_logger = get_timestamp_logger()

# Try to import helpdesk system
try:
    from jarvis_helpdesk_ticket_system import (
        HelpdeskTicket,
        TicketPriority,
        TicketStatus,
        TicketType,
        JARVISHelpdeskTicketSystem
    )
    HELPDESK_AVAILABLE = True
except ImportError:
    HELPDESK_AVAILABLE = False
    logger.warning("Helpdesk system not available - will use local tracking")


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TeamTask:
    """Task assigned to a team"""
    task_id: str
    team: str  # @BACKUP, @STORAGE, @NETWORK
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    estimated_effort_minutes: int
    dependencies: List[str] = None
    helpdesk_ticket_id: Optional[str] = None
    notes: str = ""
    created_at: str = ""
    completed_at: Optional[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


# DEPRECATED: Use JARVISC3POTeamsTriageBAU from jarvis_c3po_teams_triage_bau.py instead
class NASMigrationTeamsTriageBAU:
    """
    NAS Migration Teams Triage & BAU System

    Uses @TRIAGE to assess issues and @BAU to execute fixes.
    Delegates to @BACKUP, @STORAGE, @NETWORK teams.
    Tracks all tasks through @HELPDESK.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize triage/BAU system - DEPRECATED: Delegates to C-3PO"""
        logger.warning("⚠️  DEPRECATED: This class is deprecated. Use JARVISC3POTeamsTriageBAU from jarvis_c3po_teams_triage_bau.py")
        logger.warning("   Delegating to @C3PO...")

        # Import and delegate to C-3PO
        try:
            from jarvis_c3po_teams_triage_bau import JARVISC3POTeamsTriageBAU
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            self.c3po_system = JARVISC3POTeamsTriageBAU(project_root)
            logger.info("✅ Delegated to @C3PO Teams Triage & BAU Coordinator")
        except ImportError as e:
            logger.error(f"❌ Failed to import C-3PO system: {e}")
            raise

        # Keep old interface for backward compatibility
        self.project_root = project_root
        self.tasks: List[TeamTask] = []
        self.helpdesk_tickets: List[HelpdeskTicket] = []
        self.helpdesk_system = None

    def triage(self, diagnostic_report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            """@TRIAGE: Assess issues and create tasks for teams - DEPRECATED: Delegates to C-3PO"""
            logger.warning("⚠️  DEPRECATED: Delegating to @C3PO...")
            return self.c3po_system.triage(diagnostic_report)

            # Load diagnostic report if not provided
            if diagnostic_report is None:
                report_path = self.project_root / "data" / "system" / "nas_migration_interrupt_report.json"
                if report_path.exists():
                    with open(report_path, 'r') as f:
                        diagnostic_report = json.load(f)
                else:
                    logger.warning("⚠️  Diagnostic report not found - creating tasks from defaults")
                    diagnostic_report = {
                        "migration_status": {"active": True},
                        "team_actions": {
                            "@BACKUP": [],
                            "@STORAGE": [],
                            "@NETWORK": []
                        }
                    }

            # Extract team actions from diagnostic
            team_actions = diagnostic_report.get("team_actions", {})
            migration_status = diagnostic_report.get("migration_status", {})

            # Create tasks for each team
            self.tasks = []

            # @BACKUP Team Tasks
            for action in team_actions.get("@BACKUP", []):
                priority_map = {
                    "HIGH": TaskPriority.HIGH,
                    "MEDIUM": TaskPriority.MEDIUM,
                    "LOW": TaskPriority.LOW,
                    "CRITICAL": TaskPriority.CRITICAL
                }

                task = TeamTask(
                    task_id=f"BACKUP_{len(self.tasks) + 1:03d}",
                    team="@BACKUP",
                    title=action.get("action", "Backup Team Action"),
                    description=action.get("details", ""),
                    priority=priority_map.get(action.get("priority", "MEDIUM"), TaskPriority.MEDIUM),
                    status=TaskStatus.PENDING,
                    estimated_effort_minutes=30,
                    notes=f"From diagnostic: {action.get('priority', 'MEDIUM')} priority"
                )
                self.tasks.append(task)

            # @STORAGE Team Tasks
            for action in team_actions.get("@STORAGE", []):
                priority_map = {
                    "HIGH": TaskPriority.HIGH,
                    "MEDIUM": TaskPriority.MEDIUM,
                    "LOW": TaskPriority.LOW,
                    "CRITICAL": TaskPriority.CRITICAL
                }

                task = TeamTask(
                    task_id=f"STORAGE_{len(self.tasks) + 1:03d}",
                    team="@STORAGE",
                    title=action.get("action", "Storage Team Action"),
                    description=action.get("details", ""),
                    priority=priority_map.get(action.get("priority", "MEDIUM"), TaskPriority.MEDIUM),
                    status=TaskStatus.PENDING,
                    estimated_effort_minutes=45,
                    notes=f"From diagnostic: {action.get('priority', 'MEDIUM')} priority"
                )
                self.tasks.append(task)

            # @NETWORK Team Tasks
            for action in team_actions.get("@NETWORK", []):
                priority_map = {
                    "HIGH": TaskPriority.HIGH,
                    "MEDIUM": TaskPriority.MEDIUM,
                    "LOW": TaskPriority.LOW,
                    "CRITICAL": TaskPriority.CRITICAL
                }

                task = TeamTask(
                    task_id=f"NETWORK_{len(self.tasks) + 1:03d}",
                    team="@NETWORK",
                    title=action.get("action", "Network Team Action"),
                    description=action.get("details", ""),
                    priority=priority_map.get(action.get("priority", "MEDIUM"), TaskPriority.MEDIUM),
                    status=TaskStatus.PENDING,
                    estimated_effort_minutes=60,  # Network issues often take longer
                    notes=f"From diagnostic: {action.get('priority', 'MEDIUM')} priority"
                )
                self.tasks.append(task)

            # Add additional monitoring task
            if migration_status.get("active", False):
                monitor_task = TeamTask(
                    task_id="MONITOR_001",
                    team="@BACKUP",
                    title="Monitor NAS Migration Progress",
                    description="Continuously monitor migration status and system performance",
                    priority=TaskPriority.MEDIUM,
                    status=TaskStatus.PENDING,
                    estimated_effort_minutes=15,
                    notes="Ongoing monitoring during migration"
                )
                self.tasks.append(monitor_task)

            # Sort by priority
            priority_order = {
                TaskPriority.CRITICAL: 1,
                TaskPriority.HIGH: 2,
                TaskPriority.MEDIUM: 3,
                TaskPriority.LOW: 4
            }
            self.tasks.sort(key=lambda t: (priority_order[t.priority], t.task_id))

            # Generate triage report
            triage_report = {
                "timestamp": datetime.now().isoformat(),
                "workflow": "@TRIAGE",
                "total_tasks": len(self.tasks),
                "by_team": {
                    "@BACKUP": len([t for t in self.tasks if t.team == "@BACKUP"]),
                    "@STORAGE": len([t for t in self.tasks if t.team == "@STORAGE"]),
                    "@NETWORK": len([t for t in self.tasks if t.team == "@NETWORK"])
                },
                "by_priority": {
                    "critical": len([t for t in self.tasks if t.priority == TaskPriority.CRITICAL]),
                    "high": len([t for t in self.tasks if t.priority == TaskPriority.HIGH]),
                    "medium": len([t for t in self.tasks if t.priority == TaskPriority.MEDIUM]),
                    "low": len([t for t in self.tasks if t.priority == TaskPriority.LOW])
                },
                "tasks": [asdict(task) for task in self.tasks],
                "estimated_total_effort_minutes": sum(t.estimated_effort_minutes for t in self.tasks)
            }

            logger.info(f"📊 @TRIAGE Complete:")
            logger.info(f"   Total Tasks: {triage_report['total_tasks']}")
            logger.info(f"   @BACKUP: {triage_report['by_team']['@BACKUP']} tasks")
            logger.info(f"   @STORAGE: {triage_report['by_team']['@STORAGE']} tasks")
            logger.info(f"   @NETWORK: {triage_report['by_team']['@NETWORK']} tasks")
            logger.info(f"   Estimated Effort: {triage_report['estimated_total_effort_minutes']} minutes")

            # Save triage report
            triage_file = self.project_root / "data" / "system" / "nas_migration_triage_report.json"
            triage_file.parent.mkdir(parents=True, exist_ok=True)
            with open(triage_file, 'w') as f:
                json.dump(triage_report, f, indent=2, default=str)

            logger.info(f"   ✅ Triage report saved: {triage_file}")

            return triage_report

        except Exception as e:
            self.logger.error(f"Error in triage: {e}", exc_info=True)
            raise
    def create_helpdesk_tickets(self) -> Dict[str, Any]:
        """Create helpdesk tickets for all tasks - DEPRECATED: Delegates to C-3PO"""
        logger.warning("⚠️  DEPRECATED: Delegating to @C3PO...")
        return self.c3po_system.create_helpdesk_tickets()

        if not self.helpdesk_system:
            logger.warning("⚠️  Helpdesk system not available - using local tracking")
            # Create local ticket records
            tickets = []
            for task in self.tasks:
                ticket_id = f"PM{datetime.now().strftime('%Y%m%d')}{task.task_id}"
                task.helpdesk_ticket_id = ticket_id
                tickets.append({
                    "ticket_id": ticket_id,
                    "task_id": task.task_id,
                    "team": task.team,
                    "title": task.title,
                    "status": "open"
                })

            tickets_file = self.project_root / "data" / "system" / "nas_migration_helpdesk_tickets.json"
            tickets_file.parent.mkdir(parents=True, exist_ok=True)
            with open(tickets_file, 'w') as f:
                json.dump(tickets, f, indent=2)

            logger.info(f"   ✅ Local tickets saved: {tickets_file}")
            return {"tickets_created": len(tickets), "tickets": tickets}

        # Use actual helpdesk system
        tickets_created = []

        for task in self.tasks:
            try:
                # Map task priority to ticket priority
                priority_map = {
                    TaskPriority.CRITICAL: TicketPriority.CRITICAL,
                    TaskPriority.HIGH: TicketPriority.HIGH,
                    TaskPriority.MEDIUM: TicketPriority.MEDIUM,
                    TaskPriority.LOW: TicketPriority.LOW
                }

                # Create ticket using the helpdesk system's create_ticket method
                created_ticket = self.helpdesk_system.create_ticket(
                    title=f"[{task.team}] {task.title}",
                    description=f"{task.description}\n\nTask ID: {task.task_id}\nTeam: {task.team}\nPriority: {task.priority.value}\n\nWorkflow: @TRIAGE → @BAU → @HELPDESK",
                    ticket_type=TicketType.PROBLEM,
                    priority=priority_map.get(task.priority, TicketPriority.MEDIUM),
                    component=task.team.replace("@", ""),
                    issue_type="NAS Migration Interrupt/Latency",
                    tags=["NAS-MIGRATION", "INTERRUPTS", "LATENCY", task.team, "@TRIAGE", "@BAU"],
                    metadata={
                        "task_id": task.task_id,
                        "team": task.team,
                        "estimated_effort_minutes": task.estimated_effort_minutes,
                        "workflow": "@TRIAGE → @BAU → @HELPDESK"
                    }
                )
                task.helpdesk_ticket_id = created_ticket.ticket_id
                tickets_created.append(created_ticket)

                logger.info(f"   ✅ Created ticket {created_ticket.ticket_id} for {task.team}: {task.title}")

            except Exception as e:
                logger.error(f"   ❌ Failed to create ticket for {task.task_id}: {e}", exc_info=True)

        result = {
            "tickets_created": len(tickets_created),
            "tickets": [ticket.to_dict() for ticket in tickets_created]
        }

        logger.info(f"📊 @HELPDESK Summary:")
        logger.info(f"   Total Tickets Created: {result['tickets_created']}")

        return result

    def execute_bau(self, dry_run: bool = False) -> Dict[str, Any]:
        """@BAU: Execute tasks in priority order - DEPRECATED: Delegates to C-3PO"""
        logger.warning("⚠️  DEPRECATED: Delegating to @C3PO...")
        return self.c3po_system.execute_bau(dry_run)

        if dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")

        results = {
            "started": datetime.now().isoformat(),
            "workflow": "@BAU",
            "dry_run": dry_run,
            "completed": [],
            "failed": [],
            "skipped": [],
            "in_progress": []
        }

        # Execute tasks in priority order
        for task in self.tasks:
            logger.info(f"\n📋 Processing Task: {task.task_id}")
            logger.info(f"   Team: {task.team}")
            logger.info(f"   Title: {task.title}")
            logger.info(f"   Priority: {task.priority.value}")

            # Check dependencies
            if task.dependencies:
                unmet = [dep for dep in task.dependencies
                        if dep not in [t.task_id for t in self.tasks if t.status == TaskStatus.COMPLETED]]
                if unmet:
                    logger.warning(f"   ⚠️  Dependencies not met: {unmet}")
                    task.status = TaskStatus.BLOCKED
                    results["skipped"].append({
                        "task_id": task.task_id,
                        "reason": f"Dependencies not met: {unmet}"
                    })
                    continue

            if dry_run:
                logger.info(f"   🔍 DRY RUN: Would execute {task.team} task")
                results["completed"].append({
                    "task_id": task.task_id,
                    "status": "dry_run"
                })
                continue

            # Mark as in progress
            task.status = TaskStatus.IN_PROGRESS
            results["in_progress"].append(task.task_id)

            try:
                # Execute task based on team
                if task.team == "@BACKUP":
                    result = self._execute_backup_task(task)
                elif task.team == "@STORAGE":
                    result = self._execute_storage_task(task)
                elif task.team == "@NETWORK":
                    result = self._execute_network_task(task)
                else:
                    result = {"status": "unknown_team", "message": f"Unknown team: {task.team}"}

                if result.get("status") == "success":
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now().isoformat()
                    results["completed"].append({
                        "task_id": task.task_id,
                        "team": task.team,
                        "result": result
                    })
                    logger.info(f"   ✅ Task completed successfully")
                else:
                    task.status = TaskStatus.FAILED
                    results["failed"].append({
                        "task_id": task.task_id,
                        "team": task.team,
                        "error": result.get("error", "Unknown error")
                    })
                    logger.error(f"   ❌ Task failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                task.status = TaskStatus.FAILED
                results["failed"].append({
                    "task_id": task.task_id,
                    "team": task.team,
                    "error": str(e)
                })
                logger.error(f"   ❌ Task execution error: {e}", exc_info=True)

        results["completed_at"] = datetime.now().isoformat()

        # Save BAU results
        bau_file = self.project_root / "data" / "system" / "nas_migration_bau_results.json"
        bau_file.parent.mkdir(parents=True, exist_ok=True)
        with open(bau_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"\n📊 @BAU Execution Summary:")
        logger.info(f"   Completed: {len(results['completed'])}")
        logger.info(f"   Failed: {len(results['failed'])}")
        logger.info(f"   Skipped: {len(results['skipped'])}")
        logger.info(f"   ✅ Results saved: {bau_file}")

        return results

    def _execute_backup_task(self, task: TeamTask) -> Dict[str, Any]:
        """Execute @BACKUP team task"""
        logger.info(f"   🔄 Executing @BACKUP task: {task.title}")

        # Backup team tasks are typically monitoring/review tasks
        # Implementation would depend on specific task
        return {
            "status": "success",
            "message": f"Backup task '{task.title}' executed",
            "team": "@BACKUP"
        }

    def _execute_storage_task(self, task: TeamTask) -> Dict[str, Any]:
        """Execute @STORAGE team task"""
        logger.info(f"   🔄 Executing @STORAGE task: {task.title}")

        # Storage team tasks are typically disk I/O monitoring/optimization
        # Implementation would depend on specific task
        return {
            "status": "success",
            "message": f"Storage task '{task.title}' executed",
            "team": "@STORAGE"
        }

    def _execute_network_task(self, task: TeamTask) -> Dict[str, Any]:
        """Execute @NETWORK team task"""
        logger.info(f"   🔄 Executing @NETWORK task: {task.title}")

        # Network team tasks are typically latency/bandwidth investigation
        # Implementation would depend on specific task
        return {
            "status": "success",
            "message": f"Network task '{task.title}' executed",
            "team": "@NETWORK"
        }

    def generate_workflow_report(self) -> Dict[str, Any]:
        try:
            """Generate comprehensive workflow report"""
            logger.info("📋 Generating comprehensive workflow report...")

            report = {
                "timestamp": datetime.now().isoformat(),
                "workflow": "@TRIAGE → @BAU → @HELPDESK",
                "teams_engaged": ["@BACKUP", "@STORAGE", "@NETWORK"],
                "tasks": [asdict(task) for task in self.tasks],
                "helpdesk_tickets": [ticket.to_dict() if hasattr(ticket, 'to_dict') else ticket
                                    for ticket in self.helpdesk_tickets],
                "summary": {
                    "total_tasks": len(self.tasks),
                    "completed": len([t for t in self.tasks if t.status == TaskStatus.COMPLETED]),
                    "in_progress": len([t for t in self.tasks if t.status == TaskStatus.IN_PROGRESS]),
                    "pending": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
                    "failed": len([t for t in self.tasks if t.status == TaskStatus.FAILED])
                }
            }

            # Save report
            report_file = self.project_root / "data" / "system" / "nas_migration_workflow_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"   ✅ Workflow report saved: {report_file}")

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_workflow_report: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="NAS Migration Teams Triage & BAU with Helpdesk")
        parser.add_argument("--triage", action="store_true", help="Run @TRIAGE only")
        parser.add_argument("--helpdesk", action="store_true", help="Create helpdesk tickets")
        parser.add_argument("--bau", action="store_true", help="Run @BAU execution")
        parser.add_argument("--full", action="store_true", help="Run full workflow: @TRIAGE → @HELPDESK → @BAU")
        parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no actual changes)")
        parser.add_argument("--report", action="store_true", help="Generate workflow report")

        args = parser.parse_args()

        print("="*80)
        print("🔍 NAS MIGRATION TEAMS TRIAGE & BAU WITH HELPDESK")
        print("="*80)
        print()
        print("Workflow: @TRIAGE → @BAU → @HELPDESK")
        print("Teams: @BACKUP, @STORAGE, @NETWORK")
        print()

        system = NASMigrationTeamsTriageBAU()

        if args.full or (not args.triage and not args.helpdesk and not args.bau and not args.report):
            # Full workflow
            print("🚀 Running Full Workflow...")
            print()

            # Step 1: @TRIAGE
            triage_report = system.triage()
            print()

            # Step 2: @HELPDESK
            helpdesk_result = system.create_helpdesk_tickets()
            print()

            # Step 3: @BAU
            bau_result = system.execute_bau(dry_run=args.dry_run)
            print()

            # Step 4: Report
            workflow_report = system.generate_workflow_report()
            print()

            print("="*80)
            print("✅ FULL WORKFLOW COMPLETE")
            print("="*80)
            print(f"Tasks Created: {triage_report['total_tasks']}")
            print(f"Tickets Created: {helpdesk_result.get('tickets_created', 0)}")
            print(f"Tasks Completed: {len(bau_result['completed'])}")
            print(f"Tasks Failed: {len(bau_result['failed'])}")

        elif args.triage:
            triage_report = system.triage()
            print(json.dumps(triage_report, indent=2, default=str))

        elif args.helpdesk:
            # Need to run triage first
            system.triage()
            helpdesk_result = system.create_helpdesk_tickets()
            print(json.dumps(helpdesk_result, indent=2, default=str))

        elif args.bau:
            # Need to run triage first
            system.triage()
            bau_result = system.execute_bau(dry_run=args.dry_run)
            print(json.dumps(bau_result, indent=2, default=str))

        elif args.report:
            workflow_report = system.generate_workflow_report()
            print(json.dumps(workflow_report, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()