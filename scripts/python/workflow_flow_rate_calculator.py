#!/usr/bin/env python3
"""
@PEAK Workflow Flow Rate Calculator & IDE Footer Display

Algorithm to calculate and maximize workflow flow rate:
- Flow rate per second (average for all workflows in progress)
- Total max flow rate over time
- Algebraic formula: F = (W_completed / T_elapsed) * (W_active / W_total)
- Display in IDE footer with scrolling ticker (airport style)

Tags: #WORKFLOW #FLOWRATE #PEAK #IDE #FOOTER #TICKER @SMART @JARVIS
"""

import sys
import json
import time
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import deque
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WorkflowFlowRate")


@dataclass
class WorkflowMetrics:
    """Metrics for a single workflow"""
    workflow_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    tasks_completed: int = 0
    tasks_total: int = 0
    status: str = "active"  # active, completed, failed, paused

    @property
    def duration(self) -> float:
        """Duration in seconds"""
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()

    @property
    def completion_rate(self) -> float:
        """Completion rate (0.0 to 1.0)"""
        if self.tasks_total == 0:
            return 0.0
        return self.tasks_completed / self.tasks_total

    @property
    def flow_rate(self) -> float:
        """Flow rate (tasks per second)"""
        duration = self.duration
        if duration == 0:
            return 0.0
        return self.tasks_completed / duration


@dataclass
class FlowRateStatistics:
    """Flow rate statistics"""
    timestamp: datetime
    current_flow_rate: float  # Current flow rate (workflows/sec)
    average_flow_rate: float  # Average flow rate over time window
    peak_flow_rate: float  # Maximum flow rate achieved
    active_workflows: int
    completed_workflows: int
    total_workflows: int
    tasks_per_second: float  # Tasks completed per second
    efficiency: float  # Efficiency metric (0.0 to 1.0)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class WorkflowFlowRateCalculator:
    """
    @PEAK Workflow Flow Rate Calculator

    Algebraic Formula:
    F(t) = (Σ(W_i.completed / T_i)) / N_active * (N_active / N_total)

    Where:
    - F(t) = Flow rate at time t
    - W_i.completed = Tasks completed in workflow i
    - T_i = Duration of workflow i
    - N_active = Number of active workflows
    - N_total = Total number of workflows

    Simplified:
    F = (W_completed / T_elapsed) * (W_active / W_total) * efficiency_factor
    """

    def __init__(self, project_root: Optional[Path] = None, time_window: int = 60):
        """
        Initialize flow rate calculator

        Args:
            project_root: Project root directory
            time_window: Time window in seconds for averaging (default: 60)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.time_window = time_window

        # Workflow tracking
        self.workflows: Dict[str, WorkflowMetrics] = {}
        self.flow_rate_history: deque = deque(maxlen=1000)  # Keep last 1000 samples

        # Statistics
        self.peak_flow_rate: float = 0.0
        self.total_tasks_completed: int = 0
        self.start_time: datetime = datetime.now()

        logger.info(f"✅ Workflow Flow Rate Calculator initialized (time_window={time_window}s)")

    def register_workflow(self, workflow_id: str, tasks_total: int = 0) -> WorkflowMetrics:
        """Register a new workflow"""
        metrics = WorkflowMetrics(
            workflow_id=workflow_id,
            started_at=datetime.now(),
            tasks_total=tasks_total,
            status="active"
        )
        self.workflows[workflow_id] = metrics
        logger.debug(f"Registered workflow: {workflow_id}")
        return metrics

    def update_workflow(self, workflow_id: str, tasks_completed: int = None, status: str = None):
        """Update workflow metrics"""
        if workflow_id not in self.workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return

        workflow = self.workflows[workflow_id]

        if tasks_completed is not None:
            workflow.tasks_completed = tasks_completed

        if status:
            workflow.status = status
            if status in ["completed", "failed"]:
                workflow.completed_at = datetime.now()

        # Update total tasks completed
        if workflow.status == "completed":
            self.total_tasks_completed += workflow.tasks_completed

    def calculate_flow_rate(self) -> FlowRateStatistics:
        """
        Calculate current flow rate using algebraic formula

        Formula: F = (W_completed / T_elapsed) * (W_active / W_total) * efficiency_factor
        """
        now = datetime.now()
        active_workflows = [w for w in self.workflows.values() if w.status == "active"]
        completed_workflows = [w for w in self.workflows.values() if w.status == "completed"]
        total_workflows = len(self.workflows)

        # Calculate tasks completed per second for active workflows
        active_flow_rates = []
        total_tasks_per_second = 0.0

        for workflow in active_workflows:
            flow_rate = workflow.flow_rate
            active_flow_rates.append(flow_rate)
            total_tasks_per_second += flow_rate

        # Calculate average flow rate for active workflows
        current_flow_rate = sum(active_flow_rates) / len(active_workflows) if active_workflows else 0.0

        # Calculate efficiency factor (completion rate average)
        efficiency_factors = [w.completion_rate for w in active_workflows]
        efficiency = sum(efficiency_factors) / len(efficiency_factors) if efficiency_factors else 0.0

        # Apply algebraic formula: F = (W_completed / T_elapsed) * (W_active / W_total) * efficiency
        active_ratio = len(active_workflows) / total_workflows if total_workflows > 0 else 0.0

        # Total elapsed time
        elapsed_time = (now - self.start_time).total_seconds()

        # Enhanced formula with efficiency
        enhanced_flow_rate = current_flow_rate * active_ratio * (1.0 + efficiency)

        # Calculate average over time window
        cutoff_time = now - timedelta(seconds=self.time_window)
        recent_samples = [s for s in self.flow_rate_history if s.timestamp >= cutoff_time]

        if recent_samples:
            average_flow_rate = sum(s.current_flow_rate for s in recent_samples) / len(recent_samples)
        else:
            average_flow_rate = enhanced_flow_rate

        # Update peak
        if enhanced_flow_rate > self.peak_flow_rate:
            self.peak_flow_rate = enhanced_flow_rate

        # Create statistics
        stats = FlowRateStatistics(
            timestamp=now,
            current_flow_rate=enhanced_flow_rate,
            average_flow_rate=average_flow_rate,
            peak_flow_rate=self.peak_flow_rate,
            active_workflows=len(active_workflows),
            completed_workflows=len(completed_workflows),
            total_workflows=total_workflows,
            tasks_per_second=total_tasks_per_second,
            efficiency=efficiency
        )

        # Add to history
        self.flow_rate_history.append(stats)

        return stats

    def get_display_text(self, max_length: int = 80) -> str:
        """
        Get formatted text for IDE footer display

        Format: [FLOW: X.XX/s AVG: X.XX/s PEAK: X.XX/s ACTIVE: X EFF: XX%]
        """
        stats = self.calculate_flow_rate()

        # Format numbers
        current = f"{stats.current_flow_rate:.2f}"
        avg = f"{stats.average_flow_rate:.2f}"
        peak = f"{stats.peak_flow_rate:.2f}"
        efficiency_pct = f"{stats.efficiency * 100:.0f}"

        # Build display text
        display = f"FLOW: {current}/s AVG: {avg}/s PEAK: {peak}/s ACTIVE: {stats.active_workflows} EFF: {efficiency_pct}%"

        # Add tasks/sec if space allows
        if len(display) < max_length - 20:
            display += f" TASKS: {stats.tasks_per_second:.2f}/s"

        # Truncate if too long
        if len(display) > max_length:
            display = display[:max_length-3] + "..."

        return display

    def get_scrolling_ticker(self, width: int = 80, scroll_speed: int = 1) -> str:
        """
        Get scrolling ticker text (airport style)

        Args:
            width: Display width in characters
            scroll_speed: Scroll speed (characters per update)
        """
        stats = self.calculate_flow_rate()

        # Build full text with all metrics
        full_text = (
            f"⚡ FLOW: {stats.current_flow_rate:.2f}/s | "
            f"📊 AVG: {stats.average_flow_rate:.2f}/s | "
            f"🏆 PEAK: {stats.peak_flow_rate:.2f}/s | "
            f"🔄 ACTIVE: {stats.active_workflows}/{stats.total_workflows} | "
            f"✅ COMPLETED: {stats.completed_workflows} | "
            f"⚙️ EFF: {stats.efficiency * 100:.0f}% | "
            f"📈 TASKS: {stats.tasks_per_second:.2f}/s"
        )

        # If text fits, return as-is
        if len(full_text) <= width:
            return full_text

        # Create scrolling effect
        # Calculate scroll position based on time
        scroll_position = int((time.time() * scroll_speed) % (len(full_text) + width))

        # Extract visible portion
        if scroll_position < len(full_text):
            visible = full_text[scroll_position:scroll_position + width]
        else:
            # Wrap around
            visible = full_text[scroll_position - len(full_text):] + full_text[:scroll_position + width - len(full_text)]

        # Pad to width
        visible = visible.ljust(width)

        return visible


if __name__ == "__main__":
    print("\n" + "="*80)
    print("@PEAK Workflow Flow Rate Calculator")
    print("="*80 + "\n")

    calculator = WorkflowFlowRateCalculator(time_window=60)

    # Simulate some workflows
    for i in range(5):
        workflow_id = f"workflow_{i+1}"
        calculator.register_workflow(workflow_id, tasks_total=10)
        calculator.update_workflow(workflow_id, tasks_completed=5 + i)
        time.sleep(0.1)

    # Calculate flow rate
    stats = calculator.calculate_flow_rate()

    print("📊 Flow Rate Statistics:")
    print(f"   Current Flow Rate: {stats.current_flow_rate:.2f} workflows/s")
    print(f"   Average Flow Rate: {stats.average_flow_rate:.2f} workflows/s")
    print(f"   Peak Flow Rate: {stats.peak_flow_rate:.2f} workflows/s")
    print(f"   Active Workflows: {stats.active_workflows}")
    print(f"   Completed Workflows: {stats.completed_workflows}")
    print(f"   Efficiency: {stats.efficiency * 100:.1f}%")
    print(f"   Tasks/sec: {stats.tasks_per_second:.2f}")

    print(f"\n📺 IDE Footer Display (Standard):")
    print(f"   {calculator.get_display_text()}")

    print(f"\n📺 IDE Footer Display (Scrolling Ticker):")
    for i in range(3):
        ticker = calculator.get_scrolling_ticker(width=80, scroll_speed=2)
        print(f"   {ticker}")
        time.sleep(0.5)

    print("\n✅ Flow Rate Calculator Test Complete")
    print("="*80 + "\n")
