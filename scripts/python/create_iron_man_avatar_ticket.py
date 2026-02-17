#!/usr/bin/env python3
"""
Create Helpdesk Ticket for Iron Man Avatar Desktop Walking

Creates a helpdesk ticket to investigate and fix why Iron Man AI avatars
aren't available to walk on desktop like Ace.

Tags: #HELPDESK #TICKET #IRON_MAN #AVATAR #DESKTOP #REQUIRED @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from datetime import datetime

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

logger = get_logger("CreateIronManAvatarTicket")

try:
    from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem, TicketPriority, TicketStatus
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    SYSTEMS_AVAILABLE = False
    logger.error(f"Systems not available: {e}")


def create_iron_man_avatar_ticket():
    """Create helpdesk ticket for Iron Man avatar desktop walking"""

    if not SYSTEMS_AVAILABLE:
        logger.error("❌ Helpdesk systems not available")
        return False

    ticket_system = JARVISHelpdeskTicketSystem(project_root)
    assigner = C3POTicketAssigner(project_root)

    logger.info("=" * 80)
    logger.info("🎫 CREATING HELPDESK TICKET: IRON MAN AVATAR DESKTOP WALKING")
    logger.info("=" * 80)

    # Create ticket
    ticket = ticket_system.create_ticket(
        title="Iron Man AI Avatars Not Available for Desktop Walking Like Ace",
        description="""
**Issue**: Iron Man AI avatars are not available to walk on the desktop like Ace does.

**Current Status**:
- Ace successfully walks casually around desktop (stoic behavior)
- Iron Man animated VA exists (`ironman_animated_va.py`) but desktop walking not functional
- Iron Man avatar should have same desktop walking capabilities as Ace

**Expected Behavior**:
- Iron Man avatars should walk around desktop like Ace
- Casual movement around desktop
- Transparent window, always on top
- Draggable character
- Animated arc reactor while walking

**Reference Implementation**:
- Ace (ACVA) - Master implementation
- Kenny (IMVA) - Padawan learning from Ace
- Documentation: `docs/system/KENNY_KENJAR_LAB_EXPERIMENT_COMPLETE.md`
- Iron Man VA: `scripts/python/ironman_animated_va.py`

**Root Cause Analysis Needed**:
1. Check if desktop walking mechanics are implemented in Iron Man VA
2. Compare with Ace implementation to identify gaps
3. Verify desktop integration and window management
4. Test wandering behavior and movement patterns

**Priority**: HIGH - Feature parity with Ace is important for user experience
        """.strip(),
        priority=TicketPriority.HIGH,
        component="Avatar & Desktop Visualization",
        issue_type="feature",
        tags=["#avatar", "#desktop", "#iron_man", "#ace", "#desktop_walking", "@desktop"],
        metadata={
            "related_files": [
                "scripts/python/ironman_animated_va.py",
                "scripts/python/character_avatar_manager.py",
                "scripts/python/va_desktop_visualization.py",
                "docs/system/KENNY_KENJAR_LAB_EXPERIMENT_COMPLETE.md",
                "docs/system/IRON_MAN_ANIMATED_VA_CREATED.md"
            ],
            "reference_implementation": "Ace (ACVA) desktop walking",
            "request_id": "45199e50-8c15-46e6-b1ea-9e6ad674ba89"
        },
        auto_create_pr=False
    )

    logger.info(f"✅ Ticket created: {ticket.ticket_id}")

    # Assign to Avatar & Desktop team
    logger.info("")
    logger.info("=" * 80)
    logger.info("👥 ASSIGNING TICKET TO AVATAR & DESKTOP TEAM")
    logger.info("=" * 80)

    assignment_result = assigner.assign_ticket_to_team(
        ticket_number=ticket.ticket_id,
        team_id="avatar_desktop",
        auto_detect=False
    )

    if assignment_result.get("success"):
        logger.info("✅ Ticket assigned to Avatar & Desktop Visualization Team")
        logger.info(f"   Team: {assignment_result.get('team_name', 'Avatar & Desktop')}")
        logger.info(f"   Primary Assignee: {assignment_result.get('primary_assignee', '@r2d2')}")
        logger.info(f"   Technical Lead: {assignment_result.get('technical_lead', '@r2d2')}")
    else:
        logger.warning(f"⚠️  Assignment failed: {assignment_result.get('error', 'Unknown error')}")
        logger.info("   Ticket created but needs manual assignment")

    logger.info("=" * 80)
    logger.info(f"📋 Ticket Summary:")
    logger.info(f"   ID: {ticket.ticket_id}")
    logger.info(f"   Title: {ticket.title}")
    logger.info(f"   Status: {ticket.status.value}")
    logger.info(f"   Priority: {ticket.priority.value}")
    logger.info("=" * 80)

    return ticket


if __name__ == "__main__":
    ticket = create_iron_man_avatar_ticket()
    if ticket:
        logger.info("✅ Ticket creation complete!")
        sys.exit(0)
    else:
        logger.error("❌ Ticket creation failed")
        sys.exit(1)
