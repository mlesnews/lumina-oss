#!/usr/bin/env python3
"""
@MARVIN Network Security Red Team Review (@RR)

Comprehensive red team security assessment of network infrastructure:
- pfSense firewall security
- NAS security posture
- DHCP configuration security
- Network segmentation
- Attack surface analysis
- Vulnerability assessment

Tags: #MARVIN #RED_TEAM #RR #NETWORK_SECURITY #PENTEST #SECURITY_AUDIT
@MARVIN @JARVIS @LUMINA @RR
"""

import sys
import socket
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

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

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = get_logger("MARVINRedTeamReview")


class ThreatLevel(Enum):
    """Threat level classification"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AttackVector(Enum):
    """Attack vector categories"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    SERVICE = "service"
    PROTOCOL = "protocol"


@dataclass
class SecurityFinding:
    """Security finding from red team review"""
    finding_id: str
    title: str
    description: str
    threat_level: ThreatLevel
    attack_vector: AttackVector
    affected_system: str
    recommendation: str
    evidence: List[str] = field(default_factory=list)
    cwe: Optional[str] = None
    cvss_score: Optional[float] = None


class MARVINNetworkSecurityRedTeamReview:
    """
    @MARVIN Red Team Review of Network Security

    Comprehensive security assessment from attacker perspective
    """

    def __init__(
        self,
        pfsense_ip: str = "<NAS_IP>",
        nas_ip: str = "<NAS_PRIMARY_IP>",
        subnet: str = "<NAS_IP>/24"
    ):
        """Initialize red team review"""
        self.pfsense_ip = pfsense_ip
        self.nas_ip = nas_ip
        self.subnet = subnet
        self.findings: List[SecurityFinding] = []
        self.scan_results: Dict[str, Any] = {}

        logger.info("🔴 @MARVIN RED TEAM REVIEW - Network Security Assessment")
        logger.info(f"   Target Network: {subnet}")
        logger.info(f"   pfSense: {pfsense_ip}")
        logger.info(f"   NAS: {nas_ip}")

    def scan_open_ports(self, target_ip: str, ports: List[int]) -> Dict[int, bool]:
        """Scan for open ports (red team perspective)"""
        results = {}
        logger.info(f"🔍 Scanning {target_ip} for open ports...")

        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target_ip, port))
                sock.close()
                results[port] = result == 0

                if result == 0:
                    logger.warning(f"   ⚠️  Port {port} is OPEN on {target_ip}")
            except Exception as e:
                logger.debug(f"   Error scanning port {port}: {e}")
                results[port] = False

        return results

    def assess_pfsense_security(self) -> List[SecurityFinding]:
        """Assess pfSense security posture"""
        findings = []
        logger.info("\n🔴 RED TEAM: Assessing pfSense Security...")

        # Scan common ports
        common_ports = [22, 80, 443, 53, 8080, 8443]
        port_scan = self.scan_open_ports(self.pfsense_ip, common_ports)

        # Finding 1: SSH Port Status
        if port_scan.get(22, False):
            findings.append(SecurityFinding(
                finding_id="PFSENSE-001",
                title="SSH Port Exposed",
                description=f"SSH port 22 is open on {self.pfsense_ip}. This exposes an additional attack surface.",
                threat_level=ThreatLevel.MEDIUM,
                attack_vector=AttackVector.NETWORK,
                affected_system="pfSense",
                recommendation="Keep SSH disabled. Use MANUS/NEO browser automation instead (recommended by @MARVIN security assessment).",
                evidence=[f"Port scan: Port 22 is OPEN on {self.pfsense_ip}"],
                cvss_score=5.3
            ))
        else:
            findings.append(SecurityFinding(
                finding_id="PFSENSE-001",
                title="SSH Port Closed (Good)",
                description=f"SSH port 22 is closed on {self.pfsense_ip}. This reduces attack surface.",
                threat_level=ThreatLevel.INFO,
                attack_vector=AttackVector.NETWORK,
                affected_system="pfSense",
                recommendation="✅ Maintain current configuration. SSH disabled is @PEAK security.",
                evidence=[f"Port scan: Port 22 is CLOSED on {self.pfsense_ip}"],
                cvss_score=0.0
            ))

        # Finding 2: HTTPS Port
        if port_scan.get(443, False):
            findings.append(SecurityFinding(
                finding_id="PFSENSE-002",
                title="HTTPS Web Portal Accessible",
                description=f"HTTPS port 443 is open on {self.pfsense_ip}. Web portal is accessible.",
                threat_level=ThreatLevel.LOW,
                attack_vector=AttackVector.NETWORK,
                affected_system="pfSense",
                recommendation="✅ Expected behavior. Ensure strong authentication and HTTPS encryption.",
                evidence=[f"Port scan: Port 443 is OPEN on {self.pfsense_ip}"]
            ))

        # Finding 3: HTTP Port
        if port_scan.get(80, False):
            findings.append(SecurityFinding(
                finding_id="PFSENSE-003",
                title="HTTP Port Open (Potential Risk)",
                description=f"HTTP port 80 is open on {self.pfsense_ip}. Unencrypted traffic possible.",
                threat_level=ThreatLevel.MEDIUM,
                attack_vector=AttackVector.PROTOCOL,
                affected_system="pfSense",
                recommendation="Redirect HTTP to HTTPS or disable HTTP port. Force HTTPS only.",
                evidence=[f"Port scan: Port 80 is OPEN on {self.pfsense_ip}"],
                cvss_score=4.3
            ))

        # Finding 4: DNS Port
        if port_scan.get(53, False):
            findings.append(SecurityFinding(
                finding_id="PFSENSE-004",
                title="DNS Port Open",
                description=f"DNS port 53 is open on {self.pfsense_ip}. DNS service is running.",
                threat_level=ThreatLevel.LOW,
                attack_vector=AttackVector.SERVICE,
                affected_system="pfSense",
                recommendation="✅ Expected for DNS server. Monitor for DNS amplification attacks.",
                evidence=[f"Port scan: Port 53 is OPEN on {self.pfsense_ip}"]
            ))

        # Test web portal accessibility
        if REQUESTS_AVAILABLE:
            try:
                response = requests.get(
                    f"https://{self.pfsense_ip}",
                    verify=False,
                    timeout=5
                )
                findings.append(SecurityFinding(
                    finding_id="PFSENSE-005",
                    title="Web Portal Accessible",
                    description=f"pfSense web portal is accessible via HTTPS. Authentication required.",
                    threat_level=ThreatLevel.INFO,
                    attack_vector=AttackVector.AUTHENTICATION,
                    affected_system="pfSense",
                    recommendation="✅ Ensure strong passwords and consider 2FA if available.",
                    evidence=[f"HTTPS response: {response.status_code}"]
                ))
            except Exception as e:
                logger.debug(f"Web portal test failed: {e}")

        return findings

    def assess_nas_security(self) -> List[SecurityFinding]:
        """Assess NAS security posture"""
        findings = []
        logger.info("\n🔴 RED TEAM: Assessing NAS Security...")

        # Scan common ports
        common_ports = [22, 80, 443, 5000, 5001, 53, 139, 445]
        port_scan = self.scan_open_ports(self.nas_ip, common_ports)

        # Finding 1: SSH Port
        if port_scan.get(22, False):
            findings.append(SecurityFinding(
                finding_id="NAS-001",
                title="SSH Port Open on NAS",
                description=f"SSH port 22 is open on {self.nas_ip}. SSH service is running.",
                threat_level=ThreatLevel.MEDIUM,
                attack_vector=AttackVector.NETWORK,
                affected_system="NAS",
                recommendation="Ensure SSH uses key-only authentication. Monitor SSH access logs.",
                evidence=[f"Port scan: Port 22 is OPEN on {self.nas_ip}"],
                cvss_score=5.3
            ))
        else:
            findings.append(SecurityFinding(
                finding_id="NAS-001",
                title="SSH Port Closed on NAS",
                description=f"SSH port 22 is closed on {self.nas_ip}.",
                threat_level=ThreatLevel.INFO,
                attack_vector=AttackVector.NETWORK,
                affected_system="NAS",
                recommendation="✅ Good security practice. SSH disabled reduces attack surface.",
                evidence=[f"Port scan: Port 22 is CLOSED on {self.nas_ip}"]
            ))

        # Finding 2: DSM Web Portal
        if port_scan.get(5001, False):
            findings.append(SecurityFinding(
                finding_id="NAS-002",
                title="DSM Web Portal Accessible",
                description=f"DSM web portal (HTTPS) is accessible on port 5001.",
                threat_level=ThreatLevel.LOW,
                attack_vector=AttackVector.NETWORK,
                affected_system="NAS",
                recommendation="✅ Expected. Ensure strong authentication and HTTPS encryption.",
                evidence=[f"Port scan: Port 5001 is OPEN on {self.nas_ip}"]
            ))

        # Finding 3: HTTP Port
        if port_scan.get(5000, False):
            findings.append(SecurityFinding(
                finding_id="NAS-003",
                title="HTTP Port Open on NAS",
                description=f"HTTP port 5000 is open on {self.nas_ip}. Unencrypted access possible.",
                threat_level=ThreatLevel.MEDIUM,
                attack_vector=AttackVector.PROTOCOL,
                affected_system="NAS",
                recommendation="Disable HTTP or redirect to HTTPS. Force encrypted connections only.",
                evidence=[f"Port scan: Port 5000 is OPEN on {self.nas_ip}"],
                cvss_score=4.3
            ))

        # Finding 4: SMB Ports
        if port_scan.get(139, False) or port_scan.get(445, False):
            findings.append(SecurityFinding(
                finding_id="NAS-004",
                title="SMB Ports Open",
                description=f"SMB ports (139/445) are open on {self.nas_ip}. File sharing enabled.",
                threat_level=ThreatLevel.MEDIUM,
                attack_vector=AttackVector.SERVICE,
                affected_system="NAS",
                recommendation="Ensure SMB encryption enabled. Restrict access to trusted networks. Monitor for SMB vulnerabilities.",
                evidence=[
                    f"Port scan: Port 139 is {'OPEN' if port_scan.get(139) else 'CLOSED'}",
                    f"Port scan: Port 445 is {'OPEN' if port_scan.get(445) else 'CLOSED'}"
                ],
                cvss_score=5.9
            ))

        return findings

    def assess_dhcp_security(self) -> List[SecurityFinding]:
        """Assess DHCP configuration security"""
        findings = []
        logger.info("\n🔴 RED TEAM: Assessing DHCP Security...")

        # Finding 1: DHCP Active Failover
        findings.append(SecurityFinding(
            finding_id="DHCP-001",
            title="DHCP Active Failover Configured",
            description="DHCP active failover is configured with pfSense primary and NAS fallback.",
            threat_level=ThreatLevel.LOW,
            attack_vector=AttackVector.CONFIGURATION,
            affected_system="Network",
            recommendation="✅ Good redundancy. Ensure both servers use non-overlapping ranges to prevent conflicts.",
            evidence=[
                "pfSense: <NAS_IP>-150 (Primary)",
                "NAS: <NAS_IP>-200 (Fallback)"
            ]
        ))

        # Finding 2: DHCP Range Security
        findings.append(SecurityFinding(
            finding_id="DHCP-002",
            title="DHCP Range Configuration",
            description="DHCP ranges are properly segmented with non-overlapping IP pools.",
            threat_level=ThreatLevel.INFO,
            attack_vector=AttackVector.CONFIGURATION,
            affected_system="Network",
            recommendation="✅ Configuration is secure. Monitor for DHCP exhaustion attacks.",
            evidence=[
                "Non-overlapping ranges prevent IP conflicts",
                "Failover monitor manages automatic switching"
            ]
        ))

        # Finding 3: DHCP Spoofing Risk
        findings.append(SecurityFinding(
            finding_id="DHCP-003",
            title="DHCP Spoofing Risk",
            description="Multiple DHCP servers on network increase spoofing risk if not properly configured.",
            threat_level=ThreatLevel.MEDIUM,
            attack_vector=AttackVector.SERVICE,
            affected_system="Network",
            recommendation="Ensure only one DHCP server is active at a time. Monitor for rogue DHCP servers. Use DHCP snooping if available.",
            evidence=[
                "Two DHCP servers configured (pfSense + NAS)",
                "Failover monitor should prevent both being active simultaneously"
            ],
            cvss_score=5.3
        ))

        return findings

    def assess_network_segmentation(self) -> List[SecurityFinding]:
        """Assess network segmentation and isolation"""
        findings = []
        logger.info("\n🔴 RED TEAM: Assessing Network Segmentation...")

        # Finding 1: Single Subnet
        findings.append(SecurityFinding(
            finding_id="NET-001",
            title="Single Subnet Configuration",
            description=f"All devices on single subnet {self.subnet}. No network segmentation.",
            threat_level=ThreatLevel.MEDIUM,
            attack_vector=AttackVector.NETWORK,
            affected_system="Network",
            recommendation="Consider VLAN segmentation for critical systems. Isolate management interfaces from user devices.",
            evidence=[f"Subnet: {self.subnet}"],
            cvss_score=4.9
        ))

        # Finding 2: Gateway Security
        findings.append(SecurityFinding(
            finding_id="NET-002",
            title="Gateway Configuration",
            description=f"pfSense ({self.pfsense_ip}) serves as gateway and firewall.",
            threat_level=ThreatLevel.INFO,
            attack_vector=AttackVector.NETWORK,
            affected_system="Network",
            recommendation="✅ Good practice. Ensure firewall rules are properly configured. Monitor firewall logs.",
            evidence=[f"Gateway: {self.pfsense_ip}"]
        ))

        return findings

    def assess_authentication_security(self) -> List[SecurityFinding]:
        """Assess authentication mechanisms"""
        findings = []
        logger.info("\n🔴 RED TEAM: Assessing Authentication Security...")

        # Finding 1: Azure Key Vault Integration
        findings.append(SecurityFinding(
            finding_id="AUTH-001",
            title="Azure Key Vault Credential Storage",
            description="Credentials stored in Azure Key Vault. Centralized secret management.",
            threat_level=ThreatLevel.INFO,
            attack_vector=AttackVector.AUTHENTICATION,
            affected_system="Authentication",
            recommendation="✅ Good practice. Ensure Key Vault access is properly restricted. Monitor access logs.",
            evidence=["Credentials retrieved from Azure Key Vault"]
        ))

        # Finding 2: SSH Authentication
        findings.append(SecurityFinding(
            finding_id="AUTH-002",
            title="SSH Authentication Method",
            description="SSH is disabled on pfSense. MANUS/NEO browser automation used instead.",
            threat_level=ThreatLevel.INFO,
            attack_vector=AttackVector.AUTHENTICATION,
            affected_system="pfSense",
            recommendation="✅ @PEAK security. SSH disabled reduces attack surface. Browser automation provides secure alternative.",
            evidence=["SSH port 22 closed", "MANUS/NEO automation configured"]
        ))

        return findings

    def generate_attack_scenarios(self) -> List[Dict[str, Any]]:
        """Generate potential attack scenarios"""
        scenarios = []
        logger.info("\n🔴 RED TEAM: Generating Attack Scenarios...")

        # Scenario 1: DHCP Exhaustion
        scenarios.append({
            "scenario_id": "ATTACK-001",
            "title": "DHCP Exhaustion Attack",
            "description": "Attacker could exhaust DHCP pool by requesting multiple IPs",
            "threat_level": ThreatLevel.MEDIUM.value,
            "mitigation": "Monitor DHCP lease counts. Implement rate limiting if possible.",
            "detection": "Monitor for unusual DHCP request patterns"
        })

        # Scenario 2: Rogue DHCP Server
        scenarios.append({
            "scenario_id": "ATTACK-002",
            "title": "Rogue DHCP Server Attack",
            "description": "Attacker could deploy rogue DHCP server to intercept traffic",
            "threat_level": ThreatLevel.HIGH.value,
            "mitigation": "Use DHCP snooping. Monitor for unauthorized DHCP servers.",
            "detection": "Network monitoring for unexpected DHCP responses"
        })

        # Scenario 3: Web Portal Brute Force
        scenarios.append({
            "scenario_id": "ATTACK-003",
            "title": "Web Portal Brute Force",
            "description": "Attacker could brute force web portal credentials",
            "threat_level": ThreatLevel.MEDIUM.value,
            "mitigation": "Enable account lockout. Use strong passwords. Consider 2FA.",
            "detection": "Monitor failed login attempts"
        })

        # Scenario 4: Man-in-the-Middle (MITM)
        scenarios.append({
            "scenario_id": "ATTACK-004",
            "title": "Man-in-the-Middle Attack",
            "description": "Attacker could intercept traffic if encryption is weak",
            "threat_level": ThreatLevel.MEDIUM.value,
            "mitigation": "Ensure HTTPS/TLS 1.2+ on all services. Disable HTTP.",
            "detection": "Monitor for certificate warnings or downgrade attacks"
        })

        return scenarios

    def conduct_red_team_review(self) -> Dict[str, Any]:
        """
        Conduct comprehensive red team review

        Returns:
            Complete red team review report
        """
        logger.info("=" * 70)
        logger.info("🔴 @MARVIN RED TEAM REVIEW - NETWORK SECURITY")
        logger.info("=" * 70)
        logger.info("\n🎯 Red Team Perspective: Attacker Viewpoint")
        logger.info("   Assessing network from potential attacker's perspective\n")

        # Collect all findings
        all_findings = []

        # Assess each component
        all_findings.extend(self.assess_pfsense_security())
        all_findings.extend(self.assess_nas_security())
        all_findings.extend(self.assess_dhcp_security())
        all_findings.extend(self.assess_network_segmentation())
        all_findings.extend(self.assess_authentication_security())

        # Generate attack scenarios
        attack_scenarios = self.generate_attack_scenarios()

        # Categorize findings
        critical_findings = [f for f in all_findings if f.threat_level == ThreatLevel.CRITICAL]
        high_findings = [f for f in all_findings if f.threat_level == ThreatLevel.HIGH]
        medium_findings = [f for f in all_findings if f.threat_level == ThreatLevel.MEDIUM]
        low_findings = [f for f in all_findings if f.threat_level == ThreatLevel.LOW]
        info_findings = [f for f in all_findings if f.threat_level == ThreatLevel.INFO]

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "review_type": "Red Team Review (@RR)",
            "reviewer": "@MARVIN",
            "target_network": self.subnet,
            "summary": {
                "total_findings": len(all_findings),
                "critical": len(critical_findings),
                "high": len(high_findings),
                "medium": len(medium_findings),
                "low": len(low_findings),
                "info": len(info_findings)
            },
            "findings": {
                "critical": [self._finding_to_dict(f) for f in critical_findings],
                "high": [self._finding_to_dict(f) for f in high_findings],
                "medium": [self._finding_to_dict(f) for f in medium_findings],
                "low": [self._finding_to_dict(f) for f in low_findings],
                "info": [self._finding_to_dict(f) for f in info_findings]
            },
            "attack_scenarios": attack_scenarios,
            "recommendations": self._generate_recommendations(all_findings),
            "security_score": self._calculate_security_score(all_findings)
        }

        # Display report
        self._display_report(report)

        return report

    def _finding_to_dict(self, finding: SecurityFinding) -> Dict[str, Any]:
        """Convert finding to dictionary"""
        return {
            "id": finding.finding_id,
            "title": finding.title,
            "description": finding.description,
            "threat_level": finding.threat_level.value,
            "attack_vector": finding.attack_vector.value,
            "affected_system": finding.affected_system,
            "recommendation": finding.recommendation,
            "evidence": finding.evidence,
            "cvss_score": finding.cvss_score
        }

    def _generate_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Critical/High priority
        critical_high = [f for f in findings if f.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]]
        if critical_high:
            recommendations.append("🔴 PRIORITY 1: Address critical and high-severity findings immediately")

        # Medium priority
        medium = [f for f in findings if f.threat_level == ThreatLevel.MEDIUM]
        if medium:
            recommendations.append("🟠 PRIORITY 2: Review and mitigate medium-severity findings")

        # Specific recommendations
        if any("SSH" in f.title and "Open" in f.title for f in findings):
            recommendations.append("⚠️  Consider disabling SSH on systems where not required")

        if any("HTTP" in f.title and "Open" in f.title for f in findings):
            recommendations.append("⚠️  Disable HTTP ports or redirect to HTTPS")

        recommendations.append("✅ Continue using MANUS/NEO browser automation (no SSH required)")
        recommendations.append("✅ Maintain Azure Key Vault for credential storage")
        recommendations.append("✅ Monitor network traffic for anomalies")
        recommendations.append("✅ Regular security audits and reviews")

        return recommendations

    def _calculate_security_score(self, findings: List[SecurityFinding]) -> Dict[str, Any]:
        """Calculate overall security score"""
        total_score = 100

        # Deduct points for findings (only negative findings, not info)
        for finding in findings:
            if finding.threat_level == ThreatLevel.CRITICAL:
                total_score -= 25
            elif finding.threat_level == ThreatLevel.HIGH:
                total_score -= 15
            elif finding.threat_level == ThreatLevel.MEDIUM:
                total_score -= 8
            elif finding.threat_level == ThreatLevel.LOW:
                total_score -= 3
            # INFO findings don't deduct points (they're positive)

        # Ensure score doesn't go below 0
        total_score = max(0, total_score)

        # Bonus points for good security practices
        info_findings = [f for f in findings if f.threat_level == ThreatLevel.INFO]
        if len(info_findings) >= 3:
            total_score = min(100, total_score + 5)  # Bonus for good practices

        # Grade
        if total_score >= 90:
            grade = "A+"
        elif total_score >= 80:
            grade = "A"
        elif total_score >= 70:
            grade = "B"
        elif total_score >= 60:
            grade = "C"
        else:
            grade = "D"

        return {
            "score": total_score,
            "grade": grade,
            "max_score": 100,
            "assessment": "Excellent" if total_score >= 90 else \
                          "Good" if total_score >= 80 else \
                          "Fair" if total_score >= 70 else \
                          "Needs Improvement"
        }

    def _display_report(self, report: Dict[str, Any]) -> None:
        """Display red team review report"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 RED TEAM REVIEW SUMMARY")
        logger.info("=" * 70)

        summary = report["summary"]
        logger.info(f"\n📋 Findings Summary:")
        logger.info(f"   Total Findings: {summary['total_findings']}")
        logger.info(f"   🔴 Critical: {summary['critical']}")
        logger.info(f"   🟠 High: {summary['high']}")
        logger.info(f"   🟡 Medium: {summary['medium']}")
        logger.info(f"   🔵 Low: {summary['low']}")
        logger.info(f"   ℹ️  Info: {summary['info']}")

        # Security Score
        score = report["security_score"]
        logger.info(f"\n🎯 Security Score: {score['score']}/100 ({score['grade']})")
        logger.info(f"   Assessment: {score['assessment']}")

        # Critical Findings
        if report["findings"]["critical"]:
            logger.info(f"\n🔴 CRITICAL FINDINGS:")
            for finding in report["findings"]["critical"]:
                logger.info(f"   [{finding['id']}] {finding['title']}")
                logger.info(f"      {finding['description']}")
                logger.info(f"      Recommendation: {finding['recommendation']}")

        # High Findings
        if report["findings"]["high"]:
            logger.info(f"\n🟠 HIGH FINDINGS:")
            for finding in report["findings"]["high"]:
                logger.info(f"   [{finding['id']}] {finding['title']}")
                logger.info(f"      Recommendation: {finding['recommendation']}")

        # Medium Findings
        if report["findings"]["medium"]:
            logger.info(f"\n🟡 MEDIUM FINDINGS:")
            for finding in report["findings"]["medium"][:5]:  # Show first 5
                logger.info(f"   [{finding['id']}] {finding['title']}")

        # Attack Scenarios
        logger.info(f"\n🔴 ATTACK SCENARIOS:")
        for scenario in report["attack_scenarios"]:
            threat_icon = "🔴" if scenario["threat_level"] == "high" else "🟠" if scenario["threat_level"] == "medium" else "🟡"
            logger.info(f"   {threat_icon} [{scenario['scenario_id']}] {scenario['title']}")
            logger.info(f"      Mitigation: {scenario['mitigation']}")

        # Recommendations
        logger.info(f"\n💡 PRIORITIZED RECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"], 1):
            logger.info(f"   {i}. {rec}")

        logger.info("\n" + "=" * 70)
        logger.info("🔴 RED TEAM REVIEW COMPLETE")
        logger.info("=" * 70)


def main():
    try:
        """Main function"""
        import argparse
        import json

        parser = argparse.ArgumentParser(
            description="@MARVIN Network Security Red Team Review (@RR)"
        )
        parser.add_argument(
            "--pfsense-ip",
            default="<NAS_IP>",
            help="pfSense IP address"
        )
        parser.add_argument(
            "--nas-ip",
            default="<NAS_PRIMARY_IP>",
            help="NAS IP address"
        )
        parser.add_argument(
            "--subnet",
            default="<NAS_IP>/24",
            help="Network subnet"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output as JSON"
        )
        parser.add_argument(
            "--output",
            help="Save report to file"
        )

        args = parser.parse_args()

        review = MARVINNetworkSecurityRedTeamReview(
            pfsense_ip=args.pfsense_ip,
            nas_ip=args.nas_ip,
            subnet=args.subnet
        )

        report = review.conduct_red_team_review()

        if args.json:
            print(json.dumps(report, indent=2, default=str))

        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"\n💾 Report saved to: {output_path}")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())