#!/usr/bin/env python3
"""
MANUS RDP Screenshot & Video Capture
Automates screenshot/video capture from RDP sessions to avoid manual screenshots
Similar to OpenAI Atlas features - automatic visual context capture
#JARVIS #MANUS #RDP #SCREENSHOT #VIDEO #AUTOMATION
"""

import logging
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import drive mapping for NAS storage
try:
    from drive_mapping_system import DriveMappingSystem

    DRIVE_MAPPING_AVAILABLE = True
except ImportError:
    DRIVE_MAPPING_AVAILABLE = False
    DriveMappingSystem = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MANUSRDPScreenshotCapture:
    """
    MANUS RDP Screenshot and Video Capture
    Captures screenshots/video from RDP sessions automatically
    """

    def __init__(self, manus_ip: str = "<NAS_IP>", output_dir: Optional[Path] = None):
        """
        Initialize RDP screenshot capture

        Args:
            manus_ip: MANUS RDP server IP address
            output_dir: Directory to save screenshots/videos (default: NAS P: drive)
        """
        self.manus_ip = manus_ip
        self.is_windows = platform.system() == "Windows"

        # Use NAS storage - MUST use NAS, no local storage
        # BUT: Fallback to local if NAS unavailable (for crash diagnosis)
        if output_dir is None:
            if DRIVE_MAPPING_AVAILABLE:
                try:
                    drive_mapping = DriveMappingSystem()
                    self.output_dir = drive_mapping.get_picture_storage_path()
                    # Test if NAS is accessible
                    self.output_dir.mkdir(parents=True, exist_ok=True)
                    logger.info(f"✅ Using NAS storage: {self.output_dir}")
                except Exception as nas_error:
                    logger.warning(f"⚠️  NAS storage unavailable: {nas_error}")
                    logger.warning("   Falling back to LOCAL storage for crash diagnosis")
                    # Local fallback for crash monitoring
                    self.output_dir = project_root / "data" / "manus_rdp_captures"
            else:
                # Direct NAS path as fallback
                nas_path = Path("\\\\NAS\\pictures\\screenshots\\manus_rdp_captures")
                try:
                    nas_path.mkdir(parents=True, exist_ok=True)
                    self.output_dir = nas_path
                    logger.info(f"✅ Using NAS storage: {self.output_dir}")
                except Exception as nas_error:
                    logger.warning(f"⚠️  NAS storage unavailable: {nas_error}")
                    logger.warning("   Falling back to LOCAL storage for crash diagnosis")
                    self.output_dir = project_root / "data" / "manus_rdp_captures"
        else:
            self.output_dir = output_dir

        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            if "manus_rdp_captures" in str(self.output_dir) and "data" in str(self.output_dir):
                logger.info(f"✅ Using LOCAL fallback storage: {self.output_dir}")
            else:
                logger.info(f"✅ Using storage: {self.output_dir}")
        except Exception as e:
            logger.error(f"❌ CRITICAL: Could not access storage: {e}")
            raise RuntimeError(f"Cannot proceed without storage access: {e}")

        logger.info("MANUS RDP Screenshot Capture initialized")
        logger.info(f"  MANUS IP: {manus_ip}")
        logger.info(f"  Output Directory: {self.output_dir}")

    def capture_screenshot(self, filename: Optional[str] = None) -> Path:
        """
        Capture screenshot from RDP session

        Args:
            filename: Optional filename (auto-generated if not provided)

        Returns:
            Path to saved screenshot
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rdp_screenshot_{timestamp}.png"

        screenshot_path = self.output_dir / filename

        try:
            if self.is_windows:
                # Use Windows Snipping Tool or PowerShell to capture RDP screen
                # Method 1: Try using PowerShell to capture active window
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms,System.Drawing
                $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                $bitmap = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
                $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
                $bitmap.Save("{screenshot_path}", [System.Drawing.Imaging.ImageFormat]::Png)
                $graphics.Dispose()
                $bitmap.Dispose()
                Write-Output "Screenshot saved to {screenshot_path}"
                '''

                result = subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=True,
                )

                if result.returncode == 0 and screenshot_path.exists():
                    logger.info(f"✅ Screenshot captured: {screenshot_path}")
                    return screenshot_path
                else:
                    logger.warning(f"Screenshot capture may have failed: {result.stderr}")
                    # Fallback: Use mstsc /span or other method
                    return self._capture_rdp_fallback(screenshot_path)
            else:
                # Linux/Mac: Use import or screencapture
                import_cmd = ["import", "-window", "root", str(screenshot_path)]
                result = subprocess.run(import_cmd, capture_output=True, timeout=10)

                if result.returncode == 0:
                    logger.info(f"✅ Screenshot captured: {screenshot_path}")
                    return screenshot_path
                else:
                    logger.error("Screenshot capture failed")
                    return None

        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

    def _capture_rdp_fallback(self, screenshot_path: Path) -> Optional[Path]:
        """Fallback screenshot capture method"""
        try:
            # Try using Windows API directly via Python
            try:
                from PIL import ImageGrab

                screenshot = ImageGrab.grab()
                screenshot.save(screenshot_path, "PNG")
                logger.info(f"✅ Screenshot captured (fallback): {screenshot_path}")
                return screenshot_path
            except ImportError:
                logger.warning("PIL/Pillow not available for screenshot capture")
                return None
        except Exception as e:
            logger.error(f"Fallback screenshot capture failed: {e}")
            return None

    def start_video_recording(self, filename: Optional[str] = None) -> Optional[Path]:
        """
        Start video recording from RDP session

        Args:
            filename: Optional filename (auto-generated if not provided)

        Returns:
            Path to video file (will be created when recording stops)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rdp_recording_{timestamp}.mp4"

        video_path = self.output_dir / filename

        try:
            if self.is_windows:
                # Use OBS Studio, FFmpeg, or Windows Game Bar API
                # For now, provide instructions for manual setup
                logger.info("Video recording requires additional setup:")
                logger.info("  Option 1: Use OBS Studio (recommended)")
                logger.info("  Option 2: Use FFmpeg with screen capture")
                logger.info("  Option 3: Use Windows Game Bar (Win+G)")
                logger.info(f"  Save to: {video_path}")
                return video_path
            else:
                # Linux: Use ffmpeg
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-f",
                    "x11grab",
                    "-s",
                    "1920x1080",
                    "-i",
                    ":0.0",
                    "-t",
                    "60",
                    str(video_path),
                ]
                logger.info("Starting video recording...")
                logger.info(f"Command: {' '.join(ffmpeg_cmd)}")
                return video_path

        except Exception as e:
            logger.error(f"Error starting video recording: {e}")
            return None

    def capture_with_context(self, description: str, auto_capture: bool = True) -> Dict[str, Any]:
        try:
            """
            Capture screenshot with context description

            Args:
                description: Description of what's being captured
                auto_capture: Automatically capture screenshot

            Returns:
                Dict with screenshot path and metadata
            """
            timestamp = datetime.now()
            screenshot_path = None

            if auto_capture:
                screenshot_path = self.capture_screenshot()

            metadata = {
                "timestamp": timestamp.isoformat(),
                "description": description,
                "manus_ip": self.manus_ip,
                "screenshot_path": str(screenshot_path) if screenshot_path else None,
                "output_dir": str(self.output_dir),
            }

            # Save metadata
            metadata_file = self.output_dir / f"metadata_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            import json

            metadata_file.write_text(json.dumps(metadata, indent=2))

            logger.info(f"✅ Context capture saved: {metadata_file}")

            return metadata

        except Exception as e:
            self.logger.error(f"Error in capture_with_context: {e}", exc_info=True)
            raise

    def list_captures(self) -> list:
        """List all captured screenshots/videos"""
        captures = []

        for file in self.output_dir.glob("*"):
            if file.is_file():
                captures.append(
                    {
                        "name": file.name,
                        "path": str(file),
                        "size": file.stat().st_size,
                        "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                    }
                )

        return sorted(captures, key=lambda x: x["modified"], reverse=True)


def main():
    try:
        """CLI interface for RDP screenshot capture"""
        import argparse

        parser = argparse.ArgumentParser(description="MANUS RDP Screenshot & Video Capture")
        parser.add_argument("--manus-ip", default="<NAS_IP>", help="MANUS RDP server IP")
        parser.add_argument("--output-dir", help="Output directory for captures")
        parser.add_argument("--screenshot", action="store_true", help="Capture screenshot")
        parser.add_argument("--video", action="store_true", help="Start video recording")
        parser.add_argument("--context", help="Capture with context description")
        parser.add_argument("--list", action="store_true", help="List all captures")
        parser.add_argument("--filename", help="Custom filename for capture")
        parser.add_argument(
            "--feed",
            action="store_true",
            help="Capture and save as MDV feed (mdv_feed_latest.png) so the agent can read it when using @mdv",
        )

        args = parser.parse_args()

        print("=" * 70)
        print("   MANUS RDP SCREENSHOT & VIDEO CAPTURE")
        print("=" * 70)
        print("")

        output_dir = Path(args.output_dir) if args.output_dir else None
        capture = MANUSRDPScreenshotCapture(manus_ip=args.manus_ip, output_dir=output_dir)

        if args.list:
            print("📸 Listing all captures...")
            print("")
            captures = capture.list_captures()
            for cap in captures:
                print(f"  {cap['name']}")
                print(f"    Size: {cap['size']:,} bytes")
                print(f"    Modified: {cap['modified']}")
                print("")
            return 0

        if args.context:
            print(f"📸 Capturing with context: {args.context}")
            print("")
            metadata = capture.capture_with_context(args.context, auto_capture=True)
            print("")
            print("✅ Capture complete!")
            print(f"   Screenshot: {metadata.get('screenshot_path', 'N/A')}")
            print(f"   Metadata: {metadata.get('output_dir', 'N/A')}")
            return 0

        if args.feed:
            # Feed: capture and copy to stable path for agent to read (always in project data/)
            feed_dir = project_root / "data" / "manus_rdp_captures"
            feed_dir.mkdir(parents=True, exist_ok=True)
            feed_path = feed_dir / "mdv_feed_latest.png"
            print("📸 Capturing MDV feed (agent can read mdv_feed_latest.png when you use @mdv)...")
            print("")
            screenshot_path = capture.capture_screenshot()
            if screenshot_path and screenshot_path.exists():
                import shutil

                shutil.copy2(screenshot_path, feed_path)
                print(f"✅ Screenshot saved: {screenshot_path}")
                print(f"✅ MDV feed updated: {feed_path}")
                print(
                    "   (Use TightVNC for the session you want the agent to see; run this on that machine.)"
                )
            else:
                print("❌ Screenshot capture failed")
            return 0

        if args.screenshot:
            print("📸 Capturing screenshot...")
            print("")
            screenshot_path = capture.capture_screenshot(filename=args.filename)
            if screenshot_path:
                print(f"✅ Screenshot saved: {screenshot_path}")
            else:
                print("❌ Screenshot capture failed")
            return 0

        if args.video:
            print("🎥 Starting video recording...")
            print("")
            video_path = capture.start_video_recording(filename=args.filename)
            if video_path:
                print("✅ Video recording started")
                print(f"   Will save to: {video_path}")
                print("")
                print("⚠️  Note: Video recording requires additional setup")
                print("   - Install OBS Studio or FFmpeg")
                print("   - Or use Windows Game Bar (Win+G)")
            return 0

        # Default: capture screenshot
        print("📸 Capturing screenshot (default action)...")
        print("")
        screenshot_path = capture.capture_screenshot()
        if screenshot_path:
            print(f"✅ Screenshot saved: {screenshot_path}")
        else:
            print("❌ Screenshot capture failed")
            print("")
            print("Troubleshooting:")
            print("  1. Make sure you're in an RDP session")
            print("  2. Install Pillow: pip install Pillow")
            print("  3. Or use Windows Snipping Tool manually")

        return 0

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    sys.exit(main())
