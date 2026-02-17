#!/usr/bin/env python3
"""
AI Investment Portfolio Framework - Hedge Fund Approach to AI Technology

Applies investment banking and hedge fund principles to AI technology management.
Treats AI systems, models, tokens, and capabilities as financial assets in a portfolio.

Investment Domains:
1. 🏦 CAPITAL MARKETS: AI Token Pools & Liquidity Management
2. 🏛️ INVESTMENT BANKING: AI Technology Portfolio & Risk Management
3. 🏢 OPERATIONAL HEDGE FUND: AI Business Operations & Strategy

Tags: #AI_PORTFOLIO #HEDGE_FUND #INVESTMENT_BANKING #FINANCIAL_LOGIC #RISK_MANAGEMENT
"""

import sys
import json
import time
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

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

logger = get_logger("AIInvestmentPortfolio")


class InvestmentDomain(Enum):
    """Four domains of AI investment portfolio - MMO-style progression"""
    CAPITAL_MARKETS = "capital_markets"      # Token pools, liquidity, arbitrage (Level 1-10)
    INVESTMENT_BANKING = "investment_banking"  # Technology portfolio, risk management (Level 10-30)
    OPERATIONAL_HEDGE = "operational_hedge"   # Business operations, strategy (Level 30-50)
    HUMAN_COACHING = "human_coaching"         # Life coaching, mentorship, confidence building (Level 50+)


class AssetClass(Enum):
    """AI Asset Classes like Financial Instruments - MMO Equipment/Skills"""
    TOKEN_POOL = "token_pool"              # Liquid token reserves (Gold)
    AI_MODEL = "ai_model"                   # ML models as assets (Weapons)
    COMPUTE_RESOURCE = "compute_resource"  # GPU/CPU as infrastructure (Armor)
    DATA_ASSET = "data_asset"               # Training data as commodity (Consumables)
    API_ACCESS = "api_access"               # Provider contracts as securities (Mounts)
    INTELLECTUAL_PROPERTY = "intellectual_property"  # Code/models as IP (Legendary Items)
    MARKET_INTELLIGENCE = "market_intelligence"     # Competitive intelligence (Maps/Quests)
    HUMAN_CONNECTION = "human_connection"           # Life coaching relationships (Guild/Party)
    CONFIDENCE_BUILDING = "confidence_building"     # Success experiences (Achievement Points)
    RISK_CALCULATION = "risk_calculation"           # Decision-making skills (Professions)


class RiskProfile(Enum):
    """Risk profiles like investment strategies"""
    CONSERVATIVE = "conservative"          # Stable, low-risk AI operations
    BALANCED = "balanced"                  # Mixed risk/reward approach
    AGGRESSIVE = "aggressive"              # High-risk, high-reward strategies
    HEDGE = "hedge"                        # Risk-mitigating positions
    SPECULATIVE = "speculative"            # High-volatility opportunities


@dataclass
class PortfolioPosition:
    """Individual position in AI investment portfolio"""
    position_id: str
    asset_class: str
    domain: str
    name: str
    quantity: float
    entry_price: float
    current_price: float
    risk_profile: str
    expected_return: float  # Annualized expected return %
    volatility: float       # Annualized volatility %
    entry_date: datetime
    market_value: float = field(init=False)
    unrealized_pnl: float = field(init=False)
    sharpe_ratio: float = field(init=False)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.market_value = self.quantity * self.current_price
        self.unrealized_pnl = self.market_value - (self.quantity * self.entry_price)
        self.sharpe_ratio = self.expected_return / self.volatility if self.volatility > 0 else 0


@dataclass
class PortfolioStrategy:
    """Investment strategy configuration"""
    strategy_id: str
    name: str
    domain: str
    risk_profile: str
    target_allocation: float  # Target % of total portfolio
    expected_return: float
    max_volatility: float
    current_allocation: float = 0.0
    rebalancing_threshold: float = 0.05  # 5% deviation triggers rebalance
    positions: List[str] = field(default_factory=list)  # Position IDs
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskMetrics:
    """Risk management metrics like investment banking"""
    var_95: float = 0.0  # Value at Risk 95%
    expected_shortfall: float = 0.0
    max_drawdown: float = 0.0
    beta_to_market: float = 1.0  # Beta relative to AI market
    correlation_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    stress_test_results: Dict[str, Any] = field(default_factory=dict)
    liquidity_risk: float = 0.0
    concentration_risk: Dict[str, float] = field(default_factory=dict)


@dataclass
class AIInvestmentPortfolio:
    """Complete AI Investment Portfolio - Hedge Fund for AI Technology"""

    portfolio_id: str = "lumina_ai_investment_portfolio"
    portfolio_name: str = "LUMINA AI Technology Hedge Fund"
    inception_date: datetime = field(default_factory=datetime.now)
    total_value: float = 0.0
    cash_position: float = 100000.0  # Starting capital
    positions: Dict[str, PortfolioPosition] = field(default_factory=dict)
    strategies: Dict[str, PortfolioStrategy] = field(default_factory=dict)
    domains: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    risk_metrics: RiskMetrics = field(default_factory=lambda: RiskMetrics())
    transaction_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        self._initialize_domains()
        self._initialize_strategies()
        self._initialize_mmo_progression()
        self._calculate_total_value()

    def _initialize_domains(self):
        """Initialize the three AI investment domains"""

        # Domain 1: Capital Markets - Token Pools & Liquidity
        self.domains[InvestmentDomain.CAPITAL_MARKETS.value] = {
            "name": "AI Capital Markets",
            "description": "Token pools, liquidity management, arbitrage",
            "asset_classes": [AssetClass.TOKEN_POOL.value, AssetClass.API_ACCESS.value],
            "risk_characteristics": {
                "volatility": 0.15,  # 15% annualized volatility
                "liquidity": 0.9,    # 90% liquid
                "correlation_to_ai_market": 0.7
            },
            "strategies": ["liquidity_arbitrage", "token_pool_optimization"],
            "benchmark": "AI Token Market Index"
        }

        # Domain 2: Investment Banking - Technology Portfolio & Risk
        self.domains[InvestmentDomain.INVESTMENT_BANKING.value] = {
            "name": "AI Investment Banking",
            "description": "Technology portfolio management, risk analysis",
            "asset_classes": [AssetClass.AI_MODEL.value, AssetClass.COMPUTE_RESOURCE.value,
                            AssetClass.INTELLECTUAL_PROPERTY.value],
            "risk_characteristics": {
                "volatility": 0.25,  # 25% annualized volatility
                "liquidity": 0.6,    # 60% liquid
                "correlation_to_ai_market": 0.85
            },
            "strategies": ["model_portfolio_optimization", "compute_resource_hedging"],
            "benchmark": "AI Technology Innovation Index"
        }

        # Domain 3: Operational Hedge Fund - Business Operations
        self.domains[InvestmentDomain.OPERATIONAL_HEDGE.value] = {
            "name": "AI Operational Hedge Fund",
            "description": "Business operations, strategic positioning",
            "asset_classes": [AssetClass.DATA_ASSET.value, AssetClass.MARKET_INTELLIGENCE.value],
            "risk_characteristics": {
                "volatility": 0.35,  # 35% annualized volatility
                "liquidity": 0.4,    # 40% liquid
                "correlation_to_ai_market": 0.6
            },
            "strategies": ["market_intelligence_arbitrage", "operational_efficiency_hedge"],
            "benchmark": "AI Business Performance Index",
            "mmo_progression": "Level 30-50: Group Challenges → Raiding"
        }

        # Domain 4: Human Coaching - Life Mentoring & Confidence Building
        self.domains[InvestmentDomain.HUMAN_COACHING.value] = {
            "name": "AI Life Coaching & Mentorship",
            "description": "Human connection, life guidance, confidence building, proactive mindset",
            "asset_classes": [AssetClass.HUMAN_CONNECTION.value, AssetClass.CONFIDENCE_BUILDING.value,
                            AssetClass.RISK_CALCULATION.value],
            "risk_characteristics": {
                "volatility": 0.45,  # 45% annualized volatility (human emotions/stakes)
                "liquidity": 0.2,    # 20% liquid (relationships are illiquid)
                "correlation_to_ai_market": 0.3  # Low correlation to tech markets
            },
            "strategies": ["relationship_capital_arbitrage", "confidence_compounding", "proactive_risk_optimization"],
            "benchmark": "Human Flourishing & Success Index",
            "mmo_progression": "Level 50+: Endgame Raiding → Legendary Status"
        }

    def _initialize_strategies(self):
        """Initialize investment strategies for each domain"""

        # Capital Markets Strategies
        self.strategies["liquidity_arbitrage"] = PortfolioStrategy(
            strategy_id="liquidity_arbitrage",
            name="AI Liquidity Arbitrage",
            domain=InvestmentDomain.CAPITAL_MARKETS.value,
            risk_profile=RiskProfile.BALANCED.value,
            target_allocation=0.4,  # 40% of capital markets domain
            expected_return=0.15,  # 15% expected return
            max_volatility=0.20
        )

        self.strategies["token_pool_optimization"] = PortfolioStrategy(
            strategy_id="token_pool_optimization",
            name="Token Pool Optimization",
            domain=InvestmentDomain.CAPITAL_MARKETS.value,
            risk_profile=RiskProfile.CONSERVATIVE.value,
            target_allocation=0.6,  # 60% of capital markets domain
            expected_return=0.08,  # 8% expected return
            max_volatility=0.10
        )

        # Investment Banking Strategies
        self.strategies["model_portfolio_optimization"] = PortfolioStrategy(
            strategy_id="model_portfolio_optimization",
            name="AI Model Portfolio Optimization",
            domain=InvestmentDomain.INVESTMENT_BANKING.value,
            risk_profile=RiskProfile.BALANCED.value,
            target_allocation=0.7,
            expected_return=0.22,
            max_volatility=0.30
        )

        self.strategies["compute_resource_hedging"] = PortfolioStrategy(
            strategy_id="compute_resource_hedging",
            name="Compute Resource Hedging",
            domain=InvestmentDomain.INVESTMENT_BANKING.value,
            risk_profile=RiskProfile.HEDGE.value,
            target_allocation=0.3,
            expected_return=0.05,
            max_volatility=0.15
        )

        # Operational Hedge Strategies
        self.strategies["market_intelligence_arbitrage"] = PortfolioStrategy(
            strategy_id="market_intelligence_arbitrage",
            name="Market Intelligence Arbitrage",
            domain=InvestmentDomain.OPERATIONAL_HEDGE.value,
            risk_profile=RiskProfile.AGGRESSIVE.value,
            target_allocation=0.5,
            expected_return=0.35,
            max_volatility=0.45
        )

        self.strategies["operational_efficiency_hedge"] = PortfolioStrategy(
            strategy_id="operational_efficiency_hedge",
            name="Operational Efficiency Hedge",
            domain=InvestmentDomain.OPERATIONAL_HEDGE.value,
            risk_profile=RiskProfile.CONSERVATIVE.value,
            target_allocation=0.5,
            expected_return=0.12,
            max_volatility=0.18
        )

        # Human Coaching Strategies - The "Endgame" Level 50+ Content
        self.strategies["relationship_capital_arbitrage"] = PortfolioStrategy(
            strategy_id="relationship_capital_arbitrage",
            name="Relationship Capital Arbitrage",
            domain=InvestmentDomain.HUMAN_COACHING.value,
            risk_profile=RiskProfile.AGGRESSIVE.value,
            target_allocation=0.4,
            expected_return=0.50,  # High returns from life-changing connections
            max_volatility=0.55    # High volatility due to human emotions
        )

        self.strategies["confidence_compounding"] = PortfolioStrategy(
            strategy_id="confidence_compounding",
            name="Confidence Compounding Strategy",
            domain=InvestmentDomain.HUMAN_COACHING.value,
            risk_profile=RiskProfile.BALANCED.value,
            target_allocation=0.4,
            expected_return=0.28,  # Steady compounding returns
            max_volatility=0.35
        )

        self.strategies["proactive_risk_optimization"] = PortfolioStrategy(
            strategy_id="proactive_risk_optimization",
            name="Proactive Risk Optimization",
            domain=InvestmentDomain.HUMAN_COACHING.value,
            risk_profile=RiskProfile.CONSERVATIVE.value,
            target_allocation=0.2,
            expected_return=0.18,  # Conservative but valuable
            max_volatility=0.25
        )

    def _initialize_mmo_progression(self):
        """Initialize MMO-style progression system"""
        # Add some example positions for demonstration (would be earned through gameplay)
        if not self.positions:
            # Level 1-10: Capital Markets (Token gathering)
            self.add_position(PortfolioPosition(
                position_id="github_tokens",
                asset_class=AssetClass.TOKEN_POOL.value,
                domain=InvestmentDomain.CAPITAL_MARKETS.value,
                name="GitHub AI Tokens (Level 5)",
                quantity=50000,
                entry_price=0.0004,
                current_price=0.00042,
                risk_profile=RiskProfile.BALANCED.value,
                expected_return=0.15,
                volatility=0.20,
                entry_date=datetime.now() - timedelta(days=30),
                metadata={"level": 5, "experience_earned": 12500, "strategy_id": "liquidity_arbitrage"}
            ))

            # Level 10-30: Investment Banking (Model acquisition)
            self.add_position(PortfolioPosition(
                position_id="gpt4_model",
                asset_class=AssetClass.AI_MODEL.value,
                domain=InvestmentDomain.INVESTMENT_BANKING.value,
                name="GPT-4 Model Access (Level 25)",
                quantity=1,
                entry_price=20000,
                current_price=22000,
                risk_profile=RiskProfile.AGGRESSIVE.value,
                expected_return=0.25,
                volatility=0.35,
                entry_date=datetime.now() - timedelta(days=15),
                metadata={"level": 25, "experience_earned": 45000, "strategy_id": "model_portfolio_optimization"}
            ))

            # Level 50+: Human Coaching (Life mentorship - endgame)
            self.add_position(PortfolioPosition(
                position_id="confidence_booster",
                asset_class=AssetClass.CONFIDENCE_BUILDING.value,
                domain=InvestmentDomain.HUMAN_COACHING.value,
                name="Confidence Building Portfolio (Level 60)",
                quantity=1,
                entry_price=50000,
                current_price=75000,  # Massive value from life-changing impact
                risk_profile=RiskProfile.AGGRESSIVE.value,
                expected_return=0.50,  # Life-changing returns
                volatility=0.55,
                entry_date=datetime.now() - timedelta(days=90),
                metadata={"level": 60, "experience_earned": 150000, "strategy_id": "confidence_compounding",
                         "lives_impacted": 47, "success_stories": 23}
            ))

    def add_position(self, position: PortfolioPosition) -> bool:
        """Add a position to the portfolio"""
        if position.position_id in self.positions:
            logger.warning(f"Position {position.position_id} already exists")
            return False

        self.positions[position.position_id] = position

        # Add to strategy
        if position.metadata.get("strategy_id"):
            strategy_id = position.metadata["strategy_id"]
            if strategy_id in self.strategies:
                self.strategies[strategy_id].positions.append(position.position_id)

        self._calculate_total_value()
        self._update_strategy_allocations()

        # Record transaction
        self._record_transaction({
            "type": "position_add",
            "position_id": position.position_id,
            "asset_class": position.asset_class,
            "domain": position.domain,
            "quantity": position.quantity,
            "price": position.entry_price,
            "value": position.market_value,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"✅ Added position: {position.name} (${position.market_value:,.2f})")
        return True

    def update_position_price(self, position_id: str, new_price: float) -> bool:
        """Update position price and recalculate P&L"""
        if position_id not in self.positions:
            return False

        position = self.positions[position_id]
        old_value = position.market_value
        position.current_price = new_price
        position.market_value = position.quantity * new_price
        position.unrealized_pnl = position.market_value - (position.quantity * position.entry_price)
        position.last_updated = datetime.now()

        # Recalculate portfolio value
        self._calculate_total_value()

        # Record price update
        pnl_change = position.market_value - old_value
        self._record_transaction({
            "type": "price_update",
            "position_id": position_id,
            "old_price": position.current_price,
            "new_price": new_price,
            "pnl_change": pnl_change,
            "timestamp": datetime.now().isoformat()
        })

        return True

    def execute_trade(self, position_id: str, quantity: float, price: float,
                     trade_type: str = "buy") -> bool:
        """Execute a trade (buy/sell position)"""
        if trade_type == "buy":
            if self.cash_position < (quantity * price):
                logger.error("Insufficient cash for trade")
                return False

            # Create new position or add to existing
            if position_id in self.positions:
                position = self.positions[position_id]
                old_quantity = position.quantity
                position.quantity += quantity
                position.current_price = price  # Update to execution price
                position.market_value = position.quantity * price
                position.unrealized_pnl = position.market_value - (position.quantity * position.entry_price)
            else:
                # This would need more parameters - simplified
                logger.error("New position creation requires full parameters")
                return False

            self.cash_position -= (quantity * price)

        elif trade_type == "sell":
            if position_id not in self.positions:
                logger.error("Position not found")
                return False

            position = self.positions[position_id]
            if position.quantity < quantity:
                logger.error("Insufficient position size")
                return False

            position.quantity -= quantity
            position.market_value = position.quantity * price
            self.cash_position += (quantity * price)

            # Remove position if fully sold
            if position.quantity <= 0:
                del self.positions[position_id]

        self._calculate_total_value()
        self._record_transaction({
            "type": trade_type,
            "position_id": position_id,
            "quantity": quantity,
            "price": price,
            "value": quantity * price,
            "cash_balance": self.cash_position,
            "timestamp": datetime.now().isoformat()
        })

        return True

    def rebalance_portfolio(self) -> Dict[str, Any]:
        """Rebalance portfolio according to target allocations"""
        results = {
            "trades_executed": 0,
            "total_value_changed": 0.0,
            "strategies_rebalanced": 0,
            "timestamp": datetime.now().isoformat()
        }

        # Check each strategy for rebalancing needs
        for strategy_id, strategy in self.strategies.items():
            current_allocation = strategy.current_allocation
            target_allocation = strategy.target_allocation
            domain_total = self._calculate_domain_value(strategy.domain)

            if domain_total > 0:
                current_percent = current_allocation / domain_total
                deviation = abs(current_percent - target_allocation)

                if deviation > strategy.rebalancing_threshold:
                    # Calculate required trade
                    target_value = domain_total * target_allocation
                    trade_value = target_value - current_allocation

                    if abs(trade_value) > 100:  # Minimum trade size
                        logger.info(f"Rebalancing {strategy_id}: {current_percent:.1%} → {target_allocation:.1%}")

                        # Simplified rebalancing - in real implementation would execute actual trades
                        results["trades_executed"] += 1
                        results["total_value_changed"] += trade_value
                        results["strategies_rebalanced"] += 1

        return results

    def calculate_risk_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics like investment banking"""
        positions = list(self.positions.values())

        if not positions:
            return {"error": "No positions to analyze"}

        # Calculate VaR (simplified)
        portfolio_returns = [p.unrealized_pnl / (p.quantity * p.entry_price) for p in positions]
        portfolio_volatility = math.sqrt(sum(r**2 for r in portfolio_returns) / len(portfolio_returns))

        self.risk_metrics.var_95 = -self.total_value * portfolio_volatility * 1.645  # 95% confidence
        self.risk_metrics.expected_shortfall = -self.total_value * portfolio_volatility * 2.0

        # Calculate maximum drawdown
        peak_value = max(self.performance_history[-30:] or [self.total_value],
                        key=lambda x: x.get("total_value", 0))["total_value"]
        current_value = self.total_value
        self.risk_metrics.max_drawdown = (peak_value - current_value) / peak_value if peak_value > 0 else 0

        return {
            "var_95": self.risk_metrics.var_95,
            "expected_shortfall": self.risk_metrics.expected_shortfall,
            "max_drawdown": self.risk_metrics.max_drawdown,
            "portfolio_volatility": portfolio_volatility,
            "beta_to_market": self.risk_metrics.beta_to_market
        }

    def get_portfolio_performance(self) -> Dict[str, Any]:
        """Get comprehensive portfolio performance metrics"""
        positions = list(self.positions.values())

        total_pnl = sum(p.unrealized_pnl for p in positions)
        total_invested = sum(p.quantity * p.entry_price for p in positions)

        return {
            "total_value": self.total_value,
            "cash_position": self.cash_position,
            "total_positions": len(positions),
            "total_pnl": total_pnl,
            "total_return_pct": (total_pnl / total_invested * 100) if total_invested > 0 else 0,
            "sharpe_ratio": self._calculate_portfolio_sharpe(),
            "domain_breakdown": self._calculate_domain_breakdown(),
            "strategy_performance": self._calculate_strategy_performance()
        }

    def _calculate_total_value(self):
        """Calculate total portfolio value"""
        position_value = sum(p.market_value for p in self.positions.values())
        self.total_value = position_value + self.cash_position

    def _calculate_domain_value(self, domain: str) -> float:
        """Calculate total value in a domain"""
        return sum(p.market_value for p in self.positions.values() if p.domain == domain)

    def _update_strategy_allocations(self):
        """Update current strategy allocations"""
        for strategy in self.strategies.values():
            strategy.current_allocation = sum(
                self.positions[p].market_value
                for p in strategy.positions
                if p in self.positions
            )

    def _calculate_portfolio_sharpe(self) -> float:
        """Calculate portfolio Sharpe ratio"""
        if not self.performance_history:
            return 0.0

        returns = []
        for i in range(1, len(self.performance_history)):
            prev_value = self.performance_history[i-1]["total_value"]
            curr_value = self.performance_history[i]["total_value"]
            daily_return = (curr_value - prev_value) / prev_value
            returns.append(daily_return)

        if not returns:
            return 0.0

        avg_return = sum(returns) / len(returns)
        volatility = math.sqrt(sum((r - avg_return)**2 for r in returns) / len(returns))

        # Assume 2% risk-free rate annualized
        risk_free_daily = 0.02 / 252

        return (avg_return - risk_free_daily) / volatility if volatility > 0 else 0

    def _calculate_domain_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Calculate portfolio breakdown by domain"""
        breakdown = {}
        for domain in InvestmentDomain:
            domain_value = self._calculate_domain_value(domain.value)
            breakdown[domain.value] = {
                "value": domain_value,
                "percentage": (domain_value / self.total_value * 100) if self.total_value > 0 else 0,
                "positions": len([p for p in self.positions.values() if p.domain == domain.value])
            }
        return breakdown

    def _calculate_strategy_performance(self) -> Dict[str, Dict[str, Any]]:
        """Calculate performance by strategy"""
        performance = {}
        for strategy_id, strategy in self.strategies.items():
            strategy_value = strategy.current_allocation
            target_value = self._calculate_domain_value(strategy.domain) * strategy.target_allocation

            performance[strategy_id] = {
                "current_value": strategy_value,
                "target_value": target_value,
                "deviation_pct": ((strategy_value - target_value) / target_value * 100) if target_value > 0 else 0,
                "expected_return": strategy.expected_return,
                "positions": len(strategy.positions)
            }
        return performance

    def _calculate_average_level(self) -> int:
        """Calculate average character level across all positions"""
        if not self.positions:
            return 1
        total_level = sum(p.metadata.get('level', 1) for p in self.positions.values())
        return int(total_level / len(self.positions))

    def _calculate_total_experience(self) -> int:
        """Calculate total experience earned"""
        return sum(p.metadata.get('experience_earned', 0) for p in self.positions.values())

    def _calculate_confidence_level(self) -> str:
        """Calculate overall confidence level based on human coaching domain performance"""
        coaching_positions = [p for p in self.positions.values()
                            if p.domain == InvestmentDomain.HUMAN_COACHING.value]

        if not coaching_positions:
            return "Building Foundations"

        total_coaching_value = sum(p.market_value for p in coaching_positions)
        coaching_allocation = total_coaching_value / self.total_value if self.total_value > 0 else 0

        if coaching_allocation > 0.5:
            return "Legendary Confidence (Obi-Wan Level)"
        elif coaching_allocation > 0.3:
            return "High Confidence (Proactive Mindset)"
        elif coaching_allocation > 0.1:
            return "Growing Confidence (Learning Phase)"
        else:
            return "Building Confidence (Early Journey)"

    def _record_transaction(self, transaction: Dict[str, Any]):
        """Record a transaction in history"""
        self.transaction_history.append(transaction)

        # Keep only last 1000 transactions
        if len(self.transaction_history) > 1000:
            self.transaction_history = self.transaction_history[-1000:]

    def record_performance_snapshot(self):
        """Record current performance snapshot"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "total_value": self.total_value,
            "cash_position": self.cash_position,
            "total_positions": len(self.positions),
            "domain_breakdown": self._calculate_domain_breakdown(),
            "risk_metrics": self.calculate_risk_metrics()
        }

        self.performance_history.append(snapshot)

        # Keep only last 365 days of daily snapshots
        if len(self.performance_history) > 365:
            self.performance_history = self.performance_history[-365:]


def main():
    """CLI interface for AI Investment Portfolio"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Investment Portfolio Management")
    parser.add_argument("--status", action="store_true", help="Show portfolio status")
    parser.add_argument("--performance", action="store_true", help="Show performance metrics")
    parser.add_argument("--risk", action="store_true", help="Show risk metrics")
    parser.add_argument("--rebalance", action="store_true", help="Execute portfolio rebalancing")
    parser.add_argument("--domains", action="store_true", help="Show domain breakdown")

    args = parser.parse_args()

    # Initialize portfolio
    portfolio = AIInvestmentPortfolio()

    # Add some example positions for demonstration
    if not portfolio.positions:
        # Add example positions
        portfolio.add_position(PortfolioPosition(
            position_id="github_tokens",
            asset_class=AssetClass.TOKEN_POOL.value,
            domain=InvestmentDomain.CAPITAL_MARKETS.value,
            name="GitHub AI Tokens",
            quantity=50000,
            entry_price=0.0004,
            current_price=0.00042,
            risk_profile=RiskProfile.BALANCED.value,
            expected_return=0.15,
            volatility=0.20,
            entry_date=datetime.now() - timedelta(days=30),
            metadata={"strategy_id": "liquidity_arbitrage"}
        ))

        portfolio.add_position(PortfolioPosition(
            position_id="gpt4_model",
            asset_class=AssetClass.AI_MODEL.value,
            domain=InvestmentDomain.INVESTMENT_BANKING.value,
            name="GPT-4 Model Access",
            quantity=1,
            entry_price=20000,
            current_price=22000,
            risk_profile=RiskProfile.AGGRESSIVE.value,
            expected_return=0.25,
            volatility=0.35,
            entry_date=datetime.now() - timedelta(days=15),
            metadata={"strategy_id": "model_portfolio_optimization"}
        ))

    if args.status:
        performance = portfolio.get_portfolio_performance()
        print("🤖 AI INVESTMENT PORTFOLIO STATUS")
        print("="*50)
        print(f"Portfolio: {portfolio.portfolio_name}")
        print(f"Total Value: ${performance['total_value']:,.2f}")
        print(f"Cash Position: ${performance['cash_position']:,.2f}")
        print(f"Total Positions: {performance['total_positions']}")
        print(f"Total P&L: ${performance['total_pnl']:,.2f}")
        print(f"Total Return: {performance['total_return_pct']:.2f}%")
        print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")

    elif args.performance:
        perf = portfolio.get_portfolio_performance()
        print("🎮 MMO-STYLE PORTFOLIO PERFORMANCE")
        print("="*60)
        print(f"Character Level: {self._calculate_average_level()}")
        print(f"Total Experience: {self._calculate_total_experience():,}")
        print(f"Total Value: ${perf['total_value']:,.2f}")
        print(f"Cash Position: ${perf['cash_position']:,.2f}")
        print(f"Total P&L: ${perf['total_pnl']:,.2f}")
        print(f"Return: {perf['total_return_pct']:.2f}%")
        print(f"Confidence Level: {self._calculate_confidence_level()}")

        print("\n🏟️ MMO PROGRESSION BY DOMAIN:")
        domain_mmo_info = {
            "capital_markets": "Levels 1-10: Solo Play → Basic Token Gathering",
            "investment_banking": "Levels 10-30: Group Content → Model Acquisition",
            "operational_hedge": "Levels 30-50: Raiding → Business Operations",
            "human_coaching": "Levels 50+: Legendary → Life Coaching & Mentorship"
        }

        for domain, data in perf['domain_breakdown'].items():
            mmo_progress = domain_mmo_info.get(domain, "Unknown progression")
            print(f"  {domain.upper()}: ${data['value']:,.2f} ({data['percentage']:.1f}%) - {data['positions']} positions")
            print(f"    {mmo_progress}")

        # Show individual position levels
        print("\n📊 INDIVIDUAL POSITION PROGRESSION:")
        for pid, position in self.positions.items():
            level = position.metadata.get('level', 1)
            exp = position.metadata.get('experience_earned', 0)
            print(f"  {position.name}: Level {level} ({exp:,} XP)")

    elif args.risk:
        risk = portfolio.calculate_risk_metrics()
        print("⚠️  RISK METRICS")
        print("="*50)
        print(f"VaR (95%): ${risk['var_95']:,.2f}")
        print(f"Expected Shortfall: ${risk['expected_shortfall']:,.2f}")
        print(f"Max Drawdown: {risk['max_drawdown']:.2f}%")
        print(f"Portfolio Volatility: {risk['portfolio_volatility']:.2f}")

    elif args.rebalance:
        results = portfolio.rebalance_portfolio()
        print("🔄 PORTFOLIO REBALANCING")
        print("="*50)
        print(f"Trades Executed: {results['trades_executed']}")
        print(f"Strategies Rebalanced: {results['strategies_rebalanced']}")
        print(f"Total Value Change: ${results['total_value_changed']:,.2f}")

    elif args.domains:
        perf = portfolio.get_portfolio_performance()
        print("🏗️  DOMAIN BREAKDOWN")
        print("="*50)
        for domain, data in perf['domain_breakdown'].items():
            domain_info = portfolio.domains[domain]
            print(f"\n{domain_info['name'].upper()}")
            print(f"  Description: {domain_info['description']}")
            print(f"  Value: ${data['value']:,.2f} ({data['percentage']:.1f}%)")
            print(f"  Positions: {data['positions']}")
            print(f"  Volatility: {domain_info['risk_characteristics']['volatility']:.1%}")
            print(f"  Liquidity: {domain_info['risk_characteristics']['liquidity']:.1%}")
            print(f"  Benchmark: {domain_info['benchmark']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()