#!/usr/bin/env python3
"""
Dynamic Scaling Module

Scales Lumina dynamically based on resources and load.
"We're not enough" - scales to meet demand.

Tags: #DYNAMIC_SCALING #PRODUCTION #AUTO_SCALING @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
import psutil
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DynamicScaling")


class ScaleDirection(Enum):
    """Scaling direction"""
    UP = "up"
    DOWN = "down"
    MAINTAIN = "maintain"


@dataclass
class ResourceMetrics:
    """Resource metrics"""
    cpu_percent: float
    memory_percent: float
    memory_available: float
    disk_usage: float
    network_io: Dict[str, float]
    timestamp: str


@dataclass
class ScalingDecision:
    """Scaling decision"""
    direction: ScaleDirection
    scale_factor: float
    reason: str
    metrics: ResourceMetrics


class DynamicScalingModule:
    """
    Dynamic Scaling Module

    "We're not enough" - scales dynamically to meet demand.
    """

    def __init__(self):
        """Initialize Dynamic Scaling Module"""
        logger.info("📈 Dynamic Scaling Module initialized")
        logger.info('   "We\'re not enough" - Scaling dynamically')

        # Scaling thresholds
        self.scale_up_threshold = 0.75  # 75% resource usage
        self.scale_down_threshold = 0.30  # 30% resource usage
        self.target_utilization = 0.60  # Target 60% utilization

        # Scaling history
        self.scaling_history = []

        logger.info("✅ Dynamic Scaling Module ready")

    def monitor_resources(self) -> ResourceMetrics:
        """
        Monitor system resources.

        Returns:
            Current resource metrics
        """
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()

        metrics = ResourceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available=memory.available / (1024**3),  # GB
            disk_usage=disk.percent,
            network_io={
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            },
            timestamp=datetime.now().isoformat()
        )

        return metrics

    def should_scale(self, metrics: ResourceMetrics) -> ScalingDecision:
        """
        Determine if scaling is needed.

        Args:
            metrics: Current resource metrics

        Returns:
            Scaling decision
        """
        # Calculate overall utilization
        utilization = max(
            metrics.cpu_percent / 100,
            metrics.memory_percent / 100
        )

        # Determine scaling direction
        if utilization > self.scale_up_threshold:
            # Scale up
            scale_factor = utilization / self.target_utilization
            direction = ScaleDirection.UP
            reason = f"High utilization: {utilization:.2%}"
        elif utilization < self.scale_down_threshold:
            # Scale down
            scale_factor = utilization / self.target_utilization
            direction = ScaleDirection.DOWN
            reason = f"Low utilization: {utilization:.2%}"
        else:
            # Maintain
            scale_factor = 1.0
            direction = ScaleDirection.MAINTAIN
            reason = f"Optimal utilization: {utilization:.2%}"

        decision = ScalingDecision(
            direction=direction,
            scale_factor=scale_factor,
            reason=reason,
            metrics=metrics
        )

        logger.info(f"📈 Scaling decision: {direction.value} (factor: {scale_factor:.2f}) - {reason}")

        return decision

    def scale(
        self,
        decision: ScalingDecision,
        current_instances: int = 1
    ) -> Dict[str, Any]:
        """
        Execute scaling action.

        Args:
            decision: Scaling decision
            current_instances: Current number of instances

        Returns:
            Scaling result
        """
        if decision.direction == ScaleDirection.MAINTAIN:
            return {
                'action': 'maintain',
                'instances': current_instances,
                'reason': decision.reason
            }

        # Calculate new instance count
        if decision.direction == ScaleDirection.UP:
            new_instances = max(1, int(current_instances * decision.scale_factor))
            action = 'scale_up'
        else:  # DOWN
            new_instances = max(1, int(current_instances * decision.scale_factor))
            action = 'scale_down'

        # Record scaling
        self.scaling_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'from_instances': current_instances,
            'to_instances': new_instances,
            'reason': decision.reason
        })

        logger.info(f"📈 Scaling {action}: {current_instances} → {new_instances} instances")

        return {
            'action': action,
            'from_instances': current_instances,
            'to_instances': new_instances,
            'reason': decision.reason,
            'scale_factor': decision.scale_factor
        }

    def auto_scale(self, current_instances: int = 1) -> Dict[str, Any]:
        """
        Auto-scale based on current resources.

        Args:
            current_instances: Current number of instances

        Returns:
            Auto-scaling result
        """
        # Monitor resources
        metrics = self.monitor_resources()

        # Determine scaling
        decision = self.should_scale(metrics)

        # Execute scaling
        result = self.scale(decision, current_instances)

        return {
            'metrics': {
                'cpu_percent': metrics.cpu_percent,
                'memory_percent': metrics.memory_percent,
                'utilization': max(metrics.cpu_percent, metrics.memory_percent) / 100
            },
            'decision': {
                'direction': decision.direction.value,
                'scale_factor': decision.scale_factor,
                'reason': decision.reason
            },
            'scaling': result
        }

    def get_scaling_history(self) -> List[Dict[str, Any]]:
        """Get scaling history"""
        return self.scaling_history

    def optimize_for_hardware(self, hardware_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize scaling for specific hardware.

        Args:
            hardware_specs: Hardware specifications

        Returns:
            Optimization recommendations
        """
        recommendations = {
            'cpu_cores': hardware_specs.get('cpu_cores', 1),
            'memory_gb': hardware_specs.get('memory_gb', 4),
            'recommended_instances': 1,
            'tuning': {}
        }

        # Calculate recommended instances based on hardware
        cpu_cores = hardware_specs.get('cpu_cores', 1)
        memory_gb = hardware_specs.get('memory_gb', 4)

        # Recommend instances (1 per 2 CPU cores, or 1 per 4GB RAM, whichever is lower)
        recommended = min(
            max(1, cpu_cores // 2),
            max(1, int(memory_gb // 4))
        )

        recommendations['recommended_instances'] = recommended

        # Tuning recommendations
        if cpu_cores >= 8:
            recommendations['tuning']['high_cpu'] = True
            recommendations['tuning']['parallel_processing'] = True

        if memory_gb >= 16:
            recommendations['tuning']['high_memory'] = True
            recommendations['tuning']['caching'] = True

        logger.info(f"📈 Hardware optimization: {recommended} instances recommended")

        return recommendations


def main():
    """Example usage"""
    print("=" * 80)
    print("📈 DYNAMIC SCALING MODULE")
    print('   "We\'re not enough" - Scaling dynamically')
    print("=" * 80)
    print()

    scaling = DynamicScalingModule()

    # Monitor resources
    print("MONITORING RESOURCES:")
    print("-" * 80)
    metrics = scaling.monitor_resources()
    print(f"CPU: {metrics.cpu_percent:.1f}%")
    print(f"Memory: {metrics.memory_percent:.1f}%")
    print(f"Memory Available: {metrics.memory_available:.2f} GB")
    print()

    # Auto-scale
    print("AUTO-SCALING:")
    print("-" * 80)
    result = scaling.auto_scale(current_instances=1)
    print(f"Direction: {result['decision']['direction']}")
    print(f"Scale Factor: {result['decision']['scale_factor']:.2f}")
    print(f"Action: {result['scaling']['action']}")
    if 'from_instances' in result['scaling']:
        print(f"Instances: {result['scaling']['from_instances']} → {result['scaling']['to_instances']}")
    else:
        print(f"Instances: {result['scaling'].get('instances', 1)} (maintained)")
    print()

    # Hardware optimization
    print("HARDWARE OPTIMIZATION:")
    print("-" * 80)
    hardware = {
        'cpu_cores': 8,
        'memory_gb': 16
    }
    optimization = scaling.optimize_for_hardware(hardware)
    print(f"Recommended instances: {optimization['recommended_instances']}")
    print(f"Tuning: {optimization['tuning']}")
    print()

    print("=" * 80)
    print("📈 Dynamic Scaling - 'We're not enough' - Scaling ready")
    print("=" * 80)


if __name__ == "__main__":


    main()