#!/usr/bin/env python3
"""
Generate Bitcoin Test Data
@PEAK Optimized

Generate comprehensive test data for Bitcoin financial workflows.

Author: <COMPANY_NAME> LLC
Date: 2025-01-27
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from bitcoin_financial_workflows import (
        ClientProfile,
        RiskTolerance,
        BitcoinAllocation,
        AllocationModel
    )
    from bitcoin_workflow_enhancements import (
        BitcoinWorkflowEnhancements,
        PerformanceMetrics,
        Alert,
        AlertLevel
    )
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def generate_test_clients(count: int = 10) -> List[ClientProfile]:
    """
    @PEAK: Generate Test Clients

    Generate diverse test client profiles.
    """
    clients = []
    risk_levels = [RiskTolerance.CONSERVATIVE, RiskTolerance.MODERATE, RiskTolerance.AGGRESSIVE]
    sophistication_levels = ["retail", "accredited", "institutional"]

    for i in range(1, count + 1):
        risk = random.choice(risk_levels)
        sophistication = random.choice(sophistication_levels)

        # Adjust knowledge based on sophistication
        if sophistication == "institutional":
            knowledge = random.randint(4, 5)
        elif sophistication == "accredited":
            knowledge = random.randint(3, 5)
        else:
            knowledge = random.randint(1, 3)

        # Adjust horizon based on risk
        if risk == RiskTolerance.CONSERVATIVE:
            horizon = random.randint(3, 7)
        elif risk == RiskTolerance.AGGRESSIVE:
            horizon = random.randint(10, 20)
        else:
            horizon = random.randint(5, 15)

        client = ClientProfile(
            client_id=f"TEST_CLIENT_{i:03d}",
            risk_tolerance=risk,
            investment_horizon_years=horizon,
            bitcoin_knowledge_level=knowledge,
            financial_sophistication=sophistication,
            current_portfolio_value=random.uniform(100000, 5000000),
            max_drawdown_tolerance=random.uniform(0.20, 0.50),
            regulatory_restrictions=[] if random.random() > 0.2 else ["state_restriction"]
        )

        clients.append(client)

    return clients


def generate_test_allocations(
    clients: List[ClientProfile],
    portfolio_values: Dict[str, float]
) -> List[BitcoinAllocation]:
    """
    @PEAK: Generate Test Allocations

    Generate test allocation recommendations for clients.
    """
    allocations = []
    enhancements = BitcoinWorkflowEnhancements()

    for client in clients:
        portfolio_value = portfolio_values.get(client.client_id, client.current_portfolio_value or 1000000)

        # Determine allocation model
        if client.risk_tolerance == RiskTolerance.CONSERVATIVE:
            model = AllocationModel.CONSERVATIVE
            pct = 0.01
        elif client.risk_tolerance == RiskTolerance.AGGRESSIVE:
            model = AllocationModel.AGGRESSIVE
            pct = 0.05
        else:
            model = AllocationModel.MODERATE
            pct = 0.025

        allocation = BitcoinAllocation(
            client_id=client.client_id,
            allocation_percentage=pct,
            allocation_model=model,
            recommended_amount=portfolio_value * pct,
            dollar_cost_averaging=True,
            dca_period_months=12,
            rebalancing_frequency="quarterly",
            custody_recommendation="custodial" if client.financial_sophistication == "retail" else "self",
            rationale=f"Recommended {pct*100:.1f}% allocation based on {client.risk_tolerance.value} risk tolerance",
            risk_warnings=[
                "Bitcoin is highly volatile",
                "Past performance does not guarantee future results",
                "Regulatory changes may impact value"
            ]
        )

        allocations.append(allocation)

    return allocations


def generate_test_performance_metrics(
    clients: List[ClientProfile],
    days_back: int = 90
) -> List[PerformanceMetrics]:
    """
    @PEAK: Generate Test Performance Metrics

    Generate test performance metrics for clients.
    """
    metrics_list = []
    enhancements = BitcoinWorkflowEnhancements()

    period_end = datetime.now()
    period_start = period_end - timedelta(days=days_back)

    for client in clients:
        # Simulate portfolio values
        initial_portfolio = client.current_portfolio_value or 1000000
        portfolio_return = random.uniform(-0.10, 0.20)  # -10% to +20%
        current_portfolio = initial_portfolio * (1 + portfolio_return)

        # Simulate Bitcoin allocation
        allocation_pct = 0.025 if client.risk_tolerance == RiskTolerance.MODERATE else (
            0.01 if client.risk_tolerance == RiskTolerance.CONSERVATIVE else 0.05
        )
        initial_bitcoin = initial_portfolio * allocation_pct

        # Bitcoin typically more volatile
        bitcoin_return = random.uniform(-0.30, 0.50)  # -30% to +50%
        current_bitcoin = initial_bitcoin * (1 + bitcoin_return)

        # Current allocation may have drifted
        current_allocation_pct = (current_bitcoin / current_portfolio) if current_portfolio > 0 else allocation_pct

        metrics = enhancements.calculate_performance(
            client_id=client.client_id,
            period_start=period_start,
            period_end=period_end,
            initial_bitcoin_value=initial_bitcoin,
            current_bitcoin_value=current_bitcoin,
            initial_portfolio_value=initial_portfolio,
            current_portfolio_value=current_portfolio,
            initial_allocation_pct=allocation_pct,
            current_allocation_pct=current_allocation_pct
        )

        metrics_list.append(metrics)

    return metrics_list


def generate_test_alerts(clients: List[ClientProfile]) -> List[Alert]:
    """
    @PEAK: Generate Test Alerts

    Generate test alerts for various scenarios.
    """
    alerts = []
    enhancements = BitcoinWorkflowEnhancements()

    alert_scenarios = [
        {
            "type": "allocation_exceeded",
            "level": AlertLevel.WARNING,
            "message": "Bitcoin allocation exceeds target by more than 20%",
            "probability": 0.3
        },
        {
            "type": "volatility_spike",
            "level": AlertLevel.WARNING,
            "message": "Bitcoin volatility spike detected - 30-day volatility > 80%",
            "probability": 0.2
        },
        {
            "type": "regulatory_update",
            "level": AlertLevel.INFO,
            "message": "New regulatory guidance issued - review required",
            "probability": 0.1
        },
        {
            "type": "rebalancing_due",
            "level": AlertLevel.INFO,
            "message": "Scheduled rebalancing due",
            "probability": 0.4
        }
    ]

    for client in clients:
        for scenario in alert_scenarios:
            if random.random() < scenario["probability"]:
                alert = enhancements.generate_alert(
                    client_id=client.client_id,
                    alert_level=scenario["level"],
                    alert_type=scenario["type"],
                    message=scenario["message"],
                    metadata={"scenario": scenario["type"]}
                )
                alerts.append(alert)

    return alerts


def save_test_data(
    clients: List[ClientProfile],
    allocations: List[BitcoinAllocation],
    metrics: List[PerformanceMetrics],
    alerts: List[Alert],
    output_dir: Path
) -> None:
    """
    @PEAK: Save Test Data

    Save all test data to JSON files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save clients
    clients_data = [client.to_dict() for client in clients]
    with open(output_dir / "test_clients.json", "w", encoding="utf-8") as f:
        json.dump(clients_data, f, indent=2, ensure_ascii=False)

    # Save allocations
    allocations_data = [allocation.to_dict() for allocation in allocations]
    with open(output_dir / "test_allocations.json", "w", encoding="utf-8") as f:
        json.dump(allocations_data, f, indent=2, ensure_ascii=False)

    # Save metrics
    metrics_data = [m.to_dict() for m in metrics]
    with open(output_dir / "test_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2, ensure_ascii=False)

    # Save alerts
    alerts_data = [alert.to_dict() for alert in alerts]
    with open(output_dir / "test_alerts.json", "w", encoding="utf-8") as f:
        json.dump(alerts_data, f, indent=2, ensure_ascii=False)

    # Save summary
    summary = {
        "generated": datetime.now().isoformat(),
        "counts": {
            "clients": len(clients),
            "allocations": len(allocations),
            "metrics": len(metrics),
            "alerts": len(alerts)
        },
        "files": {
            "clients": "test_clients.json",
            "allocations": "test_allocations.json",
            "metrics": "test_metrics.json",
            "alerts": "test_alerts.json"
        }
    }

    with open(output_dir / "test_data_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Test data saved to {output_dir}")
    print(f"  Clients: {len(clients)}")
    print(f"  Allocations: {len(allocations)}")
    print(f"  Metrics: {len(metrics)}")
    print(f"  Alerts: {len(alerts)}")


def main() -> int:
    """Generate comprehensive test data"""
    print("=" * 60)
    print("Bitcoin Test Data Generation")
    print("=" * 60)

    # Generate test clients
    print("\nGenerating test clients...")
    clients = generate_test_clients(count=10)
    print(f"Generated {len(clients)} test clients")

    # Generate portfolio values
    portfolio_values = {
        client.client_id: client.current_portfolio_value or 1000000
        for client in clients
    }

    # Generate allocations
    print("\nGenerating test allocations...")
    allocations = generate_test_allocations(clients, portfolio_values)
    print(f"Generated {len(allocations)} allocations")

    # Generate performance metrics
    print("\nGenerating test performance metrics...")
    metrics = generate_test_performance_metrics(clients, days_back=90)
    print(f"Generated {len(metrics)} performance metrics")

    # Generate alerts
    print("\nGenerating test alerts...")
    alerts = generate_test_alerts(clients)
    print(f"Generated {len(alerts)} alerts")

    # Save test data
    output_dir = project_root / "data" / "bitcoin_workflows" / "test_data"
    save_test_data(clients, allocations, metrics, alerts, output_dir)

    print("\n" + "=" * 60)
    print("Test Data Generation Complete")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    import sys



    sys.exit(main())