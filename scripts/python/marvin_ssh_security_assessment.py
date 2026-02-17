#!/usr/bin/env python3
"""
@MARVIN SSH Security Assessment for pfSense

Security analysis and recommendation for enabling SSH on pfSense.
Provides @PEAK security assessment with @MARVIN verification.

Tags: #MARVIN #SECURITY #SSH #PFSENSE #PEAK #ASSESSMENT
@MARVIN @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
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

logger = get_logger("MARVINSSHSecurity")


class SecurityLevel(Enum):
    """Security level assessment"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class SSHConfiguration(Enum):
    """SSH configuration options"""
    DISABLED = "disabled"
    KEY_ONLY = "key_only"
    PASSWORD_AUTH = "password_auth"
    RESTRICTED_IP = "restricted_ip"


class MARVINSSHSecurityAssessment:
    """
    @MARVIN Security Assessment for SSH Configuration

    Analyzes security implications of enabling SSH on pfSense
    """

    def __init__(self):
        """Initialize security assessment"""
        self.assessments: List[Dict[str, Any]] = []
        logger.info("🔒 @MARVIN SSH Security Assessment initialized")

    def assess_ssh_disabled(self) -> Dict[str, Any]:
        """Assess security of SSH disabled configuration"""
        assessment = {
            "configuration": "SSH Disabled",
            "security_level": SecurityLevel.HIGH.value,
            "attack_surface": "Minimal",
            "pros": [
                "✅ No SSH port exposed (port 22 closed)",
                "✅ No password brute force risk",
                "✅ No SSH key management required",
                "✅ Reduced attack surface",
                "✅ Principle of least privilege"
            ],
            "cons": [
                "⚠️  No direct CLI access",
                "⚠️  Requires web portal for configuration",
                "⚠️  pfSsh.php commands unavailable",
                "⚠️  Slower automation (browser-based)"
            ],
            "recommendation": "RECOMMENDED for @PEAK security",
            "risk_score": 2,  # Low risk (1-10 scale)
            "automation_impact": "MANUS/NEO browser automation required"
        }

        return assessment

    def assess_ssh_key_only(self) -> Dict[str, Any]:
        """Assess security of SSH with key-only authentication"""
        assessment = {
            "configuration": "SSH Enabled - Key Only",
            "security_level": SecurityLevel.MEDIUM.value,
            "attack_surface": "Moderate",
            "pros": [
                "✅ No password authentication (more secure)",
                "✅ Public key cryptography (strong)",
                "✅ Can disable password auth completely",
                "✅ Faster automation than browser",
                "✅ Direct CLI access available"
            ],
            "cons": [
                "⚠️  SSH port exposed (port 22 open)",
                "⚠️  Requires key management",
                "⚠️  Key compromise = full access",
                "⚠️  Additional service to maintain"
            ],
            "recommendation": "ACCEPTABLE with proper key management",
            "risk_score": 5,  # Medium risk
            "requirements": [
                "Strong SSH keys (RSA 4096 or Ed25519)",
                "Key rotation policy",
                "Restricted IP access (if possible)",
                "SSH key stored in Azure Key Vault",
                "Regular security audits"
            ]
        }

        return assessment

    def assess_ssh_password_auth(self) -> Dict[str, Any]:
        """Assess security of SSH with password authentication"""
        assessment = {
            "configuration": "SSH Enabled - Password Auth",
            "security_level": SecurityLevel.CRITICAL.value,
            "attack_surface": "High",
            "pros": [
                "✅ Faster automation",
                "✅ Direct CLI access",
                "✅ Easy to use"
            ],
            "cons": [
                "❌ Password brute force risk",
                "❌ Password stored in Azure Key Vault (still risk)",
                "❌ SSH port exposed",
                "❌ Weaker than key authentication",
                "❌ Higher attack surface"
            ],
            "recommendation": "NOT RECOMMENDED for @PEAK security",
            "risk_score": 8,  # High risk
            "mitigations": [
                "Use strong passwords (20+ characters)",
                "Enable fail2ban or similar",
                "Restrict to specific IPs",
                "Regular password rotation",
                "Monitor SSH access logs"
            ]
        }

        return assessment

    def assess_manus_neo_automation(self) -> Dict[str, Any]:
        """Assess security of MANUS/NEO browser automation"""
        assessment = {
            "configuration": "MANUS/NEO Browser Automation (No SSH)",
            "security_level": SecurityLevel.HIGH.value,
            "attack_surface": "Minimal",
            "pros": [
                "✅ No SSH port exposed",
                "✅ Uses HTTPS (encrypted)",
                "✅ Web portal access only",
                "✅ Visual verification possible",
                "✅ No additional attack surface",
                "✅ Credentials in Azure Key Vault",
                "✅ Browser automation isolated"
            ],
            "cons": [
                "⚠️  Slightly slower than SSH",
                "⚠️  Requires browser automation",
                "⚠️  More complex automation code"
            ],
            "recommendation": "RECOMMENDED for @PEAK security",
            "risk_score": 3,  # Low-Medium risk
            "security_features": [
                "HTTPS encryption",
                "Azure Key Vault credential storage",
                "Browser automation isolation",
                "No exposed network services",
                "Visual audit trail"
            ]
        }

        return assessment

    def compare_configurations(self) -> Dict[str, Any]:
        """Compare all SSH configuration options"""
        logger.info("=" * 70)
        logger.info("🔒 @MARVIN SSH SECURITY ASSESSMENT")
        logger.info("=" * 70)

        assessments = {
            "ssh_disabled": self.assess_ssh_disabled(),
            "ssh_key_only": self.assess_ssh_key_only(),
            "ssh_password_auth": self.assess_ssh_password_auth(),
            "manus_neo_automation": self.assess_manus_neo_automation()
        }

        # Find @PEAK security recommendation
        peak_recommendations = []
        for config_name, assessment in assessments.items():
            if assessment["security_level"] in [SecurityLevel.HIGH.value]:
                peak_recommendations.append({
                    "configuration": config_name,
                    "assessment": assessment
                })

        logger.info("\n📊 SECURITY ASSESSMENT SUMMARY:")
        logger.info("=" * 70)

        for config_name, assessment in assessments.items():
            security_icon = "🔴" if assessment["risk_score"] >= 7 else \
                           "🟠" if assessment["risk_score"] >= 5 else \
                           "🟡" if assessment["risk_score"] >= 3 else "🟢"

            logger.info(f"\n{security_icon} {assessment['configuration']}")
            logger.info(f"   Security Level: {assessment['security_level'].upper()}")
            logger.info(f"   Risk Score: {assessment['risk_score']}/10")
            logger.info(f"   Recommendation: {assessment['recommendation']}")

        logger.info("\n" + "=" * 70)
        logger.info("🎯 @PEAK SECURITY RECOMMENDATION")
        logger.info("=" * 70)

        # @PEAK recommendation: MANUS/NEO automation (highest security)
        peak_config = assessments["manus_neo_automation"]
        logger.info(f"\n✅ RECOMMENDED: {peak_config['configuration']}")
        logger.info(f"   Security Level: {peak_config['security_level'].upper()}")
        logger.info(f"   Risk Score: {peak_config['risk_score']}/10")
        logger.info(f"   Attack Surface: {peak_config['attack_surface']}")

        logger.info("\n📋 Key Security Benefits:")
        for pro in peak_config["pros"]:
            logger.info(f"   {pro}")

        logger.info("\n⚠️  Alternative (if SSH needed):")
        key_only_config = assessments["ssh_key_only"]
        logger.info(f"   {key_only_config['configuration']}")
        logger.info(f"   Security Level: {key_only_config['security_level'].upper()}")
        logger.info(f"   Risk Score: {key_only_config['risk_score']}/10")
        logger.info(f"   Requirements:")
        for req in key_only_config.get("requirements", []):
            logger.info(f"      {req}")

        logger.info("\n" + "=" * 70)
        logger.info("🔒 @MARVIN FINAL VERDICT")
        logger.info("=" * 70)
        logger.info("\n✅ @PEAK SECURITY: Keep SSH DISABLED")
        logger.info("   Use MANUS/NEO browser automation for configuration")
        logger.info("   This provides:")
        logger.info("   - ✅ Highest security (no exposed SSH port)")
        logger.info("   - ✅ Minimal attack surface")
        logger.info("   - ✅ Encrypted HTTPS communication")
        logger.info("   - ✅ Visual verification and audit trail")
        logger.info("   - ✅ Complete automation via CLI-API")

        logger.info("\n⚠️  If SSH is required for specific operations:")
        logger.info("   - Enable SSH with KEY-ONLY authentication")
        logger.info("   - Disable password authentication")
        logger.info("   - Restrict to specific IPs (if possible)")
        logger.info("   - Store SSH keys in Azure Key Vault")
        logger.info("   - Implement key rotation policy")

        logger.info("\n❌ DO NOT enable SSH with password authentication")
        logger.info("   This significantly increases attack surface")
        logger.info("   and is NOT @PEAK security compliant")

        return {
            "assessments": assessments,
            "peak_recommendation": peak_config,
            "alternative": key_only_config if key_only_config["risk_score"] < 7 else None,
            "verdict": "Keep SSH disabled, use MANUS/NEO automation"
        }


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(
            description="@MARVIN SSH Security Assessment for pfSense"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output as JSON"
        )

        args = parser.parse_args()

        assessment = MARVINSSHSecurityAssessment()
        result = assessment.compare_configurations()

        if args.json:
            import json
            print(json.dumps(result, indent=2))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())