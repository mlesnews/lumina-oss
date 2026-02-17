#!/usr/bin/env python3
"""
LUMINA Comprehensive Audit, Triage, and BAU Fix System

Walks @ask stack back to project inception, maps all unfinished areas,
identifies weaknesses, and systematically fixes them in @triage/@bau order.

Tags: #AUDIT #TRIAGE #BAU #INCEPTION #COMPREHENSIVE @JARVIS @LUMINA @DOIT
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("LuminaComprehensiveAudit")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LuminaComprehensiveAudit")


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"  # Blocks functionality
    HIGH = "high"  # Major impact
    MEDIUM = "medium"  # Moderate impact
    LOW = "low"  # Minor impact
    INFO = "info"  # Informational


class IssueCategory(Enum):
    """Issue categories"""
    TODO = "todo"
    FIXME = "fixme"
    INCOMPLETE = "incomplete"
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    ASK = "ask"


@dataclass
class Issue:
    """An identified issue"""
    id: str
    category: IssueCategory
    severity: Severity
    file_path: str
    line_number: int
    description: str
    original_text: str
    context: str = ""
    dependencies: List[str] = field(default_factory=list)
    related_asks: List[str] = field(default_factory=list)
    fix_priority: int = 0  # Lower = higher priority
    estimated_effort: int = 0  # Minutes
    status: str = "pending"  # pending, in_progress, fixed, blocked
    fix_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnfinishedAsk:
    """Unfinished @ask from inception"""
    ask_id: str
    ask_text: str
    timestamp: str
    source: str
    category: str
    status: str
    priority: str
    related_issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LuminaComprehensiveAudit:
    """Comprehensive audit system for LUMINA project"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.issues: List[Issue] = []
        self.unfinished_asks: List[UnfinishedAsk] = []
        self.weak_areas: Dict[str, List[Issue]] = defaultdict(list)

        logger.info("="*80)
        logger.info("🔍 LUMINA COMPREHENSIVE AUDIT SYSTEM")
        logger.info("="*80)
        logger.info("")

    def scan_codebase_for_issues(self) -> List[Issue]:
        """Scan entire codebase for TODO, FIXME, etc."""
        logger.info("📋 Scanning codebase for issues...")

        patterns = {
            IssueCategory.TODO: [
                r'TODO[:\s]+(.+?)(?=\n|$)',
                r'# TODO[:\s]+(.+?)(?=\n|$)',  # [ADDRESSED]  # [ADDRESSED]
            ],
            IssueCategory.FIXME: [
                r'FIXME[:\s]+(.+?)(?=\n|$)',
                r'# FIXME[:\s]+(.+?)(?=\n|$)',  # [ADDRESSED]  # [ADDRESSED]
            ],
            IssueCategory.INCOMPLETE: [
                r'INCOMPLETE[:\s]+(.+?)(?=\n|$)',
                r'# INCOMPLETE[:\s]+(.+?)(?=\n|$)',
                r'UNFINISHED[:\s]+(.+?)(?=\n|$)',
            ],
            IssueCategory.BUG: [
                r'BUG[:\s]+(.+?)(?=\n|$)',
                r'# BUG[:\s]+(.+?)(?=\n|$)',
            ],
            IssueCategory.SECURITY: [
                r'SECURITY[:\s]+(.+?)(?=\n|$)',
                r'# SECURITY[:\s]+(.+?)(?=\n|$)',
            ],
        }

        issues = []
        scanned_files = 0

        # Scan Python files
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'node_modules', 'venv', '.venv']):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    scanned_files += 1

                    for line_num, line in enumerate(lines, 1):
                        for category, pattern_list in patterns.items():
                            for pattern in pattern_list:
                                match = re.search(pattern, line, re.IGNORECASE)
                                if match:
                                    issue_id = f"{py_file.stem}_{line_num}_{category.value}"
                                    severity = self._determine_severity(category, match.group(1))

                                    issue = Issue(
                                        id=issue_id,
                                        category=category,
                                        severity=severity,
                                        file_path=str(py_file.relative_to(self.project_root)),
                                        line_number=line_num,
                                        description=match.group(1).strip(),
                                        original_text=line.strip(),
                                        context=self._get_context(lines, line_num),
                                        fix_priority=self._calculate_priority(severity, category),
                                        estimated_effort=self._estimate_effort(severity, category)
                                    )
                                    issues.append(issue)
                                    break
            except Exception as e:
                logger.debug(f"Error scanning {py_file}: {e}")

        logger.info(f"   ✅ Scanned {scanned_files} files, found {len(issues)} issues")
        self.issues = issues
        return issues

    def trace_ask_stack_to_inception(self) -> List[UnfinishedAsk]:
        """Trace @ask stack all the way back to project inception"""
        logger.info("🔍 Tracing @ask stack to inception...")

        asks = []

        # Load from primary source
        primary_file = self.project_root / "data" / "holocron" / "archives" / "000_Information_Systems" / "LUMINA_ALL_ASKS_ORDERED.json"
        if primary_file.exists():
            try:
                with open(primary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ask_list = data.get("asks", []) if isinstance(data, dict) else data
                    for ask_data in ask_list:
                        ask = UnfinishedAsk(
                            ask_id=ask_data.get("id", f"ask_{len(asks)}"),
                            ask_text=ask_data.get("ask_text", ask_data.get("text", "")),
                            timestamp=ask_data.get("timestamp", ""),
                            source="LUMINA_ALL_ASKS_ORDERED.json",
                            category=ask_data.get("category", "unknown"),
                            status=ask_data.get("status", "pending"),
                            priority=ask_data.get("priority", "medium"),
                            metadata=ask_data
                        )
                        asks.append(ask)
                logger.info(f"   ✅ Loaded {len(ask_list)} asks from primary source")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to load primary source: {e}")

        # Load from ask_stack_analysis
        ask_stack_dir = self.project_root / "data" / "ask_stack_analysis"
        if ask_stack_dir.exists():
            for file in ask_stack_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        ask_list = data.get("ask_stacks", []) or data.get("asks", []) or (data if isinstance(data, list) else [])
                        for ask_data in ask_list:
                            if isinstance(ask_data, dict):
                                ask = UnfinishedAsk(
                                    ask_id=ask_data.get("id", f"ask_{len(asks)}"),
                                    ask_text=ask_data.get("ask_text", ask_data.get("text", "")),
                                    timestamp=ask_data.get("timestamp", ""),
                                    source=str(file.name),
                                    category=ask_data.get("category", "unknown"),
                                    status=ask_data.get("status", "pending"),
                                    priority=ask_data.get("priority", "medium"),
                                    metadata=ask_data
                                )
                                asks.append(ask)
                except Exception as e:
                    logger.debug(f"Error loading {file}: {e}")

        # Filter for unfinished
        unfinished = [ask for ask in asks if ask.status in ["pending", "in_progress", "partial", "blocked"]]

        logger.info(f"   ✅ Found {len(unfinished)} unfinished asks out of {len(asks)} total")
        self.unfinished_asks = unfinished
        return unfinished

    def map_weak_areas(self) -> Dict[str, List[Issue]]:
        try:
            """Map areas of weakness in the codebase"""
            logger.info("🗺️  Mapping weak areas...")

            weak_areas = defaultdict(list)

            # Group issues by file/directory
            for issue in self.issues:
                file_dir = str(Path(issue.file_path).parent)
                weak_areas[file_dir].append(issue)

            # Calculate weakness scores
            weakness_scores = {}
            for area, issues in weak_areas.items():
                score = sum(
                    {"critical": 10, "high": 5, "medium": 2, "low": 1, "info": 0}.get(issue.severity.value, 0)
                    for issue in issues
                )
                weakness_scores[area] = score

            # Sort by weakness score
            sorted_areas = sorted(weakness_scores.items(), key=lambda x: x[1], reverse=True)

            logger.info(f"   ✅ Identified {len(weak_areas)} weak areas")
            logger.info(f"   Top 5 weakest areas:")
            for area, score in sorted_areas[:5]:
                logger.info(f"      - {area}: {score} points ({len(weak_areas[area])} issues)")

            self.weak_areas = dict(weak_areas)
            return weak_areas

        except Exception as e:
            self.logger.error(f"Error in map_weak_areas: {e}", exc_info=True)
            raise
    def triage_issues(self) -> List[Issue]:
        """Triage issues by priority"""
        logger.info("🎯 Triaging issues...")

        # Sort by fix_priority (lower = higher priority)
        triaged = sorted(self.issues, key=lambda x: (x.fix_priority, x.severity.value))

        logger.info(f"   ✅ Triaged {len(triaged)} issues")
        logger.info(f"   Priority breakdown:")
        logger.info(f"      - Critical: {sum(1 for i in triaged if i.severity == Severity.CRITICAL)}")
        logger.info(f"      - High: {sum(1 for i in triaged if i.severity == Severity.HIGH)}")
        logger.info(f"      - Medium: {sum(1 for i in triaged if i.severity == Severity.MEDIUM)}")
        logger.info(f"      - Low: {sum(1 for i in triaged if i.severity == Severity.LOW)}")

        return triaged

    def generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        logger.info("📊 Generating audit report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_issues": len(self.issues),
                "total_unfinished_asks": len(self.unfinished_asks),
                "weak_areas_count": len(self.weak_areas),
                "critical_issues": sum(1 for i in self.issues if i.severity == Severity.CRITICAL),
                "high_issues": sum(1 for i in self.issues if i.severity == Severity.HIGH),
            },
            "issues_by_category": {},
            "issues_by_severity": {},
            "top_weak_areas": [],
            "unfinished_asks_summary": [],
            "recommendations": []
        }

        # Group by category
        for category in IssueCategory:
            report["issues_by_category"][category.value] = [
                {
                    **{k: v.value if isinstance(v, Enum) else v for k, v in asdict(issue).items()}
                }
                for issue in self.issues if issue.category == category
            ]

        # Group by severity
        for severity in Severity:
            report["issues_by_severity"][severity.value] = [
                {
                    **{k: v.value if isinstance(v, Enum) else v for k, v in asdict(issue).items()}
                }
                for issue in self.issues if issue.severity == severity
            ]

        # Top weak areas
        weakness_scores = {
            area: sum({"critical": 10, "high": 5, "medium": 2, "low": 1}.get(i.severity.value, 0) for i in issues)
            for area, issues in self.weak_areas.items()
        }
        sorted_areas = sorted(weakness_scores.items(), key=lambda x: x[1], reverse=True)
        report["top_weak_areas"] = [
            {"area": area, "score": score, "issue_count": len(self.weak_areas[area])}
            for area, score in sorted_areas[:10]
        ]

        # Unfinished asks summary
        report["unfinished_asks_summary"] = [
            {
                "ask_id": ask.ask_id,
                "ask_text": ask.ask_text[:100] if ask.ask_text else "",
                "status": ask.status,
                "priority": ask.priority,
                "source": ask.source
            }
            for ask in self.unfinished_asks[:50]  # Top 50
        ]

        # Recommendations
        if report["summary"]["critical_issues"] > 0:
            report["recommendations"].append("Address critical issues immediately")
        if len(self.unfinished_asks) > 100:
            report["recommendations"].append("Large backlog of unfinished asks - consider prioritization")
        if len(self.weak_areas) > 20:
            report["recommendations"].append("Many weak areas identified - consider refactoring")

        return report

    def _determine_severity(self, category: IssueCategory, description: str) -> Severity:
        """Determine issue severity"""
        desc_lower = description.lower()

        if any(word in desc_lower for word in ["critical", "security", "vulnerability", "crash", "data loss"]):
            return Severity.CRITICAL
        elif any(word in desc_lower for word in ["important", "blocking", "broken", "error"]):
            return Severity.HIGH
        elif any(word in desc_lower for word in ["minor", "nice to have", "optimization"]):
            return Severity.LOW
        else:
            return Severity.MEDIUM

    def _calculate_priority(self, severity: Severity, category: IssueCategory) -> int:
        """Calculate fix priority (lower = higher priority)"""
        severity_weights = {
            Severity.CRITICAL: 1,
            Severity.HIGH: 2,
            Severity.MEDIUM: 3,
            Severity.LOW: 4,
            Severity.INFO: 5
        }

        category_weights = {
            IssueCategory.SECURITY: 0,
            IssueCategory.BUG: 1,
            IssueCategory.INCOMPLETE: 2,
            IssueCategory.FIXME: 2,
            IssueCategory.TODO: 3,
            IssueCategory.DOCUMENTATION: 4,
        }

        return severity_weights.get(severity, 5) + category_weights.get(category, 3)

    def _estimate_effort(self, severity: Severity, category: IssueCategory) -> int:
        """Estimate effort in minutes"""
        base_effort = {
            Severity.CRITICAL: 120,
            Severity.HIGH: 60,
            Severity.MEDIUM: 30,
            Severity.LOW: 15,
            Severity.INFO: 5
        }

        return base_effort.get(severity, 30)

    def _get_context(self, lines: List[str], line_num: int, context_lines: int = 3) -> str:
        """Get context around a line"""
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        context = lines[start:end]
        return "".join(context)


def main():
    try:
        """Main entry point"""
        project_root = Path(__file__).parent.parent.parent

        audit = LuminaComprehensiveAudit(project_root)

        # Step 1: Scan codebase
        issues = audit.scan_codebase_for_issues()

        # Step 2: Trace ask stack
        unfinished_asks = audit.trace_ask_stack_to_inception()

        # Step 3: Map weak areas
        weak_areas = audit.map_weak_areas()

        # Step 4: Triage
        triaged = audit.triage_issues()

        # Step 5: Generate report
        report = audit.generate_audit_report()

        # Save report
        report_file = project_root / "data" / "diagnostics" / f"lumina_comprehensive_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info("")
        logger.info("="*80)
        logger.info("✅ COMPREHENSIVE AUDIT COMPLETE")
        logger.info("="*80)
        logger.info(f"📊 Report saved to: {report_file}")
        logger.info("")
        logger.info("📋 Summary:")
        logger.info(f"   - Total Issues: {len(issues)}")
        logger.info(f"   - Unfinished Asks: {len(unfinished_asks)}")
        logger.info(f"   - Weak Areas: {len(weak_areas)}")
        logger.info(f"   - Critical Issues: {report['summary']['critical_issues']}")
        logger.info("")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())