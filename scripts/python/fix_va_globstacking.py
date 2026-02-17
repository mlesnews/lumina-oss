#!/usr/bin/env python3
"""
Fix VA Globstacking - ORDER 66: @DOIT

Fixes the issue where all VAs are still stacking/clustering together.
Ensures proper spacing and prevents multiple VAs from occupying the same position.

Tags: #VAS #POSITIONING #STACKING #CLUSTERING #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixVAGlobstacking")


class VAGlobstackingFixer:
    """
    Fix VA Globstacking

    Ensures VAs are properly spaced and don't stack/cluster together
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fixer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.va_positions_file = self.data_dir / "va_positions.json"

        logger.info("✅ VA Globstacking Fixer initialized")

    def fix_globstacking(self) -> Dict[str, Any]:
        """
        Fix VA globstacking issue

        ORDER 66: @DOIT execution command
        """
        logger.info("="*80)
        logger.info("🔧 ORDER 66: Fixing VA Globstacking")
        logger.info("="*80)

        result = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "execution_type": "ORDER 66: @DOIT",
            "fixes_applied": [],
            "success": True,
            "errors": []
        }

        # Import positioning system
        try:
            from va_positioning_combat_system import VAPositioningCombatSystem
            positioning = VAPositioningCombatSystem(project_root=self.project_root)
        except Exception as e:
            error_msg = f"Could not import positioning system: {e}"
            logger.error(f"❌ {error_msg}")
            result["errors"].append(error_msg)
            result["success"] = False
            return result

        # Detect screen size
        screen_width, screen_height = positioning.detect_screen_size()
        logger.info(f"📺 Screen size: {screen_width}x{screen_height}")

        # Get current positions
        current_positions = positioning.get_positions()
        logger.info(f"📍 Current VA positions: {len(current_positions)}")

        # Calculate minimum spacing (window_size + margin)
        window_size = 120
        min_spacing = window_size + 50  # Increased spacing

        # Fix stacking by repositioning VAs
        if current_positions:
            logger.info("\n🔧 Repositioning VAs to prevent stacking...")

            # Collect all existing positions
            existing_positions: List[Tuple[int, int]] = []
            va_ids_to_reposition = []

            for va_id, pos_data in current_positions.items():
                if pos_data.get('is_active') and pos_data.get('x') and pos_data.get('y'):
                    existing_positions.append((pos_data['x'], pos_data['y']))
                    va_ids_to_reposition.append(va_id)

            # Calculate new positions with proper spacing
            new_positions = {}
            used_positions: List[Tuple[int, int]] = []

            for va_id in va_ids_to_reposition:
                # Calculate spaced position
                x, y = positioning.calculate_spaced_position(
                    va_id,
                    window_size=window_size,
                    use_random=True
                )

                # Ensure minimum spacing from all existing positions
                attempts = 0
                while attempts < 100:
                    # Check spacing from used positions
                    too_close = False
                    for (used_x, used_y) in used_positions + existing_positions:
                        distance = math.sqrt((x - used_x)**2 + (y - used_y)**2)
                        if distance < min_spacing:
                            too_close = True
                            break

                    if not too_close:
                        break

                    # Try new random position
                    x, y = positioning.calculate_spaced_position(
                        va_id,
                        window_size=window_size,
                        use_random=True
                    )
                    attempts += 1

                # Store new position
                used_positions.append((x, y))
                new_positions[va_id] = {"x": x, "y": y}

                logger.info(f"   ✅ {va_id}: ({x}, {y})")

            # Update positions in positioning system
            if new_positions:
                result["fixes_applied"].append(f"Repositioned {len(new_positions)} VAs with minimum spacing of {min_spacing}px")

                # Update positioning system
                for va_id, new_pos in new_positions.items():
                    if va_id in positioning.va_positions:
                        positioning.va_positions[va_id].x = new_pos["x"]
                        positioning.va_positions[va_id].y = new_pos["y"]

                # Save positions
                positioning._save_positions()
                logger.info(f"✅ Updated {len(new_positions)} VA positions")

        # Verify spacing
        logger.info("\n🔍 Verifying spacing...")
        final_positions = positioning.get_positions()
        spacing_issues = []

        active_positions = []
        for va_id, pos_data in final_positions.items():
            if pos_data.get('is_active') and pos_data.get('x') and pos_data.get('y'):
                active_positions.append((va_id, pos_data['x'], pos_data['y']))

        for i, (va_id1, x1, y1) in enumerate(active_positions):
            for va_id2, x2, y2 in active_positions[i+1:]:
                distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                if distance < min_spacing:
                    spacing_issues.append({
                        "va1": va_id1,
                        "va2": va_id2,
                        "distance": distance,
                        "min_required": min_spacing
                    })

        if spacing_issues:
            logger.warning(f"⚠️  Found {len(spacing_issues)} spacing issues:")
            for issue in spacing_issues:
                logger.warning(f"   • {issue['va1']} <-> {issue['va2']}: {issue['distance']:.0f}px (need {issue['min_required']}px)")
            result["fixes_applied"].append(f"Found {len(spacing_issues)} spacing issues - may need further adjustment")
        else:
            logger.info("✅ All VAs properly spaced!")
            result["fixes_applied"].append("All VAs verified with proper spacing")

        # Generate recommendations
        recommendations = []

        if len(active_positions) > 5:
            recommendations.append("Consider using a grid layout for many VAs")

        if spacing_issues:
            recommendations.append("Increase minimum spacing or reduce number of active VAs")

        result["recommendations"] = recommendations
        result["final_positions"] = {va_id: {"x": x, "y": y} for va_id, x, y in active_positions}
        result["spacing_issues"] = spacing_issues

        logger.info("="*80)
        logger.info("✅ VA Globstacking Fix Complete")
        logger.info(f"   Fixes Applied: {len(result['fixes_applied'])}")
        logger.info("="*80)

        return result


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix VA Globstacking - ORDER 66: @DOIT")
    parser.add_argument('--project-root', type=Path, help='Project root directory')

    args = parser.parse_args()

    fixer = VAGlobstackingFixer(project_root=args.project_root)
    result = fixer.fix_globstacking()

    if result["success"]:
        print(f"\n✅ Success: {len(result['fixes_applied'])} fixes applied")
        if result.get("spacing_issues"):
            print(f"\n⚠️  Spacing Issues: {len(result['spacing_issues'])}")
            for issue in result["spacing_issues"][:5]:
                print(f"   • {issue['va1']} <-> {issue['va2']}: {issue['distance']:.0f}px")
        if result.get("recommendations"):
            print(f"\n💡 Recommendations:")
            for rec in result["recommendations"]:
                print(f"   • {rec}")
        return 0
    else:
        print(f"\n❌ Failed: {len(result['errors'])} errors")
        for error in result["errors"]:
            print(f"   • {error}")
        return 1


if __name__ == "__main__":


    sys.exit(main())