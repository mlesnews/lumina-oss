#!/usr/bin/env python3
"""
Execute All @ASK Chains with Live Monitoring

Resumes all @ask chains and activities with progressive percentage tracking
and ongoing live monitoring/maintenance.

@JARVIS @ASKS @MONITORING @MAINTENANCE #LIVE #PROGRESSIVE
"""

import sys
import time
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from jarvis_execute_ask_chains import JARVISAskChainExecutor
    from jarvis_live_monitor_maintenance import get_live_monitor
    from jarvis_progress_tracker import get_progress_tracker
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"⚠️  Import error: {e}")
    sys.exit(1)

logger = get_logger("ExecuteAllAsksWithMonitoring")


def main():
    """Execute all @ask chains with live monitoring"""
    logger.info("=" * 80)
    logger.info("🔗 EXECUTING ALL @ASK CHAINS WITH LIVE MONITORING")
    logger.info("=" * 80)
    logger.info("   Progressive percentage tracking")
    logger.info("   Ongoing live monitoring & maintenance")
    logger.info("   Resuming all activities")
    logger.info("")

    # Start live monitoring first
    logger.info("📊 Step 1: Starting live monitoring...")
    monitor = get_live_monitor(project_root=project_root)
    progress_tracker = get_progress_tracker(project_root=project_root, mode="bau")
    logger.info("✅ Live monitoring active")

    # Initialize chain executor
    logger.info("")
    logger.info("📋 Step 2: Initializing @ask chain executor...")
    executor = JARVISAskChainExecutor(project_root=project_root)
    logger.info("✅ Chain executor initialized")

    # Discover and create chains
    logger.info("")
    logger.info("📋 Step 3: Discovering @asks and creating chains...")
    chain_id = executor.discover_and_create_chain()

    if not chain_id:
        logger.info("ℹ️  No long-running @asks found to chain")
        logger.info("   Live monitoring will continue in background")
        return 0

    logger.info(f"✅ Chain created: {chain_id}")

    # Register chain execution with progress tracker
    chain_process_id = f"ask_chain_{chain_id}"
    progress_tracker.register_process(
        process_id=chain_process_id,
        process_name="@ASK Chain Execution",
        source_name="JARVIS Workflow",
        total_items=100,  # Will be updated
        agent_type="jarvis"
    )

    # Execute chain with live monitoring
    logger.info("")
    logger.info("🚀 Step 4: Executing chain with live monitoring...")
    logger.info("   (Progress updates every 0.5s)")
    logger.info("")

    result = executor.execute_chain(chain_id)

    # Update progress
    if result.get("success"):
        progress_tracker.complete_process(chain_process_id)
        logger.info("")
        logger.info("✅ Chain execution completed successfully")
    else:
        if result.get("blocked"):
            logger.warning(f"⚠️  Chain execution blocked: {result.get('reason', 'Unknown reason')}")
        else:
            progress_tracker.fail_process(chain_process_id, result.get("error", "Unknown error"))
            logger.error(f"❌ Chain execution failed: {result.get('error', 'Unknown error')}")

    # Get final status
    status = monitor.get_live_status()
    progressive = status["progressive_percentage"]
    health = status["system_health"]

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 EXECUTION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"   Chain ID: {chain_id}")
    logger.info(f"   Success: {result.get('success', False)}")
    logger.info(f"   Tasks Executed: {len(result.get('tasks_executed', []))}")
    logger.info(f"   Tasks Completed: {len(result.get('tasks_completed', []))}")
    logger.info(f"   Tasks Failed: {len(result.get('tasks_failed', []))}")
    logger.info("")
    logger.info("📊 LIVE MONITORING STATUS")
    logger.info(f"   Overall Progress: {progressive['overall']:.1f}%")
    logger.info(f"   System Health: {health['overall_health_percent']:.1f}%")
    logger.info(f"   Processes Running: {health['processes_running']}")
    logger.info(f"   Maintenance Tasks: {health['maintenance_tasks_pending']} pending")
    logger.info("")
    logger.info("✅ Live monitoring continues in background")
    logger.info("=" * 80)

    return 0 if result.get("success") else 1


if __name__ == "__main__":


    sys.exit(main())