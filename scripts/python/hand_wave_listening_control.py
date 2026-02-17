#!/usr/bin/env python3
"""
Hand Wave Listening Control - REQUIRED

Uses hand waving gesture to control listening:
- Keep listening while user is waving
- Stop listening when user stops waving
- Match listening to hand movement

Tags: #HAND_WAVE #GESTURE_CONTROL #LISTENING #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from collections import deque

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

logger = get_logger("HandWaveListening")

try:
    import cv2
    import mediapipe as mp
    import numpy as np
    CV2_AVAILABLE = True
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    MEDIAPIPE_AVAILABLE = False
    logger.error("❌ OpenCV/MediaPipe not available")


class HandWaveDetector:
    """Detects hand waving gesture to control listening"""

    def __init__(self):
        self.cap = None
        self.mp_hands = None
        self.hands = None
        self.running = False

        # Wave detection
        self.last_hand_position = None
        self.movement_history = deque(maxlen=5)  # Last 5 frames (faster response)
        self.wave_threshold = 20  # Lower threshold (20 pixels, was 30) - more sensitive
        self.is_waving = False
        self.wave_duration = 0
        self.no_wave_duration = 0
        self.no_wave_threshold = 3.0  # 3.0 seconds of no wave = stopped (user might pause while speaking)

        # Listening control
        self.listening_active = False
        self.transcription_service = None

        if CV2_AVAILABLE and MEDIAPIPE_AVAILABLE:
            self._initialize()

    def _initialize(self):
        """Initialize camera and hand detection"""
        try:
            # CRITICAL: Use IR camera ONLY - regular camera emits bright white light
            # IR camera preferred to avoid distracting the operator
            try:
                from ir_camera_helper import open_ir_camera
                # Use IR camera ONLY (no backup - regular camera emits bright light)
                self.cap = open_ir_camera(use_full_spectrum_backup=False)
                if self.cap:
                    logger.info("✅ IR camera opened for hand wave detection (no bright light)")
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

            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

            logger.info("✅ Hand wave detector initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False

    def detect_waving(self):
        try:
            """Detect if user is waving hand"""
            if not self.cap or not self.hands:
                return False

            ret, frame = self.cap.read()
            if not ret:
                return False

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                frame_height, frame_width = frame.shape[:2]

                # Get wrist position (landmark 0)
                wrist = hand_landmarks.landmark[0]
                wrist_x = wrist.x * frame_width
                wrist_y = wrist.y * frame_height
                current_position = (wrist_x, wrist_y)

                # Calculate movement
                if self.last_hand_position:
                    movement = np.linalg.norm(
                        np.array(current_position) - np.array(self.last_hand_position)
                    )
                    self.movement_history.append(movement)

                    # Average movement over recent frames
                    avg_movement = np.mean(self.movement_history) if self.movement_history else 0

                    # If movement exceeds threshold, user is waving
                    if avg_movement > self.wave_threshold:
                        self.is_waving = True
                        self.wave_duration += 0.1  # Assuming ~10 FPS
                        self.no_wave_duration = 0
                    else:
                        # No movement - but wait longer before stopping (user might pause while speaking)
                        self.no_wave_duration += 0.1
                        # CRITICAL FIX: Wait 3 seconds (not 0.5s) before stopping - user might pause while speaking
                        if self.no_wave_duration >= 3.0:  # Increased from 0.5s to 3.0s
                            self.is_waving = False
                            self.wave_duration = 0

                self.last_hand_position = current_position

            return self.is_waving

        except Exception as e:
            self.logger.error(f"Error in detect_waving: {e}", exc_info=True)
            raise
    def control_listening(self):
        """Control listening based on hand waving"""
        is_waving = self.detect_waving()

        if not self.transcription_service:
            try:
                from cursor_auto_recording_transcription_fixed import CursorAutoRecordingTranscriptionFixed
                self.transcription_service = CursorAutoRecordingTranscriptionFixed(
                    project_root=project_root,
                    auto_start=False  # We'll control it manually
                )
                logger.info("✅ Transcription service initialized")
            except Exception as e:
                logger.error(f"❌ Could not initialize transcription: {e}")
                return

        # CRITICAL FIX: If waving, keep listening (don't stop during pauses)
        if is_waving:
            if not self.listening_active:
                logger.info("👋 Hand wave detected - STARTING listening IMMEDIATELY")
                try:
                    # Start listening immediately and keep it active
                    self.transcription_service.start_listening()
                    self.listening_active = True
                    # CRITICAL: Don't let pause detection stop listening while user is waving
                    if hasattr(self.transcription_service, 'dynamic_pause_timeout'):
                        # Increase pause timeout so it doesn't stop during natural pauses
                        self.transcription_service.dynamic_pause_timeout = 10.0  # 10 seconds before stopping
                except Exception as e:
                    logger.error(f"❌ Failed to start listening: {e}")
            else:
                # Already listening - ensure it stays active (don't let pause detection stop it)
                if hasattr(self.transcription_service, 'is_listening'):
                    if not self.transcription_service.is_listening:
                        logger.warning("⚠️  Listening stopped unexpectedly - restarting...")
                        try:
                            self.transcription_service.start_listening()
                        except:
                            pass
        else:
            # Not waving for 3+ seconds - stop listening
            if self.listening_active:
                logger.info("✋ Hand wave stopped (3s no movement) - STOPPING listening")
                try:
                    self.transcription_service.stop_listening()
                    self.listening_active = False
                except Exception as e:
                    logger.error(f"❌ Failed to stop listening: {e}")

    def start(self):
        """Start hand wave listening control"""
        if not self._initialize():
            return False

        self.running = True

        def control_loop():
            while self.running:
                try:
                    self.control_listening()
                    time.sleep(0.05)  # ~20 FPS - faster response (was 0.1s, now 0.05s)
                except Exception as e:
                    logger.error(f"❌ Control loop error: {e}")
                    time.sleep(1)

        thread = threading.Thread(target=control_loop, daemon=True)
        thread.start()
        logger.info("✅ Hand wave listening control started")
        logger.info("   👋 Wave your hand to start listening")
        logger.info("   ✋ Stop waving to stop listening")
        return True

    def stop(self):
        """Stop hand wave detection"""
        self.running = False
        if self.listening_active and self.transcription_service:
            try:
                self.transcription_service.stop_listening()
            except:
                pass
        if self.cap:
            self.cap.release()
        logger.info("✅ Hand wave detector stopped")


def main():
    """Main function"""
    print("=" * 80)
    print("👋 HAND WAVE LISTENING CONTROL")
    print("=" * 80)
    print()
    print("How it works:")
    print("  👋 Wave your hand → Listening starts")
    print("  ✋ Stop waving → Listening stops")
    print()
    print("Listening matches your hand movement exactly.")
    print()

    detector = HandWaveDetector()
    if detector.start():
        print("=" * 80)
        print("✅ HAND WAVE CONTROL ACTIVE")
        print("=" * 80)
        print()
        print("Wave your hand to control listening!")
        print("Press Ctrl+C to stop")
        print()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
            detector.stop()


if __name__ == "__main__":


    main()