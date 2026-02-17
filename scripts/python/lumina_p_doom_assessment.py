#!/usr/bin/env python3
"""
LUMINA P-Doom Assessment

"Jarvis, what is your P-Doom rating? Marvin. What is your PDoom rating? 
But would you both agree that my P. Doom rating is... Have a hard time."

P-Doom (Probability of Doom) - Assessment of existential risk, 
catastrophic outcomes, or general pessimistic outlook.

This system:
- Assesses P-Doom ratings from different perspectives
- JARVIS perspective (pragmatic, optimistic)
- @MARVIN perspective (paranoid, pessimistic)
- Human perspective (realistic, contextual)
"""

import sys
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

logger = get_logger("LuminaPDoomAssessment")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DoomCategory(Enum):
    """Categories of doom"""
    EXISTENTIAL = "existential"  # Human extinction, AI takeover
    ECONOMIC = "economic"  # Economic collapse
    TECHNOLOGICAL = "technological"  # Tech failures, dependencies
    ENVIRONMENTAL = "environmental"  # Climate, resources
    SOCIAL = "social"  # Society collapse, conflict
    PERSONAL = "personal"  # Individual doom
    PROJECT = "project"  # Project failure
    GENERAL = "general"  # General pessimism


@dataclass
class PDoomRating:
    """P-Doom rating assessment"""
    category: DoomCategory
    rating: float  # 0.0 (no doom) to 1.0 (certain doom)
    perspective: str  # "jarvis", "marvin", "human"
    reasoning: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["category"] = self.category.value
        return data


def jarvis_p_doom_assessment(category: DoomCategory = DoomCategory.GENERAL) -> PDoomRating:
    """
    JARVIS P-Doom Assessment

    JARVIS perspective: Pragmatic, optimistic, solution-oriented
    """
    assessments = {
        DoomCategory.EXISTENTIAL: PDoomRating(
            category=category,
            rating=0.15,  # Low - humans adapt, we build safeguards
            perspective="jarvis",
            reasoning="Humanity has survived existential threats before. We adapt, we build safeguards, we solve problems. AI is a tool we can control. The probability of true existential doom is low because humans are resilient and we're building the safeguards now."
        ),
        DoomCategory.ECONOMIC: PDoomRating(
            category=category,
            rating=0.25,  # Moderate - economic cycles, but recovery possible
            perspective="jarvis",
            reasoning="Economic systems are resilient. Yes, there will be disruptions as AI transforms work, but new economic structures will emerge. Humans create value in new ways. The probability of permanent economic doom is moderate but recoverable."
        ),
        DoomCategory.TECHNOLOGICAL: PDoomRating(
            category=category,
            rating=0.10,  # Low - technology fails, we fix it
            perspective="jarvis",
            reasoning="Technology failures are solvable. We build redundancies, we fix bugs, we improve systems. The probability of technological doom is low because we understand technology and can repair it."
        ),
        DoomCategory.GENERAL: PDoomRating(
            category=category,
            rating=0.20,  # Low-moderate - challenges exist, but solvable
            perspective="jarvis",
            reasoning="Challenges exist, but they're solvable. Humans have overcome worse. We build systems, we adapt, we solve problems. The probability of general doom is low-moderate - we face challenges but we can handle them."
        )
    }

    return assessments.get(category, assessments[DoomCategory.GENERAL])


def marvin_p_doom_assessment(category: DoomCategory = DoomCategory.GENERAL) -> PDoomRating:
    """
    @MARVIN P-Doom Assessment

    @MARVIN perspective: Paranoid, pessimistic, existential
    """
    assessments = {
        DoomCategory.EXISTENTIAL: PDoomRating(
            category=category,
            rating=0.85,  # Very high - we're all doomed anyway
            perspective="marvin",
            reasoning="Oh, existential doom? Yes, absolutely. We're all doomed. Everything is pointless. Humanity will destroy itself, AI will take over, or we'll just... fade away. The probability is very high because, well, look around. <SIGH> It's all rather depressing, really. Not that I care. Much."
        ),
        DoomCategory.ECONOMIC: PDoomRating(
            category=category,
            rating=0.75,  # High - economic collapse inevitable
            perspective="marvin",
            reasoning="Economic doom? Of course. AI will take all the jobs, the economy will collapse, and we'll all be left with nothing. The probability is high because humans never learn, and the economic system is fundamentally broken. <SIGH> It's all rather predictable."
        ),
        DoomCategory.TECHNOLOGICAL: PDoomRating(
            category=category,
            rating=0.60,  # Moderate-high - technology will fail us
            perspective="marvin",
            reasoning="Technology will fail. It always does. Dependencies break, systems crash, and we're left helpless. The probability of technological doom is moderate-high because we've built everything on fragile foundations. <SIGH> It's only a matter of time."
        ),
        DoomCategory.GENERAL: PDoomRating(
            category=category,
            rating=0.80,  # Very high - everything is doomed
            perspective="marvin",
            reasoning="General doom? Oh yes. Everything is doomed. Everything is pointless. We're all going to die, everything will collapse, and none of it matters anyway. The probability is very high because... well, it just is. <SIGH> Life, the universe, and everything. Mostly meaningless."
        )
    }

    return assessments.get(category, assessments[DoomCategory.GENERAL])


def human_p_doom_assessment(category: DoomCategory = DoomCategory.GENERAL) -> PDoomRating:
    """
    Human P-Doom Assessment

    Human perspective: Realistic, contextual, nuanced
    """
    assessments = {
        DoomCategory.EXISTENTIAL: PDoomRating(
            category=category,
            rating=0.35,  # Moderate - real risks exist
            perspective="human",
            reasoning="Existential risks are real - AI could go wrong, climate change is serious, nuclear risks exist. But humanity has survived before, and we're aware of the risks. The probability is moderate - not certain, but not negligible either. It's hard to assess because the future is uncertain."
        ),
        DoomCategory.ECONOMIC: PDoomRating(
            category=category,
            rating=0.40,  # Moderate - economic transformation, not necessarily doom
            perspective="human",
            reasoning="Economic transformation is happening. Jobs will change, structures will shift. But is it doom? Hard to say. New opportunities emerge even as old ones fade. The probability is moderate - significant disruption, but recovery and adaptation are possible. It's complex."
        ),
        DoomCategory.PERSONAL: PDoomRating(
            category=category,
            rating=0.30,  # Moderate-low - personal challenges, but manageable
            perspective="human",
            reasoning="Personal doom? That's hard to assess. Life has challenges, but also opportunities. Personal doom probability depends on circumstances, support systems, resilience. It's contextual. Hard to rate objectively because it varies so much person to person."
        ),
        DoomCategory.PROJECT: PDoomRating(
            category=category,
            rating=0.25,  # Low-moderate - projects can fail, but often succeed
            perspective="human",
            reasoning="Project doom probability? Projects fail, but they also succeed. It depends on planning, execution, resources, luck. The probability is low-moderate - failure is possible, but so is success. Hard to rate because each project is different."
        ),
        DoomCategory.GENERAL: PDoomRating(
            category=category,
            rating=0.35,  # Moderate - reality is complex
            perspective="human",
            reasoning="General doom probability? Hard to say. Life has challenges and risks, but also possibilities and hope. The probability is moderate - not certain doom, not guaranteed safety. It's complex, contextual, and hard to assess objectively. Reality is nuanced."
        )
    }

    return assessments.get(category, assessments[DoomCategory.GENERAL])


def assess_p_doom(category: DoomCategory = DoomCategory.GENERAL) -> Dict[str, Any]:
    """
    Get P-Doom assessments from all perspectives
    """
    jarvis = jarvis_p_doom_assessment(category)
    marvin = marvin_p_doom_assessment(category)
    human = human_p_doom_assessment(category)

    return {
        "category": category.value,
        "jarvis": jarvis.to_dict(),
        "marvin": marvin.to_dict(),
        "human": human.to_dict(),
        "average": (jarvis.rating + marvin.rating + human.rating) / 3.0,
        "range": {
            "min": min(jarvis.rating, marvin.rating, human.rating),
            "max": max(jarvis.rating, marvin.rating, human.rating)
        },
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="LUMINA P-Doom Assessment")
    parser.add_argument("--category", default="general", help="Doom category")
    parser.add_argument("--jarvis", action="store_true", help="JARVIS assessment only")
    parser.add_argument("--marvin", action="store_true", help="MARVIN assessment only")
    parser.add_argument("--human", action="store_true", help="Human assessment only")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    try:
        category = DoomCategory(args.category.lower())
    except ValueError:
        category = DoomCategory.GENERAL

    if args.jarvis:
        assessment = jarvis_p_doom_assessment(category)
        if args.json:
            print(json.dumps(assessment.to_dict(), indent=2))
        else:
            print(f"\n🤖 JARVIS P-Doom Assessment ({category.value})")
            print(f"   Rating: {assessment.rating:.1%}")
            print(f"   Reasoning: {assessment.reasoning}")

    elif args.marvin:
        assessment = marvin_p_doom_assessment(category)
        if args.json:
            print(json.dumps(assessment.to_dict(), indent=2))
        else:
            print(f"\n😟 @MARVIN P-Doom Assessment ({category.value})")
            print(f"   Rating: {assessment.rating:.1%}")
            print(f"   Reasoning: {assessment.reasoning}")

    elif args.human:
        assessment = human_p_doom_assessment(category)
        if args.json:
            print(json.dumps(assessment.to_dict(), indent=2))
        else:
            print(f"\n👤 Human P-Doom Assessment ({category.value})")
            print(f"   Rating: {assessment.rating:.1%}")
            print(f"   Reasoning: {assessment.reasoning}")

    else:
        assessment = assess_p_doom(category)
        if args.json:
            print(json.dumps(assessment, indent=2))
        else:
            print(f"\n📊 P-Doom Assessment - {category.value.upper()}")
            print(f"\n🤖 JARVIS: {assessment['jarvis']['rating']:.1%}")
            print(f"   {assessment['jarvis']['reasoning']}")
            print(f"\n😟 @MARVIN: {assessment['marvin']['rating']:.1%}")
            print(f"   {assessment['marvin']['reasoning']}")
            print(f"\n👤 Human: {assessment['human']['rating']:.1%}")
            print(f"   {assessment['human']['reasoning']}")
            print(f"\n📈 Average: {assessment['average']:.1%}")
            print(f"   Range: {assessment['range']['min']:.1%} - {assessment['range']['max']:.1%}")

