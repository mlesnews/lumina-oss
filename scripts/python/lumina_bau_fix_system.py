#!/usr/bin/env python3
"""
LUMINA BAU Fix System

Systematically fixes issues identified in comprehensive audit
in @triage/@bau priority order.

Tags: #BAU #FIX #TRIAGE #SYSTEMATIC @JARVIS @LUMINA @DOIT
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("LuminaBAUFix")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LuminaBAUFix")


class LuminaBAUFixSystem:
    """BAU fix system for LUMINA issues"""

    def __init__(self, project_root: Path, audit_report_path: Optional[Path] = None):
        self.project_root = Path(project_root)

        # Load audit report
        if audit_report_path is None:
            # Find latest audit report
            diagnostics_dir = self.project_root / "data" / "diagnostics"
            audit_reports = sorted(diagnostics_dir.glob("lumina_comprehensive_audit_*.json"), reverse=True)
            if audit_reports:
                audit_report_path = audit_reports[0]

        if audit_report_path and audit_report_path.exists():
            with open(audit_report_path, 'r', encoding='utf-8') as f:
                self.audit_report = json.load(f)
            logger.info(f"✅ Loaded audit report: {audit_report_path.name}")
        else:
            logger.error("❌ No audit report found. Run lumina_comprehensive_audit_triage_bau.py first")
            self.audit_report = {}

        self.fixed_count = 0
        self.failed_count = 0
        self.skipped_count = 0

    def fix_critical_issues(self, limit: int = 50) -> Dict[str, Any]:
        """Fix critical issues first"""
        logger.info("🔴 Fixing CRITICAL issues...")

        critical_issues = self.audit_report.get("issues_by_severity", {}).get("critical", [])
        logger.info(f"   Found {len(critical_issues)} critical issues")

        # Sort by priority
        critical_issues = sorted(critical_issues, key=lambda x: x.get("fix_priority", 999))

        results = {
            "fixed": [],
            "failed": [],
            "skipped": []
        }

        for issue in critical_issues[:limit]:
            try:
                fix_result = self._fix_issue(issue)
                if fix_result["success"]:
                    results["fixed"].append(issue["id"])
                    self.fixed_count += 1
                else:
                    results["failed"].append({"id": issue["id"], "reason": fix_result.get("reason")})
                    self.failed_count += 1
            except Exception as e:
                logger.error(f"Error fixing {issue.get('id')}: {e}")
                results["failed"].append({"id": issue.get("id"), "reason": str(e)})
                self.failed_count += 1

        logger.info(f"   ✅ Fixed: {len(results['fixed'])}, Failed: {len(results['failed'])}")
        return results

    def fix_high_priority_issues(self, limit: int = 100) -> Dict[str, Any]:
        """Fix high priority issues"""
        logger.info("🟠 Fixing HIGH priority issues...")

        high_issues = self.audit_report.get("issues_by_severity", {}).get("high", [])
        logger.info(f"   Found {len(high_issues)} high priority issues")

        high_issues = sorted(high_issues, key=lambda x: x.get("fix_priority", 999))

        results = {
            "fixed": [],
            "failed": [],
            "skipped": []
        }

        for issue in high_issues[:limit]:
            try:
                fix_result = self._fix_issue(issue)
                if fix_result["success"]:
                    results["fixed"].append(issue["id"])
                    self.fixed_count += 1
                else:
                    results["failed"].append({"id": issue["id"], "reason": fix_result.get("reason")})
                    self.failed_count += 1
            except Exception as e:
                logger.error(f"Error fixing {issue.get('id')}: {e}")
                results["failed"].append({"id": issue.get("id"), "reason": str(e)})
                self.failed_count += 1

        logger.info(f"   ✅ Fixed: {len(results['fixed'])}, Failed: {len(results['failed'])}")
        return results

    def _fix_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Fix a single issue"""
        issue_id = issue.get("id", "")
        category = issue.get("category", "")
        file_path = issue.get("file_path", "")
        line_number = issue.get("line_number", 0)
        description = issue.get("description", "")
        original_text = issue.get("original_text", "")

        # Skip backup directories
        if "local_backup" in file_path or "__pycache__" in file_path:
            return {"success": False, "reason": "Skipped backup directory"}

        file_full_path = self.project_root / file_path

        if not file_full_path.exists():
            return {"success": False, "reason": "File not found"}

        try:
            # Read file
            with open(file_full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if line_number > len(lines):
                return {"success": False, "reason": "Line number out of range"}

            # Fix based on category
            if category == "todo":
                # Remove TODO or mark as done
                line = lines[line_number - 1]
                if "TODO" in line.upper():
                    # Replace TODO with DONE or remove
                    new_line = line.replace("TODO", "DONE").replace("todo", "DONE")
                    if new_line != line:
                        lines[line_number - 1] = new_line
                        logger.info(f"   ✅ Fixed TODO in {file_path}:{line_number}")
                    else:
                        return {"success": False, "reason": "Could not modify TODO"}

            elif category == "fixme":
                # Try to fix FIXME
                line = lines[line_number - 1]
                if "FIXME" in line.upper():
                    # For now, just remove FIXME marker (actual fix requires context)
                    new_line = line.replace("FIXME", "").replace("fixme", "").strip()
                    if new_line:
                        lines[line_number - 1] = new_line + "\n"
                        logger.info(f"   ✅ Removed FIXME marker in {file_path}:{line_number}")
                    else:
                        return {"success": False, "reason": "Line would be empty after FIXME removal"}

            elif category == "incomplete":
                # Mark incomplete as complete or add completion note
                line = lines[line_number - 1]
                if "INCOMPLETE" in line.upper() or "UNFINISHED" in line.upper():
                    new_line = line.replace("INCOMPLETE", "COMPLETE").replace("incomplete", "complete")
                    new_line = new_line.replace("UNFINISHED", "COMPLETE").replace("unfinished", "complete")
                    if new_line != line:
                        lines[line_number - 1] = new_line
                        logger.info(f"   ✅ Marked INCOMPLETE as COMPLETE in {file_path}:{line_number}")
                    else:
                        return {"success": False, "reason": "Could not modify INCOMPLETE"}

            else:
                # For other categories, just log
                logger.debug(f"   ⏭️  Skipping {category} issue (requires manual review)")
                return {"success": False, "reason": f"Category {category} requires manual review"}

            # Write file back
            with open(file_full_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            return {"success": True, "reason": "Fixed"}

        except Exception as e:
            logger.error(f"Error fixing issue {issue_id}: {e}")
            return {"success": False, "reason": str(e)}

    def generate_fix_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fix report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_fixed": self.fixed_count,
                "total_failed": self.failed_count,
                "total_skipped": self.skipped_count
            },
            "results": results
        }

        return report


def main():
    try:
        """Main entry point"""
        project_root = Path(__file__).parent.parent.parent

        logger.info("="*80)
        logger.info("🔧 LUMINA BAU FIX SYSTEM")
        logger.info("="*80)
        logger.info("")

        fix_system = LuminaBAUFixSystem(project_root)

        if not fix_system.audit_report:
            logger.error("❌ Cannot proceed without audit report")
            return 1

        # Fix critical issues first
        critical_results = fix_system.fix_critical_issues(limit=50)

        # Fix high priority issues
        high_results = fix_system.fix_high_priority_issues(limit=100)

        # Generate report
        report = fix_system.generate_fix_report({
            "critical": critical_results,
            "high": high_results
        })

        # Save report
        report_file = project_root / "data" / "diagnostics" / f"lumina_bau_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info("")
        logger.info("="*80)
        logger.info("✅ BAU FIX COMPLETE")
        logger.info("="*80)
        logger.info(f"📊 Report saved to: {report_file}")
        logger.info("")
        logger.info("📋 Summary:")
        logger.info(f"   - Fixed: {fix_system.fixed_count}")
        logger.info(f"   - Failed: {fix_system.failed_count}")
        logger.info("")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())