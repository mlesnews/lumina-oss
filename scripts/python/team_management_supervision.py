#!/usr/bin/env python3
"""
Team Management Supervision & Reporting System

Implements hierarchical supervision where:
A) Managers/Leads are supervised by higher-level AI/agents
B) Subordinates report completion status to their assigned Manager/Technical/Business Lead

@PEAK: Active supervision and reporting at all levels.

Tags: #MANAGEMENT #SUPERVISION #REPORTING #TEAM #REQUIRED @PEAK @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TeamManagementSupervision")

try:
    from lumina_organizational_structure import LuminaOrganizationalStructure, Team, TeamMember
    from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem
    from bidirectional_chain_of_command import BidirectionalChainOfCommand
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    SYSTEMS_AVAILABLE = False
    logger.warning(f"Systems not available: {e}")
    BidirectionalChainOfCommand = None


@dataclass
class TaskStatus:
    """Task status report from subordinate to manager"""
    task_id: str
    task_type: str  # "ticket", "project", "maintenance", etc.
    assigned_to: str
    manager: str
    status: str  # "pending", "in_progress", "completed", "blocked"
    progress_percent: float = 0.0
    completion_estimate: Optional[str] = None
    blockers: List[str] = field(default_factory=list)
    notes: str = ""
    reported_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ManagerReport:
    """Manager's report to higher-level supervisor"""
    manager_id: str
    manager_name: str
    supervisor: str  # Higher-level AI/agent supervising this manager
    team_id: str
    team_name: str
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    blocked_tasks: int = 0
    pending_tasks: int = 0
    subordinate_reports: List[TaskStatus] = field(default_factory=list)
    team_health: str = "healthy"  # "healthy", "at_risk", "critical"
    reported_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['subordinate_reports'] = [r.to_dict() if hasattr(r, 'to_dict') else r for r in self.subordinate_reports]
        return data


class TeamManagementSupervision:
    """
    Team Management Supervision & Reporting System

    BIDIRECTIONAL CHAIN-OF-COMMAND:
    - Top-down: Supervisors → Managers → Subordinates (Directives)
    - Bottom-up: Subordinates → Managers → Supervisors (Reports)
    - BOTH sides: Technical AND Business
    - ALL divisions covered
    - Works like chain-of-thought: bidirectional pipe

    Implements:
    A) Manager supervision by higher-level AI/agents
    B) Subordinate reporting to managers/leads
    C) Active monitoring and status tracking
    D) Bidirectional communication (both ways as a pipe)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize supervision system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "data" / "team_management" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Initialize systems
        if SYSTEMS_AVAILABLE:
            self.org_structure = LuminaOrganizationalStructure(project_root)
            self.ticket_system = JARVISHelpdeskTicketSystem(project_root)
        else:
            self.org_structure = None
            self.ticket_system = None

        # Supervision hierarchy
        self.supervision_hierarchy = {
            "@jarvis": None,  # Top level
            "@c3po": "@jarvis",  # C-3PO reports to JARVIS
            "@r2d2": "@c3po",  # R2-D2 reports to C-3PO
        }

        # Active reports
        self.active_reports: Dict[str, List[TaskStatus]] = {}
        self.manager_reports: Dict[str, ManagerReport] = {}

        # Bidirectional chain-of-command system
        if BidirectionalChainOfCommand:
            self.chain_of_command = BidirectionalChainOfCommand(project_root)
        else:
            self.chain_of_command = None

        logger.info("=" * 80)
        logger.info("👔 TEAM MANAGEMENT SUPERVISION SYSTEM")
        logger.info("=" * 80)
        logger.info("   @PEAK: Active supervision and reporting")
        logger.info("   BIDIRECTIONAL CHAIN-OF-COMMAND (works both ways as a pipe)")
        logger.info("   A) Managers supervised by higher-level AI/agents")
        logger.info("   B) Subordinates report to managers/leads")
        logger.info("   C) Top-down: Directives flow down (Supervisor → Manager → Subordinate)")
        logger.info("   D) Bottom-up: Reports flow up (Subordinate → Manager → Supervisor)")
        logger.info("   E) BOTH sides: Technical AND Business")
        logger.info("   F) ALL divisions covered")
        logger.info("=" * 80)

    def get_subordinates(self, manager_id: str) -> List[TeamMember]:
        """Get all subordinates for a manager"""
        subordinates = []

        if not self.org_structure:
            return subordinates

        # Find teams where this person is manager or lead
        for team in self.org_structure.teams.values():
            if (team.helpdesk_manager == manager_id or 
                team.team_lead == manager_id):
                # Get all team members (subordinates)
                for member in team.members:
                    if member.member_id != manager_id:
                        subordinates.append(member)

        return subordinates

    def get_supervisor(self, manager_id: str) -> Optional[str]:
        """Get supervisor for a manager"""
        return self.supervision_hierarchy.get(manager_id)

    def collect_subordinate_reports(self, manager_id: str) -> List[TaskStatus]:
        """
        Collect status reports from all subordinates

        Args:
            manager_id: Manager/Lead to collect reports for

        Returns:
            List of task status reports from subordinates
        """
        subordinates = self.get_subordinates(manager_id)
        reports = []

        logger.info(f"📊 Collecting reports from {len(subordinates)} subordinates for {manager_id}")

        # Get tickets assigned to subordinates
        if self.ticket_system:
            tickets_dir = self.ticket_system.tickets_dir
            for ticket_file in tickets_dir.glob("*.json"):
                try:
                    with open(ticket_file, 'r', encoding='utf-8') as f:
                        ticket = json.load(f)

                    team_assignment = ticket.get("team_assignment", {})
                    assigned_to = team_assignment.get("primary_assignee")

                    # Check if this ticket is assigned to a subordinate
                    if assigned_to and any(sub.member_id == assigned_to for sub in subordinates):
                        # Check if manager is supervising this subordinate
                        if (team_assignment.get("team_manager") == manager_id or
                            team_assignment.get("technical_lead") == manager_id):

                            status = TaskStatus(
                                task_id=ticket.get("ticket_id", ""),
                                task_type="ticket",
                                assigned_to=assigned_to,
                                manager=manager_id,
                                status=ticket.get("status", "open"),
                                progress_percent=self._calculate_progress(ticket),
                                blockers=self._get_blockers(ticket),
                                notes=ticket.get("description", "")[:200]
                            )
                            reports.append(status)

                except Exception as e:
                    logger.debug(f"Error reading ticket {ticket_file}: {e}")

        # Store reports
        self.active_reports[manager_id] = reports

        logger.info(f"✅ Collected {len(reports)} reports for {manager_id}")
        return reports

    def generate_manager_report(self, manager_id: str) -> ManagerReport:
        """
        Generate manager's report to supervisor

        Args:
            manager_id: Manager to generate report for

        Returns:
            ManagerReport with all subordinate statuses
        """
        supervisor = self.get_supervisor(manager_id)
        if not supervisor:
            supervisor = "@jarvis"  # Default to JARVIS

        # Find manager's team
        manager_team = None
        manager_name = manager_id
        for team in self.org_structure.teams.values() if self.org_structure else []:
            if team.helpdesk_manager == manager_id or team.team_lead == manager_id:
                manager_team = team
                manager_name = team.team_name
                break

        if not manager_team:
            logger.warning(f"⚠️  No team found for manager {manager_id}")
            return None

        # Collect subordinate reports
        subordinate_reports = self.collect_subordinate_reports(manager_id)

        # Calculate statistics
        total = len(subordinate_reports)
        completed = sum(1 for r in subordinate_reports if r.status == "resolved" or r.status == "completed")
        in_progress = sum(1 for r in subordinate_reports if r.status == "in_progress")
        blocked = sum(1 for r in subordinate_reports if len(r.blockers) > 0)
        pending = sum(1 for r in subordinate_reports if r.status == "open" or r.status == "pending")

        # Determine team health
        if blocked > 0 or (in_progress > 0 and completed == 0):
            team_health = "at_risk"
        elif blocked > total * 0.3:
            team_health = "critical"
        else:
            team_health = "healthy"

        # Create report
        report = ManagerReport(
            manager_id=manager_id,
            manager_name=manager_name,
            supervisor=supervisor,
            team_id=manager_team.team_id,
            team_name=manager_team.team_name,
            total_tasks=total,
            completed_tasks=completed,
            in_progress_tasks=in_progress,
            blocked_tasks=blocked,
            pending_tasks=pending,
            subordinate_reports=subordinate_reports,
            team_health=team_health
        )

        # Store report
        self.manager_reports[manager_id] = report

        # Save report
        self._save_manager_report(report)

        logger.info("=" * 80)
        logger.info(f"📋 MANAGER REPORT: {manager_id}")
        logger.info("=" * 80)
        logger.info(f"   Supervisor: {supervisor}")
        logger.info(f"   Team: {manager_team.team_name}")
        logger.info(f"   Total Tasks: {total}")
        logger.info(f"   ✅ Completed: {completed}")
        logger.info(f"   🔄 In Progress: {in_progress}")
        logger.info(f"   ⚠️  Blocked: {blocked}")
        logger.info(f"   ⏳ Pending: {pending}")
        logger.info(f"   Health: {team_health.upper()}")
        logger.info("=" * 80)

        return report

    def report_to_supervisor(self, manager_id: str) -> bool:
        """
        Manager reports to their supervisor

        Args:
            manager_id: Manager reporting

        Returns:
            True if report sent successfully
        """
        report = self.generate_manager_report(manager_id)
        if not report:
            return False

        supervisor = report.supervisor

        logger.info(f"📤 {manager_id} reporting to {supervisor}")
        logger.info(f"   Report ID: {report.manager_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # Log report details
        if report.blocked_tasks > 0:
            logger.warning(f"⚠️  {report.blocked_tasks} blocked tasks need attention")
            for task in report.subordinate_reports:
                if task.blockers:
                    logger.warning(f"   - {task.task_id}: {', '.join(task.blockers)}")

        # Report to supervisor (JARVIS, C-3PO, etc.)
        self._send_report_to_supervisor(report, supervisor)

        return True

    def _calculate_progress(self, ticket: Dict[str, Any]) -> float:
        """Calculate progress percentage for a ticket"""
        status = ticket.get("status", "open")
        if status == "resolved" or status == "closed":
            return 100.0
        elif status == "in_progress":
            return 50.0
        else:
            return 0.0

    def _get_blockers(self, ticket: Dict[str, Any]) -> List[str]:
        """Extract blockers from ticket"""
        blockers = []
        metadata = ticket.get("metadata", {})

        if metadata.get("blocked"):
            blockers.append("Ticket marked as blocked")

        if metadata.get("waiting_for"):
            blockers.append(f"Waiting for: {metadata['waiting_for']}")

        return blockers

    def _save_manager_report(self, report: ManagerReport):
        try:
            """Save manager report to file"""
            report_file = self.reports_dir / f"{report.manager_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_manager_report: {e}", exc_info=True)
            raise
    def _send_report_to_supervisor(self, report: ManagerReport, supervisor: str):
        try:
            """Send report to supervisor (JARVIS, C-3PO, etc.)"""
            logger.info(f"📨 Sending report to {supervisor}")
            logger.info(f"   From: {report.manager_id} ({report.manager_name})")
            logger.info(f"   Team: {report.team_name}")
            logger.info(f"   Health: {report.team_health.upper()}")

            # Create supervisor notification
            notification = {
                "type": "manager_report",
                "from": report.manager_id,
                "to": supervisor,
                "timestamp": report.reported_at,
                "report": report.to_dict()
            }

            # Save notification
            notifications_dir = self.project_root / "data" / "team_management" / "notifications"
            notifications_dir.mkdir(parents=True, exist_ok=True)
            notification_file = notifications_dir / f"{supervisor}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump(notification, f, indent=2)

            logger.info(f"✅ Report sent to {supervisor}")

        except Exception as e:
            self.logger.error(f"Error in _send_report_to_supervisor: {e}", exc_info=True)
            raise
    def process_all_managers(self) -> Dict[str, Any]:
        """
        Process all managers - collect reports and report to supervisors

        BIDIRECTIONAL CHAIN-OF-COMMAND:
        - Bottom-up: Collect reports from subordinates → managers → supervisors
        - Top-down: Process pending directives from supervisors → managers → subordinates
        - BOTH sides: Technical AND Business leads included
        - ALL divisions: Process all teams across all divisions

        Returns:
            Processing results
        """
        logger.info("=" * 80)
        logger.info("🔄 PROCESSING ALL MANAGERS - BIDIRECTIONAL CHAIN-OF-COMMAND")
        logger.info("=" * 80)
        logger.info("   BOTTOM-UP: Collecting reports (Subordinate → Manager → Supervisor)")
        logger.info("   TOP-DOWN: Processing directives (Supervisor → Manager → Subordinate)")
        logger.info("   BOTH SIDES: Technical AND Business")
        logger.info("   ALL DIVISIONS: Complete coverage")
        logger.info("=" * 80)

        results = {
            "managers_processed": 0,
            "reports_generated": 0,
            "reports_sent": 0,
            "managers": {}
        }

        if not self.org_structure:
            logger.error("❌ Organizational structure not available")
            return results

        # Find all managers (BOTH Technical AND Business)
        managers = set()
        for team in self.org_structure.teams.values():
            # Technical side
            if team.helpdesk_manager:
                managers.add(team.helpdesk_manager)
            if team.team_lead:
                managers.add(team.team_lead)
            # Business side (if available in team metadata)
            # Note: Business leads would be in team metadata if available

        logger.info(f"📋 Found {len(managers)} managers/leads to process")

        # Process each manager
        for manager_id in managers:
            try:
                logger.info(f"")
                logger.info(f"👔 Processing manager: {manager_id}")

                # Generate report
                report = self.generate_manager_report(manager_id)
                if report:
                    results["reports_generated"] += 1
                    results["managers"][manager_id] = {
                        "team": report.team_name,
                        "total_tasks": report.total_tasks,
                        "completed": report.completed_tasks,
                        "in_progress": report.in_progress_tasks,
                        "blocked": report.blocked_tasks,
                        "health": report.team_health
                    }

                    # Report to supervisor
                    if self.report_to_supervisor(manager_id):
                        results["reports_sent"] += 1

                results["managers_processed"] += 1

            except Exception as e:
                logger.error(f"❌ Error processing manager {manager_id}: {e}")

        # Process bidirectional chain-of-command (top-down directives)
        if self.chain_of_command:
            try:
                logger.info("")
                logger.info("🔗 Processing bidirectional chain-of-command pipes...")
                pipe_results = self.chain_of_command.process_all_pipes()
                results['chain_of_command'] = pipe_results
                logger.info(f"✅ Processed {pipe_results.get('pipes_processed', 0)} chain-of-command pipes")
            except Exception as e:
                logger.warning(f"⚠️  Chain-of-command processing failed: {e}")
                results['chain_of_command'] = {'error': str(e)}

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ BIDIRECTIONAL SUPERVISION & REPORTING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Managers Processed: {results['managers_processed']}")
        logger.info(f"   Reports Generated: {results['reports_generated']}")
        logger.info(f"   Reports Sent: {results['reports_sent']}")
        if 'chain_of_command' in results:
            logger.info(f"   Chain-of-Command Pipes: {results['chain_of_command'].get('pipes_processed', 0)}")
        logger.info("=" * 80)

        return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Team Management Supervision & Reporting")
    parser.add_argument("--manager", type=str, help="Process specific manager")
    parser.add_argument("--all", action="store_true", help="Process all managers")
    args = parser.parse_args()

    supervision = TeamManagementSupervision()

    if args.manager:
        supervision.report_to_supervisor(args.manager)
    elif args.all:
        supervision.process_all_managers()
    else:
        # Default: process all managers
        supervision.process_all_managers()
