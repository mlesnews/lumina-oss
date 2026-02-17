#!/usr/bin/env python3
"""
JARVIS Execute Shortcut - Quick Command Line Tool

Quick way to execute any mapped keyboard shortcut from command line.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_use_mapped_shortcuts import JARVISShortcutExecutor

def main():
    """Execute shortcut from command line"""
    if len(sys.argv) < 2:
        print("Usage: python jarvis_execute_shortcut.py <command>")
        print()
        print("Examples:")
        print("  python jarvis_execute_shortcut.py 'open chat'")
        print("  python jarvis_execute_shortcut.py 'save file'")
        print("  python jarvis_execute_shortcut.py 'format code'")
        print("  python jarvis_execute_shortcut.py 'accept all changes'")
        sys.exit(1)

    command = ' '.join(sys.argv[1:])

    executor = JARVISShortcutExecutor()
    success = executor.execute_shortcut(command)

    if success:
        print("✅ Command executed successfully")
        sys.exit(0)
    else:
        print("❌ Command failed or not found")
        sys.exit(1)

if __name__ == "__main__":


    main()