#!/usr/bin/env python3
"""
Consolidate Help Desk Tickets

Cross-references existing tickets and consolidates duplicates.
Updates ticket format to T + 9 digits starting at T300000001.

Tags: #HELPDESK #TICKET_CONSOLIDATION #CROSS_REFERENCE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("ConsolidateHelpdeskTickets")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ConsolidateHelpdeskTickets")


class HelpdeskTicketConsolidator:
    """
    Consolidate Help Desk Tickets

    Cross-references existing tickets, identifies duplicates,
    and consolidates related tickets.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.tickets_dir = self.project_root / "data" / "helpdesk" / "tickets"
        self.counter_file = self.project_root / "data" / "helpdesk" / "ticket_counter.json"

        logger.info("="*80)
        logger.info("🔍 HELP DESK TICKET CONSOLIDATION")
        logger.info("="*80)
        logger.info("")
        logger.info("   Format: T + 9 digits starting at T300000001")
        logger.info("   Purpose: Cross-reference and consolidate existing tickets")
        logger.info("")

    def consolidate(self) -> Dict[str, Any]:
        try:
            """
            Consolidate help desk tickets

            Returns:
                Consolidation report
            """
            logger.info("🔍 Analyzing existing tickets...")
            logger.info("")

            # Load all tickets
            tickets = self._load_all_tickets()

            # Analyze tickets
            analysis = self._analyze_tickets(tickets)

            # Identify duplicates
            duplicates = self._identify_duplicates(tickets)

            # Identify related tickets
            related = self._identify_related(tickets)

            # Generate consolidation plan
            consolidation_plan = self._generate_consolidation_plan(tickets, duplicates, related)

            # Save report
            report = {
                "consolidation_date": datetime.now().isoformat(),
                "total_tickets": len(tickets),
                "analysis": analysis,
                "duplicates": duplicates,
                "related_tickets": related,
                "consolidation_plan": consolidation_plan
            }

            report_file = self.project_root / "data" / "helpdesk" / "consolidation_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info("="*80)
            logger.info("✅ CONSOLIDATION COMPLETE")
            logger.info("="*80)
            logger.info(f"   Total Tickets: {len(tickets)}")
            logger.info(f"   Duplicates Found: {len(duplicates)}")
            logger.info(f"   Related Groups: {len(related)}")
            logger.info(f"   Report: {report_file}")
            logger.info("")

            return report

        except Exception as e:
            self.logger.error(f"Error in consolidate: {e}", exc_info=True)
            raise
    def _load_all_tickets(self) -> List[Dict[str, Any]]:
        """Load all help desk tickets"""
        tickets = []

        if not self.tickets_dir.exists():
            logger.warning(f"Tickets directory not found: {self.tickets_dir}")
            return tickets

        # Load T-format tickets
        for ticket_file in sorted(self.tickets_dir.glob("T*.json")):
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)
                    ticket['_file'] = str(ticket_file)
                    tickets.append(ticket)
            except Exception as e:
                logger.warning(f"Error loading {ticket_file}: {e}")

        # Load PM-format tickets (legacy)
        for ticket_file in sorted(self.tickets_dir.glob("PM*.json")):
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)
                    ticket['_file'] = str(ticket_file)
                    ticket['_legacy_format'] = True
                    tickets.append(ticket)
            except Exception as e:
                logger.warning(f"Error loading {ticket_file}: {e}")

        logger.info(f"   Loaded {len(tickets)} tickets")

        return tickets

    def _analyze_tickets(self, tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze ticket formats and patterns"""
        analysis = {
            "t_format_count": 0,
            "pm_format_count": 0,
            "ticket_number_ranges": {},
            "status_distribution": defaultdict(int),
            "priority_distribution": defaultdict(int),
            "component_distribution": defaultdict(int)
        }

        for ticket in tickets:
            ticket_id = ticket.get("ticket_id", "")

            if ticket_id.startswith("T"):
                analysis["t_format_count"] += 1
            elif ticket_id.startswith("PM"):
                analysis["pm_format_count"] += 1

            status = ticket.get("status", "unknown")
            priority = ticket.get("priority", "unknown")
            component = ticket.get("component", "unknown")

            analysis["status_distribution"][status] += 1
            analysis["priority_distribution"][priority] += 1
            analysis["component_distribution"][component] += 1

        logger.info("   📊 Ticket Analysis:")
        logger.info(f"      T-format: {analysis['t_format_count']}")
        logger.info(f"      PM-format: {analysis['pm_format_count']}")
        logger.info(f"      Total: {len(tickets)}")

        return analysis

    def _identify_duplicates(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify duplicate tickets"""
        duplicates = []

        # Group by title similarity
        title_groups = defaultdict(list)
        for ticket in tickets:
            title = ticket.get("title", "").lower().strip()
            title_groups[title].append(ticket)

        # Find duplicates (same title)
        for title, group in title_groups.items():
            if len(group) > 1:
                duplicates.append({
                    "title": title,
                    "tickets": [t.get("ticket_id") for t in group],
                    "count": len(group)
                })

        if duplicates:
            logger.info(f"   ⚠️  Found {len(duplicates)} duplicate groups")
        else:
            logger.info("   ✅ No duplicates found")

        return duplicates

    def _identify_related(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify related tickets"""
        related = []

        # Group by component
        component_groups = defaultdict(list)
        for ticket in tickets:
            component = ticket.get("component", "unknown")
            component_groups[component].append(ticket.get("ticket_id"))

        # Group by change request
        cr_groups = defaultdict(list)
        for ticket in tickets:
            cr_id = ticket.get("change_request_id")
            if cr_id:
                cr_groups[cr_id].append(ticket.get("ticket_id"))

        # Create related groups
        for component, ticket_ids in component_groups.items():
            if len(ticket_ids) > 1:
                related.append({
                    "type": "component",
                    "key": component,
                    "tickets": ticket_ids,
                    "count": len(ticket_ids)
                })

        for cr_id, ticket_ids in cr_groups.items():
            if len(ticket_ids) > 1:
                related.append({
                    "type": "change_request",
                    "key": cr_id,
                    "tickets": ticket_ids,
                    "count": len(ticket_ids)
                })

        if related:
            logger.info(f"   🔗 Found {len(related)} related ticket groups")
        else:
            logger.info("   ✅ No related groups found")

        return related

    def _generate_consolidation_plan(self, tickets: List[Dict[str, Any]], 
                                   duplicates: List[Dict[str, Any]],
                                   related: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate consolidation plan"""
        plan = {
            "recommendations": [],
            "actions": []
        }

        # Recommendations for duplicates
        for dup in duplicates:
            plan["recommendations"].append({
                "type": "consolidate_duplicates",
                "tickets": dup["tickets"],
                "action": f"Merge {dup['count']} duplicate tickets into one",
                "priority": "high"
            })

        # Recommendations for related tickets
        for rel in related:
            plan["recommendations"].append({
                "type": "link_related",
                "tickets": rel["tickets"],
                "action": f"Link {rel['count']} related tickets ({rel['type']}: {rel['key']})",
                "priority": "medium"
            })

        # Update format recommendations
        t_format_tickets = [t for t in tickets if t.get("ticket_id", "").startswith("T")]
        if t_format_tickets:
            # Check if any need format update (6 digits -> 9 digits)
            needs_update = [t for t in t_format_tickets if len(t.get("ticket_id", "")) < 10]
            if needs_update:
                plan["recommendations"].append({
                    "type": "update_format",
                    "tickets": [t.get("ticket_id") for t in needs_update],
                    "action": "Update ticket IDs to T + 9 digits format (T300000001+)",
                    "priority": "medium"
                })

        logger.info(f"   📋 Generated {len(plan['recommendations'])} recommendations")

        return plan


def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        consolidator = HelpdeskTicketConsolidator(project_root)
        report = consolidator.consolidate()

        logger.info("")
        logger.info("="*80)
        logger.info("✅ CONSOLIDATION COMPLETE")
        logger.info("="*80)
        logger.info("")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())