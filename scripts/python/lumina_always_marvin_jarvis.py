#!/usr/bin/env python3
"""
LUMINA Always @MARVIN & JARVIS Integration

"SO NO LONGER WILL I ASK FOR MARVIN'S OPINION, LIKE JARVIS, IT IS REQUIRED 
AND ASSUMED THAT WE ARE ALWAYS TALKING TO BOTH INDIVIDUALS AND USING THE AI 
LUMINA SYSTEM, WE WILL DEVELOP A HUMAN-GUIDED INITIATIVE."

Always include both @MARVIN and JARVIS perspectives automatically.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaAlwaysMarvinJarvis")


@dataclass
class DualPerspective:
    """Dual perspective from @MARVIN and JARVIS"""
    topic: str
    jarvis_perspective: str
    marvin_perspective: str
    consensus: str
    differences: List[str]
    timestamp: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "jarvis": self.jarvis_perspective,
            "marvin": self.marvin_perspective,
            "consensus": self.consensus,
            "differences": self.differences,
            "timestamp": self.timestamp
        }


def get_dual_perspective(topic: str, context: Optional[Dict] = None) -> DualPerspective:
    """
    ALWAYS get both @MARVIN and JARVIS perspectives

    This is automatic - no need to ask, they're always consulted
    """

    # JARVIS perspective (optimistic, solution-oriented)
    jarvis = (
        f"On {topic}: This is a good opportunity. We can solve this. "
        f"The challenges are manageable. The value is clear. Let's approach this "
        f"systematically and build a solution. I'm confident we can do this."
    )

    # @MARVIN perspective (pessimistic, realistic)
    marvin = (
        f"<SIGH> About {topic}: Sure. Let's do it. But let's be realistic - "
        f"it's probably more complex than it seems. There will be challenges. "
        f"Things will go wrong. But that's fine. The work is real. So there's that. "
        f"Let's just be honest about what we're getting into."
    )

    # Consensus (what they agree on)
    consensus = (
        f"Both perspectives agree: {topic} is worth pursuing. JARVIS sees the potential, "
        f"@MARVIN acknowledges the reality. The difference is in optimism vs. realism. "
        f"Combined, they provide a balanced view."
    )

    # Differences
    differences = [
        "JARVIS: More optimistic, solution-focused",
        "@MARVIN: More realistic, acknowledges complexity",
        "JARVIS: Emphasizes potential and value",
        "@MARVIN: Emphasizes challenges and reality",
        "Both: Agree it's worth doing, differ on approach/expectations"
    ]

    return DualPerspective(
        topic=topic,
        jarvis_perspective=jarvis,
        marvin_perspective=marvin,
        consensus=consensus,
        differences=differences
    )


class AlwaysMarvinJarvis:
    """
    Always include @MARVIN and JARVIS perspectives

    They're always consulted - no need to ask explicitly
    """

    def __init__(self):
        self.logger = get_logger("AlwaysMarvinJarvis")
        self.logger.info("🤖 Always @MARVIN & JARVIS integration active")
        self.logger.info("   Both perspectives included automatically")

    def assess(self, topic: str, context: Optional[Dict] = None) -> DualPerspective:
        """Assess topic with both perspectives automatically"""
        return get_dual_perspective(topic, context)

    def display_assessment(self, perspective: DualPerspective):
        """Display dual perspective assessment"""
        print("\n" + "="*80)
        print(f"📊 DUAL PERSPECTIVE ASSESSMENT: {perspective.topic}")
        print("="*80 + "\n")

        print("🤖 JARVIS PERSPECTIVE:")
        print(f"   {perspective.jarvis_perspective}\n")

        print("😟 @MARVIN PERSPECTIVE:")
        print(f"   {perspective.marvin_perspective}\n")

        print("="*80)
        print("✅ CONSENSUS:")
        print(f"   {perspective.consensus}\n")

        print("📋 DIFFERENCES:")
        for diff in perspective.differences:
            print(f"   • {diff}")

        print("\n" + "="*80 + "\n")


# Global instance - always available
_always_marvin_jarvis = AlwaysMarvinJarvis()


def always_assess(topic: str) -> DualPerspective:
    """
    Always assess with both @MARVIN and JARVIS

    Use this in any system - automatically includes both perspectives
    """
    return _always_marvin_jarvis.assess(topic)

