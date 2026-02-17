#!/usr/bin/env python3
"""
Aggressive Button Clicker - REQUIRED

Continuously and aggressively clicks buttons so user doesn't have to.
Checks every 1 second and clicks immediately when found.

Tags: #AGGRESSIVE #BUTTON_CLICKER #REQUIRED #NO_MANUAL_CLICKS @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path

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

logger = get_logger("AggressiveButtonClicker")


class AggressiveButtonClicker:
    """Aggressively clicks all buttons user shouldn't have to click"""

    def __init__(self):
        self.running = False
        self.last_keep_all_click = 0
        self.last_voice_click = 0
        self.last_people_click = 0
        self.last_send_click = 0
        self.click_cooldown = 1.0  # Check every 1 second - more aggressive for Keep All

    def click_keep_all(self):
        """Click Keep All button - CONTINUOUSLY, automatically (if human not active)"""
        # CRITICAL: Check if human is active - don't click if human is using mouse/keyboard
        try:
            from human_activity_detector import is_automation_allowed
            if not is_automation_allowed():
                return False  # Human is active - don't click
        except ImportError:
            pass  # Human detector not available - continue

        current_time = time.time()
        if current_time - self.last_keep_all_click < self.click_cooldown:
            return False

        try:
            from manus_accept_all_button import MANUSAcceptAllButton
            button = MANUSAcceptAllButton()
            coords = button.find_accept_all_button()
            if coords:
                logger.info("🔘 Keep All button found - CLICKING NOW (automatic, continuous)")
                button.click_accept_all()
                self.last_keep_all_click = current_time
                return True
            else:
                # Keep trying - button might appear later
                logger.debug("🔍 Keep All button not found yet - will keep checking...")
        except Exception as e:
            logger.debug(f"Keep All click failed: {e}")
        return False

    def click_voice_input(self):
        """Click Voice Input button (if human not active)"""
        # CRITICAL: Check if human is active - don't click if human is using mouse/keyboard
        try:
            from human_activity_detector import is_automation_allowed
            if not is_automation_allowed():
                return False  # Human is active - don't click
        except ImportError:
            pass  # Human detector not available - continue

        current_time = time.time()
        if current_time - self.last_voice_click < self.click_cooldown:
            return False

        try:
            from manus_voice_input_button import MANUSVoiceInputButton
            button = MANUSVoiceInputButton()
            coords = button.find_voice_input_button()
            if coords:
                logger.info("🎤 Voice Input button found - CLICKING NOW")
                button.click_voice_input()
                self.last_voice_click = current_time
                return True
        except Exception as e:
            logger.debug(f"Voice Input click failed: {e}")
        return False

    def click_people(self):
        """Click People button"""
        current_time = time.time()
        if current_time - self.last_people_click < self.click_cooldown:
            return False

        try:
            from manus_people_button import MANUSPeopleButton
            button = MANUSPeopleButton()
            coords = button.find_people_button()
            if coords:
                logger.info("👥 People button found - CLICKING NOW")
                button.click_people()
                self.last_people_click = current_time
                return True
        except Exception as e:
            logger.debug(f"People click failed: {e}")
        return False

    def click_send(self):
        """Click Send button"""
        current_time = time.time()
        if current_time - self.last_send_click < self.click_cooldown:
            return False

        try:
            from manus_send_button import MANUSSendButton
            button = MANUSSendButton()
            coords = button.find_send_button()
            if coords:
                logger.info("📤 Send button found - CLICKING NOW")
                button.click_send()
                self.last_send_click = current_time
                return True
        except Exception as e:
            logger.debug(f"Send click failed: {e}")
        return False

    def start(self):
        """Start aggressive button clicking"""
        logger.info("=" * 80)
        logger.info("🔧 STARTING AGGRESSIVE BUTTON CLICKER")
        logger.info("=" * 80)
        logger.info("   Checking every 1 second")
        logger.info("   Clicking immediately when buttons found")
        logger.info("=" * 80)
        logger.info()

        self.running = True

        def click_loop():
            check_count = 0
            while self.running:
                try:
                    check_count += 1

                    # CRITICAL: Check if human is active - don't click if human is using mouse/keyboard
                    try:
                        from human_activity_detector import is_automation_allowed
                        if not is_automation_allowed():
                            # Human is active - don't click buttons
                            logger.debug("👤 Human active - pausing button clicking")
                            time.sleep(1)
                            continue
                    except ImportError:
                        pass  # Human detector not available - continue normally

                    # CRITICAL: Keep All button is PRIORITY - check it first and most aggressively
                    clicked_keep_all = self.click_keep_all()

                    # Other buttons
                    clicked_voice = self.click_voice_input()
                    clicked_people = self.click_people()
                    clicked_send = self.click_send()

                    # Log when Keep All is clicked (important!)
                    if clicked_keep_all:
                        logger.info("✅ Keep All button clicked automatically (continuous monitoring)")

                    # Log every 10 checks (every 10 seconds)
                    if check_count % 10 == 0:
                        logger.info(f"🔄 Check #{check_count}: Keep All={clicked_keep_all}, Voice={clicked_voice}, People={clicked_people}, Send={clicked_send}")

                    time.sleep(1)  # Check every 1 second - continuous monitoring
                except Exception as e:
                    logger.error(f"❌ Click loop error: {e}")
                    time.sleep(5)

        thread = threading.Thread(target=click_loop, daemon=True)
        thread.start()
        logger.info("✅ Aggressive button clicker started")

    def stop(self):
        """Stop button clicking"""
        self.running = False


def main():
    """Main function"""
    print("=" * 80)
    print("🔧 AGGRESSIVE BUTTON CLICKER - NO MANUAL CLICKS")
    print("=" * 80)
    print()
    print("This will continuously click:")
    print("  ✅ Keep All button")
    print("  ✅ Voice Input button")
    print("  ✅ People button")
    print("  ✅ Send button")
    print()
    print("Checking every 1 second and clicking immediately when found.")
    print()

    clicker = AggressiveButtonClicker()
    clicker.start()

    print("=" * 80)
    print("✅ AGGRESSIVE BUTTON CLICKER RUNNING")
    print("=" * 80)
    print()
    print("You should NOT need to click any buttons manually.")
    print("Press Ctrl+C to stop")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping...")
        clicker.stop()


if __name__ == "__main__":


    main()