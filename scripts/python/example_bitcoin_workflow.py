#!/usr/bin/env python3
"""
Example Bitcoin Financial Workflow
Demonstrates Bitcoin workflow integration with JARVIS/droid system

Author: <COMPANY_NAME> LLC
Date: 2025-01-27
"""

import sys
from pathlib import Path
from typing import Dict, Any
import json

# Add scripts/python to path for imports
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from bitcoin_financial_workflows import (
    BitcoinWorkflowSystem,
    ClientProfile,
    RiskTolerance
)
from bitcoin_jarvis_integration import BitcoinJARVISIntegration
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def example_bitcoin_onboarding():
    """Example Bitcoin client onboarding workflow"""
    print("=" * 60)
    print("Example: Bitcoin Client Onboarding Workflow")
    print("=" * 60)

    # Initialize systems
    integration = BitcoinJARVISIntegration()

    # Create example client profile
    profile = ClientProfile(
        client_id="CLIENT_001",
        risk_tolerance=RiskTolerance.MODERATE,
        investment_horizon_years=10,
        bitcoin_knowledge_level=4,
        financial_sophistication="accredited",
        current_portfolio_value=1000000.0,
        max_drawdown_tolerance=0.30
    )

    print(f"\nClient Profile:")
    print(f"  ID: {profile.client_id}")
    print(f"  Risk Tolerance: {profile.risk_tolerance.value}")
    print(f"  Investment Horizon: {profile.investment_horizon_years} years")
    print(f"  Bitcoin Knowledge: {profile.bitcoin_knowledge_level}/5")
    print(f"  Sophistication: {profile.financial_sophistication}")
    print(f"  Portfolio Value: ${profile.current_portfolio_value:,.2f}")

    # Execute onboarding workflow with JARVIS verification
    print("\n" + "=" * 60)
    print("Executing Onboarding Workflow with JARVIS Verification...")
    print("=" * 60)

    success, results = integration.execute_bitcoin_onboarding_workflow(
        profile,
        portfolio_value=1000000.0,
        require_verification=True
    )

    print(f"\nWorkflow Status: {'SUCCESS' if success else 'FAILED'}")

    if success and results.get("verification", {}).get("droid_assignment"):
        droid = results["verification"]["droid_assignment"]
        print(f"\nDroid Assignment:")
        print(f"  Droid: {droid.get('droid_name', 'Unknown')}")
        print(f"  Response: {droid.get('persona_response', 'N/A')}")

    if results.get("workflow_result"):
        workflow_result = results["workflow_result"]
        print(f"\nWorkflow Results:")
        print(f"  Suitability: {workflow_result.get('suitability_status', 'N/A')}")

        if workflow_result.get("allocation"):
            allocation = workflow_result["allocation"]
            print(f"  Allocation: {allocation.get('allocation_percentage', 0)*100:.1f}%")
            print(f"  Model: {allocation.get('allocation_model', 'N/A')}")
            print(f"  Amount: ${allocation.get('recommended_amount', 0):,.2f}")
            print(f"  Custody: {allocation.get('custody_recommendation', 'N/A')}")

        if workflow_result.get("next_steps"):
            print(f"\n  Next Steps:")
            for step in workflow_result["next_steps"]:
                print(f"    - {step}")


def example_risk_monitoring():
    """Example Bitcoin risk monitoring workflow"""
    print("\n" + "=" * 60)
    print("Example: Bitcoin Risk Monitoring Workflow")
    print("=" * 60)

    integration = BitcoinJARVISIntegration()

    # Example risk monitoring scenario
    client_id = "CLIENT_001"
    current_allocation_pct = 0.035  # 3.5% (above moderate target of 2.5%)
    position_value = 35000.0
    max_allowed_pct = 0.025  # 2.5% (moderate model)

    print(f"\nRisk Monitoring Scenario:")
    print(f"  Client ID: {client_id}")
    print(f"  Current Allocation: {current_allocation_pct*100:.1f}%")
    print(f"  Position Value: ${position_value:,.2f}")
    print(f"  Max Allowed: {max_allowed_pct*100:.1f}%")

    # Execute risk monitoring workflow
    print("\n" + "=" * 60)
    print("Executing Risk Monitoring Workflow...")
    print("=" * 60)

    success, results = integration.execute_risk_monitoring_workflow(
        client_id,
        current_allocation_pct,
        position_value,
        max_allowed_pct,
        require_verification=True
    )

    print(f"\nWorkflow Status: {'SUCCESS' if success else 'FAILED'}")

    if results.get("workflow_result"):
        workflow_result = results["workflow_result"]

        if workflow_result.get("metrics"):
            metrics = workflow_result["metrics"]
            print(f"\nRisk Metrics:")
            print(f"  Current Allocation: {metrics.get('current_allocation_percentage', 0)*100:.1f}%")
            print(f"  Position Value: ${metrics.get('position_value', 0):,.2f}")
            print(f"  Max Allowed: {metrics.get('max_allowed_percentage', 0)*100:.1f}%")

        if workflow_result.get("alerts"):
            print(f"\n  Alerts ({len(workflow_result['alerts'])}):")
            for alert in workflow_result["alerts"]:
                print(f"    ⚠️  {alert}")

        if workflow_result.get("recommendations"):
            print(f"\n  Recommendations:")
            for rec in workflow_result["recommendations"]:
                print(f"    ✓ {rec}")


def example_suitability_assessment():
    """Example suitability assessment workflow"""
    print("\n" + "=" * 60)
    print("Example: Client Suitability Assessment")
    print("=" * 60)

    system = BitcoinWorkflowSystem()

    # Example profiles with different characteristics
    profiles = [
        ClientProfile(
            client_id="CONSERVATIVE_CLIENT",
            risk_tolerance=RiskTolerance.CONSERVATIVE,
            investment_horizon_years=3,
            bitcoin_knowledge_level=2,
            financial_sophistication="retail"
        ),
        ClientProfile(
            client_id="MODERATE_CLIENT",
            risk_tolerance=RiskTolerance.MODERATE,
            investment_horizon_years=10,
            bitcoin_knowledge_level=4,
            financial_sophistication="accredited"
        ),
        ClientProfile(
            client_id="AGGRESSIVE_CLIENT",
            risk_tolerance=RiskTolerance.AGGRESSIVE,
            investment_horizon_years=15,
            bitcoin_knowledge_level=5,
            financial_sophistication="institutional"
        )
    ]

    for profile in profiles:
        print(f"\n{profile.client_id}:")
        print(f"  Risk: {profile.risk_tolerance.value}")
        print(f"  Horizon: {profile.investment_horizon_years} years")
        print(f"  Knowledge: {profile.bitcoin_knowledge_level}/5")
        print(f"  Sophistication: {profile.financial_sophistication}")

        status, rationale, recommendations = system.assess_suitability(profile)

        print(f"  Status: {status.value}")
        print(f"  Rationale: {rationale}")
        if recommendations:
            print(f"  Recommendations:")
            for rec in recommendations:
                print(f"    - {rec}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Bitcoin Financial Workflows - Examples")
    print("<COMPANY_NAME> LLC")
    print("=" * 60)

    try:
        # Example 1: Client Onboarding
        example_bitcoin_onboarding()

        # Example 2: Risk Monitoring
        example_risk_monitoring()

        # Example 3: Suitability Assessment
        example_suitability_assessment()

        print("\n" + "=" * 60)
        print("All Examples Complete")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys



    sys.exit(main())