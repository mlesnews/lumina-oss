#!/usr/bin/env python3
"""
JARVIS Ecosystem-Wide Logging System

Comprehensive logging, tailing, and validation across the entire LUMINA ecosystem.
Logs everything, everywhere, all the time.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Iterator
from datetime import datetime
import logging
import threading
import queue
import time
from collections import deque

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEcosystemLogging")


class EcosystemLogTailer:
    """
    Tails logs from all ecosystem components in real-time
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.log_dirs = self._discover_log_directories()
        self.active_tails = {}
        self.log_queue = queue.Queue()
        self.running = False

    def _discover_log_directories(self) -> List[Path]:
        try:
            """Discover all log directories in the ecosystem"""
            log_dirs = []

            # Standard log locations
            standard_dirs = [
                self.project_root / "data" / "logs",
                self.project_root / "data" / "workflow_logs",
                self.project_root / "data" / "delegation_logs",
                self.project_root / "data" / "doit_logs",
                self.project_root / "data" / "continuous_logs",
                self.project_root / "data" / "health_reports",
                self.project_root / "data" / "jarvis_marvin_roasts",
                self.project_root / "data" / "lumina_analysis",
                self.project_root / "data" / "action_plans",
                self.project_root / "reports",
            ]

            # Find all directories with "log" in name
            for dir_path in self.project_root.rglob("*"):
                if dir_path.is_dir() and ("log" in dir_path.name.lower() or "report" in dir_path.name.lower()):
                    if dir_path not in log_dirs:
                        log_dirs.append(dir_path)

            # Add standard dirs
            for dir_path in standard_dirs:
                if dir_path.exists() and dir_path not in log_dirs:
                    log_dirs.append(dir_path)

            return log_dirs

        except Exception as e:
            self.logger.error(f"Error in _discover_log_directories: {e}", exc_info=True)
            raise
    def tail_log_file(self, log_file: Path) -> Iterator[str]:
        """Tail a single log file"""
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Go to end of file
                f.seek(0, 2)

                while self.running:
                    line = f.readline()
                    if line:
                        yield line.strip()
                    else:
                        time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error tailing {log_file}: {e}")

    def start_tailing_all(self):
        try:
            """Start tailing all log files in ecosystem"""
            self.running = True

            # Find all log files
            log_files = []
            for log_dir in self.log_dirs:
                if log_dir.exists():
                    for log_file in log_dir.glob("*.json"):
                        log_files.append(log_file)
                    for log_file in log_dir.glob("*.log"):
                        log_files.append(log_file)
                    for log_file in log_dir.glob("*.txt"):
                        if "log" in log_file.name.lower() or "status" in log_file.name.lower():
                            log_files.append(log_file)

            # Start tailing each file in separate thread
            for log_file in log_files:
                thread = threading.Thread(
                    target=self._tail_file_thread,
                    args=(log_file,),
                    daemon=True
                )
                thread.start()
                self.active_tails[log_file] = thread

        except Exception as e:
            self.logger.error(f"Error in start_tailing_all: {e}", exc_info=True)
            raise
    def _tail_file_thread(self, log_file: Path):
        """Thread function to tail a log file"""
        try:
            for line in self.tail_log_file(log_file):
                self.log_queue.put({
                    'file': str(log_file),
                    'line': line,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"Error in tail thread for {log_file}: {e}")

    def get_recent_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries"""
        logs = []
        while not self.log_queue.empty() and len(logs) < count:
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        return logs

    def stop_tailing(self):
        """Stop all tailing operations"""
        self.running = False


class EcosystemLogValidator:
    """
    Validates and verifies logs across the ecosystem
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for different log types"""
        return {
            'workflow_logs': {
                'required_fields': ['started_at'],  # More flexible - accept started_at or timestamp
                'valid_statuses': ['success', 'failed', 'skipped'],
                'optional_fields': ['timestamp', 'total_steps', 'executed', 'summary']
            },
            'health_reports': {
                'required_fields': ['timestamp', 'overall_health', 'health_score'],
                'valid_health': ['excellent', 'healthy', 'degraded', 'poor', 'critical']
            },
            'delegation_logs': {
                'required_fields': ['timestamp', 'task', 'subagent', 'result'],
                'valid_results': ['success', 'failed']
            }
        }

    def validate_log_file(self, log_file: Path) -> Dict[str, Any]:
        """Validate a single log file"""
        validation_result = {
            'file': str(log_file),
            'valid': False,
            'errors': [],
            'warnings': []
        }

        try:
            if log_file.suffix == '.json':
                with open(log_file, 'r') as f:
                    data = json.load(f)

                # Determine log type
                log_type = self._determine_log_type(log_file)

                if log_type and log_type in self.validation_rules:
                    rules = self.validation_rules[log_type]

                    # Check required fields
                    for field in rules.get('required_fields', []):
                        if field not in data:
                            validation_result['errors'].append(f"Missing required field: {field}")

                    # Validate status/health values
                    if 'valid_statuses' in rules:
                        status = data.get('status') or data.get('result', {}).get('success')
                        if status and status not in rules['valid_statuses']:
                            validation_result['warnings'].append(f"Invalid status: {status}")

                    if 'valid_health' in rules:
                        health = data.get('overall_health') or data.get('health')
                        if health and health not in rules['valid_health']:
                            validation_result['warnings'].append(f"Invalid health: {health}")

                validation_result['valid'] = len(validation_result['errors']) == 0
            else:
                # Text log file - basic validation
                validation_result['valid'] = True
                validation_result['warnings'].append("Text log - limited validation")

        except json.JSONDecodeError as e:
            validation_result['errors'].append(f"Invalid JSON: {e}")
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {e}")

        return validation_result

    def _determine_log_type(self, log_file: Path) -> Optional[str]:
        """Determine log type from file path/name"""
        path_str = str(log_file).lower()

        if 'workflow' in path_str:
            return 'workflow_logs'
        elif 'health' in path_str:
            return 'health_reports'
        elif 'delegation' in path_str:
            return 'delegation_logs'
        elif 'doit' in path_str:
            return 'workflow_logs'
        elif 'continuous' in path_str:
            return 'workflow_logs'

        return None

    def validate_all_logs(self) -> Dict[str, Any]:
        try:
            """Validate all logs in ecosystem"""
            validation_report = {
                'timestamp': datetime.now().isoformat(),
                'total_files': 0,
                'valid_files': 0,
                'invalid_files': 0,
                'results': []
            }

            # Find all log files
            log_files = []
            log_dirs = [
                self.project_root / "data" / "workflow_logs",
                self.project_root / "data" / "health_reports",
                self.project_root / "data" / "delegation_logs",
                self.project_root / "data" / "doit_logs",
                self.project_root / "data" / "continuous_logs",
            ]

            for log_dir in log_dirs:
                if log_dir.exists():
                    log_files.extend(log_dir.glob("*.json"))

            validation_report['total_files'] = len(log_files)

            for log_file in log_files:
                result = self.validate_log_file(log_file)
                validation_report['results'].append(result)

                if result['valid']:
                    validation_report['valid_files'] += 1
                else:
                    validation_report['invalid_files'] += 1

            return validation_report


        except Exception as e:
            self.logger.error(f"Error in validate_all_logs: {e}", exc_info=True)
            raise
class JARVISEcosystemLogging:
    """
    Ecosystem-wide logging, tailing, and validation system
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Initialize components
        self.tailer = EcosystemLogTailer(project_root)
        self.validator = EcosystemLogValidator(project_root)

        # Centralized log directory
        self.central_log_dir = project_root / "data" / "ecosystem_logs"
        self.central_log_dir.mkdir(parents=True, exist_ok=True)

        # Log aggregation
        self.aggregated_logs = deque(maxlen=10000)  # Keep last 10k entries

    def start_ecosystem_logging(self):
        """Start ecosystem-wide logging and tailing"""
        self.logger.info("="*80)
        self.logger.info("STARTING ECOSYSTEM-WIDE LOGGING")
        self.logger.info("="*80)

        # Start tailing all logs
        self.tailer.start_tailing_all()

        self.logger.info(f"✅ Tailing {len(self.tailer.active_tails)} log files")
        self.logger.info(f"✅ Monitoring {len(self.tailer.log_dirs)} log directories")

    def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get current ecosystem logging status"""
        recent_logs = self.tailer.get_recent_logs(100)

        return {
            'timestamp': datetime.now().isoformat(),
            'active_tails': len(self.tailer.active_tails),
            'log_directories': len(self.tailer.log_dirs),
            'recent_logs': len(recent_logs),
            'tailer_running': self.tailer.running,
            'log_dirs': [str(d) for d in self.tailer.log_dirs]
        }

    def validate_ecosystem(self) -> Dict[str, Any]:
        """Validate all logs in ecosystem"""
        self.logger.info("Validating ecosystem logs...")
        validation_report = self.validator.validate_all_logs()

        # Save validation report
        report_file = self.central_log_dir / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(validation_report, f, indent=2)
            self.logger.info(f"✅ Validation report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save validation report: {e}")

        return validation_report

    def tail_live_logs(self, duration: int = 10) -> List[Dict[str, Any]]:
        """Tail live logs for specified duration"""
        self.logger.info(f"Tailing live logs for {duration} seconds...")

        if not self.tailer.running:
            self.tailer.start_tailing_all()

        logs = []
        start_time = time.time()

        while time.time() - start_time < duration:
            recent = self.tailer.get_recent_logs(50)
            logs.extend(recent)
            time.sleep(0.5)

        return logs

    def generate_ecosystem_report(self) -> Dict[str, Any]:
        """Generate comprehensive ecosystem report"""
        status = self.get_ecosystem_status()
        validation = self.validate_ecosystem()

        report = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'validation': validation,
            'summary': {
                'log_directories': status['log_directories'],
                'active_tails': status['active_tails'],
                'total_log_files': validation['total_files'],
                'valid_log_files': validation['valid_files'],
                'invalid_log_files': validation['invalid_files']
            }
        }

        # Save report
        report_file = self.central_log_dir / f"ecosystem_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"✅ Ecosystem report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save ecosystem report: {e}")

        return report


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Ecosystem Logging")
        parser.add_argument("--start", action="store_true", help="Start ecosystem logging")
        parser.add_argument("--status", action="store_true", help="Get ecosystem status")
        parser.add_argument("--validate", action="store_true", help="Validate all logs")
        parser.add_argument("--tail", type=int, help="Tail live logs for N seconds")
        parser.add_argument("--report", action="store_true", help="Generate ecosystem report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        ecosystem = JARVISEcosystemLogging(project_root)

        if args.start:
            ecosystem.start_ecosystem_logging()
            print("\n✅ Ecosystem-wide logging started")
            print("   Monitoring all log directories...")
            print("   Tailing all log files...")

        elif args.status:
            status = ecosystem.get_ecosystem_status()
            print("\n" + "="*80)
            print("ECOSYSTEM LOGGING STATUS")
            print("="*80)
            print(f"Active Tails: {status['active_tails']}")
            print(f"Log Directories: {status['log_directories']}")
            print(f"Recent Logs: {status['recent_logs']}")
            print(f"Tailer Running: {status['tailer_running']}")
            print(f"\nLog Directories:")
            for log_dir in status['log_dirs'][:10]:
                print(f"  - {log_dir}")

        elif args.validate:
            validation = ecosystem.validate_ecosystem()
            print("\n" + "="*80)
            print("ECOSYSTEM VALIDATION")
            print("="*80)
            print(f"Total Files: {validation['total_files']}")
            print(f"Valid Files: {validation['valid_files']}")
            print(f"Invalid Files: {validation['invalid_files']}")

            if validation['invalid_files'] > 0:
                print(f"\n⚠️  Invalid Files:")
                for result in validation['results']:
                    if not result['valid']:
                        print(f"  - {result['file']}")
                        for error in result['errors']:
                            print(f"    Error: {error}")

        elif args.tail:
            logs = ecosystem.tail_live_logs(args.tail)
            print(f"\n✅ Captured {len(logs)} log entries")
            for log in logs[:10]:
                print(f"  [{log['timestamp']}] {log['file']}: {log['line'][:100]}")

        elif args.report:
            report = ecosystem.generate_ecosystem_report()
            print("\n" + "="*80)
            print("ECOSYSTEM REPORT")
            print("="*80)
            summary = report['summary']
            print(f"Log Directories: {summary['log_directories']}")
            print(f"Active Tails: {summary['active_tails']}")
            print(f"Total Log Files: {summary['total_log_files']}")
            print(f"Valid Log Files: {summary['valid_log_files']}")
            print(f"Invalid Log Files: {summary['invalid_log_files']}")
            print(f"\n📄 Full report saved to ecosystem_logs/")
        else:
            print("Usage:")
            print("  python jarvis_ecosystem_logging.py --start      # Start logging")
            print("  python jarvis_ecosystem_logging.py --status     # Get status")
            print("  python jarvis_ecosystem_logging.py --validate   # Validate logs")
            print("  python jarvis_ecosystem_logging.py --tail 10    # Tail for 10s")
            print("  python jarvis_ecosystem_logging.py --report     # Generate report")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()