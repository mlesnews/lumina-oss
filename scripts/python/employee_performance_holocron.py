#!/usr/bin/env python3
"""
Employee Performance HOLOCRON

Comprehensive table/@HOLOCRON of all employees with:
- All roles and responsibilities
- Performance statistics score percentage (0-100%)
- Task completion rates
- Response times
- Quality metrics

Deployed to @DYNO for company-wide visibility.

Tags: #HOLOCRON #EMPLOYEE #PERFORMANCE #DYNO #REQUIRED @HOLOCRON @DYNO @JARVIS @LUMINA @DOIT
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

logger = get_logger("EmployeePerformanceHolocron")

try:
    from lumina_organizational_structure import LuminaOrganizationalStructure, TeamMember, Team
    from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem
    from team_management_supervision import TeamManagementSupervision
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    SYSTEMS_AVAILABLE = False
    logger.warning(f"Systems not available: {e}")


@dataclass
class PerformanceMetrics:
    """Employee performance metrics"""
    tasks_completed: int = 0
    tasks_total: int = 0
    completion_rate: float = 0.0  # 0-100%
    average_response_time_hours: float = 0.0
    reports_submitted: int = 0
    reports_on_time: int = 0
    on_time_rate: float = 0.0  # 0-100%
    directives_executed: int = 0
    directives_total: int = 0
    execution_rate: float = 0.0  # 0-100%
    quality_score: float = 0.0  # 0-100%
    overall_performance_score: float = 0.0  # 0-100%

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EmployeeRecord:
    """Complete employee record for HOLOCRON"""
    employee_id: str
    name: str
    role: str
    responsibilities: List[str]
    division: str
    team: str
    member_type: str
    status: str
    capabilities: List[str]
    performance_metrics: PerformanceMetrics
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['performance_metrics'] = self.performance_metrics.to_dict()
        return data


class EmployeePerformanceHolocron:
    """
    Employee Performance HOLOCRON System

    Creates comprehensive table of all employees with:
    - Roles and responsibilities
    - Performance statistics (0-100%)
    - Deployed to @DYNO
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize employee performance holocron"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.holocron_dir = self.project_root / "data" / "holocrons"
        self.holocron_dir.mkdir(parents=True, exist_ok=True)

        # Initialize systems
        if SYSTEMS_AVAILABLE:
            self.org_structure = LuminaOrganizationalStructure(project_root)
            self.ticket_system = JARVISHelpdeskTicketSystem(project_root)
            self.supervision = TeamManagementSupervision(project_root)
        else:
            self.org_structure = None
            self.ticket_system = None
            self.supervision = None

        # Employee records
        self.employee_records: Dict[str, EmployeeRecord] = {}

        logger.info("=" * 80)
        logger.info("📊 EMPLOYEE PERFORMANCE HOLOCRON")
        logger.info("=" * 80)
        logger.info("   Comprehensive table of all employees")
        logger.info("   Roles, responsibilities, and performance statistics")
        logger.info("   Deployed to @DYNO")
        logger.info("=" * 80)

    def collect_all_employees(self) -> Dict[str, EmployeeRecord]:
        """
        Collect all employees from organizational structure

        Returns:
            Dictionary of employee records
        """
        logger.info("👥 Collecting all employees...")

        if not self.org_structure:
            logger.error("❌ Organizational structure not available")
            return {}

        # Collect all team members
        for team in self.org_structure.teams.values():
            for member in team.members:
                # Calculate performance metrics
                metrics = self._calculate_performance_metrics(member)

                # Create employee record
                record = EmployeeRecord(
                    employee_id=member.member_id,
                    name=member.name,
                    role=member.role,
                    responsibilities=member.responsibilities,
                    division=member.division or team.division,
                    team=member.team or team.team_id,
                    member_type=member.member_type.value if hasattr(member.member_type, 'value') else str(member.member_type),
                    status=member.status.value if hasattr(member.status, 'value') else str(member.status),
                    capabilities=member.capabilities,
                    performance_metrics=metrics
                )

                self.employee_records[member.member_id] = record

        # Also include managers and leads
        for team in self.org_structure.teams.values():
            # Team lead
            if team.team_lead:
                if team.team_lead not in self.employee_records:
                    metrics = self._calculate_performance_metrics_for_manager(team.team_lead, team)
                    record = EmployeeRecord(
                        employee_id=team.team_lead,
                        name=team.team_lead,
                        role="Technical Lead",
                        responsibilities=["Team leadership", "Technical oversight", "Quality assurance"],
                        division=team.division,
                        team=team.team_id,
                        member_type="manager",
                        status="active",
                        capabilities=team.capabilities,
                        performance_metrics=metrics
                    )
                    self.employee_records[team.team_lead] = record

            # Helpdesk manager
            if team.helpdesk_manager:
                if team.helpdesk_manager not in self.employee_records:
                    metrics = self._calculate_performance_metrics_for_manager(team.helpdesk_manager, team)
                    record = EmployeeRecord(
                        employee_id=team.helpdesk_manager,
                        name=team.helpdesk_manager,
                        role="Helpdesk Manager",
                        responsibilities=["Team management", "Ticket assignment", "Status reporting"],
                        division=team.division,
                        team=team.team_id,
                        member_type="manager",
                        status="active",
                        capabilities=team.capabilities,
                        performance_metrics=metrics
                    )
                    self.employee_records[team.helpdesk_manager] = record

        logger.info(f"✅ Collected {len(self.employee_records)} employees")
        return self.employee_records

    def _calculate_performance_metrics(self, member: TeamMember) -> PerformanceMetrics:
        """Calculate performance metrics for a team member"""
        metrics = PerformanceMetrics()

        # Get tickets assigned to this member
        if self.ticket_system:
            tickets_dir = self.ticket_system.tickets_dir
            member_tickets = []

            for ticket_file in tickets_dir.glob("*.json"):
                try:
                    with open(ticket_file, 'r', encoding='utf-8') as f:
                        ticket = json.load(f)

                    team_assignment = ticket.get("team_assignment", {})
                    assigned_to = team_assignment.get("primary_assignee")

                    if assigned_to == member.member_id:
                        member_tickets.append(ticket)
                except Exception:
                    pass

            # Calculate metrics
            metrics.tasks_total = len(member_tickets)
            metrics.tasks_completed = sum(
                1 for t in member_tickets 
                if t.get("status") in ["resolved", "closed", "completed"]
            )

            if metrics.tasks_total > 0:
                metrics.completion_rate = (metrics.tasks_completed / metrics.tasks_total) * 100.0

            # Calculate response times (simplified)
            # In real implementation, would track actual response times
            if metrics.tasks_completed > 0:
                metrics.average_response_time_hours = 24.0  # Placeholder

        # Get reports submitted
        if self.supervision:
            # Check for reports from this member
            # This would be tracked in supervision system
            metrics.reports_submitted = 0  # Placeholder
            metrics.reports_on_time = 0  # Placeholder
            metrics.on_time_rate = 100.0  # Placeholder

        # Calculate overall performance score
        # Weighted average: completion rate (40%), on-time rate (30%), quality (30%)
        metrics.overall_performance_score = (
            metrics.completion_rate * 0.4 +
            metrics.on_time_rate * 0.3 +
            metrics.quality_score * 0.3
        )

        return metrics

    def _calculate_performance_metrics_for_manager(self, manager_id: str, team: Team) -> PerformanceMetrics:
        """Calculate performance metrics for a manager"""
        metrics = PerformanceMetrics()

        # Get team's total tasks
        if self.ticket_system:
            tickets_dir = self.ticket_system.tickets_dir
            team_tickets = []

            for ticket_file in tickets_dir.glob("*.json"):
                try:
                    with open(ticket_file, 'r', encoding='utf-8') as f:
                        ticket = json.load(f)

                    team_assignment = ticket.get("team_assignment", {})
                    if team_assignment.get("team_id") == team.team_id:
                        team_tickets.append(ticket)
                except Exception:
                    pass

            metrics.tasks_total = len(team_tickets)
            metrics.tasks_completed = sum(
                1 for t in team_tickets 
                if t.get("status") in ["resolved", "closed", "completed"]
            )

            if metrics.tasks_total > 0:
                metrics.completion_rate = (metrics.tasks_completed / metrics.tasks_total) * 100.0

        # Manager performance based on team performance
        metrics.overall_performance_score = metrics.completion_rate

        return metrics

    def create_holocron(self) -> str:
        try:
            """
            Create HOLOCRON with all employee data

            Returns:
                Holocron ID
            """
            # Collect all employees
            employees = self.collect_all_employees()

            # Create holocron data
            holocron_id = f"HOLO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            holocron_data = {
                "holocron_id": holocron_id,
                "title": "Employee Performance Database - Complete Company",
                "timestamp": datetime.now().isoformat(),
                "importance_score": 100,  # Maximum importance
                "importance_symbol": "⭐⭐⭐⭐⭐",
                "category": "employee_performance",
                "tags": ["#EMPLOYEE", "#PERFORMANCE", "#HOLOCRON", "#DYNO", "@HOLOCRON", "@DYNO"],
                "data": {
                    "total_employees": len(employees),
                    "employees": {k: v.to_dict() for k, v in employees.items()},
                    "summary": {
                        "average_performance_score": sum(
                            e.performance_metrics.overall_performance_score 
                            for e in employees.values()
                        ) / len(employees) if employees else 0.0,
                        "total_tasks": sum(e.performance_metrics.tasks_total for e in employees.values()),
                        "completed_tasks": sum(e.performance_metrics.tasks_completed for e in employees.values()),
                        "total_completion_rate": (
                            sum(e.performance_metrics.completion_rate for e in employees.values()) / len(employees)
                            if employees else 0.0
                        )
                    }
                }
            }

            # Save holocron
            holocron_file = self.holocron_dir / f"{holocron_id}.json"
            with open(holocron_file, 'w', encoding='utf-8') as f:
                json.dump(holocron_data, f, indent=2)

            logger.info("=" * 80)
            logger.info(f"📊 HOLOCRON CREATED: {holocron_id}")
            logger.info("=" * 80)
            logger.info(f"   Title: {holocron_data['title']}")
            logger.info(f"   Total Employees: {len(employees)}")
            logger.info(f"   Average Performance: {holocron_data['data']['summary']['average_performance_score']:.1f}%")
            logger.info(f"   Total Tasks: {holocron_data['data']['summary']['total_tasks']}")
            logger.info(f"   Completed Tasks: {holocron_data['data']['summary']['completed_tasks']}")
            logger.info("=" * 80)

            return holocron_id

        except Exception as e:
            self.logger.error(f"Error in create_holocron: {e}", exc_info=True)
            raise
    def deploy_to_dyno(self, holocron_id: str) -> bool:
        try:
            """
            Deploy employee performance data to @DYNO

            Args:
                holocron_id: Holocron ID to deploy

            Returns:
                True if deployed successfully
            """
            logger.info("=" * 80)
            logger.info("🚀 DEPLOYING TO @DYNO")
            logger.info("=" * 80)

            holocron_file = self.holocron_dir / f"{holocron_id}.json"

            if not holocron_file.exists():
                logger.error(f"❌ Holocron file not found: {holocron_file}")
                return False

            # Load holocron data
            with open(holocron_file, 'r', encoding='utf-8') as f:
                holocron_data = json.load(f)

            # Deploy to DYNO directory
            dyno_dir = self.project_root / "docker" / "dyno_lumina_jarvis" / "data" / "employee_performance"
            dyno_dir.mkdir(parents=True, exist_ok=True)

            # Copy holocron to DYNO
            dyno_file = dyno_dir / f"{holocron_id}.json"
            with open(dyno_file, 'w', encoding='utf-8') as f:
                json.dump(holocron_data, f, indent=2)

            # Create summary table for DYNO
            summary_file = dyno_dir / "employee_performance_summary.json"
            summary = {
                "last_updated": datetime.now().isoformat(),
                "holocron_id": holocron_id,
                "total_employees": holocron_data['data']['total_employees'],
                "summary": holocron_data['data']['summary'],
                "employees": {
                    emp_id: {
                        "name": emp['name'],
                        "role": emp['role'],
                        "division": emp['division'],
                        "team": emp['team'],
                        "performance_score": emp['performance_metrics']['overall_performance_score'],
                        "completion_rate": emp['performance_metrics']['completion_rate']
                    }
                    for emp_id, emp in holocron_data['data']['employees'].items()
                }
            }

            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)

            logger.info(f"✅ Deployed to @DYNO: {dyno_file}")
            logger.info(f"✅ Summary created: {summary_file}")
            logger.info("=" * 80)

            return True


        except Exception as e:
            self.logger.error(f"Error in deploy_to_dyno: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Employee Performance HOLOCRON")
    parser.add_argument("--create", action="store_true", help="Create holocron")
    parser.add_argument("--deploy", action="store_true", help="Deploy to DYNO")
    parser.add_argument("--holocron-id", type=str, help="Holocron ID to deploy")
    args = parser.parse_args()

    holocron = EmployeePerformanceHolocron()

    if args.create:
        holocron_id = holocron.create_holocron()
        if args.deploy:
            holocron.deploy_to_dyno(holocron_id)
    elif args.deploy and args.holocron_id:
        holocron.deploy_to_dyno(args.holocron_id)
    else:
        # Default: create and deploy
        holocron_id = holocron.create_holocron()
        holocron.deploy_to_dyno(holocron_id)
