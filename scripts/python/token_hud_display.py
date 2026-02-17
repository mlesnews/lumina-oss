#!/usr/bin/env python3
"""
Token Usage HUD Display - Iron Man Suit Helmet Style
=====================================================

Visual HUD display similar to Iron Man's helmet interface:
- Power Source (Local/Cloud) = Gas/Electric indicator
- Accelerator = Token usage rate
- RPM = Requests per minute  
- Speed (MPH/KPH) = Tokens per minute

@JARVIS @HUD @IRONMAN @DASHBOARD
"""

import json
import math
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


class TokenHUDDisplay:
    """Iron Man HUD-style token usage display."""

    def __init__(self):
        """Initialize HUD display."""
        self.monitor = TokenUsageMonitor()
        self.gauge_file = self.monitor.gauge_file

    def _create_speedometer(self, current: float, max_val: float, label: str, unit: str = "", width: int = 20) -> str:
        """Create a speedometer-style gauge."""
        if max_val == 0:
            max_val = max(1, current * 2)

        percentage = min(100, (current / max_val * 100) if max_val > 0 else 0)

        # Create arc gauge (visual representation)
        filled = int(percentage / 100 * width)
        gauge_bar = "█" * filled + "░" * (width - filled)

        # Format value
        if current >= 1000:
            value_str = f"{current/1000:.1f}K"
        else:
            value_str = f"{int(current)}"

        return f"{label:12} [{gauge_bar:20}] {value_str:>8} {unit}"

    def _create_rpm_gauge(self, rpm: float, max_rpm: float = 100) -> str:
        """Create RPM-style tachometer."""
        if max_rpm == 0:
            max_rpm = max(100, rpm * 2)

        percentage = min(100, (rpm / max_rpm * 100) if max_rpm > 0 else 0)

        # RPM zones
        if percentage < 33:
            zone = "🟢 IDLE"
            color = "green"
        elif percentage < 66:
            zone = "🟡 NORMAL"
            color = "yellow"
        elif percentage < 90:
            zone = "🟠 HIGH"
            color = "orange"
        else:
            zone = "🔴 MAX"
            color = "red"

        filled = int(percentage / 100 * 30)
        gauge_bar = "█" * filled + "░" * (30 - filled)

        return f"RPM: [{gauge_bar:30}] {rpm:>6.0f} {zone}"

    def _create_power_source_indicator(self, is_local: bool, local_pct: float, cloud_pct: float) -> str:
        """Create power source indicator (Gas/Electric style)."""
        if is_local:
            source = "⚡ ELECTRIC (LOCAL)"
            fuel_level = local_pct
            fuel_type = "LOCAL"
        else:
            source = "⛽ GAS (CLOUD)"
            fuel_level = cloud_pct
            fuel_type = "CLOUD"

        # Fuel gauge
        filled = int(fuel_level / 100 * 25)
        fuel_bar = "█" * filled + "░" * (25 - filled)

        return f"POWER: {source:20} [{fuel_bar:25}] {fuel_level:>5.1f}% {fuel_type}"

    def _create_speed_indicator(self, speed: float, unit: str = "TOK/MIN") -> str:
        """Create speed indicator (MPH/KPH style)."""
        # Speed zones
        if speed < 100:
            zone = "🟢 CRUISE"
        elif speed < 1000:
            zone = "🟡 ACCEL"
        elif speed < 5000:
            zone = "🟠 FAST"
        else:
            zone = "🔴 LUDICROUS"

        # Format speed
        if speed >= 1000000:
            speed_str = f"{speed/1000000:.2f}M"
        elif speed >= 1000:
            speed_str = f"{speed/1000:.1f}K"
        else:
            speed_str = f"{int(speed)}"

        return f"SPEED: {speed_str:>8} {unit:8} {zone}"

    def _create_accelerator_indicator(self, current: float, min_val: float, max_val: float) -> str:
        """Create accelerator pedal indicator."""
        if max_val == 0:
            max_val = max(1, current * 2)

        percentage = min(100, ((current - min_val) / (max_val - min_val) * 100) if max_val > min_val else 0)

        # Accelerator zones
        if percentage < 25:
            zone = "IDLE"
            pedal = "▁"
        elif percentage < 50:
            zone = "LIGHT"
            pedal = "▃"
        elif percentage < 75:
            zone = "MODERATE"
            pedal = "▅"
        elif percentage < 95:
            zone = "HEAVY"
            pedal = "▇"
        else:
            zone = "FLOORED"
            pedal = "█"

        filled = int(percentage / 100 * 30)
        gauge_bar = "█" * filled + "░" * (30 - filled)

        return f"ACCEL: [{gauge_bar:30}] {pedal} {zone:8} ({percentage:>5.1f}%)"

    def _create_full_circle_speedometer(self, speed: float, max_speed: float = 10000) -> tuple:
        """Create full circle speedometer (like vehicle dashboard).

        Returns tuple of (top_line, bottom_line, speed_str, percentage, zone)
        """
        if max_speed == 0:
            max_speed = max(10000, speed * 2)

        percentage = min(100, (speed / max_speed * 100) if max_speed > 0 else 0)

        # Create full circle visual (20 segments for display)
        segments = 20
        filled_segments = int((percentage / 100.0) * segments)

        # Build circle: filled vs empty
        circle_top = []
        circle_bottom = []

        # Top half (10 segments, left to right)
        for i in range(10):
            seg_num = i + 5  # Start from segment 5 (12 o'clock position)
            if seg_num < filled_segments:
                # Filled - gradient based on position
                if i < 3:
                    circle_top.append("▁")
                elif i < 6:
                    circle_top.append("▃")
                else:
                    circle_top.append("▅")
            else:
                circle_top.append("░")

        # Bottom half (10 segments, right to left)
        for i in range(10):
            seg_num = (20 - i) % 20  # Wrap around
            if seg_num < filled_segments:
                if i < 3:
                    circle_bottom.append("▅")
                elif i < 6:
                    circle_bottom.append("▃")
                else:
                    circle_bottom.append("▁")
            else:
                circle_bottom.append("░")

        top_half = "".join(circle_top)
        bottom_half = "".join(circle_bottom)

        # Format speed
        if speed >= 1000000:
            speed_str = f"{speed/1000000:.2f}M"
        elif speed >= 1000:
            speed_str = f"{speed/1000:.1f}K"
        else:
            speed_str = f"{int(speed)}"

        # Speed zones for color
        if percentage < 25:
            zone = "🟢"
        elif percentage < 50:
            zone = "🟡"
        elif percentage < 75:
            zone = "🟠"
        else:
            zone = "🔴"

        return (top_half, bottom_half, speed_str, percentage, zone)

    def _create_fuel_tank_1(self, total_cost: float, subscription_fee: float) -> str:
        """Create Fuel Tank 1: Total dollars (matches subscription fee)."""
        if subscription_fee == 0:
            return f"TANK 1: ${total_cost:>8.2f} SPENT (NO LIMIT SET)"

        percentage = min(100, (total_cost / subscription_fee * 100) if subscription_fee > 0 else 0)

        # Tank status
        if percentage < 25:
            status = "🟢 FULL"
        elif percentage < 50:
            status = "🟡 GOOD"
        elif percentage < 75:
            status = "🟠 LOW"
        elif percentage < 90:
            status = "🟠 VERY LOW"
        else:
            status = "🔴 CRITICAL"

        filled = int(percentage / 100 * 30)
        tank_bar = "█" * filled + "░" * (30 - filled)

        return f"TANK 1: [{tank_bar:30}] ${total_cost:>7.2f}/${subscription_fee:>7.2f} {status} ({percentage:>5.1f}%)"

    def _create_fuel_tank_2(self, current_burn: float, avg_burn: float) -> str:
        """Create Fuel Tank 2: Current burn vs average (talent metaphor)."""
        if avg_burn == 0:
            avg_burn = max(0.0001, current_burn)  # Avoid division by zero

        ratio = current_burn / avg_burn if avg_burn > 0 else 0.0

        # Talent burn metaphor: if using talent (current > avg), you're "burning fruit"
        if ratio < 0.5:
            status = "🟢 CONSERVING"
            metaphor = "Talent preserved"
        elif ratio < 1.0:
            status = "🟡 NORMAL"
            metaphor = "Steady use"
        elif ratio < 1.5:
            status = "🟠 BURNING"
            metaphor = "Using talent"
        elif ratio < 2.0:
            status = "🟠 HIGH BURN"
            metaphor = "Burning fruit"
        else:
            status = "🔴 INTENSE"
            metaphor = "Full burn"

        # Show ratio as percentage
        ratio_pct = ratio * 100

        # Create gauge (0-200% scale, 100% = average)
        gauge_pct = min(100, ratio_pct / 2.0)  # Scale to 0-100 for display
        filled = int(gauge_pct / 100 * 30)
        tank_bar = "█" * filled + "░" * (30 - filled)

        return f"TANK 2: [{tank_bar:30}] ${current_burn:>6.4f}/MIN vs ${avg_burn:>6.4f} AVG {status} ({ratio_pct:>5.1f}%)"

    def get_hud_display(self) -> str:
        """Get full HUD display."""
        data = self.monitor.get_gauge_display()
        if not data:
            return "HUD: No data available"

        gauges = data.get("gauges", {})
        lines = []

        # Header
        lines.append("╔" + "═" * 78 + "╗")
        lines.append("║" + " " * 20 + "JARVIS TOKEN USAGE HUD" + " " * 35 + "║")
        lines.append("╠" + "═" * 78 + "╣")

        # Get metrics (60min window)
        tpm_60 = gauges.get("tokens_per_minute", {}).get("60min", {})
        rpm_60 = gauges.get("requests_per_minute", {}).get("60min", {})
        cpm_60 = gauges.get("cost_per_minute", {}).get("60min", {})
        cpm_1 = gauges.get("cost_per_minute", {}).get("1min", {})
        local_usage = gauges.get("local_usage", {})
        cloud_usage = gauges.get("cloud_usage", {})
        sub = gauges.get("subscription", {})
        total_cost = gauges.get("total_cost", {})
        burn_rate = gauges.get("burn_rate", {})

        # Extract values
        if isinstance(tpm_60, dict):
            tokens_current = tpm_60.get("current", 0)
            tokens_min = tpm_60.get("min", 0)
            tokens_max = tpm_60.get("max", 1)
            tokens_avg = tpm_60.get("average", 0)
        else:
            tokens_current = tokens_min = tokens_max = tokens_avg = 0

        if isinstance(rpm_60, dict):
            rpm_current = rpm_60.get("current", 0)
            rpm_max = rpm_60.get("max", 100)
        else:
            rpm_current = rpm_max = 0

        if tokens_max == 0:
            tokens_max = max(1, tokens_current * 2)

        # Determine power source (local vs cloud)
        local_tokens = local_usage.get("tokens", {}).get("current", 0) if isinstance(local_usage.get("tokens"), dict) else 0
        cloud_tokens = cloud_usage.get("tokens", {}).get("current", 0) if isinstance(cloud_usage.get("tokens"), dict) else 0
        total_tokens = local_tokens + cloud_tokens

        is_local = local_tokens > cloud_tokens if total_tokens > 0 else True
        local_pct = (local_tokens / total_tokens * 100) if total_tokens > 0 else 0
        cloud_pct = (cloud_tokens / total_tokens * 100) if total_tokens > 0 else 0

        # POWER SOURCE (Gas/Electric)
        lines.append("║ " + self._create_power_source_indicator(is_local, local_pct, cloud_pct) + " " * 20 + "║")
        lines.append("║" + " " * 78 + "║")

        # FULL CIRCLE SPEEDOMETER (Current Actual Speed)
        if tokens_max == 0:
            tokens_max = max(10000, tokens_current * 2)
        top_half, bottom_half, speed_str, speed_pct, speed_zone = self._create_full_circle_speedometer(tokens_current, tokens_max)

        # Create speedometer display
        lines.append("║ " + f"SPEEDO: ╭{top_half:20}╮ {speed_zone} {speed_str:>8} TOK/MIN ({speed_pct:>5.1f}%)" + " " * 15 + "║")
        lines.append("║ " + f"        ╰{bottom_half:20}╯" + " " * 50 + "║")
        lines.append("║" + " " * 78 + "║")

        # SPEED (Tokens/Min = MPH/KPH) - Secondary display
        lines.append("║ " + self._create_speed_indicator(tokens_current, "TOK/MIN") + " " * 40 + "║")
        lines.append("║" + " " * 78 + "║")

        # RPM (Requests/Min)
        lines.append("║ " + self._create_rpm_gauge(rpm_current, max(100, rpm_max)) + " " * 30 + "║")
        lines.append("║" + " " * 78 + "║")

        # ACCELERATOR (Token usage rate)
        lines.append("║ " + self._create_accelerator_indicator(tokens_current, tokens_min, tokens_max) + " " * 20 + "║")
        lines.append("║" + " " * 78 + "║")

        # SUBSCRIPTION (Fuel gauge style)
        if sub:
            used = sub.get("asks_used", 0)
            remaining = sub.get("asks_remaining", 0)
            pct = sub.get("percentage_used", 0)
            max_asks = self.monitor.subscription_max_asks

            if max_asks > 0:
                # Fuel tank style
                if pct < 25:
                    tank_status = "🟢 FULL"
                elif pct < 50:
                    tank_status = "🟡 GOOD"
                elif pct < 75:
                    tank_status = "🟠 LOW"
                elif pct < 90:
                    tank_status = "🟠 VERY LOW"
                else:
                    tank_status = "🔴 CRITICAL"

                filled = int(pct / 100 * 30)
                fuel_bar = "█" * filled + "░" * (30 - filled)

                lines.append("║ " + f"FUEL: [{fuel_bar:30}] {used:>6,}/{max_asks:>6,} ASKS {tank_status} ({pct:.1f}%)" + " " * 15 + "║")
            else:
                lines.append("║ " + f"FUEL: UNLIMITED ({used:,} ASKS USED)" + " " * 45 + "║")

        lines.append("║" + " " * 78 + "║")

        # FUEL TANK 1: Total Dollars (Subscription Fee)
        if total_cost:
            total_usd = total_cost.get("total_usd", 0.0)
            sub_fee = total_cost.get("subscription_fee", 0.0)
            tank1_line = self._create_fuel_tank_1(total_usd, sub_fee)
            lines.append("║ " + tank1_line + " " * (78 - len(tank1_line) - 2) + "║")
            lines.append("║" + " " * 78 + "║")

        # FUEL TANK 2: Current Burn vs Average (Talent Metaphor - "If God gives talent, it burns fruit")
        if burn_rate:
            current_burn = burn_rate.get("current_per_min", 0.0)
            avg_burn = burn_rate.get("average_per_min", 0.0)
            if avg_burn == 0 and isinstance(cpm_60, dict):
                avg_burn = cpm_60.get("average", 0.0)
            if avg_burn == 0:
                avg_burn = 0.0001  # Avoid division by zero
            tank2_line = self._create_fuel_tank_2(current_burn, avg_burn)
            lines.append("║ " + tank2_line + " " * (78 - len(tank2_line) - 2) + "║")
            lines.append("║" + " " * 78 + "║")

        # COST METER (Legacy - kept for reference)
        if isinstance(cpm_60, dict):
            cost_current = cpm_60.get("current", 0)
            cost_max = cpm_60.get("max", 0.01)

            if cost_max == 0:
                cost_max = max(0.01, cost_current * 2)

            cost_pct = min(100, (cost_current / cost_max * 100) if cost_max > 0 else 0)
            filled = int(cost_pct / 100 * 30)
            cost_bar = "█" * filled + "░" * (30 - filled)

            lines.append("║ " + f"COST: [{cost_bar:30}] ${cost_current:>7.4f}/MIN (MAX: ${cost_max:.4f})" + " " * 20 + "║")

        # Footer
        lines.append("╚" + "═" * 78 + "╝")

        return "\n".join(lines)

    def get_compact_hud(self) -> str:
        """Get compact single-line HUD."""
        data = self.monitor.get_gauge_display()
        if not data:
            return "HUD: No data"

        gauges = data.get("gauges", {})

        # Get key metrics
        tpm_60 = gauges.get("tokens_per_minute", {}).get("60min", {})
        rpm_60 = gauges.get("requests_per_minute", {}).get("60min", {})
        local_usage = gauges.get("local_usage", {})
        cloud_usage = gauges.get("cloud_usage", {})

        tokens = tpm_60.get("current", 0) if isinstance(tpm_60, dict) else 0
        rpm = rpm_60.get("current", 0) if isinstance(rpm_60, dict) else 0

        local_tokens = local_usage.get("tokens", {}).get("current", 0) if isinstance(local_usage.get("tokens"), dict) else 0
        cloud_tokens = cloud_usage.get("tokens", {}).get("current", 0) if isinstance(cloud_usage.get("tokens"), dict) else 0

        is_local = local_tokens > cloud_tokens if (local_tokens + cloud_tokens) > 0 else True
        power = "⚡ LOCAL" if is_local else "⛽ CLOUD"

        # Format
        if tokens >= 1000:
            speed = f"{tokens/1000:.1f}K"
        else:
            speed = f"{int(tokens)}"

        return f"🚀 {power} | SPEED: {speed} TOK/MIN | RPM: {int(rpm)} | ACCEL: {min(100, int(tokens/50))}%"

    def print_hud(self):
        """Print full HUD display."""
        print("\n" + self.get_hud_display() + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Token Usage HUD Display (Iron Man Style)")
    parser.add_argument("--compact", action="store_true", help="Print compact single-line HUD")
    parser.add_argument("--full", action="store_true", help="Print full HUD display")

    args = parser.parse_args()

    hud = TokenHUDDisplay()

    if args.compact:
        print(hud.get_compact_hud())
    else:
        hud.print_hud()


if __name__ == "__main__":


    main()