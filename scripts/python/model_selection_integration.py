#!/usr/bin/env python3
"""
Model Selection Integration Wrapper

Provides easy integration of Model Selector into existing systems.
This wrapper makes it simple to use model selection in AI workflows.

Tags: #INTEGRATION #MODEL_SELECTION #WRAPPER @JARVIS @LUMINA #PEAK
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_model_selector import JARVISModelSelector, ModelSelection, ModelType
    MODEL_SELECTOR_AVAILABLE = True
except ImportError:
    MODEL_SELECTOR_AVAILABLE = False
    JARVISModelSelector = None

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ModelSelectionIntegration")


# Global selector instance (singleton)
_model_selector: Optional[JARVISModelSelector] = None


def get_model_selector() -> Optional[JARVISModelSelector]:
    """Get or create Model Selector instance (singleton)"""
    global _model_selector

    if not MODEL_SELECTOR_AVAILABLE:
        logger.warning("⚠️  Model Selector not available")
        return None

    if _model_selector is None:
        try:
            _model_selector = JARVISModelSelector()
            logger.info("✅ Model Selector initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Model Selector: {e}")
            return None

    return _model_selector


def select_model_for_task(
    task_description: str,
    task_complexity: int = 2,
    urgency: int = 2,
    cost_sensitive: bool = True,
    require_high_quality: bool = False,
    context: Optional[Dict[str, Any]] = None
) -> Optional[ModelSelection]:
    """
    Select optimal model for a task.

    Args:
        task_description: Description of the task
        task_complexity: Complexity level (1-5)
        urgency: Urgency level (1-5)
        cost_sensitive: Whether cost is a concern
        require_high_quality: Whether high quality is required
        context: Additional context for decisioning

    Returns:
        ModelSelection with selected model, or None if selector unavailable
    """
    selector = get_model_selector()
    if not selector:
        logger.warning("⚠️  Model Selector not available")
        return None

    return selector.select_model(
        task_description=task_description,
        task_complexity=task_complexity,
        urgency=urgency,
        cost_sensitive=cost_sensitive,
        require_high_quality=require_high_quality,
        context=context
    )


def get_model_stats():
    """Get model selection statistics"""
    selector = get_model_selector()
    if not selector:
        return {}

    return selector.get_stats()


def should_use_local_ai(task_complexity: int = 2) -> bool:
    """
    Quick check: Should we use local AI for this task?

    Args:
        task_complexity: Complexity level (1-5)

    Returns:
        True if local AI should be used, False if cloud might be needed
    """
    # Simple heuristic: Use local for simple tasks (complexity < 4)
    return task_complexity < 4


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Model Selection Integration")
    parser.add_argument("--task", type=str, help="Task description")
    parser.add_argument("--complexity", type=int, default=2, help="Task complexity (1-5)")
    parser.add_argument("--urgency", type=int, default=2, help="Urgency (1-5)")
    parser.add_argument("--cost-sensitive", action="store_true", help="Cost sensitive")
    parser.add_argument("--high-quality", action="store_true", help="Require high quality")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    if args.stats:
        stats = get_model_stats()
        print("\n📊 Model Selection Statistics:")
        print("=" * 80)
        print(f"  Total Selections: {stats.get('total_selections', 0)}")
        print(f"  Local Selections: {stats.get('local_selections', 0)} ({stats.get('local_rate', 0):.1f}%)")
        print(f"  Cloud Selections: {stats.get('cloud_selections', 0)} ({stats.get('cloud_rate', 0):.1f}%)")
        print(f"  Fallback Selections: {stats.get('fallback_selections', 0)} ({stats.get('fallback_rate', 0):.1f}%)")
        print(f"\n  Provider Usage:")
        for provider, count in stats.get('provider_usage', {}).items():
            print(f"    • {provider}: {count}")
        print("=" * 80)

    elif args.task:
        selection = select_model_for_task(
            task_description=args.task,
            task_complexity=args.complexity,
            urgency=args.urgency,
            cost_sensitive=args.cost_sensitive,
            require_high_quality=args.high_quality
        )

        if selection:
            print("\n🎯 Model Selection:")
            print("=" * 80)
            print(f"  Type: {selection.model_type.value}")
            print(f"  Provider: {selection.provider}")
            print(f"  Model: {selection.model_name}")
            print(f"  Reason: {selection.reason}")
            print(f"  Confidence: {selection.confidence:.2f}")
            if selection.approved_by:
                print(f"  Approved By: {', '.join(selection.approved_by)}")
            if selection.cost_estimate is not None:
                print(f"  Cost Estimate: ${selection.cost_estimate:.4f} per 1K tokens")
            if selection.latency_estimate_ms is not None:
                print(f"  Latency Estimate: {selection.latency_estimate_ms:.0f}ms")
            print("=" * 80)
        else:
            print("❌ Model selection failed")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()