"""
AIQ + Triage + JediCouncil Integration Module
Location: .lumina/scripts/python/aiq_triage_jedi.py
License: MIT / Apache 2.0
Public: Open-Source Framework for issue routing

Handles MCP calls to /triage, /aiq, and JediCouncil escalation.
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

import httpx
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class TriagePriority(str, Enum):
    """Triage severity levels for escalation routing."""

    IMMEDIATE = "Immediate"
    URGENT = "Urgent"
    ELEVATED = "Elevated"
    ROUTINE = "Routine"


@dataclass
class TriageResult:
    """Result from /triage endpoint."""

    category: str
    priority: str
    notes: Optional[str] = None


@dataclass
class AIQResult:
    """Result from /aiq consensus endpoint."""

    selected: Dict[str, Any]
    scores: Dict[str, float]


class AIQTriageRouter:
    """Route issues using Triage + AIQ + JediCouncil escalation."""

    def __init__(self, mcp_server_url: str = "http://localhost:8000"):
        """Initialize router with MCP server endpoint."""
        self.mcp_server_url = mcp_server_url
        self.client = httpx.Client(timeout=30.0)

    def triage_issue(self, text: str, severity: Optional[str] = None) -> TriageResult:
        """Call /triage endpoint to classify issue severity."""
        payload = {"text": text, "severity": severity, "metadata": {}}
        response = self.client.post(f"{self.mcp_server_url}/triage", json=payload)
        response.raise_for_status()
        data = response.json()
        return TriageResult(**data)

    def run_aiq_consensus(self, candidates: list, quorum: int = 3) -> AIQResult:
        """Run /aiq consensus across candidate solutions."""
        payload = {"candidates": candidates, "quorum": quorum}
        response = self.client.post(f"{self.mcp_server_url}/aiq", json=payload)
        response.raise_for_status()
        data = response.json()
        return AIQResult(**data)

    def escalate_to_jedi_council(
        self, issue_id: str, triage_result: TriageResult, aiq_result: AIQResult
    ) -> Dict[str, Any]:
        """Escalate high-priority issue to JediCouncil for human review."""
        escalation_payload = {
            "issue_id": issue_id,
            "triage_category": triage_result.category,
            "triage_priority": triage_result.priority,
            "aiq_winner": aiq_result.selected,
            "aiq_scores": aiq_result.scores,
            "escalation_reason": f"Priority: {triage_result.priority}",
            "requires_human_review": True,
        }
        response = self.client.post(
            f"{self.mcp_server_url}/r5", json=escalation_payload
        )
        response.raise_for_status()
        return response.json()

    def route_issue(
        self,
        issue_id: str,
        issue_text: str,
        candidate_solutions: list,
        severity: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        End-to-end issue routing: Triage → AIQ → Escalate if needed.

        Args:
            issue_id: Unique issue identifier
            issue_text: Issue description/content
            candidate_solutions: List of candidate solutions
                with 'id' and 'content' keys
            severity: Optional initial severity hint

        Returns:
            Routing decision with selected solution and escalation status
        """
        # Step 1: Triage the issue
        triage = self.triage_issue(issue_text, severity)

        # Step 2: Run AIQ consensus
        aiq = self.run_aiq_consensus(candidate_solutions, quorum=3)

        # Step 3: Escalate if high-priority
        escalation = None
        if triage.priority in [
            TriagePriority.IMMEDIATE.value,
            TriagePriority.URGENT.value,
        ]:
            escalation = self.escalate_to_jedi_council(issue_id, triage, aiq)

        return {
            "issue_id": issue_id,
            "triage": {
                "category": triage.category,
                "priority": triage.priority,
                "notes": triage.notes,
            },
            "aiq": {
                "selected_solution_id": aiq.selected.get("id"),
                "scores": aiq.scores,
            },
            "escalation": escalation,
            "requires_jedi_review": escalation is not None,
        }

    def close(self):
        """Close HTTP client connection."""
        self.client.close()


# Example usage (for testing)
if __name__ == "__main__":
    router = AIQTriageRouter(mcp_server_url="http://localhost:8000")

    # Example: Route a GitHub issue
    result = router.route_issue(
        issue_id="GH-1234",
        issue_text="Critical: System failure on database connection",
        candidate_solutions=[
            {
                "id": "sol_1",
                "content": (
                    "Comprehensive solution with connection pooling, "
                    "retry logic, and monitoring"
                ),
            },
            {"id": "sol_2", "content": "Simple fix"},
        ],
        severity="critical",
    )

    print(json.dumps(result, indent=2))
    router.close()
    router.close()
    router.close()
