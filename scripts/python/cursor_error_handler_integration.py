#!/usr/bin/env python3
"""
Cursor IDE Error Handler Integration
Automatic retry manager trigger for Cursor IDE errors

Handles:
- ConnectError (including serialize binary errors)
- ECONNRESET
- Timeout errors
- Internal Cursor IDE errors

Tags: #CURSOR_IDE #ERROR_HANDLING #RETRY #AUTOMATION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorErrorHandlerIntegration")


class CursorErrorHandlerIntegration:
    """
    Automatic error handler integration for Cursor IDE

    Automatically triggers retry manager for:
    - ConnectError (including serialize binary errors)
    - ECONNRESET
    - Timeout errors
    - Internal Cursor IDE errors
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize error handler integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cursor_error_handling"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Import retry managers
        try:
            from cursor_connection_resilience import CursorConnectionResilience
            from cursor_chat_retry_manager import CursorChatRetryManager

            self.connection_resilience = CursorConnectionResilience(max_retries=5, retry_delay=3.0)
            self.retry_manager = CursorChatRetryManager(max_retries=5, initial_delay=2.0, max_delay=15.0)

            logger.info("✅ Cursor Error Handler Integration initialized")
            logger.info("   🔄 Retry managers: Active")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not initialize retry managers: {e}")
            self.connection_resilience = None
            self.retry_manager = None

    def handle_cursor_error(self, error: Exception, request_id: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Handle Cursor IDE error with automatic retry

        Args:
            error: The error exception
            request_id: Request ID (if available)
            context: Additional context

        Returns:
            Error handling result
        """
        logger.info("=" * 80)
        logger.info("🔧 CURSOR IDE ERROR HANDLER")
        logger.info("=" * 80)
        logger.info("")

        error_str = str(error)
        error_type = type(error).__name__

        logger.warning(f"   ⚠️  Error Type: {error_type}")
        logger.warning(f"   ⚠️  Error: {error_str}")
        if request_id:
            logger.warning(f"   📋 Request ID: {request_id}")
        logger.info("")

        result = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_str,
            "request_id": request_id,
            "retry_triggered": False,
            "retry_successful": False,
            "handling_result": {}
        }

        # Check if it's a connection error that should trigger retry
        if self.connection_resilience:
            is_conn_error = self.connection_resilience.is_connection_error(error)

            if is_conn_error:
                logger.info("   ✅ Connection error detected - triggering retry manager")
                result["retry_triggered"] = True

                # Handle with connection resilience
                handling = self.connection_resilience.handle_connection_error(error, 1)
                result["handling_result"] = handling

                logger.info(f"   📊 Category: {handling.get('category')}")
                logger.info(f"   🔄 Action: {handling.get('action')}")
            else:
                logger.info("   ℹ️  Not a connection error - no retry triggered")

        # Save error record
        error_file = self.data_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"   📄 Error record saved: {error_file.name}")
        logger.info("")

        return result

    def process_error_from_request_id(self, request_id: str) -> Dict[str, Any]:
        """
        Process error from request ID

        Args:
            request_id: Cursor IDE request ID

        Returns:
            Processing result
        """
        logger.info("=" * 80)
        logger.info(f"🔍 PROCESSING ERROR FOR REQUEST ID: {request_id}")
        logger.info("=" * 80)
        logger.info("")

        # Create a ConnectError exception for this request
        error = Exception(f"ConnectError: [internal] serialize binary: invalid int 32: 4294967295 (Request ID: {request_id})")

        return self.handle_cursor_error(error, request_id=request_id)


def auto_retry_on_cursor_error(func):
    """
    Decorator to automatically retry on Cursor IDE errors

    Usage:
        @auto_retry_on_cursor_error
        def send_cursor_message(message):
            ...
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        integration = CursorErrorHandlerIntegration()
        retry_manager = integration.retry_manager

        if retry_manager:
            return retry_manager.retry(func, *args, **kwargs)
        else:
            # Fallback: try once
            return func(*args, **kwargs)

    return wrapper


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor IDE Error Handler Integration")
    parser.add_argument("--request-id", help="Process error for specific request ID")
    parser.add_argument("--test", action="store_true", help="Test error handling")

    args = parser.parse_args()

    integration = CursorErrorHandlerIntegration()

    if args.request_id:
        integration.process_error_from_request_id(args.request_id)
    elif args.test:
        # Test with the specific error
        test_error = Exception("ConnectError: [internal] serialize binary: invalid int 32: 4294967295")
        integration.handle_cursor_error(test_error, request_id="test-request-id")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())