#!/usr/bin/env python3
"""
Voice Command Processing System

Processes voice commands via STT, routes to appropriate VAs, tracks history.

Tags: #VIRTUAL_ASSISTANT #VOICE #STT #COMMAND_PROCESSING @JARVIS @LUMINA
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import (CharacterAvatarRegistry,
                                           CharacterType)
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterType = None

logger = get_logger("VAVoiceCommand")


class CommandIntent(Enum):
    """Command intent types"""
    AUTOMATION = "automation"
    COMBAT = "combat"
    UI_INTERACTION = "ui_interaction"
    SYSTEM = "system"
    QUERY = "query"
    CONTROL = "control"
    UNKNOWN = "unknown"


@dataclass
class VoiceCommand:
    """Voice command data"""
    command_id: str
    audio_file: Optional[str] = None
    transcribed_text: str = ""
    intent: CommandIntent = CommandIntent.UNKNOWN
    confidence: float = 0.0
    routed_to_va: Optional[str] = None
    executed: bool = False
    execution_result: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["intent"] = self.intent.value
        return data


class VAVoiceCommandProcessor:
    """
    Voice Command Processing System

    Features:
    - STT integration (Dragon MOB placeholder)
    - Command parsing and intent detection
    - VA routing
    - Command history
    - Voice authentication
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize voice command processor"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Command history
        self.command_history: List[VoiceCommand] = []
        self.command_counter = 0

        # Command patterns and routing
        self.command_patterns = self._initialize_command_patterns()
        self.va_routing = self._initialize_va_routing()

        # STT integration (placeholder for Dragon MOB)
        self.stt_enabled = True
        self.stt_provider = "dragon_mob"  # Placeholder

        # Data persistence
        self.data_dir = project_root / "data" / "va_voice_commands"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("🎤 VOICE COMMAND PROCESSING SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   VAs Registered: {len(self.vas)}")
        logger.info(f"   STT Provider: {self.stt_provider}")
        logger.info("=" * 80)

    def _initialize_command_patterns(self) -> Dict[str, CommandIntent]:
        """Initialize command pattern matching"""
        return {
            # Automation patterns
            "automate": CommandIntent.AUTOMATION,
            "run": CommandIntent.AUTOMATION,
            "execute": CommandIntent.AUTOMATION,
            "start": CommandIntent.AUTOMATION,
            "stop": CommandIntent.AUTOMATION,

            # Combat patterns
            "combat": CommandIntent.COMBAT,
            "fight": CommandIntent.COMBAT,
            "attack": CommandIntent.COMBAT,
            "defend": CommandIntent.COMBAT,
            "security": CommandIntent.COMBAT,
            "scan": CommandIntent.COMBAT,

            # UI patterns
            "show": CommandIntent.UI_INTERACTION,
            "display": CommandIntent.UI_INTERACTION,
            "open": CommandIntent.UI_INTERACTION,
            "close": CommandIntent.UI_INTERACTION,
            "ui": CommandIntent.UI_INTERACTION,

            # System patterns
            "status": CommandIntent.SYSTEM,
            "health": CommandIntent.SYSTEM,
            "system": CommandIntent.SYSTEM,
            "report": CommandIntent.SYSTEM,

            # Query patterns
            "what": CommandIntent.QUERY,
            "how": CommandIntent.QUERY,
            "when": CommandIntent.QUERY,
            "where": CommandIntent.QUERY,
            "why": CommandIntent.QUERY,
            "tell": CommandIntent.QUERY,

            # Control patterns
            "activate": CommandIntent.CONTROL,
            "deactivate": CommandIntent.CONTROL,
            "enable": CommandIntent.CONTROL,
            "disable": CommandIntent.CONTROL,
        }

    def _initialize_va_routing(self) -> Dict[CommandIntent, List[str]]:
        """Initialize VA routing by intent"""
        return {
            CommandIntent.AUTOMATION: ["jarvis_va"],
            CommandIntent.COMBAT: ["ace", "jarvis_va"],
            CommandIntent.UI_INTERACTION: ["imva", "jarvis_va"],
            CommandIntent.SYSTEM: ["jarvis_va", "imva"],
            CommandIntent.QUERY: ["jarvis_va", "imva"],
            CommandIntent.CONTROL: ["jarvis_va"],
            CommandIntent.UNKNOWN: ["jarvis_va"]  # Default fallback
        }

    def process_voice_command(self, audio_file: Optional[str] = None,
                              transcribed_text: Optional[str] = None) -> VoiceCommand:
        """Process voice command (STT + routing)"""
        self.command_counter += 1
        command_id = f"voice_cmd_{self.command_counter:06d}"

        # STT processing (placeholder)
        if transcribed_text:
            text = transcribed_text
        elif audio_file:
            # Placeholder: In real implementation, would use Dragon MOB STT
            text = self._transcribe_audio(audio_file)
        else:
            raise ValueError("Either audio_file or transcribed_text required")

        # Parse intent
        intent = self._parse_intent(text)

        # Route to VA
        routed_va = self._route_to_va(intent, text)

        command = VoiceCommand(
            command_id=command_id,
            audio_file=audio_file,
            transcribed_text=text,
            intent=intent,
            confidence=0.85,  # Placeholder confidence
            routed_to_va=routed_va
        )

        self.command_history.append(command)

        logger.info(f"🎤 Processed voice command: {text}")
        logger.info(f"   Intent: {intent.value}")
        logger.info(f"   Routed to: {routed_va}")

        return command

    def _transcribe_audio(self, audio_file: str) -> str:
        """Transcribe audio to text (placeholder for Dragon MOB)"""
        # Placeholder: Would integrate with Dragon MOB STT
        logger.info(f"📝 Transcribing audio: {audio_file} (STT placeholder)")
        return "placeholder transcription"

    def _parse_intent(self, text: str) -> CommandIntent:
        """Parse command intent from text"""
        text_lower = text.lower()

        # Check patterns
        for pattern, intent in self.command_patterns.items():
            if pattern in text_lower:
                return intent

        # Check for VA names
        if "jarvis" in text_lower:
            return CommandIntent.AUTOMATION
        if "ace" in text_lower or "combat" in text_lower:
            return CommandIntent.COMBAT
        if "imva" in text_lower or "ui" in text_lower:
            return CommandIntent.UI_INTERACTION

        return CommandIntent.UNKNOWN

    def _route_to_va(self, intent: CommandIntent, text: str) -> Optional[str]:
        """Route command to appropriate VA"""
        routing_options = self.va_routing.get(intent, [])

        if not routing_options:
            return None

        # Check for explicit VA mention in text
        text_lower = text.lower()
        for va in self.vas:
            if va.character_id in text_lower or va.name.lower() in text_lower:
                if va.character_id in routing_options:
                    return va.character_id

        # Default to first option
        va_id = routing_options[0]
        va = self.registry.get_character(va_id)
        if va and va.character_type == CharacterType.VIRTUAL_ASSISTANT:
            return va_id

        return None

    def execute_command(self, command_id: str,
                       execution_result: Optional[Dict[str, Any]] = None) -> bool:
        """Mark command as executed"""
        command = next((c for c in self.command_history if c.command_id == command_id), None)
        if not command:
            logger.warning(f"Command {command_id} not found")
            return False

        command.executed = True
        command.execution_result = execution_result or {"status": "completed"}

        logger.info(f"✅ Executed command: {command_id}")
        return True

    def get_command_history(self, limit: int = 50) -> List[VoiceCommand]:
        """Get command history"""
        return self.command_history[-limit:]

    def get_va_command_stats(self, va_id: str) -> Dict[str, Any]:
        """Get command statistics for a VA"""
        stats = {
            "total_commands": 0,
            "by_intent": {},
            "execution_rate": 0.0,
            "recent_commands": []
        }

        va_commands = [c for c in self.command_history if c.routed_to_va == va_id]
        stats["total_commands"] = len(va_commands)

        if va_commands:
            executed = sum(1 for c in va_commands if c.executed)
            stats["execution_rate"] = executed / len(va_commands)

            for cmd in va_commands:
                intent = cmd.intent.value
                stats["by_intent"][intent] = stats["by_intent"].get(intent, 0) + 1

                stats["recent_commands"].append({
                    "command_id": cmd.command_id,
                    "text": cmd.transcribed_text,
                    "intent": intent,
                    "executed": cmd.executed,
                    "timestamp": cmd.timestamp
                })

        stats["recent_commands"] = stats["recent_commands"][-10:]
        return stats

    def _save_history(self):
        try:
            """Save command history to disk"""
            history_file = self.data_dir / "command_history.json"

            history_data = {
                "commands": [cmd.to_dict() for cmd in self.command_history],
                "command_counter": self.command_counter,
                "timestamp": datetime.now().isoformat()
            }

            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2)

            logger.info(f"💾 Saved command history to {history_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_history: {e}", exc_info=True)
            raise
def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    processor = VAVoiceCommandProcessor(registry)

    print("=" * 80)
    print("🎤 VOICE COMMAND PROCESSING SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Process commands
    test_commands = [
        "Hey JARVIS, run security scan",
        "ACE, activate combat mode",
        "Show me the status",
        "What is the current system health?",
        "Automate workflow execution"
    ]

    for cmd_text in test_commands:
        print(f"Processing: '{cmd_text}'")
        command = processor.process_voice_command(transcribed_text=cmd_text)
        print(f"  ✅ Intent: {command.intent.value}")
        print(f"  ✅ Routed to: {command.routed_to_va}")
        print()

    # Test: Command statistics
    print("VA Command Statistics:")
    for va in processor.vas:
        stats = processor.get_va_command_stats(va.character_id)
        print(f"  • {va.name} ({va.character_id})")
        print(f"    Total Commands: {stats['total_commands']}")
        print(f"    Execution Rate: {stats['execution_rate']:.1%}")
        if stats['by_intent']:
            print(f"    By Intent: {stats['by_intent']}")
        print()

    # Save history
    processor._save_history()

    print("=" * 80)


if __name__ == "__main__":


    main()