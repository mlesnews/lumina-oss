#!/usr/bin/env python3
"""
Gap Analysis & Closure System
@PEAK Optimized | @MAX Gap Identification & Resolution

Systematically identifies and closes all gaps in the Lumina/JARVIS ecosystem.
Uses AI-powered analysis to find missing components, incomplete implementations,
and potential improvements.

Features:
- Comprehensive gap identification across all system components
- Priority-based gap resolution
- Automated gap closure suggestions
- Integration with existing systems (SYPHON, R5, JARVIS)
- Progress tracking and reporting
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
import re
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Try to import existing systems for gap analysis
try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False

try:
    from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False

@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class SystemGap:
    """Represents a gap in the system"""
    gap_id: str
    category: str
    title: str
    description: str
    severity: str  # critical, high, medium, low
    status: str  # identified, analyzing, implementing, resolved, closed
    priority: int  # 1=highest, 5=lowest
    location: str  # file path or component
    evidence: List[str] = field(default_factory=list)
    suggested_solution: str = ""
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: str = ""  # hours, days, weeks
    assigned_to: str = ""  # JARVIS component or human
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

@dataclass
class GapAnalysisReport:
    """Comprehensive gap analysis report"""
    total_gaps: int = 0
    critical_gaps: int = 0
    high_gaps: int = 0
    medium_gaps: int = 0
    low_gaps: int = 0
    resolved_gaps: int = 0
    gaps_by_category: Dict[str, int] = field(default_factory=dict)
    gaps_by_status: Dict[str, int] = field(default_factory=dict)
    top_priority_gaps: List[SystemGap] = field(default_factory=list)
    system_health_score: float = 0.0
    analysis_timestamp: datetime = field(default_factory=datetime.now)

class GapAnalysisSystem:
    """
    @PEAK Gap Analysis & Closure System

    Identifies, prioritizes, and resolves all gaps in the Lumina ecosystem.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.gaps: Dict[str, SystemGap] = {}
        self.gap_patterns = self._load_gap_patterns()

        # Load existing gaps from file if available
        self._load_existing_gaps()

        print("🎯 Gap Analysis System initialized")

    def _load_gap_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load patterns for identifying different types of gaps"""
        return {
            "missing_implementation": {
                "keywords": ["not implemented", "not yet implemented", "TODO", "FIXME", "XXX"],
                "category": "implementation",
                "severity": "high"
            },
            "broken_imports": {
                "keywords": ["ImportError", "ModuleNotFoundError", "cannot import"],
                "category": "dependencies",
                "severity": "critical"
            },
            "missing_files": {
                "keywords": ["file not found", "missing file", "does not exist"],
                "category": "infrastructure",
                "severity": "high"
            },
            "configuration_errors": {
                "keywords": ["configuration error", "config missing", "not configured"],
                "category": "configuration",
                "severity": "medium"
            },
            "api_failures": {
                "keywords": ["API error", "endpoint failure", "connection failed"],
                "category": "integration",
                "severity": "high"
            },
            "performance_issues": {
                "keywords": ["slow", "performance issue", "high CPU", "memory leak"],
                "category": "performance",
                "severity": "medium"
            },
            "security_vulnerabilities": {
                "keywords": ["security risk", "vulnerable", "exposed", "insecure"],
                "category": "security",
                "severity": "critical"
            }
        }

    def _load_existing_gaps(self) -> None:
        """Load previously identified gaps"""
        gaps_file = self.project_root / "data" / "gaps" / "system_gaps.json"
        if gaps_file.exists():
            try:
                with open(gaps_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for gap_data in data.get("gaps", []):
                        gap = SystemGap(**gap_data)
                        self.gaps[gap.gap_id] = gap
                print(f"📋 Loaded {len(self.gaps)} existing gaps")
            except Exception as e:
                print(f"❌ Error loading existing gaps: {e}")

    def _save_gaps(self) -> None:
        """Save current gaps to file"""
        gaps_file = self.project_root / "data" / "gaps" / "system_gaps.json"
        gaps_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "total_gaps": len(self.gaps),
                "gaps": [
                    {
                        "gap_id": g.gap_id,
                        "category": g.category,
                        "title": g.title,
                        "description": g.description,
                        "severity": g.severity,
                        "status": g.status,
                        "priority": g.priority,
                        "location": g.location,
                        "evidence": g.evidence,
                        "suggested_solution": g.suggested_solution,
                        "dependencies": g.dependencies,
                        "estimated_effort": g.estimated_effort,
                        "assigned_to": g.assigned_to,
                        "created_at": g.created_at.isoformat(),
                        "resolved_at": g.resolved_at.isoformat() if g.resolved_at else None
                    }
                    for g in self.gaps.values()
                ]
            }

            with open(gaps_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"💾 Saved {len(self.gaps)} gaps to {gaps_file}")
        except Exception as e:
            print(f"❌ Error saving gaps: {e}")

    def scan_for_gaps(self) -> Dict[str, List[SystemGap]]:
        """
        Comprehensive gap scanning across the entire system

        Returns categorized gaps found during scanning
        """
        print("🔍 Scanning for gaps across all system components...")

        gaps_found = {
            "code_gaps": self._scan_code_files(),
            "config_gaps": self._scan_config_files(),
            "documentation_gaps": self._scan_documentation(),
            "integration_gaps": self._scan_integrations(),
            "performance_gaps": self._scan_performance(),
            "security_gaps": self._scan_security()
        }

        # Add new gaps to the system
        for category, category_gaps in gaps_found.items():
            for gap in category_gaps:
                if gap.gap_id not in self.gaps:
                    self.gaps[gap.gap_id] = gap
                    print(f"🆕 New gap identified: {gap.gap_id} - {gap.title}")

        self._save_gaps()
        return gaps_found

    def _scan_code_files(self) -> List[SystemGap]:
        """Scan Python and other code files for gaps"""
        gaps = []
        code_extensions = ['.py', '.ps1', '.js', '.ts', '.md']

        for ext in code_extensions:
            for file_path in self.project_root.rglob(f"*{ext}"):
                if self._should_skip_file(file_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Check for TODO/FIXME comments
                    for line_num, line in enumerate(content.split('\n'), 1):
                        if any(keyword in line.upper() for keyword in ["TODO", "FIXME", "XXX", "HACK"]):
                            gap = SystemGap(
                                gap_id=f"code_todo_{hash(str(file_path) + str(line_num)) % 1000000:06d}",
                                category="code_quality",
                                title="TODO/FIXME Item Found",
                                description=f"Unresolved TODO/FIXME in {file_path.name}:{line_num}",
                                severity="low",
                                status="identified",
                                priority=4,
                                location=str(file_path),
                                evidence=[line.strip()],
                                suggested_solution="Review and resolve TODO item or convert to proper task"
                            )
                            gaps.append(gap)

                    # Check for incomplete implementations
                    if "not implemented" in content.lower() or "not yet implemented" in content.lower():
                        gap = SystemGap(
                            gap_id=f"code_missing_{hash(str(file_path)) % 1000000:06d}",
                            category="implementation",
                            title="Missing Implementation",
                            description=f"Incomplete implementation in {file_path.name}",
                            severity="medium",
                            status="identified",
                            priority=3,
                            location=str(file_path),
                            evidence=["Contains 'not implemented' text"],
                            suggested_solution="Complete the implementation or remove placeholder"
                        )
                        gaps.append(gap)

                except Exception as e:
                    gap = SystemGap(
                        gap_id=f"file_error_{hash(str(file_path)) % 1000000:06d}",
                        category="infrastructure",
                        title="File Reading Error",
                        description=f"Cannot read file: {file_path.name}",
                        severity="low",
                        status="identified",
                        priority=5,
                        location=str(file_path),
                        evidence=[str(e)],
                        suggested_solution="Check file permissions or encoding"
                    )
                    gaps.append(gap)

        return gaps

    def _scan_config_files(self) -> List[SystemGap]:
        """Scan configuration files for gaps"""
        gaps = []
        config_files = [
            "config/**/*.json",
            "config/**/*.yaml",
            "config/**/*.yml",
            ".vscode/*.json",
            "**/requirements.txt",
            "**/package.json"
        ]

        for pattern in config_files:
            for config_path in self.project_root.glob(pattern):
                if not config_path.exists():
                    continue

                try:
                    # Check if config references missing files
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Look for file references that might not exist
                    import re
                    file_refs = re.findall(r'["\']([^"\']*\.(?:py|json|yaml|yml|txt|md))["\']', content)

                    for ref in file_refs:
                        ref_path = self.project_root / ref
                        if not ref_path.exists() and not ref.startswith(('http', '/')):
                            gap = SystemGap(
                                gap_id=f"config_missing_{hash(str(config_path) + ref) % 1000000:06d}",
                                category="configuration",
                                title="Missing Referenced File",
                                description=f"Config references non-existent file: {ref}",
                                severity="medium",
                                status="identified",
                                priority=3,
                                location=str(config_path),
                                evidence=[f"References: {ref}"],
                                suggested_solution=f"Create missing file {ref} or fix reference"
                            )
                            gaps.append(gap)

                except Exception as e:
                    gap = SystemGap(
                        gap_id=f"config_error_{hash(str(config_path)) % 1000000:06d}",
                        category="configuration",
                        title="Config File Error",
                        description=f"Cannot read config file: {config_path.name}",
                        severity="low",
                        status="identified",
                        priority=4,
                        location=str(config_path),
                        evidence=[str(e)],
                        suggested_solution="Check file format and syntax"
                    )
                    gaps.append(gap)

        return gaps

    def _scan_documentation(self) -> List[SystemGap]:
        try:
            """Scan documentation for gaps"""
            gaps = []

            # Check for missing README files
            important_dirs = [
                self.project_root,
                self.project_root / "scripts",
                self.project_root / "config",
                self.project_root / "containerization"
            ]

            for dir_path in important_dirs:
                if dir_path.exists():
                    readme_files = list(dir_path.glob("README*")) + list(dir_path.glob("readme*"))
                    if not readme_files:
                        gap = SystemGap(
                            gap_id=f"docs_missing_{hash(str(dir_path)) % 1000000:06d}",
                            category="documentation",
                            title="Missing Documentation",
                            description=f"No README found in {dir_path.name}/",
                            severity="low",
                            status="identified",
                            priority=4,
                            location=str(dir_path),
                            suggested_solution="Create README.md with usage instructions"
                        )
                        gaps.append(gap)

            return gaps

        except Exception as e:
            self.logger.error(f"Error in _scan_documentation: {e}", exc_info=True)
            raise
    def _scan_integrations(self) -> List[SystemGap]:
        """Scan for integration gaps"""
        gaps = []

        # Check SYPHON integration
        if SYPHON_AVAILABLE:
            try:
                syphon = SYPHONSystem(SYPHONConfig(project_root=self.project_root, subscription_tier=SubscriptionTier.ENTERPRISE))
                # Test basic SYPHON functionality
            except Exception as e:
                gap = SystemGap(
                    gap_id="syphon_integration_error",
                    category="integration",
                    title="SYPHON Integration Error",
                    description=f"SYPHON system has integration issues: {str(e)}",
                    severity="high",
                    status="identified",
                    priority=2,
                    location="scripts/python/syphon/",
                    evidence=[str(e)],
                    suggested_solution="Fix SYPHON configuration and dependencies"
                )
                gaps.append(gap)

        # Check R5 integration
        if R5_AVAILABLE:
            try:
                r5 = R5LivingContextMatrix(self.project_root)
                # Test basic R5 functionality
            except Exception as e:
                gap = SystemGap(
                    gap_id="r5_integration_error",
                    category="integration",
                    title="R5 Integration Error",
                    description=f"R5 Living Context Matrix has integration issues: {str(e)}",
                    severity="high",
                    status="identified",
                    priority=2,
                    location="scripts/python/r5_living_context_matrix.py",
                    evidence=[str(e)],
                    suggested_solution="Fix R5 configuration and dependencies"
                )
                gaps.append(gap)

        return gaps

    def _scan_performance(self) -> List[SystemGap]:
        """Scan for performance gaps"""
        gaps = []

        # Check for resource-intensive operations
        performance_files = [
            "scripts/**/*.py",
            "scripts/**/*.ps1"
        ]

        for pattern in performance_files:
            for file_path in self.project_root.glob(pattern):
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Check for potentially inefficient operations
                        if "sleep(" in content and "time.sleep" in content:
                            if content.count("time.sleep") > 5:
                                gap = SystemGap(
                                    gap_id=f"perf_sleep_{hash(str(file_path)) % 1000000:06d}",
                                    category="performance",
                                    title="Excessive Sleep Operations",
                                    description=f"File contains {content.count('time.sleep')} sleep operations",
                                    severity="low",
                                    status="identified",
                                    priority=4,
                                    location=str(file_path),
                                    evidence=[f"Multiple sleep calls detected"],
                                    suggested_solution="Review sleep usage and consider async operations"
                                )
                                gaps.append(gap)

                    except Exception:
                        pass  # Skip files that can't be read

        return gaps

    def _scan_security(self) -> List[SystemGap]:
        """Scan for security gaps"""
        gaps = []

        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']'
        ]

        for file_path in self.project_root.rglob("*.py"):
            if self._should_skip_file(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    for pattern in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Check if it's actually a hardcoded secret (not a variable reference)
                            if not any(safe_word in line.lower() for safe_word in ['os.getenv', 'config.get', 'env[', 'variable']):
                                gap = SystemGap(
                                    gap_id=f"security_hardcoded_{hash(str(file_path) + str(line_num)) % 1000000:06d}",
                                    category="security",
                                    title="Potential Hardcoded Secret",
                                    description=f"Possible hardcoded credential in {file_path.name}:{line_num}",
                                    severity="high",
                                    status="identified",
                                    priority=1,
                                    location=str(file_path),
                                    evidence=[line.strip()],
                                    suggested_solution="Move to environment variables or secure config"
                                )
                                gaps.append(gap)
                                break

            except Exception:
                pass

        return gaps

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during analysis"""
        skip_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            "*.pyc",
            ".pytest_cache",
            ".vscode",
            "logs/",
            "data/cache/"
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)

    def generate_gap_report(self) -> GapAnalysisReport:
        """Generate comprehensive gap analysis report"""
        report = GapAnalysisReport()

        # Count gaps by severity and status
        for gap in self.gaps.values():
            report.total_gaps += 1

            if gap.severity == "critical":
                report.critical_gaps += 1
            elif gap.severity == "high":
                report.high_gaps += 1
            elif gap.severity == "medium":
                report.medium_gaps += 1
            else:
                report.low_gaps += 1

            if gap.status == "resolved":
                report.resolved_gaps += 1

            # Count by category
            report.gaps_by_category[gap.category] = report.gaps_by_category.get(gap.category, 0) + 1

            # Count by status
            report.gaps_by_status[gap.status] = report.gaps_by_status.get(gap.status, 0) + 1

        # Get top priority gaps (not resolved)
        unresolved_gaps = [g for g in self.gaps.values() if g.status != "resolved"]
        unresolved_gaps.sort(key=lambda x: (x.priority, x.severity))
        report.top_priority_gaps = unresolved_gaps[:10]

        # Calculate system health score
        total_weighted_gaps = (
            report.critical_gaps * 4 +
            report.high_gaps * 3 +
            report.medium_gaps * 2 +
            report.low_gaps * 1
        )

        # Health score = 100 - (weighted gaps / total components estimate)
        # Assuming ~100 components, adjust as needed
        estimated_components = 100
        report.system_health_score = max(0, 100 - (total_weighted_gaps / estimated_components * 10))

        return report

    def print_gap_report(self) -> None:
        """Print comprehensive gap analysis report"""
        report = self.generate_gap_report()

        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE GAP ANALYSIS REPORT")
        print("="*80)

        print(f"📊 Total Gaps Identified: {report.total_gaps}")
        print(f"✅ Resolved Gaps: {report.resolved_gaps}")
        print(f"🔄 Active Gaps: {report.total_gaps - report.resolved_gaps}")
        print(".1f")

        print("\n📈 Gap Severity Breakdown:")
        print(f"  🔴 Critical: {report.critical_gaps}")
        print(f"  🟠 High: {report.high_gaps}")
        print(f"  🟡 Medium: {report.medium_gaps}")
        print(f"  🟢 Low: {report.low_gaps}")

        print("\n📂 Gaps by Category:")
        for category, count in sorted(report.gaps_by_category.items()):
            print(f"  • {category.title()}: {count}")

        print("\n🔄 Gaps by Status:")
        for status, count in sorted(report.gaps_by_status.items()):
            print(f"  • {status.title()}: {count}")

        if report.top_priority_gaps:
            print("\n🎯 Top Priority Gaps:")
            for i, gap in enumerate(report.top_priority_gaps[:5], 1):
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(gap.severity, "⚪")
                print(f"  {i}. {severity_emoji} [{gap.category}] {gap.title}")
                print(f"     📍 {gap.location}")
                print(f"     💡 {gap.suggested_solution[:60]}{'...' if len(gap.suggested_solution) > 60 else ''}")

        print("\n" + "="*80)

    def close_gap(self, gap_id: str, resolution_notes: str = "") -> bool:
        """Mark a gap as resolved"""
        if gap_id in self.gaps:
            self.gaps[gap_id].status = "resolved"
            self.gaps[gap_id].resolved_at = datetime.now()

            if resolution_notes:
                self.gaps[gap_id].evidence.append(f"Resolution: {resolution_notes}")

            self._save_gaps()
            print(f"✅ Gap {gap_id} marked as resolved")
            return True

        print(f"❌ Gap {gap_id} not found")
        return False

def main():
    """CLI interface for gap analysis"""
    import argparse

    parser = argparse.ArgumentParser(description="Gap Analysis & Closure System")
    parser.add_argument("--scan", action="store_true", help="Scan for new gaps")
    parser.add_argument("--report", action="store_true", help="Generate gap report")
    parser.add_argument("--close", type=str, help="Close a specific gap (provide gap_id)")
    parser.add_argument("--resolution", type=str, help="Resolution notes when closing gap")

    args = parser.parse_args()

    system = GapAnalysisSystem()

    if args.scan:
        print("🔍 Scanning for gaps...")
        gaps_found = system.scan_for_gaps()
        total_new = sum(len(category_gaps) for category_gaps in gaps_found.values())
        print(f"📊 Scan complete: {total_new} new gaps identified")

    if args.close:
        if args.resolution:
            system.close_gap(args.close, args.resolution)
        else:
            system.close_gap(args.close)

    if args.report or not any([args.scan, args.close]):
        system.print_gap_report()

if __name__ == "__main__":


    main()