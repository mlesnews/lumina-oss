#!/usr/bin/env python3
"""Quick test of RAlt macro integration"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_ralt_hybrid_macro import JARVISRAltHybridMacro

def main():
    print("Testing RAlt Hybrid Macro Integration...")

    macro = JARVISRAltHybridMacro()
    result = macro.execute_hybrid_macro('work_shift')

    success = result.get('success', False)
    print(f"\n✅ Success: {success}")

    if success:
        print("✅ Voice Activation:", result.get('voice_activation'))
        print("✅ Greeting:", result.get('greeting'))
        print("✅ Roundtable:", result.get('roundtable'))
        print("\n🎉 RAlt Hybrid Macro System is WORKING!")
    else:
        print("❌ Some components failed")
        print(f"Error: {result.get('error', 'Unknown')}")

    return 0 if success else 1

if __name__ == "__main__":


    sys.exit(main())