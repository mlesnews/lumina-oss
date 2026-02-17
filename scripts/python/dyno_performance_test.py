#!/usr/bin/env python3
"""
DYNO Performance Testing Framework
Part of Performance Engineering & Capacity Management Team

Finds MIN/MAX capacity bounds and calibrates to the Goldilocks Zone.
"""

import json
import subprocess
import time
import psutil
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum
import argparse


class TestPhase(Enum):
    BASELINE = "BASELINE"
    RAMP_UP = "RAMP_UP"
    RAMP_DOWN = "RAMP_DOWN"
    GOLDILOCKS_CALIBRATION = "GOLDILOCKS_CALIBRATION"
    BURN_IN = "BURN_IN"
    IDLE = "IDLE"


@dataclass
class PerformanceMetrics:
    timestamp: str
    cursor_memory_mb: int
    cursor_process_count: int
    system_cpu_percent: float
    system_memory_percent: float
    econnreset_errors: int = 0
    response_time_ms: float = 0.0
    capacity_percent: int = 50
    zone: str = "UNKNOWN"


@dataclass
class GoldilocksZone:
    """The optimal operating range"""
    min_capacity: int = 25
    max_capacity: int = 100
    optimal_capacity: int = 50

    # Thresholds
    cursor_memory_min_mb: int = 1000
    cursor_memory_optimal_mb: int = 3000
    cursor_memory_max_mb: int = 6000

    cpu_min_percent: float = 20.0
    cpu_optimal_percent: float = 55.0
    cpu_max_percent: float = 85.0

    memory_min_percent: float = 30.0
    memory_optimal_percent: float = 50.0
    memory_max_percent: float = 80.0

    def classify_zone(self, metrics: PerformanceMetrics) -> str:
        """Determine if we're TOO_COLD, GOLDILOCKS, or TOO_HOT"""
        if (metrics.cursor_memory_mb > self.cursor_memory_max_mb or
            metrics.system_cpu_percent > self.cpu_max_percent or
            metrics.system_memory_percent > self.memory_max_percent or
            metrics.econnreset_errors > 0):
            return "TOO_HOT"

        if (metrics.cursor_memory_mb < self.cursor_memory_min_mb and
            metrics.system_cpu_percent < self.cpu_min_percent and
            metrics.system_memory_percent < self.memory_min_percent):
            return "TOO_COLD"

        return "GOLDILOCKS"


class DynoPerformanceTest:
    """DYNO Performance Testing Framework"""

    def __init__(self):
        self.lumina_path = Path(__file__).parent.parent.parent
        self.data_path = self.lumina_path / "data" / "performance_metrics"
        self.data_path.mkdir(parents=True, exist_ok=True)

        self.goldilocks = GoldilocksZone()
        self.current_phase = TestPhase.IDLE
        self.metrics_history: List[PerformanceMetrics] = []
        self.test_results: Dict = {}

        self._load_capacity_config()

    def _load_capacity_config(self):
        try:
            """Load system capacity configuration"""
            config_path = self.lumina_path / "config" / "system_capacity.json"
            if config_path.exists():
                with open(config_path) as f:
                    self.capacity_config = json.load(f)
            else:
                self.capacity_config = {}

        except Exception as e:
            self.logger.error(f"Error in _load_capacity_config: {e}", exc_info=True)
            raise
    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        # Get Cursor processes
        cursor_procs = [p for p in psutil.process_iter(['name', 'memory_info'])
                       if p.info['name'] and 'cursor' in p.info['name'].lower()]

        cursor_memory = sum(p.info['memory_info'].rss for p in cursor_procs) // (1024 * 1024)
        cursor_count = len(cursor_procs)

        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent

        # Get current capacity from config
        capacity = self.capacity_config.get('system_capacity_configuration', {}).get('target_capacity_percent', 50)

        metrics = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            cursor_memory_mb=cursor_memory,
            cursor_process_count=cursor_count,
            system_cpu_percent=cpu_percent,
            system_memory_percent=memory_percent,
            capacity_percent=capacity
        )

        # Classify zone
        metrics.zone = self.goldilocks.classify_zone(metrics)

        return metrics

    def print_status_line(self, metrics: PerformanceMetrics):
        """Print Unix-style status line"""
        zone_colors = {
            "TOO_COLD": "\033[94m",  # Blue
            "GOLDILOCKS": "\033[92m",  # Green
            "TOO_HOT": "\033[91m"  # Red
        }
        reset = "\033[0m"

        color = zone_colors.get(metrics.zone, "")

        status_map = {
            "TOO_COLD": "[COLD  ]",
            "GOLDILOCKS": "[  OK  ]",
            "TOO_HOT": "[HOT!! ]"
        }

        status = status_map.get(metrics.zone, "[????  ]")

        print(f"{color}{status}{reset} Cursor: {metrics.cursor_memory_mb}MB ({metrics.cursor_process_count} procs) | "
              f"CPU: {metrics.system_cpu_percent:.1f}% | Mem: {metrics.system_memory_percent:.1f}% | "
              f"Capacity: {metrics.capacity_percent}% | Zone: {metrics.zone}")

    def run_baseline(self, duration_minutes: int = 5):
        """Phase 1: Establish baseline at current capacity"""
        print("\n" + "=" * 70)
        print("  DYNO PERFORMANCE TEST - PHASE 1: BASELINE")
        print("=" * 70)
        print(f"  Duration: {duration_minutes} minutes at current capacity")
        print("=" * 70 + "\n")

        self.current_phase = TestPhase.BASELINE
        start_time = time.time()

        while (time.time() - start_time) < (duration_minutes * 60):
            metrics = self.collect_metrics()
            self.metrics_history.append(metrics)
            self.print_status_line(metrics)
            time.sleep(10)  # Sample every 10 seconds

        # Calculate baseline stats
        if self.metrics_history:
            avg_memory = sum(m.cursor_memory_mb for m in self.metrics_history) / len(self.metrics_history)
            avg_cpu = sum(m.system_cpu_percent for m in self.metrics_history) / len(self.metrics_history)
            hot_count = sum(1 for m in self.metrics_history if m.zone == "TOO_HOT")

            self.test_results['baseline'] = {
                'avg_cursor_memory_mb': round(avg_memory, 0),
                'avg_cpu_percent': round(avg_cpu, 1),
                'samples': len(self.metrics_history),
                'hot_samples': hot_count,
                'stable': hot_count == 0
            }

            print("\n" + "-" * 70)
            print("BASELINE RESULTS:")
            print(f"  Average Cursor Memory: {avg_memory:.0f} MB")
            print(f"  Average CPU: {avg_cpu:.1f}%")
            print(f"  Stability: {'STABLE ✓' if hot_count == 0 else f'UNSTABLE ({hot_count} hot samples)'}")
            print("-" * 70)

        return self.test_results.get('baseline', {})

    def run_ramp_up(self, increments: List[int] = None, hold_seconds: int = 60):
        """Phase 2: Ramp up to find MAX capacity"""
        if increments is None:
            increments = [60, 70, 80, 90, 100]

        print("\n" + "=" * 70)
        print("  DYNO PERFORMANCE TEST - PHASE 2: RAMP UP")
        print("=" * 70)
        print(f"  Increments: {increments}%")
        print(f"  Hold time per increment: {hold_seconds}s")
        print("=" * 70 + "\n")

        self.current_phase = TestPhase.RAMP_UP
        max_stable_capacity = 50  # Start assumption
        breaking_point = None

        for target_capacity in increments:
            print(f"\n--- Testing {target_capacity}% capacity ---")

            # Update capacity config (simulate)
            self._update_capacity_target(target_capacity)

            # Hold and measure
            start_time = time.time()
            samples = []

            while (time.time() - start_time) < hold_seconds:
                metrics = self.collect_metrics()
                metrics.capacity_percent = target_capacity
                samples.append(metrics)
                self.print_status_line(metrics)
                time.sleep(5)

            # Evaluate
            hot_count = sum(1 for m in samples if m.zone == "TOO_HOT")

            if hot_count == 0:
                max_stable_capacity = target_capacity
                print(f"[  OK  ] {target_capacity}% capacity: STABLE")
            else:
                breaking_point = target_capacity
                print(f"[FAILED] {target_capacity}% capacity: UNSTABLE ({hot_count} hot samples)")
                print(f"         Breaking point identified at {target_capacity}%")
                break

        self.test_results['ramp_up'] = {
            'max_stable_capacity': max_stable_capacity,
            'breaking_point': breaking_point,
            'tested_increments': increments
        }

        # Reset to safe capacity
        self._update_capacity_target(50)

        return self.test_results['ramp_up']

    def run_goldilocks_calibration(self):
        """Phase 4: Find the Goldilocks sweet spot"""
        print("\n" + "=" * 70)
        print("  DYNO PERFORMANCE TEST - PHASE 4: GOLDILOCKS CALIBRATION")
        print("=" * 70)

        self.current_phase = TestPhase.GOLDILOCKS_CALIBRATION

        # Use results from ramp up/down if available
        max_cap = self.test_results.get('ramp_up', {}).get('max_stable_capacity', 80)
        min_cap = self.test_results.get('ramp_down', {}).get('min_functional_capacity', 30)

        # Goldilocks = center of safe range with 20% headroom from max
        goldilocks_capacity = min(
            (min_cap + max_cap) // 2,
            int(max_cap * 0.8)  # 20% headroom
        )

        self.goldilocks.optimal_capacity = goldilocks_capacity
        self.goldilocks.min_capacity = min_cap
        self.goldilocks.max_capacity = max_cap

        self.test_results['goldilocks'] = {
            'min_capacity': min_cap,
            'max_capacity': max_cap,
            'optimal_capacity': goldilocks_capacity,
            'headroom_percent': 20,
            'recommended_mode': 'PERFORMANCE_TUNING' if goldilocks_capacity <= 60 else 'DYNO'
        }

        print(f"\n  GOLDILOCKS ZONE CALIBRATED:")
        print(f"  ├── Minimum Safe Capacity:  {min_cap}%")
        print(f"  ├── Maximum Safe Capacity:  {max_cap}%")
        print(f"  └── OPTIMAL (Goldilocks):   {goldilocks_capacity}%")
        print(f"\n  Recommended Mode: {self.test_results['goldilocks']['recommended_mode']}")

        return self.test_results['goldilocks']

    def _update_capacity_target(self, target: int):
        try:
            """Update the capacity target in config"""
            config_path = self.lumina_path / "config" / "system_capacity.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)

                config['system_capacity_configuration']['target_capacity_percent'] = target
                config['system_capacity_configuration']['last_updated'] = datetime.now().isoformat()

                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _update_capacity_target: {e}", exc_info=True)
            raise
    def get_current_status(self):
        """Get current system status"""
        metrics = self.collect_metrics()

        print("\n" + "=" * 70)
        print("  DYNO PERFORMANCE STATUS")
        print("=" * 70)
        self.print_status_line(metrics)
        print("=" * 70)

        return asdict(metrics)

    def generate_report(self):
        try:
            """Generate comprehensive performance report"""
            report = {
                'generated': datetime.now().isoformat(),
                'current_status': self.get_current_status(),
                'test_results': self.test_results,
                'goldilocks_zone': {
                    'min': self.goldilocks.min_capacity,
                    'optimal': self.goldilocks.optimal_capacity,
                    'max': self.goldilocks.max_capacity
                },
                'recommendations': []
            }

            # Add recommendations based on current state
            current = self.collect_metrics()
            if current.zone == "TOO_HOT":
                report['recommendations'].append("IMMEDIATE: Run cursor_health_recovery.ps1 -KillHeavy")
                report['recommendations'].append("Reduce capacity to 50% or lower")
            elif current.zone == "TOO_COLD":
                report['recommendations'].append("Consider enabling more services")
                report['recommendations'].append("System may be ready for DYNO mode testing")
            else:
                report['recommendations'].append("System in Goldilocks zone - maintain current state")

            # Save report
            report_path = self.data_path / f"dyno_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)

            print(f"\nReport saved to: {report_path}")
            return report


        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}", exc_info=True)
            raise
def main():
    parser = argparse.ArgumentParser(description='DYNO Performance Testing Framework')
    parser.add_argument('--mode', choices=['baseline', 'ramp_up', 'ramp_down', 'calibrate', 'full'],
                       help='Test mode to run')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--report', action='store_true', help='Generate performance report')
    parser.add_argument('--abort', action='store_true', help='Emergency abort and reset to 50%')
    parser.add_argument('--duration', type=int, default=5, help='Duration in minutes for baseline')

    args = parser.parse_args()

    dyno = DynoPerformanceTest()

    if args.abort:
        print("🛑 EMERGENCY ABORT - Resetting to 50% capacity")
        dyno._update_capacity_target(50)
        print("[  OK  ] Capacity reset to 50%")
        return

    if args.status:
        dyno.get_current_status()
        return

    if args.report:
        dyno.generate_report()
        return

    if args.mode == 'baseline':
        dyno.run_baseline(args.duration)
    elif args.mode == 'ramp_up':
        dyno.run_ramp_up()
    elif args.mode == 'calibrate':
        dyno.run_goldilocks_calibration()
    elif args.mode == 'full':
        print("Running full DYNO test sequence...")
        dyno.run_baseline(args.duration)
        dyno.run_ramp_up()
        dyno.run_goldilocks_calibration()
        dyno.generate_report()
    else:
        # Default: show status
        dyno.get_current_status()


if __name__ == "__main__":


    main()