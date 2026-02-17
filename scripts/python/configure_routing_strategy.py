#!/usr/bin/env python3
"""
Configure Intelligent LLM Routing Strategy

Easy interface to configure and test routing strategies for laptop LLM models.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from intelligent_llm_router import IntelligentLLMRouter, RoutingStrategy, AIModel
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("configure_routing_strategy")




# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def configure_routing_interactive():
    """Interactive routing strategy configuration"""
    print("=" * 80)
    print("INTELLIGENT LLM ROUTING STRATEGY CONFIGURATION")
    print("=" * 80)
    print()

    # Show available strategies
    print("Available Routing Strategies:")
    print("-" * 80)
    strategies = {
        "1": (RoutingStrategy.ROUND_ROBIN, "Round-robin - Equal distribution"),
        "2": (RoutingStrategy.LOAD_BALANCED, "Load-balanced - Least loaded model"),
        "3": (RoutingStrategy.PERFORMANCE_BASED, "Performance-based - Best performing"),
        "4": (RoutingStrategy.COST_AWARE, "Cost-aware - Balance cost and performance"),
        "5": (RoutingStrategy.LATENCY_BASED, "Latency-based - Lowest latency"),
        "6": (RoutingStrategy.PRIORITY_BASED, "Priority-based - Match priority"),
        "7": (RoutingStrategy.ADAPTIVE, "Adaptive - Learn from history (recommended)"),
        "8": (RoutingStrategy.HYBRID, "Hybrid - Context-aware combination")
    }

    for key, (strategy, desc) in strategies.items():
        print(f"  {key}. {desc} ({strategy.value})")

    print()
    choice = input("Select routing strategy (1-8, default: 7): ").strip() or "7"

    if choice in strategies:
        selected_strategy, desc = strategies[choice]
        print(f"\n✅ Selected: {desc}")
        return selected_strategy
    else:
        print(f"\n⚠️  Invalid choice, using default: Adaptive")
        return RoutingStrategy.ADAPTIVE


def save_routing_config(strategy: RoutingStrategy):
    try:
        """Save routing configuration"""
        config_file = project_root / "config" / "routing_strategy.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "version": "1.0.0",
            "routing_strategy": strategy.value,
            "last_updated": __import__("datetime").datetime.now().isoformat()
        }

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Configuration saved to: {config_file}")


    except Exception as e:
        logger.error(f"Error in save_routing_config: {e}", exc_info=True)
        raise
def load_routing_config() -> RoutingStrategy:
    """Load routing configuration"""
    config_file = project_root / "config" / "routing_strategy.json"

    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                strategy_name = config.get("routing_strategy", "adaptive")
                return RoutingStrategy(strategy_name)
        except Exception as e:
            print(f"⚠️  Failed to load config: {e}")

    return RoutingStrategy.ADAPTIVE


def test_routing_strategy(strategy: RoutingStrategy):
    """Test a routing strategy with sample models"""
    print(f"\n🧪 Testing Routing Strategy: {strategy.value}")
    print("-" * 80)

    router = IntelligentLLMRouter(routing_strategy=strategy)

    # Register test models
    test_models = [
        AIModel(
            name="laptop-llm-8b",
            endpoint="http://localhost:11434",
            model_id="llama3.1:8b",
            provider="local",
            capabilities=["code_generation", "general", "reasoning"],
            priority=8,
            max_concurrent=3,
            cost_per_1k_tokens=0.0
        ),
        AIModel(
            name="kaiju-codellama-13b",
            endpoint="http://kaiju_no_8:11437",
            model_id="codellama:13b",
            provider="kaiju",
            capabilities=["code_generation"],
            priority=10,
            max_concurrent=5,
            cost_per_1k_tokens=0.0
        ),
        AIModel(
            name="wsl-llama3.2-11b",
            endpoint="http://localhost:11434",
            model_id="llama3.2:11b",
            provider="wsl",
            capabilities=["general", "reasoning"],
            priority=9,
            max_concurrent=4,
            cost_per_1k_tokens=0.0
        )
    ]

    for model in test_models:
        router.register_model(model)

    # Test selections
    print("\n📋 Test Selections:")
    test_tasks = [
        ("code_generation", 5, ["code_generation"]),
        ("reasoning", 8, ["reasoning"]),
        ("general", 5, []),
    ]

    for task_type, priority, capabilities in test_tasks:
        selected = router.select_model(
            task_type=task_type,
            required_capabilities=capabilities,
            priority=priority
        )
        if selected:
            print(f"   Task: {task_type} (priority {priority}) → Model: {selected.name}")
        else:
            print(f"   Task: {task_type} → No model available")

    # Show statistics
    stats = router.get_routing_stats()
    print(f"\n📊 Routing Statistics:")
    print(f"   Strategy: {stats['current_strategy']}")
    print(f"   Available Models: {stats['available_models']}/{stats['total_models']}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Configure Intelligent LLM Routing Strategy")
    parser.add_argument("action", choices=["configure", "test", "show", "set"], help="Action")
    parser.add_argument("--strategy", choices=[s.value for s in RoutingStrategy], help="Routing strategy")

    args = parser.parse_args()

    if args.action == "configure":
        strategy = configure_routing_interactive()
        save_routing_config(strategy)
        test_routing_strategy(strategy)

    elif args.action == "test":
        if args.strategy:
            strategy = RoutingStrategy(args.strategy)
        else:
            strategy = load_routing_config()
        test_routing_strategy(strategy)

    elif args.action == "show":
        strategy = load_routing_config()
        print(f"Current routing strategy: {strategy.value}")
        print(f"Description: {RoutingStrategy.__doc__ or 'No description'}")

    elif args.action == "set":
        if not args.strategy:
            print("❌ Please provide --strategy")
            print(f"Available: {', '.join([s.value for s in RoutingStrategy])}")
            return 1

        strategy = RoutingStrategy(args.strategy)
        save_routing_config(strategy)
        print(f"✅ Routing strategy set to: {strategy.value}")


if __name__ == "__main__":


    main()