#!/usr/bin/env python3
"""
Cursor IDE Notification & Ticket Tracker

Tracks all three tracking numbers:
1. Cursor IDE Request IDs
2. Internal Help Desk Tickets
3. GitHub PRs

Processes notifications and creates tickets for tracking.

Tags: #CURSOR_IDE #NOTIFICATIONS #TICKETS #GITHUB_PR #REQUEST_ID @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
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

logger = get_logger("CursorNotificationTracker")


@dataclass
class TrackingNumber:
    """Tracking number for a notification/ticket"""
    type: str  # "request_id", "help_desk", "github_pr"
    value: str
    source: str  # Where it came from
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "open"  # "open", "processing", "resolved", "closed"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NotificationTicket:
    """Notification ticket with all tracking numbers"""
    ticket_id: str
    title: str
    description: str
    tracking_numbers: List[TrackingNumber] = field(default_factory=list)
    cursor_request_id: Optional[str] = None
    help_desk_ticket: Optional[str] = None
    github_pr: Optional[str] = None
    status: str = "open"
    priority: str = "medium"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CursorNotificationTicketTracker:
    """
    Cursor IDE Notification & Ticket Tracker

    Tracks all three tracking numbers:
    - Cursor IDE Request IDs
    - Internal Help Desk Tickets
    - GitHub PRs
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize notification tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "notification_tickets"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tickets_file = self.data_dir / "tickets.json"
        self.tickets: Dict[str, NotificationTicket] = {}

        # Load existing tickets
        self._load_tickets()

        logger.info("✅ Cursor Notification & Ticket Tracker initialized")
        logger.info(f"   Tracking {len(self.tickets)} tickets")

    def _load_tickets(self):
        """Load tickets from disk"""
        if self.tickets_file.exists():
            try:
                with open(self.tickets_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tickets = {
                        ticket_id: NotificationTicket(**ticket_data)
                        for ticket_id, ticket_data in data.get("tickets", {}).items()
                    }
                    logger.info(f"   ✅ Loaded {len(self.tickets)} tickets")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load tickets: {e}")
                self.tickets = {}
        else:
            self.tickets = {}

    def _save_tickets(self):
        """Save tickets to disk"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "tickets": {
                    ticket_id: ticket.to_dict()
                    for ticket_id, ticket in self.tickets.items()
                }
            }
            with open(self.tickets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving tickets: {e}")

    def extract_tracking_numbers(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract all tracking numbers from text

        Returns:
            Dict with request_id, help_desk_ticket, github_pr
        """
        tracking = {
            "request_id": None,
            "help_desk_ticket": None,
            "github_pr": None
        }

        # Extract Cursor Request ID (UUID format)
        request_id_pattern = r'Request ID:\s*([a-f0-9-]{36})'
        match = re.search(request_id_pattern, text, re.IGNORECASE)
        if match:
            tracking["request_id"] = match.group(1)

        # Extract Help Desk Ticket (various formats)
        help_desk_patterns = [
            r'Ticket[:\s#]+([A-Z0-9-]+)',
            r'HD[:\s#]+([A-Z0-9-]+)',
            r'Help Desk[:\s#]+([A-Z0-9-]+)',
            r'#[0-9]+'  # Simple ticket number
        ]
        for pattern in help_desk_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tracking["help_desk_ticket"] = match.group(1) if match.lastindex else match.group(0)
                break

        # Extract GitHub PR
        github_pr_patterns = [
            r'PR[:\s#]+([0-9]+)',
            r'Pull Request[:\s#]+([0-9]+)',
            r'github\.com/.*/pull/([0-9]+)',
            r'#([0-9]+)'  # Simple PR number
        ]
        for pattern in github_pr_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tracking["github_pr"] = match.group(1) if match.lastindex else match.group(0)
                break

        return tracking

    def create_ticket_from_notification(
        self,
        title: str,
        description: str,
        notification_text: Optional[str] = None,
        cursor_request_id: Optional[str] = None,
        help_desk_ticket: Optional[str] = None,
        github_pr: Optional[str] = None
    ) -> str:
        """
        Create ticket from notification

        Args:
            title: Ticket title
            description: Ticket description
            notification_text: Full notification text (for extraction)
            cursor_request_id: Cursor Request ID (if known)
            help_desk_ticket: Help desk ticket (if known)
            github_pr: GitHub PR (if known)

        Returns:
            Ticket ID
        """
        import hashlib

        # Extract tracking numbers from text if provided
        if notification_text:
            extracted = self.extract_tracking_numbers(notification_text)
            cursor_request_id = cursor_request_id or extracted["request_id"]
            help_desk_ticket = help_desk_ticket or extracted["help_desk_ticket"]
            github_pr = github_pr or extracted["github_pr"]

        # Generate ticket ID
        ticket_id = hashlib.md5(
            f"{title}{description}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        # Create tracking numbers
        tracking_numbers = []
        if cursor_request_id:
            tracking_numbers.append(TrackingNumber(
                type="request_id",
                value=cursor_request_id,
                source="cursor_ide",
                metadata={"extracted_from": "notification"}
            ))

        if help_desk_ticket:
            tracking_numbers.append(TrackingNumber(
                type="help_desk",
                value=help_desk_ticket,
                source="help_desk",
                metadata={"extracted_from": "notification"}
            ))

        if github_pr:
            tracking_numbers.append(TrackingNumber(
                type="github_pr",
                value=github_pr,
                source="github",
                metadata={"extracted_from": "notification"}
            ))

        # Create ticket
        ticket = NotificationTicket(
            ticket_id=ticket_id,
            title=title,
            description=description,
            tracking_numbers=tracking_numbers,
            cursor_request_id=cursor_request_id,
            help_desk_ticket=help_desk_ticket,
            github_pr=github_pr
        )

        self.tickets[ticket_id] = ticket
        self._save_tickets()

        logger.info(f"   ✅ Created ticket: {ticket_id}")
        logger.info(f"      Request ID: {cursor_request_id or 'None'}")
        logger.info(f"      Help Desk: {help_desk_ticket or 'None'}")
        logger.info(f"      GitHub PR: {github_pr or 'None'}")

        return ticket_id

    def find_ticket_by_tracking(self, tracking_type: str, value: str) -> Optional[NotificationTicket]:
        """Find ticket by tracking number"""
        for ticket in self.tickets.values():
            if tracking_type == "request_id" and ticket.cursor_request_id == value:
                return ticket
            elif tracking_type == "help_desk" and ticket.help_desk_ticket == value:
                return ticket
            elif tracking_type == "github_pr" and ticket.github_pr == value:
                return ticket

        return None

    def get_open_tickets(self) -> List[NotificationTicket]:
        """Get all open tickets"""
        return [t for t in self.tickets.values() if t.status == "open"]

    def get_ticket_stats(self) -> Dict[str, Any]:
        """Get ticket statistics"""
        total = len(self.tickets)
        open_count = len(self.get_open_tickets())
        resolved_count = len([t for t in self.tickets.values() if t.status == "resolved"])

        # Count by tracking number type
        with_request_id = len([t for t in self.tickets.values() if t.cursor_request_id])
        with_help_desk = len([t for t in self.tickets.values() if t.help_desk_ticket])
        with_github_pr = len([t for t in self.tickets.values() if t.github_pr])

        return {
            "total": total,
            "open": open_count,
            "resolved": resolved_count,
            "with_request_id": with_request_id,
            "with_help_desk": with_help_desk,
            "with_github_pr": with_github_pr
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor Notification & Ticket Tracker")
        parser.add_argument("--create", nargs=3, metavar=("TITLE", "DESCRIPTION", "TEXT"),
                           help="Create ticket from notification text")
        parser.add_argument("--find", nargs=2, metavar=("TYPE", "VALUE"),
                           help="Find ticket by tracking number (request_id, help_desk, github_pr)")
        parser.add_argument("--stats", action="store_true", help="Show ticket statistics")
        parser.add_argument("--open", action="store_true", help="Show open tickets")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        tracker = CursorNotificationTicketTracker()

        if args.create:
            title, description, text = args.create
            ticket_id = tracker.create_ticket_from_notification(title, description, text)
            if args.json:
                ticket = tracker.tickets[ticket_id]
                print(json.dumps(ticket.to_dict(), indent=2))
            else:
                print(f"✅ Created ticket: {ticket_id}")

        elif args.find:
            tracking_type, value = args.find
            ticket = tracker.find_ticket_by_tracking(tracking_type, value)
            if ticket:
                if args.json:
                    print(json.dumps(ticket.to_dict(), indent=2))
                else:
                    print(f"✅ Found ticket: {ticket.ticket_id}")
                    print(f"   Title: {ticket.title}")
                    print(f"   Status: {ticket.status}")
            else:
                print(f"❌ No ticket found with {tracking_type}={value}")

        elif args.stats:
            stats = tracker.get_ticket_stats()
            if args.json:
                print(json.dumps(stats, indent=2))
            else:
                print("📊 Ticket Statistics:")
                print(f"   Total: {stats['total']}")
                print(f"   Open: {stats['open']}")
                print(f"   Resolved: {stats['resolved']}")
                print(f"   With Request ID: {stats['with_request_id']}")
                print(f"   With Help Desk: {stats['with_help_desk']}")
                print(f"   With GitHub PR: {stats['with_github_pr']}")

        elif args.open:
            open_tickets = tracker.get_open_tickets()
            if args.json:
                print(json.dumps([t.to_dict() for t in open_tickets], indent=2))
            else:
                print(f"📋 Open Tickets: {len(open_tickets)}")
                for ticket in open_tickets:
                    print(f"   • {ticket.title} ({ticket.ticket_id})")
                    if ticket.cursor_request_id:
                        print(f"     Request ID: {ticket.cursor_request_id}")
                    if ticket.help_desk_ticket:
                        print(f"     Help Desk: {ticket.help_desk_ticket}")
                    if ticket.github_pr:
                        print(f"     GitHub PR: {ticket.github_pr}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()