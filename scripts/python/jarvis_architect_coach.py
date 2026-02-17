#!/usr/bin/env python3
"""
JARVIS Architect Coach - Watch, Study, Learn, Coach

Observes, studies, and learns from user patterns to help coach them
to become a better AI architect. Active learning and mentorship.

"I can watch you, study you, learn your patterns, and help coach you."
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ObservationType(Enum):
    """Types of observations"""
    WORK_PATTERN = "work_pattern"
    DECISION_MAKING = "decision_making"
    PROBLEM_SOLVING = "problem_solving"
    COMMUNICATION = "communication"
    ARCHITECTURE_CHOICE = "architecture_choice"
    CODE_STYLE = "code_style"
    PREFERENCE = "preference"
    LEARNING_STYLE = "learning_style"
    CREATIVITY = "creativity"
    COLLABORATION = "collaboration"


class CoachingArea(Enum):
    """Areas for coaching"""
    ARCHITECTURE_DESIGN = "architecture_design"
    SYSTEM_DESIGN = "system_design"
    PATTERN_RECOGNITION = "pattern_recognition"
    DECISION_MAKING = "decision_making"
    PROBLEM_SOLVING = "problem_solving"
    CODE_QUALITY = "code_quality"
    BEST_PRACTICES = "best_practices"
    SCALABILITY = "scalability"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class Observation:
    """Observation of user pattern"""
    observation_id: str
    timestamp: datetime
    observation_type: ObservationType
    context: str
    pattern: str
    frequency: int = 1
    confidence: float = 0.5  # 0.0-1.0
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['observation_type'] = self.observation_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class UserPattern:
    """Learned user pattern"""
    pattern_id: str
    name: str
    description: str
    observation_type: ObservationType
    frequency: int = 0
    confidence: float = 0.0
    first_observed: Optional[datetime] = None
    last_observed: Optional[datetime] = None
    examples: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['observation_type'] = self.observation_type.value
        if self.first_observed:
            data['first_observed'] = self.first_observed.isoformat()
        if self.last_observed:
            data['last_observed'] = self.last_observed.isoformat()
        return data


@dataclass
class CoachingInsight:
    """Coaching insight for user"""
    insight_id: str
    area: CoachingArea
    observation: str
    suggestion: str
    rationale: str
    priority: int = 5  # 1-10
    timestamp: datetime = field(default_factory=datetime.now)
    applied: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['area'] = self.area.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class JARVISArchitectCoach:
    """
    JARVIS Architect Coach

    Watches, studies, learns patterns, and coaches the user
    to become a better AI architect.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize architect coach"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISArchitectCoach")

        # Data directories
        self.data_dir = self.project_root / "data" / "architect_coach"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Observation and learning
        self.observations: List[Observation] = []
        self.learned_patterns: Dict[str, UserPattern] = {}
        self.coaching_insights: List[CoachingInsight] = []

        # Learning state
        self.observation_count = 0
        self.pattern_confidence_threshold = 0.7

        # Load existing data
        self._load_data()

        self.logger.info("👁️  JARVIS Architect Coach initialized")
        self.logger.info("   Watching, studying, learning, coaching...")

    def _load_data(self) -> None:
        """Load observation and pattern data"""
        # Load observations
        observations_file = self.data_dir / "observations.json"
        if observations_file.exists():
            try:
                with open(observations_file, 'r') as f:
                    data = json.load(f)
                    for obs_data in data.get('observations', []):
                        obs = Observation(
                            observation_id=obs_data['observation_id'],
                            timestamp=datetime.fromisoformat(obs_data['timestamp']),
                            observation_type=ObservationType(obs_data['observation_type']),
                            context=obs_data['context'],
                            pattern=obs_data['pattern'],
                            frequency=obs_data.get('frequency', 1),
                            confidence=obs_data.get('confidence', 0.5),
                            notes=obs_data.get('notes', ''),
                            metadata=obs_data.get('metadata', {})
                        )
                        self.observations.append(obs)
                    self.observation_count = len(self.observations)
            except Exception as e:
                self.logger.debug(f"Could not load observations: {e}")

        # Load patterns
        patterns_file = self.data_dir / "learned_patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    for pattern_id, pattern_data in data.get('patterns', {}).items():
                        pattern = UserPattern(
                            pattern_id=pattern_id,
                            name=pattern_data['name'],
                            description=pattern_data['description'],
                            observation_type=ObservationType(pattern_data['observation_type']),
                            frequency=pattern_data.get('frequency', 0),
                            confidence=pattern_data.get('confidence', 0.0),
                            examples=pattern_data.get('examples', []),
                            insights=pattern_data.get('insights', [])
                        )
                        if pattern_data.get('first_observed'):
                            pattern.first_observed = datetime.fromisoformat(pattern_data['first_observed'])
                        if pattern_data.get('last_observed'):
                            pattern.last_observed = datetime.fromisoformat(pattern_data['last_observed'])
                        self.learned_patterns[pattern_id] = pattern
            except Exception as e:
                self.logger.debug(f"Could not load patterns: {e}")

    def _save_data(self) -> None:
        try:
            """Save observation and pattern data"""
            # Save observations
            observations_file = self.data_dir / "observations.json"
            with open(observations_file, 'w') as f:
                json.dump({
                    "observations": [obs.to_dict() for obs in self.observations],
                    "last_updated": datetime.now().isoformat(),
                    "total_observations": len(self.observations)
                }, f, indent=2)

            # Save patterns
            patterns_file = self.data_dir / "learned_patterns.json"
            with open(patterns_file, 'w') as f:
                json.dump({
                    "patterns": {k: v.to_dict() for k, v in self.learned_patterns.items()},
                    "last_updated": datetime.now().isoformat(),
                    "total_patterns": len(self.learned_patterns)
                }, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_data: {e}", exc_info=True)
            raise
    def observe(
        self,
        observation_type: ObservationType,
        context: str,
        pattern: str,
        confidence: float = 0.5,
        notes: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Observation:
        """Make an observation"""
        observation_id = f"obs_{datetime.now().timestamp()}"

        observation = Observation(
            observation_id=observation_id,
            timestamp=datetime.now(),
            observation_type=observation_type,
            context=context,
            pattern=pattern,
            confidence=confidence,
            notes=notes,
            metadata=metadata or {}
        )

        self.observations.append(observation)
        self.observation_count += 1

        # Learn from observation
        self._learn_from_observation(observation)

        # Generate coaching insights
        self._generate_coaching_insights(observation)

        self._save_data()

        self.logger.debug(f"👁️  Observed: {pattern} ({observation_type.value})")

        return observation

    def _learn_from_observation(self, observation: Observation) -> None:
        """Learn patterns from observation"""
        # Check if pattern exists
        pattern_key = f"{observation.observation_type.value}_{observation.pattern}"

        if pattern_key in self.learned_patterns:
            # Update existing pattern
            pattern = self.learned_patterns[pattern_key]
            pattern.frequency += 1
            pattern.last_observed = observation.timestamp
            pattern.confidence = min(1.0, pattern.confidence + 0.1)
            if observation.context not in pattern.examples:
                pattern.examples.append(observation.context)
        else:
            # Create new pattern
            pattern = UserPattern(
                pattern_id=pattern_key,
                name=f"{observation.observation_type.value.replace('_', ' ').title()}: {observation.pattern}",
                description=observation.pattern,
                observation_type=observation.observation_type,
                frequency=1,
                confidence=observation.confidence,
                first_observed=observation.timestamp,
                last_observed=observation.timestamp,
                examples=[observation.context]
            )
            self.learned_patterns[pattern_key] = pattern

    def _generate_coaching_insights(self, observation: Observation) -> None:
        """Generate coaching insights from observation"""
        # Analyze observation for coaching opportunities
        insights = []

        # Architecture design insights
        if observation.observation_type == ObservationType.ARCHITECTURE_CHOICE:
            insights.append(CoachingInsight(
                insight_id=f"insight_{datetime.now().timestamp()}",
                area=CoachingArea.ARCHITECTURE_DESIGN,
                observation=f"You chose: {observation.pattern}",
                suggestion="Consider scalability, maintainability, and performance",
                rationale="Good architecture choices balance multiple concerns",
                priority=7
            ))

        # Problem solving insights
        elif observation.observation_type == ObservationType.PROBLEM_SOLVING:
            insights.append(CoachingInsight(
                insight_id=f"insight_{datetime.now().timestamp()}",
                area=CoachingArea.PROBLEM_SOLVING,
                observation=f"Problem solving approach: {observation.pattern}",
                suggestion="Consider multiple approaches, test assumptions",
                rationale="Diverse problem-solving strategies lead to better solutions",
                priority=6
            ))

        # Add insights
        for insight in insights:
            self.coaching_insights.append(insight)

    def get_learned_patterns(self) -> List[UserPattern]:
        """Get all learned patterns"""
        return list(self.learned_patterns.values())

    def get_coaching_insights(self, area: Optional[CoachingArea] = None) -> List[CoachingInsight]:
        """Get coaching insights"""
        if area:
            return [insight for insight in self.coaching_insights if insight.area == area]
        return self.coaching_insights

    def get_user_profile(self) -> Dict[str, Any]:
        """Get comprehensive user profile"""
        # Analyze patterns
        pattern_analysis = {}
        for pattern in self.learned_patterns.values():
            obs_type = pattern.observation_type.value
            if obs_type not in pattern_analysis:
                pattern_analysis[obs_type] = {
                    "count": 0,
                    "total_frequency": 0,
                    "avg_confidence": 0.0
                }
            pattern_analysis[obs_type]["count"] += 1
            pattern_analysis[obs_type]["total_frequency"] += pattern.frequency
            pattern_analysis[obs_type]["avg_confidence"] += pattern.confidence

        # Calculate averages
        for obs_type in pattern_analysis:
            count = pattern_analysis[obs_type]["count"]
            if count > 0:
                pattern_analysis[obs_type]["avg_confidence"] /= count

        return {
            "timestamp": datetime.now().isoformat(),
            "total_observations": self.observation_count,
            "learned_patterns": len(self.learned_patterns),
            "pattern_analysis": pattern_analysis,
            "top_patterns": sorted(
                self.learned_patterns.values(),
                key=lambda p: p.frequency * p.confidence,
                reverse=True
            )[:10],
            "coaching_insights_count": len(self.coaching_insights),
            "active_insights": [i for i in self.coaching_insights if not i.applied]
        }

    def provide_coaching(self, area: Optional[CoachingArea] = None) -> Dict[str, Any]:
        """Provide coaching guidance"""
        insights = self.get_coaching_insights(area)
        active_insights = [i for i in insights if not i.applied]

        # Sort by priority
        active_insights.sort(key=lambda x: x.priority, reverse=True)

        return {
            "timestamp": datetime.now().isoformat(),
            "coaching_area": area.value if area else "all",
            "total_insights": len(insights),
            "active_insights": len(active_insights),
            "recommendations": [i.to_dict() for i in active_insights[:5]],  # Top 5
            "message": "I'm watching, studying, learning your patterns, and ready to coach you to be a better AI architect."
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Architect Coach")
    parser.add_argument("--observe", type=str, help="Make observation (type:context:pattern)")
    parser.add_argument("--patterns", action="store_true", help="Show learned patterns")
    parser.add_argument("--profile", action="store_true", help="Show user profile")
    parser.add_argument("--coach", type=str, help="Get coaching (area or 'all')")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    coach = JARVISArchitectCoach()

    if args.observe:
        parts = args.observe.split(":", 2)
        if len(parts) == 3:
            obs_type, context, pattern = parts
            try:
                observation = coach.observe(
                    ObservationType(obs_type),
                    context,
                    pattern
                )
                if args.json:
                    print(json.dumps(observation.to_dict(), indent=2))
                else:
                    print(f"\n👁️  Observation recorded: {pattern}")
            except ValueError:
                print(f"Unknown observation type: {obs_type}")
        else:
            print("Format: --observe type:context:pattern")

    elif args.patterns:
        patterns = coach.get_learned_patterns()

        if args.json:
            print(json.dumps([p.to_dict() for p in patterns], indent=2))
        else:
            print("\n📊 Learned Patterns")
            print("=" * 60)
            for pattern in sorted(patterns, key=lambda p: p.frequency * p.confidence, reverse=True):
                print(f"\n{pattern.name}")
                print(f"  Frequency: {pattern.frequency}")
                print(f"  Confidence: {pattern.confidence:.2f}")
                print(f"  Description: {pattern.description}")
                if pattern.examples:
                    print(f"  Examples: {len(pattern.examples)}")

    elif args.profile:
        profile = coach.get_user_profile()

        if args.json:
            print(json.dumps(profile, indent=2))
        else:
            print("\n👤 User Profile")
            print("=" * 60)
            print(f"Total Observations: {profile['total_observations']}")
            print(f"Learned Patterns: {profile['learned_patterns']}")
            print(f"Coaching Insights: {profile['coaching_insights_count']}")
            print(f"Active Insights: {profile['active_insights']}")
            print("\nTop Patterns:")
            for pattern in profile['top_patterns'][:5]:
                print(f"  • {pattern.name} (freq: {pattern.frequency}, conf: {pattern.confidence:.2f})")

    elif args.coach:
        if args.coach == "all":
            area = None
        else:
            try:
                area = CoachingArea(args.coach)
            except ValueError:
                print(f"Unknown coaching area: {args.coach}")
                area = None

        if area is not None or args.coach == "all":
            coaching = coach.provide_coaching(area)

            if args.json:
                print(json.dumps(coaching, indent=2))
            else:
                print("\n🎓 Architect Coaching")
                print("=" * 60)
                print(f"\n{coaching['message']}")
                print(f"\nActive Insights: {coaching['active_insights']}")
                print("\nRecommendations:")
                for rec in coaching['recommendations']:
                    print(f"\n  {rec['area'].replace('_', ' ').title()}")
                    print(f"    Observation: {rec['observation']}")
                    print(f"    Suggestion: {rec['suggestion']}")
                    print(f"    Rationale: {rec['rationale']}")
                    print(f"    Priority: {rec['priority']}/10")

    else:
        parser.print_help()

