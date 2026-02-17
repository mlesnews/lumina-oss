#!/usr/bin/env python3
"""
Flow Rate Per Second Monitor

Monitors flow rate per second with:
- WACA time integration
- AI Token Request Tracking Rates
- Real-time flow rate calculation
- Historical tracking
- Performance analytics
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import deque

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


@dataclass
class FlowRateEntry:
    """Flow rate entry"""
    timestamp: float
    flow_rate: float  # Flow rate per second
    waca_time: Optional[float] = None  # WACA time
    ai_token_requests: Optional[int] = None  # AI token requests
    ai_tokens_used: Optional[int] = None  # AI tokens used
    agent: Optional[str] = None  # Agent name (kilo_code, github_copilot, iron_legion, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FlowRateMetrics:
    """Flow rate metrics"""
    current_flow_rate: float
    average_flow_rate: float
    peak_flow_rate: float
    waca_time_total: float
    ai_token_requests_total: int
    ai_tokens_used_total: int
    tokens_per_request: float
    requests_per_second: float
    timestamp: str
    time_window_seconds: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FlowRateMonitor:
    """
    Flow Rate Per Second Monitor

    PRIMARY METRIC: FLOW RATE PER SECOND

    Integrates with:
    - WACA time tracking
    - AI Token Request Tracking Rates

    Flow Rate Per Second = Number of flow events per second
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("FlowRateMonitor")

        # Directories
        self.data_dir = self.project_root / "data" / "flow_rate_monitor"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.flow_rate_file = self.data_dir / "flow_rate_history.jsonl"
        self.metrics_file = self.data_dir / "flow_rate_metrics.json"

        # Token tracker config
        self.token_tracker_config = self.project_root / "config" / "ai_token_request_tracker.json"

        # Flow rate tracking
        self.flow_rate_history: deque = deque(maxlen=10000)  # Last 10k entries
        self.current_flow_rate: float = 0.0
        self.waca_time_total: float = 0.0
        self.ai_token_requests_total: int = 0
        self.ai_tokens_used_total: int = 0
        self.agent_token_usage: Dict[str, Dict[str, int]] = {}  # agent -> {requests, tokens}

        # Load state
        self._load_state()

    def _load_state(self):
        """Load flow rate history"""
        if self.flow_rate_file.exists():
            try:
                with open(self.flow_rate_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            # Handle backward compatibility (old field names)
                            if "cursor_api_tokens" in data:
                                data["ai_tokens_used"] = data.pop("cursor_api_tokens", 0)
                            if "cursor_api_requests" in data:
                                data["ai_token_requests"] = data.pop("cursor_api_requests", 0)
                            # Only include valid fields
                            entry_data = {
                                "timestamp": data.get("timestamp", time.time()),
                                "flow_rate": data.get("flow_rate", 0.0),
                                "waca_time": data.get("waca_time"),
                                "ai_token_requests": data.get("ai_token_requests"),
                                "ai_tokens_used": data.get("ai_tokens_used"),
                                "agent": data.get("agent"),
                                "metadata": data.get("metadata", {})
                            }
                            entry = FlowRateEntry(**entry_data)
                            self.flow_rate_history.append(entry)
            except Exception as e:
                self.logger.error(f"Error loading flow rate history: {e}")

        # Load metrics
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    metrics_data = json.load(f)
                    self.waca_time_total = metrics_data.get("waca_time_total", 0.0)
                    self.ai_token_requests_total = metrics_data.get("ai_token_requests_total", 0)
                    self.ai_tokens_used_total = metrics_data.get("ai_tokens_used_total", 0)
                    self.agent_token_usage = metrics_data.get("agent_token_usage", {})
            except Exception as e:
                self.logger.error(f"Error loading metrics: {e}")

    def _save_entry(self, entry: FlowRateEntry):
        try:
            """Save flow rate entry"""
            # Add to history
            self.flow_rate_history.append(entry)

            # Append to file
            with open(self.flow_rate_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.to_dict()) + '\n')

        except Exception as e:
            self.logger.error(f"Error in _save_entry: {e}", exc_info=True)
            raise
    def _save_metrics(self):
        try:
            """Save metrics"""
            metrics_data = {
                "waca_time_total": self.waca_time_total,
                "ai_token_requests_total": self.ai_token_requests_total,
                "ai_tokens_used_total": self.ai_tokens_used_total,
                "agent_token_usage": self.agent_token_usage,
                "updated_at": datetime.now().isoformat()
            }
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_metrics: {e}", exc_info=True)
            raise
    def record_flow_event(
        self,
        waca_time: Optional[float] = None,
        ai_token_requests: Optional[int] = None,
        ai_tokens_used: Optional[int] = None,
        agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record a flow event with AI token request tracking

        Updates flow rate per second
        """
        now = time.time()

        # Calculate flow rate from recent events (last 60 seconds)
        recent_entries = [
            e for e in self.flow_rate_history
            if (now - e.timestamp) < 60
        ]

        # Flow rate = number of events per second
        flow_rate = len(recent_entries) / 60.0 if recent_entries else 0.0

        # Update totals
        if waca_time:
            self.waca_time_total += waca_time
        if ai_token_requests:
            self.ai_token_requests_total += ai_token_requests
        if ai_tokens_used:
            self.ai_tokens_used_total += ai_tokens_used

        # Track per-agent usage
        if agent:
            if agent not in self.agent_token_usage:
                self.agent_token_usage[agent] = {"requests": 0, "tokens": 0}
            if ai_token_requests:
                self.agent_token_usage[agent]["requests"] += ai_token_requests
            if ai_tokens_used:
                self.agent_token_usage[agent]["tokens"] += ai_tokens_used

        # Create entry
        entry = FlowRateEntry(
            timestamp=now,
            flow_rate=flow_rate,
            waca_time=waca_time,
            ai_token_requests=ai_token_requests,
            ai_tokens_used=ai_tokens_used,
            agent=agent,
            metadata=metadata or {}
        )

        # Save entry
        self._save_entry(entry)
        self._save_metrics()

        # Update current flow rate
        self.current_flow_rate = flow_rate

        self.logger.info(f"📊 FLOW RATE PER SECOND: {flow_rate:.4f}/s (WACA: {waca_time or 0:.2f}s, AI Token Requests: {ai_token_requests or 0}, AI Tokens: {ai_tokens_used or 0}, Agent: {agent or 'N/A'})")

    def get_flow_rate_per_second(self) -> float:
        """
        Get current FLOW RATE PER SECOND

        PRIMARY METRIC: Returns the current flow rate per second
        """
        return self.current_flow_rate

    def get_flow_rate_metrics(self, time_window_seconds: int = 60) -> FlowRateMetrics:
        """
        Get flow rate metrics

        Returns current, average, peak flow rates
        """
        now = time.time()

        # Get entries in time window
        window_entries = [
            e for e in self.flow_rate_history
            if (now - e.timestamp) <= time_window_seconds
        ]

        if not window_entries:
            return FlowRateMetrics(
                current_flow_rate=0.0,
                average_flow_rate=0.0,
                peak_flow_rate=0.0,
                waca_time_total=self.waca_time_total,
                ai_token_requests_total=self.ai_token_requests_total,
                ai_tokens_used_total=self.ai_tokens_used_total,
                tokens_per_request=0.0,
                requests_per_second=0.0,
                timestamp=datetime.now().isoformat(),
                time_window_seconds=time_window_seconds
            )

        # Calculate metrics
        flow_rates = [e.flow_rate for e in window_entries]
        current_flow_rate = self.current_flow_rate
        average_flow_rate = sum(flow_rates) / len(flow_rates) if flow_rates else 0.0
        peak_flow_rate = max(flow_rates) if flow_rates else 0.0

        # Calculate AI token request stats for window
        ai_requests_window = sum(e.ai_token_requests or 0 for e in window_entries)
        ai_tokens_window = sum(e.ai_tokens_used or 0 for e in window_entries)
        tokens_per_request = ai_tokens_window / max(ai_requests_window, 1)
        requests_per_second = ai_requests_window / time_window_seconds if time_window_seconds > 0 else 0.0

        return FlowRateMetrics(
            current_flow_rate=current_flow_rate,
            average_flow_rate=average_flow_rate,
            peak_flow_rate=peak_flow_rate,
            waca_time_total=self.waca_time_total,
            ai_token_requests_total=self.ai_token_requests_total,
            ai_tokens_used_total=self.ai_tokens_used_total,
            tokens_per_request=tokens_per_request,
            requests_per_second=requests_per_second,
            timestamp=datetime.now().isoformat(),
            time_window_seconds=time_window_seconds
        )

    def get_waca_time_integration(self) -> Dict[str, Any]:
        """Get WACA time integration data"""
        metrics = self.get_flow_rate_metrics()
        flow_rate_per_second = self.get_flow_rate_per_second()

        return {
            "flow_rate_per_second": flow_rate_per_second,  # PRIMARY METRIC
            "waca_time_total": self.waca_time_total,
            "waca_time_per_flow_rate": self.waca_time_total / max(flow_rate_per_second, 0.001),
            "timestamp": datetime.now().isoformat()
        }

    def get_ai_token_request_tracking(self) -> Dict[str, Any]:
        """Get AI Token Request Tracking Rates integration"""
        metrics = self.get_flow_rate_metrics()
        flow_rate_per_second = self.get_flow_rate_per_second()

        return {
            "flow_rate_per_second": flow_rate_per_second,  # PRIMARY METRIC
            "ai_token_requests_total": self.ai_token_requests_total,
            "ai_tokens_used_total": self.ai_tokens_used_total,
            "tokens_per_request": metrics.tokens_per_request,
            "requests_per_second": metrics.requests_per_second,
            "requests_per_flow_rate": self.ai_token_requests_total / max(flow_rate_per_second, 0.001),
            "agent_token_usage": self.agent_token_usage,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Main execution for testing"""
    monitor = FlowRateMonitor()

    print("=" * 80)
    print("📊 FLOW RATE PER SECOND MONITOR")
    print("=" * 80)

    # Record some flow events with AI token request tracking
    agents = ["kilo_code", "github_copilot", "llama3.2:3b", "jarvis"]
    for i in range(10):
        agent = agents[i % len(agents)]
        monitor.record_flow_event(
            waca_time=0.5,
            ai_token_requests=1,
            ai_tokens_used=100 + (i * 10),
            agent=agent,
            metadata={"test": True}
        )
        time.sleep(0.1)

    # PRIMARY METRIC: FLOW RATE PER SECOND
    flow_rate_per_second = monitor.get_flow_rate_per_second()
    print(f"\n🚀 FLOW RATE PER SECOND (PRIMARY METRIC): {flow_rate_per_second:.4f}/s")

    # Get metrics
    metrics = monitor.get_flow_rate_metrics()

    print(f"\n📊 Flow Rate Metrics:")
    print(f"   ⭐ CURRENT FLOW RATE PER SECOND: {metrics.current_flow_rate:.4f}/s")
    print(f"   📈 Average Flow Rate Per Second: {metrics.average_flow_rate:.4f}/s")
    print(f"   📊 Peak Flow Rate Per Second: {metrics.peak_flow_rate:.4f}/s")
    print(f"   🕐 WACA Time Total: {metrics.waca_time_total:.2f}s")
    print(f"   🤖 AI Token Requests Total: {metrics.ai_token_requests_total}")
    print(f"   🔢 AI Tokens Used Total: {metrics.ai_tokens_used_total}")
    print(f"   📉 Tokens per Request: {metrics.tokens_per_request:.2f}")
    print(f"   ⚡ Requests per Second: {metrics.requests_per_second:.4f}")

    # Get integrations
    waca = monitor.get_waca_time_integration()
    ai_tracking = monitor.get_ai_token_request_tracking()

    print(f"\n🕐 WACA Time Integration:")
    print(f"   ⭐ FLOW RATE PER SECOND: {waca['flow_rate_per_second']:.4f}/s")
    print(f"   WACA Time Total: {waca['waca_time_total']:.2f}s")
    print(f"   WACA Time per Flow Rate: {waca['waca_time_per_flow_rate']:.4f}s")

    print(f"\n🤖 AI Token Request Tracking Rates:")
    print(f"   ⭐ FLOW RATE PER SECOND: {ai_tracking['flow_rate_per_second']:.4f}/s")
    print(f"   AI Token Requests Total: {ai_tracking['ai_token_requests_total']}")
    print(f"   AI Tokens Used Total: {ai_tracking['ai_tokens_used_total']}")
    print(f"   Tokens per Request: {ai_tracking['tokens_per_request']:.2f}")
    print(f"   Requests per Second: {ai_tracking['requests_per_second']:.4f}")
    print(f"   Requests per Flow Rate: {ai_tracking['requests_per_flow_rate']:.4f}")
    print(f"\n   Per-Agent Usage:")
    for agent, usage in ai_tracking['agent_token_usage'].items():
        print(f"     {agent}: {usage['requests']} requests, {usage['tokens']} tokens")


if __name__ == "__main__":



    main()