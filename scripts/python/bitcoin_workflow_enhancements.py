#!/usr/bin/env python3
"""
Bitcoin Workflow Enhancements
@PEAK Optimized | @MAX Workflow Integration

Advanced features for Bitcoin financial workflows:
- Automated rebalancing
- Performance tracking
- Alert system
- Compliance automation
- Dashboard data generation

Author: <COMPANY_NAME> LLC
Date: 2025-01-27
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from bitcoin_financial_workflows import (
        BitcoinWorkflowSystem,
        ClientProfile,
        RiskTolerance,
        BitcoinAllocation,
        RiskMetrics
    )
    BITCOIN_WORKFLOWS_AVAILABLE = True
except ImportError:
    BITCOIN_WORKFLOWS_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BitcoinEnhancements")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class RebalancingTrigger(Enum):
    """Rebalancing trigger types"""
    ALLOCATION_EXCEEDED = "allocation_exceeded"
    ALLOCATION_DROPPED = "allocation_dropped"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    VOLATILITY_SPIKE = "volatility_spike"


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    client_id: str
    period_start: datetime
    period_end: datetime
    initial_value: float
    current_value: float
    bitcoin_return: float
    portfolio_return: float
    allocation_start_pct: float
    allocation_end_pct: float
    correlation: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    volatility: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["period_start"] = self.period_start.isoformat()
        data["period_end"] = self.period_end.isoformat()
        return data


@dataclass
class Alert:
    """System alert"""
    alert_id: str
    client_id: str
    alert_level: AlertLevel
    alert_type: str
    message: str
    timestamp: datetime
    acknowledged: bool = False
    action_taken: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["alert_level"] = self.alert_level.value
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class RebalancingRecommendation:
    """Rebalancing recommendation"""
    client_id: str
    trigger: RebalancingTrigger
    current_allocation_pct: float
    target_allocation_pct: float
    recommended_action: str
    amount_to_adjust: float
    rationale: str
    urgency: str  # "low", "medium", "high"
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["trigger"] = self.trigger.value
        data["timestamp"] = self.timestamp.isoformat()
        return data


class BitcoinWorkflowEnhancements:
    """
    @PEAK: Bitcoin Workflow Enhancements

    Advanced features for Bitcoin financial workflows with maximum
    automation and optimization.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize enhancements system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "bitcoin_workflows"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not BITCOIN_WORKFLOWS_AVAILABLE:
            raise ImportError("Bitcoin workflows not available")

        self.bitcoin_system = BitcoinWorkflowSystem(self.project_root)
        self.alerts: List[Alert] = []
        self.rebalancing_history: List[RebalancingRecommendation] = []

        logger.info("Bitcoin Workflow Enhancements initialized")

    def calculate_performance(
        self,
        client_id: str,
        period_start: datetime,
        period_end: datetime,
        initial_bitcoin_value: float,
        current_bitcoin_value: float,
        initial_portfolio_value: float,
        current_portfolio_value: float,
        initial_allocation_pct: float,
        current_allocation_pct: float
    ) -> PerformanceMetrics:
        """
        @PEAK: Performance Calculation

        Calculate performance metrics for Bitcoin allocation.

        Args:
            client_id: Client identifier
            period_start: Period start date
            period_end: Period end date
            initial_bitcoin_value: Initial Bitcoin position value
            current_bitcoin_value: Current Bitcoin position value
            initial_portfolio_value: Initial total portfolio value
            current_portfolio_value: Current total portfolio value
            initial_allocation_pct: Initial allocation percentage
            current_allocation_pct: Current allocation percentage

        Returns:
            Performance metrics
        """
        bitcoin_return = (current_bitcoin_value - initial_bitcoin_value) / initial_bitcoin_value
        portfolio_return = (current_portfolio_value - initial_portfolio_value) / initial_portfolio_value

        metrics = PerformanceMetrics(
            client_id=client_id,
            period_start=period_start,
            period_end=period_end,
            initial_value=initial_bitcoin_value,
            current_value=current_bitcoin_value,
            bitcoin_return=bitcoin_return,
            portfolio_return=portfolio_return,
            allocation_start_pct=initial_allocation_pct,
            allocation_end_pct=current_allocation_pct
        )

        # Save metrics
        metrics_file = self.data_dir / f"performance_{client_id}_{period_end.strftime('%Y%m%d')}.json"
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(metrics.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Performance calculated for {client_id}: Bitcoin {bitcoin_return*100:.2f}%, Portfolio {portfolio_return*100:.2f}%")
        return metrics

    def check_rebalancing_needed(
        self,
        client_id: str,
        current_allocation_pct: float,
        target_allocation_pct: float,
        tolerance: float = 0.005  # 0.5% tolerance
    ) -> Optional[RebalancingRecommendation]:
        """
        @PEAK: Rebalancing Check

        Check if rebalancing is needed based on allocation drift.

        Args:
            client_id: Client identifier
            current_allocation_pct: Current allocation percentage
            target_allocation_pct: Target allocation percentage
            tolerance: Tolerance threshold (default 0.5%)

        Returns:
            Rebalancing recommendation if needed, None otherwise
        """
        drift = abs(current_allocation_pct - target_allocation_pct)

        if drift <= tolerance:
            return None

        # Determine trigger type
        if current_allocation_pct > target_allocation_pct * 1.2:
            trigger = RebalancingTrigger.ALLOCATION_EXCEEDED
            action = "reduce"
            urgency = "high"
        elif current_allocation_pct < target_allocation_pct * 0.8:
            trigger = RebalancingTrigger.ALLOCATION_DROPPED
            action = "increase"
            urgency = "medium"
        else:
            trigger = RebalancingTrigger.SCHEDULED
            action = "adjust"
            urgency = "low"

        # Calculate adjustment amount
        adjustment_pct = target_allocation_pct - current_allocation_pct

        recommendation = RebalancingRecommendation(
            client_id=client_id,
            trigger=trigger,
            current_allocation_pct=current_allocation_pct,
            target_allocation_pct=target_allocation_pct,
            recommended_action=action,
            amount_to_adjust=adjustment_pct,
            rationale=(
                f"Allocation drift of {drift*100:.2f}% detected. "
                f"Current: {current_allocation_pct*100:.2f}%, Target: {target_allocation_pct*100:.2f}%. "
                f"Recommend {action} allocation by {abs(adjustment_pct)*100:.2f}%."
            ),
            urgency=urgency
        )

        # Save recommendation
        self.rebalancing_history.append(recommendation)
        rec_file = self.data_dir / f"rebalancing_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(rec_file, "w", encoding="utf-8") as f:
            json.dump(recommendation.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Rebalancing recommendation for {client_id}: {action} by {abs(adjustment_pct)*100:.2f}%")
        return recommendation

    def generate_alert(
        self,
        client_id: str,
        alert_level: AlertLevel,
        alert_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """
        @PEAK: Alert Generation

        Generate system alert for Bitcoin workflow.

        Args:
            client_id: Client identifier
            alert_level: Alert severity level
            alert_type: Type of alert
            message: Alert message
            metadata: Optional metadata

        Returns:
            Generated alert
        """
        alert = Alert(
            alert_id=f"alert_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            client_id=client_id,
            alert_level=alert_level,
            alert_type=alert_type,
            message=message,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )

        self.alerts.append(alert)

        # Save alert
        alert_file = self.data_dir / f"alerts" / f"{alert.alert_id}.json"
        alert_file.parent.mkdir(exist_ok=True)
        with open(alert_file, "w", encoding="utf-8") as f:
            json.dump(alert.to_dict(), f, indent=2, ensure_ascii=False)

        logger.warning(f"Alert generated for {client_id}: {alert_level.value} - {message}")
        return alert

    def get_dashboard_data(
        self,
        client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        @PEAK: Dashboard Data Generation

        Generate dashboard data for monitoring and visualization.

        Args:
            client_id: Optional client ID to filter, None for all clients

        Returns:
            Dashboard data dictionary
        """
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "clients": {},
            "summary": {
                "total_clients": 0,
                "total_bitcoin_allocation": 0.0,
                "total_alerts": 0,
                "pending_rebalancing": 0
            }
        }

        # Load client data
        profile_files = list(self.data_dir.glob("profile_*.json"))
        for profile_file in profile_files:
            with open(profile_file, "r", encoding="utf-8") as f:
                profile_data = json.load(f)

            cid = profile_data.get("client_id")
            if client_id and cid != client_id:
                continue

            # Load allocation
            allocation_file = self.data_dir / f"allocation_{cid}.json"
            allocation_data = {}
            if allocation_file.exists():
                with open(allocation_file, "r", encoding="utf-8") as f:
                    allocation_data = json.load(f)

            # Count alerts
            alert_count = len([a for a in self.alerts if a.client_id == cid and not a.acknowledged])

            dashboard["clients"][cid] = {
                "profile": profile_data,
                "allocation": allocation_data,
                "alerts": alert_count
            }

        dashboard["summary"]["total_clients"] = len(dashboard["clients"])
        dashboard["summary"]["total_alerts"] = len([a for a in self.alerts if not a.acknowledged])
        dashboard["summary"]["pending_rebalancing"] = len([
            r for r in self.rebalancing_history
            if r.urgency in ["high", "medium"]
        ])

        return dashboard

    def automate_compliance_check(
        self,
        client_id: str,
        profile: ClientProfile
    ) -> Dict[str, Any]:
        """
        @PEAK: Automated Compliance Check

        Perform automated compliance checks for Bitcoin allocation.

        Args:
            client_id: Client identifier
            profile: Client profile

        Returns:
            Compliance check results
        """
        checks = {
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "status": "compliant",
            "issues": []
        }

        # Check 1: Suitability
        suitability_status, rationale, recommendations = self.bitcoin_system.assess_suitability(profile)
        checks["checks"]["suitability"] = {
            "status": suitability_status.value,
            "rationale": rationale,
            "compliant": suitability_status.value != "not_suitable"
        }
        if suitability_status.value == "not_suitable":
            checks["status"] = "non_compliant"
            checks["issues"].append("Client not suitable for Bitcoin allocation")

        # Check 2: Regulatory restrictions
        if profile.regulatory_restrictions:
            checks["checks"]["regulatory"] = {
                "status": "restricted",
                "restrictions": profile.regulatory_restrictions,
                "compliant": False
            }
            checks["status"] = "non_compliant"
            checks["issues"].extend(profile.regulatory_restrictions)

        # Check 3: Documentation
        profile_file = self.data_dir / f"profile_{client_id}.json"
        allocation_file = self.data_dir / f"allocation_{client_id}.json"
        checks["checks"]["documentation"] = {
            "profile_exists": profile_file.exists(),
            "allocation_exists": allocation_file.exists(),
            "compliant": profile_file.exists() and allocation_file.exists()
        }
        if not (profile_file.exists() and allocation_file.exists()):
            checks["status"] = "non_compliant"
            checks["issues"].append("Missing required documentation")

        # Save compliance check
        compliance_file = self.data_dir / f"compliance_{client_id}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(compliance_file, "w", encoding="utf-8") as f:
            json.dump(checks, f, indent=2, ensure_ascii=False)

        logger.info(f"Compliance check for {client_id}: {checks['status']}")
        return checks


def main() -> int:
    try:
        """Main entry point for testing"""
        enhancements = BitcoinWorkflowEnhancements()

        # Example: Performance calculation
        from datetime import datetime, timedelta
        period_end = datetime.now()
        period_start = period_end - timedelta(days=90)

        metrics = enhancements.calculate_performance(
            client_id="CLIENT_001",
            period_start=period_start,
            period_end=period_end,
            initial_bitcoin_value=25000.0,
            current_bitcoin_value=30000.0,
            initial_portfolio_value=1000000.0,
            current_portfolio_value=1050000.0,
            initial_allocation_pct=0.025,
            current_allocation_pct=0.0286
        )

        print(json.dumps(metrics.to_dict(), indent=2, ensure_ascii=False))

        # Example: Rebalancing check
        rec = enhancements.check_rebalancing_needed(
            client_id="CLIENT_001",
            current_allocation_pct=0.035,
            target_allocation_pct=0.025
        )

        if rec:
            print("\nRebalancing Recommendation:")
            print(json.dumps(rec.to_dict(), indent=2, ensure_ascii=False))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import sys



    sys.exit(main())