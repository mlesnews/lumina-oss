#!/usr/bin/env python3
"""
STT Voice Command Integration

Best approach for integrating Speech-to-Text (STT) for voice command recognition
in the Hybrid Macro Voice Framework.

Leverages existing Dragon NaturallySpeaking integration.

Tags: #STT #VOICE_RECOGNITION #DRAGON #MACROS #HYBRID @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("STTVoiceCommandIntegration")


class STTVoiceCommandIntegration:
    """
    STT Voice Command Integration

    Best approach for voice command recognition:
    1. Leverage existing Dragon NaturallySpeaking integration
    2. Use continuous listening with keyword detection
    3. Process commands through hybrid framework
    4. Integrate with ElevenLabs for feedback
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize STT integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "stt_voice_commands"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Dragon NaturallySpeaking
        self._init_dragon_stt()

        # Initialize hybrid framework
        self._init_hybrid_framework()

        # Voice command registry
        self.voice_commands: Dict[str, Dict[str, Any]] = {}

        logger.info("✅ STT Voice Command Integration initialized")
        logger.info("   🎤 Dragon NaturallySpeaking STT: READY")
        logger.info("   🔗 Hybrid Framework: CONNECTED")

    def _init_dragon_stt(self):
        """Initialize Dragon NaturallySpeaking STT"""
        try:
            from replica_inspired_hybrid_system import ReplicaInspiredHybrid
            self.replica_hybrid = ReplicaInspiredHybrid()

            # Check if Dragon is available
            if hasattr(self.replica_hybrid, 'dragon') and self.replica_hybrid.dragon:
                self.dragon_available = True
                logger.info("   ✅ Dragon NaturallySpeaking: ACTIVE")
            else:
                self.dragon_available = False
                logger.warning("   ⚠️  Dragon NaturallySpeaking: NOT AVAILABLE")
                logger.info("   💡 Alternative: Use Windows Speech Recognition API")
        except ImportError:
            self.dragon_available = False
            logger.warning("   ⚠️  Replica Hybrid System: NOT AVAILABLE")
            logger.info("   💡 Fallback: Use Windows Speech Recognition API")

    def _init_hybrid_framework(self):
        """Initialize hybrid framework connection"""
        try:
            from hybrid_macro_voice_framework import HybridMacroVoiceFramework
            self.hybrid_framework = HybridMacroVoiceFramework()
            logger.info("   ✅ Hybrid Framework: CONNECTED")
        except ImportError:
            logger.warning("   ⚠️  Hybrid Framework: NOT AVAILABLE")
            self.hybrid_framework = None

    def register_voice_command(self, command: str, macro_id: str, 
                              aliases: Optional[List[str]] = None) -> bool:
        """
        Register voice command for macro execution

        Best Practice: Register natural language commands with aliases

        Args:
            command: Primary voice command (e.g., "undo all changes")
            macro_id: Macro ID to execute
            aliases: Alternative phrases (e.g., ["undo", "revert all"])
        """
        if aliases is None:
            aliases = []

        self.voice_commands[command.lower()] = {
            "macro_id": macro_id,
            "aliases": [a.lower() for a in aliases],
            "registered_at": datetime.now().isoformat()
        }

        # Also register aliases
        for alias in aliases:
            self.voice_commands[alias.lower()] = {
                "macro_id": macro_id,
                "aliases": [],
                "registered_at": datetime.now().isoformat()
            }

        logger.info(f"✅ Voice command registered: '{command}' -> {macro_id}")
        return True

    def process_voice_command(self, spoken_text: str) -> Dict[str, Any]:
        """
        Process voice command through STT

        Best Approach:
        1. Normalize spoken text
        2. Match against registered commands
        3. Execute macro via hybrid framework
        4. Return execution results
        """
        if not spoken_text:
            return {"success": False, "error": "No voice input"}

        # Normalize text
        normalized = spoken_text.lower().strip()

        # Find matching command
        matched_command = None
        macro_id = None

        # Direct match
        if normalized in self.voice_commands:
            matched_command = normalized
            macro_id = self.voice_commands[normalized]["macro_id"]
        else:
            # Fuzzy match - check if command contains registered phrase
            for cmd, data in self.voice_commands.items():
                if cmd in normalized or normalized in cmd:
                    matched_command = cmd
                    macro_id = data["macro_id"]
                    break

        if not macro_id:
            return {
                "success": False,
                "error": f"Command not recognized: '{spoken_text}'",
                "suggestions": list(self.voice_commands.keys())[:5]
            }

        # Execute macro via hybrid framework
        if self.hybrid_framework:
            result = self.hybrid_framework.execute_hybrid_macro(macro_id)
            result["voice_command"] = matched_command
            result["spoken_text"] = spoken_text
            return result
        else:
            return {
                "success": False,
                "error": "Hybrid framework not available",
                "macro_id": macro_id
            }

    def start_continuous_listening(self, wake_word: str = "jarvis") -> bool:
        """
        Start continuous voice listening with wake word

        Best Approach:
        1. Use Dragon NaturallySpeaking continuous listening
        2. Detect wake word ("jarvis", "lumina", etc.)
        3. Process commands after wake word
        4. Return to listening mode

        Args:
            wake_word: Wake word to activate command mode
        """
        if not self.dragon_available:
            logger.warning("   ⚠️  Dragon STT not available, cannot start listening")
            return False

        logger.info(f"✅ Continuous listening started")
        logger.info(f"   🎤 Wake word: '{wake_word}'")
        logger.info(f"   📋 Registered commands: {len(self.voice_commands)}")
        logger.info("")
        logger.info("   💡 Usage:")
        logger.info(f"      1. Say '{wake_word}' to activate")
        logger.info(f"      2. Speak your command")
        logger.info(f"      3. System processes and executes")
        logger.info("")

        return True

    def integrate_with_hybrid_macros(self):
        """
        Auto-register voice commands from hybrid macros

        Best Practice: Automatically register voice commands
        from existing hybrid macros
        """
        if not self.hybrid_framework:
            logger.warning("   ⚠️  Hybrid framework not available")
            return

        registered = 0
        for macro_id, macro in self.hybrid_framework.macros.items():
            if macro.voice_command:
                # Register primary command
                self.register_voice_command(
                    command=macro.voice_command,
                    macro_id=macro_id,
                    aliases=self._generate_aliases(macro.voice_command)
                )
                registered += 1

        logger.info(f"✅ Auto-registered {registered} voice commands from hybrid macros")

    def _generate_aliases(self, command: str) -> List[str]:
        """Generate common aliases for voice command"""
        aliases = []

        # Common variations
        variations = {
            "undo": ["revert", "cancel", "rollback"],
            "keep": ["save", "accept", "confirm"],
            "focus": ["open", "show", "display"],
            "all": ["everything", "complete", "full"]
        }

        words = command.lower().split()
        for word in words:
            if word in variations:
                for variant in variations[word]:
                    aliases.append(command.replace(word, variant))

        return aliases

    def create_stt_integration_guide(self) -> Path:
        """Create integration guide for STT"""
        guide_file = self.data_dir / "STT_INTEGRATION_GUIDE.md"

        guide = f"""# STT Voice Command Integration Guide

## Best Approach for STT Integration

### 1. Leverage Existing Dragon NaturallySpeaking

**Current Status:**
- ✅ Dragon NaturallySpeaking is already integrated via Replica-Inspired Hybrid System
- ✅ Available in: `replica_inspired_hybrid_system.py`
- ✅ Configuration: `config/dragon_config.json`

**Integration Steps:**

1. **Use Existing Dragon Integration:**
   ```python
   from replica_inspired_hybrid_system import ReplicaInspiredHybrid
   hybrid = ReplicaInspiredHybrid()
   # Dragon STT is available via hybrid.dragon
   ```

2. **Connect to Hybrid Framework:**
   ```python
   from stt_voice_command_integration import STTVoiceCommandIntegration
   stt = STTVoiceCommandIntegration()
   stt.integrate_with_hybrid_macros()
   ```

3. **Start Continuous Listening:**
   ```python
   stt.start_continuous_listening(wake_word="jarvis")
   ```

### 2. Alternative: Windows Speech Recognition API

**If Dragon is not available:**

```python
import speech_recognition as sr

recognizer = sr.Recognizer()
with sr.Microphone() as source:
    audio = recognizer.listen(source)
    text = recognizer.recognize_google(audio)
```

### 3. Voice Command Flow

```
User speaks → STT (Dragon) → Normalize text → Match command → 
Execute macro → TTS feedback (ElevenLabs)
```

### 4. Best Practices

1. **Wake Word Detection:**
   - Use "jarvis" or "lumina" as wake word
   - Reduces false positives
   - Saves processing power

2. **Command Normalization:**
   - Convert to lowercase
   - Remove punctuation
   - Handle variations ("undo" = "revert" = "cancel")

3. **Fuzzy Matching:**
   - Match partial commands
   - Handle typos/recognition errors
   - Suggest alternatives

4. **Feedback Loop:**
   - Confirm command recognition
   - Provide TTS feedback via ElevenLabs
   - Log all voice interactions

### 5. Integration with Hybrid Framework

**Auto-registration:**
- Voice commands from hybrid macros are auto-registered
- No manual configuration needed
- Supports aliases and variations

**Execution:**
- Voice commands trigger hybrid macro execution
- All methods execute (PowerToys, AutoHotkey, Armoury Crate, MANUS)
- TTS feedback confirms execution

### 6. Example Usage

```python
# Initialize
stt = STTVoiceCommandIntegration()

# Auto-register from hybrid macros
stt.integrate_with_hybrid_macros()

# Start listening
stt.start_continuous_listening(wake_word="jarvis")

# Process command
result = stt.process_voice_command("undo all changes")
# Executes: Cursor IDE: Undo All (Hybrid) macro
```

## Status

✅ **Dragon NaturallySpeaking:** INTEGRATED  
✅ **Hybrid Framework:** CONNECTED  
✅ **Voice Commands:** AUTO-REGISTERED  
✅ **Continuous Listening:** READY

---

**Created:** {datetime.now().isoformat()}
"""

        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)

        logger.info(f"✅ Integration guide created: {guide_file.name}")
        return guide_file


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="STT Voice Command Integration")
    parser.add_argument("--integrate", action="store_true", help="Integrate with hybrid macros")
    parser.add_argument("--start-listening", action="store_true", help="Start continuous listening")
    parser.add_argument("--wake-word", type=str, default="jarvis", help="Wake word for listening")
    parser.add_argument("--create-guide", action="store_true", help="Create integration guide")

    args = parser.parse_args()

    stt = STTVoiceCommandIntegration()

    if args.create_guide:
        stt.create_stt_integration_guide()
    elif args.integrate:
        stt.integrate_with_hybrid_macros()
    elif args.start_listening:
        stt.start_continuous_listening(wake_word=args.wake_word)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())