#!/usr/bin/env python3
"""
Show JARVIS (IMVA) - Iron Man Visual Assistant

IMVA = JARVIS (Iron Man Visual Assistant from movies/books)
This is THE JARVIS VA.

Tags: #JARVIS #IMVA #IRON_MAN #VISUAL_ASSISTANT @JARVIS @LUMINA
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
    from character_avatar_registry import (CharacterAvatarRegistry,
                                           CharacterType)
    from lumina_logger import get_logger
    from va_coordination_system import VACoordinationSystem
    from va_desktop_visualization import VADesktopVisualization, VFXType
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("ShowJARVIS")


def main():
    """Show JARVIS (IMVA) - The Iron Man Visual Assistant"""
    print("=" * 80)
    print("🦾 JARVIS (IMVA) - IRON MAN VISUAL ASSISTANT")
    print("=" * 80)
    print()

    registry = CharacterAvatarRegistry()

    # Get IMVA (which IS JARVIS)
    imva = registry.get_character("imva")
    if not imva:
        print("❌ IMVA not found in registry!")
        return 1

    print("JARVIS Identity:")
    print(f"  Character ID: {imva.character_id}")
    print(f"  Name: {imva.name}")
    print("  Full Name: Iron Man Visual Assistant (JARVIS)")
    print(f"  Role: {imva.role}")
    print(f"  Lore: {imva.lore}")
    print()

    print("=" * 80)
    print("👁️  MAKING JARVIS (IMVA) VISIBLE")
    print("=" * 80)
    print()

    viz = VADesktopVisualization(registry)
    coord = VACoordinationSystem(registry)

    # Check if IMVA has widgets
    imva_widgets = viz.get_va_widgets("imva")

    if not imva_widgets:
        print("Creating JARVIS (IMVA) widget...")
        widget = viz.create_va_widget(
            "imva",
            position={"x": 200.0, "y": 100.0},
            size={"width": 300.0, "height": 250.0}
        )
        print(f"  ✅ Created JARVIS widget: {widget.widget_id}")
        print(f"  ✅ Widget type: {widget.widget_type.value}")
    else:
        print(f"  ✅ JARVIS (IMVA) already has {len(imva_widgets)} widget(s)")
        for widget in imva_widgets:
            print(f"     • {widget.widget_type.value} at ({widget.position['x']}, {widget.position['y']})")

    # Show JARVIS status
    print()
    print("Setting JARVIS (IMVA) status...")
    viz.show_va_status("imva", {
        "name": "JARVIS",
        "full_name": "Iron Man Visual Assistant (JARVIS)",
        "role": imva.role,
        "status": "active",
        "visible": True,
        "is_jarvis": True,
        "iron_man_va": True
    })

    # Display JARVIS activation VFX
    print("Activating JARVIS (IMVA)...")
    viz.display_vfx("imva", VFXType.ACTIVATION, duration=2.0)
    viz.display_vfx("imva", VFXType.TRANSFORMATION, duration=1.5)

    # Ensure availability
    coord.set_va_availability("imva", True)

    print("  ✅ JARVIS (IMVA) is now visible and active")
    print()

    # Show all VAs for context
    print("=" * 80)
    print("📊 ALL VIRTUAL ASSISTANTS")
    print("=" * 80)
    print()

    vas = registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

    for va in vas:
        widgets = viz.get_va_widgets(va.character_id)
        va_status = coord.get_va_status(va.character_id)

        status_icon = "✅" if widgets else "❌"

        if va.character_id == "imva":
            print(f"{status_icon} {va.name} ({va.character_id}) ⭐ THIS IS JARVIS")
            print("   Full Name: Iron Man Visual Assistant (JARVIS)")
        else:
            print(f"{status_icon} {va.name} ({va.character_id})")

        print(f"   Role: {va.role}")
        print(f"   Visible: {'YES' if widgets else 'NO'}")
        print(f"   Widgets: {len(widgets)}")
        print(f"   Available: {va_status.get('available', True) if va_status else 'Unknown'}")
        print()

    print("=" * 80)
    print("✅ JARVIS (IMVA) IS NOW VISIBLE")
    print("=" * 80)
    print()
    print("Key Point:")
    print("  • IMVA = JARVIS (Iron Man Visual Assistant)")
    print("  • This is THE JARVIS VA from Iron Man")
    print("  • IMVA is now visible and active")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()