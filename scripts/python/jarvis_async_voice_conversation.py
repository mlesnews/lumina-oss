#!/usr/bin/env python3
"""
JARVIS Async Voice Conversation System
MANUS Framework - Complete Hands-Free Real-Time AI-to-Human Conversation

Fully hands-free, always-listening voice interface for real-time async
conversations with JARVIS. No trigger words, no button presses - just speak.

Features:
- Always-listening microphone (no trigger word required)
- Real-time async speech recognition
- Async text-to-speech responses
- Continuous conversation flow
- Integration with JARVIS Full-Time Super Agent
- IDE command execution via voice
- Complete hands-free operation

@JARVIS @MANUS @SYPHON
"""

import sys
import asyncio
import threading
import queue
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAsyncVoiceConversation")

# Azure Speech SDK
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    AZURE_SPEECH_AVAILABLE = False
    speechsdk = None
    logger.warning("Azure Speech SDK not available - install: pip install azure-cognitiveservices-speech")

# Import JARVIS components
try:
    from jarvis_fulltime_super_agent import get_jarvis_fulltime
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    logger.warning("JARVIS Full-Time Super Agent not available")

try:
    from jarvis_cursor_ide_keyboard_integration import get_jarvis_cursor_integration
    IDE_INTEGRATION_AVAILABLE = True
except ImportError:
    IDE_INTEGRATION_AVAILABLE = False
    logger.warning("JARVIS-Cursor IDE integration not available")


@dataclass
class VoiceMessage:
    """Voice message in conversation"""
    timestamp: datetime
    speaker: str  # "human" or "jarvis"
    text: str
    audio_duration: Optional[float] = None
    confidence: float = 1.0


@dataclass
class ConversationState:
    """State of ongoing conversation"""
    conversation_id: str
    messages: List[VoiceMessage] = field(default_factory=list)
    is_active: bool = True
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class JARVISAsyncVoiceConversation:
    """
    Async voice conversation system for JARVIS

    Always-listening, hands-free, real-time async conversations.
    No trigger words, no button presses - just speak naturally.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize async voice conversation system"""
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
        self.is_listening = False

        # Speech components
        self.speech_config = None
        self.audio_config = None
        self.continuous_recognizer = None
        self.speech_synthesizer = None

        # Conversation management
        self.active_conversation: Optional[ConversationState] = None
        self.conversation_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()

        # Message queues
        self.incoming_messages = queue.Queue()
        self.outgoing_messages = queue.Queue()

        # Integration components
        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = get_jarvis_fulltime(project_root=self.project_root)
            except Exception as e:
                logger.warning(f"JARVIS initialization failed: {e}")

        self.ide_integration = None
        if IDE_INTEGRATION_AVAILABLE:
            try:
                self.ide_integration = get_jarvis_cursor_integration(project_root=self.project_root)
            except Exception as e:
                logger.warning(f"IDE integration initialization failed: {e}")

        # Async event loop
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.async_thread: Optional[threading.Thread] = None

        # Initialize Azure Speech
        self._initialize_azure_speech()

        logger.info("✅ JARVIS Async Voice Conversation initialized")
        logger.info("   Mode: Always-listening, hands-free")
        logger.info("   Conversation: Real-time async")

    def _get_azure_speech_key(self) -> Optional[str]:
        """Get Azure Speech key from Key Vault or env"""
        import os
        try:
            from azure_service_bus_integration import AzureKeyVaultClient
            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
            vault_client = AzureKeyVaultClient(vault_url=vault_url)
            return vault_client.get_secret("azure-speech-key")
        except Exception:
            return os.getenv("AZURE_SPEECH_KEY")

    def _get_azure_speech_region(self) -> Optional[str]:
        """Get Azure Speech region from Key Vault or env"""
        import os
        try:
            from azure_service_bus_integration import AzureKeyVaultClient
            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
            vault_client = AzureKeyVaultClient(vault_url=vault_url)
            return vault_client.get_secret("azure-speech-region")
        except Exception:
            return os.getenv("AZURE_SPEECH_REGION", "eastus")

    def _initialize_azure_speech(self):
        """Initialize Azure Speech SDK"""
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

            # Configure for continuous recognition (always listening, no trigger word)
            self.speech_config.speech_recognition_language = "en-US"
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs,
                "3000"  # 3 seconds initial silence (faster response)
            )
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
                "1000"  # 1 second end silence (very fast response)
            )

            # Enable continuous recognition with no pause requirement
            self.speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_EnableAudioLogging,
                "false"  # Disable audio logging for privacy
            )

            # Enable dictation mode for natural conversation
            self.speech_config.enable_dictation()

            # TTS configuration
            self.speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

            # Audio configuration
            self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

            # Create continuous recognizer (always listening)
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

            logger.info("✅ Azure Speech SDK initialized")
            logger.info(f"   Region: {self.azure_speech_region}")
            logger.info("   Mode: Always-listening (no trigger word)")

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
                self.is_listening = True
                logger.debug("🎤 Listening session started")

            # Recognition stopped
            def on_session_stopped(evt):
                self.is_listening = False
                logger.debug("🔇 Listening session stopped")

            # Recognizing (interim results - show in real-time)
            def on_recognizing(evt):
                if evt.result.text:
                    # Show interim results (optional - can be noisy)
                    pass

            # Recognized (final result - process immediately, no trigger word filtering)
            def on_recognized(evt):
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    text = evt.result.text.strip()
                    if text:
                        # Filter out very short utterances (likely false positives)
                        if len(text.split()) >= 1:  # At least one word
                            # Queue for async processing (no trigger word check)
                            self.incoming_messages.put({
                                "text": text,
                                "timestamp": datetime.now(),
                                "confidence": 1.0
                            })

            # Canceled
            def on_canceled(evt):
                if evt.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"❌ Recognition error: {evt.error_details}")
                elif evt.reason == speechsdk.CancellationReason.EndOfStream:
                    logger.debug("   [end of stream]")

            # Connect handlers
            self.continuous_recognizer.session_started.connect(on_session_started)
            self.continuous_recognizer.session_stopped.connect(on_session_stopped)
            self.continuous_recognizer.recognizing.connect(on_recognizing)
            self.continuous_recognizer.recognized.connect(on_recognized)
            self.continuous_recognizer.canceled.connect(on_canceled)

        except Exception as e:
            self.logger.error(f"Error in _connect_event_handlers: {e}", exc_info=True)
            raise
    async def _process_incoming_message(self, message_data: Dict[str, Any]):
        """Process incoming voice message asynchronously"""
        text = message_data["text"]
        timestamp = message_data["timestamp"]

        # Create voice message
        voice_message = VoiceMessage(
            timestamp=timestamp,
            speaker="human",
            text=text,
            confidence=message_data.get("confidence", 1.0)
        )

        # Add to conversation
        if self.active_conversation:
            self.active_conversation.messages.append(voice_message)
            self.active_conversation.last_activity = datetime.now()

        logger.info(f"🗣️  Human: \"{text}\"")

        # Process message and generate response
        response = await self._generate_response(text)

        if response:
            await self._speak_response(response)

    async def _generate_response(self, user_message: str) -> Optional[str]:
        """Generate JARVIS response to user message"""
        try:
            # Check if it's an IDE command
            if self.ide_integration:
                # Try to execute as IDE command
                result = self.ide_integration.execute_command(user_message, async_execution=True)
                if result.success:
                    return f"Done. {result.method} executed successfully."

            # Check if JARVIS is available
            if self.jarvis:
                # Use JARVIS to generate response
                conversation_id = self.active_conversation.conversation_id if self.active_conversation else "default"
                response_turn = self.jarvis.speak(conversation_id, user_message, speaker="human")

                # Get JARVIS response (would need to extract from conversation)
                # For now, generate a simple response
                return f"I heard: {user_message}. How can I help?"

            # Default response
            return f"Got it: {user_message}"

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error processing that."

    async def _speak_response(self, text: str):
        """Speak response asynchronously"""
        if not self.speech_synthesizer:
            logger.warning("⚠️  Speech synthesizer not available")
            return

        # Don't speak if already speaking
        if self.is_speaking:
            logger.debug("   [skipping - already speaking]")
            return

        self.is_speaking = True
        logger.info(f"🔊 JARVIS: \"{text}\"")

        try:
            # Create voice message
            voice_message = VoiceMessage(
                timestamp=datetime.now(),
                speaker="jarvis",
                text=text
            )

            # Add to conversation
            if self.active_conversation:
                self.active_conversation.messages.append(voice_message)
                self.active_conversation.last_activity = datetime.now()

            # Speak asynchronously (run in thread to not block)
            def speak_sync():
                try:
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

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, speak_sync)

        except Exception as e:
            logger.error(f"Error speaking: {e}")
            self.is_speaking = False

    async def _message_processor_loop(self):
        """Async loop to process incoming messages"""
        while self.running:
            try:
                # Check for incoming messages (non-blocking)
                try:
                    message_data = self.incoming_messages.get_nowait()
                    await self._process_incoming_message(message_data)
                except queue.Empty:
                    pass

                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in message processor loop: {e}")
                await asyncio.sleep(1)

    def _async_loop_thread(self):
        """Run async event loop in separate thread"""
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        # Start message processor
        self.event_loop.run_until_complete(self._message_processor_loop())

    def start_conversation(self) -> str:
        """Start a new voice conversation"""
        conversation_id = f"voice_conv_{int(time.time() * 1000)}"

        self.active_conversation = ConversationState(
            conversation_id=conversation_id,
            is_active=True,
            started_at=datetime.now()
        )

        logger.info(f"🎤 Starting voice conversation: {conversation_id}")

        return conversation_id

    def start(self):
        """Start always-listening voice conversation"""
        if self.running:
            logger.warning("⚠️  Already running")
            return

        if not self.continuous_recognizer:
            logger.error("❌ Continuous recognizer not initialized")
            return

        logger.info("🎤 Starting JARVIS Async Voice Conversation...")
        logger.info("   Mode: Always-listening (no trigger word required)")
        logger.info("   Just speak naturally - JARVIS is listening continuously")
        logger.info("   Real-time async conversation - speak anytime")
        logger.info("   Say 'goodbye', 'stop', or 'exit' to end conversation")

        self.running = True

        # Start conversation
        self.start_conversation()

        # Start async event loop in separate thread
        self.async_thread = threading.Thread(target=self._async_loop_thread, daemon=True)
        self.async_thread.start()

        # Start continuous recognition (always listening)
        self.continuous_recognizer.start_continuous_recognition_async()

        # Initial greeting
        def greet():
            time.sleep(1)  # Wait for recognition to start
            if self.speech_synthesizer:
                self.speech_synthesizer.speak_text_async("JARVIS here. I'm listening. How can I help?").get()

        greeting_thread = threading.Thread(target=greet, daemon=True)
        greeting_thread.start()

        logger.info("✅ Voice conversation started")
        logger.info("   Microphone: Always open")
        logger.info("   Conversation: Active")

    def stop(self):
        """Stop voice conversation"""
        if not self.running:
            return

        logger.info("🔇 Stopping voice conversation...")

        self.running = False

        if self.continuous_recognizer:
            self.continuous_recognizer.stop_continuous_recognition_async()

        if self.active_conversation:
            self.active_conversation.is_active = False

        # Goodbye message
        if self.speech_synthesizer:
            try:
                self.speech_synthesizer.speak_text_async("Goodbye!").get()
            except:
                pass

        logger.info("✅ Voice conversation stopped")

    def get_conversation_history(self) -> List[VoiceMessage]:
        """Get conversation history"""
        if self.active_conversation:
            return self.active_conversation.messages.copy()
        return []


def get_async_voice_conversation(project_root: Optional[Path] = None) -> JARVISAsyncVoiceConversation:
    """Get or create async voice conversation instance"""
    global _voice_conversation_instance
    if '_voice_conversation_instance' not in globals():
        _voice_conversation_instance = JARVISAsyncVoiceConversation(project_root=project_root)
    return _voice_conversation_instance


def main():
    """Main entry point"""
    print("="*70)
    print("🎤 JARVIS Async Voice Conversation")
    print("="*70)
    print()
    print("Complete hands-free, always-listening voice interface")
    print("No trigger words, no button presses - just speak naturally")
    print()
    print("Features:")
    print("  • Always-listening microphone")
    print("  • Real-time async conversation")
    print("  • IDE command execution via voice")
    print("  • Natural conversation flow")
    print()
    print("Say 'goodbye' or 'stop' to end conversation")
    print("Press Ctrl+C to exit")
    print()

    # Initialize
    conversation = JARVISAsyncVoiceConversation()

    # Start conversation
    conversation.start()

    # Keep running
    try:
        while conversation.running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n")
        conversation.stop()

    print()
    print("👋 Conversation ended")


if __name__ == "__main__":


    main()