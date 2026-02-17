#!/usr/bin/env python3
"""
System-Wide Memory Profiler

Analyzes memory usage across ALL processes and programming languages/tools.
Extends memory optimization beyond just Python.

Tags: #MEMORY #OPTIMIZATION #PROFILING #SYSTEM_WIDE @JARVIS @LUMINA
"""

import sys
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SystemMemoryProfiler")


@dataclass
class ProcessInfo:
    """Process information"""
    pid: int
    name: str
    memory_mb: float
    cpu_percent: float
    company: str = ""
    cmdline: str = ""


class SystemMemoryProfiler:
    """Profiles memory usage across all system processes"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.processes: List[ProcessInfo] = []

    def get_all_processes(self, min_memory_mb: float = 10.0) -> List[ProcessInfo]:
        """Get all processes with memory usage above threshold"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'exe', 'cmdline']):
            try:
                memory_info = proc.info.get('memory_info')
                if not memory_info:
                    continue

                memory_mb = memory_info.rss / (1024 * 1024)
                if memory_mb < min_memory_mb:
                    continue

                # Get company/description
                company = ""
                try:
                    if proc.info.get('exe'):
                        try:
                            import win32api
                            info = win32api.GetFileVersionInfo(proc.info['exe'], '\\')
                            company = info.get('StringFileInfo', {}).get('CompanyName', '')
                        except ImportError:
                            # win32api not available, skip
                            pass
                        except Exception:
                            # Other error getting version info, skip
                            pass
                except Exception:
                    pass

                cmdline = ' '.join(proc.info.get('cmdline', []))[:200] if proc.info.get('cmdline') else ''

                processes.append(ProcessInfo(
                    pid=proc.info['pid'],
                    name=proc.info['name'],
                    memory_mb=memory_mb,
                    cpu_percent=proc.info.get('cpu_percent', 0),
                    company=company,
                    cmdline=cmdline
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return sorted(processes, key=lambda x: x.memory_mb, reverse=True)

    def categorize_processes(self, processes: List[ProcessInfo]) -> Dict[str, List[ProcessInfo]]:
        """Categorize processes by type/language"""
        categories = defaultdict(list)

        for proc in processes:
            name_lower = proc.name.lower()
            cmdline_lower = proc.cmdline.lower()

            # Programming languages and runtimes
            if 'python' in name_lower or 'python' in cmdline_lower:
                categories['python'].append(proc)
            elif 'node' in name_lower or 'node' in cmdline_lower or 'npm' in cmdline_lower:
                categories['nodejs'].append(proc)
            elif 'java' in name_lower or 'javaw' in name_lower:
                categories['java'].append(proc)
            elif 'go' in name_lower or 'golang' in name_lower:
                categories['go'].append(proc)
            elif 'rust' in name_lower or 'cargo' in cmdline_lower:
                categories['rust'].append(proc)
            elif 'dotnet' in name_lower or '.net' in cmdline_lower:
                categories['dotnet'].append(proc)
            elif 'powershell' in name_lower or 'pwsh' in name_lower:
                categories['powershell'].append(proc)
            elif 'ruby' in name_lower:
                categories['ruby'].append(proc)
            elif 'php' in name_lower:
                categories['php'].append(proc)
            elif 'perl' in name_lower:
                categories['perl'].append(proc)

            # Development tools
            elif 'cursor' in name_lower:
                categories['cursor_ide'].append(proc)
            elif 'code' in name_lower and 'visual' in cmdline_lower:
                categories['vscode'].append(proc)
            elif 'docker' in name_lower:
                categories['docker'].append(proc)
            elif 'git' in name_lower:
                categories['git'].append(proc)

            # Browsers
            elif 'chrome' in name_lower or 'chromium' in name_lower:
                categories['chrome'].append(proc)
            elif 'firefox' in name_lower:
                categories['firefox'].append(proc)
            elif 'edge' in name_lower or 'msedge' in name_lower:
                categories['edge'].append(proc)

            # AI/ML tools
            elif 'claude' in name_lower:
                categories['claude'].append(proc)
            elif 'ollama' in name_lower:
                categories['ollama'].append(proc)

            # System processes
            elif proc.company == 'Microsoft Corporation' and 'system' in name_lower:
                categories['windows_system'].append(proc)
            elif not proc.company and proc.memory_mb > 100:
                categories['system_services'].append(proc)

            # Other
            else:
                categories['other'].append(proc)

        return dict(categories)

    def analyze_system_memory(self) -> Dict[str, Any]:
        """Analyze system-wide memory usage"""
        system_memory = psutil.virtual_memory()
        processes = self.get_all_processes(min_memory_mb=20.0)
        categories = self.categorize_processes(processes)

        # Calculate totals per category
        category_totals = {}
        for category, procs in categories.items():
            total_mb = sum(p.memory_mb for p in procs)
            category_totals[category] = {
                'total_mb': total_mb,
                'total_gb': total_mb / 1024,
                'process_count': len(procs),
                'avg_mb_per_process': total_mb / len(procs) if procs else 0,
                'processes': [
                    {
                        'pid': p.pid,
                        'name': p.name,
                        'memory_mb': p.memory_mb,
                        'cpu_percent': p.cpu_percent,
                        'company': p.company
                    }
                    for p in procs
                ]
            }

        # Overall totals
        total_memory_mb = sum(p.memory_mb for p in processes)
        total_memory_gb = total_memory_mb / 1024

        # Top processes
        top_processes = processes[:20]

        return {
            'system': {
                'total_gb': system_memory.total / (1024**3),
                'available_gb': system_memory.available / (1024**3),
                'used_gb': system_memory.used / (1024**3),
                'percent': system_memory.percent,
                'free_gb': system_memory.free / (1024**3)
            },
            'profiled_total_mb': total_memory_mb,
            'profiled_total_gb': total_memory_gb,
            'profiled_process_count': len(processes),
            'categories': category_totals,
            'top_processes': [
                {
                    'pid': p.pid,
                    'name': p.name,
                    'memory_mb': p.memory_mb,
                    'cpu_percent': p.cpu_percent,
                    'company': p.company
                }
                for p in top_processes
            ],
            'timestamp': datetime.now().isoformat()
        }

    def generate_report(self) -> str:
        """Generate formatted system memory report"""
        analysis = self.analyze_system_memory()

        report = []
        report.append("=" * 80)
        report.append("📊 SYSTEM-WIDE MEMORY PROFILING REPORT")
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

        # Profiled processes
        report.append("🔍 PROFILED PROCESSES (>20 MB):")
        report.append(f"   Total Processes: {analysis['profiled_process_count']}")
        report.append(f"   Total Memory: {analysis['profiled_total_gb']:.2f} GB ({analysis['profiled_total_mb']:.2f} MB)")
        report.append(f"   % of System: {(analysis['profiled_total_mb'] / 1024) / sys_mem['total_gb'] * 100:.1f}%")
        report.append("")

        # By category
        report.append("📦 MEMORY BY CATEGORY:")
        categories = analysis['categories']
        for category, data in sorted(categories.items(), key=lambda x: x[1]['total_mb'], reverse=True):
            if data['process_count'] > 0:
                report.append(f"   {category.upper().replace('_', ' ')}:")
                report.append(f"      Processes: {data['process_count']}")
                report.append(f"      Total: {data['total_mb']:.2f} MB ({data['total_gb']:.2f} GB)")
                report.append(f"      Avg per process: {data['avg_mb_per_process']:.2f} MB")
                if data['process_count'] <= 5:
                    for proc in data['processes']:
                        report.append(f"         - {proc['name']} (PID {proc['pid']}): {proc['memory_mb']:.1f} MB")
                report.append("")

        # Top processes
        report.append("🔝 TOP 20 LARGEST PROCESSES:")
        for i, proc in enumerate(analysis['top_processes'], 1):
            company_str = f" ({proc['company']})" if proc['company'] else ""
            report.append(f"   {i:2d}. PID {proc['pid']:5d}: {proc['memory_mb']:7.1f} MB - {proc['name']}{company_str}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations for all processes"""
        analysis = self.analyze_system_memory()
        recommendations = []

        sys_mem = analysis['system']
        categories = analysis['categories']

        # Check system memory
        if sys_mem['percent'] > 80:
            recommendations.append(f"🚨 CRITICAL: System memory at {sys_mem['percent']:.1f}% - immediate action needed")
        elif sys_mem['percent'] > 70:
            recommendations.append(f"⚠️  WARNING: System memory at {sys_mem['percent']:.1f}% - consider optimization")

        # Check for categories with high memory usage
        for category, data in categories.items():
            if data['total_mb'] > 500:
                recommendations.append(f"⚠️  {category} using {data['total_mb']:.1f} MB - consider optimization")

            if data['process_count'] > 5 and data['avg_mb_per_process'] > 50:
                recommendations.append(f"⚠️  {category} has {data['process_count']} processes averaging {data['avg_mb_per_process']:.1f} MB each")

        # Check for duplicate processes
        process_names = defaultdict(list)
        for category, data in categories.items():
            for proc in data['processes']:
                process_names[proc['name']].append(proc['pid'])

        for name, pids in process_names.items():
            if len(pids) > 3:
                recommendations.append(f"⚠️  Multiple instances of {name}: {len(pids)} processes (PIDs: {pids[:5]})")

        # Specific recommendations
        if 'cursor_ide' in categories:
            cursor_total = categories['cursor_ide']['total_mb']
            if cursor_total > 1000:
                recommendations.append(f"🚨 Cursor IDE using {cursor_total:.1f} MB - consider closing unused windows/tabs")

        if 'nodejs' in categories:
            node_total = categories['nodejs']['total_mb']
            if node_total > 200:
                recommendations.append(f"⚠️  Node.js processes using {node_total:.1f} MB - check for unnecessary processes")

        if 'docker' in categories:
            docker_total = categories['docker']['total_mb']
            if docker_total > 200:
                recommendations.append(f"⚠️  Docker using {docker_total:.1f} MB - consider stopping unused containers")

        if not recommendations:
            recommendations.append("✅ System memory usage appears healthy")

        return recommendations


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="System-Wide Memory Profiler")
        parser.add_argument("--report", action="store_true", help="Generate full report")
        parser.add_argument("--recommendations", action="store_true", help="Show optimization recommendations")
        parser.add_argument("--json", action="store_true", help="Output as JSON")
        parser.add_argument("--min-mb", type=float, default=20.0, help="Minimum memory to profile (MB)")

        args = parser.parse_args()

        profiler = SystemMemoryProfiler(project_root)

        if args.json:
            import json
            analysis = profiler.analyze_system_memory()
            print(json.dumps(analysis, indent=2))
        elif args.recommendations:
            recommendations = profiler.get_optimization_recommendations()
            print("=" * 80)
            print("💡 SYSTEM-WIDE OPTIMIZATION RECOMMENDATIONS")
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