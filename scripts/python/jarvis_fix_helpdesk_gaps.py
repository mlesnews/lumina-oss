#!/usr/bin/env python3
"""
JARVIS Fix Helpdesk Gaps
Automatically fixes gaps found in helpdesk workflow.

Tags: #JARVIS #HELPDESK #GAP_FIX #AUTOMATION @helpdesk @c3po
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)
    C3POTicketAssigner = None

logger = get_logger("JARVISFixHelpdeskGaps")


def fix_ticket_gaps(project_root: Path) -> Dict[str, Any]:
    """Fix gaps in helpdesk tickets"""
    tickets_dir = project_root / "data" / "pr_tickets" / "tickets"

    results = {
        'fixed': 0,
        'failed': 0,
        'details': []
    }

    if not C3POTicketAssigner:
        logger.error("C3POTicketAssigner not available")
        return results

    assigner = C3POTicketAssigner(project_root)

    # Find all HELPDESK tickets
    for ticket_file in tickets_dir.glob("HELPDESK-*.json"):
        try:
            with open(ticket_file, 'r', encoding='utf-8') as f:
                ticket = json.load(f)

            ticket_id = ticket.get("ticket_number", ticket_file.stem)
            needs_fix = False

            # Check for gaps
            team_assignment = ticket.get("team_assignment", {})

            # Gap 1: Missing team_assignment entirely
            if not team_assignment:
                logger.info(f"🔧 Fixing {ticket_id}: Missing team_assignment")
                result = assigner.assign_ticket_to_team(ticket_id, auto_detect=True)
                if result.get("success"):
                    results['fixed'] += 1
                    results['details'].append({
                        'ticket': ticket_id,
                        'fix': 'assigned_to_team',
                        'success': True
                    })
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'ticket': ticket_id,
                        'fix': 'assigned_to_team',
                        'success': False,
                        'error': result.get('error')
                    })
                needs_fix = True

            # Gap 2: Missing primary_assignee in team_assignment
            elif team_assignment and not team_assignment.get('primary_assignee'):
                logger.info(f"🔧 Fixing {ticket_id}: Missing primary_assignee")
                # Set primary_assignee to technical_lead if available
                if team_assignment.get('technical_lead'):
                    team_assignment['primary_assignee'] = team_assignment['technical_lead']
                    ticket['team_assignment'] = team_assignment
                    with open(ticket_file, 'w', encoding='utf-8') as f:
                        json.dump(ticket, f, indent=2, ensure_ascii=False)
                    results['fixed'] += 1
                    results['details'].append({
                        'ticket': ticket_id,
                        'fix': 'added_primary_assignee',
                        'success': True
                    })
                    needs_fix = True

            # Gap 3: Missing status
            if not ticket.get('status'):
                logger.info(f"🔧 Fixing {ticket_id}: Missing status")
                ticket['status'] = 'assigned' if team_assignment else 'open'
                with open(ticket_file, 'w', encoding='utf-8') as f:
                    json.dump(ticket, f, indent=2, ensure_ascii=False)
                results['fixed'] += 1
                results['details'].append({
                    'ticket': ticket_id,
                    'fix': 'added_status',
                    'success': True
                })
                needs_fix = True

            if not needs_fix:
                logger.debug(f"✅ {ticket_id} has no gaps")

        except Exception as e:
            logger.error(f"Failed to process {ticket_file.name}: {e}", exc_info=True)
            results['failed'] += 1
            results['details'].append({
                'ticket': ticket_file.name,
                'fix': 'unknown',
                'success': False,
                'error': str(e)
            })

    return results


def main():
    try:
        """CLI interface"""
        project_root = Path(__file__).parent.parent.parent

        logger.info("="*80)
        logger.info("🔧 FIXING HELPDESK WORKFLOW GAPS")
        logger.info("="*80)

        results = fix_ticket_gaps(project_root)

        logger.info("")
        logger.info("="*80)
        logger.info("📊 GAP FIX SUMMARY")
        logger.info("="*80)
        logger.info(f"   Fixed: {results['fixed']}")
        logger.info(f"   Failed: {results['failed']}")
        logger.info("="*80)

        if results['details']:
            logger.info("")
            logger.info("**Details:**")
            for detail in results['details']:
                status = "✅" if detail.get('success') else "❌"
                logger.info(f"   {status} {detail.get('ticket')}: {detail.get('fix')}")
                if not detail.get('success'):
                    logger.info(f"      Error: {detail.get('error')}")

        return 0 if results['failed'] == 0 else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())