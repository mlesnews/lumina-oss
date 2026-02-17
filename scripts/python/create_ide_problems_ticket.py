#!/usr/bin/env python3
"""
Create Helpdesk Ticket for IDE Problems Issue
Simulates user reporting problem to helpdesk, then C-3PO routes it.

Tags: #HELPDESK #TICKET #C3PO #WORKFLOW @helpdesk @c3po
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_helpdesk_ticket_system import (
    JARVISHelpdeskTicketSystem,
    TicketPriority,
    TicketStatus
)
from jarvis_c3po_ticket_assigner import C3POTicketAssigner

def main():
    try:
        """Create ticket and route via C-3PO."""
        project_root = Path(__file__).parent.parent.parent

        print("="*80)
        print("📋 USER REPORTING PROBLEM TO HELPDESK")
        print("="*80)
        print()
        print("User: 'Hey helpdesk, I'm seeing 2,100 problems in my Cursor IDE")
        print("      Problems panel. This seems like a lot and I need help.'")
        print()

        # Create ticket system
        ticket_system = JARVISHelpdeskTicketSystem(project_root)

        # Create the ticket
        print("🔨 Creating helpdesk ticket...")
        ticket = ticket_system.create_ticket(
            title="CRITICAL: 2,100 IDE Problems Detected in Cursor IDE",
            description="""**Problem Report:**
User reports 2,100 problems detected in Cursor IDE Problems panel. This exceeds the critical threshold of 2,000 problems.

**Symptoms:**
- IDE Problems panel shows 2,100 total problems
- Problem monitor shows 0 problems (integration gap)
- Monitor cannot read from IDE Problems panel
- Critical threshold exceeded

**Impact:**
- Code quality issues may be accumulating
- Development workflow may be affected
- Monitor system not functioning properly

**Requested Actions:**
1. Investigate root cause of 2,100 problems
2. Fix monitor integration to read from IDE
3. Batch auto-fix fixable problems
4. Categorize and route remaining problems

**Priority:** CRITICAL (exceeds 2,000 threshold)
**Component:** IDE / Code Quality
**Issue Type:** Problem / Technical Issue""",
        priority=TicketPriority.CRITICAL,
        component="IDE",
        issue_type="problem",
        tags=["#IDE", "#PROBLEMS", "#CRITICAL", "@helpdesk", "#C3PO", "#R2D2"],
        auto_create_pr=False
        )

        print(f"✅ Ticket created: {ticket.ticket_id}")
        print(f"   Title: {ticket.title}")
        print(f"   Priority: {ticket.priority.value}")
        print()

        # Now C-3PO receives and routes the ticket
        print("="*80)
        print("🤖 C-3PO RECEIVING TICKET")
        print("="*80)
        print()
        print("C-3PO: 'Oh my! A critical problem has been reported. Let me analyze")
        print("        this and route it to the appropriate team immediately.'")
        print()

        # C-3PO analyzes and routes
        assigner = C3POTicketAssigner(project_root)

        print("🔍 C-3PO analyzing ticket...")
        print("   - Problem type: IDE/Code Quality")
        print("   - Severity: CRITICAL")
        print("   - Technical issue requiring diagnostics")
        print("   - Needs batch processing capability")
        print()

        # Determine routing
        # This is a technical problem that needs R2-D2's expertise
        # Route to problem_management team (R2-D2 is technical lead)
        print("📋 C-3PO routing decision:")
        print("   - Team: Problem Management Team")
        print("   - Reason: Technical problem requiring root cause analysis")
        print("   - Technical Lead: @r2d2 (R2-D2)")
        print("   - Manager: @marvin (Problem Management)")
        print()

        # Convert ticket to HELPDESK format for assignment
        # The ticket system uses PM format, but C-3PO uses HELPDESK format
        # We need to create a HELPDESK ticket or convert

        # For now, let's create a HELPDESK ticket
        helpticket_dir = project_root / "data" / "pr_tickets" / "tickets"
        helpticket_dir.mkdir(parents=True, exist_ok=True)

        # Generate HELPDESK ticket number
        import json
        from datetime import datetime

        # Find next HELPDESK number
        existing_tickets = list(helpticket_dir.glob("HELPDESK-*.json"))
        if existing_tickets:
            numbers = []
            for t in existing_tickets:
                try:
                    num = int(t.stem.split("-")[1])
                    numbers.append(num)
                except:
                    pass
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1

        helpticket_id = f"HELPDESK-{next_num:04d}"
        helpticket_file = helpticket_dir / f"{helpticket_id}.json"

        helpticket = {
            "ticket_number": helpticket_id,
            "title": ticket.title,
            "description": ticket.description,
            "priority": ticket.priority.value,
            "severity": "critical",
            "status": "open",
            "change_type": "problem",
            "component": ticket.component,
            "issue_type": ticket.issue_type,
            "created_at": ticket.created_at,
            "created_by": "user",
            "reported_by": "user",
            "tags": ticket.tags,
            "linked_tickets": [ticket.ticket_id],
            "metadata": {
                "original_ticket": ticket.ticket_id,
                "problem_count": 2100,
                "critical_threshold_exceeded": True
            }
        }

        with open(helpticket_file, 'w', encoding='utf-8') as f:
            json.dump(helpticket, f, indent=2)

        print(f"✅ Created HELPDESK ticket: {helpticket_id}")
        print()

        # Now C-3PO assigns it
        print("📤 C-3PO assigning ticket to team...")
        result = assigner.assign_ticket_to_team(
            helpticket_id,
            team_id="problem_management",
            auto_detect=False
        )

        if result.get("success"):
            assignment = result.get("team_assignment", {})
            print()
            print("="*80)
            print("✅ TICKET ROUTED SUCCESSFULLY")
            print("="*80)
            print()
            print(f"📋 Ticket: {helpticket_id}")
            print(f"   Team: {assignment.get('team_name', 'Unknown')}")
            print(f"   Team Manager: {assignment.get('team_manager', 'Unknown')}")
            print(f"   Technical Lead: {assignment.get('technical_lead', 'Unknown')}")
            print(f"   Primary Assignee: {assignment.get('primary_assignee', 'Unknown')}")
            print()
            print("🎯 Next Steps:")
            print("   1. R2-D2 will analyze the 2,100 problems")
            print("   2. Run batch auto-fix on fixable problems")
            print("   3. Fix monitor integration")
            print("   4. Categorize and address remaining problems")
            print()
            print("📊 Workflow Status:")
            print("   ✅ Ticket created")
            print("   ✅ C-3PO received and analyzed")
            print("   ✅ Routed to Problem Management Team")
            print("   ✅ Assigned to R2-D2 (Technical Lead)")
            print("   ⏳ Awaiting R2-D2 technical analysis")
        else:
            print(f"❌ Assignment failed: {result.get('error', 'Unknown error')}")
            return 1

        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":


    sys.exit(main())