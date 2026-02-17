#!/usr/bin/env python3
"""
VOICE SHORTCUT 37 - Voice Commands to Keyboard Shortcuts Bridge

Voice commands that trigger each and every keyboard shortcut.
Use short tagging to define meta qualities and tagging for patterns.
Define patterns in code with clearly defined decisioning.

Prime number: 37 (Voice bridge number - connects voice to shortcuts)

Tags: #VOICE-SHORTCUT #VOICE-COMMANDS #SHORT-TAGS #PATTERNS #DECISIONING @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from shortcut_mapper_31_intuitive import SHORTCUTMAPPER31, KeyboardShortcut
    from short_tag_mantra_applicator import ShortTagMantraApplicator
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("VoiceShortcut37")
ts_logger = get_timestamp_logger()


class VoicePatternType(Enum):
    """Voice pattern type"""
    EXACT = "exact"  # Exact match
    FUZZY = "fuzzy"  # Fuzzy match (handles speech impediment)
    PATTERN = "pattern"  # Pattern-based match
    TAG_BASED = "tag_based"  # Tag-based match


@dataclass
class ShortTag:
    """Short tag for meta qualities and tagging"""
    tag: str
    category: str  # "meta", "quality", "pattern", "decisioning"
    value: Any
    description: str = ""


@dataclass
class VoiceCommand:
    """Voice command that triggers keyboard shortcut"""
    command_id: str
    voice_phrase: str
    shortcut_id: str
    pattern_type: VoicePatternType
    short_tags: List[ShortTag] = field(default_factory=list)
    decisioning_logic: Dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.8
    fuzzy_match: bool = True  # Handle speech impediment


@dataclass
class VoiceShortcutMapping:
    """Mapping between voice command and keyboard shortcut"""
    mapping_id: str
    voice_command: VoiceCommand
    keyboard_shortcut: KeyboardShortcut
    application: str
    meta_qualities: Dict[str, Any] = field(default_factory=dict)
    pattern_definition: Dict[str, Any] = field(default_factory=dict)
    decisioning_rules: List[Dict[str, Any]] = field(default_factory=list)


class VOICESHORTCUT37:
    """
    VOICE SHORTCUT 37 - Voice Commands to Keyboard Shortcuts Bridge

    Voice commands that trigger each and every keyboard shortcut.
    Use short tagging to define meta qualities and tagging for patterns.
    Define patterns in code with clearly defined decisioning.

    Prime number: 37 (Voice bridge number - connects voice to shortcuts)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize VOICE SHORTCUT 37"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "voice_shortcut_37"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.shortcut_mapper = SHORTCUTMAPPER31(project_root=project_root)
        self.mantra = ShortTagMantraApplicator(project_root=project_root)

        self.voice_commands: Dict[str, VoiceCommand] = {}
        self.mappings: Dict[str, VoiceShortcutMapping] = {}

        logger.info("🎤 VOICE SHORTCUT 37 initialized")
        logger.info("   Voice commands to keyboard shortcuts")
        logger.info("   Short tagging for meta qualities")
        logger.info("   Patterns in code with decisioning")
        logger.info("   Prime number: 37 (Voice bridge number)")

    def create_voice_command(self, voice_phrase: str, shortcut_id: str,
                            pattern_type: VoicePatternType = VoicePatternType.FUZZY,
                            short_tags: Optional[List[ShortTag]] = None,
                            decisioning_logic: Optional[Dict[str, Any]] = None) -> VoiceCommand:
        """Create a voice command with short tags and decisioning"""
        command_id = f"voice_cmd_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Default short tags
        if short_tags is None:
            short_tags = [
                ShortTag(tag="#voice", category="meta", value=True, description="Voice command"),
                ShortTag(tag="#shortcut", category="meta", value=True, description="Keyboard shortcut trigger"),
            ]

        # Default decisioning logic
        if decisioning_logic is None:
            decisioning_logic = {
                "pattern_type": pattern_type.value,
                "fuzzy_match": True,
                "confidence_threshold": 0.8,
                "speech_impediment_handling": True,
            }

        command = VoiceCommand(
            command_id=command_id,
            voice_phrase=voice_phrase,
            shortcut_id=shortcut_id,
            pattern_type=pattern_type,
            short_tags=short_tags or [],
            decisioning_logic=decisioning_logic,
            fuzzy_match=True,  # Handle speech impediment
        )

        self.voice_commands[command_id] = command

        logger.info(f"🎤 Voice command created: {command_id}")
        logger.info(f"   Phrase: {voice_phrase}")
        logger.info(f"   Shortcut: {shortcut_id}")
        logger.info(f"   Pattern type: {pattern_type.value}")
        logger.info(f"   Short tags: {len(command.short_tags)}")

        # Save command
        self._save_voice_command(command)

        return command

    def map_voice_to_shortcut(self, voice_phrase: str, shortcut_id: str,
                             application: str, meta_qualities: Optional[Dict[str, Any]] = None,
                             pattern_definition: Optional[Dict[str, Any]] = None) -> VoiceShortcutMapping:
        """Map voice command to keyboard shortcut with short tags and patterns"""
        # Get keyboard shortcut
        shortcut = self.shortcut_mapper.shortcuts.get(shortcut_id)
        if shortcut is None:
            raise ValueError(f"Shortcut not found: {shortcut_id}")

        # Create voice command
        voice_cmd = self.create_voice_command(voice_phrase, shortcut_id)

        # Define short tags for meta qualities
        short_tags = []

        # Application tag
        short_tags.append(ShortTag(
            tag=f"#{application.lower().replace(' ', '_')}",
            category="meta",
            value=application,
            description=f"Application: {application}",
        ))

        # Action tag
        short_tags.append(ShortTag(
            tag=f"#{shortcut.action.lower().replace(' ', '_')}",
            category="pattern",
            value=shortcut.action,
            description=f"Action: {shortcut.action}",
        ))

        # Quality tags
        if meta_qualities:
            for key, value in meta_qualities.items():
                short_tags.append(ShortTag(
                    tag=f"#{key}",
                    category="quality",
                    value=value,
                    description=f"Meta quality: {key}",
                ))

        voice_cmd.short_tags = short_tags

        # Define pattern in code
        if pattern_definition is None:
            pattern_definition = {
                "voice_pattern": voice_phrase,
                "fuzzy_variants": self._generate_fuzzy_variants(voice_phrase),
                "decisioning_rules": self._create_decisioning_rules(voice_phrase, shortcut),
            }

        # Create decisioning rules
        decisioning_rules = self._create_decisioning_rules(voice_phrase, shortcut)

        mapping = VoiceShortcutMapping(
            mapping_id=f"mapping_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            voice_command=voice_cmd,
            keyboard_shortcut=shortcut,
            application=application,
            meta_qualities=meta_qualities or {},
            pattern_definition=pattern_definition,
            decisioning_rules=decisioning_rules,
        )

        self.mappings[mapping.mapping_id] = mapping

        logger.info(f"🔗 Voice-to-shortcut mapping created: {mapping.mapping_id}")
        logger.info(f"   Voice: {voice_phrase}")
        logger.info(f"   Shortcut: {shortcut.key_combination}")
        logger.info(f"   Application: {application}")
        logger.info(f"   Short tags: {len(short_tags)}")
        logger.info(f"   Decisioning rules: {len(decisioning_rules)}")

        # Save mapping
        self._save_mapping(mapping)

        return mapping

    def _generate_fuzzy_variants(self, voice_phrase: str) -> List[str]:
        """Generate fuzzy variants for speech impediment handling"""
        variants = [voice_phrase]

        # Common speech impediment variants
        # "HEY CODE" -> "HEY COAT", "HEY COLD", etc.
        if "code" in voice_phrase.lower():
            variants.append(voice_phrase.lower().replace("code", "coat"))
            variants.append(voice_phrase.lower().replace("code", "cold"))
            variants.append(voice_phrase.lower().replace("code", "cope"))

        # Add phonetic variants
        # This would use phonetic matching in practice

        return variants

    def _create_decisioning_rules(self, voice_phrase: str, shortcut: KeyboardShortcut) -> List[Dict[str, Any]]:
        """Create decisioning rules in code - clearly defined"""
        rules = []

        # Rule 1: Exact match
        rules.append({
            "rule_id": "exact_match",
            "condition": f"voice_phrase == '{voice_phrase}'",
            "action": f"trigger_shortcut('{shortcut.shortcut_id}')",
            "priority": 10,
            "description": "Exact voice phrase match",
        })

        # Rule 2: Fuzzy match (speech impediment)
        rules.append({
            "rule_id": "fuzzy_match",
            "condition": f"fuzzy_match(voice_phrase, '{voice_phrase}', threshold=0.8)",
            "action": f"trigger_shortcut('{shortcut.shortcut_id}')",
            "priority": 8,
            "description": "Fuzzy match for speech impediment",
        })

        # Rule 3: Pattern match
        rules.append({
            "rule_id": "pattern_match",
            "condition": f"pattern_match(voice_phrase, '{voice_phrase}')",
            "action": f"trigger_shortcut('{shortcut.shortcut_id}')",
            "priority": 6,
            "description": "Pattern-based match",
        })

        # Rule 4: Tag-based match
        rules.append({
            "rule_id": "tag_match",
            "condition": f"has_tag(voice_phrase, '#{shortcut.action.lower().replace(' ', '_')}')",
            "action": f"trigger_shortcut('{shortcut.shortcut_id}')",
            "priority": 4,
            "description": "Tag-based match",
        })

        return rules

    def map_all_shortcuts(self, application: str) -> List[VoiceShortcutMapping]:
        """Map all shortcuts for an application to voice commands"""
        app_mapping = self.shortcut_mapper.get_application_mapping(application)

        mappings = []

        for shortcut in app_mapping.shortcuts:
            # Generate voice phrase from action
            voice_phrase = self._action_to_voice_phrase(shortcut.action)

            # Create mapping
            mapping = self.map_voice_to_shortcut(
                voice_phrase=voice_phrase,
                shortcut_id=shortcut.shortcut_id,
                application=application,
                meta_qualities={
                    "category": shortcut.category.value,
                    "type": shortcut.shortcut_type.value,
                },
            )

            mappings.append(mapping)

        logger.info(f"🔗 Mapped {len(mappings)} shortcuts to voice commands for {application}")

        return mappings

    def _action_to_voice_phrase(self, action: str) -> str:
        """Convert action to voice phrase"""
        # Simple conversion - in practice would be more sophisticated
        voice_phrase = action.lower()

        # Common mappings
        replacements = {
            "open": "open",
            "close": "close",
            "save": "save",
            "copy": "copy",
            "paste": "paste",
            "cut": "cut",
            "undo": "undo",
            "redo": "redo",
            "find": "find",
            "replace": "replace",
            "go to": "go to",
            "show": "show",
            "toggle": "toggle",
        }

        for key, value in replacements.items():
            if key in voice_phrase:
                voice_phrase = voice_phrase.replace(key, value)

        return voice_phrase

    def get_voice_command_for_shortcut(self, shortcut_id: str) -> Optional[VoiceCommand]:
        """Get voice command for a shortcut"""
        for mapping in self.mappings.values():
            if mapping.voice_command.shortcut_id == shortcut_id:
                return mapping.voice_command
        return None

    def get_decisioning_code(self, mapping_id: str) -> str:
        """Get decisioning code for a mapping"""
        mapping = self.mappings.get(mapping_id)
        if mapping is None:
            raise ValueError(f"Mapping not found: {mapping_id}")

        code = f"""
# Decisioning code for {mapping.voice_command.voice_phrase}
# Application: {mapping.application}
# Shortcut: {mapping.keyboard_shortcut.key_combination}

def handle_voice_command(voice_phrase: str) -> bool:
    \"\"\"Handle voice command with clearly defined decisioning\"\"\"

    # Rule 1: Exact match
    if voice_phrase == '{mapping.voice_command.voice_phrase}':
        trigger_shortcut('{mapping.keyboard_shortcut.shortcut_id}')
        return True

    # Rule 2: Fuzzy match (speech impediment)
    if fuzzy_match(voice_phrase, '{mapping.voice_command.voice_phrase}', threshold=0.8):
        trigger_shortcut('{mapping.keyboard_shortcut.shortcut_id}')
        return True

    # Rule 3: Pattern match
    if pattern_match(voice_phrase, '{mapping.voice_command.voice_phrase}'):
        trigger_shortcut('{mapping.keyboard_shortcut.shortcut_id}')
        return True

    # Rule 4: Tag-based match
    if has_tag(voice_phrase, '#{mapping.keyboard_shortcut.action.lower().replace(' ', '_')}'):
        trigger_shortcut('{mapping.keyboard_shortcut.shortcut_id}')
        return True

    return False
"""

        return code

    def _save_voice_command(self, command: VoiceCommand):
        try:
            """Save voice command"""
            file_path = self.data_dir / f"{command.command_id}.json"
            data = {
                "command_id": command.command_id,
                "voice_phrase": command.voice_phrase,
                "shortcut_id": command.shortcut_id,
                "pattern_type": command.pattern_type.value,
                "short_tags": [
                    {
                        "tag": tag.tag,
                        "category": tag.category,
                        "value": tag.value,
                        "description": tag.description,
                    }
                    for tag in command.short_tags
                ],
                "decisioning_logic": command.decisioning_logic,
                "confidence_threshold": command.confidence_threshold,
                "fuzzy_match": command.fuzzy_match,
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_voice_command: {e}", exc_info=True)
            raise
    def _save_mapping(self, mapping: VoiceShortcutMapping):
        try:
            """Save mapping"""
            file_path = self.data_dir / f"{mapping.mapping_id}.json"
            data = {
                "mapping_id": mapping.mapping_id,
                "voice_command_id": mapping.voice_command.command_id,
                "shortcut_id": mapping.keyboard_shortcut.shortcut_id,
                "application": mapping.application,
                "meta_qualities": mapping.meta_qualities,
                "pattern_definition": mapping.pattern_definition,
                "decisioning_rules": mapping.decisioning_rules,
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)


        except Exception as e:
            self.logger.error(f"Error in _save_mapping: {e}", exc_info=True)
            raise
def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="VOICE SHORTCUT 37 - Voice Commands to Keyboard Shortcuts")
    parser.add_argument("--map", nargs=3, metavar=("VOICE_PHRASE", "SHORTCUT_ID", "APP"), help="Map voice to shortcut")
    parser.add_argument("--map-all", type=str, metavar="APPLICATION", help="Map all shortcuts for application")
    parser.add_argument("--decisioning", type=str, metavar="MAPPING_ID", help="Get decisioning code")
    parser.add_argument("--status", action="store_true", help="Show status")

    args = parser.parse_args()

    print("="*80)
    print("🎤 VOICE SHORTCUT 37 - VOICE COMMANDS TO KEYBOARD SHORTCUTS BRIDGE")
    print("="*80)
    print()
    print("Voice commands that trigger each and every keyboard shortcut")
    print("Use short tagging to define meta qualities and tagging for patterns")
    print("Define patterns in code with clearly defined decisioning")
    print("Prime number: 37 (Voice bridge number)")
    print()

    bridge = VOICESHORTCUT37()

    if args.map:
        voice_phrase, shortcut_id, app = args.map
        mapping = bridge.map_voice_to_shortcut(voice_phrase, shortcut_id, app)
        print(f"🔗 Mapping created: {mapping.mapping_id}")
        print(f"   Voice: {voice_phrase}")
        print(f"   Shortcut: {shortcut_id}")
        print(f"   Application: {app}")
        print()

    if args.map_all:
        mappings = bridge.map_all_shortcuts(args.map_all)
        print(f"🔗 Mapped {len(mappings)} shortcuts for {args.map_all}")
        print()

    if args.decisioning:
        code = bridge.get_decisioning_code(args.decisioning)
        print("💻 DECISIONING CODE:")
        print(code)
        print()

    if args.status:
        print("📊 STATUS:")
        print(f"   Voice commands: {len(bridge.voice_commands)}")
        print(f"   Mappings: {len(bridge.mappings)}")
        print()

    if not any([args.map, args.map_all, args.decisioning, args.status]):
        # Default: show status
        print("📊 STATUS:")
        print(f"   Voice commands: {len(bridge.voice_commands)}")
        print(f"   Mappings: {len(bridge.mappings)}")
        print()
        print("Use --map VOICE_PHRASE SHORTCUT_ID APP to map voice to shortcut")
        print("Use --map-all APPLICATION to map all shortcuts")
        print("Use --decisioning MAPPING_ID to get decisioning code")
        print("Use --status to show status")
        print()


if __name__ == "__main__":


    main()