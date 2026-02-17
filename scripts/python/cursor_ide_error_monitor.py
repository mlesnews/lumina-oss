#!/usr/bin/env python3
"""
Cursor IDE Error Monitor

Monitors Cursor IDE for ECONNRESET and other connection errors.
Records errors to health monitor and Star Trek protocol.

Tags: #CURSOR_IDE #ERROR_MONITORING #ECONNRESET #HEALTH_MONITORING @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

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

logger = get_logger("CursorIDEErrorMonitor")


class CursorIDEErrorMonitor:
    """
    Cursor IDE Error Monitor

    Monitors and records Cursor IDE connection errors.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Cursor IDE error monitor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize health monitor
        try:
            from cursor_connection_health_monitor import CursorConnectionHealthMonitor
            self.health_monitor = CursorConnectionHealthMonitor(self.project_root)
        except Exception as e:
            logger.error(f"   ❌ Could not initialize health monitor: {e}")
            self.health_monitor = None

        logger.info("✅ Cursor IDE Error Monitor initialized")

    def record_cursor_error(
        self,
        error_type: str,
        error_message: str,
        request_id: Optional[str] = None,
        stack_trace: Optional[str] = None
    ):
        """
        Record a Cursor IDE error

        Args:
            error_type: Type of error (e.g., "ConnectError", "ECONNRESET")
            error_message: Error message
            request_id: Request ID if available
            stack_trace: Stack trace if available
        """
        logger.warning("=" * 80)
        logger.warning("⚠️  CURSOR IDE ERROR DETECTED")
        logger.warning("=" * 80)
        logger.warning(f"   Error Type: {error_type}")
        logger.warning(f"   Error Message: {error_message}")
        if request_id:
            logger.warning(f"   Request ID: {request_id}")
        logger.warning("")

        # Determine error category
        error_lower = error_message.lower()
        if "econnreset" in error_lower or "connection reset" in error_lower:
            category = "ECONNRESET"
        elif "connecterror" in error_lower or "connect error" in error_lower:
            category = "ConnectError"
        elif "timeout" in error_lower:
            category = "Timeout"
        elif "aborted" in error_lower:
            category = "Aborted"
        else:
            category = "Other"

        # Create exception object for health monitor
        class CursorIDEException(Exception):
            pass

        error = CursorIDEException(f"{error_type}: {error_message}")

        # Record to health monitor
        if self.health_monitor:
            self.health_monitor.record_connection_attempt(
                success=False,
                error=error,
                retry_attempt=0,
                ai_service="Cursor IDE"
            )
            logger.info("   ✅ Error recorded to health monitor")

        # Log to Star Trek protocol
        try:
            from jarvis_star_trek_first_contact import JARVISStarTrekFirstContact

            first_contact = JARVISStarTrekFirstContact(self.project_root)

            ai_info = {
                "type": "cursor_ide_error",
                "error": error_message,
                "error_type": error_type,
                "request_id": request_id,
                "capabilities": ["IDE Integration", "AI Connection"]
            }

            encounter = first_contact.encounter_ai("cursor_ide", ai_info)
            logger.info("   🛸 Error logged to Star Trek protocol")
        except Exception as e:
            logger.debug(f"   Could not log to Star Trek protocol: {e}")

        return {
            "category": category,
            "recorded": True,
            "health_monitor": self.health_monitor is not None,
            "star_trek_logged": True
        }

    def parse_cursor_error(self, error_text: str) -> Dict[str, Any]:
        """
        Parse Cursor IDE error from text

        Args:
            error_text: Error text (from logs, console, etc.)

        Returns:
            Parsed error information
        """
        # Extract request ID
        request_id_match = re.search(r'Request ID: ([a-f0-9-]+)', error_text)
        request_id = request_id_match.group(1) if request_id_match else None

        # Extract error type
        error_type_match = re.search(r'(\w+Error):', error_text)
        error_type = error_type_match.group(1) if error_type_match else "UnknownError"

        # Extract error message
        error_message_match = re.search(r'(\w+Error):\s*(.+)', error_text, re.DOTALL)
        if error_message_match:
            error_message = error_message_match.group(2).strip()
        else:
            error_message = error_text.strip()

        # Extract stack trace
        stack_trace = None
        if "at " in error_text:
            stack_trace = error_text

        return {
            "error_type": error_type,
            "error_message": error_message,
            "request_id": request_id,
            "stack_trace": stack_trace
        }

    def record_from_text(self, error_text: str) -> Dict[str, Any]:
        """
        Record error from error text

        Args:
            error_text: Error text to parse and record

        Returns:
            Recording result
        """
        parsed = self.parse_cursor_error(error_text)

        return self.record_cursor_error(
            error_type=parsed["error_type"],
            error_message=parsed["error_message"],
            request_id=parsed["request_id"],
            stack_trace=parsed["stack_trace"]
        )


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Error Monitor")
        parser.add_argument("--record", type=str, help="Record error from text")
        parser.add_argument("--parse", type=str, help="Parse error text")
        parser.add_argument("--example", action="store_true", help="Record example error")

        args = parser.parse_args()

        monitor = CursorIDEErrorMonitor()

        if args.record:
            result = monitor.record_from_text(args.record)
            print(json.dumps(result, indent=2, default=str))

        elif args.parse:
            parsed = monitor.parse_cursor_error(args.parse)
            print(json.dumps(parsed, indent=2, default=str))

        elif args.example:
            # Record example error
            example_error = """Request ID: 803599a2-0d20-4cfc-a229-82b3d99a0bc9
ConnectError: [aborted] read ECONNRESET
    at oou.$streamAiConnect (vscode-file://vscode-app/c:/Program%20Files/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:12706:472564)"""

            result = monitor.record_from_text(example_error)
            print(json.dumps(result, indent=2, default=str))

        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":


    main()