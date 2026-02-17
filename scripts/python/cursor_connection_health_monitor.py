#!/usr/bin/env python3
"""
Cursor IDE Connection Health Monitor

Monitors Cursor IDE connection health and tracks connection errors.
Integrates with Star Trek First Contact Protocol for AI encounters.

Tags: #CURSOR_IDE #CONNECTION_HEALTH #MONITORING #STAR_TREK @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

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

logger = get_logger("CursorConnectionHealthMonitor")


@dataclass
class ConnectionHealthMetric:
    """Connection health metric"""
    timestamp: str
    error_type: str
    error_message: str
    retry_attempt: int
    success: bool
    response_time: Optional[float] = None
    ai_service: Optional[str] = None


class CursorConnectionHealthMonitor:
    """
    Cursor IDE Connection Health Monitor

    Tracks connection health, errors, and integrates with Star Trek protocol.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize connection health monitor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cursor_connection_health"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Health metrics
        self.metrics: List[ConnectionHealthMetric] = []

        # Statistics
        self.stats = {
            "total_connections": 0,
            "successful_connections": 0,
            "failed_connections": 0,
            "econnreset_errors": 0,
            "connecterror_errors": 0,
            "timeout_errors": 0,
            "other_errors": 0,
            "average_response_time": 0.0,
            "last_success": None,
            "last_failure": None
        }

        # Load existing metrics
        self._load_metrics()

        logger.info("✅ Cursor Connection Health Monitor initialized")
        logger.info(f"   Metrics directory: {self.data_dir}")

    def _load_metrics(self):
        """Load historical metrics"""
        try:
            metrics_file = self.data_dir / "metrics.json"
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    self.metrics = [
                        ConnectionHealthMetric(**m) for m in data.get("metrics", [])
                    ]
                    self.stats = data.get("stats", self.stats)
                    logger.info(f"   ✅ Loaded {len(self.metrics)} historical metrics")
        except Exception as e:
            logger.debug(f"   Could not load metrics: {e}")

    def _save_metrics(self):
        """Save metrics to disk"""
        try:
            metrics_file = self.data_dir / "metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump({
                    "metrics": [
                        {
                            "timestamp": m.timestamp,
                            "error_type": m.error_type,
                            "error_message": m.error_message,
                            "retry_attempt": m.retry_attempt,
                            "success": m.success,
                            "response_time": m.response_time,
                            "ai_service": m.ai_service
                        }
                        for m in self.metrics[-1000:]  # Keep last 1000 metrics
                    ],
                    "stats": self.stats
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving metrics: {e}")

    def record_connection_attempt(
        self,
        success: bool,
        error: Optional[Exception] = None,
        retry_attempt: int = 0,
        response_time: Optional[float] = None,
        ai_service: Optional[str] = None
    ):
        """Record a connection attempt"""
        self.stats["total_connections"] += 1

        if success:
            self.stats["successful_connections"] += 1
            self.stats["last_success"] = datetime.now().isoformat()
        else:
            self.stats["failed_connections"] += 1
            self.stats["last_failure"] = datetime.now().isoformat()

        if error:
            error_str = str(error).lower()
            error_type = type(error).__name__

            if "econnreset" in error_str:
                self.stats["econnreset_errors"] += 1
                error_category = "ECONNRESET"
            elif "connecterror" in error_str or error_type == "ConnectError":
                self.stats["connecterror_errors"] += 1
                error_category = "ConnectError"
            elif "timeout" in error_str:
                self.stats["timeout_errors"] += 1
                error_category = "Timeout"
            else:
                self.stats["other_errors"] += 1
                error_category = "Other"
        else:
            error_category = "None"
            error_str = ""

        # Update average response time
        if response_time:
            if self.stats["average_response_time"] == 0:
                self.stats["average_response_time"] = response_time
            else:
                # Moving average
                self.stats["average_response_time"] = (
                    self.stats["average_response_time"] * 0.9 + response_time * 0.1
                )

        # Create metric
        metric = ConnectionHealthMetric(
            timestamp=datetime.now().isoformat(),
            error_type=error_category,
            error_message=str(error) if error else "",
            retry_attempt=retry_attempt,
            success=success,
            response_time=response_time,
            ai_service=ai_service
        )

        self.metrics.append(metric)

        # Save metrics
        self._save_metrics()

        # Log to Star Trek First Contact Protocol if error
        if error and not success:
            self._log_to_star_trek_protocol(error, ai_service)

    def _log_to_star_trek_protocol(self, error: Exception, ai_service: Optional[str]):
        """Log connection error to Star Trek First Contact Protocol"""
        try:
            from jarvis_star_trek_first_contact import JARVISStarTrekFirstContact

            first_contact = JARVISStarTrekFirstContact(self.project_root)

            # Determine if this is an AI service connection error
            error_str = str(error).lower()

            if ai_service:
                # Log as AI vessel encounter issue
                ai_info = {
                    "type": "connection_error",
                    "error": error_str,
                    "capabilities": ["AI Service"]
                }

                encounter = first_contact.encounter_ai(f"{ai_service}_connection", ai_info)
                logger.info(f"   🛸 Logged connection error to Star Trek protocol: {ai_service}")
        except Exception as e:
            logger.debug(f"   Could not log to Star Trek protocol: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        total = self.stats["total_connections"]
        success_rate = (
            (self.stats["successful_connections"] / total * 100)
            if total > 0 else 100.0
        )

        # Recent metrics (last hour)
        recent_cutoff = datetime.now() - timedelta(hours=1)
        recent_metrics = [
            m for m in self.metrics
            if datetime.fromisoformat(m.timestamp) > recent_cutoff
        ]

        recent_success_rate = (
            (sum(1 for m in recent_metrics if m.success) / len(recent_metrics) * 100)
            if recent_metrics else 100.0
        )

        # Health status
        if success_rate >= 95.0 and recent_success_rate >= 90.0:
            health_status = "Excellent"
        elif success_rate >= 85.0 and recent_success_rate >= 80.0:
            health_status = "Good"
        elif success_rate >= 70.0:
            health_status = "Fair"
        else:
            health_status = "Poor"

        return {
            "health_status": health_status,
            "success_rate": round(success_rate, 2),
            "recent_success_rate": round(recent_success_rate, 2),
            "total_connections": total,
            "successful_connections": self.stats["successful_connections"],
            "failed_connections": self.stats["failed_connections"],
            "error_breakdown": {
                "econnreset": self.stats["econnreset_errors"],
                "connecterror": self.stats["connecterror_errors"],
                "timeout": self.stats["timeout_errors"],
                "other": self.stats["other_errors"]
            },
            "average_response_time": round(self.stats["average_response_time"], 3),
            "last_success": self.stats["last_success"],
            "last_failure": self.stats["last_failure"],
            "recent_metrics_count": len(recent_metrics)
        }

    def print_health_report(self):
        """Print health report"""
        health = self.get_health_status()

        print("=" * 80)
        print("📊 CURSOR IDE CONNECTION HEALTH REPORT")
        print("=" * 80)
        print("")
        print(f"Health Status: {health['health_status']}")
        print(f"Overall Success Rate: {health['success_rate']}%")
        print(f"Recent Success Rate (1 hour): {health['recent_success_rate']}%")
        print("")
        print(f"Total Connections: {health['total_connections']}")
        print(f"Successful: {health['successful_connections']}")
        print(f"Failed: {health['failed_connections']}")
        print("")
        print("Error Breakdown:")
        print(f"  ECONNRESET: {health['error_breakdown']['econnreset']}")
        print(f"  ConnectError: {health['error_breakdown']['connecterror']}")
        print(f"  Timeout: {health['error_breakdown']['timeout']}")
        print(f"  Other: {health['error_breakdown']['other']}")
        print("")
        print(f"Average Response Time: {health['average_response_time']}s")
        print(f"Last Success: {health['last_success']}")
        print(f"Last Failure: {health['last_failure']}")
        print("")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor Connection Health Monitor")
        parser.add_argument("--status", action="store_true", help="Show health status")
        parser.add_argument("--report", action="store_true", help="Print health report")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        monitor = CursorConnectionHealthMonitor()

        if args.report:
            monitor.print_health_report()
        elif args.status or args.json:
            health = monitor.get_health_status()
            if args.json:
                print(json.dumps(health, indent=2, default=str))
            else:
                print(f"Health Status: {health['health_status']}")
                print(f"Success Rate: {health['success_rate']}%")
        else:
            monitor.print_health_report()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()