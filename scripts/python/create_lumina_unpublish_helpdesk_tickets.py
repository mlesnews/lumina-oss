#!/usr/bin/env python3
"""
Create Helpdesk tickets (PM, C, T) for Lumina extension unpublish task.

#automation: Run from repo root: python scripts/python/create_lumina_unpublish_helpdesk_tickets.py

Routes the "unpublish Lumina extensions from all marketplaces" task through the Helpdesk.
Creates PM (Problem), C (Change Request), T (Task) and assigns to helpdesk_support.
See docs/system/REMOVE_LUMINA_FROM_ALL_MARKETPLACES.md and LUMINA_UNPUBLISH_VIA_HELPDESK.md.

Tags: #JARVIS #HELPDESK #LUMINA #UNPUBLISH @JARVIS @HELPDESK
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "python"))

def main() -> int:
    try:
        from jarvis_helpdesk_ticket_system import (
            JARVISHelpdeskTicketSystem,
            TicketPriority,
            TicketType,
        )
    except ImportError as e:
        print(f"Helpdesk ticket system not available: {e}", file=sys.stderr)
        return 1

    C3PO_AVAILABLE = False
    try:
        from jarvis_c3po_ticket_assigner import C3POTicketAssigner
        C3PO_AVAILABLE = True
    except ImportError:
        pass

    helpdesk = JARVISHelpdeskTicketSystem(project_root=REPO_ROOT)
    c3po = C3POTicketAssigner(REPO_ROOT) if C3PO_AVAILABLE else None

    pm_desc = """**PROBLEM TICKET**

Lumina extensions (Core, Premium, Unified Queue, Footer Ticker, File Auto-Close) were published to marketplace(s) despite policy: do not publish until prod-ready; VSIX only. Lumina Premium is a private paid add-on and must not be listed publicly.

**RCA**: AI (agent) published — not human. See docs/system/LUMINA_EXTENSION_NEVER_PUBLISH_WHY.md.

**Required**: Remove all five Lumina extensions from VS Code Marketplace and Open VSX. Full steps: docs/system/REMOVE_LUMINA_FROM_ALL_MARKETPLACES.md.

**Created by:** create_lumina_unpublish_helpdesk_tickets.py
**Automation:** @JARVIS @HELPDESK"""

    c_desc = """**CHANGE REQUEST TICKET**

**Problem**: Lumina extensions published to marketplaces (policy breach; Premium is paid add-on).

**Required changes**:
1. Unpublish/remove all five Lumina extensions from VS Code Marketplace (https://marketplace.visualstudio.com/manage).
2. Unpublish/remove all five from Open VSX (https://open-vsx.org).
3. Verify search "LUMINA" returns no Lumina extensions; use only VSIX install (BDA).

**Checklist**: VS Code Marketplace done | Open VSX done | Verification done.

**Docs**: docs/system/REMOVE_LUMINA_FROM_ALL_MARKETPLACES.md

**Created by:** create_lumina_unpublish_helpdesk_tickets.py
**Automation:** @JARVIS @HELPDESK"""

    t_desc = """**TASK TICKET**

**Objective**: Execute unpublish of all Lumina extensions from all marketplace sources.

**Steps**:
1. Sign in to VS Code Marketplace (publisher: lumina), unpublish/remove: lumina-core, lumina-premium, lumina-unified-queue, lumina-footer-ticker, lumina-file-auto-close.
2. Sign in to Open VSX (publisher: lumina), unpublish/remove the same five.
3. Verify no Lumina extensions appear in search; ensure local install is VSIX only (BDA).

**Linked**: PM (problem), C (change request). **Docs**: docs/system/REMOVE_LUMINA_FROM_ALL_MARKETPLACES.md

**Created by:** create_lumina_unpublish_helpdesk_tickets.py
**Automation:** @JARVIS @HELPDESK"""

    created = {}
    try:
        pm = helpdesk.create_ticket(
            title="[PM] Lumina extensions published to marketplaces — must unpublish",
            description=pm_desc,
            ticket_type=TicketType.PROBLEM,
            priority=TicketPriority.HIGH,
            component="Lumina Extensions",
            issue_type="policy_breach_marketplace_publish",
        )
        if pm:
            created["PM"] = pm.ticket_id
            print(f"Created PM: {pm.ticket_id}")
    except Exception as e:
        print(f"PM ticket failed: {e}", file=sys.stderr)

    try:
        c = helpdesk.create_ticket(
            title="[C] Change: Unpublish Lumina extensions from all marketplaces",
            description=c_desc,
            ticket_type=TicketType.CHANGE_REQUEST,
            priority=TicketPriority.HIGH,
            component="Lumina Extensions",
            issue_type="unpublish_marketplace",
            linked_tickets=[created["PM"]] if created.get("PM") else None,
        )
        if c:
            created["C"] = c.ticket_id
            print(f"Created C: {c.ticket_id}")
    except Exception as e:
        print(f"C ticket failed: {e}", file=sys.stderr)

    try:
        t = helpdesk.create_ticket(
            title="[T] Task: Unpublish Lumina extensions from VS Code Marketplace and Open VSX",
            description=t_desc,
            ticket_type=TicketType.CHANGE_TASK,
            priority=TicketPriority.HIGH,
            component="Lumina Extensions",
            issue_type="task_unpublish_marketplace",
            linked_tickets=[t for t in [created.get("PM"), created.get("C")] if t],
        )
        if t:
            created["T"] = t.ticket_id
            print(f"Created T: {t.ticket_id}")
    except Exception as e:
        print(f"T ticket failed: {e}", file=sys.stderr)

    if c3po and created:
        print("Assigning tickets to helpdesk_support...")
        for tid, ticket_id in created.items():
            if ticket_id:
                try:
                    result = c3po.assign_ticket_to_team(
                        ticket_number=ticket_id, team_id="helpdesk_support", auto_detect=True
                    )
                    if result.get("success"):
                        print(f"  {ticket_id} -> helpdesk_support")
                    else:
                        print(f"  {ticket_id} assignment: {result.get('error', 'Unknown')}", file=sys.stderr)
                except Exception as e:
                    print(f"  {ticket_id} assign failed: {e}", file=sys.stderr)
    elif not c3po and created:
        print("C-3PO assigner not available; tickets created but not assigned. Assign manually or run C3PO assigner.")

    if created:
        print(f"\nDone. Tickets: PM={created.get('PM')} C={created.get('C')} T={created.get('T')}")
        print("See docs/system/REMOVE_LUMINA_FROM_ALL_MARKETPLACES.md for unpublish steps.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
