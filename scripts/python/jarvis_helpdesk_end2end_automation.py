#!/usr/bin/env python3
"""
JARVIS Helpdesk End-to-End Automation
Ensures complete automated processing from ticket creation to resolution.

This system eliminates gaps in the helpdesk workflow:
1. Auto-creates HELPDESK tickets from PM tickets
2. Auto-routes via C-3PO
3. Auto-assigns to teams
4. Auto-tracks resolution
5. Auto-updates status

Tags: #HELPDESK #AUTOMATION #END2END #C3PO #WORKFLOW @helpdesk @c3po
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem, TicketStatus, TicketPriority
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner
except ImportError as e:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    JARVISHelpdeskTicketSystem = None
    C3POTicketAssigner = None

logger = get_logger("JARVISHelpdeskEnd2EndAutomation")


class HelpdeskEnd2EndAutomation:
    """
    End-to-end automated helpdesk processing.

    Workflow:
    1. Monitor for new tickets (PM format or direct reports)
    2. Convert PM tickets to HELPDESK format if needed
    3. Auto-route via C-3PO
    4. Auto-assign to teams
    5. Monitor resolution progress
    6. Auto-update status
    7. Track completion
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize end-to-end automation."""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # Initialize subsystems
        if JARVISHelpdeskTicketSystem:
            self.ticket_system = JARVISHelpdeskTicketSystem(project_root)
        else:
            self.ticket_system = None
            logger.warning("⚠️  Ticket system not available")

        if C3POTicketAssigner:
            self.c3po_assigner = C3POTicketAssigner(project_root)
        else:
            self.c3po_assigner = None
            logger.warning("⚠️  C-3PO assigner not available")

        # Directories
        self.pm_tickets_dir = project_root / "data" / "helpdesk" / "tickets"
        self.helpdesk_tickets_dir = project_root / "data" / "pr_tickets" / "tickets"
        self.helpdesk_tickets_dir.mkdir(parents=True, exist_ok=True)

        # State tracking
        self.state_file = project_root / "data" / "helpdesk" / "automation_state.json"
        self._load_state()

        logger.info("✅ Helpdesk End-to-End Automation initialized")

    def _load_state(self) -> None:
        """Load automation state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")
                self.state = {"processed_pm_tickets": [], "last_check": None}
        else:
            self.state = {"processed_pm_tickets": [], "last_check": None}

    def _save_state(self) -> None:
        """Save automation state."""
        try:
            self.state["last_check"] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def process_all_tickets(self) -> Dict[str, Any]:
        """
        Process all tickets end-to-end.

        Returns:
            Processing results
        """
        logger.info("="*80)
        logger.info("🔄 HELPDESK END-TO-END AUTOMATION")
        logger.info("="*80)

        results = {
            "pm_tickets_processed": 0,
            "helpdesk_tickets_created": 0,
            "tickets_routed": 0,
            "tickets_assigned": 0,
            "errors": []
        }

        # Step 1: Process PM tickets → HELPDESK tickets
        if self.ticket_system:
            pm_tickets = self._find_pm_tickets()
            for pm_ticket in pm_tickets:
                if pm_ticket.ticket_id not in self.state["processed_pm_tickets"]:
                    try:
                        helpdesk_ticket = self._convert_pm_to_helpdesk(pm_ticket)
                        if helpdesk_ticket:
                            results["helpdesk_tickets_created"] += 1
                            results["pm_tickets_processed"] += 1
                            self.state["processed_pm_tickets"].append(pm_ticket.ticket_id)
                    except Exception as e:
                        logger.error(f"Failed to convert PM ticket {pm_ticket.ticket_id}: {e}")
                        results["errors"].append(f"PM {pm_ticket.ticket_id}: {e}")

        # Step 2: Auto-route unassigned HELPDESK tickets
        if self.c3po_assigner:
            unassigned = self._find_unassigned_helpdesk_tickets()
            for ticket_file in unassigned:
                try:
                    ticket_number = ticket_file.stem
                    result = self.c3po_assigner.assign_ticket_to_team(
                        ticket_number,
                        auto_detect=True
                    )
                    if result.get("success"):
                        results["tickets_routed"] += 1
                        results["tickets_assigned"] += 1
                    else:
                        results["errors"].append(f"HELPDESK {ticket_number}: {result.get('error')}")
                except Exception as e:
                    logger.error(f"Failed to route {ticket_file.name}: {e}")
                    results["errors"].append(f"{ticket_file.name}: {e}")

        # Save state
        self._save_state()

        # Summary
        logger.info("")
        logger.info("="*80)
        logger.info("📊 PROCESSING SUMMARY")
        logger.info("="*80)
        logger.info(f"   PM Tickets Processed: {results['pm_tickets_processed']}")
        logger.info(f"   HELPDESK Tickets Created: {results['helpdesk_tickets_created']}")
        logger.info(f"   Tickets Routed: {results['tickets_routed']}")
        logger.info(f"   Tickets Assigned: {results['tickets_assigned']}")
        if results["errors"]:
            logger.warning(f"   Errors: {len(results['errors'])}")
            for error in results["errors"][:5]:  # Show first 5
                logger.warning(f"      - {error}")
        logger.info("="*80)

        return results

    def _find_pm_tickets(self) -> List[Any]:
        """Find PM format tickets that need processing."""
        if not self.ticket_system:
            return []

        tickets = []
        if self.pm_tickets_dir.exists():
            for ticket_file in self.pm_tickets_dir.glob("PM*.json"):
                try:
                    ticket = self.ticket_system.get_ticket(ticket_file.stem)
                    if ticket and ticket.status == TicketStatus.OPEN:
                        tickets.append(ticket)
                except Exception:
                    pass
        return tickets

    def _convert_pm_to_helpdesk(self, pm_ticket: Any) -> Optional[Dict[str, Any]]:
        """
        Convert PM ticket to HELPDESK format.

        Args:
            pm_ticket: PM format ticket

        Returns:
            HELPDESK ticket data or None
        """
        # Find next HELPDESK number
        existing = list(self.helpdesk_tickets_dir.glob("HELPDESK-*.json"))
        if existing:
            numbers = []
            for t in existing:
                try:
                    num = int(t.stem.split("-")[1])
                    numbers.append(num)
                except:
                    pass
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1

        helpticket_id = f"HELPDESK-{next_num:04d}"
        helpticket_file = self.helpdesk_tickets_dir / f"{helpticket_id}.json"

        # Convert ticket
        helpticket = {
            "ticket_number": helpticket_id,
            "title": pm_ticket.title,
            "description": pm_ticket.description,
            "priority": pm_ticket.priority.value,
            "severity": pm_ticket.priority.value,  # Map priority to severity
            "status": "open",
            "change_type": pm_ticket.issue_type,
            "component": pm_ticket.component,
            "issue_type": pm_ticket.issue_type,
            "created_at": pm_ticket.created_at,
            "created_by": pm_ticket.created_by,
            "reported_by": pm_ticket.created_by,
            "tags": pm_ticket.tags or [],
            "linked_tickets": [pm_ticket.ticket_id],
            "metadata": {
                "original_ticket": pm_ticket.ticket_id,
                "converted_at": datetime.now().isoformat(),
                "converted_by": "automation"
            }
        }

        # Save HELPDESK ticket
        with open(helpticket_file, 'w', encoding='utf-8') as f:
            json.dump(helpticket, f, indent=2)

        logger.info(f"✅ Converted {pm_ticket.ticket_id} → {helpticket_id}")
        return helpticket

    def _find_unassigned_helpdesk_tickets(self) -> List[Path]:
        """Find HELPDESK tickets that need assignment."""
        unassigned = []

        for ticket_file in self.helpdesk_tickets_dir.glob("HELPDESK-*.json"):
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)

                # Check if assigned
                if not ticket.get("team_assignment") and ticket.get("status") != "closed":
                    unassigned.append(ticket_file)
            except Exception:
                pass

        return unassigned

    def monitor_and_process(self, interval: int = 300) -> None:
        """
        Continuously monitor and process tickets.

        Args:
            interval: Check interval in seconds (default: 5 minutes)
        """
        import time

        logger.info(f"🔄 Starting continuous monitoring (interval: {interval}s)")

        while True:
            try:
                self.process_all_tickets()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(interval)

    def verify_end2end(self) -> Dict[str, Any]:
        try:
            """
            Verify end-to-end workflow has no gaps.

            Returns:
                Verification results
            """
            logger.info("="*80)
            logger.info("🔍 VERIFYING END-TO-END WORKFLOW")
            logger.info("="*80)

            gaps = []
            checks = {
                "ticket_system_available": self.ticket_system is not None,
                "c3po_assigner_available": self.c3po_assigner is not None,
                "pm_tickets_dir_exists": self.pm_tickets_dir.exists(),
                "helpdesk_tickets_dir_exists": self.helpdesk_tickets_dir.exists(),
                "state_file_writable": self._test_write(self.state_file.parent),
            }

            # Check for gaps
            if not checks["ticket_system_available"]:
                gaps.append("Ticket system not available")
            if not checks["c3po_assigner_available"]:
                gaps.append("C-3PO assigner not available")
            if not checks["pm_tickets_dir_exists"]:
                gaps.append("PM tickets directory missing")
            if not checks["helpdesk_tickets_dir_exists"]:
                gaps.append("HELPDESK tickets directory missing")

            # Check for unprocessed tickets
            unprocessed_pm = len(self._find_pm_tickets())
            unassigned_helpdesk = len(self._find_unassigned_helpdesk_tickets())

            if unprocessed_pm > 0:
                gaps.append(f"{unprocessed_pm} unprocessed PM tickets")
            if unassigned_helpdesk > 0:
                gaps.append(f"{unassigned_helpdesk} unassigned HELPDESK tickets")

            result = {
                "checks": checks,
                "gaps": gaps,
                "unprocessed_pm": unprocessed_pm,
                "unassigned_helpdesk": unassigned_helpdesk,
                "all_checks_passed": len(gaps) == 0
            }

            # Report
            logger.info("")
            for check, passed in checks.items():
                status = "✅" if passed else "❌"
                logger.info(f"   {status} {check}: {passed}")

            logger.info("")
            if gaps:
                logger.warning(f"⚠️  Found {len(gaps)} gap(s):")
                for gap in gaps:
                    logger.warning(f"      - {gap}")
            else:
                logger.info("✅ No gaps found - end-to-end workflow intact")

            logger.info("="*80)

            return result

        except Exception as e:
            self.logger.error(f"Error in verify_end2end: {e}", exc_info=True)
            raise
    def _test_write(self, path: Path) -> bool:
        """Test if path is writable."""
        try:
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
        except:
            return False


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Helpdesk End-to-End Automation")
    parser.add_argument('--process', action='store_true', help='Process all tickets once')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--interval', type=int, default=300, help='Monitoring interval (seconds)')
    parser.add_argument('--verify', action='store_true', help='Verify end-to-end workflow')

    args = parser.parse_args()

    automation = HelpdeskEnd2EndAutomation()

    if args.verify or not any([args.process, args.monitor]):
        automation.verify_end2end()

    if args.process:
        automation.process_all_tickets()

    if args.monitor:
        automation.monitor_and_process(args.interval)


if __name__ == "__main__":


    main()