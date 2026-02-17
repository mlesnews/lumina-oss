#!/usr/bin/env python3
"""Run the diagnostic simulation."""

import sys

sys.path.insert(0, ".")

from scripts.python.notification_lifecycle_diagnostics import NotificationLifecycleAnalyzer

analyzer = NotificationLifecycleAnalyzer()
results = analyzer.run_diagnostic_simulation()

print(f"Overall Pass Rate: {results['overall_pass_rate']:.1f}%")
print()
for sr in results["scenarios_tested"]:
    print(f"{sr['scenario']}: {sr['tests_passed']}/{sr['tests_run']} passed")
    if sr["details"]:
        for d in sr["details"][:2]:
            notif = d["notification"][:50]
            print(f"  - {notif}: {d['pattern_matched']}")
            print(f"  - {notif}: {d['pattern_matched']}")
