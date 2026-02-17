#!/usr/bin/env python3
"""
Monitor DNS Ticket Workflow
Monitors DNS ticket resolution and executes verification

Tags: #HELPDESK #MONITORING #WORKFLOW #DNS #@DOIT
"""

import sys
import json
import time
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

logger = get_logger("MonitorDNSTicketWorkflow")


class DNSTicketWorkflowMonitor:
    """Monitor DNS ticket workflow and verify resolution"""

    def __init__(self, ticket_id: str):
        """Initialize monitor"""
        self.ticket_id = ticket_id
        self.project_root = project_root
        self.monitoring_dir = self.project_root / "data" / "helpdesk" / "monitoring"
        self.monitoring_file = self.monitoring_dir / f"{ticket_id}_monitoring.json"
        self.helpdesk_dir = self.project_root / "docs" / "helpdesk"
        self.ticket_file = self.helpdesk_dir / f"{ticket_id}.json"

        logger.info("=" * 70)
        logger.info("🔍 DNS TICKET WORKFLOW MONITOR")
        logger.info("=" * 70)
        logger.info(f"   Ticket: {ticket_id}")
        logger.info("")

    def load_monitoring_config(self) -> Optional[Dict[str, Any]]:
        try:
            """Load monitoring configuration"""
            if not self.monitoring_file.exists():
                logger.warning(f"   ⚠️  Monitoring config not found: {self.monitoring_file}")
                return None

            with open(self.monitoring_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in load_monitoring_config: {e}", exc_info=True)
            raise
    def load_ticket(self) -> Optional[Dict[str, Any]]:
        try:
            """Load ticket data"""
            if not self.ticket_file.exists():
                logger.warning(f"   ⚠️  Ticket not found: {self.ticket_file}")
                return None

            with open(self.ticket_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in load_ticket: {e}", exc_info=True)
            raise
    def verify_dns_resolution(self) -> Dict[str, Any]:
        """Verify DNS resolution status"""
        logger.info("🔍 Verifying DNS resolution...")

        try:
            result = subprocess.run(
                ["python", str(self.project_root / "scripts" / "python" / "verify_homelab_dns_fix.py")],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.project_root)
            )

            # Parse results
            pfsense_success = "pfSense DNS:" in result.stdout and "successful" in result.stdout
            nas_success = "NAS DNS:" in result.stdout and "successful" in result.stdout

            return {
                "pfsense_dns": pfsense_success,
                "nas_dns": nas_success,
                "overall": pfsense_success and nas_success,
                "output": result.stdout,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"   ❌ Verification failed: {e}")
            return {
                "pfsense_dns": False,
                "nas_dns": False,
                "overall": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def check_ticket_status(self) -> Dict[str, Any]:
        """Check current ticket status"""
        ticket = self.load_ticket()
        if not ticket:
            return {"status": "UNKNOWN", "error": "Ticket not found"}

        return {
            "status": ticket.get("status", "UNKNOWN"),
            "priority": ticket.get("priority", "UNKNOWN"),
            "assigned_team": ticket.get("assigned_team", "UNKNOWN")
        }

    def update_ticket_status(self, new_status: str, notes: str = "") -> bool:
        try:
            """Update ticket status"""
            ticket = self.load_ticket()
            if not ticket:
                return False

            ticket["status"] = new_status
            ticket["last_updated"] = datetime.now().isoformat()

            if notes:
                if "notes" not in ticket:
                    ticket["notes"] = []
                ticket["notes"].append({
                    "timestamp": datetime.now().isoformat(),
                    "status": new_status,
                    "note": notes
                })

            with open(self.ticket_file, 'w', encoding='utf-8') as f:
                json.dump(ticket, f, indent=2)

            # Also update markdown
            md_file = self.helpdesk_dir / f"{self.ticket_id}.md"
            if md_file.exists():
                content = md_file.read_text(encoding='utf-8')
                content = content.replace(f"**Status**: 🔍 **{ticket.get('status', 'OPEN')}**", 
                                        f"**Status**: 🔍 **{new_status}**")
                md_file.write_text(content, encoding='utf-8')

            logger.info(f"   ✅ Ticket status updated: {new_status}")
            return True

        except Exception as e:
            self.logger.error(f"Error in update_ticket_status: {e}", exc_info=True)
            raise
    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run one monitoring cycle"""
        logger.info("=" * 70)
        logger.info("🔄 RUNNING MONITORING CYCLE")
        logger.info("=" * 70)
        logger.info("")

        # Check ticket status
        logger.info("STEP 1: Check Ticket Status")
        logger.info("-" * 70)
        ticket_status = self.check_ticket_status()
        logger.info(f"   Status: {ticket_status['status']}")
        logger.info(f"   Priority: {ticket_status['priority']}")
        logger.info(f"   Team: {ticket_status['assigned_team']}")
        logger.info("")

        # Verify DNS resolution
        logger.info("STEP 2: Verify DNS Resolution")
        logger.info("-" * 70)
        dns_status = self.verify_dns_resolution()
        logger.info(f"   pfSense DNS: {'✅' if dns_status['pfsense_dns'] else '❌'}")
        logger.info(f"   NAS DNS: {'✅' if dns_status['nas_dns'] else '❌'}")
        logger.info(f"   Overall: {'✅ RESOLVED' if dns_status['overall'] else '❌ NOT RESOLVED'}")
        logger.info("")

        # Update ticket if resolved
        if dns_status['overall'] and ticket_status['status'] != "RESOLVED":
            logger.info("STEP 3: Update Ticket Status")
            logger.info("-" * 70)
            self.update_ticket_status(
                "RESOLVED",
                f"DNS resolution verified: Both pfSense and NAS DNS working correctly"
            )
            logger.info("   ✅ Ticket marked as RESOLVED")
            logger.info("")

        return {
            "ticket_status": ticket_status,
            "dns_status": dns_status,
            "resolved": dns_status['overall']
        }

    def start_monitoring(self, interval: int = 300, max_cycles: Optional[int] = None):
        """Start continuous monitoring"""
        config = self.load_monitoring_config()
        if not config:
            logger.error("   ❌ Monitoring config not found")
            return

        interval = config.get("check_interval", interval)
        logger.info(f"🚀 Starting workflow monitoring...")
        logger.info(f"   Check interval: {interval} seconds ({interval/60:.1f} minutes)")
        logger.info(f"   Max cycles: {max_cycles or 'Unlimited'}")
        logger.info("")

        cycle_count = 0
        while True:
            cycle_count += 1
            logger.info(f"Cycle #{cycle_count}")
            logger.info("-" * 70)

            result = self.run_monitoring_cycle()

            if result['resolved']:
                logger.info("=" * 70)
                logger.info("✅ TICKET RESOLVED - Monitoring Complete")
                logger.info("=" * 70)
                logger.info("")
                logger.info("DNS services are now working correctly!")
                logger.info("   - pfSense DNS: ✅")
                logger.info("   - NAS DNS: ✅")
                logger.info("")
                break

            if max_cycles and cycle_count >= max_cycles:
                logger.info(f"   Reached max cycles ({max_cycles})")
                break

            logger.info(f"   Next check in {interval} seconds...")
            logger.info("")
            time.sleep(interval)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor DNS Ticket Workflow")
    parser.add_argument("--ticket-id", "-t", help="Ticket ID to monitor")
    parser.add_argument("--interval", "-i", type=int, default=300, help="Check interval in seconds")
    parser.add_argument("--max-cycles", "-m", type=int, help="Maximum monitoring cycles")
    parser.add_argument("--once", "-o", action="store_true", help="Run once and exit")

    args = parser.parse_args()

    # Get ticket ID
    ticket_id = args.ticket_id
    if not ticket_id:
        # Find latest DNS ticket
        helpdesk_dir = project_root / "docs" / "helpdesk"
        dns_tickets = list(helpdesk_dir.glob("HELPDESK-*-DNS-*.json"))
        if dns_tickets:
            ticket_id = dns_tickets[-1].stem
            logger.info(f"   Found ticket: {ticket_id}")
        else:
            logger.error("   ❌ No DNS ticket found. Create one first.")
            sys.exit(1)

    monitor = DNSTicketWorkflowMonitor(ticket_id)

    if args.once:
        monitor.run_monitoring_cycle()
    else:
        monitor.start_monitoring(args.interval, args.max_cycles)


if __name__ == "__main__":


    main()