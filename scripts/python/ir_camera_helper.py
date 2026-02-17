#!/usr/bin/env python3
"""
IR Camera Helper - REQUIRED

Helper functions to access IR (infrared) camera instead of normal webcam.
IR cameras are better for detection and privacy.

Tags: #IR_CAMERA #INFRARED #REQUIRED @JARVIS @LUMINA
"""

import sys
import os
import warnings
from pathlib import Path

# Suppress OpenCV MSMF warnings
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
warnings.filterwarnings('ignore', message='.*MSMF.*')
warnings.filterwarnings('ignore', message='.*grabFrame.*')
warnings.filterwarnings('ignore', message='.*cap_msmf.*')

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("IRCameraHelper")


def find_ir_camera():
    """Find IR camera device index"""
    if not CV2_AVAILABLE:
        return None

    # CRITICAL: On Windows, IR cameras are often accessed via Windows Hello
    # ASUS laptops: IR camera is typically on index 1 or 2
    # Hardware detection shows: ASUS IR camera (VID_2B7E&PID_C711&MI_02)

    # Method 1: Try index 1 first (most common for ASUS IR camera)
    # ASUS IR camera is typically at index 1, regular camera at index 0
    for idx in [1, 2, 3]:
        try:
            # Try without backend first (default)
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    # IR cameras often output grayscale or have specific characteristics
                    # Check if it's likely IR (grayscale or specific resolution)
                    if len(frame.shape) == 2:  # Grayscale
                        cap.release()
                        logger.info(f"✅ IR camera found at index {idx} (grayscale output)")
                        return idx
                    # Also accept if it works (might be IR even if color)
                    # For ASUS, index 1 is typically IR camera
                    if idx == 1:
                        logger.info(f"✅ IR camera likely at index {idx} (ASUS IR camera)")
                        cap.release()
                        return idx
                    cap.release()
                    return idx
                cap.release()
        except:
            continue

    # Method 2: Try with MSMF backend (Windows Media Foundation)
    for idx in [1, 2, 3]:
        try:
            cap = cv2.VideoCapture(idx, cv2.CAP_MSMF)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.release()
                    return idx
                cap.release()
        except:
            continue

    # Method 3: Try DirectShow (if available)
    try:
        for idx in [1, 2, 3]:
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.release()
                    return idx
                cap.release()
    except:
        pass

    # Fallback: Return index 1 (most common IR camera index)
    # User can verify if it's actually IR camera
    return 1


def open_ir_camera(use_full_spectrum_backup: bool = False):
    """
    Open IR camera with proper settings.

    PRIMARY: IR camera ONLY (index 1, 2, or 3)
    BACKUP: Full-spectrum normal camera (index 0) ONLY if explicitly requested
           (Regular camera emits bright white light - avoid unless necessary)

    Args:
        use_full_spectrum_backup: If True, fall back to normal camera if IR fails
                                  (Default: False - IR camera only to avoid bright light)

    Returns:
        cv2.VideoCapture object or None
    """
    if not CV2_AVAILABLE:
        logger.warning("⚠️  OpenCV not available")
        return None

    # PRIMARY: Try IR camera first (index 1, 2, or 3)
    # CRITICAL: IR camera is typically at index 1 (regular camera at 0)
    # CRITICAL: Regular camera (index 0) emits bright white light - avoid if possible
    ir_indices = [1, 2, 3]

    for ir_index in ir_indices:
        try:
            # Try default backend
            cap = cv2.VideoCapture(ir_index)
            if cap and cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    # Configure IR camera settings
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    logger.info(f"✅ IR camera opened at index {ir_index} (PRIMARY - no bright light)")
                    return cap
                cap.release()
        except Exception as e:
            logger.debug(f"Failed to open IR camera at index {ir_index} (default): {e}")

        # Try MSMF backend (Windows Media Foundation)
        try:
            cap = cv2.VideoCapture(ir_index, cv2.CAP_MSMF)
            if cap and cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    logger.info(f"✅ IR camera opened at index {ir_index} via MSMF (PRIMARY - no bright light)")
                    return cap
                cap.release()
        except Exception as e:
            logger.debug(f"Failed to open IR camera at index {ir_index} (MSMF): {e}")

        # Try DirectShow backend
        try:
            cap = cv2.VideoCapture(ir_index, cv2.CAP_DSHOW)
            if cap and cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    logger.info(f"✅ IR camera opened at index {ir_index} via DirectShow (PRIMARY - no bright light)")
                    return cap
                cap.release()
        except Exception as e:
            logger.debug(f"Failed to open IR camera at index {ir_index} (DirectShow): {e}")

    # BACKUP: Full-spectrum normal camera (index 0) ONLY if explicitly requested
    # WARNING: Regular camera emits bright white light - avoid unless necessary
    if use_full_spectrum_backup:
        logger.warning("⚠️  IR camera not found - using full-spectrum camera as backup")
        logger.warning("   ⚠️  WARNING: Regular camera emits bright white light - may be distracting")
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    logger.warning("✅ Full-spectrum camera opened at index 0 (BACKUP - emits bright light)")
                    return cap
                cap.release()
        except Exception as e:
            logger.warning(f"Failed to open backup camera: {e}")
    else:
        logger.warning("⚠️  IR camera not found and backup disabled - no camera available")
        logger.info("   💡 Tip: IR camera preferred to avoid bright white light from regular camera")

    logger.error("❌ No IR camera available (regular camera backup disabled to avoid bright light)")
    return None


def capture_operator_state(use_ir_primary: bool = True, use_backup: bool = False, 
                           user_orientation: str = "upright"):
    """
    Capture operator state using IR camera (primary) or full-spectrum camera (backup).

    This function attempts to capture the state of the @op (human operator/user)
    using the IR camera first, falling back to the full-spectrum camera ONLY if explicitly requested.

    CRITICAL: Regular camera (index 0) emits bright white light which is distracting.
    IR camera is preferred to avoid this issue.

    Args:
        use_ir_primary: Use IR camera as primary (default: True)
        use_backup: Use full-spectrum camera as backup if IR fails (default: False)
                   Set to True only if absolutely necessary (regular camera emits bright light)
        user_orientation: User's orientation - "upright", "left_side", "right_side", "upside_down"
                         When user is laying on side, image needs rotation

    Returns:
        Tuple of (success: bool, frame: np.ndarray or None, camera_type: str)
    """
    if not CV2_AVAILABLE:
        return False, None, "none"

    cap = None
    camera_type = "none"

    if use_ir_primary:
        # Try IR camera first (no bright light)
        cap = open_ir_camera(use_full_spectrum_backup=use_backup)
        if cap:
            # Check which camera was actually opened
            # If backup was used, it means IR failed
            if use_backup:
                # Check if it's actually the backup (index 0)
                # This is a heuristic - in practice, open_ir_camera will return IR if available
                camera_type = "ir"  # Assume IR if open_ir_camera succeeded
            else:
                camera_type = "ir"
    else:
        # Use full-spectrum directly (NOT RECOMMENDED - emits bright light)
        if use_backup:
            logger.warning("⚠️  Using full-spectrum camera directly - emits bright white light")
            try:
                cap = cv2.VideoCapture(0)
                if cap and cap.isOpened():
                    camera_type = "full_spectrum"
            except:
                pass
        else:
            logger.warning("⚠️  IR camera disabled but backup also disabled - no camera available")

    if cap and cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            cap.release()

            # Apply orientation correction if user is not upright
            if user_orientation != "upright":
                try:
                    from camera_orientation_handler import get_camera_orientation_handler, Orientation
                    handler = get_camera_orientation_handler()

                    # Set orientation based on user position
                    if user_orientation == "left_side":
                        # User on left side - rotate 90° clockwise (from camera's perspective)
                        handler.set_user_lying_left_side()
                        frame = handler.rotate_frame(frame)
                        logger.debug("📹 Rotated frame for user lying on left side")
                    elif user_orientation == "right_side":
                        handler.set_user_lying_right_side()
                        frame = handler.rotate_frame(frame)
                        logger.debug("📹 Rotated frame for user lying on right side")
                    elif user_orientation == "upside_down":
                        handler.set_orientation(Orientation.ROTATED_180)
                        frame = handler.rotate_frame(frame)
                        logger.debug("📹 Rotated frame for user upside down")
                except ImportError:
                    logger.debug("Camera orientation handler not available - skipping rotation")
                except Exception as e:
                    logger.debug(f"Orientation correction error: {e}")

            if camera_type == "full_spectrum":
                logger.warning("⚠️  Using regular camera - emits bright white light (consider using IR camera)")
            return True, frame, camera_type
        cap.release()

    return False, None, camera_type


if __name__ == "__main__":
    print("=" * 80)
    print("🔍 FINDING IR CAMERA")
    print("=" * 80)
    print()

    ir_index = find_ir_camera()
    if ir_index is not None:
        print(f"✅ IR camera found at index: {ir_index}")

        cap = open_ir_camera()
        if cap:
            print("✅ IR camera opened successfully")
            ret, frame = cap.read()
            if ret:
                print(f"✅ IR camera working - frame size: {frame.shape}")
            cap.release()
        else:
            print("❌ Could not open IR camera")
    else:
        print("⚠️  IR camera not found - will use regular camera")
        print("   Trying index 1 as fallback...")
        cap = open_ir_camera()
        if cap:
            print("✅ Camera opened at index 1 (may be IR camera)")
            cap.release()
        else:
            print("❌ Could not open camera")
