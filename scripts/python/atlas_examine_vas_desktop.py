#!/usr/bin/env python3
"""
Atlas RDP Manas View - Examine VAs on Desktop in Real-Time

Uses Atlas/RDP screenshot capture to examine Virtual Assistants on the desktop.
Similar to OpenAI Atlas - visual context capture and analysis.

Tags: #ATLAS #RDP #MANAS #VAS #DESKTOP #SCREENSHOT #REALTIME @JARVIS @TEAM
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AtlasExamineVAs")

# Import RDP screenshot capture
try:
    from manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture
    RDP_CAPTURE_AVAILABLE = True
except ImportError:
    RDP_CAPTURE_AVAILABLE = False
    logger.warning("RDP Screenshot Capture not available")

# Try PIL for image analysis
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL/Pillow not available for image analysis")


class AtlasExamineVAsDesktop:
    """
    Atlas RDP Manas View - Examine VAs on Desktop

    Uses screenshot capture to view and analyze Virtual Assistants on desktop in real-time.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Atlas VA examiner"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "atlas_va_examinations"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize RDP screenshot capture
        self.rdp_capture = None
        if RDP_CAPTURE_AVAILABLE:
            try:
                self.rdp_capture = MANUSRDPScreenshotCapture()
                logger.info("✅ RDP Screenshot Capture initialized")
            except Exception as e:
                logger.warning(f"⚠️  RDP Screenshot Capture not available: {e}")

        logger.info("✅ Atlas VA Desktop Examiner initialized")

    def capture_desktop_view(self, description: str = "VA Desktop Examination") -> Optional[Path]:
        """Capture desktop screenshot to examine VAs"""
        if not self.rdp_capture:
            logger.error("❌ RDP Screenshot Capture not available")
            return None

        logger.info("📸 Capturing desktop screenshot...")
        try:
            screenshot_path = self.rdp_capture.capture_screenshot()
            if screenshot_path:
                logger.info(f"   ✅ Screenshot captured: {screenshot_path.name}")

                # Save with context
                metadata = self.rdp_capture.capture_with_context(description, auto_capture=False)
                metadata["screenshot_path"] = str(screenshot_path)

                return screenshot_path
            else:
                logger.warning("   ⚠️  Screenshot capture returned None")
                return None
        except Exception as e:
            logger.error(f"   ❌ Error capturing screenshot: {e}")
            return None

    def analyze_va_positions(self, screenshot_path: Optional[Path] = None) -> Dict[str, Any]:
        """Analyze VA positions from screenshot"""
        if screenshot_path is None:
            screenshot_path = self.capture_desktop_view("VA Position Analysis")

        if not screenshot_path or not screenshot_path.exists():
            logger.error("❌ Screenshot not available for analysis")
            return {
                "success": False,
                "error": "Screenshot not available"
            }

        result = {
            "timestamp": datetime.now().isoformat(),
            "screenshot_path": str(screenshot_path),
            "vas_detected": [],
            "analysis": {}
        }

        if PIL_AVAILABLE:
            try:
                img = Image.open(screenshot_path)
                width, height = img.size

                result["analysis"] = {
                    "screenshot_size": {"width": width, "height": height},
                    "timestamp": datetime.now().isoformat(),
                    "note": "Screenshot captured. Visual analysis requires image processing or manual review."
                }

                logger.info(f"   📊 Screenshot analyzed: {width}x{height}")
                logger.info(f"   💡 Screenshot saved at: {screenshot_path}")
                logger.info(f"   👁️  Open the screenshot to view VAs on desktop")

            except Exception as e:
                logger.error(f"   ❌ Error analyzing screenshot: {e}")
                result["error"] = str(e)
        else:
            result["analysis"] = {
                "note": "PIL not available. Screenshot saved for manual review.",
                "screenshot_path": str(screenshot_path)
            }
            logger.info(f"   💡 Screenshot saved at: {screenshot_path}")
            logger.info(f"   👁️  Open the screenshot to view VAs on desktop")

        # Check expected VA positions from positioning system
        try:
            from va_positioning_combat_system import VAPositioningCombatSystem
            positioning = VAPositioningCombatSystem(project_root=self.project_root)
            positions = positioning.get_positions()

            result["expected_positions"] = {}
            for va_id, pos in positions.items():
                if pos.is_active:
                    result["expected_positions"][va_id] = {
                        "x": pos.x,
                        "y": pos.y,
                        "window_size": pos.window_size,
                        "is_active": pos.is_active
                    }
                    result["vas_detected"].append(va_id)

            logger.info(f"   📍 Expected VA positions from positioning system:")
            for va_id, pos_data in result["expected_positions"].items():
                logger.info(f"      {va_id}: ({pos_data['x']}, {pos_data['y']})")

        except Exception as e:
            logger.debug(f"   Could not load positioning data: {e}")

        return result

    def examine_vas_realtime(self, interval: float = 5.0, count: int = 3) -> Dict[str, Any]:
        """
        Examine VAs on desktop in real-time (multiple captures)

        Args:
            interval: Seconds between captures
            count: Number of captures to take
        """
        logger.info("="*80)
        logger.info("👁️  Atlas RDP Manas View - Examining VAs on Desktop in Real-Time")
        logger.info("="*80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "examination_type": "Real-Time Desktop View",
            "captures": [],
            "vas_analysis": [],
            "success": True,
            "errors": []
        }

        logger.info(f"\n📸 Taking {count} desktop captures (interval: {interval}s)...")
        logger.info("")

        for i in range(count):
            logger.info(f"📸 Capture {i+1}/{count}...")
            try:
                screenshot_path = self.capture_desktop_view(f"VA Examination Capture {i+1}")
                if screenshot_path:
                    analysis = self.analyze_va_positions(screenshot_path)
                    result["captures"].append({
                        "capture_number": i + 1,
                        "screenshot_path": str(screenshot_path),
                        "analysis": analysis
                    })
                    logger.info(f"   ✅ Capture {i+1} complete")
                else:
                    result["errors"].append(f"Capture {i+1} failed")
                    logger.warning(f"   ⚠️  Capture {i+1} failed")

                if i < count - 1:  # Don't wait after last capture
                    logger.info(f"   ⏳ Waiting {interval}s before next capture...")
                    time.sleep(interval)

            except Exception as e:
                error_msg = f"Error in capture {i+1}: {e}"
                logger.error(f"   ❌ {error_msg}")
                result["errors"].append(error_msg)

        # Aggregate analysis
        if result["captures"]:
            all_vas = set()
            for capture in result["captures"]:
                analysis = capture.get("analysis", {})
                expected = analysis.get("expected_positions", {})
                all_vas.update(expected.keys())

            result["vas_analysis"] = [
                {
                    "va_id": va_id,
                    "detected_in_captures": sum(
                        1 for c in result["captures"]
                        if va_id in c.get("analysis", {}).get("expected_positions", {})
                    ),
                    "total_captures": len(result["captures"])
                }
                for va_id in all_vas
            ]

        # Save report
        report_file = self.data_dir / f"atlas_va_examination_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"   ✅ Report saved: {report_file.name}")
        except Exception as e:
            logger.error(f"❌ Error saving report: {e}")

        logger.info("="*80)
        logger.info("✅ Real-Time VA Examination Complete")
        logger.info(f"   Captures taken: {len(result['captures'])}")
        logger.info(f"   VAs detected: {len(result.get('vas_analysis', []))}")
        if result.get('errors'):
            logger.info(f"   Errors: {len(result['errors'])}")
        logger.info("")
        logger.info("👁️  Review screenshots to see VAs on desktop:")
        for i, capture in enumerate(result["captures"], 1):
            logger.info(f"   📸 Capture {i}: {capture.get('screenshot_path', 'N/A')}")
        logger.info("="*80)

        return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Atlas RDP Manas View - Examine VAs on Desktop")
    parser.add_argument("--realtime", action="store_true", help="Take multiple captures in real-time")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between captures (default: 5.0)")
    parser.add_argument("--count", type=int, default=3, help="Number of captures (default: 3)")
    parser.add_argument("--single", action="store_true", help="Take single screenshot")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("👁️  Atlas RDP Manas View - Examining VAs on Desktop")
    print("="*80 + "\n")

    examiner = AtlasExamineVAsDesktop()

    if args.realtime:
        result = examiner.examine_vas_realtime(interval=args.interval, count=args.count)

        print("\n" + "="*80)
        print("📊 EXAMINATION RESULTS")
        print("="*80)
        print(f"Captures taken: {len(result['captures'])}")
        print(f"VAs detected: {len(result.get('vas_analysis', []))}")
        print("")
        print("📸 Screenshots:")
        for i, capture in enumerate(result["captures"], 1):
            print(f"   {i}. {capture.get('screenshot_path', 'N/A')}")
        print("")
        if result.get('vas_analysis'):
            print("🤖 VAs Analysis:")
            for va in result['vas_analysis']:
                print(f"   {va['va_id']}: Detected in {va['detected_in_captures']}/{va['total_captures']} captures")
        print()

    elif args.single:
        screenshot_path = examiner.capture_desktop_view("Single VA Examination")
        if screenshot_path:
            analysis = examiner.analyze_va_positions(screenshot_path)
            print(f"\n✅ Screenshot captured: {screenshot_path}")
            print(f"   Open this file to view VAs on desktop")
            if analysis.get("expected_positions"):
                print("\n📍 Expected VA Positions:")
                for va_id, pos in analysis["expected_positions"].items():
                    print(f"   {va_id}: ({pos['x']}, {pos['y']})")
            print()
        else:
            print("\n❌ Screenshot capture failed")
            print()

    else:
        # Default: single capture
        screenshot_path = examiner.capture_desktop_view("VA Desktop Examination")
        if screenshot_path:
            analysis = examiner.analyze_va_positions(screenshot_path)
            print(f"\n✅ Screenshot captured: {screenshot_path}")
            print(f"   Open this file to view VAs on desktop")
            if analysis.get("expected_positions"):
                print("\n📍 Expected VA Positions:")
                for va_id, pos in analysis["expected_positions"].items():
                    print(f"   {va_id}: ({pos['x']}, {pos['y']})")
            print()
        else:
            print("\n❌ Screenshot capture failed")
            print()

    print("="*80)
    print("✅ Atlas VA Examination Complete")
    print("="*80 + "\n")
