#!/usr/bin/env python3
"""
JARVIS Compound Log Health Monitor

Live running compound log with parsing and tailing for health checks.
Integrated into overall systems and application health checks.
BAU (Business As Usual) policy template.

Tags: #COMPOUND_LOG #HEALTH_CHECKS #LIVE_MONITORING #BAU #TAILING @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import subprocess
import re

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISCompoundLogHealthMonitor")


class CompoundLogTailer:
    """Tail compound log files for real-time monitoring"""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.position = 0
        self.running = False
        self.tail_thread = None
        self.lines = deque(maxlen=1000)  # Keep last 1000 lines

    def start_tailing(self, callback=None):
        """Start tailing the log file"""
        if not self.log_file.exists():
            logger.warning(f"Log file does not exist: {self.log_file}")
            return

        self.running = True
        self.position = self.log_file.stat().st_size  # Start from end

        def tail_loop():
            while self.running:
                try:
                    with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(self.position)
                        new_lines = f.readlines()

                        if new_lines:
                            for line in new_lines:
                                line = line.strip()
                                if line:
                                    self.lines.append({
                                        "timestamp": datetime.now().isoformat(),
                                        "line": line
                                    })

                                    if callback:
                                        callback(line)

                            self.position = f.tell()

                    time.sleep(0.5)  # Check every 0.5 seconds
                except Exception as e:
                    logger.error(f"Error tailing log: {str(e)}")
                    time.sleep(1)

        self.tail_thread = threading.Thread(target=tail_loop, daemon=True)
        self.tail_thread.start()
        logger.info(f"✅ Started tailing: {self.log_file}")

    def stop_tailing(self):
        """Stop tailing the log file"""
        self.running = False
        if self.tail_thread:
            self.tail_thread.join(timeout=2)
        logger.info("⏹️  Stopped tailing log")

    def get_recent_lines(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent lines from log"""
        return list(self.lines)[-count:]


class LogParser:
    """Parse compound log for health check information"""

    def __init__(self):
        self.health_patterns = {
            "error": re.compile(r'(?i)(error|exception|failed|failure|critical)'),
            "warning": re.compile(r'(?i)(warning|warn|caution|alert)'),
            "success": re.compile(r'(?i)(success|complete|done|finished|ok|✅)'),
            "processing": re.compile(r'(?i)(processing|running|executing|working)'),
            "batch": re.compile(r'(?i)(batch|batch\s+\d+)'),
            "rate": re.compile(r'(?i)(rate|asks/min|per\s+minute)'),
            "eta": re.compile(r'(?i)(eta|estimated|remaining|completion)'),
            "progress": re.compile(r'(?i)(progress|complete|percent|%)')
        }

    def parse_line(self, line: str) -> Dict[str, Any]:
        """Parse a log line for health indicators"""
        parsed = {
            "line": line,
            "timestamp": datetime.now().isoformat(),
            "health_indicators": [],
            "severity": "INFO"
        }

        # Check for health indicators
        for indicator, pattern in self.health_patterns.items():
            if pattern.search(line):
                parsed["health_indicators"].append(indicator)

                if indicator == "error":
                    parsed["severity"] = "ERROR"
                elif indicator == "warning" and parsed["severity"] != "ERROR":
                    parsed["severity"] = "WARNING"

        return parsed

    def extract_metrics(self, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract metrics from log lines"""
        metrics = {
            "total_lines": len(lines),
            "errors": 0,
            "warnings": 0,
            "successes": 0,
            "processing": 0,
            "batches": [],
            "rates": [],
            "etas": [],
            "progress": []
        }

        for line_data in lines:
            line = line_data.get("line", "")
            parsed = self.parse_line(line)

            if "error" in parsed["health_indicators"]:
                metrics["errors"] += 1
            if "warning" in parsed["health_indicators"]:
                metrics["warnings"] += 1
            if "success" in parsed["health_indicators"]:
                metrics["successes"] += 1
            if "processing" in parsed["health_indicators"]:
                metrics["processing"] += 1

            # Extract batch numbers
            batch_match = re.search(r'batch\s+(\d+)', line, re.IGNORECASE)
            if batch_match:
                metrics["batches"].append(int(batch_match.group(1)))

            # Extract rates
            rate_match = re.search(r'(\d+\.?\d*)\s*asks/min', line, re.IGNORECASE)
            if rate_match:
                metrics["rates"].append(float(rate_match.group(1)))

            # Extract ETAs
            eta_match = re.search(r'eta[:\s]+([^,\n]+)', line, re.IGNORECASE)
            if eta_match:
                metrics["etas"].append(eta_match.group(1).strip())

            # Extract progress
            progress_match = re.search(r'(\d+\.?\d*)%', line)
            if progress_match:
                metrics["progress"].append(float(progress_match.group(1)))

        # Calculate averages
        if metrics["rates"]:
            metrics["avg_rate"] = sum(metrics["rates"]) / len(metrics["rates"])
        else:
            metrics["avg_rate"] = 0

        if metrics["progress"]:
            metrics["avg_progress"] = sum(metrics["progress"]) / len(metrics["progress"])
        else:
            metrics["avg_progress"] = 0

        return metrics


class CompoundLogHealthMonitor:
    """Compound log health monitor with tailing"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "compound_log_health"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Compound log file
        self.compound_log = self.data_dir / "compound.log"
        self.compound_log.touch()  # Create if doesn't exist

        self.tailer = CompoundLogTailer(self.compound_log)
        self.parser = LogParser()
        self.monitoring = False

        # Health metrics history
        self.health_history = deque(maxlen=100)  # Last 100 health checks

    def start_monitoring(self):
        """Start monitoring compound log"""
        def log_callback(line: str):
            """Callback for new log lines"""
            parsed = self.parser.parse_line(line)

            # Check for critical issues
            if parsed["severity"] == "ERROR":
                logger.error(f"❌ ERROR detected: {line}")
            elif parsed["severity"] == "WARNING":
                logger.warning(f"⚠️  WARNING detected: {line}")

        self.tailer.start_tailing(callback=log_callback)
        self.monitoring = True
        logger.info("✅ Compound log health monitoring started")

    def stop_monitoring(self):
        """Stop monitoring compound log"""
        self.tailer.stop_tailing()
        self.monitoring = False
        logger.info("⏹️  Compound log health monitoring stopped")

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status from compound log"""
        recent_lines = self.tailer.get_recent_lines(100)
        metrics = self.parser.extract_metrics(recent_lines)

        # Determine overall health
        health_status = "HEALTHY"
        if metrics["errors"] > 0:
            health_status = "UNHEALTHY"
        elif metrics["warnings"] > 5:
            health_status = "DEGRADED"
        elif metrics["warnings"] > 0:
            health_status = "WARNING"

        health_data = {
            "timestamp": datetime.now().isoformat(),
            "health_status": health_status,
            "metrics": metrics,
            "recent_lines": recent_lines[-10:]  # Last 10 lines
        }

        # Add to history
        self.health_history.append(health_data)

        return health_data

    def write_to_compound_log(self, message: str, source: str = "SYSTEM"):
        try:
            """Write message to compound log"""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{source}] {message}\n"

            with open(self.compound_log, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            logger.debug(f"Written to compound log: {message}")


        except Exception as e:
            self.logger.error(f"Error in write_to_compound_log: {e}", exc_info=True)
            raise
class SystemHealthChecker:
    """Overall systems and application health checker"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "system_health"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.compound_monitor = CompoundLogHealthMonitor(project_root)
        self.health_checks = []

    def register_health_check(self, name: str, check_func):
        """Register a health check function"""
        self.health_checks.append({
            "name": name,
            "check_func": check_func,
            "last_check": None,
            "last_status": None
        })

    def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "HEALTHY",
            "checks": []
        }

        for check in self.health_checks:
            try:
                status = check["check_func"]()
                check["last_check"] = datetime.now().isoformat()
                check["last_status"] = status

                results["checks"].append({
                    "name": check["name"],
                    "status": status.get("status", "UNKNOWN"),
                    "details": status
                })

                # Update overall health
                if status.get("status") == "UNHEALTHY":
                    results["overall_health"] = "UNHEALTHY"
                elif status.get("status") == "DEGRADED" and results["overall_health"] == "HEALTHY":
                    results["overall_health"] = "DEGRADED"

                # Write to compound log
                self.compound_monitor.write_to_compound_log(
                    f"Health check: {check['name']} - {status.get('status', 'UNKNOWN')}",
                    "HEALTH_CHECK"
                )
            except Exception as e:
                logger.error(f"Error running health check {check['name']}: {str(e)}")
                results["checks"].append({
                    "name": check["name"],
                    "status": "ERROR",
                    "error": str(e)
                })
                results["overall_health"] = "UNHEALTHY"

        # Save health check results
        health_file = self.data_dir / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(health_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        return results

    def start_continuous_health_checks(self, interval: int = 60):
        """Start continuous health checks"""
        def health_check_loop():
            while True:
                try:
                    results = self.run_health_checks()
                    logger.info(f"Health check complete: {results['overall_health']}")
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error in health check loop: {str(e)}")
                    time.sleep(interval)

        thread = threading.Thread(target=health_check_loop, daemon=True)
        thread.start()
        logger.info(f"✅ Continuous health checks started (interval: {interval}s)")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Compound Log Health Monitor")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--health", action="store_true", help="Run health checks")
    parser.add_argument("--continuous", action="store_true", help="Start continuous health checks")
    parser.add_argument("--status", action="store_true", help="Get health status")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    health_checker = SystemHealthChecker(project_root)

    if args.start:
        health_checker.compound_monitor.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            health_checker.compound_monitor.stop_monitoring()
    elif args.health:
        results = health_checker.run_health_checks()
        print(json.dumps(results, indent=2, default=str))
    elif args.continuous:
        health_checker.compound_monitor.start_monitoring()
        health_checker.start_continuous_health_checks()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            health_checker.compound_monitor.stop_monitoring()
    elif args.status:
        health_checker.compound_monitor.start_monitoring()
        status = health_checker.compound_monitor.get_health_status()
        print(json.dumps(status, indent=2, default=str))
        health_checker.compound_monitor.stop_monitoring()
    else:
        # Default: show status
        health_checker.compound_monitor.start_monitoring()
        time.sleep(2)  # Wait for some log entries
        status = health_checker.compound_monitor.get_health_status()
        print(json.dumps(status, indent=2, default=str))
        health_checker.compound_monitor.stop_monitoring()


if __name__ == "__main__":


    main()