#!/usr/bin/env python3
"""
Verify Portfolio Data - Real vs Placeholder Values

Checks if portfolio values are real market data or test placeholders.
Validates data integrity and provides recommendations for production use.
"""

import sys
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ai_investment_portfolio import AIInvestmentPortfolio, InvestmentDomain
    from ai_liquidity_pool import AILiquidityManager
except ImportError:
    print("❌ Portfolio modules not available")
    sys.exit(1)


def analyze_portfolio_data():
    """Analyze whether portfolio data is real or placeholder"""

    print("🔍 PORTFOLIO DATA ANALYSIS - REAL VS PLACEHOLDER")
    print("="*60)

    # Initialize portfolio
    portfolio = AIInvestmentPortfolio()

    print("📊 CURRENT PORTFOLIO COMPOSITION:")
    print("-" * 40)

    total_positions = len(portfolio.positions)
    total_value = portfolio.total_value
    total_cash = portfolio.cash_position

    print(f"Total Positions: {total_positions}")
    print(f"Total Portfolio Value: ${total_value:,.2f}")
    print(f"Cash Position: ${total_cash:,.2f}")
    print(f"Active Strategies: {len(portfolio.strategies)}")
    print()

    # Analyze individual positions
    print("🎯 POSITION ANALYSIS:")
    print("-" * 40)

    placeholder_indicators = []
    real_data_indicators = []

    for position_id, position in portfolio.positions.items():
        print(f"\n📈 Position: {position.name}")
        print(f"   Asset Class: {position.asset_class}")
        print(f"   Domain: {position.domain}")
        print(f"   Quantity: {position.quantity:,.0f}")
        print(f"   Entry Price: ${position.entry_price:.4f}")
        print(f"   Current Price: ${position.current_price:.4f}")
        print(f"   Market Value: ${position.market_value:,.2f}")
        print(f"   Unrealized P&L: ${position.unrealized_pnl:,.2f}")
        print(f"   Risk Profile: {position.risk_profile}")
        print(f"   Expected Return: {position.expected_return:.1%}")
        print(f"   Volatility: {position.volatility:.1%}")
        print(f"   Sharpe Ratio: {position.sharpe_ratio:.2f}")

        # Check for placeholder indicators
        if position.quantity in [50000, 22000, 1000000, 500000]:  # Round placeholder numbers
            placeholder_indicators.append(f"Round quantity: {position.quantity:,}")

        if position.entry_price in [0.0004, 20000, 50000]:  # Specific placeholder prices
            placeholder_indicators.append(f"Specific entry price: ${position.entry_price}")

        if position.metadata.get('level') in [5, 25, 60]:  # MMO level placeholders
            placeholder_indicators.append(f"MMO level {position.metadata['level']}")

        if "experience_earned" in position.metadata:
            real_data_indicators.append("Experience tracking metadata")

    print("\n🔍 DATA ANALYSIS RESULTS:")
    print("-" * 40)

    if placeholder_indicators:
        print("⚠️  PLACEHOLDER DATA DETECTED:")
        for indicator in placeholder_indicators[:5]:  # Show first 5
            print(f"   • {indicator}")
        if len(placeholder_indicators) > 5:
            print(f"   ... and {len(placeholder_indicators) - 5} more")
    else:
        print("✅ No obvious placeholder patterns detected")

    if real_data_indicators:
        print("\n✅ REAL DATA ELEMENTS:")
        for indicator in real_data_indicators:
            print(f"   • {indicator}")

    print("\n📋 RECOMMENDATIONS:")
    print("-" * 40)

    if placeholder_indicators:
        print("• 🔄 Replace placeholder quantities with real market data")
        print("• 💰 Update prices to reflect current market rates")
        print("• 📊 Implement real-time price feeds for live data")
        print("• 🎮 Remove MMO-specific metadata for production use")
        print("• 🔗 Connect to real API endpoints for live pricing")

    if not placeholder_indicators:
        print("• ✅ Portfolio data appears to be production-ready")
        print("• 📈 Consider implementing real-time price updates")
        print("• 🔄 Add automated rebalancing triggers")

    print("\n🎯 PRODUCTION READINESS:")
    print("-" * 40)

    readiness_score = 0
    if total_positions > 0:
        readiness_score += 25
    if total_value > 1000:
        readiness_score += 25
    if len(portfolio.strategies) > 0:
        readiness_score += 25
    if not placeholder_indicators:
        readiness_score += 25

    print(f"Production Readiness Score: {readiness_score}%")

    if readiness_score >= 75:
        print("✅ READY FOR PRODUCTION")
        print("   Portfolio structure is sound, data can be made live")
    elif readiness_score >= 50:
        print("⚠️  NEEDS DATA INTEGRATION")
        print("   Structure is good, but needs real market data")
    else:
        print("🔄 STILL IN DEVELOPMENT")
        print("   Core architecture needs completion")

    print("\n💡 NEXT STEPS:")
    print("-" * 40)

    if placeholder_indicators:
        print("1. 🔗 Integrate real market data feeds")
        print("2. 💰 Implement live pricing APIs")
        print("3. 📊 Add real-time performance tracking")
        print("4. 🎮 Separate MMO mechanics from financial logic")
        print("5. ✅ Run comprehensive testing with real data")

    print("6. 🚀 Launch with confidence monitoring")
    print("7. 📈 Implement automated rebalancing")
    print("8. 🎯 Set up risk management alerts")

    return {
        "total_positions": total_positions,
        "total_value": total_value,
        "placeholder_indicators": len(placeholder_indicators),
        "real_indicators": len(real_data_indicators),
        "readiness_score": readiness_score
    }


def show_data_sources():
    """Show recommended data sources for production use"""

    print("\n📊 RECOMMENDED DATA SOURCES FOR PRODUCTION:")
    print("="*60)

    sources = {
        "🏦 Financial Markets": [
            "Alpha Vantage API (free tier available)",
            "Yahoo Finance API",
            "Financial Modeling Prep",
            "CoinMarketCap for crypto assets"
        ],
        "🤖 AI Token Markets": [
            "GitHub Models API pricing",
            "OpenAI API usage tracking",
            "Anthropic pricing endpoints",
            "Internal token consumption logs"
        ],
        "💰 Portfolio Analytics": [
            "Real-time P&L calculations",
            "Risk metrics (VaR, Sharpe ratio)",
            "Performance attribution",
            "Benchmark comparisons"
        ],
        "📈 Live Data Feeds": [
            "WebSocket connections for real-time prices",
            "REST APIs for periodic updates",
            "Blockchain data for crypto positions",
            "Market data aggregators"
        ]
    }

    for category, source_list in sources.items():
        print(f"\n{category}:")
        for source in source_list:
            print(f"   • {source}")

    print("\n🔧 IMPLEMENTATION PRIORITY:")
    print("1. Basic price feeds (Yahoo Finance, CoinMarketCap)")
    print("2. AI provider APIs (GitHub, OpenAI, Anthropic)")
    print("3. Real-time WebSocket connections")
    print("4. Advanced analytics and risk metrics")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verify Portfolio Data Integrity")
    parser.add_argument("--analyze", action="store_true", help="Analyze portfolio data")
    parser.add_argument("--sources", action="store_true", help="Show data source recommendations")

    args = parser.parse_args()

    if args.analyze:
        analyze_portfolio_data()
    elif args.sources:
        show_data_sources()
    else:
        # Run both by default
        results = analyze_portfolio_data()
        show_data_sources()

        print("\n🎯 SUMMARY:")
        print(f"   Positions: {results['total_positions']}")
        print(f"   Value: ${results['total_value']:,.2f}")
        print(f"   Readiness: {results['readiness_score']}%")
        print(f"   Placeholder Issues: {results['placeholder_indicators']}")
        print(f"   Status: {'READY' if results['readiness_score'] >= 75 else 'NEEDS WORK'}")