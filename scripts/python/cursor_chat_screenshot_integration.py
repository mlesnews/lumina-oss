#!/usr/bin/env python3
"""
Cursor IDE Chat Screenshot Integration
Automatically captures and attaches screenshots when errors are mentioned in chat
Similar to OpenAI Atlas - automatic visual context capture
#JARVIS #CURSOR #CHAT #SCREENSHOT #AUTOMATION
"""

import sys
import re
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture
    RDP_CAPTURE_AVAILABLE = True
except ImportError:
    RDP_CAPTURE_AVAILABLE = False
    logging.warning("MANUS RDP Screenshot Capture not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CursorChatScreenshotIntegration:
    """
    Cursor IDE Chat Screenshot Integration
    Automatically captures screenshots when errors are mentioned
    """

    # Error keywords that trigger screenshot capture
    ERROR_KEYWORDS = [
        r'\berror\b',
        r'\bfailed\b',
        r'\bfailure\b',
        r'\bincorrect\b',
        r'\bwrong\b',
        r'\bnot working\b',
        r'\bdoesn\'?t work\b',
        r'\bissue\b',
        r'\bproblem\b',
        r'\bbug\b',
        r'\bexception\b',
        r'\bcrash\b',
        r'\btimeout\b',
        r'\bauthentication.*fail',
        r'\bauth.*error',
        r'\bconnection.*fail',
        r'\bcan\'?t.*connect',
        r'\bunable.*to',
        r'\bscreenshot\b',
        r'\bcapture\b',
        r'\bshow.*me\b',
        r'\bsee.*error\b',
    ]

    # Phrases that explicitly request screenshots
    SCREENSHOT_REQUEST_PHRASES = [
        r'screenshot',
        r'capture.*screen',
        r'show.*screen',
        r'take.*picture',
        r'snap.*shot',
        r'what.*see',
        r'what.*showing',
    ]

    def __init__(self, auto_capture: bool = True, rdp_ip: str = "<NAS_IP>"):
        """
        Initialize Cursor chat screenshot integration

        Args:
            auto_capture: Automatically capture on error detection
            rdp_ip: RDP server IP for capture
        """
        self.auto_capture = auto_capture
        self.rdp_capture = None
        self.recent_captures: List[Dict[str, Any]] = []

        if RDP_CAPTURE_AVAILABLE:
            try:
                self.rdp_capture = MANUSRDPScreenshotCapture(manus_ip=rdp_ip)
                logger.info("✅ Cursor Chat Screenshot Integration initialized")
            except Exception as e:
                logger.warning(f"RDP capture initialization failed: {e}")
        else:
            logger.warning("RDP capture not available")

    def analyze_message(self, message: str) -> Dict[str, Any]:
        """
        Analyze chat message for error mentions or screenshot requests

        Args:
            message: Chat message text

        Returns:
            Dict with analysis results and suggested actions
        """
        message_lower = message.lower()

        # Check for explicit screenshot requests
        screenshot_requested = any(
            re.search(phrase, message_lower, re.IGNORECASE)
            for phrase in self.SCREENSHOT_REQUEST_PHRASES
        )

        # Check for error keywords
        error_detected = any(
            re.search(keyword, message_lower, re.IGNORECASE)
            for keyword in self.ERROR_KEYWORDS
        )

        # Determine action
        should_capture = False
        capture_reason = None

        if screenshot_requested:
            should_capture = True
            capture_reason = "Explicit screenshot request"
        elif error_detected and self.auto_capture:
            should_capture = True
            capture_reason = "Error detected in message"

        return {
            "should_capture": should_capture,
            "capture_reason": capture_reason,
            "error_detected": error_detected,
            "screenshot_requested": screenshot_requested,
            "message": message
        }

    def capture_for_chat(self, context: str = "Cursor chat error") -> Optional[Dict[str, Any]]:
        """
        Capture screenshot for chat attachment

        Args:
            context: Description of what's being captured

        Returns:
            Dict with screenshot path and metadata, or None if failed
        """
        if not self.rdp_capture:
            logger.warning("RDP capture not available")
            return None

        try:
            # Capture with context
            metadata = self.rdp_capture.capture_with_context(context, auto_capture=True)

            screenshot_path = metadata.get("screenshot_path")
            if screenshot_path and Path(screenshot_path).exists():
                capture_info = {
                    "screenshot_path": screenshot_path,
                    "metadata_path": None,
                    "timestamp": metadata.get("timestamp"),
                    "context": context,
                    "ready_for_attachment": True
                }

                # Find metadata file
                metadata_file = Path(screenshot_path).parent / f"metadata_{Path(screenshot_path).stem.split('_')[-1]}.json"
                if metadata_file.exists():
                    capture_info["metadata_path"] = str(metadata_file)

                # Add to recent captures
                self.recent_captures.append(capture_info)
                if len(self.recent_captures) > 10:
                    self.recent_captures.pop(0)  # Keep last 10

                logger.info(f"✅ Screenshot captured for chat: {screenshot_path}")
                return capture_info
            else:
                logger.warning("Screenshot capture returned no path")
                return None

        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

    def get_latest_screenshot(self) -> Optional[Dict[str, Any]]:
        """Get the most recent screenshot capture"""
        if self.recent_captures:
            return self.recent_captures[-1]
        return None

    def get_screenshots_for_context(self, context_keyword: str) -> List[Dict[str, Any]]:
        """
        Get screenshots matching a context keyword

        Args:
            context_keyword: Keyword to search in context descriptions

        Returns:
            List of matching screenshot captures
        """
        keyword_lower = context_keyword.lower()
        matches = [
            capture for capture in self.recent_captures
            if keyword_lower in capture.get("context", "").lower()
        ]
        return matches


def process_chat_message(message: str, auto_capture: bool = True) -> Dict[str, Any]:
    """
    Process a chat message and capture screenshot if needed

    Args:
        message: Chat message text
        auto_capture: Automatically capture on error detection

    Returns:
        Dict with analysis and capture results
    """
    integration = CursorChatScreenshotIntegration(auto_capture=auto_capture)

    # Analyze message
    analysis = integration.analyze_message(message)

    result = {
        "analysis": analysis,
        "screenshot": None,
        "screenshot_path": None
    }

    # Capture if needed
    if analysis["should_capture"]:
        context = f"Cursor chat: {analysis['capture_reason']}"
        screenshot_info = integration.capture_for_chat(context)

        if screenshot_info:
            result["screenshot"] = screenshot_info
            result["screenshot_path"] = screenshot_info.get("screenshot_path")
            result["message"] = f"✅ Screenshot captured automatically: {screenshot_info.get('screenshot_path')}"
        else:
            result["message"] = "⚠️ Screenshot capture attempted but failed"
    else:
        result["message"] = "ℹ️ No screenshot capture needed"

    return result


def main():
    """CLI interface for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor Chat Screenshot Integration")
    parser.add_argument("--message", help="Chat message to analyze")
    parser.add_argument("--auto-capture", action="store_true", default=True, help="Auto-capture on error")
    parser.add_argument("--test", action="store_true", help="Run test scenarios")
    args = parser.parse_args()

    print("=" * 70)
    print("   CURSOR CHAT SCREENSHOT INTEGRATION")
    print("=" * 70)
    print("")

    if args.test:
        print("🧪 Running test scenarios...")
        print("")

        test_messages = [
            "I'm getting an error",
            "Authentication failed",
            "Can you take a screenshot?",
            "The connection doesn't work",
            "Show me what you see",
            "This is working fine",
        ]

        for msg in test_messages:
            print(f"Message: '{msg}'")
            result = process_chat_message(msg, auto_capture=args.auto_capture)
            analysis = result["analysis"]
            print(f"  Error detected: {analysis['error_detected']}")
            print(f"  Screenshot requested: {analysis['screenshot_requested']}")
            print(f"  Should capture: {analysis['should_capture']}")
            if result["screenshot_path"]:
                print(f"  ✅ Screenshot: {result['screenshot_path']}")
            print("")

        return 0

    if args.message:
        print(f"Analyzing message: '{args.message}'")
        print("")
        result = process_chat_message(args.message, auto_capture=args.auto_capture)

        analysis = result["analysis"]
        print("Analysis:")
        print(f"  Error detected: {analysis['error_detected']}")
        print(f"  Screenshot requested: {analysis['screenshot_requested']}")
        print(f"  Should capture: {analysis['should_capture']}")
        if analysis["should_capture"]:
            print(f"  Reason: {analysis['capture_reason']}")
        print("")

        if result["screenshot_path"]:
            print(f"✅ {result['message']}")
            print(f"   Path: {result['screenshot_path']}")
            print("")
            print("💡 This screenshot can now be attached to Cursor chat")
        else:
            print(f"ℹ️  {result['message']}")

        return 0

    print("Usage:")
    print("  --message 'your message'  - Analyze a chat message")
    print("  --test                    - Run test scenarios")
    print("")
    print("Example:")
    print("  python cursor_chat_screenshot_integration.py --message 'I'm getting an error'")
    print("")

    return 0


if __name__ == "__main__":


    sys.exit(main())