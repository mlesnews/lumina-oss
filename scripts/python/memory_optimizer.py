#!/usr/bin/env python3
"""
Memory Optimizer for LUMINA

Implements memory optimization strategies to keep footprint balanced and efficient.

Tags: #MEMORY #OPTIMIZATION #EFFICIENCY #PERFORMANCE @JARVIS @LUMINA
"""

import sys
import gc
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MemoryOptimizer")


@dataclass
class MemoryBudget:
    """Memory budget configuration"""
    max_python_processes: int = 8  # Conservative limit (was 10)
    max_memory_per_process_mb: float = 50.0  # Target: 50 MB per process
    max_total_python_mb: float = 400.0  # Target: 400 MB total (6.3% of 64GB system)
    warning_threshold_mb: float = 300.0  # Warn at 300 MB
    system_memory_target_percent: float = 15.0  # Target: 15% system memory usage


class MemoryOptimizer:
    """Optimizes memory usage across LUMINA"""

    def __init__(self, project_root: Path, budget: Optional[MemoryBudget] = None):
        self.project_root = Path(project_root)
        self.budget = budget or MemoryBudget()
        self.optimizations_applied = []

    def force_garbage_collection(self) -> Dict[str, Any]:
        """Force garbage collection to free memory"""
        before = self._get_python_memory()

        # Collect all generations
        collected = gc.collect()

        after = self._get_python_memory()
        freed_mb = before - after

        result = {
            'collected_objects': collected,
            'freed_mb': freed_mb,
            'before_mb': before,
            'after_mb': after
        }

        if freed_mb > 0:
            logger.info(f"🧹 Garbage collection freed {freed_mb:.2f} MB")
            self.optimizations_applied.append(f"GC freed {freed_mb:.2f} MB")

        return result

    def _get_python_memory(self) -> float:
        """Get total Python process memory in MB"""
        total = 0.0
        for proc in psutil.process_iter(['name', 'memory_info']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    memory_info = proc.info.get('memory_info')
                    if memory_info:
                        total += memory_info.rss / (1024 * 1024)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return total

    def optimize_process_count(self) -> Dict[str, Any]:
        """Optimize by reducing process count"""
        try:
            from .process_watchdog import ProcessWatchdog
        except ImportError:
            from process_watchdog import ProcessWatchdog

        watchdog = ProcessWatchdog(max_processes=self.budget.max_python_processes)
        processes = watchdog.get_python_processes()
        count = len(processes)

        result = {
            'current_count': count,
            'target_count': self.budget.max_python_processes,
            'action_taken': False,
            'killed': 0
        }

        if count > self.budget.max_python_processes:
            result['killed'] = watchdog.kill_excess_processes()
            result['action_taken'] = True
            logger.info(f"🛑 Reduced process count from {count} to {self.budget.max_python_processes}")
            self.optimizations_applied.append(f"Reduced processes: {count} → {self.budget.max_python_processes}")

        return result

    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize memory usage of running processes"""
        try:
            from .memory_profiler import MemoryProfiler
        except ImportError:
            from memory_profiler import MemoryProfiler

        profiler = MemoryProfiler(self.project_root)
        analysis = profiler.analyze_memory_usage()

        total_mb = analysis['python_total_mb']
        processes = profiler.get_python_processes()

        result = {
            'current_total_mb': total_mb,
            'target_total_mb': self.budget.max_total_python_mb,
            'over_budget': total_mb > self.budget.max_total_python_mb,
            'recommendations': []
        }

        # Find processes over budget
        over_budget_processes = [
            p for p in processes 
            if p['memory_mb'] > self.budget.max_memory_per_process_mb
        ]

        if over_budget_processes:
            result['recommendations'].append(
                f"{len(over_budget_processes)} process(es) exceed {self.budget.max_memory_per_process_mb} MB limit"
            )
            for proc in over_budget_processes:
                result['recommendations'].append(
                    f"  PID {proc['pid']}: {proc['memory_mb']:.1f} MB - {proc['cmdline'][:60]}"
                )

        if total_mb > self.budget.warning_threshold_mb:
            result['recommendations'].append(
                f"Total Python memory ({total_mb:.1f} MB) exceeds warning threshold ({self.budget.warning_threshold_mb} MB)"
            )

        if total_mb > self.budget.max_total_python_mb:
            result['recommendations'].append(
                f"🚨 CRITICAL: Total Python memory ({total_mb:.1f} MB) exceeds budget ({self.budget.max_total_python_mb} MB)"
            )

        return result

    def get_optimization_plan(self) -> Dict[str, Any]:
        """Get comprehensive optimization plan"""
        try:
            from .memory_profiler import MemoryProfiler
        except ImportError:
            from memory_profiler import MemoryProfiler

        profiler = MemoryProfiler(self.project_root)
        analysis = profiler.analyze_memory_usage()

        plan = {
            'current_state': {
                'total_python_mb': analysis['python_total_mb'],
                'process_count': analysis['python_process_count'],
                'system_memory_percent': analysis['system']['percent']
            },
            'target_state': {
                'total_python_mb': self.budget.max_total_python_mb,
                'process_count': self.budget.max_python_processes,
                'system_memory_percent': self.budget.system_memory_target_percent
            },
            'optimizations': []
        }

        # Process count optimization
        if analysis['python_process_count'] > self.budget.max_python_processes:
            plan['optimizations'].append({
                'type': 'reduce_processes',
                'current': analysis['python_process_count'],
                'target': self.budget.max_python_processes,
                'priority': 'high'
            })

        # Memory optimization
        if analysis['python_total_mb'] > self.budget.max_total_python_mb:
            plan['optimizations'].append({
                'type': 'reduce_memory',
                'current_mb': analysis['python_total_mb'],
                'target_mb': self.budget.max_total_python_mb,
                'priority': 'critical'
            })

        # Large process optimization
        large_processes = [
            p for p in analysis['largest_processes'][:5]
            if p['memory_mb'] > self.budget.max_memory_per_process_mb
        ]

        if large_processes:
            plan['optimizations'].append({
                'type': 'optimize_large_processes',
                'processes': [
                    {
                        'pid': p['pid'],
                        'memory_mb': p['memory_mb'],
                        'cmdline': p['cmdline'][:80]
                    }
                    for p in large_processes
                ],
                'priority': 'medium'
            })

        # Consolidation opportunities
        categories = analysis['categories']
        for category, data in categories.items():
            if data['process_count'] > 3:
                plan['optimizations'].append({
                    'type': 'consolidate',
                    'category': category,
                    'process_count': data['process_count'],
                    'total_mb': data['total_mb'],
                    'priority': 'medium',
                    'recommendation': f"Consolidate {data['process_count']} {category} processes into unified system"
                })

        return plan

    def apply_optimizations(self, plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply optimization plan"""
        if plan is None:
            plan = self.get_optimization_plan()

        results = {
            'optimizations_applied': [],
            'memory_freed_mb': 0.0,
            'processes_reduced': 0,
            'success': True
        }

        # Force GC first
        gc_result = self.force_garbage_collection()
        if gc_result['freed_mb'] > 0:
            results['memory_freed_mb'] += gc_result['freed_mb']
            results['optimizations_applied'].append('garbage_collection')

        # Apply optimizations from plan
        for opt in plan.get('optimizations', []):
            if opt['type'] == 'reduce_processes':
                proc_result = self.optimize_process_count()
                if proc_result['action_taken']:
                    results['processes_reduced'] += proc_result['killed']
                    results['optimizations_applied'].append('reduce_processes')

            elif opt['type'] == 'reduce_memory':
                # Memory reduction is handled by process reduction
                results['optimizations_applied'].append('memory_reduction')

        return results


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Memory Optimizer")
        parser.add_argument("--plan", action="store_true", help="Show optimization plan")
        parser.add_argument("--apply", action="store_true", help="Apply optimizations")
        parser.add_argument("--gc", action="store_true", help="Force garbage collection only")
        parser.add_argument("--budget", type=str, help="Custom budget JSON file")

        args = parser.parse_args()

        budget = MemoryBudget()
        if args.budget:
            import json
            with open(args.budget, 'r') as f:
                budget_data = json.load(f)
                budget = MemoryBudget(**budget_data)

        optimizer = MemoryOptimizer(project_root, budget)

        if args.gc:
            result = optimizer.force_garbage_collection()
            print(f"🧹 Garbage collection: Freed {result['freed_mb']:.2f} MB")

        elif args.plan:
            plan = optimizer.get_optimization_plan()
            print("=" * 80)
            print("📋 MEMORY OPTIMIZATION PLAN")
            print("=" * 80)
            print(f"\nCurrent State:")
            print(f"   Python Memory: {plan['current_state']['total_python_mb']:.2f} MB")
            print(f"   Process Count: {plan['current_state']['process_count']}")
            print(f"   System Memory: {plan['current_state']['system_memory_percent']:.1f}%")
            print(f"\nTarget State:")
            print(f"   Python Memory: {plan['target_state']['total_python_mb']:.2f} MB")
            print(f"   Process Count: {plan['target_state']['process_count']}")
            print(f"   System Memory: {plan['target_state']['system_memory_percent']:.1f}%")
            print(f"\nOptimizations Needed: {len(plan['optimizations'])}")
            for i, opt in enumerate(plan['optimizations'], 1):
                print(f"\n{i}. {opt['type'].upper()} (Priority: {opt['priority']})")
                if opt['type'] == 'reduce_processes':
                    print(f"   Reduce from {opt['current']} to {opt['target']} processes")
                elif opt['type'] == 'reduce_memory':
                    print(f"   Reduce from {opt['current_mb']:.1f} MB to {opt['target_mb']:.1f} MB")
                elif opt['type'] == 'consolidate':
                    print(f"   {opt['recommendation']}")
                    print(f"   Current: {opt['process_count']} processes, {opt['total_mb']:.1f} MB")

        elif args.apply:
            print("🔧 Applying optimizations...")
            plan = optimizer.get_optimization_plan()
            results = optimizer.apply_optimizations(plan)

            print("=" * 80)
            print("✅ OPTIMIZATION RESULTS")
            print("=" * 80)
            print(f"Optimizations Applied: {len(results['optimizations_applied'])}")
            print(f"Memory Freed: {results['memory_freed_mb']:.2f} MB")
            print(f"Processes Reduced: {results['processes_reduced']}")
            print(f"Success: {results['success']}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()