#!/usr/bin/env python3
"""
Use Local VLM for Screen Analysis

Demonstrates local VLM in action - no API keys needed!

Tags: #DEMO #LOCAL_VLM #SCREEN_ANALYSIS @JARVIS @LUMINA
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
    from visual_monitoring_system import VisualMonitoringSystem
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("UseLocalVLM")


def main():
    """Use local VLM to analyze screen"""
    print("=" * 80)
    print("🤖 USING LOCAL VLM - NO API KEY NEEDED!")
    print("=" * 80)
    print()

    # Initialize visual monitoring with local VLM (default)
    print("1. Initializing visual monitoring system...")
    print("   (Using local VLM - no API key needed)")
    print()

    try:
        monitoring = VisualMonitoringSystem()
        print(f"   ✅ System initialized")
        print(f"   VLM enabled: {monitoring.use_vlm}")
        if monitoring.vlm:
            print(f"   Provider: {monitoring.vlm.provider}")
            print(f"   Device: {monitoring.vlm.device}")
            if monitoring.vlm.local_model:
                print(f"   Model: {monitoring.vlm.model}")
            else:
                print(f"   ⚠️  Model not loaded yet (will load on first use)")
        print()

        # Capture and analyze screen
        print("2. Capturing current screen...")
        print("   (Taking screenshot)")
        print()

        # Detect intent from screen
        print("3. Analyzing screen with local VLM...")
        print("   (This may take a moment, especially on first run)")
        print("   (Model will download automatically if needed)")
        print()

        intent = monitoring.detect_intent_from_screen()

        print()
        print("=" * 80)
        print("📊 ANALYSIS RESULTS")
        print("=" * 80)
        print()

        # Show results
        print(f"Intent Detected: {intent.get('detected')}")
        print(f"Intent Type: {intent.get('intent_type')}")
        print(f"Confidence: {intent.get('confidence', 0):.1%}")
        print(f"Method: {intent.get('method', 'unknown')}")
        print()

        if intent.get('suggested_action'):
            print(f"Suggested Action: {intent.get('suggested_action')}")
            print()

        # Show VLM analysis if available
        vlm_result = intent.get('vlm_result')
        if vlm_result and vlm_result.get('available'):
            print("=" * 80)
            print("🤖 LOCAL VLM ANALYSIS")
            print("=" * 80)
            print()
            print(vlm_result.get('analysis', 'No analysis available'))
            print()
            print(f"Model: {vlm_result.get('model')}")
            print(f"Device: {vlm_result.get('device')}")
            print()

        # Show screen content summary
        screen_content = intent.get('screen_content', {})
        if screen_content:
            print("=" * 80)
            print("📸 SCREEN CONTENT SUMMARY")
            print("=" * 80)
            print()
            print(f"Text words extracted: {screen_content.get('word_count', 0)}")
            print(f"UI elements detected: {screen_content.get('ui_elements', 0)}")
            print(f"OCR confidence: {screen_content.get('ocr_confidence', 0):.1f}%")
            print()

        # Show observation info
        observation = intent.get('observation', {})
        if observation.get('screenshot'):
            print(f"Screenshot saved: {observation['screenshot']}")
            print()

        print("=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print()
        print("Local VLM is working! No API keys needed.")
        print("Everything runs locally on your machine.")
        print()

        return 0

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("Troubleshooting:")
        print("  1. Ensure transformers is installed: pip install --user transformers torch pillow")
        print("  2. Check internet connection (for first model download)")
        print("  3. Ensure enough disk space (4-13GB for models)")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()