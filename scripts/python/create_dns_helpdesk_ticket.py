#!/usr/bin/env python3
"""
Create DNS Helpdesk Ticket
Creates helpdesk ticket for homelab DNS issue and sets up workflow monitoring

Tags: #HELPDESK #DNS #HOMELAB #WORKFLOW #@DOIT
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CreateDNSHelpdeskTicket")


def create_dns_ticket() -> Dict[str, Any]:
    """Create helpdesk ticket for DNS issue"""
    ticket_id = f"HELPDESK-{datetime.now().strftime('%Y%m%d')}-DNS-HOMELAB"

    ticket = {
        "ticket_id": ticket_id,
        "title": "Homelab DNS Services Not Responding - pfSense and NAS",
        "priority": "HIGH",
        "status": "OPEN",
        "category": "NETWORK",
        "subcategory": "DNS",
        "created": datetime.now().isoformat(),
        "assigned_team": "NETWORK_TEAM",
        "tags": ["#DNS", "#HOMELAB", "#PFSENSE", "#NAS", "#NETWORK", "@JARVIS", "@HELPDESK"],

        "issue_summary": {
            "description": "Both pfSense (<NAS_IP>) and NAS (<NAS_PRIMARY_IP>) DNS services are not responding to queries. DNS port 53 is open but queries timeout.",
            "impact": [
                "Browser cannot resolve DNS when using Wi-Fi adapter (configured to use pfSense DNS)",
                "IPv4 sites appear down in browser",
                "Blocks browser automation workflows",
                "Prevents Fidelity credential extraction automation"
            ],
            "affected_systems": [
                "pfSense (<NAS_IP>) - Primary DNS",
                "NAS (<NAS_PRIMARY_IP>) - Secondary DNS",
                "Wi-Fi Network Adapter (using pfSense DNS)",
                "Browser automation (Neo browser)"
            ]
        },

        "diagnostic_findings": {
            "connectivity": "✅ Both servers reachable (ping works)",
            "dns_port": "✅ Port 53 UDP open on both servers",
            "dns_queries": "❌ All DNS queries timing out",
            "root_cause": "DNS service running but not configured with upstream DNS servers",
            "working_dns": [
                "ProtonVPN DNS (10.2.0.1) - Working",
                "Google DNS (8.8.8.8) - Working"
            ]
        },

        "resolution_steps": {
            "pfSense": [
                "1. Access pfSense Web UI: https://<NAS_IP>",
                "2. Navigate to: Services > DNS Resolver (or DNS Forwarder)",
                "3. Enable DNS service",
                "4. Configure upstream DNS servers:",
                "   - 8.8.8.8 (Google)",
                "   - 1.1.1.1 (Cloudflare)",
                "   - 8.8.4.4 (Google secondary)",
                "5. Enable 'Enable Forwarding Mode' if using DNS Forwarder",
                "6. Save and apply changes",
                "7. Restart DNS service if needed"
            ],
            "NAS": [
                "1. Access NAS Web UI: https://<NAS_PRIMARY_IP>:5001",
                "2. Navigate to: Control Panel > Network > DNS Server",
                "3. Enable DNS service",
                "4. Configure upstream DNS servers (same as pfSense)",
                "5. Save and apply changes",
                "6. Restart DNS service if needed"
            ],
            "verification": [
                "Run: nslookup google.com <NAS_IP>",
                "Run: nslookup google.com <NAS_PRIMARY_IP>",
                "Run: python scripts/python/verify_homelab_dns_fix.py",
                "Test browser connectivity",
                "Retry Fidelity automation workflow"
            ]
        },

        "workflow_monitoring": {
            "enabled": True,
            "check_interval": 300,  # 5 minutes
            "verification_script": "scripts/python/verify_homelab_dns_fix.py",
            "success_criteria": {
                "pfsense_dns": "All test queries successful",
                "nas_dns": "All test queries successful",
                "browser_connectivity": "Sites load correctly"
            },
            "auto_close_on_resolution": True
        },

        "related_tickets": [],
        "related_files": [
            "docs/diagnostics/COMPREHENSIVE_SYSTEM_DIAGNOSTIC_REPORT.md",
            "docs/diagnostics/DNS_VS_REVERSE_DNS_EXPLAINED.md",
            "scripts/python/fix_homelab_dns_services.py",
            "scripts/python/verify_homelab_dns_fix.py"
        ]
    }

    return ticket


def save_ticket(ticket: Dict[str, Any]) -> Path:
    """Save ticket to helpdesk directory"""
    helpdesk_dir = project_root / "docs" / "helpdesk"
    helpdesk_dir.mkdir(parents=True, exist_ok=True)

    ticket_file = helpdesk_dir / f"{ticket['ticket_id']}.md"

    # Generate markdown ticket
    md_content = f"""# Helpdesk Ticket: {ticket['title']}

**Ticket ID**: {ticket['ticket_id']}  
**Priority**: 🔴 **{ticket['priority']}**  
**Status**: 🔍 **{ticket['status']}**  
**Category**: {ticket['category']} / {ticket['subcategory']}  
**Created**: {ticket['created']}  
**Assigned Team**: {ticket['assigned_team']}  
**Tags**: {', '.join(ticket['tags'])}

---

## 📋 Issue Summary

{ticket['issue_summary']['description']}

**Impact**: 
"""

    for impact in ticket['issue_summary']['impact']:
        md_content += f"- {impact}\n"

    md_content += f"""
**Affected Systems**:
"""
    for system in ticket['issue_summary']['affected_systems']:
        md_content += f"- {system}\n"

    md_content += f"""
---

## 🔍 Diagnostic Findings

- **Connectivity**: {ticket['diagnostic_findings']['connectivity']}
- **DNS Port**: {ticket['diagnostic_findings']['dns_port']}
- **DNS Queries**: {ticket['diagnostic_findings']['dns_queries']}
- **Root Cause**: {ticket['diagnostic_findings']['root_cause']}

**Working DNS Servers**:
"""
    for dns in ticket['diagnostic_findings']['working_dns']:
        md_content += f"- {dns}\n"

    md_content += f"""
---

## 🔧 Resolution Steps

### pfSense (<NAS_IP>)
"""
    for step in ticket['resolution_steps']['pfSense']:
        md_content += f"{step}\n"

    md_content += f"""
### NAS (<NAS_PRIMARY_IP>)
"""
    for step in ticket['resolution_steps']['NAS']:
        md_content += f"{step}\n"

    md_content += f"""
### Verification
"""
    for step in ticket['resolution_steps']['verification']:
        md_content += f"- {step}\n"

    md_content += f"""
---

## 📊 Workflow Monitoring

**Status**: {'✅ Enabled' if ticket['workflow_monitoring']['enabled'] else '❌ Disabled'}  
**Check Interval**: {ticket['workflow_monitoring']['check_interval']} seconds  
**Verification Script**: `{ticket['workflow_monitoring']['verification_script']}`

**Success Criteria**:
"""
    for criterion, description in ticket['workflow_monitoring']['success_criteria'].items():
        md_content += f"- **{criterion}**: {description}\n"

    md_content += f"""
**Auto-Close on Resolution**: {'✅ Yes' if ticket['workflow_monitoring']['auto_close_on_resolution'] else '❌ No'}

---

## 📎 Related Files

"""
    for file in ticket['related_files']:
        md_content += f"- `{file}`\n"

    md_content += f"""
---

**Ticket Created By**: JARVIS Helpdesk System  
**Workflow**: @DOIT Autonomous Execution  
**Tags**: {', '.join(ticket['tags'])}
"""

    with open(ticket_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    # Also save JSON
    json_file = helpdesk_dir / f"{ticket['ticket_id']}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(ticket, f, indent=2)

    return ticket_file


def setup_workflow_monitoring(ticket: Dict[str, Any]) -> Dict[str, Any]:
    try:
        """Set up workflow monitoring for the ticket"""
        logger.info("Setting up workflow monitoring...")

        monitoring_config = {
            "ticket_id": ticket['ticket_id'],
            "monitoring_enabled": True,
            "check_interval": ticket['workflow_monitoring']['check_interval'],
            "verification_script": ticket['workflow_monitoring']['verification_script'],
            "success_criteria": ticket['workflow_monitoring']['success_criteria'],
            "auto_close": ticket['workflow_monitoring']['auto_close_on_resolution'],
            "created": datetime.now().isoformat()
        }

        # Save monitoring config
        monitoring_dir = project_root / "data" / "helpdesk" / "monitoring"
        monitoring_dir.mkdir(parents=True, exist_ok=True)

        monitoring_file = monitoring_dir / f"{ticket['ticket_id']}_monitoring.json"
        with open(monitoring_file, 'w', encoding='utf-8') as f:
            json.dump(monitoring_config, f, indent=2)

        logger.info(f"   ✅ Monitoring config saved: {monitoring_file}")

        return monitoring_config


    except Exception as e:
        logger.error(f"Error in setup_workflow_monitoring: {e}", exc_info=True)
        raise
def route_to_team(ticket: Dict[str, Any]) -> str:
    """Route ticket to appropriate team"""
    logger.info("Routing ticket to team...")

    # Determine team based on category
    category = ticket['category']
    subcategory = ticket['subcategory']

    if category == "NETWORK" and subcategory == "DNS":
        team = "NETWORK_TEAM"
        logger.info(f"   ✅ Routed to: {team}")
        return team

    # Default routing
    team = "GENERAL_SUPPORT"
    logger.info(f"   ✅ Routed to: {team}")
    return team


def main():
    """Main entry point"""
    logger.info("=" * 70)
    logger.info("🎫 CREATING DNS HELPDESK TICKET")
    logger.info("=" * 70)
    logger.info("")

    # Create ticket
    ticket = create_dns_ticket()
    logger.info(f"✅ Ticket created: {ticket['ticket_id']}")
    logger.info(f"   Title: {ticket['title']}")
    logger.info(f"   Priority: {ticket['priority']}")
    logger.info("")

    # Route to team
    team = route_to_team(ticket)
    ticket['assigned_team'] = team
    logger.info("")

    # Save ticket
    ticket_file = save_ticket(ticket)
    logger.info(f"✅ Ticket saved: {ticket_file}")
    logger.info("")

    # Set up workflow monitoring
    monitoring = setup_workflow_monitoring(ticket)
    logger.info(f"✅ Workflow monitoring configured")
    logger.info(f"   Check interval: {monitoring['check_interval']} seconds")
    logger.info(f"   Auto-close: {'Enabled' if monitoring['auto_close'] else 'Disabled'}")
    logger.info("")

    logger.info("=" * 70)
    logger.info("✅ HELPDESK TICKET CREATED AND CONFIGURED")
    logger.info("=" * 70)
    logger.info("")
    logger.info("📋 Next Steps:")
    logger.info(f"   1. Ticket routed to: {team}")
    logger.info("   2. Workflow monitoring active")
    logger.info("   3. Team will be notified via helpdesk system")
    logger.info("   4. Resolution will be automatically verified")
    logger.info("")

    return ticket


if __name__ == "__main__":


    main()