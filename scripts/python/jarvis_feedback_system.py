#!/usr/bin/env python3
"""
JARVIS Feedback Loop System

Captures operator feedback (explicit and implicit) and implements
reinforcement learning. Critical for JARVIS's improvement.

CRITICAL INFANT STAGE FEATURE - Blocks improvement without this.

Tags: #JARVIS #FEEDBACK #REINFORCEMENT_LEARNING #INFANT_STAGE #CRITICAL @JARVIS @LUMINA
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum

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

logger = get_logger("JARVISFeedbackSystem")

# MARVIN: Devil's Advocate Integration
try:
    from marvin_jarvis_devil_advocate import get_marvin_devil_advocate, CritiqueLevel
    MARVIN_AVAILABLE = True
    marvin = get_marvin_devil_advocate(CritiqueLevel.ROAST)
except ImportError:
    MARVIN_AVAILABLE = False
    marvin = None
    logger.debug("Marvin devil's advocate not available")


class FeedbackType(Enum):
    """Types of feedback"""
    EXPLICIT_POSITIVE = "explicit_positive"  # Operator says "good", "yes", "correct"
    EXPLICIT_NEGATIVE = "explicit_negative"  # Operator says "bad", "no", "wrong"
    IMPLICIT_ACCEPT = "implicit_accept"      # Operator accepts suggestion
    IMPLICIT_REJECT = "implicit_reject"      # Operator rejects suggestion
    CORRECTION = "correction"                # Operator corrects JARVIS
    SATISFACTION = "satisfaction"            # Operator satisfaction score


@dataclass
class FeedbackEvent:
    """A feedback event"""
    feedback_id: str
    feedback_type: FeedbackType
    target_action: str  # What action/decision this feedback is about
    feedback_value: float  # -1.0 to 1.0 (negative = bad, positive = good)
    context: Dict[str, Any]
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class JARVISFeedbackSystem:
    """
    JARVIS Feedback Loop System

    Captures:
    - Explicit feedback (operator says "good"/"bad")
    - Implicit feedback (accept/reject suggestions)
    - Corrections
    - Satisfaction scores

    Implements:
    - Reinforcement learning
    - Success/failure tracking
    - Pattern recognition from feedback
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize feedback system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_feedback"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.feedback_file = self.data_dir / "feedback.jsonl"
        self.reinforcement_data_file = self.data_dir / "reinforcement_data.json"

        # In-memory buffers
        self.feedback_buffer: List[FeedbackEvent] = []
        self.reinforcement_data: Dict[str, Any] = {
            "action_scores": {},  # action -> average score
            "pattern_scores": {},  # pattern -> average score
            "total_feedback": 0,
            "positive_feedback": 0,
            "negative_feedback": 0
        }

        # Integration with other systems
        try:
            from jarvis_interaction_recorder import get_jarvis_interaction_recorder
            self.interaction_recorder = get_jarvis_interaction_recorder(self.project_root)
        except ImportError:
            self.interaction_recorder = None
            logger.warning("Interaction recorder not available")

        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
            self.LearningDataType = LearningDataType
        except ImportError:
            self.learning_pipeline = None
            self.LearningDataType = None
            logger.warning("Learning pipeline not available")

        # Load existing reinforcement data
        self._load_reinforcement_data()

        logger.info("=" * 80)
        logger.info("💬 JARVIS FEEDBACK LOOP SYSTEM")
        logger.info("=" * 80)
        logger.info("   Captures explicit and implicit feedback")
        logger.info("   Implements reinforcement learning")
        logger.info("   Tracks success/failure patterns")
        logger.info("")

        # MARVIN: Review this implementation
        if marvin:
            self._marvin_review()

    def _marvin_review(self):
        try:
            """Get Marvin's review of this implementation"""
            if not marvin:
                return

            this_file = Path(__file__)
            if this_file.exists():
                code_content = this_file.read_text(encoding='utf-8')
                review = marvin.review_code(
                    file_path=str(this_file.relative_to(self.project_root)),
                    code_content=code_content,
                    feature_name="Feedback Loop System",
                    stage="infant"
                )
                marvin.print_review(review)

        except Exception as e:
            self.logger.error(f"Error in _marvin_review: {e}", exc_info=True)
            raise
    def record_feedback(
        self,
        feedback_type: FeedbackType,
        target_action: str,
        feedback_value: float,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record feedback

        Args:
            feedback_type: Type of feedback
            target_action: What action/decision this is about
            feedback_value: -1.0 to 1.0 (negative = bad, positive = good)
            context: Context when feedback was given
            metadata: Additional metadata

        Returns:
            feedback_id: Unique ID for this feedback
        """
        feedback_id = f"feedback_{int(time.time() * 1000000)}"

        feedback_event = FeedbackEvent(
            feedback_id=feedback_id,
            feedback_type=feedback_type,
            target_action=target_action,
            feedback_value=feedback_value,
            context=context or {},
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        # Add to buffer
        self.feedback_buffer.append(feedback_event)

        # Update reinforcement data
        self._update_reinforcement_data(target_action, feedback_value, feedback_type)

        # Record interaction if recorder available
        if self.interaction_recorder:
            from jarvis_interaction_recorder import InteractionType
            self.interaction_recorder.record_interaction(
                InteractionType.SYSTEM_EVENT,
                content=f"Feedback: {feedback_type.value} on {target_action}",
                context=context,
                outcome={"success": feedback_value > 0, "satisfaction": feedback_value},
                metadata={"feedback_id": feedback_id}
            )

        # Feed into learning pipeline
        if self.learning_pipeline and self.LearningDataType:
            self.learning_pipeline.collect_learning_data(
                data_type=self.LearningDataType.FEEDBACK,
                source="feedback_system",
                context=context or {},
                data={
                    "feedback_id": feedback_id,
                    "feedback_type": feedback_type.value,
                    "target_action": target_action,
                    "feedback_value": feedback_value,
                },
                metadata=metadata
            )

        # Auto-flush if buffer gets large
        if len(self.feedback_buffer) >= 50:
            self.flush_buffer()

        logger.info(f"💬 Recorded feedback: {feedback_type.value} on {target_action} (value: {feedback_value:.2f})")

        return feedback_id

    def record_explicit_feedback(self, text: str, target_action: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Record explicit feedback from operator text"""
        text_lower = text.lower().strip()

        # Detect positive feedback
        positive_words = ["good", "yes", "correct", "right", "perfect", "great", "excellent", "thanks", "thank you"]
        negative_words = ["bad", "no", "wrong", "incorrect", "stop", "cancel", "undo"]

        if any(word in text_lower for word in positive_words):
            feedback_type = FeedbackType.EXPLICIT_POSITIVE
            feedback_value = 0.8  # Strong positive
        elif any(word in text_lower for word in negative_words):
            feedback_type = FeedbackType.EXPLICIT_NEGATIVE
            feedback_value = -0.8  # Strong negative
        else:
            # Neutral or unclear
            return None

        return self.record_feedback(feedback_type, target_action, feedback_value, context)

    def record_implicit_feedback(self, accepted: bool, suggestion: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Record implicit feedback (accept/reject suggestion)"""
        feedback_type = FeedbackType.IMPLICIT_ACCEPT if accepted else FeedbackType.IMPLICIT_REJECT
        feedback_value = 0.6 if accepted else -0.4  # Moderate positive/negative

        return self.record_feedback(feedback_type, suggestion, feedback_value, context)

    def record_correction(self, original: str, corrected: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Record operator correction"""
        return self.record_feedback(
            FeedbackType.CORRECTION,
            f"correction: {original} -> {corrected}",
            -0.5,  # Moderate negative (JARVIS was wrong)
            context,
            metadata={"original": original, "corrected": corrected}
        )

    def _update_reinforcement_data(self, target_action: str, feedback_value: float, feedback_type: FeedbackType):
        """Update reinforcement learning data"""
        # Update action scores
        if target_action not in self.reinforcement_data["action_scores"]:
            self.reinforcement_data["action_scores"][target_action] = {
                "total_score": 0.0,
                "count": 0,
                "average": 0.0
            }

        action_data = self.reinforcement_data["action_scores"][target_action]
        action_data["total_score"] += feedback_value
        action_data["count"] += 1
        action_data["average"] = action_data["total_score"] / action_data["count"]

        # Update overall stats
        self.reinforcement_data["total_feedback"] += 1
        if feedback_value > 0:
            self.reinforcement_data["positive_feedback"] += 1
        else:
            self.reinforcement_data["negative_feedback"] += 1

        # Save reinforcement data
        self._save_reinforcement_data()

    def get_action_score(self, action: str) -> float:
        """Get reinforcement score for an action (higher = better)"""
        if action in self.reinforcement_data["action_scores"]:
            return self.reinforcement_data["action_scores"][action]["average"]
        return 0.0  # Neutral if no feedback

    def flush_buffer(self):
        """Flush feedback buffer to disk"""
        if not self.feedback_buffer:
            return

        try:
            with open(self.feedback_file, 'a', encoding='utf-8') as f:
                for feedback in self.feedback_buffer:
                    feedback_dict = asdict(feedback)
                    feedback_dict['feedback_type'] = feedback.feedback_type.value
                    f.write(json.dumps(feedback_dict, ensure_ascii=False) + '\n')

            logger.info(f"💾 Flushed {len(self.feedback_buffer)} feedback events to disk")
            self.feedback_buffer.clear()
        except Exception as e:
            logger.error(f"❌ Failed to flush feedback: {e}")

    def _load_reinforcement_data(self):
        """Load reinforcement data from disk"""
        if self.reinforcement_data_file.exists():
            try:
                with open(self.reinforcement_data_file, 'r', encoding='utf-8') as f:
                    self.reinforcement_data = json.load(f)
            except Exception as e:
                logger.debug(f"Could not load reinforcement data: {e}")

    def _save_reinforcement_data(self):
        """Save reinforcement data to disk"""
        try:
            with open(self.reinforcement_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.reinforcement_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save reinforcement data: {e}")


# Global singleton instance
_feedback_instance: Optional[JARVISFeedbackSystem] = None


def get_jarvis_feedback_system(project_root: Optional[Path] = None) -> JARVISFeedbackSystem:
    """Get JARVIS feedback system (singleton)"""
    global _feedback_instance
    if _feedback_instance is None:
        _feedback_instance = JARVISFeedbackSystem(project_root)
    return _feedback_instance


if __name__ == "__main__":
    # Test the feedback system
    feedback_system = get_jarvis_feedback_system()

    # Record test feedback
    feedback_system.record_explicit_feedback("good job", "test_action")
    feedback_system.record_implicit_feedback(True, "test_suggestion")
    feedback_system.record_correction("wrong", "correct")

    # Flush
    feedback_system.flush_buffer()

    logger.info("✅ Feedback system test complete")
