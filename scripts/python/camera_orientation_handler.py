#!/usr/bin/env python3
"""
Camera Orientation Handler

Handles camera orientation when user is in different positions (laying down, etc.).
Detects orientation and rotates images accordingly.

Tags: #CAMERA #ORIENTATION #ROTATION #IR_CAMERA @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Optional, Tuple
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CameraOrientationHandler")


class Orientation(Enum):
    """Camera orientation"""
    NORMAL = "normal"  # Upright (0°)
    ROTATED_90_CW = "rotated_90_cw"  # Rotated 90° clockwise (user on left side)
    ROTATED_180 = "rotated_180"  # Upside down (180°)
    ROTATED_90_CCW = "rotated_90_ccw"  # Rotated 90° counter-clockwise (user on right side)


class CameraOrientationHandler:
    """
    Handles camera orientation detection and correction

    When user is laying on their side, the camera image needs to be rotated.
    """

    def __init__(self, default_orientation: Orientation = Orientation.NORMAL):
        """Initialize orientation handler"""
        self.current_orientation = default_orientation
        self.auto_detect = True
        self.logger = logger

        logger.info("=" * 80)
        logger.info("📹 CAMERA ORIENTATION HANDLER")
        logger.info("=" * 80)
        logger.info(f"   Default orientation: {default_orientation.value}")
        logger.info(f"   Auto-detect: {self.auto_detect}")
        logger.info("=" * 80)

    def detect_orientation(self, frame: np.ndarray) -> Orientation:
        """
        Detect camera orientation from frame

        Uses face detection to determine orientation.
        If face is detected rotated, assumes that's the correct orientation.
        """
        if not CV2_AVAILABLE:
            return self.current_orientation

        try:
            # Try to detect face to determine orientation
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Try all orientations
            orientations = [
                (Orientation.NORMAL, 0),
                (Orientation.ROTATED_90_CW, 90),
                (Orientation.ROTATED_180, 180),
                (Orientation.ROTATED_90_CCW, 270)
            ]

            best_orientation = Orientation.NORMAL
            max_faces = 0

            for orientation, angle in orientations:
                if angle == 0:
                    test_frame = gray
                else:
                    # Rotate for testing
                    h, w = gray.shape
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    test_frame = cv2.warpAffine(gray, M, (w, h))

                faces = face_cascade.detectMultiScale(test_frame, 1.1, 4)
                if len(faces) > max_faces:
                    max_faces = len(faces)
                    best_orientation = orientation

            if max_faces > 0:
                self.current_orientation = best_orientation
                logger.debug(f"Detected orientation: {best_orientation.value} ({max_faces} faces)")

            return self.current_orientation
        except Exception as e:
            logger.debug(f"Orientation detection error: {e}")
            return self.current_orientation

    def rotate_frame(self, frame: np.ndarray, orientation: Optional[Orientation] = None) -> np.ndarray:
        """
        Rotate frame based on orientation

        Args:
            frame: Input frame (numpy array)
            orientation: Orientation to apply (uses current if None)

        Returns:
            Rotated frame
        """
        if not CV2_AVAILABLE:
            return frame

        if orientation is None:
            orientation = self.current_orientation

        if orientation == Orientation.NORMAL:
            return frame

        h, w = frame.shape[:2]
        center = (w // 2, h // 2)

        if orientation == Orientation.ROTATED_90_CW:
            # User on left side - rotate 90° clockwise (or -90° counter-clockwise)
            M = cv2.getRotationMatrix2D(center, -90, 1.0)
            # Swap width/height after 90° rotation
            return cv2.warpAffine(frame, M, (h, w))

        elif orientation == Orientation.ROTATED_90_CCW:
            # User on right side - rotate 90° counter-clockwise (or 90° clockwise)
            M = cv2.getRotationMatrix2D(center, 90, 1.0)
            # Swap width/height after 90° rotation
            return cv2.warpAffine(frame, M, (h, w))

        elif orientation == Orientation.ROTATED_180:
            # Upside down
            M = cv2.getRotationMatrix2D(center, 180, 1.0)
            return cv2.warpAffine(frame, M, (w, h))

        return frame

    def set_orientation(self, orientation: Orientation):
        """Manually set orientation"""
        self.current_orientation = orientation
        logger.info(f"📹 Orientation set to: {orientation.value}")

    def set_user_lying_left_side(self):
        """Set orientation for user lying on left side"""
        # When user is on left side, camera sees them rotated
        # From user's perspective: rotated to the left
        # From camera's perspective: rotated 90° clockwise
        self.set_orientation(Orientation.ROTATED_90_CW)
        logger.info("📹 Orientation: User lying on left side (rotated 90° CW)")

    def set_user_lying_right_side(self):
        """Set orientation for user lying on right side"""
        self.set_orientation(Orientation.ROTATED_90_CCW)
        logger.info("📹 Orientation: User lying on right side (rotated 90° CCW)")

    def set_user_upright(self):
        """Set orientation for user upright"""
        self.set_orientation(Orientation.NORMAL)
        logger.info("📹 Orientation: User upright (normal)")


def get_camera_orientation_handler(default_orientation: Orientation = Orientation.NORMAL) -> CameraOrientationHandler:
    """Get global camera orientation handler"""
    global _camera_orientation_handler
    if '_camera_orientation_handler' not in globals():
        _camera_orientation_handler = CameraOrientationHandler(default_orientation)
    return _camera_orientation_handler


if __name__ == "__main__":
    handler = CameraOrientationHandler()
    print("=" * 80)
    print("📹 CAMERA ORIENTATION HANDLER TEST")
    print("=" * 80)
    print()
    print("User is laying on left side:")
    handler.set_user_lying_left_side()
    print()
    print("Current orientation:", handler.current_orientation.value)
    print("=" * 80)
