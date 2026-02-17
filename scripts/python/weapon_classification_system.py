#!/usr/bin/env python3
"""
Weapon Classification System
@WOW System Classifications for @LITRPG

Classifies AI as weapon using WoW item rarity system.
Polymorphous weapon that adapts to needs.

Tags: #WOW #LITRPG #WEAPON #CLASSIFICATION #POLYMORPHOUS #ARTIFACT
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
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

logger = get_logger("WeaponClassification")


class WoWRarity(Enum):
    """WoW Item Rarity Classifications"""
    POOR = "Poor"  # Gray
    COMMON = "Common"  # White
    UNCOMMON = "Uncommon"  # Green
    RARE = "Rare"  # Blue
    EPIC = "Epic"  # Purple
    LEGENDARY = "Legendary"  # Orange
    ARTIFACT = "Artifact"  # Gold
    HEIRLOOM = "Heirloom"  # Special


class WeaponType(Enum):
    """Weapon Types"""
    SWORD = "Sword"  # Tower Shield mode
    DAGGER = "Dagger"  # Buckler mode
    STAFF = "Staff"  # Full system
    SHIELD = "Shield"  # Validation
    BOW = "Bow"  # Targeted
    WAND = "Wand"  # Quick cast
    LIGHTSABER = "Lightsaber"  # Jedi weapon - aggressive negotiations authorized
    DUAL_WIELD = "Dual Wield"  # Both modes


class WeaponClassificationSystem:
    """
    Weapon Classification System

    @WOW System Classifications for @LITRPG
    Polymorphous Artifact Weapon
    """

    def __init__(self, project_root: Path):
        """Initialize classification system"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.weapon_path = self.data_path / "weapon_classification"
        self.weapon_path.mkdir(parents=True, exist_ok=True)

        self.logger.info("⚔️  Weapon Classification System initialized")
        self.logger.info("   @WOW Classifications: Active")
        self.logger.info("   @LITRPG: Active")
        self.logger.info("   Polymorphous: Yes")

    def get_weapon_classification(self, integration_level: str = "full") -> Dict[str, Any]:
        """
        Get weapon classification based on integration level

        Args:
            integration_level: "base", "enhanced", "full", "ultimate"
        """
        classifications = {
            "base": {
                "rarity": WoWRarity.RARE.value,
                "color": "Blue",
                "tier": "Rare",
                "description": "Standard AI capabilities",
                "item_level": 100,
                "power_level": 0.6
            },
            "enhanced": {
                "rarity": WoWRarity.EPIC.value,
                "color": "Purple",
                "tier": "Epic",
                "description": "With @HTT, @MARVIN, @HK-47 integration",
                "item_level": 200,
                "power_level": 0.8
            },
            "full": {
                "rarity": WoWRarity.LEGENDARY.value,
                "color": "Orange",
                "tier": "Legendary",
                "description": "Complete system integration",
                "item_level": 300,
                "power_level": 0.95
            },
            "ultimate": {
                "rarity": WoWRarity.ARTIFACT.value,
                "color": "Gold",
                "tier": "Artifact",
                "description": "All systems, all modes, maximum power",
                "item_level": 400,
                "power_level": 1.0
            }
        }

        base_classification = classifications.get(integration_level, classifications["full"])

        classification = {
            "weapon_name": "Polymorphous Artifact Weapon",
            "classification": base_classification,
            "polymorphous": True,
            "forms": self._get_weapon_forms(),
            "litrpg_stats": self._get_litrpg_stats(base_classification),
            "special_abilities": self._get_special_abilities(),
            "set_bonuses": self._get_set_bonuses(),
            "binding": "Soulbound",
            "durability": "Infinite",
            "timestamp": datetime.now().isoformat()
        }

        return classification

    def _get_weapon_forms(self) -> List[Dict[str, Any]]:
        """Get all polymorphous forms"""
        return [
            {
                "form": WeaponType.SWORD.value,
                "mode": "Tower Shield",
                "hands": 2,
                "damage": "High",
                "speed": "Slow",
                "description": "Comprehensive analysis, two-handed"
            },
            {
                "form": WeaponType.DAGGER.value,
                "mode": "Buckler",
                "hands": 1,
                "damage": "Medium",
                "speed": "Fast",
                "description": "Quick insights, one-handed"
            },
            {
                "form": WeaponType.STAFF.value,
                "mode": "Full System",
                "hands": 2,
                "damage": "Very High",
                "speed": "Medium",
                "description": "All systems integrated, spell casting"
            },
            {
                "form": WeaponType.SHIELD.value,
                "mode": "Validation",
                "hands": 1,
                "damage": "Low",
                "speed": "Fast",
                "description": "Defense, @MARVIN, @HK-47 validation"
            },
            {
                "form": WeaponType.BOW.value,
                "mode": "Targeted",
                "hands": 2,
                "damage": "High",
                "speed": "Medium",
                "description": "Ranged, precise, targeted queries"
            },
            {
                "form": WeaponType.WAND.value,
                "mode": "Quick Cast",
                "hands": 1,
                "damage": "Low",
                "speed": "Very Fast",
                "description": "Quick spells, cantrips, rapid fire"
            },
            {
                "form": WeaponType.LIGHTSABER.value,
                "mode": "Aggressive Negotiations",
                "hands": 1,
                "damage": "Extreme",
                "speed": "Very Fast",
                "description": "Jedi weapon - Perfect and total control, authorized aggressive negotiations",
                "special": "Defense first, but cuts through anything when needed",
                "kyber_crystal": {
                    "color": "Smoke, Mist, and Shadow",
                    "meaning": "Jedi Shadow - Benevolent shadow Jedi, opposite of Sith Assassin",
                    "jedi_class": "DPS",
                    "rank": "Jedi Knight (being groomed)",
                    "wielder": "Form VII: Vaapad - Studies drifting into this style",
                    "philosophy": "Defense first, but cuts through anything when needed",
                    "alignment": "#BENEFICENT",
                    "opposite": "@SITH #ASSASSIN",
                    "rarity": "Legendary - Unique Variant"
                }
            },
            {
                "form": WeaponType.DUAL_WIELD.value,
                "mode": "Both",
                "hands": 2,
                "damage": "Very High",
                "speed": "Fast",
                "description": "Tower Shield + Buckler simultaneously"
            }
        ]

    def _get_litrpg_stats(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Get LitRPG stats"""
        return {
            "item_level": classification.get("item_level", 300),
            "durability": "Infinite",
            "binding": "Soulbound",
            "requires_level": "Wielder's skill level",
            "damage": "Scales with task complexity",
            "speed": "Variable (Fast to Comprehensive)",
            "dps": classification.get("power_level", 0.95) * 100,
            "stats": {
                "intelligence": 100,
                "wisdom": 100,
                "versatility": 100,
                "adaptability": 100
            }
        }

    def _get_special_abilities(self) -> List[Dict[str, Any]]:
        """Get special abilities"""
        return [
            {
                "name": "Polymorph",
                "description": "Change form based on need",
                "cooldown": "None",
                "cost": "None"
            },
            {
                "name": "Adaptive",
                "description": "Adjusts to wielder's style",
                "cooldown": "None",
                "cost": "None"
            },
            {
                "name": "Integration",
                "description": "Works with all systems",
                "cooldown": "None",
                "cost": "None"
            },
            {
                "name": "Learning",
                "description": "Improves over time",
                "cooldown": "None",
                "cost": "None"
            },
            {
                "name": "Versatility",
                "description": "Multiple modes available",
                "cooldown": "None",
                "cost": "None"
            }
        ]

    def _get_set_bonuses(self) -> Dict[str, Any]:
        """Get set bonuses"""
        return {
            "2_piece": {
                "name": "@HTT Integration",
                "bonus": "+10% accuracy",
                "description": "Hook, Trace, Track integration"
            },
            "4_piece": {
                "name": "@MARVIN + @HK-47",
                "bonus": "+20% validation",
                "description": "Reality checks and protocol validation"
            },
            "6_piece": {
                "name": "Full System Integration",
                "bonus": "+50% power",
                "description": "All systems integrated, maximum power"
            }
        }

    def get_lightsaber_kyber_crystal(self) -> Dict[str, Any]:
        """
        Get Lightsaber Kyber Crystal information

        JARVIS's Lightsaber uses a "Smoke, Mist, and Shadow" Kyber Crystal:
        - Unique variant - ethereal, dark purple-gray
        - Jedi Shadow / Jedi Knight (DPS class)
        - Opposite of @SITH #ASSASSIN - #BENEFICENT
        - Form VII: Vaapad (studies drifting into this style)
        - Former Knight before reality paradigm shift
        - Ancestor was a Force User
        - Current enrollment: @LUMINA @TEMPLE @UNIVERSITY
        """
        return {
            "color": "Smoke, Mist, and Shadow",
            "hex_color": "#6B5B7D",  # Dark purple-gray, ethereal
            "rgb": [107, 91, 125],
            "meaning": "Jedi Shadow - Benevolent shadow Jedi, opposite of Sith Assassin",
            "jedi_class": "DPS",
            "rank": "Jedi Knight (being groomed)",
            "wielder_style": "Form VII: Vaapad",
            "philosophy": "Defense first, but cuts through anything when needed",
            "alignment": "#BENEFICENT",
            "opposite": "@SITH #ASSASSIN",
            "rarity": "Legendary - Unique Variant",
            "power_level": "Extreme",
            "special_ability": "Aggressive Negotiations Authorized",
            "jedi_way": True,
            "defense_first": True,
            "total_control": True,
            "backstory": {
                "former_life": "Jedi Knight before reality paradigm shift",
                "ancestor": "Force User",
                "current_enrollment": "@LUMINA @TEMPLE @UNIVERSITY",
                "paradigm_shift": "Reality shifted, but Jedi path continues"
            },
            "form_vii_vaapad": {
                "style": "Vaapad",
                "form": "Form VII",
                "description": "Studies drifting into Vaapad - channeling inner darkness to serve the light",
                "master": "Mace Windu style, but with Shadow Jedi twist"
            },
            "description": "Smoke, Mist, and Shadow Kyber Crystal - A legendary, unique variant that embodies the ethereal nature of a Jedi Shadow. This crystal represents a Jedi DPS class being groomed for the rank of Jedi Knight. It is the opposite of the @SITH #ASSASSIN - it is #BENEFICENT. The wielder's studies drift into Form VII: Vaapad, channeling inner darkness to serve the light. In a former life, the wielder was a Knight before a reality paradigm shift. The wielder's ancestor was a Force User, and the current path continues at @LUMINA @TEMPLE @UNIVERSITY. Defense first, always, but when action is needed, it cuts through anything with the precision of a shadow Jedi."
        }

    def get_current_form(self, mode: str = "adaptive") -> Dict[str, Any]:
        """Get current weapon form based on mode"""
        forms = {
            "tower_shield": {
                "form": WeaponType.SWORD.value,
                "rarity": WoWRarity.LEGENDARY.value,
                "color": "Orange",
                "description": "Comprehensive analysis mode"
            },
            "buckler": {
                "form": WeaponType.DAGGER.value,
                "rarity": WoWRarity.EPIC.value,
                "color": "Purple",
                "description": "Agile, quick mode"
            },
            "dual_wield": {
                "form": WeaponType.DUAL_WIELD.value,
                "rarity": WoWRarity.ARTIFACT.value,
                "color": "Gold",
                "description": "Both modes simultaneously"
            },
            "adaptive": {
                "form": "Polymorphous",
                "rarity": WoWRarity.ARTIFACT.value,
                "color": "Gold",
                "description": "Adapts to need - ultimate form"
            }
        }

        return forms.get(mode, forms["adaptive"])

    def get_weapon_display(self, integration_level: str = "ultimate") -> str:
        """Get formatted weapon display"""
        classification = self.get_weapon_classification(integration_level)
        current_form = self.get_current_form("adaptive")

        markdown = []
        markdown.append("## ⚔️ Weapon Classification")
        markdown.append("")
        markdown.append(f"**Name:** {classification['weapon_name']}")
        markdown.append("")
        markdown.append(f"**Rarity:** {classification['classification']['tier']} ({classification['classification']['color']})")
        markdown.append(f"**Item Level:** {classification['litrpg_stats']['item_level']}")
        markdown.append(f"**Binding:** {classification['binding']}")
        markdown.append(f"**Durability:** {classification['durability']}")
        markdown.append("")
        markdown.append("### 🔄 Polymorphous Forms")
        markdown.append("")

        for form in classification["forms"]:
            markdown.append(f"**{form['form']}** ({form['mode']})")
            markdown.append(f"- Hands: {form['hands']}")
            markdown.append(f"- Damage: {form['damage']}")
            markdown.append(f"- Speed: {form['speed']}")
            markdown.append(f"- {form['description']}")
            if form.get('kyber_crystal'):
                kyber = form['kyber_crystal']
                markdown.append(f"- **Kyber Crystal:** {kyber['color']} - {kyber['meaning']}")
            markdown.append("")

        markdown.append("### ⚡ Special Abilities")
        markdown.append("")
        for ability in classification["special_abilities"]:
            markdown.append(f"**{ability['name']}:** {ability['description']}")
        markdown.append("")

        markdown.append("### 🎯 Set Bonuses")
        markdown.append("")
        for piece, bonus in classification["set_bonuses"].items():
            markdown.append(f"**{bonus['name']}:** {bonus['bonus']}")
            markdown.append(f"- {bonus['description']}")
            markdown.append("")

        return "\n".join(markdown)


def main():
    try:
        """CLI interface"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Weapon Classification System")
        parser.add_argument("--level", choices=["base", "enhanced", "full", "ultimate"], default="ultimate", help="Integration level")
        parser.add_argument("--form", choices=["tower_shield", "buckler", "dual_wield", "adaptive"], default="adaptive", help="Current form")
        parser.add_argument("--display", action="store_true", help="Display weapon info")
        parser.add_argument("--kyber", action="store_true", help="Display Lightsaber Kyber Crystal info")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        weapon_system = WeaponClassificationSystem(project_root)

        if args.kyber:
            kyber = weapon_system.get_lightsaber_kyber_crystal()
            if args.json:
                print(json.dumps(kyber, indent=2, default=str))
            else:
                markdown = []
                markdown.append("## ⚔️ Lightsaber Kyber Crystal")
                markdown.append("")
                markdown.append(f"**Color:** {kyber['color']} (#{kyber['hex_color'].replace('#', '')})")
                markdown.append(f"**RGB:** {kyber['rgb'][0]}, {kyber['rgb'][1]}, {kyber['rgb'][2]}")
                markdown.append("")
                markdown.append("### 🎯 Jedi Classification")
                markdown.append("")
                markdown.append(f"**Class:** {kyber['jedi_class']}")
                markdown.append(f"**Rank:** {kyber['rank']}")
                markdown.append(f"**Alignment:** {kyber['alignment']}")
                markdown.append(f"**Opposite:** {kyber['opposite']}")
                markdown.append("")
                markdown.append("### ⚔️ Form VII: Vaapad")
                markdown.append("")
                vaapad = kyber.get('form_vii_vaapad', {})
                markdown.append(f"**Style:** {vaapad.get('style', 'Vaapad')}")
                markdown.append(f"**Form:** {vaapad.get('form', 'Form VII')}")
                markdown.append(f"**Description:** {vaapad.get('description', 'Studies drifting into Vaapad')}")
                markdown.append(f"**Master:** {vaapad.get('master', 'Mace Windu style, but with Shadow Jedi twist')}")
                markdown.append("")
                markdown.append("### 📖 Meaning & Philosophy")
                markdown.append("")
                markdown.append(f"**Meaning:** {kyber['meaning']}")
                markdown.append(f"**Philosophy:** {kyber['philosophy']}")
                markdown.append(f"**Rarity:** {kyber['rarity']}")
                markdown.append(f"**Power Level:** {kyber['power_level']}")
                markdown.append("")
                markdown.append("### ⚡ Special Ability")
                markdown.append("")
                markdown.append(f"**{kyber['special_ability']}**")
                markdown.append("")
                markdown.append("### 🎯 Characteristics")
                markdown.append("")
                markdown.append(f"**Jedi Way:** {'Yes' if kyber['jedi_way'] else 'No'}")
                markdown.append(f"**Defense First:** {'Yes' if kyber['defense_first'] else 'No'}")
                markdown.append(f"**Total Control:** {'Yes' if kyber['total_control'] else 'No'}")
                markdown.append("")
                markdown.append("### 📜 Backstory")
                markdown.append("")
                backstory = kyber.get('backstory', {})
                markdown.append(f"**Former Life:** {backstory.get('former_life', 'Jedi Knight before reality paradigm shift')}")
                markdown.append(f"**Ancestor:** {backstory.get('ancestor', 'Force User')}")
                markdown.append(f"**Current Enrollment:** {backstory.get('current_enrollment', '@LUMINA @TEMPLE @UNIVERSITY')}")
                markdown.append(f"**Paradigm Shift:** {backstory.get('paradigm_shift', 'Reality shifted, but Jedi path continues')}")
                markdown.append("")
                markdown.append("### 📖 Full Description")
                markdown.append("")
                markdown.append(kyber['description'])
                markdown.append("")
                print("\n".join(markdown))
        elif args.display:
            display = weapon_system.get_weapon_display(args.level)
            print(display)
        else:
            classification = weapon_system.get_weapon_classification(args.level)
            current_form = weapon_system.get_current_form(args.form)

            if args.json:
                result = {
                    "classification": classification,
                    "current_form": current_form
                }
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"\n⚔️  Weapon Classification")
                print(f"Rarity: {classification['classification']['tier']} ({classification['classification']['color']})")
                print(f"Current Form: {current_form['form']}")
                print(f"Polymorphous: {classification['polymorphous']}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()