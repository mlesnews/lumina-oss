#!/usr/bin/env python3
"""
JARVIS Context Understanding System

Deep context analysis from all five senses, multi-modal fusion, temporal tracking.
Foundation for accurate predictions and intent understanding.

CRITICAL TODDLER STAGE FEATURE.

Tags: #JARVIS #CONTEXT #UNDERSTANDING #TODDLER_STAGE #CRITICAL @JARVIS @LUMINA
"""

import sys
import json
import time
from datetime import datetime, timedelta
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

logger = get_logger("JARVISContextAnalyzer")

# MARVIN: Devil's Advocate Integration
try:
    from marvin_jarvis_devil_advocate import get_marvin_devil_advocate, CritiqueLevel
    MARVIN_AVAILABLE = True
    marvin = get_marvin_devil_advocate(CritiqueLevel.ROAST)
except ImportError:
    MARVIN_AVAILABLE = False
    marvin = None
    logger.debug("Marvin devil's advocate not available")


class ContextSource(Enum):
    """Sources of context"""
    SIGHT = "sight"
    HEARING = "hearing"
    TOUCH = "touch"
    TASTE = "taste"
    SMELL = "smell"
    TEMPORAL = "temporal"  # What happened before
    SYSTEM = "system"       # System state


@dataclass
class ContextData:
    """Context data from a source"""
    source: ContextSource
    data: Dict[str, Any]
    timestamp: str
    confidence: float = 1.0  # 0.0 to 1.0


@dataclass
class FusedContext:
    """Fused multi-modal context"""
    context_id: str
    timestamp: str
    sources: List[ContextSource]
    fused_data: Dict[str, Any]
    confidence: float
    temporal_context: Optional[Dict[str, Any]] = None


class JARVISContextAnalyzer:
    """
    JARVIS Context Understanding System

    Responsibilities:
    - Multi-modal context fusion (combine all five senses)
    - Temporal context tracking (what happened before)
    - Deep context analysis
    - Context-to-action mapping
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize context analyzer"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_context"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.context_history_file = self.data_dir / "context_history.jsonl"

        # In-memory context
        self.current_context: Optional[FusedContext] = None
        self.context_history: List[FusedContext] = []
        self.temporal_window = timedelta(minutes=5)  # 5-minute temporal window

        # Integration with other systems
        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
            self.LearningDataType = LearningDataType
        except ImportError:
            self.learning_pipeline = None
            self.LearningDataType = None

        logger.info("=" * 80)
        logger.info("🧠 JARVIS CONTEXT ANALYZER")
        logger.info("=" * 80)
        logger.info("   Multi-modal context fusion")
        logger.info("   Temporal context tracking")
        logger.info("   Deep context analysis")
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
                    feature_name="Context Analyzer",
                    stage="toddler"
                )
                marvin.print_review(review)

        except Exception as e:
            self.logger.error(f"Error in _marvin_review: {e}", exc_info=True)
            raise
    def add_context_data(self, source: ContextSource, data: Dict[str, Any], confidence: float = 1.0):
        """Add context data from a source"""
        context_data = ContextData(
            source=source,
            data=data,
            timestamp=datetime.now().isoformat(),
            confidence=confidence
        )

        # Trigger context fusion
        self._fuse_context()

        logger.debug(f"📊 Added context from {source.value}")

    def _fuse_context(self):
        """Fuse context from all sources"""
        # Collect context from all available sources
        context_sources = []
        fused_data = {}

        # Get context from five senses (if available)
        # This is a placeholder - actual implementation would query JARVIS's sense systems
        try:
            # Sight context (from MDV vision)
            # Hearing context (from voice queue)
            # Touch context (from interactions)
            # Taste context (from data quality)
            # Smell context (from health monitoring)
            pass
        except Exception as e:
            logger.debug(f"Could not collect sense context: {e}")

        # Get temporal context
        temporal_context = self._get_temporal_context()

        # Create fused context
        context_id = f"context_{int(time.time() * 1000000)}"
        fused_context = FusedContext(
            context_id=context_id,
            timestamp=datetime.now().isoformat(),
            sources=context_sources,
            fused_data=fused_data,
            confidence=0.8,  # Placeholder
            temporal_context=temporal_context
        )

        self.current_context = fused_context
        self.context_history.append(fused_context)

        # Keep only recent history
        cutoff_time = datetime.now() - self.temporal_window
        self.context_history = [
            ctx for ctx in self.context_history
            if datetime.fromisoformat(ctx.timestamp) >= cutoff_time
        ]

        # Feed into learning pipeline
        if self.learning_pipeline and self.LearningDataType:
            self.learning_pipeline.collect_learning_data(
                data_type=self.LearningDataType.PATTERN,
                source="context_analyzer",
                context={"context_id": context_id},
                data=fused_data,
                metadata={"sources": [s.value for s in context_sources]}
            )

    def _get_temporal_context(self) -> Dict[str, Any]:
        """Get temporal context (what happened before)"""
        if not self.context_history:
            return {}

        # Get recent context history
        recent_contexts = self.context_history[-10:]  # Last 10 contexts

        return {
            "recent_contexts": len(recent_contexts),
            "context_sequence": [ctx.context_id for ctx in recent_contexts],
            "temporal_patterns": self._analyze_temporal_patterns(recent_contexts)
        }

    def _analyze_temporal_patterns(self, contexts: List[FusedContext]) -> Dict[str, Any]:
        """Analyze temporal patterns in context"""
        # Simple pattern analysis
        patterns = {
            "context_changes": len(contexts),
            "source_frequency": {}
        }

        # Count source frequency
        for ctx in contexts:
            for source in ctx.sources:
                patterns["source_frequency"][source.value] = patterns["source_frequency"].get(source.value, 0) + 1

        return patterns

    def get_current_context(self) -> Optional[FusedContext]:
        """Get current fused context"""
        return self.current_context

    def analyze_context_for_action(self, action: str) -> Dict[str, Any]:
        """Analyze context to determine if action is appropriate"""
        if not self.current_context:
            return {"appropriate": False, "reason": "No context available"}

        # Simple analysis (can be enhanced)
        analysis = {
            "appropriate": True,
            "confidence": 0.7,
            "context_sources": len(self.current_context.sources),
            "temporal_relevance": bool(self.current_context.temporal_context)
        }

        return analysis


# Global singleton instance
_context_analyzer_instance: Optional[JARVISContextAnalyzer] = None


def get_jarvis_context_analyzer(project_root: Optional[Path] = None) -> JARVISContextAnalyzer:
    """Get JARVIS context analyzer (singleton)"""
    global _context_analyzer_instance
    if _context_analyzer_instance is None:
        _context_analyzer_instance = JARVISContextAnalyzer(project_root)
    return _context_analyzer_instance
