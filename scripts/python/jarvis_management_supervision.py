#!/usr/bin/env python3
"""
JARVIS Management Supervision System
Top-down management oversight - "boots on the ground" style
Active supervision of all delegated tasks and SLAs

Tags: #MANAGEMENT #SUPERVISION #DELEGATION #OVERSIGHT #BOOTS_ON_GROUND @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_sla_management_system import JARVISSLAManagementSystem
    from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("JARVISManagementSupervision")


class JARVISManagementSupervision:
    """
    JARVIS Management Supervision System

    Active top-down management - "boots on the ground" style
    Supervises all delegated tasks, SLAs, and team activities
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Management Supervision System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.sla_system = JARVISSLAManagementSystem(project_root)
        self.helpdesk_system = JARVISHelpdeskTicketSystem(project_root)

        logger.info("✅ JARVIS Management Supervision System initialized")
        logger.info("   Philosophy: Active supervision - 'boots on the ground'")
        logger.info("   Management Style: Top-down oversight")

    def supervise_slas(self) -> Dict[str, Any]:
        """Supervise all SLAs - active management oversight"""
        logger.info("=" * 80)
        logger.info("👔 MANAGEMENT SUPERVISION: SLA Oversight")
        logger.info("=" * 80)
        logger.info("   Active supervision - 'boots on the ground' management")

        # Monitor SLAs
        sla_summary = self.sla_system.monitor_slas()

        # Get critical items
        dashboard = self.sla_system.get_management_dashboard()

        # Management actions required
        actions_required = []

        # Expiring SLAs - require management attention
        expiring = self.sla_system.check_expiring_slas()
        for sla in expiring:
            actions_required.append({
                "action": "review_expiring_sla",
                "sla_id": sla.sla_id,
                "title": sla.title,
                "team_id": sla.team_id,
                "priority": sla.priority.value,
                "urgency": "high" if sla.priority in ["critical", "high"] else "medium"
            })

        # Expired SLAs - require immediate management intervention
        expired = self.sla_system.check_expired_slas()
        for sla in expired:
            actions_required.append({
                "action": "intervene_expired_sla",
                "sla_id": sla.sla_id,
                "title": sla.title,
                "team_id": sla.team_id,
                "priority": "critical",
                "urgency": "immediate"
            })

        # Unserviced SLAs - require management escalation
        unserviced = self.sla_system.check_unserviced_slas()
        for sla in unserviced:
            actions_required.append({
                "action": "escalate_unserviced_sla",
                "sla_id": sla.sla_id,
                "title": sla.title,
                "team_id": sla.team_id,
                "priority": "critical",
                "urgency": "immediate"
            })

        supervision_report = {
            "timestamp": datetime.now().isoformat(),
            "supervision_type": "sla_oversight",
            "sla_summary": sla_summary,
            "critical_items": dashboard.get("critical_items", []),
            "actions_required": actions_required,
            "management_intervention_needed": len(actions_required) > 0
        }

        logger.info(f"\n📊 Management Supervision Summary:")
        logger.info(f"   Actions Required: {len(actions_required)}")
        logger.info(f"   Management Intervention Needed: {supervision_report['management_intervention_needed']}")

        if actions_required:
            logger.warning("\n⚠️  MANAGEMENT ACTIONS REQUIRED:")
            for action in actions_required:
                logger.warning(f"   {action['action']}: {action['sla_id']} - {action['title']}")
                logger.warning(f"      Team: {action['team_id']} | Urgency: {action['urgency']}")

        return supervision_report

    def supervise_tickets(self) -> Dict[str, Any]:
        """Supervise helpdesk tickets - active management oversight"""
        logger.info("=" * 80)
        logger.info("👔 MANAGEMENT SUPERVISION: Ticket Oversight")
        logger.info("=" * 80)

        # Get all tickets
        tickets_dir = self.project_root / "data" / "helpdesk" / "tickets"
        if not tickets_dir.exists():
            return {"status": "no_tickets", "tickets": []}

        tickets = []
        for ticket_file in tickets_dir.glob("PM*.json"):
            try:
                with open(ticket_file, 'r') as f:
                    ticket = json.load(f)
                    tickets.append(ticket)
            except:
                pass

        # Categorize by status and priority
        by_status = {}
        by_priority = {}
        by_team = {}
        overdue = []
        stale = []  # No activity for > 48 hours

        now = datetime.now()

        for ticket in tickets:
            status = ticket.get("status", "unknown")
            priority = ticket.get("priority", "medium")
            team = ticket.get("team_assignment", {}).get("team_name", "unassigned")

            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1

            if team not in by_team:
                by_team[team] = []
            by_team[team].append(ticket)

            # Check for stale tickets
            created_at = ticket.get("created_at")
            if created_at:
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                hours_old = (now - created).total_seconds() / 3600

                if hours_old > 48 and status not in ["resolved", "closed"]:
                    stale.append({
                        "ticket_id": ticket.get("ticket_id"),
                        "title": ticket.get("title"),
                        "hours_old": hours_old,
                        "status": status
                    })

        supervision_report = {
            "timestamp": datetime.now().isoformat(),
            "supervision_type": "ticket_oversight",
            "total_tickets": len(tickets),
            "by_status": by_status,
            "by_priority": by_priority,
            "by_team": {team: len(tickets) for team, tickets in by_team.items()},
            "stale_tickets": stale,
            "management_intervention_needed": len(stale) > 0
        }

        logger.info(f"\n📊 Ticket Supervision Summary:")
        logger.info(f"   Total Tickets: {len(tickets)}")
        logger.info(f"   Stale Tickets (>48h): {len(stale)}")

        if stale:
            logger.warning("\n⚠️  STALE TICKETS REQUIRING ATTENTION:")
            for ticket in stale[:10]:  # Show first 10
                logger.warning(f"   {ticket['ticket_id']}: {ticket['title']} ({ticket['hours_old']:.1f}h old)")

        return supervision_report

    def notify_jarvis_management_issues(self) -> Dict[str, Any]:
        try:
            """Notify JARVIS of all management issues requiring attention"""
            logger.info("=" * 80)
            logger.info("📢 NOTIFYING JARVIS: Management Issues")
            logger.info("=" * 80)

            notifications = []

            # SLA issues
            sla_supervision = self.supervise_slas()
            if sla_supervision.get("management_intervention_needed"):
                notifications.append({
                    "type": "sla_issues",
                    "count": len(sla_supervision.get("actions_required", [])),
                    "details": sla_supervision
                })

            # Ticket issues
            ticket_supervision = self.supervise_tickets()
            if ticket_supervision.get("management_intervention_needed"):
                notifications.append({
                    "type": "ticket_issues",
                    "count": len(ticket_supervision.get("stale_tickets", [])),
                    "details": ticket_supervision
                })

            # Save notification
            notification_file = self.project_root / "data" / "system" / f"management_notifications_{datetime.now().strftime('%Y%m%d')}.json"
            notification_file.parent.mkdir(parents=True, exist_ok=True)

            notification_data = {
                "timestamp": datetime.now().isoformat(),
                "notifications": notifications,
                "total_issues": sum(n.get("count", 0) for n in notifications)
            }

            with open(notification_file, 'w') as f:
                json.dump(notification_data, f, indent=2, default=str)

            logger.info(f"📊 Total Management Issues: {notification_data['total_issues']}")
            logger.info(f"   ✅ Notifications saved: {notification_file}")

            return notification_data

        except Exception as e:
            self.logger.error(f"Error in notify_jarvis_management_issues: {e}", exc_info=True)
            raise
    def generate_management_report(self) -> Dict[str, Any]:
        try:
            """Generate comprehensive management report for top-down oversight"""
            logger.info("=" * 80)
            logger.info("📊 GENERATING MANAGEMENT REPORT")
            logger.info("=" * 80)
            logger.info("   Top-down supervision - 'boots on the ground'")

            # SLA supervision
            sla_report = self.supervise_slas()

            # Ticket supervision
            ticket_report = self.supervise_tickets()

            # Management dashboard
            sla_dashboard = self.sla_system.get_management_dashboard()

            # Comprehensive report
            report = {
                "timestamp": datetime.now().isoformat(),
                "report_type": "management_supervision",
                "management_philosophy": "Active supervision - 'boots on the ground'",
                "sla_supervision": sla_report,
                "ticket_supervision": ticket_report,
                "sla_dashboard": sla_dashboard,
                "summary": {
                    "sla_actions_required": len(sla_report.get("actions_required", [])),
                    "stale_tickets": len(ticket_report.get("stale_tickets", [])),
                    "total_management_interventions": (
                        len(sla_report.get("actions_required", [])) +
                        len(ticket_report.get("stale_tickets", []))
                    )
                }
            }

            # Save report
            report_file = self.project_root / "data" / "system" / f"management_supervision_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"\n📊 Management Report Summary:")
            logger.info(f"   SLA Actions Required: {report['summary']['sla_actions_required']}")
            logger.info(f"   Stale Tickets: {report['summary']['stale_tickets']}")
            logger.info(f"   Total Interventions: {report['summary']['total_management_interventions']}")
            logger.info(f"   ✅ Report saved: {report_file}")

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_management_report: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Management Supervision System")
    parser.add_argument("--supervise", action="store_true", help="Run full supervision")
    parser.add_argument("--slas", action="store_true", help="Supervise SLAs only")
    parser.add_argument("--tickets", action="store_true", help="Supervise tickets only")
    parser.add_argument("--notify", action="store_true", help="Notify JARVIS of issues")
    parser.add_argument("--report", action="store_true", help="Generate management report")

    args = parser.parse_args()

    print("="*80)
    print("👔 JARVIS MANAGEMENT SUPERVISION SYSTEM")
    print("="*80)
    print()
    print("Philosophy: Active supervision - 'boots on the ground'")
    print("Management Style: Top-down oversight")
    print()

    system = JARVISManagementSupervision()

    if args.supervise or (not args.slas and not args.tickets and not args.notify and not args.report):
        # Full supervision
        print("🔍 Running Full Management Supervision...")
        print()

        sla_report = system.supervise_slas()
        print()
        ticket_report = system.supervise_tickets()
        print()

        print("="*80)
        print("✅ SUPERVISION COMPLETE")
        print("="*80)

    elif args.slas:
        system.supervise_slas()

    elif args.tickets:
        system.supervise_tickets()

    elif args.notify:
        notifications = system.notify_jarvis_management_issues()
        print()
        print("="*80)
        print("✅ NOTIFICATIONS SENT")
        print("="*80)
        print(f"Total Issues: {notifications.get('total_issues', 0)}")

    elif args.report:
        report = system.generate_management_report()
        print()
        print("="*80)
        print("✅ MANAGEMENT REPORT GENERATED")
        print("="*80)


if __name__ == "__main__":


    main()