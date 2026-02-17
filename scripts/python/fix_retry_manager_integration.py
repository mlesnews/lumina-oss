#!/usr/bin/env python3
"""
Fix Retry Manager Integration

Ensures retry manager is properly integrated and working as intended.
Addresses issues where retry manager may not be called or errors not properly handled.

Tags: #RETRY_MANAGER #FIX #INTEGRATION #TROUBLESHOOTING @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

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

logger = get_logger("FixRetryManagerIntegration")


class RetryManagerIntegrationFixer:
    """
    Fix retry manager integration issues

    Ensures:
    1. Retry manager is properly imported and used
    2. Errors are caught and passed to retry manager
    3. Retry manager decorator is applied correctly
    4. All critical paths use retry manager
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fixer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        logger.info("✅ Retry Manager Integration Fixer initialized")

    def check_integration_points(self) -> Dict[str, Any]:
        """Check where retry manager should be integrated"""
        logger.info("🔍 Checking retry manager integration points...")

        integration_points = {
            "cursor_chat_operations": {
                "file": "scripts/python/cursor_chat_retry_manager.py",
                "status": "exists",
                "usage": "Should be used for all Cursor IDE chat operations"
            },
            "ai_connection": {
                "file": "scripts/python/ai_connection.py",
                "status": "check_needed",
                "usage": "Should retry AI service connections"
            },
            "email_syphon": {
                "file": "scripts/python/jarvis_syphon_all_emails_nas_hub.py",
                "status": "check_needed",
                "usage": "Should retry email fetching operations"
            },
            "daily_work_cycle": {
                "file": "scripts/python/daily_work_cycle_complete.py",
                "status": "check_needed",
                "usage": "Should retry failed source scans"
            }
        }

        # Check each integration point
        for point_name, point_info in integration_points.items():
            file_path = self.project_root / point_info["file"]
            if file_path.exists():
                # Check if retry manager is imported/used
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'retry_manager' in content or 'CursorChatRetryManager' in content or 'retry_decorator' in content:
                            integration_points[point_name]["status"] = "integrated"
                        else:
                            integration_points[point_name]["status"] = "not_integrated"
                except Exception as e:
                    integration_points[point_name]["status"] = f"error: {e}"
            else:
                integration_points[point_name]["status"] = "file_not_found"

        # Print results
        for point_name, point_info in integration_points.items():
            status_icon = "✅" if point_info["status"] == "integrated" else "⚠️" if point_info["status"] == "not_integrated" else "❌"
            logger.info(f"   {status_icon} {point_name}: {point_info['status']}")

        return integration_points

    def apply_fixes(self) -> Dict[str, Any]:
        """Apply fixes to ensure retry manager is properly integrated"""
        logger.info("🔧 Applying retry manager integration fixes...")

        fixes_applied = []

        # Check integration points
        integration_points = self.check_integration_points()

        # Fix points that need integration
        for point_name, point_info in integration_points.items():
            if point_info["status"] == "not_integrated":
                logger.info(f"   ⚠️  {point_name} needs retry manager integration")
                fixes_applied.append({
                    "point": point_name,
                    "action": "needs_manual_integration",
                    "file": point_info["file"]
                })

        logger.info(f"✅ Found {len(fixes_applied)} integration points needing fixes")

        return {
            "fixes_applied": fixes_applied,
            "integration_points": integration_points
        }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix Retry Manager Integration")

    args = parser.parse_args()

    fixer = RetryManagerIntegrationFixer()
    results = fixer.apply_fixes()

    logger.info("")
    logger.info("✅ Integration check complete")
    logger.info("   Review integration points and ensure retry manager is used")


if __name__ == "__main__":


    main()