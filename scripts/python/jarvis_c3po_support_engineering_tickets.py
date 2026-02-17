#!/usr/bin/env python3
"""
JARVIS C-3PO Support Engineering Team Ticket Creator
Creates tickets for Support Engineering team to investigate issues

Tags: #C3PO #HELPDESK #SUPPORT_ENGINEERING #TICKETS @C3PO @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_helpdesk_ticket_system import (
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketStatus,
        TicketType
    )
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("JARVISC3POSupportEngineeringTickets")


def create_support_engineering_tickets(project_root: Path = None) -> Dict[str, Any]:
    try:
        """C-3PO creates tickets for Support Engineering team"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        logger.info("=" * 80)
        logger.info("🎫 @C3PO Creating Support Engineering Team Tickets")
        logger.info("=" * 80)

        # Initialize systems
        helpdesk_system = JARVISHelpdeskTicketSystem(project_root)
        c3po_assigner = C3POTicketAssigner(project_root)

        # Issues to investigate
        issues = [
            {
                "title": "KAIJU Docker Context Connection Timeout Investigation",
                "description": """Investigate Docker context connection timeouts when connecting to KAIJU (<NAS_IP>).

ISSUE:
- Docker context 'kaiju' created successfully (ssh://root@<NAS_IP>)
- Context switching works (docker context use kaiju succeeds)
- Docker commands via context timing out (docker images, docker ps)
- SSH root access available with registered keys
- Direct SSH connection works but Docker commands timeout

ROOT CAUSE ANALYSIS NEEDED:
1. Check Docker daemon status on KAIJU
2. Verify Docker socket accessibility via SSH
3. Check network connectivity and latency
4. Verify SSH tunnel configuration
5. Check Docker context SSH configuration
6. Investigate PowerShell/SSH interaction issues

EXPECTED RESULT:
- Docker commands via context should work without timeout
- Full verification of kali-hardened-millennium-falc images on KAIJU
- Resolution of connection timeout issues

PRIORITY: HIGH - Blocks verification of hardened Kali images on KAIJU""",
            "priority": TicketPriority.HIGH,
            "component": "Docker",
            "issue_type": "Infrastructure - Docker Context"
        },
        {
            "title": "Kali Hardened Image Verification - KAIJU",
            "description": """Verify kali-hardened-millennium-falc images on KAIJU desktop system.

REQUIREMENT:
- Verify KAIJU has kali-hardened-millennium-falc:latest image
- Verify Kaiju containers are built from hardened base
- Confirm both MILLENIUM_FALC and KAIJU use same hardened image

CURRENT STATUS:
- MILLENIUM_FALC (laptop): ✅ Verified - has kali-hardened-millennium-falc:latest
- KAIJU (desktop): ⚠️ Needs verification - Docker context timeout blocking

DOCKERFILE CONFIGURATION:
- containerization/services/kaju_remote_admin/Dockerfile.kali uses:
  FROM kali-hardened-millennium-falc:latest

ACTION REQUIRED:
1. Resolve Docker context timeout (see related ticket)
2. Verify Docker images on KAIJU
3. Confirm Kaiju containers use hardened base
4. Document verification results

PRIORITY: HIGH - Security compliance requirement""",
            "priority": TicketPriority.HIGH,
            "component": "Security",
            "issue_type": "Security - Image Verification"
        },
        {
            "title": "Docker Context SSH Configuration Optimization",
            "description": """Optimize Docker context SSH configuration for remote Docker access.

ISSUE:
- Docker context using SSH (ssh://root@<NAS_IP>) timing out
- Need to optimize SSH configuration for Docker remote access
- May need Docker daemon socket forwarding or alternative connection method

INVESTIGATION AREAS:
1. Docker daemon socket forwarding via SSH
2. Alternative connection methods (TCP, TLS)
3. SSH configuration optimization
4. Network latency and timeout settings
5. Docker context configuration parameters

RECOMMENDATIONS NEEDED:
- Best practice for remote Docker access
- Optimal SSH configuration
- Alternative connection methods if SSH not suitable
- Performance optimization strategies

PRIORITY: MEDIUM - Optimization task""",
            "priority": TicketPriority.MEDIUM,
            "component": "Docker",
            "issue_type": "Infrastructure - Optimization"
        }
        ]

        tickets_created = []

        for issue in issues:
            try:
                # C-3PO creates ticket
                ticket = helpdesk_system.create_ticket(
                    title=issue["title"],
                    description=issue["description"],
                    ticket_type=TicketType.PROBLEM,
                    priority=issue["priority"],
                    component=issue["component"],
                    issue_type=issue["issue_type"],
                    tags=["SUPPORT-ENGINEERING", "DOCKER", "KAIJU", "KALI-HARDENED", "@C3PO", "@JARVIS"],
                    metadata={
                        "created_by": "@C3PO",
                        "coordinator": "@C3PO",
                        "workflow": "@C3PO @TRIAGE → @HELPDESK",
                        "investigation_required": True
                    }
                )

                tickets_created.append(ticket)
                logger.info(f"✅ C-3PO created ticket {ticket.ticket_id}: {issue['title']}")

                # C-3PO assigns to Support Engineering team
                # Try to find support engineering team
                assignment_result = c3po_assigner.assign_ticket_to_team(
                    ticket_number=ticket.ticket_id,
                    team_id="helpdesk_support",  # Using helpdesk_support as closest match
                    auto_detect=False
                )

                if assignment_result.get("success"):
                    logger.info(f"✅ C-3PO assigned ticket {ticket.ticket_id} to team")
                else:
                    logger.warning(f"⚠️  C-3PO assignment result: {assignment_result}")

            except Exception as e:
                logger.error(f"❌ C-3PO failed to create ticket: {e}", exc_info=True)

        result = {
            "coordinator": "@C3PO",
            "tickets_created": len(tickets_created),
            "tickets": [ticket.to_dict() for ticket in tickets_created],
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"\n📊 @C3PO Support Engineering Tickets Summary:")
        logger.info(f"   Total Tickets Created: {result['tickets_created']}")
        logger.info(f"   Coordinator: @C3PO")

        return result
    except Exception as e:
        logger.error(f"Error in create_support_engineering_tickets: {e}", exc_info=True)
        raise


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="C-3PO Support Engineering Ticket Creator")
    args = parser.parse_args()

    print("="*80)
    print("🎫 JARVIS C-3PO SUPPORT ENGINEERING TICKET CREATOR")
    print("="*80)
    print()
    print("Coordinator: @C3PO (Helpdesk Coordinator)")
    print("Team: Support Engineering")
    print()

    result = create_support_engineering_tickets()

    print()
    print("="*80)
    print("✅ TICKETS CREATED")
    print("="*80)
    print(f"Total Tickets: {result['tickets_created']}")
    print(f"Coordinator: @C3PO")
    print()

    for ticket in result['tickets']:
        print(f"  {ticket['ticket_id']}: {ticket['title']}")
        print(f"    Status: {ticket['status']}")
        print(f"    Priority: {ticket['priority']}")
        print()


if __name__ == "__main__":


    main()