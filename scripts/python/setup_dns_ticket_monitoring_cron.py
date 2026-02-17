#!/usr/bin/env python3
"""
Setup DNS Ticket Monitoring Cron
Registers DNS ticket workflow monitoring as a cron service

Tags: #HELPDESK #DNS #CRON #MONITORING #@DOIT
"""

import sys
from pathlib import Path

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

try:
    from auto_cron_registration import AutoCronRegistration
    CRON_REGISTRATION_AVAILABLE = True
except ImportError:
    CRON_REGISTRATION_AVAILABLE = False

logger = get_logger("SetupDNSTicketMonitoringCron")


def setup_dns_ticket_monitoring_cron():
    """Set up DNS ticket monitoring as cron service"""
    logger.info("=" * 70)
    logger.info("⏰ SETTING UP DNS TICKET MONITORING CRON")
    logger.info("=" * 70)
    logger.info("")

    if not CRON_REGISTRATION_AVAILABLE:
        logger.warning("⚠️  Auto cron registration not available")
        logger.info("   Manual cron setup required")
        return False

    # Find latest DNS ticket
    helpdesk_dir = project_root / "docs" / "helpdesk"
    dns_tickets = list(helpdesk_dir.glob("HELPDESK-*-DNS-*.json"))
    if not dns_tickets:
        logger.error("❌ No DNS ticket found. Create one first.")
        return False

    ticket_id = dns_tickets[-1].stem
    logger.info(f"   Found ticket: {ticket_id}")
    logger.info("")

    # Register monitoring cron
    cron_reg = AutoCronRegistration(project_root)

    service_config = {
        "service_name": "dns_ticket_workflow_monitor",
        "display_name": "DNS Ticket Workflow Monitor",
        "description": "Monitors DNS ticket resolution and verifies DNS services",
        "script_path": str(project_root / "scripts" / "python" / "monitor_dns_ticket_workflow.py"),
        "script_args": ["--ticket-id", ticket_id, "--once"],
        "schedule": "*/5 * * * *",  # Every 5 minutes
        "enabled": True,
        "tags": ["#HELPDESK", "#DNS", "#MONITORING", "#WORKFLOW", "@DOIT"]
    }

    logger.info("STEP 1: Registering Cron Service")
    logger.info("-" * 70)
    logger.info(f"   Service: {service_config['service_name']}")
    logger.info(f"   Schedule: {service_config['schedule']} (every 5 minutes)")
    logger.info(f"   Script: {service_config['script_path']}")
    logger.info("")

    try:
        result = cron_reg.register_service(service_config)
        if result.get("success"):
            logger.info("   ✅ Cron service registered")
            logger.info("")

            logger.info("STEP 2: Activating Service")
            logger.info("-" * 70)
            activate_result = cron_reg.activate_service(service_config["service_name"])
            if activate_result.get("success"):
                logger.info("   ✅ Cron service activated")
                logger.info("")

                logger.info("=" * 70)
                logger.info("✅ DNS TICKET MONITORING CRON SETUP COMPLETE")
                logger.info("=" * 70)
                logger.info("")
                logger.info("📋 Service Details:")
                logger.info(f"   Name: {service_config['display_name']}")
                logger.info(f"   Schedule: Every 5 minutes")
                logger.info(f"   Ticket: {ticket_id}")
                logger.info(f"   Status: Active")
                logger.info("")
                return True
            else:
                logger.error(f"   ❌ Failed to activate: {activate_result.get('error')}")
        else:
            logger.error(f"   ❌ Failed to register: {result.get('error')}")
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")

    return False


if __name__ == "__main__":
    setup_dns_ticket_monitoring_cron()
