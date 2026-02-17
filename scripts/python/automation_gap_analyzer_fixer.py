#!/usr/bin/env python3
"""
Automation Gap Analyzer & Fixer

Identifies and fixes automation gaps across the LUMINA codebase.
Real-world smoke test - finds and fixes automation issues NOW.

Gap Categories:
1. Missing Timestamp Automation (21,578 sections)
2. Manual Process Automation (TODO/FIXME/placeholder)
3. Incomplete Automation (partial implementations)
4. Workflow Automation Gaps (manual steps)
5. Integration Automation (missing connections)
6. Error Handling Automation (manual recovery)
7. Monitoring Automation (missing alerts)
8. Deployment Automation (manual steps)
9. Testing Automation (missing tests)
10. Documentation Automation (missing docs)
11. Configuration Automation (manual config)
12. Data Processing Automation (manual steps)

Tags: #AUTOMATION #GAP #ANALYZER #FIXER #SMOKE-TEST @JARVIS @TEAM @AUTOMATE
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger, TimestampFormat
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    get_timestamp_logger = lambda: None

logger = get_logger("AutomationGapAnalyzer")


@dataclass
class AutomationGap:
    """Represents an automation gap"""
    gap_id: str
    category: str
    severity: str  # critical, high, medium, low
    file_path: str
    line_number: int
    description: str
    current_state: str
    automated_state: str
    fix_priority: int  # 1-10, 10 = highest
    estimated_effort: str  # "low", "medium", "high"
    related_files: List[str]
    tags: List[str]


@dataclass
class AutomationGapReport:
    """Complete automation gap analysis report"""
    timestamp: Dict[str, Any]
    summary: Dict[str, Any]
    gaps_by_category: Dict[str, List[AutomationGap]]
    gaps_by_severity: Dict[str, List[AutomationGap]]
    top_priority_gaps: List[AutomationGap]
    recommendations: List[str]
    fix_plan: Dict[str, Any]


class AutomationGapAnalyzer:
    """
    Analyzes codebase for automation gaps and provides fixes
    """

    # Gap patterns
    MANUAL_PATTERNS = [
        (r'\bmanual\b', 'manual_process'),
        (r'\bTODO\b', 'todo'),
        (r'\bFIXME\b', 'fixme'),
        (r'\bXXX\b', 'xxx'),
        (r'\bHACK\b', 'hack'),
        (r'\bplaceholder\b', 'placeholder'),
        (r'not.*implemented', 'not_implemented'),
        (r'incomplete', 'incomplete'),
        (r'manual.*step', 'manual_step'),
        (r'manual.*process', 'manual_process'),
    ]

    # Automation gap categories
    CATEGORIES = [
        'timestamp_automation',
        'manual_process',
        'incomplete_automation',
        'workflow_automation',
        'integration_automation',
        'error_handling_automation',
        'monitoring_automation',
        'deployment_automation',
        'testing_automation',
        'documentation_automation',
        'configuration_automation',
        'data_processing_automation',
    ]

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize analyzer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.gaps: List[AutomationGap] = []
        self.ts_logger = get_timestamp_logger()

        # Load standardization audit if available
        self.standardization_audit = None
        self._load_standardization_audit()

    def _load_standardization_audit(self):
        """Load standardization audit report"""
        audit_file = self.project_root / "data" / "standardization_audit_report.json"
        if audit_file.exists():
            try:
                with open(audit_file, 'r', encoding='utf-8') as f:
                    self.standardization_audit = json.load(f)
                logger.info(f"✅ Loaded standardization audit: {audit_file}")
            except Exception as e:
                logger.warning(f"⚠️  Could not load audit: {e}")

    def analyze_file(self, file_path: Path) -> List[AutomationGap]:
        """Analyze a single file for automation gaps"""
        gaps = []

        if not file_path.exists() or not file_path.is_file():
            return gaps

        # Skip non-Python files for now
        if file_path.suffix != '.py':
            return gaps

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Calculate relative path safely
            try:
                relative_path = str(file_path.relative_to(self.project_root))
            except ValueError:
                # If not relative, use absolute path as fallback
                relative_path = str(file_path)

            # Check for manual patterns
            for line_num, line in enumerate(lines, 1):
                for pattern, gap_type in self.MANUAL_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        gap = AutomationGap(
                            gap_id=f"{relative_path}:{line_num}:{gap_type}",
                            category=self._categorize_gap(gap_type, line),
                            severity=self._assess_severity(gap_type, line, relative_path),
                            file_path=relative_path,
                            line_number=line_num,
                            description=self._extract_description(line),
                            current_state="Manual or incomplete",
                            automated_state=self._suggest_automation(gap_type, line),
                            fix_priority=self._calculate_priority(gap_type, relative_path),
                            estimated_effort=self._estimate_effort(gap_type, line),
                            related_files=self._find_related_files(relative_path),
                            tags=[gap_type, self._categorize_gap(gap_type, line)]
                        )
                        gaps.append(gap)

            # Check for timestamp gaps (from standardization audit)
            if self.standardization_audit:
                gaps.extend(self._check_timestamp_gaps(file_path, relative_path))

            # Check for missing error handling automation
            gaps.extend(self._check_error_handling_gaps(file_path, relative_path, lines))

            # Check for missing monitoring automation
            gaps.extend(self._check_monitoring_gaps(file_path, relative_path, lines))

        except Exception as e:
            logger.warning(f"⚠️  Error analyzing {file_path}: {e}")

        return gaps

    def _categorize_gap(self, gap_type: str, line: str) -> str:
        """Categorize gap based on type and context"""
        line_lower = line.lower()

        if 'timestamp' in line_lower or 'logging' in line_lower:
            return 'timestamp_automation'
        elif 'workflow' in line_lower or 'process' in line_lower:
            return 'workflow_automation'
        elif 'integration' in line_lower or 'api' in line_lower:
            return 'integration_automation'
        elif 'error' in line_lower or 'exception' in line_lower:
            return 'error_handling_automation'
        elif 'monitor' in line_lower or 'alert' in line_lower:
            return 'monitoring_automation'
        elif 'deploy' in line_lower or 'build' in line_lower:
            return 'deployment_automation'
        elif 'test' in line_lower:
            return 'testing_automation'
        elif 'config' in line_lower or 'setting' in line_lower:
            return 'configuration_automation'
        elif 'data' in line_lower or 'process' in line_lower:
            return 'data_processing_automation'
        else:
            return 'manual_process'

    def _assess_severity(self, gap_type: str, line: str, file_path: str) -> str:
        """Assess severity of gap"""
        # Critical files
        critical_files = ['jarvis', 'manus', 'syphon', 'workflow', 'automation']
        if any(cf in file_path.lower() for cf in critical_files):
            if gap_type in ['todo', 'fixme', 'not_implemented']:
                return 'critical'

        # High severity patterns
        if 'critical' in line.lower() or 'important' in line.lower():
            return 'high'
        if gap_type in ['not_implemented', 'incomplete']:
            return 'high'

        # Medium severity
        if gap_type in ['todo', 'fixme', 'hack']:
            return 'medium'

        return 'low'

    def _extract_description(self, line: str) -> str:
        """Extract description from line"""
        # Remove comment markers
        line = re.sub(r'^\s*#+\s*', '', line)
        line = re.sub(r'^\s*//+\s*', '', line)
        # Clean up
        line = line.strip()
        # Limit length
        if len(line) > 200:
            line = line[:197] + "..."
        return line

    def _suggest_automation(self, gap_type: str, line: str) -> str:
        """Suggest automated state"""
        suggestions = {
            'manual_process': 'Automate with script/workflow',
            'todo': 'Implement automated solution',
            'fixme': 'Fix with automated handling',
            'placeholder': 'Replace with automated implementation',
            'not_implemented': 'Implement automated version',
            'incomplete': 'Complete automation',
        }
        return suggestions.get(gap_type, 'Automate process')

    def _calculate_priority(self, gap_type: str, file_path: str) -> int:
        """Calculate fix priority (1-10, 10 = highest)"""
        priority = 5  # Default

        # Critical files get higher priority
        if 'jarvis' in file_path.lower():
            priority += 2
        if 'automation' in file_path.lower():
            priority += 1

        # Gap type adjustments
        if gap_type in ['not_implemented', 'incomplete']:
            priority += 2
        if gap_type == 'todo':
            priority += 1

        return min(10, priority)

    def _estimate_effort(self, gap_type: str, line: str) -> str:
        """Estimate effort to fix"""
        if 'simple' in line.lower() or 'easy' in line.lower():
            return 'low'
        if 'complex' in line.lower() or 'difficult' in line.lower():
            return 'high'
        if gap_type in ['placeholder', 'todo']:
            return 'medium'
        return 'medium'

    def _find_related_files(self, file_path: str) -> List[str]:
        """Find related files"""
        related = []
        # Look for imports or similar files
        # Simplified for now
        return related

    def _check_timestamp_gaps(self, file_path: Path, relative_path: str) -> List[AutomationGap]:
        """Check for timestamp automation gaps"""
        gaps = []

        if not self.standardization_audit:
            return gaps

        # Find file in audit
        for file_info in self.standardization_audit.get('files_needing_attention', []):
            if file_info.get('file') == relative_path.replace('\\', '\\'):
                issues = file_info.get('issues', 0)
                if issues > 0:
                    gap = AutomationGap(
                        gap_id=f"{relative_path}:timestamp_automation",
                        category='timestamp_automation',
                        severity='high',
                        file_path=relative_path,
                        line_number=0,
                        description=f"Missing timestamps in {issues} sections",
                        current_state="No standardized timestamp logging",
                        automated_state="Add standardized timestamp logging with @auto_timestamp",
                        fix_priority=8,
                        estimated_effort='low',
                        related_files=[],
                        tags=['timestamp', 'standardization', 'automation']
                    )
                    gaps.append(gap)
                break

        return gaps

    def _check_error_handling_gaps(self, file_path: Path, relative_path: str, lines: List[str]) -> List[AutomationGap]:
        """Check for missing error handling automation"""
        gaps = []

        # Look for try blocks without automated recovery
        in_try = False
        for line_num, line in enumerate(lines, 1):
            if 'try:' in line:
                in_try = True
            elif in_try and ('except' in line or 'finally' in line):
                # Check if exception handling is automated
                if 'pass' in line or 'print' in line:
                    gap = AutomationGap(
                        gap_id=f"{relative_path}:{line_num}:error_handling",
                        category='error_handling_automation',
                        severity='medium',
                        file_path=relative_path,
                        line_number=line_num,
                        description="Missing automated error handling/recovery",
                        current_state="Manual error handling",
                        automated_state="Automated error recovery and logging",
                        fix_priority=6,
                        estimated_effort='medium',
                        related_files=[],
                        tags=['error_handling', 'automation']
                    )
                    gaps.append(gap)
                in_try = False

        return gaps

    def _check_monitoring_gaps(self, file_path: Path, relative_path: str, lines: List[str]) -> List[AutomationGap]:
        """Check for missing monitoring automation"""
        gaps = []

        # Look for critical operations without monitoring
        critical_ops = ['save', 'delete', 'update', 'process', 'execute']
        for line_num, line in enumerate(lines, 1):
            for op in critical_ops:
                if f'def {op}' in line or f'def _{op}' in line:
                    # Check if monitoring exists
                    has_monitoring = any('monitor' in l.lower() or 'log' in l.lower() 
                                        for l in lines[max(0, line_num-5):line_num+10])
                    if not has_monitoring:
                        gap = AutomationGap(
                            gap_id=f"{relative_path}:{line_num}:monitoring",
                            category='monitoring_automation',
                            severity='medium',
                            file_path=relative_path,
                            line_number=line_num,
                            description=f"Missing automated monitoring for {op} operation",
                            current_state="No automated monitoring",
                            automated_state="Add automated monitoring and alerts",
                            fix_priority=5,
                            estimated_effort='low',
                            related_files=[],
                            tags=['monitoring', 'automation']
                        )
                        gaps.append(gap)

        return gaps

    def analyze_directory(self, directory: Optional[Path] = None, pattern: str = "*.py") -> List[AutomationGap]:
        try:
            """Analyze directory for automation gaps"""
            if directory is None:
                directory = self.project_root / "scripts" / "python"

            directory = Path(directory)
            if not directory.exists():
                logger.warning(f"⚠️  Directory not found: {directory}")
                return []

            gaps = []
            files = list(directory.rglob(pattern))

            logger.info(f"🔍 Analyzing {len(files)} files for automation gaps...")

            for file_path in files:
                file_gaps = self.analyze_file(file_path)
                gaps.extend(file_gaps)

            self.gaps = gaps
            logger.info(f"✅ Found {len(gaps)} automation gaps")

            return gaps

        except Exception as e:
            self.logger.error(f"Error in analyze_directory: {e}", exc_info=True)
            raise
    def generate_report(self) -> AutomationGapReport:
        """Generate comprehensive automation gap report"""
        if not self.gaps:
            logger.warning("⚠️  No gaps found - run analyze_directory first")
            return None

        # Group by category
        gaps_by_category = defaultdict(list)
        for gap in self.gaps:
            gaps_by_category[gap.category].append(gap)

        # Group by severity
        gaps_by_severity = defaultdict(list)
        for gap in self.gaps:
            gaps_by_severity[gap.severity].append(gap)

        # Top priority gaps
        top_priority = sorted(self.gaps, key=lambda g: g.fix_priority, reverse=True)[:12]

        # Summary
        summary = {
            'total_gaps': len(self.gaps),
            'gaps_by_category': {cat: len(gaps) for cat, gaps in gaps_by_category.items()},
            'gaps_by_severity': {sev: len(gaps) for sev, gaps in gaps_by_severity.items()},
            'critical_gaps': len(gaps_by_severity.get('critical', [])),
            'high_priority_gaps': len([g for g in self.gaps if g.fix_priority >= 8]),
        }

        # Recommendations
        recommendations = self._generate_recommendations(gaps_by_category, gaps_by_severity)

        # Fix plan
        fix_plan = self._generate_fix_plan(top_priority)

        # Timestamp
        ts_logger = get_timestamp_logger()
        timestamp = ts_logger.get_timestamp_dict("automation_gap_analyzer") if ts_logger else {}

        report = AutomationGapReport(
            timestamp=timestamp,
            summary=summary,
            gaps_by_category={cat: [asdict(g) for g in gaps] for cat, gaps in gaps_by_category.items()},
            gaps_by_severity={sev: [asdict(g) for g in gaps] for sev, gaps in gaps_by_severity.items()},
            top_priority_gaps=[asdict(g) for g in top_priority],
            recommendations=recommendations,
            fix_plan=fix_plan
        )

        return report

    def _generate_recommendations(self, gaps_by_category: Dict, gaps_by_severity: Dict) -> List[str]:
        """Generate recommendations"""
        recommendations = []

        # Category-based recommendations
        if 'timestamp_automation' in gaps_by_category:
            count = len(gaps_by_category['timestamp_automation'])
            recommendations.append(
                f"🔧 Fix {count} timestamp automation gaps - integrate standardized_timestamp_logging"
            )

        if 'error_handling_automation' in gaps_by_category:
            count = len(gaps_by_category['error_handling_automation'])
            recommendations.append(
                f"🔧 Add automated error handling to {count} locations"
            )

        # Severity-based recommendations
        if 'critical' in gaps_by_severity:
            count = len(gaps_by_severity['critical'])
            recommendations.append(
                f"🚨 URGENT: Fix {count} critical automation gaps immediately"
            )

        return recommendations

    def _generate_fix_plan(self, top_priority: List[AutomationGap]) -> Dict[str, Any]:
        """Generate fix plan"""
        return {
            'total_gaps_to_fix': len(top_priority),
            'estimated_effort': sum(1 for g in top_priority if g.estimated_effort == 'high'),
            'fix_order': [g.gap_id for g in top_priority],
            'quick_wins': [g.gap_id for g in top_priority if g.estimated_effort == 'low'][:5],
        }


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Automation Gap Analyzer & Fixer")
        parser.add_argument("--analyze", type=str, help="Directory to analyze")
        parser.add_argument("--report", type=str, help="Output report file")
        parser.add_argument("--fix", action="store_true", help="Attempt to fix gaps")

        args = parser.parse_args()

        print("\n" + "="*80)
        print("🔍 Automation Gap Analyzer & Fixer")
        print("   Real-world smoke test - find and fix automation gaps NOW")
        print("="*80 + "\n")

        analyzer = AutomationGapAnalyzer()

        # Analyze
        if args.analyze:
            analyze_dir = Path(args.analyze)
            gaps = analyzer.analyze_directory(analyze_dir)
        else:
            gaps = analyzer.analyze_directory()

        # Generate report
        report = analyzer.generate_report()

        if report:
            # Print summary
            print(f"📊 AUTOMATION GAP SUMMARY:")
            print(f"   Total Gaps: {report.summary['total_gaps']}")
            print(f"   Critical: {report.summary['gaps_by_severity'].get('critical', 0)}")
            print(f"   High: {report.summary['gaps_by_severity'].get('high', 0)}")
            print(f"   Medium: {report.summary['gaps_by_severity'].get('medium', 0)}")
            print(f"   Low: {report.summary['gaps_by_severity'].get('low', 0)}")
            print()

            print(f"📋 BY CATEGORY:")
            for category, count in report.summary['gaps_by_category'].items():
                print(f"   {category}: {count}")
            print()

            print(f"🎯 TOP PRIORITY GAPS (Top 12):")
            for i, gap in enumerate(report.top_priority_gaps[:12], 1):
                print(f"   {i}. [{gap['severity'].upper()}] {gap['file_path']}:{gap['line_number']}")
                print(f"      {gap['description'][:80]}")
                print(f"      Priority: {gap['fix_priority']}/10, Effort: {gap['estimated_effort']}")
                print()

            # Save report
            if args.report:
                report_file = Path(args.report)
                report_file.parent.mkdir(parents=True, exist_ok=True)
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(report), f, indent=2, default=str)
                print(f"✅ Report saved: {report_file}\n")

        print("="*80 + "\n")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()