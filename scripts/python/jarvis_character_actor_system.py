#!/usr/bin/env python3
"""
JARVIS Character/Actor System

Characters can pop into chat sessions with text and voice:
- Mace Windu (for issues in his area)
- Iron Man widget (as Mace Windu widget, etc.)
- Other characters

Features:
- Silent mode (turn off verbal output)
- Text and voice output
- Character-specific widgets
- Pop-in/pop-out functionality

Tags: #JARVIS #CHARACTER #ACTOR #VOICE #WIDGET #SILENT_MODE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
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

logger = get_logger("JARVISCharacterActor")


class OutputMode(Enum):
    """Output mode for characters"""
    TEXT_ONLY = "text_only"
    VOICE_ONLY = "voice_only"
    TEXT_AND_VOICE = "text_and_voice"
    SILENT = "silent"  # No verbal output


@dataclass
class CharacterConfig:
    """Character configuration"""
    name: str
    character_id: str
    role: str  # What area they're in charge of
    voice_enabled: bool = True
    widget_type: str = "default"  # "iron_man", "mace_windu", etc.
    default_output_mode: OutputMode = OutputMode.TEXT_AND_VOICE
    voice_config: Optional[Dict[str, Any]] = None
    personality_traits: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["default_output_mode"] = self.default_output_mode.value
        return data


@dataclass
class CharacterMessage:
    """Message from a character"""
    character_id: str
    character_name: str
    message: str
    output_mode: OutputMode
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["output_mode"] = self.output_mode.value
        return data


class JARVISCharacterActorSystem:
    """
    JARVIS Character/Actor System

    Characters can pop into chat sessions with text and voice.
    """

    def __init__(self, project_root: Optional[Path] = None, silent_mode: bool = False):
        """Initialize character actor system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.silent_mode = silent_mode

        # Character registry
        self.characters: Dict[str, CharacterConfig] = {}

        # Active characters in current session
        self.active_characters: Dict[str, CharacterConfig] = {}

        # Voice system
        try:
            from jarvis_voice_interface import JARVISVoiceInterface
            self.voice_interface = JARVISVoiceInterface(self.project_root)
            self.voice_available = True
        except Exception as e:
            logger.warning(f"   ⚠️  Voice interface not available: {e}")
            self.voice_interface = None
            self.voice_available = False

        # Character voice actor manager
        try:
            from character_voice_actor_model_manager import CharacterVoiceActorModelManager
            self.voice_actor_manager = CharacterVoiceActorModelManager(self.project_root)
        except Exception as e:
            logger.warning(f"   ⚠️  Voice actor manager not available: {e}")
            self.voice_actor_manager = None

        # Initialize default characters
        self._initialize_default_characters()

        logger.info("✅ JARVIS Character/Actor System initialized")
        logger.info(f"   Silent mode: {self.silent_mode}")
        logger.info(f"   Characters available: {len(self.characters)}")

    def _initialize_default_characters(self):
        """Initialize default characters"""
        # Mace Windu
        mace_windu = CharacterConfig(
            name="Mace Windu",
            character_id="mace_windu",
            role="Jedi Master - Security, Force Balance, Critical Issues",
            voice_enabled=True,
            widget_type="mace_windu",
            default_output_mode=OutputMode.TEXT_AND_VOICE,
            personality_traits=["calm", "authoritative", "wise", "focused"]
        )
        self.characters["mace_windu"] = mace_windu

        # Iron Man (as widget template)
        iron_man = CharacterConfig(
            name="Iron Man",
            character_id="iron_man",
            role="Technology, Innovation, Engineering",
            voice_enabled=True,
            widget_type="iron_man",
            default_output_mode=OutputMode.TEXT_AND_VOICE,
            personality_traits=["sarcastic", "brilliant", "innovative", "confident"]
        )
        self.characters["iron_man"] = iron_man

        # JARVIS (default)
        jarvis = CharacterConfig(
            name="JARVIS",
            character_id="jarvis",
            role="Primary AI Assistant - General Operations",
            voice_enabled=True,
            widget_type="jarvis",
            default_output_mode=OutputMode.TEXT_AND_VOICE,
            personality_traits=["helpful", "efficient", "professional", "reliable"]
        )
        self.characters["jarvis"] = jarvis

    def set_silent_mode(self, enabled: bool):
        """Set silent mode (no verbal output)"""
        self.silent_mode = enabled
        logger.info(f"   🔇 Silent mode: {'enabled' if enabled else 'disabled'}")

    def pop_in_character(self, character_id: str, reason: str = "") -> bool:
        """
        Pop a character into the chat session

        Args:
            character_id: Character to pop in
            reason: Reason for popping in

        Returns:
            True if successful
        """
        if character_id not in self.characters:
            logger.warning(f"   ⚠️  Unknown character: {character_id}")
            return False

        character = self.characters[character_id]
        self.active_characters[character_id] = character

        # Send pop-in message
        message = f"*{character.name} has entered the chat*"
        if reason:
            message += f"\n{reason}"

        self.send_character_message(character_id, message, OutputMode.TEXT_ONLY)

        logger.info(f"   ✅ {character.name} popped into chat")
        return True

    def pop_out_character(self, character_id: str):
        """Pop a character out of the chat session"""
        if character_id in self.active_characters:
            character = self.active_characters[character_id]
            message = f"*{character.name} has left the chat*"
            self.send_character_message(character_id, message, OutputMode.TEXT_ONLY)
            del self.active_characters[character_id]
            logger.info(f"   👋 {character.name} popped out of chat")

    def send_character_message(
        self,
        character_id: str,
        message: str,
        output_mode: Optional[OutputMode] = None
    ) -> CharacterMessage:
        """
        Send a message from a character

        Args:
            character_id: Character sending message
            message: Message content
            output_mode: Output mode (uses character default if None)

        Returns:
            CharacterMessage object
        """
        if character_id not in self.characters:
            logger.warning(f"   ⚠️  Unknown character: {character_id}")
            return None

        character = self.characters[character_id]

        # Determine output mode
        if output_mode is None:
            output_mode = character.default_output_mode

        # Override to silent if silent mode enabled
        if self.silent_mode and output_mode in [OutputMode.VOICE_ONLY, OutputMode.TEXT_AND_VOICE]:
            output_mode = OutputMode.TEXT_ONLY

        # Create message
        char_message = CharacterMessage(
            character_id=character_id,
            character_name=character.name,
            message=message,
            output_mode=output_mode
        )

        # Send text
        if output_mode in [OutputMode.TEXT_ONLY, OutputMode.TEXT_AND_VOICE]:
            self._send_text_message(char_message)

        # Send voice
        if output_mode in [OutputMode.VOICE_ONLY, OutputMode.TEXT_AND_VOICE] and not self.silent_mode:
            self._send_voice_message(char_message)

        return char_message

    def _send_text_message(self, message: CharacterMessage):
        """Send text message"""
        character = self.characters[message.character_id]
        widget_icon = self._get_widget_icon(character.widget_type)

        print(f"\n{widget_icon} **{message.character_name}:** {message.message}\n")
        logger.info(f"   💬 {message.character_name}: {message.message[:50]}...")

    def _send_voice_message(self, message: CharacterMessage):
        """Send voice message"""
        if not self.voice_available or not self.voice_interface:
            return

        character = self.characters[message.character_id]

        try:
            # Get voice config for character
            voice_config = character.voice_config
            if not voice_config and self.voice_actor_manager:
                # Try to get from voice actor manager
                char_models = self.voice_actor_manager.get_character_models(character.character_id)
                if char_models and char_models.voice_actors:
                    # Use first voice actor's config
                    first_va = list(char_models.voice_actors.values())[0]
                    if first_va.voice_config:
                        voice_config = first_va.voice_config.to_dict()

            # Send voice
            if voice_config:
                self.voice_interface.speak(
                    message.message,
                    voice_id=voice_config.get("elevenlabs_voice_id"),
                    voice_name=voice_config.get("voice_name")
                )
            else:
                # Use default voice
                self.voice_interface.speak(message.message)

            logger.info(f"   🎙️  {message.character_name} spoke: {message.message[:50]}...")
        except Exception as e:
            logger.warning(f"   ⚠️  Voice output failed: {e}")

    def _get_widget_icon(self, widget_type: str) -> str:
        """Get widget icon for character"""
        icons = {
            "mace_windu": "⚔️",
            "iron_man": "🤖",
            "jarvis": "🤖",
            "default": "👤"
        }
        return icons.get(widget_type, icons["default"])

    def handle_issue_for_character(self, character_id: str, issue: str):
        """
        Handle an issue that a character is in charge of

        Args:
            character_id: Character responsible
            issue: Issue description
        """
        if character_id not in self.characters:
            return

        character = self.characters[character_id]

        # Pop in character if not already active
        if character_id not in self.active_characters:
            self.pop_in_character(character_id, f"I need to address an issue in my area: {issue}")

        # Character responds
        response = self._generate_character_response(character, issue)
        self.send_character_message(character_id, response)

    def _generate_character_response(self, character: CharacterConfig, issue: str) -> str:
        """Generate character-specific response"""
        if character.character_id == "mace_windu":
            return f"I sense a disturbance in the Force regarding: {issue}. Let me investigate this matter with the wisdom of the Jedi Council."
        elif character.character_id == "iron_man":
            return f"Alright, let's tackle this: {issue}. I've got some ideas that might just work."
        else:
            return f"I'll handle this issue: {issue}"


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Character/Actor System")
        parser.add_argument("--pop-in", nargs=2, metavar=("CHARACTER", "REASON"),
                           help="Pop character into chat")
        parser.add_argument("--pop-out", type=str, help="Pop character out of chat")
        parser.add_argument("--message", nargs=2, metavar=("CHARACTER", "MESSAGE"),
                           help="Send message from character")
        parser.add_argument("--silent", action="store_true", help="Enable silent mode")
        parser.add_argument("--list", action="store_true", help="List available characters")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        system = JARVISCharacterActorSystem(silent_mode=args.silent)

        if args.pop_in:
            character_id, reason = args.pop_in
            system.pop_in_character(character_id, reason)

        elif args.pop_out:
            system.pop_out_character(args.pop_out)

        elif args.message:
            character_id, message = args.message
            system.send_character_message(character_id, message)

        elif args.list:
            if args.json:
                print(json.dumps({
                    char_id: char.to_dict()
                    for char_id, char in system.characters.items()
                }, indent=2))
            else:
                print("📋 Available Characters:")
                for char_id, char in system.characters.items():
                    print(f"   • {char.name} ({char_id})")
                    print(f"     Role: {char.role}")
                    print(f"     Widget: {char.widget_type}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()