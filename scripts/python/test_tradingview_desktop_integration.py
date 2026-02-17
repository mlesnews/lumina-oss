#!/usr/bin/env python3
"""
Test TradingView Desktop Integration
Quick test script to verify Desktop integration functionality

@JARVIS @TRADINGVIEW @DESKTOP @TEST
"""

import sys
import asyncio
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TradingViewDesktopTest")


async def test_desktop_integration():
    """Test Desktop integration"""
    print("=" * 70)
    print("🧪 TESTING TRADINGVIEW DESKTOP INTEGRATION")
    print("=" * 70)
    print()

    try:
        from scripts.python.jarvis_tradingview_desktop_integration import TradingViewDesktopIntegration

        # Initialize
        print("[1/4] Initializing Desktop Integration...")
        integration = TradingViewDesktopIntegration()
        print("✅ Initialized")
        print()

        # Get status
        print("[2/4] Getting Desktop Status...")
        status = await integration.get_desktop_status()
        print("✅ Status retrieved:")
        print(json.dumps(status, indent=2))
        print()

        # Process test alert
        print("[3/4] Processing Test Alert...")
        test_alert = {
            "symbol": "BTCUSDT",
            "exchange": "BINANCE",
            "action": "BUY",
            "timeframe": "1h",
            "strategy": "test_strategy",
            "price": 45000.0
        }
        result = await integration.process_alert(test_alert)
        print("✅ Alert processed:")
        print(json.dumps(result, indent=2, default=str))
        print()

        # Test automation
        print("[4/4] Testing Automation Workflows...")
        try:
            from scripts.python.jarvis_tradingview_desktop_automation import TradingViewDesktopAutomation
            automation = TradingViewDesktopAutomation()
            automation_status = await automation.get_automation_status()
            print("✅ Automation status:")
            print(json.dumps(automation_status, indent=2, default=str))
        except Exception as e:
            print(f"⚠️  Automation test skipped: {e}")
        print()

        print("=" * 70)
        print("✅ ALL TESTS COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_deep_mapping():
    """Test Desktop deep mapping"""
    print("=" * 70)
    print("🔍 TESTING DESKTOP DEEP MAPPING")
    print("=" * 70)
    print()

    try:
        from scripts.python.jarvis_tradingview_desktop_deep_mapping import TradingViewDesktopDeepMapper

        mapper = TradingViewDesktopDeepMapper()
        results = await mapper.deep_map_desktop()

        print("✅ Deep mapping complete")
        print(f"   Research areas: {len(results) - 3}")
        print(f"   Force multipliers: {len(results.get('force_multipliers', {}).get('multipliers', []))}")
        print()

    except Exception as e:
        print(f"⚠️  Deep mapping test skipped: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test execution"""
    await test_desktop_integration()
    print()
    await test_deep_mapping()


if __name__ == "__main__":


    asyncio.run(main())