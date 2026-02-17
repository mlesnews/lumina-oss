"""
MCP Server Integration for Token Budget Enforcement
Location: .lumina/scripts/python/mcp_budget_server.py
License: MIT / Apache 2.0
Public: Open-Source MCP Budget Enforcement Server

Provides /enforce-budget endpoint for token budget enforcement via MCP.
Integrates with AIRequestTracker for unified token management.
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from token_budget_enforcement import TokenBudgetEnforcer
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

app = FastAPI(title="Token Budget Enforcer", version="1.0.0")
enforcer = TokenBudgetEnforcer()



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class TokenRequest(BaseModel):
    """Request tokens from budget."""

    provider: str
    amount: int
    agent: str = "unknown"
    session_id: str = ""


class TokenResponse(BaseModel):
    """Response from token request."""

    allowed: bool
    message: str
    remaining_budget: int = 0
    percent_used: float = 0.0
    status: str = ""


class BudgetHealthRequest(BaseModel):
    """Check budget health."""

    provider: str


class BudgetHealthResponse(BaseModel):
    """Budget health response."""

    provider: str
    status: str
    limit: int
    used: int
    remaining: int
    percent_used: float
    warning_threshold: int
    critical_threshold: int
    projected_exceeded_at: str = None
    days_remaining: int = None


@app.post("/enforce-budget/request", response_model=TokenResponse)
def request_tokens(req: TokenRequest) -> TokenResponse:
    """Request tokens from budget with enforcement."""
    allowed, message = enforcer.request_tokens(
        req.provider, req.amount, agent=req.agent
    )

    if not allowed:
        raise HTTPException(status_code=429, detail=message)

    budget = enforcer.budgets[req.provider]
    return TokenResponse(
        allowed=True,
        message=message,
        remaining_budget=budget.get_remaining(),
        percent_used=round(budget.get_percent_used() * 100, 1),
        status=budget.get_status().value,
    )


@app.get("/enforce-budget/health/{provider}", response_model=BudgetHealthResponse)
def check_health(provider: str) -> Dict[str, Any]:
    """Check budget health for a provider."""
    health = enforcer.check_budget_health(provider)

    if "error" in health:
        raise HTTPException(status_code=404, detail=health["error"])

    return BudgetHealthResponse(**health)


@app.get("/enforce-budget/health-all")
def check_all_health() -> Dict[str, Any]:
    """Check health of all budgets."""
    return enforcer.get_all_budgets()


@app.post("/enforce-budget/reset/{provider}")
def reset_budget(provider: str) -> Dict[str, str]:
    """Reset budget counter (e.g., monthly reset)."""
    try:
        enforcer.reset_budget(provider)
        return {"message": f"Budget reset for {provider}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/enforce-budget/report")
def get_report() -> Dict[str, str]:
    """Get full budget status report."""
    return {"report": enforcer.get_status_report()}


@app.get("/enforce-budget/status", response_model=Dict[str, Any])
def get_status() -> Dict[str, Any]:
    """Get current budget status snapshot."""
    return {
        "timestamp": datetime.now().isoformat(),
        "budgets": enforcer.get_all_budgets(),
    }


@app.post("/enforce-budget/set-thresholds")
def set_thresholds(
    provider: str, warning: float = 0.8, critical: float = 0.9
) -> Dict[str, str]:
    """Update warning/critical thresholds."""
    try:
        enforcer.set_thresholds(provider, warning, critical)
        return {
            "message": f"Thresholds updated for {provider}",
            "warning": f"{int(warning * 100)}%",
            "critical": f"{int(critical * 100)}%",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Health check endpoint
@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "token-budget-enforcer"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
