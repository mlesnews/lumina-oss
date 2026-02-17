#!/usr/bin/env python3
"""
Performance Monitor
Monitors API performance metrics

Tracks response times, throughput, and performance bottlenecks.
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict
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

logger = get_logger("PerformanceMonitor")


class PerformanceMonitor:
    """Monitors API performance"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.metrics_dir = self.project_root / "data" / "performance_metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # In-memory metrics
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.start_time = datetime.now()

    def record_request(
        self,
        endpoint: str,
        method: str,
        duration: float,
        status_code: int
    ):
        """Record request metrics"""
        key = f"{method} {endpoint}"
        self.response_times[key].append(duration)
        self.request_counts[key] += 1

        # Keep only last 1000 requests per endpoint
        if len(self.response_times[key]) > 1000:
            self.response_times[key] = self.response_times[key][-1000:]

        if status_code >= 400:
            self.error_counts[key] += 1

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "endpoints": {}
        }

        for endpoint, times in self.response_times.items():
            if times:
                sorted_times = sorted(times)
                metrics["endpoints"][endpoint] = {
                    "request_count": self.request_counts.get(endpoint, 0),
                    "error_count": self.error_counts.get(endpoint, 0),
                    "avg_response_time_ms": sum(times) / len(times) * 1000,
                    "min_response_time_ms": min(times) * 1000,
                    "max_response_time_ms": max(times) * 1000,
                    "p50_response_time_ms": sorted_times[len(sorted_times) // 2] * 1000,
                    "p95_response_time_ms": sorted_times[int(len(sorted_times) * 0.95)] * 1000,
                    "p99_response_time_ms": sorted_times[int(len(sorted_times) * 0.99)] * 1000 if len(sorted_times) > 1 else sorted_times[0] * 1000
                }

        return metrics

    def check_performance_thresholds(self) -> Dict[str, Any]:
        """Check if performance meets requirements"""
        metrics = self.get_performance_metrics()
        violations = []

        # Check p95 response times against requirements
        requirements = {
            "GET /api/v1/workflows": 200,  # ms
            "POST /api/v1/workflows": 500,
            "GET /api/v1/chat/messages": 100,
            "POST /api/v1/chat/messages": 300,
            "POST /api/v1/r5/knowledge/search": 500,
        }

        for endpoint, data in metrics.get("endpoints", {}).items():
            p95 = data.get("p95_response_time_ms", 0)
            required = requirements.get(endpoint.split()[1] if " " in endpoint else endpoint, 1000)

            if p95 > required:
                violations.append({
                    "endpoint": endpoint,
                    "p95_ms": p95,
                    "required_ms": required,
                    "violation": p95 - required
                })

        return {
            "status": "healthy" if not violations else "degraded",
            "violations": violations,
            "metrics": metrics
        }


def get_performance_monitor(project_root: Optional[Path] = None) -> PerformanceMonitor:
    """Get global performance monitor"""
    return PerformanceMonitor(project_root)
