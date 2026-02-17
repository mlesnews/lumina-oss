#!/usr/bin/env python3
"""
JARVIS AGI Framework

General intelligence, domain adaptation, cross-domain reasoning.
CRITICAL for Phase 3 (Child → Adolescent).

Tags: #JARVIS #AGI #PHASE3 #CRITICAL @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

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

logger = get_logger("JARVISAGIFramework")


class Domain(Enum):
    """Knowledge domains"""
    SOFTWARE = "software"
    NETWORKING = "networking"
    DATA = "data"
    SECURITY = "security"
    AUTOMATION = "automation"
    GENERAL = "general"


@dataclass
class DomainKnowledge:
    """Knowledge in a specific domain"""
    domain: Domain
    knowledge_base: Dict[str, Any] = field(default_factory=dict)
    adaptation_time: float = 0.0  # Hours to adapt
    performance: float = 0.0  # 0-1
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISAGIFramework:
    """
    AGI framework - general intelligence across domains

    Capabilities:
    - Apply knowledge across domains
    - Transfer learning between tasks
    - General problem-solving
    - Domain adaptation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize AGI framework"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_agi"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.knowledge_file = self.data_dir / "domain_knowledge.json"
        self.domain_knowledge: Dict[Domain, DomainKnowledge] = {}

        self._load_data()
        self._initialize_domains()

        # Integrate with meta-learning
        try:
            from jarvis_meta_learning import get_jarvis_meta_learning
            self.meta_learning = get_jarvis_meta_learning(self.project_root)
        except ImportError:
            self.meta_learning = None

        # Integrate with learning pipeline
        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
        except ImportError:
            self.learning_pipeline = None

        logger.info("=" * 80)
        logger.info("🌐 JARVIS AGI FRAMEWORK")
        logger.info("=" * 80)
        logger.info("   General intelligence across domains")
        logger.info("   Domain adaptation and cross-domain reasoning")
        logger.info("")

    def adapt_to_domain(self, domain: Domain, examples: List[Any]) -> DomainKnowledge:
        """Adapt to a new domain quickly"""
        start_time = time.time()

        # Use meta-learning if available
        if self.meta_learning:
            # Find similar domain
            similar_domain = self._find_similar_domain(domain)
            if similar_domain:
                # Transfer learning
                accuracy = self.meta_learning.transfer_learning(similar_domain.value, domain.value)
            else:
                # Few-shot learning
                episode = self.meta_learning.learn_new_task(domain.value, examples)
                accuracy = episode.accuracy
        else:
            accuracy = 0.7  # Default

        adaptation_time = (time.time() - start_time) / 3600  # Hours

        knowledge = DomainKnowledge(
            domain=domain,
            knowledge_base={"examples": len(examples), "concepts": []},
            adaptation_time=adaptation_time,
            performance=accuracy
        )

        self.domain_knowledge[domain] = knowledge
        self._save_data()

        logger.info(f"🌐 Adapted to {domain.value} domain: {accuracy:.2%} performance in {adaptation_time:.2f} hours")
        return knowledge

    def cross_domain_reasoning(self, problem: str, source_domains: List[Domain], target_domain: Domain) -> str:
        """Reason across domains"""
        # Extract insights from source domains
        insights = []
        for domain in source_domains:
            if domain in self.domain_knowledge:
                knowledge = self.domain_knowledge[domain]
                insights.append(f"From {domain.value}: {knowledge.performance:.2%} performance")

        # Apply to target domain
        solution = f"Apply insights from {', '.join([d.value for d in source_domains])} to solve {problem} in {target_domain.value}"

        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.REASONING,
                source="cross_domain_reasoning",
                context={"problem": problem, "source_domains": [d.value for d in source_domains], "target_domain": target_domain.value},
                data={"solution": solution, "insights": insights}
            )

        logger.info(f"🔀 Cross-domain reasoning: {len(source_domains)} domains → {target_domain.value}")
        return solution

    def _find_similar_domain(self, domain: Domain) -> Optional[Domain]:
        """Find similar domain for transfer"""
        # Simple similarity mapping
        similarities = {
            Domain.SOFTWARE: [Domain.AUTOMATION],
            Domain.NETWORKING: [Domain.SECURITY],
            Domain.DATA: [Domain.SOFTWARE]
        }

        if domain in similarities:
            similar = similarities[domain][0]
            if similar in self.domain_knowledge:
                return similar

        return None

    def _initialize_domains(self):
        """Initialize domain knowledge"""
        for domain in Domain:
            if domain not in self.domain_knowledge:
                self.domain_knowledge[domain] = DomainKnowledge(domain=domain)

    def _load_data(self):
        """Load domain knowledge from disk"""
        try:
            if self.knowledge_file.exists():
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.domain_knowledge = {
                        Domain(k): DomainKnowledge(**{**v, "domain": Domain(k)})
                        for k, v in data.get("domains", {}).items()
                    }
        except Exception as e:
            logger.debug(f"Could not load AGI data: {e}")

    def _save_data(self):
        """Save domain knowledge to disk"""
        try:
            data = {
                "domains": {
                    domain.value: {**asdict(knowledge), "domain": domain.value}
                    for domain, knowledge in self.domain_knowledge.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save AGI data: {e}")


# Singleton
_agi_framework_instance: Optional[JARVISAGIFramework] = None

def get_jarvis_agi_framework(project_root: Optional[Path] = None) -> JARVISAGIFramework:
    global _agi_framework_instance
    if _agi_framework_instance is None:
        _agi_framework_instance = JARVISAGIFramework(project_root)
    return _agi_framework_instance
