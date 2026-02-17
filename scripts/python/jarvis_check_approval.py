#!/usr/bin/env python3
"""
JARVIS: Check Workflow Approval
Checks if approval exists for @cr, @helpdesk, @workflows based on #decisioning + #troubleshooting rule

@JARVIS @TEAM #decisioning #troubleshooting @cr @helpdesk @workflows
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.workflow_approval import (
    has_approval_for_operation,
    has_approval_for_code_review,
    has_approval_for_helpdesk,
    has_approval_for_workflows,
    check_decisioning_capability,
    check_troubleshooting_capability
)

def main():
    """Check approval status for all operations"""
    print("=" * 70)
    print("🔐 JARVIS: Workflow Approval Check")
    print("=" * 70)
    print()
    print("Rule: #decisioning + #troubleshooting = approval for @cr @helpdesk @workflows")
    print()
    print("-" * 70)

    # Check capabilities
    decisioning = check_decisioning_capability()
    troubleshooting = check_troubleshooting_capability()

    print("📊 Capability Status:")
    print(f"  ✅ #decisioning: {'ACTIVE' if decisioning else 'INACTIVE'}")
    print(f"  ✅ #troubleshooting: {'ACTIVE' if troubleshooting else 'INACTIVE'}")
    print()

    # Check approvals
    print("-" * 70)
    print("🔐 Approval Status:")
    print()

    operations = [
        ("@cr", "Code Review"),
        ("@helpdesk", "Helpdesk Operations"),
        ("@workflows", "Workflow Execution")
    ]

    for op_type, op_name in operations:
        approval = has_approval_for_operation(op_type, project_root)
        status = "✅ APPROVED" if approval["approved"] else "❌ DENIED"
        print(f"  {status} {op_name} ({op_type})")
        print(f"    Reason: {approval['reason']}")
        print()

    print("=" * 70)

    # Summary
    all_approved = all(
        has_approval_for_operation(op_type, project_root)["approved"]
        for op_type, _ in operations
    )

    if all_approved:
        print("✅ All operations approved")
    else:
        print("⚠️  Some operations require approval")
        print("   Ensure both #decisioning and #troubleshooting are active")

    print("=" * 70)

if __name__ == "__main__":


    main()