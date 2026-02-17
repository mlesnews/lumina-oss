#!/usr/bin/env python3
"""
Adjust Kenny Components - Dynamic Component Adjustment

Allows adjusting Kenny's sprite components in real-time without restarting.
Uses component-based design with dynamic scaling.

Usage:
    python adjust_kenny_components.py --component helmet --position_offset 0.0,-0.45
    python adjust_kenny_components.py --component arc_reactor --position_offset 0.0,0.0

Tags: #KENNY #COMPONENTS #DYNAMIC_SCALING @JARVIS @LUMINA
"""

import sys
import argparse
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from kenny_sprite_components import KennySpriteComponents
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    print("❌ Component system not available")

def main():
    parser = argparse.ArgumentParser(description="Adjust Kenny sprite components dynamically")
    parser.add_argument("--component", required=True, choices=["body", "helmet", "hud", "face", "arc_reactor"],
                       help="Component to adjust")
    parser.add_argument("--size_scale", type=float, help="Size scale factor")
    parser.add_argument("--position_offset", type=str, help="Position offset as 'x,y' (e.g., '0.0,-0.35')")
    parser.add_argument("--color", type=str, help="Color as 'r,g,b,a' (e.g., '255,140,0,255')")
    parser.add_argument("--enabled", type=bool, help="Enable/disable component")

    args = parser.parse_args()

    if not COMPONENTS_AVAILABLE:
        print("❌ Component system not available")
        return

    # Load or create component manager
    components = KennySpriteComponents()

    # Parse position offset
    position_offset = None
    if args.position_offset:
        try:
            x, y = args.position_offset.split(',')
            position_offset = (float(x), float(y))
        except ValueError:
            print(f"❌ Invalid position_offset format: {args.position_offset}")
            return

    # Parse color
    color = None
    if args.color:
        try:
            r, g, b, a = args.color.split(',')
            color = (int(r), int(g), int(b), int(a))
        except ValueError:
            print(f"❌ Invalid color format: {args.color}")
            return

    # Adjust component
    adjustments = {}
    if args.size_scale is not None:
        adjustments["size_scale"] = args.size_scale
    if position_offset:
        adjustments["position_offset"] = position_offset
    if color:
        adjustments["color"] = color
    if args.enabled is not None:
        adjustments["enabled"] = args.enabled

    if adjustments:
        components.adjust_component(args.component, **adjustments)
        print(f"✅ Adjusted {args.component}: {adjustments}")
        print(f"   Current config: {components.get_component_config(args.component)}")
    else:
        print(f"📋 Current config for {args.component}:")
        print(f"   {components.get_component_config(args.component)}")

if __name__ == "__main__":


    main()