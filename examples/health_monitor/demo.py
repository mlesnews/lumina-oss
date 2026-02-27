#!/usr/bin/env python3
"""
Health Monitor Demo — Ecosystem health scoring with weighted dimensions.

Run: python examples/health_monitor/demo.py
"""

import random
import time

from lumina.aios import HealthAggregator


def main():
    # Define a system with 5 health dimensions
    health = HealthAggregator(
        dimensions={
            "api_latency": 0.25,
            "error_rate": 0.25,
            "throughput": 0.20,
            "memory_usage": 0.15,
            "disk_io": 0.15,
        },
        thresholds={
            "CRITICAL": 40.0,
            "DEGRADED": 60.0,
            "HEALTHY": 80.0,
        },
    )

    print("=== Health Monitor Demo ===\n")

    # Simulate 5 monitoring cycles
    for cycle in range(1, 6):
        print(f"--- Cycle {cycle} ---")

        # Simulate scores with some randomness
        health.score("api_latency", 0.7 + random.uniform(-0.2, 0.2), f"p99={random.randint(80, 300)}ms")
        health.score("error_rate", 0.8 + random.uniform(-0.3, 0.15), f"{random.uniform(0.1, 3.0):.1f}% errors")
        health.score("throughput", 0.6 + random.uniform(-0.1, 0.3), f"{random.randint(500, 1200)} req/s")
        health.score("memory_usage", 0.5 + random.uniform(-0.1, 0.3), f"{random.randint(50, 85)}% used")
        health.score("disk_io", 0.7 + random.uniform(-0.2, 0.2), f"{random.randint(10, 80)}% IO wait")

        report = health.evaluate()

        print(f"  Score: {report.score_pct:.1f}% [{report.label}]")
        for dim in report.dimensions:
            bar = "#" * int(dim.score * 20)
            print(f"    {dim.name:15s} {dim.score:.0%} {bar:20s} {dim.detail}")
        print(f"  Trend: {health.get_trend()}")
        print(f"  Recommendation: {report.recommendation}")
        print()

        time.sleep(0.1)

    print("=== Demo Complete ===")


if __name__ == "__main__":
    main()
