#!/usr/bin/env python3
"""Run secret audit"""

import sys
from pathlib import Path

# Add scripts/python to path
script_dir = Path(__file__).parent
# Go up from scripts/python/ to project root
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

# Import and run audit
from audit_secrets import SecretAuditor, aggregate_to_r5
import json

print("=" * 60)
print("Secret Audit - Scavenging Codebase")
print("=" * 60)
print(f"Project Root: {project_root}\n")

# Initialize auditor
auditor = SecretAuditor(project_root)

# Scan codebase
print("Scanning codebase for secrets...")
findings = auditor.scan_codebase()

# Generate report
print("\nGenerating audit report...")
report = auditor.generate_report()

# Print summary
print("\n" + "=" * 60)
print("Audit Summary")
print("=" * 60)
print(f"Total Findings: {report['total_findings']}")
print(f"\nBy Severity:")
for severity, count in report['by_severity'].items():
    print(f"  {severity.upper()}: {count}")
print(f"\nBy Type:")
for secret_type, count in report['by_type'].items():
    print(f"  {secret_type}: {count}")

# Save report
report_path = project_root / "data" / "secret_audit_report.json"
report_path.parent.mkdir(parents=True, exist_ok=True)
auditor.save_report(report_path)
print(f"\nReport saved to: {report_path}")

# Aggregate to R5
print("\nAggregating findings to R5...")
try:
    aggregate_to_r5(project_root, report)
    print("[SUCCESS] Findings aggregated to R5")
except Exception as e:
    print(f"[WARNING] R5 aggregation failed: {e}")

print("\n" + "=" * 60)
print("Audit Complete")
print("=" * 60)
print("\nNext Steps:")
print("1. Review findings in the audit report")
print("2. Migrate all secrets to Azure Key Vault")
print("3. Update code to retrieve secrets from Key Vault")
print("4. Remove secrets from codebase")

