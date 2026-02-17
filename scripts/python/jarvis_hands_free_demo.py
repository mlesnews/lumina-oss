#!/usr/bin/env python3
"""
JARVIS Hands-Free Demo - Zero Clicks, True Conversation

Actual human-in-the-loop interaction:
- JARVIS speaks to you
- You speak to JARVIS
- Zero clicks required
- Pause detection (Audio-Technica style)
- Dictation mode
- "Ready to send?" confirmation
- Works with JARVIS and MARVIN

"JARVIS, make it happen."
"""

import sys
import os
import json
import threading
import queue
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
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
    print("⚠️  Installing Azure Speech SDK...")
    print("   Run: pip install azure-cognitiveservices-speech")

logger = get_logger("JARVISHandsFree")


class PauseDetector:
    """
    Audio-Technica style pause detection
    Scales pauses for natural dictation
    """

    def __init__(self, initial_pause_threshold: float = 1.0, 
                 scaling_factor: float = 0.5):
        """
        Args:
            initial_pause_threshold: Initial pause detection threshold (seconds)
            scaling_factor: How much to scale pauses (0.0-1.0)
        """
        self.initial_threshold = initial_pause_threshold
        self.scaling_factor = scaling_factor
        self.current_threshold = initial_pause_threshold
        self.last_speech_time = None
        self.pause_count = 0

    def detect_pause(self, time_since_speech: float) -> bool:
        """Detect if we're in a pause"""
        if time_since_speech >= self.current_threshold:
            self.pause_count += 1
            # Scale threshold based on pause frequency
            self.current_threshold = self.initial_threshold * (
                1.0 + (self.pause_count * self.scaling_factor)
            )
            return True
        return False

    def reset(self):
        """Reset pause detection"""
        self.current_threshold = self.initial_threshold
        self.pause_count = 0
        self.last_speech_time = None


class JARVISHandsFreeDemo:
    """
    JARVIS Hands-Free Demo

    Zero clicks. True conversation. JARVIS speaks. You speak. That's it.
    """

    def __init__(self, azure_speech_key: Optional[str] = None,
                 azure_speech_region: Optional[str] = None):
        """Initialize hands-free demo"""
        self.logger = get_logger("JARVISHandsFree")

        # Azure configuration - try Key Vault first, then env, then parameter
        self.azure_speech_key = azure_speech_key or self._get_azure_speech_key_from_vault() or os.getenv("AZURE_SPEECH_KEY")
        self.azure_speech_region = azure_speech_region or self._get_azure_speech_region_from_vault() or os.getenv("AZURE_SPEECH_REGION", "eastus")

        # Azure Speech SDK
        self.speech_config: Optional[speechsdk.SpeechConfig] = None
        self.audio_config: Optional[speechsdk.audio.AudioConfig] = None
        self.speech_recognizer: Optional[speechsdk.SpeechRecognizer] = None
        self.speech_synthesizer: Optional[speechsdk.SpeechSynthesizer] = None

        # Pause detection
        self.pause_detector = PauseDetector(initial_pause_threshold=1.5, scaling_factor=0.3)

        # Conversation state
        self.is_listening = False
        self.is_speaking = False
        self.dictation_mode = False
        self.dictation_buffer = []
        self.waiting_for_send_confirmation = False

        # Initialize Azure
        self._initialize_azure()

        # Load JARVIS and MARVIN
        self._load_agents()

        self.logger.info("🤖 JARVIS Hands-Free Demo initialized")
        self.logger.info("   Zero clicks required")
        self.logger.info("   True conversation enabled")
        self.logger.info("   JARVIS and MARVIN ready")
        if self.azure_speech_key:
            self.logger.info("   ✅ Azure Speech key: Retrieved from Key Vault")
        else:
            self.logger.warning("   ⚠️  Azure Speech key: Not found (check Key Vault or env)")

    def _get_azure_speech_key_from_vault(self) -> Optional[str]:
        """Retrieve Azure Speech key from Azure Key Vault"""
        try:
            # Try importing from the correct path
            try:
                from azure_service_bus_integration import AzureKeyVaultClient
            except ImportError:
                from scripts.python.azure_service_bus_integration import AzureKeyVaultClient

            # Try default vault URL
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

    def _initialize_azure(self):
        """Initialize Azure Speech SDK"""
        if not AZURE_SPEECH_AVAILABLE:
            self.logger.error("❌ Azure Speech SDK not available")
            return False

        if not self.azure_speech_key:
            self.logger.error("❌ AZURE_SPEECH_KEY not set")
            self.logger.error("   Set: export AZURE_SPEECH_KEY='your-key'")
            return False

        try:
            # Speech configuration
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_speech_key,
                region=self.azure_speech_region
            )

            # Natural voice
            self.speech_config.speech_recognition_language = "en-US"
            self.speech_config.speech_synthesis_language = "en-US"
            self.speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

            # Audio configuration
            self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

            # Speech recognizer
            self.speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=self.audio_config
            )

            # Speech synthesizer
            self.speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None
            )

            self.logger.info("✅ Azure Speech SDK configured")
            return True

        except Exception as e:
            self.logger.error(f"❌ Azure initialization failed: {e}")
            return False

    def _load_agents(self):
        """Load JARVIS and MARVIN"""
        try:
            from jarvis_vector_explorer import JARVISVectorExplorer
            self.jarvis = JARVISVectorExplorer()
            self.logger.info("✅ JARVIS loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  JARVIS not available: {e}")
            self.jarvis = None

        try:
            # Try to load MARVIN
            from marvin_dropbox_cleanup import MarvinDropboxCleanup
            self.marvin = MarvinDropboxCleanup()
            self.logger.info("✅ MARVIN loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  MARVIN not available: {e}")
            self.marvin = None

    def speak(self, text: str, wait: bool = False):
        """
        JARVIS speaks to you

        Args:
            text: Text to speak
            wait: Wait for speech to complete
        """
        if not self.speech_synthesizer:
            print(f"JARVIS: {text}")
            return

        self.is_speaking = True

        try:
            self.logger.info(f"🗣️  JARVIS: {text}")
            result = self.speech_synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                if wait:
                    time.sleep(0.5)  # Small pause after speech
            else:
                self.logger.error(f"❌ Speech synthesis failed: {result.reason}")

        except Exception as e:
            self.logger.error(f"❌ Speech error: {e}")
            print(f"JARVIS: {text}")

        finally:
            self.is_speaking = False

    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Listen for your speech

        Args:
            timeout: Timeout in seconds

        Returns:
            Recognized text or None
        """
        if not self.speech_recognizer:
            return None

        self.is_listening = True

        try:
            self.logger.info("🎤 Listening...")
            result = self.speech_recognizer.recognize_once_async().get()

            self.is_listening = False

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = result.text
                self.logger.info(f"👂 Heard: {text}")
                return text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                self.logger.debug("  No speech detected")
                return None
            else:
                self.logger.warning(f"  Recognition error: {result.reason}")
                return None

        except Exception as e:
            self.logger.error(f"❌ Listening error: {e}")
            self.is_listening = False
            return None

    def listen_with_pause_detection(self, max_pauses: int = 3) -> List[str]:
        """
        Listen with pause detection (Audio-Technica style)

        Detects natural pauses in speech and segments accordingly.

        Args:
            max_pauses: Maximum pauses before stopping

        Returns:
            List of speech segments
        """
        segments = []
        pause_count = 0
        last_speech_time = time.time()

        self.speak("I'm listening. Speak naturally, and I'll detect when you pause.")

        while pause_count < max_pauses:
            segment = self.listen(timeout=2.0)

            if segment:
                segments.append(segment)
                last_speech_time = time.time()
                pause_count = 0
                self.pause_detector.reset()
            else:
                # Check for pause
                time_since_speech = time.time() - last_speech_time
                if self.pause_detector.detect_pause(time_since_speech):
                    pause_count += 1
                    if pause_count < max_pauses:
                        self.speak("Continue...")
                else:
                    # Still listening
                    time.sleep(0.1)

        return segments

    def dictation_mode(self):
        """Enter dictation mode - continuous transcription"""
        self.dictation_mode = True
        self.dictation_buffer = []

        self.speak("Dictation mode activated. I'll transcribe everything you say. Say 'send' when done.")

        while self.dictation_mode:
            text = self.listen()

            if text:
                if "send" in text.lower() or "done" in text.lower():
                    # Ready to send
                    self.waiting_for_send_confirmation = True
                    full_text = " ".join(self.dictation_buffer + [text.replace("send", "").replace("done", "").strip()])

                    self.speak(f"I transcribed: {full_text}")
                    self.speak("Ready to send? Say 'yes' to send, 'no' to continue dictating.")

                    response = self.listen()

                    if response and "yes" in response.lower():
                        self.speak("Sending...")
                        # Process the dictation
                        self._process_dictation(full_text)
                        self.dictation_mode = False
                        self.waiting_for_send_confirmation = False
                    else:
                        self.speak("Continuing dictation...")
                        self.waiting_for_send_confirmation = False
                else:
                    self.dictation_buffer.append(text)
                    self.speak(f"Got it. {text}")

    def _process_dictation(self, text: str):
        try:
            """Process completed dictation"""
            self.logger.info(f"📝 Dictation received: {text}")

            # Save dictation
            data_dir = Path(__file__).parent.parent.parent / "data" / "jarvis" / "dictation"
            data_dir.mkdir(parents=True, exist_ok=True)

            dictation_file = data_dir / f"dictation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(dictation_file, 'w', encoding='utf-8') as f:
                f.write(text)

            self.speak(f"Dictation saved and processed. {len(text)} characters.")

        except Exception as e:
            self.logger.error(f"Error in _process_dictation: {e}", exc_info=True)
            raise
    def conversation_loop(self):
        """Main conversation loop - zero clicks"""
        self.speak("Hello. I'm JARVIS. I'm ready to work with you, hands-free. How can I help?")

        while True:
            try:
                # Listen for command
                command = self.listen()

                if not command:
                    continue

                # Process command
                if "jarvis" in command.lower() or "hey jarvis" in command.lower():
                    self.speak("Yes, I'm here. What would you like to do?")
                    continue

                elif "marvin" in command.lower():
                    if self.marvin:
                        self.speak("MARVIN is here. What would you like MARVIN to do?")
                    else:
                        self.speak("MARVIN is not available right now.")
                    continue

                elif "explore" in command.lower() or "vector" in command.lower():
                    if not self.jarvis:
                        self.speak("JARVIS Vector Explorer is not available.")
                        continue

                    # Extract problem
                    problem = command.replace("explore", "").replace("vector", "").strip()
                    if not problem:
                        self.speak("What problem would you like to explore?")
                        problem = self.listen()

                    if problem:
                        self.speak(f"Let's explore: {problem}")
                        self._explore_with_voice(problem)
                    continue

                elif "dictate" in command.lower() or "dictation" in command.lower():
                    self.dictation_mode()
                    continue

                elif "pause" in command.lower() or "detect pauses" in command.lower():
                    self.speak("Starting pause detection mode. Speak naturally.")
                    segments = self.listen_with_pause_detection()
                    self.speak(f"I heard {len(segments)} segments: {', '.join(segments)}")
                    continue

                elif "stop" in command.lower() or "exit" in command.lower() or "goodbye" in command.lower():
                    self.speak("Goodbye. It was great working with you.")
                    break

                else:
                    # General conversation
                    self.speak(f"I heard: {command}. How can I help?")
                    continue

            except KeyboardInterrupt:
                self.speak("Stopping...")
                break
            except Exception as e:
                self.logger.error(f"Error: {e}")
                self.speak("I encountered an error. Let's continue.")

    def _explore_with_voice(self, problem: str):
        """Explore problem with voice interaction"""
        if not self.jarvis:
            return

        # Identify vectors
        self.speak("Identifying vectors to explore...")
        vectors = self.jarvis.identify_vectors(problem)
        self.speak(f"I've identified {len(vectors)} vectors.")

        # Ask questions by voice
        human_responses = {}

        for vector in vectors[:2]:  # Limit for demo
            self.speak(f"Let's explore {vector.name}.")

            for question in vector.questions[:2]:  # Limit for demo
                self.speak(question)
                response = self.listen()

                if response:
                    human_responses[f"q_{len(human_responses)}"] = response
                    self.speak(f"Got it. {response}")

        # Find paths
        self.speak("Finding paths forward...")
        paths = self.jarvis.find_paths_forward()

        # Recommend
        recommended = self.jarvis.recommend_path()

        if recommended:
            self.speak(f"I recommend: {recommended.name}. "
                      f"Feasibility: {int(recommended.feasibility * 100)} percent, "
                      f"Impact: {int(recommended.impact * 100)} percent.")
        else:
            self.speak("I couldn't determine a clear recommendation.")


def main():
    """Run JARVIS Hands-Free Demo"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Hands-Free Demo - Zero Clicks")
    parser.add_argument("--azure-key", help="Azure Speech API key")
    parser.add_argument("--azure-region", help="Azure Speech region", default="eastus")
    parser.add_argument("--test", action="store_true", help="Test voice")
    parser.add_argument("--demo", action="store_true", help="Run full demo")

    args = parser.parse_args()

    # Check Azure key - but first try Key Vault
    # The demo will try Key Vault automatically, so we don't need to fail here
    # Just warn if no key is provided and let the demo try Key Vault

    # Initialize demo
    demo = JARVISHandsFreeDemo(
        azure_speech_key=args.azure_key,
        azure_speech_region=args.azure_region
    )

    if args.test:
        print("🎤 Testing voice...")
        print("   JARVIS will speak, then listen for your response")

        demo.speak("Hello. This is JARVIS. Can you hear me?")
        time.sleep(1)

        response = demo.listen()
        if response:
            demo.speak(f"I heard: {response}. Voice test successful!")
        else:
            demo.speak("I didn't hear anything. Please check your microphone.")

    elif args.demo:
        print("🤖 Starting JARVIS Hands-Free Demo...")
        print("   Zero clicks required")
        print("   JARVIS will speak to you")
        print("   You speak to JARVIS")
        print("   Say 'stop' or 'exit' to end")
        print("\n" + "="*60)
        print("🎤 JARVIS is ready. Starting conversation...")
        print("="*60 + "\n")

        demo.conversation_loop()

    else:
        parser.print_help()
        print("\n💡 Quick start:")
        print("   python jarvis_hands_free_demo.py --demo")
        print("   python jarvis_hands_free_demo.py --test")


if __name__ == "__main__":



    main()