#!/usr/bin/env python3
"""
Short Tag Mantra Applicator

Applies short tag practices as our mantra.
Enhances as we go. Into the unknown is our destination.

Tags: #MANTRA #SHORT-TAGS #PEAK #TOYSAAC #EXPLORATION @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("ShortTagMantra")
ts_logger = get_timestamp_logger()


@dataclass
class MantraPractice:
    """A mantra practice from short tags"""
    tag: str
    name: str
    description: str
    context_weight: float
    ai_weight: float
    human_weight: float
    mantra: str
    category: str


class ShortTagMantraApplicator:
    """
    Short Tag Mantra Applicator

    Applies short tag practices as our mantra.
    Enhances as we go. Into the unknown is our destination.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Short Tag Mantra Applicator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.practices = self._load_practices()

        logger.info("🎯 Short Tag Mantra Applicator initialized")
        logger.info("   Into the unknown is our destination")
        logger.info("   Flying by the seat of our pants")
        logger.info("   Let's explore together")

    def _load_practices(self) -> Dict[str, MantraPractice]:
        """Load mantra practices from short tags"""
        practices = {}

        # #peak - PEAK Quality Standards
        practices["peak"] = MantraPractice(
            tag="#peak",
            name="PEAK Quality Standards",
            description="PEAK quality standards - highest priority",
            context_weight=1.0,
            ai_weight=0.7,
            human_weight=0.3,
            mantra="Do it in @peak fashion",
            category="quality",
        )

        # #TOYSAAC - Think Of Yourself As A Customer
        practices["toysaac"] = MantraPractice(
            tag="#TOYSAAC",
            name="Think Of Yourself As A Customer",
            description="Always consider the user's perspective",
            context_weight=0.9,
            ai_weight=0.5,
            human_weight=0.5,
            mantra="Would I want to use this?",
            category="principle",
        )

        # #bullshitmeter - Reliability & Credibility
        practices["bullshitmeter"] = MantraPractice(
            tag="#bullshitmeter",
            name="Bullshit Meter",
            description="Track claim accuracy, build credibility, filter unreliable sources",
            context_weight=0.9,
            ai_weight=0.8,
            human_weight=0.2,
            mantra="Trust but verify",
            category="quality",
        )

        # #decisioning - Decision-Making Process
        practices["decisioning"] = MantraPractice(
            tag="#decisioning",
            name="Decision-Making Process",
            description="Structured decision-making process",
            context_weight=0.8,
            ai_weight=0.6,
            human_weight=0.4,
            mantra="Think, decide, act",
            category="process",
        )

        # @v3 - Verify, Validate, Verify
        practices["v3"] = MantraPractice(
            tag="@v3",
            name="Verify, Validate, Verify",
            description="Always part of global workflow - runs before main workflow execution",
            context_weight=1.0,
            ai_weight=0.8,
            human_weight=0.2,
            mantra="Verify, Validate, Verify",
            category="system",
        )

        # @grep - Primary Pattern Search
        practices["grep"] = MantraPractice(
            tag="@grep",
            name="Primary Pattern Search",
            description="Primary pattern search tool - highest precedence",
            context_weight=1.0,
            ai_weight=0.9,
            human_weight=0.1,
            mantra="Find the pattern",
            category="tool",
        )

        # #syphon - Pattern Search (Lower Ranked)
        practices["syphon"] = MantraPractice(
            tag="#syphon",
            name="Pattern Search (Lower Ranked)",
            description="Lower ranked alias for grep - use for concept or lower priority searches",
            context_weight=0.8,
            ai_weight=0.8,
            human_weight=0.2,
            mantra="Search when needed",
            category="tool",
        )

        # #patterns - Pattern Concepts
        practices["patterns"] = MantraPractice(
            tag="#patterns",
            name="Pattern Concepts",
            description="Pattern concepts that pipe to @grep - lowest precedence",
            context_weight=0.7,
            ai_weight=0.7,
            human_weight=0.3,
            mantra="Patterns → @grep → Execute",
            category="concept",
        )

        logger.info(f"📋 Loaded {len(practices)} mantra practices")
        return practices

    def apply_mantra(self, tag: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a mantra practice to a context"""
        practice = self.practices.get(tag.lower().replace("#", "").replace("@", ""))
        if not practice:
            return {"error": f"Mantra practice not found: {tag}"}

        # Apply mantra
        result = {
            "tag": practice.tag,
            "name": practice.name,
            "mantra": practice.mantra,
            "context_weight": practice.context_weight,
            "applied": True,
            "context": context,
        }

        logger.info(f"🎯 Applied mantra: {practice.tag} - {practice.mantra}")
        return result

    def get_all_practices(self) -> Dict[str, MantraPractice]:
        """Get all mantra practices"""
        return self.practices

    def apply_peak_standards(self, action: str) -> Dict[str, Any]:
        """Apply #peak standards to an action"""
        return self.apply_mantra("#peak", {"action": action})

    def apply_toysaac(self, feature: str) -> Dict[str, Any]:
        """Apply #TOYSAAC principle to a feature"""
        return self.apply_mantra("#TOYSAAC", {"feature": feature})

    def apply_v3(self, workflow: str) -> Dict[str, Any]:
        """Apply @v3 verification to a workflow"""
        return self.apply_mantra("@v3", {"workflow": workflow})


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Short Tag Mantra Applicator")
    parser.add_argument("--list", action="store_true", help="List all mantra practices")
    parser.add_argument("--apply", type=str, help="Apply specific mantra (tag)")
    parser.add_argument("--peak", type=str, help="Apply #peak standards to action")
    parser.add_argument("--toysaac", type=str, help="Apply #TOYSAAC to feature")

    args = parser.parse_args()

    print("="*80)
    print("🎯 SHORT TAG MANTRA APPLICATOR")
    print("="*80)
    print()
    print("Into the unknown is our destination")
    print("Flying by the seat of our pants")
    print("Let's explore together")
    print()

    applicator = ShortTagMantraApplicator()

    if args.list:
        print("📋 MANTRA PRACTICES:")
        practices = applicator.get_all_practices()
        for tag, practice in practices.items():
            print(f"\n   {practice.tag}: {practice.name}")
            print(f"      Mantra: {practice.mantra}")
            print(f"      Weight: {practice.context_weight}")
            print(f"      Category: {practice.category}")
        print()

    if args.apply:
        result = applicator.apply_mantra(args.apply, {})
        if "error" not in result:
            print(f"✅ Applied: {result['name']}")
            print(f"   Mantra: {result['mantra']}")
        else:
            print(f"❌ {result['error']}")
        print()

    if args.peak:
        result = applicator.apply_peak_standards(args.peak)
        print(f"⛰️  PEAK Standards Applied:")
        print(f"   Action: {args.peak}")
        print(f"   Mantra: {result['mantra']}")
        print()

    if args.toysaac:
        result = applicator.apply_toysaac(args.toysaac)
        print(f"👤 TOYSAAC Applied:")
        print(f"   Feature: {args.toysaac}")
        print(f"   Mantra: {result['mantra']}")
        print()

    if not any([args.list, args.apply, args.peak, args.toysaac]):
        # Default: show summary
        practices = applicator.get_all_practices()
        print("🎯 MANTRA PRACTICES:")
        print(f"   Total Practices: {len(practices)}")
        print()
        print("Use --list to see all practices")
        print("Use --apply <tag> to apply a mantra")
        print("Use --peak <action> to apply PEAK standards")
        print("Use --toysaac <feature> to apply TOYSAAC")
        print()


if __name__ == "__main__":


    main()