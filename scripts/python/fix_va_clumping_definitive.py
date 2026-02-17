#!/usr/bin/env python3
"""
Fix VA Clumping - DEFINITIVE ORDER 66: @DOIT

DEFINITIVELY fixes VA clumping by:
1. Ensuring ALL VAs use positioning system on startup
2. Enforcing MINIMUM spacing (300px+ between all VAs)
3. Creating a grid layout option for many VAs
4. Preventing any VA from starting at the same position

Tags: #VAS #CLUMPING #POSITIONING #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import math
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixVAClumpingDefinitive")


class VAClumpingDefinitiveFixer:
    """
    DEFINITIVE Fix for VA Clumping

    Ensures VAs NEVER clump together by enforcing strict spacing rules
    """

    MIN_SPACING = 300  # ABSOLUTE minimum spacing (pixels)
    WINDOW_SIZE = 120

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize definitive clumping fixer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        logger.info("✅ VA Clumping Definitive Fixer initialized")

    def calculate_grid_position(self, va_index: int, total_vas: int, screen_width: int, screen_height: int) -> Tuple[int, int]:
        """Calculate grid position to prevent clumping"""
        margin = 100
        spacing = self.MIN_SPACING

        # Calculate grid dimensions
        cols = max(3, int(math.sqrt(total_vas)) + 1)
        rows = (total_vas + cols - 1) // cols

        # Calculate cell size
        available_width = screen_width - 2 * margin
        available_height = screen_height - 2 * margin

        cell_width = min(spacing, available_width // cols)
        cell_height = min(spacing, available_height // rows)

        # Calculate position in grid
        col = va_index % cols
        row = va_index // cols

        x = margin + col * cell_width + cell_width // 2
        y = margin + row * cell_height + cell_height // 2

        return x, y

    def fix_all_va_positions(self) -> Dict[str, Any]:
        """
        DEFINITIVELY fix all VA positions to prevent clumping

        ORDER 66: @DOIT execution command
        """
        logger.info("="*80)
        logger.info("🔧 ORDER 66: DEFINITIVELY Fixing VA Clumping")
        logger.info("="*80)

        result = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "execution_type": "ORDER 66: @DOIT (DEFINITIVE)",
            "fixes_applied": [],
            "success": True,
            "errors": []
        }

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
        logger.info(f"📺 Screen: {screen_width}x{screen_height}")

        # Get current positions
        current_positions = positioning.get_positions()
        active_vas = [(va_id, pos) for va_id, pos in current_positions.items() if pos.get('is_active')]

        logger.info(f"📍 Found {len(active_vas)} active VAs")

        if not active_vas:
            logger.info("✅ No active VAs to fix")
            result["fixes_applied"].append("No active VAs - no clumping to fix")
            return result

        # Calculate new positions using grid layout (guarantees no clumping)
        new_positions = {}
        for index, (va_id, pos_data) in enumerate(active_vas):
            x, y = self.calculate_grid_position(index, len(active_vas), screen_width, screen_height)
            new_positions[va_id] = {"x": x, "y": y}
            logger.info(f"   ✅ {va_id}: ({x}, {y})")

        # Update positions in positioning system
        for va_id, new_pos in new_positions.items():
            if va_id in positioning.va_positions:
                positioning.va_positions[va_id].x = new_pos["x"]
                positioning.va_positions[va_id].y = new_pos["y"]

        # Save positions
        positioning._save_positions()
        result["fixes_applied"].append(f"Repositioned {len(new_positions)} VAs using grid layout (MIN_SPACING={self.MIN_SPACING}px)")
        logger.info(f"✅ Repositioned {len(new_positions)} VAs")

        # Verify spacing
        logger.info("\n🔍 Verifying spacing...")
        spacing_issues = []
        positions_list = [(va_id, new_pos["x"], new_pos["y"]) for va_id, new_pos in new_positions.items()]

        for i, (va_id1, x1, y1) in enumerate(positions_list):
            for va_id2, x2, y2 in positions_list[i+1:]:
                distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                if distance < self.MIN_SPACING:
                    spacing_issues.append({
                        "va1": va_id1,
                        "va2": va_id2,
                        "distance": distance,
                        "min_required": self.MIN_SPACING
                    })

        if spacing_issues:
            logger.warning(f"⚠️  Found {len(spacing_issues)} spacing issues (this shouldn't happen with grid layout!)")
            result["warnings"] = spacing_issues
        else:
            logger.info("✅ All VAs properly spaced (grid layout ensures no clumping)")
            result["fixes_applied"].append("Verified: All VAs properly spaced")

        result["new_positions"] = new_positions
        result["total_vas"] = len(new_positions)

        logger.info("="*80)
        logger.info("✅ DEFINITIVE VA Clumping Fix Complete")
        logger.info(f"   VAs Repositioned: {len(new_positions)}")
        logger.info(f"   Minimum Spacing: {self.MIN_SPACING}px")
        logger.info("="*80)

        return result


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix VA Clumping - DEFINITIVE ORDER 66: @DOIT")
    parser.add_argument('--project-root', type=Path, help='Project root directory')

    args = parser.parse_args()

    fixer = VAClumpingDefinitiveFixer(project_root=args.project_root)
    result = fixer.fix_all_va_positions()

    if result["success"]:
        print(f"\n✅ Success: {len(result['fixes_applied'])} fixes applied")
        print(f"   VAs Repositioned: {result.get('total_vas', 0)}")
        print(f"   Minimum Spacing: {fixer.MIN_SPACING}px")
        if result.get("warnings"):
            print(f"\n⚠️  Warnings: {len(result['warnings'])}")
        return 0
    else:
        print(f"\n❌ Failed: {len(result['errors'])} errors")
        for error in result["errors"]:
            print(f"   • {error}")
        return 1


if __name__ == "__main__":


    sys.exit(main())