"""
API budget circuit breaker.

Monitors cumulative API spend from a JSONL cost log and transitions between
OPERATIONAL / WARNING / HALT states based on month-to-date burn rate.

Pattern extracted from production: api_budget_circuit_breaker.py

Example:
    guard = BudgetGuard(monthly_budget=200.0)
    status = guard.check(cost_log_path=Path("~/logs/costs.jsonl"))
    print(f"{status['state']}: ${status['mtd_spend']:.2f} / ${status['budget']}")
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BudgetGuard:
    """
    Month-to-date budget monitor with three states.

    States:
        OPERATIONAL: Spend < warn_pct of budget
        WARNING: Spend between warn_pct and halt_pct
        HALT: Spend > halt_pct — stop all paid API calls

    Args:
        monthly_budget: Monthly budget in USD.
        warn_pct: Percentage threshold for WARNING (default 0.80).
        halt_pct: Percentage threshold for HALT (default 0.95).
    """

    def __init__(
        self,
        monthly_budget: float = 200.0,
        warn_pct: float = 0.80,
        halt_pct: float = 0.95,
    ):
        self.monthly_budget = monthly_budget
        self.warn_pct = warn_pct
        self.halt_pct = halt_pct

    def check(
        self,
        cost_log_path: Optional[Path] = None,
        entries: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate MTD spend and return budget state.

        Provide either cost_log_path (JSONL file) or entries (list of dicts
        with 'timestamp' and 'cost_usd' keys).

        Returns dict with: state, mtd_spend, budget, burn_pct,
        days_remaining, projected_monthly, updated_at.
        """
        now = datetime.now(tz=timezone.utc)
        days_elapsed = max(now.day, 1)
        days_in_month = self._days_in_month(now.year, now.month)
        days_remaining = days_in_month - now.day

        # Sum MTD spend
        mtd_spend = 0.0
        if entries is not None:
            for entry in entries:
                ts_str = entry.get("timestamp", "")
                try:
                    ts = datetime.fromisoformat(ts_str)
                    if ts.year == now.year and ts.month == now.month:
                        mtd_spend += float(entry.get("cost_usd", 0.0))
                except (ValueError, TypeError):
                    continue
        elif cost_log_path and cost_log_path.exists():
            try:
                with cost_log_path.open() as fh:
                    for raw in fh:
                        raw = raw.strip()
                        if not raw:
                            continue
                        try:
                            entry = json.loads(raw)
                            ts = datetime.fromisoformat(entry.get("timestamp", ""))
                            if ts.year == now.year and ts.month == now.month:
                                mtd_spend += float(entry.get("cost_usd", 0.0))
                        except (json.JSONDecodeError, ValueError, KeyError):
                            continue
            except OSError as exc:
                logger.warning("Could not read cost log: %s", exc)

        projected = (mtd_spend / days_elapsed) * days_in_month
        burn_pct = mtd_spend / self.monthly_budget if self.monthly_budget > 0 else 0

        if burn_pct >= self.halt_pct:
            state = "HALT"
        elif burn_pct >= self.warn_pct:
            state = "WARNING"
        else:
            state = "OPERATIONAL"

        return {
            "state": state,
            "mtd_spend": round(mtd_spend, 6),
            "budget": self.monthly_budget,
            "burn_pct": round(burn_pct, 6),
            "updated_at": now.isoformat(),
            "days_remaining": days_remaining,
            "projected_monthly": round(projected, 6),
        }

    @staticmethod
    def _days_in_month(year: int, month: int) -> int:
        if month == 12:
            nxt = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            nxt = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        return (nxt - datetime(year, month, 1, tzinfo=timezone.utc)).days
