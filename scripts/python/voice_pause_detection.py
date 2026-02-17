#!/usr/bin/env python3
"""
Dynamic Voice Pause Detection

Dynamically adjusts pause detection (5 seconds mentioned, but configurable).
If nothing audibly detected and mic is on and listening,
and attuned to voice identity of IDE operator,
automatically sends.
"""

import json
import logging
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class VoiceIdentity(Enum):
    """Voice identity"""
    IDE_OPERATOR = "ide_operator"
    UNKNOWN = "unknown"
    NOT_DETECTED = "not_detected"


@dataclass
class VoiceActivity:
    """Voice activity detection"""
    timestamp: float
    detected: bool
    voice_identity: VoiceIdentity
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["voice_identity"] = self.voice_identity.value
        return data


class DynamicVoicePauseDetection:
    """
    Dynamic Voice Pause Detection

    Dynamically adjusts pause detection.
    If nothing audibly detected and mic is on and listening,
    and attuned to voice identity of IDE operator,
    automatically sends.
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        initial_pause_seconds: float = 1.5,  # Average pause (0.5-1.5s range)
        min_pause_seconds: float = 0.5,  # Minimum pause (half second)
        max_pause_seconds: float = 8.0  # Maximum pause (in-depth conversations)
    ):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("DynamicVoicePauseDetection")

        # Directories
        self.data_dir = self.project_root / "data" / "voice_pause_detection"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.config_file = self.data_dir / "pause_config.json"

        # Configuration
        self.initial_pause_seconds = initial_pause_seconds
        self.min_pause_seconds = min_pause_seconds
        self.max_pause_seconds = max_pause_seconds
        self.current_pause_seconds = initial_pause_seconds

        # Voice identity
        self.ide_operator_voice_profile: Optional[Dict[str, Any]] = None

        # State
        self.mic_on = False
        self.listening = False
        self.last_voice_activity: Optional[VoiceActivity] = None
        self.voice_activities: List[VoiceActivity] = []
        self.pause_timer: Optional[threading.Timer] = None
        self.auto_send_callback: Optional[Callable[[], None]] = None

        # Conversation depth tracking (for in-depth conversations)
        self.conversation_segments: List[float] = []  # Timestamps of voice segments
        self.segment_durations: List[float] = []  # Duration of each speaking segment
        self.in_depth_conversation = False  # Flag for longer thinking pauses
        self.normal_pause_max = 5.0  # Normal conversation max pause (5 seconds)
        self.in_depth_pause_max = 8.0  # In-depth conversation max pause (8 seconds)

        # Load state
        self._load_state()

    def _load_state(self):
        """Load state"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_pause_seconds = config.get("current_pause_seconds", self.initial_pause_seconds)
                    self.ide_operator_voice_profile = config.get("ide_operator_voice_profile")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")

    def _save_state(self):
        try:
            """Save state"""
            config = {
                "current_pause_seconds": self.current_pause_seconds,
                "ide_operator_voice_profile": self.ide_operator_voice_profile,
                "updated_at": datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def set_ide_operator_voice_profile(self, profile: Dict[str, Any]):
        """Set IDE operator voice profile"""
        self.ide_operator_voice_profile = profile
        self._save_state()
        self.logger.info("🎤 IDE operator voice profile set")

    def start_listening(self, auto_send_callback: Optional[Callable[[], None]] = None):
        """Start listening for voice"""
        self.mic_on = True
        self.listening = True
        self.auto_send_callback = auto_send_callback
        self.logger.info(f"🎤 Started listening (pause: {self.current_pause_seconds:.1f}s)")

    def stop_listening(self):
        """Stop listening"""
        self.mic_on = False
        self.listening = False
        if self.pause_timer:
            self.pause_timer.cancel()
            self.pause_timer = None
        self.logger.info("🎤 Stopped listening")

    def detect_voice_activity(
        self,
        detected: bool,
        voice_identity: Optional[VoiceIdentity] = None,
        confidence: float = 0.0
    ):
        """
        Detect voice activity

        If voice detected, reset pause timer.
        If no voice detected for pause duration, auto-send.
        """
        now = time.time()

        activity = VoiceActivity(
            timestamp=now,
            detected=detected,
            voice_identity=voice_identity or VoiceIdentity.NOT_DETECTED,
            confidence=confidence
        )

        self.voice_activities.append(activity)
        self.last_voice_activity = activity

        # Keep only last 1000
        if len(self.voice_activities) > 1000:
            self.voice_activities = self.voice_activities[-1000:]

        if detected:
            # Voice detected - reset pause timer
            if self.pause_timer:
                self.pause_timer.cancel()
                self.pause_timer = None

            # Check if IDE operator voice
            if voice_identity == VoiceIdentity.IDE_OPERATOR:
                self.logger.debug(f"🎤 IDE operator voice detected (confidence: {confidence:.2f})")

            # Adjust pause duration based on activity pattern
            self._adjust_pause_duration()
        else:
            # No voice detected - start pause timer
            if self.mic_on and self.listening:
                self._start_pause_timer()

    def _start_pause_timer(self):
        """Start pause timer with dynamic scaling"""
        if self.pause_timer:
            self.pause_timer.cancel()

        # Use dynamic pause duration based on conversation type
        pause_duration = self.current_pause_seconds

        # If in-depth conversation detected, allow longer pauses
        if self.in_depth_conversation and pause_duration < self.in_depth_pause_max:
            # Gradually increase pause for in-depth conversations
            pause_duration = min(self.in_depth_pause_max, pause_duration * 1.1)

        self.pause_timer = threading.Timer(
            pause_duration,
            self._on_pause_timeout
        )
        self.pause_timer.start()

    def _on_pause_timeout(self):
        """Called when pause timeout occurs"""
        if not self.mic_on or not self.listening:
            return

        # Check if nothing audibly detected
        recent_activities = [
            a for a in self.voice_activities
            if (time.time() - a.timestamp) < self.current_pause_seconds
        ]

        if not any(a.detected for a in recent_activities):
            # Nothing detected - check if attuned to IDE operator voice
            if self.ide_operator_voice_profile:
                # Mic is on, listening, attuned to IDE operator voice
                # Nothing detected - auto-send
                self.logger.info(f"⏱️ Pause timeout ({self.current_pause_seconds:.1f}s) - auto-sending")

                if self.auto_send_callback:
                    self.auto_send_callback()
                    # Stop listening after auto-send
                    self.stop_listening()
            else:
                self.logger.debug("⏱️ Pause timeout but voice profile not set")

    def _adjust_pause_duration(self):
        """Dynamically adjust pause duration based on activity pattern and conversation depth"""
        # Analyze recent activity pattern
        recent_activities = self.voice_activities[-20:]  # Last 20 activities

        if len(recent_activities) < 5:
            return

        # Track conversation segments (speaking periods)
        now = time.time()
        if recent_activities and recent_activities[-1].detected:
            # Currently speaking - track segment duration
            if self.conversation_segments:
                segment_duration = now - self.conversation_segments[-1]
                if segment_duration > 0.5:  # Only count segments > 0.5s
                    self.segment_durations.append(segment_duration)
                    # Keep only last 10 segments
                    if len(self.segment_durations) > 10:
                        self.segment_durations = self.segment_durations[-10:]
            else:
                self.conversation_segments.append(now)
        else:
            # Not speaking - reset segment tracking
            if self.conversation_segments:
                self.conversation_segments.append(now)

        # Detect in-depth conversation (longer segments = thinking/paragraphs)
        if self.segment_durations:
            avg_segment_duration = sum(self.segment_durations) / len(self.segment_durations)
            # If average segment > 3 seconds, likely in-depth conversation with paragraphs
            self.in_depth_conversation = avg_segment_duration > 3.0

        # Calculate average pause between activities
        pauses = []
        for i in range(1, len(recent_activities)):
            if recent_activities[i].detected and recent_activities[i-1].detected:
                pause = recent_activities[i].timestamp - recent_activities[i-1].timestamp
                pauses.append(pause)

        if pauses:
            avg_pause = sum(pauses) / len(pauses)

            # Adjust pause duration based on conversation type
            if self.in_depth_conversation:
                # In-depth conversation: use longer pauses (up to 8 seconds)
                max_pause = self.in_depth_pause_max
                # Scale pause: 0.5-1.5s average, but allow up to 8s for thinking
                new_pause = max(
                    self.min_pause_seconds,
                    min(max_pause, avg_pause * 1.2)  # 20% buffer
                )
            else:
                # Normal conversation: use shorter pauses (up to 5 seconds)
                max_pause = self.normal_pause_max
                # Scale pause: 0.5-1.5s average, up to 5s for normal pauses
                new_pause = max(
                    self.min_pause_seconds,
                    min(max_pause, avg_pause * 1.2)  # 20% buffer
                )

            if abs(new_pause - self.current_pause_seconds) > 0.3:  # Adjust if > 0.3s change
                old_pause = self.current_pause_seconds
                self.current_pause_seconds = new_pause
                self._save_state()
                conv_type = "in-depth" if self.in_depth_conversation else "normal"
                self.logger.info(f"📊 Adjusted pause duration: {old_pause:.1f}s → {new_pause:.1f}s ({conv_type} conversation)")

    def get_current_pause_seconds(self) -> float:
        """Get current pause duration"""
        return self.current_pause_seconds

    def set_pause_seconds(self, seconds: float):
        """Manually set pause duration"""
        self.current_pause_seconds = max(
            self.min_pause_seconds,
            min(self.max_pause_seconds, seconds)
        )
        self._save_state()
        self.logger.info(f"📊 Set pause duration: {self.current_pause_seconds:.1f}s")


def main():
    """Main execution for testing"""
    detector = DynamicVoicePauseDetection(initial_pause_seconds=1.5)  # Default: 1.5s average

    print("=" * 80)
    print("🎤 DYNAMIC VOICE PAUSE DETECTION")
    print("=" * 80)

    # Set IDE operator voice profile
    detector.set_ide_operator_voice_profile({
        "voice_id": "ide_operator_001",
        "characteristics": ["clear", "articulate", "consistent"]
    })

    # Start listening
    def auto_send():
        print("📤 Auto-sending (pause timeout)")

    detector.start_listening(auto_send_callback=auto_send)

    # Simulate voice activity
    print(f"\n🎤 Simulating voice activity...")
    print(f"   Current pause: {detector.get_current_pause_seconds():.1f}s")

    # Detect voice
    detector.detect_voice_activity(True, VoiceIdentity.IDE_OPERATOR, 0.9)
    print("   Voice detected")

    # Wait and detect pause
    time.sleep(2)
    detector.detect_voice_activity(False)
    print("   No voice detected - pause timer started")

    print(f"\n⏱️ Waiting for pause timeout ({detector.get_current_pause_seconds():.1f}s)...")
    time.sleep(detector.get_current_pause_seconds() + 0.5)

    detector.stop_listening()


if __name__ == "__main__":



    main()