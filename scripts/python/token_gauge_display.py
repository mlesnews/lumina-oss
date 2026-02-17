#!/usr/bin/env python3
"""
Token Gauge Display - Visual Digital Gauge Component
====================================================

Creates a visual digital gauge display similar to bandwidth speedtest gauges.
Shows: Min | Current | Max with percentage indicators.

Format:
┌─────────────────────────────────────────┐
│ TOKENS/MIN: [MIN: 0] [CURRENT: 1234] [MAX: 5000] (25%) │
│ COST/MIN:   [MIN: $0] [CURRENT: $0.05] [MAX: $0.20] (25%) │
│ ASKS:       [USED: 150 / 1000] (15%) │
└─────────────────────────────────────────┘
"""

import json
from pathlib import Path
from typing import Dict, Optional
import sys

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from token_usage_monitor import TokenUsageMonitor
except ImportError:
    print("❌ Could not import TokenUsageMonitor")
    sys.exit(1)


class TokenGaugeDisplay:
    """Visual digital gauge display for token usage."""

    def __init__(self):
        """Initialize gauge display."""
        self.monitor = TokenUsageMonitor()
        self.gauge_file = self.monitor.gauge_file

    def _format_number(self, value: float, decimals: int = 0) -> str:
        """Format number with commas."""
        if decimals == 0:
            return f"{int(value):,}"
        return f"{value:,.{decimals}f}"

    def _format_percentage(self, value: float) -> str:
        """Format percentage."""
        return f"{value:.1f}%"

    def _create_gauge_bar(self, current: float, min_val: float, max_val: float, width: int = 40) -> str:
        """Create a visual gauge bar."""
        if max_val == 0:
            return " " * width

        percentage = (current - min_val) / (max_val - min_val) if max_val > min_val else 0.0
        percentage = max(0.0, min(1.0, percentage))

        filled = int(percentage * width)
        bar = "█" * filled + "░" * (width - filled)

        return bar

    def get_header_display(self) -> str:
        """Get formatted header display string."""
        data = self.monitor.get_gauge_display()
        if not data:
            return "Token Usage: No data"

        gauges = data.get("gauges", {})
        lines = []

        # Tokens per minute (60min window)
        tpm_60 = gauges.get("tokens_per_minute", {}).get("60min", {})
        if tpm_60 and isinstance(tpm_60, dict):
            current = tpm_60.get("current", 0)
            min_val = tpm_60.get("min", 0)
            max_val = tpm_60.get("max", 1)  # Avoid division by zero
            avg = tpm_60.get("average", 0)
            pct = tpm_60.get("percentage", 0)

            if max_val == 0:
                max_val = max(1, current * 2)  # Dynamic max

            bar = self._create_gauge_bar(current, min_val, max_val, 30)
            lines.append(
                f"TOKENS/MIN: [MIN: {self._format_number(min_val)}] "
                f"[CURRENT: {self._format_number(current)}] "
                f"[MAX: {self._format_number(max_val)}] "
                f"({self._format_percentage(pct)}) {bar}"
            )

        # Cost per minute (60min window)
        cpm_60 = gauges.get("cost_per_minute", {}).get("60min", {})
        if cpm_60 and isinstance(cpm_60, dict):
            current = cpm_60.get("current", 0)
            min_val = cpm_60.get("min", 0)
            max_val = cpm_60.get("max", 0.01)  # Default max
            pct = cpm_60.get("percentage", 0)

            if max_val == 0:
                max_val = max(0.01, current * 2)

            bar = self._create_gauge_bar(current, min_val, max_val, 30)
            lines.append(
                f"COST/MIN:   [MIN: ${self._format_number(min_val, 4)}] "
                f"[CURRENT: ${self._format_number(current, 4)}] "
                f"[MAX: ${self._format_number(max_val, 4)}] "
                f"({self._format_percentage(pct)}) {bar}"
            )

        # Subscription usage
        sub = gauges.get("subscription", {})
        if sub:
            used = sub.get("asks_used", 0)
            remaining = sub.get("asks_remaining", 0)
            pct = sub.get("percentage_used", 0)
            max_asks = self.monitor.subscription_max_asks

            if max_asks > 0:
                bar = self._create_gauge_bar(used, 0, max_asks, 30)
                lines.append(
                    f"ASKS:       [USED: {self._format_number(used)} / {self._format_number(max_asks)}] "
                    f"({self._format_percentage(pct)}) {bar}"
                )
            else:
                lines.append(
                    f"ASKS:       [USED: {self._format_number(used)}] (unlimited)"
                )

        # Local vs Cloud split
        local_tokens = gauges.get("local_usage", {}).get("tokens", {})
        cloud_tokens = gauges.get("cloud_usage", {}).get("tokens", {})

        if local_tokens and isinstance(local_tokens, dict):
            local_current = local_tokens.get("current", 0)
            local_pct = local_tokens.get("percentage", 0)
            lines.append(
                f"LOCAL:      {self._format_number(local_current)} tokens ({self._format_percentage(local_pct)})"
            )

        if cloud_tokens and isinstance(cloud_tokens, dict):
            cloud_current = cloud_tokens.get("current", 0)
            cloud_pct = cloud_tokens.get("percentage", 0)
            lines.append(
                f"CLOUD:      {self._format_number(cloud_current)} tokens ({self._format_percentage(cloud_pct)})"
            )

        return " | ".join(lines)

    def get_compact_display(self) -> str:
        """Get compact single-line display."""
        data = self.monitor.get_gauge_display()
        if not data:
            return "Token Usage: No data"

        gauges = data.get("gauges", {})
        parts = []

        # Tokens/min
        tpm_60 = gauges.get("tokens_per_minute", {}).get("60min", {})
        if tpm_60 and isinstance(tpm_60, dict):
            current = tpm_60.get("current", 0)
            parts.append(f"Tokens: {self._format_number(current)}/min")

        # Cost/min
        cpm_60 = gauges.get("cost_per_minute", {}).get("60min", {})
        if cpm_60 and isinstance(cpm_60, dict):
            current = cpm_60.get("current", 0)
            parts.append(f"Cost: ${self._format_number(current, 4)}/min")

        # Subscription
        sub = gauges.get("subscription", {})
        if sub:
            used = sub.get("asks_used", 0)
            max_asks = self.monitor.subscription_max_asks
            if max_asks > 0:
                pct = sub.get("percentage_used", 0)
                parts.append(f"Asks: {self._format_number(used)}/{self._format_number(max_asks)} ({self._format_percentage(pct)})")
            else:
                parts.append(f"Asks: {self._format_number(used)}")

        return " | ".join(parts)

    def print_display(self):
        """Print formatted display."""
        print("\n" + "=" * 100)
        print("📊 TOKEN USAGE GAUGES - DIGITAL DISPLAY")
        print("=" * 100)
        print()
        print(self.get_header_display())
        print()
        print("=" * 100)
        print()


def main():
    """Main entry point."""
    display = TokenGaugeDisplay()
    display.print_display()


if __name__ == "__main__":


    main()