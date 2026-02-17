#!/usr/bin/env python3
"""
Tape Library Team Workflow

CRITICAL: Decision-making happens at the END of the workflow.
We must START at the BEGINNING every single time:
1. Problem identification
2. Impact assessment (business impact, customer impact)
3. Root cause analysis
4. Escalation determination
5. Prevention strategies
6. THEN decision-making

This workflow ensures we never skip steps and always consider all factors.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TapeLibraryWorkflow")


@dataclass
class ProblemIdentification:
    """Step 1: Problem Identification"""
    problem_id: str
    timestamp: str
    problem_description: str
    data_path: str
    data_size_bytes: int
    symptoms: List[str]
    reported_by: str
    urgency_initial: str  # low, medium, high, critical


@dataclass
class ImpactAssessment:
    """Step 2: Impact Assessment"""
    business_impact: Dict[str, Any]
    customer_impact: Dict[str, Any]
    system_impact: Dict[str, Any]
    financial_impact: Dict[str, Any]
    operational_impact: Dict[str, Any]
    risk_level: str  # low, medium, high, critical


@dataclass
class RootCauseAnalysis:
    """Step 3: Root Cause Analysis"""
    root_cause: str
    contributing_factors: List[str]
    evidence: List[str]
    confidence_level: float  # 0.0 to 1.0


@dataclass
class EscalationDetermination:
    """Step 4: Escalation Determination"""
    escalations_required: List[Dict[str, Any]]
    escalation_reasons: List[str]
    escalation_levels: List[str]  # team, management, executive, critical
    approval_required: bool
    approval_authorities: List[str]


@dataclass
class PreventionStrategies:
    """Step 5: Prevention Strategies"""
    immediate_prevention: List[str]
    short_term_prevention: List[str]
    long_term_prevention: List[str]
    process_improvements: List[str]
    system_changes: List[str]
    monitoring_recommendations: List[str]


@dataclass
class DecisionMaking:
    """Step 6: Decision Making (LAST STEP)"""
    decision_id: str
    decision: str  # archive, delete, escalate, monitor, defer
    reasoning: str
    alternatives_considered: List[str]
    chosen_alternative: str
    risk_assessment: Dict[str, Any]
    approval_status: str  # pending, approved, rejected, delegated


@dataclass
class TapeLibraryWorkflowResult:
    """Complete workflow result"""
    workflow_id: str
    timestamp: str

    # Workflow steps (in order)
    step_1_problem_identification: ProblemIdentification
    step_2_impact_assessment: ImpactAssessment
    step_3_root_cause_analysis: RootCauseAnalysis
    step_4_escalation_determination: EscalationDetermination
    step_5_prevention_strategies: PreventionStrategies
    step_6_decision_making: DecisionMaking

    # Workflow metadata
    completed_steps: List[str]
    workflow_status: str  # in_progress, complete, blocked, escalated
    next_actions: List[str]


class TapeLibraryWorkflow:
    """
    Tape Library Team Workflow

    CRITICAL: This workflow MUST be followed from beginning to end.
    Decision-making is the LAST step, not the first.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Tape Library Workflow"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("TapeLibraryWorkflow")

        # Data directory
        self.data_dir = self.project_root / "data" / "tape_library_team" / "workflows"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ Tape Library Workflow initialized")
        self.logger.info("   REMEMBER: Decision-making is at the END of the workflow")

    def execute_workflow(self,
                        problem_description: str,
                        data_path: str,
                        data_size_bytes: int,
                        reported_by: str = "system") -> TapeLibraryWorkflowResult:
        """
        Execute complete workflow from beginning to end

        Args:
            problem_description: Description of the problem
            data_path: Path to data in question
            data_size_bytes: Size of data in bytes
            reported_by: Who/what reported the problem

        Returns:
            Complete workflow result
        """
        workflow_id = f"workflow-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.logger.info("=" * 70)
        self.logger.info("TAPE LIBRARY WORKFLOW")
        self.logger.info("=" * 70)
        self.logger.info(f"Workflow ID: {workflow_id}")
        self.logger.info("Starting at BEGINNING of workflow...")
        self.logger.info("")

        completed_steps = []

        # STEP 1: Problem Identification
        self.logger.info("STEP 1: PROBLEM IDENTIFICATION")
        self.logger.info("-" * 70)
        problem = self._identify_problem(
            problem_description, data_path, data_size_bytes, reported_by
        )
        completed_steps.append("problem_identification")
        self.logger.info(f"Problem identified: {problem.problem_description}")
        self.logger.info("")

        # STEP 2: Impact Assessment
        self.logger.info("STEP 2: IMPACT ASSESSMENT")
        self.logger.info("-" * 70)
        impact = self._assess_impact(problem)
        completed_steps.append("impact_assessment")
        self.logger.info(f"Business Impact: {impact.business_impact.get('severity', 'unknown')}")
        self.logger.info(f"Customer Impact: {impact.customer_impact.get('severity', 'unknown')}")
        self.logger.info(f"Risk Level: {impact.risk_level}")
        self.logger.info("")

        # STEP 3: Root Cause Analysis
        self.logger.info("STEP 3: ROOT CAUSE ANALYSIS")
        self.logger.info("-" * 70)
        root_cause = self._analyze_root_cause(problem, impact)
        completed_steps.append("root_cause_analysis")
        self.logger.info(f"Root Cause: {root_cause.root_cause}")
        self.logger.info(f"Confidence: {root_cause.confidence_level:.2f}")
        self.logger.info("")

        # STEP 4: Escalation Determination
        self.logger.info("STEP 4: ESCALATION DETERMINATION")
        self.logger.info("-" * 70)
        escalation = self._determine_escalations(problem, impact, root_cause)
        completed_steps.append("escalation_determination")
        self.logger.info(f"Escalations Required: {len(escalation.escalations_required)}")
        self.logger.info(f"Approval Required: {escalation.approval_required}")
        self.logger.info("")

        # STEP 5: Prevention Strategies
        self.logger.info("STEP 5: PREVENTION STRATEGIES")
        self.logger.info("-" * 70)
        prevention = self._develop_prevention_strategies(problem, impact, root_cause)
        completed_steps.append("prevention_strategies")
        self.logger.info(f"Immediate Prevention: {len(prevention.immediate_prevention)} items")
        self.logger.info(f"Long-term Prevention: {len(prevention.long_term_prevention)} items")
        self.logger.info("")

        # STEP 6: Decision Making (LAST STEP)
        self.logger.info("STEP 6: DECISION MAKING (FINAL STEP)")
        self.logger.info("-" * 70)
        decision = self._make_decision(
            problem, impact, root_cause, escalation, prevention
        )
        completed_steps.append("decision_making")
        self.logger.info(f"Decision: {decision.decision.upper()}")
        self.logger.info(f"Reasoning: {decision.reasoning}")
        self.logger.info("")

        # Create workflow result
        result = TapeLibraryWorkflowResult(
            workflow_id=workflow_id,
            timestamp=datetime.now().isoformat(),
            step_1_problem_identification=problem,
            step_2_impact_assessment=impact,
            step_3_root_cause_analysis=root_cause,
            step_4_escalation_determination=escalation,
            step_5_prevention_strategies=prevention,
            step_6_decision_making=decision,
            completed_steps=completed_steps,
            workflow_status="complete",
            next_actions=decision.reasoning.split(". ") if decision.reasoning else []
        )

        # Save workflow result
        self._save_workflow_result(result)

        # If work is blocked/waiting, automatically trigger pathfinder
        if result.workflow_status == "complete" and decision.approval_status == "pending":
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("WORK STOPPAGE DETECTED - Triggering Pathfinder")
            self.logger.info("=" * 70)
            try:
                from tape_library_pathfinder import TapeLibraryPathfinder
                pathfinder = TapeLibraryPathfinder()
                workflow_file = self.data_dir / f"{result.workflow_id}.json"
                pathfinding_result = pathfinder.find_paths_forward(workflow_file)

                # Update next_actions with pathfinder breadcrumbs
                result.next_actions = [
                    crumb.get("action", "") for crumb in pathfinding_result.breadcrumbs
                    if crumb.get("can_execute", False)
                ]

                self.logger.info("")
                self.logger.info(f"Pathfinder found {len(pathfinding_result.breadcrumbs)} breadcrumbs")
                self.logger.info(f"Recommended path: {pathfinding_result.recommended_path.get('name', 'None')}")
                self.logger.info(f"Can proceed with recommended path: {pathfinding_result.can_proceed}")

            except Exception as e:
                self.logger.warning(f"Pathfinder triggered but error occurred: {e}")

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("WORKFLOW COMPLETE")
        self.logger.info("=" * 70)

        return result

    def _identify_problem(self, description: str, data_path: str, 
                         size_bytes: int, reported_by: str) -> ProblemIdentification:
        """Step 1: Identify the problem"""
        problem_id = f"problem-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Identify symptoms
        symptoms = []
        if "space" in description.lower() or "full" in description.lower():
            symptoms.append("Storage space constraint")
        if "snapshot" in description.lower():
            symptoms.append("Snapshot-related issue")
        if "recursive" in description.lower():
            symptoms.append("Recursive data structure")
        if size_bytes > 100 * 1024**3:  # > 100 GB
            symptoms.append("Large data size")

        # Initial urgency
        size_gb = size_bytes / (1024**3)
        if size_gb > 1000:
            urgency = "critical"
        elif size_gb > 100:
            urgency = "high"
        elif size_gb > 10:
            urgency = "medium"
        else:
            urgency = "low"

        return ProblemIdentification(
            problem_id=problem_id,
            timestamp=datetime.now().isoformat(),
            problem_description=description,
            data_path=data_path,
            data_size_bytes=size_bytes,
            symptoms=symptoms,
            reported_by=reported_by,
            urgency_initial=urgency
        )

    def _assess_impact(self, problem: ProblemIdentification) -> ImpactAssessment:
        """Step 2: Assess business impact, customer impact, etc."""
        size_gb = problem.data_size_bytes / (1024**3)

        # Business Impact
        business_impact = {
            "severity": "high" if size_gb > 100 else "medium",
            "storage_costs": f"${size_gb * 0.023:.2f}/month (estimated Dropbox cost)" if size_gb > 100 else "minimal",
            "operational_blocking": size_gb > 1000,
            "compliance_risk": "low",
            "reputation_risk": "low"
        }

        # Customer Impact
        customer_impact = {
            "severity": "low",  # Internal system
            "service_degradation": "potential" if size_gb > 1000 else "none",
            "availability_impact": "none",
            "performance_impact": "potential" if size_gb > 100 else "none"
        }

        # System Impact
        system_impact = {
            "storage_utilization": "high" if size_gb > 500 else "medium",
            "backup_impact": "significant" if size_gb > 100 else "minimal",
            "sync_impact": "potential slowdown" if size_gb > 100 else "none",
            "network_impact": "minimal"
        }

        # Financial Impact
        financial_impact = {
            "storage_cost": size_gb * 0.023,  # Estimated $/GB/month
            "backup_cost": size_gb * 0.005 if size_gb > 100 else 0,
            "operational_cost": "time to resolve",
            "total_estimated_monthly": size_gb * 0.028
        }

        # Operational Impact
        operational_impact = {
            "maintenance_overhead": "high" if size_gb > 100 else "medium",
            "recovery_complexity": "high" if size_gb > 1000 else "medium",
            "management_effort": "ongoing"
        }

        # Risk Level
        if size_gb > 1000 or business_impact["operational_blocking"]:
            risk_level = "critical"
        elif size_gb > 100 or business_impact["severity"] == "high":
            risk_level = "high"
        else:
            risk_level = "medium"

        return ImpactAssessment(
            business_impact=business_impact,
            customer_impact=customer_impact,
            system_impact=system_impact,
            financial_impact=financial_impact,
            operational_impact=operational_impact,
            risk_level=risk_level
        )

    def _analyze_root_cause(self, problem: ProblemIdentification,
                           impact: ImpactAssessment) -> RootCauseAnalysis:
        """Step 3: Analyze root cause"""
        root_cause = "Unknown - requires investigation"
        contributing_factors = []
        evidence = []
        confidence = 0.5

        # Analyze based on symptoms
        if "recursive" in problem.problem_description.lower():
            root_cause = "Recursive snapshot creation - snapshots including snapshot directory"
            contributing_factors = [
                "Snapshot creation process not excluding output directory",
                "Lack of exclusion patterns in backup scripts",
                "No validation of snapshot contents before creation"
            ]
            evidence = [
                "Nested snapshot directories detected",
                "Recursive structure observed in paths"
            ]
            confidence = 0.9

        if problem.data_size_bytes > 100 * 1024**3:
            contributing_factors.append("Large data size amplifying the problem")

        return RootCauseAnalysis(
            root_cause=root_cause,
            contributing_factors=contributing_factors,
            evidence=evidence,
            confidence_level=confidence
        )

    def _determine_escalations(self, problem: ProblemIdentification,
                              impact: ImpactAssessment,
                              root_cause: RootCauseAnalysis) -> EscalationDetermination:
        """Step 4: Determine all escalations required"""
        escalations = []
        escalation_reasons = []
        escalation_levels = []
        approval_required = False
        approval_authorities = []

        size_gb = problem.data_size_bytes / (1024**3)

        # Size-based escalations
        if size_gb > 1000:
            escalations.append({
                "level": "executive",
                "authority": "JARVIS",
                "reason": "Data size exceeds 1 TB threshold"
            })
            escalation_levels.append("executive")
            escalation_reasons.append("Size threshold exceeded")
            approval_required = True
            approval_authorities.append("JARVIS")

        # Risk-based escalations
        if impact.risk_level == "critical":
            escalations.append({
                "level": "management",
                "authority": "Tape Library Team Lead",
                "reason": "Critical risk level identified"
            })
            escalation_levels.append("management")
            escalation_reasons.append("Critical risk")
            approval_required = True
            if "Tape Library Team Lead" not in approval_authorities:
                approval_authorities.append("Tape Library Team Lead")

        # Business impact escalations
        if impact.business_impact.get("operational_blocking"):
            escalations.append({
                "level": "management",
                "authority": "Operations Manager",
                "reason": "Operational blocking issue"
            })
            escalation_levels.append("management")
            escalation_reasons.append("Operational blocking")
            approval_required = True
            if "Operations Manager" not in approval_authorities:
                approval_authorities.append("Operations Manager")

        # Customer impact escalations
        if impact.customer_impact.get("severity") in ["high", "critical"]:
            escalations.append({
                "level": "executive",
                "authority": "Customer Success",
                "reason": "Customer impact identified"
            })
            escalation_levels.append("executive")
            escalation_reasons.append("Customer impact")

        return EscalationDetermination(
            escalations_required=escalations,
            escalation_reasons=escalation_reasons,
            escalation_levels=escalation_levels,
            approval_required=approval_required,
            approval_authorities=approval_authorities
        )

    def _develop_prevention_strategies(self, problem: ProblemIdentification,
                                      impact: ImpactAssessment,
                                      root_cause: RootCauseAnalysis) -> PreventionStrategies:
        """Step 5: Develop prevention strategies"""
        immediate = []
        short_term = []
        long_term = []
        process_improvements = []
        system_changes = []
        monitoring = []

        # Immediate prevention
        immediate.append("Stop creating new snapshots until issue resolved")
        immediate.append("Identify and disable snapshot creation processes")

        # Short-term prevention
        short_term.append("Fix snapshot creation to exclude output directory")
        short_term.append("Update backup scripts with exclusion patterns")
        short_term.append("Add validation checks before snapshot creation")

        # Long-term prevention
        long_term.append("Implement snapshot size limits")
        long_term.append("Add retention policies for snapshots")
        long_term.append("Automated monitoring of snapshot directory size")
        long_term.append("Regular audits of data lifecycle management")

        # Process improvements
        process_improvements.append("Require Tape Library Team review for all data deletion decisions")
        process_improvements.append("Document all snapshot creation processes")
        process_improvements.append("Add pre-creation validation checks")

        # System changes
        system_changes.append("Update backup/snapshot scripts to exclude time_travel/snapshots")
        system_changes.append("Implement automated exclusion pattern validation")
        system_changes.append("Add snapshot directory size monitoring")

        # Monitoring recommendations
        monitoring.append("Monitor snapshot directory size daily")
        monitoring.append("Alert when snapshot directory exceeds 100 GB")
        monitoring.append("Track snapshot creation frequency")
        monitoring.append("Monitor Dropbox space usage")

        return PreventionStrategies(
            immediate_prevention=immediate,
            short_term_prevention=short_term,
            long_term_prevention=long_term,
            process_improvements=process_improvements,
            system_changes=system_changes,
            monitoring_recommendations=monitoring
        )

    def _make_decision(self, problem: ProblemIdentification,
                      impact: ImpactAssessment,
                      root_cause: RootCauseAnalysis,
                      escalation: EscalationDetermination,
                      prevention: PreventionStrategies) -> DecisionMaking:
        """Step 6: Make decision (LAST STEP)"""
        decision_id = f"decision-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Decision logic based on all previous steps
        size_gb = problem.data_size_bytes / (1024**3)

        if escalation.approval_required:
            decision = "escalate"
            reasoning = f"Escalation required: {', '.join(escalation.escalation_reasons)}. Awaiting approval from {', '.join(escalation.approval_authorities)} before proceeding."
            approval_status = "pending"
        elif size_gb > 100 and not impact.business_impact.get("operational_blocking"):
            decision = "archive"
            reasoning = f"Data size ({size_gb:.2f} GB) is significant. Archive to external storage to free space while preserving data. Follow prevention strategies to prevent recurrence."
            approval_status = "approved"
        elif impact.business_impact.get("operational_blocking"):
            decision = "escalate"
            reasoning = "Operational blocking issue. Requires immediate escalation and management approval."
            approval_status = "pending"
        else:
            decision = "archive"
            reasoning = "Archive data to preserve it while freeing space. Follow prevention strategies."
            approval_status = "approved"

        alternatives = ["delete", "archive", "escalate", "monitor", "defer"]
        chosen = decision

        risk_assessment = {
            "data_loss_risk": "high" if decision == "delete" else "low",
            "operational_risk": impact.business_impact.get("severity", "medium"),
            "recovery_complexity": impact.operational_impact.get("recovery_complexity", "medium")
        }

        return DecisionMaking(
            decision_id=decision_id,
            decision=decision,
            reasoning=reasoning,
            alternatives_considered=alternatives,
            chosen_alternative=chosen,
            risk_assessment=risk_assessment,
            approval_status=approval_status
        )

    def _save_workflow_result(self, result: TapeLibraryWorkflowResult):
        try:
            """Save workflow result to disk"""
            result_file = self.data_dir / f"{result.workflow_id}.json"

            # Convert to dict
            result_dict = asdict(result)

            # Handle nested dataclasses
            def convert_dataclass(obj):
                if hasattr(obj, '__dataclass_fields__'):
                    return asdict(obj)
                return obj

            # Recursively convert
            def recursive_convert(d):
                if isinstance(d, dict):
                    return {k: recursive_convert(v) for k, v in d.items()}
                elif isinstance(d, list):
                    return [recursive_convert(item) for item in d]
                else:
                    return convert_dataclass(d) if hasattr(d, '__dataclass_fields__') else d

            result_dict = recursive_convert(result_dict)

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Workflow result saved to: {result_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_workflow_result: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Tape Library Team Workflow - Complete workflow from beginning to end"
    )
    parser.add_argument(
        "--problem",
        type=str,
        required=True,
        help="Problem description"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        required=True,
        help="Path to data"
    )
    parser.add_argument(
        "--size-gb",
        type=float,
        required=True,
        help="Data size in GB"
    )
    parser.add_argument(
        "--reported-by",
        type=str,
        default="system",
        help="Who reported the problem"
    )

    args = parser.parse_args()

    workflow = TapeLibraryWorkflow()

    size_bytes = int(args.size_gb * 1024**3)

    result = workflow.execute_workflow(
        problem_description=args.problem,
        data_path=args.data_path,
        data_size_bytes=size_bytes,
        reported_by=args.reported_by
    )

    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"Decision: {result.step_6_decision_making.decision.upper()}")
    print(f"Approval Status: {result.step_6_decision_making.approval_status}")
    print(f"Reasoning: {result.step_6_decision_making.reasoning}")
    print("=" * 70)

    return 0


if __name__ == "__main__":



    sys.exit(main())