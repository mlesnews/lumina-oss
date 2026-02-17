#!/usr/bin/env python3
"""
JARVIS Reasoning Engine

Implements logical, causal, and analogical reasoning for multi-step problem-solving.
This is a CRITICAL component for Phase 2 (Toddler → Child).

Tags: #JARVIS #REASONING #PHASE2 #CRITICAL @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
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

logger = get_logger("JARVISReasoningEngine")


class ReasoningType(Enum):
    """Types of reasoning"""
    LOGICAL = "logical"  # If-then, boolean logic, deduction
    CAUSAL = "causal"  # Cause-effect relationships
    ANALOGICAL = "analogical"  # Similarity-based reasoning
    MULTI_STEP = "multi_step"  # Complex multi-step chains


@dataclass
class ReasoningStep:
    """A single step in a reasoning chain"""
    step_id: str
    reasoning_type: ReasoningType
    premise: str
    conclusion: str
    confidence: float  # 0-1
    evidence: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ReasoningChain:
    """A complete reasoning chain"""
    chain_id: str
    problem: str
    steps: List[ReasoningStep]
    final_conclusion: str
    confidence: float
    reasoning_type: ReasoningType
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISReasoningEngine:
    """
    Multi-step reasoning engine for JARVIS

    Implements:
    - Logical reasoning (if-then, deduction, boolean logic)
    - Causal reasoning (cause-effect chains)
    - Analogical reasoning (similarity-based)
    - Multi-step reasoning (complex chains)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize reasoning engine"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_reasoning"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.chains_file = self.data_dir / "reasoning_chains.json"
        self.patterns_file = self.data_dir / "reasoning_patterns.json"

        self.reasoning_chains: List[ReasoningChain] = []
        self.reasoning_patterns: Dict[str, Any] = {}

        # Load existing data
        self._load_data()

        # Integrate with learning pipeline
        try:
            from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
            self.learning_pipeline = get_jarvis_learning_pipeline(self.project_root)
        except ImportError:
            self.learning_pipeline = None

        logger.info("=" * 80)
        logger.info("🧠 JARVIS REASONING ENGINE")
        logger.info("=" * 80)
        logger.info("   Logical, Causal, Analogical, Multi-Step Reasoning")
        logger.info("")

    def logical_reasoning(self, premises: List[str], goal: str) -> ReasoningChain:
        """
        Perform logical reasoning (if-then, deduction)

        Args:
            premises: List of logical premises
            goal: What we're trying to prove/conclude

        Returns:
            ReasoningChain with logical reasoning steps
        """
        chain_id = f"logical_{int(time.time() * 1000)}"
        steps = []

        # Simple logical inference
        # If A and B, then C
        # If C, then D
        # Therefore: If A and B, then D

        current_knowledge = set(premises)
        step_num = 0

        # Apply logical rules
        for premise in premises:
            step_num += 1
            step_id = f"{chain_id}_step_{step_num}"

            # Extract implications
            if "if" in premise.lower() and "then" in premise.lower():
                # If-then rule
                parts = premise.lower().split("then")
                if len(parts) == 2:
                    condition = parts[0].replace("if", "").strip()
                    conclusion = parts[1].strip()

                    # Check if condition is satisfied
                    condition_satisfied = all(
                        cond.strip() in current_knowledge or 
                        cond.strip() in [p.lower() for p in premises]
                        for cond in condition.split("and")
                    )

                    if condition_satisfied:
                        step = ReasoningStep(
                            step_id=step_id,
                            reasoning_type=ReasoningType.LOGICAL,
                            premise=premise,
                            conclusion=conclusion,
                            confidence=0.85,
                            evidence=[premise],
                            dependencies=[]
                        )
                        steps.append(step)
                        current_knowledge.add(conclusion)

        # Check if goal is reached
        final_conclusion = goal
        goal_reached = goal.lower() in [k.lower() for k in current_knowledge]
        confidence = 0.9 if goal_reached else 0.5

        chain = ReasoningChain(
            chain_id=chain_id,
            problem=goal,
            steps=steps,
            final_conclusion=final_conclusion,
            confidence=confidence,
            reasoning_type=ReasoningType.LOGICAL
        )

        self.reasoning_chains.append(chain)
        self._save_data()

        # Record in learning pipeline
        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.REASONING,
                source="logical_reasoning",
                context={"premises": premises, "goal": goal},
                data={"chain_id": chain_id, "steps": len(steps), "confidence": confidence}
            )

        logger.info(f"🧠 Logical reasoning: {len(steps)} steps, confidence: {confidence:.2%}")
        return chain

    def causal_reasoning(self, cause: str, effect: str, context: Dict[str, Any] = None) -> ReasoningChain:
        """
        Perform causal reasoning (cause-effect relationships)

        Args:
            cause: The cause
            effect: The effect
            context: Additional context

        Returns:
            ReasoningChain with causal reasoning steps
        """
        chain_id = f"causal_{int(time.time() * 1000)}"
        context = context or {}

        steps = []

        # Causal chain: A causes B, B causes C, therefore A causes C
        step1 = ReasoningStep(
            step_id=f"{chain_id}_step_1",
            reasoning_type=ReasoningType.CAUSAL,
            premise=cause,
            conclusion=f"{cause} → {effect}",
            confidence=0.75,
            evidence=[cause, effect],
            dependencies=[]
        )
        steps.append(step1)

        # Check for intermediate causes
        if context.get("intermediate_causes"):
            for i, intermediate in enumerate(context["intermediate_causes"], 2):
                step = ReasoningStep(
                    step_id=f"{chain_id}_step_{i}",
                    reasoning_type=ReasoningType.CAUSAL,
                    premise=steps[-1].conclusion,
                    conclusion=f"{steps[-1].conclusion} → {intermediate}",
                    confidence=0.70,
                    evidence=[intermediate],
                    dependencies=[steps[-1].step_id]
                )
                steps.append(step)

        final_conclusion = f"{cause} causes {effect}"
        confidence = 0.8 if len(steps) > 1 else 0.6

        chain = ReasoningChain(
            chain_id=chain_id,
            problem=f"Understand causal relationship: {cause} → {effect}",
            steps=steps,
            final_conclusion=final_conclusion,
            confidence=confidence,
            reasoning_type=ReasoningType.CAUSAL
        )

        self.reasoning_chains.append(chain)
        self._save_data()

        # Record in learning pipeline
        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.REASONING,
                source="causal_reasoning",
                context={"cause": cause, "effect": effect, "context": context},
                data={"chain_id": chain_id, "steps": len(steps), "confidence": confidence}
            )

        logger.info(f"🔗 Causal reasoning: {len(steps)} steps, confidence: {confidence:.2%}")
        return chain

    def analogical_reasoning(self, source: str, target: str, similarity: float = 0.7) -> ReasoningChain:
        """
        Perform analogical reasoning (similarity-based)

        Args:
            source: Source domain/case
            target: Target domain/case
            similarity: Similarity score (0-1)

        Returns:
            ReasoningChain with analogical reasoning steps
        """
        chain_id = f"analogical_{int(time.time() * 1000)}"

        steps = []

        # Analogical mapping: If A is like B, and A has property X, then B might have property X
        step1 = ReasoningStep(
            step_id=f"{chain_id}_step_1",
            reasoning_type=ReasoningType.ANALOGICAL,
            premise=f"{source} is similar to {target}",
            conclusion=f"Similarity: {similarity:.2%}",
            confidence=similarity,
            evidence=[source, target],
            dependencies=[]
        )
        steps.append(step1)

        # Transfer properties
        step2 = ReasoningStep(
            step_id=f"{chain_id}_step_2",
            reasoning_type=ReasoningType.ANALOGICAL,
            premise=step1.conclusion,
            conclusion=f"Properties from {source} may apply to {target}",
            confidence=similarity * 0.8,  # Analogical reasoning is less certain
            evidence=[source, target],
            dependencies=[step1.step_id]
        )
        steps.append(step2)

        final_conclusion = f"{target} is analogous to {source} (similarity: {similarity:.2%})"
        confidence = similarity * 0.75  # Analogical reasoning has lower confidence

        chain = ReasoningChain(
            chain_id=chain_id,
            problem=f"Find analogy: {source} → {target}",
            steps=steps,
            final_conclusion=final_conclusion,
            confidence=confidence,
            reasoning_type=ReasoningType.ANALOGICAL
        )

        self.reasoning_chains.append(chain)
        self._save_data()

        # Record in learning pipeline
        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.REASONING,
                source="analogical_reasoning",
                context={"source": source, "target": target, "similarity": similarity},
                data={"chain_id": chain_id, "steps": len(steps), "confidence": confidence}
            )

        logger.info(f"🔀 Analogical reasoning: {len(steps)} steps, confidence: {confidence:.2%}")
        return chain

    def multi_step_reasoning(self, problem: str, goal: str, max_steps: int = 10) -> ReasoningChain:
        """
        Perform multi-step reasoning (combines all reasoning types)

        Args:
            problem: The problem to solve
            goal: The goal to achieve
            max_steps: Maximum reasoning steps

        Returns:
            ReasoningChain with multi-step reasoning
        """
        chain_id = f"multistep_{int(time.time() * 1000)}"
        steps = []

        # Break problem into sub-problems
        # Use logical, causal, and analogical reasoning as needed

        # Step 1: Analyze problem
        step1 = ReasoningStep(
            step_id=f"{chain_id}_step_1",
            reasoning_type=ReasoningType.MULTI_STEP,
            premise=problem,
            conclusion=f"Problem identified: {problem}",
            confidence=0.9,
            evidence=[problem],
            dependencies=[]
        )
        steps.append(step1)

        # Step 2: Identify approach
        # Try logical first, then causal, then analogical
        approach = "logical"  # Default
        if "cause" in problem.lower() or "effect" in problem.lower():
            approach = "causal"
        elif "similar" in problem.lower() or "like" in problem.lower():
            approach = "analogical"

        step2 = ReasoningStep(
            step_id=f"{chain_id}_step_2",
            reasoning_type=ReasoningType.MULTI_STEP,
            premise=step1.conclusion,
            conclusion=f"Approach: {approach} reasoning",
            confidence=0.8,
            evidence=[problem],
            dependencies=[step1.step_id]
        )
        steps.append(step2)

        # Step 3: Apply reasoning
        if approach == "logical":
            logical_chain = self.logical_reasoning([problem], goal)
            steps.extend(logical_chain.steps)
        elif approach == "causal":
            # Extract cause and effect
            parts = problem.split("→")
            if len(parts) == 2:
                causal_chain = self.causal_reasoning(parts[0].strip(), parts[1].strip())
                steps.extend(causal_chain.steps)
        else:
            # Analogical - would need source and target
            # For now, use logical
            logical_chain = self.logical_reasoning([problem], goal)
            steps.extend(logical_chain.steps)

        # Final step: Synthesize
        final_step = ReasoningStep(
            step_id=f"{chain_id}_final",
            reasoning_type=ReasoningType.MULTI_STEP,
            premise=steps[-1].conclusion if steps else problem,
            conclusion=goal,
            confidence=0.75,
            evidence=[s.conclusion for s in steps],
            dependencies=[s.step_id for s in steps]
        )
        steps.append(final_step)

        final_conclusion = goal
        confidence = sum(s.confidence for s in steps) / len(steps) if steps else 0.5

        chain = ReasoningChain(
            chain_id=chain_id,
            problem=problem,
            steps=steps,
            final_conclusion=final_conclusion,
            confidence=confidence,
            reasoning_type=ReasoningType.MULTI_STEP
        )

        self.reasoning_chains.append(chain)
        self._save_data()

        # Record in learning pipeline
        if self.learning_pipeline:
            self.learning_pipeline.collect_learning_data(
                LearningDataType.REASONING,
                source="multi_step_reasoning",
                context={"problem": problem, "goal": goal, "max_steps": max_steps},
                data={"chain_id": chain_id, "steps": len(steps), "confidence": confidence}
            )

        logger.info(f"🔗 Multi-step reasoning: {len(steps)} steps, confidence: {confidence:.2%}")
        return chain

    def get_reasoning_history(self, limit: int = 10) -> List[ReasoningChain]:
        """Get recent reasoning chains"""
        return sorted(
            self.reasoning_chains,
            key=lambda c: c.timestamp,
            reverse=True
        )[:limit]

    def _load_data(self):
        """Load reasoning data from disk"""
        try:
            if self.chains_file.exists():
                with open(self.chains_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reasoning_chains = [
                        ReasoningChain(**chain_data)
                        for chain_data in data.get("chains", [])
                    ]
                    logger.debug(f"Loaded {len(self.reasoning_chains)} reasoning chains")
        except Exception as e:
            logger.debug(f"Could not load reasoning data: {e}")

    def _save_data(self):
        """Save reasoning data to disk"""
        try:
            data = {
                "chains": [
                    {
                        **asdict(chain),
                        "reasoning_type": chain.reasoning_type.value,
                        "steps": [
                            {
                                **asdict(step),
                                "reasoning_type": step.reasoning_type.value
                            }
                            for step in chain.steps
                        ]
                    }
                    for chain in self.reasoning_chains
                ],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.chains_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save reasoning data: {e}")


# Singleton pattern
_reasoning_engine_instance: Optional[JARVISReasoningEngine] = None


def get_jarvis_reasoning_engine(project_root: Optional[Path] = None) -> JARVISReasoningEngine:
    """Get singleton reasoning engine instance"""
    global _reasoning_engine_instance
    if _reasoning_engine_instance is None:
        _reasoning_engine_instance = JARVISReasoningEngine(project_root)
    return _reasoning_engine_instance


if __name__ == "__main__":
    engine = get_jarvis_reasoning_engine()

    # Test logical reasoning
    chain = engine.logical_reasoning(
        ["If A and B, then C", "If C, then D", "A", "B"],
        "D"
    )
    print(f"Logical reasoning: {chain.final_conclusion} (confidence: {chain.confidence:.2%})")

    # Test causal reasoning
    chain = engine.causal_reasoning(
        "System overload",
        "Performance degradation",
        {"intermediate_causes": ["High CPU usage", "Memory pressure"]}
    )
    print(f"Causal reasoning: {chain.final_conclusion} (confidence: {chain.confidence:.2%})")

    # Test analogical reasoning
    chain = engine.analogical_reasoning(
        "Previous similar problem",
        "Current problem",
        similarity=0.8
    )
    print(f"Analogical reasoning: {chain.final_conclusion} (confidence: {chain.confidence:.2%})")
