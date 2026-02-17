#!/usr/bin/env python3
"""
@SCOTTY's Shortcut Issue Workflow
First contacts helpdesk, then investigates and resolves

Tags: #SCOTTY #SHORTCUTS #HELPDESK #WORKFLOW #DESKTOP #TOOLBAR @SCOTTY @LUMINA @HELPDESK
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SCOTTYShortcutWorkflow")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SCOTTYShortcutWorkflow")

try:
    from scripts.python.jarvis_helpdesk_ticket_system import (
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketType
    )
    HELPDESK_AVAILABLE = True
except ImportError:
    HELPDESK_AVAILABLE = False
    logger.warning("⚠️  Helpdesk ticket system not available")


def create_helpdesk_ticket():
    """Step 1: Create helpdesk ticket with issue details and common causes"""
    logger.info("=" * 80)
    logger.info("📞 STEP 1: CONTACTING HELPDESK")
    logger.info("=" * 80)
    logger.info("")

    if not HELPDESK_AVAILABLE:
        logger.error("❌ Helpdesk system not available - cannot create ticket")
        logger.info("   Proceeding with investigation only...")
        return None

    try:
        ticket_system = JARVISHelpdeskTicketSystem(project_root=project_root)

        description = """**ISSUE**: Desktop and toolbar shortcuts disappeared after system reboot.

**SYMPTOMS**:
- Desktop shortcuts are missing
- Toolbar (taskbar) shortcuts are missing
- Shortcuts did not survive the previous reboot
- User has been static for a while, unsure what happened

**COMMON CAUSES** (to be investigated):

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

**INVESTIGATION PLAN**:
1. Run shortcut investigation script to check all locations
2. Check for temporary profile
3. Check Recycle Bin for deleted shortcuts
4. Check OneDrive sync status
5. Check System Restore points
6. Review Windows Event Viewer for profile errors
7. Attempt restoration from available sources

**PRIORITY**: MEDIUM (affects productivity but system is functional)

**ASSIGNED TO**: @SCOTTY (Windows Systems Architect)
**INVESTIGATION TOOLS**: 
- `scripts/powershell/scotty-investigate-shortcuts.ps1`
- `scripts/powershell/scotty-restore-shortcuts.ps1`
"""

        ticket = ticket_system.create_ticket(
            title="Desktop and Toolbar Shortcuts Missing After Reboot",
            description=description,
            ticket_type=TicketType.CHANGE_TASK,
            priority=TicketPriority.MEDIUM,
            component="Windows Desktop",
            issue_type="bug",
            tags=["shortcuts", "desktop", "toolbar", "reboot", "windows-profile", "scotty"],
            metadata={
                "investigation_script": "scripts/powershell/scotty-investigate-shortcuts.ps1",
                "restoration_script": "scripts/powershell/scotty-restore-shortcuts.ps1",
                "assigned_agent": "@SCOTTY",
                "issue_category": "windows_profile",
                "common_causes": [
                    "Temporary user profile",
                    "OneDrive sync issue",
                    "Accidental deletion",
                    "Windows profile corruption",
                    "System restore or profile reset"
                ]
            },
            auto_create_pr=False
        )

        logger.info(f"✅ Created helpdesk ticket: {ticket.ticket_id}")
        logger.info(f"   Title: {ticket.title}")
        logger.info(f"   Priority: {ticket.priority.value}")
        logger.info(f"   Status: {ticket.status.value}")
        logger.info("")
        logger.info("📋 Ticket details saved to helpdesk system")
        logger.info("")

        return ticket

    except Exception as e:
        logger.error(f"❌ Failed to create helpdesk ticket: {e}")
        logger.info("   Proceeding with investigation anyway...")
        return None


def run_investigation():
    """Step 2: Run shortcut investigation"""
    logger.info("=" * 80)
    logger.info("🔍 STEP 2: RUNNING INVESTIGATION")
    logger.info("=" * 80)
    logger.info("")

    investigation_script = project_root / "scripts" / "powershell" / "scotty-investigate-shortcuts.ps1"

    if not investigation_script.exists():
        logger.error(f"❌ Investigation script not found: {investigation_script}")
        return False

    logger.info(f"Running: {investigation_script}")
    logger.info("")

    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(investigation_script), "-Detailed"],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )

        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            logger.warning("Stderr output:")
            print(result.stderr)

        if result.returncode == 0:
            logger.info("")
            logger.info("✅ Investigation completed successfully")
            logger.info(f"   Report saved to: data/scotty_shortcut_investigation.json")
            return True
        else:
            logger.error(f"❌ Investigation failed with exit code: {result.returncode}")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to run investigation: {e}")
        return False


def attempt_restoration():
    """Step 3: Attempt to restore shortcuts"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("🔧 STEP 3: ATTEMPTING RESTORATION")
    logger.info("=" * 80)
    logger.info("")

    restoration_script = project_root / "scripts" / "powershell" / "scotty-restore-shortcuts.ps1"

    if not restoration_script.exists():
        logger.error(f"❌ Restoration script not found: {restoration_script}")
        return False

    logger.info("Checking Recycle Bin and OneDrive for shortcuts...")
    logger.info("")

    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(restoration_script), 
             "-FromRecycleBin", "-CheckOneDrive", "-DryRun"],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )

        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            logger.warning("Stderr output:")
            print(result.stderr)

        logger.info("")
        logger.info("📋 Dry run completed - review output above")
        logger.info("   To actually restore, run without -DryRun flag")
        logger.info("")
        logger.info("   Example:")
        logger.info("   .\\scripts\\powershell\\scotty-restore-shortcuts.ps1 -FromRecycleBin -CheckOneDrive")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to run restoration: {e}")
        return False


def main():
    """Main workflow: Helpdesk -> Investigation -> Restoration"""
    logger.info("=" * 80)
    logger.info("@SCOTTY's Shortcut Issue Workflow")
    logger.info("USS Lumina - @scotty (Windows Systems Architect)")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Workflow: Helpdesk Ticket → Investigation → Restoration")
    logger.info("")

    # Step 1: Create helpdesk ticket
    ticket = create_helpdesk_ticket()

    if ticket:
        logger.info("")
        logger.info("⏸️  Waiting for helpdesk ticket creation to complete...")
        logger.info("")

    # Step 2: Run investigation
    investigation_success = run_investigation()

    # Step 3: Attempt restoration (dry run first)
    if investigation_success:
        restoration_success = attempt_restoration()
    else:
        logger.warning("⚠️  Skipping restoration due to investigation failure")
        restoration_success = False

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("WORKFLOW SUMMARY")
    logger.info("=" * 80)
    logger.info(f"   Helpdesk Ticket: {'✅ Created' if ticket else '⚠️  Skipped'}")
    logger.info(f"   Investigation: {'✅ Completed' if investigation_success else '❌ Failed'}")
    logger.info(f"   Restoration Check: {'✅ Completed' if restoration_success else '❌ Failed'}")
    logger.info("")

    if ticket:
        logger.info(f"📋 Next Steps:")
        logger.info(f"   1. Review investigation report: data/scotty_shortcut_investigation.json")
        logger.info(f"   2. Review ticket: {ticket.ticket_id}")
        logger.info(f"   3. If shortcuts found, run restoration without -DryRun flag")
        logger.info("")

    logger.info("=" * 80)
    logger.info("Workflow complete. Review results and proceed with restoration if needed.")
    logger.info("=" * 80)


if __name__ == "__main__":


    main()