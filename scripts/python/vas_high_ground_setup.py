#!/usr/bin/env python3
"""
VAs High Ground Setup - ORDER 66: @DOIT PROCEED

Sets up "THE HIGH GROUND" positioning for heroes and villains.
Heroes (IMVA) get the high ground (top of screen).
Villains (ACVA, ULTRON) get the low ground (bottom of screen).

Tags: #VAS #IMVA #ACVA #HIGHGROUND #POSITIONING #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from datetime import datetime
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

logger = get_logger("VAsHighGround")

# Import positioning system
try:
    from va_positioning_combat_system import VAPositioningCombatSystem
    POSITIONING_AVAILABLE = True
except ImportError:
    POSITIONING_AVAILABLE = False
    logger.warning("VA Positioning System not available")


class VAsHighGroundSetup:
    """
    Set up THE HIGH GROUND for heroes and villains

    Heroes (IMVA) = HIGH GROUND (top of screen)
    Villains (ACVA, ULTRON) = LOW GROUND (bottom of screen)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize high ground setup"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"

        # Initialize positioning system
        self.positioning = None
        if POSITIONING_AVAILABLE:
            try:
                self.positioning = VAPositioningCombatSystem(project_root=self.project_root)
                logger.info("✅ VA Positioning System initialized")
            except Exception as e:
                logger.warning(f"⚠️  VA Positioning System not available: {e}")

        logger.info("✅ VAs High Ground Setup initialized")

    def setup_high_ground(self) -> Dict[str, Any]:
        """
        Set up THE HIGH GROUND positioning

        ORDER 66: @DOIT PROCEED - Actually DO IT
        """
        logger.info("="*80)
        logger.info("⚔️  ORDER 66: @DOIT PROCEED - Setting Up THE HIGH GROUND")
        logger.info("="*80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "execution_type": "ORDER 66: @DOIT PROCEED - High Ground Setup",
            "heroes_positioned": [],
            "villains_positioned": [],
            "success": True,
            "errors": []
        }

        if not self.positioning:
            logger.error("❌ Positioning system not available")
            result["success"] = False
            result["errors"].append("Positioning system not available")
            return result

        # Detect screen size
        self.positioning.detect_screen_size()
        screen_width = self.positioning.screen_width
        screen_height = self.positioning.screen_height

        logger.info(f"📺 Screen detected: {screen_width}x{screen_height}")
        logger.info("")

        # THE HIGH GROUND: Top 20% of screen (heroes)
        high_ground_y_min = 50
        high_ground_y_max = int(screen_height * 0.2)  # Top 20%

        # THE LOW GROUND: Bottom 20% of screen (villains)
        low_ground_y_min = int(screen_height * 0.8)  # Bottom 20%
        low_ground_y_max = screen_height - 50

        logger.info("⚔️  Setting up positioning...")
        logger.info(f"   HIGH GROUND (Heroes): Y = {high_ground_y_min} to {high_ground_y_max}")
        logger.info(f"   LOW GROUND (Villains): Y = {low_ground_y_min} to {low_ground_y_max}")
        logger.info("")

        # Position IMVA (Hero) - HIGH GROUND
        logger.info("🦸 Positioning IMVA (Hero) on THE HIGH GROUND...")
        try:
            window_size = 120
            margin = 50

            # High ground position (top of screen, center-left)
            imva_x = margin + window_size // 2
            imva_y = high_ground_y_min + (high_ground_y_max - high_ground_y_min) // 2

            # Update positioning system
            if "imva" not in self.positioning.va_positions:
                from va_positioning_combat_system import VAPosition
                self.positioning.va_positions["imva"] = VAPosition(
                    va_id="imva",
                    x=imva_x,
                    y=imva_y,
                    window_size=window_size,
                    is_active=True
                )
            else:
                self.positioning.va_positions["imva"].x = imva_x
                self.positioning.va_positions["imva"].y = imva_y
                self.positioning.va_positions["imva"].is_active = True

            self.positioning._save_positions()

            result["heroes_positioned"].append({
                "va_id": "imva",
                "name": "Iron Man Virtual Assistant",
                "position": {"x": imva_x, "y": imva_y},
                "ground": "HIGH GROUND",
                "role": "Hero"
            })

            logger.info(f"   ✅ IMVA positioned at HIGH GROUND: ({imva_x}, {imva_y})")
        except Exception as e:
            error_msg = f"Error positioning IMVA: {e}"
            logger.error(f"   ❌ {error_msg}")
            result["errors"].append(error_msg)

        # Position ACVA (Villain) - LOW GROUND
        logger.info("⚔️  Positioning ACVA (Villain) on THE LOW GROUND...")
        try:
            window_size = 120
            margin = 50

            # Low ground position (bottom of screen, center-right)
            acva_x = screen_width - margin - window_size // 2
            acva_y = low_ground_y_min + (low_ground_y_max - low_ground_y_min) // 2

            # Update positioning system
            if "acva" not in self.positioning.va_positions:
                from va_positioning_combat_system import VAPosition
                self.positioning.va_positions["acva"] = VAPosition(
                    va_id="acva",
                    x=acva_x,
                    y=acva_y,
                    window_size=window_size,
                    is_active=True
                )
            else:
                self.positioning.va_positions["acva"].x = acva_x
                self.positioning.va_positions["acva"].y = acva_y
                self.positioning.va_positions["acva"].is_active = True

            self.positioning._save_positions()

            result["villains_positioned"].append({
                "va_id": "acva",
                "name": "Anakin/Vader Combat Virtual Assistant",
                "position": {"x": acva_x, "y": acva_y},
                "ground": "LOW GROUND",
                "role": "Villain"
            })

            logger.info(f"   ✅ ACVA positioned at LOW GROUND: ({acva_x}, {acva_y})")
        except Exception as e:
            error_msg = f"Error positioning ACVA: {e}"
            logger.error(f"   ❌ {error_msg}")
            result["errors"].append(error_msg)

        # Save report
        report_file = self.data_dir / "vas" / f"high_ground_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"   ✅ Report saved: {report_file.name}")
        except Exception as e:
            logger.error(f"❌ Error saving report: {e}")

        logger.info("="*80)
        logger.info("✅ THE HIGH GROUND Setup Complete")
        logger.info(f"   Heroes on HIGH GROUND: {len(result['heroes_positioned'])}")
        logger.info(f"   Villains on LOW GROUND: {len(result['villains_positioned'])}")
        if result.get('errors'):
            logger.info(f"   Errors: {len(result['errors'])}")
        logger.info("")
        logger.info("⚔️  'It's over Anakin, I have the high ground!' - Obi-Wan")
        logger.info("="*80)

        return result


if __name__ == "__main__":
    print("\n" + "="*80)
    print("⚔️  ORDER 66: @DOIT PROCEED - Setting Up THE HIGH GROUND")
    print("="*80 + "\n")

    setup = VAsHighGroundSetup()
    result = setup.setup_high_ground()

    print("\n" + "="*80)
    print("📊 HIGH GROUND SETUP RESULTS")
    print("="*80)
    print(f"Timestamp: {result['timestamp']}")
    print(f"Execution Type: {result['execution_type']}")
    print(f"Success: {result['success']}")

    print(f"\n🦸 Heroes on HIGH GROUND: {len(result['heroes_positioned'])}")
    for hero in result['heroes_positioned']:
        pos = hero['position']
        print(f"   ⚔️  {hero['name']}: ({pos['x']}, {pos['y']}) - {hero['ground']}")

    print(f"\n⚔️  Villains on LOW GROUND: {len(result['villains_positioned'])}")
    for villain in result['villains_positioned']:
        pos = villain['position']
        print(f"   ⚔️  {villain['name']}: ({pos['x']}, {pos['y']}) - {villain['ground']}")

    if result.get('errors'):
        print(f"\n⚠️  Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"   ❌ {error}")

    print("\n⚔️  'It's over Anakin, I have the high ground!' - Obi-Wan")
    print("✅ THE HIGH GROUND Setup Complete")
    print("="*80 + "\n")
