#!/usr/bin/env python3
"""
Camera Keyboard Reach Detector

Uses laptop camera to:
1. Identify user (basic recognition, not detailed)
2. Detect when user reaches for keyboard
3. Count keyboard reach events
4. Correlate with system activity to identify automation failures

Tags: #CAMERA #COMPUTER_VISION #AUTOMATION_MONITORING @JARVIS @LUMINA
"""

import sys
import os
import warnings
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from collections import deque

# Suppress OpenCV MSMF warnings
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
warnings.filterwarnings('ignore', message='.*MSMF.*')
warnings.filterwarnings('ignore', message='.*grabFrame.*')
warnings.filterwarnings('ignore', message='.*cap_msmf.*')

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CameraKeyboardReach")

# Try to import OpenCV
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None
    logger.warning("⚠️  OpenCV not available - install: pip install opencv-python")

# Try to import mediapipe for hand detection
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None
    logger.warning("⚠️  MediaPipe not available - install: pip install mediapipe")


class CameraKeyboardReachDetector:
    """
    Detects when user reaches for keyboard using camera

    Tracks:
    - User presence/identity (basic)
    - Hand/keyboard reaching gestures
    - Frequency of manual interventions
    - Correlation with system activity
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize camera-based keyboard reach detector"""
        if not OPENCV_AVAILABLE:
            raise ImportError("OpenCV required for camera access")

        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.running = False
        self.capture_thread = None
        self.cap = None
        self.use_ir_camera = True  # REQUIRED: Use IR camera

        # Detection state
        self.user_detected = False
        self.keyboard_reach_count = 0
        self.reach_events: List[Dict[str, Any]] = []
        self.last_reach_time = 0
        self.reach_cooldown = 2.0  # Don't count same reach twice within 2 seconds

        # Hand detection (if MediaPipe available)
        if MEDIAPIPE_AVAILABLE:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
        else:
            self.hands = None
            self.mp_drawing = None

        # User baseline (for basic recognition)
        self.user_baseline = None
        self.baseline_captured = False

        # Statistics
        self.stats = {
            "total_reaches": 0,
            "reaches_per_hour": 0,
            "last_reach": None,
            "session_start": datetime.now(),
            "user_present": False
        }

        logger.info("✅ Camera Keyboard Reach Detector initialized")

    def _capture_user_baseline(self, frame):
        """Capture baseline image of user for basic recognition"""
        if self.baseline_captured:
            return

        try:
            # Simple baseline: capture face region (if face detection available)
            # For now, just mark as captured after first frame
            self.user_baseline = frame.copy()
            self.baseline_captured = True
            logger.info("✅ User baseline captured")
        except Exception as e:
            logger.debug(f"Baseline capture failed: {e}")

    def _detect_user_presence(self, frame) -> bool:
        """Detect if user is present (basic recognition)"""
        try:
            # Simple method: detect motion or face
            # For basic recognition, we just check if there's a person-like shape

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Simple motion detection (compare to baseline)
            if self.user_baseline is not None:
                baseline_gray = cv2.cvtColor(self.user_baseline, cv2.COLOR_BGR2GRAY)
                diff = cv2.absdiff(gray, baseline_gray)
                motion = np.sum(diff) / (frame.shape[0] * frame.shape[1])

                # If significant motion, user is likely present
                if motion > 10:  # Threshold
                    return True

            # Fallback: assume user is present if camera is working
            return True

        except Exception as e:
            logger.debug(f"User presence detection failed: {e}")
            return False

    def _detect_keyboard_reach(self, frame) -> bool:
        """
        Detect when user reaches for keyboard

        Indicators:
        - Hand moves toward bottom of frame (keyboard area)
        - Hand position changes significantly
        - Hand appears in lower portion of frame
        """
        try:
            if not MEDIAPIPE_AVAILABLE:
                # Fallback: simple motion detection in lower frame area
                return self._detect_reach_simple(frame)

            # Use MediaPipe for hand detection
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                frame_height, frame_width = frame.shape[:2]
                keyboard_zone_top = int(frame_height * 0.6)  # Lower 40% is keyboard zone

                for hand_landmarks in results.multi_hand_landmarks:
                    # Check if hand is in keyboard zone (lower portion of frame)
                    wrist_y = hand_landmarks.landmark[0].y * frame_height

                    # Also check if hand is moving toward keyboard
                    # (wrist is below middle of frame)
                    if wrist_y > keyboard_zone_top:
                        # Hand is in keyboard zone - likely reaching for keyboard
                        return True

                    # Check hand position relative to center
                    # If hand is moving down and toward center, likely reaching
                    index_tip_y = hand_landmarks.landmark[8].y * frame_height
                    if index_tip_y > keyboard_zone_top:
                        return True

            return False

        except Exception as e:
            logger.debug(f"Keyboard reach detection failed: {e}")
            return False

    def _detect_reach_simple(self, frame) -> bool:
        """Simple motion-based reach detection (fallback)"""
        try:
            # Focus on lower portion of frame (keyboard area)
            frame_height, frame_width = frame.shape[:2]
            keyboard_zone = frame[int(frame_height * 0.6):, :]

            # Convert to grayscale
            gray = cv2.cvtColor(keyboard_zone, cv2.COLOR_BGR2GRAY)

            # Simple motion detection using frame difference
            if not hasattr(self, 'prev_keyboard_frame'):
                self.prev_keyboard_frame = gray
                return False

            # Calculate difference
            diff = cv2.absdiff(gray, self.prev_keyboard_frame)
            motion = np.sum(diff) / (keyboard_zone.shape[0] * keyboard_zone.shape[1])

            self.prev_keyboard_frame = gray

            # Threshold for reach detection
            if motion > 15:  # Significant motion in keyboard zone
                return True

            return False

        except Exception as e:
            logger.debug(f"Simple reach detection failed: {e}")
            return False

    def _process_frame(self, frame):
        """Process a single frame"""
        try:
            # Capture baseline on first frame
            if not self.baseline_captured:
                self._capture_user_baseline(frame)

            # Detect user presence
            user_present = self._detect_user_presence(frame)
            self.user_detected = user_present
            self.stats["user_present"] = user_present

            # Detect keyboard reach
            current_time = time.time()
            if current_time - self.last_reach_time > self.reach_cooldown:
                reach_detected = self._detect_keyboard_reach(frame)

                if reach_detected:
                    self.keyboard_reach_count += 1
                    self.stats["total_reaches"] += 1
                    self.last_reach_time = current_time

                    # Record event
                    event = {
                        "timestamp": datetime.now().isoformat(),
                        "count": self.keyboard_reach_count,
                        "user_present": user_present
                    }
                    self.reach_events.append(event)

                    # Keep only last 100 events
                    if len(self.reach_events) > 100:
                        self.reach_events.pop(0)

                    self.stats["last_reach"] = event["timestamp"]

                    logger.info(f"🎹 Keyboard reach detected! (Total: {self.keyboard_reach_count})")

                    # Calculate reaches per hour
                    session_duration = (datetime.now() - self.stats["session_start"]).total_seconds() / 3600
                    if session_duration > 0:
                        self.stats["reaches_per_hour"] = self.keyboard_reach_count / session_duration

                    return True

            return False

        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return False

    def _capture_loop(self):
        """Main camera capture loop"""
        logger.info("📹 Starting camera capture...")

        try:
            # CRITICAL: Use IR camera ONLY - regular camera emits bright white light
            # IR camera preferred to avoid distracting the operator
            try:
                from ir_camera_helper import open_ir_camera
                # Use IR camera ONLY (no backup - regular camera emits bright light)
                self.cap = open_ir_camera(use_full_spectrum_backup=False)
                if self.cap:
                    logger.info("✅ IR camera opened for keyboard reach detection (no bright light)")
                else:
                    logger.error("❌ IR camera not available - NOT using regular camera to avoid bright light")
                    logger.warning("   💡 Please ensure IR camera is available or enable backup if necessary")
                    self.cap = None
            except ImportError:
                logger.error("❌ IR camera helper not available")
                logger.warning("   💡 Regular camera emits bright white light - IR camera preferred")
                self.cap = None

            if not self.cap or not self.cap.isOpened():
                logger.error("❌ Could not open camera")
                self.running = False
                return

            logger.info("✅ Camera opened successfully")

            consecutive_failures = 0
            max_failures = 10  # Stop after 10 consecutive failures

            while self.running:
                try:
                    ret, frame = self.cap.read()

                    if not ret or frame is None:
                        consecutive_failures += 1
                        if consecutive_failures >= max_failures:
                            logger.error(f"❌ Camera read failed {consecutive_failures} times - stopping")
                            self.running = False
                            break
                        time.sleep(0.5)  # Wait longer between retries
                        continue

                    # Reset failure counter on success
                    consecutive_failures = 0
                except Exception as e:
                    consecutive_failures += 1
                    logger.debug(f"Camera read exception: {e}")
                    if consecutive_failures >= max_failures:
                        logger.error(f"❌ Camera read exceptions ({consecutive_failures}) - stopping")
                        self.running = False
                        break
                    time.sleep(0.5)
                    continue

                # Process frame
                self._process_frame(frame)

                # Small delay to prevent CPU overload
                time.sleep(0.1)  # ~10 FPS

        except Exception as e:
            logger.error(f"❌ Camera capture error: {e}")
        finally:
            if self.cap:
                self.cap.release()
            logger.info("📹 Camera released")

    def start(self):
        """Start camera monitoring"""
        if self.running:
            logger.warning("⚠️  Already running")
            return True

        if not OPENCV_AVAILABLE:
            logger.error("❌ OpenCV not available")
            return False

        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

        logger.info("✅ Camera monitoring started")
        return True

    def stop(self):
        """Stop camera monitoring"""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        logger.info("👋 Camera monitoring stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get detection statistics"""
        return {
            **self.stats,
            "current_reach_count": self.keyboard_reach_count,
            "user_detected": self.user_detected,
            "recent_events": self.reach_events[-10:] if self.reach_events else []
        }

    def reset_count(self):
        """Reset reach counter"""
        self.keyboard_reach_count = 0
        self.stats["total_reaches"] = 0
        self.stats["session_start"] = datetime.now()
        logger.info("🔄 Reach counter reset")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Camera Keyboard Reach Detector")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--reset", action="store_true", help="Reset counter")

    args = parser.parse_args()

    try:
        detector = CameraKeyboardReachDetector()

        if args.reset:
            detector.reset_count()
            print("✅ Counter reset")
            return 0

        if args.stats:
            stats = detector.get_stats()
            print("="*80)
            print("📊 KEYBOARD REACH STATISTICS")
            print("="*80)
            print(f"Total Reaches: {stats['total_reaches']}")
            print(f"Reaches Per Hour: {stats['reaches_per_hour']:.2f}")
            print(f"Last Reach: {stats['last_reach'] or 'Never'}")
            print(f"User Present: {stats['user_present']}")
            print(f"Session Duration: {(datetime.now() - stats['session_start']).total_seconds() / 60:.1f} minutes")
            return 0

        if args.start or not any([args.stats, args.reset]):
            print("="*80)
            print("📹 CAMERA KEYBOARD REACH DETECTOR")
            print("="*80)
            print()
            print("Monitoring camera for keyboard reach events...")
            print("Press Ctrl+C to stop")
            print()

            detector.start()

            try:
                while True:
                    time.sleep(1)
                    # Print stats every 10 seconds
                    if int(time.time()) % 10 == 0:
                        stats = detector.get_stats()
                        print(f"Reaches: {stats['total_reaches']} | Per Hour: {stats['reaches_per_hour']:.2f} | User: {stats['user_present']}")
            except KeyboardInterrupt:
                pass

            detector.stop()
            return 0

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main() or 0)