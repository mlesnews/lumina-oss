#!/usr/bin/env python3
"""
User Interaction & Flowstate Tracker

Tracks user interactions, workflow patterns, and flowstate to enable:
- Replication of user flow and flowstate
- Automation of interactions and workflows
- Enhancement of @manus scaffolding framework
- AI-driven workflow automation

This system watches closely to learn and replicate your work patterns.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class InteractionType(Enum):
    """Types of user interactions"""
    FILE_OPEN = "file_open"
    FILE_EDIT = "file_edit"
    FILE_SAVE = "file_save"
    FILE_CLOSE = "file_close"
    CURSOR_MOVE = "cursor_move"
    TEXT_SELECTION = "text_selection"
    SEARCH = "search"
    COMMAND_EXECUTE = "command_execute"
    TERMINAL_INPUT = "terminal_input"
    TAB_SWITCH = "tab_switch"
    WINDOW_FOCUS = "window_focus"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_STEP = "workflow_step"
    WORKFLOW_COMPLETE = "workflow_complete"
    ASK_REQUEST = "ask_request"
    AI_RESPONSE = "ai_response"


class FlowstateLevel(Enum):
    """Flowstate intensity levels"""
    DEEP_FOCUS = "deep_focus"  # Highly focused, productive state
    ACTIVE_WORK = "active_work"  # Actively working
    EXPLORATION = "exploration"  # Exploring, learning, researching
    CONTEXT_SWITCH = "context_switch"  # Switching between tasks
    IDLE = "idle"  # Not actively working
    BLOCKED = "blocked"  # Blocked or stuck


@dataclass
class UserInteraction:
    """Single user interaction event"""
    interaction_id: str
    timestamp: str
    interaction_type: InteractionType
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["interaction_type"] = self.interaction_type.value
        return data


@dataclass
class FlowstateSession:
    """A flowstate session - continuous period of work"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    flowstate_level: FlowstateLevel = FlowstateLevel.ACTIVE_WORK
    interactions: List[UserInteraction] = field(default_factory=list)
    workflow_pattern: Optional[str] = None
    productivity_score: float = 0.0
    context_switches: int = 0
    focus_duration: float = 0.0  # seconds in deep focus
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["flowstate_level"] = self.flowstate_level.value
        data["interactions"] = [i.to_dict() for i in self.interactions]
        return data


@dataclass
class WorkflowPattern:
    """Identified workflow pattern from user interactions"""
    pattern_id: str
    pattern_name: str
    description: str
    frequency: int = 0
    success_rate: float = 0.0
    average_duration: float = 0.0
    steps: List[Dict[str, Any]] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    automation_candidate: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class UserInteractionFlowstateTracker:
    """
    Tracks user interactions and flowstate to enable workflow automation

    This system watches closely to learn and replicate your work patterns.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "user_interactions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.interactions_file = self.data_dir / "interactions.jsonl"
        self.sessions_file = self.data_dir / "sessions.json"
        self.patterns_file = self.data_dir / "workflow_patterns.json"
        self.flowstate_file = self.data_dir / "current_flowstate.json"

        # Current state
        self.current_session: Optional[FlowstateSession] = None
        self.interactions: List[UserInteraction] = []
        self.workflow_patterns: Dict[str, WorkflowPattern] = {}

        self.logger = get_logger("UserInteractionTracker")
        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing interaction data"""
        # Load sessions
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load last session if active
                    if data.get("active_session"):
                        session_data = data["active_session"]
                        self.current_session = FlowstateSession(
                            session_id=session_data["session_id"],
                            start_time=session_data["start_time"],
                            flowstate_level=FlowstateLevel(session_data["flowstate_level"]),
                            interactions=[UserInteraction(**i) for i in session_data.get("interactions", [])]
                        )
            except Exception as e:
                self.logger.warning(f"Could not load sessions: {e}")

        # Load workflow patterns
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.workflow_patterns = {
                        pid: WorkflowPattern(**pattern_data)
                        for pid, pattern_data in data.items()
                    }
            except Exception as e:
                self.logger.warning(f"Could not load patterns: {e}")

    def start_session(self, flowstate_level: FlowstateLevel = FlowstateLevel.ACTIVE_WORK) -> str:
        """Start a new flowstate session"""
        session_id = f"session_{int(time.time())}"

        self.current_session = FlowstateSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            flowstate_level=flowstate_level
        )

        self.logger.info(f"Started flowstate session: {session_id} ({flowstate_level.value})")
        self._save_current_state()

        return session_id

    def end_session(self):
        """End current flowstate session"""
        if not self.current_session:
            return

        self.current_session.end_time = datetime.now().isoformat()

        # Calculate session metrics
        self._calculate_session_metrics()

        # Save session
        self._save_session()

        # Detect workflow patterns
        self._detect_workflow_patterns()

        self.logger.info(f"Ended flowstate session: {self.current_session.session_id}")
        self.current_session = None
        self._save_current_state()

    def track_interaction(
        self,
        interaction_type: InteractionType,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track a user interaction"""
        # Ensure session exists
        if not self.current_session:
            self.start_session()

        interaction_id = f"interaction_{int(time.time() * 1000)}"

        interaction = UserInteraction(
            interaction_id=interaction_id,
            timestamp=datetime.now().isoformat(),
            interaction_type=interaction_type,
            context=context or {},
            metadata=metadata or {}
        )

        # Add to current session
        self.current_session.interactions.append(interaction)
        self.interactions.append(interaction)

        # Update flowstate based on interaction
        self._update_flowstate(interaction)

        # Save interaction
        self._save_interaction(interaction)
        self._save_current_state()

        return interaction_id

    def _update_flowstate(self, interaction: UserInteraction):
        """Update flowstate based on interaction patterns"""
        if not self.current_session:
            return

        # Analyze interaction patterns to determine flowstate
        recent_interactions = self.current_session.interactions[-10:]

        # Count interaction types
        interaction_counts = {}
        for i in recent_interactions:
            it = i.interaction_type.value
            interaction_counts[it] = interaction_counts.get(it, 0) + 1

        # Determine flowstate level
        if interaction_counts.get(InteractionType.FILE_EDIT.value, 0) > 5:
            # High edit activity = deep focus
            self.current_session.flowstate_level = FlowstateLevel.DEEP_FOCUS
            self.current_session.focus_duration += 1.0
        elif interaction_counts.get(InteractionType.TAB_SWITCH.value, 0) > 3:
            # High tab switching = context switch
            self.current_session.flowstate_level = FlowstateLevel.CONTEXT_SWITCH
            self.current_session.context_switches += 1
        elif interaction_counts.get(InteractionType.SEARCH.value, 0) > 2:
            # High search = exploration
            self.current_session.flowstate_level = FlowstateLevel.EXPLORATION
        else:
            # Default to active work
            self.current_session.flowstate_level = FlowstateLevel.ACTIVE_WORK

    def _calculate_session_metrics(self):
        """Calculate session productivity metrics"""
        if not self.current_session:
            return

        session = self.current_session

        # Calculate productivity score
        total_interactions = len(session.interactions)
        focus_ratio = session.focus_duration / max(1, (time.time() - datetime.fromisoformat(session.start_time).timestamp()))

        # Productivity factors
        edit_count = sum(1 for i in session.interactions if i.interaction_type == InteractionType.FILE_EDIT)
        save_count = sum(1 for i in session.interactions if i.interaction_type == InteractionType.FILE_SAVE)

        session.productivity_score = (
            (edit_count * 0.4) +
            (save_count * 0.3) +
            (focus_ratio * 0.3)
        )

    def _detect_workflow_patterns(self):
        """Detect workflow patterns from session interactions"""
        if not self.current_session:
            return

        session = self.current_session
        interactions = session.interactions

        # Group interactions into sequences
        sequences = []
        current_sequence = []

        for interaction in interactions:
            if interaction.interaction_type in [InteractionType.WORKFLOW_START, InteractionType.ASK_REQUEST]:
                if current_sequence:
                    sequences.append(current_sequence)
                current_sequence = [interaction]
            elif interaction.interaction_type in [InteractionType.WORKFLOW_COMPLETE, InteractionType.AI_RESPONSE]:
                current_sequence.append(interaction)
                sequences.append(current_sequence)
                current_sequence = []
            else:
                current_sequence.append(interaction)

        # Analyze sequences for patterns
        for sequence in sequences:
            if len(sequence) < 3:
                continue

            # Create pattern signature
            pattern_signature = self._create_pattern_signature(sequence)
            pattern_id = hashlib.md5(pattern_signature.encode()).hexdigest()[:16]

            # Check if pattern exists
            if pattern_id in self.workflow_patterns:
                pattern = self.workflow_patterns[pattern_id]
                pattern.frequency += 1
            else:
                # Create new pattern
                pattern = WorkflowPattern(
                    pattern_id=pattern_id,
                    pattern_name=f"Pattern_{pattern_id[:8]}",
                    description=f"Workflow pattern detected from interactions",
                    frequency=1,
                    steps=[i.to_dict() for i in sequence],
                    automation_candidate=len(sequence) > 5  # Auto-candidate if >5 steps
                )
                self.workflow_patterns[pattern_id] = pattern

            # Update pattern metrics
            pattern.average_duration = (
                (pattern.average_duration * (pattern.frequency - 1) + len(sequence)) / pattern.frequency
            )

        # Save patterns
        self._save_patterns()

    def _create_pattern_signature(self, sequence: List[UserInteraction]) -> str:
        """Create a signature for a sequence of interactions"""
        types = [i.interaction_type.value for i in sequence]
        return "->".join(types)

    def get_automation_candidates(self) -> List[WorkflowPattern]:
        """Get workflow patterns that are candidates for automation"""
        return [
            pattern for pattern in self.workflow_patterns.values()
            if pattern.automation_candidate and pattern.frequency >= 3
        ]

    def generate_automation_script(self, pattern_id: str) -> Optional[str]:
        """Generate automation script for a workflow pattern"""
        if pattern_id not in self.workflow_patterns:
            return None

        pattern = self.workflow_patterns[pattern_id]

        # Generate Python script for automation
        script_lines = [
            f"#!/usr/bin/env python3",
            f'"""',
            f"Automated Workflow: {pattern.pattern_name}",
            f"",
            f"Description: {pattern.description}",
            f"Frequency: {pattern.frequency}",
            f"Average Duration: {pattern.average_duration:.2f} steps",
            f'"""',
            "",
            "from pathlib import Path",
            "import time",
            "",
            f"def automate_{pattern.pattern_name.lower().replace('-', '_')}():",
            f'    """Automate workflow pattern: {pattern.pattern_name}"""',
            "    # Generated from user interaction tracking",
            "",
        ]

        # Add steps based on pattern
        for i, step in enumerate(pattern.steps):
            interaction_type = step.get("interaction_type")
            context = step.get("context", {})

            if interaction_type == InteractionType.FILE_OPEN.value:
                file_path = context.get("file_path", "")
                script_lines.append(f"    # Step {i+1}: Open file")
                script_lines.append(f'    open_file("{file_path}")')
            elif interaction_type == InteractionType.FILE_EDIT.value:
                script_lines.append(f"    # Step {i+1}: Edit file")
                script_lines.append(f'    edit_file(context={context})')
            elif interaction_type == InteractionType.COMMAND_EXECUTE.value:
                command = context.get("command", "")
                script_lines.append(f"    # Step {i+1}: Execute command")
                script_lines.append(f'    execute_command("{command}")')

        script_lines.extend([
            "",
            "if __name__ == '__main__':",
            f"    automate_{pattern.pattern_name.lower().replace('-', '_')}()",
            ""
        ])

        return "\n".join(script_lines)

    def _save_interaction(self, interaction: UserInteraction):
        """Save interaction to JSONL file"""
        try:
            with open(self.interactions_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(interaction.to_dict()) + '\n')
        except Exception as e:
            self.logger.error(f"Error saving interaction: {e}")

    def _save_session(self):
        """Save completed session"""
        if not self.current_session:
            return

        sessions_data = {}
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
            except Exception:
                pass

        sessions_data.setdefault("sessions", []).append(self.current_session.to_dict())
        sessions_data["last_session"] = self.current_session.session_id

        with open(self.sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions_data, f, indent=2, ensure_ascii=False)

    def _save_current_state(self):
        try:
            """Save current flowstate"""
            if not self.current_session:
                return

            state = {
                "active_session": self.current_session.to_dict(),
                "timestamp": datetime.now().isoformat()
            }

            with open(self.flowstate_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_current_state: {e}", exc_info=True)
            raise
    def _save_patterns(self):
        try:
            """Save workflow patterns"""
            patterns_data = {
                pid: pattern.to_dict()
                for pid, pattern in self.workflow_patterns.items()
            }

            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_patterns: {e}", exc_info=True)
            raise
    def get_current_flowstate(self) -> Optional[Dict[str, Any]]:
        """Get current flowstate"""
        if not self.current_session:
            return None

        return {
            "session_id": self.current_session.session_id,
            "flowstate_level": self.current_session.flowstate_level.value,
            "productivity_score": self.current_session.productivity_score,
            "interaction_count": len(self.current_session.interactions),
            "context_switches": self.current_session.context_switches,
            "focus_duration": self.current_session.focus_duration
        }

    def enhance_manus_scaffolding(self) -> Dict[str, Any]:
        """Enhance @manus scaffolding framework with learned patterns"""
        automation_candidates = self.get_automation_candidates()

        enhancement = {
            "patterns_learned": len(self.workflow_patterns),
            "automation_candidates": len(automation_candidates),
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "pattern_name": p.pattern_name,
                    "frequency": p.frequency,
                    "automation_script": self.generate_automation_script(p.pattern_id)
                }
                for p in automation_candidates
            ],
            "recommendations": self._generate_automation_recommendations()
        }

        return enhancement

    def _generate_automation_recommendations(self) -> List[str]:
        """Generate recommendations for automation"""
        recommendations = []

        automation_candidates = self.get_automation_candidates()

        if automation_candidates:
            recommendations.append(
                f"Found {len(automation_candidates)} workflow patterns ready for automation"
            )

        # Check for high-frequency patterns
        high_freq = [p for p in self.workflow_patterns.values() if p.frequency >= 5]
        if high_freq:
            recommendations.append(
                f"{len(high_freq)} patterns detected 5+ times - strong automation candidates"
            )

        return recommendations


def main():
    """Main execution for testing"""
    tracker = UserInteractionFlowstateTracker()

    print("👁️ User Interaction & Flowstate Tracker")
    print("=" * 80)

    # Start session
    session_id = tracker.start_session(FlowstateLevel.ACTIVE_WORK)
    print(f"✅ Started session: {session_id}")

    # Simulate some interactions
    tracker.track_interaction(
        InteractionType.FILE_OPEN,
        context={"file_path": "workflow_base.py"},
        metadata={"reason": "reviewing code"}
    )

    tracker.track_interaction(
        InteractionType.FILE_EDIT,
        context={"file_path": "workflow_base.py", "lines": "1-50"},
        metadata={"action": "review"}
    )

    # Get current flowstate
    flowstate = tracker.get_current_flowstate()
    print(f"\n📊 Current Flowstate:")
    print(f"   Level: {flowstate['flowstate_level']}")
    print(f"   Interactions: {flowstate['interaction_count']}")

    # End session
    tracker.end_session()
    print(f"\n✅ Session ended")

    # Get automation candidates
    candidates = tracker.get_automation_candidates()
    print(f"\n🤖 Automation Candidates: {len(candidates)}")

    # Enhance MANUS scaffolding
    enhancement = tracker.enhance_manus_scaffolding()
    print(f"\n🔧 MANUS Enhancement:")
    print(f"   Patterns Learned: {enhancement['patterns_learned']}")
    print(f"   Automation Candidates: {enhancement['automation_candidates']}")


if __name__ == "__main__":



    main()