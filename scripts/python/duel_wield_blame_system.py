#!/usr/bin/env python3
"""
Dual Wield Blame System
Tower Shield + Buckler - Use Both Simultaneously

D&D Analytics: Dual wielding shields/weapons
One-handed + Two-handed combinations
Spells & Casters integration

Tags: #DUAL-WIELD #TOWER-SHIELD #BUCKLER #D&D #ANALYTICS
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from enhanced_github_blame_htt import EnhancedGitHubBlameHTT
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    EnhancedGitHubBlameHTT = None

logger = get_logger("DualWieldBlame")


class DualWieldBlameSystem:
    """
    Dual Wield Blame System

    D&D Analytics:
    - Tower Shield (two-handed) = Comprehensive, powerful
    - Buckler (one-handed) = Agile, quick
    - Dual Wield = Both simultaneously

    Spells & Casters:
    - Cantrips = Quick checks (Buckler)
    - High-level spells = Comprehensive analysis (Tower Shield)
    - Multiple spells = Dual wield
    """

    def __init__(self, project_root: Path):
        """Initialize dual wield system"""
        self.project_root = project_root
        self.logger = logger

        if EnhancedGitHubBlameHTT:
            self.blame_system = EnhancedGitHubBlameHTT(project_root)
        else:
            self.blame_system = None
            self.logger.warning("⚠️  EnhancedGitHubBlameHTT not available")

        self.logger.info("⚔️  Dual Wield Blame System initialized")
        self.logger.info("   Tower Shield: Ready (two-handed)")
        self.logger.info("   Buckler: Ready (one-handed)")
        self.logger.info("   Dual Wield: Ready (both)")

    def dual_wield_blame(self, file_path: str, line_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Dual Wield: Use both Tower Shield and Buckler simultaneously

        D&D: Dual wielding weapons for maximum versatility
        """
        if not self.blame_system:
            return {"error": "Blame system not available"}

        self.logger.info("⚔️  Dual Wielding: Tower Shield + Buckler")

        result = {
            "mode": "dual_wield",
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "line_number": line_number,
            "tower_shield": {},
            "buckler": {},
            "combined_insights": {}
        }

        # Tower Shield (comprehensive)
        if line_number:
            result["tower_shield"] = self.blame_system.get_enhanced_blame(file_path, line_number)
        else:
            result["tower_shield"] = self.blame_system.get_tower_shield_blame(file_path)

        # Buckler (agile)
        if line_number:
            result["buckler"] = self.blame_system.get_buckler_blame(file_path, line_number)

        # Combined insights
        result["combined_insights"] = self._combine_insights(result["tower_shield"], result["buckler"])

        return result

    def _combine_insights(self, tower_shield: Dict[str, Any], buckler: Dict[str, Any]) -> Dict[str, Any]:
        """Combine insights from both modes"""
        combined = {
            "agility": buckler.get("mode") == "buckler",
            "comprehensiveness": tower_shield.get("mode") == "tower_shield" or "enhanced_blame" in tower_shield,
            "versatility": "dual_wield",
            "recommendation": self._get_recommendation(tower_shield, buckler)
        }

        # Extract key insights
        if "author" in buckler:
            combined["quick_author"] = buckler["author"]

        if "authors" in tower_shield:
            combined["all_authors"] = tower_shield["authors"]

        if "character_stats" in tower_shield:
            combined["character_stats"] = tower_shield["character_stats"]

        return combined

    def _get_recommendation(self, tower_shield: Dict[str, Any], buckler: Dict[str, Any]) -> str:
        """Get recommendation based on both modes"""
        if "error" in tower_shield or "error" in buckler:
            return "Use Buckler for quick checks when Tower Shield unavailable"

        if buckler.get("mode") == "buckler" and "enhanced_blame" in tower_shield:
            return "Dual Wield: Quick insights (Buckler) + Comprehensive analysis (Tower Shield)"

        return "Both modes available - choose based on need"

    def get_dnd_analytics(self, file_path: str) -> Dict[str, Any]:
        """
        D&D Analytics for code blame

        Character stats as D&D attributes
        """
        if not self.blame_system:
            return {"error": "Blame system not available"}

        enhanced = self.blame_system.get_enhanced_blame(file_path)

        dnd_stats = {
            "file": file_path,
            "character_sheet": {},
            "weapon_proficiencies": {
                "tower_shield": "Proficient",
                "buckler": "Proficient",
                "dual_wield": "Proficient"
            },
            "spell_slots": {
                "cantrips": "Unlimited (Buckler mode)",
                "level_1_3": "Standard blame",
                "level_4_6": "Tower Shield mode",
                "level_7_9": "Full system integration"
            }
        }

        # Convert character stats to D&D attributes
        for author, stats in enhanced.get("character_stats", {}).items():
            dnd_stats["character_sheet"][author] = {
                "strength": stats.get("performance", {}).get("score", 0.5) * 20,  # 0-20 scale
                "dexterity": (1.0 - stats.get("consistency", {}).get("score", 0.5)) * 20,  # Inverse for agility
                "intelligence": stats.get("intent", {}).get("score", 0.5) * 20,
                "wisdom": stats.get("reputation", {}).get("score", 0.5) * 20,
                "constitution": 10,  # Base system resilience
                "charisma": 10,  # Professional communication
                "class": self._determine_class(stats),
                "alignment": self._determine_alignment(stats)
            }

        return dnd_stats

    def _determine_class(self, stats: Dict[str, Any]) -> str:
        """Determine D&D class based on stats"""
        intent = stats.get("intent", {}).get("primary", "unknown")
        performance = stats.get("performance", {}).get("score", 0.5)

        if intent == "fix" and performance > 0.7:
            return "Paladin"  # Fix-focused, high performance
        elif intent == "feature":
            return "Wizard"  # Feature creation
        elif intent == "optimize":
            return "Ranger"  # Optimization focus
        elif intent == "refactor":
            return "Monk"  # Code improvement
        else:
            return "Fighter"  # Versatile

    def _determine_alignment(self, stats: Dict[str, Any]) -> str:
        """Determine D&D alignment based on stats"""
        reputation = stats.get("reputation", {}).get("score", 0.5)
        consistency = stats.get("consistency", {}).get("score", 0.5)

        if reputation > 0.7 and consistency > 0.7:
            return "Lawful Good"
        elif reputation > 0.7:
            return "Neutral Good"
        elif consistency > 0.7:
            return "Lawful Neutral"
        elif reputation < 0.3:
            return "Chaotic Evil"
        else:
            return "True Neutral"


def main():
    try:
        """CLI interface"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Dual Wield Blame System")
        parser.add_argument("--file", type=str, required=True, help="File to analyze")
        parser.add_argument("--line", type=int, help="Specific line number")
        parser.add_argument("--dnd", action="store_true", help="Get D&D analytics")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        dual_wield = DualWieldBlameSystem(project_root)

        if args.dnd:
            result = dual_wield.get_dnd_analytics(args.file)
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"\n⚔️  D&D Analytics for {args.file}")
                print(f"Weapon Proficiencies: {result.get('weapon_proficiencies', {})}")
                print(f"Spell Slots: {result.get('spell_slots', {})}")
        else:
            result = dual_wield.dual_wield_blame(args.file, args.line)
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"\n⚔️  Dual Wield Blame")
                print(f"Mode: {result.get('mode', 'unknown')}")
                print(f"File: {result.get('file_path', args.file)}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()