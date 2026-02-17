"""
LUMINA Metrics Dashboard
Real-time dashboard for LUMINA metrics and analytics.

#JARVIS #LUMINA #METRICS #DASHBOARD #ANALYTICS
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("LuminaMetricsDashboard")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LuminaMetricsDashboard")

from scripts.python.lumina_hook_trace_system import get_hook_trace


class LuminaMetricsDashboard:
    """Real-time metrics dashboard."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.hook_trace = get_hook_trace(project_root)

    def generate_dashboard(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive dashboard."""
        metrics = self.hook_trace.get_metrics(hours=hours)
        analytics = self.hook_trace.generate_analytics_report(hours=hours)

        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "period_hours": hours,
            "system_health": {
                "status": metrics.system_health,
                "success_rate": f"{metrics.success_rate:.2f}%",
                "error_rate": f"{metrics.error_rate:.2f}%",
                "total_operations": metrics.total_operations
            },
            "operations": {
                "by_type": metrics.operations_by_type,
                "by_level": metrics.operations_by_level,
                "total": metrics.total_operations,
                "successful": metrics.successful_operations,
                "failed": metrics.failed_operations
            },
            "performance": {
                "average_duration_ms": f"{metrics.average_duration_ms:.2f}",
                "operations_per_hour": metrics.total_operations / hours if hours > 0 else 0
            },
            "recent_errors": metrics.recent_errors,
            "recommendations": analytics.get("recommendations", []),
            "top_operations": self._get_top_operations(hours)
        }

        return dashboard

    def _get_top_operations(self, hours: int) -> List[Dict[str, Any]]:
        """Get top operations by count."""
        traces = self.hook_trace._load_recent_traces(
            datetime.now() - timedelta(hours=hours)
        )

        op_counts = {}
        for trace in traces:
            op_name = trace.get("operation_name", "unknown")
            op_counts[op_name] = op_counts.get(op_name, 0) + 1

        top_ops = sorted(op_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return [{"operation": op, "count": count} for op, count in top_ops]

    def print_dashboard(self, hours: int = 24):
        """Print dashboard to console."""
        dashboard = self.generate_dashboard(hours=hours)

        print("\n" + "="*80)
        print("LUMINA METRICS DASHBOARD")
        print("="*80)
        print(f"Timestamp: {dashboard['timestamp']}")
        print(f"Period: Last {hours} hours")
        print()

        # System Health
        health = dashboard['system_health']
        print("SYSTEM HEALTH")
        print("-" * 80)
        print(f"Status: {health['status'].upper()}")
        print(f"Success Rate: {health['success_rate']}")
        print(f"Error Rate: {health['error_rate']}")
        print(f"Total Operations: {health['total_operations']}")
        print()

        # Operations
        ops = dashboard['operations']
        print("OPERATIONS")
        print("-" * 80)
        print(f"Total: {ops['total']}")
        print(f"Successful: {ops['successful']}")
        print(f"Failed: {ops['failed']}")
        print()
        print("By Type:")
        for op_type, count in sorted(ops['by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {op_type}: {count}")
        print()

        # Performance
        perf = dashboard['performance']
        print("PERFORMANCE")
        print("-" * 80)
        print(f"Average Duration: {perf['average_duration_ms']}ms")
        print(f"Operations/Hour: {perf['operations_per_hour']:.1f}")
        print()

        # Top Operations
        print("TOP OPERATIONS")
        print("-" * 80)
        for op in dashboard['top_operations']:
            print(f"  {op['operation']}: {op['count']}")
        print()

        # Recommendations
        if dashboard['recommendations']:
            print("RECOMMENDATIONS")
            print("-" * 80)
            for rec in dashboard['recommendations']:
                print(f"  {rec}")
            print()

        # Recent Errors
        if dashboard['recent_errors']:
            print("RECENT ERRORS")
            print("-" * 80)
            for error in dashboard['recent_errors'][-5:]:
                print(f"  [{error['timestamp']}] {error['operation']}: {error['error']}")
            print()

        print("="*80)


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Metrics Dashboard")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--hours", type=int, default=24, help="Hours of data to show")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        dashboard = LuminaMetricsDashboard(args.project_root)

        if args.json:
            data = dashboard.generate_dashboard(hours=args.hours)
            print(json.dumps(data, indent=2))
        else:
            dashboard.print_dashboard(hours=args.hours)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()