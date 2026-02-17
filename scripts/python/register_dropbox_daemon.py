#!/usr/bin/env python3
"""
Register Dropbox Optimized Daemon with NAS Kron
<COMPANY_NAME> LLC

Registers Dropbox optimized processor daemon with NAS Kron scheduler.

@JARVIS @MARVIN @SYPHON
"""

import sys
from pathlib import Path
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from nas_kron_daemon_manager import NASKronDaemonManager

def main():
    try:
        """Register Dropbox daemon with NAS Kron"""

        project_root = Path(__file__).parent.parent.parent
        manager = NASKronDaemonManager(project_root)

        # Create cron entry for Dropbox daemon
        # Run every hour (at minute 0)
        cron_entry = f"""# Dropbox Optimized Processor Daemon
# Runs every hour to process Dropbox files with caching and resource-aware processing
0 * * * * cd {project_root} && python scripts/python/dropbox_optimized_daemon.py start --path "C:\\Users\\mlesn\\Dropbox" --interval 60 >> logs/dropbox_daemon.log 2>&1
"""

        # Save cron file
        cron_file = project_root / "data" / "tasks" / "nas_kron" / "dropbox_optimized_daemon.cron"
        cron_file.parent.mkdir(parents=True, exist_ok=True)

        with open(cron_file, 'w', encoding='utf-8') as f:
            f.write(cron_entry)

        print(f"✅ Cron file created: {cron_file}")
        print("\nCron entry:")
        print(cron_entry)

        # Deploy to NAS
        print("\n🚀 Deploying to NAS Kron scheduler...")
        success = manager.deploy_cron_to_nas(cron_file)

        if success:
            print("✅ Dropbox daemon registered with NAS Kron scheduler")
            print("   The daemon will run every hour to optimize Dropbox processing")
        else:
            print("⚠️  Failed to deploy to NAS - cron file saved locally")
            print(f"   You can manually deploy: {cron_file}")

        return 0 if success else 1
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":



    sys.exit(main())