#!/usr/bin/env python3
"""
Kenny & Ace Visual Auto-Corrector - Dynamic Scaling Analysis & Auto-Fix

Takes burst snapshots (1-10 rounds) to examine Kenny and Ace on desktop,
analyzes their visual relationship, and automatically corrects/adopts design
to overcome visual design challenges.

Features:
- Burst snapshot capture (multiple rounds)
- Desktop analysis (Kenny + Ace relationship)
- Automatic size/position/proportion correction
- Visual design challenge detection and resolution
- Dynamic scaling adjustments

Tags: #KENNY #ACE #VISUAL_ANALYSIS #AUTO_CORRECT #DYNAMIC_SCALING @JARVIS @LUMINA
"""

import sys
import time
import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageGrab
import numpy as np

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("KennyAceVisualAutoCorrector")

def find_windows():
    """Find Kenny and Ace window positions"""
    windows = {"kenny": None, "ace": None}

    try:
        import win32gui

        def enum_windows_callback(hwnd, found_windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).lower()
                if "kenny" in title or "imva" in title:
                    rect = win32gui.GetWindowRect(hwnd)
                    found_windows["kenny"] = {
                        "hwnd": hwnd,
                        "title": win32gui.GetWindowText(hwnd),
                        "left": rect[0],
                        "top": rect[1],
                        "right": rect[2],
                        "bottom": rect[3],
                        "width": rect[2] - rect[0],
                        "height": rect[3] - rect[1]
                    }
                elif "iron" in title or "ace" in title or "acva" in title:
                    rect = win32gui.GetWindowRect(hwnd)
                    found_windows["ace"] = {
                        "hwnd": hwnd,
                        "title": win32gui.GetWindowText(hwnd),
                        "left": rect[0],
                        "top": rect[1],
                        "right": rect[2],
                        "bottom": rect[3],
                        "width": rect[2] - rect[0],
                        "height": rect[3] - rect[1]
                    }
            return True

        win32gui.EnumWindows(enum_windows_callback, windows)
    except ImportError:
        logger.warning("win32gui not available - using fallback detection")
    except Exception as e:
        logger.warning(f"Error finding windows: {e}")

    return windows

def capture_burst_snapshot(round_number: int, burst_count: int = 10) -> List[Image.Image]:
    """Capture burst of snapshots (multiple frames)"""
    snapshots = []
    windows = find_windows()

    logger.info(f"📸 Round {round_number}: Capturing {burst_count} burst snapshots...")

    for i in range(burst_count):
        # Small delay between captures
        if i > 0:
            time.sleep(0.1)

        # Capture full screen or specific regions
        try:
            screenshot = ImageGrab.grab()
            snapshots.append(screenshot)
        except Exception as e:
            logger.warning(f"Error capturing snapshot {i+1}: {e}")

    return snapshots, windows

def analyze_kenny_visual(snapshot: Image.Image, kenny_window: Optional[Dict]) -> Dict[str, Any]:
    """Analyze Kenny's visual appearance"""
    if not kenny_window:
        return {"detected": False}

    # Extract Kenny region
    bbox = (
        kenny_window["left"],
        kenny_window["top"],
        kenny_window["right"],
        kenny_window["bottom"]
    )

    try:
        kenny_region = snapshot.crop(bbox)
        pixels = np.array(kenny_region)

        # Find Hot Rod Red pixels (220, 20, 60)
        red_mask = (
            (pixels[:,:,0] > 180) & (pixels[:,:,0] < 255) &  # Red
            (pixels[:,:,1] > 10) & (pixels[:,:,1] < 80) &  # Green
            (pixels[:,:,2] > 40) & (pixels[:,:,2] < 100)  # Blue
        )

        # Find Gold pixels (255, 215, 0)
        gold_mask = (
            (pixels[:,:,0] > 240) &  # Red
            (pixels[:,:,1] > 180) & (pixels[:,:,1] < 240) &  # Green
            (pixels[:,:,2] < 50)  # Blue
        )

        # Find Cyan pixels (arc reactor/eyes: 0, 217, 255)
        cyan_mask = (
            (pixels[:,:,0] < 50) &  # Red
            (pixels[:,:,1] > 150) & (pixels[:,:,1] < 255) &  # Green
            (pixels[:,:,2] > 200)  # Blue
        )

        red_count = red_mask.sum()
        gold_count = gold_mask.sum()
        cyan_count = cyan_mask.sum()
        total_pixels = pixels.shape[0] * pixels.shape[1]

        # Calculate visual size (how much of window is filled)
        filled_ratio = (red_count + gold_count + cyan_count) / total_pixels if total_pixels > 0 else 0

        # Detect geometric head (hexagonal)
        red_coords = np.where(red_mask)
        is_geometric = False
        shape_score = 0.0

        if len(red_coords[0]) > 0:
            center_y = red_coords[0].mean()
            center_x = red_coords[1].mean()
            distances = np.sqrt(
                (red_coords[0] - center_y)**2 + 
                (red_coords[1] - center_x)**2
            )
            distance_variance = np.var(distances)
            max_dist = distances.max()
            shape_score = float(distance_variance / (max_dist ** 2) if max_dist > 0 else 0)
            is_geometric = shape_score > 0.15

        return {
            "detected": True,
            "window_size": {"width": kenny_window["width"], "height": kenny_window["height"]},
            "red_pixels": int(red_count),
            "gold_pixels": int(gold_count),
            "cyan_pixels": int(cyan_count),
            "filled_ratio": float(filled_ratio),
            "is_geometric_head": bool(is_geometric),
            "shape_score": float(shape_score),
            "visual_size_estimate": float(filled_ratio * kenny_window["width"])
        }
    except Exception as e:
        logger.error(f"Error analyzing Kenny: {e}")
        return {"detected": False, "error": str(e)}

def analyze_ace_visual(snapshot: Image.Image, ace_window: Optional[Dict]) -> Dict[str, Any]:
    """Analyze Ace's visual appearance"""
    if not ace_window:
        return {"detected": False}

    # Extract Ace region
    bbox = (
        ace_window["left"],
        ace_window["top"],
        ace_window["right"],
        ace_window["bottom"]
    )

    try:
        ace_region = snapshot.crop(bbox)
        pixels = np.array(ace_region)

        # Find red/gold pixels (Iron Man colors)
        red_mask = (
            (pixels[:,:,0] > 180) &  # Red
            (pixels[:,:,1] < 100) &  # Low green
            (pixels[:,:,2] < 100)  # Low blue
        )

        gold_mask = (
            (pixels[:,:,0] > 240) &  # Red
            (pixels[:,:,1] > 180) &  # Green
            (pixels[:,:,2] < 50)  # Blue
        )

        red_count = red_mask.sum()
        gold_count = gold_mask.sum()
        total_pixels = pixels.shape[0] * pixels.shape[1]

        filled_ratio = (red_count + gold_count) / total_pixels if total_pixels > 0 else 0

        return {
            "detected": True,
            "window_size": {"width": ace_window["width"], "height": ace_window["height"]},
            "red_pixels": int(red_count),
            "gold_pixels": int(gold_count),
            "filled_ratio": float(filled_ratio),
            "visual_size_estimate": float(filled_ratio * ace_window["width"])
        }
    except Exception as e:
        logger.error(f"Error analyzing Ace: {e}")
        return {"detected": False, "error": str(e)}

def analyze_desktop_relationship(kenny_analysis: Dict, ace_analysis: Dict, windows: Dict) -> Dict[str, Any]:
    """Analyze desktop relationship between Kenny and Ace"""
    relationship = {
        "kenny_detected": kenny_analysis.get("detected", False),
        "ace_detected": ace_analysis.get("detected", False),
        "size_comparison": {},
        "position_relationship": {},
        "visual_challenges": []
    }

    if kenny_analysis.get("detected") and ace_analysis.get("detected"):
        # Size comparison
        kenny_size = kenny_analysis.get("visual_size_estimate", 0)
        ace_size = ace_analysis.get("visual_size_estimate", 0)

        size_ratio = kenny_size / ace_size if ace_size > 0 else 0
        relationship["size_comparison"] = {
            "kenny_size": kenny_size,
            "ace_size": ace_size,
            "ratio": size_ratio,
            "kenny_too_small": size_ratio < 0.8,
            "kenny_too_large": size_ratio > 1.2,
            "size_match": 0.8 <= size_ratio <= 1.2
        }

        # Position relationship
        if windows.get("kenny") and windows.get("ace"):
            kenny_center_x = (windows["kenny"]["left"] + windows["kenny"]["right"]) / 2
            kenny_center_y = (windows["kenny"]["top"] + windows["kenny"]["bottom"]) / 2
            ace_center_x = (windows["ace"]["left"] + windows["ace"]["right"]) / 2
            ace_center_y = (windows["ace"]["top"] + windows["ace"]["bottom"]) / 2

            distance = np.sqrt(
                (kenny_center_x - ace_center_x)**2 + 
                (kenny_center_y - ace_center_y)**2
            )

            relationship["position_relationship"] = {
                "distance": float(distance),
                "kenny_pos": (float(kenny_center_x), float(kenny_center_y)),
                "ace_pos": (float(ace_center_x), float(ace_center_y))
            }

        # Detect visual challenges
        if relationship["size_comparison"].get("kenny_too_small"):
            relationship["visual_challenges"].append({
                "issue": "kenny_too_small",
                "severity": "high",
                "recommendation": "Increase Kenny's size to match Ace"
            })

        if relationship["size_comparison"].get("kenny_too_large"):
            relationship["visual_challenges"].append({
                "issue": "kenny_too_large",
                "severity": "medium",
                "recommendation": "Decrease Kenny's size to match Ace"
            })

        if not kenny_analysis.get("is_geometric_head", False):
            relationship["visual_challenges"].append({
                "issue": "head_not_geometric",
                "severity": "low",
                "recommendation": "Ensure hexagonal head is visible"
            })

    return relationship

def auto_correct_kenny(analysis_results: List[Dict], component_config_file: Path):
    """Automatically correct Kenny based on analysis results"""
    if not analysis_results:
        return

    # Aggregate results across all rounds
    avg_kenny_size = 0
    avg_ace_size = 0
    size_ratios = []
    challenges = []

    for result in analysis_results:
        relationship = result.get("relationship", {})
        size_comp = relationship.get("size_comparison", {})

        if size_comp.get("kenny_size"):
            avg_kenny_size += size_comp["kenny_size"]
        if size_comp.get("ace_size"):
            avg_ace_size += size_comp["ace_size"]
        if size_comp.get("ratio"):
            size_ratios.append(size_comp["ratio"])

        challenges.extend(relationship.get("visual_challenges", []))

    if len(analysis_results) > 0:
        avg_kenny_size /= len(analysis_results)
        avg_ace_size /= len(analysis_results)
        avg_ratio = sum(size_ratios) / len(size_ratios) if size_ratios else 1.0

    # Determine corrections needed
    corrections = {}

    if avg_ratio < 0.8:
        # Kenny too small - increase size
        size_adjustment = 1.0 / avg_ratio if avg_ratio > 0 else 1.2
        corrections["body"] = {"size_scale": size_adjustment}
        corrections["helmet"] = {"size_scale": size_adjustment}
        logger.info(f"🔧 Auto-correct: Increasing Kenny size (ratio: {avg_ratio:.2f})")

    elif avg_ratio > 1.2:
        # Kenny too large - decrease size
        size_adjustment = 1.0 / avg_ratio
        corrections["body"] = {"size_scale": size_adjustment}
        corrections["helmet"] = {"size_scale": size_adjustment}
        logger.info(f"🔧 Auto-correct: Decreasing Kenny size (ratio: {avg_ratio:.2f})")

    # Apply corrections via live component config
    if corrections:
        try:
            # Load existing config or create new
            if component_config_file.exists():
                with open(component_config_file, 'r') as f:
                    config = json.load(f)
            else:
                from kenny_live_component_adjuster import load_component_config
                config = load_component_config()

            # Apply corrections
            for component, adjustments in corrections.items():
                if component in config.get("components", {}):
                    for key, value in adjustments.items():
                        config["components"][component][key] = value

            config["last_updated"] = datetime.now().isoformat()
            config["auto_corrected"] = True
            config["correction_reason"] = f"Size ratio: {avg_ratio:.2f}, Target: 1.0"

            # Save config (triggers live update in Kenny)
            component_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(component_config_file, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"✅ Auto-corrections applied and saved to {component_config_file.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error applying auto-corrections: {e}")
            return False

    return False

def main():
    """Main execution - burst snapshot analysis and auto-correction"""
    import argparse

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
    SYPHONConfig = None
    DataSourceType = None

    parser = argparse.ArgumentParser(description="Kenny & Ace Visual Auto-Corrector")
    parser.add_argument("--rounds", type=int, default=10, help="Number of burst rounds (default: 10)")
    parser.add_argument("--burst-count", type=int, default=10, help="Snapshots per round (default: 10)")
    parser.add_argument("--auto-correct", action="store_true", help="Automatically apply corrections")
    parser.add_argument("--output-dir", type=str, help="Output directory for snapshots")

    args = parser.parse_args()

    print("=" * 80)
    print("🔬 KENNY & ACE VISUAL AUTO-CORRECTOR")
    print("   Dynamic Scaling Analysis & Auto-Fix")
    print("=" * 80)
    print()

    # Create output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / "data" / "kenny_ace_visual_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    component_config_file = project_root / "data" / "kenny_live_components.json"

    all_results = []

    # Run multiple rounds of burst snapshots
    for round_num in range(1, args.rounds + 1):
        print(f"📸 Round {round_num}/{args.rounds}")
        print("-" * 80)

        # Capture burst
        snapshots, windows = capture_burst_snapshot(round_num, args.burst_count)

        if not snapshots:
            print(f"⚠️  Round {round_num}: No snapshots captured")
            continue

        # Analyze middle snapshot (most representative)
        mid_snapshot = snapshots[len(snapshots) // 2]

        # Analyze Kenny
        kenny_analysis = analyze_kenny_visual(mid_snapshot, windows.get("kenny"))
        print(f"   Kenny: {'✅ Detected' if kenny_analysis.get('detected') else '❌ Not detected'}")
        if kenny_analysis.get("detected"):
            print(f"      Visual size: {kenny_analysis.get('visual_size_estimate', 0):.1f}px")
            print(f"      Filled ratio: {kenny_analysis.get('filled_ratio', 0):.1%}")
            print(f"      Geometric head: {'✅' if kenny_analysis.get('is_geometric_head') else '❌'}")

        # Analyze Ace
        ace_analysis = analyze_ace_visual(mid_snapshot, windows.get("ace"))
        print(f"   Ace: {'✅ Detected' if ace_analysis.get('detected') else '❌ Not detected'}")
        if ace_analysis.get("detected"):
            print(f"      Visual size: {ace_analysis.get('visual_size_estimate', 0):.1f}px")
            print(f"      Filled ratio: {ace_analysis.get('filled_ratio', 0):.1%}")

        # Analyze relationship
        relationship = analyze_desktop_relationship(kenny_analysis, ace_analysis, windows)

        if relationship.get("kenny_detected") and relationship.get("ace_detected"):
            size_comp = relationship.get("size_comparison", {})
            print(f"   Size Ratio: {size_comp.get('ratio', 0):.2f} (Kenny/Ace)")
            if size_comp.get("kenny_too_small"):
                print(f"      ⚠️  Kenny is too small!")
            elif size_comp.get("kenny_too_large"):
                print(f"      ⚠️  Kenny is too large!")
            else:
                print(f"      ✅ Size match!")

            challenges = relationship.get("visual_challenges", [])
            if challenges:
                print(f"   Visual Challenges: {len(challenges)}")
                for challenge in challenges:
                    print(f"      - {challenge.get('issue')}: {challenge.get('recommendation')}")

        # Save snapshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_path = output_dir / f"round_{round_num}_snapshot_{timestamp}.png"
        mid_snapshot.save(snapshot_path)

        # Store results
        result = {
            "round": round_num,
            "timestamp": timestamp,
            "kenny_analysis": kenny_analysis,
            "ace_analysis": ace_analysis,
            "relationship": relationship,
            "snapshot_path": str(snapshot_path)
        }
        all_results.append(result)

        print()

        # Small delay between rounds
        if round_num < args.rounds:
            time.sleep(0.5)

    # Save analysis results
    results_file = output_dir / f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"✅ Analysis results saved: {results_file.name}")
    print()

    # Auto-correct if requested
    if args.auto_correct:
        print("=" * 80)
        print("🔧 AUTO-CORRECTING KENNY...")
        print("=" * 80)
        print()

        if auto_correct_kenny(all_results, component_config_file):
            print("✅ Auto-corrections applied! Kenny will update live.")
        else:
            print("ℹ️  No corrections needed or unable to apply.")
        print()

    print("=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":


    main()