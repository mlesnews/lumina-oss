#!/usr/bin/env python3
"""
Capture Kenny Snapshot - Take screenshot and analyze visual state

Captures Kenny's current visual state and analyzes it using SYPHON capabilities.
Can examine the hexagonal head, body proportions, colors, and overall appearance.

Tags: #KENNY #SNAPSHOT #SYPHON #VISUAL_ANALYSIS @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from datetime import datetime
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

logger = get_logger("CaptureKennySnapshot")

def find_kenny_window():
    """Find Kenny's window position using Windows API"""
    try:
        import win32gui
        import win32con

        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if "kenny" in window_title.lower() or "imva" in window_title.lower():
                    windows.append((hwnd, window_title))
            return True

        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)

        if windows:
            hwnd, title = windows[0]
            rect = win32gui.GetWindowRect(hwnd)
            return {
                "hwnd": hwnd,
                "title": title,
                "left": rect[0],
                "top": rect[1],
                "right": rect[2],
                "bottom": rect[3],
                "width": rect[2] - rect[0],
                "height": rect[3] - rect[1]
            }
    except ImportError:
        logger.warning("win32gui not available - will try alternative method")
    except Exception as e:
        logger.warning(f"Error finding window: {e}")

    return None

def capture_kenny_window_screenshot():
    """Capture screenshot of Kenny's window"""
    window_info = find_kenny_window()

    if window_info:
        # Capture specific window region
        bbox = (
            window_info["left"],
            window_info["top"],
            window_info["right"],
            window_info["bottom"]
        )
        logger.info(f"📸 Capturing Kenny window: {window_info['title']}")
        logger.info(f"   Position: ({window_info['left']}, {window_info['top']})")
        logger.info(f"   Size: {window_info['width']}x{window_info['height']}")
    else:
        # Fallback: Try to capture center of screen (where Kenny usually is)
        logger.warning("⚠️  Could not find Kenny window - capturing screen center")
        screen_width, screen_height = 1920, 1080  # Default screen size
        window_size = 120  # Kenny's window size
        bbox = (
            screen_width // 2 - window_size // 2,
            screen_height // 2 - window_size // 2,
            screen_width // 2 + window_size // 2,
            screen_height // 2 + window_size // 2
        )

    try:
        screenshot = ImageGrab.grab(bbox=bbox)
        return screenshot, window_info
    except Exception as e:
        logger.error(f"❌ Error capturing screenshot: {e}")
        return None, None

def analyze_kenny_appearance(img: Image.Image) -> dict:
    """Analyze Kenny's visual appearance using SYPHON-like analysis"""
    pixels = np.array(img)

    # Find Hot Rod Red pixels (Kenny's body/head color: RGB 220, 20, 60)
    # Updated to match Hot Rod Red (220, 20, 60) instead of orange (255, 140, 0)
    hot_rod_red_mask = (
        (pixels[:,:,0] > 200) & (pixels[:,:,0] < 240) &  # Red 200-240 (Hot Rod Red is 220)
        (pixels[:,:,1] < 50) &  # Green < 50 (Hot Rod Red is 20)
        (pixels[:,:,2] > 40) & (pixels[:,:,2] < 80)  # Blue 40-80 (Hot Rod Red is 60)
    )

    # Find cyan pixels (arc reactor/eyes: RGB 0, 217, 255)
    cyan_mask = (
        (pixels[:,:,0] < 50) &  # Red < 50
        (pixels[:,:,1] > 150) & (pixels[:,:,1] < 255) &  # Green 150-255
        (pixels[:,:,2] > 200)  # Blue > 200
    )

    hot_rod_red_count = hot_rod_red_mask.sum()
    cyan_count = cyan_mask.sum()
    total_pixels = pixels.shape[0] * pixels.shape[1]

    # Analyze shape (check for hexagonal head vs round)
    hot_rod_red_coords = np.where(hot_rod_red_mask)
    if len(hot_rod_red_coords[0]) > 0:
        center_y = hot_rod_red_coords[0].mean()
        center_x = hot_rod_red_coords[1].mean()

        # Calculate distances from center
        distances = np.sqrt(
            (hot_rod_red_coords[0] - center_y)**2 + 
            (hot_rod_red_coords[1] - center_x)**2
        )

        # Check for angular/geometric shape (hexagon) vs round
        # Hexagonal shape will have more variation in distance from center
        distance_variance = np.var(distances)
        max_dist = distances.max()

        # Geometric/angular shapes have higher variance
        shape_score = float(distance_variance / (max_dist ** 2) if max_dist > 0 else 0)
        is_geometric = bool(shape_score > 0.15)  # Threshold for geometric vs round
    else:
        center_x, center_y = img.width // 2, img.height // 2
        is_geometric = False
        shape_score = 0.0

    return {
        "timestamp": datetime.now().isoformat(),
        "image_size": {"width": img.width, "height": img.height},
        "orange_pixels": int(hot_rod_red_count),  # Keep API name for backward compatibility
        "cyan_pixels": int(cyan_count),
        "orange_percentage": float(hot_rod_red_count / total_pixels * 100) if total_pixels > 0 else 0.0,
        "cyan_percentage": float(cyan_count / total_pixels * 100) if total_pixels > 0 else 0.0,
        "center": {"x": float(center_x), "y": float(center_y)},
        "is_geometric_head": is_geometric,
        "shape_score": float(shape_score),
        "head_type": "geometric/hexagonal" if is_geometric else "round",
        "analysis": {
            "body_detected": hot_rod_red_count > 100,
            "arc_reactor_detected": cyan_count > 10,
            "head_shape": "hexagonal (Jarvis-like)" if is_geometric else "round",
            "proportions": "Iron Man-like" if hot_rod_red_count > 500 else "small"
        }
    }

def main():
    try:
        """Capture and analyze Kenny snapshot"""
        print("=" * 80)
        print("📸 KENNY SNAPSHOT CAPTURE & ANALYSIS")
        print("=" * 80)
        print()

        # Create output directory
        output_dir = project_root / "data" / "kenny_snapshots"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Capture screenshot
        print("📸 Capturing Kenny window...")
        screenshot, window_info = capture_kenny_window_screenshot()

        if screenshot is None:
            print("❌ Failed to capture screenshot")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = output_dir / f"kenny_snapshot_{timestamp}.png"
        screenshot.save(screenshot_path)
        print(f"✅ Screenshot saved: {screenshot_path.name}")
        print()

        # Analyze appearance
        print("🔍 Analyzing Kenny's appearance...")
        analysis = analyze_kenny_appearance(screenshot)

        print()
        print("=" * 80)
        print("ANALYSIS RESULTS:")
        print("=" * 80)
        print(f"Image Size: {analysis['image_size']['width']}x{analysis['image_size']['height']}")
        print(f"Orange Pixels: {analysis['orange_pixels']} ({analysis['orange_percentage']:.2f}%)")
        print(f"Cyan Pixels (Arc Reactor/Eyes): {analysis['cyan_pixels']} ({analysis['cyan_percentage']:.2f}%)")
        print(f"Head Shape: {analysis['head_type']}")
        print(f"  - Geometric/Hexagonal: {'✅ Yes' if analysis['is_geometric_head'] else '❌ No'}")
        print(f"  - Shape Score: {analysis['shape_score']:.3f}")
        print()
        print("DETECTED FEATURES:")
        print(f"  - Body: {'✅ Detected' if analysis['analysis']['body_detected'] else '❌ Not detected'}")
        print(f"  - Arc Reactor: {'✅ Detected' if analysis['analysis']['arc_reactor_detected'] else '❌ Not detected'}")
        print(f"  - Head Shape: {analysis['analysis']['head_shape']}")
        print(f"  - Proportions: {analysis['analysis']['proportions']}")
        print("=" * 80)

        # Save analysis
        analysis_path = output_dir / f"kenny_analysis_{timestamp}.json"
        import json
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"✅ Analysis saved: {analysis_path.name}")
        print()

        return screenshot_path, analysis

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()