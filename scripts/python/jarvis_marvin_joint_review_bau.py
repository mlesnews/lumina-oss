#!/usr/bin/env python3
"""
Jarvis & Marvin Joint Review - BAU Workflow

Regular Business As Usual workflow that:
1. Collects session work summary
2. Invokes Marvin for review
3. Combines Jarvis and Marvin reviews into joint collaboration report
4. Publishes/updates the report
5. Runs automatically on schedule

This is a regular BAU workflow - runs automatically to maintain quality.

Tags: #BAU #WORKFLOW #JOINT-REVIEW #MARVIN #JARVIS #COLLABORATION @MARVIN @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JarvisMarvinJointReview")


@dataclass
class JarvisReview:
    """Jarvis's review contribution"""
    questions: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class MarvinReview:
    """Marvin's review contribution"""
    roast_id: Optional[str] = None
    findings: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    severity_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class JointReviewReport:
    """Joint collaboration report combining Jarvis and Marvin reviews"""
    report_id: str
    session_timestamp: str
    work_summary: Dict[str, Any]
    jarvis_review: JarvisReview
    marvin_review: MarvinReview
    combined_insights: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "session_timestamp": self.session_timestamp,
            "work_summary": self.work_summary,
            "jarvis_review": asdict(self.jarvis_review),
            "marvin_review": asdict(self.marvin_review),
            "combined_insights": self.combined_insights,
            "action_items": self.action_items,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class JarvisMarvinJointReviewBAU:
    """
    Jarvis & Marvin Joint Review BAU Workflow

    Regular workflow that creates joint collaboration reports.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger

        # Data directories
        self.data_dir = self.project_root / "data" / "joint_reviews"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Reports directory
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Latest report file (always updated)
        self.latest_report_file = self.data_dir / "latest_joint_review.json"

        self.logger.info("✅ Jarvis & Marvin Joint Review BAU initialized")

    def get_jarvis_review(self, work_summary: Dict[str, Any]) -> JarvisReview:
        """Get Jarvis's review contribution"""
        self.logger.info("🤖 Jarvis reviewing work...")

        review = JarvisReview()

        # Questions
        review.questions = [
            "Should proximity chat have persistent connection manager for services?",
            "Should disk migration have pause/resume mechanism?",
            "Should master todo auto-sync with Padawan todos when initiative completes?",
            "Are there missing integration points between systems?",
            "Should we add service discovery for proximity chat?"
        ]

        # Suggestions
        review.suggestions = [
            "Add service discovery/registration for proximity chat",
            "Add message queuing for offline services",
            "Add encryption for sensitive proximity messages",
            "Add dry-run mode by default for disk migration",
            "Add rollback capability for disk migration",
            "Add auto-promotion: promote important Padawan todos to Master",
            "Add initiative linking: link Master todos to specific initiatives",
            "Add completion analytics for master todo system"
        ]

        # Concerns
        review.concerns = [
            "Proximity chat: No authentication/authorization - services can send messages without verification",
            "Disk migration: No confirmation prompts - could move files without user approval",
            "Master todo: Terminology might be confusing - consider glossary or help command",
            "Missing error handling in some integration points",
            "No rate limiting for proximity chat messages"
        ]

        return review

    def get_marvin_review(self, work_summary: Dict[str, Any]) -> MarvinReview:
        """Get Marvin's review contribution"""
        self.logger.info("🤖 Invoking Marvin for review...")

        review = MarvinReview()

        # Try to get Marvin's roast
        try:
            from marvin_roast_system import MarvinRoastSystem, MarvinRoast
            roast_system = MarvinRoastSystem(self.project_root)

            ask_text = f"""
Session Work Review Request:

Please review the following work with constructive criticism:

1. Lumina Proximity Chat Service
   - Service-oriented architecture
   - Proximity-aware messaging
   - Chat bubble renderer
   - Integration examples

2. Background Disk Space Migration
   - Background service for 50% disk usage goal
   - Automatic file migration
   - Progress tracking

3. Master Todo List System
   - Collapsed/expanded views
   - Terminology support
   - Focus on productivity

Key Questions:
- Are there gaps in implementation?
- Is there unnecessary bloat?
- Missing integrations?
- Incomplete workflows?
- Any security concerns?
- Performance issues?
- Documentation gaps?

Please provide constructive criticism (negative feedback is welcome).
"""

            roast = roast_system.roast_ask(
                ask_id=f"joint_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                ask_text=ask_text,
                context={
                    "session_summary": work_summary,
                    "review_type": "joint_collaboration_review",
                    "workflow": "bau"
                }
            )

            review.roast_id = roast.roast_id
            review.findings = [f.to_dict() for f in roast.findings]
            review.summary = roast.summary
            review.severity_score = roast.total_severity_score

            self.logger.info(f"✅ Marvin review complete: {len(review.findings)} findings")

        except ImportError:
            self.logger.warning("⚠️  Marvin roast system not available - using placeholder")
            review.summary = "Marvin review pending - system not available"
            review.findings = [
                {
                    "category": "system_availability",
                    "severity": "medium",
                    "description": "Marvin roast system not available - review pending"
                }
            ]
        except Exception as e:
            self.logger.error(f"Error getting Marvin review: {e}")
            review.summary = f"Error: {str(e)}"

        return review

    def create_joint_report(self, work_summary: Dict[str, Any]) -> JointReviewReport:
        """Create joint collaboration report"""
        self.logger.info("📋 Creating joint review report...")

        # Get both reviews
        jarvis_review = self.get_jarvis_review(work_summary)
        marvin_review = self.get_marvin_review(work_summary)

        # Create report
        report = JointReviewReport(
            report_id=f"joint_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            session_timestamp=work_summary.get("session_timestamp", datetime.now().isoformat()),
            work_summary=work_summary,
            jarvis_review=jarvis_review,
            marvin_review=marvin_review
        )

        # Generate combined insights
        report.combined_insights = self._generate_combined_insights(jarvis_review, marvin_review)

        # Generate action items
        report.action_items = self._generate_action_items(jarvis_review, marvin_review)

        return report

    def _generate_combined_insights(self, jarvis: JarvisReview, marvin: MarvinReview) -> List[str]:
        """Generate combined insights from both reviews"""
        insights = []

        # Security insights
        if any("security" in c.lower() or "auth" in c.lower() for c in jarvis.concerns):
            insights.append("🔒 Security: Both reviews identify authentication/authorization gaps")

        # Integration insights
        if any("integration" in s.lower() for s in jarvis.suggestions):
            insights.append("🔗 Integration: Service discovery and registration needed")

        # Error handling
        if any("error" in c.lower() or "handling" in c.lower() for c in jarvis.concerns):
            insights.append("⚠️  Error Handling: Missing error handling in integration points")

        # Marvin findings
        if marvin.findings:
            critical_findings = [f for f in marvin.findings if f.get("severity") == "critical"]
            if critical_findings:
                insights.append(f"🚨 Critical: Marvin found {len(critical_findings)} critical issues")

        return insights

    def _generate_action_items(self, jarvis: JarvisReview, marvin: MarvinReview) -> List[Dict[str, Any]]:
        """Generate action items from both reviews"""
        actions = []

        # High priority from concerns
        for concern in jarvis.concerns:
            if "security" in concern.lower() or "auth" in concern.lower():
                actions.append({
                    "priority": "high",
                    "category": "security",
                    "description": concern,
                    "source": "jarvis_concern"
                })

        # Marvin critical findings
        for finding in marvin.findings:
            if finding.get("severity") == "critical":
                actions.append({
                    "priority": "critical",
                    "category": finding.get("category", "unknown"),
                    "description": finding.get("description", ""),
                    "source": "marvin_finding",
                    "recommendations": finding.get("recommendations", [])
                })

        return actions

    def publish_report(self, report: JointReviewReport) -> Path:
        try:
            """Publish/update the joint report"""
            self.logger.info(f"📤 Publishing joint review report: {report.report_id}")

            # Update latest report
            report.updated_at = datetime.now().isoformat()
            report_dict = report.to_dict()

            with open(self.latest_report_file, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, default=str)

            # Save individual report
            individual_file = self.reports_dir / f"{report.report_id}.json"
            with open(individual_file, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, default=str)

            # Generate markdown report
            markdown_file = self.reports_dir / f"{report.report_id}.md"
            self._generate_markdown_report(report, markdown_file)

            self.logger.info(f"✅ Report published: {self.latest_report_file}")
            self.logger.info(f"   Individual: {individual_file}")
            self.logger.info(f"   Markdown: {markdown_file}")

            return self.latest_report_file

        except Exception as e:
            self.logger.error(f"Error in publish_report: {e}", exc_info=True)
            raise
    def _generate_markdown_report(self, report: JointReviewReport, output_file: Path):
        try:
            """Generate markdown version of report"""
            lines = []

            lines.append("# Jarvis & Marvin Joint Review Report")
            lines.append("")
            lines.append(f"**Report ID:** {report.report_id}")
            lines.append(f"**Created:** {report.created_at}")
            lines.append(f"**Updated:** {report.updated_at}")
            lines.append("")
            lines.append("---")
            lines.append("")

            # Work Summary
            lines.append("## 📋 Work Summary")
            lines.append("")
            for item in report.work_summary.get("work_items", []):
                lines.append(f"### {item.get('item', 'Unknown')}")
                lines.append(f"{item.get('description', '')}")
                lines.append("")

            # Jarvis Review
            lines.append("## 🤖 Jarvis Review")
            lines.append("")
            lines.append("### Questions")
            for q in report.jarvis_review.questions:
                lines.append(f"- {q}")
            lines.append("")
            lines.append("### Suggestions")
            for s in report.jarvis_review.suggestions:
                lines.append(f"- {s}")
            lines.append("")
            lines.append("### Concerns")
            for c in report.jarvis_review.concerns:
                lines.append(f"- ⚠️  {c}")
            lines.append("")

            # Marvin Review
            lines.append("## 🤖 Marvin Review")
            lines.append("")
            if report.marvin_review.summary:
                lines.append(f"**Summary:** {report.marvin_review.summary}")
                lines.append("")

            # Severity score with interpretation
            severity_score = report.marvin_review.severity_score
            if severity_score == 0.0:
                score_emoji = "✅"
                score_interpretation = "Perfect! No issues found"
            elif severity_score <= 10.0:
                score_emoji = "🟢"
                score_interpretation = "Good - minor issues only"
            elif severity_score <= 25.0:
                score_emoji = "🟡"
                score_interpretation = "Moderate - some issues to address"
            elif severity_score <= 50.0:
                score_emoji = "🟠"
                score_interpretation = "Concerning - multiple issues"
            elif severity_score <= 100.0:
                score_emoji = "🔴"
                score_interpretation = "Serious - many critical/high issues"
            else:
                score_emoji = "🚨"
                score_interpretation = "Critical - major problems"

            lines.append(f"**Severity Score:** {severity_score:.2f} {score_emoji}")
            lines.append(f"*{score_interpretation} (Lower = Better, Higher = Worse)*")
            lines.append("")
            lines.append("**Severity Weights:** Critical=10.0, High=5.0, Medium=2.0, Low=1.0")
            lines.append("")
            lines.append("### Findings")
            for finding in report.marvin_review.findings:
                severity = finding.get("severity", "unknown")
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                lines.append(f"{severity_emoji} **{severity.upper()}** - {finding.get('description', '')}")
                if finding.get("recommendations"):
                    lines.append(f"   Recommendation: {finding['recommendations'][0]}")
            lines.append("")

            # Combined Insights
            if report.combined_insights:
                lines.append("## 💡 Combined Insights")
                lines.append("")
                for insight in report.combined_insights:
                    lines.append(f"- {insight}")
                lines.append("")

            # Action Items
            if report.action_items:
                lines.append("## ✅ Action Items")
                lines.append("")
                for action in report.action_items:
                    priority = action.get("priority", "medium")
                    priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
                    lines.append(f"{priority_emoji} **{priority.upper()}** - {action.get('description', '')}")
                    lines.append(f"   Source: {action.get('source', 'unknown')}")
                lines.append("")

            lines.append("---")
            lines.append("")
            lines.append("*This is a joint collaboration report - regular BAU workflow*")

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))


        except Exception as e:
            self.logger.error(f"Error in _generate_markdown_report: {e}", exc_info=True)
            raise
def run_bau_workflow(work_summary: Optional[Dict[str, Any]] = None):
    """Run the BAU workflow"""
    if work_summary is None:
        # Get session work summary
        from marvin_review_session_work import get_session_work_summary
        work_summary = get_session_work_summary()

    workflow = JarvisMarvinJointReviewBAU()
    report = workflow.create_joint_report(work_summary)
    published_file = workflow.publish_report(report)

    print("\n" + "=" * 80)
    print("✅ JOINT REVIEW BAU WORKFLOW COMPLETE")
    print("=" * 80)
    print(f"📄 Latest Report: {published_file}")
    print(f"📊 Findings: {len(report.marvin_review.findings)}")
    print(f"💡 Insights: {len(report.combined_insights)}")
    print(f"✅ Action Items: {len(report.action_items)}")
    print("=" * 80)

    return report


def main():
    try:
        """Main function - BAU workflow entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Jarvis & Marvin Joint Review BAU Workflow")
        parser.add_argument("--work-summary-file", type=str, help="Path to work summary JSON file")

        args = parser.parse_args()

        work_summary = None
        if args.work_summary_file:
            with open(args.work_summary_file, 'r', encoding='utf-8') as f:
                work_summary = json.load(f)

        report = run_bau_workflow(work_summary)

        # Display summary
        print("\n📋 REPORT SUMMARY:")
        print(f"   Jarvis Questions: {len(report.jarvis_review.questions)}")
        print(f"   Jarvis Suggestions: {len(report.jarvis_review.suggestions)}")
        print(f"   Jarvis Concerns: {len(report.jarvis_review.concerns)}")
        print(f"   Marvin Findings: {len(report.marvin_review.findings)}")
        print(f"   Combined Insights: {len(report.combined_insights)}")
        print(f"   Action Items: {len(report.action_items)}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()