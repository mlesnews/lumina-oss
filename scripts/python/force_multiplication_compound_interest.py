#!/usr/bin/env python3
"""
Force Multiplication & Compound Interest - End Goal

"Let's filter out the noise, apply force-multiplication,
and compound interest be our end goal."

Force Multiplication:
- Leverage AI to multiply our effectiveness
- Automate repetitive tasks
- Scale solutions

Compound Interest:
- Small improvements compound over time
- Learning builds on learning
- Success breeds success
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ForceMultiplicationCompoundInterest")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ForceMultiplier:
    """Force multiplier"""
    multiplier_id: str
    name: str
    description: str
    multiplier_value: float  # How much it multiplies effectiveness
    noise_filtered: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CompoundInterest:
    """Compound interest calculation"""
    interest_id: str
    name: str
    initial_value: float
    rate: float  # Interest rate (e.g., 0.1 for 10%)
    periods: int  # Number of periods
    current_value: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def calculate(self) -> float:
        """Calculate compound interest: A = P(1 + r)^n"""
        self.current_value = self.initial_value * ((1 + self.rate) ** self.periods)
        return self.current_value

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['calculated_value'] = self.calculate()
        return data


class ForceMultiplicationCompoundInterest:
    """
    Force Multiplication & Compound Interest - End Goal

    "Let's filter out the noise, apply force-multiplication,
    and compound interest be our end goal."
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Force Multiplication & Compound Interest"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("ForceMultiplicationCompoundInterest")

        # Force multipliers
        self.force_multipliers: List[ForceMultiplier] = []

        # Compound interest calculations
        self.compound_interests: List[CompoundInterest] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "force_multiplication_compound_interest"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("⚡ Force Multiplication & Compound Interest initialized")
        self.logger.info("   Filter out the noise")
        self.logger.info("   Apply force-multiplication")
        self.logger.info("   Compound interest be our end goal")

    def add_force_multiplier(self, name: str, description: str,
                            multiplier_value: float,
                            noise_filtered: bool = True) -> ForceMultiplier:
        """
        Add force multiplier

        "Apply force-multiplication"
        """
        multiplier = ForceMultiplier(
            multiplier_id=f"multiplier_{len(self.force_multipliers) + 1}_{int(datetime.now().timestamp())}",
            name=name,
            description=description,
            multiplier_value=multiplier_value,
            noise_filtered=noise_filtered
        )

        self.force_multipliers.append(multiplier)
        self._save_force_multiplier(multiplier)

        self.logger.info(f"  ⚡ Force multiplier added: {name}")
        self.logger.info(f"     Multiplier: {multiplier_value}x")
        self.logger.info(f"     Noise Filtered: {noise_filtered}")

        return multiplier

    def calculate_compound_interest(self, name: str, initial_value: float,
                                   rate: float, periods: int) -> CompoundInterest:
        """
        Calculate compound interest

        "Compound interest be our end goal"

        Formula: A = P(1 + r)^n
        """
        interest = CompoundInterest(
            interest_id=f"interest_{len(self.compound_interests) + 1}_{int(datetime.now().timestamp())}",
            name=name,
            initial_value=initial_value,
            rate=rate,
            periods=periods
        )

        calculated_value = interest.calculate()
        self.compound_interests.append(interest)
        self._save_compound_interest(interest)

        self.logger.info(f"  💰 Compound interest calculated: {name}")
        self.logger.info(f"     Initial: {initial_value}")
        self.logger.info(f"     Rate: {rate * 100}%")
        self.logger.info(f"     Periods: {periods}")
        self.logger.info(f"     Final Value: {calculated_value:.2f}")

        return interest

    def filter_noise(self, items: List[str], noise_patterns: List[str] = None) -> List[str]:
        """
        Filter out the noise

        "Filter out the noise"
        """
        if noise_patterns is None:
            noise_patterns = ["noise", "unimportant", "distraction", "irrelevant"]

        filtered = []
        for item in items:
            is_noise = any(pattern.lower() in item.lower() for pattern in noise_patterns)
            if not is_noise:
                filtered.append(item)

        self.logger.info(f"  🔇 Filtered noise: {len(items)} -> {len(filtered)} items")

        return filtered

    def get_end_goal(self) -> Dict[str, Any]:
        """Get end goal summary"""
        total_multiplier = 1.0
        for multiplier in self.force_multipliers:
            total_multiplier *= multiplier.multiplier_value

        total_compound_value = sum(interest.calculate() for interest in self.compound_interests)

        return {
            "force_multiplication": {
                "total_multipliers": len(self.force_multipliers),
                "total_multiplier_value": total_multiplier,
                "effectiveness_multiplied": f"{total_multiplier:.2f}x"
            },
            "compound_interest": {
                "total_calculations": len(self.compound_interests),
                "total_value": total_compound_value,
                "growth": "Exponential"
            },
            "end_goal": "Filter out the noise, apply force-multiplication, and compound interest be our end goal.",
            "philosophy": "Small improvements compound over time. Force multiplication amplifies our effectiveness."
        }

    def _save_force_multiplier(self, multiplier: ForceMultiplier) -> None:
        try:
            """Save force multiplier"""
            multiplier_file = self.data_dir / "force_multipliers" / f"{multiplier.multiplier_id}.json"
            multiplier_file.parent.mkdir(parents=True, exist_ok=True)
            with open(multiplier_file, 'w', encoding='utf-8') as f:
                json.dump(multiplier.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_force_multiplier: {e}", exc_info=True)
            raise
    def _save_compound_interest(self, interest: CompoundInterest) -> None:
        try:
            """Save compound interest"""
            interest_file = self.data_dir / "compound_interests" / f"{interest.interest_id}.json"
            interest_file.parent.mkdir(parents=True, exist_ok=True)
            with open(interest_file, 'w', encoding='utf-8') as f:
                json.dump(interest.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_compound_interest: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Force Multiplication & Compound Interest - End Goal")
    parser.add_argument("--add-multiplier", nargs=3, metavar=("NAME", "DESCRIPTION", "VALUE"),
                       help="Add force multiplier")
    parser.add_argument("--calculate-interest", nargs=4, metavar=("NAME", "INITIAL", "RATE", "PERIODS"),
                       help="Calculate compound interest")
    parser.add_argument("--filter-noise", nargs='+', help="Filter out noise (items)")
    parser.add_argument("--end-goal", action="store_true", help="Get end goal summary")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    force_compound = ForceMultiplicationCompoundInterest()

    if args.add_multiplier:
        name, description, value = args.add_multiplier
        multiplier = force_compound.add_force_multiplier(name, description, float(value))
        if args.json:
            print(json.dumps(multiplier.to_dict(), indent=2))
        else:
            print(f"\n⚡ Force Multiplier Added")
            print(f"   Name: {multiplier.name}")
            print(f"   Multiplier: {multiplier.multiplier_value}x")

    elif args.calculate_interest:
        name, initial, rate, periods = args.calculate_interest
        interest = force_compound.calculate_compound_interest(name, float(initial), float(rate), int(periods))
        if args.json:
            print(json.dumps(interest.to_dict(), indent=2))
        else:
            print(f"\n💰 Compound Interest Calculated")
            print(f"   Name: {interest.name}")
            print(f"   Initial: {interest.initial_value}")
            print(f"   Final: {interest.calculate():.2f}")

    elif args.filter_noise:
        filtered = force_compound.filter_noise(args.filter_noise)
        if args.json:
            print(json.dumps({"original": args.filter_noise, "filtered": filtered}, indent=2))
        else:
            print(f"\n🔇 Noise Filtered")
            print(f"   Original: {len(args.filter_noise)} items")
            print(f"   Filtered: {len(filtered)} items")
            print(f"   Removed: {len(args.filter_noise) - len(filtered)} items")

    elif args.end_goal:
        end_goal = force_compound.get_end_goal()
        if args.json:
            print(json.dumps(end_goal, indent=2))
        else:
            print(f"\n🎯 End Goal Summary")
            print(f"   Force Multiplication: {end_goal['force_multiplication']['effectiveness_multiplied']}")
            print(f"   Compound Interest: {end_goal['compound_interest']['total_value']:.2f}")
            print(f"\n   {end_goal['end_goal']}")
            print(f"   {end_goal['philosophy']}")

    else:
        parser.print_help()
        print("\n⚡ Force Multiplication & Compound Interest - End Goal")
        print("   Filter out the noise")
        print("   Apply force-multiplication")
        print("   Compound interest be our end goal")

