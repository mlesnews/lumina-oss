#!/usr/bin/env python3
"""
Granular Azure Security Verification
Phase 1: Verification - Every Single Check

This script performs comprehensive verification of:
- Azure Key Vault (every detail)
- Azure Service Bus (every detail)

Author: @marvin + @hk-47 Security Team
Date: 2025-01-28
Status: 🔴 CRITICAL SECURITY VERIFICATION
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from azure.keyvault.secrets import SecretClient
    from azure.keyvault.keys import KeyClient
    from azure.keyvault.certificates import CertificateClient
    from azure.identity import DefaultAzureCredential
    from azure.core.exceptions import AzureError, ResourceNotFoundError
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    print("⚠️  Azure Key Vault SDK not installed")
    print("Install with: pip install azure-keyvault-secrets azure-keyvault-keys azure-keyvault-certificates azure-identity")

try:
    from azure.servicebus import ServiceBusClient
    from azure.servicebus.exceptions import ServiceBusError
    from azure.servicebus.management import ServiceBusAdministrationClient
    SERVICE_BUS_AVAILABLE = True
except ImportError:
    SERVICE_BUS_AVAILABLE = False
    print("⚠️  Azure Service Bus SDK not installed")
    print("Install with: pip install azure-servicebus")

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AzureSecurityVerification")


class VerificationStatus(Enum):
    """Verification result status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class VerificationResult:
    """Result of a single verification check"""
    check_id: str
    check_name: str
    status: VerificationStatus
    message: str
    details: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat()
        }


class AzureKeyVaultVerifier:
    """Granular Key Vault Verification - Every Single Check"""

    def __init__(self, vault_url: str):
        self.vault_url = vault_url
        self.vault_name = vault_url.replace("https://", "").replace(".vault.azure.net/", "").replace(".vault.azure.net", "")
        self.results: List[VerificationResult] = []
        self.credential = None
        self.secret_client = None
        self.key_client = None
        self.cert_client = None

    def verify_all(self) -> List[VerificationResult]:
        """Run all Key Vault verifications"""
        logger.info("=" * 80)
        logger.info("🔴 AZURE KEY VAULT GRANULAR VERIFICATION")
        logger.info("=" * 80)
        logger.info(f"Vault URL: {self.vault_url}")
        logger.info(f"Vault Name: {self.vault_name}\n")

        # Step 1.1.1: Verify Key Vault Exists
        self._verify_vault_exists()

        # Step 1.1.2: Verify Authentication
        if self._verify_authentication():
            # Step 1.1.3: Verify Access Policies
            self._verify_access_policies()

            # Step 1.1.4: Verify Secret Storage
            self._verify_secret_storage()

            # Step 1.1.5: Verify Secret Retrieval
            self._verify_secret_retrieval()

            # Step 1.1.6: Verify Secret Rotation
            self._verify_secret_rotation()

            # Step 1.1.7: Verify Monitoring and Logging
            self._verify_monitoring()

            # Step 1.1.8: Verify Backup and Recovery
            self._verify_backup()

        return self.results

    def _verify_vault_exists(self):
        """Step 1.1.1: Verify Key Vault Exists"""
        logger.info("Step 1.1.1: Verifying Key Vault Exists...")

        # Check if SDK is available
        if not KEY_VAULT_AVAILABLE:
            self.results.append(VerificationResult(
                check_id="kv-1.1.1-sdk",
                check_name="Key Vault SDK Available",
                status=VerificationStatus.FAIL,
                message="Azure Key Vault SDK not installed",
                details={"action": "Install: pip install azure-keyvault-secrets azure-identity"}
            ))
            return

        # Try to create client (this will fail if vault doesn't exist)
        try:
            self.credential = DefaultAzureCredential(
                    exclude_interactive_browser_credential=False,
                    exclude_shared_token_cache_credential=False
                )
            self.secret_client = SecretClient(vault_url=self.vault_url, credential=self.credential)

            # Try to list secrets (this will fail if vault doesn't exist or we can't access)
            try:
                list(self.secret_client.list_properties_of_secrets())
                self.results.append(VerificationResult(
                    check_id="kv-1.1.1-exists",
                    check_name="Key Vault Exists",
                    status=VerificationStatus.PASS,
                    message=f"Key Vault '{self.vault_name}' exists and is accessible",
                    details={"vault_name": self.vault_name, "vault_url": self.vault_url}
                ))
            except ResourceNotFoundError:
                self.results.append(VerificationResult(
                    check_id="kv-1.1.1-exists",
                    check_name="Key Vault Exists",
                    status=VerificationStatus.FAIL,
                    message=f"Key Vault '{self.vault_name}' not found",
                    details={"vault_name": self.vault_name, "action": "Create vault in Azure Portal"}
                ))
            except Exception as e:
                self.results.append(VerificationResult(
                    check_id="kv-1.1.1-exists",
                    check_name="Key Vault Exists",
                    status=VerificationStatus.ERROR,
                    message=f"Error accessing Key Vault: {str(e)}",
                    details={"error": str(e), "action": "Check authentication and permissions"}
                ))
        except Exception as e:
            self.results.append(VerificationResult(
                check_id="kv-1.1.1-exists",
                check_name="Key Vault Exists",
                status=VerificationStatus.ERROR,
                message=f"Failed to initialize Key Vault client: {str(e)}",
                details={"error": str(e)}
            ))

    def _verify_authentication(self) -> bool:
        """Step 1.1.2: Verify Authentication"""
        logger.info("Step 1.1.2: Verifying Authentication...")

        if not self.credential:
            self.results.append(VerificationResult(
                check_id="kv-1.1.2-auth",
                check_name="Authentication",
                status=VerificationStatus.SKIP,
                message="Skipped - Key Vault client not initialized",
                details={}
            ))
            return False

        try:
            # Test authentication by trying to get a non-existent secret
            # This will fail with ResourceNotFoundError if auth works, or AuthenticationError if it doesn't
            try:
                self.secret_client.get_secret("__test_auth_check__")
            except ResourceNotFoundError:
                # This is good - it means auth worked but secret doesn't exist
                self.results.append(VerificationResult(
                    check_id="kv-1.1.2-auth",
                    check_name="Authentication",
                    status=VerificationStatus.PASS,
                    message="Authentication successful",
                    details={"method": "DefaultAzureCredential"}
                ))
                return True
            except Exception as e:
                error_str = str(e)
                if "authentication" in error_str.lower() or "unauthorized" in error_str.lower():
                    self.results.append(VerificationResult(
                        check_id="kv-1.1.2-auth",
                        check_name="Authentication",
                        status=VerificationStatus.FAIL,
                        message="Authentication failed",
                        details={"error": error_str, "action": "Run 'az login' or configure Managed Identity"}
                    ))
                else:
                    self.results.append(VerificationResult(
                        check_id="kv-1.1.2-auth",
                        check_name="Authentication",
                        status=VerificationStatus.ERROR,
                        message=f"Unexpected error: {error_str}",
                        details={"error": error_str}
                    ))
                return False
        except Exception as e:
            self.results.append(VerificationResult(
                check_id="kv-1.1.2-auth",
                check_name="Authentication",
                status=VerificationStatus.ERROR,
                message=f"Error testing authentication: {str(e)}",
                details={"error": str(e)}
            ))
            return False

    def _verify_access_policies(self):
        """Step 1.1.3: Verify Access Policies"""
        logger.info("Step 1.1.3: Verifying Access Policies...")

        # Note: Access policies are managed via Azure Management API, not the data plane
        # This is a simplified check - full verification requires Azure Management SDK
        self.results.append(VerificationResult(
            check_id="kv-1.1.3-policies",
            check_name="Access Policies",
            status=VerificationStatus.WARNING,
            message="Access policy verification requires Azure Management API",
            details={"action": "Check access policies in Azure Portal or use Azure Management SDK"}
        ))

    def _verify_secret_storage(self):
        """Step 1.1.4: Verify Secret Storage"""
        logger.info("Step 1.1.4: Verifying Secret Storage...")

        if not self.secret_client:
            self.results.append(VerificationResult(
                check_id="kv-1.1.4-storage",
                check_name="Secret Storage",
                status=VerificationStatus.SKIP,
                message="Skipped - Key Vault client not initialized",
                details={}
            ))
            return

        # Expected secrets
        expected_secrets = [
            "jarvis-api-key",
            "lumina-api-key",
            "r5-api-key",
            "anthropic-api-key",
            "openai-api-key",
            "github-token",
            "n8n-webhook-secret",
            "service-bus-connection-string",
            "database-connection-string",
            "redis-connection-string",
            "r5-encryption-key",
            "workflow-signing-key",
            "nas-username",
            "nas-password",
            "azure-speech-key",
            "azure-speech-region",
        ]

        try:
            # List all secrets
            existing_secrets = []
            for secret_properties in self.secret_client.list_properties_of_secrets():
                existing_secrets.append(secret_properties.name)

            # Check which expected secrets exist
            found_secrets = []
            missing_secrets = []

            for secret_name in expected_secrets:
                if secret_name in existing_secrets:
                    found_secrets.append(secret_name)
                else:
                    missing_secrets.append(secret_name)

            # Report results
            if found_secrets:
                self.results.append(VerificationResult(
                    check_id="kv-1.1.4-found",
                    check_name="Expected Secrets Found",
                    status=VerificationStatus.PASS,
                    message=f"Found {len(found_secrets)} expected secrets",
                    details={"found": found_secrets, "count": len(found_secrets)}
                ))

            if missing_secrets:
                self.results.append(VerificationResult(
                    check_id="kv-1.1.4-missing",
                    check_name="Expected Secrets Missing",
                    status=VerificationStatus.WARNING,
                    message=f"Missing {len(missing_secrets)} expected secrets",
                    details={"missing": missing_secrets, "count": len(missing_secrets)}
                ))

            # Check for unexpected secrets
            unexpected = [s for s in existing_secrets if s not in expected_secrets]
            if unexpected:
                self.results.append(VerificationResult(
                    check_id="kv-1.1.4-unexpected",
                    check_name="Unexpected Secrets",
                    status=VerificationStatus.WARNING,
                    message=f"Found {len(unexpected)} unexpected secrets",
                    details={"unexpected": unexpected[:10], "total": len(unexpected)}
                ))

            # Total count
            self.results.append(VerificationResult(
                check_id="kv-1.1.4-total",
                check_name="Total Secrets",
                status=VerificationStatus.PASS,
                message=f"Total secrets in vault: {len(existing_secrets)}",
                details={"total": len(existing_secrets)}
            ))

        except Exception as e:
            self.results.append(VerificationResult(
                check_id="kv-1.1.4-storage",
                check_name="Secret Storage",
                status=VerificationStatus.ERROR,
                message=f"Error listing secrets: {str(e)}",
                details={"error": str(e)}
            ))

    def _verify_secret_retrieval(self):
        """Step 1.1.5: Verify Secret Retrieval"""
        logger.info("Step 1.1.5: Verifying Secret Retrieval...")

        if not self.secret_client:
            self.results.append(VerificationResult(
                check_id="kv-1.1.5-retrieval",
                check_name="Secret Retrieval",
                status=VerificationStatus.SKIP,
                message="Skipped - Key Vault client not initialized",
                details={}
            ))
            return

        # Try to retrieve a few secrets to test
        test_secrets = ["jarvis-api-key", "lumina-api-key", "azure-speech-key"]
        retrieved = 0
        failed = 0

        for secret_name in test_secrets:
            try:
                secret = self.secret_client.get_secret(secret_name)
                if secret and secret.value:
                    retrieved += 1
                else:
                    failed += 1
            except ResourceNotFoundError:
                # Secret doesn't exist - that's okay for this test
                pass
            except Exception as e:
                failed += 1
                logger.debug(f"Failed to retrieve {secret_name}: {e}")

        if retrieved > 0:
            self.results.append(VerificationResult(
                check_id="kv-1.1.5-retrieval",
                check_name="Secret Retrieval",
                status=VerificationStatus.PASS,
                message=f"Successfully retrieved {retrieved} test secrets",
                details={"retrieved": retrieved, "tested": len(test_secrets)}
            ))
        else:
            self.results.append(VerificationResult(
                check_id="kv-1.1.5-retrieval",
                check_name="Secret Retrieval",
                status=VerificationStatus.WARNING,
                message="Could not retrieve test secrets (may not exist)",
                details={"tested": len(test_secrets)}
            ))

    def _verify_secret_rotation(self):
        """Step 1.1.6: Verify Secret Rotation"""
        logger.info("Step 1.1.6: Verifying Secret Rotation...")

        # Rotation is typically managed externally or via automation
        self.results.append(VerificationResult(
            check_id="kv-1.1.6-rotation",
            check_name="Secret Rotation",
            status=VerificationStatus.WARNING,
            message="Secret rotation verification requires manual review",
            details={"action": "Check if rotation is configured in Azure Portal or automation"}
        ))

    def _verify_monitoring(self):
        """Step 1.1.7: Verify Monitoring and Logging"""
        logger.info("Step 1.1.7: Verifying Monitoring and Logging...")

        # Monitoring requires Azure Monitor/Log Analytics
        self.results.append(VerificationResult(
            check_id="kv-1.1.7-monitoring",
            check_name="Monitoring and Logging",
            status=VerificationStatus.WARNING,
            message="Monitoring verification requires Azure Monitor API",
            details={"action": "Check diagnostic settings in Azure Portal"}
        ))

    def _verify_backup(self):
        """Step 1.1.8: Verify Backup and Recovery"""
        logger.info("Step 1.1.8: Verifying Backup and Recovery...")

        # Backup verification requires Azure Management API
        self.results.append(VerificationResult(
            check_id="kv-1.1.8-backup",
            check_name="Backup and Recovery",
            status=VerificationStatus.WARNING,
            message="Backup verification requires Azure Management API",
            details={"action": "Check backup configuration in Azure Portal"}
        ))


class AzureServiceBusVerifier:
    """Granular Service Bus Verification - Every Single Check"""

    def __init__(self, connection_string: Optional[str] = None, namespace: Optional[str] = None):
        self.connection_string = connection_string
        self.namespace = namespace or "jarvis-lumina-bus"
        self.results: List[VerificationResult] = []
        self.client = None
        self.admin_client = None

    def verify_all(self) -> List[VerificationResult]:
        """Run all Service Bus verifications"""
        logger.info("=" * 80)
        logger.info("🔴 AZURE SERVICE BUS GRANULAR VERIFICATION")
        logger.info("=" * 80)
        logger.info(f"Namespace: {self.namespace}\n")

        # Step 1.2.1: Verify Service Bus Namespace Exists
        if self._verify_namespace_exists():
            # Step 1.2.2: Verify Authentication
            if self._verify_authentication():
                # Step 1.2.3: Verify Topics Exist
                self._verify_topics()

                # Step 1.2.4: Verify Queues Exist
                self._verify_queues()

                # Step 1.2.5: Verify Subscriptions
                self._verify_subscriptions()

                # Step 1.2.6: Verify Message Publishing
                self._verify_publishing()

                # Step 1.2.7: Verify Message Receiving
                self._verify_receiving()

        # Step 1.2.8: Verify Monitoring
        self._verify_monitoring()

        return self.results

    def _verify_namespace_exists(self) -> bool:
        """Step 1.2.1: Verify Service Bus Namespace Exists"""
        logger.info("Step 1.2.1: Verifying Service Bus Namespace Exists...")

        if not SERVICE_BUS_AVAILABLE:
            self.results.append(VerificationResult(
                check_id="sb-1.2.1-sdk",
                check_name="Service Bus SDK Available",
                status=VerificationStatus.FAIL,
                message="Azure Service Bus SDK not installed",
                details={"action": "Install: pip install azure-servicebus"}
            ))
            return False

        # Try to create admin client to check namespace
        try:
            if self.connection_string:
                self.admin_client = ServiceBusAdministrationClient.from_connection_string(self.connection_string)
            else:
                # Try with DefaultAzureCredential
                from azure.identity import DefaultAzureCredential
                credential = DefaultAzureCredential(

                                    exclude_interactive_browser_credential=False,

                                    exclude_shared_token_cache_credential=False

                                )
                fully_qualified_namespace = f"{self.namespace}.servicebus.windows.net"
                self.admin_client = ServiceBusAdministrationClient(fully_qualified_namespace, credential)

            # Try to get namespace properties
            try:
                props = self.admin_client.get_namespace_properties()
                self.results.append(VerificationResult(
                    check_id="sb-1.2.1-exists",
                    check_name="Service Bus Namespace Exists",
                    status=VerificationStatus.PASS,
                    message=f"Namespace '{self.namespace}' exists",
                    details={"namespace": self.namespace}
                ))
                return True
            except Exception as e:
                self.results.append(VerificationResult(
                    check_id="sb-1.2.1-exists",
                    check_name="Service Bus Namespace Exists",
                    status=VerificationStatus.FAIL,
                    message=f"Namespace '{self.namespace}' not found or not accessible",
                    details={"namespace": self.namespace, "error": str(e)}
                ))
                return False
        except Exception as e:
            self.results.append(VerificationResult(
                check_id="sb-1.2.1-exists",
                check_name="Service Bus Namespace Exists",
                status=VerificationStatus.ERROR,
                message=f"Error checking namespace: {str(e)}",
                details={"error": str(e), "action": "Check connection string or authentication"}
            ))
            return False

    def _verify_authentication(self) -> bool:
        """Step 1.2.2: Verify Authentication"""
        logger.info("Step 1.2.2: Verifying Authentication...")

        if not self.admin_client:
            self.results.append(VerificationResult(
                check_id="sb-1.2.2-auth",
                check_name="Authentication",
                status=VerificationStatus.SKIP,
                message="Skipped - Admin client not initialized",
                details={}
            ))
            return False

        # Authentication is already verified if we got here
        self.results.append(VerificationResult(
            check_id="sb-1.2.2-auth",
            check_name="Authentication",
            status=VerificationStatus.PASS,
            message="Authentication successful",
            details={}
        ))
        return True

    def _verify_topics(self):
        """Step 1.2.3: Verify Topics Exist"""
        logger.info("Step 1.2.3: Verifying Topics Exist...")

        if not self.admin_client:
            self.results.append(VerificationResult(
                check_id="sb-1.2.3-topics",
                check_name="Topics",
                status=VerificationStatus.SKIP,
                message="Skipped - Admin client not initialized",
                details={}
            ))
            return

        expected_topics = [
            "jarvis.workflows",
            "jarvis.escalations",
            "jarvis.intelligence",
            "jarvis.responses",
            "lumina.workflows",
            "lumina.verification",
            "r5.knowledge",
            "helpdesk.coordination",
        ]

        try:
            existing_topics = []
            for topic_properties in self.admin_client.list_topics():
                existing_topics.append(topic_properties.name)

            found_topics = [t for t in expected_topics if t in existing_topics]
            missing_topics = [t for t in expected_topics if t not in existing_topics]

            if found_topics:
                self.results.append(VerificationResult(
                    check_id="sb-1.2.3-found",
                    check_name="Expected Topics Found",
                    status=VerificationStatus.PASS,
                    message=f"Found {len(found_topics)} expected topics",
                    details={"found": found_topics, "count": len(found_topics)}
                ))

            if missing_topics:
                self.results.append(VerificationResult(
                    check_id="sb-1.2.3-missing",
                    check_name="Expected Topics Missing",
                    status=VerificationStatus.WARNING,
                    message=f"Missing {len(missing_topics)} expected topics",
                    details={"missing": missing_topics, "count": len(missing_topics)}
                ))
        except Exception as e:
            self.results.append(VerificationResult(
                check_id="sb-1.2.3-topics",
                check_name="Topics",
                status=VerificationStatus.ERROR,
                message=f"Error listing topics: {str(e)}",
                details={"error": str(e)}
            ))

    def _verify_queues(self):
        """Step 1.2.4: Verify Queues Exist"""
        logger.info("Step 1.2.4: Verifying Queues Exist...")

        if not self.admin_client:
            self.results.append(VerificationResult(
                check_id="sb-1.2.4-queues",
                check_name="Queues",
                status=VerificationStatus.SKIP,
                message="Skipped - Admin client not initialized",
                details={}
            ))
            return

        expected_queues = [
            "jarvis-escalation-queue",
            "workflow-execution-queue",
            "r5-ingestion-queue",
            "verification-queue",
            "droid-assignment-queue",
        ]

        try:
            existing_queues = []
            for queue_properties in self.admin_client.list_queues():
                existing_queues.append(queue_properties.name)

            found_queues = [q for q in expected_queues if q in existing_queues]
            missing_queues = [q for q in expected_queues if q not in existing_queues]

            if found_queues:
                self.results.append(VerificationResult(
                    check_id="sb-1.2.4-found",
                    check_name="Expected Queues Found",
                    status=VerificationStatus.PASS,
                    message=f"Found {len(found_queues)} expected queues",
                    details={"found": found_queues, "count": len(found_queues)}
                ))

            if missing_queues:
                self.results.append(VerificationResult(
                    check_id="sb-1.2.4-missing",
                    check_name="Expected Queues Missing",
                    status=VerificationStatus.WARNING,
                    message=f"Missing {len(missing_queues)} expected queues",
                    details={"missing": missing_queues, "count": len(missing_queues)}
                ))
        except Exception as e:
            self.results.append(VerificationResult(
                check_id="sb-1.2.4-queues",
                check_name="Queues",
                status=VerificationStatus.ERROR,
                message=f"Error listing queues: {str(e)}",
                details={"error": str(e)}
            ))

    def _verify_subscriptions(self):
        """Step 1.2.5: Verify Subscriptions"""
        logger.info("Step 1.2.5: Verifying Subscriptions...")

        # This would require checking each topic for subscriptions
        self.results.append(VerificationResult(
            check_id="sb-1.2.5-subscriptions",
            check_name="Subscriptions",
            status=VerificationStatus.WARNING,
            message="Subscription verification requires checking each topic",
            details={"action": "Manually verify subscriptions in Azure Portal"}
        ))

    def _verify_publishing(self):
        """Step 1.2.6: Verify Message Publishing"""
        logger.info("Step 1.2.6: Verifying Message Publishing...")

        # Publishing test would require actual message send
        self.results.append(VerificationResult(
            check_id="sb-1.2.6-publishing",
            check_name="Message Publishing",
            status=VerificationStatus.WARNING,
            message="Publishing test requires test message",
            details={"action": "Test publishing with a test message"}
        ))

    def _verify_receiving(self):
        """Step 1.2.7: Verify Message Receiving"""
        logger.info("Step 1.2.7: Verifying Message Receiving...")

        # Receiving test would require actual message receive
        self.results.append(VerificationResult(
            check_id="sb-1.2.7-receiving",
            check_name="Message Receiving",
            status=VerificationStatus.WARNING,
            message="Receiving test requires test message",
            details={"action": "Test receiving with a test message"}
        ))

    def _verify_monitoring(self):
        """Step 1.2.8: Verify Monitoring"""
        logger.info("Step 1.2.8: Verifying Monitoring...")

        self.results.append(VerificationResult(
            check_id="sb-1.2.8-monitoring",
            check_name="Monitoring",
            status=VerificationStatus.WARNING,
            message="Monitoring verification requires Azure Monitor API",
            details={"action": "Check diagnostic settings in Azure Portal"}
        ))


def main():
    try:
        """Main execution"""
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent

        print("=" * 80)
        print("🔴 GRANULAR AZURE SECURITY VERIFICATION")
        print("=" * 80)
        print(f"Project Root: {project_root}\n")

        all_results = []

        # Key Vault Verification
        vault_url = "https://jarvis-lumina.vault.azure.net/"
        print("Verifying Azure Key Vault...")
        kv_verifier = AzureKeyVaultVerifier(vault_url)
        kv_results = kv_verifier.verify_all()
        all_results.extend(kv_results)

        # Service Bus Verification
        print("\nVerifying Azure Service Bus...")
        sb_verifier = AzureServiceBusVerifier()
        sb_results = sb_verifier.verify_all()
        all_results.extend(sb_results)

        # Generate Report
        report = {
            "verification_date": datetime.now().isoformat(),
            "total_checks": len(all_results),
            "results_by_status": {},
            "results": [r.to_dict() for r in all_results]
        }

        # Group by status
        for result in all_results:
            status = result.status.value
            if status not in report["results_by_status"]:
                report["results_by_status"][status] = 0
            report["results_by_status"][status] += 1

        # Save report
        report_path = project_root / "data" / "azure_security_verification_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Print Summary
        print("\n" + "=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total Checks: {len(all_results)}")
        print(f"\nResults by Status:")
        for status, count in report["results_by_status"].items():
            print(f"  {status.upper()}: {count}")

        print(f"\nReport saved to: {report_path}")

        # Show critical findings
        critical = [r for r in all_results if r.status == VerificationStatus.FAIL]
        if critical:
            print("\n" + "=" * 80)
            print("🔴 CRITICAL FINDINGS")
            print("=" * 80)
            for result in critical:
                print(f"\n{result.check_name}: {result.message}")
                if result.details:
                    print(f"  Details: {json.dumps(result.details, indent=2)}")

        print("\n" + "=" * 80)
        print("VERIFICATION COMPLETE")
        print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()