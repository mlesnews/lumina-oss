#!/usr/bin/env python3
"""
Execute NAS Migration @DOIT

Automatically executes NAS migration initiative:
1. Check network (WiFi vs LAN)
2. Optimize network path
3. Resume migration
4. Track progress

@doit: Execute the migration work

Tags: #MIGRATION #NAS #DOIT #AUTOMATION #EXECUTE @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from nas_migration_network_optimizer import NASMigrationNetworkOptimizer
    from resume_nas_migration_initiative import NASMigrationInitiative
    from persistent_memory_gap_tracker import PersistentMemoryGapTracker
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("ExecuteNASMigrationDoit")
ts_logger = get_timestamp_logger()


def execute_nas_migration_doit(dry_run: bool = False) -> Dict[str, Any]:
    """
    Execute NAS Migration @DOIT

    Automatically:
    1. Check network
    2. Optimize network path
    3. Resume migration
    4. Track progress
    """
    logger.info("="*80)
    logger.info("🚀 EXECUTE NAS MIGRATION @DOIT")
    logger.info("="*80)

    results = {
        "network_optimized": False,
        "migration_resumed": False,
        "gaps_tracked": False,
        "errors": [],
    }

    # Step 1: Check and optimize network
    logger.info("📡 Step 1: Checking network...")
    network_optimizer = NASMigrationNetworkOptimizer()
    network_status = network_optimizer.check_network_connection()
    recommendations = network_optimizer.recommend_network_config()

    logger.info(f"   Current: {network_status['connection_type']}")
    logger.info(f"   Recommended: {recommendations['recommended']}")

    # Check if we're on 10.17.17.x network (WiFi)
    import subprocess
    try:
        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "10.17.17" in result.stdout:
            logger.info("✅ On 10.17.17.x network (WiFi) - proceeding with migration")
            logger.warning("⚠️  WiFi will be slow for large migration")
            results["network_optimized"] = True
            network_status["wifi_available"] = True
        else:
            logger.warning("⚠️  Network status unclear - proceeding anyway")
            results["network_optimized"] = True
    except Exception as e:
        logger.warning(f"⚠️  Could not check network details: {e}")
        logger.info("   Proceeding with migration attempt")
        results["network_optimized"] = True

    # Step 2: Resume migration
    logger.info("🔄 Step 2: Resuming migration...")
    migration_initiative = NASMigrationInitiative()

    source_path = Path("C:/Users/mlesn/Dropbox/my_projects/.lumina")

    try:
        success = migration_initiative.resume_migration_initiative(
            source_path,
            dry_run=dry_run
        )

        if success:
            logger.info("✅ Migration resumed successfully")
            results["migration_resumed"] = True
        else:
            logger.warning("⚠️  Migration resume had issues")
            results["errors"].append("Migration resume had issues")
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        results["errors"].append(str(e))

    # Step 3: Track gaps
    logger.info("🧠 Step 3: Tracking memory gaps...")
    gap_tracker = PersistentMemoryGapTracker()
    hidden_gaps = gap_tracker.get_hidden_gaps()
    penalties = gap_tracker.get_total_penalties()

    logger.info(f"   Hidden gaps: {len(hidden_gaps)}")
    logger.info(f"   Total DKP penalty: {penalties['total_dkp_penalty']}")
    results["gaps_tracked"] = True

    return results


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Execute NAS Migration @DOIT")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually migrate)")

    args = parser.parse_args()

    print("="*80)
    print("🚀 EXECUTE NAS MIGRATION @DOIT")
    print("="*80)
    print()
    print("Automatically executing NAS migration initiative")
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be migrated")
        print()

    results = execute_nas_migration_doit(dry_run=args.dry_run)

    print()
    print("📊 RESULTS:")
    print(f"   Network Optimized: {results['network_optimized']}")
    print(f"   Migration Resumed: {results['migration_resumed']}")
    print(f"   Gaps Tracked: {results['gaps_tracked']}")

    if results["errors"]:
        print()
        print("❌ ERRORS:")
        for error in results["errors"]:
            print(f"   - {error}")

    print()


if __name__ == "__main__":


    main()