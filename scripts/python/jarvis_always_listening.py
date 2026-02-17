#!/usr/bin/env python3
"""
JARVIS Always-Listening Mode

Continuously open microphone that transcribes everything you say.
No button press, no wake word - just speak and JARVIS listens.

Features:
- Continuous speech recognition
- Real-time transcription
- Automatic command detection
- Voice response
- Hands-free operation
"""

import sys
import os
import threading
import queue
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, List
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAlwaysListening")

# Azure Speech SDK
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    AZURE_SPEECH_AVAILABLE = False
    speechsdk = None
    logger.error("❌ Azure Speech SDK not available - install: pip install azure-cognitiveservices-speech")


class JARVISAlwaysListening:
    """
    Always-listening voice interface for JARVIS

    Keeps microphone continuously open, transcribes speech in real-time,
    and processes commands hands-free.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize always-listening system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Azure Speech credentials
        self.azure_speech_key = self._get_azure_speech_key()
        self.azure_speech_region = self._get_azure_speech_region()

        # State
        self.running = False
        self.is_speaking = False
        self.continuous_recognizer = None

        # Trigger word detection
        self.trigger_word = "jarvis"
        self.waiting_for_trigger = True  # Start by waiting for trigger word
        self.trigger_detected = False
        self.command_buffer: List[str] = []  # Buffer commands after trigger

        # Transcription queue
        self.transcription_queue = queue.Queue()

        # Callbacks
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_command: Optional[Callable[[str], str]] = None

        # History
        self.transcription_history: List[dict] = []

        # Initialize Azure Speech
        self._initialize_azure_speech()

        logger.info("🎤 JARVIS Always-Listening initialized")
        logger.info("   Mode: Continuous speech recognition")
        logger.info("   Mic: Always open")

    def _get_azure_speech_key(self) -> Optional[str]:
        """Get Azure Speech key from Key Vault or env"""
        try:
            from azure_service_bus_integration import AzureKeyVaultClient
            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
            vault_client = AzureKeyVaultClient(vault_url=vault_url)
            return vault_client.get_secret("azure-speech-key")
        except Exception:
            return os.getenv("AZURE_SPEECH_KEY")

    def _get_azure_speech_region(self) -> Optional[str]:
        """Get Azure Speech region from Key Vault or env"""
        try:
            from azure_service_bus_integration import AzureKeyVaultClient
            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
            vault_client = AzureKeyVaultClient(vault_url=vault_url)
            return vault_client.get_secret("azure-speech-region")
        except Exception:
            return os.getenv("AZURE_SPEECH_REGION", "eastus")

    def _initialize_azure_speech(self):
        """Initialize Azure Speech SDK for continuous recognition"""
        if not AZURE_SPEECH_AVAILABLE:
            logger.error("❌ Azure Speech SDK not available")
            return False

        if not self.azure_speech_key:
            logger.error("❌ Azure Speech key not found")
            return False

        try:
            # Speech configuration
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_speech_key,
                region=self.azure_speech_region
            )

            # Configure for continuous recognition
            self.speech_config.speech_recognition_language = "en-US"
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, 
                "10000"  # 10 seconds initial silence timeout
            )
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
                "2000"  # 2 seconds end silence timeout
            )

            # Enable dictation mode for better continuous recognition
            self.speech_config.enable_dictation()

            # TTS configuration
            self.speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

            # Audio configuration (default microphone)
            self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

            # Create continuous speech recognizer
            self.continuous_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=self.audio_config
            )

            # Speech synthesizer for responses
            self.speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None  # Default speaker
            )

            # Connect event handlers
            self._connect_event_handlers()

            logger.info("✅ Azure Speech SDK initialized for continuous recognition")
            logger.info(f"   Region: {self.azure_speech_region}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure Speech SDK: {e}")
            return False

    def _connect_event_handlers(self):
        try:
            """Connect event handlers for continuous recognition"""
            if not self.continuous_recognizer:
                return

            # Recognition started
            def on_session_started(evt):
                logger.info("🎤 Listening session started - mic is open")

            # Recognition stopped
            def on_session_stopped(evt):
                logger.info("🔇 Listening session stopped")

            # Recognizing (interim results)
            def on_recognizing(evt):
                if evt.result.text:
                    logger.debug(f"   [recognizing] {evt.result.text}")

            # Recognized (final result)
            def on_recognized(evt):
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    text = evt.result.text.strip()
                    if text:
                        self._handle_transcription(text)
                elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                    logger.debug("   [no match]")

            # Canceled
            def on_canceled(evt):
                if evt.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"❌ Recognition error: {evt.error_details}")
                elif evt.reason == speechsdk.CancellationReason.EndOfStream:
                    logger.info("   [end of stream]")

            # Connect handlers
            self.continuous_recognizer.session_started.connect(on_session_started)
            self.continuous_recognizer.session_stopped.connect(on_session_stopped)
            self.continuous_recognizer.recognizing.connect(on_recognizing)
            self.continuous_recognizer.recognized.connect(on_recognized)
            self.continuous_recognizer.canceled.connect(on_canceled)

        except Exception as e:
            self.logger.error(f"Error in _connect_event_handlers: {e}", exc_info=True)
            raise
    def _handle_transcription(self, text: str):
        """Handle transcribed text with trigger word detection"""
        timestamp = datetime.now()
        text_lower = text.lower().strip()

        # Check for trigger word "jarvis"
        if self.waiting_for_trigger:
            # Look for trigger word in the transcription
            if self.trigger_word.lower() in text_lower:
                self.waiting_for_trigger = False
                self.trigger_detected = True
                self.command_buffer = []

                # Remove trigger word from text to get the actual command
                command_text = text_lower.replace(self.trigger_word.lower(), "", 1).strip()

                logger.info(f"🎯 Trigger word detected: \"{self.trigger_word}\"")

                if command_text:
                    # Command was part of the same transcription
                    self._process_command(command_text)
                else:
                    # Just the trigger word, wait for next transcription
                    logger.info("   Waiting for command after trigger...")

                # Store in history
                self.transcription_history.append({
                    "text": text,
                    "timestamp": timestamp.isoformat(),
                    "speaker": "human",
                    "trigger_detected": True
                })
                return

        # Not waiting for trigger - process as command
        if not self.waiting_for_trigger:
            # Check for stop commands that should reset to waiting mode
            # Use word boundaries to avoid false matches in legitimate commands
            # Only match if the stop phrase is at the start or end, or as a complete phrase
            stop_phrases = [
                r"^(stop|cancel|done|never mind|that's all)$",  # Exact match
                r"^(stop|cancel|done|never mind|that's all)\s",  # At start
                r"\s(stop|cancel|done|never mind|that's all)$",  # At end
                r"^stop listening$",  # Specific stop command
                r"^cancel that$",  # Specific cancel command
                r"^that's all$",  # Specific completion phrase
            ]

            import re
            is_stop_command = False
            for pattern in stop_phrases:
                if re.match(pattern, text_lower.strip()):
                    is_stop_command = True
                    break

            # Also check for specific unambiguous stop phrases
            if not is_stop_command:
                explicit_stop_phrases = [
                    "stop listening",
                    "that's all",
                    "never mind",
                    "cancel that",
                    "done talking",
                    "finished talking"
                ]
                is_stop_command = any(text_lower.strip() == phrase or text_lower.strip().startswith(phrase + " ") for phrase in explicit_stop_phrases)

            if is_stop_command:
                logger.info("🔄 Command complete - returning to trigger word mode")
                self.waiting_for_trigger = True
                self.trigger_detected = False
                self.command_buffer = []
                return

            # Process as command
            self._process_command(text)
        else:
            # Waiting for trigger but didn't detect it - just log
            logger.debug(f"🔇 Listening (waiting for '{self.trigger_word}')...")

    def _process_command(self, text: str):
        """Process a command after trigger word detection"""
        timestamp = datetime.now()

        # Log transcription
        logger.info(f"🗣️  Command: \"{text}\"")

        # Store in history
        self.transcription_history.append({
            "text": text,
            "timestamp": timestamp.isoformat(),
            "speaker": "human",
            "command": True
        })

        # Add to queue
        self.transcription_queue.put(text)

        # Call transcription callback
        if self.on_transcription:
            self.on_transcription(text)

        # Check if it's a command and process
        if self.on_command:
            response = self.on_command(text)
            if response:
                self.speak(response)

        # After processing, return to waiting for trigger
        # IMPORTANT: This must be outside the on_command block so trigger state
        # resets even when no command handler is registered
        self.waiting_for_trigger = True
        self.trigger_detected = False
        logger.info(f"✅ Ready - waiting for '{self.trigger_word}' trigger word")

    def speak(self, text: str) -> bool:
        """Speak text using TTS"""
        if not self.speech_synthesizer:
            logger.warning("⚠️  Speech synthesizer not available")
            return False

        self.is_speaking = True
        logger.info(f"🔊 JARVIS: \"{text}\"")

        try:
            # Store in history
            self.transcription_history.append({
                "text": text,
                "timestamp": datetime.now().isoformat(),
                "speaker": "jarvis"
            })

            # Speak
            result = self.speech_synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self.is_speaking = False
                return True
            else:
                logger.error(f"❌ TTS failed: {result.reason}")
                self.is_speaking = False
                return False

        except Exception as e:
            logger.error(f"❌ TTS error: {e}")
            self.is_speaking = False
            return False

    def start(self):
        """Start always-listening mode"""
        if self.running:
            logger.warning("⚠️  Already listening")
            return

        if not self.continuous_recognizer:
            logger.error("❌ Continuous recognizer not initialized")
            return

        logger.info("🎤 Starting always-listening mode with trigger word...")
        logger.info(f"   Listening for trigger word: '{self.trigger_word}'")
        logger.info(f"   Say '{self.trigger_word}' followed by your command")
        logger.info("   Say 'stop listening' or 'goodbye' to stop")

        self.running = True

        # Start continuous recognition
        self.continuous_recognizer.start_continuous_recognition_async()

        logger.info("✅ Microphone is now always open")

    def stop(self):
        """Stop always-listening mode"""
        if not self.running:
            return

        logger.info("🔇 Stopping always-listening mode...")

        self.running = False

        if self.continuous_recognizer:
            self.continuous_recognizer.stop_continuous_recognition_async()

        logger.info("✅ Microphone closed")

    def get_transcription(self, timeout: float = None) -> Optional[str]:
        """Get next transcription from queue"""
        try:
            return self.transcription_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def set_command_handler(self, handler: Callable[[str], str]):
        """Set command handler callback"""
        self.on_command = handler

    def set_transcription_handler(self, handler: Callable[[str], None]):
        """Set transcription callback"""
        self.on_transcription = handler


def main():
    """Main entry point"""
    print("="*70)
    print("🎤 JARVIS Always-Listening Mode")
    print("="*70)
    print()
    print("Microphone will be always open, listening for trigger word: 'jarvis'")
    print("Say 'jarvis' followed by your command to activate JARVIS.")
    print("Example: 'jarvis, what time is it?'")
    print()
    print("Say 'stop listening' or press Ctrl+C to stop.")
    print()

    # Initialize
    listener = JARVISAlwaysListening()

    # Try to integrate with hands-free control
    try:
        from jarvis_hands_free_cursor_control import JARVISHandsFreeCursorControl
        hands_free = JARVISHandsFreeCursorControl()

        def handle_command(text: str) -> str:
            """Handle voice command"""
            text_lower = text.lower()

            # Stop commands
            if any(phrase in text_lower for phrase in ["stop listening", "goodbye jarvis", "exit", "goodbye"]):
                listener.stop()
                return "Goodbye!"

            # Process through hands-free control
            result = hands_free.process_voice_command(text)
            return result.get("response", "Got it.")

        listener.set_command_handler(handle_command)
        print("✅ Hands-free Cursor control: Enabled")

    except Exception as e:
        print(f"⚠️  Hands-free control not available: {e}")

        # Basic command handler
        def handle_command(text: str) -> str:
            text_lower = text.lower()
            if any(phrase in text_lower for phrase in ["stop listening", "goodbye", "exit", "goodbye jarvis"]):
                listener.stop()
                return "Goodbye!"
            return "Command received."  # Acknowledge command

        listener.set_command_handler(handle_command)

    # Start listening
    listener.start()

    # Keep running
    try:
        while listener.running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n")
        listener.stop()

    print()
    print("👋 Bye!")


if __name__ == "__main__":


    main()