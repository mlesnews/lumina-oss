#!/usr/bin/env python3
"""
Automatic Microphone Activation System

Enables passive and active listening without manual microphone activation.
Automatically activates microphone for voice input.

@VOICE @MICROPHONE @PASSIVE @ACTIVE @LISTENING @AUTOMATIC
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class AutomaticMicrophoneActivation:
    """
    Automatic Microphone Activation System

    Enables passive and active listening without manual activation.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize automatic microphone activation"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("AutoMicActivation")

        # State
        self.microphone_active = False
        self.passive_listening = False
        self.active_listening = False
        self.auto_activate = True

        # Voice detection
        self.voice_detection_enabled = True
        self.voice_threshold = 0.5

        # Callbacks
        self.on_voice_detected: Optional[Callable] = None
        self.on_activation: Optional[Callable] = None

        # Threads
        self.listening_thread = None
        self.running = False

        # Audio stream (for real voice detection)
        self._audio = None
        self._audio_stream = None
        self._recognizer = None

        self.logger.info("=" * 80)
        self.logger.info("🎤 AUTOMATIC MICROPHONE ACTIVATION")
        self.logger.info("=" * 80)
        self.logger.info("   Passive Listening: ✅ ENABLED")
        self.logger.info("   Active Listening: ✅ ENABLED")
        self.logger.info("   Auto-Activate: ✅ ENABLED")
        self.logger.info("=" * 80)

    def activate_microphone(self) -> bool:
        """Activate microphone automatically - FAST activation"""
        if self.microphone_active:
            return True

        try:
            # FAST activation - immediate state change
            self.microphone_active = True

            # Trigger callback immediately (no delay)
            if self.on_activation:
                try:
                    self.on_activation()
                except:
                    pass  # Don't block activation on callback error

            self.logger.info("🎤 Microphone activated automatically (FAST)")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to activate microphone: {e}")
            return False

    def deactivate_microphone(self):
        """Deactivate microphone"""
        self.microphone_active = False
        self.logger.info("🎤 Microphone deactivated")

    def start_passive_listening(self):
        """Start passive listening (always on)"""
        if self.passive_listening:
            return

        self.passive_listening = True
        self.running = True

        # Start listening thread
        self.listening_thread = threading.Thread(target=self._passive_listening_loop, daemon=True)
        self.listening_thread.start()

        self.logger.info("👂 Passive listening started")

    def start_active_listening(self):
        """Start active listening (triggered)"""
        if self.active_listening:
            return

        self.active_listening = True
        self.activate_microphone()
        self.logger.info("👂 Active listening started")

    def _passive_listening_loop(self):
        """Passive listening loop"""
        while self.running:
            try:
                # Check for voice activity
                if self.voice_detection_enabled:
                    # Detect voice (simplified - would use actual voice detection)
                    voice_detected = self._detect_voice()

                    if voice_detected and not self.microphone_active:
                        # Auto-activate on voice detection
                        if self.auto_activate:
                            self.activate_microphone()
                            if self.on_voice_detected:
                                self.on_voice_detected()

                time.sleep(0.01)  # Check every 10ms for faster activation
            except Exception as e:
                self.logger.error(f"Error in passive listening: {e}")
                time.sleep(1.0)

    def _detect_voice(self) -> bool:
        """Detect voice activity - REAL IMPLEMENTATION"""
        try:
            # Try to use PyAudio for real voice detection
            import pyaudio
            import numpy as np

            if not hasattr(self, '_audio_stream') or self._audio_stream is None:
                # Initialize audio stream
                self._audio = pyaudio.PyAudio()
                self._audio_stream = self._audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024
                )

            # Read audio data
            audio_data = self._audio_stream.read(1024, exception_on_overflow=False)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # Calculate RMS (Root Mean Square) for volume detection
            rms = np.sqrt(np.mean(audio_array**2))

            # Voice threshold (adjustable)
            threshold = 500  # Adjust based on environment

            voice_detected = rms > threshold

            if voice_detected:
                self.logger.debug(f"🎤 Voice detected (RMS: {rms:.0f})")

            return voice_detected

        except ImportError:
            # Fallback: Try speech_recognition for VAD
            try:
                import speech_recognition as sr
                if not hasattr(self, '_recognizer'):
                    self._recognizer = sr.Recognizer()
                    self._recognizer.energy_threshold = 300
                    self._recognizer.dynamic_energy_threshold = True

                # Quick listen for voice activity
                with sr.Microphone() as source:
                    self._recognizer.adjust_for_ambient_noise(source, duration=0.1)
                    try:
                        audio = self._recognizer.listen(source, timeout=0.1, phrase_time_limit=0.1)
                        # If we got audio, voice was detected
                        return True
                    except sr.WaitTimeoutError:
                        return False
            except ImportError:
                # Final fallback: Always activate (no detection)
                self.logger.debug("⚠️  No voice detection libraries available - auto-activating")
                return True  # Auto-activate if no detection available
        except Exception as e:
            self.logger.debug(f"Voice detection error: {e}")
            return False

    def start(self):
        """Start automatic microphone activation - AUTOMATIC (no manual activation)"""
        # CRITICAL: Auto-activate immediately (no manual activation required)
        if self.auto_activate:
            self.activate_microphone()
            self.logger.info("🎤 Microphone AUTO-ACTIVATED (no manual activation required)")

        # Start passive listening (always on)
        self.start_passive_listening()

        # Start active listening (triggered)
        self.start_active_listening()

        self.logger.info("✅ Automatic microphone activation started")
        self.logger.info("   🎤 Microphone: ACTIVE")
        self.logger.info("   👂 Passive Listening: ACTIVE")
        self.logger.info("   👂 Active Listening: ACTIVE")

    def stop(self):
        """Stop automatic microphone activation"""
        self.running = False
        self.passive_listening = False
        self.active_listening = False
        self.deactivate_microphone()

        # Clean up audio stream
        if hasattr(self, '_audio_stream') and self._audio_stream:
            try:
                self._audio_stream.stop_stream()
                self._audio_stream.close()
            except:
                pass
            self._audio_stream = None

        if hasattr(self, '_audio') and self._audio:
            try:
                self._audio.terminate()
            except:
                pass
            self._audio = None

        self.logger.info("⏹️  Automatic microphone activation stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Automatic Microphone Activation")
    parser.add_argument("--start", action="store_true", help="Start automatic activation")
    parser.add_argument("--stop", action="store_true", help="Stop activation")

    args = parser.parse_args()

    activation = AutomaticMicrophoneActivation()

    if args.start:
        activation.start()
        try:
            while activation.running:
                time.sleep(1)
        except KeyboardInterrupt:
            activation.stop()

    if args.stop:
        activation.stop()


if __name__ == "__main__":


    main()