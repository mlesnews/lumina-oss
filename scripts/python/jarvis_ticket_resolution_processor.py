#!/usr/bin/env python3
"""
JARVIS Ticket Resolution Processor
Actually resolves tickets to decrease queue numbers.

Tags: #JARVIS #HELPDESK #RESOLUTION #QUEUE @helpdesk @c3po @r2d2
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISTicketResolutionProcessor")


class JARVISTicketResolutionProcessor:
    """
    Processes and resolves tickets to decrease queue numbers.

    Resolution criteria:
    - Test tickets can be auto-resolved
    - Tickets with resolution metadata
    - Tickets marked as completed by teams
    - Stale tickets that are no longer relevant
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize resolution processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.tickets_dir = self.project_root / "data" / "pr_tickets" / "tickets"

        logger.info("✅ JARVIS Ticket Resolution Processor initialized")

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        tickets = self._load_all_tickets()

        status = {
            'total': len(tickets),
            'open': 0,
            'assigned': 0,
            'in_progress': 0,
            'resolved': 0,
            'closed': 0,
            'by_team': {},
            'by_priority': {}
        }

        for ticket in tickets:
            ticket_status = ticket.get('status', 'open').lower()

            if ticket_status == 'resolved' or ticket_status == 'closed':
                status['resolved'] += 1
            elif ticket_status == 'in_progress':
                status['in_progress'] += 1
            elif ticket_status == 'assigned':
                status['assigned'] += 1
            else:
                status['open'] += 1

            # Count by team
            team_assignment = ticket.get('team_assignment', {})
            team_name = team_assignment.get('team_name', 'unassigned')
            if team_name not in status['by_team']:
                status['by_team'][team_name] = 0
            status['by_team'][team_name] += 1

            # Count by priority
            priority = ticket.get('priority', 'medium')
            if priority not in status['by_priority']:
                status['by_priority'][priority] = 0
            status['by_priority'][priority] += 1

        # Calculate active queue (non-resolved)
        status['active_queue'] = status['open'] + status['assigned'] + status['in_progress']

        return status

    def resolve_tickets(self, criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Resolve tickets based on criteria.

        Args:
            criteria: Resolution criteria (auto_resolve_test, auto_resolve_stale, etc.)

        Returns:
            Resolution results
        """
        if criteria is None:
            criteria = {
                'auto_resolve_test': True,
                'auto_resolve_stale_days': 30,
                'auto_resolve_completed': True
            }

        tickets = self._load_all_tickets()
        results = {
            'processed': 0,
            'resolved': 0,
            'failed': 0,
            'resolved_tickets': []
        }

        logger.info("="*80)
        logger.info("🔧 RESOLVING TICKETS")
        logger.info("="*80)

        for ticket in tickets:
            ticket_id = ticket.get('ticket_number', 'unknown')
            current_status = ticket.get('status', 'open').lower()

            # Skip already resolved tickets
            if current_status in ['resolved', 'closed']:
                continue

            results['processed'] += 1

            # Check resolution criteria
            should_resolve = False
            resolve_reason = ""

            # Criterion 1: Test tickets
            if criteria.get('auto_resolve_test', False):
                title = ticket.get('title', '').lower()
                description = ticket.get('description', '').lower()
                if 'test' in title or 'test' in description:
                    if 'test problem' in title or 'test' in title:
                        should_resolve = True
                        resolve_reason = "Test ticket - auto-resolved"

            # Criterion 2: Tickets with resolution metadata
            metadata = ticket.get('metadata', {})
            if metadata.get('resolved') or metadata.get('auto_resolved'):
                should_resolve = True
                resolve_reason = "Marked as resolved in metadata"

            # Criterion 3: Stale tickets (older than X days)
            if criteria.get('auto_resolve_stale_days'):
                try:
                    created_at = ticket.get('created_at', '')
                    if created_at:
                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if isinstance(created_time, datetime):
                            created_time = created_time.replace(tzinfo=None)
                        days_old = (datetime.now() - created_time).days
                        if days_old >= criteria['auto_resolve_stale_days']:
                            # Only resolve if low priority
                            priority = ticket.get('priority', 'medium').lower()
                            if priority in ['low', 'trivial']:
                                should_resolve = True
                                resolve_reason = f"Stale ticket ({days_old} days old, {priority} priority)"
                except Exception as e:
                    logger.debug(f"Failed to check age for {ticket_id}: {e}")

            # Criterion 4: Completed tickets
            if criteria.get('auto_resolve_completed', False):
                if metadata.get('completed') or metadata.get('work_complete'):
                    should_resolve = True
                    resolve_reason = "Work completed"

            if should_resolve:
                if self._resolve_ticket(ticket, resolve_reason):
                    results['resolved'] += 1
                    results['resolved_tickets'].append({
                        'ticket_id': ticket_id,
                        'reason': resolve_reason
                    })
                    logger.info(f"✅ Resolved {ticket_id}: {resolve_reason}")
                else:
                    results['failed'] += 1
                    logger.warning(f"⚠️  Failed to resolve {ticket_id}")

        logger.info("")
        logger.info("="*80)
        logger.info("📊 RESOLUTION SUMMARY")
        logger.info("="*80)
        logger.info(f"   Processed: {results['processed']}")
        logger.info(f"   Resolved: {results['resolved']}")
        logger.info(f"   Failed: {results['failed']}")
        logger.info("="*80)

        return results

    def _load_all_tickets(self) -> List[Dict[str, Any]]:
        """Load all tickets"""
        tickets = []

        for ticket_file in self.tickets_dir.glob("HELPDESK-*.json"):
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)
                    tickets.append(ticket)
            except Exception as e:
                logger.debug(f"Failed to load {ticket_file.name}: {e}")

        return tickets

    def _resolve_ticket(self, ticket: Dict[str, Any], reason: str) -> bool:
        """Mark ticket as resolved"""
        try:
            ticket_id = ticket.get('ticket_number', 'unknown')
            ticket_file = self.tickets_dir / f"{ticket_id}.json"

            # Update ticket status
            ticket['status'] = 'resolved'
            ticket['resolved_at'] = datetime.now().isoformat()
            ticket['resolved_by'] = 'JARVIS'
            ticket['resolution_reason'] = reason

            # Add to metadata
            if 'metadata' not in ticket:
                ticket['metadata'] = {}
            ticket['metadata']['auto_resolved'] = True
            ticket['metadata']['resolution_timestamp'] = datetime.now().isoformat()

            # Save updated ticket
            with open(ticket_file, 'w', encoding='utf-8') as f:
                json.dump(ticket, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            logger.error(f"Failed to resolve ticket {ticket_id}: {e}", exc_info=True)
            return False

    def show_queue_progress(self) -> str:
        """Show queue progress with decreasing numbers"""
        before_status = self.get_queue_status()

        logger.info("")
        logger.info("📊 QUEUE STATUS (BEFORE)")
        logger.info(f"   Total Tickets: {before_status['total']}")
        logger.info(f"   Active Queue: {before_status['active_queue']}")
        logger.info(f"   Resolved: {before_status['resolved']}")
        logger.info("")

        # Resolve tickets
        resolution_results = self.resolve_tickets()

        # Get status after
        after_status = self.get_queue_status()

        logger.info("")
        logger.info("📊 QUEUE STATUS (AFTER)")
        logger.info(f"   Total Tickets: {after_status['total']}")
        logger.info(f"   Active Queue: {after_status['active_queue']} ⬇️  ({before_status['active_queue'] - after_status['active_queue']} decrease)")
        logger.info(f"   Resolved: {after_status['resolved']} ⬆️  (+{after_status['resolved'] - before_status['resolved']} increase)")
        logger.info("")

        # Calculate progress
        queue_decrease = before_status['active_queue'] - after_status['active_queue']
        resolution_increase = after_status['resolved'] - before_status['resolved']

        progress_report = f"""
📊 **Queue Progress Report**

**Before Resolution:**
- Total Tickets: {before_status['total']}
- Active Queue: {before_status['active_queue']}
- Resolved: {before_status['resolved']}

**After Resolution:**
- Total Tickets: {after_status['total']}
- Active Queue: {after_status['active_queue']} ⬇️  (Decreased by {queue_decrease})
- Resolved: {after_status['resolved']} ⬆️  (Increased by {resolution_increase})

**Resolution Results:**
- Tickets Resolved: {resolution_results['resolved']}
- Success Rate: {(resolution_results['resolved'] / max(resolution_results['processed'], 1) * 100):.1f}%

**Queue Reduction: {queue_decrease} tickets** ✅
"""

        return progress_report


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Ticket Resolution Processor")
        parser.add_argument('--resolve', action='store_true', help='Resolve tickets')
        parser.add_argument('--status', action='store_true', help='Show queue status')
        parser.add_argument('--progress', action='store_true', help='Show queue progress')

        args = parser.parse_args()

        processor = JARVISTicketResolutionProcessor()

        if args.progress or not any([args.resolve, args.status]):
            report = processor.show_queue_progress()
            print(report)
        elif args.status:
            status = processor.get_queue_status()
            print(json.dumps(status, indent=2, default=str))
        elif args.resolve:
            results = processor.resolve_tickets()
            print(json.dumps(results, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()