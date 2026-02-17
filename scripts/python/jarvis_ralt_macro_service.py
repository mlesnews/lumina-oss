#!/usr/bin/env python3
"""
JARVIS RAlt Macro Service
Background service to run RAlt hybrid macro system continuously

Tags: #JARVIS #SERVICE #MACRO #VOICE @JARVIS @DOIT
"""

import sys
import signal
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_ralt_hybrid_macro import JARVISRAltHybridMacro

def main():
    """Run RAlt macro service"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS RAlt Macro Service")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--background", action="store_true", help="Run in background (non-interactive)")

    args = parser.parse_args()

    macro = JARVISRAltHybridMacro(project_root=args.project_root)

    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down RAlt macro service...")
        macro.stop_listening()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if macro.start_listening():
        if args.background:
            print("✅ RAlt macro service running in background")
            print("Press Right Alt to activate hybrid macro")
            # Keep running
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                signal_handler(None, None)
        else:
            print("✅ RAlt macro service active")
            print("Press Right Alt to activate hybrid macro")
            print("Press Ctrl+C to stop...")
            try:
                import keyboard
                keyboard.wait()
            except KeyboardInterrupt:
                signal_handler(None, None)
    else:
        print("❌ Failed to start RAlt macro service")
        sys.exit(1)

if __name__ == "__main__":


    main()