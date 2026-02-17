#!/usr/bin/env python3
"""
Kenny Froot Loop Test Loop - Conditional Testing Until Fixed

while (Froot Loop == Kenny):
    test()
    if (Kenny != Froot Loop):
        break  # Exit condition achieved

Tags: #KENNY #TEST_LOOP #CONDITIONAL #LOGIC @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.python.analyze_kenny_visual_state import analyze_kenny_visual_state
from scripts.python.burst_photo_window import BurstPhotoWindow

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

def test_kenny_visual_state() -> bool:
    """
    Test if Kenny is Froot Loop or solid circle

    Returns:
        True if Kenny is SOLID_CIRCLE (not Froot Loop)
        False if Kenny is FROOT_LOOP_RING
    """
    # Capture burst frames
    burst = BurstPhotoWindow()
    frames = burst.capture_burst(
        frame_count=3,
        interval=0.2,
        description="kenny_froot_loop_test"
    )

    if not frames:
        return False

    # Analyze first frame
    result = analyze_kenny_visual_state(frames[0])

    is_solid = result.get('result') == 'SOLID_CIRCLE'
    ring_ratio = result.get('ring_ratio', 1.0)

    print(f"  Test result: {result.get('result')}")
    print(f"  Ring ratio: {ring_ratio:.1%}")
    print(f"  Is solid circle: {is_solid}")

    return is_solid

def main():
    """Main test loop"""
    print("=" * 80)
    print("🔄 KENNY FROOT LOOP TEST LOOP")
    print("=" * 80)
    print()
    print("Condition: while (Froot Loop == Kenny)")
    print("Exit: when Kenny != Froot Loop (solid circle)")
    print()

    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration}/{max_iterations} ---")

        # Test condition: Is Kenny a Froot Loop?
        is_froot_loop = not test_kenny_visual_state()

        if is_froot_loop:
            print(f"  ❌ Condition TRUE: Kenny is Froot Loop (iteration {iteration})")
            print("  Continuing loop...")
            time.sleep(2)  # Wait before next test
        else:
            print(f"  ✅ Condition FALSE: Kenny is NOT Froot Loop (solid circle)")
            print("  BREAK: Exit condition achieved!")
            break

    print()
    print("=" * 80)
    if iteration >= max_iterations:
        print("⚠️  Loop ended: Max iterations reached")
        print("   Kenny is still Froot Loop - need to fix root cause")
    else:
        print("✅ Loop ended: Exit condition achieved")
        print(f"   Kenny is solid circle after {iteration} iterations")
    print("=" * 80)

if __name__ == "__main__":


    main()