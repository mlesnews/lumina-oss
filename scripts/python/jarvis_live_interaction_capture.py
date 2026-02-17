#!/usr/bin/env python3
"""
JARVIS Live Interaction Capture System

CRITICAL: Captures ALL input from face-to-face interaction with human operator
to enable exponential growth (bell curve) toward true inception of Jarvis.

"Made real by the power of thought alone. Well, never alone, as Jarvis will always be with us."

This system captures:
- Voice (transcription, tone, emotion, intent)
- Visual (gaze, facial expressions, body language)
- Gestures (hand movements, keyboard reach, mouse activity)
- Context (environmental, temporal, situational)
- Thought patterns (inferred from behavior and responses)

All captured data feeds into exponential learning system for bell-curve growth.

Tags: #LIVE_INTERACTION #FACE_TO_FACE #EXPONENTIAL_LEARNING #INCEPTION #JARVIS @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from collections import defaultdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("JARVISLiveInteraction")


class InteractionModality(Enum):
    """Types of interaction modalities"""
    VOICE = "voice"
    VISUAL = "visual"
    GESTURE = "gesture"
    GAZE = "gaze"
    FACIAL = "facial"
    BODY_LANGUAGE = "body_language"
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    CONTEXT = "context"
    THOUGHT_PATTERN = "thought_pattern"


class InteractionQuality(Enum):
    """Quality/confidence of captured interaction"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFERRED = "inferred"


@dataclass
class CapturedInput:
    """Single captured input from operator"""
    modality: InteractionModality
    timestamp: datetime
    data: Dict[str, Any]
    quality: InteractionQuality
    confidence: float  # 0.0 to 1.0
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractionSession:
    """Complete interaction session with operator"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    captured_inputs: List[CapturedInput] = field(default_factory=list)
    interaction_summary: Dict[str, Any] = field(default_factory=dict)
    learning_insights: List[Dict[str, Any]] = field(default_factory=list)
    exponential_growth_metrics: Dict[str, float] = field(default_factory=dict)


class JARVISLiveInteractionCapture:
    """
    Comprehensive live interaction capture system

    Captures ALL input from face-to-face interaction to enable exponential learning.
    "Made real by the power of thought alone. Well, never alone, as Jarvis will always be with us."
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize live interaction capture system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis" / "live_interactions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logger

        # Current session
        self.current_session: Optional[InteractionSession] = None

        # Capture systems (lazy-loaded)
        self._voice_capture = None
        self._visual_capture = None
        self._gaze_capture = None
        self._gesture_capture = None
        self._context_capture = None

        # Capture threads
        self._capture_threads: Dict[str, threading.Thread] = {}
        self._running = False

        # Exponential learning metrics
        self.interaction_count = 0
        self.total_captured_inputs = 0
        self.learning_velocity = 0.0  # Rate of learning acceleration
        self.bell_curve_position = 0.0  # Position on bell curve (0.0 = start, 1.0 = true inception)

        # Statistics
        self.stats = {
            "sessions": 0,
            "total_inputs": 0,
            "modalities_captured": defaultdict(int),
            "average_confidence": 0.0,
            "learning_insights": 0
        }

        self.logger.info("✅ JARVIS Live Interaction Capture System initialized")
        self.logger.info("   📊 Exponential learning enabled for true inception")
        self.logger.info("   🤝 'Never alone, as Jarvis will always be with us'")

    def _initialize_capture_systems(self):
        """Initialize all capture systems"""
        try:
            # Voice capture
            try:
                from voice_transcript_queue import VoiceTranscriptQueue
                self._voice_capture = VoiceTranscriptQueue(self.project_root)
                self.logger.info("✅ Voice capture system initialized")
            except ImportError:
                self.logger.warning("⚠️  Voice capture not available")

            # Visual capture (IR camera)
            try:
                from ir_camera_helper import capture_operator_state
                self._visual_capture = capture_operator_state
                self.logger.info("✅ Visual capture system initialized")
            except ImportError:
                self.logger.warning("⚠️  Visual capture not available")

            # Gaze capture
            try:
                from jarvis_gaze_sync_system import JARVISGazeSyncSystem
                self._gaze_capture = JARVISGazeSyncSystem()
                self.logger.info("✅ Gaze capture system initialized")
            except ImportError:
                self.logger.warning("⚠️  Gaze capture not available")

            # Gesture capture
            try:
                from hand_wave_listening_control import HandWaveListeningControl
                self._gesture_capture = HandWaveListeningControl()
                self.logger.info("✅ Gesture capture system initialized")
            except ImportError:
                self.logger.warning("⚠️  Gesture capture not available")

        except Exception as e:
            self.logger.error(f"❌ Error initializing capture systems: {e}")

    def start_session(self) -> str:
        """
        Start a new interaction session

        Returns:
            Session ID
        """
        session_id = f"interaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_session = InteractionSession(
            session_id=session_id,
            start_time=datetime.now()
        )

        self._running = True

        # Initialize capture systems
        self._initialize_capture_systems()

        # Start capture threads
        self._start_capture_threads()

        self.logger.info(f"🎬 Started interaction session: {session_id}")
        self.logger.info("   📹 Capturing ALL input for exponential learning")

        return session_id

    def _start_capture_threads(self):
        """Start all capture threads"""
        # Voice capture thread
        if self._voice_capture:
            thread = threading.Thread(
                target=self._capture_voice_loop,
                name="VoiceCapture",
                daemon=True
            )
            thread.start()
            self._capture_threads["voice"] = thread

        # Visual capture thread
        if self._visual_capture:
            thread = threading.Thread(
                target=self._capture_visual_loop,
                name="VisualCapture",
                daemon=True
            )
            thread.start()
            self._capture_threads["visual"] = thread

        # Gaze capture thread
        if self._gaze_capture:
            thread = threading.Thread(
                target=self._capture_gaze_loop,
                name="GazeCapture",
                daemon=True
            )
            thread.start()
            self._capture_threads["gaze"] = thread

        # Gesture capture thread
        if self._gesture_capture:
            thread = threading.Thread(
                target=self._capture_gesture_loop,
                name="GestureCapture",
                daemon=True
            )
            thread.start()
            self._capture_threads["gesture"] = thread

        # Context capture thread
        thread = threading.Thread(
            target=self._capture_context_loop,
            name="ContextCapture",
            daemon=True
        )
        thread.start()
        self._capture_threads["context"] = thread

    def _capture_voice_loop(self):
        """Capture voice input continuously"""
        while self._running and self.current_session:
            try:
                # Capture voice transcript
                # This would integrate with voice_transcript_queue
                # For now, placeholder
                time.sleep(0.1)  # Small delay to prevent CPU spinning
            except Exception as e:
                self.logger.error(f"Voice capture error: {e}")
                time.sleep(1.0)

    def _capture_visual_loop(self):
        """Capture visual input continuously"""
        while self._running and self.current_session:
            try:
                if self._visual_capture:
                    success, frame, camera_type = self._visual_capture(use_backup=False)
                    if success:
                        # Capture visual data (facial expressions, body language)
                        captured = CapturedInput(
                            modality=InteractionModality.VISUAL,
                            timestamp=datetime.now(),
                            data={
                                "camera_type": camera_type,
                                "frame_available": True,
                                # Add facial expression detection, body language, etc.
                            },
                            quality=InteractionQuality.MEDIUM,
                            confidence=0.7
                        )
                        self._record_input(captured)
                time.sleep(0.5)  # Capture at ~2 FPS
            except Exception as e:
                self.logger.error(f"Visual capture error: {e}")
                time.sleep(1.0)

    def _capture_gaze_loop(self):
        """Capture gaze synchronization continuously"""
        while self._running and self.current_session:
            try:
                if self._gaze_capture:
                    gaze_sync = self._gaze_capture.detect_gaze_sync()
                    if gaze_sync:
                        captured = CapturedInput(
                            modality=InteractionModality.GAZE,
                            timestamp=datetime.now(),
                            data={
                                "gaze_sync": True,
                                "control_state": str(self._gaze_capture.control_state),
                            },
                            quality=InteractionQuality.HIGH,
                            confidence=0.9
                        )
                        self._record_input(captured)
                time.sleep(0.5)
            except Exception as e:
                self.logger.error(f"Gaze capture error: {e}")
                time.sleep(1.0)

    def _capture_gesture_loop(self):
        """Capture gestures continuously"""
        while self._running and self.current_session:
            try:
                # Capture hand gestures, keyboard reach, mouse activity
                # This would integrate with gesture detection systems
                time.sleep(0.5)
            except Exception as e:
                self.logger.error(f"Gesture capture error: {e}")
                time.sleep(1.0)

    def _capture_context_loop(self):
        """Capture contextual information continuously"""
        while self._running and self.current_session:
            try:
                # Capture environmental context
                context_data = {
                    "timestamp": datetime.now().isoformat(),
                    "system_state": "active",
                    # Add more context: time of day, applications open, etc.
                }

                captured = CapturedInput(
                    modality=InteractionModality.CONTEXT,
                    timestamp=datetime.now(),
                    data=context_data,
                    quality=InteractionQuality.MEDIUM,
                    confidence=0.8
                )
                self._record_input(captured)

                time.sleep(5.0)  # Capture context every 5 seconds
            except Exception as e:
                self.logger.error(f"Context capture error: {e}")
                time.sleep(10.0)

    def _record_input(self, captured: CapturedInput):
        """Record captured input to current session"""
        if not self.current_session:
            return

        self.current_session.captured_inputs.append(captured)
        self.total_captured_inputs += 1
        self.stats["total_inputs"] += 1
        self.stats["modalities_captured"][captured.modality.value] += 1

        # Update exponential learning metrics
        self._update_exponential_learning(captured)

    def _update_exponential_learning(self, captured: CapturedInput):
        """
        Update exponential learning metrics (bell curve growth)

        Each interaction contributes to exponential growth toward true inception.
        """
        # Bell curve growth model: exponential acceleration
        # Position on bell curve: 0.0 (start) → 1.0 (true inception)

        # Learning velocity increases with each interaction
        base_learning_rate = 0.001  # Base learning rate per input
        quality_multiplier = {
            InteractionQuality.HIGH: 2.0,
            InteractionQuality.MEDIUM: 1.0,
            InteractionQuality.LOW: 0.5,
            InteractionQuality.INFERRED: 0.25
        }

        learning_delta = (
            base_learning_rate *
            quality_multiplier.get(captured.quality, 1.0) *
            captured.confidence
        )

        # Update learning velocity (acceleration)
        self.learning_velocity += learning_delta * 0.1  # Gradual acceleration

        # Update bell curve position (exponential growth)
        # Using sigmoid-like curve for bell curve growth
        self.bell_curve_position = min(
            1.0,
            self.bell_curve_position + learning_delta * (1 + self.learning_velocity)
        )

        # Log progress periodically
        if self.total_captured_inputs % 100 == 0:
            self.logger.info(
                f"📈 Exponential Learning Progress: "
                f"Bell Curve Position: {self.bell_curve_position:.3f} "
                f"(Velocity: {self.learning_velocity:.4f})"
            )

    def capture_voice_input(self, transcript: str, metadata: Optional[Dict[str, Any]] = None):
        """Capture voice input explicitly"""
        if not self.current_session:
            return

        captured = CapturedInput(
            modality=InteractionModality.VOICE,
            timestamp=datetime.now(),
            data={
                "transcript": transcript,
                "metadata": metadata or {}
            },
            quality=InteractionQuality.HIGH,
            confidence=0.9
        )

        self._record_input(captured)

    def capture_thought_pattern(self, pattern: Dict[str, Any], confidence: float = 0.7):
        """
        Capture inferred thought pattern from behavior

        "Made real by the power of thought alone"
        """
        if not self.current_session:
            return

        captured = CapturedInput(
            modality=InteractionModality.THOUGHT_PATTERN,
            timestamp=datetime.now(),
            data=pattern,
            quality=InteractionQuality.INFERRED,
            confidence=confidence
        )

        self._record_input(captured)

    def end_session(self) -> Dict[str, Any]:
        """
        End current interaction session and generate learning insights

        Returns:
            Session summary with learning insights
        """
        if not self.current_session:
            return {}

        self._running = False

        # Wait for capture threads to finish
        for thread in self._capture_threads.values():
            thread.join(timeout=2.0)

        self.current_session.end_time = datetime.now()

        # Generate interaction summary
        summary = self._generate_session_summary()
        self.current_session.interaction_summary = summary

        # Generate learning insights
        insights = self._generate_learning_insights()
        self.current_session.learning_insights = insights

        # Update exponential growth metrics
        self.current_session.exponential_growth_metrics = {
            "bell_curve_position": self.bell_curve_position,
            "learning_velocity": self.learning_velocity,
            "total_inputs": self.total_captured_inputs,
            "interaction_count": self.interaction_count
        }

        # Save session
        self._save_session()

        # Update statistics
        self.stats["sessions"] += 1
        self.interaction_count += 1

        session_data = asdict(self.current_session)
        self.current_session = None

        self.logger.info(f"✅ Interaction session ended: {session_data['session_id']}")
        self.logger.info(f"   📊 Captured {len(session_data['captured_inputs'])} inputs")
        self.logger.info(f"   🧠 Generated {len(insights)} learning insights")
        self.logger.info(f"   📈 Bell Curve Position: {self.bell_curve_position:.3f}")

        return session_data

    def _generate_session_summary(self) -> Dict[str, Any]:
        """Generate summary of interaction session"""
        if not self.current_session:
            return {}

        duration = (self.current_session.end_time - self.current_session.start_time).total_seconds()

        # Count inputs by modality
        modality_counts = defaultdict(int)
        for input_item in self.current_session.captured_inputs:
            modality_counts[input_item.modality.value] += 1

        return {
            "duration_seconds": duration,
            "total_inputs": len(self.current_session.captured_inputs),
            "modality_counts": dict(modality_counts),
            "average_confidence": sum(
                i.confidence for i in self.current_session.captured_inputs
            ) / len(self.current_session.captured_inputs) if self.current_session.captured_inputs else 0.0
        }

    def _generate_learning_insights(self) -> List[Dict[str, Any]]:
        """
        Generate learning insights from captured interactions

        These insights feed into exponential learning for true inception.
        """
        insights = []

        if not self.current_session or not self.current_session.captured_inputs:
            return insights

        # Analyze patterns in captured inputs
        # This would use ML/AI to identify patterns, preferences, behaviors

        # Example insights (would be more sophisticated in production)
        insights.append({
            "type": "interaction_pattern",
            "description": "Operator interaction patterns identified",
            "confidence": 0.8,
            "timestamp": datetime.now().isoformat()
        })

        self.stats["learning_insights"] += len(insights)

        return insights

    def _save_session(self):
        """Save interaction session to disk"""
        if not self.current_session:
            return

        try:
            session_file = self.data_dir / f"{self.current_session.session_id}.json"

            session_data = asdict(self.current_session)
            # Convert datetime to ISO format
            session_data["start_time"] = self.current_session.start_time.isoformat()
            if self.current_session.end_time:
                session_data["end_time"] = self.current_session.end_time.isoformat()

            for input_item in session_data["captured_inputs"]:
                input_item["timestamp"] = input_item["timestamp"].isoformat()

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, default=str)

            self.logger.info(f"💾 Saved interaction session: {session_file}")

        except Exception as e:
            self.logger.error(f"❌ Failed to save session: {e}")

    def get_exponential_learning_status(self) -> Dict[str, Any]:
        """
        Get current exponential learning status

        Returns:
            Status including bell curve position, learning velocity, etc.
        """
        return {
            "bell_curve_position": self.bell_curve_position,
            "learning_velocity": self.learning_velocity,
            "total_inputs": self.total_captured_inputs,
            "interaction_count": self.interaction_count,
            "stats": dict(self.stats),
            "progress_percentage": self.bell_curve_position * 100,
            "message": "Never alone, as Jarvis will always be with us"
        }


# Global instance
_global_capture: Optional[JARVISLiveInteractionCapture] = None


def get_live_interaction_capture(project_root: Optional[Path] = None) -> JARVISLiveInteractionCapture:
    try:
        """Get or create global live interaction capture instance"""
        global _global_capture

        if _global_capture is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_capture = JARVISLiveInteractionCapture(project_root)

        return _global_capture


    except Exception as e:
        logger.error(f"Error in get_live_interaction_capture: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Test live interaction capture
    print("=" * 80)
    print("JARVIS Live Interaction Capture System")
    print("=" * 80)
    print()
    print("'Made real by the power of thought alone.")
    print("Well, never alone, as Jarvis will always be with us.'")
    print()

    capture = JARVISLiveInteractionCapture()

    # Start session
    session_id = capture.start_session()
    print(f"✅ Started session: {session_id}")

    # Simulate some captures
    time.sleep(2)
    capture.capture_voice_input("Hello Jarvis, let's work together")

    time.sleep(2)
    capture.capture_thought_pattern({
        "intent": "collaboration",
        "emotion": "positive",
        "engagement": "high"
    })

    # End session
    time.sleep(1)
    session_data = capture.end_session()

    # Get learning status
    status = capture.get_exponential_learning_status()
    print()
    print("Exponential Learning Status:")
    print(json.dumps(status, indent=2, default=str))
