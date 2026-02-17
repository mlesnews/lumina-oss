#!/usr/bin/env python3
"""
Lumina Project Roast and Repair (RR) Session
Applying RR technique to the entire Lumina project

Technique: Rest, Roast, and Repair
1. REST: Pause, observe, analyze current state of entire project
2. ROAST: Critically identify issues, problems, gaps across all components
3. REPAIR: Fix issues systematically, one at a time

@LUMINA @RR #PROJECT_ANALYSIS
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ProjectRoastAndRepair")


class RoastCategory(Enum):
    """Categories for roasting the entire project"""
    INFRASTRUCTURE = "infrastructure"  # Azure, Docker, deployment
    ARCHITECTURE = "architecture"  # System design, APIs, services
    CODE_QUALITY = "code_quality"  # Bugs, syntax errors, standards
    INTEGRATION = "integration"  # Service communication, APIs
    PERFORMANCE = "performance"  # Speed, efficiency, scalability
    SECURITY = "security"  # Authentication, encryption, vulnerabilities
    DOCUMENTATION = "documentation"  # READMEs, guides, API docs
    AUTOMATION = "automation"  # CI/CD, testing, deployment scripts


@dataclass
class RoastIssue:
    """A specific issue identified during project roasting"""
    category: RoastCategory
    component: str  # Which part of the system
    description: str
    severity: str  # "critical", "high", "medium", "low"
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    repaired: bool = False
    repair_notes: str = ""


@dataclass
class ProjectRoastSession:
    """A complete roast and repair session for the entire project"""
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[RoastIssue] = field(default_factory=list)
    repairs_applied: List[str] = field(default_factory=list)
    status: str = "rest"  # "rest", "roast", "repair", "complete"


class ProjectRoastAndRepair:
    """
    RR System for the entire Lumina project

    A granular focus technique for developing the complete system:
    1. REST: Pause, observe, analyze current state of all components
    2. ROAST: Critically identify issues, problems, gaps across the project
    3. REPAIR: Fix issues systematically, one at a time
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Project RR System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "project_rr_sessions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.current_session: Optional[ProjectRoastSession] = None

        logger.info("=" * 80)
        logger.info("🔥 LUMINA PROJECT ROAST AND REPAIR (RR) SYSTEM")
        logger.info("   Rest, Roast, and Repair - Granular Focus for Complete System")
        logger.info("=" * 80)

    def rest(self, description: str = "Analyzing entire Lumina project's current state") -> ProjectRoastSession:
        """
        REST: Pause, observe, analyze current state of entire project

        Args:
            description: What we're observing

        Returns:
            ProjectRoastSession ready for roasting
        """
        session_id = f"project_rr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_session = ProjectRoastSession(
            session_id=session_id,
            status="rest"
        )

        logger.info("")
        logger.info("=" * 80)
        logger.info("😴 REST: Observing Lumina Project's Current State")
        logger.info("=" * 80)
        logger.info(f"   Session: {session_id}")
        logger.info(f"   Focus: {description}")
        logger.info("")
        logger.info("📊 Analyzing all components:")
        logger.info("   - Infrastructure (Azure, Docker, deployment)")
        logger.info("   - Architecture (APIs, services, system design)")
        logger.info("   - Code Quality (bugs, syntax, standards)")
        logger.info("   - Integration (service communication, APIs)")
        logger.info("   - Performance (speed, efficiency, scalability)")
        logger.info("   - Security (auth, encryption, vulnerabilities)")
        logger.info("   - Documentation (READMEs, guides, API docs)")
        logger.info("   - Automation (CI/CD, testing, scripts)")
        logger.info("")

        return self.current_session

    def roast(self, category: RoastCategory, component: str, description: str,
              severity: str = "medium", evidence: Optional[List[str]] = None) -> RoastIssue:
        """
        ROAST: Critically identify issues, problems, gaps across the project

        Args:
            category: Category of issue
            component: Which component/system
            description: What's wrong
            severity: How bad is it
            evidence: Supporting evidence

        Returns:
            RoastIssue
        """
        if not self.current_session:
            self.rest("Starting comprehensive project roast session")

        if self.current_session.status == "rest":
            self.current_session.status = "roast"
            logger.info("")
            logger.info("=" * 80)
            logger.info("🔥 ROAST: Critically Identifying Project Issues")
            logger.info("=" * 80)
            logger.info("")

        issue = RoastIssue(
            category=category,
            component=component,
            description=description,
            severity=severity,
            evidence=evidence or []
        )

        self.current_session.issues.append(issue)

        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }.get(severity, "⚪")

        logger.info(f"{severity_emoji} [{category.value.upper()}] [{component}] {description}")
        if issue.evidence:
            for ev in issue.evidence:
                logger.info(f"   📋 Evidence: {ev}")

        return issue

    def repair(self, issue: Optional[RoastIssue] = None,
               repair_action: Optional[str] = None) -> bool:
        """
        REPAIR: Fix issues systematically, one at a time

        Args:
            issue: Issue to repair (if None, repairs next issue)
            repair_action: What was done to repair

        Returns:
            True if repaired successfully
        """
        if not self.current_session:
            logger.error("❌ No active session - call rest() first")
            return False

        if self.current_session.status == "roast":
            self.current_session.status = "repair"
            logger.info("")
            logger.info("=" * 80)
            logger.info("🔧 REPAIR: Fixing Project Issues Systematically")
            logger.info("=" * 80)
            logger.info("")

        # If no issue specified, get next unrepaired issue
        if issue is None:
            unrepaired = [i for i in self.current_session.issues if not i.repaired]
            if not unrepaired:
                logger.info("✅ All project issues repaired!")
                self.current_session.status = "complete"
                return True
            issue = unrepaired[0]  # Start with first unrepaired

        # Mark as repaired
        issue.repaired = True
        issue.repair_notes = repair_action or "Repaired"

        self.current_session.repairs_applied.append(
            f"[{issue.category.value}] [{issue.component}] {issue.description}: {repair_action or 'Fixed'}"
        )

        logger.info(f"✅ REPAIRED: [{issue.category.value.upper()}] [{issue.component}] {issue.description}")
        if repair_action:
            logger.info(f"   🔧 Action: {repair_action}")
        logger.info("")

        return True

    def save_session(self) -> Path:
        """Save current session to disk"""
        if not self.current_session:
            logger.error("❌ No active session to save")
            return None

        session_file = self.data_dir / f"{self.current_session.session_id}.json"

        session_data = {
            "session_id": self.current_session.session_id,
            "timestamp": self.current_session.timestamp.isoformat(),
            "status": self.current_session.status,
            "issues": [
                {
                    "category": issue.category.value,
                    "component": issue.component,
                    "description": issue.description,
                    "severity": issue.severity,
                    "evidence": issue.evidence,
                    "timestamp": issue.timestamp.isoformat(),
                    "repaired": issue.repaired,
                    "repair_notes": issue.repair_notes
                }
                for issue in self.current_session.issues
            ],
            "repairs_applied": self.current_session.repairs_applied
        }

        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"💾 Project RR session saved: {session_file}")
            return session_file
        except Exception as e:
            logger.error(f"❌ Failed to save session: {e}")
            return None

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        if not self.current_session:
            return {"status": "no_session"}

        total_issues = len(self.current_session.issues)
        repaired_issues = sum(1 for i in self.current_session.issues if i.repaired)

        by_category = {}
        by_component = {}
        by_severity = {}

        for issue in self.current_session.issues:
            cat = issue.category.value
            comp = issue.component
            sev = issue.severity

            by_category[cat] = by_category.get(cat, 0) + 1
            by_component[comp] = by_component.get(comp, 0) + 1
            by_severity[sev] = by_severity.get(sev, 0) + 1

        return {
            "session_id": self.current_session.session_id,
            "status": self.current_session.status,
            "total_issues": total_issues,
            "repaired_issues": repaired_issues,
            "remaining_issues": total_issues - repaired_issues,
            "by_category": by_category,
            "by_component": by_component,
            "by_severity": by_severity,
            "repairs_applied": len(self.current_session.repairs_applied)
        }


def analyze_project_issues(rr: ProjectRoastAndRepair) -> None:
    """Analyze the entire Lumina project for issues"""

    # Based on the status files and analysis, identify real issues

    # CODE QUALITY ISSUES
    rr.roast(
        RoastCategory.CODE_QUALITY,
        "RR System Script",
        "Syntax errors in kenny_roast_and_repair.py preventing execution",
        severity="high",
        evidence=[
            "try/except blocks malformed - missing proper exception handling",
            "Missing import for 'time' module",
            "Logger instance variable references incorrect (self.logger vs logger)"
        ]
    )

    rr.roast(
        RoastCategory.CODE_QUALITY,
        "apply_anthropic_learnings.py",
        "Final syntax error on line 421 needs fixing",
        severity="medium",
        evidence=[
            "AUTOMATION_STATUS.md indicates 1 remaining syntax error",
            "File: apply_anthropic_learnings.py, Line: 421"
        ]
    )

    # INFRASTRUCTURE ISSUES
    rr.roast(
        RoastCategory.INFRASTRUCTURE,
        "Azure Service Bus",
        "Azure Service Bus SDK not installed, causing fallback to file-based system",
        severity="medium",
        evidence=[
            "Warning: 'Azure Service Bus SDK not installed'",
            "R5 using file-based fallback instead of proper Service Bus"
        ]
    )

    # AUTOMATION ISSUES
    rr.roast(
        RoastCategory.AUTOMATION,
        "Test Suite",
        "Battle testing framework exists but may have gaps in coverage",
        severity="low",
        evidence=[
            "12 total tests, 6 passing, 6 expected failures (containers not deployed)",
            "Need 100% pass rate after deployment"
        ]
    )

    # SECURITY ISSUES
    rr.roast(
        RoastCategory.SECURITY,
        "API Key Management",
        "ElevenLabs MCP configuration updated to use secure wrapper but needs verification",
        severity="high",
        evidence=[
            "No API keys in clear text (good)",
            "Keys retrieved from Azure Key Vault at runtime",
            "Need to verify secure wrapper functionality"
        ]
    )

    # DOCUMENTATION ISSUES
    rr.roast(
        RoastCategory.DOCUMENTATION,
        "Project Status",
        "Multiple status files but may have inconsistencies or outdated information",
        severity="low",
        evidence=[
            "37/46 tasks completed (80% complete)",
            "Multiple status files: COMPLETE_SYSTEM_STATUS.md, FINAL_STATUS.md, AUTOMATION_STATUS.md",
            "Need to ensure all status information is current and consistent"
        ]
    )

    # PERFORMANCE ISSUES
    rr.roast(
        RoastCategory.PERFORMANCE,
        "Log Processing",
        "Log compression system may impact performance during high-volume operations",
        severity="low",
        evidence=[
            "LOG_COMPRESSION_SYSTEM_SUMMARY.md exists",
            "May need performance monitoring during peak usage"
        ]
    )

    # INTEGRATION ISSUES
    rr.roast(
        RoastCategory.INTEGRATION,
        "Container Services",
        "NAS container manager integration needs deployment verification",
        severity="medium",
        evidence=[
            "Container configuration ready but not yet deployed",
            "Need to verify MCP connections work properly"
        ]
    )


def main():
    """Execute comprehensive project RR analysis"""
    rr = ProjectRoastAndRepair()

    # REST: Observe current state
    session = rr.rest("Comprehensive analysis of entire Lumina project for systematic improvement")

    # ROAST: Identify issues across the entire project
    analyze_project_issues(rr)

    # REPAIR: Fix issues systematically
    logger.info("")
    logger.info("🔧 STARTING SYSTEMATIC REPAIRS")
    logger.info("=" * 80)

    # Fix the RR script syntax errors first
    rr.repair(
        repair_action="Fixed try/except blocks, added missing time import, corrected logger references"
    )

    # Save session
    rr.save_session()

    # Get comprehensive summary
    summary = rr.get_summary()
    logger.info("")
    logger.info("📊 PROJECT RR SESSION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"   Session ID: {summary['session_id']}")
    logger.info(f"   Total Issues Identified: {summary['total_issues']}")
    logger.info(f"   Issues Repaired: {summary['repaired_issues']}")
    logger.info(f"   Remaining Issues: {summary['remaining_issues']}")
    logger.info("")
    logger.info("📈 BY CATEGORY:")
    for cat, count in summary['by_category'].items():
        logger.info(f"   {cat.upper()}: {count} issues")
    logger.info("")
    logger.info("🏗️ BY COMPONENT:")
    for comp, count in summary['by_component'].items():
        logger.info(f"   {comp}: {count} issues")
    logger.info("")
    logger.info("🚨 BY SEVERITY:")
    for sev, count in summary['by_severity'].items():
        severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(sev, "⚪")
        logger.info(f"   {severity_emoji} {sev.upper()}: {count} issues")


if __name__ == "__main__":

    main()