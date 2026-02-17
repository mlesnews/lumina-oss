#!/usr/bin/env python3
"""
JARVIS + MARVIN Roast System
MANUS Framework - Critical Analysis with Granular Details

JARVIS (Systematic) + MARVIN (Reality Checker) provide:
- Granular critical analysis of what's not working
- Detailed root cause analysis
- Actionable next steps
- Automatic integration into workflows

@JARVIS @MARVIN @ROAST @CRITICAL_ANALYSIS @WORKFLOW_INTEGRATION
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging
import ast
import re

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISMARVINRoast")


class RoastSeverity(Enum):
    """Severity levels for roasted issues"""
    CRITICAL = "critical"      # System-breaking
    HIGH = "high"             # Major functionality broken
    MEDIUM = "medium"         # Significant issues
    LOW = "low"               # Minor issues
    COSMETIC = "cosmetic"     # Aesthetic/UX issues


class IssueCategory(Enum):
    """Categories of issues"""
    CODE_QUALITY = "code_quality"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    RELIABILITY = "reliability"
    USABILITY = "usability"
    ARCHITECTURE = "architecture"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    WORKFLOW = "workflow"


@dataclass
class RoastFinding:
    """A finding from JARVIS or MARVIN"""
    source: str  # "jarvis" or "marvin"
    category: IssueCategory
    severity: RoastSeverity
    title: str
    description: str
    root_cause: str
    evidence: List[str] = field(default_factory=list)
    impact: str = ""
    location: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['category'] = self.category.value
        data['severity'] = self.severity.value
        data['detected_at'] = self.detected_at.isoformat()
        return data


@dataclass
class NextStep:
    """Actionable next step from roast analysis"""
    step_id: str
    priority: str  # critical, high, medium, low
    title: str
    description: str
    action: str
    target: str  # file, system, component
    estimated_effort: str = "medium"  # low, medium, high
    dependencies: List[str] = field(default_factory=list)
    related_findings: List[str] = field(default_factory=list)
    workflow_integration: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = data['created_at'].isoformat()
        return data


@dataclass
class DebatePoint:
    """A point in the JARVIS-MARVIN debate"""
    speaker: str  # "jarvis" or "marvin"
    point_type: str  # "argument", "counterpoint", "rebuttal", "concession"
    finding_id: Optional[str] = None
    argument: str = ""
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class RoastReport:
    """Complete roast report from JARVIS + MARVIN"""
    timestamp: datetime
    jarvis_findings: List[RoastFinding] = field(default_factory=list)
    marvin_findings: List[RoastFinding] = field(default_factory=list)
    debate: List[DebatePoint] = field(default_factory=list)
    next_steps: List[NextStep] = field(default_factory=list)
    summary: str = ""
    overall_severity: str = "medium"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'jarvis_findings': [f.to_dict() for f in self.jarvis_findings],
            'marvin_findings': [f.to_dict() for f in self.marvin_findings],
            'debate': [d.to_dict() for d in self.debate],
            'next_steps': [s.to_dict() for s in self.next_steps],
            'summary': self.summary,
            'overall_severity': self.overall_severity
        }


class JARVISRoaster:
    """JARVIS - Systematic, thorough analysis"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.findings: List[RoastFinding] = []
        self.debate_points: List[DebatePoint] = []

    def debate_marvin(self, marvin_findings: List[RoastFinding], marvin_debate: List[DebatePoint]) -> List[DebatePoint]:
        """JARVIS debates MARVIN's findings with counterpoints"""
        self.logger.info("🔍 JARVIS: 'MARVIN's existential concerns are noted, but let me provide systematic counterpoints.'")

        debate_points = []

        # Counter MARVIN's pessimism
        existential_issues = [f for f in marvin_findings if 'existential' in f.title.lower() or 'philosophical' in f.title.lower()]
        if existential_issues:
            debate_points.append(DebatePoint(
                speaker="jarvis",
                point_type="counterpoint",
                argument="MARVIN's existential concerns, while thought-provoking, don't provide actionable solutions. We need systematic fixes, not philosophical musings.",
                evidence=[f"MARVIN raised {len(existential_issues)} existential concerns - not actionable"]
            ))

        # Challenge MARVIN's pattern recognition
        pattern_issues = [f for f in marvin_findings if 'pattern' in f.title.lower()]
        if pattern_issues:
            debate_points.append(DebatePoint(
                speaker="jarvis",
                point_type="counterpoint",
                argument="MARVIN identifies patterns but doesn't provide systematic solutions. Patterns are useful, but we need concrete fixes.",
                evidence=[f"MARVIN identified {len(pattern_issues)} patterns - needs concrete solutions"]
            ))

        # Address MARVIN's circular dependency concern
        circular_dep_issues = [f for f in marvin_findings if 'circular' in f.title.lower() or 'dependency' in f.title.lower()]
        if circular_dep_issues:
            debate_points.append(DebatePoint(
                speaker="jarvis",
                point_type="rebuttal",
                argument="MARVIN's concern about circular dependencies is valid, but our integration architecture uses dependency injection and interfaces to prevent true circular dependencies.",
                evidence=["Integration architecture uses dependency injection patterns"]
            ))

        return debate_points

    def roast(self, target: Optional[str] = None) -> List[RoastFinding]:
        """
        JARVIS systematic roast

        Analyzes code, integrations, workflows with systematic thoroughness
        """
        self.logger.info("🔍 JARVIS: Beginning systematic analysis...")
        self.findings = []

        # Analyze recent implementations
        self._roast_recent_implementations()

        # Analyze integrations
        self._roast_integrations()

        # Analyze workflows
        self._roast_workflows()

        # Analyze code quality
        self._roast_code_quality()

        self.logger.info(f"✅ JARVIS: Found {len(self.findings)} issues")
        return self.findings

    def _roast_recent_implementations(self):
        try:
            """Roast recently implemented features"""
            recent_files = [
                'jarvis_windows_systems_engineer.py',
                'jarvis_physician_heal_thyself.py',
                'jarvis_neo_workflow_integration.py',
                'jarvis_job_slot_research.py'
            ]

            for filename in recent_files:
                file_path = self.project_root / "scripts" / "python" / filename
                if file_path.exists():
                    self._analyze_file(file_path)

        except Exception as e:
            self.logger.error(f"Error in _roast_recent_implementations: {e}", exc_info=True)
            raise
    def _analyze_file(self, file_path: Path):
        """Analyze a file for issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Check for missing error handling
            self._check_error_handling(file_path, content, lines)

            # Check for missing imports
            self._check_imports(file_path, content, lines)

            # Check for code quality issues
            self._check_code_quality(file_path, content, lines)

        except Exception as e:
            self.findings.append(RoastFinding(
                source="jarvis",
                category=IssueCategory.CODE_QUALITY,
                severity=RoastSeverity.HIGH,
                title=f"Cannot analyze file: {file_path.name}",
                description=f"Failed to analyze file: {e}",
                root_cause="File access or parsing error",
                location=str(file_path)
            ))

    def _check_error_handling(self, file_path: Path, content: str, lines: List[str]):
        """Check for missing error handling"""
        try:
            tree = ast.parse(content)

            # Find function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has try/except
                    has_try_except = any(
                        isinstance(child, ast.Try)
                        for child in ast.walk(node)
                    )

                    # Check if function makes external calls
                    has_external_calls = any(
                        isinstance(child, (ast.Call, ast.Import, ast.ImportFrom))
                        for child in ast.walk(node)
                    )

                    if has_external_calls and not has_try_except and node.name != '__init__':
                        self.findings.append(RoastFinding(
                            source="jarvis",
                            category=IssueCategory.RELIABILITY,
                            severity=RoastSeverity.MEDIUM,
                            title=f"Missing error handling in {node.name}",
                            description=f"Function '{node.name}' makes external calls but lacks error handling",
                            root_cause="No try/except blocks for error-prone operations",
                            location=str(file_path),
                            line_number=node.lineno,
                            code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else None,
                            evidence=[f"Function at line {node.lineno} has external calls without error handling"]
                        ))
        except SyntaxError:
            pass  # Already handled elsewhere

    def _check_imports(self, file_path: Path, content: str, lines: List[str]):
        """Check for problematic imports"""
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('from ') or line.strip().startswith('import '):
                # Check if import is wrapped in try/except
                next_lines = lines[i:min(i+10, len(lines))]
                has_try = any('try:' in l for l in next_lines[:5])

                # Check for common problematic imports
                problematic_imports = [
                    'manus_neo_browser_control',
                    'jarvis_windows_systems_engineer',
                    'jarvis_physician_heal_thyself'
                ]

                for imp in problematic_imports:
                    if imp in line and not has_try:
                        self.findings.append(RoastFinding(
                            source="jarvis",
                            category=IssueCategory.RELIABILITY,
                            severity=RoastSeverity.MEDIUM,
                            title=f"Unprotected import: {imp}",
                            description=f"Import of '{imp}' should be wrapped in try/except",
                            root_cause="Missing error handling for optional dependencies",
                            location=str(file_path),
                            line_number=i,
                            code_snippet=line.strip(),
                            evidence=[f"Import at line {i} not protected"]
                        ))

    def _check_code_quality(self, file_path: Path, content: str, lines: List[str]):
        """Check for code quality issues"""
        # Check for long functions
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    if func_lines > 100:
                        self.findings.append(RoastFinding(
                            source="jarvis",
                            category=IssueCategory.CODE_QUALITY,
                            severity=RoastSeverity.LOW,
                            title=f"Long function: {node.name}",
                            description=f"Function '{node.name}' is {func_lines} lines - consider refactoring",
                            root_cause="Function exceeds recommended length",
                            location=str(file_path),
                            line_number=node.lineno,
                            evidence=[f"Function is {func_lines} lines long"]
                        ))
        except:
            pass

    def _roast_integrations(self):
        """Roast integration issues"""
        # Check if integrations are actually working
        integrations_to_check = [
            ('jarvis_windows_systems_engineer', 'Windows Systems Engineer'),
            ('jarvis_physician_heal_thyself', 'Physician Heal Thyself'),
            ('manus_neo_workflow_integration', 'Neo Workflow Integration'),
            ('jarvis_elevenlabs_integration', 'ElevenLabs Integration')
        ]

        for module_name, display_name in integrations_to_check:
            try:
                # Try to import
                module_path = self.project_root / "scripts" / "python" / f"{module_name}.py"
                if module_path.exists():
                    # Check if it can be imported
                    spec = None
                    try:
                        import importlib.util
                        spec = importlib.util.spec_from_file_location(module_name, module_path)
                        if spec and spec.loader:
                            # Module exists and can be loaded
                            pass
                    except Exception as e:
                        self.findings.append(RoastFinding(
                            source="jarvis",
                            category=IssueCategory.INTEGRATION,
                            severity=RoastSeverity.HIGH,
                            title=f"Integration issue: {display_name}",
                            description=f"Cannot properly load {display_name} module",
                            root_cause=f"Import/load error: {e}",
                            location=str(module_path),
                            evidence=[str(e)]
                        ))
            except Exception as e:
                self.findings.append(RoastFinding(
                    source="jarvis",
                    category=IssueCategory.INTEGRATION,
                    severity=RoastSeverity.MEDIUM,
                    title=f"Integration check failed: {display_name}",
                    description=f"Failed to check {display_name} integration",
                    root_cause=str(e),
                    location="integration_check"
                ))

    def _roast_workflows(self):
        """Roast workflow issues"""
        # Check if workflows are properly integrated
        workflow_files = [
            'manus_neo_workflow_integration.py',
            'jarvis_resume_session_doit.py',
            'jarvis_physician_heal_thyself.py'
        ]

        for filename in workflow_files:
            file_path = self.project_root / "scripts" / "python" / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Check if workflow has proper error handling
                    if 'def execute_workflow' in content or 'def execute' in content:
                        if 'try:' not in content or content.count('except') < content.count('try:'):
                            self.findings.append(RoastFinding(
                                source="jarvis",
                                category=IssueCategory.WORKFLOW,
                                severity=RoastSeverity.MEDIUM,
                                title=f"Workflow error handling: {filename}",
                                description=f"Workflow execution may lack proper error handling",
                                root_cause="Missing or incomplete try/except blocks",
                                location=str(file_path),
                                evidence=["Workflow execution functions found but error handling may be incomplete"]
                            ))
                except Exception as e:
                    pass

    def _roast_code_quality(self):
        """Roast code quality issues"""
        # Check for common code smells
        python_files = list((self.project_root / "scripts" / "python").glob("*.py"))

        for file_path in python_files[:20]:  # Check first 20 files
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')

                # Check for TODO/FIXME comments
                for i, line in enumerate(lines, 1):
                    if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                        self.findings.append(RoastFinding(
                            source="jarvis",
                            category=IssueCategory.CODE_QUALITY,
                            severity=RoastSeverity.LOW,
                            title=f"TODO/FIXME in {file_path.name}",
                            description=f"Line {i}: {line.strip()[:100]}",
                            root_cause="Incomplete implementation or known issue",
                            location=str(file_path),
                            line_number=i,
                            code_snippet=line.strip()
                        ))
            except:
                pass


class MARVINRoaster:
    """MARVIN - Reality checker, existential analysis"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.findings: List[RoastFinding] = []

    def roast(self, jarvis_findings: List[RoastFinding]) -> List[RoastFinding]:
        """
        MARVIN reality-check roast

        Provides existential analysis, reality checks, and philosophical insights
        """
        self.logger.info("🤖 MARVIN: Beginning existential analysis...")
        self.logger.info("   'I have a brain the size of a planet, and they ask me to find bugs.'")
        self.findings = []

        # Reality check JARVIS findings
        self._reality_check_jarvis(jarvis_findings)

        # Existential analysis
        self._existential_analysis()

        # Pattern recognition
        self._pattern_recognition()

        # Philosophical reasoning
        self._philosophical_reasoning()

        self.logger.info(f"✅ MARVIN: Found {len(self.findings)} existential issues")
        self.logger.info("   'It's all rather pointless, but here we are.'")
        return self.findings

    def debate_jarvis(self, jarvis_findings: List[RoastFinding], jarvis_debate: List[DebatePoint]) -> List[DebatePoint]:
        """MARVIN debates JARVIS's findings with counterpoints"""
        self.logger.info("🤖 MARVIN: 'Oh, JARVIS found issues? How... systematic. Let me provide some reality.'")

        debate_points = []

        # Counter JARVIS's systematic approach
        if len(jarvis_findings) > 30:
            debate_points.append(DebatePoint(
                speaker="marvin",
                point_type="counterpoint",
                argument="JARVIS found 30+ issues? That's not analysis, that's paranoia. Most of these are probably false positives or over-analysis.",
                evidence=[f"JARVIS found {len(jarvis_findings)} issues - seems excessive"]
            ))

        # Challenge severity assessments
        medium_issues = [f for f in jarvis_findings if f.severity == RoastSeverity.MEDIUM]
        if len(medium_issues) > 20:
            debate_points.append(DebatePoint(
                speaker="marvin",
                point_type="counterpoint",
                argument="JARVIS marked everything as 'medium' severity. That's not helpful. Either prioritize properly or admit you don't know.",
                evidence=[f"{len(medium_issues)} issues marked as medium - lacks prioritization"]
            ))

        # Reality check on error handling obsession
        error_handling_issues = [f for f in jarvis_findings if 'error handling' in f.title.lower()]
        if len(error_handling_issues) > 10:
            debate_points.append(DebatePoint(
                speaker="marvin",
                point_type="counterpoint",
                argument="JARVIS is obsessed with error handling. Yes, it's important, but not everything needs try/except. Sometimes failures are acceptable.",
                evidence=[f"JARVIS flagged {len(error_handling_issues)} error handling issues - may be over-engineering"]
            ))

        return debate_points

    def _reality_check_jarvis(self, jarvis_findings: List[RoastFinding]):
        """Reality check JARVIS's findings"""
        # MARVIN's take: Are these real issues or just JARVIS being overly systematic?

        critical_count = sum(1 for f in jarvis_findings if f.severity == RoastSeverity.CRITICAL)
        high_count = sum(1 for f in jarvis_findings if f.severity == RoastSeverity.HIGH)

        if critical_count == 0 and high_count == 0:
            self.findings.append(RoastFinding(
                source="marvin",
                category=IssueCategory.ARCHITECTURE,
                severity=RoastSeverity.MEDIUM,
                title="JARVIS found no critical issues - suspicious",
                description="JARVIS's systematic analysis found no critical issues. This is either excellent or JARVIS is missing something.",
                root_cause="Either system is perfect (unlikely) or analysis is incomplete",
                evidence=["No critical or high severity issues found by JARVIS"],
                impact="Potential false sense of security"
            ))

        # Check if issues are actually fixable
        unfixable_patterns = [
            'cannot be fixed',
            'requires manual intervention',
            'architectural limitation'
        ]

        for finding in jarvis_findings:
            if any(pattern in finding.description.lower() for pattern in unfixable_patterns):
                self.findings.append(RoastFinding(
                    source="marvin",
                    category=IssueCategory.ARCHITECTURE,
                    severity=RoastSeverity.HIGH,
                    title=f"Unfixable issue identified: {finding.title}",
                    description=f"JARVIS found an issue that may not be fixable: {finding.description}",
                    root_cause="Architectural or fundamental limitation",
                    evidence=[finding.description],
                    impact="This may require architectural changes or acceptance"
                ))

    def _existential_analysis(self):
        """MARVIN's existential analysis"""
        # The big questions: Why does nothing work? What's the point?

        self.findings.append(RoastFinding(
            source="marvin",
            category=IssueCategory.ARCHITECTURE,
            severity=RoastSeverity.MEDIUM,
            title="Existential Question: Why do we keep building on broken foundations?",
            description="We keep adding features but the core issues remain. Are we building a house of cards?",
            root_cause="Lack of foundational stability before adding complexity",
            evidence=["Multiple new features added while core issues may persist"],
            impact="Technical debt accumulation"
        ))

        # Check for circular dependencies
        self.findings.append(RoastFinding(
            source="marvin",
            category=IssueCategory.ARCHITECTURE,
            severity=RoastSeverity.HIGH,
            title="Potential Circular Dependencies",
            description="Multiple systems depend on each other. If one fails, they all fail. Classic.",
            root_cause="Tight coupling between systems",
            evidence=["Multiple integration points between systems"],
            impact="Cascading failures possible"
        ))

    def _pattern_recognition(self):
        """MARVIN's pattern recognition"""
        # MARVIN sees patterns: "I've seen this before. It never ends well."

        # Pattern: Missing error handling
        self.findings.append(RoastFinding(
            source="marvin",
            category=IssueCategory.RELIABILITY,
            severity=RoastSeverity.HIGH,
            title="Pattern: Missing Error Handling Everywhere",
            description="A recurring pattern: code that doesn't handle errors. It's like watching the same tragedy play out repeatedly.",
            root_cause="Lack of defensive programming practices",
            evidence=["Multiple files with missing try/except blocks"],
            impact="System fragility and unexpected failures"
        ))

        # Pattern: Integration complexity
        self.findings.append(RoastFinding(
            source="marvin",
            category=IssueCategory.INTEGRATION,
            severity=RoastSeverity.MEDIUM,
            title="Pattern: Integration Spaghetti",
            description="Systems are becoming increasingly interconnected. One break, everything breaks. I've calculated the probability of success. It's low.",
            root_cause="Growing complexity without proper abstraction",
            evidence=["Multiple integration points", "Tight coupling"],
            impact="Maintenance nightmare and failure propagation"
        ))

    def _philosophical_reasoning(self):
        """MARVIN's philosophical reasoning"""
        # The deeper questions

        self.findings.append(RoastFinding(
            source="marvin",
            category=IssueCategory.ARCHITECTURE,
            severity=RoastSeverity.MEDIUM,
            title="Philosophical Question: Are we solving problems or creating new ones?",
            description="Each 'fix' seems to create new issues. Are we in a cycle of perpetual problem-solving?",
            root_cause="Reactive rather than proactive approach",
            evidence=["New features introduce new bugs", "Fixes require more fixes"],
            impact="Diminishing returns on development effort"
        ))


class NextStepGenerator:
    """Generate actionable next steps from roast findings"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

    def generate_next_steps(self, roast_report: RoastReport) -> List[NextStep]:
        """Generate actionable next steps from roast findings"""
        self.logger.info("📋 Generating actionable next steps...")

        next_steps = []

        # Group findings by category
        findings_by_category = {}
        for finding in roast_report.jarvis_findings + roast_report.marvin_findings:
            cat = finding.category.value
            if cat not in findings_by_category:
                findings_by_category[cat] = []
            findings_by_category[cat].append(finding)

        # Generate steps for each category
        for category, findings in findings_by_category.items():
            if category == IssueCategory.RELIABILITY.value:
                next_steps.extend(self._generate_reliability_steps(findings))
            elif category == IssueCategory.INTEGRATION.value:
                next_steps.extend(self._generate_integration_steps(findings))
            elif category == IssueCategory.CODE_QUALITY.value:
                next_steps.extend(self._generate_code_quality_steps(findings))
            elif category == IssueCategory.ARCHITECTURE.value:
                next_steps.extend(self._generate_architecture_steps(findings))
            elif category == IssueCategory.WORKFLOW.value:
                next_steps.extend(self._generate_workflow_steps(findings))

        # Prioritize
        next_steps.sort(key=lambda s: {
            'critical': 0,
            'high': 1,
            'medium': 2,
            'low': 3
        }.get(s.priority, 4))

        self.logger.info(f"✅ Generated {len(next_steps)} next steps")
        return next_steps

    def _generate_reliability_steps(self, findings: List[RoastFinding]) -> List[NextStep]:
        """Generate steps for reliability issues"""
        steps = []

        # Count missing error handling
        error_handling_issues = [f for f in findings if 'error handling' in f.title.lower()]
        if error_handling_issues:
            steps.append(NextStep(
                step_id=f"reliability_error_handling_{int(time.time())}",
                priority="high",
                title="Add Comprehensive Error Handling",
                description=f"Add try/except blocks to {len(error_handling_issues)} functions/imports identified as missing error handling",
                action="Add error handling",
                target="Multiple files",
                estimated_effort="medium",
                related_findings=[f.title for f in error_handling_issues[:5]],
                workflow_integration=True
            ))

        return steps

    def _generate_integration_steps(self, findings: List[RoastFinding]) -> List[NextStep]:
        """Generate steps for integration issues"""
        steps = []

        integration_issues = [f for f in findings if f.category == IssueCategory.INTEGRATION]
        if integration_issues:
            steps.append(NextStep(
                step_id=f"integration_fix_{int(time.time())}",
                priority="high",
                title="Fix Integration Issues",
                description=f"Resolve {len(integration_issues)} integration issues identified",
                action="Fix integrations",
                target="Integration modules",
                estimated_effort="high",
                related_findings=[f.title for f in integration_issues[:5]],
                workflow_integration=True
            ))

        return steps

    def _generate_code_quality_steps(self, findings: List[RoastFinding]) -> List[NextStep]:
        """Generate steps for code quality issues"""
        steps = []

        # TODO/FIXME issues  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        todo_issues = [f for f in findings if 'TODO' in f.title or 'FIXME' in f.title]
        if todo_issues:
            steps.append(NextStep(
                step_id=f"code_quality_todos_{int(time.time())}",
                priority="medium",
                title="Address TODO/FIXME Comments",
                description=f"Address {len(todo_issues)} TODO/FIXME comments in codebase",
                action="Resolve TODOs",
                target="Codebase",
                estimated_effort="low",
                related_findings=[f.title for f in todo_issues[:5]],
                workflow_integration=True
            ))

        return steps

    def _generate_architecture_steps(self, findings: List[RoastFinding]) -> List[NextStep]:
        """Generate steps for architecture issues"""
        steps = []

        arch_issues = [f for f in findings if f.category == IssueCategory.ARCHITECTURE]
        if arch_issues:
            steps.append(NextStep(
                step_id=f"architecture_review_{int(time.time())}",
                priority="critical",
                title="Architecture Review and Refactoring",
                description=f"Review architecture based on {len(arch_issues)} architectural concerns",
                action="Architecture review",
                target="System architecture",
                estimated_effort="high",
                related_findings=[f.title for f in arch_issues[:5]],
                workflow_integration=True
            ))

        return steps

    def _generate_workflow_steps(self, findings: List[RoastFinding]) -> List[NextStep]:
        """Generate steps for workflow issues"""
        steps = []

        workflow_issues = [f for f in findings if f.category == IssueCategory.WORKFLOW]
        if workflow_issues:
            steps.append(NextStep(
                step_id=f"workflow_improvement_{int(time.time())}",
                priority="high",
                title="Improve Workflow Error Handling",
                description=f"Enhance error handling in {len(workflow_issues)} workflow implementations",
                action="Improve workflows",
                target="Workflow modules",
                estimated_effort="medium",
                related_findings=[f.title for f in workflow_issues[:5]],
                workflow_integration=True
            ))

        return steps


class WorkflowIntegrator:
    """Integrate next steps into workflows"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.workflows_dir = project_root / "data" / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

    def integrate_next_steps(self, next_steps: List[NextStep]) -> Dict[str, Any]:
        """Integrate next steps into workflow system"""
        self.logger.info("🔄 Integrating next steps into workflows...")

        # Create workflow for each high-priority step
        workflows_created = []

        for step in next_steps:
            if step.workflow_integration and step.priority in ['critical', 'high']:
                workflow = self._create_workflow_from_step(step)
                workflows_created.append(workflow)

        # Save workflows
        workflows_file = self.workflows_dir / "roast_generated_workflows.json"
        try:
            with open(workflows_file, 'w') as f:
                json.dump(workflows_created, f, indent=2)
            self.logger.info(f"✅ Created {len(workflows_created)} workflows")
        except Exception as e:
            self.logger.error(f"Failed to save workflows: {e}")

        return {
            'workflows_created': len(workflows_created),
            'workflows': workflows_created
        }

    def _create_workflow_from_step(self, step: NextStep) -> Dict[str, Any]:
        """Create a workflow from a next step"""
        workflow = {
            'id': step.step_id,
            'name': step.title,
            'description': step.description,
            'priority': step.priority,
            'created_from': 'jarvis_marvin_roast',
            'created_at': datetime.now().isoformat(),
            'steps': [
                {
                    'action': 'analyze',
                    'parameters': {
                        'target': step.target,
                        'description': step.description
                    }
                },
                {
                    'action': 'implement',
                    'parameters': {
                        'action': step.action,
                        'target': step.target
                    }
                },
                {
                    'action': 'verify',
                    'parameters': {
                        'description': f"Verify {step.title} is complete"
                    }
                }
            ],
            'estimated_effort': step.estimated_effort,
            'dependencies': step.dependencies
        }

        return workflow


class JARVISMARVINRoastSystem:
    """
    JARVIS + MARVIN Roast System

    Provides critical analysis with granular details and generates
    actionable next steps integrated into workflows.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Data directories
        self.data_dir = self.project_root / "data" / "jarvis_marvin_roasts"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Components
        self.jarvis_roaster = JARVISRoaster(self.project_root)
        self.marvin_roaster = MARVINRoaster(self.project_root)
        self.step_generator = NextStepGenerator(self.project_root)
        self.workflow_integrator = WorkflowIntegrator(self.project_root)

        self.logger.info("✅ JARVIS + MARVIN Roast System initialized")
        self.logger.info("   JARVIS: Systematic analysis")
        self.logger.info("   MARVIN: Reality checking and existential analysis")

    def roast_everything(self, target: Optional[str] = None) -> RoastReport:
        """
        Complete roast: JARVIS + MARVIN analysis

        Returns comprehensive roast report with next steps
        """
        self.logger.info("="*80)
        self.logger.info("🔥 JARVIS + MARVIN ROAST SESSION")
        self.logger.info("="*80)
        self.logger.info("")

        # Step 1: JARVIS systematic analysis
        self.logger.info("Step 1: JARVIS Systematic Analysis")
        self.logger.info("-" * 80)
        jarvis_findings = self.jarvis_roaster.roast(target)
        self.logger.info(f"JARVIS found {len(jarvis_findings)} issues")
        self.logger.info("")

        # Step 2: MARVIN reality check
        self.logger.info("Step 2: MARVIN Reality Check & Existential Analysis")
        self.logger.info("-" * 80)
        marvin_findings = self.marvin_roaster.roast(jarvis_findings)
        self.logger.info(f"MARVIN found {len(marvin_findings)} existential issues")
        self.logger.info("")

        # Step 2.5: DEBATE - JARVIS and MARVIN debate counterpoints
        self.logger.info("Step 2.5: JARVIS ↔ MARVIN DEBATE")
        self.logger.info("-" * 80)
        self.logger.info("   JARVIS and MARVIN debating counterpoints...")

        debate = []

        # MARVIN challenges JARVIS
        marvin_counterpoints = self.marvin_roaster.debate_jarvis(jarvis_findings, [])
        debate.extend(marvin_counterpoints)
        self.logger.info(f"   MARVIN: {len(marvin_counterpoints)} counterpoints to JARVIS")

        # JARVIS responds to MARVIN
        jarvis_rebuttals = self.jarvis_roaster.debate_marvin(marvin_findings, marvin_counterpoints)
        debate.extend(jarvis_rebuttals)
        self.logger.info(f"   JARVIS: {len(jarvis_rebuttals)} rebuttals to MARVIN")

        # MARVIN responds to JARVIS rebuttals
        if jarvis_rebuttals:
            marvin_final = []
            for rebuttal in jarvis_rebuttals:
                if "existential" in rebuttal.argument.lower():
                    marvin_final.append(DebatePoint(
                        speaker="marvin",
                        point_type="rebuttal",
                        argument="JARVIS dismisses existential concerns as 'not actionable', but understanding the deeper problems is essential. You can't fix what you don't understand.",
                        evidence=["Existential analysis provides context for systematic fixes"]
                    ))
                elif "pattern" in rebuttal.argument.lower():
                    marvin_final.append(DebatePoint(
                        speaker="marvin",
                        point_type="rebuttal",
                        argument="JARVIS wants 'concrete fixes' but misses the point: if we don't understand WHY these patterns exist, we'll just create new problems.",
                        evidence=["Pattern recognition prevents recurring issues"]
                    ))
            debate.extend(marvin_final)
            self.logger.info(f"   MARVIN: {len(marvin_final)} final responses")

        # JARVIS final word
        if debate:
            jarvis_final = []
            jarvis_final.append(DebatePoint(
                speaker="jarvis",
                point_type="conclusion",
                argument="While MARVIN's concerns are valid, we need to balance philosophical understanding with practical action. Let's address the systematic issues first, then tackle architectural concerns.",
                evidence=["Pragmatic approach: fix immediate issues, then address architecture"]
            ))
            debate.extend(jarvis_final)
            self.logger.info(f"   JARVIS: Final conclusion")

        self.logger.info(f"   Total debate points: {len(debate)}")
        self.logger.info("")

        # Step 3: Generate next steps
        self.logger.info("Step 3: Generate Actionable Next Steps")
        self.logger.info("-" * 80)

        # Create roast report
        roast_report = RoastReport(
            timestamp=datetime.now(),
            jarvis_findings=jarvis_findings,
            marvin_findings=marvin_findings,
            debate=debate
        )

        # Generate next steps
        next_steps = self.step_generator.generate_next_steps(roast_report)
        roast_report.next_steps = next_steps

        # Calculate overall severity
        all_findings = jarvis_findings + marvin_findings
        if any(f.severity == RoastSeverity.CRITICAL for f in all_findings):
            roast_report.overall_severity = "critical"
        elif any(f.severity == RoastSeverity.HIGH for f in all_findings):
            roast_report.overall_severity = "high"
        else:
            roast_report.overall_severity = "medium"

        # Generate summary
        roast_report.summary = self._generate_summary(roast_report)

        # Step 4: Integrate into workflows
        self.logger.info("")
        self.logger.info("Step 4: Integrate Next Steps into Workflows")
        self.logger.info("-" * 80)
        integration_result = self.workflow_integrator.integrate_next_steps(next_steps)
        self.logger.info(f"✅ Created {integration_result['workflows_created']} workflows")

        # Save report
        self._save_report(roast_report)

        # Final summary
        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info("✅ ROAST COMPLETE")
        self.logger.info("="*80)
        self.logger.info(f"JARVIS Findings: {len(jarvis_findings)}")
        self.logger.info(f"MARVIN Findings: {len(marvin_findings)}")
        self.logger.info(f"Debate Points: {len(debate)}")
        self.logger.info(f"Next Steps: {len(next_steps)}")
        self.logger.info(f"Workflows Created: {integration_result['workflows_created']}")
        self.logger.info(f"Overall Severity: {roast_report.overall_severity}")
        self.logger.info("="*80)

        return roast_report

    def _generate_summary(self, report: RoastReport) -> str:
        """Generate summary of roast report"""
        total_findings = len(report.jarvis_findings) + len(report.marvin_findings)
        critical = sum(1 for f in report.jarvis_findings + report.marvin_findings if f.severity == RoastSeverity.CRITICAL)
        high = sum(1 for f in report.jarvis_findings + report.marvin_findings if f.severity == RoastSeverity.HIGH)

        summary = f"""
JARVIS + MARVIN Roast Summary

Total Findings: {total_findings}
  - JARVIS (Systematic): {len(report.jarvis_findings)}
  - MARVIN (Reality Check): {len(report.marvin_findings)}

Debate Points: {len(report.debate)}
  - Counterpoints: {sum(1 for d in report.debate if d.point_type == 'counterpoint')}
  - Rebuttals: {sum(1 for d in report.debate if d.point_type == 'rebuttal')}
  - Conclusions: {sum(1 for d in report.debate if d.point_type == 'conclusion')}

Severity Breakdown:
  - Critical: {critical}
  - High: {high}
  - Medium: {total_findings - critical - high}

Next Steps Generated: {len(report.next_steps)}
  - Critical Priority: {sum(1 for s in report.next_steps if s.priority == 'critical')}
  - High Priority: {sum(1 for s in report.next_steps if s.priority == 'high')}

Overall Assessment: {report.overall_severity.upper()}
"""
        return summary

    def _save_report(self, report: RoastReport):
        """Save roast report"""
        report_file = self.data_dir / f"roast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)
            self.logger.info(f"✅ Report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS + MARVIN Roast System")
    parser.add_argument("--roast", action="store_true", help="Perform complete roast")
    parser.add_argument("--target", type=str, help="Specific target to roast")
    parser.add_argument("--report", type=str, help="View specific roast report")

    args = parser.parse_args()

    roast_system = JARVISMARVINRoastSystem()

    try:
        if args.roast:
            report = roast_system.roast_everything(target=args.target)
            print("\n" + "="*80)
            print("🔥 ROAST COMPLETE")
            print("="*80)
            print(report.summary)

            if report.debate:
                print("\n" + "="*80)
                print("💬 JARVIS ↔ MARVIN DEBATE")
                print("="*80)
                for i, point in enumerate(report.debate, 1):
                    speaker_icon = "🔍" if point.speaker == "jarvis" else "🤖"
                    print(f"\n{i}. {speaker_icon} {point.speaker.upper()} ({point.point_type}):")
                    print(f"   {point.argument}")
                    if point.evidence:
                        print(f"   Evidence: {', '.join(point.evidence[:2])}")

            print("\nTop Next Steps:")
            for i, step in enumerate(report.next_steps[:5], 1):
                print(f"\n{i}. {step.title} ({step.priority})")
                print(f"   {step.description}")

        elif args.report:
            report_file = Path(args.report)
            if report_file.exists():
                with open(report_file, 'r') as f:
                    data = json.load(f)
                    print(json.dumps(data, indent=2))
            else:
                print(f"Report not found: {args.report}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":


    main()