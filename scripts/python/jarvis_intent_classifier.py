#!/usr/bin/env python3
"""
JARVIS Intent Classification System

Classifies operator intent from voice/text with high accuracy.
Multi-intent detection, confidence scoring, intent-to-action mapping.

CRITICAL TODDLER STAGE FEATURE.

Tags: #JARVIS #INTENT #CLASSIFICATION #TODDLER_STAGE #CRITICAL @JARVIS @LUMINA
"""

import sys
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
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

logger = get_logger("JARVISIntentClassifier")

# MARVIN: Devil's Advocate Integration
try:
    from marvin_jarvis_devil_advocate import get_marvin_devil_advocate, CritiqueLevel
    MARVIN_AVAILABLE = True
    marvin = get_marvin_devil_advocate(CritiqueLevel.ROAST)
except ImportError:
    MARVIN_AVAILABLE = False
    marvin = None
    logger.debug("Marvin devil's advocate not available")


class IntentType(Enum):
    """Types of intents"""
    COMMAND = "command"           # Do something
    QUESTION = "question"         # Ask something
    FEEDBACK = "feedback"         # Give feedback
    CORRECTION = "correction"     # Correct something
    REQUEST = "request"           # Request something
    MULTIPLE = "multiple"         # Multiple intents


@dataclass
class Intent:
    """A classified intent"""
    intent_id: str
    intent_type: IntentType
    text: str
    confidence: float  # 0.0 to 1.0
    entities: Dict[str, Any] = field(default_factory=dict)
    action: Optional[str] = None  # Suggested action
    metadata: Dict[str, Any] = field(default_factory=dict)


class JARVISIntentClassifier:
    """
    JARVIS Intent Classification System

    Classifies:
    - Operator intent from voice/text
    - Multi-intent detection
    - Intent confidence scoring
    - Intent-to-action mapping
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize intent classifier"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_intents"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.intents_file = self.data_dir / "intents.jsonl"
        self.action_mappings_file = self.data_dir / "action_mappings.json"

        # Intent patterns (can be enhanced with ML)
        self.intent_patterns = {
            IntentType.COMMAND: [
                r"^(do|make|create|build|run|start|stop|execute|implement)",
                r"^(please|can you|could you)",
                r"^(let's|let me)",
            ],
            IntentType.QUESTION: [
                r"\?$",
                r"^(what|how|why|when|where|who|which)",
                r"^(is|are|can|could|should|would)",
            ],
            IntentType.FEEDBACK: [
                r"^(good|bad|yes|no|correct|wrong|perfect|great)",
                r"^(thanks|thank you|appreciate)",
            ],
            IntentType.CORRECTION: [
                r"^(no|wrong|incorrect|actually|instead)",
                r"^(should be|meant to|supposed to)",
            ],
            IntentType.REQUEST: [
                r"^(please|can you|could you|would you)",
                r"^(I need|I want|I'd like)",
            ],
        }

        # Action mappings (intent -> action)
        self.action_mappings = {
            "create": "create_file",
            "build": "build_system",
            "run": "execute_script",
            "start": "start_process",
            "stop": "stop_process",
            "implement": "implement_feature",
        }

        # Load existing action mappings
        self._load_action_mappings()

        # Integration with context analyzer
        try:
            from jarvis_context_analyzer import get_jarvis_context_analyzer
            self.context_analyzer = get_jarvis_context_analyzer(self.project_root)
        except ImportError:
            self.context_analyzer = None
            logger.warning("Context analyzer not available")

        # Integration with learning pipeline
        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
            self.LearningDataType = LearningDataType
        except ImportError:
            self.learning_pipeline = None
            self.LearningDataType = None

        logger.info("=" * 80)
        logger.info("🎯 JARVIS INTENT CLASSIFIER")
        logger.info("=" * 80)
        logger.info("   Classifies operator intent from voice/text")
        logger.info("   Multi-intent detection")
        logger.info("   Intent-to-action mapping")
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
                    feature_name="Intent Classifier",
                    stage="toddler"
                )
                marvin.print_review(review)

        except Exception as e:
            self.logger.error(f"Error in _marvin_review: {e}", exc_info=True)
            raise
    def classify_intent(self, text: str, context: Optional[Dict[str, Any]] = None) -> Intent:
        """
        Classify intent from text

        Args:
            text: Input text
            context: Optional context

        Returns:
            Intent: Classified intent
        """
        text_lower = text.lower().strip()
        intent_id = f"intent_{int(time.time() * 1000000)}"

        # Detect intents
        detected_intents = []
        intent_scores = {}

        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            matches = 0
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matches += 1
                    score += 0.3

            if matches > 0:
                detected_intents.append(intent_type)
                intent_scores[intent_type] = min(score, 1.0)

        # Determine primary intent
        if len(detected_intents) > 1:
            primary_intent = IntentType.MULTIPLE
            confidence = max(intent_scores.values()) if intent_scores else 0.5
        elif detected_intents:
            primary_intent = detected_intents[0]
            confidence = intent_scores.get(primary_intent, 0.7)
        else:
            primary_intent = IntentType.COMMAND  # Default
            confidence = 0.5

        # Extract entities (simple - can be enhanced)
        entities = self._extract_entities(text)

        # Map to action
        action = self._map_intent_to_action(primary_intent, text, entities)

        intent = Intent(
            intent_id=intent_id,
            intent_type=primary_intent,
            text=text,
            confidence=confidence,
            entities=entities,
            action=action,
            metadata={"detected_intents": [i.value for i in detected_intents]}
        )

        # Save intent
        self._save_intent(intent)

        # Feed into learning pipeline
        if self.learning_pipeline and self.LearningDataType:
            self.learning_pipeline.collect_learning_data(
                data_type=self.LearningDataType.PATTERN,
                source="intent_classifier",
                context=context or {},
                data={
                    "intent_id": intent_id,
                    "intent_type": primary_intent.value,
                    "confidence": confidence,
                    "action": action,
                },
                metadata={"text": text}
            )

        logger.info(f"🎯 Classified intent: {primary_intent.value} (confidence: {confidence:.2f}, action: {action})")

        return intent

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text (simple implementation)"""
        entities = {}
        text_lower = text.lower()

        # Extract action words
        action_words = ["create", "build", "run", "start", "stop", "implement", "fix", "add"]
        for word in action_words:
            if word in text_lower:
                entities["action"] = word
                break

        # Extract file names (simple pattern)
        file_pattern = r'\b[\w\-\.]+\.(py|js|ts|json|md|txt)\b'
        files = re.findall(file_pattern, text, re.IGNORECASE)
        if files:
            entities["files"] = files

        return entities

    def _map_intent_to_action(self, intent_type: IntentType, text: str, entities: Dict[str, Any]) -> Optional[str]:
        """Map intent to suggested action"""
        text_lower = text.lower()

        # Check action mappings
        for keyword, action in self.action_mappings.items():
            if keyword in text_lower:
                return action

        # Default actions based on intent type
        if intent_type == IntentType.COMMAND:
            return "execute_command"
        elif intent_type == IntentType.QUESTION:
            return "answer_question"
        elif intent_type == IntentType.FEEDBACK:
            return "process_feedback"
        elif intent_type == IntentType.CORRECTION:
            return "apply_correction"
        elif intent_type == IntentType.REQUEST:
            return "fulfill_request"

        return None

    def _save_intent(self, intent: Intent):
        """Save intent to file"""
        try:
            with open(self.intents_file, 'a', encoding='utf-8') as f:
                intent_dict = asdict(intent)
                intent_dict['intent_type'] = intent.intent_type.value
                f.write(json.dumps(intent_dict, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.debug(f"Could not save intent: {e}")

    def _load_action_mappings(self):
        """Load action mappings from file"""
        if self.action_mappings_file.exists():
            try:
                with open(self.action_mappings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.action_mappings.update(loaded)
            except Exception as e:
                logger.debug(f"Could not load action mappings: {e}")


# Global singleton instance
_intent_classifier_instance: Optional[JARVISIntentClassifier] = None


def get_jarvis_intent_classifier(project_root: Optional[Path] = None) -> JARVISIntentClassifier:
    """Get JARVIS intent classifier (singleton)"""
    global _intent_classifier_instance
    if _intent_classifier_instance is None:
        _intent_classifier_instance = JARVISIntentClassifier(project_root)
    return _intent_classifier_instance
