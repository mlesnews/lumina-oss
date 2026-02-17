#!/usr/bin/env python3
"""
SYPHON Lumina Hourly - NAS KRON SCHEDULER Executor

Executes hourly SYPHON Lumina operations as ordered by NAS KRON SCHEDULER.
SYPHONs the entire Lumina ecosystem to extract intelligence.

ORDER 66: @DOIT execution command

Tags: #SYPHON #LUMINA #HOURLY #NAS #KRON #SCHEDULER #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# SYPHON system integration
try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    SubscriptionTier = None
    logger = get_logger("SyphonLuminaHourly")
    logger.warning("SYPHON system not available")

# NAS Kron scheduler integration
try:
    from nas_kron_daemon_manager import NASKronDaemonManager
    NAS_KRON_AVAILABLE = True
except ImportError:
    NAS_KRON_AVAILABLE = False
    NASKronDaemonManager = None
    logger = get_logger("SyphonLuminaHourly")
    logger.warning("NAS Kron Daemon Manager not available")

logger = get_logger("SyphonLuminaHourly")


class SyphonLuminaHourlyNASKron:
    """
    SYPHON Lumina Hourly - NAS KRON SCHEDULER Executor

    Executes hourly SYPHON Lumina operations as ordered by NAS KRON SCHEDULER.
    SYPHONs the entire Lumina ecosystem to extract intelligence.

    ORDER 66: @DOIT execution command
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize hourly SYPHON Lumina executor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "syphon_lumina_hourly"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # SYPHON system
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.ENTERPRISE,
                    enable_self_healing=True
                )
                self.syphon = SYPHONSystem(config)
                logger.info("✅ SYPHON System initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON System not available: {e}")

        # NAS Kron scheduler
        self.nas_kron = None
        if NAS_KRON_AVAILABLE:
            try:
                self.nas_kron = NASKronDaemonManager(project_root=self.project_root)
                logger.info("✅ NAS Kron Daemon Manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  NAS Kron Daemon Manager not available: {e}")

        logger.info("✅ SYPHON Lumina Hourly NAS Kron Executor initialized")

    def execute_syphon_lumina(self) -> Dict[str, Any]:
        """
        Execute SYPHON Lumina operation

        ORDER 66: @DOIT execution command

        Returns:
            Dict with execution results
        """
        logger.info("="*80)
        logger.info("🔍 ORDER 66: Executing SYPHON LUMINA (Hourly)")
        logger.info("   Ordered by: NAS KRON SCHEDULER")
        logger.info("="*80)

        execution_result = {
            "timestamp": datetime.now().isoformat(),
            "ordered_by": "NAS KRON SCHEDULER",
            "execution_type": "ORDER 66: @DOIT",
            "command": "syphon_lumina",
            "success": False,
            "errors": [],
            "intelligence_extracted": 0,
            "files_processed": 0,
            "dirs_processed": 0
        }

        if not self.syphon:
            error_msg = "SYPHON System not available"
            logger.error(f"❌ {error_msg}")
            execution_result["errors"].append(error_msg)
            return execution_result

        try:
            # Execute SYPHON Lumina
            logger.info("🔍 SYPHONing Lumina ecosystem...")
            result = self.syphon.syphon_lumina(
                project_root=self.project_root,
                max_depth=100
            )

            if result and result.get("success", False):
                execution_result["success"] = True
                execution_result["intelligence_extracted"] = len(result.get("intelligence", []))
                execution_result["files_processed"] = result.get("processed_files", 0)
                execution_result["dirs_processed"] = result.get("processed_dirs", 0)
                execution_result["result"] = result

                logger.info(
                    f"✅ SYPHON LUMINA Complete: "
                    f"{execution_result['files_processed']} files, "
                    f"{execution_result['dirs_processed']} dirs, "
                    f"{execution_result['intelligence_extracted']} intelligence items"
                )
            else:
                error_msg = "SYPHON Lumina returned unsuccessful result"
                logger.warning(f"⚠️  {error_msg}")
                execution_result["errors"].append(error_msg)
                if result:
                    execution_result["result"] = result

        except Exception as e:
            error_msg = f"Error executing SYPHON Lumina: {e}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            execution_result["errors"].append(error_msg)

        # Save execution result
        result_file = self.data_dir / f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(execution_result, f, indent=2, default=str, ensure_ascii=False)
            logger.info(f"💾 Execution result saved: {result_file.name}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save execution result: {e}")

        logger.info("="*80)
        if execution_result["success"]:
            logger.info("✅ ORDER 66: SYPHON LUMINA execution complete")
        else:
            logger.info("❌ ORDER 66: Execution completed with errors")
        logger.info("="*80)

        return execution_result

    def create_hourly_cron_file(self) -> Path:
        """
        Create hourly cron file for NAS KRON SCHEDULER

        The cron job will SSH from NAS to Windows to execute the script.
        This allows the script to run on Windows where the Lumina project is located.

        Returns:
            Path to cron file
        """
        try:
            logger.info("📅 Creating hourly cron file for NAS KRON SCHEDULER...")

            # Get Windows host info (for SSH from NAS to Windows)
            # The NAS will SSH to Windows to run the script
            windows_host = "localhost"  # Adjust if Windows has a different hostname/IP on the network
            windows_user = None  # Will use current user or configure separately

            # Get Python path (Windows path)
            python_path = sys.executable.replace("\\", "/")

            # Get script path (Windows path, converted for SSH)
            script_path = Path(__file__).absolute()
            script_path_ssh = str(script_path).replace("\\", "/")

            # Get log path
            log_path = (self.data_dir / "hourly_syphon.log").absolute()
            log_path_ssh = str(log_path).replace("\\", "/")

            # Create cron entry (runs every hour at minute 0)
            # Option 1: If script is accessible via network share from NAS
            # Option 2: SSH from NAS to Windows (requires SSH server on Windows)
            # Option 3: Run script on NAS if project is synced there

            # For now, create a cron that runs the script directly if it's on a network share
            # Or use SSH if configured. Default: assume script is accessible via network path
            # The user can adjust the path based on their NAS setup

            cron_entry = f"""# SYPHON Lumina Hourly - NAS KRON SCHEDULER
# Runs every hour at minute 0
# ORDER 66: @DOIT execution command
# 
# NOTE: This cron job assumes the script is accessible from the NAS.
# Options:
# 1. If project is synced to NAS: Use NAS path to script
# 2. If using network share: Use mounted share path
# 3. If SSH to Windows: Use SSH command (requires SSH server on Windows)
#
# Example for network share (adjust path as needed):
# 0 * * * * /volume1/@appstore/python3/bin/python3 /volume1/shares/lumina/scripts/python/syphon_lumina_hourly_nas_kron.py >> /volume1/shares/lumina/data/syphon_lumina_hourly/hourly_syphon.log 2>&1
#
# Example for SSH to Windows (requires SSH server on Windows):
# 0 * * * * ssh {windows_user}@{windows_host} "{python_path} {script_path_ssh}" >> {log_path_ssh} 2>&1
#
# Current configuration (Windows paths - adjust for your NAS setup):
0 * * * * {python_path} {script_path_ssh} >> {log_path_ssh} 2>&1
"""

            # Save cron file
            cron_file = self.data_dir / "syphon_lumina_hourly.cron"
            with open(cron_file, 'w', encoding='utf-8') as f:
                f.write(cron_entry)

            logger.info(f"✅ Cron file created: {cron_file}")
            logger.info("⚠️  NOTE: You may need to adjust the paths in the cron file based on your NAS setup:")
            logger.info("   - If project is synced to NAS, use NAS paths")
            logger.info("   - If using network share, use mounted share paths")
            logger.info("   - If SSH to Windows, configure SSH server on Windows first")

            return cron_file
        except Exception as e:
            logger.error(f"Error in create_hourly_cron_file: {e}", exc_info=True)
            raise

    def deploy_to_nas_kron(self) -> bool:
        """
        Deploy hourly SYPHON Lumina to NAS KRON SCHEDULER

        Returns:
            True if deployment successful
        """
        if not self.nas_kron:
            logger.warning("⚠️  NAS Kron Daemon Manager not available")
            return False

        try:
            logger.info("📅 Deploying hourly SYPHON Lumina to NAS KRON SCHEDULER...")

            # Create cron file
            cron_file = self.create_hourly_cron_file()

            # Deploy to NAS
            if self.nas_kron.deploy_cron_to_nas(cron_file):
                logger.info("✅ Hourly SYPHON Lumina deployed to NAS KRON SCHEDULER")
                return True
            else:
                logger.error("❌ Failed to deploy to NAS KRON SCHEDULER")
                return False

        except Exception as e:
            logger.error(f"❌ Error deploying to NAS KRON SCHEDULER: {e}", exc_info=True)
            return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 ORDER 66: SYPHON LUMINA HOURLY - NAS KRON SCHEDULER")
    print("="*80 + "\n")

    executor = SyphonLuminaHourlyNASKron()

    # Check if we should deploy or execute
    import argparse
    parser = argparse.ArgumentParser(description="SYPHON Lumina Hourly - NAS KRON SCHEDULER")
    parser.add_argument("--deploy", action="store_true", help="Deploy to NAS KRON SCHEDULER")
    parser.add_argument("--execute", action="store_true", help="Execute SYPHON Lumina (default)")

    args = parser.parse_args()

    if args.deploy:
        # Deploy to NAS KRON SCHEDULER
        success = executor.deploy_to_nas_kron()
        if success:
            print("\n✅ ORDER 66: Deployment Complete")
        else:
            print("\n❌ ORDER 66: Deployment Failed")
    else:
        # Execute SYPHON Lumina
        result = executor.execute_syphon_lumina()

        print("\n" + "="*80)
        print("📊 EXECUTION RESULT")
        print("="*80)
        print(f"Ordered By: {result['ordered_by']}")
        print(f"Execution Type: {result['execution_type']}")
        print(f"Success: {result['success']}")
        print(f"Files Processed: {result['files_processed']}")
        print(f"Dirs Processed: {result['dirs_processed']}")
        print(f"Intelligence Extracted: {result['intelligence_extracted']}")

        if result.get('errors'):
            print(f"\n  Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"    ⚠️  {error}")

        print("\n✅ ORDER 66: Execution Complete")
        print("="*80 + "\n")
