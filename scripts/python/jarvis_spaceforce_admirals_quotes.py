#!/usr/bin/env python3
"""
JARVIS Spaceforce Admirals Quotes

Adding the two best admirals' quotes to the galaxy soup:
- "Make it so" - Captain Jean-Luc Picard (Star Trek)
- "So say we all" - Admiral William Adama (Battlestar Galactica)

@JARVIS @PICARD @ADAMA @SPACEFORCE @NAVY @MARINES @MAKE_IT_SO @SO_SAY_WE_ALL
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

logger = get_logger("SpaceforceAdmiralsQuotes")


class AdmiralRank(Enum):
    """Admiral ranks"""
    CAPTAIN = "CAPTAIN"
    ADMIRAL = "ADMIRAL"
    COMMANDER = "COMMANDER"


@dataclass
class AdmiralQuote:
    """A quote from a spaceforce admiral"""
    quote_id: str
    quote: str
    admiral: str
    series: str
    rank: AdmiralRank
    meaning: str
    infrastructure_application: str
    force_multiplier: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = self.__dict__.copy()
        data['rank'] = self.rank.value
        return data


class SpaceforceAdmiralsQuotes:
    """
    Spaceforce Admirals Quotes

    Adding the two best admirals' quotes:
    - "Make it so" - Picard
    - "So say we all" - Adama
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = self.project_root / "data" / "spaceforce_admirals"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("SpaceforceAdmiralsQuotes")

        self.quotes: List[AdmiralQuote] = []

        self.logger.info("=" * 70)
        self.logger.info("⭐ SPACEFORCE ADMIRALS QUOTES")
        self.logger.info("   Two of the three best admirals")
        self.logger.info("=" * 70)
        self.logger.info("")

    def add_admiral_quotes(self) -> List[AdmiralQuote]:
        """Add admiral quotes to the galaxy soup"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("⭐ ADDING ADMIRAL QUOTES")
        self.logger.info("=" * 70)
        self.logger.info("")

        quotes = [
            # Picard - "Make it so"
            AdmiralQuote(
                quote_id="PICARD_MAKE_IT_SO",
                quote="Make it so.",
                admiral="Captain Jean-Luc Picard",
                series="Star Trek: The Next Generation",
                rank=AdmiralRank.CAPTAIN,
                meaning="Simple, direct command. When infrastructure decisions are made, execute them with confidence and authority.",
                infrastructure_application="Infrastructure decisions require decisive action. 'Make it so' - execute infrastructure changes with confidence, authority, and precision. No hesitation, no second-guessing.",
                force_multiplier=1.0,
                metadata={
                    "character": "Picard",
                    "episode": "Multiple",
                    "philosophy": "Decisive action",
                    "tea": "Earl Grey, hot"
                }
            ),

            # Adama - "So say we all"
            AdmiralQuote(
                quote_id="ADAMA_SO_SAY_WE_ALL",
                quote="So say we all.",
                admiral="Admiral William Adama",
                series="Battlestar Galactica",
                rank=AdmiralRank.ADMIRAL,
                meaning="Unity, consensus, collective commitment. Infrastructure requires team alignment and shared commitment.",
                infrastructure_application="Infrastructure requires unity and consensus. 'So say we all' - when infrastructure decisions are made, the entire team must be aligned, committed, and unified. Collective responsibility, shared commitment.",
                force_multiplier=1.0,
                metadata={
                    "character": "Adama",
                    "episode": "Multiple",
                    "philosophy": "Unity and consensus",
                    "ship": "Battlestar Galactica"
                }
            ),

            # Picard - "Engage"
            AdmiralQuote(
                quote_id="PICARD_ENGAGE",
                quote="Engage.",
                admiral="Captain Jean-Luc Picard",
                series="Star Trek: The Next Generation",
                rank=AdmiralRank.CAPTAIN,
                meaning="Begin execution. Infrastructure deployment starts with engagement - activating systems, starting processes.",
                infrastructure_application="Infrastructure deployment begins with engagement. 'Engage' - activate systems, start processes, begin infrastructure operations. Simple command, powerful execution.",
                force_multiplier=0.98,
                metadata={
                    "character": "Picard",
                    "philosophy": "Execution",
                    "action": "Begin"
                }
            ),

            # Adama - "All of this has happened before"
            AdmiralQuote(
                quote_id="ADAMA_CYCLE",
                quote="All of this has happened before, and all of this will happen again.",
                admiral="Admiral William Adama",
                series="Battlestar Galactica",
                rank=AdmiralRank.ADMIRAL,
                meaning="Patterns repeat. Infrastructure problems, solutions, and patterns cycle. Learn from history.",
                infrastructure_application="Infrastructure patterns repeat. Learn from infrastructure history - problems, solutions, and patterns cycle. Understanding these cycles helps prevent repeating mistakes and leverage proven solutions.",
                force_multiplier=0.95,
                metadata={
                    "character": "Adama",
                    "philosophy": "Cyclical patterns",
                    "theme": "History repeats"
                }
            ),

            # Picard - "There are four lights"
            AdmiralQuote(
                quote_id="PICARD_FOUR_LIGHTS",
                quote="There are four lights!",
                admiral="Captain Jean-Luc Picard",
                series="Star Trek: The Next Generation",
                rank=AdmiralRank.CAPTAIN,
                meaning="Truth and reality cannot be denied, even under extreme pressure. Infrastructure truth must be maintained.",
                infrastructure_application="Infrastructure truth must be maintained, even under pressure. 'There are four lights' - reality is reality, truth is truth. Don't let pressure, complexity, or manipulation distort infrastructure reality.",
                force_multiplier=0.97,
                metadata={
                    "character": "Picard",
                    "episode": "Chain of Command",
                    "philosophy": "Truth and reality",
                    "resistance": "Extreme"
                }
            ),

            # Adama - "Frak"
            AdmiralQuote(
                quote_id="ADAMA_FRAK",
                quote="Frak.",
                admiral="Admiral William Adama",
                series="Battlestar Galactica",
                rank=AdmiralRank.ADMIRAL,
                meaning="Sometimes infrastructure fails. Acknowledge it, deal with it, move forward.",
                infrastructure_application="Infrastructure failures happen. 'Frak' - acknowledge the failure, deal with it directly, move forward. No sugar-coating, no denial. Face infrastructure problems head-on.",
                force_multiplier=0.90,
                metadata={
                    "character": "Adama",
                    "philosophy": "Direct acknowledgment",
                    "language": "Colonial"
                }
            ),

            # Picard - "The line must be drawn here"
            AdmiralQuote(
                quote_id="PICARD_LINE",
                quote="The line must be drawn here! This far, no further!",
                admiral="Captain Jean-Luc Picard",
                series="Star Trek: First Contact",
                rank=AdmiralRank.CAPTAIN,
                meaning="Infrastructure has boundaries. Some things cannot be compromised. Draw the line.",
                infrastructure_application="Infrastructure has boundaries. 'The line must be drawn here' - some infrastructure principles cannot be compromised. Security, reliability, integrity - these are non-negotiable. Draw the line and hold it.",
                force_multiplier=0.99,
                metadata={
                    "character": "Picard",
                    "movie": "First Contact",
                    "philosophy": "Boundaries and principles",
                    "determination": "Absolute"
                }
            ),

            # Adama - "Sometimes you have to roll the hard six"
            AdmiralQuote(
                quote_id="ADAMA_HARD_SIX",
                quote="Sometimes you have to roll the hard six.",
                admiral="Admiral William Adama",
                series="Battlestar Galactica",
                rank=AdmiralRank.ADMIRAL,
                meaning="Sometimes infrastructure requires difficult decisions, calculated risks, and hard choices.",
                infrastructure_application="Infrastructure sometimes requires difficult decisions. 'Roll the hard six' - make the hard choice, take the calculated risk, do what's necessary even when it's difficult. Infrastructure leadership requires courage.",
                force_multiplier=0.96,
                metadata={
                    "character": "Adama",
                    "philosophy": "Hard decisions",
                    "gambling": "Calculated risk"
                }
            ),

            # Picard - "The first duty"
            AdmiralQuote(
                quote_id="PICARD_FIRST_DUTY",
                quote="The first duty of every Starfleet officer is to the truth, whether it's scientific truth or historical truth or personal truth!",
                admiral="Captain Jean-Luc Picard",
                series="Star Trek: The Next Generation",
                rank=AdmiralRank.CAPTAIN,
                meaning="Truth is the foundation. Infrastructure must be built on truth - accurate data, honest assessment, real understanding.",
                infrastructure_application="Infrastructure must be built on truth. 'The first duty is to the truth' - accurate data, honest assessment, real understanding. Infrastructure built on falsehoods, assumptions, or lies will fail. Truth is the foundation.",
                force_multiplier=1.0,
                metadata={
                    "character": "Picard",
                    "episode": "The First Duty",
                    "philosophy": "Truth as foundation",
                    "duty": "Primary"
                }
            ),

            # Adama - "We're at war"
            AdmiralQuote(
                quote_id="ADAMA_WAR",
                quote="We're at war. You don't get to bring your personal problems to work.",
                admiral="Admiral William Adama",
                series="Battlestar Galactica",
                rank=AdmiralRank.ADMIRAL,
                meaning="Infrastructure is critical. When infrastructure is under threat, focus is essential. Personal issues cannot interfere.",
                infrastructure_application="Infrastructure is critical. When infrastructure is under threat (security breach, system failure, attack), focus is essential. 'We're at war' - infrastructure requires discipline, focus, and commitment. Personal issues cannot interfere with infrastructure protection.",
                force_multiplier=0.98,
                metadata={
                    "character": "Adama",
                    "philosophy": "Focus and discipline",
                    "context": "War"
                }
            )
        ]

        self.quotes = quotes

        for quote in quotes:
            self.logger.info(f"   ⭐ '{quote.quote}'")
            self.logger.info(f"      Admiral: {quote.admiral}")
            self.logger.info(f"      Series: {quote.series}")
            self.logger.info(f"      Force Multiplier: {quote.force_multiplier:.2f}")
            self.logger.info("")

        self.logger.info("=" * 70)
        self.logger.info(f"✅ ADDED {len(quotes)} ADMIRAL QUOTES")
        self.logger.info("=" * 70)
        self.logger.info("")

        return quotes

    def create_admirals_tribute(self) -> Dict[str, Any]:
        try:
            """Create tribute to the two best admirals"""
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("⭐ CREATING ADMIRALS TRIBUTE")
            self.logger.info("=" * 70)
            self.logger.info("")

            quotes = self.add_admiral_quotes()

            # Separate Picard and Adama quotes
            picard_quotes = [q for q in quotes if "Picard" in q.admiral]
            adama_quotes = [q for q in quotes if "Adama" in q.admiral]

            # Calculate statistics
            total_quotes = len(quotes)
            picard_count = len(picard_quotes)
            adama_count = len(adama_quotes)
            avg_force_multiplier = sum(q.force_multiplier for q in quotes) / len(quotes) if quotes else 0

            # The two signature quotes
            make_it_so = [q for q in quotes if q.quote_id == "PICARD_MAKE_IT_SO"][0]
            so_say_we_all = [q for q in quotes if q.quote_id == "ADAMA_SO_SAY_WE_ALL"][0]

            tribute = {
                "tribute_id": f"spaceforce_admirals_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "title": "Spaceforce Admirals Tribute - Two of the Three Best",
                "signature_quotes": {
                    "make_it_so": {
                        "quote": make_it_so.quote,
                        "admiral": make_it_so.admiral,
                        "series": make_it_so.series,
                        "meaning": make_it_so.meaning,
                        "infrastructure_application": make_it_so.infrastructure_application,
                        "force_multiplier": make_it_so.force_multiplier
                    },
                    "so_say_we_all": {
                        "quote": so_say_we_all.quote,
                        "admiral": so_say_we_all.admiral,
                        "series": so_say_we_all.series,
                        "meaning": so_say_we_all.meaning,
                        "infrastructure_application": so_say_we_all.infrastructure_application,
                        "force_multiplier": so_say_we_all.force_multiplier
                    }
                },
                "statistics": {
                    "total_quotes": total_quotes,
                    "picard_quotes": picard_count,
                    "adama_quotes": adama_count,
                    "average_force_multiplier": avg_force_multiplier
                },
                "admirals": {
                    "picard": {
                        "name": "Captain Jean-Luc Picard",
                        "series": "Star Trek: The Next Generation",
                        "rank": "Captain",
                        "quotes": [q.to_dict() for q in picard_quotes],
                        "philosophy": "Decisive action, truth, boundaries, engagement"
                    },
                    "adama": {
                        "name": "Admiral William Adama",
                        "series": "Battlestar Galactica",
                        "rank": "Admiral",
                        "quotes": [q.to_dict() for q in adama_quotes],
                        "philosophy": "Unity, consensus, hard decisions, focus"
                    }
                },
                "all_quotes": {
                    quote.quote_id: quote.to_dict() for quote in quotes
                },
                "galaxy_soup_status": {
                    "star_wars": "Added",
                    "star_trek": "Added (Enhanced with Picard)",
                    "battlestar_galactica": "Added (Enhanced with Adama)",
                    "the_expanse": "Added",
                    "the_matrix": "Added",
                    "inception": "Added",
                    "hhgttg": "Added",
                    "amazon_audible": "Added",
                    "admirals": "Added - Two of the Three Best",
                    "stir_status": "PERFECTLY STIRRED WITH ADMIRAL COMMAND"
                }
            }

            # Save tribute
            tribute_file = self.data_dir / f"spaceforce_admirals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(tribute_file, 'w', encoding='utf-8') as f:
                json.dump(tribute, f, indent=2, default=str)

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📊 ADMIRALS TRIBUTE STATISTICS")
            self.logger.info("=" * 70)
            self.logger.info(f"   Total Quotes: {total_quotes}")
            self.logger.info(f"   Picard Quotes: {picard_count}")
            self.logger.info(f"   Adama Quotes: {adama_count}")
            self.logger.info(f"   Average Force Multiplier: {avg_force_multiplier:.2f}")
            self.logger.info("")
            self.logger.info("⭐ SIGNATURE QUOTES:")
            self.logger.info(f"   Picard: '{make_it_so.quote}'")
            self.logger.info(f"   Adama: '{so_say_we_all.quote}'")
            self.logger.info("")
            self.logger.info("✅ ADMIRALS TRIBUTE COMPLETE!")
            self.logger.info("")
            self.logger.info(f"✅ Tribute saved: {tribute_file.name}")
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("✅ SPACEFORCE ADMIRALS TRIBUTE - TWO OF THE THREE BEST")
            self.logger.info("=" * 70)
            self.logger.info("")

            return tribute


        except Exception as e:
            self.logger.error(f"Error in create_admirals_tribute: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    admirals = SpaceforceAdmiralsQuotes(project_root)

    # Create admirals tribute
    tribute = admirals.create_admirals_tribute()

    print("")
    print("=" * 70)
    print("⭐ SPACEFORCE ADMIRALS TRIBUTE")
    print("=" * 70)
    print(f"✅ Tribute ID: {tribute['tribute_id']}")
    print(f"✅ Total Quotes: {tribute['statistics']['total_quotes']}")
    print(f"✅ Picard Quotes: {tribute['statistics']['picard_quotes']}")
    print(f"✅ Adama Quotes: {tribute['statistics']['adama_quotes']}")
    print("")
    print("⭐ SIGNATURE QUOTES:")
    print(f"   Picard: '{tribute['signature_quotes']['make_it_so']['quote']}'")
    print(f"   Adama: '{tribute['signature_quotes']['so_say_we_all']['quote']}'")
    print("")
    print("⭐ INFRASTRUCTURE APPLICATION:")
    print(f"   Picard: {tribute['signature_quotes']['make_it_so']['infrastructure_application'][:100]}...")
    print(f"   Adama: {tribute['signature_quotes']['so_say_we_all']['infrastructure_application'][:100]}...")
    print("")
    print("=" * 70)
    print("✅ 'MAKE IT SO' AND 'SO SAY WE ALL' - ADMIRALS HONORED!")
    print("=" * 70)


if __name__ == "__main__":


    main()