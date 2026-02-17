#!/usr/bin/env python3
"""
JARVIS Automatic Ticket Creation
Automatically creates helpdesk tickets for all detected problems

Tags: #JARVIS #HELPDESK #WORKFLOWS #AUTOMATION @JARVIS @HELPDESK
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_physician_heal_thyself import JARVISPhysician
from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem, TicketPriority, TicketStatus
from lumina_logger import get_logger

logger = get_logger("JARVISAutoCreateTickets")


def main():
    """Automatically create tickets for all detected issues"""
    logger.info("=" * 80)
    logger.info("🎫 JARVIS AUTOMATIC TICKET CREATION")
    logger.info("=" * 80)
    logger.info("")

    project_root = Path(__file__).parent.parent.parent

    # Initialize systems
    physician = JARVISPhysician(project_root=project_root)
    ticket_system = JARVISHelpdeskTicketSystem(project_root=project_root)

    # Diagnose issues
    logger.info("1️⃣  Diagnosing system issues...")
    diagnoses = physician.diagnose()

    if not diagnoses:
        logger.info("✅ No issues detected - system is healthy")
        return 0

    logger.info(f"   Found {len(diagnoses)} issue(s)")
    logger.info("")

    # Create tickets for each diagnosis
    logger.info("2️⃣  Creating helpdesk tickets...")
    created_tickets = []

    for diagnosis in diagnoses:
        try:
            ticket = ticket_system.create_ticket_from_diagnosis(
                diagnosis=diagnosis,
                auto_create_pr=True,
                auto_heal=True
            )
            created_tickets.append(ticket)
            logger.info(f"   ✅ Created ticket: {ticket.ticket_id} - {ticket.title}")
        except Exception as e:
            logger.error(f"   ❌ Failed to create ticket for {diagnosis.component}: {e}")

    logger.info("")
    logger.info("3️⃣  Creating tickets for known issues...")

    # Create ticket for Bedrock routing issue
    try:
        bedrock_ticket = ticket_system.create_ticket(
            title="Cursor Bedrock Routing Issue - Local models being sent to Bedrock",
            description="""**Issue**: Cursor is attempting to route local Ollama models (ULTRON/qwen2.5:72b) through AWS Bedrock, causing "Selected model is not supported by bedrock" errors.

**Component**: Cursor IDE Configuration

**Root Cause**: Cursor settings.json routing configuration incorrectly sending local models to Bedrock instead of Ollama

**Symptoms**:
- Error: "Selected model is not supported by bedrock, please use a different model"
- Local models (ULTRON, qwen2.5:72b) failing to load
- Bedrock attempting to handle local models

**Fix**: Run `fix_cursor_bedrock_routing.py` to correct routing configuration

**Priority**: CRITICAL - Blocks local-first AI operations
""",
            priority=TicketPriority.CRITICAL,
            component="Cursor IDE",
            issue_type="configuration",
            tags=["bedrock", "routing", "cursor", "local-first", "critical"],
            metadata={
                'fix_script': 'scripts/python/fix_cursor_bedrock_routing.py',
                'detected_by': 'User report'
            },
            auto_create_pr=True
        )
        created_tickets.append(bedrock_ticket)
        logger.info(f"   ✅ Created ticket: {bedrock_ticket.ticket_id}")
    except Exception as e:
        logger.error(f"   ❌ Failed to create Bedrock ticket: {e}")

    # Create ticket for Git "too many active changes" warning
    try:
        git_ticket = ticket_system.create_ticket(
            title="Git Repository: Too Many Active Changes Warning",
            description="""**Issue**: Git repository at project root has too many active changes, limiting Git features.

**Component**: Git Repository

**Root Cause**: Large number of uncommitted changes in working directory

**Symptoms**:
- Warning: "The git repository has too many active changes, only a subset of Git features will be enabled"
- Limited Git/GitLens functionality
- Potential performance issues

**Recommended Actions**:
1. Review uncommitted changes
2. Commit or stash changes appropriately
3. Consider .gitignore updates if many files shouldn't be tracked

**Priority**: MEDIUM - Affects Git workflow efficiency
""",
            priority=TicketPriority.MEDIUM,
            component="Git Repository",
            issue_type="workflow",
            tags=["git", "repository", "changes", "gitlens"],
            metadata={
                'detected_by': 'User report'
            },
            auto_create_pr=True
        )
        created_tickets.append(git_ticket)
        logger.info(f"   ✅ Created ticket: {git_ticket.ticket_id}")
    except Exception as e:
        logger.error(f"   ❌ Failed to create Git ticket: {e}")

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ TICKET CREATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"   Total tickets created: {len(created_tickets)}")
    logger.info("")
    logger.info("📋 Created tickets:")
    for ticket in created_tickets:
        logger.info(f"   • {ticket.ticket_id}: {ticket.title} [{ticket.priority.value}]")
    logger.info("")

    return 0


if __name__ == "__main__":


    sys.exit(main())