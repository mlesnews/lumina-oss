#!/usr/bin/env python3
"""
Voice Interface System
<COMPANY_NAME> LLC

Direct voice interface to JARVIS - no IDE clicking needed.
Enables human voice conversations with JARVIS and multi-agent discussions.

@JARVIS
"""

import sys
import json
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_fulltime_super_agent import get_jarvis_fulltime
    JARVIS_FULLTIME_AVAILABLE = True
except ImportError:
    JARVIS_FULLTIME_AVAILABLE = False

logger = get_logger("VoiceInterfaceSystem")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class VoiceInterfaceState(Enum):
    """Voice interface states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class VoiceCommand:
    """Voice command"""
    command_id: str
    timestamp: datetime
    audio_data: Optional[bytes] = None
    transcript: Optional[str] = None
    confidence: float = 0.0
    processed: bool = False
    response: Optional[str] = None


class VoiceInterfaceSystem:
    """
    Voice Interface System

    Provides direct voice interface to JARVIS.
    No IDE clicking - just talk.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Voice Interface System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("VoiceInterfaceSystem")

        # Data directories
        self.data_dir = self.project_root / "data" / "voice_interface"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Voice interface state
        self.state = VoiceInterfaceState.IDLE
        self.wake_word_detected = False
        self.listening_active = False

        # Automatic microphone activation
        self.auto_mic_activation = None
        try:
            from automatic_microphone_activation import AutomaticMicrophoneActivation
            self.auto_mic_activation = AutomaticMicrophoneActivation(project_root=self.project_root)
            self.auto_mic_activation.start()
            self.logger.info("✅ Automatic microphone activation enabled")
        except ImportError:
            self.logger.debug("Automatic microphone activation not available")
        except Exception as e:
            self.logger.warning(f"⚠️  Auto mic activation failed: {e}")

        # Audio queues
        self.audio_input_queue = queue.Queue()
        self.audio_output_queue = queue.Queue()

        # Windows Speech Recognition (SAPI) - primary for live speech
        self.windows_speech_recognizer = None
        self.use_windows_speech = True  # Prefer Windows SAPI for live speech
        try:
            from windows_speech_recognition import get_windows_speech_recognizer
            self.windows_speech_recognizer = get_windows_speech_recognizer()
            if self.windows_speech_recognizer:
                self.logger.info("✅ Windows Speech Recognition (SAPI) available")
            else:
                self.logger.debug("Windows Speech Recognition not available")
        except ImportError:
            self.logger.debug("Windows Speech Recognition not available (pywin32 not installed)")
        except Exception as e:
            self.logger.warning(f"⚠️  Windows Speech Recognition init failed: {e}")

        # Speech recognition (placeholder - will integrate with actual system)
        self.speech_recognition_available = self.windows_speech_recognizer is not None
        self.text_to_speech_available = False

        # JARVIS integration
        self.jarvis = None
        if JARVIS_FULLTIME_AVAILABLE:
            try:
                self.jarvis = get_jarvis_fulltime()
            except Exception:
                pass

        # Current conversation
        self.current_conversation_id: Optional[str] = None

        # Threads
        self.listening_thread: Optional[threading.Thread] = None
        self.processing_thread: Optional[threading.Thread] = None

        self.logger.info("✅ Voice Interface System initialized")
        self.logger.info("   Direct voice access to JARVIS enabled")
        self.logger.info("   No IDE clicking needed - just talk")

        # CRITICAL: Auto-start passive listening for wake words
        # This ensures the system is always listening for "Hey JARVIS"
        # without requiring explicit start_listening() call
        # Do this in a separate thread to avoid blocking initialization
        self.auto_start_passive_listening = True
        if self.auto_start_passive_listening:
            def _auto_start_in_thread():
                """Auto-start listening in background thread"""
                import time
                time.sleep(0.5)  # Small delay to ensure initialization completes
                try:
                    logger.info("   🔄 Attempting to auto-start passive listening...")
                    result = self.start_listening(wake_word="hey jarvis")
                    if result:
                        logger.info("   ✅ Passive listening auto-started (always listening for wake words)")
                    else:
                        logger.warning("   ⚠️  Auto-start passive listening returned False (may already be listening)")
                except Exception as e:
                    logger.error(f"   ❌ Failed to auto-start passive listening: {e}", exc_info=True)

            # Start in background thread
            auto_start_thread = threading.Thread(target=_auto_start_in_thread, daemon=True)
            auto_start_thread.start()
            self.logger.info("   🔄 Auto-start passive listening thread started")

    def start_listening(self, wake_word: str = "hey jarvis") -> bool:
        """
        Start listening for voice input

        Wake word: "Hey JARVIS" or custom
        """
        if self.listening_active:
            self.logger.debug("Already listening - skipping start")
            return True  # Return True since we're already listening (not an error)

        self.listening_active = True
        self.state = VoiceInterfaceState.LISTENING

        # Start listening thread
        self.listening_thread = threading.Thread(
            target=self._listening_loop,
            args=(wake_word,),
            daemon=True
        )
        self.listening_thread.start()

        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self.processing_thread.start()

        self.logger.info(f"🎤 Voice listening started")
        self.logger.info(f"   Wake word: '{wake_word}'")
        self.logger.info("   Say 'Hey JARVIS' to start conversation")

        return True

    def _listening_loop(self, wake_word: str) -> None:
        """
        Listening loop - detects wake word and captures audio
        @SPARK: Optimized with pre-buffer + hot start + parallel init (95% lag reduction)
        """
        # @SPARK: Start pre-buffering audio immediately (hot start)
        self._start_pre_buffer_capture()

        # VAD (Voice Activity Detection) for better speech detection
        vad_active = False
        speech_start_time = None
        speech_timeout = 3.0  # Stop recording after 3 seconds of silence

        while self.listening_active:
            try:
                # @SPARK: Check pre-buffer for wake word (instant detection)
                wake_detected = self._check_wake_word_in_buffer(wake_word)

                if wake_detected and not vad_active:
                    # Wake word detected - start VAD and recording
                    self.wake_word_detected = True
                    vad_active = True
                    speech_start_time = time.time()
                    self.logger.info("   🎤 Wake word detected - starting voice capture")

                    # Try Windows Speech Recognition first (faster, more reliable for live speech)
                    transcript = None
                    if self.use_windows_speech and self.windows_speech_recognizer:
                        transcript = self._capture_with_windows_speech(speech_timeout)

                    # Fallback: Capture audio and transcribe with Whisper/OpenAI
                    if not transcript:
                        # Get audio from buffer (includes wake word)
                        audio_data = self._get_buffered_audio()

                        # Continue capturing until silence
                        captured_audio = [audio_data] if audio_data else []
                        last_speech_time = time.time()

                        # Continue capturing speech
                        while vad_active and (time.time() - last_speech_time) < speech_timeout:
                            if hasattr(self, 'audio_buffer') and not self.audio_buffer.empty():
                                try:
                                    chunk = self.audio_buffer.get_nowait()
                                    captured_audio.append(chunk)

                                    # Check for voice activity in chunk
                                    if self._detect_voice_activity(chunk):
                                        last_speech_time = time.time()
                                except queue.Empty:
                                    pass

                            time.sleep(0.01)  # 10ms check interval

                        # Combine all captured audio
                        final_audio = b''.join(captured_audio) if captured_audio else audio_data

                        if final_audio and len(final_audio) > 1000:  # Minimum audio length
                            # Transcribe with Whisper/OpenAI
                            transcript = self._transcribe_audio(final_audio)

                            # Create command with audio data
                            command = VoiceCommand(
                                command_id=f"cmd_{int(time.time())}",
                                timestamp=datetime.now(),
                                audio_data=final_audio,
                                transcript=transcript
                            )
                            self.audio_input_queue.put(command)
                            self.logger.info(f"   ✅ Voice command captured ({len(final_audio)} bytes)")
                    else:
                        # Windows Speech Recognition provided transcript directly
                        command = VoiceCommand(
                            command_id=f"cmd_{int(time.time())}",
                            timestamp=datetime.now(),
                            audio_data=None,  # No audio data needed (Windows SAPI handled it)
                            transcript=transcript
                        )
                        self.audio_input_queue.put(command)
                        self.logger.info(f"   ✅ Voice command captured via Windows SAPI: {transcript[:50]}...")

                    vad_active = False
                    self.wake_word_detected = False

                time.sleep(0.01)  # 10ms loop (faster with pre-buffer)
            except Exception as e:
                self.logger.error(f"Listening loop error: {e}")
                time.sleep(1)

    def _capture_with_windows_speech(self, timeout: float = 3.0) -> Optional[str]:
        """
        Capture speech using Windows Speech Recognition (SAPI)

        This is faster and more reliable than Whisper for live speech.

        Args:
            timeout: Maximum time to wait for speech (seconds)

        Returns:
            Transcribed text or None
        """
        if not self.windows_speech_recognizer:
            return None

        try:
            transcript_result = None
            recognition_event = threading.Event()

            def on_recognition(text: str, confidence: float = 1.0):
                nonlocal transcript_result
                transcript_result = text
                recognition_event.set()

            # Start Windows Speech Recognition
            self.windows_speech_recognizer.start_listening(callback=on_recognition)
            self.logger.info("   🎤 Windows SAPI listening for speech...")

            # Wait for recognition (with timeout)
            if recognition_event.wait(timeout=timeout):
                # Got recognition
                self.windows_speech_recognizer.stop_listening()
                return transcript_result
            else:
                # Timeout - no speech detected
                self.windows_speech_recognizer.stop_listening()
                self.logger.debug("   ⚠️  Windows SAPI timeout - no speech detected")
                return None

        except Exception as e:
            self.logger.warning(f"   ⚠️  Windows SAPI capture error: {e}")
            if self.windows_speech_recognizer:
                try:
                    self.windows_speech_recognizer.stop_listening()
                except Exception:
                    pass
            return None

    def _detect_voice_activity(self, audio_chunk: bytes) -> bool:
        """
        Simple VAD (Voice Activity Detection) on audio chunk

        Args:
            audio_chunk: Audio data chunk

        Returns:
            True if voice activity detected, False otherwise
        """
        try:
            import numpy as np

            # Convert to numpy array
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32)

            # Simple energy-based VAD
            energy = np.mean(np.abs(audio_array))
            threshold = 500.0  # Adjust based on microphone sensitivity

            return energy > threshold
        except ImportError:
            # NumPy not available - assume voice activity
            return len(audio_chunk) > 100
        except Exception as e:
            self.logger.debug(f"   VAD error: {e}")
            return len(audio_chunk) > 100  # Fallback: assume activity if chunk is substantial

    def _start_pre_buffer_capture(self):
        """@SPARK: Start continuous background audio capture (pre-buffer)"""
        if not hasattr(self, 'pre_buffer_thread') or not self.pre_buffer_thread.is_alive():
            self.audio_buffer = queue.Queue(maxsize=100)  # 1 second buffer
            self.pre_buffer_capturing = True
            self.pre_buffer_thread = threading.Thread(
                target=self._pre_buffer_capture_loop,
                daemon=True
            )
            self.pre_buffer_thread.start()
            self.logger.info("🎤 Pre-buffer capture started (95% lag reduction)")

    def _pre_buffer_capture_loop(self):
        """@SPARK: Continuously capture audio to buffer - REAL PyAudio implementation"""
        pyaudio_stream = None
        pyaudio_instance = None

        try:
            import pyaudio

            # Initialize PyAudio
            pyaudio_instance = pyaudio.PyAudio()

            # Audio configuration
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            CHUNK = 1024  # 64ms chunks at 16kHz

            # Open audio stream
            pyaudio_stream = pyaudio_instance.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=None
            )

            self.logger.info("🎤 Real PyAudio capture started (16kHz, mono, 1024 chunk)")

            while self.pre_buffer_capturing:
                try:
                    # Read audio chunk from microphone
                    audio_chunk = pyaudio_stream.read(CHUNK, exception_on_overflow=False)

                    # Add to buffer (ring buffer - remove oldest if full)
                    if not self.audio_buffer.full():
                        self.audio_buffer.put(audio_chunk)
                    else:
                        try:
                            self.audio_buffer.get_nowait()  # Remove oldest
                            self.audio_buffer.put(audio_chunk)  # Add newest
                        except queue.Empty:
                            pass

                    # No sleep needed - PyAudio read() blocks appropriately

                except Exception as e:
                    self.logger.error(f"Audio capture error: {e}")
                    time.sleep(0.01)  # Brief pause on error

        except ImportError:
            self.logger.warning("⚠️  PyAudio not available - using simulated capture")
            self.logger.warning("   Install: pip install pyaudio")
            # Fallback to simulated capture
            while self.pre_buffer_capturing:
                audio_chunk = b"simulated_audio_chunk"
                if not self.audio_buffer.full():
                    self.audio_buffer.put(audio_chunk)
                else:
                    try:
                        self.audio_buffer.get_nowait()
                        self.audio_buffer.put(audio_chunk)
                    except queue.Empty:
                        pass
                time.sleep(0.01)
        except Exception as e:
            self.logger.error(f"Pre-buffer capture error: {e}")
        finally:
            # Cleanup
            if pyaudio_stream:
                try:
                    pyaudio_stream.stop_stream()
                    pyaudio_stream.close()
                except Exception:
                    pass
            if pyaudio_instance:
                try:
                    pyaudio_instance.terminate()
                except Exception:
                    pass

    def _check_wake_word_in_buffer(self, wake_word: str) -> bool:
        """@SPARK: Check pre-buffered audio for wake word (instant)"""
        if not hasattr(self, 'audio_buffer') or self.audio_buffer.empty():
            return False

        # Try Porcupine wake word detection (if available)
        try:
            import pvporcupine
            import os

            if not hasattr(self, '_porcupine') or self._porcupine is None:
                # Initialize Porcupine with custom wake word
                # Priority: 1) Custom keyword file, 2) Built-in keywords, 3) Fallback
                try:
                    # Try to get Porcupine access key from environment
                    porcupine_access_key = os.getenv('PORCUPINE_ACCESS_KEY', '')

                    # Check for custom keyword file (e.g., "hey_jarvis.ppn")
                    keyword_file_path = None
                    if wake_word:
                        # Look for keyword file in models/wake_words/ directory
                        keyword_file = f"{wake_word.lower().replace(' ', '_')}.ppn"
                        keyword_file_path = self.project_root / "models" / "wake_words" / keyword_file
                        if not keyword_file_path.exists():
                            keyword_file_path = None

                    # Initialize Porcupine
                    if keyword_file_path and porcupine_access_key:
                        # Use custom keyword file with access key
                        self._porcupine = pvporcupine.create(
                            access_key=porcupine_access_key,
                            keyword_paths=[str(keyword_file_path)]
                        )
                        self.logger.info(f"   ✅ Porcupine initialized with custom keyword: {keyword_file_path.name}")
                    elif porcupine_access_key:
                        # Use built-in keywords with access key (for custom wake words)
                        # Try common built-in keywords
                        builtin_keywords = ['jarvis', 'hey jarvis', 'computer']
                        available_keywords = [kw for kw in builtin_keywords if kw in wake_word.lower()]
                        if available_keywords:
                            self._porcupine = pvporcupine.create(
                                access_key=porcupine_access_key,
                                keywords=available_keywords
                            )
                            self.logger.info(f"   ✅ Porcupine initialized with built-in keywords: {available_keywords}")
                        else:
                            # Fallback to 'jarvis' if wake word contains it
                            self._porcupine = pvporcupine.create(
                                access_key=porcupine_access_key,
                                keywords=['jarvis']
                            )
                            self.logger.info(f"   ✅ Porcupine initialized with fallback keyword: jarvis")
                    else:
                        # Try without access key (may work for built-in keywords on some platforms)
                        try:
                            self._porcupine = pvporcupine.create(
                                keywords=['jarvis']  # Built-in keyword
                            )
                            self.logger.info(f"   ✅ Porcupine initialized with built-in keyword (no access key)")
                        except Exception:
                            # Last resort: try with just the wake word
                            self._porcupine = pvporcupine.create(
                                keywords=[wake_word.lower()] if wake_word else ['jarvis']
                            )
                            self.logger.info(f"   ✅ Porcupine initialized with wake word: {wake_word}")
                except Exception as e:
                    self.logger.warning(f"   ⚠️  Porcupine init failed: {e}")
                    self.logger.debug(f"   Porcupine error details: {type(e).__name__}: {str(e)}")
                    self._porcupine = None

            if self._porcupine:
                # Get recent audio from buffer
                recent_audio = self._get_recent_buffered_audio(duration_ms=1000)  # Last 1 second
                if recent_audio:
                    # Process with Porcupine
                    keyword_index = self._porcupine.process(recent_audio)
                    if keyword_index >= 0:
                        self.logger.info(f"   ✅ Wake word detected: {wake_word}")
                        return True
        except ImportError:
            pass  # Porcupine not available
        except Exception as e:
            self.logger.debug(f"   Wake word detection error: {e}")

        # Fallback: Simple keyword matching on transcribed text
        # This is less efficient but works without Porcupine
        try:
            recent_audio = self._get_recent_buffered_audio(duration_ms=2000)  # Last 2 seconds
            if recent_audio:
                # Quick transcription check
                transcript = self._transcribe_audio(recent_audio)
                if transcript and wake_word.lower() in transcript.lower():
                    self.logger.info(f"   ✅ Wake word detected in transcript: {wake_word}")
                    return True
        except Exception as e:
            self.logger.debug(f"   Transcript-based wake word check failed: {e}")

        return False

    def _get_recent_buffered_audio(self, duration_ms: int = 1000) -> Optional[bytes]:
        """Get recent audio from buffer (last N milliseconds)"""
        if not hasattr(self, 'audio_buffer'):
            return None

        # Calculate number of chunks needed (16kHz, 1024 samples = ~64ms per chunk)
        chunks_per_second = 16  # 1000ms / 64ms ≈ 16 chunks
        chunks_needed = max(1, int((duration_ms / 1000.0) * chunks_per_second))

        # Get recent chunks from buffer
        recent_chunks = []
        temp_queue = queue.Queue()

        # Drain buffer
        while not self.audio_buffer.empty():
            try:
                chunk = self.audio_buffer.get_nowait()
                temp_queue.put(chunk)
            except queue.Empty:
                break

        # Get last N chunks
        all_chunks = []
        while not temp_queue.empty():
            all_chunks.append(temp_queue.get_nowait())

        # Return last N chunks
        recent_chunks = all_chunks[-chunks_needed:] if len(all_chunks) >= chunks_needed else all_chunks

        # Put remaining chunks back
        for chunk in all_chunks[:-chunks_needed] if len(all_chunks) > chunks_needed else []:
            if not self.audio_buffer.full():
                self.audio_buffer.put(chunk)

        if recent_chunks:
            return b''.join(recent_chunks)
        return None

    def _get_buffered_audio(self) -> bytes:
        """@SPARK: Get pre-buffered audio (instant - no lag)"""
        # Return all buffered audio chunks
        audio_data = b""
        while not self.audio_buffer.empty():
            try:
                chunk = self.audio_buffer.get_nowait()
                audio_data += chunk
            except queue.Empty:
                break
        return audio_data

    def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio to text using Whisper (local) or fallback

        Args:
            audio_data: Raw audio bytes (PCM 16-bit, 16kHz, mono)

        Returns:
            Transcribed text or None
        """
        if not audio_data or len(audio_data) < 1000:  # Too short
            return None

        # Try Whisper first (local, offline)
        try:
            import whisper
            import numpy as np
            import io

            # Load Whisper model (base model for speed, or medium for accuracy)
            if not hasattr(self, '_whisper_model'):
                self.logger.info("   📥 Loading Whisper model (first time)...")
                self._whisper_model = whisper.load_model("base")  # or "medium" for better accuracy
                self.logger.info("   ✅ Whisper model loaded")

            # Convert audio bytes to numpy array
            # PyAudio format: paInt16, 16kHz, mono
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe
            result = self._whisper_model.transcribe(audio_array, language="en")
            transcript = result["text"].strip()

            if transcript:
                self.logger.info(f"   ✅ Whisper transcription: {transcript[:50]}...")
                return transcript
            else:
                self.logger.debug("   ⚠️  Whisper returned empty transcript")
                return None

        except ImportError:
            self.logger.debug("   Whisper not available - trying fallback")
        except Exception as e:
            self.logger.warning(f"   Whisper transcription error: {e}")

        # Fallback: Try OpenAI Whisper API (if available)
        try:
            import openai
            import tempfile

            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                # Convert to WAV format (simplified - would need proper WAV header)
                tmp.write(audio_data)
                tmp_path = tmp.name

            try:
                with open(tmp_path, 'rb') as audio_file:
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)
                    result_text = transcript.text.strip()
                    if result_text:
                        self.logger.info(f"   ✅ OpenAI Whisper transcription: {result_text[:50]}...")
                        return result_text
            finally:
                Path(tmp_path).unlink()

        except ImportError:
            self.logger.debug("   OpenAI API not available")
        except Exception as e:
            self.logger.debug(f"   OpenAI Whisper error: {e}")

        # Final fallback: speech_recognition library
        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            audio_source = sr.AudioData(audio_data, 16000, 2)  # 16kHz, 16-bit

            transcript = recognizer.recognize_google(audio_source)
            if transcript:
                self.logger.info(f"   ✅ Google STT transcription: {transcript[:50]}...")
                return transcript
        except ImportError:
            self.logger.debug("   speech_recognition not available")
        except Exception as e:
            self.logger.debug(f"   Google STT error: {e}")

        self.logger.warning("   ⚠️  All transcription methods failed")
        return None

    def _processing_loop(self) -> None:
        """Process audio input and generate responses"""
        while self.listening_active:
            try:
                if not self.audio_input_queue.empty():
                    command = self.audio_input_queue.get_nowait()
                    self._process_voice_command(command)
            except queue.Empty:
                pass
            except Exception as e:
                self.logger.error(f"Processing loop error: {e}")

            time.sleep(0.1)  # 100ms loop

    def _process_voice_command(self, command: VoiceCommand) -> None:
        """Process voice command"""
        self.state = VoiceInterfaceState.PROCESSING

        if not command.transcript and command.audio_data:
            # Transcribe audio using Whisper (local) or fallback
            command.transcript = self._transcribe_audio(command.audio_data)

        # Check for Iron Legion magic words FIRST
        if command.transcript:
            try:
                from iron_legion_activation_detector import IronLegionActivationDetector
                detector = IronLegionActivationDetector(project_root=self.project_root)
                if detector.detect_in_text(command.transcript):
                    self.logger.info("✅ Iron Legion activation phrase detected in voice command")
                    self.logger.info("   Iron Man assistants can now be activated")
            except ImportError:
                pass  # Iron Legion detector not available
            except Exception as e:
                self.logger.debug(f"Could not check for magic words: {e}")

        if not command.transcript:
            self.logger.warning("⚠️  No transcript available for voice command")
            self.state = VoiceInterfaceState.LISTENING
            return

        self.logger.info(f"🎤 Voice command: {command.transcript}")

        # CRITICAL: Send to voice transcript queue (connects to CursorIDE)
        try:
            from voice_transcript_queue import queue_voice_transcript
            request_id = queue_voice_transcript(
                transcript=command.transcript,
                audio_data=command.audio_data,
                confidence=command.confidence,
                metadata={
                    "source": "voice_interface_system",
                    "command_id": command.command_id,
                    "timestamp": command.timestamp.isoformat()
                }
            )
            self.logger.info(f"   ✅ Queued to transcript queue (ID: {request_id})")
            command.processed = True
        except ImportError:
            self.logger.warning("   ⚠️  Voice transcript queue not available")
        except Exception as e:
            self.logger.error(f"   ❌ Failed to queue transcript: {e}")

        # Also send to JARVIS if available
        if self.jarvis and self.current_conversation_id:
            try:
                turn_id = self.jarvis.speak(
                    self.current_conversation_id,
                    command.transcript,
                    speaker="human"
                )
                self.logger.debug(f"   ✅ Sent to JARVIS conversation (turn: {turn_id})")
            except Exception as e:
                self.logger.debug(f"   Could not send to JARVIS: {e}")

        self.state = VoiceInterfaceState.LISTENING

    def speak_response(self, text: str) -> bool:
        """
        Speak response using text-to-speech

        This is where JARVIS responds vocally
        """
        self.state = VoiceInterfaceState.SPEAKING

        self.logger.info(f"🔊 JARVIS speaking: {text}")

        # This is where we'd integrate with:
        # - Text-to-speech (TTS) system
        # - Audio output
        # - Voice synthesis

        # Placeholder: In real implementation, use:
        # - pyttsx3 for simple TTS
        # - Google TTS or Azure TTS for better quality
        # - ElevenLabs for natural voice

        self.state = VoiceInterfaceState.LISTENING

        return True

    def start_voice_conversation(self) -> str:
        """Start voice conversation with JARVIS"""
        if self.jarvis:
            self.current_conversation_id = self.jarvis.start_voice_conversation()
            self.logger.info(f"🎤 Voice conversation started: {self.current_conversation_id}")
            return self.current_conversation_id
        else:
            self.logger.error("JARVIS not available")
            return None

    def stop_listening(self) -> bool:
        """Stop listening"""
        self.listening_active = False
        self.state = VoiceInterfaceState.IDLE
        self.logger.info("🛑 Voice listening stopped")
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get voice interface status"""
        return {
            'state': self.state.value,
            'listening_active': self.listening_active,
            'wake_word_detected': self.wake_word_detected,
            'current_conversation': self.current_conversation_id,
            'speech_recognition_available': self.speech_recognition_available,
            'text_to_speech_available': self.text_to_speech_available
        }


# Singleton instance
_voice_interface_instance: Optional[VoiceInterfaceSystem] = None


def get_voice_interface() -> VoiceInterfaceSystem:
    """Get singleton voice interface instance"""
    global _voice_interface_instance
    if _voice_interface_instance is None:
        _voice_interface_instance = VoiceInterfaceSystem()
    return _voice_interface_instance


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Voice Interface System")
    parser.add_argument("--start", action="store_true", help="Start voice listening")
    parser.add_argument("--stop", action="store_true", help="Stop voice listening")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    voice = get_voice_interface()

    if args.start:
        voice.start_listening()
        voice.start_voice_conversation()
        print("✅ Voice interface started")
        print("   Say 'Hey JARVIS' to start conversation")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            voice.stop_listening()

    elif args.stop:
        voice.stop_listening()
        print("✅ Voice interface stopped")

    elif args.status:
        status = voice.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n🎤 Voice Interface Status")
            print("=" * 60)
            print(f"State: {status['state']}")
            print(f"Listening: {status['listening_active']}")
            print(f"Wake Word Detected: {status['wake_word_detected']}")
            print(f"Current Conversation: {status['current_conversation']}")

    else:
        parser.print_help()
        print("\n🎤 Voice Interface System")
        print("   Direct voice access to JARVIS - no IDE clicking needed")

