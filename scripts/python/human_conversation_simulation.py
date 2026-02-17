#!/usr/bin/env python3
"""
Human Conversation Simulation - Visual & Audio with 3D Avatars

Enables real, human-like conversations with visual and audio avatars (@synths),
3D adaptable for all persons, including those with physical/mental disabilities.

Tags: #HUMAN_CONVERSATION #SIMULATION #VISUAL #AUDIO #AVATAR #3D #ACCESSIBILITY
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("HumanConversationSim")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("HumanConversationSim")

try:
    from scripts.python.deep_thought_collective_system import (
        DeepThoughtCollectiveSystem, ConversationMode, AccessibilityMode
    )
    from scripts.python.synth_avatar_3d_accessibility import (
        SynthAvatar3DSystem, DisabilityType
    )
    SYSTEMS_AVAILABLE = True
except ImportError:
    SYSTEMS_AVAILABLE = False
    logger.warning("Required systems not available")


@dataclass
class ConversationFrame:
    """A frame in the conversation simulation"""
    timestamp: str
    speaker: str
    message: str
    visual_avatar_state: Dict[str, Any] = field(default_factory=dict)
    audio_state: Dict[str, Any] = field(default_factory=dict)
    accessibility_features: List[str] = field(default_factory=list)


@dataclass
class HumanConversationSession:
    """Human conversation simulation session"""
    session_id: str
    entity: str  # @DT, @DT2, @borg, or user
    user_profile: Dict[str, Any]
    conversation_mode: ConversationMode
    avatar_config: Dict[str, Any]
    frames: List[ConversationFrame] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())


class HumanConversationSimulation:
    """
    Human Conversation Simulation System

    Enables real, human-like conversations with:
    - Visual and audio avatars (@synths)
    - 3D adaptable for all persons
    - Accessibility for disabilities
    - Integration with @DT/@DT2/@borg
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.sessions_dir = self.project_root / "data" / "human_conversations"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Initialize systems
        self.dtc_system: Optional[DeepThoughtCollectiveSystem] = None
        self.avatar_system: Optional[SynthAvatar3DSystem] = None

        if SYSTEMS_AVAILABLE:
            try:
                self.dtc_system = DeepThoughtCollectiveSystem(project_root)
                self.avatar_system = SynthAvatar3DSystem(project_root)
            except Exception as e:
                logger.warning(f"System initialization failed: {e}")

        logger.info("="*80)
        logger.info("💬 HUMAN CONVERSATION SIMULATION")
        logger.info("="*80)
        logger.info("   Visual & Audio with 3D Avatars - Full Accessibility")
        logger.info("")

    def start_conversation(self, entity: str, user_message: str,
                          user_profile: Dict[str, Any]) -> HumanConversationSession:
        """Start human conversation simulation"""
        logger.info(f"💬 Starting conversation with {entity}...")

        # Determine accessibility mode
        disability_type = DisabilityType(user_profile.get("disability_type", "none"))
        accessibility_mode = self._map_disability_to_accessibility_mode(disability_type)

        # Create conversation mode
        conversation_mode = ConversationMode(
            visual_enabled=user_profile.get("visual_enabled", True),
            audio_enabled=user_profile.get("audio_enabled", True),
            text_enabled=user_profile.get("text_enabled", True),
            sign_language_enabled=user_profile.get("sign_language_enabled", False),
            braille_enabled=user_profile.get("braille_enabled", False),
            accessibility_mode=accessibility_mode,
            avatar_3d=True,
            real_time=True
        )

        # Create avatar
        avatar = None
        if self.avatar_system:
            avatar = self.avatar_system.create_accessible_avatar(user_profile)

        # Create conversation with entity
        entity_response = None
        if self.dtc_system:
            conversation_data = self.dtc_system.create_conversation_simulation(
                entity, user_message, conversation_mode
            )
            entity_response = conversation_data.get("entity_response", "")

        # Convert avatar to dict, handling enums
        avatar_config = {}
        if avatar:
            avatar_dict = asdict(avatar)
            # Convert DisabilityType enum to string
            if "accessibility" in avatar_dict and "disability_type" in avatar_dict["accessibility"]:
                avatar_dict["accessibility"]["disability_type"] = avatar.accessibility.disability_type.value
            avatar_config = avatar_dict

        # Create session
        session_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = HumanConversationSession(
            session_id=session_id,
            entity=entity,
            user_profile=user_profile,
            conversation_mode=conversation_mode,
            avatar_config=avatar_config
        )

        # Add frames
        user_frame = ConversationFrame(
            timestamp=datetime.now().isoformat(),
            speaker="user",
            message=user_message,
            accessibility_features=conversation_mode.accessibility_mode.value
        )
        session.frames.append(user_frame)

        if entity_response:
            entity_frame = ConversationFrame(
                timestamp=datetime.now().isoformat(),
                speaker=entity,
                message=entity_response,
                visual_avatar_state={
                    "entity": entity,
                    "animation": "speaking",
                    "accessibility": accessibility_mode.value
                },
                audio_state={
                    "synthesis": "natural",
                    "accessibility": accessibility_mode.value
                },
                accessibility_features=conversation_mode.accessibility_mode.value
            )
            session.frames.append(entity_frame)

        # Save session
        self._save_session(session)

        logger.info("✅ Conversation simulation started")
        logger.info("")

        return session

    def _map_disability_to_accessibility_mode(self, disability_type: DisabilityType) -> AccessibilityMode:
        """Map disability type to accessibility mode"""
        mapping = {
            DisabilityType.VISUAL_IMPAIRMENT: AccessibilityMode.VISUAL_IMPAIRMENT,
            DisabilityType.HEARING_IMPAIRMENT: AccessibilityMode.HEARING_IMPAIRMENT,
            DisabilityType.MOTOR_IMPAIRMENT: AccessibilityMode.MOTOR_IMPAIRMENT,
            DisabilityType.COGNITIVE_IMPAIRMENT: AccessibilityMode.COGNITIVE_IMPAIRMENT,
            DisabilityType.MULTIPLE_IMPAIRMENTS: AccessibilityMode.FULL_ACCESSIBILITY,
            DisabilityType.NONE: AccessibilityMode.STANDARD
        }
        return mapping.get(disability_type, AccessibilityMode.STANDARD)

    def _save_session(self, session: HumanConversationSession):
        try:
            """Save conversation session"""
            session_file = self.sessions_dir / f"{session.session_id}.json"

            # Convert enums to strings for JSON serialization
            conv_mode_dict = asdict(session.conversation_mode)
            conv_mode_dict["accessibility_mode"] = session.conversation_mode.accessibility_mode.value

            data = {
                "session_id": session.session_id,
                "entity": session.entity,
                "user_profile": session.user_profile,
                "conversation_mode": conv_mode_dict,
                "avatar_config": session.avatar_config,
                "frames": [asdict(frame) for frame in session.frames],
                "started_at": session.started_at
            }

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)


        except Exception as e:
            self.logger.error(f"Error in _save_session: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution - Example conversation"""
        import argparse

        parser = argparse.ArgumentParser(description="Human Conversation Simulation")
        parser.add_argument("--entity", default="@DT", help="Entity to talk to (@DT, @DT2, @borg)")
        parser.add_argument("--message", help="Message to send")
        parser.add_argument("--user-profile", help="User profile JSON file")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        simulation = HumanConversationSimulation(project_root)

        # Default user profile
        user_profile = {
            "name": "User",
            "user_id": "user_001",
            "disability_type": "none",
            "visual_enabled": True,
            "audio_enabled": True,
            "text_enabled": True
        }

        if args.user_profile:
            with open(args.user_profile, 'r', encoding='utf-8') as f:
                user_profile = json.load(f)

        if args.message:
            session = simulation.start_conversation(args.entity, args.message, user_profile)
            if session.frames:
                print(f"\n[{session.frames[-1].speaker}]: {session.frames[-1].message}\n")
            print(f"Session ID: {session.session_id}")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())