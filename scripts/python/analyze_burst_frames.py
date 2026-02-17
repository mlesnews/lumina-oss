#!/usr/bin/env python3
"""
Analyze Burst Frames - See the Stark Reality

Analyzes captured burst frames to see what's actually happening.
"Just the facts, ma'am."
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import logging
logger = logging.getLogger("analyze_burst_frames")


project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from PIL import Image, ImageStat
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not available - cannot analyze images")

def analyze_frame(frame_path: Path) -> Dict[str, Any]:
    """Analyze a single frame"""
    if not PIL_AVAILABLE or not frame_path.exists():
        return {"error": "Cannot analyze"}

    try:
        img = Image.open(frame_path)
        stat = ImageStat.Stat(img)

        return {
            "size": img.size,
            "mode": img.mode,
            "mean_rgb": stat.mean[:3] if len(stat.mean) >= 3 else stat.mean,
            "stddev_rgb": stat.stddev[:3] if len(stat.stddev) >= 3 else stat.stddev,
            "has_alpha": img.mode == "RGBA"
        }
    except Exception as e:
        return {"error": str(e)}

def compare_frames(frames: List[Path]) -> Dict[str, Any]:
    """Compare frames to see if they're identical or different"""
    if not PIL_AVAILABLE:
        return {"error": "PIL not available"}

    if len(frames) < 2:
        return {"error": "Need at least 2 frames"}

    analyses = [analyze_frame(f) for f in frames]

    # Check if frames are identical
    first_frame = Image.open(frames[0])
    identical_count = 0

    for frame_path in frames[1:]:
        try:
            frame_img = Image.open(frame_path)
            if first_frame.size == frame_img.size:
                # Compare pixel data
                if list(first_frame.getdata()) == list(frame_img.getdata()):
                    identical_count += 1
        except:
            pass

    return {
        "total_frames": len(frames),
        "identical_frames": identical_count,
        "frames_changing": len(frames) - identical_count - 1,
        "analyses": analyses
    }

def find_kenny_in_frame(frame_path: Path) -> Dict[str, Any]:
    """Try to find Kenny/IMVA in frame"""
    if not PIL_AVAILABLE or not frame_path.exists():
        return {"error": "Cannot analyze"}

    try:
        img = Image.open(frame_path)
        width, height = img.size

        # Look for small circular/oval shapes (avatars are typically 60-120px)
        # This is a simple heuristic - look for regions with consistent colors

        # Sample center region (where avatars often are)
        center_x, center_y = width // 2, height // 2
        sample_size = 200

        left = max(0, center_x - sample_size)
        top = max(0, center_y - sample_size)
        right = min(width, center_x + sample_size)
        bottom = min(height, center_y + sample_size)

        center_region = img.crop((left, top, right, bottom))
        center_stat = ImageStat.Stat(center_region)

        # Look for orange/red colors (Kenny/Iron Man colors)
        mean_rgb = center_stat.mean[:3] if len(center_stat.mean) >= 3 else center_stat.mean

        # Check if orange/red dominant (Kenny is orange)
        orange_detected = mean_rgb[0] > 200 and mean_rgb[1] > 100  # Red/Orange

        return {
            "frame_size": (width, height),
            "center_region_mean": mean_rgb,
            "orange_detected": orange_detected,
            "possible_avatar": orange_detected
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    try:
        """Analyze burst frames"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Analyze Burst Frames - See the Truth")
        parser.add_argument('burst_dir', type=str, help='Burst capture directory')

        args = parser.parse_args()

        burst_dir = Path(args.burst_dir)
        if not burst_dir.exists():
            print(f"❌ Directory not found: {burst_dir}")
            return

        # Find all frame images
        frames = sorted(burst_dir.glob("frame_*.png"))

        if not frames:
            print(f"❌ No frames found in {burst_dir}")
            return

        print("=" * 80)
        print("🔍 ANALYZING BURST FRAMES - Seeing the Stark Reality")
        print("   'Just the facts, ma'am.'")
        print("=" * 80)
        print(f"\n📸 Found {len(frames)} frames")

        # Analyze each frame
        print("\n📊 Frame Analysis:")
        for i, frame in enumerate(frames[:5], 1):  # Analyze first 5
            analysis = analyze_frame(frame)
            kenny_analysis = find_kenny_in_frame(frame)

            print(f"\n  Frame {i}: {frame.name}")
            if "error" not in analysis:
                print(f"    Size: {analysis['size']}")
                print(f"    Mean RGB: {[int(x) for x in analysis['mean_rgb']]}")
                if kenny_analysis.get("orange_detected"):
                    print(f"    🟠 Orange detected - Possible Kenny/Iron Man!")

        # Compare frames
        print("\n🔄 Frame Comparison:")
        comparison = compare_frames(frames)
        if "error" not in comparison:
            print(f"    Total frames: {comparison['total_frames']}")
            print(f"    Identical frames: {comparison['identical_frames']}")
            print(f"    Frames changing: {comparison['frames_changing']}")

            if comparison['identical_frames'] == comparison['total_frames'] - 1:
                print("    ⚠️  All frames identical - no movement detected")
            else:
                print("    ✅ Frames are changing - movement detected")

        print("\n" + "=" * 80)
        print("✅ Analysis complete")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()