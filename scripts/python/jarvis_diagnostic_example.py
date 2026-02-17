#!/usr/bin/env python3
"""
JARVIS: Diagnostic Module Usage Examples
🔍 Examples of how to use the diagnostic module
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

async def example_1_simple_spy():
    """Example 1: Simple spy usage"""
    print("=" * 70)
    print("📖 EXAMPLE 1: Simple Keyboard Spy")
    print("=" * 70)
    print()

    spy = WindowsKeyboardSpy()
    result = await spy.spy(target="keyboard_locks")

    if result.success:
        lock_states = result.data["lock_states"]
        print("Current lock states:")
        for lock_name, lock_info in lock_states.items():
            print(f"  {lock_name}: {lock_info['state']}")
    else:
        print(f"Error: {result.message}")

    print()

async def example_2_multiple_spies():
    """Example 2: Using multiple spies"""
    print("=" * 70)
    print("📖 EXAMPLE 2: Multiple Spies")
    print("=" * 70)
    print()

    # Create spies
    keyboard_spy = WindowsKeyboardSpy()
    service_spy = WindowsServiceSpy()
    process_spy = WindowsProcessSpy()

    # Check keyboard locks
    print("1. Checking keyboard locks...")
    kb_result = await keyboard_spy.spy(target="keyboard_locks")
    if kb_result.success:
        print("   ✅ Keyboard locks checked")

    # Check services
    print("2. Checking services...")
    svc_result = await service_spy.spy(
        target="services",
        service_names=["ArmouryCrateService"]
    )
    if svc_result.success:
        services = svc_result.data.get("services", {})
        for name, info in services.items():
            print(f"   {name}: {info.get('status', 'Unknown')}")

    # Check processes
    print("3. Checking processes...")
    proc_result = await process_spy.spy(
        target="processes",
        process_names=["ArmouryCrateControlInterface"]
    )
    if proc_result.success:
        processes = proc_result.data.get("processes", {})
        for name, info in processes.items():
            print(f"   {name}: {info.get('status', 'Unknown')}")

    print()

async def example_3_troubleshooter():
    """Example 3: Using Troubleshooter"""
    print("=" * 70)
    print("📖 EXAMPLE 3: Troubleshooter (Full Workflow)")
    print("=" * 70)
    print()

    # Create spies
    keyboard_spy = WindowsKeyboardSpy()
    service_spy = WindowsServiceSpy()
    process_spy = WindowsProcessSpy()

    # Create troubleshooter
    troubleshooter = Troubleshooter(
        spies=[keyboard_spy, service_spy, process_spy],
        enable_research=False  # Disable for faster execution
    )

    # Run troubleshooting
    result = await troubleshooter.troubleshoot(
        spy_targets=["keyboard_locks", "services", "processes"],
        auto_fix=False  # Just diagnose, don't fix
    )

    print(f"Troubleshooting Results:")
    print(f"  Issues: {len(result.issues)}")
    print(f"  Recommendations: {len(result.recommendations)}")

    if result.issues:
        print("\nIssues found:")
        for issue in result.issues:
            print(f"  - {issue}")

    if result.recommendations:
        print("\nRecommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")

    print()

async def example_4_factory_function():
    """Example 4: Using factory function"""
    print("=" * 70)
    print("📖 EXAMPLE 4: Factory Function (Quick Setup)")
    print("=" * 70)
    print()

    # Use factory function for quick setup
    troubleshooter = create_keyboard_troubleshooter(
        service_names=["ArmouryCrateService"],
        process_names=["ArmouryCrateControlInterface"],
        enable_research=False
    )

    # Run troubleshooting
    result = await troubleshooter.troubleshoot(
        spy_targets=["keyboard_locks", "services", "processes"],
        auto_fix=False
    )

    print(f"Factory Troubleshooter Results:")
    print(f"  Issues: {len(result.issues)}")
    print(f"  Recommendations: {len(result.recommendations)}")
    print()

async def example_5_custom_analyzer():
    """Example 5: Custom analyzer"""
    print("=" * 70)
    print("📖 EXAMPLE 5: Custom Analyzer")
    print("=" * 70)
    print()

    def custom_analyzer(diagnostics: dict) -> list:
        """Custom analyzer that checks for specific conditions"""
        issues = []

        # Check if Num Lock is ON
        if "keyboard_locks" in diagnostics:
            lock_states = diagnostics["keyboard_locks"].get("lock_states", {})
            if lock_states.get("num_lock", {}).get("state") == "ON":
                issues.append("Num Lock is ON - may interfere with keyboard shortcuts")

        # Check if critical services are missing
        if "services" in diagnostics:
            services = diagnostics["services"].get("services", {})
            if services.get("ArmouryCrateService", {}).get("status") != "Found":
                issues.append("ArmouryCrateService is not running")

        return issues

    # Create troubleshooter with custom analyzer
    keyboard_spy = WindowsKeyboardSpy()
    service_spy = WindowsServiceSpy()

    troubleshooter = Troubleshooter(
        spies=[keyboard_spy, service_spy],
        analyzers=[custom_analyzer],
        enable_research=False
    )

    result = await troubleshooter.troubleshoot(
        spy_targets=["keyboard_locks", "services"],
        auto_fix=False
    )

    print(f"Custom Analyzer Results:")
    print(f"  Issues: {len(result.issues)}")
    for issue in result.issues:
        print(f"    - {issue}")
    print()

async def main():
    """Run all examples"""
    print("=" * 70)
    print("📚 JARVIS: Diagnostic Module Usage Examples")
    print("=" * 70)
    print()

    await example_1_simple_spy()
    await example_2_multiple_spies()
    await example_3_troubleshooter()
    await example_4_factory_function()
    await example_5_custom_analyzer()

    print("=" * 70)
    print("✅ All examples complete")
    print("=" * 70)

if __name__ == "__main__":


    asyncio.run(main())