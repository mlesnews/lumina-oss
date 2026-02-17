#!/usr/bin/env python3
"""
VA Full Voice Mode System

Complete voice/audio coordination system for all virtual assistants with:
- Full voice mode activation
- Audio coordination (prevent conflicts)
- Voice recognition across all VAs
- Text-to-speech coordination
- Company-wide voice collaboration

Features:
- Multi-VA voice recognition
- Coordinated TTS (no overlapping speech)
- Voice priority system
- Audio mixing and coordination
- Real-time voice collaboration

Tags: #VOICE #AUDIO #TTS #COLLABORATION #FULL_MODE @JARVIS @LUMINA
"""

import sys
import time
import threading
import queue
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("VAFullVoiceMode")

# Voice/Audio imports
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    JARVISElevenLabsTTS = None

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None


class VoicePriority(Enum):
    """Voice priority levels"""
    CRITICAL = 1  # JARVIS, system alerts
    HIGH = 2      # Iron Man, important notifications
    MEDIUM = 3    # Kenny, Anakin, regular updates
    LOW = 4       # Background, ambient


class VoiceState(Enum):
    """Voice state"""
    IDLE = "idle"
    LISTENING = "listening"
    SPEAKING = "speaking"
    PROCESSING = "processing"


@dataclass
class VoiceRequest:
    """Voice request for TTS"""
    request_id: str
    va_name: str
    text: str
    priority: VoicePriority
    blocking: bool = False
    voice_id: Optional[str] = None
    callback: Optional[Callable] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VoiceMessage:
    """Voice message between VAs"""
    message_id: str
    from_va: str
    to_va: Optional[str]  # None = broadcast
    text: str
    voice_data: Optional[bytes] = None
    timestamp: datetime = field(default_factory=datetime.now)


class VAFullVoiceModeSystem:
    """
    Full Voice Mode System for Virtual Assistants

    Coordinates voice/audio across all VAs:
    - Voice recognition
    - Text-to-speech
    - Audio mixing
    - Voice collaboration
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.log_dir = project_root / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        setup_logging()

        # Voice state
        self.voice_mode_active = False
        self.vas: Dict[str, Any] = {}  # Registered VAs
        self.voice_queue = queue.PriorityQueue()  # Priority queue for TTS
        self.current_speaker: Optional[str] = None
        self.voice_lock = threading.Lock()

        # Voice recognition
        self.recognizer = None
        self.microphone = None
        self.listening_vas: Dict[str, bool] = {}  # Which VAs are listening

        # TTS systems
        self.tts_systems: Dict[str, Any] = {}
        self._init_tts()

        # Voice messages
        self.voice_messages: List[VoiceMessage] = []
        self.message_lock = threading.Lock()

        # Voice recognition thread
        self.recognition_thread = None
        self.recognition_running = False

        # TTS processing thread
        self.tts_thread = None
        self.tts_running = False

        logger.info("✅ VA Full Voice Mode System initialized")

    def _init_tts(self):
        """Initialize TTS systems"""
        # ElevenLabs (preferred)
        if ELEVENLABS_AVAILABLE:
            try:
                self.tts_systems["elevenlabs"] = JARVISElevenLabsTTS(project_root=self.project_root)
                logger.info("✅ ElevenLabs TTS initialized")
            except Exception as e:
                logger.warning(f"⚠️  ElevenLabs TTS not available: {e}")

        # pyttsx3 (fallback)
        if PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                self.tts_systems["pyttsx3"] = engine
                logger.info("✅ pyttsx3 TTS initialized")
            except Exception as e:
                logger.warning(f"⚠️  pyttsx3 TTS not available: {e}")

    def register_va(self, va_name: str, va_instance: Any, priority: VoicePriority = VoicePriority.MEDIUM):
        """Register a VA with the voice system"""
        self.vas[va_name] = {
            "instance": va_instance,
            "priority": priority,
            "state": VoiceState.IDLE,
            "voice_id": None  # Can be set per VA
        }
        self.listening_vas[va_name] = False
        logger.info(f"✅ Registered VA: {va_name} (priority: {priority.name})")

    def start_full_voice_mode(self):
        """Start full voice mode"""
        if self.voice_mode_active:
            logger.warning("⚠️  Full voice mode already active")
            return

        self.voice_mode_active = True

        # Initialize voice recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("✅ Voice recognition initialized")
            except Exception as e:
                logger.warning(f"⚠️  Voice recognition not available: {e}")

        # Start TTS processing thread
        self.tts_running = True
        self.tts_thread = threading.Thread(target=self._tts_processor, daemon=True)
        self.tts_thread.start()

        # Start voice recognition thread
        if self.recognizer:
            self.recognition_running = True
            self.recognition_thread = threading.Thread(target=self._voice_recognition_loop, daemon=True)
            self.recognition_thread.start()

        logger.info("🎤 Full voice mode activated")

    def stop_full_voice_mode(self):
        """Stop full voice mode"""
        self.voice_mode_active = False
        self.recognition_running = False
        self.tts_running = False

        if self.tts_thread:
            self.tts_thread.join(timeout=2)
        if self.recognition_thread:
            self.recognition_thread.join(timeout=2)

        logger.info("🔇 Full voice mode deactivated")

    def speak(self, va_name: str, text: str, priority: Optional[VoicePriority] = None, 
              blocking: bool = False, voice_id: Optional[str] = None, 
              callback: Optional[Callable] = None) -> str:
        """
        Queue text for TTS

        Returns request_id for tracking
        """
        if va_name not in self.vas:
            logger.warning(f"⚠️  VA {va_name} not registered")
            return ""

        va_info = self.vas[va_name]
        request_priority = priority or va_info["priority"]

        request_id = f"{va_name}_{int(time.time() * 1000)}"
        request = VoiceRequest(
            request_id=request_id,
            va_name=va_name,
            text=text,
            priority=request_priority,
            blocking=blocking,
            voice_id=voice_id or va_info.get("voice_id"),
            callback=callback
        )

        # Add to priority queue (lower number = higher priority)
        self.voice_queue.put((request_priority.value, request))

        logger.debug(f"📢 Queued speech: {va_name} - {text[:50]}...")
        return request_id

    def _tts_processor(self):
        """Process TTS queue"""
        while self.tts_running:
            try:
                # Get next request (blocking with timeout)
                try:
                    priority, request = self.voice_queue.get(timeout=1)
                except queue.Empty:
                    continue

                # Wait if someone else is speaking
                with self.voice_lock:
                    if self.current_speaker and self.current_speaker != request.va_name:
                        # Check if current speaker has higher priority
                        current_va = self.vas.get(self.current_speaker)
                        if current_va and current_va["priority"].value < priority:
                            # Current speaker has higher priority, requeue
                            self.voice_queue.put((priority, request))
                            continue

                    self.current_speaker = request.va_name
                    self.vas[request.va_name]["state"] = VoiceState.SPEAKING

                # Speak using available TTS
                try:
                    if "elevenlabs" in self.tts_systems and request.voice_id:
                        # Use ElevenLabs with specific voice
                        self.tts_systems["elevenlabs"].speak(
                            request.text,
                            voice_id=request.voice_id
                        )
                        if request.blocking:
                            time.sleep(len(request.text) * 0.05)  # Rough estimate: 50ms per character
                    elif "elevenlabs" in self.tts_systems:
                        # Use ElevenLabs default voice
                        self.tts_systems["elevenlabs"].speak(request.text)
                        if request.blocking:
                            time.sleep(len(request.text) * 0.05)  # Rough estimate: 50ms per character
                    elif "pyttsx3" in self.tts_systems:
                        # Use pyttsx3
                        engine = self.tts_systems["pyttsx3"]
                        engine.say(request.text)
                        if request.blocking:
                            engine.runAndWait()
                        else:
                            engine.startLoop(False)
                            engine.iterate()
                            engine.endLoop()
                    else:
                        logger.warning("⚠️  No TTS system available")

                    # Callback
                    if request.callback:
                        request.callback(request.request_id, True)

                except Exception as e:
                    logger.error(f"❌ TTS error: {e}", exc_info=True)
                    if request.callback:
                        request.callback(request.request_id, False)

                finally:
                    with self.voice_lock:
                        self.current_speaker = None
                        self.vas[request.va_name]["state"] = VoiceState.IDLE

            except Exception as e:
                logger.error(f"❌ TTS processor error: {e}", exc_info=True)

    def _voice_recognition_loop(self):
        """Continuous voice recognition loop"""
        while self.recognition_running:
            try:
                # Check if any VA is listening
                if not any(self.listening_vas.values()):
                    time.sleep(0.5)
                    continue

                with self.microphone as source:
                    try:
                        # Listen for audio
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)

                        # Recognize speech
                        try:
                            text = self.recognizer.recognize_google(audio)
                            logger.info(f"🎤 Recognized: {text}")

                            # Broadcast to all listening VAs
                            self._broadcast_voice_input(text)

                        except sr.UnknownValueError:
                            # Could not understand audio
                            pass
                        except sr.RequestError as e:
                            logger.warning(f"⚠️  Speech recognition error: {e}")

                    except sr.WaitTimeoutError:
                        # Timeout - continue listening
                        pass

            except Exception as e:
                logger.error(f"❌ Voice recognition error: {e}", exc_info=True)
                time.sleep(1)

    def _broadcast_voice_input(self, text: str):
        """Broadcast voice input to all listening VAs"""
        for va_name, is_listening in self.listening_vas.items():
            if is_listening and va_name in self.vas:
                va_info = self.vas[va_name]
                va_instance = va_info["instance"]

                # Try to process voice input
                try:
                    if hasattr(va_instance, "process_voice_input"):
                        va_instance.process_voice_input(text)
                    elif hasattr(va_instance, "process_voice_command"):
                        va_instance.process_voice_command(text)
                except Exception as e:
                    logger.warning(f"⚠️  Error processing voice in {va_name}: {e}")

    def set_listening(self, va_name: str, listening: bool):
        """Set whether a VA is listening"""
        if va_name in self.listening_vas:
            self.listening_vas[va_name] = listening
            logger.debug(f"🎤 {va_name} listening: {listening}")

    def send_voice_message(self, from_va: str, to_va: Optional[str], text: str, 
                          voice_data: Optional[bytes] = None) -> str:
        """Send voice message between VAs"""
        message_id = f"msg_{int(time.time() * 1000)}"
        message = VoiceMessage(
            message_id=message_id,
            from_va=from_va,
            to_va=to_va,
            text=text,
            voice_data=voice_data
        )

        with self.message_lock:
            self.voice_messages.append(message)
            # Keep only last 100 messages
            if len(self.voice_messages) > 100:
                self.voice_messages.pop(0)

        # Deliver message
        if to_va and to_va in self.vas:
            va_info = self.vas[to_va]
            va_instance = va_info["instance"]
            try:
                if hasattr(va_instance, "receive_voice_message"):
                    va_instance.receive_voice_message(message)
            except Exception as e:
                logger.warning(f"⚠️  Error delivering message to {to_va}: {e}")
        elif to_va is None:
            # Broadcast to all VAs
            for va_name, va_info in self.vas.items():
                if va_name != from_va:
                    va_instance = va_info["instance"]
                    try:
                        if hasattr(va_instance, "receive_voice_message"):
                            va_instance.receive_voice_message(message)
                    except Exception as e:
                        logger.warning(f"⚠️  Error broadcasting to {va_name}: {e}")

        logger.info(f"📨 Voice message: {from_va} → {to_va or 'ALL'}: {text[:50]}...")
        return message_id

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "voice_mode_active": self.voice_mode_active,
            "registered_vas": list(self.vas.keys()),
            "current_speaker": self.current_speaker,
            "listening_vas": {k: v for k, v in self.listening_vas.items() if v},
            "queue_size": self.voice_queue.qsize(),
            "tts_systems": list(self.tts_systems.keys()),
            "voice_recognition_available": self.recognizer is not None
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="VA Full Voice Mode System")
    parser.add_argument("--start", action="store_true", help="Start full voice mode")
    parser.add_argument("--stop", action="store_true", help="Stop full voice mode")
    parser.add_argument("--status", action="store_true", help="Show status")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    system = VAFullVoiceModeSystem(project_root)

    if args.start:
        system.start_full_voice_mode()
        print("✅ Full voice mode started")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            system.stop_full_voice_mode()
            print("✅ Full voice mode stopped")
    elif args.stop:
        system.stop_full_voice_mode()
        print("✅ Full voice mode stopped")
    elif args.status:
        status = system.get_status()
        print(json.dumps(status, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":


    main()