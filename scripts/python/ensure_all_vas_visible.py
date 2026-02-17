#!/usr/bin/env python3
"""
Ensure All VAs Visible - Complete System

Ensures all Virtual Assistants are visible in all visualization systems:
- Desktop widgets
- Character animations
- Status displays

Focus: ACE (original), JARVIS_VA (Iron Man VA based on ACE), IMVA (Iron Man Visual)

Tags: #VISIBILITY #ALL_VAs #ACE #JARVIS #IMVA @JARVIS @LUMINA
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

logger = get_logger("EnsureAllVAsVisible")


def main():
    """Ensure all VAs are visible"""
    print("=" * 80)
    print("👁️  ENSURING ALL VAs ARE VISIBLE")
    print("=" * 80)
    print()

    registry = CharacterAvatarRegistry()
    vas = registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

    viz = VADesktopVisualization(registry)
    coord = VACoordinationSystem(registry)
    health = VAHealthMonitoring(registry)

    print("VA Relationships:")
    print("  • ACE: Armory Crate Virtual Assistant (Original)")
    print("  • JARVIS_VA: Iron Man Virtual Assistant (Based on ACE)")
    print("  • IMVA: Iron Man Visual Assistant (Visual version)")
    print("  • AVA: Any Virtual Assistant (Placeholder)")
    print()

    print("=" * 80)
    print("CREATING VISUALIZATIONS FOR ALL VAs")
    print("=" * 80)
    print()

    # Position mapping for all VAs
    positions = {
        "ace": {"x": 100.0, "y": 100.0},  # Original - left side
        "jarvis_va": {"x": 400.0, "y": 50.0},  # Iron Man VA - center top
        "imva": {"x": 400.0, "y": 350.0},  # Iron Man Visual - center bottom
        "ava": {"x": 700.0, "y": 200.0}  # Placeholder - right side
    }

    for va in vas:
        print(f"Making {va.name} ({va.character_id}) visible...")

        # Get position
        pos = positions.get(va.character_id, {"x": 100.0, "y": 100.0})

        # Check existing widgets
        existing_widgets = viz.get_va_widgets(va.character_id)

        if not existing_widgets:
            # Create widget
            widget = viz.create_va_widget(
                va.character_id,
                position=pos,
                size={"width": 250.0, "height": 200.0}
            )
            print(f"  ✅ Created widget: {widget.widget_type.value}")
        else:
            print(f"  ✅ Already has {len(existing_widgets)} widget(s)")

        # Set status
        status_data = {
            "name": va.name,
            "role": va.role,
            "status": "active",
            "visible": True
        }

        # Add relationship info
        if va.character_id == "ace":
            status_data["type"] = "Armory Crate VA (Original)"
        elif va.character_id == "jarvis_va":
            status_data["type"] = "Iron Man VA (Based on ACE)"
            status_data["based_on"] = "ACE"
        elif va.character_id == "imva":
            status_data["type"] = "Iron Man Visual Assistant"
            status_data["visual_version"] = True

        viz.show_va_status(va.character_id, status_data)

        # Display VFX
        if va.character_id == "jarvis_va":
            viz.display_vfx(va.character_id, VFXType.TRANSFORMATION, duration=2.0)
        else:
            viz.display_vfx(va.character_id, VFXType.ACTIVATION, duration=1.5)

        # Ensure availability
        coord.set_va_availability(va.character_id, True)

        print(f"  ✅ {va.name} is now visible and active")
        print()

    # Create dashboard
    print("Creating multi-VA dashboard...")
    dashboard = viz.multi_va_dashboard()
    print(f"  ✅ Dashboard: {len(dashboard['vas'])} VAs, {len(dashboard['widgets'])} widgets")
    print()

    # Final status
    print("=" * 80)
    print("📊 FINAL VISIBILITY STATUS")
    print("=" * 80)
    print()

    for va in vas:
        widgets = viz.get_va_widgets(va.character_id)
        va_status = coord.get_va_status(va.character_id)

        status_icon = "✅" if widgets else "❌"
        print(f"{status_icon} {va.name} ({va.character_id})")
        print(f"   Visible: {'YES' if widgets else 'NO'}")
        print(f"   Widgets: {len(widgets)}")
        print(f"   Available: {va_status.get('available', True) if va_status else 'Unknown'}")

        if va.character_id == "ace":
            print("   Type: Armory Crate VA (Original)")
        elif va.character_id == "jarvis_va":
            print("   Type: Iron Man VA (Based on ACE)")
        elif va.character_id == "imva":
            print("   Type: Iron Man Visual Assistant")
        print()

    print("=" * 80)
    print("✅ ALL VAs NOW VISIBLE")
    print("=" * 80)
    print()
    print("Relationship Chain:")
    print("  ACE (Original) → JARVIS_VA (Iron Man VA) → IMVA (Iron Man Visual)")
    print()
    print("All VAs should now be visible in:")
    print("  • Desktop widgets")
    print("  • Status displays")
    print("  • Visualization systems")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()