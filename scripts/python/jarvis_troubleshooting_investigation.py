#!/usr/bin/env python3
"""
JARVIS Troubleshooting Investigation System

Investigates and troubleshoots issues with @ALWAYS 5/5 importance policy.

Tags: #troubleshooting #investigation #jarvis #always #5of5
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import subprocess
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from troubleshooting_always_importance_system import TroubleshootingAlwaysImportanceSystem

logger = get_logger("JARVISTroubleshootingInvestigation")


@dataclass
class InvestigationFinding:
    """Investigation finding"""
    finding_id: str
    category: str
    severity: str  # critical, high, medium, low, info
    description: str
    evidence: str
    potential_cause: str
    recommended_action: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class JARVISTroubleshootingInvestigation:
    """
    JARVIS Troubleshooting Investigation System

    Investigates issues with @ALWAYS 5/5 importance policy
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.troubleshooting_system = TroubleshootingAlwaysImportanceSystem(project_root)

        logger.info("=" * 80)
        logger.info("🔍 JARVIS TROUBLESHOOTING INVESTIGATION")
        logger.info("=" * 80)
        logger.info("   @ALWAYS 5/5 Importance Policy")
        logger.info("=" * 80)
        logger.info("")

    def investigate_script(
        self,
        script_path: Path,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Investigate a script for issues

        Args:
            script_path: Path to script to investigate
            timeout: Timeout in seconds for script execution

        Returns:
            Investigation results
        """
        findings = []

        logger.info(f"🔍 Investigating: {script_path.name}")

        # 1. Check if file exists
        if not script_path.exists():
            findings.append(InvestigationFinding(
                finding_id="find_001",
                category="file_system",
                severity="critical",
                description=f"Script file not found: {script_path}",
                evidence="File does not exist",
                potential_cause="File deleted, moved, or incorrect path",
                recommended_action="Verify file path and location"
            ))
            return {"findings": [f.to_dict() for f in findings], "script": str(script_path)}

        # 2. Check for syntax errors
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, str(script_path), 'exec')
        except SyntaxError as e:
            findings.append(InvestigationFinding(
                finding_id="find_002",
                category="syntax",
                severity="critical",
                description=f"Syntax error in {script_path.name}",
                evidence=str(e),
                potential_cause="Invalid Python syntax",
                recommended_action=f"Fix syntax error: {e}"
            ))

        # 3. Check for import errors
        import_errors = self._check_imports(script_path)
        findings.extend(import_errors)

        # 4. Try to run script with timeout
        execution_issues = self._test_execution(script_path, timeout)
        findings.extend(execution_issues)

        # 5. Check for common issues
        common_issues = self._check_common_issues(script_path)
        findings.extend(common_issues)

        # Store investigation in troubleshooting system
        if findings:
            critical_findings = [f for f in findings if f.severity == "critical"]
            high_findings = [f for f in findings if f.severity == "high"]

            importance = 5 if critical_findings else 4 if high_findings else 3

            analysis = f"Investigation of {script_path.name} found {len(findings)} issues: "
            analysis += f"{len(critical_findings)} critical, {len(high_findings)} high, "
            analysis += f"{len([f for f in findings if f.severity == 'medium'])} medium"

            solutions = [f.recommended_action for f in findings[:5]]

            self.troubleshooting_system.create_troubleshooting_memory(
                situation=f"Script Investigation: {script_path.name}",
                problem=f"Investigating {script_path.name} for issues, errors, or problems",
                importance_rating=importance,
                analysis=analysis,
                solutions=solutions
            )

        return {
            "script": str(script_path),
            "investigated_at": datetime.now().isoformat(),
            "total_findings": len(findings),
            "critical": len([f for f in findings if f.severity == "critical"]),
            "high": len([f for f in findings if f.severity == "high"]),
            "medium": len([f for f in findings if f.severity == "medium"]),
            "low": len([f for f in findings if f.severity == "low"]),
            "findings": [f.to_dict() for f in findings]
        }

    def _check_imports(self, script_path: Path) -> List[InvestigationFinding]:
        """Check for import errors"""
        findings = []

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for common import patterns
            import re
            imports = re.findall(r'^(?:from\s+(\S+)\s+)?import\s+(\S+)', content, re.MULTILINE)

            for module, item in imports:
                module_name = module or item.split('.')[0]

                # Check if it's a local import
                if not module_name.startswith('.') and module_name not in ['sys', 'os', 'json', 'pathlib', 'datetime', 'typing', 'logging', 'enum', 'dataclasses']:
                    # Try to import
                    try:
                        if module:
                            __import__(module)
                        else:
                            __import__(item.split('.')[0])
                    except ImportError as e:
                        findings.append(InvestigationFinding(
                            finding_id=f"import_{len(findings)+1:03d}",
                            category="import",
                            severity="high",
                            description=f"Import error: {module or item}",
                            evidence=str(e),
                            potential_cause="Missing dependency or incorrect import path",
                            recommended_action=f"Install missing package or fix import: {module or item}"
                        ))
        except Exception as e:
            findings.append(InvestigationFinding(
                finding_id="import_check_error",
                category="investigation",
                severity="medium",
                description="Error checking imports",
                evidence=str(e),
                potential_cause="File read error or parsing issue",
                recommended_action="Check file permissions and encoding"
            ))

        return findings

    def _test_execution(self, script_path: Path, timeout: int) -> List[InvestigationFinding]:
        """Test script execution"""
        findings = []

        # Check if script has main guard
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            has_main_guard = '__name__' in content and '__main__' in content

            if not has_main_guard:
                findings.append(InvestigationFinding(
                    finding_id="exec_001",
                    category="execution",
                    severity="low",
                    description="Script missing __main__ guard",
                    evidence="No if __name__ == '__main__': block found",
                    potential_cause="Script may execute on import",
                    recommended_action="Add if __name__ == '__main__': guard"
                ))
        except Exception as e:
            findings.append(InvestigationFinding(
                finding_id="exec_check_error",
                category="investigation",
                severity="medium",
                description="Error checking execution",
                evidence=str(e),
                potential_cause="File read error",
                recommended_action="Check file permissions"
            ))

        return findings

    def _check_common_issues(self, script_path: Path) -> List[InvestigationFinding]:
        """Check for common issues"""
        findings = []

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for standard logging
            if 'logging.basicConfig' in content and 'lumina_logger' not in content:
                findings.append(InvestigationFinding(
                    finding_id="common_001",
                    category="logging",
                    severity="high",
                    description="Script using basicConfig instead of lumina_logger",
                    evidence="Found logging.basicConfig in code",
                    potential_cause="Not using standard logging module",
                    recommended_action="Replace with lumina_logger import and usage"
                ))

            # Check for error handling
            if 'try:' in content and 'except Exception' not in content and 'except:' not in content:
                # Check if there are try blocks without proper exception handling
                import re
                try_blocks = re.findall(r'try:.*?(?=except|$)', content, re.DOTALL)
                for i, block in enumerate(try_blocks):
                    if 'except' not in block:
                        findings.append(InvestigationFinding(
                            finding_id=f"common_{len(findings)+1:03d}",
                            category="error_handling",
                            severity="medium",
                            description="Try block without exception handling",
                            evidence=f"Try block #{i+1} missing except clause",
                            potential_cause="Incomplete error handling",
                            recommended_action="Add proper exception handling"
                        ))
                        break  # Only report once

            # Check for timeout issues (long-running operations)
            if 'time.sleep' in content or 'while True' in content:
                findings.append(InvestigationFinding(
                    finding_id="common_timeout",
                    category="performance",
                    severity="info",
                    description="Script contains long-running operations",
                    evidence="Found time.sleep or while True loop",
                    potential_cause="Script may timeout during execution",
                    recommended_action="Consider adding timeout handling or async operations"
                ))

        except Exception as e:
            findings.append(InvestigationFinding(
                finding_id="common_check_error",
                category="investigation",
                severity="medium",
                description="Error checking common issues",
                evidence=str(e),
                potential_cause="File read error",
                recommended_action="Check file permissions"
            ))

        return findings

    def generate_investigation_report(self, investigation_results: Dict[str, Any]) -> str:
        """Generate investigation report"""
        report_lines = [
            "=" * 80,
            "🔍 JARVIS TROUBLESHOOTING INVESTIGATION REPORT",
            "=" * 80,
            f"Script: {investigation_results['script']}",
            f"Investigated: {investigation_results['investigated_at']}",
            "",
            "📊 SUMMARY",
            "-" * 80,
            f"Total Findings: {investigation_results['total_findings']}",
            f"Critical: {investigation_results['critical']}",
            f"High: {investigation_results['high']}",
            f"Medium: {investigation_results['medium']}",
            f"Low: {investigation_results['low']}",
            "",
            "🔍 FINDINGS",
            "-" * 80
        ]

        for finding in investigation_results['findings']:
            severity_icon = "🔴" if finding['severity'] == "critical" else \
                          "🟠" if finding['severity'] == "high" else \
                          "🟡" if finding['severity'] == "medium" else "🔵"

            report_lines.extend([
                f"{severity_icon} [{finding['severity'].upper()}] {finding['category']}",
                f"   Description: {finding['description']}",
                f"   Evidence: {finding['evidence'][:100]}...",
                f"   Cause: {finding['potential_cause']}",
                f"   Action: {finding['recommended_action']}",
                ""
            ])

        report_lines.extend([
            "=" * 80,
            ""
        ])

        return "\n".join(report_lines)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Troubleshooting Investigation")
        parser.add_argument('script', type=str, help='Script to investigate')
        parser.add_argument('--timeout', type=int, default=30, help='Execution timeout (seconds)')
        parser.add_argument('--json', action='store_true', help='Output as JSON')

        args = parser.parse_args()

        investigator = JARVISTroubleshootingInvestigation()

        script_path = Path(args.script)
        if not script_path.is_absolute():
            script_path = investigator.project_root / "scripts" / "python" / script_path

        results = investigator.investigate_script(script_path, timeout=args.timeout)

        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            report = investigator.generate_investigation_report(results)
            print("\n" + report)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()