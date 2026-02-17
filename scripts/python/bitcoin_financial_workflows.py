#!/usr/bin/env python3
"""
Bitcoin Financial Services Workflows
@PEAK Optimized | @MAX Workflow Integration

Comprehensive workflow system for integrating Bitcoin into financial services
with proper risk management, compliance, and client suitability frameworks.

Features:
- Client suitability assessment
- Portfolio allocation models
- Risk management workflows
- Compliance monitoring
- Performance tracking
- Integration with JARVIS/droid system

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
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BitcoinWorkflows")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class RiskTolerance(Enum):
    """Client risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class AllocationModel(Enum):
    """Bitcoin allocation models"""
    CONSERVATIVE = "conservative"  # 1%
    MODERATE = "moderate"  # 2-3%
    AGGRESSIVE = "aggressive"  # 5%


class SuitabilityStatus(Enum):
    """Client suitability status"""
    SUITABLE = "suitable"
    NOT_SUITABLE = "not_suitable"
    CONDITIONAL = "conditional"  # Requires additional education/qualification


@dataclass
class ClientProfile:
    """Client profile for Bitcoin suitability assessment"""
    client_id: str
    risk_tolerance: RiskTolerance
    investment_horizon_years: int
    bitcoin_knowledge_level: int  # 1-5 scale
    financial_sophistication: str  # "accredited", "institutional", "retail"
    regulatory_restrictions: List[str] = field(default_factory=list)
    current_portfolio_value: Optional[float] = None
    max_drawdown_tolerance: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["risk_tolerance"] = self.risk_tolerance.value
        return data


@dataclass
class BitcoinAllocation:
    """Bitcoin allocation recommendation"""
    client_id: str
    allocation_percentage: float
    allocation_model: AllocationModel
    recommended_amount: Optional[float] = None
    dollar_cost_averaging: bool = True
    dca_period_months: int = 12
    rebalancing_frequency: str = "quarterly"
    custody_recommendation: str = "custodial"  # "self" or "custodial"
    rationale: str = ""
    risk_warnings: List[str] = field(default_factory=list)
    created: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["allocation_model"] = self.allocation_model.value
        data["created"] = self.created.isoformat()
        return data


@dataclass
class RiskMetrics:
    """Risk metrics for Bitcoin position"""
    client_id: str
    current_allocation_percentage: float
    position_value: float
    max_allowed_percentage: float
    drawdown_percentage: Optional[float] = None
    volatility_30d: Optional[float] = None
    correlation_with_portfolio: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.now)
    alerts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["last_updated"] = self.last_updated.isoformat()
        return data


class BitcoinWorkflowSystem:
    """
    @PEAK: Bitcoin Financial Services Workflow System

    Nutrient-dense, small-footprint system for Bitcoin integration
    into financial services with maximum workflow efficiency.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Bitcoin workflow system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "bitcoin_workflows"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Allocation model mappings
        self.allocation_models = {
            AllocationModel.CONSERVATIVE: 0.01,  # 1%
            AllocationModel.MODERATE: 0.025,  # 2.5% (midpoint)
            AllocationModel.AGGRESSIVE: 0.05,  # 5%
        }

        logger.info("Bitcoin Workflow System initialized")

    def assess_suitability(self, profile: ClientProfile) -> Tuple[SuitabilityStatus, str, List[str]]:
        """
        @PEAK: Client Suitability Assessment

        Assess client suitability for Bitcoin allocation based on
        risk tolerance, knowledge, horizon, and regulatory factors.

        Args:
            profile: Client profile to assess

        Returns:
            Tuple of (status, rationale, recommendations)
        """
        issues = []
        recommendations = []

        # Risk tolerance check
        if profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            issues.append("Low risk tolerance may not be suitable for Bitcoin's volatility")
            recommendations.append("Consider conservative 1% allocation only")

        # Investment horizon check
        if profile.investment_horizon_years < 5:
            issues.append("Short investment horizon (<5 years) increases risk")
            recommendations.append("Recommend minimum 5-year investment horizon")

        # Knowledge level check
        if profile.bitcoin_knowledge_level < 3:
            issues.append("Low Bitcoin knowledge level requires education")
            recommendations.append("Provide comprehensive Bitcoin education before allocation")

        # Regulatory restrictions check
        if profile.regulatory_restrictions:
            issues.append(f"Regulatory restrictions: {', '.join(profile.regulatory_restrictions)}")
            recommendations.append("Review regulatory compliance before proceeding")

        # Financial sophistication check
        if profile.financial_sophistication == "retail" and profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            issues.append("Retail client with conservative risk tolerance may not be suitable")
            recommendations.append("Consider suitability carefully for retail conservative clients")

        # Determine status
        if len(issues) == 0:
            status = SuitabilityStatus.SUITABLE
            rationale = "Client meets all suitability criteria for Bitcoin allocation"
        elif len(issues) <= 2 and all(
            "education" in issue.lower() or "regulatory" in issue.lower()
            for issue in issues
        ):
            status = SuitabilityStatus.CONDITIONAL
            rationale = "Client suitable pending education and/or regulatory compliance"
        else:
            status = SuitabilityStatus.NOT_SUITABLE
            rationale = "Client does not meet suitability criteria for Bitcoin allocation"

        logger.info(f"Suitability assessment for {profile.client_id}: {status.value}")
        return status, rationale, recommendations

    def calculate_allocation(
        self,
        profile: ClientProfile,
        portfolio_value: float,
        custom_percentage: Optional[float] = None
    ) -> BitcoinAllocation:
        """
        @PEAK: Portfolio Allocation Calculation

        Calculate recommended Bitcoin allocation based on client profile
        and portfolio value.

        Args:
            profile: Client profile
            portfolio_value: Total portfolio value
            custom_percentage: Optional custom allocation percentage

        Returns:
            Bitcoin allocation recommendation
        """
        # Determine allocation model based on risk tolerance
        if profile.risk_tolerance == RiskTolerance.CONSERVATIVE:
            model = AllocationModel.CONSERVATIVE
        elif profile.risk_tolerance == RiskTolerance.AGGRESSIVE:
            model = AllocationModel.AGGRESSIVE
        else:
            model = AllocationModel.MODERATE

        # Use custom percentage if provided
        if custom_percentage is not None:
            allocation_pct = custom_percentage
            # Determine closest model
            if allocation_pct <= 0.01:
                model = AllocationModel.CONSERVATIVE
            elif allocation_pct <= 0.03:
                model = AllocationModel.MODERATE
            else:
                model = AllocationModel.AGGRESSIVE
        else:
            allocation_pct = self.allocation_models[model]

        # Calculate recommended amount
        recommended_amount = portfolio_value * allocation_pct

        # Determine custody recommendation
        if profile.financial_sophistication in ["accredited", "institutional"]:
            custody = "self"  # Self-custody for sophisticated clients
        else:
            custody = "custodial"  # Custodial for retail clients

        # Build rationale
        rationale = (
            f"Recommended {allocation_pct*100:.1f}% allocation ({model.value} model) "
            f"based on {profile.risk_tolerance.value} risk tolerance. "
            f"Total allocation: ${recommended_amount:,.2f}"
        )

        # Risk warnings
        risk_warnings = [
            "Bitcoin is highly volatile and can experience 50%+ drawdowns",
            "Past performance does not guarantee future results",
            "Regulatory changes may impact Bitcoin's value",
            "Bitcoin is a speculative asset, not guaranteed returns",
            "Only invest what you can afford to lose"
        ]

        allocation = BitcoinAllocation(
            client_id=profile.client_id,
            allocation_percentage=allocation_pct,
            allocation_model=model,
            recommended_amount=recommended_amount,
            dollar_cost_averaging=True,
            dca_period_months=12,
            rebalancing_frequency="quarterly",
            custody_recommendation=custody,
            rationale=rationale,
            risk_warnings=risk_warnings
        )

        logger.info(f"Allocation calculated for {profile.client_id}: {allocation_pct*100:.1f}%")
        return allocation

    def monitor_risk(
        self,
        client_id: str,
        current_allocation_pct: float,
        position_value: float,
        max_allowed_pct: float,
        portfolio_value: Optional[float] = None
    ) -> RiskMetrics:
        """
        @PEAK: Risk Monitoring

        Monitor Bitcoin position risk metrics and generate alerts.

        Args:
            client_id: Client identifier
            current_allocation_pct: Current Bitcoin allocation percentage
            position_value: Current Bitcoin position value
            max_allowed_pct: Maximum allowed allocation percentage
            portfolio_value: Optional total portfolio value for correlation

        Returns:
            Risk metrics with alerts
        """
        alerts = []

        # Check allocation limit
        if current_allocation_pct > max_allowed_pct:
            alerts.append(
                f"Allocation {current_allocation_pct*100:.1f}% exceeds "
                f"maximum {max_allowed_pct*100:.1f}% - rebalancing recommended"
            )

        # Check if allocation has grown significantly (rebalancing trigger)
        if current_allocation_pct > max_allowed_pct * 1.2:
            alerts.append(
                f"Allocation has grown to {current_allocation_pct*100:.1f}% - "
                "immediate rebalancing recommended"
            )

        # Check if allocation has dropped significantly
        if current_allocation_pct < max_allowed_pct * 0.5:
            alerts.append(
                f"Allocation has dropped to {current_allocation_pct*100:.1f}% - "
                "consider rebalancing to target"
            )

        metrics = RiskMetrics(
            client_id=client_id,
            current_allocation_percentage=current_allocation_pct,
            position_value=position_value,
            max_allowed_percentage=max_allowed_pct,
            last_updated=datetime.now(),
            alerts=alerts
        )

        if alerts:
            logger.warning(f"Risk alerts for {client_id}: {len(alerts)} alerts")
        else:
            logger.info(f"Risk monitoring for {client_id}: No alerts")

        return metrics

    def generate_client_report(
        self,
        profile: ClientProfile,
        allocation: BitcoinAllocation,
        suitability_status: SuitabilityStatus,
        risk_metrics: Optional[RiskMetrics] = None
    ) -> Dict[str, Any]:
        """
        @PEAK: Client Report Generation

        Generate comprehensive client report with suitability, allocation,
        and risk information.

        Args:
            profile: Client profile
            allocation: Bitcoin allocation recommendation
            suitability_status: Suitability assessment result
            risk_metrics: Optional current risk metrics

        Returns:
            Complete client report dictionary
        """
        report = {
            "client_id": profile.client_id,
            "report_date": datetime.now().isoformat(),
            "suitability": {
                "status": suitability_status.value,
                "risk_tolerance": profile.risk_tolerance.value,
                "investment_horizon_years": profile.investment_horizon_years,
                "bitcoin_knowledge_level": profile.bitcoin_knowledge_level,
                "financial_sophistication": profile.financial_sophistication
            },
            "allocation": allocation.to_dict(),
            "risk_metrics": risk_metrics.to_dict() if risk_metrics else None,
            "recommendations": {
                "custody": allocation.custody_recommendation,
                "dollar_cost_averaging": allocation.dollar_cost_averaging,
                "rebalancing_frequency": allocation.rebalancing_frequency
            },
            "risk_warnings": allocation.risk_warnings
        }

        # Save report
        report_file = self.data_dir / f"report_{profile.client_id}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Client report generated for {profile.client_id}")
        return report

    def execute_onboarding_workflow(
        self,
        profile: ClientProfile,
        portfolio_value: float
    ) -> Dict[str, Any]:
        """
        @PEAK: Client Onboarding Workflow

        Execute complete client onboarding workflow for Bitcoin allocation.

        Args:
            profile: Client profile
            portfolio_value: Total portfolio value

        Returns:
            Complete workflow results
        """
        logger.info(f"Starting onboarding workflow for {profile.client_id}")

        # Step 1: Suitability Assessment
        suitability_status, rationale, recommendations = self.assess_suitability(profile)

        if suitability_status == SuitabilityStatus.NOT_SUITABLE:
            return {
                "success": False,
                "client_id": profile.client_id,
                "suitability_status": suitability_status.value,
                "rationale": rationale,
                "recommendations": recommendations,
                "message": "Client not suitable for Bitcoin allocation"
            }

        # Step 2: Calculate Allocation
        allocation = self.calculate_allocation(profile, portfolio_value)

        # Step 3: Generate Report
        report = self.generate_client_report(profile, allocation, suitability_status)

        # Step 4: Save profile and allocation
        profile_file = self.data_dir / f"profile_{profile.client_id}.json"
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)

        allocation_file = self.data_dir / f"allocation_{profile.client_id}.json"
        with open(allocation_file, "w", encoding="utf-8") as f:
            json.dump(allocation.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Onboarding workflow complete for {profile.client_id}")

        return {
            "success": True,
            "client_id": profile.client_id,
            "suitability_status": suitability_status.value,
            "allocation": allocation.to_dict(),
            "report": report,
            "next_steps": [
                "Client education session",
                "Custodian selection and setup",
                "Initial purchase (DCA recommended)",
                "Schedule quarterly review"
            ]
        }


def main() -> int:
    try:
        """Main entry point for testing"""
        system = BitcoinWorkflowSystem()

        # Example client profile
        profile = ClientProfile(
            client_id="CLIENT_001",
            risk_tolerance=RiskTolerance.MODERATE,
            investment_horizon_years=10,
            bitcoin_knowledge_level=4,
            financial_sophistication="accredited",
            current_portfolio_value=1000000.0,
            max_drawdown_tolerance=0.30
        )

        # Execute onboarding workflow
        result = system.execute_onboarding_workflow(profile, 1000000.0)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import sys



    sys.exit(main())