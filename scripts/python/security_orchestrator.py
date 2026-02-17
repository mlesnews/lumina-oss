#!/usr/bin/env python3
"""
Security Orchestrator

Orchestrates all security components:
- Intrusion Detection System (IDS)
- Vulnerability Scanner
- Counter-Penetration System
- Threat correlation
- Automated response
- Incident management

Designed by @MARVIN, @HK-47, JARVIS, and @MANUS collaboration.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from security_ids import IntrusionDetectionSystem, IDSAlert
    from security_vulnerability_scanner import VulnerabilityScanner, Vulnerability
    from security_counter_penetration import CounterPenetrationSystem, CounterMeasure
    SECURITY_COMPONENTS_AVAILABLE = True
except ImportError:
    SECURITY_COMPONENTS_AVAILABLE = False
    IntrusionDetectionSystem = None
    VulnerabilityScanner = None
    CounterPenetrationSystem = None

logger = get_logger("SecurityOrchestrator")


class SecurityOrchestrator:
    """
    Security Orchestrator

    Coordinates all security components:
    - IDS for threat detection
    - Vulnerability Scanner for proactive assessment
    - Counter-Penetration for active defense
    - Threat correlation and analysis
    - Automated response workflows
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("SecurityOrchestrator")

        self.data_dir = self.project_root / "data" / "security"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize security components
        self.ids = None
        self.vulnerability_scanner = None
        self.counter_penetration = None

        if SECURITY_COMPONENTS_AVAILABLE:
            self.ids = IntrusionDetectionSystem(project_root=self.project_root)
            self.vulnerability_scanner = VulnerabilityScanner(project_root=self.project_root)
            self.counter_penetration = CounterPenetrationSystem(project_root=self.project_root)

        # Integration with other systems
        try:
            from network_security_orchestrator import NetworkSecurityOrchestrator
            self.network_security = NetworkSecurityOrchestrator(project_root=self.project_root)
        except ImportError:
            self.network_security = None

        self.logger.info("🛡️  Security Orchestrator initialized")

    def detect_and_respond(self, log_entry: str, source_ip: str = None) -> Dict[str, Any]:
        """
        Detect threats and automatically respond

        Workflow:
        1. IDS detects threat
        2. Assess severity
        3. Apply countermeasures
        4. Log incident
        """
        self.logger.info("🛡️  Security Orchestrator: Detecting and responding...")

        response = {
            "threat_detected": False,
            "alert": None,
            "countermeasures_applied": [],
            "incident_id": None
        }

        if not self.ids:
            self.logger.warning("⚠️  IDS not available")
            return response

        # Step 1: Detect threat
        alert = self.ids.analyze_log_entry(log_entry, source_ip)

        if alert:
            response["threat_detected"] = True
            response["alert"] = {
                "alert_id": alert.alert_id,
                "signature": alert.signature.value if hasattr(alert.signature, 'value') else str(alert.signature),
                "severity": alert.severity,
                "source_ip": alert.source_ip
            }

            # Step 2: Apply countermeasures based on severity
            if alert.severity in ["critical", "high"]:
                if self.counter_penetration:
                    # Block IP
                    block_measure = self.counter_penetration.block_ip(
                        alert.source_ip,
                        f"Threat detected: {alert.signature.value}",
                        duration_hours=24
                    )
                    response["countermeasures_applied"].append({
                        "type": "ip_blocking",
                        "measure_id": block_measure.measure_id,
                        "target": alert.source_ip
                    })

                    # Apply rate limiting
                    rate_limit = self.counter_penetration.apply_rate_limiting(
                        alert.source_ip,
                        max_requests_per_minute=5
                    )
                    response["countermeasures_applied"].append({
                        "type": "rate_limiting",
                        "measure_id": rate_limit.measure_id,
                        "target": alert.source_ip
                    })

            # Step 3: Create incident
            incident_id = f"incident_{datetime.now().timestamp()}"
            response["incident_id"] = incident_id

            self.logger.warning(f"🚨 Threat detected and responded: {alert.signature.value}")

        return response

    def scan_and_remediate(self, host: str) -> Dict[str, Any]:
        """
        Scan for vulnerabilities and generate remediation plan

        Workflow:
        1. Scan host for vulnerabilities
        2. Assess risk
        3. Generate remediation plan
        4. Prioritize fixes
        """
        self.logger.info(f"🔍 Security Orchestrator: Scanning {host}...")

        if not self.vulnerability_scanner:
            self.logger.warning("⚠️  Vulnerability Scanner not available")
            return {}

        # Scan host
        vulnerabilities = self.vulnerability_scanner.scan_host(host)

        # Generate report
        report = self.vulnerability_scanner.generate_report()

        # Prioritize remediation
        prioritized = sorted(
            vulnerabilities,
            key=lambda v: (v.severity.value, -v.risk_score),
            reverse=True
        )

        remediation_plan = {
            "host": host,
            "scan_date": datetime.now().isoformat(),
            "total_vulnerabilities": len(vulnerabilities),
            "prioritized_fixes": [
                {
                    "priority": i + 1,
                    "vuln_id": v.vuln_id,
                    "title": v.title,
                    "severity": v.severity.value,
                    "risk_score": v.risk_score,
                    "remediation": v.remediation
                }
                for i, v in enumerate(prioritized[:10])  # Top 10
            ],
            "report": report
        }

        self.logger.info(f"🔍 Scan complete: {len(vulnerabilities)} vulnerabilities found")

        return remediation_plan

    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "threats": {},
            "vulnerabilities": {},
            "countermeasures": {}
        }

        # IDS status
        if self.ids:
            recent_alerts = self.ids.get_recent_alerts(hours=24)
            status["components"]["ids"] = {
                "enabled": True,
                "recent_alerts": len(recent_alerts),
                "critical_alerts": len([a for a in recent_alerts if a.severity == "critical"]),
                "high_alerts": len([a for a in recent_alerts if a.severity == "high"])
            }
            status["threats"] = {
                "total_alerts_24h": len(recent_alerts),
                "by_severity": {
                    "critical": len([a for a in recent_alerts if a.severity == "critical"]),
                    "high": len([a for a in recent_alerts if a.severity == "high"]),
                    "medium": len([a for a in recent_alerts if a.severity == "medium"]),
                    "low": len([a for a in recent_alerts if a.severity == "low"])
                }
            }
        else:
            status["components"]["ids"] = {"enabled": False}

        # Vulnerability Scanner status
        if self.vulnerability_scanner:
            report = self.vulnerability_scanner.generate_report()
            status["components"]["vulnerability_scanner"] = {
                "enabled": True,
                "total_vulnerabilities": report["total_vulnerabilities"],
                "average_risk_score": report["average_risk_score"]
            }
            status["vulnerabilities"] = report["by_severity"]
        else:
            status["components"]["vulnerability_scanner"] = {"enabled": False}

        # Counter-Penetration status
        if self.counter_penetration:
            stats = self.counter_penetration.get_statistics()
            status["components"]["counter_penetration"] = {
                "enabled": True,
                "active_countermeasures": stats["active_countermeasures"],
                "blocked_ips": stats["blocked_ips"],
                "honeypots": stats["honeypots_deployed"]
            }
            status["countermeasures"] = stats
        else:
            status["components"]["counter_penetration"] = {"enabled": False}

        return status


def main():
    """CLI for security orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(description="Security Orchestrator")
    parser.add_argument("--detect", help="Log entry to analyze")
    parser.add_argument("--source-ip", help="Source IP address")
    parser.add_argument("--scan", help="Host to scan for vulnerabilities")
    parser.add_argument("--status", action="store_true", help="Get security status")

    args = parser.parse_args()

    orchestrator = SecurityOrchestrator()

    if args.detect:
        response = orchestrator.detect_and_respond(args.detect, args.source_ip)
        if response["threat_detected"]:
            print(f"\n🚨 Threat Detected:")
            print(f"  Signature: {response['alert']['signature']}")
            print(f"  Severity: {response['alert']['severity']}")
            print(f"  Source IP: {response['alert']['source_ip']}")
            print(f"\n  Countermeasures Applied: {len(response['countermeasures_applied'])}")
            for cm in response["countermeasures_applied"]:
                print(f"    - {cm['type']}: {cm['target']}")
        else:
            print("✅ No threats detected")

    elif args.scan:
        plan = orchestrator.scan_and_remediate(args.scan)
        print(f"\n🔍 Vulnerability Scan Results:")
        print(f"  Total Vulnerabilities: {plan['total_vulnerabilities']}")
        print(f"\n  Top Priority Fixes:")
        for fix in plan["prioritized_fixes"][:5]:
            print(f"    {fix['priority']}. [{fix['severity'].upper()}] {fix['title']} (Risk: {fix['risk_score']}/10.0)")

    elif args.status:
        status = orchestrator.get_security_status()
        print(f"\n🛡️  Security Status:")
        print(f"\n  Components:")
        for component, info in status["components"].items():
            enabled = "✅" if info.get("enabled") else "❌"
            print(f"    {enabled} {component.replace('_', ' ').title()}")

        if status.get("threats"):
            print(f"\n  Threats (24h):")
            print(f"    Total Alerts: {status['threats']['total_alerts_24h']}")
            for severity, count in status["threats"]["by_severity"].items():
                if count > 0:
                    print(f"    {severity.upper()}: {count}")

        if status.get("vulnerabilities"):
            print(f"\n  Vulnerabilities:")
            for severity, count in status["vulnerabilities"].items():
                if count > 0:
                    print(f"    {severity.upper()}: {count}")

        if status.get("countermeasures"):
            print(f"\n  Countermeasures:")
            print(f"    Active: {status['countermeasures']['active_countermeasures']}")
            print(f"    Blocked IPs: {status['countermeasures']['blocked_ips']}")
            print(f"    Honeypots: {status['countermeasures']['honeypots_deployed']}")

    else:
        parser.print_help()


if __name__ == "__main__":



    main()