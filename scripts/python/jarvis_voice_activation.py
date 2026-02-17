#!/usr/bin/env python3
"""
JARVIS Voice Activation - Full Voice Interface

Activates JARVIS with complete voice capabilities:
- JARVIS speaks responses out loud (TTS)
- JARVIS listens to voice input (STT)
- Determines intent from voice commands
- Works across all interfaces

@JARVIS @VOICE @ACTIVATION @TTS @STT
"""

import sys
import time
import signal
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISVoiceActivation")

# Import JARVIS components
try:
    from jarvis_azure_voice_interface import JARVISAzureVoiceInterface
    VOICE_AVAILABLE = True
except ImportError as e:
    VOICE_AVAILABLE = False
    logger.error(f"Azure Voice Interface not available: {e}")

try:
    from jarvis_master_command import JARVISMasterCommand
    MASTER_COMMAND_AVAILABLE = True
except ImportError as e:
    MASTER_COMMAND_AVAILABLE = False
    logger.error(f"Master Command not available: {e}")

try:
    from jarvis_core_intelligence import JARVISCoreIntelligence
    CORE_INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    CORE_INTELLIGENCE_AVAILABLE = False
    logger.error(f"Core Intelligence not available: {e}")

try:
    from jarvis_conversation_formatter import ConversationFormatter, Speaker
    FORMATTER_AVAILABLE = True
except ImportError:
    FORMATTER_AVAILABLE = False


class JARVISVoiceActivation:
    """
    Full voice activation for JARVIS.

    JARVIS speaks out loud and listens to voice input to determine intent.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Voice Activation"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger

        # Initialize components
        self.voice_interface: Optional[JARVISAzureVoiceInterface] = None
        self.master_command: Optional[JARVISMasterCommand] = None
        self.core_intelligence: Optional[JARVISCoreIntelligence] = None
        self.formatter: Optional[ConversationFormatter] = None

        self.running = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received {signal_name} signal, shutting down...")
        self.running = False
        if self.voice_interface:
            self.voice_interface.stop_conversation()

    def activate(self) -> bool:
        """Activate JARVIS with full voice capabilities"""
        self.logger.info("="*80)
        self.logger.info("🎯 Activating JARVIS Voice Interface")
        self.logger.info("="*80)

        # Check prerequisites
        if not VOICE_AVAILABLE:
            self.logger.error("❌ Azure Voice Interface not available")
            print("❌ ERROR: Azure Voice Interface not available")
            print("   Install: pip install azure-cognitiveservices-speech")
            print("   Configure Azure Speech API key in Azure Key Vault")
            return False

        if not MASTER_COMMAND_AVAILABLE:
            self.logger.error("❌ Master Command not available")
            print("❌ ERROR: JARVIS Master Command not available")
            return False

        # Initialize voice interface
        self.logger.info("Initializing Azure Voice Interface...")
        try:
            self.voice_interface = JARVISAzureVoiceInterface(project_root=self.project_root)
            if not self.voice_interface.speech_synthesizer:
                self.logger.error("❌ Speech synthesizer not initialized")
                print("❌ ERROR: Speech synthesizer not initialized")
                print("   Check Azure Speech API key configuration")
                return False
            self.logger.info("✅ Voice Interface initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Voice Interface: {e}", exc_info=True)
            print(f"❌ ERROR: Failed to initialize Voice Interface: {e}")
            return False

        # Initialize Master Command
        self.logger.info("Initializing JARVIS Master Command...")
        try:
            self.master_command = JARVISMasterCommand(project_root=self.project_root)
            self.logger.info("✅ Master Command initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Master Command: {e}", exc_info=True)
            print(f"❌ ERROR: Failed to initialize Master Command: {e}")
            return False

        # Initialize Core Intelligence (for intent detection)
        if CORE_INTELLIGENCE_AVAILABLE:
            try:
                self.core_intelligence = JARVISCoreIntelligence(project_root=self.project_root)
                self.logger.info("✅ Core Intelligence initialized")
            except Exception as e:
                self.logger.warning(f"Core Intelligence not available: {e}")

        # Initialize formatter
        if FORMATTER_AVAILABLE:
            self.formatter = ConversationFormatter(use_emojis=True, use_timestamps=True)

        self.logger.info("="*80)
        self.logger.info("✅ JARVIS Voice Activation Complete!")
        self.logger.info("="*80)

        # Speak activation message
        activation_message = "JARVIS activated. Voice interface ready. I'm listening."
        self.voice_interface.speak(activation_message)
        print(f"🤖 JARVIS: {activation_message}")

        return True

    def process_voice_command(self, voice_text: str) -> Optional[str]:
        """
        Process a voice command through JARVIS

        Args:
            voice_text: Text recognized from voice input

        Returns:
            JARVIS response text (to be spoken)
        """
        if not self.master_command:
            return "Master command system not available."

        # Display human input (with clear label)
        if self.formatter:
            human_msg = self.formatter.format_message(Speaker.HUMAN, voice_text)
            print(human_msg.formatted)
        else:
            print(f"👤 HUMAN: {voice_text}")

        # Process command through JARVIS
        try:
            result = self.master_command.process_command(voice_text)
            response = result.get('response', 'Command processed.')

            # Display JARVIS response (with clear label)
            if self.formatter:
                jarvis_msg = self.formatter.format_message(Speaker.JARVIS, response)
                print(jarvis_msg.formatted)
            else:
                print(f"🤖 JARVIS: {response}")

            return response

        except Exception as e:
            error_msg = f"Error processing command: {e}"
            self.logger.error(error_msg, exc_info=True)
            return error_msg

    def listen_and_respond(self, timeout: Optional[float] = None) -> bool:
        """
        Listen for voice input and respond

        Args:
            timeout: Timeout in seconds (None for no timeout)

        Returns:
            True if successful, False if error or timeout
        """
        if not self.voice_interface:
            self.logger.error("Voice interface not initialized")
            return False

        try:
            # Listen for voice input
            self.logger.info("🎤 Listening for voice input...")
            voice_text = self.voice_interface.listen(timeout=timeout)

            if not voice_text:
                if timeout:
                    self.logger.debug("No speech recognized (timeout)")
                else:
                    self.logger.debug("No speech recognized")
                return False

            # Process the voice command
            response = self.process_voice_command(voice_text)

            # Speak the response
            if response:
                self.logger.info("🗣️  Speaking response...")
                self.voice_interface.speak(response)

            return True

        except Exception as e:
            self.logger.error(f"Error in listen_and_respond: {e}", exc_info=True)
            return False

    def run_continuous(self):
        """Run continuous voice conversation loop"""
        if not self.activate():
            return

        self.running = True
        self.logger.info("Starting continuous voice conversation...")
        print("\n" + "="*80)
        print("🎯 JARVIS Voice Interface Active")
        print("="*80)
        print("\nSay 'exit', 'quit', or 'goodbye' to end the conversation")
        print("JARVIS is listening...\n")

        try:
            while self.running:
                # Listen and respond
                success = self.listen_and_respond()

                if not success:
                    # Small delay before next listen attempt
                    time.sleep(0.5)
                    continue

                # Check if user said exit
                # This check happens in process_voice_command output, 
                # but we can also check the last recognized text
                if self.voice_interface.conversation_history:
                    last_message = self.voice_interface.conversation_history[-1]
                    if last_message.speaker == "human":
                        text_lower = last_message.text.lower()
                        if any(word in text_lower for word in ['exit', 'quit', 'goodbye', 'stop', 'end']):
                            goodbye_message = "Goodbye. JARVIS voice interface deactivated."
                            self.voice_interface.speak(goodbye_message)
                            print(f"\n🤖 JARVIS: {goodbye_message}")
                            break

                # Small delay before next listen
                time.sleep(0.5)

        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
            goodbye_message = "Goodbye. JARVIS voice interface deactivated."
            if self.voice_interface:
                self.voice_interface.speak(goodbye_message)
            print(f"\n🤖 JARVIS: {goodbye_message}")
        except Exception as e:
            self.logger.error(f"Error in continuous loop: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
        finally:
            self.running = False
            if self.voice_interface:
                self.voice_interface.stop_conversation()
            self.logger.info("JARVIS voice interface stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Voice Activation")
    parser.add_argument('--continuous', action='store_true', 
                       help='Run continuous voice conversation')
    parser.add_argument('--single', action='store_true',
                       help='Listen once and respond')
    parser.add_argument('--timeout', type=float, default=None,
                       help='Timeout for listening (seconds)')

    args = parser.parse_args()

    activation = JARVISVoiceActivation()

    if args.continuous:
        # Continuous conversation mode
        activation.run_continuous()
    elif args.single:
        # Single listen and respond
        if not activation.activate():
            sys.exit(1)
        activation.listen_and_respond(timeout=args.timeout)
    else:
        # Default: continuous mode
        activation.run_continuous()


if __name__ == "__main__":


    main()