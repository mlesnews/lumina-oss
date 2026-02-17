#!/usr/bin/env python3
"""
Analyze Kenny Design Elements - Comprehensive Visual Analysis

Examines frames to verify:
- Arc reactor position (chest/torso area)
- Helmet/head position (upper area)
- Color distribution
- Element positioning
- Design correctness

Tags: #KENNY #VISUAL_ANALYSIS #DESIGN_VERIFICATION @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
from typing import Dict, List, Tuple
import logging
logger = logging.getLogger("analyze_kenny_design_elements")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def find_color_regions(img: Image.Image, color_range: Dict[str, Tuple[int, int]]) -> Dict:
    """Find regions of specific colors in image"""
    pixels = np.array(img)

    # Orange (Kenny's body): R>200, G 100-180, B<100
    orange_mask = (
        (pixels[:,:,0] > 200) &
        (pixels[:,:,1] > 100) & (pixels[:,:,1] < 180) &
        (pixels[:,:,2] < 100)
    )

    # Cyan (Arc reactor): R<50, G>200, B>200
    cyan_mask = (
        (pixels[:,:,0] < 50) &
        (pixels[:,:,1] > 200) &
        (pixels[:,:,2] > 200)
    )

    # Black (HUD/Face): R<50, G<50, B<50
    black_mask = (
        (pixels[:,:,0] < 50) &
        (pixels[:,:,1] < 50) &
        (pixels[:,:,2] < 50)
    )

    return {
        "orange": orange_mask,
        "cyan": cyan_mask,
        "black": black_mask
    }

def analyze_element_positions(img: Image.Image, masks: Dict) -> Dict:
    """Analyze positions of design elements"""
    height, width = img.size[1], img.size[0]
    center_y = height / 2
    center_x = width / 2

    results = {}

    # Find orange body center and bounds
    if masks["orange"].any():
        orange_coords = np.where(masks["orange"])
        orange_y_coords = orange_coords[0]
        orange_x_coords = orange_coords[1]

        body_center_y = orange_y_coords.mean()
        body_center_x = orange_x_coords.mean()
        body_top = orange_y_coords.min()
        body_bottom = orange_y_coords.max()
        body_left = orange_x_coords.min()
        body_right = orange_x_coords.max()

        body_height = body_bottom - body_top
        body_width = body_right - body_left

        results["body"] = {
            "center": (body_center_x, body_center_y),
            "bounds": (body_left, body_top, body_right, body_bottom),
            "size": (body_width, body_height),
            "pixel_count": masks["orange"].sum()
        }
    else:
        results["body"] = None

    # Find cyan arc reactor position
    if masks["cyan"].any():
        cyan_coords = np.where(masks["cyan"])
        cyan_y_coords = cyan_coords[0]
        cyan_x_coords = cyan_coords[1]

        arc_y = cyan_y_coords.mean()
        arc_x = cyan_x_coords.mean()
        arc_top = cyan_y_coords.min()
        arc_bottom = cyan_y_coords.max()

        # Calculate position relative to body
        if results["body"]:
            body_center_y = results["body"]["center"][1]
            body_top = results["body"]["bounds"][1]
            body_bottom = results["body"]["bounds"][3]

            # Is arc reactor in upper, middle, or lower third of body?
            body_range = body_bottom - body_top
            arc_position_ratio = (arc_y - body_top) / body_range if body_range > 0 else 0.5

            results["arc_reactor"] = {
                "center": (arc_x, arc_y),
                "bounds": (cyan_x_coords.min(), arc_top, cyan_x_coords.max(), arc_bottom),
                "pixel_count": masks["cyan"].sum(),
                "position_in_body": arc_position_ratio,  # 0.0 = top, 1.0 = bottom
                "is_in_chest": 0.3 < arc_position_ratio < 0.7,  # Middle third = chest area
                "is_visible": True
            }
        else:
            results["arc_reactor"] = {
                "center": (arc_x, arc_y),
                "pixel_count": masks["cyan"].sum(),
                "is_visible": True
            }
    else:
        results["arc_reactor"] = {"is_visible": False}

    # Find black HUD/face position
    if masks["black"].any():
        black_coords = np.where(masks["black"])
        black_y_coords = black_coords[0]
        black_x_coords = black_coords[1]

        hud_y = black_y_coords.mean()
        hud_x = black_x_coords.mean()
        hud_top = black_y_coords.min()
        hud_bottom = black_y_coords.max()

        # Calculate position relative to body
        if results["body"]:
            body_center_y = results["body"]["center"][1]
            body_top = results["body"]["bounds"][1]
            body_bottom = results["body"]["bounds"][3]

            body_range = body_bottom - body_top
            hud_position_ratio = (hud_y - body_top) / body_range if body_range > 0 else 0.5

            results["helmet"] = {
                "center": (hud_x, hud_y),
                "bounds": (black_x_coords.min(), hud_top, black_x_coords.max(), hud_bottom),
                "pixel_count": masks["black"].sum(),
                "position_in_body": hud_position_ratio,
                "is_in_head": hud_position_ratio < 0.4,  # Upper 40% = head area
                "is_visible": True
            }
        else:
            results["helmet"] = {
                "center": (hud_x, hud_y),
                "pixel_count": masks["black"].sum(),
                "is_visible": True
            }
    else:
        results["helmet"] = {"is_visible": False}

    return results

def analyze_frame(frame_path: Path) -> Dict:
    try:
        """Analyze a single frame"""
        img = Image.open(frame_path)

        # Find color regions
        masks = find_color_regions(img, {})

        # Analyze element positions
        positions = analyze_element_positions(img, masks)

        return {
            "frame": frame_path.name,
            "size": img.size,
            "positions": positions,
            "pixel_counts": {
                "orange": masks["orange"].sum(),
                "cyan": masks["cyan"].sum(),
                "black": masks["black"].sum()
            }
        }

    except Exception as e:
        logger.error(f"Error in analyze_frame: {e}", exc_info=True)
        raise
def analyze_burst_frames(frame_dir: Path) -> Dict:
    """Analyze all frames in burst capture"""
    frames = sorted(frame_dir.glob("frame_*.png"))

    if not frames:
        return {"error": "No frames found"}

    analyses = []
    for frame in frames:
        try:
            analysis = analyze_frame(frame)
            analyses.append(analysis)
        except Exception as e:
            print(f"⚠️  Error analyzing {frame.name}: {e}")

    # Aggregate results
    if not analyses:
        return {"error": "No valid analyses"}

    # Calculate averages
    arc_reactor_visible = sum(1 for a in analyses if a["positions"].get("arc_reactor", {}).get("is_visible", False))
    arc_reactor_in_chest = sum(1 for a in analyses if a["positions"].get("arc_reactor", {}).get("is_in_chest", False))
    helmet_visible = sum(1 for a in analyses if a["positions"].get("helmet", {}).get("is_visible", False))
    helmet_in_head = sum(1 for a in analyses if a["positions"].get("helmet", {}).get("is_in_head", False))

    avg_arc_position = np.mean([a["positions"].get("arc_reactor", {}).get("position_in_body", 0.5) 
                                for a in analyses if a["positions"].get("arc_reactor", {}).get("is_visible", False)])
    avg_helmet_position = np.mean([a["positions"].get("helmet", {}).get("position_in_body", 0.5) 
                                   for a in analyses if a["positions"].get("helmet", {}).get("is_visible", False)])

    return {
        "total_frames": len(analyses),
        "arc_reactor": {
            "visible_in": f"{arc_reactor_visible}/{len(analyses)} frames",
            "in_chest_area": f"{arc_reactor_in_chest}/{arc_reactor_visible} visible frames",
            "avg_position_ratio": avg_arc_position if arc_reactor_visible > 0 else None,
            "position_interpretation": "CHEST" if 0.3 < avg_arc_position < 0.7 else ("HEAD" if avg_arc_position < 0.3 else "LOWER_BODY")
        },
        "helmet": {
            "visible_in": f"{helmet_visible}/{len(analyses)} frames",
            "in_head_area": f"{helmet_in_head}/{helmet_visible} visible frames",
            "avg_position_ratio": avg_helmet_position if helmet_visible > 0 else None,
            "position_interpretation": "HEAD" if avg_helmet_position < 0.4 else ("CHEST" if avg_helmet_position < 0.7 else "LOWER_BODY")
        },
        "frame_analyses": analyses
    }

def main():
    try:
        import argparse

        parser = argparse.ArgumentParser(description="Analyze Kenny design elements in burst frames")
        parser.add_argument("frame_dir", type=Path, help="Directory containing burst frames")
        args = parser.parse_args()

        if not args.frame_dir.exists():
            print(f"❌ Directory not found: {args.frame_dir}")
            return

        print("=" * 80)
        print("🔍 KENNY DESIGN ELEMENTS ANALYSIS")
        print("=" * 80)
        print()

        results = analyze_burst_frames(args.frame_dir)

        if "error" in results:
            print(f"❌ {results['error']}")
            return

        print(f"📊 Total Frames Analyzed: {results['total_frames']}")
        print()

        # Arc Reactor Analysis
        print("⚡ ARC REACTOR ANALYSIS:")
        arc = results["arc_reactor"]
        print(f"   Visible in: {arc['visible_in']} frames")
        if arc["avg_position_ratio"] is not None:
            print(f"   Average position in body: {arc['avg_position_ratio']:.2%} (0% = top, 100% = bottom)")
            print(f"   Position interpretation: {arc['position_interpretation']}")
            print(f"   In chest area: {arc['in_chest_area']} frames")
            if arc["position_interpretation"] == "CHEST":
                print("   ✅ CORRECT: Arc reactor is in chest/torso area")
            else:
                print(f"   ⚠️  WARNING: Arc reactor appears to be in {arc['position_interpretation']} area, not chest")
        else:
            print("   ❌ Arc reactor not detected in any frames")
        print()

        # Helmet Analysis
        print("🪖 HELMET/HEAD ANALYSIS:")
        helmet = results["helmet"]
        print(f"   Visible in: {helmet['visible_in']} frames")
        if helmet["avg_position_ratio"] is not None:
            print(f"   Average position in body: {helmet['avg_position_ratio']:.2%} (0% = top, 100% = bottom)")
            print(f"   Position interpretation: {helmet['position_interpretation']}")
            print(f"   In head area: {helmet['in_head_area']} frames")
            if helmet["position_interpretation"] == "HEAD":
                print("   ✅ CORRECT: Helmet/head is in upper area")
            else:
                print(f"   ⚠️  WARNING: Helmet appears to be in {helmet['position_interpretation']} area, not head")
        else:
            print("   ❌ Helmet not detected in any frames")
        print()

        # Overall Assessment
        print("=" * 80)
        print("📋 OVERALL ASSESSMENT:")
        print("=" * 80)

        arc_correct = arc.get("position_interpretation") == "CHEST" if arc.get("avg_position_ratio") else False
        helmet_correct = helmet.get("position_interpretation") == "HEAD" if helmet.get("avg_position_ratio") else False

        if arc_correct and helmet_correct:
            print("✅ DESIGN CORRECT: Arc reactor in chest, helmet in head")
        elif arc_correct:
            print("⚠️  PARTIAL: Arc reactor correct, but helmet position needs adjustment")
        elif helmet_correct:
            print("⚠️  PARTIAL: Helmet correct, but arc reactor position needs adjustment")
        else:
            print("❌ DESIGN ISSUES: Both elements need position adjustment")

        print()

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()