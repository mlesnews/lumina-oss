#!/usr/bin/env python3
"""
R2-D2 Sound System
Star Wars themed sound effects using R2-D2 beeps and whistles

Replaces system sounds, notification chimes, and alerts with R2-D2 sounds.

Tags: #R2D2 #STAR_WARS #SOUND #NOTIFICATION #ALERT @JARVIS @LUMINA
"""

import sys
import time
import random
from pathlib import Path
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

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

logger = get_logger("R2D2SoundSystem")


class R2D2SoundType(Enum):
    """R2-D2 sound types for different contexts"""
    # Happy/Positive
    HAPPY = "happy"                    # Happy beeps (success, completion)
    EXCITED = "excited"                # Excited whistles (great success)
    PLEASED = "pleased"                # Pleased chirps (satisfaction)

    # Neutral/Informational
    NOTIFICATION = "notification"       # Notification beep (info, message)
    PROMPT = "prompt"                  # Prompt sound (waiting for input)
    CONFIRMATION = "confirmation"      # Confirmation beep (acknowledged)
    CONNECTION = "connection"          # Connection established (mutual gaze)

    # Alert/Warning
    ALERT = "alert"                    # Alert beep (attention needed)
    WARNING = "warning"                # Warning whistle (caution)
    ATTENTION = "attention"            # Attention sound (important)

    # Error/Negative
    ERROR = "error"                    # Error beep (something wrong)
    SAD = "sad"                        # Sad whistle (disappointment)
    CONCERNED = "concerned"            # Concerned beeps (worry)

    # Special
    WORKING = "working"                # Working sound (processing)
    SCANNING = "scanning"              # Scanning sound (analyzing)
    THINKING = "thinking"              # Thinking sound (processing)


class R2D2SoundSystem:
    """
    R2-D2 Sound System

    Plays R2-D2 style beeps and whistles for different contexts.
    Uses Windows winsound or system beeps to create R2-D2-like sounds.
    """

    def __init__(self):
        """Initialize R2-D2 sound system"""
        self.sound_enabled = True
        self.volume = 1.0  # 0.0 to 1.0
        self.tactical_silence = True  # Enable silence during disk crisis
        self.last_sound_time: Dict[str, float] = {}
        self.sound_cooldown = 300  # 5 minute cooldown

        # Daytime hours configuration (24-hour format)
        self.daytime_start_hour = 6   # 6 AM
        self.daytime_end_hour = 22   # 10 PM (22:00)
        self.daytime_only = True      # Only play beeps during daytime

        # Sound patterns for different contexts
        self.sound_patterns = self._initialize_sound_patterns()

        logger.info("✅ R2-D2 Sound System initialized")
        logger.info("   🔊 Star Wars themed sound effects ready")
        logger.info(f"   ⏰ Daytime-only mode: {self.daytime_start_hour:02d}:00 - {self.daytime_end_hour:02d}:00")

    def _initialize_sound_patterns(self) -> Dict[R2D2SoundType, list]:
        """Initialize sound patterns for each R2-D2 sound type"""
        return {
            # Happy/Positive
            R2D2SoundType.HAPPY: [
                {"freq": 1000, "duration": 100, "pause": 50},
                {"freq": 1200, "duration": 100, "pause": 0}
            ],
            R2D2SoundType.EXCITED: [
                {"freq": 800, "duration": 80, "pause": 30},
                {"freq": 1000, "duration": 80, "pause": 30},
                {"freq": 1200, "duration": 100, "pause": 30},
                {"freq": 1400, "duration": 120, "pause": 0}
            ],
            R2D2SoundType.PLEASED: [
                {"freq": 1100, "duration": 150, "pause": 0}
            ],

            # Neutral/Informational
            R2D2SoundType.NOTIFICATION: [
                {"freq": 900, "duration": 120, "pause": 0}
            ],
            R2D2SoundType.PROMPT: [
                {"freq": 800, "duration": 100, "pause": 50},
                {"freq": 800, "duration": 100, "pause": 0}
            ],
            R2D2SoundType.CONFIRMATION: [
                {"freq": 1000, "duration": 80, "pause": 0}
            ],
            R2D2SoundType.CONNECTION: [
                {"freq": 700, "duration": 100, "pause": 50},
                {"freq": 900, "duration": 100, "pause": 50},
                {"freq": 1100, "duration": 150, "pause": 0}
            ],

            # Alert/Warning
            R2D2SoundType.ALERT: [
                {"freq": 1200, "duration": 150, "pause": 100},
                {"freq": 1200, "duration": 150, "pause": 0}
            ],
            R2D2SoundType.WARNING: [
                {"freq": 1000, "duration": 100, "pause": 50},
                {"freq": 800, "duration": 100, "pause": 0}
            ],
            R2D2SoundType.ATTENTION: [
                {"freq": 1300, "duration": 120, "pause": 0}
            ],

            # Error/Negative
            R2D2SoundType.ERROR: [
                {"freq": 600, "duration": 200, "pause": 100},
                {"freq": 500, "duration": 200, "pause": 0}
            ],
            R2D2SoundType.SAD: [
                {"freq": 700, "duration": 150, "pause": 50},
                {"freq": 600, "duration": 200, "pause": 0}
            ],
            R2D2SoundType.CONCERNED: [
                {"freq": 800, "duration": 100, "pause": 50},
                {"freq": 750, "duration": 100, "pause": 50},
                {"freq": 700, "duration": 150, "pause": 0}
            ],

            # Special
            R2D2SoundType.WORKING: [
                {"freq": 900, "duration": 50, "pause": 30},
                {"freq": 1000, "duration": 50, "pause": 30},
                {"freq": 1100, "duration": 50, "pause": 0}
            ],
            R2D2SoundType.SCANNING: [
                {"freq": 1000, "duration": 80, "pause": 40},
                {"freq": 1200, "duration": 80, "pause": 40},
                {"freq": 1000, "duration": 80, "pause": 0}
            ],
            R2D2SoundType.THINKING: [
                {"freq": 850, "duration": 100, "pause": 50},
                {"freq": 950, "duration": 100, "pause": 0}
            ]
        }

    def _is_daytime(self) -> bool:
        """Check if current time is within daytime hours"""
        if not self.daytime_only:
            return True  # Always allow if daytime-only is disabled

        current_hour = datetime.now().hour

        # Handle wrap-around (e.g., 6 AM to 10 PM)
        if self.daytime_start_hour <= self.daytime_end_hour:
            # Normal case: start < end (e.g., 6 AM to 10 PM)
            return self.daytime_start_hour <= current_hour < self.daytime_end_hour
        else:
            # Wrap-around case: start > end (e.g., 10 PM to 6 AM)
            return current_hour >= self.daytime_start_hour or current_hour < self.daytime_end_hour

    def play_sound(self, sound_type: R2D2SoundType, variation: Optional[int] = None):
        """
        Play R2-D2 sound for given context - with Tactical Silence and Throttling
        """
        if not self.sound_enabled or self.tactical_silence:
            return

        # Check cooldown for non-critical sounds
        current_time = time.time()
        sound_key = sound_type.value
        last_time = self.last_sound_time.get(sound_key, 0)

        # Only allow if cooldown passed OR if it's an ALERT/ERROR variation
        is_high_priority = sound_type in [R2D2SoundType.ALERT, R2D2SoundType.ERROR, R2D2SoundType.WARNING]
        if (current_time - last_time < self.sound_cooldown) and not is_high_priority:
            return

        self.last_sound_time[sound_key] = current_time

        # Check if it's daytime - only play beeps during daytime hours
        if not self._is_daytime():
            logger.debug(f"🔇 Skipping R2-D2 sound ({sound_type.value}) - outside daytime hours")
            return

        try:
            import winsound

            pattern = self.sound_patterns.get(sound_type)
            if not pattern:
                logger.warning(f"⚠️  No sound pattern for {sound_type.value}")
                return

            # Apply variation if specified
            if variation is not None and variation > 0:
                pattern = self._apply_variation(pattern, variation)

            # Play the sound pattern
            for note in pattern:
                freq = note["freq"]
                duration = note["duration"]
                pause = note.get("pause", 0)

                # Adjust volume (Windows winsound doesn't support volume, but we can adjust duration slightly)
                if self.volume < 1.0:
                    duration = int(duration * self.volume)

                winsound.Beep(freq, duration)

                if pause > 0:
                    time.sleep(pause / 1000.0)  # Convert ms to seconds

            logger.debug(f"🔊 Played R2-D2 sound: {sound_type.value}")

        except ImportError:
            # winsound not available (non-Windows), try alternative
            try:
                import os
                # System beep as fallback
                os.system("echo '\a'")
                logger.debug(f"🔊 Played system beep (R2-D2 sound: {sound_type.value})")
            except:
                logger.debug("Could not play R2-D2 sound")
        except Exception as e:
            logger.debug(f"Error playing R2-D2 sound: {e}")

    def _apply_variation(self, pattern: list, variation: int) -> list:
        """Apply variation to sound pattern (slight frequency/duration changes)"""
        varied = []
        for note in pattern:
            new_note = note.copy()
            # Vary frequency by ±50Hz
            freq_variation = random.randint(-50, 50) * variation
            new_note["freq"] = max(200, min(2000, note["freq"] + freq_variation))
            # Vary duration by ±10ms
            dur_variation = random.randint(-10, 10) * variation
            new_note["duration"] = max(50, note["duration"] + dur_variation)
            varied.append(new_note)
        return varied

    def play_happy(self, variation: Optional[int] = None):
        """Play happy R2-D2 sound"""
        self.play_sound(R2D2SoundType.HAPPY, variation)

    def play_excited(self, variation: Optional[int] = None):
        """Play excited R2-D2 sound"""
        self.play_sound(R2D2SoundType.EXCITED, variation)

    def play_notification(self, variation: Optional[int] = None):
        """Play notification R2-D2 sound"""
        self.play_sound(R2D2SoundType.NOTIFICATION, variation)

    def play_prompt(self, variation: Optional[int] = None):
        """Play prompt R2-D2 sound"""
        self.play_sound(R2D2SoundType.PROMPT, variation)

    def play_connection(self, variation: Optional[int] = None):
        """Play connection R2-D2 sound (mutual gaze)"""
        self.play_sound(R2D2SoundType.CONNECTION, variation)

    def play_alert(self, variation: Optional[int] = None):
        """Play alert R2-D2 sound"""
        self.play_sound(R2D2SoundType.ALERT, variation)

    def play_warning(self, variation: Optional[int] = None):
        """Play warning R2-D2 sound"""
        self.play_sound(R2D2SoundType.WARNING, variation)

    def play_error(self, variation: Optional[int] = None):
        """Play error R2-D2 sound"""
        self.play_sound(R2D2SoundType.ERROR, variation)

    def play_working(self, variation: Optional[int] = None):
        """Play working R2-D2 sound"""
        self.play_sound(R2D2SoundType.WORKING, variation)

    def play_pleased(self, variation: Optional[int] = None):
        """Play pleased R2-D2 sound"""
        self.play_sound(R2D2SoundType.PLEASED, variation)

    def play_confirmation(self, variation: Optional[int] = None):
        """Play confirmation R2-D2 sound"""
        self.play_sound(R2D2SoundType.CONFIRMATION, variation)

    def play_attention(self, variation: Optional[int] = None):
        """Play attention R2-D2 sound"""
        self.play_sound(R2D2SoundType.ATTENTION, variation)

    def play_sad(self, variation: Optional[int] = None):
        """Play sad R2-D2 sound"""
        self.play_sound(R2D2SoundType.SAD, variation)

    def play_concerned(self, variation: Optional[int] = None):
        """Play concerned R2-D2 sound"""
        self.play_sound(R2D2SoundType.CONCERNED, variation)

    def play_scanning(self, variation: Optional[int] = None):
        """Play scanning R2-D2 sound"""
        self.play_sound(R2D2SoundType.SCANNING, variation)

    def play_thinking(self, variation: Optional[int] = None):
        """Play thinking R2-D2 sound"""
        self.play_sound(R2D2SoundType.THINKING, variation)

    def set_enabled(self, enabled: bool):
        """Enable or disable sound system"""
        self.sound_enabled = enabled
        logger.info(f"🔊 R2-D2 Sound System: {'Enabled' if enabled else 'Disabled'}")

    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        logger.info(f"🔊 R2-D2 Sound System volume: {self.volume:.0%}")

    def set_daytime_hours(self, start_hour: int, end_hour: int):
        """Set daytime hours (24-hour format)"""
        self.daytime_start_hour = max(0, min(23, start_hour))
        self.daytime_end_hour = max(0, min(23, end_hour))
        logger.info(f"⏰ Daytime hours set: {self.daytime_start_hour:02d}:00 - {self.daytime_end_hour:02d}:00")

    def set_daytime_only(self, enabled: bool):
        """Enable or disable daytime-only mode"""
        self.daytime_only = enabled
        logger.info(f"⏰ Daytime-only mode: {'Enabled' if enabled else 'Disabled'}")


# Singleton instance
_r2d2_sound_system: Optional[R2D2SoundSystem] = None


def get_r2d2_sound_system() -> R2D2SoundSystem:
    """Get singleton R2-D2 sound system instance"""
    global _r2d2_sound_system
    if _r2d2_sound_system is None:
        _r2d2_sound_system = R2D2SoundSystem()
    return _r2d2_sound_system


def main():
    """Test R2-D2 sound system"""
    print("=" * 80)
    print("🔊 R2-D2 SOUND SYSTEM TEST")
    print("=" * 80)
    print()

    r2d2 = get_r2d2_sound_system()

    print("Playing all R2-D2 sounds...")
    print()

    # Happy sounds
    print("Happy sounds:")
    r2d2.play_happy()
    time.sleep(0.5)
    r2d2.play_excited()
    time.sleep(0.5)
    r2d2.play_pleased()
    time.sleep(1.0)
    print()

    # Notifications
    print("Notification sounds:")
    r2d2.play_notification()
    time.sleep(0.5)
    r2d2.play_prompt()
    time.sleep(0.5)
    r2d2.play_confirmation()
    time.sleep(0.5)
    r2d2.play_connection()
    time.sleep(1.0)
    print()

    # Alerts
    print("Alert sounds:")
    r2d2.play_alert()
    time.sleep(0.5)
    r2d2.play_warning()
    time.sleep(0.5)
    r2d2.play_attention()
    time.sleep(1.0)
    print()

    # Errors
    print("Error sounds:")
    r2d2.play_error()
    time.sleep(0.5)
    r2d2.play_sad()
    time.sleep(0.5)
    r2d2.play_concerned()
    time.sleep(1.0)
    print()

    # Special
    print("Special sounds:")
    r2d2.play_working()
    time.sleep(0.5)
    r2d2.play_scanning()
    time.sleep(0.5)
    r2d2.play_thinking()
    time.sleep(1.0)
    print()

    print("=" * 80)
    print("✅ R2-D2 Sound System test complete")
    print("=" * 80)


if __name__ == "__main__":


    main()