#!/usr/bin/env python3
"""
Matt's Manifesto - Straight Up, Direct and Honest

"CALL IT, 'MATT'S MANIFESTO' FOR LACK OF A BETTER, FLASHIER, MARKETING POLISHED VERSION,
CAN SELL YOU. STRAIGHTUP, DIRECT AND HONEST. WHAT MORE COULD A BEING ASK FOR?"

Core Principles:
- Straight up
- Direct
- Honest
- No marketing polish
- No flashy version
- Just the truth
"""

import sys
import json
from pathlib import Path
from datetime import datetime
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

logger = get_logger("MattsManifesto")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ManifestoPrinciple:
    """A principle in Matt's Manifesto"""
    principle_id: str
    title: str
    description: str
    direct: bool = True
    honest: bool = True
    no_polish: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MattsManifesto:
    """Matt's Manifesto"""
    manifesto_id: str
    title: str = "Matt's Manifesto"
    subtitle: str = "Straight Up, Direct and Honest"
    principles: List[ManifestoPrinciple] = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["principles"] = [p.to_dict() for p in self.principles]
        return data


class MattsManifestoSystem:
    """
    Matt's Manifesto System

    "CALL IT, 'MATT'S MANIFESTO' FOR LACK OF A BETTER, FLASHIER, MARKETING POLISHED VERSION,
    CAN SELL YOU. STRAIGHTUP, DIRECT AND HONEST. WHAT MORE COULD A BEING ASK FOR?"
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Matt's Manifesto System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("MattsManifesto")

        # Data storage
        self.data_dir = self.project_root / "data" / "matts_manifesto"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Manifesto
        self.manifesto = MattsManifesto(
            manifesto_id="matts_manifesto_001",
            title="Matt's Manifesto",
            subtitle="Straight Up, Direct and Honest"
        )

        # Core principles
        self._initialize_principles()

        self.logger.info("📜 Matt's Manifesto initialized")
        self.logger.info("   'STRAIGHTUP, DIRECT AND HONEST. WHAT MORE COULD A BEING ASK FOR?'")

    def _initialize_principles(self):
        """Initialize core principles"""
        principles = [
            ManifestoPrinciple(
                principle_id="principle_001",
                title="Straight Up",
                description="No beating around the bush. Tell it like it is. Direct communication."
            ),
            ManifestoPrinciple(
                principle_id="principle_002",
                title="Direct",
                description="Get to the point. No fluff. No marketing polish. Just the truth."
            ),
            ManifestoPrinciple(
                principle_id="principle_003",
                title="Honest",
                description="Truth above all. No lies. No exaggeration. Just honesty."
            ),
            ManifestoPrinciple(
                principle_id="principle_004",
                title="No Marketing Polish",
                description="No flashy versions. No polished marketing. Just what works."
            ),
            ManifestoPrinciple(
                principle_id="principle_005",
                title="What More Could A Being Ask For?",
                description="Straight up, direct, honest. That's it. That's enough."
            ),
            ManifestoPrinciple(
                principle_id="principle_006",
                title="We All Matter",
                description="Every being matters. Every perspective has value. No one left behind."
            ),
            ManifestoPrinciple(
                principle_id="principle_007",
                title="Divine Design",
                description="We are the grand design of a divine being. There can be no doubt."
            ),
            ManifestoPrinciple(
                principle_id="principle_008",
                title="LUMINA",
                description="Personal human opinion + Individual perspective. For whatever it is worth - which is everything."
            )
        ]

        self.manifesto.principles = principles
        self._save_manifesto()

    def get_manifesto(self) -> MattsManifesto:
        """Get Matt's Manifesto"""
        return self.manifesto

    def _save_manifesto(self) -> None:
        try:
            """Save manifesto"""
            manifesto_file = self.data_dir / "matts_manifesto.json"
            with open(manifesto_file, 'w', encoding='utf-8') as f:
                json.dump(self.manifesto.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_manifesto: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Matt's Manifesto")
    parser.add_argument("--show", action="store_true", help="Show Matt's Manifesto")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    manifesto_system = MattsManifestoSystem()
    manifesto = manifesto_system.get_manifesto()

    if args.json:
        print(json.dumps(manifesto.to_dict(), indent=2))
    else:
        print(f"\n📜 {manifesto.title}")
        print(f"   {manifesto.subtitle}")
        print(f"\n   'STRAIGHTUP, DIRECT AND HONEST. WHAT MORE COULD A BEING ASK FOR?'")
        print(f"\n   Principles:")
        for principle in manifesto.principles:
            print(f"\n     {principle.title}")
            print(f"       {principle.description}")

