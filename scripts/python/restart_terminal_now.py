#!/usr/bin/env python3
"""
Restart Terminal Now

Immediately restarts the current terminal using keyboard shortcuts.
Run this in the terminal with the orange triangle to restart it.

Tags: #TERMINAL #RESTART #IMMEDIATE @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from terminal_restart_manager import restart_terminal_aggressive
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from terminal_restart_manager import restart_terminal_aggressive
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)
        restart_terminal_aggressive = None

logger = get_logger("RestartTerminalNow")

print("🔄 Restarting terminal NOW...", flush=True)
print("   This will close and reopen the terminal to fix the orange triangle.", flush=True)
print("", flush=True)

if restart_terminal_aggressive:
    try:
        success = restart_terminal_aggressive()
        if success:
            print("✅ Terminal restart initiated!", flush=True)
            print("   The terminal should close and reopen shortly.", flush=True)
        else:
            print("⚠️  Terminal restart may have failed.", flush=True)
            print("   Try running this script again.", flush=True)
    except Exception as e:
        print(f"❌ Error restarting terminal: {e}", flush=True)
        print("   You may need to manually close and reopen the terminal.", flush=True)
else:
    print("❌ Terminal restart manager not available", flush=True)
    print("   Please manually close and reopen the terminal (Ctrl+Shift+` twice)", flush=True)
