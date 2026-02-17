#!/usr/bin/env python3
"""
VA Visibility System

Ensures all Virtual Assistants are visible and displayed properly.
Creates visual representations for all VAs including JARVIS_VA and IMVA.

Tags: #VISIBILITY #DISPLAY #VIRTUAL_ASSISTANT #IRON_MAN @JARVIS @LUMINA
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

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
    from va_desktop_visualization import (VADesktopVisualization, VFXType)
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Replika renderer import removed to avoid circular import
# If needed, import it lazily where it's used
REPLIKA_RENDERER_AVAILABLE = False
render_replika_inspired = None

# Try to import VA health monitoring
try:
    from va_health_monitoring import VAHealthMonitoring
except ImportError:
    VAHealthMonitoring = None

# Try to import DEFCON monitoring
try:
    from defcon_monitoring_system import DEFCONMonitoringSystem
except ImportError:
    DEFCONMonitoringSystem = None

logger = get_logger("VAVisibility")


class VAVisibilitySystem:
    """VA Visibility System - Ensures all VAs are visible"""

    def __init__(self, project_root_path: Optional[Path] = None):
        """Initialize visibility system"""
        if project_root_path is None:
            project_root_path = Path(__file__).parent.parent.parent

        self.project_root = project_root_path
        self.registry = CharacterAvatarRegistry()

        # Get VAs and also include characters that should be displayed (like Kenny)
        vas_list = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Also include MINOR_CHARACTER types that have avatars (like Kenny)
        minor_chars = self.registry.get_characters_by_type(CharacterType.MINOR_CHARACTER)
        for char in minor_chars:
            # Include if it has an avatar template (like Kenny with kenny_bobblehead)
            if hasattr(char, 'avatar_template') and char.avatar_template:
                if char.character_id == "kenny" or 'bobblehead' in char.avatar_template.lower():
                    vas_list.append(char)

        self.vas = vas_list
        self.viz = VADesktopVisualization(self.registry)
        self.coord = VACoordinationSystem(self.registry)
        self.health = VAHealthMonitoring(self.registry) if VAHealthMonitoring else None
        self.defcon = DEFCONMonitoringSystem() if DEFCONMonitoringSystem else None

        logger.info("=" * 80)
        logger.info("👁️  VA VISIBILITY SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   Found {len(self.vas)} VAs/characters to display")
        logger.info("   Includes: VIRTUAL_ASSISTANT + MINOR_CHARACTER (with avatars)")

    def show_all_vas(self):
        """Show all VAs with proper visualization"""
        print("=" * 80)
        print("👁️  MAKING ALL VAs VISIBLE")
        print("=" * 80)
        print()

        print(f"Total VAs: {len(self.vas)}")
        print()

        # Create widgets for all VAs
        for i, va in enumerate(self.vas):
            print(f"Making {va.name} ({va.character_id}) visible...")

            # Check if widget already exists
            existing_widgets = self.viz.get_va_widgets(va.character_id)

            if existing_widgets:
                # Use existing widget
                widget = existing_widgets[0]
                print(f"  ℹ️  Using existing widget: {widget.widget_id}")

                # Refresh widget properties from character registry (in case character was updated)
                if hasattr(va, 'is_training_dummy') and va.is_training_dummy:
                    widget.properties["is_training_dummy"] = True
                    widget.properties["immortal"] = va.immortal if hasattr(va, 'immortal') else True
                    widget.properties["training_partners"] = va.training_partners if hasattr(va, 'training_partners') else []
                    widget.properties["training_status"] = "Ready for training"
                    if va.character_id == "ace":
                        widget.properties["training_mode"] = "Immortal Demigod - Training Dummy"
                        widget.properties["regeneration"] = "Instant"

                # Check if widget position overlaps with other widgets
                x = widget.position.get("x", 100.0 + (i * 250))
                y = widget.position.get("y", 100.0)
                width = widget.size.get("width", 200.0)
                height = widget.size.get("height", 150.0)

                # Check for overlaps with other VAs' widgets
                overlap = False
                for other_va in self.vas:
                    if other_va.character_id == va.character_id:
                        continue
                    other_widgets = self.viz.get_va_widgets(other_va.character_id)
                    for other_widget in other_widgets:
                        ox = other_widget.position.get("x", 0)
                        oy = other_widget.position.get("y", 0)
                        ow = other_widget.size.get("width", 200)
                        oh = other_widget.size.get("height", 150)

                        if not (x + width < ox or x > ox + ow or
                               y + height < oy or y > oy + oh):
                            overlap = True
                            break
                    if overlap:
                        break

                # If overlap, find new position
                if overlap:
                    new_pos = self.viz.find_available_position(
                        {"width": width, "height": height},
                        existing_widgets=[w for w in self.viz.widgets.values() 
                                         if w.va_id != va.character_id]
                    )
                    self.viz.update_widget_position(widget.widget_id, new_pos)
                    print(f"  📍 Repositioned widget to avoid overlap: ({new_pos['x']}, {new_pos['y']})")
            else:
                # Create new widget with smaller, organized sizes
                # Organize widgets in a compact grid
                cols = 4
                row = i // cols
                col = i % cols
                widget = self.viz.create_va_widget(
                    va.character_id,
                    position={"x": 20.0 + (col * 140), "y": 20.0 + (row * 110)},
                    size=None  # Let widget type determine size
                )

            # Ensure widget is visible
            widget.visible = True

            # Show status
            va_status = self.coord.get_va_status(va.character_id)
            health_metrics = self.health.health_metrics.get(va.character_id) if va.character_id in self.health.health_metrics else None

            status_data = {
                "name": va.name,
                "role": va.role,
                "hierarchy": va.hierarchy_level,
                "visible": True,
                "widget_type": widget.widget_type.value,
                "widget_id": widget.widget_id,
                "status": "active"
            }

            if va_status:
                status_data["tasks"] = va_status.get("current_tasks", 0)
                status_data["messages"] = va_status.get("pending_messages", 0)

            if health_metrics:
                status_data["health"] = health_metrics.status.value

            # Add training dummy status for ACE
            if hasattr(va, 'is_training_dummy') and va.is_training_dummy:
                status_data["is_training_dummy"] = True
                status_data["immortal"] = va.immortal if hasattr(va, 'immortal') else True
                status_data["training_partners"] = va.training_partners if hasattr(va, 'training_partners') else []
                if va.character_id == "ace":
                    status_data["training_mode"] = "Immortal Demigod - Training Dummy"
                    status_data["regeneration"] = "Instant"
                    status_data["status"] = "Ready for IMVA training"

            self.viz.show_va_status(va.character_id, status_data)

            # Display activation VFX
            self.viz.display_vfx(va.character_id, VFXType.ACTIVATION, duration=1.0)

            print(f"  ✅ {va.name} visible:")
            print(f"     Widget: {widget.widget_type.value} ({widget.widget_id})")
            print(f"     Position: ({widget.position['x']}, {widget.position['y']})")
            print(f"     Status: {status_data.get('status', 'active')}")
            if 'tasks' in status_data:
                print(f"     Tasks: {status_data['tasks']}")
            if 'health' in status_data:
                print(f"     Health: {status_data['health']}")
            # Display training dummy status for ACE
            if status_data.get('is_training_dummy'):
                print(f"     🎯 Training Dummy: Active")
                print(f"     ⚡ Immortal: {status_data.get('immortal', True)}")
                if status_data.get('training_partners'):
                    partners = ', '.join(status_data['training_partners'])
                    print(f"     🤝 Training Partners: {partners}")
                if status_data.get('training_mode'):
                    print(f"     🛡️  Mode: {status_data['training_mode']}")
            print()

        # Create multi-VA dashboard
        print("Creating multi-VA dashboard...")
        dashboard = self.viz.multi_va_dashboard()
        print(f"  ✅ Dashboard created with {len(dashboard['vas'])} VAs")
        print(f"  ✅ Total widgets: {len(dashboard['widgets'])}")
        print()

        # Create and update DEFCON streetlight widget
        if self.defcon:
            print("Initializing DEFCON streetlight widget...")
            defcon_status = self.defcon.get_current_status()
            self.viz.update_defcon_level(
                defcon_status["defcon_level"],
                alerts=defcon_status["alerts"],
                problems=defcon_status["problems"]
            )
            print(f"  ✅ DEFCON Level: {defcon_status['defcon_level']} ({defcon_status['defcon_name']})")
            print(f"  ✅ Total Issues: {defcon_status['total_issues']}")
            print()

        return dashboard

    def get_va_visibility_status(self):
        """Get visibility status of all VAs"""
        print("=" * 80)
        print("📊 VA VISIBILITY STATUS")
        print("=" * 80)
        print()

        visibility_report = {
            "total_vas": len(self.vas),
            "visible_vas": [],
            "widgets": [],
            "timestamp": datetime.now().isoformat()
        }

        for va in self.vas:
            # Get widgets for this VA
            widgets = self.viz.get_va_widgets(va.character_id)

            va_info = {
                "va_id": va.character_id,
                "name": va.name,
                "role": va.role,
                "visible": len(widgets) > 0,
                "widget_count": len(widgets),
                "widgets": [w.widget_id for w in widgets]
            }

            visibility_report["visible_vas"].append(va_info)
            visibility_report["widgets"].extend([w.widget_id for w in widgets])

            status_icon = "✅" if va_info["visible"] else "❌"
            print(f"{status_icon} {va.name} ({va.character_id})")
            print(f"   Role: {va.role}")
            print(f"   Visible: {va_info['visible']}")
            print(f"   Widgets: {va_info['widget_count']}")
            if widgets:
                for widget in widgets:
                    print(f"     • {widget.widget_type.value} at ({widget.position['x']}, {widget.position['y']})")
            print()

        return visibility_report

    def ensure_iron_man_vas_visible(self):
        """Specifically ensure Iron Man VAs (JARVIS_VA, IMVA) are visible"""
        print("=" * 80)
        print("🦾 ENSURING IRON MAN VAs ARE VISIBLE")
        print("=" * 80)
        print()

        iron_man_vas = [va for va in self.vas if va.character_id in ["jarvis_va", "imva"]]

        if not iron_man_vas:
            print("❌ No Iron Man VAs found!")
            return

        for va in iron_man_vas:
            print(f"Ensuring {va.name} ({va.character_id}) is visible...")

            # Check if already has widgets
            existing_widgets = self.viz.get_va_widgets(va.character_id)

            if not existing_widgets:
                # Create widget
                if va.character_id == "jarvis_va":
                    widget = self.viz.create_va_widget(
                        va.character_id,
                        position={"x": 50.0, "y": 50.0},  # Top-left for JARVIS HUD
                        size={"width": 300.0, "height": 200.0}
                    )
                    print(f"  ✅ Created JARVIS HUD widget: {widget.widget_id}")
                elif va.character_id == "imva":
                    widget = self.viz.create_va_widget(
                        va.character_id,
                        position={"x": 50.0, "y": 300.0},  # Below JARVIS for IMVA bobblehead
                        size={"width": 150.0, "height": 150.0}
                    )
                    print(f"  ✅ Created IMVA bobblehead widget: {widget.widget_id}")
            else:
                print(f"  ✅ Already has {len(existing_widgets)} widget(s)")

            # Show status
            self.viz.show_va_status(va.character_id, {
                "name": va.name,
                "role": va.role,
                "status": "active",
                "visible": True,
                "iron_man_va": True
            })

            # Display activation VFX
            self.viz.display_vfx(va.character_id, VFXType.ACTIVATION, duration=2.0)

            print(f"  ✅ {va.name} is now visible")
            print()

        print("✅ All Iron Man VAs are now visible")
        print()


def main():
    """Main visibility function"""
    visibility = VAVisibilitySystem()

    # Ensure Iron Man VAs are visible
    visibility.ensure_iron_man_vas_visible()

    # Show all VAs
    dashboard = visibility.show_all_vas()

    # Get visibility status
    status = visibility.get_va_visibility_status()

    print("=" * 80)
    print("✅ VISIBILITY SYSTEM COMPLETE")
    print("=" * 80)
    print()
    print(f"Total VAs: {status['total_vas']}")
    print(f"Visible VAs: {sum(1 for v in status['visible_vas'] if v['visible'])}")
    print(f"Total Widgets: {len(status['widgets'])}")
    print()

    # List all visible VAs
    print("Visible VAs:")
    for va_info in status["visible_vas"]:
        if va_info["visible"]:
            print(f"  ✅ {va_info['name']} ({va_info['va_id']}) - {va_info['widget_count']} widget(s)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()