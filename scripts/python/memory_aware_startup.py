#!/usr/bin/env python3
"""
Memory-Aware Startup System

Ensures LUMINA components start only if memory budget allows.
Prevents running at the edge of memory limits.

Tags: #MEMORY #OPTIMIZATION #STARTUP #SAFETY @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MemoryAwareStartup")

try:
    from memory_optimizer import MemoryOptimizer, MemoryBudget
    from memory_profiler import MemoryProfiler
    from startup_safety_check import check_system_safe
except ImportError:
    # If running as module
    from .memory_optimizer import MemoryOptimizer, MemoryBudget
    from .memory_profiler import MemoryProfiler
    from .startup_safety_check import check_system_safe


def load_memory_budget() -> MemoryBudget:
    """Load memory budget from config"""
    budget_file = project_root / "config" / "memory_budget.json"

    if budget_file.exists():
        try:
            with open(budget_file, 'r') as f:
                config = json.load(f)
                targets = config.get('memory_budget', {}).get('targets', {})
                return MemoryBudget(
                    max_python_processes=targets.get('max_python_processes', 8),
                    max_memory_per_process_mb=targets.get('max_memory_per_process_mb', 50.0),
                    max_total_python_mb=targets.get('max_total_python_mb', 400.0),
                    warning_threshold_mb=targets.get('warning_threshold_mb', 300.0),
                    system_memory_target_percent=targets.get('system_memory_target_percent', 15.0)
                )
        except Exception as e:
            logger.warning(f"Failed to load budget config: {e}, using defaults")

    return MemoryBudget()


def check_memory_budget(component: str, required_mb: float = 50.0) -> tuple[bool, str]:
    """
    Check if memory budget allows starting a component.
    Returns (can_start, message)
    """
    budget = load_memory_budget()
    profiler = MemoryProfiler(project_root)
    analysis = profiler.analyze_memory_usage()

    current_total_mb = analysis['python_total_mb']
    current_process_count = analysis['python_process_count']

    # Check process count
    if current_process_count >= budget.max_python_processes:
        return False, f"Cannot start {component}: {current_process_count} processes (limit: {budget.max_python_processes})"

    # Check total memory
    projected_total = current_total_mb + required_mb
    if projected_total > budget.max_total_python_mb:
        return False, f"Cannot start {component}: Projected memory {projected_total:.1f} MB exceeds budget {budget.max_total_python_mb} MB"

    # Check warning threshold
    if projected_total > budget.warning_threshold_mb:
        return True, f"⚠️  WARNING: Starting {component} will bring total to {projected_total:.1f} MB (warning: {budget.warning_threshold_mb} MB)"

    return True, f"✅ Memory budget allows starting {component}"


def optimize_before_start(component: str) -> Dict[str, Any]:
    """Optimize memory before starting a component"""
    budget = load_memory_budget()
    optimizer = MemoryOptimizer(project_root, budget)

    # Get current state
    profiler = MemoryProfiler(project_root)
    analysis = profiler.analyze_memory_usage()

    before_mb = analysis['python_total_mb']
    before_count = analysis['python_process_count']

    # Apply optimizations
    plan = optimizer.get_optimization_plan()
    results = optimizer.apply_optimizations(plan)

    # Get new state
    analysis_after = profiler.analyze_memory_usage()
    after_mb = analysis_after['python_total_mb']
    after_count = analysis_after['python_process_count']

    return {
        'optimized': True,
        'memory_freed_mb': before_mb - after_mb,
        'processes_reduced': before_count - after_count,
        'before_mb': before_mb,
        'after_mb': after_mb,
        'before_count': before_count,
        'after_count': after_count
    }


def can_start_component(component: str, required_mb: float = 50.0, auto_optimize: bool = True) -> tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Check if component can start, with optional auto-optimization.
    Returns (can_start, message, optimization_results)
    """
    # First check system safety
    is_safe, safety_msg = check_system_safe()
    if not is_safe:
        return False, f"System not safe: {safety_msg}", None

    # Check memory budget
    can_start, budget_msg = check_memory_budget(component, required_mb)

    if not can_start and auto_optimize:
        # Try optimizing
        logger.info(f"⚠️  Memory budget exceeded, attempting optimization...")
        opt_results = optimize_before_start(component)

        # Check again after optimization
        can_start, budget_msg = check_memory_budget(component, required_mb)

        if can_start:
            return True, f"✅ Optimized and can start {component}", opt_results
        else:
            return False, f"❌ Cannot start {component} even after optimization: {budget_msg}", opt_results

    return can_start, budget_msg, None


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Memory-Aware Startup System")
    parser.add_argument("--component", type=str, required=True, help="Component name to check")
    parser.add_argument("--required-mb", type=float, default=50.0, help="Required memory in MB")
    parser.add_argument("--no-optimize", action="store_true", help="Don't auto-optimize")
    parser.add_argument("--check-only", action="store_true", help="Only check, don't optimize")

    args = parser.parse_args()

    can_start, message, opt_results = can_start_component(
        args.component,
        args.required_mb,
        auto_optimize=not args.no_optimize
    )

    print("=" * 80)
    print("🧠 MEMORY-AWARE STARTUP CHECK")
    print("=" * 80)
    print(f"Component: {args.component}")
    print(f"Required Memory: {args.required_mb} MB")
    print(f"Can Start: {'✅ YES' if can_start else '❌ NO'}")
    print(f"Message: {message}")

    if opt_results:
        print(f"\nOptimization Results:")
        print(f"   Memory Freed: {opt_results['memory_freed_mb']:.2f} MB")
        print(f"   Processes Reduced: {opt_results['processes_reduced']}")
        print(f"   Before: {opt_results['before_mb']:.1f} MB, {opt_results['before_count']} processes")
        print(f"   After: {opt_results['after_mb']:.1f} MB, {opt_results['after_count']} processes")

    print("=" * 80)

    return 0 if can_start else 1


if __name__ == "__main__":


    sys.exit(main())