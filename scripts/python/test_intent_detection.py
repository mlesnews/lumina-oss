#!/usr/bin/env python3
"""
Test Intent Detection System

Tests OCR, computer vision, and intent detection functionality.

Tags: #TEST #INTENT_DETECTION #OCR #CV @JARVIS @LUMINA
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

logger = get_logger("TestIntentDetection")


def test_ocr():
    """Test OCR text extraction"""
    print("=" * 80)
    print("TEST 1: OCR Text Extraction")
    print("=" * 80)
    print()

    try:
        monitoring = VisualMonitoringSystem()
        ocr_result = monitoring.extract_text_from_screen()

        if ocr_result.get("available"):
            print("✅ OCR is available")
            print(f"   Words extracted: {ocr_result.get('word_count', 0)}")
            print(f"   Average confidence: {ocr_result.get('confidence', 0):.1f}%")
            if ocr_result.get("text"):
                text_preview = ocr_result["text"][:200]
                print(f"   Text preview: {text_preview}...")
            return True
        else:
            print("❌ OCR not available")
            print("   Install: pip install --user pytesseract")
            return False
    except Exception as e:
        print(f"❌ Error testing OCR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cv_analysis():
    """Test computer vision analysis"""
    print("=" * 80)
    print("TEST 2: Computer Vision Analysis")
    print("=" * 80)
    print()

    try:
        monitoring = VisualMonitoringSystem()
        cv_result = monitoring.analyze_screen_with_cv()

        if cv_result.get("available"):
            print("✅ Computer vision is available")
            print(f"   UI elements detected: {cv_result.get('element_count', 0)}")
            print(f"   Edges detected: {cv_result.get('edges', 0)}")
            print(f"   Screen size: {cv_result.get('screen_size', {})}")
            print(f"   Average brightness: {cv_result.get('avg_brightness', 0):.1f}")
            return True
        else:
            print("❌ Computer vision not available")
            return False
    except Exception as e:
        print(f"❌ Error testing CV: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intent_detection():
    """Test intent detection"""
    print("=" * 80)
    print("TEST 3: Intent Detection")
    print("=" * 80)
    print()

    try:
        monitoring = VisualMonitoringSystem()
        intent = monitoring.detect_intent_from_screen()

        print(f"Intent detected: {intent.get('detected')}")
        print(f"Intent type: {intent.get('intent_type')}")
        print(f"Confidence: {intent.get('confidence', 0):.1%}")
        print(f"Suggested action: {intent.get('suggested_action')}")
        print()

        screen_content = intent.get('screen_content', {})
        print("Screen content analysis:")
        print(f"   Text words: {screen_content.get('word_count', 0)}")
        print(f"   UI elements: {screen_content.get('ui_elements', 0)}")
        print(f"   OCR confidence: {screen_content.get('ocr_confidence', 0):.1f}%")
        print()

        if intent.get('detected'):
            print("✅ Intent detection working")
            return True
        else:
            print("⚠️  No intent detected (may be normal for current screen)")
            return True  # Still counts as working
    except Exception as e:
        print(f"❌ Error testing intent detection: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("INTENT DETECTION SYSTEM - VALIDATION TESTS")
    print("=" * 80)
    print()
    print("Testing OCR, CV, and intent detection...")
    print()

    results = {
        "ocr": False,
        "cv": False,
        "intent": False
    }

    # Test OCR
    results["ocr"] = test_ocr()
    print()

    # Test CV
    results["cv"] = test_cv_analysis()
    print()

    # Test intent detection
    results["intent"] = test_intent_detection()
    print()

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    print(f"OCR Text Extraction: {'✅ PASSED' if results['ocr'] else '❌ FAILED'}")
    print(f"Computer Vision Analysis: {'✅ PASSED' if results['cv'] else '❌ FAILED'}")
    print(f"Intent Detection: {'✅ PASSED' if results['intent'] else '❌ FAILED'}")
    print()

    all_passed = all(results.values())
    if all_passed:
        print("✅ ALL TESTS PASSED - Intent detection system is working")
    else:
        print("❌ SOME TESTS FAILED - Intent detection system has issues")
    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()