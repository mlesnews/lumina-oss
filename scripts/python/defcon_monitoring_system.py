#!/usr/bin/env python3
"""
DEFCON Monitoring System

Monitors system alerts, problems, and WOPR status to determine DEFCON level.
Provides visual and audible alerts through the DEFCON streetlight widget.

DEFCON Levels:
- DEFCON 5: Normal operations (Blue)
- DEFCON 4: Normal operations, minor issues (Green)
- DEFCON 3: Elevated alert, some problems (Yellow)
- DEFCON 2: High alert, significant problems (Orange)
- DEFCON 1: Critical alert, system problems (Red)

Tags: #DEFCON #ALERT #MONITORING #WOPR #STREETLIGHT @JARVIS @LUMINA
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DEFCONMonitor")


class DEFCONLevel(Enum):
    """DEFCON alert levels"""
    PEACEFUL = 5  # Normal operations
    NORMAL = 4    # Normal operations, minor issues
    ELEVATED = 3  # Elevated alert, some problems
    HIGH = 2      # High alert, significant problems
    CRITICAL = 1  # Critical alert, system problems


class DEFCONMonitoringSystem:
    """
    DEFCON Monitoring System

    Monitors:
    - WOPR status
    - System alerts
    - VA health issues
    - Critical errors
    - Network problems
    - Security issues
    """

    def __init__(self):
        """Initialize DEFCON monitoring system"""
        self.project_root = project_root
        self.data_dir = project_root / "data" / "defcon_monitoring"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.current_level = DEFCONLevel.PEACEFUL
        self.alerts: List[Dict[str, Any]] = []
        self.problems: List[Dict[str, Any]] = []
        self.wopr_status: Optional[Dict[str, Any]] = None

        logger.info("=" * 80)
        logger.info("🚦 DEFCON MONITORING SYSTEM")
        logger.info("=" * 80)

    def check_wopr_status(self) -> Dict[str, Any]:
        """Check WOPR system status"""
        try:
            # Check for WOPR-related files or status
            wopr_data_dir = self.project_root / "data" / "wopr"
            if wopr_data_dir.exists():
                status_files = list(wopr_data_dir.glob("*status*.json"))
                if status_files:
                    with open(status_files[-1], 'r', encoding='utf-8') as f:
                        wopr_status = json.load(f)
                        self.wopr_status = wopr_status
                        return wopr_status
        except Exception as e:
            logger.warning(f"Could not check WOPR status: {e}")

        return {"status": "unknown", "last_check": datetime.now().isoformat()}

    def check_system_alerts(self) -> List[Dict[str, Any]]:
        """Check for system alerts and problems"""
        alerts = []
        problems = []

        try:
            # Check for error logs
            error_logs = self.project_root / "data" / "logs"
            if error_logs.exists():
                error_files = list(error_logs.glob("*error*.log")) + list(error_logs.glob("*error*.jsonl"))
                if error_files:
                    # Check recent errors
                    for error_file in error_files[-5:]:  # Check last 5 error files
                        try:
                            if error_file.suffix == ".jsonl":
                                with open(error_file, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                    if lines:
                                        last_line = lines[-1]
                                        try:
                                            error_data = json.loads(last_line)
                                            if error_data.get("level") in ["ERROR", "CRITICAL"]:
                                                alerts.append({
                                                    "type": "error",
                                                    "source": error_file.name,
                                                    "message": error_data.get("message", "Unknown error"),
                                                    "timestamp": error_data.get("timestamp", datetime.now().isoformat()),
                                                    "severity": error_data.get("level", "ERROR")
                                                })
                                        except json.JSONDecodeError:
                                            pass
                        except Exception as e:
                            logger.debug(f"Could not read error file {error_file}: {e}")

            # Check for security alerts
            security_logs = self.project_root / "data" / "lumina_gmail" / "security_logs"
            if security_logs.exists():
                security_files = list(security_logs.glob("*.jsonl"))
                if security_files:
                    try:
                        with open(security_files[-1], 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            recent_security_issues = [
                                json.loads(line) for line in lines[-10:]
                                if "alert" in line.lower() or "threat" in line.lower() or "unauthorized" in line.lower()
                            ]
                            if recent_security_issues:
                                alerts.append({
                                    "type": "security",
                                    "source": "security_logs",
                                    "message": f"{len(recent_security_issues)} recent security events",
                                    "timestamp": datetime.now().isoformat(),
                                    "severity": "HIGH"
                                })
                    except Exception as e:
                        logger.debug(f"Could not read security logs: {e}")

            # Check for VA health issues
            va_health_dir = self.project_root / "data" / "va_health"
            if va_health_dir.exists():
                health_files = list(va_health_dir.glob("*.json"))
                if health_files:
                    try:
                        with open(health_files[-1], 'r', encoding='utf-8') as f:
                            health_data = json.load(f)
                            unhealthy_vas = [
                                va for va in health_data.get("vas", {}).values()
                                if va.get("status") not in ["healthy", "normal"]
                            ]
                            if unhealthy_vas:
                                problems.append({
                                    "type": "va_health",
                                    "source": "va_health_monitoring",
                                    "message": f"{len(unhealthy_vas)} VAs with health issues",
                                    "timestamp": datetime.now().isoformat(),
                                    "severity": "MEDIUM"
                                })
                    except Exception as e:
                        logger.debug(f"Could not read VA health data: {e}")

        except Exception as e:
            logger.warning(f"Error checking system alerts: {e}")

        self.alerts = alerts
        self.problems = problems
        return alerts + problems

    def calculate_defcon_level(self) -> DEFCONLevel:
        """Calculate current DEFCON level based on alerts and problems"""
        # Check WOPR status
        wopr_status = self.check_wopr_status()

        # Check system alerts
        all_issues = self.check_system_alerts()

        # Count critical issues
        critical_alerts = [a for a in self.alerts if a.get("severity") == "CRITICAL"]
        high_alerts = [a for a in self.alerts if a.get("severity") == "HIGH"]
        medium_problems = [p for p in self.problems if p.get("severity") == "MEDIUM"]

        # Determine DEFCON level
        if critical_alerts:
            return DEFCONLevel.CRITICAL  # DEFCON 1
        elif high_alerts or len(all_issues) > 5:
            return DEFCONLevel.HIGH  # DEFCON 2
        elif medium_problems or len(all_issues) > 2:
            return DEFCONLevel.ELEVATED  # DEFCON 3
        elif all_issues:
            return DEFCONLevel.NORMAL  # DEFCON 4
        else:
            return DEFCONLevel.PEACEFUL  # DEFCON 5

    def get_current_status(self) -> Dict[str, Any]:
        """Get current DEFCON status"""
        self.current_level = self.calculate_defcon_level()

        return {
            "defcon_level": self.current_level.value,
            "defcon_name": self.current_level.name,
            "alerts": self.alerts,
            "problems": self.problems,
            "wopr_status": self.wopr_status,
            "total_issues": len(self.alerts) + len(self.problems),
            "timestamp": datetime.now().isoformat()
        }

    def get_alert_sound(self) -> Optional[str]:
        """Get sound file path for current DEFCON level"""
        # Return sound file path based on DEFCON level
        sound_map = {
            DEFCONLevel.CRITICAL: "defcon1_alert.wav",  # Critical alert sound
            DEFCONLevel.HIGH: "defcon2_alert.wav",      # High alert sound
            DEFCONLevel.ELEVATED: "defcon3_alert.wav",  # Elevated alert sound
        }
        return sound_map.get(self.current_level)


def main():
    """Main entry point for testing"""
    monitor = DEFCONMonitoringSystem()

    print("=" * 80)
    print("🚦 DEFCON MONITORING SYSTEM TEST")
    print("=" * 80)
    print()

    status = monitor.get_current_status()

    print(f"Current DEFCON Level: {status['defcon_level']} ({status['defcon_name']})")
    print(f"Total Issues: {status['total_issues']}")
    print(f"Alerts: {len(status['alerts'])}")
    print(f"Problems: {len(status['problems'])}")
    print()

    if status['alerts']:
        print("Alerts:")
        for alert in status['alerts']:
            print(f"  • {alert['type']}: {alert['message']} ({alert['severity']})")
        print()

    if status['problems']:
        print("Problems:")
        for problem in status['problems']:
            print(f"  • {problem['type']}: {problem['message']} ({problem['severity']})")
        print()

    print("=" * 80)


if __name__ == "__main__":


    main()