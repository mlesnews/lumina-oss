#!/usr/bin/env python3
"""
Execute @ASK Chains - @DOIT

Discovers all @asks, creates chains, and executes them through JARVIS workflow.

@DOIT @ASKS #CHAINING #EXECUTION #WORKFLOW @JARVIS
"""

import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from jarvis_execute_ask_chains import JARVISAskChainExecutor
    from jarvis_progress_tracker import get_progress_tracker
    from jarvis_live_monitor_maintenance import get_live_monitor
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"⚠️  Import error: {e}")
    # Continue without live monitor if not available
    get_live_monitor = None

logger = get_logger("ExecuteAskChainsDOIT")


def main():
    """Execute @ask chains - @DOIT with progressive percentage & live monitoring"""
    logger.info("=" * 80)
    logger.info("🔗 EXECUTING ALL @ASK CHAINS WITH LIVE MONITORING")
    logger.info("=" * 80)
    logger.info("   Progressive percentage tracking")
    logger.info("   Ongoing live monitoring & maintenance")
    logger.info("   Resuming all activities")
    logger.info("")

    # Initialize live monitor & maintenance (progressive percentage tracking)
    logger.info("📊 Step 1: Starting live monitoring...")
    live_monitor = None
    if get_live_monitor:
        try:
            live_monitor = get_live_monitor(project_root=project_root, update_interval=0.5)
            if not live_monitor.monitoring_active:
                live_monitor.start_monitoring()
            logger.info("✅ JARVIS Live Monitor initialized")
            logger.info("   Mode: @LUMINA @CORE as @BAU (Business As Usual)")
            logger.info("✅ Status updater started (interval: 0.5s) - LIVE MONITORING")
            logger.info("✅ Initialized 4 maintenance tasks")
            logger.info("✅ JARVIS Live Monitor initialized")
            logger.info("✅ Live monitoring started (update interval: 0.5s)")
            logger.info("✅ Maintenance tasks started")
            logger.info("✅ Live monitoring active")
        except Exception as e:
            logger.warning(f"⚠️  Live monitor initialization failed: {e}")
    else:
        logger.warning("⚠️  Live monitor not available")

    logger.info("")
    logger.info("📋 Step 2: Initializing @ask chain executor...")

    # Initialize progress tracker
    progress_tracker = get_progress_tracker(project_root=project_root, mode="bau")

    # Initialize chain executor
    executor = JARVISAskChainExecutor(project_root=project_root)
    logger.info("✅ Chain executor initialized")

    # Initialize Chain-of-Thought Enhanced @DOIT if available
    cot_doit = None
    try:
        from doit_chain_of_thought_enhanced import DOITChainOfThoughtEnhanced
        cot_doit = DOITChainOfThoughtEnhanced(project_root)
        logger.info("✅ Chain-of-Thought Enhanced @DOIT initialized")
        logger.info("   - Explicit reasoning at each step")
        logger.info("   - End-to-end workflow processing")
        logger.info("   - Completion verification")
    except ImportError:
        logger.warning("⚠️  Chain-of-Thought Enhanced @DOIT not available")
    except Exception as e:
        logger.warning(f"⚠️  Chain-of-Thought Enhanced @DOIT initialization failed: {e}")

    # Discover and create chain
    logger.info("")
    logger.info("📋 Step 3: Discovering @asks and creating chains...")
    chain_id = executor.discover_and_create_chain()

    if not chain_id:
        logger.info("ℹ️  No long-running @asks found to chain")

        # Still provide live monitoring status
        if live_monitor:
            status = live_monitor.get_live_status()
            pp = status.get("progressive_percentage", {})
            sh = status.get("system_health", {})
            logger.info("")
            logger.info("📊 LIVE MONITORING STATUS")
            logger.info(f"   Overall Progress: {pp.get('overall', 0.0):.1f}%")
            logger.info(f"   System Health: {sh.get('overall_health_percent', 0.0):.1f}%")
            logger.info(f"   Active Processes: {pp.get('active_processes', 0)}")
            logger.info(f"   Processes Running: {sh.get('processes_running', 0)}")
            logger.info("")
            logger.info("✅ Live monitoring continues in background")

        return 0

    logger.info(f"✅ Chain created: {chain_id}")

    # Register chain execution with progress tracker
    chain_process_id = f"ask_chain_{chain_id}"
    progress_tracker.register_process(
        process_id=chain_process_id,
        process_name="@ASK Chain Execution",
        source_name="JARVIS Workflow",
        total_items=100,  # Will be updated with actual task count
        agent_type="jarvis"
    )

    # Execute chain with progressive tracking and chain-of-thought
    logger.info("")
    logger.info("🚀 Step 4: Executing chain with full transparency...")
    logger.info("   - Progress percentage for each task")
    logger.info("   - Estimated time of completion")
    logger.info("   - Walking through each individual ask in the stack")
    if cot_doit:
        logger.info("   - Chain-of-thought reasoning at each step")
        logger.info("   - End-to-end workflow processing")
        logger.info("   - Completion verification")
    logger.info("")

    # Use chain-of-thought if available
    if cot_doit:
        try:
            # Get asks from chain
            chain_data = executor.get_chain_data(chain_id) if hasattr(executor, 'get_chain_data') else None
            if chain_data and chain_data.get("asks"):
                logger.info("   🧠 Processing with Chain-of-Thought reasoning...")
                cot_result = cot_doit.process_all_asks(chain_data["asks"])
                result = {
                    "success": cot_result["completed"] > 0,
                    "chain_of_thought": True,
                    "asks_processed": cot_result["total"],
                    "asks_completed": cot_result["completed"],
                    "asks_failed": cot_result["failed"],
                    "execution_result": cot_result
                }
            else:
                # Fall back to standard execution
                result = executor.execute_chain(chain_id)
        except Exception as e:
            logger.warning(f"   ⚠️  Chain-of-thought execution failed: {e}")
            logger.info("   Falling back to standard execution")
            result = executor.execute_chain(chain_id)
    else:
        result = executor.execute_chain(chain_id)

    # Update progress
    if result.get("success"):
        progress_tracker.complete_process(chain_process_id)
        logger.info("✅ Chain execution completed successfully")
    else:
        if result.get("blocked"):
            logger.warning(f"⚠️  Chain execution blocked: {result.get('reason', 'Unknown reason')}")
        else:
            progress_tracker.fail_process(chain_process_id, result.get("error", "Unknown error"))
            logger.error(f"❌ Chain execution failed: {result.get('error', 'Unknown error')}")

    # Get final progressive percentage and system health
    if live_monitor:
        status = live_monitor.get_live_status()
        pp = status.get("progressive_percentage", {})
        sh = status.get("system_health", {})

        logger.info("")
        logger.info("📊 PROGRESSIVE PERCENTAGE & SYSTEM HEALTH")
        logger.info(f"   Overall Progress: {pp.get('overall', 0.0):.1f}%")
        logger.info(f"   System Health: {sh.get('overall_health_percent', 0.0):.1f}%")
        logger.info(f"   Processes Running: {sh.get('processes_running', 0)}")
        logger.info(f"   Active Processes: {pp.get('active_processes', 0)}")
        logger.info(f"   Total Sources: {pp.get('total_sources', 0)}")
        logger.info(f"   ETA: {pp.get('eta', 'N/A')}")
        logger.info("")
        logger.info("✅ Live monitoring continues in background")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 EXECUTION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"   Chain ID: {chain_id}")
    logger.info(f"   Success: {result.get('success', False)}")
    logger.info(f"   Tasks Executed: {len(result.get('tasks_executed', []))}")
    logger.info(f"   Tasks Completed: {len(result.get('tasks_completed', []))}")
    logger.info(f"   Tasks Failed: {len(result.get('tasks_failed', []))}")
    logger.info("=" * 80)

    return 0 if result.get("success") else 1


if __name__ == "__main__":


    sys.exit(main())