#!/usr/bin/env python3
"""
JARVIS Auto-Accept Monitor - Fully Automatic

Monitors for "Accept All Changes" dialogs and automatically accepts them
WITHOUT requiring any clicks or hotkeys.
"""

import sys
import time
import threading
import psutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAutoAcceptMonitor")


def check_singleton() -> bool:
    """
    CRITICAL: Singleton check to prevent multiple instances.
    This prevents the system freeze issue (see MEMORY_CRITICAL_SYSTEM_FREEZE_PREVENTION.md)
    """
    script_name = "jarvis_auto_accept_monitor.py"
    count = 0

    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline') or []
                    cmdline_str = ' '.join(cmdline).lower()
                    if script_name.lower() in cmdline_str:
                        count += 1
                        if count > 1:  # More than 1 means another instance is running
                            logger.error(f"❌ CRITICAL: Another instance of {script_name} is already running!")
                            logger.error(f"   Found {count} instances. This can cause system freeze.")
                            logger.error(f"   Exiting to prevent process proliferation.")
                            return False
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        if count == 1:
            logger.info(f"✅ Singleton check passed (this is the only instance)")
        return True

    except Exception as e:
        logger.error(f"❌ Singleton check failed: {e}")
        # Fail safe: exit if we can't verify singleton
        logger.error("   Exiting to prevent potential system freeze.")
        return False

try:
    import pyautogui
    import keyboard
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False
    pyautogui = None
    keyboard = None
    print("❌ Missing dependencies. Install: pip install pyautogui keyboard")

logger = get_logger("JARVISAutoAcceptMonitor")


class JARVISAutoAcceptMonitor:
    """
    Fully automatic monitor for "Accept All Changes" dialogs

    Continuously monitors screen and automatically accepts dialogs
    """

    def __init__(self):
        self.running = False
        self.monitor_thread = None

        if AUTOMATION_AVAILABLE:
            pyautogui.PAUSE = 0.1
            pyautogui.FAILSAFE = True
            self.logger = logger
        else:
            self.logger = logger
            self.logger.error("Automation libraries not available")

    def _detect_accept_dialog(self) -> bool:
        """Detect if 'Accept All Changes' dialog is visible using VLM"""
        if not AUTOMATION_AVAILABLE:
            return False

        try:
            # Use VLM to detect dialog
            try:
                from vlm_integration import VLMIntegration
                from screen_capture_system import ScreenCaptureSystem

                # Capture screen
                capture = ScreenCaptureSystem()
                screenshot_path = capture.capture_screenshot()

                # Use VLM to analyze
                vlm = VLMIntegration(use_vlm=True, vlm_provider="local", vlm_model="Qwen/Qwen2-VL-2B-Instruct")
                prompt = "Is there a button that says 'Keep All' or 'Accept All Changes' or 'Accept All' visible on this screen? The button may say 'Keep All' but it's the accept button. Answer YES or NO only."

                result = vlm.analyze_screen_with_vlm(screenshot_path, prompt=prompt)

                # VLM returns dict with 'analysis' or 'text' key
                if result and isinstance(result, dict):
                    analysis_text = result.get('analysis', result.get('text', result.get('response', '')))
                    if analysis_text and ("YES" in str(analysis_text).upper() or "yes" in str(analysis_text).lower()):
                        self.logger.info("✅ VLM detected 'Accept All' dialog")
                        return True
                    else:
                        return False
                elif result and isinstance(result, str):
                    if "YES" in result.upper() or "yes" in result.lower():
                        self.logger.info("✅ VLM detected 'Accept All' dialog")
                        return True
                    else:
                        return False
            except ImportError:
                self.logger.debug("VLM not available for dialog detection")
            except Exception as e:
                self.logger.debug(f"VLM detection error: {e}")

            # Fallback: Check for common dialog button positions
            screen_width, screen_height = pyautogui.size()

            # Common button positions
            button_positions = [
                (screen_width * 0.85, screen_height * 0.85),  # Bottom right
                (screen_width * 0.75, screen_height * 0.85),  # Bottom right-center
            ]

            return False  # Simplified - VLM is primary method

        except Exception as e:
            self.logger.debug(f"Dialog detection error: {e}")
            return False

    def _auto_accept(self):
        """Automatically accept dialog - uses MANUS to find and click button"""
        if not AUTOMATION_AVAILABLE:
            return False

        self.logger.info("🔧 Auto-accepting dialog...")

        # Method 1: Use MANUS to find and click button (BEST)
        try:
            from manus_accept_all_button import MANUSAcceptAllButton
            manus_automator = MANUSAcceptAllButton()
            if manus_automator.accept_all_changes():
                self.logger.info("✅ Auto-accepted via MANUS")
                return True
        except Exception as e:
            self.logger.debug(f"MANUS auto-accept failed: {e}")

        # Method 2: Try keyboard shortcuts
        shortcuts = [
            ('enter',),
            ('alt', 'a'),
            ('ctrl', 'shift', 'a'),
            ('tab',),  # Tab to button, then Enter
        ]

        for shortcut in shortcuts:
            try:
                if len(shortcut) == 1:
                    keyboard.press_and_release(shortcut[0])
                else:
                    keyboard.press_and_release('+'.join(shortcut))
                time.sleep(0.5)
                self.logger.info(f"✅ Sent shortcut: {'+'.join(shortcut)}")
                return True
            except Exception as e:
                self.logger.debug(f"Shortcut {shortcut} failed: {e}")

        # Method 3: Try common button positions
        try:
            screen_width, screen_height = pyautogui.size()
            common_positions = [
                (screen_width * 0.85, screen_height * 0.85),  # Bottom right
                (screen_width * 0.75, screen_height * 0.85),  # Bottom right-center
                (screen_width * 0.9, screen_height * 0.9),     # Very bottom right
            ]

            for x, y in common_positions:
                try:
                    pyautogui.click(x, y)
                    time.sleep(0.5)
                    self.logger.info(f"✅ Clicked position ({x}, {y})")
                    return True
                except Exception as e:
                    self.logger.debug(f"Click at ({x}, {y}) failed: {e}")
        except Exception as e:
            self.logger.debug(f"Position clicking failed: {e}")

        self.logger.warning("⚠️  All auto-accept methods failed")
        return False

    def _monitor_loop(self):
        """Main monitoring loop - uses VLM to detect dialogs"""
        self.logger.info("👀 Monitoring for 'Accept All Changes' dialogs...")
        self.logger.info("   Using VLM for visual detection")
        self.logger.info("   Will auto-accept when detected")

        last_check = time.time()
        check_interval = 2.0  # Check every 2 seconds (VLM takes time)
        last_accept_time = 0
        accept_cooldown = 5.0  # Don't accept again for 5 seconds after last accept

        # Track consecutive failures for debugging
        consecutive_failures = 0
        max_failures = 5

        while self.running:
            try:
                current_time = time.time()

                # Check if enough time has passed
                if current_time - last_check >= check_interval:
                    # Check cooldown
                    if current_time - last_accept_time < accept_cooldown:
                        last_check = current_time
                        time.sleep(0.1)
                        continue

                    # Detect dialog using VLM
                    try:
                        dialog_detected = self._detect_accept_dialog()
                        if dialog_detected:
                            self.logger.info("🔧 Dialog detected - auto-accepting...")
                            if self._auto_accept():
                                last_accept_time = current_time
                                consecutive_failures = 0
                                self.logger.info("✅ Auto-accepted successfully")
                            else:
                                consecutive_failures += 1
                                self.logger.warning(f"⚠️  Auto-accept failed (attempt {consecutive_failures}/{max_failures})")
                        else:
                            # Reset failure counter if no dialog (not a failure)
                            if consecutive_failures > 0:
                                consecutive_failures = 0
                    except Exception as detect_error:
                        consecutive_failures += 1
                        self.logger.error(f"❌ Detection error: {detect_error}")
                        if consecutive_failures >= max_failures:
                            self.logger.error(f"❌ Too many failures ({consecutive_failures}), check VLM/system status")
                            consecutive_failures = 0  # Reset after warning

                    last_check = current_time

                time.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(1)

    def start(self):
        """Start automatic monitoring"""
        if not AUTOMATION_AVAILABLE:
            self.logger.error("❌ Automation not available")
            return False

        if self.running:
            self.logger.warning("⚠️  Already running")
            return True

        self.running = True

        # Register global hotkey as backup
        keyboard.add_hotkey('ctrl+shift+a', self._auto_accept)
        keyboard.add_hotkey('ctrl+shift+k', self._auto_accept)

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info("✅ Auto-accept monitor started")
        self.logger.info("   Monitoring continuously")
        self.logger.info("   Hotkeys: Ctrl+Shift+A, Ctrl+Shift+K (backup)")

        return True

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.logger.info("👋 Auto-accept monitor stopped")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Auto-Accept Monitor")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--background", action="store_true", help="Run in background mode")

    args = parser.parse_args()

    # CRITICAL: Check singleton before starting (prevents system freeze)
    if not check_singleton():
        logger.error("❌ Cannot start: Another instance is already running")
        logger.error("   This prevents system freeze from process proliferation")
        sys.exit(1)

    monitor = JARVISAutoAcceptMonitor()

    if args.background:
        # Background mode - start and keep running without interactive prompts
        monitor.start()
        try:
            # Keep running indefinitely
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop()
    elif args.start or not args:
        print("="*80)
        print("🤖 JARVIS Auto-Accept Monitor")
        print("="*80)
        print()
        print("✅ Monitoring for 'Accept All Changes' dialogs")
        print("   Will automatically accept when detected")
        print()
        print("Press Ctrl+C to stop")
        print("-"*80)
        print()

        monitor.start()

        try:
            keyboard.wait('ctrl+c')
        except KeyboardInterrupt:
            pass

        monitor.stop()


if __name__ == "__main__":


    main()