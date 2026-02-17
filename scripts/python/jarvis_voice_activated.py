#!/usr/bin/env python3
"""
JARVIS Voice Activated - Full Voice Interface

Activate JARVIS with full voice capabilities:
- Listens to you (speech-to-text)
- Determines your intent from voice input
- Processes requests through JARVIS
- Speaks responses out loud (text-to-speech)

Works across all JARVIS interfaces with clear speaker labels.

@JARVIS @VOICE @SPEECH @ACTIVATION
"""

import sys
import time
import signal
from pathlib import Path
from typing import Optional, Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISVoiceActivated")

# Import JARVIS components
try:
    from jarvis_azure_voice_interface import JARVISAzureVoiceInterface
    VOICE_INTERFACE_AVAILABLE = True
except ImportError:
    VOICE_INTERFACE_AVAILABLE = False
    logger.error("JARVIS Azure Voice Interface not available")

try:
    from jarvis_master_command import JARVISMasterCommand
    MASTER_COMMAND_AVAILABLE = True
except ImportError:
    MASTER_COMMAND_AVAILABLE = False
    logger.error("JARVIS Master Command not available")

try:
    from jarvis_core_intelligence import JARVISCoreIntelligence
    CORE_INTELLIGENCE_AVAILABLE = True
except ImportError:
    CORE_INTELLIGENCE_AVAILABLE = False
    logger.error("JARVIS Core Intelligence not available")

try:
    from jarvis_conversation_formatter import ConversationFormatter, Speaker
    FORMATTER_AVAILABLE = True
except ImportError:
    FORMATTER_AVAILABLE = False
    logger.warning("Conversation formatter not available - will use basic formatting")


class JARVISVoiceActivated:
    """
    Full Voice-Activated JARVIS Interface

    Listens to you, determines intent, processes through JARVIS, and speaks responses.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize voice-activated JARVIS"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger
        self.running = False

        # Initialize components
        self.voice_interface: Optional[JARVISAzureVoiceInterface] = None
        self.master_command: Optional[JARVISMasterCommand] = None
        self.core_intelligence: Optional[JARVISCoreIntelligence] = None
        self.formatter: Optional[ConversationFormatter] = None

        self._initialize_components()

        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _initialize_components(self):
        """Initialize all JARVIS components"""
        self.logger.info("Initializing JARVIS Voice Activated...")

        # Voice Interface
        if VOICE_INTERFACE_AVAILABLE:
            try:
                self.voice_interface = JARVISAzureVoiceInterface(project_root=self.project_root)
                self.logger.info("✅ Voice Interface initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Voice Interface: {e}")

        # Master Command (for processing requests)
        if MASTER_COMMAND_AVAILABLE:
            try:
                self.master_command = JARVISMasterCommand(project_root=self.project_root)
                self.logger.info("✅ Master Command initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Master Command: {e}")

        # Core Intelligence (for intent understanding)
        if CORE_INTELLIGENCE_AVAILABLE:
            try:
                self.core_intelligence = JARVISCoreIntelligence(project_root=self.project_root)
                self.logger.info("✅ Core Intelligence initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Core Intelligence: {e}")

        # Conversation Formatter
        if FORMATTER_AVAILABLE:
            try:
                self.formatter = ConversationFormatter(use_emojis=True, use_timestamps=True)
                self.logger.info("✅ Conversation Formatter initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Conversation Formatter not available: {e}")

    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received {signal_name} signal, shutting down...")
        self.running = False
        if self.voice_interface:
            self.voice_interface.stop_conversation()

    def activate(self):
        """Activate voice-activated JARVIS"""
        if not self.voice_interface:
            self.logger.error("❌ Voice Interface not available - cannot activate")
            return False

        if not self.master_command:
            self.logger.error("❌ Master Command not available - cannot process requests")
            return False

        self.logger.info("="*80)
        self.logger.info("🎯 JARVIS Voice Activated - Full Voice Interface")
        self.logger.info("="*80)
        self.logger.info("")
        self.logger.info("JARVIS is now:")
        self.logger.info("  👂 Listening to you (speech-to-text)")
        self.logger.info("  🧠 Understanding your intent")
        self.logger.info("  ⚙️  Processing through all JARVIS interfaces")
        self.logger.info("  🗣️  Speaking responses out loud (text-to-speech)")
        self.logger.info("")
        self.logger.info("Say 'exit' or 'quit' to stop")
        self.logger.info("="*80)
        self.logger.info("")

        # Speak activation message
        activation_message = "JARVIS voice interface activated. I'm listening. How can I help you?"
        if self.formatter:
            formatted = self.formatter.format_message(Speaker.JARVIS, activation_message)
            print(f"\n{formatted.formatted}")
        else:
            print(f"\n🤖 JARVIS: {activation_message}")

        self.voice_interface.speak(activation_message)

        # Start conversation loop
        self.running = True
        self._conversation_loop()

        return True

    def _conversation_loop(self):
        """Main conversation loop"""
        while self.running:
            try:
                # Listen for user input
                self.logger.info("👂 Listening...")

                # Listen with a reasonable timeout
                # Note: The listen() method may need to be called in a way that doesn't block indefinitely
                user_text = None
                try:
                    user_text = self.voice_interface.listen(timeout=30.0)  # 30 second timeout
                except Exception as e:
                    self.logger.debug(f"Listen error (may be timeout): {e}")

                if not user_text:
                    continue

                # Display what we heard (with clear labels)
                if self.formatter:
                    human_msg = self.formatter.format_message(Speaker.HUMAN, user_text)
                    print(f"\n{human_msg.formatted}")
                else:
                    print(f"\n👤 HUMAN: {user_text}")

                # Check for exit commands
                if user_text.lower().strip() in ['exit', 'quit', 'stop', 'goodbye']:
                    goodbye_message = "Goodbye. JARVIS voice interface deactivated."
                    if self.formatter:
                        formatted = self.formatter.format_message(Speaker.JARVIS, goodbye_message)
                        print(f"\n{formatted.formatted}")
                    else:
                        print(f"\n🤖 JARVIS: {goodbye_message}")
                    self.voice_interface.speak(goodbye_message)
                    break

                # Determine intent (optional, for logging/debugging)
                intent = None
                if self.core_intelligence:
                    try:
                        intent = self.core_intelligence.understand_intent(user_text)
                        self.logger.info(f"Intent detected: {intent.intent_type.value} (confidence: {intent.confidence:.2f})")
                    except Exception as e:
                        self.logger.debug(f"Intent detection error: {e}")

                # Process command through JARVIS
                self.logger.info("⚙️  Processing request through JARVIS...")
                result = self.master_command.process_command(user_text)

                # Get response
                response = result.get('response', "I'm not sure how to respond to that.")

                # Display response (with clear labels)
                if self.formatter:
                    jarvis_msg = self.formatter.format_message(Speaker.JARVIS, response)
                    print(f"\n{jarvis_msg.formatted}")
                else:
                    print(f"\n🤖 JARVIS: {response}")

                # Speak response out loud
                self.logger.info("🗣️  Speaking response...")
                self.voice_interface.speak(response)

                # Small delay before next listen
                time.sleep(0.5)

            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Error in conversation loop: {e}", exc_info=True)
                error_message = "I encountered an error. Please try again."
                if self.formatter:
                    error_msg = self.formatter.format_message(Speaker.SYSTEM, error_message)
                    print(f"\n{error_msg.formatted}")
                else:
                    print(f"\n⚙️  SYSTEM: {error_message}")
                self.voice_interface.speak(error_message)
                time.sleep(1)

        self.running = False
        self.logger.info("JARVIS voice interface deactivated")

    def test_voice(self):
        """Test voice input/output"""
        if not self.voice_interface:
            print("❌ Voice Interface not available")
            return False

        print("\n" + "="*80)
        print("JARVIS Voice Test")
        print("="*80)
        print("\nTesting voice capabilities...")
        print()

        # Test speech output
        test_message = "This is a test of JARVIS voice interface. Can you hear me?"
        print(f"🤖 JARVIS: {test_message}")
        self.voice_interface.speak(test_message)

        time.sleep(1)

        # Test speech input
        print("\n👂 Listening for 5 seconds... Say something:")
        print("(Or wait for timeout)")

        user_text = None
        try:
            # Use a timeout for testing
            # Note: listen() may need modification to support timeout properly
            user_text = self.voice_interface.listen()
        except Exception as e:
            print(f"Listening error: {e}")

        if user_text:
            print(f"\n👤 You said: {user_text}")
        else:
            print("\n(No speech detected)")

        print("\n✅ Voice test complete")
        return True


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Voice Activated - Full Voice Interface")
        parser.add_argument('--test', action='store_true', help='Test voice input/output')
        parser.add_argument('--use-elevenlabs', action='store_true', help='Use ElevenLabs TTS instead of Azure TTS')
        parser.add_argument('--project-root', type=str, help='Project root directory')

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        jarvis_voice = JARVISVoiceActivated(project_root=project_root)

        # Enable ElevenLabs if requested
        if args.use_elevenlabs and jarvis_voice.voice_interface:
            jarvis_voice.voice_interface.enable_elevenlabs_tts(True)
            logger.info("✅ ElevenLabs TTS enabled for voice responses")

        if args.test:
            jarvis_voice.test_voice()
        else:
            # Activate full voice interface
            jarvis_voice.activate()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()