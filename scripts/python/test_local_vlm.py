#!/usr/bin/env python3
"""
Test Local VLM Integration

Tests local VLM without requiring API keys.

Tags: #TEST #LOCAL_VLM #NO_API_KEY @JARVIS @LUMINA
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
    from vlm_integration import VLMIntegration
    from screen_capture_system import ScreenCaptureSystem
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("TestLocalVLM")


def test_local_vlm():
    """Test local VLM"""
    print("=" * 80)
    print("TEST: Local VLM Integration")
    print("=" * 80)
    print()
    print("Testing local VLM - NO API KEY NEEDED!")
    print()

    try:
        # Initialize local VLM
        print("1. Initializing local VLM...")
        vlm = VLMIntegration(provider="local")
        print(f"   ✅ VLM initialized")
        print(f"   Provider: {vlm.provider}")
        print(f"   Device: {vlm.device}")
        print()

        if not vlm.transformers_available:
            print("❌ Transformers not available")
            print("   Install: pip install --user transformers torch pillow")
            return False

        if not vlm.local_model:
            print("⚠️  Local model not loaded")
            print("   This is normal on first run - model will download")
            print("   Install: pip install --user transformers torch pillow")
            return False

        print(f"   ✅ Model loaded: {vlm.model}")
        print()

        # Capture screenshot
        print("2. Capturing screenshot...")
        capture = ScreenCaptureSystem()
        screenshot_path = capture.capture_screenshot("test_local_vlm.png")
        print(f"   ✅ Screenshot: {screenshot_path}")
        print()

        # Analyze with local VLM
        print("3. Analyzing with local VLM...")
        print("   (This may take a moment, especially on CPU)")
        result = vlm.analyze_screen_with_vlm(
            screenshot_path,
            prompt="What is happening on this screen? Describe any UI elements, text, and what the user might be trying to do."
        )

        if result.get("available"):
            print("   ✅ Analysis complete!")
            print()
            print("VLM Analysis:")
            print("-" * 80)
            print(result.get("analysis", "No analysis"))
            print("-" * 80)
            print()
            print(f"Model: {result.get('model')}")
            print(f"Device: {result.get('device')}")
            return True
        else:
            print(f"   ❌ Analysis failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("=" * 80)
    print("LOCAL VLM TEST - NO API KEY NEEDED")
    print("=" * 80)
    print()

    result = test_local_vlm()

    print("=" * 80)
    if result:
        print("✅ LOCAL VLM TEST PASSED")
        print()
        print("Local VLM is working! No API keys needed.")
    else:
        print("❌ LOCAL VLM TEST FAILED")
        print()
        print("Install required libraries:")
        print("  pip install --user transformers torch pillow accelerate")
    print("=" * 80)

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()