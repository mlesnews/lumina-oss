#!/usr/bin/env python3
"""
Log Aggregation Service
Continuously monitors and aggregates logs, detecting patterns over time

Features:
- Continuous log monitoring
- Pattern detection and aggregation
- Time-based aggregation
- Debugging support
- Pattern trend analysis
"""

import time
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

try:
    from centralized_log_parser import CentralizedLogParser, LogSource, LogLevel
    from universal_logging_wrapper import get_logger
except ImportError:
    import logging
    get_logger = logging.getLogger
    CentralizedLogParser = None

logger = get_logger("LogAggregationService")


class LogAggregationService:
    """Service for continuous log aggregation and pattern detection"""

    def __init__(self, project_root: Optional[Path] = None, interval: int = 300):
        """
        Initialize log aggregation service

        Args:
            project_root: Project root directory
            interval: Aggregation interval in seconds (default: 5 minutes)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.interval = interval
        self.running = False
        self.thread = None

        if CentralizedLogParser is None:
            logger.error("CentralizedLogParser not available")
            raise ImportError("CentralizedLogParser required")

        self.parser = CentralizedLogParser(project_root=project_root)

        # Aggregation history
        self.aggregation_history_dir = project_root / "data" / "log_aggregation" / "history"
        self.aggregation_history_dir.mkdir(parents=True, exist_ok=True)

        # Pattern trends
        self.pattern_trends_file = self.aggregation_history_dir / "pattern_trends.json"
        self.pattern_trends: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # Load existing trends
        self._load_trends()

        logger.info(f"Log Aggregation Service initialized (interval: {interval}s)")

    def _load_trends(self):
        """Load existing pattern trends"""
        if self.pattern_trends_file.exists():
            try:
                with open(self.pattern_trends_file, 'r', encoding='utf-8') as f:
                    self.pattern_trends = json.load(f)
                logger.info(f"Loaded {len(self.pattern_trends)} pattern trends")
            except Exception as e:
                logger.warning(f"Failed to load trends: {e}")

    def _save_trends(self):
        """Save pattern trends"""
        try:
            with open(self.pattern_trends_file, 'w', encoding='utf-8') as f:
                json.dump(self.pattern_trends, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save trends: {e}")

    def _aggregate_cycle(self):
        """Single aggregation cycle"""
        try:
            logger.info("Starting aggregation cycle...")

            # Parse all logs
            result = self.parser.parse_all_logs()

            # Update pattern trends
            timestamp = datetime.now().isoformat()
            for pattern_id, details in result['pattern_aggregation']['pattern_details'].items():
                trend_entry = {
                    "timestamp": timestamp,
                    "occurrences": details['occurrences'],
                    "severity": details['severity'],
                    "category": details['category']
                }
                self.pattern_trends[pattern_id].append(trend_entry)

                # Keep only last 100 entries per pattern
                if len(self.pattern_trends[pattern_id]) > 100:
                    self.pattern_trends[pattern_id] = self.pattern_trends[pattern_id][-100:]

            # Save trends
            self._save_trends()

            logger.info(f"Aggregation complete: {result['total_entries']} entries, {result['pattern_aggregation']['patterns_matched']} patterns")

            # Check for critical patterns
            critical_patterns = [
                pattern_id for pattern_id, details in result['pattern_aggregation']['pattern_details'].items()
                if details['severity'] in ['critical', 'error']
            ]

            if critical_patterns:
                logger.warning(f"⚠️  Critical patterns detected: {', '.join(critical_patterns)}")

        except Exception as e:
            logger.error(f"Error in aggregation cycle: {e}")

    def _run_service(self):
        """Main service loop"""
        logger.info("Log Aggregation Service started")

        while self.running:
            try:
                self._aggregate_cycle()

                # Sleep until next cycle
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Service error: {e}")
                time.sleep(self.interval)

        logger.info("Log Aggregation Service stopped")

    def start(self):
        """Start the aggregation service"""
        if self.running:
            logger.warning("Service already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_service, daemon=True)
        self.thread.start()
        logger.info("Log Aggregation Service started")

    def stop(self):
        """Stop the aggregation service"""
        if not self.running:
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Log Aggregation Service stopped")

    def get_pattern_trends(self, pattern_id: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """
        Get pattern trends over time

        Args:
            pattern_id: Specific pattern ID (None for all)
            hours: Number of hours to look back

        Returns:
            Dictionary of pattern trends
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        if pattern_id:
            # Get specific pattern
            trends = self.pattern_trends.get(pattern_id, [])
            filtered_trends = [
                t for t in trends
                if datetime.fromisoformat(t['timestamp']) >= cutoff_time
            ]
            return {
                pattern_id: filtered_trends
            }
        else:
            # Get all patterns
            result = {}
            for pid, trends in self.pattern_trends.items():
                filtered_trends = [
                    t for t in trends
                    if datetime.fromisoformat(t['timestamp']) >= cutoff_time
                ]
                if filtered_trends:
                    result[pid] = filtered_trends
            return result

    def get_debugging_insights(self) -> Dict[str, Any]:
        """Get insights for debugging"""
        insights = {
            "timestamp": datetime.now().isoformat(),
            "recent_errors": [],
            "pattern_summary": {},
            "trending_patterns": [],
            "recommendations": []
        }

        # Get recent errors
        try:
            startup_logs = self.parser.get_startup_logs()
            recent_errors = [
                entry for entry in startup_logs[-50:]  # Last 50 entries
                if entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]
            ]
            insights["recent_errors"] = [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "source": entry.source.value,
                    "component": entry.component,
                    "message": entry.message[:200]
                }
                for entry in recent_errors[-10:]  # Last 10 errors
            ]
        except Exception as e:
            logger.debug(f"Error getting recent errors: {e}")

        # Get pattern summary
        try:
            pattern_summary = self.parser.get_pattern_summary()
            insights["pattern_summary"] = {
                "total_patterns": pattern_summary["total_patterns"],
                "patterns_by_severity": defaultdict(int)
            }

            for pattern_id, pattern_data in pattern_summary["patterns"].items():
                severity = pattern_data.get("severity", "info")
                insights["pattern_summary"]["patterns_by_severity"][severity] += 1
        except Exception as e:
            logger.debug(f"Error getting pattern summary: {e}")

        # Get trending patterns (patterns with increasing occurrences)
        try:
            trends = self.get_pattern_trends(hours=24)
            for pattern_id, trend_data in trends.items():
                if len(trend_data) >= 2:
                    # Check if occurrences are increasing
                    recent = trend_data[-1]['occurrences']
                    previous = trend_data[-2]['occurrences']
                    if recent > previous:
                        insights["trending_patterns"].append({
                            "pattern_id": pattern_id,
                            "current": recent,
                            "previous": previous,
                            "increase": recent - previous
                        })
        except Exception as e:
            logger.debug(f"Error getting trending patterns: {e}")

        # Generate recommendations
        if insights["recent_errors"]:
            insights["recommendations"].append(
                f"Review {len(insights['recent_errors'])} recent errors for patterns"
            )

        if insights["trending_patterns"]:
            insights["recommendations"].append(
                f"Monitor {len(insights['trending_patterns'])} trending patterns"
            )

        return insights


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Log Aggregation Service")
    parser.add_argument("--start", action="store_true", help="Start the service")
    parser.add_argument("--once", action="store_true", help="Run aggregation once and exit")
    parser.add_argument("--insights", action="store_true", help="Get debugging insights")
    parser.add_argument("--trends", help="Get pattern trends (pattern ID or 'all')")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back for trends")

    args = parser.parse_args()

    service = LogAggregationService()

    if args.once:
        # Run once
        service._aggregate_cycle()
    elif args.insights:
        # Get insights
        insights = service.get_debugging_insights()
        print(json.dumps(insights, indent=2))
    elif args.trends:
        # Get trends
        pattern_id = None if args.trends == "all" else args.trends
        trends = service.get_pattern_trends(pattern_id, args.hours)
        print(json.dumps(trends, indent=2))
    elif args.start:
        # Start service
        service.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            service.stop()
    else:
        # Default: run once
        service._aggregate_cycle()

