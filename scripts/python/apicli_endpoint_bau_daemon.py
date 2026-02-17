#!/usr/bin/env python3
"""
APICLI Endpoint @BAU Daemon

Headless daemon for automated, scheduled, recurring NAS cron scheduler task.
Runs APICLI endpoint updates at configured intervals as part of @bau workflows.

Intervals:
- @v3 Verification: Every 15-30 minutes (configurable)
- Health Checks: Every 5-10 minutes (configurable)
- Full Update: Every hour (configurable)

Tags: #APICLI #BAU #V3 #HEALTH_CHECK #DAEMON #NAS #CRON @JARVIS @LUMINA
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional

from lumina_core.paths import get_script_dir
script_dir = get_script_dir()
project_root = script_dir.parent.parent
from lumina_core.paths import setup_paths
setup_paths()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Import daemon template
try:
    from daemon_template import BaseDaemon
except ImportError:
    from lumina_core.logging import get_logger

from apicli_endpoint_bau_updater import APICLIEndpointBAUUpdater


class APICLIEndpointBAUDaemon(BaseDaemon):
    """
    APICLI Endpoint @BAU Daemon

    Automated daemon for scheduled APICLI endpoint updates as part of @bau workflows.
    Supports multiple check modes and intervals.
    """

    def __init__(self, 
                 check_mode: str = "full",
                 interval: int = 3600,
                 project_root: Optional[Path] = None):
        """
        Initialize APICLI endpoint @BAU daemon

        Args:
            check_mode: Check mode - "v3_only", "health_only", or "full"
            interval: Cycle interval in seconds
            project_root: Project root directory
        """
        self.check_mode = check_mode
        self.interval = interval

        # Determine log subdirectory based on mode
        log_subdir = f"apicli_bau_{check_mode}"

        super().__init__(
            daemon_name=f"APICLIEndpointBAU-{check_mode}",
            log_subdirectory=log_subdir,
            project_root=project_root,
            interval=interval
        )

        # Initialize updater
        self.updater = APICLIEndpointBAUUpdater(project_root=project_root)

        self.logger.info(f"✅ APICLI Endpoint @BAU Daemon initialized")
        self.logger.info(f"   Mode: {check_mode}")
        self.logger.info(f"   Interval: {interval}s ({interval/60:.1f} minutes)")

    def _run_cycle(self):
        """Run one cycle of endpoint checks"""
        self.logger.info("=" * 80)
        self.logger.info(f"Starting @BAU endpoint check cycle ({self.check_mode})")
        self.logger.info("=" * 80)

        try:
            if self.check_mode == "v3_only":
                # Run only @v3 verification
                self.logger.info("Running @v3 verification (first pass)...")
                results = asyncio.run(self._run_v3_verification())
                self.logger.info(f"✅ @v3 verification complete: {len([r for r in results if r.verified])}/{len(results)} verified")

            elif self.check_mode == "health_only":
                # Run only health and welfare checks
                self.logger.info("Running health & welfare checks (second pass)...")
                results = asyncio.run(self._run_health_checks())
                self.logger.info(f"✅ Health checks complete: {len(results)} endpoints checked")

            else:  # full
                # Run full update
                self.logger.info("Running full @BAU endpoint update...")
                report = asyncio.run(self.updater.update_all_endpoints_bau())

                self.logger.info("=" * 80)
                self.logger.info("📊 Update Report Summary")
                self.logger.info("=" * 80)
                self.logger.info(f"   @v3 Verified: {report['v3_verification']['verified']}/{report['v3_verification']['total_endpoints']}")
                self.logger.info(f"   Health Status: {report['health_welfare_checks']['healthy']} healthy, {report['health_welfare_checks']['degraded']} degraded")
                self.logger.info(f"   Datapoints: {report['datapoints_summary']['total']} total, {report['datapoints_summary']['healthy']} healthy, {report['datapoints_summary']['critical']} critical")
                self.logger.info(f"   Painpoints: {report['painpoints_summary']['total']} total, {report['painpoints_summary']['active']} active, {report['painpoints_summary']['critical']} critical")
                self.logger.info(f"   Interconnected: {report['interconnected_endpoints']['total_connections']} connections")
                self.logger.info("=" * 80)

            self.logger.info("✅ Cycle complete")

        except Exception as e:
            self.logger.error(f"❌ Error in cycle: {e}", exc_info=True)
            raise

    async def _run_v3_verification(self):
        """Run @v3 verification only"""
        results = []
        for endpoint in self.updater.endpoints:
            if endpoint.bau_workflow:
                result = await self.updater._v3_verify_endpoint(endpoint)
                results.append(result)
                self.updater.v3_results.append(result)
        return results

    async def _run_health_checks(self):
        """Run health and welfare checks only"""
        results = []
        for endpoint in self.updater.endpoints:
            if endpoint.bau_workflow:
                result = await self.updater._health_welfare_check(endpoint)
                results.append(result)
                self.updater.health_welfare_results.append(result)
                endpoint.last_health_check = self.updater.updater.__class__.__module__  # Fix this
        return results


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="APICLI Endpoint @BAU Daemon - Automated endpoint health monitoring"
    )
    parser.add_argument(
        "--mode",
        choices=["v3_only", "health_only", "full"],
        default="full",
        help="Check mode: v3_only, health_only, or full (default: full)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Cycle interval in seconds (default: 3600 = 1 hour)"
    )
    parser.add_argument(
        "--cycle",
        action="store_true",
        help="Run one cycle and exit (for cron)"
    )

    args = parser.parse_args()

    daemon = APICLIEndpointBAUDaemon(
        check_mode=args.mode,
        interval=args.interval
    )

    if args.cycle:
        # Run one cycle and exit (for cron)
        daemon._run_cycle()
    else:
        # Run as daemon
        daemon.run()


if __name__ == "__main__":


    main()