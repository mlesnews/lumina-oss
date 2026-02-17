#!/usr/bin/env python3
"""
Iron Man Suit System

JARVIS can spawn random Iron Man suits (Mark 5, 6, 7, etc.)
- Mark 5: Suitcase suit (collapses into briefcase)
- Random suit selection
- Transformation animations
- Tony Stark can step out (or empty suit)
- One-to-one correlations between comics and movies

Tags: #IRON_MAN #SUIT #MARK5 #SUITCASE #COMICS #MOVIES #JARVIS @JARVIS @LUMINA
"""

import sys
import random
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IronManSuitSystem")


class SuitMark(Enum):
    """Iron Man suit marks"""
    MARK_1 = "mark_1"  # Original cave suit
    MARK_2 = "mark_2"  # First flight suit
    MARK_3 = "mark_3"  # Red and gold classic
    MARK_4 = "mark_4"  # Refined version
    MARK_5 = "mark_5"  # Suitcase suit (Iron Man 2)
    MARK_6 = "mark_6"  # New element suit
    MARK_7 = "mark_7"  # Autonomous suit
    MARK_42 = "mark_42"  # Autonomous prehensile
    MARK_43 = "mark_43"  # Age of Ultron
    MARK_44 = "mark_44"  # Hulkbuster
    MARK_45 = "mark_45"  # Age of Ultron final
    MARK_46 = "mark_46"  # Civil War
    MARK_47 = "mark_47"  # Homecoming
    MARK_50 = "mark_50"  # Bleeding Edge (Infinity War)
    MARK_85 = "mark_85"  # Endgame final suit


class SuitState(Enum):
    """Suit state"""
    SUITCASE = "suitcase"  # Collapsed into briefcase (Mark 5)
    EXPANDING = "expanding"  # Transforming from suitcase
    ACTIVE = "active"  # Fully deployed
    COLLAPSING = "collapsing"  # Transforming to suitcase
    EMPTY = "empty"  # No one inside
    OCCUPIED = "occupied"  # Tony inside (or other)


@dataclass
class SuitSpecs:
    """Specifications for a suit mark"""
    mark: SuitMark
    name: str
    color_primary: str
    color_secondary: str
    color_arc: str
    has_suitcase_mode: bool
    comic_appearance: str  # First comic appearance
    movie_appearance: str  # Movie appearance
    special_features: List[str]
    transformation_time: float  # Seconds to transform


class IronManSuitSystem:
    """
    Iron Man Suit System

    Manages spawning, transformation, and rendering of Iron Man suits.
    Supports Mark 5 suitcase mode and random suit selection.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize suit system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger

        # Suit database
        self.suit_specs = self._load_suit_specs()

        # Active suits
        self.active_suits: Dict[str, Dict] = {}  # suit_id -> suit_data

        # Comic-to-movie correlations
        self.comic_movie_correlations = self._load_comic_movie_correlations()

        logger.info("=" * 80)
        logger.info("🦾 IRON MAN SUIT SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   Suits available: {len(self.suit_specs)}")
        logger.info("   Features: Random spawning, Mark 5 suitcase mode, transformations")
        logger.info("=" * 80)

    def _load_suit_specs(self) -> Dict[SuitMark, SuitSpecs]:
        """Load suit specifications"""
        specs = {
            SuitMark.MARK_5: SuitSpecs(
                mark=SuitMark.MARK_5,
                name="Mark V (Suitcase Suit)",
                color_primary="#B22222",  # Hot Rod Red
                color_secondary="#FFD700",  # Gold
                color_arc="#00FFFF",  # Cyan
                has_suitcase_mode=True,
                comic_appearance="Tales of Suspense #39 (1963)",
                movie_appearance="Iron Man 2 (2010)",
                special_features=["Suitcase transformation", "Portable", "Quick deploy"],
                transformation_time=2.0
            ),
            SuitMark.MARK_6: SuitSpecs(
                mark=SuitMark.MARK_6,
                name="Mark VI (New Element)",
                color_primary="#B22222",
                color_secondary="#FFD700",
                color_arc="#00FFFF",
                has_suitcase_mode=False,
                comic_appearance="Tales of Suspense #40 (1963)",
                movie_appearance="Iron Man 2 (2010)",
                special_features=["New element arc reactor", "Improved power"],
                transformation_time=3.0
            ),
            SuitMark.MARK_7: SuitSpecs(
                mark=SuitMark.MARK_7,
                name="Mark VII (Autonomous)",
                color_primary="#B22222",
                color_secondary="#FFD700",
                color_arc="#00FFFF",
                has_suitcase_mode=False,
                comic_appearance="Iron Man #55 (1973)",
                movie_appearance="The Avengers (2012)",
                special_features=["Autonomous deployment", "Flight capable"],
                transformation_time=2.5
            ),
            SuitMark.MARK_42: SuitSpecs(
                mark=SuitMark.MARK_42,
                name="Mark XLII (Prehensile)",
                color_primary="#B22222",
                color_secondary="#FFD700",
                color_arc="#00FFFF",
                has_suitcase_mode=False,
                comic_appearance="Iron Man #200 (1985)",
                movie_appearance="Iron Man 3 (2013)",
                special_features=["Autonomous pieces", "Remote control"],
                transformation_time=4.0
            ),
            SuitMark.MARK_50: SuitSpecs(
                mark=SuitMark.MARK_50,
                name="Mark L (Bleeding Edge)",
                color_primary="#B22222",
                color_secondary="#FFD700",
                color_arc="#00FFFF",
                has_suitcase_mode=False,
                comic_appearance="Invincible Iron Man #1 (2008)",
                movie_appearance="Avengers: Infinity War (2018)",
                special_features=["Nanotech", "Shape-shifting"],
                transformation_time=1.5
            ),
            SuitMark.MARK_85: SuitSpecs(
                mark=SuitMark.MARK_85,
                name="Mark LXXXV (Endgame)",
                color_primary="#B22222",
                color_secondary="#FFD700",
                color_arc="#00FFFF",
                has_suitcase_mode=False,
                comic_appearance="Iron Man #200 (1985)",
                movie_appearance="Avengers: Endgame (2019)",
                special_features=["Final suit", "Nanotech", "Quantum suit"],
                transformation_time=2.0
            ),
        }
        return specs

    def _load_comic_movie_correlations(self) -> Dict[str, Dict]:
        """Load one-to-one correlations between comics and movies"""
        correlations = {
            "mark_5": {
                "comic": {
                    "first_appearance": "Tales of Suspense #39 (1963)",
                    "key_storylines": [
                        "Original Iron Man origin",
                        "Suitcase suit concept introduced",
                        "Portable armor technology"
                    ],
                    "artists": ["Don Heck", "Jack Kirby"],
                    "writers": ["Stan Lee", "Larry Lieber"]
                },
                "movie": {
                    "film": "Iron Man 2 (2010)",
                    "director": "Jon Favreau",
                    "key_scenes": [
                        "Monaco Grand Prix suitcase deployment",
                        "Tony's portable armor reveal",
                        "Quick transformation sequence"
                    ],
                    "visual_design": "Based on comic Mark 5 with movie enhancements"
                },
                "correlations": {
                    "suitcase_concept": "Both feature portable briefcase suit",
                    "transformation": "Both show quick deployment",
                    "color_scheme": "Red and gold maintained",
                    "portability": "Core feature in both"
                }
            },
            "mark_6": {
                "comic": {
                    "first_appearance": "Tales of Suspense #40 (1963)",
                    "key_storylines": [
                        "New element arc reactor",
                        "Improved power systems"
                    ]
                },
                "movie": {
                    "film": "Iron Man 2 (2010)",
                    "key_scenes": [
                        "New element creation",
                        "Improved suit capabilities"
                    ]
                },
                "correlations": {
                    "new_element": "Both feature improved power source",
                    "evolution": "Represents suit evolution"
                }
            }
        }
        return correlations

    def spawn_random_suit(self, position: Tuple[float, float]) -> str:
        """Spawn a random Iron Man suit"""
        # Weighted random selection (Mark 5 more common for suitcase mode)
        suit_marks = list(self.suit_specs.keys())
        weights = [2.0 if mark == SuitMark.MARK_5 else 1.0 for mark in suit_marks]

        selected_mark = random.choices(suit_marks, weights=weights)[0]
        suit_spec = self.suit_specs[selected_mark]

        suit_id = f"suit_{selected_mark.value}_{random.randint(1000, 9999)}"

        # Determine if Tony is inside (or empty)
        has_tony = random.choice([True, False])

        suit_data = {
            "suit_id": suit_id,
            "mark": selected_mark,
            "specs": suit_spec,
            "state": SuitState.SUITCASE if suit_spec.has_suitcase_mode else SuitState.ACTIVE,
            "transformation_progress": 0.0 if suit_spec.has_suitcase_mode else 1.0,
            "position": position,
            "has_tony": has_tony,
            "tony_visible": False,  # Tony steps out after expansion
            "spawn_time": None
        }

        self.active_suits[suit_id] = suit_data

        self.logger.info(f"🦾 Spawned {suit_spec.name} at {position}")
        self.logger.info(f"   State: {suit_data['state'].value}")
        self.logger.info(f"   Has Tony: {has_tony}")

        return suit_id

    def toggle_suit_transformation(self, suit_id: str) -> bool:
        """Toggle suit transformation (suitcase ↔ active)"""
        if suit_id not in self.active_suits:
            return False

        suit = self.active_suits[suit_id]
        if not suit["specs"].has_suitcase_mode:
            return False  # This suit doesn't have suitcase mode

        if suit["state"] == SuitState.SUITCASE:
            # Expand
            suit["state"] = SuitState.EXPANDING
            suit["transformation_progress"] = 0.0
            self.logger.info(f"🚀 Expanding {suit['specs'].name}...")
        elif suit["state"] == SuitState.ACTIVE:
            # Collapse
            suit["state"] = SuitState.COLLAPSING
            suit["transformation_progress"] = 1.0
            self.logger.info(f"💼 Collapsing {suit['specs'].name}...")

        return True

    def update_suit_animation(self, suit_id: str, delta_time: float):
        """Update suit transformation animation"""
        if suit_id not in self.active_suits:
            return

        suit = self.active_suits[suit_id]
        specs = suit["specs"]

        if suit["state"] == SuitState.EXPANDING:
            suit["transformation_progress"] += delta_time / specs.transformation_time
            if suit["transformation_progress"] >= 1.0:
                suit["transformation_progress"] = 1.0
                suit["state"] = SuitState.ACTIVE
                # Tony can step out after expansion
                if suit["has_tony"] and random.random() > 0.5:
                    suit["tony_visible"] = True
                    self.logger.info(f"👤 Tony Stark steps out of {specs.name}")

        elif suit["state"] == SuitState.COLLAPSING:
            suit["transformation_progress"] -= delta_time / specs.transformation_time
            if suit["transformation_progress"] <= 0.0:
                suit["transformation_progress"] = 0.0
                suit["state"] = SuitState.SUITCASE
                suit["tony_visible"] = False

        # Update Tony visibility
        if suit["state"] == SuitState.ACTIVE and suit["has_tony"]:
            # Tony might step out or stay in
            pass

    def get_suit_render_data(self, suit_id: str) -> Optional[Dict]:
        """Get rendering data for a suit"""
        if suit_id not in self.active_suits:
            return None

        suit = self.active_suits[suit_id]
        return {
            "mark": suit["mark"],
            "specs": suit["specs"],
            "state": suit["state"],
            "transformation_progress": suit["transformation_progress"],
            "position": suit["position"],
            "has_tony": suit["has_tony"],
            "tony_visible": suit["tony_visible"]
        }

    def get_comic_movie_correlation(self, mark: SuitMark) -> Optional[Dict]:
        """Get comic-to-movie correlation for a suit mark"""
        mark_key = mark.value
        return self.comic_movie_correlations.get(mark_key)


def get_iron_man_suit_system(project_root: Optional[Path] = None) -> IronManSuitSystem:
    """Get global Iron Man suit system instance"""
    global _iron_man_suit_system
    if '_iron_man_suit_system' not in globals():
        _iron_man_suit_system = IronManSuitSystem(project_root)
    return _iron_man_suit_system


if __name__ == "__main__":
    system = IronManSuitSystem()
    print("\n🦾 Iron Man Suit System Test")
    print("=" * 80)

    # Spawn a random suit
    suit_id = system.spawn_random_suit((100, 100))
    print(f"\n✅ Spawned suit: {suit_id}")

    # Get correlation
    suit = system.active_suits[suit_id]
    correlation = system.get_comic_movie_correlation(suit["mark"])
    if correlation:
        print(f"\n📚 Comic-Movie Correlation:")
        print(f"   Comic: {correlation['comic']['first_appearance']}")
        print(f"   Movie: {correlation['movie']['film']}")
