#!/usr/bin/env python3
"""
Show All VAs - Quick Display Script

Quick script to make all VAs visible, especially Iron Man VAs.

Tags: #QUICK #DISPLAY #VISIBILITY @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from va_visibility_system import VAVisibilitySystem

if __name__ == "__main__":
    print("=" * 80)
    print("👁️  SHOWING ALL VAs")
    print("=" * 80)
    print()

    visibility = VAVisibilitySystem()

    # Ensure Iron Man VAs are visible first
    visibility.ensure_iron_man_vas_visible()

    # Show all VAs
    visibility.show_all_vas()

    # Show status
    status = visibility.get_va_visibility_status()

    print("=" * 80)
    print("✅ ALL VAs NOW VISIBLE")
    print("=" * 80)
    print()
    print("Visible VAs:")
    for va_info in status["visible_vas"]:
        if va_info["visible"]:
            print(f"  ✅ {va_info['name']} ({va_info['va_id']})")
    print()
