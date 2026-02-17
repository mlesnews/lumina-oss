#!/usr/bin/env python3
"""
Create Change Requests for Session Tasks

Creates change request tickets for all tasks completed in this session.
Delegates to C3PO for helpdesk workflow management.

Author: LUMINA Security Team
Date: 2025-01-24
Tags: @cr @change-requests @JARVIS @C3PO @helpdesk #workflows
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class ChangeRequestCreator:
    """Create change request tickets for session tasks"""

    def __init__(self, project_root: Optional[Path] = None):
        self.logger = get_logger("ChangeRequestCreator")
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.tickets_dir = self.project_root / "data" / "pr_tickets" / "tickets"
        self.tickets_dir.mkdir(parents=True, exist_ok=True)
        self.counter_file = self.project_root / "data" / "pr_tickets" / "ticket_counter.json"

        # Load ticket counter
        self.ticket_counter = self._load_counter()

    def _load_counter(self) -> Dict[str, int]:
        """Load ticket counter"""
        if self.counter_file.exists():
            try:
                with open(self.counter_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both old and new counter formats
                    if "ticket_number" in data:
                        return data
                    elif "counter" in data:
                        return {"ticket_number": data["counter"], "change_request_number": 1}
            except Exception:
                pass
        return {"ticket_number": 3000000, "change_request_number": 1}

    def _save_counter(self):
        """Save ticket counter"""
        try:
            with open(self.counter_file, 'w', encoding='utf-8') as f:
                json.dump(self.ticket_counter, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving counter: {e}")

    def _get_next_ticket_number(self, ticket_type: str = "ticket") -> str:
        """
        Get next ticket number in 9-digit format

        Format: PREFIX + 9 digits (e.g., PM000000001, CR000000001, T000000001)

        Args:
            ticket_type: Type of ticket (ticket, change_request, task)
        """
        # Prefixes
        prefix_map = {
            "ticket": "PM",  # Problem Management
            "change_request": "CR",  # Change Request
            "task": "T"  # Task
        }

        prefix = prefix_map.get(ticket_type, "PM")

        # Get counter for this type
        counter_key = f"{ticket_type}_counter"
        ticket_num = self.ticket_counter.get(counter_key, 1)
        self.ticket_counter[counter_key] = ticket_num + 1
        self._save_counter()

        # Format as 9 digits with leading zeros
        return f"{prefix}{ticket_num:09d}"

    def _get_next_cr_number(self) -> str:
        """
        Get next change request number in 9-digit format

        Format: CR + 9 digits (e.g., CR000000001)
        """
        cr_num = self.ticket_counter.get("change_request_counter", 1)
        self.ticket_counter["change_request_counter"] = cr_num + 1
        self._save_counter()
        return f"CR{cr_num:09d}"

    def create_change_request(
        self,
        title: str,
        description: str,
        change_type: str,
        priority: str,
        assigned_to: str = "C-3PO",
        delegated_by: str = "JARVIS",
        tags: List[str] = None,
        related_files: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a change request ticket

        Args:
            title: Change request title
            description: Detailed description
            change_type: Type of change (feature, bug_fix, security, etc.)
            priority: Priority level (critical, high, medium, low)
            assigned_to: Assigned droid/team (default: C-3PO)
            delegated_by: Who delegated this (default: JARVIS)
            tags: List of tags
            related_files: List of related files

        Returns:
            Change request ticket data
        """
        # Determine ticket type from change_type
        ticket_type = "change_request" if change_type == "change_request" else "ticket"
        ticket_number = self._get_next_ticket_number(ticket_type)
        cr_number = self._get_next_cr_number()

        ticket = {
            "ticket_number": ticket_number,
            "change_request_number": cr_number,
            "title": title,
            "description": description,
            "change_type": change_type,
            "priority": priority,
            "severity": priority,
            "status": "open",
            "assigned_to": assigned_to,
            "delegated_by": delegated_by,
            "delegation_note": f"Delegated by {delegated_by} to {assigned_to} for @helpdesk workflow management",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "tags": tags or [],
            "related_files": related_files or [],
            "workflow_category": "helpdesk",
            "helpdesk_location": "@helpdesk",
            "escalation_path": f"{assigned_to} → JARVIS (as protocol demands)"
        }

        # Save ticket
        ticket_file = self.tickets_dir / f"{ticket_number}.json"
        with open(ticket_file, 'w', encoding='utf-8') as f:
            json.dump(ticket, f, indent=2, ensure_ascii=False)

        self.logger.info(f"✅ Created change request: {cr_number} ({ticket_number})")
        return ticket

    def create_email_hub_change_request(self) -> Dict[str, Any]:
        """Create change request for N8N Email Hub expansion"""
        return self.create_change_request(
            title="@N8N Expansion: NAS/DSM Email Hub Integration",
            description="""Created @N8N expansion for integration with custom company email hub on NAS/DSM package configuration.

Features:
- Email sending via NAS/DSM SMTP (port 25)
- Email receiving via NAS/DSM IMAP (port 143)
- Email hub management operations via DSM API
- Health monitoring and alerts
- Integration with JARVIS, @SYPHON, MARVIN
- Credentials stored in Azure Key Vault

Workflows:
- email_hub_send: Send emails via SMTP
- email_hub_receive: Receive emails via IMAP (every 5 minutes)
- email_hub_management: Manage mailboxes, aliases, distribution lists
- email_hub_monitoring: Health checks (every hour)

Files Created:
- config/n8n/nas_dsm_email_hub_expansion.json
- docs/system/N8N_NAS_DSM_EMAIL_HUB_SETUP.md

Files Updated:
- config/n8n/unified_communications_config.json
- config/n8n/workflows.json""",
            change_type="feature",
            priority="high",
            tags=["@n8n", "@nas", "@dsm", "@email", "#email-hub", "#integration"],
            related_files=[
                "config/n8n/nas_dsm_email_hub_expansion.json",
                "docs/system/N8N_NAS_DSM_EMAIL_HUB_SETUP.md",
                "config/n8n/unified_communications_config.json",
                "config/n8n/workflows.json"
            ]
        )


def main():
    """Create email hub change request"""
    creator = ChangeRequestCreator()

    print("\n🎫 Creating Change Request for N8N Email Hub Expansion...")
    print("=" * 70)

    cr = creator.create_email_hub_change_request()

    print(f"\n✅ Created change request:")
    print(f"  - {cr['change_request_number']}: {cr['title']}")
    print(f"    Ticket: {cr['ticket_number']} | Assigned to: {cr['assigned_to']}")
    print(f"    Priority: {cr['priority']} | Status: {cr['status']}")


if __name__ == "__main__":

    main()