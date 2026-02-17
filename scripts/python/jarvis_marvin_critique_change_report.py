#!/usr/bin/env python3
"""
JARVIS & MARVIN Change Report Critique

MARVIN does his worst (critical analysis), then JARVIS balances it out.
Generates implementation plan based on their feedback.

Tags: #CRITIQUE #REVIEW #MARVIN #JARVIS #IMPLEMENTATION_PLAN @JARVIS @MARVIN @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("JARVISMARVINCritique")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISMARVINCritique")


class JARVISMARVINChangeReportCritique:
    """
    JARVIS & MARVIN critique the executive change report

    MARVIN: Does his worst - critical, harsh, reality-checking
    JARVIS: Balances it out - systematic, measured, actionable
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "data" / "executive_reports"
        self.critiques_dir = self.project_root / "data" / "executive_reports" / "critiques"
        self.critiques_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("🎭 JARVIS & MARVIN CHANGE REPORT CRITIQUE")
        logger.info("=" * 80)
        logger.info("   MARVIN: Doing his worst (critical analysis)")
        logger.info("   JARVIS: Balancing it out (systematic review)")
        logger.info("   Output: Implementation plan")
        logger.info("")

    def load_report(self, report_file: Optional[Path] = None) -> Dict[str, Any]:
        try:
            """Load the executive change report"""
            if report_file is None:
                # Find latest report
                reports = list(self.reports_dir.glob("change_report_*.json"))
                if not reports:
                    raise FileNotFoundError("No change report found")
                report_file = max(reports, key=lambda p: p.stat().st_mtime)

            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)

            logger.info(f"📄 Loaded report: {report_file.name}")
            logger.info(f"   Version: {report['version_info']['version']}")
            logger.info("")

            return report

        except Exception as e:
            self.logger.error(f"Error in load_report: {e}", exc_info=True)
            raise
    def marvin_critique(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        MARVIN does his worst - critical, harsh, reality-checking

        MARVIN's style: Existential, critical, finds all the problems
        """
        logger.info("=" * 80)
        logger.info("🤖 MARVIN'S CRITIQUE (Doing His Worst)")
        logger.info("=" * 80)
        logger.info("")

        critique = {
            "critic": "MARVIN",
            "tone": "critical",
            "style": "existential_reality_check",
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "concerns": [],
            "missing_elements": [],
            "overstatements": [],
            "reality_checks": [],
            "harsh_truths": []
        }

        version_info = report.get("version_info", {})
        features = report.get("features_by_category", {})
        summary = report.get("summary", {})

        # MARVIN's harsh truths
        logger.info("MARVIN: *sigh* Let me tell you what's wrong with this report...")
        logger.info("")

        # Issue 1: Version numbers are arbitrary
        critique["harsh_truths"].append({
            "issue": "Version numbers don't reflect actual change magnitude",
            "details": f"Jumping from 0.9.0 to 1.0.0 suggests major milestone, but only {summary.get('total_new_features', 0)} features? That's not a major version bump.",
            "severity": "medium"
        })
        logger.info("   ⚠️  Version numbers are arbitrary - 0.9.0 to 1.0.0 with only 7 features?")

        # Issue 2: Missing validation
        critique["concerns"].append({
            "issue": "No validation of claimed features",
            "details": "Report claims features exist, but where's the proof? No test results, no metrics, no validation.",
            "severity": "high"
        })
        logger.info("   ⚠️  No validation - claims features exist but no proof")

        # Issue 3: Overstatement of integration
        critique["overstatements"].append({
            "issue": "Claims 'unified roof' but systems may still be fragmented",
            "details": "Saying everything is 'under one roof' doesn't make it true. Are they actually integrated or just listed together?",
            "severity": "high"
        })
        logger.info("   ⚠️  'Unified roof' claim may be overstated - are systems actually integrated?")

        # Issue 4: Missing metrics
        critique["missing_elements"].append({
            "element": "Performance metrics",
            "details": "No actual performance numbers, no benchmarks, no before/after comparisons",
            "severity": "medium"
        })
        logger.info("   ⚠️  Missing performance metrics - no numbers, no benchmarks")

        # Issue 5: Contributing systems credit is vague
        critique["concerns"].append({
            "issue": "Credit given but contribution unclear",
            "details": "Lists 21 contributing systems but doesn't explain what each actually contributed. Is this real credit or just name-dropping?",
            "severity": "medium"
        })
        logger.info("   ⚠️  Contributing systems listed but actual contributions unclear")

        # Issue 6: No implementation timeline
        critique["missing_elements"].append({
            "element": "Implementation timeline",
            "details": "Report says 'new features' but when were they implemented? What's the actual deployment status?",
            "severity": "high"
        })
        logger.info("   ⚠️  No implementation timeline - when were features actually deployed?")

        # Issue 7: Business value unclear
        critique["reality_checks"].append({
            "check": "Business value not quantified",
            "details": "For a 'board member' report, there's no ROI, no business impact, no user benefits quantified. Just a feature list.",
            "severity": "high"
        })
        logger.info("   ⚠️  Business value not quantified - no ROI, no impact metrics")

        # Issue 8: Testing status unknown
        critique["concerns"].append({
            "issue": "Testing and quality assurance status missing",
            "details": "Are these features tested? Production-ready? Or just implemented?",
            "severity": "high"
        })
        logger.info("   ⚠️  Testing status unknown - are features production-ready?")

        # MARVIN's existential conclusion
        critique["harsh_truths"].append({
            "issue": "Report reads like marketing, not engineering",
            "details": "This is a feature list with nice formatting, not an engineering change report. Where's the technical depth?",
            "severity": "medium"
        })
        logger.info("   ⚠️  Report reads like marketing, not engineering")
        logger.info("")

        logger.info("MARVIN: *sigh* Life is meaningless, but at least I've pointed out the problems.")
        logger.info("")

        return critique

    def jarvis_balance(self, report: Dict[str, Any], marvin_critique: Dict[str, Any]) -> Dict[str, Any]:
        """
        JARVIS balances it out - systematic, measured, actionable

        JARVIS's style: Systematic, balanced, solution-oriented
        """
        logger.info("=" * 80)
        logger.info("🤖 JARVIS'S BALANCED ANALYSIS")
        logger.info("=" * 80)
        logger.info("")

        logger.info("JARVIS: Thank you, MARVIN, for the critical analysis. Let me provide a balanced perspective.")
        logger.info("")

        analysis = {
            "analyst": "JARVIS",
            "tone": "balanced",
            "style": "systematic_solution_oriented",
            "timestamp": datetime.now().isoformat(),
            "acknowledgments": [],
            "valid_points": [],
            "additions_needed": [],
            "improvements": [],
            "actionable_items": [],
            "positive_aspects": []
        }

        # Acknowledge MARVIN's valid points
        logger.info("✅ Acknowledging MARVIN's valid concerns:")
        analysis["acknowledgments"].append({
            "point": "Version numbering needs justification",
            "action": "Add versioning rationale and change magnitude assessment"
        })
        logger.info("   - Version numbering needs better justification")

        analysis["acknowledgments"].append({
            "point": "Validation and metrics are essential",
            "action": "Add validation section with test results and metrics"
        })
        logger.info("   - Validation and metrics are essential")

        analysis["acknowledgments"].append({
            "point": "Business value should be quantified",
            "action": "Add ROI, impact metrics, and business value section"
        })
        logger.info("   - Business value should be quantified")
        logger.info("")

        # Positive aspects
        logger.info("✅ Positive aspects of the report:")
        analysis["positive_aspects"].append({
            "aspect": "Comprehensive feature categorization",
            "details": "Well-organized by category (Personal Assistance, Coding, IDE, etc.)"
        })
        logger.info("   - Well-organized feature categorization")

        analysis["positive_aspects"].append({
            "aspect": "Proper credit to contributing systems",
            "details": "Acknowledges all 21 contributing systems"
        })
        logger.info("   - Proper credit to contributing systems")

        analysis["positive_aspects"].append({
            "aspect": "Clear executive summary",
            "details": "Appropriate level of detail for board members"
        })
        logger.info("   - Appropriate level for executive audience")
        logger.info("")

        # Improvements needed
        logger.info("📋 Improvements needed:")
        analysis["improvements"].append({
            "improvement": "Add validation section",
            "details": "Include test results, metrics, benchmarks for each feature category",
            "priority": "high"
        })
        logger.info("   - Add validation section with test results and metrics")

        analysis["improvements"].append({
            "improvement": "Add business value section",
            "details": "Quantify ROI, user impact, efficiency gains, cost savings",
            "priority": "high"
        })
        logger.info("   - Add business value section with ROI and impact metrics")

        analysis["improvements"].append({
            "improvement": "Add implementation timeline",
            "details": "Show when features were implemented, deployment status, rollout plan",
            "priority": "medium"
        })
        logger.info("   - Add implementation timeline and deployment status")

        analysis["improvements"].append({
            "improvement": "Add technical depth appendix",
            "details": "For engineering review, include technical details, architecture changes, integration points",
            "priority": "medium"
        })
        logger.info("   - Add technical depth appendix for engineering review")

        analysis["improvements"].append({
            "improvement": "Clarify system contributions",
            "details": "For each contributing system, specify what they actually contributed",
            "priority": "low"
        })
        logger.info("   - Clarify actual contributions from each system")
        logger.info("")

        # Actionable items
        logger.info("🎯 Actionable items for implementation plan:")
        analysis["actionable_items"] = [
            {
                "action": "Enhance report with validation section",
                "priority": "high",
                "effort": "medium"
            },
            {
                "action": "Add business value quantification",
                "priority": "high",
                "effort": "high"
            },
            {
                "action": "Create implementation timeline",
                "priority": "medium",
                "effort": "low"
            },
            {
                "action": "Add technical appendix",
                "priority": "medium",
                "effort": "medium"
            },
            {
                "action": "Clarify system contributions",
                "priority": "low",
                "effort": "low"
            }
        ]

        logger.info("JARVIS: The report is a good foundation. With MARVIN's critical feedback")
        logger.info("        and these improvements, it will be production-ready.")
        logger.info("")

        return analysis

    def generate_implementation_plan(
        self,
        report: Dict[str, Any],
        marvin_critique: Dict[str, Any],
        jarvis_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate implementation plan based on JARVIS & MARVIN feedback"""
        logger.info("=" * 80)
        logger.info("📋 GENERATING IMPLEMENTATION PLAN")
        logger.info("=" * 80)
        logger.info("")

        plan = {
            "plan_type": "Change Report Enhancement Implementation Plan",
            "generated_at": datetime.now().isoformat(),
            "based_on": {
                "report_version": report["version_info"]["version"],
                "marvin_critique": marvin_critique["timestamp"],
                "jarvis_analysis": jarvis_analysis["timestamp"]
            },
            "phases": [],
            "priorities": {
                "high": [],
                "medium": [],
                "low": []
            },
            "estimated_effort": {},
            "success_criteria": []
        }

        # Phase 1: Critical Enhancements (MARVIN's high-severity issues)
        phase1 = {
            "phase": 1,
            "name": "Critical Enhancements",
            "description": "Address MARVIN's high-severity concerns",
            "tasks": [
                {
                    "task": "Add validation section",
                    "description": "Include test results, metrics, benchmarks for each feature",
                    "priority": "high",
                    "effort": "medium",
                    "owner": "Engineering",
                    "deliverables": [
                        "Test results per feature category",
                        "Performance benchmarks",
                        "Before/after comparisons"
                    ]
                },
                {
                    "task": "Add business value quantification",
                    "description": "Quantify ROI, user impact, efficiency gains",
                    "priority": "high",
                    "effort": "high",
                    "owner": "Product/Business",
                    "deliverables": [
                        "ROI calculations",
                        "User impact metrics",
                        "Efficiency gain measurements",
                        "Cost savings analysis"
                    ]
                },
                {
                    "task": "Add implementation timeline",
                    "description": "Show deployment status and rollout plan",
                    "priority": "high",
                    "effort": "low",
                    "owner": "Project Management",
                    "deliverables": [
                        "Feature deployment timeline",
                        "Rollout status per feature",
                        "Future roadmap"
                    ]
                }
            ]
        }
        plan["phases"].append(phase1)

        # Phase 2: Quality Improvements
        phase2 = {
            "phase": 2,
            "name": "Quality Improvements",
            "description": "Enhance report quality and depth",
            "tasks": [
                {
                    "task": "Add technical appendix",
                    "description": "Technical details for engineering review",
                    "priority": "medium",
                    "effort": "medium",
                    "owner": "Engineering",
                    "deliverables": [
                        "Architecture changes",
                        "Integration points",
                        "Technical specifications"
                    ]
                },
                {
                    "task": "Clarify system contributions",
                    "description": "Specify what each system actually contributed",
                    "priority": "medium",
                    "effort": "low",
                    "owner": "Documentation",
                    "deliverables": [
                        "Contribution matrix",
                        "System-specific feature lists"
                    ]
                },
                {
                    "task": "Add testing status",
                    "description": "Document QA status for each feature",
                    "priority": "medium",
                    "effort": "low",
                    "owner": "QA",
                    "deliverables": [
                        "Testing status per feature",
                        "Production readiness assessment"
                    ]
                }
            ]
        }
        plan["phases"].append(phase2)

        # Phase 3: Polish and Finalization
        phase3 = {
            "phase": 3,
            "name": "Polish and Finalization",
            "description": "Final touches and review",
            "tasks": [
                {
                    "task": "Version numbering rationale",
                    "description": "Justify version jump from 0.9.0 to 1.0.0",
                    "priority": "low",
                    "effort": "low",
                    "owner": "Product",
                    "deliverables": [
                        "Versioning rationale document"
                    ]
                },
                {
                    "task": "Executive review",
                    "description": "Final review with stakeholders",
                    "priority": "low",
                    "effort": "low",
                    "owner": "Executive",
                    "deliverables": [
                        "Approved change report"
                    ]
                }
            ]
        }
        plan["phases"].append(phase3)

        # Organize by priority
        for phase in plan["phases"]:
            for task in phase["tasks"]:
                priority = task["priority"]
                plan["priorities"][priority].append(task)

        # Success criteria
        plan["success_criteria"] = [
            "All high-priority MARVIN concerns addressed",
            "Business value quantified and validated",
            "Implementation timeline documented",
            "Technical depth sufficient for engineering review",
            "Executive approval obtained"
        ]

        logger.info("✅ Implementation plan generated")
        logger.info(f"   Phases: {len(plan['phases'])}")
        logger.info(f"   High Priority Tasks: {len(plan['priorities']['high'])}")
        logger.info(f"   Medium Priority Tasks: {len(plan['priorities']['medium'])}")
        logger.info(f"   Low Priority Tasks: {len(plan['priorities']['low'])}")
        logger.info("")

        return plan

    def save_critique(self, report: Dict, marvin: Dict, jarvis: Dict, plan: Dict) -> Path:
        try:
            """Save complete critique and implementation plan"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version = report["version_info"]["version"]

            critique_file = self.critiques_dir / f"critique_v{version}_{timestamp}.json"

            complete_critique = {
                "report_reviewed": {
                    "version": version,
                    "file": "change_report_v1.0.0_*.json"
                },
                "marvin_critique": marvin,
                "jarvis_analysis": jarvis,
                "implementation_plan": plan,
                "generated_at": datetime.now().isoformat()
            }

            with open(critique_file, 'w', encoding='utf-8') as f:
                json.dump(complete_critique, f, indent=2, ensure_ascii=False)

            logger.info(f"📁 Critique saved: {critique_file}")

            return critique_file

        except Exception as e:
            self.logger.error(f"Error in save_critique: {e}", exc_info=True)
            raise
    def print_summary(self, marvin: Dict, jarvis: Dict, plan: Dict):
        """Print summary of critique and plan"""
        print("=" * 80)
        print("🎭 JARVIS & MARVIN CRITIQUE SUMMARY")
        print("=" * 80)
        print("")
        print("MARVIN'S CONCERNS:")
        print(f"   - Issues Found: {len(marvin.get('issues', []))}")
        print(f"   - Harsh Truths: {len(marvin.get('harsh_truths', []))}")
        print(f"   - Missing Elements: {len(marvin.get('missing_elements', []))}")
        print("")
        print("JARVIS'S BALANCE:")
        print(f"   - Valid Points Acknowledged: {len(jarvis.get('acknowledgments', []))}")
        print(f"   - Improvements Identified: {len(jarvis.get('improvements', []))}")
        print(f"   - Actionable Items: {len(jarvis.get('actionable_items', []))}")
        print("")
        print("IMPLEMENTATION PLAN:")
        print(f"   - Phases: {len(plan.get('phases', []))}")
        print(f"   - High Priority Tasks: {len(plan.get('priorities', {}).get('high', []))}")
        print(f"   - Medium Priority Tasks: {len(plan.get('priorities', {}).get('medium', []))}")
        print(f"   - Low Priority Tasks: {len(plan.get('priorities', {}).get('low', []))}")
        print("")
        print("=" * 80)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS & MARVIN critique change report")
    parser.add_argument("--report", type=Path, help="Path to change report JSON file")
    parser.add_argument("--save", action="store_true", help="Save critique and plan")

    args = parser.parse_args()

    critique_system = JARVISMARVINChangeReportCritique()

    # Load report
    report = critique_system.load_report(args.report)

    # MARVIN's critique
    marvin_critique = critique_system.marvin_critique(report)

    # JARVIS's balance
    jarvis_analysis = critique_system.jarvis_balance(report, marvin_critique)

    # Generate implementation plan
    implementation_plan = critique_system.generate_implementation_plan(
        report, marvin_critique, jarvis_analysis
    )

    # Print summary
    critique_system.print_summary(marvin_critique, jarvis_analysis, implementation_plan)

    # Save if requested
    if args.save:
        critique_system.save_critique(report, marvin_critique, jarvis_analysis, implementation_plan)

    return {
        "marvin": marvin_critique,
        "jarvis": jarvis_analysis,
        "plan": implementation_plan
    }


if __name__ == "__main__":

    main()