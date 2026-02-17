#!/usr/bin/env python3
"""
Integrate VA Positioning System with IMVA - ORDER 66: @DOIT

Updates IMVA to use the positioning system to prevent stacking/clustering
and enable proper 1v1 combat positioning.

Tags: #VAS #IMVA #POSITIONING #COMBAT #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, Any
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IntegrateVAPositioning")


def integrate_positioning_system() -> Dict[str, Any]:
    """
    Integrate positioning system with IMVA

    ORDER 66: @DOIT execution command
    """
    logger.info("="*80)
    logger.info("🔧 ORDER 66: Integrating VA Positioning System with IMVA")
    logger.info("="*80)

    result = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "execution_type": "ORDER 66: @DOIT",
        "changes_applied": [],
        "success": True,
        "errors": []
    }

    project_root = Path(__file__).parent.parent.parent
    imva_file = project_root / "scripts" / "python" / "ironman_virtual_assistant.py"

    if not imva_file.exists():
        error_msg = f"File not found: {imva_file}"
        logger.error(f"❌ {error_msg}")
        result["errors"].append(error_msg)
        result["success"] = False
        return result

    try:
        # Read the file
        logger.info(f"\n📖 Reading {imva_file.name}...")
        with open(imva_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Integration 1: Add positioning system import at the top
        import_section = "from va_positioning_combat_system import VAPositioningCombatSystem, OpponentType"
        if "from va_positioning_combat_system import" not in content:
            # Find the imports section (after docstring, before class)
            lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_idx = i
                    break

            # Insert after last import
            last_import_idx = insert_idx
            for i in range(insert_idx, len(lines)):
                if lines[i].startswith('import ') or lines[i].startswith('from '):
                    last_import_idx = i
                elif lines[i].strip() == '' or lines[i].startswith('class ') or lines[i].startswith('def '):
                    break

            lines.insert(last_import_idx + 1, import_section)
            content = '\n'.join(lines)
            result["changes_applied"].append("Added positioning system import")
            logger.info("   ✅ Added positioning system import")

        # Integration 2: Initialize positioning system in __init__
        if 'self.ac_va_position = None' in content and 'self.positioning_system = None' not in content:
            # Add positioning system initialization after ac_va_position
            positioning_init = """        # VA Positioning & Combat System (prevents stacking, enables 1v1 combat)
        try:
            self.positioning_system = VAPositioningCombatSystem(project_root=self.project_root)
            logger.info("✅ VA Positioning System initialized")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize positioning system: {e}")
            self.positioning_system = None"""

            content = content.replace(
                'self.ac_va_position = None  # AC VA window position (x, y)',
                f'self.ac_va_position = None  # AC VA window position (x, y)\n{positioning_init}'
            )
            result["changes_applied"].append("Added positioning system initialization")
            logger.info("   ✅ Added positioning system initialization")

        # Integration 3: Use positioning system for initial position
        if 'initial_x = max(50, min(int(self.x), screen_width - self.window_size))' in content:
            # Replace initial positioning with positioning system
            positioning_code = """        # Use positioning system for proper spacing (prevents stacking)
        if self.positioning_system:
            try:
                pos_x, pos_y = self.positioning_system.calculate_spaced_position("imva", self.window_size)
                initial_x = max(50, min(pos_x, screen_width - self.window_size))
                initial_y = max(50, min(pos_y, screen_height - self.window_size))
                logger.info(f"✅ Positioned using positioning system: ({initial_x}, {initial_y})")
            except Exception as e:
                logger.warning(f"⚠️  Could not use positioning system: {e}")
                initial_x = max(50, min(int(self.x), screen_width - self.window_size))
                initial_y = max(50, min(int(self.y), screen_height - self.window_size))
        else:
            initial_x = max(50, min(int(self.x), screen_width - self.window_size))
            initial_y = max(50, min(int(self.y), screen_height - self.window_size))"""

            # Find and replace the initial positioning code
            lines = content.split('\n')
            new_lines = []
            skip_next = False
            for i, line in enumerate(lines):
                if 'initial_x = max(50, min(int(self.x), screen_width - self.window_size))' in line:
                    # Replace this section
                    new_lines.append(positioning_code)
                    skip_next = True
                    continue
                elif skip_next and 'initial_y = max(50, min(int(self.y), screen_height - self.window_size))' in line:
                    skip_next = False
                    continue
                elif skip_next:
                    continue
                new_lines.append(line)

            if new_lines != lines:
                content = '\n'.join(new_lines)
                result["changes_applied"].append("Integrated positioning system for initial position")
                logger.info("   ✅ Integrated positioning system for initial position")

        # Write the updated file
        if content != original_content:
            logger.info(f"\n💾 Writing changes to {imva_file.name}...")
            with open(imva_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"   ✅ File updated with {len(result['changes_applied'])} integrations")
        else:
            logger.info("\n✅ No changes needed - positioning system already integrated")
            result["changes_applied"].append("No changes needed - already integrated")

        logger.info("="*80)
        logger.info("✅ VA Positioning System Integration Complete")
        logger.info(f"   Changes Applied: {len(result['changes_applied'])}")
        for change in result["changes_applied"]:
            logger.info(f"   • {change}")
        logger.info("="*80)

    except Exception as e:
        error_msg = f"Error integrating positioning system: {e}"
        logger.error(f"❌ {error_msg}", exc_info=True)
        result["errors"].append(error_msg)
        result["success"] = False

    return result


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Integrate VA Positioning System with IMVA - ORDER 66: @DOIT")
    parser.add_argument('--project-root', type=Path, help='Project root directory')

    args = parser.parse_args()

    result = integrate_positioning_system()

    if result["success"]:
        print(f"\n✅ Success: Applied {len(result['changes_applied'])} integrations")
        return 0
    else:
        print(f"\n❌ Failed: {len(result['errors'])} errors")
        for error in result["errors"]:
            print(f"   • {error}")
        return 1


if __name__ == "__main__":


    sys.exit(main())