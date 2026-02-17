#!/usr/bin/env python3
"""
JARVIS Reboot Advisor

Monitors system health and advises when a reboot is needed.
Proactive system maintenance recommendations.

Tags: #REBOOT #ADVISOR #SYSTEM_HEALTH #MAINTENANCE @JARVIS @LUMINA
"""

import sys
import json
import platform
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISRebootAdvisor")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISRebootAdvisor")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISRebootAdvisor")


class RebootAdvisor:
    """Advise when reboot is needed"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "reboot_advisor"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.advisor_file = self.data_dir / "reboot_advisories.jsonl"
        self.last_reboot_file = self.data_dir / "last_reboot.json"
        self.advisory_status_file = self.data_dir / "advisory_status.json"

        self.reboot_indicators = {
            "uptime_days": 7,  # Recommend reboot after 7 days
            "memory_pressure": 0.85,  # 85% memory usage
            "cpu_stress": 0.90,  # 90% CPU usage sustained
            "system_errors": 10,  # Multiple system errors
            "pending_updates": True,  # Pending system updates
            "performance_degradation": True  # Performance issues
        }

    def check_reboot_needed(self) -> Dict[str, Any]:
        """Check if reboot is needed and provide advisory"""
        advisory = {
            "advisory_id": f"advisory_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "reboot_recommended": False,
            "urgency": "none",  # none, low, medium, high, critical
            "reasons": [],
            "system_metrics": {},
            "recommendation": None
        }

        # Check system uptime
        uptime_info = self._get_uptime()
        advisory["system_metrics"]["uptime_days"] = uptime_info.get("days", 0)

        if uptime_info.get("days", 0) >= self.reboot_indicators["uptime_days"]:
            advisory["reboot_recommended"] = True
            advisory["urgency"] = "medium"
            advisory["reasons"].append({
                "reason": "System uptime exceeds recommended threshold",
                "details": f"System has been up for {uptime_info.get('days', 0)} days",
                "threshold": self.reboot_indicators["uptime_days"]
            })

        # Check memory pressure
        memory_info = self._get_memory_info()
        advisory["system_metrics"]["memory_usage_percent"] = memory_info.get("percent", 0)

        if memory_info.get("percent", 0) >= (self.reboot_indicators["memory_pressure"] * 100):
            advisory["reboot_recommended"] = True
            if advisory["urgency"] == "none":
                advisory["urgency"] = "high"
            advisory["reasons"].append({
                "reason": "High memory pressure",
                "details": f"Memory usage at {memory_info.get('percent', 0):.1f}%",
                "threshold": f"{self.reboot_indicators['memory_pressure'] * 100}%"
            })

        # Check CPU stress
        cpu_info = self._get_cpu_info()
        advisory["system_metrics"]["cpu_usage_percent"] = cpu_info.get("percent", 0)

        if cpu_info.get("percent", 0) >= (self.reboot_indicators["cpu_stress"] * 100):
            advisory["reboot_recommended"] = True
            if advisory["urgency"] in ["none", "low", "medium"]:
                advisory["urgency"] = "high"
            advisory["reasons"].append({
                "reason": "High CPU stress",
                "details": f"CPU usage at {cpu_info.get('percent', 0):.1f}%",
                "threshold": f"{self.reboot_indicators['cpu_stress'] * 100}%"
            })

        # Check for system errors (if accessible)
        system_errors = self._check_system_errors()
        if system_errors:
            advisory["system_metrics"]["system_errors"] = system_errors
            if system_errors.get("count", 0) >= self.reboot_indicators["system_errors"]:
                advisory["reboot_recommended"] = True
                if advisory["urgency"] in ["none", "low"]:
                    advisory["urgency"] = "medium"
                advisory["reasons"].append({
                    "reason": "Multiple system errors detected",
                    "details": f"{system_errors.get('count', 0)} system errors",
                    "threshold": self.reboot_indicators["system_errors"]
                })

        # Generate recommendation
        if advisory["reboot_recommended"]:
            advisory["recommendation"] = self._generate_recommendation(advisory)
        else:
            advisory["recommendation"] = "No reboot needed at this time. System is healthy."

        # Save advisory
        try:
            with open(self.advisor_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(advisory) + '\n')

            # Update advisory status
            self._update_advisory_status(advisory)
        except Exception as e:
            logger.error(f"Error saving advisory: {e}")

        logger.info("=" * 80)
        logger.info("🔄 REBOOT ADVISORY")
        logger.info("=" * 80)
        logger.info(f"Reboot recommended: {advisory['reboot_recommended']}")
        logger.info(f"Urgency: {advisory['urgency']}")
        logger.info(f"Reasons: {len(advisory['reasons'])}")
        if advisory['reboot_recommended']:
            logger.info(f"Recommendation: {advisory['recommendation']}")
        logger.info("=" * 80)

        return advisory

    def _get_uptime(self) -> Dict[str, Any]:
        """Get system uptime"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            return {
                "days": uptime.days,
                "hours": uptime.seconds // 3600,
                "minutes": (uptime.seconds % 3600) // 60,
                "boot_time": boot_time.isoformat()
            }
        except Exception as e:
            logger.debug(f"Error getting uptime: {e}")
            return {"days": 0}

    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            return {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
                "free": memory.free
            }
        except Exception as e:
            logger.debug(f"Error getting memory info: {e}")
            return {"percent": 0}

    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            return {
                "percent": cpu_percent,
                "count": cpu_count,
                "load": cpu_percent / 100.0
            }
        except Exception as e:
            logger.debug(f"Error getting CPU info: {e}")
            return {"percent": 0}

    def _check_system_errors(self) -> Optional[Dict[str, Any]]:
        """Check for system errors (platform-specific)"""
        # This is a placeholder - actual implementation would check system logs
        # Windows: Event Viewer, Linux: syslog, etc.
        return None

    def _generate_recommendation(self, advisory: Dict[str, Any]) -> str:
        """Generate reboot recommendation"""
        urgency = advisory.get("urgency", "none")
        reasons_count = len(advisory.get("reasons", []))

        if urgency == "critical":
            return f"CRITICAL: Immediate reboot recommended. {reasons_count} critical issue(s) detected."
        elif urgency == "high":
            return f"HIGH: Reboot recommended soon. {reasons_count} issue(s) requiring attention."
        elif urgency == "medium":
            return f"MEDIUM: Reboot recommended when convenient. {reasons_count} issue(s) detected."
        else:
            return f"LOW: Consider rebooting. {reasons_count} minor issue(s) detected."

    def _update_advisory_status(self, advisory: Dict[str, Any]):
        """Update advisory status"""
        status = {
            "last_check": advisory["timestamp"],
            "reboot_recommended": advisory["reboot_recommended"],
            "urgency": advisory["urgency"],
            "reasons_count": len(advisory.get("reasons", [])),
            "system_metrics": advisory.get("system_metrics", {})
        }

        try:
            with open(self.advisory_status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error updating advisory status: {e}")

    def get_advisory_status(self) -> Dict[str, Any]:
        """Get current advisory status"""
        if self.advisory_status_file.exists():
            try:
                with open(self.advisory_status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "status": "no_advisory_available",
            "message": "Run --check to get reboot advisory"
        }

    def record_reboot(self) -> Dict[str, Any]:
        """Record that a reboot was performed"""
        reboot_record = {
            "reboot_id": f"reboot_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "recorded_by": "JARVIS Reboot Advisor",
            "system": platform.system(),
            "platform": platform.platform()
        }

        try:
            with open(self.last_reboot_file, 'w', encoding='utf-8') as f:
                json.dump(reboot_record, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error recording reboot: {e}")

        logger.info(f"✅ Reboot recorded: {reboot_record['reboot_id']}")

        return reboot_record


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Reboot Advisor")
        parser.add_argument("--check", action="store_true", help="Check if reboot is needed")
        parser.add_argument("--status", action="store_true", help="Get advisory status")
        parser.add_argument("--record-reboot", action="store_true", help="Record that reboot was performed")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        advisor = RebootAdvisor(project_root)

        if args.check:
            advisory = advisor.check_reboot_needed()
            print("=" * 80)
            print("🔄 REBOOT ADVISORY")
            print("=" * 80)
            print(f"\nReboot recommended: {advisory['reboot_recommended']}")
            print(f"Urgency: {advisory['urgency'].upper()}")
            print(f"\nReasons ({len(advisory['reasons'])}):")
            for reason in advisory['reasons']:
                print(f"  - {reason['reason']}: {reason['details']}")
            print(f"\nRecommendation: {advisory['recommendation']}")
            print("=" * 80)
            print(json.dumps(advisory, indent=2, default=str))

        elif args.status:
            status = advisor.get_advisory_status()
            print("=" * 80)
            print("🔄 REBOOT ADVISORY STATUS")
            print("=" * 80)
            if status.get("reboot_recommended"):
                print(f"\n⚠️  REBOOT RECOMMENDED")
                print(f"Urgency: {status.get('urgency', 'unknown').upper()}")
                print(f"Reasons: {status.get('reasons_count', 0)}")
            else:
                print("\n✅ No reboot needed")
            print("=" * 80)
            print(json.dumps(status, indent=2, default=str))

        elif args.record_reboot:
            record = advisor.record_reboot()
            print(f"✅ Reboot recorded: {record['reboot_id']}")
            print(json.dumps(record, indent=2, default=str))

        else:
            # Default: check reboot status
            advisory = advisor.check_reboot_needed()
            print("=" * 80)
            print("🔄 REBOOT ADVISORY")
            print("=" * 80)
            if advisory['reboot_recommended']:
                print(f"\n⚠️  REBOOT RECOMMENDED")
                print(f"Urgency: {advisory['urgency'].upper()}")
                print(f"\nReasons:")
                for reason in advisory['reasons']:
                    print(f"  - {reason['reason']}")
                print(f"\n{advisory['recommendation']}")
            else:
                print("\n✅ No reboot needed at this time")
                print("System is healthy")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()