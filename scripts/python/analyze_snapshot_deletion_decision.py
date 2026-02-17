#!/usr/bin/env python3
"""
Snapshot Deletion Decision Analysis

Applies escalation framework and decision-making system to evaluate
whether to delete recursive snapshots consuming 1.22 TB of space.

Uses:
- Universal Decision Tree
- Triage System
- Escalation Framework
- Opposing Viewpoints (JARVIS vs MARVIN)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    from aiq_triage_jedi import AIQTriageRouter, TriagePriority
except ImportError as e:
    print(f"Warning: Could not import decision systems: {e}")
    decide = None
    AIQTriageRouter = None

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SnapshotDeletionDecisionAnalysis")


def analyze_snapshot_deletion_decision(
    snapshot_path: Path,
    snapshot_size_gb: float,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Analyze decision to delete recursive snapshot using escalation framework

    Args:
        snapshot_path: Path to snapshot directory
        snapshot_size_gb: Size of snapshot in GB
        dry_run: If True, only analyze without taking action

    Returns:
        Decision analysis result
    """
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "snapshot_path": str(snapshot_path),
        "snapshot_size_gb": snapshot_size_gb,
        "dry_run": dry_run,
        "triage_result": None,
        "decision_context": None,
        "decision_result": None,
        "escalation_needed": True,
        "escalation_level": "jedi_council",
        "recommended_action": None,
        "risk_assessment": {},
        "options_evaluation": []
    }

    # Step 1: Triage the issue
    logger.info("=" * 70)
    logger.info("SNAPSHOT DELETION DECISION ANALYSIS")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Step 1: Triage")
    logger.info("-" * 70)

    issue_description = f"""
    Recursive snapshot consuming {snapshot_size_gb:.2f} GB of Dropbox space.
    Snapshot location: {snapshot_path}
    Nesting depth: 12 levels (recursive copy of copy)
    Impact: Dropbox space warnings, 90% of my_projects directory
    """

    # Determine priority based on size and impact
    if snapshot_size_gb > 1000:  # > 1 TB
        priority = "Elevated"
        urgency = "high"
    elif snapshot_size_gb > 100:  # > 100 GB
        priority = "Elevated"
        urgency = "medium"
    else:
        priority = "Routine"
        urgency = "low"

    analysis["triage_result"] = {
        "category": "data_management",
        "priority": priority,
        "urgency": urgency,
        "severity": "high" if snapshot_size_gb > 1000 else "medium",
        "notes": "Large data deletion decision requires careful evaluation"
    }

    logger.info(f"Priority: {priority}")
    logger.info(f"Urgency: {urgency}")
    logger.info(f"Category: data_management")
    logger.info("")

    # Step 2: Decision Context
    logger.info("Step 2: Decision Context")
    logger.info("-" * 70)

    decision_context = DecisionContext(
        complexity="medium",
        urgency=urgency,
        cost_sensitive=True,
        custom_data={
            "snapshot_size_gb": snapshot_size_gb,
            "snapshot_path": str(snapshot_path),
            "action_type": "data_deletion",
            "irreversible": True,
            "requires_approval": True
        }
    )

    analysis["decision_context"] = {
        "complexity": decision_context.complexity,
        "urgency": decision_context.urgency,
        "cost_sensitive": decision_context.cost_sensitive,
        "custom_data": decision_context.custom_data
    }

    logger.info(f"Complexity: {decision_context.complexity}")
    logger.info(f"Urgency: {decision_context.urgency}")
    logger.info(f"Cost Sensitive: {decision_context.cost_sensitive}")
    logger.info("")

    # Step 3: Options Evaluation
    logger.info("Step 3: Options Evaluation")
    logger.info("-" * 70)

    options = [
        {
            "id": "delete",
            "action": "Delete recursive snapshot",
            "pros": [
                "Frees 1.22 TB immediately",
                "Resolves Dropbox space issue",
                "Eliminates storage costs",
                "Recursive = redundant data"
            ],
            "cons": [
                "Irreversible",
                "Potential data loss",
                "Uncertainty about unique data"
            ],
            "risk": "medium",
            "recommended_for": "If recursive data confirmed redundant"
        },
        {
            "id": "archive",
            "action": "Archive to external storage",
            "pros": [
                "Preserves data",
                "Frees Dropbox space",
                "Reversible",
                "Lower risk"
            ],
            "cons": [
                "Requires external storage",
                "Time to move 1.22 TB",
                "Ongoing storage management"
            ],
            "risk": "low",
            "recommended_for": "If external storage available and data preservation desired"
        },
        {
            "id": "analyze_then_decide",
            "action": "Deep analysis before decision",
            "pros": [
                "Informed decision",
                "Identifies unique data",
                "Lower risk"
            ],
            "cons": [
                "Time-consuming",
                "Space issue remains",
                "Resource intensive"
            ],
            "risk": "low",
            "recommended_for": "If uncertainty about data value"
        },
        {
            "id": "extract_then_delete",
            "action": "Extract unique data, then delete",
            "pros": [
                "Preserves unique data",
                "Frees space",
                "Balanced approach"
            ],
            "cons": [
                "Complex",
                "Time-consuming",
                "May find nothing unique"
            ],
            "risk": "low",
            "recommended_for": "If unique data suspected"
        }
    ]

    analysis["options_evaluation"] = options

    for option in options:
        logger.info(f"Option: {option['id']}")
        logger.info(f"  Action: {option['action']}")
        logger.info(f"  Risk: {option['risk']}")
        logger.info(f"  Recommended for: {option['recommended_for']}")
        logger.info("")

    # Step 4: Risk Assessment
    logger.info("Step 4: Risk Assessment")
    logger.info("-" * 70)

    risk_assessment = {
        "data_loss_risk": {
            "level": "medium",
            "reasoning": "Recursive snapshots likely contain only redundant data, but uncertainty exists"
        },
        "space_recovery_benefit": {
            "level": "high",
            "reasoning": f"Frees {snapshot_size_gb:.2f} GB immediately, resolves Dropbox warnings"
        },
        "irreversibility": {
            "level": "high",
            "reasoning": "Deletion is permanent, cannot be undone"
        },
        "decision_confidence": {
            "level": "medium",
            "reasoning": "Need more information: Is original data intact? Is snapshot truly redundant?"
        }
    }

    analysis["risk_assessment"] = risk_assessment

    for risk, assessment in risk_assessment.items():
        logger.info(f"{risk}: {assessment['level']}")
        logger.info(f"  {assessment['reasoning']}")
        logger.info("")

    # Step 5: Escalation Decision
    logger.info("Step 5: Escalation Decision")
    logger.info("-" * 70)

    # This is a data deletion decision affecting 1.22 TB - requires escalation
    analysis["escalation_needed"] = True
    analysis["escalation_level"] = "jedi_council"

    logger.info("Escalation: REQUIRED")
    logger.info("Escalation Level: Jedi Council")
    logger.info("Reason: Data deletion decision affecting 1.22 TB requires upper management approval")
    logger.info("")

    # Step 6: Recommended Action (pending escalation)
    logger.info("Step 6: Recommended Action (PENDING ESCALATION)")
    logger.info("-" * 70)

    recommended_action = {
        "immediate": "DO NOT DELETE - Await escalation decision",
        "pre_deletion_steps": [
            "1. Verify original data source is intact",
            "2. Confirm snapshot is truly recursive (contains only nested copies)",
            "3. Check if data is preserved in Git/GitLens",
            "4. Identify external storage options for archiving (if desired)",
            "5. Escalate to Jedi Council for approval"
        ],
        "recommended_approach": "Archive to external storage if available, otherwise delete after verification",
        "requires_approval": True
    }

    analysis["recommended_action"] = recommended_action

    logger.info("Immediate Action: DO NOT DELETE - Await escalation decision")
    logger.info("")
    logger.info("Pre-deletion steps:")
    for step in recommended_action["pre_deletion_steps"]:
        logger.info(f"  {step}")
    logger.info("")
    logger.info(f"Recommended Approach: {recommended_action['recommended_approach']}")
    logger.info("")

    # Summary
    logger.info("=" * 70)
    logger.info("ANALYSIS SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Priority: {priority}")
    logger.info(f"Escalation: REQUIRED (Jedi Council)")
    logger.info(f"Decision Authority: Upper Management")
    logger.info(f"Recommended: Archive if possible, otherwise delete after verification")
    logger.info(f"Risk: Medium (due to irreversibility and uncertainty)")
    logger.info("=" * 70)

    return analysis


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Analyze snapshot deletion decision using escalation framework"
        )
        parser.add_argument(
            "--snapshot-path",
            type=str,
            default="c:\\Users\\mlesn\\Dropbox\\my_projects\\data\\time_travel\\snapshots\\snapshot_main_20251228_005758_292043",
            help="Path to snapshot directory"
        )
        parser.add_argument(
            "--snapshot-size-gb",
            type=float,
            default=1337.69,  # 1.22 TB in GB
            help="Size of snapshot in GB"
        )
        parser.add_argument(
            "--report",
            type=str,
            default="data/snapshot_deletion_decision_analysis.json",
            help="Save analysis report to JSON file"
        )

        args = parser.parse_args()

        snapshot_path = Path(args.snapshot_path)

        # Run analysis
        analysis = analyze_snapshot_deletion_decision(
            snapshot_path,
            args.snapshot_size_gb,
            dry_run=True
        )

        # Save report
        report_path = project_root / args.report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        logger.info(f"Analysis report saved to: {report_path}")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())