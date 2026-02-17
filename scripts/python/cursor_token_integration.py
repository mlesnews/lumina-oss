#!/usr/bin/env python3
"""
Cursor Token Integration
========================

Monitors Cursor IDE for token usage and integrates with Token Usage Monitor.

Tracks:
- API requests to AI models
- Token counts from responses
- Local vs Cloud model usage
- Request duration
"""

import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import sys

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from token_usage_monitor import TokenUsageMonitor
    from cursor_active_model_tracker import CursorActiveModelTracker
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorTokenIntegration")


class CursorTokenIntegration:
    """Integrate Cursor IDE token usage with monitor."""

    def __init__(self):
        """Initialize Cursor token integration."""
        self.monitor = TokenUsageMonitor()
        self.model_tracker = CursorActiveModelTracker()

        # Cursor paths
        self.cursor_log_paths = [
            Path.home() / "AppData" / "Roaming" / "Cursor" / "logs",
            Path.home() / ".cursor" / "logs",
        ]

        # Track last processed request
        self.last_request_id = None
        self.request_cache = {}

    def _find_cursor_logs(self) -> Optional[Path]:
        try:
            """Find Cursor log directory."""
            for log_path in self.cursor_log_paths:
                if log_path.exists():
                    return log_path
            return None

        except Exception as e:
            self.logger.error(f"Error in _find_cursor_logs: {e}", exc_info=True)
            raise
    def _parse_cursor_request(self, log_line: str) -> Optional[Dict]:
        """Parse Cursor log line for token usage."""
        # Look for patterns like:
        # - "tokens": 1234
        # - "usage": {"prompt_tokens": 100, "completion_tokens": 200}
        # - Request ID patterns

        tokens_pattern = r'"tokens":\s*(\d+)'
        usage_pattern = r'"usage":\s*\{[^}]*"prompt_tokens":\s*(\d+)[^}]*"completion_tokens":\s*(\d+)'
        request_id_pattern = r'request[_-]?id["\']?\s*[:=]\s*["\']?([a-f0-9-]+)'

        tokens_match = re.search(tokens_pattern, log_line, re.IGNORECASE)
        usage_match = re.search(usage_pattern, log_line, re.IGNORECASE)
        request_id_match = re.search(request_id_pattern, log_line, re.IGNORECASE)

        if tokens_match or usage_match:
            request_id = request_id_match.group(1) if request_id_match else None

            if usage_match:
                prompt_tokens = int(usage_match.group(1))
                completion_tokens = int(usage_match.group(2))
                total_tokens = prompt_tokens + completion_tokens
            elif tokens_match:
                total_tokens = int(tokens_match.group(1))
            else:
                return None

            return {
                "request_id": request_id,
                "tokens": total_tokens,
                "timestamp": datetime.now().isoformat()
            }

        return None

    def _determine_if_local(self, model_name: str) -> bool:
        """Determine if model is local based on name/endpoint."""
        model_lower = model_name.lower()

        # Local indicators
        local_indicators = [
            "localhost",
            "127.0.0.1",
            "ollama",
            "local",
            "iron-legion",
            "ultron",
            "kaiju"
        ]

        # Check model tracker for endpoint
        model_details = self.model_tracker.get_active_model()
        endpoint = model_details.get("endpoint", "")

        if any(indicator in model_lower or indicator in endpoint.lower() for indicator in local_indicators):
            return True

        # Cloud indicators
        cloud_indicators = [
            "openai.com",
            "anthropic.com",
            "api.openai",
            "api.anthropic"
        ]

        if any(indicator in endpoint.lower() for indicator in cloud_indicators):
            return False

        # Default: assume local if endpoint is localhost-like
        return "localhost" in endpoint or "127.0.0.1" in endpoint or not endpoint

    def process_cursor_activity(self):
        """Process Cursor activity and record token usage."""
        log_dir = self._find_cursor_logs()
        if not log_dir:
            logger.warning("Could not find Cursor log directory")
            return

        # Get current model
        model_details = self.model_tracker.get_active_model()
        model_name = model_details.get("name", "unknown")
        is_local = self._determine_if_local(model_name)

        # Look for recent log files
        log_files = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)

        if not log_files:
            return

        # Process most recent log file
        latest_log = log_files[0]

        try:
            with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                # Read last 100 lines
                lines = f.readlines()[-100:]

                for line in lines:
                    request_data = self._parse_cursor_request(line)
                    if request_data:
                        request_id = request_data.get("request_id")
                        tokens = request_data.get("tokens", 0)

                        # Avoid duplicate processing
                        if request_id and request_id in self.request_cache:
                            continue

                        if request_id:
                            self.request_cache[request_id] = datetime.now()
                            # Clean old cache entries (older than 1 hour)
                            cutoff = datetime.now().timestamp() - 3600
                            self.request_cache = {
                                k: v for k, v in self.request_cache.items()
                                if v.timestamp() > cutoff
                            }

                        if tokens > 0:
                            # Record usage
                            self.monitor.record_usage(
                                tokens=tokens,
                                is_local=is_local,
                                duration_seconds=0.0  # Could be calculated from logs
                            )

                            logger.debug(f"Recorded {tokens} tokens ({'local' if is_local else 'cloud'})")
        except Exception as e:
            logger.error(f"Error processing Cursor logs: {e}")

    def monitor_loop(self, interval: float = 5.0):
        """Monitor Cursor activity in a loop."""
        logger.info("🔍 Starting Cursor token monitoring...")
        logger.info(f"   Update interval: {interval}s")
        logger.info("")

        try:
            while True:
                self.process_cursor_activity()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor Token Integration")
    parser.add_argument("--monitor", action="store_true", help="Monitor continuously")
    parser.add_argument("--interval", type=float, default=5.0, help="Update interval in seconds")
    parser.add_argument("--process-once", action="store_true", help="Process once and exit")

    args = parser.parse_args()

    integration = CursorTokenIntegration()

    if args.process_once:
        integration.process_cursor_activity()
        print("✅ Processed Cursor activity")
    elif args.monitor:
        integration.monitor_loop(interval=args.interval)
    else:
        # Default: process once
        integration.process_cursor_activity()
        print("✅ Processed Cursor activity")


if __name__ == "__main__":


    main()