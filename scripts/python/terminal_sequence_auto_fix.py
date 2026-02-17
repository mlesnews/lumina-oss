#!/usr/bin/env python3
"""
Terminal Sequence Auto-Fix Monitor

Automatically monitors and fixes terminal sequence issues in the background.
Detects orange triangle warnings and re-initializes terminal automatically.

Tags: #TERMINAL #AUTO_FIX #MONITOR #SEQUENCE @JARVIS @LUMINA
"""

import sys
import os
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from terminal_sequence_manager import (
        get_terminal_manager,
        reinitialize_terminal,
        record_terminal_sequence
    )
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from terminal_sequence_manager import (
            get_terminal_manager,
            reinitialize_terminal,
            record_terminal_sequence
        )
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("TerminalSequenceAutoFix")

# Dynamic scaling for adaptive intervals and backoff
try:
    from dynamic_timeout_scaling import get_timeout_scaler, TimeoutConfig
    DYNAMIC_SCALING_AVAILABLE = True
except ImportError:
    DYNAMIC_SCALING_AVAILABLE = False
    get_timeout_scaler = None
    TimeoutConfig = None
    logger.debug("   Dynamic timeout scaling not available")

# Resource scaling (optional - may have import issues)
DynamicScalingModule = None
try:
    from lumina.dynamic_scaling import DynamicScalingModule
except (ImportError, SyntaxError):
    # Try alternative import path
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from dynamic_scaling import DynamicScalingModule
    except (ImportError, SyntaxError):
        DynamicScalingModule = None
        logger.debug("   Resource scaling module not available")


class TerminalSequenceAutoFix:
    """
    Automatically monitors and fixes terminal sequence issues.

    Runs in background and:
    - Monitors terminal sequence state
    - Detects out-of-order sequences
    - Automatically re-initializes terminal when needed
    - Prevents race conditions proactively
    """

    def __init__(self):
        """Initialize auto-fix monitor with dynamic scaling"""
        self.running = False
        self.monitor_thread = None

        # Dynamic scaling for adaptive intervals
        self.timeout_scaler = None
        self.resource_scaler = None
        if DYNAMIC_SCALING_AVAILABLE:
            try:
                self.timeout_scaler = get_timeout_scaler()
                # Configure terminal monitoring system
                terminal_config = TimeoutConfig(
                    base_timeout=5.0,  # Base 5 seconds
                    min_timeout=2.0,  # Minimum 2 seconds
                    max_timeout=30.0,  # Maximum 30 seconds
                    latency_multiplier=2.0,
                    adaptive_factor=1.2,
                    retry_backoff_base=1.5,
                    max_retries=3
                )
                self.timeout_scaler.configure_system("terminal_monitoring", terminal_config)
                logger.info("   ✅ Dynamic timeout scaling configured")
            except Exception as e:
                logger.debug(f"   Timeout scaler error: {e}")

            try:
                if DynamicScalingModule:
                    self.resource_scaler = DynamicScalingModule()
                    logger.info("   ✅ Resource scaling module initialized")
            except Exception as e:
                logger.debug(f"   Resource scaler error: {e}")

        # Adaptive check interval (starts at base, scales dynamically)
        self.base_check_interval = 5.0  # Base 5 seconds
        self.check_interval = self.base_check_interval
        self.min_check_interval = 2.0  # Never check more than every 2 seconds
        self.max_check_interval = 30.0  # Never check less than every 30 seconds

        self.last_fix_time = None
        self.min_fix_interval = 10.0  # Don't fix more than once per 10 seconds
        self.fix_count = 0
        self.last_status = None
        self.last_resource_check = None
        self.resource_check_interval = 10.0  # Check resources every 10 seconds

        logger.info("✅ Terminal Sequence Auto-Fix initialized with dynamic scaling")

    def start(self):
        """Start automatic monitoring and fixing"""
        if self.running:
            logger.warning("   Auto-fix monitor already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="TerminalSequenceAutoFix"
        )
        self.monitor_thread.start()
        logger.info("🚀 Terminal Sequence Auto-Fix monitor started")

    def stop(self):
        """Stop automatic monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("⏹️  Terminal Sequence Auto-Fix monitor stopped")

    def _monitor_loop(self):
        """Main monitoring loop with dynamic scaling"""
        logger.info("📡 Monitoring terminal sequences (auto-fix active with dynamic scaling)...")

        while self.running:
            try:
                # CRITICAL: Adjust check interval based on system load and workflow impact
                self._adjust_check_interval()

                # Get terminal manager
                manager = get_terminal_manager()

                # Get current status
                status = manager.get_status()
                self.last_status = status

                # Check if terminal needs fixing
                needs_fix = self._check_if_needs_fix(status)

                if needs_fix:
                    # Check if we've fixed recently (rate limiting)
                    if self._can_fix_now():
                        logger.warning("   ⚠️  Terminal sequence issue detected - handling notification...")
                        logger.warning("   🔔 This is likely the 'extensions want to relaunch terminal' notification")
                        success = self._auto_fix(manager, status)

                        if success:
                            self.fix_count += 1
                            self.last_fix_time = datetime.now()
                            logger.info("   ✅ Terminal notification handled successfully (fix #%d)", self.fix_count)
                            # Scale up check interval after successful fix (backoff)
                            self._scale_up_interval()
                        else:
                            logger.warning("   ⚠️  Notification handling failed - will retry")
                            # Scale down check interval after failure (more aggressive)
                            self._scale_down_interval()
                    else:
                        logger.debug("   ⏳ Rate limiting - skipping fix (recently fixed)")
                else:
                    logger.debug("   ✅ Terminal sequences OK")
                    # Gradually scale up interval when things are stable (backoff)
                    self._scale_up_interval()

                # Sleep with dynamically adjusted interval
                time.sleep(self.check_interval)

            except Exception as e:
                logger.error("   ❌ Error in monitor loop: %s", e)
                # On error, scale up interval to reduce impact
                self._scale_up_interval()
                time.sleep(self.check_interval)

    def _check_if_needs_fix(self, status: dict) -> bool:
        """
        Check if terminal needs fixing based on status.

        Args:
            status: Terminal status dictionary

        Returns:
            True if terminal needs fixing
        """
        # Check state - if out of order or error, definitely needs fix
        state = status.get('state', '')
        if state in ['out_of_order', 'error']:
            logger.warning("   ⚠️  Terminal in bad state: %s - needs restart", state)
            return True

        # Check if sequences are out of order
        recent_sequences = status.get('recent_sequences', [])
        expected_order = status.get('expected_order', [])

        if len(recent_sequences) >= 3:
            # Check if last 3 sequences match expected order
            last_three = recent_sequences[-3:]
            if last_three != expected_order:
                logger.warning(
                    "   ⚠️  Sequence mismatch detected: %s != %s - needs restart",
                    "→".join(last_three),
                    "→".join(expected_order)
                )
                return True

        # Check if terminal is not ready but should be
        if not status.get('ready', False) and state not in ['initializing', 'reinitializing']:
            # Terminal should be ready but isn't - needs restart
            logger.warning("   ⚠️  Terminal not ready - needs restart")
            return True

        return False

    def _can_fix_now(self) -> bool:
        """Check if we can fix now (rate limiting)"""
        if self.last_fix_time is None:
            return True

        time_since_last = (datetime.now() - self.last_fix_time).total_seconds()
        return time_since_last >= self.min_fix_interval

    def _auto_fix(self, manager, status: dict) -> bool:
        """
        Automatically fix terminal sequence issues.

        Args:
            manager: Terminal sequence manager
            status: Current status

        Returns:
            True if fix successful
        """
        try:
            logger.info("   🔄 Auto-fixing terminal sequences...")

            # CRITICAL: First try to handle Cursor IDE notification
            # This is the actual cause - extensions want to relaunch terminal
            try:
                from cursor_notification_handler import handle_terminal_relaunch_notification
                logger.info("   🔔 Handling terminal relaunch notification...")
                notification_handled = handle_terminal_relaunch_notification()
                if notification_handled:
                    logger.info("   ✅ Notification handled - terminal should relaunch")
                    time.sleep(2.0)  # Wait for terminal to relaunch
                    return True
            except ImportError:
                logger.debug("   Notification handler not available")
            except Exception as e:
                logger.debug("   Notification handling error: %s", e)

            # Try direct terminal restart (most reliable)
            try:
                from terminal_restart_direct import restart_terminal_direct
                restart_success = restart_terminal_direct()
                if restart_success:
                    logger.info("   ✅ Terminal restarted directly")
                    return True
            except ImportError:
                logger.debug("   Direct terminal restart not available")
            except Exception as e:
                logger.debug("   Direct restart error: %s", e)

            # Fallback: Try aggressive terminal restart
            try:
                from terminal_restart_manager import restart_terminal_aggressive
                restart_success = restart_terminal_aggressive()
                if restart_success:
                    logger.info("   ✅ Terminal restarted successfully")
                    return True
            except ImportError:
                logger.debug("   Terminal restart manager not available")
            except Exception as e:
                logger.debug("   Terminal restart error: %s", e)

            # Fallback: Send direct sequence reset
            try:
                from terminal_sequence_powershell_fix import send_sequence_reset
                send_sequence_reset()
                logger.info("   ✅ Direct sequence reset sent")
            except Exception as e:
                logger.debug("   Direct reset error: %s", e)

            # Re-initialize terminal
            success = reinitialize_terminal()

            if success:
                # Record proper sequence to establish correct order
                logger.debug("   📝 Recording proper sequence order...")
                try:
                    import os
                    record_terminal_sequence("A", process_id=os.getpid(), process_name="auto_fix")
                    time.sleep(0.1)
                    record_terminal_sequence("B", process_id=os.getpid(), process_name="auto_fix")
                    time.sleep(0.1)
                    record_terminal_sequence("P", process_id=os.getpid(), process_name="auto_fix")
                    logger.debug("   ✅ Proper sequence recorded")
                except Exception as e:
                    logger.debug("   ⚠️  Could not record sequence: %s", e)

                return True
            else:
                logger.warning("   ⚠️  Re-initialization failed")
                return False

        except Exception as e:
            logger.error("   ❌ Auto-fix error: %s", e)
            return False

    def _adjust_check_interval(self):
        """
        Dynamically adjust check interval based on system load and workflow impact.

        Uses dynamic scaling module to maintain system balance.
        """
        # Check resources periodically (not every loop to reduce overhead)
        now = datetime.now()
        if (self.last_resource_check is None or 
            (now - self.last_resource_check).total_seconds() >= self.resource_check_interval):

            self.last_resource_check = now

            if self.resource_scaler:
                try:
                    # Monitor resources
                    metrics = self.resource_scaler.monitor_resources()

                    # Calculate utilization
                    utilization = max(metrics.cpu_percent / 100, metrics.memory_percent / 100)

                    # Adjust interval based on utilization
                    # High utilization = longer interval (less frequent checks)
                    # Low utilization = shorter interval (more frequent checks)
                    if utilization > 0.75:
                        # High load - scale up interval (check less frequently)
                        new_interval = self.check_interval * 1.5
                        logger.debug("   📈 High system load (%.1f%%) - scaling up interval", utilization * 100)
                    elif utilization < 0.30:
                        # Low load - can check more frequently
                        new_interval = self.check_interval * 0.8
                        logger.debug("   📉 Low system load (%.1f%%) - scaling down interval", utilization * 100)
                    else:
                        # Normal load - maintain current interval
                        new_interval = self.check_interval

                    # Clamp to min/max
                    new_interval = max(self.min_check_interval, min(self.max_check_interval, new_interval))

                    if abs(new_interval - self.check_interval) > 0.5:
                        old_interval = self.check_interval
                        self.check_interval = new_interval
                        logger.info("   🔄 Check interval adjusted: %.1fs → %.1fs (utilization: %.1f%%)",
                                  old_interval, new_interval, utilization * 100)
                except Exception as e:
                    logger.debug(f"   Resource scaling error: {e}")

            # Also use timeout scaler if available
            if self.timeout_scaler:
                try:
                    # Get dynamic timeout for monitoring operation
                    dynamic_timeout = self.timeout_scaler.get_dynamic_timeout("terminal_monitoring", "check")
                    # Use timeout as basis for check interval (with some adjustment)
                    suggested_interval = dynamic_timeout * 0.3  # Check 3x more frequently than timeout
                    suggested_interval = max(self.min_check_interval, min(self.max_check_interval, suggested_interval))

                    if abs(suggested_interval - self.check_interval) > 1.0:
                        old_interval = self.check_interval
                        self.check_interval = suggested_interval
                        logger.debug("   ⏱️  Interval adjusted from timeout scaler: %.1fs → %.1fs",
                                   old_interval, suggested_interval)
                except Exception as e:
                    logger.debug(f"   Timeout scaler error: {e}")

    def _scale_up_interval(self):
        """Scale up check interval (backoff - check less frequently)"""
        if self.check_interval < self.max_check_interval:
            new_interval = min(self.max_check_interval, self.check_interval * 1.2)
            if abs(new_interval - self.check_interval) > 0.5:
                self.check_interval = new_interval
                logger.debug("   📈 Scaled up interval: %.1fs (backoff)", new_interval)

    def _scale_down_interval(self):
        """Scale down check interval (more aggressive - check more frequently)"""
        if self.check_interval > self.min_check_interval:
            new_interval = max(self.min_check_interval, self.check_interval * 0.8)
            if abs(new_interval - self.check_interval) > 0.5:
                self.check_interval = new_interval
                logger.debug("   📉 Scaled down interval: %.1fs (more aggressive)", new_interval)

    def get_stats(self) -> dict:
        """Get monitoring statistics"""
        stats = {
            "running": self.running,
            "fix_count": self.fix_count,
            "last_fix_time": self.last_fix_time.isoformat() if self.last_fix_time else None,
            "check_interval": self.check_interval,
            "base_check_interval": self.base_check_interval,
            "min_check_interval": self.min_check_interval,
            "max_check_interval": self.max_check_interval,
            "last_status": self.last_status
        }

        # Add resource metrics if available
        if self.resource_scaler:
            try:
                metrics = self.resource_scaler.monitor_resources()
                stats["system_resources"] = {
                    "cpu_percent": metrics.cpu_percent,
                    "memory_percent": metrics.memory_percent,
                    "utilization": max(metrics.cpu_percent, metrics.memory_percent) / 100
                }
            except Exception:
                pass

        return stats


# Global instance
_auto_fix_instance = None
_auto_fix_lock = threading.Lock()


def get_auto_fix_monitor() -> TerminalSequenceAutoFix:
    """Get or create global auto-fix monitor instance"""
    global _auto_fix_instance  # pylint: disable=global-statement

    with _auto_fix_lock:
        if _auto_fix_instance is None:
            _auto_fix_instance = TerminalSequenceAutoFix()
            # Auto-start monitoring
            _auto_fix_instance.start()
            logger.info("✅ Auto-fix monitor initialized and started")
        elif not _auto_fix_instance.running:
            # Restart if stopped
            _auto_fix_instance.start()
        return _auto_fix_instance


def start_auto_fix():
    """Start automatic terminal sequence fixing"""
    monitor = get_auto_fix_monitor()
    monitor.start()
    return monitor


def stop_auto_fix():
    """Stop automatic terminal sequence fixing"""
    global _auto_fix_instance  # pylint: disable=global-statement

    if _auto_fix_instance:
        _auto_fix_instance.stop()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Terminal Sequence Auto-Fix Monitor")
    parser.add_argument("--start", action="store_true", help="Start auto-fix monitor")
    parser.add_argument("--stop", action="store_true", help="Stop auto-fix monitor")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--check-interval", type=float, default=5.0, help="Check interval in seconds")

    args = parser.parse_args()

    if args.start:
        monitor = start_auto_fix()
        monitor.check_interval = args.check_interval
        logger.info("✅ Auto-fix monitor started")
        logger.info("   Check interval: %.1fs", monitor.check_interval)
        try:
            # Keep running
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping...")
            stop_auto_fix()

    elif args.stop:
        stop_auto_fix()
        logger.info("✅ Auto-fix monitor stopped")

    elif args.stats:
        monitor = get_auto_fix_monitor()
        stats = monitor.get_stats()
        print("\n📊 Auto-Fix Monitor Statistics:")
        print(f"   Running: {stats['running']}")
        print(f"   Fix count: {stats['fix_count']}")
        print(f"   Last fix: {stats['last_fix_time']}")
        print(f"\n📈 Dynamic Scaling:")
        print(f"   Current interval: {stats['check_interval']:.1f}s")
        print(f"   Base interval: {stats['base_check_interval']:.1f}s")
        print(f"   Min interval: {stats['min_check_interval']:.1f}s")
        print(f"   Max interval: {stats['max_check_interval']:.1f}s")
        if 'system_resources' in stats:
            resources = stats['system_resources']
            print(f"\n💻 System Resources:")
            print(f"   CPU: {resources['cpu_percent']:.1f}%")
            print(f"   Memory: {resources['memory_percent']:.1f}%")
            print(f"   Utilization: {resources['utilization']:.1%}")
        if stats['last_status']:
            status = stats['last_status']
            print(f"\n🔧 Terminal Status:")
            print(f"   State: {status.get('state', 'unknown')}")
            print(f"   Ready: {status.get('ready', False)}")
            print(f"   Recent sequences: {' → '.join(status.get('recent_sequences', []))}")

    else:
        # Default: start and keep running
        monitor = start_auto_fix()
        monitor.check_interval = args.check_interval
        logger.info("✅ Auto-fix monitor running in background")
        logger.info("   Use --stats to check status")
        logger.info("   Use --stop to stop")
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping...")
            stop_auto_fix()


if __name__ == "__main__":


    main()