#!/usr/bin/env python3
"""
Start All Virtual Assistants

Simple launcher that makes all VAs visible and displays them.

Tags: #LAUNCHER #VIRTUAL_ASSISTANT #STARTUP @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from va_visibility_system import VAVisibilitySystem
    from character_avatar_registry import CharacterAvatarRegistry, CharacterType
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("StartVAs")


def main():
    """Start all VAs"""
    print("=" * 80)
    print("🦾 STARTING ALL VIRTUAL ASSISTANTS")
    print("=" * 80)
    print()

    try:
        # Initialize visibility system
        visibility = VAVisibilitySystem()

        # Ensure Iron Man VAs are visible
        print("Making Iron Man VAs visible...")
        visibility.ensure_iron_man_vas_visible()
        print("✅ Iron Man VAs initialized")
        print()

        # Show all VAs
        print("Making all VAs visible...")
        dashboard = visibility.show_all_vas()
        print("✅ All VAs initialized")
        print()

        # Get status
        status = visibility.get_va_visibility_status()

        print("=" * 80)
        print("✅ ALL VIRTUAL ASSISTANTS STARTED")
        print("=" * 80)
        print()

        print("Virtual Assistants Active:")
        for va_info in status["visible_vas"]:
            if va_info["visible"]:
                print(f"  ✅ {va_info['name']} ({va_info['va_id']})")
                print(f"     Role: {va_info['role']}")
                print(f"     Widgets: {va_info['widget_count']}")
                print()

        print(f"Total: {status['total_vas']} VAs")
        print(f"Visible: {sum(1 for v in status['visible_vas'] if v['visible'])} VAs")
        print(f"Total Widgets: {len(status['widgets'])}")
        print()

        print("Note: VAs are active. To see visual display, run:")
        print("  python scripts/python/render_va_desktop_widgets.py")
        print()

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()