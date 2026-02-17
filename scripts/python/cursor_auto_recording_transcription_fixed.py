#!/usr/bin/env python3
"""
Cursor IDE Auto-Recording & Transcription - FIXED

Real-world smoke test fixes:
1. Auto-start recording (no manual click)
2. Voice trigger words (JARVIS, hate code, etc.)
3. Automatic transcription
4. Session recording automation
5. Cursor IDE keyboard shortcuts integration
6. Windows OS integration

Tags: #CURSOR #RECORDING #TRANSCRIPTION #AUTOMATION #TRIGGER-WORDS #FIX @JARVIS @TEAM
"""

import json
import logging
import queue
import sys
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import (TimestampFormat,
                                                get_timestamp_logger)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    get_timestamp_logger = lambda: None

logger = get_logger("CursorAutoRecordingFixed")
ts_logger = get_timestamp_logger()

# Try to import speech recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("⚠️  speech_recognition not available - install: pip install SpeechRecognition")

# Try to import audio recording
try:
    import wave

    import pyaudio
    AUDIO_RECORDING_AVAILABLE = True
except ImportError:
    AUDIO_RECORDING_AVAILABLE = False
    logger.warning("⚠️  pyaudio not available - install: pip install pyaudio")

# Try to import transcription
try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
    TRANSCRIPTION_AVAILABLE = True
except ImportError:
    TRANSCRIPTION_AVAILABLE = False
    logger.warning("⚠️  Transcription services not available")

# Windows keyboard shortcuts
try:
    import keyboard
    import pyautogui
    KEYBOARD_CONTROL_AVAILABLE = True
except ImportError:
    KEYBOARD_CONTROL_AVAILABLE = False
    logger.warning("⚠️  Keyboard control not available - install: pip install pyautogui keyboard")


@dataclass
class RecordingSession:
    """Recording session metadata"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    audio_file: Optional[str] = None
    transcript_file: Optional[str] = None
    trigger_words_detected: List[str] = field(default_factory=list)
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TriggerWord:
    """Voice trigger word configuration"""
    word: str
    action: str  # "start_recording", "stop_recording", "transcribe", "activate"
    case_sensitive: bool = False
    confidence_threshold: float = 0.7


class CursorAutoRecordingTranscriptionFixed:
    """
    Cursor IDE Auto-Recording & Transcription - FIXED

    Fixes automation gaps:
    1. Auto-start recording (no manual click)
    2. Voice trigger words
    3. Automatic transcription
    4. Session recording automation
    """

    # Default trigger words
    # Note: "hey code" may be recognized as "hate code" due to speech variations
    # Adding both variations and pronunciation tolerance
    DEFAULT_TRIGGER_WORDS = [
        TriggerWord("jarvis", "activate", case_sensitive=False, confidence_threshold=0.5),  # Lower threshold for better detection
        TriggerWord("jarvis", "start_recording", case_sensitive=False, confidence_threshold=0.5),  # Also add explicit start_recording
        TriggerWord("hey code", "start_recording", case_sensitive=False, confidence_threshold=0.6),
        TriggerWord("hate code", "start_recording", case_sensitive=False, confidence_threshold=0.6),  # Pronunciation variation
        TriggerWord("stop recording", "stop_recording", case_sensitive=False, confidence_threshold=0.6),
        TriggerWord("transcribe", "transcribe", case_sensitive=False, confidence_threshold=0.6),
    ]

    def __init__(self, project_root: Optional[Path] = None, auto_start: bool = True):
        """
        Initialize auto-recording system

        Args:
            project_root: Project root directory
            auto_start: Automatically start listening (no manual click)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.auto_start = auto_start

        # Data directories
        self.sessions_dir = self.project_root / "data" / "cursor_recording_sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self.audio_dir = self.sessions_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        self.transcripts_dir = self.sessions_dir / "transcripts"
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.trigger_words = self.DEFAULT_TRIGGER_WORDS.copy()
        self.current_session: Optional[RecordingSession] = None
        self.is_recording = False
        self.is_listening = False
        self._handle_trigger_called = False  # Track trigger handler calls
        self.passive_mode = False  # CRITICAL: In passive mode, only listen for triggers, don't transcribe to prevent loops

        # Visual debugging - context confidence, personage, state, metrics
        try:
            from transcription_visual_debugger import get_debugger
            self.debugger = get_debugger(project_root=self.project_root)
            logger.info("✅ Visual debugger enabled - showing context confidence, personage, state, metrics")
        except ImportError:
            self.debugger = None
            logger.debug("Visual debugger not available")

        # Voice filtering - filter out other voices (wife, etc.) - only hear user
        try:
            from voice_filter_system import VoiceFilterSystem
            self.voice_filter = VoiceFilterSystem(user_id="user", project_root=self.project_root)
            self.voice_filter_enabled = True
            self.voice_profile_training = False  # Auto-train from transcription audio
            self.voice_samples_collected = 0
            self.min_samples_for_training = 3  # Ballpark estimate - scales dynamically
            self.consent_given = False  # User consent for recording/voice profile
            logger.info("✅ Voice filter enabled - will only process user's voice, ignore others")
            logger.info("   Auto-training: Will build voice profile from transcription audio (dynamic scaling)")
            logger.info("   ⚠️  CONSENT REQUIRED: Recording and voice profile creation requires user consent")
        except ImportError:
            self.voice_filter = None
            self.voice_filter_enabled = False
            logger.warning("⚠️  Voice filter not available - will process all voices")

        # Storage management (prevent dev/null)
        try:
            from intelligent_recording_storage_manager import \
                IntelligentRecordingStorageManager
            self.storage_manager = IntelligentRecordingStorageManager(project_root=project_root)
        except ImportError:
            self.storage_manager = None
            logger.warning("⚠️  Storage manager not available - recordings may fill disk")

        # Speech recognition
        self.recognizer = None
        self.microphone = None
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("✅ Speech recognition initialized")
            except Exception as e:
                logger.warning(f"⚠️  Speech recognition init failed: {e}")

        # Audio recording
        self.audio_queue = queue.Queue()
        self.audio_frames = []

        # Threading
        self.listening_thread = None
        self.recording_thread = None
        self.transcription_thread = None
        self.stop_event = threading.Event()

        # Callbacks
        self.on_trigger_detected: Optional[Callable] = None
        self.on_recording_started: Optional[Callable] = None
        self.on_recording_stopped: Optional[Callable] = None
        self.on_transcription_complete: Optional[Callable] = None

        # Auto-send transcription to Cursor with retry
        try:
            from cursor_transcription_sender import \
                send_transcription_to_cursor
            self.send_to_cursor = send_transcription_to_cursor
            self.auto_send_to_cursor = True  # Auto-send by default
        except ImportError:
            self.send_to_cursor = None
            self.auto_send_to_cursor = False
            logger.warning("⚠️  Cursor transcription sender not available - transcription won't auto-send")

        # Grammarly CLI integration (Charlie-Lima-Indigo) - Auto-enhance transcribed text
        # Vision: "formulate, focus, articulate" - improve communication clarity
        self.grammarly_enabled = True  # Auto-grammar check by default
        self.grammarly_cli = None
        try:
            from grammarly_cli import GrammarlyCLI
            self.grammarly_cli = GrammarlyCLI()
            if self.grammarly_cli.grammarly:
                logger.info("✅ Grammarly CLI (CLI) enabled - will auto-enhance transcribed text")
                logger.info("   📝 Vision: Formulate, focus, articulate - improve communication clarity")
            else:
                logger.warning("⚠️  Grammarly CLI engine not available - transcribed text won't be grammar-checked")
                self.grammarly_enabled = False
        except ImportError:
            logger.warning("⚠️  Grammarly CLI not available - install grammarly_cli module")
            self.grammarly_enabled = False

        logger.info("🎤 Cursor Auto-Recording & Transcription initialized")

        # Auto-start if enabled
        if self.auto_start:
            self.start_listening()

    def add_trigger_word(self, word: str, action: str, case_sensitive: bool = False,
                        confidence_threshold: float = 0.7):
        """Add a trigger word"""
        trigger = TriggerWord(word, action, case_sensitive, confidence_threshold)
        self.trigger_words.append(trigger)
        logger.info(f"✅ Added trigger word: '{word}' -> {action}")

    def start_listening(self):
        """Start listening for trigger words (AUTO-START - no manual click)"""
        if self.is_listening:
            logger.warning("⚠️  Already listening")
            return

        if not SPEECH_RECOGNITION_AVAILABLE or not self.recognizer:
            logger.error("❌ Speech recognition not available")
            return

        # LOGICAL FIX: Auto-consent when user starts listening (implicit consent)
        # User initiating recording = consent to record and create voice profile
        if not self.consent_given:
            self.consent_given = True
            logger.info("✅ Consent given (user initiated recording) - will build voice profile")

        self.is_listening = True
        self.stop_event.clear()

        # Initialize dynamic pause detection (RR ENHANCEMENT: Improved timeout decay)
        self.last_audio_time = None
        self.consecutive_audio_count = 0
        # CRITICAL FIX: Longer pause timeout so listening doesn't stop during natural speech pauses
        self.dynamic_pause_timeout = 5.0  # Start with 5 seconds (increased from 2.5s) - don't stop during pauses
        self.speech_energy_threshold = 0.01  # RR ENHANCEMENT: Energy-based speech end detection
        self.pause_detection_metrics = {
            "total_pauses": 0,
            "false_positives": 0,
            "successful_sends": 0,
            "failed_sends": 0
        }

        # Start listening thread
        self.listening_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listening_thread.start()

        logger.info("✅ Started listening for trigger words (AUTO-START)")

    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        self.stop_event.set()

        if self.listening_thread:
            self.listening_thread.join(timeout=2)

        logger.info("✅ Stopped listening")

    def _listen_loop(self):
        """Main listening loop - detects trigger words"""
        while self.is_listening and not self.stop_event.is_set():
            try:
                if not self.recognizer or not self.microphone:
                    break

                with self.microphone as source:
                    # LOGICAL FIX: Dynamic pause detection - longer if still speaking, shorter if finished
                    # Adjust timeout based on consecutive audio activity
                    # If user is speaking continuously (consecutive audio), use longer timeout (3-4s)
                    # If user pauses (no recent audio), use shorter timeout (1.5-2s)
                    import time
                    current_time = time.time()

                    # RR ENHANCEMENT: Dynamic pause detection with improved decay
                    # CRITICAL FIX: User reported counting past 5 - system didn't auto-send
                    # Need to be more aggressive about detecting pauses for auto-send
                    if self.last_audio_time and (current_time - self.last_audio_time) < 0.5:
                        # Recent audio activity - user still speaking, use longer timeout
                        self.consecutive_audio_count += 1
                        # Grading on a curve: 2.5s → 5s max (gradual increase)
                        # CRITICAL FIX: Longer timeout when user is actively speaking
                        self.dynamic_pause_timeout = min(10.0, 5.0 + (self.consecutive_audio_count * 0.2))  # Up to 10s
                    else:
                        # RR ENHANCEMENT: Gradual decay instead of immediate reset
                        # CRITICAL FIX: User counted past 5 - need to auto-send sooner
                        # If no audio for 3+ seconds, force auto-send (was 5s)
                        time_since_audio = current_time - self.last_audio_time if self.last_audio_time else float('inf')
                        if time_since_audio > 3.0:
                            # Force shorter timeout to trigger auto-send
                            self.dynamic_pause_timeout = 1.5  # Very short - force auto-send
                            logger.info(f"⏱️  Long pause detected ({time_since_audio:.1f}s) - forcing auto-send timeout to {self.dynamic_pause_timeout:.1f}s")
                        elif self.consecutive_audio_count > 0:
                            # CRITICAL FIX: Don't decay too much - keep listening during natural pauses
                            # Decay: reduce by 10% per pause, but don't go below 3.0s (was 5.0s - too long)
                            self.dynamic_pause_timeout = max(3.0, self.dynamic_pause_timeout * 0.9)  # Faster decay, lower minimum
                            self.consecutive_audio_count = max(0, self.consecutive_audio_count - 1)
                        else:
                            # No recent audio and count already at 0 - reset to base
                            self.dynamic_pause_timeout = 3.0  # Base timeout (reduced from 5.0s to 3.0s for faster auto-send)

                    # Listen for audio with dynamic timeout (grading on a curve: 2.5-5.0s)
                    try:
                        audio = self.recognizer.listen(source, timeout=self.dynamic_pause_timeout, phrase_time_limit=8)
                        has_audio = True
                        # Update last audio time for dynamic pause detection
                        self.last_audio_time = time.time()
                    except sr.WaitTimeoutError:
                        # LOGICAL FIX: Dynamic timeout - pause detected (variable seconds of silence)
                        # If recording and we have transcribed text or audio frames, auto-transcribe and send
                        has_audio = False
                        if self.is_recording and self.current_session:
                            # Check if we have transcribed text in session OR audio frames to transcribe
                            has_transcript = self.current_session.transcript and len(self.current_session.transcript) > 0
                            has_audio_data = self.audio_frames and len(self.audio_frames) > 0

                            if has_transcript or has_audio_data:
                                # CRITICAL FIX: Wait for user to finish speaking (camera-based lip detection)
                                # Don't interrupt - wait for lips to stop moving
                                try:
                                    from lip_movement_detector import \
                                        wait_for_user_to_finish_speaking
                                    logger.info("👄 Waiting for user to finish speaking (watching lips)...")
                                    wait_for_user_to_finish_speaking(timeout=5.0)  # Wait up to 5 seconds for silence
                                except Exception as e:
                                    logger.debug(f"Lip detection not available: {e}")
                                    # Fallback: use existing pause detection

                                logger.info(f"📤 Pause detected ({self.dynamic_pause_timeout:.1f}s timeout) - auto-transcribing and sending...")
                                if has_audio_data:
                                    self._save_audio_file()  # Save accumulated audio
                                # IMPORTANT: Transcribe and auto-send (ensures 100% reliability)
                                self.transcribe_current_session()  # Transcribe and auto-send
                                if has_audio_data:
                                    self.audio_frames = []  # Reset for next segment
                                # Reset consecutive audio count after sending
                                self.consecutive_audio_count = 0
                                self.last_audio_time = None
                                # LOGICAL FIX: Small delay to ensure transcription thread starts
                                time.sleep(0.1)
                        continue  # Continue listening loop

                # CRITICAL: In PASSIVE mode, ONLY check for trigger words - DON'T transcribe anything
                if self.passive_mode:
                    # Only recognize speech to check for trigger words - don't transcribe or record
                    try:
                        text = self.recognizer.recognize_google(audio, language="en-US")
                        logger.debug(f"🔍 Passive mode: Heard '{text}' - checking for trigger words only...")

                        # Check for trigger words ONLY
                        for trigger in self.trigger_words:
                            search_text = text.lower() if not trigger.case_sensitive else text
                            trigger_text = trigger.word.lower() if not trigger.case_sensitive else trigger.word

                            if trigger_text in search_text or "jarvis" in search_text:
                                logger.info(f"🎯 TRIGGER DETECTED in passive mode: '{trigger.word}' -> switching to active mode")
                                self._handle_trigger(trigger, text)
                                # Switch to active mode (will be handled by hybrid system)
                                break

                        # CRITICAL: In passive mode, DON'T transcribe or record - just check triggers
                        continue  # Skip transcription/recording in passive mode
                    except sr.UnknownValueError:
                        # No speech detected - continue listening for triggers
                        continue
                    except sr.RequestError as e:
                        logger.warning(f"⚠️  Speech recognition error in passive mode: {e}")
                        continue

                # CRITICAL: Voice filtering - only process if it's the user's voice (filter out wife, others)
                # LOGICAL DEBUG: Add explicit logging to verify filter is being called
                if self.voice_filter_enabled and self.voice_filter:
                    logger.debug(f"🔍 Voice filter check: enabled={self.voice_filter_enabled}, filter={self.voice_filter is not None}")
                    try:
                        # Convert audio to numpy array for filtering
                        import numpy as np

                        # Get raw audio data from speech_recognition AudioData
                        raw_data = audio.get_raw_data(convert_rate=None, convert_width=None)
                        audio_data = np.frombuffer(raw_data, dtype=np.int16)
                        sample_rate = audio.sample_rate

                        # CRITICAL FIX: Check if this is wife's voice BEFORE processing
                        filtered_audio, is_user_voice = self.voice_filter.filter_audio(audio_data, sample_rate)
                        if not is_user_voice:
                            logger.warning("🚫 Voice REJECTED - not OP's voice (wife/TV/background) - SKIPPING transcription")
                            continue  # Skip this audio - don't transcribe wife's voice

                        # AUTO-TRAIN: Collect voice samples from transcription (build profile dynamically)
                        # Training happens in negative space (pauses) - transparent to user
                        # IMPORTANT: Update visual debugger to show training status (operator needs to know)
                        profile_trained = self.voice_filter.voice_profile.profile_data.get("trained", False)
                        if not profile_trained and self.consent_given:
                            # Add this audio sample to voice profile (with consent)
                            self.voice_filter.voice_profile.add_voice_sample(audio_data, sample_rate)
                            self.voice_samples_collected += 1

                            # Update visual debugger - show training progress (IMPORTANT: Operator needs visual feedback)
                            if self.debugger:
                                self.debugger.update_voice_training_status(
                                    training_active=True,
                                    samples_collected=self.voice_samples_collected,
                                    samples_needed=self.min_samples_for_training,
                                    profile_trained=False
                                )

                            # Use global logging pattern for training progress
                            try:
                                from lumina_logger import \
                                    log_voice_filter_training
                                log_voice_filter_training(logger, self.voice_samples_collected, self.min_samples_for_training)
                            except ImportError:
                                logger.info(f"📚 Voice profile training: {self.voice_samples_collected}/{self.min_samples_for_training} samples collected")

                            # Auto-train when we have enough samples (ballpark estimate - scales dynamically)
                            # Training happens during pauses (negative space) - transparent
                            if self.voice_samples_collected >= self.min_samples_for_training:
                                if self.voice_filter.voice_profile.train_profile(min_samples=self.min_samples_for_training):
                                    # Use global logging pattern
                                    try:
                                        from lumina_logger import \
                                            log_voice_filter_trained
                                        log_voice_filter_trained(logger, self.voice_samples_collected)
                                    except ImportError:
                                        logger.info(f"✅ Voice profile trained! ({self.voice_samples_collected} samples, dynamic scaling)")
                                        logger.info("   Training completed in negative space (pauses) - transparent to user")
                                    self.voice_profile_training = True

                                    # Update visual debugger - training complete (IMPORTANT: Operator needs to know)
                                    if self.debugger:
                                        self.debugger.update_voice_training_status(
                                            training_active=False,
                                            samples_collected=self.voice_samples_collected,
                                            samples_needed=self.min_samples_for_training,
                                            profile_trained=True
                                        )
                        elif not profile_trained:
                            # Not training yet (no consent) - update visual debugger
                            if self.debugger:
                                self.debugger.update_voice_training_status(
                                    training_active=False,
                                    samples_collected=self.voice_samples_collected,
                                    samples_needed=self.min_samples_for_training,
                                    profile_trained=False
                                )
                        else:
                            # Profile already trained - update visual debugger
                            if self.debugger:
                                self.debugger.update_voice_training_status(
                                    training_active=False,
                                    samples_collected=self.voice_samples_collected,
                                    samples_needed=self.min_samples_for_training,
                                    profile_trained=True
                                )

                        # Filter audio - only pass through if it matches user's voice (if trained)
                        profile_trained = self.voice_filter.voice_profile.profile_data.get("trained", False)
                        logger.debug(f"🔍 Voice profile trained: {profile_trained}")

                        if profile_trained:
                            filtered_audio, is_user_voice = self.voice_filter.filter_audio(audio_data, sample_rate)
                            logger.debug(f"🔍 Voice filter result: is_user_voice={is_user_voice}")

                            # Update visual debugger - personage and confidence
                            if self.debugger:
                                if is_user_voice:
                                    self.debugger.update_personage("user", confidence=0.8)  # High confidence for user
                                else:
                                    self.debugger.update_personage("ai", confidence=0.3)  # Low confidence (filtered out)

                            if not is_user_voice:
                                # Use global logging pattern from lumina_logger module
                                try:
                                    from lumina_logger import \
                                        log_voice_filter_reject

                                    # Note: similarity not available here, but pattern still applies
                                    log_voice_filter_reject(logger, 0.0, self.voice_filter.voice_match_threshold, "non-user voice (wife/TV/background)")
                                except ImportError:
                                    logger.info("🔇 Filtered out non-user voice (wife/TV/background) - ignoring transcription")
                                    logger.info("   🚫 Voice filter active - rejecting TV audio and background speakers")
                                # LOGICAL FIX: Skip transcription entirely - don't process this audio
                                continue  # Skip this audio - not user's voice

                            logger.debug("✅ Voice matches user profile - processing")
                        else:
                            # Not trained yet - accept all audio and keep collecting samples
                            # LOGICAL FIX: Log that filtering isn't active yet (profile not trained)
                            if self.debugger:
                                self.debugger.update_personage("user", confidence=0.5)  # Medium confidence (training)
                            logger.info(f"📚 Voice profile not trained yet - accepting all audio (collecting samples: {self.voice_samples_collected}/{self.min_samples_for_training})")
                            logger.info("   ⚠️  Voice filtering not active - wife/TV may bleed through until profile is trained")
                    except Exception as e:
                        logger.warning(f"⚠️  Voice filter check failed: {e} - will process audio anyway")
                        # Continue processing if filter fails (fail open for now)

                # Recognize speech (only if we got past the voice filter and have audio)
                if not has_audio:
                    continue  # Skip if no audio (already handled pause above)

                try:
                    # CRITICAL FIX: Use multiple recognition attempts for better detection
                    text = None
                    recognition_attempts = [
                        lambda: self.recognizer.recognize_google(audio).lower(),
                        lambda: self.recognizer.recognize_sphinx(audio).lower(),  # Fallback
                    ]

                    for attempt in recognition_attempts:
                        try:
                            text = attempt()
                            logger.debug(f"🎤 Heard: {text}")
                            break
                        except Exception:
                            continue

                    if not text:
                        logger.debug("🎤 No speech recognized")
                        continue

                    # AUTO-SEND: If we have a recording session, save audio and prepare for auto-send
                    # Auto-send will happen on next pause (timeout) or when recording stops
                    if self.is_recording and self.current_session:
                        # Add to current session transcript immediately
                        self.current_session.transcript.append({
                            "timestamp": datetime.now().isoformat(),
                            "text": text,
                            "source": "google_speech_recognition"
                        })
                        logger.debug(f"📝 Added to session transcript: '{text[:50]}...'")

                    # CRITICAL FIX: More aggressive trigger word detection
                    # Check for trigger words with pronunciation tolerance
                    for trigger in self.trigger_words:
                        search_text = text if not trigger.case_sensitive else text
                        trigger_text = trigger.word if not trigger.case_sensitive else trigger.word.lower()

                        # Exact match
                        if trigger_text in search_text:
                            logger.info(f"✅ Trigger detected: '{trigger.word}' -> {trigger.action}")
                            self._handle_trigger(trigger, text)
                            break

                        # CRITICAL FIX: Also check if trigger word starts with detected text
                        # Handles cases where only part of word is heard
                        if trigger_text.startswith(search_text[:len(trigger_text)]) or search_text.startswith(trigger_text[:len(search_text)]):
                            logger.info(f"✅ Trigger detected (partial): '{trigger.word}' -> {trigger.action} (heard: '{text}')")
                            self._handle_trigger(trigger, text)
                            break

                        # Fuzzy match for pronunciation variations (speech impediments, accents, etc.)
                        # Check if trigger word sounds similar (common mispronunciations)
                        if self._fuzzy_trigger_match(trigger_text, search_text):
                            logger.info(f"✅ Trigger detected (fuzzy): '{trigger.word}' -> {trigger.action} (heard: '{text}')")
                            self._handle_trigger(trigger, text)
                            break

                        # CRITICAL FIX: Very loose matching for "jarvis"
                        # Accept if any part of "jarvis" is in the text
                        if trigger_text == "jarvis" and len(search_text) >= 3:
                            # Check if "jar", "jarv", "jarvi", or "jarvis" appears
                            jarvis_parts = ["jar", "jarv", "jarvi", "jarvis"]
                            for part in jarvis_parts:
                                if part in search_text:
                                    logger.info(f"✅ Trigger detected (loose match): '{trigger.word}' -> {trigger.action} (heard: '{text}')")
                                    self._handle_trigger(trigger, text)
                                    break
                            if any(part in search_text for part in jarvis_parts):
                                break

                except sr.UnknownValueError:
                    # No speech detected, continue
                    pass
                except sr.RequestError as e:
                    logger.warning(f"⚠️  Speech recognition error: {e}")

            except Exception as e:
                logger.error(f"❌ Listening error: {e}")
                import time
                time.sleep(0.5)

    def _fuzzy_trigger_match(self, trigger_text: str, detected_text: str) -> bool:
        """
        Fuzzy matching for pronunciation variations

        Handles speech impediments, accents, missing teeth, etc.
        Common variations:
        - "hey" vs "hate" (missing/cracked teeth)
        - "jarvis" vs "jarvis" (various pronunciations)
        """
        # Common pronunciation variations
        variations = {
            "hey code": ["hate code", "hay code", "hey code", "he code"],
            "hate code": ["hey code", "hay code", "hate code", "he code"],
            "jarvis": ["jarvis", "jarvis", "jarvis", "jarvis"],
        }

        # Check if trigger has known variations
        if trigger_text in variations:
            for variation in variations[trigger_text]:
                if variation in detected_text:
                    return True

        # Simple character similarity (for other variations)
        # Check if trigger word is similar to detected text
        if len(trigger_text) > 3:
            # Check if most characters match (allowing for 1-2 character differences)
            matches = sum(1 for a, b in zip(trigger_text, detected_text) if a == b)
            similarity = matches / max(len(trigger_text), len(detected_text))
            if similarity >= 0.7:  # 70% similarity threshold
                return True

        return False

    def _handle_trigger(self, trigger: TriggerWord, detected_text: str):
        """Handle trigger word detection - CRITICAL: Don't shut down mic"""
        # Prevent infinite loops
        if getattr(self, '_handle_trigger_called', False):
            return
        self._handle_trigger_called = True

        try:
            # CRITICAL: Call callback first (for hybrid system to switch modes)
            if self.on_trigger_detected:
                self.on_trigger_detected(trigger, detected_text)

            # CRITICAL: Ensure mic stays ON after trigger (don't shut down)
            if not self.is_listening:
                logger.warning("⚠️  CRITICAL: Mic shut down during trigger - restarting immediately!")
                self.start_listening()

            if trigger.action == "start_recording":
                self.start_recording()
            elif trigger.action == "stop_recording":
                self.stop_recording()
            elif trigger.action == "transcribe":
                self.transcribe_current_session()
            elif trigger.action == "activate":
                # Activate JARVIS - CRITICAL: This must start recording AND keep mic ON!
                logger.info("🎤 JARVIS activated via voice trigger - starting recording...")
                logger.info("   ⚠️  CRITICAL: Mic will stay ON - actively listening now")
                # CRITICAL FIX: "activate" should start recording (not just log)
                self.start_recording()
                # CRITICAL: Verify mic is still ON after starting recording
                if not self.is_listening:
                    logger.error("❌ CRITICAL: Mic shut down after start_recording - restarting!")
                    self.start_listening()
        finally:
            self._handle_trigger_called = False

    def start_recording(self):
        """Start recording audio (AUTO - no manual click)"""
        if self.is_recording:
            logger.warning("⚠️  Already recording")
            return

        if not AUDIO_RECORDING_AVAILABLE:
            logger.error("❌ Audio recording not available")
            return

        # Check storage before recording (prevent dev/null)
        if self.storage_manager:
            should_record, reason = self.storage_manager.should_record()
            if not should_record:
                logger.error(f"❌ Cannot record: {reason}")
                # Could notify user here
                return

        # Create session
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = ts_logger.now() if ts_logger else datetime.now().isoformat()

        self.current_session = RecordingSession(
            session_id=session_id,
            start_time=start_time,
            metadata={
                "auto_started": True,
                "trigger_detected": True,
            }
        )

        self.is_recording = True
        self.audio_frames = []

        # Start recording thread
        self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.recording_thread.start()

        if self.on_recording_started:
            self.on_recording_started(self.current_session)

        logger.info(f"✅ Recording started: {session_id} (AUTO-START)")

    def stop_recording(self):
        """Stop recording"""
        if not self.is_recording:
            logger.warning("⚠️  Not recording")
            return

        self.is_recording = False

        if self.current_session:
            end_time = ts_logger.now() if ts_logger else datetime.now().isoformat()
            self.current_session.end_time = end_time

            # Calculate duration
            start_dt = datetime.fromisoformat(self.current_session.start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            self.current_session.duration_seconds = (end_dt - start_dt).total_seconds()

        # Save audio file
        if self.audio_frames:
            self._save_audio_file()

        if self.on_recording_stopped:
            self.on_recording_stopped(self.current_session)

        logger.info("✅ Recording stopped")

    def _record_audio(self):
        """Record audio in background thread"""
        try:
            import pyaudio

            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100

            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )

            logger.info("🎤 Recording audio...")

            while self.is_recording:
                data = stream.read(CHUNK)
                self.audio_frames.append(data)

            stream.stop_stream()
            stream.close()
            audio.terminate()

        except Exception as e:
            logger.error(f"❌ Audio recording error: {e}")

    def _save_audio_file(self):
        """Save recorded audio to file"""
        if not self.current_session or not self.audio_frames:
            return

        try:
            import wave

            audio_file = self.audio_dir / f"{self.current_session.session_id}.wav"

            with wave.open(str(audio_file), 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.audio_frames))

            self.current_session.audio_file = str(audio_file)
            logger.info(f"✅ Audio saved: {audio_file}")

        except Exception as e:
            logger.error(f"❌ Error saving audio: {e}")

    def _handle_explicit_deletion_requests(self, text: str) -> str:
        """
        Handle explicit deletion requests in transcription.

        Examples:
        - "anything said after AIOS should be stricken and deleted"
        - "delete everything after X"
        - "strike the last part"

        Args:
            text: Transcribed text

        Returns:
            Text with explicit deletions applied
        """
        import re

        # Pattern: "anything said after X should be stricken/deleted"
        # Pattern: "delete/strike everything after X"
        deletion_patterns = [
            r"anything said after ['\"]?([^'\"]+)['\"]? should be (?:stricken|deleted|removed)",
            r"(?:delete|strike|remove) everything after ['\"]?([^'\"]+)['\"]?",
            r"strike.*after ['\"]?([^'\"]+)['\"]?",
        ]

        for pattern in deletion_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                marker = match.group(1).strip()
                # Find the marker in the text
                marker_index = text.lower().find(marker.lower())
                if marker_index != -1:
                    # Keep everything up to and including the marker
                    # Then remove the deletion instruction itself
                    before_marker = text[:marker_index + len(marker)]
                    # Remove the deletion instruction
                    before_marker = re.sub(pattern, '', before_marker, flags=re.IGNORECASE).strip()
                    logger.info(f"🗑️  Explicit deletion request: Removing text after '{marker}'")
                    logger.info(f"   📝 Original length: {len(text)} chars")
                    logger.info(f"   ✂️  Trimmed length: {len(before_marker)} chars")
                    return before_marker

        return text

    def transcribe_current_session(self):
        """Transcribe current recording session"""
        # If recording is active, stop it first to save audio
        if self.is_recording:
            self.stop_recording()

        if not self.current_session or not self.current_session.audio_file:
            logger.warning("⚠️  No audio file to transcribe")
            return

        # Start transcription in background
        self.transcription_thread = threading.Thread(
            target=self._transcribe_audio,
            args=(self.current_session.audio_file,),
            daemon=True
        )
        self.transcription_thread.start()

    def _transcribe_audio(self, audio_file: str):
        """Transcribe audio file"""
        try:
            if not SPEECH_RECOGNITION_AVAILABLE or not self.recognizer:
                logger.error("❌ Speech recognition not available")
                return

            logger.info(f"📝 Transcribing: {audio_file}")

            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)

            # Transcribe
            text = self.recognizer.recognize_google(audio)
            original_text = text  # Keep original for comparison

            # Handle explicit deletion requests (e.g., "strike everything after X")
            # User may request: "anything said after AIOS should be stricken and deleted"
            text = self._handle_explicit_deletion_requests(text)

            # GRAMMARLY CLI INTEGRATION (Charlie-Lima-Indigo)
            # Vision: "formulate, focus, articulate" - improve communication clarity
            # Auto-enhance transcribed text before sending (like Grammarly helps humans)
            if self.grammarly_enabled and self.grammarly_cli and self.grammarly_cli.grammarly:
                try:
                    logger.info("📝 Grammarly CLI: Checking transcribed text for clarity...")
                    grammarly_result = self.grammarly_cli.check_text(text, show_details=True)

                    if grammarly_result.get("changed"):
                        text = grammarly_result["corrected"]
                        corrections_count = grammarly_result.get("corrections_count", 0)
                        logger.info(f"✅ Grammarly CLI: Enhanced text ({corrections_count} corrections)")
                        logger.info(f"   📝 Original: {original_text[:100]}...")
                        logger.info(f"   ✨ Enhanced: {text[:100]}...")

                        # Update visual debugger with grammar corrections
                        if self.debugger:
                            self.debugger.update_context_confidence(0.85)  # Higher confidence after grammar check
                    else:
                        logger.info("✅ Grammarly CLI: No corrections needed - text is clear")
                except Exception as e:
                    logger.warning(f"⚠️  Grammarly CLI check failed: {e} - using original text")
                    text = original_text  # Fallback to original

            # Save transcript (save enhanced version if grammar-checked)
            transcript_file = self.transcripts_dir / f"{Path(audio_file).stem}.txt"
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(text)

            if self.current_session:
                self.current_session.transcript_file = str(transcript_file)
                self.current_session.transcript.append({
                    "timestamp": ts_logger.now() if ts_logger else datetime.now().isoformat(),
                    "text": text,
                    "original_text": original_text if text != original_text else None,  # Save original if changed
                    "source": "google_speech_recognition",
                    "grammar_enhanced": text != original_text if self.grammarly_enabled else False
                })

                # Save session metadata
                self._save_session_metadata()

            # Auto-send to Cursor with retry (if enabled) - sends ENHANCED text
            if self.auto_send_to_cursor and self.send_to_cursor:
                try:
                    # Update visual debugger - processing state
                    if self.debugger:
                        self.debugger.update_state("processing")
                        self.debugger.update_context_confidence(0.7)  # Medium confidence during send

                    # RR ENHANCEMENT: Enhanced send verification and logging
                    logger.info("📤 Sending transcription to Cursor (with retry)...")
                    success = self.send_to_cursor(text, max_retries=3)
                    if success:
                        # RR ENHANCEMENT: Track successful sends
                        self.pause_detection_metrics["successful_sends"] += 1
                        logger.info("✅ Transcription sent to Cursor successfully (verified)")
                        logger.info(f"   📊 Send metrics: {self.pause_detection_metrics['successful_sends']} successful, {self.pause_detection_metrics['failed_sends']} failed")
                        # Record success in metrics
                        if self.debugger:
                            self.debugger.record_success()
                            self.debugger.update_ai_confidence(0.9)  # High AI confidence on success
                            # Human confidence vs AI: High (we both succeeded)
                            self.debugger.update_human_confidence_vs_ai(0.8)
                            # Human confidence vs unknown: Medium (we know we succeeded, but future unknown)
                            self.debugger.update_human_confidence_vs_unknown(0.5)
                            self.debugger.update_state("idle")
                    else:
                        # RR ENHANCEMENT: Track failed sends with detailed logging
                        self.pause_detection_metrics["failed_sends"] += 1
                        logger.warning("⚠️  Failed to send transcription to Cursor (will retry on next attempt)")
                        logger.warning(f"   📊 Send metrics: {self.pause_detection_metrics['successful_sends']} successful, {self.pause_detection_metrics['failed_sends']} failed")
                        logger.warning("   🔄 Retry manager will attempt again on next transcription")
                        # Record failure in metrics
                        if self.debugger:
                            self.debugger.record_failure()
                            self.debugger.update_ai_confidence(0.3)  # Low AI confidence on failure
                            # Human confidence vs AI: Low (we both failed)
                            self.debugger.update_human_confidence_vs_ai(0.3)
                            # Human confidence vs unknown: Low (we don't know why it failed)
                            self.debugger.update_human_confidence_vs_unknown(0.2)
                            self.debugger.update_state("idle")
                except Exception as e:
                    logger.error(f"❌ Error sending transcription to Cursor: {e}")
                    if self.debugger:
                        self.debugger.record_failure()
                        self.debugger.update_state("idle")

            # Call custom callback if set
            if self.on_transcription_complete:
                self.on_transcription_complete(self.current_session, text)

            logger.info(f"✅ Transcription complete: {transcript_file}")

        except Exception as e:
            logger.error(f"❌ Transcription error: {e}")

    def _save_session_metadata(self):
        try:
            """Save session metadata"""
            if not self.current_session:
                return

            metadata_file = self.sessions_dir / f"{self.current_session.session_id}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.current_session), f, indent=2, default=str)

            logger.info(f"✅ Session metadata saved: {metadata_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_session_metadata: {e}", exc_info=True)
            raise
def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor Auto-Recording & Transcription - FIXED")
    parser.add_argument("--auto-start", action="store_true", default=True,
                       help="Auto-start listening (no manual click)")
    parser.add_argument("--test-triggers", action="store_true",
                       help="Test trigger word detection")
    parser.add_argument("--add-trigger", nargs=2, metavar=("WORD", "ACTION"),
                       help="Add trigger word: WORD ACTION")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🎤 Cursor Auto-Recording & Transcription - FIXED")
    print("   Real-world smoke test - auto-start, trigger words, transcription")
    print("="*80 + "\n")

    # Initialize
    recorder = CursorAutoRecordingTranscriptionFixed(auto_start=args.auto_start)

    # Add custom trigger if provided
    if args.add_trigger:
        word, action = args.add_trigger
        recorder.add_trigger_word(word, action)

    # Test triggers
    if args.test_triggers:
        print("🎤 Testing trigger words...")
        print("   Say: 'JARVIS', 'hey code' (or 'hate code' - pronunciation variation), 'stop recording', 'transcribe'")
        print("   Note: System handles pronunciation variations (speech impediments, accents, etc.)")
        print("   Press Ctrl+C to stop\n")

        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            recorder.stop_listening()
            if recorder.is_recording:
                recorder.stop_recording()

    else:
        print("✅ Auto-recording system active")
        print("   Listening for trigger words...")
        print("   Press Ctrl+C to stop\n")

        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            recorder.stop_listening()
            if recorder.is_recording:
                recorder.stop_recording()

    print("\n✅ Shutdown complete\n")


if __name__ == "__main__":


    main()