#!/usr/bin/env python3
"""
Intrusion Detection System (IDS)

Real-time threat detection and alerting.
Designed by @MARVIN, @HK-47, JARVIS, and @MANUS collaboration.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import re

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SecurityIDS")


class ThreatSignature(Enum):
    """Threat signatures for detection"""
    PORT_SCAN = "port_scan"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    COMMAND_INJECTION = "command_injection"
    DNS_TUNNELING = "dns_tunneling"
    CERTIFICATE_MISMATCH = "certificate_mismatch"
    UNUSUAL_TRAFFIC = "unusual_traffic"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"


@dataclass
class IDSAlert:
    """IDS alert"""
    alert_id: str
    signature: ThreatSignature
    severity: str  # critical, high, medium, low
    source_ip: str
    target_ip: str
    description: str
    detected_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    countermeasures_applied: List[str] = field(default_factory=list)


class IntrusionDetectionSystem:
    """
    Intrusion Detection System

    Features:
    - Signature-based detection
    - Anomaly detection
    - Real-time alerting
    - Threat intelligence integration
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("IntrusionDetectionSystem")

        self.data_dir = self.project_root / "data" / "security" / "ids"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.alerts: List[IDSAlert] = []
        self.threat_signatures = self._load_threat_signatures()
        self.whitelist_ips = self._load_whitelist()

        self.logger.info("🛡️  Intrusion Detection System initialized")

    def _load_threat_signatures(self) -> Dict[str, Dict[str, Any]]:
        """Load threat signatures"""
        return {
            ThreatSignature.PORT_SCAN.value: {
                "pattern": r"(\d+\.\d+\.\d+\.\d+).*?(\d+\.\d+\.\d+\.\d+).*?(\d+)",
                "threshold": 10,  # 10 connection attempts
                "time_window": 60,  # within 60 seconds
                "severity": "high"
            },
            ThreatSignature.BRUTE_FORCE.value: {
                "pattern": r"(?i)(failed.*?login|authentication.*?failed|invalid.*?password)",
                "threshold": 5,  # 5 failed attempts
                "time_window": 300,  # within 5 minutes
                "severity": "high"
            },
            ThreatSignature.SQL_INJECTION.value: {
                "pattern": r"(?i)(union.*?select|';.*?--|or.*?1=1|drop.*?table)",
                "threshold": 1,
                "time_window": 0,
                "severity": "critical"
            },
            ThreatSignature.XSS_ATTACK.value: {
                "pattern": r"(?i)(<script|javascript:|onerror=|onload=)",
                "threshold": 1,
                "time_window": 0,
                "severity": "high"
            },
            ThreatSignature.DNS_TUNNELING.value: {
                "pattern": r"([a-zA-Z0-9]{50,}\.[a-z]{2,})",  # Very long hostnames
                "threshold": 3,
                "time_window": 60,
                "severity": "medium"
            },
            ThreatSignature.CERTIFICATE_MISMATCH.value: {
                "pattern": r"(?i)(certificate.*?mismatch|ssl.*?error|certificate.*?invalid)",
                "threshold": 1,
                "time_window": 0,
                "severity": "high"
            }
        }

    def _load_whitelist(self) -> List[str]:
        """Load whitelist IPs"""
        whitelist_file = self.data_dir / "whitelist_ips.json"
        if whitelist_file.exists():
            try:
                with open(whitelist_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return ["127.0.0.1", "::1", "<NAS_PRIMARY_IP>", "<NAS_IP>"]  # Default whitelist

    def analyze_log_entry(self, log_entry: str, source_ip: str = None, target_ip: str = None) -> Optional[IDSAlert]:
        """Analyze log entry for threats"""
        # Skip whitelisted IPs
        if source_ip and source_ip in self.whitelist_ips:
            return None

        # Check each threat signature
        for signature_name, signature_config in self.threat_signatures.items():
            pattern = signature_config["pattern"]
            if re.search(pattern, log_entry, re.IGNORECASE):
                alert = IDSAlert(
                    alert_id=f"ids_{datetime.now().timestamp()}",
                    signature=ThreatSignature(signature_name),
                    severity=signature_config["severity"],
                    source_ip=source_ip or "unknown",
                    target_ip=target_ip or "unknown",
                    description=f"Detected {signature_name} in log entry",
                    detected_at=datetime.now(),
                    metadata={
                        "log_entry": log_entry[:500],  # Truncate long entries
                        "pattern_matched": pattern
                    }
                )

                self.alerts.append(alert)
                self.logger.warning(f"🚨 IDS Alert: {signature_name} from {source_ip}")

                return alert

        return None

    def detect_anomaly(self, metrics: Dict[str, Any]) -> Optional[IDSAlert]:
        """Detect anomalies in system metrics"""
        # Example: Unusual network traffic
        if metrics.get("network_traffic_mb_per_min", 0) > 1000:  # > 1GB/min
            alert = IDSAlert(
                alert_id=f"ids_anomaly_{datetime.now().timestamp()}",
                signature=ThreatSignature.UNUSUAL_TRAFFIC,
                severity="high",
                source_ip=metrics.get("source_ip", "unknown"),
                target_ip=metrics.get("target_ip", "unknown"),
                description=f"Unusual network traffic detected: {metrics.get('network_traffic_mb_per_min')} MB/min",
                detected_at=datetime.now(),
                metadata=metrics
            )

            self.alerts.append(alert)
            self.logger.warning(f"🚨 IDS Alert: Unusual traffic detected")

            return alert

        return None

    def get_recent_alerts(self, hours: int = 24) -> List[IDSAlert]:
        """Get recent alerts"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.detected_at >= cutoff]

    def get_alerts_by_severity(self, severity: str) -> List[IDSAlert]:
        """Get alerts by severity"""
        return [alert for alert in self.alerts if alert.severity == severity]

    def save_alerts(self):
        try:
            """Save alerts to file"""
            alerts_file = self.data_dir / f"alerts_{datetime.now().strftime('%Y%m%d')}.json"

            alerts_data = []
            for alert in self.alerts:
                alerts_data.append({
                    "alert_id": alert.alert_id,
                    "signature": alert.signature.value if isinstance(alert.signature, ThreatSignature) else alert.signature,
                    "severity": alert.severity,
                    "source_ip": alert.source_ip,
                    "target_ip": alert.target_ip,
                    "description": alert.description,
                    "detected_at": alert.detected_at.isoformat(),
                    "metadata": alert.metadata,
                    "countermeasures_applied": alert.countermeasures_applied
                })

            with open(alerts_file, 'w', encoding='utf-8') as f:
                json.dump(alerts_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"💾 Saved {len(self.alerts)} alerts to {alerts_file}")


        except Exception as e:
            self.logger.error(f"Error in save_alerts: {e}", exc_info=True)
            raise
def main():
    """CLI for IDS"""
    import argparse

    parser = argparse.ArgumentParser(description="Intrusion Detection System")
    parser.add_argument("--analyze-log", help="Analyze log entry")
    parser.add_argument("--source-ip", help="Source IP address")
    parser.add_argument("--target-ip", help="Target IP address")
    parser.add_argument("--recent-alerts", type=int, default=24, help="Show recent alerts (hours)")
    parser.add_argument("--severity", help="Filter alerts by severity")

    args = parser.parse_args()

    ids = IntrusionDetectionSystem()

    if args.analyze_log:
        alert = ids.analyze_log_entry(args.analyze_log, args.source_ip, args.target_ip)
        if alert:
            print(f"\n🚨 IDS Alert Generated:")
            print(f"  Signature: {alert.signature.value}")
            print(f"  Severity: {alert.severity}")
            print(f"  Source IP: {alert.source_ip}")
            print(f"  Description: {alert.description}")
        else:
            print("✅ No threats detected in log entry")

    elif args.recent_alerts:
        alerts = ids.get_recent_alerts(args.recent_alerts)
        if args.severity:
            alerts = [a for a in alerts if a.severity == args.severity]

        print(f"\n📊 Recent Alerts ({len(alerts)}):")
        for alert in alerts[-10:]:  # Show last 10
            print(f"  [{alert.severity.upper()}] {alert.signature.value}: {alert.description}")
            print(f"    Source: {alert.source_ip} → Target: {alert.target_ip}")
            print(f"    Time: {alert.detected_at}")
            print()

    else:
        parser.print_help()


if __name__ == "__main__":



    main()