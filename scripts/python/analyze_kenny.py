#!/usr/bin/env python3
"""
Analyze Kenny - Compare frames to observe speed, position, size, proportions, appearance
Self-validation by analyzing captured burst photos
Analyzes movement, size, visual appearance, and other properties
"""

import sys
from pathlib import Path
from PIL import Image, ImageChops
import json
import logging
logger = logging.getLogger("analyze_kenny")


project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def find_kenny_in_frame(img: Image.Image) -> tuple:
    """Find Kenny's position in frame by looking for orange pixels"""
    pixels = img.load()
    width, height = img.size

    orange_positions = []
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            if isinstance(pixel, tuple) and len(pixel) >= 3:
                r, g, b = pixel[0], pixel[1], pixel[2]
                # Orange: high red, medium green, low blue
                if r > 200 and g > 100 and g < 180 and b < 100:
                    orange_positions.append((x, y))

    if not orange_positions:
        return None

    # Calculate centroid
    avg_x = sum(p[0] for p in orange_positions) / len(orange_positions)
    avg_y = sum(p[1] for p in orange_positions) / len(orange_positions)

    # Find bounding box
    min_x = min(p[0] for p in orange_positions)
    max_x = max(p[0] for p in orange_positions)
    min_y = min(p[1] for p in orange_positions)
    max_y = max(p[1] for p in orange_positions)

    size = max(max_x - min_x, max_y - min_y)

    return (avg_x, avg_y, size, len(orange_positions))

def analyze_kenny(frame_dir: Path):
    try:
        """Analyze Kenny - movement, size, proportions, appearance between frames"""
        frames = sorted(frame_dir.glob("kenny_frame_*.png"))

        if len(frames) < 2:
            print("❌ Need at least 2 frames to analyze movement")
            return

        print("🔍 ANALYZING KENNY (Self-Validation)")
        print("=" * 80)
        print()

        frame_data = []

        # Load and analyze each frame
        for i, frame_path in enumerate(frames):
            img = Image.open(frame_path)
            kenny_data = find_kenny_in_frame(img)

            if kenny_data:
                x, y, size, orange_count = kenny_data
                frame_data.append({
                    "frame": i + 1,
                    "path": str(frame_path.name),
                    "position": {"x": x, "y": y},
                    "size": size,
                    "orange_pixels": orange_count
                })
                print(f"Frame {i+1}: Position ({x:.1f}, {y:.1f}), Size: {size:.1f}px, Orange pixels: {orange_count}")
            else:
                print(f"Frame {i+1}: Kenny not found")

        print()

        if len(frame_data) < 2:
            print("❌ Not enough frames with Kenny found for movement analysis")
            return

        # Calculate movement between frames
        print("📊 MOVEMENT ANALYSIS:")
        print("-" * 80)

        observations = []

        for i in range(len(frame_data) - 1):
            frame1 = frame_data[i]
            frame2 = frame_data[i + 1]

            x1, y1 = frame1["position"]["x"], frame1["position"]["y"]
            x2, y2 = frame2["position"]["x"], frame2["position"]["y"]

            dx = x2 - x1
            dy = y2 - y1
            distance = (dx**2 + dy**2)**0.5

            # Frame interval was 0.5 seconds
            time_interval = 0.5
            speed = distance / time_interval  # pixels per second

            print(f"Frame {frame1['frame']} → Frame {frame2['frame']}:")
            print(f"  Distance: {distance:.1f}px")
            print(f"  Speed: {speed:.1f} px/s")
            print(f"  Direction: dx={dx:.1f}, dy={dy:.1f}")

            observations.append({
                "from_frame": frame1["frame"],
                "to_frame": frame2["frame"],
                "distance_px": distance,
                "speed_px_per_sec": speed,
                "direction": {"dx": dx, "dy": dy}
            })

        print()
        print("=" * 80)
        print("🔍 OBSERVATIONS:")
        print("-" * 80)

        # Average speed
        if observations:
            avg_speed = sum(o["speed_px_per_sec"] for o in observations) / len(observations)
            print(f"Average Speed: {avg_speed:.1f} px/s")

            # Compare to expected (balanced mode: movement_speed = 1.0, interpolation_factor = 0.1)
            # Expected: slow, steady movement
            if avg_speed > 50:
                print("⚠️  OBSERVATION: Speed appears FAST (may be too fast for balanced mode)")
            elif avg_speed < 5:
                print("⚠️  OBSERVATION: Speed appears SLOW (may be too slow)")
            else:
                print("✅ OBSERVATION: Speed appears BALANCED")

        # Size consistency
        sizes = [f["size"] for f in frame_data]
        size_variance = max(sizes) - min(sizes) if sizes else 0
        if size_variance > 20:
            print(f"⚠️  OBSERVATION: Size variance is {size_variance:.1f}px (may indicate scaling issues)")
        else:
            print("✅ OBSERVATION: Size appears consistent")

        print()

        # Save analysis
        analysis_file = frame_dir / "kenny_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump({
                "frames": frame_data,
                "observations": observations,
                "summary": {
                    "average_speed": avg_speed if observations else None,
                    "size_variance": size_variance
                }
            }, f, indent=2)

        print(f"✅ Analysis saved: {analysis_file.name}")

    except Exception as e:
        logger.error(f"Error in analyze_kenny: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    frame_dir = project_root / "data" / "manus_rdp_captures"
    analyze_kenny(frame_dir)
