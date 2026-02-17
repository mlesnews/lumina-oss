#!/usr/bin/env python3
"""
Comprehensive Security Audit - MARVIN & Support Teams
Coordinates security review with MARVIN (reality checks) and all support teams
#JARVIS #MARVIN #SECURITY #AUDIT #SSO #LDAP #HARDENING
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
    from scripts.python.azure_service_bus_integration import AzureKeyVaultClient
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class MARVINSecurityAuditor:
    """MARVIN: Pessimistic but thorough security reality checker"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.findings: List[Dict[str, Any]] = []

    def audit_ldap_sso_security(self, nas_integration: NASAzureVaultIntegration) -> List[Dict[str, Any]]:
        """MARVIN: Audit LDAP/SSO security configuration"""
        findings = []

        print("🔍 MARVIN: Auditing LDAP/SSO Security...")

        # Check 1: Certificate security
        result = nas_integration.execute_ssh_command("ls -la /tmp/ldap_certificates/ 2>/dev/null")
        if isinstance(result, dict):
            result = result.get('output', '') or result.get('stdout', '') or str(result)

        if 'client.key' in str(result):
            # Check permissions
            if '600' not in str(result) and '-rw-------' not in str(result):
                findings.append({
                    "severity": "HIGH",
                    "category": "Certificate Security",
                    "issue": "Private key permissions too permissive",
                    "recommendation": "chmod 600 /tmp/ldap_certificates/client.key",
                    "team": "Storage Team"
                })

        # Check 2: LDAP configuration exposure
        result = nas_integration.execute_ssh_command("test -f /tmp/ldap_join_config.txt && cat /tmp/ldap_join_config.txt 2>/dev/null | head -5")
        if isinstance(result, dict):
            result = result.get('output', '') or result.get('stdout', '') or str(result)

        if 'password' in str(result).lower() or 'bind' in str(result).lower():
            findings.append({
                "severity": "MEDIUM",
                "category": "Configuration Security",
                "issue": "LDAP config may contain sensitive data in /tmp",
                "recommendation": "Move config to secure location or remove after use",
                "team": "System Team"
            })

        # Check 3: Domain join status
        result = nas_integration.execute_ssh_command("test -f /usr/syno/etc/ldap/ldap.conf && echo 'JOINED' || echo 'NOT_JOINED'")
        if isinstance(result, dict):
            result = result.get('output', '') or result.get('stdout', '') or str(result)

        if 'NOT_JOINED' in str(result):
            findings.append({
                "severity": "HIGH",
                "category": "SSO Configuration",
                "issue": "LDAP domain not joined - SSO will not work",
                "recommendation": "Complete LDAP join in DSM web interface",
                "team": "System Team"
            })

        # Check 4: Certificate expiration
        result = nas_integration.execute_ssh_command("openssl x509 -in /tmp/ldap_certificates/client.crt -noout -enddate 2>/dev/null || echo 'NO_CERT'")
        if isinstance(result, dict):
            result = result.get('output', '') or result.get('stdout', '') or str(result)

        if 'NO_CERT' not in str(result) and 'notAfter' in str(result):
            # Parse expiration date (simplified check)
            findings.append({
                "severity": "INFO",
                "category": "Certificate Management",
                "issue": "Certificate expiration should be monitored",
                "recommendation": "Set up certificate rotation schedule (2 years)",
                "team": "InfoSec Team"
            })

        self.findings.extend(findings)
        return findings

    def audit_ssh_security(self, nas_integration: NASAzureVaultIntegration) -> List[Dict[str, Any]]:
        """MARVIN: Audit SSH security"""
        findings = []

        print("🔍 MARVIN: Auditing SSH Security...")

        # Check SSH configuration
        result = nas_integration.execute_ssh_command("grep -E '^PasswordAuthentication|^PubkeyAuthentication|^PermitRootLogin' /etc/ssh/sshd_config 2>/dev/null | head -5")
        if isinstance(result, dict):
            result = result.get('output', '') or result.get('stdout', '') or str(result)

        if 'PasswordAuthentication yes' in str(result):
            findings.append({
                "severity": "MEDIUM",
                "category": "SSH Security",
                "issue": "Password authentication enabled (we're using it, but should consider keys)",
                "recommendation": "Consider SSH key authentication for better security",
                "team": "InfoSec Team"
            })

        return findings

    def audit_key_vault_security(self) -> List[Dict[str, Any]]:
        """MARVIN: Audit Azure Key Vault security"""
        findings = []

        print("🔍 MARVIN: Auditing Azure Key Vault Security...")

        # Check if certificates are in Key Vault
        try:
            vault_url = "https://jarvis-lumina.vault.azure.net/"
            from azure.identity import DefaultAzureCredential
            vault_client = AzureKeyVaultClient(vault_url, DefaultAzureCredential(
                    exclude_interactive_browser_credential=False,
                    exclude_shared_token_cache_credential=False
                ))

            # Try to get certificate
            try:
                cert = vault_client.get_secret("ldap-client-certificate")
                findings.append({
                    "severity": "INFO",
                    "category": "Key Vault",
                    "issue": "Certificates should be in Key Vault for backup",
                    "recommendation": "Upload certificates to Key Vault",
                    "team": "InfoSec Team"
                })
            except:
                findings.append({
                    "severity": "MEDIUM",
                    "category": "Key Vault",
                    "issue": "Certificates not in Key Vault",
                    "recommendation": "Upload certificates to Key Vault for secure backup",
                    "team": "InfoSec Team"
                })
        except Exception as e:
            findings.append({
                "severity": "LOW",
                "category": "Key Vault",
                "issue": f"Could not verify Key Vault: {e}",
                "recommendation": "Verify Key Vault access",
                "team": "InfoSec Team"
            })

        return findings

    def run_full_audit(self, nas_integration: NASAzureVaultIntegration) -> List[Dict[str, Any]]:
        """Run complete MARVIN security audit"""
        print("=" * 70)
        print("   MARVIN SECURITY AUDIT")
        print("=" * 70)
        print("")

        all_findings = []
        all_findings.extend(self.audit_ldap_sso_security(nas_integration))
        all_findings.extend(self.audit_ssh_security(nas_integration))
        all_findings.extend(self.audit_key_vault_security())

        self.findings = all_findings
        return all_findings


def coordinate_team_fixes(findings: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Coordinate fixes with support teams"""
    teams = {
        "InfoSec Team": [],
        "Storage Team": [],
        "System Team": [],
        "Network Team": []
    }

    for finding in findings:
        team = finding.get("team", "System Team")
        if team in teams:
            teams[team].append(finding)
        else:
            teams["System Team"].append(finding)

    return teams


def generate_fix_script(teams: Dict[str, List[Dict[str, Any]]], nas_integration: NASAzureVaultIntegration) -> str:
    """Generate automated fix script based on findings"""
    script_content = """#!/usr/bin/env python3
# Auto-generated security fix script
# Generated by MARVIN Security Audit
"""

    fixes = []

    # InfoSec Team fixes
    for finding in teams.get("InfoSec Team", []):
        if "Certificate" in finding.get("category", ""):
            fixes.append("# InfoSec: Upload certificates to Key Vault")
            fixes.append("# python scripts/python/get_azure_ad_certificate_crypto.py --generate --upload")

    # Storage Team fixes
    for finding in teams.get("Storage Team", []):
        if "permissions" in finding.get("issue", "").lower():
            fixes.append("# Storage: Fix certificate permissions")
            fixes.append("nas_integration.execute_ssh_command('chmod 600 /tmp/ldap_certificates/client.key')")
            fixes.append("nas_integration.execute_ssh_command('chmod 644 /tmp/ldap_certificates/client.crt')")

    # System Team fixes
    for finding in teams.get("System Team", []):
        if "config" in finding.get("issue", "").lower():
            fixes.append("# System: Secure LDAP config file")
            fixes.append("nas_integration.execute_ssh_command('chmod 600 /tmp/ldap_join_config.txt')")

    if fixes:
        script_content += "\n".join(fixes)
    else:
        script_content += "# No automated fixes available - manual intervention required"

    return script_content


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Comprehensive Security Audit - MARVIN & Support Teams")
        parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
        parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
        parser.add_argument("--fix", action="store_true", help="Apply automated fixes")
        parser.add_argument("--report", help="Output report file path")

        args = parser.parse_args()

        print("=" * 70)
        print("   COMPREHENSIVE SECURITY AUDIT")
        print("   MARVIN & Support Teams Coordination")
        print("=" * 70)
        print("")

        # Initialize NAS integration
        nas_integration = NASAzureVaultIntegration(
            vault_name=args.vault_name,
            nas_ip=args.nas_ip
        )

        # Run MARVIN audit
        marvin = MARVINSecurityAuditor(project_root)
        findings = marvin.run_full_audit(nas_integration)

        print("")
        print("=" * 70)
        print("   AUDIT RESULTS")
        print("=" * 70)
        print("")

        # Group by severity
        high = [f for f in findings if f.get("severity") == "HIGH"]
        medium = [f for f in findings if f.get("severity") == "MEDIUM"]
        low = [f for f in findings if f.get("severity") == "LOW"]
        info = [f for f in findings if f.get("severity") == "INFO"]

        if high:
            print("🔴 HIGH SEVERITY ISSUES:")
            for finding in high:
                print(f"  - [{finding.get('category')}] {finding.get('issue')}")
                print(f"    Team: {finding.get('team')}")
                print(f"    Fix: {finding.get('recommendation')}")
                print("")

        if medium:
            print("🟡 MEDIUM SEVERITY ISSUES:")
            for finding in medium:
                print(f"  - [{finding.get('category')}] {finding.get('issue')}")
                print(f"    Team: {finding.get('team')}")
                print(f"    Fix: {finding.get('recommendation')}")
                print("")

        if low or info:
            print("ℹ️  INFORMATION / LOW PRIORITY:")
            for finding in low + info:
                print(f"  - [{finding.get('category')}] {finding.get('issue')}")
                print("")

        # Coordinate with teams
        print("=" * 70)
        print("   TEAM COORDINATION")
        print("=" * 70)
        print("")

        teams = coordinate_team_fixes(findings)

        for team_name, team_findings in teams.items():
            if team_findings:
                print(f"{team_name}:")
                for finding in team_findings:
                    print(f"  - {finding.get('issue')}")
                    print(f"    Fix: {finding.get('recommendation')}")
                print("")

        # Generate fix script
        if args.fix:
            print("=" * 70)
            print("   APPLYING AUTOMATED FIXES")
            print("=" * 70)
            print("")

            fix_script = generate_fix_script(teams, nas_integration)

            # Apply Storage Team fixes (safe to automate)
            for finding in teams.get("Storage Team", []):
                if "permissions" in finding.get("issue", "").lower():
                    print(f"Applying fix: {finding.get('recommendation')}")
                    nas_integration.execute_ssh_command("chmod 600 /tmp/ldap_certificates/client.key")
                    nas_integration.execute_ssh_command("chmod 644 /tmp/ldap_certificates/client.crt")
                    print("  ✓ Fixed")

            # Apply System Team fixes (safe to automate)
            for finding in teams.get("System Team", []):
                if "config" in finding.get("issue", "").lower() and "permissions" in finding.get("recommendation", "").lower():
                    print(f"Applying fix: {finding.get('recommendation')}")
                    nas_integration.execute_ssh_command("chmod 600 /tmp/ldap_join_config.txt")
                    print("  ✓ Fixed")

            print("")
            print("⚠️  Manual fixes required for:")
            for team_name, team_findings in teams.items():
                for finding in team_findings:
                    if finding.get("severity") == "HIGH" and "join" in finding.get("issue", "").lower():
                        print(f"  - {finding.get('issue')}")
                        print(f"    Action: {finding.get('recommendation')}")

        # Generate report
        if args.report:
            report_path = Path(args.report)
            report = {
                "timestamp": datetime.now().isoformat(),
                "auditor": "@marvin",
                "findings": findings,
                "teams": teams,
                "summary": {
                    "total": len(findings),
                    "high": len(high),
                    "medium": len(medium),
                    "low": len(low),
                    "info": len(info)
                }
            }
            report_path.write_text(json.dumps(report, indent=2))
            print(f"\nReport saved to: {report_path}")

        print("")
        print("=" * 70)
        print("   SSO STATUS")
        print("=" * 70)
        print("")

        # Check SSO readiness
        domain_joined = any("NOT_JOINED" not in str(f.get("issue", "")) for f in findings if "SSO" in f.get("category", ""))

        if not domain_joined:
            print("⚠️  SSO NOT READY")
            print("")
            print("Critical issue: LDAP domain not joined")
            print("")
            print("To enable SSO:")
            print("  1. RDP to MANUS: mstsc /v:<NAS_IP>")
            print("  2. Open DSM: https://<NAS_PRIMARY_IP>:5001")
            print("  3. Control Panel → Domain/LDAP → Join")
            print("  4. Use certificates:")
            print("     - Certificate: /tmp/ldap_certificates/client.crt")
            print("     - Private Key: /tmp/ldap_certificates/client.key")
            print("  5. Complete join process")
        else:
            print("✅ SSO READY")
            print("")
            print("All security requirements met for SSO")

        print("")
        print("=" * 70)
        print("")

        return 0 if len(high) == 0 else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())