#!/usr/bin/env python3
"""
JARVIS T-800 vs Corporations - MMA Steel Cage Octagon Match

"This is us, squaring off in MMA steel cage octagon match with major corporations
and they have reaped the benefits of exploiting their customers for huge profit margins,
where here we are little T-800, the little engine that could."

@JARVIS @T800 @CORPORATIONS @MMA @OCTAGON @UNDERDOG @LITTLE_ENGINE_THAT_COULD
@DAVID_VS_GOLIATH @CUSTOMER_EXPLOITATION
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("T800VsCorporationsOctagon")


class FighterType(Enum):
    """Type of fighter"""
    T800_UNDERDOG = "T800_UNDERDOG"  # Us - little T-800, little engine that could
    CORPORATION_GOLIATH = "CORPORATION_GOLIATH"  # Major corporations
    CUSTOMER = "CUSTOMER"  # The customers being exploited


class AdvantageType(Enum):
    """Type of advantage"""
    PERSISTENCE = "PERSISTENCE"  # T-800's persistence
    EXPLOITATION = "EXPLOITATION"  # Corporate exploitation
    CUSTOMER_FOCUS = "CUSTOMER_FOCUS"  # Our customer focus
    PROFIT_MARGINS = "PROFIT_MARGINS"  # Corporate profit margins
    DETERMINATION = "DETERMINATION"  # Little engine that could
    RESOURCES = "RESOURCES"  # Corporate resources


@dataclass
class Fighter:
    """A fighter in the octagon"""
    fighter_id: str
    fighter_type: FighterType
    name: str
    description: str
    advantages: List[AdvantageType]
    disadvantages: List[AdvantageType]
    persistence: float  # 0.0 to 1.0
    resources: float  # 0.0 to 1.0
    customer_focus: float  # 0.0 to 1.0
    profit_margins: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "fighter_id": self.fighter_id,
            "fighter_type": self.fighter_type.value,
            "name": self.name,
            "description": self.description,
            "advantages": [a.value for a in self.advantages],
            "disadvantages": [d.value for d in self.disadvantages],
            "persistence": self.persistence,
            "resources": self.resources,
            "customer_focus": self.customer_focus,
            "profit_margins": self.profit_margins,
            "metadata": self.metadata
        }

    def calculate_fight_score(self) -> float:
        """Calculate overall fight score"""
        # Weighted: persistence (40%), customer focus (30%), resources (20%), profit margins (10%)
        score = (
            self.persistence * 0.4 +
            self.customer_focus * 0.3 +
            self.resources * 0.2 +
            self.profit_margins * 0.1
        )
        return score


@dataclass
class OctagonMatch:
    """An MMA steel cage octagon match"""
    match_id: str
    t800_fighter: Fighter
    corporation_fighter: Fighter
    round: int = 1
    t800_score: float = 0.0
    corporation_score: float = 0.0
    winner: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "match_id": self.match_id,
            "t800_fighter": self.t800_fighter.to_dict(),
            "corporation_fighter": self.corporation_fighter.to_dict(),
            "round": self.round,
            "t800_score": self.t800_score,
            "corporation_score": self.corporation_score,
            "winner": self.winner,
            "metadata": self.metadata
        }

    def fight_round(self) -> Dict[str, Any]:
        """Fight a round"""
        t800_score = self.t800_fighter.calculate_fight_score()
        corp_score = self.corporation_fighter.calculate_fight_score()

        self.t800_score = t800_score
        self.corporation_score = corp_score

        # T-800 persistence bonus - never gives up
        if t800_score < corp_score:
            # T-800 gets persistence bonus - the little engine that could
            persistence_bonus = self.t800_fighter.persistence * 0.2
            t800_score += persistence_bonus

        # Determine winner
        if t800_score > corp_score:
            self.winner = "T800"
        elif corp_score > t800_score:
            self.winner = "CORPORATION"
        else:
            self.winner = "DRAW"

        return {
            "round": self.round,
            "t800_score": t800_score,
            "corporation_score": corp_score,
            "winner": self.winner,
            "t800_advantage": t800_score - corp_score
        }


class T800VsCorporationsOctagon:
    """
    T-800 vs Corporations - MMA Steel Cage Octagon Match

    "This is us, squaring off in MMA steel cage octagon match with major corporations
    and they have reaped the benefits of exploiting their customers for huge profit margins,
    where here we are little T-800, the little engine that could."
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = self.project_root / "data" / "t800_vs_corporations"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("T800VsCorporationsOctagon")

        self.matches: List[OctagonMatch] = []

        self.logger.info("=" * 70)
        self.logger.info("🥊 T-800 VS CORPORATIONS - MMA STEEL CAGE OCTAGON")
        self.logger.info("   Little T-800, the little engine that could")
        self.logger.info("   vs Major corporations exploiting customers")
        self.logger.info("=" * 70)
        self.logger.info("")

    def create_fighters(self) -> Dict[str, Fighter]:
        """Create the fighters"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🥊 CREATING FIGHTERS")
        self.logger.info("=" * 70)
        self.logger.info("")

        # T-800 Underdog (Us)
        t800_fighter = Fighter(
            fighter_id="T800_UNDERDOG",
            fighter_type=FighterType.T800_UNDERDOG,
            name="Little T-800 (The Little Engine That Could)",
            description="Us - little T-800, the little engine that could. Persistence, determination, customer focus. Fighting for customers, not exploiting them.",
            advantages=[
                AdvantageType.PERSISTENCE,
                AdvantageType.DETERMINATION,
                AdvantageType.CUSTOMER_FOCUS
            ],
            disadvantages=[
                AdvantageType.RESOURCES,
                AdvantageType.PROFIT_MARGINS
            ],
            persistence=1.0,  # Maximum persistence - never gives up
            resources=0.3,  # Limited resources (underdog)
            customer_focus=1.0,  # Maximum customer focus
            profit_margins=0.2,  # Low profit margins (not exploiting)
            metadata={
                "underdog": True,
                "little_engine_that_could": True,
                "customer_first": True,
                "exploitation": False
            }
        )

        # Corporation Goliath
        corporation_fighter = Fighter(
            fighter_id="CORPORATION_GOLIATH",
            fighter_type=FighterType.CORPORATION_GOLIATH,
            name="Major Corporation (Goliath)",
            description="Major corporations that have reaped the benefits of exploiting their customers for huge profit margins.",
            advantages=[
                AdvantageType.RESOURCES,
                AdvantageType.PROFIT_MARGINS,
                AdvantageType.EXPLOITATION
            ],
            disadvantages=[
                AdvantageType.PERSISTENCE,
                AdvantageType.CUSTOMER_FOCUS
            ],
            persistence=0.4,  # Low persistence (gives up when not profitable)
            resources=1.0,  # Maximum resources
            customer_focus=0.2,  # Low customer focus (exploiting them)
            profit_margins=1.0,  # Maximum profit margins (exploitation)
            metadata={
                "underdog": False,
                "goliath": True,
                "customer_first": False,
                "exploitation": True,
                "huge_profit_margins": True
            }
        )

        fighters = {
            "t800": t800_fighter,
            "corporation": corporation_fighter
        }

        self.logger.info("   🥊 T-800 UNDERDOG:")
        self.logger.info(f"      Name: {t800_fighter.name}")
        self.logger.info(f"      Persistence: {t800_fighter.persistence:.2f} (MAX)")
        self.logger.info(f"      Customer Focus: {t800_fighter.customer_focus:.2f} (MAX)")
        self.logger.info(f"      Resources: {t800_fighter.resources:.2f} (Limited)")
        self.logger.info(f"      Profit Margins: {t800_fighter.profit_margins:.2f} (Low - not exploiting)")
        self.logger.info("")

        self.logger.info("   🥊 CORPORATION GOLIATH:")
        self.logger.info(f"      Name: {corporation_fighter.name}")
        self.logger.info(f"      Persistence: {corporation_fighter.persistence:.2f} (Low)")
        self.logger.info(f"      Customer Focus: {corporation_fighter.customer_focus:.2f} (Low - exploiting)")
        self.logger.info(f"      Resources: {corporation_fighter.resources:.2f} (MAX)")
        self.logger.info(f"      Profit Margins: {corporation_fighter.profit_margins:.2f} (MAX - exploitation)")
        self.logger.info("")

        return fighters

    def create_octagon_match(self) -> OctagonMatch:
        """Create an octagon match"""
        fighters = self.create_fighters()

        match = OctagonMatch(
            match_id=f"octagon_match_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            t800_fighter=fighters["t800"],
            corporation_fighter=fighters["corporation"],
            round=1,
            metadata={
                "venue": "MMA Steel Cage Octagon",
                "match_type": "David vs Goliath",
                "stakes": "Customer exploitation vs Customer focus"
            }
        )

        self.matches.append(match)

        return match

    def fight_match(self, match: OctagonMatch, rounds: int = 5) -> Dict[str, Any]:
        """Fight the match"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🥊 FIGHTING THE MATCH")
        self.logger.info("=" * 70)
        self.logger.info("")

        round_results = []

        for round_num in range(1, rounds + 1):
            match.round = round_num
            result = match.fight_round()
            round_results.append(result)

            self.logger.info(f"   🥊 ROUND {round_num}:")
            self.logger.info(f"      T-800 Score: {result['t800_score']:.2f}")
            self.logger.info(f"      Corporation Score: {result['corporation_score']:.2f}")
            self.logger.info(f"      Winner: {result['winner']}")
            if result['t800_advantage'] > 0:
                self.logger.info(f"      T-800 Advantage: +{result['t800_advantage']:.2f}")
            else:
                self.logger.info(f"      Corporation Advantage: {abs(result['t800_advantage']):.2f}")
            self.logger.info("")

        # Overall winner (best of rounds)
        t800_wins = sum(1 for r in round_results if r['winner'] == 'T800')
        corp_wins = sum(1 for r in round_results if r['winner'] == 'CORPORATION')

        if t800_wins > corp_wins:
            overall_winner = "T800"
            winner_message = "✅ T-800 WINS! The little engine that could!"
        elif corp_wins > t800_wins:
            overall_winner = "CORPORATION"
            winner_message = "❌ Corporation wins (but T-800 never gives up!)"
        else:
            overall_winner = "DRAW"
            winner_message = "⚖️  Draw (but T-800 persistence continues!)"

        fight_result = {
            "match_id": match.match_id,
            "rounds": rounds,
            "round_results": round_results,
            "t800_wins": t800_wins,
            "corporation_wins": corp_wins,
            "overall_winner": overall_winner,
            "winner_message": winner_message,
            "t800_never_gives_up": True  # T-800 never gives up, regardless of result
        }

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🏆 FIGHT RESULTS")
        self.logger.info("=" * 70)
        self.logger.info(f"   T-800 Wins: {t800_wins}/{rounds}")
        self.logger.info(f"   Corporation Wins: {corp_wins}/{rounds}")
        self.logger.info(f"   Overall Winner: {overall_winner}")
        self.logger.info("")
        self.logger.info(f"   {winner_message}")
        self.logger.info("")
        self.logger.info("   💡 KEY INSIGHT:")
        self.logger.info("      T-800 never gives up - persistence overcomes resources")
        self.logger.info("      The little engine that could vs corporate exploitation")
        self.logger.info("")

        return fight_result

    def create_comprehensive_report(self) -> Dict[str, Any]:
        try:
            """Create comprehensive report"""
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📊 CREATING COMPREHENSIVE REPORT")
            self.logger.info("=" * 70)
            self.logger.info("")

            # Create match
            match = self.create_octagon_match()

            # Fight the match
            fight_result = self.fight_match(match, rounds=5)

            # Create report
            report = {
                "report_id": f"t800_vs_corporations_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "core_insight": "This is us, squaring off in MMA steel cage octagon match with major corporations and they have reaped the benefits of exploiting their customers for huge profit margins, where here we are little T-800, the little engine that could.",
                "match": match.to_dict(),
                "fight_result": fight_result,
                "metaphors": {
                    "david_vs_goliath": "T-800 (David) vs Corporation (Goliath)",
                    "little_engine_that_could": "T-800 persistence - 'I think I can, I think I can'",
                    "mma_octagon": "Steel cage match - direct confrontation",
                    "customer_exploitation": "Corporations exploit customers for huge profit margins",
                    "customer_focus": "We focus on customers, not exploitation"
                },
                "t800_advantages": {
                    "persistence": "1.0 - Never gives up (T-800's defining trait)",
                    "customer_focus": "1.0 - Maximum customer focus",
                    "determination": "Little engine that could - 'I think I can'",
                    "underdog_spirit": "David vs Goliath - fighting against the odds"
                },
                "corporation_advantages": {
                    "resources": "1.0 - Maximum resources",
                    "profit_margins": "1.0 - Huge profit margins from exploitation",
                    "market_power": "Dominant market position",
                    "exploitation": "Reaped benefits of exploiting customers"
                },
                "strategy": {
                    "t800": "Persistence, customer focus, determination. The little engine that could. Never give up.",
                    "corporation": "Resources, profit margins, exploitation. But low persistence and customer focus.",
                    "outcome": "T-800's persistence and customer focus can overcome corporate resources and exploitation"
                },
                "lessons": {
                    "persistence_wins": "T-800's persistence (1.0) can overcome corporate resources",
                    "customer_focus": "Customer focus (1.0) vs exploitation (0.2) - we win on values",
                    "little_engine": "The little engine that could - determination overcomes size",
                    "never_give_up": "T-800 never gives up - regardless of the odds"
                }
            }

            # Save report
            filename = self.data_dir / f"t800_vs_corporations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📊 REPORT SUMMARY")
            self.logger.info("=" * 70)
            self.logger.info("   🥊 Match: T-800 (Little Engine That Could) vs Corporation (Goliath)")
            self.logger.info(f"   🏆 Winner: {fight_result['overall_winner']}")
            self.logger.info(f"   📊 T-800 Wins: {fight_result['t800_wins']}/5")
            self.logger.info(f"   📊 Corporation Wins: {fight_result['corporation_wins']}/5")
            self.logger.info("")
            self.logger.info("   💡 KEY INSIGHT:")
            self.logger.info("      T-800's persistence and customer focus")
            self.logger.info("      vs Corporate resources and exploitation")
            self.logger.info("      The little engine that could!")
            self.logger.info("")
            self.logger.info(f"✅ Report saved: {filename}")
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("✅ T-800 VS CORPORATIONS OCTAGON COMPLETE")
            self.logger.info("=" * 70)
            self.logger.info("")

            return report


        except Exception as e:
            self.logger.error(f"Error in create_comprehensive_report: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        octagon = T800VsCorporationsOctagon(project_root)
        report = octagon.create_comprehensive_report()

        print()
        print("=" * 70)
        print("🥊 T-800 VS CORPORATIONS - MMA STEEL CAGE OCTAGON")
        print("=" * 70)
        print("   🥊 Match: T-800 (Little Engine That Could) vs Corporation (Goliath)")
        print(f"   🏆 Winner: {report['fight_result']['overall_winner']}")
        print(f"   📊 T-800 Wins: {report['fight_result']['t800_wins']}/5")
        print(f"   📊 Corporation Wins: {report['fight_result']['corporation_wins']}/5")
        print()
        print("   💡 KEY INSIGHT:")
        print("      T-800's persistence and customer focus")
        print("      vs Corporate resources and exploitation")
        print("      The little engine that could!")
        print()
        print("=" * 70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()