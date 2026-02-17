#!/usr/bin/env python3
"""
Cursor IDE Auto-Accept Changes

Automatically accepts "Keep All" / "Accept Changes" in Cursor IDE using #DECISIONING.
No manual clicking required - fully automated.

Tags: #CURSOR_IDE #AUTOMATION #DECISIONING #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger
from lumina_decisioning_engine import LuminaDecisioningEngine, DecisionContext

logger = get_adaptive_logger("CursorAutoAccept")


class CursorIDEAutoAccept:
    """
    Automatically accept changes in Cursor IDE

    Uses UI automation to click "Keep All" / "Accept Changes" buttons
    when detected, using #DECISIONING workflow.

    FEEDBACK LOOP: Tracks state to prevent infinite loops.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize auto-accept system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.decisioning_engine = LuminaDecisioningEngine(project_root)

        # FEEDBACK LOOP: State tracking to prevent infinite loops
        self.last_acceptance_time = None
        self.last_acceptance_hash = None  # Hash of what was accepted
        self.acceptance_cooldown = 3.0  # Seconds - prevent re-triggering for 3 seconds
        self.acceptance_count = 0
        self.max_acceptances_per_minute = 10  # Safety limit

        # PERIODIC REFRESH: Track refresh state
        self.last_refresh_time = None
        self.refresh_interval = 30.0  # Refresh window connection every 30 seconds
        self.cached_app = None  # Cache window connection

        # UI automation
        try:
            import pyautogui
            import pywinauto
            self.pyautogui = pyautogui
            self.pywinauto = pywinauto
            self.ui_available = True
        except ImportError:
            logger.warning("   ⚠️  pyautogui/pywinauto not available - install with: pip install pyautogui pywinauto")
            self.ui_available = False

        # MANUS integration (primary control method)
        self.manus_available = False
        self.manus_accept_all = None
        try:
            from manus_accept_all_button import MANUSAcceptAllButton
            self.manus_accept_all = MANUSAcceptAllButton()
            self.manus_available = True
            logger.info("   ✅ MANUS Accept All Button integration available")
        except ImportError as e:
            logger.debug(f"   MANUS not available: {e}")
        except Exception as e:
            logger.debug(f"   MANUS initialization failed: {e}")

    def _should_accept(self) -> bool:
        """
        FEEDBACK LOOP: Check if we should accept changes (prevent infinite loop)

        Returns: True if we should proceed with acceptance, False if we should skip
        """
        import hashlib
        from datetime import datetime, timedelta

        now = datetime.now()

        # Check cooldown period
        if self.last_acceptance_time:
            time_since_last = (now - self.last_acceptance_time).total_seconds()
            if time_since_last < self.acceptance_cooldown:
                logger.debug(f"   ⏸️  Cooldown active ({time_since_last:.1f}s < {self.acceptance_cooldown}s) - skipping")
                return False

        # Check rate limit (max acceptances per minute)
        # Reset counter if more than 1 minute has passed
        if self.last_acceptance_time:
            time_since_last = (now - self.last_acceptance_time).total_seconds()
            if time_since_last > 60:
                self.acceptance_count = 0

        if self.acceptance_count >= self.max_acceptances_per_minute:
            logger.warning(f"   ⚠️  Rate limit reached ({self.acceptance_count}/{self.max_acceptances_per_minute}) - preventing infinite loop")
            return False

        return True

    def _record_acceptance(self, acceptance_hash: Optional[str] = None):
        """Record that we accepted changes (FEEDBACK LOOP state tracking)"""
        from datetime import datetime
        import hashlib

        self.last_acceptance_time = datetime.now()
        self.acceptance_count += 1

        if acceptance_hash:
            self.last_acceptance_hash = acceptance_hash

        logger.debug(f"   📝 Recorded acceptance (#{self.acceptance_count}, cooldown: {self.acceptance_cooldown}s)")

    def detect_and_accept_changes(self, verbose: bool = False) -> bool:
        """
        Detect "Keep All" / "Accept Changes" dialog and automatically accept

        FEEDBACK LOOP: Uses state tracking to prevent infinite loops.

        Uses multiple methods:
        1. Keyboard shortcut (Ctrl+Alt+Enter) - most reliable
        2. UI automation to find and click button
        3. Screen search for button

        Args:
            verbose: If True, log more details for debugging

        Returns: True if changes were accepted, False otherwise
        """
        # FEEDBACK LOOP: Check if we should proceed
        if not self._should_accept():
            if verbose:
                logger.info("   ⏸️  Cooldown/rate limit active - skipping detection")
            return False

        # Log detection attempt
        if verbose:
            logger.info("   🔍 Checking for 'Keep All' / 'Accept All Changes' dialog...")
        else:
            logger.debug("   🔍 Checking for 'Keep All' / 'Accept All Changes' dialog...")

        # Method 0: Try MANUS FIRST (primary control method - was working before)
        if self.manus_available and self.manus_accept_all:
            try:
                logger.info("   🤖 Using MANUS to accept all changes...")
                success = self.manus_accept_all.accept_all_changes()
                if success:
                    self._record_acceptance("manus_accept_all")
                    logger.info("   ✅ MANUS successfully accepted all changes")
                    return True
                else:
                    if verbose:
                        logger.debug("   MANUS accept_all_changes returned False - trying other methods")
            except Exception as e:
                logger.debug(f"   MANUS accept failed: {e} - trying other methods")

        # Method 1: Try keyboard shortcuts (fallback if MANUS not available or failed)
        # NOTE: Keyboard shortcuts are also sent aggressively in monitor loop
        # This method is for when detect_and_accept_changes is called directly
        try:
            import keyboard
            # Try primary shortcut (Ctrl+Alt+Enter) - most common in Cursor IDE
            keyboard.press_and_release('ctrl+alt+enter')
            time.sleep(0.3)
            if verbose:
                logger.info("   ⌨️  Sent Ctrl+Alt+Enter (primary shortcut)")
            else:
                logger.debug("   ⌨️  Sent Ctrl+Alt+Enter")

            # FEEDBACK LOOP: Record acceptance
            self._record_acceptance()
            logger.info("   ✅ Keyboard shortcut sent - 'Keep All' should be accepted")
            return True
        except ImportError:
            logger.warning("   ⚠️  keyboard module not available - install: pip install keyboard")
            # Continue to UI automation methods
        except Exception as e:
            if verbose:
                logger.debug(f"   Primary keyboard shortcut failed: {e}")
            # Try alternative shortcuts
            try:
                import keyboard
                alt_shortcuts = ['ctrl+shift+enter', 'alt+enter', 'ctrl+enter']
                for alt_shortcut in alt_shortcuts:
                    try:
                        keyboard.press_and_release(alt_shortcut)
                        time.sleep(0.2)
                        if verbose:
                            logger.info(f"   ⌨️  Sent {alt_shortcut} (alternative shortcut)")
                        self._record_acceptance()
                        return True
                    except Exception:
                        continue
            except Exception:
                pass

        # Keyboard shortcuts are tried FIRST above - if we get here, they didn't work
        # Now try UI automation as fallback
        if not self.ui_available:
            logger.debug("   ⚠️  UI automation not available - keyboard shortcuts only")
            return False

        # Method 2: Try UI automation
        try:
            # PERIODIC REFRESH: Reconnect to window periodically
            from datetime import datetime
            now = datetime.now()

            # Refresh window connection if needed
            if (self.cached_app is None or
                self.last_refresh_time is None or
                (now - self.last_refresh_time).total_seconds() > self.refresh_interval):
                try:
                    # Try multiple ways to connect to Cursor IDE window
                    app = None
                    # Method 1: By title regex
                    try:
                        app = self.pywinauto.Application().connect(title_re=".*Cursor.*", found_index=0)
                    except Exception:
                        pass

                    # Method 2: By process name
                    if app is None:
                        try:
                            app = self.pywinauto.Application().connect(process="Cursor.exe")
                        except Exception:
                            pass

                    # Method 3: By class name
                    if app is None:
                        try:
                            app = self.pywinauto.Application().connect(class_name="Chrome_WidgetWin_1")
                        except Exception:
                            pass

                    if app:
                        self.cached_app = app
                        self.last_refresh_time = now
                        logger.debug("   🔄 Refreshed window connection")
                    else:
                        logger.debug("   ⚠️  Could not find Cursor window")
                        self.cached_app = None
                except Exception as e:
                    logger.debug(f"   ⚠️  Could not refresh window connection: {e}")
                    self.cached_app = None

            if self.cached_app is None:
                # Try fresh connection with multiple methods
                app = None
                try:
                    app = self.pywinauto.Application().connect(title_re=".*Cursor.*", found_index=0)
                except Exception:
                    try:
                        app = self.pywinauto.Application().connect(process="Cursor.exe")
                    except Exception:
                        pass
                if app is None:
                    raise Exception("Could not connect to Cursor window")
            else:
                app = self.cached_app

            # Try to get the active window or top window
            try:
                window = app.top_window()
            except Exception:
                # Fallback: try to get active window
                try:
                    window = app.active()
                except Exception:
                    raise Exception("Could not get window handle")

            # Look for "Keep All" or "Accept Changes" button
            # Common button texts in Cursor IDE (DOUBLED list for better detection)
            button_texts = [
                "Keep All",
                "Accept All",
                "Accept Changes",
                "Keep Changes",
                "Accept",
                "Accept All Changes",
                "Keep",  # Short form
                "Apply",  # Alternative text
                "Apply All",  # Alternative
                "✓ Keep All",  # With checkmark
                "✓ Accept",  # With checkmark
                # DOUBLED: Additional variations for better detection
                "Keep All Changes",
                "Accept All Changes",
                "Keep All Files",
                "Accept All Files",
                "Keep Current",
                "Accept Current",
                "Keep Selection",
                "Accept Selection",
                "Keep This",
                "Accept This",
                "Keep These",
                "Accept These",
                "✓ Keep All Changes",  # With checkmark
                "✓ Accept All Changes",  # With checkmark
                "✓ Keep",  # With checkmark
                "✓ Accept",  # With checkmark
                "Keep All (Ctrl+Alt+Enter)",  # With shortcut hint
                "Accept All (Ctrl+Alt+Enter)",  # With shortcut hint
                "Keep All Changes (Ctrl+Alt+Enter)",  # With shortcut hint
                "Accept All Changes (Ctrl+Alt+Enter)",  # With shortcut hint
            ]

            for button_text in button_texts:
                try:
                    # Try multiple search methods
                    button = None

                    # Method 2a: By title
                    try:
                        button = window.child_window(title=button_text, control_type="Button")
                    except Exception:
                        pass

                    # Method 2b: By partial title match
                    if not button or not button.exists():
                        try:
                            button = window.child_window(title_re=f".*{button_text}.*", control_type="Button")
                        except Exception:
                            pass

                    # Method 2c: Find all buttons and check text
                    if not button or not button.exists():
                        try:
                            buttons = window.descendants(control_type="Button")
                            for btn in buttons:
                                try:
                                    btn_text = btn.window_text().lower()
                                    if button_text.lower() in btn_text or btn_text in button_text.lower():
                                        button = btn
                                        break
                                except Exception:
                                    continue
                        except Exception:
                            pass

                    # Method 2d: Search in all dialogs/panels
                    if not button or not button.exists():
                        try:
                            # Look for dialogs that might contain the button
                            dialogs = window.descendants(control_type="Dialog")
                            for dialog in dialogs:
                                try:
                                    dialog_buttons = dialog.descendants(control_type="Button")
                                    for btn in dialog_buttons:
                                        try:
                                            btn_text = btn.window_text().lower()
                                            if button_text.lower() in btn_text:
                                                button = btn
                                                break
                                        except Exception:
                                            continue
                                    if button and button.exists():
                                        break
                                except Exception:
                                    continue
                        except Exception:
                            pass

                    if button and button.exists():
                        # FEEDBACK LOOP: Check again before clicking (state may have changed)
                        if not self._should_accept():
                            logger.debug("   ⏸️  Skipping - cooldown/rate limit active")
                            return False

                        logger.info(f"   ✅ Found '{button_text}' button - auto-accepting")

                        # Use decisioning engine to make decision
                        try:
                            decision = self.decisioning_engine.handle_cursor_changes({
                                "count": 1,
                                "files": ["auto-detected"],
                                "source": "cursor_ide_auto_accept"
                            })
                        except Exception:
                            pass  # Continue even if decisioning fails

                        # Click button
                        button.click()
                        time.sleep(0.5)  # Brief pause

                        # FEEDBACK LOOP: Record acceptance
                        button_hash = f"{button_text}_{button.rectangle()}"
                        self._record_acceptance(button_hash)

                        logger.info(f"   ✅ Changes accepted automatically (feedback loop: #{self.acceptance_count})")
                        return True
                except Exception as e:
                    logger.debug(f"   Button search failed for '{button_text}': {e}")
                    continue

            # Method 3: Try keyboard shortcut via pyautogui (fallback)
            try:
                # FEEDBACK LOOP: Check again before sending
                if not self._should_accept():
                    return False

                self.pyautogui.hotkey('ctrl', 'alt', 'enter')
                time.sleep(0.3)
                if verbose:
                    logger.info("   ✅ Sent Ctrl+Alt+Enter via pyautogui")
                else:
                    logger.debug("   ✅ Sent Ctrl+Alt+Enter via pyautogui")

                # FEEDBACK LOOP: Record acceptance
                self._record_acceptance()
                return True
            except Exception as e:
                if verbose:
                    logger.debug(f"   Pyautogui shortcut failed: {e}")
                pass

            return False

        except Exception as e:
            logger.debug(f"   🔍 No changes dialog detected: {e}")
            return False

        # If we get here, no method worked - log for debugging
        logger.debug("   ⚠️  All detection methods failed - dialog may not be present")
        return False

    def _is_cursor_running(self) -> bool:
        """Check if Cursor IDE is actually running"""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and 'cursor' in proc.info['name'].lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except ImportError:
            # psutil not available - try alternative method
            try:
                if self.ui_available:
                    # Try to connect - if it fails, Cursor isn't running
                    app = self.pywinauto.Application().connect(title_re=".*Cursor.*", found_index=0)
                    return app is not None
            except Exception:
                pass
            return True  # Assume running if we can't check

    def _monitor_dialog_signal(self):
        """
        OSCILLOSCOPE-STYLE MONITORING: Monitor for dialog appearance as a signal/frequency

        Like an oscilloscope monitoring electrical frequencies, we monitor for the
        "Keep All" dialog signal and only act when we detect it.

        Returns: True if dialog signal detected, False otherwise
        """
        if not self.ui_available:
            return False

        try:
            # Connect to Cursor IDE window
            app = None
            try:
                app = self.pywinauto.Application().connect(title_re=".*Cursor.*", found_index=0)
            except Exception:
                try:
                    app = self.pywinauto.Application().connect(process="Cursor.exe")
                except Exception:
                    return False

            if not app:
                return False

            # Get window
            try:
                window = app.top_window()
            except Exception:
                try:
                    window = app.active()
                except Exception:
                    return False

            # OSCILLOSCOPE: Scan for dialog signal (button presence = signal detected)
            # Look for "Keep All" button as the signal
            button_texts = ["Keep All", "Accept All", "Accept All Changes", "Keep All Changes"]

            for button_text in button_texts:
                try:
                    # Method 1: Direct button search
                    button = window.child_window(title=button_text, control_type="Button")
                    if button.exists():
                        return True  # SIGNAL DETECTED
                except Exception:
                    pass

                # Method 2: Search all buttons
                try:
                    buttons = window.descendants(control_type="Button")
                    for btn in buttons:
                        try:
                            if button_text.lower() in btn.window_text().lower():
                                return True  # SIGNAL DETECTED
                        except Exception:
                            continue
                except Exception:
                    pass

                # Method 3: Search dialogs
                try:
                    dialogs = window.descendants(control_type="Dialog")
                    for dialog in dialogs:
                        try:
                            dialog_buttons = dialog.descendants(control_type="Button")
                            for btn in dialog_buttons:
                                try:
                                    if button_text.lower() in btn.window_text().lower():
                                        return True  # SIGNAL DETECTED
                                except Exception:
                                    continue
                        except Exception:
                            continue
                except Exception:
                    pass

            return False  # No signal detected

        except Exception:
            return False

    def monitor_and_auto_accept(self, interval: float = 0.5):  # High-frequency monitoring (oscilloscope-style)
        """
        OSCILLOSCOPE-STYLE MONITORING: Monitor for dialog signal and auto-accept

        Like an oscilloscope monitoring frequencies, we continuously scan for the
        "Keep All" dialog signal. When detected, we act immediately.

        FEEDBACK LOOP: Uses state tracking to prevent infinite loops.

        Args:
            interval: Scan interval in seconds (default: 0.5s for high-frequency monitoring)
        """
        logger.info("   📡 Starting oscilloscope-style dialog monitoring...")
        logger.info(f"      Scan frequency: {1.0/interval:.1f} Hz (monitoring for 'Keep All' dialog signal)")
        logger.info(f"      Cooldown: {self.acceptance_cooldown}s")
        logger.info(f"      Rate limit: {self.max_acceptances_per_minute}/min")
        logger.info("   ✅ Oscilloscope monitoring ACTIVE - detecting dialog signals")

        # Initialize stats
        self.stats = {"total_checks": 0, "successful_accepts": 0, "signals_detected": 0}

        # Check if UI libraries are available
        if not self.ui_available:
            logger.warning("   ⚠️  UI automation libraries not available - using keyboard fallback")
            logger.warning("   Install: pip install pyautogui pywinauto for oscilloscope monitoring")
        else:
            logger.info("   ✅ UI automation available (oscilloscope + keyboard)")

        # Check MANUS availability
        if self.manus_available:
            logger.info("   ✅ MANUS control available (primary method)")
        else:
            logger.warning("   ⚠️  MANUS not available - using fallback methods")

        consecutive_failures = 0
        max_failures = 10
        last_signal_state = False  # Track signal state changes

        while True:
            try:
                # Check if Cursor IDE is running
                if not self._is_cursor_running():
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        logger.warning(
                            "   ⚠️  Cursor IDE not detected (failed %d times) - "
                            "pausing monitoring",
                            consecutive_failures
                        )
                        consecutive_failures = 0
                        time.sleep(interval * 10)  # Longer pause if Cursor not running
                    else:
                        time.sleep(interval)
                    continue

                # Reset failure counter if Cursor is running
                consecutive_failures = 0

                # OSCILLOSCOPE: Monitor for dialog signal (high-frequency scanning)
                signal_detected = self._monitor_dialog_signal()

                # Log detection attempts periodically for debugging
                if self.stats.get("total_checks", 0) % 20 == 0:  # Every 10 seconds at 0.5s interval
                    logger.debug(f"   🔍 Dialog monitoring: Cursor running={self._is_cursor_running()}, Signal detected={signal_detected}")

                # Track signal state changes (signal appeared = dialog opened)
                if signal_detected and not last_signal_state:
                    # SIGNAL DETECTED: Dialog just appeared
                    logger.info("   📡 DIALOG SIGNAL DETECTED - 'Keep All' dialog appeared")
                    self.stats["signals_detected"] = self.stats.get("signals_detected", 0) + 1

                    # Try MANUS first (primary method)
                    accepted = False
                    if self.manus_available and self.manus_accept_all:
                        try:
                            logger.info("   🤖 Using MANUS to accept (signal detected)...")
                            accepted = self.manus_accept_all.accept_all_changes()
                            if accepted:
                                self._record_acceptance("manus_signal_detected")
                                logger.info("   ✅ MANUS accepted changes (signal-based)")
                        except Exception as e:
                            logger.debug(f"   MANUS signal-based accept failed: {e}")

                    # Fallback to detect_and_accept_changes if MANUS failed
                    if not accepted:
                        accepted = self.detect_and_accept_changes(verbose=True)

                    if accepted:
                        self.stats["successful_accepts"] = self.stats.get("successful_accepts", 0) + 1
                        logger.info("   ✅ Changes accepted automatically - signal processed")
                        time.sleep(max(1.0, self.acceptance_cooldown))
                    else:
                        logger.warning("   ⚠️  Signal detected but acceptance failed - retrying...")
                        # Retry a few times
                        for retry in range(3):
                            time.sleep(0.2)
                            accepted = self.detect_and_accept_changes(verbose=False)
                            if accepted:
                                self.stats["successful_accepts"] = self.stats.get("successful_accepts", 0) + 1
                                logger.info("   ✅ Changes accepted on retry #%d", retry + 1)
                                break

                last_signal_state = signal_detected

                # Track checks
                if not hasattr(self, 'stats'):
                    self.stats = {"total_checks": 0, "successful_accepts": 0, "signals_detected": 0}
                self.stats["total_checks"] = self.stats.get("total_checks", 0) + 1

                # High-frequency scanning (oscilloscope-style)
                time.sleep(interval)

            except KeyboardInterrupt:
                logger.info("   ⏹️  Monitoring stopped")
                break
            except Exception as e:
                consecutive_failures += 1
                logger.warning(f"   ⚠️  Error in oscilloscope monitoring: {e}")
                if consecutive_failures >= max_failures:
                    logger.error(
                        "   ❌ Multiple consecutive failures (%d) - "
                        "checking if Cursor IDE is running",
                        consecutive_failures
                    )
                    consecutive_failures = 0
                time.sleep(interval)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor IDE Auto-Accept Changes")
    parser.add_argument("--once", action="store_true", help="Check once and exit")
    parser.add_argument("--monitor", action="store_true", help="Continuously monitor")
    parser.add_argument("--interval", type=float, default=2.0, help="Monitor interval (seconds) - default 2.0 for faster detection")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging for debugging")
    parser.add_argument("--test", action="store_true", help="Test mode - check once with verbose output")

    args = parser.parse_args()

    auto_accept = CursorIDEAutoAccept()

    if args.test:
        # Test mode - verbose check once
        print("\n🧪 Testing Auto-Accept (verbose mode)...")
        print("💡 Make sure a 'Keep All' / 'Accept All Changes' dialog is open in Cursor IDE\n")
        result = auto_accept.detect_and_accept_changes(verbose=True)
        if result:
            print("\n✅ SUCCESS: Changes accepted!")
        else:
            print("\n⚠️  No dialog detected or acceptance failed")
            print("💡 Check:")
            print("   - Is Cursor IDE running?")
            print("   - Is a 'Keep All' dialog open?")
            print("   - Is Cursor IDE window focused?")
        sys.exit(0 if result else 1)
    elif args.monitor:
        auto_accept.monitor_and_auto_accept(interval=args.interval)
    elif args.once:
        result = auto_accept.detect_and_accept_changes(verbose=args.verbose)
        sys.exit(0 if result else 1)
    else:
        # Default: check once
        result = auto_accept.detect_and_accept_changes(verbose=args.verbose)
        sys.exit(0 if result else 1)

    return 0


if __name__ == "__main__":


    sys.exit(main())