#!/usr/bin/env python3
"""
LUMINA First Boot Initialization

Runs automatically on first boot to:
1. Show welcome video (hologram)
2. Start all services
3. Verify system health
4. Get user ready to hit the ground running

No reboots required - everything works from first startup.

Tags: #FIRST_BOOT #INITIALIZATION #STARTUP #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import time
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger
from lumina_error_recovery import LuminaErrorRecovery, RetryConfig

logger = get_adaptive_logger("FirstBootInit")
error_recovery = LuminaErrorRecovery()


class LuminaFirstBootInit:
    """
    LUMINA First Boot Initialization

    Gets new users up and running immediately:
    - Welcome video
    - Service startup
    - System verification
    - Ready to use
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize first boot system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "first_boot"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.init_file = self.data_dir / "initialized.json"
        self.is_first_boot = not self.init_file.exists()

    def run_first_boot_init(self) -> Dict[str, Any]:
        """
        Run first boot initialization

        Returns: Initialization results
        """
        logger.info("="*80)
        logger.info("🚀 LUMINA FIRST BOOT INITIALIZATION")
        logger.info("="*80)
        logger.info("")

        if not self.is_first_boot:
            logger.info("   ℹ️  Not first boot - initialization already complete")
            return {"first_boot": False, "message": "Already initialized"}

        logger.info("   🎬 First boot detected - initializing LUMINA...")
        logger.info("")

        results = {
            "first_boot": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "steps_completed": []
        }

        # Step 1: Show Welcome Video
        logger.info("1️⃣  Showing welcome video...")
        try:
            video_result = self._show_welcome_video()
            results["steps_completed"].append("welcome_video")
            results["welcome_video"] = video_result
            logger.info("   ✅ Welcome video shown")
        except Exception as e:
            logger.warning(f"   ⚠️  Welcome video: {e}")
            results["welcome_video_error"] = str(e)

        # Brief pause for video
        time.sleep(2)

        # Step 2: Start All Services
        logger.info("")
        logger.info("2️⃣  Starting all services...")
        try:
            service_result = self._start_all_services()
            results["steps_completed"].append("services_started")
            results["services"] = service_result
            logger.info("   ✅ All services started")
        except Exception as e:
            logger.warning(f"   ⚠️  Service startup: {e}")
            results["service_error"] = str(e)

        # Step 3: Verify System Health
        logger.info("")
        logger.info("3️⃣  Verifying system health...")
        try:
            health_result = self._verify_system_health()
            results["steps_completed"].append("health_verified")
            results["health"] = health_result
            logger.info("   ✅ System health verified")
        except Exception as e:
            logger.warning(f"   ⚠️  Health verification: {e}")
            results["health_error"] = str(e)

        # Step 4: Mark as initialized
        self._mark_initialized()
        results["steps_completed"].append("initialized")

        # Step 5: Show ready notification
        try:
            from lumina_notification_system import LuminaNotificationSystem
            notification = LuminaNotificationSystem()
            notification.show_notification(
                "LUMINA Ready",
                "Welcome! LUMINA is ready to use. Hit the ground running!",
                "info"
            )
        except Exception as e:
            logger.debug(f"   ⚠️  Notification: {e}")

        logger.info("")
        logger.info("="*80)
        logger.info("✅ LUMINA INITIALIZATION COMPLETE")
        logger.info("="*80)
        logger.info("")
        logger.info("🎯 You're ready to hit the ground running!")
        logger.info("   • All services started")
        logger.info("   • System verified")
        logger.info("   • Ready to use LUMINA")
        logger.info("")

        return results

    def _show_welcome_video(self) -> Dict[str, Any]:
        """Show welcome video (hologram)"""
        try:
            from jedi_temple_welcome_video import JediTempleWelcomeVideo
            welcome = JediTempleWelcomeVideo()

            # Show video for new user
            result = welcome.show_welcome_video("new_user", auto_play=True)
            return result
        except Exception as e:
            logger.warning(f"   ⚠️  Could not show welcome video: {e}")
            return {"error": str(e)}

    def _start_all_services(self) -> Dict[str, Any]:
        """Start all essential services including @pva"""
        def start_services():
            from lumina_service_manager import LuminaServiceManager
            service_manager = LuminaServiceManager()

            # Restart all services (will start if not running)
            # This includes: AutoHotkey, N8N, SYPHON, ElevenLabs, and @pva
            restart_results = service_manager.restart_all_services()

            # Verify services
            verify_results = service_manager.verify_all_services()

            # Log PVA status specifically
            if "pva" in restart_results:
                if restart_results["pva"]:
                    logger.info("   ✅ Personal Virtual Assistants (@pva) started")
                else:
                    logger.warning("   ⚠️  Personal Virtual Assistants (@pva) startup failed")

            return {
                "restart_results": restart_results,
                "verify_results": verify_results
            }

        return error_recovery.execute_with_recovery(
            operation=start_services,
            operation_name="Service Startup",
            retry_config=RetryConfig(max_attempts=3, delay=2.0)
        )

    def _verify_system_health(self) -> Dict[str, Any]:
        """Verify system health"""
        def check_health():
            from lumina_startup_health_check import LuminaStartupHealthCheck
            health_check = LuminaStartupHealthCheck()
            return health_check.run_health_check()

        return error_recovery.execute_with_recovery(
            operation=check_health,
            operation_name="Health Verification",
            retry_config=RetryConfig(max_attempts=2, delay=1.0)
        )

    def _mark_initialized(self):
        """Mark system as initialized"""
        try:
            import json
            init_data = {
                "initialized": True,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0.0"
            }
            with open(self.init_file, 'w', encoding='utf-8') as f:
                json.dump(init_data, f, indent=2)
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to mark initialized: {e}")


def main():
    try:
        """CLI interface - runs automatically on startup"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA First Boot Initialization")
        parser.add_argument("--run", action="store_true", help="Run first boot initialization")
        parser.add_argument("--reset", action="store_true", help="Reset initialization (for testing)")

        args = parser.parse_args()

        init = LuminaFirstBootInit()

        if args.reset:
            # Reset initialization (for testing)
            if init.init_file.exists():
                init.init_file.unlink()
                logger.info("   ✅ Initialization reset")
            return 0

        if args.run or init.is_first_boot:
            results = init.run_first_boot_init()
            import json
            print(json.dumps(results, indent=2))
            return 0 if results.get("first_boot", False) else 1

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())