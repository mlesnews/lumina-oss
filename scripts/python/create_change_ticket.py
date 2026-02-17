#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem, TicketPriority

def create_change_ticket():
    system = JARVISHelpdeskTicketSystem()
    ticket = system.create_ticket(
        title="IMPLEMENTATION: NAS Migration + Lighting Control",
        description="Change Control Request: Proceed with NAS Migration Phase 1.3 (Ollama models move) and restore keyboard lighting to dimmest red level.",
        priority=TicketPriority.MEDIUM,
        component="System Engineering",
        issue_type="task",
        tags=["lighting", "migration", "change-control", "@DOIT"]
    )
    print(f"Created ticket: {ticket.ticket_id}")

if __name__ == "__main__":
    create_change_ticket()
