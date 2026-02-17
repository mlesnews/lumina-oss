#!/usr/bin/env python3
"""
Voice Systems Watchdog - Monitors and maintains voice system health

Continuously monitors voice systems and automatically restarts them if they fail:
- Auto-Send Monitor (Dynamic Listening Scaling)
- Auto-Accept Service (Keep All / Accept All)
- Full-Time Monitoring Service
- Voice Transcript Queue

Uses #troubleshooting → #decisioning workflow to diagnose and fix issues.

Tags: #troubleshooting #decisioning #WATCHDOG #VOICE_SYSTEM #MONITORING
"""

import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    logger = get_adaptive_logger("VoiceSystemsWatchdog")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("VoiceSystemsWatchdog")


class VoiceSystemsWatchdog:
    """
    Watchdog service for voice systems

    Monitors and maintains:
    - Auto-Send Monitor (dynamic listening scaling)
    - Auto-Accept Service (Keep All)
    - Full-Time Monitoring Service
    - Voice Transcript Queue
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize watchdog"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.running = False
        self.watchdog_thread = None

        # Monitoring intervals
        self.check_interval = 10.0  # Check every 10 seconds
        self.restart_cooldown = 30.0  # Wait 30 seconds between restarts

        # Track last restart times (prevent restart loops)
        self.last_restart_times: Dict[str, float] = {}

        # Health tracking
        self.health_status: Dict[str, Dict[str, Any]] = {}

        # Statistics
        self.stats = {
            "total_checks": 0,
            "restarts": 0,
            "issues_detected": 0,
            "issues_resolved": 0
        }

        logger.info("✅ Voice Systems Watchdog initialized")

    def start(self):
        """Start watchdog monitoring"""
        if self.running:
            logger.warning("Watchdog already running")
            return

        self.running = True
        self.watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            daemon=True,
            name="VoiceSystemsWatchdog"
        )
        self.watchdog_thread.start()
        logger.info("🚀 Voice Systems Watchdog started")

    def stop(self):
        """Stop watchdog"""
        self.running = False
        if self.watchdog_thread:
            self.watchdog_thread.join(timeout=5.0)
        logger.info("🛑 Voice Systems Watchdog stopped")

    def _watchdog_loop(self):
        """Main watchdog monitoring loop"""
        logger.info("📡 Watchdog monitoring active - checking systems every %.1fs", self.check_interval)

        while self.running:
            try:
                self.stats["total_checks"] += 1

                # Check all systems
                self._check_auto_send_monitor()
                self._check_auto_accept_service()
                self._check_full_time_monitoring()
                self._check_voice_transcript_queue()

                # Log health status periodically
                if self.stats["total_checks"] % 6 == 0:  # Every minute (6 * 10s)
                    self._log_health_status()

                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"❌ Watchdog loop error: {e}")
                time.sleep(self.check_interval)

    def _check_auto_send_monitor(self):
        """Check auto-send monitor health"""
        try:
            from cursor_auto_send_monitor import get_auto_send_monitor
            monitor = get_auto_send_monitor()

            if not monitor:
                self._record_issue("auto_send_monitor", "Monitor instance is None")
                self._restart_auto_send_monitor()
                return

            issues = []

            # Check if running
            if not monitor.running:
                issues.append("Monitor not running")

            # Check configuration
            if monitor.min_pause_threshold != 1.5:
                issues.append(f"Min threshold incorrect: {monitor.min_pause_threshold}s (expected 1.5s)")

            if issues:
                self._record_issue("auto_send_monitor", "; ".join(issues))
                self._restart_auto_send_monitor()
            else:
                self._record_health("auto_send_monitor", {
                    "running": monitor.running,
                    "enabled": monitor.enabled,
                    "min_threshold": monitor.min_pause_threshold,
                    "current_threshold": monitor.pause_threshold,
                    "has_pending": monitor.has_pending_message
                })

        except Exception as e:
            self._record_issue("auto_send_monitor", f"Error checking: {e}")
            logger.debug(f"Auto-send monitor check error: {e}")

    def _check_auto_accept_service(self):
        """Check auto-accept service health"""
        try:
            from cursor_ide_auto_accept import CursorIDEAutoAccept
            from full_time_monitoring_service import get_full_time_monitoring_service

            service = get_full_time_monitoring_service()

            issues = []

            # Check if instance exists in monitoring service
            if not hasattr(service, 'auto_accept_instance') or service.auto_accept_instance is None:
                issues.append("Instance not in monitoring service")

            # Check if thread is alive
            if hasattr(service, 'auto_accept_thread'):
                if not service.auto_accept_thread.is_alive():
                    issues.append("Monitoring thread not alive")
            else:
                issues.append("No monitoring thread found")

            # Check Cursor IDE detection
            if service.auto_accept_instance:
                if not service.auto_accept_instance._is_cursor_running():
                    issues.append("Cursor IDE not detected")

            if issues:
                self._record_issue("auto_accept_service", "; ".join(issues))
                self._restart_auto_accept_service(service)
            else:
                self._record_health("auto_accept_service", {
                    "instance_exists": service.auto_accept_instance is not None,
                    "thread_alive": service.auto_accept_thread.is_alive() if hasattr(service, 'auto_accept_thread') else False,
                    "cursor_detected": service.auto_accept_instance._is_cursor_running() if service.auto_accept_instance else False
                })

        except Exception as e:
            self._record_issue("auto_accept_service", f"Error checking: {e}")
            logger.debug(f"Auto-accept service check error: {e}")

    def _check_full_time_monitoring(self):
        """Check full-time monitoring service health"""
        try:
            from full_time_monitoring_service import get_full_time_monitoring_service
            service = get_full_time_monitoring_service()

            if not service.running:
                self._record_issue("full_time_monitoring", "Service not running")
                self._restart_full_time_monitoring(service)
            else:
                self._record_health("full_time_monitoring", {
                    "running": service.running,
                    "stats": service.stats
                })

        except Exception as e:
            self._record_issue("full_time_monitoring", f"Error checking: {e}")
            logger.debug(f"Full-time monitoring check error: {e}")

    def _check_voice_transcript_queue(self):
        """Check voice transcript queue health"""
        try:
            from voice_transcript_queue import get_voice_transcript_queue
            queue = get_voice_transcript_queue()

            stats = queue.get_stats()

            if not stats.get("processing", False):
                self._record_issue("voice_transcript_queue", "Queue not processing")
                self._restart_voice_transcript_queue(queue)
            else:
                self._record_health("voice_transcript_queue", {
                    "processing": stats.get("processing", False),
                    "queue_size": stats.get("queue_size", 0),
                    "total_queued": stats.get("total_queued", 0)
                })

        except Exception as e:
            self._record_issue("voice_transcript_queue", f"Error checking: {e}")
            logger.debug(f"Voice transcript queue check error: {e}")

    def _restart_auto_send_monitor(self):
        """Restart auto-send monitor"""
        system_name = "auto_send_monitor"

        # Check cooldown
        if self._is_in_cooldown(system_name):
            return

        try:
            logger.warning(f"🔄 Restarting {system_name}...")
            from cursor_auto_send_monitor import get_auto_send_monitor
            monitor = get_auto_send_monitor()

            if monitor:
                monitor.stop()
                time.sleep(1.0)
                monitor.start()
                self._record_restart(system_name)
                logger.info(f"✅ {system_name} restarted")
            else:
                logger.error(f"❌ Cannot restart {system_name} - instance is None")

        except Exception as e:
            logger.error(f"❌ Failed to restart {system_name}: {e}")

    def _restart_auto_accept_service(self, monitoring_service):
        """Restart auto-accept service"""
        system_name = "auto_accept_service"

        # Check cooldown
        if self._is_in_cooldown(system_name):
            return

        try:
            logger.warning(f"🔄 Restarting {system_name}...")
            import threading

            # Stop existing thread if alive
            if hasattr(monitoring_service, 'auto_accept_thread') and monitoring_service.auto_accept_thread.is_alive():
                # Can't easily stop, but we can restart the monitoring
                pass

            # Restart monitoring thread
            if monitoring_service.auto_accept_instance:
                auto_accept_thread = threading.Thread(
                    target=monitoring_service.auto_accept_instance.monitor_and_auto_accept,
                    daemon=True,
                    name="AutoAcceptMonitor",
                    kwargs={"interval": 0.5}
                )
                auto_accept_thread.start()
                monitoring_service.auto_accept_thread = auto_accept_thread
                self._record_restart(system_name)
                logger.info(f"✅ {system_name} restarted")
            else:
                logger.error(f"❌ Cannot restart {system_name} - instance is None")

        except Exception as e:
            logger.error(f"❌ Failed to restart {system_name}: {e}")

    def _restart_full_time_monitoring(self, service):
        """Restart full-time monitoring service"""
        system_name = "full_time_monitoring"

        # Check cooldown
        if self._is_in_cooldown(system_name):
            return

        try:
            logger.warning(f"🔄 Restarting {system_name}...")
            service.stop()
            time.sleep(2.0)
            service.start()
            self._record_restart(system_name)
            logger.info(f"✅ {system_name} restarted")

        except Exception as e:
            logger.error(f"❌ Failed to restart {system_name}: {e}")

    def _restart_voice_transcript_queue(self, queue):
        """Restart voice transcript queue"""
        system_name = "voice_transcript_queue"

        # Check cooldown
        if self._is_in_cooldown(system_name):
            return

        try:
            logger.warning(f"🔄 Restarting {system_name}...")
            queue.stop_processing()
            time.sleep(1.0)
            queue.start_processing()
            self._record_restart(system_name)
            logger.info(f"✅ {system_name} restarted")

        except Exception as e:
            logger.error(f"❌ Failed to restart {system_name}: {e}")

    def _is_in_cooldown(self, system_name: str) -> bool:
        """Check if system is in restart cooldown"""
        if system_name not in self.last_restart_times:
            return False

        time_since_restart = time.time() - self.last_restart_times[system_name]
        return time_since_restart < self.restart_cooldown

    def _record_restart(self, system_name: str):
        """Record that a system was restarted"""
        self.last_restart_times[system_name] = time.time()
        self.stats["restarts"] += 1
        self.stats["issues_resolved"] += 1

    def _record_issue(self, system_name: str, issue: str):
        """Record an issue with a system"""
        if system_name not in self.health_status or self.health_status[system_name].get("status") != "issue":
            self.stats["issues_detected"] += 1

        self.health_status[system_name] = {
            "status": "issue",
            "issue": issue,
            "timestamp": datetime.now().isoformat()
        }

    def _record_health(self, system_name: str, health_data: Dict[str, Any]):
        """Record healthy status for a system"""
        was_issue = self.health_status.get(system_name, {}).get("status") == "issue"

        self.health_status[system_name] = {
            "status": "healthy",
            "data": health_data,
            "timestamp": datetime.now().isoformat()
        }

        if was_issue:
            self.stats["issues_resolved"] += 1

    def _log_health_status(self):
        """Log current health status"""
        logger.info("📊 Voice Systems Health Status:")
        for system, status in self.health_status.items():
            if status.get("status") == "healthy":
                logger.info(f"   ✅ {system}: Healthy")
            else:
                logger.warning(f"   ⚠️  {system}: {status.get('issue', 'Unknown issue')}")

        logger.info(f"   Stats: {self.stats['total_checks']} checks, {self.stats['restarts']} restarts, "
                   f"{self.stats['issues_detected']} issues detected, {self.stats['issues_resolved']} resolved")

    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "running": self.running,
            "health_status": self.health_status,
            "stats": self.stats,
            "last_restarts": {
                system: datetime.fromtimestamp(time).isoformat()
                for system, time in self.last_restart_times.items()
            }
        }


_watchdog_instance = None

def get_voice_systems_watchdog() -> VoiceSystemsWatchdog:
    """Get or create global watchdog instance"""
    global _watchdog_instance
    if _watchdog_instance is None:
        _watchdog_instance = VoiceSystemsWatchdog()
        _watchdog_instance.start()
    return _watchdog_instance


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice Systems Watchdog")
    parser.add_argument("--start", action="store_true", help="Start watchdog")
    parser.add_argument("--stop", action="store_true", help="Stop watchdog")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--health", action="store_true", help="Show health report")

    args = parser.parse_args()

    watchdog = VoiceSystemsWatchdog()

    if args.start:
        watchdog.start()
        print("✅ Watchdog started")
        print("   Monitoring voice systems every 10 seconds")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            watchdog.stop()
            print("\n🛑 Watchdog stopped")

    elif args.stop:
        watchdog.stop()
        print("✅ Watchdog stopped")

    elif args.status:
        if watchdog.running:
            watchdog._log_health_status()
        else:
            print("⚠️  Watchdog is not running")

    elif args.health:
        report = watchdog.get_health_report()
        import json
        print(json.dumps(report, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":


    main()