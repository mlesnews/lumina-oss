#!/usr/bin/env python3
"""
Trading Skeleton Demo — Molecule architecture for automated trading.

This is a sanitized reference implementation showing how Lumina AIOS
primitives compose into a trading system. No real API keys or live trading.

Run: python examples/trading_skeleton/demo.py
"""

from lumina.aios import (
    HealthAggregator,
    Molecule,
    MoleculeRunner,
    MemoryManager,
    MemoryTier,
)
from lumina.safety import CircuitBreaker, Level
from lumina.workflow import DecisionEngine


def main():
    print("=== Trading Skeleton Demo ===\n")

    # 1. Initialize safety layer
    cb = CircuitBreaker(thresholds={
        Level.YELLOW: {"daily_loss_pct": 2.0},
        Level.ORANGE: {"daily_loss_pct": 5.0},
        Level.RED: {"daily_loss_pct": 10.0},
    })

    # 2. Initialize memory
    memory = MemoryManager(max_blocks=100)
    memory.store("regime", "trending_up", MemoryTier.HIGH)
    memory.store("last_signal", None, MemoryTier.MEDIUM)

    # 3. Initialize health monitoring
    health = HealthAggregator(dimensions={
        "signal_quality": 0.30,
        "circuit_breaker": 0.25,
        "regime_clarity": 0.25,
        "track_record": 0.20,
    })

    # 4. Initialize decisioning
    decision = DecisionEngine(threshold=0.6)

    # 5. Define trading molecules
    def trend_trigger(ctx):
        """Buy when price breaks above 20-day high."""
        return ctx.get("price", 0) > ctx.get("high_20d", float("inf"))

    def trend_action(ctx):
        """Execute buy signal."""
        return {
            "signal": "BUY",
            "pair": ctx["pair"],
            "price": ctx["price"],
            "reason": "20-day breakout",
        }

    def loss_stopper(ctx):
        """Stop if circuit breaker is not green."""
        level, _ = cb.check({"daily_loss_pct": ctx.get("daily_loss_pct", 0)})
        return level >= Level.ORANGE

    breakout_mol = Molecule(
        name="trend_breakout",
        trigger=trend_trigger,
        action=trend_action,
        stopper=loss_stopper,
    )

    mean_revert_mol = Molecule(
        name="mean_reversion",
        trigger=lambda ctx: ctx.get("rsi", 50) < 30,
        action=lambda ctx: {"signal": "BUY", "pair": ctx["pair"], "reason": "RSI oversold"},
        stopper=loss_stopper,
    )

    # 6. Run simulation
    runner = MoleculeRunner()

    market_data = [
        {"pair": "BTC/USDT", "price": 68000, "high_20d": 65000, "rsi": 65, "daily_loss_pct": 0.5},
        {"pair": "ETH/USDT", "price": 3200, "high_20d": 3500, "rsi": 28, "daily_loss_pct": 1.0},
        {"pair": "SOL/USDT", "price": 150, "high_20d": 140, "rsi": 55, "daily_loss_pct": 6.0},
    ]

    print("Running molecules against market data:\n")
    for data in market_data:
        results = runner.evaluate_all([breakout_mol, mean_revert_mol], data)
        for result in results:
            if result.output:
                print(f"  {result.molecule_name:20s} -> {result.state.name:10s} {result.output}")
            elif result.stopped_by:
                print(f"  {result.molecule_name:20s} -> STOPPED ({result.stopped_by})")
            else:
                print(f"  {result.molecule_name:20s} -> {result.state.name}")

    # 7. Score health
    print("\nHealth Assessment:")
    health.score("signal_quality", 0.7, f"{len(runner.history)} signals evaluated")
    cb_level, _ = cb.check({"daily_loss_pct": 1.0})
    health.score("circuit_breaker", 1.0 if cb_level == Level.GREEN else 0.5, cb_level.name)
    health.score("regime_clarity", 0.8, memory.recall("regime"))
    health.score("track_record", 0.0, "No closed trades yet")

    report = health.evaluate()
    print(f"  Readiness: {report.score_pct:.1f}% [{report.label}]")
    print(f"  {report.recommendation}")

    # 8. Decision gate
    print("\nDecision Gate:")
    decision.add_context("signals", "3 pairs evaluated, 2 signals generated")
    decision.add_context("safety", f"Circuit breaker: {cb_level.name}")
    decision.add_context("regime", f"Market regime: {memory.recall('regime')}")

    result = decision.decide("Should we go live with this strategy?")
    print(f"  Score: {result.score:.2f} (threshold: {result.threshold})")
    print(f"  Decision: {result.decision}")
    print(f"  {result.rationale}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
