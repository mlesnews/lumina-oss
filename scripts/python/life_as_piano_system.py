#!/usr/bin/env python3
"""
Life as Piano System - Playing Life Like a Piano

"LIKE EBONY-IVORY. LET'S PLAY LIFE LIKE A PIANO"

Sci-Fi Fantasy as the keys - every command is a note, every workflow is a song.

Tags: #LIFE_AS_PIANO #EBONY_IVORY #SCIFI_FANTASY #CREATIVITY #MUSIC #LUMINA_CORE
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LifeAsPiano")


class KeyType(Enum):
    """Type of piano key"""
    EBONY = "ebony"  # Science Fiction - dark, mysterious, technical
    IVORY = "ivory"  # Fantasy - light, magical, creative


@dataclass
class PianoKey:
    """A piano key (command/action)"""
    key_name: str
    key_type: KeyType
    note: str  # The "note" this key plays
    command: str  # The command it represents
    description: str


@dataclass
class PianoChord:
    """A chord (combination of keys)"""
    chord_name: str
    keys: List[PianoKey]
    harmony: str  # What the chord creates


@dataclass
class PianoNote:
    """A single note played"""
    key: PianoKey
    timestamp: datetime
    result: Any
    duration: float


class LifeAsPianoSystem:
    """
    Life as Piano System - LUMINA IS A MUSICAL INSTRUMENT

    "LIKE EBONY-IVORY. LET'S PLAY LIFE LIKE A PIANO"

    LUMINA is the musical instrument.
    Sci-Fi Fantasy are the keys - every command is a note, every workflow is a song.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Life as Piano System - LUMINA as the instrument"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # LUMINA IS A MUSICAL INSTRUMENT
        self.instrument_name = "LUMINA"
        self.instrument_type = "Piano"

        # Define the keys (Ebony = Sci-Fi, Ivory = Fantasy)
        self.keys = self._initialize_keys()

        # Play history
        self.notes_played: List[PianoNote] = []
        self.chords_played: List[PianoChord] = []

        logger.info("✅ Life as Piano System initialized")
        logger.info(f"   🎹 {self.instrument_name} is a {self.instrument_type}")
        logger.info("   🎹 Ebony & Ivory keys ready")
        logger.info("   🎵 Let's play LUMINA like a piano")

    def _initialize_keys(self) -> Dict[str, PianoKey]:
        """Initialize piano keys (Sci-Fi Fantasy)"""
        keys = {}

        # Ebony Keys (Science Fiction)
        ebony_keys = [
            PianoKey("jarvis", KeyType.EBONY, "C", "@JARVIS", "AI assistant - Iron Man"),
            PianoKey("spock", KeyType.EBONY, "D", "@SPOCK", "Logic & analysis - Star Trek"),
            PianoKey("bones", KeyType.EBONY, "E", "@BONES", "Medical & health - Star Trek"),
            PianoKey("doit", KeyType.EBONY, "F", "@DOIT", "Immediate execution"),
            PianoKey("api_cli", KeyType.EBONY, "G", "API/CLI", "Technical control"),
            PianoKey("intent", KeyType.EBONY, "A", "Intent", "Understanding"),
            PianoKey("dragon", KeyType.EBONY, "B", "Dragon", "Voice control"),
        ]

        # Ivory Keys (Fantasy)
        ivory_keys = [
            PianoKey("magic", KeyType.IVORY, "C#", "Magic", "Possibility & wonder"),
            PianoKey("clarity", KeyType.IVORY, "D#", "Clarity", "Crystal clear understanding"),
            PianoKey("blocks", KeyType.IVORY, "F#", "Blocks", "Basic building blocks"),
            PianoKey("context", KeyType.IVORY, "G#", "Context", "The story"),
            PianoKey("workflow", KeyType.IVORY, "A#", "Workflow", "The journey"),
            PianoKey("response", KeyType.IVORY, "C", "Response", "The magic"),
        ]

        # Add all keys
        for key in ebony_keys + ivory_keys:
            keys[key.key_name] = key

        logger.info(f"   🎹 LUMINA Instrument: {len(ebony_keys)} Ebony keys (Sci-Fi)")
        logger.info(f"   🎹 LUMINA Instrument: {len(ivory_keys)} Ivory keys (Fantasy)")
        logger.info(f"   🎵 Total keys on LUMINA: {len(ebony_keys) + len(ivory_keys)}")

        return keys

    def play_key(self, command: str) -> PianoNote:
        """
        Play a single key (execute a command)

        This is like pressing a piano key - it creates a note.
        """
        # Find the key
        key = self._find_key_for_command(command)

        if not key:
            # Create a default key
            key = PianoKey(
                key_name="unknown",
                key_type=KeyType.EBONY,
                note="?",
                command=command,
                description="Unknown command"
            )

        logger.info(f"   🎹 Playing LUMINA key: {key.key_name} ({key.note}) - {key.description}")

        # Execute the command (play the note on LUMINA)
        start_time = datetime.now()
        result = self._execute_key(key, command)
        duration = (datetime.now() - start_time).total_seconds()

        # Create the note
        note = PianoNote(
            key=key,
            timestamp=start_time,
            result=result,
            duration=duration
        )

        self.notes_played.append(note)

        logger.info(f"   🎵 LUMINA note played: {key.note} - Duration: {duration:.2f}s")

        return note

    def play_chord(self, commands: List[str]) -> PianoChord:
        """
        Play a chord (execute multiple commands together)

        This is like pressing multiple keys simultaneously - it creates harmony.
        """
        keys = []
        notes = []

        for command in commands:
            key = self._find_key_for_command(command)
            if key:
                keys.append(key)
                note = self.play_key(command)
                notes.append(note)

        # Create the chord
        chord_name = "-".join([k.key_name for k in keys])
        harmony = self._create_harmony(keys)

        chord = PianoChord(
            chord_name=chord_name,
            keys=keys,
            harmony=harmony
        )

        self.chords_played.append(chord)

        logger.info(f"   🎹 LUMINA chord played: {chord_name}")
        logger.info(f"   🎵 Harmony on LUMINA: {harmony}")

        return chord

    def compose_symphony(self, workflow: List[str]) -> Dict[str, Any]:
        """
        Compose a symphony (execute a complete workflow)

        This is like playing a complete piece of music.
        """
        logger.info(f"   🎼 Composing symphony on LUMINA: {len(workflow)} movements")

        movements = []
        for i, command in enumerate(workflow, 1):
            logger.info(f"   🎵 LUMINA Movement {i}: {command}")
            note = self.play_key(command)
            movements.append({
                "movement": i,
                "command": command,
                "note": note.key.note,
                "result": note.result,
                "duration": note.duration
            })

        symphony = {
            "title": "LUMINA Symphony",
            "instrument": "LUMINA",
            "movements": movements,
            "total_duration": sum(m["duration"] for m in movements),
            "keys_played": len(set(m["note"] for m in movements)),
            "harmony": "Beautiful music created on LUMINA"
        }

        logger.info(f"   🎼 LUMINA Symphony complete: {symphony['harmony']}")
        logger.info(f"   🎹 LUMINA keys played: {symphony['keys_played']}")
        logger.info(f"   ⏱️  Total duration: {symphony['total_duration']:.2f}s")

        return symphony

    def _find_key_for_command(self, command: str) -> Optional[PianoKey]:
        """Find the piano key for a command"""
        command_lower = command.lower()

        for key_name, key in self.keys.items():
            if key_name in command_lower or key.command.lower() in command_lower:
                return key

        return None

    def _execute_key(self, key: PianoKey, command: str) -> Any:
        """Execute a key (play the note)"""
        # This would integrate with JARVIS API/CLI, intent preservation, etc.
        # For now, simulate execution

        if key.key_type == KeyType.EBONY:
            # Science Fiction keys - technical execution
            logger.debug(f"   🔧 Executing Sci-Fi key: {key.key_name}")
            return f"Sci-Fi execution: {command}"
        else:
            # Fantasy keys - magical execution
            logger.debug(f"   ✨ Executing Fantasy key: {key.key_name}")
            return f"Fantasy execution: {command}"

    def _create_harmony(self, keys: List[PianoKey]) -> str:
        """Create harmony from multiple keys"""
        ebony_count = sum(1 for k in keys if k.key_type == KeyType.EBONY)
        ivory_count = sum(1 for k in keys if k.key_type == KeyType.IVORY)

        if ebony_count > ivory_count:
            return "Technical harmony - Sci-Fi dominant"
        elif ivory_count > ebony_count:
            return "Magical harmony - Fantasy dominant"
        else:
            return "Perfect harmony - Ebony & Ivory balanced"

    def get_play_history(self) -> Dict[str, Any]:
        """Get history of notes and chords played"""
        return {
            "notes_played": len(self.notes_played),
            "chords_played": len(self.chords_played),
            "recent_notes": [
                {
                    "key": note.key.key_name,
                    "note": note.key.note,
                    "type": note.key.key_type.value,
                    "timestamp": note.timestamp.isoformat(),
                    "duration": note.duration
                }
                for note in self.notes_played[-10:]  # Last 10 notes
            ],
            "recent_chords": [
                {
                    "name": chord.chord_name,
                    "harmony": chord.harmony,
                    "keys": [k.key_name for k in chord.keys]
                }
                for chord in self.chords_played[-5:]  # Last 5 chords
            ]
        }


# Global instance
_life_as_piano_instance = None


def get_life_as_piano() -> LifeAsPianoSystem:
    """Get or create global Life as Piano System - LUMINA IS A MUSICAL INSTRUMENT"""
    global _life_as_piano_instance
    if _life_as_piano_instance is None:
        _life_as_piano_instance = LifeAsPianoSystem()
        logger.info("✅ Life as Piano System initialized")
        logger.info("   🎹 LUMINA IS A MUSICAL INSTRUMENT")
        logger.info("   🎵 LET'S PLAY LUMINA LIKE A PIANO")
    return _life_as_piano_instance


def play_key(command: str) -> PianoNote:
    """Play a single key"""
    piano = get_life_as_piano()
    return piano.play_key(command)


def play_chord(commands: List[str]) -> PianoChord:
    """Play a chord"""
    piano = get_life_as_piano()
    return piano.play_chord(commands)


def compose_symphony(workflow: List[str]) -> Dict[str, Any]:
    """Compose a symphony"""
    piano = get_life_as_piano()
    return piano.compose_symphony(workflow)


if __name__ == "__main__":
    # Test
    piano = get_life_as_piano()

    # Play a single key
    print("\n🎹 Playing a single key...")
    note = piano.play_key("@JARVIS check grammar")
    print(f"   Note: {note.key.note}, Result: {note.result}")

    # Play a chord
    print("\n🎹 Playing a chord...")
    chord = piano.play_chord(["@JARVIS", "@SPOCK", "analyze"])
    print(f"   Chord: {chord.chord_name}, Harmony: {chord.harmony}")

    # Compose a symphony
    print("\n🎼 Composing a symphony...")
    symphony = piano.compose_symphony([
        "Establish context",
        "Analyze intent",
        "Confirm understanding",
        "Execute with grace"
    ])
    print(f"   Symphony: {symphony['title']}")
    print(f"   Harmony: {symphony['harmony']}")
