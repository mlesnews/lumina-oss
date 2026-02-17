#!/usr/bin/env python3
"""
Show Active Models

Quick command to display actively used AI models.

Usage:
    python scripts/python/show_active_models.py
    python scripts/python/show_active_models.py --live
    python scripts/python/show_active_models.py --json
"""

import sys
import json
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from intercept_and_track_model_usage import ModelUsageInterceptor
from live_model_usage_dashboard import LiveModelUsageDashboard


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Show Active Models")
    parser.add_argument("--live", action="store_true", help="Live dashboard")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--simulate", action="store_true", help="Simulate usage")

    args = parser.parse_args()

    if args.live:
        # Run live dashboard
        dashboard = LiveModelUsageDashboard(project_root)

        # Load existing usage
        usage_file = project_root / "data" / "model_usage.json"
        if usage_file.exists():
            try:
                with open(usage_file, 'r') as f:
                    data = json.load(f)
                    for model, usage in data.get("all_models", {}).items():
                        dashboard.model_usage[model] = {
                            "count": usage.get("count", 0),
                            "last_used": usage.get("last_used"),
                            "routed_to": usage.get("routed_to"),
                            "blocked": usage.get("blocked", False),
                            "requests": []
                        }
                    if "statistics" in data:
                        dashboard.stats.update(data["statistics"])
            except (json.JSONDecodeError, KeyError) as e:
                # File corrupted or incomplete, start fresh
                pass

        dashboard.run_live(simulate=args.simulate)
    else:
        # Show current state
        interceptor = ModelUsageInterceptor(project_root)

        # Load existing usage
        usage_file = project_root / "data" / "model_usage.json"
        if usage_file.exists():
            try:
                with open(usage_file, 'r') as f:
                    data = json.load(f)
                    for model, usage in data.get("all_models", {}).items():
                        interceptor.dashboard.model_usage[model] = {
                            "count": usage.get("count", 0),
                            "last_used": usage.get("last_used"),
                            "routed_to": usage.get("routed_to"),
                            "blocked": usage.get("blocked", False),
                            "requests": []
                        }
                    if "statistics" in data:
                        interceptor.dashboard.stats.update(data["statistics"])
            except (json.JSONDecodeError, KeyError) as e:
                # File corrupted or incomplete, start fresh
                pass

        if args.json:
            report = interceptor.dashboard.get_json_report()
            print(json.dumps(report, indent=2))
        else:
            interceptor.display_active_models()

            # Show summary
            stats = interceptor.dashboard.stats
            if stats["total_requests"] > 0:
                print("=" * 80)
                print("📊 SUMMARY")
                print("=" * 80)
                print(f"Total Requests: {stats['total_requests']}")
                print(f"Local Requests: {stats['local_requests']} ({stats['local_requests']/stats['total_requests']*100:.1f}%)")
                print(f"Cloud Requests: {stats['cloud_requests']} ({stats['cloud_requests']/stats['total_requests']*100:.1f}%)")
                print(f"Blocked Cloud: {stats['blocked_cloud']}")
                print()


if __name__ == "__main__":


    main()