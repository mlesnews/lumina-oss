#!/usr/bin/env python3
"""
ACVA Frame-by-Frame Video Capture with SYPHON Integration

Re-SYPHONing and refactoring/repurposing the ASUS Armoury Crate Virtual Assistant (ACVA).
Captures video "snapshots" of all frames, similar to OpenAI Atlas/Operator method.

How Atlas/Operator Does It:
1. Captures screenshots at regular intervals (frame-by-frame)
2. Processes each frame for visual context
3. Extracts intelligence from visual data
4. Builds understanding from frame sequences

Tags: #ACVA #FRAME_CAPTURE #VIDEO #SYPHON #ATLAS #OPERATOR #REFACTOR @JARVIS @TEAM
"""

import sys
import time
import ctypes
from ctypes import wintypes
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ACVAFrameCaptureSyphon")

# Try PIL for image processing
try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL/Pillow not available - install: pip install Pillow")

# Try mss for faster screenshots
try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    logger.warning("mss not available - install: pip install mss (faster screenshots)")


class ACVAFrameCaptureSyphon:
    """
    ACVA Frame-by-Frame Video Capture with SYPHON Integration

    Re-SYPHONing and refactoring/repurposing ACVA by capturing all frames
    and extracting intelligence via SYPHON.

    Similar to OpenAI Atlas/Operator frame capture method.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ACVA frame capture system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "acva_frame_capture"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.frames_dir = self.data_dir / "frames"
        self.frames_dir.mkdir(parents=True, exist_ok=True)

        self.syphon_dir = self.project_root / "data" / "syphon" / "acva_frames"
        self.syphon_dir.mkdir(parents=True, exist_ok=True)

        # Windows API for window capture
        if sys.platform == "win32":
            self.user32 = ctypes.windll.user32
            self.gdi32 = ctypes.windll.gdi32
        else:
            self.user32 = None
            self.gdi32 = None

        # ACVA window handle
        self.acva_hwnd = None
        self.acva_window_rect = None

        # Frame capture settings
        self.fps = 30  # Frames per second (Atlas typically uses 1-5 fps for efficiency)
        self.frame_interval = 1.0 / self.fps

        # SYPHON integration
        self.syphon_enabled = True

        logger.info("✅ ACVA Frame Capture SYPHON initialized")
        logger.info("   Re-SYPHONing and refactoring ACVA via frame-by-frame capture")
        logger.info("   Method: Similar to OpenAI Atlas/Operator")

    def find_acva_window(self) -> Optional[int]:
        """Find ACVA window (ASUSMascot)"""
        if not self.user32:
            logger.error("❌ Windows API not available")
            return None

        logger.info("🔍 Finding ACVA window...")

        # Search by process name first (more reliable)
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                proc_name = proc.info.get('name', '').lower()
                if 'virtual pet.exe' in proc_name or 'virtualpet.exe' in proc_name:
                    pid = proc.info['pid']

                    # Find windows for this process
                    windows_found = []

                    def enum_callback(hwnd, lParam):
                        process_id = wintypes.DWORD()
                        self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
                        if process_id.value == pid and self.user32.IsWindowVisible(hwnd):
                            buffer = ctypes.create_unicode_buffer(512)
                            self.user32.GetWindowTextW(hwnd, buffer, 512)
                            title = buffer.value
                            if title:
                                windows_found.append((hwnd, title))
                        return True

                    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
                    self.user32.EnumWindows(EnumWindowsProc(enum_callback), 0)

                    if windows_found:
                        # Prefer "ASUSMascot" window
                        for hwnd, title in windows_found:
                            if 'mascot' in title.lower() or 'asus' in title.lower():
                                self.acva_hwnd = hwnd
                                logger.info(f"✅ Found ACVA window: {title} (HWND: {hwnd})")
                                return hwnd

                        # Use first found window
                        self.acva_hwnd = windows_found[0][0]
                        logger.info(f"✅ Found ACVA window: {windows_found[0][1]} (HWND: {self.acva_hwnd})")
                        return self.acva_hwnd
        except ImportError:
            logger.warning("⚠️  psutil not available - using window title search")

        # Fallback: Search by window title
        def enum_callback(hwnd, lParam):
            if self.user32.IsWindowVisible(hwnd):
                buffer = ctypes.create_unicode_buffer(512)
                self.user32.GetWindowTextW(hwnd, buffer, 512)
                title = buffer.value.lower()
                if 'mascot' in title or 'virtual pet' in title or 'asus' in title:
                    windows_found.append((hwnd, buffer.value))
            return True

        windows_found = []
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        self.user32.EnumWindows(EnumWindowsProc(enum_callback), 0)

        if windows_found:
            self.acva_hwnd = windows_found[0][0]
            logger.info(f"✅ Found ACVA window: {windows_found[0][1]} (HWND: {self.acva_hwnd})")
            return self.acva_hwnd

        logger.warning("⚠️  ACVA window not found")
        return None

    def get_window_rect(self, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """Get window rectangle (x, y, width, height)"""
        if not self.user32:
            return None

        try:
            rect = wintypes.RECT()
            self.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            x = rect.left
            y = rect.top
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            return (x, y, width, height)
        except Exception as e:
            logger.error(f"❌ Error getting window rect: {e}")
            return None

    def capture_window_frame(self, hwnd: int) -> Optional[Image.Image]:
        """Capture a single frame from a specific window"""
        if not PIL_AVAILABLE:
            logger.error("❌ PIL/Pillow not available")
            return None

        # Get window rectangle
        rect = self.get_window_rect(hwnd)
        if not rect:
            return None

        x, y, width, height = rect

        # Capture window region
        try:
            if MSS_AVAILABLE:
                # Use mss for faster capture
                with mss.mss() as sct:
                    monitor = {
                        "top": y,
                        "left": x,
                        "width": width,
                        "height": height
                    }
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            else:
                # Use PIL ImageGrab (slower but works)
                img = ImageGrab.grab(bbox=(x, y, x + width, y + height))

            return img
        except Exception as e:
            logger.error(f"❌ Error capturing frame: {e}")
            return None

    def capture_frame(self, frame_number: int) -> Optional[Dict[str, Any]]:
        """Capture a single frame from ACVA"""
        if not self.acva_hwnd:
            if not self.find_acva_window():
                logger.error("❌ Cannot capture - ACVA window not found")
                return None

        timestamp = datetime.now()
        frame_data = {
            "frame_number": frame_number,
            "timestamp": timestamp.isoformat(),
            "timestamp_unix": timestamp.timestamp(),
            "hwnd": self.acva_hwnd,
            "window_rect": None,
            "frame_path": None,
            "frame_size": None,
            "success": False
        }

        # Get window rect
        rect = self.get_window_rect(self.acva_hwnd)
        if rect:
            frame_data["window_rect"] = {
                "x": rect[0],
                "y": rect[1],
                "width": rect[2],
                "height": rect[3]
            }

        # Capture frame
        img = self.capture_window_frame(self.acva_hwnd)
        if img:
            # Save frame
            frame_filename = f"acva_frame_{frame_number:06d}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.png"
            frame_path = self.frames_dir / frame_filename
            img.save(frame_path, "PNG")

            frame_data["frame_path"] = str(frame_path)
            frame_data["frame_size"] = {"width": img.width, "height": img.height}
            frame_data["success"] = True

            logger.debug(f"   📸 Frame {frame_number} captured: {frame_filename}")
        else:
            logger.warning(f"   ⚠️  Frame {frame_number} capture failed")

        return frame_data

    def capture_video_frames(self, duration_seconds: float = 10.0, fps: Optional[float] = None) -> Dict[str, Any]:
        """
        Capture video frames from ACVA (like Atlas/Operator)

        Args:
            duration_seconds: How long to capture (default: 10 seconds)
            fps: Frames per second (default: self.fps, typically 1-5 for efficiency)
        """
        if fps is None:
            fps = self.fps

        frame_interval = 1.0 / fps
        total_frames = int(duration_seconds * fps)

        logger.info("="*80)
        logger.info("🎬 ACVA Frame-by-Frame Video Capture (Atlas/Operator Method)")
        logger.info("="*80)
        logger.info(f"   Duration: {duration_seconds}s")
        logger.info(f"   FPS: {fps}")
        logger.info(f"   Total Frames: {total_frames}")
        logger.info(f"   Frame Interval: {frame_interval:.3f}s")
        logger.info("")

        if not self.find_acva_window():
            logger.error("❌ Cannot capture - ACVA window not found")
            return {
                "success": False,
                "error": "ACVA window not found",
                "frames_captured": 0
            }

        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration_seconds,
            "fps": fps,
            "total_frames": total_frames,
            "frames_captured": 0,
            "frames": [],
            "frame_metadata": [],
            "syphon_extracted": []
        }

        start_time = time.time()

        logger.info(f"📸 Starting frame capture...")
        logger.info("")

        for frame_num in range(total_frames):
            frame_start = time.time()

            # Capture frame
            frame_data = self.capture_frame(frame_num + 1)
            if frame_data and frame_data.get("success"):
                result["frames"].append(frame_data)
                result["frames_captured"] += 1

                # SYPHON extraction
                if self.syphon_enabled and frame_data.get("frame_path"):
                    syphon_data = self.syphon_extract_frame(frame_data)
                    if syphon_data:
                        result["syphon_extracted"].append(syphon_data)

                logger.info(f"   ✅ Frame {frame_num + 1}/{total_frames} captured")
            else:
                logger.warning(f"   ⚠️  Frame {frame_num + 1}/{total_frames} failed")

            # Wait for next frame (account for capture time)
            elapsed = time.time() - frame_start
            sleep_time = max(0, frame_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

        total_elapsed = time.time() - start_time

        result["actual_duration"] = total_elapsed
        result["actual_fps"] = result["frames_captured"] / total_elapsed if total_elapsed > 0 else 0

        # Save metadata
        metadata_file = self.data_dir / f"acva_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"   ✅ Metadata saved: {metadata_file.name}")
        except Exception as e:
            logger.error(f"❌ Error saving metadata: {e}")

        logger.info("")
        logger.info("="*80)
        logger.info("✅ Frame Capture Complete")
        logger.info(f"   Frames Captured: {result['frames_captured']}/{total_frames}")
        logger.info(f"   Actual Duration: {total_elapsed:.2f}s")
        logger.info(f"   Actual FPS: {result['actual_fps']:.2f}")
        logger.info(f"   SYPHON Extractions: {len(result['syphon_extracted'])}")
        logger.info("="*80)

        return result

    def syphon_extract_frame(self, frame_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract intelligence from frame via SYPHON"""
        if not frame_data.get("frame_path"):
            return None

        frame_path = Path(frame_data["frame_path"])
        if not frame_path.exists():
            return None

        syphon_data = {
            "frame_number": frame_data.get("frame_number"),
            "timestamp": frame_data.get("timestamp"),
            "frame_path": str(frame_path),
            "extraction_timestamp": datetime.now().isoformat(),
            "intelligence": {}
        }

        # Basic frame analysis
        try:
            if PIL_AVAILABLE:
                img = Image.open(frame_path)
                width, height = img.size

                # Get image stats
                pixels = list(img.getdata())
                if pixels:
                    # Calculate basic statistics
                    r_values = [p[0] for p in pixels if isinstance(p, tuple) and len(p) >= 3]
                    g_values = [p[1] for p in pixels if isinstance(p, tuple) and len(p) >= 3]
                    b_values = [p[2] for p in pixels if isinstance(p, tuple) and len(p) >= 3]

                    if r_values:
                        syphon_data["intelligence"] = {
                            "image_size": {"width": width, "height": height},
                            "pixel_count": len(pixels),
                            "color_stats": {
                                "r_avg": sum(r_values) / len(r_values) if r_values else 0,
                                "g_avg": sum(g_values) / len(g_values) if g_values else 0,
                                "b_avg": sum(b_values) / len(b_values) if b_values else 0,
                            },
                            "analysis": "Basic frame statistics extracted"
                        }
        except Exception as e:
            logger.warning(f"⚠️  SYPHON extraction error: {e}")
            syphon_data["intelligence"]["error"] = str(e)

        # Save SYPHON data
        syphon_file = self.syphon_dir / f"syphon_frame_{frame_data.get('frame_number', 0):06d}.json"
        try:
            with open(syphon_file, 'w', encoding='utf-8') as f:
                json.dump(syphon_data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"⚠️  Error saving SYPHON data: {e}")

        return syphon_data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ACVA Frame-by-Frame Video Capture with SYPHON")
    parser.add_argument("--duration", type=float, default=10.0, help="Capture duration in seconds (default: 10.0)")
    parser.add_argument("--fps", type=float, default=5.0, help="Frames per second (default: 5.0, Atlas-style)")
    parser.add_argument("--find", action="store_true", help="Find ACVA window only")
    parser.add_argument("--single", action="store_true", help="Capture single frame")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🎬 ACVA Frame-by-Frame Video Capture with SYPHON")
    print("   Re-SYPHONing and Refactoring ACVA (Atlas/Operator Method)")
    print("="*80 + "\n")

    capture = ACVAFrameCaptureSyphon()

    if args.find:
        hwnd = capture.find_acva_window()
        if hwnd:
            rect = capture.get_window_rect(hwnd)
            if rect:
                print(f"\n✅ ACVA Window Found:")
                print(f"   HWND: {hwnd}")
                print(f"   Position: ({rect[0]}, {rect[1]})")
                print(f"   Size: {rect[2]}x{rect[3]}")
                print()
        else:
            print("\n❌ ACVA window not found")
            print()

    elif args.single:
        if capture.find_acva_window():
            frame_data = capture.capture_frame(1)
            if frame_data and frame_data.get("success"):
                print(f"\n✅ Single frame captured:")
                print(f"   Frame: {frame_data.get('frame_path')}")
                print(f"   Size: {frame_data.get('frame_size')}")
                print()
            else:
                print("\n❌ Frame capture failed")
                print()
        else:
            print("\n❌ ACVA window not found")
            print()

    else:
        # Full video capture
        result = capture.capture_video_frames(duration_seconds=args.duration, fps=args.fps)

        print("\n" + "="*80)
        print("📊 CAPTURE RESULTS")
        print("="*80)
        print(f"Frames Captured: {result.get('frames_captured', 0)}/{result.get('total_frames', 0)}")
        print(f"Actual Duration: {result.get('actual_duration', 0):.2f}s")
        print(f"Actual FPS: {result.get('actual_fps', 0):.2f}")
        print(f"SYPHON Extractions: {len(result.get('syphon_extracted', []))}")
        print()
        if result.get('frames'):
            print("📸 Frame Files:")
            for i, frame in enumerate(result['frames'][:5], 1):  # Show first 5
                print(f"   {i}. {Path(frame.get('frame_path', '')).name}")
            if len(result['frames']) > 5:
                print(f"   ... and {len(result['frames']) - 5} more")
            print()
        print("="*80 + "\n")
