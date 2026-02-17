#!/usr/bin/env python3
"""
Cursor IDE Auto-Send Monitor - Maintains Conversation Flow

Automatically sends messages in Cursor IDE after a pause (default: 10 seconds)
to keep the conversation flowing naturally without manual "Send" button clicks.

This maintains the flow of back-and-forth discussion and workflow execution.
"""

import logging
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

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

logger = get_logger("AutoSendMonitor")

# Optional import for full-time monitoring service
try:
    from full_time_monitoring_service import get_full_time_monitoring_service
except ImportError:
    get_full_time_monitoring_service = None

# Token usage tracking integration
try:
    from cursor_active_model_tracker import CursorActiveModelTracker
    from token_usage_monitor import TokenUsageMonitor
    HAS_TOKEN_TRACKING = True
except ImportError:
    HAS_TOKEN_TRACKING = False
    TokenUsageMonitor = None
    CursorActiveModelTracker = None

# JARVIS oversight integration
JARVIS_OVERSIGHT_AVAILABLE = False
get_jarvis_fulltime = None

try:
    from jarvis_fulltime_super_agent import get_jarvis_fulltime  # type: ignore
    JARVIS_OVERSIGHT_AVAILABLE = True
except ImportError:
    try:
        from jarvis_fulltime import get_jarvis_fulltime  # type: ignore
        JARVIS_OVERSIGHT_AVAILABLE = True
    except ImportError:
        JARVIS_OVERSIGHT_AVAILABLE = False
        get_jarvis_fulltime = None


@dataclass
class CursorAutoSendMonitor:
    """
    Monitors for pauses in conversation and auto-sends messages

    Maintains natural conversation flow by detecting when user has paused
    (stopped typing/speaking) and automatically sends the message.
    """
    pause_threshold: float = 5.0
    check_interval: float = 1.0
    enabled: bool = True

    def __post_init__(self):
        self.base_pause_threshold = self.pause_threshold
        self.running = False
        self.monitor_thread = None
        self.keyboard_hook_thread = None

        # Track last activity and speech patterns
        self.last_activity_time = None
        self.last_speech_end_time = None
        self.has_pending_message = False
        self.pending_transcript = None

        # CONTROL CONFLICT PREVENTION
        self.user_stopped = False
        self.stop_requested = False
        self.cancel_pending = False
        self.listening_mode = True

        self.f23_handler_setup = False

        # RALT @DOIT remapping (lazy-loaded)
        self._ralt_remap = None
        self._ralt_remap_started = False

        # Dynamic scaling parameters
        self.min_pause_threshold = 1.5
        self.max_pause_threshold = 10.0
        self.scaling_factor = 1.5
        self.consecutive_clips = 0
        self.speech_duration_history = []

        # Statistics
        self.stats = {
            "auto_sends": 0,
            "total_checks": 0,
            "pauses_detected": 0,
            "keyboard_events": 0,
            "dynamic_adjustments": 0,
            "clipping_detected": 0
        }

        # Token usage tracking
        self.token_monitor = None
        self.model_tracker = None
        if HAS_TOKEN_TRACKING:
            try:
                self.token_monitor = TokenUsageMonitor()
                self.model_tracker = CursorActiveModelTracker()
                logger.info("   ✅ Token usage tracking enabled")
            except (ImportError, AttributeError, ValueError) as e:
                logger.warning("   ⚠️  Token tracking unavailable: %s", e)

        # JARVIS oversight for automatic sends
        self.jarvis_oversight = None
        self.jarvis_oversight_enabled = True
        if JARVIS_OVERSIGHT_AVAILABLE:
            try:
                self.jarvis_oversight = get_jarvis_fulltime()
                logger.info("   ✅ JARVIS oversight enabled for auto-send")
            except (AttributeError, TypeError, RuntimeError, ImportError) as e:
                logger.warning("   ⚠️  JARVIS oversight unavailable: %s", e)
                self.jarvis_oversight_enabled = False
        else:
            logger.warning("   ⚠️  JARVIS oversight not available")
            self.jarvis_oversight_enabled = False

        logger.info("✅ Auto-Send Monitor initialized")
        logger.info("   Pause threshold: %ss", self.pause_threshold)
        logger.info("   Check interval: %ss", self.check_interval)
        logger.info("   Enabled: %s", self.enabled)

    def start(self):
        """Start the auto-send monitor"""
        if self.running:
            logger.warning("Monitor already running")
            return

        if not self.enabled:
            logger.info("Auto-send is disabled")
            return

        self.running = True

        # Start monitor thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="AutoSendMonitor"
        )
        self.monitor_thread.start()

        # Start keyboard hook
        self._start_keyboard_hook()

        # Setup F23 handler
        if not self.f23_handler_setup:
            self._setup_f23_handler()
            self.f23_handler_setup = True

        # Start RALT @DOIT remapping
        self._start_ralt_remap()

        logger.info("🚀 Auto-Send Monitor started")

    def stop_monitor(self):
        """Stop the auto-send monitor (internal)"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        if self.keyboard_hook_thread:
            self.keyboard_hook_thread.join(timeout=2.0)
        logger.info("⏹️  Auto-Send Monitor stopped")

    def _setup_f23_handler(self):
        """Setup F23 key handler"""
        try:
            import keyboard

            def on_f23_press(_event):
                logger.info("   🛑 F23 pressed - returning to listening mode")
                self.user_stopped = True
                self.stop_requested = True
                self.cancel_pending = True
                self.listening_mode = True
                self.has_pending_message = False
                self.last_activity_time = None
                self.last_speech_end_time = None
                logger.info("   ✅ Returned to listening mode")

            # Hook F23 key
            try:
                keyboard.on_press_key('f23', on_f23_press)
                logger.info("   ✅ F23 key handler installed (direct)")
            except (AttributeError, ValueError, RuntimeError):
                try:
                    keyboard.on_press_key(125, on_f23_press)
                    logger.info("   ✅ F23 key handler installed (scan code)")
                except (AttributeError, ValueError, RuntimeError):
                    try:
                        def check_f23(event):
                            is_f23 = (event.scan_code == 125 or
                                     event.name == 'f23' or
                                     (hasattr(event, 'name') and
                                      'f23' in str(event.name).lower()))
                            if is_f23:
                                on_f23_press(event)
                        keyboard.on_press(check_f23)
                        logger.info("   ✅ F23 key handler installed (scan check)")
                    except (AttributeError, ValueError, RuntimeError) as e2:
                        logger.warning("   ⚠️  Could not install F23 handler: %s", e2)
        except ImportError:
            logger.debug("   keyboard library not available")
        except (AttributeError, ValueError, RuntimeError) as e:
            logger.warning("   ⚠️  Could not install F23 handler: %s", e)

    def _start_ralt_remap(self):
        """Start RALT @DOIT remapping"""
        if self._ralt_remap_started:
            return

        try:
            from right_alt_doit_remap import RightAltDoitRemap
            self._ralt_remap = RightAltDoitRemap()
            if self._ralt_remap.start():
                self._ralt_remap_started = True
                logger.info("   ✅ RALT @DOIT remapping started")
            else:
                logger.warning("   ⚠️  RALT remapping failed to start")
        except ImportError:
            logger.debug("   RALT remap handler not available")
        except (AttributeError, TypeError, RuntimeError, OSError) as e:
            logger.warning("   ⚠️  Could not start RALT remapping: %s", e)

    def _start_keyboard_hook(self):
        """Start keyboard hook to detect activity"""
        try:
            import keyboard

            def on_key_press(event):
                if (event.name == 'f23' or
                    (hasattr(event, 'scan_code') and event.scan_code == 125)):
                    return

                # RIGHT ALT KEY - Allow through for @DOIT remapping
                # RALT should trigger @DOIT, not be filtered out
                # Check for both scan codes (54 and 56) as different systems use different codes
                is_right_alt = (
                    (hasattr(event, 'scan_code') and event.scan_code in [54, 56]) or
                    (hasattr(event, 'name') and event.name in [
                        'right alt', 'alt gr', 'altgr', 'right menu'
                    ])
                )

                if is_right_alt:
                    # RALT pressed - trigger @DOIT remapping
                    # Don't filter it out - let the RALT remap handler process it
                    logger.debug(
                        "   ⌨️  RALT detected (scan_code=%s, name=%s) - "
                        "allowing through for @DOIT remapping",
                        getattr(event, 'scan_code', 'N/A'),
                        getattr(event, 'name', 'N/A')
                    )
                    # Don't mark activity for RALT (it's a special key for @DOIT)
                    return

                if event.name not in [
                    'shift', 'ctrl', 'alt', 'cmd', 'meta',
                    'right alt', 'alt gr', 'altgr', 'right menu'
                ]:
                    self.mark_activity()
                    self.stats["keyboard_events"] += 1

            keyboard.on_press(on_key_press)
            logger.info("   ✅ Keyboard hook installed")
        except ImportError:
            logger.warning("   ⚠️  keyboard library not available")
        except (AttributeError, ValueError, RuntimeError) as e:
            logger.warning("   ⚠️  Could not install keyboard hook: %s", e)

    def stop(self):
        """Stop auto-send and cancel pending"""
        self.user_stopped = True
        self.stop_requested = True
        self.cancel_pending = True
        self.has_pending_message = False
        logger.info("   🛑 User stopped - cancelled pending messages")

    def cancel_pending_message(self):
        """Cancel pending message"""
        self.cancel_pending = True
        self.has_pending_message = False
        self.last_activity_time = None
        self.last_speech_end_time = None
        logger.info("   🛑 Pending message cancelled")

    def resume_listening(self):
        """Resume listening mode"""
        self.user_stopped = False
        self.stop_requested = False
        self.cancel_pending = False
        self.listening_mode = True
        logger.info("   ✅ Resumed listening mode")

    def mark_activity(self):
        """Mark user activity"""
        if self.user_stopped or self.stop_requested:
            return

        now = datetime.now()
        if self.last_activity_time:
            speech_duration = (now - self.last_activity_time).total_seconds()
            if speech_duration > 0.5:
                self.speech_duration_history.append(speech_duration)
                if len(self.speech_duration_history) > 10:
                    self.speech_duration_history.pop(0)

        self.last_activity_time = now
        self.has_pending_message = True
        self.user_stopped = False
        self.stop_requested = False
        self.cancel_pending = False
        logger.debug("Activity marked - resetting pause timer")

    def mark_speech_end(self):
        """Mark when speech ends"""
        self.last_speech_end_time = datetime.now()
        logger.debug("Speech end marked - starting dynamic wait timer")
        self._adjust_pause_threshold()

    def _adjust_pause_threshold(self):
        """Adjust pause threshold dynamically"""
        new_threshold = self.min_pause_threshold

        if self.consecutive_clips > 0:
            new_threshold = self.min_pause_threshold + (self.consecutive_clips * 1.5)
            logger.debug("   📈 Scaling up pause threshold: %.1fs", new_threshold)

        if self.speech_duration_history:
            avg_speech = (sum(self.speech_duration_history) /
                         len(self.speech_duration_history))
            speech_based = max(self.min_pause_threshold,
                              min(self.max_pause_threshold, avg_speech * 1.5))
            new_threshold = max(new_threshold, speech_based)

        new_threshold = max(self.min_pause_threshold,
                           min(self.max_pause_threshold, new_threshold))

        if abs(new_threshold - self.pause_threshold) > 0.5:
            old_threshold = self.pause_threshold
            self.pause_threshold = new_threshold
            self.stats["dynamic_adjustments"] += 1
            logger.info("   🔄 Adjusted: %.1fs → %.1fs", old_threshold, new_threshold)
        else:
            self.pause_threshold = new_threshold

    def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info("📡 Monitoring for pauses (dynamic scaling active)...")

        while self.running:
            try:
                self.stats["total_checks"] += 1

                if self.user_stopped or self.stop_requested or self.cancel_pending:
                    if self.cancel_pending:
                        self.has_pending_message = False
                        self.last_activity_time = None
                        self.last_speech_end_time = None
                        self.cancel_pending = False
                    time.sleep(self.check_interval)
                    continue

                if self.has_pending_message and self.last_activity_time:
                    now = datetime.now()
                    time_since_act = (now - self.last_activity_time).total_seconds()

                    time_since_speech_end = None
                    if self.last_speech_end_time:
                        time_since_speech_end = (now - self.last_speech_end_time).total_seconds()

                    # CRITICAL: Use speech_end_time if available (more accurate for voice)
                    # Otherwise fall back to activity_time
                    wait_time = (time_since_speech_end if time_since_speech_end is not None
                                else time_since_act)

                    if self.user_stopped or self.stop_requested or self.cancel_pending:
                        time.sleep(self.check_interval)
                        continue

                    # DEBUG: Log pause detection status
                    logger.debug(
                        "   ⏸️  Pause check: wait_time=%.1fs, threshold=%.1fs, "
                        "speech_end=%.1fs, activity=%.1fs",
                        wait_time, self.pause_threshold,
                        time_since_speech_end if time_since_speech_end else 0,
                        time_since_act
                    )

                    if wait_time >= self.pause_threshold:
                        is_clipping = (time_since_speech_end is not None and
                                      time_since_speech_end < 3.0 and
                                      self.pause_threshold < 5.0)
                        if is_clipping:
                            self.consecutive_clips += 1
                            self.stats["clipping_detected"] += 1
                            logger.warning("   ⚠️  Possible clipping detected (%.1fs)",
                                           time_since_speech_end)
                            self._adjust_pause_threshold()
                            time.sleep(self.check_interval)
                            continue

                        self.stats["pauses_detected"] += 1
                        logger.info("⏸️  Pause detected (%.1fs, threshold: %.1fs)",
                                    wait_time, self.pause_threshold)

                        # CRITICAL: If pending_transcript is set, it means text is already in
                        # chat field from voice transcript queue. We just need to send it
                        # (Enter key). If not set, this is keyboard input and text should
                        # already be in chat field.
                        if self.pending_transcript:
                            logger.debug(
                                "   ✅ Pending transcript found - text already in chat field "
                                "from voice queue"
                            )
                            # Clear pending transcript - we're about to send it
                            self.pending_transcript = None
                        else:
                            logger.debug(
                                "   ✅ No pending transcript - assuming text already in chat field "
                                "(keyboard input)"
                            )

                        # Send the message (Enter key) - text is already in chat field
                        self._auto_send()

                        # Reset state
                        self.has_pending_message = False
                        self.last_activity_time = None
                        self.last_speech_end_time = None
                        self.pending_transcript = None

                        logger.info("   ✅ Auto-send complete - message sent to CursorIDE")

                        if self.consecutive_clips > 0:
                            self.consecutive_clips = 0
                time.sleep(self.check_interval)
            except (AttributeError, RuntimeError) as e:
                logger.error("Error in monitor loop: %s", e)
                time.sleep(self.check_interval)

    def _type_transcript(self, transcript: str):
        """Type transcript into chat (fallback)"""
        try:
            import keyboard

            # FIXED: Removed ctrl+l to prevent layout switching
            # Assume chat is already focused, or user will focus it manually
            keyboard.write(transcript, delay=0.01)
            time.sleep(0.1)
            logger.debug("   ✅ Transcript typed (fallback)")
        except ImportError:
            logger.warning("keyboard not available")
        except (AttributeError, RuntimeError) as e:
            logger.error("   ❌ Failed to type transcript: %s", e)

    def _auto_send(self):
        """Automatically send the message with JARVIS oversight"""
        # JARVIS OVERSIGHT: Check with JARVIS before auto-sending
        if self.jarvis_oversight_enabled and self.jarvis_oversight:
            try:
                # Get pending message context (if available)
                message_context = {
                    "type": "auto_send",
                    "has_pending_transcript": self.pending_transcript is not None,
                    "pause_duration": self.pause_threshold,
                    "timestamp": datetime.now().isoformat()
                }

                # Request JARVIS approval for auto-send
                approval = self._request_jarvis_approval(message_context)

                if not approval:
                    logger.warning("   ⚠️  JARVIS did not approve auto-send - skipping")
                    self.has_pending_message = False
                    self.last_activity_time = None
                    self.last_speech_end_time = None
                    return

                logger.info("   ✅ JARVIS approved auto-send")
            except (AttributeError, TypeError, RuntimeError, ValueError) as e:
                logger.warning("   ⚠️  JARVIS oversight check failed: %s - proceeding anyway", e)

        # Proceed with auto-send
        try:
            import keyboard

            # FIXED: Removed ctrl+l and alt+l which were causing layout switching
            # Just send Enter key - text should already be in chat field
            # If chat is not focused, user can manually focus it
            keyboard.press_and_release('enter')
            self.stats["auto_sends"] += 1
            logger.info("✅ Message auto-sent (with JARVIS oversight)")
        except ImportError:
            logger.warning("keyboard not available - using alternative method")
            try:
                import win32api
                import win32con
                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                self.stats["auto_sends"] += 1
                logger.info("✅ Message auto-sent (Windows API, with JARVIS oversight)")
            except ImportError:
                logger.error("No keyboard automation available")

    def _request_jarvis_approval(self, context: dict) -> bool:
        """
        Request JARVIS approval for automatic send

        Args:
            context: Context about the pending message

        Returns:
            True if JARVIS approves, False otherwise
        """
        if not self.jarvis_oversight or not self.jarvis_oversight_enabled:
            return True  # Default to approve if JARVIS not available

        try:
            # Create approval request
            approval_request = {
                "action": "auto_send_message",
                "context": context,
                "request_type": "oversight_approval"
            }

            # Request approval from JARVIS
            # JARVIS will review and approve/reject based on context
            if hasattr(self.jarvis_oversight, 'approve_action'):
                result = self.jarvis_oversight.approve_action(approval_request)
                return result.get("approved", True)  # Default to approve if unclear
            elif hasattr(self.jarvis_oversight, 'process_request'):
                result = self.jarvis_oversight.process_request(approval_request)
                return result.get("approved", True)
            else:
                # JARVIS available but no approval method - log and approve
                logger.debug("   JARVIS available but no approval method - defaulting to approve")
                return True

        except (AttributeError, TypeError, RuntimeError, ValueError, KeyError) as e:
            logger.warning("   Error requesting JARVIS approval: %s - defaulting to approve", e)
            return True  # Default to approve on error

    def get_stats(self):
        """Get monitoring statistics"""
        stats = self.stats.copy()
        stats["running"] = self.running
        stats["enabled"] = self.enabled
        stats["monitor_alive"] = (self.monitor_thread.is_alive()
                                 if self.monitor_thread else False)
        if self.enabled and not self.running:
            self.start()
            stats["auto_restarted"] = True
        return stats

    def set_pause_threshold(self, seconds: float):
        """Update pause threshold"""
        self.pause_threshold = max(1.0, seconds)
        logger.info("✅ Pause threshold updated to %.1fs", self.pause_threshold)

    def enable(self, enabled: bool = True):
        """Enable or disable auto-send"""
        self.enabled = enabled
        if enabled and not self.running:
            self.start()
        elif not enabled and self.running:
            self.stop_monitor()
        logger.info("✅ Auto-send %s", "enabled" if enabled else "disabled")


# Global instance
_monitor_instance = None


def get_auto_send_monitor() -> CursorAutoSendMonitor:
    """Get or create global auto-send monitor instance"""
    global _monitor_instance  # pylint: disable=global-statement
    if _monitor_instance is None:
        _monitor_instance = CursorAutoSendMonitor()
        if _monitor_instance.enabled:
            _monitor_instance.start()
            logger.info("✅ Auto-send monitor initialized and ACTIVE")
            _start_full_time_monitoring()
    else:
        if _monitor_instance.enabled and not _monitor_instance.running:
            _monitor_instance.start()
        if (_monitor_instance.monitor_thread and
            not _monitor_instance.monitor_thread.is_alive()):
            _monitor_instance.start()
    return _monitor_instance


def _start_full_time_monitoring():
    """Start full-time monitoring service (@mdv)"""
    if get_full_time_monitoring_service is None:
        logger.debug("   Full-time monitoring not available")
        return

    try:
        get_full_time_monitoring_service()
        logger.debug("   ✅ Full-time monitoring active")
    except (AttributeError, TypeError, ValueError) as e:
        logger.debug("   Could not start full-time monitoring: %s", e)


def start_auto_send(pause_threshold: float = 10.0):
    """Start auto-send monitoring"""
    monitor = get_auto_send_monitor()
    monitor.set_pause_threshold(pause_threshold)
    monitor.start()
    return monitor


def stop_auto_send():
    """Stop auto-send and cancel pending"""
    monitor = get_auto_send_monitor()
    monitor.stop()
    monitor.cancel_pending_message()


def stop_monitor():
    """Stop auto-send monitoring thread"""
    if _monitor_instance:
        _monitor_instance.stop_monitor()


def mark_activity():
    """Mark user activity"""
    monitor = get_auto_send_monitor()
    monitor.mark_activity()


def mark_speech_end():
    """Mark when speech input ends"""
    monitor = get_auto_send_monitor()
    monitor.mark_speech_end()


def resume_listening():
    """Resume listening mode"""
    monitor = get_auto_send_monitor()
    monitor.resume_listening()


def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Cursor IDE Auto-Send Monitor")
    parser.add_argument("--pause-threshold", type=float, default=10.0)
    parser.add_argument("--check-interval", type=float, default=1.0)
    parser.add_argument("--disable", action="store_true")
    args = parser.parse_args()

    mon = CursorAutoSendMonitor(
        pause_threshold=args.pause_threshold,
        check_interval=args.check_interval,
        enabled=not args.disable
    )

    if not args.disable:
        mon.start()
        logger.info("✅ Auto-Send Monitor running")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping...")
            mon.stop()
    else:
        logger.info("Auto-send is disabled")


if __name__ == "__main__":


    main()