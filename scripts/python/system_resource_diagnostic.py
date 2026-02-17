#!/usr/bin/env python3
"""
System Resource Diagnostic

Diagnoses system resource issues that could cause freezes.
Checks CPU, memory, disk, and process counts.

Tags: #DIAGNOSTIC #SYSTEM_STABILITY #RESOURCE_MANAGEMENT @JARVIS @LUMINA
"""

import sys
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

def diagnose_system_resources() -> Dict[str, Any]:
    """Diagnose system resource usage"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "cpu": {},
        "memory": {},
        "disk": {},
        "processes": {},
        "warnings": [],
        "critical_issues": []
    }

    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    results["cpu"] = {
        "percent": cpu_percent,
        "count": cpu_count,
        "status": "CRITICAL" if cpu_percent > 90 else "WARNING" if cpu_percent > 70 else "OK"
    }
    if cpu_percent > 90:
        results["critical_issues"].append(f"CPU usage critical: {cpu_percent}%")
    elif cpu_percent > 70:
        results["warnings"].append(f"CPU usage high: {cpu_percent}%")

    # Memory
    memory = psutil.virtual_memory()
    results["memory"] = {
        "total_gb": round(memory.total / (1024**3), 2),
        "available_gb": round(memory.available / (1024**3), 2),
        "used_gb": round(memory.used / (1024**3), 2),
        "percent": memory.percent,
        "status": "CRITICAL" if memory.percent > 90 else "WARNING" if memory.percent > 70 else "OK"
    }
    if memory.percent > 90:
        results["critical_issues"].append(f"Memory usage critical: {memory.percent}% ({round(memory.used / (1024**3), 2)}GB used)")
    elif memory.percent > 70:
        results["warnings"].append(f"Memory usage high: {memory.percent}%")

    # Disk
    disk = psutil.disk_usage(str(project_root))
    results["disk"] = {
        "total_gb": round(disk.total / (1024**3), 2),
        "used_gb": round(disk.used / (1024**3), 2),
        "free_gb": round(disk.free / (1024**3), 2),
        "percent": round((disk.used / disk.total) * 100, 2),
        "status": "CRITICAL" if (disk.used / disk.total) * 100 > 90 else "WARNING" if (disk.used / disk.total) * 100 > 75 else "OK"
    }

    # Python processes
    python_processes = []
    total_python_memory = 0
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                mem_mb = proc.info['memory_info'].rss / (1024**2)
                total_python_memory += mem_mb
                cmdline = proc.info.get('cmdline') or []
                cmdline_str = ' '.join(cmdline[:3]) if cmdline else 'N/A'
                python_processes.append({
                    "pid": proc.info['pid'],
                    "memory_mb": round(mem_mb, 2),
                    "cpu_percent": proc.info.get('cpu_percent', 0),
                    "cmdline": cmdline_str
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    results["processes"] = {
        "python_count": len(python_processes),
        "total_python_memory_mb": round(total_python_memory, 2),
        "total_python_memory_gb": round(total_python_memory / 1024, 2),
        "processes": python_processes[:20]  # Top 20
    }

    if len(python_processes) > 10:
        results["critical_issues"].append(f"Too many Python processes: {len(python_processes)}")
    if total_python_memory > 1000:  # > 1GB
        results["critical_issues"].append(f"Python processes using too much memory: {round(total_python_memory / 1024, 2)}GB")

    # Overall status
    if results["critical_issues"]:
        results["overall_status"] = "CRITICAL"
    elif results["warnings"]:
        results["overall_status"] = "WARNING"
    else:
        results["overall_status"] = "OK"

    return results

def print_diagnostic(results: Dict[str, Any]):
    """Print diagnostic results"""
    print("\n" + "=" * 80)
    print("🔍 SYSTEM RESOURCE DIAGNOSTIC")
    print("=" * 80)
    print(f"📅 Timestamp: {results['timestamp']}")
    print(f"📊 Overall Status: {results['overall_status']}")
    print()

    print("💻 CPU:")
    print(f"   Usage: {results['cpu']['percent']}% ({results['cpu']['status']})")
    print(f"   Cores: {results['cpu']['count']}")
    print()

    print("🧠 Memory:")
    print(f"   Total: {results['memory']['total_gb']}GB")
    print(f"   Used: {results['memory']['used_gb']}GB ({results['memory']['percent']}%)")
    print(f"   Available: {results['memory']['available_gb']}GB")
    print(f"   Status: {results['memory']['status']}")
    print()

    print("💾 Disk:")
    print(f"   Total: {results['disk']['total_gb']}GB")
    print(f"   Used: {results['disk']['used_gb']}GB ({results['disk']['percent']}%)")
    print(f"   Free: {results['disk']['free_gb']}GB")
    print(f"   Status: {results['disk']['status']}")
    print()

    print("🐍 Python Processes:")
    print(f"   Count: {results['processes']['python_count']}")
    print(f"   Total Memory: {results['processes']['total_python_memory_gb']}GB")
    print()

    if results['processes']['python_count'] > 0:
        print("   Top Processes:")
        for proc in results['processes']['processes'][:10]:
            print(f"   - PID {proc['pid']}: {proc['memory_mb']}MB CPU:{proc['cpu_percent']}% {proc['cmdline']}")
    print()

    if results['critical_issues']:
        print("🚨 CRITICAL ISSUES:")
        for issue in results['critical_issues']:
            print(f"   ❌ {issue}")
        print()

    if results['warnings']:
        print("⚠️  WARNINGS:")
        for warning in results['warnings']:
            print(f"   ⚠️  {warning}")
        print()

    print("=" * 80)

if __name__ == "__main__":
    print("🔍 Running system resource diagnostic...")
    results = diagnose_system_resources()
    print_diagnostic(results)

    # Save to file
    import json
    diagnostic_file = project_root / "data" / "system_diagnostics" / f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    diagnostic_file.parent.mkdir(parents=True, exist_ok=True)
    with open(diagnostic_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Saved diagnostic to: {diagnostic_file}")
