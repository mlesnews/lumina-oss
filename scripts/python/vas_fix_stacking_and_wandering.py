#!/usr/bin/env python3
"""
Fix VA Stacking and Enable Wandering

Fixes the issue where multiple VAs (Mark I-VII) stack on top of each other.
Ensures proper spacing and enables wandering behavior across the desktop battle map.

Tags: #VAS #STACKING #WANDERING #BATTLEMAP #FANTASYGROUNDS @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VAsFixStacking")


class VAsFixStackingAndWandering:
    """
    Fix VA stacking and enable proper wandering
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fixer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.va_positions_file = self.data_dir / "va_positions.json"

        logger.info("✅ VAs Fix Stacking and Wandering initialized")

    def fix_imva_initialization(self) -> Dict[str, Any]:
        """
        Fix IMVA initialization to use positioning system BEFORE setting x/y

        This ensures each VA instance gets a unique, properly spaced position.
        """
        logger.info("="*80)
        logger.info("🔧 Fixing IMVA Initialization for Proper Spacing")
        logger.info("="*80)

        result = {
            "success": True,
            "changes": [],
            "errors": []
        }

        try:
            # Read IMVA file
            imva_file = self.project_root / "scripts" / "python" / "ironman_virtual_assistant.py"

            if not imva_file.exists():
                result["success"] = False
                result["errors"].append(f"IMVA file not found: {imva_file}")
                return result

            content = imva_file.read_text(encoding='utf-8')
            original_content = content

            # Fix 1: Update initial x/y to use positioning system
            # Find the section where self.x and self.y are initialized
            # Line ~360: self.x = 400
            # Line ~361: self.y = 300

            # Replace hardcoded initialization with positioning system call
            old_init = """        self.x = 400
        self.y = 300"""

            new_init = """        # Initialize position using positioning system to prevent stacking
        # This ensures each VA instance gets a unique, properly spaced position
        if self.positioning_system:
            try:
                pos_x, pos_y = self.positioning_system.calculate_spaced_position("imva", 120)
                self.x = pos_x
                self.y = pos_y
                logger.info(f"✅ Initialized position using positioning system: ({self.x}, {self.y})")
            except Exception as e:
                logger.warning(f"⚠️  Could not use positioning system for initial position: {e}")
                # Fallback: Use screen center with random offset to prevent stacking
                import random
                screen_width = 1920  # Will be updated when window is created
                screen_height = 1080
                self.x = screen_width // 2 + random.randint(-200, 200)
                self.y = screen_height // 2 + random.randint(-200, 200)
        else:
            # No positioning system - use random position to prevent stacking
            import random
            screen_width = 1920
            screen_height = 1080
            self.x = screen_width // 2 + random.randint(-200, 200)
            self.y = screen_height // 2 + random.randint(-200, 200)"""

            if old_init in content:
                content = content.replace(old_init, new_init)
                result["changes"].append("Updated initial x/y to use positioning system")
                logger.info("   ✅ Fixed initial position initialization")
            else:
                # Try alternative pattern
                old_init_alt = "self.x = 400"
                if old_init_alt in content:
                    # More targeted replacement
                    lines = content.split('\n')
                    new_lines = []
                    i = 0
                    while i < len(lines):
                        if 'self.x = 400' in lines[i]:
                            # Replace this section
                            new_lines.append("        # Initialize position using positioning system to prevent stacking")
                            new_lines.append("        if self.positioning_system:")
                            new_lines.append("            try:")
                            new_lines.append("                pos_x, pos_y = self.positioning_system.calculate_spaced_position(\"imva\", 120)")
                            new_lines.append("                self.x = pos_x")
                            new_lines.append("                self.y = pos_y")
                            new_lines.append("                logger.info(f\"✅ Initialized position using positioning system: ({self.x}, {self.y})\")")
                            new_lines.append("            except Exception as e:")
                            new_lines.append("                logger.warning(f\"⚠️  Could not use positioning system for initial position: {e}\")")
                            new_lines.append("                import random")
                            new_lines.append("                screen_width = 1920")
                            new_lines.append("                screen_height = 1080")
                            new_lines.append("                self.x = screen_width // 2 + random.randint(-200, 200)")
                            new_lines.append("                self.y = screen_height // 2 + random.randint(-200, 200)")
                            new_lines.append("        else:")
                            new_lines.append("            import random")
                            new_lines.append("            screen_width = 1920")
                            new_lines.append("            screen_height = 1080")
                            new_lines.append("            self.x = screen_width // 2 + random.randint(-200, 200)")
                            new_lines.append("            self.y = screen_height // 2 + random.randint(-200, 200)")
                            # Skip the next line if it's self.y = 300
                            i += 1
                            if i < len(lines) and 'self.y = 300' in lines[i]:
                                i += 1
                            continue
                        new_lines.append(lines[i])
                        i += 1
                    content = '\n'.join(new_lines)
                    result["changes"].append("Updated initial x/y to use positioning system (alternative pattern)")
                    logger.info("   ✅ Fixed initial position initialization (alternative)")

            # Fix 2: Ensure wandering uses collision avoidance
            # The wander loop should check for other VAs and avoid them

            # Fix 3: Update window creation to use positioning system position
            # This is already done in lines 702-714, but we should verify it's correct

            # Save changes
            if content != original_content:
                imva_file.write_text(content, encoding='utf-8')
                result["changes"].append("Saved changes to ironman_virtual_assistant.py")
                logger.info("   ✅ Saved changes to IMVA file")
            else:
                logger.info("   ℹ️  No changes needed (may already be fixed)")

        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Error fixing IMVA initialization: {e}")
            logger.error(f"❌ Error: {e}", exc_info=True)

        return result

    def fix_wandering_collision_avoidance(self) -> Dict[str, Any]:
        """
        Enhance wandering to avoid collisions with other VAs
        """
        logger.info("="*80)
        logger.info("🔧 Enhancing Wandering with Collision Avoidance")
        logger.info("="*80)

        result = {
            "success": True,
            "changes": [],
            "errors": []
        }

        try:
            imva_file = self.project_root / "scripts" / "python" / "ironman_virtual_assistant.py"

            if not imva_file.exists():
                result["success"] = False
                result["errors"].append(f"IMVA file not found: {imva_file}")
                return result

            content = imva_file.read_text(encoding='utf-8')
            original_content = content

            # Find the wandering section and add collision avoidance
            # Look for "elif self.wandering:" in wander_loop

            wander_section = """                    elif self.wandering:
                        # Normal wandering behavior
                        dx = self.target_x - self.x
                        dy = self.target_y - self.y
                        distance = (dx**2 + dy**2)**0.5

                        if distance > self.speed:
                            self.x += (dx / distance) * self.speed
                            self.y += (dy / distance) * self.speed
                        else:
                            # Reached target, pick new one
                            screen_width = self.root.winfo_screenwidth() if self.root else 1920
                            screen_height = self.root.winfo_screenheight() if self.root else 1080
                            self.target_x = random.randint(100, screen_width - 100)
                            self.target_y = random.randint(100, screen_height - 100)"""

            enhanced_wander = """                    elif self.wandering:
                        # Normal wandering behavior with collision avoidance
                        # Check for other VAs and avoid them
                        avoid_x, avoid_y = 0, 0
                        min_distance = 200  # Minimum distance from other VAs

                        if self.positioning_system:
                            try:
                                # Get positions of other active VAs
                                all_positions = self.positioning_system.get_positions()
                                for va_id, pos_data in all_positions.items():
                                    if va_id != "imva" and pos_data.get("is_active"):
                                        other_x = pos_data.get("x", 0)
                                        other_y = pos_data.get("y", 0)
                                        if other_x and other_y:
                                            # Calculate distance to other VA
                                            dx_other = self.x - other_x
                                            dy_other = self.y - other_y
                                            dist_other = (dx_other**2 + dy_other**2)**0.5

                                            # If too close, add avoidance vector
                                            if dist_other < min_distance and dist_other > 0:
                                                avoid_strength = (min_distance - dist_other) / min_distance
                                                avoid_x += (dx_other / dist_other) * avoid_strength * 50
                                                avoid_y += (dy_other / dist_other) * avoid_strength * 50
                            except Exception as e:
                                self.logger.debug(f"Collision avoidance check failed: {e}")

                        # Normal wandering movement
                        dx = self.target_x - self.x
                        dy = self.target_y - self.y
                        distance = (dx**2 + dy**2)**0.5

                        if distance > self.speed:
                            # Apply avoidance vector if needed
                            if avoid_x != 0 or avoid_y != 0:
                                # Blend wandering and avoidance
                                self.x += (dx / distance) * self.speed * 0.7 + avoid_x * 0.3
                                self.y += (dy / distance) * self.speed * 0.7 + avoid_y * 0.3
                            else:
                                self.x += (dx / distance) * self.speed
                                self.y += (dy / distance) * self.speed
                        else:
                            # Reached target, pick new one (avoiding other VAs)
                            screen_width = self.root.winfo_screenwidth() if self.root else 1920
                            screen_height = self.root.winfo_screenheight() if self.root else 1080

                            # Pick new target that's not too close to other VAs
                            attempts = 0
                            while attempts < 20:
                                new_x = random.randint(100, screen_width - 100)
                                new_y = random.randint(100, screen_height - 100)

                                # Check distance to other VAs
                                too_close = False
                                if self.positioning_system:
                                    try:
                                        all_positions = self.positioning_system.get_positions()
                                        for va_id, pos_data in all_positions.items():
                                            if va_id != "imva" and pos_data.get("is_active"):
                                                other_x = pos_data.get("x", 0)
                                                other_y = pos_data.get("y", 0)
                                                if other_x and other_y:
                                                    dist = ((new_x - other_x)**2 + (new_y - other_y)**2)**0.5
                                                    if dist < min_distance:
                                                        too_close = True
                                                        break
                                    except:
                                        pass

                                if not too_close:
                                    self.target_x = new_x
                                    self.target_y = new_y
                                    break

                                attempts += 1

                            # If we couldn't find a good spot, just use random (better than stacking)
                            if attempts >= 20:
                                self.target_x = random.randint(100, screen_width - 100)
                                self.target_y = random.randint(100, screen_height - 100)"""

            if wander_section in content:
                content = content.replace(wander_section, enhanced_wander)
                result["changes"].append("Enhanced wandering with collision avoidance")
                logger.info("   ✅ Enhanced wandering with collision avoidance")
            else:
                logger.info("   ℹ️  Wandering section not found or already enhanced")

            # Save changes
            if content != original_content:
                imva_file.write_text(content, encoding='utf-8')
                result["changes"].append("Saved enhanced wandering to ironman_virtual_assistant.py")
                logger.info("   ✅ Saved enhanced wandering")
            else:
                logger.info("   ℹ️  No changes needed")

        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Error enhancing wandering: {e}")
            logger.error(f"❌ Error: {e}", exc_info=True)

        return result

    def fix_all(self) -> Dict[str, Any]:
        """Fix all stacking and wandering issues"""
        logger.info("="*80)
        logger.info("🔧 Fixing All VA Stacking and Wandering Issues")
        logger.info("="*80)

        result = {
            "success": True,
            "fixes": [],
            "errors": []
        }

        # Fix 1: Initialization
        init_result = self.fix_imva_initialization()
        result["fixes"].append(init_result)
        if not init_result["success"]:
            result["success"] = False

        # Fix 2: Wandering collision avoidance
        wander_result = self.fix_wandering_collision_avoidance()
        result["fixes"].append(wander_result)
        if not wander_result["success"]:
            result["success"] = False

        logger.info("="*80)
        if result["success"]:
            logger.info("✅ All fixes applied successfully")
        else:
            logger.info("⚠️  Some fixes had errors")
        logger.info("="*80)

        return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix VA Stacking and Enable Wandering")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--init-only", action="store_true", help="Only fix initialization")
    parser.add_argument("--wander-only", action="store_true", help="Only fix wandering")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🔧 Fixing VA Stacking and Wandering")
    print("="*80 + "\n")

    fixer = VAsFixStackingAndWandering(project_root=args.project_root)

    if args.init_only:
        result = fixer.fix_imva_initialization()
    elif args.wander_only:
        result = fixer.fix_wandering_collision_avoidance()
    else:
        result = fixer.fix_all()

    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    print(f"Success: {'✅' if result['success'] else '❌'}")

    if result.get("changes"):
        print("\nChanges:")
        for change in result["changes"]:
            print(f"   ✅ {change}")

    if result.get("fixes"):
        print("\nFixes Applied:")
        for i, fix in enumerate(result["fixes"], 1):
            status = "✅" if fix.get("success") else "❌"
            print(f"   {status} Fix {i}: {len(fix.get('changes', []))} changes")

    if result.get("errors"):
        print("\nErrors:")
        for error in result["errors"]:
            print(f"   ❌ {error}")

    print("\n✅ Complete")
    print("="*80 + "\n")
