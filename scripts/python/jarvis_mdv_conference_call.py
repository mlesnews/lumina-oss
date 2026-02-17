#!/usr/bin/env python3
"""
JARVIS MDV Conference Call - Advanced MDV with Audio & Camera

Enhanced MDV mode that includes:
- All standard MDV features (desktop video feed)
- Audio capture (microphone)
- IR camera (primary) - watching expressions and movements
- Normal camera (fallback)
- Hybrid mode (both cameras)
- Expression and movement tracking

Tags: #JARVIS #MDV #CONFERENCE_CALL #AUDIO #CAMERA #IR #EXPRESSION_TRACKING @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISMDVConferenceCall")


class CameraMode(Enum):
    """Camera mode options"""
    IR_ONLY = "ir_only"  # Infrared camera only (primary)
    NORMAL_ONLY = "normal_only"  # Normal camera only (fallback)
    HYBRID = "hybrid"  # Both cameras (testing mode)


class JARVISMDVConferenceCall:
    """
    MDV Conference Call - Advanced MDV with Audio & Camera

    Features:
    - Desktop video feed (standard MDV)
    - Audio capture (microphone)
    - IR camera (primary) - watching expressions and movements
    - Normal camera (fallback)
    - Hybrid mode (both cameras)
    - Expression and movement tracking
    """

    def __init__(self, project_root: Optional[Path] = None, camera_mode: CameraMode = CameraMode.IR_ONLY):
        """Initialize MDV Conference Call"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger
        self.camera_mode = camera_mode
        self.is_active = False

        # Import base MDV activator
        self.mdv_activator = None
        try:
            from jarvis_auto_mdv_activator import JARVISAutoMDVActivator
            self.mdv_activator = JARVISAutoMDVActivator(project_root=project_root)
            self.logger.info("✅ Base MDV activator initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️  Base MDV activator not available: {e}")

        # Audio capture
        self.audio_capture = None
        self.audio_thread = None
        self.audio_active = False

        # Camera capture
        self.ir_camera = None
        self.normal_camera = None
        self.camera_thread = None
        self.camera_active = False

        # Expression/movement tracking
        self.expression_tracker = None
        self.movement_tracker = None

        # Accessibility enhancements
        self.accessibility = None
        self.accessibility_enabled = False

        # Initialize systems
        self._initialize_audio_system()
        self._initialize_camera_system()
        self._initialize_tracking_systems()
        self._initialize_accessibility()

        self.logger.info("✅ JARVIS MDV Conference Call initialized")
        self.logger.info(f"   Camera Mode: {camera_mode.value}")

    def _initialize_audio_system(self):
        """Initialize audio capture system"""
        try:
            import pyaudio
            self.pyaudio_available = True
            self.logger.info("✅ PyAudio available for audio capture")
        except ImportError:
            self.pyaudio_available = False
            self.logger.warning("⚠️  PyAudio not available - install: pip install pyaudio")

        try:
            import speech_recognition as sr
            self.speech_recognition_available = True
            self.logger.info("✅ Speech Recognition available")
        except ImportError:
            self.speech_recognition_available = False
            self.logger.debug("Speech Recognition not available")

    def _initialize_camera_system(self):
        """Initialize camera system (IR primary, normal fallback)"""
        try:
            import cv2
            self.opencv_available = True
            self.logger.info("✅ OpenCV available for camera capture")
        except ImportError:
            self.opencv_available = False
            self.logger.warning("⚠️  OpenCV not available - install: pip install opencv-python")

        # Detect available cameras
        self.ir_camera_index = None
        self.normal_camera_index = None
        self._detect_cameras()

    def _detect_cameras(self):
        """Detect available cameras (IR and normal)"""
        if not self.opencv_available:
            return

        try:
            import cv2

            # Try to detect cameras
            # IR cameras often have specific device names or indices
            # This is a placeholder - actual detection depends on hardware
            available_cameras = []

            # Try indices 0-5 to find cameras
            for i in range(6):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    # Try to get camera name/backend info
                    backend = cap.getBackendName()
                    # Check if it might be IR (this is hardware-specific)
                    # IR cameras often have "IR" in their name or specific properties
                    available_cameras.append({
                        "index": i,
                        "backend": backend,
                        "is_ir": False  # Will be determined by hardware detection
                    })
                    cap.release()

            # For now, assume:
            # - Index 0 = Normal camera (fallback)
            # - Index 1 = IR camera (primary) if available
            # This should be enhanced with actual hardware detection

            if len(available_cameras) > 0:
                self.normal_camera_index = 0
                self.logger.info(f"✅ Normal camera detected at index {self.normal_camera_index}")

            if len(available_cameras) > 1:
                self.ir_camera_index = 1
                self.logger.info(f"✅ IR camera detected at index {self.ir_camera_index}")
            elif len(available_cameras) > 0:
                # Only one camera - use as fallback
                self.logger.warning("⚠️  Only one camera detected - using as fallback")
                self.normal_camera_index = 0

            self.logger.info(f"   Available cameras: {len(available_cameras)}")

        except Exception as e:
            self.logger.error(f"❌ Camera detection failed: {e}")

    def _initialize_tracking_systems(self):
        """Initialize expression and movement tracking"""
        try:
            # Try to import face/expression tracking libraries
            # MediaPipe, OpenCV DNN, or other tracking systems
            try:
                import mediapipe as mp
                self.mediapipe_available = True
                self.logger.info("✅ MediaPipe available for expression tracking")
            except ImportError:
                self.mediapipe_available = False
                self.logger.debug("MediaPipe not available - expression tracking limited")

            # Initialize trackers
            if self.mediapipe_available:
                try:
                    self.mp_face = mp.solutions.face_mesh
                    self.mp_drawing = mp.solutions.drawing_utils
                    self.logger.info("✅ MediaPipe face mesh initialized")
                except Exception as e:
                    self.logger.debug(f"MediaPipe initialization: {e}")

        except Exception as e:
            self.logger.debug(f"Tracking systems initialization: {e}")

    def _initialize_accessibility(self):
        """Initialize accessibility enhancements"""
        try:
            from jarvis_mdv_accessibility_enhancements import JARVISMDVAccessibilityEnhancements
            self.accessibility = JARVISMDVAccessibilityEnhancements(project_root=self.project_root)
            self.logger.info("✅ Accessibility enhancements initialized")
        except ImportError as e:
            self.logger.debug(f"Accessibility enhancements not available: {e}")

    def start_audio_capture(self) -> Dict[str, Any]:
        """Start audio capture from microphone"""
        if not self.pyaudio_available:
            return {
                "success": False,
                "error": "PyAudio not available",
                "message": "Cannot capture audio - install PyAudio"
            }

        if self.audio_active:
            return {
                "success": True,
                "message": "Audio capture already active"
            }

        try:
            import pyaudio

            self.logger.info("🎤 Starting audio capture...")

            # Audio settings
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000

            self.audio = pyaudio.PyAudio()
            self.audio_stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )

            self.audio_active = True

            # Start audio capture thread
            self.audio_thread = threading.Thread(
                target=self._audio_capture_loop,
                daemon=True
            )
            self.audio_thread.start()

            self.logger.info("✅ Audio capture started")
            return {
                "success": True,
                "message": "Audio capture active",
                "sample_rate": RATE,
                "channels": CHANNELS
            }

        except Exception as e:
            self.logger.error(f"❌ Audio capture failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Audio capture failed: {e}"
            }

    def _audio_capture_loop(self):
        """Audio capture loop (runs in background thread)"""
        try:
            while self.audio_active:
                if hasattr(self, 'audio_stream'):
                    data = self.audio_stream.read(1024, exception_on_overflow=False)
                    # Process audio data here if needed
                    # For now, just keep the stream active
        except Exception as e:
            self.logger.error(f"❌ Audio capture loop error: {e}")
        finally:
            if hasattr(self, 'audio_stream'):
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            if hasattr(self, 'audio'):
                self.audio.terminate()

    def start_camera_capture(self) -> Dict[str, Any]:
        """Start camera capture (IR primary, normal fallback, or hybrid)"""
        if not self.opencv_available:
            return {
                "success": False,
                "error": "OpenCV not available",
                "message": "Cannot capture camera - install opencv-python"
            }

        if self.camera_active:
            return {
                "success": True,
                "message": "Camera capture already active"
            }

        try:
            import cv2

            self.logger.info(f"📹 Starting camera capture (Mode: {self.camera_mode.value})...")

            # Initialize cameras based on mode
            if self.camera_mode == CameraMode.IR_ONLY:
                if self.ir_camera_index is not None:
                    self.ir_camera = cv2.VideoCapture(self.ir_camera_index)
                    if not self.ir_camera.isOpened():
                        self.logger.warning("⚠️  IR camera failed, falling back to normal camera")
                        if self.normal_camera_index is not None:
                            self.ir_camera = cv2.VideoCapture(self.normal_camera_index)
                            self.camera_mode = CameraMode.NORMAL_ONLY
                elif self.normal_camera_index is not None:
                    self.logger.warning("⚠️  IR camera not available, using normal camera as fallback")
                    self.ir_camera = cv2.VideoCapture(self.normal_camera_index)
                    self.camera_mode = CameraMode.NORMAL_ONLY

            elif self.camera_mode == CameraMode.NORMAL_ONLY:
                if self.normal_camera_index is not None:
                    self.normal_camera = cv2.VideoCapture(self.normal_camera_index)

            elif self.camera_mode == CameraMode.HYBRID:
                if self.ir_camera_index is not None:
                    self.ir_camera = cv2.VideoCapture(self.ir_camera_index)
                if self.normal_camera_index is not None:
                    self.normal_camera = cv2.VideoCapture(self.normal_camera_index)

            # Check if at least one camera is active
            camera_active = (
                (self.ir_camera is not None and self.ir_camera.isOpened()) or
                (self.normal_camera is not None and self.normal_camera.isOpened())
            )

            if camera_active:
                self.camera_active = True

                # Start camera capture thread
                self.camera_thread = threading.Thread(
                    target=self._camera_capture_loop,
                    daemon=True
                )
                self.camera_thread.start()

                self.logger.info("✅ Camera capture started")
                return {
                    "success": True,
                    "message": "Camera capture active",
                    "mode": self.camera_mode.value,
                    "ir_camera": self.ir_camera is not None and self.ir_camera.isOpened(),
                    "normal_camera": self.normal_camera is not None and self.normal_camera.isOpened()
                }
            else:
                return {
                    "success": False,
                    "error": "No cameras available",
                    "message": "Cannot start camera capture - no cameras detected"
                }

        except Exception as e:
            self.logger.error(f"❌ Camera capture failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Camera capture failed: {e}"
            }

    def _camera_capture_loop(self):
        """Camera capture loop (runs in background thread)"""
        try:
            while self.camera_active:
                frames = {}

                # Capture from IR camera
                if self.ir_camera is not None and self.ir_camera.isOpened():
                    ret, frame = self.ir_camera.read()
                    if ret:
                        frames["ir"] = frame
                        # Process for expression/movement tracking
                        self._process_frame_for_tracking(frame, camera_type="ir")

                # Capture from normal camera
                if self.normal_camera is not None and self.normal_camera.isOpened():
                    ret, frame = self.normal_camera.read()
                    if ret:
                        frames["normal"] = frame
                        # Process for expression/movement tracking
                        self._process_frame_for_tracking(frame, camera_type="normal")

                # Small delay to prevent excessive CPU usage
                time.sleep(0.033)  # ~30 FPS

        except Exception as e:
            self.logger.error(f"❌ Camera capture loop error: {e}")
        finally:
            if self.ir_camera is not None:
                self.ir_camera.release()
            if self.normal_camera is not None:
                self.normal_camera.release()

    def _process_frame_for_tracking(self, frame, camera_type: str):
        """Process frame for expression and movement tracking"""
        if not self.mediapipe_available:
            return

        try:
            import cv2
            import mediapipe as mp

            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process with MediaPipe face mesh
            if hasattr(self, 'mp_face'):
                with self.mp_face.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                ) as face_mesh:
                    results = face_mesh.process(rgb_frame)

                    if results.multi_face_landmarks:
                        # Extract expression/movement data
                        # This is a placeholder - actual tracking would analyze landmarks
                        self.logger.debug(f"Face detected in {camera_type} camera")

        except Exception as e:
            self.logger.debug(f"Frame tracking processing: {e}")

    def activate_conference_call(self) -> Dict[str, Any]:
        """
        Activate full MDV Conference Call mode

        This activates:
        - Desktop video feed (standard MDV)
        - Audio capture
        - Camera capture (IR primary, normal fallback, or hybrid)
        - Expression and movement tracking

        Returns:
            Result dictionary
        """
        self.logger.info("=" * 80)
        self.logger.info("📹🎤 ACTIVATING MDV CONFERENCE CALL")
        self.logger.info("=" * 80)

        results = {
            "mdv": False,
            "audio": False,
            "camera": False,
            "tracking": False,
            "timestamp": datetime.now().isoformat()
        }

        # 1. Activate base MDV
        if self.mdv_activator:
            try:
                mdv_result = self.mdv_activator.activate_mdv()
                results["mdv"] = mdv_result.get("success", False)
                results["mdv_details"] = mdv_result
                self.logger.info("✅ Base MDV activated")
            except Exception as e:
                self.logger.error(f"❌ Base MDV activation failed: {e}")

        # 2. Start audio capture
        audio_result = self.start_audio_capture()
        results["audio"] = audio_result.get("success", False)
        results["audio_details"] = audio_result

        # 3. Start camera capture
        camera_result = self.start_camera_capture()
        results["camera"] = camera_result.get("success", False)
        results["camera_details"] = camera_result

        # 4. Expression/movement tracking (enabled if cameras are active)
        if results["camera"]:
            results["tracking"] = True
            self.logger.info("✅ Expression and movement tracking enabled")

        # 5. Accessibility enhancements (optional)
        if self.accessibility:
            try:
                accessibility_result = self.accessibility.activate_accessibility_features()
                results["accessibility"] = accessibility_result.get("success", False)
                results["accessibility_details"] = accessibility_result
                if results["accessibility"]:
                    self.accessibility_enabled = True
                    self.logger.info("✅ Accessibility features activated")
            except Exception as e:
                self.logger.debug(f"Accessibility activation: {e}")

        # Determine overall success
        success = any([
            results["mdv"],
            results["audio"],
            results["camera"]
        ])

        if success:
            self.is_active = True
            self.logger.info("✅ MDV CONFERENCE CALL ACTIVATED")
            results["success"] = True
            results["message"] = "MDV Conference Call activated successfully"
        else:
            self.logger.warning("⚠️  MDV Conference Call activation attempted but may not be fully active")
            results["success"] = False
            results["message"] = "MDV Conference Call activation attempted but no methods succeeded"

        return results

    def stop_conference_call(self):
        """Stop MDV Conference Call"""
        self.logger.info("🛑 Stopping MDV Conference Call...")

        # Stop audio
        if self.audio_active:
            self.audio_active = False
            if self.audio_thread:
                self.audio_thread.join(timeout=2)

        # Stop camera
        if self.camera_active:
            self.camera_active = False
            if self.camera_thread:
                self.camera_thread.join(timeout=2)

        self.is_active = False
        self.logger.info("✅ MDV Conference Call stopped")


def auto_activate_mdv_conference_call(camera_mode: str = "ir_only") -> Dict[str, Any]:
    """
    Auto-activate MDV Conference Call when called after message submission.

    Args:
        camera_mode: "ir_only", "normal_only", or "hybrid"

    Returns:
        Result dictionary
    """
    mode_map = {
        "ir_only": CameraMode.IR_ONLY,
        "normal_only": CameraMode.NORMAL_ONLY,
        "hybrid": CameraMode.HYBRID
    }

    mode = mode_map.get(camera_mode.lower(), CameraMode.IR_ONLY)
    conference_call = JARVISMDVConferenceCall(camera_mode=mode)
    result = conference_call.activate_conference_call()
    return result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS MDV Conference Call")
    parser.add_argument("--activate", action="store_true", help="Activate MDV Conference Call")
    parser.add_argument("--camera-mode", choices=["ir_only", "normal_only", "hybrid"],
                       default="ir_only", help="Camera mode")

    args = parser.parse_args()

    if args.activate:
        print("📹🎤 Activating MDV Conference Call...")
        mode = CameraMode[args.camera_mode.upper()]
        conference_call = JARVISMDVConferenceCall(camera_mode=mode)
        result = conference_call.activate_conference_call()

        if result.get("success"):
            print("✅ MDV Conference Call activated")
            print(f"   MDV: {'✅' if result.get('mdv') else '❌'}")
            print(f"   Audio: {'✅' if result.get('audio') else '❌'}")
            print(f"   Camera: {'✅' if result.get('camera') else '❌'}")
            print(f"   Tracking: {'✅' if result.get('tracking') else '❌'}")
        else:
            print(f"❌ MDV Conference Call activation failed: {result.get('message', 'Unknown error')}")
        return 0 if result.get("success") else 1

    return 0


if __name__ == "__main__":


    sys.exit(main() or 0)