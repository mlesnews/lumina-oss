#!/usr/bin/env python3
"""
Fix VA Visual Blob Rendering - AGGRESSIVE ORDER 66: @DOIT

AGGRESSIVELY fixes the "blob" visual appearance of Virtual Assistants by:
1. Dramatically reducing glow layers (from 6 to 2 for outer glow)
2. Removing excessive gradient layers (from 5 to 2 for body)
3. Increasing outline widths significantly for sharp definition
4. Reducing alpha values to prevent excessive blending
5. Making features (eyes, mouth, arc reactor) much more distinct

Tags: #VAS #IMVA #ACVA #JARVIS #VISUAL #RENDERING #ORDER66 #DOIT @JARVIS @TEAM
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

logger = get_logger("FixVABlobAggressive")


class FixVABlobAggressive:
    """
    Fix VA Visual Blob Rendering - AGGRESSIVE

    Dramatically reduces blending and glow to eliminate "blob" appearance
    """

    def __init__(self, project_root: Path = None):
        """Initialize aggressive VA blob fixer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.ironman_va_file = self.project_root / "scripts" / "python" / "ironman_virtual_assistant.py"

        logger.info("✅ Fix VA Blob Aggressive initialized")

    def fix_va_blob_aggressive(self) -> Dict[str, Any]:
        """
        AGGRESSIVELY fix VA visual blob rendering issues

        ORDER 66: @DOIT execution command
        """
        logger.info("="*80)
        logger.info("🎨 ORDER 66: AGGRESSIVELY Fixing VA Visual Blob Rendering")
        logger.info("="*80)

        result = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "execution_type": "ORDER 66: @DOIT (AGGRESSIVE)",
            "fixes_applied": [],
            "success": True,
            "errors": []
        }

        if not self.ironman_va_file.exists():
            error_msg = f"File not found: {self.ironman_va_file}"
            logger.error(f"❌ {error_msg}")
            result["errors"].append(error_msg)
            result["success"] = False
            return result

        try:
            # Read the file
            logger.info(f"\n📖 Reading {self.ironman_va_file.name}...")
            with open(self.ironman_va_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # AGGRESSIVE FIX 1: Reduce outer glow layers from 6 to 2 (dramatically reduce blending)
            if 'for i in range(6, 0, -1):  # Reduced from 12 to 6 for clearer definition' in content:
                logger.info("   🔧 AGGRESSIVE Fix 1: Dramatically reducing outer glow layers (6 → 2)")
                content = content.replace(
                    'for i in range(6, 0, -1):  # Reduced from 12 to 6 for clearer definition',
                    'for i in range(2, 0, -1):  # AGGRESSIVE: Reduced to 2 to eliminate blob appearance'
                )
                result["fixes_applied"].append("AGGRESSIVE: Reduced outer glow layers: 6 → 2")

            # AGGRESSIVE FIX 2: Reduce glow alpha even more
            if 'alpha = max(0, min(200, int(60 - (i * 8))))  # Reduced for clearer definition, less blending' in content:
                logger.info("   🔧 AGGRESSIVE Fix 2: Dramatically reducing glow alpha values")
                content = content.replace(
                    'alpha = max(0, min(200, int(60 - (i * 8))))  # Reduced for clearer definition, less blending',
                    'alpha = max(0, min(100, int(40 - (i * 15))))  # AGGRESSIVE: Much lower alpha to eliminate blob'
                )
                result["fixes_applied"].append("AGGRESSIVE: Reduced glow alpha values significantly")

            # AGGRESSIVE FIX 3: Reduce body gradient layers from 5 to 2
            if 'for i in range(5):  # Reduced from 8 to 5 for clearer definition while maintaining smoothness' in content:
                logger.info("   🔧 AGGRESSIVE Fix 3: Dramatically reducing body gradient layers (5 → 2)")
                content = content.replace(
                    'for i in range(5):  # Reduced from 8 to 5 for clearer definition while maintaining smoothness',
                    'for i in range(2):  # AGGRESSIVE: Reduced to 2 to eliminate blob, sharp definition only'
                )
                result["fixes_applied"].append("AGGRESSIVE: Reduced body gradient layers: 5 → 2")

            # AGGRESSIVE FIX 4: Increase outline widths even more for sharp definition
            if 'outline=(*secondary_rgb, 255), width=max(3, int(3.5 * scale))  # Increased for clearer definition' in content:
                logger.info("   🔧 AGGRESSIVE Fix 4: Dramatically increasing outline widths")
                content = content.replace(
                    'outline=(*secondary_rgb, 255), width=max(3, int(3.5 * scale))  # Increased for clearer definition',
                    'outline=(*secondary_rgb, 255), width=max(5, int(5 * scale))  # AGGRESSIVE: Much thicker outline for sharp definition'
                )
                result["fixes_applied"].append("AGGRESSIVE: Increased main body outline width dramatically")

            # AGGRESSIVE FIX 5: Reduce arc reactor glow layers from 3 to 1
            if 'for glow_layer in range(3, 0, -1):  # Reduced from 5 to 3 for clearer definition' in content:
                logger.info("   🔧 AGGRESSIVE Fix 5: Reducing arc reactor glow layers (3 → 1)")
                content = content.replace(
                    'for glow_layer in range(3, 0, -1):  # Reduced from 5 to 3 for clearer definition',
                    'for glow_layer in range(1, 0, -1):  # AGGRESSIVE: Single glow layer only for sharp definition'
                )
                result["fixes_applied"].append("AGGRESSIVE: Reduced arc reactor glow layers: 3 → 1")

            # AGGRESSIVE FIX 6: Increase helmet outline width
            if 'draw.ellipse(helmet_bbox, fill=(*primary_rgb, 255), outline=(*secondary_rgb, 255), width=max(3, int(3 * scale))  # Increased for clearer definition' in content:
                logger.info("   🔧 AGGRESSIVE Fix 6: Increasing helmet outline width")
                content = content.replace(
                    'draw.ellipse(helmet_bbox, fill=(*primary_rgb, 255), outline=(*secondary_rgb, 255), width=max(3, int(3 * scale))  # Increased for clearer definition',
                    'draw.ellipse(helmet_bbox, fill=(*primary_rgb, 255), outline=(*secondary_rgb, 255), width=max(5, int(5 * scale))  # AGGRESSIVE: Much thicker outline'
                )
                result["fixes_applied"].append("AGGRESSIVE: Increased helmet outline width dramatically")

            # AGGRESSIVE FIX 7: Reduce glow_alpha multiplier (currently 0.25, reduce to 0.1)
            if 'glow_alpha = int(alpha * 0.25)  # Even more subtle' in content:
                logger.info("   🔧 AGGRESSIVE Fix 7: Reducing glow alpha multiplier")
                content = content.replace(
                    'glow_alpha = int(alpha * 0.25)  # Even more subtle',
                    'glow_alpha = int(alpha * 0.1)  # AGGRESSIVE: Minimal glow to eliminate blob'
                )
                result["fixes_applied"].append("AGGRESSIVE: Reduced glow alpha multiplier: 0.25 → 0.1")

            # Write the fixed file
            if content != original_content:
                logger.info(f"\n💾 Writing AGGRESSIVE fixes to {self.ironman_va_file.name}...")
                with open(self.ironman_va_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"   ✅ File updated with {len(result['fixes_applied'])} AGGRESSIVE fixes")
            else:
                logger.info("\n✅ No changes needed - checking for other patterns...")
                # Try to find any remaining patterns that might cause blob appearance
                if 'range(6' in content or 'range(5' in content or 'range(3' in content:
                    logger.warning("   ⚠️  Found potential blob-causing patterns but exact matches not found")
                    logger.warning("   ⚠️  Manual review may be needed")
                else:
                    result["fixes_applied"].append("No changes needed - file already optimized")

            logger.info("="*80)
            logger.info("✅ AGGRESSIVE VA Visual Blob Rendering Fix Complete")
            logger.info(f"   Fixes Applied: {len(result['fixes_applied'])}")
            for fix in result["fixes_applied"]:
                logger.info(f"   • {fix}")
            logger.info("="*80)

        except Exception as e:
            error_msg = f"Error aggressively fixing VA visual rendering: {e}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            result["errors"].append(error_msg)
            result["success"] = False

        return result


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix VA Visual Blob Rendering - AGGRESSIVE ORDER 66: @DOIT")
    parser.add_argument('--project-root', type=Path, help='Project root directory')

    args = parser.parse_args()

    fixer = FixVABlobAggressive(project_root=args.project_root)
    result = fixer.fix_va_blob_aggressive()

    if result["success"]:
        print(f"\n✅ Success: Applied {len(result['fixes_applied'])} AGGRESSIVE fixes")
        return 0
    else:
        print(f"\n❌ Failed: {len(result['errors'])} errors")
        for error in result["errors"]:
            print(f"   • {error}")
        return 1


if __name__ == "__main__":


    sys.exit(main())