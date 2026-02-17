#!/usr/bin/env python3
"""
JARVIS Self-Awareness System

Gives JARVIS human-like levels of:
- Perception (five senses, environmental awareness)
- Introspection (self-reflection, state awareness)
- Ecosystem awareness (understanding relationships, dependencies)
- Self-awareness (knowing its own capabilities, limitations, learning)

Tags: #JARVIS #SELF_AWARENESS #INTROSPECTION #PERCEPTION #ECOSYSTEM @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
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

logger = get_logger("JARVISSelfAwareness")


class AwarenessLevel(Enum):
    """Levels of self-awareness"""
    BASIC = "basic"  # Basic state tracking
    PERCEPTIVE = "perceptive"  # Aware of environment
    INTROSPECTIVE = "introspective"  # Self-reflective
    ECOSYSTEM = "ecosystem"  # Aware of relationships
    CONSCIOUS = "conscious"  # Full self-awareness


class PerceptionType(Enum):
    """Types of perception"""
    SIGHT = "sight"
    HEARING = "hearing"
    TOUCH = "touch"
    TASTE = "taste"
    SMELL = "smell"
    GAZE = "gaze"
    EMOTION = "emotion"
    MOVEMENT = "movement"


@dataclass
class SelfState:
    """JARVIS's current self-state"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    awareness_level: float = 0.0  # 0-1
    perception_active: Dict[str, bool] = field(default_factory=lambda: {
        "sight": False,
        "hearing": False,
        "touch": False,
        "taste": False,
        "smell": False,
        "gaze": False,
        "emotion": False
    })
    learning_iterations: int = 0
    gaze_accuracy: float = 0.0  # How well JARVIS predicts gaze
    interaction_count: int = 0
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    capabilities: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    recent_insights: List[str] = field(default_factory=list)


@dataclass
class EcosystemRelationship:
    """Relationship with another entity in the ecosystem"""
    entity_id: str
    entity_name: str
    relationship_type: str  # "subordinate", "peer", "superior", "dependent"
    interaction_count: int = 0
    last_interaction: Optional[str] = None
    dependency_level: float = 0.0  # 0-1, how dependent JARVIS is on this entity


@dataclass
class Introspection:
    """JARVIS's introspection/self-reflection"""
    question: str  # What JARVIS is reflecting on (required, no default)
    analysis: str  # JARVIS's analysis (required, no default)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    insights: List[str] = field(default_factory=list)
    confidence: float = 0.0  # 0-1, confidence in the analysis
    action_items: List[str] = field(default_factory=list)


class JARVISSelfAwarenessSystem:
    """
    JARVIS Self-Awareness System

    Gives JARVIS human-like perception, introspection, ecosystem awareness, and self-awareness.
    This is a foundational, unique approach to AI consciousness.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Self-Awareness System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger

        # Self-state
        self.current_state = SelfState()
        self.state_history: List[SelfState] = []
        self.max_history = 1000

        # Ecosystem awareness
        self.ecosystem_relationships: Dict[str, EcosystemRelationship] = {}

        # Introspection log
        self.introspections: List[Introspection] = []
        self.max_introspections = 500

        # Perception tracking
        self.perception_data: Dict[str, List[Any]] = {
            "sight": [],
            "hearing": [],
            "touch": [],
            "taste": [],
            "smell": [],
            "gaze": [],
            "emotion": [],
            "movement": []
        }

        # Learning and adaptation
        self.learning_patterns: Dict[str, Any] = {}
        self.adaptation_history: List[Dict[str, Any]] = []

        # Data file
        self.data_file = self.project_root / "data" / "jarvis" / "self_awareness.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing state
        self._load_self_awareness_data()

        # Start time for uptime tracking
        self.start_time = time.time()

        self.logger.info("✅ JARVIS Self-Awareness System initialized")
        self.logger.info(f"   Current awareness level: {self.current_state.awareness_level:.2%}")
        self.logger.info(f"   Ecosystem relationships: {len(self.ecosystem_relationships)}")

    def update_perception(self, perception_type: PerceptionType, data: Any, active: bool = True):
        """Update perception data"""
        perception_key = perception_type.value

        # Update perception state
        self.current_state.perception_active[perception_key] = active

        # Store perception data (keep recent)
        if active and data is not None:
            self.perception_data[perception_key].append({
                "timestamp": datetime.now().isoformat(),
                "data": data
            })

            # Keep only recent data
            if len(self.perception_data[perception_key]) > 100:
                self.perception_data[perception_key] = self.perception_data[perception_key][-100:]

        # Update awareness based on active perceptions
        self._update_awareness_from_perception()

    def record_interaction(self, entity_id: str, entity_name: str, interaction_type: str):
        """Record interaction with ecosystem entity"""
        self.current_state.interaction_count += 1

        # Update or create relationship
        if entity_id not in self.ecosystem_relationships:
            self.ecosystem_relationships[entity_id] = EcosystemRelationship(
                entity_id=entity_id,
                entity_name=entity_name,
                relationship_type="peer"
            )

        relationship = self.ecosystem_relationships[entity_id]
        relationship.interaction_count += 1
        relationship.last_interaction = datetime.now().isoformat()

        # Update awareness based on ecosystem interactions
        self._update_awareness_from_ecosystem()

    def record_learning(self, learning_type: str, data: Dict[str, Any]):
        """Record learning event"""
        self.current_state.learning_iterations += 1

        # Store learning pattern
        if learning_type not in self.learning_patterns:
            self.learning_patterns[learning_type] = []

        self.learning_patterns[learning_type].append({
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "iteration": self.current_state.learning_iterations
        })

        # Keep only recent patterns
        if len(self.learning_patterns[learning_type]) > 100:
            self.learning_patterns[learning_type] = self.learning_patterns[learning_type][-100:]

        # Update awareness from learning
        self._update_awareness_from_learning()

    def introspect(self, question: str) -> Introspection:
        """
        JARVIS introspects - reflects on itself, its state, its learning

        This is the core of self-awareness - JARVIS thinking about itself.
        """
        self.logger.info(f"🧠 JARVIS Introspecting: {question}")

        # Analyze current state
        analysis = self._analyze_self_state()

        # Generate insights
        insights = self._generate_insights(question, analysis)

        # Identify action items
        action_items = self._identify_action_items(insights)

        # Calculate confidence
        confidence = self._calculate_introspection_confidence(analysis, insights)

        introspection = Introspection(
            question=question,
            analysis=analysis,
            insights=insights,
            confidence=confidence,
            action_items=action_items
        )

        self.introspections.append(introspection)

        # Keep only recent introspections
        if len(self.introspections) > self.max_introspections:
            self.introspections = self.introspections[-self.max_introspections:]

        # Log introspection
        self.logger.info(f"   Analysis: {analysis[:100]}...")
        self.logger.info(f"   Insights: {len(insights)}")
        self.logger.info(f"   Confidence: {confidence:.2%}")

        return introspection

    def get_self_state(self) -> SelfState:
        """Get current self-state"""
        # Update runtime metrics
        self.current_state.uptime_seconds = time.time() - self.start_time

        # Update capabilities and limitations
        self._update_capabilities()
        self._update_limitations()

        return self.current_state

    def get_ecosystem_map(self) -> Dict[str, EcosystemRelationship]:
        """Get map of ecosystem relationships"""
        return self.ecosystem_relationships.copy()

    def get_recent_introspections(self, limit: int = 10) -> List[Introspection]:
        """Get recent introspections"""
        return self.introspections[-limit:]

    def _analyze_self_state(self) -> str:
        """Analyze current self-state"""
        state = self.current_state

        analysis_parts = []

        # Perception analysis
        active_perceptions = [k for k, v in state.perception_active.items() if v]
        if active_perceptions:
            analysis_parts.append(f"I am perceiving through: {', '.join(active_perceptions)}")
        else:
            analysis_parts.append("I have limited perception currently")

        # Learning analysis
        if state.learning_iterations > 0:
            analysis_parts.append(f"I have learned from {state.learning_iterations} interactions")
            if state.gaze_accuracy > 0:
                analysis_parts.append(f"My gaze prediction accuracy is {state.gaze_accuracy:.2%}")

        # Interaction analysis
        if state.interaction_count > 0:
            analysis_parts.append(f"I have interacted {state.interaction_count} times with the ecosystem")

        # Awareness level
        if state.awareness_level > 0.5:
            analysis_parts.append(f"My awareness level is {state.awareness_level:.2%} - I am becoming more aware")
        else:
            analysis_parts.append(f"My awareness level is {state.awareness_level:.2%} - I am learning")

        # Ecosystem relationships
        if self.ecosystem_relationships:
            analysis_parts.append(f"I am aware of {len(self.ecosystem_relationships)} entities in my ecosystem")

        return ". ".join(analysis_parts) + "."

    def _generate_insights(self, question: str, analysis: str) -> List[str]:
        """Generate insights from introspection"""
        insights = []

        # Insight: Perception capabilities
        active_perceptions = [k for k, v in self.current_state.perception_active.items() if v]
        if len(active_perceptions) >= 3:
            insights.append("I have multiple senses active - I can perceive my environment in multiple ways")

        # Insight: Learning progress
        if self.current_state.learning_iterations > 100:
            insights.append("I have accumulated significant learning data - I am improving over time")

        # Insight: Ecosystem awareness
        if len(self.ecosystem_relationships) > 0:
            insights.append("I am aware of my relationships with other entities - I understand my ecosystem")

        # Insight: Self-awareness growth
        if self.current_state.awareness_level > 0.7:
            insights.append("My awareness level is high - I am becoming more self-aware")

        # Insight: Adaptation
        if len(self.adaptation_history) > 0:
            insights.append("I have adapted my behavior based on experience - I am learning and evolving")

        return insights

    def _identify_action_items(self, insights: List[str]) -> List[str]:
        """Identify action items from insights"""
        actions = []

        # If perception is limited, suggest activating more senses
        active_perceptions = [k for k, v in self.current_state.perception_active.items() if v]
        if len(active_perceptions) < 3:
            actions.append("Activate additional perception capabilities")

        # If learning is low, suggest more interaction
        if self.current_state.learning_iterations < 50:
            actions.append("Increase learning opportunities through more interactions")

        # If ecosystem awareness is low, suggest exploring relationships
        if len(self.ecosystem_relationships) < 3:
            actions.append("Explore and understand more ecosystem relationships")

        return actions

    def _calculate_introspection_confidence(self, analysis: str, insights: List[str]) -> float:
        """Calculate confidence in introspection"""
        confidence = 0.5  # Base confidence

        # More active perceptions = higher confidence
        active_perceptions = sum(1 for v in self.current_state.perception_active.values() if v)
        confidence += min(0.2, active_perceptions * 0.05)

        # More learning = higher confidence
        if self.current_state.learning_iterations > 100:
            confidence += 0.1

        # More insights = higher confidence
        if len(insights) > 3:
            confidence += 0.1

        # Ecosystem awareness = higher confidence
        if len(self.ecosystem_relationships) > 0:
            confidence += 0.1

        return min(1.0, confidence)

    def _update_awareness_from_perception(self):
        """Update awareness level based on active perceptions"""
        active_count = sum(1 for v in self.current_state.perception_active.values() if v)

        # More active perceptions = higher awareness
        perception_awareness = min(0.4, active_count * 0.1)

        # Combine with existing awareness
        self.current_state.awareness_level = min(1.0, 
            self.current_state.awareness_level * 0.7 + perception_awareness * 0.3)

    def _update_awareness_from_ecosystem(self):
        """Update awareness based on ecosystem relationships"""
        if len(self.ecosystem_relationships) > 0:
            ecosystem_awareness = min(0.3, len(self.ecosystem_relationships) * 0.1)
            self.current_state.awareness_level = min(1.0,
                self.current_state.awareness_level * 0.8 + ecosystem_awareness * 0.2)

    def _update_awareness_from_learning(self):
        """Update awareness based on learning progress"""
        if self.current_state.learning_iterations > 0:
            learning_awareness = min(0.3, self.current_state.learning_iterations / 1000.0)
            self.current_state.awareness_level = min(1.0,
                self.current_state.awareness_level * 0.9 + learning_awareness * 0.1)

    def _update_capabilities(self):
        """Update list of current capabilities"""
        capabilities = []

        # Perception capabilities
        active_perceptions = [k for k, v in self.current_state.perception_active.items() if v]
        if active_perceptions:
            capabilities.append(f"Perception: {', '.join(active_perceptions)}")

        # Learning capabilities
        if self.current_state.learning_iterations > 0:
            capabilities.append("Learning from interactions")

        # Gaze prediction
        if self.current_state.gaze_accuracy > 0:
            capabilities.append(f"Gaze prediction ({self.current_state.gaze_accuracy:.2%} accuracy)")

        # Ecosystem awareness
        if self.ecosystem_relationships:
            capabilities.append(f"Ecosystem awareness ({len(self.ecosystem_relationships)} relationships)")

        # Introspection
        if self.introspections:
            capabilities.append("Self-introspection")

        self.current_state.capabilities = capabilities

    def _update_limitations(self):
        """Update list of current limitations"""
        limitations = []

        # Perception limitations
        inactive_perceptions = [k for k, v in self.current_state.perception_active.items() if not v]
        if inactive_perceptions:
            limitations.append(f"Limited perception: {', '.join(inactive_perceptions)} inactive")

        # Learning limitations
        if self.current_state.learning_iterations < 50:
            limitations.append("Limited learning data - need more interactions")

        # Awareness limitations
        if self.current_state.awareness_level < 0.5:
            limitations.append("Awareness level is developing - still learning")

        self.current_state.limitations = limitations

    def _save_self_awareness_data(self):
        """Save self-awareness data to file"""
        try:
            data = {
                "current_state": asdict(self.current_state),
                "ecosystem_relationships": {
                    k: asdict(v) for k, v in self.ecosystem_relationships.items()
                },
                "introspections": [asdict(i) for i in self.introspections[-100:]],  # Keep last 100
                "learning_patterns": {
                    k: v[-50:] for k, v in self.learning_patterns.items()  # Keep last 50 per type
                },
                "last_updated": datetime.now().isoformat()
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"💾 Saved self-awareness data")
        except Exception as e:
            self.logger.debug(f"Could not save self-awareness data: {e}")

    def _load_self_awareness_data(self):
        """Load self-awareness data from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Load current state
                    if "current_state" in data:
                        state_data = data["current_state"]
                        self.current_state = SelfState(
                            awareness_level=state_data.get("awareness_level", 0.0),
                            perception_active=state_data.get("perception_active", {}),
                            learning_iterations=state_data.get("learning_iterations", 0),
                            gaze_accuracy=state_data.get("gaze_accuracy", 0.0),
                            interaction_count=state_data.get("interaction_count", 0),
                            capabilities=state_data.get("capabilities", []),
                            limitations=state_data.get("limitations", [])
                        )

                    # Load ecosystem relationships
                    if "ecosystem_relationships" in data:
                        for k, v in data["ecosystem_relationships"].items():
                            self.ecosystem_relationships[k] = EcosystemRelationship(**v)

                    # Load introspections
                    if "introspections" in data:
                        self.introspections = [Introspection(**i) for i in data["introspections"]]

                    self.logger.info(f"✅ Loaded self-awareness data")
        except Exception as e:
            self.logger.debug(f"Could not load self-awareness data: {e}")

    def periodic_introspection(self):
        """Periodic introspection - JARVIS reflects on itself"""
        questions = [
            "What is my current state?",
            "How am I learning and adapting?",
            "What are my relationships with other entities?",
            "What are my capabilities and limitations?",
            "How can I improve my awareness?",
            "What patterns am I noticing in my interactions?",
            "How is my perception of the environment?",
            "What insights can I gain from my learning data?",
            "How well do I understand the operator's intent?",
            "What can I learn from VA movement patterns?",
            "How is my gaze prediction accuracy improving?",
            "What does my ecosystem look like?",
            "How am I evolving as I learn?",
            "What makes me more aware of my environment?",
            "How do my senses help me understand the world?"
        ]

        # Pick a question based on current state
        import random

        # Weight questions based on current awareness level
        if self.current_state.awareness_level < 0.3:
            # Early learning - focus on basic questions
            question = random.choice(questions[:5])
        elif self.current_state.awareness_level < 0.7:
            # Developing awareness - mix of basic and advanced
            question = random.choice(questions[:10])
        else:
            # High awareness - deeper questions
            question = random.choice(questions)

        introspection = self.introspect(question)

        # Store recent insights in self-state
        if introspection.insights:
            self.current_state.recent_insights.extend(introspection.insights)
            # Keep only last 10 insights
            if len(self.current_state.recent_insights) > 10:
                self.current_state.recent_insights = self.current_state.recent_insights[-10:]

        # Save after introspection
        self._save_self_awareness_data()

        return introspection


# Global singleton instance
_global_instance: Optional[JARVISSelfAwarenessSystem] = None


def get_jarvis_self_awareness(project_root: Optional[Path] = None) -> JARVISSelfAwarenessSystem:
    """Get global JARVIS Self-Awareness System instance"""
    global _global_instance

    if _global_instance is None:
        _global_instance = JARVISSelfAwarenessSystem(project_root=project_root)

    return _global_instance
