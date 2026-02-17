#!/usr/bin/env python3
"""
LUMINA Live Vehicle Gauges System

Real-time monitoring dashboard with gauges for:
- Speedometer (workflow speed)
- RPM (operations per second)
- Fuel (resource utilization)
- Temperature (system load)
- Weight (data/queue size)
- Intensity (activity level)
- And other critical metrics

@LIVE monitoring with #MONITORING #ESCALATION #DECISIONING #OPERATOR #ARTIFICIAL-INTELLIGENCE

Tags: #live_gauges #monitoring #dashboard #real_time #metrics #ff
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from collections import deque
import threading

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("LUMINALiveVehicleGauges")

try:
    import psutil
except ImportError:
    psutil = None
    logger.warning("psutil not available - system metrics limited")


class GaugeType(Enum):
    """Gauge types"""
    SPEEDOMETER = "speedometer"  # Workflow speed
    RPM = "rpm"  # Operations per second
    FUEL = "fuel"  # Resource utilization
    TEMPERATURE = "temperature"  # System load
    WEIGHT = "weight"  # Data/queue size
    INTENSITY = "intensity"  # Activity level
    PRESSURE = "pressure"  # System pressure
    VOLTAGE = "voltage"  # Power/energy
    FLOW_RATE = "flow_rate"  # Data flow per second
    EFFICIENCY = "efficiency"  # Performance efficiency


class LayerType(Enum):
    """System layer types"""
    APPLICATION = "application"
    WORKFLOW = "workflow"
    SYSTEM = "system"
    NETWORK = "network"
    STORAGE = "storage"
    MEMORY = "memory"
    CPU = "cpu"
    AI = "ai"
    DATABASE = "database"
    API = "api"


@dataclass
class GaugeReading:
    """Single gauge reading"""
    gauge_type: GaugeType
    layer: LayerType
    value: float
    max_value: float
    unit: str
    timestamp: datetime
    percentage: float  # 0-100
    status: str  # normal, warning, critical

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['gauge_type'] = self.gauge_type.value
        result['layer'] = self.layer.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class LayerState:
    """State of a particular layer"""
    layer: LayerType
    gauges: Dict[str, GaugeReading] = field(default_factory=dict)
    workflow_count: int = 0
    active_workflows: List[str] = field(default_factory=list)
    utilization_percent: float = 0.0
    flow_rate_per_second: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['layer'] = self.layer.value
        result['gauges'] = {k: v.to_dict() for k, v in self.gauges.items()}
        result['last_updated'] = self.last_updated.isoformat()
        return result


class LUMINALiveVehicleGauges:
    """
    LUMINA Live Vehicle Gauges System

    Real-time monitoring with gauges for all critical metrics
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize live gauges system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "live_gauges"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Layer states
        self.layer_states: Dict[LayerType, LayerState] = {}

        # Historical readings (for flow rate calculation)
        self.reading_history: deque = deque(maxlen=1000)

        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None

        # Initialize all layers
        self._initialize_layers()

        logger.info("=" * 80)
        logger.info("🚗 LUMINA LIVE VEHICLE GAUGES SYSTEM")
        logger.info("=" * 80)
        logger.info("   Real-time monitoring: @LIVE")
        logger.info("   Layers: Application, Workflow, System, Network, Storage, Memory, CPU, AI")
        logger.info("   Gauges: Speedometer, RPM, Fuel, Temperature, Weight, Intensity")
        logger.info("=" * 80)
        logger.info("")

    def _initialize_layers(self):
        """Initialize all system layers"""
        for layer in LayerType:
            self.layer_states[layer] = LayerState(layer=layer)
        logger.info(f"✅ Initialized {len(self.layer_states)} layers")

    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system-level metrics"""
        metrics = {}

        if psutil:
            # CPU metrics
            metrics['cpu_percent'] = psutil.cpu_percent(interval=0.1)
            metrics['cpu_count'] = psutil.cpu_count()

            # Memory metrics
            mem = psutil.virtual_memory()
            metrics['memory_percent'] = mem.percent
            metrics['memory_available_gb'] = mem.available / (1024**3)
            metrics['memory_total_gb'] = mem.total / (1024**3)

            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics['disk_percent'] = disk.percent
            metrics['disk_free_gb'] = disk.free / (1024**3)

            # Network metrics
            net_io = psutil.net_io_counters()
            metrics['network_bytes_sent'] = net_io.bytes_sent
            metrics['network_bytes_recv'] = net_io.bytes_recv
        else:
            # Default values if psutil not available
            metrics = {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'disk_percent': 0.0,
                'network_bytes_sent': 0,
                'network_bytes_recv': 0
            }

        return metrics

    def calculate_flow_rate(self, layer: LayerType, metric_name: str) -> float:
        """Calculate flow rate (change per second)"""
        # Get recent readings for this layer and metric
        recent = [
            r for r in self.reading_history
            if r.get('layer') == layer.value and r.get('metric') == metric_name
        ][-10:]  # Last 10 readings

        if len(recent) < 2:
            return 0.0

        # Calculate rate of change
        time_diff = (recent[-1]['timestamp'] - recent[0]['timestamp']).total_seconds()
        value_diff = recent[-1]['value'] - recent[0]['value']

        if time_diff > 0:
            return value_diff / time_diff
        return 0.0

    def update_gauge(
        self,
        layer: LayerType,
        gauge_type: GaugeType,
        value: float,
        max_value: float,
        unit: str = ""
    ):
        """Update a gauge reading"""
        percentage = min(100.0, max(0.0, (value / max_value) * 100.0)) if max_value > 0 else 0.0

        # Determine status
        if percentage >= 90:
            status = "critical"
        elif percentage >= 70:
            status = "warning"
        else:
            status = "normal"

        reading = GaugeReading(
            gauge_type=gauge_type,
            layer=layer,
            value=value,
            max_value=max_value,
            unit=unit,
            timestamp=datetime.now(),
            percentage=percentage,
            status=status
        )

        # Store in layer state
        layer_state = self.layer_states[layer]
        layer_state.gauges[gauge_type.value] = reading
        layer_state.last_updated = datetime.now()

        # Store in history for flow rate calculation
        self.reading_history.append({
            'layer': layer.value,
            'metric': gauge_type.value,
            'value': value,
            'timestamp': datetime.now()
        })

        return reading

    def update_workflow_metrics(self):
        """Update workflow layer metrics"""
        # Count active workflows
        workflow_dir = self.project_root / "data" / "workflows"
        active_workflows = []
        workflow_count = 0

        if workflow_dir.exists():
            for file in workflow_dir.glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        if data.get('status') == 'active':
                            active_workflows.append(file.stem)
                            workflow_count += 1
                except:
                    pass

        layer_state = self.layer_states[LayerType.WORKFLOW]
        layer_state.workflow_count = workflow_count
        layer_state.active_workflows = active_workflows[:10]  # Limit to 10

        # Calculate utilization (workflows / max capacity)
        max_workflows = 100  # Assume max capacity
        utilization = min(100.0, (workflow_count / max_workflows) * 100.0)
        layer_state.utilization_percent = utilization

        # Calculate flow rate (workflows per second)
        flow_rate = self.calculate_flow_rate(LayerType.WORKFLOW, "workflow_count")
        layer_state.flow_rate_per_second = flow_rate

        # Update workflow speedometer (workflows per minute)
        self.update_gauge(
            LayerType.WORKFLOW,
            GaugeType.SPEEDOMETER,
            workflow_count * 60,  # workflows per minute
            6000,  # max (100 workflows * 60)
            "wpm"  # workflows per minute
        )

    def update_system_metrics(self):
        """Update system layer metrics"""
        metrics = self.collect_system_metrics()

        # CPU Temperature (RPM equivalent - operations per second)
        cpu_ops_per_sec = metrics.get('cpu_percent', 0.0) * 10  # Estimate
        self.update_gauge(
            LayerType.CPU,
            GaugeType.RPM,
            cpu_ops_per_sec,
            1000,  # max operations per second
            "ops/s"
        )

        # Memory Fuel (utilization)
        self.update_gauge(
            LayerType.MEMORY,
            GaugeType.FUEL,
            metrics.get('memory_percent', 0.0),
            100.0,
            "%"
        )

        # System Temperature (load)
        self.update_gauge(
            LayerType.SYSTEM,
            GaugeType.TEMPERATURE,
            metrics.get('cpu_percent', 0.0),
            100.0,
            "°C"
        )

        # Storage Weight (disk usage)
        self.update_gauge(
            LayerType.STORAGE,
            GaugeType.WEIGHT,
            metrics.get('disk_percent', 0.0),
            100.0,
            "%"
        )

        # Network Intensity (bytes per second)
        net_sent = metrics.get('network_bytes_sent', 0)
        net_recv = metrics.get('network_bytes_recv', 0)
        net_total = net_sent + net_recv

        # Calculate flow rate
        flow_rate = self.calculate_flow_rate(LayerType.NETWORK, "network_bytes")
        self.update_gauge(
            LayerType.NETWORK,
            GaugeType.FLOW_RATE,
            flow_rate,
            1000000000,  # 1 GB/s max
            "B/s"
        )

        # Network Intensity
        self.update_gauge(
            LayerType.NETWORK,
            GaugeType.INTENSITY,
            min(100.0, (net_total / 1000000000) * 100),  # Percentage of 1GB
            100.0,
            "%"
        )

    def update_ai_metrics(self):
        try:
            """Update AI layer metrics"""
            # Count active AI processes/sessions
            ai_sessions_dir = self.project_root / "data" / "agent_chat_sessions"
            ai_count = 0

            if ai_sessions_dir.exists():
                ai_count = len(list(ai_sessions_dir.glob("*.json")))

            # AI Intensity (active sessions)
            self.update_gauge(
                LayerType.AI,
                GaugeType.INTENSITY,
                ai_count,
                100,  # max sessions
                "sessions"
            )

            # AI Flow Rate (sessions per second)
            flow_rate = self.calculate_flow_rate(LayerType.AI, "ai_sessions")
            self.update_gauge(
                LayerType.AI,
                GaugeType.FLOW_RATE,
                flow_rate,
                10,  # max sessions per second
                "sessions/s"
            )

        except Exception as e:
            self.logger.error(f"Error in update_ai_metrics: {e}", exc_info=True)
            raise
    def update_all_gauges(self):
        """Update all gauges"""
        self.update_system_metrics()
        self.update_workflow_metrics()
        self.update_ai_metrics()

        # Update layer states
        for layer_state in self.layer_states.values():
            layer_state.last_updated = datetime.now()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "layers": {
                layer.value: state.to_dict()
                for layer, state in self.layer_states.items()
            },
            "summary": {
                "total_layers": len(self.layer_states),
                "active_gauges": sum(len(state.gauges) for state in self.layer_states.values()),
                "critical_gauges": sum(
                    1 for state in self.layer_states.values()
                    for gauge in state.gauges.values()
                    if gauge.status == "critical"
                ),
                "warning_gauges": sum(
                    1 for state in self.layer_states.values()
                    for gauge in state.gauges.values()
                    if gauge.status == "warning"
                )
            }
        }

    def start_monitoring(self, interval_seconds: float = 1.0):
        """Start continuous monitoring"""
        if self.monitoring_active:
            logger.warning("⚠️  Monitoring already active")
            return

        self.monitoring_active = True

        def monitor_loop():
            while self.monitoring_active:
                try:
                    self.update_all_gauges()
                    time.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")

        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()

        logger.info(f"🚗 Started live monitoring (interval: {interval_seconds}s)")

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        logger.info("🛑 Stopped live monitoring")

    def save_dashboard_snapshot(self):
        try:
            """Save current dashboard snapshot"""
            snapshot_file = self.data_dir / f"dashboard_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            dashboard_data = self.get_dashboard_data()

            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, default=str)

            logger.info(f"💾 Dashboard snapshot saved: {snapshot_file}")
            return snapshot_file

        except Exception as e:
            self.logger.error(f"Error in save_dashboard_snapshot: {e}", exc_info=True)
            raise
    def print_dashboard(self):
        """Print live dashboard to console"""
        dashboard = self.get_dashboard_data()

        print("\n" + "=" * 80)
        print("🚗 LUMINA LIVE VEHICLE GAUGES DASHBOARD")
        print("=" * 80)
        print(f"Timestamp: {dashboard['timestamp']}")
        print("")

        # Summary
        summary = dashboard['summary']
        print("📊 SUMMARY")
        print(f"   Total Layers: {summary['total_layers']}")
        print(f"   Active Gauges: {summary['active_gauges']}")
        print(f"   Critical: {summary['critical_gauges']} ⚠️")
        print(f"   Warning: {summary['warning_gauges']} ⚠️")
        print("")

        # Layer details
        for layer_name, layer_data in dashboard['layers'].items():
            if not layer_data['gauges']:
                continue

            print(f"📊 LAYER: {layer_name.upper()}")
            print("-" * 80)
            print(f"   Workflows: {layer_data['workflow_count']}")
            print(f"   Utilization: {layer_data['utilization_percent']:.1f}%")
            print(f"   Flow Rate: {layer_data['flow_rate_per_second']:.2f}/s")
            print("")

            for gauge_name, gauge in layer_data['gauges'].items():
                status_icon = "🔴" if gauge['status'] == "critical" else "🟡" if gauge['status'] == "warning" else "🟢"
                bar_length = int(gauge['percentage'] / 5)  # 20 chars max
                bar = "█" * bar_length + "░" * (20 - bar_length)

                print(f"   {status_icon} {gauge_name.upper()}: {gauge['value']:.2f} {gauge['unit']}")
                print(f"      [{bar}] {gauge['percentage']:.1f}% ({gauge['status']})")

            print("")

        print("=" * 80)
        print("")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Live Vehicle Gauges")
    parser.add_argument('--update', action='store_true', help='Update all gauges')
    parser.add_argument('--dashboard', action='store_true', help='Show dashboard')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--interval', type=float, default=1.0, help='Monitoring interval (seconds)')
    parser.add_argument('--save', action='store_true', help='Save dashboard snapshot')

    args = parser.parse_args()

    gauges = LUMINALiveVehicleGauges()

    if args.monitor:
        try:
            gauges.start_monitoring(args.interval)
            print("\n🚗 Live monitoring started. Press Ctrl+C to stop.")
            while True:
                gauges.print_dashboard()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            gauges.stop_monitoring()
            print("\n🛑 Monitoring stopped.")

    elif args.update:
        gauges.update_all_gauges()
        logger.info("✅ All gauges updated")
        if args.save:
            gauges.save_dashboard_snapshot()

    elif args.dashboard:
        gauges.update_all_gauges()
        gauges.print_dashboard()
        if args.save:
            gauges.save_dashboard_snapshot()

    if args.update and not args.dashboard and not args.monitor:
        # If only --update, show quick summary
        dashboard = gauges.get_dashboard_data()
        print(f"\n✅ Updated {dashboard['summary']['active_gauges']} gauges across {dashboard['summary']['total_layers']} layers")

    else:
        print("\n" + "=" * 80)
        print("🚗 LUMINA LIVE VEHICLE GAUGES SYSTEM")
        print("=" * 80)
        print("   Use --update to update all gauges")
        print("   Use --dashboard to show dashboard")
        print("   Use --monitor to start continuous monitoring")
        print("   Use --save to save snapshot")
        print("=" * 80)
        print("")


if __name__ == "__main__":


    main()