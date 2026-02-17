#!/usr/bin/env python3
"""
Ensure JARVIS and ACE are Visible

Makes JARVIS and ACE visible on desktop if they're running but not visible.

Tags: #VA #VISIBILITY #JARVIS #ACE @JARVIS @ACE @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from va_visibility_system import VAVisibilitySystem
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("EnsureJARVISACEVisible")


def ensure_jarvis_ace_visible():
    """Ensure JARVIS and ACE are visible"""
    print("=" * 80)
    print("👁️  ENSURING JARVIS AND ACE ARE VISIBLE")
    print("=" * 80)
    print()

    # Initialize visibility system
    visibility = VAVisibilitySystem(project_root)

    # Find JARVIS and ACE
    jarvis_va = None
    ace_va = None

    for va in visibility.vas:
        va_id_lower = va.character_id.lower()
        va_name_lower = va.name.lower()

        if "jarvis" in va_id_lower or "jarvis" in va_name_lower:
            jarvis_va = va
            print(f"✅ Found JARVIS: {va.name} ({va.character_id})")

        if "ace" in va_id_lower or "ace" in va_name_lower or "ironman" in va_id_lower:
            ace_va = va
            print(f"✅ Found ACE: {va.name} ({va.character_id})")

    print()

    # Show all VAs (this will make JARVIS and ACE visible)
    print("📺 Showing all VAs (including JARVIS and ACE)...")
    print()

    visibility.show_all_vas()

    print()
    print("=" * 80)
    print("✅ JARVIS and ACE visibility ensured")
    print("=" * 80)
    print()

    if jarvis_va:
        widgets = visibility.viz.get_va_widgets(jarvis_va.character_id)
        print(f"JARVIS widgets: {len(widgets)}")
        for widget in widgets:
            print(f"   - {widget.widget_id} at ({widget.position.get('x', 0)}, {widget.position.get('y', 0)})")

    if ace_va:
        widgets = visibility.viz.get_va_widgets(ace_va.character_id)
        print(f"ACE widgets: {len(widgets)}")
        for widget in widgets:
            print(f"   - {widget.widget_id} at ({widget.position.get('x', 0)}, {widget.position.get('y', 0)})")

    print()


if __name__ == "__main__":
    ensure_jarvis_ace_visible()
