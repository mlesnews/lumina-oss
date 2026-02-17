#!/usr/bin/env python3
"""
Insights & Sparks System - Inceptions of Ideas

Original Vision:
- Insights = Inceptions of Ideas (the word "insight" is apropos)
- @Sparks or Sparks = Single insight
- Force multipliers: Force, force, force (the force)

This system captures and leverages insights/sparks systematically,
applying force multipliers to amplify their impact.

Tags: #INSIGHTS #SPARKS #INCEPTIONS #FORCE_MULTIPLIERS @LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("InsightsSparksSystem")

# Import SYPHON and R5 for integration
try:
    from ai_thinking_syphon import siphon_thinking
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False


class Spark:
    """
    A single insight - an inception of an idea.

    @Sparks or Sparks = Single insight
    """

    def __init__(
        self,
        content: str,
        source: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ):
        self.spark_id = f"spark_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.content = content
        self.source = source
        self.context = context or {}
        self.tags = tags or []
        self.timestamp = datetime.now()
        self.force_multipliers = []  # Applied force multipliers
        self.impact_score = 0.0  # Calculated impact

    def to_dict(self) -> Dict[str, Any]:
        """Convert spark to dictionary"""
        return {
            "spark_id": self.spark_id,
            "content": self.content,
            "source": self.source,
            "context": self.context,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
            "force_multipliers": self.force_multipliers,
            "impact_score": self.impact_score
        }


class Insight:
    """
    An insight - an inception of an idea.

    Insights = Inceptions of Ideas (the word "insight" is apropos)
    Can contain multiple sparks or be a single spark.
    """

    def __init__(
        self,
        title: str,
        description: str,
        sparks: Optional[List[Spark]] = None,
        source: str = "unknown",
        context: Optional[Dict[str, Any]] = None
    ):
        self.insight_id = f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.title = title
        self.description = description
        self.sparks = sparks or []
        self.source = source
        self.context = context or {}
        self.timestamp = datetime.now()
        self.force_multipliers = []
        self.impact_score = 0.0

    def add_spark(self, spark: Spark):
        """Add a spark to this insight"""
        self.sparks.append(spark)

    def to_dict(self) -> Dict[str, Any]:
        """Convert insight to dictionary"""
        return {
            "insight_id": self.insight_id,
            "title": self.title,
            "description": self.description,
            "sparks": [s.to_dict() for s in self.sparks],
            "source": self.source,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "force_multipliers": self.force_multipliers,
            "impact_score": self.impact_score
        }


class ForceMultiplier:
    """
    Force multiplier - amplifies the impact of insights/sparks.

    Force, force, force - the force.
    """

    def __init__(self, name: str, multiplier: float, description: str = ""):
        self.name = name
        self.multiplier = multiplier  # e.g., 2.0 = doubles impact
        self.description = description

    def apply(self, base_score: float) -> float:
        """Apply force multiplier to base score"""
        return base_score * self.multiplier


class InsightsSparksSystem:
    """
    Insights & Sparks System - Captures and leverages inceptions of ideas.

    Original Vision:
    - Insights = Inceptions of Ideas
    - @Sparks = Single insight
    - Force multipliers: Force, force, force (the force)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Insights & Sparks System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "insights_sparks"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize R5 if available
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root=self.project_root)
                logger.info("✅ R5 Living Context Matrix initialized for insights")
            except Exception as e:
                logger.warning(f"⚠️  R5 init error: {e}")

        # Force multipliers registry
        self.force_multipliers = {
            "SYPHON": ForceMultiplier("SYPHON", 2.0, "Intelligence extraction amplifies insight impact"),
            "R5": ForceMultiplier("R5", 3.0, "R5 matrix aggregation multiplies insight value"),
            "Animatrix": ForceMultiplier("Animatrix", 5.0, "10,000 years of simulation validates insights"),
            "RR": ForceMultiplier("RR", 2.5, "Roast and Repair system refines insights"),
            "Workflow": ForceMultiplier("Workflow", 2.0, "Workflow integration amplifies insight application"),
            "Matrix": ForceMultiplier("Matrix", 4.0, "Matrix system multiplies insight convergence"),
            "Animatrix_Matrix": ForceMultiplier("Animatrix+Matrix", 10.0, "Combined Animatrix and Matrix - maximum force")
        }

        logger.info("=" * 80)
        logger.info("💡 INSIGHTS & SPARKS SYSTEM")
        logger.info("   Inceptions of Ideas - Force, force, force (the force)")
        logger.info("=" * 80)

    def capture_spark(
        self,
        content: str,
        source: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        apply_force_multipliers: bool = True
    ) -> Spark:
        """
        Capture a single spark (insight).

        Args:
            content: The spark content (single insight)
            source: Source of the spark
            context: Additional context
            tags: Tags for categorization
            apply_force_multipliers: Whether to apply force multipliers

        Returns:
            Spark object
        """
        spark = Spark(content, source, context, tags)

        logger.info(f"💡 Capturing spark: {content[:80]}...")

        # Apply force multipliers
        if apply_force_multipliers:
            spark.force_multipliers = self._apply_force_multipliers(spark)
            spark.impact_score = self._calculate_impact(spark)

        # Save spark
        spark_file = self.data_dir / "sparks" / f"{spark.spark_id}.json"
        spark_file.parent.mkdir(parents=True, exist_ok=True)
        with open(spark_file, 'w', encoding='utf-8') as f:
            json.dump(spark.to_dict(), f, indent=2, default=str)

        logger.info(f"   💾 Spark saved: {spark_file}")
        logger.info(f"   🎯 Impact score: {spark.impact_score:.2f}")

        # Integrate with R5
        if self.r5:
            try:
                self.r5.ingest_session({
                    "session_id": spark.spark_id,
                    "timestamp": spark.timestamp.isoformat(),
                    "messages": [{
                        "role": "spark",
                        "content": f"@SPARK: {spark.content}",
                        "timestamp": spark.timestamp.isoformat()
                    }],
                    "metadata": {
                        "type": "spark",
                        "source": spark.source,
                        "tags": spark.tags,
                        "impact_score": spark.impact_score,
                        "force_multipliers": spark.force_multipliers
                    }
                })
                logger.info("   ✅ Spark ingested into R5 matrix")
            except Exception as e:
                logger.warning(f"⚠️  R5 integration error: {e}")

        # SYPHON the spark
        if SYPHON_AVAILABLE:
            try:
                siphon_thinking(
                    f"@SPARK: {spark.content}",
                    context={
                        "type": "spark",
                        "source": spark.source,
                        "tags": spark.tags,
                        "impact_score": spark.impact_score
                    },
                    trigger_workflow=True
                )
                logger.info("   ✅ Spark SYPHONed into workflows")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON error: {e}")

        return spark

    def capture_insight(
        self,
        title: str,
        description: str,
        sparks: Optional[List[Spark]] = None,
        source: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
        apply_force_multipliers: bool = True
    ) -> Insight:
        """
        Capture an insight (inception of ideas).

        Args:
            title: Insight title
            description: Insight description
            sparks: List of sparks (single insights) that form this insight
            source: Source of the insight
            context: Additional context
            apply_force_multipliers: Whether to apply force multipliers

        Returns:
            Insight object
        """
        insight = Insight(title, description, sparks, source, context)

        logger.info(f"💡 Capturing insight: {title}")
        logger.info(f"   Description: {description[:80]}...")
        logger.info(f"   Sparks: {len(insight.sparks)}")

        # Apply force multipliers
        if apply_force_multipliers:
            insight.force_multipliers = self._apply_force_multipliers(insight)
            insight.impact_score = self._calculate_impact(insight)

        # Save insight
        insight_file = self.data_dir / "insights" / f"{insight.insight_id}.json"
        insight_file.parent.mkdir(parents=True, exist_ok=True)
        with open(insight_file, 'w', encoding='utf-8') as f:
            json.dump(insight.to_dict(), f, indent=2, default=str)

        logger.info(f"   💾 Insight saved: {insight_file}")
        logger.info(f"   🎯 Impact score: {insight.impact_score:.2f}")

        return insight

    def _apply_force_multipliers(self, item: Any) -> List[str]:
        """Apply force multipliers to spark/insight"""
        applied = []

        # Check which force multipliers are applicable
        # SYPHON: Always available if SYPHON_AVAILABLE
        if SYPHON_AVAILABLE:
            applied.append("SYPHON")

        # R5: Always available if R5_AVAILABLE
        if R5_AVAILABLE:
            applied.append("R5")

        # Animatrix: Available if we're testing
        if hasattr(self, 'animatrix_available'):
            applied.append("Animatrix")

        # RR: Available (we have RR system)
        applied.append("RR")

        # Workflow: Always available
        applied.append("Workflow")

        # Matrix: Available if Matrix system exists
        # TODO: Check for Matrix system  # [ADDRESSED]  # [ADDRESSED]

        # Animatrix+Matrix: If both available
        if "Animatrix" in applied:  # and Matrix available
            applied.append("Animatrix_Matrix")

        return applied

    def _calculate_impact(self, item: Any) -> float:
        """Calculate impact score with force multipliers"""
        base_score = 1.0  # Base impact

        # Apply force multipliers
        for multiplier_name in item.force_multipliers:
            if multiplier_name in self.force_multipliers:
                multiplier = self.force_multipliers[multiplier_name]
                base_score = multiplier.apply(base_score)

        return base_score

    def get_force_multipliers(self) -> Dict[str, ForceMultiplier]:
        """Get all available force multipliers"""
        return self.force_multipliers


# Global instance
_global_insights_system = None

def get_insights_system() -> InsightsSparksSystem:
    """Get global Insights & Sparks system instance"""
    global _global_insights_system
    if _global_insights_system is None:
        _global_insights_system = InsightsSparksSystem()
    return _global_insights_system


def capture_spark(content: str, **kwargs) -> Spark:
    """Convenience function to capture a spark"""
    system = get_insights_system()
    return system.capture_spark(content, **kwargs)


def capture_insight(title: str, description: str, **kwargs) -> Insight:
    """Convenience function to capture an insight"""
    system = get_insights_system()
    return system.capture_insight(title, description, **kwargs)


if __name__ == "__main__":
    # Demo
    system = InsightsSparksSystem()

    # Capture a spark
    spark = system.capture_spark(
        content="Use Animatrix simulation to validate design changes before implementing",
        source="user_feedback",
        tags=["animatrix", "validation", "design"],
        context={"task": "kenny_improvements"}
    )

    print(f"\n✅ Spark captured: {spark.spark_id}")
    print(f"   Impact score: {spark.impact_score:.2f}")
    print(f"   Force multipliers: {', '.join(spark.force_multipliers)}")

    # Capture an insight
    insight = system.capture_insight(
        title="Animatrix A/B Testing for Rapid Validation",
        description="Leverage 10,000 years of matrix simulation to validate changes before implementing",
        sparks=[spark],
        source="system_development",
        context={"system": "kenny_animatrix_ab_test"}
    )

    print(f"\n✅ Insight captured: {insight.insight_id}")
    print(f"   Impact score: {insight.impact_score:.2f}")
    print(f"   Force multipliers: {', '.join(insight.force_multipliers)}")
