#!/usr/bin/env python3
"""
Logging/Documentation Compliance Audit

LOGGING = DOCUMENTING - They share the same principal intention.
This audit tracks our progress toward 100% standard logging compliance.

Calculates:
- Percentage of scripts using standard logging (lumina_logger)
- Outstanding logging/documentation issues
- Progress toward full compliance
- Files needing updates

Tags: #logging #documentation #compliance #audit #standard
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("LoggingComplianceAudit")


class LoggingStatus(Enum):
    """Logging compliance status"""
    COMPLIANT = "compliant"  # Uses lumina_logger correctly
    NON_COMPLIANT = "non_compliant"  # Uses fallback or basic logging
    NO_LOGGING = "no_logging"  # No logging at all
    UNKNOWN = "unknown"  # Can't determine


@dataclass
class FileAuditResult:
    """Audit result for a single file"""
    file_path: Path
    status: LoggingStatus
    has_standard_logging: bool = False
    has_fallback_logging: bool = False
    has_basic_logging: bool = False
    has_no_logging: bool = False
    issues: List[str] = field(default_factory=list)
    line_numbers: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['file_path'] = str(self.file_path)
        result['status'] = self.status.value
        return result


class LoggingComplianceAudit:
    """
    Logging/Documentation Compliance Audit System

    LOGGING = DOCUMENTING
    Tracks progress toward 100% standard logging compliance.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize compliance audit"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts" / "python"

        # Patterns for detection
        self.standard_pattern = re.compile(r'from\s+lumina_logger\s+import\s+get_logger', re.IGNORECASE)
        self.fallback_pattern = re.compile(
            r'except\s+ImportError:.*?logging\.basicConfig',
            re.DOTALL | re.IGNORECASE
        )
        self.basic_logging_pattern = re.compile(
            r'import\s+logging\s*\n\s*logging\.basicConfig',
            re.MULTILINE | re.IGNORECASE
        )
        self.get_logger_pattern = re.compile(r'get_logger\s*\(', re.IGNORECASE)

        logger.info("=" * 80)
        logger.info("📋 LOGGING/DOCUMENTATION COMPLIANCE AUDIT")
        logger.info("=" * 80)
        logger.info("   LOGGING = DOCUMENTING")
        logger.info("   Tracking progress toward 100% compliance")
        logger.info("=" * 80)
        logger.info("")

    def audit_file(self, file_path: Path) -> FileAuditResult:
        """Audit a single Python file for logging compliance"""
        result = FileAuditResult(file_path=file_path, status=LoggingStatus.UNKNOWN)

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            result.status = LoggingStatus.UNKNOWN
            result.issues.append(f"Could not read file: {e}")
            return result

        # Check for standard logging
        if self.standard_pattern.search(content):
            result.has_standard_logging = True
            result.status = LoggingStatus.COMPLIANT

            # Check if get_logger is actually used
            if self.get_logger_pattern.search(content):
                # Fully compliant
                pass
            else:
                result.status = LoggingStatus.NON_COMPLIANT
                result.issues.append("Imports lumina_logger but doesn't use get_logger()")
                result.line_numbers['import'] = self._find_line_number(content, 'from lumina_logger import')
        else:
            # Check for fallback pattern
            if self.fallback_pattern.search(content):
                result.has_fallback_logging = True
                result.status = LoggingStatus.NON_COMPLIANT
                result.issues.append("Uses fallback logging pattern (try/except with basicConfig)")
                result.line_numbers['fallback'] = self._find_line_number(content, 'except ImportError')

            # Check for basic logging
            elif self.basic_logging_pattern.search(content):
                result.has_basic_logging = True
                result.status = LoggingStatus.NON_COMPLIANT
                result.issues.append("Uses basic logging.basicConfig() directly")
                result.line_numbers['basic'] = self._find_line_number(content, 'logging.basicConfig')

            # Check if there's any logging at all
            elif 'logging' in content.lower() or 'logger' in content.lower():
                result.status = LoggingStatus.NON_COMPLIANT
                result.issues.append("Uses logging but not standard lumina_logger")
            else:
                result.has_no_logging = True
                result.status = LoggingStatus.NO_LOGGING
                result.issues.append("No logging found (may be acceptable for some scripts)")

        return result

    def _find_line_number(self, content: str, pattern: str) -> int:
        """Find line number of pattern in content"""
        try:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if pattern.lower() in line.lower():
                    return i
        except:
            pass
        return 0

    def audit_all_scripts(self) -> Dict[str, Any]:
        """Audit all Python scripts in the project"""
        logger.info("🔍 Auditing all Python scripts...")
        logger.info("")

        results: List[FileAuditResult] = []

        # Find all Python files
        python_files = list(self.scripts_dir.rglob("*.py"))

        # Exclude certain files
        exclude_patterns = ['__pycache__', '.pyc', 'test_', '_test.py']
        python_files = [
            f for f in python_files
            if not any(pattern in str(f) for pattern in exclude_patterns)
        ]

        logger.info(f"   Found {len(python_files)} Python files to audit")
        logger.info("")

        # Audit each file
        for py_file in python_files:
            result = self.audit_file(py_file)
            results.append(result)

        # Calculate statistics
        total_files = len(results)
        compliant = sum(1 for r in results if r.status == LoggingStatus.COMPLIANT)
        non_compliant = sum(1 for r in results if r.status == LoggingStatus.NON_COMPLIANT)
        no_logging = sum(1 for r in results if r.status == LoggingStatus.NO_LOGGING)
        unknown = sum(1 for r in results if r.status == LoggingStatus.UNKNOWN)

        # Calculate percentage
        if total_files > 0:
            compliance_percentage = (compliant / total_files) * 100
            outstanding_percentage = ((non_compliant + no_logging) / total_files) * 100
        else:
            compliance_percentage = 0.0
            outstanding_percentage = 0.0

        # Generate report
        report = {
            "audit_date": datetime.now().isoformat(),
            "principle": "LOGGING = DOCUMENTING",
            "summary": {
                "total_files": total_files,
                "compliant": compliant,
                "non_compliant": non_compliant,
                "no_logging": no_logging,
                "unknown": unknown,
                "compliance_percentage": round(compliance_percentage, 2),
                "outstanding_percentage": round(outstanding_percentage, 2),
                "progress_toward_100": round(compliance_percentage, 2)
            },
            "compliant_files": [
                str(r.file_path.relative_to(self.project_root))
                for r in results if r.status == LoggingStatus.COMPLIANT
            ],
            "non_compliant_files": [
                {
                    "file": str(r.file_path.relative_to(self.project_root)),
                    "issues": r.issues,
                    "line_numbers": r.line_numbers
                }
                for r in results if r.status == LoggingStatus.NON_COMPLIANT
            ],
            "no_logging_files": [
                str(r.file_path.relative_to(self.project_root))
                for r in results if r.status == LoggingStatus.NO_LOGGING
            ],
            "detailed_results": [r.to_dict() for r in results]
        }

        return report

    def print_report(self, report: Dict[str, Any]):
        """Print formatted compliance report"""
        summary = report['summary']

        print("\n" + "=" * 80)
        print("📊 LOGGING/DOCUMENTATION COMPLIANCE REPORT")
        print("=" * 80)
        print(f"   Principle: LOGGING = DOCUMENTING")
        print("")
        print(f"📈 PROGRESS TOWARD 100% COMPLIANCE")
        print(f"   Current Compliance: {summary['compliance_percentage']:.2f}%")
        print(f"   Outstanding Issues: {summary['outstanding_percentage']:.2f}%")
        print("")
        print(f"📋 BREAKDOWN")
        print(f"   Total Files: {summary['total_files']}")
        print(f"   ✅ Compliant: {summary['compliant']} ({summary['compliance_percentage']:.2f}%)")
        print(f"   ❌ Non-Compliant: {summary['non_compliant']}")
        print(f"   ⚠️  No Logging: {summary['no_logging']}")
        print(f"   ❓ Unknown: {summary['unknown']}")
        print("")

        if summary['non_compliant'] > 0:
            print("=" * 80)
            print("❌ NON-COMPLIANT FILES (Need Updates)")
            print("=" * 80)
            for file_info in report['non_compliant_files'][:20]:  # Show first 20
                print(f"\n   {file_info['file']}")
                for issue in file_info['issues']:
                    print(f"      • {issue}")
            if len(report['non_compliant_files']) > 20:
                print(f"\n   ... and {len(report['non_compliant_files']) - 20} more files")

        print("\n" + "=" * 80)
        print(f"🎯 TARGET: 100% Compliance")
        print(f"📊 CURRENT: {summary['compliance_percentage']:.2f}%")
        print(f"📉 REMAINING: {100 - summary['compliance_percentage']:.2f}%")
        print("=" * 80)
        print("")


def main():
    try:
        """Main entry point"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Logging/Documentation Compliance Audit")
        parser.add_argument('--audit', action='store_true', help='Run compliance audit')
        parser.add_argument('--save', action='store_true', help='Save report to file')
        parser.add_argument('--output', type=str, help='Output file path')

        args = parser.parse_args()

        auditor = LoggingComplianceAudit()

        if args.audit or not any(vars(args).values()):
            report = auditor.audit_all_scripts()
            auditor.print_report(report)

            if args.save or args.output:
                output_file = Path(args.output) if args.output else auditor.project_root / "data" / "logging_compliance_audit.json"
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, default=str)

                logger.info(f"💾 Report saved to: {output_file}")
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()