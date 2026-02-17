#!/usr/bin/env python3
"""
Tactile Feedback System
Provides haptic and tactile feedback for blind users
Equivalent to visual feedback for deaf users

Author: LUMINA Project
Date: 2026-01-14
Tag: @telepathy #blind #tactile #haptic #accessibility
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("TactileFeedbackSystem")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("TactileFeedbackSystem")


class FeedbackType(Enum):
    """Types of tactile feedback"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    NAVIGATION = "navigation"
    SELECTION = "selection"
    CONTEXT_CHANGE = "context_change"
    ACTION_START = "action_start"
    ACTION_COMPLETE = "action_complete"
    PROGRESS = "progress"


@dataclass
class TactilePattern:
    """Tactile feedback pattern"""
    pattern: List[float]  # List of durations in seconds (on, off, on, off, ...)
    intensity: float  # 0.0 to 1.0
    repeat: int = 1  # Number of times to repeat pattern


class TactileFeedbackSystem:
    """
    Tactile feedback system for blind users.

    Provides haptic and tactile feedback through:
    - Vibration patterns
    - Tactile patterns
    - Haptic controllers
    - Force feedback devices

    This is the tactile equivalent of visual feedback for deaf users.
    """

    # Predefined feedback patterns
    PATTERNS: Dict[FeedbackType, TactilePattern] = {
        FeedbackType.SUCCESS: TactilePattern(
            pattern=[0.1, 0.05, 0.1, 0.05, 0.1],
            intensity=0.7,
            repeat=1
        ),
        FeedbackType.ERROR: TactilePattern(
            pattern=[0.2, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2],
            intensity=1.0,
            repeat=1
        ),
        FeedbackType.WARNING: TactilePattern(
            pattern=[0.15, 0.1, 0.15],
            intensity=0.8,
            repeat=2
        ),
        FeedbackType.INFO: TactilePattern(
            pattern=[0.1],
            intensity=0.5,
            repeat=1
        ),
        FeedbackType.NAVIGATION: TactilePattern(
            pattern=[0.05, 0.05, 0.05],
            intensity=0.6,
            repeat=1
        ),
        FeedbackType.SELECTION: TactilePattern(
            pattern=[0.1, 0.05, 0.1],
            intensity=0.7,
            repeat=1
        ),
        FeedbackType.CONTEXT_CHANGE: TactilePattern(
            pattern=[0.15],
            intensity=0.6,
            repeat=1
        ),
        FeedbackType.ACTION_START: TactilePattern(
            pattern=[0.1, 0.05],
            intensity=0.6,
            repeat=1
        ),
        FeedbackType.ACTION_COMPLETE: TactilePattern(
            pattern=[0.1, 0.05, 0.1],
            intensity=0.7,
            repeat=1
        ),
    }

    def __init__(self, intensity: float = 0.7):
        """
        Initialize tactile feedback system.

        Args:
            intensity: Default intensity (0.0 to 1.0)
        """
        self.intensity = max(0.0, min(1.0, intensity))
        self.logger = logger
        self.available_devices: List[str] = []

        # Detect available haptic devices
        self._detect_devices()

        self.logger.info(f"Tactile Feedback System initialized (intensity: {self.intensity})")
        if self.available_devices:
            self.logger.info(f"Available devices: {', '.join(self.available_devices)}")
        else:
            self.logger.info("No haptic devices detected (using software simulation)")

    def _detect_devices(self):
        """Detect available haptic/tactile devices"""
        # Check for common haptic devices
        # This is a placeholder - actual implementation would detect:
        # - Game controllers with haptic feedback
        # - Haptic vests/gloves
        # - Vibration devices
        # - Force feedback devices

        # For now, we'll simulate feedback
        self.available_devices = ["software_simulation"]

    def feedback(self, feedback_type: str):
        """
        Provide tactile feedback.

        Args:
            feedback_type: Type of feedback (string or FeedbackType enum)
        """
        # Convert string to enum if needed
        if isinstance(feedback_type, str):
            try:
                feedback_type = FeedbackType(feedback_type.lower())
            except ValueError:
                self.logger.warning(f"Unknown feedback type: {feedback_type}, using INFO")
                feedback_type = FeedbackType.INFO

        # Get pattern
        pattern = self.PATTERNS.get(feedback_type)
        if not pattern:
            # Default pattern
            pattern = TactilePattern(
                pattern=[0.1],
                intensity=self.intensity,
                repeat=1
            )

        # Apply intensity scaling
        scaled_intensity = pattern.intensity * self.intensity

        # Execute pattern
        self._execute_pattern(pattern.pattern, scaled_intensity, pattern.repeat)

    def progress_feedback(self, progress: float):
        """
        Provide progress feedback (vibration intensity based on progress).

        Args:
            progress: Progress (0.0 to 1.0)
        """
        progress = max(0.0, min(1.0, progress))

        # Continuous vibration with intensity based on progress
        intensity = self.intensity * progress

        # Short vibration pulse
        self._vibrate(0.1, intensity)

    def custom_pattern(
        self,
        pattern: List[float],
        intensity: Optional[float] = None,
        repeat: int = 1
    ):
        """
        Provide custom tactile pattern.

        Args:
            pattern: List of durations (on, off, on, off, ...)
            intensity: Intensity (0.0 to 1.0), uses default if None
            repeat: Number of times to repeat
        """
        if intensity is None:
            intensity = self.intensity

        intensity = max(0.0, min(1.0, intensity))
        self._execute_pattern(pattern, intensity, repeat)

    def _execute_pattern(
        self,
        pattern: List[float],
        intensity: float,
        repeat: int
    ):
        """
        Execute tactile pattern.

        Args:
            pattern: Pattern of durations
            intensity: Vibration intensity
            repeat: Number of repetitions
        """
        for _ in range(repeat):
            for i, duration in enumerate(pattern):
                if i % 2 == 0:  # Even index = on
                    self._vibrate(duration, intensity)
                else:  # Odd index = off
                    time.sleep(duration)

    def _vibrate(self, duration: float, intensity: float):
        """
        Vibrate for specified duration and intensity.

        Args:
            duration: Duration in seconds
            intensity: Intensity (0.0 to 1.0)
        """
        # This is a placeholder - actual implementation would:
        # - Control haptic devices
        # - Send commands to game controllers
        # - Control vibration motors
        # - Interface with haptic APIs

        # For now, log the vibration
        self.logger.debug(f"Vibrate: {duration}s at {intensity:.2f} intensity")

        # In a real implementation, this would control actual hardware:
        # - Windows: XInput for game controllers
        # - Linux: evdev for input devices
        # - macOS: IOKit for haptic devices
        # - Custom: USB/Serial communication with haptic devices

    def set_intensity(self, intensity: float):
        """
        Set default intensity.

        Args:
            intensity: Intensity (0.0 to 1.0)
        """
        self.intensity = max(0.0, min(1.0, intensity))
        self.logger.info(f"Tactile intensity set to {self.intensity:.2f}")

    def is_available(self) -> bool:
        """Check if tactile feedback is available"""
        return len(self.available_devices) > 0


def main():
    """Test tactile feedback system"""
    print("\nTactile Feedback System Test")
    print("=" * 60)

    system = TactileFeedbackSystem(intensity=0.7)

    print("\n1. Success feedback...")
    system.feedback("success")
    time.sleep(0.5)

    print("\n2. Error feedback...")
    system.feedback("error")
    time.sleep(0.5)

    print("\n3. Warning feedback...")
    system.feedback("warning")
    time.sleep(0.5)

    print("\n4. Navigation feedback...")
    system.feedback("navigation")
    time.sleep(0.5)

    print("\n5. Progress feedback...")
    for progress in [0.25, 0.5, 0.75, 1.0]:
        print(f"  Progress: {int(progress * 100)}%")
        system.progress_feedback(progress)
        time.sleep(0.3)

    print("\n6. Custom pattern...")
    system.custom_pattern([0.1, 0.05, 0.1, 0.05, 0.1], intensity=0.8)

    print("\n✅ Test complete")
    print("\nNote: Actual haptic feedback requires compatible hardware.")


if __name__ == "__main__":


    main()