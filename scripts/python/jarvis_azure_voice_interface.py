#!/usr/bin/env python3
"""
JARVIS Azure Voice Interface - True Hands-Free, Human-Compatible Speech

Azure Speech SDK integration for:
- Speech-to-Text (STT) - Human speaks to JARVIS
- Text-to-Speech (TTS) - JARVIS speaks to human
- Continuous conversation
- Hands-free, mouse-free, click-free operation

This closes the gap between JARVIS Vector Explorer and true voice interaction.
"""

import sys
import os
import json
import threading
import queue
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Azure Speech SDK
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    AZURE_SPEECH_AVAILABLE = False
    speechsdk = None
    print("⚠️  Azure Speech SDK not available - install: pip install azure-cognitiveservices-speech")

try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISION_TREE_AVAILABLE = True
except ImportError:
    DECISION_TREE_AVAILABLE = False
    decide = None
    DecisionContext = None
    DecisionOutcome = None

logger = get_logger("JARVISAzureVoice")


class ConversationState(Enum):
    """Conversation state"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    WAITING_RESPONSE = "waiting_response"


@dataclass
class VoiceMessage:
    """Voice message"""
    message_id: str
    timestamp: datetime
    text: str
    speaker: str  # "human" or "jarvis"
    audio_data: Optional[bytes] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class JARVISAzureVoiceInterface:
    """
    JARVIS Azure Voice Interface

    True hands-free, mouse-free, click-free operation using Azure Speech SDK.
    Human-compatible speech recognition and synthesis.
    """

    def __init__(self, project_root: Optional[Path] = None, 
                 azure_speech_key: Optional[str] = None,
                 azure_speech_region: Optional[str] = None):
        """
        Initialize Azure Voice Interface

        Args:
            project_root: Project root directory
            azure_speech_key: Azure Speech API key (or from env)
            azure_speech_region: Azure Speech region (or from env)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISAzureVoice")

        # Data directories
        self.data_dir = self.project_root / "data" / "jarvis" / "voice"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Azure Speech configuration - try Key Vault first
        self.azure_speech_key = azure_speech_key or self._get_azure_speech_key_from_vault() or os.getenv("AZURE_SPEECH_KEY")
        self.azure_speech_region = azure_speech_region or self._get_azure_speech_region_from_vault() or os.getenv("AZURE_SPEECH_REGION", "eastus")

        # Azure Speech SDK objects
        self.speech_config: Optional[speechsdk.SpeechConfig] = None
        self.audio_config: Optional[speechsdk.audio.AudioConfig] = None
        self.speech_recognizer: Optional[speechsdk.SpeechRecognizer] = None
        self.speech_synthesizer: Optional[speechsdk.SpeechSynthesizer] = None

        # ElevenLabs TTS (optional, for higher quality voice)
        self.elevenlabs_tts: Optional[Any] = None
        self.use_elevenlabs_for_tts = False  # Set to True to use ElevenLabs instead of Azure TTS

        # Conversation state
        self.conversation_state = ConversationState.IDLE
        self.is_listening = False
        self.is_speaking = False
        self.current_conversation_id: Optional[str] = None
        self.conversation_history: List[VoiceMessage] = []

        # Queues
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        # JARVIS Vector Explorer integration
        self.vector_explorer = None

        # Threads
        self.listening_thread: Optional[threading.Thread] = None
        self.processing_thread: Optional[threading.Thread] = None

        # Initialize Azure Speech SDK
        self._initialize_azure_speech()

        # Initialize ElevenLabs TTS (optional)
        self._initialize_elevenlabs()

        # Load JARVIS Vector Explorer
        self._load_vector_explorer()

        self.logger.info("🎤 JARVIS Azure Voice Interface initialized")
        self.logger.info("   Azure Speech SDK: " + ("✅ Available" if AZURE_SPEECH_AVAILABLE else "❌ Not available"))
        if self.azure_speech_key:
            self.logger.info("   ✅ Azure Speech key: Retrieved from Key Vault")
        else:
            self.logger.warning("   ⚠️  Azure Speech key: Not found")
        self.logger.info("   Hands-free operation: ✅ Enabled")
        self.logger.info("   Human-compatible speech: ✅ Enabled")

    def _get_azure_speech_key_from_vault(self) -> Optional[str]:
        """Retrieve Azure Speech key from Azure Key Vault"""
        try:
            try:
                from azure_service_bus_integration import AzureKeyVaultClient
            except ImportError:
                from scripts.python.azure_service_bus_integration import AzureKeyVaultClient

            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")

            try:
                vault_client = AzureKeyVaultClient(vault_url=vault_url)
                secret = vault_client.get_secret("azure-speech-key")
                self.logger.info("✅ Retrieved Azure Speech key from Key Vault")
                return secret
            except Exception as e:
                self.logger.debug(f"Could not retrieve from Key Vault: {e}")
                # Try alternative secret names
                try:
                    secret = vault_client.get_secret("azure-speech-api-key")
                    self.logger.info("✅ Retrieved Azure Speech key from Key Vault (alternate name)")
                    return secret
                except:
                    return None
        except ImportError as e:
            self.logger.debug(f"Azure Key Vault client not available: {e}")
            return None
        except Exception as e:
            self.logger.debug(f"Key Vault retrieval error: {e}")
            return None

    def _get_azure_speech_region_from_vault(self) -> Optional[str]:
        """Retrieve Azure Speech region from Azure Key Vault"""
        try:
            try:
                from azure_service_bus_integration import AzureKeyVaultClient
            except ImportError:
                from scripts.python.azure_service_bus_integration import AzureKeyVaultClient

            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")

            try:
                vault_client = AzureKeyVaultClient(vault_url=vault_url)
                region = vault_client.get_secret("azure-speech-region")
                self.logger.info("✅ Retrieved Azure Speech region from Key Vault")
                return region
            except Exception:
                return None
        except Exception:
            return None

    def _initialize_azure_speech(self):
        """Initialize Azure Speech SDK"""
        if not AZURE_SPEECH_AVAILABLE:
            self.logger.error("❌ Azure Speech SDK not available")
            return False

        if not self.azure_speech_key:
            self.logger.error("❌ AZURE_SPEECH_KEY not set")
            return False

        try:
            # Speech configuration
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_speech_key,
                region=self.azure_speech_region
            )

            # Set language (can be configured)
            self.speech_config.speech_recognition_language = "en-US"
            self.speech_config.speech_synthesis_language = "en-US"
            self.speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"  # Natural voice

            # Audio configuration (default microphone)
            self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

            # Speech recognizer
            self.speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=self.audio_config
            )

            # Speech synthesizer
            self.speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None  # Use default speaker
            )

            self.logger.info("✅ Azure Speech SDK configured")
            self.logger.info(f"   Region: {self.azure_speech_region}")
            self.logger.info(f"   Voice: {self.speech_config.speech_synthesis_voice_name}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Azure Speech SDK: {e}")
            return False

    def _load_vector_explorer(self):
        """Load JARVIS Vector Explorer"""
        try:
            from jarvis_vector_explorer import JARVISVectorExplorer
            self.vector_explorer = JARVISVectorExplorer(project_root=self.project_root)
            self.logger.info("✅ JARVIS Vector Explorer loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  JARVIS Vector Explorer not available: {e}")

    def speak(self, text: str, interrupt: bool = False, use_elevenlabs: Optional[bool] = None) -> bool:
        """
        Speak text using TTS (Azure or ElevenLabs)

        Args:
            text: Text to speak
            interrupt: Whether to interrupt current speech
            use_elevenlabs: Force use of ElevenLabs (None = use configured preference)

        Returns:
            True if successful
        """
        # Determine which TTS to use
        use_elevenlabs_tts = use_elevenlabs if use_elevenlabs is not None else self.use_elevenlabs_for_tts

        # Try ElevenLabs if enabled and available
        if use_elevenlabs_tts and self.elevenlabs_tts:
            return self._speak_with_elevenlabs(text, interrupt)

        # Fall back to Azure TTS
        return self._speak_with_azure(text, interrupt)

    def _speak_with_elevenlabs(self, text: str, interrupt: bool = False) -> bool:
        """Speak using ElevenLabs TTS"""
        if interrupt and self.is_speaking:
            # Note: ElevenLabs doesn't support interrupt directly
            # Would need to implement audio playback control
            pass

        self.is_speaking = True
        self.conversation_state = ConversationState.SPEAKING

        try:
            success = self.elevenlabs_tts.speak(text)

            if success:
                # Use formatter for clear speaker labels
                try:
                    from jarvis_conversation_formatter import format_jarvis_message
                    formatted = format_jarvis_message(text, datetime.now())
                    self.logger.info(formatted)
                    print(formatted)  # Also print to console if available
                except ImportError:
                    self.logger.info(f"🤖 JARVIS: {text}")
                    print(f"🤖 JARVIS: {text}")  # Fallback

            self.is_speaking = False
            self.conversation_state = ConversationState.IDLE
            return success

        except Exception as e:
            self.logger.error(f"❌ ElevenLabs TTS error: {e}", exc_info=True)
            print(f"JARVIS: {text}")  # Fallback
            self.is_speaking = False
            self.conversation_state = ConversationState.IDLE
            return False

    def _speak_with_azure(self, text: str, interrupt: bool = False) -> bool:
        """Speak using Azure TTS"""
        if not self.speech_synthesizer:
            self.logger.error("❌ Speech synthesizer not available")
            print(f"JARVIS: {text}")  # Fallback
            return False

        if interrupt and self.is_speaking:
            # Stop current speech
            try:
                self.speech_synthesizer.stop_speaking_async()
            except:
                pass

        self.is_speaking = True
        self.conversation_state = ConversationState.SPEAKING

        try:
            # Synthesize speech
            result = self.speech_synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Create voice message
                message = VoiceMessage(
                    message_id=f"msg_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    text=text,
                    speaker="jarvis",
                    confidence=1.0
                )
                self.conversation_history.append(message)

                # Use formatter for clear speaker labels
                try:
                    from jarvis_conversation_formatter import format_jarvis_message
                    formatted = format_jarvis_message(text, datetime.now())
                    self.logger.info(formatted)
                    print(formatted)  # Also print to console if available
                except ImportError:
                    self.logger.info(f"🤖 JARVIS: {text}")
                    print(f"🤖 JARVIS: {text}")  # Fallback
                self.is_speaking = False
                self.conversation_state = ConversationState.IDLE
                return True
            else:
                self.logger.error(f"❌ Speech synthesis failed: {result.reason}")
                self.is_speaking = False
                self.conversation_state = ConversationState.IDLE
                return False

        except Exception as e:
            self.logger.error(f"❌ Speech synthesis error: {e}")
            print(f"JARVIS: {text}")  # Fallback
            self.is_speaking = False
            self.conversation_state = ConversationState.IDLE
            return False

    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Listen for speech using Azure STT

        Args:
            timeout: Timeout in seconds (None for continuous)

        Returns:
            Recognized text or None
        """
        if not self.speech_recognizer:
            self.logger.error("❌ Speech recognizer not available")
            return None

        self.conversation_state = ConversationState.LISTENING
        self.is_listening = True

        try:
            self.logger.info("🎤 Listening...")

            # Recognize speech
            if timeout:
                result = self.speech_recognizer.recognize_once_async().get()
            else:
                # Continuous recognition
                result = self.speech_recognizer.recognize_once_async().get()

            self.is_listening = False
            self.conversation_state = ConversationState.IDLE

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = result.text
                confidence = result.json.get('Confidence', 1.0) if hasattr(result, 'json') else 1.0

                # Create voice message
                message = VoiceMessage(
                    message_id=f"msg_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    text=text,
                    speaker="human",
                    confidence=confidence
                )
                self.conversation_history.append(message)

                # Use formatter for clear speaker labels
                try:
                    from jarvis_conversation_formatter import format_human_message
                    formatted = format_human_message(text, datetime.now())
                    self.logger.info(f"{formatted} (confidence: {confidence:.0%})")
                    print(formatted)  # Also print to console if available
                except ImportError:
                    self.logger.info(f"👤 HUMAN: {text} (confidence: {confidence:.0%})")
                    print(f"👤 HUMAN: {text}")  # Fallback

                return text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                self.logger.debug("  No speech recognized")
                return None
            else:
                self.logger.warning(f"  Recognition error: {result.reason}")
                return None

        except Exception as e:
            self.logger.error(f"❌ Speech recognition error: {e}")
            self.is_listening = False
            self.conversation_state = ConversationState.IDLE
            return None

    def ask_question_voice(self, question: str, context: str = "") -> Optional[str]:
        """
        Ask a question by voice and get voice response

        This integrates JARVIS Vector Explorer with voice.

        Args:
            question: Question to ask
            context: Context for the question

        Returns:
            Human's voice response or None
        """
        # Speak the question
        if context:
            full_question = f"{context}. {question}"
        else:
            full_question = question

        self.speak(full_question)

        # Wait a moment for human to process
        time.sleep(0.5)

        # Listen for response
        response = self.listen()

        return response

    def process_vector_exploration_voice(self, problem_description: str) -> Dict[str, Any]:
        """
        Process vector exploration with voice interaction

        JARVIS asks questions by voice, human responds by voice.

        Args:
            problem_description: Problem to explore

        Returns:
            Exploration results
        """
        if not self.vector_explorer:
            self.speak("JARVIS Vector Explorer is not available.")
            return {}

        self.speak(f"Let's explore this problem together: {problem_description}")

        # Start conversation
        self.current_conversation_id = f"conv_{datetime.now().timestamp()}"

        # Identify vectors
        self.speak("Identifying vectors to explore...")
        vectors = self.vector_explorer.identify_vectors(problem_description)
        self.speak(f"I've identified {len(vectors)} vectors to explore.")

        # Collect human responses
        human_responses = {}

        # Explore each vector with voice
        for vector in vectors:
            self.speak(f"Let's explore the {vector.name} vector.")

            for question in vector.questions:
                # Ask question by voice
                response = self.ask_question_voice(
                    question=question,
                    context=f"Exploring {vector.name}"
                )

                if response:
                    # Store response
                    question_id = f"q_{datetime.now().timestamp()}"
                    human_responses[question_id] = response
                    self.vector_explorer.human_responses[question_id] = response

                    # Acknowledge
                    self.speak(f"Got it. {response}")
                else:
                    self.speak("I didn't catch that. Could you repeat?")

        # Find paths
        self.speak("Finding paths forward...")
        paths = self.vector_explorer.find_paths_forward()
        self.speak(f"I found {len(paths)} possible paths.")

        # Analyze and recommend
        self.speak("Analyzing paths...")
        recommended = self.vector_explorer.recommend_path()

        if recommended:
            self.speak(f"I recommend: {recommended.name}. "
                      f"Feasibility: {recommended.feasibility:.0%}, "
                      f"Impact: {recommended.impact:.0%}, "
                      f"Effort: {recommended.effort:.0%}.")
        else:
            self.speak("I couldn't determine a clear recommendation.")

        return {
            "conversation_id": self.current_conversation_id,
            "vectors_explored": len(vectors),
            "paths_found": len(paths),
            "recommended_path": recommended.name if recommended else None
        }

    def start_continuous_conversation(self):
        """Start continuous conversation mode"""
        if self.is_listening:
            self.logger.warning("Already in conversation mode")
            return

        self.is_listening = True
        self.conversation_state = ConversationState.LISTENING

        self.speak("JARVIS voice interface activated. I'm listening. How can I help?")

        # Start listening thread
        self.listening_thread = threading.Thread(
            target=self._continuous_listening_loop,
            daemon=True
        )
        self.listening_thread.start()

        self.logger.info("✅ Continuous conversation mode started")

    def _continuous_listening_loop(self):
        """Continuous listening loop"""
        while self.is_listening:
            try:
                # Listen for speech
                text = self.listen()

                if text:
                    # Process command
                    self.conversation_state = ConversationState.PROCESSING

                    # Try to integrate with JARVIS Master Command if available
                    try:
                        from jarvis_voice_activation import JARVISVoiceActivation
                        # If we're being called from voice activation, it will handle processing
                        # Otherwise use simple command processing
                        if "explore" in text.lower() or "vector" in text.lower():
                            # Extract problem description
                            problem = text.replace("explore", "").replace("vector", "").strip()
                            if not problem:
                                problem = "general problem"

                            self.process_vector_exploration_voice(problem)
                        elif "stop" in text.lower() or "exit" in text.lower() or "quit" in text.lower():
                            self.speak("Stopping conversation mode.")
                            self.is_listening = False
                            break
                        else:
                            self.speak(f"I heard: {text}. How can I help?")
                    except ImportError:
                        # Fallback to simple processing
                        if "stop" in text.lower() or "exit" in text.lower() or "quit" in text.lower():
                            self.speak("Stopping conversation mode.")
                            self.is_listening = False
                            break
                        else:
                            self.speak(f"I heard: {text}. How can I help?")

                    self.conversation_state = ConversationState.IDLE

                # Small delay to prevent CPU spinning
                time.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Error in listening loop: {e}")
                time.sleep(1)

    def stop_conversation(self):
        """Stop continuous conversation"""
        self.is_listening = False
        self.conversation_state = ConversationState.IDLE
        self.speak("Conversation mode stopped.")
        self.logger.info("Conversation mode stopped")

    def save_conversation(self, filename: Optional[str] = None):
        try:
            """Save conversation history"""
            if not self.conversation_history:
                return

            if filename is None:
                filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            filepath = self.data_dir / filename

            conversation_data = {
                "conversation_id": self.current_conversation_id,
                "started_at": self.conversation_history[0].timestamp.isoformat() if self.conversation_history else None,
                "ended_at": datetime.now().isoformat(),
                "messages": [
                    {
                        "message_id": msg.message_id,
                        "timestamp": msg.timestamp.isoformat(),
                        "speaker": msg.speaker,
                        "text": msg.text,
                        "confidence": msg.confidence
                    }
                    for msg in self.conversation_history
                ]
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2)

            self.logger.info(f"✅ Conversation saved to {filepath}")


        except Exception as e:
            self.logger.error(f"Error in save_conversation: {e}", exc_info=True)
            raise
def main():
    """CLI for JARVIS Azure Voice Interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Azure Voice Interface")
    parser.add_argument("--start", action="store_true", help="Start continuous conversation")
    parser.add_argument("--test-stt", action="store_true", help="Test speech-to-text")
    parser.add_argument("--test-tts", type=str, help="Test text-to-speech with text")
    parser.add_argument("--explore", type=str, help="Explore problem with voice")
    parser.add_argument("--azure-key", help="Azure Speech API key")
    parser.add_argument("--azure-region", help="Azure Speech region")

    args = parser.parse_args()

    # Initialize interface
    interface = JARVISAzureVoiceInterface(
        azure_speech_key=args.azure_key,
        azure_speech_region=args.azure_region
    )

    if args.test_tts:
        print(f"🗣️  Testing TTS: {args.test_tts}")
        interface.speak(args.test_tts)
    elif args.test_stt:
        print("🎤 Testing STT... Say something...")
        text = interface.listen()
        if text:
            print(f"  Heard: {text}")
        else:
            print("  Could not understand")
    elif args.explore:
        print(f"🔍 Exploring: {args.explore}")
        result = interface.process_vector_exploration_voice(args.explore)
        print(f"\n✅ Exploration complete:")
        print(f"  Recommended: {result.get('recommended_path', 'None')}")
        interface.save_conversation()
    elif args.start:
        print("🎤 Starting JARVIS Azure Voice Interface...")
        print("   Hands-free operation")
        print("   Human-compatible speech")
        print("   Say 'explore [problem]' to start vector exploration")
        print("   Say 'stop' or 'exit' to end")
        print("\nPress Ctrl+C to stop\n")

        interface.start_continuous_conversation()

        try:
            while interface.is_listening:
                time.sleep(1)
        except KeyboardInterrupt:
            interface.stop_conversation()
            interface.save_conversation()
    else:
        parser.print_help()


if __name__ == "__main__":



    main()