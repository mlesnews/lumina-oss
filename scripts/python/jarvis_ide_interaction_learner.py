#!/usr/bin/env python3
"""
JARVIS IDE Interaction Learner
MANUS Framework - Learn from IDE Operator Inputs

Tracks and learns from all IDE operator inputs to map features/functions
to appropriate MANUS agents for intelligent task assignment.

Features:
- Real-time IDE interaction tracking
- Pattern recognition from user behavior
- Feature-to-agent mapping
- Learning and adaptation
- Agent assignment recommendations

@JARVIS @MANUS @SYPHON
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict, Counter
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISIDEInteractionLearner")

try:
    from jarvis_cursor_ide_keyboard_integration import get_jarvis_cursor_integration
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logger.warning("JARVIS-Cursor integration not available")


@dataclass
class IDEInteraction:
    """Record of a single IDE interaction"""
    timestamp: datetime
    interaction_type: str  # "keyboard_shortcut", "command_palette", "mouse", "voice", "chat"
    command: str
    feature: str  # Feature/function being used
    context: Dict[str, Any] = field(default_factory=dict)
    outcome: Optional[str] = None  # "success", "failure", "partial"
    duration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class FeaturePattern:
    """Pattern learned for a specific feature"""
    feature: str
    interaction_sequence: List[str]  # Sequence of interactions
    context_patterns: Dict[str, Any] = field(default_factory=dict)
    success_rate: float = 0.0
    average_duration: float = 0.0
    frequency: int = 0
    last_used: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        return data


@dataclass
class AgentAssignment:
    """Agent assignment recommendation for a feature"""
    feature: str
    agent_id: str
    agent_name: str
    confidence: float
    rationale: str
    capabilities_match: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    last_assigned: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.last_assigned:
            data['last_assigned'] = self.last_assigned.isoformat()
        return data


class JARVISIDEInteractionLearner:
    """
    Learn from IDE operator inputs and map features to MANUS agents

    Tracks all IDE interactions, learns patterns, and assigns
    appropriate MANUS agents to each feature/function.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize interaction learner"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Data directories
        self.data_dir = self.project_root / "data" / "jarvis_ide_learning"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Interaction history
        self.interaction_history: List[IDEInteraction] = []
        self.interaction_queue = []
        self.tracking_active = False

        # Learning data
        self.feature_patterns: Dict[str, FeaturePattern] = {}
        self.feature_agent_mappings: Dict[str, AgentAssignment] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}

        # Load existing data
        self._load_agent_capabilities()
        self._load_learning_data()

        # Integration with Cursor IDE
        self.integration = None
        if INTEGRATION_AVAILABLE:
            try:
                self.integration = get_jarvis_cursor_integration(project_root=self.project_root)
            except Exception as e:
                logger.warning(f"Integration initialization failed: {e}")

        # Tracking thread
        self.tracking_thread: Optional[threading.Thread] = None

        logger.info("✅ JARVIS IDE Interaction Learner initialized")
        logger.info(f"   Loaded {len(self.feature_patterns)} feature patterns")
        logger.info(f"   Loaded {len(self.feature_agent_mappings)} agent mappings")

    def _load_agent_capabilities(self):
        """Load MANUS agent capabilities from config"""
        agents_config = self.project_root / "config" / "agent_communication" / "agents.json"

        try:
            if agents_config.exists():
                with open(agents_config, 'r', encoding='utf-8') as f:
                    agents = json.load(f)
                    for agent_id, agent_info in agents.items():
                        self.agent_capabilities[agent_id] = agent_info.get("capabilities", [])
                    logger.info(f"✅ Loaded capabilities for {len(self.agent_capabilities)} agents")
        except Exception as e:
            logger.warning(f"Failed to load agent capabilities: {e}")
            # Fallback to default capabilities
            self.agent_capabilities = {
                "r2d2": ["technical", "repair", "hacking", "system_access", "diagnostics"],
                "c3po": ["communication", "translation", "protocol", "escalation", "coordination"],
                "k2so": ["security", "threat_analysis", "access_control", "monitoring"],
                "2-1b": ["health_monitoring", "system_health", "recovery", "prevention"],
                "ig88": ["critical_resolution", "elimination", "force", "escalation"],
                "mousedroid": ["mouse_automation", "keyboard_automation", "screen_automation"],
                "uatu": ["deep_research", "pattern_analysis", "comprehensive_validation", "insight_generation"]
            }

    def _load_learning_data(self):
        """Load previously learned patterns and mappings"""
        patterns_file = self.data_dir / "feature_patterns.json"
        mappings_file = self.data_dir / "feature_agent_mappings.json"

        # Load feature patterns
        try:
            if patterns_file.exists():
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
                    for feature, pattern_data in patterns_data.items():
                        pattern = FeaturePattern(
                            feature=feature,
                            interaction_sequence=pattern_data.get("interaction_sequence", []),
                            context_patterns=pattern_data.get("context_patterns", {}),
                            success_rate=pattern_data.get("success_rate", 0.0),
                            average_duration=pattern_data.get("average_duration", 0.0),
                            frequency=pattern_data.get("frequency", 0),
                            last_used=datetime.fromisoformat(pattern_data["last_used"]) if pattern_data.get("last_used") else None
                        )
                        self.feature_patterns[feature] = pattern
                    logger.info(f"✅ Loaded {len(self.feature_patterns)} feature patterns")
        except Exception as e:
            logger.warning(f"Failed to load feature patterns: {e}")

        # Load agent mappings
        try:
            if mappings_file.exists():
                with open(mappings_file, 'r', encoding='utf-8') as f:
                    mappings_data = json.load(f)
                    for feature, mapping_data in mappings_data.items():
                        assignment = AgentAssignment(
                            feature=feature,
                            agent_id=mapping_data.get("agent_id", ""),
                            agent_name=mapping_data.get("agent_name", ""),
                            confidence=mapping_data.get("confidence", 0.0),
                            rationale=mapping_data.get("rationale", ""),
                            capabilities_match=mapping_data.get("capabilities_match", []),
                            success_rate=mapping_data.get("success_rate", 0.0),
                            last_assigned=datetime.fromisoformat(mapping_data["last_assigned"]) if mapping_data.get("last_assigned") else None
                        )
                        self.feature_agent_mappings[feature] = assignment
                    logger.info(f"✅ Loaded {len(self.feature_agent_mappings)} agent mappings")
        except Exception as e:
            logger.warning(f"Failed to load agent mappings: {e}")

    def _save_learning_data(self):
        """Save learned patterns and mappings"""
        patterns_file = self.data_dir / "feature_patterns.json"
        mappings_file = self.data_dir / "feature_agent_mappings.json"

        # Save feature patterns
        try:
            patterns_data = {
                feature: pattern.to_dict()
                for feature, pattern in self.feature_patterns.items()
            }
            with open(patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save feature patterns: {e}")

        # Save agent mappings
        try:
            mappings_data = {
                feature: mapping.to_dict()
                for feature, mapping in self.feature_agent_mappings.items()
            }
            with open(mappings_file, 'w', encoding='utf-8') as f:
                json.dump(mappings_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save agent mappings: {e}")

    def record_interaction(self, interaction: IDEInteraction):
        """
        Record an IDE interaction for learning

        Args:
            interaction: IDEInteraction to record
        """
        self.interaction_history.append(interaction)
        self.interaction_queue.append(interaction)

        # Keep history limited (last 10000 interactions)
        if len(self.interaction_history) > 10000:
            self.interaction_history = self.interaction_history[-10000:]

        # Learn from interaction
        self._learn_from_interaction(interaction)

        logger.debug(f"📝 Recorded interaction: {interaction.feature} ({interaction.interaction_type})")

    def _learn_from_interaction(self, interaction: IDEInteraction):
        """Learn patterns from a single interaction"""
        feature = interaction.feature

        # Update or create feature pattern
        if feature not in self.feature_patterns:
            self.feature_patterns[feature] = FeaturePattern(
                feature=feature,
                interaction_sequence=[interaction.command],
                context_patterns={},
                success_rate=1.0 if interaction.outcome == "success" else 0.0,
                average_duration=interaction.duration,
                frequency=1,
                last_used=interaction.timestamp
            )
        else:
            pattern = self.feature_patterns[feature]
            pattern.frequency += 1
            pattern.last_used = interaction.timestamp

            # Update interaction sequence (keep last 10)
            if interaction.command not in pattern.interaction_sequence:
                pattern.interaction_sequence.append(interaction.command)
            if len(pattern.interaction_sequence) > 10:
                pattern.interaction_sequence = pattern.interaction_sequence[-10:]

            # Update success rate
            if interaction.outcome:
                total = pattern.frequency
                current_successes = pattern.success_rate * (total - 1)
                if interaction.outcome == "success":
                    current_successes += 1
                pattern.success_rate = current_successes / total

            # Update average duration
            total_duration = pattern.average_duration * (pattern.frequency - 1) + interaction.duration
            pattern.average_duration = total_duration / pattern.frequency

        # Update context patterns
        if interaction.context:
            for key, value in interaction.context.items():
                if key not in pattern.context_patterns:
                    pattern.context_patterns[key] = []
                pattern.context_patterns[key].append(value)
                # Keep last 20 context values per key
                if len(pattern.context_patterns[key]) > 20:
                    pattern.context_patterns[key] = pattern.context_patterns[key][-20:]

        # Periodically save learning data
        if len(self.interaction_queue) >= 100:
            self._save_learning_data()
            self.interaction_queue.clear()

    def map_feature_to_agent(self, feature: str, context: Optional[Dict[str, Any]] = None) -> Optional[AgentAssignment]:
        """
        Map a feature to the most appropriate MANUS agent

        Args:
            feature: Feature/function name
            context: Optional context information

        Returns:
            AgentAssignment recommendation
        """
        # Check if we have an existing mapping
        if feature in self.feature_agent_mappings:
            assignment = self.feature_agent_mappings[feature]
            # Update last assigned time
            assignment.last_assigned = datetime.now()
            return assignment

        # Learn new mapping based on feature characteristics
        assignment = self._create_agent_assignment(feature, context)
        if assignment:
            self.feature_agent_mappings[feature] = assignment
            self._save_learning_data()

        return assignment

    def _create_agent_assignment(self, feature: str, context: Optional[Dict[str, Any]] = None) -> Optional[AgentAssignment]:
        """Create agent assignment for a feature based on analysis"""
        # Feature-to-agent mapping rules (learned from patterns)
        feature_keywords = {
            "file": ["r2d2", "mousedroid"],
            "edit": ["r2d2", "mousedroid"],
            "debug": ["r2d2", "2-1b"],
            "git": ["r2d2", "c3po"],
            "search": ["r2d2", "uatu"],
            "refactor": ["r2d2", "uatu"],
            "chat": ["c3po", "r2d2"],
            "composer": ["r2d2", "uatu"],
            "security": ["k2so"],
            "health": ["2-1b"],
            "critical": ["ig88"],
            "automation": ["mousedroid", "r2d2"],
            "pattern": ["uatu", "r2d2"],
            "research": ["uatu"],
            "coordination": ["c3po"],
            "communication": ["c3po"]
        }

        # Find best matching agent
        best_agent = None
        best_score = 0.0
        best_capabilities = []

        feature_lower = feature.lower()

        for agent_id, capabilities in self.agent_capabilities.items():
            score = 0.0
            matched_capabilities = []

            # Check keyword matches
            for keyword, preferred_agents in feature_keywords.items():
                if keyword in feature_lower:
                    if agent_id in preferred_agents:
                        score += 2.0
                    matched_capabilities.append(keyword)

            # Check capability matches
            for capability in capabilities:
                if capability in feature_lower:
                    score += 1.0
                    matched_capabilities.append(capability)

            # Check pattern-based recommendations
            if feature in self.feature_patterns:
                pattern = self.feature_patterns[feature]
                # Prefer agents that match successful patterns
                if pattern.success_rate > 0.7:
                    score += 1.0

            if score > best_score:
                best_score = score
                best_agent = agent_id
                best_capabilities = matched_capabilities

        if not best_agent:
            # Default to R2-D2 for technical tasks
            best_agent = "r2d2"
            best_score = 0.5
            best_capabilities = ["technical"]

        # Get agent name
        agent_name = best_agent.upper().replace("-", "-")
        if best_agent == "r2d2":
            agent_name = "R2-D2"
        elif best_agent == "c3po":
            agent_name = "C-3PO"
        elif best_agent == "k2so":
            agent_name = "K-2SO"
        elif best_agent == "2-1b":
            agent_name = "2-1B"
        elif best_agent == "ig88":
            agent_name = "IG-88"
        elif best_agent == "mousedroid":
            agent_name = "MouseDroid"
        elif best_agent == "uatu":
            agent_name = "The Watcher Uatu"

        # Create assignment
        confidence = min(best_score / 5.0, 1.0)  # Normalize to 0-1
        rationale = f"Assigned based on feature analysis: {', '.join(best_capabilities[:3])}"

        assignment = AgentAssignment(
            feature=feature,
            agent_id=best_agent,
            agent_name=agent_name,
            confidence=confidence,
            rationale=rationale,
            capabilities_match=best_capabilities[:5],
            success_rate=0.0,  # Will be updated as we learn
            last_assigned=datetime.now()
        )

        return assignment

    def get_all_assignments(self) -> Dict[str, AgentAssignment]:
        """Get all feature-to-agent mappings"""
        return self.feature_agent_mappings.copy()

    def get_agent_assignments(self, agent_id: str) -> List[AgentAssignment]:
        """Get all assignments for a specific agent"""
        return [
            assignment
            for assignment in self.feature_agent_mappings.values()
            if assignment.agent_id == agent_id
        ]

    def update_assignment_success(self, feature: str, success: bool):
        """Update success rate for an agent assignment"""
        if feature in self.feature_agent_mappings:
            assignment = self.feature_agent_mappings[feature]
            # Simple moving average update
            if assignment.success_rate == 0.0:
                assignment.success_rate = 1.0 if success else 0.0
            else:
                assignment.success_rate = (assignment.success_rate * 0.9) + (1.0 if success else 0.0) * 0.1
            self._save_learning_data()

    def start_tracking(self):
        """Start tracking IDE interactions"""
        if self.tracking_active:
            return

        self.tracking_active = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()
        logger.info("👁️ Started tracking IDE interactions")

    def stop_tracking(self):
        """Stop tracking IDE interactions"""
        self.tracking_active = False
        if self.tracking_thread:
            self.tracking_thread.join(timeout=5)
        self._save_learning_data()
        logger.info("🛑 Stopped tracking IDE interactions")

    def _tracking_loop(self):
        """Background tracking loop"""
        while self.tracking_active:
            try:
                # This would integrate with IDE event monitoring
                # For now, interactions are recorded manually via record_interaction()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}")
                time.sleep(5)

    def generate_assignments_report(self) -> Dict[str, Any]:
        """Generate a report of all feature-to-agent assignments"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_features": len(self.feature_agent_mappings),
            "total_patterns": len(self.feature_patterns),
            "agents": {},
            "features_by_category": defaultdict(list)
        }

        # Group by agent
        for feature, assignment in self.feature_agent_mappings.items():
            agent_id = assignment.agent_id
            if agent_id not in report["agents"]:
                report["agents"][agent_id] = {
                    "agent_name": assignment.agent_name,
                    "features": [],
                    "total_assignments": 0,
                    "average_confidence": 0.0,
                    "average_success_rate": 0.0
                }

            agent_info = report["agents"][agent_id]
            agent_info["features"].append({
                "feature": feature,
                "confidence": assignment.confidence,
                "success_rate": assignment.success_rate,
                "capabilities_match": assignment.capabilities_match
            })
            agent_info["total_assignments"] += 1

        # Calculate averages
        for agent_id, agent_info in report["agents"].items():
            if agent_info["total_assignments"] > 0:
                confidences = [f["confidence"] for f in agent_info["features"]]
                success_rates = [f["success_rate"] for f in agent_info["features"] if f["success_rate"] > 0]
                agent_info["average_confidence"] = sum(confidences) / len(confidences) if confidences else 0.0
                agent_info["average_success_rate"] = sum(success_rates) / len(success_rates) if success_rates else 0.0

        return report


def get_ide_learner(project_root: Optional[Path] = None) -> JARVISIDEInteractionLearner:
    """Get or create IDE interaction learner instance"""
    global _learner_instance
    if '_learner_instance' not in globals():
        _learner_instance = JARVISIDEInteractionLearner(project_root=project_root)
    return _learner_instance


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS IDE Interaction Learner - Learn from operator inputs and map to MANUS agents"
    )
    parser.add_argument("--record", type=str, nargs=3, metavar=("FEATURE", "COMMAND", "TYPE"),
                       help="Record an interaction: feature command type")
    parser.add_argument("--map", type=str, help="Map feature to agent")
    parser.add_argument("--report", action="store_true", help="Generate assignments report")
    parser.add_argument("--agent", type=str, help="Show assignments for specific agent")
    parser.add_argument("--start-tracking", action="store_true", help="Start tracking interactions")

    args = parser.parse_args()

    learner = get_ide_learner()

    if args.record:
        feature, command, interaction_type = args.record
        interaction = IDEInteraction(
            timestamp=datetime.now(),
            interaction_type=interaction_type,
            command=command,
            feature=feature,
            outcome="success"
        )
        learner.record_interaction(interaction)
        print(f"✅ Recorded interaction: {feature}")

    elif args.map:
        assignment = learner.map_feature_to_agent(args.map)
        if assignment:
            print(f"Feature: {args.map}")
            print(f"Agent: {assignment.agent_name} ({assignment.agent_id})")
            print(f"Confidence: {assignment.confidence:.2f}")
            print(f"Rationale: {assignment.rationale}")
            print(f"Capabilities: {', '.join(assignment.capabilities_match)}")
        else:
            print(f"❌ Could not map feature: {args.map}")

    elif args.report:
        report = learner.generate_assignments_report()
        print(json.dumps(report, indent=2, default=str))

    elif args.agent:
        assignments = learner.get_agent_assignments(args.agent)
        print(f"Assignments for {args.agent}:")
        for assignment in assignments:
            print(f"  {assignment.feature}: {assignment.confidence:.2f} confidence")

    elif args.start_tracking:
        learner.start_tracking()
        print("👁️ Tracking started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            learner.stop_tracking()
            print("\n🛑 Tracking stopped")

    else:
        parser.print_help()
        print("\n✅ JARVIS IDE Interaction Learner")
        print("   Learn from operator inputs and map features to MANUS agents")


if __name__ == "__main__":


    main()