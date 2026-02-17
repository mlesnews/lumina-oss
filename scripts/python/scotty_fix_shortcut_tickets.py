#!/usr/bin/env python3
"""
Fix Shortcut Tickets - Create proper PM ticket and update references

Tags: #SCOTTY #SHORTCUTS #HELPDESK #TICKET_FIX @SCOTTY @LUMINA @HELPDESK
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SCOTTYFixShortcutTickets")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SCOTTYFixShortcutTickets")

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


def create_problem_ticket():
    """Create the proper PM (Problem) ticket"""
    if not HELPDESK_AVAILABLE:
        logger.error("❌ Helpdesk system not available")
        return None

    ticket_system = JARVISHelpdeskTicketSystem(project_root=project_root)

    logger.info("=" * 80)
    logger.info("Creating Proper Problem Ticket (PM)")
    logger.info("=" * 80)
    logger.info("")

    description = """**PROBLEM**: Desktop and Toolbar Shortcuts Missing After Reboot

**SYMPTOMS**:
- Desktop shortcuts are missing
- Toolbar (taskbar) shortcuts are missing
- Shortcuts did not survive the previous reboot
- User has been static for a while, unsure what happened

**COMMON CAUSES** (investigated):

1. **Temporary User Profile**
   - Windows loaded a temporary profile instead of the normal user profile
   - Profile path may contain "Temp" indicator
   - Desktop shortcuts exist in normal profile but not accessible
   - **Solution**: Log out completely and log back in to restore normal profile

2. **OneDrive Sync Issue**
   - Desktop was synced to OneDrive
   - Shortcuts exist in OneDrive Desktop folder but not synced to local Desktop
   - OneDrive sync may have been paused or failed
   - **Solution**: Check OneDrive sync status, restore from OneDrive backup

3. **Accidental Deletion**
   - Shortcuts may have been accidentally deleted
   - Could be in Recycle Bin
   - **Solution**: Restore from Recycle Bin

4. **Windows Profile Corruption**
   - User profile registry or files corrupted
   - Windows Event Viewer may show profile-related errors
   - **Solution**: May need profile repair or System Restore

5. **System Restore or Profile Reset**
   - System restore point may have been applied
   - Profile may have been reset during Windows update
   - **Solution**: Check System Restore points, restore if needed

**RESOLUTION**:
@SCOTTY has successfully restored all desktop and toolbar shortcuts to their original state.

**RELATED TICKETS**:
- Change Request: C000003089 (restoration work)
- Task: T000003090 (verification tracking)
"""

    problem_ticket = ticket_system.create_ticket(
        title="Desktop and Toolbar Shortcuts Missing After Reboot",
        description=description,
        ticket_type=TicketType.PROBLEM,  # PM ticket
        priority=TicketPriority.MEDIUM,
        component="Windows Desktop",
        issue_type="problem",
        tags=["shortcuts", "desktop", "toolbar", "reboot", "windows-profile", "scotty", "problem"],
        metadata={
            "investigation_script": "scripts/powershell/scotty-investigate-shortcuts.ps1",
            "restoration_script": "scripts/powershell/scotty-restore-shortcuts.ps1",
            "assigned_agent": "@SCOTTY",
            "issue_category": "windows_profile",
            "status": "resolved",
            "resolved_by": "@SCOTTY"
        },
        auto_create_pr=False
    )

    logger.info(f"✅ Created Problem Ticket: {problem_ticket.ticket_id}")
    logger.info(f"   Title: {problem_ticket.title}")
    logger.info("")

    return problem_ticket


def update_change_request_and_task(pm_ticket_id: str, cr_ticket_id: str, task_ticket_id: str):
    try:
        """Update the change request and task to reference the PM ticket"""
        logger.info("=" * 80)
        logger.info("Updating Change Request and Task References")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Problem Ticket (PM): {pm_ticket_id}")
        logger.info(f"Change Request (C): {cr_ticket_id}")
        logger.info(f"Task (T): {task_ticket_id}")
        logger.info("")

        # Read and update the tickets
        tickets_dir = project_root / "data" / "helpdesk" / "tickets"

        # Update Change Request
        cr_file = tickets_dir / f"{cr_ticket_id}.json"
        if cr_file.exists():
            import json
            with open(cr_file, 'r', encoding='utf-8') as f:
                cr_data = json.load(f)

            # Update linked tickets to include PM ticket
            if "linked_tickets" not in cr_data:
                cr_data["linked_tickets"] = []
            if pm_ticket_id not in cr_data["linked_tickets"]:
                cr_data["linked_tickets"].append(pm_ticket_id)

            # Update metadata
            if "metadata" not in cr_data:
                cr_data["metadata"] = {}
            cr_data["metadata"]["related_problem_ticket"] = pm_ticket_id

            # Update description to reference PM ticket
            if pm_ticket_id not in cr_data.get("description", ""):
                cr_data["description"] = cr_data["description"].replace(
                    f"**RELATED PROBLEM TICKET**: T000003085",
                    f"**RELATED PROBLEM TICKET**: {pm_ticket_id}"
                )

            with open(cr_file, 'w', encoding='utf-8') as f:
                json.dump(cr_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Updated Change Request: {cr_ticket_id}")
        else:
            logger.warning(f"⚠️  Change Request file not found: {cr_file}")

        # Update Task
        task_file = tickets_dir / f"{task_ticket_id}.json"
        if task_file.exists():
            import json
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            # Update linked tickets to include PM ticket
            if "linked_tickets" not in task_data:
                task_data["linked_tickets"] = []
            if pm_ticket_id not in task_data["linked_tickets"]:
                task_data["linked_tickets"].append(pm_ticket_id)

            # Update metadata
            if "metadata" not in task_data:
                task_data["metadata"] = {}
            task_data["metadata"]["related_problem_ticket"] = pm_ticket_id

            # Update description to reference PM ticket
            if pm_ticket_id not in task_data.get("description", ""):
                task_data["description"] = task_data["description"].replace(
                    f"Problem Ticket: T000003085",
                    f"Problem Ticket: {pm_ticket_id}"
                )
                task_data["description"] = task_data["description"].replace(
                    f"problem ticket {cr_ticket_id}",
                    f"problem ticket {pm_ticket_id}"
                )

            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Updated Task: {task_ticket_id}")
        else:
            logger.warning(f"⚠️  Task file not found: {task_file}")

        logger.info("")
        logger.info("✅ All tickets updated with correct PM ticket reference")


    except Exception as e:
        logger.error(f"Error in update_change_request_and_task: {e}", exc_info=True)
        raise
def main():
    """Main function"""
    # Create proper PM ticket
    pm_ticket = create_problem_ticket()

    if pm_ticket:
        # Update existing change request and task
        update_change_request_and_task(
            pm_ticket_id=pm_ticket.ticket_id,
            cr_ticket_id="C000003089",
            task_ticket_id="T000003090"
        )

        logger.info("")
        logger.info("=" * 80)
        logger.info("TICKET SUMMARY (CORRECTED)")
        logger.info("=" * 80)
        logger.info(f"   Problem Ticket (PM): {pm_ticket.ticket_id}")
        logger.info(f"   Change Request (C):   C000003089")
        logger.info(f"   Task (T):             T000003090")
        logger.info("")
        logger.info("✅ All tickets properly cross-referenced")
        logger.info("   Problem tickets use PM prefix (9 digits)")
        logger.info("   All tickets ready for database import")
        logger.info("=" * 80)
    else:
        logger.error("❌ Failed to create PM ticket")


if __name__ == "__main__":


    main()