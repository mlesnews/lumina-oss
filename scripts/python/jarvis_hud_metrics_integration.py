#!/usr/bin/env python3
"""
JARVIS HUD Metrics Integration

Integrates live metrics with JARVIS HUD Iron Man virtual assistant desktop.
When dashboards aren't open, runs through JARVIS HUD system.

Also accessible via ROAMwise AI frontend.

@JARVIS @HUD @IRON_MAN @METRICS @ROAMWISE @VIRTUAL_ASSISTANT
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

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
    from jarvis_hud_system import JARVISHUDSystem, HUDDisplayType, AlertPriority
    HUD_AVAILABLE = True
except ImportError:
    HUD_AVAILABLE = False
    JARVISHUDSystem = None

try:
    from jarvis_live_metrics_dashboard import LiveMetricsDashboard
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False

try:
    from jarvis_syphon_autonomous_doit_executor import JARVISSYPHONAutonomousDOITExecutor
    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False


class JARVISHUDMetricsIntegration:
    """
    JARVIS HUD Metrics Integration

    Integrates metrics with JARVIS HUD Iron Man virtual assistant desktop.
    When dashboards aren't open, displays metrics through JARVIS HUD.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize HUD metrics integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISHUDMetrics")

        # Systems
        self.jarvis_hud = None
        self.metrics_dashboard = None
        self.executor = None

        # Dashboard open state
        self.dashboard_open = False
        self.hud_active = False

        # Initialize systems
        self._initialize_systems()

        # Metrics update thread
        self.update_thread = None
        self.running = False

    def _initialize_systems(self):
        """Initialize JARVIS HUD and metrics systems"""
        # Initialize JARVIS HUD
        if HUD_AVAILABLE:
            try:
                self.jarvis_hud = JARVISHUDSystem(project_root=self.project_root)
                self.logger.info("✅ JARVIS HUD initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  JARVIS HUD initialization failed: {e}")

        # Initialize metrics dashboard
        if DASHBOARD_AVAILABLE:
            try:
                self.metrics_dashboard = LiveMetricsDashboard()
                self.logger.info("✅ Metrics dashboard initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Metrics dashboard initialization failed: {e}")

        # Initialize executor
        if EXECUTOR_AVAILABLE:
            try:
                self.executor = JARVISSYPHONAutonomousDOITExecutor()
                self.logger.info("✅ Executor initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Executor initialization failed: {e}")

    def _update_hud_metrics(self):
        """Update JARVIS HUD with current metrics"""
        if not self.jarvis_hud or not self.executor:
            return

        try:
            # Get metrics
            status = self.executor.get_status()
            metrics = self.metrics_dashboard._get_system_metrics() if self.metrics_dashboard else {}

            # Create HUD displays for metrics
            displays = []

            # System Status Display
            displays.append({
                "display_id": "system_status",
                "display_type": HUDDisplayType.METRICS.value,
                "position": {"x": 10, "y": 10},
                "size": {"width": 300, "height": 150},
                "content": {
                    "title": "System Status",
                    "metrics": {
                        "Uptime": f"{status.get('uptime_hours', 0):.2f}h",
                        "Active": status.get('active_actions', 0),
                        "Queued": status.get('queued_actions', 0),
                        "Total": status.get('total_actions', 0)
                    }
                },
                "style": {
                    "background_color": "rgba(0, 0, 0, 0.8)",
                    "border_color": "#00ff00",
                    "text_color": "#00ff00"
                }
            })

            # Performance Metrics Display
            peak_status = status.get("peak_excellence", {})
            current_metrics = peak_status.get("current_metrics", {})

            perf_metrics = {}
            if "execution_speed" in current_metrics:
                perf_metrics["Speed"] = f"{current_metrics['execution_speed']['value']:.3f}s"
            if "success_rate" in current_metrics:
                perf_metrics["Success"] = f"{current_metrics['success_rate']['value']*100:.1f}%"
            if "efficiency" in current_metrics:
                perf_metrics["Efficiency"] = f"{current_metrics['efficiency']['value']:.1f}/h"

            displays.append({
                "display_id": "performance_metrics",
                "display_type": HUDDisplayType.METRICS.value,
                "position": {"x": 320, "y": 10},
                "size": {"width": 300, "height": 150},
                "content": {
                    "title": "Performance",
                    "metrics": perf_metrics
                },
                "style": {
                    "background_color": "rgba(0, 0, 0, 0.8)",
                    "border_color": "#00ffff",
                    "text_color": "#00ffff"
                }
            })

            # GPU Display (if available)
            if metrics.get("gpu_usage", 0) > 0:
                displays.append({
                    "display_id": "gpu_metrics",
                    "display_type": HUDDisplayType.METRICS.value,
                    "position": {"x": 10, "y": 170},
                    "size": {"width": 300, "height": 100},
                    "content": {
                        "title": f"GPU: {metrics.get('gpu_name', 'GPU')[:20]}",
                        "metrics": {
                            "Usage": f"{metrics.get('gpu_usage', 0):.1f}%",
                            "Memory": f"{metrics.get('gpu_memory_used', 0):.1f}/{metrics.get('gpu_memory_total', 0):.1f} GB"
                        }
                    },
                    "style": {
                        "background_color": "rgba(0, 0, 0, 0.8)",
                        "border_color": "#ff8800",
                        "text_color": "#ff8800"
                    }
                })

            # Phone Display (if connected)
            if metrics.get("phone_connected", False):
                displays.append({
                    "display_id": "phone_metrics",
                    "display_type": HUDDisplayType.METRICS.value,
                    "position": {"x": 320, "y": 170},
                    "size": {"width": 300, "height": 100},
                    "content": {
                        "title": f"Phone: {metrics.get('phone_type', 'Device')}",
                        "metrics": {
                            "Battery": f"{metrics.get('phone_battery', 0)}%",
                            "Status": "Connected"
                        }
                    },
                    "style": {
                        "background_color": "rgba(0, 0, 0, 0.8)",
                        "border_color": "#00ff88",
                        "text_color": "#00ff88"
                    }
                })

            # Update HUD displays
            for display_data in displays:
                self.jarvis_hud.update_display(display_data)

        except Exception as e:
            self.logger.debug(f"Error updating HUD metrics: {e}")

    def _metrics_update_loop(self):
        """Metrics update loop for HUD"""
        while self.running:
            try:
                # If dashboard not open, update HUD
                if not self.dashboard_open and self.hud_active:
                    self._update_hud_metrics()

                time.sleep(2.0)  # Update every 2 seconds
            except Exception as e:
                self.logger.error(f"Error in metrics update loop: {e}")
                time.sleep(5.0)

    def start_hud_metrics(self):
        """Start HUD metrics display"""
        if not self.jarvis_hud:
            self.logger.warning("⚠️  JARVIS HUD not available")
            return False

        self.hud_active = True
        self.running = True

        # Start update thread
        self.update_thread = threading.Thread(target=self._metrics_update_loop, daemon=True)
        self.update_thread.start()

        self.logger.info("✅ JARVIS HUD metrics started")
        self.logger.info("   Metrics will display in JARVIS HUD when dashboard not open")

        return True

    def stop_hud_metrics(self):
        """Stop HUD metrics display"""
        self.hud_active = False
        self.running = False
        self.logger.info("⏹️  JARVIS HUD metrics stopped")

    def set_dashboard_open(self, is_open: bool):
        """Set dashboard open state"""
        self.dashboard_open = is_open
        if is_open:
            self.logger.info("📊 Dashboard open - HUD metrics paused")
        else:
            self.logger.info("🖥️  Dashboard closed - HUD metrics active")
            if self.hud_active:
                self._update_hud_metrics()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS HUD Metrics Integration")
    parser.add_argument("--start", action="store_true", help="Start HUD metrics")
    parser.add_argument("--stop", action="store_true", help="Stop HUD metrics")

    args = parser.parse_args()

    integration = JARVISHUDMetricsIntegration()

    if args.start:
        integration.start_hud_metrics()
        # Keep running
        try:
            while integration.running:
                time.sleep(1)
        except KeyboardInterrupt:
            integration.stop_hud_metrics()

    if args.stop:
        integration.stop_hud_metrics()


if __name__ == "__main__":


    main()