#!/usr/bin/env python3
"""
Register Zero-Sum Reverse Learning Pattern as @core @wopr @ff pattern
"""

from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from peak_pattern_system import PeakPatternSystem, PeakPattern, PatternType, PatternQuality
from zero_sum_reverse_learning_pattern import ZeroSumReverseLearningPattern, ZeroSumReverseLearningEngine

def register_zero_sum_pattern():
    """Register zero-sum reverse learning as @core @wopr @ff pattern"""

    print("=" * 70)
    print("🎯 Registering Zero-Sum Reverse Learning Pattern")
    print("   @core @wopr @ff - Core WOPR pattern for AI/ML/RL")
    print("=" * 70)

    # Initialize Peak Pattern System
    pattern_system = PeakPatternSystem(project_root)

    # Create Zero-Sum Reverse Learning pattern
    zsrl_pattern = ZeroSumReverseLearningPattern(
        pattern_id="zero_sum_reverse_learning_core_wopr",
        name="Zero-Sum Reverse Learning (RL/ML)"
    )

    # Convert to PeakPattern
    peak_pattern = PeakPattern(
        pattern_id="zero_sum_reverse_learning_core_wopr",
        name="Zero-Sum Reverse Learning (RL/ML)",
        pattern_type=PatternType.PATTERN,  # Meta-pattern
        description="""
Zero-Sum Reverse Learning Pattern for RL/ML systems.

Core principles:
- Zero-sum constraint: Sum of all utilities = 0
- Reverse learning: Learn by reversing/adversarial processes
- Adversarial training: Train agents against each other
- Counter-strategy development: Develop optimal counter-strategies
- Nash equilibrium seeking: Find equilibrium in zero-sum games
- Minimax optimization: Optimize using minimax algorithm

Use cases:
- Adversarial training in neural networks
- Game theory strategy development
- Counter-strategy learning in competitive environments
- Reverse engineering optimal policies
- Nash equilibrium finding
- Minimax optimization

@core @wopr @ff - Core WOPR pattern for AI/ML/RL systems.
        """.strip(),
        code_example="""
from zero_sum_reverse_learning_pattern import ZeroSumReverseLearningEngine

# Create engine
engine = ZeroSumReverseLearningEngine()

# Adversarial training (zero-sum)
result = engine.adversarial_training_step(
    {"id": "agent_a", "strategy": "strategy_a"},
    {"id": "agent_b", "strategy": "strategy_b"}
)

# Reverse learn counter-strategy
counter = engine.reverse_learn_strategy(opponent_strategy)

# Minimax optimization
minimax = engine.minimax_optimization("agent_a", depth=3)

# Find Nash equilibrium
equilibrium = engine.find_nash_equilibrium(strategies)
        """.strip(),
        usage_context=[
            "reinforcement_learning",
            "machine_learning",
            "adversarial_training",
            "game_theory",
            "strategy_optimization"
        ],
        dependencies=[
            "zero_sum_reverse_learning_pattern",
            "peak_pattern_system"
        ],
        tags=[
            "@core",
            "@wopr",
            "@ff",
            "zero_sum",
            "reverse_learning",
            "rl",
            "ml",
            "adversarial",
            "game_theory",
            "nash_equilibrium",
            "minimax",
            "counter_strategy"
        ],
        frequency=1,
        quality=PatternQuality.EXCELLENT,
        metadata={
            "core": True,
            "wopr": True,
            "ff": True,
            "ai": True,
            "engineer": True,
            "architect": True,
            "zero_sum_constraint": True,
            "reverse_learning": True,
            "adversarial_training": True,
            "reinforcement_learning": True,
            "machine_learning": True
        }
    )

    # Register pattern
    success = pattern_system.register_pattern(peak_pattern, merge_existing=True)

    if success:
        print("\n✅ Zero-Sum Reverse Learning Pattern registered successfully!")
        print(f"   Pattern ID: {peak_pattern.pattern_id}")
        print(f"   Tags: {', '.join(peak_pattern.tags)}")
        print(f"   Quality: {peak_pattern.quality.value}")
        print("\n🎯 Pattern is now available as @core @wopr @ff pattern")
    else:
        print("\n❌ Failed to register pattern")

    print("=" * 70)

    return success

if __name__ == "__main__":
    register_zero_sum_pattern()
