"""
JARVIS Proactive IDE Problem Monitor
Monitors VS Code/Cursor IDE problems and proactively addresses them.

JARVIS should be "watching the desktop" and detecting IDE problems,
not waiting for manual confirmation.

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #IDE #PROBLEMS #PROACTIVE
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class ProblemSeverity(str, Enum):
    """Problem severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class IDEProblem:
    """IDE problem/diagnostic."""
    file: str
    line: int
    column: int
    severity: ProblemSeverity
    message: str
    source: str
    code: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class JARVISProactiveIDEProblemMonitor:
    """
    Proactive IDE problem monitor for JARVIS.

    Monitors:
    - VS Code/Cursor IDE problems panel
    - Linter errors
    - Build errors
    - Code quality issues

    Actions:
    - Detects problems automatically
    - Alerts when problems accumulate
    - Auto-fixes where possible
    - Reports to JARVIS
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize proactive IDE problem monitor.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # File paths
        self.problems_file = self.project_root / "data" / "ide_problems" / "current_problems.json"
        self.history_file = self.project_root / "data" / "ide_problems" / "problem_history.jsonl"
        self.alerts_file = self.project_root / "data" / "ide_problems" / "alerts.json"

        # Ensure directories exist
        self.problems_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)

        # Thresholds
        self.error_threshold = 10  # Alert if more than 10 errors
        self.warning_threshold = 50  # Alert if more than 50 warnings
        self.total_threshold = 100  # Alert if more than 100 total problems
        self.critical_threshold = 2000  # CRITICAL if more than 2000 problems

        # Monitoring state
        self.last_check = None
        self.check_interval = 60  # Check every 60 seconds
        self.problems: List[IDEProblem] = []

    def read_ide_problems(self) -> List[IDEProblem]:
        """
        Read IDE problems from Cursor/VS Code.

        This integrates with:
        - VS Code API (if running as extension)
        - Cursor API
        - File system (if problems are cached)
        - Linter output
        - read_lints tool (via external call)

        Returns:
            List of IDE problems
        """
        problems = []

        # Method 1: Try to read from Cursor workspace state
        cursor_workspace = self.project_root / ".cursor" / "workspace"
        if cursor_workspace.exists():
            # Look for diagnostics/problems cache
            diagnostics_file = cursor_workspace / "diagnostics.json"
            if diagnostics_file.exists():
                try:
                    with open(diagnostics_file, encoding='utf-8') as f:
                        diagnostics = json.load(f)
                        problems.extend(self._parse_diagnostics(diagnostics))
                except Exception as e:
                    logger.debug(f"Could not read diagnostics: {e}")

        # Method 2: Read from exported problems file (if manually exported)
        exported_problems_file = self.project_root / "data" / "ide_problems" / "exported_problems.json"
        if exported_problems_file.exists():
            try:
                with open(exported_problems_file, encoding='utf-8') as f:
                    exported_data = json.load(f)
                    if isinstance(exported_data, list):
                        problems.extend(self._parse_exported_problems(exported_data))
                    elif isinstance(exported_data, dict) and 'problems' in exported_data:
                        problems.extend(self._parse_exported_problems(exported_data['problems']))
            except Exception as e:
                logger.debug(f"Could not read exported problems: {e}")

        # Method 3: Read from linter output files
        linter_outputs = [
            self.project_root / ".pylint-output.json",
            self.project_root / ".mypy-output.json",
            self.project_root / ".flake8-output.json"
        ]

        for linter_file in linter_outputs:
            if linter_file.exists():
                try:
                    with open(linter_file, encoding='utf-8') as f:
                        linter_data = json.load(f)
                        problems.extend(self._parse_linter_output(linter_data, linter_file.stem))
                except Exception as e:
                    logger.debug(f"Could not read {linter_file}: {e}")

        # Method 4: Try to read from current_problems.json (if updated by external tool)
        current_problems_file = self.project_root / "data" / "ide_problems" / "current_problems.json"
        if current_problems_file.exists():
            try:
                with open(current_problems_file, encoding='utf-8') as f:
                    current_data = json.load(f)
                    if isinstance(current_data, dict) and 'problems' in current_data:
                        # Check if timestamp is recent (within last hour)
                        timestamp_str = current_data.get('timestamp', '')
                        if timestamp_str:
                            try:
                                from datetime import datetime, timedelta
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                if datetime.now() - timestamp.replace(tzinfo=None) < timedelta(hours=1):
                                    problems.extend(self._parse_exported_problems(current_data['problems']))
                            except Exception:
                                pass  # Use anyway if timestamp parsing fails
            except Exception as e:
                logger.debug(f"Could not read current problems: {e}")

        # Note: read_lints tool is available via AI assistant interface
        # This method should be called externally and results saved to exported_problems.json

        return problems

    def _parse_exported_problems(self, problems_data: List[Dict[str, Any]]) -> List[IDEProblem]:
        """Parse exported problems from IDE Problems panel."""
        problems = []

        for item in problems_data:
            try:
                problem = IDEProblem(
                    file=item.get('file', item.get('path', 'unknown')),
                    line=item.get('line', item.get('lineNumber', 0)),
                    column=item.get('column', item.get('columnNumber', 0)),
                    severity=self._map_severity(item.get('severity', item.get('level', 'warning'))),
                    message=item.get('message', item.get('text', '')),
                    source=item.get('source', item.get('provider', 'unknown')),
                    code=item.get('code', item.get('errorCode'))
                )
                problems.append(problem)
            except Exception as e:
                logger.debug(f"Could not parse exported problem: {e}")

        return problems

    def _parse_diagnostics(self, diagnostics: Dict[str, Any]) -> List[IDEProblem]:
        """Parse VS Code diagnostics format."""
        problems = []

        if isinstance(diagnostics, dict):
            for file_path, file_diagnostics in diagnostics.items():
                if isinstance(file_diagnostics, list):
                    for diag in file_diagnostics:
                        try:
                            problem = IDEProblem(
                                file=file_path,
                                line=diag.get('range', {}).get('start', {}).get('line', 0) + 1,
                                column=diag.get('range', {}).get('start', {}).get('character', 0) + 1,
                                severity=ProblemSeverity(diag.get('severity', 1)),  # 1=error, 2=warning, etc.
                                message=diag.get('message', ''),
                                source=diag.get('source', 'unknown'),
                                code=diag.get('code')
                            )
                            problems.append(problem)
                        except Exception as e:
                            logger.debug(f"Could not parse diagnostic: {e}")

        return problems

    def _parse_linter_output(self, linter_data: Any, linter_name: str) -> List[IDEProblem]:
        """Parse linter output format."""
        problems = []

        # Generic linter output parser
        if isinstance(linter_data, list):
            for item in linter_data:
                try:
                    problem = IDEProblem(
                        file=item.get('file', item.get('path', 'unknown')),
                        line=item.get('line', item.get('line_number', 0)),
                        column=item.get('column', item.get('column_number', 0)),
                        severity=self._map_severity(item.get('severity', item.get('type', 'warning'))),
                        message=item.get('message', item.get('text', '')),
                        source=linter_name,
                        code=item.get('code', item.get('message_id'))
                    )
                    problems.append(problem)
                except Exception as e:
                    logger.debug(f"Could not parse linter item: {e}")

        return problems

    def _map_severity(self, severity: Any) -> ProblemSeverity:
        """Map severity string/number to ProblemSeverity."""
        if isinstance(severity, int):
            severity_map = {1: ProblemSeverity.ERROR, 2: ProblemSeverity.WARNING,
                          3: ProblemSeverity.INFO, 4: ProblemSeverity.HINT}
            return severity_map.get(severity, ProblemSeverity.WARNING)

        severity_str = str(severity).lower()
        if 'error' in severity_str:
            return ProblemSeverity.ERROR
        elif 'warning' in severity_str:
            return ProblemSeverity.WARNING
        elif 'info' in severity_str:
            return ProblemSeverity.INFO
        else:
            return ProblemSeverity.HINT

    def check_problems(self) -> Dict[str, Any]:
        """
        Check for IDE problems and return status.

        Returns:
            Dictionary with problem status
        """
        self.problems = self.read_ide_problems()
        self.last_check = datetime.now()

        # Count by severity
        errors = [p for p in self.problems if p.severity == ProblemSeverity.ERROR]
        warnings = [p for p in self.problems if p.severity == ProblemSeverity.WARNING]
        infos = [p for p in self.problems if p.severity == ProblemSeverity.INFO]
        hints = [p for p in self.problems if p.severity == ProblemSeverity.HINT]

        total = len(self.problems)

        # Save current problems
        self._save_problems()

        # Log to history
        self._log_to_history()

        # Check thresholds and alert
        alerts = self._check_thresholds(errors, warnings, total)

        status = {
            'timestamp': self.last_check.isoformat(),
            'total': total,
            'errors': len(errors),
            'warnings': len(warnings),
            'infos': len(infos),
            'hints': len(hints),
            'alerts': alerts,
            'critical': total >= self.critical_threshold
        }

        return status

    def _check_thresholds(self, errors: List[IDEProblem],
                         warnings: List[IDEProblem],
                         total: int) -> List[Dict[str, Any]]:
        """
        Check thresholds and generate alerts.

        Args:
            errors: List of error problems
            warnings: List of warning problems
            total: Total problem count

        Returns:
            List of alerts
        """
        alerts = []

        if len(errors) >= self.error_threshold:
            alerts.append({
                'type': 'error_threshold',
                'severity': 'high',
                'message': f"⚠️  {len(errors)} errors detected (threshold: {self.error_threshold})",
                'count': len(errors),
                'threshold': self.error_threshold
            })

        if len(warnings) >= self.warning_threshold:
            alerts.append({
                'type': 'warning_threshold',
                'severity': 'medium',
                'message': f"⚠️  {len(warnings)} warnings detected (threshold: {self.warning_threshold})",
                'count': len(warnings),
                'threshold': self.warning_threshold
            })

        if total >= self.critical_threshold:
            alerts.append({
                'type': 'critical_threshold',
                'severity': 'critical',
                'message': f"🚨 CRITICAL: {total} problems detected! (threshold: {self.critical_threshold})",
                'count': total,
                'threshold': self.critical_threshold
            })
        elif total >= self.total_threshold:
            alerts.append({
                'type': 'total_threshold',
                'severity': 'medium',
                'message': f"⚠️  {total} total problems detected (threshold: {self.total_threshold})",
                'count': total,
                'threshold': self.total_threshold
            })

        # Save alerts
        if alerts:
            self._save_alerts(alerts)

        return alerts

    def _save_problems(self) -> None:
        """Save current problems to file."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'total': len(self.problems),
                'problems': [p.to_dict() for p in self.problems]
            }
            with open(self.problems_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save problems: {e}", exc_info=True)

    def _log_to_history(self) -> None:
        """Log problem check to history."""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'total': len(self.problems),
                'errors': len([p for p in self.problems if p.severity == ProblemSeverity.ERROR]),
                'warnings': len([p for p in self.problems if p.severity == ProblemSeverity.WARNING])
            }
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(status) + '\n')
        except Exception as e:
            logger.error(f"Failed to log to history: {e}", exc_info=True)

    def _save_alerts(self, alerts: List[Dict[str, Any]]) -> None:
        """Save alerts to file."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'alerts': alerts
            }
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}", exc_info=True)

    def get_status_report(self) -> str:
        """
        Get human-readable status report.

        Returns:
            Formatted status report
        """
        status = self.check_problems()

        lines = []
        lines.append("📊 **JARVIS IDE Problem Monitor Status**")
        lines.append("")
        lines.append(f"**Last Check:** {status['timestamp']}")
        lines.append("")
        lines.append(f"**Total Problems:** {status['total']}")
        lines.append(f"  - Errors: {status['errors']}")
        lines.append(f"  - Warnings: {status['warnings']}")
        lines.append(f"  - Infos: {status['infos']}")
        lines.append(f"  - Hints: {status['hints']}")
        lines.append("")

        if status['critical']:
            lines.append("🚨 **CRITICAL: Over 2000 problems detected!**")
            lines.append("")

        if status['alerts']:
            lines.append("**⚠️  Alerts:**")
            for alert in status['alerts']:
                lines.append(f"  - {alert['message']}")
            lines.append("")
        else:
            lines.append("✅ **No alerts - problems within thresholds**")

        return "\n".join(lines)

    def start_monitoring(self, interval: Optional[int] = None) -> None:
        """
        Start continuous monitoring.

        Args:
            interval: Check interval in seconds (default: self.check_interval)
        """
        if interval:
            self.check_interval = interval

        logger.info(f"Starting proactive IDE problem monitoring (interval: {self.check_interval}s)")

        while True:
            try:
                status = self.check_problems()

                if status['alerts']:
                    for alert in status['alerts']:
                        logger.warning(alert['message'])

                if status['critical']:
                    logger.critical(f"CRITICAL: {status['total']} problems detected!")

                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(self.check_interval)


def main():
    """CLI interface for IDE problem monitor."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Proactive IDE Problem Monitor")
    parser.add_argument('--check', action='store_true', help='Check problems once')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--interval', type=int, help='Monitoring interval in seconds')
    parser.add_argument('--status', action='store_true', help='Show status report')

    args = parser.parse_args()

    monitor = JARVISProactiveIDEProblemMonitor()

    if args.status or not any([args.check, args.monitor]):
        print(monitor.get_status_report())

    if args.check:
        status = monitor.check_problems()
        print(f"\n✅ Checked: {status['total']} problems found")
        if status['alerts']:
            for alert in status['alerts']:
                print(f"  {alert['message']}")

    if args.monitor:
        monitor.start_monitoring(args.interval)


if __name__ == "__main__":


    main()