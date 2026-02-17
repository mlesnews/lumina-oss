#!/usr/bin/env python3
"""
JARVIS Auto MDV Activator

Automatically activates MANUS Desktop Videofeed (MDV) after message submission.
This ensures the AI can always "see" the output to respond better.

Tags: #JARVIS #MDV #MANUS #DESKTOP_VIDEOFEED #AUTO_ACTIVATE @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAutoMDVActivator")


class JARVISAutoMDVActivator:
    """
    Automatically activates MANUS Desktop Videofeed (MDV) after message submission.

    This ensures the AI can always "see" the output to respond better.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Auto MDV Activator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger
        self.mdv_active = False

        # Import MANUS systems
        self.rdp_capture = None
        self.unified_control = None
        self.vision_control = None

        self._initialize_manus_systems()

        self.logger.info("✅ JARVIS Auto MDV Activator initialized")

    def _initialize_manus_systems(self):
        """Initialize MANUS systems for MDV"""
        try:
            from manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture
            self.rdp_capture = MANUSRDPScreenshotCapture()
            self.logger.info("✅ MANUS RDP Screenshot Capture initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️  MANUS RDP Screenshot Capture not available: {e}")

        try:
            from manus_unified_control import MANUSUnifiedControl, ControlOperation, ControlArea
            self.unified_control = MANUSUnifiedControl(self.project_root)
            self.logger.info("✅ MANUS Unified Control initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️  MANUS Unified Control not available: {e}")

        try:
            from manus_cursor_vision_control import ManusCursorVisionControl
            self.vision_control = ManusCursorVisionControl()
            self.logger.info("✅ MANUS Cursor Vision Control initialized")
        except ImportError as e:
            self.logger.debug(f"MANUS Cursor Vision Control not available: {e}")

    def activate_mdv(self) -> Dict[str, Any]:
        """
        Activate MANUS Desktop Videofeed (MDV)

        This starts the video feed so the AI can "see" the output.

        Returns:
            Result dictionary
        """
        self.logger.info("=" * 80)
        self.logger.info("📹 ACTIVATING MANUS DESKTOP VIDEOFEED (MDV)")
        self.logger.info("=" * 80)

        results = {
            "screenshot_capture": False,
            "video_recording": False,
            "vision_control": False,
            "timestamp": datetime.now().isoformat()
        }

        # Method 1: Start continuous screenshot capture (primary method)
        if self.rdp_capture:
            try:
                self.logger.info("📸 Starting continuous screenshot capture...")
                # Capture initial screenshot to establish feed
                screenshot_path = self.rdp_capture.capture_screenshot()
                if screenshot_path:
                    results["screenshot_capture"] = True
                    results["screenshot_path"] = str(screenshot_path)
                    self.logger.info(f"✅ Initial screenshot captured: {screenshot_path}")
                else:
                    self.logger.warning("⚠️  Screenshot capture returned None")
            except Exception as e:
                self.logger.error(f"❌ Screenshot capture failed: {e}")
                results["screenshot_error"] = str(e)

        # Method 2: Start video recording (if available)
        if self.unified_control:
            try:
                self.logger.info("🎥 Attempting to start video recording...")
                video_op = ControlOperation(
                    operation_id=f"mdv_video_{int(time.time())}",
                    area=ControlArea.RDP_CAPTURE,
                    action="start_video",
                    parameters={"filename": f"mdv_feed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"}
                )
                video_result = self.unified_control.execute_operation(video_op)
                if video_result.success:
                    results["video_recording"] = True
                    results["video_path"] = video_result.data.get("video_path")
                    self.logger.info(f"✅ Video recording started: {video_result.data.get('video_path')}")
                else:
                    self.logger.warning(f"⚠️  Video recording not available: {video_result.message}")
            except Exception as e:
                self.logger.debug(f"Video recording not available: {e}")

        # Method 3: Activate vision control (extrapolate desktop area)
        if self.vision_control:
            try:
                self.logger.info("🔍 Activating vision control (extrapolating desktop area)...")
                desktop_state = self.vision_control.extrapolate_desktop_area()
                if desktop_state:
                    results["vision_control"] = True
                    results["desktop_state"] = desktop_state
                    self.logger.info("✅ Vision control activated - desktop area extrapolated")
            except Exception as e:
                self.logger.debug(f"Vision control not available: {e}")

        # Determine overall success
        success = any([
            results["screenshot_capture"],
            results["video_recording"],
            results["vision_control"]
        ])

        if success:
            self.mdv_active = True
            self.logger.info("✅ MDV ACTIVATED - AI can now 'see' the output")
            results["success"] = True
            results["message"] = "MDV activated successfully"
        else:
            self.logger.warning("⚠️  MDV activation attempted but may not be fully active")
            results["success"] = False
            results["message"] = "MDV activation attempted but no methods succeeded"

        return results

    def ensure_mdv_active(self) -> Dict[str, Any]:
        """
        Ensure MDV is active, activate if not

        Returns:
            Status dictionary
        """
        if self.mdv_active:
            return {
                "active": True,
                "message": "MDV already active",
                "timestamp": datetime.now().isoformat()
            }

        return self.activate_mdv()

    def capture_current_view(self) -> Optional[Path]:
        """
        Capture current view (screenshot) for immediate context

        Returns:
            Path to screenshot or None
        """
        if not self.rdp_capture:
            self.logger.warning("⚠️  RDP capture not available")
            return None

        try:
            screenshot_path = self.rdp_capture.capture_screenshot()
            if screenshot_path:
                self.logger.info(f"📸 Current view captured: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            self.logger.error(f"❌ Failed to capture current view: {e}")
            return None


def auto_activate_mdv_on_submit(conference_call_mode: bool = False, camera_mode: str = "ir_only"):
    """
    Auto-activate MDV when called after message submission.

    This is the main entry point for automatic MDV activation.

    Args:
        conference_call_mode: If True, activate full MDV Conference Call (with audio & camera)
        camera_mode: Camera mode for conference call ("ir_only", "normal_only", "hybrid")

    Returns:
        Result dictionary
    """
    if conference_call_mode:
        # Use enhanced MDV Conference Call mode
        try:
            from jarvis_mdv_conference_call import auto_activate_mdv_conference_call
            result = auto_activate_mdv_conference_call(camera_mode=camera_mode)
            return result
        except ImportError:
            logger.warning("⚠️  MDV Conference Call not available, falling back to basic MDV")
            # Fall through to basic MDV

    # Basic MDV mode
    activator = JARVISAutoMDVActivator()
    result = activator.activate_mdv()
    return result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Auto MDV Activator")
    parser.add_argument("--activate", action="store_true", help="Activate MDV")
    parser.add_argument("--capture", action="store_true", help="Capture current view")
    parser.add_argument("--status", action="store_true", help="Check MDV status")

    args = parser.parse_args()

    activator = JARVISAutoMDVActivator()

    if args.capture:
        print("📸 Capturing current view...")
        screenshot_path = activator.capture_current_view()
        if screenshot_path:
            print(f"✅ Screenshot saved: {screenshot_path}")
        else:
            print("❌ Screenshot capture failed")
        return 0

    if args.status:
        status = activator.ensure_mdv_active()
        print(f"MDV Status: {'✅ Active' if status.get('active') else '❌ Inactive'}")
        return 0

    if args.activate or not any([args.capture, args.status]):
        print("📹 Activating MDV...")
        result = activator.activate_mdv()
        if result.get("success"):
            print("✅ MDV activated successfully")
            print(f"   Screenshot: {result.get('screenshot_path', 'N/A')}")
            print(f"   Video: {result.get('video_path', 'N/A')}")
            print(f"   Vision Control: {'✅' if result.get('vision_control') else '❌'}")
        else:
            print(f"❌ MDV activation failed: {result.get('message', 'Unknown error')}")
        return 0 if result.get("success") else 1

    return 0


if __name__ == "__main__":


    sys.exit(main() or 0)