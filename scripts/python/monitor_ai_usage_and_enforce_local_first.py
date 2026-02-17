#!/usr/bin/env python3
"""
Monitor AI Usage and Enforce Local-First

Continuously monitors AI usage and enforces local-first routing.
Alerts when cloud providers are being used instead of ULTRON/KAIJU/R5.

Tags: #MONITORING #LOCAL_FIRST #ENFORCEMENT @JARVIS @LUMINA @R5
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

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

logger = get_logger("MonitorAIUsage")

from enforce_local_first_ai_routing import LocalFirstAIRouter
from cursor_local_first_interceptor import CursorLocalFirstInterceptor


class AIUsageMonitor:
    """Monitor AI usage and enforce local-first"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.router = LocalFirstAIRouter(project_root)
        self.interceptor = CursorLocalFirstInterceptor(project_root)
        self.running = False
        self.monitor_thread = None
        self.check_interval = 30.0  # Check every 30 seconds

    def start(self):
        """Start monitoring"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ AI Usage Monitor started")

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("🛑 AI Usage Monitor stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Check Cursor settings
                self.interceptor._monitor_cursor_settings()

                # Get routing stats
                stats = self.router.get_routing_stats()

                # Alert if cloud usage is high
                total = stats.get("total_requests", 0)
                if total > 0:
                    cloud_percent = float(stats.get("cloud_percent", "0%").rstrip("%"))
                    if cloud_percent > 10.0:  # More than 10% cloud usage
                        logger.warning(f"⚠️  High cloud usage detected: {cloud_percent:.1f}%")
                        logger.warning("   Recommendation: Review routing to use ULTRON/KAIJU/R5 instead")

                # Log stats periodically
                if total > 0 and total % 10 == 0:
                    logger.info(f"📊 Routing Stats: {stats['local_percent']} local, {stats['cloud_percent']} cloud")

                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(self.check_interval)

    def get_report(self) -> Dict[str, Any]:
        """Get comprehensive usage report"""
        stats = self.router.get_routing_stats()
        cursor_report = self.interceptor.get_routing_report()

        return {
            "timestamp": datetime.now().isoformat(),
            "local_first_enforced": True,
            "routing_statistics": stats,
            "cursor_status": cursor_report,
            "recommendations": self._generate_recommendations(stats)
        }

    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on stats"""
        recommendations = []

        total = stats.get("total_requests", 0)
        if total == 0:
            recommendations.append("No AI requests detected - system ready for local-first routing")
            return recommendations

        local_percent = float(stats.get("local_percent", "0%").rstrip("%"))
        cloud_percent = float(stats.get("cloud_percent", "0%").rstrip("%"))
        blocked = stats.get("blocked_cloud", 0)

        if local_percent >= 90.0:
            recommendations.append("✅ Excellent local-first usage - continue using ULTRON/KAIJU/R5")
        elif local_percent >= 70.0:
            recommendations.append("✅ Good local-first usage - aim for 90%+ local")
        else:
            recommendations.append("⚠️  Low local-first usage - prioritize ULTRON/KAIJU/R5")

        if blocked > 0:
            recommendations.append(f"✅ Successfully blocked {blocked} cloud requests - routed to local instead")

        if cloud_percent > 10.0:
            recommendations.append("⚠️  Cloud usage above 10% - review and route to local-first AI")
            recommendations.append("   Use: ULTRON (localhost:11434) or KAIJU (<NAS_PRIMARY_IP>:11434)")

        return recommendations


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor AI Usage and Enforce Local-First")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--report", action="store_true", help="Generate report and exit")

    args = parser.parse_args()

    monitor = AIUsageMonitor(project_root)

    if args.report:
        report = monitor.get_report()
        print("=" * 80)
        print("📊 AI USAGE REPORT")
        print("=" * 80)
        print()
        print(f"Local Requests: {report['routing_statistics']['local_requests']}")
        print(f"Cloud Requests: {report['routing_statistics']['cloud_requests']}")
        print(f"Blocked Cloud: {report['routing_statistics']['blocked_cloud']}")
        print(f"Local Percent: {report['routing_statistics']['local_percent']}")
        print()
        print("Recommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
        print()
        return

    if args.daemon:
        monitor.start()
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            monitor.stop()
    else:
        # One-time check
        monitor.interceptor._monitor_cursor_settings()
        report = monitor.get_report()

        print("=" * 80)
        print("📊 AI USAGE MONITORING")
        print("=" * 80)
        print()
        print(f"Local-First Enforced: {report['local_first_enforced']}")
        print(f"Local Requests: {report['routing_statistics']['local_requests']}")
        print(f"Cloud Requests: {report['routing_statistics']['cloud_requests']}")
        print()
        print("Recommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
        print()


if __name__ == "__main__":


    main()