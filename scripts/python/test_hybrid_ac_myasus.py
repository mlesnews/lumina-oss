#!/usr/bin/env python3
"""
Test ASUS Unified Integration (@ASUS_UI)
AC + MyASUS unified interface

@JARVIS @ASUS_UNIFIED @ASUS_UI @TEST
"""

import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HybridACMyASUSTest")


async def test_hybrid_integration():
    """Test the hybrid AC + MyASUS integration"""
    print("=" * 70)
    print("🔌 ASUS UNIFIED INTEGRATION TEST (@ASUS_UI)")
    print("=" * 70)
    print()

    try:
        from src.cfservices.services.jarvis_core.integrations.armoury_crate_myasus_hybrid import create_hybrid_integration

        # Create unified integration instance
        print("📡 Initializing ASUS Unified Integration (@ASUS_UI)...")
        hybrid = create_hybrid_integration(project_root=project_root)
        print(f"   Armoury Crate: {'✅' if hybrid.ac_available else '❌'}")
        print(f"   MyASUS: {'✅' if hybrid.myasus_available else '❌'}")
        print()

        # Test 1: Get capabilities
        print("🔍 Test 1: Get Capabilities...")
        capabilities = hybrid.get_capabilities()
        print(f"   AC Available: {capabilities['armoury_crate']['available']}")
        print(f"   MyASUS Available: {capabilities['myasus']['available']}")
        print(f"   Hybrid Available: {capabilities['hybrid']['available']}")
        print()

        # Test 2: MyASUS Diagnostics
        if hybrid.myasus_available:
            print("🔍 Test 2: MyASUS Diagnostics...")
            response = await hybrid.process_request({
                "action": "myasus_diagnostics",
                "source": "myasus"
            })
            if response.success:
                print(f"   ✅ Diagnostics completed")
                diag = response.data.get("diagnostics", {})
                if diag:
                    print(f"   System: {diag.get('system_info', {}).get('os', 'Unknown')}")
            else:
                print(f"   ⚠️  Diagnostics failed: {response.error}")
            print()

        # Test 3: MyASUS Device Info
        if hybrid.myasus_available:
            print("🔍 Test 3: MyASUS Device Info...")
            response = await hybrid.process_request({
                "action": "myasus_device_info",
                "source": "myasus"
            })
            if response.success:
                print(f"   ✅ Device info retrieved")
                device = response.data.get("device", {})
                if device:
                    print(f"   Model: {device.get('model', 'Unknown')}")
                    print(f"   Serial: {device.get('serial', 'Unknown')}")
            else:
                print(f"   ⚠️  Device info failed: {response.error}")
            print()

        # Test 4: Hybrid Request (both AC + MyASUS)
        print("🔍 Test 4: Hybrid Request (AC + MyASUS)...")
        response = await hybrid.process_request({
            "action": "hybrid",
            "source": "auto"
        })
        if response.success:
            print(f"   ✅ Hybrid data retrieved")
            data = response.data
            if "armoury_crate" in data:
                ac_data = data["armoury_crate"]
                print(f"   AC: {'Available' if ac_data.get('available') else 'Not available'}")
            if "myasus" in data:
                myasus_data = data["myasus"]
                print(f"   MyASUS: {'Available' if myasus_data.get('available') else 'Not available'}")
        else:
            print(f"   ⚠️  Hybrid request failed: {response.error}")
        print()

        # Test 5: Armoury Crate Lighting (if available)
        if hybrid.ac_available:
            print("🔍 Test 5: Armoury Crate Lighting...")
            response = await hybrid.process_request({
                "action": "ac_lighting",
                "source": "armoury_crate"
            })
            if response.success:
                print(f"   ✅ Lighting state retrieved")
            else:
                print(f"   ⚠️  Lighting query failed: {response.error}")
            print()

        print("=" * 70)
        print("✅ HYBRID INTEGRATION TEST COMPLETE")
        print("=" * 70)

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("   Make sure the hybrid integration module is available")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_hybrid_integration())
