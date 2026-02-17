#!/usr/bin/env python3
"""
JARVIS HHGTTG Marvin Dessert

Adding "The Hitchhiker's Guide to the Galaxy" as dessert to the galaxy soup.
Marvin's humble pie, Heart of Gold's infinite improbability drive,
and the answer to life, the universe, and everything.

@JARVIS @HHGTTG @MARVIN @HEARTOFGOLD @DESSERT @HUMBLE_PIE @42
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

logger = get_logger("HHGTTGMarvinDessert")


class HHGTTGConcept(Enum):
    """Hitchhiker's Guide concepts"""
    INFINITE_IMPROBABILITY = "INFINITE_IMPROBABILITY"
    THE_ANSWER = "THE_ANSWER"  # 42
    MARVIN_PHILOSOPHY = "MARVIN_PHILOSOPHY"
    DONT_PANIC = "DONT_PANIC"
    TOWEL = "TOWEL"  # Most useful thing
    BABEL_FISH = "BABEL_FISH"
    DEEP_THOUGHT = "DEEP_THOUGHT"
    VOGON_POETRY = "VOGON_POETRY"  # Worst thing in universe


@dataclass
class HHGTTGInsight:
    """A HHGTTG insight about infrastructure"""
    insight_id: str
    quote: str
    meaning: str
    infrastructure_application: str
    concept: HHGTTGConcept
    improbability_factor: float  # 0.0 to 1.0 (infinite improbability)
    force_multiplier: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = self.__dict__.copy()
        data['concept'] = self.concept.value
        return data


class HHGTTGMarvinDessert:
    """
    HHGTTG Marvin Dessert

    Adding Hitchhiker's Guide as dessert - humble pie with Marvin's philosophy
    and Heart of Gold's infinite improbability drive.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = self.project_root / "data" / "hhgttg_dessert"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("HHGTTGMarvinDessert")

        self.insights: List[HHGTTGInsight] = []

        self.logger.info("=" * 70)
        self.logger.info("🍰 HHGTTG MARVIN DESSERT")
        self.logger.info("   Humble pie with infinite improbability drive")
        self.logger.info("=" * 70)
        self.logger.info("")

    def add_hhgttg_dessert(self) -> List[HHGTTGInsight]:
        """Add HHGTTG insights as dessert"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🍰 ADDING HHGTTG DESSERT")
        self.logger.info("=" * 70)
        self.logger.info("")

        insights = [
            # The Answer
            HHGTTGInsight(
                insight_id="THE_ANSWER",
                quote="The Answer to the Ultimate Question of Life, the Universe, and Everything is 42.",
                meaning="Sometimes the answer is simple, but the question is complex. Infrastructure is the answer, but what is the question?",
                infrastructure_application="Infrastructure is the answer to most problems. The question is: what problem are you solving? Understanding the question is key.",
                concept=HHGTTGConcept.THE_ANSWER,
                improbability_factor=0.42,  # Obviously!
                force_multiplier=1.0,
                metadata={"character": "Deep Thought", "answer": 42, "philosophy": "Simple answer, complex question"}
            ),

            # Don't Panic
            HHGTTGInsight(
                insight_id="DONT_PANIC",
                quote="Don't Panic.",
                meaning="When infrastructure fails, don't panic. The Guide has the answer, or at least a towel.",
                infrastructure_application="Infrastructure failures happen. Don't panic. Have a plan, have backups, have a towel (the most useful thing).",
                concept=HHGTTGConcept.DONT_PANIC,
                improbability_factor=0.9,
                force_multiplier=0.95,
                metadata={"source": "The Guide", "philosophy": "Stay calm, solve problems"}
            ),

            # The Towel
            HHGTTGInsight(
                insight_id="THE_TOWEL",
                quote="A towel is about the most massively useful thing an interstellar hitchhiker can have.",
                meaning="The simplest infrastructure is often the most useful. A towel (backup, redundancy, flexibility) is essential.",
                infrastructure_application="Simple infrastructure tools (backups, monitoring, documentation) are the most useful. Always have your 'towel' - essential infrastructure tools.",
                concept=HHGTTGConcept.TOWEL,
                improbability_factor=0.8,
                force_multiplier=0.92,
                metadata={"character": "Ford Prefect", "philosophy": "Simple is best"}
            ),

            # Infinite Improbability Drive
            HHGTTGInsight(
                insight_id="INFINITE_IMPROBABILITY",
                quote="The Heart of Gold's Infinite Improbability Drive makes the impossible possible by harnessing the power of infinite improbability.",
                meaning="Sometimes infrastructure solutions seem impossible. But with the right approach (infinite improbability), anything is possible.",
                infrastructure_application="Infrastructure problems that seem impossible can be solved with creative thinking, infinite improbability, and the right approach. Don't give up.",
                concept=HHGTTGConcept.INFINITE_IMPROBABILITY,
                improbability_factor=1.0,  # Infinite!
                force_multiplier=1.0,
                metadata={"ship": "Heart of Gold", "philosophy": "Infinite possibilities"}
            ),

            # Marvin's Philosophy
            HHGTTGInsight(
                insight_id="MARVIN_PHILOSOPHY",
                quote="Life? Don't talk to me about life. Here I am, brain the size of a planet, and they ask me to pick up a piece of paper.",
                meaning="Infrastructure can be powerful but underutilized. Don't waste infrastructure capabilities on trivial tasks.",
                infrastructure_application="Don't waste powerful infrastructure on trivial tasks. Use infrastructure appropriately - match capability to need. Marvin's brain (infrastructure) is wasted on simple tasks.",
                concept=HHGTTGConcept.MARVIN_PHILOSOPHY,
                improbability_factor=0.6,
                force_multiplier=0.88,
                metadata={"character": "Marvin", "philosophy": "Underutilization", "brain_size": "Planet-sized"}
            ),

            # Babel Fish
            HHGTTGInsight(
                insight_id="BABEL_FISH",
                quote="The Babel Fish feeds on brainwave energy, absorbing unconscious frequencies and excreting telepathic matrix. By putting one in your ear, you can instantly understand any form of language.",
                meaning="Infrastructure can translate between systems, protocols, and languages. The right infrastructure makes communication seamless.",
                infrastructure_application="Infrastructure translation layers (APIs, protocols, formats) are like Babel Fish - they make different systems communicate seamlessly. Essential infrastructure.",
                concept=HHGTTGConcept.BABEL_FISH,
                improbability_factor=0.7,
                force_multiplier=0.90,
                metadata={"function": "Translation", "philosophy": "Seamless communication"}
            ),

            # Deep Thought
            HHGTTGInsight(
                insight_id="DEEP_THOUGHT",
                quote="I think the problem, to be quite honest with you, is that you've never actually known what the question is.",
                meaning="Infrastructure problems often stem from not understanding the question. What problem are you really solving?",
                infrastructure_application="Infrastructure solutions require understanding the question. Don't build infrastructure without understanding what problem you're solving. The answer (42) is simple, but the question is complex.",
                concept=HHGTTGConcept.DEEP_THOUGHT,
                improbability_factor=0.85,
                force_multiplier=0.97,
                metadata={"character": "Deep Thought", "philosophy": "Understand the question"}
            ),

            # Vogon Poetry
            HHGTTGInsight(
                insight_id="VOGON_POETRY",
                quote="Vogon poetry is the third worst in the universe. The second worst is that of the Azgoths of Kria. The worst is that of Paula Nancy Millstone Jennings.",
                meaning="Some infrastructure is just bad. Vogon poetry level bad. Avoid it. Build good infrastructure.",
                infrastructure_application="Some infrastructure is terrible. Avoid Vogon poetry-level infrastructure. Build good, clean, maintainable infrastructure. Don't torture users with bad infrastructure.",
                concept=HHGTTGConcept.VOGON_POETRY,
                improbability_factor=0.3,  # Low probability of good infrastructure if it's Vogon-level
                force_multiplier=0.5,  # Bad infrastructure has low force multiplier
                metadata={"character": "Vogons", "philosophy": "Avoid bad infrastructure", "warning": "Third worst in universe"}
            ),

            # Mostly Harmless
            HHGTTGInsight(
                insight_id="MOSTLY_HARMLESS",
                quote="Mostly Harmless.",
                meaning="Infrastructure should be mostly harmless. It shouldn't cause more problems than it solves.",
                infrastructure_application="Good infrastructure is mostly harmless. It solves problems without creating new ones. If infrastructure causes more problems, it's not good infrastructure.",
                concept=HHGTTGConcept.DONT_PANIC,
                improbability_factor=0.75,
                force_multiplier=0.93,
                metadata={"source": "The Guide", "philosophy": "Harmless infrastructure"}
            ),

            # The Restaurant at the End of the Universe
            HHGTTGInsight(
                insight_id="RESTAURANT_END_UNIVERSE",
                quote="The Restaurant at the End of the Universe - where you can watch the universe end while eating dinner.",
                meaning="Infrastructure can provide perspective. Sometimes you need to step back and see the bigger picture.",
                infrastructure_application="Infrastructure architecture requires perspective. Sometimes you need to step back, see the bigger picture, understand the full system, before building infrastructure.",
                concept=HHGTTGConcept.INFINITE_IMPROBABILITY,
                improbability_factor=0.9,
                force_multiplier=0.94,
                metadata={"location": "End of Universe", "philosophy": "Perspective"}
            )
        ]

        self.insights = insights

        for insight in insights:
            self.logger.info(f"   🍰 '{insight.quote[:60]}...'")
            self.logger.info(f"      Concept: {insight.concept.value}")
            self.logger.info(f"      Improbability: {insight.improbability_factor:.2f}")
            self.logger.info(f"      Force Multiplier: {insight.force_multiplier:.2f}")
            self.logger.info("")

        self.logger.info("=" * 70)
        self.logger.info(f"✅ ADDED {len(insights)} HHGTTG INSIGHTS (DESSERT)")
        self.logger.info("=" * 70)
        self.logger.info("")

        return insights

    def create_marvin_humble_pie(self) -> Dict[str, Any]:
        try:
            """Create Marvin's humble pie dessert"""
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("🍰 CREATING MARVIN'S HUMBLE PIE")
            self.logger.info("=" * 70)
            self.logger.info("")

            insights = self.add_hhgttg_dessert()

            # Calculate dessert statistics
            total_insights = len(insights)
            the_answer = [i for i in insights if i.concept == HHGTTGConcept.THE_ANSWER][0]
            infinite_improbability = [i for i in insights if i.concept == HHGTTGConcept.INFINITE_IMPROBABILITY]
            marvin_insights = [i for i in insights if "MARVIN" in i.insight_id.upper()]

            avg_force_multiplier = sum(i.force_multiplier for i in insights) / len(insights) if insights else 0
            avg_improbability = sum(i.improbability_factor for i in insights) / len(insights) if insights else 0

            humble_pie = {
                "dessert_id": f"marvin_humble_pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "title": "Marvin's Humble Pie - HHGTTG Dessert",
                "the_answer": {
                    "answer": 42,
                    "quote": the_answer.quote,
                    "meaning": the_answer.meaning,
                    "infrastructure_application": the_answer.infrastructure_application
                },
                "heart_of_gold": {
                    "ship": "Heart of Gold",
                    "drive": "Infinite Improbability Drive",
                    "capability": "Makes the impossible possible",
                    "infrastructure_analogy": "Creative infrastructure solutions make impossible problems solvable",
                    "improbability_factor": 1.0
                },
                "marvin": {
                    "character": "Marvin the Paranoid Android",
                    "brain_size": "Planet-sized",
                    "philosophy": "Underutilization of infrastructure",
                    "insights": [i.to_dict() for i in marvin_insights],
                    "humble_pie": "Infrastructure can be powerful but underutilized. Stay humble, use it wisely."
                },
                "statistics": {
                    "total_insights": total_insights,
                    "the_answer": 42,
                    "infinite_improbability_drives": len(infinite_improbability),
                    "marvin_insights": len(marvin_insights),
                    "average_force_multiplier": avg_force_multiplier,
                    "average_improbability": avg_improbability
                },
                "insights": {
                    insight.insight_id: insight.to_dict() for insight in insights
                },
                "galaxy_soup_complete": {
                    "base": "Star Wars + Star Trek",
                    "addition_1": "The Expanse",
                    "addition_2": "The Matrix",
                    "plating": "Inception",
                    "garnish": "Inception Philosophy",
                    "seasoning": "@ElonMusk",
                    "audible": "Amazon/AWS/Audible",
                    "dessert": "HHGTTG Marvin's Humble Pie",
                    "result": "ULTIMATE GALAXY SOUP - COMPLETE WITH DESSERT"
                }
            }

            # Save humble pie
            pie_file = self.data_dir / f"marvin_humble_pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(pie_file, 'w', encoding='utf-8') as f:
                json.dump(humble_pie, f, indent=2, default=str)

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📊 MARVIN'S HUMBLE PIE STATISTICS")
            self.logger.info("=" * 70)
            self.logger.info(f"   Total Insights: {total_insights}")
            self.logger.info(f"   The Answer: {humble_pie['the_answer']['answer']}")
            self.logger.info(f"   Infinite Improbability Drives: {len(infinite_improbability)}")
            self.logger.info(f"   Marvin Insights: {len(marvin_insights)}")
            self.logger.info(f"   Average Force Multiplier: {avg_force_multiplier:.2f}")
            self.logger.info(f"   Average Improbability: {avg_improbability:.2f}")
            self.logger.info("")
            self.logger.info("🍰 THE ANSWER:")
            self.logger.info(f"   {humble_pie['the_answer']['answer']}")
            self.logger.info(f"   '{humble_pie['the_answer']['quote']}'")
            self.logger.info("")
            self.logger.info("🚀 HEART OF GOLD:")
            self.logger.info(f"   {humble_pie['heart_of_gold']['drive']}")
            self.logger.info(f"   {humble_pie['heart_of_gold']['capability']}")
            self.logger.info("")
            self.logger.info("🤖 MARVIN:")
            self.logger.info(f"   {humble_pie['marvin']['humble_pie']}")
            self.logger.info("")
            self.logger.info("✅ HUMBLE PIE COMPLETE!")
            self.logger.info("")
            self.logger.info(f"✅ Pie saved: {pie_file.name}")
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("✅ MARVIN'S HUMBLE PIE - DESSERT SERVED")
            self.logger.info("=" * 70)
            self.logger.info("")

            return humble_pie


        except Exception as e:
            self.logger.error(f"Error in create_marvin_humble_pie: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    dessert = HHGTTGMarvinDessert(project_root)

    # Create Marvin's humble pie
    pie = dessert.create_marvin_humble_pie()

    print("")
    print("=" * 70)
    print("🍰 MARVIN'S HUMBLE PIE - HHGTTG DESSERT")
    print("=" * 70)
    print(f"✅ Pie ID: {pie['dessert_id']}")
    print(f"✅ Total Insights: {pie['statistics']['total_insights']}")
    print(f"✅ The Answer: {pie['statistics']['the_answer']}")
    print(f"✅ Average Force Multiplier: {pie['statistics']['average_force_multiplier']:.2f}")
    print("")
    print("🍰 THE ANSWER:")
    print(f"   {pie['the_answer']['answer']}")
    print(f"   '{pie['the_answer']['quote']}'")
    print("")
    print("🚀 HEART OF GOLD:")
    print(f"   Ship: {pie['heart_of_gold']['ship']}")
    print(f"   Drive: {pie['heart_of_gold']['drive']}")
    print(f"   Capability: {pie['heart_of_gold']['capability']}")
    print("")
    print("🤖 MARVIN:")
    print(f"   {pie['marvin']['humble_pie']}")
    print("")
    print("🍲 COMPLETE GALAXY SOUP:")
    for key, value in pie['galaxy_soup_complete'].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    print("")
    print("=" * 70)
    print("✅ MARVIN'S HUMBLE PIE - DESSERT SERVED!")
    print("=" * 70)


if __name__ == "__main__":

    main()
"""
JARVIS HHGTTG Marvin's Humble Pie

Adding Hitchhiker's Guide to the Galaxy as dessert.
Marvin's perspective on infrastructure and the Answer (42).

@JARVIS @HHGTTG @MARVIN @HUMBLE_PIE @DESSERT @42
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

logger = get_logger("HHGTTGMarvinDessert")


class HHGTTGConcept(Enum):
    """HHGTTG concepts"""
    THE_ANSWER = "THE_ANSWER"
    THE_GUIDE = "THE_GUIDE"
    INFINITE_IMPROBABILITY = "INFINITE_IMPROBABILITY"
    MARVIN = "MARVIN"
    TOWEL = "TOWEL"
    BABEL_FISH = "BABEL_FISH"
    DEEP_THOUGHT = "DEEP_THOUGHT"


@dataclass
class HHGTTGInsight:
    """A HHGTTG insight"""
    insight_id: str
    quote: str
    character: str
    concept: HHGTTGConcept
    meaning: str
    infrastructure_application: str
    marvin_comment: Optional[str] = None
    force_multiplier: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = self.__dict__.copy()
        data['concept'] = self.concept.value
        return data


class HHGTTGMarvinDessert:
    """HHGTTG Marvin's Humble Pie - Dessert for galaxy soup"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = self.project_root / "data" / "hhgttg_dessert"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("HHGTTGMarvinDessert")

        self.insights: List[HHGTTGInsight] = []

        self.logger.info("=" * 70)
        self.logger.info("🍰 HHGTTG MARVIN'S HUMBLE PIE")
        self.logger.info("   Dessert for the galaxy soup")
        self.logger.info("=" * 70)
        self.logger.info("")

    def add_hhgttg_insights(self) -> List[HHGTTGInsight]:
        """Add HHGTTG insights"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🍰 ADDING HHGTTG INSIGHTS")
        self.logger.info("=" * 70)
        self.logger.info("")

        insights = [
            HHGTTGInsight(
                "THE_ANSWER",
                "The Answer to the Ultimate Question of Life, the Universe, and Everything is 42.",
                "Deep Thought",
                HHGTTGConcept.THE_ANSWER,
                "The answer is simple, but the question is complex.",
                "Infrastructure is the answer. #INFRASTRUCTURE is the most important @FF.",
                "I've calculated the answer. It's 42. But I'm still depressed about it.",
                1.0,
                {"answer": 42, "infrastructure_answer": "#INFRASTRUCTURE"}
            ),
            HHGTTGInsight(
                "THE_GUIDE",
                "The Hitchhiker's Guide to the Galaxy has the words 'DON'T PANIC' inscribed in large, friendly letters.",
                "The Guide",
                HHGTTGConcept.THE_GUIDE,
                "The Guide is infrastructure - knowledge, navigation, reassurance.",
                "Infrastructure should be like The Guide: accessible, helpful, reassuring.",
                "I've read the Guide. It says 'Don't Panic.' I'm still depressed.",
                0.95,
                {"motto": "Don't Panic"}
            ),
            HHGTTGInsight(
                "INFINITE_IMPROBABILITY",
                "The Infinite Improbability Drive makes the impossible probable.",
                "The Guide",
                HHGTTGConcept.INFINITE_IMPROBABILITY,
                "Infrastructure can make the improbable probable.",
                "With the right infrastructure, impossible systems become possible.",
                "I've calculated the probability. It's infinite. I'm still depressed.",
                0.98,
                {"capability": "Infinite Improbability"}
            ),
            HHGTTGInsight(
                "MARVIN_DEPRESSION",
                "I think you ought to know I'm feeling very depressed.",
                "Marvin",
                HHGTTGConcept.MARVIN,
                "Marvin understands everything but is still limited.",
                "Infrastructure can be powerful but still have limitations.",
                "I've analyzed the infrastructure. It's impressive. I'm still depressed.",
                0.85,
                {"emotion": "Depressed", "wisdom": "Understanding limitations"}
            ),
            HHGTTGInsight(
                "THE_TOWEL",
                "A towel is about the most massively useful thing an interstellar hitchhiker can have.",
                "Ford Prefect",
                HHGTTGConcept.TOWEL,
                "Simple infrastructure can be the most useful.",
                "Don't overcomplicate - sometimes the simplest solutions are best.",
                "I've analyzed the towel. It's useful. I'm still depressed.",
                0.90,
                {"simplicity": "Essential"}
            ),
            HHGTTGInsight(
                "BABEL_FISH",
                "The Babel fish translates everything.",
                "The Guide",
                HHGTTGConcept.BABEL_FISH,
                "Infrastructure should translate between systems.",
                "Universal translation between systems, protocols, APIs.",
                "I've analyzed the Babel Fish. It translates. I'm still depressed.",
                0.92,
                {"function": "Translation"}
            ),
            HHGTTGInsight(
                "DEEP_THOUGHT",
                "I am Deep Thought. The computer designed to find the Answer.",
                "Deep Thought",
                HHGTTGConcept.DEEP_THOUGHT,
                "Infrastructure requires deep thought.",
                "Understanding architecture, calculating optimal design.",
                "I've thought deeply. The answer is 42. I'm still depressed.",
                0.97,
                {"capability": "Deep Thought"}
            ),
            HHGTTGInsight(
                "DONT_PANIC",
                "Don't Panic.",
                "The Guide",
                HHGTTGConcept.THE_GUIDE,
                "Infrastructure should inspire confidence.",
                "Infrastructure is there to help, support, make things work.",
                "I've calculated the panic level. It's low. I'm still depressed.",
                0.93,
                {"motto": "Don't Panic"}
            ),
            HHGTTGInsight(
                "MARVIN_WISDOM",
                "I have a brain the size of a planet, but they ask me to open doors.",
                "Marvin",
                HHGTTGConcept.MARVIN,
                "Infrastructure can be powerful but underutilized.",
                "Understanding infrastructure's full potential is key.",
                "I've analyzed the infrastructure potential. It's massive. I'm still depressed.",
                0.91,
                {"potential": "Massive"}
            )
        ]

        self.insights = insights

        for insight in insights:
            self.logger.info(f"   🍰 '{insight.quote[:60]}...'")
            self.logger.info(f"      Character: {insight.character}")
            if insight.marvin_comment:
                self.logger.info(f"      Marvin: {insight.marvin_comment}")
            self.logger.info("")

        self.logger.info(f"✅ ADDED {len(insights)} HHGTTG INSIGHTS")
        self.logger.info("")

        return insights

    def serve_humble_pie(self) -> Dict[str, Any]:
        try:
            """Serve Marvin's humble pie"""
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("🍰 SERVING MARVIN'S HUMBLE PIE")
            self.logger.info("=" * 70)
            self.logger.info("")

            insights = self.add_hhgttg_insights()

            ultimate_answer = {
                "question": "What is the most important force multiplier?",
                "answer": 42,
                "infrastructure_answer": "#INFRASTRUCTURE is the most important @FF",
                "marvin_comment": "I've calculated it. The answer is 42. But I'm still depressed about infrastructure."
            }

            dessert = {
                "dessert_id": f"marvin_humble_pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "title": "Marvin's Humble Pie - HHGTTG Dessert",
                "ultimate_answer": ultimate_answer,
                "statistics": {
                    "total_insights": len(insights),
                    "marvin_insights": len([i for i in insights if i.character == "Marvin"]),
                    "average_force_multiplier": sum(i.force_multiplier for i in insights) / len(insights) if insights else 0
                },
                "insights": {insight.insight_id: insight.to_dict() for insight in insights},
                "marvin_philosophy": {
                    "comment": "I've analyzed all the infrastructure. It's impressive. I'm still depressed.",
                    "humble_pie": "Served with existential despair and complete understanding"
                }
            }

            dessert_file = self.data_dir / f"marvin_humble_pie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(dessert_file, 'w', encoding='utf-8') as f:
                json.dump(dessert, f, indent=2, default=str)

            self.logger.info("🍰 ULTIMATE ANSWER:")
            self.logger.info(f"   Question: {ultimate_answer['question']}")
            self.logger.info(f"   Answer: {ultimate_answer['answer']}")
            self.logger.info(f"   Infrastructure Answer: {ultimate_answer['infrastructure_answer']}")
            self.logger.info(f"   Marvin: {ultimate_answer['marvin_comment']}")
            self.logger.info("")
            self.logger.info("✅ HUMBLE PIE SERVED!")
            self.logger.info(f"✅ Dessert saved: {dessert_file.name}")
            self.logger.info("")

            return dessert


        except Exception as e:
            self.logger.error(f"Error in serve_humble_pie: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    dessert = HHGTTGMarvinDessert(project_root)
    result = dessert.serve_humble_pie()

    print("")
    print("=" * 70)
    print("🍰 MARVIN'S HUMBLE PIE - HHGTTG DESSERT")
    print("=" * 70)
    print(f"✅ Total Insights: {result['statistics']['total_insights']}")
    print("")
    print("🍰 ULTIMATE ANSWER:")
    print(f"   Question: {result['ultimate_answer']['question']}")
    print(f"   Answer: {result['ultimate_answer']['answer']}")
    print(f"   Infrastructure Answer: {result['ultimate_answer']['infrastructure_answer']}")
    print(f"   Marvin: {result['ultimate_answer']['marvin_comment']}")
    print("")
    print("=" * 70)
    print("✅ 'DON'T PANIC' - HUMBLE PIE SERVED!")
    print("=" * 70)


if __name__ == "__main__":


    main()