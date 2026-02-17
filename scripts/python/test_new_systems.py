#!/usr/bin/env python3
"""
Test New Systems - Priority 1 Testing

Tests the newly implemented systems:
- Recursive Experiment Detector
- MANUS Restrictions
- Complete Workflow Chain
- Penalty System Integration
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("🧪 TESTING NEW SYSTEMS - Priority 1")
print("=" * 70)
print()

# Test 1: Recursive Experiment Detector
print("Test 1: Recursive Experiment Detector")
print("-" * 70)
try:
    from scripts.python.jarvis_recursive_experiment_detector import get_experiment_detector

    detector = get_experiment_detector(project_root)

    # Test experimental action
    blocked1, trans1, penalty1 = detector.assess_and_penalize(
        'test_cursor_ide_experiment',
        'cursor_ide'
    )
    print(f"✅ Experimental Action Test: {'BLOCKED' if blocked1 else 'ALLOWED'}")
    if blocked1:
        print(f"   Penalty: -{penalty1}")
        print(f"   Pattern: {trans1.pattern_type if trans1 else 'N/A'}")

    # Test recursive action
    blocked2, trans2, penalty2 = detector.assess_and_penalize(
        'recursive_loop_test',
        'system'
    )
    print(f"✅ Recursive Action Test: {'BLOCKED' if blocked2 else 'ALLOWED'}")
    if blocked2:
        print(f"   Penalty: -{penalty2}")
        print(f"   Pattern: {trans2.pattern_type if trans2 else 'N/A'}")

    # Get summary
    summary = detector.get_transgression_summary(hours=1)
    print(f"✅ Transgression Summary: {summary['total']} violations, -{summary['total_penalty']} total penalty")

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: MANUS Restrictions
print("Test 2: MANUS Restrictions")
print("-" * 70)
try:
    from scripts.python.manus_unified_control import MANUSUnifiedControl, ControlArea, ControlOperation

    control = MANUSUnifiedControl(project_root=project_root)

    # Test IDE control operation
    op = ControlOperation(
        operation_id='test_1',
        area=ControlArea.IDE_CONTROL,
        action='test_cursor_ide',
        parameters={}
    )

    result = control.execute_operation(op)
    print(f"✅ MANUS Operation Test: {'BLOCKED' if not result.success else 'ALLOWED'}")
    print(f"   Message: {result.message}")
    if not result.success:
        print(f"   Errors: {result.errors}")

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Complete Workflow Chain
print("Test 3: Complete Workflow Chain Initialization")
print("-" * 70)
try:
    from scripts.python.jarvis_execute_complete_workflow import JARVISCompleteWorkflowChain

    chain = JARVISCompleteWorkflowChain(project_root=project_root)

    print(f"✅ WOPR Operations: {'Available' if chain.wopr_ops else 'Not Available'}")
    print(f"✅ SYPHON Troubleshooter: {'Available' if chain.syphon_troubleshooter else 'Not Available'}")
    print(f"✅ @ASKChain SYPHON: {'Available' if chain.askchain_syphon else 'Not Available'}")
    print(f"✅ Proactive Troubleshooter: {'Available' if chain.proactive_troubleshooter else 'Not Available'}")

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Penalty System
print("Test 4: Penalty System Integration")
print("-" * 70)
try:
    from scripts.python.jarvis_policy_violation_penalty import get_penalty_system

    penalty_system = get_penalty_system(project_root)

    print(f"✅ Penalty System: Initialized")
    print(f"   Current XP: {penalty_system.jarvis_xp.current_xp}")
    print(f"   Total Penalties: {penalty_system.jarvis_xp.total_penalties}")
    print(f"   Violations Count: {penalty_system.jarvis_xp.violations_count}")

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("✅ TESTING COMPLETE")
print("=" * 70)
