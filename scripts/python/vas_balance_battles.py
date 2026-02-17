#!/usr/bin/env python3
"""
Balance VA Streetfighter/WoW Jedi Battles

Reduces fight frequency and intensity to make battles more balanced and less aggressive.
Current settings are too aggressive - fights happen too often and last too long.

Tags: #VAS #BATTLES #BALANCE #STREETFIGHTER #WOW #JEDI @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VAsBalanceBattles")


class VAsBalanceBattles:
    """
    Balance VA battle system parameters
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize balancer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        logger.info("✅ VAs Battle Balancer initialized")

    def balance_battle_parameters(self) -> Dict[str, Any]:
        """
        Balance battle parameters to reduce frequency and intensity

        Changes:
        - fight_probability: 0.40 (40%) -> 0.12 (12%) - Much less frequent
        - fight_check_interval: 5.0s -> 20.0s - Check less often
        - min_fight_duration: 30.0s -> 12.0s - Shorter minimum fights
        - end_probability: 0.003/0.005 -> 0.01/0.015 - End fights more easily
        - Reduce aggressive mode damage multipliers
        """
        logger.info("="*80)
        logger.info("⚖️  Balancing VA Battle System")
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

            # Change 1: Reduce fight probability (40% -> 12%)
            old_prob = "self.fight_probability = 0.40  # 40% chance to initiate fight (increased for more hunting)"
            new_prob = "self.fight_probability = 0.12  # 12% chance to initiate fight (balanced for less frequent battles)"
            if old_prob in content:
                content = content.replace(old_prob, new_prob)
                result["changes"].append("Reduced fight probability from 40% to 12%")
                logger.info("   ✅ Reduced fight probability")

            # Change 2: Increase fight check interval (5s -> 20s)
            old_interval = "self.fight_check_interval = 5.0  # Check for fight chance every 5 seconds"
            new_interval = "self.fight_check_interval = 20.0  # Check for fight chance every 20 seconds (balanced frequency)"
            if old_interval in content:
                content = content.replace(old_interval, new_interval)
                result["changes"].append("Increased fight check interval from 5s to 20s")
                logger.info("   ✅ Increased fight check interval")

            # Change 3: Reduce minimum fight duration (30s -> 12s)
            old_duration = "self.min_fight_duration = 30.0  # Minimum fight duration in seconds (longer charges)"
            new_duration = "self.min_fight_duration = 12.0  # Minimum fight duration in seconds (balanced for shorter battles)"
            if old_duration in content:
                content = content.replace(old_duration, new_duration)
                result["changes"].append("Reduced minimum fight duration from 30s to 12s")
                logger.info("   ✅ Reduced minimum fight duration")

            # Change 4: Increase end probability (0.003/0.005 -> 0.01/0.015)
            old_end_agg = "end_probability = 0.003 if self.aggressive_negotiation_mode else 0.005  # Even lower for aggressive mode"
            new_end_agg = "end_probability = 0.01 if self.aggressive_negotiation_mode else 0.015  # Balanced end probability"
            if old_end_agg in content:
                content = content.replace(old_end_agg, new_end_agg)
                result["changes"].append("Increased end probability for fights")
                logger.info("   ✅ Increased end probability")

            # Change 5: Reduce aggressive mode damage multiplier (1.5 -> 1.2)
            old_mult = "base_multiplier = 1.5 if self.aggressive_negotiation_mode else 1.0"
            new_mult = "base_multiplier = 1.2 if self.aggressive_negotiation_mode else 1.0  # Reduced aggressive damage (balanced)"
            if old_mult in content:
                content = content.replace(old_mult, new_mult)
                result["changes"].append("Reduced aggressive mode damage multiplier from 1.5x to 1.2x")
                logger.info("   ✅ Reduced aggressive damage multiplier")

            # Change 6: Reduce aggressive mode damage chances and amounts
            # Close range damage chance: 50% -> 35%
            old_close_chance = "damage_chance = 0.5 if self.aggressive_negotiation_mode else 0.3  # 50% vs 30%"
            new_close_chance = "damage_chance = 0.35 if self.aggressive_negotiation_mode else 0.25  # 35% vs 25% (balanced)"
            if old_close_chance in content:
                content = content.replace(old_close_chance, new_close_chance)
                result["changes"].append("Reduced close range damage chance")
                logger.info("   ✅ Reduced close range damage chance")

            # Close range damage amount: 7-20 -> 5-15
            old_close_dmg = "base_damage = random.uniform(7.0, 20.0) if self.aggressive_negotiation_mode else random.uniform(5.0, 15.0)"
            new_close_dmg = "base_damage = random.uniform(5.0, 15.0) if self.aggressive_negotiation_mode else random.uniform(3.0, 10.0)  # Balanced damage"
            if old_close_dmg in content:
                content = content.replace(old_close_dmg, new_close_dmg)
                result["changes"].append("Reduced close range damage amounts")
                logger.info("   ✅ Reduced close range damage")

            # Medium range damage chance: 30% -> 20%
            old_med_chance = "damage_chance = 0.3 if self.aggressive_negotiation_mode else 0.15  # 30% vs 15%"
            new_med_chance = "damage_chance = 0.20 if self.aggressive_negotiation_mode else 0.12  # 20% vs 12% (balanced)"
            if old_med_chance in content:
                content = content.replace(old_med_chance, new_med_chance)
                result["changes"].append("Reduced medium range damage chance")
                logger.info("   ✅ Reduced medium range damage chance")

            # Medium range damage amount: 5-15 -> 3-10
            old_med_dmg = "base_damage = random.uniform(5.0, 15.0) if self.aggressive_negotiation_mode else random.uniform(3.0, 10.0)"
            new_med_dmg = "base_damage = random.uniform(3.0, 10.0) if self.aggressive_negotiation_mode else random.uniform(2.0, 7.0)  # Balanced damage"
            if old_med_dmg in content:
                content = content.replace(old_med_dmg, new_med_dmg)
                result["changes"].append("Reduced medium range damage amounts")
                logger.info("   ✅ Reduced medium range damage")

            # Far range damage chance: 15% -> 10%
            old_far_chance = "damage_chance = 0.15 if self.aggressive_negotiation_mode else 0.05  # 15% vs 5%"
            new_far_chance = "damage_chance = 0.10 if self.aggressive_negotiation_mode else 0.04  # 10% vs 4% (balanced)"
            if old_far_chance in content:
                content = content.replace(old_far_chance, new_far_chance)
                result["changes"].append("Reduced far range damage chance")
                logger.info("   ✅ Reduced far range damage chance")

            # Far range damage amount: 3-10 -> 2-7
            old_far_dmg = "base_damage = random.uniform(3.0, 10.0) if self.aggressive_negotiation_mode else random.uniform(1.0, 5.0)"
            new_far_dmg = "base_damage = random.uniform(2.0, 7.0) if self.aggressive_negotiation_mode else random.uniform(1.0, 4.0)  # Balanced damage"
            if old_far_dmg in content:
                content = content.replace(old_far_dmg, new_far_dmg)
                result["changes"].append("Reduced far range damage amounts")
                logger.info("   ✅ Reduced far range damage")

            # Change 7: Reduce aggressive charge frequency (every 30 frames -> every 60 frames)
            old_charge = "if self.attack_charge_counter % 30 == 0:"
            new_charge = "if self.attack_charge_counter % 60 == 0:  # Reduced charge frequency (balanced)"
            if old_charge in content:
                content = content.replace(old_charge, new_charge)
                result["changes"].append("Reduced aggressive charge frequency")
                logger.info("   ✅ Reduced aggressive charge frequency")

            # Save changes
            if content != original_content:
                imva_file.write_text(content, encoding='utf-8')
                result["changes"].append("Saved balanced battle parameters to ironman_virtual_assistant.py")
                logger.info("   ✅ Saved balanced battle parameters")
            else:
                logger.info("   ℹ️  No changes needed (may already be balanced)")

        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Error balancing battles: {e}")
            logger.error(f"❌ Error: {e}", exc_info=True)

        return result


if __name__ == "__main__":
    import argparse
    from typing import Optional

    parser = argparse.ArgumentParser(description="Balance VA Streetfighter/WoW Jedi Battles")
    parser.add_argument("--project-root", type=Path, help="Project root directory")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("⚖️  Balancing VA Battle System")
    print("="*80 + "\n")

    balancer = VAsBalanceBattles(project_root=args.project_root)
    result = balancer.balance_battle_parameters()

    print("\n" + "="*80)
    print("📊 BALANCE RESULTS")
    print("="*80)
    print(f"Success: {'✅' if result['success'] else '❌'}")

    if result.get("changes"):
        print(f"\n✅ Changes Applied: {len(result['changes'])}")
        for change in result["changes"]:
            print(f"   • {change}")

    if result.get("errors"):
        print("\n❌ Errors:")
        for error in result["errors"]:
            print(f"   • {error}")

    print("\n" + "="*80)
    print("📊 BALANCE SUMMARY")
    print("="*80)
    print("Before → After:")
    print("  Fight Probability: 40% → 12%")
    print("  Fight Check Interval: 5s → 20s")
    print("  Min Fight Duration: 30s → 12s")
    print("  End Probability: 0.3-0.5% → 1.0-1.5%")
    print("  Aggressive Damage Multiplier: 1.5x → 1.2x")
    print("  Damage Chances: Reduced across all ranges")
    print("  Damage Amounts: Reduced across all ranges")
    print("  Charge Frequency: Every 30 frames → Every 60 frames")
    print("\n✅ Battles are now more balanced and less frequent")
    print("="*80 + "\n")
