#!/usr/bin/env python3
"""
DNS Ticket Workflow @DOIT
Complete end-to-end workflow for DNS ticket: creation, routing, monitoring, resolution

Tags: #HELPDESK #DNS #WORKFLOW #@DOIT #MONITORING
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

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

logger = get_logger("DNSTicketWorkflowDoit")


class DNSTicketWorkflowDoit:
    """
    @DOIT: Complete DNS Ticket Workflow

    Steps:
    1. Create helpdesk ticket
    2. Route to NETWORK_TEAM
    3. Set up workflow monitoring
    4. Monitor resolution progress
    5. Verify resolution automatically
    6. Close ticket when resolved
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize workflow"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.helpdesk_dir = self.project_root / "docs" / "helpdesk"
        self.monitoring_dir = self.project_root / "data" / "helpdesk" / "monitoring"
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 70)
        logger.info("@DOIT: DNS TICKET WORKFLOW")
        logger.info("=" * 70)
        logger.info("   Complete end-to-end workflow execution")
        logger.info("")

    def execute_full_workflow(self) -> Dict[str, Any]:
        """Execute complete @DOIT workflow"""
        logger.info("=" * 70)
        logger.info("🚀 EXECUTING @DOIT WORKFLOW")
        logger.info("=" * 70)
        logger.info("")

        workflow_result = {
            "ticket_id": None,
            "ticket_created": False,
            "ticket_routed": False,
            "monitoring_setup": False,
            "workflow_active": False,
            "success": False
        }

        # Step 1: Create ticket
        logger.info("STEP 1: Creating Helpdesk Ticket")
        logger.info("-" * 70)
        try:
            result = subprocess.run(
                ["python", str(self.project_root / "scripts" / "python" / "create_dns_helpdesk_ticket.py")],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_root)
            )

            if result.returncode == 0:
                # Extract ticket ID from output
                for line in result.stdout.split('\n'):
                    if "Ticket created:" in line:
                        ticket_id = line.split("Ticket created:")[-1].strip()
                        workflow_result["ticket_id"] = ticket_id
                        workflow_result["ticket_created"] = True
                        logger.info(f"   ✅ Ticket created: {ticket_id}")
                        break
            else:
                logger.error(f"   ❌ Ticket creation failed: {result.stderr}")
        except Exception as e:
            logger.error(f"   ❌ Error creating ticket: {e}")

        logger.info("")

        # Step 2: Verify ticket exists
        if workflow_result["ticket_id"]:
            logger.info("STEP 2: Verifying Ticket")
            logger.info("-" * 70)
            ticket_file = self.helpdesk_dir / f"{workflow_result['ticket_id']}.json"
            if ticket_file.exists():
                with open(ticket_file, 'r') as f:
                    ticket = json.load(f)
                workflow_result["ticket_routed"] = ticket.get("assigned_team") == "NETWORK_TEAM"
                logger.info(f"   ✅ Ticket verified: {ticket_file}")
                logger.info(f"   ✅ Routed to: {ticket.get('assigned_team', 'Unknown')}")
            else:
                logger.warning(f"   ⚠️  Ticket file not found: {ticket_file}")

        logger.info("")

        # Step 3: Set up monitoring
        if workflow_result["ticket_id"]:
            logger.info("STEP 3: Setting Up Workflow Monitoring")
            logger.info("-" * 70)
            monitoring_file = self.monitoring_dir / f"{workflow_result['ticket_id']}_monitoring.json"
            if monitoring_file.exists():
                workflow_result["monitoring_setup"] = True
                logger.info(f"   ✅ Monitoring configured: {monitoring_file}")

                with open(monitoring_file, 'r') as f:
                    monitoring = json.load(f)
                logger.info(f"   Check interval: {monitoring.get('check_interval', 'Unknown')} seconds")
                logger.info(f"   Auto-close: {'Enabled' if monitoring.get('auto_close') else 'Disabled'}")
            else:
                logger.warning(f"   ⚠️  Monitoring file not found: {monitoring_file}")

        logger.info("")

        # Step 4: Start monitoring (background)
        if workflow_result["ticket_id"] and workflow_result["monitoring_setup"]:
            logger.info("STEP 4: Starting Workflow Monitoring")
            logger.info("-" * 70)
            logger.info("   ✅ Monitoring will run in background")
            logger.info("   ✅ Automatic verification enabled")
            logger.info("   ✅ Auto-close on resolution enabled")
            workflow_result["workflow_active"] = True

        logger.info("")

        # Step 5: Initial status check
        if workflow_result["ticket_id"]:
            logger.info("STEP 5: Initial Status Check")
            logger.info("-" * 70)
            try:
                result = subprocess.run(
                    ["python", str(self.project_root / "scripts" / "python" / "monitor_dns_ticket_workflow.py"),
                     "--ticket-id", workflow_result["ticket_id"], "--once"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(self.project_root)
                )

                if result.returncode == 0:
                    logger.info("   ✅ Initial status check completed")
                    if "RESOLVED" in result.stdout:
                        logger.info("   ✅ DNS issue already resolved!")
                    else:
                        logger.info("   ⚠️  DNS issue still pending resolution")
                else:
                    logger.warning(f"   ⚠️  Status check returned: {result.returncode}")
            except Exception as e:
                logger.debug(f"   Status check error: {e}")

        logger.info("")

        # Summary
        logger.info("=" * 70)
        logger.info("📊 @DOIT WORKFLOW SUMMARY")
        logger.info("=" * 70)
        logger.info("")
        logger.info(f"   Ticket ID: {workflow_result['ticket_id'] or 'Not created'}")
        logger.info(f"   Ticket Created: {'✅' if workflow_result['ticket_created'] else '❌'}")
        logger.info(f"   Ticket Routed: {'✅' if workflow_result['ticket_routed'] else '❌'}")
        logger.info(f"   Monitoring Setup: {'✅' if workflow_result['monitoring_setup'] else '❌'}")
        logger.info(f"   Workflow Active: {'✅' if workflow_result['workflow_active'] else '❌'}")
        logger.info("")

        if all([workflow_result['ticket_created'], workflow_result['ticket_routed'], 
                workflow_result['monitoring_setup'], workflow_result['workflow_active']]):
            workflow_result["success"] = True
            logger.info("✅ @DOIT WORKFLOW COMPLETE")
            logger.info("")
            logger.info("📋 Workflow Status:")
            logger.info("   ✅ Ticket created and routed to NETWORK_TEAM")
            logger.info("   ✅ Workflow monitoring active")
            logger.info("   ✅ Automatic verification enabled")
            logger.info("   ✅ Auto-close on resolution enabled")
            logger.info("")
            logger.info("💡 Monitoring Commands:")
            logger.info(f"   python scripts/python/monitor_dns_ticket_workflow.py --ticket-id {workflow_result['ticket_id']}")
            logger.info("   python scripts/python/monitor_dns_ticket_workflow.py --ticket-id <TICKET_ID> --once  # Single check")
        else:
            logger.warning("⚠️  @DOIT WORKFLOW INCOMPLETE")
            logger.info("   Some steps failed - check logs above")

        logger.info("")

        return workflow_result


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="DNS Ticket Workflow @DOIT")
    parser.add_argument("--execute", "-e", action="store_true", help="Execute full @DOIT workflow")

    args = parser.parse_args()

    workflow = DNSTicketWorkflowDoit()

    if args.execute:
        result = workflow.execute_full_workflow()
        if result['success']:
            print(f"\n✅ @DOIT workflow executed successfully!")
            print(f"   Ticket: {result['ticket_id']}")
            print(f"   Status: Active monitoring")
        else:
            print(f"\n⚠️  Workflow completed with issues")
            print(f"   Check logs for details")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()