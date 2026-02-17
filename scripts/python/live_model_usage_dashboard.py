#!/usr/bin/env python3
"""
Live Model Usage Dashboard

Displays actively used AI models in real-time with routing decisions.
Shows which models are currently being used and where requests are routed.

Tags: #DASHBOARD #LIVE_MONITORING #MODEL_USAGE @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque

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
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LiveModelUsageDashboard")

from enforce_local_first_ai_routing import LocalFirstAIRouter


class LiveModelUsageDashboard:
    """Live dashboard showing actively used AI models"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.router = LocalFirstAIRouter(project_root)

        # Track active usage
        self.active_requests: deque = deque(maxlen=100)  # Last 100 requests
        self.model_usage: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "count": 0,
            "last_used": None,
            "routed_to": None,
            "blocked": False,
            "requests": []
        })

        # Statistics
        self.stats = {
            "total_requests": 0,
            "local_requests": 0,
            "cloud_requests": 0,
            "blocked_cloud": 0,
            "start_time": datetime.now()
        }

        self.running = False
        self.update_interval = 2.0  # Update every 2 seconds

    def track_request(self, model: str, routed_to: str, blocked: bool = False):
        try:
            """Track a model usage request"""
            timestamp = datetime.now()

            # Add to active requests
            request_data = {
                "timestamp": timestamp.isoformat(),
                "model": model,
                "routed_to": routed_to,
                "blocked": blocked
            }
            self.active_requests.append(request_data)

            # Update model usage stats
            self.model_usage[model]["count"] += 1
            self.model_usage[model]["last_used"] = timestamp.isoformat()
            self.model_usage[model]["routed_to"] = routed_to
            self.model_usage[model]["blocked"] = blocked
            self.model_usage[model]["requests"].append(request_data)

            # Keep only last 20 requests per model
            if len(self.model_usage[model]["requests"]) > 20:
                self.model_usage[model]["requests"] = self.model_usage[model]["requests"][-20:]

            # Update statistics
            self.stats["total_requests"] += 1
            if routed_to in ["ULTRON", "KAIJU", "R5"]:
                self.stats["local_requests"] += 1
            else:
                self.stats["cloud_requests"] += 1
            if blocked:
                self.stats["blocked_cloud"] += 1

        except Exception as e:
            self.logger.error(f"Error in track_request: {e}", exc_info=True)
            raise
    def get_active_models(self) -> List[Dict[str, Any]]:
        """Get list of actively used models"""
        active = []

        # Get models used in last 5 minutes
        cutoff = datetime.now() - timedelta(minutes=5)

        for model, usage in self.model_usage.items():
            if usage["last_used"]:
                last_used = datetime.fromisoformat(usage["last_used"])
                if last_used >= cutoff:
                    active.append({
                        "model": model,
                        "count": usage["count"],
                        "last_used": usage["last_used"],
                        "routed_to": usage["routed_to"],
                        "blocked": usage["blocked"],
                        "is_active": True,
                        "time_since_last": str(datetime.now() - last_used).split('.')[0]
                    })

        # Sort by last used (most recent first)
        active.sort(key=lambda x: x["last_used"], reverse=True)

        return active

    def get_recent_requests(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent routing requests"""
        return list(self.active_requests)[-count:]

    def display_dashboard(self, clear_screen: bool = True):
        """Display live dashboard"""
        if clear_screen:
            import os
            os.system('cls' if os.name == 'nt' else 'clear')

        print("=" * 100)
        print("📊 LIVE MODEL USAGE DASHBOARD")
        print("=" * 100)
        print()

        # Statistics
        uptime = datetime.now() - self.stats["start_time"]
        print(f"⏱️  Uptime: {str(uptime).split('.')[0]}")
        print(f"📈 Total Requests: {self.stats['total_requests']}")
        print(f"✅ Local Requests: {self.stats['local_requests']} ({self.stats['local_requests']/max(self.stats['total_requests'], 1)*100:.1f}%)")
        print(f"☁️  Cloud Requests: {self.stats['cloud_requests']} ({self.stats['cloud_requests']/max(self.stats['total_requests'], 1)*100:.1f}%)")
        print(f"🚫 Blocked Cloud: {self.stats['blocked_cloud']}")
        print()

        # Active Models
        active_models = self.get_active_models()
        if active_models:
            print("=" * 100)
            print("🔄 ACTIVELY USED MODELS (Last 5 minutes)")
            print("=" * 100)
            print()

            for model_info in active_models:
                model = model_info["model"]
                routed_to = model_info["routed_to"]
                blocked = model_info["blocked"]
                count = model_info["count"]
                time_since = model_info["time_since_last"]

                # Determine status
                if routed_to in ["ULTRON", "KAIJU", "R5"]:
                    status = "✅ LOCAL"
                    provider = routed_to
                elif blocked:
                    status = "🚫 BLOCKED"
                    provider = f"{routed_to} (was {model})"
                else:
                    status = "☁️  CLOUD"
                    provider = model

                print(f"   {status} {model}")
                print(f"      → Routed to: {provider}")
                print(f"      → Usage count: {count}")
                print(f"      → Last used: {time_since} ago")
                print()
        else:
            print("=" * 100)
            print("ℹ️  NO ACTIVE MODELS (Last 5 minutes)")
            print("=" * 100)
            print()

        # Recent Requests
        recent = self.get_recent_requests(10)
        if recent:
            print("=" * 100)
            print("📋 RECENT ROUTING DECISIONS (Last 10)")
            print("=" * 100)
            print()

            for req in reversed(recent):  # Most recent first
                timestamp = datetime.fromisoformat(req["timestamp"])
                time_str = timestamp.strftime("%H:%M:%S")
                model = req["model"]
                routed_to = req["routed_to"]
                blocked = req["blocked"]

                if blocked:
                    print(f"   🚫 [{time_str}] {model} → BLOCKED → {routed_to}")
                elif routed_to in ["ULTRON", "KAIJU", "R5"]:
                    print(f"   ✅ [{time_str}] {model} → {routed_to}")
                else:
                    print(f"   ☁️  [{time_str}] {model} → {routed_to}")
            print()

        # All Models Summary
        if self.model_usage:
            print("=" * 100)
            print("📊 ALL MODELS SUMMARY")
            print("=" * 100)
            print()

            # Sort by usage count
            sorted_models = sorted(
                self.model_usage.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )

            for model, usage in sorted_models[:10]:  # Top 10
                routed_to = usage["routed_to"]
                count = usage["count"]
                blocked = usage["blocked"]

                if routed_to in ["ULTRON", "KAIJU", "R5"]:
                    status = "✅"
                elif blocked:
                    status = "🚫"
                else:
                    status = "☁️ "

                print(f"   {status} {model:30s} → {routed_to:15s} (used {count} times)")
            print()

        print("=" * 100)
        print("Press Ctrl+C to exit")
        print("=" * 100)

    def simulate_usage(self):
        """Simulate model usage for testing"""
        test_models = [
            ("qwen2.5:72b", "ULTRON", False),
            ("llama3.2:3b", "ULTRON", False),
            ("gpt-4", "ULTRON", True),  # Blocked
            ("claude-3-opus", "ULTRON", True),  # Blocked
        ]

        import random
        while self.running:
            model, routed_to, blocked = random.choice(test_models)
            self.track_request(model, routed_to, blocked)
            time.sleep(random.uniform(3, 8))  # Random interval

    def run_live(self, simulate: bool = False):
        """Run live dashboard"""
        self.running = True

        if simulate:
            # Start simulation thread
            sim_thread = threading.Thread(target=self.simulate_usage, daemon=True)
            sim_thread.start()

        try:
            while self.running:
                self.display_dashboard()
                time.sleep(self.update_interval)
        except KeyboardInterrupt:
            self.running = False
            print("\n\n🛑 Dashboard stopped")

    def get_json_report(self) -> Dict[str, Any]:
        """Get JSON report of current state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.stats,
            "active_models": self.get_active_models(),
            "recent_requests": self.get_recent_requests(20),
            "all_models": {
                model: {
                    "count": usage["count"],
                    "last_used": usage["last_used"],
                    "routed_to": usage["routed_to"],
                    "blocked": usage["blocked"]
                }
                for model, usage in self.model_usage.items()
            }
        }


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Live Model Usage Dashboard")
        parser.add_argument("--simulate", action="store_true", help="Simulate model usage")
        parser.add_argument("--json", action="store_true", help="Output JSON report")
        parser.add_argument("--once", action="store_true", help="Display once and exit")

        args = parser.parse_args()

        dashboard = LiveModelUsageDashboard(project_root)

        if args.json:
            # Load existing usage if available
            usage_file = project_root / "data" / "model_usage.json"
            if usage_file.exists():
                with open(usage_file, 'r') as f:
                    data = json.load(f)
                    # Restore state
                    for model, usage in data.get("all_models", {}).items():
                        dashboard.model_usage[model] = {
                            "count": usage.get("count", 0),
                            "last_used": usage.get("last_used"),
                            "routed_to": usage.get("routed_to"),
                            "blocked": usage.get("blocked", False),
                            "requests": []
                        }

            report = dashboard.get_json_report()
            print(json.dumps(report, indent=2))
            return

        if args.once:
            dashboard.display_dashboard(clear_screen=False)
            return

        # Run live dashboard
        dashboard.run_live(simulate=args.simulate)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()