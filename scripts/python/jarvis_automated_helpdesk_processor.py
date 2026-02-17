#!/usr/bin/env python3
"""
JARVIS Automated Helpdesk Processor - End-to-End Workflow
Ensures no gaps in automated helpdesk processing from ticket creation to resolution.

Workflow:
1. Monitor for new tickets
2. Auto-assign via C-3PO
3. Route to appropriate teams
4. Track progress
5. Auto-resolve when possible
6. Report status

Tags: #JARVIS #HELPDESK #AUTOMATION #END2END #WORKFLOW @helpdesk @c3po
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem, TicketStatus, TicketPriority
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    SYSTEMS_AVAILABLE = False
    get_logger("JARVISAutomatedHelpdeskProcessor").warning(f"Systems not available: {e}")

logger = get_logger("JARVISAutomatedHelpdeskProcessor")


@dataclass
class WorkflowStep:
    """Workflow step tracking"""
    step_name: str
    status: str  # pending, in_progress, completed, failed
    timestamp: str
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class JARVISAutomatedHelpdeskProcessor:
    """
    Automated Helpdesk Processor - End-to-End Workflow

    Ensures complete automation from ticket creation to resolution:
    1. Ticket Detection → Auto-assignment
    2. Team Routing → Processing
    3. Progress Tracking → Resolution
    4. Status Reporting → Completion
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize automated processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.tickets_dir = self.project_root / "data" / "pr_tickets" / "tickets"
        self.workflow_dir = self.project_root / "data" / "helpdesk" / "workflows"
        self.workflow_dir.mkdir(parents=True, exist_ok=True)

        # Initialize systems
        if SYSTEMS_AVAILABLE:
            self.ticket_system = JARVISHelpdeskTicketSystem(project_root)
            self.assigner = C3POTicketAssigner(project_root)
        else:
            self.ticket_system = None
            self.assigner = None

        # Processing state
        self.processed_tickets = set()
        self.workflow_history: List[WorkflowStep] = []

        logger.info("✅ JARVIS Automated Helpdesk Processor initialized")

    def process_all_tickets(self) -> Dict[str, Any]:
        """
        Process all tickets end-to-end.

        Returns:
            Processing results
        """
        logger.info("="*80)
        logger.info("🔄 PROCESSING ALL TICKETS - END-TO-END")
        logger.info("="*80)

        results = {
            'processed': 0,
            'assigned': 0,
            'resolved': 0,
            'failed': 0,
            'gaps_found': [],
            'workflow_steps': []
        }

        # Step 1: Find all unassigned tickets
        step1 = WorkflowStep(
            step_name="ticket_detection",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        self.workflow_history.append(step1)

        unassigned_tickets = self._find_unassigned_tickets()
        step1.details = {'found': len(unassigned_tickets)}
        step1.status = "completed"

        logger.info(f"📋 Found {len(unassigned_tickets)} unassigned tickets")
        results['workflow_steps'].append(asdict(step1))

        # Step 2: Auto-assign via C-3PO
        if unassigned_tickets and self.assigner:
            step2 = WorkflowStep(
                step_name="auto_assignment",
                status="in_progress",
                timestamp=datetime.now().isoformat()
            )
            self.workflow_history.append(step2)

            assignment_result = self.assigner.assign_all_unassigned_tickets()
            assigned_count = assignment_result.get('successful', 0)
            step2.details = assignment_result
            step2.status = "completed" if assigned_count > 0 else "failed"

            logger.info(f"✅ Assigned {assigned_count} tickets")
            results['assigned'] = assigned_count
            results['workflow_steps'].append(asdict(step2))

            # Check for gaps
            if assignment_result.get('failed', 0) > 0:
                gap = {
                    'type': 'assignment_failure',
                    'count': assignment_result.get('failed', 0),
                    'details': assignment_result.get('results', [])
                }
                results['gaps_found'].append(gap)
                logger.warning(f"⚠️  GAP: {gap['count']} tickets failed assignment")

        # Step 3: Check for tickets needing processing
        step3 = WorkflowStep(
            step_name="processing_check",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        self.workflow_history.append(step3)

        assigned_tickets = self._find_assigned_tickets()
        step3.details = {'assigned_tickets': len(assigned_tickets)}
        step3.status = "completed"

        logger.info(f"🔧 Found {len(assigned_tickets)} assigned tickets")
        results['workflow_steps'].append(asdict(step3))

        # Step 4: Track progress and identify gaps
        step4 = WorkflowStep(
            step_name="progress_tracking",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        self.workflow_history.append(step4)

        progress_gaps = self._identify_progress_gaps(assigned_tickets)
        if progress_gaps:
            results['gaps_found'].extend(progress_gaps)
            logger.warning(f"⚠️  Found {len(progress_gaps)} progress gaps")

        step4.details = {'gaps_found': len(progress_gaps)}
        step4.status = "completed"
        results['workflow_steps'].append(asdict(step4))

        # Step 5: Auto-resolve where possible
        step5 = WorkflowStep(
            step_name="auto_resolution",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        self.workflow_history.append(step5)

        auto_resolved = self._attempt_auto_resolution(assigned_tickets)
        step5.details = {'resolved': len(auto_resolved)}
        step5.status = "completed"

        logger.info(f"✅ Auto-resolved {len(auto_resolved)} tickets")
        results['resolved'] = len(auto_resolved)
        results['workflow_steps'].append(asdict(step5))

        # Step 6: Manager Supervision & Reporting (@PEAK)
        step6 = WorkflowStep(
            step_name="manager_supervision_reporting",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        self.workflow_history.append(step6)

        try:
            from team_management_supervision import TeamManagementSupervision
            supervision = TeamManagementSupervision(self.project_root)
            supervision_results = supervision.process_all_managers()
            step6.details = supervision_results
            step6.status = "completed"
            logger.info("✅ Manager supervision and reporting completed")
            results['supervision_reports'] = supervision_results.get('reports_sent', 0)
        except Exception as e:
            logger.warning(f"⚠️  Manager supervision failed: {e}")
            step6.details = {'error': str(e)}
            step6.status = "failed"
            results['supervision_reports'] = 0

        results['workflow_steps'].append(asdict(step6))

        # Summary
        results['processed'] = len(unassigned_tickets) + len(assigned_tickets)
        results['total_gaps'] = len(results['gaps_found'])

        logger.info("="*80)
        logger.info("📊 PROCESSING SUMMARY")
        logger.info("="*80)
        logger.info(f"   Processed: {results['processed']}")
        logger.info(f"   Assigned: {results['assigned']}")
        logger.info(f"   Resolved: {results['resolved']}")
        logger.info(f"   Gaps Found: {results['total_gaps']}")
        logger.info("="*80)

        # Save workflow history
        self._save_workflow_history()

        return results

    def _find_unassigned_tickets(self) -> List[Dict[str, Any]]:
        """Find all unassigned tickets"""
        tickets = []

        for ticket_file in self.tickets_dir.glob("HELPDESK-*.json"):
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)

                if not ticket.get("team_assignment"):
                    tickets.append(ticket)
            except Exception as e:
                logger.debug(f"Failed to read {ticket_file.name}: {e}")

        return tickets

    def _find_assigned_tickets(self) -> List[Dict[str, Any]]:
        """Find all assigned tickets"""
        tickets = []

        for ticket_file in self.tickets_dir.glob("HELPDESK-*.json"):
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)

                if ticket.get("team_assignment") and ticket.get("status") != "resolved":
                    tickets.append(ticket)
            except Exception as e:
                logger.debug(f"Failed to read {ticket_file.name}: {e}")

        return tickets

    def _identify_progress_gaps(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify gaps in ticket progress"""
        gaps = []

        for ticket in tickets:
            ticket_id = ticket.get("ticket_number", "unknown")
            status = ticket.get("status", "unknown")
            created_at = ticket.get("created_at", "")
            team_assignment = ticket.get("team_assignment", {})

            # Gap 1: Assigned but no progress
            if status == "assigned":
                try:
                    assigned_at = team_assignment.get("assigned_at", created_at)
                    assigned_time = datetime.fromisoformat(assigned_at.replace('Z', '+00:00'))
                    if isinstance(assigned_time, datetime):
                        # Remove timezone for comparison
                        assigned_time = assigned_time.replace(tzinfo=None)

                    now = datetime.now()
                    hours_since_assigned = (now - assigned_time).total_seconds() / 3600

                    if hours_since_assigned > 24:  # No progress in 24 hours
                        gaps.append({
                            'type': 'stalled_ticket',
                            'ticket_id': ticket_id,
                            'hours_since_assigned': hours_since_assigned,
                            'team': team_assignment.get('team_name', 'unknown')
                        })
                except Exception as e:
                    logger.debug(f"Failed to check progress for {ticket_id}: {e}")

            # Gap 2: Missing required fields
            # Check if team_assignment exists and has required sub-fields
            team_assignment = ticket.get("team_assignment", {})
            required_fields = []

            if not team_assignment:
                required_fields.append('team_assignment')
            else:
                # Check sub-fields within team_assignment
                if not team_assignment.get('primary_assignee'):
                    required_fields.append('primary_assignee')
                if not team_assignment.get('team_id'):
                    required_fields.append('team_id')

            if not ticket.get('status'):
                required_fields.append('status')

            if required_fields:
                gaps.append({
                    'type': 'missing_fields',
                    'ticket_id': ticket_id,
                    'missing': required_fields,
                    'has_team_assignment': bool(team_assignment)
                })

        return gaps

    def _attempt_auto_resolution(self, tickets: List[Dict[str, Any]]) -> List[str]:
        """Attempt to auto-resolve tickets where possible"""
        resolved = []

        for ticket in tickets:
            ticket_id = ticket.get("ticket_number", "unknown")

            # Check if ticket can be auto-resolved
            # This would integrate with actual resolution logic
            # For now, just track the capability

            # Example: If ticket has resolution metadata, mark as resolved
            metadata = ticket.get("metadata", {})
            if metadata.get("auto_resolved"):
                try:
                    if self.ticket_system:
                        self.ticket_system.update_ticket_status(
                            ticket_id.replace("HELPDESK-", "PM"),
                            TicketStatus.RESOLVED,
                            "Auto-resolved by automated processor"
                        )
                    resolved.append(ticket_id)
                except Exception as e:
                    logger.debug(f"Failed to auto-resolve {ticket_id}: {e}")

        return resolved

    def _save_workflow_history(self) -> None:
        """Save workflow history"""
        history_file = self.workflow_dir / f"workflow_history_{datetime.now().strftime('%Y%m%d')}.jsonl"

        try:
            with open(history_file, 'a', encoding='utf-8') as f:
                for step in self.workflow_history:
                    f.write(json.dumps(asdict(step), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to save workflow history: {e}")

    def generate_gap_report(self) -> str:
        """Generate report of identified gaps"""
        results = self.process_all_tickets()

        lines = []
        lines.append("📊 **Helpdesk Workflow Gap Report**")
        lines.append("")
        lines.append(f"**Generated**: {datetime.now().isoformat()}")
        lines.append("")
        lines.append(f"**Total Gaps Found**: {results['total_gaps']}")
        lines.append("")

        if results['gaps_found']:
            lines.append("**Gaps Identified:**")
            for i, gap in enumerate(results['gaps_found'], 1):
                lines.append(f"")
                lines.append(f"{i}. **{gap.get('type', 'unknown')}**")
                if gap.get('ticket_id'):
                    lines.append(f"   - Ticket: {gap['ticket_id']}")
                if gap.get('count'):
                    lines.append(f"   - Count: {gap['count']}")
                if gap.get('hours_since_assigned'):
                    lines.append(f"   - Stalled for: {gap['hours_since_assigned']:.1f} hours")
                if gap.get('team'):
                    lines.append(f"   - Team: {gap['team']}")
        else:
            lines.append("✅ **No gaps found - workflow is complete!**")

        lines.append("")
        lines.append("**Workflow Steps:**")
        for step in results['workflow_steps']:
            status_icon = "✅" if step['status'] == "completed" else "⏳" if step['status'] == "in_progress" else "❌"
            lines.append(f"   {status_icon} {step['step_name']}: {step['status']}")

        return "\n".join(lines)

    def run_continuous_monitoring(self, interval: int = 300) -> None:
        """
        Run continuous monitoring and processing.

        Args:
            interval: Check interval in seconds (default: 5 minutes)
        """
        logger.info(f"🔄 Starting continuous monitoring (interval: {interval}s)")

        while True:
            try:
                results = self.process_all_tickets()

                if results['total_gaps'] > 0:
                    logger.warning(f"⚠️  {results['total_gaps']} gaps found in workflow")

                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(interval)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Automated Helpdesk Processor")
    parser.add_argument('--process', action='store_true', help='Process all tickets once')
    parser.add_argument('--monitor', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=300, help='Monitoring interval in seconds')
    parser.add_argument('--gap-report', action='store_true', help='Generate gap report')

    args = parser.parse_args()

    processor = JARVISAutomatedHelpdeskProcessor()

    if args.gap_report or not any([args.process, args.monitor]):
        report = processor.generate_gap_report()
        print(report)

    if args.process:
        results = processor.process_all_tickets()
        print(f"\n✅ Processed {results['processed']} tickets")
        if results['total_gaps'] > 0:
            print(f"⚠️  Found {results['total_gaps']} gaps")

    if args.monitor:
        processor.run_continuous_monitoring(args.interval)


if __name__ == "__main__":


    main()