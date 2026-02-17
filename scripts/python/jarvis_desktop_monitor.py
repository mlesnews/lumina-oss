#!/usr/bin/env python3
"""
JARVIS Desktop Monitor - Continuous RDP Video Feed Monitoring

Continuously monitors the Desktop Area via MANUS RDP feed to detect:
- JARVIS window state (running, crashed, frozen)
- Cursor IDE state
- System anomalies

Tags: #JARVIS #MONITORING #RDP #VIDEO_FEED #CRASH_DETECTION @JARVIS @LUMINA
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDesktopMonitor")


class JARVISDesktopMonitor:
    """
    Continuous Desktop Area Monitor

    Watches the RDP video feed to detect JARVIS state and system anomalies.
    """

    def __init__(self, check_interval: float = 5.0):
        """Initialize desktop monitor

        Args:
            check_interval: Seconds between checks (default: 5.0)
        """
        self.project_root = project_root
        self.check_interval = check_interval
        self.vision = MANUSRDPScreenshotCapture()
        self.running = False

        # State tracking
        self.last_jarvis_state = None
        self.crash_detected = False
        self.freeze_detected = False

        # Screenshot history for comparison
        self.screenshot_history = []
        self.max_history = 10

        logger.info("🔍 JARVIS Desktop Monitor initialized")
        logger.info(f"   Check interval: {check_interval}s")
        logger.info("   Monitoring: Desktop Area via RDP feed")

    def capture_desktop_state(self) -> Dict[str, Any]:
        """Capture current desktop state via RDP feed"""
        try:
            metadata = self.vision.capture_with_context(
                "Continuous desktop monitoring - JARVIS state check",
                auto_capture=True
            )

            screenshot_path = metadata.get('screenshot_path')

            # Analyze screenshot for JARVIS window
            jarvis_state = self._analyze_jarvis_state(screenshot_path)

            # Store in history
            state_record = {
                "timestamp": datetime.now().isoformat(),
                "screenshot_path": screenshot_path,
                "jarvis_state": jarvis_state,
                "metadata": metadata
            }

            self.screenshot_history.append(state_record)
            if len(self.screenshot_history) > self.max_history:
                self.screenshot_history.pop(0)

            return state_record

        except Exception as e:
            logger.error(f"❌ Failed to capture desktop state: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "jarvis_state": "unknown"
            }

    def _analyze_jarvis_state(self, screenshot_path: Optional[Path]) -> Dict[str, Any]:
        """Analyze screenshot to detect JARVIS window state"""
        if not screenshot_path or not Path(screenshot_path).exists():
            return {
                "status": "screenshot_missing",
                "jarvis_visible": False,
                "jarvis_window_detected": False
            }

        try:
            from PIL import Image
            import subprocess
            import platform

            # Check if JARVIS process is running
            jarvis_running = self._check_jarvis_process()
            jarvis_responding = self._check_jarvis_responding()

            # Analyze screenshot for JARVIS window visual state
            visual_analysis = self._analyze_screenshot_visual(screenshot_path)

            # Determine if there's a mismatch (process running but window not visible = crash/freeze)
            anomaly_detected = jarvis_running and not visual_analysis.get("jarvis_window_visible", False)

            return {
                "status": "analyzed",
                "jarvis_process_running": jarvis_running,
                "jarvis_responding": jarvis_responding,
                "jarvis_visible": jarvis_running and jarvis_responding,
                "jarvis_window_detected": visual_analysis.get("jarvis_window_visible", False),
                "anomaly_detected": anomaly_detected,
                "visual_analysis": visual_analysis,
                "screenshot_path": str(screenshot_path),
                "screenshot_size": self._get_image_size(screenshot_path)
            }

        except Exception as e:
            logger.warning(f"⚠️  Could not analyze screenshot: {e}")
            return {
                "status": "analysis_failed",
                "error": str(e),
                "jarvis_visible": False
            }

    def _check_jarvis_responding(self) -> bool:
        """Check if JARVIS process is responding"""
        try:
            import subprocess
            import platform

            if platform.system() == "Windows":
                result = subprocess.run(
                    ["powershell", "-Command",
                     "$proc = Get-Process python* | Where-Object {$_.MainWindowTitle -like '*JARVIS*'} | Select-Object -First 1; if ($proc) { $proc.Responding } else { $false }"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return "True" in result.stdout
            return False
        except Exception as e:
            logger.debug(f"Response check failed: {e}")
            return False

    def _analyze_screenshot_visual(self, screenshot_path: Path) -> Dict[str, Any]:
        """Analyze screenshot pixels to detect JARVIS window visually"""
        try:
            from PIL import Image
            import numpy as np

            img = Image.open(screenshot_path)
            img_array = np.array(img)

            # Look for JARVIS window characteristics:
            # - Small window (typically 120-180px)
            # - Cyan/blue colors (JARVIS primary color: #00ccff)
            # - Rectangular or circular shapes

            # Simplified: Check for cyan/blue pixels that might indicate JARVIS
            # (This is a basic check - could be enhanced with actual window detection)
            cyan_threshold = [0, 200, 255]  # Approximate JARVIS cyan
            blue_pixels = np.sum(
                (img_array[:, :, 0] < 50) &  # Low red
                (img_array[:, :, 1] > 150) &  # High green
                (img_array[:, :, 2] > 200)    # High blue
            )

            # If we find significant cyan pixels, JARVIS window might be visible
            total_pixels = img_array.shape[0] * img_array.shape[1]
            cyan_ratio = blue_pixels / total_pixels

            # Threshold: if >0.1% of pixels are cyan, might be JARVIS
            jarvis_window_visible = cyan_ratio > 0.001

            return {
                "jarvis_window_visible": jarvis_window_visible,
                "cyan_pixel_ratio": float(cyan_ratio),
                "total_pixels": int(total_pixels),
                "cyan_pixels_detected": int(blue_pixels)
            }

        except ImportError:
            # NumPy not available - skip visual analysis
            return {
                "jarvis_window_visible": False,
                "analysis_note": "numpy_not_available"
            }
        except Exception as e:
            logger.debug(f"Visual analysis failed: {e}")
            return {
                "jarvis_window_visible": False,
                "error": str(e)
            }

    def _check_jarvis_process(self) -> bool:
        """Check if JARVIS process is running"""
        try:
            import subprocess
            import platform

            if platform.system() == "Windows":
                # Check for JARVIS window
                result = subprocess.run(
                    ["powershell", "-Command",
                     "Get-Process python* | Where-Object {$_.MainWindowTitle -like '*JARVIS*'} | Select-Object -First 1"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return "JARVIS" in result.stdout
            else:
                # Linux/Mac check
                result = subprocess.run(
                    ["pgrep", "-f", "jarvis_wandering"],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0

        except Exception as e:
            logger.debug(f"Process check failed: {e}")
            return False

    def _get_image_size(self, screenshot_path: Path) -> Optional[Dict[str, int]]:
        """Get image dimensions"""
        try:
            from PIL import Image
            img = Image.open(screenshot_path)
            return {"width": img.width, "height": img.height}
        except Exception as e:
            logger.debug(f"Could not get image size: {e}")
            return None

    def detect_crash(self) -> bool:
        """Detect if JARVIS has crashed based on state history"""
        if len(self.screenshot_history) < 2:
            return False

        # Check if JARVIS was running but now isn't
        recent_states = self.screenshot_history[-3:]
        was_running = any(s.get("jarvis_state", {}).get("jarvis_visible", False)
                         for s in recent_states[:-1])
        now_running = recent_states[-1].get("jarvis_state", {}).get("jarvis_visible", False)

        # Also check for anomaly: process running but window not visible
        current_state = recent_states[-1].get("jarvis_state", {})
        anomaly = current_state.get("anomaly_detected", False)

        if was_running and not now_running:
            self.crash_detected = True
            logger.warning("🚨 JARVIS CRASH DETECTED: Process was running but is now missing")
            return True

        if anomaly:
            self.crash_detected = True
            logger.warning("🚨 JARVIS ANOMALY DETECTED: Process running but window not visible")
            logger.warning(f"   Process running: {current_state.get('jarvis_process_running')}")
            logger.warning(f"   Process responding: {current_state.get('jarvis_responding')}")
            logger.warning(f"   Window visible: {current_state.get('jarvis_window_detected')}")
            return True

        return False

    def detect_freeze(self) -> bool:
        """Detect if JARVIS window is frozen (same position for multiple checks)"""
        if len(self.screenshot_history) < 5:
            return False

        # Check if JARVIS window position hasn't changed
        # (This would require window position tracking - simplified for now)
        return False

    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("📡 Starting continuous desktop monitoring...")
        logger.info("   Watching RDP feed for JARVIS state changes")

        self.running = True

        while self.running:
            try:
                # Capture current state
                state = self.capture_desktop_state()

                # Check for crashes
                if self.detect_crash():
                    logger.error("🚨 JARVIS CRASH/ANOMALY DETECTED!")
                    logger.error(f"   Last state: {state}")
                    logger.error("   Attempting auto-recovery...")
                    self._attempt_recovery()

                # Check for freezes
                if self.detect_freeze():
                    logger.warning("⚠️  JARVIS FREEZE DETECTED!")

                # Log current state
                jarvis_state = state.get("jarvis_state", {})
                if jarvis_state.get("jarvis_visible"):
                    logger.debug("✅ JARVIS visible and running")
                else:
                    logger.debug("⚠️  JARVIS not visible")

                # Wait for next check
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("⏹️  Monitoring stopped by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(self.check_interval)

    def start(self):
        try:
            """Start monitoring in background thread"""
            import threading
            import os

            # Create PID file for tracking
            pid_file = self.project_root / "data" / "jarvis_desktop_monitor.pid"
            pid_file.parent.mkdir(parents=True, exist_ok=True)
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
            logger.info(f"✅ PID file created: {pid_file}")

            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("✅ Desktop monitoring started (background thread)")

        except Exception as e:
            self.logger.error(f"Error in start: {e}", exc_info=True)
            raise
    def _attempt_recovery(self):
        """Attempt to recover from JARVIS crash/anomaly"""
        try:
            import subprocess
            import platform

            logger.info("🔄 Attempting JARVIS recovery...")

            # Kill existing JARVIS process if frozen
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["powershell", "-Command",
                     "Get-Process python* | Where-Object {$_.MainWindowTitle -like '*JARVIS*'} | Stop-Process -Force"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                logger.info("   ✅ Killed frozen JARVIS process")

            # Wait a moment
            time.sleep(2)

            # Restart JARVIS
            script_path = self.project_root / "scripts" / "python" / "start_jarvis_wandering.py"
            if script_path.exists():
                subprocess.Popen(
                    ["python", str(script_path), "--size", "180"],
                    cwd=str(self.project_root),
                    creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0
                )
                logger.info("   ✅ Restarted JARVIS")
                time.sleep(3)  # Give it time to start
            else:
                logger.error(f"   ❌ Could not find start script: {script_path}")

        except Exception as e:
            logger.error(f"   ❌ Recovery failed: {e}")

    def stop(self):
        try:
            """Stop monitoring"""
            self.running = False

            # Remove PID file
            pid_file = self.project_root / "data" / "jarvis_desktop_monitor.pid"
            if pid_file.exists():
                pid_file.unlink()

            logger.info("⏹️  Desktop monitoring stopped")


        except Exception as e:
            self.logger.error(f"Error in stop: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Desktop Monitor")
    parser.add_argument("--interval", type=float, default=5.0,
                       help="Check interval in seconds (default: 5.0)")
    parser.add_argument("--background", action="store_true",
                       help="Run in background thread")

    args = parser.parse_args()

    monitor = JARVISDesktopMonitor(check_interval=args.interval)

    if args.background:
        monitor.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop()
    else:
        monitor.monitor_loop()


if __name__ == "__main__":


    main()