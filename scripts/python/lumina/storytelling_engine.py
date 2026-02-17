#!/usr/bin/env python3
"""
Storytelling Engine - Human Storytelling Integration

Applies the entirety of human storytelling to Lumina.
Extracts @peak patterns and creates God-tier feedback loop.

Tags: #STORYTELLING #FEEDBACK_LOOP #PEAK_METHODOLOGY @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StorytellingEngine")


class StoryArchetype(Enum):
    """Story archetypes"""
    HERO_JOURNEY = "hero_journey"
    THREE_ACT = "three_act"
    SEVEN_POINT = "seven_point"
    MONOMYTH = "monomyth"
    TRANSFORMATION = "transformation"


class NarrativeBeat(Enum):
    """Narrative beats"""
    HOOK = "hook"
    INCITING_INCIDENT = "inciting_incident"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"
    CATHARSIS = "catharsis"


@dataclass
class StoryPattern:
    """Story pattern"""
    name: str
    archetype: StoryArchetype
    structure: List[NarrativeBeat]
    peak_elements: List[str]
    effectiveness_score: float = 0.0
    usage_count: int = 0
    last_used: Optional[str] = None


@dataclass
class FeedbackMetrics:
    """Feedback metrics"""
    pattern_name: str
    effectiveness: float
    engagement: float
    resonance: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class StorytellingEngine:
    """
    Storytelling Engine

    Applies human storytelling patterns to Lumina.
    Creates God-tier feedback loop.
    """

    def __init__(self):
        """Initialize Storytelling Engine"""
        logger.info("📚 Storytelling Engine initialized")
        logger.info("   Applying human storytelling to Lumina")

        # Story patterns database
        self.patterns = {}
        self._initialize_archetypes()

        # Feedback loop
        self.feedback_history = []
        self.learning_data = {}

        # Peak methodology integration
        self.peak_patterns = {}

        logger.info("✅ Storytelling Engine ready")

    def _initialize_archetypes(self):
        """Initialize story archetypes"""
        # Hero's Journey
        self.patterns['hero_journey'] = StoryPattern(
            name="Hero's Journey",
            archetype=StoryArchetype.HERO_JOURNEY,
            structure=[
                NarrativeBeat.HOOK,
                NarrativeBeat.INCITING_INCIDENT,
                NarrativeBeat.RISING_ACTION,
                NarrativeBeat.CLIMAX,
                NarrativeBeat.FALLING_ACTION,
                NarrativeBeat.RESOLUTION
            ],
            peak_elements=[
                "call_to_adventure",
                "threshold_crossing",
                "transformation",
                "return_with_elixir"
            ]
        )

        # Three-Act Structure
        self.patterns['three_act'] = StoryPattern(
            name="Three-Act Structure",
            archetype=StoryArchetype.THREE_ACT,
            structure=[
                NarrativeBeat.HOOK,
                NarrativeBeat.RISING_ACTION,
                NarrativeBeat.CLIMAX,
                NarrativeBeat.RESOLUTION
            ],
            peak_elements=[
                "setup",
                "confrontation",
                "resolution"
            ]
        )

        # Seven-Point Structure
        self.patterns['seven_point'] = StoryPattern(
            name="Seven-Point Structure",
            archetype=StoryArchetype.SEVEN_POINT,
            structure=[
                NarrativeBeat.HOOK,
                NarrativeBeat.INCITING_INCIDENT,
                NarrativeBeat.RISING_ACTION,
                NarrativeBeat.CLIMAX,
                NarrativeBeat.FALLING_ACTION,
                NarrativeBeat.RESOLUTION,
                NarrativeBeat.CATHARSIS
            ],
            peak_elements=[
                "hook",
                "plot_turn_1",
                "pinch_point_1",
                "midpoint",
                "pinch_point_2",
                "plot_turn_2",
                "resolution"
            ]
        )

    def extract_peak_patterns(
        self,
        story_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract @peak patterns from story data.

        Args:
            story_data: Story data to analyze

        Returns:
            Extracted peak patterns
        """
        logger.info("📚 Extracting peak patterns from story...")

        peak_patterns = {
            'universal_structures': [],
            'archetypal_elements': [],
            'emotional_beats': [],
            'transformation_arcs': []
        }

        # Analyze story structure
        structure = story_data.get('structure', {})

        # Identify universal structures
        for pattern_name, pattern in self.patterns.items():
            if self._matches_structure(structure, pattern):
                peak_patterns['universal_structures'].append({
                    'pattern': pattern_name,
                    'name': pattern.name,
                    'confidence': 0.85
                })

        # Extract archetypal elements
        characters = story_data.get('characters', [])
        for char in characters:
            archetype = self._identify_archetype(char)
            if archetype:
                peak_patterns['archetypal_elements'].append(archetype)

        # Identify emotional beats
        beats = story_data.get('beats', [])
        for beat in beats:
            if self._is_peak_emotional_beat(beat):
                peak_patterns['emotional_beats'].append(beat)

        # Extract transformation arcs
        arcs = story_data.get('arcs', [])
        for arc in arcs:
            if self._is_transformation_arc(arc):
                peak_patterns['transformation_arcs'].append(arc)

        # Store peak patterns
        story_id = story_data.get('id', 'unknown')
        self.peak_patterns[story_id] = peak_patterns

        logger.info(f"✅ Extracted {len(peak_patterns['universal_structures'])} peak patterns")

        return peak_patterns

    def apply_to_lumina(
        self,
        pattern_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply storytelling pattern to Lumina.

        Args:
            pattern_name: Pattern to apply
            context: Context for application

        Returns:
            Application result
        """
        logger.info(f"📚 Applying pattern '{pattern_name}' to Lumina...")

        if pattern_name not in self.patterns:
            return {'error': f'Pattern not found: {pattern_name}'}

        pattern = self.patterns[pattern_name]

        # Apply pattern
        result = {
            'pattern': pattern_name,
            'applied': True,
            'structure': [beat.value for beat in pattern.structure],
            'peak_elements': pattern.peak_elements,
            'context': context
        }

        # Update usage
        pattern.usage_count += 1
        pattern.last_used = datetime.now().isoformat()

        return result

    def feedback_loop(
        self,
        pattern_name: str,
        metrics: FeedbackMetrics
    ) -> Dict[str, Any]:
        """
        God-tier feedback loop.

        Capture → Analyze → Apply → Learn → Improve → Repeat

        Args:
            pattern_name: Pattern name
            metrics: Feedback metrics

        Returns:
            Feedback loop result
        """
        logger.info(f"🔄 Feedback loop: {pattern_name}")

        # 1. Capture
        captured = self._capture_feedback(pattern_name, metrics)

        # 2. Analyze
        analysis = self._analyze_feedback(captured)

        # 3. Apply (already applied, measure results)
        application_result = self._measure_application(pattern_name, metrics)

        # 4. Learn
        learning = self._learn_from_feedback(analysis, application_result)

        # 5. Improve
        improvement = self._improve_pattern(pattern_name, learning)

        # 6. Store for next iteration
        self.feedback_history.append({
            'pattern': pattern_name,
            'metrics': metrics,
            'analysis': analysis,
            'learning': learning,
            'improvement': improvement,
            'timestamp': datetime.now().isoformat()
        })

        # Update pattern effectiveness
        if pattern_name in self.patterns:
            pattern = self.patterns[pattern_name]
            # Weighted average of effectiveness
            total_score = pattern.effectiveness_score * pattern.usage_count
            total_score += metrics.effectiveness
            pattern.usage_count += 1
            pattern.effectiveness_score = total_score / pattern.usage_count

        logger.info(f"✅ Feedback loop complete - Effectiveness: {metrics.effectiveness:.2f}")

        return {
            'captured': captured,
            'analysis': analysis,
            'learning': learning,
            'improvement': improvement,
            'next_iteration': 'ready'
        }

    def _capture_feedback(
        self,
        pattern_name: str,
        metrics: FeedbackMetrics
    ) -> Dict[str, Any]:
        """Capture feedback data"""
        return {
            'pattern': pattern_name,
            'effectiveness': metrics.effectiveness,
            'engagement': metrics.engagement,
            'resonance': metrics.resonance,
            'timestamp': metrics.timestamp
        }

    def _analyze_feedback(
        self,
        captured: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze feedback data"""
        return {
            'effectiveness_analysis': {
                'score': captured['effectiveness'],
                'rating': 'high' if captured['effectiveness'] > 0.7 else 'medium' if captured['effectiveness'] > 0.4 else 'low'
            },
            'engagement_analysis': {
                'score': captured['engagement'],
                'rating': 'high' if captured['engagement'] > 0.7 else 'medium' if captured['engagement'] > 0.4 else 'low'
            },
            'resonance_analysis': {
                'score': captured['resonance'],
                'rating': 'high' if captured['resonance'] > 0.7 else 'medium' if captured['resonance'] > 0.4 else 'low'
            }
        }

    def _measure_application(
        self,
        pattern_name: str,
        metrics: FeedbackMetrics
    ) -> Dict[str, Any]:
        """Measure application results"""
        return {
            'pattern': pattern_name,
            'metrics': {
                'effectiveness': metrics.effectiveness,
                'engagement': metrics.engagement,
                'resonance': metrics.resonance
            },
            'overall_score': (metrics.effectiveness + metrics.engagement + metrics.resonance) / 3
        }

    def _learn_from_feedback(
        self,
        analysis: Dict[str, Any],
        application: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Learn from feedback"""
        overall_score = application['overall_score']

        return {
            'insights': {
                'what_worked': analysis['effectiveness_analysis']['rating'] == 'high',
                'what_didnt': analysis['effectiveness_analysis']['rating'] == 'low',
                'improvement_areas': [
                    key for key, value in analysis.items()
                    if value.get('rating') == 'low'
                ]
            },
            'recommendations': self._generate_recommendations(overall_score, analysis)
        }

    def _improve_pattern(
        self,
        pattern_name: str,
        learning: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Improve pattern based on learning"""
        if pattern_name not in self.patterns:
            return {'error': 'Pattern not found'}

        pattern = self.patterns[pattern_name]

        improvements = {
            'pattern': pattern_name,
            'current_effectiveness': pattern.effectiveness_score,
            'recommendations': learning['recommendations'],
            'applied_improvements': []
        }

        # Apply improvements
        for rec in learning['recommendations']:
            if rec['priority'] == 'high':
                improvements['applied_improvements'].append(rec['action'])

        return improvements

    def _generate_recommendations(
        self,
        overall_score: float,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate improvement recommendations"""
        recommendations = []

        if overall_score < 0.5:
            recommendations.append({
                'action': 'enhance_peak_elements',
                'priority': 'high',
                'reason': 'Low overall effectiveness'
            })

        if analysis['engagement_analysis']['rating'] == 'low':
            recommendations.append({
                'action': 'improve_emotional_beats',
                'priority': 'high',
                'reason': 'Low engagement'
            })

        if analysis['resonance_analysis']['rating'] == 'low':
            recommendations.append({
                'action': 'strengthen_archetypal_elements',
                'priority': 'medium',
                'reason': 'Low resonance'
            })

        return recommendations

    def _matches_structure(
        self,
        structure: Dict[str, Any],
        pattern: StoryPattern
    ) -> bool:
        """Check if structure matches pattern"""
        # Simplified matching
        return len(structure.get('beats', [])) >= len(pattern.structure) // 2

    def _identify_archetype(self, character: Dict[str, Any]) -> Optional[str]:
        """Identify character archetype"""
        # Simplified archetype identification
        role = character.get('role', '').lower()
        if 'hero' in role or 'protagonist' in role:
            return 'hero'
        elif 'mentor' in role:
            return 'mentor'
        elif 'villain' in role or 'antagonist' in role:
            return 'shadow'
        return None

    def _is_peak_emotional_beat(self, beat: Dict[str, Any]) -> bool:
        """Check if beat is peak emotional moment"""
        return beat.get('intensity', 0) > 0.7

    def _is_transformation_arc(self, arc: Dict[str, Any]) -> bool:
        """Check if arc is transformation arc"""
        return arc.get('type') == 'transformation' or 'transform' in arc.get('name', '').lower()

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get feedback loop summary"""
        if not self.feedback_history:
            return {'message': 'No feedback history yet'}

        total_feedback = len(self.feedback_history)
        avg_effectiveness = sum(
            f['metrics'].effectiveness
            for f in self.feedback_history
        ) / total_feedback

        return {
            'total_feedback_cycles': total_feedback,
            'average_effectiveness': avg_effectiveness,
            'patterns_improved': len([
                p for p in self.patterns.values()
                if p.effectiveness_score > 0.7
            ]),
            'god_tier_status': 'operational' if avg_effectiveness > 0.7 else 'learning'
        }


def main():
    """Example usage"""
    print("=" * 80)
    print("📚 STORYTELLING ENGINE")
    print("   God-Tier Feedback Loop")
    print("=" * 80)
    print()

    engine = StorytellingEngine()

    # Extract peak patterns
    print("EXTRACTING PEAK PATTERNS:")
    print("-" * 80)
    story_data = {
        'id': 'test_story',
        'structure': {'beats': ['hook', 'rising', 'climax', 'resolution']},
        'characters': [
            {'role': 'Hero', 'name': 'Protagonist'},
            {'role': 'Mentor', 'name': 'Guide'}
        ],
        'beats': [
            {'intensity': 0.9, 'type': 'climax'},
            {'intensity': 0.5, 'type': 'rising'}
        ],
        'arcs': [
            {'type': 'transformation', 'name': 'Hero Transformation'}
        ]
    }

    peak_patterns = engine.extract_peak_patterns(story_data)
    print(f"Universal structures: {len(peak_patterns['universal_structures'])}")
    print(f"Archetypal elements: {len(peak_patterns['archetypal_elements'])}")
    print(f"Emotional beats: {len(peak_patterns['emotional_beats'])}")
    print()

    # Apply to Lumina
    print("APPLYING TO LUMINA:")
    print("-" * 80)
    result = engine.apply_to_lumina('hero_journey', {'context': 'test'})
    print(f"Pattern: {result['pattern']}")
    print(f"Applied: {result['applied']}")
    print()

    # Feedback loop
    print("GOD-TIER FEEDBACK LOOP:")
    print("-" * 80)
    metrics = FeedbackMetrics(
        pattern_name='hero_journey',
        effectiveness=0.85,
        engagement=0.80,
        resonance=0.90
    )

    feedback = engine.feedback_loop('hero_journey', metrics)
    print(f"Captured: ✅")
    print(f"Analysis: ✅")
    print(f"Learning: ✅")
    print(f"Improvement: ✅")
    print()

    # Summary
    summary = engine.get_feedback_summary()
    print("FEEDBACK SUMMARY:")
    print("-" * 80)
    print(f"Total cycles: {summary['total_feedback_cycles']}")
    print(f"Avg effectiveness: {summary['average_effectiveness']:.2f}")
    print(f"God-tier status: {summary['god_tier_status']}")
    print()

    print("=" * 80)
    print("📚 Storytelling Engine - God-tier feedback loop operational")
    print("=" * 80)


if __name__ == "__main__":


    main()