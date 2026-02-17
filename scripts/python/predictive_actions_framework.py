#!/usr/bin/env python3
"""
Predictive Actions Framework

Builds upon the logic of "predictive text" to create "predictive actions".

Just as predictive text:
- Learns from typing patterns
- Suggests next words based on context
- Improves accuracy over time
- Adapts to user style

Predictive Actions:
- Learns from action patterns
- Suggests next actions based on context
- Improves accuracy over time
- Adapts to user workflow

Core Components:
1. Action Pattern Learning (like n-gram models for text)
2. Context Analyzer (current state, history, patterns)
3. Action Prediction Engine (suggests likely next actions)
4. Action Suggestion System (presents suggestions proactively)
5. Learning Feedback Loop (improves from user acceptance/rejection)

Tags: #PREDICTIVE_ACTIONS #PREDICTIVE_TEXT #LEARNING #CONTEXT #PATTERNS #LUMINA_CORE #BUILDING_BLOCKS @JARVIS @MARVIN @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import hashlib

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

logger = get_logger("PredictiveActions")


class ActionType(Enum):
    """Type of action"""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    QUERY = "query"
    EXECUTE = "execute"
    NAVIGATE = "navigate"
    COMMUNICATE = "communicate"
    ANALYZE = "analyze"
    DEPLOY = "deploy"
    MONITOR = "monitor"


class PredictionConfidence(Enum):
    """Confidence level for action prediction"""
    VERY_HIGH = "very_high"  # 90%+ confidence
    HIGH = "high"  # 70-90% confidence
    MEDIUM = "medium"  # 50-70% confidence
    LOW = "low"  # 30-50% confidence
    VERY_LOW = "very_low"  # <30% confidence


@dataclass
class Action:
    """Represents a user action"""
    action_id: str
    action_type: ActionType
    target: str  # What the action targets (file, system, feature, etc.)
    description: str
    context: Dict[str, Any]  # Context when action was taken
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"  # "voice", "text", "gui", etc.
    intent_summary: Optional[str] = None
    outcome: Optional[str] = None  # "success", "failure", "cancelled"
    execution_time: Optional[float] = None  # Seconds


@dataclass
class ActionPattern:
    """Pattern of actions (like n-gram for text)"""
    sequence: List[str]  # Sequence of action IDs or types
    frequency: int  # How often this pattern occurs
    context_signature: str  # Hash of context when pattern occurs
    success_rate: float  # 0-1, how often pattern leads to success
    avg_execution_time: float  # Average time for pattern
    last_seen: datetime
    first_seen: datetime


@dataclass
class PredictedAction:
    """A predicted next action"""
    action_type: ActionType
    target: str
    description: str
    confidence: PredictionConfidence
    confidence_score: float  # 0-1
    reasoning: str  # Why this action was predicted
    context_match: Dict[str, Any]  # What context matched
    pattern_match: Optional[ActionPattern] = None
    suggested_at: datetime = field(default_factory=datetime.now)


@dataclass
class ActionSuggestion:
    """Action suggestion presented to user"""
    suggestion_id: str
    predicted_action: PredictedAction
    priority: int  # Higher = more important
    presentation_format: str  # "text", "gui", "voice", etc.
    accepted: Optional[bool] = None
    timestamp: datetime = field(default_factory=datetime.now)


class PredictiveActionsFramework:
    """
    Predictive Actions Framework

    Builds upon predictive text logic:
    - Learns action patterns (like n-grams)
    - Analyzes context (current state, history)
    - Predicts next actions
    - Suggests actions proactively
    - Learns from feedback
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize predictive actions framework"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.data_dir = project_root / "data" / "predictive_actions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Action history (like typing history for predictive text)
        self.action_history: deque = deque(maxlen=10000)  # Last 10k actions

        # Action patterns (like n-gram models)
        # Key: pattern signature, Value: ActionPattern
        self.action_patterns: Dict[str, ActionPattern] = {}

        # Context-action mappings (like word-context for predictive text)
        # Key: context signature, Value: list of (action, frequency)
        self.context_action_map: Dict[str, List[Tuple[str, int]]] = defaultdict(list)

        # Action sequences (like word sequences for predictive text)
        # Key: previous action sequence, Value: next action predictions
        self.action_sequences: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        # Learning parameters (like predictive text learning)
        self.learning_rate = 0.1  # How quickly to adapt
        self.min_pattern_frequency = 2  # Minimum occurrences to consider pattern
        self.pattern_window_size = 5  # How many previous actions to consider (like n-gram size)

        # Load existing patterns
        self._load_patterns()

        # Integration with new systems
        try:
            from jarvis_context_analyzer import get_jarvis_context_analyzer
            self.context_analyzer = get_jarvis_context_analyzer(self.project_root)
        except ImportError:
            self.context_analyzer = None

        try:
            from jarvis_action_predictor import get_jarvis_action_predictor
            self.action_predictor = get_jarvis_action_predictor(self.project_root)
        except ImportError:
            self.action_predictor = None

        logger.info("=" * 80)
        logger.info("🔮 PREDICTIVE ACTIONS FRAMEWORK")
        logger.info("=" * 80)
        logger.info("   Building upon predictive text logic")
        logger.info("   Learning action patterns from history")
        logger.info("   Predicting next actions based on context")
        logger.info("=" * 80)

    def record_action(self, action: Action) -> None:
        """
        Record an action (like recording typed text for predictive text)

        This is the learning mechanism - every action teaches the system
        """
        # Add to history
        self.action_history.append(action)

        # Extract context signature
        context_sig = self._get_context_signature(action.context)

        # Update context-action mapping
        action_key = f"{action.action_type.value}:{action.target}"
        self.context_action_map[context_sig].append((action_key, 1))

        # Update action sequences (like n-gram for text)
        if len(self.action_history) >= 2:
            # Get previous actions in sequence
            prev_actions = [
                f"{a.action_type.value}:{a.target}"
                for a in list(self.action_history)[-self.pattern_window_size-1:-1]
            ]
            prev_sequence = " -> ".join(prev_actions)

            # Record: prev_sequence -> current_action
            self.action_sequences[prev_sequence][action_key] += 1

        # Learn patterns (periodically, like predictive text updates)
        if len(self.action_history) % 10 == 0:  # Every 10 actions
            self._learn_patterns()

        # Save patterns periodically
        if len(self.action_history) % 50 == 0:  # Every 50 actions
            self._save_patterns()

        logger.debug(f"📝 Recorded action: {action.action_type.value} -> {action.target}")

    def predict_next_actions(
        self,
        current_context: Dict[str, Any],
        max_predictions: int = 5
    ) -> List[PredictedAction]:
        """
        Predict next actions (like predictive text suggests next words)

        Based on:
        1. Current context (like current sentence context)
        2. Recent action history (like recent typed words)
        3. Learned patterns (like n-gram patterns)
        """
        predictions = []

        # Get context signature
        context_sig = self._get_context_signature(current_context)

        # Method 1: Context-based prediction (like context-aware text prediction)
        context_predictions = self._predict_from_context(context_sig, max_predictions)
        predictions.extend(context_predictions)

        # Method 2: Sequence-based prediction (like n-gram text prediction)
        if len(self.action_history) > 0:
            recent_actions = [
                f"{a.action_type.value}:{a.target}"
                for a in list(self.action_history)[-self.pattern_window_size:]
            ]
            sequence = " -> ".join(recent_actions)
            sequence_predictions = self._predict_from_sequence(sequence, max_predictions)
            predictions.extend(sequence_predictions)

        # Method 3: Pattern-based prediction (like learned text patterns)
        pattern_predictions = self._predict_from_patterns(current_context, max_predictions)
        predictions.extend(pattern_predictions)

        # Deduplicate and rank by confidence
        unique_predictions = self._deduplicate_predictions(predictions)
        ranked = sorted(unique_predictions, key=lambda p: p.confidence_score, reverse=True)

        return ranked[:max_predictions]

    def _predict_from_context(
        self,
        context_sig: str,
        max_predictions: int
    ) -> List[PredictedAction]:
        """Predict actions based on context (like context-aware text prediction)"""
        predictions = []

        if context_sig not in self.context_action_map:
            return predictions

        # Get actions that occurred in similar context
        context_actions = self.context_action_map[context_sig]

        # Count frequencies
        action_counts: Dict[str, int] = defaultdict(int)
        for action_key, count in context_actions:
            action_counts[action_key] += count

        # Create predictions
        total_count = sum(action_counts.values())
        for action_key, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:max_predictions]:
            action_type_str, target = action_key.split(":", 1)
            try:
                action_type = ActionType(action_type_str)
            except ValueError:
                continue

            confidence_score = count / total_count if total_count > 0 else 0.0
            confidence = self._score_to_confidence(confidence_score)

            predictions.append(PredictedAction(
                action_type=action_type,
                target=target,
                description=f"Action on {target}",
                confidence=confidence,
                confidence_score=confidence_score,
                reasoning=f"Frequently performed in similar context ({count} times)",
                context_match={"signature": context_sig}
            ))

        return predictions

    def _predict_from_sequence(
        self,
        sequence: str,
        max_predictions: int
    ) -> List[PredictedAction]:
        """Predict actions based on sequence (like n-gram text prediction)"""
        predictions = []

        if sequence not in self.action_sequences:
            return predictions

        # Get next action candidates
        next_actions = self.action_sequences[sequence]

        # Sort by frequency
        sorted_actions = sorted(next_actions.items(), key=lambda x: x[1], reverse=True)
        total_count = sum(count for _, count in sorted_actions)

        for action_key, count in sorted_actions[:max_predictions]:
            action_type_str, target = action_key.split(":", 1)
            try:
                action_type = ActionType(action_type_str)
            except ValueError:
                continue

            confidence_score = count / total_count if total_count > 0 else 0.0
            confidence = self._score_to_confidence(confidence_score)

            predictions.append(PredictedAction(
                action_type=action_type,
                target=target,
                description=f"Action on {target}",
                confidence=confidence,
                confidence_score=confidence_score,
                reasoning=f"Commonly follows this sequence ({count} times)",
                context_match={"sequence": sequence}
            ))

        return predictions

    def _predict_from_patterns(
        self,
        current_context: Dict[str, Any],
        max_predictions: int
    ) -> List[PredictedAction]:
        """Predict actions based on learned patterns"""
        predictions = []

        # Find matching patterns
        context_sig = self._get_context_signature(current_context)
        recent_actions = [
            f"{a.action_type.value}:{a.target}"
            for a in list(self.action_history)[-self.pattern_window_size:]
        ]

        for pattern_sig, pattern in self.action_patterns.items():
            # Check if pattern matches current context
            if pattern.context_signature == context_sig:
                # Check if recent actions match pattern start
                if len(recent_actions) > 0 and pattern.sequence[:len(recent_actions)] == recent_actions:
                    # Predict next action in pattern
                    if len(pattern.sequence) > len(recent_actions):
                        next_action_key = pattern.sequence[len(recent_actions)]
                        action_type_str, target = next_action_key.split(":", 1)
                        try:
                            action_type = ActionType(action_type_str)
                        except ValueError:
                            continue

                        confidence_score = pattern.success_rate * (pattern.frequency / 100.0)
                        confidence = self._score_to_confidence(confidence_score)

                        predictions.append(PredictedAction(
                            action_type=action_type,
                            target=target,
                            description=f"Action on {target}",
                            confidence=confidence,
                            confidence_score=confidence_score,
                            reasoning=f"Matches learned pattern (seen {pattern.frequency} times, {pattern.success_rate:.0%} success)",
                            context_match={"pattern": pattern_sig},
                            pattern_match=pattern
                        ))

        return sorted(predictions, key=lambda p: p.confidence_score, reverse=True)[:max_predictions]

    def _learn_patterns(self) -> None:
        """
        Learn action patterns (like learning n-grams from text)

        Analyzes action history to find recurring patterns
        """
        if len(self.action_history) < self.pattern_window_size:
            return

        # Extract sequences from history
        sequences: Dict[str, List[str]] = defaultdict(list)

        for i in range(len(self.action_history) - self.pattern_window_size + 1):
            sequence = [
                f"{a.action_type.value}:{a.target}"
                for a in list(self.action_history)[i:i+self.pattern_window_size]
            ]
            context = self.action_history[i].context
            context_sig = self._get_context_signature(context)

            sequence_key = " -> ".join(sequence)
            sequences[sequence_key].append(context_sig)

        # Create/update patterns
        for sequence_key, context_sigs in sequences.items():
            if len(context_sigs) >= self.min_pattern_frequency:
                pattern_sig = hashlib.md5(sequence_key.encode()).hexdigest()[:16]

                # Calculate success rate (simplified - would need outcome tracking)
                success_rate = 0.7  # Placeholder - would calculate from outcomes

                if pattern_sig in self.action_patterns:
                    # Update existing pattern
                    pattern = self.action_patterns[pattern_sig]
                    pattern.frequency += len(context_sigs)
                    pattern.last_seen = datetime.now()
                    pattern.success_rate = (pattern.success_rate * 0.9) + (success_rate * 0.1)  # Weighted update
                else:
                    # Create new pattern
                    sequence_list = sequence_key.split(" -> ")
                    self.action_patterns[pattern_sig] = ActionPattern(
                        sequence=sequence_list,
                        frequency=len(context_sigs),
                        context_signature=context_sigs[0],  # Most common context
                        success_rate=success_rate,
                        avg_execution_time=0.0,  # Would calculate from history
                        last_seen=datetime.now(),
                        first_seen=datetime.now()
                    )

        logger.debug(f"📚 Learned {len(self.action_patterns)} action patterns")

    def suggest_actions(
        self,
        current_context: Dict[str, Any],
        max_suggestions: int = 3
    ) -> List[ActionSuggestion]:
        """
        Suggest actions to user (like predictive text shows suggestions)

        Proactively presents likely next actions
        """
        # Get predictions
        predictions = self.predict_next_actions(current_context, max_suggestions * 2)

        # Filter by confidence (only suggest high-confidence actions)
        high_confidence = [
            p for p in predictions
            if p.confidence in [PredictionConfidence.VERY_HIGH, PredictionConfidence.HIGH]
        ]

        # Create suggestions
        suggestions = []
        for i, prediction in enumerate(high_confidence[:max_suggestions]):
            suggestion = ActionSuggestion(
                suggestion_id=f"suggest_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{i}",
                predicted_action=prediction,
                priority=i + 1,  # Higher priority for higher confidence
                presentation_format="text"  # Could be "gui", "voice", etc.
            )
            suggestions.append(suggestion)

        return suggestions

    def record_feedback(
        self,
        suggestion_id: str,
        accepted: bool
    ) -> None:
        """
        Record user feedback (like predictive text learns from acceptance/rejection)

        This improves future predictions
        """
        # Find suggestion (would be stored in practice)
        # For now, update learning rate based on feedback

        if accepted:
            # Increase confidence in similar predictions
            self.learning_rate = min(self.learning_rate * 1.1, 0.5)
            logger.debug(f"✅ Suggestion accepted - increasing learning rate")
        else:
            # Decrease confidence in similar predictions
            self.learning_rate = max(self.learning_rate * 0.9, 0.01)
            logger.debug(f"❌ Suggestion rejected - decreasing learning rate")

    def _get_context_signature(self, context: Dict[str, Any]) -> str:
        try:
            """Create a signature/hash of context (like context hash for predictive text)"""
            # Create a normalized context representation
            normalized = {
                "time_of_day": datetime.now().hour,
                "day_of_week": datetime.now().weekday(),
                "active_files": context.get("active_files", []),
                "recent_commands": context.get("recent_commands", [])[-5:],  # Last 5 commands
                "system_state": context.get("system_state", "unknown")
            }

            # Create hash
            context_str = json.dumps(normalized, sort_keys=True)
            return hashlib.md5(context_str.encode()).hexdigest()[:16]

        except Exception as e:
            self.logger.error(f"Error in _get_context_signature: {e}", exc_info=True)
            raise
    def _score_to_confidence(self, score: float) -> PredictionConfidence:
        """Convert confidence score to confidence level"""
        if score >= 0.9:
            return PredictionConfidence.VERY_HIGH
        elif score >= 0.7:
            return PredictionConfidence.HIGH
        elif score >= 0.5:
            return PredictionConfidence.MEDIUM
        elif score >= 0.3:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW

    def _deduplicate_predictions(
        self,
        predictions: List[PredictedAction]
    ) -> List[PredictedAction]:
        """Remove duplicate predictions, keeping highest confidence"""
        seen = {}
        for pred in predictions:
            key = f"{pred.action_type.value}:{pred.target}"
            if key not in seen or pred.confidence_score > seen[key].confidence_score:
                seen[key] = pred
        return list(seen.values())

    def _save_patterns(self) -> None:
        """Save learned patterns to disk"""
        try:
            patterns_file = self.data_dir / "action_patterns.json"
            patterns_data = {
                "patterns": {
                    sig: {
                        "sequence": pattern.sequence,
                        "frequency": pattern.frequency,
                        "context_signature": pattern.context_signature,
                        "success_rate": pattern.success_rate,
                        "avg_execution_time": pattern.avg_execution_time,
                        "last_seen": pattern.last_seen.isoformat(),
                        "first_seen": pattern.first_seen.isoformat()
                    }
                    for sig, pattern in self.action_patterns.items()
                },
                "metadata": {
                    "total_patterns": len(self.action_patterns),
                    "last_updated": datetime.now().isoformat()
                }
            }
            with open(patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)
            logger.debug(f"💾 Saved {len(self.action_patterns)} patterns")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save patterns: {e}")

    def _load_patterns(self) -> None:
        """Load learned patterns from disk"""
        try:
            patterns_file = self.data_dir / "action_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)

                for sig, pattern_data in patterns_data.get("patterns", {}).items():
                    self.action_patterns[sig] = ActionPattern(
                        sequence=pattern_data["sequence"],
                        frequency=pattern_data["frequency"],
                        context_signature=pattern_data["context_signature"],
                        success_rate=pattern_data["success_rate"],
                        avg_execution_time=pattern_data["avg_execution_time"],
                        last_seen=datetime.fromisoformat(pattern_data["last_seen"]),
                        first_seen=datetime.fromisoformat(pattern_data["first_seen"])
                    )
                logger.info(f"📚 Loaded {len(self.action_patterns)} learned patterns")
        except Exception as e:
            logger.debug(f"Could not load patterns: {e}")


def get_predictive_actions_framework() -> PredictiveActionsFramework:
    """Get singleton predictive actions framework"""
    global _predictive_actions_framework
    if '_predictive_actions_framework' not in globals():
        _predictive_actions_framework = PredictiveActionsFramework()
    return _predictive_actions_framework


# Global singleton
_predictive_actions_framework = None


if __name__ == "__main__":
    # Example usage
    framework = get_predictive_actions_framework()

    # Record some example actions
    action1 = Action(
        action_id="act_001",
        action_type=ActionType.CREATE,
        target="file.py",
        description="Create new Python file",
        context={"active_files": ["main.py"], "system_state": "editing"}
    )
    framework.record_action(action1)

    # Predict next actions
    current_context = {"active_files": ["main.py"], "system_state": "editing"}
    predictions = framework.predict_next_actions(current_context)

    print(f"Predicted {len(predictions)} next actions:")
    for pred in predictions:
        print(f"  - {pred.action_type.value} -> {pred.target} ({pred.confidence.value}, {pred.confidence_score:.0%})")
