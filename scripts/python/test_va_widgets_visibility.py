#!/usr/bin/env python3
"""
Test VA Widgets Visibility - Debug script to ensure all widgets are visible
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
from va_desktop_visualization import VADesktopVisualization
from render_va_desktop_widgets import render_with_tkinter

# Try Replika-inspired renderer first
try:
    from replika_inspired_va_renderer import render_replika_inspired
    USE_REPLIKA = True
except ImportError:
    USE_REPLIKA = False

print("=" * 80)
print("🔍 TESTING VA WIDGETS VISIBILITY")
print("=" * 80)
print()

# Initialize visibility system
visibility = VAVisibilitySystem()

# Show all VAs
print("Making all VAs visible...")
visibility.show_all_vas()

# Check widget positions
print()
print("=" * 80)
print("📊 WIDGET POSITIONS")
print("=" * 80)

viz = visibility.viz
for va in visibility.vas:
    widgets = viz.get_va_widgets(va.character_id)
    for widget in widgets:
        x = widget.position.get("x", 0)
        y = widget.position.get("y", 0)
        width = widget.size.get("width", 200)
        height = widget.size.get("height", 150)
        visible = widget.visible

        print(f"{va.name} ({va.character_id}):")
        print(f"  Widget ID: {widget.widget_id}")
        print(f"  Position: ({x}, {y})")
        print(f"  Size: {width}x{height}")
        print(f"  Visible: {visible}")
        print(f"  On screen: {0 <= x <= 1920 and 0 <= y <= 1080}")
        print()

# Reposition any widgets that are off-screen
print("=" * 80)
print("🔧 FIXING OFF-SCREEN WIDGETS")
print("=" * 80)

screen_width = 1920
screen_height = 1080

for va in visibility.vas:
    widgets = viz.get_va_widgets(va.character_id)
    for widget in widgets:
        x = widget.position.get("x", 0)
        y = widget.position.get("y", 0)
        width = widget.size.get("width", 200)
        height = widget.size.get("height", 150)

        # Check if widget is off-screen
        if x < 0 or x + width > screen_width or y < 0 or y + height > screen_height:
            # Find new position
            new_pos = viz.find_available_position(
                {"width": width, "height": height},
                existing_widgets=[w for w in viz.widgets.values() 
                                 if w.va_id != va.character_id]
            )
            viz.update_widget_position(widget.widget_id, new_pos)
            print(f"  ✅ Repositioned {va.name} from ({x}, {y}) to ({new_pos['x']}, {new_pos['y']})")
        else:
            print(f"  ✓ {va.name} is on screen at ({x}, {y})")

print()
print("=" * 80)
print("✅ READY TO RENDER")
print("=" * 80)
print()
print("Rendering widgets...")
print("(Close the window when done)")
print()

# Render with Replika-inspired design (preferred) or standard
try:
    if USE_REPLIKA:
        print("Using Replika-inspired renderer...")
        render_replika_inspired(visibility)
    else:
        print("Using standard renderer...")
        render_with_tkinter(visibility)
except Exception as e:
    print(f"❌ Error rendering: {e}")
    import traceback
    traceback.print_exc()
