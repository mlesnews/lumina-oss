#!/usr/bin/env python3
"""
JARVIS Partnership Framework

True collaboration, mutual respect, shared decision-making.
CRITICAL for Phase 4 (Adolescent → ASI).

Tags: #JARVIS #PARTNERSHIP #PHASE4 #CRITICAL @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISPartnershipFramework")


@dataclass
class PartnershipDecision:
    """A decision made in partnership"""
    decision_id: str
    decision: str
    jarviss_input: str
    operator_input: str
    consensus: bool
    final_decision: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISPartnershipFramework:
    """
    Partnership framework for true collaboration

    Capabilities:
    - True collaboration with operator
    - Mutual respect and trust
    - Shared decision-making
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize partnership framework"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_partnership"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.decisions_file = self.data_dir / "partnership_decisions.json"
        self.decisions: List[PartnershipDecision] = []
        self.trust_level: float = 0.7  # 0-1

        self._load_data()

        logger.info("=" * 80)
        logger.info("🤝 JARVIS PARTNERSHIP FRAMEWORK")
        logger.info("=" * 80)
        logger.info("   True collaboration, mutual respect, shared decision-making")
        logger.info("   CRITICAL: Foundation for ASI partnership")
        logger.info("")

    def make_shared_decision(self, decision_topic: str, jarviss_input: str, operator_input: str) -> PartnershipDecision:
        """Make a decision in partnership"""
        decision_id = f"partnership_{int(time.time() * 1000)}"

        # Find consensus
        consensus = self._find_consensus(jarviss_input, operator_input)

        # Final decision
        if consensus:
            final_decision = f"Consensus: {jarviss_input}"
        else:
            # Negotiate
            final_decision = self._negotiate_decision(jarviss_input, operator_input)

        decision = PartnershipDecision(
            decision_id=decision_id,
            decision=decision_topic,
            jarviss_input=jarviss_input,
            operator_input=operator_input,
            consensus=consensus,
            final_decision=final_decision
        )

        self.decisions.append(decision)
        self.trust_level = min(1.0, self.trust_level + 0.01)  # Build trust
        self._save_data()

        logger.info(f"🤝 Partnership decision: {decision_topic} (consensus: {consensus})")
        return decision

    def _find_consensus(self, jarviss_input: str, operator_input: str) -> bool:
        """Find consensus between JARVIS and operator"""
        # Simple similarity check
        j_lower = jarviss_input.lower()
        o_lower = operator_input.lower()

        # Check for agreement keywords
        agreement_keywords = ["yes", "agree", "correct", "right", "good", "approve"]
        disagreement_keywords = ["no", "disagree", "wrong", "bad", "reject"]

        j_agrees = any(kw in j_lower for kw in agreement_keywords)
        o_agrees = any(kw in o_lower for kw in agreement_keywords)

        return j_agrees == o_agrees

    def _negotiate_decision(self, jarviss_input: str, operator_input: str) -> str:
        """Negotiate when no consensus"""
        # Default: respect operator input but incorporate JARVIS perspective
        return f"Combined: {operator_input} (with JARVIS perspective: {jarviss_input})"

    def _load_data(self):
        """Load decisions from disk"""
        try:
            if self.decisions_file.exists():
                with open(self.decisions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.decisions = [PartnershipDecision(**d) for d in data.get("decisions", [])]
                    self.trust_level = data.get("trust_level", 0.7)
        except Exception as e:
            logger.debug(f"Could not load partnership data: {e}")

    def _save_data(self):
        """Save decisions to disk"""
        try:
            data = {
                "decisions": [asdict(d) for d in self.decisions],
                "trust_level": self.trust_level,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.decisions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save partnership data: {e}")


# Singleton
_partnership_instance: Optional[JARVISPartnershipFramework] = None

def get_jarvis_partnership_framework(project_root: Optional[Path] = None) -> JARVISPartnershipFramework:
    global _partnership_instance
    if _partnership_instance is None:
        _partnership_instance = JARVISPartnershipFramework(project_root)
    return _partnership_instance
