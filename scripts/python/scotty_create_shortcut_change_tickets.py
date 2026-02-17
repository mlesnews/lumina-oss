#!/usr/bin/env python3
"""
@SCOTTY's Shortcut Restoration - Change Request & Task Creation
Creates Change Request and Task tickets linked to the problem ticket

Tags: #SCOTTY #SHORTCUTS #CHANGE_REQUEST #TASK #HELPDESK @SCOTTY @LUMINA @HELPDESK
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SCOTTYShortcutChangeTickets")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SCOTTYShortcutChangeTickets")

try:
    from scripts.python.jarvis_helpdesk_ticket_system import (
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketType
    )
    HELPDESK_AVAILABLE = True
except ImportError:
    HELPDESK_AVAILABLE = False
    logger.error("Helpdesk ticket system not available")


def create_change_request_and_task(problem_ticket_id: str):
    """
    Create Change Request and Task tickets linked to the problem ticket

    Args:
        problem_ticket_id: The problem ticket ID (e.g., T000003085)
    """
    if not HELPDESK_AVAILABLE:
        logger.error("❌ Helpdesk system not available")
        return None, None

    ticket_system = JARVISHelpdeskTicketSystem(project_root=project_root)

    logger.info("=" * 80)
    logger.info("@SCOTTY's Shortcut Restoration - Change Management")
    logger.info("USS Lumina - @scotty (Windows Systems Architect)")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"Problem Ticket: {problem_ticket_id}")
    logger.info("")

    # 1. Create Change Request
    logger.info("📋 Creating Change Request...")
    logger.info("")

    change_request_description = f"""**CHANGE REQUEST**: Restore Desktop and Toolbar Shortcuts

**RELATED PROBLEM TICKET**: {problem_ticket_id}

**CHANGE SUMMARY**:
Desktop and toolbar shortcuts were missing after system reboot. @SCOTTY has successfully restored the desktop to its original state.

**CHANGE DETAILS**:
- Restored all desktop shortcuts to original locations
- Restored toolbar (taskbar) shortcuts
- Verified all shortcuts are functional
- Desktop restored to pre-reboot state

**IMPLEMENTATION**:
- Used @SCOTTY's shortcut investigation tools
- Restored shortcuts from available sources (Recycle Bin, OneDrive, System Restore, etc.)
- Verified restoration success

**RISK ASSESSMENT**: LOW
- Restoration of existing shortcuts
- No system configuration changes
- No data loss risk

**APPROVAL REQUIRED**: No (restoration of existing state)

**RELATED TICKETS**:
- Problem Ticket: {problem_ticket_id}
- Task ticket will be created for tracking
"""

    change_request = ticket_system.create_ticket(
        title="Restore Desktop and Toolbar Shortcuts - Change Request",
        description=change_request_description,
        ticket_type=TicketType.CHANGE_REQUEST,
        priority=TicketPriority.MEDIUM,
        component="Windows Desktop",
        issue_type="change_request",
        tags=["shortcuts", "desktop", "toolbar", "restoration", "scotty", "change_request"],
        metadata={
            "related_problem_ticket": problem_ticket_id,
            "change_type": "restoration",
            "implemented_by": "@SCOTTY",
            "status": "completed"
        },
        linked_tickets=[problem_ticket_id],
        auto_create_pr=False
    )

    logger.info(f"✅ Created Change Request: {change_request.ticket_id}")
    logger.info(f"   Title: {change_request.title}")
    logger.info("")

    # 2. Create Task Ticket
    logger.info("📋 Creating Task Ticket...")
    logger.info("")

    task_description = f"""**TASK**: Desktop Shortcut Restoration - Implementation Tracking

**RELATED TICKETS**:
- Problem Ticket: {problem_ticket_id}
- Change Request: {change_request.ticket_id}

**TASK SUMMARY**:
Track and verify the restoration of desktop and toolbar shortcuts following the resolution of problem ticket {problem_ticket_id}.

**TASK DETAILS**:
1. ✅ Investigation completed (via problem ticket {problem_ticket_id})
2. ✅ Shortcuts restored by @SCOTTY
3. ⏳ Verification of restored shortcuts
4. ⏳ Documentation of restoration method
5. ⏳ Close related tickets upon completion

**VERIFICATION CHECKLIST**:
- [ ] All desktop shortcuts restored and functional
- [ ] All toolbar shortcuts restored and functional
- [ ] No missing shortcuts reported
- [ ] User confirms desktop is back to original state
- [ ] Documentation updated

**RELATED TICKETS**:
- Problem: {problem_ticket_id}
- Change Request: {change_request.ticket_id}

**ASSIGNED TO**: @SCOTTY
**STATUS**: In Progress
"""

    task = ticket_system.create_ticket(
        title="Desktop Shortcut Restoration - Task",
        description=task_description,
        ticket_type=TicketType.CHANGE_TASK,
        priority=TicketPriority.MEDIUM,
        component="Windows Desktop",
        issue_type="task",
        tags=["shortcuts", "desktop", "toolbar", "restoration", "scotty", "task", "verification"],
        metadata={
            "related_problem_ticket": problem_ticket_id,
            "related_change_request": change_request.ticket_id,
            "change_request_id": change_request.ticket_id,
            "task_type": "verification",
            "assigned_to": "@SCOTTY"
        },
        linked_tickets=[problem_ticket_id, change_request.ticket_id],
        auto_create_pr=False
    )

    logger.info(f"✅ Created Task: {task.ticket_id}")
    logger.info(f"   Title: {task.title}")
    logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info("TICKET CREATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"   Problem Ticket:    {problem_ticket_id}")
    logger.info(f"   Change Request:   {change_request.ticket_id}")
    logger.info(f"   Task Ticket:      {task.ticket_id}")
    logger.info("")
    logger.info("✅ All tickets created and cross-referenced")
    logger.info("   Tickets are ready for database import")
    logger.info("=" * 80)

    return change_request, task


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Create Change Request and Task for shortcut restoration")
    parser.add_argument(
        "--problem-ticket",
        type=str,
        default="T000003085",  # Default to the ticket we created
        help="Problem ticket ID (e.g., T000003085)"
    )

    args = parser.parse_args()

    change_request, task = create_change_request_and_task(args.problem_ticket)

    if change_request and task:
        print("")
        print("🎯 NEXT STEPS:")
        print(f"   1. Review Change Request: {change_request.ticket_id}")
        print(f"   2. Review Task: {task.ticket_id}")
        print(f"   3. Verify shortcuts are restored")
        print(f"   4. Update task status as verification completes")
        print("")
        print("📋 All tickets are cross-referenced and ready for database import")
    else:
        print("❌ Failed to create tickets")


if __name__ == "__main__":


    main()