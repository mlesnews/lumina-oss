#!/usr/bin/env python3
"""
Setup NAS Migration Interrupt & Latency Monitor Cron Job
Sets up continuous monitoring via C-3PO coordination

Tags: #NAS-MIGRATION #MONITORING #CRON #C3PO #TRIAGE #BAU @C3PO @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from auto_cron_registration import AutoCronRegistry
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("NASMigrationInterruptMonitorCron")


def setup_monitoring_cron() -> Dict[str, Any]:
    """Setup continuous monitoring cron job for NAS migration interrupts"""
    logger.info("=" * 80)
    logger.info("📅 Setting up NAS Migration Interrupt Monitor Cron Job")
    logger.info("=" * 80)

    project_root = Path(__file__).parent.parent.parent

    # Create cron job configuration
    cron_config = {
        "name": "nas_migration_interrupt_monitor",
        "description": "Monitor NAS migration interrupts and latency via @C3PO",
        "command": f"python {project_root / 'scripts' / 'python' / 'nas_migration_interrupt_latency_diagnostic.py'} --report",
        "schedule": "*/15 * * * *",  # Every 15 minutes
        "enabled": True,
        "tags": ["NAS-MIGRATION", "MONITORING", "INTERRUPTS", "LATENCY", "@C3PO"],
        "metadata": {
            "coordinator": "@C3PO",
            "workflow": "@C3PO @TRIAGE → @BAU → @HELPDESK",
            "teams": ["@BACKUP", "@STORAGE", "@NETWORK"]
        }
    }

    # Register with cron system
    try:
        registry = AutoCronRegistry(project_root)
        result = registry.register_cron_job(
            name=cron_config["name"],
            command=cron_config["command"],
            schedule=cron_config["schedule"],
            description=cron_config["description"],
            enabled=cron_config["enabled"],
            tags=cron_config["tags"],
            metadata=cron_config["metadata"]
        )

        logger.info(f"✅ Cron job registered: {cron_config['name']}")
        logger.info(f"   Schedule: {cron_config['schedule']} (every 15 minutes)")
        logger.info(f"   Coordinator: @C3PO")

        return {
            "success": True,
            "cron_job": cron_config,
            "registration": result
        }

    except Exception as e:
        logger.error(f"❌ Failed to register cron job: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def setup_c3po_workflow_cron() -> Dict[str, Any]:
    """Setup C-3PO workflow cron job for periodic team coordination"""
    logger.info("=" * 80)
    logger.info("📅 Setting up @C3PO Workflow Cron Job")
    logger.info("=" * 80)

    project_root = Path(__file__).parent.parent.parent

    # Create cron job configuration
    cron_config = {
        "name": "c3po_nas_migration_teams_coordination",
        "description": "@C3PO coordinates teams for NAS migration issues",
        "command": f"python {project_root / 'scripts' / 'python' / 'jarvis_c3po_teams_triage_bau.py'} --full",
        "schedule": "0 */2 * * *",  # Every 2 hours
        "enabled": True,
        "tags": ["@C3PO", "TRIAGE", "BAU", "HELPDESK", "TEAMS"],
        "metadata": {
            "coordinator": "@C3PO",
            "workflow": "@C3PO @TRIAGE → @BAU → @HELPDESK",
            "teams": ["@BACKUP", "@STORAGE", "@NETWORK"]
        }
    }

    # Register with cron system
    try:
        registry = AutoCronRegistry(project_root)
        result = registry.register_cron_job(
            name=cron_config["name"],
            command=cron_config["command"],
            schedule=cron_config["schedule"],
            description=cron_config["description"],
            enabled=cron_config["enabled"],
            tags=cron_config["tags"],
            metadata=cron_config["metadata"]
        )

        logger.info(f"✅ Cron job registered: {cron_config['name']}")
        logger.info(f"   Schedule: {cron_config['schedule']} (every 2 hours)")
        logger.info(f"   Coordinator: @C3PO")

        return {
            "success": True,
            "cron_job": cron_config,
            "registration": result
        }

    except Exception as e:
        logger.error(f"❌ Failed to register cron job: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Setup NAS Migration Interrupt Monitor Cron Jobs")
    parser.add_argument("--monitor-only", action="store_true", help="Setup monitoring cron only")
    parser.add_argument("--workflow-only", action="store_true", help="Setup C-3PO workflow cron only")
    parser.add_argument("--both", action="store_true", help="Setup both cron jobs")

    args = parser.parse_args()

    print("="*80)
    print("📅 NAS MIGRATION INTERRUPT MONITOR CRON SETUP")
    print("="*80)
    print()
    print("Coordinator: @C3PO")
    print()

    if args.monitor_only:
        result = setup_monitoring_cron()
        print(f"Result: {'✅ Success' if result.get('success') else '❌ Failed'}")

    elif args.workflow_only:
        result = setup_c3po_workflow_cron()
        print(f"Result: {'✅ Success' if result.get('success') else '❌ Failed'}")

    elif args.both:
        print("Setting up both cron jobs...")
        print()
        monitor_result = setup_monitoring_cron()
        print()
        workflow_result = setup_c3po_workflow_cron()
        print()
        print("="*80)
        print("📊 SETUP SUMMARY")
        print("="*80)
        print(f"Monitoring Cron: {'✅ Success' if monitor_result.get('success') else '❌ Failed'}")
        print(f"Workflow Cron: {'✅ Success' if workflow_result.get('success') else '❌ Failed'}")

    else:
        # Default: setup both
        print("Setting up both cron jobs...")
        print()
        monitor_result = setup_monitoring_cron()
        print()
        workflow_result = setup_c3po_workflow_cron()
        print()
        print("="*80)
        print("📊 SETUP SUMMARY")
        print("="*80)
        print(f"Monitoring Cron: {'✅ Success' if monitor_result.get('success') else '❌ Failed'}")
        print(f"Workflow Cron: {'✅ Success' if workflow_result.get('success') else '❌ Failed'}")


if __name__ == "__main__":


    main()