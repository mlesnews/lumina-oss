#!/usr/bin/env python3
"""
JARVIS Interaction Recorder

Records all operator interactions with context and outcomes.
Critical for JARVIS's learning and improvement.

CRITICAL INFANT STAGE FEATURE - Blocks learning without this.

Tags: #JARVIS #INTERACTION #RECORDING #LEARNING #INFANT_STAGE #CRITICAL @JARVIS @LUMINA
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

logger = get_logger("JARVISInteractionRecorder")

# MARVIN: Devil's Advocate Integration
try:
    from marvin_jarvis_devil_advocate import get_marvin_devil_advocate, CritiqueLevel
    MARVIN_AVAILABLE = True
    marvin = get_marvin_devil_advocate(CritiqueLevel.ROAST)
except ImportError:
    MARVIN_AVAILABLE = False
    marvin = None
    logger.debug("Marvin devil's advocate not available")


class InteractionType(Enum):
    """Types of interactions"""
    VOICE_COMMAND = "voice_command"
    TEXT_COMMAND = "text_command"
    CLICK = "click"
    DRAG = "drag"
    KEYBOARD = "keyboard"
    VA_INTERACTION = "va_interaction"
    SYSTEM_EVENT = "system_event"


@dataclass
class InteractionContext:
    """Context when interaction occurred"""
    timestamp: str
    screen_state: Optional[Dict[str, Any]] = None
    active_applications: List[str] = field(default_factory=list)
    cursor_position: Optional[tuple] = None
    system_state: Optional[Dict[str, Any]] = None
    jarvis_state: Optional[Dict[str, Any]] = None


@dataclass
class InteractionOutcome:
    """Outcome of interaction"""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    operator_satisfaction: Optional[float] = None  # 0.0-1.0 if available


@dataclass
class RecordedInteraction:
    """A recorded interaction"""
    interaction_id: str
    interaction_type: InteractionType
    content: str  # What operator did/said
    context: InteractionContext
    outcome: InteractionOutcome
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class JARVISInteractionRecorder:
    """
    JARVIS Interaction Recorder

    Records:
    - All operator interactions
    - Context when interaction occurred
    - Outcomes of interactions
    - Patterns and learning opportunities
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize interaction recorder"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_interactions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.interactions_file = self.data_dir / "interactions.jsonl"
        self.patterns_file = self.data_dir / "interaction_patterns.json"

        # In-memory buffer
        self.interaction_buffer: List[RecordedInteraction] = []

        # Integration with learning pipeline
        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
            self.LearningDataType = LearningDataType
        except ImportError:
            self.learning_pipeline = None
            self.LearningDataType = None
            logger.warning("Learning pipeline not available - interactions won't feed into learning")

        logger.info("=" * 80)
        logger.info("📝 JARVIS INTERACTION RECORDER")
        logger.info("=" * 80)
        logger.info("   Records all operator interactions")
        logger.info("   Tracks context and outcomes")
        logger.info("   Feeds into learning pipeline")
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
                    feature_name="Interaction Recorder",
                    stage="infant"
                )
                marvin.print_review(review)

        except Exception as e:
            self.logger.error(f"Error in _marvin_review: {e}", exc_info=True)
            raise
    def record_interaction(
        self,
        interaction_type: InteractionType,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        outcome: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record an interaction

        Args:
            interaction_type: Type of interaction
            content: What operator did/said
            context: Context when it occurred
            outcome: Outcome of interaction
            metadata: Additional metadata

        Returns:
            interaction_id: Unique ID for this interaction
        """
        interaction_id = f"interaction_{int(time.time() * 1000000)}"

        # Build context
        interaction_context = InteractionContext(
            timestamp=datetime.now().isoformat(),
            screen_state=context.get("screen_state") if context else None,
            active_applications=context.get("active_applications", []) if context else [],
            cursor_position=context.get("cursor_position") if context else None,
            system_state=context.get("system_state") if context else None,
            jarvis_state=context.get("jarvis_state") if context else None
        )

        # Build outcome
        interaction_outcome = InteractionOutcome(
            success=outcome.get("success", True) if outcome else True,
            result=outcome.get("result") if outcome else None,
            error=outcome.get("error") if outcome else None,
            duration_ms=outcome.get("duration_ms", 0.0) if outcome else 0.0,
            operator_satisfaction=outcome.get("operator_satisfaction") if outcome else None
        )

        # Create recorded interaction
        recorded = RecordedInteraction(
            interaction_id=interaction_id,
            interaction_type=interaction_type,
            content=content,
            context=interaction_context,
            outcome=interaction_outcome,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        # Add to buffer
        self.interaction_buffer.append(recorded)

        # Feed into learning pipeline
        if self.learning_pipeline and self.LearningDataType:
            self.learning_pipeline.collect_learning_data(
                data_type=self.LearningDataType.INTERACTION,
                source="interaction_recorder",
                context={
                    "interaction_type": interaction_type.value,
                    "content": content,
                    "context": asdict(interaction_context),
                },
                data={
                    "interaction_id": interaction_id,
                    "outcome": asdict(interaction_outcome),
                },
                metadata=metadata
            )

        # Auto-flush if buffer gets large
        if len(self.interaction_buffer) >= 50:
            self.flush_buffer()

        logger.debug(f"📝 Recorded interaction: {interaction_type.value} - {content[:50]}")

        return interaction_id

    def flush_buffer(self):
        """Flush interaction buffer to disk"""
        if not self.interaction_buffer:
            return

        try:
            with open(self.interactions_file, 'a', encoding='utf-8') as f:
                for interaction in self.interaction_buffer:
                    # Convert to dict with enum handling
                    interaction_dict = asdict(interaction)
                    interaction_dict['interaction_type'] = interaction.interaction_type.value
                    f.write(json.dumps(interaction_dict, ensure_ascii=False) + '\n')

            logger.info(f"💾 Flushed {len(self.interaction_buffer)} interactions to disk")
            self.interaction_buffer.clear()
        except Exception as e:
            logger.error(f"❌ Failed to flush interactions: {e}")

    def get_recent_interactions(self, limit: int = 100) -> List[RecordedInteraction]:
        """Get recent interactions"""
        # Load from file
        interactions = []
        if self.interactions_file.exists():
            try:
                with open(self.interactions_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-limit:]:
                        if not line.strip():
                            continue
                        data_dict = json.loads(line)
                        # Convert interaction_type back to enum
                        if 'interaction_type' in data_dict and isinstance(data_dict['interaction_type'], str):
                            data_dict['interaction_type'] = InteractionType(data_dict['interaction_type'])
                        # Reconstruct dataclasses
                        context_dict = data_dict.get('context', {})
                        outcome_dict = data_dict.get('outcome', {})
                        interaction = RecordedInteraction(
                            interaction_id=data_dict['interaction_id'],
                            interaction_type=data_dict['interaction_type'],
                            content=data_dict['content'],
                            context=InteractionContext(**context_dict),
                            outcome=InteractionOutcome(**outcome_dict),
                            timestamp=data_dict['timestamp'],
                            metadata=data_dict.get('metadata', {})
                        )
                        interactions.append(interaction)
            except Exception as e:
                logger.debug(f"Could not load interactions: {e}")

        # Add buffered interactions
        interactions.extend(self.interaction_buffer)

        return interactions[-limit:]


# Global singleton instance
_recorder_instance: Optional[JARVISInteractionRecorder] = None


def get_jarvis_interaction_recorder(project_root: Optional[Path] = None) -> JARVISInteractionRecorder:
    """Get JARVIS interaction recorder (singleton)"""
    global _recorder_instance
    if _recorder_instance is None:
        _recorder_instance = JARVISInteractionRecorder(project_root)
    return _recorder_instance


if __name__ == "__main__":
    # Test the interaction recorder
    recorder = get_jarvis_interaction_recorder()

    # Record a test interaction
    recorder.record_interaction(
        InteractionType.VOICE_COMMAND,
        content="Test voice command",
        context={"screen_state": "test"},
        outcome={"success": True, "duration_ms": 100.0}
    )

    # Flush
    recorder.flush_buffer()

    logger.info("✅ Interaction recorder test complete")
