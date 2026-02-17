#!/usr/bin/env python3
"""
VA Positioning & Combat System - ORDER 66: @DOIT

Fixes VA positioning to prevent stacking/clustering and implements proper 1v1 combat system:
- Only one IMVA vs one opponent at a time (ULTRON or ACVA)
- Random MONSTER encounters (AI model providers - mega-corp billionaires)
- Boss fights (top 5 wealthiest tech billionaires)

Tags: #VAS #IMVA #ACVA #ULTRON #COMBAT #POSITIONING #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import random
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
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

logger = get_logger("VAPositioningCombatSystem")


class OpponentType(Enum):
    """Opponent type classification"""
    ULTRON = "ultron"
    ACVA = "acva"
    MONSTER = "monster"  # AI model provider (mega-corp)
    BOSS = "boss"  # Top 5 wealthiest tech billionaires


class MonsterCategory(Enum):
    """WoW Champion type monster categories"""
    COMMON = "common"  # Standard AI model provider
    ELITE = "elite"  # Major AI company
    CHAMPION = "champion"  # Leading AI provider
    LEGENDARY = "legendary"  # Dominant AI platform


@dataclass
class BossFight:
    """Boss fight definition for tech billionaires"""
    name: str
    company: str
    net_worth: float  # Billions USD
    ai_models: List[str]  # AI models they control
    difficulty: int  # 1-5 (5 = hardest)
    special_abilities: List[str] = field(default_factory=list)
    voice_lines: List[str] = field(default_factory=list)
    visual_style: str = ""


@dataclass
class MonsterEncounter:
    """Monster encounter for AI model providers"""
    name: str
    company: str
    category: MonsterCategory
    ai_models: List[str]
    difficulty: int  # 1-10
    special_abilities: List[str] = field(default_factory=list)
    visual_style: str = ""


@dataclass
class VAPosition:
    """VA position and state"""
    va_id: str  # "imva", "acva", "ultron", etc.
    x: int
    y: int
    window_size: int = 120
    is_active: bool = False
    opponent_type: Optional[OpponentType] = None
    opponent_id: Optional[str] = None


class VAPositioningCombatSystem:
    """
    VA Positioning & Combat System

    Manages VA positioning to prevent stacking and implements 1v1 combat
    """

    # Top 5 wealthiest tech billionaires (BOSS FIGHTS)
    BOSS_FIGHTS = [
        BossFight(
            name="Elon Musk",
            company="Tesla/X/SpaceX/xAI",
            net_worth=200.0,  # Approximate
            ai_models=["Grok", "Tesla FSD", "Neuralink AI"],
            difficulty=5,
            special_abilities=["Mars Colony Defense", "Hyperloop Strike", "Neuralink Control"],
            voice_lines=["Time to show you the power of real AI!", "Grok sees all!"],
            visual_style="tech_industrial"
        ),
        BossFight(
            name="Jeff Bezos",
            company="Amazon",
            net_worth=180.0,
            ai_models=["Alexa", "AWS Bedrock", "Amazon Q"],
            difficulty=4,
            special_abilities=["Prime Delivery Strike", "AWS Cloud Burst", "Alexa Command"],
            voice_lines=["Alexa, destroy the competition!", "Prime time is over!"],
            visual_style="blue_orange_amazon"
        ),
        BossFight(
            name="Mark Zuckerberg",
            company="Meta",
            net_worth=150.0,
            ai_models=["Llama", "Meta AI", "Horizon Worlds AI"],
            difficulty=4,
            special_abilities=["Metaverse Portal", "Reality Warp", "Social Network Overload"],
            voice_lines=["Welcome to the Metaverse!", "Like, comment, and destroy!"],
            visual_style="blue_meta"
        ),
        BossFight(
            name="Bill Gates",
            company="Microsoft",
            net_worth=140.0,
            ai_models=["Copilot", "Azure AI", "GPT Integration"],
            difficulty=5,
            special_abilities=["Windows Blue Screen", "Office Suite Assault", "Azure Cloud Strike"],
            voice_lines=["I see everything through Windows!", "Copilot, engage!"],
            visual_style="windows_blue"
        ),
        BossFight(
            name="Larry Page / Sergey Brin",
            company="Google/Alphabet",
            net_worth=130.0,
            ai_models=["Gemini", "Bard", "DeepMind"],
            difficulty=5,
            special_abilities=["Search Engine Overload", "DeepMind Intelligence", "Gemini Fusion"],
            voice_lines=["I'm feeling lucky... for you to lose!", "Searching for your weakness..."],
            visual_style="google_colors"
        ),
    ]

    # Monster encounters (AI model providers - mega-corp)
    MONSTER_ENCOUNTERS = [
        # Common tier
        MonsterEncounter("OpenAI", "OpenAI", MonsterCategory.COMMON, ["GPT-4", "GPT-3.5", "DALL-E"], 3),
        MonsterEncounter("Anthropic", "Anthropic", MonsterCategory.COMMON, ["Claude"], 3),
        MonsterEncounter("Cohere", "Cohere", MonsterCategory.COMMON, ["Command", "Embed"], 2),

        # Elite tier
        MonsterEncounter("Google DeepMind", "Google", MonsterCategory.ELITE, ["Gemini", "AlphaFold"], 5),
        MonsterEncounter("Microsoft Azure AI", "Microsoft", MonsterCategory.ELITE, ["Copilot", "Azure OpenAI"], 5),
        MonsterEncounter("Amazon AWS AI", "Amazon", MonsterCategory.ELITE, ["Bedrock", "SageMaker"], 4),

        # Champion tier
        MonsterEncounter("Meta AI Research", "Meta", MonsterCategory.CHAMPION, ["Llama", "Code Llama"], 6),
        MonsterEncounter("Tesla AI", "Tesla", MonsterCategory.CHAMPION, ["FSD", "Dojo"], 7),
        MonsterEncounter("NVIDIA AI", "NVIDIA", MonsterCategory.CHAMPION, ["NeMo", "DGX"], 6),

        # Legendary tier
        MonsterEncounter("xAI Grok", "xAI", MonsterCategory.LEGENDARY, ["Grok"], 8),
        MonsterEncounter("Apple Intelligence", "Apple", MonsterCategory.LEGENDARY, ["Apple Intelligence"], 7),
        MonsterEncounter("Oracle AI", "Oracle", MonsterCategory.LEGENDARY, ["Oracle AI"], 6),
    ]

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize VA positioning and combat system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"
        self.va_positions_file = self.data_dir / "va_positions.json"

        # Screen dimensions (default to 1920x1080, will detect)
        self.screen_width = 1920
        self.screen_height = 1080

        # VA positions (tracked)
        self.va_positions: Dict[str, VAPosition] = {}

        # Active combat (1v1 only)
        self.active_combat: Optional[Dict[str, Any]] = None

        # Load existing positions
        self._load_positions()

        logger.info("✅ VA Positioning & Combat System initialized")

    def _load_positions(self):
        """Load VA positions from file"""
        if self.va_positions_file.exists():
            try:
                with open(self.va_positions_file, 'r') as f:
                    data = json.load(f)
                    for va_id, pos_data in data.items():
                        self.va_positions[va_id] = VAPosition(**pos_data)
                logger.info(f"✅ Loaded {len(self.va_positions)} VA positions")
            except Exception as e:
                logger.warning(f"⚠️  Could not load positions: {e}")
                self.va_positions = {}

    def _save_positions(self):
        """Save VA positions to file"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        try:
            data = {
                va_id: {
                    "va_id": pos.va_id,
                    "x": pos.x,
                    "y": pos.y,
                    "window_size": pos.window_size,
                    "is_active": pos.is_active,
                    "opponent_type": pos.opponent_type.value if pos.opponent_type else None,
                    "opponent_id": pos.opponent_id
                }
                for va_id, pos in self.va_positions.items()
            }
            with open(self.va_positions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Could not save positions: {e}")

    def detect_screen_size(self) -> Tuple[int, int]:
        """Detect screen size"""
        try:
            import tkinter as tk
            root = tk.Tk()
            self.screen_width = root.winfo_screenwidth()
            self.screen_height = root.winfo_screenheight()
            root.destroy()
            logger.info(f"✅ Detected screen size: {self.screen_width}x{self.screen_height}")
        except Exception as e:
            logger.warning(f"⚠️  Could not detect screen size: {e}")
            # Default to 1920x1080
            self.screen_width = 1920
            self.screen_height = 1080

        return self.screen_width, self.screen_height

    def calculate_spaced_position(self, va_id: str, window_size: int = 120, use_random: bool = True) -> Tuple[int, int]:
        """
        Calculate spaced position for a VA to prevent stacking

        Positioning strategy:
        - Random positioning (if use_random=True) within safe bounds
        - Minimum spacing: window_size + 150 pixels (270px for 120px window) to prevent globstacking
        - Falls back to strategic positioning if random fails

        Args:
            va_id: VA identifier
            window_size: Window size
            use_random: Use random positioning (True) or strategic (False)
        """
        self.detect_screen_size()

        # DEFINITIVE spacing to prevent clumping (300px absolute minimum)
        spacing = max(300, window_size + 200)  # ABSOLUTE minimum 300px to prevent clumping
        margin = 50

        # Get existing active positions to avoid
        avoid_positions = []
        for pos in self.va_positions.values():
            if pos.is_active and pos.x is not None and pos.y is not None:
                avoid_positions.append((pos.x, pos.y))

        # Use random positioning for authentic combat feel
        if use_random:
            try:
                from jedi_sith_lightsaber_combat import calculate_random_position
                x, y = calculate_random_position(
                    screen_width=self.screen_width,
                    screen_height=self.screen_height,
                    window_size=window_size,
                    margin=margin,
                    avoid_positions=avoid_positions
                )
                # Double-check spacing after random position
                attempts = 0
                while attempts < 100:
                    too_close = False
                    for (avoid_x, avoid_y) in avoid_positions:
                        distance = math.sqrt((x - avoid_x)**2 + (y - avoid_y)**2)
                        if distance < spacing:
                            too_close = True
                            break

                    if not too_close:
                        break

                    # Try new random position
                    x, y = calculate_random_position(
                        screen_width=self.screen_width,
                        screen_height=self.screen_height,
                        window_size=window_size,
                        margin=margin,
                        avoid_positions=avoid_positions
                    )
                    attempts += 1

                return x, y
            except ImportError:
                logger.warning("⚠️  Jedi/Sith combat module not available, using strategic positioning")

        # Fallback: Strategic positioning (original behavior)
        if va_id.lower() == "imva":
            # IMVA at center-left
            x = margin + window_size // 2
            y = self.screen_height // 2
            return x, y

        # Opponents: Center-right, spaced vertically
        center_right_x = self.screen_width - margin - window_size // 2

        active_opponent_y_positions = [pos.y for pos in self.va_positions.values() 
                                      if pos.is_active and pos.va_id != "imva" and pos.y is not None]

        if not active_opponent_y_positions:
            y = self.screen_height // 2
        else:
            center_y = self.screen_height // 2
            y = center_y
            attempts = 0
            while any(abs(y - existing_y) < spacing for existing_y in active_opponent_y_positions) and attempts < 10:
                offset = spacing * ((attempts // 2) + 1) * (1 if attempts % 2 == 0 else -1)
                y = center_y + offset
                attempts += 1
            y = max(margin + window_size // 2, min(y, self.screen_height - margin - window_size // 2))

        return center_right_x, y

    def start_1v1_combat(self, opponent_type: OpponentType, opponent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start 1v1 combat (only one active opponent at a time)

        Args:
            opponent_type: Type of opponent (ULTRON, ACVA, MONSTER, BOSS)
            opponent_id: Optional specific opponent ID

        Returns:
            Combat configuration
        """
        logger.info("="*80)
        logger.info(f"⚔️  Starting 1v1 Combat: IMVA vs {opponent_type.value.upper()}")
        logger.info("="*80)

        # End any existing combat first
        if self.active_combat:
            self.end_combat()

        # Position IMVA
        imva_x, imva_y = self.calculate_spaced_position("imva")
        self.va_positions["imva"] = VAPosition(
            va_id="imva",
            x=imva_x,
            y=imva_y,
            is_active=True
        )

        # Determine opponent
        opponent_name = opponent_id
        if opponent_type == OpponentType.ULTRON:
            opponent_name = opponent_name or "ultron"
            opponent_config = {
                "name": "ULTRON",
                "type": "ultron",
                "difficulty": 5,
                "special_abilities": ["AI Hive Mind", "Self-Replication", "World Domination"],
                "visual_style": "dark_red_glowing"
            }
        elif opponent_type == OpponentType.ACVA:
            opponent_name = opponent_name or "acva"
            opponent_config = {
                "name": "ACVA",
                "type": "acva",
                "difficulty": 4,
                "special_abilities": ["Lightsaber Combat", "Force Powers", "Hybrid Fusion"],
                "visual_style": "anakin_vader"
            }
        elif opponent_type == OpponentType.BOSS:
            # Select random boss or specific one
            if opponent_id:
                boss = next((b for b in self.BOSS_FIGHTS if b.name.lower() == opponent_id.lower()), None)
            else:
                boss = random.choice(self.BOSS_FIGHTS)

            if not boss:
                return {"error": f"Boss '{opponent_id}' not found"}

            opponent_name = boss.name.lower().replace(" ", "_")
            opponent_config = {
                "name": boss.name,
                "company": boss.company,
                "type": "boss",
                "net_worth": boss.net_worth,
                "ai_models": boss.ai_models,
                "difficulty": boss.difficulty,
                "special_abilities": boss.special_abilities,
                "voice_lines": boss.voice_lines,
                "visual_style": boss.visual_style
            }
        elif opponent_type == OpponentType.MONSTER:
            # Select random monster or specific one
            if opponent_id:
                monster = next((m for m in self.MONSTER_ENCOUNTERS if m.name.lower() == opponent_id.lower()), None)
            else:
                monster = random.choice(self.MONSTER_ENCOUNTERS)

            if not monster:
                return {"error": f"Monster '{opponent_id}' not found"}

            opponent_name = monster.name.lower().replace(" ", "_")
            opponent_config = {
                "name": monster.name,
                "company": monster.company,
                "type": "monster",
                "category": monster.category.value,
                "ai_models": monster.ai_models,
                "difficulty": monster.difficulty,
                "special_abilities": monster.special_abilities,
                "visual_style": monster.visual_style
            }
        else:
            return {"error": f"Unknown opponent type: {opponent_type}"}

        # Position opponent (random positioning, spaced from IMVA)
        opponent_x, opponent_y = self.calculate_spaced_position(opponent_name, use_random=True)
        self.va_positions[opponent_name] = VAPosition(
            va_id=opponent_name,
            x=opponent_x,
            y=opponent_y,
            is_active=True,
            opponent_type=opponent_type,
            opponent_id=opponent_name
        )

        # Set active combat (1v1 only)
        self.active_combat = {
            "imva": {
                "position": {"x": imva_x, "y": imva_y},
                "active": True
            },
            "opponent": {
                "name": opponent_name,
                "type": opponent_type.value,
                "config": opponent_config,
                "position": {"x": opponent_x, "y": opponent_y},
                "active": True
            },
            "started_at": __import__('datetime').datetime.now().isoformat()
        }

        # Save positions
        self._save_positions()

        logger.info(f"✅ 1v1 Combat Started: IMVA vs {opponent_config['name']}")
        logger.info(f"   IMVA Position: ({imva_x}, {imva_y})")
        logger.info(f"   {opponent_config['name']} Position: ({opponent_x}, {opponent_y})")

        return {
            "success": True,
            "combat": self.active_combat,
            "message": f"1v1 Combat started: IMVA vs {opponent_config['name']}"
        }

    def end_combat(self) -> Dict[str, Any]:
        """End active combat"""
        if not self.active_combat:
            return {"success": False, "error": "No active combat"}

        # Deactivate opponent
        opponent_name = self.active_combat["opponent"]["name"]
        if opponent_name in self.va_positions:
            self.va_positions[opponent_name].is_active = False

        # Keep IMVA active but clear opponent
        if "imva" in self.va_positions:
            self.va_positions["imva"].is_active = True
            self.va_positions["imva"].opponent_type = None
            self.va_positions["imva"].opponent_id = None

        self.active_combat = None
        self._save_positions()

        logger.info("✅ Combat ended")
        return {"success": True, "message": "Combat ended"}

    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get all VA positions"""
        return {
            va_id: {
                "va_id": pos.va_id,
                "x": pos.x,
                "y": pos.y,
                "window_size": pos.window_size,
                "is_active": pos.is_active,
                "opponent_type": pos.opponent_type.value if pos.opponent_type else None,
                "opponent_id": pos.opponent_id
            }
            for va_id, pos in self.va_positions.items()
        }

    def get_active_combat(self) -> Optional[Dict[str, Any]]:
        """Get active combat configuration"""
        return self.active_combat

    def list_bosses(self) -> List[Dict[str, Any]]:
        """List all available bosses"""
        return [
            {
                "name": boss.name,
                "company": boss.company,
                "net_worth": boss.net_worth,
                "difficulty": boss.difficulty,
                "ai_models": boss.ai_models,
                "special_abilities": boss.special_abilities
            }
            for boss in self.BOSS_FIGHTS
        ]

    def list_monsters(self) -> List[Dict[str, Any]]:
        """List all available monsters"""
        return [
            {
                "name": monster.name,
                "company": monster.company,
                "category": monster.category.value,
                "difficulty": monster.difficulty,
                "ai_models": monster.ai_models,
                "special_abilities": monster.special_abilities
            }
            for monster in self.MONSTER_ENCOUNTERS
        ]


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="VA Positioning & Combat System - ORDER 66: @DOIT")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--start-combat', choices=['ultron', 'acva', 'boss', 'monster'], help='Start 1v1 combat')
    parser.add_argument('--opponent-id', type=str, help='Specific opponent ID (boss or monster name)')
    parser.add_argument('--end-combat', action='store_true', help='End active combat')
    parser.add_argument('--list-bosses', action='store_true', help='List all bosses')
    parser.add_argument('--list-monsters', action='store_true', help='List all monsters')
    parser.add_argument('--positions', action='store_true', help='Show current positions')

    args = parser.parse_args()

    system = VAPositioningCombatSystem(project_root=args.project_root)

    if args.list_bosses:
        print("\n👑 BOSS FIGHTS (Top 5 Wealthiest Tech Billionaires):")
        print("="*80)
        for boss in system.list_bosses():
            print(f"\n  {boss['name']} ({boss['company']})")
            print(f"    Net Worth: ${boss['net_worth']:.1f}B")
            print(f"    Difficulty: {boss['difficulty']}/5")
            print(f"    AI Models: {', '.join(boss['ai_models'])}")
            print(f"    Abilities: {', '.join(boss['special_abilities'])}")
        return 0

    if args.list_monsters:
        print("\n👹 MONSTER ENCOUNTERS (AI Model Providers):")
        print("="*80)
        by_category = {}
        for monster in system.list_monsters():
            cat = monster['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(monster)

        for category, monsters in sorted(by_category.items()):
            print(f"\n  {category.upper()}:")
            for monster in monsters:
                print(f"    • {monster['name']} ({monster['company']}) - Difficulty: {monster['difficulty']}/10")
                print(f"      AI Models: {', '.join(monster['ai_models'])}")
        return 0

    if args.end_combat:
        result = system.end_combat()
        print(f"\n{'✅' if result['success'] else '❌'} {result.get('message', result.get('error', 'Unknown'))}")
        return 0 if result['success'] else 1

    if args.start_combat:
        opponent_type_map = {
            'ultron': OpponentType.ULTRON,
            'acva': OpponentType.ACVA,
            'boss': OpponentType.BOSS,
            'monster': OpponentType.MONSTER
        }
        result = system.start_1v1_combat(opponent_type_map[args.start_combat], args.opponent_id)
        if result.get('success'):
            print(f"\n✅ {result['message']}")
            combat = result['combat']
            print(f"\n  IMVA: ({combat['imva']['position']['x']}, {combat['imva']['position']['y']})")
            print(f"  {combat['opponent']['config']['name']}: ({combat['opponent']['position']['x']}, {combat['opponent']['position']['y']})")
            return 0
        else:
            print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
            return 1

    if args.positions:
        positions = system.get_positions()
        print("\n📍 Current VA Positions:")
        print("="*80)
        for va_id, pos in positions.items():
            status = "ACTIVE" if pos['is_active'] else "INACTIVE"
            print(f"\n  {va_id.upper()}: ({pos['x']}, {pos['y']}) - {status}")
            if pos['opponent_type']:
                print(f"    Opponent Type: {pos['opponent_type']}")
        return 0

    # Default: show status
    print("\n⚔️  VA Positioning & Combat System")
    print("="*80)
    active_combat = system.get_active_combat()
    if active_combat:
        print(f"\n✅ Active Combat: IMVA vs {active_combat['opponent']['config']['name']}")
        print(f"   Type: {active_combat['opponent']['type']}")
        print(f"   Started: {active_combat['started_at']}")
    else:
        print("\n❌ No active combat")

    positions = system.get_positions()
    if positions:
        print(f"\n📍 Active VAs: {len([p for p in positions.values() if p['is_active']])}")

    print("\n💡 Use --help for commands")
    return 0


if __name__ == "__main__":


    sys.exit(main())