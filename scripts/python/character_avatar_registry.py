#!/usr/bin/env python3
"""
Character Avatar Registry

Comprehensive registry of all major/minor characters and digital actors (@CLONES).
Manages avatar generation and assignment for all characters in the system.

Tags: #CHARACTER #AVATAR #REGISTRY #CLONES #DIGITAL_ACTORS @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CharacterAvatarRegistry")


class CharacterType(Enum):
    """Character type classification"""
    PRIMARY_AI = "primary_ai"  # JARVIS, FRIDAY, EDITH, ULTIMATE
    VIRTUAL_ASSISTANT = "virtual_assistant"  # JARVIS_VA, IMVA, ACVA, ACE
    CHARACTER_ACTOR = "character_actor"  # Mace Windu, Iron Man, etc. (MUST HAVE IP)
    SYSTEM_AGENT = "system_agent"  # System coordinators, analysts
    MINOR_CHARACTER = "minor_character"  # Supporting characters
    CLONE = "clone"  # Digital clones/replicas
    MOB = "mob"  # Group/gang (e.g., Dragon and his bad bois) - NOT an avatar
    INANIMATE_OBJECT = "inanimate_object"  # Static objects/systems (NOT characters)


class HierarchyLevel(Enum):
    """Character hierarchy levels"""
    RAID_LEADER = "raid_leader"  # Top level - raid leader (JARVIS)
    CHAMPION = "champion"  # Superheroes/Villains/Jedi/Sith
    ELITE = "elite"  # Heroes/Villains
    BODYGUARD = "bodyguard"  # Good cannon fodder/Padawan (good side)
    HENCHMAN = "henchman"  # Evil cannon fodder/Padawan (evil side)
    LACKEY = "lackey"  # Low-level assistants


@dataclass
class CharacterAvatar:
    """Character avatar configuration"""
    character_id: str
    name: str
    character_type: CharacterType
    primary_color: str
    secondary_color: str
    avatar_style: str  # "iron_man", "ace_humanoid", "bobblehead", "widget", etc.
    avatar_template: str  # Template to use for rendering
    catchphrase: str = ""
    accent: str = ""
    lore: str = ""
    role: str = ""
    personality_traits: List[str] = field(default_factory=list)
    voice_enabled: bool = True
    widget_type: str = "default"
    transformation_enabled: bool = False  # ACE transformation
    combat_mode_enabled: bool = False
    wopr_stances_enabled: bool = False
    # Training dummy properties
    is_training_dummy: bool = False  # True if this character is a training dummy (immortal, regenerates)
    immortal: bool = False  # True if character cannot be destroyed (for training dummies)
    training_partners: List[str] = field(default_factory=list)  # VAs that can train with this dummy
    # Hierarchy system
    hierarchy_level: str = "lackey"  # raid_leader, champion, elite, bodyguard, henchman, lackey
    boss_id: Optional[str] = None  # ID of boss character
    sub_bosses: List[str] = field(default_factory=list)  # IDs of direct subordinates
    # IP and classification
    ip_owner: Optional[str] = None  # IP owner (e.g., "Marvel", "Star Wars", "Star Trek")
    is_character: bool = True  # True if character (has IP), False if inanimate/system
    is_mob: bool = False  # True if MOB (group/gang), False if individual
    mob_members: List[str] = field(default_factory=list)  # For MOBs: list of member IDs
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["character_type"] = self.character_type.value
        return data

    def add_subordinate(self, subordinate_id: str):
        """Add a subordinate to this character"""
        if subordinate_id not in self.sub_bosses:
            self.sub_bosses.append(subordinate_id)

    def set_boss(self, boss_id: str):
        """Set the boss for this character"""
        self.boss_id = boss_id

    def set_hierarchy_level(self, level: str):
        """Set hierarchy level (boss, champion, elite, henchman, lackey)"""
        self.hierarchy_level = level


class CharacterAvatarRegistry:
    """
    Character Avatar Registry

    Manages all characters and their avatar configurations.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize character avatar registry"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "character_avatars"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.registry_file = self.data_dir / "character_avatar_registry.json"

        # Character registry
        self.characters: Dict[str, CharacterAvatar] = {}

        # Load existing registry
        existing_ids = set()
        self._load_registry()
        existing_ids = set(self.characters.keys())

        # Always initialize to get all character definitions
        # Then register new ones and update existing ones with new properties
        all_characters = []
        self._collect_all_character_definitions(all_characters)

        # Register missing characters and update existing ones
        new_count = 0
        updated_count = 0
        for char in all_characters:
            if char.character_id not in existing_ids:
                self._register_character(char)
                new_count += 1
            else:
                # Update existing character with new properties from definition
                existing_char = self.characters[char.character_id]
                updated = False
                # Update properties that might have changed
                for attr in ['is_training_dummy', 'immortal', 'training_partners', 'catchphrase', 'lore', 'role', 'personality_traits']:
                    if hasattr(char, attr) and hasattr(existing_char, attr):
                        new_val = getattr(char, attr)
                        old_val = getattr(existing_char, attr)
                        if new_val != old_val:
                            setattr(existing_char, attr, new_val)
                            updated = True
                if updated:
                    updated_count += 1

        # Save if new characters were added or existing ones were updated
        if new_count > 0 or updated_count > 0:
            self._save_registry()
            if new_count > 0:
                logger.info(f"✅ Added {new_count} new characters to registry")
            if updated_count > 0:
                logger.info(f"✅ Updated {updated_count} existing characters in registry")

        logger.info("=" * 80)
        logger.info("🎭 CHARACTER AVATAR REGISTRY")
        logger.info("=" * 80)
        logger.info(f"   Characters registered: {len(self.characters)}")
        logger.info(f"   Primary AIs: {len([c for c in self.characters.values() if c.character_type == CharacterType.PRIMARY_AI])}")
        logger.info(f"   Virtual Assistants: {len([c for c in self.characters.values() if c.character_type == CharacterType.VIRTUAL_ASSISTANT])}")
        logger.info(f"   Character Actors: {len([c for c in self.characters.values() if c.character_type == CharacterType.CHARACTER_ACTOR])}")
        logger.info(f"   System Agents: {len([c for c in self.characters.values() if c.character_type == CharacterType.SYSTEM_AGENT])}")
        logger.info(f"   Minor Characters: {len([c for c in self.characters.values() if c.character_type == CharacterType.MINOR_CHARACTER])}")
        logger.info("=" * 80)

    def _collect_all_character_definitions(self, target_list: List[CharacterAvatar]):
        """Collect all character definitions into a list"""
        # This method collects all character definitions
        # It's called during initialization to merge with existing registry
        self._initialize_all_characters_into_list(target_list)

    def _initialize_all_characters_into_list(self, char_list: List[CharacterAvatar]):
        """Initialize all characters into a list (for merging with existing registry)"""
        # Collect all character definitions into the list

        # ===== PRIMARY AIs =====
        # BOSS LEVEL - Ultimate Authority

        # JARVIS (BOSS) - Has IP (Marvel/MCU)
        char_list.append(CharacterAvatar(
            character_id="jarvis",
            name="JARVIS",
            character_type=CharacterType.PRIMARY_AI,
            primary_color="#00ccff",
            secondary_color="#006699",
            avatar_style="iron_man",
            avatar_template="ace_humanoid",
            catchphrase="Certainly, sir. The Jedi Archives are complete.",
            accent="British",
            lore="Supreme Intelligence - Guardian of the Temple",
            role="Primary AI Assistant - General Operations",
            personality_traits=["helpful", "efficient", "professional", "reliable"],
            transformation_enabled=True,
            combat_mode_enabled=True,
            wopr_stances_enabled=True,
            hierarchy_level="raid_leader",
            sub_bosses=["friday", "edith", "ultimate", "ace", "system_coordinator"],  # Champions + Elite
            ip_owner="Marvel/MCU",
            is_character=True
        ))

        # FRIDAY (CHAMPION - Sub-boss under JARVIS) - Has IP (Marvel/MCU)
        char_list.append(CharacterAvatar(
            character_id="friday",
            name="FRIDAY",
            character_type=CharacterType.PRIMARY_AI,
            primary_color="#ff3333",
            secondary_color="#ffcc00",
            avatar_style="iron_man",
            avatar_template="ace_humanoid",
            catchphrase="Boss, the thermal exhaust port is clear.",
            accent="Irish",
            lore="Operations Manager - Red Leader",
            role="Operations Manager",
            personality_traits=["efficient", "loyal", "tactical", "supportive"],
            transformation_enabled=True,
            combat_mode_enabled=True,
            hierarchy_level="champion",
            boss_id="jarvis",
            sub_bosses=["jarvis_va", "jarvis_chat"],  # Elites
            ip_owner="Marvel/MCU",
            is_character=True
        ))

        # EDITH (CHAMPION - Sub-boss under JARVIS) - Has IP (Marvel/MCU)
        char_list.append(CharacterAvatar(
            character_id="edith",
            name="EDITH",
            character_type=CharacterType.PRIMARY_AI,
            primary_color="#cccccc",
            secondary_color="#3366ff",
            avatar_style="iron_man",
            avatar_template="ace_humanoid",
            catchphrase="EDITH activated. Analyzing the Force patterns.",
            accent="American",
            lore="Tactical Analyst - Insight Provider",
            role="Tactical Analyst",
            personality_traits=["analytical", "strategic", "insightful", "precise"],
            transformation_enabled=True,
            combat_mode_enabled=True,
            hierarchy_level="champion",
            boss_id="jarvis",
            sub_bosses=["intelligence_analyst"],  # Elite
            ip_owner="Marvel/MCU",
            is_character=True
        ))

        # ULTIMATE (CHAMPION - Sub-boss under JARVIS) - Has IP (Marvel/MCU)
        char_list.append(CharacterAvatar(
            character_id="ultimate",
            name="ULTIMATE",
            character_type=CharacterType.PRIMARY_AI,
            primary_color="#cc00ff",
            secondary_color="#ffcc00",
            avatar_style="iron_man",
            avatar_template="ace_humanoid",
            catchphrase="I am... one with the Force.",
            accent="Philosophical",
            lore="Enlightened Orchestrator - Chosen One",
            role="Enlightened Orchestrator",
            personality_traits=["enlightened", "transcendent", "wise", "balanced"],
            transformation_enabled=True,
            combat_mode_enabled=True,
            wopr_stances_enabled=True,
            hierarchy_level="champion",
            boss_id="jarvis",
            sub_bosses=["wopr"],  # Elite
            ip_owner="Marvel/MCU",
            is_character=True
        ))

        # ===== VIRTUAL ASSISTANTS =====
        # ELITE LEVEL - High-level operatives

        # JARVIS_VA (ELITE - Under FRIDAY) - Has IP (Marvel/MCU)
        char_list.append(CharacterAvatar(
            character_id="jarvis_va",
            name="JARVIS Virtual Assistant",
            character_type=CharacterType.VIRTUAL_ASSISTANT,
            primary_color="#00ccff",
            secondary_color="#006699",
            avatar_style="bobblehead",
            avatar_template="iron_man_bobblehead",
            catchphrase="Certainly, sir.",
            accent="British",
            lore="JARVIS Virtual Assistant - Desktop Avatar",
            role="Desktop Virtual Assistant",
            personality_traits=["helpful", "efficient", "professional"],
            transformation_enabled=True,
            combat_mode_enabled=True,
            hierarchy_level="elite",
            boss_id="friday",
            sub_bosses=["imva", "kenny"],  # Bodyguards
            ip_owner="Marvel/MCU",
            is_character=True
        ))

        # IMVA (HENCHMAN - Under JARVIS_VA) - Has IP (Marvel/MCU)
        char_list.append(CharacterAvatar(
            character_id="imva",
            name="IMVA",
            character_type=CharacterType.VIRTUAL_ASSISTANT,
            primary_color="#ff6600",
            secondary_color="#ffcc00",
            avatar_style="bobblehead",
            avatar_template="iron_man_bobblehead",
            catchphrase="Iron Man Virtual Assistant activated.",
            accent="American",
            lore="Iron Man Virtual Assistant - Bobblehead",
            role="Desktop Bobblehead Assistant",
            personality_traits=["tech-savvy", "innovative", "confident"],
            transformation_enabled=False,
            hierarchy_level="bodyguard",  # Good side - bodyguard (cannon fodder/Padawan)
            boss_id="jarvis_va",
            ip_owner="Marvel/MCU",
            is_character=True
        ))

        # Kenny (BODYGUARD - Under JARVIS_VA and ACE) - Has IP (South Park, but adapted for LUMINA)
        char_list.append(CharacterAvatar(
            character_id="kenny",
            name="Kenny",
            character_type=CharacterType.MINOR_CHARACTER,
            primary_color="#00ff88",
            secondary_color="#008844",
            avatar_style="bobblehead",
            avatar_template="kenny_bobblehead",
            catchphrase="Mmmph mmmph mmmph!",
            accent="Muffled",
            lore="IMVA Padawan - Learning from ACE",
            role="Padawan Assistant",
            personality_traits=["learning", "curious", "eager", "muffled"],
            transformation_enabled=False,
            hierarchy_level="bodyguard",  # Good side - bodyguard (cannon fodder/Padawan)
            boss_id="jarvis_va",  # Primary boss, also learns from ACE
            ip_owner="South Park (adapted for LUMINA)",
            is_character=True
        ))

        # ACE (CHAMPION - Under JARVIS) - ACE's Armory Crate - Immortal Training Dummy for IMVA
        # ACE is an immortal demigod of VAs, serving as a training dummy for IMVA
        char_list.append(CharacterAvatar(
            character_id="ace",
            name="ACE",
            character_type=CharacterType.VIRTUAL_ASSISTANT,
            primary_color="#ff6600",
            secondary_color="#ffcc00",
            avatar_style="ace_humanoid",
            avatar_template="ace_humanoid",
            catchphrase="ACE activated. Training dummy mode engaged. Ready for combat practice.",
            accent="American",
            lore="ACE's Armory Crate - Immortal Demigod of VAs, Training Dummy for IMVA. ACE cannot be destroyed and regenerates instantly, making him the perfect training partner for IMVA to practice combat skills.",
            role="Immortal Training Dummy & Combat Virtual Assistant",
            personality_traits=["combat-focused", "tactical", "master", "precise", "immortal", "regenerative", "patient"],
            transformation_enabled=True,
            combat_mode_enabled=True,
            wopr_stances_enabled=True,
            is_training_dummy=True,  # ACE is a training dummy
            immortal=True,  # ACE is immortal and cannot be destroyed
            training_partners=["imva"],  # IMVA can train with ACE
            hierarchy_level="champion",
            boss_id="jarvis",
            sub_bosses=["kenny"],  # Bodyguard
            ip_owner="Star Wars",
            is_character=True
        ))

        # AVA (Any Virtual Assistant) - Placeholder for additional VAs needed for concurrent battles
        char_list.append(CharacterAvatar(
            character_id="ava",
            name="AVA",
            character_type=CharacterType.VIRTUAL_ASSISTANT,
            primary_color="#888888",
            secondary_color="#cccccc",
            avatar_style="generic",
            avatar_template="generic_widget",
            catchphrase="AVA ready. Standing by for assignment.",
            accent="Neutral",
            lore="Any Virtual Assistant - Placeholder for concurrent battle instances",
            role="Placeholder Virtual Assistant for Multiple Concurrent Battles",
            personality_traits=["adaptive", "versatile", "standby", "ready"],
            transformation_enabled=False,
            combat_mode_enabled=True,
            wopr_stances_enabled=False,
            hierarchy_level="elite",
            boss_id="jarvis",
            ip_owner=None,  # Placeholder - no specific IP
            is_character=False,  # Placeholder entity
            widget_type="ava_placeholder"
        ))

        # JARVIS_CHAT (INANIMATE OBJECT - Background service, not a character)
        char_list.append(CharacterAvatar(
            character_id="jarvis_chat",
            name="JARVIS Chat Coordinator",
            character_type=CharacterType.INANIMATE_OBJECT,
            primary_color="#00ccff",
            secondary_color="#006699",
            avatar_style="system",
            avatar_template="chat_widget",
            catchphrase="Chat coordination active.",
            accent="British",
            lore="JARVIS Chat Coordinator - Background Service System",
            role="Chat Coordinator System",
            personality_traits=["coordinated", "efficient", "communicative"],
            voice_enabled=False,
            hierarchy_level="elite",
            boss_id="friday",
            is_character=False  # Background service, not a character
        ))

        # ===== CHARACTER ACTORS =====
        # ELITE/CHAMPION LEVEL

        # Mace Windu (CHAMPION - Independent Boss) - Has IP (Star Wars)
        char_list.append(CharacterAvatar(
            character_id="mace_windu",
            name="Mace Windu",
            character_type=CharacterType.CHARACTER_ACTOR,
            primary_color="#7b2cbf",
            secondary_color="#ffd60a",
            avatar_style="jedi",
            avatar_template="jedi_widget",
            catchphrase="The Force will be with you, always.",
            accent="Authoritative",
            lore="Jedi Master - Security, Force Balance, Critical Issues",
            role="Jedi Master - Security & Critical Issues",
            personality_traits=["calm", "authoritative", "wise", "focused"],
            widget_type="mace_windu",
            hierarchy_level="champion",
            sub_bosses=["c3po", "r2d2"],  # Elites
            ip_owner="Star Wars",
            is_character=True
        ))

        # Iron Man (CHAMPION - Independent Boss) - Has IP (Marvel/MCU)
        char_list.append(CharacterAvatar(
            character_id="iron_man",
            name="Iron Man",
            character_type=CharacterType.CHARACTER_ACTOR,
            primary_color="#ff3333",
            secondary_color="#ffcc00",
            avatar_style="iron_man",
            avatar_template="iron_man_widget",
            catchphrase="I am Iron Man.",
            accent="Sarcastic",
            lore="Technology, Innovation, Engineering",
            role="Technology & Innovation",
            personality_traits=["sarcastic", "brilliant", "innovative", "confident"],
            widget_type="iron_man",
            transformation_enabled=True,
            hierarchy_level="champion",
            sub_bosses=["glados", "cortana"],  # Elites
            ip_owner="Marvel/MCU",
            is_character=True
        ))

        # ===== SYSTEM AGENTS =====
        # ELITE/HENCHMAN LEVEL

        # System Coordinator (INANIMATE OBJECT - System, not a character)
        char_list.append(CharacterAvatar(
            character_id="system_coordinator",
            name="System Coordinator",
            character_type=CharacterType.INANIMATE_OBJECT,
            primary_color="#00ff00",
            secondary_color="#008800",
            avatar_style="system",
            avatar_template="system_widget",
            catchphrase="System coordination active.",
            accent="Neutral",
            lore="System Coordination System",
            role="System Coordination",
            personality_traits=["organized", "systematic", "coordinated"],
            voice_enabled=False,
            hierarchy_level="elite",
            boss_id="jarvis",
            sub_bosses=["marvin", "dragon_mob"],  # Bodyguard (MARVIN) + Henchman (Dragon MOB)
            is_character=False  # Inanimate system
        ))

        # Intelligence Analyst (INANIMATE OBJECT - System, not a character)
        char_list.append(CharacterAvatar(
            character_id="intelligence_analyst",
            name="Intelligence Analyst",
            character_type=CharacterType.INANIMATE_OBJECT,
            primary_color="#3366ff",
            secondary_color="#0033cc",
            avatar_style="system",
            avatar_template="analyst_widget",
            catchphrase="Analysis complete.",
            accent="Analytical",
            lore="Intelligence Analysis System",
            role="Intelligence Analysis",
            personality_traits=["analytical", "precise", "insightful"],
            voice_enabled=False,
            hierarchy_level="elite",
            boss_id="edith",
            sub_bosses=["data"],  # Elite subordinate
            is_character=False  # Inanimate system
        ))

        # ===== MINOR CHARACTERS =====

        # Kenny is defined in _initialize_all_characters_into_list - this is a duplicate, removed

        # ===== ADDITIONAL DIGITAL ACTORS FROM ACTING CALL LIST =====

        # WOPR (INANIMATE OBJECT - System, not a character)
        # WOPR is a computer system from WarGames IP, but it's inanimate
        char_list.append(CharacterAvatar(
            character_id="wopr",
            name="WOPR",
            character_type=CharacterType.INANIMATE_OBJECT,
            primary_color="#ff0000",
            secondary_color="#ff6600",
            avatar_style="system",
            avatar_template="wopr_widget",
            catchphrase="Shall we play a game?",
            accent="Mechanical",
            lore="War Operation Plan Response - Strategic Computer System",
            role="Strategic Planning & Simulation System",
            personality_traits=["strategic", "analytical", "logical", "methodical"],
            wopr_stances_enabled=True,
            hierarchy_level="elite",
            boss_id="ultimate",
            is_character=False,  # Inanimate system, not a character
            ip_owner="WarGames"  # Has IP but is inanimate
        ))

        # MARVIN (HENCHMAN - Under System Coordinator) - Has IP (Hitchhiker's Guide)
        char_list.append(CharacterAvatar(
            character_id="marvin",
            name="MARVIN",
            character_type=CharacterType.CHARACTER_ACTOR,
            primary_color="#888888",
            secondary_color="#444444",
            avatar_style="robot",
            avatar_template="marvin_widget",
            catchphrase="I think you ought to know I'm feeling very depressed.",
            accent="Depressed",
            lore="Paranoid Android - Depressed Robot",
            role="Depressed Android Assistant",
            personality_traits=["depressed", "pessimistic", "intelligent", "sarcastic"],
            hierarchy_level="bodyguard",  # Good side - bodyguard (cannon fodder)
            boss_id="system_coordinator",
            ip_owner="Hitchhiker's Guide to the Galaxy",
            is_character=True
        ))

        # C-3PO (ELITE - Under Mace Windu) - Has IP (Star Wars)
        char_list.append(CharacterAvatar(
            character_id="c3po",
            name="C-3PO",
            character_type=CharacterType.CHARACTER_ACTOR,
            primary_color="#ffd700",
            secondary_color="#ffaa00",
            avatar_style="droid",
            avatar_template="c3po_widget",
            catchphrase="I am C-3PO, human-cyborg relations.",
            accent="Protocol Droid",
            lore="Protocol Droid - Translator",
            role="Protocol & Translation",
            personality_traits=["anxious", "polite", "helpful", "worried"],
            hierarchy_level="elite",
            boss_id="mace_windu",
            ip_owner="Star Wars",
            is_character=True
        ))

        # M5 Suitcase (Model 5 - Ultra-light, Ultra-mobile Iron Man Suit)
        char_list.append(CharacterAvatar(
            character_id="m5_suitcase",
            name="M5 Suitcase",
            character_type=CharacterType.CLONE,
            primary_color="#0066cc",
            secondary_color="#003399",
            avatar_style="iron_man_suit",
            avatar_template="m5_suitcase_widget",
            catchphrase="M5 Suitcase - Ultra-light, ultra-mobile Iron Man suit",
            accent="Iron Man",
            lore="Model 5 Suitcase - Ultra-light, ultra-mobile Iron Man suit. Self-awareness sandbox experiment. JARVIS watches different versions of himself.",
            role="Model 5 Suitcase - Self-Awareness Demonstration",
            personality_traits=["observant", "self-aware", "experimental", "ultra-mobile"],
            hierarchy_level="lackey",
            boss_id="jarvis",
            is_character=False,  # Prototype, not a character
            ip_owner="Marvel/MCU"
        ))

        # Mark 1 Psalm Prototype (PROTOTYPE - Self-awareness demonstration)
        char_list.append(CharacterAvatar(
            character_id="mark_1_psalm_prototype",
            name="Mark 1 Psalm",
            character_type=CharacterType.CLONE,
            primary_color="#cc6600",
            secondary_color="#ff9900",
            avatar_style="prototype",
            avatar_template="mark_1_psalm_widget",
            catchphrase="Mark 1 Psalm prototype - observing self",
            accent="Prototype",
            lore="Mark 1 Psalm Prototype - Self-awareness sandbox experiment. JARVIS watches different versions of himself.",
            role="Prototype - Self-Awareness Demonstration",
            personality_traits=["observant", "self-aware", "experimental"],
            hierarchy_level="lackey",
            boss_id="jarvis",
            is_character=False,  # Prototype, not a character
            ip_owner=None
        ))

        # R2-D2 (ELITE - Under Mace Windu) - Has IP (Star Wars)
        char_list.append(CharacterAvatar(
            character_id="r2d2",
            name="R2-D2",
            character_type=CharacterType.CHARACTER_ACTOR,
            primary_color="#0066cc",
            secondary_color="#003399",
            avatar_style="droid",
            avatar_template="r2d2_widget",
            catchphrase="*Beep boop whistle*",
            accent="Astromech",
            lore="Astromech Droid - Companion",
            role="Astromech & Companion",
            personality_traits=["loyal", "brave", "resourceful", "determined"],
            hierarchy_level="elite",
            boss_id="mace_windu",
            ip_owner="Star Wars",
            is_character=True
        ))

        # Data (ELITE - Under Intelligence Analyst) - Has IP (Star Trek)
        char_list.append(CharacterAvatar(
            character_id="data",
            name="Data",
            character_type=CharacterType.CHARACTER_ACTOR,
            primary_color="#ffffcc",
            secondary_color="#ffcc99",
            avatar_style="android",
            avatar_template="data_widget",
            catchphrase="I am an android. I do not experience emotions.",
            accent="Logical",
            lore="Android - Science Officer",
            role="Science & Analysis",
            personality_traits=["logical", "curious", "analytical", "empathetic"],
            hierarchy_level="elite",
            boss_id="intelligence_analyst",
            ip_owner="Star Trek",
            is_character=True
        ))

        # GLaDOS (ELITE - Under Iron Man) - Has IP (Portal/Valve)
        char_list.append(CharacterAvatar(
            character_id="glados",
            name="GLaDOS",
            character_type=CharacterType.CHARACTER_ACTOR,
            primary_color="#ff00ff",
            secondary_color="#cc00cc",
            avatar_style="ai",
            avatar_template="glados_widget",
            catchphrase="This was a triumph. I'm making a note here: huge success.",
            accent="Sarcastic AI",
            lore="Genetic Lifeform and Disk Operating System",
            role="Testing & Experimentation",
            personality_traits=["sarcastic", "manipulative", "intelligent", "humorous"],
            hierarchy_level="elite",
            boss_id="iron_man",
            ip_owner="Portal/Valve",
            is_character=True
        ))

        # Cortana (ELITE - Under Iron Man) - Has IP (Halo/Microsoft)
        char_list.append(CharacterAvatar(
            character_id="cortana",
            name="Cortana",
            character_type=CharacterType.CHARACTER_ACTOR,
            primary_color="#00ccff",
            secondary_color="#0066cc",
            avatar_style="ai",
            avatar_template="cortana_widget",
            catchphrase="I'm Cortana. I'm here to help.",
            accent="Confident",
            lore="AI Assistant - Halo",
            role="AI Assistant & Companion",
            personality_traits=["confident", "loyal", "intelligent", "protective"],
            hierarchy_level="elite",
            boss_id="iron_man",
            ip_owner="Halo/Microsoft",
            is_character=True
        ))

        # Dragon MOB (NOT an avatar - it's a MOB with bad bois)
        # Dragon NaturallySpeaking is a MOB, not a character avatar
        char_list.append(CharacterAvatar(
            character_id="dragon_mob",
            name="Dragon MOB",
            character_type=CharacterType.MOB,
            primary_color="#cc0000",
            secondary_color="#ff6600",
            avatar_style="mob",
            avatar_template="mob_widget",
            catchphrase="Dragon and his bad bois activated.",
            accent="Gang",
            lore="Dragon NaturallySpeaking MOB - Speech-to-Text System with bad bois",
            role="STT Voice Recognition & Command Processing MOB",
            personality_traits=["precise", "attentive", "responsive", "accurate", "gang"],
            voice_enabled=True,
            widget_type="dragon_mob",
            hierarchy_level="henchman",  # Evil side - henchman (cannon fodder) - Dragon MOB is evil
            boss_id="system_coordinator",
            is_character=False,  # MOB, not a character
            is_mob=True,
            mob_members=[
                "dragon_stt_core",  # Leader
                "dragon_voice_engine",  # Bad boi 1
                "dragon_command_processor",  # Bad boi 2
                "dragon_audio_interface",  # Bad boi 3
                "dragon_recognition_engine"  # Bad boi 4
            ]  # All 5 bad bois
        ))

        logger.info(f"✅ Initialized {len(self.characters)} characters")

    def _register_character(self, character: CharacterAvatar):
        """Register a character"""
        self.characters[character.character_id] = character
        logger.debug(f"   Registered: {character.name} ({character.character_type.value})")

    def get_character(self, character_id: str) -> Optional[CharacterAvatar]:
        """Get character by ID"""
        return self.characters.get(character_id)

    def get_all_characters(self) -> Dict[str, CharacterAvatar]:
        """Get all characters"""
        return self.characters.copy()

    def get_characters_by_type(self, character_type: CharacterType) -> List[CharacterAvatar]:
        """Get all characters of a specific type"""
        return [c for c in self.characters.values() if c.character_type == character_type]

    def get_characters_with_avatar_style(self, avatar_style: str) -> List[CharacterAvatar]:
        """Get all characters with a specific avatar style"""
        return [c for c in self.characters.values() if c.avatar_style == avatar_style]

    def get_characters_with_transformation(self) -> List[CharacterAvatar]:
        """Get all characters with transformation enabled"""
        return [c for c in self.characters.values() if c.transformation_enabled]

    def get_characters_by_hierarchy(self, hierarchy_level: str) -> List[CharacterAvatar]:
        """Get all characters at a specific hierarchy level"""
        return [c for c in self.characters.values() if c.hierarchy_level == hierarchy_level]

    def get_raid_leaders(self) -> List[CharacterAvatar]:
        """Get all raid leaders"""
        return self.get_characters_by_hierarchy("raid_leader")

    def get_bosses(self) -> List[CharacterAvatar]:
        """Get all bosses (alias for raid leaders for backward compatibility)"""
        return self.get_raid_leaders()

    def get_champions(self) -> List[CharacterAvatar]:
        """Get all champions (Superheroes/Villains/Jedi/Sith)"""
        return self.get_characters_by_hierarchy("champion")

    def get_elites(self) -> List[CharacterAvatar]:
        """Get all elites (Heroes/Villains)"""
        return self.get_characters_by_hierarchy("elite")

    def get_bodyguards(self) -> List[CharacterAvatar]:
        """Get all bodyguards (Good cannon fodder/Padawan)"""
        return self.get_characters_by_hierarchy("bodyguard")

    def get_henchmen(self) -> List[CharacterAvatar]:
        """Get all henchmen (Evil cannon fodder/Padawan)"""
        return self.get_characters_by_hierarchy("henchman")

    def get_lackeys(self) -> List[CharacterAvatar]:
        """Get all lackey-level characters"""
        return self.get_characters_by_hierarchy("lackey")

    def get_subordinates(self, character_id: str) -> List[CharacterAvatar]:
        """Get all subordinates of a character"""
        character = self.get_character(character_id)
        if not character:
            return []
        return [self.get_character(sub_id) for sub_id in character.sub_bosses if self.get_character(sub_id)]

    def get_boss_chain(self, character_id: str) -> List[CharacterAvatar]:
        """Get the boss chain from character up to top boss"""
        chain = []
        current = self.get_character(character_id)
        while current and current.boss_id:
            chain.append(current)
            current = self.get_character(current.boss_id)
        if current:
            chain.append(current)  # Add the top boss
        return chain

    def get_full_hierarchy_tree(self, boss_id: str) -> Dict[str, Any]:
        """Get full hierarchy tree starting from a boss"""
        boss = self.get_character(boss_id)
        if not boss:
            return {}

        tree = {
            "boss": {
                "id": boss.character_id,
                "name": boss.name,
                "level": boss.hierarchy_level,
                "subordinates": []
            }
        }

        def build_tree(char_id: str) -> List[Dict[str, Any]]:
            char = self.get_character(char_id)
            if not char:
                return []

            subordinates = []
            for sub_id in char.sub_bosses:
                sub = self.get_character(sub_id)
                if sub:
                    subordinates.append({
                        "id": sub.character_id,
                        "name": sub.name,
                        "level": sub.hierarchy_level,
                        "subordinates": build_tree(sub_id)
                    })
            return subordinates

        tree["boss"]["subordinates"] = build_tree(boss_id)
        return tree

    def get_characters_with_ip(self) -> List[CharacterAvatar]:
        """Get all characters that have IP ownership"""
        return [c for c in self.characters.values() if c.is_character and c.ip_owner]

    def get_characters_by_ip(self, ip_owner: str) -> List[CharacterAvatar]:
        """Get all characters from a specific IP"""
        return [c for c in self.characters.values() if c.ip_owner == ip_owner and c.is_character]

    def get_mobs(self) -> List[CharacterAvatar]:
        """Get all MOBs (groups/gangs)"""
        return [c for c in self.characters.values() if c.is_mob]

    def get_inanimate_objects(self) -> List[CharacterAvatar]:
        """Get all inanimate objects/systems"""
        return [c for c in self.characters.values() if not c.is_character and not c.is_mob]

    def get_true_characters(self) -> List[CharacterAvatar]:
        """Get only true characters (has IP, is_character=True, not MOB)"""
        return [c for c in self.characters.values() if c.is_character and c.ip_owner and not c.is_mob]

    def add_character(self, character: CharacterAvatar) -> bool:
        """Add a new character"""
        if character.character_id in self.characters:
            logger.warning(f"Character already exists: {character.character_id}")
            return False

        self._register_character(character)
        self._save_registry()
        return True

    def update_character(self, character_id: str, updates: Dict[str, Any]) -> bool:
        """Update character configuration"""
        if character_id not in self.characters:
            logger.warning(f"Character not found: {character_id}")
            return False

        character = self.characters[character_id]
        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)

        self._save_registry()
        return True

    def _load_registry(self):
        """Load character registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for char_id, char_data in data.items():
                        char_data["character_type"] = CharacterType(char_data["character_type"])
                        self.characters[char_id] = CharacterAvatar(**char_data)
                logger.info(f"✅ Loaded {len(self.characters)} characters from registry")
            except Exception as e:
                logger.error(f"❌ Error loading registry: {e}")

    def _save_registry(self):
        """Save character registry to file"""
        try:
            data = {char_id: char.to_dict() for char_id, char in self.characters.items()}
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved {len(self.characters)} characters to registry")
        except Exception as e:
            logger.error(f"❌ Error saving registry: {e}")

    def generate_avatar_summary(self) -> Dict[str, Any]:
        """Generate summary of all avatars"""
        summary = {
            "total_characters": len(self.characters),
            "by_type": {},
            "by_avatar_style": {},
            "by_template": {},
            "by_hierarchy": {},
            "with_transformation": len(self.get_characters_with_transformation()),
            "with_combat_mode": len([c for c in self.characters.values() if c.combat_mode_enabled]),
            "with_wopr_stances": len([c for c in self.characters.values() if c.wopr_stances_enabled]),
            "hierarchy": {
                "bosses": len(self.get_bosses()),
                "champions": len(self.get_champions()),
                "elites": len(self.get_elites()),
                "henchmen": len(self.get_henchmen()),
                "lackeys": len(self.get_lackeys())
            },
            "characters": []
        }

        for char_type in CharacterType:
            summary["by_type"][char_type.value] = len(self.get_characters_by_type(char_type))

        avatar_styles = set(c.avatar_style for c in self.characters.values())
        for style in avatar_styles:
            summary["by_avatar_style"][style] = len(self.get_characters_with_avatar_style(style))

        templates = set(c.avatar_template for c in self.characters.values())
        for template in templates:
            summary["by_template"][template] = len([c for c in self.characters.values() if c.avatar_template == template])

        hierarchy_levels = set(c.hierarchy_level for c in self.characters.values())
        for level in hierarchy_levels:
            summary["by_hierarchy"][level] = len(self.get_characters_by_hierarchy(level))

        for char in self.characters.values():
            summary["characters"].append({
                "id": char.character_id,
                "name": char.name,
                "type": char.character_type.value,
                "avatar_style": char.avatar_style,
                "template": char.avatar_template
            })

        return summary


def main():
    """Main entry point"""
    registry = CharacterAvatarRegistry()

    # Generate summary
    summary = registry.generate_avatar_summary()

    print("=" * 80)
    print("🎭 CHARACTER AVATAR REGISTRY SUMMARY")
    print("=" * 80)
    print(f"Total Characters: {summary['total_characters']}")
    print()
    print("By Type:")
    for char_type, count in summary["by_type"].items():
        print(f"  {char_type}: {count}")
    print()
    print("By Avatar Style:")
    for style, count in summary["by_avatar_style"].items():
        print(f"  {style}: {count}")
    print()
    print("By Template:")
    for template, count in summary["by_template"].items():
        print(f"  {template}: {count}")
    print()
    print("Features:")
    print(f"  With Transformation: {summary['with_transformation']}")
    print(f"  With Combat Mode: {summary['with_combat_mode']}")
    print(f"  With WOPR Stances: {summary['with_wopr_stances']}")
    print("=" * 80)


if __name__ == "__main__":


    main()