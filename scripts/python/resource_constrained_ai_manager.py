#!/usr/bin/env python3
"""
Resource Constrained AI Manager

Manages AI clusters when resources are limited (96% disk, low memory, etc.).
Automatically scales down/up based on available resources.

Tags: #RESOURCE_MANAGEMENT #CONSTRAINED #AUTO_SCALE @JARVIS @LUMINA
"""

import sys
import time
import psutil
import shutil
import requests
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import threading

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ResourceConstrainedAI")


class ResourceMonitor:
    """Monitor system resources"""

    def __init__(self):
        self.critical_disk = 95.0
        self.warning_disk = 90.0
        self.critical_memory = 90.0
        self.warning_memory = 80.0
        self.critical_cpu = 90.0
        self.warning_cpu = 80.0

    def get_resources(self) -> Dict[str, Any]:
        """Get current resource status"""
        disk = shutil.disk_usage("C:")
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)

        disk_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024**3)

        return {
            "disk": {
                "percent_used": disk_percent,
                "free_gb": disk_free_gb,
                "is_critical": disk_percent >= self.critical_disk,
                "is_warning": disk_percent >= self.warning_disk
            },
            "memory": {
                "percent_used": memory.percent,
                "available_gb": memory.available / (1024**3),
                "is_critical": memory.percent >= self.critical_memory,
                "is_warning": memory.percent >= self.warning_memory
            },
            "cpu": {
                "percent": cpu,
                "is_critical": cpu >= self.critical_cpu,
                "is_warning": cpu >= self.warning_cpu
            },
            "timestamp": datetime.now().isoformat()
        }


class ResourceConstrainedAIManager:
    """Manage AI clusters under resource constraints"""

    def __init__(self):
        self.monitor = ResourceMonitor()
        self.clusters = {
            "ollama": {
                "endpoint": "http://localhost:11434",
                "priority": 1,  # Highest priority
                "min_resources": {"disk_gb": 10, "memory_gb": 2}
            },
            "iron_legion": {
                "endpoint": "http://localhost:3000",
                "priority": 2,  # Lower priority
                "min_resources": {"disk_gb": 50, "memory_gb": 8}
            }
        }
        self.running_clusters = {}
        self.monitoring = False

    def can_run_cluster(self, cluster_name: str, resources: Dict[str, Any]) -> bool:
        """Check if cluster can run with current resources"""
        cluster = self.clusters.get(cluster_name)
        if not cluster:
            return False

        min_disk = cluster["min_resources"]["disk_gb"]
        min_memory = cluster["min_resources"]["memory_gb"]

        disk_ok = resources["disk"]["free_gb"] >= min_disk
        memory_ok = resources["memory"]["available_gb"] >= min_memory

        # Critical resources - can't run
        if resources["disk"]["is_critical"] or resources["memory"]["is_critical"]:
            return False

        return disk_ok and memory_ok

    def get_available_clusters(self, resources: Dict[str, Any]) -> List[str]:
        """Get list of clusters that can run"""
        available = []

        for name, cluster in self.clusters.items():
            if self.can_run_cluster(name, resources):
                available.append(name)

        # Sort by priority
        available.sort(key=lambda x: self.clusters[x]["priority"])
        return available

    def scale_clusters(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Scale clusters based on resources"""
        actions = {
            "timestamp": datetime.now().isoformat(),
            "actions": [],
            "running": []
        }

        # Check what can run
        available = self.get_available_clusters(resources)

        # Stop clusters that can't run
        for name in list(self.running_clusters.keys()):
            if name not in available:
                logger.warning(f"📉 Stopping {name} - insufficient resources")
                actions["actions"].append({
                    "action": "stop",
                    "cluster": name,
                    "reason": "insufficient_resources"
                })
                del self.running_clusters[name]

        # Start clusters that can run (priority order)
        for name in available:
            if name not in self.running_clusters:
                # Check if cluster is actually running
                cluster = self.clusters[name]
                try:
                    response = requests.get(f"{cluster['endpoint']}/api/tags", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✅ {name} is running")
                        self.running_clusters[name] = True
                        actions["running"].append(name)
                except:
                    logger.warning(f"⚠️  {name} not accessible - may need to start")
                    actions["actions"].append({
                        "action": "start_needed",
                        "cluster": name
                    })

        return actions

    def monitor_and_scale(self):
        """Monitor resources and scale clusters"""
        self.monitoring = True
        logger.info("🤖 Starting resource-constrained monitoring...")

        while self.monitoring:
            try:
                resources = self.monitor.get_resources()

                # Log critical warnings
                if resources["disk"]["is_critical"]:
                    logger.warning(f"🚨 CRITICAL: Disk at {resources['disk']['percent_used']:.1f}%")
                elif resources["disk"]["is_warning"]:
                    logger.warning(f"⚠️  WARNING: Disk at {resources['disk']['percent_used']:.1f}%")

                if resources["memory"]["is_critical"]:
                    logger.warning(f"🚨 CRITICAL: Memory at {resources['memory']['percent_used']:.1f}%")

                # Scale clusters
                actions = self.scale_clusters(resources)

                if actions["actions"]:
                    for action in actions["actions"]:
                        logger.info(f"   {action['action']}: {action.get('cluster', 'unknown')}")

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(30)

    def start_monitoring(self):
        """Start monitoring in background thread"""
        thread = threading.Thread(target=self.monitor_and_scale, daemon=True)
        thread.start()
        logger.info("✅ Resource monitoring started")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        logger.info("🛑 Resource monitoring stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        resources = self.monitor.get_resources()
        actions = self.scale_clusters(resources)

        return {
            "resources": resources,
            "clusters": {
                "available": self.get_available_clusters(resources),
                "running": list(self.running_clusters.keys())
            },
            "actions": actions
        }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Resource Constrained AI Manager")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")

    args = parser.parse_args()

    manager = ResourceConstrainedAIManager()

    if args.monitor or args.daemon:
        manager.start_monitoring()

        if args.daemon:
            print("🤖 Running as daemon...")
            print("   Press Ctrl+C to stop")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                manager.stop_monitoring()
                print("\n🛑 Stopped")

    elif args.status:
        status = manager.get_status()
        print("\n" + "=" * 80)
        print("📊 RESOURCE STATUS")
        print("=" * 80)
        print()

        res = status["resources"]
        print(f"💾 Disk: {res['disk']['percent_used']:.1f}% ({res['disk']['free_gb']:.1f}GB free)")
        print(f"🧠 Memory: {res['memory']['percent_used']:.1f}% ({res['memory']['available_gb']:.1f}GB free)")
        print(f"⚡ CPU: {res['cpu']['percent']:.1f}%")
        print()

        clusters = status["clusters"]
        print(f"✅ Available: {', '.join(clusters['available']) if clusters['available'] else 'None'}")
        print(f"🚀 Running: {', '.join(clusters['running']) if clusters['running'] else 'None'}")
        print()

    else:
        parser.print_help()


if __name__ == "__main__":

    main()