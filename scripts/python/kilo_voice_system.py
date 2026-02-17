#!/usr/bin/env python3
"""
Kilo Voice System - Full Voice Interface for Kilo Code

Combines all Jarvis Voice capabilities into Kilo Code:
- STT: Local Whisper transcription
- TTS: ElevenLabs high-quality voice output
- Hands-free IDE control via voice commands
- Push-to-talk AND continuous listening modes
- Wake word detection ("Hey Kilo")
- Voice command parsing and execution

This is the unified voice system replacing kilo_voice_input.py.

Requirements:
    pip install sounddevice numpy keyboard pyperclip faster-whisper scipy elevenlabs pynput

Usage:
    python kilo_voice_system.py              # Start voice system
    python kilo_voice_system.py --ptt        # Push-to-talk mode (default)
    python kilo_voice_system.py --continuous # Continuous listening mode
    python kilo_voice_system.py --test-mic   # Test microphone
    python kilo_voice_system.py --test-tts   # Test TTS
    python kilo_voice_system.py --install    # Install dependencies

Tags: @PEAK @KILO_CODE @VOICE #automation
"""

import argparse
import json
import os
import queue
import re
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data" / "kilo_voice"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_CONFIG = {
    # Hotkey settings
    "push_to_talk_key": "ctrl+shift+k",
    "wake_word": "hey kilo",
    "wake_word_enabled": False,  # Start with PTT, wake word optional
    # Audio settings
    "sample_rate": 16000,
    "channels": 1,
    "chunk_size": 1024,
    "silence_threshold": 0.01,
    "silence_duration": 1.5,  # seconds of silence before stopping
    "max_recording_duration": 30,  # max seconds
    # Whisper STT settings
    "whisper_model": "base.en",  # tiny.en, base.en, small.en, medium.en, large
    "whisper_device": "cuda",  # cuda, cpu
    "language": "en",
    # ElevenLabs TTS settings
    "elevenlabs_enabled": True,
    "elevenlabs_voice_id": None,  # Auto-detect JARVIS voice
    "elevenlabs_model": "eleven_turbo_v2_5",  # Free tier compatible model
    "tts_feedback_enabled": True,  # Speak confirmations
    # Kilo Code integration
    "kilo_auto_send": True,  # Auto-paste to Kilo
    "kilo_prefix": "",
    "kilo_suffix": "",
    # Mode settings
    "mode": "ptt",  # ptt (push-to-talk), continuous, wake_word
    "sound_feedback": True,
    "visual_feedback": True,
}


def load_config() -> dict:
    """Load configuration from file"""
    config_path = CONFIG_DIR / "kilo_voice_system.json"
    if config_path.exists():
        with open(config_path) as f:
            saved = json.load(f)
        return {**DEFAULT_CONFIG, **saved}
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Save configuration to file"""
    config_path = CONFIG_DIR / "kilo_voice_system.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


# =============================================================================
# VOICE COMMANDS
# =============================================================================


class CommandType(Enum):
    """Voice command types"""

    KILO_CHAT = "kilo_chat"  # Send to Kilo Code chat
    IDE_CONTROL = "ide_control"  # VS Code/Cursor commands
    FILE_OP = "file_operation"
    TERMINAL = "terminal"
    GIT = "git"
    NAVIGATION = "navigation"
    SYSTEM = "system"  # Voice system control


@dataclass
class VoiceCommand:
    """Parsed voice command"""

    command_id: str
    raw_text: str
    command_type: CommandType
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# Command patterns (regex -> action)
COMMAND_PATTERNS = {
    # System commands
    CommandType.SYSTEM: [
        (r"^stop listening$", "stop_listening", {}),
        (r"^pause$", "pause_listening", {}),
        (r"^resume$", "resume_listening", {}),
        (r"^quiet mode$", "toggle_tts", {"enabled": False}),
        (r"^voice mode$", "toggle_tts", {"enabled": True}),
    ],
    # IDE control
    CommandType.IDE_CONTROL: [
        (r"^save( file)?$", "save_file", {}),
        (r"^close( file)?$", "close_file", {}),
        (r"^new file$", "new_file", {}),
        (r"^undo$", "undo", {}),
        (r"^redo$", "redo", {}),
        (r"^format( code)?$", "format_code", {}),
        (r"^run( code)?$", "run_code", {}),
        (r"^go to line (\d+)$", "go_to_line", {"line": 1}),
        (r"^find (.+)$", "find_text", {"text": 1}),
        (r"^replace (.+) with (.+)$", "replace_text", {"find": 1, "replace": 2}),
        (r"^select all$", "select_all", {}),
        (r"^copy$", "copy", {}),
        (r"^cut$", "cut", {}),
        (r"^paste$", "paste", {}),
    ],
    # Terminal
    CommandType.TERMINAL: [
        (r"^run command (.+)$", "run_command", {"cmd": 1}),
        (r"^execute (.+)$", "run_command", {"cmd": 1}),
        (r"^terminal (.+)$", "run_command", {"cmd": 1}),
        (r"^clear terminal$", "clear_terminal", {}),
    ],
    # Git
    CommandType.GIT: [
        (r"^git status$", "git_status", {}),
        (r"^git commit (.+)$", "git_commit", {"message": 1}),
        (r"^git push$", "git_push", {}),
        (r"^git pull$", "git_pull", {}),
    ],
    # Navigation
    CommandType.NAVIGATION: [
        (r"^open file (.+)$", "open_file", {"file": 1}),
        (r"^go to definition$", "go_to_definition", {}),
        (r"^go back$", "go_back", {}),
        (r"^go forward$", "go_forward", {}),
        (r"^show files?$", "show_explorer", {}),
        (r"^show terminal$", "show_terminal", {}),
    ],
}


def parse_command(text: str) -> Optional[VoiceCommand]:
    """Parse voice text into a command"""
    text_lower = text.lower().strip()

    for cmd_type, patterns in COMMAND_PATTERNS.items():
        for pattern, action, param_map in patterns:
            match = re.match(pattern, text_lower)
            if match:
                params = {}
                for param_name, group_idx in param_map.items():
                    if isinstance(group_idx, int) and group_idx <= len(match.groups()):
                        params[param_name] = match.group(group_idx)
                    else:
                        params[param_name] = group_idx

                return VoiceCommand(
                    command_id=f"cmd_{int(time.time() * 1000)}",
                    raw_text=text,
                    command_type=cmd_type,
                    action=action,
                    parameters=params,
                )

    # No match = send to Kilo Code as chat
    return VoiceCommand(
        command_id=f"chat_{int(time.time() * 1000)}",
        raw_text=text,
        command_type=CommandType.KILO_CHAT,
        action="send_to_kilo",
        parameters={"text": text},
    )


# =============================================================================
# AUDIO COMPONENTS
# =============================================================================


class AudioRecorder:
    """Records audio from microphone"""

    def __init__(self, config: dict):
        self.config = config
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream = None

        # Import here to allow graceful degradation
        import numpy as np
        import sounddevice as sd

        self.sd = sd
        self.np = np

    def start(self):
        """Start recording"""
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_queue = queue.Queue()

        def callback(indata, frames, time_info, status):
            if self.is_recording:
                self.audio_queue.put(indata.copy())

        self.stream = self.sd.InputStream(
            samplerate=self.config["sample_rate"],
            channels=self.config["channels"],
            callback=callback,
            dtype=self.np.float32,
        )
        self.stream.start()

    def stop(self) -> "np.ndarray":
        """Stop recording and return audio"""
        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Collect all audio chunks
        chunks = []
        while not self.audio_queue.empty():
            chunks.append(self.audio_queue.get())

        if chunks:
            return self.np.concatenate(chunks, axis=0)
        return self.np.array([])

    def get_level(self) -> float:
        """Get current audio level"""
        if self.audio_queue.empty():
            return 0.0
        # Peek at latest chunk
        latest = list(self.audio_queue.queue)[-1] if self.audio_queue.queue else None
        if latest is not None:
            return float(self.np.abs(latest).mean())
        return 0.0


class WhisperSTT:
    """Speech-to-text using Whisper"""

    def __init__(self, config: dict):
        self.config = config
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load Whisper model"""
        print(f"Loading Whisper model: {self.config['whisper_model']}...")

        # Prefer openai-whisper (more reliable on Windows)
        try:
            import whisper

            self.model = whisper.load_model(self.config["whisper_model"])
            self.model_type = "openai_whisper"
            print(f"Loaded openai-whisper model: {self.config['whisper_model']}")
        except Exception as e:
            print(f"openai-whisper not available ({e}), trying faster-whisper...")
            try:
                from faster_whisper import WhisperModel

                compute_type = "float16" if self.config["whisper_device"] == "cuda" else "int8"
                self.model = WhisperModel(
                    self.config["whisper_model"],
                    device=self.config["whisper_device"],
                    compute_type=compute_type,
                )
                self.model_type = "faster_whisper"
                print("Loaded faster-whisper model")
            except Exception as e2:
                print(f"ERROR: No whisper model available: {e2}")
                self.model = None
                self.model_type = None

    def transcribe(self, audio: "np.ndarray") -> Optional[str]:
        """Transcribe audio to text"""
        if self.model is None:
            return None

        # Save to temp file
        import scipy.io.wavfile as wav

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            wav.write(temp_path, self.config["sample_rate"], audio)

            if self.model_type == "faster_whisper":
                segments, _ = self.model.transcribe(temp_path, language=self.config["language"])
                text = " ".join([s.text for s in segments]).strip()
            else:
                result = self.model.transcribe(temp_path, language=self.config["language"])
                text = result["text"].strip()

            return text if text else None

        except Exception as e:
            print(f"Transcription error: {e}")
            return None
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass


class ElevenLabsTTS:
    """Text-to-speech using ElevenLabs"""

    def __init__(self, config: dict):
        self.config = config
        self.client = None
        self.voice_id = config.get("elevenlabs_voice_id")
        self._initialize()

    def _initialize(self):
        """Initialize ElevenLabs client"""
        if not self.config.get("elevenlabs_enabled"):
            return

        try:
            # Get API key from Azure Vault
            api_key = self._get_api_key()
            if not api_key:
                print("ElevenLabs API key not found")
                return

            from elevenlabs.client import ElevenLabs

            self.client = ElevenLabs(api_key=api_key)

            # Find voice
            if not self.voice_id:
                self._find_voice()

            print(f"ElevenLabs TTS initialized (voice: {self.voice_id})")

        except ImportError:
            print("ElevenLabs not installed: pip install elevenlabs")
        except Exception as e:
            print(f"ElevenLabs initialization error: {e}")

    def _get_api_key(self) -> Optional[str]:
        """Get ElevenLabs API key from Azure Vault"""
        try:
            sys.path.insert(0, str(SCRIPT_DIR))
            from azure_service_bus_integration import AzureKeyVaultClient

            vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
            return vault.get_secret("elevenlabs-api-key")
        except Exception as e:
            print(f"Could not get API key from vault: {e}")
            # Try environment variable as fallback
            return os.environ.get("ELEVENLABS_API_KEY")

    def _find_voice(self):
        """Find a suitable voice"""
        if not self.client:
            return

        try:
            voices = self.client.voices.get_all()
            # Look for JARVIS or Kilo voice
            for voice in voices.voices:
                if "jarvis" in voice.name.lower() or "kilo" in voice.name.lower():
                    self.voice_id = voice.voice_id
                    return
            # Use first voice
            if voices.voices:
                self.voice_id = voices.voices[0].voice_id
        except Exception as e:
            print(f"Could not list voices: {e}")

    def speak(self, text: str, blocking: bool = False):
        """Speak text"""
        if not self.client or not self.voice_id:
            print(f"[TTS disabled] {text}")
            return

        try:
            # New ElevenLabs API uses text_to_speech.convert
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.config.get("elevenlabs_model", "eleven_monolingual_v1"),
            )

            # Collect audio bytes from generator
            audio_bytes = b"".join(audio_generator)

            # Save to temp and play
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name
                f.write(audio_bytes)

            if sys.platform == "win32":
                if blocking:
                    subprocess.run(["start", "/WAIT", temp_path], shell=True)
                else:
                    subprocess.Popen(["start", "/MIN", "/B", temp_path], shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["afplay", temp_path])
            else:
                subprocess.Popen(["aplay", temp_path])

            # Cleanup after delay
            def cleanup():
                time.sleep(15)
                try:
                    os.unlink(temp_path)
                except:
                    pass

            threading.Thread(target=cleanup, daemon=True).start()

        except Exception as e:
            print(f"TTS error: {e}")


# =============================================================================
# COMMAND EXECUTOR
# =============================================================================


class CommandExecutor:
    """Executes voice commands"""

    def __init__(self, config: dict, tts: Optional[ElevenLabsTTS] = None):
        self.config = config
        self.tts = tts

    def execute(self, cmd: VoiceCommand) -> Dict[str, Any]:
        """Execute a voice command"""
        try:
            if cmd.command_type == CommandType.KILO_CHAT:
                return self._send_to_kilo(cmd)
            elif cmd.command_type == CommandType.SYSTEM:
                return self._handle_system(cmd)
            elif cmd.command_type == CommandType.IDE_CONTROL:
                return self._handle_ide(cmd)
            elif cmd.command_type == CommandType.TERMINAL:
                return self._handle_terminal(cmd)
            elif cmd.command_type == CommandType.GIT:
                return self._handle_git(cmd)
            elif cmd.command_type == CommandType.NAVIGATION:
                return self._handle_navigation(cmd)
            else:
                return self._send_to_kilo(cmd)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_to_kilo(self, cmd: VoiceCommand) -> Dict[str, Any]:
        """Send text to Kilo Code via clipboard"""
        import pyperclip

        text = cmd.parameters.get("text", cmd.raw_text)
        prefix = self.config.get("kilo_prefix", "")
        suffix = self.config.get("kilo_suffix", "")
        full_text = f"{prefix}{text}{suffix}"

        pyperclip.copy(full_text)

        if self.config.get("kilo_auto_send", True):
            # Simulate Ctrl+V to paste
            import keyboard

            time.sleep(0.1)
            keyboard.send("ctrl+v")
            time.sleep(0.05)
            keyboard.send("enter")  # Send to Kilo

        if self.tts and self.config.get("tts_feedback_enabled"):
            self.tts.speak("Sent to Kilo")

        return {"success": True, "action": "send_to_kilo", "text": full_text}

    def _handle_system(self, cmd: VoiceCommand) -> Dict[str, Any]:
        """Handle system commands"""
        action = cmd.action

        if action == "toggle_tts":
            enabled = cmd.parameters.get("enabled", True)
            self.config["tts_feedback_enabled"] = enabled
            return {"success": True, "action": action, "tts_enabled": enabled}

        return {"success": True, "action": action}

    def _handle_ide(self, cmd: VoiceCommand) -> Dict[str, Any]:
        """Handle IDE commands via keyboard shortcuts"""
        import keyboard

        shortcuts = {
            "save_file": "ctrl+s",
            "close_file": "ctrl+w",
            "new_file": "ctrl+n",
            "undo": "ctrl+z",
            "redo": "ctrl+y",
            "format_code": "shift+alt+f",
            "run_code": "f5",
            "select_all": "ctrl+a",
            "copy": "ctrl+c",
            "cut": "ctrl+x",
            "paste": "ctrl+v",
            "find_text": "ctrl+f",
        }

        action = cmd.action
        if action in shortcuts:
            keyboard.send(shortcuts[action])

            # For find, type the search text
            if action == "find_text" and "text" in cmd.parameters:
                time.sleep(0.2)
                keyboard.write(cmd.parameters["text"])

            return {"success": True, "action": action}

        if action == "go_to_line":
            keyboard.send("ctrl+g")
            time.sleep(0.2)
            keyboard.write(str(cmd.parameters.get("line", 1)))
            keyboard.send("enter")
            return {"success": True, "action": action}

        return {"success": False, "error": f"Unknown IDE action: {action}"}

    def _handle_terminal(self, cmd: VoiceCommand) -> Dict[str, Any]:
        """Handle terminal commands"""
        import keyboard

        if cmd.action == "clear_terminal":
            keyboard.send("ctrl+l")
            return {"success": True, "action": "clear_terminal"}

        if cmd.action == "run_command":
            command = cmd.parameters.get("cmd", "")
            # Focus terminal and type command
            keyboard.send("ctrl+`")  # Toggle terminal
            time.sleep(0.3)
            keyboard.write(command)
            keyboard.send("enter")
            return {"success": True, "action": "run_command", "command": command}

        return {"success": False, "error": "Unknown terminal action"}

    def _handle_git(self, cmd: VoiceCommand) -> Dict[str, Any]:
        """Handle git commands"""
        import keyboard

        action = cmd.action

        # Open terminal and run git command
        keyboard.send("ctrl+`")
        time.sleep(0.3)

        if action == "git_status":
            keyboard.write("git status")
        elif action == "git_push":
            keyboard.write("git push")
        elif action == "git_pull":
            keyboard.write("git pull")
        elif action == "git_commit":
            msg = cmd.parameters.get("message", "voice commit")
            keyboard.write(f'git commit -m "{msg}"')

        keyboard.send("enter")
        return {"success": True, "action": action}

    def _handle_navigation(self, cmd: VoiceCommand) -> Dict[str, Any]:
        """Handle navigation commands"""
        import keyboard

        shortcuts = {
            "go_to_definition": "f12",
            "go_back": "alt+left",
            "go_forward": "alt+right",
            "show_explorer": "ctrl+shift+e",
            "show_terminal": "ctrl+`",
        }

        action = cmd.action
        if action in shortcuts:
            keyboard.send(shortcuts[action])
            return {"success": True, "action": action}

        if action == "open_file":
            file_name = cmd.parameters.get("file", "")
            keyboard.send("ctrl+p")
            time.sleep(0.2)
            keyboard.write(file_name)
            return {"success": True, "action": action, "file": file_name}

        return {"success": False, "error": "Unknown navigation action"}


# =============================================================================
# MAIN VOICE SYSTEM
# =============================================================================


class KiloVoiceSystem:
    """Main voice system for Kilo Code"""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.running = False
        self.paused = False

        # Initialize components
        print("\n" + "=" * 60)
        print("       KILO VOICE SYSTEM - Initializing")
        print("=" * 60)

        self.recorder = AudioRecorder(self.config)
        self.stt = WhisperSTT(self.config)
        self.tts = ElevenLabsTTS(self.config) if self.config.get("elevenlabs_enabled") else None
        self.executor = CommandExecutor(self.config, self.tts)

        # Command history
        self.history: List[VoiceCommand] = []

        print("=" * 60)
        print("       Initialization Complete")
        print("=" * 60 + "\n")

    def _on_recording_start(self):
        """Called when recording starts"""
        if self.config.get("sound_feedback"):
            print("🎤 Recording...")

    def _on_recording_stop(self):
        """Called when recording stops"""
        if self.config.get("sound_feedback"):
            print("🔄 Processing...")

    def _process_audio(self, audio) -> Optional[str]:
        """Process recorded audio"""

        if len(audio) == 0:
            return None

        # Transcribe
        text = self.stt.transcribe(audio)
        if not text:
            print("(no speech detected)")
            return None

        print(f"📝 Heard: {text}")
        return text

    def _handle_text(self, text: str):
        """Handle transcribed text"""
        # Parse command
        cmd = parse_command(text)

        # Log
        self.history.append(cmd)

        # Handle system commands
        if cmd.command_type == CommandType.SYSTEM:
            if cmd.action == "stop_listening":
                self.running = False
                if self.tts:
                    self.tts.speak("Goodbye")
                return
            elif cmd.action == "pause_listening":
                self.paused = True
                if self.tts:
                    self.tts.speak("Paused")
                return
            elif cmd.action == "resume_listening":
                self.paused = False
                if self.tts:
                    self.tts.speak("Resumed")
                return

        # Execute
        result = self.executor.execute(cmd)

        if result.get("success"):
            print(f"✅ {cmd.action}")
        else:
            print(f"❌ {result.get('error', 'Failed')}")

    def run_ptt(self):
        """Run in push-to-talk mode"""
        import keyboard

        hotkey = self.config["push_to_talk_key"]
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║               KILO VOICE SYSTEM - PTT MODE                   ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Hotkey: {hotkey:<20}                                  ║
║                                                              ║
║  HOLD {hotkey} to speak                                ║
║  RELEASE to send to Kilo Code                                ║
║                                                              ║
║  Say "stop listening" to exit                                ║
║  Press Ctrl+C to force exit                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

        if self.tts and self.config.get("tts_feedback_enabled"):
            self.tts.speak("Kilo voice ready")

        self.running = True
        is_pressed = False

        # Parse hotkey parts
        parts = hotkey.lower().split("+")
        main_key = parts[-1]
        modifiers = parts[:-1]

        def check_modifiers():
            for mod in modifiers:
                if not keyboard.is_pressed(mod):
                    return False
            return True

        def on_press(event):
            nonlocal is_pressed
            if event.name == main_key and check_modifiers() and not is_pressed:
                is_pressed = True
                if not self.paused:
                    self._on_recording_start()
                    self.recorder.start()

        def on_release(event):
            nonlocal is_pressed
            if event.name == main_key and is_pressed:
                is_pressed = False
                if not self.paused:
                    self._on_recording_stop()
                    audio = self.recorder.stop()
                    text = self._process_audio(audio)
                    if text:
                        self._handle_text(text)

        keyboard.on_press(on_press)
        keyboard.on_release(on_release)

        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            keyboard.unhook_all()
            print("\n👋 Kilo Voice stopped")

    def run_continuous(self):
        """Run in continuous listening mode"""

        print("""
╔══════════════════════════════════════════════════════════════╗
║            KILO VOICE SYSTEM - CONTINUOUS MODE               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Listening continuously...                                   ║
║  Just speak naturally                                        ║
║                                                              ║
║  Say "stop listening" to exit                                ║
║  Say "pause" / "resume" to control                           ║
║  Press Ctrl+C to force exit                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

        if self.tts and self.config.get("tts_feedback_enabled"):
            self.tts.speak("Kilo voice listening")

        self.running = True
        silence_start = None
        recording = False

        try:
            while self.running:
                if self.paused:
                    time.sleep(0.5)
                    continue

                # Start recording if not already
                if not recording:
                    self.recorder.start()
                    recording = True

                # Check audio level
                level = self.recorder.get_level()

                if level > self.config["silence_threshold"]:
                    # Voice detected
                    silence_start = None
                else:
                    # Silence
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > self.config["silence_duration"]:
                        # Silence threshold reached
                        self._on_recording_stop()
                        audio = self.recorder.stop()
                        recording = False

                        text = self._process_audio(audio)
                        if text:
                            self._handle_text(text)

                        silence_start = None

                time.sleep(0.05)

        except KeyboardInterrupt:
            pass
        finally:
            if recording:
                self.recorder.stop()
            print("\n👋 Kilo Voice stopped")


# =============================================================================
# CLI
# =============================================================================


def check_dependencies() -> List[str]:
    """Check for missing dependencies"""
    missing = []

    deps = [
        ("sounddevice", "sounddevice"),
        ("numpy", "numpy"),
        ("keyboard", "keyboard"),
        ("pyperclip", "pyperclip"),
        ("scipy", "scipy"),
    ]

    for module, package in deps:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    return missing


def install_dependencies():
    """Install required dependencies"""
    deps = [
        "sounddevice",
        "numpy",
        "keyboard",
        "pyperclip",
        "scipy",
        "faster-whisper",
        "elevenlabs",
    ]
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install"] + deps, check=True)
    print("Dependencies installed!")


def test_microphone():
    """Test microphone"""
    import numpy as np
    import sounddevice as sd

    print("\nTesting microphone...")
    print("\nAvailable devices:")
    print(sd.query_devices())

    print("\nRecording 3 seconds...")
    audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype=np.float32)
    sd.wait()

    level = np.abs(audio).mean()
    print(f"\nAudio level: {level:.6f}")

    if level < 0.001:
        print("⚠️  Audio level very low - check microphone")
    else:
        print("✅ Microphone working!")


def test_tts():
    """Test TTS"""
    config = load_config()
    tts = ElevenLabsTTS(config)

    if tts.client:
        print("\nSpeaking test message...")
        tts.speak("Kilo voice system test. Hello!")
        print("✅ TTS working!")
    else:
        print("❌ TTS not available")


def main():
    parser = argparse.ArgumentParser(description="Kilo Voice System")
    parser.add_argument("--ptt", action="store_true", help="Push-to-talk mode (default)")
    parser.add_argument("--continuous", action="store_true", help="Continuous listening mode")
    parser.add_argument("--test-mic", action="store_true", help="Test microphone")
    parser.add_argument("--test-tts", action="store_true", help="Test TTS")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--hotkey", default=None, help="Override PTT hotkey")
    parser.add_argument("--model", default=None, help="Whisper model size")
    parser.add_argument("--cpu", action="store_true", help="Force CPU mode")
    parser.add_argument("--no-tts", action="store_true", help="Disable TTS")

    args = parser.parse_args()

    if args.install:
        install_dependencies()
        return

    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Run: python kilo_voice_system.py --install")
        return 1

    if args.test_mic:
        test_microphone()
        return

    if args.test_tts:
        test_tts()
        return

    # Load config
    config = load_config()

    # Apply overrides
    if args.hotkey:
        config["push_to_talk_key"] = args.hotkey
    if args.model:
        config["whisper_model"] = args.model
    if args.cpu:
        config["whisper_device"] = "cpu"
    if args.no_tts:
        config["elevenlabs_enabled"] = False

    # Save config
    save_config(config)

    # Run
    system = KiloVoiceSystem(config)

    if args.continuous:
        system.run_continuous()
    else:
        system.run_ptt()


if __name__ == "__main__":
    main()
