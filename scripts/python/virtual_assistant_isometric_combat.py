#!/usr/bin/env python3
"""
Virtual Assistant Isometric Combat System

3D Isometric Top-Down Fighting Game
Inspired by: Mortal Kombat / Street Fighter (mechanics)
Style: League of Legends / Diablo (isometric top-down view)

Interactive entertainment enhancement for virtual assistants.

Tags: #virtual_assistant #gaming #isometric #3d #combat #entertainment #interactive
"""

import sys
import math
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VirtualAssistantIsometricCombat")

# Try to import graphics libraries
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("⚠️  Pygame not available - install: pip install pygame")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("⚠️  NumPy not available - install: pip install numpy")


class FighterType(Enum):
    """Fighter types/characters"""
    JARVIS = "jarvis"
    FRIDAY = "friday"
    EDITH = "edith"
    VISION = "vision"
    IRON_LEGION = "iron_legion"
    CUSTOM = "custom"


class CombatAction(Enum):
    """Combat actions"""
    IDLE = "idle"
    MOVE = "move"
    ATTACK_LIGHT = "attack_light"
    ATTACK_HEAVY = "attack_heavy"
    SPECIAL = "special"
    BLOCK = "block"
    DODGE = "dodge"
    ULTIMATE = "ultimate"
    TAUNT = "taunt"


class Direction(Enum):
    """Movement directions"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    UP_LEFT = "up_left"
    UP_RIGHT = "up_right"
    DOWN_LEFT = "down_left"
    DOWN_RIGHT = "down_right"


@dataclass
class FighterStats:
    """Fighter statistics"""
    health: int = 100
    max_health: int = 100
    energy: int = 100
    max_energy: int = 100
    attack_power: int = 10
    defense: int = 5
    speed: int = 5
    special_cooldown: int = 0
    ultimate_cooldown: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Fighter:
    """Fighter character"""
    fighter_id: str
    fighter_type: FighterType
    name: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # (x, y, z) in 3D space
    isometric_position: Tuple[int, int] = (0, 0)  # (x, y) on screen
    rotation: float = 0.0  # Rotation angle in degrees
    stats: FighterStats = field(default_factory=FighterStats)
    current_action: CombatAction = CombatAction.IDLE
    action_frame: int = 0
    facing_direction: Direction = Direction.DOWN
    color: Tuple[int, int, int] = (255, 255, 255)
    is_alive: bool = True

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['fighter_type'] = self.fighter_type.value
        result['current_action'] = self.current_action.value
        result['facing_direction'] = self.facing_direction.value
        result['position'] = list(self.position)
        result['isometric_position'] = list(self.isometric_position)
        result['color'] = list(self.color)
        result['stats'] = self.stats.to_dict()
        return result


@dataclass
class CombatMove:
    """Combat move definition"""
    move_id: str
    name: str
    action_type: CombatAction
    damage: int
    energy_cost: int
    cooldown: int
    range: float
    animation_frames: int
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['action_type'] = self.action_type.value
        return result


class IsometricProjection:
    """
    Isometric projection for 3D to 2D conversion
    League of Legends / Diablo style top-down isometric view
    """

    def __init__(self, tile_width: int = 64, tile_height: int = 32):
        self.tile_width = tile_width
        self.tile_height = tile_height
        # Isometric angle (typically 30 degrees)
        self.angle = math.radians(30)
        self.cos_angle = math.cos(self.angle)
        self.sin_angle = math.sin(self.angle)

    def world_to_screen(self, x: float, y: float, z: float = 0.0) -> Tuple[int, int]:
        """
        Convert 3D world coordinates to 2D isometric screen coordinates

        Args:
            x: World X coordinate
            y: World Y coordinate (depth)
            z: World Z coordinate (height)

        Returns:
            (screen_x, screen_y) tuple
        """
        # Isometric projection formula
        screen_x = int((x - y) * self.cos_angle * self.tile_width / 2)
        screen_y = int((x + y) * self.sin_angle * self.tile_height / 2 - z * self.tile_height)

        return (screen_x, screen_y)

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """
        Convert 2D screen coordinates to 3D world coordinates (approximate)
        """
        # Inverse isometric projection
        world_x = (screen_x / (self.cos_angle * self.tile_width / 2) + 
                  screen_y / (self.sin_angle * self.tile_height / 2)) / 2
        world_y = (screen_y / (self.sin_angle * self.tile_height / 2) - 
                  screen_x / (self.cos_angle * self.tile_width / 2)) / 2

        return (world_x, world_y)


class VirtualAssistantIsometricCombat:
    """
    Virtual Assistant Isometric Combat System

    3D Isometric Top-Down Fighting Game
    - Mortal Kombat / Street Fighter mechanics
    - League of Legends / Diablo style view
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "isometric_combat"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Isometric projection
        self.projection = IsometricProjection()

        # Fighters
        self.fighters: Dict[str, Fighter] = {}

        # Combat moves
        self.moves: Dict[str, CombatMove] = {}

        # Game state
        self.is_running = False
        self.current_round = 1
        self.round_time = 0
        self.winner: Optional[str] = None

        # Initialize default fighters
        self._initialize_default_fighters()
        self._initialize_default_moves()

        logger.info("=" * 80)
        logger.info("⚔️  VIRTUAL ASSISTANT ISOMETRIC COMBAT SYSTEM")
        logger.info("=" * 80)
        logger.info("   Style: 3D Isometric Top-Down (LoL/Diablo)")
        logger.info("   Mechanics: Mortal Kombat/Street Fighter")
        logger.info("=" * 80)
        logger.info("")

    def _initialize_default_fighters(self):
        """Initialize default fighter characters"""
        fighters_data = [
            {
                "fighter_id": "jarvis_001",
                "fighter_type": FighterType.JARVIS,
                "name": "JARVIS",
                "position": (0.0, 0.0, 0.0),
                "color": (0, 204, 255),  # Cyan
                "stats": FighterStats(
                    health=100,
                    max_health=100,
                    attack_power=12,
                    defense=6,
                    speed=6
                )
            },
            {
                "fighter_id": "friday_001",
                "fighter_type": FighterType.FRIDAY,
                "name": "FRIDAY",
                "position": (5.0, 0.0, 0.0),
                "color": (255, 51, 51),  # Red
                "stats": FighterStats(
                    health=90,
                    max_health=90,
                    attack_power=15,
                    defense=4,
                    speed=8
                )
            },
            {
                "fighter_id": "edith_001",
                "fighter_type": FighterType.EDITH,
                "name": "EDITH",
                "position": (0.0, 5.0, 0.0),
                "color": (204, 204, 204),  # Silver
                "stats": FighterStats(
                    health=110,
                    max_health=110,
                    attack_power=10,
                    defense=8,
                    speed=5
                )
            },
            {
                "fighter_id": "vision_001",
                "fighter_type": FighterType.VISION,
                "name": "VISION",
                "position": (5.0, 5.0, 0.0),
                "color": (255, 200, 0),  # Gold
                "stats": FighterStats(
                    health=110,
                    max_health=110,
                    attack_power=13,
                    defense=8,
                    speed=6
                )
            }
        ]

        for fighter_data in fighters_data:
            fighter = Fighter(**fighter_data)
            # Calculate isometric position
            iso_x, iso_y = self.projection.world_to_screen(*fighter.position)
            fighter.isometric_position = (iso_x, iso_y)
            self.fighters[fighter.fighter_id] = fighter

        logger.info(f"✅ Initialized {len(self.fighters)} default fighters")

    def _initialize_default_moves(self):
        """Initialize default combat moves"""
        moves_data = [
            {
                "move_id": "light_punch",
                "name": "Light Punch",
                "action_type": CombatAction.ATTACK_LIGHT,
                "damage": 5,
                "energy_cost": 5,
                "cooldown": 0,
                "range": 1.5,
                "animation_frames": 10,
                "description": "Quick light attack"
            },
            {
                "move_id": "heavy_punch",
                "name": "Heavy Punch",
                "action_type": CombatAction.ATTACK_HEAVY,
                "damage": 15,
                "energy_cost": 15,
                "cooldown": 20,
                "range": 1.5,
                "animation_frames": 20,
                "description": "Powerful heavy attack"
            },
            {
                "move_id": "special_attack",
                "name": "Special Attack",
                "action_type": CombatAction.SPECIAL,
                "damage": 25,
                "energy_cost": 30,
                "cooldown": 60,
                "range": 3.0,
                "animation_frames": 30,
                "description": "Fighter-specific special move"
            },
            {
                "move_id": "ultimate",
                "name": "Ultimate",
                "action_type": CombatAction.ULTIMATE,
                "damage": 50,
                "energy_cost": 50,
                "cooldown": 180,
                "range": 5.0,
                "animation_frames": 60,
                "description": "Devastating ultimate attack"
            },
            {
                "move_id": "block",
                "name": "Block",
                "action_type": CombatAction.BLOCK,
                "damage": 0,
                "energy_cost": 10,
                "cooldown": 0,
                "range": 0.0,
                "animation_frames": 5,
                "description": "Block incoming attacks"
            },
            {
                "move_id": "dodge",
                "name": "Dodge",
                "action_type": CombatAction.DODGE,
                "damage": 0,
                "energy_cost": 15,
                "cooldown": 30,
                "range": 2.0,
                "animation_frames": 15,
                "description": "Dodge incoming attacks"
            }
        ]

        for move_data in moves_data:
            move = CombatMove(**move_data)
            self.moves[move.move_id] = move

        logger.info(f"✅ Initialized {len(self.moves)} default moves")

    def add_fighter(
        self,
        fighter_id: str,
        fighter_type: FighterType,
        name: str,
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        color: Tuple[int, int, int] = (255, 255, 255),
        stats: Optional[FighterStats] = None
    ) -> Fighter:
        """Add a new fighter to the combat"""
        fighter = Fighter(
            fighter_id=fighter_id,
            fighter_type=fighter_type,
            name=name,
            position=position,
            color=color,
            stats=stats or FighterStats()
        )

        # Calculate isometric position
        iso_x, iso_y = self.projection.world_to_screen(*fighter.position)
        fighter.isometric_position = (iso_x, iso_y)

        self.fighters[fighter_id] = fighter

        logger.info(f"✅ Added fighter: {name} ({fighter_id})")

        return fighter

    def move_fighter(
        self,
        fighter_id: str,
        direction: Direction,
        distance: float = 1.0
    ) -> bool:
        """Move fighter in specified direction"""
        if fighter_id not in self.fighters:
            return False

        fighter = self.fighters[fighter_id]
        if not fighter.is_alive:
            return False

        # Calculate movement vector
        dx, dy = 0.0, 0.0

        if direction == Direction.UP:
            dy = -distance
        elif direction == Direction.DOWN:
            dy = distance
        elif direction == Direction.LEFT:
            dx = -distance
        elif direction == Direction.RIGHT:
            dx = distance
        elif direction == Direction.UP_LEFT:
            dx = -distance * 0.707
            dy = -distance * 0.707
        elif direction == Direction.UP_RIGHT:
            dx = distance * 0.707
            dy = -distance * 0.707
        elif direction == Direction.DOWN_LEFT:
            dx = -distance * 0.707
            dy = distance * 0.707
        elif direction == Direction.DOWN_RIGHT:
            dx = distance * 0.707
            dy = distance * 0.707

        # Update position
        x, y, z = fighter.position
        fighter.position = (x + dx, y + dy, z)

        # Update isometric position
        iso_x, iso_y = self.projection.world_to_screen(*fighter.position)
        fighter.isometric_position = (iso_x, iso_y)
        fighter.facing_direction = direction

        fighter.current_action = CombatAction.MOVE
        fighter.action_frame = 0

        return True

    def execute_move(
        self,
        fighter_id: str,
        move_id: str,
        target_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a combat move"""
        if fighter_id not in self.fighters:
            return {"success": False, "error": "Fighter not found"}

        if move_id not in self.moves:
            return {"success": False, "error": "Move not found"}

        fighter = self.fighters[fighter_id]
        move = self.moves[move_id]

        if not fighter.is_alive:
            return {"success": False, "error": "Fighter is dead"}

        if fighter.stats.energy < move.energy_cost:
            return {"success": False, "error": "Not enough energy"}

        # Set action
        fighter.current_action = move.action_type
        fighter.action_frame = 0

        # Consume energy
        fighter.stats.energy -= move.energy_cost

        result = {
            "success": True,
            "fighter": fighter_id,
            "move": move_id,
            "damage": 0,
            "hit": False
        }

        # If attack move, check for target
        if move.action_type in [CombatAction.ATTACK_LIGHT, CombatAction.ATTACK_HEAVY,
                                CombatAction.SPECIAL, CombatAction.ULTIMATE]:
            if target_id and target_id in self.fighters:
                target = self.fighters[target_id]

                # Check range
                distance = self._calculate_distance(fighter.position, target.position)
                if distance <= move.range:
                    # Calculate damage
                    damage = move.damage - target.stats.defense
                    damage = max(1, damage)  # Minimum 1 damage

                    target.stats.health -= damage
                    target.stats.health = max(0, target.stats.health)

                    if target.stats.health <= 0:
                        target.is_alive = False
                        target.stats.health = 0

                    result["damage"] = damage
                    result["hit"] = True
                    result["target"] = target_id
                    result["target_health"] = target.stats.health

                    logger.info(f"💥 {fighter.name} hit {target.name} for {damage} damage!")
                else:
                    result["hit"] = False
                    result["error"] = "Target out of range"

        return result

    def _calculate_distance(self, pos1: Tuple[float, float, float], 
                           pos2: Tuple[float, float, float]) -> float:
        """Calculate 3D distance between two positions"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def update(self, delta_time: float = 0.016):
        """Update game state"""
        if not self.is_running:
            return

        self.round_time += delta_time

        # Update fighters
        for fighter in self.fighters.values():
            if fighter.current_action != CombatAction.IDLE:
                fighter.action_frame += 1

                # Get move for current action
                move = None
                for m in self.moves.values():
                    if m.action_type == fighter.current_action:
                        move = m
                        break

                if move and fighter.action_frame >= move.animation_frames:
                    fighter.current_action = CombatAction.IDLE
                    fighter.action_frame = 0

            # Regenerate energy
            if fighter.stats.energy < fighter.stats.max_energy:
                fighter.stats.energy = min(
                    fighter.stats.max_energy,
                    fighter.stats.energy + 1 * delta_time
                )

        # Check for winner
        alive_fighters = [f for f in self.fighters.values() if f.is_alive]
        if len(alive_fighters) == 1:
            self.winner = alive_fighters[0].fighter_id
            self.is_running = False
            logger.info(f"🏆 Winner: {alive_fighters[0].name}")
        elif len(alive_fighters) == 0:
            self.winner = None
            self.is_running = False
            logger.info("🤝 Draw - All fighters eliminated")

    def start_combat(self, fighter_ids: Optional[List[str]] = None):
        """Start a combat round"""
        if fighter_ids is None:
            fighter_ids = list(self.fighters.keys())

        # Reset fighters
        for fighter_id in fighter_ids:
            if fighter_id in self.fighters:
                fighter = self.fighters[fighter_id]
                fighter.stats.health = fighter.stats.max_health
                fighter.stats.energy = fighter.stats.max_energy
                fighter.is_alive = True
                fighter.current_action = CombatAction.IDLE
                fighter.action_frame = 0

        self.is_running = True
        self.round_time = 0
        self.winner = None
        self.current_round += 1

        logger.info("=" * 80)
        logger.info("⚔️  COMBAT STARTED")
        logger.info("=" * 80)
        logger.info(f"Round: {self.current_round}")
        logger.info(f"Fighters: {', '.join([self.fighters[fid].name for fid in fighter_ids])}")
        logger.info("=" * 80)
        logger.info("")

    def get_combat_state(self) -> Dict[str, Any]:
        """Get current combat state"""
        return {
            "is_running": self.is_running,
            "round": self.current_round,
            "round_time": self.round_time,
            "winner": self.winner,
            "fighters": {fid: f.to_dict() for fid, f in self.fighters.items()},
            "moves": {mid: m.to_dict() for mid, m in self.moves.items()}
        }

    def save_state(self):
        try:
            """Save combat state"""
            state_file = self.data_dir / "combat_state.json"

            state = {
                "combat_state": self.get_combat_state(),
                "saved_at": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)

            logger.info(f"💾 Combat state saved: {state_file}")


        except Exception as e:
            self.logger.error(f"Error in save_state: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Virtual Assistant Isometric Combat")
    parser.add_argument('--start', action='store_true', help='Start combat')
    parser.add_argument('--fighters', nargs='+', metavar='FIGHTER_ID', help='Fighter IDs to include')
    parser.add_argument('--move', nargs=3, metavar=('FIGHTER_ID', 'MOVE_ID', 'TARGET_ID'),
                       help='Execute move (target optional)')
    parser.add_argument('--state', action='store_true', help='Show combat state')
    parser.add_argument('--save', action='store_true', help='Save state')

    args = parser.parse_args()

    combat = VirtualAssistantIsometricCombat()

    if args.start:
        combat.start_combat(args.fighters)
        print("\n✅ Combat started")
        if args.save:
            combat.save_state()

    elif args.move:
        fighter_id, move_id, target_id = args.move
        if target_id == "None":
            target_id = None
        result = combat.execute_move(fighter_id, move_id, target_id)
        print(f"\n{'✅' if result.get('success') else '❌'} Move executed")
        if result.get('success'):
            print(f"   Fighter: {result.get('fighter')}")
            print(f"   Move: {result.get('move')}")
            if result.get('hit'):
                print(f"   Damage: {result.get('damage')}")
                print(f"   Target Health: {result.get('target_health')}")
        else:
            print(f"   Error: {result.get('error')}")
        if args.save:
            combat.save_state()

    elif args.state:
        state = combat.get_combat_state()
        print("\n" + "=" * 80)
        print("⚔️  COMBAT STATE")
        print("=" * 80)
        print(f"Running: {state['is_running']}")
        print(f"Round: {state['round']}")
        print(f"Winner: {state['winner'] or 'None'}")
        print("")
        print("Fighters:")
        for fid, fighter in state['fighters'].items():
            status = "✅" if fighter['is_alive'] else "❌"
            print(f"   {status} {fighter['name']}: HP {fighter['stats']['health']}/{fighter['stats']['max_health']}, "
                  f"Energy {fighter['stats']['energy']}/{fighter['stats']['max_energy']}")
        print("=" * 80)
        print("")
        if args.save:
            combat.save_state()

    else:
        print("\n" + "=" * 80)
        print("⚔️  VIRTUAL ASSISTANT ISOMETRIC COMBAT")
        print("=" * 80)
        print("   Style: 3D Isometric Top-Down (LoL/Diablo)")
        print("   Mechanics: Mortal Kombat/Street Fighter")
        print("")
        print("Use --start to start combat")
        print("Use --move to execute moves")
        print("Use --state to show state")
        print("=" * 80)
        print("")


if __name__ == "__main__":


    main()