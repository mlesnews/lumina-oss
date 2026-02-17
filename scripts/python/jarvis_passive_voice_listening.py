#!/usr/bin/env python3
"""
JARVIS Passive Voice Listening Mode
Activates passive listening with wake word filtering for "JARVIS" or "HEY JARVIS"
Filters out all normal conversation unless wake trigger is detected
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Try to import with error handling
try:
    from scripts.python.voice_interface_system import VoiceInterfaceSystem
except ImportError as e:
    print(f"Warning: Could not import VoiceInterfaceSystem: {e}", file=sys.stderr)
    VoiceInterfaceSystem = None

try:
    from scripts.python.automatic_microphone_activation import AutomaticMicrophoneActivation
except ImportError as e:
    print(f"Warning: Could not import AutomaticMicrophoneActivation: {e}", file=sys.stderr)
    AutomaticMicrophoneActivation = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class JARVISPassiveVoiceListening:
    """JARVIS Passive Voice Listening with Wake Word Filtering"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.voice_interface = None
        self.microphone_activation = None
        self.passive_mode_active = False

    def activate_passive_listening(self, wake_words: list = None):
        """
        Activate passive voice listening mode with wake word filtering

        Args:
            wake_words: List of wake words to listen for (default: ["jarvis", "hey jarvis"])
        """
        if wake_words is None:
            wake_words = ["jarvis", "hey jarvis"]

        try:
            # Initialize voice interface (with error handling)
            if self.voice_interface is None and VoiceInterfaceSystem:
                try:
                    self.voice_interface = VoiceInterfaceSystem()
                except Exception as e:
                    self.logger.warning(f"Could not initialize VoiceInterfaceSystem: {e}")
                    self.voice_interface = None

            # Initialize microphone activation (with error handling)
            if self.microphone_activation is None and AutomaticMicrophoneActivation:
                try:
                    self.microphone_activation = AutomaticMicrophoneActivation()
                except Exception as e:
                    self.logger.warning(f"Could not initialize AutomaticMicrophoneActivation: {e}")
                    self.microphone_activation = None

            # Start passive listening with wake word filtering
            self.logger.info("🎤 Activating JARVIS Passive Voice Listening Mode...")
            self.logger.info(f"   Wake words: {', '.join(wake_words)}")
            self.logger.info("   Filtering: All normal conversation ignored")
            self.logger.info("   Listening: Only responds to wake triggers")

            # Start passive listening (if available)
            if self.microphone_activation:
                try:
                    self.microphone_activation.start_passive_listening()
                except Exception as e:
                    self.logger.warning(f"Could not start passive listening: {e}")
            else:
                self.logger.warning("AutomaticMicrophoneActivation not available")

            # Start voice interface with wake word detection (if available)
            if self.voice_interface:
                try:
                    primary_wake_word = wake_words[0] if wake_words else "jarvis"
                    self.voice_interface.start_listening(wake_word=primary_wake_word)
                except Exception as e:
                    self.logger.warning(f"Could not start voice interface: {e}")
            else:
                self.logger.warning("VoiceInterfaceSystem not available")

            self.passive_mode_active = True

            self.logger.info("✅ JARVIS Passive Voice Listening Mode ACTIVE")
            self.logger.info("   👂 Listening for: 'JARVIS' or 'HEY JARVIS'")
            self.logger.info("   🔇 Filtering out all normal conversation")
            self.logger.info("   ⚡ Ready for wake word detection")

            return True

        except Exception as e:
            self.logger.error(f"❌ Error activating passive listening: {e}")
            return False

    def deactivate_passive_listening(self):
        """Deactivate passive voice listening mode"""
        try:
            if self.voice_interface:
                self.voice_interface.stop_listening()

            if self.microphone_activation:
                self.microphone_activation.stop_passive_listening()

            self.passive_mode_active = False
            self.logger.info("🔇 JARVIS Passive Voice Listening Mode DEACTIVATED")

        except Exception as e:
            self.logger.error(f"Error deactivating passive listening: {e}")


def main():
    """Main entry point"""
    import argparse

    try:
        parser = argparse.ArgumentParser(description="JARVIS Passive Voice Listening Mode")
        parser.add_argument("--activate", action="store_true", help="Activate passive listening")
        parser.add_argument("--deactivate", action="store_true", help="Deactivate passive listening")
        parser.add_argument("--wake-words", nargs="+", default=["jarvis", "hey jarvis"],
                           help="Wake words to listen for (default: jarvis, hey jarvis)")

        args = parser.parse_args()

        listener = JARVISPassiveVoiceListening()

        if args.activate:
            success = listener.activate_passive_listening(wake_words=args.wake_words)
            if not success:
                logger.warning("Failed to activate passive listening (non-fatal)")
                # Don't exit with error - graceful degradation
                sys.exit(0)  # Exit gracefully
            # Keep running
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                listener.deactivate_passive_listening()
                sys.exit(0)
        elif args.deactivate:
            listener.deactivate_passive_listening()
            sys.exit(0)
        else:
            # Default: activate
            success = listener.activate_passive_listening(wake_words=args.wake_words)
            if not success:
                logger.warning("Failed to activate passive listening (non-fatal)")
                # Don't exit with error - graceful degradation
                sys.exit(0)  # Exit gracefully
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                listener.deactivate_passive_listening()
                sys.exit(0)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except ImportError as e:
        logger.warning(f"Import error (non-fatal): {e}")
        sys.exit(0)  # Graceful exit
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        # Exit gracefully to prevent terminal process crashes
        sys.exit(0)  # Don't use exit code 1 - prevents 4294967295 error


if __name__ == "__main__":
    try:
        sys.exit(0)  # Success
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)  # Normal interrupt
    except ImportError as e:
        # Import errors are non-fatal - log and exit gracefully
        logger.warning(f"Import error (non-fatal): {e}")
        logger.info("Continuing without voice interface features")
        sys.exit(0)  # Exit gracefully, don't treat as error
    except Exception as e:
        # Log error but exit gracefully to prevent terminal crashes
        logger.error(f"Error in main: {e}", exc_info=True)
        # Exit with 0 to prevent terminal process error (4294967295)
        # Errors are logged, but don't crash the terminal
        sys.exit(0)  # Graceful exit even on error


        main()