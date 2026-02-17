#!/usr/bin/env python3
"""
Create All Cron Entries for Documented Tasks
<COMPANY_NAME> LLC

Creates cron entries for all documented scheduled tasks:
- WOPR automation tasks
- Dropbox optimization
- Other recurring tasks

@JARVIS @MARVIN @SYPHON
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from nas_kron_daemon_manager import NASKronDaemonManager
import logging
logger = logging.getLogger("create_all_cron_entries")


def create_wopr_cron_entries(project_root: Path) -> Path:
    """Create cron entries for WOPR automation tasks"""

    cron_content = """# WOPR Automation - Daily Tasks
# Daily operations check
0 0 * * * cd {project_root} && python scripts/python/wopr_ops.py >> logs/wopr_daily_ops.log 2>&1

# Status report generation
0 6 * * * cd {project_root} && python scripts/python/wopr_status_report.py >> logs/wopr_status_report.log 2>&1

# Threat feed check
0 12 * * * cd {project_root} && python scripts/python/holocron_threat_monitor.py --check >> logs/wopr_threat_feed.log 2>&1

# Containment status check
0 18 * * * cd {project_root} && python scripts/python/wopr_ops.py --containment-check >> logs/wopr_containment.log 2>&1

# WOPR Automation - Weekly Tasks
# Weekly summary report (Monday 00:00)
0 0 * * 1 cd {project_root} && python scripts/python/wopr_status_report.py --weekly >> logs/wopr_weekly_report.log 2>&1

# Integration verification (Wednesday 00:00)
0 0 * * 3 cd {project_root} && python scripts/python/wopr_integration.py --verify >> logs/wopr_integration.log 2>&1

# Threat assessment update (Friday 00:00)
0 0 * * 5 cd {project_root} && python scripts/python/holocron_threat_monitor.py --assessment >> logs/wopr_threat_assessment.log 2>&1

# WOPR Automation - Monthly Tasks
# Monthly review (First of month)
0 0 1 * * cd {project_root} && python scripts/python/wopr_ops.py --monthly-review >> logs/wopr_monthly_review.log 2>&1

# Killswitch testing (15th of month)
0 0 15 * * cd {project_root} && python scripts/python/wopr_ops.py --killswitch-test >> logs/wopr_killswitch_test.log 2>&1

# Metrics compilation (Last of month - runs on 28th)
0 0 28 * * cd {project_root} && python scripts/python/wopr_status_report.py --monthly >> logs/wopr_monthly_metrics.log 2>&1
""".format(project_root=project_root)

    cron_file = project_root / "data" / "tasks" / "nas_kron" / "wopr_automation.cron"
    cron_file.parent.mkdir(parents=True, exist_ok=True)

    with open(cron_file, 'w', encoding='utf-8') as f:
        f.write(cron_content)

    return cron_file

def main():
    try:
        """Create all cron entries"""
        project_root = Path(__file__).parent.parent.parent

        print("=" * 80)
        print("CREATING ALL CRON ENTRIES FOR RECURRING TASKS")
        print("=" * 80)
        print()

        cron_files = []

        # 1. WOPR Automation
        print("📋 Creating WOPR automation cron entries...")
        wopr_cron = create_wopr_cron_entries(project_root)
        cron_files.append(wopr_cron)
        print(f"   ✅ Created: {wopr_cron.name}")
        print(f"      - 4 daily tasks")
        print(f"      - 3 weekly tasks")
        print(f"      - 3 monthly tasks")
        print()

        # 2. Dropbox Optimization (already exists)
        dropbox_cron = project_root / "data" / "tasks" / "nas_kron" / "dropbox_optimized_daemon.cron"
        if dropbox_cron.exists():
            cron_files.append(dropbox_cron)
            print(f"   ✅ Dropbox daemon: {dropbox_cron.name}")
            print(f"      - Runs every hour")
            print()

        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total cron files created: {len(cron_files)}")
        print()

        for cron_file in cron_files:
            print(f"  ✓ {cron_file.name}")

        print()
        print("=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("1. Review cron files in: data/tasks/nas_kron/")
        print("2. Deploy to NAS Kron:")
        print("   python nas_kron_daemon_manager.py --deploy <cron_file>")
        print("3. Or deploy all:")
        print("   for file in data/tasks/nas_kron/*.cron; do")
        print("     python nas_kron_daemon_manager.py --deploy $file")
        print("   done")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()