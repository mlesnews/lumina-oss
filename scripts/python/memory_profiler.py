#!/usr/bin/env python3
"""
Memory Profiler for LUMINA

Analyzes memory usage across all LUMINA components to identify optimization opportunities.

Tags: #MEMORY #OPTIMIZATION #PROFILING #PERFORMANCE @JARVIS @LUMINA
"""

import sys
import psutil
import gc
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

logger = get_logger("MemoryProfiler")


@dataclass
class MemoryUsage:
    """Memory usage information"""
    component: str
    memory_mb: float
    memory_percent: float
    process_count: int
    details: Dict[str, Any] = None


class MemoryProfiler:
    """Profiles memory usage across LUMINA components"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.results: List[MemoryUsage] = []

    def get_system_memory(self) -> Dict[str, Any]:
        """Get overall system memory usage"""
        memory = psutil.virtual_memory()
        return {
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3),
            'used_gb': memory.used / (1024**3),
            'percent': memory.percent,
            'free_gb': memory.free / (1024**3)
        }

    def get_python_processes(self) -> List[Dict[str, Any]]:
        """Get all Python processes with memory details"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent', 'create_time']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline') or []
                    memory_info = proc.info.get('memory_info')

                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(cmdline) if cmdline else '',
                        'memory_mb': memory_info.rss / (1024 * 1024) if memory_info else 0,
                        'memory_vms_mb': memory_info.vms / (1024 * 1024) if memory_info else 0,
                        'cpu_percent': proc.info.get('cpu_percent', 0),
                        'uptime_seconds': (psutil.boot_time() - proc.info.get('create_time', 0)) if proc.info.get('create_time') else 0
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes

    def categorize_processes(self, processes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize processes by component"""
        categories = {
            'monitoring': [],
            'health_checks': [],
            'ask_processing': [],
            'logging': [],
            'fixes': [],
            'diagnostics': [],
            'other': []
        }

        for proc in processes:
            cmdline_lower = proc['cmdline'].lower()
            categorized = False

            # Monitoring
            if any(keyword in cmdline_lower for keyword in ['monitor', 'watchdog', 'live_monitor']):
                categories['monitoring'].append(proc)
                categorized = True

            # Health checks
            if any(keyword in cmdline_lower for keyword in ['health', 'compound_log']):
                categories['health_checks'].append(proc)
                categorized = True

            # Ask processing
            if any(keyword in cmdline_lower for keyword in ['ask_processor', 'ask_live']):
                categories['ask_processing'].append(proc)
                categorized = True

            # Logging
            if any(keyword in cmdline_lower for keyword in ['log', 'compound_log']):
                categories['logging'].append(proc)
                categorized = True

            # Fixes
            if 'fix' in cmdline_lower:
                categories['fixes'].append(proc)
                categorized = True

            # Diagnostics
            if any(keyword in cmdline_lower for keyword in ['diagnostic', 'check_', 'system_resource']):
                categories['diagnostics'].append(proc)
                categorized = True

            if not categorized:
                categories['other'].append(proc)

        return categories

    def analyze_memory_usage(self) -> Dict[str, Any]:
        """Analyze memory usage across all components"""
        system_memory = self.get_system_memory()
        processes = self.get_python_processes()
        categories = self.categorize_processes(processes)

        # Calculate totals per category
        category_totals = {}
        for category, procs in categories.items():
            total_mb = sum(p['memory_mb'] for p in procs)
            category_totals[category] = {
                'total_mb': total_mb,
                'total_gb': total_mb / 1024,
                'process_count': len(procs),
                'avg_mb_per_process': total_mb / len(procs) if procs else 0,
                'processes': procs
            }

        # Overall Python memory
        total_python_mb = sum(p['memory_mb'] for p in processes)
        total_python_gb = total_python_mb / 1024

        # Find largest processes
        largest_processes = sorted(processes, key=lambda x: x['memory_mb'], reverse=True)[:10]

        return {
            'system': system_memory,
            'python_total_mb': total_python_mb,
            'python_total_gb': total_python_gb,
            'python_process_count': len(processes),
            'categories': category_totals,
            'largest_processes': largest_processes,
            'timestamp': datetime.now().isoformat()
        }

    def generate_report(self) -> str:
        """Generate a formatted memory usage report"""
        analysis = self.analyze_memory_usage()

        report = []
        report.append("=" * 80)
        report.append("📊 LUMINA MEMORY PROFILING REPORT")
        report.append("=" * 80)
        report.append("")

        # System memory
        sys_mem = analysis['system']
        report.append("💻 SYSTEM MEMORY:")
        report.append(f"   Total: {sys_mem['total_gb']:.2f} GB")
        report.append(f"   Used: {sys_mem['used_gb']:.2f} GB ({sys_mem['percent']:.1f}%)")
        report.append(f"   Available: {sys_mem['available_gb']:.2f} GB")
        report.append(f"   Free: {sys_mem['free_gb']:.2f} GB")
        report.append("")

        # Python processes
        report.append("🐍 PYTHON PROCESSES:")
        report.append(f"   Total Processes: {analysis['python_process_count']}")
        report.append(f"   Total Memory: {analysis['python_total_gb']:.2f} GB ({analysis['python_total_mb']:.2f} MB)")
        report.append(f"   % of System: {(analysis['python_total_mb'] / 1024) / sys_mem['total_gb'] * 100:.1f}%")
        report.append("")

        # By category
        report.append("📦 MEMORY BY CATEGORY:")
        categories = analysis['categories']
        for category, data in sorted(categories.items(), key=lambda x: x[1]['total_mb'], reverse=True):
            if data['process_count'] > 0:
                report.append(f"   {category.upper()}:")
                report.append(f"      Processes: {data['process_count']}")
                report.append(f"      Total: {data['total_mb']:.2f} MB ({data['total_gb']:.2f} GB)")
                report.append(f"      Avg per process: {data['avg_mb_per_process']:.2f} MB")
                report.append("")

        # Largest processes
        report.append("🔝 TOP 10 LARGEST PROCESSES:")
        for i, proc in enumerate(analysis['largest_processes'], 1):
            cmdline_short = proc['cmdline'][:80] + "..." if len(proc['cmdline']) > 80 else proc['cmdline']
            report.append(f"   {i}. PID {proc['pid']}: {proc['memory_mb']:.2f} MB")
            report.append(f"      {cmdline_short}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on analysis"""
        analysis = self.analyze_memory_usage()
        recommendations = []

        sys_mem = analysis['system']
        python_total_gb = analysis['python_total_gb']
        categories = analysis['categories']

        # Check if Python is using too much memory
        python_percent = (python_total_gb / sys_mem['total_gb']) * 100
        if python_percent > 20:
            recommendations.append(f"⚠️  Python processes using {python_percent:.1f}% of system memory - consider reducing")

        # Check for categories with many processes
        for category, data in categories.items():
            if data['process_count'] > 5:
                recommendations.append(f"⚠️  {category} has {data['process_count']} processes - consider consolidation")

            if data['avg_mb_per_process'] > 100:
                recommendations.append(f"⚠️  {category} processes average {data['avg_mb_per_process']:.1f} MB each - optimize")

        # Check for duplicate processes
        process_cmdlines = {}
        for proc in analysis['largest_processes']:
            cmdline = proc['cmdline']
            if cmdline in process_cmdlines:
                process_cmdlines[cmdline].append(proc['pid'])
            else:
                process_cmdlines[cmdline] = [proc['pid']]

        for cmdline, pids in process_cmdlines.items():
            if len(pids) > 1:
                recommendations.append(f"⚠️  Duplicate process detected: {len(pids)} instances of same script")
                recommendations.append(f"      PIDs: {pids}")

        # Memory pressure
        if sys_mem['percent'] > 80:
            recommendations.append(f"🚨 CRITICAL: System memory at {sys_mem['percent']:.1f}% - immediate action needed")

        if not recommendations:
            recommendations.append("✅ Memory usage appears healthy")

        return recommendations


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Memory Profiler")
        parser.add_argument("--report", action="store_true", help="Generate full report")
        parser.add_argument("--recommendations", action="store_true", help="Show optimization recommendations")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        profiler = MemoryProfiler(project_root)

        if args.json:
            import json
            analysis = profiler.analyze_memory_usage()
            print(json.dumps(analysis, indent=2))
        elif args.recommendations:
            recommendations = profiler.get_optimization_recommendations()
            print("=" * 80)
            print("💡 OPTIMIZATION RECOMMENDATIONS")
            print("=" * 80)
            for rec in recommendations:
                print(f"   {rec}")
            print("=" * 80)
        else:
            report = profiler.generate_report()
            print(report)

            recommendations = profiler.get_optimization_recommendations()
            if recommendations:
                print("\n💡 RECOMMENDATIONS:")
                for rec in recommendations:
                    print(f"   {rec}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()