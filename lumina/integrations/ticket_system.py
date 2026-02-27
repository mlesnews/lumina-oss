"""
Ticket system — UUID-to-ticket collation and lifecycle management.

Provides ticket creation, tracking, and status management with
sequential ID generation and JSON persistence.

Example:
    ts = TicketSystem(data_dir=Path("./tickets"))
    ticket = ts.create("Fix API timeout", priority="P1", category="incident")
    print(f"Created: {ticket['id']}")

    ts.update_status(ticket["id"], "IN_PROGRESS")
    ts.add_note(ticket["id"], "Root cause: connection pool exhaustion")
    ts.update_status(ticket["id"], "RESOLVED")

    open_tickets = ts.list_open()
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

STATUSES = [
    "PENDING", "ASSIGNED", "IN_PROGRESS",
    "DELEGATED", "FOLLOW_UP",
    "RESOLVED", "CLOSED",
]

PRIORITIES = ["P0", "P1", "P2", "P3"]


class TicketSystem:
    """
    JSON-backed ticket management system.

    Args:
        data_dir: Directory for ticket JSON files.
        prefix: Ticket ID prefix (default "C-").
    """

    def __init__(
        self,
        data_dir: Path,
        prefix: str = "C-",
    ):
        self._data_dir = data_dir
        self._prefix = prefix
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._counter_file = data_dir / "ticket_counter.json"

    def create(
        self,
        description: str,
        priority: str = "P2",
        category: str = "task",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new ticket.

        Args:
            description: What needs to be done.
            priority: P0 (critical) through P3 (low).
            category: incident, problem, change, task.
            metadata: Arbitrary metadata.

        Returns:
            The created ticket dict.
        """
        seq = self._next_seq()
        ticket_id = f"{self._prefix}{seq:09d}"

        ticket = {
            "id": ticket_id,
            "uuid": str(uuid4()),
            "description": description,
            "priority": priority if priority in PRIORITIES else "P2",
            "category": category,
            "status": "PENDING",
            "created_at": time.time(),
            "updated_at": time.time(),
            "notes": [],
            "metadata": metadata or {},
        }

        path = self._data_dir / f"{ticket_id}.json"
        path.write_text(json.dumps(ticket, indent=2))
        return ticket

    def get(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get a ticket by ID."""
        path = self._data_dir / f"{ticket_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def update_status(self, ticket_id: str, status: str) -> bool:
        """Update ticket status. Returns False if ticket not found."""
        ticket = self.get(ticket_id)
        if not ticket:
            return False
        if status not in STATUSES:
            logger.warning("Unknown status: %s", status)
            return False

        ticket["status"] = status
        ticket["updated_at"] = time.time()
        path = self._data_dir / f"{ticket_id}.json"
        path.write_text(json.dumps(ticket, indent=2))
        return True

    def add_note(self, ticket_id: str, note: str) -> bool:
        """Add a note to a ticket."""
        ticket = self.get(ticket_id)
        if not ticket:
            return False

        ticket["notes"].append({
            "text": note,
            "timestamp": time.time(),
        })
        ticket["updated_at"] = time.time()
        path = self._data_dir / f"{ticket_id}.json"
        path.write_text(json.dumps(ticket, indent=2))
        return True

    def list_open(self) -> List[Dict[str, Any]]:
        """List all non-closed tickets."""
        tickets = []
        for path in sorted(self._data_dir.glob(f"{self._prefix}*.json")):
            try:
                ticket = json.loads(path.read_text())
                if ticket.get("status") not in ("RESOLVED", "CLOSED"):
                    tickets.append(ticket)
            except (json.JSONDecodeError, OSError):
                continue
        return tickets

    def list_all(self) -> List[Dict[str, Any]]:
        """List all tickets."""
        tickets = []
        for path in sorted(self._data_dir.glob(f"{self._prefix}*.json")):
            try:
                tickets.append(json.loads(path.read_text()))
            except (json.JSONDecodeError, OSError):
                continue
        return tickets

    def _next_seq(self) -> int:
        """Get and increment the ticket counter."""
        counter = 1
        if self._counter_file.exists():
            try:
                data = json.loads(self._counter_file.read_text())
                counter = data.get("next", 1)
            except (json.JSONDecodeError, OSError):
                pass
        self._counter_file.write_text(json.dumps({"next": counter + 1}))
        return counter
