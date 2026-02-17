#!/usr/bin/env python3
"""
Quick Start Local AI Services

One-command startup for all local AI services with monitoring.

Usage:
    python scripts/python/quick_start_local_ai.py
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from auto_start_local_ai_services import LocalAIServiceManager
import time

def main():
    """Quick start all services"""
    print("=" * 80)
    print("🚀 QUICK START: LOCAL AI SERVICES")
    print("=" * 80)
    print()

    manager = LocalAIServiceManager(project_root)

    # Start all services
    print("Starting services...")
    results = manager.auto_start_all()

    for service, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {service}")

    print()

    # Show status
    status = manager.get_status()
    print("System Resources:")
    print(f"  CPU: {status['resources']['cpu_percent']:.1f}%")
    print(f"  Memory: {status['resources']['memory_percent']:.1f}%")
    print()

    # Start monitoring
    print("Starting resource monitoring...")
    manager.start_monitoring()
    print("✅ Monitoring active")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)

    try:
        while True:
            time.sleep(60)
            # Show periodic status
            status = manager.get_status()
            cpu = status['resources']['cpu_percent']
            if cpu > 70:
                print(f"⚠️  High CPU: {cpu:.1f}%")
    except KeyboardInterrupt:
        manager.stop_monitoring()
        print("\n🛑 Stopped")

if __name__ == "__main__":


    main()