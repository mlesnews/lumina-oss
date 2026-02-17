#!/usr/bin/env python3
"""
Analyze Kenny Visual State - Determine if Froot Loop or Solid Circle

Logical analysis of sprite appearance:
- Count orange pixels
- Calculate center and radius
- Determine if pixels form ring (Froot Loop) or solid circle
- Ring = large gap between inner and outer radius
- Solid = pixels fill from center to edge

Tags: #KENNY #VISUAL_ANALYSIS #LOGIC @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
import logging
logger = logging.getLogger("analyze_kenny_visual_state")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def analyze_kenny_visual_state(frame_path: Path) -> dict:
    """Analyze frame to determine if Kenny is Froot Loop or solid circle"""
    try:
        img = Image.open(frame_path)
        pixels = np.array(img)

        # Find Hot Rod Red pixels (Kenny's body color: RGB 220, 20, 60)
        # Updated to match Hot Rod Red (220, 20, 60) instead of orange (255, 140, 0)
        hot_rod_red_mask = (
            (pixels[:,:,0] > 200) & (pixels[:,:,0] < 240) &  # Red 200-240 (Hot Rod Red is 220)
            (pixels[:,:,1] < 50) &  # Green < 50 (Hot Rod Red is 20)
            (pixels[:,:,2] > 40) & (pixels[:,:,2] < 80)  # Blue 40-80 (Hot Rod Red is 60)
        )

        hot_rod_red_count = hot_rod_red_mask.sum()

        if hot_rod_red_count == 0:
            return {
                "result": "NO_HOT_ROD_RED_DETECTED",
                "hot_rod_red_pixels": 0,
                "confidence": 0.0
            }

        # Find Hot Rod Red pixel coordinates
        hot_rod_red_coords = np.where(hot_rod_red_mask)
        center_y = hot_rod_red_coords[0].mean()
        center_x = hot_rod_red_coords[1].mean()

        # Calculate distances from center
        distances = np.sqrt(
            (hot_rod_red_coords[0] - center_y)**2 + 
            (hot_rod_red_coords[1] - center_x)**2
        )

        max_dist = distances.max()
        min_dist = distances.min()
        mean_dist = distances.mean()

        # Calculate ring thickness
        ring_thickness = max_dist - min_dist
        ring_ratio = ring_thickness / max_dist if max_dist > 0 else 0

        # Determine if ring or solid
        # Ring: large gap between inner and outer radius (>30% of max radius)
        # Solid: pixels fill from center (ring ratio < 20%)
        if ring_ratio > 0.3:
            result = "FROOT_LOOP_RING"
            confidence = min(1.0, ring_ratio)
        elif ring_ratio < 0.2:
            result = "SOLID_CIRCLE"
            confidence = 1.0 - ring_ratio
        else:
            result = "UNCERTAIN"
            confidence = 0.5

        return {
            "result": result,
            "hot_rod_red_pixels": int(hot_rod_red_count),
            "center": (float(center_x), float(center_y)),
            "max_radius": float(max_dist),
            "min_radius": float(min_dist),
            "mean_radius": float(mean_dist),
            "ring_thickness": float(ring_thickness),
            "ring_ratio": float(ring_ratio),
            "confidence": float(confidence)
        }
    except Exception as e:
        return {
            "result": "ERROR",
            "error": str(e),
            "confidence": 0.0
        }

def main():
    try:
        """Main analysis"""
        import argparse

        parser = argparse.ArgumentParser(description="Analyze Kenny Visual State")
        parser.add_argument('frame_dir', type=str, help='Frame directory or single frame')
        args = parser.parse_args()

        frame_dir = Path(args.frame_dir)

        if frame_dir.is_file():
            frames = [frame_dir]
        else:
            frames = sorted(frame_dir.glob("frame_*.png"))

        if not frames:
            print("❌ No frames found")
            return

        print("=" * 80)
        print("🔍 KENNY VISUAL STATE ANALYSIS")
        print("=" * 80)
        print()

        results = []
        for frame_path in frames[:5]:  # Analyze first 5 frames
            result = analyze_kenny_visual_state(frame_path)
            results.append(result)

            print(f"Frame: {frame_path.name}")
            print(f"  Result: {result['result']}")
            if 'orange_pixels' in result:
                print(f"  Orange pixels: {result['orange_pixels']}")
            if 'ring_ratio' in result:
                print(f"  Ring ratio: {result['ring_ratio']:.1%}")
                print(f"  Ring thickness: {result['ring_thickness']:.1f}px")
            if 'confidence' in result:
                print(f"  Confidence: {result['confidence']:.1%}")
            print()

        # Overall result
        if results:
            avg_confidence = sum(r.get('confidence', 0) for r in results) / len(results)
            most_common = max(set(r['result'] for r in results), key=[r['result'] for r in results].count)

            print("=" * 80)
            print("OVERALL RESULT:")
            print(f"  Visual State: {most_common}")
            print(f"  Average Confidence: {avg_confidence:.1%}")

            if most_common == "FROOT_LOOP_RING":
                print("  ❌ NEGATIVE: Kenny appears as Froot Loop (ring)")
            elif most_common == "SOLID_CIRCLE":
                print("  ✅ POSITIVE: Kenny appears as solid circle")
            else:
                print("  ⚠️  UNCERTAIN: Cannot determine visual state")
            print("=" * 80)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()