#!/usr/bin/env python3
"""
Token Usage Monitor - Digital Gauge System
===========================================

Tracks AI token usage with digital gauges showing:
- Current/Min/Max token requests
- Subscription limits
- Average cost per minute (local vs cloud)
- Exponential increment tracking
- Integration with Cursor and WakaTime metrics

@ASK @TOKEN @COST @MONITORING
"""

import json
import time
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import sys

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TokenUsageMonitor")


@dataclass
class TokenMetrics:
    """Token usage metrics for a time period."""
    timestamp: str
    tokens_used: int
    requests: int
    is_local: bool
    cost_usd: float
    duration_seconds: float


@dataclass
class GaugeMetrics:
    """Digital gauge display metrics."""
    current: float
    min: float
    max: float
    average: float
    percentage: float  # 0-100
    trend: str  # "up", "down", "stable"


class TokenUsageMonitor:
    """Monitor and track AI token usage with digital gauges."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the token usage monitor."""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "token_usage"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.metrics_file = self.data_dir / "metrics.jsonl"
        self.gauge_file = self.data_dir / "gauge_status.json"
        self.config_file = self.project_root / "config" / "token_usage_config.json"

        # Load configuration
        self.config = self._load_config()

        # Metrics storage (rolling window)
        self.metrics_window = deque(maxlen=1000)  # Last 1000 data points
        self._load_historical_metrics()

        # Subscription limits
        self.subscription_max_asks = self.config.get("subscription_max_asks", 0)
        self.subscription_reset_period = self.config.get("subscription_reset_period", "monthly")

        # Cost tracking
        self.local_cost_per_1k_tokens = self.config.get("local_cost_per_1k_tokens", 0.0)  # Free
        self.cloud_cost_per_1k_tokens = self.config.get("cloud_cost_per_1k_tokens", 0.002)  # Default

        # Total cost tracking (cumulative)
        self.total_cost_file = self.data_dir / "total_cost.json"
        # Get subscription fee from config
        subscription_config = self.config.get("subscription", {})
        self.subscription_fee = subscription_config.get("subscription_fee", 0.0) if isinstance(subscription_config, dict) else 0.0

        # Exponential tracking
        self.exponential_base = self.config.get("exponential_base", 1.1)
        self.exponential_window_minutes = self.config.get("exponential_window_minutes", 60)

    def _load_config(self) -> Dict:
        """Load configuration file."""
        default_config = {
            "subscription_max_asks": 0,  # 0 = unlimited or not set
            "subscription_reset_period": "monthly",
            "local_cost_per_1k_tokens": 0.0,
            "cloud_cost_per_1k_tokens": 0.002,  # $0.002 per 1K tokens (example)
            "exponential_base": 1.1,
            "exponential_window_minutes": 60,
            "gauge_update_interval_seconds": 1.0,
            "wakatime_integration": {
                "enabled": False,
                "api_key": None,
                "api_url": "https://wakatime.com/api/v1"
            },
            "cursor_integration": {
                "enabled": True,
                "metrics_path": None  # Auto-detect
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")

        return default_config

    def _load_historical_metrics(self):
        """Load historical metrics from file."""
        if not self.metrics_file.exists():
            return

        try:
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        metric = TokenMetrics(**data)
                        self.metrics_window.append(metric)
        except Exception as e:
            logger.warning(f"Could not load historical metrics: {e}")

    def _get_total_cost(self) -> Dict:
        """Get total cost tracking data."""
        default_data = {
            "total_cost_usd": 0.0,
            "period_start": datetime.now().replace(day=1, hour=0, minute=0, second=0).isoformat(),
            "period_type": self.subscription_reset_period,
            "last_updated": datetime.now().isoformat()
        }

        if not self.total_cost_file.exists():
            return default_data

        try:
            with open(self.total_cost_file, 'r') as f:
                data = json.load(f)
                # Check if period reset needed
                period_start = datetime.fromisoformat(data.get("period_start", default_data["period_start"]))
                now = datetime.now()

                if self.subscription_reset_period == "monthly":
                    if now.month != period_start.month or now.year != period_start.year:
                        # New month - reset
                        data = default_data
                        data["period_start"] = now.replace(day=1, hour=0, minute=0, second=0).isoformat()
                elif self.subscription_reset_period == "daily":
                    if now.date() != period_start.date():
                        # New day - reset
                        data = default_data
                        data["period_start"] = now.replace(hour=0, minute=0, second=0).isoformat()

                return data
        except Exception as e:
            logger.warning(f"Could not read total cost: {e}")
            return default_data

    def _update_total_cost(self, cost: float):
        """Update total cost tracking."""
        data = self._get_total_cost()
        data["total_cost_usd"] += cost
        data["last_updated"] = datetime.now().isoformat()

        try:
            with open(self.total_cost_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not write total cost: {e}")

    def record_usage(self, tokens: int, is_local: bool = False, duration_seconds: float = 0.0):
        """Record token usage."""
        # Calculate cost
        cost_per_1k = self.local_cost_per_1k_tokens if is_local else self.cloud_cost_per_1k_tokens
        cost = (tokens / 1000.0) * cost_per_1k

        metric = TokenMetrics(
            timestamp=datetime.now().isoformat(),
            tokens_used=tokens,
            requests=1,
            is_local=is_local,
            cost_usd=cost,
            duration_seconds=duration_seconds
        )

        # Store metric
        self.metrics_window.append(metric)

        # Update total cost (only cloud costs count)
        if not is_local and cost > 0:
            self._update_total_cost(cost)

        # Append to file
        try:
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(asdict(metric)) + "\n")
        except Exception as e:
            logger.error(f"Could not write metric: {e}")

        # Update gauges
        self._update_gauges()

    def _calculate_exponential_increment(self, window_minutes: int = None) -> float:
        """Calculate exponential increment based on usage pattern."""
        if window_minutes is None:
            window_minutes = self.exponential_window_minutes

        # Get metrics from last N minutes
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_metrics = [
            m for m in self.metrics_window
            if datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]

        if not recent_metrics:
            return 0.0

        # Calculate exponential growth
        total_tokens = sum(m.tokens_used for m in recent_metrics)
        total_requests = sum(m.requests for m in recent_metrics)

        if total_requests == 0:
            return 0.0

        # Exponential formula: base^(requests/10) - 1
        # More requests = faster growth
        exponent = total_requests / 10.0
        increment = (self.exponential_base ** exponent) - 1.0

        return increment * total_tokens

    def _calculate_gauge_metrics(self, metric_type: str, window_minutes: int = 60) -> GaugeMetrics:
        """Calculate gauge metrics for a specific type."""
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_metrics = [
            m for m in self.metrics_window
            if datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]

        if not recent_metrics:
            return GaugeMetrics(
                current=0.0,
                min=0.0,
                max=0.0,
                average=0.0,
                percentage=0.0,
                trend="stable"
            )

        # Extract values based on metric type
        if metric_type == "tokens":
            values = [m.tokens_used for m in recent_metrics]
        elif metric_type == "requests":
            values = [m.requests for m in recent_metrics]
        elif metric_type == "cost":
            values = [m.cost_usd for m in recent_metrics]
        elif metric_type == "tokens_per_minute":
            # Calculate tokens per minute
            total_tokens = sum(m.tokens_used for m in recent_metrics)
            total_minutes = window_minutes
            values = [total_tokens / total_minutes] if total_minutes > 0 else [0.0]
        else:
            values = [0.0]

        current = values[-1] if values else 0.0
        min_val = min(values) if values else 0.0
        max_val = max(values) if values else 0.0
        avg_val = sum(values) / len(values) if values else 0.0

        # Calculate percentage (0-100) based on max
        percentage = (current / max_val * 100) if max_val > 0 else 0.0

        # Determine trend
        if len(values) >= 2:
            recent_avg = sum(values[-5:]) / min(5, len(values))
            older_avg = sum(values[:-5]) / max(1, len(values) - 5) if len(values) > 5 else recent_avg
            if recent_avg > older_avg * 1.1:
                trend = "up"
            elif recent_avg < older_avg * 0.9:
                trend = "down"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return GaugeMetrics(
            current=current,
            min=min_val,
            max=max_val,
            average=avg_val,
            percentage=percentage,
            trend=trend
        )

    def _update_gauges(self):
        """Update all gauge metrics."""
        now = datetime.now()

        # Calculate metrics for different time windows
        gauges = {
            "tokens_per_minute": {
                "1min": self._calculate_gauge_metrics("tokens_per_minute", 1),
                "5min": self._calculate_gauge_metrics("tokens_per_minute", 5),
                "60min": self._calculate_gauge_metrics("tokens_per_minute", 60),
            },
            "cost_per_minute": {
                "1min": self._calculate_gauge_metrics("cost", 1),
                "5min": self._calculate_gauge_metrics("cost", 5),
                "60min": self._calculate_gauge_metrics("cost", 60),
            },
            "requests_per_minute": {
                "1min": self._calculate_gauge_metrics("requests", 1),
                "5min": self._calculate_gauge_metrics("requests", 5),
                "60min": self._calculate_gauge_metrics("requests", 60),
            },
            "local_usage": {
                "tokens": self._calculate_gauge_metrics("tokens", 60),
                "cost": self._calculate_gauge_metrics("cost", 60),
            },
            "cloud_usage": {
                "tokens": self._calculate_gauge_metrics("tokens", 60),
                "cost": self._calculate_gauge_metrics("cost", 60),
            },
            "subscription": {
                "asks_used": self._get_subscription_usage(),
                "asks_remaining": max(0, self.subscription_max_asks - self._get_subscription_usage()),
                "percentage_used": (self._get_subscription_usage() / self.subscription_max_asks * 100) if self.subscription_max_asks > 0 else 0.0,
            },
            "exponential_increment": {
                "1min": self._calculate_exponential_increment(1),
                "5min": self._calculate_exponential_increment(5),
                "60min": self._calculate_exponential_increment(60),
            },
            "total_cost": {
                "total_usd": self._get_total_cost().get("total_cost_usd", 0.0),
                "subscription_fee": self.subscription_fee,
                "percentage_of_fee": (self._get_total_cost().get("total_cost_usd", 0.0) / self.subscription_fee * 100) if self.subscription_fee > 0 else 0.0,
            },
            "burn_rate": {
                "current_per_min": self._calculate_gauge_metrics("cost", 1).current,
                "average_per_min": self._calculate_gauge_metrics("cost", 60).average,
                "ratio": (self._calculate_gauge_metrics("cost", 1).current / self._calculate_gauge_metrics("cost", 60).average) if self._calculate_gauge_metrics("cost", 60).average > 0 else 1.0,
            }
        }

        # Convert to JSON-serializable format
        gauge_data = {
            "timestamp": now.isoformat(),
            "gauges": {}
        }

        for gauge_name, gauge_values in gauges.items():
            gauge_data["gauges"][gauge_name] = {}
            for key, value in gauge_values.items():
                if isinstance(value, GaugeMetrics):
                    gauge_data["gauges"][gauge_name][key] = asdict(value)
                else:
                    gauge_data["gauges"][gauge_name][key] = value

        # Save to file
        try:
            with open(self.gauge_file, 'w') as f:
                json.dump(gauge_data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not write gauge data: {e}")

    def _get_subscription_usage(self) -> int:
        """Get current subscription usage (asks used)."""
        # Count requests in current period
        if self.subscription_reset_period == "monthly":
            cutoff = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        elif self.subscription_reset_period == "daily":
            cutoff = datetime.now().replace(hour=0, minute=0, second=0)
        else:
            cutoff = datetime.now() - timedelta(days=30)

        recent_metrics = [
            m for m in self.metrics_window
            if datetime.fromisoformat(m.timestamp) >= cutoff
        ]

        return sum(m.requests for m in recent_metrics)

    def get_gauge_display(self) -> Dict:
        """Get formatted gauge display data."""
        if not self.gauge_file.exists():
            self._update_gauges()

        try:
            with open(self.gauge_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not read gauge data: {e}")
            return {}

    def print_gauge_display(self):
        """Print formatted gauge display."""
        data = self.get_gauge_display()
        if not data:
            print("No gauge data available")
            return

        gauges = data.get("gauges", {})

        print("\n" + "=" * 80)
        print("📊 TOKEN USAGE GAUGES")
        print("=" * 80)
        print()

        # Tokens per minute
        tpm = gauges.get("tokens_per_minute", {})
        if tpm:
            print("🔢 TOKENS PER MINUTE:")
            for window, metrics in tpm.items():
                if isinstance(metrics, dict):
                    current = metrics.get("current", 0)
                    avg = metrics.get("average", 0)
                    trend = metrics.get("trend", "stable")
                    trend_icon = "📈" if trend == "up" else "📉" if trend == "down" else "➡️"
                    print(f"   {window:>6}: {current:>10.0f} tokens/min (avg: {avg:.0f}) {trend_icon}")
            print()

        # Cost per minute
        cpm = gauges.get("cost_per_minute", {})
        if cpm:
            print("💰 COST PER MINUTE:")
            for window, metrics in cpm.items():
                if isinstance(metrics, dict):
                    current = metrics.get("current", 0)
                    avg = metrics.get("average", 0)
                    print(f"   {window:>6}: ${current:>10.4f}/min (avg: ${avg:.4f})")
            print()

        # Subscription
        sub = gauges.get("subscription", {})
        if sub:
            used = sub.get("asks_used", 0)
            remaining = sub.get("asks_remaining", 0)
            pct = sub.get("percentage_used", 0)
            max_asks = self.subscription_max_asks

            print("📋 SUBSCRIPTION USAGE:")
            if max_asks > 0:
                print(f"   Used: {used:,} / {max_asks:,} asks ({pct:.1f}%)")
                print(f"   Remaining: {remaining:,} asks")
            else:
                print(f"   Used: {used:,} asks (unlimited subscription)")
            print()

        # Local vs Cloud
        local = gauges.get("local_usage", {})
        cloud = gauges.get("cloud_usage", {})
        if local or cloud:
            print("🌐 USAGE BY TYPE:")
            if local.get("tokens"):
                local_tokens = local["tokens"].get("current", 0) if isinstance(local["tokens"], dict) else 0
                local_cost = local["cost"].get("current", 0) if isinstance(local["cost"], dict) else 0
                print(f"   Local:  {local_tokens:>10.0f} tokens (${local_cost:.4f})")
            if cloud.get("tokens"):
                cloud_tokens = cloud["tokens"].get("current", 0) if isinstance(cloud["tokens"], dict) else 0
                cloud_cost = cloud["cost"].get("current", 0) if isinstance(cloud["cost"], dict) else 0
                print(f"   Cloud:  {cloud_tokens:>10.0f} tokens (${cloud_cost:.4f})")
            print()

        # Exponential increment
        exp = gauges.get("exponential_increment", {})
        if exp:
            print("📈 EXPONENTIAL INCREMENT:")
            for window, value in exp.items():
                if isinstance(value, (int, float)):
                    print(f"   {window:>6}: {value:>10.0f} tokens")
            print()

        print("=" * 80)
        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Token Usage Monitor")
    parser.add_argument("--display", action="store_true", help="Display current gauges")
    parser.add_argument("--record", type=int, help="Record token usage (provide token count)")
    parser.add_argument("--local", action="store_true", help="Mark usage as local (free)")
    parser.add_argument("--duration", type=float, default=0.0, help="Duration in seconds")
    parser.add_argument("--update", action="store_true", help="Update gauges")

    args = parser.parse_args()

    monitor = TokenUsageMonitor()

    if args.record:
        monitor.record_usage(args.record, is_local=args.local, duration_seconds=args.duration)
        print(f"✅ Recorded {args.record} tokens ({'local' if args.local else 'cloud'})")
    elif args.update:
        monitor._update_gauges()
        print("✅ Gauges updated")
    elif args.display:
        monitor.print_gauge_display()
    else:
        # Default: display
        monitor.print_gauge_display()


if __name__ == "__main__":


    main()