#!/usr/bin/env python3
"""
Windows Speech Recognition (SAPI) Integration

Provides speech-to-text using Windows native Speech API.
Used after wake word detection for transcribing voice commands.

@LUMINA @JARVIS
"""

import threading
import queue
import time
from typing import Optional, Callable
from datetime import datetime
from pathlib import Path

try:
    import win32com.client
    import pythoncom
    WINDOWS_SPEECH_AVAILABLE = True
except ImportError:
    WINDOWS_SPEECH_AVAILABLE = False

from lumina_logger import get_logger

logger = get_logger("WindowsSpeechRecognition")


class WindowsSpeechRecognizer:
    """
    Windows Speech Recognition using SAPI (Speech API)

    Provides speech-to-text functionality using Windows native APIs.
    More reliable and faster than Whisper for simple commands.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Windows Speech Recognition"""
        if not WINDOWS_SPEECH_AVAILABLE:
            raise ImportError("Windows Speech Recognition not available (win32com not installed)")

        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("WindowsSpeechRecognition")

        # Recognition state
        self.recognizer = None
        self.context = None
        self.grammar = None
        self.event_handler = None
        self.is_listening = False
        self.recognition_thread = None

        # Results queue
        self.recognition_queue = queue.Queue()
        self.current_transcript = None
        self.recognition_callback: Optional[Callable[[str], None]] = None

        # Initialize SAPI
        self._initialize_sapi()

        self.logger.info("✅ Windows Speech Recognition initialized")

    def _initialize_sapi(self):
        """Initialize Windows Speech API components"""
        try:
            # Create shared recognizer
            self.recognizer = win32com.client.Dispatch("SAPI.SpSharedRecognizer")

            # Create recognition context
            self.context = self.recognizer.CreateRecoContext()

            # Create grammar for dictation (free-form speech)
            self.grammar = self.context.CreateGrammar()

            # Enable dictation mode (free-form speech recognition)
            self.grammar.DictationSetState(1)  # 1 = enabled

            # Set up event handler
            self.event_handler = ContextEvents(self.context, self._on_recognition)

            # Set event interests (we want recognition events)
            self.context.EventInterests = 1  # SPEI_RECOGNITION

            self.logger.info("   ✅ SAPI components initialized")
            self.logger.info("   ✅ Dictation mode enabled (free-form speech)")

        except Exception as e:
            self.logger.error(f"   ❌ Failed to initialize SAPI: {e}")
            raise

    def _on_recognition(self, text: str, confidence: float = 1.0):
        """
        Callback when speech is recognized

        Args:
            text: Recognized text
            confidence: Recognition confidence (0.0-1.0)
        """
        if text:
            self.current_transcript = text
            self.recognition_queue.put({
                'text': text,
                'confidence': confidence,
                'timestamp': datetime.now()
            })

            self.logger.info(f"   ✅ Windows SAPI recognized: {text[:50]}...")

            # Call user callback if set
            if self.recognition_callback:
                try:
                    self.recognition_callback(text)
                except Exception as e:
                    self.logger.warning(f"   ⚠️  Recognition callback error: {e}")

    def start_listening(self, callback: Optional[Callable[[str], None]] = None):
        """
        Start listening for speech

        Args:
            callback: Optional callback function called when speech is recognized
        """
        if self.is_listening:
            self.logger.warning("Already listening")
            return

        self.recognition_callback = callback
        self.is_listening = True

        # Start recognition thread (needed for COM message pumping)
        self.recognition_thread = threading.Thread(
            target=self._recognition_loop,
            daemon=True
        )
        self.recognition_thread.start()

        self.logger.info("   ✅ Windows Speech Recognition started")

    def stop_listening(self):
        """Stop listening for speech"""
        if not self.is_listening:
            return

        self.is_listening = False

        # Disable dictation
        if self.grammar:
            try:
                self.grammar.DictationSetState(0)  # Disable
            except Exception:
                pass

        self.logger.info("   ✅ Windows Speech Recognition stopped")

    def _recognition_loop(self):
        """Recognition loop - pumps Windows messages for COM events"""
        try:
            while self.is_listening:
                pythoncom.PumpWaitingMessages()  # type: ignore
                time.sleep(0.01)  # Small delay to prevent CPU spinning
        except (RuntimeError, OSError, AttributeError) as e:
            self.logger.error("   ❌ Recognition loop error: %s", e)

    def transcribe_audio_file(self, _audio_file_path: str) -> Optional[str]:
        """
        Transcribe audio file using Windows Speech Recognition

        Note: SAPI works best with live audio streams.
        For file transcription, Whisper may be better.

        Args:
            _audio_file_path: Path to audio file (unused - SAPI is for live streams)

        Returns:
            Transcribed text or None
        """
        # SAPI is primarily for live recognition, not file transcription
        # This is a placeholder - for files, use Whisper instead
        self.logger.warning("   ⚠️  SAPI transcribe_audio_file not fully implemented - use Whisper for files")
        return None

    def get_latest_transcript(self, timeout: float = 1.0) -> Optional[str]:
        """
        Get latest recognized transcript

        Args:
            timeout: Maximum time to wait for new transcript

        Returns:
            Latest transcript or None
        """
        try:
            result = self.recognition_queue.get(timeout=timeout)
            return result.get('text') if result else None
        except queue.Empty:
            return self.current_transcript

    def clear_queue(self):
        """Clear the recognition queue"""
        while not self.recognition_queue.empty():
            try:
                self.recognition_queue.get_nowait()
            except queue.Empty:
                break


class ContextEvents(win32com.client.getevents("SAPI.SpRecoContext")):
    """
    Event handler for SAPI recognition events
    """

    def __init__(self, context, recognition_callback: Callable[[str], None]):
        super().__init__(context)
        self.recognition_callback = recognition_callback
        self.logger = get_logger("WindowsSpeechRecognition.Events")

    def OnRecognition(self, _stream_number, _stream_position, _recognition_type, result):
        """
        Called when speech is recognized

        Args:
            _stream_number: Audio stream number (unused)
            _stream_position: Position in stream (unused)
            _recognition_type: Type of recognition (unused)
            result: Recognition result object
        """
        try:
            # Get the recognized text
            result_obj = win32com.client.Dispatch(result)
            recognized_text = result_obj.PhraseInfo.GetText()

            # Get confidence (if available)
            confidence = 1.0
            try:
                confidence = result_obj.PhraseInfo.GetRule().GetConfidence()
            except (AttributeError, RuntimeError):
                pass

            # Call callback
            if recognized_text and self.recognition_callback:
                self.recognition_callback(recognized_text.strip(), confidence)

        except (AttributeError, RuntimeError, OSError) as e:
            self.logger.error("   ❌ Error processing recognition: %s", e)


# Singleton instance
_windows_speech_instance: Optional[WindowsSpeechRecognizer] = None


def get_windows_speech_recognizer() -> Optional[WindowsSpeechRecognizer]:
    """
    Get singleton Windows Speech Recognition instance

    Returns:
        WindowsSpeechRecognizer instance or None if not available
    """
    global _windows_speech_instance

    if not WINDOWS_SPEECH_AVAILABLE:
        return None

    if _windows_speech_instance is None:
        try:
            _windows_speech_instance = WindowsSpeechRecognizer()
        except (ImportError, RuntimeError, OSError) as e:
            logger.error("Failed to create Windows Speech Recognizer: %s", e)
            return None

    return _windows_speech_instance


if __name__ == "__main__":
    # Test Windows Speech Recognition
    print("Testing Windows Speech Recognition...")

    if not WINDOWS_SPEECH_AVAILABLE:
        print("❌ Windows Speech Recognition not available")
        print("   Install: pip install pywin32")
        exit(1)

    recognizer = get_windows_speech_recognizer()
    if not recognizer:
        print("❌ Failed to initialize Windows Speech Recognition")
        exit(1)

    print("✅ Windows Speech Recognition initialized")
    print("   Say something... (Press Ctrl+C to stop)")

    def on_recognition(text: str, confidence: float = 1.0):
        print(f"   Recognized: {text} (confidence: {confidence:.2f})")

    recognizer.start_listening(callback=on_recognition)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        recognizer.stop_listening()
        print("\n✅ Stopped")
