#!/usr/bin/env python3
"""
VA Status Display

Shows comprehensive status of all VAs including visibility, activity, and presence.

Tags: #STATUS #DISPLAY #VISIBILITY @JARVIS @LUMINA
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
    from va_analytics import VAAnalytics
    from va_coordination_system import VACoordinationSystem
    from va_desktop_visualization import VADesktopVisualization
    from va_health_monitoring import VAHealthMonitoring
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("VAStatusDisplay")


def main():
    """Display comprehensive VA status"""
    print("=" * 80)
    print("📊 VIRTUAL ASSISTANT STATUS DISPLAY")
    print("=" * 80)
    print()

    registry = CharacterAvatarRegistry()
    vas = registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

    coord = VACoordinationSystem(registry)
    health = VAHealthMonitoring(registry)
    viz = VADesktopVisualization(registry)
    analytics = VAAnalytics(registry)

    print(f"Total Virtual Assistants: {len(vas)}")
    print()

    # Ensure all VAs have widgets
    print("Ensuring all VAs are visible...")
    for va in vas:
        widgets = viz.get_va_widgets(va.character_id)
        if not widgets:
            widget = viz.create_va_widget(va.character_id)
            print(f"  ✅ Created widget for {va.name}")
        else:
            print(f"  ✅ {va.name} already has {len(widgets)} widget(s)")
    print()

    # Display status for each VA
    print("=" * 80)
    print("VA STATUS DETAILS")
    print("=" * 80)
    print()

    for va in vas:
        print(f"🤖 {va.name} ({va.character_id})")
        print(f"   Role: {va.role}")
        print(f"   Hierarchy: {va.hierarchy_level}")
        print(f"   Type: {va.character_type.value}")

        # Coordination status
        va_status = coord.get_va_status(va.character_id)
        if va_status:
            print(f"   Tasks: {va_status.get('current_tasks', 0)}")
            print(f"   Messages: {va_status.get('pending_messages', 0)}")
            print(f"   Available: {va_status.get('available', True)}")

        # Health status
        health_metrics = health.health_metrics.get(va.character_id)
        if health_metrics:
            print(f"   Health: {health_metrics.status.value}")
            print(f"   Response Time: {health_metrics.response_time:.2f}s")
            print(f"   Completion Rate: {health_metrics.task_completion_rate:.1%}")

        # Visibility status
        widgets = viz.get_va_widgets(va.character_id)
        print(f"   Visible: {'✅ YES' if widgets else '❌ NO'}")
        print(f"   Widgets: {len(widgets)}")
        if widgets:
            for widget in widgets:
                print(f"     • {widget.widget_type.value} at ({widget.position['x']}, {widget.position['y']})")

        # Analytics
        stats = analytics.get_va_activation_stats(va.character_id) if hasattr(analytics, 'get_va_activation_stats') else {}
        if stats:
            print(f"   Activations: {stats.get('total_activations', 0)}")

        # Special note for Iron Man VAs
        if va.character_id in ["jarvis_va", "imva"]:
            print("   🦾 IRON MAN VA")
            if va.character_id == "jarvis_va":
                print("   🎯 Iron Man HUD Active")
            elif va.character_id == "imva":
                print("   🎯 Bobblehead Widget Active")

        print()

    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print()

    visible_count = sum(1 for va in vas if viz.get_va_widgets(va.character_id))
    active_count = sum(1 for va in vas if coord.get_va_status(va.character_id) and coord.get_va_status(va.character_id).get('available', True))

    print(f"Total VAs: {len(vas)}")
    print(f"Visible VAs: {visible_count}/{len(vas)}")
    print(f"Active VAs: {active_count}/{len(vas)}")
    print()

    print("Iron Man VAs:")
    iron_man_vas = [va for va in vas if va.character_id in ["jarvis_va", "imva"]]
    for va in iron_man_vas:
        widgets = viz.get_va_widgets(va.character_id)
        status = "✅ VISIBLE" if widgets else "❌ NOT VISIBLE"
        print(f"  {status} {va.name} ({va.character_id})")
    print()

    print("=" * 80)
    print("✅ STATUS DISPLAY COMPLETE")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()