#!/usr/bin/env python3
"""
Mark Ticket as In Progress (Worked)
Updates ticket status from "assigned" to "in_progress" to show active work.

Tags: #JARVIS #HELPDESK #TICKET #STATUS @helpdesk @r2d2
"""

import json
import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MarkTicketInProgress")


def mark_ticket_in_progress(ticket_number: str, assignee: str = "@r2d2") -> bool:
    """
    Mark ticket as in_progress (being worked on).

    Args:
        ticket_number: Ticket ID (e.g., HELPDESK-0011)
        assignee: Who is working on it

    Returns:
        True if successful
    """
    project_root = Path(__file__).parent.parent.parent
    tickets_dir = project_root / "data" / "pr_tickets" / "tickets"
    ticket_file = tickets_dir / f"{ticket_number}.json"

    if not ticket_file.exists():
        logger.error(f"❌ Ticket not found: {ticket_number}")
        return False

    try:
        # Load ticket
        with open(ticket_file, 'r', encoding='utf-8') as f:
            ticket = json.load(f)

        # Update status
        old_status = ticket.get('status', 'unknown')
        ticket['status'] = 'in_progress'
        ticket['in_progress_at'] = datetime.now().isoformat()
        ticket['in_progress_by'] = assignee

        # Add work log entry
        if 'work_log' not in ticket:
            ticket['work_log'] = []

        ticket['work_log'].append({
            'action': 'started_work',
            'status_change': f"{old_status} → in_progress",
            'timestamp': datetime.now().isoformat(),
            'by': assignee,
            'note': 'R2-D2 started working on this ticket'
        })

        # Update metadata
        if 'metadata' not in ticket:
            ticket['metadata'] = {}
        ticket['metadata']['work_started'] = True
        ticket['metadata']['work_started_at'] = datetime.now().isoformat()
        ticket['metadata']['work_started_by'] = assignee

        # Save updated ticket
        with open(ticket_file, 'w', encoding='utf-8') as f:
            json.dump(ticket, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Ticket {ticket_number} marked as IN PROGRESS")
        logger.info(f"   Status: {old_status} → in_progress")
        logger.info(f"   Assigned to: {assignee}")
        logger.info(f"   Started at: {ticket['in_progress_at']}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to update ticket {ticket_number}: {e}", exc_info=True)
        return False


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Mark Ticket as In Progress")
    parser.add_argument('ticket', help='Ticket number (e.g., HELPDESK-0011)')
    parser.add_argument('--assignee', default='@r2d2', help='Who is working on it')

    args = parser.parse_args()

    logger.info("="*80)
    logger.info("🔧 MARKING TICKET AS IN PROGRESS")
    logger.info("="*80)
    logger.info("")

    success = mark_ticket_in_progress(args.ticket, args.assignee)

    if success:
        logger.info("")
        logger.info("✅ Ticket status updated - R2-D2 is now working on it")
        return 0
    else:
        logger.error("")
        logger.error("❌ Failed to update ticket status")
        return 1


if __name__ == "__main__":


    sys.exit(main())