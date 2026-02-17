#!/usr/bin/env python3
"""
Unified Visual-Audio Listening Control - REQUIRED

Uses BOTH visual (lips, hand gestures) AND audio cues simultaneously,
like real humans do when conversing. Speech pathologist approach.

Tags: #UNIFIED #VISUAL_AUDIO #SPEECH_PATHOLOGY #NATURAL_CONVERSATION #REQUIRED @JARVIS @LUMINA
"""

import sys
import os
import warnings
import time
import threading
from pathlib import Path
from collections import deque
from enum import Enum

# Suppress OpenCV MSMF warnings
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
warnings.filterwarnings('ignore', message='.*MSMF.*')
warnings.filterwarnings('ignore', message='.*grabFrame.*')
warnings.filterwarnings('ignore', message='.*cap_msmf.*')

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("UnifiedVisualAudio")

try:
    import cv2
    import mediapipe as mp
    import numpy as np
    import speech_recognition as sr
    CV2_AVAILABLE = True
    MEDIAPIPE_AVAILABLE = True
    SPEECH_REC_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    MEDIAPIPE_AVAILABLE = False
    SPEECH_REC_AVAILABLE = False
    logger.error("❌ Required libraries not available")


class SpeakingState(Enum):
    """User speaking state based on combined visual + audio cues"""
    SPEAKING = "speaking"  # Visual OR audio indicates speaking
    PAUSING = "pausing"    # Brief pause but likely continuing
    FINISHED = "finished"  # BOTH visual AND audio indicate finished
    SILENT = "silent"      # No cues detected


class UnifiedVisualAudioListening:
    """
    Unified Visual-Audio Listening Control

    Like real humans: watches AND listens simultaneously.
    Uses speech pathologist principles for natural conversation flow.
    """

    def __init__(self):
        self.running = False

        # Visual detection (lips + hand)
        self.cap = None
        self.mp_face_mesh = None
        self.face_mesh = None
        self.mp_hands = None
        self.hands = None

        # Audio detection
        self.recognizer = None
        self.microphone = None

        # Combined state
        self.speaking_state = SpeakingState.SILENT
        self.visual_speaking = False  # Lips moving or hand waving
        self.audio_speaking = False   # Audio detected

        # History for smoothing
        self.visual_history = deque(maxlen=10)
        self.audio_history = deque(maxlen=10)

        # Timing
        self.last_visual_cue = 0
        self.last_audio_cue = 0
        self.finished_threshold = 2.0  # 2 seconds of BOTH visual+audio silence = finished

        # Listening control
        self.listening_active = False
        self.transcription_service = None

        if CV2_AVAILABLE and MEDIAPIPE_AVAILABLE and SPEECH_REC_AVAILABLE:
            self._initialize()

    def _initialize(self):
        """Initialize camera and audio"""
        try:
            # CRITICAL: Use IR camera ONLY - regular camera emits bright white light
            # IR camera preferred to avoid distracting the operator
            try:
                from ir_camera_helper import open_ir_camera
                # Use IR camera ONLY (no backup - regular camera emits bright light)
                self.cap = open_ir_camera(use_full_spectrum_backup=False)
                if self.cap:
                    logger.info("✅ IR camera opened for visual detection (no bright light)")
                else:
                    logger.error("❌ IR camera not available - NOT using regular camera to avoid bright light")
                    logger.warning("   💡 Please ensure IR camera is available")
                    self.cap = None
            except ImportError:
                logger.error("❌ IR camera helper not available")
                logger.warning("   💡 Regular camera emits bright white light - IR camera preferred")
                self.cap = None

            if not self.cap or not self.cap.isOpened():
                logger.error("❌ Could not open camera (IR or regular)")
                return False

            # Face mesh for lip detection
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

            # Hands for gesture detection
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

            # Audio
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.recognizer.adjust_for_ambient_noise(self.microphone, duration=0.5)

            logger.info("✅ Unified visual-audio listening initialized")
            logger.info("   👁️  Watching: Lips + Hand gestures")
            logger.info("   👂 Listening: Audio cues")
            logger.info("   🧠 Combining: Like real human conversation")
            return True
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False

    def detect_visual_cues(self):
        """Detect visual cues: lips moving OR hand waving"""
        if not self.cap or not self.face_mesh or not self.hands:
            return False

        if not self.cap.isOpened():
            return False

        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                return False
        except Exception as e:
            logger.debug(f"Camera read error: {e}")
            return False

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_height, frame_width = frame.shape[:2]

        visual_detected = False

        # Check 1: Lip movement
        face_results = self.face_mesh.process(frame_rgb)
        if face_results.multi_face_landmarks:
            landmarks = face_results.multi_face_landmarks[0]
            # Upper lip: 12-17, Lower lip: 0-5
            upper_lip_y = np.mean([landmarks.landmark[i].y for i in [12, 13, 14, 15, 16, 17]])
            lower_lip_y = np.mean([landmarks.landmark[i].y for i in [0, 1, 2, 3, 4, 5]])
            lip_distance = abs(upper_lip_y - lower_lip_y) * frame_height

            # If lips are open enough, user might be speaking
            if lip_distance > 5:  # Threshold for "lips open"
                visual_detected = True

        # Check 2: Hand waving
        hand_results = self.hands.process(frame_rgb)
        if hand_results.multi_hand_landmarks:
            # Hand detected - could be waving
            # For now, if hand is visible, consider it a visual cue
            visual_detected = True

        return visual_detected

    def detect_audio_cues(self):
        """Detect audio cues: voice/speech detected"""
        if not self.microphone or not self.recognizer:
            return False

        try:
            # Quick audio check (non-blocking)
            with self.microphone as source:
                # Listen with very short timeout (0.3s) - just checking if audio exists
                try:
                    audio = self.recognizer.listen(source, timeout=0.3, phrase_time_limit=0.3)
                    # If we got audio, user is speaking
                    return True
                except sr.WaitTimeoutError:
                    # No audio detected
                    return False
        except Exception as e:
            logger.debug(f"Audio detection error: {e}")
            return False

    def update_speaking_state(self):
        """Update speaking state based on BOTH visual AND audio cues"""
        current_time = time.time()

        # Detect cues
        visual = self.detect_visual_cues()
        audio = self.detect_audio_cues()

        # Update history
        self.visual_history.append(visual)
        self.audio_history.append(audio)

        # Smooth detection (majority vote over recent frames)
        visual_smoothed = sum(self.visual_history) > len(self.visual_history) * 0.5
        audio_smoothed = sum(self.audio_history) > len(self.audio_history) * 0.5

        # Update timestamps
        if visual_smoothed:
            self.last_visual_cue = current_time
            self.visual_speaking = True
        else:
            self.visual_speaking = False

        if audio_smoothed:
            self.last_audio_cue = current_time
            self.audio_speaking = True
        else:
            self.audio_speaking = False

        # SPEECH PATHOLOGIST PRINCIPLE: Use BOTH cues like humans do
        # If EITHER visual OR audio indicates speaking → user is speaking
        # Only stop when BOTH visual AND audio indicate finished

        if visual_smoothed or audio_smoothed:
            # EITHER cue indicates speaking → user is speaking
            self.speaking_state = SpeakingState.SPEAKING
        else:
            # Both cues silent - check how long
            time_since_visual = current_time - self.last_visual_cue
            time_since_audio = current_time - self.last_audio_cue

            if time_since_visual < 1.0 or time_since_audio < 1.0:
                # Recent cues - user might be pausing
                self.speaking_state = SpeakingState.PAUSING
            elif time_since_visual >= self.finished_threshold and time_since_audio >= self.finished_threshold:
                # BOTH visual AND audio silent for threshold → user finished
                self.speaking_state = SpeakingState.FINISHED
            else:
                self.speaking_state = SpeakingState.SILENT

    def control_listening(self):
        """Control listening based on unified visual+audio state"""
        self.update_speaking_state()

        if not self.transcription_service:
            try:
                from cursor_auto_recording_transcription_fixed import CursorAutoRecordingTranscriptionFixed
                self.transcription_service = CursorAutoRecordingTranscriptionFixed(
                    project_root=project_root,
                    auto_start=False
                )
                # CRITICAL: Enable voice filtering to exclude wife's voice
                try:
                    from voice_filter_system import VoiceFilterSystem, VoicePrintProfile
                    voice_filter = VoiceFilterSystem(project_root)
                    # Load or create OP voice profile
                    op_profile = VoicePrintProfile.load_or_create(project_root, "primary_operator")
                    voice_filter.add_voice_profile(op_profile)
                    # Load wife's voice profile and mark as excluded
                    try:
                        wife_profile = VoicePrintProfile.load_or_create(project_root, "wife")
                        voice_filter.add_voice_profile(wife_profile, excluded=True)
                        logger.debug("✅ Wife's voice profile loaded and marked as excluded")
                    except Exception as e:
                        logger.debug(f"⚠️  Could not load wife's voice profile: {e}")
                    self.transcription_service.voice_filter = voice_filter
                    self.transcription_service.voice_filter_enabled = True
                    logger.info("✅ Voice filtering enabled - will exclude wife's voice")
                except Exception as e:
                    logger.warning(f"⚠️  Voice filtering not available: {e}")
                logger.info("✅ Transcription service initialized")
            except Exception as e:
                logger.error(f"❌ Could not initialize transcription: {e}")
                return

        # SPEECH PATHOLOGIST PRINCIPLE: Natural conversation flow
        # Also analyze MM-HMM sounds to distinguish between user and wife
        if self.speaking_state == SpeakingState.SPEAKING:
            # User is speaking (visual OR audio) → KEEP listening
            # CRITICAL: Check for MM-HMM sounds (speech pathologist analysis)
            try:
                # Get recent audio for MM-HMM detection
                if hasattr(self.transcription_service, 'get_recent_audio'):
                    recent_audio = self.transcription_service.get_recent_audio()
                    if recent_audio:
                        from mmhmm_voice_detection import MMHMMVoiceDetector
                        mmhmm_detector = MMHMMVoiceDetector(project_root)
                        mmhmm_analysis = mmhmm_detector.analyze_mmhmm(recent_audio[0], recent_audio[1])

                        if mmhmm_analysis and mmhmm_analysis.get("speaker_id") == "wife":
                            logger.warning("🚫 Wife's 'mm-hmm' detected - NOT starting listening")
                            logger.warning(f"   Speech pathologist insights: {mmhmm_analysis.get('insights', [])}")
                            return  # Don't start listening for wife's sounds
            except Exception as e:
                logger.debug(f"MM-HMM detection in unified listener: {e}")

            if not self.listening_active:
                logger.info("🎤 User speaking detected (visual+audio) - STARTING listening")
                try:
                    self.transcription_service.start_listening()
                    self.listening_active = True
                    # CRITICAL: Don't let pause detection stop listening while user is speaking
                    if hasattr(self.transcription_service, 'dynamic_pause_timeout'):
                        self.transcription_service.dynamic_pause_timeout = 15.0  # Very long timeout
                except Exception as e:
                    logger.error(f"❌ Failed to start listening: {e}")
            else:
                # Already listening - ensure it stays active
                if hasattr(self.transcription_service, 'is_listening'):
                    if not self.transcription_service.is_listening:
                        logger.warning("⚠️  Listening stopped unexpectedly - restarting...")
                        try:
                            self.transcription_service.start_listening()
                        except:
                            pass

        elif self.speaking_state == SpeakingState.PAUSING:
            # Brief pause - KEEP listening (user might continue)
            if self.listening_active:
                # Ensure listening stays active during pause
                if hasattr(self.transcription_service, 'is_listening'):
                    if not self.transcription_service.is_listening:
                        logger.warning("⚠️  Listening stopped during pause - restarting...")
                        try:
                            self.transcription_service.start_listening()
                        except:
                            pass

        elif self.speaking_state == SpeakingState.FINISHED:
            # BOTH visual AND audio indicate finished → stop listening
            if self.listening_active:
                logger.info("✅ User finished speaking (both visual+audio silent) - processing...")
                # Don't stop immediately - let transcription finish processing
                # The transcription service will handle sending
                # Just mark as finished, but keep listening briefly for any final words
                time.sleep(0.5)  # Brief wait for any final audio

        # Log state periodically
        if hasattr(self, '_log_counter'):
            self._log_counter += 1
        else:
            self._log_counter = 0

        if self._log_counter % 20 == 0:  # Every 2 seconds at 10 FPS
            logger.debug(f"📊 State: {self.speaking_state.value}, Visual={self.visual_speaking}, Audio={self.audio_speaking}")

    def start(self):
        """Start unified visual-audio listening control"""
        if not self._initialize():
            return False

        self.running = True

        def control_loop():
            while self.running:
                try:
                    self.control_listening()
                    time.sleep(0.1)  # ~10 FPS
                except Exception as e:
                    logger.error(f"❌ Control loop error: {e}")
                    time.sleep(1)

        thread = threading.Thread(target=control_loop, daemon=True)
        thread.start()
        logger.info("✅ Unified visual-audio listening control started")
        logger.info("   👁️👂 Watching AND listening simultaneously (like humans)")
        logger.info("   🧠 Using speech pathologist principles")
        return True

    def stop(self):
        """Stop unified listening"""
        self.running = False
        if self.listening_active and self.transcription_service:
            try:
                self.transcription_service.stop_listening()
            except:
                pass
        if self.cap:
            self.cap.release()
        logger.info("✅ Unified visual-audio listening stopped")


def main():
    """Main function"""
    print("=" * 80)
    print("👁️👂 UNIFIED VISUAL-AUDIO LISTENING CONTROL")
    print("=" * 80)
    print()
    print("Speech Pathologist Approach:")
    print("  👁️  Watching: Lips moving + Hand gestures")
    print("  👂 Listening: Audio/voice cues")
    print("  🧠 Combining: Like real human conversation")
    print()
    print("Principles:")
    print("  - Watch AND listen simultaneously")
    print("  - Keep listening if EITHER visual OR audio indicates speaking")
    print("  - Only stop when BOTH visual AND audio indicate finished")
    print("  - Natural conversation flow (no interruptions)")
    print()

    controller = UnifiedVisualAudioListening()
    if controller.start():
        print("=" * 80)
        print("✅ UNIFIED LISTENING ACTIVE")
        print("=" * 80)
        print()
        print("System is watching AND listening like a human would.")
        print("Press Ctrl+C to stop")
        print()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
            controller.stop()


if __name__ == "__main__":


    main()