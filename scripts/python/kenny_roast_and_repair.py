#!/usr/bin/env python3
"""
Kenny Roast and Repair (RR) System
Rest, Roast, and Repair - Granular Focus for Kenny Development

Technique for developing Kenny into the JARVIS we want:
1. REST: Pause, observe, analyze current state
2. ROAST: Critically identify issues, problems, gaps
3. REPAIR: Fix issues systematically, one at a time

Tags: #RR #ROAST_AND_REPAIR #KENNY #JARVIS #DEVELOPMENT #GRANULAR_FOCUS
@JARVIS @LUMINA @KENNY
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

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None

logger = get_logger("KennyRoastAndRepair")


class RoastCategory(Enum):
    """Categories for roasting Kenny"""
    VISUAL = "visual"  # Appearance, sprite, rendering
    BEHAVIORAL = "behavioral"  # Movement, actions, state
    FUNCTIONAL = "functional"  # Features, capabilities
    INTEGRATION = "integration"  # Collaboration, ecosystem
    PERFORMANCE = "performance"  # Speed, responsiveness
    QUALITY = "quality"  # Bugs, errors, edge cases


@dataclass
class RoastIssue:
    """A specific issue identified during roasting"""
    category: RoastCategory
    description: str
    severity: str  # "critical", "high", "medium", "low"
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    repaired: bool = False
    repair_notes: str = ""


@dataclass
class RoastSession:
    """A complete roast and repair session"""
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[RoastIssue] = field(default_factory=list)
    repairs_applied: List[str] = field(default_factory=list)
    status: str = "rest"  # "rest", "roast", "repair", "complete"


class KennyRoastAndRepair:
    """
    RR System: Rest, Roast, and Repair

    A granular focus technique for developing Kenny into JARVIS:
    1. REST: Pause, observe, analyze current state
    2. ROAST: Critically identify issues, problems, gaps
    3. REPAIR: Fix issues systematically, one at a time
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize RR System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "kenny_rr_sessions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.current_session: Optional[RoastSession] = None

        logger.info("=" * 80)
        logger.info("🔥 KENNY ROAST AND REPAIR (RR) SYSTEM")
        logger.info("   Rest, Roast, and Repair - Granular Focus for Development")
        logger.info("=" * 80)

        # SYPHON integration - Intelligence extraction for VA enhancement
        self.syphon = None
        self.syphon_enhancement_interval = 60.0  # Extract intelligence every 60 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_enhanced_knowledge = []
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                logger.info("✅ SYPHON intelligence extraction integrated for VA enhancement")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON integration failed: {e}")

        # R5 Living Context Matrix - Context aggregation
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                logger.info("✅ R5 context aggregation integrated")
            except Exception as e:
                logger.warning(f"⚠️  R5 integration failed: {e}")

    def rest(self, description: str = "Observing Kenny's current state") -> RoastSession:
        """
        REST: Pause, observe, analyze current state

        Args:
            description: What we're observing

        Returns:
            RoastSession ready for roasting
        """
        session_id = f"rr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_session = RoastSession(
            session_id=session_id,
            status="rest"
        )

        logger.info("")
        logger.info("=" * 80)
        logger.info("😴 REST: Observing Kenny's Current State")
        logger.info("=" * 80)
        logger.info(f"   Session: {session_id}")
        logger.info(f"   Focus: {description}")
        logger.info("")
        logger.info("📊 Analyzing:")
        logger.info("   - Visual state (sprite, rendering, appearance)")
        logger.info("   - Behavioral state (movement, actions, state machine)")
        logger.info("   - Functional state (features, capabilities)")
        logger.info("   - Integration state (collaboration, ecosystem)")
        logger.info("   - Performance state (speed, responsiveness)")
        logger.info("   - Quality state (bugs, errors, edge cases)")
        logger.info("")

        return self.current_session

    def roast(self, category: RoastCategory, description: str,
              severity: str = "medium", evidence: Optional[List[str]] = None) -> RoastIssue:
        """
        ROAST: Critically identify issues, problems, gaps

        Args:
            category: Category of issue
            description: What's wrong
            severity: How bad is it
            evidence: Supporting evidence

        Returns:
            RoastIssue
        """
        if not self.current_session:
            self.rest("Starting roast session")

        if self.current_session.status == "rest":
            self.current_session.status = "roast"
            logger.info("")
            logger.info("=" * 80)
            logger.info("🔥 ROAST: Critically Identifying Issues")
            logger.info("=" * 80)
            logger.info("")

        issue = RoastIssue(
            category=category,
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

        logger.info(f"{severity_emoji} [{category.value.upper()}] {description}")
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
            logger.info("🔧 REPAIR: Fixing Issues Systematically")
            logger.info("=" * 80)
            logger.info("")

        # If no issue specified, get next unrepaired issue
        if issue is None:
            unrepaired = [i for i in self.current_session.issues if not i.repaired]
            if not unrepaired:
                logger.info("✅ All issues repaired!")
                self.current_session.status = "complete"
                return True
            issue = unrepaired[0]  # Start with first unrepaired

        # Mark as repaired
        issue.repaired = True
        issue.repair_notes = repair_action or "Repaired"

        self.current_session.repairs_applied.append(
            f"[{issue.category.value}] {issue.description}: {repair_action or 'Fixed'}"
        )

        logger.info(f"✅ REPAIRED: [{issue.category.value.upper()}] {issue.description}")
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

            logger.info(f"💾 Session saved: {session_file}")
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
        by_severity = {}

        for issue in self.current_session.issues:
            cat = issue.category.value
            sev = issue.severity

            by_category[cat] = by_category.get(cat, 0) + 1
            by_severity[sev] = by_severity.get(sev, 0) + 1

        return {
            "session_id": self.current_session.session_id,
            "status": self.current_session.status,
            "total_issues": total_issues,
            "repaired_issues": repaired_issues,
            "remaining_issues": total_issues - repaired_issues,
            "by_category": by_category,
            "by_severity": by_severity,
            "repairs_applied": len(self.current_session.repairs_applied)
        }


def main():
    """Example usage of RR System"""
    rr = KennyRoastAndRepair()

    # REST: Observe current state
    session = rr.rest("Analyzing Kenny's current state for development")

    # ROAST: Identify issues
    rr.roast(
        RoastCategory.VISUAL,
        "Kenny appears as orange Froot Loop instead of solid circle",
        severity="high",
        evidence=["Programmatic analysis shows 96.8% ring ratio", "User reports 'orange Froot Loop'"]
    )

    rr.roast(
        RoastCategory.BEHAVIORAL,
        "Kenny stops moving after initial movement",
        severity="medium",
        evidence=["User reports Kenny 'came to rest in bottom right corner'"]
    )

    # REPAIR: Fix issues
    rr.repair(
        repair_action="Implemented component-based design system with dynamic scaling"
    )

    # Save session
    rr.save_session()

    # Get summary
    summary = rr.get_summary()
    logger.info("")
    logger.info("📊 Session Summary:")
    logger.info(f"   Total Issues: {summary['total_issues']}")
    logger.info(f"   Repaired: {summary['repaired_issues']}")
    logger.info(f"   Remaining: {summary['remaining_issues']}")


if __name__ == "__main__":


    main()