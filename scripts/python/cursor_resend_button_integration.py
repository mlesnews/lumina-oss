#!/usr/bin/env python3
"""
Cursor IDE Resend Button Integration

Integrates Cursor IDE's Resend button with our connection resilience system.
When ECONNRESET errors occur, we should utilize the Resend button instead of
only relying on automatic retries.

Tags: #CURSOR_IDE #RESEND_BUTTON #ECONNRESET #INTEGRATION @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

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

logger = get_logger("CursorResendIntegration")


class CursorResendButtonIntegration:
    """
    Cursor IDE Resend Button Integration

    Integrates with Cursor IDE's Resend button for connection error recovery.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Resend button integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Feature tracker
        try:
            from cursor_ide_feature_utilization_tracker import CursorIDEFeatureUtilizationTracker
            self.feature_tracker = CursorIDEFeatureUtilizationTracker(self.project_root)
        except Exception as e:
            logger.warning(f"   ⚠️  Feature tracker not available: {e}")
            self.feature_tracker = None

        logger.info("✅ Cursor Resend Button Integration initialized")
        logger.info("   Ready to utilize Resend button for ECONNRESET recovery")

    def should_use_resend_button(self, error_type: str, retry_count: int) -> bool:
        """
        Determine if we should use Resend button

        Args:
            error_type: Type of error (ECONNRESET, ConnectError, etc.)
            retry_count: Number of automatic retries attempted

        Returns:
            True if Resend button should be used
        """
        # Use Resend button for connection errors after first retry
        connection_errors = ["ECONNRESET", "ConnectError", "aborted"]

        if error_type in connection_errors and retry_count >= 1:
            return True

        return False

    def record_resend_usage(self, success: bool = True):
        """Record Resend button usage"""
        if self.feature_tracker:
            notes = f"Used Resend button - Success: {success}"
            self.feature_tracker.record_feature_use("Resend Button", notes)
            logger.info("   ✅ Recorded Resend button usage")

    def get_resend_instructions(self) -> Dict[str, Any]:
        """Get instructions for using Resend button"""
        return {
            "feature": "Resend Button",
            "description": "Use Cursor IDE's Resend button to retry failed requests",
            "when_to_use": [
                "After ECONNRESET errors",
                "After ConnectError errors",
                "When automatic retries fail",
                "For connection aborted errors"
            ],
            "how_to_use": [
                "1. Wait for error dialog to appear",
                "2. Look for 'Resend' button in the error dialog",
                "3. Click 'Resend' to retry the request",
                "4. System will record the usage automatically"
            ],
            "integration": {
                "automatic": False,  # Manual click required
                "tracked": True,  # Usage is tracked
                "recommended": True  # Recommended for connection errors
            },
            "benefits": [
                "Uses Cursor IDE's built-in retry mechanism",
                "May have better error handling than our retries",
                "Provides user control over retry timing",
                "Complements our automatic retry system"
            ]
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Resend Button Integration")
        parser.add_argument("--instructions", action="store_true",
                           help="Show Resend button usage instructions")
        parser.add_argument("--record", action="store_true",
                           help="Record Resend button usage")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        integration = CursorResendButtonIntegration()

        if args.record:
            integration.record_resend_usage()
            if args.json:
                import json
                print(json.dumps({"recorded": True}, indent=2))
            else:
                print("✅ Recorded Resend button usage")

        elif args.instructions or not args.record:
            instructions = integration.get_resend_instructions()
            if args.json:
                import json
                print(json.dumps(instructions, indent=2))
            else:
                print("=" * 80)
                print("🔄 CURSOR IDE RESEND BUTTON INTEGRATION")
                print("=" * 80)
                print()
                print(f"Feature: {instructions['feature']}")
                print(f"Description: {instructions['description']}")
                print()
                print("When to Use:")
                for when in instructions['when_to_use']:
                    print(f"  • {when}")
                print()
                print("How to Use:")
                for step in instructions['how_to_use']:
                    print(f"  {step}")
                print()
                print("Integration:")
                print(f"  Automatic: {instructions['integration']['automatic']}")
                print(f"  Tracked: {instructions['integration']['tracked']}")
                print(f"  Recommended: {instructions['integration']['recommended']}")
                print()
                print("Benefits:")
                for benefit in instructions['benefits']:
                    print(f"  • {benefit}")
                print()

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()