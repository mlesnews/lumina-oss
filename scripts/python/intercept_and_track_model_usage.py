#!/usr/bin/env python3
"""
Intercept and Track Model Usage

Intercepts AI model requests and tracks which models are actively being used.
Integrates with the routing system to monitor real usage.

Tags: #INTERCEPTOR #TRACKING #MODEL_USAGE @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
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

logger = get_logger("InterceptAndTrackModelUsage")

from enforce_local_first_ai_routing import LocalFirstAIRouter
from live_model_usage_dashboard import LiveModelUsageDashboard


class ModelUsageInterceptor:
    """Intercept and track model usage"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.router = LocalFirstAIRouter(project_root)
        self.dashboard = LiveModelUsageDashboard(project_root)
        self.usage_file = project_root / "data" / "model_usage.json"
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)

    def intercept_request(self, model: str, request_type: str = "chat", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Intercept a model request and track usage

        Args:
            model: Model name being requested
            request_type: Type of request (chat, completion, etc.)
            context: Request context

        Returns:
            Routing result with tracking
        """
        # Route the request
        result = self.router.route_request(request_type, {"model": model, **(context or {})})

        # Track usage
        routed_to = result.get("provider", "UNKNOWN")
        blocked = result.get("blocked_cloud", False)

        self.dashboard.track_request(model, routed_to, blocked)

        # Save to file periodically
        self._save_usage()

        return result

    def _save_usage(self):
        """Save usage data to file"""
        try:
            report = self.dashboard.get_json_report()
            with open(self.usage_file, 'w') as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            logger.debug(f"Error saving usage: {e}")

    def get_active_models(self) -> list:
        """Get list of actively used models"""
        return self.dashboard.get_active_models()

    def display_active_models(self):
        """Display currently active models"""
        active = self.get_active_models()

        if not active:
            print("ℹ️  No active models in the last 5 minutes")
            return

        print("=" * 80)
        print("🔄 ACTIVELY USED MODELS")
        print("=" * 80)
        print()

        for model_info in active:
            model = model_info["model"]
            routed_to = model_info["routed_to"]
            blocked = model_info["blocked"]
            count = model_info["count"]
            time_since = model_info["time_since_last"]

            if routed_to in ["ULTRON", "KAIJU", "R5"]:
                status = "✅ LOCAL"
            elif blocked:
                status = "🚫 BLOCKED"
            else:
                status = "☁️  CLOUD"

            print(f"{status} {model}")
            print(f"   → Routed to: {routed_to}")
            print(f"   → Used {count} times")
            print(f"   → Last used: {time_since} ago")
            print()


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Intercept and Track Model Usage")
    parser.add_argument("--test", action="store_true", help="Test with sample requests")
    parser.add_argument("--show", action="store_true", help="Show active models")

    args = parser.parse_args()

    interceptor = ModelUsageInterceptor(project_root)

    if args.test:
        # Test with sample requests
        print("Testing model usage tracking...")
        print()

        test_models = [
            "qwen2.5:72b",
            "llama3.2:3b",
            "gpt-4",
            "claude-3-opus"
        ]

        for model in test_models:
            result = interceptor.intercept_request(model)
            print(f"Requested: {model}")
            print(f"  Routed to: {result.get('provider')}")
            if result.get('blocked_cloud'):
                print(f"  Cloud blocked: ✅")
            print()

        time.sleep(1)

    if args.show or not args.test:
        interceptor.display_active_models()

        # Show dashboard
        print()
        print("=" * 80)
        print("📊 USAGE STATISTICS")
        print("=" * 80)
        stats = interceptor.dashboard.stats
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Local Requests: {stats['local_requests']}")
        print(f"Cloud Requests: {stats['cloud_requests']}")
        print(f"Blocked Cloud: {stats['blocked_cloud']}")
        print()


if __name__ == "__main__":


    main()