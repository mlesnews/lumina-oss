#!/usr/bin/env python3
"""
AI Liquidity Pool - Financial-Grade Token Management

Unified AI token liquidity pool treating tokens like financial assets.
Consolidates all AI providers into a single liquidity pool for optimal usage.

Financial Principles Applied:
- Liquidity Pool: Unified token reserve across all providers
- Arbitrage: Route to lowest cost provider
- Diversification: Balance usage across providers
- Risk Management: Avoid single-provider dependency
- Cost Averaging: Optimize long-term token economics

Tags: #AI_LIQUIDITY #FINANCIAL_LOGIC #TOKEN_ECONOMICS #ARBITRAGE #LIQUIDITY_POOL
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

logger = get_logger("AILiquidityPool")


class LiquidityTier(Enum):
    """Liquidity tiers based on cost efficiency"""
    PREMIUM = "premium"      # Highest performance, highest cost
    STANDARD = "standard"    # Balanced performance/cost
    ECONOMY = "economy"      # Lowest cost, acceptable performance
    SURPLUS = "surplus"      # Excess capacity, minimal cost


@dataclass
class ProviderLiquidity:
    """Individual provider liquidity contribution"""
    provider_id: str
    provider_name: str
    token_balance: float = 0.0
    token_cost_per_unit: float = 0.0  # Cost per 1K tokens in USD
    liquidity_tier: str = LiquidityTier.STANDARD.value
    max_requests_per_minute: int = 60
    current_requests_per_minute: int = 0
    performance_score: float = 1.0  # 0.0 to 1.0
    reliability_score: float = 1.0  # 0.0 to 1.0
    last_used: datetime = field(default_factory=datetime.now)
    total_requests: int = 0
    failed_requests: int = 0

    @property
    def liquidity_score(self) -> float:
        """Calculate overall liquidity score for this provider"""
        # Weighted score: cost (40%), performance (30%), reliability (20%), availability (10%)
        availability_ratio = min(1.0, (self.max_requests_per_minute - self.current_requests_per_minute) / self.max_requests_per_minute)

        cost_score = 1.0 / (1.0 + self.token_cost_per_unit)  # Inverse relationship with cost
        performance_score = self.performance_score
        reliability_score = 1.0 - (self.failed_requests / max(1, self.total_requests))
        availability_score = availability_ratio

        return (
            cost_score * 0.4 +
            performance_score * 0.3 +
            reliability_score * 0.2 +
            availability_score * 0.1
        )

    @property
    def effective_liquidity_units(self) -> float:
        """Convert token balance to standardized liquidity units"""
        # Normalize all tokens to a common unit based on cost efficiency
        base_cost = 0.001  # $0.001 per 1K tokens as baseline
        efficiency_multiplier = base_cost / max(self.token_cost_per_unit, 0.0001)
        return self.token_balance * efficiency_multiplier


@dataclass
class LiquidityTransaction:
    """Record of liquidity transactions"""
    transaction_id: str
    timestamp: datetime
    provider_from: str
    provider_to: str
    token_amount: float
    usd_value: float
    transaction_type: str  # "arbitrage", "balancing", "usage", "replenishment"
    reason: str = ""
    success: bool = True


@dataclass
class LiquidityPool:
    """Unified AI liquidity pool"""
    pool_id: str = "lumina_ai_liquidity"
    total_liquidity_units: float = 0.0
    total_usd_value: float = 0.0
    providers: Dict[str, ProviderLiquidity] = field(default_factory=dict)
    transaction_history: List[LiquidityTransaction] = field(default_factory=list)
    last_rebalance: datetime = field(default_factory=datetime.now)
    rebalance_interval_hours: int = 24
    target_allocation_percent: Dict[str, float] = field(default_factory=dict)

    def add_provider(self, provider: ProviderLiquidity):
        """Add a provider to the liquidity pool"""
        self.providers[provider.provider_id] = provider
        self._recalculate_totals()
        logger.info(f"✅ Added provider {provider.provider_name} to liquidity pool")

    def remove_provider(self, provider_id: str):
        """Remove a provider from the liquidity pool"""
        if provider_id in self.providers:
            provider = self.providers.pop(provider_id)
            self._recalculate_totals()
            logger.info(f"✅ Removed provider {provider.provider_name} from liquidity pool")

    def update_provider_balance(self, provider_id: str, new_balance: float):
        """Update a provider's token balance"""
        if provider_id in self.providers:
            old_balance = self.providers[provider_id].token_balance
            self.providers[provider_id].token_balance = new_balance
            self._recalculate_totals()

            # Record transaction
            usd_value = abs(new_balance - old_balance) * self.providers[provider_id].token_cost_per_unit
            transaction = LiquidityTransaction(
                transaction_id=f"balance_update_{int(time.time())}",
                timestamp=datetime.now(),
                provider_from="external" if new_balance > old_balance else provider_id,
                provider_to=provider_id if new_balance > old_balance else "external",
                token_amount=abs(new_balance - old_balance),
                usd_value=usd_value,
                transaction_type="replenishment",
                reason=f"Balance update: {old_balance} → {new_balance}"
            )
            self.transaction_history.append(transaction)

    def route_request(self, request_complexity: float = 1.0,
                     preferred_tier: Optional[str] = None) -> Optional[Tuple[str, float]]:
        """
        Route AI request to optimal provider based on liquidity

        Args:
            request_complexity: 0.0-1.0 (higher = more complex, needs better model)
            preferred_tier: Optional preferred liquidity tier

        Returns:
            Tuple of (provider_id, confidence_score) or None if no provider available
        """
        available_providers = [
            (pid, p) for pid, p in self.providers.items()
            if p.token_balance > 100 and  # Minimum token threshold
               p.current_requests_per_minute < p.max_requests_per_minute
        ]

        if not available_providers:
            logger.warning("🚫 No providers with sufficient liquidity available")
            return None

        # Score providers based on liquidity and request requirements
        provider_scores = []
        for provider_id, provider in available_providers:
            # Base liquidity score
            score = provider.liquidity_score

            # Adjust for request complexity
            if request_complexity > 0.7 and provider.liquidity_tier == LiquidityTier.ECONOMY.value:
                score *= 0.7  # Penalize economy tier for complex requests
            elif request_complexity < 0.3 and provider.liquidity_tier == LiquidityTier.PREMIUM.value:
                score *= 0.8  # Slight penalty for overkill

            # Adjust for preferred tier
            if preferred_tier and provider.liquidity_tier != preferred_tier:
                score *= 0.9  # Small penalty for non-preferred tier

            # Adjust for recent usage (favor less recently used)
            hours_since_used = (datetime.now() - provider.last_used).total_seconds() / 3600
            recency_bonus = min(1.0, hours_since_used / 24)  # Max bonus after 24 hours
            score *= (1.0 + recency_bonus * 0.1)

            provider_scores.append((provider_id, score))

        if not provider_scores:
            return None

        # Select best provider
        best_provider, confidence = max(provider_scores, key=lambda x: x[1])

        # Update provider usage tracking
        self.providers[best_provider].current_requests_per_minute += 1
        self.providers[best_provider].last_used = datetime.now()
        self.providers[best_provider].total_requests += 1

        logger.info(f"🎯 Routed request to {best_provider} (confidence: {confidence:.2f})")
        return (best_provider, confidence)

    def record_request_result(self, provider_id: str, success: bool, tokens_used: float):
        """Record the result of a routed request"""
        if provider_id in self.providers:
            provider = self.providers[provider_id]
            provider.current_requests_per_minute = max(0, provider.current_requests_per_minute - 1)

            if not success:
                provider.failed_requests += 1

            # Deduct tokens
            if tokens_used > 0:
                old_balance = provider.token_balance
                provider.token_balance = max(0, provider.token_balance - tokens_used)

                # Record usage transaction
                usd_value = tokens_used * provider.token_cost_per_unit
                transaction = LiquidityTransaction(
                    transaction_id=f"usage_{int(time.time())}_{provider_id}",
                    timestamp=datetime.now(),
                    provider_from=provider_id,
                    provider_to="consumed",
                    token_amount=tokens_used,
                    usd_value=usd_value,
                    transaction_type="usage",
                    reason=f"AI request consumption",
                    success=success
                )
                self.transaction_history.append(transaction)

                self._recalculate_totals()

    def perform_arbitrage(self) -> List[LiquidityTransaction]:
        """
        Perform liquidity arbitrage - move tokens between providers for optimal efficiency

        Returns list of arbitrage transactions performed
        """
        transactions = []

        # Find providers with surplus liquidity that could be moved to deficit providers
        surplus_providers = [
            (pid, p) for pid, p in self.providers.items()
            if p.liquidity_tier == LiquidityTier.SURPLUS.value and p.token_balance > 1000
        ]

        deficit_providers = [
            (pid, p) for pid, p in self.providers.items()
            if p.liquidity_tier in [LiquidityTier.PREMIUM.value, LiquidityTier.STANDARD.value]
            and p.token_balance < 500
        ]

        for surplus_pid, surplus_provider in surplus_providers:
            for deficit_pid, deficit_provider in deficit_providers:
                if surplus_pid == deficit_pid:
                    continue

                # Calculate arbitrage opportunity
                # Move tokens from surplus to deficit if it improves overall liquidity
                surplus_score_before = surplus_provider.liquidity_score
                deficit_score_before = deficit_provider.liquidity_score

                # Simulate moving 1000 tokens
                transfer_amount = min(1000, surplus_provider.token_balance, 10000 - deficit_provider.token_balance)
                if transfer_amount < 100:
                    continue

                # Calculate scores after transfer
                temp_surplus_balance = surplus_provider.token_balance - transfer_amount
                temp_deficit_balance = deficit_provider.token_balance + transfer_amount

                # Recalculate liquidity scores (simplified)
                surplus_score_after = surplus_score_before * (temp_surplus_balance / surplus_provider.token_balance)
                deficit_score_after = deficit_score_before * (temp_deficit_balance / deficit_provider.token_balance)

                overall_improvement = (deficit_score_after - deficit_score_before) + (surplus_score_after - surplus_score_before)

                if overall_improvement > 0.05:  # 5% improvement threshold
                    # Execute arbitrage
                    surplus_provider.token_balance = temp_surplus_balance
                    deficit_provider.token_balance = temp_deficit_balance

                    usd_value = transfer_amount * surplus_provider.token_cost_per_unit

                    transaction = LiquidityTransaction(
                        transaction_id=f"arbitrage_{int(time.time())}_{surplus_pid}_{deficit_pid}",
                        timestamp=datetime.now(),
                        provider_from=surplus_pid,
                        provider_to=deficit_pid,
                        token_amount=transfer_amount,
                        usd_value=usd_value,
                        transaction_type="arbitrage",
                        reason=f"Liquidity arbitrage: {surplus_score_before:.2f} → {surplus_score_after:.2f} overall improvement"
                    )

                    transactions.append(transaction)
                    self.transaction_history.append(transaction)

                    logger.info(f"💰 Arbitrage executed: {transfer_amount} tokens from {surplus_pid} to {deficit_pid}")

        self._recalculate_totals()
        return transactions

    def rebalance_portfolio(self) -> List[LiquidityTransaction]:
        """
        Rebalance portfolio according to target allocations
        Similar to financial portfolio rebalancing
        """
        if not self.target_allocation_percent:
            return []

        transactions = []
        current_allocations = self._calculate_current_allocations()

        for provider_id, target_percent in self.target_allocation_percent.items():
            if provider_id not in self.providers:
                continue

            current_percent = current_allocations.get(provider_id, 0)
            deviation = abs(current_percent - target_percent)

            if deviation > 0.05:  # 5% deviation threshold
                # Calculate rebalancing trade
                target_liquidity = self.total_liquidity_units * (target_percent / 100)
                current_liquidity = self.providers[provider_id].effective_liquidity_units

                if current_liquidity < target_liquidity:
                    # Need to add liquidity - find surplus providers
                    needed = target_liquidity - current_liquidity
                    surplus_providers = [
                        (pid, p) for pid, p in self.providers.items()
                        if pid != provider_id and p.effective_liquidity_units > current_liquidity + needed
                    ]

                    for surplus_pid, surplus_provider in surplus_providers:
                        transfer_liquidity = min(needed, surplus_provider.effective_liquidity_units - current_liquidity)
                        if transfer_liquidity < 100:
                            continue

                        # Convert back to actual tokens
                        transfer_tokens = transfer_liquidity / surplus_provider.effective_liquidity_units * surplus_provider.token_balance

                        surplus_provider.token_balance -= transfer_tokens
                        self.providers[provider_id].token_balance += transfer_tokens

                        usd_value = transfer_tokens * surplus_provider.token_cost_per_unit

                        transaction = LiquidityTransaction(
                            transaction_id=f"rebalance_{int(time.time())}_{surplus_pid}_{provider_id}",
                            timestamp=datetime.now(),
                            provider_from=surplus_pid,
                            provider_to=provider_id,
                            token_amount=transfer_tokens,
                            usd_value=usd_value,
                            transaction_type="balancing",
                            reason=f"Portfolio rebalancing: {current_percent:.1f}% → {target_percent:.1f}%"
                        )

                        transactions.append(transaction)
                        self.transaction_history.append(transaction)
                        break

        self._recalculate_totals()
        self.last_rebalance = datetime.now()
        return transactions

    def _calculate_current_allocations(self) -> Dict[str, float]:
        """Calculate current percentage allocations by provider"""
        allocations = {}
        for provider_id, provider in self.providers.items():
            if self.total_liquidity_units > 0:
                allocations[provider_id] = (provider.effective_liquidity_units / self.total_liquidity_units) * 100
            else:
                allocations[provider_id] = 0
        return allocations

    def _recalculate_totals(self):
        """Recalculate total pool statistics"""
        self.total_liquidity_units = sum(p.effective_liquidity_units for p in self.providers.values())
        self.total_usd_value = sum(p.token_balance * p.token_cost_per_unit for p in self.providers.values())

    def get_pool_status(self) -> Dict[str, Any]:
        """Get comprehensive pool status"""
        return {
            "pool_id": self.pool_id,
            "total_liquidity_units": round(self.total_liquidity_units, 2),
            "total_usd_value": round(self.total_usd_value, 2),
            "provider_count": len(self.providers),
            "providers": {
                pid: {
                    "name": p.provider_name,
                    "tier": p.liquidity_tier,
                    "token_balance": round(p.token_balance, 2),
                    "liquidity_units": round(p.effective_liquidity_units, 2),
                    "liquidity_score": round(p.liquidity_score, 3),
                    "usd_value": round(p.token_balance * p.token_cost_per_unit, 2),
                    "utilization_percent": round((p.current_requests_per_minute / max(1, p.max_requests_per_minute)) * 100, 1),
                    "allocation_percent": round((p.effective_liquidity_units / max(1, self.total_liquidity_units)) * 100, 1)
                }
                for pid, p in self.providers.items()
            },
            "last_rebalance": self.last_rebalance.isoformat(),
            "transaction_count": len(self.transaction_history),
            "recent_transactions": [
                {
                    "id": t.transaction_id,
                    "timestamp": t.timestamp.isoformat() if isinstance(t.timestamp, datetime) else t.timestamp,
                    "type": t.transaction_type,
                    "from": t.provider_from,
                    "to": t.provider_to,
                    "amount": round(t.token_amount, 2),
                    "usd_value": round(t.usd_value, 2),
                    "reason": t.reason
                }
                for t in self.transaction_history[-10:]  # Last 10 transactions
            ]
        }


class AILiquidityManager:
    """
    AI Liquidity Manager - Financial-grade AI token management

    Treats AI tokens like financial liquidity with arbitrage, diversification,
    and portfolio optimization principles.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize liquidity manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "liquidity_pool"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.pool_file = self.data_dir / "liquidity_pool.json"
        self.transactions_file = self.data_dir / "transactions.json"

        # Core components
        self.liquidity_pool = LiquidityPool()
        self._load_state()

        # Initialize default providers if empty
        if not self.liquidity_pool.providers:
            self._initialize_default_providers()

        logger.info("✅ AI Liquidity Manager initialized")
        logger.info(f"   Total liquidity: {self.liquidity_pool.total_liquidity_units:.0f} units")
        logger.info(f"   Total value: ${self.liquidity_pool.total_usd_value:.2f}")
        logger.info(f"   Providers: {len(self.liquidity_pool.providers)}")

    def _initialize_default_providers(self):
        """Initialize default AI providers with realistic token allocations"""

        # GitHub Models (User's $20 subscription = ~50K tokens)
        github_provider = ProviderLiquidity(
            provider_id="github",
            provider_name="GitHub Models",
            token_balance=50000,  # $20 subscription
            token_cost_per_unit=0.0004,  # Average $0.0004 per token
            liquidity_tier=LiquidityTier.STANDARD.value,
            max_requests_per_minute=100,
            performance_score=0.85,
            reliability_score=0.95
        )

        # Local ULTRON (Free, unlimited)
        ultron_provider = ProviderLiquidity(
            provider_id="ultron",
            provider_name="ULTRON Local",
            token_balance=1000000,  # Effectively unlimited
            token_cost_per_unit=0.0,  # Free
            liquidity_tier=LiquidityTier.SURPLUS.value,
            max_requests_per_minute=1000,
            performance_score=0.75,
            reliability_score=0.98
        )

        # KAIJU Iron Legion (NAS-based, free)
        kaiju_provider = ProviderLiquidity(
            provider_id="kaiju",
            provider_name="KAIJU Iron Legion",
            token_balance=500000,  # High capacity
            token_cost_per_unit=0.0,  # Free
            liquidity_tier=LiquidityTier.SURPLUS.value,
            max_requests_per_minute=500,
            performance_score=0.80,
            reliability_score=0.90
        )

        # Add providers to pool
        self.liquidity_pool.add_provider(github_provider)
        self.liquidity_pool.add_provider(ultron_provider)
        self.liquidity_pool.add_provider(kaiju_provider)

        # Set target allocations (like financial portfolio targets)
        self.liquidity_pool.target_allocation_percent = {
            "github": 20,    # 20% GitHub (premium but limited)
            "ultron": 40,    # 40% Local ULTRON (reliable, free)
            "kaiju": 40     # 40% NAS KAIJU (capacity, free)
        }

        self._save_state()
        logger.info("✅ Initialized default AI liquidity providers")

    def route_ai_request(self, model_complexity: float = 0.5,
                        preferred_tier: Optional[str] = None,
                        max_cost_per_token: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Route AI request using liquidity optimization

        Args:
            model_complexity: 0.0-1.0 (higher = needs better model)
            preferred_tier: Optional preferred liquidity tier
            max_cost_per_token: Optional maximum cost per token

        Returns:
            Routing decision with provider, confidence, and cost analysis
        """

        # Apply cost filter if specified
        if max_cost_per_token is not None:
            affordable_providers = [
                pid for pid, p in self.liquidity_pool.providers.items()
                if p.token_cost_per_unit <= max_cost_per_token and p.token_balance > 100
            ]
            if not affordable_providers:
                logger.warning(f"🚫 No providers within cost limit: ${max_cost_per_token} per token")
                return None

        # Route using liquidity algorithm
        routing_result = self.liquidity_pool.route_request(model_complexity, preferred_tier)

        if not routing_result:
            return None

        provider_id, confidence = routing_result
        provider = self.liquidity_pool.providers[provider_id]

        # Calculate cost analysis
        estimated_tokens = 1000  # Rough estimate for cost calculation
        estimated_cost = estimated_tokens * provider.token_cost_per_unit

        return {
            "provider_id": provider_id,
            "provider_name": provider.provider_name,
            "confidence_score": round(confidence, 3),
            "liquidity_tier": provider.liquidity_tier,
            "estimated_cost_per_1k_tokens": round(provider.token_cost_per_unit * 1000, 4),
            "estimated_cost_usd": round(estimated_cost, 4),
            "performance_score": provider.performance_score,
            "reliability_score": provider.reliability_score,
            "routing_reason": self._explain_routing_decision(provider_id, model_complexity, preferred_tier)
        }

    def _explain_routing_decision(self, provider_id: str, complexity: float, preferred_tier: Optional[str]) -> str:
        """Explain why a particular provider was selected"""
        provider = self.liquidity_pool.providers[provider_id]

        reasons = []

        # Cost efficiency
        if provider.token_cost_per_unit == 0:
            reasons.append("free tokens available")
        elif provider.token_cost_per_unit < 0.001:
            reasons.append("cost-effective option")
        else:
            reasons.append(f"optimal cost-performance ratio")

        # Availability
        utilization = provider.current_requests_per_minute / provider.max_requests_per_minute
        if utilization < 0.5:
            reasons.append("high availability")
        elif utilization < 0.8:
            reasons.append("good availability")
        else:
            reasons.append("limited availability")

        # Complexity matching
        if complexity > 0.7 and provider.liquidity_tier in [LiquidityTier.PREMIUM.value, LiquidityTier.STANDARD.value]:
            reasons.append("suitable for complex requests")
        elif complexity < 0.3 and provider.liquidity_tier == LiquidityTier.ECONOMY.value:
            reasons.append("efficient for simple requests")

        # Preference matching
        if preferred_tier and provider.liquidity_tier == preferred_tier:
            reasons.append(f"matches preferred {preferred_tier} tier")

        return ", ".join(reasons)

    def record_usage(self, provider_id: str, tokens_used: float, success: bool = True):
        """Record AI usage for liquidity tracking"""
        self.liquidity_pool.record_request_result(provider_id, success, tokens_used)
        self._save_state()

    def optimize_liquidity(self) -> Dict[str, Any]:
        """Perform liquidity optimization (arbitrage + rebalancing)"""
        results = {
            "arbitrage_transactions": 0,
            "rebalancing_transactions": 0,
            "total_improvement": 0.0,
            "timestamp": datetime.now().isoformat()
        }

        # Perform arbitrage
        arbitrage_txns = self.liquidity_pool.perform_arbitrage()
        results["arbitrage_transactions"] = len(arbitrage_txns)

        # Perform rebalancing if due
        hours_since_rebalance = (datetime.now() - self.liquidity_pool.last_rebalance).total_seconds() / 3600
        if hours_since_rebalance >= self.liquidity_pool.rebalance_interval_hours:
            rebalance_txns = self.liquidity_pool.rebalance_portfolio()
            results["rebalancing_transactions"] = len(rebalance_txns)

        # Calculate total improvement (simplified)
        current_status = self.liquidity_pool.get_pool_status()
        total_liquidity = current_status["total_liquidity_units"]
        results["total_improvement"] = total_liquidity  # Placeholder for actual improvement calculation

        self._save_state()

        logger.info(f"💰 Liquidity optimization complete: {results['arbitrage_transactions']} arbitrage, {results['rebalancing_transactions']} rebalancing")
        return results

    def get_liquidity_status(self) -> Dict[str, Any]:
        """Get comprehensive liquidity status"""
        return self.liquidity_pool.get_pool_status()

    def add_provider_tokens(self, provider_id: str, token_amount: float):
        """Add tokens to a provider"""
        if provider_id in self.liquidity_pool.providers:
            old_balance = self.liquidity_pool.providers[provider_id].token_balance
            self.liquidity_pool.update_provider_balance(provider_id, old_balance + token_amount)
            self._save_state()
            logger.info(f"✅ Added {token_amount} tokens to {provider_id}")

    def _load_state(self):
        """Load liquidity pool state"""
        if self.pool_file.exists():
            try:
                with open(self.pool_file, 'r') as f:
                    pool_data = json.load(f)

                    # Create LiquidityPool without providers
                    self.liquidity_pool = LiquidityPool(
                        pool_id=pool_data.get('pool_id', 'lumina_ai_liquidity'),
                        total_liquidity_units=pool_data.get('total_liquidity_units', 0.0),
                        total_usd_value=pool_data.get('total_usd_value', 0.0),
                        rebalance_interval_hours=pool_data.get('rebalance_interval_hours', 24),
                        target_allocation_percent=pool_data.get('target_allocation_percent', {})
                    )

                    # Convert last_rebalance date
                    if isinstance(pool_data.get('last_rebalance'), str):
                        self.liquidity_pool.last_rebalance = datetime.fromisoformat(pool_data['last_rebalance'])

                    # Load transaction history
                    if self.transactions_file.exists():
                        with open(self.transactions_file, 'r') as f:
                            txn_data = json.load(f)
                            self.liquidity_pool.transaction_history = [
                                LiquidityTransaction(**txn) for txn in txn_data
                            ]

                    # Reconstruct provider objects from dicts
                    reconstructed_providers = {}
                    for pid, provider_dict in pool_data.get('providers', {}).items():
                        if isinstance(provider_dict, dict):
                            # Convert string datetime back to datetime object
                            if 'last_used' in provider_dict and isinstance(provider_dict['last_used'], str):
                                provider_dict['last_used'] = datetime.fromisoformat(provider_dict['last_used'])

                            provider = ProviderLiquidity(**provider_dict)
                            reconstructed_providers[pid] = provider
                        else:
                            # Already a ProviderLiquidity object
                            reconstructed_providers[pid] = provider_dict

                    self.liquidity_pool.providers = reconstructed_providers

                    logger.info("✅ Liquidity pool state loaded")
            except Exception as e:
                logger.error(f"Failed to load liquidity pool state: {e}")

    def _save_state(self):
        """Save liquidity pool state"""
        try:
            # Prepare data for JSON serialization
            pool_data = {
                'pool_id': self.liquidity_pool.pool_id,
                'total_liquidity_units': self.liquidity_pool.total_liquidity_units,
                'total_usd_value': self.liquidity_pool.total_usd_value,
                'last_rebalance': self.liquidity_pool.last_rebalance.isoformat(),
                'rebalance_interval_hours': self.liquidity_pool.rebalance_interval_hours,
                'target_allocation_percent': self.liquidity_pool.target_allocation_percent
            }

            # Save providers as dicts
            providers_data = {}
            for pid, provider in self.liquidity_pool.providers.items():
                provider_dict = asdict(provider)
                # Convert datetime to string
                if isinstance(provider_dict['last_used'], datetime):
                    provider_dict['last_used'] = provider_dict['last_used'].isoformat()
                providers_data[pid] = provider_dict

            pool_data['providers'] = providers_data

            with open(self.pool_file, 'w') as f:
                json.dump(pool_data, f, indent=2)

            # Save transaction history separately
            txn_data = [asdict(txn) for txn in self.liquidity_pool.transaction_history]
            for txn in txn_data:
                if 'timestamp' in txn and isinstance(txn['timestamp'], datetime):
                    txn['timestamp'] = txn['timestamp'].isoformat()

            with open(self.transactions_file, 'w') as f:
                json.dump(txn_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save liquidity pool state: {e}")


def main():
    """CLI interface for AI Liquidity Manager"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Liquidity Pool Manager")
    parser.add_argument("--status", action="store_true", help="Show liquidity pool status")
    parser.add_argument("--route", nargs=2, metavar=('COMPLEXITY', 'TIER'),
                       help="Route AI request (complexity 0.0-1.0, tier: premium/standard/economy)")
    parser.add_argument("--optimize", action="store_true", help="Run liquidity optimization")
    parser.add_argument("--add-tokens", nargs=2, metavar=('PROVIDER', 'AMOUNT'),
                       help="Add tokens to provider")
    parser.add_argument("--transactions", action="store_true", help="Show recent transactions")

    args = parser.parse_args()

    manager = AILiquidityManager()

    if args.status:
        status = manager.get_liquidity_status()
        print("🤖 AI Liquidity Pool Status")
        print("="*50)
        print(f"Total Liquidity Units: {status['total_liquidity_units']:.0f}")
        print(f"Total USD Value: ${status['total_usd_value']:.2f}")
        print(f"Active Providers: {status['provider_count']}")
        print()

        print("Provider Allocations:")
        for pid, provider in status['providers'].items():
            print(f"  {provider['name']} ({provider['tier']}):")
            print(f"    Balance: {provider['token_balance']:.0f} tokens")
            print(f"    Liquidity: {provider['liquidity_units']:.0f} units ({provider['allocation_percent']}%)")
            print(f"    Value: ${provider['usd_value']:.2f}")
            print(f"    Score: {provider['liquidity_score']:.3f}")
            print()

    elif args.route:
        complexity = float(args.route[0])
        tier = args.route[1] if args.route[1] != 'none' else None

        result = manager.route_ai_request(complexity, tier)
        if result:
            print("🎯 Routing Decision:")
            print(f"  Provider: {result['provider_name']} ({result['provider_id']})")
            print(f"  Confidence: {result['confidence_score']}")
            print(f"  Tier: {result['liquidity_tier']}")
            print(f"  Est. Cost: ${result['estimated_cost_usd']} per 1K tokens")
            print(f"  Reason: {result['routing_reason']}")
        else:
            print("❌ No suitable provider available")

    elif args.optimize:
        results = manager.optimize_liquidity()
        print("💰 Liquidity Optimization Results:")
        print(f"  Arbitrage Transactions: {results['arbitrage_transactions']}")
        print(f"  Rebalancing Transactions: {results['rebalancing_transactions']}")
        print(f"  Total Improvement: {results['total_improvement']}")

    elif args.add_tokens:
        provider_id, amount = args.add_tokens[0], float(args.add_tokens[1])
        manager.add_provider_tokens(provider_id, amount)
        print(f"✅ Added {amount} tokens to {provider_id}")

    elif args.transactions:
        status = manager.get_liquidity_status()
        print("📊 Recent Transactions:")
        for txn in status['recent_transactions'][-5:]:  # Last 5
            print(f"  {txn['timestamp'][:19]} | {txn['type']} | {txn['from']} → {txn['to']} | {txn['amount']:.0f} tokens | ${txn['usd_value']:.2f}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()