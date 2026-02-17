#!/usr/bin/env python3
"""
Open Fidelity Trader Dashboard
Quick access script to open Fidelity's trader dashboard

Usage:
    python open_fidelity_dashboard.py

Tags: #FIDELITY #DASHBOARD #QUICK_ACCESS @JARVIS
"""

import sys
import webbrowser
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("OpenFidelityDashboard")

# Fidelity URLs
TRADER_DASHBOARD_URL = "https://digital.fidelity.com/ftgw/digital/trader-dashboard"
ACTIVE_TRADER_PRO_URL = "https://www.fidelity.com/trading/advanced-trading-tools/active-trader-pro/overview"
LOGIN_URL = "https://digital.fidelity.com/ftgw/digital/login"


def open_trader_dashboard():
    """Open Fidelity Trader Dashboard"""
    print("")
    print("=" * 70)
    print("💰 FIDELITY TRADER DASHBOARD")
    print("=" * 70)
    print("")
    print(f"Opening: {TRADER_DASHBOARD_URL}")
    print("")

    try:
        webbrowser.open(TRADER_DASHBOARD_URL)
        print("✅ Trader Dashboard opened in your default browser")
        print("")
        print("Available Fidelity Resources:")
        print(f"  • Trader Dashboard: {TRADER_DASHBOARD_URL}")
        print(f"  • Active Trader Pro: {ACTIVE_TRADER_PRO_URL}")
        print(f"  • Login: {LOGIN_URL}")
        print("")
        return True
    except Exception as e:
        print(f"❌ Failed to open dashboard: {e}")
        print("")
        print("Please open manually:")
        print(f"  {TRADER_DASHBOARD_URL}")
        return False


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Open Fidelity Trader Dashboard")
        parser.add_argument("--dashboard", action="store_true", default=True, help="Open trader dashboard (default)")
        parser.add_argument("--login", action="store_true", help="Open login page")
        parser.add_argument("--active-trader", action="store_true", help="Open Active Trader Pro page")

        args = parser.parse_args()

        if args.login:
            webbrowser.open(LOGIN_URL)
            print(f"✅ Opened Fidelity Login: {LOGIN_URL}")
        elif args.active_trader:
            webbrowser.open(ACTIVE_TRADER_PRO_URL)
            print(f"✅ Opened Active Trader Pro page: {ACTIVE_TRADER_PRO_URL}")
        else:
            open_trader_dashboard()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()