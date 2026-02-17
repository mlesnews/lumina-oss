#!/usr/bin/env python3
"""
Human Activity Detector - REQUIRED

Detects when human is actively using mouse/keyboard.
Pauses automation when human is active - human takes precedence.

Tags: #HUMAN_ACTIVITY #AUTOMATION_PAUSE #HUMAN_PRECEDENCE #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from collections import deque
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HumanActivityDetector")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    keyboard = None

try:
    import mouse
    MOUSE_AVAILABLE = True
except ImportError:
    MOUSE_AVAILABLE = False
    mouse = None

if not (PYAUTOGUI_AVAILABLE and KEYBOARD_AVAILABLE and MOUSE_AVAILABLE):
    logger.warning("⚠️  Some libraries not available - install: pip install pyautogui keyboard mouse")


class HumanActivityDetector:
    """
    Detects human activity (mouse/keyboard usage)

    When human is active:
    - Pause all automation
    - Don't control mouse/keyboard
    - Human takes precedence

    When human stops:
    - Resume automation
    """

    def __init__(self):
        self.running = False

        # Activity tracking
        self.last_mouse_activity = None
        self.last_keyboard_activity = None
        self.mouse_activity_history = deque(maxlen=10)
        self.keyboard_activity_history = deque(maxlen=10)

        # Activity thresholds
        self.activity_timeout = 2.0  # 2 seconds of no activity = human stopped
        self.is_human_active = False

        # Callbacks for automation pause/resume
        self.on_human_active = None
        self.on_human_inactive = None

        # Automation state
        self.automation_paused = False

        if PYAUTOGUI_AVAILABLE and KEYBOARD_AVAILABLE and MOUSE_AVAILABLE:
            self._setup_hooks()

    def _setup_hooks(self):
        """Setup hooks to detect mouse/keyboard activity"""
        if not MOUSE_AVAILABLE or not KEYBOARD_AVAILABLE:
            logger.warning("⚠️  Mouse/keyboard libraries not available - using polling method")
            return False

        try:
            # Mouse activity hooks
            if MOUSE_AVAILABLE:
                mouse.on_move(self._on_mouse_move)
                mouse.on_click(self._on_mouse_click)
                mouse.on_scroll(self._on_mouse_scroll)

            # Keyboard activity hooks
            if KEYBOARD_AVAILABLE:
                keyboard.on_press(self._on_key_press)

            logger.info("✅ Human activity hooks set up")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup hooks: {e}")
            return False

    def _on_mouse_move(self, event):
        """Mouse moved - human is active"""
        self.last_mouse_activity = time.time()
        self.mouse_activity_history.append(self.last_mouse_activity)
        self._check_activity()

    def _on_mouse_click(self, event):
        """Mouse clicked - human is active"""
        self.last_mouse_activity = time.time()
        self.mouse_activity_history.append(self.last_mouse_activity)
        self._check_activity()

    def _on_mouse_scroll(self, event):
        """Mouse scrolled - human is active"""
        self.last_mouse_activity = time.time()
        self.mouse_activity_history.append(self.last_mouse_activity)
        self._check_activity()

    def _on_key_press(self, event):
        """Key pressed - human is active"""
        self.last_keyboard_activity = time.time()
        self.keyboard_activity_history.append(self.last_keyboard_activity)
        self._check_activity()

    def _check_activity(self):
        """Check if human is currently active"""
        current_time = time.time()

        # Check recent activity
        mouse_active = False
        keyboard_active = False

        if self.last_mouse_activity:
            time_since_mouse = current_time - self.last_mouse_activity
            if time_since_mouse < self.activity_timeout:
                mouse_active = True

        if self.last_keyboard_activity:
            time_since_keyboard = current_time - self.last_keyboard_activity
            if time_since_keyboard < self.activity_timeout:
                keyboard_active = True

        # FALLBACK: If hooks not available, use polling method
        if not MOUSE_AVAILABLE or not KEYBOARD_AVAILABLE:
            # Poll mouse/keyboard position to detect activity
            try:
                if PYAUTOGUI_AVAILABLE:
                    # Check if mouse moved (compare to last position)
                    current_mouse_pos = pyautogui.position()
                    if not hasattr(self, 'last_mouse_pos'):
                        self.last_mouse_pos = current_mouse_pos

                    if current_mouse_pos != self.last_mouse_pos:
                        self.last_mouse_activity = current_time
                        mouse_active = True
                        self.last_mouse_pos = current_mouse_pos
            except:
                pass

        # Human is active if EITHER mouse OR keyboard active
        human_active = mouse_active or keyboard_active

        # State change detection
        if human_active != self.is_human_active:
            self.is_human_active = human_active

            if human_active:
                # Human just became active - PAUSE automation
                logger.info("👤 Human activity detected - PAUSING automation")
                self._pause_automation()
            else:
                # Human just stopped - RESUME automation
                logger.info("⏸️  Human activity stopped - RESUMING automation")
                self._resume_automation()

    def _pause_automation(self):
        """Pause all automation - human takes precedence"""
        if not self.automation_paused:
            self.automation_paused = True

            # Notify callbacks
            if self.on_human_active:
                try:
                    self.on_human_active()
                except Exception as e:
                    logger.error(f"❌ Error in on_human_active callback: {e}")

            logger.info("⏸️  Automation paused - human has control")

    def _resume_automation(self):
        """Resume automation - human stopped"""
        if self.automation_paused:
            self.automation_paused = False

            # Notify callbacks
            if self.on_human_inactive:
                try:
                    self.on_human_inactive()
                except Exception as e:
                    logger.error(f"❌ Error in on_human_inactive callback: {e}")

            logger.info("▶️  Automation resumed - system has control")

    def is_automation_allowed(self) -> bool:
        """Check if automation is allowed (human not active)"""
        return not self.is_human_active

    def start(self):
        """Start human activity detection"""
        if not PYAUTOGUI_AVAILABLE or not KEYBOARD_AVAILABLE or not MOUSE_AVAILABLE:
            logger.error("❌ Required libraries not available")
            return False

        self.running = True

        def monitor_loop():
            while self.running:
                try:
                    self._check_activity()
                    time.sleep(0.5)  # Check every 0.5 seconds
                except Exception as e:
                    logger.error(f"❌ Monitor loop error: {e}")
                    time.sleep(1)

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info("✅ Human activity detector started")
        logger.info("   👤 Human takes precedence - automation pauses when human active")
        return True

    def stop(self):
        """Stop human activity detection"""
        self.running = False
        try:
            mouse.unhook_all()
            keyboard.unhook_all()
        except:
            pass
        logger.info("✅ Human activity detector stopped")


# Global instance
_human_detector = None


def get_human_detector() -> HumanActivityDetector:
    """Get global human activity detector instance"""
    global _human_detector
    if _human_detector is None:
        _human_detector = HumanActivityDetector()
    return _human_detector


def is_automation_allowed() -> bool:
    """Check if automation is allowed (human not active)"""
    detector = get_human_detector()
    return detector.is_automation_allowed()


def main():
    """Main function"""
    print("=" * 80)
    print("👤 HUMAN ACTIVITY DETECTOR")
    print("=" * 80)
    print()
    print("Purpose:")
    print("  - Detect when human is using mouse/keyboard")
    print("  - Pause automation when human is active")
    print("  - Resume automation when human stops")
    print("  - Human always takes precedence")
    print()

    detector = HumanActivityDetector()
    if detector.start():
        print("=" * 80)
        print("✅ HUMAN ACTIVITY DETECTION ACTIVE")
        print("=" * 80)
        print()
        print("Automation will pause when you use mouse/keyboard.")
        print("Press Ctrl+C to stop")
        print()

        try:
            while True:
                time.sleep(1)
                if detector.is_human_active:
                    print("👤 Human active - automation paused")
                else:
                    print("⏸️  Human inactive - automation active")
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
            detector.stop()


if __name__ == "__main__":


    main()