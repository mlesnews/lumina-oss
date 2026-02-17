#!/usr/bin/env python3
"""Test Grammarly Desktop integration with JARVIS"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_unified_api import JARVISUnifiedAPI
    from jarvis_grammarly_desktop_integration import JARVISGrammarlyDesktopBridge

    print("=" * 80)
    print("🧪 TESTING GRAMMARLY DESKTOP INTEGRATION")
    print("=" * 80)
    print()

    # Test JARVIS Unified API registration
    print("Testing JARVIS Unified API registration...")
    api = JARVISUnifiedAPI()
    print(f"✅ Registered systems: {len(api.registered_systems)}")
    for sys_id, sys_info in api.registered_systems.items():
        print(f"  - {sys_info['system_name']} ({sys_id})")
    print()

    # Test Grammarly Bridge
    print("Testing Grammarly Desktop Bridge...")
    bridge = JARVISGrammarlyDesktopBridge()
    status = bridge.get_integration_status()
    print(f"✅ Bridge initialized")
    print(f"   Auto-check: {status['auto_check_enabled']}")
    print(f"   Auto-improve: {status['auto_improve_jarvis']}")
    print()

    # Test text checking
    print("Testing text checking...")
    test_text = "This is a test text with some grammer errors."
    result = bridge.check_text(test_text)
    print(f"✅ Checked text")
    print(f"   Score: {result['score']:.0%}")
    print(f"   Suggestions: {result['suggestions_count']}")
    print()

    print("=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
