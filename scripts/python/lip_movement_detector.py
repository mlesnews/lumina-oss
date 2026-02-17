#!/usr/bin/env python3
"""
Lip Movement Detector - REQUIRED

Detects when user is speaking by watching their lips/mouth move.
Waits for user to finish speaking before responding.

Tags: #LIP_DETECTION #SPEECH_DETECTION #CAMERA #REQUIRED @JARVIS @LUMINA
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

logger = get_logger("LipMovementDetector")

try:
    import cv2
    import mediapipe as mp
    import numpy as np
    CV2_AVAILABLE = True
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    MEDIAPIPE_AVAILABLE = False
    logger.error("❌ OpenCV/MediaPipe not available - install: pip install opencv-python mediapipe")


class LipMovementDetector:
    """Detects lip/mouth movement to know when user is speaking"""

    def __init__(self):
        self.cap = None
        self.mp_face_mesh = None
        self.face_mesh = None
        self.running = False

        # Lip landmark indices (MediaPipe face mesh)
        # Upper lip: 12, 13, 14, 15, 16, 17
        # Lower lip: 0, 1, 2, 3, 4, 5
        self.upper_lip_indices = [12, 13, 14, 15, 16, 17]
        self.lower_lip_indices = [0, 1, 2, 3, 4, 5]

        # Movement detection
        self.last_lip_distance = 0
        self.movement_threshold = 0.02  # Threshold for detecting movement
        self.movement_history = deque(maxlen=10)  # Last 10 frames

        # Speaking state
        self.is_speaking = False
        self.silence_duration = 0
        self.silence_threshold = 1.5  # 1.5 seconds of silence = finished speaking

        if CV2_AVAILABLE and MEDIAPIPE_AVAILABLE:
            self._initialize()

    def _initialize(self):
        """Initialize camera and face mesh"""
        try:
            # CRITICAL: Use IR camera ONLY - regular camera emits bright white light
            # IR camera preferred to avoid distracting the operator
            try:
                from ir_camera_helper import open_ir_camera
                # Use IR camera ONLY (no backup - regular camera emits bright light)
                self.cap = open_ir_camera(use_full_spectrum_backup=False)
                if self.cap:
                    logger.info("✅ IR camera opened for lip movement detection (no bright light)")
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

            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

            logger.info("✅ Lip movement detector initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False

    def _calculate_lip_distance(self, landmarks, frame_width, frame_height):
        """Calculate distance between upper and lower lip"""
        if not landmarks:
            return 0

        # Get upper lip center
        upper_lip_points = []
        for idx in self.upper_lip_indices:
            if idx < len(landmarks.landmark):
                x = landmarks.landmark[idx].x * frame_width
                y = landmarks.landmark[idx].y * frame_height
                upper_lip_points.append((x, y))

        # Get lower lip center
        lower_lip_points = []
        for idx in self.lower_lip_indices:
            if idx < len(landmarks.landmark):
                x = landmarks.landmark[idx].x * frame_width
                y = landmarks.landmark[idx].y * frame_height
                lower_lip_points.append((x, y))

        if not upper_lip_points or not lower_lip_points:
            return 0

        # Calculate centers
        upper_center = np.mean(upper_lip_points, axis=0)
        lower_center = np.mean(lower_lip_points, axis=0)

        # Distance between centers
        distance = np.linalg.norm(upper_center - lower_center)
        return distance

    def detect_speaking(self):
        try:
            """Detect if user is currently speaking"""
            if not self.cap or not self.face_mesh:
                return False

            ret, frame = self.cap.read()
            if not ret:
                return False

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(frame_rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                frame_height, frame_width = frame.shape[:2]

                # Calculate lip distance
                lip_distance = self._calculate_lip_distance(landmarks, frame_width, frame_height)

                # Calculate movement (change in distance)
                if self.last_lip_distance > 0:
                    movement = abs(lip_distance - self.last_lip_distance)
                    self.movement_history.append(movement)

                    # Average movement over recent frames
                    avg_movement = np.mean(self.movement_history) if self.movement_history else 0

                    # If movement exceeds threshold, user is speaking
                    if avg_movement > self.movement_threshold:
                        self.is_speaking = True
                        self.silence_duration = 0
                    else:
                        # No movement - check if silence threshold reached
                        self.silence_duration += 0.1  # Assuming ~10 FPS
                        if self.silence_duration >= self.silence_threshold:
                            self.is_speaking = False

                self.last_lip_distance = lip_distance

            return self.is_speaking

        except Exception as e:
            self.logger.error(f"Error in detect_speaking: {e}", exc_info=True)
            raise
    def wait_for_silence(self, timeout=10.0):
        """Wait for user to finish speaking (silence detected)"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.detect_speaking():
                # Not speaking - check if silence threshold reached
                if self.silence_duration >= self.silence_threshold:
                    logger.info("✅ User finished speaking (silence detected)")
                    return True
            time.sleep(0.1)

        logger.warning("⚠️  Timeout waiting for silence")
        return False

    def start_monitoring(self, callback=None):
        """Start monitoring lip movement"""
        if not self._initialize():
            return False

        self.running = True

        def monitor_loop():
            while self.running:
                is_speaking = self.detect_speaking()
                if callback:
                    callback(is_speaking)
                time.sleep(0.1)  # ~10 FPS

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info("✅ Lip movement monitoring started")
        return True

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.cap:
            self.cap.release()
        logger.info("✅ Lip movement detector stopped")


def wait_for_user_to_finish_speaking(timeout=10.0):
    """Wait for user to finish speaking before responding"""
    detector = LipMovementDetector()
    if detector._initialize():
        detector.wait_for_silence(timeout)
        detector.stop()
        return True
    return False


if __name__ == "__main__":
    detector = LipMovementDetector()
    if detector.start_monitoring():
        print("👄 Lip movement detector running")
        print("   Watching for when you're speaking...")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
            detector.stop()
