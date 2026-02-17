#!/usr/bin/env python3
"""
Virtual Assistant Action Framework - Unified Action Sequences

Extracts and unifies action sequences from Ace (Iron Man VA) and integrates
them with full JARVIS and Lumina ecosystem features for both IM and AC virtual assistants.

Features:
- State management (idle, listening, speaking, processing, combat, alert)
- Action sequences (wandering, combat, conversation, SYPHON enhancement)
- Visual effects (arc reactor, expressions, health, dice rolls)
- JARVIS integration (combat logging, decision tracking, pattern extraction)
- Lumina integration (R5, @helpdesk, alerts, ecosystem)

Tags: #VA #ACTIONS #JARVIS #LUMINA #PEAK @JARVIS @LUMINA
"""

import sys
import time
import json
import random
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, field

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

logger = get_logger("VAActionFramework")


class VAState(Enum):
    """Virtual Assistant States"""
    IDLE = "idle"
    LISTENING = "listening"
    SPEAKING = "speaking"
    PROCESSING = "processing"
    WANDERING = "wandering"
    COMBAT = "combat"
    ALERT = "alert"
    CRITICAL = "critical"
    THINKING = "thinking"
    NOTIFYING = "notifying"


class EyeExpression(Enum):
    """Eye expression states"""
    NORMAL = "normal"
    ALERT = "alert"
    THINKING = "thinking"
    SPEAKING = "speaking"
    COMBAT = "combat"
    CRITICAL = "critical"


class MouthExpression(Enum):
    """Mouth expression states"""
    NEUTRAL = "neutral"
    SMILE = "smile"
    FROWN = "frown"
    SPEAKING = "speaking"
    COMBAT = "combat"


@dataclass
class ActionSequence:
    """Action sequence definition"""
    name: str
    description: str
    state: VAState
    duration: float  # seconds
    visual_effects: List[str] = field(default_factory=list)
    audio_effects: List[str] = field(default_factory=list)
    jarvis_logged: bool = False
    lumina_integrated: bool = False
    pattern_id: Optional[str] = None


@dataclass
class CombatAction:
    """Combat action definition"""
    action_type: str  # lightsaber, repulsor, unibeam, etc.
    damage: float
    visual_effect: str
    jarvis_logged: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class VAActionFramework:
    """
    Unified Action Framework for Virtual Assistants

    Extracts action sequences from Ace and provides unified interface
    for both IM and AC virtual assistants with full JARVIS/Lumina integration.
    """

    def __init__(self, project_root: Path, va_type: str = "im"):
        """
        Initialize action framework

        Args:
            project_root: Project root directory
            va_type: Virtual assistant type ("im" or "ac")
        """
        self.project_root = project_root
        self.va_type = va_type
        self.logger = logger

        # State management
        self.current_state = VAState.IDLE
        self.previous_state = None
        self.state_transitions = []

        # Expression system
        self.eye_expression = EyeExpression.NORMAL
        self.mouth_expression = MouthExpression.NEUTRAL
        self.eye_intensity = 1.0
        self.expression_modifier = 0.0

        # Action sequences
        self.active_sequences: List[ActionSequence] = []
        self.sequence_history: List[ActionSequence] = []

        # Combat system
        self.combat_active = False
        self.combat_actions: List[CombatAction] = []
        self.combat_start_time: Optional[float] = None

        # JARVIS integration
        self.jarvis_integration = None
        self.jarvis_combat_log = []
        self.jarvis_decisions = []
        self._init_jarvis()

        # Lumina integration
        self.lumina_integrated = False
        self.r5_integration = None
        self.helpdesk_integration = None
        self._init_lumina()

        # Visual effects
        self.arc_reactor_pulse = 0.0
        self.visual_effects_queue = []

        # Action callbacks
        self.action_callbacks: Dict[str, List[Callable]] = {}

        logger.info(f"✅ VAActionFramework initialized for {va_type.upper()} VA")

    def _init_jarvis(self):
        """Initialize JARVIS integration"""
        try:
            from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
            self.jarvis_integration = JARVISHelpdeskIntegration(self.project_root)
            logger.info("✅ JARVIS integration loaded")
        except Exception as e:
            logger.debug(f"JARVIS integration not available: {e}")

    def _init_lumina(self):
        """Initialize Lumina ecosystem integration"""
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            self.r5_integration = R5LivingContextMatrix(self.project_root)
            logger.info("✅ R5 integration loaded")
        except Exception as e:
            logger.debug(f"R5 integration not available: {e}")

        try:
            from droid_actor_system import DroidActorSystem
            self.helpdesk_integration = DroidActorSystem(self.project_root)
            logger.info("✅ @helpdesk integration loaded")
        except Exception as e:
            logger.debug(f"@helpdesk integration not available: {e}")

        self.lumina_integrated = self.r5_integration is not None or self.helpdesk_integration is not None

    def set_state(self, new_state: VAState, reason: str = ""):
        """
        Set VA state with JARVIS logging

        Args:
            new_state: New state to transition to
            reason: Reason for state transition
        """
        if new_state == self.current_state:
            return

        self.previous_state = self.current_state
        self.current_state = new_state

        transition = {
            "timestamp": datetime.now().isoformat(),
            "from": self.previous_state.value if self.previous_state else None,
            "to": new_state.value,
            "reason": reason
        }
        self.state_transitions.append(transition)

        # Update expressions based on state
        self._update_expressions_for_state(new_state)

        # JARVIS logging
        if self.jarvis_integration:
            try:
                self.jarvis_decisions.append({
                    "type": "state_transition",
                    "data": transition,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.debug(f"JARVIS logging error: {e}")

        logger.debug(f"State transition: {self.previous_state} → {new_state} ({reason})")

    def _update_expressions_for_state(self, state: VAState):
        """Update eye and mouth expressions based on state"""
        if state == VAState.LISTENING:
            self.eye_expression = EyeExpression.ALERT
            self.mouth_expression = MouthExpression.NEUTRAL
        elif state == VAState.SPEAKING:
            self.eye_expression = EyeExpression.SPEAKING
            self.mouth_expression = MouthExpression.SPEAKING
        elif state == VAState.PROCESSING or state == VAState.THINKING:
            self.eye_expression = EyeExpression.THINKING
            self.mouth_expression = MouthExpression.NEUTRAL
        elif state == VAState.COMBAT:
            self.eye_expression = EyeExpression.COMBAT
            self.mouth_expression = MouthExpression.COMBAT
        elif state == VAState.ALERT or state == VAState.CRITICAL:
            self.eye_expression = EyeExpression.ALERT
            self.mouth_expression = MouthExpression.FROWN
        elif state == VAState.NOTIFYING:
            self.eye_expression = EyeExpression.NORMAL
            self.mouth_expression = MouthExpression.SMILE
        else:  # IDLE, WANDERING
            self.eye_expression = EyeExpression.NORMAL
            self.mouth_expression = MouthExpression.NEUTRAL

    def start_action_sequence(self, sequence: ActionSequence) -> bool:
        """
        Start an action sequence

        Args:
            sequence: Action sequence to start

        Returns:
            True if sequence started successfully
        """
        try:
            # Set state
            self.set_state(sequence.state, f"Starting action: {sequence.name}")

            # Add to active sequences
            self.active_sequences.append(sequence)

            # Register callbacks
            if sequence.name in self.action_callbacks:
                for callback in self.action_callbacks[sequence.name]:
                    try:
                        callback(sequence)
                    except Exception as e:
                        logger.warning(f"Action callback error: {e}")

            # JARVIS logging
            if sequence.jarvis_logged and self.jarvis_integration:
                self._log_to_jarvis("action_sequence_started", {
                    "sequence": sequence.name,
                    "state": sequence.state.value,
                    "duration": sequence.duration
                })

            # Lumina integration
            if sequence.lumina_integrated and self.r5_integration:
                try:
                    self.r5_integration.aggregate_context({
                        "type": "va_action",
                        "sequence": sequence.name,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.debug(f"R5 aggregation error: {e}")

            logger.info(f"▶️  Action sequence started: {sequence.name}")
            return True
        except Exception as e:
            logger.error(f"Error starting action sequence: {e}")
            return False

    def end_action_sequence(self, sequence_name: str):
        """End an action sequence"""
        for seq in self.active_sequences[:]:
            if seq.name == sequence_name:
                self.active_sequences.remove(seq)
                self.sequence_history.append(seq)

                # JARVIS logging
                if seq.jarvis_logged and self.jarvis_integration:
                    self._log_to_jarvis("action_sequence_ended", {
                        "sequence": seq.name,
                        "duration": seq.duration
                    })

                logger.debug(f"⏹️  Action sequence ended: {sequence_name}")
                break

    def start_combat(self, combat_type: str = "lightsaber", opponent: str = "acva"):
        """
        Start combat action sequence

        Args:
            combat_type: Type of combat (lightsaber, repulsor, unibeam, etc.)
            opponent: Opponent identifier
        """
        self.combat_active = True
        self.combat_start_time = time.time()

        sequence = ActionSequence(
            name=f"combat_{combat_type}",
            description=f"{combat_type} combat with {opponent}",
            state=VAState.COMBAT,
            duration=12.0,  # Default combat duration
            visual_effects=[f"{combat_type}_effect"],
            jarvis_logged=True,
            lumina_integrated=True,
            pattern_id=f"combat_{combat_type}"
        )

        self.start_action_sequence(sequence)

        # JARVIS combat logging
        combat_action = CombatAction(
            action_type=combat_type,
            damage=0.0,
            visual_effect=f"{combat_type}_initiated",
            jarvis_logged=True
        )
        self.combat_actions.append(combat_action)
        self.jarvis_combat_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "combat_started",
            "combat_type": combat_type,
            "opponent": opponent
        })

        logger.info(f"⚔️  Combat started: {combat_type} vs {opponent}")

    def end_combat(self):
        """End combat action sequence"""
        if not self.combat_active:
            return

        self.combat_active = False
        duration = time.time() - self.combat_start_time if self.combat_start_time else 0.0

        # End combat sequence
        for seq in self.active_sequences[:]:
            if seq.state == VAState.COMBAT:
                self.end_action_sequence(seq.name)

        # JARVIS logging
        self.jarvis_combat_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "combat_ended",
            "duration": duration,
            "actions_count": len(self.combat_actions)
        })

        # Return to idle/wandering
        self.set_state(VAState.WANDERING, "Combat ended")

        logger.info(f"✅ Combat ended (duration: {duration:.1f}s)")

    def register_action_callback(self, action_name: str, callback: Callable):
        """
        Register callback for action

        Args:
            action_name: Name of action to register callback for
            callback: Callback function to call when action starts
        """
        if action_name not in self.action_callbacks:
            self.action_callbacks[action_name] = []
        self.action_callbacks[action_name].append(callback)

    def _log_to_jarvis(self, event_type: str, data: Dict[str, Any]):
        """Log event to JARVIS"""
        if not self.jarvis_integration:
            return

        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "va_type": self.va_type,
                "data": data
            }
            self.jarvis_decisions.append(log_entry)

            # Keep only last 100 decisions
            if len(self.jarvis_decisions) > 100:
                self.jarvis_decisions = self.jarvis_decisions[-100:]
        except Exception as e:
            logger.debug(f"JARVIS logging error: {e}")

    def update_arc_reactor_pulse(self):
        """Update arc reactor pulse animation"""
        self.arc_reactor_pulse = math.sin(time.time() * 2)  # 2 Hz pulse

    def get_arc_reactor_color(self) -> Tuple[int, int, int, int]:
        """
        Get arc reactor color based on current state

        Returns:
            RGBA color tuple
        """
        if self.current_state == VAState.LISTENING:
            return (255, 255, 0, 255)  # Yellow
        elif self.current_state == VAState.SPEAKING:
            return (0, 255, 255, 255)  # Cyan
        elif self.current_state == VAState.COMBAT:
            return (255, 0, 0, 255)  # Red
        else:
            return (0, 217, 255, 255)  # Cyan (default)

    def get_state_summary(self) -> Dict[str, Any]:
        """Get current state summary"""
        return {
            "current_state": self.current_state.value,
            "eye_expression": self.eye_expression.value,
            "mouth_expression": self.mouth_expression.value,
            "combat_active": self.combat_active,
            "active_sequences": [seq.name for seq in self.active_sequences],
            "jarvis_integrated": self.jarvis_integration is not None,
            "lumina_integrated": self.lumina_integrated,
            "combat_actions_count": len(self.combat_actions),
            "state_transitions_count": len(self.state_transitions)
        }


# Predefined action sequences extracted from Ace
ACE_ACTION_SEQUENCES = {
    "wandering": ActionSequence(
        name="wandering",
        description="Smooth wandering movement",
        state=VAState.WANDERING,
        duration=float('inf'),
        visual_effects=["smooth_movement"],
        jarvis_logged=False,
        lumina_integrated=False
    ),
    "listening": ActionSequence(
        name="listening",
        description="Voice recognition listening",
        state=VAState.LISTENING,
        duration=10.0,
        visual_effects=["arc_reactor_yellow", "eye_alert"],
        jarvis_logged=True,
        lumina_integrated=True,
        pattern_id="voice_listening"
    ),
    "speaking": ActionSequence(
        name="speaking",
        description="Text-to-speech output",
        state=VAState.SPEAKING,
        duration=5.0,
        visual_effects=["arc_reactor_cyan", "mouth_speaking", "eye_speaking"],
        jarvis_logged=True,
        lumina_integrated=True,
        pattern_id="voice_speaking"
    ),
    "processing": ActionSequence(
        name="processing",
        description="AI model processing",
        state=VAState.PROCESSING,
        duration=3.0,
        visual_effects=["eye_thinking", "arc_reactor_pulse"],
        jarvis_logged=True,
        lumina_integrated=True,
        pattern_id="ai_processing"
    ),
    "lightsaber_combat": ActionSequence(
        name="lightsaber_combat",
        description="Lightsaber combat with opponent",
        state=VAState.COMBAT,
        duration=12.0,
        visual_effects=["lightsaber_effect", "combat_animation", "health_bar"],
        jarvis_logged=True,
        lumina_integrated=True,
        pattern_id="combat_lightsaber"
    ),
    "syphon_enhancement": ActionSequence(
        name="syphon_enhancement",
        description="SYPHON intelligence extraction and enhancement",
        state=VAState.THINKING,
        duration=30.0,
        visual_effects=["eye_thinking", "intelligence_extraction"],
        jarvis_logged=True,
        lumina_integrated=True,
        pattern_id="syphon_enhancement"
    )
}


def create_action_framework(project_root: Path, va_type: str = "im") -> VAActionFramework:
    """
    Create and initialize action framework

    Args:
        project_root: Project root directory
        va_type: Virtual assistant type ("im" or "ac")

    Returns:
        Initialized VAActionFramework instance
    """
    return VAActionFramework(project_root, va_type)
