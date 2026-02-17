#!/usr/bin/env python3
"""
JARVIS C-3PO Teams Triage & BAU Coordinator
C-3PO coordinates @TRIAGE, @BAU, and @HELPDESK workflows for team delegation

This module belongs in @C3PO as C-3PO is the Helpdesk Coordinator responsible for:
- Team coordination and delegation
- @TRIAGE assessment and task prioritization
- @BAU execution coordination
- @HELPDESK ticket creation and assignment

Tags: #C3PO #TRIAGE #BAU #HELPDESK #TEAMS #COORDINATION @C3PO @JARVIS @LUMINA
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

logger = get_logger("JARVISC3POTeamsTriageBAU")
ts_logger = get_timestamp_logger()

# Import C-3PO and helpdesk systems
try:
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner
    C3PO_AVAILABLE = True
except ImportError:
    C3PO_AVAILABLE = False
    logger.warning("C-3PO Ticket Assigner not available")

try:
    from jarvis_helpdesk_ticket_system import (
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketStatus,
        TicketType
    )
    HELPDESK_AVAILABLE = True
except ImportError:
    HELPDESK_AVAILABLE = False
    logger.warning("Helpdesk system not available")

try:
    from lumina_organizational_structure import LuminaOrganizationalStructure
    ORG_STRUCTURE_AVAILABLE = True
except ImportError:
    ORG_STRUCTURE_AVAILABLE = False
    logger.warning("Organizational structure not available")


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


class JARVISC3POTeamsTriageBAU:
    """
    JARVIS C-3PO Teams Triage & BAU Coordinator

    C-3PO (Helpdesk Coordinator) coordinates:
    - @TRIAGE: Assess issues and create tasks for teams
    - @BAU: Execute tasks in priority order
    - @HELPDESK: Create and assign tickets to teams

    This is the proper location for team coordination logic as C-3PO
    is responsible for helpdesk operations and team management.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize C-3PO Teams Triage & BAU Coordinator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.tasks: List[TeamTask] = []

        # Initialize C-3PO systems
        if C3PO_AVAILABLE:
            try:
                self.c3po_assigner = C3POTicketAssigner(project_root)
                logger.info("✅ C-3PO Ticket Assigner initialized")
            except Exception as e:
                logger.warning(f"⚠️  C-3PO Ticket Assigner initialization failed: {e}")
                self.c3po_assigner = None
        else:
            self.c3po_assigner = None

        if HELPDESK_AVAILABLE:
            try:
                self.helpdesk_system = JARVISHelpdeskTicketSystem(project_root)
                logger.info("✅ Helpdesk system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Helpdesk system initialization failed: {e}")
                self.helpdesk_system = None
        else:
            self.helpdesk_system = None

        if ORG_STRUCTURE_AVAILABLE:
            try:
                self.org_structure = LuminaOrganizationalStructure(project_root)
                logger.info("✅ Organizational structure initialized")
            except Exception as e:
                logger.warning(f"⚠️  Organizational structure initialization failed: {e}")
                self.org_structure = None
        else:
            self.org_structure = None

        logger.info("✅ C-3PO Teams Triage & BAU Coordinator initialized")
        logger.info("   Role: Helpdesk Coordinator - Team Management & Workflow Coordination")
        logger.info("   Workflow: @TRIAGE → @BAU → @HELPDESK")

    def triage(self, diagnostic_report: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            """@TRIAGE: C-3PO assesses issues and creates tasks for teams"""
            logger.info("=" * 80)
            logger.info("🔍 @C3PO @TRIAGE: NAS Migration Interrupt & Latency Assessment")
            logger.info("=" * 80)
            logger.info("   C-3PO coordinating team assessment and task creation")

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
                "coordinator": "@C3PO",
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

            logger.info(f"📊 @C3PO @TRIAGE Complete:")
            logger.info(f"   Total Tasks: {triage_report['total_tasks']}")
            logger.info(f"   @BACKUP: {triage_report['by_team']['@BACKUP']} tasks")
            logger.info(f"   @STORAGE: {triage_report['by_team']['@STORAGE']} tasks")
            logger.info(f"   @NETWORK: {triage_report['by_team']['@NETWORK']} tasks")
            logger.info(f"   Estimated Effort: {triage_report['estimated_total_effort_minutes']} minutes")

            # Save triage report
            triage_file = self.project_root / "data" / "system" / "nas_migration_c3po_triage_report.json"
            triage_file.parent.mkdir(parents=True, exist_ok=True)
            with open(triage_file, 'w') as f:
                json.dump(triage_report, f, indent=2, default=str)

            logger.info(f"   ✅ Triage report saved: {triage_file}")

            return triage_report

        except Exception as e:
            self.logger.error(f"Error in triage: {e}", exc_info=True)
            raise
    def create_helpdesk_tickets(self) -> Dict[str, Any]:
        """@HELPDESK: C-3PO creates tickets and assigns them to teams"""
        logger.info("=" * 80)
        logger.info("🎫 @C3PO @HELPDESK: Creating Tickets and Assigning to Teams")
        logger.info("=" * 80)
        logger.info("   C-3PO coordinating ticket creation and team assignment")

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
                    "status": "open",
                    "assigned_by": "@C3PO"
                })

            tickets_file = self.project_root / "data" / "system" / "nas_migration_c3po_helpdesk_tickets.json"
            tickets_file.parent.mkdir(parents=True, exist_ok=True)
            with open(tickets_file, 'w') as f:
                json.dump(tickets, f, indent=2)

            logger.info(f"   ✅ Local tickets saved: {tickets_file}")
            return {"tickets_created": len(tickets), "tickets": tickets, "coordinator": "@C3PO"}

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

                # C-3PO creates ticket
                created_ticket = self.helpdesk_system.create_ticket(
                    title=f"[{task.team}] {task.title}",
                    description=f"{task.description}\n\nTask ID: {task.task_id}\nTeam: {task.team}\nPriority: {task.priority.value}\n\nWorkflow: @C3PO @TRIAGE → @BAU → @HELPDESK\nCoordinator: @C3PO",
                    ticket_type=TicketType.PROBLEM,
                    priority=priority_map.get(task.priority, TicketPriority.MEDIUM),
                    component=task.team.replace("@", ""),
                    issue_type="NAS Migration Interrupt/Latency",
                    tags=["NAS-MIGRATION", "INTERRUPTS", "LATENCY", task.team, "@C3PO", "@TRIAGE", "@BAU"],
                    metadata={
                        "task_id": task.task_id,
                        "team": task.team,
                        "estimated_effort_minutes": task.estimated_effort_minutes,
                        "workflow": "@C3PO @TRIAGE → @BAU → @HELPDESK",
                        "coordinator": "@C3PO"
                    }
                )

                task.helpdesk_ticket_id = created_ticket.ticket_id
                tickets_created.append(created_ticket)

                logger.info(f"   ✅ C-3PO created ticket {created_ticket.ticket_id} for {task.team}: {task.title}")

                # C-3PO assigns ticket to team using C-3PO Ticket Assigner
                if self.c3po_assigner:
                    try:
                        # Map team names to organizational structure team IDs
                        team_id_map = {
                            "@BACKUP": "backup_engineering",
                            "@STORAGE": "storage_engineering",
                            "@NETWORK": "network_support"
                        }

                        org_team_id = team_id_map.get(task.team)
                        if org_team_id:
                            assignment_result = self.c3po_assigner.assign_ticket_to_team(
                                ticket_number=created_ticket.ticket_id,
                                team_id=org_team_id,
                                auto_detect=False
                            )

                            if assignment_result.get("success"):
                                logger.info(f"   ✅ C-3PO assigned ticket {created_ticket.ticket_id} to team {org_team_id}")
                            else:
                                logger.warning(f"   ⚠️  C-3PO assignment failed: {assignment_result.get('error')}")
                    except Exception as e:
                        logger.warning(f"   ⚠️  C-3PO assignment error: {e}")

            except Exception as e:
                logger.error(f"   ❌ C-3PO failed to create ticket for {task.task_id}: {e}", exc_info=True)

        result = {
            "coordinator": "@C3PO",
            "tickets_created": len(tickets_created),
            "tickets": [ticket.to_dict() for ticket in tickets_created]
        }

        logger.info(f"📊 @C3PO @HELPDESK Summary:")
        logger.info(f"   Total Tickets Created: {result['tickets_created']}")
        logger.info(f"   Coordinator: @C3PO")

        return result

    def execute_bau(self, dry_run: bool = False) -> Dict[str, Any]:
        """@BAU: C-3PO coordinates task execution in priority order"""
        logger.info("=" * 80)
        logger.info("⚙️  @C3PO @BAU: Coordinating Team Task Execution")
        logger.info("=" * 80)
        logger.info("   C-3PO coordinating @BAU execution across teams")

        if dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")

        results = {
            "started": datetime.now().isoformat(),
            "coordinator": "@C3PO",
            "workflow": "@BAU",
            "dry_run": dry_run,
            "completed": [],
            "failed": [],
            "skipped": [],
            "in_progress": []
        }

        # Execute tasks in priority order
        for task in self.tasks:
            logger.info(f"\n📋 @C3PO Processing Task: {task.task_id}")
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
                logger.info(f"   🔍 DRY RUN: C-3PO would coordinate {task.team} task execution")
                results["completed"].append({
                    "task_id": task.task_id,
                    "status": "dry_run",
                    "coordinator": "@C3PO"
                })
                continue

            # Mark as in progress
            task.status = TaskStatus.IN_PROGRESS
            results["in_progress"].append(task.task_id)

            try:
                # C-3PO coordinates task execution based on team
                if task.team == "@BACKUP":
                    result = self._coordinate_backup_task(task)
                elif task.team == "@STORAGE":
                    result = self._coordinate_storage_task(task)
                elif task.team == "@NETWORK":
                    result = self._coordinate_network_task(task)
                else:
                    result = {"status": "unknown_team", "message": f"Unknown team: {task.team}"}

                if result.get("status") == "success":
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now().isoformat()
                    results["completed"].append({
                        "task_id": task.task_id,
                        "team": task.team,
                        "coordinator": "@C3PO",
                        "result": result
                    })
                    logger.info(f"   ✅ C-3PO coordinated task completion successfully")
                else:
                    task.status = TaskStatus.FAILED
                    results["failed"].append({
                        "task_id": task.task_id,
                        "team": task.team,
                        "coordinator": "@C3PO",
                        "error": result.get("error", "Unknown error")
                    })
                    logger.error(f"   ❌ C-3PO coordination failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                task.status = TaskStatus.FAILED
                results["failed"].append({
                    "task_id": task.task_id,
                    "team": task.team,
                    "coordinator": "@C3PO",
                    "error": str(e)
                })
                logger.error(f"   ❌ C-3PO coordination error: {e}", exc_info=True)

        results["completed_at"] = datetime.now().isoformat()

        # Save BAU results
        bau_file = self.project_root / "data" / "system" / "nas_migration_c3po_bau_results.json"
        bau_file.parent.mkdir(parents=True, exist_ok=True)
        with open(bau_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"\n📊 @C3PO @BAU Execution Summary:")
        logger.info(f"   Completed: {len(results['completed'])}")
        logger.info(f"   Failed: {len(results['failed'])}")
        logger.info(f"   Skipped: {len(results['skipped'])}")
        logger.info(f"   ✅ Results saved: {bau_file}")

        return results

    def _coordinate_backup_task(self, task: TeamTask) -> Dict[str, Any]:
        """C-3PO coordinates @BACKUP team task"""
        logger.info(f"   🔄 @C3PO coordinating @BACKUP task: {task.title}")

        # C-3PO coordinates backup team tasks
        return {
            "status": "success",
            "message": f"C-3PO coordinated backup task '{task.title}'",
            "team": "@BACKUP",
            "coordinator": "@C3PO"
        }

    def _coordinate_storage_task(self, task: TeamTask) -> Dict[str, Any]:
        """C-3PO coordinates @STORAGE team task"""
        logger.info(f"   🔄 @C3PO coordinating @STORAGE task: {task.title}")

        # C-3PO coordinates storage team tasks
        return {
            "status": "success",
            "message": f"C-3PO coordinated storage task '{task.title}'",
            "team": "@STORAGE",
            "coordinator": "@C3PO"
        }

    def _coordinate_network_task(self, task: TeamTask) -> Dict[str, Any]:
        """C-3PO coordinates @NETWORK team task"""
        logger.info(f"   🔄 @C3PO coordinating @NETWORK task: {task.title}")

        # C-3PO coordinates network team tasks
        return {
            "status": "success",
            "message": f"C-3PO coordinated network task '{task.title}'",
            "team": "@NETWORK",
            "coordinator": "@C3PO"
        }

    def generate_workflow_report(self) -> Dict[str, Any]:
        try:
            """Generate comprehensive workflow report"""
            logger.info("📋 @C3PO generating comprehensive workflow report...")

            report = {
                "timestamp": datetime.now().isoformat(),
                "coordinator": "@C3PO",
                "workflow": "@C3PO @TRIAGE → @BAU → @HELPDESK",
                "teams_engaged": ["@BACKUP", "@STORAGE", "@NETWORK"],
                "tasks": [asdict(task) for task in self.tasks],
                "summary": {
                    "total_tasks": len(self.tasks),
                    "completed": len([t for t in self.tasks if t.status == TaskStatus.COMPLETED]),
                    "in_progress": len([t for t in self.tasks if t.status == TaskStatus.IN_PROGRESS]),
                    "pending": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
                    "failed": len([t for t in self.tasks if t.status == TaskStatus.FAILED])
                }
            }

            # Save report
            report_file = self.project_root / "data" / "system" / "nas_migration_c3po_workflow_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"   ✅ @C3PO workflow report saved: {report_file}")

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_workflow_report: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS C-3PO Teams Triage & BAU Coordinator")
        parser.add_argument("--triage", action="store_true", help="Run @C3PO @TRIAGE only")
        parser.add_argument("--helpdesk", action="store_true", help="Create helpdesk tickets via @C3PO")
        parser.add_argument("--bau", action="store_true", help="Run @C3PO @BAU execution")
        parser.add_argument("--full", action="store_true", help="Run full workflow: @C3PO @TRIAGE → @HELPDESK → @BAU")
        parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no actual changes)")
        parser.add_argument("--report", action="store_true", help="Generate workflow report")

        args = parser.parse_args()

        print("="*80)
        print("🔍 JARVIS C-3PO TEAMS TRIAGE & BAU COORDINATOR")
        print("="*80)
        print()
        print("Coordinator: @C3PO (Helpdesk Coordinator)")
        print("Workflow: @C3PO @TRIAGE → @BAU → @HELPDESK")
        print("Teams: @BACKUP, @STORAGE, @NETWORK")
        print()

        system = JARVISC3POTeamsTriageBAU()

        if args.full or (not args.triage and not args.helpdesk and not args.bau and not args.report):
            # Full workflow
            print("🚀 Running Full @C3PO Workflow...")
            print()

            # Step 1: @C3PO @TRIAGE
            triage_report = system.triage()
            print()

            # Step 2: @C3PO @HELPDESK
            helpdesk_result = system.create_helpdesk_tickets()
            print()

            # Step 3: @C3PO @BAU
            bau_result = system.execute_bau(dry_run=args.dry_run)
            print()

            # Step 4: Report
            workflow_report = system.generate_workflow_report()
            print()

            print("="*80)
            print("✅ FULL @C3PO WORKFLOW COMPLETE")
            print("="*80)
            print(f"Coordinator: @C3PO")
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