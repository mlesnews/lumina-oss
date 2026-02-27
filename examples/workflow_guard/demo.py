#!/usr/bin/env python3
"""
Workflow Guard Demo — Circuit breaker + gatekeeper + troubleshooting.

Run: python examples/workflow_guard/demo.py
"""

from lumina.safety import CircuitBreaker, Level
from lumina.workflow import Gatekeeper, GateColor
from lumina.workflow.troubleshooting import TroubleshootTracker, troubleshoot


def main():
    print("=== Workflow Guard Demo ===\n")

    # 1. Circuit Breaker
    print("--- Circuit Breaker ---")
    cb = CircuitBreaker(thresholds={
        Level.YELLOW: {"error_rate": 0.05, "latency_ms": 200},
        Level.ORANGE: {"error_rate": 0.10, "latency_ms": 500},
        Level.RED: {"error_rate": 0.20, "latency_ms": 1000},
    })

    scenarios = [
        {"error_rate": 0.02, "latency_ms": 100},   # GREEN
        {"error_rate": 0.07, "latency_ms": 150},   # YELLOW
        {"error_rate": 0.15, "latency_ms": 600},   # ORANGE
        {"error_rate": 0.25, "latency_ms": 1200},  # RED
        {"error_rate": 0.01, "latency_ms": 50},    # GREEN (recovery)
    ]

    for metrics in scenarios:
        level, reason = cb.check(metrics)
        proceed = "PROCEED" if cb.can_proceed() else "BLOCKED"
        print(f"  {level.name:7s} [{proceed:7s}] {reason}")

    # 2. Quality Gatekeeper
    print("\n--- Quality Gatekeeper ---")
    gk = Gatekeeper(name="deploy-gate")

    # Simulated checks
    gk.add_check("tests", GateColor.RED, lambda: [])  # Tests pass
    gk.add_check("lint", GateColor.ORANGE, lambda: ["Line 42: line too long (120 > 100)"])
    gk.add_check("git", GateColor.CYAN, lambda: ["Modified: api/handler.py"])
    gk.add_check("docs", GateColor.BLUE, lambda: ["Consider adding docstring to handler()"])

    result = gk.audit()
    print(f"  Status: {result.status.name}")
    print(f"  Can proceed: {result.can_proceed}")
    print(f"  Needs commit: {result.needs_commit}")
    for f in result.findings:
        print(f"    [{f.color.name:6s}] {f.check_name}: {f.message}")

    # 3. Troubleshooting Decorator
    print("\n--- Troubleshooting ---")
    tracker = TroubleshootTracker()

    @troubleshoot(tracker, issue="High API latency")
    def investigate_latency(ctx):
        ctx.add_symptom("p99 > 500ms for 10 minutes")
        ctx.add_symptom("Connection pool at 95% capacity")
        ctx.add_step("Checked connection pool: saturated")
        ctx.add_step("Increased pool size 10 -> 50")
        ctx.add_step("Verified latency dropped to 80ms")
        return "Pool size increased, latency resolved"

    resolution = investigate_latency()
    print(f"  Resolution: {resolution}")

    report = tracker.get_report()
    print(f"  Sessions: {report['total_sessions']}")
    print(f"  Success rate: {report['success_rate']:.0%}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
