#!/usr/bin/env python3
"""
JARVIS Learning Data Pipeline

Collects, aggregates, and persists learning data from all JARVIS interactions.
This is the foundation for JARVIS's ability to learn and improve.

CRITICAL INFANT STAGE FEATURE - Blocks all learning without this.

Tags: #JARVIS #LEARNING #PIPELINE #INFANT_STAGE #CRITICAL @JARVIS @LUMINA
"""

import sys
import json
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

logger = get_logger("JARVISLearningPipeline")

# MARVIN: Devil's Advocate Integration
try:
    from marvin_jarvis_devil_advocate import get_marvin_devil_advocate, CritiqueLevel
    MARVIN_AVAILABLE = True
    marvin = get_marvin_devil_advocate(CritiqueLevel.ROAST)  # Full roast mode
except ImportError:
    MARVIN_AVAILABLE = False
    marvin = None
    logger.debug("Marvin devil's advocate not available")


class LearningDataType(Enum):
    """Types of learning data"""
    INTERACTION = "interaction"           # Operator interactions
    FEEDBACK = "feedback"                 # Operator feedback
    OUTCOME = "outcome"                   # Action outcomes
    PATTERN = "pattern"                   # Recognized patterns
    INSIGHT = "insight"                   # Generated insights
    ERROR = "error"                       # Errors and failures
    SUCCESS = "success"                   # Successful actions


@dataclass
class LearningDataPoint:
    """A single learning data point"""
    data_id: str
    data_type: LearningDataType
    timestamp: str
    source: str  # Where it came from (e.g., "interaction", "feedback", "self_awareness")
    context: Dict[str, Any]  # Context when this happened
    data: Dict[str, Any]  # The actual learning data
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata


class JARVISLearningPipeline:
    """
    JARVIS Learning Data Pipeline

    Responsibilities:
    - Collect learning data from all sources
    - Aggregate patterns and insights
    - Update knowledge base
    - Persist learning across sessions
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize learning pipeline"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_learning"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data storage files
        self.raw_data_file = self.data_dir / "raw_learning_data.jsonl"
        self.aggregated_patterns_file = self.data_dir / "aggregated_patterns.json"
        self.knowledge_base_file = self.data_dir / "knowledge_base.json"

        # In-memory buffers
        self.data_buffer: List[LearningDataPoint] = []
        self.patterns: Dict[str, Any] = {}
        self.knowledge_base: Dict[str, Any] = {}

        # Load existing data
        self._load_existing_data()

        logger.info("=" * 80)
        logger.info("🧠 JARVIS LEARNING DATA PIPELINE")
        logger.info("=" * 80)
        logger.info("   This is the foundation for JARVIS's ability to learn")
        logger.info("   Without this, JARVIS cannot improve or progress")
        logger.info("")

        # MARVIN: Review this implementation
        if marvin:
            self._marvin_review()

    def _marvin_review(self):
        try:
            """Get Marvin's review of this implementation"""
            if not marvin:
                return

            # Read this file for review
            this_file = Path(__file__)
            if this_file.exists():
                code_content = this_file.read_text(encoding='utf-8')
                review = marvin.review_code(
                    file_path=str(this_file.relative_to(self.project_root)),
                    code_content=code_content,
                    feature_name="Learning Data Pipeline",
                    stage="infant"
                )
                marvin.print_review(review)

        except Exception as e:
            self.logger.error(f"Error in _marvin_review: {e}", exc_info=True)
            raise
    def collect_learning_data(self, data_type: LearningDataType, 
                            source: str, context: Dict[str, Any],
                            data: Dict[str, Any],
                            metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Collect a learning data point

        Args:
            data_type: Type of learning data
            source: Where it came from
            context: Context when this happened
            data: The actual learning data
            metadata: Additional metadata

        Returns:
            data_id: Unique ID for this data point
        """
        data_point = LearningDataPoint(
            data_id=f"{data_type.value}_{int(time.time() * 1000000)}",
            data_type=data_type,
            timestamp=datetime.now().isoformat(),
            source=source,
            context=context,
            data=data,
            metadata=metadata or {}
        )

        # Add to buffer
        self.data_buffer.append(data_point)

        # Auto-flush if buffer gets large
        if len(self.data_buffer) >= 100:
            self.flush_buffer()

        logger.debug(f"📊 Collected learning data: {data_type.value} from {source}")

        return data_point.data_id

    def flush_buffer(self):
        """Flush data buffer to disk"""
        if not self.data_buffer:
            return

        try:
            with open(self.raw_data_file, 'a', encoding='utf-8') as f:
                for data_point in self.data_buffer:
                    # Convert to dict with enum handling
                    data_dict = asdict(data_point)
                    data_dict['data_type'] = data_point.data_type.value  # Convert enum to value
                    f.write(json.dumps(data_dict, ensure_ascii=False) + '\n')

            logger.info(f"💾 Flushed {len(self.data_buffer)} learning data points to disk")
            self.data_buffer.clear()
        except Exception as e:
            logger.error(f"❌ Failed to flush learning data: {e}")

    def aggregate_patterns(self):
        """Aggregate patterns from collected data"""
        # Load recent data
        recent_data = self._load_recent_data(days=7)

        # Simple pattern aggregation (can be enhanced)
        pattern_counts: Dict[str, int] = {}

        for data_point in recent_data:
            # Extract patterns based on data type
            if data_point.data_type == LearningDataType.INTERACTION:
                # Pattern: operator action -> outcome
                action = data_point.data.get("action", "unknown")
                outcome = data_point.data.get("outcome", "unknown")
                pattern_key = f"{action}->{outcome}"
                pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1

            elif data_point.data_type == LearningDataType.FEEDBACK:
                # Pattern: action -> feedback type
                action = data_point.data.get("action", "unknown")
                feedback_type = data_point.data.get("feedback_type", "unknown")
                pattern_key = f"{action}->{feedback_type}"
                pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1

        # Update patterns
        self.patterns = {
            "patterns": pattern_counts,
            "last_updated": datetime.now().isoformat(),
            "data_points_analyzed": len(recent_data)
        }

        # Save patterns
        self._save_patterns()

        logger.info(f"🔍 Aggregated {len(pattern_counts)} patterns from {len(recent_data)} data points")

    def update_knowledge_base(self):
        """Update knowledge base from patterns and insights"""
        # Load patterns
        if not self.patterns:
            self.aggregate_patterns()

        # Update knowledge base with patterns
        self.knowledge_base = {
            "patterns": self.patterns.get("patterns", {}),
            "insights": self._generate_insights(),
            "last_updated": datetime.now().isoformat()
        }

        # Save knowledge base
        self._save_knowledge_base()

        logger.info("📚 Knowledge base updated")

    def _generate_insights(self) -> List[Dict[str, Any]]:
        """Generate insights from patterns"""
        insights = []

        # Simple insight generation (can be enhanced)
        patterns = self.patterns.get("patterns", {})

        # Find most common patterns
        if patterns:
            sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
            top_patterns = sorted_patterns[:5]

            for pattern, count in top_patterns:
                insights.append({
                    "insight": f"Pattern '{pattern}' occurred {count} times",
                    "confidence": min(count / 10.0, 1.0),  # Simple confidence
                    "pattern": pattern,
                    "count": count
                })

        return insights

    def _load_recent_data(self, days: int = 7) -> List[LearningDataPoint]:
        """Load recent learning data"""
        if not self.raw_data_file.exists():
            return []

        recent_data = []
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)

        try:
            with open(self.raw_data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    data_dict = json.loads(line)
                    # Convert data_type back to enum
                    if 'data_type' in data_dict and isinstance(data_dict['data_type'], str):
                        data_dict['data_type'] = LearningDataType(data_dict['data_type'])
                    data_point = LearningDataPoint(**data_dict)
                    # Check if recent
                    point_time = datetime.fromisoformat(data_point.timestamp).timestamp()
                    if point_time >= cutoff_time:
                        recent_data.append(data_point)
        except Exception as e:
            logger.debug(f"Could not load recent data: {e}")

        return recent_data

    def _load_existing_data(self):
        """Load existing patterns and knowledge base"""
        # Load patterns
        if self.aggregated_patterns_file.exists():
            try:
                with open(self.aggregated_patterns_file, 'r', encoding='utf-8') as f:
                    self.patterns = json.load(f)
                logger.info(f"📂 Loaded existing patterns ({len(self.patterns.get('patterns', {}))} patterns)")
            except Exception as e:
                logger.debug(f"Could not load patterns: {e}")

        # Load knowledge base
        if self.knowledge_base_file.exists():
            try:
                with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
                logger.info(f"📂 Loaded existing knowledge base ({len(self.knowledge_base.get('insights', []))} insights)")
            except Exception as e:
                logger.debug(f"Could not load knowledge base: {e}")

        # ENHANCED: Load raw learning data on startup for cross-session continuity
        if self.raw_data_file.exists():
            try:
                # Count existing data points
                with open(self.raw_data_file, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for line in f if line.strip())
                if line_count > 0:
                    logger.info(f"📂 Found {line_count} existing learning data points - cross-session continuity enabled")
            except Exception as e:
                logger.debug(f"Could not check learning data: {e}")

    def _save_patterns(self):
        """Save aggregated patterns"""
        try:
            with open(self.aggregated_patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")

    def _save_knowledge_base(self):
        """Save knowledge base"""
        try:
            with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save knowledge base: {e}")

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Get current knowledge base"""
        return self.knowledge_base.copy()

    def get_patterns(self) -> Dict[str, Any]:
        """Get current patterns"""
        return self.patterns.copy()


# Global singleton instance
_pipeline_instance: Optional[JARVISLearningPipeline] = None


def get_jarvis_learning_pipeline(project_root: Optional[Path] = None) -> JARVISLearningPipeline:
    """Get JARVIS learning pipeline (singleton)"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = JARVISLearningPipeline(project_root)
    return _pipeline_instance


if __name__ == "__main__":
    # Test the learning pipeline
    pipeline = get_jarvis_learning_pipeline()

    # Collect some test data
    pipeline.collect_learning_data(
        LearningDataType.INTERACTION,
        source="test",
        context={"test": True},
        data={"action": "test_action", "outcome": "success"}
    )

    # Flush and aggregate
    pipeline.flush_buffer()
    pipeline.aggregate_patterns()
    pipeline.update_knowledge_base()

    logger.info("✅ Learning pipeline test complete")
