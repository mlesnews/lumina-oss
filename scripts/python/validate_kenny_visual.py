#!/usr/bin/env python3
"""
Validate Kenny Visual - Analyze captured frames to verify speed, proportions, appearance
"""

import sys
from pathlib import Path
from PIL import Image
import json

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None

# JARVIS integration
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def analyze_kenny_frames(frame_dir: Path):
    """Analyze captured Kenny frames for validation"""
    frames = sorted(frame_dir.glob("kenny_frame_*.png"))

    if not frames:
        print("❌ No Kenny frames found")
        return

    print(f"📸 Analyzing {len(frames)} frames...")
    print()

    results = {
        "frames_analyzed": len(frames),
        "frame_details": []
    }

    for i, frame_path in enumerate(frames, 1):
        try:
            img = Image.open(frame_path)
            width, height = img.size

            # Basic analysis
            print(f"Frame {i}: {frame_path.name}")
            print(f"   Size: {width}x{height}")
            print(f"   Format: {img.format}")
            print(f"   Mode: {img.mode}")

            # Check for orange pixels (Kenny's color)
            pixels = list(img.getdata())
            orange_pixels = 0
            for pixel in pixels:
                if isinstance(pixel, tuple) and len(pixel) >= 3:
                    r, g, b = pixel[0], pixel[1], pixel[2]
                    # Orange: high red, medium green, low blue
                    if r > 200 and g > 100 and g < 180 and b < 100:
                        orange_pixels += 1

            orange_percentage = (orange_pixels / len(pixels)) * 100 if pixels else 0
            print(f"   Orange pixels: {orange_pixels} ({orange_percentage:.2f}%)")

            results["frame_details"].append({
                "frame": frame_path.name,
                "size": {"width": width, "height": height},
                "orange_pixels": orange_pixels,
                "orange_percentage": orange_percentage
            })

            print()

        except Exception as e:
            print(f"   ❌ Error analyzing frame: {e}")
            print()

    # Save analysis
    analysis_file = frame_dir / "kenny_validation_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✅ Analysis saved: {analysis_file.name}")

if __name__ == "__main__":
    frame_dir = project_root / "data" / "manus_rdp_captures"
    analyze_kenny_frames(frame_dir)
