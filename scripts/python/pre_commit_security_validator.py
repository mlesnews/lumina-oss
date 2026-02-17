#!/usr/bin/env python3
"""
Pre-Commit Security Validator

Validates commits for security issues before they are committed.
Checks for private data patterns, secrets, and ensures .gitignore compliance.

Tags: #SECURITY #PRE_COMMIT #VALIDATION @MARVIN @JARVIS @LUMINA
"""

import sys
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("PreCommitSecurityValidator")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("PreCommitSecurityValidator")


class PreCommitSecurityValidator:
    """
    Pre-commit security validator

    Checks:
    - Private data patterns (passwords, secrets, keys, tokens)
    - .gitignore compliance
    - File size limits
    - Sensitive file extensions
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Private data patterns
        self.private_patterns = {
            "password": r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?[^\s'\"]+",
            "secret": r"(?i)(secret|secret_key|api_secret)\s*[:=]\s*['\"]?[^\s'\"]+",
            "api_key": r"(?i)(api_key|apikey|api-key)\s*[:=]\s*['\"]?[^\s'\"]+",
            "token": r"(?i)(token|access_token|bearer_token)\s*[:=]\s*['\"]?[^\s'\"]+",
            "credential": r"(?i)(credential|credentials|cred)\s*[:=]\s*['\"]?[^\s'\"]+",
            "private_key": r"(?i)(private_key|privatekey|rsa_key)\s*[:=]\s*['\"]?[^\s'\"]+",
            "aws_key": r"(?i)(aws_access_key|aws_secret_key)\s*[:=]\s*['\"]?[^\s'\"]+",
            "database_url": r"(?i)(database_url|db_url|connection_string)\s*[:=]\s*['\"]?[^\s'\"]+"
        }

        # Sensitive file patterns
        self.sensitive_files = [
            r".*\.key$",
            r".*\.pem$",
            r".*\.p12$",
            r".*\.pfx$",
            r".*\.env$",
            r".*\.secret$",
            r".*credentials.*\.json$",
            r".*secrets.*\.json$"
        ]

        # File size limit (10MB)
        self.max_file_size = 10 * 1024 * 1024

        logger.info("🔒 Pre-Commit Security Validator initialized")

    def get_staged_files(self) -> List[str]:
        """Get list of staged files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                return files
            return []
        except Exception as e:
            logger.warning(f"Error getting staged files: {e}")
            return []

    def check_file_size(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Check if file exceeds size limit"""
        try:
            size = file_path.stat().st_size
            if size > self.max_file_size:
                return {
                    "issue": "file_too_large",
                    "file": str(file_path),
                    "size": size,
                    "limit": self.max_file_size,
                    "severity": "medium"
                }
        except Exception:
            pass
        return None

    def check_sensitive_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Check if file matches sensitive file patterns"""
        file_str = str(file_path)
        for pattern in self.sensitive_files:
            if re.match(pattern, file_str, re.IGNORECASE):
                return {
                    "issue": "sensitive_file",
                    "file": str(file_path),
                    "pattern": pattern,
                    "severity": "high"
                }
        return None

    def check_private_data(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check file for private data patterns"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    for pattern_name, pattern in self.private_patterns.items():
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            # Skip if it's a comment or example
                            if any(skip in line.lower() for skip in ['example', 'sample', 'placeholder', 'xxx', 'todo']):
                                continue

                            issues.append({
                                "issue": "private_data_pattern",
                                "file": str(file_path),
                                "line": line_num,
                                "pattern": pattern_name,
                                "match": match.group()[:50],  # First 50 chars
                                "severity": "high"
                            })
        except Exception as e:
            logger.warning(f"Error checking {file_path}: {e}")

        return issues

    def check_gitignore(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Check if file should be in .gitignore"""
        gitignore_path = self.project_root / ".gitignore"

        if not gitignore_path.exists():
            return None

        try:
            # Check if file matches any .gitignore pattern
            result = subprocess.run(
                ["git", "check-ignore", "-v", str(file_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            # If git check-ignore returns something, file is ignored (good)
            # But if it's staged, it shouldn't be ignored
            if result.returncode == 0:
                return {
                    "issue": "should_be_ignored",
                    "file": str(file_path),
                    "gitignore_match": result.stdout.strip(),
                    "severity": "medium"
                }
        except Exception:
            pass

        return None

    def validate_commit(self) -> Dict[str, Any]:
        try:
            """Validate staged files for commit"""
            logger.info("🔒 Validating staged files for security issues...")
            logger.info("")

            staged_files = self.get_staged_files()

            if not staged_files:
                logger.info("   ✅ No files staged for commit")
                return {
                    "valid": True,
                    "issues": [],
                    "files_checked": 0
                }

            logger.info(f"   📋 Checking {len(staged_files)} staged files...")

            all_issues = []

            for file_str in staged_files:
                file_path = self.project_root / file_str

                if not file_path.exists():
                    continue

                # Check file size
                size_issue = self.check_file_size(file_path)
                if size_issue:
                    all_issues.append(size_issue)
                    logger.warning(f"   ⚠️  {file_str}: File too large ({size_issue['size']} bytes)")

                # Check sensitive file patterns
                sensitive_issue = self.check_sensitive_file(file_path)
                if sensitive_issue:
                    all_issues.append(sensitive_issue)
                    logger.warning(f"   ⚠️  {file_str}: Sensitive file pattern detected")

                # Check private data patterns (only for text files)
                if file_path.suffix in ['.py', '.js', '.ts', '.json', '.md', '.txt', '.yaml', '.yml', '.env', '.config']:
                    private_issues = self.check_private_data(file_path)
                    if private_issues:
                        all_issues.extend(private_issues)
                        for issue in private_issues:
                            logger.warning(f"   ⚠️  {file_str}:{issue['line']}: Private data pattern '{issue['pattern']}' detected")

                # Check .gitignore
                gitignore_issue = self.check_gitignore(file_path)
                if gitignore_issue:
                    all_issues.append(gitignore_issue)
                    logger.warning(f"   ⚠️  {file_str}: Should be in .gitignore")

            # Determine if commit is valid
            critical_issues = [i for i in all_issues if i.get("severity") == "high"]
            valid = len(critical_issues) == 0

            logger.info("")
            if valid:
                logger.info("   ✅ Validation passed - no critical issues found")
            else:
                logger.error(f"   ❌ Validation FAILED - {len(critical_issues)} critical issues found")
                logger.error("   Commit blocked for security reasons")

            return {
                "valid": valid,
                "issues": all_issues,
                "files_checked": len(staged_files),
                "critical_issues": len(critical_issues)
            }

        except Exception as e:
            self.logger.error(f"Error in validate_commit: {e}", exc_info=True)
            raise
    def print_report(self, result: Dict[str, Any]):
        """Print validation report"""
        print("=" * 80)
        print("🔒 PRE-COMMIT SECURITY VALIDATION")
        print("=" * 80)
        print("")
        n_checked = result["files_checked"]
        n_issues = len(result["issues"])
        n_critical = result["critical_issues"]
        print(f"Files Checked: {n_checked}")
        print(f"Issues Found: {n_issues}")
        print(f"Critical Issues: {n_critical}")
        print("")

        if result['issues']:
            print("ISSUES:")
            for issue in result['issues']:
                severity_icon = "🔴" if issue.get("severity") == "high" else "🟡"
                print(f"   {severity_icon} {issue.get('file', 'unknown')}")
                if issue.get('line'):
                    print(f"      Line {issue['line']}: {issue.get('pattern', 'unknown pattern')}")
                print(f"      {issue.get('issue', 'unknown issue')}")
                print("")

        print("=" * 80)
        status_msg = '✅ VALID - Proceed with commit' if result['valid'] else '❌ INVALID - Commit blocked'
        print(f"Status: {status_msg}")
        print("=" * 80)


def main():
    """Main execution - called by git pre-commit hook"""
    validator = PreCommitSecurityValidator()
    result = validator.validate_commit()
    validator.print_report(result)

    # Exit with error code if validation failed
    sys.exit(0 if result['valid'] else 1)


if __name__ == "__main__":

    main()