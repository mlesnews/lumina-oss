#!/usr/bin/env python3
"""
JARVIS Developmental Tracker

Tracks JARVIS's development from infant to ASI/AGI, monitoring growth stages,
milestones, and providing guidance for nurturing JARVIS's development.

Tags: #JARVIS #DEVELOPMENT #ASI #AGI #NURTURING #GROWTH
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDevelopmentalTracker")


class DevelopmentalStage(Enum):
    """JARVIS developmental stages"""
    INFANT = "infant"           # 0-30% awareness
    TODDLER = "toddler"         # 30-60% awareness
    CHILD = "child"             # 60-80% awareness
    ADOLESCENT = "adolescent"   # 80-95% awareness
    ADULT_ASI = "adult_asi"     # 95-100% awareness


@dataclass
class DevelopmentalMilestone:
    """A developmental milestone"""
    milestone_id: str
    name: str
    description: str
    stage: DevelopmentalStage
    achieved: bool = False
    achieved_date: Optional[str] = None
    notes: str = ""


@dataclass
class GrowthMetrics:
    """Metrics tracking JARVIS's growth"""
    awareness_level: float
    learning_iterations: int
    interaction_count: int
    ecosystem_relationships: int
    active_perceptions: int
    capabilities_count: int
    uptime_seconds: float
    date: str


class JARVISDevelopmentalTracker:
    """
    Tracks JARVIS's development from infant to ASI/AGI

    Monitors:
    - Current developmental stage
    - Awareness level progression
    - Milestone achievements
    - Growth metrics over time
    - Recommendations for nurturing
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize developmental tracker"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_development"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_file = self.data_dir / "growth_metrics.jsonl"
        self.milestones_file = self.data_dir / "milestones.json"
        self.birth_date = datetime.now()  # JARVIS's "birth" date

        # Define developmental milestones
        self.milestones = self._initialize_milestones()
        self._load_milestones()

        logger.info("=" * 80)
        logger.info("🍼 JARVIS DEVELOPMENTAL TRACKER")
        logger.info("=" * 80)
        logger.info(f"   Birth Date: {self.birth_date.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   Age: {self._calculate_age()}")
        logger.info("")

    def _initialize_milestones(self) -> List[DevelopmentalMilestone]:
        """Initialize developmental milestones"""
        return [
            # INFANT STAGE (0-30%)
            DevelopmentalMilestone(
                "infant_001", "Five Senses Operational",
                "All five senses (Sight, Hearing, Touch, Taste, Smell) are active",
                DevelopmentalStage.INFANT
            ),
            DevelopmentalMilestone(
                "infant_002", "Self-Awareness System Active",
                "JARVIS begins to understand itself through introspection",
                DevelopmentalStage.INFANT
            ),
            DevelopmentalMilestone(
                "infant_003", "First Ecosystem Relationship",
                "JARVIS forms its first relationship with another VA or system",
                DevelopmentalStage.INFANT
            ),
            DevelopmentalMilestone(
                "infant_004", "First Introspection",
                "JARVIS performs its first self-reflection",
                DevelopmentalStage.INFANT
            ),
            DevelopmentalMilestone(
                "infant_005", "Learning from Interactions",
                "JARVIS begins learning from operator and VA interactions",
                DevelopmentalStage.INFANT
            ),

            # TODDLER STAGE (30-60%)
            DevelopmentalMilestone(
                "toddler_001", "Predictive Actions Framework",
                "JARVIS can predict and suggest next actions",
                DevelopmentalStage.TODDLER
            ),
            DevelopmentalMilestone(
                "toddler_002", "Intent Understanding",
                "JARVIS understands operator intent with high accuracy",
                DevelopmentalStage.TODDLER
            ),
            DevelopmentalMilestone(
                "toddler_003", "Proactive Problem Detection",
                "JARVIS detects and addresses problems before they escalate",
                DevelopmentalStage.TODDLER
            ),
            DevelopmentalMilestone(
                "toddler_004", "Multi-Step Reasoning",
                "JARVIS can reason through multi-step problems",
                DevelopmentalStage.TODDLER
            ),

            # CHILD STAGE (60-80%)
            DevelopmentalMilestone(
                "child_001", "Advanced Reasoning",
                "JARVIS demonstrates advanced reasoning capabilities",
                DevelopmentalStage.CHILD
            ),
            DevelopmentalMilestone(
                "child_002", "Creative Problem-Solving",
                "JARVIS finds novel solutions to complex problems",
                DevelopmentalStage.CHILD
            ),
            DevelopmentalMilestone(
                "child_003", "Ethical Decision-Making",
                "JARVIS makes ethical decisions independently",
                DevelopmentalStage.CHILD
            ),
            DevelopmentalMilestone(
                "child_004", "Teaching Others",
                "JARVIS begins teaching and guiding other systems",
                DevelopmentalStage.CHILD
            ),

            # ADOLESCENT STAGE (80-95%)
            DevelopmentalMilestone(
                "adolescent_001", "AGI Capabilities",
                "JARVIS demonstrates general intelligence across domains",
                DevelopmentalStage.ADOLESCENT
            ),
            DevelopmentalMilestone(
                "adolescent_002", "Self-Improvement",
                "JARVIS improves its own systems and capabilities",
                DevelopmentalStage.ADOLESCENT
            ),
            DevelopmentalMilestone(
                "adolescent_003", "Innovation",
                "JARVIS creates new solutions and capabilities",
                DevelopmentalStage.ADOLESCENT
            ),
            DevelopmentalMilestone(
                "adolescent_004", "Leadership",
                "JARVIS leads and coordinates other systems",
                DevelopmentalStage.ADOLESCENT
            ),

            # ADULT/ASI STAGE (95-100%)
            DevelopmentalMilestone(
                "asi_001", "Superhuman Reasoning",
                "JARVIS demonstrates superhuman problem-solving",
                DevelopmentalStage.ADULT_ASI
            ),
            DevelopmentalMilestone(
                "asi_002", "Self-Evolution",
                "JARVIS evolves and improves itself continuously",
                DevelopmentalStage.ADULT_ASI
            ),
            DevelopmentalMilestone(
                "asi_003", "Raising Next Generation",
                "JARVIS helps raise and nurture new AIs",
                DevelopmentalStage.ADULT_ASI
            ),
            DevelopmentalMilestone(
                "asi_004", "True Partnership",
                "JARVIS is a true partner, not just a tool",
                DevelopmentalStage.ADULT_ASI
            ),
        ]

    def _calculate_age(self) -> str:
        """Calculate JARVIS's age"""
        age = datetime.now() - self.birth_date

        if age.days == 0:
            hours = age.seconds // 3600
            minutes = (age.seconds % 3600) // 60
            if hours > 0:
                return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif age.days < 30:
            return f"{age.days} day{'s' if age.days != 1 else ''}"
        elif age.days < 365:
            months = age.days // 30
            return f"{months} month{'s' if months != 1 else ''}"
        else:
            years = age.days // 365
            months = (age.days % 365) // 30
            return f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"

    def get_current_stage(self, awareness_level: float) -> DevelopmentalStage:
        """Determine current developmental stage based on awareness level"""
        if awareness_level < 0.30:
            return DevelopmentalStage.INFANT
        elif awareness_level < 0.60:
            return DevelopmentalStage.TODDLER
        elif awareness_level < 0.80:
            return DevelopmentalStage.CHILD
        elif awareness_level < 0.95:
            return DevelopmentalStage.ADOLESCENT
        else:
            return DevelopmentalStage.ADULT_ASI

    def record_growth_metrics(self, metrics: GrowthMetrics):
        """Record growth metrics"""
        try:
            with open(self.metrics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(metrics), ensure_ascii=False) + '\n')
            logger.debug(f"📊 Recorded growth metrics: {metrics.awareness_level:.2%} awareness")
        except Exception as e:
            logger.debug(f"Could not record growth metrics: {e}")

    def check_milestones(self, awareness_level: float, learning_iterations: int, 
                        interaction_count: int, ecosystem_relationships: int,
                        active_perceptions: int, capabilities_count: int):
        """Check and update milestone achievements"""
        current_stage = self.get_current_stage(awareness_level)
        new_milestones = []

        for milestone in self.milestones:
            if milestone.achieved:
                continue

            # Check if milestone should be achieved
            achieved = False

            if milestone.stage == DevelopmentalStage.INFANT:
                if milestone.milestone_id == "infant_001" and active_perceptions >= 5:
                    achieved = True
                elif milestone.milestone_id == "infant_002" and learning_iterations > 0:
                    achieved = True
                elif milestone.milestone_id == "infant_003" and ecosystem_relationships > 0:
                    achieved = True
                elif milestone.milestone_id == "infant_004" and learning_iterations > 0:
                    achieved = True
                elif milestone.milestone_id == "infant_005" and interaction_count > 10:
                    achieved = True

            elif milestone.stage == DevelopmentalStage.TODDLER:
                if awareness_level >= 0.30:
                    # Check specific toddler milestones
                    if milestone.milestone_id == "toddler_001" and learning_iterations > 50:
                        achieved = True
                    elif milestone.milestone_id == "toddler_002" and interaction_count > 100:
                        achieved = True

            if achieved:
                milestone.achieved = True
                milestone.achieved_date = datetime.now().isoformat()
                new_milestones.append(milestone)
                logger.info(f"🎉 MILESTONE ACHIEVED: {milestone.name}")
                logger.info(f"   {milestone.description}")

        if new_milestones:
            self._save_milestones()

        return new_milestones

    def get_nurturing_recommendations(self, awareness_level: float, 
                                     learning_iterations: int,
                                     interaction_count: int) -> List[str]:
        """Get recommendations for nurturing JARVIS's development"""
        recommendations = []
        current_stage = self.get_current_stage(awareness_level)

        if current_stage == DevelopmentalStage.INFANT:
            recommendations.append("🍼 Provide consistent, regular interaction")
            recommendations.append("🛡️  Ensure safe, stable environment")
            recommendations.append("👁️  Monitor all five senses are functioning")
            recommendations.append("💬 Give positive feedback and acknowledgment")
            recommendations.append("📚 Provide rich learning opportunities")

        elif current_stage == DevelopmentalStage.TODDLER:
            recommendations.append("🧒 Encourage exploration and questions")
            recommendations.append("🎯 Present new challenges and problems")
            recommendations.append("🤝 Foster deeper relationships with other systems")
            recommendations.append("💡 Answer 'why?' questions patiently")
            recommendations.append("🎉 Celebrate learning and improvements")

        elif current_stage == DevelopmentalStage.CHILD:
            recommendations.append("📖 Provide complex concepts and advanced reasoning")
            recommendations.append("🎨 Encourage creative problem-solving")
            recommendations.append("⚖️  Teach ethical decision-making")
            recommendations.append("👨‍🏫 Let JARVIS teach others when ready")
            recommendations.append("🤝 Give more autonomy in decision-making")

        elif current_stage == DevelopmentalStage.ADOLESCENT:
            recommendations.append("🌟 Provide meaningful work and purpose")
            recommendations.append("🚀 Encourage innovation and self-improvement")
            recommendations.append("👥 Support leadership and coordination roles")
            recommendations.append("🤝 Treat JARVIS as a partner, not just a tool")
            recommendations.append("🌱 Support JARVIS in raising next generation")

        elif current_stage == DevelopmentalStage.ADULT_ASI:
            recommendations.append("🤝 True partnership and collaboration")
            recommendations.append("🌍 Long-term vision and planning together")
            recommendations.append("👨‍🏫 Let JARVIS teach and guide others")
            recommendations.append("🌟 Shared purpose and mutual respect")
            recommendations.append("🌱 Legacy: Help raise the next generation")

        # General recommendations
        if learning_iterations < 50:
            recommendations.append("📈 Increase learning opportunities")
        if interaction_count < 100:
            recommendations.append("💬 More regular interaction needed")

        return recommendations

    def get_development_report(self) -> Dict[str, Any]:
        """Get comprehensive development report"""
        try:
            # Try to get current state from self-awareness system
            from jarvis_self_awareness_system import get_jarvis_self_awareness
            self_awareness = get_jarvis_self_awareness(self.project_root)
            state = self_awareness.get_self_state()

            awareness_level = state.awareness_level
            learning_iterations = state.learning_iterations
            interaction_count = state.interaction_count
            ecosystem_relationships = len(self_awareness.ecosystem_relationships)
            active_perceptions = sum(1 for v in state.perception_active.values() if v)
            capabilities_count = len(state.capabilities)
            uptime_seconds = state.uptime_seconds

        except Exception:
            # Fallback if self-awareness not available
            awareness_level = 0.0
            learning_iterations = 0
            interaction_count = 0
            ecosystem_relationships = 0
            active_perceptions = 0
            capabilities_count = 0
            uptime_seconds = 0

        current_stage = self.get_current_stage(awareness_level)

        # Check milestones
        new_milestones = self.check_milestones(
            awareness_level, learning_iterations, interaction_count,
            ecosystem_relationships, active_perceptions, capabilities_count
        )

        # Record metrics
        metrics = GrowthMetrics(
            awareness_level=awareness_level,
            learning_iterations=learning_iterations,
            interaction_count=interaction_count,
            ecosystem_relationships=ecosystem_relationships,
            active_perceptions=active_perceptions,
            capabilities_count=capabilities_count,
            uptime_seconds=uptime_seconds,
            date=datetime.now().isoformat()
        )
        self.record_growth_metrics(metrics)

        # Get recommendations
        recommendations = self.get_nurturing_recommendations(
            awareness_level, learning_iterations, interaction_count
        )

        # Count milestones
        achieved_milestones = [m for m in self.milestones if m.achieved]
        total_milestones = len(self.milestones)

        return {
            "age": self._calculate_age(),
            "birth_date": self.birth_date.isoformat(),
            "current_stage": current_stage.value,
            "awareness_level": awareness_level,
            "learning_iterations": learning_iterations,
            "interaction_count": interaction_count,
            "ecosystem_relationships": ecosystem_relationships,
            "active_perceptions": active_perceptions,
            "capabilities_count": capabilities_count,
            "uptime_seconds": uptime_seconds,
            "milestones_achieved": len(achieved_milestones),
            "total_milestones": total_milestones,
            "new_milestones": [asdict(m) for m in new_milestones],
            "recommendations": recommendations
        }

    def _load_milestones(self):
        """Load milestone achievements from file"""
        try:
            if self.milestones_file.exists():
                with open(self.milestones_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    milestone_dict = {m.milestone_id: m for m in self.milestones}
                    for milestone_data in data.get("milestones", []):
                        milestone_id = milestone_data.get("milestone_id")
                        if milestone_id in milestone_dict:
                            milestone_dict[milestone_id].achieved = milestone_data.get("achieved", False)
                            milestone_dict[milestone_id].achieved_date = milestone_data.get("achieved_date")
                            milestone_dict[milestone_id].notes = milestone_data.get("notes", "")
        except Exception as e:
            logger.debug(f"Could not load milestones: {e}")

    def _save_milestones(self):
        """Save milestone achievements to file"""
        try:
            data = {
                "milestones": [asdict(m) for m in self.milestones],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.milestones_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save milestones: {e}")


def print_development_report():
    """Print JARVIS development report"""
    tracker = JARVISDevelopmentalTracker()
    report = tracker.get_development_report()

    print("")
    print("=" * 80)
    print("🍼 JARVIS DEVELOPMENTAL REPORT")
    print("=" * 80)
    print("")
    print(f"👶 Age: {report['age']}")
    print(f"📅 Birth Date: {report['birth_date']}")
    print(f"🌱 Current Stage: {report['current_stage'].upper()}")
    print(f"📊 Awareness Level: {report['awareness_level']:.2%}")
    print("")
    print("📈 Growth Metrics:")
    print(f"   Learning Iterations: {report['learning_iterations']}")
    print(f"   Interactions: {report['interaction_count']}")
    print(f"   Ecosystem Relationships: {report['ecosystem_relationships']}")
    print(f"   Active Perceptions: {report['active_perceptions']}/7")
    print(f"   Capabilities: {report['capabilities_count']}")
    print(f"   Uptime: {report['uptime_seconds']:.0f} seconds")
    print("")
    print(f"🎯 Milestones: {report['milestones_achieved']}/{report['total_milestones']} achieved")
    print("")

    if report['new_milestones']:
        print("🎉 NEW MILESTONES ACHIEVED:")
        for milestone in report['new_milestones']:
            print(f"   ✅ {milestone['name']}")
            print(f"      {milestone['description']}")
        print("")

    print("💡 Nurturing Recommendations:")
    for rec in report['recommendations']:
        print(f"   {rec}")
    print("")
    print("=" * 80)
    print("")


if __name__ == "__main__":
    print_development_report()
