#!/usr/bin/env python3
"""
Start JARVIS Live Monitoring & Maintenance

Initializes and starts progressive percentage tracking and ongoing maintenance.

@JARVIS @MONITORING @MAINTENANCE #LIVE #PROGRESSIVE
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from jarvis_live_monitor_maintenance import get_live_monitor
    from jarvis_progress_tracker import get_progress_tracker
    from lumina_logger import get_logger
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    sys.exit(1)

logger = get_logger("StartLiveMonitoring")


def main():
    """Start live monitoring and maintenance"""
    logger.info("=" * 80)
    logger.info("📊 STARTING JARVIS LIVE MONITORING & MAINTENANCE")
    logger.info("=" * 80)
    logger.info("   Progressive percentage tracking")
    logger.info("   Ongoing live monitoring")
    logger.info("   Automated maintenance tasks")
    logger.info("")

    # Initialize progress tracker (starts status updater automatically)
    progress_tracker = get_progress_tracker(project_root=project_root, mode="bau")
    logger.info("✅ Progress tracker initialized")

    # Initialize and start live monitor
    monitor = get_live_monitor(project_root=project_root)
    logger.info("✅ Live monitor started")

    # Get initial status
    status = monitor.get_live_status()
    progressive = status["progressive_percentage"]
    health = status["system_health"]

    logger.info("")
    logger.info("📊 INITIAL STATUS")
    logger.info("=" * 80)
    logger.info(f"   Overall Progress: {progressive['overall']:.1f}%")
    logger.info(f"   System Health: {health['overall_health_percent']:.1f}%")
    logger.info(f"   Processes Running: {health['processes_running']}")
    logger.info(f"   Processes Failed: {health['processes_failed']}")
    logger.info(f"   Active Sources: {progressive.get('total_sources', 0)}")
    logger.info(f"   Maintenance Tasks Pending: {health['maintenance_tasks_pending']}")
    logger.info("")
    logger.info("✅ Live monitoring active - updates every 0.5s")
    logger.info("✅ Maintenance tasks running in background")
    logger.info("=" * 80)
    logger.info("")
    logger.info("💡 Monitoring data saved to: data/live_monitoring/live_monitoring.json")
    logger.info("💡 Status updates saved to: data/progress_tracking/cursor_status.json")
    logger.info("")
    logger.info("🔄 Monitoring will continue in background...")

    return 0


if __name__ == "__main__":


    sys.exit(main())