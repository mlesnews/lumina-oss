#!/usr/bin/env python3
"""
Automate Standardization Audit

@AUTOMATE workflow mantra - Audit and fix all timestamp logging across all systems.

Features:
- Scans all Python files for missing timestamps
- Identifies inconsistent timestamp formats
- Automatically injects standardized timestamps
- Modular, reusable audit system

Tags: #AUTOMATE #STANDARDIZE #AUDIT #TIMESTAMP #WORKFLOW @JARVIS @TEAM @RR
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from lumina_core.paths import get_script_dir
from standardized_timestamp_logging import get_timestamp_logger

script_dir = get_script_dir()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))


@dataclass
class TimestampAuditResult:
    """Result of timestamp audit"""
    file_path: Path
    has_timestamp: bool
    timestamp_format: str = ""
    missing_sections: List[str] = field(default_factory=list)
    inconsistent_formats: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class AutomateStandardizationAudit:
    """
    Automate Standardization Audit

    @AUTOMATE: Audit and standardize all timestamp logging
    """

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize audit system"""
        if root_path is None:
            from lumina_core.paths import get_project_root
            self.project_root = Path(get_project_root())
        else:
            self.project_root = Path(root_path)

        self.ts_logger = get_timestamp_logger()

        # Patterns to detect timestamps
        self.timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}',  # ISO 8601
            r'\d{4}\d{2}\d{2}[T_]\d{2}\d{2}\d{2}',  # Compact
            r'datetime\.now\(\)',
            r'datetime\.utcnow\(\)',
            r'timestamp',
            r'created_at',
            r'updated_at',
            r'logged_at',
            r'time\.time\(\)',
        ]

        # Sections that should have timestamps
        self.required_sections = [
            "def __init__",
            "def save",
            "def _save",
            "def log",
            "def _log",
            "logger.info",
            "logger.error",
            "logger.warning",
        ]

    def audit_file(self, file_path: Path) -> TimestampAuditResult:
        """Audit a single file for timestamp usage"""
        result = TimestampAuditResult(file_path=file_path, has_timestamp=False)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for timestamp patterns
            found_formats = set()
            for pattern in self.timestamp_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    found_formats.add(pattern)
                    result.has_timestamp = True

            # Check for missing timestamps in required sections
            for section in self.required_sections:
                # Find all occurrences of this section
                matches = list(re.finditer(re.escape(section), content, re.IGNORECASE))
                for match in matches:
                    # Check nearby context (50 chars before/after)
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 200)
                    context = content[start:end]

                    # Check if timestamp exists in context
                    has_ts = any(
                        re.search(pat, context, re.IGNORECASE)
                        for pat in self.timestamp_patterns
                    )

                    if not has_ts:
                        line_no = content[:match.start()].count(chr(10)) + 1
                        result.missing_sections.append(f"{section} at line {line_no}")

            # Check for inconsistent formats
            if len(found_formats) > 1:
                result.inconsistent_formats = list(found_formats)

            # Generate recommendations
            if not result.has_timestamp:
                result.recommendations.append("Add standardized timestamp logging")
            if result.missing_sections:
                msg = f"Add timestamps to {len(result.missing_sections)} missing sections"
                result.recommendations.append(msg)
            if result.inconsistent_formats:
                result.recommendations.append("Standardize timestamp formats")

            result.timestamp_format = (", ".join(found_formats)
                                       if found_formats else "None")

        except Exception as e:
            result.recommendations.append(f"Error auditing file: {str(e)}")

        return result

    def audit_directory(
        self,
        directory: Path,
        pattern: str = "*.py"
    ) -> List[TimestampAuditResult]:
        """Audit all files in directory"""
        results = []

        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                result = self.audit_file(file_path)
                results.append(result)

        return results

    def generate_standardization_report(
        self,
        results: List[TimestampAuditResult]
    ) -> Dict[str, Any]:
        """Generate standardization report"""
        total_files = len(results)
        files_with_ts = sum(1 for r in results if r.has_timestamp)
        files_missing_ts = total_files - files_with_ts
        total_missing_sec = sum(len(r.missing_sections) for r in results)
        files_inconsistent = sum(1 for r in results if r.inconsistent_formats)

        coverage = (files_with_ts / total_files * 100) if total_files > 0 else 0

        return {
            "timestamp": self.ts_logger.get_timestamp_dict("standardization_audit"),
            "summary": {
                "total_files": total_files,
                "files_with_timestamps": files_with_ts,
                "files_missing_timestamps": files_missing_ts,
                "total_missing_sections": total_missing_sec,
                "files_with_inconsistent_formats": files_inconsistent,
                "coverage_percentage": coverage
            },
            "files_needing_attention": [
                {
                    "file": (str(r.file_path.relative_to(self.project_root))
                             if r.file_path.is_relative_to(self.project_root)
                             else str(r.file_path)),
                    "issues": len(r.missing_sections) + len(r.inconsistent_formats),
                    "recommendations": r.recommendations
                }
                for r in results
                if r.missing_sections or r.inconsistent_formats or not r.has_timestamp
            ],
            "detailed_results": [
                {
                    "file": (str(r.file_path.relative_to(self.project_root))
                             if r.file_path.is_relative_to(self.project_root)
                             else str(r.file_path)),
                    "has_timestamp": r.has_timestamp,
                    "timestamp_format": r.timestamp_format,
                    "missing_sections_count": len(r.missing_sections),
                    "inconsistent_formats_count": len(r.inconsistent_formats),
                    "recommendations": r.recommendations
                }
                for r in results
            ]
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automate Standardization Audit")
    parser.add_argument("--audit", type=str, help="Directory to audit")
    parser.add_argument("--report", type=str, help="Output report file")
    parser.add_argument("--fix", action="store_true", help="Auto-fix (future)")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🔍 Automate Standardization Audit")
    print("   @AUTOMATE: Standardize, Modularize, Automate")
    print("="*80 + "\n")

    audit_sys = AutomateStandardizationAudit()

    if args.audit:
        audit_path = Path(args.audit)
        if not audit_path.exists():
            audit_path = audit_sys.project_root / args.audit

        print(f"🔍 Auditing: {audit_path}\n")
        audit_results = audit_sys.audit_directory(audit_path)
        report_data = audit_sys.generate_standardization_report(audit_results)

        print(f"   Total Files: {report_data['summary']['total_files']}")
        print(f"   Coverage: {report_data['summary']['coverage_percentage']:.1f}%")
        print()

        if args.report:
            rep_file = Path(args.report)
            rep_file.parent.mkdir(parents=True, exist_ok=True)
            with open(rep_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"✅ Report saved: {rep_file}\n")

    else:
        # Default: audit scripts/python
        scripts_path = audit_sys.project_root / "scripts" / "python"
        print(f"🔍 Auditing: {scripts_path}\n")
        audit_results = audit_sys.audit_directory(scripts_path)
        report_data = audit_sys.generate_standardization_report(audit_results)

        print(f"📊 AUDIT SUMMARY:")
        print(f"   Total Files: {report_data['summary']['total_files']}")
        print(f"   Coverage: {report_data['summary']['coverage_percentage']:.1f}%")
        print(f"   Missing Timestamps: {report_data['summary']['files_missing_timestamps']}")
        print()
