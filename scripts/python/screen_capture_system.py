#!/usr/bin/env python3
"""
Screen Capture System - Like OpenAI Atlas Operator

Captures screen/video to monitor what's actually happening.
Stores videos on NAS drive (V:) instead of C: drive.

Tags: #SCREEN_CAPTURE #ATLAS #VIDEO #NAS #MONITORING @JARVIS @LUMINA
"""

import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from drive_mapping_system import DriveMappingSystem
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Try to import screen capture libraries
try:
    import cv2
    import mss
    import numpy as np
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    SCREEN_CAPTURE_AVAILABLE = False
    mss = None
    np = None
    cv2 = None

logger = get_logger("ScreenCapture")


class ScreenCaptureSystem:
    """
    Screen Capture System - Like OpenAI Atlas Operator

    Features:
    - Screen recording
    - Video storage on NAS (V: drive)
    - Real-time monitoring
    - Intent detection from screen
    """

    def __init__(self):
        """Initialize screen capture system"""
        self.drive_mapping = DriveMappingSystem()

        # Get video storage path (NAS drive) - MUST use NAS, no local fallback
        self.video_storage_path = self.drive_mapping.get_video_storage_path()
        try:
            self.video_storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Using NAS storage: {self.video_storage_path}")
        except Exception as e:
            logger.error(f"❌ CRITICAL: Could not access NAS storage: {e}")
            logger.error("   Local storage is at CRITICAL utilization - NAS access required!")
            raise RuntimeError(f"Cannot proceed without NAS storage access: {e}")

        # Recording state
        self.recording = False
        self.current_recording_path: Optional[Path] = None
        self.video_writer: Optional[Any] = None
        self.recording_thread: Optional[threading.Thread] = None
        self.fps = 10  # Frames per second for recording

        logger.info("=" * 80)
        logger.info("📹 SCREEN CAPTURE SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   Video Storage: {self.video_storage_path}")
        logger.info(f"   Screen Capture Available: {SCREEN_CAPTURE_AVAILABLE}")
        logger.info("=" * 80)

    def start_recording(self, session_name: Optional[str] = None) -> Path:
        """Start screen recording"""
        if self.recording:
            logger.warning("Recording already in progress")
            return self.current_recording_path or Path()

        if not SCREEN_CAPTURE_AVAILABLE:
            logger.error("Screen capture libraries not available. Install: pip install --user mss opencv-python")
            return Path()

        # Generate filename
        if not session_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"screen_capture_{timestamp}"

        video_file = self.video_storage_path / f"{session_name}.mp4"

        try:
            # Get screen dimensions
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                width = monitor["width"]
                height = monitor["height"]

            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                str(video_file),
                fourcc,
                self.fps,
                (width, height)
            )

            if not self.video_writer.isOpened():
                logger.error(f"Failed to open video writer for {video_file}")
                return Path()

            self.recording = True
            self.current_recording_path = video_file

            # Start recording thread
            self.recording_thread = threading.Thread(target=self._record_frames, daemon=True)
            self.recording_thread.start()

            logger.info(f"📹 Started recording: {video_file}")
            return video_file
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            return Path()

    def _record_frames(self):
        """Record frames in background thread"""
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            frame_time = 1.0 / self.fps

            while self.recording:
                try:
                    # Capture screen
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot)
                    # Convert BGRA to BGR for OpenCV
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    # Write frame
                    if self.video_writer:
                        self.video_writer.write(frame)

                    time.sleep(frame_time)
                except Exception as e:
                    logger.error(f"Error recording frame: {e}")
                    break

        # Release video writer
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

    def stop_recording(self) -> Optional[Path]:
        try:
            """Stop screen recording"""
            if not self.recording:
                logger.warning("No recording in progress")
                return None

            self.recording = False

            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=2.0)

            video_file = self.current_recording_path
            self.current_recording_path = None

            if video_file and video_file.exists():
                logger.info(f"📹 Stopped recording: {video_file} ({video_file.stat().st_size} bytes)")
            else:
                logger.warning(f"📹 Stopped recording but file not found: {video_file}")

            return video_file

        except Exception as e:
            self.logger.error(f"Error in stop_recording: {e}", exc_info=True)
            raise
    def capture_screenshot(self, filename: Optional[str] = None) -> Path:
        """Capture single screenshot"""
        if not SCREEN_CAPTURE_AVAILABLE:
            logger.error("Screen capture libraries not available. Install: pip install --user mss opencv-python")
            return Path()

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        screenshot_path = self.video_storage_path / filename

        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = sct.grab(monitor)

                # Convert to PIL Image and save
                from PIL import Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                img.save(str(screenshot_path))

            if screenshot_path.exists():
                logger.info(f"📸 Captured screenshot: {screenshot_path} ({screenshot_path.stat().st_size} bytes)")
            else:
                logger.warning(f"📸 Screenshot file not created: {screenshot_path}")
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return Path()

        return screenshot_path

    def get_storage_info(self) -> Dict[str, Any]:
        """Get video storage information"""
        storage_type = "NAS"
        if str(self.video_storage_path).startswith("V:") or "\\\\NAS" in str(self.video_storage_path):
            storage_type = "NAS (V: drive / \\\\NAS\\video)"
        elif str(self.video_storage_path).startswith("P:") or "pictures" in str(self.video_storage_path).lower():
            storage_type = "NAS (P: drive / \\\\NAS\\pictures)"

        info = {
            "storage_path": str(self.video_storage_path),
            "storage_type": storage_type,
            "recording": self.recording,
            "current_recording": str(self.current_recording_path) if self.current_recording_path else None
        }

        # Check storage space if available
        try:
            if self.video_storage_path.exists():
                # Count files
                video_files = list(self.video_storage_path.glob("*.mp4"))
                screenshot_files = list(self.video_storage_path.glob("*.png"))
                info["video_count"] = len(video_files)
                info["screenshot_count"] = len(screenshot_files)
        except Exception:
            pass

        return info


def main():
    """Main function"""
    print("=" * 80)
    print("📹 SCREEN CAPTURE SYSTEM")
    print("=" * 80)
    print()

    capture = ScreenCaptureSystem()

    # Show storage info
    info = capture.get_storage_info()
    print("Video Storage:")
    print(f"  Path: {info['storage_path']}")
    print(f"  Type: {info['storage_type']}")
    print(f"  Recording: {info['recording']}")
    print()

    print("=" * 80)
    print("✅ SCREEN CAPTURE SYSTEM READY")
    print("=" * 80)
    print()
    print("Note: Actual screen capture implementation requires:")
    print("  • mss or PIL for screenshots")
    print("  • opencv or ffmpeg for video recording")
    print("  • Video files will be stored on NAS (V: drive)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()