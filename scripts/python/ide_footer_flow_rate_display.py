#!/usr/bin/env python3
"""
IDE Footer Flow Rate Display with Scrolling Ticker

Displays @PEAK workflow flow rate in IDE footer with scrolling ticker (airport style).
Integrates with Cursor IDE status bar/footer.

Tags: #IDE #FOOTER #TICKER #FLOWRATE #PEAK @SMART @JARVIS
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IDEFooterFlowRate")

# Flow rate calculator
try:
    from workflow_flow_rate_calculator import WorkflowFlowRateCalculator, FlowRateStatistics
    FLOW_RATE_CALCULATOR_AVAILABLE = True
except ImportError:
    FLOW_RATE_CALCULATOR_AVAILABLE = False
    WorkflowFlowRateCalculator = None
    FlowRateStatistics = None

# Progress tracker
try:
    from lumina_progress_tracker import LUMINAProgressTracker
    PROGRESS_TRACKER_AVAILABLE = True
except ImportError:
    PROGRESS_TRACKER_AVAILABLE = False
    LUMINAProgressTracker = None

# GitLens alert handler
try:
    from gitlens_ide_footer_alert_handler import GitLensIDEFooterAlertHandler
    GITLENS_HANDLER_AVAILABLE = True
except ImportError:
    GITLENS_HANDLER_AVAILABLE = False
    GitLensIDEFooterAlertHandler = None

# Workflow telemetry
try:
    from syphon_workflow_telemetry_system import get_telemetry_system
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    get_telemetry_system = None


class IDEFooterFlowRateDisplay:
    """
    IDE Footer Flow Rate Display with Scrolling Ticker

    Displays workflow flow rate metrics in IDE footer/status bar.
    Automatically scrolls if content is longer than display width.
    """

    def __init__(self, project_root: Optional[Path] = None, update_interval: float = 1.0):
        """
        Initialize IDE footer display

        Args:
            project_root: Project root directory
            update_interval: Update interval in seconds (default: 1.0)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.update_interval = update_interval
        self.display_width = 80  # Standard terminal/IDE footer width

        # Flow rate calculator
        self.calculator = None
        if FLOW_RATE_CALCULATOR_AVAILABLE:
            try:
                self.calculator = WorkflowFlowRateCalculator(project_root=self.project_root)
                logger.info("✅ Flow rate calculator initialized")
            except Exception as e:
                logger.warning(f"⚠️  Flow rate calculator not available: {e}")

        # Progress tracker
        self.progress_tracker = None
        if PROGRESS_TRACKER_AVAILABLE:
            try:
                self.progress_tracker = LUMINAProgressTracker(project_root=self.project_root)
                logger.info("✅ Progress tracker initialized")
            except Exception as e:
                logger.warning(f"⚠️  Progress tracker not available: {e}")

        # GitLens handler
        self.gitlens_handler = None
        if GITLENS_HANDLER_AVAILABLE:
            try:
                self.gitlens_handler = GitLensIDEFooterAlertHandler(project_root=self.project_root)
                logger.info("✅ GitLens handler initialized")
            except Exception as e:
                logger.warning(f"⚠️  GitLens handler not available: {e}")

        # Telemetry system
        self.telemetry = None
        if TELEMETRY_AVAILABLE:
            try:
                self.telemetry = get_telemetry_system()
                logger.info("✅ Workflow telemetry system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Telemetry system not available: {e}")

        # Display state
        self.running = False
        self.update_thread = None
        self.current_display_text = ""
        self.scroll_position = 0

        # Configuration
        self.config_file = self.project_root / "config" / "ide_footer_display.json"
        self.load_config()

        logger.info("✅ IDE Footer Flow Rate Display initialized")

    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "enabled": True,
            "update_interval": 1.0,
            "display_width": 80,
            "scroll_speed": 1,
            "format": "ticker",  # "standard" or "ticker"
            "show_icons": True,
            "metrics": {
                "current_flow_rate": True,
                "average_flow_rate": True,
                "peak_flow_rate": True,
                "active_workflows": True,
                "efficiency": True,
                "tasks_per_second": True,
                "overall_progress": True,
                "gitlens_followups": True
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save config: {e}")

    def start(self):
        """Start the footer display"""
        if self.running:
            logger.warning("Display already running")
            return

        if not self.config.get("enabled", True):
            logger.info("Display disabled in config")
            return

        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info("🚀 IDE Footer Flow Rate Display started")

    def stop(self):
        """Stop the footer display"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
        logger.info("🛑 IDE Footer Flow Rate Display stopped")

    def _update_loop(self):
        """Main update loop"""
        while self.running:
            try:
                # Update flow rate from telemetry
                self._update_from_telemetry()

                # Calculate current flow rate
                if self.calculator:
                    stats = self.calculator.calculate_flow_rate()

                    # Generate display text
                    if self.config.get("format") == "ticker":
                        self.current_display_text = self._generate_ticker_text(stats)
                    else:
                        self.current_display_text = self._generate_standard_text(stats)

                    # Update scroll position for ticker
                    if self.config.get("format") == "ticker":
                        self._update_scroll_position()

                time.sleep(self.config.get("update_interval", 1.0))

            except Exception as e:
                logger.error(f"Error in update loop: {e}", exc_info=True)
                time.sleep(5.0)

    def _update_from_telemetry(self):
        """Update calculator from telemetry system"""
        if not self.telemetry or not self.calculator:
            return

        try:
            # Get recent workflow executions
            # This would need to be implemented based on telemetry API
            # For now, we'll simulate with existing workflows
            pass
        except Exception as e:
            logger.debug(f"Could not update from telemetry: {e}")

    def _generate_standard_text(self, stats: FlowRateStatistics) -> str:
        """Generate standard format display text"""
        metrics = self.config.get("metrics", {})
        show_icons = self.config.get("show_icons", True)

        parts = []

        if metrics.get("current_flow_rate", True):
            icon = "⚡" if show_icons else ""
            parts.append(f"{icon}FLOW: {stats.current_flow_rate:.2f}/s")

        if metrics.get("average_flow_rate", True):
            icon = "📊" if show_icons else ""
            parts.append(f"{icon}AVG: {stats.average_flow_rate:.2f}/s")

        if metrics.get("peak_flow_rate", True):
            icon = "🏆" if show_icons else ""
            parts.append(f"{icon}PEAK: {stats.peak_flow_rate:.2f}/s")

        if metrics.get("active_workflows", True):
            icon = "🔄" if show_icons else ""
            parts.append(f"{icon}ACTIVE: {stats.active_workflows}/{stats.total_workflows}")

        if metrics.get("efficiency", True):
            icon = "⚙️" if show_icons else ""
            parts.append(f"{icon}EFF: {stats.efficiency * 100:.0f}%")

        if metrics.get("tasks_per_second", True):
            icon = "📈" if show_icons else ""
            parts.append(f"{icon}TASKS: {stats.tasks_per_second:.2f}/s")

        text = " | ".join(parts)

        # Truncate if too long
        max_width = self.config.get("display_width", 80)
        if len(text) > max_width:
            text = text[:max_width-3] + "..."

        return text

    def _generate_ticker_text(self, stats: FlowRateStatistics) -> str:
        """Generate scrolling ticker text"""
        metrics = self.config.get("metrics", {})
        show_icons = self.config.get("show_icons", True)

        parts = []

        # Add Overall Progress
        if metrics.get("overall_progress", True) and self.progress_tracker:
            try:
                progress_summary = self.progress_tracker.get_progress_summary()
                percentage = progress_summary.get("overall_percentage", 0.0)
                icon = "🏗️ " if show_icons else ""
                parts.append(f"{icon}LUMINA: {percentage:.1f}%")
            except Exception as e:
                logger.debug(f"Could not get progress: {e}")

        # Add GitLens Follow-ups
        if metrics.get("gitlens_followups", True) and self.gitlens_handler:
            try:
                followup_count = len(self.gitlens_handler.active_alerts)
                if followup_count > 0:
                    icon = "🚩 " if show_icons else ""
                    parts.append(f"{icon}GITLENS: {followup_count} FOLLOW-UPS")
            except Exception as e:
                logger.debug(f"Could not get GitLens alerts: {e}")

        if metrics.get("current_flow_rate", True):
            icon = "⚡" if show_icons else ""
            parts.append(f"{icon} FLOW: {stats.current_flow_rate:.2f}/s")

        if metrics.get("average_flow_rate", True):
            icon = "📊" if show_icons else ""
            parts.append(f"{icon} AVG: {stats.average_flow_rate:.2f}/s")

        if metrics.get("peak_flow_rate", True):
            icon = "🏆" if show_icons else ""
            parts.append(f"{icon} PEAK: {stats.peak_flow_rate:.2f}/s")

        if metrics.get("active_workflows", True):
            icon = "🔄" if show_icons else ""
            parts.append(f"{icon} ACTIVE: {stats.active_workflows}/{stats.total_workflows}")

        if metrics.get("efficiency", True):
            icon = "⚙️" if show_icons else ""
            parts.append(f"{icon} EFF: {stats.efficiency * 100:.0f}%")

        if metrics.get("tasks_per_second", True):
            icon = "📈" if show_icons else ""
            parts.append(f"{icon} TASKS: {stats.tasks_per_second:.2f}/s")

        # Join with separator
        full_text = " | ".join(parts)

        # Add padding for smooth scrolling
        padding = " " * 10
        full_text = padding + full_text + padding

        return full_text

    def _update_scroll_position(self):
        """Update scroll position for ticker"""
        scroll_speed = self.config.get("scroll_speed", 1)
        self.scroll_position = (self.scroll_position + scroll_speed) % max(len(self.current_display_text), 1)

    def get_display_text(self) -> str:
        """
        Get current display text (for IDE integration)

        Returns text ready to display in IDE footer/status bar
        """
        if not self.config.get("enabled", True):
            return ""

        if not self.current_display_text:
            return "FLOW RATE: Initializing..."

        # For ticker format, extract visible portion
        if self.config.get("format") == "ticker":
            max_width = self.config.get("display_width", 80)
            start_pos = self.scroll_position % len(self.current_display_text)
            visible = self.current_display_text[start_pos:start_pos + max_width]

            # Pad if needed
            if len(visible) < max_width:
                visible = visible.ljust(max_width)

            return visible
        else:
            # Standard format - just return as-is (already truncated)
            return self.current_display_text

    def get_stats(self) -> Optional[Dict[str, Any]]:
        """Get current flow rate statistics"""
        if not self.calculator:
            return None

        try:
            stats = self.calculator.calculate_flow_rate()
            return stats.to_dict()
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return None


if __name__ == "__main__":
    print("\n" + "="*80)
    print("IDE Footer Flow Rate Display - Scrolling Ticker")
    print("="*80 + "\n")

    display = IDEFooterFlowRateDisplay(update_interval=0.5)

    # Start display
    print("🚀 Starting IDE Footer Display...")
    display.start()

    # Simulate some workflows
    if display.calculator:
        for i in range(3):
            workflow_id = f"test_workflow_{i+1}"
            display.calculator.register_workflow(workflow_id, tasks_total=10)
            display.calculator.update_workflow(workflow_id, tasks_completed=5 + i)
            time.sleep(0.2)

    # Show display updates
    print("\n📺 IDE Footer Display (Scrolling Ticker):\n")
    for i in range(10):
        text = display.get_display_text()
        print(f"   {text}")
        time.sleep(0.3)

    # Stop display
    display.stop()

    # Show stats
    stats = display.get_stats()
    if stats:
        print(f"\n📊 Final Statistics:")
        print(f"   Current Flow Rate: {stats.get('current_flow_rate', 0):.2f} workflows/s")
        print(f"   Peak Flow Rate: {stats.get('peak_flow_rate', 0):.2f} workflows/s")
        print(f"   Active Workflows: {stats.get('active_workflows', 0)}")
        print(f"   Efficiency: {stats.get('efficiency', 0) * 100:.1f}%")

    print("\n✅ IDE Footer Display Test Complete")
    print("="*80 + "\n")
