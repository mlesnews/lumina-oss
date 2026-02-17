#!/usr/bin/env python3
"""
Burst Photo Window - Rapid frame capture to see the truth

Like camera burst mode - captures rapid frames to see what's really happening.
Video is just seamless frames. We need to see the stark reality, not the illusion.

"Just the facts, ma'am." - Tony Stark reality
"""

import sys
import time
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture

class BurstPhotoWindow:
    """
    Burst Photo Window - Rapid frame capture

    Captures rapid frames like camera burst mode to see the truth.
    Video is just seamless frames - we need to see what's really happening.
    """

    def __init__(self):
        """Initialize burst capture"""
        self.capture = MANUSRDPScreenshotCapture()
        self.output_dir = self.capture.output_dir / "burst_captures"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print("=" * 80)
        print("📸 BURST PHOTO WINDOW - Seeing the Stark Reality")
        print("   'Just the facts, ma'am.'")
        print("=" * 80)

    def capture_burst(
        self,
        frame_count: int = 10,
        interval: float = 0.1,  # 100ms = 10 FPS burst
        description: str = "kenny_observation"
    ) -> list:
        """
        Capture burst of frames - rapid succession

        Args:
            frame_count: Number of frames to capture
            interval: Time between frames (seconds)
            description: Description of what we're observing

        Returns:
            List of captured frame paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        burst_dir = self.output_dir / f"{description}_{timestamp}"
        burst_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📸 BURST CAPTURE: {frame_count} frames @ {interval*1000:.0f}ms intervals")
        print(f"   Output: {burst_dir}")
        print(f"   Observing: {description}")
        print()

        frames = []
        start_time = time.time()

        for i in range(frame_count):
            frame_num = i + 1
            frame_filename = f"frame_{frame_num:03d}.png"
            frame_path = burst_dir / frame_filename

            # Capture frame
            screenshot = self.capture.capture_screenshot(frame_filename)
            if screenshot:
                # Move to burst directory
                if screenshot.parent != burst_dir:
                    target_path = burst_dir / screenshot.name
                    if screenshot.exists():
                        import shutil
                        shutil.move(str(screenshot), str(target_path))
                        frame_path = target_path
                    else:
                        frame_path = screenshot
                else:
                    frame_path = screenshot

                frames.append(frame_path)
                elapsed = time.time() - start_time
                print(f"  Frame {frame_num:03d}/{frame_count:03d}: {frame_path.name} ({elapsed:.2f}s)")
            else:
                print(f"  Frame {frame_num:03d}/{frame_count:03d}: FAILED")

            # Wait for next frame (except last)
            if i < frame_count - 1:
                time.sleep(interval)

        total_time = time.time() - start_time
        fps = frame_count / total_time if total_time > 0 else 0

        print()
        print("=" * 80)
        print(f"✅ BURST CAPTURE COMPLETE")
        print(f"   Frames captured: {len(frames)}/{frame_count}")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Effective FPS: {fps:.1f}")
        print(f"   Location: {burst_dir}")
        print("=" * 80)

        # Save metadata
        metadata = {
            "timestamp": timestamp,
            "description": description,
            "frame_count": frame_count,
            "interval": interval,
            "frames_captured": len(frames),
            "total_time": total_time,
            "effective_fps": fps,
            "frames": [str(f.relative_to(self.output_dir)) for f in frames]
        }

        import json
        metadata_file = burst_dir / "burst_metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

        return frames

    def analyze_burst(self, frames: list) -> dict:
        """
        Analyze burst frames to see what's really happening

        Returns:
            Analysis of what we observed
        """
        if not frames:
            return {"error": "No frames to analyze"}

        # Basic analysis
        analysis = {
            "total_frames": len(frames),
            "frame_paths": [str(f) for f in frames],
            "observation": "Burst capture complete - review frames to see stark reality"
        }

        print("\n🔍 BURST ANALYSIS:")
        print(f"   Total frames: {len(frames)}")
        print(f"   Review frames to see what's actually happening")
        print(f"   'Just the facts, ma'am.'")

        return analysis


def main():
    """Main - capture burst to see the truth"""
    import argparse

    parser = argparse.ArgumentParser(description="Burst Photo Window - See the Stark Reality")
    parser.add_argument('--frames', type=int, default=10, help='Number of frames (default: 10)')
    parser.add_argument('--interval', type=float, default=0.1, help='Interval between frames in seconds (default: 0.1 = 10 FPS)')
    parser.add_argument('--description', type=str, default='kenny_observation', help='Description of observation')

    args = parser.parse_args()

    burst = BurstPhotoWindow()
    frames = burst.capture_burst(
        frame_count=args.frames,
        interval=args.interval,
        description=args.description
    )

    analysis = burst.analyze_burst(frames)

    print(f"\n📊 Analysis saved to burst metadata")
    print(f"   Review frames in: {burst.output_dir}")


if __name__ == "__main__":


    main()