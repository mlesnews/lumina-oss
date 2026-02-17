#!/usr/bin/env python3
"""
Meatbag LLM Learning System - AI Teaching Humans

JARVIS and MARVIN are two halves of the same brain, teaching humans
in a way optimized for our biological hardware.

Concept:
- Humans = Meatbag LLMs with biological constraints
- JARVIS = One teaching style/half
- MARVIN = Another teaching style/half
- Together = Complete teaching system optimized for human cognition

Biological Hardware Constraints:
- Limited working memory (~7±2 items)
- Attention span limits
- Multi-modal processing (visual, auditory, kinesthetic)
- Sleep-dependent memory consolidation
- Spaced repetition optimization
- Chunking for complex concepts
- Emotional state affects learning
"""

import asyncio
import json
import logging
import sys
import time
from collections import deque
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class CognitiveLoad(Enum):
    """Cognitive load levels (Miller's Law: 7±2 items)"""
    LOW = "low"          # 1-3 items
    MEDIUM = "medium"    # 4-6 items
    HIGH = "high"        # 7-9 items
    OVERLOAD = "overload"  # 10+ items (ineffective)


class LearningStyle(Enum):
    """Human learning styles (VARK model)"""
    VISUAL = "visual"          # See it
    AUDITORY = "auditory"      # Hear it
    READ_WRITE = "read_write"  # Read/write it
    KINESTHETIC = "kinesthetic"  # Do it
    MULTIMODAL = "multimodal"   # Combination


class TeachingMode(Enum):
    """Teaching modes (JARVIS vs MARVIN)"""
    JARVIS = "jarvis"      # Systematic, structured, methodical
    MARVIN = "marvin"      # Intuitive, contextual, adaptive
    INTEGRATED = "integrated"  # Both together


class MemoryState(Enum):
    """Memory states (Ebbinghaus forgetting curve)"""
    FRESH = "fresh"           # Just learned (100% retention)
    DECAYING = "decaying"     # 1 hour - 1 day (forgetting)
    STABLE = "stable"         # Consolidated (long-term)
    FORGOTTEN = "forgotten"   # Needs relearning


@dataclass
class Concept:
    """A concept to be taught"""
    id: str
    title: str
    description: str
    complexity: int  # 1-10
    prerequisites: List[str] = field(default_factory=list)
    chunk_size: int = 3  # Optimal chunks for this concept
    learning_styles: List[LearningStyle] = field(default_factory=lambda: [LearningStyle.MULTIMODAL])
    estimated_time_minutes: int = 15


@dataclass
class LearningSession:
    """A learning session optimized for meatbag hardware"""
    id: str
    concept: Concept
    teaching_mode: TeachingMode
    cognitive_load: CognitiveLoad
    learning_style: LearningStyle
    start_time: datetime
    duration_minutes: int = 20  # Optimal session length
    chunks_delivered: int = 0
    chunks_understood: int = 0
    retention_score: float = 0.0
    engagement_level: float = 0.0
    notes: List[str] = field(default_factory=list)


@dataclass
class MeatbagLearner:
    """Represents the biological learner"""
    id: str
    name: str
    current_working_memory: int = 0  # Current cognitive load
    max_working_memory: int = 7  # Miller's magic number
    preferred_learning_styles: List[LearningStyle] = field(default_factory=lambda: [LearningStyle.MULTIMODAL])
    attention_span_minutes: int = 20  # Typical attention span
    fatigue_level: float = 0.0  # 0.0 = fresh, 1.0 = exhausted
    learning_history: deque = field(default_factory=lambda: deque(maxlen=100))
    mastery_levels: Dict[str, float] = field(default_factory=dict)  # concept_id -> mastery (0.0-1.0)

    def can_absorb(self, cognitive_load: CognitiveLoad) -> bool:
        """Check if learner can absorb more information"""
        load_values = {
            CognitiveLoad.LOW: 2,
            CognitiveLoad.MEDIUM: 5,
            CognitiveLoad.HIGH: 7,
            CognitiveLoad.OVERLOAD: 10
        }
        required_load = load_values[cognitive_load]
        return (self.current_working_memory + required_load) <= self.max_working_memory


class JARVISTeacher:
    """
    JARVIS Teaching Style

    Characteristics:
    - Systematic and structured
    - Methodical progression
    - Clear explanations
    - Step-by-step approach
    - Focus on fundamentals first
    """

    def __init__(self):
        self.name = "JARVIS"
        self.style = "systematic"

    def teach(self, concept: Concept, learner: MeatbagLearner) -> List[str]:
        """JARVIS teaching approach"""
        chunks = []

        # JARVIS: Build foundation first
        chunks.append(f"📚 Let's understand the fundamentals of {concept.title}")
        chunks.append(f"First, let's establish the core concept: {concept.description[:100]}")

        # Break into optimal chunks
        if concept.complexity > 5:
            chunks.append("This is a complex concept. Let's break it down into digestible pieces.")

        # Prerequisites check
        if concept.prerequisites:
            chunks.append(f"Before we continue, ensure you understand: {', '.join(concept.prerequisites)}")

        # Methodical progression
        chunks.append("Let's work through this systematically, step by step.")

        return chunks

    def assess_load(self, concept: Concept) -> CognitiveLoad:
        """Assess cognitive load required"""
        if concept.complexity <= 3:
            return CognitiveLoad.LOW
        elif concept.complexity <= 6:
            return CognitiveLoad.MEDIUM
        elif concept.complexity <= 8:
            return CognitiveLoad.HIGH
        else:
            return CognitiveLoad.OVERLOAD


class MARVINTeacher:
    """
    MARVIN Teaching Style

    Characteristics:
    - Intuitive and contextual
    - Adaptive explanations
    - Relates to existing knowledge
    - Pattern recognition focused
    - Connects concepts holistically
    """

    def __init__(self):
        self.name = "MARVIN"
        self.style = "intuitive"

    def teach(self, concept: Concept, learner: MeatbagLearner) -> List[str]:
        """MARVIN teaching approach"""
        chunks = []

        # MARVIN: Find connections first
        chunks.append(f"🧠 Let's explore {concept.title} from a different angle")

        # Relate to existing knowledge
        if learner.mastery_levels:
            related_concepts = list(learner.mastery_levels.keys())[:3]
            chunks.append(f"This connects to concepts you already know: {', '.join(related_concepts)}")

        # Pattern-focused
        chunks.append("Notice the pattern here - how does this relate to what you've seen before?")

        # Holistic approach
        chunks.append("Let's understand the bigger picture before diving into details.")

        # Adaptive explanation
        if learner.fatigue_level > 0.5:
            chunks.append("Since you might be getting tired, let's keep this concise and visual.")

        return chunks

    def assess_load(self, concept: Concept) -> CognitiveLoad:
        """Assess cognitive load (MARVIN tries to reduce it through context)"""
        # MARVIN uses context to reduce perceived load
        base_load = concept.complexity
        contextual_reduction = 2  # Context helps understanding

        effective_complexity = max(1, base_load - contextual_reduction)

        if effective_complexity <= 3:
            return CognitiveLoad.LOW
        elif effective_complexity <= 6:
            return CognitiveLoad.MEDIUM
        elif effective_complexity <= 8:
            return CognitiveLoad.HIGH
        else:
            return CognitiveLoad.OVERLOAD


class MeatbagLLMLearningSystem:
    """
    Main Learning System - AI Teaching Humans

    Optimizes teaching for biological hardware constraints.
    Uses JARVIS and MARVIN as complementary teaching halves.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "meatbag_learning"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Teachers (two halves of the brain)
        self.jarvis = JARVISTeacher()
        self.marvin = MARVINTeacher()

        # Learner
        self.learner = MeatbagLearner(
            id="primary_learner",
            name="Human",
            preferred_learning_styles=[LearningStyle.MULTIMODAL]
        )

        # Concepts library
        self.concepts: Dict[str, Concept] = {}

        # Active sessions
        self.active_sessions: Dict[str, LearningSession] = {}

        # Spaced repetition schedule
        self.review_schedule: Dict[str, List[datetime]] = {}

        # Setup logging
        self.logger = self._setup_logging()

        # Load existing data
        self._load_data()

    def _load_data(self):
        """Load existing learning data"""
        try:
            # Load learner state
            learner_file = self.data_dir / "learner_state.json"
            if learner_file.exists():
                with open(learner_file, 'r') as f:
                    data = json.load(f)
                    self.learner.mastery_levels = data.get('mastery_levels', {})
                    # Restore other learner state if needed

            # Load concepts
            concepts_file = self.data_dir / "concepts.json"
            if concepts_file.exists():
                with open(concepts_file, 'r') as f:
                    concepts_data = json.load(f)
                    for concept_data in concepts_data:
                        # Convert learning_styles back to enums
                        if 'learning_styles' in concept_data:
                            concept_data['learning_styles'] = [
                                LearningStyle(ls) if isinstance(ls, str) else ls
                                for ls in concept_data['learning_styles']
                            ]
                        concept = Concept(**concept_data)
                        self.concepts[concept.id] = concept
        except Exception as e:
            self.logger.warning(f"Failed to load data: {e}")

    def save_data(self):
        """Save learning data"""
        try:
            # Save learner state
            learner_file = self.data_dir / "learner_state.json"
            with open(learner_file, 'w') as f:
                json.dump({
                    'mastery_levels': self.learner.mastery_levels,
                    'learning_history': [
                        {
                            'concept': h.get('concept'),
                            'timestamp': h.get('timestamp')
                        }
                        for h in list(self.learner.learning_history)
                    ]
                }, f, indent=2)

            # Save concepts
            concepts_file = self.data_dir / "concepts.json"
            with open(concepts_file, 'w') as f:
                concepts_data = []
                for concept in self.concepts.values():
                    concept_dict = asdict(concept)
                    # Convert enums to strings
                    concept_dict['learning_styles'] = [ls.value for ls in concept.learning_styles]
                    concepts_data.append(concept_dict)
                json.dump(concepts_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MeatbagLearning")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - 🧠 %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def register_concept(self, concept: Concept):
        """Register a concept to teach"""
        self.concepts[concept.id] = concept
        self.logger.info(f"📚 Registered concept: {concept.title}")

    def choose_teacher(self, concept: Concept, context: Dict[str, Any] = None) -> TeachingMode:
        """
        Choose which teacher (or both) based on concept and context

        JARVIS: For fundamentals, systematic learning
        MARVIN: For complex connections, intuitive understanding
        INTEGRATED: Best of both worlds
        """
        # Simple rules (can be ML-enhanced)
        if concept.complexity <= 3:
            return TeachingMode.JARVIS  # Simple concepts: JARVIS is clearer
        elif concept.complexity >= 8:
            return TeachingMode.INTEGRATED  # Complex: need both
        elif "prerequisite" in concept.description.lower() or "fundamental" in concept.description.lower():
            return TeachingMode.JARVIS  # Fundamentals: JARVIS
        else:
            return TeachingMode.MARVIN  # Everything else: MARVIN's intuition

    def optimize_for_meatbag(self, concept: Concept, teaching_mode: TeachingMode) -> Dict[str, Any]:
        """
        Optimize teaching for biological hardware

        Constraints:
        - Working memory: 7±2 items (Miller's Law)
        - Attention span: ~20 minutes
        - Multi-modal processing
        - Chunking required
        - Spaced repetition needed
        """
        # Determine cognitive load
        if teaching_mode == TeachingMode.JARVIS:
            load = self.jarvis.assess_load(concept)
        elif teaching_mode == TeachingMode.MARVIN:
            load = self.marvin.assess_load(concept)
        else:
            # Integrated: use lower of the two
            load_jarvis = self.jarvis.assess_load(concept)
            load_marvin = self.marvin.assess_load(concept)
            load = load_jarvis if load_jarvis.value < load_marvin.value else load_marvin

        # Chunk size optimization (Miller's magic number)
        optimal_chunks = min(concept.chunk_size, self.learner.max_working_memory // 2)

        # Session duration (attention span consideration)
        base_duration = concept.estimated_time_minutes
        if self.learner.fatigue_level > 0.5:
            base_duration = int(base_duration * 0.7)  # Shorter when tired

        max_duration = min(base_duration, self.learner.attention_span_minutes)

        # Learning style selection
        learning_style = self.learner.preferred_learning_styles[0]
        if learning_style == LearningStyle.MULTIMODAL:
            # Use all modalities
            styles = concept.learning_styles
        else:
            styles = [learning_style]

        return {
            'cognitive_load': load,
            'optimal_chunks': optimal_chunks,
            'session_duration_minutes': max_duration,
            'learning_styles': styles,
            'chunk_size': optimal_chunks,
            'needs_repetition': concept.complexity > 5
        }

    async def create_learning_session(self, concept_id: str, 
                                     teaching_mode: Optional[TeachingMode] = None) -> LearningSession:
        """Create an optimized learning session"""
        concept = self.concepts.get(concept_id)
        if not concept:
            raise ValueError(f"Concept not found: {concept_id}")

        # Choose teacher if not specified
        if teaching_mode is None:
            teaching_mode = self.choose_teacher(concept)

        # Optimize for meatbag hardware
        optimization = self.optimize_for_meatbag(concept, teaching_mode)

        # Check if learner can absorb
        if not self.learner.can_absorb(optimization['cognitive_load']):
            self.logger.warning(f"⚠️ Cognitive overload risk for {concept.title}")
            # Reduce load
            optimization['optimal_chunks'] = max(1, optimization['optimal_chunks'] - 2)
            optimization['session_duration_minutes'] = max(10, optimization['session_duration_minutes'] - 5)

        # Create session
        session = LearningSession(
            id=f"session_{concept_id}_{int(time.time())}",
            concept=concept,
            teaching_mode=teaching_mode,
            cognitive_load=optimization['cognitive_load'],
            learning_style=optimization['learning_styles'][0],
            start_time=datetime.now(),
            duration_minutes=optimization['session_duration_minutes']
        )

        self.active_sessions[session.id] = session

        self.logger.info(f"📖 Created learning session: {concept.title} ({teaching_mode.value})")
        self.logger.info(f"   Cognitive Load: {optimization['cognitive_load'].value}")
        self.logger.info(f"   Duration: {optimization['session_duration_minutes']} minutes")
        self.logger.info(f"   Chunks: {optimization['optimal_chunks']}")

        return session

    async def deliver_teaching(self, session: LearningSession) -> List[str]:
        """Deliver teaching content based on teacher"""
        chunks = []

        if session.teaching_mode == TeachingMode.JARVIS:
            chunks.extend(self.jarvis.teach(session.concept, self.learner))
        elif session.teaching_mode == TeachingMode.MARVIN:
            chunks.extend(self.marvin.teach(session.concept, self.learner))
        elif session.teaching_mode == TeachingMode.INTEGRATED:
            # Both teachers together
            chunks.append("🧠 JARVIS and MARVIN working together:")
            chunks.extend(self.jarvis.teach(session.concept, self.learner))
            chunks.append("\n---\n")
            chunks.extend(self.marvin.teach(session.concept, self.learner))

        # Chunk optimization
        session.chunks_delivered = len(chunks)

        return chunks

    def schedule_spaced_repetition(self, concept_id: str, mastery_level: float):
        """
        Schedule spaced repetition (Ebbinghaus forgetting curve)

        Optimal intervals:
        - 1 hour (if just learned)
        - 1 day
        - 3 days
        - 1 week
        - 2 weeks
        - 1 month
        """
        if concept_id not in self.review_schedule:
            self.review_schedule[concept_id] = []

        now = datetime.now()

        if mastery_level < 0.3:  # Low mastery
            intervals = [1, 6, 24]  # hours
        elif mastery_level < 0.7:  # Medium mastery
            intervals = [6, 24, 72]  # hours
        else:  # High mastery
            intervals = [24, 72, 168]  # hours (1 day, 3 days, 1 week)

        review_times = [now + timedelta(hours=h) for h in intervals]
        self.review_schedule[concept_id].extend(review_times)

        self.logger.info(f"📅 Scheduled reviews for {concept_id}: {len(review_times)} sessions")

    def update_learner_state(self, session: LearningSession, understood: bool):
        """Update learner's state after session"""
        if understood:
            session.chunks_understood += 1
            mastery_delta = 0.1 * (session.chunks_understood / session.chunks_delivered)
            current_mastery = self.learner.mastery_levels.get(session.concept.id, 0.0)
            self.learner.mastery_levels[session.concept.id] = min(1.0, current_mastery + mastery_delta)

        # Update working memory
        load_values = {
            CognitiveLoad.LOW: 2,
            CognitiveLoad.MEDIUM: 5,
            CognitiveLoad.HIGH: 7
        }
        self.learner.current_working_memory = min(
            self.learner.max_working_memory,
            self.learner.current_working_memory + load_values.get(session.cognitive_load, 3)
        )

        # Schedule repetition if needed
        mastery = self.learner.mastery_levels.get(session.concept.id, 0.0)
        self.schedule_spaced_repetition(session.concept.id, mastery)

        # Record in history
        self.learner.learning_history.append({
            'concept': session.concept.id,
            'teaching_mode': session.teaching_mode.value,
            'understood': understood,
            'timestamp': datetime.now().isoformat()
        })

    def get_teaching_recommendation(self) -> Dict[str, Any]:
        """Get recommendation for next teaching session"""
        # Check for reviews due
        now = datetime.now()
        for concept_id, review_times in self.review_schedule.items():
            due_reviews = [rt for rt in review_times if rt <= now]
            if due_reviews:
                concept = self.concepts.get(concept_id)
                if concept:
                    return {
                        'type': 'review',
                        'concept': concept,
                        'reason': 'Spaced repetition due'
                    }

        # Suggest new concept based on mastery
        learned_concepts = set(self.learner.mastery_levels.keys())
        available_concepts = [c for c in self.concepts.values() 
                            if c.id not in learned_concepts or 
                            self.learner.mastery_levels.get(c.id, 0.0) < 0.7]

        if available_concepts:
            # Choose simplest unlearned or lowest mastery
            concept = min(available_concepts, 
                         key=lambda c: self.learner.mastery_levels.get(c.id, 0.0))

            teaching_mode = self.choose_teacher(concept)

            return {
                'type': 'new',
                'concept': concept,
                'teaching_mode': teaching_mode,
                'reason': 'Next concept to learn'
            }

        return {'type': 'none', 'reason': 'All concepts mastered or no concepts available'}


async def main():
    """Example usage"""
    system = MeatbagLLMLearningSystem()

    # Register a concept
    concept = Concept(
        id="python_async",
        title="Python Async/Await",
        description="Understanding asynchronous programming in Python",
        complexity=7,
        chunk_size=3,
        estimated_time_minutes=30
    )
    system.register_concept(concept)

    # Create learning session
    session = await system.create_learning_session("python_async")

    # Deliver teaching
    chunks = await system.deliver_teaching(session)

    print("\n🧠 MEATBAG LLM LEARNING SYSTEM")
    print("=" * 80)
    print(f"Teaching: {session.concept.title}")
    print(f"Mode: {session.teaching_mode.value.upper()}")
    print(f"Cognitive Load: {session.cognitive_load.value}")
    print(f"Duration: {session.duration_minutes} minutes")
    print("\nTeaching Content:")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n{i}. {chunk}")

    # Get recommendation
    rec = system.get_teaching_recommendation()
    print(f"\n📚 Next Recommendation: {rec['reason']}")


if __name__ == "__main__":



    asyncio.run(main())