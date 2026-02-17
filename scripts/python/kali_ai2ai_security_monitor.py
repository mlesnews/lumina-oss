#!/usr/bin/env python3
"""
Kali Linux AI2AI Security Monitor
Automated security monitoring and vulnerability tracking via AI2AI integration

Tags: #security #kali #AI2AI #monitoring #automation @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("KaliAI2AISecurityMonitor")


class KaliAI2AISecurityMonitor:
    """
    AI2AI-integrated security monitor for Kali Linux containers

    Monitors:
    - Container health
    - Security vulnerabilities
    - System resource usage
    - Network activity
    - Automated remediation suggestions
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize AI2AI security monitor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "kali_security_monitoring"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.image_name = "kali-hardened-millennium-falc:latest"
        self.container_name = "kali-hardened"

        # AI2AI integration
        self.ai2ai_framework = None
        self._init_ai2ai()

        logger.info("✅ Kali AI2AI Security Monitor initialized")

    def _init_ai2ai(self):
        """Initialize AI2AI framework"""
        try:
            sys.path.insert(0, str(self.project_root / "scripts" / "python"))
            from jarvis_assistant_framework import JARVISAssistantFramework

            self.ai2ai_framework = JARVISAssistantFramework()
            logger.info("   ✅ AI2AI framework connected")
        except ImportError:
            logger.warning("   ⚠️  JARVIS AI2AI framework not available")
        except Exception as e:
            logger.debug(f"   AI2AI init error: {e}")

    def send_ai2ai_message(self, message_type: str, data: Dict[str, Any]):
        """Send message via AI2AI framework"""
        if not self.ai2ai_framework:
            return

        try:
            message = {
                "type": message_type,
                "source": "kali_security_monitor",
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            self.ai2ai_framework.send_message(message)
            logger.debug(f"   📤 AI2AI message sent: {message_type}")
        except Exception as e:
            logger.debug(f"   AI2AI message error: {e}")

    def check_container_health(self) -> Dict[str, Any]:
        """Check container health status"""
        logger.info("🔍 Checking container health...")

        health = {
            "timestamp": datetime.now().isoformat(),
            "container_running": False,
            "container_status": None,
            "resource_usage": {},
            "health_status": "unknown"
        }

        try:
            # Check if container exists and is running
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                health["container_running"] = True
                health["container_status"] = result.stdout.strip()
                logger.info(f"   ✅ Container running: {health['container_status']}")

                # Get resource usage
                try:
                    stats_result = subprocess.run(
                        ["docker", "stats", self.container_name, "--no-stream", "--format", 
                         "{{.CPUPerc}},{{.MemUsage}},{{.NetIO}}"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if stats_result.returncode == 0:
                        stats = stats_result.stdout.strip().split(",")
                        health["resource_usage"] = {
                            "cpu_percent": stats[0] if len(stats) > 0 else "N/A",
                            "memory": stats[1] if len(stats) > 1 else "N/A",
                            "network": stats[2] if len(stats) > 2 else "N/A"
                        }
                except Exception as e:
                    logger.debug(f"   Resource stats error: {e}")

                health["health_status"] = "healthy"
            else:
                logger.warning("   ⚠️  Container not running")
                health["health_status"] = "not_running"

        except Exception as e:
            logger.warning(f"   ⚠️  Container check error: {e}")
            health["health_status"] = "error"

        # Send to AI2AI
        self.send_ai2ai_message("container_health", health)

        return health

    def scan_vulnerabilities(self) -> Dict[str, Any]:
        """Scan container for vulnerabilities"""
        logger.info("🔒 Scanning for vulnerabilities...")

        scan_results = {
            "timestamp": datetime.now().isoformat(),
            "scanner": None,
            "vulnerabilities": [],
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0
        }

        # Try Trivy
        try:
            result = subprocess.run(
                ["trivy", "image", "--format", "json", self.image_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                scan_results["scanner"] = "trivy"
                scan_data = json.loads(result.stdout)

                # Parse vulnerabilities
                if "Results" in scan_data:
                    for result_item in scan_data["Results"]:
                        if "Vulnerabilities" in result_item:
                            for vuln in result_item["Vulnerabilities"]:
                                severity = vuln.get("Severity", "UNKNOWN").upper()
                                scan_results["vulnerabilities"].append({
                                    "id": vuln.get("VulnerabilityID"),
                                    "severity": severity,
                                    "package": vuln.get("PkgName"),
                                    "description": vuln.get("Title", vuln.get("Description", ""))
                                })

                                if severity == "CRITICAL":
                                    scan_results["critical_count"] += 1
                                elif severity == "HIGH":
                                    scan_results["high_count"] += 1
                                elif severity == "MEDIUM":
                                    scan_results["medium_count"] += 1
                                elif severity == "LOW":
                                    scan_results["low_count"] += 1

                logger.info(f"   ✅ Trivy scan complete: {len(scan_results['vulnerabilities'])} vulnerabilities found")
                logger.info(f"      Critical: {scan_results['critical_count']}, High: {scan_results['high_count']}")

        except FileNotFoundError:
            logger.info("   ℹ️  Trivy not installed (optional)")
        except Exception as e:
            logger.debug(f"   Trivy scan error: {e}")

        # Try Docker Scout as fallback
        if not scan_results["scanner"]:
            try:
                result = subprocess.run(
                    ["docker", "scout", "cves", self.image_name],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    scan_results["scanner"] = "docker_scout"
                    scan_results["raw_output"] = result.stdout
                    logger.info("   ✅ Docker Scout scan complete")
            except Exception as e:
                logger.debug(f"   Docker Scout scan error: {e}")

        # Send to AI2AI
        self.send_ai2ai_message("vulnerability_scan", scan_results)

        return scan_results

    def generate_security_report(self) -> Dict[str, Any]:
        try:
            """Generate comprehensive security report"""
            logger.info("=" * 80)
            logger.info("📊 GENERATING SECURITY REPORT")
            logger.info("=" * 80)
            logger.info("")

            # Gather all data
            health = self.check_container_health()
            vulnerabilities = self.scan_vulnerabilities()

            report = {
                "timestamp": datetime.now().isoformat(),
                "container_health": health,
                "vulnerabilities": vulnerabilities,
                "recommendations": [],
                "ai2ai_integrated": self.ai2ai_framework is not None
            }

            # Generate recommendations
            if vulnerabilities.get("critical_count", 0) > 0:
                report["recommendations"].append({
                    "priority": "CRITICAL",
                    "action": "Update packages with critical vulnerabilities immediately",
                    "count": vulnerabilities["critical_count"]
                })

            if vulnerabilities.get("high_count", 0) > 0:
                report["recommendations"].append({
                    "priority": "HIGH",
                    "action": "Review and update packages with high-severity vulnerabilities",
                    "count": vulnerabilities["high_count"]
                })

            if not health.get("container_running"):
                report["recommendations"].append({
                    "priority": "MEDIUM",
                    "action": "Start container or investigate why it's not running",
                    "count": 1
                })

            # Save report
            report_file = self.data_dir / f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ✅ Report saved: {report_file.name}")

            # Print summary
            print("\n" + "=" * 80)
            print("🔒 KALI SECURITY REPORT")
            print("=" * 80)
            print(f"Container Status: {health.get('health_status', 'unknown').upper()}")
            print(f"Vulnerabilities Found: {len(vulnerabilities.get('vulnerabilities', []))}")
            print(f"  Critical: {vulnerabilities.get('critical_count', 0)}")
            print(f"  High: {vulnerabilities.get('high_count', 0)}")
            print(f"  Medium: {vulnerabilities.get('medium_count', 0)}")
            print(f"  Low: {vulnerabilities.get('low_count', 0)}")
            print(f"AI2AI Integrated: {'✅ YES' if report['ai2ai_integrated'] else '❌ NO'}")
            print(f"Recommendations: {len(report['recommendations'])}")
            print("=" * 80)
            print()

            # Send to AI2AI
            self.send_ai2ai_message("security_report", report)

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_security_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Kali Linux AI2AI Security Monitor")
    parser.add_argument("--health", action="store_true", help="Check container health")
    parser.add_argument("--scan", action="store_true", help="Scan for vulnerabilities")
    parser.add_argument("--report", action="store_true", help="Generate full security report")

    args = parser.parse_args()

    monitor = KaliAI2AISecurityMonitor()

    if args.report or not any(vars(args).values()):
        # Default: full report
        monitor.generate_security_report()
    elif args.health:
        monitor.check_container_health()
    elif args.scan:
        monitor.scan_vulnerabilities()

    return 0


if __name__ == "__main__":


    sys.exit(main())