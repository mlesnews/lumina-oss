#!/usr/bin/env python3
"""
Test Screen Capture System

Actually tests screen capture to verify it works.
Only makes factual statements based on test results.

Tags: #TEST #SCREEN_CAPTURE #VALIDATION @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from screen_capture_system import (SCREEN_CAPTURE_AVAILABLE,
                                       ScreenCaptureSystem)
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("TestScreenCapture")


def test_screenshot():
    """Test screenshot capture"""
    print("=" * 80)
    print("TEST 1: Screenshot Capture")
    print("=" * 80)
    print()

    if not SCREEN_CAPTURE_AVAILABLE:
        print("❌ FAILED: Screen capture libraries not available")
        print("   Install: pip install --user mss opencv-python")
        return False

    try:
        capture = ScreenCaptureSystem()
        screenshot_path = capture.capture_screenshot("test_screenshot.png")

        if screenshot_path and screenshot_path.exists():
            file_size = screenshot_path.stat().st_size
            print("✅ PASSED: Screenshot captured")
            print(f"   File: {screenshot_path}")
            print(f"   Size: {file_size} bytes")
            return True
        else:
            print("❌ FAILED: Screenshot file not created")
            print(f"   Expected: {screenshot_path}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Error during screenshot capture: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_recording():
    """Test screen recording"""
    print("=" * 80)
    print("TEST 2: Screen Recording")
    print("=" * 80)
    print()

    if not SCREEN_CAPTURE_AVAILABLE:
        print("❌ FAILED: Screen capture libraries not available")
        print("   Install: pip install --user mss opencv-python")
        return False

    try:
        capture = ScreenCaptureSystem()

        print("Starting 3-second recording...")
        video_path = capture.start_recording("test_recording")

        if not video_path or not capture.recording:
            print("❌ FAILED: Recording did not start")
            return False

        print(f"   Recording to: {video_path}")

        # Record for 3 seconds
        import time
        time.sleep(3)

        stopped_path = capture.stop_recording()

        if not stopped_path:
            print("❌ FAILED: Recording did not stop properly")
            return False

        if stopped_path.exists():
            file_size = stopped_path.stat().st_size
            print("✅ PASSED: Recording completed")
            print(f"   File: {stopped_path}")
            print(f"   Size: {file_size} bytes")
            return True
        else:
            print("❌ FAILED: Video file not created")
            print(f"   Expected: {stopped_path}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Error during recording: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("SCREEN CAPTURE SYSTEM - VALIDATION TESTS")
    print("=" * 80)
    print()
    print("Testing actual functionality...")
    print()

    results = {
        "screenshot": False,
        "recording": False
    }

    # Test screenshot
    results["screenshot"] = test_screenshot()
    print()

    # Test recording
    results["recording"] = test_recording()
    print()

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    print(f"Screenshot Capture: {'✅ PASSED' if results['screenshot'] else '❌ FAILED'}")
    print(f"Screen Recording: {'✅ PASSED' if results['recording'] else '❌ FAILED'}")
    print()

    all_passed = all(results.values())
    if all_passed:
        print("✅ ALL TESTS PASSED - Screen capture system is working")
    else:
        print("❌ SOME TESTS FAILED - Screen capture system has issues")
    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()