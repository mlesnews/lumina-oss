#!/usr/bin/env python3
"""
JARVIS C-3PO Ticket Assigner
C-3PO assigns tickets to teams with proper team structure (Manager, Technical Lead, Business Lead).

Tags: #HELPDESK #TICKET #ASSIGNMENT #TEAM @C3PO @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from lumina_organizational_structure import LuminaOrganizationalStructure
    from jarvis_pr_ticket_coordinator import PRTicketCoordinator
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    LuminaOrganizationalStructure = None
    PRTicketCoordinator = None

logger = get_logger("JARVISC3POTicketAssigner")


class C3POTicketAssigner:
    """
    C-3PO Ticket Assignment System

    C-3PO (Helpdesk Coordinator) assigns tickets to teams with proper structure:
    - Team Manager: @c3po (required)
    - Technical Lead: @r2d2 or team-specific (required)
    - Business Lead: Domain-specific (optional)

    This ensures proper team management and coordination.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Load organizational structure
        if LuminaOrganizationalStructure:
            try:
                self.org_structure = LuminaOrganizationalStructure(project_root)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load organizational structure: {e}")
                self.org_structure = None
        else:
            self.org_structure = None

        # PR/Ticket coordinator
        if PRTicketCoordinator:
            self.coordinator = PRTicketCoordinator(project_root)
        else:
            self.coordinator = None

        # Ticket directory - check both locations
        self.ticket_dir = project_root / "data" / "helpdesk" / "tickets"
        self.ticket_dir.mkdir(parents=True, exist_ok=True)
        # Also check pr_tickets for backward compatibility
        self.pr_ticket_dir = project_root / "data" / "pr_tickets" / "tickets"
        self.pr_ticket_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ C-3PO Ticket Assigner initialized")
        if self.org_structure:
            self.logger.info(f"   Available Teams: {len(self.org_structure.teams)}")

    def assign_ticket_to_team(
        self,
        ticket_number: str,
        team_id: Optional[str] = None,
        auto_detect: bool = True
    ) -> Dict[str, Any]:
        """
        Assign ticket to team with proper team structure.

        Args:
            ticket_number: Ticket number (HELPDESK-XXXX)
            team_id: Specific team ID (optional, auto-detects if not provided)
            auto_detect: Auto-detect team from ticket content if team_id not provided
        """
        self.logger.info("="*80)
        self.logger.info(f"C-3PO ASSIGNING TICKET {ticket_number} TO TEAM")
        self.logger.info("="*80)

        # Load ticket - check both locations
        ticket_file = self.ticket_dir / f"{ticket_number}.json"
        if not ticket_file.exists():
            # Try pr_tickets directory for backward compatibility
            ticket_file = self.pr_ticket_dir / f"{ticket_number}.json"
        if not ticket_file.exists():
            return {"success": False, "error": f"Ticket {ticket_number} not found"}

        try:
            with open(ticket_file, 'r', encoding='utf-8') as f:
                ticket = json.load(f)
        except Exception as e:
            return {"success": False, "error": f"Failed to load ticket: {e}"}

        # Determine team
        if team_id:
            team = self.org_structure.teams.get(team_id) if self.org_structure else None
            if not team:
                return {"success": False, "error": f"Team {team_id} not found"}
        elif auto_detect and self.coordinator:
            # Use coordinator's routing logic
            description = ticket.get("description", "")
            change_type = ticket.get("change_type", "")
            severity_str = ticket.get("severity", "minor")

            from jarvis_pr_ticket_coordinator import IssueSeverity
            severity_map = {
                "critical": IssueSeverity.CRITICAL,
                "major": IssueSeverity.MAJOR,
                "minor": IssueSeverity.MINOR,
                "trivial": IssueSeverity.TRIVIAL
            }
            severity = severity_map.get(severity_str, IssueSeverity.MINOR)

            team_info = self.coordinator._route_to_helpdesk_team(change_type, severity, description)
            team_id = team_info["team_id"]
            team = self.org_structure.teams.get(team_id) if self.org_structure else None
        else:
            return {"success": False, "error": "No team specified and auto_detect disabled"}

        if not team:
            return {"success": False, "error": f"Could not determine team for ticket {ticket_number}"}

        # Get team structure
        team_manager = team.helpdesk_manager or "@c3po"
        technical_lead = team.team_lead or "@r2d2"

        # Determine business lead (domain-specific)
        business_lead = self._determine_business_lead(team.team_id, team.division)

        # Update ticket with team assignment
        ticket["team_assignment"] = {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "division": team.division,
            "team_manager": team_manager,  # Required: Team Manager
            "technical_lead": technical_lead,  # Required: Technical Lead
            "business_lead": business_lead,  # Optional: Business Lead
            "primary_assignee": technical_lead,  # Primary team member
            "assigned_at": datetime.now().isoformat(),
            "assigned_by": "@c3po",
            "supervision_enabled": True,  # @PEAK: Enable supervision
            "reporting_required": True  # Subordinate must report to manager
        }

        ticket["status"] = "assigned"
        ticket["assigned_by"] = "@c3po"
        ticket["assigned_at"] = datetime.now().isoformat()

        # Save updated ticket
        try:
            with open(ticket_file, 'w', encoding='utf-8') as f:
                json.dump(ticket, f, indent=2, default=str)
        except Exception as e:
            return {"success": False, "error": f"Failed to save ticket: {e}"}

        self.logger.info(f"✅ Ticket {ticket_number} assigned to {team.team_name}")
        self.logger.info(f"   📋 Team Manager: {team_manager}")
        self.logger.info(f"   🔧 Technical Lead: {technical_lead}")
        if business_lead:
            self.logger.info(f"   💼 Business Lead: {business_lead}")
        self.logger.info(f"   👤 Primary Assignee: {technical_lead}")

        return {
            "success": True,
            "ticket_number": ticket_number,
            "team_assignment": ticket["team_assignment"]
        }

    def _determine_business_lead(self, team_id: str, division: str) -> Optional[str]:
        """Determine business lead for team (domain-specific)"""
        business_leads = {
            "docker_engineering": "Docker Engineering Lead",
            "storage_engineering": "Storage Engineering Lead",
            "network_support": None,  # Technical team, no business lead
            "security_analysis": None,  # Security team, no business lead
            "system_health": None,  # Operations team, no business lead
            "ai_intelligence": None,  # Technical team, no business lead
            "helpdesk_support": "Helpdesk Support Lead",
            "problem_management": "Problem Management Lead",
            "change_management": "Change Management Lead",
            "jarvis_superagent": "JARVIS Superagent Lead"
        }
        return business_leads.get(team_id)

    def assign_all_unassigned_tickets(self) -> Dict[str, Any]:
        """Assign all unassigned tickets to appropriate teams"""
        self.logger.info("="*80)
        self.logger.info("C-3PO ASSIGNING ALL UNASSIGNED TICKETS")
        self.logger.info("="*80)

        results = []

        # Find all tickets
        for ticket_file in self.ticket_dir.glob("HELPDESK-*.json"):
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)

                # Check if already assigned
                if ticket.get("team_assignment"):
                    self.logger.debug(f"   ⏭️  {ticket_file.name} already assigned")
                    continue

                # Assign ticket
                ticket_number = ticket.get("ticket_number", ticket_file.stem)
                result = self.assign_ticket_to_team(ticket_number, auto_detect=True)
                results.append(result)

            except Exception as e:
                self.logger.warning(f"⚠️  Failed to process {ticket_file.name}: {e}")
                results.append({
                    "success": False,
                    "ticket_file": ticket_file.name,
                    "error": str(e)
                })

        successful = sum(1 for r in results if r.get("success"))
        self.logger.info(f"✅ Assigned {successful}/{len(results)} tickets")

        return {
            "total_tickets": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }

    def get_team_tickets(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all tickets assigned to a team"""
        tickets = []

        for ticket_file in self.ticket_dir.glob("HELPDESK-*.json"):
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)

                team_assignment = ticket.get("team_assignment", {})
                if team_assignment.get("team_id") == team_id:
                    tickets.append(ticket)
            except Exception as e:
                self.logger.debug(f"Failed to load {ticket_file.name}: {e}")

        return tickets


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="C-3PO Ticket Assigner")
        parser.add_argument("--assign", type=str, help="Assign specific ticket (HELPDESK-XXXX)")
        parser.add_argument("--team", type=str, help="Specific team ID (optional)")
        parser.add_argument("--assign-all", action="store_true", help="Assign all unassigned tickets")
        parser.add_argument("--team-tickets", type=str, help="Get all tickets for team")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        assigner = C3POTicketAssigner(project_root)

        if args.assign:
            result = assigner.assign_ticket_to_team(args.assign, team_id=args.team)
            print(json.dumps(result, indent=2, default=str))
        elif args.assign_all:
            result = assigner.assign_all_unassigned_tickets()
            print(json.dumps(result, indent=2, default=str))
        elif args.team_tickets:
            tickets = assigner.get_team_tickets(args.team_tickets)
            print(json.dumps(tickets, indent=2, default=str))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()