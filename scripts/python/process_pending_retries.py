#!/usr/bin/env python3
"""
Process Pending Retries - NAS KronScheduler Integration

Automatically processes all pending retries from the retry tracking system.
Scans for failed requests and automatically retries them.

Tags: #RETRY_MANAGER #AUTOMATIC_RETRY #NAS_KRONSCHEDULER @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

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

logger = get_logger("ProcessPendingRetries")


class ProcessPendingRetries:
    """Process pending retries automatically"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize retry processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cursor_retry_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.retries_file = self.data_dir / "pending_retries.json"
        self.processed_file = self.data_dir / "processed_retries.jsonl"

        logger.info("✅ Process Pending Retries initialized")

    def load_pending_retries(self) -> List[Dict[str, Any]]:
        """Load pending retries"""
        if not self.retries_file.exists():
            return []

        try:
            with open(self.retries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "pending_retries" in data:
                    return data["pending_retries"]
                return []
        except Exception as e:
            logger.error(f"Error loading pending retries: {e}")
            return []

    def save_pending_retries(self, retries: List[Dict[str, Any]]):
        """Save pending retries"""
        try:
            with open(self.retries_file, 'w', encoding='utf-8') as f:
                json.dump({"pending_retries": retries, "last_updated": datetime.now().isoformat()}, 
                         f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving pending retries: {e}")

    def log_processed_retry(self, retry_data: Dict[str, Any], result: Dict[str, Any]):
        """Log processed retry"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "retry_data": retry_data,
                "result": result
            }
            with open(self.processed_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, default=str) + '\n')
        except Exception as e:
            logger.error(f"Error logging processed retry: {e}")

    def process_retry(self, retry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single retry"""
        request_id = retry_data.get("request_id")
        if not request_id:
            return {"success": False, "error": "No request_id provided"}

        try:
            from cursor_retry_with_request_id import CursorRetryWithRequestID
            manager = CursorRetryWithRequestID(self.project_root)

            result = manager.handle_retry_with_request_id(
                request_id=request_id,
                original_error=retry_data.get("error"),
                operator=retry_data.get("operator", "@OP")
            )

            return {
                "success": True,
                "request_id": request_id,
                "result": result
            }
        except Exception as e:
            logger.error(f"Error processing retry for {request_id}: {e}")
            return {
                "success": False,
                "request_id": request_id,
                "error": str(e)
            }

    def process_all_pending(self, max_retries: int = 10) -> Dict[str, Any]:
        """Process all pending retries"""
        logger.info("=" * 80)
        logger.info("🔄 PROCESSING PENDING RETRIES")
        logger.info("=" * 80)
        logger.info("")

        pending = self.load_pending_retries()

        if not pending:
            logger.info("✅ No pending retries found")
            return {
                "processed": 0,
                "succeeded": 0,
                "failed": 0,
                "remaining": 0
            }

        logger.info(f"📋 Found {len(pending)} pending retries")
        logger.info("")

        processed = []
        succeeded = 0
        failed = 0

        for i, retry_data in enumerate(pending[:max_retries], 1):
            request_id = retry_data.get("request_id", "unknown")
            logger.info(f"[{i}/{min(len(pending), max_retries)}] Processing: {request_id}")

            result = self.process_retry(retry_data)

            if result.get("success"):
                succeeded += 1
                logger.info(f"   ✅ Success: {request_id}")
            else:
                failed += 1
                logger.warning(f"   ❌ Failed: {request_id} - {result.get('error', 'Unknown error')}")
                # Keep failed retries for next attempt
                processed.append(retry_data)

            self.log_processed_retry(retry_data, result)
            logger.info("")

        # Save remaining pending retries
        remaining = pending[max_retries:] + [r for r in processed if not any(
            r.get("request_id") == p.get("request_id") for p in pending[:max_retries] if p.get("request_id")
        )]
        self.save_pending_retries(remaining)

        logger.info("=" * 80)
        logger.info("✅ PROCESSING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Processed: {min(len(pending), max_retries)}")
        logger.info(f"   Succeeded: {succeeded}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"   Remaining: {len(remaining)}")
        logger.info("")

        return {
            "processed": min(len(pending), max_retries),
            "succeeded": succeeded,
            "failed": failed,
            "remaining": len(remaining)
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Process Pending Retries")
        parser.add_argument("--max-retries", type=int, default=10, help="Maximum retries to process")

        args = parser.parse_args()

        processor = ProcessPendingRetries()
        result = processor.process_all_pending(max_retries=args.max_retries)

        print(json.dumps(result, indent=2, default=str))
        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())