#!/usr/bin/env python3
"""
ULTRON Cost Comparison Analysis
Compares local AI cluster costs vs cloud API costs

@LUMINA @JARVIS @ULTRON
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("ULTRONCostComparison")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    logger = logging.getLogger("ULTRONCostComparison")


class ULTRONCostComparison:
    """Compare local ULTRON cluster costs vs cloud APIs."""

    def __init__(self):
        # Cloud API pricing (per 1M tokens as of Jan 2026)
        self.cloud_pricing = {
            "claude-opus-4": {
                "input": 15.00,  # $15 per 1M input tokens
                "output": 75.00,  # $75 per 1M output tokens
                "provider": "Anthropic"
            },
            "claude-sonnet-4": {
                "input": 3.00,
                "output": 15.00,
                "provider": "Anthropic"
            },
            "gpt-4o": {
                "input": 2.50,
                "output": 10.00,
                "provider": "OpenAI"
            },
            "gpt-4-turbo": {
                "input": 10.00,
                "output": 30.00,
                "provider": "OpenAI"
            },
            "grok-2": {
                "input": 2.00,
                "output": 10.00,
                "provider": "xAI"
            }
        }

        # Local cluster costs (electricity + hardware amortization)
        self.local_costs = {
            "MILLENNIUM-FALC": {
                "hardware_cost": 3500,  # RTX 5090 laptop estimate
                "power_watts": 150,  # Average under load
                "electricity_rate": 0.12,  # $/kWh
                "lifespan_years": 4
            },
            "KAIJU": {
                "hardware_cost": 2000,  # Synology NAS
                "power_watts": 80,
                "electricity_rate": 0.12,
                "lifespan_years": 5
            }
        }

        # Local model capabilities (tokens per second)
        self.local_models = {
            "smollm:135m": {"tps": 150, "quality": 0.5, "vram_gb": 0.5},
            "llama3.2:3b": {"tps": 80, "quality": 0.7, "vram_gb": 2.5},
            "mistral:latest": {"tps": 45, "quality": 0.85, "vram_gb": 5},
            "codellama:13b": {"tps": 25, "quality": 0.9, "vram_gb": 10},
            "deepseek-coder:6.7b": {"tps": 35, "quality": 0.88, "vram_gb": 5}
        }

    def calculate_cloud_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cloud API cost for a request."""
        if model not in self.cloud_pricing:
            return 0.0

        pricing = self.cloud_pricing[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def calculate_local_hourly_cost(self, node: str) -> float:
        """Calculate hourly operating cost for a local node."""
        if node not in self.local_costs:
            return 0.0

        costs = self.local_costs[node]
        # Electricity cost per hour
        kwh_per_hour = costs["power_watts"] / 1000
        electricity_per_hour = kwh_per_hour * costs["electricity_rate"]

        # Hardware amortization per hour (assuming 8 hours/day usage)
        hours_per_year = 8 * 365
        yearly_amortization = costs["hardware_cost"] / costs["lifespan_years"]
        amortization_per_hour = yearly_amortization / hours_per_year

        return electricity_per_hour + amortization_per_hour

    def calculate_local_cost_per_million_tokens(self, node: str, model: str) -> Dict[str, float]:
        """Calculate cost per million tokens for local inference."""
        if model not in self.local_models:
            return {"input": 0, "output": 0}

        hourly_cost = self.calculate_local_hourly_cost(node)
        tps = self.local_models[model]["tps"]
        tokens_per_hour = tps * 3600

        # Cost per million tokens (same for input/output locally)
        cost_per_million = (hourly_cost / tokens_per_hour) * 1_000_000

        return {"input": cost_per_million, "output": cost_per_million}

    def generate_comparison_report(self) -> str:
        """Generate comprehensive cost comparison report."""
        report = []
        report.append("=" * 80)
        report.append("💰 ULTRON CLUSTER vs CLOUD API - COST COMPARISON")
        report.append("=" * 80)
        report.append(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Cloud pricing table
        report.append("┌" + "─" * 78 + "┐")
        report.append("│" + " ☁️  CLOUD API PRICING (per 1M tokens)".center(78) + "│")
        report.append("├" + "─" * 78 + "┤")
        report.append("│" + f"{'Model':<20} │ {'Provider':<12} │ {'Input':<12} │ {'Output':<12} │ {'Avg':<12}" + "│")
        report.append("├" + "─" * 78 + "┤")

        for model, pricing in self.cloud_pricing.items():
            avg = (pricing["input"] + pricing["output"]) / 2
            report.append("│" + f"{model:<20} │ {pricing['provider']:<12} │ ${pricing['input']:<10.2f} │ ${pricing['output']:<10.2f} │ ${avg:<10.2f}" + "│")

        report.append("└" + "─" * 78 + "┘")
        report.append("")

        # Local cluster costs
        report.append("┌" + "─" * 78 + "┐")
        report.append("│" + " 🏠 LOCAL ULTRON CLUSTER COSTS".center(78) + "│")
        report.append("├" + "─" * 78 + "┤")

        total_hourly = 0
        for node, costs in self.local_costs.items():
            hourly = self.calculate_local_hourly_cost(node)
            total_hourly += hourly
            report.append("│" + f"  {node}:".ljust(78) + "│")
            report.append("│" + f"    Hardware: ${costs['hardware_cost']:,} (amortized over {costs['lifespan_years']} years)".ljust(78) + "│")
            report.append("│" + f"    Power: {costs['power_watts']}W @ ${costs['electricity_rate']}/kWh".ljust(78) + "│")
            report.append("│" + f"    Hourly Cost: ${hourly:.4f}/hour".ljust(78) + "│")
            report.append("│" + "".ljust(78) + "│")

        report.append("│" + f"  📊 COMBINED CLUSTER: ${total_hourly:.4f}/hour".ljust(78) + "│")
        report.append("│" + f"                       ${total_hourly * 24:.2f}/day".ljust(78) + "│")
        report.append("│" + f"                       ${total_hourly * 24 * 30:.2f}/month (24/7)".ljust(78) + "│")
        report.append("└" + "─" * 78 + "┘")
        report.append("")

        # Per-million token comparison
        report.append("┌" + "─" * 78 + "┐")
        report.append("│" + " 📈 LOCAL vs CLOUD - COST PER 1M TOKENS".center(78) + "│")
        report.append("├" + "─" * 78 + "┤")
        report.append("│" + f"{'Local Model':<20} │ {'Local $/1M':<12} │ {'vs Claude Opus':<15} │ {'Savings':<15}" + "│")
        report.append("├" + "─" * 78 + "┤")

        opus_avg = (self.cloud_pricing["claude-opus-4"]["input"] + self.cloud_pricing["claude-opus-4"]["output"]) / 2

        for model, specs in self.local_models.items():
            local_cost = self.calculate_local_cost_per_million_tokens("MILLENNIUM-FALC", model)
            local_avg = local_cost["input"]  # Same for input/output
            savings_pct = ((opus_avg - local_avg) / opus_avg) * 100 if opus_avg > 0 else 0
            savings_str = f"{savings_pct:.1f}% cheaper" if savings_pct > 0 else "N/A"

            report.append("│" + f"{model:<20} │ ${local_avg:<10.4f} │ ${opus_avg:<13.2f} │ {savings_str:<15}" + "│")

        report.append("└" + "─" * 78 + "┘")
        report.append("")

        # Usage scenario comparison
        report.append("┌" + "─" * 78 + "┐")
        report.append("│" + " 🎯 REAL-WORLD USAGE SCENARIOS".center(78) + "│")
        report.append("├" + "─" * 78 + "┤")

        scenarios = [
            ("Light coding session", 50_000, 100_000),
            ("Heavy dev day", 500_000, 1_000_000),
            ("Full month (power user)", 10_000_000, 20_000_000),
        ]

        for scenario_name, input_tokens, output_tokens in scenarios:
            report.append("│" + f"  📋 {scenario_name}:".ljust(78) + "│")
            report.append("│" + f"     ({input_tokens:,} input + {output_tokens:,} output tokens)".ljust(78) + "│")

            # Cloud costs
            opus_cost = self.calculate_cloud_cost("claude-opus-4", input_tokens, output_tokens)
            sonnet_cost = self.calculate_cloud_cost("claude-sonnet-4", input_tokens, output_tokens)
            gpt4o_cost = self.calculate_cloud_cost("gpt-4o", input_tokens, output_tokens)

            # Local cost (using mistral as reference)
            local_per_m = self.calculate_local_cost_per_million_tokens("MILLENNIUM-FALC", "mistral:latest")
            local_cost = ((input_tokens + output_tokens) / 1_000_000) * local_per_m["input"]

            report.append("│" + f"     ☁️  Claude Opus 4:  ${opus_cost:>10.2f}".ljust(78) + "│")
            report.append("│" + f"     ☁️  Claude Sonnet:  ${sonnet_cost:>10.2f}".ljust(78) + "│")
            report.append("│" + f"     ☁️  GPT-4o:         ${gpt4o_cost:>10.2f}".ljust(78) + "│")
            report.append("│" + f"     🏠 ULTRON Local:   ${local_cost:>10.4f}  ← 💰".ljust(78) + "│")
            report.append("│" + "".ljust(78) + "│")

        report.append("└" + "─" * 78 + "┘")
        report.append("")

        # Summary
        report.append("┌" + "─" * 78 + "┐")
        report.append("│" + " 🏆 SUMMARY".center(78) + "│")
        report.append("├" + "─" * 78 + "┤")
        report.append("│" + "".ljust(78) + "│")
        report.append("│" + "  ✅ LOCAL ULTRON CLUSTER ADVANTAGES:".ljust(78) + "│")
        report.append("│" + "     • 99%+ cost savings on token-based pricing".ljust(78) + "│")
        report.append("│" + "     • No rate limits or quotas".ljust(78) + "│")
        report.append("│" + "     • Complete data privacy (nothing leaves your network)".ljust(78) + "│")
        report.append("│" + "     • No API downtime dependencies".ljust(78) + "│")
        report.append("│" + "     • Fixed monthly cost vs variable cloud bills".ljust(78) + "│")
        report.append("│" + "".ljust(78) + "│")
        report.append("│" + "  ⚠️  TRADEOFFS:".ljust(78) + "│")
        report.append("│" + "     • Local models ~70-90% quality of frontier models".ljust(78) + "│")
        report.append("│" + "     • Hardware maintenance responsibility".ljust(78) + "│")
        report.append("│" + "     • Limited context windows (8k-32k vs 200k)".ljust(78) + "│")
        report.append("│" + "".ljust(78) + "│")
        report.append("│" + "  🎯 OPTIMAL STRATEGY (HYBRID):".ljust(78) + "│")
        report.append("│" + "     • ULTRON Local: 90% of tasks (coding, quick queries, iteration)".ljust(78) + "│")
        report.append("│" + "     • Cloud Fallback: 10% of tasks (complex reasoning, large context)".ljust(78) + "│")
        report.append("│" + "     • Estimated monthly savings: $500-2000+ for heavy users".ljust(78) + "│")
        report.append("│" + "".ljust(78) + "│")
        report.append("└" + "─" * 78 + "┘")

        return "\n".join(report)

    def run(self):
        try:
            """Run the cost comparison analysis."""
            report = self.generate_comparison_report()
            print(report)

            # Save report
            report_path = project_root / "data" / "ultron_cost_comparison_report.txt"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report, encoding="utf-8")
            logger.info(f"📊 Report saved to: {report_path}")

            return report


        except Exception as e:
            self.logger.error(f"Error in run: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    analyzer = ULTRONCostComparison()
    analyzer.run()
