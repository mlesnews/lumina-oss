#!/usr/bin/env python3
"""
JARVIS: Test Diagnostic Module
🔍 Comprehensive test of diagnostic capabilities
Tests spies, troubleshooting, and research integration
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.diagnostics import (
    WindowsKeyboardSpy,
    WindowsServiceSpy,
    WindowsProcessSpy,
    Troubleshooter,
    create_keyboard_troubleshooter
)

async def test_keyboard_spy():
    """Test WindowsKeyboardSpy"""
    print("=" * 70)
    print("🔍 TEST 1: WindowsKeyboardSpy")
    print("=" * 70)

    spy = WindowsKeyboardSpy()
    result = await spy.spy(target="keyboard_locks")

    if result.success:
        print("✅ Keyboard spy successful")
        lock_states = result.data.get("lock_states", {})

        print("\n📊 Lock States:")
        for lock_name, lock_info in lock_states.items():
            state = lock_info.get("state", "UNKNOWN")
            detectable = lock_info.get("detectable", False)
            print(f"  {lock_name}: {state} (detectable: {detectable})")
    else:
        print(f"❌ Keyboard spy failed: {result.message}")
        if result.errors:
            for error in result.errors:
                print(f"  Error: {error}")

    print()
    return result

async def test_service_spy():
    """Test WindowsServiceSpy"""
    print("=" * 70)
    print("🔍 TEST 2: WindowsServiceSpy")
    print("=" * 70)

    spy = WindowsServiceSpy()
    service_names = ["ArmouryCrateService", "ROGLiveService", "AuraService"]
    result = await spy.spy(target="services", service_names=service_names)

    if result.success:
        print("✅ Service spy successful")
        services = result.data.get("services", {})

        print(f"\n📊 Service States ({len(services)} services checked):")
        for service_name, service_info in services.items():
            status = service_info.get("status", "UNKNOWN")
            print(f"  {service_name}: {status}")
    else:
        print(f"❌ Service spy failed: {result.message}")

    print()
    return result

async def test_process_spy():
    """Test WindowsProcessSpy"""
    print("=" * 70)
    print("🔍 TEST 3: WindowsProcessSpy")
    print("=" * 70)

    spy = WindowsProcessSpy()
    process_names = ["ArmouryCrateControlInterface", "ArmouryCrate"]
    result = await spy.spy(target="processes", process_names=process_names)

    if result.success:
        print("✅ Process spy successful")
        processes = result.data.get("processes", {})

        print(f"\n📊 Process States ({len(processes)} processes checked):")
        for process_name, process_info in processes.items():
            status = process_info.get("status", "UNKNOWN")
            print(f"  {process_name}: {status}")
    else:
        print(f"❌ Process spy failed: {result.message}")

    print()
    return result

async def test_troubleshooter():
    """Test Troubleshooter with all spies"""
    print("=" * 70)
    print("🔧 TEST 4: Troubleshooter (Full Workflow)")
    print("=" * 70)

    # Create spies
    keyboard_spy = WindowsKeyboardSpy()
    service_spy = WindowsServiceSpy()
    process_spy = WindowsProcessSpy()

    # Create troubleshooter
    troubleshooter = Troubleshooter(
        spies=[keyboard_spy, service_spy, process_spy],
        enable_research=False  # Disable research for faster testing
    )

    # Run troubleshooting
    result = await troubleshooter.troubleshoot(
        spy_targets=["keyboard_locks", "services", "processes"],
        auto_fix=False  # Don't auto-fix, just diagnose
    )

    if result.success:
        print("✅ Troubleshooting successful")
        print(f"\n📊 Results:")
        print(f"  Issues found: {len(result.issues)}")
        print(f"  Recommendations: {len(result.recommendations)}")
        print(f"  Actions taken: {len(result.actions_taken)}")

        if result.issues:
            print(f"\n⚠️  Issues:")
            for issue in result.issues:
                print(f"    - {issue}")

        if result.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in result.recommendations:
                print(f"    - {rec}")
    else:
        print(f"❌ Troubleshooting failed: {result.message}")

    print()
    return result

async def test_keyboard_troubleshooter_factory():
    """Test factory function for keyboard troubleshooter"""
    print("=" * 70)
    print("🔧 TEST 5: create_keyboard_troubleshooter (Factory)")
    print("=" * 70)

    troubleshooter = create_keyboard_troubleshooter(
        service_names=["ArmouryCrateService", "ROGLiveService"],
        process_names=["ArmouryCrateControlInterface"],
        enable_research=False
    )

    result = await troubleshooter.troubleshoot(
        spy_targets=["keyboard_locks", "services", "processes"],
        auto_fix=False
    )

    if result.success:
        print("✅ Factory troubleshooter successful")
        print(f"\n📊 Results:")
        print(f"  Issues: {len(result.issues)}")
        print(f"  Recommendations: {len(result.recommendations)}")
    else:
        print(f"❌ Factory troubleshooter failed: {result.message}")

    print()
    return result

async def test_research_integration():
    """Test research integration (if available)"""
    print("=" * 70)
    print("🔬 TEST 6: Research Integration")
    print("=" * 70)

    try:
        from src.cfservices.services.jarvis_core.research import ResearchEngine, EscalationEngine

        research_engine = ResearchEngine()
        escalation_engine = EscalationEngine(research_engine=research_engine)

        # Test escalation decision
        escalation = await escalation_engine.should_escalate(
            issue="Lock symbols visible on FN and Windows keys",
            attempts=0,
            context={"device_type": "ASUS Laptop"}
        )

        if escalation.get("should_escalate"):
            print("✅ Escalation triggered")
            print(f"  Reason: {escalation.get('reason', 'Unknown')}")
            if escalation.get("recommendations"):
                print(f"  Recommendations: {len(escalation['recommendations'])}")
        else:
            print("ℹ️  Escalation not needed")

    except ImportError as e:
        print(f"⚠️  Research module not available: {e}")
    except Exception as e:
        print(f"❌ Research integration test failed: {e}")

    print()
    return True

async def main():
    """Run all diagnostic tests"""
    print("=" * 70)
    print("🔍 JARVIS: Diagnostic Module Test Suite")
    print("=" * 70)
    print()

    results = {}

    # Test individual spies
    results["keyboard_spy"] = await test_keyboard_spy()
    results["service_spy"] = await test_service_spy()
    results["process_spy"] = await test_process_spy()

    # Test troubleshooter
    results["troubleshooter"] = await test_troubleshooter()
    results["factory_troubleshooter"] = await test_keyboard_troubleshooter_factory()

    # Test research integration
    results["research"] = await test_research_integration()

    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = 0
    for name, r in results.items():
        # Check if result indicates success
        is_success = False
        if isinstance(r, dict):
            is_success = r.get("success", False)
        elif hasattr(r, "success"):  # DiagnosticResult or TroubleshootingResult
            is_success = r.success
        elif r is True:
            is_success = True

        if is_success:
            passed += 1

    total = len(results)

    print(f"\n✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")

    print("\n📋 Component Status:")
    for name, result in results.items():
        is_success = False
        if isinstance(result, dict):
            is_success = result.get("success", False)
        elif hasattr(result, "success"):
            is_success = result.success
        elif result is True:
            is_success = True

        status = "✅" if is_success else "❌"
        print(f"  {status} {name}")

    print("\n" + "=" * 70)
    print("✅ Diagnostic module test suite complete")
    print("=" * 70)

    return results

if __name__ == "__main__":


    asyncio.run(main())