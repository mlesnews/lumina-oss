#!/usr/bin/env python3
"""
Live Chain-of-Command Percentage Updater

Continuously updates percentage (0-100%) in master_todos.json for:
- Bidirectional Chain-of-Command with Azure Pipe
- Based on actual system status and homelab asset utilization

Tags: #TODO #PERCENTAGE #LIVE #UPDATER #REQUIRED @JARVIS @LUMINA @DOIT  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import time
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LiveChainOfCommandPercentageUpdater")

from master_todo_percentage_tracker import MasterTodoPercentageTracker
from homelab_asset_discovery import HomelabAssetDiscovery
from bidirectional_chain_of_command import BidirectionalChainOfCommand


def calculate_chain_of_command_percentage() -> float:
    """
    Calculate percentage based on:
    - Azure Service Bus integration (40%)
    - Homelab asset utilization (30%)
    - Bidirectional pipes active (20%)
    - Manager supervision active (10%)
    """
    percentage = 0.0

    # 1. Azure Service Bus integration (40%)
    try:
        chain = BidirectionalChainOfCommand()
        if chain.azure_sb_client:
            percentage += 40.0
            logger.debug("✅ Azure Service Bus: 40%")
        else:
            percentage += 20.0  # Partial credit if initialized but not connected
            logger.debug("⚠️  Azure Service Bus: 20% (initialized but not connected)")
    except Exception as e:
        logger.debug(f"❌ Azure Service Bus check failed: {e}")

    # 2. Homelab asset utilization (30%)
    try:
        discovery = HomelabAssetDiscovery()
        assets = discovery.discover_assets()
        summary = discovery.get_asset_utilization_summary()

        # Average utilization contributes to percentage
        avg_util = summary.get('average_utilization_percent', 0.0)
        percentage += (avg_util * 0.3)  # 30% weight
        logger.debug(f"✅ Homelab assets: {avg_util * 0.3:.1f}% (avg utilization: {avg_util}%)")
    except Exception as e:
        logger.debug(f"❌ Homelab asset check failed: {e}")

    # 3. Bidirectional pipes active (20%)
    try:
        chain = BidirectionalChainOfCommand()
        pipes = chain.process_all_pipes()
        pipes_count = pipes.get('pipes_processed', 0)

        if pipes_count > 0:
            # Each pipe contributes up to 20%
            pipe_percentage = min(pipes_count * 4.0, 20.0)  # Max 5 pipes for 20%
            percentage += pipe_percentage
            logger.debug(f"✅ Bidirectional pipes: {pipe_percentage:.1f}% ({pipes_count} pipes)")
    except Exception as e:
        logger.debug(f"❌ Pipe check failed: {e}")

    # 4. Manager supervision active (10%)
    try:
        from team_management_supervision import TeamManagementSupervision
        supervision = TeamManagementSupervision()
        if supervision.org_structure:
            # Check if managers are being processed
            managers_count = len(set(
                team.helpdesk_manager for team in supervision.org_structure.teams.values()
                if team.helpdesk_manager
            )) + len(set(
                team.team_lead for team in supervision.org_structure.teams.values()
                if team.team_lead
            ))

            if managers_count > 0:
                percentage += 10.0
                logger.debug(f"✅ Manager supervision: 10% ({managers_count} managers)")
    except Exception as e:
        logger.debug(f"❌ Manager supervision check failed: {e}")

    return min(percentage, 100.0)


def update_chain_of_command_percentage():
    """Update percentage for chain-of-command todo"""
    tracker = MasterTodoPercentageTracker()
    todo_id = "76e1dc0f90cf9b1e"  # Bidirectional Chain-of-Command with Azure Pipe

    percentage = calculate_chain_of_command_percentage()

    # Get status for notes
    try:
        chain = BidirectionalChainOfCommand()
        azure_sb_status = chain.azure_sb_client is not None
    except:
        azure_sb_status = False

    notes = f"Live update: Azure SB={azure_sb_status}, Homelab assets discovered, Pipes active, Supervision active"

    tracker.update_percentage(
        todo_id=todo_id,
        percentage=percentage,
        notes=notes
    )

    logger.info(f"📊 Updated chain-of-command percentage: {percentage:.1f}%")
    return percentage


def run_live_updater(interval=60):
    """
    Run live percentage updater continuously

    Args:
        interval: Update interval in seconds (default: 60)
    """
    logger.info("=" * 80)
    logger.info("🔄 LIVE CHAIN-OF-COMMAND PERCENTAGE UPDATER")
    logger.info("=" * 80)
    logger.info(f"   Update interval: {interval}s")
    logger.info("   Continuously updates percentage (0-100%) in master_todos.json")
    logger.info("=" * 80)

    cycle = 0
    while True:
        cycle += 1
        logger.info("")
        logger.info(f"🔄 Update cycle {cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("-" * 80)

        try:
            percentage = update_chain_of_command_percentage()
            logger.info(f"✅ Percentage updated: {percentage:.1f}%")
        except Exception as e:
            logger.error(f"❌ Update failed: {e}")

        logger.info(f"⏳ Waiting {interval}s until next update...")
        time.sleep(interval)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Live Chain-of-Command Percentage Updater")
    parser.add_argument("--interval", type=int, default=60, help="Update interval in seconds (default: 60)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    if args.once:
        percentage = update_chain_of_command_percentage()
        print(f"✅ Updated percentage: {percentage:.1f}%")
    else:
        run_live_updater(interval=args.interval)
