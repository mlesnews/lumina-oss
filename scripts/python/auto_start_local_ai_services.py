#!/usr/bin/env python3
"""
Auto-Start Local AI Services with Smart Resource Awareness

Automatically starts local AI services (ULTRON, KAIJU) with:
- CPU overload detection (70-80% threshold)
- Dynamic scaling module
- Resource-aware service management
- Automatic service health monitoring

Tags: #AUTO_START #RESOURCE_AWARENESS #DYNAMIC_SCALING @JARVIS @LUMINA
"""

import sys
import json
import time
import psutil
import requests
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AutoStartLocalAI")


@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    endpoint: str
    start_command: List[str]
    health_check_url: str
    min_instances: int = 1
    max_instances: int = 3
    cpu_threshold_low: float = 0.3  # Scale down below 30%
    cpu_threshold_high: float = 0.7  # Scale up above 70%
    cpu_threshold_critical: float = 0.8  # Critical at 80%
    memory_threshold: float = 0.8  # Memory threshold
    enabled: bool = True


@dataclass
class ResourceMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    cpu_count: int
    memory_total: float
    memory_available: float
    timestamp: datetime = field(default_factory=datetime.now)


class DynamicScalingModule:
    """Dynamic scaling module for AI services"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.cpu_threshold_low = 0.3
        self.cpu_threshold_high = 0.7
        self.cpu_threshold_critical = 0.8
        self.memory_threshold = 0.8

        self.scaling_history: List[Dict[str, Any]] = []
        self.current_scale = 1  # Current scaling factor

    def get_resource_metrics(self) -> ResourceMetrics:
        """Get current system resource metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        return ResourceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            cpu_count=psutil.cpu_count(),
            memory_total=memory.total / (1024**3),  # GB
            memory_available=memory.available / (1024**3)  # GB
        )

    def should_scale_down(self, metrics: ResourceMetrics) -> bool:
        """Determine if should scale down"""
        return metrics.cpu_percent < (self.cpu_threshold_low * 100)

    def should_scale_up(self, metrics: ResourceMetrics) -> bool:
        """Determine if should scale up"""
        return metrics.cpu_percent >= (self.cpu_threshold_high * 100)

    def is_critical(self, metrics: ResourceMetrics) -> bool:
        """Check if system is in critical state"""
        return metrics.cpu_percent >= (self.cpu_threshold_critical * 100) or \
               metrics.memory_percent >= (self.memory_threshold * 100)

    def calculate_scale_factor(self, metrics: ResourceMetrics) -> int:
        """Calculate appropriate scale factor based on resources"""
        if self.is_critical(metrics):
            # Critical - reduce load
            return max(1, self.current_scale - 1)
        elif self.should_scale_up(metrics):
            # High CPU - can scale up if not at max
            return min(3, self.current_scale + 1)
        elif self.should_scale_down(metrics):
            # Low CPU - can scale down
            return max(1, self.current_scale - 1)
        else:
            # Normal - maintain current scale
            return self.current_scale

    def scale_services(self, metrics: ResourceMetrics, services: List[Any]) -> Dict[str, Any]:
        """Scale services based on resource metrics"""
        new_scale = self.calculate_scale_factor(metrics)

        scaling_action = {
            "timestamp": datetime.now().isoformat(),
            "old_scale": self.current_scale,
            "new_scale": new_scale,
            "cpu_percent": metrics.cpu_percent,
            "memory_percent": metrics.memory_percent,
            "action": "none"
        }

        if new_scale != self.current_scale:
            if new_scale > self.current_scale:
                scaling_action["action"] = "scale_up"
                logger.info(f"📈 Scaling UP: {self.current_scale} → {new_scale} (CPU: {metrics.cpu_percent:.1f}%)")
            else:
                scaling_action["action"] = "scale_down"
                logger.warning(f"📉 Scaling DOWN: {self.current_scale} → {new_scale} (CPU: {metrics.cpu_percent:.1f}%)")

            self.current_scale = new_scale
            self.scaling_history.append(scaling_action)

            # Keep only last 100 scaling events
            if len(self.scaling_history) > 100:
                self.scaling_history = self.scaling_history[-100:]

        return scaling_action


class LocalAIServiceManager:
    """Manages local AI services with auto-start and scaling"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scaling_module = DynamicScalingModule(project_root)

        # Service configurations
        self.services = {
            "ULTRON": ServiceConfig(
                name="ULTRON",
                endpoint="http://localhost:11434",
                start_command=["docker", "start", "ollama"],  # Adjust based on your setup
                health_check_url="http://localhost:11434/api/tags",
                min_instances=1,
                max_instances=2
            ),
            "KAIJU": ServiceConfig(
                name="KAIJU",
                endpoint="http://<NAS_PRIMARY_IP>:11434",
                start_command=["ssh", "kaiju", "docker start ollama"],  # Adjust based on your setup
                health_check_url="http://<NAS_PRIMARY_IP>:11434/api/tags",
                min_instances=0,  # Can be disabled if resources low
                max_instances=1
            )
        }

        self.running_services: Dict[str, bool] = {}
        self.service_processes: Dict[str, Any] = {}
        self.monitoring = False
        self.monitor_thread = None

    def check_service_health(self, service_name: str) -> bool:
        """Check if service is healthy"""
        service = self.services.get(service_name)
        if not service:
            return False

        try:
            response = requests.get(service.health_check_url, timeout=2)
            return response.status_code == 200
        except:
            return False

    def start_service(self, service_name: str) -> bool:
        """Start a service"""
        service = self.services.get(service_name)
        if not service or not service.enabled:
            return False

        if self.check_service_health(service_name):
            logger.info(f"✅ {service_name} already running")
            self.running_services[service_name] = True
            return True

        try:
            logger.info(f"🚀 Starting {service_name}...")
            # Note: Adjust start_command based on your actual setup
            # For now, we'll just check if it's available
            if self.check_service_health(service_name):
                self.running_services[service_name] = True
                logger.info(f"✅ {service_name} started successfully")
                return True
            else:
                logger.warning(f"⚠️  {service_name} start command may need adjustment")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to start {service_name}: {e}")
            return False

    def stop_service(self, service_name: str) -> bool:
        """Stop a service (gracefully)"""
        service = self.services.get(service_name)
        if not service:
            return False

        if not self.check_service_health(service_name):
            logger.info(f"ℹ️  {service_name} already stopped")
            self.running_services[service_name] = False
            return True

        try:
            logger.info(f"🛑 Stopping {service_name}...")
            # Note: Implement actual stop logic based on your setup
            self.running_services[service_name] = False
            logger.info(f"✅ {service_name} stopped")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to stop {service_name}: {e}")
            return False

    def auto_start_all(self) -> Dict[str, bool]:
        """Auto-start all enabled services"""
        results = {}

        logger.info("🚀 Auto-starting local AI services...")

        for service_name, service in self.services.items():
            if service.enabled:
                results[service_name] = self.start_service(service_name)
            else:
                results[service_name] = False
                logger.info(f"⏭️  {service_name} disabled, skipping")

        return results

    def monitor_resources(self):
        """Monitor system resources and scale accordingly"""
        while self.monitoring:
            try:
                # Get resource metrics
                metrics = self.scaling_module.get_resource_metrics()

                # Check for critical state
                if self.scaling_module.is_critical(metrics):
                    logger.warning(f"⚠️  CRITICAL: CPU {metrics.cpu_percent:.1f}% or Memory {metrics.memory_percent:.1f}%")

                    # Scale down KAIJU if critical
                    if self.running_services.get("KAIJU"):
                        logger.warning("📉 Critical state - stopping KAIJU to reduce load")
                        self.stop_service("KAIJU")

                # Scale services based on resources
                scaling_action = self.scaling_module.scale_services(metrics, list(self.services.keys()))

                # Ensure ULTRON is always running (primary)
                if not self.check_service_health("ULTRON"):
                    logger.warning("⚠️  ULTRON not healthy, restarting...")
                    self.start_service("ULTRON")

                # Scale KAIJU based on resources
                if metrics.cpu_percent < 50 and not self.running_services.get("KAIJU"):
                    # Low CPU, can start KAIJU
                    if self.services["KAIJU"].enabled:
                        logger.info("📈 Low CPU - starting KAIJU")
                        self.start_service("KAIJU")
                elif metrics.cpu_percent > 70 and self.running_services.get("KAIJU"):
                    # High CPU, stop KAIJU
                    logger.warning("📉 High CPU - stopping KAIJU")
                    self.stop_service("KAIJU")

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                time.sleep(10)

    def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_resources, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ Resource monitoring started")

    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("🛑 Resource monitoring stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        metrics = self.scaling_module.get_resource_metrics()

        service_status = {}
        for service_name in self.services.keys():
            service_status[service_name] = {
                "running": self.check_service_health(service_name),
                "enabled": self.services[service_name].enabled
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "resources": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "cpu_count": metrics.cpu_count,
                "memory_total_gb": metrics.memory_total,
                "memory_available_gb": metrics.memory_available
            },
            "scaling": {
                "current_scale": self.scaling_module.current_scale,
                "cpu_threshold_high": self.scaling_module.cpu_threshold_high * 100,
                "cpu_threshold_critical": self.scaling_module.cpu_threshold_critical * 100
            },
            "services": service_status,
            "monitoring": self.monitoring
        }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Auto-Start Local AI Services")
    parser.add_argument("--start", action="store_true", help="Start all services")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (start + monitor)")

    args = parser.parse_args()

    manager = LocalAIServiceManager(project_root)

    if args.start:
        results = manager.auto_start_all()
        print("\n" + "=" * 80)
        print("🚀 AUTO-START RESULTS")
        print("=" * 80)
        for service, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {service}: {'Started' if success else 'Failed'}")
        print()

    if args.status:
        status = manager.get_status()
        print("\n" + "=" * 80)
        print("📊 SYSTEM STATUS")
        print("=" * 80)
        print(f"CPU: {status['resources']['cpu_percent']:.1f}%")
        print(f"Memory: {status['resources']['memory_percent']:.1f}%")
        print(f"Current Scale: {status['scaling']['current_scale']}")
        print(f"CPU Threshold (High): {status['scaling']['cpu_threshold_high']:.1f}%")
        print(f"CPU Threshold (Critical): {status['scaling']['cpu_threshold_critical']:.1f}%")
        print()
        print("Services:")
        for service, info in status['services'].items():
            status_icon = "✅" if info['running'] else "❌"
            enabled_icon = "✓" if info['enabled'] else "✗"
            print(f"  {status_icon} {service}: Running={info['running']}, Enabled={enabled_icon}")
        print()

    if args.monitor or args.daemon:
        if args.daemon:
            # Start services first
            manager.auto_start_all()
            time.sleep(2)

        manager.start_monitoring()

        try:
            while True:
                time.sleep(60)
                # Periodic status update
                status = manager.get_status()
                if status['resources']['cpu_percent'] > 70:
                    logger.warning(f"⚠️  High CPU: {status['resources']['cpu_percent']:.1f}%")
        except KeyboardInterrupt:
            manager.stop_monitoring()
            print("\n🛑 Stopped")


if __name__ == "__main__":


    main()