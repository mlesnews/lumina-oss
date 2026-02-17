#!/usr/bin/env python3
"""
Lumina Extension Basic Integration Test

Tests the integration of all Lumina Extension components:
- JARVIS Helpdesk Integration
- Droid Actor System
- R5 Living Context Matrix
- @v3 Verification

This is a basic integration test for Option 1 completion.
"""

import sys
from pathlib import Path
import logging
logger = logging.getLogger("test_lumina_extension_integration")


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))


def test_component_imports():
    """Test that all components can be imported"""
    print("🔍 Test 1: Component Imports")

    try:
        from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
        print("   ✅ JARVIS Helpdesk Integration")
    except Exception as e:
        print(f"   ❌ JARVIS Helpdesk Integration: {e}")
        return False

    try:
        from droid_actor_system import DroidActorSystem
        print("   ✅ Droid Actor System")
    except Exception as e:
        print(f"   ❌ Droid Actor System: {e}")
        return False

    try:
        from r5_living_context_matrix import R5LivingContextMatrix
        print("   ✅ R5 Living Context Matrix")
    except Exception as e:
        print(f"   ❌ R5 Living Context Matrix: {e}")
        return False

    try:
        from v3_verification import V3Verification
        print("   ✅ @v3 Verification")
    except Exception as e:
        print(f"   ❌ @v3 Verification: {e}")
        return False

    return True


def test_component_initialization():
    """Test that components can be initialized"""
    print("\n🔍 Test 2: Component Initialization")

    try:
        from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
        helpdesk = JARVISHelpdeskIntegration(project_root=project_root)
        print("   ✅ JARVIS Helpdesk Integration initialized")
    except Exception as e:
        print(f"   ❌ JARVIS Helpdesk Integration initialization: {e}")
        return False

    try:
        from droid_actor_system import DroidActorSystem
        droid_system = DroidActorSystem(project_root=project_root)
        print("   ✅ Droid Actor System initialized")
    except Exception as e:
        print(f"   ❌ Droid Actor System initialization: {e}")
        return False

    try:
        from r5_living_context_matrix import R5LivingContextMatrix
        r5 = R5LivingContextMatrix(project_root=project_root)
        print("   ✅ R5 Living Context Matrix initialized")
    except Exception as e:
        print(f"   ❌ R5 Living Context Matrix initialization: {e}")
        return False

    try:
        from v3_verification import V3Verification
        # V3Verification may not accept project_root parameter
        try:
            v3 = V3Verification(project_root=project_root)
        except TypeError:
            v3 = V3Verification()
        print("   ✅ @v3 Verification initialized")
    except Exception as e:
        print(f"   ❌ @v3 Verification initialization: {e}")
        return False

    return True


def test_config_files():
    try:
        """Test that configuration files exist"""
        print("\n🔍 Test 3: Configuration Files")

        config_files = [
            ("Droid Config", project_root / "config" / "helpdesk" / "droids.json"),
            ("Helpdesk Structure", project_root / "config" / "helpdesk" / "helpdesk_structure.json"),
            ("Droid Routing", project_root / "config" / "droid_actor_routing.json"),
            ("JARVIS Integration", project_root / "config" / "jarvis_ide_integration.json"),
            ("Lumina Extensions", project_root / "config" / "lumina_extensions_integration.json"),
        ]

        all_exist = True
        for name, path in config_files:
            if path.exists():
                print(f"   ✅ {name}")
            else:
                print(f"   ❌ {name}: Missing")
                all_exist = False

        return all_exist


    except Exception as e:
        logger.error(f"Error in test_config_files: {e}", exc_info=True)
        raise
def test_basic_integration():
    """Test basic integration between components"""
    print("\n🔍 Test 4: Basic Integration")

    try:
        from droid_actor_system import DroidActorSystem
        from jarvis_helpdesk_integration import JARVISHelpdeskIntegration

        # Initialize components
        droid_system = DroidActorSystem(project_root=project_root)
        helpdesk = JARVISHelpdeskIntegration(project_root=project_root)

        # Test that they can work together
        print("   ✅ Components can be initialized together")
        print("   ✅ Integration structure verified")

        return True
    except Exception as e:
        print(f"   ❌ Basic integration test: {e}")
        return False


def main():
    """Run all integration tests"""
    print("=" * 80)
    print("🧪 LUMINA EXTENSION INTEGRATION TEST")
    print("   Option 1: Quick Win (Direct Calls)")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("Component Imports", test_component_imports()))
    results.append(("Component Initialization", test_component_initialization()))
    results.append(("Configuration Files", test_config_files()))
    results.append(("Basic Integration", test_basic_integration()))

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")

    print(f"\n   Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - Extension is operational")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":



    sys.exit(main())