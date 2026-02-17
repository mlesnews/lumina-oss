#!/usr/bin/env python3
"""
JARVIS Voice System Watchdog - Auto-Start & Monitor

Automatically starts and monitors all voice system components:
- Voice Interface System (voice_interface_system.py)
- Auto-Send Monitor (cursor_auto_send_monitor.py)
- Voice Transcript Queue (voice_transcript_queue.py)

Features:
- Auto-start all components on launch
- Watchdog monitoring with automatic restart on failure
- Health checks and status reporting
- Graceful shutdown handling
- Logging and error reporting
"""

import logging
import signal
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

# Setup paths for lumina_core
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        logging.basicConfig(level=logging.INFO)

        def get_logger(name):
            """Fallback logger factory"""
            return logging.getLogger(name)

logger = get_logger("VoiceWatchdog")


@dataclass
class ComponentStatus:
    """Status of a monitored component"""
    name: str
    running: bool = False
    last_start_time: Optional[datetime] = None
    restart_count: int = 0
    last_error: Optional[str] = None
    health_check_passed: bool = False


class VoiceSystemWatchdog:
    """
    Watchdog for JARVIS voice system components

    Monitors and auto-restarts:
    - Voice Interface System
    - Auto-Send Monitor
    - Voice Transcript Queue
    """

    def __init__(self):
        self.running = False
        self.components = {
            "voice_interface": ComponentStatus("Voice Interface System"),
            "auto_send_monitor": ComponentStatus("Auto-Send Monitor"),
            "transcript_queue": ComponentStatus("Voice Transcript Queue"),
        }
        self.monitor_thread: Optional[threading.Thread] = None
        self.health_check_interval = 5.0  # Check every 5 seconds
        self.restart_delay = 2.0  # Wait 2 seconds before restarting
        self.shutdown_event = threading.Event()

    def start(self) -> bool:
        """Start the watchdog and all components"""
        if self.running:
            logger.warning("Watchdog already running")
            return False

        logger.info("=" * 70)
        logger.info("🚀 JARVIS Voice System Watchdog Starting")
        logger.info("=" * 70)

        self.running = True
        self.shutdown_event.clear()

        # Start all components
        self._start_all_components()

        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()

        logger.info("✅ Watchdog started - monitoring all voice components")
        logger.info("   Press Ctrl+C to stop")

        return True

    def stop(self):
        """Stop the watchdog and all components"""
        if not self.running:
            return

        logger.info("🛑 Stopping JARVIS Voice System Watchdog...")
        self.running = False
        self.shutdown_event.set()

        # Stop all components
        self._stop_all_components()

        # Wait for monitor thread
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)

        logger.info("✅ Watchdog stopped")

    def _start_all_components(self):
        """Start all voice system components"""
        logger.info("📦 Starting voice system components...")

        # 1. Start Auto-Send Monitor (needed by transcript queue)
        self._start_auto_send_monitor()
        time.sleep(1.0)  # Give it time to initialize

        # 2. Start Voice Transcript Queue (needed by voice interface)
        self._start_transcript_queue()
        time.sleep(1.0)  # Give it time to initialize

        # 3. Start Voice Interface System
        self._start_voice_interface()

        logger.info("✅ All components started")
        self._print_status()

    def _stop_all_components(self):
        """Stop all voice system components"""
        logger.info("🛑 Stopping voice system components...")

        # Stop in reverse order
        self._stop_voice_interface()
        time.sleep(0.5)

        self._stop_transcript_queue()
        time.sleep(0.5)

        self._stop_auto_send_monitor()

        logger.info("✅ All components stopped")

    def _start_voice_interface(self):
        """Start Voice Interface System"""
        try:
            from voice_interface_system import get_voice_interface

            # get_voice_interface() creates the instance, which auto-starts listening in __init__
            # So we just need to check if it's running, not call start_listening() again
            voice = get_voice_interface()

            # Verify it's actually listening (auto-start should have done this)
            if voice.listening_active:
                self.components["voice_interface"].running = True
                self.components["voice_interface"].last_start_time = datetime.now()
                self.components["voice_interface"].last_error = None
                logger.info("   ✅ Voice Interface System started (auto-started on init)")
            else:
                # Fallback: if auto-start didn't work, try manual start
                logger.warning("   ⚠️  Auto-start didn't work, trying manual start")
                if voice.start_listening():
                    self.components["voice_interface"].running = True
                    self.components["voice_interface"].last_start_time = datetime.now()
                    self.components["voice_interface"].last_error = None
                    logger.info("   ✅ Voice Interface System started (manual start)")
                else:
                    raise RuntimeError("Failed to start listening")
        except Exception as e:
            self.components["voice_interface"].running = False
            self.components["voice_interface"].last_error = str(e)
            logger.error(f"   ❌ Failed to start Voice Interface: {e}")

    def _stop_voice_interface(self):
        """Stop Voice Interface System"""
        try:
            from voice_interface_system import get_voice_interface

            voice = get_voice_interface()
            voice.stop_listening()
            self.components["voice_interface"].running = False
            logger.info("   ✅ Voice Interface System stopped")
        except Exception as e:
            logger.warning(f"   ⚠️  Error stopping Voice Interface: {e}")

    def _start_auto_send_monitor(self):
        """Start Auto-Send Monitor"""
        try:
            from cursor_auto_send_monitor import get_auto_send_monitor

            monitor = get_auto_send_monitor()
            if monitor.start():
                self.components["auto_send_monitor"].running = True
                self.components["auto_send_monitor"].last_start_time = datetime.now()
                self.components["auto_send_monitor"].last_error = None
                logger.info("   ✅ Auto-Send Monitor started")
            else:
                raise RuntimeError("Failed to start monitor")
        except Exception as e:
            self.components["auto_send_monitor"].running = False
            self.components["auto_send_monitor"].last_error = str(e)
            logger.error(f"   ❌ Failed to start Auto-Send Monitor: {e}")

    def _stop_auto_send_monitor(self):
        """Stop Auto-Send Monitor"""
        try:
            from cursor_auto_send_monitor import get_auto_send_monitor

            monitor = get_auto_send_monitor()
            monitor.stop()
            self.components["auto_send_monitor"].running = False
            logger.info("   ✅ Auto-Send Monitor stopped")
        except Exception as e:
            logger.warning(f"   ⚠️  Error stopping Auto-Send Monitor: {e}")

    def _start_transcript_queue(self):
        """Start Voice Transcript Queue"""
        try:
            from voice_transcript_queue import get_voice_transcript_queue

            queue = get_voice_transcript_queue()
            queue.start()
            self.components["transcript_queue"].running = True
            self.components["transcript_queue"].last_start_time = datetime.now()
            self.components["transcript_queue"].last_error = None
            logger.info("   ✅ Voice Transcript Queue started")
        except Exception as e:
            self.components["transcript_queue"].running = False
            self.components["transcript_queue"].last_error = str(e)
            logger.error(f"   ❌ Failed to start Transcript Queue: {e}")

    def _stop_transcript_queue(self):
        """Stop Voice Transcript Queue"""
        try:
            from voice_transcript_queue import get_voice_transcript_queue

            queue = get_voice_transcript_queue()
            queue.stop()
            self.components["transcript_queue"].running = False
            logger.info("   ✅ Voice Transcript Queue stopped")
        except Exception as e:
            logger.warning(f"   ⚠️  Error stopping Transcript Queue: {e}")

    def _monitor_loop(self):
        """Main monitoring loop - checks component health and restarts if needed"""
        logger.info("👁️  Watchdog monitoring started")

        while self.running and not self.shutdown_event.is_set():
            try:
                # Check each component
                self._check_voice_interface()
                self._check_auto_send_monitor()
                self._check_transcript_queue()

                # Wait before next check
                self.shutdown_event.wait(self.health_check_interval)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(self.health_check_interval)

        logger.info("👁️  Watchdog monitoring stopped")

    def _check_voice_interface(self):
        """Check Voice Interface health and restart if needed"""
        try:
            from voice_interface_system import get_voice_interface

            voice = get_voice_interface()
            is_running = voice.listening_active

            if not is_running and self.components["voice_interface"].running:
                # Component was running but stopped
                logger.warning("   ⚠️  Voice Interface stopped unexpectedly - restarting...")
                self._restart_voice_interface()
            elif is_running:
                self.components["voice_interface"].health_check_passed = True
                self.components["voice_interface"].last_error = None
        except Exception as e:
            if self.components["voice_interface"].running:
                logger.warning(f"   ⚠️  Voice Interface health check failed: {e}")
                self.components["voice_interface"].health_check_passed = False
                self.components["voice_interface"].last_error = str(e)
                self._restart_voice_interface()

    def _check_auto_send_monitor(self):
        """Check Auto-Send Monitor health and restart if needed"""
        try:
            from cursor_auto_send_monitor import get_auto_send_monitor

            monitor = get_auto_send_monitor()
            is_running = monitor.running

            if not is_running and self.components["auto_send_monitor"].running:
                # Component was running but stopped
                logger.warning("   ⚠️  Auto-Send Monitor stopped unexpectedly - restarting...")
                self._restart_auto_send_monitor()
            elif is_running:
                self.components["auto_send_monitor"].health_check_passed = True
                self.components["auto_send_monitor"].last_error = None
        except Exception as e:
            if self.components["auto_send_monitor"].running:
                logger.warning(f"   ⚠️  Auto-Send Monitor health check failed: {e}")
                self.components["auto_send_monitor"].health_check_passed = False
                self.components["auto_send_monitor"].last_error = str(e)
                self._restart_auto_send_monitor()

    def _check_transcript_queue(self):
        """Check Transcript Queue health and restart if needed"""
        try:
            from voice_transcript_queue import get_voice_transcript_queue

            queue = get_voice_transcript_queue()
            is_running = queue.processing

            if not is_running and self.components["transcript_queue"].running:
                # Component was running but stopped
                logger.warning("   ⚠️  Transcript Queue stopped unexpectedly - restarting...")
                self._restart_transcript_queue()
            elif is_running:
                self.components["transcript_queue"].health_check_passed = True
                self.components["transcript_queue"].last_error = None
        except Exception as e:
            if self.components["transcript_queue"].running:
                logger.warning(f"   ⚠️  Transcript Queue health check failed: {e}")
                self.components["transcript_queue"].health_check_passed = False
                self.components["transcript_queue"].last_error = str(e)
                self._restart_transcript_queue()

    def _restart_voice_interface(self):
        """Restart Voice Interface System"""
        logger.info("   🔄 Restarting Voice Interface System...")
        self.components["voice_interface"].restart_count += 1

        # Stop first
        self._stop_voice_interface()
        time.sleep(self.restart_delay)

        # Start again
        self._start_voice_interface()

    def _restart_auto_send_monitor(self):
        """Restart Auto-Send Monitor"""
        logger.info("   🔄 Restarting Auto-Send Monitor...")
        self.components["auto_send_monitor"].restart_count += 1

        # Stop first
        self._stop_auto_send_monitor()
        time.sleep(self.restart_delay)

        # Start again
        self._start_auto_send_monitor()

    def _restart_transcript_queue(self):
        """Restart Voice Transcript Queue"""
        logger.info("   🔄 Restarting Transcript Queue...")
        self.components["transcript_queue"].restart_count += 1

        # Stop first
        self._stop_transcript_queue()
        time.sleep(self.restart_delay)

        # Start again
        self._start_transcript_queue()

    def _print_status(self):
        """Print status of all components"""
        logger.info("")
        logger.info("📊 Component Status:")
        logger.info("-" * 70)

        for key, status in self.components.items():
            status_icon = "✅" if status.running else "❌"
            health_icon = "💚" if status.health_check_passed else "💔"
            restart_info = f" (restarted {status.restart_count}x)" if status.restart_count > 0 else ""

            logger.info(f"   {status_icon} {status.name}: {'RUNNING' if status.running else 'STOPPED'}")
            logger.info(f"      Health: {health_icon} {'OK' if status.health_check_passed else 'FAILED'}{restart_info}")

            if status.last_error:
                logger.info(f"      Last Error: {status.last_error}")

            if status.last_start_time:
                uptime = (datetime.now() - status.last_start_time).total_seconds()
                logger.info(f"      Uptime: {uptime:.1f}s")

        logger.info("-" * 70)
        logger.info("")

    def get_status(self) -> dict:
        """Get status of all components"""
        return {
            "watchdog_running": self.running,
            "components": {
                key: {
                    "name": status.name,
                    "running": status.running,
                    "restart_count": status.restart_count,
                    "health_check_passed": status.health_check_passed,
                    "last_error": status.last_error,
                    "last_start_time": status.last_start_time.isoformat() if status.last_start_time else None,
                }
                for key, status in self.components.items()
            }
        }


# Global watchdog instance
_watchdog_instance: Optional[VoiceSystemWatchdog] = None


def get_voice_watchdog() -> VoiceSystemWatchdog:
    """Get or create watchdog instance"""
    global _watchdog_instance
    if _watchdog_instance is None:
        _watchdog_instance = VoiceSystemWatchdog()
    return _watchdog_instance


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("")
    logger.info("🛑 Shutdown signal received")
    watchdog = get_voice_watchdog()
    watchdog.stop()
    sys.exit(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Voice System Watchdog")
    parser.add_argument("--start", action="store_true", help="Start watchdog and all components")
    parser.add_argument("--stop", action="store_true", help="Stop watchdog and all components")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    watchdog = get_voice_watchdog()

    if args.start:
        if watchdog.start():
            try:
                # Keep running
                while watchdog.running:
                    time.sleep(1.0)
                    # Print status every 60 seconds
                    if int(time.time()) % 60 == 0:
                        watchdog._print_status()
            except KeyboardInterrupt:
                watchdog.stop()

    elif args.stop:
        watchdog.stop()

    elif args.status:
        status = watchdog.get_status()
        if args.json:
            import json
            print(json.dumps(status, indent=2))
        else:
            watchdog._print_status()

    else:
        parser.print_help()
        print("\n🎤 JARVIS Voice System Watchdog")
        print("   Automatically starts and monitors all voice components")
        print("\nUsage:")
        print("   python jarvis_voice_watchdog.py --start    # Start watchdog")
        print("   python jarvis_voice_watchdog.py --status   # Check status")
        print("   python jarvis_voice_watchdog.py --stop     # Stop watchdog")
