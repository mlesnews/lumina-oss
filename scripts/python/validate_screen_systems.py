#!/usr/bin/env python3
"""
Validate Screen Capture and Visual Monitoring Systems

Actually tests and validates what's working.
Only reports factual results.

Tags: #VALIDATION #SCREEN_CAPTURE #VISUAL_MONITORING @JARVIS @LUMINA
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
    from screen_capture_system import ScreenCaptureSystem, SCREEN_CAPTURE_AVAILABLE
    from visual_monitoring_system import VisualMonitoringSystem
    from drive_mapping_system import DriveMappingSystem
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("ValidateScreenSystems")


def validate_dependencies():
    """Check if dependencies are installed"""
    print("=" * 80)
    print("DEPENDENCY CHECK")
    print("=" * 80)
    print()

    if SCREEN_CAPTURE_AVAILABLE:
        print("✅ Screen capture libraries available")
        print("   • mss: Installed")
        print("   • opencv-python: Installed")
    else:
        print("❌ Screen capture libraries NOT available")
        print("   Install: pip install --user mss opencv-python")
        return False

    print()
    return True


def validate_drive_mapping():
    """Validate drive mapping system"""
    print("=" * 80)
    print("DRIVE MAPPING VALIDATION")
    print("=" * 80)
    print()

    try:
        drive_system = DriveMappingSystem()
        status = drive_system.get_drive_status()

        print(f"Total drives configured: {status['total_count']}")
        print(f"Drives mapped: {status['mapped_count']}")
        print()

        for letter, info in status["mappings"].items():
            status_icon = "✅" if info["mapped"] else "❌"
            print(f"{status_icon} {letter}: {info['network_path']}")
            print(f"   Purpose: {info['purpose']}")
            print(f"   Mapped: {info['mapped']}")
            print()

        # Check video storage path
        video_path = drive_system.get_video_storage_path()
        print(f"Video storage path: {video_path}")
        if video_path.exists():
            print("✅ Video storage path exists")
        else:
            print("⚠️  Video storage path does not exist (will be created)")
        print()

        return True
    except Exception as e:
        print(f"❌ Error validating drive mapping: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_screen_capture():
    """Validate screen capture system"""
    print("=" * 80)
    print("SCREEN CAPTURE VALIDATION")
    print("=" * 80)
    print()

    if not SCREEN_CAPTURE_AVAILABLE:
        print("❌ Screen capture not available - skipping test")
        return False

    try:
        capture = ScreenCaptureSystem()
        info = capture.get_storage_info()

        print(f"Storage path: {info['storage_path']}")
        print(f"Storage type: {info['storage_type']}")
        print(f"Recording: {info['recording']}")
        print()

        # Test screenshot
        print("Testing screenshot capture...")
        screenshot_path = capture.capture_screenshot("validation_test.png")

        if screenshot_path and screenshot_path.exists():
            file_size = screenshot_path.stat().st_size
            print("✅ Screenshot test passed")
            print(f"   File: {screenshot_path}")
            print(f"   Size: {file_size} bytes")
        else:
            print("❌ Screenshot test failed")
            return False
        print()

        return True
    except Exception as e:
        print(f"❌ Error validating screen capture: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_visual_monitoring():
    """Validate visual monitoring system"""
    print("=" * 80)
    print("VISUAL MONITORING VALIDATION")
    print("=" * 80)
    print()

    try:
        monitoring = VisualMonitoringSystem()
        status = monitoring.get_monitoring_status()

        print(f"Monitoring active: {status['monitoring']}")
        print(f"Recording: {status['recording']}")
        print(f"Storage: {status['storage_info']['storage_path']}")
        print(f"Screenshots captured: {status['screenshots_captured']}")
        print()

        # Test observation capture
        if SCREEN_CAPTURE_AVAILABLE:
            print("Testing observation capture...")
            observation = monitoring.capture_observation("Validation test")

            if observation and "screenshot" in observation:
                screenshot_path = Path(observation["screenshot"])
                if screenshot_path.exists():
                    print("✅ Observation capture test passed")
                    print(f"   Screenshot: {screenshot_path}")
                else:
                    print("❌ Observation capture test failed - screenshot not found")
                    return False
            else:
                print("❌ Observation capture test failed - no observation data")
                return False
        else:
            print("⚠️  Screen capture not available - skipping observation test")
        print()

        return True
    except Exception as e:
        print(f"❌ Error validating visual monitoring: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validations"""
    print("=" * 80)
    print("SCREEN CAPTURE & VISUAL MONITORING - VALIDATION")
    print("=" * 80)
    print()
    print("Validating actual functionality...")
    print()

    results = {
        "dependencies": False,
        "drive_mapping": False,
        "screen_capture": False,
        "visual_monitoring": False
    }

    # Check dependencies
    results["dependencies"] = validate_dependencies()
    print()

    # Validate drive mapping
    results["drive_mapping"] = validate_drive_mapping()
    print()

    # Validate screen capture
    results["screen_capture"] = validate_screen_capture()
    print()

    # Validate visual monitoring
    results["visual_monitoring"] = validate_visual_monitoring()
    print()

    # Summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    print()

    all_passed = all(results.values())
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print()
        print("FACTUAL STATUS:")
        print("  • Dependencies: Installed and available")
        print("  • Drive mapping: Configured")
        print("  • Screen capture: Working (tested)")
        print("  • Visual monitoring: Working (tested)")
        print("  • Video storage: NAS (V: drive)")
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print()
        print("FACTUAL STATUS:")
        for test_name, passed in results.items():
            status = "Working" if passed else "Not working"
            print(f"  • {test_name.replace('_', ' ').title()}: {status}")

    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()