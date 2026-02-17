#!/usr/bin/env python3
"""
JARVIS System Reboot with Full Tracing

Performs system reboot with comprehensive tracing, capture, and tracking for performance tuning.
Tracks all startup/shutdown procedures in a staggered parallel manner.

Tags: #REBOOT #TRACING #PERFORMANCE #STARTUP #SHUTDOWN #OPTIMIZATION @JARVIS @LUMINA
"""

import sys
import json
import time
import os
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISReboot")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISReboot")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISReboot")

# Import performance tracker and optimized executor
try:
    from jarvis_startup_performance_tracker import StartupPerformanceTracker, PhaseType
    from jarvis_optimized_startup_executor import OptimizedStartupExecutor
    TRACKING_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.jarvis_startup_performance_tracker import StartupPerformanceTracker, PhaseType
        from scripts.python.jarvis_optimized_startup_executor import OptimizedStartupExecutor
        TRACKING_AVAILABLE = True
    except ImportError:
        TRACKING_AVAILABLE = False
        logger.warning("Performance tracking not available")


class SystemRebootWithTracing:
    """System reboot with full tracing and performance tracking"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "reboot_tracing"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.reboot_log = self.data_dir / "reboot_log.jsonl"
        self.reboot_marker_file = self.data_dir / "reboot_marker.json"

        # Performance tracking
        if TRACKING_AVAILABLE:
            try:
                self.perf_tracker = StartupPerformanceTracker(project_root)
                self.startup_executor = OptimizedStartupExecutor(project_root)
                logger.info("✅ Performance tracking and optimized executor initialized")
            except Exception as e:
                logger.warning(f"Performance tracking initialization failed: {e}")
                self.perf_tracker = None
                self.startup_executor = None
        else:
            self.perf_tracker = None
            self.startup_executor = None

    def create_reboot_marker(self, reason: str = "Performance optimization reboot") -> Dict[str, Any]:
        """Create reboot marker to track reboot cycle"""
        marker = {
            "reboot_id": f"reboot_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "platform": platform.system(),
            "platform_version": platform.version(),
            "pre_reboot_tracking": True,
            "post_reboot_tracking": True
        }

        try:
            with open(self.reboot_marker_file, 'w', encoding='utf-8') as f:
                json.dump(marker, f, indent=2, default=str)
            logger.info(f"✅ Reboot marker created: {marker['reboot_id']}")
        except Exception as e:
            logger.error(f"Error creating reboot marker: {e}")

        return marker

    def check_reboot_marker(self) -> Optional[Dict[str, Any]]:
        """Check if we're in a post-reboot state"""
        if not self.reboot_marker_file.exists():
            return None

        try:
            with open(self.reboot_marker_file, 'r', encoding='utf-8') as f:
                marker = json.load(f)
            return marker
        except Exception as e:
            logger.error(f"Error reading reboot marker: {e}")
            return None

    def perform_shutdown_tracking(self) -> Dict[str, Any]:
        """Track shutdown performance"""
        if not self.perf_tracker:
            return {}

        logger.info("=" * 80)
        logger.info("📊 STARTING SHUTDOWN PERFORMANCE TRACKING")
        logger.info("=" * 80)

        phase_id = self.perf_tracker.start_phase(PhaseType.SHUTDOWN)

        # Wait a moment to capture shutdown metrics
        time.sleep(2)

        report = self.perf_tracker.stop_phase()

        logger.info("=" * 80)
        logger.info("📊 SHUTDOWN TRACKING COMPLETE")
        logger.info("=" * 80)

        return report

    def perform_reboot(self, reason: str = "Performance optimization reboot", delay_seconds: int = 10) -> None:
        """Perform system reboot with full tracing"""
        logger.info("=" * 80)
        logger.info("🔄 SYSTEM REBOOT WITH FULL TRACING")
        logger.info("=" * 80)
        logger.info(f"Reason: {reason}")
        logger.info(f"Delay: {delay_seconds} seconds")
        logger.info("=" * 80)

        # Create reboot marker
        marker = self.create_reboot_marker(reason)

        # Start shutdown tracking
        shutdown_report = self.perform_shutdown_tracking()

        # Log reboot initiation
        reboot_entry = {
            "timestamp": datetime.now().isoformat(),
            "reboot_id": marker["reboot_id"],
            "reason": reason,
            "shutdown_report": shutdown_report,
            "status": "initiated"
        }

        try:
            with open(self.reboot_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(reboot_entry) + '\n')
        except Exception as e:
            logger.error(f"Error logging reboot: {e}")

        logger.info(f"⏳ Reboot will occur in {delay_seconds} seconds...")
        logger.info("📊 Full tracing will be captured on next startup")
        logger.info("=" * 80)

        # Countdown
        for i in range(delay_seconds, 0, -1):
            logger.info(f"   {i}...")
            time.sleep(1)

        # Perform reboot based on platform
        system = platform.system()
        if system == "Windows":
            logger.info("🔄 Initiating Windows reboot...")
            os.system("shutdown /r /t 0 /f")
        elif system == "Linux":
            logger.info("🔄 Initiating Linux reboot...")
            os.system("sudo reboot")
        elif system == "Darwin":  # macOS
            logger.info("🔄 Initiating macOS reboot...")
            os.system("sudo reboot")
        else:
            logger.error(f"Unsupported platform: {system}")
            logger.info("Please reboot manually")

    def handle_post_reboot(self) -> Dict[str, Any]:
        """Handle post-reboot startup with full tracing"""
        marker = self.check_reboot_marker()
        if not marker:
            logger.info("No reboot marker found - normal startup")
            return {}

        logger.info("=" * 80)
        logger.info("🔄 POST-REBOOT STARTUP WITH FULL TRACING")
        logger.info("=" * 80)
        logger.info(f"Reboot ID: {marker['reboot_id']}")
        logger.info(f"Reboot Time: {marker['timestamp']}")
        logger.info(f"Reason: {marker.get('reason', 'Unknown')}")
        logger.info("=" * 80)

        # Start startup performance tracking
        if self.perf_tracker:
            phase_id = self.perf_tracker.start_phase(PhaseType.STARTUP)
            logger.info(f"Performance tracking started: {phase_id}")

        # Execute optimized startup
        if self.startup_executor:
            startup_result = self.startup_executor.execute_optimized_startup()
        else:
            startup_result = {"error": "Optimized executor not available"}

        # Stop performance tracking
        if self.perf_tracker:
            report = self.perf_tracker.stop_phase()
            startup_result["performance_report"] = report

        # Update marker
        marker["post_reboot_completed"] = True
        marker["post_reboot_completed_at"] = datetime.now().isoformat()
        marker["startup_result"] = startup_result

        try:
            with open(self.reboot_marker_file, 'w', encoding='utf-8') as f:
                json.dump(marker, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error updating reboot marker: {e}")

        # Log completion
        reboot_entry = {
            "timestamp": datetime.now().isoformat(),
            "reboot_id": marker["reboot_id"],
            "status": "post_reboot_completed",
            "startup_result": startup_result
        }

        try:
            with open(self.reboot_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(reboot_entry) + '\n')
        except Exception as e:
            logger.error(f"Error logging reboot completion: {e}")

        logger.info("=" * 80)
        logger.info("🔄 POST-REBOOT STARTUP COMPLETE")
        logger.info("=" * 80)

        return startup_result


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS System Reboot with Full Tracing")
        parser.add_argument("--reboot", action="store_true", help="Perform system reboot with tracing")
        parser.add_argument("--reason", type=str, default="Performance optimization reboot",
                           help="Reason for reboot")
        parser.add_argument("--delay", type=int, default=10, help="Delay before reboot (seconds)")
        parser.add_argument("--post-reboot", action="store_true", help="Handle post-reboot startup")
        parser.add_argument("--check-marker", action="store_true", help="Check reboot marker")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        reboot_system = SystemRebootWithTracing(project_root)

        if args.reboot:
            reboot_system.perform_reboot(args.reason, args.delay)

        elif args.post_reboot:
            result = reboot_system.handle_post_reboot()
            print("=" * 80)
            print("POST-REBOOT STARTUP RESULT")
            print("=" * 80)
            print(json.dumps(result, indent=2, default=str))

        elif args.check_marker:
            marker = reboot_system.check_reboot_marker()
            if marker:
                print("=" * 80)
                print("REBOOT MARKER FOUND")
                print("=" * 80)
                print(json.dumps(marker, indent=2, default=str))
            else:
                print("No reboot marker found")

        else:
            print("JARVIS System Reboot with Full Tracing")
            print("Use --help for usage information")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()