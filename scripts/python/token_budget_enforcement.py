"""
Token Budget Enforcement API
Location: .lumina/scripts/python/token_budget_enforcement.py
License: MIT / Apache 2.0
Public: Open-Source Token Budget Management Framework

Implements spending limits and warning thresholds for token budgets.
Prevents overspending and alerts on budget health.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class BudgetStatus(str, Enum):
    """Status of budget health."""

    HEALTHY = "healthy"  # 0-70%
    WARNING = "warning"  # 70-90%
    CRITICAL = "critical"  # 90-99%
    EXCEEDED = "exceeded"  # 100%+


@dataclass
class TokenBudget:
    """Token budget for a provider/agent."""

    name: str
    limit: int
    used: int = 0
    reset_date: datetime = field(default_factory=datetime.now)
    warning_threshold: float = 0.8  # Warn at 80%
    critical_threshold: float = 0.9  # Critical at 90%

    def get_remaining(self) -> int:
        """Get remaining tokens."""
        return max(0, self.limit - self.used)

    def get_percent_used(self) -> float:
        """Get percentage of budget used (0.0-1.0)."""
        if self.limit == 0:
            return 0.0
        return self.used / self.limit

    def get_status(self) -> BudgetStatus:
        """Get current budget status."""
        percent = self.get_percent_used()
        if percent >= 1.0:
            return BudgetStatus.EXCEEDED
        elif percent >= self.critical_threshold:
            return BudgetStatus.CRITICAL
        elif percent >= self.warning_threshold:
            return BudgetStatus.WARNING
        else:
            return BudgetStatus.HEALTHY

    def get_projected_exceeded_date(self) -> Optional[datetime]:
        """Project when budget will be exceeded (linear extrapolation)."""
        if self.used == 0:
            return None
        elapsed = datetime.now() - self.reset_date
        if elapsed.total_seconds() == 0:
            return None
        rate = self.used / elapsed.total_seconds()  # tokens/second
        remaining = self.get_remaining()
        if rate <= 0:
            return None
        seconds_until_exceeded = remaining / rate
        return datetime.now() + timedelta(seconds=seconds_until_exceeded)


class TokenBudgetEnforcer:
    """Enforce token budgets with warnings and hard limits."""

    def __init__(
        self, config_path: str = ".lumina/config/ai_token_request_tracker.json"
    ):
        """Initialize enforcer with budget config."""
        self.config_path = Path(config_path)
        self.budgets: Dict[str, TokenBudget] = {}
        self.load_config()

    def load_config(self):
        try:
            """Load budget configuration from file."""
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config not found: {self.config_path}")

            with open(self.config_path) as f:
                config = json.load(f)

            budget_config = config.get("budget", {})
            for provider_name, limit in budget_config.items():
                self.budgets[provider_name] = TokenBudget(
                    name=provider_name,
                    limit=limit,
                    warning_threshold=0.8,
                    critical_threshold=0.9,
                )

        except Exception as e:
            self.logger.error(f"Error in load_config: {e}", exc_info=True)
            raise
    def request_tokens(
        self, provider: str, amount: int, agent: str = "unknown"
    ) -> Tuple[bool, str]:
        """
        Request tokens from budget.

        Returns:
            (allowed, message) - allowed=True if request granted
        """
        if provider not in self.budgets:
            return False, f"Provider '{provider}' not configured"

        budget = self.budgets[provider]

        # Check if adding tokens would exceed budget
        new_total = budget.used + amount
        if new_total > budget.limit:
            return False, (
                f"Token request DENIED for {agent}. "
                f"Would exceed {provider} budget: "
                f"{budget.used} + {amount} > {budget.limit}"
            )

        # Check if adding tokens would trigger warning
        new_percent = new_total / budget.limit
        if new_percent >= budget.critical_threshold:
            status = "🔴 CRITICAL"
        elif new_percent >= budget.warning_threshold:
            status = "🟡 WARNING"
        else:
            status = "🟢 HEALTHY"

        # Grant the request
        budget.used = new_total
        message = (
            f"{status}: {agent} allocated {amount} tokens from {provider}. "
            f"Remaining: {budget.get_remaining()} "
            f"({100 - int(new_percent * 100)}%)"
        )
        return True, message

    def check_budget_health(self, provider: str) -> Dict[str, any]:
        """Check health of a budget."""
        if provider not in self.budgets:
            return {"error": f"Provider '{provider}' not configured"}

        budget = self.budgets[provider]
        status = budget.get_status()
        projected_exceeded = budget.get_projected_exceeded_date()

        return {
            "provider": provider,
            "status": status.value,
            "limit": budget.limit,
            "used": budget.used,
            "remaining": budget.get_remaining(),
            "percent_used": round(budget.get_percent_used() * 100, 1),
            "warning_threshold": int(budget.warning_threshold * 100),
            "critical_threshold": int(budget.critical_threshold * 100),
            "projected_exceeded_at": projected_exceeded.isoformat()
            if projected_exceeded
            else None,
            "days_remaining": (
                (projected_exceeded - datetime.now()).days
                if projected_exceeded
                else None
            ),
        }

    def get_all_budgets(self) -> Dict[str, Dict]:
        """Get health of all budgets."""
        return {name: self.check_budget_health(name) for name in self.budgets}

    def set_thresholds(self, provider: str, warning: float, critical: float):
        """Update warning/critical thresholds for a provider."""
        if provider not in self.budgets:
            raise ValueError(f"Provider '{provider}' not configured")
        self.budgets[provider].warning_threshold = warning
        self.budgets[provider].critical_threshold = critical

    def reset_budget(self, provider: str):
        """Reset budget counters (e.g., monthly reset)."""
        if provider not in self.budgets:
            raise ValueError(f"Provider '{provider}' not configured")
        self.budgets[provider].used = 0
        self.budgets[provider].reset_date = datetime.now()

    def get_status_report(self) -> str:
        """Generate human-readable budget status report."""
        lines = [
            "=" * 60,
            "TOKEN BUDGET STATUS REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
        ]

        for name, budget in self.budgets.items():
            health = self.check_budget_health(name)
            status = health["status"]

            if status == "healthy":
                indicator = "🟢"
            elif status == "warning":
                indicator = "🟡"
            elif status == "critical":
                indicator = "🔴"
            else:
                indicator = "❌"

            lines.extend(
                [
                    f"{indicator} {name.upper()}",
                    f"   Used: {budget.used:,} / {budget.limit:,} tokens",
                    (
                        f"   Remaining: {budget.get_remaining():,} "
                        f"({100 - health['percent_used']:.1f}%)"
                    ),
                    f"   Status: {status.upper()}",
                    (
                        f"   Projected exceeded: "
                        f"{health['projected_exceeded_at'] or 'Never'}"
                    ),
                ]
            )

            if health.get("days_remaining"):
                lines.append(f"   Days remaining: {health['days_remaining']}")

            lines.append("")

        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    enforcer = TokenBudgetEnforcer()

    # Check single budget
    health = enforcer.check_budget_health("github_copilot")
    status = health["status"]
    percent = health["percent_used"]
    print(f"GitHub Copilot: {status} ({percent}% used)")

    # Request tokens
    allowed, msg = enforcer.request_tokens("github_copilot", 5000, agent="kilo_code")
    print(msg)

    # Request more tokens
    for i in range(15):
        allowed, msg = enforcer.request_tokens("github_copilot", 5000, agent="test")
        print(msg)
        if not allowed:
            break

    # Print full report
    print("\n" + enforcer.get_status_report())
