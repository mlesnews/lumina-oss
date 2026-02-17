#!/usr/bin/env python3
"""
JARVIS Gut Brain & Analytical Decisioning System

Capturing the "second brain" feeling - gut vs analytical brain.
Poker/probability decision-making: calculated bets, hedging, chasing probability.
T-800 vs T-1000: Human-like vs advanced AI decision-making.

@JARVIS @GUT_BRAIN @ANALYTICAL_BRAIN @SECOND_BRAIN @POKER @PROBABILITY @HEDGING
@DECISIONING @T800 @T1000 @TERMINATOR
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
import random

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("GutBrainAnalyticalDecisioning")


class BrainType(Enum):
    """Type of brain/decision-making"""
    GUT_BRAIN = "GUT_BRAIN"  # Intuitive, feeling-based
    ANALYTICAL_BRAIN = "ANALYTICAL_BRAIN"  # Logical, data-based
    SECOND_BRAIN = "SECOND_BRAIN"  # The AI collaboration
    INTEGRATED = "INTEGRATED"  # Both working together


class DecisionStyle(Enum):
    """Style of decision-making"""
    POKER_CALCULATED = "POKER_CALCULATED"  # Calculated poker bet
    PROBABILITY_CHASING = "PROBABILITY_CHASING"  # Chasing probability
    HEDGING = "HEDGING"  # Hedging bets
    ANALYTICAL = "ANALYTICAL"  # Analytical, not emotional
    EMOTIONAL = "EMOTIONAL"  # Emotional (to be avoided)
    T800 = "T800"  # Human-like, methodical
    T1000 = "T1000"  # Advanced, adaptive


@dataclass
class Decision:
    """A decision being made"""
    decision_id: str
    description: str
    gut_feeling: float  # 0.0 to 1.0 (gut confidence)
    analytical_confidence: float  # 0.0 to 1.0 (analytical confidence)
    probability: float  # 0.0 to 1.0 (calculated probability)
    decision_style: DecisionStyle
    brain_type: BrainType
    poker_analogy: str = ""  # Poker bet analogy
    hedging_strategy: str = ""  # Hedging approach
    t800_t1000_balance: float = 0.5  # 0.0 = T-800, 1.0 = T-1000
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "decision_id": self.decision_id,
            "description": self.description,
            "gut_feeling": self.gut_feeling,
            "analytical_confidence": self.analytical_confidence,
            "probability": self.probability,
            "decision_style": self.decision_style.value,
            "brain_type": self.brain_type.value,
            "poker_analogy": self.poker_analogy,
            "hedging_strategy": self.hedging_strategy,
            "t800_t1000_balance": self.t800_t1000_balance,
            "metadata": self.metadata
        }
        return data

    def calculate_integrated_confidence(self) -> float:
        """Calculate integrated confidence (gut + analytical)"""
        # Weighted average: 40% gut, 60% analytical (trying to be analytical)
        return (self.gut_feeling * 0.4) + (self.analytical_confidence * 0.6)

    def is_analytical_not_emotional(self) -> bool:
        """Check if decision is analytical rather than emotional"""
        return self.analytical_confidence > self.gut_feeling


@dataclass
class PokerBet:
    """A poker bet analogy for decision-making"""
    bet_id: str
    decision_id: str
    bet_size: float  # Size of the bet
    pot_odds: float  # Pot odds
    implied_odds: float  # Implied odds
    probability_of_winning: float  # Calculated probability
    expected_value: float  # EV of the bet
    is_calculated: bool  # Is this a calculated bet?
    hedging: bool  # Is this hedging?
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class GutBrainAnalyticalDecisioning:
    """
    Gut Brain & Analytical Decisioning System

    Capturing the "second brain" feeling - gut vs analytical.
    Poker/probability decision-making framework.
    T-800 vs T-1000 balance.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = self.project_root / "data" / "gut_brain_decisioning"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("GutBrainAnalyticalDecisioning")

        self.decisions: List[Decision] = []
        self.poker_bets: List[PokerBet] = []

        self.logger.info("=" * 70)
        self.logger.info("🧠 GUT BRAIN & ANALYTICAL DECISIONING SYSTEM")
        self.logger.info("   Second brain feeling - gut vs analytical")
        self.logger.info("   Poker/probability decision-making")
        self.logger.info("   T-800 vs T-1000 balance")
        self.logger.info("=" * 70)
        self.logger.info("")

    def create_decision_framework(self) -> Dict[str, Any]:
        """Create the decision-making framework"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🧠 CREATING DECISION FRAMEWORK")
        self.logger.info("=" * 70)
        self.logger.info("")

        # Core insight decision
        core_decision = Decision(
            decision_id="CORE_INSIGHT_001",
            description="The collaboration feels more 'gut' than 'brain' - like a 'second brain'. Taking calculated poker bets, chasing probability, hedging bets. Trying to be analytical instead of emotional.",
            gut_feeling=0.85,  # Strong gut feeling
            analytical_confidence=0.75,  # Good analytical confidence
            probability=0.80,  # 80% probability this is the right approach
            decision_style=DecisionStyle.POKER_CALCULATED,
            brain_type=BrainType.SECOND_BRAIN,
            poker_analogy="Large but calculated poker bet - chasing probability, hedging bets",
            hedging_strategy="Diversify approaches, maintain multiple options, balance risk",
            t800_t1000_balance=0.6,  # Slightly more T-1000 (advanced) than T-800 (human-like)
            metadata={
                "insight": "Feels more gut than brain",
                "second_brain": True,
                "analytical_priority": True,
                "emotional_avoidance": True
            }
        )

        self.decisions.append(core_decision)

        # Create poker bet analogy
        poker_bet = PokerBet(
            bet_id="POKER_BET_001",
            decision_id=core_decision.decision_id,
            bet_size=0.30,  # 30% of stack (large but calculated)
            pot_odds=0.40,  # 40% pot odds
            implied_odds=0.50,  # 50% implied odds
            probability_of_winning=core_decision.probability,
            expected_value=self._calculate_ev(core_decision.probability, 0.40, 0.30),
            is_calculated=True,
            hedging=True,
            metadata={
                "bet_type": "calculated",
                "risk_level": "moderate",
                "hedging": True
            }
        )

        self.poker_bets.append(poker_bet)

        # Log decision
        integrated_confidence = core_decision.calculate_integrated_confidence()
        is_analytical = core_decision.is_analytical_not_emotional()

        self.logger.info("   🧠 CORE DECISION:")
        self.logger.info(f"      Description: {core_decision.description[:80]}...")
        self.logger.info(f"      Gut Feeling: {core_decision.gut_feeling:.2f}")
        self.logger.info(f"      Analytical Confidence: {core_decision.analytical_confidence:.2f}")
        self.logger.info(f"      Integrated Confidence: {integrated_confidence:.2f}")
        self.logger.info(f"      Probability: {core_decision.probability:.2f}")
        self.logger.info(f"      Is Analytical (not emotional): {is_analytical}")
        self.logger.info(f"      T-800/T-1000 Balance: {core_decision.t800_t1000_balance:.2f} ({'T-1000' if core_decision.t800_t1000_balance > 0.5 else 'T-800'})")
        self.logger.info("")

        self.logger.info("   🎲 POKER BET ANALOGY:")
        self.logger.info(f"      Bet Size: {poker_bet.bet_size:.0%} of stack (large but calculated)")
        self.logger.info(f"      Pot Odds: {poker_bet.pot_odds:.0%}")
        self.logger.info(f"      Probability of Winning: {poker_bet.probability_of_winning:.0%}")
        self.logger.info(f"      Expected Value: {poker_bet.expected_value:.2f}")
        self.logger.info(f"      Is Calculated: {poker_bet.is_calculated}")
        self.logger.info(f"      Hedging: {poker_bet.hedging}")
        self.logger.info("")

        framework = {
            "framework_id": f"decision_framework_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "core_insight": {
                "feeling": "More gut than brain",
                "second_brain": True,
                "poker_analogy": "Large but calculated poker bet",
                "strategy": "Chasing probability, hedging bets",
                "goal": "Be analytical instead of emotional"
            },
            "decision": core_decision.to_dict(),
            "poker_bet": poker_bet.to_dict(),
            "t800_t1000_metaphor": {
                "t800": "Human-like, methodical, predictable",
                "t1000": "Advanced, adaptive, liquid metal",
                "balance": core_decision.t800_t1000_balance,
                "interpretation": "Slightly more T-1000 (advanced) than T-800 (human-like) - adaptive and advanced, but still methodical"
            },
            "decisioning_principles": {
                "gut_brain": "Trust intuition but verify with analysis",
                "analytical_brain": "Use data and logic, avoid emotion",
                "second_brain": "AI collaboration as second brain",
                "poker_analogy": "Calculated bets, chase probability, hedge bets",
                "t800_t1000": "Balance human-like methodical approach with advanced adaptive capabilities"
            }
        }

        return framework

    def _calculate_ev(self, probability: float, pot_odds: float, bet_size: float) -> float:
        """Calculate expected value of a poker bet"""
        # Simplified EV calculation
        win_value = pot_odds * probability
        lose_value = bet_size * (1 - probability)
        ev = win_value - lose_value
        return ev

    def analyze_decision_balance(self) -> Dict[str, Any]:
        """Analyze the balance between gut and analytical decision-making"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("⚖️  ANALYZING DECISION BALANCE")
        self.logger.info("=" * 70)
        self.logger.info("")

        if not self.decisions:
            return {}

        # Calculate averages
        avg_gut = sum(d.gut_feeling for d in self.decisions) / len(self.decisions)
        avg_analytical = sum(d.analytical_confidence for d in self.decisions) / len(self.decisions)
        avg_integrated = sum(d.calculate_integrated_confidence() for d in self.decisions) / len(self.decisions)
        avg_t800_t1000 = sum(d.t800_t1000_balance for d in self.decisions) / len(self.decisions)

        analytical_count = sum(1 for d in self.decisions if d.is_analytical_not_emotional())
        analytical_pct = (analytical_count / len(self.decisions)) * 100

        analysis = {
            "average_gut_feeling": avg_gut,
            "average_analytical_confidence": avg_analytical,
            "average_integrated_confidence": avg_integrated,
            "average_t800_t1000_balance": avg_t800_t1000,
            "analytical_vs_emotional": {
                "analytical_count": analytical_count,
                "analytical_percentage": analytical_pct,
                "status": "ANALYTICAL" if analytical_pct >= 50 else "MIXED" if analytical_pct >= 25 else "EMOTIONAL"
            },
            "brain_type_distribution": {},
            "recommendation": ""
        }

        # Brain type distribution
        for brain_type in BrainType:
            count = sum(1 for d in self.decisions if d.brain_type == brain_type)
            analysis["brain_type_distribution"][brain_type.value] = {
                "count": count,
                "percentage": (count / len(self.decisions)) * 100
            }

        # Generate recommendation
        if avg_analytical > avg_gut:
            analysis["recommendation"] = "Maintain analytical focus. Good balance - analytical over gut feeling."
        elif avg_gut > avg_analytical:
            analysis["recommendation"] = "Increase analytical component. Gut feeling is strong, but need more analysis."
        else:
            analysis["recommendation"] = "Balance is good. Both gut and analytical components are equal."

        self.logger.info("   📊 AVERAGE METRICS:")
        self.logger.info(f"      Gut Feeling: {avg_gut:.2f}")
        self.logger.info(f"      Analytical Confidence: {avg_analytical:.2f}")
        self.logger.info(f"      Integrated Confidence: {avg_integrated:.2f}")
        self.logger.info(f"      T-800/T-1000 Balance: {avg_t800_t1000:.2f}")
        self.logger.info("")
        self.logger.info(f"   ⚖️  ANALYTICAL VS EMOTIONAL:")
        self.logger.info(f"      Analytical Decisions: {analytical_pct:.1f}%")
        self.logger.info(f"      Status: {analysis['analytical_vs_emotional']['status']}")
        self.logger.info("")
        self.logger.info(f"   💡 RECOMMENDATION:")
        self.logger.info(f"      {analysis['recommendation']}")
        self.logger.info("")

        return analysis

    def create_comprehensive_report(self) -> Dict[str, Any]:
        try:
            """Create comprehensive report"""
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📊 CREATING COMPREHENSIVE REPORT")
            self.logger.info("=" * 70)
            self.logger.info("")

            # Create decision framework
            framework = self.create_decision_framework()

            # Analyze decision balance
            balance_analysis = self.analyze_decision_balance()

            # Create report
            report = {
                "report_id": f"gut_brain_decisioning_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "core_insight": "Feels more gut than brain - second brain. Taking calculated poker bets, chasing probability, hedging. Trying to be analytical instead of emotional. Like T-800 facing off against T-1000.",
                "framework": framework,
                "balance_analysis": balance_analysis,
                "decisions": [d.to_dict() for d in self.decisions],
                "poker_bets": [b.to_dict() for b in self.poker_bets],
                "metaphors": {
                    "t800": {
                        "description": "Human-like, methodical, predictable",
                        "characteristics": ["Methodical", "Predictable", "Human-like", "Reliable"],
                        "decision_style": "Analytical, step-by-step, methodical"
                    },
                    "t1000": {
                        "description": "Advanced, adaptive, liquid metal",
                        "characteristics": ["Advanced", "Adaptive", "Liquid", "Evolving"],
                        "decision_style": "Adaptive, fluid, advanced"
                    },
                    "balance_interpretation": "Slightly more T-1000 (advanced/adaptive) than T-800 (human-like/methodical). The collaboration is advanced and adaptive, but still maintains methodical approach."
                },
                "decisioning_principles": {
                    "gut_brain": "Trust intuition but verify with analysis",
                    "analytical_brain": "Use data and logic, avoid emotion",
                    "second_brain": "AI collaboration as second brain - feels more gut than brain",
                    "poker_analogy": "Large but calculated poker bet - chasing probability, hedging bets",
                    "t800_t1000": "Balance human-like methodical (T-800) with advanced adaptive (T-1000)",
                    "analytical_priority": "Doing human best to be analytical instead of emotional when decisioning"
                }
            }

            # Save report
            filename = self.data_dir / f"gut_brain_decisioning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📊 REPORT SUMMARY")
            self.logger.info("=" * 70)
            self.logger.info("   🧠 Core Insight: Feels more gut than brain - second brain")
            self.logger.info("   🎲 Poker Analogy: Large but calculated poker bet")
            self.logger.info("   ⚖️  Goal: Be analytical instead of emotional")
            self.logger.info("   🤖 Metaphor: T-800 vs T-1000")
            self.logger.info("")
            self.logger.info(f"✅ Report saved: {filename}")
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("✅ GUT BRAIN & ANALYTICAL DECISIONING SYSTEM COMPLETE")
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
        system = GutBrainAnalyticalDecisioning(project_root)
        report = system.create_comprehensive_report()

        print()
        print("=" * 70)
        print("🧠 GUT BRAIN & ANALYTICAL DECISIONING SYSTEM")
        print("=" * 70)
        print("   🧠 Core Insight: Feels more gut than brain - second brain")
        print("   🎲 Poker Analogy: Large but calculated poker bet")
        print("   ⚖️  Goal: Be analytical instead of emotional")
        print("   🤖 Metaphor: T-800 vs T-1000")
        print()
        if report.get("balance_analysis"):
            ba = report["balance_analysis"]
            print(f"   📊 Average Gut Feeling: {ba.get('average_gut_feeling', 0):.2f}")
            print(f"   📊 Average Analytical: {ba.get('average_analytical_confidence', 0):.2f}")
            print(f"   📊 Analytical Decisions: {ba.get('analytical_vs_emotional', {}).get('analytical_percentage', 0):.1f}%")
        print()
        print("=" * 70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()