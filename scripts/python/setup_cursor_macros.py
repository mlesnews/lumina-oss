#!/usr/bin/env python3
"""
Setup Cursor IDE Macros and Triggers
Configures tasks and keybindings for MANUS automation
#JARVIS #CURSOR #MACROS #SETUP
"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_tasks_and_keybindings():
    """Verify tasks and keybindings are correctly configured"""
    tasks_file = project_root / ".cursor" / "tasks.json"
    keybindings_file = project_root / ".cursor" / "keybindings.json"

    print("=" * 70)
    print("   CURSOR MACROS & TRIGGERS VERIFICATION")
    print("=" * 70)
    print("")

    # Check tasks
    if tasks_file.exists():
        try:
            with open(tasks_file) as f:
                tasks = json.load(f)
            print("✅ tasks.json is valid")
            print(f"   Found {len(tasks.get('tasks', []))} tasks")
            print("")
            print("Available Tasks:")
            for task in tasks.get("tasks", []):
                print(f"   - {task.get('label', 'Unknown')}")
        except Exception as e:
            print(f"❌ tasks.json error: {e}")
    else:
        print("❌ tasks.json not found")

    print("")

    # Check keybindings
    if keybindings_file.exists():
        try:
            with open(keybindings_file) as f:
                keybindings = json.load(f)
            print("✅ keybindings.json is valid")
            print(f"   Found {len(keybindings)} keybindings")
            print("")
            print("Screenshot Keybindings:")
            for kb in keybindings:
                if "screenshot" in kb.get("args", "").lower() or "Screenshot" in str(kb.get("args", "")):
                    print(f"   {kb.get('key', 'Unknown')} → {kb.get('args', 'Unknown')}")
        except Exception as e:
            print(f"❌ keybindings.json error: {e}")
    else:
        print("❌ keybindings.json not found")

    print("")
    print("=" * 70)
    print("   USAGE")
    print("=" * 70)
    print("")
    print("Keyboard Shortcuts:")
    print("  Ctrl+Shift+S  → Quick Screenshot")
    print("  Ctrl+Shift+C  → Screenshot with Context")
    print("  Ctrl+Alt+S    → Full Screenshot")
    print("")
    print("Command Palette:")
    print("  1. Press Ctrl+Shift+P")
    print("  2. Type: 'Tasks: Run Task'")
    print("  3. Select task from list")
    print("")
    print("=" * 70)
    print("")


if __name__ == "__main__":
    verify_tasks_and_keybindings()
