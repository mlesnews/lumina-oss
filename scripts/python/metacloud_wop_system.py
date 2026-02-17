#!/usr/bin/env python3
"""
METACLOUD @WOP System

Metacloud of most popular short@tags, shorthand one-liners, single/multi-context tagging,
and AI chat language.

@WOP = Word(s) of Power / #POWERWORD(S)
Pronounced: "WHOPE|WIPE" (nod to wife's father, 2010, Eastern-Shore-Demarvaian dialect)

Inspired by "Wit" from Brandon Sanderson's Lightbringer:
- Collects dialects & slangs/words
- Forms custom characters based on "best-custom-tailorfit"
- General/common to unique/obscure outliers
- Situation/problem-based character formation

Tags: #metacloud #wop #powerwords #tags #dialect #wit #lightbringer #character_formation
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from collections import Counter, defaultdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("MetacloudWOPSystem")


class WOPCategory(Enum):
    """Word of Power categories"""
    GENERAL = "general"  # Common, general use
    UNIQUE = "unique"  # Unique to specific context
    OBSCURE = "obscure"  # Rare, obscure outliers
    DIALECT = "dialect"  # Regional dialect
    SLANG = "slang"  # Slang terminology
    TECHNICAL = "technical"  # Technical terminology


class ContextType(Enum):
    """Context types for tagging"""
    SINGLE = "single"  # Single context
    MULTI = "multi"  # Multi-context


@dataclass
class WordOfPower:
    """Word of Power (@WOP)"""
    wop_id: str
    word: str
    pronunciation: str  # "WHOPE|WIPE" format
    category: WOPCategory
    contexts: List[str] = field(default_factory=list)
    context_type: ContextType = ContextType.SINGLE
    usage_count: int = 0
    popularity_score: float = 0.0
    dialect_origin: Optional[str] = None  # Eastern-Shore-Demarvaian, etc.
    best_fit_situations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['category'] = self.category.value
        result['context_type'] = self.context_type.value
        result['created_at'] = self.created_at.isoformat()
        result['last_used'] = self.last_used.isoformat()
        return result


@dataclass
class ShortTag:
    """Short @tag"""
    tag_id: str
    tag: str  # e.g., "@WOP", "@REC", "@ASK"
    shorthand: str  # One-liner shorthand
    contexts: List[str] = field(default_factory=list)
    context_type: ContextType = ContextType.SINGLE
    usage_count: int = 0
    popularity_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['context_type'] = self.context_type.value
        result['created_at'] = self.created_at.isoformat()
        result['last_used'] = self.last_used.isoformat()
        return result


@dataclass
class CustomCharacter:
    """Custom character formed from @WOP collection (Wit-inspired)"""
    character_id: str
    name: str
    wops_used: List[str] = field(default_factory=list)  # Words of Power used
    dialects_collected: List[str] = field(default_factory=list)
    best_fit_situation: str = ""
    tailorfit_score: float = 0.0  # Best-custom-tailorfit score
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['created_at'] = result['created_at'].isoformat() if isinstance(result['created_at'], datetime) else result['created_at']
        return result


class MetacloudWOPSystem:
    """
    METACLOUD @WOP System

    Tracks popular @tags, @WOP (Words of Power), and forms custom characters
    based on best-fit to situations (Wit-inspired from Lightbringer)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize METACLOUD @WOP system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "metacloud_wop"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Words of Power
        self.wops: Dict[str, WordOfPower] = {}

        # Short @tags
        self.short_tags: Dict[str, ShortTag] = {}

        # Custom characters (Wit-inspired)
        self.characters: Dict[str, CustomCharacter] = {}

        # Dialect collection
        self.dialects_collected: Dict[str, List[str]] = defaultdict(list)

        # Initialize with common @WOP
        self._initialize_common_wops()
        self._initialize_common_tags()

        # Load saved data
        self._load_state()

        logger.info("=" * 80)
        logger.info("☁️  METACLOUD @WOP SYSTEM")
        logger.info("=" * 80)
        logger.info("   @WOP = Word(s) of Power / #POWERWORD(S)")
        logger.info("   Pronunciation: WHOPE|WIPE (Eastern-Shore-Demarvaian)")
        logger.info("   Inspired by: Wit from Brandon Sanderson's Lightbringer")
        logger.info("=" * 80)
        logger.info("")

    def _initialize_common_wops(self):
        """Initialize common Words of Power"""
        common_wops = [
            {
                "word": "WOP",
                "pronunciation": "WHOPE|WIPE",
                "category": WOPCategory.DIALECT,
                "dialect_origin": "Eastern-Shore-Demarvaian",
                "best_fit_situations": ["power_words", "tagging", "character_formation"],
                "contexts": ["tagging", "power", "language"]
            },
            {
                "word": "REC",
                "pronunciation": "REC",
                "category": WOPCategory.GENERAL,
                "best_fit_situations": ["recommendations", "suggestions", "advice"],
                "contexts": ["recommendation", "suggestion"]
            },
            {
                "word": "ASK",
                "pronunciation": "ASK",
                "category": WOPCategory.GENERAL,
                "best_fit_situations": ["requests", "questions", "tasks"],
                "contexts": ["request", "question", "task"]
            },
            {
                "word": "SLMM",
                "pronunciation": "SLI-M",
                "category": WOPCategory.TECHNICAL,
                "best_fit_situations": ["multimedia", "production", "sound_light_music_magic"],
                "contexts": ["multimedia", "production", "slmm"]
            },
            {
                "word": "LAFF",
                "pronunciation": "LAFF",
                "category": WOPCategory.GENERAL,
                "best_fit_situations": ["multimedia_studios", "production", "content"],
                "contexts": ["studio", "production", "multimedia"]
            }
        ]

        for wop_data in common_wops:
            wop_id = f"wop_{wop_data['word'].lower()}"
            wop = WordOfPower(
                wop_id=wop_id,
                word=wop_data['word'],
                pronunciation=wop_data['pronunciation'],
                category=wop_data['category'],
                contexts=wop_data.get('contexts', []),
                context_type=ContextType.MULTI if len(wop_data.get('contexts', [])) > 1 else ContextType.SINGLE,
                dialect_origin=wop_data.get('dialect_origin'),
                best_fit_situations=wop_data.get('best_fit_situations', [])
            )
            self.wops[wop_id] = wop

        logger.info(f"✅ Initialized {len(self.wops)} common @WOP")

    def _initialize_common_tags(self):
        """Initialize common short @tags"""
        common_tags = [
            {"tag": "@WOP", "shorthand": "Word(s) of Power"},
            {"tag": "@REC", "shorthand": "Recommendation"},
            {"tag": "@ASK", "shorthand": "Request/Question"},
            {"tag": "@SLMM", "shorthand": "Sound-Light-Music-Magic"},
            {"tag": "@LAFF", "shorthand": "Individual Multimedia Studios"},
            {"tag": "@ACS", "shorthand": "Agent Chat Session"},
            {"tag": "@SACS", "shorthand": "Subagent Chat Session"},
            {"tag": "@ALWAYS", "shorthand": "Always practice/policy"},
            {"tag": "@LIVE", "shorthand": "Real-time monitoring"},
            {"tag": "@HOLOCRONS", "shorthand": "History preservation"},
        ]

        for tag_data in common_tags:
            tag_id = tag_data['tag'].lower().replace('@', '')
            tag = ShortTag(
                tag_id=tag_id,
                tag=tag_data['tag'],
                shorthand=tag_data['shorthand'],
                contexts=[tag_data['shorthand'].lower()],
                context_type=ContextType.SINGLE
            )
            self.short_tags[tag_id] = tag

        logger.info(f"✅ Initialized {len(self.short_tags)} common @tags")

    def _load_state(self):
        """Load saved state"""
        state_file = self.data_dir / "metacloud_wop_state.json"

        if not state_file.exists():
            return

        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load WOPs
            for wid, wop_data in data.get('wops', {}).items():
                wop = WordOfPower(
                    wop_id=wop_data['wop_id'],
                    word=wop_data['word'],
                    pronunciation=wop_data['pronunciation'],
                    category=WOPCategory(wop_data['category']),
                    contexts=wop_data.get('contexts', []),
                    context_type=ContextType(wop_data.get('context_type', 'single')),
                    usage_count=wop_data.get('usage_count', 0),
                    popularity_score=wop_data.get('popularity_score', 0.0),
                    dialect_origin=wop_data.get('dialect_origin'),
                    best_fit_situations=wop_data.get('best_fit_situations', []),
                    created_at=datetime.fromisoformat(wop_data['created_at']),
                    last_used=datetime.fromisoformat(wop_data.get('last_used', wop_data['created_at']))
                )
                self.wops[wid] = wop

            # Load tags
            for tid, tag_data in data.get('short_tags', {}).items():
                tag = ShortTag(
                    tag_id=tag_data['tag_id'],
                    tag=tag_data['tag'],
                    shorthand=tag_data['shorthand'],
                    contexts=tag_data.get('contexts', []),
                    context_type=ContextType(tag_data.get('context_type', 'single')),
                    usage_count=tag_data.get('usage_count', 0),
                    popularity_score=tag_data.get('popularity_score', 0.0),
                    created_at=datetime.fromisoformat(tag_data['created_at']),
                    last_used=datetime.fromisoformat(tag_data.get('last_used', tag_data['created_at']))
                )
                self.short_tags[tid] = tag

            logger.info(f"📂 Loaded {len(self.wops)} @WOP and {len(self.short_tags)} @tags")
        except Exception as e:
            logger.debug(f"Could not load state: {e}")

    def register_wop(
        self,
        word: str,
        pronunciation: str,
        category: WOPCategory = WOPCategory.GENERAL,
        dialect_origin: Optional[str] = None,
        best_fit_situations: Optional[List[str]] = None
    ) -> WordOfPower:
        """Register a new Word of Power"""
        wop_id = f"wop_{word.lower()}"

        if wop_id in self.wops:
            # Update existing
            self.wops[wop_id].usage_count += 1
            self.wops[wop_id].last_used = datetime.now()
            logger.info(f"📝 Updated @WOP: {word} (usage: {self.wops[wop_id].usage_count})")
            return self.wops[wop_id]

        wop = WordOfPower(
            wop_id=wop_id,
            word=word,
            pronunciation=pronunciation,
            category=category,
            dialect_origin=dialect_origin,
            best_fit_situations=best_fit_situations or [],
            contexts=[word.lower()]
        )

        self.wops[wop_id] = wop

        # Track dialect if provided
        if dialect_origin:
            self.dialects_collected[dialect_origin].append(word)

        logger.info(f"✅ Registered @WOP: {word} ({pronunciation})")
        logger.info(f"   Category: {category.value}")
        if dialect_origin:
            logger.info(f"   Dialect: {dialect_origin}")

        return wop

    def register_tag(
        self,
        tag: str,
        shorthand: str,
        contexts: Optional[List[str]] = None
    ) -> ShortTag:
        """Register a new short @tag"""
        tag_id = tag.lower().replace('@', '')

        if tag_id in self.short_tags:
            # Update existing
            self.short_tags[tag_id].usage_count += 1
            self.short_tags[tag_id].last_used = datetime.now()
            logger.info(f"📝 Updated @tag: {tag} (usage: {self.short_tags[tag_id].usage_count})")
            return self.short_tags[tag_id]

        tag_obj = ShortTag(
            tag_id=tag_id,
            tag=tag,
            shorthand=shorthand,
            contexts=contexts or [shorthand.lower()],
            context_type=ContextType.MULTI if contexts and len(contexts) > 1 else ContextType.SINGLE
        )

        self.short_tags[tag_id] = tag_obj

        logger.info(f"✅ Registered @tag: {tag} ({shorthand})")

        return tag_obj

    def use_wop(self, word: str, situation: Optional[str] = None):
        """Use a Word of Power (increases usage count)"""
        wop_id = f"wop_{word.lower()}"

        if wop_id not in self.wops:
            logger.warning(f"⚠️  @WOP {word} not found, registering...")
            self.register_wop(word, word.upper(), WOPCategory.GENERAL)

        wop = self.wops[wop_id]
        wop.usage_count += 1
        wop.last_used = datetime.now()

        # Update popularity score
        wop.popularity_score = self._calculate_popularity_score(wop)

        # Track situation if provided
        if situation and situation not in wop.best_fit_situations:
            wop.best_fit_situations.append(situation)

        logger.info(f"💪 Used @WOP: {word} (total: {wop.usage_count})")

    def use_tag(self, tag: str):
        """Use a short @tag (increases usage count)"""
        tag_id = tag.lower().replace('@', '')

        if tag_id not in self.short_tags:
            logger.warning(f"⚠️  @tag {tag} not found, registering...")
            self.register_tag(tag, tag.replace('@', '').upper())

        tag_obj = self.short_tags[tag_id]
        tag_obj.usage_count += 1
        tag_obj.last_used = datetime.now()

        # Update popularity score
        tag_obj.popularity_score = self._calculate_popularity_score_tag(tag_obj)

        logger.info(f"🏷️  Used @tag: {tag} (total: {tag_obj.usage_count})")

    def _calculate_popularity_score(self, wop: WordOfPower) -> float:
        """Calculate popularity score for @WOP"""
        # Base score from usage count
        base_score = wop.usage_count * 10.0

        # Bonus for recent usage
        days_since_use = (datetime.now() - wop.last_used).days
        recency_bonus = max(0, 100 - days_since_use)

        # Bonus for multiple contexts
        context_bonus = len(wop.contexts) * 5.0

        # Bonus for dialect (unique/obscure)
        dialect_bonus = 20.0 if wop.dialect_origin else 0.0

        return base_score + recency_bonus + context_bonus + dialect_bonus

    def _calculate_popularity_score_tag(self, tag: ShortTag) -> float:
        """Calculate popularity score for @tag"""
        base_score = tag.usage_count * 10.0

        days_since_use = (datetime.now() - tag.last_used).days
        recency_bonus = max(0, 100 - days_since_use)

        context_bonus = len(tag.contexts) * 5.0

        return base_score + recency_bonus + context_bonus

    def form_custom_character(
        self,
        situation: str,
        problem: str,
        name: Optional[str] = None
    ) -> CustomCharacter:
        """
        Form custom character based on best-fit @WOP (Wit-inspired)

        Collects dialects/slangs/words and forms character based on
        "best-custom-tailorfit" to situation/problem
        """
        # Find best-fit @WOP for situation
        best_fit_wops = []

        for wop in self.wops.values():
            # Check if situation matches best_fit_situations
            situation_lower = situation.lower()
            problem_lower = problem.lower()

            match_score = 0.0

            # Check situation match
            for fit_situation in wop.best_fit_situations:
                if fit_situation.lower() in situation_lower or situation_lower in fit_situation.lower():
                    match_score += 10.0

            # Check problem match
            for context in wop.contexts:
                if context.lower() in problem_lower:
                    match_score += 5.0

            # Check word match
            if wop.word.lower() in problem_lower or wop.word.lower() in situation_lower:
                match_score += 15.0

            if match_score > 0:
                best_fit_wops.append((wop, match_score))

        # Sort by match score
        best_fit_wops.sort(key=lambda x: x[1], reverse=True)

        # Select top WOPs (general to unique/obscure)
        selected_wops = []
        dialects_used = set()

        # Start with general, move to unique/obscure
        for category_order in [WOPCategory.GENERAL, WOPCategory.TECHNICAL, WOPCategory.SLANG, 
                               WOPCategory.DIALECT, WOPCategory.UNIQUE, WOPCategory.OBSCURE]:
            for wop, score in best_fit_wops:
                if wop.category == category_order and wop not in [x[0] for x in selected_wops]:
                    selected_wops.append((wop, score))
                    if wop.dialect_origin:
                        dialects_used.add(wop.dialect_origin)
                    if len(selected_wops) >= 5:  # Limit to 5 WOPs
                        break
            if len(selected_wops) >= 5:
                break

        # Calculate tailorfit score
        total_score = sum(score for _, score in selected_wops)
        tailorfit_score = min(100.0, total_score / len(selected_wops) if selected_wops else 0.0)

        # Create character
        character_id = f"character_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        character_name = name or f"Character_{len(self.characters) + 1}"

        character = CustomCharacter(
            character_id=character_id,
            name=character_name,
            wops_used=[wop.word for wop, _ in selected_wops],
            dialects_collected=list(dialects_used),
            best_fit_situation=situation,
            tailorfit_score=tailorfit_score,
            description=f"Custom character formed from @WOP collection. Best-fit to situation: {situation}. Problem: {problem}. Uses {len(selected_wops)} Words of Power."
        )

        self.characters[character_id] = character

        logger.info("=" * 80)
        logger.info("🎭 CUSTOM CHARACTER FORMED (Wit-Inspired)")
        logger.info("=" * 80)
        logger.info(f"   Character: {character_name}")
        logger.info(f"   Situation: {situation}")
        logger.info(f"   Tailorfit Score: {tailorfit_score:.1f}/100")
        logger.info(f"   @WOP Used: {', '.join(character.wops_used)}")
        logger.info(f"   Dialects: {', '.join(character.dialects_collected) if character.dialects_collected else 'None'}")
        logger.info("=" * 80)
        logger.info("")

        return character

    def get_metacloud(self, limit: int = 50) -> Dict[str, Any]:
        """Get METACLOUD of most popular @tags and @WOP"""
        # Sort by popularity
        popular_wops = sorted(
            self.wops.values(),
            key=lambda w: w.popularity_score,
            reverse=True
        )[:limit]

        popular_tags = sorted(
            self.short_tags.values(),
            key=lambda t: t.popularity_score,
            reverse=True
        )[:limit]

        return {
            "metacloud_date": datetime.now().isoformat(),
            "words_of_power": {
                "total": len(self.wops),
                "popular": [w.to_dict() for w in popular_wops]
            },
            "short_tags": {
                "total": len(self.short_tags),
                "popular": [t.to_dict() for t in popular_tags]
            },
            "dialects_collected": {
                dialect: words
                for dialect, words in self.dialects_collected.items()
            },
            "custom_characters": {
                "total": len(self.characters),
                "recent": [c.to_dict() for c in list(self.characters.values())[-5:]]
            }
        }

    def save_state(self):
        try:
            """Save METACLOUD @WOP state"""
            state_file = self.data_dir / "metacloud_wop_state.json"

            state = {
                "wops": {wid: w.to_dict() for wid, w in self.wops.items()},
                "short_tags": {tid: t.to_dict() for tid, t in self.short_tags.items()},
                "characters": {cid: c.to_dict() for cid, c in self.characters.items()},
                "dialects_collected": dict(self.dialects_collected),
                "saved_at": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)

            logger.info(f"💾 METACLOUD @WOP state saved: {state_file}")


        except Exception as e:
            self.logger.error(f"Error in save_state: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="METACLOUD @WOP System")
    parser.add_argument('--register-wop', nargs=4, metavar=('WORD', 'PRONUNCIATION', 'CATEGORY', 'DIALECT'),
                       help='Register Word of Power')
    parser.add_argument('--register-tag', nargs=2, metavar=('TAG', 'SHORTHAND'),
                       help='Register short @tag')
    parser.add_argument('--use-wop', nargs=2, metavar=('WORD', 'SITUATION'),
                       help='Use @WOP')
    parser.add_argument('--use-tag', type=str, metavar='TAG', help='Use @tag')
    parser.add_argument('--form-character', nargs=2, metavar=('SITUATION', 'PROBLEM'),
                       help='Form custom character (Wit-inspired)')
    parser.add_argument('--metacloud', action='store_true', help='Show METACLOUD')
    parser.add_argument('--save', action='store_true', help='Save state')

    args = parser.parse_args()

    metacloud = MetacloudWOPSystem()

    if args.register_wop:
        word, pronunciation, category_str, dialect = args.register_wop
        category = WOPCategory(category_str.lower())
        dialect = dialect if dialect != "none" else None
        wop = metacloud.register_wop(word, pronunciation, category, dialect)
        print(f"\n✅ Registered @WOP: {wop.word} ({wop.pronunciation})")
        if args.save:
            metacloud.save_state()

    elif args.register_tag:
        tag, shorthand = args.register_tag
        tag_obj = metacloud.register_tag(tag, shorthand)
        print(f"\n✅ Registered @tag: {tag_obj.tag} ({tag_obj.shorthand})")
        if args.save:
            metacloud.save_state()

    elif args.use_wop:
        word, situation = args.use_wop
        metacloud.use_wop(word, situation)
        if args.save:
            metacloud.save_state()

    elif args.use_tag:
        metacloud.use_tag(args.use_tag)
        if args.save:
            metacloud.save_state()

    elif args.form_character:
        situation, problem = args.form_character
        character = metacloud.form_custom_character(situation, problem)
        print(f"\n✅ Formed character: {character.name}")
        print(f"   Tailorfit Score: {character.tailorfit_score:.1f}/100")
        print(f"   @WOP Used: {', '.join(character.wops_used)}")
        if args.save:
            metacloud.save_state()

    elif args.metacloud:
        cloud = metacloud.get_metacloud()
        print("\n" + "=" * 80)
        print("☁️  METACLOUD - MOST POPULAR @TAGS & @WOP")
        print("=" * 80)
        print(f"Total @WOP: {cloud['words_of_power']['total']}")
        print(f"Total @tags: {cloud['short_tags']['total']}")
        print("")
        print("Top @WOP:")
        for wop in cloud['words_of_power']['popular'][:10]:
            print(f"   {wop['word']} ({wop['pronunciation']}) - Score: {wop['popularity_score']:.1f}")
        print("")
        print("Top @tags:")
        for tag in cloud['short_tags']['popular'][:10]:
            print(f"   {tag['tag']} ({tag['shorthand']}) - Score: {tag['popularity_score']:.1f}")
        print("")
        print("Dialects Collected:")
        for dialect, words in cloud['dialects_collected'].items():
            print(f"   {dialect}: {len(words)} words")
        print("")
        print("=" * 80)
        print("")
        if args.save:
            metacloud.save_state()

    else:
        print("\n" + "=" * 80)
        print("☁️  METACLOUD @WOP SYSTEM")
        print("=" * 80)
        print("   @WOP = Word(s) of Power (WHOPE|WIPE)")
        print("   Inspired by: Wit from Brandon Sanderson's Lightbringer")
        print("")
        print("Use --register-wop to register Word of Power")
        print("Use --register-tag to register @tag")
        print("Use --use-wop to use @WOP")
        print("Use --form-character to form custom character")
        print("Use --metacloud to show METACLOUD")
        print("=" * 80)
        print("")

    if args.save:
        metacloud.save_state()


if __name__ == "__main__":


    main()