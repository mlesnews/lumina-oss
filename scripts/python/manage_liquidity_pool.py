#!/usr/bin/env python3
"""
AI Liquidity Pool Management CLI

Comprehensive command-line interface for managing the AI liquidity pool.
Financial-grade token management with arbitrage, rebalancing, and optimization.

Usage:
    python manage_liquidity_pool.py status                    # Show pool status
    python manage_liquidity_pool.py optimize                  # Run optimization
    python manage_liquidity_pool.py add-tokens github 10000   # Add tokens to provider
    python manage_liquidity_pool.py route-test                # Test routing decision
    python manage_liquidity_pool.py dashboard                 # Open dashboard

Tags: #LIQUIDITY #MANAGEMENT #CLI #FINANCIAL #AI_TOKENS @LUMINA
"""

import sys
import json
import webbrowser
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ai_liquidity_pool import AILiquidityManager
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    AILiquidityManager = None

logger = get_logger("LiquidityCLI")


class LiquidityCLIManager:
    """Command-line interface for AI liquidity pool management"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize CLI manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.liquidity_manager = None

        if AILiquidityManager:
            try:
                self.liquidity_manager = AILiquidityManager(project_root=project_root)
                logger.info("✅ Liquidity CLI Manager initialized")
            except Exception as e:
                logger.error(f"Failed to initialize liquidity manager: {e}")
        else:
            logger.error("AILiquidityManager not available")

    def show_status(self):
        """Display comprehensive liquidity pool status"""
        if not self.liquidity_manager:
            print("❌ Liquidity manager not available")
            return

        status = self.liquidity_manager.get_liquidity_status()

        print("🤖 AI LIQUIDITY POOL STATUS")
        print("="*60)
        print(f"Pool ID: {status['pool_id']}")
        print(f"Total Liquidity Units: {status['total_liquidity_units']:,.0f}")
        print(f"Total USD Value: ${status['total_usd_value']:,.2f}")
        print(f"Active Providers: {status['provider_count']}")
        print(f"Last Rebalance: {status['last_rebalance'][:19]}")
        print(f"Total Transactions: {status['transaction_count']}")
        print()

        print("PROVIDER ALLOCATIONS")
        print("-"*60)
        for pid, provider in status['providers'].items():
            print(f"📊 {provider['name']} ({provider['tier'].upper()})")
            print(f"   Tokens: {provider['token_balance']:,.0f}")
            print(f"   Liquidity Units: {provider['liquidity_units']:,.0f}")
            print(f"   Allocation: {provider['allocation_percent']:.1f}%")
            print(f"   USD Value: ${provider['usd_value']:,.2f}")
            print(f"   Liquidity Score: {provider['liquidity_score']:.3f}")
            print(f"   Utilization: {provider['utilization_percent']:.1f}%")
            print()

        print("RECENT TRANSACTIONS")
        print("-"*60)
        if status['recent_transactions']:
            for txn in status['recent_transactions'][:5]:
                timestamp = txn['timestamp'][:19]
                amount = f"{txn['amount']:,.0f}"
                usd_value = f"${txn['usd_value']:.2f}"
                print(f"💰 {timestamp} | {txn['type'].upper()} | {txn['from']} → {txn['to']} | {amount} tokens | {usd_value}")
        else:
            print("No recent transactions")
        print()

    def optimize_pool(self):
        """Run liquidity optimization (arbitrage + rebalancing)"""
        if not self.liquidity_manager:
            print("❌ Liquidity manager not available")
            return

        print("🚀 OPTIMIZING LIQUIDITY POOL...")
        print("Running arbitrage and rebalancing algorithms...")

        try:
            results = self.liquidity_manager.optimize_liquidity()

            print("✅ OPTIMIZATION COMPLETE")
            print(f"Arbitrage Transactions: {results['arbitrage_transactions']}")
            print(f"Rebalancing Transactions: {results['rebalancing_transactions']}")
            print(f"Total Improvement: {results['total_improvement']:.0f} liquidity units")
            print(f"Timestamp: {results['timestamp'][:19]}")

        except Exception as e:
            print(f"❌ Optimization failed: {e}")

    def add_tokens(self, provider_id: str, amount: float):
        """Add tokens to a provider"""
        if not self.liquidity_manager:
            print("❌ Liquidity manager not available")
            return

        try:
            self.liquidity_manager.add_provider_tokens(provider_id, amount)
            print(f"✅ Added {amount:,.0f} tokens to {provider_id}")
        except Exception as e:
            print(f"❌ Failed to add tokens: {e}")

    def test_routing(self):
        """Test liquidity-based routing decision"""
        if not self.liquidity_manager:
            print("❌ Liquidity manager not available")
            return

        print("🎯 TESTING LIQUIDITY ROUTING")
        print("-"*40)

        # Test different scenarios
        test_scenarios = [
            {"complexity": 0.2, "tier": "economy", "description": "Simple task, cost-conscious"},
            {"complexity": 0.5, "tier": "standard", "description": "Balanced task"},
            {"complexity": 0.8, "tier": "premium", "description": "Complex task, best quality"},
            {"complexity": 0.5, "tier": None, "description": "Auto-routing"},
        ]

        for scenario in test_scenarios:
            print(f"\n{scenario['description']}:")
            print(f"  Complexity: {scenario['complexity']}, Tier: {scenario['tier'] or 'auto'}")

            result = self.liquidity_manager.route_ai_request(
                model_complexity=scenario['complexity'],
                preferred_tier=scenario['tier'],
                max_cost_per_token=0.01
            )

            if result:
                print(f"  ✅ Route: {result['provider_name']}")
                print(f"  Confidence: {(result['confidence_score'] * 100):.1f}%")
                print(f"  Cost: ${result['estimated_cost_usd']} per 1K tokens")
                print(f"  Reason: {result['routing_reason']}")
            else:
                print("  ❌ No suitable provider found")

    def open_dashboard(self):
        """Open the liquidity dashboard in browser"""
        dashboard_url = "http://<NAS_IP>:8080/liquidity-dashboard"
        print(f"🌐 Opening liquidity dashboard: {dashboard_url}")

        try:
            webbrowser.open(dashboard_url)
            print("✅ Dashboard opened in browser")
        except Exception as e:
            print(f"❌ Failed to open dashboard: {e}")
            print(f"   You can manually visit: {dashboard_url}")

    def show_help(self):
        """Show help information"""
        print("🤖 AI Liquidity Pool Management CLI")
        print("="*50)
        print()
        print("COMMANDS:")
        print("  status                    Show comprehensive pool status")
        print("  optimize                  Run arbitrage and rebalancing")
        print("  add-tokens <provider> <amount>  Add tokens to provider")
        print("  route-test                Test routing decisions")
        print("  dashboard                 Open liquidity dashboard")
        print("  help                      Show this help")
        print()
        print("EXAMPLES:")
        print("  python manage_liquidity_pool.py status")
        print("  python manage_liquidity_pool.py optimize")
        print("  python manage_liquidity_pool.py add-tokens github 50000")
        print("  python manage_liquidity_pool.py route-test")
        print("  python manage_liquidity_pool.py dashboard")
        print()
        print("PROVIDERS:")
        print("  github    - GitHub Models ($20 subscription)")
        print("  ultron    - Local ULTRON cluster (free)")
        print("  kaiju     - KAIJU Iron Legion NAS (free)")
        print()


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Liquidity Pool Management CLI")
    parser.add_argument("command", choices=[
        "status", "optimize", "add-tokens", "route-test", "dashboard", "help"
    ], help="Command to execute")

    parser.add_argument("args", nargs="*", help="Command arguments")

    args = parser.parse_args()

    manager = LiquidityCLIManager()

    if args.command == "help":
        manager.show_help()

    elif args.command == "status":
        manager.show_status()

    elif args.command == "optimize":
        manager.optimize_pool()

    elif args.command == "add-tokens":
        if len(args.args) != 2:
            print("❌ Usage: add-tokens <provider> <amount>")
            return
        provider_id, amount_str = args.args
        try:
            amount = float(amount_str)
            manager.add_tokens(provider_id, amount)
        except ValueError:
            print("❌ Amount must be a number")

    elif args.command == "route-test":
        manager.test_routing()

    elif args.command == "dashboard":
        manager.open_dashboard()

    else:
        manager.show_help()


if __name__ == "__main__":
    main()