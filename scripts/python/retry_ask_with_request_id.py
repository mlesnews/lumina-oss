#!/usr/bin/env python3
"""
Retry @ask with Request ID - @bau Workflow

Retries the original @ask directive that was tied to a Request ID.
Always executes as @bau (Business As Usual) workflow.

Tags: #BAU #RETRY #@ASK #REQUEST_ID @JARVIS @LUMINA
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RetryAskWithRequestID")


class AskRequestTracker:
    """
    Tracks @ask directives with Request IDs for retry capability
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Ask Request Tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.tracking_dir = self.project_root / "data" / "ask_tracking"
        self.tracking_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Ask Request Tracker initialized")
        logger.info(f"   Tracking directory: {self.tracking_dir}")

    def track_ask_with_request_id(
        self,
        ask_text: str,
        request_id: str,
        source: str = "user",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track an @ask directive with its Request ID

        Args:
            ask_text: The original @ask directive text
            request_id: The Request ID associated with this @ask
            source: Source of the @ask
            context: Additional context

        Returns:
            Tracking entry dictionary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ask_request_{request_id}_{timestamp}.json"
        filepath = self.tracking_dir / filename

        entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "ask_text": ask_text,
            "source": source,
            "status": "tracked",
            "retry_count": 0,
            "last_retry": None,
            "context": context or {},
            "tags": ["#BAU", "#RETRY", "@ASK", "#REQUEST_ID", "@JARVIS", "@LUMINA"]
        }

        # Save tracking entry
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ @ask tracked with Request ID: {request_id}")
        logger.info(f"   Ask text: {ask_text[:100]}...")

        return entry

    def get_ask_by_request_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        try:
            """
            Get the original @ask directive by Request ID

            Args:
                request_id: The Request ID to look up

            Returns:
                Tracking entry if found, None otherwise
            """
            pattern = f"ask_request_{request_id}_*.json"
            files = list(self.tracking_dir.glob(pattern))

            if not files:
                logger.warning(f"   ⚠️  No @ask found for Request ID: {request_id}")
                return None

            # Get most recent entry
            latest_file = max(files, key=lambda p: p.stat().st_mtime)

            with open(latest_file, 'r', encoding='utf-8') as f:
                entry = json.load(f)

            logger.info(f"   ✅ Found @ask for Request ID: {request_id}")
            logger.info(f"   Ask text: {entry.get('ask_text', '')[:100]}...")

            return entry

        except Exception as e:
            self.logger.error(f"Error in get_ask_by_request_id: {e}", exc_info=True)
            raise
    def retry_ask_as_bau(
        self,
        request_id: str,
        ask_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retry an @ask directive as @bau

        Args:
            request_id: The Request ID to retry
            ask_text: Optional ask text (if not provided, will look up)

        Returns:
            Retry result dictionary
        """
        logger.info(f"🔄 Retrying @ask as @bau for Request ID: {request_id}")

        # Get original @ask if not provided
        if ask_text is None:
            entry = self.get_ask_by_request_id(request_id)
            if entry is None:
                return {
                    "success": False,
                    "error": f"No @ask found for Request ID: {request_id}",
                    "request_id": request_id
                }
            ask_text = entry.get("ask_text", "")

        # Update retry count
        pattern = f"ask_request_{request_id}_*.json"
        files = list(self.tracking_dir.glob(pattern))
        if files:
            latest_file = max(files, key=lambda p: p.stat().st_mtime)
            with open(latest_file, 'r', encoding='utf-8') as f:
                entry = json.load(f)

            entry["retry_count"] = entry.get("retry_count", 0) + 1
            entry["last_retry"] = datetime.now().isoformat()
            entry["status"] = "retrying_as_bau"

            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(entry, f, indent=2, ensure_ascii=False)

        result = {
            "success": True,
            "request_id": request_id,
            "ask_text": ask_text,
            "retry_count": entry.get("retry_count", 1),
            "workflow": "@bau",
            "timestamp": datetime.now().isoformat(),
            "status": "ready_for_execution"
        }

        logger.info(f"   ✅ @ask ready for retry as @bau")
        logger.info(f"   Ask text: {ask_text[:100]}...")
        logger.info(f"   Retry count: {result['retry_count']}")

        return result


def retry_ask_with_request_id(request_id: str) -> Dict[str, Any]:
    """
    Retry @ask directive with Request ID as @bau

    Args:
        request_id: The Request ID to retry

    Returns:
        Retry result dictionary
    """
    tracker = AskRequestTracker(project_root=project_root)
    result = tracker.retry_ask_as_bau(request_id)

    if result.get("success"):
        logger.info(f"\n✅ @ask retry prepared as @bau")
        logger.info(f"   Request ID: {request_id}")
        logger.info(f"   Ask text: {result.get('ask_text', '')[:200]}")
        logger.info(f"\n📋 Next step: Execute the @ask as @bau:")
        logger.info(f"   @bau {result.get('ask_text', '')}")
    else:
        logger.error(f"\n❌ Failed to retry @ask")
        logger.error(f"   Error: {result.get('error', 'Unknown error')}")

    return result


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="Retry @ask directive with Request ID as @bau"
        )
        parser.add_argument(
            "request_id",
            help="Request ID to retry"
        )
        parser.add_argument(
            "--ask-text",
            help="Optional ask text (if not provided, will look up)"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results as JSON"
        )

        args = parser.parse_args()

        tracker = AskRequestTracker(project_root=project_root)
        result = tracker.retry_ask_as_bau(args.request_id, args.ask_text)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print(f"\n🔄 @ask Retry as @bau")
                print("=" * 60)
                print(f"Request ID: {result['request_id']}")
                print(f"Retry Count: {result['retry_count']}")
                print(f"Status: {result['status']}")
                print(f"\n@ask Text:")
                print(f"  {result['ask_text']}")
                print(f"\n📋 Execute as @bau:")
                print(f"  @bau {result['ask_text']}")
            else:
                print(f"\n❌ Failed to retry @ask")
                print(f"Error: {result.get('error', 'Unknown error')}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()