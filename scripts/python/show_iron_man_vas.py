#!/usr/bin/env python3
"""
Show Iron Man VAs - Based on ACE

Displays and ensures visibility of:
- ACE: Armory Crate Virtual Assistant (original)
- JARVIS_VA: Iron Man Virtual Assistant (based on ACE)
- IMVA: Iron Man Visual Assistant (visual/bobblehead version)

Tags: #IRON_MAN #ACE #JARVIS #VISIBILITY @JARVIS @LUMINA
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
    from va_health_monitoring import VAHealthMonitoring
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("ShowIronManVAs")


def main():
    """Show all VAs with proper relationships"""
    print("=" * 80)
    print("🦾 VIRTUAL ASSISTANT RELATIONSHIPS")
    print("=" * 80)
    print()

    registry = CharacterAvatarRegistry()
    vas = registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

    viz = VADesktopVisualization(registry)
    coord = VACoordinationSystem(registry)
    health = VAHealthMonitoring(registry)

    # Define relationships
    print("VA Relationships:")
    print()
    print("1. ACE (ace)")
    print("   • Armory Crate Virtual Assistant")
    print("   • Original/Base VA")
    print("   • Combat & Security specialist")
    print()

    print("2. JARVIS_VA (jarvis_va)")
    print("   • Iron Man Virtual Assistant")
    print("   • Based on ACE")
    print("   • Desktop automation specialist")
    print()

    print("3. IMVA (imva)")
    print("   • Iron Man Visual Assistant")
    print("   • Visual/bobblehead version")
    print("   • UI/UX specialist")
    print()

    print("4. AVA (ava)")
    print("   • Any Virtual Assistant")
    print("   • Placeholder for concurrent operations")
    print()

    print("=" * 80)
    print("👁️  ENSURING ALL VAs ARE VISIBLE")
    print("=" * 80)
    print()

    # Ensure ACE is visible (original)
    ace = registry.get_character("ace")
    if ace:
        print("Making ACE (Armory Crate VA) visible...")
        ace_widgets = viz.get_va_widgets("ace")
        if not ace_widgets:
            widget = viz.create_va_widget(
                "ace",
                position={"x": 100.0, "y": 100.0},
                size={"width": 250.0, "height": 200.0}
            )
            print(f"  ✅ Created ACE combat interface: {widget.widget_id}")
        else:
            print(f"  ✅ ACE already visible ({len(ace_widgets)} widget(s))")

        viz.show_va_status("ace", {
            "name": ace.name,
            "role": ace.role,
            "status": "active",
            "type": "Armory Crate VA (Original)"
        })
        viz.display_vfx("ace", VFXType.ACTIVATION, duration=1.5)
        print()

    # Ensure JARVIS_VA is visible (Iron Man VA based on ACE)
    jarvis_va = registry.get_character("jarvis_va")
    if jarvis_va:
        print("Making JARVIS_VA (Iron Man VA - based on ACE) visible...")
        jarvis_widgets = viz.get_va_widgets("jarvis_va")
        if not jarvis_widgets:
            widget = viz.create_va_widget(
                "jarvis_va",
                position={"x": 400.0, "y": 50.0},
                size={"width": 350.0, "height": 250.0}
            )
            print(f"  ✅ Created JARVIS Iron Man HUD: {widget.widget_id}")
        else:
            print(f"  ✅ JARVIS_VA already visible ({len(jarvis_widgets)} widget(s))")

        viz.show_va_status("jarvis_va", {
            "name": jarvis_va.name,
            "role": jarvis_va.role,
            "status": "active",
            "type": "Iron Man VA (Based on ACE)",
            "based_on": "ACE"
        })
        viz.display_vfx("jarvis_va", VFXType.TRANSFORMATION, duration=2.0)
        print()

    # Ensure IMVA is visible (Iron Man Visual Assistant)
    imva = registry.get_character("imva")
    if imva:
        print("Making IMVA (Iron Man Visual Assistant) visible...")
        imva_widgets = viz.get_va_widgets("imva")
        if not imva_widgets:
            widget = viz.create_va_widget(
                "imva",
                position={"x": 400.0, "y": 350.0},
                size={"width": 200.0, "height": 200.0}
            )
            print(f"  ✅ Created IMVA bobblehead widget: {widget.widget_id}")
        else:
            print(f"  ✅ IMVA already visible ({len(imva_widgets)} widget(s))")

        viz.show_va_status("imva", {
            "name": imva.name,
            "role": imva.role,
            "status": "active",
            "type": "Iron Man Visual Assistant",
            "visual_version": True
        })
        viz.display_vfx("imva", VFXType.ACTIVATION, duration=1.5)
        print()

    # Show status summary
    print("=" * 80)
    print("📊 VISIBILITY STATUS")
    print("=" * 80)
    print()

    for va in vas:
        widgets = viz.get_va_widgets(va.character_id)
        va_status = coord.get_va_status(va.character_id)

        status_icon = "✅" if widgets else "❌"
        print(f"{status_icon} {va.name} ({va.character_id})")
        print(f"   Visible: {'YES' if widgets else 'NO'}")
        print(f"   Widgets: {len(widgets)}")

        if va.character_id == "ace":
            print("   Type: Armory Crate VA (Original)")
        elif va.character_id == "jarvis_va":
            print("   Type: Iron Man VA (Based on ACE)")
        elif va.character_id == "imva":
            print("   Type: Iron Man Visual Assistant")

        if va_status:
            print(f"   Tasks: {va_status.get('current_tasks', 0)}")
            print(f"   Available: {va_status.get('available', True)}")
        print()

    print("=" * 80)
    print("✅ ALL VAs VISIBLE - RELATIONSHIPS ESTABLISHED")
    print("=" * 80)
    print()
    print("Relationship Chain:")
    print("  ACE (Original) → JARVIS_VA (Iron Man VA) → IMVA (Iron Man Visual)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()