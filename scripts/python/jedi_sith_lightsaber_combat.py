#!/usr/bin/env python3
"""
Jedi/Sith Lightsaber Combat Styles with OBI/ANI Swing - ORDER 66: @DOIT

Implements Jedi and Sith lightsaber combat styles with the iconic OBI/ANI swing.
Includes random positioning for combatants and authentic lightsaber animations.

Tags: #COMBAT #LIGHTSABER #JEDI #SITH #OBI #ANI #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import math
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JediSithLightsaberCombat")


class LightsaberStyle(Enum):
    """Lightsaber combat style"""
    JEDI = "jedi"  # Form III: Soresu (defensive), Form IV: Ataru (aggressive)
    SITH = "sith"  # Form VII: Juyo/Vaapad (aggressive), Djem So (power strikes)
    OBI_WAN = "obi_wan"  # Form III: Soresu - Defensive master
    ANAKIN = "anakin"  # Form V: Djem So - Aggressive power strikes


class CombatStance(Enum):
    """Combat stance/position"""
    READY = "ready"
    ATTACKING = "attacking"
    DEFENDING = "defending"
    OBI_ANI_SWING = "obi_ani_swing"  # Iconic overhead downward swing
    PARrying = "parrying"
    RETREATING = "retreating"


@dataclass
class LightsaberCombatStyle:
    """Lightsaber combat style definition"""
    style: LightsaberStyle
    blade_color: str  # Hex color
    hilt_color: str  # Hex color
    blade_length_multiplier: float = 2.5
    swing_speed: float = 1.0
    attack_angles: List[float] = field(default_factory=list)  # Preferred attack angles
    defensive_angles: List[float] = field(default_factory=list)  # Defensive angles
    special_moves: List[str] = field(default_factory=list)
    voice_lines: List[str] = field(default_factory=list)


# Predefined combat styles
JEDI_STYLE = LightsaberCombatStyle(
    style=LightsaberStyle.JEDI,
    blade_color="#00FFFF",  # Cyan (traditional Jedi)
    hilt_color="#404040",
    blade_length_multiplier=2.5,
    swing_speed=1.0,
    attack_angles=[0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4],
    defensive_angles=[math.pi/6, math.pi/3, 2*math.pi/3, 5*math.pi/6],
    special_moves=["Force Push", "Force Pull", "Saber Throw"],
    voice_lines=["The Force is with me!", "I will do what I must!", "For the Republic!"]
)

SITH_STYLE = LightsaberCombatStyle(
    style=LightsaberStyle.SITH,
    blade_color="#FF0000",  # Red (traditional Sith)
    hilt_color="#202020",
    blade_length_multiplier=2.7,  # Slightly longer, more aggressive
    swing_speed=1.2,  # Faster, more aggressive
    attack_angles=[math.pi/6, math.pi/3, math.pi/2, 2*math.pi/3, 5*math.pi/6, math.pi],
    defensive_angles=[math.pi/4, 3*math.pi/4],
    special_moves=["Force Lightning", "Force Choke", "Dark Side Rage"],
    voice_lines=["You will pay for your weakness!", "The Dark Side is stronger!", "Give in to your anger!"]
)

OBI_WAN_STYLE = LightsaberCombatStyle(
    style=LightsaberStyle.OBI_WAN,
    blade_color="#00FFFF",  # Cyan (Jedi blue)
    hilt_color="#404040",
    blade_length_multiplier=2.5,
    swing_speed=0.9,  # More defensive, calculated
    attack_angles=[math.pi/3, math.pi/2, 2*math.pi/3],  # High guard positions
    defensive_angles=[0, math.pi/6, 5*math.pi/6, math.pi],  # Strong defensive coverage
    special_moves=["Soresu Defense", "OBI/ANI Swing", "Defensive Stance", "Force Push"],
    voice_lines=["You were the chosen one!", "Hello there!", "So uncivilized.", "You underestimate my power!"]
)

ANAKIN_STYLE = LightsaberCombatStyle(
    style=LightsaberStyle.ANAKIN,
    blade_color="#00AAFF",  # Bright blue (Anakin's saber)
    hilt_color="#404040",
    blade_length_multiplier=2.6,
    swing_speed=1.3,  # Fast, aggressive, powerful
    attack_angles=[0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi],  # Wide, aggressive arcs
    defensive_angles=[math.pi/6, 5*math.pi/6],
    special_moves=["Djem So Power Strike", "OBI/ANI Swing", "Aggressive Flurry", "Force Choke"],
    voice_lines=["I have the high ground!", "You underestimate my power!", "This is where the fun begins!", "I hate you!"]
)


class JediSithLightsaberCombat:
    """
    Jedi/Sith Lightsaber Combat System

    Implements authentic lightsaber combat with Jedi/Sith styles and OBI/ANI swing
    """

    STYLE_MAP = {
        LightsaberStyle.JEDI: JEDI_STYLE,
        LightsaberStyle.SITH: SITH_STYLE,
        LightsaberStyle.OBI_WAN: OBI_WAN_STYLE,
        LightsaberStyle.ANAKIN: ANAKIN_STYLE,
    }

    def __init__(self):
        """Initialize lightsaber combat system"""
        self.current_style: Optional[LightsaberCombatStyle] = None
        self.current_stance: CombatStance = CombatStance.READY
        self.animation_frame: int = 0
        self.obi_ani_swing_frame: int = 0  # Special frame counter for OBI/ANI swing
        self.obi_ani_swing_active: bool = False

        logger.info("✅ Jedi/Sith Lightsaber Combat System initialized")

    def set_style(self, style: LightsaberStyle) -> Dict[str, Any]:
        """Set combat style"""
        self.current_style = self.STYLE_MAP.get(style)
        if not self.current_style:
            return {"error": f"Unknown style: {style}"}

        logger.info(f"⚔️  Combat style set: {style.value}")
        return {
            "success": True,
            "style": style.value,
            "blade_color": self.current_style.blade_color,
            "hilt_color": self.current_style.hilt_color
        }

    def execute_obi_ani_swing(self) -> Dict[str, Any]:
        """
        Execute the iconic OBI/ANI swing

        This is the overhead downward swing that Obi-Wan and Anakin use in their duel.
        Starts high, swings down with power.
        """
        if not self.current_style:
            return {"error": "No combat style set"}

        self.obi_ani_swing_active = True
        self.obi_ani_swing_frame = 0
        self.current_stance = CombatStance.OBI_ANI_SWING

        logger.info("⚔️  OBI/ANI SWING EXECUTED!")
        return {
            "success": True,
            "move": "OBI/ANI Swing",
            "description": "Iconic overhead downward swing - high to low power strike",
            "damage_multiplier": 1.5,  # More powerful than regular swings
            "stance": self.current_stance.value
        }

    def get_lightsaber_angle(self, base_angle: float = 0.0) -> float:
        """
        Get current lightsaber angle based on style and stance

        Args:
            base_angle: Base angle offset

        Returns:
            Current lightsaber angle in radians
        """
        if not self.current_style:
            return base_angle

        # OBI/ANI Swing animation (overhead downward swing)
        if self.obi_ani_swing_active:
            # Swing starts at -pi/2 (overhead) and swings down to pi/2 (low)
            swing_progress = min(1.0, self.obi_ani_swing_frame / 20.0)  # 20 frames for swing
            swing_angle = -math.pi/2 + (math.pi * swing_progress)  # -90° to +90°

            # Add slight arc for more dramatic effect
            arc_offset = math.sin(swing_progress * math.pi) * 0.2
            return swing_angle + arc_offset + base_angle

        # Regular combat based on stance
        if self.current_stance == CombatStance.ATTACKING:
            # Use attack angles from style
            if self.current_style.attack_angles:
                angle_idx = (self.animation_frame // 5) % len(self.current_style.attack_angles)
                return self.current_style.attack_angles[angle_idx] + base_angle
            else:
                # Default aggressive arc
                return (self.animation_frame * 0.2 * self.current_style.swing_speed) % (2 * math.pi)

        elif self.current_stance == CombatStance.DEFENDING:
            # Use defensive angles
            if self.current_style.defensive_angles:
                angle_idx = (self.animation_frame // 8) % len(self.current_style.defensive_angles)
                return self.current_style.defensive_angles[angle_idx] + base_angle
            else:
                # Default defensive position (horizontal)
                return math.pi/2 + base_angle

        elif self.current_stance == CombatStance.PARrying:
            # Parrying motion (quick defensive arcs)
            return (self.animation_frame * 0.3 * self.current_style.swing_speed) % (2 * math.pi) + base_angle

        else:
            # Ready stance - subtle movement
            return (self.animation_frame * 0.1 * self.current_style.swing_speed) % (2 * math.pi) + base_angle

    def update_animation(self):
        """Update animation frame"""
        self.animation_frame += 1

        # Update OBI/ANI swing
        if self.obi_ani_swing_active:
            self.obi_ani_swing_frame += 1
            if self.obi_ani_swing_frame >= 20:  # Swing completes in 20 frames
                self.obi_ani_swing_active = False
                self.obi_ani_swing_frame = 0
                self.current_stance = CombatStance.READY

    def get_blade_color(self) -> str:
        """Get current blade color"""
        if not self.current_style:
            return "#00FFFF"  # Default cyan
        return self.current_style.blade_color

    def get_hilt_color(self) -> str:
        """Get current hilt color"""
        if not self.current_style:
            return "#404040"  # Default gray
        return self.current_style.hilt_color

    def get_blade_length_multiplier(self) -> float:
        """Get blade length multiplier"""
        if not self.current_style:
            return 2.5
        return self.current_style.blade_length_multiplier

    def set_stance(self, stance: CombatStance):
        """Set combat stance"""
        self.current_stance = stance
        logger.debug(f"⚔️  Stance changed to: {stance.value}")

    def get_voice_line(self) -> Optional[str]:
        """Get random voice line for current style"""
        if not self.current_style or not self.current_style.voice_lines:
            return None
        return random.choice(self.current_style.voice_lines)


def calculate_random_position(
    screen_width: int = 1920,
    screen_height: int = 1080,
    window_size: int = 120,
    margin: int = 50,
    avoid_positions: Optional[List[Tuple[int, int]]] = None
) -> Tuple[int, int]:
    """
    Calculate random position for combatant (within safe bounds)

    Args:
        screen_width: Screen width
        screen_height: Screen height
        window_size: Window size
        margin: Margin from edges
        avoid_positions: List of (x, y) positions to avoid (for spacing)

    Returns:
        (x, y) position
    """
    if avoid_positions is None:
        avoid_positions = []

    min_x = margin + window_size // 2
    max_x = screen_width - margin - window_size // 2
    min_y = margin + window_size // 2
    max_y = screen_height - margin - window_size // 2

    spacing = max(300, window_size + 200)  # DEFINITIVE spacing to prevent clumping (300px absolute minimum)

    # Try up to 50 times to find a position that doesn't overlap
    for attempt in range(50):
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)

        # Check if position is far enough from existing positions
        if not avoid_positions:
            return x, y

        too_close = False
        for (avoid_x, avoid_y) in avoid_positions:
            distance = math.sqrt((x - avoid_x)**2 + (y - avoid_y)**2)
            if distance < spacing:
                too_close = True
                break

        if not too_close:
            return x, y

    # If we couldn't find a good position, use center with offset
    center_x = screen_width // 2
    center_y = screen_height // 2
    offset_x = random.randint(-200, 200)
    offset_y = random.randint(-200, 200)

    return (
        max(min_x, min(max_x, center_x + offset_x)),
        max(min_y, min(max_y, center_y + offset_y))
    )


def main():
    """Main entry point - demo"""
    import argparse

    parser = argparse.ArgumentParser(description="Jedi/Sith Lightsaber Combat - ORDER 66: @DOIT")
    parser.add_argument('--style', choices=['jedi', 'sith', 'obi_wan', 'anakin'], default='jedi', help='Combat style')
    parser.add_argument('--demo-obi-ani', action='store_true', help='Demo OBI/ANI swing')

    args = parser.parse_args()

    combat = JediSithLightsaberCombat()

    style_map = {
        'jedi': LightsaberStyle.JEDI,
        'sith': LightsaberStyle.SITH,
        'obi_wan': LightsaberStyle.OBI_WAN,
        'anakin': LightsaberStyle.ANAKIN
    }

    result = combat.set_style(style_map[args.style])
    if result.get('success'):
        print(f"\n⚔️  Combat Style: {args.style.upper()}")
        print(f"   Blade Color: {result['blade_color']}")
        print(f"   Hilt Color: {result['hilt_color']}")
        print(f"   Special Moves: {', '.join(combat.current_style.special_moves)}")
        print(f"   Voice Lines: {', '.join(combat.current_style.voice_lines[:3])}...")

    if args.demo_obi_ani:
        print("\n⚔️  Executing OBI/ANI Swing...")
        result = combat.execute_obi_ani_swing()
        if result.get('success'):
            print(f"   ✅ {result['move']}")
            print(f"   {result['description']}")
            print(f"   Damage Multiplier: {result['damage_multiplier']}x")

    # Demo random positioning
    print("\n📍 Random Positioning Demo:")
    positions = []
    for i in range(3):
        x, y = calculate_random_position(avoid_positions=positions)
        positions.append((x, y))
        print(f"   Combatant {i+1}: ({x}, {y})")

    return 0


if __name__ == "__main__":


    sys.exit(main())