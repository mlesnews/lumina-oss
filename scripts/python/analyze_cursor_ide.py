#!/usr/bin/env python3
"""
Analyze Cursor IDE with Local VLM

Captures and analyzes Cursor IDE screen to identify configuration opportunities.

Tags: #CURSOR_IDE #VLM #ANALYSIS #CONFIGURATION @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from visual_monitoring_system import VisualMonitoringSystem
    from screen_capture_system import ScreenCaptureSystem
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("AnalyzeCursorIDE")


def analyze_cursor_ide():
    """Analyze Cursor IDE screen with local VLM"""
    print("=" * 80)
    print("🔍 ANALYZING CURSOR IDE WITH LOCAL VLM")
    print("=" * 80)
    print()
    print("This will:")
    print("  1. Capture current Cursor IDE screen")
    print("  2. Analyze with local VLM")
    print("  3. Identify configuration opportunities")
    print("  4. Review features 1-1500+")
    print()

    # Initialize visual monitoring
    print("Initializing visual monitoring system...")
    monitoring = VisualMonitoringSystem()
    print(f"✅ System ready (VLM: {monitoring.use_vlm})")
    print()

    # Give user time to switch to Cursor IDE
    print("=" * 80)
    print("⏳ PREPARING TO CAPTURE")
    print("=" * 80)
    print()
    print("Please switch to Cursor IDE now...")
    print("Capturing in 3 seconds...")
    print()

    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    print()
    print("📸 Capturing screen...")
    print()

    # Capture and analyze
    try:
        # Capture screenshot
        capture = ScreenCaptureSystem()
        screenshot_path = capture.capture_screenshot("cursor_ide_analysis.png")
        print(f"✅ Screenshot captured: {screenshot_path}")
        print()

        # Analyze with VLM
        print("🤖 Analyzing with local VLM...")
        print("   (This may take a moment)")
        print()

        # Use VLM directly for detailed analysis
        if monitoring.vlm and monitoring.vlm.local_model:
            vlm_result = monitoring.vlm.analyze_screen_with_vlm(
                screenshot_path,
                prompt="""Analyze this Cursor IDE screen in detail. Identify:
1. All visible UI elements (menus, panels, toolbars, status bar)
2. Current configuration settings visible
3. Features that could be enabled/configured
4. Settings panels or preferences that are accessible
5. Any configuration opportunities
6. List all features and settings you can see that should be configured (1-1500+)

Provide a comprehensive analysis of what's visible and what configuration options are available."""
            )

            if vlm_result.get("available"):
                print("=" * 80)
                print("📊 CURSOR IDE ANALYSIS RESULTS")
                print("=" * 80)
                print()
                print(vlm_result.get("analysis", "No analysis available"))
                print()
                print("=" * 80)
                print("✅ ANALYSIS COMPLETE")
                print("=" * 80)
                print()

                # Also get intent detection
                print("Detecting intent and configuration needs...")
                intent = monitoring.detect_intent_from_screen()
                print(f"Intent: {intent.get('intent_type')}")
                print(f"Confidence: {intent.get('confidence', 0):.1%}")
                print()

                return vlm_result
            else:
                print(f"❌ VLM analysis failed: {vlm_result.get('error')}")
                return None
        else:
            print("❌ Local VLM not available")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function"""
    result = analyze_cursor_ide()

    if result:
        print("=" * 80)
        print("📋 NEXT STEPS")
        print("=" * 80)
        print()
        print("Based on the analysis, you can now:")
        print("  1. Review the VLM analysis above")
        print("  2. Configure Cursor IDE features identified")
        print("  3. Set up settings panels mentioned")
        print("  4. Enable features 1-1500+ as needed")
        print()
        print("Screenshot saved for reference.")
        print()

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()