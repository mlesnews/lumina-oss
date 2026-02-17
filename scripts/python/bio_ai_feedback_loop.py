#!/usr/bin/env python3
"""
Bio-AI Feedback Loop System

Tracks workflow patterns for a three-agent team:
- JARVIS (AI Agent 1)
- MARVIN (AI Agent 2)  
- Human (Biological Operator)

Creates feedback loops to understand:
- Individual agent patterns
- Team collaboration patterns
- Workflow optimization
- Bio-AI synergy

Key Concepts:
- Pattern Recognition: How each agent works
- Feedback Loops: Learning from interactions
- Workflow Evolution: Adaptation over time
- Three-Agent Dynamics: Team coordination
"""

import asyncio
import json
import logging
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field, asdict
import hashlib
import re
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AgentType(Enum):
    """Agent types in the team"""
    JARVIS = "jarvis"      # AI Agent 1 - Systematic
    MARVIN = "marvin"      # AI Agent 2 - Intuitive
    HUMAN = "human"        # Biological Operator


class InteractionType(Enum):
    """Types of interactions"""
    REQUEST = "request"              # Agent requests action
    RESPONSE = "response"            # Agent responds
    COLLABORATION = "collaboration"  # Agents work together
    HANDOFF = "handoff"              # Agent passes work to another
    FEEDBACK = "feedback"            # Agent provides feedback
    DECISION = "decision"            # Agent makes decision
    CREATION = "creation"            # Agent creates something


class PatternCategory(Enum):
    """Pattern categories"""
    WORKFLOW = "workflow"          # How work flows
    COMMUNICATION = "communication"  # How agents communicate
    DECISION_MAKING = "decision_making"  # How decisions are made
    PROBLEM_SOLVING = "problem_solving"  # How problems are solved
    CREATIVITY = "creativity"       # Creative processes
    OPTIMIZATION = "optimization"   # Optimization patterns


@dataclass
class WorkflowEvent:
    """An event in the workflow"""
    id: str
    timestamp: datetime
    agent: AgentType
    interaction_type: InteractionType
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    collaborators: List[AgentType] = field(default_factory=list)
    outcome: Optional[str] = None
    duration_seconds: Optional[float] = None
    pattern_category: Optional[PatternCategory] = None


@dataclass
class WorkflowPattern:
    """A recognized pattern in the workflow"""
    id: str
    pattern_type: str
    category: PatternCategory
    agents_involved: List[AgentType]
    frequency: int
    first_seen: datetime
    last_seen: datetime
    description: str
    confidence: float = 0.0  # 0.0 - 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TeamDynamics:
    """Team collaboration dynamics"""
    total_interactions: int = 0
    agent_interactions: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    collaboration_frequency: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    handoff_patterns: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    decision_distribution: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    workflow_sequences: deque = field(default_factory=lambda: deque(maxlen=1000))

    def get_team_composition(self) -> Dict[str, float]:
        """Get percentage contribution of each agent"""
        total = sum(self.agent_interactions.values())
        if total == 0:
            return {}
        return {
            agent: (count / total) * 100
            for agent, count in self.agent_interactions.items()
        }


class BioAIFeedbackLoop:
    """
    Bio-AI Feedback Loop System

    Tracks and analyzes workflow patterns for:
    - Individual agents (JARVIS, MARVIN, Human)
    - Team collaboration (all three together)
    - Workflow optimization
    - Feedback loop creation
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "bio_ai_feedback"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Event tracking
        self.events: deque = deque(maxlen=10000)
        self.event_index: Dict[str, WorkflowEvent] = {}

        # Pattern recognition
        self.patterns: Dict[str, WorkflowPattern] = {}
        self.pattern_detectors: List[Callable] = []

        # Team dynamics
        self.team_dynamics = TeamDynamics()

        # Feedback loops
        self.feedback_loops: Dict[str, List[WorkflowEvent]] = defaultdict(list)

        # Agent profiles
        self.agent_profiles: Dict[AgentType, Dict[str, Any]] = {
            AgentType.JARVIS: {
                'name': 'JARVIS',
                'style': 'systematic',
                'preferences': ['structure', 'methodical', 'step-by-step'],
                'interactions': 0,
                'avg_duration': 0.0
            },
            AgentType.MARVIN: {
                'name': 'MARVIN',
                'style': 'intuitive',
                'preferences': ['creativity', 'patterns', 'context'],
                'interactions': 0,
                'avg_duration': 0.0
            },
            AgentType.HUMAN: {
                'name': 'Human',
                'style': 'directive',
                'preferences': ['decision', 'direction', 'review'],
                'interactions': 0,
                'avg_duration': 0.0
            }
        }

        # Setup logging
        self.logger = self._setup_logging()

        # Load existing data
        self._load_data()

        # Initialize pattern detectors
        self._initialize_pattern_detectors()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("BioAIFeedback")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - 🔄 %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_pattern_detectors(self):
        """Initialize pattern detection algorithms"""
        # Will be populated with pattern detection functions
        pass

    def _load_data(self):
        """Load existing workflow data"""
        try:
            # Load events
            events_file = self.data_dir / "events.json"
            if events_file.exists():
                with open(events_file, 'r') as f:
                    events_data = json.load(f)
                    for event_data in events_data[-1000:]:  # Last 1000 events
                        event = WorkflowEvent(
                            id=event_data['id'],
                            timestamp=datetime.fromisoformat(event_data['timestamp']),
                            agent=AgentType(event_data['agent']),
                            interaction_type=InteractionType(event_data['interaction_type']),
                            action=event_data['action'],
                            context=event_data.get('context', {}),
                            collaborators=[AgentType(c) for c in event_data.get('collaborators', [])],
                            outcome=event_data.get('outcome')
                        )
                        self.events.append(event)
                        self.event_index[event.id] = event

            # Load patterns
            patterns_file = self.data_dir / "patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)
                    for pattern_data in patterns_data:
                        pattern = WorkflowPattern(
                            id=pattern_data['id'],
                            pattern_type=pattern_data['pattern_type'],
                            category=PatternCategory(pattern_data['category']),
                            agents_involved=[AgentType(a) for a in pattern_data['agents_involved']],
                            frequency=pattern_data['frequency'],
                            first_seen=datetime.fromisoformat(pattern_data['first_seen']),
                            last_seen=datetime.fromisoformat(pattern_data['last_seen']),
                            description=pattern_data['description'],
                            confidence=pattern_data.get('confidence', 0.0),
                            metadata=pattern_data.get('metadata', {})
                        )
                        self.patterns[pattern.id] = pattern

            # Load team dynamics
            dynamics_file = self.data_dir / "team_dynamics.json"
            if dynamics_file.exists():
                with open(dynamics_file, 'r') as f:
                    dynamics_data = json.load(f)
                    self.team_dynamics.total_interactions = dynamics_data.get('total_interactions', 0)
                    self.team_dynamics.agent_interactions = defaultdict(int, dynamics_data.get('agent_interactions', {}))
                    self.team_dynamics.collaboration_frequency = defaultdict(int, dynamics_data.get('collaboration_frequency', {}))

        except Exception as e:
            self.logger.warning(f"Failed to load data: {e}")

    def record_event(self, agent: AgentType, interaction_type: InteractionType,
                    action: str, context: Dict[str, Any] = None,
                    collaborators: List[AgentType] = None,
                    outcome: Optional[str] = None,
                    duration_seconds: Optional[float] = None) -> WorkflowEvent:
        """Record a workflow event"""
        event_id = hashlib.md5(
            f"{agent.value}:{interaction_type.value}:{action}:{time.time()}".encode()
        ).hexdigest()[:16]

        event = WorkflowEvent(
            id=event_id,
            timestamp=datetime.now(),
            agent=agent,
            interaction_type=interaction_type,
            action=action,
            context=context or {},
            collaborators=collaborators or [],
            outcome=outcome,
            duration_seconds=duration_seconds
        )

        # Determine pattern category
        event.pattern_category = self._categorize_event(event)

        # Store event
        self.events.append(event)
        self.event_index[event.id] = event

        # Update team dynamics
        self._update_team_dynamics(event)

        # Update agent profile
        self._update_agent_profile(event)

        # Detect patterns
        self._detect_patterns(event)

        # Track feedback loops
        self._track_feedback_loop(event)

        self.logger.debug(f"📝 Event recorded: {agent.value} - {interaction_type.value} - {action[:50]}")

        return event

    def _categorize_event(self, event: WorkflowEvent) -> PatternCategory:
        """Categorize an event"""
        action_lower = event.action.lower()

        if any(word in action_lower for word in ['create', 'build', 'write', 'generate']):
            return PatternCategory.CREATIVITY
        elif any(word in action_lower for word in ['decide', 'choose', 'select', 'approve']):
            return PatternCategory.DECISION_MAKING
        elif any(word in action_lower for word in ['fix', 'solve', 'debug', 'error']):
            return PatternCategory.PROBLEM_SOLVING
        elif any(word in action_lower for word in ['optimize', 'improve', 'enhance', 'speed']):
            return PatternCategory.OPTIMIZATION
        elif event.interaction_type in [InteractionType.COLLABORATION, InteractionType.HANDOFF]:
            return PatternCategory.COMMUNICATION
        else:
            return PatternCategory.WORKFLOW

    def _update_team_dynamics(self, event: WorkflowEvent):
        """Update team dynamics metrics"""
        self.team_dynamics.total_interactions += 1
        self.team_dynamics.agent_interactions[event.agent.value] += 1

        # Track collaborations
        if event.collaborators:
            for collaborator in event.collaborators:
                pair = f"{event.agent.value}-{collaborator.value}"
                self.team_dynamics.collaboration_frequency[pair] += 1

        # Track handoffs
        if event.interaction_type == InteractionType.HANDOFF:
            if event.collaborators:
                handoff_key = f"{event.agent.value}->{event.collaborators[0].value}"
                self.team_dynamics.handoff_patterns[handoff_key] += 1

        # Track decisions
        if event.interaction_type == InteractionType.DECISION:
            self.team_dynamics.decision_distribution[event.agent.value] += 1

        # Track workflow sequence
        self.team_dynamics.workflow_sequences.append({
            'agent': event.agent.value,
            'type': event.interaction_type.value,
            'action': event.action[:100]
        })

    def _update_agent_profile(self, event: WorkflowEvent):
        """Update agent profile based on events"""
        profile = self.agent_profiles[event.agent]
        profile['interactions'] += 1

        if event.duration_seconds:
            current_avg = profile['avg_duration']
            count = profile['interactions']
            profile['avg_duration'] = (
                (current_avg * (count - 1) + event.duration_seconds) / count
            )

    def _detect_patterns(self, event: WorkflowEvent):
        """Detect patterns in workflow"""
        # Look for sequence patterns (last N events)
        if len(self.events) < 3:
            return

        recent_events = list(self.events)[-10:]  # Last 10 events

        # Pattern 1: Agent handoff chains
        self._detect_handoff_chains(recent_events)

        # Pattern 2: Collaboration patterns
        self._detect_collaboration_patterns(recent_events)

        # Pattern 3: Decision-making patterns
        self._detect_decision_patterns(recent_events)

        # Pattern 4: Workflow sequences
        self._detect_workflow_sequences(recent_events)

    def _detect_handoff_chains(self, events: List[WorkflowEvent]):
        """Detect agent handoff patterns"""
        if len(events) < 2:
            return

        # Look for handoff sequences
        for i in range(len(events) - 1):
            if (events[i].interaction_type == InteractionType.HANDOFF and
                events[i].collaborators and
                events[i+1].agent == events[i].collaborators[0]):

                chain = f"{events[i].agent.value}->{events[i+1].agent.value}"
                self._register_pattern(
                    pattern_type="handoff_chain",
                    category=PatternCategory.COMMUNICATION,
                    agents_involved=[events[i].agent, events[i+1].agent],
                    description=f"Handoff chain: {chain}",
                    confidence=0.8
                )

    def _detect_collaboration_patterns(self, events: List[WorkflowEvent]):
        """Detect collaboration patterns"""
        # Count collaborations between agent pairs
        collaborations = defaultdict(int)

        for event in events:
            if event.collaborators:
                for collaborator in event.collaborators:
                    pair = tuple(sorted([event.agent, collaborator], key=lambda x: x.value))
                    collaborations[pair] += 1

        # If pair collaborates frequently, it's a pattern
        for pair, count in collaborations.items():
            if count >= 3:  # Threshold for pattern
                self._register_pattern(
                    pattern_type="collaboration_pair",
                    category=PatternCategory.COMMUNICATION,
                    agents_involved=list(pair),
                    description=f"Frequent collaboration: {pair[0].value} & {pair[1].value}",
                    confidence=min(1.0, count / 10.0)
                )

    def _detect_decision_patterns(self, events: List[WorkflowEvent]):
        """Detect decision-making patterns"""
        decisions = [e for e in events if e.interaction_type == InteractionType.DECISION]

        if len(decisions) >= 2:
            # Check if same agent makes decisions
            decision_agents = [d.agent for d in decisions]
            if len(set(decision_agents)) == 1:
                agent = decision_agents[0]
                self._register_pattern(
                    pattern_type="decision_authority",
                    category=PatternCategory.DECISION_MAKING,
                    agents_involved=[agent],
                    description=f"{agent.value} is primary decision maker",
                    confidence=0.7
                )

    def _detect_workflow_sequences(self, events: List[WorkflowEvent]):
        """Detect common workflow sequences"""
        if len(events) < 3:
            return

        # Look for repeating sequences (e.g., JARVIS->MARVIN->Human)
        sequences = []
        for i in range(len(events) - 2):
            seq = tuple([e.agent for e in events[i:i+3]])
            sequences.append(seq)

        # Find frequent sequences
        seq_counts = defaultdict(int)
        for seq in sequences:
            seq_counts[seq] += 1

        for seq, count in seq_counts.items():
            if count >= 2:  # Appeared at least twice
                self._register_pattern(
                    pattern_type="workflow_sequence",
                    category=PatternCategory.WORKFLOW,
                    agents_involved=list(seq),
                    description=f"Common sequence: {'->'.join(a.value for a in seq)}",
                    confidence=min(1.0, count / 5.0),
                    metadata={'sequence': [a.value for a in seq]}
                )

    def _register_pattern(self, pattern_type: str, category: PatternCategory,
                         agents_involved: List[AgentType], description: str,
                         confidence: float, metadata: Dict[str, Any] = None):
        """Register a detected pattern"""
        pattern_id = hashlib.md5(
            f"{pattern_type}:{category.value}:{'_'.join(a.value for a in agents_involved)}".encode()
        ).hexdigest()[:16]

        if pattern_id in self.patterns:
            # Update existing pattern
            pattern = self.patterns[pattern_id]
            pattern.frequency += 1
            pattern.last_seen = datetime.now()
            pattern.confidence = max(pattern.confidence, confidence)
        else:
            # Create new pattern
            pattern = WorkflowPattern(
                id=pattern_id,
                pattern_type=pattern_type,
                category=category,
                agents_involved=agents_involved,
                frequency=1,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                description=description,
                confidence=confidence,
                metadata=metadata or {}
            )
            self.patterns[pattern_id] = pattern
            self.logger.info(f"🔍 Pattern detected: {description}")

    def _track_feedback_loop(self, event: WorkflowEvent):
        """Track feedback loops in the workflow"""
        # Simple feedback loop detection: event -> response -> follow-up
        if len(self.events) < 3:
            return

        # Look for patterns where an agent acts, another responds, first agent acts again
        recent = list(self.events)[-3:]

        if (len(recent) == 3 and
            recent[0].agent == recent[2].agent and
            recent[1].agent != recent[0].agent):

            loop_key = f"{recent[0].agent.value}-{recent[1].agent.value}"
            self.feedback_loops[loop_key].append(event)

    def get_agent_workflow_pattern(self, agent: AgentType) -> Dict[str, Any]:
        """Get workflow pattern for a specific agent"""
        agent_events = [e for e in self.events if e.agent == agent]

        if not agent_events:
            return {}

        # Analyze agent's workflow
        interaction_types = defaultdict(int)
        categories = defaultdict(int)
        avg_duration = 0.0

        for event in agent_events:
            interaction_types[event.interaction_type.value] += 1
            if event.pattern_category:
                categories[event.pattern_category.value] += 1
            if event.duration_seconds:
                avg_duration += event.duration_seconds

        if agent_events:
            avg_duration /= len(agent_events)

        return {
            'agent': agent.value,
            'total_events': len(agent_events),
            'interaction_distribution': dict(interaction_types),
            'category_distribution': dict(categories),
            'average_duration': avg_duration,
            'profile': self.agent_profiles[agent],
            'recent_actions': [e.action[:50] for e in agent_events[-10:]]
        }

    def get_team_workflow_pattern(self) -> Dict[str, Any]:
        """Get team workflow patterns"""
        composition = self.team_dynamics.get_team_composition()

        # Most common collaboration pairs
        top_collaborations = sorted(
            self.team_dynamics.collaboration_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # Most common handoff patterns
        top_handoffs = sorted(
            self.team_dynamics.handoff_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # Recent workflow sequence
        recent_sequence = list(self.team_dynamics.workflow_sequences)[-20:]

        return {
            'total_interactions': self.team_dynamics.total_interactions,
            'team_composition': composition,
            'top_collaborations': [{'pair': k, 'frequency': v} for k, v in top_collaborations],
            'top_handoffs': [{'pattern': k, 'frequency': v} for k, v in top_handoffs],
            'decision_distribution': dict(self.team_dynamics.decision_distribution),
            'recent_workflow': recent_sequence,
            'feedback_loops': {
                k: len(v) for k, v in self.feedback_loops.items()
            }
        }

    def get_detected_patterns(self, agent: Optional[AgentType] = None,
                             category: Optional[PatternCategory] = None) -> List[WorkflowPattern]:
        """Get detected patterns"""
        patterns = list(self.patterns.values())

        if agent:
            patterns = [p for p in patterns if agent in p.agents_involved]

        if category:
            patterns = [p for p in patterns if p.category == category]

        # Sort by confidence and frequency
        patterns.sort(key=lambda p: (p.confidence, p.frequency), reverse=True)

        return patterns

    def generate_feedback_insights(self) -> Dict[str, Any]:
        """Generate insights from feedback loops"""
        insights = {
            'individual_patterns': {},
            'team_patterns': self.get_team_workflow_pattern(),
            'detected_patterns': [
                {
                    'type': p.pattern_type,
                    'category': p.category.value,
                    'agents': [a.value for a in p.agents_involved],
                    'description': p.description,
                    'confidence': p.confidence,
                    'frequency': p.frequency
                }
                for p in self.get_detected_patterns()
            ],
            'recommendations': []
        }

        # Individual agent patterns
        for agent in AgentType:
            insights['individual_patterns'][agent.value] = self.get_agent_workflow_pattern(agent)

        # Generate recommendations
        team_composition = self.team_dynamics.get_team_composition()

        # Check if one agent is overworked
        max_contribution = max(team_composition.values()) if team_composition else 0
        if max_contribution > 60:
            max_agent = max(team_composition.items(), key=lambda x: x[1])[0]
            insights['recommendations'].append(
                f"⚠️ {max_agent} is handling {max_contribution:.1f}% of interactions. Consider redistributing workload."
            )

        # Check for feedback loops
        if self.feedback_loops:
            top_loop = max(self.feedback_loops.items(), key=lambda x: len(x[1]))
            insights['recommendations'].append(
                f"🔄 Strong feedback loop detected: {top_loop[0]} ({len(top_loop[1])} iterations)"
            )

        return insights

    def save_data(self):
        """Save workflow data"""
        try:
            # Save events
            events_file = self.data_dir / "events.json"
            with open(events_file, 'w') as f:
                events_data = [
                    {
                        'id': e.id,
                        'timestamp': e.timestamp.isoformat(),
                        'agent': e.agent.value,
                        'interaction_type': e.interaction_type.value,
                        'action': e.action,
                        'context': e.context,
                        'collaborators': [c.value for c in e.collaborators],
                        'outcome': e.outcome,
                        'duration_seconds': e.duration_seconds
                    }
                    for e in list(self.events)[-1000:]  # Last 1000 events
                ]
                json.dump(events_data, f, indent=2)

            # Save patterns
            patterns_file = self.data_dir / "patterns.json"
            with open(patterns_file, 'w') as f:
                patterns_data = [
                    {
                        'id': p.id,
                        'pattern_type': p.pattern_type,
                        'category': p.category.value,
                        'agents_involved': [a.value for a in p.agents_involved],
                        'frequency': p.frequency,
                        'first_seen': p.first_seen.isoformat(),
                        'last_seen': p.last_seen.isoformat(),
                        'description': p.description,
                        'confidence': p.confidence,
                        'metadata': p.metadata
                    }
                    for p in self.patterns.values()
                ]
                json.dump(patterns_data, f, indent=2)

            # Save team dynamics
            dynamics_file = self.data_dir / "team_dynamics.json"
            with open(dynamics_file, 'w') as f:
                json.dump({
                    'total_interactions': self.team_dynamics.total_interactions,
                    'agent_interactions': dict(self.team_dynamics.agent_interactions),
                    'collaboration_frequency': dict(self.team_dynamics.collaboration_frequency),
                    'handoff_patterns': dict(self.team_dynamics.handoff_patterns),
                    'decision_distribution': dict(self.team_dynamics.decision_distribution)
                }, f, indent=2)

            self.logger.info("💾 Data saved")

        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")


async def main():
    """Example usage"""
    system = BioAIFeedbackLoop()

    # Record some example workflow events
    print("🔄 Recording workflow events...")

    # JARVIS creates something
    system.record_event(
        agent=AgentType.JARVIS,
        interaction_type=InteractionType.CREATION,
        action="Created systematic error monitoring system",
        duration_seconds=120.5
    )

    # MARVIN reviews and enhances
    system.record_event(
        agent=AgentType.MARVIN,
        interaction_type=InteractionType.COLLABORATION,
        action="Enhanced system with intuitive pattern recognition",
        collaborators=[AgentType.JARVIS],
        duration_seconds=95.3
    )

    # Human makes decision
    system.record_event(
        agent=AgentType.HUMAN,
        interaction_type=InteractionType.DECISION,
        action="Approved integration of both systems",
        collaborators=[AgentType.JARVIS, AgentType.MARVIN],
        duration_seconds=45.2
    )

    # Handoff from JARVIS to MARVIN
    system.record_event(
        agent=AgentType.JARVIS,
        interaction_type=InteractionType.HANDOFF,
        action="Handed off optimization task",
        collaborators=[AgentType.MARVIN],
        duration_seconds=10.1
    )

    # Generate insights
    insights = system.generate_feedback_insights()

    print("\n🔄 BIO-AI FEEDBACK LOOP INSIGHTS")
    print("=" * 80)
    print(f"Total Interactions: {insights['team_patterns']['total_interactions']}")
    print(f"\nTeam Composition:")
    for agent, percentage in insights['team_patterns']['team_composition'].items():
        print(f"  {agent}: {percentage:.1f}%")

    print(f"\nDetected Patterns: {len(insights['detected_patterns'])}")
    for pattern in insights['detected_patterns'][:5]:
        print(f"  - {pattern['description']} (confidence: {pattern['confidence']:.2f})")

    if insights['recommendations']:
        print(f"\nRecommendations:")
        for rec in insights['recommendations']:
            print(f"  {rec}")

    # Save data
    system.save_data()


if __name__ == "__main__":



    asyncio.run(main())