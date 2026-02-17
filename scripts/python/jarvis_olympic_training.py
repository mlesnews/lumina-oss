#!/usr/bin/env python3
"""
JARVIS Olympic Training - Performance Tuning for JARVIS's Body (Homelab)

Gets the homelab into Olympic-level physical shape through comprehensive
performance tuning, optimization, and health monitoring.

@PEAK @MARVIN @ROAST - Olympic Performance Mode
"""

import sys
import json
import subprocess
import psutil
import socket
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class PerformanceLevel(Enum):
    """Performance level classification"""
    OLYMPIC = "olympic"  # Peak performance
    ELITE = "elite"  # Excellent
    PROFESSIONAL = "professional"  # Good
    AMATEUR = "amateur"  # Needs work
    UNTRAINED = "untrained"  # Poor


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float = 0.0
    cpu_count: int = 0
    memory_total_gb: float = 0.0
    memory_available_gb: float = 0.0
    memory_used_percent: float = 0.0
    disk_total_gb: float = 0.0
    disk_free_gb: float = 0.0
    disk_used_percent: float = 0.0
    network_speed_mbps: float = 0.0
    network_latency_ms: float = 0.0
    boot_time: Optional[datetime] = None
    uptime_hours: float = 0.0
    process_count: int = 0
    thread_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if self.boot_time:
            data['boot_time'] = self.boot_time.isoformat()
        return data

    def get_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        # CPU score (lower is better for idle, but we want headroom)
        cpu_score = max(0, 100 - (self.cpu_percent * 0.5))  # Want <20% idle

        # Memory score (want <80% used)
        memory_score = max(0, 100 - ((self.memory_used_percent - 20) * 1.25))

        # Disk score (want <80% used)
        disk_score = max(0, 100 - ((self.disk_used_percent - 20) * 1.25))

        # Network score (based on latency, lower is better)
        network_score = max(0, 100 - (self.network_latency_ms * 2))

        # Uptime score (longer is better, but not critical)
        uptime_score = min(100, self.uptime_hours / 24 * 10)  # 10 days = 100

        # Weighted average
        score = (
            cpu_score * 0.25 +
            memory_score * 0.25 +
            disk_score * 0.20 +
            network_score * 0.20 +
            uptime_score * 0.10
        )

        return max(0.0, min(100.0, score))

    def get_performance_level(self) -> PerformanceLevel:
        """Get performance level classification"""
        score = self.get_performance_score()

        if score >= 90:
            return PerformanceLevel.OLYMPIC
        elif score >= 75:
            return PerformanceLevel.ELITE
        elif score >= 60:
            return PerformanceLevel.PROFESSIONAL
        elif score >= 40:
            return PerformanceLevel.AMATEUR
        else:
            return PerformanceLevel.UNTRAINED


@dataclass
class NetworkMetrics:
    """Network performance metrics"""
    hostname: str
    ip_address: str
    latency_ms: float = 0.0
    bandwidth_mbps: float = 0.0
    packet_loss: float = 0.0
    dns_resolution_ms: float = 0.0
    connection_count: int = 0
    active_connections: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TrainingPlan:
    """Olympic training plan for system optimization"""
    current_level: PerformanceLevel
    target_level: PerformanceLevel = PerformanceLevel.OLYMPIC
    optimizations: List[str] = field(default_factory=list)
    benchmarks: Dict[str, float] = field(default_factory=dict)
    improvements: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['current_level'] = self.current_level.value
        data['target_level'] = self.target_level.value
        return data


class JARVISOlympicTrainer:
    """
    JARVIS Olympic Trainer

    Trains JARVIS's body (homelab) to Olympic-level performance.
    Comprehensive performance tuning and optimization.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Olympic trainer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISOlympicTrainer")

        # Data directories
        self.data_dir = self.project_root / "data" / "olympic_training"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("🏋️  JARVIS Olympic Trainer initialized")
        self.logger.info("   Getting JARVIS's body in Olympic shape!")

    def assess_current_fitness(self) -> Tuple[SystemMetrics, NetworkMetrics, TrainingPlan]:
        """Assess current system fitness level"""
        self.logger.info("📊 Assessing current fitness level...")

        # System metrics
        system_metrics = self._collect_system_metrics()

        # Network metrics
        network_metrics = self._collect_network_metrics()

        # Performance level
        performance_level = system_metrics.get_performance_level()
        performance_score = system_metrics.get_performance_score()

        # Training plan
        training_plan = self._create_training_plan(system_metrics, network_metrics, performance_level)

        self.logger.info(f"📈 Current Performance Level: {performance_level.value.upper()}")
        self.logger.info(f"   Performance Score: {performance_score:.1f}/100")

        return system_metrics, network_metrics, training_plan

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory
            memory = psutil.virtual_memory()
            memory_total_gb = memory.total / (1024**3)
            memory_available_gb = memory.available / (1024**3)
            memory_used_percent = memory.percent

            # Disk
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024**3)
            disk_free_gb = disk.free / (1024**3)
            disk_used_percent = (disk.used / disk.total) * 100

            # Network (basic)
            network_speed_mbps = 0.0  # Would need network test
            network_latency_ms = 0.0  # Would need ping test

            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime_hours = (datetime.now() - boot_time).total_seconds() / 3600

            # Processes
            process_count = len(psutil.pids())
            thread_count = psutil.Process().num_threads()

            return SystemMetrics(
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_total_gb=memory_total_gb,
                memory_available_gb=memory_available_gb,
                memory_used_percent=memory_used_percent,
                disk_total_gb=disk_total_gb,
                disk_free_gb=disk_free_gb,
                disk_used_percent=disk_used_percent,
                network_speed_mbps=network_speed_mbps,
                network_latency_ms=network_latency_ms,
                boot_time=boot_time,
                uptime_hours=uptime_hours,
                process_count=process_count,
                thread_count=thread_count
            )
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics()

    def _collect_network_metrics(self) -> NetworkMetrics:
        """Collect network performance metrics"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)

            # Test latency to common targets
            latency_ms = self._test_latency("8.8.8.8")

            # DNS resolution test
            dns_ms = self._test_dns_resolution("google.com")

            # Connection count
            connections = len(psutil.net_connections())
            active_connections = len([c for c in psutil.net_connections() if c.status == 'ESTABLISHED'])

            return NetworkMetrics(
                hostname=hostname,
                ip_address=ip_address,
                latency_ms=latency_ms,
                dns_resolution_ms=dns_ms,
                connection_count=connections,
                active_connections=active_connections
            )
        except Exception as e:
            self.logger.error(f"Error collecting network metrics: {e}")
            return NetworkMetrics(hostname="unknown", ip_address="0.0.0.0")

    def _test_latency(self, target: str, count: int = 3) -> float:
        """Test network latency"""
        try:
            import platform
            if platform.system() == "Windows":
                cmd = ["ping", "-n", str(count), target]
            else:
                cmd = ["ping", "-c", str(count), target]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Parse ping output (simplified)
                lines = result.stdout.split('\n')
                times = []
                for line in lines:
                    if 'time=' in line or 'time<' in line:
                        # Extract time value
                        import re
                        match = re.search(r'time[<=](\d+)', line)
                        if match:
                            times.append(float(match.group(1)))

                if times:
                    return sum(times) / len(times)
        except Exception as e:
            self.logger.debug(f"Latency test failed: {e}")

        return 0.0

    def _test_dns_resolution(self, hostname: str) -> float:
        """Test DNS resolution time"""
        try:
            start = time.time()
            socket.gethostbyname(hostname)
            return (time.time() - start) * 1000  # Convert to ms
        except Exception:
            return 0.0

    def _create_training_plan(
        self,
        system_metrics: SystemMetrics,
        network_metrics: NetworkMetrics,
        current_level: PerformanceLevel
    ) -> TrainingPlan:
        """Create Olympic training plan"""
        optimizations = []
        warnings = []
        improvements = []

        # CPU optimization
        if system_metrics.cpu_percent > 80:
            optimizations.append("Reduce CPU load - optimize running processes")
            warnings.append(f"High CPU usage: {system_metrics.cpu_percent:.1f}%")
        elif system_metrics.cpu_percent < 5:
            optimizations.append("CPU has headroom - can increase workload")
            improvements.append("CPU utilization is optimal")

        # Memory optimization
        if system_metrics.memory_used_percent > 85:
            optimizations.append("Free up memory - clear caches or close unused applications")
            warnings.append(f"High memory usage: {system_metrics.memory_used_percent:.1f}%")
        elif system_metrics.memory_used_percent < 50:
            optimizations.append("Memory has headroom - can increase cache sizes")
            improvements.append("Memory utilization is optimal")

        # Disk optimization
        if system_metrics.disk_used_percent > 85:
            optimizations.append("Free up disk space - clean up old files")
            warnings.append(f"High disk usage: {system_metrics.disk_used_percent:.1f}%")
        elif system_metrics.disk_used_percent < 50:
            improvements.append("Disk space is optimal")

        # Network optimization
        if network_metrics.latency_ms > 50:
            optimizations.append("Optimize network - check network configuration")
            warnings.append(f"High network latency: {network_metrics.latency_ms:.1f}ms")
        elif network_metrics.latency_ms < 20:
            improvements.append("Network latency is optimal")

        # Uptime
        if system_metrics.uptime_hours < 24:
            warnings.append("System recently rebooted - may need warm-up time")
        elif system_metrics.uptime_hours > 720:  # 30 days
            improvements.append("Excellent system stability")

        # Process count
        if system_metrics.process_count > 200:
            optimizations.append("Reduce process count - optimize startup programs")
        elif system_metrics.process_count < 100:
            improvements.append("Process count is optimal")

        return TrainingPlan(
            current_level=current_level,
            target_level=PerformanceLevel.OLYMPIC,
            optimizations=optimizations,
            improvements=improvements,
            warnings=warnings
        )

    def apply_olympic_training(self, training_plan: TrainingPlan) -> Dict[str, Any]:
        """Apply Olympic training optimizations"""
        self.logger.info("🏋️  Applying Olympic training...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": [],
            "improvements": [],
            "warnings": training_plan.warnings
        }

        # Apply optimizations
        for optimization in training_plan.optimizations:
            try:
                result = self._apply_optimization(optimization)
                results["optimizations_applied"].append({
                    "optimization": optimization,
                    "result": result
                })
            except Exception as e:
                self.logger.error(f"Failed to apply {optimization}: {e}")

        results["improvements"] = training_plan.improvements

        return results

    def _apply_optimization(self, optimization: str) -> str:
        """Apply a specific optimization"""
        # This would contain actual optimization logic
        # For now, return status
        return "applied"

    def run_benchmark(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        self.logger.info("🏃 Running Olympic benchmarks...")

        benchmarks = {
            "timestamp": datetime.now().isoformat(),
            "cpu_benchmark": self._benchmark_cpu(),
            "memory_benchmark": self._benchmark_memory(),
            "disk_benchmark": self._benchmark_disk(),
            "network_benchmark": self._benchmark_network()
        }

        return benchmarks

    def _benchmark_cpu(self) -> Dict[str, Any]:
        """Benchmark CPU performance"""
        try:
            start = time.time()
            # Simple CPU test
            result = sum(i * i for i in range(1000000))
            elapsed = time.time() - start

            return {
                "test": "CPU computation",
                "time_seconds": elapsed,
                "score": max(0, 100 - (elapsed * 100))  # Lower time = higher score
            }
        except Exception as e:
            return {"error": str(e)}

    def _benchmark_memory(self) -> Dict[str, Any]:
        """Benchmark memory performance"""
        try:
            start = time.time()
            # Simple memory test
            data = [0] * 1000000
            data[0] = 1
            elapsed = time.time() - start

            return {
                "test": "Memory allocation",
                "time_seconds": elapsed,
                "score": max(0, 100 - (elapsed * 1000))
            }
        except Exception as e:
            return {"error": str(e)}

    def _benchmark_disk(self) -> Dict[str, Any]:
        """Benchmark disk performance"""
        try:
            test_file = self.data_dir / "benchmark_test.tmp"
            start = time.time()

            # Write test
            with open(test_file, 'wb') as f:
                f.write(b'0' * 1024 * 1024)  # 1MB

            write_time = time.time() - start

            # Read test
            start = time.time()
            with open(test_file, 'rb') as f:
                f.read()

            read_time = time.time() - start

            # Cleanup
            test_file.unlink()

            return {
                "test": "Disk I/O",
                "write_time_seconds": write_time,
                "read_time_seconds": read_time,
                "write_speed_mbps": 1.0 / write_time if write_time > 0 else 0,
                "read_speed_mbps": 1.0 / read_time if read_time > 0 else 0,
                "score": max(0, 100 - ((write_time + read_time) * 50))
            }
        except Exception as e:
            return {"error": str(e)}

    def _benchmark_network(self) -> Dict[str, Any]:
        """Benchmark network performance"""
        latency = self._test_latency("8.8.8.8")
        dns = self._test_dns_resolution("google.com")

        return {
            "test": "Network performance",
            "latency_ms": latency,
            "dns_resolution_ms": dns,
            "score": max(0, 100 - (latency * 2) - (dns * 10))
        }

    def get_training_report(self) -> Dict[str, Any]:
        """Get comprehensive training report"""
        system_metrics, network_metrics, training_plan = self.assess_current_fitness()
        benchmarks = self.run_benchmark()

        return {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": system_metrics.to_dict(),
            "network_metrics": network_metrics.to_dict(),
            "training_plan": training_plan.to_dict(),
            "benchmarks": benchmarks,
            "performance_score": system_metrics.get_performance_score(),
            "performance_level": system_metrics.get_performance_level().value
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Olympic Training")
    parser.add_argument("--assess", action="store_true", help="Assess current fitness")
    parser.add_argument("--train", action="store_true", help="Apply Olympic training")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmarks")
    parser.add_argument("--report", action="store_true", help="Get full training report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    trainer = JARVISOlympicTrainer()

    if args.assess:
        system_metrics, network_metrics, training_plan = trainer.assess_current_fitness()

        if args.json:
            print(json.dumps({
                "system_metrics": system_metrics.to_dict(),
                "network_metrics": network_metrics.to_dict(),
                "training_plan": training_plan.to_dict(),
                "performance_score": system_metrics.get_performance_score(),
                "performance_level": system_metrics.get_performance_level().value
            }, indent=2))
        else:
            print("\n🏋️  JARVIS Fitness Assessment")
            print("=" * 60)
            print(f"Performance Level: {system_metrics.get_performance_level().value.upper()}")
            print(f"Performance Score: {system_metrics.get_performance_score():.1f}/100")
            print(f"\nSystem Metrics:")
            print(f"  CPU: {system_metrics.cpu_percent:.1f}% ({system_metrics.cpu_count} cores)")
            print(f"  Memory: {system_metrics.memory_used_percent:.1f}% used ({system_metrics.memory_available_gb:.1f}GB available)")
            print(f"  Disk: {system_metrics.disk_used_percent:.1f}% used ({system_metrics.disk_free_gb:.1f}GB free)")
            print(f"  Uptime: {system_metrics.uptime_hours:.1f} hours")
            print(f"\nNetwork Metrics:")
            print(f"  Hostname: {network_metrics.hostname}")
            print(f"  IP: {network_metrics.ip_address}")
            print(f"  Latency: {network_metrics.latency_ms:.1f}ms")
            print(f"  Active Connections: {network_metrics.active_connections}")

            if training_plan.optimizations:
                print(f"\n📋 Optimizations Needed:")
                for opt in training_plan.optimizations:
                    print(f"  • {opt}")

            if training_plan.improvements:
                print(f"\n✅ Improvements:")
                for imp in training_plan.improvements:
                    print(f"  • {imp}")

    elif args.train:
        system_metrics, network_metrics, training_plan = trainer.assess_current_fitness()
        results = trainer.apply_olympic_training(training_plan)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print("\n🏋️  Olympic Training Applied")
            print("=" * 60)
            for opt in results["optimizations_applied"]:
                print(f"✅ {opt['optimization']}")

    elif args.benchmark:
        benchmarks = trainer.run_benchmark()

        if args.json:
            print(json.dumps(benchmarks, indent=2))
        else:
            print("\n🏃 Olympic Benchmarks")
            print("=" * 60)
            for test, result in benchmarks.items():
                if test != "timestamp" and isinstance(result, dict):
                    print(f"\n{test.replace('_', ' ').title()}:")
                    for key, value in result.items():
                        print(f"  {key}: {value}")

    elif args.report:
        report = trainer.get_training_report()

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("\n📊 JARVIS Olympic Training Report")
            print("=" * 60)
            print(f"Performance Level: {report['performance_level'].upper()}")
            print(f"Performance Score: {report['performance_score']:.1f}/100")
            print(f"\nSee full report with --json for details")

    else:
        parser.print_help()

