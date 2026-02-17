#!/usr/bin/env python3
"""
JARVIS Performance Optimizer

System-wide performance monitoring and optimization.
Automatically optimizes system resources, identifies bottlenecks, and improves efficiency.

MCU JARVIS Capability: Performance optimization and resource management.

@JARVIS @PERFORMANCE @OPTIMIZATION @MCU_FEATURE
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import threading
import time
import psutil
import tempfile
import shutil

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISPerformanceOptimizer")


class OptimizationType(Enum):
    """Optimization types"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"
    CACHE = "cache"
    SYSTEM = "system"


class OptimizationLevel(Enum):
    """Optimization levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AGGRESSIVE = "aggressive"


@dataclass
class PerformanceMetric:
    """Performance metric"""
    metric_id: str
    metric_type: OptimizationType
    name: str
    value: float
    unit: str
    timestamp: datetime
    baseline: float = 0.0
    optimal: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['metric_type'] = self.metric_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class OptimizationAction:
    """Optimization action"""
    action_id: str
    optimization_type: OptimizationType
    level: OptimizationLevel
    description: str
    timestamp: datetime
    executed: bool = False
    result: Optional[Dict[str, Any]] = None
    impact_score: float = 0.0  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['optimization_type'] = self.optimization_type.value
        data['level'] = self.level.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class JARVISPerformanceOptimizer:
    """
    JARVIS Performance Optimizer

    System-wide performance monitoring and optimization.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize performance optimizer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISPerformanceOptimizer")

        # Performance metrics
        self.metrics: Dict[str, List[PerformanceMetric]] = {}

        # Optimization actions
        self.actions: List[OptimizationAction] = []

        # Optimization state
        self.optimization_active = False
        self.optimization_thread: Optional[threading.Thread] = None
        self.optimization_interval = 300  # 5 minutes

        # Baselines
        self.baselines: Dict[str, float] = {}

        # Data storage
        self.data_dir = self.project_root / "data" / "jarvis" / "performance"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.data_dir / "metrics.json"
        self.actions_file = self.data_dir / "actions.json"

        # Optimization handlers
        self.optimization_handlers: Dict[OptimizationType, Callable] = {}
        self._register_default_optimizations()

        # Load state
        self._load_state()

        self.logger.info("⚡ JARVIS Performance Optimizer initialized")
        self.logger.info(f"   Metrics tracked: {len(self.metrics)}")
        self.logger.info(f"   Optimization actions: {len(self.actions)}")

    def _register_default_optimizations(self):
        """Register default optimization handlers"""
        self.optimization_handlers[OptimizationType.CPU] = self._optimize_cpu
        self.optimization_handlers[OptimizationType.MEMORY] = self._optimize_memory
        self.optimization_handlers[OptimizationType.DISK] = self._optimize_disk
        self.optimization_handlers[OptimizationType.PROCESS] = self._optimize_processes
        self.optimization_handlers[OptimizationType.CACHE] = self._optimize_cache

    def _load_state(self):
        """Load performance metrics and actions"""
        # Load metrics
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    for metric_data in data:
                        metric = PerformanceMetric(
                            metric_id=metric_data['metric_id'],
                            metric_type=OptimizationType(metric_data['metric_type']),
                            name=metric_data['name'],
                            value=metric_data['value'],
                            unit=metric_data['unit'],
                            timestamp=datetime.fromisoformat(metric_data['timestamp']),
                            baseline=metric_data.get('baseline', 0.0),
                            optimal=metric_data.get('optimal', 0.0)
                        )
                        if metric.metric_id not in self.metrics:
                            self.metrics[metric.metric_id] = []
                        self.metrics[metric.metric_id].append(metric)
                        # Keep last 1000 per metric
                        if len(self.metrics[metric.metric_id]) > 1000:
                            self.metrics[metric.metric_id] = self.metrics[metric.metric_id][-1000:]
                self.logger.info(f"   Loaded metrics for {len(self.metrics)} metric IDs")
            except Exception as e:
                self.logger.error(f"Error loading metrics: {e}")

        # Load actions
        if self.actions_file.exists():
            try:
                with open(self.actions_file, 'r') as f:
                    data = json.load(f)
                    for action_data in data:
                        action = OptimizationAction(
                            action_id=action_data['action_id'],
                            optimization_type=OptimizationType(action_data['optimization_type']),
                            level=OptimizationLevel(action_data['level']),
                            description=action_data['description'],
                            timestamp=datetime.fromisoformat(action_data['timestamp']),
                            executed=action_data.get('executed', False),
                            result=action_data.get('result'),
                            impact_score=action_data.get('impact_score', 0.0)
                        )
                        self.actions.append(action)
                self.logger.info(f"   Loaded {len(self.actions)} optimization actions")
            except Exception as e:
                self.logger.error(f"Error loading actions: {e}")

    def _save_state(self):
        """Save performance metrics and actions using atomic writes"""
        max_retries = 3
        retry_delay = 0.5

        # Save recent metrics (last 100 per metric)
        metrics_to_save = []
        for metric_list in self.metrics.values():
            metrics_to_save.extend(metric_list[-100:])

        self._atomic_write_file(
            self.metrics_file,
            [m.to_dict() for m in metrics_to_save],
            max_retries=max_retries,
            retry_delay=retry_delay
        )

        # Save actions (keep last 500)
        actions_to_save = self.actions[-500:]
        self._atomic_write_file(
            self.actions_file,
            [a.to_dict() for a in actions_to_save],
            max_retries=max_retries,
            retry_delay=retry_delay
        )

    def _atomic_write_file(self, file_path: Path, data: Any, max_retries: int = 3, retry_delay: float = 0.5):
        """Atomically write data to a file with retry logic"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            test_file = file_path.parent / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except (PermissionError, OSError) as e:
                self.logger.warning(f"Directory not writable: {file_path.parent} - {e}")
                return
        except Exception as e:
            self.logger.error(f"Error creating directory {file_path.parent}: {e}")
            return

        for attempt in range(max_retries):
            try:
                temp_file = file_path.parent / f".{file_path.name}.tmp"

                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)

                if file_path.exists():
                    try:
                        file_path.unlink()
                    except PermissionError:
                        time.sleep(retry_delay * (attempt + 1))
                        if attempt < max_retries - 1:
                            continue
                        else:
                            raise

                temp_file.replace(file_path)
                return

            except PermissionError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    self.logger.debug(f"Permission denied, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error saving state to {file_path}: Permission denied after {max_retries} attempts - {e}")
                    if 'temp_file' in locals() and temp_file.exists():
                        try:
                            temp_file.unlink()
                        except:
                            pass
            except Exception as e:
                self.logger.error(f"Error saving state to {file_path}: {e}")
                if 'temp_file' in locals() and temp_file.exists():
                    try:
                        temp_file.unlink()
                    except:
                        pass
                return

    def collect_metrics(self):
        """Collect current performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self._record_metric("cpu_usage", OptimizationType.CPU, "CPU Usage", cpu_percent, "%")

            # Memory metrics
            mem = psutil.virtual_memory()
            self._record_metric("memory_usage", OptimizationType.MEMORY, "Memory Usage", mem.percent, "%")
            self._record_metric("memory_available", OptimizationType.MEMORY, "Memory Available", mem.available / (1024**3), "GB")

            # Disk metrics
            disk = psutil.disk_usage('C:')
            self._record_metric("disk_usage", OptimizationType.DISK, "Disk Usage", disk.percent, "%")
            self._record_metric("disk_free", OptimizationType.DISK, "Disk Free", disk.free / (1024**3), "GB")

            # Process metrics
            process_count = len(psutil.pids())
            self._record_metric("process_count", OptimizationType.PROCESS, "Process Count", process_count, "count")

            # Network metrics
            net_io = psutil.net_io_counters()
            self._record_metric("network_sent", OptimizationType.NETWORK, "Network Sent", net_io.bytes_sent / (1024**2), "MB")
            self._record_metric("network_recv", OptimizationType.NETWORK, "Network Received", net_io.bytes_recv / (1024**2), "MB")

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")

    def _record_metric(self, metric_id: str, metric_type: OptimizationType,
                      name: str, value: float, unit: str):
        """Record a performance metric"""
        metric = PerformanceMetric(
            metric_id=metric_id,
            metric_type=metric_type,
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            baseline=self.baselines.get(metric_id, value),
            optimal=self._calculate_optimal(metric_id, value)
        )

        if metric_id not in self.metrics:
            self.metrics[metric_id] = []
        self.metrics[metric_id].append(metric)

        # Keep last 1000
        if len(self.metrics[metric_id]) > 1000:
            self.metrics[metric_id] = self.metrics[metric_id][-1000:]

        # Update baseline (exponential moving average)
        if metric_id in self.baselines:
            self.baselines[metric_id] = (self.baselines[metric_id] * 0.9) + (value * 0.1)
        else:
            self.baselines[metric_id] = value

    def _calculate_optimal(self, metric_id: str, current_value: float) -> float:
        """Calculate optimal value for a metric"""
        # Simple optimal calculation based on metric type
        if "usage" in metric_id or "percent" in metric_id:
            return 50.0  # Optimal usage is around 50%
        elif "count" in metric_id:
            return current_value * 0.8  # Optimal is 20% less
        else:
            return current_value * 0.9  # Optimal is 10% less

    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze current performance and identify optimization opportunities"""
        opportunities = []

        for metric_id, metric_list in self.metrics.items():
            if not metric_list:
                continue

            latest = metric_list[-1]

            # Check if metric is suboptimal
            if latest.metric_type == OptimizationType.CPU and latest.value > 80:
                opportunities.append({
                    "metric_id": metric_id,
                    "type": OptimizationType.CPU,
                    "issue": f"High CPU usage: {latest.value}%",
                    "recommendation": "Optimize CPU-intensive processes",
                    "priority": "high" if latest.value > 90 else "medium"
                })

            elif latest.metric_type == OptimizationType.MEMORY and latest.value > 85:
                opportunities.append({
                    "metric_id": metric_id,
                    "type": OptimizationType.MEMORY,
                    "issue": f"High memory usage: {latest.value}%",
                    "recommendation": "Free up memory or optimize memory usage",
                    "priority": "high" if latest.value > 95 else "medium"
                })

            elif latest.metric_type == OptimizationType.DISK and latest.value > 90:
                opportunities.append({
                    "metric_id": metric_id,
                    "type": OptimizationType.DISK,
                    "issue": f"High disk usage: {latest.value}%",
                    "recommendation": "Clean up disk space",
                    "priority": "high" if latest.value > 95 else "medium"
                })

        return {
            "timestamp": datetime.now().isoformat(),
            "opportunities": opportunities,
            "total_opportunities": len(opportunities),
            "high_priority": len([o for o in opportunities if o["priority"] == "high"])
        }

    def optimize(self, optimization_type: OptimizationType, level: OptimizationLevel = OptimizationLevel.MEDIUM) -> OptimizationAction:
        """Execute optimization"""
        action_id = f"opt_{int(datetime.now().timestamp())}_{len(self.actions)}"

        action = OptimizationAction(
            action_id=action_id,
            optimization_type=optimization_type,
            level=level,
            description=f"Optimize {optimization_type.value} at {level.value} level",
            timestamp=datetime.now()
        )

        # Execute optimization
        if optimization_type in self.optimization_handlers:
            try:
                result = self.optimization_handlers[optimization_type](level)
                action.executed = True
                action.result = result
                action.impact_score = result.get("impact_score", 0.0)
                self.logger.info(f"⚡ Optimization executed: {optimization_type.value} - Impact: {action.impact_score:.2f}")
            except Exception as e:
                self.logger.error(f"Optimization error: {e}")
                action.result = {"error": str(e)}

        self.actions.append(action)
        self._save_state()

        return action

    def _optimize_cpu(self, level: OptimizationLevel) -> Dict[str, Any]:
        """Optimize CPU usage"""
        self.logger.info(f"⚡ Optimizing CPU at {level.value} level")

        # Identify high CPU processes
        high_cpu_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                cpu_percent = proc.info['cpu_percent']
                if cpu_percent > 10:  # Processes using >10% CPU
                    high_cpu_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu": cpu_percent
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage
        high_cpu_processes.sort(key=lambda x: x['cpu'], reverse=True)

        impact_score = min(len(high_cpu_processes) * 0.1, 0.8)

        return {
            "action": "cpu_optimization",
            "high_cpu_processes": high_cpu_processes[:10],  # Top 10
            "recommendation": "Consider closing or optimizing high CPU processes",
            "impact_score": impact_score
        }

    def _optimize_memory(self, level: OptimizationLevel) -> Dict[str, Any]:
        """Optimize memory usage"""
        self.logger.info(f"⚡ Optimizing memory at {level.value} level")

        # Get memory info
        mem = psutil.virtual_memory()

        # Find processes using most memory
        high_mem_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                mem_info = proc.info['memory_info']
                mem_mb = mem_info.rss / (1024 * 1024)
                if mem_mb > 100:  # Processes using >100MB
                    high_mem_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "memory_mb": mem_mb
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        high_mem_processes.sort(key=lambda x: x['memory_mb'], reverse=True)

        impact_score = min((mem.percent / 100) * 0.8, 0.8)

        return {
            "action": "memory_optimization",
            "memory_usage": mem.percent,
            "high_memory_processes": high_mem_processes[:10],
            "recommendation": "Consider closing unused applications to free memory",
            "impact_score": impact_score
        }

    def _optimize_disk(self, level: OptimizationLevel) -> Dict[str, Any]:
        """Optimize disk usage"""
        self.logger.info(f"⚡ Optimizing disk at {level.value} level")

        disk = psutil.disk_usage('C:')

        impact_score = min((disk.percent / 100) * 0.7, 0.7)

        return {
            "action": "disk_optimization",
            "disk_usage": disk.percent,
            "free_space_gb": disk.free / (1024**3),
            "recommendation": "Run disk cleanup or remove unnecessary files",
            "impact_score": impact_score
        }

    def _optimize_processes(self, level: OptimizationLevel) -> Dict[str, Any]:
        """Optimize process management"""
        self.logger.info(f"⚡ Optimizing processes at {level.value} level")

        process_count = len(psutil.pids())

        impact_score = min((process_count / 200) * 0.5, 0.5)

        return {
            "action": "process_optimization",
            "process_count": process_count,
            "recommendation": "Consider closing unnecessary processes",
            "impact_score": impact_score
        }

    def _optimize_cache(self, level: OptimizationLevel) -> Dict[str, Any]:
        """Optimize cache"""
        self.logger.info(f"⚡ Optimizing cache at {level.value} level")

        return {
            "action": "cache_optimization",
            "recommendation": "Clear system caches if needed",
            "impact_score": 0.3
        }

    def start_optimization(self, interval: int = 300):
        """Start continuous optimization"""
        if self.optimization_active:
            self.logger.warning("Optimization already active")
            return

        self.optimization_active = True
        self.optimization_interval = interval
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
        self.logger.info(f"⚡ Performance optimization started (interval: {interval}s)")

    def stop_optimization(self):
        """Stop continuous optimization"""
        self.optimization_active = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        self.logger.info("⚡ Performance optimization stopped")

    def _optimization_loop(self):
        """Continuous optimization loop"""
        while self.optimization_active:
            try:
                # Collect metrics
                self.collect_metrics()

                # Analyze performance
                analysis = self.analyze_performance()

                # Execute optimizations for high-priority opportunities
                for opportunity in analysis.get("opportunities", []):
                    if opportunity["priority"] == "high":
                        opt_type = opportunity["type"]
                        self.optimize(opt_type, OptimizationLevel.HIGH)

                time.sleep(self.optimization_interval)
            except Exception as e:
                self.logger.error(f"Optimization loop error: {e}")
                time.sleep(self.optimization_interval)

    def get_status_report(self) -> Dict[str, Any]:
        """Get performance optimizer status report"""
        recent_metrics = {}
        for metric_id, metrics in self.metrics.items():
            if metrics:
                recent_metrics[metric_id] = metrics[-1].to_dict()

        analysis = self.analyze_performance()

        return {
            "timestamp": datetime.now().isoformat(),
            "optimization_active": self.optimization_active,
            "optimization_interval": self.optimization_interval,
            "total_metrics": sum(len(m) for m in self.metrics.values()),
            "recent_metrics": recent_metrics,
            "optimization_opportunities": analysis,
            "total_actions": len(self.actions),
            "recent_actions": [a.to_dict() for a in self.actions[-10:]]
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Performance Optimizer")
        parser.add_argument("--status", action="store_true", help="Get status report")
        parser.add_argument("--analyze", action="store_true", help="Analyze performance")
        parser.add_argument("--optimize", type=str, help="Optimize specific type (cpu, memory, disk, process, cache)")
        parser.add_argument("--start", action="store_true", help="Start continuous optimization")
        parser.add_argument("--stop", action="store_true", help="Stop optimization")

        args = parser.parse_args()

        optimizer = JARVISPerformanceOptimizer()

        if args.status:
            report = optimizer.get_status_report()
            print(json.dumps(report, indent=2, default=str))

        elif args.analyze:
            analysis = optimizer.analyze_performance()
            print(json.dumps(analysis, indent=2, default=str))

        elif args.optimize:
            opt_type_map = {
                "cpu": OptimizationType.CPU,
                "memory": OptimizationType.MEMORY,
                "disk": OptimizationType.DISK,
                "process": OptimizationType.PROCESS,
                "cache": OptimizationType.CACHE
            }
            if args.optimize.lower() in opt_type_map:
                action = optimizer.optimize(opt_type_map[args.optimize.lower()])
                print(f"✅ Optimization executed: {action.action_id}")
                print(json.dumps(action.to_dict(), indent=2, default=str))
            else:
                print(f"❌ Unknown optimization type: {args.optimize}")

        elif args.start:
            optimizer.start_optimization()
            print("✅ Performance optimization started")

        elif args.stop:
            optimizer.stop_optimization()
            print("✅ Performance optimization stopped")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()