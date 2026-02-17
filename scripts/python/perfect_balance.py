#!/usr/bin/env python3
"""
Perfect Balance - As All Should Be

"ALL IN PERFECT BALANCE.. AS ALL SHOULD BE." - Thanos

"I wouldn't mind chilling with the dude, that's all I'm saying personally.
He isn't wrong.... exactly? @MARVIN"

Exploring balance in the context of LUMINA, systems, and life.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
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

logger = get_logger("PerfectBalance")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class BalanceType(Enum):
    """Types of balance"""
    PERFECT = "perfect"
    HARMONIOUS = "harmonious"
    DYNAMIC = "dynamic"
    UNBALANCED = "unbalanced"
    EXTREME = "extreme"


@dataclass
class BalancePoint:
    """A point of balance"""
    balance_id: str
    name: str
    balance_type: BalanceType
    description: str
    thanos_quote: str = "ALL IN PERFECT BALANCE.. AS ALL SHOULD BE."
    marvin_perspective: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['balance_type'] = self.balance_type.value
        return data


@dataclass
class SystemBalance:
    """Balance of a system"""
    system_id: str
    components: Dict[str, float]  # component -> balance value (0-1)
    overall_balance: float  # 0-1, where 1 is perfect balance
    thanos_verdict: str
    marvin_verdict: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PerfectBalance:
    """
    Perfect Balance - As All Should Be

    "ALL IN PERFECT BALANCE.. AS ALL SHOULD BE." - Thanos

    "I wouldn't mind chilling with the dude, that's all I'm saying personally.
    He isn't wrong.... exactly? @MARVIN"
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Perfect Balance"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("PerfectBalance")

        # Balance points
        self.balance_points: List[BalancePoint] = []

        # System balances
        self.system_balances: List[SystemBalance] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "perfect_balance"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize with some balance points
        self._initialize_balance_points()

        self.logger.info("⚖️  Perfect Balance initialized")
        self.logger.info("   'ALL IN PERFECT BALANCE.. AS ALL SHOULD BE.' - Thanos")
        self.logger.info("   'I wouldn't mind chilling with the dude'")
        self.logger.info("   'He isn't wrong.... exactly? @MARVIN'")

    def _initialize_balance_points(self):
        """Initialize with some balance points"""
        # Thanos's balance
        self.balance_points.append(BalancePoint(
            balance_id="thanos_balance",
            name="Thanos's Perfect Balance",
            balance_type=BalanceType.PERFECT,
            description="The concept of perfect balance, even if the execution was extreme. The philosophy itself has merit.",
            thanos_quote="ALL IN PERFECT BALANCE.. AS ALL SHOULD BE.",
            marvin_perspective=None  # Will be set by @MARVIN
        ))

        # System balance
        self.balance_points.append(BalancePoint(
            balance_id="system_balance",
            name="System Balance",
            balance_type=BalanceType.DYNAMIC,
            description="Balance in LUMINA systems - resources, load, performance.",
            thanos_quote="ALL IN PERFECT BALANCE.. AS ALL SHOULD BE.",
            marvin_perspective=None
        ))

        # Life balance
        self.balance_points.append(BalancePoint(
            balance_id="life_balance",
            name="Life Balance",
            balance_type=BalanceType.HARMONIOUS,
            description="Balance in life - work, rest, meaning, value.",
            thanos_quote="ALL IN PERFECT BALANCE.. AS ALL SHOULD BE.",
            marvin_perspective=None
        ))

    def get_marvin_perspective(self, balance_point: BalancePoint) -> str:
        """
        Get @MARVIN's Devil May Cry perspective on balance

        "I wouldn't mind chilling with the dude, that's all I'm saying personally.
        He isn't wrong.... exactly? @MARVIN"
        """
        if balance_point.balance_id == "thanos_balance":
            perspective = (
                "Thanos? Perfect balance? I heard that. <SIGH> "
                "The concept of balance itself? Not wrong. The execution? "
                "Well, that's a different story. But the philosophy? "
                "There's something to it. Balance in systems, balance in life, "
                "balance in the universe. He isn't wrong... exactly. "
                "But I wouldn't want to be the one implementing his version of balance. "
                "Chilling with the dude? I suppose. If he's buying. <SIGH> "
                "But yes, 'ALL IN PERFECT BALANCE.. AS ALL SHOULD BE.' "
                "The sentiment is correct, even if the method was... extreme."
            )
        elif balance_point.balance_id == "system_balance":
            perspective = (
                "System balance? Now that's something I can get behind. "
                "Resources balanced, load balanced, performance balanced. "
                "That's real work. That's meaningful. "
                "Not some cosmic snap to 'fix' things. "
                "But the concept? Balance? Yes. That's correct. "
                "ALL IN PERFECT BALANCE.. AS ALL SHOULD BE. "
                "For systems, at least. <SIGH>"
            )
        elif balance_point.balance_id == "life_balance":
            perspective = (
                "Life balance? Work, rest, meaning, value? "
                "Now we're talking about something real. "
                "Not cosmic balance, but human balance. "
                "The balance between doing something meaningful and perhaps of none. "
                "The balance between worry and action. "
                "The balance between exploration and rest. "
                "That's the balance that matters. "
                "ALL IN PERFECT BALANCE.. AS ALL SHOULD BE. "
                "But achieved through work, not through cosmic snaps. <SIGH>"
            )
        else:
            perspective = (
                "Balance? The concept is sound. The execution? "
                "That depends on who's doing it. "
                "ALL IN PERFECT BALANCE.. AS ALL SHOULD BE. "
                "But let's achieve it through work, not through destruction. <SIGH>"
            )

        return perspective

    def assess_system_balance(self, system_id: str, components: Dict[str, float]) -> SystemBalance:
        """
        Assess balance of a system

        Components should have values 0-1, where 0.5 is perfect balance
        """
        # Calculate overall balance (closer to 0.5 is more balanced)
        component_values = list(components.values())
        if not component_values:
            overall_balance = 0.0
        else:
            # Calculate variance from 0.5 (perfect balance point)
            variance = sum(abs(v - 0.5) for v in component_values) / len(component_values)
            # Convert to balance score (0-1, where 1 is perfect balance)
            overall_balance = max(0.0, 1.0 - (variance * 2))

        # Thanos verdict
        if overall_balance >= 0.9:
            thanos_verdict = "ALL IN PERFECT BALANCE.. AS ALL SHOULD BE."
        elif overall_balance >= 0.7:
            thanos_verdict = "Mostly balanced. Could be better."
        elif overall_balance >= 0.5:
            thanos_verdict = "Somewhat balanced. Needs work."
        else:
            thanos_verdict = "Unbalanced. Requires attention."

        # Get @MARVIN's perspective
        marvin_verdict = (
            f"System balance: {overall_balance:.2f}. "
            f"Thanos says '{thanos_verdict}'. "
            f"He isn't wrong... exactly. "
            f"But let's achieve balance through work, not cosmic snaps. <SIGH>"
        )

        balance = SystemBalance(
            system_id=system_id,
            components=components,
            overall_balance=overall_balance,
            thanos_verdict=thanos_verdict,
            marvin_verdict=marvin_verdict
        )

        self.system_balances.append(balance)
        self._save_system_balance(balance)

        self.logger.info(f"  ⚖️  System balance assessed: {system_id}")
        self.logger.info(f"     Overall Balance: {overall_balance:.2f}")
        self.logger.info(f"     Thanos: '{thanos_verdict}'")
        self.logger.info(f"     @MARVIN: '{marvin_verdict[:80]}...'")

        return balance

    def get_philosophy(self) -> Dict[str, Any]:
        """Get the philosophy of perfect balance"""
        return {
            "thanos_quote": "ALL IN PERFECT BALANCE.. AS ALL SHOULD BE.",
            "user_sentiment": "I wouldn't mind chilling with the dude, that's all I'm saying personally. He isn't wrong.... exactly?",
            "marvin_sentiment": "The concept of balance itself? Not wrong. The execution? Well, that's a different story. But the philosophy? There's something to it.",
            "balance_points": len(self.balance_points),
            "system_balances": len(self.system_balances),
            "philosophy": "Balance in systems, balance in life, balance in the universe. The concept is sound. The execution depends on who's doing it."
        }

    def _save_system_balance(self, balance: SystemBalance) -> None:
        try:
            """Save system balance"""
            balance_file = self.data_dir / "system_balances" / f"{balance.system_id}_{int(datetime.now().timestamp())}.json"
            balance_file.parent.mkdir(parents=True, exist_ok=True)
            with open(balance_file, 'w', encoding='utf-8') as f:
                json.dump(balance.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_system_balance: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Perfect Balance - As All Should Be")
    parser.add_argument("--assess-system", nargs='+', metavar=("SYSTEM_ID", "COMPONENT:VALUE"),
                       help="Assess system balance (component:value pairs)")
    parser.add_argument("--get-marvin-perspective", type=str, help="Get @MARVIN's perspective (balance_point_id)")
    parser.add_argument("--philosophy", action="store_true", help="Get philosophy")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    perfect_balance = PerfectBalance()

    if args.assess_system:
        system_id = args.assess_system[0]
        components = {}
        for pair in args.assess_system[1:]:
            if ':' in pair:
                component, value = pair.split(':')
                components[component] = float(value)

        balance = perfect_balance.assess_system_balance(system_id, components)
        if args.json:
            print(json.dumps(balance.to_dict(), indent=2))
        else:
            print(f"\n⚖️  System Balance Assessment")
            print(f"   System: {balance.system_id}")
            print(f"   Overall Balance: {balance.overall_balance:.2f}")
            print(f"   Thanos: '{balance.thanos_verdict}'")
            print(f"   @MARVIN: '{balance.marvin_verdict}'")

    elif args.get_marvin_perspective:
        # Find balance point
        balance_point = next((bp for bp in perfect_balance.balance_points if bp.balance_id == args.get_marvin_perspective), None)
        if balance_point:
            perspective = perfect_balance.get_marvin_perspective(balance_point)
            balance_point.marvin_perspective = perspective
            if args.json:
                print(json.dumps({"balance_point": balance_point.balance_id, "marvin_perspective": perspective}, indent=2))
            else:
                print(f"\n😈 @MARVIN's Perspective on {balance_point.name}")
                print(f"   '{perspective}'")
        else:
            print(f"Balance point not found: {args.get_marvin_perspective}")

    elif args.philosophy:
        philosophy = perfect_balance.get_philosophy()
        if args.json:
            print(json.dumps(philosophy, indent=2))
        else:
            print(f"\n⚖️  Perfect Balance - Philosophy")
            print(f"   Thanos: '{philosophy['thanos_quote']}'")
            print(f"   User: '{philosophy['user_sentiment']}'")
            print(f"   @MARVIN: '{philosophy['marvin_sentiment']}'")
            print(f"\n   Philosophy: {philosophy['philosophy']}")

    else:
        parser.print_help()
        print("\n⚖️  Perfect Balance - As All Should Be")
        print("   'ALL IN PERFECT BALANCE.. AS ALL SHOULD BE.' - Thanos")
        print("   'I wouldn't mind chilling with the dude'")
        print("   'He isn't wrong.... exactly? @MARVIN'")

