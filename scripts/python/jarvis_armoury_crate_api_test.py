#!/usr/bin/env python3
"""
JARVIS Armoury Crate API Test
Test tight integration with Armoury Crate AI/API

@JARVIS @ARMOURY_CRATE @API @TEST
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

logger = get_logger("ArmouryCrateAPITest")


async def test_api_integration():
    """Test Armoury Crate API integration"""
    print("=" * 70)
    print("🔌 ARMOURY CRATE API INTEGRATION TEST")
    print("=" * 70)
    print()

    try:
        from src.cfservices.services.jarvis_core.integrations.armoury_crate_api import create_armoury_crate_api

        # Create API instance
        print("📡 Initializing Armoury Crate API...")
        api = create_armoury_crate_api(project_root=project_root)
        print("✅ API initialized")
        print()

        # Test 1: List devices
        print("🔍 Test 1: List devices...")
        response = await api.call_api("/devices")
        if response.success:
            print(f"✅ Found {response.data.get('count', 0)} devices")
            for device in response.data.get("devices", [])[:5]:  # Show first 5
                print(f"   - {device.get('name', 'Unknown')} ({device.get('device_type', 'unknown')})")
        else:
            print(f"⚠️  Device listing failed: {response.error}")
        print()

        # Test 2: Get lighting state
        print("💡 Test 2: Get lighting state...")
        response = await api.call_api("/lighting", method="GET")
        if response.success:
            print("✅ Lighting state retrieved")
            lighting = response.data.get("lighting", {})
            if lighting:
                print(f"   Lighting zones: {len(lighting)}")
            else:
                print("   No lighting data available")
        else:
            print(f"⚠️  Lighting query failed: {response.error}")
        print()

        # Test 3: AI prediction
        print("🤖 Test 3: AI prediction...")
        response = await api.call_api("/ai/predict", method="POST", data={
            "type": "action",
            "context": {"device": "keyboard", "action": "set_lighting"}
        })
        if response.success:
            prediction = response.data.get("prediction", {})
            print(f"✅ AI prediction generated")
            print(f"   Predicted action: {prediction.get('predicted_action', 'N/A')}")
            print(f"   Confidence: {prediction.get('confidence', 0):.2%}")
        else:
            print(f"⚠️  AI prediction failed: {response.error}")
        print()

        # Test 4: Device control (if devices available)
        if api.devices:
            device_id = list(api.devices.keys())[0]
            print(f"🎮 Test 4: Control device ({device_id})...")
            response = await api.call_api(
                f"/devices/{device_id}/state",
                method="GET"
            )
            if response.success:
                print("✅ Device state retrieved")
                state = response.data.get("state", {})
                if state:
                    print(f"   State keys: {list(state.keys())[:5]}")
            else:
                print(f"⚠️  Device control failed: {response.error}")
            print()

        print("=" * 70)
        print("✅ API INTEGRATION TEST COMPLETE")
        print("=" * 70)

    except ImportError as e:
        print(f"❌ API module not available: {e}")
        print("   Install required dependencies or check module path")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_api_integration())
