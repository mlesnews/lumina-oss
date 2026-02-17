#!/usr/bin/env python3
"""
JARVIS Live Metrics & Analytics Dashboard

Real-time display of metrics, analytics, and resource utilization
as the autonomous system executes.

Updates continuously like resource utilization monitors.

@LIVE @METRICS @ANALYTICS @DASHBOARD @REALTIME
"""

import sys
import json
import time
import os
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import threading

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import systems
try:
    from jarvis_syphon_autonomous_doit_executor import JARVISSYPHONAutonomousDOITExecutor
    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False

try:
    from jarvis_peak_excellence_evolution import JARVISPeakExcellenceEvolution
    PEAK_EXCELLENCE_AVAILABLE = True
except ImportError:
    PEAK_EXCELLENCE_AVAILABLE = False


class LiveMetricsDashboard:
    """
    Live Metrics & Analytics Dashboard

    Displays real-time metrics, analytics, and resource utilization
    as the system executes.
    """

    def __init__(self, update_interval: float = 1.0):
        """Initialize live dashboard"""
        self.update_interval = update_interval
        self.logger = get_logger("LiveMetricsDashboard")

        # Systems
        self.executor = None
        self.peak_excellence = None

        # Metrics history (for trends)
        self.metrics_history = {
            "execution_speed": deque(maxlen=100),
            "success_rate": deque(maxlen=100),
            "uptime": deque(maxlen=100),
            "efficiency": deque(maxlen=100),
            "active_actions": deque(maxlen=100),
            "queued_actions": deque(maxlen=100),
            "gpu_usage": deque(maxlen=100),
            "gpu_memory": deque(maxlen=100),
            "phone_connected": deque(maxlen=100),
            "phone_battery": deque(maxlen=100)
        }

        # GPU detection
        self.gpu_available = False
        self.gpu_info = {}
        self._detect_gpu()

        # Phone/device detection
        self.phone_available = False
        self.phone_info = {}
        self._detect_phone()

        # Running state
        self.running = False
        self.start_time = datetime.now()

        # Initialize systems
        self._initialize_systems()

        # JARVIS HUD integration
        self.jarvis_hud = None
        self._initialize_jarvis_hud()

    def _detect_gpu(self):
        """Detect GPU availability and info"""
        try:
            # Try nvidia-smi (NVIDIA GPUs)
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total", 
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                self.gpu_available = True
                lines = result.stdout.strip().split('\n')
                if lines:
                    parts = lines[0].split(', ')
                    self.gpu_info = {
                        "name": parts[0] if len(parts) > 0 else "NVIDIA GPU",
                        "usage": float(parts[1]) if len(parts) > 1 else 0.0,
                        "memory_used": float(parts[2]) if len(parts) > 2 else 0.0,
                        "memory_total": float(parts[3]) if len(parts) > 3 else 0.0
                    }
                return
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        # Try Windows WMI for GPU (Windows)
        if platform.system() == "Windows":
            try:
                import wmi
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    self.gpu_available = True
                    self.gpu_info = {
                        "name": gpu.Name or "GPU",
                        "usage": 0.0,  # WMI doesn't provide usage
                        "memory_used": 0.0,
                        "memory_total": (gpu.AdapterRAM or 0) / (1024**3)  # Convert to GB
                    }
                    break
            except ImportError:
                pass
            except Exception:
                pass

        # Fallback: Assume GPU available but no metrics
        if not self.gpu_available:
            self.gpu_info = {
                "name": "GPU (No metrics)",
                "usage": 0.0,
                "memory_used": 0.0,
                "memory_total": 0.0
            }

    def _detect_phone(self):
        """Detect phone/device connection"""
        try:
            # Try ADB for Android devices
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and "device" in result.stdout:
                self.phone_available = True
                # Get battery info
                battery_result = subprocess.run(
                    ["adb", "shell", "dumpsys", "battery"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if battery_result.returncode == 0:
                    battery_output = battery_result.stdout
                    level = 0
                    for line in battery_output.split('\n'):
                        if 'level:' in line:
                            level = int(line.split(':')[1].strip())
                            break
                    self.phone_info = {
                        "connected": True,
                        "battery": level,
                        "type": "Android"
                    }
                else:
                    self.phone_info = {
                        "connected": True,
                        "battery": 0,
                        "type": "Android"
                    }
                return
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        # Try iOS devices (if available)
        # This would require additional tools

        # Fallback
        if not self.phone_available:
            self.phone_info = {
                "connected": False,
                "battery": 0,
                "type": "None"
            }

    def _initialize_jarvis_hud(self):
        """Initialize JARVIS HUD integration"""
        try:
            from jarvis_hud_system import JARVISHUDSystem
            self.jarvis_hud = JARVISHUDSystem(project_root=self.executor.project_root if self.executor else project_root)
            self.logger.info("✅ JARVIS HUD connected")
        except ImportError:
            self.logger.debug("JARVIS HUD not available")
        except Exception as e:
            self.logger.warning(f"⚠️  JARVIS HUD initialization failed: {e}")

    def _initialize_systems(self):
        """Initialize monitoring systems"""
        if EXECUTOR_AVAILABLE:
            try:
                self.executor = JARVISSYPHONAutonomousDOITExecutor()
                self.logger.info("✅ Executor connected")
            except Exception as e:
                self.logger.warning(f"⚠️  Executor connection failed: {e}")

        if PEAK_EXCELLENCE_AVAILABLE:
            try:
                self.peak_excellence = JARVISPeakExcellenceEvolution()
                self.logger.info("✅ Peak Excellence connected")
            except Exception as e:
                self.logger.warning(f"⚠️  Peak Excellence connection failed: {e}")

    def _clear_screen(self):
        """Clear screen (cross-platform)"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _format_bar(self, value: float, max_value: float, width: int = 40) -> str:
        """Format value as progress bar"""
        if max_value == 0:
            return "░" * width

        percentage = min(value / max_value, 1.0)
        filled = int(percentage * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"{bar} {percentage*100:5.1f}%"

    def _format_metric(self, name: str, value: float, unit: str = "", 
                      trend: Optional[float] = None) -> str:
        """Format metric with trend indicator"""
        value_str = f"{value:.3f} {unit}".strip()

        if trend is not None:
            if trend > 0.01:
                trend_str = "📈"
            elif trend < -0.01:
                trend_str = "📉"
            else:
                trend_str = "➡️"
            return f"{name:20s}: {value_str:15s} {trend_str}"
        else:
            return f"{name:20s}: {value_str:15s}"

    def _calculate_trend(self, history: deque) -> Optional[float]:
        """Calculate trend from history"""
        if len(history) < 2:
            return None

        recent = list(history)[-10:] if len(history) >= 10 else list(history)
        if len(recent) < 2:
            return None

        # Simple linear trend
        return (recent[-1] - recent[0]) / len(recent)

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        metrics = {
            "timestamp": datetime.now(),
            "uptime": (datetime.now() - self.start_time).total_seconds() / 3600,
            "execution_speed": 0.0,
            "success_rate": 0.0,
            "efficiency": 0.0,
            "active_actions": 0,
            "queued_actions": 0,
            "total_actions": 0,
            "failed_actions": 0,
            "excellence_score": 0.0,
            "evolution_generation": 0,
            "peak_achievements": 0,
            "obstacles_overcome": 0,
            "adaptations_made": 0,
            "gpu_usage": 0.0,
            "gpu_memory_used": 0.0,
            "gpu_memory_total": 0.0,
            "gpu_name": "N/A",
            "phone_connected": False,
            "phone_battery": 0,
            "phone_type": "None"
        }

        # Get executor status
        if self.executor:
            try:
                status = self.executor.get_status()
                metrics["active_actions"] = status.get("active_actions", 0)
                metrics["queued_actions"] = status.get("queued_actions", 0)
                metrics["total_actions"] = status.get("total_actions", 0)
                metrics["uptime"] = status.get("uptime_hours", 0.0)

                # Get peak excellence metrics
                peak_status = status.get("peak_excellence", {})
                if peak_status:
                    current_metrics = peak_status.get("current_metrics", {})

                    if "execution_speed" in current_metrics:
                        metrics["execution_speed"] = current_metrics["execution_speed"].get("value", 0.0)
                    if "success_rate" in current_metrics:
                        metrics["success_rate"] = current_metrics["success_rate"].get("value", 0.0)
                    if "efficiency" in current_metrics:
                        metrics["efficiency"] = current_metrics["efficiency"].get("value", 0.0)

                    evolution_state = peak_status.get("evolution_state", {})
                    metrics["excellence_score"] = peak_status.get("excellence_score", 0.0)
                    metrics["evolution_generation"] = evolution_state.get("generation", 0)
                    metrics["peak_achievements"] = peak_status.get("peak_achievements", 0)
                    metrics["obstacles_overcome"] = peak_status.get("obstacles_overcome", 0)
                    metrics["adaptations_made"] = peak_status.get("adaptations_made", 0)

                # Calculate success rate from action history
                if metrics["total_actions"] > 0:
                    failed = status.get("system_state", {}).get("failed_actions", 0)
                    metrics["failed_actions"] = failed
                    metrics["success_rate"] = (metrics["total_actions"] - failed) / metrics["total_actions"]

                # Calculate efficiency
                if metrics["uptime"] > 0:
                    metrics["efficiency"] = metrics["total_actions"] / metrics["uptime"]

            except Exception as e:
                self.logger.debug(f"Error getting executor status: {e}")

        # Get GPU metrics
        if self.gpu_available:
            try:
                # Refresh GPU info
                self._detect_gpu()
                metrics["gpu_usage"] = self.gpu_info.get("usage", 0.0)
                metrics["gpu_memory_used"] = self.gpu_info.get("memory_used", 0.0)
                metrics["gpu_memory_total"] = self.gpu_info.get("memory_total", 0.0)
                metrics["gpu_name"] = self.gpu_info.get("name", "GPU")
            except Exception as e:
                self.logger.debug(f"Error getting GPU metrics: {e}")

        # Get phone metrics
        if self.phone_available:
            try:
                # Refresh phone info
                self._detect_phone()
                metrics["phone_connected"] = self.phone_info.get("connected", False)
                metrics["phone_battery"] = self.phone_info.get("battery", 0)
                metrics["phone_type"] = self.phone_info.get("type", "Unknown")
            except Exception as e:
                self.logger.debug(f"Error getting phone metrics: {e}")

        # Update history
        self.metrics_history["execution_speed"].append(metrics["execution_speed"])
        self.metrics_history["success_rate"].append(metrics["success_rate"])
        self.metrics_history["uptime"].append(metrics["uptime"])
        self.metrics_history["efficiency"].append(metrics["efficiency"])
        self.metrics_history["active_actions"].append(metrics["active_actions"])
        self.metrics_history["queued_actions"].append(metrics["queued_actions"])
        self.metrics_history["gpu_usage"].append(metrics["gpu_usage"])
        self.metrics_history["gpu_memory"].append(metrics["gpu_memory_used"] / max(metrics["gpu_memory_total"], 1) * 100 if metrics["gpu_memory_total"] > 0 else 0)
        self.metrics_history["phone_connected"].append(1.0 if metrics["phone_connected"] else 0.0)
        self.metrics_history["phone_battery"].append(metrics["phone_battery"])

        return metrics

    def _display_header(self):
        """Display dashboard header"""
        print("=" * 100)
        print("📊 JARVIS LIVE METRICS & ANALYTICS DASHBOARD".center(100))
        print("=" * 100)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
              f"Update Interval: {self.update_interval}s | "
              f"Press Ctrl+C to exit")
        print("=" * 100)
        print()

    def _display_system_status(self, metrics: Dict[str, Any]):
        """Display system status section"""
        print("🤖 SYSTEM STATUS")
        print("-" * 100)

        status_items = [
            ("Uptime", f"{metrics['uptime']:.2f} hours"),
            ("Active Actions", f"{metrics['active_actions']}"),
            ("Queued Actions", f"{metrics['queued_actions']}"),
            ("Total Actions", f"{metrics['total_actions']}"),
            ("Failed Actions", f"{metrics['failed_actions']}"),
        ]

        for i in range(0, len(status_items), 3):
            row = status_items[i:i+3]
            print(" | ".join(f"{name:20s}: {value:>15s}" for name, value in row))

        print()

    def _display_performance_metrics(self, metrics: Dict[str, Any]):
        """Display performance metrics section"""
        print("⚡ PERFORMANCE METRICS")
        print("-" * 100)

        # Execution Speed
        exec_trend = self._calculate_trend(self.metrics_history["execution_speed"])
        exec_str = self._format_metric("Execution Speed", metrics["execution_speed"], "s", exec_trend)
        print(exec_str)
        print(f"   {self._format_bar(1.0 - metrics['execution_speed'], 1.0)}")

        # Success Rate
        success_trend = self._calculate_trend(self.metrics_history["success_rate"])
        success_str = self._format_metric("Success Rate", metrics["success_rate"], "ratio", success_trend)
        print(success_str)
        print(f"   {self._format_bar(metrics['success_rate'], 1.0)}")

        # Efficiency
        eff_trend = self._calculate_trend(self.metrics_history["efficiency"])
        eff_str = self._format_metric("Efficiency", metrics["efficiency"], "actions/h", eff_trend)
        print(eff_str)
        print(f"   {self._format_bar(metrics['efficiency'], 100.0)}")

        print()

    def _display_peak_excellence(self, metrics: Dict[str, Any]):
        """Display peak excellence section"""
        print("🏆 PEAK EXCELLENCE EVOLUTION")
        print("-" * 100)

        excellence_items = [
            ("Excellence Score", f"{metrics['excellence_score']:.1f}/100"),
            ("Generation", f"{metrics['evolution_generation']}"),
            ("Peak Achievements", f"{metrics['peak_achievements']}"),
            ("Obstacles Overcome", f"{metrics['obstacles_overcome']}"),
            ("Adaptations Made", f"{metrics['adaptations_made']}"),
        ]

        for i in range(0, len(excellence_items), 3):
            row = excellence_items[i:i+3]
            print(" | ".join(f"{name:20s}: {value:>15s}" for name, value in row))

        # Excellence Score Bar
        print(f"\n   Excellence Score: {self._format_bar(metrics['excellence_score'], 100.0)}")

        print()

    def _display_action_queue(self, metrics: Dict[str, Any]):
        """Display action queue section"""
        print("📋 ACTION QUEUE")
        print("-" * 100)

        queue_items = [
            ("Active", metrics["active_actions"]),
            ("Queued", metrics["queued_actions"]),
            ("Total", metrics["total_actions"]),
            ("Failed", metrics["failed_actions"]),
        ]

        for name, value in queue_items:
            max_val = max(metrics["total_actions"], 1)
            print(f"{name:10s}: {value:>5} {self._format_bar(value, max_val, 30)}")

        print()

    def _display_resource_utilization(self, metrics: Dict[str, Any]):
        """Display resource utilization (like system monitors)"""
        print("💻 RESOURCE UTILIZATION")
        print("-" * 100)

        # CPU-like: Active actions / Max concurrent
        cpu_usage = min((metrics["active_actions"] / max(metrics.get("max_concurrent", 5), 1)) * 100, 100)
        print(f"CPU (Actions):     {self._format_bar(cpu_usage, 100.0)} {cpu_usage:.1f}%")

        # Memory-like: Queued actions
        memory_usage = min((metrics["queued_actions"] / max(metrics["total_actions"], 1)) * 100, 100) if metrics["total_actions"] > 0 else 0
        print(f"Memory (Queue):    {self._format_bar(memory_usage, 100.0)} {memory_usage:.1f}%")

        # GPU: GPU utilization
        if metrics["gpu_usage"] > 0 or self.gpu_available:
            gpu_usage = metrics["gpu_usage"]
            gpu_mem_pct = (metrics["gpu_memory_used"] / max(metrics["gpu_memory_total"], 1)) * 100 if metrics["gpu_memory_total"] > 0 else 0
            print(f"GPU ({metrics['gpu_name'][:20]:20s}): {self._format_bar(gpu_usage, 100.0)} {gpu_usage:.1f}%")
            print(f"GPU Memory:        {self._format_bar(gpu_mem_pct, 100.0)} {gpu_mem_pct:.1f}% ({metrics['gpu_memory_used']:.1f}/{metrics['gpu_memory_total']:.1f} GB)")
        else:
            print(f"GPU:               {'Not Available':50s}")

        # Network-like: Efficiency
        network_usage = min((metrics["efficiency"] / 100.0) * 100, 100)
        print(f"Network (Efficiency): {self._format_bar(network_usage, 100.0)} {network_usage:.1f}%")

        # Disk-like: Total actions processed
        disk_usage = min((metrics["total_actions"] / 1000.0) * 100, 100)
        print(f"Disk (Processed):   {self._format_bar(disk_usage, 100.0)} {metrics['total_actions']} actions")

        # Phone/Device
        if metrics["phone_connected"]:
            phone_battery = metrics["phone_battery"]
            phone_type = metrics["phone_type"]
            print(f"Phone ({phone_type:10s}): {self._format_bar(phone_battery, 100.0)} {phone_battery}%")
        else:
            print(f"Phone:              {'Not Connected':50s}")

        print()

    def _display_trends(self, metrics: Dict[str, Any]):
        """Display metric trends"""
        print("📈 METRIC TRENDS (Last 10 Updates)")
        print("-" * 100)

        # Execution Speed Trend
        if len(self.metrics_history["execution_speed"]) > 1:
            recent = list(self.metrics_history["execution_speed"])[-10:]
            trend_str = " ".join("█" if v < 0.5 else "▓" if v < 1.0 else "▒" for v in recent)
            print(f"Execution Speed: {trend_str}")

        # Success Rate Trend
        if len(self.metrics_history["success_rate"]) > 1:
            recent = list(self.metrics_history["success_rate"])[-10:]
            trend_str = " ".join("█" if v > 0.95 else "▓" if v > 0.90 else "▒" for v in recent)
            print(f"Success Rate:    {trend_str}")

        # Efficiency Trend
        if len(self.metrics_history["efficiency"]) > 1:
            recent = list(self.metrics_history["efficiency"])[-10:]
            trend_str = " ".join("█" if v > 50 else "▓" if v > 25 else "▒" for v in recent)
            print(f"Efficiency:      {trend_str}")

        print()

    def display(self):
        """Display full dashboard"""
        self._clear_screen()
        self._display_header()

        # Get current metrics
        metrics = self._get_system_metrics()

        # Display sections
        self._display_system_status(metrics)
        self._display_performance_metrics(metrics)
        self._display_peak_excellence(metrics)
        self._display_action_queue(metrics)
        self._display_resource_utilization(metrics)
        self._display_trends(metrics)

        # Footer
        print("=" * 100)
        print("Live updates every {:.1f}s | Press Ctrl+C to exit".format(self.update_interval))
        print("=" * 100)

    def start(self):
        """Start live dashboard"""
        self.running = True
        self.logger.info("📊 Starting live metrics dashboard...")

        try:
            while self.running:
                self.display()
                time.sleep(self.update_interval)
        except KeyboardInterrupt:
            self.logger.info("\n⏹️  Stopping dashboard...")
            self.running = False
        except Exception as e:
            self.logger.error(f"❌ Dashboard error: {e}")
            self.running = False

    def stop(self):
        """Stop dashboard"""
        self.running = False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Live Metrics Dashboard")
    parser.add_argument("--interval", type=float, default=1.0,
                       help="Update interval in seconds (default: 1.0)")

    args = parser.parse_args()

    dashboard = LiveMetricsDashboard(update_interval=args.interval)
    dashboard.start()


if __name__ == "__main__":


    main()