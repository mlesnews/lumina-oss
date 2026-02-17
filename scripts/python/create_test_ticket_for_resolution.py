#!/usr/bin/env python3
"""
Create a test ticket that can be auto-resolved to demonstrate queue decrease
"""

import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
tickets_dir = project_root / "data" / "pr_tickets" / "tickets"

# Create a test ticket
test_ticket = {
    "ticket_number": "HELPDESK-0010",
    "title": "Test Problem - Auto Resolution Test",
    "description": "This is a test problem for demonstrating auto-resolution and queue decrease functionality.",
    "priority": "low",
    "severity": "low",
    "status": "assigned",
    "change_type": "test",
    "component": "Testing",
    "issue_type": "test",
    "created_at": datetime.now().isoformat(),
    "created_by": "system",
    "reported_by": "system",
    "tags": ["#TEST", "#AUTO_RESOLVE"],
    "team_assignment": {
        "team_id": "helpdesk_support",
        "team_name": "Helpdesk Support Team",
        "division": "Helpdesk Operations",
        "team_manager": "@c3po",
        "technical_lead": "@r2d2",
        "primary_assignee": "@r2d2",
        "assigned_at": datetime.now().isoformat(),
        "assigned_by": "@c3po"
    },
    "metadata": {
        "test_ticket": True,
        "auto_resolvable": True
    }
}

ticket_file = tickets_dir / "HELPDESK-0010.json"
with open(ticket_file, 'w', encoding='utf-8') as f:
    json.dump(test_ticket, f, indent=2, ensure_ascii=False)

print(f"✅ Created test ticket: HELPDESK-0010")
print("   This ticket will be auto-resolved to demonstrate queue decrease")
