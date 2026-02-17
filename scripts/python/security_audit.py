#!/usr/bin/env python3
"""
Security Audit
Performs security audit of the system

Checks for security vulnerabilities, misconfigurations, and compliance.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

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

logger = get_logger("SecurityAudit")


class SecurityAuditor:
    """Performs security audits"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.audit_results_dir = self.project_root / "data" / "security_audits"
        self.audit_results_dir.mkdir(parents=True, exist_ok=True)

    def audit_authentication(self) -> Dict[str, Any]:
        """Audit authentication security"""
        findings = []
        score = 100

        # Check JWT secret strength
        try:
            from api_authentication_service import get_auth_service
            auth_service = get_auth_service(self.project_root)
            jwt_secret = auth_service.jwt_secret

            if jwt_secret == "default-secret-key-change-in-production":
                findings.append({
                    "severity": "critical",
                    "issue": "Default JWT secret in use",
                    "recommendation": "Change JWT secret to strong random value in Key Vault"
                })
                score -= 30

            if len(jwt_secret) < 32:
                findings.append({
                    "severity": "high",
                    "issue": "JWT secret too short",
                    "recommendation": "Use JWT secret of at least 32 characters"
                })
                score -= 20
        except Exception as e:
            findings.append({
                "severity": "medium",
                "issue": f"Could not audit JWT secret: {e}",
                "recommendation": "Manually verify JWT secret configuration"
            })
            score -= 10

        # Check password hashing
        try:
            from api_authentication_service import BCRYPT_AVAILABLE
            if not BCRYPT_AVAILABLE:
                findings.append({
                    "severity": "critical",
                    "issue": "bcrypt not available - using insecure password hashing",
                    "recommendation": "Install bcrypt for secure password hashing"
                })
                score -= 40
        except Exception:
            pass

        return {
            "category": "authentication",
            "score": max(0, score),
            "findings": findings,
            "status": "pass" if score >= 70 else "fail"
        }

    def audit_secrets_management(self) -> Dict[str, Any]:
        """Audit secrets management"""
        findings = []
        score = 100

        # Check for hardcoded secrets
        config_files = list(self.project_root.rglob("*.py"))
        config_files.extend(list(self.project_root.rglob("*.json")))

        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'connection[_-]?string\s*=\s*["\'][^"\']+["\']'
        ]

        import re
        hardcoded_secrets = []
        for config_file in config_files:
            if "test" in str(config_file) or "__pycache__" in str(config_file):
                continue

            try:
                content = config_file.read_text(encoding='utf-8')
                for pattern in secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Skip if it's a variable reference or placeholder
                        value = match.group(0)
                        if not (value.startswith("${") or "PLACEHOLDER" in value.upper() or "YOUR_" in value.upper()):
                            hardcoded_secrets.append({
                                "file": str(config_file.relative_to(self.project_root)),
                                "line": content[:match.start()].count('\n') + 1,
                                "pattern": pattern
                            })
            except Exception:
                pass

        if hardcoded_secrets:
            findings.append({
                "severity": "critical",
                "issue": f"Found {len(hardcoded_secrets)} potential hardcoded secrets",
                "details": hardcoded_secrets[:10],  # Show first 10
                "recommendation": "Move all secrets to Azure Key Vault"
            })
            score -= min(50, len(hardcoded_secrets) * 5)

        return {
            "category": "secrets_management",
            "score": max(0, score),
            "findings": findings,
            "status": "pass" if score >= 70 else "fail"
        }

    def audit_api_security(self) -> Dict[str, Any]:
        """Audit API security"""
        findings = []
        score = 100

        # Check CORS configuration
        try:
            from jarvis_master_agent_api_server import app
            # Check if CORS allows all origins
            for middleware in app.user_middleware:
                if 'CORSMiddleware' in str(middleware):
                    # This would need more sophisticated checking
                    findings.append({
                        "severity": "medium",
                        "issue": "CORS configuration should be reviewed",
                        "recommendation": "Restrict CORS to specific origins in production"
                    })
                    score -= 10
        except Exception:
            pass

        # Check rate limiting
        try:
            from api_middleware import RateLimitMiddleware
            findings.append({
                "severity": "info",
                "issue": "Rate limiting middleware implemented",
                "recommendation": "Verify rate limits are appropriate for production"
            })
        except Exception:
            findings.append({
                "severity": "medium",
                "issue": "Rate limiting middleware not found",
                "recommendation": "Implement rate limiting to prevent abuse"
            })
            score -= 15

        return {
            "category": "api_security",
            "score": max(0, score),
            "findings": findings,
            "status": "pass" if score >= 70 else "fail"
        }

    def audit_database_security(self) -> Dict[str, Any]:
        """Audit database security"""
        findings = []
        score = 100

        # Check connection string security
        try:
            from database_connection_manager import get_db_manager
            db_manager = get_db_manager(self.project_root)

            # Check if connection string comes from Key Vault
            connection_string = db_manager._get_connection_string()
            if "localhost" in connection_string or "127.0.0.1" in connection_string:
                findings.append({
                    "severity": "info",
                    "issue": "Using local database connection",
                    "recommendation": "Ensure production uses secure remote database"
                })
        except Exception as e:
            findings.append({
                "severity": "medium",
                "issue": f"Could not audit database: {e}",
                "recommendation": "Manually verify database security configuration"
            })
            score -= 10

        return {
            "category": "database_security",
            "score": max(0, score),
            "findings": findings,
            "status": "pass" if score >= 70 else "fail"
        }

    def run_full_audit(self) -> Dict[str, Any]:
        try:
            """Run comprehensive security audit"""
            logger.info("Starting security audit...")

            audit_results = {
                "audit_date": datetime.now().isoformat(),
                "auditor": "JARVIS Security Auditor",
                "categories": {}
            }

            # Run all audits
            audit_results["categories"]["authentication"] = self.audit_authentication()
            audit_results["categories"]["secrets_management"] = self.audit_secrets_management()
            audit_results["categories"]["api_security"] = self.audit_api_security()
            audit_results["categories"]["database_security"] = self.audit_database_security()

            # Calculate overall score
            category_scores = [
                cat["score"] for cat in audit_results["categories"].values()
            ]
            overall_score = sum(category_scores) / len(category_scores) if category_scores else 0

            audit_results["overall_score"] = overall_score
            audit_results["overall_status"] = "pass" if overall_score >= 70 else "fail"

            # Collect all findings
            all_findings = []
            for category, results in audit_results["categories"].items():
                for finding in results.get("findings", []):
                    all_findings.append({
                        "category": category,
                        **finding
                    })

            audit_results["all_findings"] = all_findings
            audit_results["critical_findings"] = [f for f in all_findings if f.get("severity") == "critical"]
            audit_results["high_findings"] = [f for f in all_findings if f.get("severity") == "high"]

            # Save audit results
            audit_file = self.audit_results_dir / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(audit_file, 'w', encoding='utf-8') as f:
                json.dump(audit_results, f, indent=2)

            logger.info(f"Security audit complete. Results saved to: {audit_file}")

            return audit_results


        except Exception as e:
            self.logger.error(f"Error in run_full_audit: {e}", exc_info=True)
            raise
def main():
    try:
        """Main security audit function"""
        project_root = Path(__file__).parent.parent.parent
        auditor = SecurityAuditor(project_root)

        print("=" * 60)
        print("Security Audit")
        print("=" * 60)

        results = auditor.run_full_audit()

        print(f"\nOverall Security Score: {results['overall_score']:.1f}/100")
        print(f"Status: {results['overall_status'].upper()}")
        print(f"\nCritical Findings: {len(results['critical_findings'])}")
        print(f"High Findings: {len(results['high_findings'])}")

        if results['critical_findings']:
            print("\nCritical Findings:")
            for finding in results['critical_findings']:
                print(f"  [{finding['category']}] {finding['issue']}")

        print("=" * 60)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    from typing import Optional


    main()