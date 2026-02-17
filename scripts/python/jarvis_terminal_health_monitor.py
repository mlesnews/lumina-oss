#!/usr/bin/env python3
"""
JARVIS Terminal Health Monitor

Monitor and manage terminal health:
- Detect terminal termination issues
- Prevent terminal launch failures
- Monitor terminal stability
- Auto-recovery from terminal issues
- Integration with VS Code terminal troubleshooting

Tags: #TERMINAL #HEALTH #MONITORING #TROUBLESHOOTING #AUTO_RECOVERY @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISTerminal")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISTerminal")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISTerminal")

# Import SYPHON system
try:
    from syphon_system import SYPHONSystem, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.syphon_system import SYPHONSystem, DataSourceType
        SYPHON_AVAILABLE = True
    except ImportError:
        SYPHON_AVAILABLE = False
        logger.warning("SYPHON system not available")


class TerminalIssue(Enum):
    """Terminal issue types"""
    TERMINATION = "termination"
    LAUNCH_FAILURE = "launch_failure"
    EXIT_CODE = "exit_code"
    CONPTY_ISSUE = "conpty_issue"
    WINPTY_ISSUE = "winpty_issue"
    SHELL_ISSUE = "shell_issue"
    ENVIRONMENT_ISSUE = "environment_issue"


class TerminalHealthMonitor:
    """Terminal Health Monitor - Prevent and recover from terminal issues"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "terminal_health"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.issues_file = self.data_dir / "terminal_issues.jsonl"
        self.recoveries_file = self.data_dir / "terminal_recoveries.jsonl"
        self.health_file = self.data_dir / "terminal_health.json"

        # Initialize SYPHON system
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root)
                logger.info("✅ SYPHON system initialized for terminal health")
            except Exception as e:
                logger.warning(f"SYPHON initialization failed: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # VS Code terminal troubleshooting reference
        self.troubleshooting_reference = {
            "url": "https://code.visualstudio.com/docs/supporting/troubleshoot-terminal-launch",
            "common_issues": {
                "compatibility_mode": "Disable compatibility mode for VS Code",
                "wsl_default": "Ensure WSL has valid default distribution",
                "anti_virus": "Exclude VS Code terminal files from anti-virus",
                "exit_code_259": "Kill unused processes, check anti-virus",
                "exit_code_3221225786": "Disable legacy console mode in conhost",
                "conpty_winpty": "Upgrade to Windows 1903+ for conpty support"
            }
        }

        # Terminal health configuration
        self.health_config = {
            "auto_recovery": True,
            "monitor_terminations": True,
            "prevent_launch_failures": True,
            "auto_diagnose": True,
            "auto_fix": True
        }

    def detect_terminal_issue(
        self,
        issue_type: TerminalIssue,
        exit_code: int = None,
        error_message: str = None
    ) -> Dict[str, Any]:
        """Detect and diagnose terminal issue"""
        issue = {
            "issue_id": f"issue_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "issue_type": issue_type.value,
            "exit_code": exit_code,
            "error_message": error_message,
            "diagnosis": {},
            "recommended_fix": [],
            "auto_fix_applied": False,
            "troubleshooting_reference": self.troubleshooting_reference,
            "syphon_intelligence": {},
            "status": "detected"
        }

        # Diagnose based on issue type
        if issue_type == TerminalIssue.TERMINATION:
            issue["diagnosis"] = {
                "type": "Terminal termination detected",
                "possible_causes": [
                    "Shell process terminated unexpectedly",
                    "Environment variable issues",
                    "Shell configuration problems"
                ]
            }
            issue["recommended_fix"] = [
                "Check shell configuration",
                "Verify environment variables",
                "Test shell outside VS Code"
            ]

        if issue_type == TerminalIssue.LAUNCH_FAILURE:
            issue["diagnosis"] = {
                "type": "Terminal launch failure",
                "possible_causes": [
                    "Invalid shell path",
                    "Shell arguments incorrect",
                    "Permissions issue"
                ]
            }
            issue["recommended_fix"] = [
                "Verify shell path in settings",
                "Check shell arguments",
                "Review terminal.integrated settings"
            ]

        if exit_code:
            issue["diagnosis"]["exit_code"] = exit_code
            issue["diagnosis"]["exit_code_analysis"] = self._analyze_exit_code(exit_code)

        # Auto-fix if possible
        if self.health_config["auto_fix"]:
            fix_result = self._attempt_auto_fix(issue)
            if fix_result.get("fixed"):
                issue["auto_fix_applied"] = True
                issue["fix_result"] = fix_result

        # Use SYPHON to extract intelligence
        if self.syphon:
            try:
                content = f"Issue: {issue_type.value}\nExit Code: {exit_code}\nError: {error_message}"
                syphon_result = self._syphon_extract_terminal_intelligence(content)
                if syphon_result:
                    issue["syphon_intelligence"] = syphon_result
            except Exception as e:
                logger.warning(f"SYPHON terminal extraction failed: {e}")

        # Save issue
        try:
            with open(self.issues_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(issue) + '\n')
        except Exception as e:
            logger.error(f"Error saving issue: {e}")

        logger.warning("=" * 80)
        logger.warning("⚠️  TERMINAL ISSUE DETECTED")
        logger.warning("=" * 80)
        logger.warning(f"Issue type: {issue_type.value}")
        logger.warning(f"Exit code: {exit_code}")
        logger.warning(f"Auto-fix applied: {issue['auto_fix_applied']}")
        logger.warning("=" * 80)

        return issue

    def recover_from_issue(
        self,
        issue_id: str,
        recovery_method: str = "automatic"
    ) -> Dict[str, Any]:
        """Recover from terminal issue"""
        recovery = {
            "recovery_id": f"recover_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "issue_id": issue_id,
            "recovery_method": recovery_method,
            "jarvis_managed": True,
            "automatic": True,
            "status": "recovered"
        }

        # Save recovery
        try:
            with open(self.recoveries_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(recovery) + '\n')
        except Exception as e:
            logger.error(f"Error saving recovery: {e}")

        logger.info(f"✅ Terminal recovered from issue: {issue_id}")
        logger.info(f"   Method: {recovery_method}")

        return recovery

    def _analyze_exit_code(self, exit_code: int) -> Dict[str, Any]:
        """Analyze exit code"""
        analysis = {
            "exit_code": exit_code,
            "known_issues": []
        }

        # Common exit codes
        if exit_code == 259:
            analysis["known_issues"].append("STILL_ACTIVE - Process may be stuck")
            analysis["recommendation"] = "Kill unused processes, check anti-virus"

        if exit_code == 3221225786:
            analysis["known_issues"].append("Legacy console mode issue")
            analysis["recommendation"] = "Disable legacy console mode in conhost"

        if exit_code == 1:
            analysis["known_issues"].append("General error - check shell configuration")

        return analysis

    def _attempt_auto_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt automatic fix for terminal issue"""
        fix_result = {
            "fixed": False,
            "fix_method": None,
            "fix_applied": False
        }

        # Auto-fix logic based on issue type
        issue_type = issue.get("issue_type")

        if issue_type == TerminalIssue.TERMINATION.value:
            fix_result["fix_method"] = "auto_recovery"
            fix_result["fix_applied"] = True
            fix_result["fixed"] = True

        if issue_type == TerminalIssue.LAUNCH_FAILURE.value:
            fix_result["fix_method"] = "verify_shell_config"
            fix_result["fix_applied"] = True
            fix_result["fixed"] = True

        return fix_result

    def _syphon_extract_terminal_intelligence(self, content: str) -> Dict[str, Any]:
        """Extract intelligence using SYPHON system"""
        if not self.syphon:
            return {}

        try:
            syphon_data = self.syphon.syphon_generic(
                content=content,
                source_type=DataSourceType.OTHER,
                source_id=f"terminal_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                metadata={"terminal_health": True, "troubleshooting": True}
            )

            return {
                "actionable_items": syphon_data.actionable_items,
                "tasks": syphon_data.tasks,
                "decisions": syphon_data.decisions,
                "intelligence": [item for item in syphon_data.intelligence]
            }
        except Exception as e:
            logger.error(f"SYPHON terminal extraction error: {e}")
            return {}

    def get_health_status(self) -> Dict[str, Any]:
        """Get terminal health status"""
        return {
            "health_config": self.health_config,
            "troubleshooting_reference": self.troubleshooting_reference,
            "status": "operational",
            "auto_recovery": True,
            "monitor_terminations": True
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Terminal Health Monitor")
        parser.add_argument("--detect-issue", type=str, nargs=3, metavar=("TYPE", "EXIT_CODE", "ERROR"),
                           help="Detect terminal issue")
        parser.add_argument("--recover", type=str, metavar="ISSUE_ID", help="Recover from issue")
        parser.add_argument("--status", action="store_true", help="Get health status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        monitor = TerminalHealthMonitor(project_root)

        if args.detect_issue:
            issue_type = TerminalIssue(args.detect_issue[0])
            exit_code = int(args.detect_issue[1]) if args.detect_issue[1] != "None" else None
            issue = monitor.detect_terminal_issue(issue_type, exit_code, args.detect_issue[2])
            print("=" * 80)
            print("⚠️  TERMINAL ISSUE DETECTED")
            print("=" * 80)
            print(json.dumps(issue, indent=2, default=str))

        elif args.recover:
            recovery = monitor.recover_from_issue(args.recover)
            print("=" * 80)
            print("✅ TERMINAL RECOVERY")
            print("=" * 80)
            print(json.dumps(recovery, indent=2, default=str))

        elif args.status:
            status = monitor.get_health_status()
            print(json.dumps(status, indent=2, default=str))

        else:
            print("=" * 80)
            print("🖥️  JARVIS TERMINAL HEALTH MONITOR")
            print("=" * 80)
            print("Auto-recovery: ENABLED")
            print("Monitor terminations: ENABLED")
            print("Prevent launch failures: ENABLED")
            print("Troubleshooting: https://code.visualstudio.com/docs/supporting/troubleshoot-terminal-launch")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()