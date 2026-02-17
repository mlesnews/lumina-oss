#!/usr/bin/env python3
"""
Capture Kenny frames - Frame-by-frame desktop capture to see what's happening

Captures multiple screenshots in sequence to see desktop state.
"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture

def capture_frames(count: int = 5, interval: float = 1.0):
    """Capture multiple frames to see desktop state"""
    capture = MANUSRDPScreenshotCapture()

    print(f"📸 Capturing {count} frames at {interval}s intervals...")

    frames = []
    for i in range(count):
        frame_path = capture.capture_screenshot(f"kenny_frame_{i+1}.png")
        if frame_path:
            frames.append(frame_path)
            print(f"  Frame {i+1}/{count}: {frame_path.name}")
        else:
            print(f"  Frame {i+1}/{count}: Failed")

        if i < count - 1:
            time.sleep(interval)

    print(f"\n✅ Captured {len(frames)} frames")
    print(f"   Location: {frames[0].parent if frames else 'N/A'}")

    return frames

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=5, help='Number of frames')
    parser.add_argument('--interval', type=float, default=1.0, help='Interval between frames')
    args = parser.parse_args()

    capture_frames(args.count, args.interval)
